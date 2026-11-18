from types import SimpleNamespace

from w10_common_20261116 import (
    Part, np, math, trace, turn,
    DARK, ARMOR, GOLD, WHITE, AMBER, LIGHT, PURPLE, GLASS, GILDED,
)


def slab(part, low, high, half):
    q = np.arange(-half, half)
    x, z = np.meshgrid(q, q, indexing='ij')
    mask = np.abs(x) + np.abs(z) <= int(half * 1.6)
    x, z = x[mask], z[mask]
    edge = (np.maximum(np.abs(x), np.abs(z)) >= half - 5) | (np.abs(x) + np.abs(z) >= int(half * 1.6) - 5)
    for y in range(low, high + 1):
        points = np.c_[400 + x, np.full(len(x), y), z]
        part.points(points, DARK if (y - low) % 6 < 4 else ARMOR)
        if y - low < 2 or high - y < 2:
            part.points(points[edge], GOLD)


def tower():
    chassis = Part('tower_body', '黑金悬置甲板与白色承重骨架', tower_center=[400, 204, 0], nominal_width=120,
                   nominal_height=280, endpoint_y=[64, 344], fixed_interface_positions=[])
    for low, high, half in [(64, 79, 60), (110, 119, 56), (142, 151, 58),
                            (172, 189, 60), (300, 311, 58), (336, 344, 60)]:
        slab(chassis, low, high, half)
    for x in (-42, 42):
        for z in (-42, 42):
            chassis.box((400 + x - 8, 78, z - 8), (400 + x + 8, 338, z + 8), DARK)
            for y in (80, 132, 160, 292, 322):
                chassis.box((400 + x - 11, y, z - 11), (400 + x + 11, y + 5, z + 11), GILDED)
    for y in (96, 128, 156, 320):
        for side in (-1, 1):
            chassis.box((348, y, side * 42 - 4), (451, y + 6, side * 42 + 4), DARK)
            chassis.box((400 + side * 42 - 4, y, -52), (400 + side * 42 + 4, y + 6, 51), DARK)
    for side in (-1, 1):
        for y in (88, 120, 152, 316):
            chassis.box((394, y, side * 52 - 2), (405, y + 6, side * 52 + 2), LIGHT)
            chassis.box((400 + side * 52 - 2, y, -6), (400 + side * 52 + 2, y + 6, 5), LIGHT)
    chassis = chassis.finish()

    lens = Part('tower_lens', '悬置球形引力透镜', center=[400, 244, 0], radius=32)
    lens.sphere((400, 244, 0), 32, GLASS, inner=28)
    lens.sphere((400, 244, 0), 14, DARK)
    lens.ring((400, 244, 0), 31, 2, PURPLE, normal=(1, 0, 0), depth=3)
    lens.ring((400, 244, 0), 25, 2, AMBER, normal=(1, 0, 0), depth=3)
    lens.ring((400, 244, 0), 16, 2, LIGHT, normal=(1, 0, 0), depth=4)
    lens = lens.finish()

    ring = Part('tower_halo', '引力透镜黑金机械环', center=[400, 244, 0], normal=[1, 0, 0], outer_radius=59)
    ring.ring((400, 244, 0), 59, 10, DARK, normal=(1, 0, 0), depth=13)
    ring.ring((400, 244, 0), 58, 7, GOLD, normal=(1, 0, 0), depth=9)
    ring.ring((400, 244, 0), 50, 2, GILDED, normal=(1, 0, 0), depth=7)
    for theta in np.linspace(0, 2 * math.pi, 12, endpoint=False):
        a = np.array([400, 244 + 49 * math.cos(theta), 49 * math.sin(theta)])
        b = np.array([400, 244 + 57 * math.cos(theta), 57 * math.sin(theta)])
        ring.beam(a, b, 2, GILDED)
    ring = ring.finish()

    points = np.concatenate([chassis.p, lens.p, ring.p])
    low, size = points.min(0), np.ptp(points, axis=0) + 1
    local = points - low
    count = len(np.unique((local[:, 1] * size[2] + local[:, 2]) * size[0] + local[:, 0]))
    white_count = round(count * .25)
    x, z = chassis.p[:, 0] - 400, chassis.p[:, 2]
    distance = np.minimum.reduce([np.maximum(np.abs(x - a), np.abs(z - b)) for a in (-42, 42) for b in (-42, 42)])
    chassis.states[np.argsort(distance, kind='stable')[:white_count]] = WHITE
    chassis.metadata.update(white_skeleton_blocks=white_count, tower_unique_blocks=count,
                            white_skeleton_fraction=white_count / count)
    return [chassis, lens, ring]


def bridge():
    part = Part('bridge', '黄色透明物质桥与金色芯', center_y=180, width=35, thickness=20,
                source=[400, 180, 0], target=[0, 180, 0], fixed_interface_positions=[])
    x, z = np.meshgrid(np.arange(401), np.arange(-17, 18), indexing='ij')
    x, z = x.ravel(), z.ravel()
    for y in range(170, 190):
        points = np.c_[x, np.full(len(x), y), z]
        wall = (np.abs(z) >= 14) | (y <= 172) | (y >= 187)
        part.points(points[wall], GLASS)
        rib = ((x % 32 < 3) | (x == 400)) & ((np.abs(z) >= 15) | (y <= 171) | (y >= 188))
        part.points(points[rib], DARK)
        rail = (np.abs(z) >= 16) & ((y <= 172) | (y >= 187))
        part.points(points[rail], GOLD)
    part.box((0, 178, -3), (400, 182, 3), GOLD)
    for x in range(0, 400, 32):
        part.box((x, 176, -5), (x + 2, 184, 5), GILDED)
    return part.finish()


def arch():
    part = Part('dome_arch', '八百格穹顶黑金白拱梁', centerline_start=[400, 344, 0],
                centerline_end=[0, 444, 0], centerline_diameter=800, nominal_apex_y=444)
    theta = np.linspace(0, math.pi / 2, 85)
    curve = np.c_[400 * np.cos(theta), 344 + 100 * np.sin(theta), np.zeros(len(theta))]
    trace(part, curve, 7, WHITE)
    for side in (-1, 1):
        trace(part, curve + [0, 0, side * 10], 4, DARK)
        trace(part, curve + [0, 0, side * 10], 2, GOLD)
    trace(part, curve + [0, 6, 0], 3, GOLD)
    for at in range(0, len(curve), 7):
        a, b = curve[at] + [0, 0, -13], curve[at] + [0, 0, 13]
        part.beam(a, b, 2, GILDED)
    return part.finish()


def hammer():
    part = Part('zenith_hammer', '倒挂阶梯黑金引力重锤', centerline=[0, 0], nominal_diameter=70,
                endpoint_y=[290, 444], fixed_interface_positions=[])
    for y in range(290, 445):
        radius = min(35, 1 + max(0, y - 300) // 13 * 4)
        q = np.arange(-radius, radius + 1)
        x, z = np.meshgrid(q, q, indexing='ij')
        mask = np.abs(x) + np.abs(z) <= max(1, int(radius * 1.45))
        x, z = x[mask], z[mask]
        points = np.c_[x, np.full(len(x), y), z]
        part.points(points, DARK)
        edge = (np.maximum(np.abs(x), np.abs(z)) >= radius - 1) | (np.abs(x) + np.abs(z) >= int(radius * 1.45) - 1)
        if y >= 301:
            part.points(points[edge], GOLD if (y - 301) % 13 < 3 or y >= 438 else GILDED)
        spine = (np.abs(x) <= 1) | (np.abs(z) <= 1)
        part.points(points[spine & edge], GOLD)
    part = part.finish()

    halo = Part('hammer_halo', '重锤一百二十格悬浮金环', center=[0, 392, 0], nominal_diameter=120,
                normal=[0, 1, 0], sampled_height=True)
    halo.ring((0, 392, 0), 60, 9, GILDED, depth=5)
    halo.ring((0, 392, 0), 60, 5, GOLD, depth=9)
    halo.ring((0, 392, 0), 51, 2, AMBER, depth=3)
    halo = halo.finish()
    rings = []
    for index, y in enumerate((328, 360, 392), 1):
        rings.append(SimpleNamespace(name=f'hammer_halo_{index:02}', label=f'重锤·第{index}重悬浮金环',
            p=halo.p + [0, y - 392, 0], states=halo.states.copy(),
            metadata={**halo.metadata, 'center': [0, y, 0]}))
    return [part, *rings]


def rotated(part, angle, suffix, direction):
    metadata = {**part.metadata, 'azimuth_degrees': round(math.degrees(angle)), 'cardinal_direction': direction}
    for key in metadata.keys() & {'center', 'tower_center', 'source', 'target', 'centerline_start', 'centerline_end', 'normal'}:
        metadata[key] = np.rint(turn([metadata[key]], angle)[0]).astype(int).tolist()
    return SimpleNamespace(name=part.name + '_' + suffix, label=direction + '·' + part.label,
                           p=np.rint(turn(part.p, angle)).astype(np.int32), states=part.states.copy(),
                           metadata=metadata)


def build():
    parts = []
    tower_parts, bridge_part, arch_part = tower(), bridge(), arch()
    for index, (suffix, direction) in enumerate([('east', '东'), ('south', '南'), ('west', '西'), ('north', '北')]):
        angle = index * math.pi / 2
        parts.extend(rotated(part, angle, suffix, direction) for part in tower_parts)
        parts.append(rotated(bridge_part, angle, suffix, direction))
        parts.append(rotated(arch_part, angle, suffix, direction))
    parts.extend(hammer())
    notes = [
        '四塔中心按半径400格正东南西北布置，主体甲板名义宽120格；Y64至344包含全部连续端点，实体占格高281，原案标称高度280保留。',
        '四塔白色承重骨架优先覆盖四角连续主柱及相连甲板载荷垫，按每塔去重实体数量分配约25%，不使用随机白色散点。球形透镜取中心Y244、半径32；巨大金环取竖直径向法线、外半径59，这些局部参数为本稿取样。',
        '四桥保持中心Y180、35格宽及20格厚，端点由塔中心半径400贯至(0,180,0)。透明黄色管壁、金色芯与内部机械肋保持原轴，四桥中心交叉完整保留。',
        '四拱中心线采用400格水平半径、100格拱高的四分之一椭圆，从各塔(半径400,Y344)汇至(0,444,0)。主梁半径7、侧脊偏移10格、金色顶脊上浮6格均完整生成，厚梁实际最高Y453，未按名义穹顶Y444裁切。',
        '天顶倒挂重锤保留Y290至444全部端点；70格为名义直径，整数对称端点X/Z=-35至35使实际最大宽71格。周边三重金环名义直径120、整数对称端点实际宽121格，数量3及水平悬浮高度Y328/360/392为原案未指定参数的本稿取样。',
        '四塔金环与甲板和承重架的安装重叠、四拱在天顶的汇合及重锤交叠均保留；各部件独立输出，与核心笼、桩及主环的跨模块交集由总装逐格记录，禁止通过移动或删除化解。',
        '本模块无主控与固定接口位；全部实体格沿用合法通用接口自由替换、朝向自选规则。',
    ]
    return parts, notes
