import numpy as np

from w14_engine_common_e3_20261118 import DIRT, LOG_BLOCK, OAK_LEAVES


OAK_SOURCE = {
    'version': 'Minecraft Java 1.20.1',
    'archive': 'C:/Users/OWNER/.gradle/caches/fabric-loom/1.20.1/forge/1.20.1-47.3.0/minecraft-merged-srg.jar',
    'classes': [
        'net.minecraft.data.worldgen.features.TreeFeatures',
        'net.minecraft.world.level.levelgen.feature.trunkplacers.StraightTrunkPlacer',
        'net.minecraft.world.level.levelgen.feature.foliageplacers.BlobFoliagePlacer',
        'net.minecraft.world.level.levelgen.feature.foliageplacers.FoliagePlacer',
    ],
    'trunk': [4, 2, 0],
    'foliage': {'radius': 2, 'offset': 0, 'height': 3},
    'description': '按原版普通橡树配置、四层树冠及随机角叶逐格生成，尺寸为一比一。',
}


def oak_tree(part, foot, rng):
    foot = np.rint(foot).astype(int)
    height = 4 + int(rng.integers(3))
    leaves = []
    for dy in range(0, -4, -1):
        radius = 1 - int(dy / 2)
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if abs(dx) == radius and abs(dz) == radius and (rng.integers(2) == 0 or dy == 0):
                    continue
                leaves.append(foot + [dx, height + dy, dz])
    part.points(leaves, OAK_LEAVES)
    part.points(foot - [0, 1, 0], DIRT)
    part.box(foot, foot + [0, height - 1, 0], LOG_BLOCK)
    return {'foot': foot.tolist(), 'trunk_height': height}


def decorate_overworld(part, position, orb=False):
    rng = np.random.default_rng(14032 if orb else 14031)
    locations, trees = [], []
    count, separation = (15, 12) if orb else (50, 24)
    while len(locations) < count:
        if orb:
            distance = 53 * np.sqrt(rng.random())
            angle = rng.uniform(0, 2 * np.pi)
            u, v = np.rint([distance * np.cos(angle), distance * np.sin(angle)]).astype(int)
        else:
            u = int(rng.integers(190, 591))
            width = (u * np.sin(np.pi / 7) - 53 - 8) / np.cos(np.pi / 7)
            v = int(np.rint(rng.uniform(-width, width)))
            if np.hypot(u, v) > 594:
                continue
        if any((u - x) ** 2 + (v - z) ** 2 < separation ** 2 for x, z in locations):
            continue
        locations.append((int(u), int(v)))
        trees.append(oak_tree(part, position(u, v, 1), rng))
    return trees
