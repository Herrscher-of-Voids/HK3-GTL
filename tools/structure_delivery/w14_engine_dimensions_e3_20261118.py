import numpy as np
from scipy.ndimage import binary_erosion

from w14_engine_common_e3_20261118 import *
from w14_engine_bubbles_20261117 import enclosure, feed
from w14_engine_dimensions_e2_20261117 import (
    DIMENSIONS, MOON_ORB_CRATERS, MOON_SECTOR_CRATERS, crater, cloud_cluster,
    orb_height as old_orb_height, sector_height as old_sector_height, galaxy_orb,
    sector_decorations as old_sector_decorations,
)
from w14_engine_partitions_e3_20261118 import sector_mask
from w14_engine_native_oak_e3_20261118 import decorate_overworld
from w14_engine_native_nether_end_e3_20261118 import nether_height, nether_states, decorate_nether, decorate_end


def orb_height(kind, x, z, radius):
    if kind == 'nether':
        return nether_height(x, z, orb=True)
    if kind == 'overworld':
        return -.28 * radius + 1.3 * np.sin(x / 31) * np.cos(z / 35)
    if kind == 'end':
        r = np.sqrt(x * x + z * z)
        return -.25 * radius + 4 * np.clip((r - 10) / 42, 0, 1)
    return old_orb_height(kind, x, z, radius)


def sector_height(kind, u, v):
    if kind == 'nether':
        return nether_height(u, v)
    if kind == 'overworld':
        return 21 + 2 * np.sin(u / 71) * np.cos(v / 83)
    if kind == 'end':
        r = np.sqrt(((u - 410) / 1.2) ** 2 + v * v)
        return 24 + 6 * np.clip((r - 12) / 100, 0, 1) - 7 * np.clip((r - 140) / 90, 0, 1)
    return old_sector_height(kind, u, v)


def states_for(kind, u, v, surface, orb=False):
    if kind == 'nether':
        return nether_states(u, v, surface, orb=orb)
    base = {'overworld': STONE, 'end': END_STONE, 'moon': MOON_STONE,
            'mars': MARS_STONE, 'venus': VENUS_STONE, 'galaxy': BLACK}[kind]
    states = np.full(len(surface), base, np.uint8)
    if kind == 'overworld':
        states[surface < 4] = DIRT
        states[surface < 1] = GRASS_BLOCK
    elif kind in ['moon', 'mars', 'venus']:
        states[surface < 2] = {'moon': MOON_SAND, 'mars': MARS_SAND, 'venus': VENUS_SAND}[kind]
        if kind == 'moon':
            for cx, cz, radius, depth in MOON_ORB_CRATERS if orb else MOON_SECTOR_CRATERS:
                distance = np.sqrt((u - cx) ** 2 + (v - cz) ** 2) / radius
                states[(surface < 1) & (distance < .48)] = MOON_STONE
    return states


def orb_ground(part, center, radius, kind):
    z, x = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    top = orb_height(kind, x, z, radius)
    for y in range(-radius + 5, int(np.ceil(top.max())) + 1):
        mask = (x * x + z * z + y * y <= (radius - 5) ** 2) & (y <= top)
        surface = top[mask] - y
        states = states_for(kind, x[mask], z[mask], surface, orb=True)
        points = np.c_[x[mask], np.full(mask.sum(), y), z[mask]] + center
        for state in np.unique(states):
            part.points(points[states == state], state)


def orb_decorations(part, center, radius, kind):
    def position(u, v, offset=0):
        return center + [u, int(np.floor(orb_height(kind, u, v, radius))) + offset, v]

    if kind == 'overworld':
        decorate_overworld(part, position, orb=True)
    elif kind == 'end':
        return decorate_end(part, position, orb=True)
    elif kind == 'nether':
        decorate_nether(part, position, orb=True)
    elif kind in ['moon', 'mars']:
        for u, v, size in [(-42, -29, 5), (34, 23, 4), (-4, 35, 3), (39, -5, 5)]:
            part.sphere(position(u, v, size * .4), size, MOON_STONE if kind == 'moon' else MARS_STONE)
    elif kind == 'venus':
        for u, v, height, length, width, thickness, angle in [(-37, -20, 29, 23, 9, 3, -.2), (8, -5, 42, 17, 10, 4, .35), (33, 25, 27, 22, 8, 3, -.35), (-25, 27, 47, 16, 11, 4, .1), (4, -39, 50, 16, 7, 3, -.15)]:
            cloud_cluster(part, center + [u, height, v], length, width, thickness, angle)
    return []


def sector_ground(part, kind, angle):
    z, x = np.mgrid[-606:607, -606:607]
    mask, u, v = sector_mask(x, z, angle)
    edge = mask & ~binary_erosion(mask, iterations=2)
    xx, zz, uu, vv, border = x[mask], z[mask], u[mask], v[mask], edge[mask]
    top = np.rint(sector_height(kind, uu, vv)).astype(int)
    for y in range(5, int(top.max()) + 1):
        outer = 624 - max(0, min(y, 43) - 5) * .28 - 18
        keep = (y <= top) & ((y >= top - 5) | border | (y <= 6)) & (xx * xx + zz * zz <= outer * outer)
        states = states_for(kind, uu[keep], vv[keep], top[keep] - y)
        points = np.c_[xx[keep], np.full(keep.sum(), y), zz[keep]]
        for state in np.unique(states):
            part.points(points[states == state], state)


def sector_decorations(part, kind, angle):
    def position(u, v, offset=0):
        return radial(u, int(np.rint(sector_height(kind, u, v))) + offset, v, angle)

    if kind == 'overworld':
        decorate_overworld(part, position)
    elif kind == 'end':
        return decorate_end(part, position)
    elif kind == 'nether':
        decorate_nether(part, position)
    elif kind in ['moon', 'mars']:
        for u, v, size in [(190, 0, 6), (245, 20, 5), (315, -30, 7), (365, 50, 9), (460, -105, 7), (520, 115, 6), (550, -50, 8), (565, 12, 5)]:
            part.sphere(position(u, v, size * .4), size, MOON_STONE if kind == 'moon' else MARS_STONE)
    else:
        old_sector_decorations(part, kind, angle)
    return []


def build():
    parts, info = [], []
    for index, (kind, label, distance, height, radius, lamp) in enumerate(DIMENSIONS):
        angle = np.pi / 2 + (index + .5) * 2 * np.pi / 7
        center = np.rint(radial(distance, height, 0, angle)).astype(int)
        identity = f'dimension_{index + 1:02d}_{kind}'
        landscape = Part(identity + '_interior', label + '原生维度球内景', group='dimensions')
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
        sector = Part(identity + '_sector', label + '完整扇区地貌', group='sectors')
        sector_ground(sector, kind, angle)
        sector_decorations(sector, kind, angle)
        parts.append(sector.finish())
        info.append(dict(id=identity, label=label, center=center.tolist(), radius=radius, kind=kind,
            sector_angle=float(angle), sector_center=np.rint(radial(410, 35, 0, angle)).astype(int).tolist(),
            source='原生Minecraft1.20.1与Ad Astra1.15.20维度材质和地貌',
            sector_radial_range=[123, 606], leg_clearance='贴合53至39格变宽隔墙及外坝内壁，无额外留空'))
        print(f'{label}原生维度球与完整扇区生成完成', flush=True)
    return parts, info
