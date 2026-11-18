import math

import numpy as np

from w09_common_20261116 import (
    ARMOR, CENTER, CRIMSON, CX, CZ, DARK, GILDED, GLASS, GOLD, HOT,
    PEAKS, RED, WHITE, Part, rod,
)


def column(part, bottom, height, angle, heading, width, depth):
    bottom = np.asarray(bottom, float)
    along = np.array([math.cos(heading), 0, math.sin(heading)])
    across = np.array([-along[2], 0, along[0]])
    displacement = along * height / math.tan(math.radians(angle))
    radius = math.ceil(math.hypot(width, depth))
    for level in range(height + 1):
        t = level / height
        center = bottom + displacement * t + [0, level, 0]
        w, d = width * (1 - .63 * t), depth * (1 - .59 * t)
        x, z = np.mgrid[math.floor(center[0]) - radius:math.ceil(center[0]) + radius + 1,
                       math.floor(center[2]) - radius:math.ceil(center[2]) + radius + 1]
        q = np.c_[x.ravel(), np.full(x.size, center[1]), z.ravel()]
        local = q - center
        a, b = local @ along, local @ across
        inside = (abs(a) <= w) & (abs(b) <= d) & (abs(a) / w + abs(b) / d <= 1.55)
        q, a, b = q[inside], a[inside], b[inside]
        states = np.full(len(q), DARK, np.uint8)
        states[(a > w - 4) | (abs(b) > d - 4)] = ARMOR
        states[(a < -w + 3) & (abs(b) < d * .72)] = GLASS
        states[(abs(abs(b) - d * .76) < 1.3) | (level % 28 < 2)] = GILDED
        states[(a < -w + 4) & (abs(b - ((level // 13) % 3 - 1) * 3) < 2)] = RED
        for state in (DARK, ARMOR, GLASS, GILDED, RED):
            part.points(q[states == state], state)
    top = bottom + displacement + [0, height, 0]
    for side in (-1, 1):
        rod(part, bottom + across * side * depth * .72,
            top + across * side * depth * .28, 1.5, GOLD)
    return top


def pavilion(index, top, heading):
    part = Part(f'taixu_pavilion_{index + 1}', f'太虚机械剑亭{index + 1}',
                section='mountains', peak_index=index + 1, floor_blueprint_xyz=top.tolist())
    along = np.array([math.cos(heading), 0, math.sin(heading)])
    across = np.array([-along[2], 0, along[0]])
    floor = top + [0, 3, 0]
    for y, radius, state in ((-3, 23, DARK), (-2, 24, GILDED), (-1, 23, ARMOR), (0, 21, WHITE)):
        x, z = np.mgrid[-radius:radius + 1, -radius:radius + 1]
        part.points(floor + x.ravel()[:, None] * along + z.ravel()[:, None] * across + [0, y, 0], state)
    for a in (-15, 15):
        for b in (-15, 15):
            start = floor + along * a + across * b
            rod(part, start, start + [0, 23, 0], 2.4, DARK)
            rod(part, start + along, start + along + [0, 23, 0], .8, RED)
            part.ring(start + [0, 4, 0], 3.5, 1.5, GOLD, depth=2)
    for side in (-1, 1):
        rod(part, floor + along * side * 18 - across * 18 + [0, 21, 0],
            floor + along * side * 18 + across * 18 + [0, 21, 0], 2.1, ARMOR)
        rod(part, floor + across * side * 18 - along * 18 + [0, 21, 0],
            floor + across * side * 18 + along * 18 + [0, 21, 0], 2.1, ARMOR)
    x, z = np.mgrid[math.floor(floor[0]) - 46:math.ceil(floor[0]) + 47,
                   math.floor(floor[2]) - 46:math.ceil(floor[2]) + 47]
    delta = np.c_[x.ravel() - floor[0], np.zeros(x.size), z.ravel() - floor[2]]
    a, b = delta @ along, delta @ across
    keep = (abs(a) <= 32) & (abs(b) <= 29)
    a, b, delta = a[keep], b[keep], delta[keep]
    slope = np.maximum(abs(a) / 32, abs(b) / 29)
    roof_y = np.rint(34 - 13 * slope + 5 * np.maximum(0, (slope - .78) / .22))
    roof = floor + delta + roof_y[:, None] * [0, 1, 0]
    for offset in (0, -1):
        part.points(roof + [0, offset, 0], GILDED)
    seams = (np.abs(a - np.rint(a / 7) * 7) < .55) | (np.abs(b - np.rint(b / 7) * 7) < .55)
    part.points(roof[seams] + [0, 1, 0], GOLD)
    rod(part, floor - along * 19 + [0, 35, 0], floor + along * 19 + [0, 35, 0], 1.5, DARK)
    for sa in (-1, 1):
        for sb in (-1, 1):
            start = floor + along * sa * 24 + across * sb * 21 + [0, 25, 0]
            middle = floor + along * sa * 32 + across * sb * 29 + [0, 28, 0]
            tip = floor + along * sa * 39 + across * sb * 35 + [0, 34, 0]
            rod(part, start, middle, 2, DARK)
            rod(part, middle, tip, 1.3, GILDED)
    return part.finish()


def waterfalls(index, origin, height, heading):
    inward = np.array([math.cos(heading), 0, math.sin(heading)])
    across = np.array([-inward[2], 0, inward[0]])
    mouth = origin + inward * (height * .58 / math.tan(math.radians(75)) + 29)
    mouth[1] = 46 + round(height * .58)
    part = Part(f'peak_waterfalls_{index + 1}', f'机械太虚山红白飞瀑{index + 1}',
                section='mountains', peak_index=index + 1, fall_bottom_y=5,
                exhaust_center_blueprint_xyz=np.rint(mouth).astype(int).tolist(), fall_count=2)
    for side, state in ((-1, RED), (1, WHITE)):
        center = mouth + across * side * 11
        for offset in np.arange(-5, 6):
            start = center + across * offset
            rod(part, start - inward * 14, start + inward * 2, 2.5, DARK)
            rod(part, start - inward * 13 + [0, 3, 0], start + inward * 3 + [0, 3, 0], 1.2, GILDED)
        for width in range(-3, 4):
            for depth in range(3):
                a = center + across * width + inward * (depth + 4)
                q = a + np.arange(5, int(mouth[1]) + 1)[:, None] * [0, 1, 0] - [0, a[1], 0]
                part.points(q, GOLD if abs(width) == 3 else CRIMSON if state == RED and depth == 2 else state)
        splash = center + inward * 5
        splash[1] = 5
        part.ring(splash, 8, 2, state, depth=1)
    return part.finish()


def fan_depth(x, y):
    return 900 + 110 * ((y - 187) / 130) + 14 * ((x - CX) / 225) ** 2


def fan_line(part, points, radius, state):
    for a, b in zip(np.asarray(points, float)[:-1], np.asarray(points, float)[1:]):
        length = np.linalg.norm(b - a)
        line = a + np.linspace(0, 1, math.ceil(length * 2) + 1)[:, None] * (b - a)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                q = np.rint(line + [dx, dy])
                part.points(np.c_[q, fan_depth(q[:, 0], q[:, 1]) - 4], state)


def fan():
    part = Part('mechanical_fan_canopy', '十八骨万象机械折扇天幕', section='crown',
                fan_ribs=18, fan_nominal_width=450, fan_bottom_y=187, fan_top_y=317,
                fan_pivot_blueprint_xyz=[CX, 187, 900],
                panel_drawing='实体像素太虚山河与星图电路')
    x, y = np.mgrid[-225:226, 0:131]
    keep = (x / 225) ** 2 + (y / 130) ** 2 <= 1
    x, y = x[keep], y[keep]
    z = fan_depth(x + CX, y + 187)
    panel = np.c_[x + CX, y + 187, z]
    for depth in (0, 1, 2):
        part.points(panel + [0, 0, depth], GLASS)
    for index, angle in enumerate(np.linspace(0, math.pi, 18)):
        end = np.array([225 * math.cos(angle), 130 * math.sin(angle)])
        t = (x * end[0] + y * end[1]) / (end @ end)
        distance = abs(x * end[1] - y * end[0]) / np.linalg.norm(end)
        rib = (distance <= 2) & (t >= 0) & (t <= 1)
        for depth in (-3, -2, -1, 3, 4):
            part.points(panel[rib] + [0, 0, depth], GILDED if index % 2 else GOLD)
    edge = np.sqrt((x / 225) ** 2 + (y / 130) ** 2) >= .981
    part.points(panel[edge] + [0, 0, -2], GOLD)
    skyline = np.array([[-193, 20], [-168, 40], [-145, 28], [-111, 77], [-83, 44],
                        [-48, 62], [-14, 92], [20, 56], [48, 71], [87, 44],
                        [120, 57], [148, 29], [188, 23]])
    for a, b in zip(skyline[:-1], skyline[1:]):
        for xx in range(int(a[0]), int(b[0]) + 1):
            peak = round(a[1] + (b[1] - a[1]) * (xx - a[0]) / (b[0] - a[0]))
            yy = np.arange(199, 187 + peak + 1)
            part.points(np.c_[np.full(len(yy), CX + xx), yy, fan_depth(CX + xx, yy) - 3],
                        ARMOR if (xx // 16) % 3 else DARK)
    fan_line(part, skyline + [CX, 187], 1, GOLD)
    for x0, y0, dx, dy in ((-173, 240, 33, 13), (-91, 281, 27, 12),
                           (38, 288, 29, -12), (119, 257, 36, -10)):
        points = np.array([[CX + x0, y0], [CX + x0 + dx, y0],
                           [CX + x0 + dx, y0 + dy], [CX + x0 + dx + 16, y0 + dy]])
        fan_line(part, points, 0, RED)
        for px, py in points[[0, -1]]:
            for ax, ay in ((-2, 0), (-1, -1), (-1, 1), (0, -2), (0, 2), (1, -1), (1, 1), (2, 0)):
                qx, qy = px + ax, py + ay
                part.points([[qx, qy, fan_depth(qx, qy) - 5]], HOT)
    fan_line(part, [(CX - 175, 204), (CX - 90, 204), (CX - 77, 211),
                    (CX - 12, 211), (CX + 2, 205), (CX + 170, 205)], 1, RED)
    part.box([CX - 14, 187, 887], [CX + 14, 199, 900], DARK)
    part.box([CX - 9, 189, 884], [CX + 9, 197, 886], GILDED)
    return part.finish()


def throne():
    part = Part('sovereign_observation_throne', '唯我独尊黑红重工御座', section='crown',
                seat_blueprint_xyz=[CX, 295, 900], throne_front='-Z')
    for y0, y1, x, z0, z1, state in ((284, 288, 32, 869, 919, DARK),
                                    (289, 291, 30, 872, 917, GILDED),
                                    (292, 293, 27, 875, 914, ARMOR),
                                    (294, 295, 17, 884, 908, RED),
                                    (296, 298, 17, 886, 909, DARK)):
        part.box([CX - x, y0, z0], [CX + x, y1, z1], state)
    part.hull([[CX - 23, 295, 908], [CX + 23, 295, 908], [CX - 16, 315, 914],
               [CX + 16, 315, 914], [CX - 23, 295, 916], [CX + 23, 295, 916]], DARK)
    part.box([CX - 13, 299, 905], [CX + 13, 312, 908], RED)
    part.box([CX - 3, 302, 903], [CX + 3, 312, 904], GOLD)
    for side in (-1, 1):
        part.box([CX + side * 21 - 3, 296, 881], [CX + side * 21 + 3, 304, 909], DARK)
        part.box([CX + side * 21 - 3, 305, 881], [CX + side * 21 + 3, 306, 908], GILDED)
        rod(part, [CX + side * 15, 309, 914], [CX + side * 26, 316, 916], 1.2, GOLD)
    part.box([CX - 13, 292, 872], [CX + 13, 294, 881], DARK)
    part.box([CX - 13, 295, 872], [CX + 13, 295, 881], GILDED)
    return part.finish()


def link_samples():
    x, y, z = np.meshgrid(np.arange(18) - 8.5, np.arange(-5, 6), np.arange(-1, 2), indexing='ij')
    distance = np.sqrt(np.maximum(abs(x) - 3.5, 0) ** 2 + y ** 2)
    keep = (distance - 4) ** 2 + z ** 2 <= 1.45 ** 2
    return np.c_[x[keep], y[keep], z[keep]], distance[keep] < 3.5


def chain(number, start, end, samples, sag, source, source_index):
    start, end = np.asarray(start, float), np.asarray(end, float)
    length = np.linalg.norm(end - start)
    count = math.ceil((length - 18) / 12) + 1
    spacing = (length - 18) / (count - 1)
    part = Part(f'soul_binding_chain_{number:02}', f'法则镇魂实体巨链{number:02}', section='chains',
                source=source, source_index=source_index, chain_links=count,
                start_blueprint_xyz=np.round(start, 3).tolist(),
                end_blueprint_xyz=np.round(end, 3).tolist(), anchor_radius=110,
                nominal_link_length=18, nominal_link_width=11, sampled_cross_section=[3, 3],
                center_spacing=float(spacing), sag_y=sag, alternating_link_planes=True)
    local, inner = samples
    for index in range(count):
        t = (9 + index * spacing) / length
        center = start * (1 - t) + end * t + [0, -sag * math.sin(math.pi * t), 0]
        axis = end - start + [0, -sag * math.pi * math.cos(math.pi * t), 0]
        axis /= np.linalg.norm(axis)
        side = np.cross(axis, [0, 1, 0])
        side /= np.linalg.norm(side)
        normal = np.cross(axis, side)
        across, thickness = (side, normal) if index % 2 == 0 else (normal, -side)
        q = center + local[:, :1] * axis + local[:, 1:2] * across + local[:, 2:] * thickness
        part.points(q[~inner], DARK)
        part.points(q[inner], RED)
    for point in (start, end):
        part.sphere(point, 4.2, GILDED, inner=2.4)
    return part.finish()


def build():
    parts, starts = [], []
    heights = [176, 204, 151, 220, 166, 193, 140, 211]
    for index, ((x, z), height) in enumerate(zip(PEAKS, heights)):
        heading = index * math.pi / 4 + math.pi
        origin = np.array([x, 46, z])
        inward = np.array([math.cos(heading), 0, math.sin(heading)])
        across = np.array([-inward[2], 0, inward[0]])
        part = Part(f'faceted_mechanical_peak_{index + 1}', f'黑金切面机械太虚山{index + 1}',
                    section='mountains', peak_index=index + 1, mountain_height=height,
                    mountain_bottom_y=46, mountain_top_y=46 + height,
                    base_center_blueprint_xyz=origin.tolist(), column_angles_degrees=[75, 60, 75])
        top = column(part, origin, height, 75, heading, 34, 31)
        column(part, origin + across * 29 - inward * 11, round(height * .72), 60,
               heading - .2, 20, 23)
        column(part, origin - across * 31 - inward * 7, round(height * .59), 75,
               heading + .35, 23, 20)
        for j, scale in enumerate((.34, .53, .69)):
            center = origin + inward * (height * scale / math.tan(math.radians(75)) + 22)
            center[1] += height * scale
            tip = center + inward * (17 + 3 * j) + across * (9 * (-1) ** j) + [0, 28, 0]
            u, v = across * 8, inward * 6
            part.hull([center - u - v, center - u + v, center + u - v,
                       center + u + v, tip], CRIMSON)
            rod(part, center, tip, 1.2, HOT)
        parts.extend([part.finish(), waterfalls(index, origin, height, heading), pavilion(index, top, heading)])
        for j in range(3):
            t = .66 + .09 * j
            start = origin + inward * (height * t / math.tan(math.radians(75)) + 18)
            start += across * (j - 1) * 16
            start[1] += height * t
            angle = index * math.pi / 4 + (j - 1) * .16
            direction = np.array([math.cos(angle), (j - 1) * .28, math.sin(angle)])
            end = CENTER + direction / np.linalg.norm(direction) * 110
            starts.append((start, end, 13 + index % 3 * 4, 'mountain', index + 1))
    parts.extend([fan(), throne()])
    box_mounts = [(-52, 174), (-52, 204), (-30, 232), (-10, 237),
                  (10, 237), (30, 232), (52, 204), (52, 174)]
    for index, (dx, y) in enumerate(box_mounts):
        start = np.array([CX + dx, y, 804])
        angle = math.pi / 2 + (index - 3.5) * .15
        direction = np.array([math.cos(angle), .32 if index % 2 else -.32, math.sin(angle)])
        end = CENTER + direction / np.linalg.norm(direction) * 110
        starts.append((start, end, 16 + index % 3 * 3, 'blade_box', index + 1))
    samples = link_samples()
    for number, (start, end, sag, source, index) in enumerate(starts, 1):
        parts.append(chain(number, start, end, samples, sag, source, index))
    notes = [
        '八峰底面统一Y46；山体高度依次176、204、151、220、166、193、140、211格，峰顶Y222、250、197、266、212、239、186、257。山巅剑亭另向上完整延伸。',
        '机械山以75度主柱、60度侧柱和75度副柱取样，角度相对水平面；玄玉幕墙、黑金切面与赤红晶簇均为真实整数格。',
        '每峰一红一白两道实体方块飞瀑，白金瀑布以白色主体和金边构成；半山排口取山高58%，下端延伸至原案墨海表层Y5，排口位置为本稿几何取样。',
        '折扇采用宽450、高130的半椭圆边界，底Y187、顶Y317，18根扇骨内嵌扇面，山河图与星图电路均由像素方块拼出。御座座面取(487,295,900)。',
        '32条巨链分为每峰3条共24条与剑匣8条；终端位于距核心(487,220,500)110格的球面锚区。每条metadata保存起终点、垂度与来源。',
        '原文同时指定18×11格链环与7×7格截面；7格杆体会封堵11格宽链环的交扣孔。本稿保留18×11名义轮廓，取约3×3格杆体并逐环翻转90度；旋转后的整数格包围盒受方块取整影响。',
        '剑匣挂点取正面Z804，上部Y232至237、侧部X435与539及Y174至204；这些挂点与悬链垂度均为原案未给出的几何取样。',
        '本稿保留山体、天幕、锁链与其他构件的原案交叠；未为核心、武器或名义包围盒裁切任何构件。',
    ]
    return parts, notes
