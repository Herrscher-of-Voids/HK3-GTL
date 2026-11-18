from types import SimpleNamespace

from w10_common_20261116 import Part, rod, np, math, bezier, DARK, ARMOR, GOLD, AMBER, LIGHT, STONE, GILDED


def build():
    parts, notes = [], []
    z, x = np.mgrid[-474:475, -474:475]
    radius = np.hypot(x, z)
    octagon = np.maximum(np.maximum(abs(x), abs(z)), (abs(x) + abs(z)) * 474 / 670)
    inside = octagon <= 474

    def layer(part, y, selected, state):
        part.points(np.c_[x[selected], np.full(np.count_nonzero(selected), y), z[selected]], state)

    lower = Part('base_underplate', '八角底基·下承力甲板', source='八角基座Y0到64', thickness=4)
    for y in range(4):
        layer(lower, y, inside & (radius >= 350 * y / 64), STONE)
    parts.append(lower.finish())

    hull = Part('base_lower_hull', '八角底基·下段装甲壳', thickness=6)
    for y in range(4, 24):
        layer(hull, y, inside & (octagon >= 468), DARK)
        if y in (4, 5, 22, 23):
            layer(hull, y, inside & (octagon >= 470), GILDED)
    parts.append(hull.finish())

    dike = Part('base_blast_dike', '八角底基·斜面防爆堤坝', y_range=[24, 64], thickness=30,
                inward_slope=12, shape='外边缘沿40格高度向内收12格，厚度沿八角轮廓保持30格。')
    for y in range(24, 65):
        outer = 474 - 12 * (y - 24) / 40
        band = (octagon <= outer) & (octagon >= outer - 30)
        layer(dike, y, band, STONE)
        layer(dike, y, band & ((octagon >= outer - 4) | (octagon <= outer - 27)), DARK)
        layer(dike, y, band & (octagon >= outer - 3) & ((x % 48 < 3) | (z % 48 < 3)), ARMOR)
        if y in (24, 25, 63, 64):
            layer(dike, y, band & (octagon >= outer - 3), GILDED)
    parts.append(dike.finish())

    deck = Part('base_upper_deck', '八角底基·上检修甲板', thickness=4, funnel_mouth_radius=350)
    for y in range(61, 65):
        outer = 474 - 12 * (y - 24) / 40
        selected = (octagon <= outer - 30) & (radius >= 350 * y / 64 + 5)
        layer(deck, y, selected, DARK)
        if y == 64:
            layer(deck, y, selected & ((x % 48 < 2) | (z % 48 < 2)), ARMOR)
            layer(deck, y, selected & ((abs(x) <= 2) | (abs(z) <= 2) | (abs(x - z) <= 3) | (abs(x + z) <= 3)), GOLD)
    parts.append(deck.finish())

    ribs = Part('base_internal_ribs', '八角底基·径向承力肋与环形检修梁', radial_ribs=16,
                rib_width=8, maintenance_levels=[18, 40])
    spoke = np.zeros(x.shape, bool)
    for angle in np.arange(16) * math.pi / 8:
        spoke |= (abs(x * math.sin(angle) - z * math.cos(angle)) <= 4)
    for y in range(4, 61):
        outer = 468 if y < 24 else 444 - 12 * (y - 24) / 40
        available = (octagon < outer) & (radius > 350 * y / 64 + 5)
        selected = available & spoke
        if y in (16, 17, 18, 38, 39, 40):
            selected |= available & ((abs(radius - 385) <= 5) | (abs(radius - 425) <= 5))
        layer(ribs, y, selected, ARMOR)
    parts.append(ribs.finish())

    well = Part('gravity_funnel_shell', '重力漏斗·倒锥凹井壁', top_radius=350, y_range=[0, 64],
                radial_thickness=5, profile='r=350*y/64')
    for y in range(65):
        r = 350 * y / 64
        layer(well, y, (radius >= r) & (radius <= r + 5), ARMOR)
        if y % 4 in (1, 2):
            layer(well, y, (radius >= r) & (radius <= r + 2), DARK)
    parts.append(well.finish())

    void = Part('gravity_funnel_void', '重力漏斗·井底黑色虚空面', radius=24, y=0, visual='void')
    layer(void, 0, radius <= 24, DARK)
    parts.append(void.finish())
    for index in range(16):
        y = (index + 1) * 4
        r = 350 * y / 64
        coil = Part(f'gravity_funnel_coil_{index + 1:02}', f'重力漏斗·第{index + 1:02}圈发光重力线圈',
                    center_xyz=[0, y, 0], outer_radius=r + 2, lower_y=y - 1,
                    radial_width=9, source='16圈阶梯式金色重力线圈')
        band = (radius >= r - 7) & (radius <= r + 2)
        core = (radius >= r - 5) & (radius <= r - 3)
        layer(coil, y - 1, band, GOLD)
        layer(coil, y - 1, core, LIGHT)
        layer(coil, y, band, GOLD)
        layer(coil, y, core, AMBER)
        parts.append(coil.finish())

    def pile_master():
        px, pz = 440, 180
        start = np.array([px, 0, pz], float)
        outward = np.array([px, 0, pz], float)
        outward /= np.linalg.norm(outward)
        end = start - outward * (180 * math.tan(math.radians(15))) + [0, 180, 0]
        axis = end - start
        axis /= np.linalg.norm(axis)
        tangent = np.array([outward[2], 0, -outward[0]])
        cross = np.cross(axis, tangent)
        pile = Part('suppression_pile_master', '向心倾斜镇压桩母型',
                    base_center_xyz=start.tolist(), upper_axis_xyz=end.tolist(), axis_vertical_height=180,
                    diameter=55, inward_degrees=15, root_count=3,
                    source='8桩中心(±440,±180)、(±180,±440)，柱帽与根须保留完整外包络。')
        rod(pile, start, end, 27.5, DARK, inner=23.5)
        for angle in np.arange(8) * math.pi / 4:
            offset = 26 * (tangent * math.cos(angle) + cross * math.sin(angle))
            rod(pile, start + offset, end + offset, 2.5, GILDED)
        for fraction in (0, .2, .4, .6, .8, 1):
            center = start + (end - start) * fraction
            rod(pile, center - axis * 3, center + axis * 3, 30, GILDED, inner=24)
            rod(pile, center - axis, center + axis, 30.5, GOLD, inner=28)
        rod(pile, start - axis * 6, start + axis * 6, 32, ARMOR, inner=22)
        rod(pile, end - axis * 3, end + axis * 9, 31, GOLD, inner=22)
        for sign in (-1, 1):
            offset = tangent * (sign * 25) + cross * 4
            rod(pile, start + axis * 10 + offset, end - axis * 8 + offset, 3, LIGHT)
            rod(pile, start + axis * 10 + offset + tangent * sign,
                end - axis * 8 + offset + tangent * sign, 3.5, AMBER)
        for side in (-1, 0, 1):
            attach = start + (end - start) * (52 / 180)
            begin = attach + outward * 20 + tangent * (side * 16) + [0, 4, 0]
            finish = start - outward * (88 if side == 0 else 70) + tangent * (side * 42) + [0, 12, 0]
            controls = [begin, begin - outward * 24 + [0, -10, 0], finish + outward * 24 + [0, 18, 0], finish]
            line = np.array([bezier(controls, t) for t in np.linspace(0, 1, 16)])
            for a, b in zip(line[:-1], line[1:]):
                rod(pile, a, b, 7, GILDED, inner=4)
        return pile.finish()

    canonical = pile_master()
    centers = [(sx * 440, sz * 180) for sx in (-1, 1) for sz in (-1, 1)]
    centers += [(sx * 180, sz * 440) for sx in (-1, 1) for sz in (-1, 1)]
    for index, (px, pz) in enumerate(centers):
        points = canonical.p.copy()
        endpoint = np.array(canonical.metadata['upper_axis_xyz'])
        if abs(px) == 180:
            points[:, [0, 2]] = points[:, [2, 0]]
            endpoint[[0, 2]] = endpoint[[2, 0]]
        points[:, 0] *= 1 if px > 0 else -1
        points[:, 2] *= 1 if pz > 0 else -1
        endpoint[0] *= 1 if px > 0 else -1
        endpoint[2] *= 1 if pz > 0 else -1
        metadata = dict(canonical.metadata, base_center_xyz=[px, 0, pz], upper_axis_xyz=endpoint.tolist(),
                        sampling='同一整数格母型镜像与X/Z轴交换，八桩严格对称。')
        parts.append(SimpleNamespace(name=f'suppression_pile_{index + 1:02}',
            label=f'第{index + 1:02}座向心倾斜镇压桩', p=points, states=canonical.states.copy(), metadata=metadata))

    notes.extend([
        '底座八角形按|x|、|z|≤474及|x|+|z|≤670生成，轴端半宽474、截角端196，底基完整保留Y0到64。',
        '原案未指定甲板、井壁及桩壁厚度：底板4格、上检修甲板4格、下段外壳6格、井壁径向5格、桩筒壁4格；内部采用径向承力肋和两层环形检修梁，不用全体积实心填充。',
        '外围防爆堤坝按负责人补充放在Y24到64，连续高度40，整数端点共41层；沿八角轮廓厚30格，外斜面从半宽474内收12格。',
        '漏斗按r=350*y/64取样，16圈中心位于Y4、8至64；每圈两层金框夹原生发光底芯及琥珀面，井底Y0另保留半径24的黑色虚空面。',
        '八桩以Y0与Y180为轴心端点，垂直跨度180，轴线向心倾斜15度；直径55的斜截面、底部座箍、柱帽及三根粗金根须全部保留，由实际体素求包围盒。',
        '八桩由同一完成整数格母型镜像及X/Z轴交换生成，材料与全部细节严格对称，保留每座独立构件。',
        '根须中心线从桩身Y56扎向基座Y12，外径14格，位于原基座Y0到64范围；倾斜底箍截面可越过Y0，柱帽厚度可超过Y180，保留这些实体取样端部。',
        '粗金根须从桩侧向心扎入基座内部，保留完整曲线与管壁；没有将桩帽、斜截面或独立构件裁到949×949×444窗口。',
        '甲板、装甲、承力肋、凹井及线圈的连接处保留原坐标重合；八桩分别独立，外部构件如与桩帽或根须相交，由整机记录冲突，不自行移位。'
    ])
    return parts, notes
