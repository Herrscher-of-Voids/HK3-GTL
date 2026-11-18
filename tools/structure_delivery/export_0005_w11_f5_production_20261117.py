from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from w11_f5_geometry import CONTROLLER, read_sources, rasterize
from w11_f5_materials import LOG, MACHINE, ROOT, SOURCE
from w11_f5_dynamic_mask import write_dynamic_mask
from theatre_f1_actors import DOMINION


RESOURCE = ROOT/'src/main/resources/data/hk3gtl/structures'
BLUEPRINT = RESOURCE/'w11_candidate.bin.gz'
MASK = RESOURCE/'w11_f5_mask.bin.gz'
METADATA = RESOURCE/'w11_approved.json'
RAW = np.dtype([('x', '>i4'), ('y', '>i4'), ('z', '>i4'), ('length', '>u2'), ('state', '>u2')])
RUN = np.dtype([('x', '>i4'), ('y', '>i4'), ('z', '>i4'), ('length', 'u1'), ('state', '>u2')])


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def compressed(path):
    return gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', compresslevel=6, mtime=0)


def strips(values):
    nonzero = values != 0
    starts = nonzero.copy()
    starts[:, 1:] &= values[:, 1:] != values[:, :-1]
    ends = nonzero.copy()
    ends[:, :-1] &= values[:, :-1] != values[:, 1:]
    rows, first = np.nonzero(starts)
    last = np.nonzero(ends)[1]
    return values[rows, first], rows, first, last-first+1


def perpendicular(labels, face, x, low):
    values, y, z, length = strips(labels)
    if not len(values):
        return np.empty((0, 8), np.int32)
    order = np.lexsort((y, length, z, values))
    values, y, z, length = (a[order] for a in (values, y, z, length))
    breaks = np.r_[True, (values[1:] != values[:-1])|(z[1:] != z[:-1])|
                   (length[1:] != length[:-1])|(y[1:] != y[:-1]+1)]
    first = np.flatnonzero(breaks)
    spans = np.diff(np.r_[first, len(values)])
    return np.c_[values[first] >> 8, values[first]&255, np.full(len(first), face), np.full(len(first), x),
                 y[first]+low[1], z[first]+low[2], length[first], spans].astype(np.int32)


def longitudinal(labels, face, x, low, previous):
    values, row, column, spans = strips(labels.T if face in (2, 3) else labels)
    current, finished = {}, []
    for value, r, c, span in zip(values.tolist(), row.tolist(), column.tolist(), spans.tolist()):
        y, z = (c, r) if face in (2, 3) else (r, c)
        key = value, face, y, z, span
        if key in previous:
            record = previous.pop(key)
            record[6] += 1
        else:
            record = [value >> 8, value&255, face, x, y+int(low[1]), z+int(low[2]), 1, span]
        current[key] = record
    finished.extend(previous.values())
    return current, finished


def write_raw(scene, sample=rasterize, controller=CONTROLLER, out=LOG):
    low, high = scene['low'], scene['high']
    palette_count = len(scene['materials'])+1
    counts = np.zeros(palette_count, np.int64)
    actual_low, actual_high = high.copy(), low.copy()
    transparent = np.array([False, *[m['transparent'] for m in scene['materials']], False])
    previous_plane = np.zeros((high[1]-low[1]+1, high[2]-low[2]+1), np.uint8)
    previous_owner = previous_plane.copy()
    raw_path, quads_path, layers_path = out/'world-runs.bin', out/'surface-quads.bin', out/'layer-quads.bin'
    with raw_path.open('wb') as raw, quads_path.open('wb') as mesh, layers_path.open('wb') as layer_stream:
        for x0 in range(int(low[0]), int(high[0])+1, 16):
            x1 = min(x0+16, int(high[0])+1)
            states, owners = sample(scene, x0, min(x1+1, int(high[0])+1))
            if x0 <= controller[0] < x1:
                p = controller-[x0, low[1], low[2]]
                states[tuple(p)], owners[tuple(p)] = palette_count, 1
            active = {face: {} for face in (2, 3, 4, 5)}
            active_layer = {}
            for offset, x in enumerate(range(x0, x1)):
                plane, owner = states[offset], owners[offset]
                values, y, z, lengths = strips(plane)
                records = np.empty(len(values), RAW)
                records['x'], records['y'], records['z'] = x, y+low[1], z+low[2]
                records['length'], records['state'] = lengths, values-1
                raw.write(records.tobytes())
                if len(values):
                    counts += np.bincount(plane.ravel(), minlength=palette_count+1)[1:]
                    actual_low = np.minimum(actual_low, [x, int(y.min()+low[1]), int(z.min()+low[2])])
                    actual_high = np.maximum(actual_high, [x, int(y.max()+low[1]), int((z+lengths-1).max()+low[2])])
                plane = plane.copy()
                owner = owner.copy()
                plane[plane == palette_count] = 0
                owner[plane == 0] = 0
                labels = (owner.astype(np.uint16) << 8)|plane
                active_layer, finished = longitudinal(labels, 5, x, low, active_layer)
                np.asarray(finished, np.int32).reshape(-1, 8).tofile(layer_stream)
                for face in range(6):
                    neighbor, neighbor_owner = np.zeros_like(plane), np.zeros_like(owner)
                    if face == 0 and offset+1 < len(states):
                        neighbor, neighbor_owner = states[offset+1], owners[offset+1]
                    elif face == 1:
                        neighbor, neighbor_owner = previous_plane, previous_owner
                    elif face == 2:
                        neighbor[:, :-1], neighbor_owner[:, :-1] = plane[:, 1:], owner[:, 1:]
                    elif face == 3:
                        neighbor[:, 1:], neighbor_owner[:, 1:] = plane[:, :-1], owner[:, :-1]
                    elif face == 4:
                        neighbor[1:], neighbor_owner[1:] = plane[:-1], owner[:-1]
                    elif face == 5:
                        neighbor[:-1], neighbor_owner[:-1] = plane[1:], owner[1:]
                    visible = (plane != 0)&((neighbor == 0)|(owner != neighbor_owner)|
                              (transparent[neighbor]&~transparent[plane]))
                    selected = np.where(visible, labels, 0)
                    if face < 2:
                        perpendicular(selected, face, x, low).tofile(mesh)
                    else:
                        active[face], finished = longitudinal(selected, face, x, low, active[face])
                        np.asarray(finished, np.int32).reshape(-1, 8).tofile(mesh)
                previous_plane, previous_owner = plane, owner
            for entries in active.values():
                np.asarray(list(entries.values()), np.int32).reshape(-1, 8).tofile(mesh)
            np.asarray(list(active_layer.values()), np.int32).reshape(-1, 8).tofile(layer_stream)
            print(f'实体条带 X={x0}..{x1-1}，累计{int(counts.sum()):,}格', flush=True)
    return raw_path, quads_path, layers_path, actual_low, actual_high, counts


def normalized(records, low):
    x, y, z = (records[name].astype(np.int32)-low[i] for i, name in enumerate(('x', 'y', 'z')))
    length = records['length'].astype(np.int32)
    segments = ((z&15)+length+15)//16
    owners = np.repeat(np.arange(len(records)), segments)
    sequence = np.arange(len(owners))-np.repeat(np.cumsum(segments)-segments, segments)
    start = np.maximum(z[owners], ((z[owners] >> 4)+sequence)*16)
    result = np.empty(len(owners), RUN)
    result['x'], result['y'], result['z'] = x[owners], y[owners], start
    result['length'] = np.minimum(z[owners]+length[owners], (start//16+1)*16)-start
    result['state'] = records['state'][owners]
    return result


def write_blueprint(raw_path, low, high, counts, palette, controller=CONTROLLER, output=BLUEPRINT):
    raw = np.memmap(raw_path, mode='r', dtype=RAW)
    run_count = 0
    for start in range(0, len(raw), 262144):
        records = raw[start:start+262144]
        z = records['z'].astype(np.int32)-low[2]
        run_count += int(np.sum(((z&15)+records['length'].astype(np.int32)+15)//16))
    size, controller = high-low+1, controller-low
    with compressed(output) as stream:
        stream.write(struct.pack('>10iH', 0x484B3357, 1, *map(int, size), *map(int, controller), int(counts.sum()), run_count, len(palette)))
        for state in palette:
            value = state.encode('utf8')
            stream.write(struct.pack('>H', len(value))+value)
        for start in range(0, len(raw), 262144):
            runs = normalized(raw[start:start+262144], low)
            stream.write(runs.tobytes())
    del raw
    return run_count


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    RESOURCE.mkdir(parents=True, exist_ok=True)
    scene = read_sources()
    save(LOG/'materials.json', scene['materials'])
    save(LOG/'actor-material-map.json', scene['mapping'])
    print('源构件与138色真实方块映射载入完成', flush=True)
    raw, quads, layers, low, high, counts = write_raw(scene)
    palette = [m['state'] for m in scene['materials']]+[MACHINE+'[facing=south]']
    geometry = dict(low=low.tolist(), high=high.tolist(), size_xyz=(high-low+1).tolist(),
                    sizeXYZ=(high-low+1).tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
                    controller_blueprint=CONTROLLER.tolist(), controller_xyz=(CONTROLLER-low).tolist(),
                    owners=scene['owners'], rig=scene['rig'], palette=palette, material_counts=counts.tolist())
    save(LOG/'geometry-scene.json', geometry)
    q = np.memmap(quads, mode='r', dtype=np.int32).reshape(-1, 8)
    l = np.memmap(layers, mode='r', dtype=np.int32).reshape(-1, 8)
    surface_counts = dict(quads=len(q), layers=len(l))
    np.savez_compressed(LOG/'w11_f5_surfaces.npz', quads=q, layers=l)
    mask_blocks, section_count = write_dynamic_mask(MASK, l, low)
    del q, l
    run_count = write_blueprint(raw, low, high, counts, palette)
    metadata = dict(id='W11', version='0005-W11-F5', controller=MACHINE,
        recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        blueprint='hk3gtl:structures/w11_candidate.bin.gz', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_quote='可以，没问题，但是你控制器打算放哪，实装一下',
        material_exception_approval_quote='按 F5 原样实装，允许 W11 专项例外',
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=digest(SOURCE/'manifest.json'), source_actors_sha256=digest(SOURCE/'actors.js'),
        source_theatre_sha256=digest(SOURCE/'theatre.js'), source_npz_sha256=digest(SOURCE/'演员整数格构件.npz'),
        source_inputs={str(path.relative_to(ROOT)).replace('\\', '/'): digest(path) for path in (
            DOMINION/'完整整数格模型.npz', DOMINION/'manifest.json',
            ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117/完整整数格模型.npz',
            ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117/manifest.json',
            SOURCE/'演员色板.json', LOG/'materials.json', LOG/'actor-material-map.json',
            Path(__file__).with_name('w11_f5_geometry.py'), Path(__file__).with_name('w11_f5_materials.py'),
            Path(__file__).with_name('w11_f5_dynamic_mask.py'))},
        size_xyz=(high-low+1).tolist(), size_wdh=(high-low+1)[[0, 2, 1]].tolist(),
        source_bounds=dict(min=low.tolist(), max=high.tolist()), source_origin_xyz=low.tolist(),
        blueprint_to_export_offset_xyz=(-low).tolist(), controller_source_xyz=CONTROLLER.tolist(),
        controller_xyz=(CONTROLLER-low).tolist(), source_facing='south',
        controller_location='正面敞口红毯入口最前沿中轴，原坐标(0,20,500)，朝外侧+Z。',
        controller_previous_state='minecraft:red_nether_bricks', controller_state=palette[-1], controller_replacements=1,
        block_count=int(counts.sum()), source_component_voxels=333666158, full_geometry=True,
        merge_priority='剧场、天窗细框、F5巨像原构件序、左人偶、右人偶，后写优先。',
        geometry_source='完整T2剧场按F5删前墙与开天窗；完整P3与F5源构件经F5层级矩阵逐区域逆映射格心体素化。',
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        target_voltage='CEV', research='RN-DIO', product='hk3gtl:distributed_industrial_contract',
        palette=palette, palette_count=len(palette), used_palette_count=int(np.count_nonzero(counts)),
        unique_block_types=len({state.split('[', 1)[0] for state, count in zip(palette, counts) if count}),
        material_counts={state: int(count) for state, count in zip(palette, counts)},
        material_count_exception=dict(approved=True, scope='仅W11 F5', unique_block_types=int(np.count_nonzero(counts))),
        runtime_format='HK3W/1；全局XYZ升序，+Z连续游程，每段不跨16格Z区段，state为0基ushort。',
        rle_record_count=run_count, blueprint_sha256=digest(BLUEPRINT), blueprint_bytes=BLUEPRINT.stat().st_size,
        animation_mask='hk3gtl:structures/w11_f5_mask.bin.gz', animation_mask_sha256=digest(MASK),
        animation_mask_sections=section_count, animation_mask_blocks=mask_blocks,
        animation_mask_scope='仅两只提线掌与双人偶逐骨参考体素，owner>1；静态剧场与俯身主像保留原生方块绘制。',
        surface_geometry=surface_counts, overworld_height_compatible=False, minimum_dimension_height=int(high[1]-low[1]+1),
        game_verified=False, jar_built=False, installed=False, game_started=False)
    save(METADATA, metadata)
    save(LOG/'资源导出回执.json', dict(**metadata, exporter_sha256=digest(Path(__file__)), metadata_sha256=digest(METADATA),
                                 geometry_sha256=digest(LOG/'geometry-scene.json'), surfaces_sha256=digest(LOG/'w11_f5_surfaces.npz')))
    for path in (raw, quads, layers):
        path.unlink()
    print(json.dumps(dict(blocks=int(counts.sum()), bounds=metadata['source_bounds'], size=metadata['size_xyz'],
                          palette=len(palette), runs=run_count, sections=section_count, **surface_counts), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
