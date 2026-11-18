import math

import numpy as np

from author_w05_shapes_20261115 import (
    Part, SHELL, ARMOR, GLASS, IMPELLER, COIL, CORE, FRAME, bezier, trace,
)


def base():
    p = Part('base_octagon', '零熵边界层八角阶梯基盘', source='二·1', nominal_xz=[480, 680], y=[0, 45])
    z, x = np.mgrid[-340:341, -240:241]
    edge = np.minimum.reduce([240-abs(x), 340-abs(z), (520-abs(x)-abs(z))/1.41421356])
    well = np.maximum(abs(x)/80, abs(z)/100)
    for y in range(46):
        inset = 0 if y <= 12 else 10 if y <= 23 else 21 if y <= 34 else 32
        rim = (edge >= inset) & (edge <= inset+11)
        deck = (edge >= inset) if y <= 7 or y in (10, 11, 12) else rim
        if 13 <= y <= 45:
            deck |= (edge >= inset) & (edge <= inset+32) & ((x//12+z//12)%5 == 0)
        deck &= well > 1
        state = np.full(x.shape, SHELL, np.uint8)
        if y in (7, 12, 23, 34, 45):
            state[(edge >= inset) & (edge <= inset+2)] = ARMOR
        if y in (5, 21, 32, 43):
            state[(edge >= inset) & (edge <= inset+1)] = COIL
        if y in (11, 12):
            state[((abs(x)%40 <= 1) | (abs(z)%48 <= 1)) & (edge > inset+18)] = FRAME
        if 13 <= y <= 45:
            state[(x//12+z//12)%5 == 0] = IMPELLER
        for value in np.unique(state[deck]):
            mask = deck & (state == value)
            p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], value)
    return p.finish()


def bearing_arm(sx, sz):
    p = Part(f'anchor_arm_{sx:+d}_{sz:+d}', '对角承重巨臂与高密度流体管', source='二·1·四条对角承重巨臂')
    path = np.array([[sx*205, 13, sz*300], [sx*171, 17, sz*257],
                     [sx*118, 31, sz*152], [sx*88, 35, sz*111]])
    route = np.array([bezier(path, t) for t in np.linspace(0, 1, 23)])
    trace(p, route, 10, SHELL, inner=7)
    normal = np.array([sz*.84, 0, -sx*.54])
    for shift in np.arange(-7, 8, 2):
        trace(p, route+normal*shift+[0, 5, 0], .75, GLASS if shift%4 else COIL)
    for t in np.linspace(.04, .96, 10):
        point = bezier(path, t)
        p.beam(point-normal*11+[0, 7, 0], point+normal*11+[0, 7, 0], 1.5, FRAME)
    p.box([sx*205-16, 0, sz*300-18], [sx*205+16, 8, sz*300+18], SHELL)
    return p.finish()


def exhaust_well():
    p = Part('negative_pressure_well', '负压漏斗井·防爆玻璃与液态风能', source='二·1·底部负压排风井', opening_xz=[[-80, 80], [-100, 100]])
    z, x = np.mgrid[-100:101, -80:81]
    for y in range(1, 41):
        rx = 32+(80-32)*(y/40)
        rz = 42+(100-42)*(y/40)
        radial = np.maximum(abs(x)/rx, abs(z)/rz)
        wall = (radial <= 1) & (radial >= .94)
        p.points(np.c_[x[wall], np.full(wall.sum(), y), z[wall]], ARMOR if y%10 == 0 else SHELL)
        grate = (radial <= .94) & ((x%16 == 0) | (z%20 == 0))
        if y in (10, 20, 30):
            p.points(np.c_[x[grate], np.full(grate.sum(), y), z[grate]], FRAME)
    mask = (abs(x) <= 78) & (abs(z) <= 98)
    p.points(np.c_[x[mask], np.full(mask.sum(), 40), z[mask]], GLASS)
    for y in range(2, 7):
        plasma = (x/31)**2+(z/41)**2 <= 1
        p.points(np.c_[x[plasma], np.full(plasma.sum(), y), z[plasma]], COIL)
    return p.finish()


def interfaces():
    ports = []
    p = Part('front_interfaces', '前方主控与对称检修接口区', source='二·1·接口区', controller=[0, 12, -345],
             conflict='主控Z=-345；480×680底座前沿Z=-340，保留原文悬出关系。')
    p.box([-6, 6, -344], [6, 18, -339], SHELL)
    p.box([-4, 8, -345], [4, 16, -345], ARMOR)
    p.box([-2, 10, -345], [2, 14, -345], IMPELLER)
    p.points([[0, 12, -345]], COIL)
    labels = ['输入总线', '输出总线', '超维流体输入仓', 'MAX+激光源仓']
    for side in (-1, 1):
        p.box([side*36, 10, -345], [side*177, 12, -314], SHELL)
        for z in (-344, -315):
            p.box([side*36, 12, z], [side*177, 12, z], FRAME)
        for i, cx in enumerate((54, 90, 126, 162)):
            x = side*cx
            p.box([x-7, 13, -341], [x+7, 25, -329], SHELL)
            p.box([x-6, 14, -342], [x+6, 24, -342], ARMOR)
            p.box([x-4, 16, -343], [x+4, 22, -343], GLASS if i == 2 else IMPELLER)
            if i == 3:
                p.ring([x, 19, -344], 4, 1.5, COIL, (0, 0, 1), 1)
            if i == 2:
                p.box([x-1, 16, -344], [x+1, 21, -344], COIL)
            if i < 2:
                for xx in (-2, 2):
                    p.box([x+xx, 17, -344], [x+xx, 21, -344], FRAME)
            ports.append(dict(label=labels[i], pos=[x, 19, -344], preview_only=True))
    p.metadata['ports'] = ports
    return p.finish()


def intake():
    p = Part('laval_intake', '吞星进气喇叭口与超导外壁', source='二·2·前段', z=[-350, -120], nominal_diameters=[180, 120])
    yy, xx = np.mgrid[65:256, -95:96]
    dy = yy-160
    radius = np.hypot(xx, dy)
    angle = np.arctan2(dy, xx)
    for z in range(-350, -119):
        t = (z+350)/230
        outer = 60+30*(1-t)**1.7
        wall = (radius <= outer) & (radius >= outer-4)
        material = np.full(xx.shape, SHELL, np.uint8)
        seam = np.cos(angle*12) > .965
        window = (np.cos(angle*8) > .5) & (-319 < z < -139)
        material[window] = GLASS
        material[seam] = FRAME
        if z in (-350, -349, -348, -281, -280, -279, -221, -220, -219, -122, -121, -120):
            material[:] = ARMOR
        if z in (-346, -315, -275, -215, -169, -124):
            material[:] = COIL
        for value in np.unique(material[wall]):
            mask = wall & (material == value)
            p.points(np.c_[xx[mask], yy[mask], np.full(mask.sum(), z)], value)
    p.beam([0, 160, -338], [0, 160, -123], 3, FRAME)
    return p.finish()


def turbine(index, z):
    p = Part(f'intake_turbine_{index+1}', f'第{index+1}组同轴反转涡轮·直径100', source='二·2·前段·3组涡轮',
             motion=dict(kind='turbine', pivot=[0, 160, z], axis=[0, 0, 1], sign=1 if index%2 == 0 else -1),
             nominal_diameter=100, blade_count=12)
    y, x = np.mgrid[110:211, -50:51]
    r = np.hypot(x, y-160)
    theta = np.arctan2(y-160, x)
    for depth in range(-4, 5):
        phase = (theta+.016*r+.015*depth)*12
        blade = (r >= 9) & (r <= 47) & (np.cos(phase) >= .72)
        edge = blade & ((np.cos(phase) < .84) | (r > 43))
        state = np.where(edge, ARMOR, GLASS)
        state[(r < 18) & blade] = IMPELLER
        for value in (GLASS, ARMOR, IMPELLER):
            mask = blade & (state == value)
            p.points(np.c_[x[mask], y[mask], np.full(mask.sum(), z+depth)], value)
    p.ring([0, 160, z], 50, 3, IMPELLER, (0, 0, 1), 8)
    p.ring([0, 160, z-5], 49, 1.5, ARMOR, (0, 0, 1), 1)
    p.ring([0, 160, z-6], 11, 2, COIL, (0, 0, 1), 2)
    p.sphere([0, 160, z], 9, ARMOR)
    return p.finish()


def constraint_rail(index):
    a = index*math.tau/8
    p = Part(f'constraint_rail_{index+1:02d}', f'第{index+1}根超导磁场约束轨', source='二·2·中段·8根约束轨', z=[-120, 120])
    samples = np.linspace(0, 1, 41)
    radius = 61+19*np.sin(math.pi*samples)**2
    phase = a+.12*np.sin(math.tau*samples)
    route = np.c_[radius*np.cos(phase), 160+radius*np.sin(phase), -120+240*samples]
    trace(p, route, 5.5, SHELL, inner=3)
    trace(p, route, 2.2, COIL)
    offset = np.array([math.cos(a), math.sin(a), 0])
    trace(p, route+offset*4.5, 1.2, ARMOR)
    for i in (0, 8, 16, 24, 32, 40):
        p.ring(route[i], 7, 2, FRAME, (0, 0, 1), 3)
    return p.finish()


def singularity():
    p = Part('herren_core', '直径50·风之律者核心多面体', source='二·2·中段·核心', nominal_center=[0, 160, 0], nominal_diameter=50,
             motion=dict(kind='core', pivot=[0, 160, 0]))
    vertices = [[25*s, 160, 0] for s in (-1, 1)]+[[0, 160+25*s, 0] for s in (-1, 1)]+[[0, 160, 25*s] for s in (-1, 1)]
    vertices += [[x*14.4, 160+y*14.4, z*14.4] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    p.hull(vertices, CORE)
    p.sphere([0, 160, 0], 17, COIL)
    return p.finish()


def gyroscope(index):
    radius = (39, 54)[index]
    normal = np.array(((.30, .70, .648), (-.75, .42, .51))[index])
    normal /= np.linalg.norm(normal)
    u = np.cross(normal, [0, 1, 0])
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    center = np.array([0, 160, 0])
    p = Part(f'core_gyroscope_{index+1}', f'核心第{index+1}层镂空机械陀螺环', source='二·2·中段·两层陀螺仪',
             motion=dict(kind='gyro', pivot=[0, 160, 0], axis=[0, 1, 0] if index == 0 else [1, 0, 0], sign=1 if index == 0 else -1))
    p.ring(center, radius, 4, ARMOR, normal, 4)
    p.ring(center, radius-1, 1, COIL, normal, 5)
    for a in np.arange(12)*math.tau/12:
        q = center+(u*math.cos(a)+v*math.sin(a))*(radius-2)
        p.sphere(q, 2.3, FRAME)
    return p.finish()


def tail_petal(index):
    p = Part(f'tail_petal_{index+1:02d}', f'第{index+1}片200格流线装甲瓣膜', source='二·2·后段·12片装甲瓣膜',
             nominal_axial_length=200, z=[120, 320])
    y, x = np.mgrid[98:223, -62:63]
    radius = np.hypot(x, y-160)
    angle = np.arctan2(y-160, x)
    middle = index*math.tau/12
    angular = np.angle(np.exp(1j*(angle-middle)))
    for z in range(120, 321):
        t = (z-120)/200
        outer = 60-26*math.sin(math.pi*t)
        mask = (radius <= outer) & (radius >= outer-4) & (abs(angular) <= math.radians(13.3))
        material = np.full(x.shape, ARMOR, np.uint8)
        material[(abs(angular) > math.radians(10)) | (radius < outer-2.5)] = SHELL
        material[abs(angular) < math.radians(1.1)] = COIL
        if z%25 in (0, 1, 2):
            material[(abs(angular) > math.radians(3)) & (abs(angular) < math.radians(9))] = IMPELLER
        for value in np.unique(material[mask]):
            selected = mask & (material == value)
            p.points(np.c_[x[selected], y[selected], np.full(selected.sum(), z)], value)
    return p.finish()


def tail_feather(index):
    a = index*math.tau/12
    p = Part(f'tail_feather_{index+1:02d}', f'第{index+1}列青色机械尾羽', source='二·2·后段·机械羽毛阵列', z=[316, 350])
    radial = np.array([math.cos(a), math.sin(a), 0])
    tangent = np.array([-math.sin(a), math.cos(a), 0])
    base = np.array([0, 160, 318])+radial*58
    tip = np.array([0, 160, 350])+radial*75
    p.hull([base+tangent*7-radial*2, base-tangent*7-radial*2,
            base+tangent*7+radial*3, base-tangent*7+radial*3,
            tip-radial*1.2, tip+radial*1.2], ARMOR)
    p.beam(base+radial*3, tip-[0, 0, 1], 1, COIL)
    for fraction in (.25, .48, .70):
        q = base*(1-fraction)+tip*fraction
        width = 5*(1-fraction)
        p.beam(q-tangent*width+radial*3, q+tangent*width+radial*3, .7, IMPELLER)
    return p.finish()


def build():
    parts = [base()]
    parts += [bearing_arm(sx, sz) for sx in (-1, 1) for sz in (-1, 1)]
    parts += [exhaust_well(), interfaces(), intake()]
    parts += [turbine(i, z) for i, z in enumerate((-310, -245, -180))]
    parts += [constraint_rail(i) for i in range(8)]
    parts += [singularity(), gyroscope(0), gyroscope(1)]
    parts += [tail_petal(i) for i in range(12)]
    parts += [tail_feather(i) for i in range(12)]
    interpretations = [
        dict(item='整数格采样', value='原文坐标作格点中心采样，含两端；480×680按X±240、Z±340连续跨度保留，离散包围盒为481×681。直径与长度同理，不裁去端点。'),
        dict(item='底座高度冲突', value='总述高40，精确分区Y0～45；按明确分区呈现到Y45。阶梯层位取0～12、13～23、24～34、35～45，原文未列这些细层。'),
        dict(item='前主控与底座冲突', value='主控保持(0,12,-345)，底座前沿Z=-340；前检修廊道延到Z=-345，底座不扩大，接口仅视觉示意。'),
        dict(item='排风井', value='上开口保持X±80、Z±100；原文未给深度与漏斗下口，取Y1～40、下口约64×84，防爆玻璃Y40、等离子Y2～6。'),
        dict(item='轴线高度', value='原文仅给核心中心Y160，前后喷管与同轴涡轮据此保持同轴Y160。'),
        dict(item='进气口越界', value='180直径口径保持，连续轮廓X±90、Y70～250，超过中轴分区X±60与Y240；未缩小。'),
        dict(item='三组涡轮取样', value='原文未给Z位置、叶数与扭转角；取Z=-310/-245/-180，每组12叶，直径100；相邻反转。'),
        dict(item='八根轨道取样', value='原文未给轨道曲线；八等分环绕，半径61～80，Z=-120～120，5.5半径空心轨壳。中段无连续管壁。'),
        dict(item='核心外环取样', value='原文未给两层陀螺环直径/倾角；半径39/54，法线(0.30,0.70,0.648)、(-0.75,0.42,0.51)，中心均(0,160,0)。核心以六轴25及八角14.4的多面体采样。'),
        dict(item='尾段长度空缺', value='后段Z120～350长230，但每片装甲瓣长200；瓣膜取Z120～320保留200轴向跨度，Z318～350为尾羽，未加长或缩短瓣膜。瓣半径60→34→60。'),
        dict(item='尾羽取样', value='原文未给羽片数和张开半径；按12片瓣膜各接一列尾羽，尾端Z350、张开半径75。'),
        dict(item='材质实施', value='仅用原文七类预览专用材质；CORE只用于中心50直径多面体，井内等离子与管内发光用COIL槽位表达。没有注册或替换游戏方块。'),
    ]
    return parts, interpretations
