import math

import numpy as np

from w12_common_20261116 import CENTER, GILDED, GOLD, HOT, LIGHT, VOID, WHITE, Part, rod
from w12_core_20261116 import cross_frame


RING_RADII = (25, 36, 47)
CAVITY_RADIUS = 55
LANCE_TIP_RADIUS = 55
LANCE_TAIL_RADIUS = 74


def cube_shell(points):
    q = points - CENTER
    near = np.maximum(np.maximum(q, -q - 1), 0)
    far = np.maximum(abs(q), abs(q + 1))
    return float(np.linalg.norm(near, axis=1).min()), float(np.linalg.norm(far, axis=1).max())


def lance(part, direction):
    normal = np.asarray(direction, float)
    normal /= np.linalg.norm(normal)
    rod(part, CENTER + normal * 62, CENTER + normal * LANCE_TAIL_RADIUS, 2.2, GOLD)
    rod(part, CENTER + normal * 62, CENTER + normal * LANCE_TAIL_RADIUS, .8, LIGHT)
    part.ring(CENTER + normal * 72, 4, 1.5, GILDED, normal=normal, depth=2)
    reference = np.array([0, 1, 0]) if abs(normal[1]) < .9 else np.array([1, 0, 0])
    u = np.cross(normal, reference)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    grid = np.arange(-4, 5)
    a, b = np.meshgrid(grid, grid, indexing='ij')
    for distance in np.arange(LANCE_TIP_RADIUS, 63, .5):
        radius = (distance - LANCE_TIP_RADIUS) * .42 + .35
        selected = a * a + b * b <= radius * radius
        points = CENTER + normal * distance + a[selected, None] * u + b[selected, None] * v
        part.points(points, LIGHT if distance < 58 else GOLD)
    return normal.tolist()


def build():
    r = math.sqrt(.5)
    parts = [
        cross_frame('grand_cross', '四层神恩主十字架', 120, 90, 1, np.eye(3)),
        cross_frame('secondary_cross_a', '斜置副十字架甲', 80, 60, .68,
                    [[0, 0, 1], [r, r, 0], [-r, r, 0]]),
        cross_frame('secondary_cross_b', '斜置副十字架乙', 80, 60, .68,
                    [[0, 0, 1], [r, -r, 0], [r, r, 0]]),
    ]
    for part in parts:
        keep = np.linalg.norm(part.p - CENTER, axis=1) >= CAVITY_RADIUS
        part.p, part.states = part.p[keep], part.states[keep]
        part.metadata.update(cavity_diameter=CAVITY_RADIUS * 2,
                             cavity_rule='保留整数格原点至核心中心距离大于等于55格的完整方块')
    for index, normal in enumerate(([1, 0, 0], [0, 1, 0], [0, 0, 1])):
        radius = RING_RADII[index]
        ring = Part(f'core_gyroscope_{index + 1}', f'分层陀螺约束环{index + 1}', section='core',
                    pivot=CENTER.tolist(), motion_axis=normal, motion_speed=(.055, -.047, .062)[index],
                    nominal_radius=radius, gold_radial_thickness=3, white_edge_radius=radius + 1)
        ring.ring(CENTER, radius, 3, GOLD, normal=normal, depth=3)
        ring.ring(CENTER, radius + 1, 1, WHITE, normal=normal, depth=4)
        n = np.asarray(normal, float)
        u, v = np.roll(n, 1), np.cross(n, np.roll(n, 1))
        for angle in np.arange(12) * math.pi / 6:
            ring.sphere(CENTER + (u * math.cos(angle) + v * math.sin(angle)) * (radius - 2), 2.2, LIGHT)
        parts.append(ring.finish())
    spears = Part('twelve_binding_lances', '十二外置神恩长矛', section='core', lance_count=12,
                  physical_tip_radius=LANCE_TIP_RADIUS, physical_tail_radius=LANCE_TAIL_RADIUS,
                  beam_inner_radius=15.9, beam_outer_radius=LANCE_TIP_RADIUS)
    phi, directions = (1 + math.sqrt(5)) / 2, []
    for a in (-1, 1):
        for b in (-phi, phi):
            for direction in ([0, a, b], [a, b, 0], [b, 0, a]):
                directions.append(lance(spears, direction))
    spears.metadata['beam_directions'] = directions
    parts.append(spears.finish())
    core = Part('white_singularity', '纯白奇点与黑金约束纹', section='core', radius=14,
                pivot=CENTER.tolist(), motion_axis=[.3, 1, .15], motion_speed=.095)
    q = np.mgrid[-14:15, -14:15, -14:15].reshape(3, -1).T
    q = q[np.linalg.norm(q, axis=1) <= 14]
    phase = np.abs(np.sin(np.arctan2(q[:, 2], q[:, 0]) * 3 + q[:, 1] * .14))
    for mask, state in ((phase >= .3, HOT), ((phase >= .15) & (phase < .3), GOLD), (phase < .15, VOID)):
        core.points(q[mask] + CENTER, state)
    parts.append(core.finish())
    notes = [
        'A2三环名义半径改为25、36、47格，分别保留绕自身X、Y、Z法线的原转速；各环金色径宽3格，白边外半径另加1格，12个灯节点位于名义半径减2格处。',
        '三十字架保留原臂长、深度及四层装甲，在中心采用整数格原点半径55格挖腔，名义直径110格；完整方块最近边界另以球壳数据计算。',
        '十二实体长矛沿原二十面体顶点方向外移，尖端名义半径55格、尾端74格，实体长度19格。球面至矛尖的约束由金色光束续接，光束属于动态特效；实体矛与旋转环保持连续净空。',
        '核心白洞保持名义半径14格与原整体转动。环间及对固定邻件的连续净空采用原始完整单位方块[p,p+(1,1,1)]的精确径向上下界计算。',
    ]
    return parts, notes
