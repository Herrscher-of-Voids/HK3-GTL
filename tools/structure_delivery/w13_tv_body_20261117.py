import numpy as np

from w13_tv_common_20261117 import (
    Part, rounded, box_shell, BLACK, STUDS, GRAY, SILVER, VENT,
    WHITE, GOLD, YELLOW, PINK, MAGENTA, RED, PINK_LIGHT,
    MAGENTA_LIGHT, RED_LIGHT, BLUE, WHITE_LIGHT, COMPUTER, ADVANCED, IWV,
)


def build_body():
    parts = []
    body = Part('main_cabinet', '深纵向切角主机壳', group='tv')
    x, y = np.meshgrid(np.arange(-420, 421), np.arange(370, 681))
    yy = y - 525
    for z in range(-220, 231):
        rear = max(0, -z - 100) / 120
        hx, hy = 420 - int(32 * rear), 155 - int(22 * rear)
        outer = rounded(x, yy, hx, hy, 24)
        shell = outer & ~rounded(x, yy, hx - 5, hy - 5, 24)
        if z <= -216:
            shell = outer
        if z >= 225:
            shell = outer & ~rounded(x, yy, 151, 92, 12)
        body.points(np.c_[x[shell], y[shell], np.full(shell.sum(), z)], BLACK)
    parts.append(body.finish())

    rim = Part('front_recess', '中央小屏凹框与前面板', group='tv')
    x, yy = np.meshgrid(np.arange(-420, 421), np.arange(-155, 156))
    for z in range(231, 266):
        d = z - 231
        if d < 15:
            outer = rounded(x, yy, 213, 123, 17)
            inner = rounded(x, yy, 188 + d // 3, 100 + d // 4, 13)
        else:
            outer = rounded(x, yy, 213 - (d - 15) // 2, 123 - (d - 15) // 2, 17)
            inner = rounded(x, yy, 193, 104, 14)
        mask = outer & ~inner
        state = STUDS if d < 21 else GRAY
        if d >= 29:
            state = SILVER
        rim.points(np.c_[x[mask] * .75, yy[mask] * .82 + 525, np.full(mask.sum(), z)], state)
    for sign in [-1, 1]:
        a, b = sorted([sign * 240, sign * 387])
        rim.box([a, 445, 231], [b, 615, 235], STUDS)
        rim.box([a + 7, 454, 236], [b - 7, 606, 237], BLACK)
        for y in range(466, 601, 22):
            rim.box([a + 15, y, 238], [b - 15, y + 3, 238], VENT)
        rim.box([sign * 231 - 2, 460, 237], [sign * 231, 503, 238], BLUE)
        rim.box([sign * 231 - 2, 542, 237], [sign * 231, 594, 238], BLUE)
        rim.box([a + 12, 421, 232], [b - 12, 428, 236], GRAY)
        rim.box([a + 19, 423, 237], [a + 27, 426, 237], WHITE_LIGHT)
        rim.box([a + 22, 631, 233], [b - 22, 635, 237], BLACK)
    rim.box([-124, 393, 231], [124, 407, 238], STUDS)
    for x in [-92, -54, -16, 22, 60]:
        rim.box([x, 397, 239], [x + 11, 400, 239], GRAY)
    parts.append(rim.finish())

    for index, z in enumerate([-191, -100, -9, 82, 173]):
        fold = Part(f'side_fold_{index}', f'第{index + 1}道U形折板', group='tv')
        for sign in [-1, 1]:
            outer, inner = sorted([sign * 433, sign * 413])
            fold.box([outer, 392, z], [inner, 651, z + 12], STUDS)
            fold.box([outer, 392, z], [inner, 407, z + 56], STUDS)
            fold.box([outer, 638, z], [inner, 651, z + 43], BLACK)
            a, b = sorted([sign * 434, sign * 438])
            fold.box([a, 409, z + 2], [b, 632, z + 5], GRAY)
            a, b = sorted([sign * 408, sign * 419])
            fold.box([a, 400, z + 18], [b, 620, z + 72], BLACK)
            a, b = sorted([sign * 420, sign * 423])
            for y in range(429, 616, 31):
                fold.box([a, y, z + 23], [b, y + 3, z + 63], VENT)
        fold.box([-365, 675, z], [365, 685, z + 13], STUDS)
        fold.box([-355, 682, z + 1], [355, 686, z + 3], GRAY)
        parts.append(fold.finish())

    lower = Part('underside', '错层底板与下挂机匣连接梁', group='tv')
    for sign in [-1, 1]:
        a, b = sorted([sign * 410, sign * 210])
        lower.box([a, 366, -151], [b, 373, 171], STUDS)
        lower.box([a + 10, 362, -140], [b - 10, 365, 161], GRAY)
        for z in [-116, -14, 88]:
            lower.box([a + 19, 358, z], [b - 19, 361, z + 41], BLACK)
    for x in [-181, -48, 98, 240]:
        lower.box([x, 359, -75], [x + 36, 378, 132], BLACK)
        lower.box([x + 5, 355, -68], [x + 31, 362, 119], STUDS)
    parts.append(lower.finish())

    rear = Part('rear_panels', '背面补全机壳与检修格栅', group='tv', inference='背面未获完整官方视角，按已见折板结构补全')
    box_shell(rear, [-330, 414, -231], [330, 630, -219], 4, STUDS)
    for x in [-286, -169, -52, 65, 182]:
        rear.box([x, 442, -235], [x + 83, 598, -232], VENT)
        rear.box([x + 6, 450, -237], [x + 77, 590, -236], BLACK)
        for y in range(459, 588, 14):
            rear.box([x + 11, y, -239], [x + 72, y + 2, -238], GRAY)
    rear.box([-183, 397, -228], [183, 407, -222], BLACK)
    rear.box([-117, 637, -226], [117, 649, -220], COMPUTER)
    parts.append(rear.finish())
    return parts


def build_screen(include_pupil=True):
    screen = Part('eye_display', '粉红杏眼与同心瞳环像素屏', group='screen')
    x, y = np.meshgrid(np.arange(-192, 193), np.arange(-103, 104))
    mask = rounded(x, y, 192, 103, 14)
    states = np.full(x.shape, BLACK, np.uint8)
    states[(x % 3 == 0) & ((y // 3 + x // 9) % 7 < 3)] = RED
    states[(x % 17 == 0) & ((y // 5 + x // 11) % 9 < 2)] = MAGENTA
    states[(y % 31 == 0) & (abs(y) < 92)] = IWV
    states[(abs(x) > 182) | (abs(y) > 96)] = BLACK
    def paint(selected, state):
        states[selected & mask] = state
    eye_height = 70 * np.maximum(0, 1 - (abs(x) / 117) ** 1.65) ** .6
    paint((abs(x) <= 125) & (abs(y) <= eye_height + 7), BLACK)
    paint((abs(x) <= 117) & (abs(y) <= eye_height), PINK_LIGHT)
    r = np.hypot(x, y)
    if include_pupil:
        paint(r <= 63, MAGENTA_LIGHT)
        paint(r <= 60, WHITE_LIGHT)
        paint(r <= 36, RED_LIGHT)
        paint(r <= 28, PINK_LIGHT)
        paint(r <= 23, RED)
        paint(r <= 20, YELLOW)
        paint(r <= 17, WHITE_LIGHT)
        paint(r <= 4, MAGENTA_LIGHT)
    for sign in [-1, 1]:
        paint((sign * y >= 59) & (sign * y <= 93) & (abs(x) <= (93 - sign * y) * .55), MAGENTA_LIGHT)
    for cx, cy, ax, ay in [(-82, 45, 10, 15), (82, 45, 10, 15), (-82, -45, 10, 15), (82, -45, 10, 15)]:
        paint(abs(x - cx) / ax + abs(y - cy) / ay <= 1, MAGENTA_LIGHT)
    for cx in [-154, 154]:
        distance = np.sqrt(abs(x - cx) / 25) + np.sqrt(abs(y) / 66)
        paint((distance <= 1.14) & (distance >= .82), MAGENTA_LIGHT)
        paint((abs(y) <= 2) & (abs(x - cx) <= 32), MAGENTA_LIGHT)
    paint((abs(y) < 2) & (abs(x) > 121), MAGENTA_LIGHT)
    z = 247 - np.floor(6 * (x / 193) ** 2 + 5 * (y / 104) ** 2).astype(int)
    for state in np.unique(states):
        selected = mask & (states == state)
        for offset in [0, -1, -2]:
            screen.points(np.c_[x[selected] * .75, y[selected] * .82 + 525, z[selected] + offset], int(state))
    return [screen.finish()]
