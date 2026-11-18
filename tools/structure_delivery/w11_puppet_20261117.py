import math

import numpy as np

from w11_common_20261117 import (
    Part, rod, BLACK, STUDS, WHITE, GOLD, RED, MAGENTA, LIGHT, WHITE_LIGHT,
    GLASS, GRAY, HK, CONTROLLER, line,
)


CENTER = np.array([-.5, 223., -.5])


def _part(name, label, section='puppet', **metadata):
    return Part('w11_' + name, label, section=section, **metadata)


def _layer(points, y):
    return np.column_stack((points[:, 0], np.full(len(points), y), points[:, 1]))


def _octagon(radius, inner=0):
    x, z = np.meshgrid(np.arange(-60, 60), np.arange(-60, 60), indexing='ij')
    ax, az = np.abs(x + .5), np.abs(z + .5)
    outer = (np.maximum(ax, az) <= radius) & (ax + az <= radius * (1 + math.sqrt(2)))
    inset = (np.maximum(ax, az) < inner) & (ax + az < inner * (1 + math.sqrt(2)))
    return np.column_stack((x[outer & ~inset], z[outer & ~inset]))


def _ring(part, radius, normal, state, thickness=2, depth=2):
    axes = [axis for axis in range(3) if axis != normal]
    bounds = [np.arange(math.ceil(CENTER[i] - radius), math.floor(CENTER[i] + radius) + 1) for i in axes]
    a, b = np.meshgrid(*bounds, indexing='ij')
    distance = (a - CENTER[axes[0]]) ** 2 + (b - CENTER[axes[1]]) ** 2
    selected = (distance <= radius ** 2) & (distance >= (radius - thickness) ** 2)
    half_depth = (depth - 1) / 2
    for fixed in range(math.ceil(CENTER[normal] - half_depth), math.floor(CENTER[normal] + half_depth) + 1):
        points = np.empty((int(selected.sum()), 3), dtype=np.int32)
        points[:, axes[0]], points[:, axes[1]] = a[selected], b[selected]
        points[:, normal] = fixed
        part.points(points, state)


def _mirror(point, side):
    x, y, z = point
    return (x if side > 0 else -1 - x, y, z)


def _box(part, low, high, state, side=1):
    a, b = _mirror(low, side), _mirror(high, side)
    part.box(tuple(min(x, y) for x, y in zip(a, b)), tuple(max(x, y) for x, y in zip(a, b)), state)


def _bone(part, start, end, side):
    a, b = np.array(_mirror(start, side), float), np.array(_mirror(end, side), float)
    delta = b - a
    part.beam(a, b, 2.5, BLACK)
    part.beam(a + delta * .13, a + delta * .87, 4, WHITE, inner=2)
    part.beam(a + (0, 0, -4), b + (0, 0, -4), 1, RED)
    for t in (.12, .88):
        part.beam(a + delta * (t - .045), a + delta * (t + .045), 4.5, GOLD, inner=3)


def _joint(part, point, side, radius=5):
    center = _mirror(point, side)
    part.sphere(center, radius, STUDS, inner=radius - 2)
    part.ring(center, radius, 1, GOLD, normal=(0, 0, 1), depth=2)
    x, y, z = center
    part.box((x - 1, y - 1, z + radius - 1), (x + 1, y + 1, z + radius), RED)


def _hand_up(part, side):
    _box(part, (64, 246, 20), (74, 252, 25), BLACK, side)
    _box(part, (64, 248, 25), (74, 252, 26), WHITE, side)
    _box(part, (65, 246, 20), (73, 247, 25), GOLD, side)
    _box(part, (68, 249, 27), (70, 251, 27), RED, side)
    for x, length in zip((64, 67, 70, 73), (5, 8, 7, 4)):
        _box(part, (x, 253, 22), (x + 1, 252 + length, 23), WHITE, side)
        _box(part, (x, 255, 22), (x + 1, 255, 23), BLACK, side)
        _box(part, (x, 252 + length, 22), (x + 1, 252 + length, 23), GOLD, side)
    thumb = [_mirror(point, side) for point in ((75, 249, 22), (78, 252, 22), (77, 255, 22))]
    part.beam(thumb[0], thumb[1], 1.3, WHITE)
    part.beam(thumb[1], thumb[2], 1.3, WHITE)
    part.sphere(thumb[1], 1.5, BLACK)


def _hand_forward(part, side):
    _box(part, (64, 229, 18), (74, 235, 24), BLACK, side)
    _box(part, (64, 229, 22), (74, 235, 24), WHITE, side)
    _box(part, (65, 229, 18), (73, 235, 19), GOLD, side)
    _box(part, (68, 231, 25), (70, 233, 25), MAGENTA, side)
    for x, length in zip((64, 67, 70, 73), (8, 11, 10, 7)):
        _box(part, (x, 231, 25), (x + 1, 232, 24 + length), WHITE, side)
        _box(part, (x, 231, 28), (x + 1, 232, 28), BLACK, side)
        _box(part, (x, 231, 24 + length), (x + 1, 232, 24 + length), GOLD, side)
    thumb = [_mirror(point, side) for point in ((75, 231, 23), (78, 231, 26), (77, 231, 30))]
    part.beam(thumb[0], thumb[1], 1.3, WHITE)
    part.beam(thumb[1], thumb[2], 1.3, WHITE)
    part.sphere(thumb[1], 1.5, BLACK)


def _hand_down(part, side):
    _box(part, (54, 201, 17), (64, 207, 23), BLACK, side)
    _box(part, (54, 201, 23), (64, 205, 24), WHITE, side)
    _box(part, (55, 206, 17), (63, 207, 23), GOLD, side)
    _box(part, (58, 202, 25), (60, 204, 25), RED, side)
    for x, length in zip((54, 57, 60, 63), (6, 9, 8, 5)):
        _box(part, (x, 201 - length, 20), (x + 1, 200, 21), WHITE, side)
        _box(part, (x, 197, 20), (x + 1, 197, 21), BLACK, side)
        _box(part, (x, 201 - length, 20), (x + 1, 201 - length, 21), GOLD, side)
    thumb = [_mirror(point, side) for point in ((65, 203, 20), (68, 200, 21), (67, 197, 22))]
    part.beam(thumb[0], thumb[1], 1.3, WHITE)
    part.beam(thumb[1], thumb[2], 1.3, WHITE)
    part.sphere(thumb[1], 1.5, BLACK)


def build_puppet():
    parts = []
    stage = _part('stage_shell', '统御舞台 · 倒八角黑金阶台', 'stage')
    for y in range(161, 191):
        radius = 30 + (y - 161) * 29.5 / 29
        inner = 0 if y in (161, 170, 180, 188, 189, 190) else radius - 3
        state = GOLD if y in (164, 173, 182, 188) else STUDS if y < 188 else BLACK
        stage.points(_layer(_octagon(radius, inner), y), state)
    stage.points(_layer(_octagon(59.5, 57.5), 190), GOLD)
    parts.append(stage.finish())

    inlay = _part('stage_inlay', '统御舞台 · 八向律令与南侧步行面', 'stage')
    x, z = np.meshgrid(np.arange(-56, 56), np.arange(-56, 56), indexing='ij')
    dx, dz = x + .5, z + .5
    radius = np.hypot(dx, dz)
    rings = (np.abs(radius - 16) < .65) | (np.abs(radius - 31) < .7) | (np.abs(radius - 46) < .65)
    spokes = (np.minimum(np.abs(dx), np.abs(dz)) < .7) | (np.abs(np.abs(dx) - np.abs(dz)) < .85)
    inlay.points(np.column_stack((x[rings], np.full(int(rings.sum()), 190), z[rings])), GOLD)
    selected = spokes & (radius > 20) & (radius < 44)
    inlay.points(np.column_stack((x[selected], np.full(int(selected.sum()), 190), z[selected])), LIGHT)
    inlay.box((-7, 190, 1), (6, 190, 56), STUDS)
    for edge in (-8, 7):
        inlay.box((edge, 190, 2), (edge, 190, 55), GOLD)
    for z0 in range(8, 53, 9):
        inlay.box((-2, 190, z0), (1, 190, z0 + 2), WHITE_LIGHT)
    for angle in np.arange(8) * math.pi / 4:
        cx, cz = -.5 + 52 * math.cos(angle), -.5 + 52 * math.sin(angle)
        inlay.box((round(cx) - 1, 190, round(cz) - 1), (round(cx) + 1, 190, round(cz) + 1), RED)
    parts.append(inlay.finish())

    torso = _part('puppet_torso', '机械木偶 · 开放骨瓷胸架与背脊')
    for side in (-1, 1):
        for a, b in (((11, 197, -23), (30, 216, -14)), ((30, 216, -14), (33, 244, -3)), ((33, 244, -3), (10, 248, -2))):
            _bone(torso, a, b, side)
        for y in (213, 231, 241):
            angles = np.linspace(-1.1, 1.1, 30)
            points = np.column_stack((33 * np.cos(angles) - .5, np.full(len(angles), y), 21 * np.sin(angles) - 2.5))
            if side < 0:
                points[:, 0] = -1 - points[:, 0]
            for a, b in zip(points[:-1], points[1:]):
                torso.beam(a, b, 2, BLACK)
                torso.beam(a + (0, 0, .7), b + (0, 0, .7), 1.25, WHITE)
            torso.sphere(points[-1], 2, GOLD)
        for point in ((33, 244, -3), (32, 232, -8), (30, 217, -12)):
            _joint(torso, point, side, 6)
    torso.box((-10, 196, -25), (9, 202, -22), STUDS)
    torso.box((-7, 198, -26), (6, 200, -26), GOLD)
    for x0 in (-4, 3):
        torso.beam((x0, 248, -2), (x0, 252, -2), 1.5, GRAY)
    parts.append(torso.finish())

    core = _part('puppet_heart', '统御之心 · 半径15红金空心胸核')
    points = np.stack(np.meshgrid(np.arange(-16, 16), np.arange(208, 239), np.arange(-16, 16), indexing='ij'), -1).reshape(-1, 3)
    local = points - CENTER
    r2 = np.sum(local * local, axis=1)
    shell = (r2 <= 225) & (r2 >= 144)
    core.points(points[shell], RED)
    seams = shell & ((np.abs(local[:, 0]) < 1) | (np.abs(local[:, 1]) < .6) | (np.abs(local[:, 2]) < 1))
    core.points(points[seams], GOLD)
    seal = shell & (local[:, 2] > 13) & (np.abs(local[:, 0]) < 3) & (np.abs(local[:, 1]) < 3)
    core.points(points[seal], LIGHT)
    parts.append(core.finish())

    for name, label, radius, normal, depth in (
        ('inner', '内层正交框 · R20', 20, 0, 2),
        ('middle', '中层正交框 · R24', 24, 2, 2),
        ('outer', '外层水平框 · R28', 28, 1, 3),
    ):
        frame = _part('puppet_frame_' + name, label, radius=radius, center=CENTER.tolist())
        _ring(frame, radius, normal, BLACK, depth=depth)
        _ring(frame, radius - .3, normal, GOLD, thickness=1.2, depth=depth)
        parts.append(frame.finish())

    poses = (
        ('command', '举手统御', ((33, 244, -3), (50, 250, 4), (68, 248, 22)), _hand_up),
        ('spread', '展掌操演', ((32, 232, -8), (51, 228, 2), (68, 232, 20)), _hand_forward),
        ('strings', '垂手提线', ((30, 217, -12), (48, 214, 3), (59, 207, 19)), _hand_down),
    )
    for side, side_label in ((-1, '左'), (1, '右')):
        for name, label, joints, hand in poses:
            arm = _part(f'puppet_arm_{name}_{side}', f'机械木偶 · {side_label}{label}臂与五指')
            for a, b in zip(joints[:-1], joints[1:]):
                _bone(arm, a, b, side)
            _joint(arm, joints[1], side)
            _joint(arm, joints[2], side, 4)
            hand(arm, side)
            parts.append(arm.finish())

    head = _part('puppet_head', '机械木偶 · 无脸骨瓷面具与暗红眼金冠')
    for y, width in zip(range(251, 260), (4, 5, 6, 8, 9, 9, 8, 8, 7)):
        head.box((-width - 1, y, -5), (width, y, 6), BLACK)
        head.box((-width - 1, y, 7), (width, y, 8), WHITE)
        head.box((-width - 1, y, 9), (-width - 1, y, 9), GOLD)
        head.box((width, y, 9), (width, y, 9), GOLD)
    head.box((-7, 255, 9), (-3, 255, 9), RED)
    head.box((2, 255, 9), (6, 255, 9), RED)
    head.box((-8, 256, 9), (-4, 256, 9), GOLD)
    head.box((3, 256, 9), (7, 256, 9), GOLD)
    head.box((-12, 259, -4), (11, 259, 1), GOLD)
    for x0 in (-11, -6, 4, 9):
        head.box((x0, 260, -3), (x0 + 1, 260, 0), GOLD)
    parts.append(head.finish())

    controller = _part('stage_controller', '唯一主控 · 舞台中心朝南', 'stage', facing='south', controller=[-1, 190, -1])
    controller.box((-1, 190, -1), (-1, 190, -1), CONTROLLER)
    parts.append(controller.finish())
    return parts
