# -*- coding: utf-8 -*-
from w07_ark_common_20261118 import *


def hull():
    dark = Part('dark_shell', '黑色凋亡船壳', group='hull_dark')
    white = Part('white_shell', '白色创生船壳', group='hull_white')
    frames = Part('shared_keel', '共用龙骨与裸露肋架', group='spine')
    dark_deck = Part('broken_deck', '凋亡侧破损甲板', group='deck_dark')
    white_deck = Part('complete_deck', '创生侧完整甲板', group='deck_white')
    for z in range(-470, 502):
        bottom, top = bottom_at(z), deck_at(z)
        ys = np.arange(bottom, top + 1)
        radii = radius_at(ys, z)
        x, y = np.meshgrid(np.arange(-197, 198), ys)
        radius = np.broadcast_to(radii[:, None], x.shape)
        shell = (np.abs(x) <= radius) & ((np.abs(x) >= radius - 4) | (y <= bottom + 3))
        if z in [-470, -469, -468, -467]:
            shell = np.abs(x) <= radius
        decay = np.zeros(x.shape, bool)
        for cz, cy, rz, ry in [(-278, 133, 69, 43), (-26, 155, 106, 54), (261, 173, 72, 43)]:
            decay |= ((z - cz) / rz) ** 2 + ((y - cy) / ry) ** 2 < 1 + .10 * np.sin(z * .18) + .06 * np.cos(y * .31)
        left = shell & (x < -4) & ~((np.abs(x) > 42) & decay)
        right = shell & (x > 4)
        for mask, part, base, plate in [(left, dark, DARK, ASH), (right, white, WHITE, CLEAN)]:
            seams = ((y - bottom) % 25 < 2) | ((z + 470) % 57 < 2)
            panel = ((z // 57 + (y - bottom) // 25) % 7 == 0) & ~seams
            for current, state in [(mask & ~seams & ~panel, base), (mask & panel, plate), (mask & seams, RIB if part is dark else SILVER)]:
                xx, yy = x[current], y[current]
                part.points(np.c_[xx, yy, np.full(len(xx), z)], state)
            windows = mask & (y >= top - 22) & (y <= top - 14) & ((z + 470) % 57 >= 16) & ((z + 470) % 57 <= 36)
            xx, yy = x[windows], y[windows]
            part.points(np.c_[xx, yy, np.full(len(xx), z)], GRATE if part is dark else GLASS)
        w = int(width_at(z)) - 3
        for side, part, state in [(-1, dark_deck, ASH), (1, white_deck, CLEAN)]:
            xx = np.arange(8, w + 1) * side
            if side < 0:
                missing = ((xx + 100) / 73) ** 2 + ((z + 20) / 105) ** 2 < 1 + .06 * np.sin(z * .17)
                missing |= ((xx + 117) / 43) ** 2 + ((z + 291) / 57) ** 2 < 1
                xx = xx[~missing]
            for yy in range(top - 2, top + 1):
                part.points(np.c_[xx, np.full(len(xx), yy), np.full(len(xx), z)], state)
            if len(xx):
                edge = side * w
                for yy in range(top + 1, top + 6):
                    if side > 0 or (z // 29) % 5 not in [1, 2]:
                        part.points([[edge, yy, z], [edge - side, yy, z]], WHITE if side > 0 else RIB)
        for xx in range(-4, 5):
            frames.points([[xx, bottom - 6, z], [xx, bottom - 5, z], [xx, bottom - 4, z]], RIB)
        for yy in range(bottom - 3, bottom + 5):
            frames.points([[-6, yy, z], [6, yy, z]], SILVER)
        for xx in [-7, 7]:
            frames.points([[xx, top, z], [xx, top + 1, z]], LIGHT)
    for index, z in enumerate(range(-444, 480, 44)):
        bottom, top = bottom_at(z), deck_at(z)
        for side in [-1, 1]:
            levels = np.linspace(bottom + 5, top - 4, 15)
            points = [[side * (radius_at(y, z) - 8), y, z] for y in levels]
            if side < 0 and index % 6 in [1, 2]:
                points = points[:-3]
            polyline(frames, points, 4, RIB if side < 0 else SILVER)
        frames.box([-8, bottom + 3, z - 4], [8, top - 7, z + 4], RIB)
        frames.box([-9, bottom + 8, z - 5], [9, bottom + 14, z + 5], CORE)
    polyline(frames, [[0, bottom_at(z) - 3, z] for z in range(-470, 502, 8)], 5, RIB)
    polyline(frames, [[0, 177, -470], [0, 207, -477], [0, 232, -483]], 7, SILVER)
    polyline(frames, [[0, 156, 490], [0, 190, 505], [0, 230, 522], [0, 246, 525]], 7, WHITE)
    return [part.finish() for part in [dark, white, frames, dark_deck, white_deck]]


def dock():
    part = Part('dry_dock', '工业干船坞与承托架', group='dock')
    for side in [-1, 1]:
        x0, x1 = sorted([side * 235, side * 278])
        part.box([x0, 0, -520], [x1, 17, 545], DARK)
        part.box([x0 + 3, 18, -515], [x1 - 3, 20, 540], ASH)
        for x in [x0 + 2, x1 - 2]:
            part.box([x, 21, -515], [x + 1, 23, 540], SILVER)
        for z in range(-485, 530, 44):
            part.box([x0 + 9, 21, z], [x1 - 9, 21, z + 10], GRATE)
            part.box([x0 + 3, 21, z + 15], [x0 + 5, 21, z + 17], LIGHT)
    part.box([-278, 0, -546], [278, 20, -520], RIB)
    part.box([-278, 0, 540], [278, 20, 567], RIB)
    part.box([-39, 0, 540], [39, 20, 590], ASH)
    part.box([-32, 20, 546], [32, 20, 583], CLEAN)
    part.box(CONTROLLER, CONTROLLER, CONTROL)
    for z in range(-425, 451, 88):
        bottom = bottom_at(z)
        part.box([-237, 7, z - 10], [237, 17, z + 10], RIB)
        part.box([-18, 18, z - 9], [18, bottom - 8, z + 9], ASH)
        for side in [-1, 1]:
            x, y = side * radius_at(bottom + 24, z), bottom + 24
            rod(part, [side * 174, 18, z], [x, y - 7, z], 6, ASH)
            rod(part, [side * 174, 18, z], [side * 36, bottom - 6, z], 4, RIB)
            rod(part, [x - side * 8, y - 8, z], [x + side * 8, y - 8, z], 6, CLEAN)
    for index, z in enumerate([-325, -91, 92, 312]):
        x = -207 - index % 2 * 8
        part.box([x - 11, 18, z - 26], [x + 8, 22 + index * 2, z + 18], ASH)
        part.box([x - 8, 23, z - 20], [x + 5, 24, z + 13], DARK)
    return [part.finish()]
