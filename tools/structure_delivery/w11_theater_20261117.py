import math

import numpy as np

from w11_common_20261117 import (
    Part, rod, BLACK, STUDS, WHITE, GOLD, RED, MAGENTA, LIGHT,
    WHITE_LIGHT, GLASS, GRAY, HK, CONTROLLER, line,
)


RINGS = ((212, 40), (320, 64), (440, 96))
CENTER = -.5


def cabin_layout():
    cabins = []
    for level in range(5):
        y = 46 + level * 23
        for ring, (radius, count) in enumerate(RINGS, 1):
            for index in range(count):
                theta = math.tau * (index + .5) / count
                cx = round(CENTER + radius * math.cos(theta))
                cz = round(CENTER + radius * math.sin(theta))
                wire_radius = radius + 40 - 6 * level
                wx = round(CENTER + wire_radius * math.cos(theta))
                wz = round(CENTER + wire_radius * math.sin(theta))
                cabins.append(dict(cx=cx, cz=cz, y=y, ring=ring, level=level + 1,
                    theta=theta, sector=index // (count // 8),
                    string_top=[wx, 266 + 9 * level, wz],
                    roof_anchor=[cx, y + 20, cz], string_elbow=[wx, y + 20, wz]))
    return cabins


def axes(cabin):
    x, z = cabin['cx'] - CENTER, cabin['cz'] - CENTER
    if abs(x) >= abs(z):
        vx, vz = (1 if x > 0 else -1), 0
    else:
        vx, vz = 0, (1 if z > 0 else -1)
    return vz, -vx, vx, vz


def box(part, cabin, low, high, state):
    ux, uz, vx, vz = axes(cabin)
    a, b = low, high
    part.box([cabin['cx'] + a[0] * ux + a[2] * vx, cabin['y'] + a[1],
              cabin['cz'] + a[0] * uz + a[2] * vz],
             [cabin['cx'] + b[0] * ux + b[2] * vx, cabin['y'] + b[1],
              cabin['cz'] + b[0] * uz + b[2] * vz], state)


def build_cabin(part, cabin):
    box(part, cabin, [-7, 0, -7], [7, 0, 7], STUDS)
    box(part, cabin, [-7, 19, -7], [7, 19, 7], STUDS)
    for u in (-7, 7):
        box(part, cabin, [u, 1, -7], [u, 18, 7], BLACK)
        box(part, cabin, [u, 6, -4], [u, 14, 4], GLASS)
    box(part, cabin, [-6, 1, 7], [6, 18, 7], BLACK)
    box(part, cabin, [-4, 6, 7], [4, 14, 7], GLASS)
    box(part, cabin, [-2, 2, 7], [2, 4, 7], HK)
    for u in (-5, 5):
        box(part, cabin, [u, 3, 7], [u, 16, 7], GRAY)
    box(part, cabin, [-6, 1, -7], [-3, 18, -7], BLACK)
    box(part, cabin, [3, 1, -7], [6, 18, -7], BLACK)
    box(part, cabin, [-2, 6, -7], [2, 18, -7], BLACK)
    box(part, cabin, [-5, 6, -7], [5, 17, -7], WHITE)
    box(part, cabin, [-4, 14, -7], [-1, 15, -7], BLACK)
    box(part, cabin, [1, 14, -7], [4, 15, -7], BLACK)
    eye = RED if (cabin['ring'] + cabin['level']) % 2 else MAGENTA
    box(part, cabin, [-4, 13, -7], [-2, 13, -7], eye)
    box(part, cabin, [2, 13, -7], [4, 13, -7], eye)
    box(part, cabin, [0, 10, -7], [0, 13, -7], GOLD)
    box(part, cabin, [-3, 8, -7], [3, 8, -7], BLACK)
    for u in (-2, 0, 2):
        box(part, cabin, [u, 8, -7], [u, 8, -7], GRAY)
    for u in (-7, 7):
        for v in (-7, 7):
            box(part, cabin, [u, 1, v], [u, 18, v], GOLD)
    for v in (-7, 7):
        box(part, cabin, [-7, 18, v], [7, 18, v], GOLD)
    box(part, cabin, [-2, 19, -2], [2, 19, 2], WHITE_LIGHT)


def arc(part, radius, y, start, end, state):
    angles = np.linspace(start, end, math.ceil((end - start) * radius * 2) + 1)
    part.points(np.c_[CENTER + radius * np.cos(angles), np.full(len(angles), y),
        CENTER + radius * np.sin(angles)], state)


def build_walkways(part, radius, y, sector):
    start, end = sector * math.pi / 4, (sector + 1) * math.pi / 4
    for r in (*range(radius - 10, radius - 6), *range(radius + 12, radius + 16)):
        arc(part, r, y, start, end, GRAY)
    for r in (radius - 10, radius + 15):
        arc(part, r, y + 1, start, end, BLACK)
        for theta in (start, (start + end) / 2, end):
            x, z = round(CENTER + r * math.cos(theta)), round(CENTER + r * math.sin(theta))
            part.box([x, y + 1, z], [x, y + 2, z], GOLD)


def connect_cabin(part, cabin, radius):
    ux, uz, vx, vz = axes(cabin)
    cx, cz, y, theta = cabin['cx'], cabin['cz'], cabin['y'], cabin['theta']
    for side, walkway_radius in ((-1, radius - 8), (1, radius + 13)):
        end = [round(CENTER + walkway_radius * math.cos(theta)), y,
               round(CENTER + walkway_radius * math.sin(theta))]
        for width in (-1, 0, 1):
            line(part, [cx + side * 7 * vx + width * ux, y, cz + side * 7 * vz + width * uz],
                 [end[0] + width * ux, y, end[2] + width * uz], STUDS)
    line(part, cabin['roof_anchor'], cabin['string_elbow'], GOLD)
    index = int(theta / math.tau * RINGS[cabin['ring'] - 1][1])
    wire = GOLD if (index + cabin['level']) % 4 == 0 else RED
    line(part, cabin['string_elbow'], cabin['string_top'], wire)
    part.points([cabin['roof_anchor'], cabin['string_top']], LIGHT)


def build_theater():
    cabins, parts = cabin_layout(), []
    for level in range(1, 6):
        y = 46 + (level - 1) * 23
        for ring, (radius, count) in enumerate(RINGS, 1):
            for sector in range(8):
                selected = [cabin for cabin in cabins
                    if cabin['level'] == level and cabin['ring'] == ring and cabin['sector'] == sector]
                part = Part(f'theater_r{ring}_l{level}_s{sector + 1}',
                    f'第{level}层第{ring}圈第{sector + 1}扇区机舱与提线', section='theater',
                    count=len(selected), ring=ring, level=level, radius=radius, sector=sector + 1,
                    cabin_size_xyz=[15, 20, 15], floor_y=y, hollow_interior=True,
                    motion_kind='固定方块参考姿态', inner_ring_nominal_boundary=200)
                build_walkways(part, radius, y, sector)
                for cabin in selected:
                    build_cabin(part, cabin)
                    connect_cabin(part, cabin, radius)
                arc(part, radius + 40 - 6 * (level - 1), 266 + 9 * (level - 1),
                    sector * math.pi / 4, (sector + 1) * math.pi / 4, RED if level % 2 else GOLD)
                parts.append(part.finish())
    return parts
