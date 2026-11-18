from datetime import datetime
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import hashlib
import json
import shutil
import struct

import numpy as np
from PIL import Image

from package_0005_w10_author_blueprint_20261116 import mesh_part


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W10_引力奇点刑架_净空修订_A3_20261116'
OUT = ROOT / 'deliveries/0005_W10_A3_批准接入_20261116'
RESOURCE = ROOT / 'src/main/resources'
BLUEPRINT = RESOURCE / 'data/hk3gtl/structures/w10_candidate.bin.gz'
METADATA = BLUEPRINT.with_name('w10_approved.json')
MASK = BLUEPRINT.with_name('w10_a3_mask.bin.gz')
SCENE = RESOURCE / 'assets/hk3gtl/models/scene/w10_a3.json.gz'
ATLAS = RESOURCE / 'assets/hk3gtl/textures/effect/w10_a3_atlas.png'
MACHINE = 'hk3gtl:w10_gravitational_singularity_forge'
CONTROLLER = np.array([0, 64, -462])
RUN = struct.Struct('>iiiHi')
FACES = ('east', 'west', 'south', 'north', 'down', 'up')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def compressed(path):
    return gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', compresslevel=9, mtime=0)


def write_blueprint(positions, states, palette, size, controller):
    w, h, d = size
    entity_id = MACHINE.encode('utf8')
    entity = b'\x0a\x00\x00\x08\x00\x02id' + struct.pack('>H', len(entity_id)) + entity_id + b'\x00'
    delta = np.diff(positions)
    changes = np.flatnonzero((states[1:] != states[:-1]) |
        (delta != np.r_[delta[:1], delta[:-1]])) + 1
    with compressed(BLUEPRINT) as stream:
        stream.write(struct.pack('>9iH', 0x484b3350, 2, w, h, d, *map(int, controller), len(positions), len(palette)))
        for state in palette:
            encoded = state.encode('utf8')
            stream.write(struct.pack('>H', len(encoded)) + encoded)
        for start, end in zip(np.r_[0, changes], np.r_[changes, len(positions)]):
            count = int(end - start)
            state = int(states[start]) - 1
            step = int(positions[start + 1] - positions[start]) if count > 1 else 0
            tag = entity if state == len(palette) - 1 else b''
            stream.write(RUN.pack(int(positions[start]), step, count, state, len(tag)) + tag)
    return len(changes) + 1


def write_mask(positions, control_index, size):
    w, h, d = size
    nx, ny, nz = (np.array(size) + 15) // 16
    rows = np.zeros((nx * ny * nz, 64), np.uint64)
    for start in range(0, len(positions), 262144):
        current = positions[start:start + 262144]
        current = current[current != positions[control_index]]
        x, y, z = current // (h * d), current // d % h, current % d
        owner = ((x >> 4) * ny + (y >> 4)) * nz + (z >> 4)
        bit = (((y & 15) * 16 + (z & 15)) * 16 + (x & 15)).astype(np.uint64)
        np.bitwise_or.at(rows, (owner, (bit >> 6).astype(np.int64)), np.left_shift(np.uint64(1), bit & 63))
    selected = np.flatnonzero(np.any(rows, axis=1))
    sections = ((selected // (ny * nz)) << 38) | ((selected % nz) << 12) | (selected // nz % ny)
    order = np.argsort(sections)
    with compressed(MASK) as stream:
        stream.write(struct.pack('>2i', 0x5731304d, len(sections)))
        for index in order:
            stream.write(struct.pack('>q', int(sections[index])))
            stream.write(rows[selected[index]].astype('>u8').tobytes())
    return len(sections)


def write_scene(materials, geometry, low, controller):
    payload = (SOURCE / 'data.js').read_text('utf8')
    config = json.loads(gzip.decompress(base64.b64decode(json.loads(payload.split('=', 1)[1].rstrip(';\n')))))
    holes = []
    with np.load(SOURCE / '净空修订构件数据.npz') as archive:
        for index, item in enumerate(config['parts']):
            p = archive[item['id'] + '_xyz']
            selected = np.any(p != CONTROLLER, axis=1)
            if selected.all():
                continue
            part = SimpleNamespace(name=item['id'], label=item['label'],
                metadata=dict(item['metadata'], production_controller_hole=True),
                p=p[selected], states=archive[item['id'] + '_materials'][selected])
            config['parts'][index], _ = mesh_part(part, materials)
            holes.append(item['id'])
    config['data'].update(appearance_approved=True, controller_blueprint=CONTROLLER.tolist(),
        controller_export=controller.tolist(), source_facing='north', controller_status='已指定',
        stage='外观已批准；完整蓝图与动画资源已导出，尚未游戏核验',
        blueprint_to_export_offset_xyz=(-low).tolist(), sizeXYZ=geometry['actual_size_xyz'],
        bounds=geometry['bounds'])
    config['data']['effects'].update(center=[0, 222, 0], jet_y_range=[0, 444])
    quads = sum(len(face) for part in config['parts'] for material in part['starts'] for face in material)
    config['audit'].update(viewer_rendered_quads=quads, production_controller_hole=True)
    with compressed(SCENE) as stream:
        stream.write(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf8'))
    atlas = Image.new('RGBA', (16 * 64, 8 * 64))
    for material, item in enumerate(materials):
        for face, name in enumerate(FACES):
            image = Image.open(BytesIO(base64.b64decode(item['faces'][name].split(',', 1)[1])))
            slot = material * 6 + face
            atlas.paste(image.convert('RGBA').resize((64, 64), Image.Resampling.NEAREST),
                ((slot % 16) * 64, (slot // 16) * 64))
    atlas.save(ATLAS, optimize=True)
    return quads, holes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    previous = OUT / ('before-export-' + now.strftime('%H%M%S-%f'))
    for path in (BLUEPRINT, METADATA, MASK, SCENE, ATLAS):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            previous.mkdir(exist_ok=True)
            shutil.copy2(path, previous / path.name)
    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    palette = [m['state'] for m in materials]
    low = np.array(geometry['bounds']['min'])
    size = np.array(geometry['bounds']['max']) - low + 1
    w, h, d = map(int, size)
    position_arrays, state_arrays = [], []
    with np.load(SOURCE / '净空修订构件数据.npz') as archive:
        for name in geometry['components']:
            p = archive[name + '_xyz'] - low
            position_arrays.append((p[:, 0].astype(np.int64) * h + p[:, 1]) * d + p[:, 2])
            state_arrays.append(archive[name + '_materials'])
    all_positions, all_states = np.concatenate(position_arrays), np.concatenate(state_arrays)
    positions, chosen = np.unique(all_positions[::-1], return_index=True)
    states = all_states[len(all_states) - chosen - 1]
    del all_positions, all_states, chosen, position_arrays, state_arrays
    controller = CONTROLLER - low
    control_linear = int((controller[0] * h + controller[1]) * d + controller[2])
    control_index = int(np.searchsorted(positions, control_linear))
    previous_state = palette[int(states[control_index]) - 1]
    palette.append(MACHINE + '[facing=north]')
    states[control_index] = len(palette)
    counts = np.bincount(states, minlength=len(palette) + 1)[1:]
    print(f'完整蓝图：{len(positions):,}格，主控{controller.tolist()}', flush=True)
    runs = write_blueprint(positions, states, palette, [w, h, d], controller)
    print(f'HK3P/2：{runs:,}游程', flush=True)
    sections = write_mask(positions, control_index, [w, h, d])
    print(f'掩码：{sections:,}区段', flush=True)
    quads, holes = write_scene(materials, geometry, low, controller)
    metadata = dict(id='W10', version='0005-W10-A3', controller=MACHINE,
        blueprint='hk3gtl:structures/w10_candidate.bin.gz', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_basis='负责人批准W10 A3并要求游戏接入。',
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_geometry_sha256=digest(SOURCE / 'geometry.json'),
        source_npz_sha256=digest(SOURCE / '净空修订构件数据.npz'),
        source_preview_payload_sha256=digest(SOURCE / 'data.js'),
        source_clearance_sha256=digest(SOURCE / 'continuous-clearance.json'),
        source_approval_fields_preserved=True, external_approval_is_authoritative=True,
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_bounds=geometry['bounds'],
        source_origin_xyz=low.tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
        controller_source_xyz=CONTROLLER.tolist(), controller_xyz=controller.tolist(), source_facing='north',
        controller_location='北侧中央防爆堤坝最高层，替换现有镀金黑石；上邻空气、下邻镀金黑石、北面外露。',
        block_count=len(positions), component_count=len(geometry['components']),
        source_component_voxels=geometry['source_component_blocks'],
        overlap_extra_memberships=geometry['overlap_extra_memberships'], full_geometry=True,
        merge_priority='按A3构件顺序后写优先，全局去重后导出，每个实体坐标只出现一次。',
        controller_previous_state=previous_state, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=1,
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        production_recipe='hk3gtl:wonder_gravitational_singularity_matrix', target_voltage='CIV', research='RN-GSF',
        material_counts={state: int(count) for state, count in zip(palette, counts)},
        runtime_format='HK3P/2；Z最快线性坐标全局升序等差游程；主控原生方块实体NBT。',
        blueprint_linear_index='(x*sizeY+y)*sizeZ+z', rle_record_count=runs,
        blueprint_sha256=digest(BLUEPRINT),
        animation_scene='hk3gtl:models/scene/w10_a3.json.gz', animation_scene_sha256=digest(SCENE),
        animation_scene_origins='原蓝图坐标，保持A3完整构件与运动pivot。',
        animation_atlas='hk3gtl:textures/effect/w10_a3_atlas.png', animation_atlas_sha256=digest(ATLAS),
        animation_mesh_quads=quads, animation_mesh_controller_hole=True, controller_hole_components=holes,
        animation_mask='hk3gtl:structures/w10_a3_mask.bin.gz', animation_mask_sha256=digest(MASK),
        animation_mask_magic='0x5731304d', animation_mask_sections=sections,
        animation_mask_blocks=len(positions) - 1,
        animation_mask_scope='全部62构件参考姿态，排除主控；合法接口由客户端保留原生绘制。',
        animation_mask_section_index='BlockPos.asLong(sectionX,sectionY,sectionZ)',
        interface_linear_index='(y*sizeZ+z)*sizeX+x', atlas_size_pixels=[1024, 512],
        atlas_tile_pixels=64, atlas_grid=[16, 8], atlas_face_order=list(FACES),
        motion_parameters={name: item['metadata'] for name, item in geometry['components'].items()
            if 'motion_speed' in item['metadata']},
        overworld_vertical_span=384, overworld_height_compatible=h <= 384, game_verified=False)
    save(METADATA, metadata)
    for path in (BLUEPRINT, METADATA, MASK, SCENE, ATLAS):
        shutil.copy2(path, OUT / path.name)
    for name in ('geometry.json', 'materials.json', 'continuous-clearance.json', 'conflicts.json'):
        shutil.copy2(SOURCE / name, OUT / name)
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    save(OUT / '资源导出回执.json', dict(recorded_at=now.isoformat(timespec='seconds'), **metadata,
        exporter_sha256=digest(Path(__file__)), metadata_sha256=digest(METADATA),
        resources={str(path.relative_to(ROOT)).replace('\\', '/'): dict(bytes=path.stat().st_size, sha256=digest(path))
            for path in (BLUEPRINT, METADATA, MASK, SCENE, ATLAS)},
        jar_built=False, installed=False, game_started=False, automated_tests_run=False))
    print(json.dumps(dict(size_xyz=[w, h, d], controller=controller.tolist(), facing='north',
        blocks=len(positions), runs=runs, mask_sections=sections, animation_quads=quads,
        blueprint_sha256=metadata['blueprint_sha256']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
