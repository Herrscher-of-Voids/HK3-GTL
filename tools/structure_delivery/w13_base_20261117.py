import numpy as np

from w13_common_20261117 import (
    Part, BLACK, STUDS, GRAY, SILVER, HK_BLACK, HK_GRAY, PURPLE, VOID,
    STONE, VENT, RED, MAGENTA, RED_GLASS, PINK_GLASS,
    PINK_LIGHT, RED_LIGHT, COMPUTER, ADVANCED, GOLD, CONTROL,
)


BOXES = [
    (-494, -295, -444, -245), (-494, -295, 244, 443),
    (295, 494, -444, -245), (295, 494, 244, 443),
]
LASER_SOURCES = [(-394, 79, -344), (-394, 79, 343),
                 (394, 79, -344), (394, 79, 343)]


def _metric(x, z):
    return np.maximum.reduce((abs(x) / 517, abs(z + .5) / 482.5,
                              (abs(x) + abs(z + .5)) / 939.5))


def _wells(x, z):
    selected = np.zeros(np.broadcast(x, z).shape, bool)
    for xa, xb, za, zb in BOXES:
        selected |= (x >= xa - 6) & (x <= xb + 6) & (z >= za - 6) & (z <= zb + 6)
    return selected


def _gate(x, z):
    return (x >= -68) & (x <= 67) & (z >= 451)


def _height(x, z):
    height = 15 + 5 * np.floor(np.clip((_metric(x, z) - .12) / .84, 0, 1) * 13)
    height = np.where(_wells(x, z), 19, height)
    return np.where(_gate(x, z), 7, height).astype(np.int32)


def _points(part, x, y, z, selected, state):
    part.points(np.c_[x[selected], np.broadcast_to(y, x.shape)[selected], z[selected]], state)


def _foundation():
    parts = []
    z, x = np.mgrid[-483:483, -517:518]
    metric, height = _metric(x, z), _height(x, z)
    inside = metric <= 1
    plate = Part('base_underplate', '黑盒矩阵三层底板', group='base', thickness=3)
    for y in range(3):
        _points(plate, x, y, z, inside, HK_BLACK if y == 2 else STONE)
    parts.append(plate.finish())
    for sector in range(4):
        quadrant = ((x >= 0) == bool(sector & 1)) & ((z >= 0) == bool(sector & 2))
        selected = inside & quadrant
        shell = Part(f'pit_lining_{sector}', f'第{sector + 1}象限阶梯侵蚀井衬层',
                     group='base', lining_thickness=4, bottom_surface_y=15,
                     installation_well_floor_y=19, stair_rise=5)
        for dy in range(4):
            _points(shell, x, height - dy, z, selected, HK_GRAY if dy else BLACK)
        seams = selected & (((x % 64 < 2) & (z % 64 < 51)) |
                            ((z % 64 < 2) & (x % 64 < 51)))
        _points(shell, x, height, z, seams, PURPLE)
        edge = selected & (metric > .97) & ~_gate(x, z) & ~_wells(x, z)
        _points(shell, x, height, z, edge, STUDS)
        parts.append(shell.finish())
        braces = Part(f'pit_understructure_{sector}', f'第{sector + 1}象限内部钢架', group='base',
                      beam_spacing=64, beam_width=3)
        lattice = selected & ((x % 64 < 3) | (z % 64 < 3))
        for y in range(3, 77):
            available = selected & (height >= y + 4)
            support = available & lattice
            if y in (12, 13, 32, 33, 52, 53):
                support |= available & ((x % 128 < 5) | (z % 128 < 5))
            _points(braces, x, y, z, support, STUDS)
        parts.append(braces.finish())
    for sector in range(4):
        quadrant = ((x >= 0) == bool(sector & 1)) & ((z >= 0) == bool(sector & 2))
        rim = inside & quadrant & (metric >= .97) & ~_gate(x, z) & ~_wells(x, z)
        sides = rim & ((metric >= .99) | (metric <= .976))
        wall = Part(f'pit_armored_rim_{sector}', f'第{sector + 1}象限八角装甲城墙',
                    group='base', nominal_y=[0, 80], corner_cut=60, hollow_wall=True)
        for y in range(3, 81):
            selected = rim if y >= 76 or y <= 7 else sides
            _points(wall, x, y, z, selected, BLACK if y % 16 < 12 else PURPLE)
            if y in (15, 31, 47, 63, 79):
                _points(wall, x, y, z, selected & ((x % 64 < 3) | (z % 64 < 3)), RED_LIGHT)
        parts.append(wall.finish())
    return parts


def _hydraulics():
    parts = []
    vertices = np.array([[-457, -483], [457, -483], [517, -423], [517, 422],
                         [457, 482], [-457, 482], [-517, 422], [-517, -423]], float)
    for index, (a, b) in enumerate(zip(vertices, np.roll(vertices, -1, axis=0))):
        tangent = (b - a) / np.linalg.norm(b - a)
        inward = np.array([-tangent[1], tangent[0]])
        centers = a + np.arange(16, np.linalg.norm(b - a) - 8, 32)[:, None] * tangent
        p = Part(f'rim_hydraulics_{index}', f'八角边界第{index + 1}段斜液压肋', group='base',
                 spacing=32, nominal_width=24, nominal_height=80,
                 inward_axis_offset=10, pillar_count=len(centers))
        u, v = np.meshgrid(np.arange(-11.5, 12, 1), np.arange(-5, 6), indexing='ij')
        offsets = u.ravel()[:, None] * tangent + v.ravel()[:, None] * inward
        for center in centers:
            for y in range(81):
                q = np.rint(center + inward * (6 + y / 8) + offsets).astype(np.int32)
                selected = ~_gate(q[:, 0], q[:, 1])
                if 44 <= y <= 70:
                    selected &= (abs(u.ravel()) < 5) & (abs(v.ravel()) < 4)
                p.points(np.c_[q[selected, 0], np.full(np.count_nonzero(selected), y), q[selected, 1]],
                         SILVER if 44 <= y <= 70 else STUDS if y < 10 or y > 70 else HK_GRAY)
                rails = selected & (abs(u.ravel()) > 9) & (abs(v.ravel()) < 2)
                p.points(np.c_[q[rails, 0], np.full(np.count_nonzero(rails), y), q[rails, 1]], PURPLE)
        parts.append(p.finish())
    return parts


def _black_box(index, bounds):
    xa, xb, za, zb = bounds
    cx, cz = (xa + xb) / 2, (za + zb) / 2
    z, x = np.mgrid[za:zb + 1, xa:xb + 1]
    lx, lz = x - cx, z - cz
    p = Part(f'black_box_{index}', f'第{index + 1}座破裂黑盒副算力塔', group='base',
             source_bounds=[[xa, 20, za], [xb, 79, zb]], size_xyz=[200, 60, 200],
             laser_source=list(LASER_SOURCES[index]), diagonal_cracks='外壳实际留空，红色算力列位于内部')
    skin = (abs(lx) >= 95.5) | (abs(lz) >= 95.5)
    front_y = 49 + .30 * lx + 3 * np.sin(lx / 11)
    side_y = 49 + .30 * lz - 3 * np.sin(lz / 13)
    for y in range(20, 80):
        face = np.ones(x.shape, bool) if y < 24 or y >= 76 else skin
        crack = ((abs(lz) >= 95.5) & (abs(y - front_y) <= 4)) | \
                ((abs(lx) >= 95.5) & (abs(y - side_y) <= 4))
        if y >= 76:
            crack |= abs(lx - lz) <= 6
        _points(p, x, y, z, face & ~crack, VOID)
        edge = face & ~crack & ((abs(lx) >= 98.5) | (abs(lz) >= 98.5))
        _points(p, x, y, z, edge, BLACK)
        if y in (24, 25, 74, 75):
            _points(p, x, y, z, edge & ((x % 32 < 2) | (z % 32 < 2)), SILVER)
        inner = ((abs(lx) == 91.5) & (abs(lz) < 92)) | ((abs(lz) == 91.5) & (abs(lx) < 92))
        if 24 <= y <= 74:
            _points(p, x, y, z, inner, RED)
            circuit = inner & ((x % 24 < 2) | (z % 24 < 2) | (y % 12 < 2))
            _points(p, x, y, z, circuit, MAGENTA if y % 24 < 12 else RED_LIGHT)
    for dx in (-66, -22, 22, 66):
        for dz in (-66, -22, 22, 66):
            px, pz = int(cx + dx), int(cz + dz)
            p.box((px - 6, 24, pz - 6), (px + 6, 70, pz + 6), COMPUTER)
            for y in (25, 37, 49, 61, 71):
                p.box((px - 7, y, pz - 7), (px + 7, y + 1, pz + 7), ADVANCED)
                p.box((px - 7, y + 1, pz - 7), (px + 7, y + 1, pz - 7), RED_LIGHT)
    px, py, pz = LASER_SOURCES[index]
    p.box((px - 8, 75, pz - 8), (px + 8, 77, pz + 8), STUDS)
    p.box((px - 6, 78, pz - 6), (px + 6, 78, pz + 6), RED)
    p.box((px - 3, 79, pz - 3), (px + 3, 79, pz + 3), RED_LIGHT)
    return p.finish()


def _coolant():
    p = Part('coolant_pipe_grid', '八格粉红主管与阶梯工业格栅', group='base', trunk_width=8,
             route='沿各格阶梯顶面铺设，管壳高六格，上覆留孔金属格栅，避开黑盒安装井')
    z, x = np.mgrid[-440:440, -470:471]
    dx = np.minimum.reduce([abs(x - at) for at in (-192, 0, 192)])
    dz = np.minimum.reduce([abs(z - at) for at in (-160, 0, 160)])
    path = ((dx < 4) | (dz < 4)) & (_metric(x, z) < .89) & ~_wells(x, z) & ~_gate(x, z)
    top = _height(x, z)
    for dy in range(1, 7):
        _points(p, x, top + dy, z, path, PINK_GLASS if dy % 3 else RED_GLASS)
    _points(p, x, top + 3, z, path & ((dx < 1) | (dz < 1)), PINK_LIGHT)
    _points(p, x, top + 1, z, path & ((x % 24 < 2) | (z % 24 < 2)), GRAY)
    grate = path & ((x % 3 == 0) | (z % 3 == 0))
    _points(p, x, top + 7, z, grate, VENT)
    return p.finish()


def _terminal():
    p = Part('south_control_terminal', '南侧敞口舰桥控制终端', group='base',
             source_bounds=[[-60, 8, 459], [59, 47, 482]], nominal_size_xyz=[120, 40, 24],
             controller=[0, 47, 470], facing='south', fixed_interface_positions=[],
             recess='基座南沿局部降至Y7；两侧横向一格一级阶梯登上中央主控台')
    p.box((-60, 8, 459), (59, 11, 482), STUDS)
    p.box((-60, 12, 459), (59, 47, 462), BLACK)
    for x in (-58, -32, 31, 57):
        p.box((x - 2, 12, 463), (x + 2, 46, 464), HK_BLACK)
        p.box((x, 15, 465), (x, 42, 465), RED_LIGHT)
    p.box((-28, 18, 463), (27, 38, 464), ADVANCED)
    for x in range(-24, 25, 8):
        p.box((x, 23, 465), (x + 2, 34, 465), COMPUTER)
        p.box((x, 25, 466), (x + 2, 25, 466), PINK_LIGHT)
    for side in (-1, 1):
        for step in range(37):
            x = -59 + step if side < 0 else 58 - step
            p.box((x, 11, 469), (x, 11 + step, 480), BLACK)
            p.box((x, 11 + step, 469), (x, 11 + step, 480), HK_GRAY)
        p.box((side * 18 - 3, 12, 467), (side * 18 + 3, 44, 481), BLACK)
    p.box((-22, 42, 466), (21, 46, 481), HK_BLACK)
    p.box((-21, 46, 467), (20, 46, 480), ADVANCED)
    p.box((-12, 47, 467), (11, 47, 468), RED)
    p.box((-11, 47, 469), (10, 47, 469), GOLD)
    p.box((-4, 47, 470), (3, 47, 470), HK_GRAY)
    p.points([[0, 47, 470]], CONTROL)
    return p.finish()


def build_base():
    return [*_foundation(), *_hydraulics(),
            *[_black_box(i, bounds) for i, bounds in enumerate(BOXES)],
            _coolant(), _terminal()]
