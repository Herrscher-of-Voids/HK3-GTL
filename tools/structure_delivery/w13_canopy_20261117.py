import math

import numpy as np

from w13_common_20261117 import *


def build_canopy():
    parts = []
    for i in range(13):
        a = i * math.tau / 13 + math.pi / 26
        x, z = round(410 * math.cos(a)), round(-.5 + 365 * math.sin(a))
        bottom = 256 + round(2 * math.sin(3 * a))
        part = Part(f'obelisk_{i}', f'第{i + 1}座倒悬黑色机械碑', group='canopy', motion='obelisk', pivot=[x, bottom, z], axis=[0, 1, 0], index=i, speed=.18)
        for y in range(bottom, bottom + 70):
            k = y - bottom
            half = min(10, max(1, (k + 2) // 2))
            part.box((x - half, y, z - half), (x + half - 1, y, z + half - 1), BLACK if k % 16 > 2 else STUDS)
        part.box((x - 6, bottom + 24, z - 6), (x + 5, bottom + 65, z + 5), VOID)
        for dx, dz in [(-10, -3), (9, 2), (-3, 9), (2, -10)]:
            for j in range(5):
                y = bottom + 25 + j * 7
                part.box((x + dx, y, z + dz), (x + dx + (dx not in (-10, 9)) * 2, y + 2 + j % 2, z + dz + (dz not in (-10, 9)) * 2), PINK_LIGHT if j % 2 else MAGENTA)
        prism(part, (x, bottom + 24, z), (x, bottom, z), 6, PINK_GLASS, sides=4, tip=0)
        rod(part, (x, bottom + 18, z), (x, bottom + 3, z), 1, MAGENTA_LIGHT)
        part.box((x - 10, bottom + 66, z - 10), (x + 9, bottom + 69, z + 9), GRAY)
        parts.append(part.finish())
    net = Part('fractured_honeycomb', '900×850范围内的残缺六边天幕', group='canopy', canopy_grid=True)
    rain = []
    used_edges, nodes = set(), set()
    side = 55
    for col in range(-6, 7):
        for row in range(-5, 6):
            center = np.array([col * side * 1.5, 324 + (col + row) % 3 * 3, -.5 + (row + .5 * (col & 1)) * math.sqrt(3) * side])
            points = [center + [side * math.cos(a), 0, side * math.sin(a)] for a in np.arange(6) * math.tau / 6]
            if max(abs(p[0]) for p in points) > 450 or max(abs(p[2] + .5) for p in points) > 425:
                continue
            if (col * 13 + row * 7) % 11 in (1, 2):
                continue
            for j, (a, b) in enumerate(zip(points, points[1:] + points[:1])):
                key = tuple(sorted((tuple(np.rint(a[[0, 2]]).astype(int)), tuple(np.rint(b[[0, 2]]).astype(int)))))
                if key in used_edges:
                    continue
                used_edges.add(key)
                if (col * 7 + row * 3 + j) % 13 == 0:
                    line(net, a, a * .72 + b * .28, BLACK)
                    line(net, a * .26 + b * .74, b, BLACK)
                else:
                    rod(net, a, b, 1.4, BLACK)
                    line(net, a + [0, -1, 0], b + [0, -1, 0], PINK_LIGHT if j % 3 == 0 else MAGENTA_GLASS)
                for point in (a, b):
                    key = tuple(np.rint(point).astype(int))
                    nodes.add(key)
    for i, top in enumerate(sorted(nodes)):
        if i % 3 == 0:
            continue
        length = 20 + (i * 17) % 61
        line(net, top, np.array(top) - [0, length - 1, 0], PINK_LIGHT if i % 5 == 0 else PINK_GLASS)
        rain.append(dict(top=list(map(int, top)), length=length))
    parts.append(net.finish())
    return parts, rain
