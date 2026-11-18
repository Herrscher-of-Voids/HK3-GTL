import numpy as np

from author_w05_shapes_20261115 import Part, trace


STONE, DARK, TRIM, GOLD, WHITE, RED, CARPET_EDGE, LAMP, GLASS, IRIS, HK, BRONZE = range(1, 13)
WHITE_LAMP = 13


def build_window():
    parts = []
    y, x = np.mgrid[83:581, -119:120]
    radius = np.hypot(x, y-202)
    circle = radius-105
    neck = np.hypot(x, np.maximum.reduce([202-y, y-510, np.zeros_like(y)]))-56
    distance = np.minimum(circle, neck)

    def slab(mask, low, high, state):
        yy, xx = y[mask], x[mask]
        for z in range(low, high+1):
            part.points(np.c_[xx, yy, np.full(xx.size, z)], state)

    def disk(cx, cy, r, low, high, state, inner=0):
        radial = np.hypot(x-cx, y-cy)
        slab((radial <= r) & (radial >= inner), low, high, state)

    def line(points, width, state, z):
        trace(part, [[px, py, z] for px, py in points], width, state)

    def curve(points, width, state, z):
        t = np.linspace(0, 1, 65)[:, None]
        a, b, c, d = np.asarray(points, float)
        xy = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*d
        line(xy, width, state, z)

    part = Part('rear_window_bevelled_masonry', '花窗分层斜阶石框与砌缝', section='window',
                source='V008-0024.0s.jpg、F01-0023.0s.jpg',
                confirmed='圆形石框、多层内收轮廓、径向石缝与长颈竖框',
                inferred='六层斜阶、24段圆弧砌块与背部厚度按整数格补全')
    frame = (distance > -3) & (distance <= 14)
    slab(frame, -480, -475, STONE)
    angle = np.arctan2(y-202, x)
    phase = (angle+np.pi/24) % (np.pi/12)-np.pi/24
    joints = (np.abs(np.sin(phase)*radius) <= .55) & (circle <= neck)
    joints |= (neck < circle) & (y <= 510) & ((y-202) % 48 == 0)
    cap_radius = np.hypot(x, y-510)
    cap_angle = np.arctan2(y-510, x)
    cap_phase = (cap_angle+np.pi/12) % (np.pi/6)-np.pi/12
    joints |= (neck < circle) & (y > 510) & (np.abs(np.sin(cap_phase)*cap_radius) <= .55)
    for inner, outer, front, state in [(11, 14, -461, STONE), (8, 11, -458, STONE),
                                       (5, 8, -455, TRIM), (2, 5, -452, WHITE),
                                       (-1, 2, -449, STONE), (-3, -1, -447, WHITE)]:
        band = (distance > inner) & (distance <= outer)
        slab(band, -474, front-2, state)
        if inner >= 5:
            slab(band & joints, front-2, front-2, DARK)
            slab(band & ~joints, front-1, front, state)
        else:
            slab(band, front-1, front, state)
    parts.append(part.finish())

    part = Part('rear_window_cream_glazing', '奶黄长颈圆窗玻璃', section='window',
                source='V008-0024.0s.jpg', confirmed='奶黄发光窗面与细竖棂分格')
    slab(distance <= -3, -474, -460, GLASS)
    for side in (-1, 1):
        slab((distance <= -5) & (x*side >= 22) & (x*side <= 48) & (y >= 279), -459, -459, WHITE)
    parts.append(part.finish())

    part = Part('rear_window_teardrop_tracery', '泪滴窗棂与细金节点', section='window',
                source='F01-0023.0s.jpg、V008-0024.0s.jpg',
                confirmed='双竖边下接泪滴尖端、内部圆弧、三列细竖棂及小横档',
                inferred='金属包边厚度与窄窗横档连接节点按整数格补全')
    for side in (-1, 1):
        straight = [(side*54, 510), (side*54, 237)]
        lower = [(side*54, 237), (side*54, 187), (side*27, 155), (0, 133)]
        line(straight, 4.1, WHITE, -455)
        curve(lower, 4.1, WHITE, -455)
        line(straight, 2.1, TRIM, -450)
        curve(lower, 2.1, TRIM, -450)
        line(straight, .8, GOLD, -447)
        curve(lower, .8, GOLD, -447)
        line([(side*19, 254), (side*19, 555)], 1.5, WHITE, -456)
        line([(side*19, 254), (side*19, 555)], .75, TRIM, -452)
    line([(0, 267), (0, 563)], 1.2, WHITE, -455)
    line([(0, 267), (0, 563)], .7, TRIM, -452)
    for height in (301, 390, 480):
        line([(-53, height), (53, height)], 1.4, WHITE, -455)
        line([(-53, height), (53, height)], .8, TRIM, -452)
        for cx in (-19, 0, 19):
            line([(cx-4, height), (cx, height-4), (cx+4, height)], 1.1, TRIM, -450)
            disk(cx, height-1, 1.4, -449, -447, GOLD)
    angles = np.deg2rad(np.linspace(128, 412, 211))
    for r, width, state, z in [(102, 1.8, WHITE, -455), (101, .8, TRIM, -451),
                                 (84, 2.8, WHITE, -456), (84, 1.2, TRIM, -452),
                                 (84, .65, GOLD, -449)]:
        line(np.c_[r*np.cos(angles), 202+r*np.sin(angles)], width, state, z)
    for side in (-1, 1):
        line([(side*55, 224), (side*84, 224)], 1.2, TRIM, -452)
        curve([(side*15, 209), (side*29, 196), (side*26, 188), (0, 172)], 1.6, TRIM, -450)
        curve([(0, 172), (side*7, 186), (side*19, 190), (side*15, 209)], 1.6, TRIM, -450)
        leaf = ((x-side*19)/16)**2+((y-196-side*(x-side*19)*.65)/7)**2 <= 1
        slab(leaf, -458, -453, WHITE)
    line([(-5, 141), (0, 133), (5, 141)], 1, GOLD, -444)
    disk(0, 134, 2.3, -447, -444, TRIM)
    parts.append(part.finish())

    part = Part('rear_window_carved_ornaments', '窗圈圆饰与三叶浮雕', section='window',
                source='V008-0024.0s.jpg',
                confirmed='环周重复圆饰和内向叶尖、眼纹上方两组奶白叶饰',
                inferred='29组重复数、单组叶片轮廓与浮雕背座厚度按画面节奏补全')
    for angle in np.deg2rad(np.linspace(130, 410, 29)):
        cx, cy = 94*np.cos(angle), 202+94*np.sin(angle)
        radial = (x-cx)*np.cos(angle)+(y-cy)*np.sin(angle)
        tangent = -(x-cx)*np.sin(angle)+(y-cy)*np.cos(angle)
        bead = tangent*tangent+(radial-1)**2 <= 4.1**2
        leaves = (tangent/2.6)**2+((radial+5)/4.4)**2 <= 1
        for side in (-1, 1):
            leaves |= ((tangent-side*2.5)/2.5)**2+((radial+2.8)/3.1)**2 <= 1
        shape = bead | leaves
        slab(shape, -458, -453, TRIM)
        inset = (tangent*tangent+(radial-1)**2 <= 3.25**2) | \
                ((tangent/1.7)**2+((radial+4.9)/3.3)**2 <= 1)
        for side in (-1, 1):
            inset |= ((tangent-side*2.3)/1.7)**2+((radial+2.7)/2.3)**2 <= 1
        slab(inset, -452, -449, WHITE)
        disk(cx+np.cos(angle), cy+np.sin(angle), 2.4, -448, -446, WHITE)
    for cx in (-29, 29):
        cy = 255
        shape = np.zeros(x.shape, bool)
        inset = np.zeros(x.shape, bool)
        for theta in np.deg2rad((90, 210, 330)):
            dx, dy = 5.4*np.cos(theta), 5.4*np.sin(theta)
            shape |= np.hypot(x-cx-dx, y-cy-dy) <= 6.5
            inset |= np.hypot(x-cx-dx, y-cy-dy) <= 5.2
        slab(shape, -459, -452, TRIM)
        slab(inset, -451, -447, WHITE)
        disk(cx, cy, 4.4, -446, -444, WHITE)
        line([(cx, 266), (cx, 273)], 1, TRIM, -451)
        disk(cx, 273, 1.6, -450, -448, TRIM)
    disk(0, 254, 6, -456, -451, TRIM)
    disk(0, 254, 4.5, -450, -447, WHITE)
    parts.append(part.finish())

    part = Part('rear_window_lilac_eye', '淡紫眼纹分层圆心', section='window',
                source='V008-0024.0s.jpg', confirmed='淡紫中心、奶白光环与同心细边',
                inferred='前凸同心层厚度与单格高光按整数格补全')
    disk(0, 226, 25, -458, -452, TRIM)
    disk(0, 226, 23, -451, -448, WHITE)
    disk(0, 226, 20, -447, -445, GLASS)
    disk(0, 226, 18.5, -444, -444, IRIS, inner=16.8)
    disk(0, 226, 16.5, -444, -443, WHITE_LAMP)
    disk(0, 226, 13, -442, -442, GLASS)
    disk(0, 226, 9, -441, -441, IRIS)
    disk(-3, 230, 2, -440, -440, WHITE)
    parts.append(part.finish())
    return parts
