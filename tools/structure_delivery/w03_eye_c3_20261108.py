# -*- coding: utf-8 -*-
"""W03 C3: complete Möbius geometry and four controlled comparison variants."""
import copy
import json
import math
from pathlib import Path
import numpy as np
import w03_clearance_c2_20261108 as c2
import w03_void_spear_c1_20261108 as c1

ROOT = Path(__file__).resolve().parents[2]
STATES, ROLES = c1.STATES, c1.ROLES
IDS = {s: i + 1 for i, s in enumerate(STATES)}
M = c1.original.M
CENTER = np.array([336., 355., 264.])
VARIANTS = [('3H', 3, False), ('3U', 3, True), ('5H', 5, False), ('5U', 5, True)]


def unique_part(name, points, states):
    # Stable last-write precedence belongs only to one component, never a repair
    # that discards the intersecting half of another component.
    p = np.rint(points).astype(np.int32)
    _, reverse = np.unique(p[::-1], axis=0, return_index=True)
    selected = len(p) - 1 - reverse
    return c2.Part(name, p[selected], np.asarray(states, np.uint8)[selected])


def mobius(radius, tilt):
    angle = math.radians(tilt)
    u, v = np.array([1., 0, 0]), np.array([0, math.cos(angle), math.sin(angle)])
    normal = np.cross(u, v)
    half = 10 if radius == 210 else 6
    theta = np.linspace(0, 2 * math.pi, math.ceil(2 * math.pi * radius * 3) + 1)
    radial = np.cos(theta[:, None]) * u + np.sin(theta[:, None]) * v
    width = np.cos(theta[:, None] / 2) * radial + np.sin(theta[:, None] / 2) * normal
    thick = -np.sin(theta[:, None] / 2) * radial + np.cos(theta[:, None] / 2) * normal
    coords, states = [], []
    for s in np.arange(-half, half + .1, .5):
        for t in (-1., -.5, 0., .5, 1.):
            coords.append(CENTER + radius * radial + s * width + t * thick)
            material = c1.original.WHITE
            if abs(s) >= half - 1: material = M.GOLD
            elif abs(s) <= .5: material = c1.original.MAGENTA
            elif abs(s) == 2 and t < -.5: material = c1.original.COIL
            elif t < -.5: material = M.ATOMIC
            states.append(np.full(len(theta), IDS[material], np.uint8))
    part = unique_part('ring:' + str(radius), np.concatenate(coords), np.concatenate(states))
    assert np.allclose(width[0], -width[-1]) and np.allclose(thick[0], -thick[-1])
    # The two rectangular end sections coincide after reversing both local axes.
    assert np.allclose(CENTER + radius * radial[0] + half * width[0],
                       CENTER + radius * radial[-1] - half * width[-1])
    return part, dict(radius_x=radius, radius_y=radius, center_blueprint=CENTER.tolist(),
        plane_tilt_from_XY_deg=tilt, band_width=2 * half + 1, thickness=3,
        half_twists=1, twist_degrees=180, seam_closed_with_reversed_cross_section=True,
        centerline_is_circle=True, shape='mobius_strip',
        parameterization='C + R*r(theta) + s*(cos(theta/2)*r + sin(theta/2)*n) + t*(-sin(theta/2)*r + cos(theta/2)*n)')


def crystal(index):
    row, col = divmod(index, 8)
    side = [8, 18, 12, 24, 10, 22, 14, 26][(col + row * 3) % 8]
    center = CENTER + [(col - 3.5) * 48, [170, 216, 262][row] - CENTER[1],
                       -152 if (row + col) % 2 == 0 else 152]
    axis = np.arange(side) - (side - 1) / 2
    a, b, d = np.meshgrid(axis, axis, axis, indexing='ij')
    xyz = np.c_[a.ravel(), b.ravel(), d.ravel()]
    boundary = np.abs(xyz) >= (side - 1) / 2 - .1
    shell = boundary.any(1)
    xyz, boundary = xyz[shell], boundary[shell]
    ry, rz = math.radians((index * 37) % 90), math.radians((index * 19) % 45)
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    values = np.where(boundary.sum(1) >= 2, IDS[c1.original.MAGENTA], IDS[c1.original.PURPLE])
    part = unique_part('crystal:' + str(index), center + xyz @ (Ry @ Rz).T, values)
    low, high = part.bounds
    assert low[1] >= 145 and high[1] <= 285, (index, low, high)
    return part, dict(id=index + 1, side_length=side, center=center.tolist(),
        euler_yz_degrees=[math.degrees(ry), math.degrees(rz)],
        meaning='空之律者能力下极度压缩的浓缩崩坏能晶体', lower_third_y_blueprint=[145, 285])


def build(ring_count=3, upward=False):
    with np.load(ROOT / 'logs/w03-clearance-c2-20261108/raw-circle.npz', allow_pickle=False) as f:
        data = json.loads(str(f['metadata']))
        names = json.loads(str(f['names']))
        kept = [n for n in names if n == 'base' or n == 'core' or n.startswith(('anchor:', 'crown:', 'cannon:'))]
        parts = {n: c2.Part(n, f[n + '__p'], f[n + '__s']) for n in kept}
    old = json.loads((ROOT / 'logs/w03-clearance-c2-20261108/component-clearance.json').read_text('utf8'))
    for n, p in parts.items(): p.move(old['part_bounds_blueprint'][n]['translation'])
    ring_settings = [(210, 0), (146, 35), (82, 20)] if ring_count == 3 else [(210, 0), (178, -25), (146, 35), (114, -45), (82, 20)]
    rings = []
    for radius, tilt in ring_settings:
        p, info = mobius(radius, tilt); parts[p.name] = p; rings.append(info)
    crystals = []
    for i in range(24):
        p, info = crystal(i); parts[p.name] = p; crystals.append(info)
    local = np.array(list(c1.LOCAL), float)
    materials = np.array([IDS[s] for s in c1.LOCAL.values()], np.uint8)
    spears = []
    for i in range(6):
        row, side = i // 2, (-1 if i % 2 == 0 else 1)
        v = np.array([side * (.72 if upward else 1), -.69 if upward else 0, 0.])
        v /= np.linalg.norm(v)
        u = np.array([-v[1], v[0], 0.]); w = np.cross(v, u)
        tip = np.array([336 + side * 72, (350 + row * 45) if upward else (318 + row * 44),
                        264 + (-215 if row % 2 == 0 else 215)])
        p = unique_part('spear:' + str(i), tip + local[:, :1] * v + local[:, 1:2] * u + local[:, 2:3] * w, materials)
        parts[p.name] = p
        spears.append(dict(id=i + 1, tip=tip.tolist(), tail_axis=v.tolist(),
            point_direction=(-v).tolist(), length=206, style='upward' if upward else 'horizontal',
            source='C1黑白橙亚空之矛完整局部体素，整柄刚性转向'))
    # Keep every full component. Any required displacement is explicit and rigid.
    settled, shifts = [], {}
    for n in ['base'] + [n for n in parts if n.startswith('anchor:')] + ['core'] + [p for p in parts if p.startswith('ring:')]:
        shifts[n] = c2.place(parts[n], settled)
    for prefix, direction in [('crown:', [0, 1, 0]), ('cannon:', None), ('crystal:', [0, 0, 1]), ('spear:', None)]:
        for n, p in parts.items():
            if not n.startswith(prefix): continue
            move = direction
            if prefix == 'cannon:':
                delta = p.p.mean(0) - CENTER; move = delta / max(1, np.linalg.norm(delta))
            if prefix == 'crystal:': move = [0, 0, -1 if p.p[:, 2].mean() < 264 else 1]
            if prefix == 'spear:': move = [0, 0, -1 if p.p[:, 2].mean() < 264 else 1]
            shifts[n] = c2.place(p, settled, move)
    after = c2.collisions(parts)
    assert not after, after
    for i, info in enumerate(crystals): info['center'] = (np.array(info['center']) + parts['crystal:' + str(i)].translation).tolist()
    for i, info in enumerate(spears): info['tip'] = (np.array(info['tip']) + parts['spear:' + str(i)].translation).tolist()
    lo = np.min([p.bounds[0] for p in settled], axis=0)
    hi = np.max([p.bounds[1] for p in settled], axis=0)
    size = hi - lo + 1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    for p in settled:
        at = p.p - lo; cube[at[:, 1], at[:, 2], at[:, 0]] = p.states
    for item in data['ports']:
        item['pos'] = (np.array(item['pos']) - lo).tolist()
    for item in data['paths']:
        for k in ('min', 'max'): item[k] = (np.array(item[k]) - lo).tolist()
    for item in data['pipe_routes']:
        for k in ('start', 'end', 'path'): item[k] = (np.array(item[k]) - lo).tolist()
    data['controller'] = (np.array(data['controller']) - lo).tolist()
    code = str(ring_count) + ('U' if upward else 'H')
    label = f'{ring_count}环 · ' + ('向上刺矛' if upward else '水平亚空之矛')
    data.update(name='hk3gtl-w03-eye-c3-' + code.lower(), candidate_version='C3-' + code,
        title='空之律者 · 穹界·虚数锚定环 · ' + label, size=size.tolist(),
        nominal_size_xyz=[673, 321, 529], blueprint_bounds_xyz=dict(min=lo.tolist(), max=hi.tolist()),
        blueprint_to_export_offset_xyz=(-lo).tolist(), rings=rings, spears=spears, cubes=crystals,
        ribbons=[], feathers=[], removed_component_types=['ribbon', 'feather'],
        zones=[dict(name='莫比乌斯眼形环系', pos=(CENTER - lo).tolist()),
               dict(name='下方三分之一浓缩崩坏能晶体', pos=(np.array([336, 216, 264]) - lo).tolist()),
               dict(name='八处通用接口与主控', pos=data['controller'])],
        description='移除左右飘带与翼刃；真正半扭转莫比乌斯带环，24颗不同大小的浓缩崩坏能晶体均匀分布在环的下方三分之一。',
        purpose='同镜头比较三环／五环、水平／向上刺矛；四份均为待审外观候选。',
        part_metadata_coordinates='构件为原蓝图坐标；主控、接口、分区、通道、管路为导出坐标',
        clearance=dict(after=after, intersection_pairs_after=0, min_nonconnection_distance=8,
            gap_rule='独立构件体素中心切比雪夫距离至少8；基座与锚桩接合为同一建筑组件。',
            part_count=len(parts), shifts=shifts,
            part_bounds_blueprint={n: dict(min=p.bounds[0].tolist(), max=p.bounds[1].tolist(), translation=p.translation.tolist()) for n, p in parts.items()},
            standard_overworld_build_height_exceeded=bool(size[1] > 384)),
        comparison=dict(code=code, ring_count=ring_count, spear_direction='upward' if upward else 'horizontal',
            ribbons=0, wing_blades=0, crystal_count=24, crystal_band_y_blueprint=[145, 285],
            crystal_distribution='8列×3行等间距，前后纵深交错；大小不单调排列',
            no_nominal_clipping=True, ring_half_twist_verified=True))
    print(json.dumps(dict(variant=code, size_xyz=data['size'], blocks=int(np.count_nonzero(cube)),
        absent_materials=[s for i, s in enumerate(STATES, 1) if not np.any(cube == i)],
        rigid_shifts={n: v for n, v in shifts.items() if any(v)})), flush=True)
    return cube, data


if __name__ == '__main__':
    build(5, True)
