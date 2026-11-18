import math

import numpy as np

from thousand_d1_common import (Part, trace, ellipsoid, BLACK, SEAM, WHITE,
    WHITE_SHADE, WHITE_LIGHT, GOLD, GOLD_LIGHT, GOLD_DARK, HAIR, HAIR_LIGHT, HAIR_SHADE)


def front_z(x, y):
    skull = 20*np.sqrt(np.maximum(0, 1-(x/22)**2-((y-177)/25)**2))
    jaw = 4+14*np.sqrt(np.maximum(0, 1-(x/16)**2-((y-165)/12)**2))
    return np.maximum(skull, np.where((x/16)**2+((y-165)/12)**2 <= 1, jaw, 0))


def face_line(part, points, radius, state):
    trace(part, [(x, y, float(front_z(x, y))+.7) for x, y in points], radius, state)


def crown(part, side):
    a, b = np.array([side*22, 194, -4.]), np.array([side*34, 209, -6.])
    axis = b-a
    length = np.linalg.norm(axis)
    direction = axis/length
    x, y, z = np.mgrid[-38:39, 185:212, -16:9]
    q = np.stack((x, y, z), axis=-1)
    axial = (q-a)@direction
    t = axial/length
    radial = np.linalg.norm(q-a-axial[..., None]*direction, axis=-1)
    radius = 9-7*t
    mask = (t >= 0) & (t <= 1) & (radial <= radius)
    state = np.full(x.shape, GOLD, np.uint8)
    surface = radial >= radius-1.6
    state[mask & surface & (z > -5)] = GOLD_LIGHT
    for ring in (.15, .56, .85):
        state[mask & surface & (np.abs(t-ring) < .035)] = GOLD_DARK
    state[mask & surface & (np.abs(z+5+.13*axial) < .55)] = GOLD_DARK
    where = np.where(mask)
    part.points(np.c_[x[where], y[where], z[where]], state[where])
    center = a+axis*.27+np.array([0, 0, 7.2])
    part.ring(center, 2.4, 1, GOLD_DARK, normal=(0, 0, 1), depth=1.4)
    ellipsoid(part, center+[0, 0, .3], [1.5, 1.5, .8], GOLD_LIGHT)


def side_lock(side):
    part = Part(f'head_lock_{side:+}', '奶金长侧发', section='head',
        pivot=[side*19, 186, 10], parent='head', references=['SA003', 'SA014', 'SA033'])
    control = np.array([[side*19, 186, 10], [side*27, 167, 15],
        [side*25, 133, 21], [side*15, 126, 18]], float)
    for t in np.linspace(0, 1, 75):
        center = (1-t)**3*control[0]+3*(1-t)**2*t*control[1]+3*(1-t)*t*t*control[2]+t**3*control[3]
        width, depth = 3.7*(1-t)**.65+.4, 2.1*(1-t)**.5+.4
        ellipsoid(part, center, [width, 1.6, depth], HAIR_SHADE)
        ellipsoid(part, center+[0, 0, .5], [width*.83, 1.5, depth*.82], HAIR)
        if t < .9:
            ellipsoid(part, center+[-side*width*.38, 0, depth*.65], [max(.45, width*.22), 1.2, .6], HAIR_LIGHT)
    return part.finish()


def build_head():
    x, y, z = np.mgrid[-27:28, 153:205, -25:25]
    volume = np.zeros(x.shape, np.uint8)
    skull = (x/22)**2+((y-177)/25)**2+(z/20)**2
    jaw = (x/16)**2+((y-165)/12)**2+((z-4)/14)**2
    shell = (skull <= 1) | (jaw <= 1)
    volume[shell] = WHITE_SHADE
    volume[shell & (z >= -1)] = WHITE
    volume[shell & (z >= 8) & (x < -6)] = WHITE_LIGHT
    hair_ellipsoid = (x/24)**2+((y-179)/25)**2+((z+2)/21)**2
    hairline = 195-.83*np.abs(x)
    hair = (hair_ellipsoid <= 1) & (y >= 160) & ((z < 4) | (y > hairline))
    volume[hair] = HAIR
    volume[hair & (y > 192) & (x < 9)] = HAIR_LIGHT
    volume[hair & (z < -16) & (y < 180)] = HAIR_SHADE
    angle = np.arctan2(x, z+2)
    seams = hair & (hair_ellipsoid > .82) & (np.abs(np.sin(4*angle+.017*(y-179))) < .05)
    volume[seams] = HAIR_SHADE
    rear_sweep = hair & (z < -8) & (hair_ellipsoid > .82) & (np.abs(y-175-.11*x-.012*x*x) < .55)
    volume[rear_sweep] = HAIR_SHADE
    top = 181+.08*np.abs(x)-2*np.exp(-(x/4)**2)
    bottom = 168+.035*(np.abs(x)-10)**2
    eye = shell & ~hair & (z >= front_z(x, y)-2) & (z > 1) & (y >= bottom) & (y <= top)
    volume[eye] = BLACK
    where = np.where(volume)
    part = Part('head', '白瓷蒙眼脸、双锥冠与分片发壳', section='head',
        pivot=[0, 149, 0], parent='body', references=['SA003', 'SA010', 'SA014', 'SA020', 'SA033'],
        notes='按薪炎永燃金发蒙眼人偶重建，保留双锥冠、三叶额纹、后脑金回折与菱扣。')
    part.points(np.c_[x[where], y[where], z[where]], volume[where])
    for side in (-1, 1):
        ellipsoid(part, [side*22, 172, -1], [2.8, 4.1, 2.3], WHITE_SHADE)
        trace(part, [(side*23, 174, 0), (side*23.5, 172, 1), (side*22.5, 170, 1)], .6, SEAM)
        crown(part, side)
        for yy, zz in [(178, 12), (173, 13)]:
            part.hull([(side*18, yy+1.5, zz), (side*23, yy+1, zz-3),
                (side*19, yy-1, zz+1), (side*18, yy+.5, zz-1)], GOLD)
    face_line(part, [(-18, 182), (-11, 181.5), (-4, 181), (0, 178.5),
        (4, 181), (11, 181.5), (18, 182)], .8, GOLD)
    for theta in (math.pi/2, math.pi/2+2*math.pi/3, math.pi/2+4*math.pi/3):
        u, v = np.array([math.cos(theta), math.sin(theta)]), np.array([-math.sin(theta), math.cos(theta)])
        points = [np.array([0, 188.5])+u*(3-3*math.cos(t))+v*(1.9*math.sin(t)) for t in np.linspace(0, 2*math.pi, 48)]
        face_line(part, points, .85, GOLD)
    ellipsoid(part, [-.5, 165.8, 18], [1.5, 2.1, 1.9], WHITE_LIGHT)
    face_line(part, [(-10, 162), (-8, 161), (-7, 159.5), (-5, 161),
        (0, 160.5), (5, 161), (7, 159.5), (8, 161), (10, 162)], .8, SEAM)
    for side in (-1, 1):
        face_line(part, [(side*11, 155.5), (side*15, 158), (side*18, 162), (side*19, 166)], .5, SEAM)
    rear_rim = [(-21, 166, -10), (-17, 163, -16), (-10, 162, -19),
        (-5, 164, -20), (0, 161, -21), (5, 164, -20), (10, 162, -19),
        (17, 163, -16), (21, 166, -10)]
    trace(part, rear_rim, 1.5, GOLD_DARK)
    trace(part, [(a, b+.6, c-.5) for a, b, c in rear_rim], 1.1, GOLD)
    for side in (-1, 1):
        xx = side*5.5
        trace(part, [(xx-2, 165, -21), (xx, 167, -21), (xx+2, 165, -21),
            (xx, 163, -21), (xx-2, 165, -21)], .7, GOLD_LIGHT)
    return [part.finish(), side_lock(-1), side_lock(1)]
