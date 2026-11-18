import math

import numpy as np

from w11_common_20261117 import Part, rod, line, BLACK, STUDS, WHITE, GOLD, RED, LIGHT, GLASS, GRAY, HK


def build_foundation():
    parts = []
    z, x = np.mgrid[-301:301, -301:301]
    r = np.hypot(x + .5, z + .5)
    angle = np.mod(np.arctan2(z + .5, x + .5), 2 * math.pi)
    floor = np.floor(44 * (r / 300) ** 1.45).astype(int)
    for sector in range(8):
        p = Part(f'well_{sector}', f'深渊冷却井 {sector + 1}', group='foundation')
        mask = (r <= 300) & (angle >= sector * math.pi / 4) & (angle < (sector + 1) * math.pi / 4)
        xx, zz, yy, rr = x[mask], z[mask], floor[mask], r[mask]
        for dy in range(3):
            p.points(np.c_[xx, np.maximum(0, yy - dy), zz], BLACK if dy else STUDS)
        bands = (rr > 30) & (np.mod(rr, 19) < 2)
        p.points(np.c_[xx[bands], yy[bands] + 1, zz[bands]], LIGHT)
        liquid = (rr < 278) & (np.mod(rr, 19) > 3) & (np.mod(rr, 19) < 10)
        p.points(np.c_[xx[liquid], yy[liquid] + 1, zz[liquid]], GLASS)
        spine = (np.abs(np.sin(8 * angle[mask])) < .018) & (rr > 35)
        p.points(np.c_[xx[spine], yy[spine] + 2, zz[spine]], GOLD)
        parts.append(p.finish())
    for i, (a, b) in enumerate([(a, b) for a, b in ((369, 153), (153, 369)) for a in (a, -a) for b in (b, -b)]):
        cx, cz = a - .5, b - .5
        p = Part(f'foundation_{i}', f'八向梯形工业基座 {i + 1}', group='foundation', footprint=[150, 150], height=45)
        for y in range(45):
            inset = y // 4
            lo = [int(cx - 74.5 + inset), y, int(cz - 74.5 + inset)]
            hi = [int(cx + 74.5 - inset), y, int(cz + 74.5 - inset)]
            material = GOLD if y in (7, 23, 40) else STUDS if y % 4 == 0 else BLACK
            if y < 4 or y >= 42:
                p.box(lo, hi, material)
            else:
                p.box(lo, [hi[0], y, lo[2] + 2], material)
                p.box([lo[0], y, hi[2] - 2], hi, material)
                p.box(lo, [lo[0] + 2, y, hi[2]], material)
                p.box([hi[0] - 2, y, lo[2]], hi, material)
        for dx in range(-46, 47, 23):
            for dz in (-33, 33):
                p.box([cx + dx - 6, 44, cz + dz - 12], [cx + dx + 6, 46, cz + dz + 12], GRAY)
                p.box([cx + dx - 4, 47, cz + dz - 10], [cx + dx + 4, 47, cz + dz + 10], HK)
                for strip in (-7, 0, 7):
                    p.box([cx + dx - 4, 48, cz + dz + strip], [cx + dx + 4, 48, cz + dz + strip], GOLD)
        for dx in (-24, 24):
            for dz in (-24, 24):
                foot = np.array([cx + dx, 45, cz + dz])
                elbow = np.array([cx + dx * .75, 69, cz + dz * .75])
                tip = np.array([cx + dx * .35, 82, cz + dz * .35])
                rod(p, foot, elbow, 3.1, GRAY)
                rod(p, elbow, tip, 2.1, GOLD)
                p.sphere(elbow, 4, WHITE)
                rod(p, tip, tip + [0, 5, 0], 2, STUDS)
                up = tip + [0, 98, 0]
                radial = np.array([tip[0] + .5, 0, tip[2] + .5])
                radial /= np.linalg.norm(radial)
                roof = np.array([-.5, 264, -.5]) + radial * 486
                line(p, tip, up, LIGHT)
                line(p, up, roof, LIGHT)
        for dx in (-53, 53):
            p.box([cx + dx - 2, 45, cz - 47], [cx + dx + 2, 46, cz + 47], RED)
        parts.append(p.finish())
    return parts
