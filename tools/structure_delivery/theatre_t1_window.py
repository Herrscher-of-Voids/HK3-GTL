import numpy as np

from author_w05_shapes_20261115 import Part, trace


STONE, DARK, TRIM, GOLD, WHITE, RED, CARPET_EDGE, LAMP, GLASS, IRIS, HK, BRONZE = range(1, 13)


def build_window():
    part = Part('rear_teardrop_window', '长颈泪滴花窗与淡紫圆眼', section='window',
                source='F01-0023.0s.jpg、V008-0024.0s.jpg',
                design='原作圆窗、长竖窗、泪滴内框及环周小圆饰按整数格重建')
    y, x = np.mgrid[82:581, -120:121]
    circle = np.hypot(x, y-202)-105
    neck = np.hypot(x, np.maximum.reduce([202-y, y-510, np.zeros_like(y)]))-56
    distance = np.minimum(circle, neck)

    def slab(mask, low, high, state):
        yy, xx = y[mask], x[mask]
        for z in range(low, high+1):
            part.points(np.c_[xx, yy, np.full(xx.size, z)], state)

    def disk(cx, cy, radius, low, high, state, inner=0):
        r = np.hypot(x-cx, y-cy)
        slab((r <= radius) & (r >= inner), low, high, state)

    def line(points, radius, state, z=-450):
        trace(part, [[px, py, z] for px, py in points], radius, state)

    def curve(points, radius, state, z=-450):
        t = np.linspace(0, 1, 65)[:, None]
        a, b, c, d = np.asarray(points, float)
        xy = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t**2*c+t**3*d
        line(xy, radius, state, z)

    slab((distance > -3) & (distance <= 14), -480, -463, STONE)
    slab((distance > 8) & (distance <= 14), -462, -456, TRIM)
    slab((distance > 5) & (distance <= 8), -462, -453, DARK)
    slab((distance > 0) & (distance <= 5), -462, -451, TRIM)
    slab((distance > -3) & (distance <= 0), -462, -449, GOLD)
    slab(distance <= -3, -474, -460, GLASS)

    # 竖向窗棂沿长颈延续，下端弯成包围圆眼的泪滴。
    for side in (-1, 1):
        line([(side*54, 510), (side*54, 237)], 3.8, BRONZE, -454)
        curve([(side*54, 237), (side*54, 187), (side*27, 155), (0, 133)], 3.8, BRONZE, -454)
        line([(side*54, 510), (side*54, 237)], 1.6, GOLD)
        curve([(side*54, 237), (side*54, 187), (side*27, 155), (0, 133)], 1.6, GOLD)
        line([(side*19, 254), (side*19, 555)], 1.1, GOLD, -454)
    line([(0, 267), (0, 563)], 1.0, GOLD, -454)
    for height in (301, 390, 480):
        line([(-53, height), (53, height)], 1.2, GOLD, -453)
        for cx in (-19, 19):
            line([(cx-5, height), (cx, height-5), (cx+5, height)], 1.1, GOLD, -452)

    angles = np.deg2rad(np.linspace(128, 412, 211))
    for radius, width, state, z in [(102, 1.6, GOLD, -452), (84, 1.5, BRONZE, -453)]:
        line(np.c_[radius*np.cos(angles), 202+radius*np.sin(angles)], width, state, z)
    for angle in np.deg2rad(np.linspace(130, 410, 29)):
        cx, cy = 93*np.cos(angle), 202+93*np.sin(angle)
        disk(cx, cy, 5.2, -457, -451, GOLD)
        disk(cx, cy, 3.8, -450, -447, WHITE)

    for side in (-1, 1):
        line([(side*55, 224), (side*84, 224)], 1.4, GOLD, -452)
        curve([(side*15, 209), (side*29, 196), (side*26, 188), (0, 172)], 1.4, GOLD, -450)
        curve([(0, 172), (side*7, 186), (side*19, 190), (side*15, 209)], 1.4, GOLD, -450)
    for cx, cy in [(-29, 255), (29, 255)]:
        for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5)]:
            disk(cx+dx, cy+dy, 6, -455, -451, GOLD)
            disk(cx+dx, cy+dy, 4.6, -450, -447, WHITE)
    disk(0, 254, 7, -454, -450, GOLD)
    disk(0, 254, 5, -449, -447, WHITE)
    disk(0, 226, 25, -455, -451, GOLD)
    disk(0, 226, 22, -450, -448, WHITE)
    disk(0, 226, 18, -447, -446, LAMP)
    disk(0, 226, 13, -446, -446, GLASS)
    disk(0, 226, 9, -446, -446, IRIS)
    disk(-3, 230, 2, -446, -446, WHITE)
    return [part.finish()]
