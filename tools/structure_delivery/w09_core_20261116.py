import math

from PIL import Image, ImageDraw, ImageFont

from w09_common_20261116 import (
    ARMOR, CENTER, CRIMSON, CX, CZ, DARK, GILDED, GOLD, HOT, LIGHT,
    RED, VOID, Part, np, rod,
)


def sword():
    part = Part('sword_tower', '镇岳·倒插重装古剑塔', section='weapons',
                axis_blueprint_xyz=[220, 30, 500], nominal_height=260,
                nominal_blade_width=48, nominal_guard_width=90, tip_direction=[0, -1, 0])
    for y in range(30, 216):
        width = min(24, (y - 30) * .18)
        depth = min(9, 2 + width * .3)
        x, z = np.meshgrid(np.arange(-24, 25), np.arange(-9, 10), indexing='ij')
        keep = (abs(x) <= width) & (abs(z) <= depth * (1 - abs(x) / (width + 3)))
        q = np.c_[x[keep], np.full(keep.sum(), y), z[keep]]
        distance = width - abs(q[:, 0])
        state = np.full(len(q), DARK, np.uint8)
        state[(abs(q[:, 0]) >= 7) & (distance > 4)] = ARMOR
        state[(distance >= 3) & (distance <= 5)] = GOLD
        state[distance < 3] = RED
        state[(distance < 1) & (y % 14 < 4)] = HOT
        for material in np.unique(state):
            part.points(q[state == material] + [220, 0, 500], material)
    for y in range(82, 207, 22):
        part.box([216, y, 490], [224, y + 2, 510], GOLD)
        for z in (489, 510):
            part.box([218, y + 5, z], [222, y + 14, z], RED)
    part.box([203, 210, 489], [237, 219, 511], ARMOR)
    part.ring([220, 221, 500], 45, 10, ARMOR, depth=4)
    part.ring([220, 224, 500], 45, 2, GOLD, depth=2)
    part.ring([220, 221, 500], 35, 2, RED, depth=3)
    part.box([175, 219, 493], [265, 225, 507], DARK)
    for side in (-1, 1):
        part.hull([[220 + side * x, y, 500 + z] for x, y in
                   ((17, 219), (45, 221), (42, 233), (25, 228)) for z in (-7, 7)], GILDED)
        rod(part, [220 + side * 20, 226, 492], [220 + side * 41, 231, 492], 1.2, GOLD)
    rod(part, [220, 225, 500], [220, 282, 500], 7, DARK)
    for y in range(231, 281, 7):
        part.ring([220, y, 500], 7, 2, GOLD, depth=2)
    part.sphere([220, 285, 500], 5, GILDED)
    part.box([218, 282, 498], [222, 290, 502], RED)
    return part.finish()


def spear():
    tilt = math.radians(15)
    axis = np.array([-math.sin(tilt), math.cos(tilt), 0])
    u, v = np.array([math.cos(tilt), math.sin(tilt), 0]), np.array([0, 0, 1])
    origin = np.array([755, 30, 500], float)
    point = lambda t: origin + axis * t
    part = Part('spear_tower', '破军·赤金空心机械长枪', section='weapons',
                axis_start=origin.tolist(), axis_end=point(275).tolist(), axis_length=275,
                inward_tilt_degrees=15, shaft_outer_diameter=28, shaft_inner_diameter=20,
                tassel_strands=216, beam_origin=point(255).tolist())
    rod(part, point(0), point(218), 14, DARK, inner=10)
    for angle in np.arange(8) * math.pi / 4:
        offset = (u * math.cos(angle) + v * math.sin(angle)) * 12.4
        rod(part, point(1) + offset, point(217) + offset, 1.45, ARMOR)
    for phase in (0, math.pi):
        t = np.arange(0, 218.1, 1.4)
        theta = t * math.pi * 2 / 46 + phase
        q = origin + t[:, None] * axis + 12.4 * (
            np.cos(theta[:, None]) * u + np.sin(theta[:, None]) * v)
        for a, b in zip(q[:-1], q[1:]):
            rod(part, a, b, 1.45, GOLD)
    for t in range(8, 218, 29):
        part.ring(point(t), 14, 3, GILDED, normal=axis, depth=3)
        part.ring(point(t + 4), 14, 1, RED, normal=axis, depth=2)
    a, b = np.meshgrid(np.arange(-17, 18), np.arange(-7, 8), indexing='ij')
    for t in range(218, 276):
        width = max(0, 17 * (275 - t) / 57)
        depth = max(.1, 6 * (275 - t) / 57)
        keep = (abs(a) <= width) & (abs(b) <= depth * (1 - abs(a) / (width + 1)))
        aa, bb = a[keep], b[keep]
        q = point(t) + aa[:, None] * u + bb[:, None] * v
        distance = width - abs(aa)
        for selected, material in ((distance > 3, DARK),
                                   ((distance >= 1) & (distance <= 3), GOLD), (distance < 1, RED)):
            part.points(q[selected], material)
        part.points(q[(abs(aa) <= 1) & (abs(bb) >= max(0, depth - 1))], HOT)
    for index in range(216):
        angle = index * math.pi * 2 / 72
        layer = index // 72
        start = point(219 - layer * 3) + (u * math.cos(angle) + v * math.sin(angle)) * (16 + layer * 2)
        length = 35 + (index * 17 % 39)
        t = np.linspace(0, 1, length * 2)
        q = start + np.c_[-6 * t * t + np.sin(t * 5 + angle) * 1.4,
                          -length * t, np.sin(t * 4 + angle) * 2.2]
        part.points(q, CRIMSON)
        part.points(q[::10] + [0, 0, 1], RED)
    return part.finish()


def blade_case():
    part = Part('chain_blade_case', '缚神·展开链刃匣与蜂窝发射井', section='weapons',
                axis_blueprint_xyz=[CX, 30, 820], nominal_height=210,
                nominal_width=110, launch_wells=78, opening_direction=[0, 0, -1])
    part.box([443, 30, 838], [531, 240, 850], DARK)
    part.box([443, 30, 795], [531, 41, 850], ARMOR)
    for x in (443, 525):
        part.box([x, 38, 799], [x + 6, 237, 840], ARMOR)
        part.box([x + 1, 43, 796], [x + 4, 232, 798], RED)
    part.box([443, 234, 795], [531, 240, 849], GILDED)
    for side in (-1, 1):
        hinge, edge = CX + side * 44, CX + side * 55
        vertices = [[x, y, z + dz] for x, z in ((hinge, 820), (edge, 773))
                    for y in (41, 234) for dz in (-2, 2)]
        part.hull(vertices, DARK)
        for y in (45, 230):
            rod(part, [hinge, y, 817], [edge, y, 770], 1.5, GOLD)
        rod(part, [edge, 46, 771], [edge, 229, 771], 1.7, RED)
        for y in range(62, 225, 25):
            rod(part, [hinge, y, 817], [edge, y + 9, 770], 1.3, GILDED)
    x, y = np.meshgrid(np.arange(-8, 9), np.arange(-8, 9), indexing='ij')
    outer = (abs(y) <= 7.3 * math.sqrt(3) / 2) & (abs(x) + abs(y) / math.sqrt(3) <= 7.3)
    inner = (abs(y) <= 4.8 * math.sqrt(3) / 2) & (abs(x) + abs(y) / math.sqrt(3) <= 4.8)
    wall = np.c_[x[outer & ~inner], y[outer & ~inner]]
    aperture = np.c_[x[inner], y[inner]]
    for row in range(13):
        for column in range(6):
            center = np.array([448 + column * 14 + (row % 2) * 7, 49 + row * 14])
            for z in range(802, 838):
                part.points(np.c_[wall + center, np.full(len(wall), z)], GOLD if z <= 804 else ARMOR)
            part.points(np.c_[aperture + center, np.full(len(aperture), 838)], VOID)
            part.box([center[0] - 1, center[1] - 1, 837], [center[0] + 1, center[1] + 1, 837], RED)
    return part.finish()


def feather_template():
    part = Part('feather_template', '赤金机械羽刃')
    outline = ((45, 0), (61, -1.5), (75, -4.2), (87, -3),
               (90, 0), (85, 4.2), (74, 7.5), (60, 4.1))
    part.hull([[r, t, z] for r, t in outline for z in (-1.5, 1.5)], GOLD)
    part.hull([[r, t, z] for r, t in ((47, 0), (62, -1), (77, -3.2), (87, -1.7), (75, 1))
               for z in (-2, 2)], DARK)
    rod(part, [47, .2, 2], [84, 3.4, 2], .65, RED)
    for r in (60, 67, 74, 81):
        rod(part, [r, (r - 45) * .09, 2], [r + 3, (r - 45) * .09 + 3.5, 2], .6, GILDED)
    part.points([[45, 0, 0], [46, 0, 0]], HOT)
    return part.finish()


def feather_rings():
    leaf = feather_template()
    parts = []
    for index, normal in enumerate(([0, .42, .9075], [.78, .55, .3], [-.55, .4, .733])):
        normal = np.array(normal, float)
        normal /= np.linalg.norm(normal)
        u = np.cross(normal, [0, 1, 0])
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        part = Part(f'feather_ring_{index + 1}', f'千羽万象环{index + 1}', section='core',
                    pivot=CENTER.tolist(), motion_axis=normal.tolist(), ring_normal=normal.tolist(),
                    motion_speed=(.045, -.037, .029)[index], feathers=40,
                    feather_nominal_length=45, nominal_inner_radius=45, nominal_outer_radius=90)
        part.ring(CENTER, 88, 2, ARMOR, normal=normal, depth=3)
        for number in range(40):
            angle = number * math.pi / 20 + index * math.pi / 60
            radial = u * math.cos(angle) + v * math.sin(angle)
            tangent = -u * math.sin(angle) + v * math.cos(angle)
            q = CENTER + leaf.p[:, :1] * radial + leaf.p[:, 1:2] * tangent + leaf.p[:, 2:] * normal
            for state in np.unique(leaf.states):
                part.points(q[leaf.states == state], int(state))
        parts.append(part.finish())
    return parts


def cognitive_core():
    cage = Part('crimson_octahedron', '破碎虚空·红玻璃八面体囚笼', section='core',
                center=CENTER.tolist(), nominal_diameter=90, glass_shell_taxicab_thickness=3)
    q = np.mgrid[-45:46, -45:46, -45:46].reshape(3, -1).T
    distance = abs(q).sum(axis=1)
    q = q[(distance >= 42) & (distance <= 45)]
    edge = abs(q).min(axis=1)
    for selected, state in ((edge > 2, CRIMSON), ((edge > 0) & (edge <= 2), ARMOR), (edge == 0, GOLD)):
        cage.points(q[selected] + CENTER, state)
    route = np.array([[7, 27, 11], [7, 17, 21], [15, 9, 21], [15, 20, 10], [24, 11, 10]], float)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                line = CENTER + route * [sx, sy, sz]
                for a, b in zip(line[:-1], line[1:]):
                    rod(cage, a, b, .65, LIGHT)
    glyphs = ('识', '破', '灭', '万', '象', '识', '破', '灭')
    font = ImageFont.truetype('C:/Windows/Fonts/simkai.ttf', 18)
    for index, signs in enumerate(np.array(np.meshgrid((-1, 1), (-1, 1), (-1, 1))).reshape(3, -1).T):
        image = Image.new('1', (18, 18))
        draw = ImageDraw.Draw(image)
        left, top, right, bottom = draw.textbbox((0, 0), glyphs[index], font=font)
        draw.text(((18 - right + left) / 2 - left, (18 - bottom + top) / 2 - top),
                  glyphs[index], font=font, fill=1)
        pixels = np.argwhere(np.asarray(image))
        normal = signs / math.sqrt(3)
        u = np.cross([0, 1, 0], normal)
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        q = signs * 15 + (pixels[:, 1:2] - 8.5) * u - (pixels[:, :1] - 8.5) * v
        local = np.rint(q * signs).astype(int)
        local[:, 1] = 45 - local[:, 0] - local[:, 2]
        cage.points(CENTER + local * signs, LIGHT)
    cage.metadata.update(surface_glyphs=list(glyphs), glyph_pixel_grid=[18, 18], glyph_font='楷体')
    core = Part('sentience_singularity', '真我·吸光黑球与赤红意识内核', section='core',
                center=CENTER.tolist(), nominal_diameter=40, inner_core_diameter=26)
    core.sphere(CENTER, 20, DARK)
    core.sphere(CENTER, 13, RED)
    core.sphere(CENTER, 6, HOT)
    return [cage.finish(), core.finish()]


def build():
    parts = [sword(), spear(), blade_case()] + feather_rings() + cognitive_core()
    notes = [
        '左剑主轴位于(220,Y,500)，倒插剑尖Y30，护手环中心Y221，握柄与柄首至Y290；48格刃宽与90格护手按连续跨度取样，包含两端整数原点后最多多一格。维护环外半径45、内半径35，只有护手横梁及四处连接占据环内部分区域。',
        '右枪以(755,30,500)为底端，轴向长275，向中心方向倾15°，顶端约(683.825,295.630,500)；原文把275同时写为高度，本稿按轴长解释并保留实际倾斜端点。杆体外径28、空心内径20，双股暗金螺旋节距46；刃头始于轴向218，216条猩红透明玻璃流苏长度35至73格，全部为整数方块。',
        '后匣以(487,30,820)为定位轴，主体至Y240，黑红匣体与前开双盖按名义110格宽取样，边缘杆件厚度计入实际包围盒；前向井口Z802，井底Z838，13排6列共78个真实空心六角发射井。未给定的纵深、开盖角度和内部蜂窝间距为本稿取样。',
        '三道千羽万象环共同球心为(487,220,500)，各40片，共120片；单片沿半径45至90布置，名义长45格，尖端朝内，赤金叶身配黑色羽脊与猩红槽。支撑分节环半径88，羽刃厚度、侧弯、倾角和转速为本稿取样，整数取整与方块实体厚度计入实际包围盒。',
        '三羽环沿各自倾斜法线正反转动，motion_axis、ring_normal、pivot和motion_speed保存在各构件元数据；三环采用共同半径，原文交错转动会产生环间穿插，原位保留，未在本稿提前改半径或移位。',
        '核心八面体采用|x|+|y|+|z|在42至45之间的猩红透明方块壳，90格为顶点连续跨度，包含端点为91格原点跨度；黑金边框和发光电路位于同一表面，线宽及图案为本稿取样。内部名义直径40的吸光黑球包裹26格赤红内核与12格炽红中心。',
        '八面体八个三角面中心分别拼出识、破、灭、万、象、识、破、灭，采用系统楷体18×18单色像素取样，通过面内正交基映射到|x|+|y|+|z|=45的整数格表面，由发光方块构成可读汉字；原文未提供古篆笔形，本稿不把楷体取样称为原作篆字。',
        '金红莫比乌斯、水墨冲击和对心激光交由独立网页特效；本模块只生成武器与核心整数格构件，未加入实体光带。三兵、核心与其它原案构件的交叠保留供整体记录。',
    ]
    return parts, notes
