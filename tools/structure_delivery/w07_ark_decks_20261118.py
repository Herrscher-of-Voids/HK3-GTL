# -*- coding: utf-8 -*-
from w07_ark_common_20261118 import *


TIERS = [(103, 190, 224, -315, 245, 28),
         (78, 225, 253, -230, 168, 26),
         (50, 254, 278, -145, 85, 22)]


def damaged(x, z, tier):
    holes = [[(-207, 85, 62), (16, 78, 75), (187, 93, 42)],
             [(-137, 66, 49), (89, 62, 46)],
             [(-71, 36, 36), (64, 42, 32)]][tier]
    return any(((z - cz) / rz) ** 2 + ((x - cx) / 44) ** 2 < 1 for cz, cx, rz in holes)


def cabin(side, tier):
    width, bottom, top, back, front, rise = TIERS[tier]
    white = side > 0
    wall, frame = (WHITE, SILVER) if white else (DARK, RIB)
    part = Part(('life' if white else 'decay') + f'_cabin_{tier + 1}',
                ('创生' if white else '凋亡') + f'侧第{tier + 1}层船屋',
                group='deck_white' if white else 'deck_dark')
    left, right = sorted([side * 9, side * width])
    part.box([left, bottom - 3, back], [right, bottom, front], CLEAN if white else ASH)
    for z in range(back, front + 1):
        if tier == 0:
            part.box([left, deck_at(z), z], [right, bottom - 3, z], CLEAN if white else ASH)
        for y in range(bottom + 1, top + 1):
            if white or not damaged(width, z, tier):
                state = GLASS if bottom + 9 <= y <= top - 8 and (z - back) % 49 in range(12, 35) else wall
                part.box([side * (width - 2), y, z], [side * width, y, z], state)
        for x in range(9, width + 6):
            roof_y = top + round(rise * (1 - min(x, width) / width))
            if white or not damaged(x, z, tier):
                state = frame if (z - back) % 49 < 3 or x >= width else wall
                part.box([side * x, roof_y, z], [side * x, roof_y + 2, z], state)
    for z in [back, front]:
        for x in range(9, width + 1):
            roof_y = top + round(rise * (1 - x / width))
            if white or not damaged(x, z, tier):
                part.box([side * x, bottom + 1, z], [side * x, roof_y, z + 2], wall)
        for xa, xb in [(21, 37), (51, 67)]:
            if xb < width:
                part.box([side * xa, bottom + 8, z - 1], [side * xb, top - 8, z + 3], GLASS if white else GRATE)
        if tier == 0:
            part.box([side * 15, bottom + 1, z - 1], [side * 29, bottom + 20, z + 3], GLASS if white else GRATE)
            part.box([side * 14, bottom + 21, z - 1], [side * 30, bottom + 23, z + 3], frame)
    for z in range(back, front + 1, 49):
        height = top if white or (z // 49) % 3 else top - 12
        part.box([side * (width - 3), bottom, z], [side * width, height, z + 3], frame)
        roof_points = [[side * x, top + round(rise * (1 - x / width)) + 1, z + 1]
                       for x in range(11, width + 2, 5)]
        polyline(part, roof_points, 2, frame)
        part.box([side * 10, bottom, z], [side * width, bottom + 2, z + 3], frame)
    for z in range(back + 17, front - 10, 49):
        if white:
            part.box([side * (width + 1), bottom + 5, z], [side * (width + 2), bottom + 6, z + 16], LIGHT)
        elif (z // 49) % 3 == 0:
            part.box([side * (width - 4), bottom + 4, z], [side * (width - 1), bottom + 7, z + 14], GRATE)
    return part.finish()


def greenhouse(index, z):
    part = Part(f'life_greenhouse_{index + 1}', f'创生甲板第{index + 1}座种子温室', group='life')
    x0, x1, z0, z1, y = 114, 164, z - 27, z + 27, deck_at(z) + 1
    part.box([x0, y, z0], [x1, y + 3, z1], CLEAN)
    part.box([x0 + 3, y + 4, z0 + 3], [x1 - 3, y + 4, z1 - 3], SOIL)
    part.box([x0 + 4, y + 5, z0 + 4], [x1 - 4, y + 5, z1 - 4], MOSS)
    for zz in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            height = 12 + round(12 * np.sqrt(1 - ((x - 139) / 25) ** 2))
            state = WHITE if (zz - z0) % 13 < 2 or x in [x0, x1] else GLASS
            part.box([x, y + height, zz], [x, y + height + 1, zz], state)
        for x in [x0, x1]:
            part.box([x, y + 4, zz], [x, y + 12, zz], WHITE if (zz - z0) % 13 < 2 else GLASS)
    for zz in [z0, z1]:
        for x in range(x0, x1 + 1):
            height = 12 + round(12 * np.sqrt(1 - ((x - 139) / 25) ** 2))
            if x < 133 or x > 145:
                part.box([x, y + 4, zz], [x, y + height, zz], GLASS)
            else:
                part.box([x, y + 15, zz], [x, y + height, zz], GLASS)
        for x in [132, 146]:
            part.box([x, y + 4, zz], [x, y + 16, zz], SILVER)
        part.box([132, y + 16, zz], [146, y + 17, zz], WHITE)
    for x in [118, 158]:
        part.box([x, y + 4, z0 + 4], [x + 2, y + 5, z1 - 4], SILVER)
        part.box([x, y + 6, z0 + 7], [x + 2, y + 6, z1 - 7], LIGHT)
    return part.finish()


def gardens():
    flora = Part('living_seed_archive', '完整橡树与白花种植槽', group='life')
    for index, z in enumerate([-160, -80, 0, 80, 160]):
        y = deck_at(z) + 7
        flora.box([137, y, z - 1], [139, y + 6 + index % 2, z + 1], LOG_BLOCK)
        for dy, radius in [(4, 4), (5, 5), (6, 5), (7, 4), (8, 3), (9, 1)]:
            for x in range(-radius, radius + 1):
                for zz in range(-radius, radius + 1):
                    if abs(x) + abs(zz) <= radius * 1.6:
                        flora.points([[138 + x, y + dy + index % 2, z + zz]], LEAVES)
        for zz in range(z - 17, z + 18, 9):
            for x in [122, 153]:
                flora.box([x - 2, y - 1, zz - 2], [x + 2, y, zz + 2], CLEAN)
                flora.box([x - 1, y + 1, zz - 1], [x + 1, y + 1, zz + 1], MOSS)
                flora.points([[x, y + 2, zz]], LIGHT)
                flora.points([[x - 1, y + 2, zz], [x + 1, y + 2, zz],
                              [x, y + 2, zz - 1], [x, y + 2, zz + 1]], FLOWER)
    return flora.finish()


def decay_deck():
    part = Part('decay_deck_equipment', '凋亡侧枯枝与分解甲板设备', group='deck_dark')
    for z in [-176, 158]:
        y = deck_at(z) + 1
        part.box([-165, y, z - 25], [-114, y + 3, z + 25], RIB)
        for zz in range(z - 21, z + 22, 14):
            framed_box(part, [-157, y + 4, zz - 4], [-122, y + 14, zz + 4], DARK, ASH, 2)
            part.box([-151, y + 5, zz - 3], [-128, y + 12, zz + 3], GRATE)
        polyline(part, [[-117, y + 6, z - 20], [-110, y + 6, z - 20],
                        [-110, y + 18, z], [-113, y + 18, z + 20]], 2, ASH)
    for z in [-375, 323]:
        y = deck_at(z) + 1
        x = -111
        part.box([x - 6, y, z - 6], [x + 6, y + 3, z + 6], RIB)
        polyline(part, [[x, y + 4, z], [x - 1, y + 11, z], [x + 1, y + 16, z - 1]], 1.5, LOG_BLOCK)
        polyline(part, [[x - 1, y + 10, z], [x - 5, y + 13, z + 1], [x - 7, y + 13, z + 3]], 1, LOG_BLOCK)
        polyline(part, [[x, y + 12, z], [x + 4, y + 15, z - 3], [x + 5, y + 18, z - 3]], 1, LOG_BLOCK)
    return part.finish()


def belly_machinery(side):
    white = side > 0
    part = Part('regeneration_machines' if white else 'decomposition_machines',
                '船腹白色再构设备' if white else '船腹裸露分解设备', group='machinery')
    shell, frame = (CLEAN, SILVER) if white else (DARK, RIB)
    for z in [-275, 0, 260]:
        x0, x1 = sorted([side * 43, side * 99])
        part.box([x0, 110, z - 29], [x1, 115, z + 29], frame)
        framed_box(part, [x0 + 4, 116, z - 25], [x1 - 4, 159, z + 25], shell, frame, 3)
        part.box([x0 + 8, 121, z - 20], [x1 - 8, 153, z + 20], MACHINE)
        part.box([side * 98, 124, z - 18], [side * 101, 151, z + 18], GLASS if white else GRATE)
        for zz in [z - 16, z, z + 16]:
            part.box([x0 + 8, 156, zz - 2], [x1 - 8, 160, zz + 2], LIGHT if white else GRATE)
        part.box([side * 59, 121, z - 13], [side * 79, 147, z + 13], CORE)
        part.box([side * 97, 133, z - 7], [side * 102, 141, z + 7], LIGHT if white else ASH)
        polyline(part, [[side * 47, 145, z - 24], [side * 31, 145, z - 24],
                        [side * 31, 166, z - 24], [side * 14, 166, z - 24]], 3, frame)
        for zz in [z - 24, z + 24]:
            part.box([side * 43, 115, zz - 2], [side * 99, 119, zz + 2], GRATE)
    polyline(part, [[side * 35, 156, -304], [side * 35, 156, 289]], 3, frame)
    return part.finish()


def build():
    parts = [cabin(side, tier) for tier in range(3) for side in [-1, 1]]
    parts += [greenhouse(index, z) for index, z in enumerate([-160, -80, 0, 80, 160])]
    parts += [gardens(), decay_deck(), belly_machinery(-1), belly_machinery(1)]
    return parts
