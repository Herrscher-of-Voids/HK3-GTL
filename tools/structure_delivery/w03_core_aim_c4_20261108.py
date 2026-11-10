# -*- coding: utf-8 -*-
"""C4: six real voxel axes converge on the core; crystals occupy a volume."""
import json
import math
from pathlib import Path
import numpy as np
import w03_eye_c3_20261108 as c3

ROOT, STATES, ROLES, IDS = c3.ROOT, c3.STATES, c3.ROLES, c3.IDS
CORE = np.array([336, 366, 264])
# Length 41 divides the 205-block spear axis: both voxel endpoints and the
# target can be exactly collinear, without relying on a front-view projection.
AXES = [(32, -24, 9), (9, -24, 32), (-23, -24, 24),
        (-32, -24, -9), (-9, -24, -32), (23, -24, -24)]


def failures(part, settled):
    return [dict(other=p.name, distance=distance) for p in settled
            if c3.c2.connections(part.name) != c3.c2.connections(p.name)
            for distance, _ in [part.nearest(p, 8)] if distance < 8]


def build():
    with np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False) as f:
        data = json.loads(str(f['metadata']))
        names = json.loads(str(f['names']))
        kept = [n for n in names if n in ('base', 'core') or n.startswith(('anchor:', 'crown:', 'cannon:'))]
        parts = {n: c3.c2.Part(n, f[n + '__p'], f[n + '__s']) for n in kept}
    history = json.loads((ROOT / 'logs/w03-clearance-c2-20261108/component-clearance.json').read_text('utf8'))
    for n, p in parts.items(): p.move(history['part_bounds_blueprint'][n]['translation'])
    rings = []
    for radius, tilt in [(210, 0), (178, -25), (146, 35), (114, -45), (82, 20)]:
        p, info = c3.mobius(radius, tilt); parts[p.name] = p; rings.append(info)
    settled = []
    for p in parts.values(): c3.c2.place(p, settled)
    local = np.array(list(c3.c1.LOCAL), float)
    materials = np.array([IDS[s] for s in c3.c1.LOCAL.values()], np.uint8)
    spears = []
    for i, integer_axis in enumerate(AXES):
        a = np.array(integer_axis); assert a @ a == 41 ** 2
        v = a / 41
        u = np.cross(v, [0., 1, 0]); u /= np.linalg.norm(u)
        w = np.cross(v, u)
        for multiplier in range(3, 9):
            tip, tail = CORE + multiplier * a, CORE + (multiplier + 5) * a
            p = c3.unique_part('spear:' + str(i), tip + local[:, :1] * v + local[:, 1:2] * u + local[:, 2:3] * w, materials)
            if not failures(p, settled): break
        else: raise AssertionError(('No complete convergent spear clearance', i))
        assert tuple(tip) in set(map(tuple, p.p)) and tuple(tail) in set(map(tuple, p.p))
        assert np.array_equal(np.cross(CORE - tip, tip - tail), np.zeros(3))
        parts[p.name] = p; settled.append(p)
        spears.append(dict(id=i + 1, tip=tip.tolist(), tail=tail.tolist(),
            target_core=CORE.tolist(), tail_axis=v.tolist(), point_direction=(-v).tolist(),
            length=206, local_axis_length=205, source='C1完整黑白橙亚空之矛，仅刚性旋转及沿自身轴线定位',
            tip_distance_to_core=float(np.linalg.norm(CORE - tip)),
            voxel_axis_miss_distance_to_core=0, core_in_forward_direction=True,
            upward=True, axis_position_multiplier=multiplier))
    crystals = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(24):
        p, info = c3.crystal(i)
        original_center = np.array(info['center'])
        low = i < 10
        y = (32 + i * 12) if low else (148 + (i - 10) * 8)
        radius = (34 + (i * 29) % 65) if low else (55 + (i * 37) % 126)
        for trial in range(48):
            angle = i * golden + trial * .29
            center = np.rint([336 + radius * math.cos(angle), y + trial % 3 * 3,
                              264 + radius * math.sin(angle)]).astype(int)
            delta = center - original_center
            candidate = c3.c2.Part('crystal:' + str(i), p.p + np.rint(delta).astype(int), p.states)
            if not failures(candidate, settled): break
        else: raise AssertionError(('No complete crystal clearance', i))
        parts[candidate.name] = candidate; settled.append(candidate)
        info.update(center=center.tolist(), meaning='空之律者能力下极度压缩的浓缩崩坏能晶体',
            distribution_region='基座中央坑内与上空' if low else '环下方立体空间',
            placement_attempt=trial, radial_distance_xz=float(np.linalg.norm(center[[0, 2]] - CORE[[0, 2]])))
        info.pop('lower_third_y_blueprint', None)
        crystals.append(info)
    after = c3.c2.collisions(parts); assert not after, after
    centers = np.array([c['center'] for c in crystals])
    central_lower = [c for c in crystals if c['center'][1] < 150 and c['radial_distance_xz'] < 115]
    assert len(central_lower) >= 8 and len(np.unique(centers[:, 2])) >= 20
    assert np.linalg.matrix_rank(centers - centers.mean(0)) == 3
    eigenvalues = np.linalg.eigvalsh(np.cov(centers.T))
    assert eigenvalues[0] / eigenvalues[-1] > .15, eigenvalues
    lo = np.min([p.bounds[0] for p in settled], axis=0)
    hi = np.max([p.bounds[1] for p in settled], axis=0)
    size = hi - lo + 1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    for p in settled:
        at = p.p - lo; cube[at[:, 1], at[:, 2], at[:, 0]] = p.states
    for item in data['ports']: item['pos'] = (np.array(item['pos']) - lo).tolist()
    for item in data['paths']:
        for k in ('min', 'max'): item[k] = (np.array(item[k]) - lo).tolist()
    for item in data['pipe_routes']:
        for k in ('start', 'end', 'path'): item[k] = (np.array(item[k]) - lo).tolist()
    data['controller'] = (np.array(data['controller']) - lo).tolist()
    data.update(name='hk3gtl-w03-core-aim-c4', candidate_version='C4-五环向上锁芯',
        title='空之律者 · 穹界·虚数锚定环 · C4五环锁芯与立体晶云',
        size=size.tolist(), nominal_size_xyz=[673, 321, 529],
        blueprint_bounds_xyz=dict(min=lo.tolist(), max=hi.tolist()), blueprint_to_export_offset_xyz=(-lo).tolist(),
        rings=rings, spears=spears, cubes=crystals, ribbons=[], feathers=[],
        core_center_blueprint=CORE.tolist(),
        zones=[dict(name='五环莫比乌斯眼形', pos=(c3.CENTER - lo).tolist()),
               dict(name='六柄亚空之矛共同指向核心', pos=(CORE - lo).tolist()),
               dict(name='中央反应池与立体晶云', pos=(np.array([336, 120, 264]) - lo).tolist())],
        description='五环向上方案续修：六柄矛的真实尖端—尾端轴线精确指向同一核心；24颗紫晶散入基座中央坑上空与环下方的三维体积。',
        purpose='按负责人侧面截图纠正三维矛向与晶体成墙问题；新的待审外观候选。',
        part_metadata_coordinates='核心、矛尖、矛尾、晶体和构件边界为原蓝图坐标；主控、接口、分区、通道、管路为导出坐标',
        clearance=dict(after=after, intersection_pairs_after=0, min_nonconnection_distance=8,
            gap_rule='独立体素构件中心切比雪夫距离至少8；基座与锚桩接合为同一建筑组件。',
            part_count=len(parts), part_bounds_blueprint={n: dict(min=p.bounds[0].tolist(), max=p.bounds[1].tolist()) for n, p in parts.items()},
            standard_overworld_build_height_exceeded=bool(size[1] > 384)),
        aiming=dict(target_core_blueprint=CORE.tolist(), actual_voxel_tip_and_tail_verified=True,
            all_six_axes_exactly_collinear_with_core=True, maximum_miss_distance=0,
            all_six_upward=True, radial_azimuths_degrees=[math.degrees(math.atan2(a[2], a[0])) for a in AXES]),
        crystal_cloud=dict(count=24, size_variants=8, lower_central_count=len(central_lower),
            center_bounds_blueprint=dict(min=centers.min(0).tolist(), max=centers.max(0).tolist()),
            unique_z_coordinates=int(len(np.unique(centers[:, 2]))), spatial_rank=3,
            covariance_eigenvalues=eigenvalues.tolist(), smallest_to_largest_eigenvalue_ratio=float(eigenvalues[0] / eigenvalues[-1]),
            arrangement='分散于三维体积；10颗优先占据基座中央坑及上空，14颗散入环下方，避免两层平面与等高行列'),
        comparison=dict(code='C4', ring_count=5, spear_direction='upward_toward_core',
            ribbons=0, wing_blades=0, crystal_count=24, no_nominal_clipping=True,
            ring_half_twist_verified=True, selected_base='C3-5U；仅选定修订方向，不代表批准部署'))
    print(json.dumps(dict(size_xyz=data['size'], spears=spears, cloud=data['crystal_cloud']), ensure_ascii=False), flush=True)
    return cube, data


if __name__ == '__main__': build()
