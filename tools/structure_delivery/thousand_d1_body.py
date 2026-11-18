import math

import numpy as np

from thousand_d1_common import (Part, trace, ellipsoid, BLACK, CLOTH, CLOTH_LIGHT,
                               WHITE, WHITE_SHADE, WHITE_LIGHT, GOLD, GOLD_LIGHT,
                               GOLD_DARK)


def build_body():
    p = Part('body', '黑金裙装本体', section='body', pivot=[0, 110, 0], parent='root')
    levels = [110, 117, 126, 134, 139, 143, 146]
    widths = [11, 13, 18, 20, 21, 16, 8]
    depths = [8, 9, 11, 12, 11, 9, 6]
    for y in range(110, 147):
        rx, rz = np.interp(y, levels, widths), np.interp(y, levels, depths)
        z, x = np.mgrid[-math.ceil(rz):math.ceil(rz)+1, -math.ceil(rx):math.ceil(rx)+1]
        q = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        p.points(q[(q[:, 0]/rx)**2+(q[:, 2]/rz)**2 <= 1], CLOTH)

    ellipsoid(p, (0, 149, 0), (6, 6, 5), WHITE)
    for side in (-1, 1):
        ellipsoid(p, (side*25, 140, 0), (6, 6, 6), WHITE)
        trace(p, [(side*27, 145, 2), (side*30, 140, 3), (side*27, 136, 2)], .65, WHITE_SHADE)
        trace(p, [(side*9, 112, 4), (side*13, 121, 7), (side*18, 133, 6)], .8, CLOTH_LIGHT)

    for y in range(128, 148):
        half = np.interp(y, [128, 136, 141, 147], [6, 17, 18, 7])
        back = -np.interp(y, levels, depths)-1
        for x in range(-math.floor(half), math.floor(half)+1):
            bottom = 128+round(4*(abs(x)/19)**1.7)
            if y >= bottom:
                z = back+2*(abs(x)/20)**2
                p.box((x, y, z), (x, y, z+2), WHITE)
    for side in (-1, 1):
        trace(p, [(side*6, 146, -8), (side*9, 140, -12), (side*7, 132, -12)], .65, WHITE_SHADE)
        trace(p, [(side*15, 143, -8), (side*17, 138, -10), (side*12, 132, -11)], .65, WHITE_SHADE)
        trace(p, [(side*7, 147, 1), (side*9, 143, 7), (side*5, 139, 11)], 1.2, WHITE_LIGHT)

    p.hull([(-1, 137, 12), (1, 137, 12), (-6, 130, 13), (6, 130, 13),
            (0, 119, 10), (-1, 137, 14), (1, 137, 14), (-6, 130, 15),
            (6, 130, 15), (0, 119, 12)], WHITE)
    trace(p, [(0, 147, 6), (0, 142, 10), (0, 137, 14)], .9, GOLD)
    p.hull([(-2, 140, 12), (0, 143, 11), (2, 140, 12), (0, 136, 14),
            (-2, 140, 14), (0, 143, 13), (2, 140, 14), (0, 136, 16)], GOLD_LIGHT)
    trace(p, [(-10, 112, -4), (-7, 110, -8), (0, 109, -9), (7, 110, -8), (10, 112, -4)], .8, GOLD_DARK)

    skirt_y = [83, 86, 90, 96, 103, 110]
    skirt_x = [29, 31, 30, 25, 17, 11]
    skirt_z = [18, 20, 20, 17, 12, 8]

    def skirt_point(angle, y, offset=0):
        rx = np.interp(y, skirt_y, skirt_x)+offset
        rz = np.interp(y, skirt_y, skirt_z)+offset
        return (math.sin(angle)*rx, y, math.cos(angle)*rz)

    for y in range(82, 111):
        rx = np.interp(y, skirt_y, skirt_x)
        rz = np.interp(y, skirt_y, skirt_z)
        z, x = np.mgrid[-math.ceil(rz):math.ceil(rz)+1, -math.ceil(rx):math.ceil(rx)+1]
        q = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        angle = np.arctan2(q[:, 0]/rx, q[:, 2]/rz)
        wave = 2.3*np.cos(10*angle)
        radial = (q[:, 0]/rx)**2+(q[:, 2]/rz)**2
        keep = (radial <= 1) & (radial >= .68) & (y >= 85+wave)
        p.points(q[keep], CLOTH)

    for i in range(14):
        a = i*2*math.pi/14
        lower = 83+round(1.5*math.cos(i*math.pi))
        samples = []
        for u in np.linspace(-1, 1, 17):
            theta = a+u*.16
            y = lower+3*u*u
            samples.append(skirt_point(theta, y, -.6))
        trace(p, samples, 1.5, WHITE)
        trace(p, [(v[0], v[1]-1, v[2]) for v in samples], .65, WHITE_SHADE)

    # 裙片金边沿椭圆伞面延伸，正侧背共用同一弧面。
    for i in range(10):
        center = i*2*math.pi/10
        tip_y = 107 if i % 5 else 109
        petal = []
        for u in np.linspace(0, 1, 23):
            y = tip_y-(tip_y-87)*u
            spread = .18*math.sin(math.pi*u)**.7
            petal.append(skirt_point(center-spread, y, .8))
        for u in np.linspace(1, 0, 23):
            y = tip_y-(tip_y-87)*u
            spread = .18*math.sin(math.pi*u)**.7
            petal.append(skirt_point(center+spread, y, .8))
        trace(p, petal, 1.2, GOLD)
        trace(p, [skirt_point(center-.16, 95, 1), skirt_point(center-.1, 100, 1),
                  skirt_point(center, tip_y, 1)], .55, GOLD_LIGHT)

    front = [(-3, 108, 10), (-5, 103, 14), (-7, 98, 18), (-10, 92, 20),
             (-10, 87, 21), (-7, 85, 21), (0, 84, 21), (7, 85, 21),
             (10, 87, 21), (10, 92, 20), (7, 98, 18), (5, 103, 14), (3, 108, 10)]
    trace(p, front, 1.25, GOLD_LIGHT)
    ellipsoid(p, (0, 94, 21), (2.8, 2.5, .9), GOLD_DARK)
    ellipsoid(p, (0, 94, 22), (2, 1.7, .55), GOLD)
    p.points([(0, 99, 19), (0, 89, 22)], GOLD_LIGHT)
    return [p.finish()]
