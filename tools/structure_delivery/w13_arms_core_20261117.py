import itertools
import math

import numpy as np

from w13_common_20261117 import *


def arm_point(angle, t):
    radius = 440 - 185 * math.sin(t * math.pi / 2) + 28 * math.sin(t * math.pi)
    return np.array([radius * math.cos(angle), 20 + 220 * t, -.5 + radius * .91 * math.sin(angle)])


def build_arms():
    parts = []
    anchors = []
    for i in range(6):
        angle = i * math.tau / 6
        radial = np.array([math.cos(angle), 0, math.sin(angle)])
        tangent = np.array([-math.sin(angle), 0, math.cos(angle)])
        infected = bool(radial[0] > 0)
        part = Part(f'arm_{i}', f'{"侵蚀" if infected else "完整"}机械刺剑翼{i + 1}', group='arms', infected=infected)
        for y in range(20, 241):
            t = (y - 20) / 220
            center = arm_point(angle, t)
            width, depth = 30 - 18 * t, 15 - 8 * t
            u, v = np.mgrid[-math.ceil(width):math.ceil(width) + 1, -math.ceil(depth):math.ceil(depth) + 1]
            mask = (abs(u) <= width) & (abs(v) <= depth) & ((abs(u) / width + abs(v) / depth) < 1.7)
            u, v = u[mask], v[mask]
            points = center + u[:, None] * tangent + v[:, None] * radial
            states = np.full(len(points), CLEAN if not infected else WHITE, np.uint8)
            states[(abs(u) < width * .56) & (abs(v) < depth * .55)] = STUDS
            states[(abs(u) > width - 3) | (abs(v) > depth - 2)] = WHITE_STUDS
            if infected:
                eaten = ((np.sin(y * .12 + u * .22) + np.cos(v * .6 - y * .07)) > .3) & (t > .22)
                states[eaten] = HK_MAGENTA
                states[eaten & ((np.rint(u + y).astype(int) % 13) < 2)] = MAGENTA_LIGHT
            for state in np.unique(states):
                part.points(points[states == state], state)
        for t in (.12, .34, .56, .78, .96):
            center = arm_point(angle, t)
            axis = arm_point(angle, min(1, t + .02)) - arm_point(angle, max(0, t - .02))
            part.ring(center, 36 - 16 * t, 3, GOLD if not infected else GRAY, normal=axis, depth=5)
        cooling = [arm_point(angle, t) + tangent * (22 - 12 * t) - radial * (15 - 7 * t) for t in np.linspace(.05, .95, 23)]
        for a, b in zip(cooling[:-1], cooling[1:]):
            rod(part, a, b, 4, BLUE if not infected else MAGENTA)
            rod(part, a - radial * 3, b - radial * 3, 2, BLUE_GLASS if not infected else RED_GLASS)
        for t in (.18, .45, .7):
            center = arm_point(angle, t)
            rod(part, center - tangent * 31, center + tangent * 31, 3, SILVER)
        if infected:
            for j, t in enumerate((.39, .62, .8)):
                root = arm_point(angle, t) + radial * 8
                direction = radial * (.7 if j != 1 else .45) + tangent * ((j - 1) * .32) + np.array([0, .72, 0])
                direction /= np.linalg.norm(direction)
                tip = root + direction * (80 + 20 * j)
                prism(part, root, tip, 13 + j * 2, MAGENTA_GLASS if j % 2 else PINK_GLASS)
                prism(part, root, root * .18 + tip * .82, 6, HK_PINK if j % 2 else PINK)
                rod(part, root + tangent * 2, tip * .95 + root * .05, 1, PINK_LIGHT)
                root2 = root - tangent * 12
                prism(part, root2, root2 + direction * 52 - tangent * 20, 8, MAGENTA_GLASS)
            for t in (.52, .76):
                center = arm_point(angle, t)
                rod(part, center - tangent * 36 - radial * 8, center + tangent * 32 + radial * 7 + np.array([0, 18, 0]), 2, RED_LIGHT)
        else:
            center = arm_point(angle, .16)
            rod(part, center - tangent * 20, center + tangent * 20, 6, HK_WHITE)
            for t in (.28, .58, .9):
                center = arm_point(angle, t) - radial * (15 - 7 * t)
                rod(part, center - tangent * 6, center + tangent * 6, 1, WHITE_LIGHT)
        parts.append(part.finish())
        anchors.append(arm_point(angle, .92))
    return parts, anchors


def build_rings():
    parts, specs = [], []
    for i, (radius, cy, tilt, azimuth) in enumerate([(375, 120, 15, 0), (300, 160, -25, 120), (225, 200, 40, 240)]):
        a, b = math.radians(tilt), math.radians(azimuth)
        rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
        ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
        matrix = ry @ rx
        normal = matrix[:, 1]
        center = np.array([0, cy, -.5])
        part = Part(f'ring_{i}', f'第{i + 1}重拓扑算力环', group='core', motion='ring', pivot=center.tolist(), axis=normal.tolist(), speed=[.035, -.047, .061][i], index=i)
        extent = np.sqrt(1 - normal * normal) * (radius + 9) + abs(normal) * 6
        low, high = np.floor(center - extent).astype(int), np.ceil(center + extent).astype(int)
        z, x = np.mgrid[low[2]:high[2] + 1, low[0]:high[0] + 1]
        for y in range(low[1], high[1] + 1):
            q = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
            d = q - center
            axial = d @ normal
            squared = np.einsum('ij,ij->i', d, d) - axial * axial
            mask = (abs(axial) <= 5.5) & (squared >= (radius - 9) ** 2) & (squared < (radius + 9) ** 2)
            q, local = q[mask], d[mask] @ matrix
            r = np.sqrt(squared[mask])
            angular = np.arctan2(local[:, 2], local[:, 0])
            state = np.full(len(q), BLACK, np.uint8)
            state[(r > radius + 5) | (abs(local[:, 1]) > 3.5)] = WHITE
            state[(r < radius - 6) & (abs(local[:, 1]) < 3)] = MAGENTA_LIGHT
            state[((np.floor((angular + math.pi) * 72 / math.tau).astype(int) % 6) == 0) & (abs(local[:, 1]) >= 3.5)] = PINK_LIGHT
            for material in np.unique(state):
                part.points(q[state == material], material)
        for j in range(60):
            t = j * math.tau / 60
            radial = np.array([math.cos(t), 0, math.sin(t)])
            tangent = np.array([-math.sin(t), 0, math.cos(t)])
            c = radial * (radius + 11)
            vertices = [center + matrix @ (c + radial * u + tangent * v + np.array([0, w, 0])) for u, v, w in itertools.product((-2, 2), (-2, 2), (-8, 8))]
            part.hull(vertices, VENT)
        parts.append(part.finish())
        specs.append(dict(radius=radius, center=center.tolist(), centerline_diameter=radius * 2, radial_width=18, axial_depth=12, tilt_degrees=tilt, azimuth_degrees=azimuth, normal=normal.tolist(), motion='沿各自倾斜法线转动'))
    return parts, specs


def build_core(anchors):
    parts = []
    transform = np.array([[1, -1, 0], [1, 1, 1], [-1, -1, 2]], float) / np.sqrt(np.array([2, 3, 6]))[:, None]
    corners = np.array(list(itertools.product((-110, 110), repeat=3)), float)
    vertices = corners @ transform.T + CORE
    frame = Part('broken_ark', '单尖朝下的破碎白金圣柜', group='core', source_cube_side=220, rotation=transform.tolist())
    for i, a in enumerate(corners):
        for j, b in enumerate(corners):
            if j <= i or np.count_nonzero(a != b) != 1:
                continue
            p, q = vertices[i], vertices[j]
            direction = (q - p) / np.linalg.norm(q - p)
            p, q = p + direction * 11, q - direction * 11
            rod(frame, p, q, 5, PORCELAIN)
            offset = np.cross(direction, [0, 1, 0])
            offset /= np.linalg.norm(offset)
            rod(frame, p + offset * 4, q + offset * 4, 1.5, GOLD)
            for t in (.12, .5, .88):
                c = p * (1 - t) + q * t
                rod(frame, c - direction * 2, c + direction * 2, 6, QUARTZ)
    for i, v in enumerate(vertices):
        moved = CORE + (v - CORE) * 1.035
        frame.sphere(moved, 7, HK_WHITE, inner=4)
        frame.sphere(moved, 3, GOLD_LIGHT)
    parts.append(frame.finish())
    chains = Part('restraint_chains', '八角粉色拘束能量锁链', group='arms')
    for i, v in enumerate(vertices):
        anchor = np.asarray(anchors[i % 6])
        endpoint = CORE + (v - CORE) * 1.035
        rod(chains, anchor, endpoint, 4.5, PINK_GLASS)
        rod(chains, anchor, endpoint, 1.2, PINK_LIGHT)
        axis = endpoint - anchor
        for t in np.linspace(.08, .92, 8):
            chains.ring(anchor * (1 - t) + endpoint * t, 6, 1.5, MAGENTA, normal=axis, depth=2)
    parts.append(chains.finish())
    body = Part('erosion_heart', '黑色数据坍缩球与下半剥离体素', group='core')
    body.sphere(CORE, 70, HK_BLACK, inner=64)
    rng = np.random.default_rng(13)
    for i in range(155):
        a = rng.uniform(0, math.tau)
        y = rng.uniform(-70, 13)
        r = math.sqrt(max(0, 70 * 70 - y * y)) + rng.uniform(-3, 13)
        size = int(rng.integers(3, 21))
        c = CORE + [r * math.cos(a), y, r * math.sin(a)]
        body.box(np.rint(c - size / 2), np.rint(c - size / 2) + size - 1, [VOID, HK_BLACK, OBSIDIAN][i % 3])
    body.sphere(CORE + [0, 14, 0], 56, HK_MAGENTA, inner=52)
    body.ring(CORE + [0, 5, 0], 58, 4, MAGENTA_LIGHT, depth=5)
    parts.append(body.finish())
    flower = Part('crystal_flower', '直径180格的几何结晶曼陀罗', group='core', motion='flower', pivot=[0, 244, -.5], axis=[0, 1, 0], speed=1.6)
    for layer, (count, base_radius, end_radius, base_y, end_y, width) in enumerate([(12, 27, 88, 227, 255, 16), (9, 18, 65, 232, 280, 15), (6, 10, 37, 240, 290, 12)]):
        for i in range(count):
            a = i * math.tau / count + layer * .29
            root = np.array([base_radius * math.cos(a), base_y, -.5 + base_radius * math.sin(a)])
            tip = np.array([end_radius * math.cos(a + .14), end_y + (i % 3 - 1) * 4, -.5 + end_radius * math.sin(a + .14)])
            prism(flower, root, tip, width, PINK_GLASS if (i + layer) % 3 else MAGENTA_GLASS, sides=5, tip=0)
            prism(flower, root, root * .35 + tip * .65, width * .4, HK_PINK if layer else PINK)
            rod(flower, root, tip * .95 + root * .05, 1, PINK_LIGHT)
    flower.sphere((0, 251, -.5), 17, PINK_LIGHT, inner=11)
    flower.sphere((0, 251, -.5), 9, WHITE_LIGHT)
    parts.append(flower.finish())
    beam = Part('central_reaction_beam', '直径16格贯穿反应池的惨粉光柱', group='core')
    rod(beam, (0, 16, -.5), (0, 330, -.5), 7.5, PINK_GLASS)
    rod(beam, (0, 16, -.5), (0, 330, -.5), 3, PINK_LIGHT)
    parts.append(beam.finish())
    return parts, dict(cube_edge=220, center=CORE.tolist(), single_corner_down=True, exact_vertex_xyz=vertices.tolist(), corner_displacement=1.035)
