from itertools import combinations

from w10_common_20261116 import *


def asteroid_belt(index, radius, count, sign):
    axis = np.array([0, math.cos(math.radians(25)), sign * math.sin(math.radians(25))])
    center = np.array([0, 190, 0])
    tangent = np.cross(axis, [1, 0, 0])
    part = Part(f'asteroid_belt_0{index}', f'第{index}重碎星带', section='core', pivot=center.tolist(),
        motion_axis=axis.tolist(), motion_speed=.025 if index == 1 else -.02,
        radius=radius, tilt_degrees=25, rock_count=count, source='双层半径220/310、倾角25度陨石环')
    part.ring(center, radius + 2, 5, PURPLE, normal=axis, depth=5)
    for i in range(count):
        angle = i * math.tau / count + .025 * math.sin(i * 7.1)
        radial = np.array([math.cos(angle), 0, 0]) + tangent * math.sin(angle)
        position = center + radial * (radius + 6 * math.sin(i * 2.3))
        rock_radius = 7.5 + 12.5 * (.5 + .5 * math.sin(i * 3.7 + index))
        extent = math.ceil(rock_radius * 1.15)
        q = np.arange(-extent, extent + 1)
        x, y, z = np.meshgrid(q, q, q, indexing='ij')
        points = np.c_[x.ravel(), y.ravel(), z.ravel()]
        distance = np.linalg.norm(points * [1, 1.09, .93], axis=1)
        theta = np.arctan2(points[:, 2], points[:, 0])
        shape = rock_radius * (.88 + .065 * np.sin(theta * 3 + i) + .045 * np.cos(points[:, 1] * .31 + i))
        inside = distance <= shape
        shell = inside & (distance > shape - 2.2)
        cracks = shell & (np.abs(np.sin(theta * 4.2 + points[:, 1] * .11 + i)) < .115)
        part.points(points[inside] + position, STONE)
        part.points(points[shell] + position, ARMOR)
        part.points(points[shell & ((points[:, 0] + points[:, 1] * 3 + i) % 13 < 2)] + position, GILDED)
        part.points(points[cracks] + position, AMBER)
        part.points(points[cracks & ((points[:, 1] + i) % 5 == 0)] + position, LIGHT)
    return part.finish()


def cage(radius=80):
    phi = (1 + math.sqrt(5)) / 2
    vertices = np.array([(0, a, b * phi) for a in (-1, 1) for b in (-1, 1)]
        + [(a, b * phi, 0) for a in (-1, 1) for b in (-1, 1)]
        + [(b * phi, 0, a) for a in (-1, 1) for b in (-1, 1)], float)
    vertices *= radius / np.linalg.norm(vertices[0])
    part = Part('golden_icosahedron_cage', '黄金正二十面体拘束笼', section='core',
        source=f'中心(0,222,0)、外接球直径{radius * 2:g}、金属梁宽7')
    edge = min(np.linalg.norm(vertices[a] - vertices[b]) for a, b in combinations(range(12), 2))
    for a, b in combinations(range(12), 2):
        if np.linalg.norm(vertices[a] - vertices[b]) < edge + .01:
            rod(part, vertices[a] + CENTER, vertices[b] + CENTER, 3.5, GOLD)
            rod(part, vertices[a] + CENTER, vertices[b] + CENTER, .8, LIGHT)
    for vertex in vertices:
        part.sphere(vertex + CENTER, 6, GOLD)
        part.sphere(vertex + CENTER, 3, LIGHT)
    return part.finish()


def accretion():
    part = Part('core_accretion_disk', '黄金视界螺旋吸积盘', section='core', pivot=CENTER.tolist(),
        motion_axis=[0, 1, 0], motion_speed=.015, source='Y222、直径130、外暗红至内纯白')
    z, x = np.mgrid[-65:66, -65:66]
    radius = np.hypot(x, z)
    angle = np.arctan2(z, x)
    spiral = np.mod(angle + radius * .115, math.tau / 4) / (math.tau / 4)
    thickness = 1 + np.floor(8 * (1 - radius / 65)).astype(int)
    area = (radius >= 24) & (radius <= 65) & ((spiral < .66) | (radius < 34))
    for dy in range(-9, 10):
        selected = area & (abs(dy) <= thickness)
        points = np.c_[x[selected], np.full(selected.sum(), 222 + dy), z[selected]]
        part.points(points, RED)
        amber = selected & (radius <= 53)
        part.points(np.c_[x[amber], np.full(amber.sum(), 222 + dy), z[amber]], GLASS)
        white = selected & (radius <= 35)
        part.points(np.c_[x[white], np.full(white.sum(), 222 + dy), z[white]], HOT)
        streak = selected & (spiral < .14) & (radius > 35)
        part.points(np.c_[x[streak], np.full(streak.sum(), 222 + dy), z[streak]], LIGHT)
    return part.finish()


def black_hole():
    part = Part('core_void_horizon', '坠星纯黑事件视界', section='core', visual='void',
        source='中心(0,222,0)、直径50纯黑球体')
    part.sphere(CENTER, 25, DARK)
    return part.finish()


def crystal(index, y):
    part = Part(f'core_polar_crystal_{index}', '上极律者拘束晶' if index == 1 else '下极律者拘束晶',
        section='core', source=f'中心(0,{y},0)、直径30暗金八面体')
    center = np.array([0, y, 0])
    vertices = np.array([[15, 0, 0], [-15, 0, 0], [0, 15, 0], [0, -15, 0], [0, 0, 15], [0, 0, -15]])
    part.hull(vertices + center, GOLD)
    part.hull(vertices * .72 + center, AMBER)
    for a, b in combinations(range(6), 2):
        if np.linalg.norm(vertices[a] - vertices[b]) < 25:
            rod(part, vertices[a] + center, vertices[b] + center, 1, GOLD)
    return part.finish()


def build():
    parts = [asteroid_belt(1, 220, 28, 1), asteroid_belt(2, 310, 36, -1), cage(),
        accretion(), black_hole(), crystal(1, 250), crystal(2, 194)]
    notes = [
        '双碎星环以原文Y120..260中点190为共同中心，保留半径220/310和25度倾角；实际垂向范围由完整实体计算，超过120..260的部分照实保留。',
        '原文未给陨石精确数量与碎片表面坐标；内28、外36块按15..40名义直径取样，规则裂纹属于本项目方块化设计。',
        '黄金拘束笼选择原文允许的正二十面体，外接球直径160，梁宽7，节点接头半径6；实际梁体包围盒另计。',
        '吸积盘为直径130、四臂螺旋实体，中心厚边缘薄；黑洞与两极晶体按原坐标嵌接，嵌入部分保留分构件记录。',
        '双陨石环逆向转动、吸积盘慢转、纯黑井面细纹、引力透镜背景、金紫光束、相对论喷流及十秒冲击波均为网页演示；NBT只记录参考姿态的真实方块。',
    ]
    return parts, notes
