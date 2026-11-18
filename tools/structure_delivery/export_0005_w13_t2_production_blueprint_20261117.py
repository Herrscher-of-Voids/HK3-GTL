from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import struct
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117'
RESOURCE = ROOT / 'src/main/resources/data/hk3gtl/structures'
LOG = ROOT / 'logs/0005-w13-t2-production-20261117'
BLUEPRINT = RESOURCE / 'w13_candidate.bin.gz'
METADATA = RESOURCE / 'w13_approved.json'
MASK = RESOURCE / 'w13_t2_m1_mask.bin.gz'
LAYERS = LOG / 'layers.json.gz'
MACHINE = 'hk3gtl:w13_self_computing_research_mother'
CONTROLLER = np.array([0, 16, 472], np.int64)
CHUNK = 1_048_576
RUN = np.dtype([('position', '>i4'), ('step', '>i4'), ('count', '>i4'),
                ('state', '>u2'), ('entity_bytes', '>i4')])
APPROVAL_QUOTE = '可以，没问题，但是你控制器打算放哪，实装一下'
MATERIAL_EXCEPTION_QUOTE = '原样实装，允许 W13 专项例外（推荐）'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def backup(now):
    paths = [path for path in (BLUEPRINT, METADATA, MASK) if path.exists()]
    if not paths:
        return dict(files=[], archive=None)
    archive_path = LOG / ('before-export-' + now.strftime('%H%M%S-%f') + '.zip')
    files = [dict(path=str(path.relative_to(ROOT)).replace('\\', '/'),
                  original_name=path.name, bytes=path.stat().st_size, sha256=digest(path)) for path in paths]
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            archive.write(path, str(path.relative_to(ROOT)).replace('\\', '/'))
    with zipfile.ZipFile(archive_path) as archive:
        failure = archive.testzip()
        if failure:
            raise OSError('旧资源压缩归档损坏：' + failure)
        for item in files:
            item['compressed_bytes'] = archive.getinfo(item['path']).compress_size
    return dict(files=files, archive=str(archive_path.relative_to(ROOT)).replace('\\', '/'),
                archive_bytes=archive_path.stat().st_size, archive_sha256=digest(archive_path))


def layer_rectangles(plane, origin):
    nonzero = plane != 0
    starts, ends = nonzero.copy(), nonzero.copy()
    starts[:, 1:] &= plane[:, 1:] != plane[:, :-1]
    ends[:, :-1] &= plane[:, :-1] != plane[:, 1:]
    z, x = np.nonzero(starts)
    width = np.nonzero(ends)[1]-x+1
    values = plane[z, x]
    order = np.lexsort((z, width, x, values))
    values, z, x, width = (array[order] for array in (values, z, x, width))
    first = np.flatnonzero(np.r_[True, (values[1:] != values[:-1]) | (x[1:] != x[:-1]) |
                                 (width[1:] != width[:-1]) | (z[1:] != z[:-1]+1)]) if len(values) else np.empty(0, int)
    depth = np.diff(np.r_[first, len(values)])
    return np.c_[values[first].astype(np.int32)-1, x[first]+origin[0], z[first]+origin[2], width[first], depth]


def write_mask(rows, section_size, count):
    _, ny, nz = map(int, section_size)
    selected = np.flatnonzero(np.any(rows, axis=1))
    keys = ((selected // (ny*nz)) << 38) | ((selected % nz) << 12) | (selected // nz % ny)
    with MASK.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=9, mtime=0) as stream:
        stream.write(struct.pack('>2i', 0x5731334D, len(selected)))
        for index in np.argsort(keys):
            stream.write(struct.pack('>q', int(keys[index])))
            stream.write(rows[selected[index]].astype('>u8').tobytes())
    return dict(blocks=count, sections=len(selected), magic='0x5731334d', sha256=digest(MASK), bytes=MASK.stat().st_size)


def sorted_cells(geometry):
    source = SOURCE / '完整整数格模型.npz'
    with np.load(source) as archive:
        states, origin, size = archive['states'], archive['origin'], archive['size']
    count = len(states)
    packed_path = LOG / 'sorted-cells.tmp'
    packed = np.memmap(packed_path, mode='w+', dtype=np.uint64, shape=(count,))
    w, h, d = map(int, size)
    controller = CONTROLLER-origin
    section_size = (size+15)//16
    rows = np.zeros((int(np.prod(section_size)), 64), np.uint64)
    owner_mask = np.array([part['id']=='eye_display' or part['id'].startswith('cable_') for part in geometry['components']])
    dynamic_blocks = 0
    plane, current_y, rectangle_count = np.zeros((d,w), np.uint8), 0, 0
    with zipfile.ZipFile(source) as archive, archive.open('xyz.npy') as stream, archive.open('owners.npy') as owners_stream, \
            LAYERS.open('wb') as layers_raw, gzip.GzipFile(filename='', fileobj=layers_raw, mode='wb', compresslevel=6, mtime=0) as layers:
        np.lib.format.read_magic(stream)
        _, _, dtype = np.lib.format.read_array_header_1_0(stream)
        np.lib.format.read_magic(owners_stream)
        _, _, owner_dtype = np.lib.format.read_array_header_1_0(owners_stream)
        layers.write(b'[')

        def finish_layer():
            nonlocal rectangle_count
            if current_y==int(controller[1]):
                plane[int(controller[2]),int(controller[0])] = 0
            rectangles = layer_rectangles(plane, origin)
            rectangle_count += len(rectangles)
            item = dict(y=current_y+int(origin[1]), rectangles=rectangles.tolist())
            layers.write(((',' if current_y else '') + json.dumps(item, separators=(',', ':'))).encode('utf8'))

        for start in range(0, count, CHUNK):
            stop = min(start + CHUNK, count)
            xyz = np.frombuffer(stream.read((stop-start) * 3 * dtype.itemsize), dtype).reshape(-1, 3)
            owners = np.frombuffer(owners_stream.read((stop-start)*owner_dtype.itemsize), owner_dtype)
            linear = (xyz[:, 0].astype(np.int64) * h + xyz[:, 1]) * d + xyz[:, 2]
            packed[start:stop] = (linear.astype(np.uint64) << np.uint64(8)) | states[start:stop]
            selected = xyz[owner_mask[owners]]
            dynamic_blocks += len(selected)
            xx, yy, zz = (selected[:, i].astype(np.int64) for i in range(3))
            section = ((xx >> 4)*int(section_size[1])+(yy >> 4))*int(section_size[2])+(zz >> 4)
            bit = (((yy & 15)*16+(zz & 15))*16+(xx & 15)).astype(np.uint64)
            np.bitwise_or.at(rows, (section, (bit >> 6).astype(np.int64)), np.left_shift(np.uint64(1), bit & 63))
            first = np.r_[0, np.flatnonzero(xyz[1:,1] != xyz[:-1,1])+1, len(xyz)]
            for a, b in zip(first[:-1], first[1:]):
                next_y = int(xyz[a,1])
                while current_y<next_y:
                    finish_layer()
                    current_y += 1
                    plane.fill(0)
                plane[xyz[a:b,2],xyz[a:b,0]] = states[start+a:start+b]
        while current_y<h:
            finish_layer()
            current_y += 1
            plane.fill(0)
        layers.write(b']')
    mask = write_mask(rows, section_size, dynamic_blocks)
    counts = np.bincount(states, minlength=30)[1:]
    del states, xyz, linear, owners, rows, plane, selected
    layers_info = dict(layers=h, rectangles=rectangle_count, blocks=count-1, path=str(LAYERS.relative_to(ROOT)).replace('\\', '/'))
    print(f'逐层矩形{rectangle_count:,}个；动态遮罩{dynamic_blocks:,}格、{mask["sections"]:,}区段。', flush=True)
    print(f'完整坐标流写入：{count:,}格；开始原地排序。', flush=True)
    packed.sort()
    packed.flush()
    return packed, packed_path, origin, size, counts, mask, layers_info


def write_blueprint(packed, palette, size, controller):
    entity_id = MACHINE.encode('utf8')
    entity = b'\x0a\x00\x00\x08\x00\x02id' + struct.pack('>H', len(entity_id)) + entity_id + b'\x00'
    control_state = len(palette) - 1
    run_count = 0

    def write_runs(stream, runs):
        nonlocal run_count
        selected = np.flatnonzero(runs['state'] == control_state)
        if len(selected):
            at = int(selected[0])
            runs['entity_bytes'][at] = len(entity)
            stream.write(runs[:at].tobytes())
            stream.write(runs[at:at+1].tobytes() + entity)
            stream.write(runs[at+1:].tobytes())
        else:
            stream.write(runs.tobytes())
        run_count += len(runs)

    with BLUEPRINT.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=9, mtime=0) as stream:
        stream.write(struct.pack('>9iH', 0x484B3350, 2, *map(int, size), *map(int, controller), len(packed), len(palette)))
        for state in palette:
            value = state.encode('utf8')
            stream.write(struct.pack('>H', len(value)) + value)
        pending = np.empty(0, RUN)
        for start in range(0, len(packed), CHUNK):
            current = packed[start:start+CHUNK]
            positions, states = current >> 8, (current & 255).astype(np.uint16)-1
            first = np.r_[0, np.flatnonzero((positions[1:] != positions[:-1]+1) | (states[1:] != states[:-1]))+1]
            runs = np.zeros(len(first), RUN)
            runs['position'], runs['step'] = positions[first], 1
            runs['count'], runs['state'] = np.diff(np.r_[first, len(current)]), states[first]
            if len(pending):
                if pending['state'][0] == runs['state'][0] and int(pending['position'][0])+int(pending['count'][0]) == runs['position'][0]:
                    runs['position'][0] = pending['position'][0]
                    runs['count'][0] += pending['count'][0]
                else:
                    write_runs(stream, pending)
            write_runs(stream, runs[:-1])
            pending = runs[-1:].copy()
        write_runs(stream, pending)
    return run_count


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    RESOURCE.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    previous = backup(now)
    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    palette = [material['state'] for material in materials]
    packed, temporary, origin, size, counts, mask, layers = sorted_cells(geometry)
    w, h, d = map(int, size)
    controller = CONTROLLER - origin
    linear = int((controller[0] * h + controller[1]) * d + controller[2])
    control_index = int(np.searchsorted(packed, np.uint64(linear) << np.uint64(8)))
    old_state = int(packed[control_index] & np.uint64(255))
    previous_state = palette[old_state-1]
    palette.append(MACHINE + '[facing=south]')
    packed[control_index] = (np.uint64(linear) << np.uint64(8)) | np.uint64(len(palette))
    counts[old_state-1] -= 1
    counts[len(palette)-1] += 1
    print(f'主控归一化：{controller.tolist()}，朝南；完整导出HK3P/2。', flush=True)
    runs = write_blueprint(packed, palette, size, controller)
    count = len(packed)
    del packed
    temporary.unlink()
    metadata = dict(
        id='W13', version='0005-W13-T2-M1', controller=MACHINE,
        recorded_at=now.isoformat(timespec='seconds'),
        blueprint='hk3gtl:structures/w13_candidate.bin.gz', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_basis='负责人本轮批准T2-M1外观与动画并要求实装，沿用原稿20种方块与现有配色。',
        approval_quote=APPROVAL_QUOTE, material_exception_approval_quote=MATERIAL_EXCEPTION_QUOTE,
        source_approval_fields_preserved=True,
        external_approval_is_authoritative=True,
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=digest(SOURCE / 'manifest.json'),
        source_geometry_sha256=digest(SOURCE / 'geometry.json'),
        source_materials_sha256=digest(SOURCE / 'materials.json'),
        source_npz_sha256=digest(SOURCE / '完整整数格模型.npz'),
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_bounds=geometry['bounds'],
        source_origin_xyz=origin.tolist(), blueprint_to_export_offset_xyz=(-origin).tolist(),
        controller_source_xyz=CONTROLLER.tolist(), controller_xyz=controller.tolist(), source_facing='south',
        controller_location='前方主缆检修端子正面，源坐标(0,16,472)，朝外侧+Z。',
        controller_previous_state=previous_state, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=1,
        block_count=count, source_block_count=geometry['blocks'],
        component_count=len(geometry['components']), source_component_voxels=geometry['source_component_voxels'],
        overlap_extra_memberships=geometry['shared_component_cells'], full_geometry=True,
        geometry_source='T2完整整数格NPZ，保持全部静态实体，仅按XYZ顺序重排并替换唯一主控标记。',
        merge_priority='沿用T2完整NPZ已完成的去重结果，每个实体坐标输出一次。',
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        target_voltage='CEV', research='RN-ASR', product='hk3gtl:bounded_research_model',
        palette=palette, palette_count=len(palette), used_palette_count=int(np.count_nonzero(counts)),
        unique_block_types=len({state.split('[', 1)[0] for state, amount in zip(palette, counts) if amount}),
        material_counts={state: int(amount) for state, amount in zip(palette, counts)},
        source_scale_metrics=geometry['scale_comparison']['metrics'],
        material_count_exception=dict(approved=True, scope='仅W13 T2-M1', unique_block_types=20,
                                      approval_quote=MATERIAL_EXCEPTION_QUOTE,
                                      basis='负责人明确选中20种方块原稿，原样实装；不添加材料凑数。'),
        runtime_format='HK3P/2；XYZ全局升序、Z连续游程；唯一主控附原生方块实体NBT。',
        blueprint_linear_index='(x*sizeY+y)*sizeZ+z', rle_record_count=runs,
        blueprint_sha256=digest(BLUEPRINT), blueprint_bytes=BLUEPRINT.stat().st_size,
        animation_mask='hk3gtl:structures/w13_t2_m1_mask.bin.gz', animation_mask_sha256=mask['sha256'],
        animation_mask_magic=mask['magic'], animation_mask_sections=mask['sections'], animation_mask_blocks=mask['blocks'],
        animation_mask_scope='最终NPZ中eye_display与cable_XX_[12]所有实体格，保留后写主控端子；合法接口由客户端原生绘制。',
        minimum_dimension_height=h, dimension_requirement='完整高度1213格，须在可容纳整座结构的维度建造。',
        controller_relative_y_range=[-int(controller[1]), h-1-int(controller[1])],
        overworld_vertical_span=384, overworld_height_compatible=False,
        animation_state='静态完整实体沿用T2；T2-M1眼珠与分节粗缆动画由独立渲染资源接入。',
        game_verified=False, jar_built=False, installed=False, game_started=False)
    save(METADATA, metadata)
    receipt = dict(**metadata, exporter_sha256=digest(Path(__file__)), metadata_sha256=digest(METADATA),
                   backup=previous, layer_preview=layers, layer_preview_sha256=digest(LAYERS), automated_tests_run=False)
    save(LOG / 'blueprint-export.json', receipt)
    print(json.dumps(dict(blocks=count, size_xyz=[w,h,d], controller=controller.tolist(),
                          source_state=previous_state, runs=runs, blueprint_bytes=metadata['blueprint_bytes'],
                          sha256=metadata['blueprint_sha256']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
