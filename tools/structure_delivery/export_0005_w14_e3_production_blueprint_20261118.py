# -*- coding: utf-8 -*-
from datetime import datetime
import gzip
import json
from pathlib import Path
import zipfile
from zoneinfo import ZoneInfo

import numpy as np

import export_0005_w13_t2_production_blueprint_20261117 as shared


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118'
RESOURCE = ROOT / 'src/main/resources/data/hk3gtl/structures'
LOG = ROOT / 'logs/0005-w14-e3-production-20261118'
BLUEPRINT = RESOURCE / 'w14_candidate.bin.gz'
METADATA = RESOURCE / 'w14_approved.json'
LAYERS = LOG / 'layers.json.gz'
MACHINE = 'hk3gtl:w14_world_bubble_recurrence_engine'
CONTROLLER = np.array([0, 44, 610], np.int64)
CHUNK = 1_048_576
APPROVAL_QUOTE = '可以，没问题，但是你控制器打算放哪，实装一下'
MATERIAL_EXCEPTION_QUOTE = '按 E3 原样实装，允许 W14 专项例外'


def backup(now):
    paths = [path for path in (BLUEPRINT, METADATA) if path.exists()]
    if not paths:
        return dict(files=[], archive=None)
    path = LOG / ('before-export-' + now.strftime('%H%M%S-%f') + '.zip')
    files = [dict(path=str(item.relative_to(ROOT)).replace('\\', '/'), original_name=item.name,
                  bytes=item.stat().st_size, sha256=shared.digest(item)) for item in paths]
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item, info in zip(paths, files):
            archive.write(item, info['path'])
    with zipfile.ZipFile(path) as archive:
        failure = archive.testzip()
        if failure:
            raise OSError('旧资源压缩归档损坏：' + failure)
        for info in files:
            info['compressed_bytes'] = archive.getinfo(info['path']).compress_size
    return dict(files=files, archive=str(path.relative_to(ROOT)).replace('\\', '/'),
                archive_bytes=path.stat().st_size, archive_sha256=shared.digest(path))


def sorted_cells(palette_size):
    source = SOURCE / '完整整数格模型.npz'
    with np.load(source) as archive:
        states, origin, size = archive['states'], archive['origin'], archive['size']
    count = len(states)
    path = LOG / 'sorted-cells.tmp'
    packed = np.memmap(path, mode='w+', dtype=np.uint64, shape=(count,))
    w, h, d = map(int, size)
    controller = CONTROLLER-origin
    plane, current_y, rectangle_count = np.zeros((d, w), np.uint8), 0, 0
    with zipfile.ZipFile(source) as archive, archive.open('xyz.npy') as stream, \
            LAYERS.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=6, mtime=0) as layers:
        np.lib.format.read_magic(stream)
        _, _, dtype = np.lib.format.read_array_header_1_0(stream)
        layers.write(b'[')

        def finish_layer():
            nonlocal rectangle_count
            if current_y == int(controller[1]):
                plane[int(controller[2]), int(controller[0])] = 0
            rectangles = shared.layer_rectangles(plane, origin)
            rectangle_count += len(rectangles)
            item = dict(y=current_y+int(origin[1]), rectangles=rectangles.tolist())
            layers.write(((',' if current_y else '') + json.dumps(item, separators=(',', ':'))).encode('utf8'))

        for start in range(0, count, CHUNK):
            stop = min(start+CHUNK, count)
            xyz = np.frombuffer(stream.read((stop-start)*3*dtype.itemsize), dtype).reshape(-1, 3)
            linear = (xyz[:, 0].astype(np.int64)*h+xyz[:, 1])*d+xyz[:, 2]
            packed[start:stop] = (linear.astype(np.uint64) << np.uint64(8)) | states[start:stop]
            first = np.r_[0, np.flatnonzero(xyz[1:, 1] != xyz[:-1, 1])+1, len(xyz)]
            for a, b in zip(first[:-1], first[1:]):
                next_y = int(xyz[a, 1])
                while current_y < next_y:
                    finish_layer()
                    current_y += 1
                    plane.fill(0)
                plane[xyz[a:b, 2], xyz[a:b, 0]] = states[start+a:start+b]
        while current_y < h:
            finish_layer()
            current_y += 1
            plane.fill(0)
        layers.write(b']')
    counts = np.bincount(states, minlength=palette_size+2)[1:]
    del states, xyz, linear, plane
    print(f'逐层矩形{rectangle_count:,}个；完整坐标流{count:,}格，开始原地排序。', flush=True)
    packed.sort()
    packed.flush()
    return packed, path, origin, size, counts, dict(layers=h, rectangles=rectangle_count, blocks=count-1,
        path=str(LAYERS.relative_to(ROOT)).replace('\\', '/'))


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    RESOURCE.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo('Asia/Hong_Kong'))
    previous = backup(now)
    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    palette = [item['state'] for item in materials]
    packed, temporary, origin, size, counts, layers = sorted_cells(len(palette))
    w, h, d = map(int, size)
    controller = CONTROLLER-origin

    def at(source):
        x, y, z = np.array(source)-origin
        linear = int((x*h+y)*d+z)
        index = int(np.searchsorted(packed, np.uint64(linear) << np.uint64(8)))
        state = int(packed[index] & np.uint64(255)) if int(packed[index] >> np.uint64(8)) == linear else 0
        return dict(source_xyz=source, state=palette[state-1] if state else 'minecraft:air')

    access = dict(below_controller=at([0, 43, 610]), front=at([0, 44, 611]),
                  front_head=at([0, 45, 611]), front_floor=at([0, 43, 611]))
    linear = int((controller[0]*h+controller[1])*d+controller[2])
    index = int(np.searchsorted(packed, np.uint64(linear) << np.uint64(8)))
    old_state = int(packed[index] & np.uint64(255))
    previous_state = palette[old_state-1]
    palette.append(MACHINE+'[facing=south]')
    packed[index] = (np.uint64(linear) << np.uint64(8)) | np.uint64(len(palette))
    counts[old_state-1] -= 1
    counts[len(palette)-1] += 1
    shared.BLUEPRINT, shared.MACHINE = BLUEPRINT, MACHINE
    print(f'主控归一化{controller.tolist()}，朝南；完整导出HK3P/2。', flush=True)
    runs = shared.write_blueprint(packed, palette, size, controller)
    count = len(packed)
    del packed
    temporary.unlink()
    material_counts = dict.fromkeys(palette, 0)
    for state, amount in zip(palette, counts):
        material_counts[state] += int(amount)
    metadata = dict(id='W14', version='0005-W14-E3', controller=MACHINE,
        recorded_at=now.isoformat(timespec='seconds'), conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_quote=APPROVAL_QUOTE, approval_basis='负责人批准E3当前外观并要求实装。',
        external_approval_is_authoritative=True, source_approval_fields_preserved=True,
        blueprint='hk3gtl:structures/w14_candidate.bin.gz', source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=shared.digest(SOURCE / 'manifest.json'),
        source_geometry_sha256=shared.digest(SOURCE / 'geometry.json'),
        source_materials_sha256=shared.digest(SOURCE / 'materials.json'),
        source_npz_sha256=shared.digest(SOURCE / '完整整数格模型.npz'), source_nbt=manifest['nbt'],
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_bounds=geometry['bounds'],
        source_origin_xyz=origin.tolist(), blueprint_to_export_offset_xyz=(-origin).tolist(),
        controller_source_xyz=CONTROLLER.tolist(), controller_xyz=controller.tolist(), source_facing='south',
        controller_location='正面中央入口平台，源坐标(0,44,610)，朝外侧+Z。',
        controller_previous_state=previous_state, controller_state=palette[-1], controller_replacements=1,
        controller_nbt_blockentity_id=MACHINE, controller_access=access,
        block_count=count, source_block_count=manifest['blocks'], component_count=manifest['components'],
        source_component_voxels=manifest['source_component_blocks'],
        overlap_extra_memberships=manifest['source_component_blocks']-manifest['blocks'], full_geometry=True,
        geometry_source='E3完整整数格NPZ，按XYZ顺序重排并替换唯一主控标记。',
        merge_priority='沿用E3完整NPZ已完成的去重结果，每个实体坐标输出一次。',
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        target_voltage='CEV', research='RN-WCE', product='hk3gtl:civilization_cycle_model',
        palette=palette, palette_count=len(palette), used_palette_count=sum(amount > 0 for amount in material_counts.values()),
        used_palette_slots=int(np.count_nonzero(counts)),
        unique_block_types=len({state.split('[', 1)[0] for state, amount in zip(palette, counts) if amount}),
        material_counts=material_counts,
        material_count_exception=dict(approved=True, scope='仅W14 E3', unique_block_types=56,
            required_unique_block_types=59, approval_quote=MATERIAL_EXCEPTION_QUOTE,
            basis='负责人明确批准E3原样实装，保留完整尺寸、配色与现有56种方块。'),
        runtime_format='HK3P/2；XYZ全局升序、Z连续游程；唯一主控附原生方块实体NBT。',
        blueprint_linear_index='(x*sizeY+y)*sizeZ+z', rle_record_count=runs,
        blueprint_sha256=shared.digest(BLUEPRINT), blueprint_bytes=BLUEPRINT.stat().st_size,
        entity_count=0, block_crystals=manifest['block_crystals'],
        minimum_dimension_height=h, controller_relative_y_range=[-int(controller[1]), h-1-int(controller[1])],
        overworld_vertical_span=384, overworld_height_compatible=h <= 384,
        scope='批准的E3行星发动机及七维度地貌完整模型，旧A1上层未融合。',
        animation_state='运行喷嘴尾焰与供料粒子由独立客户端渲染接入。',
        game_verified=False, jar_built=False, installed=False, game_started=False)
    shared.save(METADATA, metadata)
    shared.save(LOG / 'blueprint-export.json', dict(**metadata, exporter_sha256=shared.digest(Path(__file__)),
        metadata_sha256=shared.digest(METADATA), backup=previous, layer_preview=layers,
        layer_preview_sha256=shared.digest(LAYERS), automated_tests_run=False))
    print(json.dumps(dict(blocks=count, size_xyz=[w,h,d], controller=controller.tolist(), access=access,
        runs=runs, blueprint_bytes=metadata['blueprint_bytes'], sha256=metadata['blueprint_sha256']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
