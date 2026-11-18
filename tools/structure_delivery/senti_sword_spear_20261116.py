# -*- coding: utf-8 -*-
import math


def polygon(points):
    xs, ys = zip(*points)
    result = []
    for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
        for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
            inside = False
            for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
                if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                    inside = not inside
            if inside:
                result.append((x, y))
    return result


def plate(voxels, points, depth, material):
    for x, y in polygon(points):
        for z in range(-depth, depth + 1):
            voxels[x, y, z] = material


def surface(voxels, points, material):
    for x, y in points:
        columns = [z for z in range(-9, 10) if (x, y, z) in voxels]
        if columns:
            voxels[x, y, max(columns)] = material
            voxels[x, y, min(columns)] = material


def stroke(points, width=1):
    result = set()
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        distance = math.hypot(bx - ax, by - ay)
        for i in range(math.ceil(distance * 3) + 1):
            t = i / max(1, math.ceil(distance * 3))
            px, py = round(ax + (bx - ax) * t), round(ay + (by - ay) * t)
            for dx in range(-width + 1, width):
                for dy in range(-width + 1, width):
                    result.add((px + dx, py + dy))
    return result


def round_shaft(voxels, bottom, top, radius, material):
    for y in range(bottom, top + 1):
        r = radius(y)
        for x in range(-math.ceil(r), math.ceil(r) + 1):
            for z in range(-math.ceil(r), math.ceil(r) + 1):
                if x * x + z * z <= r * r:
                    voxels[x, y, z] = material(x, y, z)


def sword():
    voxels = {}
    blade = [(-.4, 0), (-4, 9), (-8, 28), (-10, 63), (-10, 204), (-8, 218),
             (8, 218), (10, 204), (10, 63), (8, 28), (4, 9), (.4, 0)]
    for x, y in polygon(blade):
        half_width = min(10, .7 + y * .28)
        depth = max(1, round(3.1 * (1 - abs(x) / (half_width + 1))))
        for z in range(-depth, depth + 1):
            material = 5 if abs(z) == depth else 6
            if abs(x) > half_width - 1.8:
                material = 6
            if y > 189 + abs(x) * 1.6:
                material = 9
            voxels[x, y, z] = material
    engrave = [(0, 24), (-1, 44), (2, 56), (2, 77), (-2, 86), (-2, 103),
               (2, 113), (2, 137), (-2, 148), (-2, 164), (2, 178), (1, 193)]
    surface(voxels, stroke(engrave), 8)
    for y in [63, 108, 156, 185]:
        surface(voxels, stroke([(0, y - 6), (-4, y), (0, y + 5), (4, y), (0, y - 6)]), 8)
    plate(voxels, [(-10, 213), (-20, 209), (-30, 207), (-26, 214), (-18, 218),
                    (-13, 225), (-16, 232), (-24, 236), (-27, 243), (-23, 250),
                    (-13, 255), (-16, 246), (-10, 240), (0, 242), (11, 237),
                    (19, 239), (25, 245), (27, 251), (27, 240), (22, 233),
                    (15, 229), (12, 220), (5, 217)], 4, 3)
    plate(voxels, [(-12, 217), (-18, 213), (-25, 213), (-19, 216), (-13, 221),
                    (-9, 228), (-5, 229), (-6, 220)], 5, 3)
    center_y = 232
    for x in range(-17, 18):
        for y in range(215, 250):
            r = math.hypot(x, y - center_y)
            if r <= 16:
                for z in range(-5, 6):
                    voxels[x, y, z] = 3
                if 12.5 < r < 14:
                    voxels[x, y, 5] = voxels[x, y, -5] = 4
    for x in range(-12, 13):
        for y in range(220, 245):
            r = math.hypot(x, y - center_y)
            angle = math.atan2(y - center_y, x)
            if r < 7.3 + 3.5 * math.cos(3 * angle + .19 * r):
                voxels[x, y, 5] = voxels[x, y, -5] = 9
    filigree = [(-22, 242), (-18, 246), (-12, 245), (-8, 241), (-7, 234),
                (-10, 227), (-8, 220), (-2, 217), (6, 220), (9, 226),
                (16, 231), (22, 235), (24, 243)]
    surface(voxels, stroke(filigree), 8)
    for x in range(-11, 12):
        for y in range(219, 246):
            r = math.hypot(x, y - center_y)
            if 11.2 < r < 12.2:
                voxels[x, y, 6] = voxels[x, y, -6] = 3

    def grip_material(x, y, z):
        phase = (math.atan2(z, x) / (2 * math.pi) - (y - 249) / 19) % 1
        cross = (math.atan2(z, x) / (2 * math.pi) + (y - 249) / 19) % 1
        return 3 if phase < .25 else 8 if cross < .055 else 5

    round_shaft(voxels, 247, 310, lambda y: 4.5, grip_material)
    round_shaft(voxels, 247, 251, lambda y: 5.2, lambda x, y, z: 3)
    round_shaft(voxels, 309, 319, lambda y: 5.2 if y < 316 else 5.2 - (y - 316) * .65,
                lambda x, y, z: 8 if y in (309, 310, 316) else 3)
    round_shaft(voxels, 320, 323, lambda y: 2.9 - (y - 320) * .65, lambda x, y, z: 3)
    return dict(id='sword', title='宝剑 · 言多必弑', voxels=voxels,
                features=['细长双刃与阶梯收尖，红刃、暗红侧缘和暖黑刃根。',
                          '骨白流卷护手、哑光金窄饰线与灰黑三瓣纹圆盘。',
                          '圆截面红柄，宽白斜缠带、细金交叉线与骨白柄尾。',
                          '双面细纹及五至七格刃脊厚度按画面转译。'],
                references=['R14', 'R15', 'R18', 'R19', 'R20', 'R21'],
                views=dict(guard=dict(target=[0, 232, 0], radius=41),
                           grip=dict(target=[0, 285, 0], radius=43),
                           blade=dict(target=[0, 120, 0], radius=100)))


def spear():
    voxels = {}

    def shaft_material(x, y, z):
        angle = math.atan2(z, x) / (2 * math.pi)
        phase = (angle - y / 21) % 1
        cross = (angle + y / 21) % 1
        dark_band = (y < 98 and phase < .71) or (y > 263 and phase < .76)
        return 1 if dark_band else 8 if phase < .06 or cross < .06 else 5

    round_shaft(voxels, 51, 294, lambda y: 3.4, shaft_material)
    for y0, y1 in [(58, 65), (88, 93), (265, 270), (287, 294)]:
        round_shaft(voxels, y0, y1, lambda y: 3.8,
                    lambda x, y, z: 1 if (y - y0) % 6 < 3 else 9)
    head = [(0, 0), (-3, 10), (-5, 21), (-11, 29), (-14, 38),
            (-11, 43), (-7, 44), (-6, 52), (-3, 59), (3, 59),
            (6, 52), (7, 44), (11, 43), (14, 38), (11, 29),
            (5, 21), (3, 10)]
    for x, y in polygon(head):
        depth = max(1, round(3 * min(1, y / 18) * (1 - abs(x) / 15)))
        for z in range(-depth, depth + 1):
            voxels[x, y, z] = 3
    surface(voxels, stroke([(0, 8), (0, 31)]), 4)
    surface(voxels, stroke([(-9, 37), (-5, 34), (0, 35), (4, 39),
                            (1, 43), (-3, 43), (-5, 39), (-2, 35), (3, 34), (9, 37)]), 9)
    surface(voxels, stroke([(-6, 48), (0, 43), (6, 48)]), 5)
    surface(voxels, stroke([(0, 2), (0, 28)]), 3)
    round_shaft(voxels, 291, 328, lambda y: 4.6 if y < 322 else 4.6 - (y - 322) * .17,
                lambda x, y, z: 4 if abs(x) > 3 else 3)
    round_shaft(voxels, 329, 337, lambda y: 4.3 - (y - 329) * .48,
                lambda x, y, z: 8 if y < 331 else 3)
    surface(voxels, stroke([(-2, 294), (-1, 306), (-3, 319), (0, 329)]), 8)
    voxels = {(round(x * .72) if y < 60 else x, y, z): material
              for (x, y, z), material in voxels.items()}
    return dict(id='spear', title='长枪 · 有话直槊', voxels=voxels,
                features=['细长红黑圆杆，端部黑色缠带与杆上细金交叉纹。',
                          '一端骨白套帽并逐格收尖，另一端骨白菱形枪头与红色饰纹。',
                          '枪头的灰脊与卷折纹依官方侧面与全长画面转译，刃缘阶梯收薄。',
                          '主体保持细长比例，圆杆七格直径，套帽九格直径。'],
                references=['R22', 'R23', 'R24', 'R25', 'R26', 'R27', 'R28', 'R29'],
                views=dict(head=dict(target=[0, 29, 0], radius=38),
                           shaft=dict(target=[0, 178, 0], radius=54),
                           cap=dict(target=[0, 313, 0], radius=32)))


def build():
    return [sword(), spear()]
