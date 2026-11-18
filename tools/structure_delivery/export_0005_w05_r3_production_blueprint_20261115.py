"""将批准的W05 R3原始构件合并为完整生产蓝图。"""
from datetime import datetime
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import struct

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_七处穿模修订_R3_20261115'
LOG = ROOT / 'logs/0005-w05-r3-runtime-20261115'
DESTINATION = ROOT / 'src/main/resources/data/hk3gtl/structures/w05_candidate.bin.gz'
METADATA = DESTINATION.with_name('w05_approved.json')
MACHINE = 'hk3gtl:w05_ideal_fluid_circulation_array'
RUN = struct.Struct('>iiiHi')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    LOG.mkdir(exist_ok=True)
    now = datetime.now().astimezone()
    backup = LOG / ('before-runtime-' + now.strftime('%H%M%S-%f'))
    backup.mkdir()
    for path in (DESTINATION, METADATA):
        shutil.copy2(path, backup / path.name)
    meta = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    materials = json.loads((SOURCE / 'materials/materials.json').read_text('utf8'))
    palette = list(dict.fromkeys(m['state'] for m in materials))
    slots = np.array([0, *[palette.index(m['state']) + 1 for m in materials]], np.uint8)
    low = np.array(meta['occupied_bounds_xyz']['min'])
    size = np.array(meta['occupied_bounds_xyz']['max']) - low + 1
    w, h, d = map(int, size)
    cube = np.zeros(w * h * d, np.uint8)
    with np.load(SOURCE / '原始构件数据.npz') as archive:
        for part in meta['components']:
            name = part['id']
            p = archive[name + '_xyz'] - low
            linear = (p[:, 0] * h + p[:, 1]) * d + p[:, 2]
            cube[linear] = slots[archive[name + '_materials']]
    controller_source = [0, 12, -345]
    controller = np.array(controller_source) - low
    cx, cy, cz = map(int, controller)
    control_linear = (cx * h + cy) * d + cz
    previous_marker = palette[int(cube[control_linear]) - 1]
    palette.append(MACHINE + '[facing=north]')
    cube[control_linear] = len(palette)
    counts = np.bincount(cube, minlength=len(palette) + 1)[1:]
    block_count = int(counts.sum())
    entity_id = MACHINE.encode('utf8')
    entity = b'\x0a\x00\x00\x08\x00\x02id' + struct.pack('>H', len(entity_id)) + entity_id + b'\x00'
    temporary = DESTINATION.with_suffix('.gz.r3-pending')
    runs = 0
    with temporary.open('wb') as output:
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', compresslevel=9, mtime=0) as stream:
            stream.write(struct.pack('>9iH', 0x484b3350, 2, w, h, d, cx, cy, cz, block_count, len(palette)))
            for state in palette:
                encoded = state.encode('utf8')
                stream.write(struct.pack('>H', len(encoded)) + encoded)
            positions = np.flatnonzero(cube)
            states = cube[positions] - 1
            delta = np.diff(positions)
            changes = np.flatnonzero((states[1:] != states[:-1]) |
                (delta != np.r_[delta[:1], delta[:-1]])) + 1
            for start, end in zip(np.r_[0, changes], np.r_[changes, len(positions)]):
                count = int(end - start)
                state = int(states[start])
                step = int(positions[start + 1] - positions[start]) if count > 1 else 0
                tag = entity if state == len(palette) - 1 else b''
                stream.write(RUN.pack(int(positions[start]), step, count, state, len(tag)) + tag)
                runs += 1
    temporary.replace(DESTINATION)
    metadata = dict(id='W05', version='0005-R3', controller=MACHINE,
        blueprint='hk3gtl:structures/w05_candidate.bin.gz', conversation='0005',
        conversation_id=meta['conversation_id'], appearance_approved=True,
        approval_basis='负责人：可以就这台吧，接入吧，你主控打算放哪里',
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=digest(SOURCE / 'manifest.json'),
        source_npz_sha256=digest(SOURCE / '原始构件数据.npz'),
        source_manifest_approved_field_preserved=True, external_approval_is_authoritative=True,
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_origin_xyz=low.tolist(),
        controller_source_xyz=controller_source, controller_xyz=controller.tolist(),
        source_facing='north', block_count=block_count, full_geometry=True,
        source_component_voxels=meta['source_component_voxels'],
        overlap_extra_memberships=meta['source_component_voxels'] - block_count,
        overlap_material_policy='沿用既有整机生成顺序，后构件覆盖前构件；正常嵌接合并为唯一方块，外形不裁切。',
        fixed_interface_positions=[], production_recipe='hk3gtl:wonder_ideal_flow_exchange_matrix',
        target_voltage='WSV', research='RN-IFF',
        interface_policy='保留既有自由通用接口规则；本蓝图不预装固定仓室。',
        material_counts={state: int(count) for state, count in zip(palette, counts)},
        controller_previous_state=previous_marker, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=1,
        runtime_format='HK3P/2；线性坐标全局升序等差游程，兼容稀疏蓝图二分查找；主控原生方块实体NBT',
        rle_record_count=runs, blueprint_sha256=digest(DESTINATION),
        native_animation_integrated=False,
        animation_scope='本次接入完整静态方块蓝图；R3叶轮、陀螺仪和流场动画仍仅网页演示。',
        game_verified=False)
    save(METADATA, metadata)
    receipt = dict(recorded_at=now.isoformat(timespec='seconds'), **metadata,
        destination=str(DESTINATION.relative_to(ROOT)).replace('\\', '/'),
        destination_bytes=DESTINATION.stat().st_size, previous_runtime_snapshot=str(backup),
        runtime_metadata_sha256=digest(METADATA), exporter_sha256=digest(Path(__file__)),
        jar_built=False, installed=False, game_started=False, automated_tests_run=False)
    save(LOG / 'blueprint-export.json', receipt)
    print(json.dumps(dict(size_xyz=[w, h, d], controller=controller.tolist(), facing='north',
        blocks=block_count, materials=metadata['material_counts'], runs=runs,
        bytes=DESTINATION.stat().st_size), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
