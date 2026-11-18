import base64
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np

import package_0005_w10_author_blueprint_20261116 as original
from w10_core_20261116 import cage


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W10_引力奇点刑架_工业材质_A2_20261116'
OUT = ROOT / 'deliveries/0005_W10_引力奇点刑架_净空修订_A3_20261116'
LOG = ROOT / 'logs/0005-w10-clearance-a3-20261116'
RINGS = ('asteroid_belt_01', 'asteroid_belt_02')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def current_notes(notes):
    replacements = {
        '双碎星环以原文': 'A3按负责人决定将双碎星环整体上移40格，共同中心由(0,190,0)变为(0,230,0)，半径220/310、倾角25度、形状、材质、旋转轴和速度保持。',
        '黄金拘束笼选择': 'A3黄金正二十面体拘束笼中心保持(0,222,0)，外接球半径由80扩为100，名义直径200；重新生成7格金梁与半径6格节点，梁厚和节点尺寸保持。',
        '运动构件交集为': '参考姿态逐格交集按A3完整构件重算，连续旋转净空另见continuous-clearance.json；盘内缘嵌入事件视界按原案保留。',
        'A2保留A1全部': 'A3逐项复用A2的13种原生方块与PNG贴图，黑金、冷白、琥珀、紫黑配色及全部材质状态保持。',
    }
    return [next((replacement for prefix, replacement in replacements.items() if note.startswith(prefix)), note) for note in notes]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    encoded = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';\n'))
    config = json.loads(gzip.decompress(base64.b64decode(encoded)))
    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    geometry['baseline_material_replacements'] = geometry.pop('material_replacements')
    geometry['material_changes_from_a2'] = []
    materials = config['materials']
    archive = np.load(SOURCE / '工业材质构件数据.npz')
    parts = []
    golden_cage = cage(100)
    golden_cage.metadata.update(circumradius=100, beam_radius=3.5, node_radius=6, revision='A3')
    old_cage_quads = 0
    for item in config['parts']:
        name = item['id']
        part = SimpleNamespace(name=name, label=item['label'], p=archive[name + '_xyz'],
            states=archive[name + '_materials'], metadata=deepcopy(item['metadata']))
        if name in RINGS:
            part.p = part.p + np.array([0, 40, 0], np.int32)
            part.metadata.update(pivot=[0, 230, 0], translation_from_a2=[0, 40, 0])
            item['origin'][1] += 40
            item['metadata'] = part.metadata
        if name == golden_cage.name:
            old_cage_quads = sum(len(face) for material in item['starts'] for face in material)
            part = golden_cage
            replacement, cage_quads = original.mesh_part(part, materials)
            item.clear()
            item.update(replacement)
        parts.append(part)

    low = np.min([part.p.min(0) for part in parts], axis=0)
    high = np.max([part.p.max(0) for part in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size

    def encode(points):
        return ((points[:, 1].astype(np.int64) - low[1]) * d + points[:, 2] - low[2]) * w + points[:, 0] - low[0]

    part_keys = [encode(part.p) for part in parts]
    all_keys = np.concatenate(part_keys)
    all_states = np.concatenate([part.states for part in parts])
    keys, chosen = np.unique(all_keys[::-1], return_index=True)
    states = all_states[len(all_states) - chosen - 1]
    del all_keys, all_states, chosen
    print(f'A3合并完成：{len(keys):,}格，{w}×{d}×{h}', flush=True)

    intersections, cage_connections = [], []
    for index, moving in enumerate(parts):
        is_moving = 'motion_speed' in moving.metadata
        if not is_moving and moving.name != golden_cage.name:
            continue
        lo, hi = moving.p.min(0), moving.p.max(0)
        for other_index, fixed in enumerate(parts):
            if index == other_index or (is_moving and 'motion_speed' in fixed.metadata and other_index < index):
                continue
            if not is_moving and 'motion_speed' in fixed.metadata:
                continue
            if np.any(fixed.p.max(0) < lo) or np.any(fixed.p.min(0) > hi):
                continue
            selected = np.all((fixed.p >= lo) & (fixed.p <= hi), axis=1)
            overlap = np.intersect1d(part_keys[index], part_keys[other_index][selected], assume_unique=True)
            if len(overlap):
                record = dict(moving=moving.name, other=fixed.name, reference_pose_blocks=len(overlap),
                    example_blueprint_xyz=[int(overlap[0] % w + low[0]), int(overlap[0] // (w * d) + low[1]), int(overlap[0] // w % d + low[2])])
                (intersections if is_moving else cage_connections).append(record)
    del part_keys

    data = config['data']
    data.update(candidate='A3', stage='净空修订方块预览待审', sizeXYZ=size, size=size,
        bounds=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
        geometry_revision='双环上移40格；金笼名义直径200；949×949占地保持',
        material_revision='原样复用A2的13种方块状态及PNG贴图')
    data['views']['core']['center'][1] = 230
    data['views']['cage'] = dict(label='吸积盘与金笼', direction=[-.8, .48, -1.2], center=[0, 222, 0], half=[112, 106, 112])
    quads = config['audit']['viewer_rendered_quads'] - old_cage_quads + cage_quads
    config['audit'].update(viewer_rendered_quads=quads, blocks=len(keys))
    counts = np.bincount(states, minlength=len(materials) + 1)[1:]
    geometry.update(candidate='A3', stage='净空修订方块预览待审', actual_size_xyz=size, actual_size_wdh=[w, d, h],
        bounds=data['bounds'], blocks=len(keys), footprint_area=w * d, bounding_box_volume=w * d * h,
        actual_height=h, unique_block_types=len(np.unique(states)),
        source_component_blocks=sum(len(part.p) for part in parts),
        overlap_extra_memberships=sum(len(part.p) for part in parts) - len(keys), surface_quads=quads,
        material_counts={material['state']: int(count) for material, count in zip(materials, counts)},
        non_vanilla_blocks=sum(int(count) for material, count in zip(materials, counts) if not material['state'].startswith('minecraft:')),
        components={part.name: dict(label=part.label, blocks=len(part.p),
            bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist()), metadata=part.metadata) for part in parts},
        source_notes=current_notes(geometry['source_notes']), reference_pose_moving_intersections=intersections,
        static_cage_connections=cage_connections, geometry_source=str(SOURCE / 'geometry.json'), geometry_positions_modified=True,
        approved_changes=dict(ring_translation_xyz=[0, 40, 0], ring_pivot=[0, 230, 0], cage_circumradius=100,
            cage_nominal_diameter=200, cage_center=[0, 222, 0], cage_beam_radius=3.5, cage_node_radius=6,
            preserved_footprint_wd=[949, 949], preserved_colors=['黑金', '冷白', '琥珀', '紫黑']),
        clearance_report='continuous-clearance.json')
    geometry['source_notes'].append('A3仅变更双环整体位置与金笼半径；固定塔桥、穹顶、重锤、吸积盘及黑球坐标沿用A2。完整构件重新合并NBT，原位置的固定结构按独立构件恢复。')
    payload = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W10_STATIC_PAYLOAD=' + json.dumps(payload) + ';\n', 'utf8')
    shutil.copy2(SOURCE / 'materials.json', OUT / 'materials.json')
    np.savez_compressed(OUT / '净空修订构件数据.npz', **{key: values for part in parts for key, values in
        ((part.name + '_xyz', part.p), (part.name + '_materials', part.states))})
    print('A3构件数据与网页载荷就绪', flush=True)
    original.OUT = OUT
    original.export_nbt(keys, states, size, materials)
    (OUT / 'W10-引力奇点刑架-A1.nbt').replace(OUT / 'W10-引力奇点刑架-A3.nbt')
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / 'conflicts.json', dict(source='负责人批准双环上移40格、金笼外扩', notes=geometry['source_notes'],
        reference_pose_moving_intersections=intersections, static_cage_connections=cage_connections,
        continuous_clearance_report='continuous-clearance.json'))
    for name in ('w10_core_20261116.py', Path(__file__).name):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    files = ['data.js', 'materials.json', 'geometry.json', 'conflicts.json', '净空修订构件数据.npz', 'W10-引力奇点刑架-A3.nbt']
    save(OUT / 'manifest.json', dict(machine='W10', candidate='A3', status='净空修订方块预览与NBT，外观待审',
        actual_size_wdh=[w, d, h], blocks=len(keys),
        files={name: dict(bytes=(OUT / name).stat().st_size, sha256=hashlib.sha256((OUT / name).read_bytes()).hexdigest()) for name in files}))
    print(json.dumps(dict(blocks=len(keys), quads=quads, intersections=intersections, cage_connections=cage_connections), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
