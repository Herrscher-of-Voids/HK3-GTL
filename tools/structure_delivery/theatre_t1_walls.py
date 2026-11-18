import numpy as np

from author_w05_shapes_20261115 import Part, trace


STONE, DARK, TRIM, GOLD, WHITE, RED, CARPET_EDGE, LAMP, GLASS, IRIS, HK, BRONZE = range(1, 13)


def _coordinates(u, y, depth, axis, center=0):
    points = np.empty((np.size(u), 3), np.int32)
    points[:, axis] = depth
    points[:, 1] = np.ravel(y)
    points[:, 2-axis] = np.ravel(u)+center
    return points


def _arch(u, y, bottom, spring, radius, offset):
    height = spring+np.sqrt(np.maximum(0, radius*radius-(np.abs(u)+offset)**2))
    return (np.abs(u) <= radius-offset) & (y >= bottom) & (y <= height)


def _niche(name, label, axis, center, depth, inward, scale=1):
    part = Part(name, label, section='walls', source='V001-0020.5s.jpg、V015-0027.5s.jpg',
                design='尖拱壁龛、成对眼形浮雕与下垂细肋')
    y, u = np.mgrid[78:583, -99:100]

    def slab(mask, start, stop, state):
        for d in range(start, stop+1):
            part.points(_coordinates(u[mask]*scale, y[mask], depth+inward*d, axis, center), state)

    def line(points, radius, state, d):
        xy = np.asarray(points)
        trace(part, _coordinates(xy[:, 0]*scale, xy[:, 1], depth+inward*d, axis, center), radius, state)

    def curve(points, radius, state, d):
        t = np.linspace(0, 1, 33)[:, None]
        a, b, c, e = np.asarray(points, float)
        xy = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*e
        line(xy, radius, state, d)

    outer = _arch(u, y, 80, 139, 100, 14)
    inset = _arch(u, y, 87, 139, 93, 14)
    inner = _arch(u, y, 90, 139, 90, 14)
    slab(outer, 0, 2, TRIM)
    slab(inset, 3, 3, GOLD)
    slab(inner, 3, 3, DARK)
    slab(inner & ((u % 18) < 2), 4, 4, STONE)
    for side in (-1, 1):
        top = [(side*8, 162), (side*17, 194), (side*48, 211), (side*70, 187)]
        bottom = [(side*70, 187), (side*66, 148), (side*37, 135), (side*8, 162)]
        curve(top, 4.0, TRIM, 5)
        curve(bottom, 4.0, TRIM, 5)
        curve(top, 1.3, GOLD, 8)
        curve(bottom, 1.3, GOLD, 8)
        curve([(side*44, 190), (side*51, 175), (side*51, 158), (side*39, 152)], 4.5, DARK, 7)
        line([(side*39, 148), (side*28, 113), (side*25, 92)], 2.1, TRIM, 6)
        line([(side*39, 148), (side*28, 113), (side*25, 92)], 0.7, GOLD, 8)
    line([(0, 93), (0, 139)], 1.6, TRIM, 6)

    upper = _arch(u, y, 288, 462, 120, 28)
    inner_upper = _arch(u, y, 295, 462, 113, 28)
    edge_upper = _arch(u, y, 298, 462, 110, 28)
    slab(upper, 0, 2, TRIM)
    slab(inner_upper, 3, 3, DARK)
    slab(edge_upper, 3, 3, STONE)
    narrow = _arch(u, y, 308, 452, 76, 18)
    narrow_inner = _arch(u, y, 312, 452, 72, 18)
    slab(narrow & ~narrow_inner, 4, 4, TRIM)
    for side in (-1, 1):
        line([(side*68, 305), (side*68, 455)], 1.5, GOLD, 4)
        curve([(0, 516), (side*36, 476), (side*37, 413), (0, 378)], 2.1, TRIM, 5)
        line([(side*24, 329), (side*24, 373)], 1.5, TRIM, 5)
    line([(0, 319), (0, 514)], 1.7, TRIM, 5)
    return part.finish()


def _column(side, z):
    x = side*375
    part = Part(f'cluster_column_{side}_{z}', '高束柱与分叉柱头', section='walls',
                source='V001-0020.5s.jpg、V010-0025.0s.jpg',
                design='阶梯柱基、细束柱石壳与上端四向短肋')
    dz, dx = np.mgrid[-43:44, -43:44]
    for y in range(20, 570):
        radius = 41 if y < 36 else 35 if y < 60 else 29 if y < 82 else 21 if y < 115 else 18 if y < 535 else 23 if y < 552 else 29
        edge = np.maximum(np.abs(dx), np.abs(dz))
        octagon = (edge <= radius) & (np.abs(dx)+np.abs(dz) <= radius*1.45)
        inside = (edge <= radius-5) & (np.abs(dx)+np.abs(dz) <= (radius-5)*1.45)
        mask = octagon & ~inside
        state = TRIM if y in range(33, 38) or y in range(57, 62) or y >= 549 else STONE
        part.points(np.c_[dx[mask]+x, np.full(mask.sum(), y), dz[mask]+z], state)
    for a, b in [(-22, 0), (22, 0), (0, -22), (0, 22)]:
        part.box((x+a-3, 90, z+b-3), (x+a+3, 549, z+b+3), TRIM)
        part.box((x+a, 103, z+b), (x+a, 543, z+b), GOLD)
    for y, radius in [(36, 41), (61, 35), (83, 29), (535, 23), (552, 29)]:
        part.ring((x, y, z), radius, 2, BRONZE, depth=2)
    t = np.linspace(0, 1, 33)[:, None]
    for vx, vz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        extent = min(103, 496-z) if vz == 1 else 103
        controls = np.array([(x+vx*24, 551, z+vz*24), (x+vx*31, 574, z+vz*31),
                             (x+vx*min(67, extent*.7), 597, z+vz*min(67, extent*.7)),
                             (x+vx*extent, 602, z+vz*extent)])
        a, b, c, d = controls
        path = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*d
        trace(part, path, 6.5, TRIM)
        trace(part, path+[0, -5, 0], 1.4, GOLD)
    for vx in (-1, 1):
        part.box((x+vx*27-4, 558, z-4), (x+vx*27+4, 563, z+4), BRONZE)
        part.box((x+vx*27-2, 564, z-2), (x+vx*27+2, 573, z+2), LAMP)
    return part.finish()


def build_walls():
    parts = []
    rear = Part('rear_wall_shell', '后厅墙与花窗轮廓洞口', section='walls',
                design='冷灰紫薄石墙按完整长颈圆窗外框避让')
    y, x = np.mgrid[20:601, -500:501]
    circle = np.hypot(x, y-202)-105
    neck = np.hypot(x, np.maximum.reduce([202-y, y-510, np.zeros_like(y)]))-56
    wall = np.minimum(circle, neck) > 14
    for z in range(-486, -481):
        rear.points(np.c_[x[wall], y[wall], np.full(wall.sum(), z)], STONE)
    for bottom, top, state in [(20, 33, DARK), (66, 73, TRIM), (88, 93, TRIM),
                               (244, 250, TRIM), (260, 267, TRIM), (587, 600, TRIM)]:
        mask = wall & (y >= bottom) & (y <= top)
        for z in range(-481, -473):
            rear.points(np.c_[x[mask], y[mask], np.full(mask.sum(), z)], state)
    parts.append(rear.finish())

    for side in (-1, 1):
        wall_part = Part(f'side_wall_{side}', '侧厅冷灰石墙', section='walls')
        wall_part.box((side*480, 20, -486), (side*483, 600, 500), STONE)
        for bottom, top, state in [(20, 33, DARK), (60, 72, TRIM), (244, 250, TRIM),
                                   (260, 267, TRIM), (587, 600, TRIM)]:
            wall_part.box((side*470, bottom, -486), (side*479, top, 500), state)
        for yline in (75, 252, 585):
            wall_part.box((side*469, yline, -486), (side*470, yline+1, 500), GOLD)
        parts.append(wall_part.finish())
        for z in (-360, -140, 80, 300):
            parts.append(_niche(f'side_niche_{side}_{z}', '双眼壁龛与上层尖拱', 0, z, side*479, -side))
        for z in (-472, -250, -30, 190, 410, 490):
            pier = Part(f'wall_pier_{side}_{z}', '侧壁分格扶柱', section='walls')
            pier.box((side*453, 20, z-15), (side*479, 80, z+15), TRIM)
            pier.box((side*462, 81, z-9), (side*479, 568, z+9), STONE)
            pier.box((side*459, 87, z-3), (side*462, 574, z+3), TRIM)
            pier.box((side*457, 96, z), (side*458, 566, z), GOLD)
            pier.box((side*450, 569, z-17), (side*479, 587, z+17), TRIM)
            parts.append(pier.finish())
        for xcol in (160, 330, 470):
            pier = Part(f'rear_pier_{side}_{xcol}', '后厅分束扶柱', section='walls')
            px = side*xcol
            pier.box((px-19, 20, -481), (px+19, 91, -457), TRIM)
            pier.box((px-10, 92, -481), (px+10, 570, -463), STONE)
            pier.box((px-3, 95, -462), (px+3, 572, -458), TRIM)
            pier.box((px, 104, -457), (px, 562, -457), GOLD)
            pier.box((px-21, 571, -481), (px+21, 587, -452), TRIM)
            parts.append(pier.finish())
        parts.append(_niche(f'rear_niche_{side}', '后厅金框眼形壁龛', 2, side*246, -481, 1, .75))
        for z in (-75, 180, 430):
            parts.append(_column(side, z))

    front = Part('front_wall', '前厅围护与中轴入口', section='front')
    front.box((-500, 20, 494), (-151, 600, 500), STONE)
    front.box((151, 20, 494), (500, 600, 500), STONE)
    front.box((-150, 341, 494), (150, 600, 500), STONE)
    for xedge in (-158, 158):
        front.box((xedge-7, 20, 480), (xedge+7, 348, 493), TRIM)
        front.box((xedge-1, 28, 478), (xedge+1, 340, 479), GOLD)
    front.box((-165, 341, 480), (165, 354, 493), TRIM)
    for height in (66, 244, 587):
        front.box((-500, height, 484), (-166, height+7, 493), TRIM)
        front.box((166, height, 484), (500, height+7, 493), TRIM)
    parts.append(front.finish())

    xs, zs = [-480, -375, 0, 375, 480], [-486, -75, 180, 430, 500]
    for zi, z in enumerate(zs):
        beam = Part(f'roof_crossbeam_{zi}', '顶棚横向矩形梁', section='roof')
        beam.box((-480, 600, max(-486, z-7)), (480, 618, min(500, z+7)), STONE)
        beam.box((-480, 597, max(-486, z-10)), (480, 600, min(500, z+10)), TRIM)
        beam.box((-480, 596, max(-486, z-1)), (480, 597, min(500, z+1)), BRONZE)
        parts.append(beam.finish())
    for xi, x in enumerate(xs):
        beam = Part(f'roof_longbeam_{xi}', '顶棚纵向矩形梁', section='roof')
        beam.box((x-7, 600, -486), (x+7, 618, 500), STONE)
        beam.box((x-10, 597, -486), (x+10, 600, 500), TRIM)
        beam.box((x-1, 596, -486), (x+1, 597, 500), BRONZE)
        parts.append(beam.finish())
    for xi, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
        for zi, (c, d) in enumerate(zip(zs[:-1], zs[1:])):
            panel = Part(f'roof_panel_{xi}_{zi}', '凹入式矩形顶板', section='roof')
            panel.box((a+8, 619, c+8), (b-8, 620, d-8), DARK)
            for zedge in (c+15, d-15):
                panel.box((a+15, 618, zedge), (b-15, 618, zedge+1), BRONZE)
            for xedge in (a+15, b-15):
                panel.box((xedge, 618, c+15), (xedge+1, 618, d-15), BRONZE)
            parts.append(panel.finish())
    return parts
