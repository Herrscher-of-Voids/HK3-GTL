from w12_common_20261116 import (
    Part, rod, np, math, CX, CZ, ARMOR, GOLD, WHITE, LIGHT, GLASS,
    GILDED, HOT, VOID, CONTROL,
)


def build():
    parts, notes = [], []
    z, x = np.mgrid[0:847, 0:1063]
    dx, dz = x - CX, z - CZ
    metric = np.maximum.reduce((abs(dx) / 531, abs(dz) / 423, (abs(dx) + abs(dz)) / 774))
    inside = metric <= 1
    edge = np.minimum.reduce((531 - abs(dx), 423 - abs(dz), (774 - abs(dx) - abs(dz)) / math.sqrt(2)))
    step = np.minimum((metric * 6).astype(int), 5)
    surface = 15 + step * 6

    def layer(part, y, mask, state):
        part.points(np.c_[x[mask], np.full(np.count_nonzero(mask), y), z[mask]], state)

    bottom = Part('judgement_lower_plate', '罪业审判基盘·黑甲下承力底板', section='base', thickness=3)
    for y in range(3):
        layer(bottom, y, inside, VOID)
    parts.append(bottom.finish())

    rim = Part('judgement_octagonal_rim', '罪业审判基盘·八角重装甲外缘', section='base', wall_thickness=4)
    for y in range(3, 46):
        band = inside & (edge < 4)
        layer(rim, y, band, VOID)
        layer(rim, y, band & ((x % 48 < 3) | (z % 48 < 3)), ARMOR)
        if y in (5, 6, 19, 20, 43, 44, 45):
            layer(rim, y, inside & (edge < (7 if y >= 43 else 5)), GOLD)
    for y in (43, 44, 45):
        layer(rim, y, inside & (edge < 48), VOID)
    layer(rim, 45, inside & ((edge < 3) | ((edge > 43) & (edge < 47))), GOLD)
    layer(rim, 45, inside & (edge < 48) & ((x % 48 < 3) | (z % 48 < 3)), ARMOR)
    parts.append(rim.finish())

    terraces = Part('judgement_terraced_glass', '审判深井·六层金色防爆玻璃梯台', section='base', lower_y=15,
                    upper_y=45, drop=30, terrace_levels=[15, 21, 27, 33, 39, 45])
    grid = (x % 24 < 2) | (z % 24 < 2)
    for level in range(6):
        y = 15 + level * 6
        mask = inside & (step == level)
        layer(terraces, y - 2, mask & grid, ARMOR)
        layer(terraces, y - 1, mask & grid, VOID)
        layer(terraces, y, mask, GLASS if level < 5 else VOID)
        layer(terraces, y, mask & grid, VOID)
        layer(terraces, y, mask & (x % 96 < 2) & (z % 96 < 2), LIGHT)
        if level:
            border = inside & (abs(metric - level / 6) <= .004)
            for yy in range(y - 6, y + 1):
                layer(terraces, yy, border, ARMOR)
            layer(terraces, y, border, GOLD)
            layer(terraces, y - 3, border, LIGHT)
    parts.append(terraces.finish())

    machinery = Part('judgement_heat_grilles', '深渊散热阵列·三层超导格栅与径向承力肋', section='base',
                     grille_y=[6, 12, 18], grille_pitch=24, radial_ribs=24)
    spokes = np.zeros(x.shape, bool)
    for angle in np.arange(24) * math.pi / 12:
        spokes |= abs(dx * math.sin(angle) - dz * math.cos(angle)) < 2
    for y in range(3, 43):
        available = inside & (surface > y + 2) & (edge > 5)
        mask = available & spokes
        if y in (6, 12, 18):
            mask |= available & ((x % 24 < 2) | (z % 24 < 2))
        layer(machinery, y, mask, ARMOR)
        if y in (8, 20, 32):
            layer(machinery, y, available & spokes, GOLD)
    parts.append(machinery.finish())

    cooling = Part('judgement_cooling_pipes', '深渊散热阵列·金色冷却主管与分配支路', section='base',
                   trunk_y=7, plasma_y=8)
    for offset in (-192, 0, 192):
        cooling.box([CX - 430, 5, CZ + offset - 3], [CX + 430, 9, CZ + offset + 3], GILDED)
        cooling.box([CX - 430, 8, CZ + offset - 1], [CX + 430, 10, CZ + offset + 1], LIGHT)
    for offset in (-288, -144, 0, 144, 288):
        cooling.box([CX + offset - 3, 5, CZ - 300], [CX + offset + 3, 9, CZ + 300], GILDED)
        cooling.box([CX + offset - 1, 8, CZ - 300], [CX + offset + 1, 10, CZ + 300], GLASS)
    for px in range(CX - 384, CX + 385, 96):
        for pz in (CZ - 192, CZ, CZ + 192):
            cooling.box([px - 5, 4, pz - 5], [px + 5, 11, pz + 5], ARMOR)
            cooling.box([px - 3, 12, pz - 3], [px + 3, 12, pz + 3], GOLD)
    parts.append(cooling.finish())

    for index, angle in enumerate(np.arange(12) * math.pi / 6):
        px, pz = CX + round(292 * math.cos(angle)), CZ + round(220 * math.sin(angle))
        fan = Part(f'judgement_condenser_{index + 1:02}', f'第{index + 1:02}座深井冷凝风扇', section='base',
                   center_xyz=[px, 12, pz], outer_radius=28, blades=8)
        fan.ring([px, 11, pz], 28, 5, ARMOR, depth=6)
        fan.ring([px, 14, pz], 28, 2, GOLD, depth=2)
        fan.ring([px, 12, pz], 22, 1, LIGHT, depth=2)
        fan.beam([px, 7, pz], [px, 15, pz], 6, WHITE)
        for blade in np.arange(8) * math.pi / 4:
            inner = np.array([px + 7 * math.cos(blade), 12, pz + 7 * math.sin(blade)])
            outer = np.array([px + 23 * math.cos(blade + .24), 12, pz + 23 * math.sin(blade + .24)])
            rod(fan, inner, outer, 2.5, ARMOR)
            rod(fan, inner + [0, 1, 0], outer + [0, 1, 0], 1, WHITE)
        parts.append(fan.finish())

    sigil = Part('judgement_divine_inscription', '神恩结界·同心圆六芒星与十字刻度铭文', section='base',
                 circle_radii=[90, 160, 230, 300, 375], hexagram_radius=360)
    radius = np.hypot(dx, dz)
    broad = np.zeros(x.shape, bool)
    narrow = np.zeros(x.shape, bool)
    for r in (90, 160, 230, 300, 375):
        broad |= abs(radius - r) <= 3
        narrow |= abs(radius - r) <= 1
    vertices = np.array([[CX + 360 * math.cos(t), CZ + 360 * math.sin(t)] for t in np.arange(6) * math.pi / 3 - math.pi / 2])
    for i in range(6):
        a, b = vertices[i], vertices[(i + 2) % 6]
        vx, vz = b - a
        t = np.clip(((x - a[0]) * vx + (z - a[1]) * vz) / (vx * vx + vz * vz), 0, 1)
        distance = np.hypot(x - a[0] - t * vx, z - a[1] - t * vz)
        broad |= distance <= 3
        narrow |= distance <= 1
    broad |= (abs(dx) <= 3) | (abs(dz) <= 3)
    narrow |= (abs(dx) <= 1) | (abs(dz) <= 1)
    ticks = ((abs(dx) <= 14) & (abs(dz) % 32 <= 2)) | ((abs(dz) <= 14) & (abs(dx) % 32 <= 2))
    broad |= ticks
    ellipse = np.sqrt((dx / 501) ** 2 + (dz / 394) ** 2)
    broad |= abs(ellipse - 1) <= .007
    narrow |= abs(ellipse - 1) <= .002
    broad &= inside
    narrow &= inside
    sigil.points(np.c_[x[broad], surface[broad] + 1, z[broad]], GOLD)
    sigil.points(np.c_[x[narrow], surface[narrow] + 1, z[narrow]], LIGHT)
    parts.append(sigil.finish())

    vertices = np.array([[-309, -381], [309, -381], [489, -201], [489, 201],
                         [309, 381], [-309, 381], [-489, 201], [-489, -201]], float)
    pile_index = 0
    for edge_index, a in enumerate(vertices):
        b = vertices[(edge_index + 1) % 8]
        fractions = (.125, .375, .625, .875) if edge_index % 2 == 0 else (1 / 3, 2 / 3)
        for fraction in fractions:
            pile_index += 1
            px, pz = a + (b - a) * fraction
            outward = np.array([px, 0, pz]) / math.hypot(px, pz)
            start = np.array([CX + px, 0, CZ + pz])
            end = start - outward * 90 + [0, 90, 0]
            axis = (end - start) / np.linalg.norm(end - start)
            tangent = np.array([outward[2], 0, -outward[0]])
            across = np.cross(axis, tangent)
            anchor = start - outward * 70 + [0, 70, 0]
            pile = Part(f'judgement_hydraulic_anchor_{pile_index:02}', f'第{pile_index:02}根断罪液压锚桩', section='base',
                        edge_index=edge_index, edge_fraction=fraction, base_center_xyz=start.tolist(),
                        upper_axis_xyz=end.tolist(), chain_anchor_xyz=anchor.tolist(), axis_vertical_height=90,
                        nominal_cross_section=[40, 40], inward_degrees=45)
            q = np.arange(-19.5, 20.5)
            uu, vv = np.meshgrid(q, q, indexing='ij')
            selected = (abs(uu) >= 16.5) | (abs(vv) >= 16.5)
            offsets = uu[selected, None] * tangent + vv[selected, None] * across
            for j, center in enumerate(start + np.linspace(0, 1, 183)[:, None] * (end - start)):
                pile.points(center + offsets, ARMOR if j % 36 < 7 else VOID)
            for level in (0, 1 / 3, 2 / 3, 1):
                center = start + (end - start) * level
                q = np.arange(-23.5, 24.5)
                uu, vv = np.meshgrid(q, q, indexing='ij')
                selected = (abs(uu) >= 20.5) | (abs(vv) >= 20.5)
                offsets = uu[selected, None] * tangent + vv[selected, None] * across
                for s in np.arange(-3, 3.1, .75):
                    pile.points(center + axis * s + offsets, GOLD)
            rod(pile, start, end, 7, GILDED)
            rod(pile, start + axis * 10, end - axis * 10, 4, LIGHT)
            for sign in (-1, 1):
                flank = tangent * (sign * 16) + across * 20
                rod(pile, start + flank, end + flank, 2.5, GOLD)
                rod(pile, start + flank + across, end + flank + across, 1.5, LIGHT)
                rear = tangent * (sign * 20) - across * 12
                rod(pile, start + axis * 8 + rear, end - axis * 8 + rear, 2.5, WHITE)
            rod(pile, anchor - tangent * 13, anchor + tangent * 13, 7, GOLD, inner=4)
            parts.append(pile.finish())

    avenue = Part('judgement_starlight_avenue', '审判台前庭·四百格金色星光大道', section='base',
                  z_range=[20, 419], deck_y=45, width=23)
    avenue.box([CX - 11, 43, 20], [CX + 11, 45, 419], GOLD)
    avenue.box([CX - 9, 45, 20], [CX + 9, 45, 419], VOID)
    avenue.box([CX - 1, 45, 20], [CX + 1, 45, 419], GLASS)
    for pz in range(28, 420, 16):
        avenue.box([CX - 8, 45, pz], [CX + 8, 45, pz + 1], LIGHT)
    for pz in range(44, 420, 48):
        base_y = 15 + 6 * min(int(max(abs(pz - CZ) / 423, abs(pz - CZ) / 774) * 6), 5)
        for sign in (-1, 1):
            avenue.box([CX + sign * 9 - 2, base_y, pz - 3], [CX + sign * 9 + 2, 43, pz + 3], ARMOR)
    parts.append(avenue.finish())

    altar = Part('judgement_controller_altar', '告解审判台·唯一主控祭坛', section='base',
                 controller_blueprint_xyz=[CX, 50, 10], controller_marker_state=CONTROL)
    for level in range(5):
        altar.box([CX - 29 + 2 * level, 45 + level, level], [CX + 29 - 2 * level, 45 + level, 38 - 2 * level], GOLD if level % 2 == 0 else VOID)
    altar.box([CX - 18, 49, 5], [CX + 18, 49, 27], WHITE)
    altar.box([CX - 1, 49, 7], [CX + 1, 49, 27], GOLD)
    altar.box([CX - 8, 49, 9], [CX + 8, 49, 11], GOLD)
    for sign in (-1, 1):
        px = CX + sign * 21
        altar.box([px - 3, 50, 26], [px + 3, 60, 32], VOID)
        altar.box([px - 1, 51, 25], [px + 1, 58, 25], LIGHT)
        altar.box([px - 4, 55, 25], [px + 4, 56, 25], GOLD)
        for k in range(4):
            altar.box([px - 3 + k, 61 + k, 26 + k], [px + 3 - k, 61 + k, 32 - k], GOLD if k == 3 else WHITE)
    altar.points([[CX, 50, 10]], CONTROL)
    parts.append(altar.finish())

    notes.extend([
        '基座按X0..1062、Z0..846的八角轮廓生成，四角斜切180格；中心(531,423)。八角下承力底板Y0..2，外缘壳厚4格、上沿检修环带宽48格。',
        '原文未给下沉井半径与台阶分配，本稿按归一化八角半径分成六层，玻璃面Y15、21、27、33、39、45，最大下沉30格；24格节距黑甲支梁托举金色防爆玻璃，台阶立面保留可见金色散热线。',
        '散热格栅设于Y6、12、18，24根径向承力肋、金色液冷主管与分支、12座八叶冷凝风扇位于透明地面下方。冷却介质取用现有黄灯与黄色玻璃，网页流水特效由预览单独决定。',
        '地面铭文取五个半径90、160、230、300、375格的同心圆、外接半径360的六芒星、32格节距十字刻度，以及半轴501/394的外围椭圆铭线；铭文随六层玻璃梯台改变高度，全部由整数方块构成。',
        '24桩底轴心沿内缩八角形取样，顶点相对中心为(-309,-381)、(309,-381)、(489,-201)、(489,201)、(309,381)、(-309,381)、(-489,201)、(-489,-201)。第0/2/4/6边各按t=1/8、3/8、5/8、7/8取4桩，其余四斜边按t=1/3、2/3取2桩。',
        '每桩轴心垂直跨度Y0..90、向心倾角45度，垂直轴心公式Q(y)=S-y*U+(0,y,0)，U为XZ向外单位向量；局部方截面40×40格、壳厚约4格，四道48格外宽金色抱箍、内置液压芯和双侧冷却管完整保留。',
        '24根锚桩按边序与t递增编号，metadata记录Y70轴心为chain_anchor_xyz，供实体锁链接入；倾斜截面与抱箍会越过轴心Y0/90端点，实际边界随完整几何记录。',
        '主控固定源坐标(531,50,10)，红石定位块位于开放式黑白金审判台上；400格金色星光大道取Z20..419、Y45，宽23格。原文称Z10为南侧的方向命名矛盾另由整机记录，坐标原样保留。',
        '原文固定仓位安排由负责人通用接口规则覆盖，基座没有专用接口槽位；除唯一主控外，全部实体格可替换合法通用接口并由玩家选择朝向。',
        '底板、梯台、承力肋、管线、风扇、铭文、大道、祭坛及液压桩按构件完整保留，连接处的重合由整机统计；未按名义高度或占地窗口裁切实体。',
    ])
    return parts, notes
