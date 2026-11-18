import math

import numpy as np

from thousand_d1_common import (
    BLACK, CLOTH, CLOTH_LIGHT, GOLD, GOLD_DARK, GOLD_LIGHT, SEAM,
    WHITE, WHITE_LIGHT, WHITE_SHADE, Part, ellipsoid, trace,
)


def tapered(part, start, end, start_radii, end_radii, state):
    a, b = np.asarray(start, float), np.asarray(end, float)
    axis = (b-a)/np.linalg.norm(b-a)
    u = np.cross(axis, [0, 0, 1])
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    vertices = []
    for center, radii in [(a, start_radii), (b, end_radii)]:
        for angle in np.arange(8)*math.pi/4:
            vertices.append(center+u*math.cos(angle)*radii[0]+v*math.sin(angle)*radii[1])
    part.hull(vertices, state)


def upper_arm(side, suffix):
    shoulder = [side*25, 140, 0]
    elbow = [side*33, 113, 0]
    part = Part('arm_'+suffix, '黑色长袖上臂', section='arms', pivot=shoulder, parent='body')
    tapered(part, [side*26, 136, 0], [side*32.5, 117, 0], [4.3, 4], [3.6, 3.5], CLOTH)
    ellipsoid(part, elbow, [4.2, 4, 3.8], BLACK)
    ellipsoid(part, [side*36.5, 113, 0], [1, 2.7, 2.7], CLOTH_LIGHT)
    trace(part, [[side*26.5, 133, 3.7], [side*30, 129, 3.7], [side*29, 125, 3.7]], .65, CLOTH_LIGHT)
    trace(part, [[side*29, 132, 3.6], [side*31.5, 128, 3.5], [side*31, 123, 3.4]], .6, CLOTH_LIGHT)
    return part.finish()


def forearm(side, suffix):
    elbow = [side*33, 113, 0]
    wrist = [side*39, 88, 2]
    part = Part('forearm_'+suffix, '黑色长袖前臂与金袖口', section='arms', pivot=elbow, parent='arm_'+suffix)
    tapered(part, [side*33.5, 110, .2], [side*38.6, 90, 1.8], [3.8, 3.7], [2.8, 2.8], CLOTH)
    tapered(part, [side*35.5, 107, 2.3], [side*38.4, 92, 3.7], [1, .6], [.6, .4], CLOTH_LIGHT)
    part.ring([side*38.7, 89.5, 1.9], 3.5, 1.2, GOLD, normal=np.asarray(wrist)-elbow, depth=2)
    ellipsoid(part, wrist, [2.3, 2.5, 2.3], GOLD_DARK)
    for offset in [-1, 1]:
        part.hull([[side*(38+offset*2.5), 92, 3], [side*(39+offset*2), 87, 4],
                   [side*(39+offset*.5), 88, 4], [side*(38+offset), 91, 3.7],
                   [side*(38+offset*2), 90, 2.8]], GOLD_LIGHT)
    return part.finish()


def hand(side, suffix):
    wrist = [side*39, 88, 2]
    part = Part('hand_'+suffix, '金色五指机械手', section='hands', pivot=wrist, parent='forearm_'+suffix)
    tapered(part, [side*39, 86.5, 2], [side*39, 79, 2.5], [3.5, 2.3], [4.2, 2.2], GOLD)
    ellipsoid(part, [side*39, 82.5, 2.6], [4.1, 4.1, 2.4], GOLD)
    for offset, length in [(-3, 7), (-1, 10), (1, 9), (3, 7)]:
        x = side*(39+offset)
        y0, y1, y2, y3 = 79, 76, 73, 79-length
        for a, b in [(y0, y1), (y1, y2), (y2, y3)]:
            tapered(part, [x, a, 2.5], [x, b, 3], [.85, 1.25], [.75, 1], GOLD_LIGHT)
        for y in [y1, y2]:
            tapered(part, [x, y+.25, 2.7], [x, y-.35, 2.7], [.9, 1.2], [.9, 1.2], GOLD_DARK)
        ellipsoid(part, [x, y3, 3], [.75, .85, 1], GOLD)
    tapered(part, [side*35.5, 83, 2.3], [side*32.5, 79, 3], [1.7, 1.6], [1.1, 1.3], GOLD)
    ellipsoid(part, [side*32.5, 79, 3], [1.4, 1.3, 1.4], GOLD_DARK)
    tapered(part, [side*32.5, 78.5, 3], [side*32, 75.5, 4], [1.2, 1.2], [.9, 1], GOLD_LIGHT)
    part.hull([[side*35.8, 82.5, 4.5], [side*39, 84, 5], [side*42.2, 82.5, 4.5],
               [side*39, 81, 5], [side*39, 82.5, 4.2]], GOLD_DARK)
    ellipsoid(part, [side*39, 82.5, 5], [1, 1, .6], GOLD_LIGHT)
    trace(part, [[side*36, 85, 4], [side*39, 86, 4.4], [side*42, 85, 4]], .55, GOLD_LIGHT)
    return part.finish()


def thigh(side, suffix):
    hip = [side*12, 88, 0]
    part = Part('thigh_'+suffix, '白瓷分瓣大腿', section='legs', pivot=hip, parent='body')
    tapered(part, hip, [side*14, 50.5, 1], [3.5, 3.5], [3.2, 3.2], BLACK)
    ellipsoid(part, hip, [5.3, 5.2, 4.8], WHITE_SHADE)
    tapered(part, [side*12.3, 83, .1], [side*13.8, 56, .8], [5.8, 5.1], [4.2, 3.9], WHITE)
    tapered(part, [side*12.4, 81, 4.2], [side*13.7, 58, 4], [2.8, .8], [2.1, .7], WHITE_LIGHT)
    trace(part, [[side*16.6, 81, 1.9], [side*17.2, 70, 2], [side*17.2, 58, 2]], 1.1, WHITE_SHADE)
    trace(part, [[side*14.8, 82, 4.5], [side*15.5, 70, 4.3], [side*16.2, 58, 3.5]], .55, SEAM)
    ellipsoid(part, [side*13.8, 54, 1], [3.5, 2.3, 3.4], BLACK)
    return part.finish()


def shin(side, suffix):
    knee = [side*14, 49, 1]
    part = Part('shin_'+suffix, '白瓷膝球与小腿', section='legs', pivot=knee, parent='thigh_'+suffix)
    tapered(part, knee, [side*14, 10, 0], [2.7, 2.7], [2.4, 2.4], BLACK)
    ellipsoid(part, knee, [4.9, 4.7, 4.6], WHITE_SHADE)
    ellipsoid(part, [side*14, 49, 4], [3.9, 3.9, 1.8], WHITE_LIGHT)
    ellipsoid(part, [side*18.5, 49, 1], [.9, 2, 2], SEAM)
    tapered(part, [side*14, 43.5, .8], [side*14, 14, 0], [4.3, 4.2], [2.7, 3], WHITE)
    tapered(part, [side*13.8, 42, 4.1], [side*13.8, 15.5, 2.7], [1.8, .6], [1.2, .45], WHITE_LIGHT)
    trace(part, [[side*17.5, 42, 1.8], [side*17.3, 31, 1.6], [side*16.1, 16, 1.1]], .8, WHITE_SHADE)
    trace(part, [[side*11, 42, 3.2], [side*11.3, 30, 2.9], [side*12, 17, 2.4]], .5, SEAM)
    part.ring([side*14, 13, 0], 3.1, .8, GOLD_DARK, depth=1)
    return part.finish()


def foot(side, suffix):
    ankle = [side*14, 10, 0]
    part = Part('foot_'+suffix, '黑金短靴', section='legs', pivot=ankle, parent='shin_'+suffix)
    ellipsoid(part, [side*14, 7.5, 0], [3.5, 4.5, 3.9], BLACK)
    ellipsoid(part, [side*14, 3, 5], [4, 3, 7], CLOTH)
    part.box([side*14-3, 0, -2], [side*14+3, 1, 10], BLACK)
    part.ring([side*14, 10, 0], 3.6, .9, GOLD, depth=1)
    for offset in [-1, 1]:
        part.hull([[side*(14+offset*3), 3, 8], [side*(14+offset*3.5), 6, 4],
                   [side*(14+offset*1.8), 8, 3], [side*(14+offset*.7), 5, 7],
                   [side*(14+offset*1.8), 3, 10], [side*(14+offset*2), 3, 5]], GOLD)
    trace(part, [[side*11.5, 4, 10], [side*14, 5, 11], [side*16.5, 4, 10]], .6, GOLD_LIGHT)
    return part.finish()


def build_limbs():
    return [builder(side, suffix) for side, suffix in [(-1, 'l'), (1, 'r')]
            for builder in [upper_arm, forearm, hand, thigh, shin, foot]]
