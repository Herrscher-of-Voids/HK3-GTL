from datetime import datetime
from io import BytesIO
from pathlib import Path
import base64
import gzip
import json
import shutil

import numpy as np
from PIL import Image

import export_0005_w10_a3_production_blueprint_20261116 as shared


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W12_三环翻转_A3_20261116'
OUT = ROOT / 'deliveries/0005_W12_A3_批准接入_20261116'
RESOURCE = ROOT / 'src/main/resources'
BLUEPRINT = RESOURCE / 'data/hk3gtl/structures/w12_candidate.bin.gz'
METADATA = BLUEPRINT.with_name('w12_approved.json')
MASK = BLUEPRINT.with_name('w12_a3_mask.bin.gz')
SCENE = RESOURCE / 'assets/hk3gtl/models/scene/w12_a3.json.gz'
ATLAS = RESOURCE / 'assets/hk3gtl/textures/effect/w12_a3_atlas.png'
MACHINE = 'hk3gtl:w12_global_energy_constraint_wall'
CONTROLLER = np.array([531, 50, 10])
FACES = shared.FACES


def write_scene(materials, geometry, low, controller):
    payload = (SOURCE / 'data.js').read_text('utf8')
    config = json.loads(gzip.decompress(base64.b64decode(json.loads(payload.split('=', 1)[1].rstrip(';\n')))))
    marker = next(i for i, material in enumerate(materials) if material['state'] == 'minecraft:redstone_block')
    holes = []
    for part in config['parts']:
        if any(part['starts'][marker]):
            for key in ('starts', 'lengths', 'spans'):
                part[key][marker] = [[] for _ in range(6)]
            part['metadata']['production_controller_hole'] = True
            holes.append(part['id'])
    config['data'].update(appearance_approved=True, controller_blueprint=CONTROLLER.tolist(),
        controller_export=controller.tolist(), source_facing='north', controller_status='已指定',
        stage='A3外观已批准，完整蓝图与三环翻转资源已导出',
        blueprint_to_export_offset_xyz=(-low).tolist(), sizeXYZ=geometry['actual_size_xyz'], bounds=geometry['bounds'])
    config['data']['effects']['center'] = config['data']['core_center']
    quads = sum(len(face) for part in config['parts'] for material in part['starts'] for face in material)
    config['audit'].update(viewer_rendered_quads=quads, production_controller_hole=True)
    with shared.compressed(SCENE) as stream:
        stream.write(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode('utf8'))
    atlas = Image.new('RGBA', (1024, 512))
    for material, item in enumerate(materials):
        for face, name in enumerate(FACES):
            image = Image.open(BytesIO(base64.b64decode(item['faces'][name].split(',', 1)[1])))
            slot = material * 6 + face
            atlas.paste(image.convert('RGBA').resize((64, 64), Image.Resampling.NEAREST),
                ((slot % 16) * 64, (slot // 16) * 64))
    atlas.save(ATLAS, optimize=True)
    return quads, holes


def controller_neighbors(positions, states, palette, controller, size):
    _, h, d = size
    result = {}
    for name, step in zip(('east', 'west', 'up', 'down', 'south', 'north'),
                          ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1])):
        x, y, z = controller + step
        linear = int((x * h + y) * d + z)
        index = int(np.searchsorted(positions, linear))
        result[name] = palette[int(states[index]) - 1] if positions[index] == linear else 'minecraft:air'
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    previous = OUT / ('before-export-' + now.strftime('%H%M%S-%f'))
    resources = (BLUEPRINT, METADATA, MASK, SCENE, ATLAS)
    for path in resources:
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
    with np.load(SOURCE / '修订构件数据.npz') as archive:
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
    shared.BLUEPRINT, shared.MASK, shared.MACHINE = BLUEPRINT, MASK, MACHINE
    runs = shared.write_blueprint(positions, states, palette, [w, h, d], controller)
    print(f'HK3P/2：{runs:,}游程', flush=True)
    sections = shared.write_mask(positions, control_index, [w, h, d])
    with gzip.open(MASK, 'rb') as stream:
        mask_bytes = bytearray(stream.read())
    mask_bytes[:4] = bytes.fromhex('5731324d')
    with shared.compressed(MASK) as stream:
        stream.write(mask_bytes)
    del mask_bytes
    print(f'掩码：{sections:,}区段', flush=True)
    quads, holes = write_scene(materials, geometry, low, controller)
    neighbors = controller_neighbors(positions, states, palette, controller, [w, h, d])
    metadata = dict(id='W12', version='0005-W12-A3', controller=MACHINE,
        blueprint='hk3gtl:structures/w12_candidate.bin.gz', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', appearance_approved=True,
        approval_basis='负责人明确批准W12 A3并要求接入完整机器与特效。',
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_geometry_sha256=shared.digest(SOURCE / 'geometry.json'),
        source_npz_sha256=shared.digest(SOURCE / '修订构件数据.npz'),
        source_preview_payload_sha256=shared.digest(SOURCE / 'data.js'),
        source_clearance_sha256=shared.digest(SOURCE / 'continuous-clearance.json'),
        source_approval_fields_preserved=True, external_approval_is_authoritative=True,
        size_xyz=[w, h, d], size_wdh=[w, d, h], source_bounds=geometry['bounds'],
        source_origin_xyz=low.tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
        controller_source_xyz=CONTROLLER.tolist(), controller_xyz=controller.tolist(), source_facing='north',
        controller_location='负Z前侧中央开放式黑白金审判操作台，替换原红石定位块，台面上方独立放置。',
        controller_neighbors=neighbors, controller_entry='玩家从前侧台阶登上Y49台面，直接操作Y50主控。',
        block_count=len(positions), component_count=len(geometry['components']),
        source_component_voxels=geometry['source_component_blocks'],
        overlap_extra_memberships=geometry['overlap_extra_memberships'], full_geometry=True,
        merge_priority='按A3构件顺序后写优先，全局去重后导出，每个实体坐标只出现一次。',
        controller_previous_state=previous_state, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=1,
        fixed_interface_positions=[], interface_policy='除主控外，全部实体格均可替换合法通用接口，朝向自选。',
        production_recipe='hk3gtl:wonder_global_energy_constraint_matrix', target_voltage='CIV', research='RN-ECB',
        material_counts={state: int(count) for state, count in zip(palette, counts)},
        runtime_format='HK3P/2；Z最快线性坐标全局升序等差游程；主控原生方块实体NBT。',
        blueprint_linear_index='(x*sizeY+y)*sizeZ+z', rle_record_count=runs,
        blueprint_sha256=shared.digest(BLUEPRINT),
        animation_scene='hk3gtl:models/scene/w12_a3.json.gz', animation_scene_sha256=shared.digest(SCENE),
        animation_scene_origins='原蓝图坐标，保持A3全部构件及球心翻转pivot。',
        animation_atlas='hk3gtl:textures/effect/w12_a3_atlas.png', animation_atlas_sha256=shared.digest(ATLAS),
        animation_mesh_quads=quads, animation_mesh_controller_hole=True, controller_hole_components=holes,
        animation_mask='hk3gtl:structures/w12_a3_mask.bin.gz', animation_mask_sha256=shared.digest(MASK),
        animation_mask_magic='0x5731324d', animation_mask_sections=sections,
        animation_mask_blocks=len(positions) - 1,
        animation_mask_scope='全部100构件参考姿态，排除主控；合法接口由客户端保留原生绘制。',
        animation_mask_section_index='BlockPos.asLong(sectionX,sectionY,sectionZ)',
        interface_linear_index='(y*sizeZ+z)*sizeX+x', atlas_size_pixels=[1024, 512],
        atlas_tile_pixels=64, atlas_grid=[16, 8], atlas_face_order=list(FACES),
        motion_parameters={name: item['metadata'] for name, item in geometry['components'].items()
            if 'motion_speed' in item['metadata']},
        known_pending=['核心以外链链与链廊固定交叠', '冠环与四内塔、垂丝与墙塔固定交叠',
            '1063×847占地比W10少240格，规模递增待修订'],
        overworld_vertical_span=384, overworld_height_compatible=h <= 384,
        overworld_controller_y_range=[-64 + int(controller[1]), 320 - (h - int(controller[1]))], game_verified=False)
    shared.save(METADATA, metadata)
    for path in resources:
        shutil.copy2(path, OUT / path.name)
    for name in ('geometry.json', 'materials.json', 'continuous-clearance.json', 'motion.json'):
        shutil.copy2(SOURCE / name, OUT / name)
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    shared.save(OUT / '资源导出回执.json', dict(recorded_at=now.isoformat(timespec='seconds'), **metadata,
        exporter_sha256=shared.digest(Path(__file__)), metadata_sha256=shared.digest(METADATA),
        resources={str(path.relative_to(ROOT)).replace('\\', '/'): dict(bytes=path.stat().st_size, sha256=shared.digest(path))
            for path in resources}, jar_built=False, installed=False, game_started=False, automated_tests_run=False))
    print(json.dumps(dict(size_xyz=[w, h, d], controller=controller.tolist(), facing='north',
        neighbors=neighbors, blocks=len(positions), runs=runs, mask_sections=sections, animation_quads=quads,
        blueprint_sha256=metadata['blueprint_sha256']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
