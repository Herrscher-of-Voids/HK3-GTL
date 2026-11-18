import numpy as np

from w14_engine_common_e3_20261118 import (
    Part, NETHERRACK, BASALT, OBSIDIAN, END_STONE, MAGMA,
    CRIMSON_NYLIUM, WARPED_NYLIUM, CRIMSON_STEM, WARPED_STEM,
    NETHER_WART_BLOCK, WARPED_WART_BLOCK, SHROOMLIGHT,
    SOUL_SAND, SOUL_SOIL, BLACKSTONE, GRAVEL, BONE_BLOCK,
    BEDROCK, IRON_BARS, END_PORTAL, NETHER_LAVA, CRYSTAL_WHITE, CRYSTAL_PINK,
    WALL_TORCH_EAST, WALL_TORCH_WEST, WALL_TORCH_SOUTH, WALL_TORCH_NORTH,
)


NETHER_BIOMES = ['下界荒地', '绯红森林', '诡异森林', '灵魂沙峡谷', '玄武岩三角洲']
NETHER_CENTERS = np.array([[230, 0], [375, -82], [452, 112], [530, -123], [550, 22]])
PILLAR_RANKS = [4, 1, 7, 2, 9, 0, 6, 3, 8, 5]
VANILLA_SOURCE = {
    'archive': 'C:/Users/OWNER/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.18_mapped_official_1.20.1/forge-1.20.1-47.4.18_mapped_official_1.20.1-sources.jar',
    'entries': [
        'net/minecraft/world/level/levelgen/feature/HugeFungusFeature.java',
        'net/minecraft/world/level/levelgen/feature/EndPodiumFeature.java',
        'net/minecraft/world/level/levelgen/feature/SpikeFeature.java',
        'net/minecraft/client/renderer/entity/EndCrystalRenderer.java',
    ],
    'scope': '原生菌柄尺寸与菌帽分层概率、龙池7格主体、十根圆柱与两座铁笼。末影水晶转译为5×5×7整数格方块雕塑：浅色透明玻璃菱形框与粉色发光芯，禁止放置原生实体。末地主岛柱环间距及高度按微缩景观调整。',
}


def nether_coordinates(u, v, orb=False):
    u, v = np.broadcast_arrays(np.asarray(u, float), np.asarray(v, float))
    if orb:
        return 420 + 2.6 * u, 2.5 * v
    return u, v


def nether_biome(u, v, orb=False):
    u, v = nether_coordinates(u, v, orb)
    x = u + 10 * np.sin(v / 23) + 7 * np.cos(u / 41)
    z = v + 11 * np.sin(u / 29) + 5 * np.cos(v / 19)
    return np.argmin((x[..., None] - NETHER_CENTERS[:, 0]) ** 2 +
                     (z[..., None] - NETHER_CENTERS[:, 1]) ** 2, axis=-1)


def nether_lava(u, v, orb=False):
    x, z = nether_coordinates(u, v, orb)
    biome = nether_biome(u, v, orb)
    channel = abs(z - 22 * np.sin(x / 41) - 14 * np.sin(x / 77))
    pools = (np.sin(x / 17) + np.cos(z / 14) + .4 * np.cos((x + z) / 11))
    return ((biome == 0) & (channel < 10)) | ((biome == 4) & (pools > 1.25))


def nether_height(u, v, orb=False):
    x, z = nether_coordinates(u, v, orb)
    biome = nether_biome(u, v, orb)
    height = 23 + 5 * np.sin(x / 45) * np.cos(z / 29)
    height += np.where(biome == 4, 13 * abs(np.sin((x + .65 * z) / 43)) ** 5, 0)
    height += np.where(biome == 3, 4 * np.cos((x - z) / 28), 0)
    height = np.where(nether_lava(u, v, orb), 12, height)
    return -25 + (height - 18) * .45 if orb else height


def nether_states(u, v, surface, orb=False):
    u, v, surface = np.broadcast_arrays(u, v, surface)
    x, z = nether_coordinates(u, v, orb)
    biome = nether_biome(u, v, orb)
    states = np.full(u.shape, NETHERRACK, np.uint8)
    states[(biome == 3) & (surface < 4)] = SOUL_SOIL
    states[(biome == 3) & (surface < 1) & (np.sin(x / 12) + np.cos(z / 17) > -.25)] = SOUL_SAND
    states[(biome == 4) & (surface < 6)] = BLACKSTONE
    states[(biome == 4) & (surface < 2) & (np.cos(x / 8) + np.sin(z / 11) > -.25)] = BASALT
    states[(biome == 0) & (surface < 2) & (np.sin(x / 13) + np.cos(z / 16) > 1.05)] = GRAVEL
    states[(biome == 1) & (surface < 1)] = CRIMSON_NYLIUM
    states[(biome == 2) & (surface < 1)] = WARPED_NYLIUM
    lava = nether_lava(u, v, orb)
    states[lava & (surface < 3)] = MAGMA
    states[lava & (surface < 1)] = NETHER_LAVA
    return states


def huge_fungus(part, foot, warped, seed):
    rng = np.random.default_rng(seed)
    height = int(rng.integers(4, 14))
    stem, cap = (WARPED_STEM, WARPED_WART_BLOCK) if warped else (CRIMSON_STEM, NETHER_WART_BLOCK)
    blocks = {(0, y, 0): stem for y in range(height)}
    depth = min(int(rng.integers(1 + height // 3)) + 5, height)
    start = height - depth
    for y in range(start, height + 1):
        radius = 2 if y < height - rng.integers(3) else 1
        if depth > 8 and y < start + 4:
            radius = 3
        for x in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                point = (x, y, z)
                if point in blocks:
                    continue
                edge_x, edge_z = abs(x) == radius, abs(z) == radius
                inside = not edge_x and not edge_z and y != height
                if y < start + 3:
                    if not inside and (blocks.get((x, y - 1, z)) == cap or rng.random() < .15):
                        blocks[point] = cap
                else:
                    light_chance, cap_chance = (.1, .2) if inside else ((.01, .7) if edge_x and edge_z else (.0005, .98))
                    if rng.random() < light_chance:
                        blocks[point] = SHROOMLIGHT
                    elif rng.random() < cap_chance:
                        blocks[point] = cap
    for state in [stem, cap, SHROOMLIGHT]:
        points = [point for point, block in blocks.items() if block == state]
        part.points(np.asarray(points).reshape(-1, 3) + foot, state)


def scatter_points(orb, seed):
    rng = np.random.default_rng(seed)
    if orb:
        grid = [(u, v) for u in range(-54, 55, 11) for v in range(-54, 55, 11)]
        return [(u + rng.integers(-2, 3), v + rng.integers(-2, 3)) for u, v in grid if u * u + v * v < 57 ** 2]
    grid = [(u, v) for u in range(190, 592, 10) for v in range(-250, 251, 10)]
    return [(u + rng.integers(-3, 4), v + rng.integers(-3, 4)) for u, v in grid
            if u * u + v * v < 590 ** 2 and abs(v) < u * np.tan(np.pi / 7) - 70]


def decorate_nether(part, position, orb=False):
    rng = np.random.default_rng(140300 + orb)
    counts = dict.fromkeys(NETHER_BIOMES, 0)
    for index, (u, v) in enumerate(scatter_points(orb, 14371)):
        biome = int(nether_biome(u, v, orb))
        if nether_lava(u, v, orb):
            continue
        foot = np.rint(position(u, v, 1)).astype(int)
        if biome in (1, 2) and rng.random() < .56:
            huge_fungus(part, foot, biome == 2, 140000 + index)
            counts[NETHER_BIOMES[biome]] += 1
        elif biome == 4 and rng.random() < .30:
            height = int(rng.integers(3, 11 if orb else 21))
            radius = int(rng.integers(1, 3))
            part.box(foot + [-radius, 0, -radius], foot + [radius, height, radius], BASALT)
            counts[NETHER_BIOMES[biome]] += 1
        elif biome == 3 and index % (14 if orb else 29) == 0:
            length = 5 if orb else 11
            for d in range(-length // 2, length // 2 + 1):
                part.points(np.rint(position(u + d, v, 1)).reshape(1, 3), BONE_BLOCK)
            for d in [-length // 3, 0, length // 3]:
                for side in [-1, 1]:
                    for width in range(1, 4 if orb else 6):
                        point = np.rint(position(u + d, v + side * width, 1 + max(0, 3 - width)))
                        part.points(point.reshape(1, 3), BONE_BLOCK)
            counts[NETHER_BIOMES[biome]] += 1
    return counts


def cylinder(part, center, radius, low_y, high_y, state):
    z, x = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    inside = x * x + z * z <= radius * radius + 1
    xx, zz = x[inside] + center[0], z[inside] + center[2]
    for y in range(low_y, high_y + 1):
        part.points(np.c_[xx, np.full(len(xx), y), zz], state)


def dragon_pool(part, center):
    center = np.rint(center).astype(int)
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            radius2 = dx * dx + dz * dz
            if radius2 + 1 < 3.5 ** 2:
                part.points([center + [dx, -1, dz]], BEDROCK if radius2 + 1 < 2.5 ** 2 else END_STONE)
            if radius2 < 3.5 ** 2:
                part.points([center + [dx, 0, dz]], END_PORTAL if radius2 < 2.5 ** 2 else BEDROCK)
    part.box(center, center + [0, 3, 0], BEDROCK)
    for offset, state in [([1, 2, 0], WALL_TORCH_EAST), ([-1, 2, 0], WALL_TORCH_WEST),
                          ([0, 2, 1], WALL_TORCH_SOUTH), ([0, 2, -1], WALL_TORCH_NORTH)]:
        part.points([center + offset], state)


def crystal_sculpture(part, base):
    for y, radius in enumerate([0, 1, 2, 2, 2, 1, 0]):
        for x in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                if abs(x) + abs(z) == radius:
                    part.points([base + [x, y, z]], CRYSTAL_WHITE)
    for x, y, z in [(0, 2, 0), (0, 3, 0), (0, 4, 0),
                    (-1, 3, 0), (1, 3, 0), (0, 3, -1), (0, 3, 1)]:
        part.points([base + [x, y, z]], CRYSTAL_PINK)


def decorate_end(part, position, orb=False):
    center_u, radius_u, radius_v = (0, 42, 42) if orb else (410, 110, 82)
    dragon_pool(part, position(center_u, 0, 1))
    for index, rank in enumerate(PILLAR_RANKS):
        angle = -np.pi + index * 2 * np.pi / 10
        u, v = center_u + radius_u * np.cos(angle), radius_v * np.sin(angle)
        foot = np.rint(position(u, v, 1)).astype(int)
        radius, height = (2 + rank // 4, 12 + rank * 2) if orb else (3 + rank // 3, 34 + rank * 4)
        top_y = int(foot[1] + height)
        cylinder(part, foot, radius, int(foot[1]) - 3, top_y - 1, OBSIDIAN)
        part.points([[foot[0], top_y, foot[2]]], BEDROCK)
        crystal_sculpture(part, np.array([foot[0], top_y + 1, foot[2]]))
        if rank in (1, 2):
            for dx in range(-4, 5):
                for dz in range(-4, 5):
                    for dy in range(10):
                        if abs(dx) == 4 or abs(dz) == 4 or dy == 9:
                            part.points([[foot[0] + dx, top_y + dy, foot[2] + dz]], IRON_BARS)
    return []
