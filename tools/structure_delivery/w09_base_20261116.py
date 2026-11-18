import math

from w09_common_20261116 import (
    Part, rod, np, CX, CZ, DARK, ARMOR, GOLD, WHITE, RED, LIGHT,
    PURPLE, GLASS, STONE, GILDED, HOT, VOID, CONTROL,
)


def build():
    parts, notes = [], []
    z, x = np.mgrid[0:1026, 0:976]
    dx, dz = x - CX, z - CZ
    edge = np.minimum.reduce((x, 975 - x, z, 1025 - z,
        (x + z - 96) / math.sqrt(2), (975 - x + z - 96) / math.sqrt(2),
        (x + 1025 - z - 96) / math.sqrt(2), (975 - x + 1025 - z - 96) / math.sqrt(2)))
    inside = edge >= 0
    radius = np.hypot(dx, dz)
    eyes = [(CX, CZ - 188), (CX, CZ + 188)]
    holes = np.zeros(x.shape, bool)
    for ex, ez in eyes:
        holes |= np.hypot(x - ex, z - ez) <= 32.5

    def layer(part, y, mask, state):
        part.points(np.c_[x[mask], np.full(np.count_nonzero(mask), y), z[mask]], state)

    floor = Part('ink_sea_lower_pan', '九幽墨海·切角下承力池底', section='base',
                 source_bounds_xz=[[0, 975], [0, 1025]], corner_cut=96, through_wells=True)
    for y in (0, 1):
        layer(floor, y, inside & ~holes, STONE)
    ribs = (x % 64 < 3) | (z % 64 < 3)
    for y in (2, 3, 4):
        layer(floor, y, inside & ~holes & ribs, ARMOR)
    parts.append(floor.finish())

    dike = Part('ink_sea_black_gold_dike', '九幽墨海·三十五格黑金切角重工堤', section='base',
                width=35, wall_thickness=4, y_range=[0, 45], corner_cut=96)
    band = inside & (edge < 35)
    face_ribs = (((x < 40) | (x > 935)) & (z % 64 < 4)) | (
        ((z < 40) | (z > 985)) & (x % 64 < 4))
    for y in range(2, 46):
        shell = band & ((edge < 4) | (edge >= 31))
        layer(dike, y, shell, DARK)
        layer(dike, y, shell & face_ribs, ARMOR)
        if y in (4, 5, 20, 21, 43, 44, 45):
            layer(dike, y, shell, GILDED if y < 43 else GOLD)
    for y in (42, 43, 44, 45):
        layer(dike, y, band, DARK)
    layer(dike, 45, band & ((edge < 3) | (edge > 31)), GOLD)
    layer(dike, 45, band & (x % 32 < 2) & (z % 32 < 2), LIGHT)
    parts.append(dike.finish())

    ink = Part('ink_sea_surface', '九幽墨海·纯黑认知水墨表层', section='base',
               surface_y=5, registered_fluid=False, visual='ink_surface',
               effect_semantics='暗金与绯红星点在纯黑表层流动，流体身份待后续确定。')
    layer(ink, 5, inside & (edge >= 35) & ~holes, DARK)
    parts.append(ink.finish())

    perimeter = np.array([[113, 17], [862, 17], [958, 113], [958, 912],
                          [862, 1008], [113, 1008], [17, 912], [17, 113]], float)
    vectors = np.roll(perimeter, -1, axis=0) - perimeter
    lengths = np.linalg.norm(vectors, axis=1)
    distances = np.r_[0, np.cumsum(lengths)]
    for index, distance in enumerate(np.arange(0, distances[-1], 64)):
        segment = np.searchsorted(distances, distance, side='right') - 1
        px, pz = np.rint(perimeter[segment] + vectors[segment] * (
            distance - distances[segment]) / lengths[segment]).astype(int)
        stele = Part(f'boundary_stele_{index + 1:02}', f'第{index + 1:02}座太虚镇界散热碑',
                     section='base', perimeter_distance=float(distance), center_xz=[int(px), int(pz)],
                     height=60, y_range=[0, 59], nominal_pitch=64)
        stele.box([px - 9, 0, pz - 9], [px + 9, 5, pz + 9], ARMOR)
        stele.box([px - 9, 5, pz - 9], [px + 9, 6, pz + 9], GOLD)
        for y in range(7, 48):
            qz, qx = np.mgrid[-6:7, -6:7]
            border = (abs(qx) >= 4) | (abs(qz) >= 4)
            stele.points(np.c_[px + qx[border], np.full(np.count_nonzero(border), y), pz + qz[border]], DARK)
            stele.box([px - 1, y, pz - 1], [px + 1, y, pz + 1], RED)
            if y % 12 < 2:
                stele.box([px - 7, y, pz - 7], [px + 7, y, pz - 5], GILDED)
                stele.box([px - 7, y, pz + 5], [px + 7, y, pz + 7], GILDED)
                stele.box([px - 7, y, pz - 4], [px - 5, y, pz + 4], GILDED)
                stele.box([px + 5, y, pz - 4], [px + 7, y, pz + 4], GILDED)
        for y in range(48, 60):
            half = max(0, 5 - (y - 48) // 2)
            stele.box([px - half, y, pz - half], [px + half, y, pz + half], GOLD)
        parts.append(stele.finish())

    glyphs = [('乾', (1, 1, 1)), ('坤', (0, 0, 0)), ('震', (1, 0, 0)), ('巽', (0, 1, 1)),
              ('坎', (0, 1, 0)), ('离', (1, 0, 1)), ('艮', (0, 0, 1)), ('兑', (1, 1, 0))]
    reserved = np.zeros(x.shape, bool)
    for index, (name, lines) in enumerate(glyphs):
        angle = -math.pi / 2 + index * math.pi / 4
        radial = np.array([math.cos(angle), math.sin(angle)])
        tangent = np.array([-radial[1], radial[0]])
        gv, gu = np.mgrid[-12:13, -60:60]
        trigram = Part(f'bagua_trigram_{index + 1}', f'赛博八卦·{name}卦三爻超导阵列', section='base',
                       trigram=name, lines_inner_to_outer=list(lines), line_size_lwh=[120, 25, 18],
                       radial_centers=[272, 309, 346], angle_degrees=math.degrees(angle),
                       y_range=[28, 45], broken_line_gap=24)
        for row, solid in enumerate(lines):
            selected = np.ones(gu.shape, bool) if solid else ((gu < -12) | (gu >= 12))
            local = np.stack((gu, gv), axis=-1)
            points = np.rint(np.array([CX, CZ]) + (272 + row * 37 + local[..., 1, None]) * radial
                             + local[..., 0, None] * tangent).astype(int)
            reserved[points[..., 1][selected], points[..., 0][selected]] = True
            caps = (gu < -57) | (gu >= 57)
            if not solid:
                caps |= ((gu >= -15) & (gu < -12)) | ((gu >= 12) & (gu < 15))
            wall = selected & ((abs(gv) >= 10) | caps)
            for y in range(28, 46):
                mask = selected if y <= 30 else wall
                trigram.points(np.c_[points[..., 0][mask], np.full(np.count_nonzero(mask), y),
                                     points[..., 1][mask]], ARMOR if y < 42 else GOLD)
                if y == 43:
                    liquid = selected & ~wall
                    trigram.points(np.c_[points[..., 0][liquid], np.full(np.count_nonzero(liquid), y),
                                         points[..., 1][liquid]], HOT)
                if y in (44, 45):
                    clamp = selected & (gu % 16 < 2)
                    trigram.points(np.c_[points[..., 0][clamp], np.full(np.count_nonzero(clamp), y),
                                         points[..., 1][clamp]], WHITE)
        parts.append(trigram.finish())

    disc = (radius <= 375) & ~holes
    curve = np.sign(dz) * np.sqrt(np.maximum(0, 187.5 ** 2 - (abs(dz) - 187.5) ** 2))
    yang = dx <= curve
    for name, label, mask, state in [('yang', '阳鱼·白瓷双层盘面', yang, WHITE),
                                     ('yin', '阴鱼·玄铁双层盘面', ~yang, DARK)]:
        fish = Part(f'bagua_{name}_double_deck', f'立体机械太极盘·{label}', section='base',
                    center_xz=[CX, CZ], nominal_diameter=750, y_range=[15, 45],
                    lower_deck_y=[15, 18], upper_deck_y=[42, 45], open_trigram_troughs=True)
        for y in range(15, 19):
            layer(fish, y, disc & mask, state)
        for y in range(42, 46):
            layer(fish, y, disc & mask & ~reserved, state)
        parts.append(fish.finish())

    drum = Part('bagua_hollow_drum', '立体八卦盘·中空外鼓与十六径向承力肋', section='base',
                radial_ribs=16, rim_thickness=5, y_range=[19, 41])
    spokes = np.zeros(x.shape, bool)
    for angle in np.arange(16) * math.pi / 8:
        spokes |= abs(dx * math.sin(angle) - dz * math.cos(angle)) <= 2
    frame = disc & (spokes | (radius >= 370) | (abs(radius - 250) < 3))
    for y in range(19, 42):
        layer(drum, y, frame, ARMOR)
        if y in (21, 22, 37, 38):
            layer(drum, y, disc & (radius >= 371), GOLD)
    parts.append(drum.finish())

    circuits = Part('bagua_dual_cognition_circuits', '阴阳盘·赤金与紫红双极回路', section='base',
                    circuit_y=45, conduit_semantics='现有方块表现导管与发光介质，未注册专用流体。')
    rings = (abs(radius - 115) < 2) | (abs(radius - 245) < 2) | (abs(radius - 365) < 2)
    available = disc & ~reserved
    layer(circuits, 45, available & yang & rings, GOLD)
    layer(circuits, 45, available & ~yang & rings, PURPLE)
    layer(circuits, 45, available & yang & (abs(radius - 119) <= 1), RED)
    layer(circuits, 45, available & ~yang & (abs(radius - 249) <= 1), RED)
    layer(circuits, 45, available & (abs(dx - curve) <= 2), GOLD)
    layer(circuits, 45, available & (abs(dx - curve) <= .6), RED)
    parts.append(circuits.finish())

    for index, (ex, ez) in enumerate(eyes):
        well_radius = np.hypot(x - ex, z - ez)
        well = Part(f'bagua_through_well_{index + 1}', f'太极鱼眼·第{index + 1}口贯通引力井', section='base',
                    center_xz=[ex, ez], clear_diameter=65, y_range=[0, 45], through_entire_base=True,
                    constraint_ring_y=[5, 15, 25, 35, 45], exclusive_hatch_positions=[])
        shell = (well_radius > 32.5) & (well_radius <= 39.5)
        for y in range(46):
            layer(well, y, shell, DARK)
            if y % 10 in (4, 5):
                layer(well, y, shell & (well_radius <= 35.5), GOLD)
                layer(well, y, shell & (well_radius <= 33.5), LIGHT)
        layer(well, 45, (well_radius > 32.5) & (well_radius <= 44.5), GOLD)
        parts.append(well.finish())

    for index, px in enumerate((408, 440, 520, 552)):
        column = Part(f'taixu_gate_column_{index + 1}', f'万识朝宗牌坊·第{index + 1}根冲天玄铁柱',
                      section='entry', x_range=[px, px + 15], z_range=[0, 15], y_range=[45, 154],
                      height=110, wall_thickness=3)
        column.box([px, 45, 0], [px + 15, 51, 15], ARMOR)
        for y in range(52, 151):
            column.box([px, y, 0], [px + 2, y, 15], DARK)
            column.box([px + 13, y, 0], [px + 15, y, 15], DARK)
            column.box([px + 3, y, 0], [px + 12, y, 2], DARK)
            column.box([px + 3, y, 13], [px + 12, y, 15], DARK)
            column.box([px + 6, y, 0], [px + 9, y, 0], RED)
            if y in (53, 54, 91, 92, 125, 126, 148, 149):
                column.box([px, y, 0], [px + 15, y, 15], GOLD)
        for y in range(151, 155):
            inset = y - 151
            column.box([px + inset, y, inset], [px + 15 - inset, y, 15 - inset], GOLD)
        parts.append(column.finish())

    gate = Part('taixu_gate_three_bay_beams', '万识朝宗牌坊·三间黑金重梁与狂草导光纹', section='entry',
                width=160, height=110, x_range=[408, 567], y_range=[45, 154],
                bay_clear_widths=[16, 64, 16], inscription_kind='自主设计水墨笔势导光纹，不引用官方字形。')
    for y in range(127, 136):
        gate.box([408, y, 2], [567, y, 13], GOLD if y in (127, 135) else DARK)
    for y in range(143, 150):
        gate.box([408, y, 2], [567, y, 13], GOLD if y in (143, 149) else DARK)
    gate.box([455, 130, 1], [520, 146, 14], GILDED)
    gate.box([457, 132, 0], [518, 144, 0], VOID)
    strokes = [[(0, 3), (11, 9), (2, 8)], [(2, 0), (9, 10), (4, 6), (11, 2)],
               [(0, 9), (10, 7), (3, 3), (11, 0)], [(1, 9), (8, 10), (5, 0), (11, 4)]]
    oy, ox = np.mgrid[-1:2, -1:2]
    brush = np.c_[ox.ravel(), oy.ravel(), np.zeros(ox.size)]
    for origin, points in zip((460, 474, 488, 502), strokes):
        for a, b in zip(points[:-1], points[1:]):
            start = np.array([origin + a[0], 133 + a[1], 0])
            end = np.array([origin + b[0], 133 + b[1], 0])
            samples = start + np.linspace(0, 1, 32)[:, None] * (end - start)
            gate.points((samples[:, None, :] + brush).reshape(-1, 3), LIGHT)
    parts.append(gate.finish())

    road = Part('taixu_floating_white_jade_stair', '万识朝宗·白玉金边悬浮神道', section='entry', width=45,
                z_range=[0, 244], floor_y_range=[45, 159], landing_walk_height=160,
                ramp_formula='踏面Y=45+floor(114*max(0,Z-24)/220)，Z0..244。')
    deck = []
    for pz in range(245):
        y = 45 + int(114 * max(0, pz - 24) / 220)
        deck.append(y)
        road.box([CX - 22, y - 2, pz], [CX + 22, y - 1, pz], ARMOR)
        road.box([CX - 20, y, pz], [CX + 20, y, pz], WHITE)
        for sign in (-1, 1):
            road.box([CX + sign * 21, y, pz], [CX + sign * 22, y, pz], GOLD)
        if pz % 16 < 2:
            road.box([CX - 16, y, pz], [CX + 16, y, pz], GOLD)
        if pz % 24 == 0:
            road.box([CX - 19, y - 6, pz], [CX + 19, y - 4, pz], ARMOR)
            for sign in (-1, 1):
                road.box([CX + sign * 21, y + 1, pz], [CX + sign * 22, y + 3, pz], GOLD)
    for sign in (-1, 1):
        for pz in range(0, 244, 24):
            end = min(244, pz + 24)
            rod(road, [CX + sign * 17, deck[pz] - 7, pz],
                [CX + sign * 17, deck[end] - 7, end], 2, GILDED)
    parts.append(road.finish())

    altar = Part('taixu_controller_altar', '太虚演武拜仙台·唯一主控操作台', section='entry',
                 controller_blueprint_xyz=[487, 160, 260], controller_marker_state=CONTROL,
                 surface_y=159, size_xz=[73, 33], controller_facing='north')
    az, ax = np.mgrid[244:277, CX - 36:CX + 37]
    border = (abs(ax - CX) > 32) | (abs(az - 260) > 12)
    for y in (157, 158, 159):
        altar.points(np.c_[ax.ravel(), np.full(ax.size, y), az.ravel()], GOLD if y < 159 else WHITE)
    for y in range(151, 157):
        altar.points(np.c_[ax[border], np.full(np.count_nonzero(border), y), az[border]], DARK)
    altar.points(np.c_[ax[border], np.full(np.count_nonzero(border), 159), az[border]], GOLD)
    altar.box([CX - 1, 159, 247], [CX + 1, 159, 273], GOLD)
    altar.box([CX - 15, 159, 259], [CX + 15, 159, 261], GOLD)
    for sign in (-1, 1):
        for pz in (248, 272):
            px = CX + sign * 33
            altar.box([px - 2, 160, pz - 2], [px + 2, 163, pz + 2], DARK)
            altar.box([px - 2, 164, pz - 2], [px + 2, 164, pz + 2], GOLD)
            altar.points([[px, 165, pz]], RED)
    altar.points([[CX, 160, 260]], CONTROL)
    parts.append(altar.finish())

    notes.extend([
        '底座按原文端点X0..975、Z0..1025完整生成，整数格包围范围为976×1026，较名义975×1025各多1格；四角斜切96格为自主施工取样，未按名义尺寸裁切。',
        '35格黑金外堤采用4格外壁、4格内壁与Y42..45上甲板，内部中空；池底Y0..1与64格节距池底肋保留。镇界碑中心沿内缩17格的八边折线按累计路程64格取样，高60格取Y0..59，最后一段到起点的余数间距独立保留。',
        '墨海只以Y5纯黑实体表层表现，金红星点留作特效语义；没有注册或宣称存在液态高维水墨流体。两口鱼眼的65格净孔从池底到盘面逐层排除，孔位继续向下、向上开放。',
        '750格阴阳盘按中心(487,500)、半径375的整数格圆采样，极轴可含751个方块中心，完整外缘保留；Y15..18下盘与Y42..45上盘之间保留中空鼓体、16径向肋及半径250格环梁。',
        '阴阳S形分界由两个187.5格半径半圆构成，鱼眼中心取(487,312)、(487,688)，净孔半径32.5格，内壁Y0..45、五组金色约束环。井壁用现有黑金结构与灯表现，没有预装激光仓或限定仓室位置。',
        '八卦方位原文未指定，本稿从负Z起顺时针采用乾、坤、震、巽、坎、离、艮、兑；爻序由内向外读取。每爻局部长120、径向宽25、高18，三爻径向中心272/309/346，断爻中缝24格；这是对8组三爻阵列尺寸的施工解释。',
        '三爻阵列设于Y28..45，开放凹槽嵌入上盘，盘面对应槽位留空；槽底赤金发光介质取现有HOT材质。阳鱼使用白瓷、金色与红色回路，阴鱼使用玄铁、紫色管路和深红脉冲回路。',
        '牌坊原文未给基面，本稿以广场Y45为基面取110格高度Y45..154，完整宽160取X408..567，四柱横截面16×16、内部中空，三间净宽16/64/16格；发光狂草笔势为自主导光纹，不冒充官方书法。',
        '神道宽45取X465..509，Z0..24为Y45入口，Z24..244以整数梯级升至实体踏面Y159，玩家脚底到达Y160操作层。原文入口区Z0..150与神道终点Z260跨区矛盾按原坐标保留。',
        '主控唯一定位为(487,160,260)，红石放在Y159的73×33开放式拜仙台面上；前方神道接到Z244，平台Z244..276，中央主控五面可操作。台面尺度、悬浮下框与四角矮灯为自主施工取样。',
        '原文外堤、64格镇界碑、入口神道与上层兵装可能相交，原坐标及完整构件保留，交叠交由整机统计；没有为视觉净空私自移位、缩短或删件。',
        '除唯一主控外全部实体格可替换合法通用接口、朝向自选；原文前区集中输入输出安排由负责人自由接口规则覆盖，预览没有特定总线或接口槽位。',
    ])
    return parts, notes
