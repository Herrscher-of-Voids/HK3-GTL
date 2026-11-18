import numpy as np

from w13_tv_common_20261117 import Part, rounded, BLACK, STUDS, GRAY, SILVER, VENT, YELLOW, PINK, RED, WHITE_LIGHT


CYAN_LIGHT, GREEN_LIGHT, BLUE_LIGHT = 26, 27, 28


def build_crt(name, label, size, center, orientation='front', lean=0, screen='off', seed=0):
    w, h, d = map(int, size)
    part = Part(name, label, group='mountain', size=list(size), center=list(center), orientation=orientation, lean=lean, screen=screen)
    rng = np.random.default_rng(seed)
    x, y = np.meshgrid(np.arange(w), np.arange(h), indexing='ij')
    xx, yy = x - (w - 1) / 2, y - (h - 1) / 2
    bevel = max(2, round(min(w, h) * .075))
    for z in range(d - 5):
        taper = (d - 6 - z) / (d - 6)
        hx, hy = (w - 1) / 2 - round(w * .10 * taper), (h - 1) / 2 - round(h * .06 * taper)
        outer = rounded(xx, yy, hx, hy, bevel)
        shell = outer if z < 2 else outer & ~rounded(xx, yy, hx - 2, hy - 2, bevel)
        part.points(np.c_[x[shell], y[shell], np.full(shell.sum(), z)], BLACK)
    front = rounded(xx, yy, (w - 1) / 2, (h - 1) / 2, bevel)
    for z in range(d - 5, d - 2):
        part.points(np.c_[x[front], y[front], np.full(front.sum(), z)], STUDS if z == d - 3 else BLACK)

    sx0, sx1 = 3, w - max(8, round(w * .20)) - 3
    sy0, sy1 = 3, h - 4
    cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    hx, hy = (sx1 - sx0) / 2, (sy1 - sy0) / 2
    sx, sy = x - cx, y - cy
    frame = rounded(sx, sy, hx, hy, bevel)
    part.points(np.c_[x[frame], y[frame], np.full(frame.sum(), d - 2)], BLACK)
    display = rounded(sx, sy, hx - 2, hy - 2, bevel)
    tx, ty = x[display], y[display]
    u, v = (tx - cx) / (hx - 2), (ty - cy) / (hy - 2)
    z = d - 3 + np.floor(2.5 * (1 - .5 * u * u - .5 * v * v)).astype(int)
    pixels = np.full(len(tx), BLACK, np.uint8)
    noise = rng.random(len(tx))
    if screen == 'static':
        pixels[noise > .82] = VENT
        pixels[noise > .94] = GRAY
        pixels[(noise > .995) & (ty % 3 == 0)] = WHITE_LIGHT
    elif screen == 'white':
        band = (abs(v) < .57) & (ty % 4 != 0)
        pixels[band] = GRAY
        pixels[band & (noise > .32)] = WHITE_LIGHT
    elif screen == 'cyan':
        pixels[(abs(v) < .78) & (ty % 3 != 0)] = CYAN_LIGHT
        pixels[(abs(v) < .15) & (abs(u) < .14)] = WHITE_LIGHT
    elif screen == 'bars':
        colors = np.array([YELLOW, CYAN_LIGHT, GREEN_LIGHT, PINK, RED, BLUE_LIGHT, WHITE_LIGHT], np.uint8)
        band = (v > -.35) & (v < .72) & (ty % 4 != 0)
        pixels[band] = colors[np.clip(((u[band] + 1) * 3.5).astype(int), 0, 6)]
        pixels[(v < -.65) & (v > -.77) & (u < -.25)] = WHITE_LIGHT
    elif screen == 'code':
        text = (ty % 6 < 2) & (tx % 4 < 3) & (abs(v) < .8) & (noise > .25)
        pixels[text] = GREEN_LIGHT
        pixels[text & (tx % 11 < 3)] = CYAN_LIGHT
    for state in np.unique(pixels):
        mask = pixels == state
        part.points(np.c_[tx[mask], ty[mask], z[mask]], state)

    px0, px1 = sx1 + 3, w - 4
    pc = (px0 + px1) / 2
    for py in [round(h * .76), round(h * .56)]:
        radius = min((px1 - px0) / 2, h * .075)
        rr = (x - pc) ** 2 + (y - py) ** 2
        knob = rr <= radius * radius
        part.points(np.c_[x[knob], y[knob], np.full(knob.sum(), d - 1)], SILVER)
        knob &= rr <= (radius - 1) ** 2
        part.points(np.c_[x[knob], y[knob], np.full(knob.sum(), d - 1)], GRAY)
        part.box([round(pc), py, d - 1], [round(pc), py + round(radius - 1), d - 1], BLACK)
    for py in range(4, round(h * .40), 3):
        part.box([px0, py, d - 2], [px1, py, d - 2], VENT)
    part.box([px0, round(h * .45), d - 1], [px0 + 1, round(h * .45) + 1, d - 1], CYAN_LIGHT if screen != 'off' else GRAY)

    for z in range(round(d * .17), round(d * .65)):
        taper = (d - 6 - z) / (d - 6)
        left = round(w * .10 * taper)
        for py in range(round(h * .24), round(h * .73), 4):
            part.points([[left, py, z], [w - 1 - left, py, z]], VENT)
    for py in range(round(h * .28), round(h * .75), 4):
        part.box([round(w * .24), py, 0], [round(w * .76), py, 0], VENT)
    part.box([round(w * .42), round(h * .11), 0], [round(w * .58), round(h * .17), 0], GRAY)

    angle = np.radians(lean)
    rotation = np.array([[np.cos(angle), -np.sin(angle), 0], [np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
    axes = {
        'front': np.eye(3),
        'back': np.diag([-1, 1, -1]),
        'left': np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]),
        'right': np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]),
        'up': np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]]),
    }
    origin = (np.array(size) - 1) / 2
    matrix = axes[orientation] @ rotation
    part.chunks = [np.floor((p - origin) @ matrix.T + center + .5).astype(np.int32) for p in part.chunks]
    return part.finish()
