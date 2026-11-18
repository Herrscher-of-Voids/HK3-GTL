from w08_common_20261116 import *


def star_floor():
    p = Part('base_star_foundation', '八芒星与卡斯兰娜十字重装底盘', source='二·4：Y0..30八角星芒矩阵、45格防爆挡板')
    z, x = np.mgrid[0:922, 0:979]
    dx, dz = (x - CX) / 489, (z - 460.5) / 460.5
    angle = np.arctan2(dz, dx)
    sector = np.abs((angle + np.pi / 8) % (np.pi / 4) - np.pi / 8)
    radial = np.hypot(dx, dz)
    edge = (1 - .57 * math.cos(np.pi / 8)) / (.57 * math.sin(np.pi / 8))
    outline = 1 / (np.cos(sector) + edge * np.sin(sector))
    footprint = radial <= outline
    boundary = footprint & (radial >= outline - .022)
    cross = footprint & ((np.abs(dx) < .075) | (np.abs(dz) < .075))
    slot = np.zeros_like(footprint)
    rail_masks = []
    for k in range(8):
        a = k * np.pi / 4
        along = (x - CX) * np.cos(a) + (z - CZ) * np.sin(a)
        across = -(x - CX) * np.sin(a) + (z - CZ) * np.cos(a)
        channel = footprint & (along >= 85) & (np.abs(across) < 18)
        slot |= channel
        rail_masks.append((along, across, channel))
    for y in range(31):
        if y <= 4:
            mask = footprint
        elif y >= 26:
            mask = footprint & ~slot
        else:
            mask = boundary | (cross & ~slot)
        p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], DARK)
    for y in range(31, 46):
        p.points(np.c_[x[boundary], np.full(boundary.sum(), y), z[boundary]], DARK)
    for y, state in [(29, GRATE), (30, METAL), (34, GOLD), (40, RED), (45, GOLD)]:
        mask = boundary if y > 30 else footprint & ~slot & ((x % 32 < 2) | (z % 32 < 2))
        p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], state)
    for y in (30, 31):
        mask = footprint & ~slot & (np.minimum(abs(dx), abs(dz)) < .012)
        p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], GOLD)
    return p.finish(), rail_masks


def channel(index, along, across, mask):
    p = Part(f'base_injection_channel_{index + 1:02d}', f'第{index + 1}道36格宽25格深粒子加速槽', nominal_width=36, nominal_depth=25)
    z, x = np.mgrid[0:922, 0:979]
    p.points(np.c_[x[mask], np.full(mask.sum(), 5), z[mask]], GRATE)
    rails = mask & ((abs(abs(across) - 10) <= 1.5) | (abs(across) <= 1))
    p.points(np.c_[x[rails], np.full(rails.sum(), 6), z[rails]], GOLD)
    p.points(np.c_[x[rails], np.full(rails.sum(), 7), z[rails]], ORANGE)
    for y in range(6, 31):
        wall = mask & (abs(across) >= 16)
        p.points(np.c_[x[wall], np.full(wall.sum(), y), z[wall]], METAL if y % 8 == 0 else DARK)
    a = index * np.pi / 4
    u, v = np.array([math.cos(a), 0, math.sin(a)]), np.array([-math.sin(a), 0, math.cos(a)])
    for distance in (170, 245, 320):
        for side in (-1, 1):
            center = np.array([CX, 7, CZ]) + u * distance + v * side * 31
            low, high = center + [-6, 0, -6], center + [6, 29, 6]
            p.box(low, high, DARK)
            p.box(center + [-7, 0, -7], center + [7, 3, 7], GOLD)
            p.box(center + [-6, 27, -6], center + [6, 29, 6], ARMOR)
            for level in (6, 11, 16, 21):
                rod(p, center + [-7, level, -7], center + [7, level, -7], 1.2, COOL)
                rod(p, center + [-7, level, 7], center + [7, level, 7], 1.2, COOL)
                rod(p, center + [-7, level, -7], center + [-7, level, 7], 1.2, METAL)
                rod(p, center + [7, level, -7], center + [7, level, 7], 1.2, METAL)
    return p.finish()


def bridge():
    p = Part('base_cathedral_bridge', '180×60纯白金圣堂舰桥', source='二·4：前端Y45舰桥；五：主控(489,46,10)', nominal_length=180, nominal_width=60)
    p.box([459, 35, 0], [518, 42, 179], ARMOR)
    p.box([462, 43, 0], [515, 45, 179], METAL)
    for x in (459, 518):
        p.box([x, 43, 0], [x, 46, 179], GOLD)
        p.box([x, 37, 1], [x, 39, 178], LIGHT)
    for z in range(22, 176, 22):
        p.box([464, 46, z], [513, 46, z + 1], GOLD)
        for x in (463, 514):
            p.box([x - 1, 46, z - 1], [x + 1, 49, z + 1], ARMOR)
    p.box([480, 46, 4], [498, 46, 16], ARMOR)
    p.box([482, 47, 4], [496, 48, 6], COOL)
    p.box([480, 46, 11], [498, 47, 13], GOLD)
    return p.finish()


def anvil():
    p = Part('base_stellar_anvil', '恒星砧、凝固岩浆巨浪与锯齿空间裂隙', source='二·1：剑尖周围150格半径凝固岩浆浪与空间裂隙')
    p.ring([CX, 26, CZ], 85, 28, VOID, depth=24)
    p.ring([CX, 39, CZ], 86, 7, GOLD, depth=3)
    p.ring([CX, 33, CZ], 60, 5, RED, depth=7)
    for index in range(16):
        a = index * 2 * np.pi / 16
        radial = np.array([math.cos(a), 0, math.sin(a)])
        tangent = np.array([-math.sin(a), 0, math.cos(a)])
        center = np.array([CX, 0, CZ])
        points = [center + radial * 64 + [0, 29, 0], center + radial * 97 + tangent * 16 + [0, 37, 0],
                  center + radial * 145 + tangent * 25 + [0, 8, 0]]
        rod(p, points[0], points[1], 5, MAGMA)
        rod(p, points[1], points[2], 3, RED)
        rod(p, points[0] + [0, 4, 0], points[1] + [0, 3, 0], 1.6, ORANGE)
        for j in range(3):
            at = center + radial * (90 + j * 22) + tangent * ((j % 2) * 12 - 6) + [0, 31, 0]
            rod(p, at, at + radial * 20 + tangent * (10 if j % 2 else -10), 1.5, RED_GLASS)
    return p.finish()


def build():
    floor, masks = star_floor()
    parts = [floor] + [channel(index, *values) for index, values in enumerate(masks)]
    parts += [anvil(), bridge()]
    controller = Part('controller_marker', '唯一主控定位', controller_blueprint=[489, 46, 10])
    controller.points([[489, 46, 10]], CONTROL)
    parts.append(controller.finish())
    notes = [
        '八角星由八个外尖点与八个内凹点离散化，叠加纵横十字梁；原文未给星形内径，内尖半径按外尖的0.57取样。',
        '底盘采用上下装甲板、周边挡板及十字承重梁；八条槽从Y30下挖至Y5，25格深，36格宽；原文未给冷却塔数量，按每槽两列、每列三座取样。',
        '主控舰桥60格宽、180格长，主甲板Y45，主控固定在(489,46,10)；舰桥梁厚与栏杆属于整数格取样。',
        '原文第五节集中接口、两座专用能量仓塔基及64预留仓位由负责人全实体自由接口规则覆盖；完整舰桥保留，专用接口槽与支座不生成。',
        '底座连续坐标端点X0..978、Z0..921参与完整生成，实际占格边界随星尖、挡板及其他构件计算，不以名义978×921裁切。'
    ]
    return parts, notes
