import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from w12_common_20261116 import CENTER
from w12_core_20261116 import chain, chain_ring_samples


ROOT = Path(__file__).resolve().parents[2]
A1 = ROOT / 'deliveries/0005_W12_作者蓝图原案_A1_20261116'
CAVITY_RADIUS = 53.4


def cube_radii(points):
    q = points - CENTER
    return np.linalg.norm(np.maximum(np.maximum(q, -q - 1), 0), axis=1)


def load_part(name, archive, components):
    info = components[name]
    return SimpleNamespace(name=name, label=info['label'], p=archive[name + '_xyz'],
                           states=archive[name + '_materials'], metadata=info['metadata'].copy())


def terminal(start, old_end):
    delta = old_end - CENTER
    side = np.sign(start - CENTER)
    if delta[2]:
        return CENTER + [0, 0, 59 * side[2]]
    if delta[1] and delta[0]:
        return CENTER + [54 * side[0], 54 * side[1], 0]
    return CENTER + [90 * side[0], 0, 0]


def build():
    cavity_radius = CAVITY_RADIUS
    components = json.loads((A1 / 'geometry.json').read_text('utf8'))['components']
    archive = np.load(A1 / '原案构件数据.npz')
    parts = []
    samples = chain_ring_samples()
    for name in components:
        if not name.startswith('binding_chain_'):
            continue
        original = load_part(name, archive, components)
        old_min = float(cube_radii(original.p).min())
        if old_min >= cavity_radius:
            continue
        metadata = original.metadata
        start = np.asarray(metadata['start_blueprint_xyz'], float)
        old_end = np.asarray(metadata['end_blueprint_xyz'], float)
        end = terminal(start, old_end)
        source = {k: metadata[k] for k in ('source', 'anchor_number') if k in metadata}
        part = chain(name, original.label, start, end, samples, **source)
        part.metadata.update(a2_change='终点移到来向同侧的固定十字外臂',
                             a1_end_blueprint_xyz=old_end.astype(int).tolist(),
                             minimum_complete_cube_radius=float(cube_radii(part.p).min()))
        parts.append(part)
        change = dict(name=name, before_blocks=len(original.p), after_blocks=len(part.p),
                      before_minimum_cube_radius=old_min,
                      after_minimum_cube_radius=part.metadata['minimum_complete_cube_radius'],
                      old_end=old_end.astype(int).tolist(), new_end=end.astype(int).tolist(),
                      before_chain_links=metadata['chain_links'],
                      after_chain_links=part.metadata['chain_links'])
        part.metadata['a2_comparison'] = change
    for name in ('energy_wing_west', 'energy_wing_east'):
        part = load_part(name, archive, components)
        keep = cube_radii(part.p) >= cavity_radius
        old_count = len(part.p)
        removed = part.p[~keep]
        part.p, part.states = part.p[keep], part.states[keep]
        part.metadata.update(core_bay_radius=cavity_radius,
                             a2_change='中央球形核心开口，删除与开口相交的完整方块',
                             removed_core_bay_blocks=old_count - len(part.p),
                             minimum_complete_cube_radius=float(cube_radii(part.p).min()))
        parts.append(part)
        change = dict(name=name, before_blocks=old_count, after_blocks=len(part.p),
                      removed_blocks=len(removed),
                      removed_integer_bounds=dict(min=removed.min(0).tolist(), max=removed.max(0).tolist()),
                      after_minimum_cube_radius=part.metadata['minimum_complete_cube_radius'])
        part.metadata['a2_comparison'] = change
    archive.close()
    notes = [
        'A2在双翼长廊靠近核心处开出球形中央机舱，按完整单位立方体到中心的最小距离删除侵入方块；两翼外侧轮廓、地面轨道与137格交汇范围保留。开口半径为' + str(cavity_radius) + '格。',
        '32条实体链全部保留。18条进入中央开口的链重新生成完整链节，并把终点接到来向同侧的固定十字外臂；Z向末端取核心相对Z±59，接入原Z±60臂端内一格，斜臂取相对(±54,±54,0)，主横臂取相对X±90。',
        '此次端点调整保留墙顶与液压桩的原始起点、逐节穿扣形式和黑白金材质。外部链链交叉、链穿长廊、冠环与尖塔的既有冲突继续单列。',
    ]
    return parts, notes
