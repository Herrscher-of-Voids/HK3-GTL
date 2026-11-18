import math

import numpy as np

from author_w05_shapes_20261115 import Part


ARMOR, DARK, ICE, GOLD, COIL, CORE, GRID, ZERO = range(1, 9)
CENTER = np.array([401.0, 0.0, 361.0])


def perimeter_point(distance):
    x, z = 1.0, 1.0
    lengths = (800.0, 720.0, 800.0, 720.0)
    segment = 0
    while distance > lengths[segment]:
        distance -= lengths[segment]
        segment += 1
    if segment == 0:
        return np.array([x + distance, 0, z])
    if segment == 1:
        return np.array([801, 0, z + distance])
    if segment == 2:
        return np.array([801 - distance, 0, 721])
    return np.array([1, 0, 721 - distance])


def pillar(index):
    p = Part(f'ice_heat_pillar_{index + 1:02d}', f'第{index + 1}座排热冰柱',
             source='二·1：沿外围每隔40格嵌入，共24座', material='外层冰晶玻璃、内芯青色超导线圈',
             sampling='原文每隔40格与共24座不相容；按矩形周界等距采样24座。冰柱沿斜坡墙向内倾斜。')
    start = perimeter_point(index * 3040 / 24)
    radial = np.array([401 - start[0], 0, 361 - start[2]], float)
    radial /= np.linalg.norm(radial)
    for y in range(61):
        center = start + radial * (50 * y / 60)
        center[1] = y
        x0, x1 = math.floor(center[0] - 8), math.ceil(center[0] + 8)
        z0, z1 = math.floor(center[2] - 8), math.ceil(center[2] + 8)
        z, x = np.mgrid[z0:z1 + 1, x0:x1 + 1]
        distance = (x - center[0]) ** 2 + (z - center[2]) ** 2
        p.points(np.c_[x[distance <= 64], np.full(np.count_nonzero(distance <= 64), y), z[distance <= 64]], ICE)
        p.points(np.c_[x[distance <= 16], np.full(np.count_nonzero(distance <= 16), y), z[distance <= 16]], COIL)
    return p.finish()


def perimeter_wall():
    p = Part('perimeter_ice_breakwater', '50格内倾式永冻防波堤', source='二·1：最外圈、宽约50格、高60格、向内倾斜的暗蓝重装甲斜坡墙',
             sampling='每层边界整体向中心内收50×Y/60格，墙体横向厚50格；矩形角部由相邻边自然相交。')
    for y in range(61):
        inset = round(50 * y / 60)
        x0, x1 = 1 + inset, 801 - inset
        z0, z1 = 1 + inset, 721 - inset
        inner = 50
        top_z, top_x = np.mgrid[z0:z0 + inner, x0:x1 + 1]
        bottom_z, bottom_x = np.mgrid[z1 - inner + 1:z1 + 1, x0:x1 + 1]
        side_z, left_x = np.mgrid[z0 + inner:z1 - inner + 1, x0:x0 + inner]
        right_z, right_x = np.mgrid[z0 + inner:z1 - inner + 1, x1 - inner + 1:x1 + 1]
        q = np.concatenate((
            np.c_[top_x.ravel(), np.full(top_x.size, y), top_z.ravel()],
            np.c_[bottom_x.ravel(), np.full(bottom_x.size, y), bottom_z.ravel()],
            np.c_[left_x.ravel(), np.full(left_x.size, y), side_z.ravel()],
            np.c_[right_x.ravel(), np.full(right_x.size, y), right_z.ravel()],
        )).reshape(-1, 3)
        p.points(q, DARK)
        if y % 10 == 0:
            p.points(q, ARMOR)
        if y % 12 == 0:
            p.points(q, COIL)
    return p.finish()


def funnel():
    p = Part('absolute_zero_heat_sink', '深渊漏斗与零点能底池', source='二·1：Y0..20地面、深达40格漏斗状阶梯深渊、底部液态氦/液态时空',
             sampling='“Y0..20地面”与“深40格”相交于Y0基面；漏斗按深度向下延伸至Y=-40，顶口半径80、底池半径12为展示取样。')
    xz = np.arange(-81, 82)
    z, x = np.meshgrid(xz, xz, indexing='ij')
    for depth in range(41):
        y = -depth
        radius = 80 - 68 * depth / 40
        radial = np.sqrt(x * x + z * z)
        wall = (radial <= radius) & (radial >= radius - 3)
        points = np.c_[x[wall] + 401, np.full(np.count_nonzero(wall), y), z[wall] + 361]
        p.points(points, DARK if y % 8 else ICE)
    pool = x * x + z * z <= 12 ** 2
    p.points(np.c_[x[pool] + 401, np.full(np.count_nonzero(pool), -40), z[pool] + 361], ZERO)
    return p.finish()


def hexagram_bridge():
    p = Part('six_point_superconducting_bridge', '六芒星超导栈桥', source='二·1：Y40..60、直径700格、白色与暗银格雷机械方块',
             center=[401, 0, 361], nominal_diameter=700,
             sampling='六尖端按中心半径350的两组三角形取样；主桥厚21格对应Y40..60，格栅与线圈叠层收在该高度内。')
    angles = np.radians([-90, 30, 150, 90, -30, -150])
    vertices = np.c_[401 + 350 * np.cos(angles), np.full(6, 50), 361 + 350 * np.sin(angles)]
    for triangle in ((0, 1, 2), (3, 4, 5)):
        for index in range(3):
            start, end = vertices[triangle[index]], vertices[triangle[(index + 1) % 3]]
            p.beam(start, end, 10, ARMOR)
            p.beam(start + [0, 2, 0], end + [0, 2, 0], 7, GRID)
            p.beam(start + [0, 5, 0], end + [0, 5, 0], 3, COIL)
    return p.finish()


def precooler(index, center):
    x0, z0 = center
    p = Part(f'precooling_tower_{index + 1:02d}', f'第{index + 1}座极低温预冷塔', source='二·1：六芒星六尖端各接一座直径60格的多层线圈预冷塔',
             center=[x0, 0, z0], diameter=60, y=[0, 60], sampling='原文未给塔高，按底层Y0..60布置。')
    x = np.arange(x0 - 31, x0 + 32)
    z = np.arange(z0 - 31, z0 + 32)
    zz, xx = np.meshgrid(z, x, indexing='ij')
    r2 = (xx - x0) ** 2 + (zz - z0) ** 2
    for y in range(61):
        outer = (r2 <= 30 ** 2) & (r2 >= 26 ** 2)
        glass = (r2 <= 22 ** 2) & (r2 >= 17 ** 2)
        core = r2 <= (8 + (y % 12 == 0) * 4) ** 2
        for mask, state in ((outer, ARMOR if y % 10 == 0 else DARK), (glass, ICE), (core, COIL)):
            count = np.count_nonzero(mask)
            p.points(np.c_[xx[mask], np.full(count, y), zz[mask]], state)
    return p.finish()


def ring_points(radius, center_y, degrees, spacing, radial_half, normal_half):
    angle = math.radians(degrees)
    u = np.array([1.0, 0, 0])
    v = np.array([0, math.sin(angle), math.cos(angle)])
    n = np.cross(u, v)
    count = math.ceil(2 * math.pi * radius / spacing)
    theta = np.arange(count) * (2 * math.pi / count)
    radial = np.cos(theta)[:, None] * u + np.sin(theta)[:, None] * v
    curve = np.array([401, center_y, 361]) + radius * radial
    return curve, radial, n


def annulus_tube(name, label, radius, center_y, tilt, radial_half, normal_half, state, circular=False):
    p = Part(name, label, source='三：倾斜交错的暴风雪星环', radius=radius, diameter=radius * 2,
             tilt_degrees=tilt, center=[401, center_y, 361],
             sampling='原文未指定垂直中心高度；取Y190，使倾斜环落在所述Y80..300空间内。')
    curve, radial, normal = ring_points(radius, center_y, tilt, 1.2, radial_half, normal_half)
    offsets = np.array([(dr, dn) for dr in range(-radial_half, radial_half + 1)
                        for dn in range(-normal_half, normal_half + 1)
                        if not circular or dr * dr + dn * dn <= radial_half ** 2], float)
    points = curve[:, None, :] + (radius + offsets[None, :, 0, None]) * radial[:, None, :] - radius * radial[:, None, :]
    points += offsets[None, :, 1, None] * normal
    p.points(points.reshape(-1, 3), state)
    return p


def gold_ring_spurs():
    p = Part('golden_cross_star_spurs', '每30度金色十字星芒尖刺', source='三·第一环：每隔30度一根40格金色十字星芒尖刺', count=12, length=40,
             sampling='十字副翼各按原文长度40取样；副翼宽度未给，预览取12格。')
    curve, radial, normal = ring_points(260, 190, 15, 1.2, 6, 3)
    for index in range(12):
        at = round(index * len(curve) / 12)
        base, direction, n = curve[at], radial[at], normal
        tip = base + direction * 40
        p.beam(base, tip, 2, GOLD)
        across = np.cross(direction, n)
        p.beam(tip - across * 6, tip + across * 6, 1, GOLD)
        p.beam(tip - n * 6, tip + n * 6, 1, GOLD)
    return p.finish()


def ice_spikes():
    p = Part('outer_ring_ice_spikes', '第三环外侧冰晶倒刺', source='三·第三环：外侧向外延伸无数锋利不规则冰晶倒刺',
             sampling='原文未给倒刺数量与长度；按144根等角疏密混合、长度8..20格转译，不作边界裁切。')
    for index in range(144):
        angle = 2 * math.pi * index / 144
        direction = np.array([math.cos(angle), 0, math.sin(angle)])
        tangent = np.array([-math.sin(angle), 0, math.cos(angle)])
        inner = np.array([401, 180, 361]) + 354 * direction
        length = 8 + (index * 37 % 13)
        outer = inner + direction * length + tangent * ((index % 5 - 2) * 2) + [0, (index % 7 - 3) * 2, 0]
        p.beam(inner, outer, 2 if index % 3 else 3, ICE)
    return p.finish()


def ring3_bridge(index, angle):
    p = Part(f'outer_ring_energy_bridge_{index + 1}', f'第三环第{index + 1}座斜拉能量桥',
             source='三·第三环：六座斜拉能量桥连接六座预冷塔', sampling='为体现斜拉，环上锚点相对塔位错开15度。')
    tower_angle = math.radians(angle)
    ring_angle = tower_angle + math.radians(15)
    start = np.array([401 + 350 * math.cos(tower_angle), 58, 361 + 350 * math.sin(tower_angle)])
    end = np.array([401 + 355 * math.cos(ring_angle), 180, 361 + 355 * math.sin(ring_angle)])
    p.beam(start, end, 6, ARMOR)
    p.beam(start + [0, 1, 0], end + [0, 1, 0], 3, COIL)
    p.beam(start + [0, 2, 0], end + [0, 2, 0], 1, ICE)
    return p.finish()


def controller_marker():
    p = Part('controller_position_marker', '主控定位标记（非注册方块）', source='二·1：南向主栈桥尽头观景台',
             controller=[401, 45, 700], facing='north', preview_only=True,
             conflict='主控坐标按原文固定；它落在南端预冷塔直径60格范围内，与塔体预览占格重叠。')
    p.points([[401, 45, 700]], CORE)
    return p.finish()


def build():
    parts = [perimeter_wall(), funnel()]
    parts.extend(pillar(index) for index in range(24))
    parts.append(hexagram_bridge())
    angles = [-90, -30, 30, 90, 150, 210]
    centers = [(401 + 350 * math.cos(math.radians(a)), 361 + 350 * math.sin(math.radians(a))) for a in angles]
    parts.extend(precooler(i, center) for i, center in enumerate(centers))
    parts.extend((annulus_tube('golden_inner_ring', '第一环·金色律者几何环', 260, 190, 15, 6, 3, GOLD).finish(),
                  gold_ring_spurs(),
                  annulus_tube('accelerator_outer_shell', '第二环·冷却粒子加速器外壁', 320, 190, -20, 10, 10, DARK, circular=True).finish()))
    core = Part('accelerator_luminous_core', '第二环·蓝白超导核心', source='三·第二环：蓝白发光核心与透明视窗',
                sampling='管截面直径20，内芯半径7；每60度一组透明窗，窗处保留内芯。')
    curve, radial, normal = ring_points(320, 190, -20, 1.2, 10, 10)
    disk = np.array([(dr, dn) for dr in range(-7, 8) for dn in range(-7, 8) if dr * dr + dn * dn <= 49], float)
    core_points = curve[:, None, :] + disk[None, :, 0, None] * radial[:, None, :] + disk[None, :, 1, None] * normal
    core.points(core_points.reshape(-1, 3), COIL)
    parts.append(core.finish())
    windows = Part('accelerator_viewports', '第二环·间隔透明视窗', source='三·第二环：外壁每隔一段设透明视窗露出内芯',
                   sampling='按60度间隔、每组4度宽取样；非原文数值。')
    curve, radial, normal = ring_points(320, 190, -20, 1.2, 10, 10)
    theta = np.arange(len(curve)) * 2 * math.pi / len(curve)
    offsets = np.array([(dr, dn) for dr in range(-10, 11) for dn in range(-10, 11)
                        if 64 <= dr * dr + dn * dn <= 100], float)
    selected = np.min(np.abs(((theta[:, None] - np.radians(np.arange(0, 360, 60)) + math.pi) % (2 * math.pi)) - math.pi), axis=1) <= math.radians(2)
    q = curve[selected, None, :] + offsets[None, :, 0, None] * radial[selected, None, :] + offsets[None, :, 1, None] * normal
    windows.points(q.reshape(-1, 3), ICE)
    parts.append(windows.finish())
    outer = annulus_tube('horizontal_outer_ring_walkway', '第三环·水平高空回廊', 355, 180, 0, 6, 2, ARMOR)
    parts.append(outer.finish())
    grid = Part('horizontal_outer_ring_grid', '第三环·回廊格栅与导能线', source='三·第三环：完整环形高空回廊')
    curve, radial, normal = ring_points(355, 180, 0, 1.2, 6, 2)
    offsets = np.array([(dr, dn) for dr in range(-3, 4) for dn in range(-2, 3)], float)
    q = curve[:, None, :] + offsets[None, :, 0, None] * radial[:, None, :] + offsets[None, :, 1, None] * normal
    grid.points(q.reshape(-1, 3), GRID)
    parts.append(grid.finish())
    parts.extend(ring3_bridge(index, angle) for index, angle in enumerate(angles))
    parts.append(ice_spikes())
    parts.append(controller_marker())
    interpretations = [
        {'source': '二·1', 'conflict': '每40格设置一座与总数24座不一致。', 'preview': '严格保留24座，沿周界等距分布。'},
        {'source': '二·1', 'conflict': '地面Y0..20与向下深40格跨越Y=0基面；原文没有说明漏斗相对地面的上沿标高。', 'preview': '以Y=0为基面向下取样到Y=-40，顶口半径80、底池半径12为展示取样。'},
        {'source': '二·1', 'conflict': '主控(401,45,700)与南端预冷塔半径30范围相交。', 'preview': '保留主控绝对坐标，重叠交给整机占格审计，不移动塔或主控。'},
        {'source': '二·1', 'conflict': '六芒星直径700，中心Z361时南尖端到Z711；南塔半径30继续越出名义深721边界，控制器Z700也落入塔范围。', 'preview': '保留几何关系，不裁切或移动，实际包围盒由整机导出计算。'},
        {'source': '三·第一环', 'conflict': '环心高度未指定。', 'preview': '取Y190，15度、直径520环主体位于Y123..257；12根40格金色十字芒刺按30度布置。'},
        {'source': '三·第二环', 'conflict': '环心高度未指定。', 'preview': '取Y190，-20度、直径640环主体位于Y81..299；保留与第一环原文要求的交错穿越。'},
        {'source': '三·第三环', 'conflict': '直径710回廊本体可落在名义X/Z边界附近，外向冰刺明确越界。', 'preview': '环半径355，144根冰刺取样长度8..20；不夹到801×721边界。'},
        {'source': '二·1、三·第三环', 'conflict': '星尖塔中心、回廊锚点及管线截面未逐点指定。', 'preview': '按中心(401,361)、六方位和15度桥端错位完成可见连通，属于预览取样。'},
    ]
    return parts, interpretations
