import numpy as np

from author_w05_shapes_20261115 import Part, trace
from theatre_t1_walls import STONE, DARK, TRIM, GOLD, BRONZE, _arch, _coordinates


DETAIL_NOTES = [
    'V001与F03可见柱础暗色嵌板、细金菱饰、复层柱脚与盾形线饰。',
    'V015与H049可见双眼壁龛的同心泪滴眼睑、深色瞳孔、中央尖菱冠饰与复层拱线。',
    '束柱接头、砌缝间距和浮雕厚度按T1整数格比例推定，沿用冷灰紫与细金边。',
]


def _surface(part, xy, radius, state, axis, center, depth, inward, offset, scale=1):
    xy = np.asarray(xy, float)
    points = np.empty((len(xy), 3), float)
    points[:, axis] = depth+inward*offset
    points[:, 1] = xy[:, 1]
    points[:, 2-axis] = xy[:, 0]*scale+center
    trace(part, points, radius, state)


def _shield(part, axis, center, depth, inward, cy, width, height):
    y, u = np.mgrid[cy-height:cy+height+1, -width:width+1]
    extent = np.where(y >= cy, width, width*(y-cy+height)/height)
    mask = np.abs(u) <= extent
    part.points(_coordinates(u[mask], y[mask], depth, axis, center), DARK)
    outline = [(-width, cy+height), (width, cy+height), (width, cy),
               (0, cy-height), (-width, cy), (-width, cy+height)]
    _surface(part, outline, 1.1, TRIM, axis, center, depth, inward, 1)
    inset = [(0, cy+height-3), (3, cy+1), (0, cy-4), (-3, cy+1), (0, cy+height-3)]
    _surface(part, inset, .75, GOLD, axis, center, depth, inward, 2)


def _column_details(side, z):
    x = side*375
    part = Part(f'column_cluster_{side}_details_{z}', '束柱柱础嵌饰与冠部接头', section='walls',
                source='V001-0020.5s.jpg、V010-0025.0s.jpg、V015-0027.5s.jpg',
                design='柱础暗底菱饰、束柱细缝、冠部复层线脚；接头尺寸按方块比例推定')
    dz, dx = np.mgrid[-42:43, -42:43]
    edge, diagonal = np.maximum(np.abs(dx), np.abs(dz)), np.abs(dx)+np.abs(dz)
    for y, radius, state in [(30, 41, STONE), (32, 41, TRIM), (38, 35, DARK),
                             (58, 35, TRIM), (63, 29, STONE), (78, 29, TRIM),
                             (85, 21, DARK), (111, 21, TRIM), (533, 18, DARK),
                             (539, 23, TRIM), (547, 23, DARK), (553, 29, STONE),
                             (564, 29, TRIM), (568, 29, DARK)]:
        outer = (edge <= radius) & (diagonal <= radius*1.45)
        inner = (edge < radius-1) & (diagonal < (radius-1)*1.45)
        mask = outer & ~inner
        part.points(np.c_[x+dx[mask], np.full(mask.sum(), y), z+dz[mask]], state)
    for axis, center, depth, inward in [(0, z, x-35, -1), (0, z, x+35, 1),
                                        (2, x, z-35, -1), (2, x, z+35, 1)]:
        _shield(part, axis, center, depth, inward, 48, 10, 9)
        _surface(part, [(-15, 40), (-15, 58), (15, 58), (15, 40)],
                 1.1, STONE, axis, center, depth, inward, 0)
    for y in (154, 238, 322, 406, 490):
        mask = (edge == 18) & (diagonal <= 18*1.45)
        part.points(np.c_[x+dx[mask], np.full(mask.sum(), y), z+dz[mask]], DARK)
    for vx, vz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        part.box((x+vx*12, 116, z+vz*12), (x+vx*12, 530, z+vz*12), TRIM)
    for vx, vz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        extent = min(103, 496-z) if vz == 1 else 103
        a, b, c, d = np.array([(x+vx*24, 551, z+vz*24), (x+vx*31, 574, z+vz*31),
                               (x+vx*min(67, extent*.7), 597, z+vz*min(67, extent*.7)),
                               (x+vx*extent, 602, z+vz*extent)], float)
        for t in (.21, .62):
            p = (1-t)**3*a+3*t*(1-t)**2*b+3*t*t*(1-t)*c+t**3*d
            tangent = 3*(1-t)**2*(b-a)+6*t*(1-t)*(c-b)+3*t*t*(d-c)
            part.ring(p, 7.6, 1.3, TRIM, normal=tangent, depth=3)
            part.ring(p, 7.8, .9, BRONZE, normal=tangent, depth=1)
    return part.finish()


def _pier_details(side, center, rear=False):
    axis = 2 if rear else 0
    transverse = side*center if rear else center
    depth = -456 if rear else side*452
    inward = 1 if rear else -side
    name = f'rear_pier_{side}_details_{center}' if rear else f'wall_pier_{side}_side_details_{center}'
    part = Part(name, '墙扶柱嵌板与分层柱头', section='walls', source='F03-2145.0s.jpg、H049-2540.0s.jpg',
                design='暗底盾饰、收边线脚和分段石缝；局部厚度按T1方块比例推定')
    _shield(part, axis, transverse, depth, inward, 50, 8, 11)
    for y, width in [(30, 15), (36, 15), (75, 15)]:
        _surface(part, [(-width, y), (width, y)], .8, STONE,
                 axis, transverse, depth, inward, 0)
    shaft_depth = -462 if rear else side*461
    for y in (163, 337, 511):
        _surface(part, [(-9, y), (-4, y)], .65, DARK,
                 axis, transverse, shaft_depth, inward, 0)
        _surface(part, [(4, y), (9, y)], .65, DARK,
                 axis, transverse, shaft_depth, inward, 0)
    crown_depth = -451 if rear else side*449
    for y, width, state in [(571, 20 if rear else 17, STONE), (576, 20 if rear else 17, DARK),
                             (583, 20 if rear else 17, STONE)]:
        _surface(part, [(-width, y), (width, y)], .9, state,
                 axis, transverse, crown_depth, inward, 0)
    _shield(part, axis, transverse, crown_depth, inward, 578, 4, 5)
    for offset in (-7, 7):
        depths = np.array([crown_depth, crown_depth-inward*11, crown_depth-inward*22])
        points = _coordinates(np.array([offset]*3), np.array([587, 593, 598]), depths, axis, transverse)
        trace(part, points, 2.1, TRIM)
    return part.finish()


def _niche_details(name, axis, center, depth, inward, scale=1):
    part = Part(name, '同心泪滴双眼与复层尖拱', section='walls',
                source='V001-0020.5s.jpg、V015-0027.5s.jpg、F03-2145.0s.jpg、H049-2540.0s.jpg',
                design='同心眼睑、深色瞳孔、尖菱冠饰与拱线细化；层距按整数格比例推定')
    y, u = np.mgrid[77:585, -109:110]

    def slab(mask, state, offset):
        part.points(_coordinates(u[mask]*scale, y[mask], depth+inward*offset, axis, center), state)

    def line(points, radius, state, offset):
        _surface(part, points, radius, state, axis, center, depth, inward, offset, scale)

    def curve(points, radius, state, offset):
        a, b, c, d = np.asarray(points, float)
        t = np.linspace(0, 1, 33)[:, None]
        xy = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*d
        line(xy, radius, state, offset)

    for bottom, spring, radius, displacement, state, offset in [
            (80, 139, 100, 14, STONE, 4), (88, 139, 92, 14, BRONZE, 5),
            (91, 139, 89, 14, TRIM, 6), (288, 462, 120, 28, STONE, 3),
            (296, 462, 112, 28, DARK, 5), (299, 462, 109, 28, TRIM, 6)]:
        outer = _arch(u, y, bottom, spring, radius, displacement)
        inner = _arch(u, y, bottom+1, spring, radius-1, displacement)
        slab(outer & ~inner, state, offset)
    for side in (-1, 1):
        cx = side*41
        for width, top, point, radius, state, offset in [(22, 195, 151, 2.2, STONE, 9),
                                                         (16, 190, 160, 1.7, TRIM, 11)]:
            curve([(cx, point), (cx-width*1.2, point+18), (cx-width, top), (cx, top)],
                  radius, state, offset)
            curve([(cx, top), (cx+width, top), (cx+width*1.2, point+18), (cx, point)],
                  radius, state, offset)
        lens = ((u-cx)/10)**2+((y-179)/11)**2 <= 1
        slab(lens, DARK, 10)
        lens_edge = (((u-cx)/9)**2+((y-179)/10)**2 <= 1) & (((u-cx)/6.5)**2+((y-179)/8)**2 >= 1)
        slab(lens_edge, STONE, 12)
        pupil = ((u-cx)/4)**2+((y-180)/6)**2 <= 1
        slab(pupil, DARK, 13)
        curve([(0, 229), (side*24, 219), (side*53, 207), (side*75, 176)],
              1.8, TRIM, 8)
        line([(side*48, 145), (side*36, 125), (side*36, 95)], 1.1, STONE, 8)
        line([(side*21, 139), (side*18, 117), (side*18, 95)], .75, DARK, 8)
        line([(side*78, 309), (side*78, 454)], 1.0, STONE, 5)
        line([(side*80, 310), (side*80, 454)], .6, DARK, 6)
    diamond = np.abs(u)/11+np.abs(y-217)/16 <= 1
    inside = np.abs(u)/8+np.abs(y-217)/12 < 1
    slab(diamond, TRIM, 7)
    slab(inside, STONE, 8)
    slab((np.abs(u)/3+np.abs(y-218)/6 <= 1), DARK, 9)
    line([(0, 233), (0, 237)], .8, TRIM, 8)
    for bottom, half in [(82, 84), (91, 80), (292, 89), (301, 84)]:
        line([(-half, bottom), (half, bottom)], .8, TRIM, 6)
    line([(-7, 573), (0, 560), (7, 573), (7, 582), (-7, 582), (-7, 573)],
         1.1, TRIM, 5)
    line([(-3, 577), (0, 569), (3, 577)], .7, BRONZE, 7)
    lower = _arch(u, y, 78, 139, 102, 14)
    upper = _arch(u, y, 286, 462, 122, 28)
    blank_wall = ~lower & ~upper
    for height in (105, 159, 213, 321, 375, 429, 483, 537):
        slab(blank_wall & (y == height), DARK, 0)
    for row, bottom in enumerate((105, 159, 321, 375, 429, 483, 537)):
        seams = ((np.abs(u) == (103 if row % 2 else 98)) & (y > bottom) & (y < bottom+52))
        slab(blank_wall & seams, DARK, 0)
    return part.finish()


def build_details():
    parts = []
    for side in (-1, 1):
        for z in (-75, 180, 430):
            parts.append(_column_details(side, z))
        for z in (-472, -250, -30, 190, 410, 490):
            parts.append(_pier_details(side, z))
        for x in (160, 330, 470):
            parts.append(_pier_details(side, x, rear=True))
        for z in (-360, -140, 80, 300):
            parts.append(_niche_details(f'side_niche_{side}_details_{z}', 0, z, side*479, -side))
        parts.append(_niche_details(f'rear_niche_{side}_details', 2, side*246, -481, 1, .75))
    return parts
