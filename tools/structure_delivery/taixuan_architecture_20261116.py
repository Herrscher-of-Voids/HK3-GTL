import numpy as np

from taixuan_common_20261116 import (
    Part, model, WOOD, FRAME, ROOF, TILE, WHITE, PAVING, GOLD, BRONZE, BROWN, PATINA,
)


def _roof(p, center, half, base, rise, state=ROOF, edge=TILE, axis=0, opening=None):
    hx, hz = half
    z, x = np.mgrid[-hz:hz + 1, -hx:hx + 1]
    if axis == 0:
        d = np.maximum(abs(z) / hz, np.maximum(0, abs(x) - (hx - hz)) / hz)
    else:
        d = np.maximum(abs(x) / hx, np.maximum(0, abs(z) - (hz - hx)) / hx)
    corners = (abs(x) / hx) ** 10 * (abs(z) / hz) ** 10
    y = np.rint(base + rise * (1 - d) ** 1.5 + min(7, rise / 2) * corners).astype(int)
    keep = np.ones(x.shape, dtype=bool)
    if opening:
        keep &= (abs(x) > opening[0]) | (abs(z) > opening[1])
    rim = ((abs(x) >= hx - 1) | (abs(z) >= hz - 1)) & keep
    ribs = ((x % 10 == 0) if axis == 0 else (z % 10 == 0)) & keep
    for depth in (0, -1):
        p.points(np.c_[x[keep] + center[0], y[keep] + depth, z[keep] + center[1]], state)
    p.points(np.c_[x[ribs] + center[0], y[ribs] + 1, z[ribs] + center[1]], TILE)
    p.points(np.c_[x[rim] + center[0], y[rim], z[rim] + center[1]], edge)
    p.points(np.c_[x[rim] + center[0], y[rim] - 2, z[rim] + center[1]], FRAME)


def _pagoda_roof(p, center, radius, base, rise, edge=GOLD):
    z, x = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    d = np.maximum(np.maximum(abs(x), abs(z)) / radius, (abs(x) + abs(z)) / (radius * 1.4))
    vertices = np.array([(sx * radius, sz * radius * .4) for sx in (-1, 1) for sz in (-1, 1)]
                        + [(sx * radius * .4, sz * radius) for sx in (-1, 1) for sz in (-1, 1)])
    distance = np.sqrt(((np.stack((x, z), -1)[..., None, :] - vertices) ** 2).sum(-1)).min(-1)
    tips = np.maximum(0, 1 - distance / (radius * .35)) ** 2 * min(4, rise)
    keep = d <= 1
    rim = (d > 1 - 1.4 / radius) & keep
    y = np.rint(base + rise * np.maximum(0, 1 - d) ** 1.6 + tips).astype(int)
    for depth in (0, -1):
        p.points(np.c_[x[keep] + center[0], y[keep] + depth, z[keep] + center[1]], PATINA)
    p.points(np.c_[x[rim] + center[0], y[rim], z[rim] + center[1]], edge)
    p.points(np.c_[x[rim] + center[0], y[rim] - 2, z[rim] + center[1]], FRAME)


def _window(p, center, axis, bottom=169, width=15, height=30, door=False):
    half = width // 2

    def put(coords, state):
        p.points([(center[0] + u * axis[0], bottom + round(y * (height - 1) / 29), center[1] + u * axis[1]) for u, y in coords], state)

    put([(u, y) for u in range(-half, half + 1) for y in range(30)], PAVING)
    if door:
        put([(u, y) for u in range(-half, half + 1) for y in range(10)], WOOD)
    put([(u, y) for u in (-half, half) for y in range(30)], WOOD)
    put([(u, y) for u in range(-half, half + 1) for y in (0, 10, 29)], WOOD)
    put([(u, y) for u in range(-half + 1, half) if u % 3 == 0 for y in range(11, 29)], WOOD)
    put([(u, y) for u in range(-half + 1, half) for y in (14, 18, 22, 26)], WOOD)
    if door:
        ornament = min(2, half - 1)
        put([(u, y) for u in range(-ornament, ornament + 1) for y in (3, 7)], GOLD)
        put([(u, y) for u in (-ornament, ornament) for y in range(3, 8)], GOLD)


def _temple():
    p = Part('temple', '拂云观重檐主殿', inference='殿宇比例、背面、内堂及后窗依据可见正侧立面作复刻推断；官方未提供完整总图。')
    p.box((-70, 160, -126), (71, 163, -51), TILE)
    p.box((-68, 164, -124), (69, 166, -53), PAVING)
    p.box((-65, 167, -120), (65, 168, -56), WOOD)
    for step in range(8):
        p.box((-22, 160, -35 - step * 2), (22, 160 + step, -36 - step * 2), PAVING)
    for x in (-63, -45, -27, -9, 9, 27, 45, 63):
        for z in (-119, -57):
            if z == -119 or abs(x) != 9:
                p.box((x - 2, 167, z - 2), (x + 2, 170, z + 2), TILE)
                p.box((x - 1, 171, z - 1), (x + 1, 202, z + 1), FRAME)
                p.box((x - 5, 198, z - 2), (x + 5, 200, z + 2), WOOD)
                p.box((x - 7, 201, z - 3), (x + 7, 202, z + 3), FRAME)
                p.beam((x, 198, z), (x, 204, z + (12 if z == -57 else -12)), 1.4, WOOD)
    for x in (-54, -36, 36, 54):
        _window(p, (x, -57), (1, 0))
    for x in (-18, -6, 18):
        _window(p, (x, -57), (1, 0), width=11, height=26, door=True)
    _window(p, (12, -62), (0, 1), width=11, height=26, door=True)
    for x in (-25, -12, 0, 12, 25):
        p.box((x, 169, -57), (x, 198, -57), WOOD)
    for x in (-54, -36, -18, 0, 18, 36, 54):
        _window(p, (x, -119), (1, 0))
    for x in (-65, 65):
        for z in (-107, -89, -71):
            if (x, z) != (-65, -107):
                _window(p, (x, z), (0, 1))
        p.box((x - 1, 199, -120), (x + 1, 202, -56), WOOD)
    p.box((-66, 194, -116), (-64, 198, -98), FRAME)
    p.box((-63, 199, -59), (63, 202, -55), WOOD)
    p.box((-63, 199, -121), (63, 202, -117), WOOD)
    p.box((-26, 195, -58), (26, 198, -56), WOOD)
    for x in (-18, -6, 6, 18):
        p.box((x - 3, 197, -55), (x + 3, 197, -55), GOLD)
    for x in (-36, 36):
        for z in (-105, -71):
            p.box((x - 1, 169, z - 1), (x + 1, 203, z + 1), WOOD)
    for x in range(-60, 61, 10):
        p.box((x, 201, -119), (x + 1, 203, -57), WOOD)
    for z in (-108, -88, -68):
        p.box((-63, 202, z), (63, 204, z + 1), FRAME)
    _roof(p, (0, -88), (83, 48), 201, 18, opening=(54, 20))
    for x in (-48, -24, 0, 24, 48):
        for z in (-104, -72):
            p.box((x - 1, 202, z - 1), (x + 1, 225, z + 1), WOOD)
    for z in (-108, -68):
        p.box((-54, 213, z), (54, 224, z), FRAME)
        for x in range(-48, 49, 12):
            p.box((x - 3, 217, z), (x + 3, 221, z), WHITE)
            p.box((x, 217, z), (x, 221, z), WOOD)
    for x in (-54, 54):
        p.box((x, 213, -108), (x, 224, -68), FRAME)
    _roof(p, (0, -88), (65, 33), 223, 17)
    p.box((-32, 240, -89), (32, 242, -87), TILE)
    for sign in (-1, 1):
        p.beam((sign * 30, 242, -88), (sign * 38, 244, -88), 1, TILE)
    return model(p, ['四扇窄格门，一扇向内打开', '双层青灰瓦檐、曲脊与四角翘起', '木构柱梁斗拱', '暖米白细木窗棂与缩小铜金门饰'],
                 ['G10', 'G14', 'G15', 'O02', 'O05', 'O06', 'O08', 'O10'],
                 {'roof': {'label': '重檐曲脊', 'center': [0, 215, -88], 'half': [85, 38, 58], 'direction': [-.8, .4, 1]},
                  'doors': {'label': '格扇与内堂门洞', 'center': [0, 185, -57], 'half': [68, 24, 12], 'direction': [-.3, .15, 1]},
                  'interior': {'label': '内堂柱梁', 'center': [0, 185, -87], 'half': [62, 22, 30], 'direction': [0, .05, 1]}})


def _gallery_span(p, center, length, axis):
    hx, hz = (length // 2, 14) if axis == 0 else (14, length // 2)
    cx, cz = center
    p.box((cx - hx, 160, cz - hz), (cx + hx, 165, cz + hz), TILE)
    p.box((cx - hx, 166, cz - hz), (cx + hx, 167, cz + hz), PAVING)
    for u in range(-length // 2 + 4, length // 2, 12):
        for side in (-11, 11):
            x, z = (cx + u, cz + side) if axis == 0 else (cx + side, cz + u)
            p.box((x - 1, 168, z - 1), (x + 1, 184, z + 1), BROWN)
            p.box((x - 3, 181, z - 3), (x + 3, 183, z + 3), WOOD)
    if axis == 2:
        p.box((cx - 12, 168, cz - hz), (cx - 12, 174, cz + hz), WHITE)
        p.box((cx - 13, 175, cz - hz), (cx - 11, 176, cz + hz), FRAME)
        for u in range(-length // 2 + 10, length // 2, 12):
            _window(p, (cx - 12, cz + u), (0, 1), bottom=168, width=9, height=15)
    _roof(p, center, (hx + 3, hz + 3), 184, 11, axis=axis)


def _gallery():
    p = Part('gallery', '西侧木构长廊', inference='O08/O10长条窗格与O05殿宇的同一性未核实，按殿与廊分置；主廊尺寸、折廊连接及背面均为复刻推断。')
    _gallery_span(p, (-108, -16), 100, 2)
    _gallery_span(p, (-108, -87), 44, 2)
    _gallery_span(p, (-86, -108), 44, 0)
    return model(p, ['单侧红褐细柱长廊', '墙下浅白条与连续格扇', '折廊连接主殿西后侧'], ['G14', 'O08', 'O10'],
                 {'gallery': {'label': '西侧格扇长廊', 'center': [-108, 177, -20], 'half': [22, 25, 60], 'direction': [1, .3, .8]},
                  'connection': {'label': '西后折廊', 'center': [-95, 177, -97], 'half': [35, 25, 30], 'direction': [-1, .5, .8]}})


def _censer():
    p = Part('censer', '古铜双重塔檐香炉', inference='依据O02、O07与G11建立圆腹、卷耳、圆章与前一后两的三足造型；背面花纹与48格高度为复刻推断。')
    for x, z in ((0, 31), (-9, 14), (9, 14)):
        p.beam((x * 1.25, 162, 20 + (z - 20) * 1.25), (x, 170, z), 1.6, BRONZE)
        p.box((round(x * 1.25) - 1, 161, round(20 + (z - 20) * 1.25) - 1),
              (round(x * 1.25) + 1, 162, round(20 + (z - 20) * 1.25) + 1), FRAME)
    z, x = np.mgrid[6:35, -14:15]
    for y in range(167, 186):
        r = (x / 14) ** 2 + ((y - 176) / 9) ** 2 + ((z - 20) / 14) ** 2
        shell = (r <= 1) & (r >= .75)
        p.points(np.c_[x[shell], np.full(shell.sum(), y), z[shell]], BROWN)
    for y, radius in ((168, 10), (183, 11), (185, 9)):
        p.ring((0, y, 20), radius, 2, BRONZE, depth=2)
    p.ring((0, 177, 20), 14, 1, GOLD, depth=1)
    for center, normal in (((0, 177, 34), (0, 0, 1)), ((-14, 177, 20), (1, 0, 0)), ((14, 177, 20), (1, 0, 0))):
        p.ring(center, 4, 4, GOLD, normal=normal, depth=1)
        p.ring(center, 3, 1, BRONZE, normal=normal, depth=2)
    for sign in (-1, 1):
        path = [(sign * 12, 174, 20), (sign * 17, 177, 20), (sign * 20, 183, 20),
                (sign * 19, 187, 20), (sign * 16, 188, 20), (sign * 15, 185, 20)]
        for a, b in zip(path, path[1:]):
            p.beam(a, b, 1.3, BRONZE)
    for y0, y1, radius in ((184, 189, 9), (193, 198, 6)):
        for side in (-1, 1):
            p.box((-radius, y0, 20 + side * radius), (radius, y0, 20 + side * radius), BRONZE)
            p.box((side * radius, y0, 20 - radius), (side * radius, y0, 20 + radius), BRONZE)
            p.box((-radius, y1, 20 + side * radius), (radius, y1, 20 + side * radius), BRONZE)
            p.box((side * radius, y1, 20 - radius), (side * radius, y1, 20 + radius), BRONZE)
            for u in range(-radius, radius + 1, 3):
                p.box((u, y0, 20 + side * radius), (u, y1, 20 + side * radius), FRAME)
                p.box((side * radius, y0, 20 + u), (side * radius, y1, 20 + u), FRAME)
    _pagoda_roof(p, (0, 20), 18, 188, 5)
    _pagoda_roof(p, (0, 20), 12, 198, 5)
    p.ring((0, 204, 20), 2, 2, BRONZE, depth=2)
    p.box((0, 205, 20), (0, 208, 20), GOLD)
    return model(p, ['椭圆炉腹与三足', '双侧卷耳、环腰金线及三面圆章', '双层八角绿铜翘檐与镂空格窗'], ['G11', 'O02', 'O07'],
                 {'censer': {'label': '古铜圆腹与绿铜重檐', 'center': [0, 184, 20], 'half': [23, 28, 22], 'direction': [-.8, .25, 1]}})


def _lanterns():
    p = Part('lanterns', '殿前四座石灯', inference='石灯塔檐形制来自官方庭院远景；四盏数量、间距与内部灯芯为复刻推断。')
    for x, z in ((-55, -32), (55, -32), (-37, -20), (37, -20)):
        p.box((x - 3, 160, z - 3), (x + 3, 162, z + 3), PAVING)
        p.box((x - 1, 163, z - 1), (x + 1, 167, z + 1), TILE)
        p.box((x - 3, 167, z - 3), (x + 3, 168, z + 3), FRAME)
        p.box((x - 2, 169, z - 2), (x + 2, 172, z + 2), WHITE)
        for sx in (-2, 2):
            for sz in (-2, 2):
                p.box((x + sx, 169, z + sz), (x + sx, 173, z + sz), BRONZE)
        _pagoda_roof(p, (x, z), 5, 173, 2, TILE)
        p.box((x, 176, z), (x, 177, z), GOLD)
    return model(p, ['浅色石座与细柱灯室', '四座小型翘檐石灯'], ['O02', 'O07'],
                 {'lanterns': {'label': '殿前四座石灯', 'center': [0, 168, -26], 'half': [64, 14, 18], 'direction': [-.4, .4, 1]}})


def build():
    return [_temple(), _gallery(), _censer(), _lanterns()]
