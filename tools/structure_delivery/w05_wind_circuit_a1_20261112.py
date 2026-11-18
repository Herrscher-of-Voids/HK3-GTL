# -*- coding: utf-8 -*-
"""W05原创静态候选：双层回流风道、中央整流风眼与弧形导流壳。"""
from pathlib import Path
import math
import numpy as np
from w02_19c_geometry_v4_20261110 import SolidPart, hull, solid_annulus, bezier

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/remove-fixed-ports-r266-20261113/w05'
LOG = ROOT / 'logs/remove-fixed-ports-r266-20261113/w05-build'
GREEN = 'hk3gtl:voltage_machine_casing_hdv'
WHITE = 'minecraft:white_concrete'
SILVER = 'minecraft:light_gray_concrete'
METAL = 'minecraft:iron_block'
BLACK = 'minecraft:black_concrete'
LIGHT = 'minecraft:sea_lantern'
GLASS = 'minecraft:cyan_stained_glass'
CONTROL = 'minecraft:redstone_block'
STATES = [GREEN, WHITE, SILVER, METAL, BLACK, LIGHT, GLASS, CONTROL]
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = dict(zip(STATES, [
    'HDV风息绿主甲与流路边缘；外观身份，运行仍为WSV',
    '银白导流壳、整流叶栅与检修栈桥', '浅灰承托和流道防护边', '金属泵壳、轴承和换热鳍片',
    '暗色结构梁、设备内衬与机械接缝', '静态流路照明及工位指示',
    '青色可视流路与观察窗，不代表正式工艺介质', '未注册W05控制器的明确占位'
]))
CTRL = np.array([0, 23, 331], np.int32)


class Part(SolidPart):
    def points(self, points, state):
        a = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(a)
        self.values.append(np.full(len(a), IDS[state], np.uint8))


def stadium(p, outer, inner, y0, y1, state):
    """两端为半圆、中间为直道的完整闭合流路。"""
    z, x = np.mgrid[-math.ceil(outer + 92):math.ceil(outer + 92) + 1,
                     -math.ceil(outer):math.ceil(outer) + 1]
    distance = np.sqrt(x * x + np.maximum(abs(z) - 92, 0) ** 2)
    keep = (distance <= outer) & (distance >= inner)
    x, z = x[keep], z[keep]
    for y in range(y0, y1 + 1):
        p.points(np.c_[x, np.full(len(x), y), z], state)


def ring(p, c, radius, inner, depth, state, axis=(0, 1, 0)):
    solid_annulus(p, c, axis, radius, inner, depth, state)


def path(p, points, radius, state):
    for a, b in zip(points[:-1], points[1:]):
        p.beam(a, b, radius, state)


def slab(p, outline, y0, y1, state):
    hull(p, [(x, y, z) for y in [y0, y1] for x, z in outline], state)


def deck():
    p = Part('01_开敞环形承台与检修廊')
    stadium(p, 254, 139, 0, 5, BLACK)
    stadium(p, 252, 246, 6, 9, GREEN)
    stadium(p, 244, 229, 6, 10, SILVER)
    stadium(p, 155, 140, 6, 10, SILVER)
    stadium(p, 153, 150, 11, 12, WHITE)
    ring(p, [0, 6, 0], 105, 0, 12, BLACK)
    ring(p, [0, 14, 0], 102, 0, 5, GREEN)
    for z in [-63, 63]:
        p.box([-150, 6, z - 7], [150, 10, z + 7], SILVER)
        for edge in [-8, 8]:
            p.box([-145, 11, z + edge], [145, 12, z + edge], WHITE)
    for x in [-65, 65]:
        p.box([x - 7, 6, -254], [x + 7, 10, 254], SILVER)
    for side in [-1, 1]:
        for z in [-180, -90, 0, 90, 180]:
            x = side * (238 if abs(z) < 100 else 213)
            p.box([x - 5, 11, z - 5], [x + 5, 16, z + 5], GREEN)
            p.box([x - 3, 17, z - 3], [x + 3, 18, z + 3], LIGHT)
    return p.finish()


def flow_deck(level):
    y, outer, inner = (48, 226, 164) if level == 0 else (112, 195, 145)
    p = Part(f'02_{level + 1}_闭合回流槽与可视流带')
    stadium(p, outer, inner, y - 5, y, BLACK)
    stadium(p, outer, outer - 5, y + 1, y + 19, GREEN)
    stadium(p, inner + 5, inner, y + 1, y + 19, GREEN)
    stadium(p, outer + 1, outer - 6, y + 20, y + 22, WHITE)
    stadium(p, inner + 6, inner - 1, y + 20, y + 22, WHITE)
    stadium(p, outer - 8, outer - 13, y + 1, y + 1, LIGHT)
    stadium(p, inner + 13, inner + 8, y + 1, y + 1, LIGHT)
    stadium(p, outer - 7, inner + 7, y + 2, y + 5, GLASS)
    for side in [-1, 1]:
        x = side * ((inner + outer) / 2)
        for z in range(-72, 73, 36):
            direction = side * (1 if level == 0 else -1)
            for dz in range(-6, 7):
                tip = z + direction * (7 - abs(dz))
                p.box([x + dz - 1, y + 6, tip], [x + dz + 1, y + 6, tip + 1], WHITE)
    return p.finish()


def pylons(side):
    p = Part(f'03_{side:+d}_双层承托与外侧换热肋')
    for z in [-180, -90, 0, 90, 180]:
        x = side * (201 if abs(z) >= 100 else 202)
        hull(p, [(x + dx, y, z + dz) for y, width in [(10, 10), (43, 7)]
                 for dx in [-width, width] for dz in [-12, 12]], BLACK)
        p.box([x - 10, 23, z - 10], [x + 10, 28, z + 10], GREEN)
        root = [side * 201, 68, z]
        tip = [side * 171, 106, z]
        p.beam(root, tip, 5, SILVER)
        p.beam([side * 220, 68, z], tip, 3, GREEN)
    for z in [-60, 60]:
        x = side * 256
        p.box([x - 16, 10, z - 30], [x + 16, 32, z + 30], BLACK)
        for dz in range(-26, 27, 6):
            p.box([x - 19, 15, z + dz], [x + 19, 31, z + dz + 1], METAL)
        p.box([x - 14, 33, z - 28], [x + 14, 36, z + 28], GREEN)
    return p.finish()


def pumps(side, end):
    p = Part(f'04_{side:+d}_{end:+d}_回流泵与高低换向管')
    x, z = side * 126, end * 245
    p.box([x - 25, 6, z - 27], [x + 25, 14, z + 27], BLACK)
    for y, r, inner, d, state in [(23, 25, 0, 17, BLACK), (28, 27, 23, 9, GREEN),
                                (42, 23, 17, 19, METAL), (53, 26, 18, 5, WHITE),
                                (57, 17, 11, 5, GREEN)]:
        ring(p, [x, y, z], r, inner, d, state)
    for a in np.arange(8) * math.pi / 4:
        p.beam([x + 22 * math.cos(a), 34, z + 22 * math.sin(a)],
               [x + 22 * math.cos(a), 48, z + 22 * math.sin(a)], 1.2, BLACK)
    ring(p, [x, 60, z], 14, 7, 8, METAL)
    # 粗换向管只在端部联通上下层，两条回流槽本身保持各自闭合。
    route = [[x, 61, z], [x, 82, z], [x, 99, z - end * 20],
             [x, 114, z - end * 48]]
    path(p, route, 10, GREEN)
    path(p, [[x, 62, z + end * 9], [x, 82, z + end * 9],
             [x, 101, z - end * 12], [x, 116, z - end * 43]], 2, WHITE)
    ring(p, [x, 80, z], 13, 10, 5, SILVER)
    return p.finish()


def center_island():
    p = Part('05_中央整流岛与分流歧管')
    ring(p, [0, 23, 0], 88, 0, 12, BLACK)
    ring(p, [0, 31, 0], 92, 77, 7, WHITE)
    ring(p, [0, 37, 0], 79, 65, 7, GREEN)
    ring(p, [0, 41, 0], 65, 0, 7, SILVER)
    ring(p, [0, 49, 0], 56, 42, 10, GREEN)
    for a in np.arange(12) * math.pi / 6:
        direction = np.array([math.cos(a), 0, math.sin(a)])
        p.beam(direction * 60 + [0, 43, 0], direction * 101 + [0, 17, 0], 3, METAL)
        p.beam(direction * 64 + [0, 45, 0], direction * 79 + [0, 45, 0], 1.2, LIGHT)
    for side in [-1, 1]:
        for z in [-52, 52]:
            path(p, [[side * 60, 38, z], [side * 105, 38, z],
                     [side * 132, 49, z], [side * 164, 49, z]], 6, BLACK)
            path(p, [[side * 62, 44, z], [side * 105, 44, z],
                     [side * 132, 55, z], [side * 163, 55, z]], 1.5, GREEN)
    return p.finish()


def wind_eye():
    p = Part('06_中央立体风眼与静态扭转叶栅')
    for y, radius in [(62, 61), (94, 77), (141, 108), (235, 108)]:
        ring(p, [0, y, 0], radius, radius - 10, 9, BLACK)
        ring(p, [0, y + 5, 0], radius + 2, radius - 12, 3, GREEN)
        ring(p, [0, y + 8, 0], radius, radius - 5, 3, WHITE)
    for a in np.arange(6) * math.pi / 3:
        for r in [53, 98]:
            points = []
            for t in np.linspace(0, 1, 28):
                angle = a + math.radians(64) * t
                points.append([r * math.cos(angle), 81 + 151 * t, r * math.sin(angle)])
            path(p, points, 3.1 if r == 98 else 2.2, GREEN if r == 98 else SILVER)
        stations = []
        for t in np.linspace(0, 1, 25):
            angle = a + math.radians(64) * t
            u = np.array([math.cos(angle), 0, math.sin(angle)])
            v = np.array([-math.sin(angle), 0, math.cos(angle)])
            center = np.array([0, 89 + 141 * t, 0])
            profile = [(56, -3), (71, -10), (96, -7), (98, -3), (76, 2), (56, 3)]
            stations.append(np.array([center + u * r + v * d for r, d in profile]))
        for first, second in zip(stations[:-1], stations[1:]):
            hull(p, np.vstack([first, second]), WHITE)
    # 固定轴体的空心窗口与分段灯带，避免实心柱堵住风眼。
    for a in np.arange(6) * math.pi / 3:
        u = np.array([math.cos(a), 0, math.sin(a)])
        p.beam(u * 18 + [0, 43, 0], u * 18 + [0, 222, 0], 3, BLACK)
        for y in [67, 98, 129, 160, 191, 220]:
            p.beam(u * 18 + [0, y, 0], u * 33 + [0, y, 0], 1.5, GREEN)
    ring(p, [0, 55, 0], 58, 42, 8, GREEN)
    ring(p, [0, 223, 0], 36, 18, 8, METAL)
    ring(p, [0, 230, 0], 30, 0, 6, GREEN)
    ring(p, [0, 235, 0], 20, 0, 3, GLASS)
    for a in np.arange(6) * math.pi / 3:
        points = []
        for t in np.linspace(0, 1, 20):
            angle = a + .72 * t
            r = 31 + 53 * t
            points.append([r * math.cos(angle), 231 + 20 * math.sin(math.pi * t), r * math.sin(angle)])
        path(p, points, 3, SILVER)
        path(p, np.array(points) + [0, 4, 0], 1, GREEN)
    return p.finish()


def airfoil(side):
    p = Part(f'07_{side:+d}_上扬弧面导流壳')
    curve = np.array([[side * 245, 34, 65], [side * 310, 177, 15],
                      [side * 205, 312, -35], [side * 88, 318, -65]], float)

    def section(t, offset=0):
        c = bezier(curve, t)
        tangent = bezier(curve, min(1, t + .001)) - bezier(curve, max(0, t - .001))
        normal = np.array([-tangent[1] * side, tangent[0] * side, 0])
        normal /= np.linalg.norm(normal)
        width = np.interp(t, [0, .18, .55, .83, 1], [31, 51, 50, 29, 3])
        thick = np.interp(t, [0, .25, .7, 1], [11, 16, 9, 2])
        return c, normal, width, thick

    ts = np.linspace(0, 1, 35)
    for a, b in zip(ts[:-1], ts[1:]):
        vertices = []
        for t in [a, b]:
            c, n, w, h = section(t)
            profile = [(-.86, -.45), (-1, .12), (-.5, .85), (.2, 1),
                       (1, .1), (.72, -.6), (-.25, -.85)]
            vertices.extend(c + n * x * h + [0, 0, z * w] for z, x in profile)
        hull(p, vertices, WHITE)
    for lateral, state, radius in [(-.88, GREEN, 3.3), (.78, GREEN, 2.6), (.08, BLACK, 2.5)]:
        points = []
        for t in ts:
            c, n, w, h = section(t)
            points.append(c + n * h * .85 + [0, 0, w * lateral])
        path(p, points, radius, state)
    for t in np.linspace(.12, .88, 12):
        c, n, w, h = section(t)
        p.beam(c + n * (h + 1) + [0, 0, -.52 * w],
               c + n * (h + 1) + [0, 0, .53 * w], 1.4, SILVER)
    # 前后分开的液压撑杆让巨大壳体有可读的落地连接。
    for zoff in [-23, 23]:
        c, n, w, h = section(.36)
        p.beam([side * 267, 32, math.copysign(60, zoff)], c + [0, 0, zoff], 5, BLACK)
        p.beam([side * 267, 44, math.copysign(60, zoff)], c + [0, 0, zoff], 2.5, METAL)
    return p.finish()


def conditioner(end):
    p = Part(f'08_{end:+d}_进流调理与分流换热端站')
    z = end * 276
    slab(p, [(-77, z - 31), (77, z - 31), (88, z + 18), (61, z + 36),
             (-61, z + 36), (-88, z + 18)], 9, 18, BLACK)
    for x in [-48, 0, 48]:
        p.box([x - 15, 19, z - 20], [x + 15, 40, z + 20], GREEN)
        for dz in range(-18, 19, 6):
            p.box([x - 17, 22, z + dz], [x + 17, 39, z + dz + 1], METAL)
        p.box([x - 18, 41, z - 22], [x + 18, 45, z + 22], WHITE)
        p.box([x - 9, 47, z - 12], [x + 9, 49, z + 12], BLACK)
        for dx in [-5, 0, 5]:
            p.box([x + dx, 50, z - 9], [x + dx + 1, 50, z + 9], GREEN)
    return p.finish()


def control_bridge():
    p = Part('09_前庭主控墙与检修桥')
    slab(p, [(-72, 296), (72, 296), (78, 320), (58, 353),
             (-58, 353), (-78, 320)], 0, 10, BLACK)
    p.box([-43, 11, 306], [43, 14, 346], SILVER)
    for x in [-42, 42]:
        p.box([x - 2, 15, 306], [x + 2, 18, 345], GREEN)
    p.box([-14, 15, 324], [14, 31, 330], GREEN)
    p.box([-15, 32, 324], [15, 35, 332], WHITE)
    p.box([-10, 19, 331], [10, 28, 331], BLACK)
    p.box(CTRL, CTRL, CONTROL)
    for side in [-1, 1]:
        x = side * 23
        p.box([x - 4, 16, 325], [x + 4, 27, 330], WHITE)
        p.box([x - 2, 20, 331], [x + 2, 25, 331], GLASS)
        p.box([x - 2, 28, 325], [x + 2, 29, 330], LIGHT)
    for z in range(333, 342, 3):
        y = 17 - (z - 333) // 3
        p.box([-7, y, z], [7, y, z + 2], SILVER)
    return p.finish()


def build():
    parts = [deck(), flow_deck(0), flow_deck(1), pylons(-1), pylons(1)]
    parts += [pumps(s, e) for s in [-1, 1] for e in [-1, 1]]
    parts += [center_island(), wind_eye(), airfoil(-1), airfoil(1),
              conditioner(-1), conditioner(1), control_bridge()]
    points = np.concatenate([p.p for p in parts])
    low, high = points.min(0), points.max(0)
    size = high - low + 1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    for p in parts:
        at = p.p - low
        cube[at[:, 1], at[:, 2], at[:, 0]] = p.states
    ports = []
    data = dict(
        name='hk3gtl-w05-wind-circuit-a1-20261112-freeports-r266', title='风之律者 · 长风·理想流体环流阵 · 双层回流A1',
        display_version='A1', size=size.tolist(), actual_scene_size_xyz=size.tolist(),
        blocks=int(np.count_nonzero(cube)), blueprint_bounds=dict(min=low.tolist(), max=high.tolist()),
        blueprint_to_export_offset_xyz=(-low).tolist(), controller=(CTRL - low).tolist(),
        controller_blueprint=CTRL.tolist(), ports=ports, center_blueprint=[0, 155, 0],
        detail_views=dict(flow=dict(center=[190, 85, 0], half=[70, 75, 125]),
                          pump=dict(center=[126, 60, 245], half=[40, 62, 60]),
                          casing=dict(center=[222, 60, 0], half=[8, 8, 8])),
        palette_identity=dict(name='风息绿', color='#48C9A3', tier='HDV', runtime_voltage='WSV'),
        nominal_reference_xzy=[289, 321, 97], no_nominal_clipping=True, whole_integer_voxel=True,
        animation_enabled=False, approved=False, installed=False, game_verified=False, design_original=True,
        summary='双层闭合回流槽环绕中央扭转叶栅风眼，两片银白绿边导流壳向上收拢；四组回流泵联通高低流层，前后调理与换热端站接入同一环流骨架。',
        process_zones=['进流调理', '下层环流', '中央整流风眼', '上层回流', '分流换热', '回流泵阵'],
        source_conflicts=[
            '原创工业风洞候选，不宣称官方角色武装复刻；正式生产规则及介质尚未冻结。',
            '所有构件先完整生成再求实际边界，旧表289×321×97仅作尺寸参考，不用于裁切。',
            '全部1×1×1真实方块与静态构件，无运行时旋转缩放；未注册W05控制器或接入机器Pattern。',
            '主控为红石块占位；实体建筑位置可由玩家自行选择通用接口，主控除外。',
            '循环补液与热收支仅在外观上分区表达，未实现正式配方、研究或运行验收。'
        ], component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist(),
                                                  blocks=len(p.p)) for p in parts})
    return cube, data, parts


if __name__ == '__main__':
    import json
    _, manifest, _ = build()
    print(json.dumps(dict(size=manifest['size'], blocks=manifest['blocks']), ensure_ascii=False))
