import math
from types import SimpleNamespace

import numpy as np
from scipy.ndimage import distance_transform_cdt, label


QSV = 'hk3gtl:voltage_machine_casing_qsv'
WHITE, GRAY, BLACK = ('minecraft:' + c + '_concrete' for c in ('white', 'light_gray', 'black'))
IRON, LIGHT = 'minecraft:iron_block', 'minecraft:sea_lantern'
GLASS, CYAN, ICE = 'minecraft:light_blue_stained_glass', 'minecraft:cyan_stained_glass', 'minecraft:blue_ice'
CONTROL = 'minecraft:redstone_block'
STATES = [QSV, WHITE, GRAY, BLACK, IRON, LIGHT, GLASS, CYAN, ICE, CONTROL]
IDS = {s: i for i, s in enumerate(STATES, 1)}
NAMES = dict(zip(STATES, ['QSV冰晶蓝机壳', '白色混凝土', '浅灰混凝土', '黑色混凝土', '铁块', '海晶灯', '淡蓝色染色玻璃', '青色染色玻璃', '蓝冰', '主控位置标记']))
ROLES = dict(zip(STATES, ['六棱塔框架、低温机组与冷媒回路', '承台收边、密封环和热端机壳', '基座检修面与后部冷凝机房', '承重基础、机械接缝和工艺分区', '热端独立换热鳍片', '静态晶体细芯、工艺灯与引导线', '密封凝态塔和冠冕晶体的透明外层', '晶体内层、塔内凝态核心和冷媒观察槽', '凝态室下承台及结晶工艺件', '仅定位本候选主控；已有W06真实GT控制器']))
PARTS = []


def grid(x0, x1, z0, z1):
    z, x = np.mgrid[z0:z1+1, x0:x1+1]
    return x, z


def part(name, layers):
    points, values = [], []
    for y, x, z, states in layers:
        occupied = states > 0
        points.append(np.c_[x[occupied], np.full(occupied.sum(), y), z[occupied]])
        values.append(states[occupied])
    return SimpleNamespace(name=name, p=np.concatenate(points).astype(np.int32), states=np.concatenate(values).astype(np.uint8))


def hexmetric(x, z):
    return np.maximum(abs(z), .8660254 * abs(x) + .5 * abs(z))


def deck():
    x, z = grid(-400, 400, -360, 360)
    edge = np.minimum.reduce([400-abs(x), 360-abs(z), (715-abs(x)-abs(z))//2])
    layers = []
    for y in range(-24, 12):
        mask = edge >= 0
        if -21 <= y <= 7:
            mask &= (edge <= 7) | (abs(x) <= 10) | (abs(z) <= 10)
        state = np.where(mask, IDS[BLACK], 0).astype(np.uint8)
        if y >= 8:
            state[mask] = IDS[WHITE]
            state[edge >= 8] = IDS[QSV]
            state[edge >= 13] = IDS[GRAY]
        if y == 11:
            state[(edge >= 16) & (edge <= 17)] = IDS[LIGHT]
            state[(abs(x) <= 28) & (z >= 155) & (z <= 326)] = IDS[BLACK]
            state[(abs(abs(x)-32) <= 1) & (z >= 155) & (z <= 326)] = IDS[QSV]
            state[(abs(abs(x)-190) <= 2) & (abs(z) <= 305)] = IDS[WHITE]
        layers.append((y, x, z, state))
    return part('deck', layers)


def tower():
    x, z = grid(-195, 195, -200, 190)
    metric = hexmetric(x, z+5)
    layers = []
    for y in range(12, 226):
        state = np.zeros(x.shape, np.uint8)
        if y <= 42:
            radius = 118 if y <= 20 else 112 if y <= 30 else 105
            state[metric <= radius] = IDS[BLACK if y <= 20 else QSV if y <= 30 else WHITE]
            if y >= 35:
                state[metric <= 96] = IDS[ICE]
        elif y <= 214:
            state[(metric <= 98) & ((metric >= 95) | (y <= 45) | (y >= 209))] = IDS[GLASS]
            state[(metric <= 104) & (metric >= 96) & ((y <= 52) | (y >= 204))] = IDS[QSV]
            state[(metric <= 105) & (metric >= 101) & ((y <= 47) | (y >= 209))] = IDS[WHITE]
            for angle in np.arange(6)*math.pi/3:
                vx, vz = math.cos(angle)*117, math.sin(angle)*117
                column = (abs(x-vx) <= 4) & (abs(z+5-vz) <= 4)
                state[column] = IDS[QSV]
                state[column & (abs(x-vx) <= 1) & (abs(z+5-vz) <= 1)] = IDS[LIGHT]
        else:
            state[(metric >= 105) & (metric <= 147)] = IDS[QSV] if y <= 219 else IDS[WHITE]
            state[(metric >= 112) & (metric <= 140)] = 0
            if y >= 222:
                state[(metric >= 143) & (metric <= 146)] = IDS[LIGHT]
        layers.append((y, x, z, state))
    return part('sealed_hex_tower', layers)


def crystal(name, cx, cz, bottom, top, width, lean=0, angle=0):
    extent = math.ceil(width*1.3+abs(lean)+2)
    x, z = grid(round(cx)-extent, round(cx)+extent, round(cz)-extent, round(cz)+extent)
    layers = []
    for y in range(bottom, top+1):
        t = (y-bottom)/(top-bottom)
        shift = lean*t
        dx, dz = x-cx-math.cos(angle)*shift, z-cz-math.sin(angle)*shift
        metric = hexmetric(dx, dz)
        radius = np.interp(t, [0, .18, .66, 1], [1, width*.74, width, 1])
        state = np.where(metric <= radius, IDS[GLASS], 0).astype(np.uint8)
        state[metric <= radius*.58] = IDS[CYAN]
        state[(abs(dx) <= 1.2) & (abs(dz) <= 1.2) & (metric <= radius)] = IDS[LIGHT]
        layers.append((y, x, z, state))
    return part(name, layers)


def cage():
    x, z = grid(-72, 72, -77, 67)
    radius = np.hypot(x, z+5)
    layers = []
    for y in range(58, 199):
        state = np.zeros(x.shape, np.uint8)
        if y in range(72, 78) or y in range(191, 197):
            state[(radius >= 48) & (radius <= 54)] = IDS[WHITE]
            state[(radius >= 50) & (radius <= 52)] = IDS[LIGHT]
        for angle in np.arange(6)*math.pi/3:
            vx, vz = math.cos(angle)*65, math.sin(angle)*65
            post = (abs(x-vx) <= 2) & (abs(z+5-vz) <= 2)
            state[post] = IDS[QSV]
        layers.append((y, x, z, state))
    return part('core_constraint_cage', layers)


def machinery():
    x, z = grid(-160, 160, -315, -199)
    layers = []
    for y in range(12, 134):
        state = np.zeros(x.shape, np.uint8)
        for z0, z1, width, top in [(-245, -199, 160, 57), (-280, -246, 130, 91), (-315, -281, 100, 125)]:
            region = (z >= z0) & (z <= z1) & (abs(x) <= width)
            wall = region & ((abs(x) >= width-3) | (z <= z0+3) | (z >= z1-3) | (y <= 15) | (y >= top-3))
            if y <= top:
                state[wall] = IDS[GRAY]
                state[wall & ((y >= top-4) | (abs(x) >= width-3))] = IDS[WHITE]
                state[region & (z >= z1-2) & (y >= 24) & (y <= top-12) & (abs(x) <= width-12)] = IDS[GLASS]
                state[wall & (abs(x) % 40 <= 2)] = IDS[QSV]
            if top < y <= top+8:
                state[region & (abs(x) % 18 <= 2) & (z <= z1-9) & (z >= z0+9)] = IDS[IRON]
        layers.append((y, x, z, state))
    return part('stepped_condensation_hall', layers)


def loop(side):
    x, z = grid(side*275-47, side*275+47, -217, 217)
    distance = np.hypot(x-side*275, np.maximum(abs(z)-170, 0))
    layers = []
    for y in range(12, 40):
        state = np.zeros(x.shape, np.uint8)
        ring = (distance >= 31) & (distance <= 47)
        state[ring] = IDS[BLACK if y <= 17 else QSV if y <= 22 else CYAN]
        if y >= 23:
            state[ring & ((distance <= 33) | (distance >= 45))] = IDS[WHITE]
            state[ring & (distance >= 38) & (distance <= 40)] = IDS[LIGHT if y == 39 else GLASS]
        layers.append((y, x, z, state))
    return part('coolant_loop_' + ('left' if side < 0 else 'right'), layers)


def heat(side, cz):
    cx = side*351
    x, z = grid(cx-25, cx+25, cz-27, cz+27)
    layers = []
    for y in range(12, 69):
        state = np.zeros(x.shape, np.uint8)
        if y <= 17:
            state[:] = IDS[BLACK]
        elif y <= 60:
            state[(abs(x-cx) <= 19) & (abs(z-cz) <= 22)] = IDS[QSV]
            state[(abs(x-cx) <= 24) & (abs(z-cz) <= 24) & ((z-cz) % 7 <= 1)] = IDS[IRON]
            state[(abs(x-cx) >= 20) & (abs(x-cx) <= 24) & (abs(z-cz) <= 24)] = IDS[WHITE]
        else:
            state[(abs(x-cx) <= 22) & (abs(z-cz) <= 25)] = IDS[WHITE]
            state[(abs(x-cx) <= 15) & (abs(z-cz) <= 19)] = IDS[BLACK]
            state[(abs(x-cx) <= 2) & (abs(z-cz) <= 16)] = IDS[LIGHT]
        layers.append((y, x, z, state))
    return part(f'heat_end_{side:+d}_{cz:+d}', layers)


def control():
    x, z = grid(-36, 36, 285, 310)
    layers = []
    for y in range(12, 39):
        state = np.full(x.shape, IDS[BLACK if y <= 20 else QSV if y <= 33 else WHITE], np.uint8)
        if y >= 25:
            state[(abs(x) <= 25) & (z >= 308)] = IDS[GLASS]
        if y == 30:
            state[(x == 0) & (z == 310)] = IDS[CONTROL]
        layers.append((y, x, z, state))
    return part('front_controller', layers)


def build():
    entries = [(deck(), '覆盖全机投影的承托基座'), (tower(), '六棱密封凝态塔与开放冠冕框架'),
        (crystal('suspended_condensed_core', 0, -5, 100, 183, 27), '塔内悬浮凝态核心'),
        (cage(), '独立六柱核心约束架'), (machinery(), '后部退台冷凝机房')]
    for i, top in enumerate([365, 347, 347, 365, 391, 391]):
        angle = i*math.pi/3
        entries += [(crystal(f'crown_main_{i+1}', math.cos(angle)*145, math.sin(angle)*145-5, 235, top, 23, 12, angle), f'冠冕第{i+1}组长冰晶')]
        entries += [(crystal(f'crown_satellite_{i+1}', math.cos(angle)*205, math.sin(angle)*205-5, 242, [316,302,302,316,335,335][i], 11, 7, angle), f'冠冕第{i+1}组短冰晶')]
    for side, name in [(-1, '左'), (1, '右')]:
        entries += [(loop(side), name+'侧低位闭合冷媒回路')]
        entries += [(heat(side, z), name+f'侧独立热端机组{n+1}') for n,z in enumerate([-245, 0, 245])]
    entries += [(control(), '前庭居中主控台')]
    PARTS[:] = [dict(id=p.name, name=name) for p,name in entries]
    parts = [p for p,_ in entries]
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = high-low+1
    cube = np.zeros((size[1],size[2],size[0]), np.uint8)
    owners = np.zeros_like(cube)
    for index,p in enumerate(parts, 1):
        q = p.p-low
        occupied = owners[q[:,1],q[:,2],q[:,0]]
        collisions = np.flatnonzero(occupied)
        if len(collisions):
            raise ValueError(f'{p.name} 与其他构件交叠 {len(collisions)} 格，首个坐标 {p.p[collisions[0]].tolist()}，已有owner={int(occupied[collisions[0]])}')
        owners[q[:,1],q[:,2],q[:,0]] = index
        cube[q[:,1],q[:,2],q[:,0]] = p.states
    footprint = owners[11-low[1]] == 1
    projection = (owners > 1).any(axis=0)
    outside = int((projection & ~footprint).sum())
    margin = int(distance_transform_cdt(footprint, metric='chessboard')[projection].min())-1
    if outside:
        raise ValueError(f'上部投影超出底座 {outside} 列')
    crystals = []
    for p in parts:
        if p.name.startswith('crown_') or p.name == 'suspended_condensed_core':
            q = p.p-p.p.min(0)
            dense = np.zeros(tuple(q.max(0)+1), bool)
            dense[tuple(q.T)] = True
            crystals.append(dict(id=p.name, blocks=len(p.p), six_connected_components=int(label(dense)[1])))
    clearance = dict(method='全部独立构件合并前按实际整数格查重，交叠即停止；未覆盖消解、未裁切。',
        independent_components=len(parts), checked_component_pairs=len(parts)*(len(parts)-1)//2,
        cross_component_overlapping_voxels=0, overlap_pairs=[], all_static=True, runtime_animation=False,
        crystal_connectivity=crystals,
        critical_clearances=[dict(first='冠冕框架',second='长冰晶',surface_gap_voxels=9,method='完整Y分层边界225与235'),
            dict(first='悬浮核心',second='核心下约束环',surface_gap_voxels=22,method='Y边界77与100'),
            dict(first='悬浮核心',second='核心上约束环',surface_gap_voxels=7,method='Y边界183与191'),
            dict(first='右冷媒回路',second='中热端脚座',surface_gap_voxels=3,method='完整X边界322与326')],
        base_projection=dict(bottom_size_wd=[801,721],outside_top_deck_columns=outside,minimum_projected_border_margin_voxels=margin),
        intentional_joins='承台顶Y11与落地设备底Y12相接；塔体、框架、机房分层均为各自构件内部连续材质分区。六组冠冕与塔顶保留空气隙。',
        scope='仅完整静态外观与构件净空；不代替GT成型、运行或游戏验收。')
    def detail(center, half, position):
        return dict(center=(np.array(center)-low).tolist(), half=half,position=(np.array(position)-low).tolist())
    data = dict(title='冰之律者 · 永霜 · 冰晶冠冕凝态宫 A2', name='0005-w06-crystal-crown-a2',size=size.tolist(),
        controller=(np.array([0,30,310])-low).tolist(),controller_face='south',ports=[],
        summary='中央透明六棱密封凝态塔包裹悬浮核心；塔顶六组长短交错、彼此分离的冰晶形成开放冠冕。后置退台冷凝机房、左右低位闭合冷媒回路与六台独立热端围绕主塔，前庭居中主控。全静态。',
        detail_views=dict(core=detail([0,142,-5],[130,112,130],[255,190,350]),
            crown=detail([0,310,-5],[240,110,240],[530,430,630]),
            heat=detail([351,44,0],[54,55,67],[515,125,230])),
        palette_identity=dict(tier='QSV',name='冰晶蓝',color='#91DCEB',runtime_voltage='WSV'),
        source_blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),source_blueprint_to_export=(-low).tolist(),nominal_clipping=False,
        geometry_clearance=clearance,original_translation='冰晶冠冕、六棱密封塔及内部悬核为原创工业建筑转译，不宣称安娜或原作源模型复刻。',
        animation_enabled=False,approved=False,installed=False,game_verified=False)
    print('W06 A2几何完成',size.tolist(),int(np.count_nonzero(cube)),len(parts),'构件交叠0、底座外投影',outside,'外沿',margin,flush=True)
    return cube,owners,data
