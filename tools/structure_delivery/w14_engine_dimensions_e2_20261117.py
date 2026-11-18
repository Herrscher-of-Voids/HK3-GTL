import numpy as np
from scipy.ndimage import binary_erosion

from w14_engine_common_e2_20261117 import (
    Part, BLACK, BLUE_LIGHT, PURPLE_LIGHT, STONE, MOSS, DIRT, LOG_BLOCK,
    LEAVES, MAGMA, OBSIDIAN, WATER, AMETHYST, END_STONE, LIGHT, YELLOW,
    GREEN_LIGHT, RED_LIGHT, NETHERRACK, LAVA, BASALT, RED_SAND,
    RED_TERRACOTTA, YELLOW_TERRACOTTA, ORANGE_TERRACOTTA, CALCITE,
    radial,
)
from w14_engine_bubbles_20261117 import enclosure, feed


DIMENSIONS = [
    ('overworld', '主世界', 812, 176, 88, GREEN_LIGHT),
    ('end', '末地', 802, 160, 92, PURPLE_LIGHT),
    ('nether', '地狱', 820, 189, 86, RED_LIGHT),
    ('moon', '月球', 810, 154, 80, BLUE_LIGHT),
    ('mars', '火星', 800, 220, 90, RED_LIGHT),
    ('venus', '金星', 816, 202, 82, YELLOW),
    ('galaxy', '银河系', 808, 184, 85, PURPLE_LIGHT),
]
MOON_ORB_CRATERS = [(-23, 6, 20, 13), (25, -24, 14, 9), (28, 29, 11, 7)]
MOON_SECTOR_CRATERS = [(405, 0, 72, 17), (535, 85, 42, 12), (535, -105, 33, 10), (290, 0, 25, 7)]


def crater(x, z, cx, cz, radius, depth):
    distance = np.sqrt((x - cx) ** 2 + (z - cz) ** 2) / radius
    return depth * (.47 * np.exp(-((distance - 1) / .18) ** 2) - np.exp(-(distance / .75) ** 4))


def moon_surface(states, surface, x, z, craters):
    for cx, cz, radius, depth in craters:
        distance = np.sqrt((x - cx) ** 2 + (z - cz) ** 2) / radius
        states[(surface < 1.5) & (distance > .96) & (distance < 1.05)] = CALCITE
        states[(surface < 1.5) & (distance < .45)] = BASALT


def cloud_cluster(part, center, length, width, thickness, angle=0):
    for dx, dz, sx, sz, lift in [(-.37, -.12, .65, .75, 0), (.31, .22, .70, .87, .35), (.02, -.34, .57, .64, -.2)]:
        cx = center[0] + length * dx * np.cos(angle) - width * dz * np.sin(angle)
        cz = center[2] + length * dx * np.sin(angle) + width * dz * np.cos(angle)
        cy = center[1] + thickness * lift
        extent = int(np.ceil(max(length * sx, width * sz)))
        z, x = np.mgrid[-extent:extent + 1, -extent:extent + 1]
        u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
        for y in range(-thickness, thickness + 1):
            mask = (u / (length * sx)) ** 2 + (v / (width * sz)) ** 2 + (y / thickness) ** 2 <= 1
            part.points(np.c_[x[mask] + cx, np.full(mask.sum(), cy + y), z[mask] + cz], CALCITE if y > -.6 * thickness else YELLOW_TERRACOTTA)


def orb_height(kind, x, z, radius):
    r = radius
    if kind == 'overworld':
        return -.28 * r + 8 * np.sin(x / 21) * np.cos(z / 26) + 11 * np.exp(-((x + 22) ** 2 + (z - 18) ** 2) / (r * .45) ** 2)
    if kind == 'end':
        return -.27 * r + 5 * np.sin(x / 19) * np.cos(z / 23)
    if kind == 'nether':
        return -.30 * r + 12 * np.sin(x / 18) * np.cos(z / 24) + 10 * np.sin((x + z) / 31) ** 4
    if kind == 'moon':
        return -.24 * r + 2 * np.sin(x / 24) + sum(crater(x, z, *item) for item in MOON_ORB_CRATERS)
    if kind == 'mars':
        return -.25 * r + 7 * np.sin((x + .35 * z) / 21) + 4 * np.cos(z / 31) + crater(x, z, -27, 15, 19, 9) + crater(x, z, 22, -27, 13, 7)
    return -.29 * r + 11 * np.sin((x + .7 * z) / 15) + 6 * np.cos((z - x) / 23)


def orb_ground(part, center, radius, kind):
    r = radius
    z, x = np.mgrid[-r:r + 1, -r:r + 1]
    distance2 = x * x + z * z
    top = orb_height(kind, x, z, r)
    for y in range(-r + 5, int(np.ceil(top.max())) + 1):
        mask = (distance2 + y * y <= (r - 5) ** 2) & (y <= top)
        surface = top[mask] - y
        xx, zz = x[mask], z[mask]
        states = np.full(mask.sum(), STONE, np.uint8)
        if kind == 'overworld':
            states[surface < 7] = DIRT
            states[surface < 2] = MOSS
        elif kind == 'end':
            states[:] = END_STONE
        elif kind == 'nether':
            states[:] = NETHERRACK
            states[(surface < 3) & (np.sin(xx / 9) + np.cos(zz / 12) > 1.2)] = BASALT
            states[(surface < 2) & (abs(zz - 8 * np.sin(xx / 14)) < 3)] = MAGMA
        elif kind == 'moon':
            moon_surface(states, surface, xx, zz, MOON_ORB_CRATERS)
        elif kind == 'mars':
            states[:] = RED_TERRACOTTA
            states[surface < 3] = RED_SAND
            states[(surface < 2) & (np.sin(xx / 17) + np.cos(zz / 19) > 1.2)] = ORANGE_TERRACOTTA
        elif kind == 'venus':
            states[:] = ORANGE_TERRACOTTA
            states[surface < 3] = YELLOW_TERRACOTTA
        points = np.c_[xx, np.full(mask.sum(), y), zz] + center
        for state in np.unique(states):
            part.points(points[states == state], state)
    if kind == 'overworld':
        for y in range(int(-.40 * r), int(-.24 * r) + 1):
            river = abs(z - 9 * np.sin(x / 20)) < 8
            mask = (distance2 + y * y < (r - 7) ** 2) & river & (top < y)
            part.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]] + center, WATER)
    if kind == 'nether':
        for y in range(int(-.39 * r), int(-.32 * r) + 1):
            river = abs(z - 8 * np.sin(x / 14)) < 6
            mask = (distance2 + y * y < (r - 7) ** 2) & river & (top < y)
            part.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]] + center, LAVA)


def tree(part, foot, height, scale=1):
    x, y, z = foot
    trunk = max(1, int(2 * scale))
    part.box([x - trunk, y - 2, z - trunk], [x + trunk, y + height, z + trunk], LOG_BLOCK)
    for dx, dy, dz, radius in [(0, 3, 0, 13), (-8, 0, 0, 10), (8, 1, 1, 10), (0, -1, 8, 10), (0, 0, -8, 10)]:
        part.sphere([x + dx * scale, y + height + dy * scale, z + dz * scale], radius * scale, LEAVES)


def end_pillar(part, foot, width, height):
    x, y, z = foot
    part.box([x - width, y - 3, z - width], [x + width, y + height, z + width], OBSIDIAN)
    part.box([x - width - 2, y + height, z - width - 2], [x + width + 2, y + height + 2, z + width + 2], BASALT)
    center = np.array([x, y + height + 11, z])
    part.hull(center + np.array([[0, -9, 0], [-7, 0, 0], [7, 0, 0], [0, 0, -7], [0, 0, 7], [0, 9, 0]]), AMETHYST)
    part.sphere(center, 3, PURPLE_LIGHT)


def orb_decorations(part, center, radius, kind):
    r = radius
    if kind == 'overworld':
        for x, z, height in [(-35, -24, 22), (25, 27, 26), (-19, 33, 24), (33, -25, 23)]:
            tree(part, center + [x, int(orb_height(kind, x, z, r)), z], height, .75)
    elif kind == 'end':
        for x, z, height, width in [(-33, -15, 42, 5), (24, -26, 57, 6), (19, 29, 35, 4)]:
            end_pillar(part, center + [x, int(orb_height(kind, x, z, r)), z], width, height)
    elif kind == 'nether':
        for x, z, height, width in [(-35, -28, 35, 8), (31, -25, 45, 9), (33, 33, 29, 7), (-26, 35, 25, 6)]:
            y = int(orb_height(kind, x, z, r))
            part.hull(center + np.array([[x - width, y - 5, z - width], [x + width, y - 5, z - width], [x + width, y - 5, z + width], [x - width, y - 5, z + width], [x + 2, y + height, z - 2]]), BASALT)
    elif kind in ['moon', 'mars']:
        for x, z, radius in [(-42, -29, 5), (34, 23, 4), (-4, 35, 3), (39, -5, 5)]:
            y = int(orb_height(kind, x, z, r))
            part.sphere(center + [x, y + radius * .4, z], radius, STONE if kind == 'moon' else RED_TERRACOTTA)
    elif kind == 'venus':
        for x, z, height, length, width, thickness, angle in [(-37, -20, 29, 23, 9, 3, -.2), (8, -5, 42, 17, 10, 4, .35), (33, 25, 27, 22, 8, 3, -.35), (-25, 27, 47, 16, 11, 4, .1), (4, -39, 50, 16, 7, 3, -.15)]:
            cloud_cluster(part, center + [x, height, z], length, width, thickness, angle)


def galaxy_orb(part, center, radius):
    for arm in range(5):
        for r in np.arange(7, radius * .83, .8):
            angle = arm * 2 * np.pi / 5 + r / 22
            x, z = r * np.cos(angle), r * np.sin(angle)
            y = .42 * z
            width = 2 if r < 35 else 1
            part.box(center + [x - width, y - 1, z - width], center + [x + width, y + 1, z + width], PURPLE_LIGHT if arm % 2 else BLUE_LIGHT)
            if int(r * 2) % 9 < 2:
                part.sphere(center + [x, y + 2, z], 2, LIGHT)
    rng = np.random.default_rng(1407)
    phi, cosine = rng.uniform(0, 2 * np.pi, 180), rng.uniform(-1, 1, 180)
    rr = radius * rng.uniform(.15, .85, 180)
    stars = np.c_[rr * np.sqrt(1 - cosine ** 2) * np.cos(phi), rr * cosine, rr * np.sqrt(1 - cosine ** 2) * np.sin(phi)]
    for index, point in enumerate(stars):
        width = 1 if index % 11 else 2
        part.box(center + point - width, center + point + width, LIGHT if index % 4 else YELLOW)
    part.sphere(center, 10, BLUE_LIGHT)
    part.sphere(center, 7, LIGHT)
    part.sphere(center + [0, 1, 2], 4, YELLOW)


def sector_height(kind, u, v):
    if kind == 'overworld':
        hill = 26 * np.exp(-((u - 465) ** 2 + (v + 80) ** 2) / 95 ** 2) + 18 * np.exp(-((u - 355) ** 2 + (v - 42) ** 2) / 70 ** 2)
        river = np.exp(-((v - 32 * np.sin((u - 250) / 53)) / 15) ** 4)
        return np.maximum(8, 17 + hill + 4 * np.sin(u / 29) * np.cos(v / 32) - 15 * river)
    if kind == 'end':
        return 24 + 13 * np.sin(u / 57) * np.cos(v / 49) + 6 * np.sin((u + v) / 26)
    if kind == 'nether':
        ridge = 22 * np.abs(np.sin((u + .65 * v) / 44)) ** 5
        river = np.exp(-((v - 32 * np.sin(u / 47)) / 18) ** 4)
        return np.maximum(8, 22 + ridge + 5 * np.cos(v / 17) - 24 * river)
    if kind == 'moon':
        return 25 + 3 * np.sin(u / 39) + sum(crater(u, v, *item) for item in MOON_SECTOR_CRATERS)
    if kind == 'mars':
        return 25 + 8 * np.sin((u + .35 * v) / 35) + 8 * np.exp(-((u - 350) ** 2 + (v + 25) ** 2) / 80 ** 2) + crater(u, v, 465, 35, 65, 13) + crater(u, v, 560, -85, 28, 9)
    if kind == 'venus':
        return 29 + 16 * np.sin((u + .52 * v) / 30) + 8 * np.cos((v - .3 * u) / 27)
    return 8 + 2 * np.sin(u / 53) * np.cos(v / 47)


def sector_ground(part, kind, angle):
    z, x = np.mgrid[-590:591, -590:591]
    u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
    r2 = x * x + z * z
    mask = (r2 >= 225 ** 2) & (r2 <= 590 ** 2) & (u * np.sin(np.pi / 7) - abs(v) * np.cos(np.pi / 7) > 72)
    if kind == 'end':
        mask &= (np.sin(u / 37) * np.cos(v / 47) > -.73) | (abs(v) < 17)
    edge = mask & ~binary_erosion(mask, iterations=3)
    xx, zz, uu, vv, border = x[mask], z[mask], u[mask], v[mask], edge[mask]
    top = np.rint(sector_height(kind, uu, vv)).astype(int)
    for y in range(5, int(top.max()) + 1):
        keep = (y <= top) & ((y >= top - 5) | border | (y <= 6))
        surface = top[keep] - y
        pu, pv = uu[keep], vv[keep]
        states = np.full(keep.sum(), STONE, np.uint8)
        if kind == 'overworld':
            states[surface < 4] = DIRT
            states[surface < 1] = MOSS
        elif kind == 'end':
            states[:] = END_STONE
        elif kind == 'nether':
            states[:] = NETHERRACK
            states[(surface < 2) & (np.sin(pu / 19) * np.cos(pv / 21) > .45)] = BASALT
            states[(surface < 1) & (abs(pv - 32 * np.sin(pu / 47)) < 21)] = MAGMA
        elif kind == 'moon':
            moon_surface(states, surface, pu, pv, MOON_SECTOR_CRATERS)
        elif kind == 'mars':
            states[:] = RED_TERRACOTTA
            states[surface < 3] = RED_SAND
            states[(surface < 1) & (np.sin(pu / 29) + np.cos(pv / 31) > 1.15)] = ORANGE_TERRACOTTA
        elif kind == 'venus':
            states[:] = ORANGE_TERRACOTTA
            states[surface < 2] = YELLOW_TERRACOTTA
        else:
            states[:] = BLACK
        points = np.c_[xx[keep], np.full(keep.sum(), y), zz[keep]]
        for state in np.unique(states):
            part.points(points[states == state], state)
    if kind in ['overworld', 'nether']:
        waterline = 15 if kind == 'overworld' else 14
        river = abs(vv - 32 * np.sin((uu - 250) / 53 if kind == 'overworld' else uu / 47)) < (17 if kind == 'overworld' else 20)
        for y in range(9, waterline + 1):
            keep = river & (top < y)
            part.points(np.c_[xx[keep], np.full(keep.sum(), y), zz[keep]], WATER if kind == 'overworld' else LAVA)


def sector_decorations(part, kind, angle):
    def position(u, v, offset=0):
        return radial(u, int(sector_height(kind, u, v)) + offset, v, angle)

    if kind == 'overworld':
        for u, v, height in [(330, -32, 30), (330, 35, 35), (405, -80, 36), (405, 85, 39), (470, -110, 42), (470, 100, 37), (530, -115, 31), (530, 125, 33), (550, 60, 32)]:
            tree(part, position(u, v), height, 1.15)
    elif kind == 'end':
        for u, v, height, width in [(315, 0, 76, 10), (425, -78, 126, 14), (520, 95, 104, 12)]:
            end_pillar(part, position(u, v), width, height)
    elif kind == 'nether':
        for u, v, height, width in [(315, -30, 55, 12), (390, 77, 77, 16), (455, -109, 69, 15), (535, 120, 52, 13), (560, -100, 45, 11)]:
            foot = position(u, v)
            part.hull(foot + np.array([[-width, -3, -width], [width, -3, -width], [width, -3, width], [-width, -3, width], [2, height, -2]]), BASALT)
            part.box(foot + [-3, 1, -3], foot + [3, height - 8, 3], MAGMA)
    elif kind in ['moon', 'mars']:
        for u, v, radius in [(315, -30, 7), (365, 50, 9), (460, -105, 7), (520, 115, 6), (550, -50, 8), (565, 12, 5)]:
            part.sphere(position(u, v, radius * .4), radius, STONE if kind == 'moon' else RED_TERRACOTTA)
    elif kind == 'venus':
        for u, v, height, length, width, thickness, turn in [(330, 0, 83, 26, 11, 4, -.2), (390, -57, 91, 34, 17, 5, .25), (425, 62, 114, 42, 22, 7, -.35), (485, -95, 76, 31, 18, 5, .1), (520, 42, 95, 49, 24, 6, .3), (550, -30, 66, 20, 11, 4, -.4)]:
            cloud_cluster(part, radial(u, height, v, angle), length, width, thickness, angle + turn)
    else:
        for arm in range(5):
            for radius in np.arange(9, 146, 1):
                phase = arm * 2 * np.pi / 5 + radius / 42
                u, v = 420 + radius * np.cos(phase), radius * .66 * np.sin(phase)
                point = radial(u, 15 + 2 * np.sin(radius / 19), v, angle)
                part.box(point + [-2, -1, -2], point + [2, 1, 2], PURPLE_LIGHT if arm % 2 else BLUE_LIGHT)
                if int(radius) % 9 < 2:
                    part.sphere(point + [0, 2, 0], 2, LIGHT)
        rng = np.random.default_rng(1470)
        for index in range(230):
            u = rng.uniform(280, 570)
            width = min((u * np.sin(np.pi / 7) - 85) / np.cos(np.pi / 7), np.sqrt(580 ** 2 - u ** 2))
            v = rng.uniform(-width, width)
            point = radial(u, rng.uniform(13, 47), v, angle)
            radius = 1 if index % 9 else 3
            part.box(point - radius, point + radius, LIGHT if index % 4 else YELLOW)
        part.sphere(radial(420, 22, 0, angle), 16, BLUE_LIGHT)
        part.sphere(radial(420, 22, 0, angle), 11, LIGHT)
        part.sphere(radial(420, 25, 0, angle), 7, YELLOW)


def build():
    parts, info = [], []
    for index, (kind, label, distance, height, radius, lamp) in enumerate(DIMENSIONS):
        angle = np.pi / 2 + (index + .5) * 2 * np.pi / 7
        center = np.rint(radial(distance, height, 0, angle)).astype(int)
        identity = f'dimension_{index + 1:02d}_{kind}'
        landscape = Part(identity + '_interior', label + '维度球内景', group='dimensions')
        if kind == 'galaxy':
            galaxy_orb(landscape, center, radius)
        else:
            orb_ground(landscape, center, radius, kind)
            orb_decorations(landscape, center, radius, kind)
        parts.append(landscape.finish())
        shell = Part(identity + '_enclosure', label + '观察壳与约束环', group='dimensions')
        enclosure(shell, center, radius, lamp)
        parts.append(shell.finish())
        support = Part(identity + '_feed', label + '供料桥与支座', group='feed')
        feed(support, center, radius, distance, angle, lamp)
        parts.append(support.finish())
        sector = Part(identity + '_sector', label + '对应扇区地貌', group='sectors')
        sector_ground(sector, kind, angle)
        sector_decorations(sector, kind, angle)
        parts.append(sector.finish())
        info.append(dict(id=identity, label=label, center=center.tolist(), radius=radius, kind=kind,
                         sector_angle=float(angle), sector_center=np.rint(radial(420, 35, 0, angle)).astype(int).tolist(),
                         source='HK3GTL维度与星系外观设计', sector_radial_range=[225, 590], leg_clearance=72))
        print(f'{label}维度球与对应扇区生成完成', flush=True)
    return parts, info
