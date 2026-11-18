import math

import numpy as np
from scipy.spatial import cKDTree

from author_w05_shapes_20261115 import Part, SHELL, ARMOR, GLASS, IMPELLER, COIL, FRAME, bezier


ROOT_Z = [-253, -172, -91, -10, 71, 152]
TIP_Z = [-150, -65, 20, 105, 190, 273]
ROOT_Y = [115, 130, 145, 160, 145, 125]
TIP_Y = [190, 230, 267, 283, 240, 185]
TOWER_Z = [-170, 10, 190]


def solid_route(part, route, radius, state):
    route = np.asarray(route, float)
    distance = np.r_[0, np.cumsum(np.linalg.norm(np.diff(route, axis=0), axis=1))]
    samples = np.arange(0, distance[-1], .55)
    points = np.c_[[np.interp(samples, distance, route[:, i]) for i in range(3)]].T
    extent = math.ceil(radius)
    y, z, x = np.mgrid[-extent:extent+1, -extent:extent+1, -extent:extent+1]
    offsets = np.c_[x.ravel(), y.ravel(), z.ravel()]
    offsets = offsets[np.linalg.norm(offsets, axis=1) <= radius]
    part.points((np.rint(points).astype(int)[:, None, :] + offsets[None, :, :]).reshape(-1, 3), state)


def beam(side, index):
    name = 'left' if side < 0 else 'right'
    controls = np.array([[67, ROOT_Y[index], ROOT_Z[index]],
                         [112, ROOT_Y[index]+40, ROOT_Z[index]+10],
                         [238, TIP_Y[index]-8, TIP_Z[index]-35],
                         [270, TIP_Y[index], TIP_Z[index]]], float)
    controls[:, 0] *= side
    route = np.array([bezier(controls, t) for t in np.linspace(0, 1, 620)])
    p = Part(f'wing_{name}_beam_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}根后掠空心主梁',
             source='二·3：6对弧形空心主梁', centerline=route[::12].round(3).tolist(),
             outside_radius=7, inside_radius=4.2)
    tree = cKDTree(route)
    low, high = np.floor(route.min(0)-7).astype(int), np.ceil(route.max(0)+7).astype(int)
    z, x = np.mgrid[low[2]:high[2]+1, low[0]:high[0]+1]
    for y in range(low[1], high[1]+1):
        points = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        distance, nearest = tree.query(points)
        wall = (distance <= 7) & (distance >= 4.2)
        p.points(points[wall], SHELL)
        leading = wall & (points[:, 2] < route[nearest, 2]-3)
        p.points(points[leading], ARMOR)
        slot = wall & (abs(points[:, 1]-route[nearest, 1]) < 1.2) & (side*points[:, 0] > side*route[nearest, 0]+3)
        p.points(points[slot], COIL)
    for t in np.linspace(.12, .91, 7):
        center = bezier(controls, t)
        axis = bezier(controls, t+.002)-bezier(controls, t-.002)
        p.ring(center, 7.8, 1.9, FRAME, axis, 2.3)
    return p.finish()


def mobius(side):
    name = 'left' if side < 0 else 'right'
    p = Part(f'wing_{name}_mobius_network', f'{"左" if side < 0 else "右"}翼半扭转莫比乌斯环流管网',
             source='二·3：透明青绿流体管与银白外壳编织的莫比乌斯环流网',
             ribbon_center=[side*171, 164, 10], half_twist=True)
    paths = []
    for lane, u in enumerate(np.linspace(0, 20, 11)):
        angle = np.linspace(0, 2*math.pi if lane == 0 else 4*math.pi, 1400 if lane == 0 else 2800)
        route = np.c_[side*(171+(80+u*np.cos(angle/2))*np.cos(angle)),
                      164+62*np.sin(angle)+u*np.sin(angle/2),
                      10+(228+u*np.cos(angle/2))*np.sin(angle)]
        solid_route(p, route, 2.1, GLASS)
        solid_route(p, route, .85, COIL)
        for t in np.linspace(0, len(route)-10, 18 if lane == 0 else 36).astype(int):
            axis = route[t+8]-route[t]
            p.ring(route[t+4], 3.1, 1, FRAME, axis, 1.7)
        if lane in (0, 5, 10):
            paths.append(route[::20].round(3).tolist())
    for u in (-22.5, 22.5):
        angle = np.linspace(0, 4*math.pi, 2800)
        route = np.c_[side*(171+(80+u*np.cos(angle/2))*np.cos(angle)),
                      164+62*np.sin(angle)+u*np.sin(angle/2),
                      10+(228+u*np.cos(angle/2))*np.sin(angle)]
        solid_route(p, route, 1.5, FRAME)
    p.metadata['flow_paths'] = paths
    return p.finish()


def guide_blades(side):
    name = 'left' if side < 0 else 'right'
    p = Part(f'wing_{name}_guide_vanes', f'{"左" if side < 0 else "右"}翼倾斜导流百叶与冷凝桁架',
             source='一·2、三：倾斜导流叶片、格栅、冷凝管道帧外壳')
    for index in range(24):
        theta = 2*math.pi*index/24
        x0, z0 = 171+76*math.cos(theta), 10+213*math.sin(theta)
        y0 = 164+62*math.sin(theta)
        inward = np.array([-math.cos(theta), -.2, -math.sin(theta)])
        along = np.array([-math.sin(theta), .35, math.cos(theta)])
        center = np.array([x0, y0, z0])
        vertices = [center+inward*u+along*v+[0, h, 0]
                    for u in (-6, 6) for v in (-13, 13) for h in (-1, 1)]
        vertices = np.asarray(vertices)
        vertices[:, 0] *= side
        p.hull(vertices, IMPELLER)
        edge_a = center+inward*6-along*13+[0, 2, 0]
        edge_b = center+inward*6+along*13+[0, 2, 0]
        edge_a[0] *= side
        edge_b[0] *= side
        p.beam(edge_a, edge_b, .8, ARMOR)
    for z0 in TOWER_Z:
        for dx in (-30, 30):
            root = np.array([side*(175+dx), 45, z0])
            top = np.array([side*(175+dx), 71, z0+8])
            p.beam(root, top, 2.7, FRAME, 1.3)
            p.beam(root+[side*8, 0, 0], top+[side*8, 0, 0], 1.4, FRAME)
            for t in (0, .33, .66):
                a, b = root*(1-t)+top*t, root*(1-t-.33)+top*(t+.33)
                p.beam(a, b+[side*8, 0, 0], 1, ARMOR)
    return p.finish()


def tower(side, index):
    name = 'left' if side < 0 else 'right'
    x, z = side*175, TOWER_Z[index]
    p = Part(f'wing_{name}_vortex_tower_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}座直径90贯通涡流副塔',
             source='二·3：每侧3座直径90的上下贯通垂直涡流副塔',
             effect=dict(kind='vortex_tower', center=[x, 132, z], bottom=58, top=210, radius=34),
             diameter=90, open_ends=True)
    for y in (64, 204):
        p.ring([x, y, z], 45, 7, SHELL, depth=12)
        p.ring([x, y+5, z], 45, 3, ARMOR, depth=2)
        p.ring([x, y+6, z], 39, 1.5, COIL, depth=1)
    for y in (99, 132, 168):
        p.ring([x, y, z], 43, 2, FRAME, depth=3)
    for angle in np.arange(8)*math.pi/4:
        dx, dz = 42*math.cos(angle), 42*math.sin(angle)
        p.beam([x+dx, 66, z+dz], [x+dx, 201, z+dz], 2.2, FRAME)
        for y in (71, 113, 155):
            next_angle = angle+math.pi/4
            p.beam([x+dx, y, z+dz], [x+42*math.cos(next_angle), y+35, z+42*math.sin(next_angle)], .9, FRAME)
    return p.finish()


def lift_rotor(side, index):
    name = 'left' if side < 0 else 'right'
    x, z = side*175, TOWER_Z[index]
    p = Part(f'wing_{name}_lift_rotor_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}座涡流副塔叶轮',
             source='三：机翼上的6个垂直升力风扇',
             motion=dict(kind='turbine', pivot=[x, 128, z], axis=[0, 1, 0], sign=side*(-1)**index),
             blade_count=10)
    zz, xx = np.mgrid[-38:39, -38:39]
    radius = np.sqrt(xx*xx+zz*zz)
    angle = np.arctan2(zz, xx)
    phase = (angle-.012*radius) % (math.pi/5)
    blade = (radius >= 9) & (radius <= 38) & (phase < .34)
    for y in range(126, 131):
        p.points(np.c_[xx[blade]+x, np.full(blade.sum(), y), zz[blade]+z], IMPELLER)
        edge = blade & (phase < .04)
        p.points(np.c_[xx[edge]+x, np.full(edge.sum(), y), zz[edge]+z], ARMOR)
    p.ring([x, 128, z], 10, 6, ARMOR, depth=8)
    p.ring([x, 132, z], 7, 4, COIL, depth=1)
    return p.finish()


def vortex(side, index):
    name = 'left' if side < 0 else 'right'
    x, z = side*175, TOWER_Z[index]
    p = Part(f'wing_{name}_vortex_column_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}座发光龙卷风柱',
             source='二·3：副塔内部由发光青色方块构成龙卷风柱',
             motion=dict(kind='vortex', pivot=[x, 132, z], axis=[0, 1, 0], sign=side))
    y = np.linspace(60, 208, 700)
    radius = 8+23*((y-60)/148)**1.4
    angle = (y-60)/148*math.pi*7
    for phase in (0, math.pi):
        route = np.c_[x+radius*np.cos(angle+phase), y, z+radius*np.sin(angle+phase)]
        solid_route(p, route, 1.5, COIL)
    return p.finish()


def blade(side):
    name = 'left' if side < 0 else 'right'
    p = Part(f'wing_{name}_tip_blade', f'{"左" if side < 0 else "右"}翼200格高内向电容弧刃',
             source='二·3：X=±277最外缘、200格高弧形内刃电容阵列',
             outermost_x=side*277, height=200, inward=[-side, 0, 0],
             effect=dict(kind='lightning', origin=[side*249, 190, 183], target=[0, 160, 0]))
    z, x = np.mgrid[65:203, 247:278]
    for y in range(90, 290):
        t = (y-90)/199
        width = 1+28*math.sin(math.pi*t)
        middle_z = 95+88*math.sin(math.pi*t)+.2*(y-190)
        thickness = 1+11*math.sin(math.pi*t)
        mask = (x >= 277-width) & (abs(z-middle_z) <= thickness/2)
        p.points(np.c_[side*x[mask], np.full(mask.sum(), y), z[mask]], ARMOR)
        back = mask & (x >= 273)
        p.points(np.c_[side*x[back], np.full(back.sum(), y), z[back]], SHELL)
        edge = mask & (x <= 279-width)
        p.points(np.c_[side*x[edge], np.full(edge.sum(), y), z[edge]], COIL)
        if y % 15 in (0, 1):
            p.points(np.c_[side*x[mask], np.full(mask.sum(), y), z[mask]], FRAME)
    return p.finish()


def crown(index):
    radius, tilt, azimuth = [(130, 12, 0), (90, 18, 120), (50, 28, 240)][index]
    tilt, azimuth = math.radians(tilt), math.radians(azimuth)
    normal = np.array([math.sin(tilt)*math.cos(azimuth), math.cos(tilt), math.sin(tilt)*math.sin(azimuth)])
    center = np.array([0, 290, 0], float)
    u = np.cross(normal, [0, 0, 1])
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    p = Part(f'crown_{index+1}', ['外径260倾斜机械王冠环', '中径180倾斜机械王冠环', '内径100倾斜机械王冠环'][index],
             source='二·4：三层同心、不共面倾斜机械圆环，白金/淡青/紫晶点缀',
             diameter=radius*2, motion=dict(kind='crown', pivot=center.tolist(), axis=normal.tolist()),
             accents=[])
    p.ring(center, radius, 6, ARMOR, normal, 5)
    p.ring(center, radius-6, 2, FRAME, normal, 3)
    p.ring(center, radius-2, 1.5, COIL, normal, 5.2)
    for angle in np.arange(24)*math.pi/12:
        radial = math.cos(angle)*u+math.sin(angle)*v
        p.beam(center+radial*(radius-7.5), center+radial*(radius-.5), 1.2, FRAME)
    for angle in np.arange(8)*math.pi/4:
        anchor = center+(radius-3)*(math.cos(angle)*u+math.sin(angle)*v)
        p.metadata['accents'].append(dict(center=anchor.round(3).tolist(), radius=2.2, color='#b7a0e4'))
    return p.finish()


def build():
    parts = []
    for side in (-1, 1):
        parts.extend(beam(side, index) for index in range(6))
        parts.extend([mobius(side), guide_blades(side)])
        for index in range(3):
            parts.extend([tower(side, index), lift_rotor(side, index), vortex(side, index)])
        parts.append(blade(side))
    parts.extend(crown(index) for index in range(3))
    interpretations = [
        dict(section='二·3 双翼骨架', source_missing='主梁曲线控制点、壁厚与根尖位置未给出',
             preview_sampling='左右镜像；6根/侧根部X=±67，尖部X=±270，外半径7、内半径4.2；根Z='+str(ROOT_Z)+'，尖Z='+str(TIP_Z)+'；最高梁尖中心Y283，外壁到Y290。'),
        dict(section='二·3 莫比乌斯环流网', source_missing='管网条数、半扭转方向、流线与粗细未给出',
             preview_sampling='每翼中心(±171,164,10)，平面主半径80/228；11条中心偏距0..20的半扭转流体管；中心管绕一周、其余双绕行闭合；双缘银白框线，逐段桁架卡箍。'),
        dict(section='一·2 倾斜导流叶片', source_missing='叶片数量、尺寸及位置未给出',
             preview_sampling='每翼莫比乌斯内缘按24等分放置倾斜暗青百叶，冷凝桁架从基座Y45接向机翼。'),
        dict(section='二·3 六座副塔', source_missing='副塔中心、塔高、支架与叶数未给出',
             preview_sampling='中心X=±175，Z=-170/10/190；上下贯通外径90，外壳Y58..210，10片副塔叶轮轴心Y128；青色双螺旋风柱Y60..208。'),
        dict(section='二·3 翼尖刀刃', source_missing='刀刃的Y区间、Z轮廓、厚度未给出',
             preview_sampling='外缘X=±277；Y90..289共200整数层；内刃向中央，Z方向以正弦弧线成形，不更改翼宽。'),
        dict(section='二·4 三环王冠', source_missing='共心高度、倾角、方位、环截面与紫晶间距未给出',
             preview_sampling='三环共同中心(0,290,0)，外/中/内半径130/90/50；倾角12°/18°/28°，倾斜方位0°/120°/240°；白金环宽6、厚5，每环8处紫晶表面渲染点缀；相交保留。'),
        dict(section='二·3 构件相交', source_missing='双翼、主梁、管网、副塔的精确避让关系未给出',
             preview_sampling='各构件独立保存；主梁、管网与副塔依上述取样参数产生的重合不通过移位或删除解决，交给主预览报告。')
    ]
    return parts, interpretations
