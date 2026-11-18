from pathlib import Path
import math

import numpy as np
from scipy.spatial import cKDTree

from w02_19c_geometry_v4_20261110 import SolidPart, hull, solid_annulus, bezier
from w02_19c_geometry_v2_20261110 import panel


ROOT = Path(__file__).resolve().parents[2]
GREEN = 'hk3gtl:voltage_machine_casing_hdv'
WHITE, GRAY, BLACK = ('minecraft:' + color + '_concrete' for color in ('white', 'light_gray', 'black'))
IRON, LIGHT = 'minecraft:iron_block', 'minecraft:sea_lantern'
LIME, GLASS, CYAN = 'minecraft:lime_concrete', 'minecraft:green_stained_glass', 'minecraft:cyan_stained_glass'
CONTROL = 'minecraft:redstone_block'
STATES = [GREEN, WHITE, GRAY, BLACK, IRON, LIGHT, LIME, GLASS, CYAN, CONTROL]
IDS = {state: index for index, state in enumerate(STATES, 1)}
NAMES = dict(zip(STATES, ['HDV风息绿机壳', '白色混凝土', '浅灰混凝土', '黑色混凝土', '铁块', '海晶灯', '黄绿色混凝土', '绿色染色玻璃', '青色染色玻璃', '主控位置标记']))
ROLES = dict(zip(STATES, ['风翼主甲、约束器与回流槽外壳', '羽片白边和承台收边', '检修承台与设备裙边', '承力脊、机械接缝与基础', '换热鳍片、轴承及检修件', '静态导流光脊与晶体内芯', '晶体棱线和风车纹章', '渴望宝石的建筑转译外层', '静态分段导流带和流道观察层', '仅定位本候选主控，W05真实GT主控已有注册']))
PARTS = []


class Part(SolidPart):
    def points(self, points, state):
        points = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(points)
        self.values.append(np.full(len(points), IDS[state], np.uint8))


def trace(p, points, radius, state):
    for a, b in zip(points[:-1], points[1:]):
        p.beam(a, b, radius, state)


def slab(p, outline, y0, y1, state):
    hull(p, [(x, y, z) for y in (y0, y1) for x, z in outline], state)


def cylinder(p, center, radius, inner, depth, state, axis=(0, 1, 0)):
    solid_annulus(p, center, axis, radius, inner, depth, state)


def deck():
    p = Part('deck')
    outline = [(-300, -270), (300, -270), (370, -190), (370, 90), (240, 180),
               (160, 180), (160, 320), (-160, 320), (-160, 180), (-240, 180), (-370, 90), (-370, -190)]
    slab(p, outline, 0, 7, BLACK)
    slab(p, outline, 8, 11, WHITE)
    slab(p, [(x * .975, z * .975) for x, z in outline], 9, 11, GREEN)
    slab(p, [(x * .955, z * .955) for x, z in outline], 10, 11, GRAY)
    for side in (-1, 1):
        for x in (174, 320):
            p.box([side*x-2, 11, -176], [side*x+2, 11, 85], BLACK)
        for z in range(-234, 245, 28):
            p.box([side*44-2, 11, z], [side*44+2, 11, z+12], WHITE)
        for z in (-234, -130, -26, 78):
            p.box([side*338-4, 11, z], [side*338+4, 11, z+9], LIGHT)
    p.box([-28, 11, 170], [28, 11, 275], BLACK)
    for x in (-31, 31):
        p.box([x-1, 11, 170], [x+1, 11, 276], WHITE)
    return p.finish()


def collector():
    p = Part('collector')
    for y, r, inner, depth, state in [(18, 116, 0, 12, BLACK), (27, 112, 0, 6, GREEN),
        (34, 105, 0, 7, GRAY), (40, 102, 88, 5, WHITE), (45, 88, 0, 5, BLACK),
        (54, 85, 71, 12, GREEN), (61, 86, 78, 3, WHITE), (65, 70, 0, 7, BLACK),
        (72, 65, 51, 7, GREEN), (78, 64, 57, 3, LIGHT), (84, 50, 32, 8, IRON),
        (91, 52, 42, 5, GREEN), (97, 41, 0, 6, BLACK), (102, 34, 23, 4, LIME),
        (107, 32, 23, 5, LIGHT)]:
        cylinder(p, [0, y, 55], r, inner, depth, state)
    for a in np.arange(12)*math.pi/6:
        u = np.array([math.cos(a), 0, math.sin(a)])
        p.beam(u*71+[0, 42, 55], u*104+[0, 35, 55], 2, IRON)
        p.beam(u*60+[0, 73, 55], u*76+[0, 54, 55], 2, WHITE)
    return p.finish()


def crystal():
    p = Part('gem')
    center = np.array([0, 250, 55])
    for y in range(170, 346):
        r = float(np.interp(y, [170, 215, 284, 345], [0, 40, 40, 0]))
        z, x = np.mgrid[-30:31, -40:41]
        metric = np.maximum(abs(x), abs(x)*.5 + abs(z)*40/30*.866)
        inside = metric <= r
        state = np.full(x.shape, IDS[GLASS], np.uint8)
        state[(abs(x) < 6) & (abs(z) < 5)] = IDS[LIGHT]
        state[(metric >= r-1.4) & ((x >= 0) == (z >= 0))] = IDS[LIME]
        for value in np.unique(state[inside]):
            mask = inside & (state == value)
            p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]+center[2]], STATES[value-1])
    return p.finish()


def constraint(side):
    p = Part('constraint_' + ('left' if side < 0 else 'right'))
    p.box([side*155-18, 12, -35], [side*155+18, 38, 5], BLACK)
    curve = [[side*155, 39, -15], [side*152, 150, -15], [side*137, 309, -15], [side*27, 374, -15]]
    route = np.array([bezier(curve, t) for t in np.linspace(0, 1, 80)])
    trace(p, route, 8, BLACK)
    trace(p, route+[0, 0, 7], 5, GREEN)
    trace(p, route+[0, 0, 12], 1.7, LIGHT)
    for t in np.linspace(.15, .89, 11):
        c = bezier(curve, t)
        cylinder(p, c+[0, 0, 10], 10, 7, 4, WHITE, (0, 0, 1))
    return p.finish()


def wing_frame(side):
    p = Part('wing_frame_' + ('left' if side < 0 else 'right'))
    p.box([side*108-28, 12, -235], [side*108+28, 30, -185], BLACK)
    p.box([side*108-24, 31, -231], [side*108+24, 38, -189], GREEN)
    route = np.array([[side*108, 39, -210], [side*93, 140, -210],
                      [side*104, 250, -210], [side*128, 357, -210]])
    trace(p, route, 10, BLACK)
    trace(p, route+[side*9, 0, 1], 3.5, WHITE)
    for i, y in enumerate((142, 176, 210, 244, 278, 312, 346)):
        x = side*(93+max(0, y-140)*.16)
        cylinder(p, [x, y, -190], 15, 9, 12, GREEN, (0, 0, 1))
        cylinder(p, [x, y, -182], 13, 10, 3, LIGHT, (0, 0, 1))
    return p.finish()


FEATHERS = [(126, 345, 354, 452), (120, 310, 359, 379), (114, 275, 347, 306),
            (108, 240, 324, 233), (102, 205, 286, 164), (96, 170, 235, 105),
            (90, 135, 176, 67)]


def feather(side, index):
    p = Part(('left' if side < 0 else 'right') + '_feather_' + str(index+1))
    x0, y0, x1, y1 = FEATHERS[index]
    a, b = np.array([x0, y0], float), np.array([x1, y1], float)
    direction = b-a
    normal = np.array([-direction[1], direction[0]])/np.linalg.norm(direction)
    middle = a+direction*.43
    outline = np.array([a+normal*7, middle+normal*16, b, middle-normal*13, a-normal*7])
    outline[:, 0] *= side
    z = -162+index*3
    panel(p, outline, z-9, z+5, BLACK, 0)
    panel(p, outline, z-4, z+8, WHITE, 0)
    origin = outline.mean(0)
    inset = origin+(outline-origin)*np.array([.93, .72])
    panel(p, inset, z+7, z+10, GREEN, 0)
    root, tip = np.array([side*x0, y0, z+11]), np.array([side*x1, y1, z+11])
    trace(p, [root*.91+tip*.09, root*.30+tip*.70, root*.10+tip*.90], 1.2, LIGHT)
    for t in (.24, .48, .69):
        c = root*(1-t)+tip*t
        p.beam(c+[side*4, -3, 0], c+[side*8, 2, 0], 1, IRON)
    return p.finish()


def flow_channel(side):
    p = Part('channel_' + ('left' if side < 0 else 'right'))
    z, x = np.mgrid[-153:154, -47:48]
    q = np.sqrt((x/46)**2+(z/152)**2)
    for y in range(12, 54):
        keep = (q <= 1) & (q >= .72)
        state = BLACK if y < 21 else GREEN
        if y in (22, 23, 51, 52, 53):
            state = WHITE
        if 27 <= y <= 31:
            state = CYAN
        p.points(np.c_[x[keep]+side*252, np.full(keep.sum(), y), z[keep]], state)
    for end in (-1, 1):
        p.box([side*252-16, 20, end*140-5], [side*252+16, 24, end*140+5], IRON)
    return p.finish()


def pump(side, end):
    p = Part(('left' if side < 0 else 'right') + '_pump_' + ('rear' if end < 0 else 'front'))
    x, z = side*252, end*211
    p.box([x-43, 12, z-39], [x+43, 20, z+39], BLACK)
    p.box([x-40, 21, z-36], [x+40, 25, z+36], GREEN)
    for y, radius, inner, depth, state in [(32, 31, 0, 12, IRON), (41, 34, 26, 5, WHITE),
        (53, 28, 18, 19, GREEN), (65, 31, 24, 5, WHITE), (74, 24, 15, 12, IRON),
        (82, 26, 20, 3, GREEN), (86, 19, 0, 4, CYAN), (90, 12, 0, 3, LIGHT)]:
        cylinder(p, [x, y, z], radius, inner, depth, state)
    for dx in (-38, 38):
        p.box([x+dx-3, 26, z-29], [x+dx+3, 57, z+29], BLACK)
        for dz in range(-27, 28, 6):
            p.box([x+dx-4, 29, z+dz], [x+dx+4, 54, z+dz+2], IRON)
    return p.finish()


def ribbon(side):
    p = Part('ribbon_' + ('left' if side < 0 else 'right'))
    curve = np.array([[side*55, 257, 55], [side*135, 370, 185],
                      [side*230, 210, 160], [side*252, 73, 0]])
    route = [bezier(curve, t) for t in np.linspace(0, 1, 95)]
    trace(p, route, 3.5, CYAN)
    trace(p, route, 1.2, LIGHT)
    return p.finish()


def badge():
    p = Part('badge')
    p.box([-58, 12, 207], [58, 20, 261], BLACK)
    p.box([-54, 21, 211], [54, 25, 257], WHITE)
    for side in (-1, 1):
        p.beam([side*54, 26, 220], [side*54, 77, 223], 3, BLACK)
        p.beam([side*54, 26, 224], [side*54, 77, 227], 1.2, GREEN)
        p.beam([side*54, 77, 223], [side*54, 77, 234], 2, IRON)
    center = np.array([0, 111, 234])
    cylinder(p, center, 64, 60, 6, BLACK, (0, 0, 1))
    cylinder(p, center+[0, 0, 5], 63, 61, 3, WHITE, (0, 0, 1))
    cylinder(p, center, 11, 0, 16, GREEN, (0, 0, 1))
    cylinder(p, center+[0, 0, 10], 6, 0, 4, LIGHT, (0, 0, 1))
    return p.finish()


def badge_sail(index):
    p = Part('badge_sail_'+str(index+1))
    sail = np.array([(8, 8), (26, 7), (51, 27), (43, 49), (25, 44), (13, 19)])*.70+8/math.sqrt(2)
    a = index*math.pi/2
    matrix = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    outline = sail@matrix.T+[0, 111]
    panel(p, outline, 233, 242, WHITE, 0)
    midpoint = outline.mean(0)
    panel(p, midpoint+(outline-midpoint)*.74, 243, 245, LIME, 0)
    return p.finish()


def control():
    p = Part('control')
    p.box([-50, 12, 280], [50, 20, 319], BLACK)
    p.box([-46, 21, 283], [46, 25, 316], WHITE)
    p.box([-33, 26, 294], [33, 42, 309], GREEN)
    p.box([-35, 43, 293], [35, 46, 310], WHITE)
    p.box([-11, 29, 310], [11, 39, 310], BLACK)
    p.box([0, 34, 310], [0, 34, 310], CONTROL)
    for side in (-1, 1):
        p.box([side*23-5, 30, 310], [side*23+5, 37, 310], CYAN)
        p.box([side*23-5, 39, 310], [side*23+5, 40, 310], LIGHT)
    return p.finish()


def build():
    entries = [(deck(), '展开式工业承台'), (collector(), '中央分级集流座'), (crystal(), '渴望之心悬浮晶体')]
    for side, name in ((-1, '左'), (1, '右')):
        entries += [(constraint(side), name+'侧开口约束轨'), (wing_frame(side), name+'翼后置磁悬浮翼骨')]
        entries += [(feather(side, i), name+'翼独立羽片'+str(i+1)) for i in range(7)]
        entries += [(flow_channel(side), name+'侧低位回流槽'), (pump(side, -1), name+'后换热泵'),
                    (pump(side, 1), name+'前换热泵'), (ribbon(side), name+'侧静态导流光带')]
    entries += [(badge(), '前庭风车外圈轮毂与支架')]
    entries += [(badge_sail(i), '风车独立叶片'+str(i+1)) for i in range(4)]
    entries += [(control(), '前控台与主控定位')]
    PARTS[:] = [dict(id=p.name, name=name) for p, name in entries]
    parts = [p for p, _ in entries]
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = high-low+1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    owners = np.zeros_like(cube)
    contacts = []
    for index, p in enumerate(parts, 1):
        q = p.p-low
        occupied = owners[q[:, 1], q[:, 2], q[:, 0]]
        collisions = np.bincount(occupied, minlength=len(parts)+1)
        for prior in np.flatnonzero(collisions[1:])+1:
            contacts.append(dict(first=parts[prior-1].name, second=p.name, voxels=int(collisions[prior])))
        owners[q[:, 1], q[:, 2], q[:, 0]] = index
        cube[q[:, 1], q[:, 2], q[:, 0]] = p.states
    if contacts:
        raise ValueError('独立构件交叠：'+str(contacts))
    named = {p.name: p for p in parts}
    pairs = [('gem', 'constraint_left'), ('gem', 'constraint_right'), ('gem', 'badge'),
             ('gem', 'collector'), ('gem', 'ribbon_left'), ('gem', 'ribbon_right')]
    pairs += [('badge', 'badge_sail_'+str(i)) for i in range(1, 5)]
    for side in ('left', 'right'):
        pairs += [('gem', side+'_feather_1'), ('gem', 'wing_frame_'+side)]
        pairs += [(side+'_feather_'+str(i), side+'_feather_'+str(i+1)) for i in range(1, 7)]
        pairs += [('wing_frame_'+side, side+'_feather_'+str(i)) for i in range(1, 8)]
    distances = []
    for first, second in pairs:
        a, b = named[first].p, named[second].p
        distance = float(cKDTree(a).query(b, k=1, p=np.inf, workers=-1)[0].min())
        distances.append(dict(first=first, second=second, minimum_center_chebyshev=distance,
                              surface_gap_voxel_lower_bound=max(0, math.floor(distance)-1)))
    clearance = dict(method='全部独立构件在最终整机合并前按整数格坐标查重；任何交叠立即停止，不覆盖消解、不裁切。关键净距为实际体素最近切比雪夫中心距向下取整减一，仅表示两件之间的表面间隔下界，不等于整机空闲通道证明。',
        independent_components=len(parts), checked_component_pairs=len(parts)*(len(parts)-1)//2,
        cross_component_overlapping_voxels=0, overlap_pairs=[], critical_clearances=distances,
        wing_feathers_per_side=7, all_static=True, runtime_animation=False,
        intentional_joins='承台顶面Y=11，各落地构件从Y=12起按面相接；羽片与后翼骨之间保留磁悬浮空气隙。单一构件内的分层甲面、灯带与内芯为同一实体的材料分区。',
        scope='本轮完整静态候选的实际方块；不将净空检查冒充游戏成型或运行验收。')
    def detail(center, half, position=None):
        value = dict(center=(np.array(center)-low).tolist(), half=half)
        if position is not None:
            value['position'] = (np.array(position)-low).tolist()
        return value
    data = dict(title='风之律者 · 长风 · 温蒂风翼与渴望之心 A2', name='0005-w05-wendy-wings-a2',
        size=size.tolist(), controller=(np.array([0, 34, 310])-low).tolist(), controller_face='south', ports=[],
        summary='中央青绿晶体悬于分级集流座上方；十四片分离的青绿白边风翼在后方展开，前庭风车纹章独立成景，两侧静态导流光带引向低位回流槽与四座换热泵。宝石、翼片、纹章、工业机组分层留空，全静态。',
        detail_views=dict(core=detail([0, 257, 55], [147, 129, 100]),
                          wing=detail([-224, 265, -154], [155, 195, 61], [-550, 350, 330])),
        palette_identity=dict(tier='HDV', name='风息绿', color='#48C9A3', runtime_voltage='WSV'),
        source_blueprint_bounds=dict(min=low.tolist(), max=high.tolist()), source_blueprint_to_export=(-low).tolist(),
        nominal_clipping=False, geometry_clearance=clearance,
        original_translation='风翼、渴望宝石、风车饰物取自温蒂形象；七片工业羽片、四叶风车以及晶体几何均为本项目建筑转译，非官方实体模型复刻。',
        animation_enabled=False, approved=False, installed=False, game_verified=False)
    print('几何完成', size.tolist(), int(np.count_nonzero(cube)), len(parts), '构件交叠0', flush=True)
    return cube, owners, data
