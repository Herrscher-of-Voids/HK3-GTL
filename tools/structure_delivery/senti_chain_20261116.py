# -*- coding: utf-8 -*-
import math


def polygon(points, x, y):
    inside = False
    for a, b in zip(points, points[1:] + points[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def extrude(voxels, points, half_depth, material):
    for x in range(math.floor(min(p[0] for p in points)), math.ceil(max(p[0] for p in points)) + 1):
        for y in range(math.floor(min(p[1] for p in points)), math.ceil(max(p[1] for p in points)) + 1):
            if polygon(points, x + .5, y + .5):
                for z in range(-half_depth, half_depth + 1):
                    voxels[x, y, z] = material


def rod(voxels, start, end, radius, material):
    delta = [b - a for a, b in zip(start, end)]
    length2 = sum(v * v for v in delta)
    for x in range(math.floor(min(start[0], end[0]) - radius), math.ceil(max(start[0], end[0]) + radius) + 1):
        for y in range(math.floor(min(start[1], end[1]) - radius), math.ceil(max(start[1], end[1]) + radius) + 1):
            for z in range(math.floor(min(start[2], end[2]) - radius), math.ceil(max(start[2], end[2]) + radius) + 1):
                p = (x, y, z)
                t = max(0, min(1, sum((p[i] - start[i]) * delta[i] for i in range(3)) / length2))
                if sum((p[i] - start[i] - t * delta[i]) ** 2 for i in range(3)) <= radius * radius:
                    voxels[p] = material


def baton():
    v = {}
    for y in range(129):
        if y < 8:
            radius = 3.5 if y > 1 else 2.5
        elif y < 59:
            radius = 7.2
        elif y < 68:
            radius = 9
        elif y < 119:
            radius = 7.5
        elif y < 124:
            radius = 8.5
        else:
            radius = 7.2 - (y - 124) * .7
        for x in range(-math.ceil(radius), math.ceil(radius) + 1):
            for z in range(-math.ceil(radius), math.ceil(radius) + 1):
                if x * x + z * z <= radius * radius:
                    material = 1
                    if y < 8:
                        material = 5 if z >= 0 else 6
                    elif y < 59:
                        material = 2 if abs(x) > 4 else 9
                    elif y in range(60, 64):
                        material = 4
                    elif y in range(119, 122):
                        material = 2
                    elif y >= 124:
                        material = 3
                    v[x, y, z] = material
    left = [(-5, 11), (-10, 19), (-13, 53), (-10, 64), (-9, 40), (-5, 25)]
    right = [(5, 11), (10, 19), (14, 57), (10, 69), (9, 41), (5, 25)]
    for blade in (left, right):
        extrude(v, blade, 4, 2)
        center = sum(p[0] for p in blade) / len(blade)
        inset = [(center + (x - center) * .83, y) for x, y in blade]
        extrude(v, inset, 5, 3)
    for y in range(12, 47):
        width = 2 if y < 34 else 1
        for x in range(-width, width + 1):
            v[x, y, 7] = 5
            v[x, y, -7] = 6
    for y in range(23, 43):
        x = round(2 * math.sin((y - 23) * math.pi / 19))
        v[x, y, 8] = 3
        v[x + 1, y, 8] = 3
    for sign in (-1, 1):
        for y in range(72, 116):
            for x in range(-3, 4):
                z = sign * round(math.sqrt(7.5 ** 2 - x * x))
                v[x, y, z] = 6 if x < -1 else 1
            for x in range(4, 7):
                z = sign * round(math.sqrt(7.5 ** 2 - x * x))
                if (y - 72) // 14 % 2 == 0 and y % 14 > (x - 4) * 2:
                    v[x, y, z] = 2
    for y in (69, 117):
        for x in range(-7, 8):
            for z in range(-7, 8):
                if 37 <= x * x + z * z <= 58:
                    v[x, y, z] = 4
    return v


def curve(t):
    return (-22 + 46 * t + 26 * math.sin(math.pi * t), 134 + 99 * t, 9 * math.sin(2 * math.pi * t))


def chain_link(voxels, t, index):
    center = curve(t)
    tangent = (46 + 26 * math.pi * math.cos(math.pi * t), 99, 18 * math.pi * math.cos(2 * math.pi * t))
    norm = math.sqrt(sum(x * x for x in tangent))
    axis = tuple(x / norm for x in tangent)
    side = (-axis[1], axis[0], 0)
    length = math.hypot(side[0], side[1])
    side = tuple(x / length for x in side)
    depth = (axis[1] * side[2] - axis[2] * side[1], axis[2] * side[0] - axis[0] * side[2], axis[0] * side[1] - axis[1] * side[0])
    radial = side if index % 2 == 0 else depth
    points = []
    for i in range(49):
        angle = i * 2 * math.pi / 48
        along, across = 7.3 * math.cos(angle), 1.8 * math.sin(angle)
        points.append(tuple(center[k] + along * axis[k] + across * radial[k] for k in range(3)))
    for a, b in zip(points, points[1:]):
        rod(voxels, a, b, .7, 2)
    if index % 3 == 1:
        a = tuple(center[k] - 3.2 * axis[k] for k in range(3))
        b = tuple(center[k] + 3.2 * axis[k] for k in range(3))
        rod(voxels, a, b, 1.6, 2)


def build():
    voxels = {}
    body = baton()
    for (x, y, z), material in body.items():
        voxels[x - 22, y, z] = material
        voxels[24 - x, 367 - y, -z] = material
    rod(voxels, (-22, 127, 0), (-22, 136, 0), 2, 2)
    rod(voxels, (24, 231, 0), (24, 240, 0), 2, 2)
    for i in range(14):
        chain_link(voxels, i / 13, i)
    points = [curve(i / 80) for i in range(81)]
    for a, b in zip(points, points[1:]):
        rod(voxels, a, b, .7, 6)
    return [dict(
        id='chain', title='链刃 · 双端杆刃与柔性连接', voxels=voxels,
        features=[
            '双端各129格，圆截面黑色握筒、暗红纵纹及骨白端盖。',
            '末端保留短钝红色接头与两侧不等长骨白分叉，侧刃收窄并向内回折。',
            '14枚细长交扣链节与细暗红内线连接双端，间隔暗色套节；静态舒展弯链用于观察。',
            '攻击残影与大片红色斩击光效不进入实体模型。',
        ],
        references=['R30', 'R33', 'R34', 'R35', 'R38', 'R39'],
        views={
            'chain': dict(target=[7, 183, 0], radius=205),
            'chain_tip': dict(target=[-22, 38, 0], radius=61),
            'chain_links': dict(target=[27, 183, 0], radius=70),
            'chain_grip': dict(target=[-22, 95, 0], radius=45),
        },
    )]
