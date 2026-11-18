import math

import numpy as np

from w12_common_20261116 import (
    ARMOR, GLASS, GOLD, HOT, LIGHT, VOID, WHITE, CX, CZ,
    Part, bezier, rod, wall_z,
)


WINDOW_X = np.arange(131, 932, 100)


def window_mask(points):
    dx = np.min(abs(points[:, 0, None] - WINDOW_X), axis=1)
    y = points[:, 1]
    return ((dx <= 9) & (y >= 80) & (y <= 219)) | ((dx <= 32) & (y >= 155) & (y <= 181))


def wall(side):
    tag = 'front' if side < 0 else 'back'
    part = Part('binding_wall_' + tag, '前侧约束壁' if side < 0 else '后侧约束壁', section='walls', columns=240)
    for x in np.arange(88, 974, 15):
        for shift in (-24, -8, 8, 24):
            z = round(wall_z(x, side)) + shift
            zz, xx = np.mgrid[-7:8, -7:8]
            rr = xx * xx + zz * zz
            shell = (rr <= 7.5 ** 2) & (rr >= 5.2 ** 2)
            coil = (rr <= 4.8 ** 2) & (rr >= 3.4 ** 2)
            for y in range(55, 251):
                q = np.c_[xx[shell] + x, np.full(shell.sum(), y), zz[shell] + z]
                band = y % 28
                state = GOLD if band < 3 else ARMOR if band in (3, 27) else WHITE
                part.points(q[~window_mask(q)], state)
                if y % 9 == 0:
                    q = np.c_[xx[coil] + x, np.full(coil.sum(), y), zz[coil] + z]
                    part.points(q[~window_mask(q)], LIGHT)
    xs = np.arange(81, 981)
    zz, xx = np.meshgrid(np.arange(-32, 33), xs)
    for y in (*range(45, 55), *range(251, 261)):
        q = np.c_[xx.ravel(), np.full(xx.size, y), np.rint(wall_z(xx, side) + zz).ravel()]
        part.points(q, GOLD if y in (45, 54, 251, 260) else VOID)
    for x in range(81, 981, 50):
        z = wall_z(x, side)
        for outward in (-1, 1):
            points = [bezier([[x, 50, z + outward * 32], [x, 65, z + outward * 64], [x, 172, z + outward * 61], [x, 240, z + outward * 25]], t) for t in np.linspace(0, 1, 24)]
            for a, b in zip(points[:-1], points[1:]):
                rod(part, a, b, 3.2, WHITE)
            for a, b in zip(points[:-1], points[1:]):
                rod(part, np.asarray(a) + [0, 0, outward * 2], np.asarray(b) + [0, 0, outward * 2], 1.2, GOLD)
    return part.finish()


def windows(side):
    tag = 'front' if side < 0 else 'back'
    part = Part('cross_windows_' + tag, '前壁十字花窗' if side < 0 else '后壁十字花窗', section='walls', windows=9)
    for x in WINDOW_X:
        z = round(wall_z(x, side))
        zz, xx = np.mgrid[-32:33, -35:36]
        for y in range(77, 223):
            q = np.c_[xx.ravel() + x, np.full(xx.size, y), zz.ravel() + z]
            inner = window_mask(q)
            nearest = np.min(abs(q[:, 0, None] - WINDOW_X), axis=1)
            frame = (((nearest <= 12) & (y >= 77) & (y <= 222)) | ((nearest <= 35) & (y >= 152) & (y <= 184))) & ~inner
            part.points(q[frame], GOLD)
            panel = inner & (abs(zz.ravel()) <= 1)
            part.points(q[panel], GLASS)
            for depth in (-27, -18, -9, 9, 18, 27):
                bars = inner & (zz.ravel() == depth) & (((xx.ravel() + y) % 19 == 0) | ((xx.ravel() - y) % 19 == 0))
                part.points(q[bars], HOT if abs(depth) == 9 else GOLD)
        for y in (88, 120, 168, 205):
            for dz in (-30, 30):
                part.box([x - 4, y - 3, z + dz - 2], [x + 4, y + 3, z + dz + 2], WHITE)
                part.box([x - 1, y - 1, z + dz - 3], [x + 1, y + 1, z + dz + 3], HOT)
    return part.finish()


def wing(side):
    start = 0 if side < 0 else 463
    end = start + 599
    tag = 'west' if side < 0 else 'east'
    part = Part('energy_wing_' + tag, '西翼能量注入长廊' if side < 0 else '东翼能量注入长廊', section='wings', nominal_length=600, magnetic_rings=20)
    for z0, z1 in ((333, 350), (495, 512)):
        part.box([start, 45, z0], [end, 50, z1], VOID)
        part.box([start, 51, z0 + 2], [end, 52, z0 + 4], GOLD)
        part.box([start, 51, z1 - 4], [end, 52, z1 - 2], WHITE)
    for dz in (-59, -26, 25, 58):
        z = CZ + dz
        part.box([start, 51, z - 4], [end, 55, z + 4], ARMOR)
        part.box([start, 56, z - 2], [end, 57, z + 2], LIGHT)
    for x in range(start + 8, end, 30):
        part.box([x - 3, 47, 351], [x + 3, 50, 494], WHITE)
        part.box([x - 1, 51, 351], [x + 1, 52, 494], GOLD)
    zz, yy = np.meshgrid(np.arange(-77, 78), np.arange(65, 206))
    outer = ((abs(zz) <= 13) | ((yy >= 119) & (yy <= 147)))
    inner = ((abs(zz) <= 8) & (yy >= 70) & (yy <= 200)) | ((abs(zz) <= 72) & (yy >= 124) & (yy <= 142))
    outline = outer & ~inner
    for x in range(start + 15, end, 30):
        for dx in (-2, -1, 0, 1, 2):
            part.points(np.c_[np.full(outline.sum(), x + dx), yy[outline], zz[outline] + CZ], LIGHT if dx == 0 else GOLD)
        part.box([x - 4, 53, CZ - 14], [x + 4, 66, CZ + 14], WHITE)
        for dz in (-77, 77):
            part.box([x - 5, 116, CZ + dz - 3], [x + 5, 150, CZ + dz + 3], VOID)
            part.box([x - 3, 121, CZ + dz - 4], [x + 3, 145, CZ + dz + 4], WHITE)
    direction = -side
    outer_x = start + 5 if side < 0 else end - 5
    inner_x = end - 5 if side < 0 else start + 5
    for sign in (-1, 1):
        z = CZ + sign * 84
        curve = [[outer_x, 61, z], [outer_x + direction * 180, 205, z], [inner_x - direction * 100, 205, z], [inner_x, 75, z]]
        spine = [bezier(curve, t) for t in np.linspace(0, 1, 80)]
        for a, b in zip(spine[:-1], spine[1:]):
            rod(part, a, b, 4.3, WHITE)
            rod(part, np.asarray(a) + [0, 3, 0], np.asarray(b) + [0, 3, 0], 1.4, GOLD)
        for index, t in enumerate(np.linspace(.08, .92, 10)):
            tip = bezier(curve, t)
            foot = [tip[0] - direction * 24, 55, CZ + sign * 80]
            rib = [foot, [foot[0] + direction * 48, 86, foot[2]], [tip[0] + direction * 16, tip[1] - 5, tip[2]], tip]
            line = [bezier(rib, u) for u in np.linspace(0, 1, 18)]
            for a, b in zip(line[:-1], line[1:]):
                rod(part, a, b, 2.5, ARMOR if index % 2 else WHITE)
    return part.finish()


def spire(x, side, index):
    z = round(wall_z(x, side))
    part = Part(f'gothic_spire_{index:02}', f'第{index}座哥特尖塔', section='crown', tower_center=[int(x), int(z)])
    zz, xx = np.mgrid[-26:27, -26:27]
    radial = np.maximum(abs(xx), abs(zz)) + .4142 * np.minimum(abs(xx), abs(zz))
    for y in range(328):
        r = 26 if y < 21 else 20 if y <= 250 else 20 - 13 * (y - 250) / 50 if y <= 300 else 6 * (327 - y) / 27
        shell = (radial <= r) & (radial >= max(0, r - 3.5))
        q = np.c_[xx[shell] + x, np.full(shell.sum(), y), zz[shell] + z]
        state = GOLD if y in (0, 20, 21, 48, 49, 100, 101, 152, 153, 204, 205, 249, 250, 280, 300) else VOID if y < 49 else WHITE
        part.points(q, state)
        if 50 <= y <= 248:
            flute = shell & (((abs(xx) <= 2) & (abs(zz) >= 17)) | ((abs(zz) <= 2) & (abs(xx) >= 17)))
            part.points(np.c_[xx[flute] + x, np.full(flute.sum(), y), zz[flute] + z], LIGHT)
    for dx, dz in ((-15, -15), (-15, 15), (15, -15), (15, 15)):
        part.box([x + dx - 2, 42, z + dz - 2], [x + dx + 2, 268, z + dz + 2], GOLD)
        rod(part, [x + dx, 269, z + dz], [x + dx, 295, z + dz], 1.8, HOT)
    return part.finish()


def crown():
    part = Part('discipline_halo', '白金荆棘齿轮天幕', section='crown', nominal_diameter=750)
    part.ring([CX, 294, CZ], 359, 16, WHITE, depth=11)
    part.ring([CX, 294, CZ], 361, 3, GOLD, depth=15)
    part.ring([CX, 294, CZ], 344, 3, GOLD, depth=15)
    part.ring([CX, 288, CZ], 333, 4, LIGHT, depth=5)
    for index in range(48):
        angle = 2 * math.pi * index / 48
        u = np.array([math.cos(angle), 0, math.sin(angle)])
        v = np.array([-math.sin(angle), 0, math.cos(angle)])
        c = np.array([CX, 294, CZ], float)
        vertices = [c + r * u + s * v + [0, y, 0] for r, s in ((353, -6), (353, 6), (375, -4), (375, 4)) for y in (-7, 7)]
        part.hull(vertices, WHITE)
        rod(part, c + 355 * u + [0, 8, 0], c + 374 * u + [0, 8, 0], 1, GOLD)
        rod(part, c + 332 * u + [0, -6, 0], c + 350 * u + [0, -6, 0], 2, GOLD)
    for index in range(8):
        angle = index * math.pi / 4
        u = np.array([math.cos(angle), 0, math.sin(angle)])
        v = np.array([-math.sin(angle), 0, math.cos(angle)])
        c = np.array([CX, 280, CZ], float)
        for radius, half, top in ((348, 12, 327), (329, 8, 314)):
            vertices = [c + (radius + dr) * u + s * v + [0, y, 0] for dr, s in ((-13, -half), (-13, half), (13, -half), (13, half)) for y in (0, 10)]
            vertices.append(c + radius * u + [0, top - 280, 0])
            part.hull(vertices, WHITE)
            rod(part, c + radius * u + [0, 11, 0], c + radius * u + [0, top - 280, 0], 1, GOLD)
        rod(part, c + 346 * u - 28 * v + [0, 17, 0], c + 346 * u + 28 * v + [0, 17, 0], 3, GOLD)
    return part.finish()


def filaments():
    part = Part('discipline_filaments', '320根戒律光丝', section='crown', filament_count=320)
    for index in range(320):
        angle = index * 2 * math.pi / 320
        radius = 332 + (index % 4) * 4
        x, z = round(CX + radius * math.cos(angle)), round(CZ + radius * math.sin(angle))
        bottom = 200 + (index * 37 % 71)
        part.box([x, bottom, z], [x, 280, z], GLASS)
        part.box([x, 281, z], [x, 290, z], GOLD)
        part.box([x - 1, bottom, z - 1], [x + 1, bottom + 2, z + 1], LIGHT)
    return part.finish()


def build():
    parts = []
    for side in (-1, 1):
        parts.extend((wall(side), windows(side), wing(side)))
    for index, (side, x) in enumerate(((side, x) for side in (-1, 1) for x in (81, 381, 681, 980)), 1):
        parts.append(spire(x, side, index))
    parts.extend((crown(), filaments()))
    notes = [
        '双壁采用X=81..980共900格投影长度，弧形中线前壁z=100+110×((x−531)/450)²，后壁关于Z423镜像；厚度按Z轴65格取样，弧长大于900格，原文未给曲率。飞扶壁在墙厚之外完整保留。',
        '每壁四排、每排60根直径15格中空约束柱，共480根；十字孔穿透全部四排。原文“数千根柱”与给定长度、直径及墙厚存在数量冲突，本稿记录实际480根。',
        '每壁9个十字花窗，中心X131..931间隔100格；竖孔Y80..219共140层，横孔Y155..181，竖孔宽19、横孔宽65为本稿取样。金玻璃屏障、准直器和交叉束管为实体。',
        '两条长廊沿X轴对向中心：西侧0..599、东侧463..1062，各600格；两者在X463..599重复137格，完整保留原文长度。地板Z333..512共180格，骨架及十字磁环包络由真实方块计算。',
        '长廊名义Y45..205；金色十字磁环每条20座，中心X按各自起点+15、每30格布置。翼骨使用连续体素弧线，曲线和截面为本稿取样，不设任何专用接口位。',
        '八尖塔中心位于两壁X81、381、681、980的中线上，Y0..327包含328层。墙体各层端点、塔脚与尖顶完整保留，原文327高度和含端点层数分别记录。',
        '天幕以半径375的齿尖作为750名义直径，主环外半径361、内半径328；48齿、八组双荆棘十字冠、Y280..327为本稿取样。齿尖和梁厚按实际占格计算包络。',
        '320根真实金色玻璃光丝均匀分布，顶端Y280、底端Y200..270；Y281..290金色挂接段连至光环。长度序列与截面为本稿取样。',
    ]
    return parts, notes
