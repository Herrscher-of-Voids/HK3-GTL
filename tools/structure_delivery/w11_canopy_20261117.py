import math

import numpy as np

from w11_common_20261117 import Part, rod, line, BLACK, STUDS, WHITE, GOLD, RED, LIGHT, GRAY


def build_canopy():
    parts = []
    z, x = np.mgrid[-500:500, -500:500]
    r = np.hypot(x + .5, z + .5)
    angle = np.mod(np.arctan2(z + .5, x + .5), 2 * math.pi)
    for sector in range(16):
        p = Part(f'canopy_ring_{sector}', f'天幕外环分段 {sector + 1}', group='canopy')
        mask = (r <= 500) & (r >= 478) & (angle >= sector * math.pi / 8) & (angle < (sector + 1) * math.pi / 8)
        xx, zz, rr = x[mask], z[mask], r[mask]
        for y in range(261, 311):
            shell = np.ones(len(rr), bool) if y in (261, 262, 263, 307, 308, 309, 310) else (rr < 481) | (rr > 497)
            p.points(np.c_[xx[shell], np.full(shell.sum(), y), zz[shell]], GOLD if y in (264, 305) else STUDS if y % 8 == 0 else BLACK)
        for radius, y, state in ((482, 310, GOLD), (491, 310, LIGHT), (498, 308, GOLD), (478, 285, WHITE)):
            chosen = np.abs(rr - radius) < 1
            p.points(np.c_[xx[chosen], np.full(chosen.sum(), y), zz[chosen]], state)
        for a in np.linspace(sector * math.pi / 8, (sector + 1) * math.pi / 8, 4):
            v = np.array([math.cos(a), 0, math.sin(a)])
            q = np.array([-.5, 0, -.5])
            rod(p, q + v * 480 + [0, 265, 0], q + v * 497 + [0, 304, 0], 1.8, GRAY)
            rod(p, q + v * 497 + [0, 265, 0], q + v * 480 + [0, 304, 0], 1.8, GOLD)
        parts.append(p.finish())
    for axis in (0, 2):
        for segment, start in enumerate(range(-500, 500, 100)):
            p = Part(f'cross_{axis}_{segment}', f'十字控制架 {"东西" if axis == 0 else "南北"} {segment + 1}', group='canopy')
            def box(a, b, state):
                lo, hi = [0, a[1], 0], [0, b[1], 0]
                lo[axis], hi[axis] = a[0], b[0]
                lo[2 - axis], hi[2 - axis] = a[2], b[2]
                p.box(lo, hi, state)
            box([start, 261, -24], [start + 99, 264, 23], STUDS)
            box([start, 307, -24], [start + 99, 310, 23], BLACK)
            for side in (-24, 21):
                box([start, 265, side], [start + 99, 306, side + 2], BLACK)
                box([start, 268, side], [start + 99, 269, side + 2], GOLD)
                box([start, 302, side], [start + 99, 303, side + 2], GOLD)
                for t in (12, 36, 60, 84):
                    box([start + t, 275, side - (side > 0)], [start + t + 7, 296, side + 1], WHITE)
            for strip in (-18, 16):
                box([start, 310, strip], [start + 99, 310, strip + 1], LIGHT)
            box([start, 310, -4], [start + 99, 310, 3], RED)
            for t in (0, 48):
                a, b = np.array([start + t + 2, 266, -20.5]), np.array([start + t + 46, 305, 19.5])
                if axis == 2:
                    a, b = a[[2, 1, 0]], b[[2, 1, 0]]
                rod(p, a, b, 1.6, GOLD)
                reflected_a, reflected_b = a.copy(), b.copy()
                reflected_a[2 - axis] = -1 - a[2 - axis]
                reflected_b[2 - axis] = -1 - b[2 - axis]
                rod(p, reflected_a, reflected_b, 1.6, GRAY)
            parts.append(p.finish())
    p = Part('puppet_suspension', '中央机械手臂与舞台提线', group='strings')
    for angle in np.arange(8) * math.pi / 4:
        x, z = -.5 + 48 * math.cos(angle), -.5 + 48 * math.sin(angle)
        line(p, [x, 190, z], [x, 266, z], LIGHT)
        end = [x, 266, -.5] if abs(x + .5) > abs(z + .5) else [-.5, 266, z]
        line(p, [x, 266, z], end, GOLD)
    for x, y, z in ((-70, 252, 22), (69, 252, 22), (-70, 235, 22), (69, 235, 22), (-60, 207, 20), (59, 207, 20)):
        line(p, [x, y, z], [x, 263, z], RED)
        line(p, [x, 263, z], [x, 263, -.5], LIGHT)
    parts.append(p.finish())
    return parts
