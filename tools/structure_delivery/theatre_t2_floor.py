import numpy as np

from author_w05_shapes_20261115 import Part
from w08_common_20261116 import rod


STONE, DARK, TRIM, GOLD, WHITE, RED, CARPET_EDGE, LAMP, GLASS, IRIS, HK, BRONZE = range(1, 13)
WHITE_LAMP = 13


def rail(part, start, end):
    a, b = np.asarray(start, float), np.asarray(end, float)
    count = int(np.linalg.norm((b-a)[[0, 2]])//18)
    for height, radius, state in [(0, 3, STONE), (4, 2, TRIM), (27, 3, STONE), (30, 2, TRIM)]:
        rod(part, a+[0, height, 0], b+[0, height, 0], radius, state)
    for t in np.linspace(0, 1, count+1):
        p = a+t*(b-a)
        for bottom, top, radius in [(5, 6, 3), (7, 8, 2), (9, 10, 3), (11, 13, 4),
                                    (14, 16, 3), (17, 19, 2), (20, 23, 1), (24, 26, 2)]:
            part.box(p+[-radius, bottom, -radius], p+[radius, top, radius], STONE)
        for h in (7, 23):
            part.box(p+[-2, h, -2], p+[2, h, 2], TRIM)
        part.box(p+[-3, 4, -3], p+[3, 5, 3], TRIM)


def lamp(part, x, y, z):
    for half, bottom, top, state in [(13, 0, 3, DARK), (12, 4, 6, TRIM), (9, 7, 22, STONE),
                                      (11, 23, 25, TRIM), (13, 26, 28, STONE), (10, 29, 30, BRONZE)]:
        part.box([x-half, y+bottom, z-half], [x+half, y+top, z+half], state)
    for axis in (0, 2):
        for side in (-1, 1):
            center = np.array([x, y+15, z], float)
            center[axis] += side*10
            u = np.zeros(3);u[2-axis] = 1
            v = np.array([0, 1, 0])
            corners = [center-5*u, center+7*v, center+5*u, center-6*v, center-5*u]
            for a, b in zip(corners[:-1], corners[1:]):
                rod(part, a, b, .6, GOLD)
    for h in range(33, 55):
        radius = max(1, int(5*(1-abs(h-43)/11)))
        part.box([x-radius, y+h, z-radius], [x+radius, y+h, z+radius], WHITE_LAMP)
    for sx, sz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        rod(part, [x+sx*11, y+31, z+sz*11], [x, y+64, z], 1.4, BRONZE)
        rod(part, [x+sx*10, y+31, z+sz*10], [x, y+62, z], .65, GOLD)
    for sx in (-1, 1):
        rod(part, [x+sx*11, y+31, z-11], [x+sx*11, y+31, z+11], 1.5, BRONZE)
    for sz in (-1, 1):
        rod(part, [x-11, y+31, z+sz*11], [x+11, y+31, z+sz*11], 1.5, BRONZE)
    for h, radius in [(64, 2), (65, 2), (66, 1), (67, 1)]:
        part.box([x-radius, y+h, z-radius], [x+radius, y+h, z+radius], GOLD)


def tiles(part, x0, x1, z0, z1, y):
    part.box([x0, y-2, z0], [x1, y, z1], DARK)
    for z in range(z0, z1+1, 52):
        part.box([x0, y, z], [x1, y, min(z+1, z1)], BRONZE)
        part.box([x0, y, z], [x1, y, z], GOLD)
        for x in range(x0+(26 if (z-z0)//52 % 2 else 0), x1+1, 52):
            part.box([x, y, z], [min(x+1, x1), y, min(z+51, z1)], BRONZE)
            part.box([x, y, z], [x, y, min(z+51, z1)], GOLD)


def carpet(part, x0, x1, z0, z1, y, transverse=False):
    x0, x1 = sorted((x0, x1))
    part.box([x0, y, z0], [x1, y, z1], RED)
    if transverse:
        for z in [z0, z1-7]:
            part.box([x0, y, z], [x1, y, z+7], CARPET_EDGE)
            part.box([x0, y, z+3], [x1, y, z+4], GOLD)
    else:
        for x in [x0, x1-7]:
            part.box([x, y, z0], [x+7, y, z1], CARPET_EDGE)
            part.box([x+3, y, z0], [x+4, y, z1], GOLD)
    zz, xx = np.mgrid[z0:z1+1, x0:x1+1]
    edge = np.minimum(zz-z0, z1-zz) if transverse else np.minimum(xx-x0, x1-xx)
    along = xx if transverse else zz
    width = z1-z0+1 if transverse else x1-x0+1
    amplitude = min(6, (width-18)/8)
    center = 10+amplitude
    angle = 2*np.pi*along/32
    ornament = ((abs(edge-center-amplitude*np.sin(angle)) < .65) |
                (abs(edge-center+amplitude*np.sin(angle)) < .65)) & (edge > 8)
    part.points(np.c_[xx[ornament], np.full(ornament.sum(), y), zz[ornament]], CARPET_EDGE)
    stitches = (abs(edge-center) < 1) & ((along % 32) == 0)
    part.points(np.c_[xx[stitches], np.full(stitches.sum(), y), zz[stitches]], GOLD)


def build_floor():
    parts = []
    ground = Part('hall_floor', '金缝大砖与中轴红毯', section='floor', source='P02.jpg、V001-0020.5s.jpg')
    ground.box([-500, 14, -486], [500, 16, 500], HK)
    tiles(ground, -500, 500, -486, 500, 20)
    carpet(ground, -132, 132, 120, 500, 20)
    for side in (-1, 1):
        ground.box([side*480, 21, -486], [side*493, 26, 500], STONE)
        ground.box([side*478, 26, -486], [side*480, 27, 500], GOLD)
    parts.append(ground.finish())

    podium = Part('rear_landing', '圆窗前中层平台与侧廊', section='stairs', source='F01-0023.0s.jpg、H049-2540.0s.jpg')
    tiles(podium, -480, 480, -468, -84, 88)
    podium.box([-480, 21, -90], [480, 85, -84], STONE)
    for side in (-1, 1):
        podium.box([side*475, 21, -468], [side*480, 85, -84], STONE)
    carpet(podium, -132, 132, -445, -84, 88)
    for side in (-1, 1):
        rail(podium, [side*231, 89, -80], [side*465, 89, -80])
        for z in (-370, -105):
            lamp(podium, side*270, 89, z)
        for x in (165, 450):
            lamp(podium, side*x, 89, -388)
    parts.append(podium.finish())

    stair = Part('central_stair', '中轴宽楼梯与连贯织毯', section='stairs', source='V001-0020.5s.jpg')
    for step in range(1, 69):
        y, z = 20+step, 120-3*step
        stair.box([-225, y-3, z], [225, y, z+2], STONE)
        carpet(stair, -132, 132, z, z+2, y)
        for side in (-1, 1):
            stair.box([side*135, y, z], [side*225, y, z], TRIM)
    for side in (-1, 1):
        rail(stair, [side*229, 21, 120], [side*229, 89, -84])
        for z, y in [(126, 21), (-80, 89)]:
            lamp(stair, side*236, y, z)
    parts.append(stair.finish())

    for side in (-1, 1):
        branches = Part(f'split_stair_{side}', '左侧外展楼梯与二层回廊' if side < 0 else '右侧外展楼梯与二层回廊',
                        section='stairs', source='F01-0023.0s.jpg、V010-0025.0s.jpg')
        for step in range(1, 157):
            y = 88+step
            x0, x1 = 175+int((step-1)*235/156), 175+int(step*235/156)
            branches.box([side*x0, y-3, -350], [side*x1, y, -242], STONE)
            carpet(branches, side*x0, side*x1, -326, -266, y, transverse=True)
        for z in (-353, -239):
            rail(branches, [side*175, 89, z], [side*410, 245, z])
        tiles(branches, min(side*400, side*470), max(side*400, side*470), -468, 445, 244)
        carpet(branches, min(side*418, side*454), max(side*418, side*454), -468, 445, 244)
        rail(branches, [side*398, 245, -235], [side*398, 245, 445])
        rail(branches, [side*398, 245, -468], [side*398, 245, -355])
        for z in (-435, -210, 80, 415):
            lamp(branches, side*394, 245, z)
        for z in (-150, 160, 420):
            branches.box([side*430, 21, z-13], [side*460, 241, z+13], STONE)
            branches.box([side*422, 21, z-20], [side*468, 34, z+20], TRIM)
            branches.box([side*422, 227, z-20], [side*468, 241, z+20], STONE)
        parts.append(branches.finish())
    branches = Part('front_gallery', '前端二层连接回廊', section='front', design='按完整大厅动线补全')
    tiles(branches, -470, 470, 445, 475, 244)
    rail(branches, [-398, 245, 442], [398, 245, 442])
    parts.append(branches.finish())
    return parts
