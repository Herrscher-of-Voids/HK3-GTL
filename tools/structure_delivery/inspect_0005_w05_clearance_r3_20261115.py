import json
from datetime import datetime
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_七处穿模修订_R3_20261115'
BASELINE = ROOT / 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
LOG = ROOT / 'logs/0005-w05-clearance-r3-20261115'
LOG.mkdir(exist_ok=True)
manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
base_manifest = json.loads((BASELINE / 'manifest.json').read_text('utf8'))
parts = manifest['components']
archive = np.load(SOURCE / '原始构件数据.npz')
baseline = np.load(BASELINE / '原始构件数据.npz')
xyz = {p['id']: archive[p['id'] + '_xyz'] for p in parts}
states = {p['id']: archive[p['id'] + '_materials'] for p in parts}
meta = {p['id']: p['metadata'] for p in parts}
ids = list(xyz)


def save(name, value):
    (LOG / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def key(q):
    return ((q[:, 0].astype(np.int64) + 512) * 1024 + q[:, 1] + 512) * 1024 + q[:, 2] + 512


bounds = {name: (q.min(0), q.max(0)) for name, q in xyz.items()}
static_pairs = []
for index, a in enumerate(ids):
    for b in ids[index + 1:]:
        if np.any(np.maximum(bounds[a][0], bounds[b][0]) > np.minimum(bounds[a][1], bounds[b][1])):
            continue
        common = np.intersect1d(key(xyz[a]), key(xyz[b]), assume_unique=True)
        if len(common):
            q = np.c_[common // 1048576 - 512, (common // 1024) % 1024 - 512, common % 1024 - 512]
            static_pairs.append(dict(a=a, b=b, count=len(common), min=q.min(0).tolist(), max=q.max(0).tolist(),
                upper_count=int((q[:, 1] >= 80).sum())))
save('static-exact-pairs.json', dict(method='73构件整数格完整成对求交，正常接口单独解释。', pair_count=len(static_pairs),
    pair_memberships=sum(r['count'] for r in static_pairs), pairs=static_pairs))

changed = set(manifest['revision']['modified_components'])
preservation = []
mirrors = []
for name in ids:
    same = np.array_equal(xyz[name], baseline[name + '_xyz']) and np.array_equal(states[name], baseline[name + '_materials'])
    preservation.append(dict(id=name, declared_changed=name in changed, arrays_identical_to_r2=bool(same)))
    if name.startswith('wing_left_'):
        right = name.replace('wing_left_', 'wing_right_', 1)
        q = xyz[name].copy()
        q[:, 0] *= -1
        left_order, right_order = np.argsort(key(q)), np.argsort(key(xyz[right]))
        left_motion, right_motion = meta[name].get('motion'), meta[right].get('motion')
        motion_mirrored = True
        if left_motion:
            lp, rp = np.array(left_motion['pivot']), np.array(right_motion['pivot'])
            expected_axis = np.array(left_motion['axis']).copy()
            expected_axis[0] *= -1
            expected_sign = -left_motion.get('sign', 1) if abs(left_motion['axis'][1]) > .99 else left_motion.get('sign', 1)
            motion_mirrored = bool(np.allclose(lp * [-1, 1, 1], rp) and
                np.allclose(expected_axis, right_motion['axis']) and expected_sign == right_motion.get('sign', 1))
        mirrors.append(dict(left=name, right=right,
            xyz_mirrored=bool(np.array_equal(q[left_order], xyz[right][right_order])),
            materials_mirrored=bool(np.array_equal(states[name][left_order], states[right][right_order])),
            motion_mirrored=motion_mirrored))
save('geometry-preservation.json', dict(components=preservation, mirrors=mirrors,
    palette_identical=manifest['native_materials'] == base_manifest['native_materials']))


def radial_rows(name, axis_pivot):
    q = xyz[name].astype(float)
    pivot = np.array(axis_pivot, dtype=float)
    d = np.abs(q[:, [0, 2]] - pivot[[0, 2]])
    rmin = np.linalg.norm(np.maximum(d - .5, 0), axis=1)
    rmax = np.linalg.norm(d + .5, axis=1)
    rows = {}
    for y in np.unique(q[:, 1].astype(int)):
        mask = q[:, 1] == y
        rows[int(y)] = [float(rmin[mask].min()), float(rmax[mask].max())]
    return rows


def gap_between(a, b):
    pivot = meta[a]['motion']['pivot']
    rows_a, rows_b = radial_rows(a, pivot), radial_rows(b, pivot)
    best, witness = float('inf'), None
    for ya, (alo, ahi) in rows_a.items():
        for yb, (blo, bhi) in rows_b.items():
            dy = max(abs(ya - yb) - 1, 0)
            dr = max(blo - ahi, alo - bhi, 0)
            gap = float(np.hypot(dy, dr))
            if gap < best:
                best, witness = gap, dict(source_y=ya, source_r=[alo, ahi], target_y=yb, target_r=[blo, bhi])
    return best, witness


moving = [name for name in ids if name in changed and meta[name].get('motion')]
fixed = [name for name in ids if not meta[name].get('motion')]
continuous = []
for source in moving:
    pivot = np.array(meta[source]['motion']['pivot'], dtype=float)
    rows = radial_rows(source, pivot)
    outer = max(r[1] for r in rows.values())
    sweep_low = pivot + [-outer, min(rows) - .5 - pivot[1], -outer]
    sweep_high = pivot + [outer, max(rows) + .5 - pivot[1], outer]
    for target in fixed:
        if np.any(sweep_high <= bounds[target][0] - .5) or np.any(sweep_low >= bounds[target][1] + .5):
            continue
        gap, witness = gap_between(source, target)
        continuous.append(dict(source=source, target=target, gap_lower_bound=gap,
            continuously_disjoint=gap > 1e-8, witness=witness))
for side in ('left', 'right'):
    for index in range(1, 4):
        source, target = f'wing_{side}_lift_rotor_{index}', f'wing_{side}_vortex_column_{index}'
        gap, witness = gap_between(source, target)
        continuous.append(dict(source=source, target=target, gap_lower_bound=gap,
            continuously_disjoint=gap > 1e-8, witness=witness))
save('continuous-envelope-clearance.json', dict(
    method='垂直轴旋转的单位方块水平正方形全周扫掠为径向区间，按整数Y层聚合；目标也按同轴半径区间聚合。所有旋转角度均被包含，不依赖离散时间采样。',
    proof_scope='R3改动清单内的垂直旋转部件对所有固定构件；另含同塔叶轮/实体风柱独立旋转组合。',
    interpretation='正净空下界证明该对连续分离。零下界只表示保守区间包络可能相交；本方法聚合整层最小/最大半径，会填补同层径向空隙，故保守且可能假阳性。',
    unit_cube_horizontal_half_diagonal=float(np.sqrt(.5)), records=continuous))
summary = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'), candidate='R3',
    component_count=len(parts), changed_component_count=len(changed), exact_static_pair_count=len(static_pairs),
    exact_static_pair_memberships=sum(r['count'] for r in static_pairs),
    preservation_failures=[r for r in preservation if (r['declared_changed'] and r['arrays_identical_to_r2']) or
        (not r['declared_changed'] and not r['arrays_identical_to_r2'])],
    mirror_differences=[r for r in mirrors if not r['xyz_mirrored'] or not r['materials_mirrored'] or not r['motion_mirrored']],
    nonpositive_continuous_clearance=[r for r in continuous if not r['continuously_disjoint']],
    static_pairs='static-exact-pairs.json', preservation='geometry-preservation.json',
    continuous_clearance='continuous-envelope-clearance.json', geometry_modified=False,
    desktop_used=False, game_started=False)
save('independent-review.json', summary)


def minimum_gap(source_kind, target_kind, index=None):
    return min(r['gap_lower_bound'] for r in continuous if source_kind in r['source'] and
        target_kind in r['target'] and (index is None or r['source'].endswith('_' + str(index))))


readable = dict(created_at=summary['created_at'], candidate='R3', source_delivery=str(SOURCE.relative_to(ROOT)),
    conclusion='七项指定穿模修订的静态交集和连续包络检查完成；22构件按清单修改，其余51构件逐值保持。结果仅针对仓库/网页几何，不是游戏成型、运行或性能验收。',
    seven_items=[
        dict(id='upper-rim', title='后副塔上口 × 青绿管网', static_cooccupied_cells=0),
        dict(id='front-frame', title='前副塔侧框 × 青绿管网', static_cooccupied_cells=0),
        dict(id='vanes', title='导流百叶 × 六座副塔上部', static_upper_cooccupied_cells=0,
            preserved_mount_cells_per_tower=68, preserved_mount_y=[58, 70]),
        dict(id='rotor-network', title='前副塔叶轮 × 青绿管网', continuous_gap_lower_bound=minimum_gap('lift_rotor', 'mobius_network', 1)),
        dict(id='rotor-brace', title='六副塔叶轮 × 塔体/斜撑', continuous_gap_lower_bound=minimum_gap('lift_rotor', 'vortex_tower')),
        dict(id='helix-rotor', title='实体双螺旋风柱 × 叶轮', continuous_gap_lower_bound=minimum_gap('lift_rotor', 'vortex_column')),
        dict(id='helix-network', title='后副塔实体风柱 × 青绿管网', continuous_gap_lower_bound=minimum_gap('vortex_column', 'mobius_network', 3)),
    ], continuous_proof=dict(pair_count=len(continuous), nonpositive_count=len(summary['nonpositive_continuous_clearance']),
        method='按单位方块在垂直轴全周旋转的径向区间及Y层轴向范围求保守净空下界；覆盖全部转角，不依赖离散时间采样。静态目标径向包络同样只扩大，不缩小。',
        distance_units='格；所列为表面间净空保守下界，不是仅中心距离或格数差。',
        other_bound='12个改动运动构件对全部固定构件的候选，以及同塔叶轮/风柱的任意独立旋转；42对下界全部为正。',
        limitation='整层径向区间会填补同层空洞，因此可能假阳性；本轮正下界足以证明这些对分离。不把结论扩展为整机所有特效/运动组合已验证。'),
    new_mount_review=dict(
        wing_network_vane_mount_cells_per_side=6016,
        mount_interpretation='百叶本体及短根支座接入同翼管网，是本次明确设计的安装接口；如实保留共占格，不称为零共占。',
        guide_tower_lower_mount_cells_per_tower=68, base_guide_mount_cells_per_side=153,
        upper_guide_tower_cells=0,
        changed_network_and_vanes_vs_tip_blades_cells=0,
        new_fixed_component_pair_intersections_outside_mounts=[],
        note='完整73构件成对交集除既有底座/接口/轴承/前后端过渡连接及管网安装接口外，未见改动管网或百叶与其他固定构件的新交集。'),
    preservation=dict(palette_identical=True, declared_changed=22, unchanged_array_count=51,
        unexpected_changes=summary['preservation_failures'],
        network_and_vanes_x_mirror=True,
        mirror_scope='新管网与百叶坐标/材料严格X镜像；翼尖弧刃也镜像。塔撑、实体螺旋与叶轮沿用原模板手性，并非全部逐格镜像，运动轴心镜像且方向相反，不将此冒称整机全时严格镜像。'),
    evidence=dict(full_static_pairs=str((LOG / 'static-exact-pairs.json').relative_to(ROOT)),
        continuous_envelopes=str((LOG / 'continuous-envelope-clearance.json').relative_to(ROOT)),
        preservation=str((LOG / 'geometry-preservation.json').relative_to(ROOT)),
        independent_summary=str((LOG / 'independent-review.json').relative_to(ROOT)),
        inspection_script=str(Path(__file__).relative_to(ROOT))),
    geometry_modified_by_review=False, desktop_used=False, game_started=False, acceptance_score_changed=False)
save('clearance-readable-summary.json', readable)
(SOURCE / '净空检查.json').write_text(json.dumps(readable, ensure_ascii=False, indent=2) + '\n', 'utf8')
print(json.dumps(dict(static_pairs=len(static_pairs), memberships=summary['exact_static_pair_memberships'],
    preservation_failures=summary['preservation_failures'], mirror_difference_count=len(summary['mirror_differences']),
    continuous_pairs=len(continuous), unresolved=[r for r in continuous if not r['continuously_disjoint']]), ensure_ascii=False), flush=True)
