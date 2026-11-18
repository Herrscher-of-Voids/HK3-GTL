# -*- coding: utf-8 -*-
from pathlib import Path
import json, math
import numpy as np
from w02_19c_geometry_v4_20261110 import SolidPart, solid_annulus
from w04_kurikara_d1_parts_20261110 import hull
import w04_kurikara_d4_20261110 as dragon
import w04_narukami_s1_20261110 as sword

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-em-skyhub-a1-20261114'
BLACK = 'minecraft:polished_blackstone_bricks'
DARK = 'minecraft:deepslate_tiles'
RED = 'hk3gtl:voltage_machine_casing_hrv'
IRON = 'minecraft:iron_block'
GOLD = 'minecraft:gold_block'
LIGHT = 'minecraft:sea_lantern'
QUARTZ = 'minecraft:quartz_block'
CONTROL = 'minecraft:redstone_block'
DRAGON_MAP = {'minecraft:black_concrete': BLACK, 'minecraft:gray_concrete': 'minecraft:polished_deepslate',
    'minecraft:cyan_terracotta': DARK, 'minecraft:red_concrete': RED, 'minecraft:pink_terracotta': RED,
    'minecraft:white_terracotta': QUARTZ, 'minecraft:white_concrete': QUARTZ, 'minecraft:light_gray_concrete': IRON}
SWORD_MAP = {'minecraft:black_concrete': BLACK, 'minecraft:gray_concrete': DARK,
    'minecraft:white_concrete': QUARTZ, 'minecraft:light_gray_concrete': IRON}
STATES = list(dict.fromkeys([BLACK, DARK, RED, IRON, GOLD, LIGHT, QUARTZ, CONTROL,
    *[DRAGON_MAP.get(s, s) for s in dragon.STATES], *[SWORD_MAP.get(s, s) for s in sword.STATES]]))
IDS = {s: i + 1 for i, s in enumerate(STATES)}
CENTER = np.array([0., 0., 110.])


class Part(SolidPart):
    def points(self, points, state):
        points = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(points)
        self.values.append(np.full(len(points), IDS[state], np.uint8))


def ring(p, center, radius, inner, depth, state):
    solid_annulus(p, center, [0, 1, 0], radius, inner, depth, state)


def polar(r, angle, y):
    return CENTER + [r * math.cos(angle), y, r * math.sin(angle)]


def imported(file, source_states, prefix, matrix, shift, mapping):
    source = np.load(file)
    for key in source.files:
        if not key.endswith('__p'):
            continue
        name = key[:-3]
        p = Part(prefix + '_' + name)
        points = np.rint(source[key] @ matrix.T + shift).astype(np.int32)
        values = source[name + '__states']
        for i, state in enumerate(source_states, 1):
            p.points(points[values == i], mapping.get(state, state))
        yield p.finish()


def deck():
    p = Part('base_01_削角八边形空腔重型机台')
    zz, xx = np.mgrid[-410:371, -420:421]
    edge_distance = np.maximum.reduce([abs(xx) - 420, -zz - 410, zz - 370,
        abs(xx) + np.maximum(-zz - 340, zz - 300) - 420])
    radial = np.hypot(xx, zz - 110)
    outline = edge_distance <= 0
    for y in range(25):
        shell = (y < 3) | (y >= 22) | (edge_distance >= -8)
        keep = outline & (radial >= 179) & shell
        ribs = (abs(xx) % 56 < 3) | (abs(zz + 18) % 56 < 3)
        for state, mask in [(BLACK, keep & ~ribs), (DARK, keep & ribs)]:
            p.points(np.c_[xx[mask], np.full(np.count_nonzero(mask), y), zz[mask]], state)
    for side in [-1, 1]:
        p.box([side * 396 - 3, 25, -320], [side * 396 + 3, 27, 275], RED)
        for z in range(-300, 281, 58):
            p.box([side * 396 - 5, 28, z], [side * 396 + 5, 29, z + 10], IRON)
    for x in range(-355, 356, 71):
        p.box([x - 19, 25, -371], [x + 19, 28, -354], IRON)
    return p.finish()


def basin():
    p = Part('base_02_下沉雷池与七相汇流底盘')
    ring(p, [0, 7, 110], 179, 0, 8, DARK)
    ring(p, [0, 14, 110], 179, 168, 12, BLACK)
    ring(p, [0, 19, 110], 174, 168, 3, RED)
    ring(p, [0, 15, 110], 42, 0, 10, BLACK)
    ring(p, [0, 22, 110], 29, 0, 4, LIGHT)
    ring(p, [0, 26, 110], 31, 26, 3, 'minecraft:magenta_stained_glass')
    for a in np.linspace(0, 2 * math.pi, 7, endpoint=False):
        p.beam(polar(46, a, 14), polar(165, a, 14), 3, GOLD)
        p.beam(polar(62, a + .035, 17), polar(155, a + .035, 17), 1.2, LIGHT)
    return p.finish()


def magnet(index, radius, y):
    p = Part(f'field_01_{index}_十二分瓣水平超导磁环')
    center = CENTER + [0, y, 0]
    ring(p, center, radius + 11, radius - 17, 18, BLACK)
    ring(p, center, radius + 5, radius - 11, 20, RED)
    ring(p, center + [0, 11, 0], radius + 10, radius + 7, 2, IRON)
    ring(p, center + [0, 11, 0], radius - 13, radius - 16, 2, IRON)
    for a in np.linspace(0, 2 * math.pi, 12, endpoint=False):
        p.beam(polar(radius - 17, a, y + 13), polar(radius + 11, a, y + 13), 2.3, IRON)
        p.beam(polar(radius - 13, a + .065, y + 12), polar(radius + 7, a + .065, y + 12), 1.5, GOLD)
        for da in np.linspace(.13, .34, 7):
            p.sphere(polar(radius, a + da, y + 12), 1.6, LIGHT)
    for a in np.linspace(0, 2 * math.pi, 6, endpoint=False):
        p.beam(polar(radius, a, 25), polar(radius, a, y - 10), 5, BLACK)
    return p.finish()


def tower(side):
    p = Part(f'field_02_{side:+d}_分瓣储能与鬼角绝缘塔')
    x, z = side * 302, 140
    p.box([x - 43, 25, z - 45], [x + 43, 35, z + 45], BLACK)
    ring(p, [x, 100, z], 29, 0, 130, DARK)
    for y in range(48, 170, 18):
        ring(p, [x, y, z], 37, 27, 8, RED)
        ring(p, [x, y + 5, z], 38, 34, 2, IRON)
    ring(p, [x, 179, z], 35, 0, 8, BLACK)
    for dx in [-15, 15]:
        a = np.array([x + dx, 182, z])
        b = np.array([x + dx * 1.7, 208, z - 3])
        c = np.array([x + dx * 2.3, 221, z - 7])
        hull(p, [a + [i, 0, j] for i in [-7, 7] for j in [-10, 10]] +
            [b + [i, 0, j] for i in [-4, 4] for j in [-6, 6]] + [c], BLACK)
        p.beam(a + [0, 0, 10], b + [0, 0, 6], 1.7, GOLD)
    for dx in [-35, 35]:
        p.beam([x + dx, 36, z - 28], [x + dx, 177, z - 28], 3, IRON)
    p.beam([x - side * 30, 48, z], [side * 208, 44, 110], 10, BLACK)
    p.beam([x - side * 30, 58, z], [side * 208, 54, 110], 4, GOLD)
    p.beam([x - side * 30, 41, z + 17], [side * 208, 37, 127], 3, LIGHT)
    return p.finish()


def cooling(side):
    p = Part(f'base_03_{side:+d}_后置低温冷却站与保温管组')
    x, z = side * 302, -275
    p.box([x - 52, 25, z - 61], [x + 52, 33, z + 61], BLACK)
    for dz in [-32, 32]:
        ring(p, [x, 55, z + dz], 24, 0, 40, IRON)
        for y in [36, 48, 62, 74]:
            ring(p, [x, y, z + dz], 26, 21, 3, BLACK)
        ring(p, [x, 78, z + dz], 21, 0, 4, RED)
        p.box([x - 3, 39, z + dz + 24], [x + 3, 71, z + dz + 25], LIGHT)
    for dz in [-24, 24]:
        path = [[x, 35, z + dz], [side * 242, 35, z + dz], [side * 242, 35, 30 + dz], [side * 204, 44, 60 + dz]]
        for a, b in zip(path[:-1], path[1:]):
            p.beam(a, b, 5, BLACK)
            p.beam(np.array(a) + [0, 4, 0], np.array(b) + [0, 4, 0], 2, IRON)
    return p.finish()


def mounts():
    p = Part('base_04_龙爪鞍座与七雷实体剑托')
    for x in [29, 101]:
        p.box([x - 28, 25, -41], [x + 28, 48, 6], BLACK)
        p.box([x - 24, 49, -37], [x + 24, 54, 2], IRON)
        p.box([x - 18, 55, -33], [x + 18, 56, -2], RED)
    for a in [[-145, 25, 265], [-35, 25, 265], [-90, 25, 302]]:
        p.beam(a, [-90, 91, 240], 5, BLACK)
    p.box([-109, 90, 233], [-71, 95, 247], IRON)
    for side in [-1, 1]:
        p.beam([65 + side * 72, 25, -190], [65 + side * 28, 115, -128], 7, BLACK)
        p.beam([65 + side * 72, 32, -190], [65 + side * 28, 122, -128], 2, RED)
    return p.finish()


def control():
    p = Part('base_05_嵌入前庭的中轴主控占位')
    p.box([-42, 3, 312], [42, 12, 333], BLACK)
    p.box([-28, 13, 312], [28, 27, 328], RED)
    p.box([-18, 28, 311], [18, 30, 327], IRON)
    p.box([0, 18, 329], [0, 18, 329], CONTROL)
    for z in range(336, 371, 6):
        p.box([-30, 25, z], [-10, 26, z + 1], IRON)
        p.box([10, 25, z], [30, 26, z + 1], IRON)
    return p.finish()


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    parts = [deck(), basin()]
    parts += [magnet(i, r, y) for i, (r, y) in enumerate([(199, 44), (163, 78), (127, 112)], 1)]
    parts += [tower(s) for s in [-1, 1]] + [cooling(s) for s in [-1, 1]] + [mounts(), control()]
    parts += list(imported(dragon.LOG / 'components.npz', dragon.STATES, 'dragon', np.eye(3) * .74, [65, 54, -100], DRAGON_MAP))
    matrix = np.array([[0, -.32, 0], [.32, 0, 0], [0, 0, .32]])
    shift = np.array([-90, 96, 240]) - matrix @ np.array([5, 53, 0])
    parts += list(imported(ROOT / 'logs/w04-narukami-study-20261110/s1-components.npz', sword.STATES, 'sword', matrix, shift, SWORD_MAP))
    np.savez_compressed(LOG / 'components.npz', **{key: value for p in parts for key, value in [(p.name + '__p', p.p), (p.name + '__states', p.states)]})
    low = np.min([p.p.min(0) for p in parts], 0)
    high = np.max([p.p.max(0) for p in parts], 0)
    details = dict(reactor=dict(center=[0, 72, 110], half=[225, 80, 225]),
        dragon=dict(center=[65, 205, -155], half=[345, 155, 230]),
        sword=dict(center=[-90, 213, 240], half=[45, 123, 35]),
        field=dict(center=[0, 125, 120], half=[350, 112, 240]),
        head=dict(center=[65, 285, 12], half=[48, 74, 63]),
        casing=dict(center=[302, 120, 175], half=[14, 15, 12]),
        torii=dict(center=[0, 25, 329], half=[60, 38, 47]),
        magnet=dict(center=[0, 72, 110], half=[225, 80, 225]),
        controller=dict(center=[0, 18, 329], half=[45, 20, 38]))
    scene = dict(states=STATES, parts=[dict(id=p.name, asset=p.name.split('_')[0]) for p in parts],
        controller_world=[0, 18, 329], detail_views=details,
        transforms=dict(dragon=dict(scale=.74, translation=[65, 54, -100]),
            sword=dict(scale=.32, rotation_z=90, anchor=[5, 53, 0], target=[-90, 96, 240])),
        summary='三层水平超导磁环、七相汇流雷池、左前七雷、右后龙首与展开双翼；双侧储能塔和低温冷却站。',
        bounds_world=dict(min=low.tolist(), max=high.tolist()),
        source_models=['logs/w04-kurikara-d4-20261110/components.npz', 'logs/w04-narukami-study-20261110/s1-components.npz'],
        source_quantization='每个源方块中心参与统一比例缩放与整数格量化；未以名义尺寸裁切，运行时无模型缩放。')
    (LOG / 'scene.json').write_text(json.dumps(scene, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(parts=len(parts), size_xyz=(high - low + 1).tolist(), source_component_blocks=sum(len(p.p) for p in parts)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
