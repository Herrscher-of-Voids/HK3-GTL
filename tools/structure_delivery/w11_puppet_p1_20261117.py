import math

import numpy as np
from PIL import Image, ImageDraw

from w11_common_20261117 import Part, BLACK, STUDS, WHITE, GOLD, RED, LIGHT, GRAY


VIEWS = dict(
    head=dict(label='头盔与红眼', center=[-.5, 224, 10], half=[24, 24, 23], direction=[-.45, .2, 1]),
    chest=dict(label='胸甲金纹', center=[-.5, 169, 14], half=[58, 47, 38], direction=[-.3, .15, 1]),
    hands=dict(label='悬浮手掌', center=[-142, 182, 17], half=[38, 48, 28], direction=[-.35, .2, 1]),
    elbow=dict(label='主臂球关节', center=[86, 143, 7], half=[29, 43, 35], direction=[.8, .2, 1]),
    legs=dict(label='盾状腿甲', center=[-.5, 65, 6], half=[65, 62, 39], direction=[-.6, .15, 1]),
    pixels=dict(label='原生像素近景', center=[26, 96, 30], half=[7, 7, 7], direction=[-.7, .4, 1]),
)
NOTES = [
    '形制以官方《薪炎永燃》巨型乌合之众为主：小型尖盔、宽肩收腰胸甲、一对粗主臂和巨大盾状腿甲。',
    '九只外圈悬浮手掌分别成件；位置、比例与展开姿态取自多个动画镜头的方块转译。',
    '胸甲保留上扬眼形金纹与下方成对叶形纹；头部采用尖额盔、红眼和W形下颌。',
    '肩甲分层上翘，肘部为镂空孔纹金球关节，手指分三节，腿甲保留三点孔与锯齿切面。',
    '原作蓝灰甲映射为W11黑白甲，金关节、金纹与红眼保留；使用已有GT方块与原生像素贴图。',
    '背部轮廓有迎光镜头，内部连接与遮挡区域按现有分片甲的工程延续处理。',
    '本稿为独立人偶形制小样，后续按确认后的比例安置到W11剧场。',
]


def part(name, label, section):
    return Part('w11_p1_' + name, label, section=section)


def mirror(points, side):
    points = np.asarray(points, float).copy()
    points[..., 0] = side * points[..., 0] - .5
    return points


def loft(p, levels, state, shell=0):
    for a, b in zip(levels[:-1], levels[1:]):
        for y in range(math.ceil(a[0]), math.ceil(b[0])):
            t = (y - a[0]) / (b[0] - a[0])
            cx, cz, rx, rz = np.array(a[1:]) * (1 - t) + np.array(b[1:]) * t
            x, z = np.meshgrid(np.arange(math.floor(cx-rx), math.ceil(cx+rx)+1), np.arange(math.floor(cz-rz), math.ceil(cz+rz)+1), indexing='ij')
            outer = ((x-cx)/rx)**2 + ((z-cz)/rz)**2 <= 1
            if shell and rx > shell and rz > shell:
                outer &= ((x-cx)/(rx-shell))**2 + ((z-cz)/(rz-shell))**2 >= 1
            p.points(np.c_[x[outer], np.full(int(outer.sum()), y), z[outer]], state)


def polygon(p, outline, front, back, state, side=1):
    points = np.asarray(outline, float)
    lo, hi = np.floor(points.min(0)).astype(int), np.ceil(points.max(0)).astype(int)
    mask = Image.new('L', tuple(hi-lo+1))
    ImageDraw.Draw(mask).polygon([tuple(point-lo) for point in points], fill=1)
    y, x = np.nonzero(np.asarray(mask))
    x, y = x+lo[0], y+lo[1]
    x = x if side>0 else -1-x
    for z in range(round(back), round(front)+1):
        p.points(np.c_[x, y, np.full(len(x), z)], state)


def stroke(p, points, radius, state, side=1):
    points = mirror(points, side)
    for a, b in zip(points[:-1], points[1:]):
        p.beam(a, b, radius, state)


def panel(p, outline, front, back, state, side=1, inset=True):
    polygon(p, outline, front, back, BLACK, side)
    points = np.asarray(outline, float)
    center = points.mean(0)
    inner = center + (points-center) * .92
    polygon(p, inner, front+.6, back+.6, state, side)


def chest_surface(x, y):
    rx = np.interp(y, [116, 135, 162, 191, 209], [23, 32, 43, 47, 35])
    rz = np.interp(y, [116, 135, 162, 191, 209], [15, 21, 27, 24, 18])
    return -3 + rz * math.sqrt(max(0, 1-(x/rx)**2))


def motif(p, xy, side, radius=1.4, state=GOLD):
    for a, b in zip(xy[:-1], xy[1:]):
        for t in np.linspace(0, 1, max(2, int(np.linalg.norm(np.array(b)-a))*2)):
            x, y = np.array(a)*(1-t) + np.array(b)*t
            p.sphere((side*x-.5, y, chest_surface(x, y)+.9), radius, state)


def curve(p, points, side, radius=1.5):
    a, b, c, d = np.asarray(points, float)
    t = np.linspace(0, 1, 65)[:, None]
    q = (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
    motif(p, q, side, radius)


def joint(p, center, radius, normal=(0, 0, 1)):
    c = np.asarray(center, float)
    p.sphere(c, radius, GOLD, inner=radius-3)
    p.ring(c, radius+.4, 1.6, BLACK, normal=normal, depth=2)
    p.ring(c, radius+.6, .8, GOLD, normal=normal, depth=2)
    for dx, dy in ((-radius*.42, radius*.3), (radius*.42, radius*.3), (0, -radius*.4)):
        z = math.sqrt(radius*radius-dx*dx-dy*dy)
        q = c + (dx, dy, z)
        p.sphere(q, radius*.21, BLACK)
        p.ring(q+(0, 0, .6), radius*.24, .7, GRAY, normal=(0, 0, 1), depth=1)


def hand(center, scale, roll, pitch, name, main=False, curl=.3):
    p = part(name, ('主手' if main else '悬浮手掌')+' · 三节长指与莲瓣袖口', 'arms' if main else 'crown')
    a, b = math.radians(roll), math.radians(pitch)
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    matrix = rz @ rx
    temp = Part('local', '局部手掌')
    loft(temp, [(-24, 0, 0, 11, 8), (-20, 0, 0, 14, 10), (-8, 0, 0, 11, 8), (-4, 0, 0, 8, 6)], WHITE, 2)
    for y in (-22, -8):
        temp.ring((0, y, 0), 13 if y == -22 else 11, 1.3, GOLD, depth=2)
    for angle in np.arange(5)*math.tau/5:
        u = np.array([math.cos(angle), 0, math.sin(angle)])
        v = np.array([-math.sin(angle), 0, math.cos(angle)])
        base = u*8+(0, -7, 0)
        tip = u*19+(0, -14, 0)
        temp.hull([base-v*3, base+v*3, u*16+v*4+(0, -20, 0), u*16-v*4+(0, -20, 0), tip, tip+(0, 2, 0)], GOLD)
        temp.sphere(u*16+(0, -17, 0), 1.5, BLACK)
    temp.beam((0, -6, 0), (0, 1, 0), 4, BLACK)
    temp.hull([(-11, -3, -4), (11, -3, -4), (-12, 10, -3), (12, 10, -3), (-8, -4, 5), (8, -4, 5), (-9, 10, 6), (9, 10, 6)], GOLD)
    temp.hull([(-7, -2, 6), (7, -2, 6), (-8, 8, 6), (8, 8, 6), (-6, -1, 8), (6, -1, 8), (-6, 7, 8), (6, 7, 8)], BLACK)
    for x, length in zip((-9, -3, 3, 9), (19, 27, 25, 19)):
        spread = x*.2
        pts = np.array([(x, 9, 1), (x+spread, 10+length*.43, 1.8), (x+spread*1.2, 10+length*.76, 1.8+curl*8), (x+spread*.9, 10+length*.9-curl*3, 3+curl*15)])
        for j, (u, v) in enumerate(zip(pts[:-1], pts[1:])):
            delta = v-u
            temp.beam(u+delta*.09, v-delta*.07, 2.1-j*.3, GOLD)
            temp.sphere(u, 2.2-j*.25, BLACK)
            temp.beam(u+(-.6, 0, 1.4), v+(-.6, 0, 1.4), .55, WHITE)
        temp.sphere(pts[-1], 1.4, GOLD)
    thumb = np.array([(10, -1, 0), (18, 1, 1), (23, 9, 4), (21, 15, 7+curl*6)])
    for u, v in zip(thumb[:-1], thumb[1:]):
        temp.beam(u, v, 2.2, GOLD)
        temp.sphere(u, 2.5, BLACK)
    finished = temp.finish()
    lo, hi = finished.p.min(0), finished.p.max(0)
    size = hi-lo+3
    volume = np.zeros(size, np.uint8)
    local = finished.p-lo+1
    volume[tuple(local.T)] = finished.states
    transformed = finished.p @ matrix.T * scale + center
    low, high = np.floor(transformed.min(0)).astype(int), np.ceil(transformed.max(0)).astype(int)
    x, z = np.meshgrid(np.arange(low[0], high[0]+1), np.arange(low[2], high[2]+1), indexing='ij')
    for y in range(low[1], high[1]+1):
        world = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        local = np.rint((world-center) @ matrix / scale).astype(int)-lo+1
        inside = np.all((local>=0)&(local<size), axis=1)
        world, local = world[inside], local[inside]
        values = volume[tuple(local.T)]
        selected = values>0
        p.points(world[selected], 1)
        p.values[-1] = values[selected]
    result = p.finish()
    result.metadata.update(center=list(center), scale=scale, roll=roll, pitch=pitch, connection='主臂腕部' if main else '独立悬浮袖口，原作无连续臂根')
    return result


def build():
    parts = []
    torso = part('torso', '收腰胸甲 · 眼形与叶形金纹', 'body')
    levels = [(112, -.5, -3, 20, 14), (130, -.5, -3, 29, 19), (160, -.5, -3, 43, 27), (190, -.5, -3, 47, 24), (207, -.5, -3, 35, 18), (214, -.5, -3, 18, 12)]
    loft(torso, levels, BLACK, 3)
    for side in (-1, 1):
        panel(torso, [(0, 204), (23, 212), (43, 201), (44, 193), (30, 201), (20, 203), (0, 194)], 17, 8, WHITE, side)
        curve(torso, [(0, 174), (16, 170), (27, 181), (35, 194)], side, 1.7)
        curve(torso, [(35, 194), (24, 185), (5, 194), (5, 178)], side, 1.7)
        curve(torso, [(5, 178), (5, 176), (2, 175), (0, 174)], side, 1.7)
        curve(torso, [(4, 169), (20, 169), (17, 153), (26, 145)], side, 1.4)
        curve(torso, [(26, 145), (11, 154), (6, 157), (4, 169)], side, 1.4)
        motif(torso, [(39, 186), (42, 175), (39, 159), (30, 143), (23, 129)], side, .7, GRAY)
        torso.ring((side*39-.5, 179, -2), 17, 2.2, GOLD, normal=(side, .05, 0), depth=3)
        torso.ring((side*40-.5, 179, -2), 14.5, 2, STUDS, normal=(side, .05, 0), depth=5)
    loft(torso, [(103, -.5, -3, 16, 12), (114, -.5, -3, 23, 15), (120, -.5, -3, 21, 15)], STUDS, 3)
    parts.append(torso.finish())

    back = part('back', '背部 · 分片脊甲与肩后连接', 'body')
    for y, r in ((124, 22), (142, 30), (161, 35), (180, 37), (197, 28)):
        back.hull([(-r, y-6, -12), (r-1, y-6, -12), (-r*.7, y+7, -15), (r*.7-1, y+7, -15), (-r*.85, y-2, -28), (r*.85-1, y-2, -28), (-4, y+8, -30), (3, y+8, -30)], WHITE if y in (142, 180) else BLACK)
    for side in (-1, 1):
        stroke(back, [(0, 200, -27), (14, 188, -30), (29, 192, -21)], 1, GOLD, side)
        stroke(back, [(1, 196, -29), (9, 185, -31), (8, 178, -31)], .8, GOLD, side)
        back.beam((side*27-.5, 192, -16), (side*54-.5, 192, -13), 5, STUDS)
    parts.append(back.finish())

    for side, label in ((-1, '左'), (1, '右')):
        shoulder = part(f'shoulder_{side}', label+'肩 · 上翘尖甲与环形肩根', 'arms')
        shoulder.beam(*mirror([(44, 189, -2), (65, 180, -1)], side), 11, BLACK)
        joint(shoulder, mirror([59, 183, -2], side), 12)
        panel(shoulder, [(46, 193), (55, 213), (78, 232), (95, 252), (89, 217), (79, 188), (65, 174)], 13, -16, WHITE, side)
        panel(shoulder, [(61, 199), (80, 213), (91, 226), (85, 195), (73, 178)], 17, -5, BLACK, side)
        stroke(shoulder, [(51, 196, 14), (65, 206, 15), (83, 231, 9)], 1, GRAY, side)
        panel(shoulder, [(57, 183), (72, 193), (86, 186), (91, 174), (70, 169)], 18, -12, WHITE, side)
        stroke(shoulder, [(65, 178, 19), (80, 177, 19), (87, 181, 19)], .8, GRAY, side)
        parts.append(shoulder.finish())

        arm = part(f'arm_{side}', label+'主臂 · 金球肘与叶刃前臂', 'arms')
        for a, b, r in [((68, 178, -2), (85, 148, 0), 9), ((86, 142, 0), (88, 109, 15), 7)]:
            arm.beam(*mirror([a, b], side), r, BLACK)
        joint(arm, mirror([86, 145, 1], side), 13)
        panel(arm, [(74, 136), (91, 137), (105, 116), (111, 89), (93, 95), (80, 108)], 25, -3, WHITE, side)
        panel(arm, [(99, 132), (111, 155), (111, 118), (103, 100)], 9, -8, BLACK, side)
        polygon(arm, [(85, 113), (94, 123), (104, 112), (96, 110), (87, 103)], 28, 25, GOLD, side)
        stroke(arm, [(82, 131, 26), (89, 122, 27), (101, 116, 27)], 1, GRAY, side)
        arm.beam(*mirror([(89, 107, 13), (89, 94, 17)], side), 4, GOLD)
        parts.append(arm.finish())
        parts.append(hand((side*89-.5, 83, 20), 1.1, 180+side*8, -15, f'main_hand_{side}', True, .8))

        leg = part(f'leg_{side}', label+'腿 · 分层盾甲与三点孔纹', 'body')
        cx = side*27-.5
        loft(leg, [(1, cx, -7, 8, 10), (17, cx, -4, 12, 14), (45, cx, -3, 17, 19), (76, cx, -3, 21, 21), (105, cx, -3, 20, 17), (116, cx, -3, 15, 13)], BLACK, 3)
        joint(leg, mirror([27, 106, -2], side), 12)
        panel(leg, [(8, 104), (18, 119), (39, 117), (52, 101), (50, 78), (38, 43), (34, 68), (23, 59), (13, 78)], 26, 8, WHITE, side)
        polygon(leg, [(16, 76), (23, 83), (31, 72), (42, 85), (39, 61), (33, 47), (27, 64), (21, 59)], 28, 25, BLACK, side)
        stroke(leg, [(11, 103, 28), (20, 114, 28), (38, 112, 28), (48, 100, 28)], .7, GRAY, side)
        for x, y in ((24, 106), (32, 107), (28, 100)):
            leg.beam(*mirror([(x, y, 27), (x, y, 28)], side), 1.7, BLACK)
        for x, y in ((14, 119), (25, 124), (36, 120), (46, 113)):
            polygon(leg, [(x-2, y-8), (x+2, y-8), (x, y+3)], 15, 10, GOLD, side)
        panel(leg, [(15, 48), (31, 36), (40, 47), (34, 17), (28, 0), (18, 17)], 16, -2, BLACK, side)
        stroke(leg, [(14, 52, 16), (21, 40, 18), (28, 31, 18)], 1, GRAY, side)
        parts.append(leg.finish())

    pelvis = part('pelvis', '腰下 · 分叉金边悬垂甲', 'body')
    for side in (-1, 1):
        polygon(pelvis, [(0, 113), (12, 104), (15, 84), (8, 65), (4, 83), (0, 91)], 14, 4, GOLD, side)
        polygon(pelvis, [(1, 105), (8, 98), (10, 85), (7, 76), (5, 90)], 16, 14, BLACK, side)
    parts.append(pelvis.finish())

    head = part('helmet', '尖额盔 · 红眼与W形下颌', 'head')
    head.beam((-.5, 207, -1), (-.5, 222, -1), 6, STUDS)
    loft(head, [(214, -.5, 1, 10, 9), (223, -.5, 1, 17, 12), (237, -.5, -1, 18, 12), (243, -.5, -2, 12, 9)], BLACK, 3)
    mask = Image.new('L', (41, 36))
    draw = ImageDraw.Draw(mask)
    for side in (-1, 1):
        def face(points, state):
            draw.polygon([(round((x if side>0 else -1-x)+20), round(247-y)) for x, y in points], fill=state)
        face([(0, 245), (14, 238), (18, 227), (17, 215), (10, 218), (5, 215), (0, 218)], GOLD)
        face([(2, 229), (7, 233), (15, 229), (16, 222), (10, 224), (7, 226), (2, 223)], BLACK)
        face([(4, 227), (8, 229), (12, 227), (9, 227), (7, 228), (6, 226)], RED)
        face([(3, 219), (7, 222), (11, 219), (15, 221), (14, 217), (10, 216), (7, 220), (5, 217)], BLACK)
        face([(0, 245), (1, 240), (1, 230), (0, 225)], LIGHT)
    values = np.asarray(mask)
    iy, ix = np.nonzero(values)
    x, y = ix-20, 247-iy
    z = np.rint(16-.024*x*x+.025*(y-225)).astype(int)
    for depth in (0, 1, 2):
        head.points(np.c_[x, y, z-depth], 1)
        head.values[-1] = values[iy, ix]
    parts.append(head.finish())

    floating = [
        ((-142, 185, 18), .88, -35, -8, .2),
        ((-125, 254, -2), .76, -70, -12, .9),
        ((-60, 253, 14), .94, -32, 4, .55),
        ((-166, 110, 21), 1.02, -67, -5, .85),
        ((-113, 82, 35), .67, -111, 15, .5),
        ((67, 254, 16), 1.02, 28, -12, .25),
        ((137, 185, 11), .96, 47, -2, .25),
        ((165, 112, 24), 1.02, 82, -15, .65),
        ((171, 215, -12), .69, 32, 18, .95),
    ]
    for i, (center, scale, roll, pitch, curl) in enumerate(floating, 1):
        parts.append(hand(center, scale, roll, pitch, f'floating_hand_{i:02}', curl=curl))
    return parts
