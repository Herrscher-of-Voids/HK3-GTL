from w08_common_20261116 import *


SLOPE = 1 / math.tan(math.radians(75))
SWORD_UP = np.array([0., math.sin(math.radians(75)), math.cos(math.radians(75))])
SWORD_FRONT = np.array([0., -SWORD_UP[2], SWORD_UP[1]])


def axis(y):
    return np.array([CX, y, CZ + y * SLOPE], float)


def blade_width(y):
    return float(np.interp(y, [0, 40, 85, 145, 230, 260], [0, 9, 43, 69.5, 58, 46]))


def sword_blades():
    p = Part('sword_plasma_blades', '劫灭双侧渐变等离子刃与贯地剑尖',
             source='二·1：宽140格，Y40..260镂空重型剑身、白黄橙红渐变外刃；Y0..40剑尖',
             sampling='最大连续宽度140格，以X=489为中心。外刃保留双锋分离的开口，剑尖逐层收至Y0。')
    for y in range(261):
        width = blade_width(y)
        center = axis(y)
        for side in (-1, 1):
            for distance, state, depth in [(0, LIGHT, 2), (3, YELLOW, 3), (6, ORANGE, 4), (9, RED_GLASS, 5), (12, DARK, 6)]:
                outside = width - distance
                inside = max(0, outside - 2)
                if outside < 0:
                    continue
                xx, zz = np.meshgrid(np.arange(math.ceil(inside), math.floor(outside) + 1), np.arange(-depth, depth + 1), indexing='ij')
                p.points(np.c_[CX + side * xx.ravel(), np.full(xx.size, y), center[2] + zz.ravel()], state)
    return p.finish()


def sword_truss():
    p = Part('sword_open_blackgold_truss', '开放黑金剑脊、双侧桁架与对角撑',
             source='二·1：镂空重型桁架剑身，暴露的机械骨架',
             sampling='剑身沿75度主轴，Y40..260。双侧开口桁架与内部交叉拉撑独立于等离子刃。')
    for x in (-13, 13):
        for z in (-12, 12):
            rod(p, axis(42) + [x, 0, z], axis(260) + [x, 0, z], 3.5, DARK)
            rod(p, axis(42) + [x, 0, z - 1], axis(260) + [x, 0, z - 1], 1.5, GOLD)
    for y0 in range(55, 240, 30):
        y1 = y0 + 24
        w0, w1 = blade_width(y0) - 16, blade_width(y1) - 16
        for z in (-10, 10):
            rod(p, axis(y0) + [-w0, 0, z], axis(y0) + [w0, 0, z], 3, DARK)
            rod(p, axis(y0) + [-w0, 0, z], axis(y1) + [w1, 0, z], 2.3, GOLD)
            rod(p, axis(y0) + [w0, 0, z], axis(y1) + [-w1, 0, z], 2.3, METAL)
        for side in (-1, 1):
            rod(p, axis(y0) + [side * w0, 0, -9], axis(y1) + [side * w1, 0, -9], 3, DARK)
    return p.finish()


def sword_machinery():
    p = Part('sword_pistons_coils_waterfall', '剑脊活塞阵列、磁场线圈与中子星物质瀑布',
             source='二·1：超大型活塞阵列、旋转磁场线圈、向下的液态中子星物质瀑布',
             sampling='六层成对侧活塞与六道轴向磁环。液态物质用白炽、苍蓝方块薄层表示，剑脊磁环与物质瀑布当前为静态方块。')
    for index, y in enumerate(range(65, 246, 35)):
        center = axis(y)
        for side in (-1, 1):
            base = center + [side * 31, 0, 0]
            end = center + [side * 13, 0, 0]
            rod(p, base, end, 5.5, DARK)
            rod(p, base, (base + end) / 2, 4, METAL)
            rod(p, base + [0, 0, -5], end + [0, 0, -5], 1.1, GOLD)
        p.ring(center, 20, 3, GOLD, normal=SWORD_UP, depth=5)
        p.ring(center + SWORD_UP * 3, 18, 2, COOL, normal=SWORD_UP, depth=2)
    for y in range(42, 260):
        center = axis(y)
        width = 6 if y % 22 < 15 else 4
        xx, zz = np.mgrid[-width:width + 1, -2:3]
        p.points(np.c_[CX + xx.ravel(), np.full(xx.size, y), center[2] + zz.ravel()], COOL)
        p.points(np.c_[CX + np.arange(-2, 3), np.full(5, y), np.full(5, center[2] - 3)], LIGHT)
    return p.finish()


def sword_guard():
    p = Part('sword_whitegold_guard_and_grip', '三百格白金燕尾护手与黑金剑柄',
             source='二·1：Y260..338白陶瓷暗金护手、展开300格',
             nominal_guard_width=300,
             sampling='护手为上扬的双层白金楔形，横向连续宽300格；长柄沿同一75度轴抬至Y338。')
    for side in (-1, 1):
        profiles = [
            (DARK, [(0, 263), (64, 266), (145, 289), (150, 299), (124, 291), (52, 280), (0, 283)], 11),
            (ARMOR, [(0, 269), (66, 273), (150, 301), (140, 303), (65, 286), (0, 284)], 8),
        ]
        for state, profile, depth in profiles:
            front = [[CX + side * x, y, axis(y)[2] - depth] for x, y in profile]
            back = [[CX + side * x, y, axis(y)[2] + depth] for x, y in profile]
            p.hull(front + back, state)
        rod(p, axis(283), axis(300) + [side * 145, 0, 0], 2, GOLD)
        rod(p, axis(275) + [side * 35, 0, -10], axis(294) + [side * 121, 0, -10], 2, COOL)
        for x in (48, 82, 116):
            y = 274 + x * .12
            rod(p, axis(y) + [side * x, -5, -10], axis(y) + [side * x, 5, -10], 2, GOLD)
    for y in range(298, 339):
        c = axis(y)
        radius = 11 if y < 327 else 15 - (y - 327) * .6
        xx, zz = np.mgrid[-15:16, -15:16]
        mask = xx * xx + zz * zz <= radius * radius
        state = GOLD if y % 9 < 2 else DARK
        p.points(np.c_[CX + xx[mask], np.full(mask.sum(), y), c[2] + zz[mask]], state)
        if y % 9 >= 2:
            p.points([[CX - radius + 1, y, c[2]], [CX + radius - 1, y, c[2]]], ARMOR)
    return p.finish()


def sword_octahedral_core():
    c = axis(280)
    p = Part('sword_crimson_octahedral_core', '护手四十格赤红八面律者核心',
             source='二·1：护手中央直径40格高发光透明八面体',
             nominal_diameter=40,
             sampling='以剑轴Y280点为中心，赤红玻璃外壳与白黄热核分层占格。')
    xx, zz = np.mgrid[-20:21, -20:21]
    for y in range(-20, 21):
        score = np.abs(xx) + abs(y) + np.abs(zz)
        for mask, state in [(score <= 20, RED_GLASS), (score <= 15, RED), (score <= 9, ORANGE), (score <= 4, LIGHT)]:
            p.points(np.c_[CX + xx[mask], np.full(mask.sum(), c[1] + y), c[2] + zz[mask]], state)
    return p.finish()


def sword_clamp(index):
    theta = index * math.tau / 6
    radial = np.array([math.cos(theta), 0., math.sin(theta)])
    c = axis(280)
    p = Part(f'sword_core_hydraulic_clamp_{index + 1:02d}', f'赤核黑金液压钳 {index + 1}',
             source='二·1：六根粗壮黑色机械液压臂钳住核心', count_in_group=6)
    outer, middle, tip = c + radial * 43, c + radial * 30 + [0, 5, 0], c + radial * 17
    rod(p, outer, middle, 4.5, DARK)
    rod(p, middle, tip, 3, METAL)
    rod(p, middle + [0, 0, -3], tip + [0, 0, -3], 1.2, GOLD)
    p.sphere(outer, 5.5, DARK)
    p.sphere(tip, 3.5, DARK)
    return p.finish()


def star_body(radius=80):
    p = Part('star_compressed_supergiant', '白炽核、黄热层与赤红岩浆恒星',
             source='二·2：恒星直径160，白核心、亮黄、橙红岩浆与暗红黑曜石碎块',
             nominal_diameter=radius * 2,
             sampling='恒星按名义直径连续半径离散化，完整保留球面端点。角向连续热斑与暗壳碎块使外表呈非均匀星面；纯白与黄色内层可用剖切查看。')
    scale = radius / 80
    xx, zz = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    phi = np.arctan2(zz, xx)
    radial_xz = xx * xx + zz * zz
    for yy in range(-radius, radius + 1):
        r = np.sqrt(radial_xz + yy * yy)
        latitude = np.arctan2(yy, np.sqrt(radial_xz) + .001)
        for lo, hi, state in [(0, 28, LIGHT), (28, 48, YELLOW), (48, 66, ORANGE), (66, 80, MAGMA)]:
            lo, hi = lo * scale, hi * scale
            mask = (r > lo) & (r <= hi)
            p.points(np.c_[CX + xx[mask], 150 + np.full(mask.sum(), yy), CZ + zz[mask]], state)
        patches = (np.sin(phi * 5 + latitude * 2) + np.cos(latitude * 7 - phi * 2)) > 1.15
        mask = (r > 75 * scale) & (r <= radius) & patches
        p.points(np.c_[CX + xx[mask], 150 + np.full(mask.sum(), yy), CZ + zz[mask]], RED)
        plates = patches & (np.sin(phi * 3 - latitude * 4) > .5)
        mask = (r > 78 * scale) & (r <= radius) & plates
        p.points(np.c_[CX + xx[mask], 150 + np.full(mask.sum(), yy), CZ + zz[mask]], VOID)
    p.points([[CX, 150, CZ]], LIGHT)
    return p.finish()


def star_prominence(index):
    theta = index * math.tau / 12
    latitude = math.radians([-30, 12, 36, -12][index % 4])
    radial = np.array([math.cos(latitude) * math.cos(theta), math.sin(latitude), math.cos(latitude) * math.sin(theta)])
    tangent = np.array([-math.sin(theta), 0., math.cos(theta)])
    p = Part(f'star_prominence_{index + 1:02d}', f'六十格卷曲日珥 {index + 1}',
             source='二·2：向外卷曲、长达60格的立体火焰触须', radial_extension=60,
             sampling='十二条日珥，以恒星表面为起点沿径向外伸60格并回卷；外红中橙、内层亮黄。')
    curve = []
    for t in np.linspace(0, 1, 52):
        r = 78 + 60 * math.sin(math.pi * t)
        curve.append(STAR_CENTER + r * radial + 35 * t * tangent)
    for a, b in zip(curve[:-1], curve[1:]):
        rod(p, a, b, 4, RED_GLASS)
        rod(p, a, b, 2.6, ORANGE)
        rod(p, a, b, 1.2, YELLOW)
    return p.finish()


def ring_basis(index):
    return [
        (np.array([0., 1, 0]), np.array([1., 0, 0]), np.array([0., 0, 1])),
        (np.array([1., 0, 0]), np.array([0., 1, 0]), np.array([0., 0, 1])),
        (np.array([0., 0, 1]), np.array([1., 0, 0]), np.array([0., 1, 0])),
    ][index]


def star_ring(index, radial_offset=0):
    normal, u, v = ring_basis(index)
    p = Part(f'star_ring_{index + 1:02d}', f'第{index + 1}道白金圣痕拘束环',
             source='二·2：互相垂直的三道直径240、厚18白金装甲环、冷却管与向内激光器',
             nominal_diameter=2 * (120 + radial_offset), radial_thickness=18, motion_axis=normal.tolist(),
             rotation_center=STAR_CENTER.tolist(),
             sampling=f'径向半径{102 + radial_offset}..{120 + radial_offset}、轴向深度10格；四组双翼齿轮徽记附在环外侧，原文未定的徽记取样与环整体运动。')
    p.ring(STAR_CENTER, 120 + radial_offset, 18, ARMOR, normal=normal, depth=10)
    p.ring(STAR_CENTER, 113 + radial_offset, 3, DARK, normal=normal, depth=12)
    p.ring(STAR_CENTER, 118 + radial_offset, 2, GOLD, normal=normal, depth=12)
    p.ring(STAR_CENTER + normal * 6, 107 + radial_offset, 2, COOL, normal=normal, depth=2)
    for i in range(24):
        a = i * math.tau / 24
        radial = math.cos(a) * u + math.sin(a) * v
        tangent = -math.sin(a) * u + math.cos(a) * v
        start, end = STAR_CENTER + radial * (105 + radial_offset), STAR_CENTER + radial * (96 + radial_offset)
        rod(p, start, end, 3.6, DARK)
        rod(p, end, end - radial * 2, 2.4, COOL)
        for side in (-1, 1):
            rod(p, STAR_CENTER + radial * (113 + radial_offset) + side * tangent * 4 + normal * 6,
                STAR_CENTER + radial * (118 + radial_offset) + side * tangent * 4 + normal * 6, 1.1, GOLD)
    for a in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        radial, tangent = math.cos(a) * u + math.sin(a) * v, -math.sin(a) * u + math.cos(a) * v
        crest = STAR_CENTER + radial * (119 + radial_offset)
        for side in (-1, 1):
            for feather in range(3):
                base = crest + tangent * side * (3 + feather * 4)
                tip = base + radial * (13 - feather * 3) + tangent * side * 6
                rod(p, base, tip, 2, ARMOR)
                rod(p, base + normal * 2, tip + normal * 2, .9, GOLD)
        rod(p, crest - normal * 1, crest + radial * 15 - normal * 1, 2.5, GOLD)
        p.sphere(crest + normal * 6, 3.5, COOL)
    return p.finish()


def star_dimension_fragment(index):
    angle = (index % 12) * math.tau / 12 + (index // 12) * .19
    latitude = [-.62, .04, .66][index // 12]
    radial = np.array([math.cos(latitude) * math.cos(angle), math.sin(latitude), math.cos(latitude) * math.sin(angle)])
    u = np.array([-math.sin(angle), 0., math.cos(angle)])
    v = np.cross(radial, u)
    center = STAR_CENTER + radial * 140
    width = 11 + index % 4 * 2
    height = 13 + index % 5 * 2
    profile = [(-width, -height * .6), (-width * .8, height * .7), (width * .1, height), (width, height * .2), (width * .6, -height)]
    p = Part(f'star_dimension_fragment_{index + 1:02d}', f'五格厚破碎维度片 {index + 1:02d}',
             source='二·2：外径280附近几十块厚5格的不规则赤金橙色透明碎片',
             count_in_group=36, normal_thickness=5,
             sampling='中心沿半径140球面分三圈、每圈12片；五边形截面及方位为原文未定的展示取样，保留各片完整边角。')
    vertices = [center + u * x + v * y + radial * depth for x, y in profile for depth in (-2, 2)]
    p.hull(vertices, GLASS if index % 3 else RED_GLASS)
    for i, (x, y) in enumerate(profile):
        next_x, next_y = profile[(i + 1) % len(profile)]
        if i % 2 == index % 2:
            rod(p, center + u * x + v * y, center + u * next_x + v * next_y, .7, ORANGE)
    return p.finish()


def sword_impact():
    p = Part('sword_impact_lava_waves', '恒星砧板上的凝固熔岩浪与破碎裂隙',
             source='二·1：剑尖周围150格半径内凝固岩浆巨浪与空间裂隙',
             nominal_radius=150,
             sampling='十二条不等长放射裂隙与四圈局部翻卷熔岩浪，位于Y0..40；每段完整保留，局部厚度可伸出原文核心高度。')
    for index in range(12):
        angle = index * math.tau / 12
        radial = np.array([math.cos(angle), 0., math.sin(angle)])
        tangent = np.array([-math.sin(angle), 0., math.cos(angle)])
        length = 100 + (index % 4) * 16
        curve = []
        for t in np.linspace(0, 1, 32):
            point = np.array([CX, 6., CZ]) + radial * (14 + (length - 14) * t)
            point += tangent * (6 * math.sin(t * math.pi * 3 + index))
            point[1] += 6 * t + 18 * math.sin(t * math.pi) ** 3
            curve.append(point)
        for a, b in zip(curve[:-1], curve[1:]):
            rod(p, a, b, 5.5, VOID)
            rod(p, a + [0, 3, 0], b + [0, 3, 0], 2.2, RED_GLASS)
            rod(p, a + [0, 4, 0], b + [0, 4, 0], .9, ORANGE)
    for index, radius in enumerate((42, 72, 103, 135)):
        for petal in range(8):
            a0 = petal * math.tau / 8 + index * .23
            curve = []
            for t in np.linspace(0, 1, 14):
                angle = a0 + t * .36
                curve.append(np.array([CX + radius * math.cos(angle), 10 + 16 * math.sin(t * math.pi), CZ + radius * math.sin(angle)]))
            for a, b in zip(curve[:-1], curve[1:]):
                rod(p, a, b, 5, MAGMA)
                rod(p, a + [0, 4, 0], b + [0, 4, 0], 1.5, ORANGE)
    return p.finish()


def build():
    parts = [sword_impact(), sword_truss(), sword_machinery(), sword_blades(), sword_guard(), sword_octahedral_core()]
    parts += [sword_clamp(i) for i in range(6)]
    parts += [star_body()]
    parts += [star_prominence(i) for i in range(12)]
    parts += [star_ring(i) for i in range(3)]
    parts += [star_dimension_fragment(i) for i in range(36)]
    notes = [
        {'source': '一·高度分层／二·1', 'conflict': '剑轴同时要求长338、高338与75度倾角，三者不能同时满足。',
         'sampling': '保留Y0..338端点与相对水平75度，Z轴投影约90.57格，主轴连续长度约349.93格。护手、刃体厚度按各自完整取样保留。'},
        {'source': '一·核心层／二·2', 'conflict': '恒星直径先写200，细节段与动态段两处写160。',
         'sampling': '本体采用细节段的160；三环采用240，维度片中心位于半径140外层。'},
        {'source': '一·核心层／二·2', 'conflict': '中心层Y46..220、球膛Y60..240，与三道垂直直径240环及日珥的完整范围不相容。',
         'sampling': '中心(489,150,460)，完整保留三道240环、徽记、60格日珥和五格碎片；实际边界由几何求取。'},
        {'source': '二·1／二·2', 'sampling': '六液压钳、六层活塞磁环、十二日珥与36维度片分别独立构件；原文未指定的细节数量、轮廓和方位按本模块采样。三道圣痕环metadata.motion_axis为数值三向量，绕恒星中心运动。'},
    ]
    return parts, notes
