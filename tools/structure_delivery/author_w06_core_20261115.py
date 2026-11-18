import math

import numpy as np

from author_w05_shapes_20261115 import Part, trace


ARMOR, DARK, ICE, GOLD, COIL, CORE, GRATE, ZERO = range(1, 9)
CX, CZ = 401, 361


def _tapered_cylinder(part, start, end, radius_start, radius_end, state):
    a, b = np.asarray(start, float), np.asarray(end, float)
    axis = b - a
    length = np.linalg.norm(axis)
    axis /= length
    u = np.cross(axis, [0, 1, 0])
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(axis, [1, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    radius = max(radius_start, radius_end)
    q = np.arange(-math.ceil(radius), math.ceil(radius) + 1)
    uu, vv = np.meshgrid(q, q, indexing='ij')
    disk = uu * uu + vv * vv
    points = []
    for distance in np.arange(0, length + 0.5, 0.5):
        t = min(distance / length, 1)
        r = radius_start + (radius_end - radius_start) * t
        mask = disk <= r * r
        center = a + axis * distance
        xyz = center + uu[mask, None] * u + vv[mask, None] * v
        points.append(np.rint(xyz).astype(np.int32))
    part.points(np.concatenate(points), state)


def _oriented_ring(part, center, normal, radius, thickness, depth, state):
    c, n = np.asarray(center, float), np.asarray(normal, float)
    n /= np.linalg.norm(n)
    u = np.cross(n, [0, 1, 0])
    if np.linalg.norm(u) < 1e-6:
        u = np.cross(n, [1, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    extent = math.ceil(radius)
    grid = np.arange(-extent, extent + 1)
    uu, vv = np.meshgrid(grid, grid, indexing='ij')
    r = np.sqrt(uu * uu + vv * vv)
    mask = (r <= radius) & (r >= radius - thickness)
    points = []
    for axial in np.arange(-depth / 2, depth / 2 + 0.5, 1):
        xyz = c + uu[mask, None] * u + vv[mask, None] * v + axial * n
        points.append(np.rint(xyz).astype(np.int32))
    part.points(np.concatenate(points), state)


def _oriented_panel(part, angle, r0, r1, w0, w1, y0, y1, state):
    radii = np.arange(r0, r1 + 1)
    widths = np.arange(w0, w1 + 1)
    rr, ww = np.meshgrid(radii, widths, indexing='ij')
    x = CX + rr * math.cos(angle) - ww * math.sin(angle)
    z = CZ + rr * math.sin(angle) + ww * math.cos(angle)
    yy = np.arange(y0, y1 + 1)
    xf, zf = x.ravel(), z.ravel()
    xx = np.broadcast_to(xf[:, None], (len(xf), len(yy)))
    zz = np.broadcast_to(zf[:, None], (len(zf), len(yy)))
    yyy = np.broadcast_to(yy[None, :], xx.shape)
    part.points(np.c_[xx.ravel(), yyy.ravel(), zz.ravel()], state)


def _petal(index):
    layer = '内层' if index < 6 else '外层'
    petal_index = index % 6
    angle = math.radians(petal_index * 60 + (30 if index >= 6 else 0))
    radial_start = 0 if index < 6 else 25
    layer_offset = 0 if index < 6 else 15
    part = Part(
        f'anna_mechanical_ice_lotus_petal_{index + 1:02d}',
        f'安娜之冕·{layer}机械冰莲花瓣 {petal_index + 1:02d}',
        source='二·2·十二瓣巨型机械冰莲',
        sampling=f'{layer}各6瓣，每瓣间隔60°，与另一层错开30°；每瓣长200、宽80、厚15。内层从半径0起、Y61开始，外层从半径25起、Y76开始；两层各上升165格，整数格厚度使顶层落在Y240..255。',
        layer=layer, nominal_length=200, nominal_width=80, thickness=15,
        radius=[radial_start, radial_start + 200],
    )
    radii = np.arange(radial_start, radial_start + 201)
    widths = np.arange(-40, 41)
    rr, ww = np.meshgrid(radii, widths, indexing='ij')
    distance = rr - radial_start
    base_y = np.rint(61 + layer_offset + 165 * (distance / 200) ** 2).astype(np.int32)
    x = np.rint(CX + rr * math.cos(angle) - ww * math.sin(angle)).astype(np.int32)
    z = np.rint(CZ + rr * math.sin(angle) + ww * math.cos(angle)).astype(np.int32)
    thickness = np.arange(15, dtype=np.int32)
    xx = np.broadcast_to(x[:, :, None], (201, 81, 15))
    zz = np.broadcast_to(z[:, :, None], (201, 81, 15))
    yy = base_y[:, :, None] + thickness
    part.points(np.c_[xx.ravel(), yy.ravel(), zz.ravel()], ARMOR)

    top = base_y + 14
    part.points(np.c_[x.ravel(), top.ravel(), z.ravel()], ICE)
    groove = (distance % 24 == 0) | (np.abs(ww) >= 38)
    part.points(np.c_[x[groove], base_y[groove], z[groove]], DARK)

    for lateral in (-22, 0, 22):
        path = []
        for r in np.linspace(radial_start + 3, radial_start + 197, 80):
            w = lateral
            y = 61 + layer_offset + 165 * ((r - radial_start) / 200) ** 2 + 16
            path.append([CX + r * math.cos(angle) - w * math.sin(angle), y,
                         CZ + r * math.sin(angle) + w * math.cos(angle)])
        trace(part, path, 1.25, ICE)
    return part.finish()


def _octahedron():
    part = Part(
        'anna_silent_herald_octahedral_prism', '静谧之赫·修长八面体棱镜',
        source='二·2·中央“静谧之赫”八面体棱镜',
        sampling='中心(401,170,361)，顶底Y=100/240、水平半径60；整数端点造成121×121×141占格边界，对应原文120×120×140的连续尺寸。透明壳取加权八面体外沿约3格。',
        nominal_size=[120, 120, 140], shell_thickness=3,
    )
    xs = np.arange(CX - 60, CX + 61)
    zs = np.arange(CZ - 60, CZ + 61)
    xx, zz = np.meshgrid(xs, zs, indexing='ij')
    for y in range(100, 241):
        q = abs(xx - CX) / 60 + abs(zz - CZ) / 60 + abs(y - 170) / 70
        shell = (q <= 1.00001) & (q >= 0.94)
        part.points(np.c_[xx[shell], np.full(shell.sum(), y), zz[shell]], ICE)

    ys = np.arange(105, 236)
    for index in range(4):
        angle = np.linspace(index * math.pi / 2, index * math.pi / 2 + math.pi * 2.5, len(ys))
        envelope = 60 * (1 - np.abs(ys - 170) / 70)
        r = 0.48 * envelope / (np.abs(np.cos(angle)) + np.abs(np.sin(angle)))
        route = np.c_[CX + r * np.cos(angle), ys, CZ + r * np.sin(angle)]
        trace(part, route, 1.5, ARMOR)

    core = Part('anna_black_gold_law_core', '律者核心·黑金球体', source='二·2·最内核',
                sampling='球心(401,170,361)，半径20；金色经纬线为未指定纹样的离散转译。', diameter=40)
    core.sphere([CX, 170, CZ], 20, CORE)
    for latitude in (-0.65, -0.3, 0.3, 0.65):
        y = 170 + latitude * 20
        radius = 20 * math.sqrt(1 - latitude * latitude)
        _oriented_ring(core, [CX, y, CZ], [0, 1, 0], radius, 1.5, 1, GOLD)
    for longitude in range(4):
        theta = longitude * math.pi / 4
        points = [[CX + 20 * math.cos(t) * math.cos(theta), 170 + 20 * math.sin(t),
                   CZ + 20 * math.cos(t) * math.sin(theta)] for t in np.linspace(-math.pi / 2, math.pi / 2, 70)]
        trace(core, points, 1, GOLD)

    vertices = [
        [CX - 60, 170, CZ], [CX + 60, 170, CZ], [CX, 100, CZ],
        [CX, 240, CZ], [CX, 170, CZ - 60], [CX, 170, CZ + 60],
    ]
    starts = [[CX - 20, 170, CZ], [CX + 20, 170, CZ], [CX, 150, CZ],
              [CX, 190, CZ], [CX, 170, CZ - 20], [CX, 170, CZ + 20]]
    for start, end in zip(starts, vertices):
        _tapered_cylinder(part, start, end, 2.5, 0.75, ZERO)
    return [part.finish(), core.finish()]


def _golden_halo():
    part = Part(
        'anna_rotating_golden_halo_180', '律者权能·背置旋转金环（180格）',
        source='三·2·中央八面体核心背后的金色律者光环',
        sampling='原文只给直径180并称“核心背后”，未给距离/平面；取中心(401,170,451)、法线+Z（南向背侧），与八面体后表面留约30格。',
        diameter=180, motion={'axis': [0, 0, 1], 'pivot': [CX, 170, 451]},
    )
    _oriented_ring(part, [CX, 170, 451], [0, 0, 1], 90, 5, 4, GOLD)
    for i in range(12):
        angle = i * math.tau / 12
        p = [CX + 90 * math.cos(angle), 170 + 90 * math.sin(angle), 451]
        _tapered_cylinder(part, p, [CX + 83 * math.cos(angle), 170 + 83 * math.sin(angle), 451], 2.5, 0.5, ZERO)
    return part.finish()


def _crown():
    part = Part(
        'anna_inverted_gothic_ice_crown', '倒置哥特式冰晶王冠',
        source='二·4·悬浮王冠',
        sampling='原文给Y=280..340、直径300；取中心轴(401,361)、支撑环Y=338、外半径150，16根朝下尖晶由Y=338落至Y=280。',
        y=[280, 340], diameter=300,
    )
    _oriented_ring(part, [CX, 338, CZ], [0, 1, 0], 150, 6, 4, GOLD)
    _oriented_ring(part, [CX, 334, CZ], [0, 1, 0], 137, 3, 3, COIL)
    for index in range(16):
        angle = index * math.tau / 16
        radius = 72 if index % 2 == 0 else 133
        x, z = CX + radius * math.cos(angle), CZ + radius * math.sin(angle)
        length = 58 if index % 2 == 0 else 42
        _tapered_cylinder(part, [x, 338, z], [x, 338 - length, z], 8 if index % 2 == 0 else 5, 0.5, ICE)
        if index % 2 == 0:
            _tapered_cylinder(part, [x, 336, z], [x, 326, z], 3, 2, ZERO)
    return part.finish()


def _laser_and_wings():
    part = Part(
        'anna_superconducting_laser_altar', '绝对零度圣枪阵列·聚焦天柱与金色十字翼',
        source='二·4·主激光聚焦天柱',
        sampling='主轴(401,361)，圆柱直径30；主柱Y=240..382。四翼按正交方位各一片，径向位置26..48，切向宽5格，十字横臂Y=300..306。',
        diameter=30, y=[240, 382], cross_wings=4,
    )
    _tapered_cylinder(part, [CX, 240, CZ], [CX, 382, CZ], 15, 15, COIL)
    _tapered_cylinder(part, [CX, 170, CZ], [CX, 382, CZ], 3, 3, ZERO)
    for y in range(246, 383, 20):
        _oriented_ring(part, [CX, y, CZ], [0, 1, 0], 15, 2, 3, GOLD)
    for index in range(4):
        angle = index * math.pi / 2
        _oriented_panel(part, angle, 31, 37, -3, 3, 242, 382, GOLD)
        _oriented_panel(part, angle, 25, 45, -18, 18, 300, 306, GOLD)
        _oriented_panel(part, angle, 25, 43, -13, 13, 257, 261, GOLD)
        _oriented_panel(part, angle, 25, 43, -13, 13, 350, 354, GOLD)
    return part.finish()


def _spears():
    parts = []
    for index in range(12):
        angle = index * math.tau / 12
        radial = np.array([math.cos(angle), 0, math.sin(angle)])
        center = np.array([CX, 315, CZ], float) + radial * 250
        start = center + radial * (55 * math.sqrt(2) / 2) + np.array([0, 55 * math.sqrt(2) / 2, 0])
        end = center - radial * (55 * math.sqrt(2) / 2) - np.array([0, 55 * math.sqrt(2) / 2, 0])
        part = Part(
            f'anna_orbital_ice_spear_{index + 1:02d}', f'环绕冰枪 {index + 1:02d}',
            source='二·4·十二座环绕冰枪',
            sampling='每30°一枪，轴线中心落在半径250圆周、Y=315；110格长轴与水平成45°向内下指，最大半径12。枪体外侧缠绕4圈收尖超导螺旋肋，尾部推进器在外端；原文未给起始角，首枪沿+X。',
            length=110, diameter=24, inclination_degrees=45, orbit_diameter=500,
        )
        _tapered_cylinder(part, start, end, 12, 0.5, ICE)
        axis = end - start
        axis /= np.linalg.norm(axis)
        basis_u = np.cross(axis, [0, 1, 0])
        if np.linalg.norm(basis_u) < 1e-6:
            basis_u = np.cross(axis, [1, 0, 0])
        basis_u /= np.linalg.norm(basis_u)
        basis_v = np.cross(axis, basis_u)
        helix = []
        for t in np.linspace(0, 1, 440):
            radius = 12 * (1 - t) + 0.5 * t + 0.8
            angle = t * math.tau * 4
            helix.append(start + (end - start) * t + radius * (math.cos(angle) * basis_u + math.sin(angle) * basis_v))
        trace(part, helix, 1.25, COIL)
        for t in (0.08, 0.14, 0.2):
            centerline = start + (end - start) * t
            _oriented_ring(part, centerline, axis, 12 * (1 - t) + 0.5 * t, 1.5, 2, COIL)
        tail_end = start + (end - start) * 0.2
        _tapered_cylinder(part, start, tail_end, 12, 9, ARMOR)
        light_start = start + (end - start) * 0.24
        _tapered_cylinder(part, light_start, end, 2.25, 0.5, ZERO)
        parts.append(part.finish())
    return parts


def build():
    parts = [_petal(index) for index in range(12)]
    parts.extend(_octahedron())
    parts.extend([_golden_halo(), _crown(), _laser_and_wings()])
    parts.extend(_spears())
    interpretations = [
        {'source': '整体布局·坐标轴锚定', 'detail': '采用原文中心(401,Y,361)。与801×721偶数范围的几何中心(400,360)有1格偏差，按原文中心保留；任何越界由总装实测包围盒记录，不裁切。'},
        {'source': '二·2·十二瓣巨型机械冰莲', 'detail': '按内外两层各6瓣、层间错开30°离散；每瓣长200、宽80、厚15。内层半径0..200、Y61..240；外层半径25..225、Y76..255。两层起始半径与高度为实现“内外两层”所需取样。'},
        {'source': '二·2·中央八面体棱镜', 'detail': '以(401,170,361)构造120×120×140连续尺寸的八面体；整数占格边界会比偶数连续尺寸多一个端点，记录实际包围盒而不缩小。透明壳约3格，内置4条螺旋合金肋、直径40黑金球及六向光束。'},
        {'source': '二·3·三道暴风雪星环', 'detail': '星环由总装几何模块实现；直径710的外环相对721格深度仅留约5格名义余量，按中心(401,361)会落在Z=6..716，不裁切。'},
        {'source': '二·4·悬浮王冠', 'detail': '直径300转为半径150，Y=280..340；原文未定尖晶数量，取16根交替长短的向下冰晶。'},
        {'source': '二·4·主激光聚焦天柱', 'detail': '直径30取半径15，柱体Y=240..382；四片正交金色十字翼跨Y=242..382。另以细零点能束延至棱镜中心，表达“直插核心”的指定关系。'},
        {'source': '二·4·十二座环绕冰枪', 'detail': '每30°一枪，直径24取半径12；轴线长110并向内下倾45°，中点位于半径250、Y=315的圆周。原文未定义起始角，首枪取+X。'},
        {'source': '三·2·核心背后金色光环', 'detail': '原文只规定直径180与背后方位；取+Z背侧、环面法线+Z、中心(401,170,451)，旋转轴+Z且枢轴同心，距离是预览采样。'},
        {'source': '坐标整数化', 'detail': 'Y=0..382共有383个整数高度；Y=0..60等闭区间按端点完整保留。名义801×721×382是连续尺寸口径，不用作坐标裁切盒。基座外缘按中心(401,361)取X1..801、Z1..721。'},
    ]
    return parts, interpretations
