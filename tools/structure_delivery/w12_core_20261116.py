import math

import numpy as np

from w12_common_20261116 import (
    ARMOR, CENTER, CX, CZ, GILDED, GOLD, HOT, LIGHT, VOID, WHITE,
    Part, rod, wall_z,
)


def transformed(part, basis):
    result = part.finish()
    points = np.rint(result.p @ np.asarray(basis) + CENTER).astype(np.int32)
    keep = np.linalg.norm(points - CENTER, axis=1) >= 35
    points, states = points[keep], result.states[keep]
    low = points.min(0)
    size = points.max(0) - low + 1
    q = points - low
    keys = (q[:, 1] * size[2] + q[:, 2]) * size[0] + q[:, 0]
    _, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(keys) - chosen - 1
    result.p, result.states = points[chosen], states[chosen]
    return result


def cross_frame(name, label, half_height, half_width, scale, basis):
    part = Part(name, label, section='core', layers=4, local_height=half_height * 2,
                local_width=half_width * 2, cavity_diameter=70)
    depth = 9 * scale
    part.box([-8 * scale, -half_height, -depth], [8 * scale, half_height, depth], VOID)
    part.box([-half_width, -8 * scale, -depth], [half_width, 8 * scale, depth], VOID)
    for direction, transverse, length in (
        (np.array([0, 1, 0]), np.array([1, 0, 0]), half_height),
        (np.array([0, -1, 0]), np.array([1, 0, 0]), half_height),
        (np.array([1, 0, 0]), np.array([0, 1, 0]), half_width),
        (np.array([-1, 0, 0]), np.array([0, 1, 0]), half_width),
    ):
        for side in (-1, 1):
            for z in (-9 * scale, 9 * scale):
                shift = transverse * side * 7 * scale + [0, 0, z]
                rod(part, direction * 33 + shift, direction * (length - 3) + shift, 1.6 * scale, LIGHT)
        for layer, z in enumerate((-24 * scale, -13 * scale, 13 * scale, 24 * scale)):
            for index, start in enumerate(np.arange(36, length - 6, 18 * scale)):
                end = min(start + 13 * scale, length - 3)
                spread = (15 - 4 * start / length) * scale
                for side in (-1, 1):
                    a = direction * start + transverse * side * spread + [0, 0, z]
                    b = direction * end + transverse * side * spread + [0, 0, z]
                    rod(part, a, b, 3.3 * scale, WHITE)
                    rod(part, a - transverse * side * 3 * scale,
                        b - transverse * side * 3 * scale, 1.15 * scale, GOLD)
                    rod(part, a, a - np.array([0, 0, z * .5]), 1.8 * scale, ARMOR)
                if index % 2 == layer % 2:
                    a = direction * (end - 2 * scale) + [0, 0, z]
                    rod(part, a - transverse * spread, a + transverse * spread, 1.5 * scale, GILDED)
            for side in (-1, 1):
                a = direction * (length - 17 * scale) + transverse * side * 13 * scale + [0, 0, z]
                b = direction * (length - 3) + [0, 0, z * .45]
                rod(part, a, b, 2.7 * scale, WHITE)
        for distance in np.arange(47, length - 10, 24 * scale):
            part.ring(direction * distance, 13 * scale, 2.2 * scale, WHITE,
                      normal=direction, depth=2 * scale)
        rod(part, direction * 35, direction * (length - 1), 1.5 * scale, GOLD)
    return transformed(part, basis)


def lance(part, direction):
    normal = np.asarray(direction, float)
    normal /= np.linalg.norm(normal)
    rod(part, CENTER + normal * 39, CENTER + normal * 23, 2.2, GOLD)
    rod(part, CENTER + normal * 39, CENTER + normal * 23, .8, LIGHT)
    part.ring(CENTER + normal * 38, 5, 1.5, GILDED, normal=normal, depth=2)
    reference = np.array([0, 1, 0]) if abs(normal[1]) < .9 else np.array([1, 0, 0])
    u = np.cross(normal, reference)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    grid = np.arange(-5, 6)
    a, b = np.meshgrid(grid, grid, indexing='ij')
    for distance in np.arange(14, 25, .65):
        radius = (distance - 14) * .44 + .4
        selected = a * a + b * b <= radius * radius
        points = CENTER + normal * distance + a[selected, None] * u + b[selected, None] * v
        part.points(points, GOLD if distance > 18 else LIGHT)


def chain_ring_samples():
    cap = np.linspace(-math.pi / 2, math.pi / 2, 29)
    right = np.c_[6.7 + 3.8 * np.cos(cap), 3.8 * np.sin(cap)]
    left = np.c_[-6.7 - 3.8 * np.cos(cap), -3.8 * np.sin(cap)]
    top = np.c_[np.linspace(6.7, -6.7, 29), np.full(29, 3.8)]
    bottom = np.c_[np.linspace(-6.7, 6.7, 29), np.full(29, -3.8)]
    outline = np.vstack([right, top, left, bottom])
    tangent = np.roll(outline, -1, axis=0) - np.roll(outline, 1, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    outward = np.c_[tangent[:, 1], -tangent[:, 0]]
    offsets = np.array([(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)])
    return outline, outward, offsets


def chain(name, label, start, end, samples, **metadata):
    start, end = np.asarray(start, float), np.asarray(end, float)
    length = np.linalg.norm(end - start)
    count = math.ceil((length - 25) / 17) + 1
    spacing = (length - 25) / (count - 1)
    part = Part(name, label, section='chains', start_blueprint_xyz=np.rint(start).astype(int).tolist(),
                end_blueprint_xyz=np.rint(end).astype(int).tolist(), chain_links=count,
                link_length=25, link_width=12, center_spacing=float(spacing), **metadata)
    outline, outward, offsets = samples
    for index in range(count):
        fraction = (12.5 + index * spacing) / length
        center = start * (1 - fraction) + end * fraction + [0, -6 * math.sin(math.pi * fraction), 0]
        axis = end - start + [0, -6 * math.pi * math.cos(math.pi * fraction), 0]
        axis /= np.linalg.norm(axis)
        lateral = np.cross(axis, [0, 1, 0])
        lateral /= np.linalg.norm(lateral)
        normal = np.cross(axis, lateral)
        across, thickness = (lateral, normal) if index % 2 == 0 else (normal, -lateral)
        points = center + outline[:, :1] * axis + outline[:, 1:] * across
        radial = outward[:, :1] * axis + outward[:, 1:] * across
        for a, b in offsets:
            state = GILDED if b == -1 else LIGHT if a == 0 and b == 1 else GOLD
            part.points(points + a * radial + b * thickness, state)
    return part.finish()


def lower_anchors():
    corners = np.array([[-309, -381], [309, -381], [489, -201], [489, 201],
                        [309, 381], [-309, 381], [-489, 201], [-489, -201]], float)
    anchors, number = [], 1
    for edge in range(8):
        for t in ((1 / 8, 3 / 8, 5 / 8, 7 / 8) if edge % 2 == 0 else (1 / 3, 2 / 3)):
            x, z = corners[edge] * (1 - t) + corners[(edge + 1) % 8] * t
            direction = np.array([x, 0, z]) / math.hypot(x, z)
            if edge % 2 == 0:
                anchors.append((number, np.array([CX + x, 70, CZ + z]) - direction * 70))
            number += 1
    return anchors


def build():
    r = math.sqrt(.5)
    parts = [
        cross_frame('grand_cross', '四层神恩主十字架', 120, 90, 1, np.eye(3)),
        cross_frame('secondary_cross_a', '斜置副十字架甲', 80, 60, .68,
                    [[0, 0, 1], [r, r, 0], [-r, r, 0]]),
        cross_frame('secondary_cross_b', '斜置副十字架乙', 80, 60, .68,
                    [[0, 0, 1], [r, -r, 0], [r, r, 0]]),
    ]
    for index, normal in enumerate(([1, 0, 0], [0, 1, 0], [0, 0, 1])):
        ring = Part(f'core_gyroscope_{index + 1}', f'奇点陀螺约束环{index + 1}', section='core',
                    pivot=CENTER.tolist(), motion_axis=normal, motion_speed=(.055, -.047, .062)[index])
        ring.ring(CENTER, 39, 4, GOLD, normal=normal, depth=3)
        ring.ring(CENTER, 40, 1, WHITE, normal=normal, depth=4)
        n = np.asarray(normal, float)
        u = np.roll(n, 1)
        v = np.cross(n, u)
        for angle in np.arange(12) * math.pi / 6:
            point = CENTER + (u * math.cos(angle) + v * math.sin(angle)) * 37
            ring.sphere(point, 2.2, LIGHT)
        parts.append(ring.finish())
    spears = Part('twelve_binding_lances', '十二神恩长矛', section='core', lance_count=12)
    phi = (1 + math.sqrt(5)) / 2
    for a in (-1, 1):
        for b in (-phi, phi):
            for direction in ([0, a, b], [a, b, 0], [b, 0, a]):
                lance(spears, direction)
    parts.append(spears.finish())
    core = Part('white_singularity', '纯白奇点与黑金约束纹', section='core', radius=14,
                pivot=CENTER.tolist(), motion_axis=[.3, 1, .15], motion_speed=.095)
    q = np.mgrid[-14:15, -14:15, -14:15].reshape(3, -1).T
    q = q[np.linalg.norm(q, axis=1) <= 14]
    phase = np.abs(np.sin(np.arctan2(q[:, 2], q[:, 0]) * 3 + q[:, 1] * .14))
    for mask, state in ((phase >= .3, HOT), ((phase >= .15) & (phase < .3), GOLD), (phase < .15, VOID)):
        core.points(q[mask] + CENTER, state)
    parts.append(core.finish())
    samples = chain_ring_samples()
    ends = [CENTER + q for q in ([0, 120, 0], [-90, 0, 0], [0, -120, 0], [90, 0, 0],
                                [0, 0, -36], [0, 0, 36], [-28, 28, 0], [28, -28, 0])]
    for wall_index, side in enumerate((-1, 1)):
        for index, x in enumerate((140, 250, 360, 470, 592, 702, 812, 922)):
            start = [x, 258, wall_z(x, side)]
            end = ends[index] if side < 0 else ends[7 - index]
            number = wall_index * 8 + index + 1
            parts.append(chain(f'binding_chain_{number:02}', f'墙顶戒律锁链{number:02}', start, end,
                               samples, source='约束壁顶端'))
    for index, (anchor_number, start) in enumerate(lower_anchors()):
        end = ends[(index + 2) % len(ends)]
        number = index + 17
        parts.append(chain(f'binding_chain_{number:02}', f'锚桩戒律锁链{number:02}', start, end,
                           samples, source='断罪液压锚桩', anchor_number=anchor_number))
    notes = [
        '主十字架中心(531,180,423)，主平面XY，轴向端点Y60..300、X441..621；整数端点包含241层和181列。四层外骨骼位于局部深度-24、-13、13、24，板条厚度与18格分节为本稿取样。',
        '两个副十字架各高160、横臂120，局部长轴分别沿(1,1,0)及(1,-1,0)倾45°，横轴沿Z；与主XY平面构成三组正交平面。局部160格端点取样后旋转并四舍五入为整数格，副十字交叉处保留。',
        '三十字架共同挖除距核心中心不足35格的全部方块，形成直径70球腔；内设三道名义半径39的金色陀螺环、十二个二十面体顶点方向的长矛，以及名义半径14的纯白黑金能量球。环和球的网页转动仅作演示。',
        '32条锁链均由真实整数方块链环组成，16条始于两墙顶端，X140/250/360/470/592/702/812/922，Y258，Z跟随墙轴线；其余16条接入24桩中的直边16桩，在各桩Y70的轴心取锚点。各链端点与链节数保存在构件元数据。',
        '链环外长约25、外宽约12，截面采用3×3整数近圆，黑金背边、金色主体与发光金脊；相邻链环法向交替90°，中心距按全链长度取不超过17格，弧线最大下垂6格。首末环外端对准锚点，端环厚度与整数取整会形成额外包围盒。',
        '锁链终点在主十字上下端、左右端及核心前后约束环、腰部两斜向连接点之间分配；精确分配、未给出的装甲厚度、间隔与锚接形式均为本稿取样，保留与其它原案构件的空间交叠。',
    ]
    return parts, notes
