# -*- coding: utf-8 -*-
"""Gemini重装小兔十二翼船坞原案：完整坐标生成，冲突保留并记录。"""
import math
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from i42_prefabrication_geometry_v1_20261028 import Material

ROOT = Path(__file__).resolve().parents[2]
M = Material()
WHITE, BLACK = 'minecraft:quartz_block', 'minecraft:black_concrete'
CYAN, GLASS = 'minecraft:cyan_concrete', 'minecraft:cyan_stained_glass'
VIOLET = 'minecraft:purple_stained_glass'
COIL = 'gtceu:superconducting_coil[active=false]'
STATES = sorted({WHITE, BLACK, CYAN, GLASS, VIOLET, COIL, M.ATOMIC, M.GOLD, M.STRESS,
                 M.STEEL_PIPE, M.VENT, M.TURBINE, M.GRATE, M.LIGHT, M.CONTROL, M.PORT})
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {s: 'Gemini原案的实体构件；使用增强版3.0已有真实材质，不代表新材质已注册' for s in STATES}
ROLES.update({WHITE: '逆熵白陶瓷装甲的现有石英替代', BLACK: '深渊钛黑装甲的现有黑混凝土替代',
              M.ATOMIC: '内部黑色金属骨架', M.GOLD: '暗金框架的现有金块替代，颜色以真实贴图为准',
              CYAN: '理构造光路实体色带', GLASS: '逻辑玻璃与物质打印瀑布的静态实体',
              VIOLET: '量子紫观察窗', M.LIGHT: '实际发光的海晶灯与光路节点',
              COIL: '可见格雷超导线圈', M.CONTROL: '南侧胸甲平台Y32主控占位',
              M.PORT: '八处通用接口，不限定输入输出或仓型'})
CORE = np.array([324., 140., 246.])


class Part:
    def __init__(self, name):
        self.name, self.chunks, self.values = name, [], []

    def points(self, points, state):
        p = np.rint(points).astype(np.int32).reshape(-1, 3)
        if not len(p): return
        assert np.all(np.abs(p) < 2048), '坐标编码边界，仅报错，不裁切'
        self.chunks.append(p)
        self.values.append(np.full(len(p), IDS[state], np.uint8))

    def box(self, low, high, state):
        low, high = np.rint(low).astype(int), np.rint(high).astype(int)
        assert np.all(high >= low)
        p = np.indices(tuple(high - low + 1), dtype=np.int32).reshape(3, -1).T + low
        self.points(p, state)

    def beam(self, start, end, radius, state):
        a, b = np.array(start, float), np.array(end, float)
        v = b - a
        length = np.linalg.norm(v)
        if length < .01: return self.sphere(a, radius, state)
        v /= length
        ref = [0, 1, 0] if abs(v[1]) < .9 else [0, 0, 1]
        u = np.cross(v, ref); u /= np.linalg.norm(u)
        w = np.cross(v, u)
        q = np.arange(-math.ceil(radius), math.ceil(radius) + 1)
        x, y = np.meshgrid(q, q, indexing='ij')
        mask = x * x + y * y <= radius * radius
        cross = x[mask, None] * u + y[mask, None] * w
        t = np.linspace(0, length, max(2, math.ceil(length * 1.7) + 1))
        self.points((a + t[:, None, None] * v + cross).reshape(-1, 3), state)

    def sphere(self, center, radius, state, hollow=False):
        q = np.arange(-math.ceil(radius), math.ceil(radius) + 1)
        p = np.array(np.meshgrid(q, q, q, indexing='ij')).reshape(3, -1).T
        r = (p * p).sum(1)
        mask = r <= radius * radius
        if hollow: mask &= r >= (radius - 2) ** 2
        self.points(p[mask] + center, state)

    def finish(self):
        p, states = np.concatenate(self.chunks), np.concatenate(self.values)
        keys = encode(p)
        _, reverse = np.unique(keys[::-1], return_index=True)
        selected = len(keys) - 1 - reverse
        self.p, self.states = p[selected], states[selected]
        self.chunks.clear(); self.values.clear()
        return self


def encode(p):
    q = p.astype(np.int64) + 2048
    return (q[:, 1] * 4096 + q[:, 2]) * 4096 + q[:, 0]


def ring(part, center, radius, radial_half, axial_half, tilt_x=0, tilt_z=0, glass=False):
    x, z = math.radians(tilt_x), math.radians(tilt_z)
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    rotation = rz @ rx
    theta = np.linspace(0, 2 * math.pi, math.ceil(2 * math.pi * radius * 1.8) + 1)
    radial = np.c_[np.cos(theta), np.zeros(len(theta)), np.sin(theta)] @ rotation.T
    normal = rotation @ [0, 1, 0]
    for r in np.arange(-radial_half, radial_half + .1, 1):
        for h in np.arange(-axial_half, axial_half + .1, 1):
            shell = abs(r) >= radial_half - 1 or abs(h) >= axial_half - 1
            if not shell and not glass: continue
            state = GLASS if glass else WHITE
            if abs(r) >= radial_half - 1 and abs(h) >= axial_half - 1: state = M.GOLD
            elif abs(h) < 1: state = CYAN
            part.points(center + (radius + r) * radial + h * normal, state)
    return rotation


def base():
    p = Part('base')
    z, x = np.mgrid[0:493, 0:649]
    X, Z = x - 324, z - 246
    for y in range(66):
        inset = y // 16 * 3
        a, b = 324 - inset, 246 - inset
        shape = (np.abs(X) <= a) & (np.abs(Z) <= b) & (np.abs(X) + np.abs(Z) <= a + b - 72)
        inside = (np.abs(X) < a - 4) & (np.abs(Z) < b - 4) & (np.abs(X) + np.abs(Z) < a + b - 79)
        shell = shape & (~inside | (y <= 3) | (y >= 61))
        channel = (np.abs(X) <= 22) | (np.abs(Z) <= 22)
        if y > 35: shell &= ~channel
        p.points(np.c_[x[shell], np.full(shell.sum(), y), z[shell]], BLACK if y % 16 else M.STRESS)
        if y in (34, 35):
            m = shape & channel
            p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], M.LIGHT if y == 34 else GLASS)
        if y == 65:
            stripes = shell & (((x // 24) % 5 == 0) | ((z // 24) % 5 == 0))
            p.points(np.c_[x[stripes], np.full(stripes.sum(), y), z[stripes]], WHITE)
    for axis in (0, 2):
        for side in (-13, 13):
            a, b = [0, 39, 246], [648, 39, 246]
            if axis == 2: a, b = [324, 39, 0], [324, 39, 492]
            a[2 if axis == 0 else 0] += side; b[2 if axis == 0 else 0] += side
            p.beam(a, b, 2, M.STEEL_PIPE)
    bridges = []
    for axis, maximum, center in [(0, 648, 324), (2, 492, 246)]:
        for value in range(20, maximum, 20):
            if abs(value - center) < 34: continue
            for t in range(-26, 27):
                at = [value, 65 + round(8 * (1 - (t / 26) ** 2)), 246 + t]
                if axis == 2: at = [324 + t, at[1], value]
                p.box(np.array(at) - [1, 0, 1], np.array(at) + [1, 1, 1], M.GOLD)
            if axis == 0: p.box([value-1,65,220],[value+1,65,272],M.GRATE)
            else: p.box([298,65,value-1],[350,65,value+1],M.GRATE)
            bridges.append(dict(axis='X' if axis == 0 else 'Z', coordinate=value, spacing=20))
    polygon = [(72, 0), (576, 0), (648, 72), (648, 420), (576, 492), (72, 492), (0, 420), (0, 72)]
    perimeter = np.array(polygon + [polygon[0]], float)
    pillars = []
    for a, b in zip(perimeter[:-1], perimeter[1:]):
        length = np.linalg.norm(b - a)
        for distance in np.arange(0, length, 32):
            x0, z0 = np.rint(a + (b - a) * distance / length).astype(int)
            p.box([x0-7, 0, z0-7], [x0+7, 65, z0+7], M.ATOMIC)
            for y in (4, 22, 42, 60):
                for side in (-8, 8):
                    p.box([x0-8,y,z0+side],[x0+8,y+2,z0+side],M.GOLD if y != 42 else CYAN)
                    p.box([x0+side,y,z0-8],[x0+side,y+2,z0+8],M.GOLD if y != 42 else CYAN)
            pillars.append(dict(root=[int(x0),0,int(z0)], height=65, cross_section=[15,15]))
    return p.finish(), dict(bridges=bridges, pillars=pillars, depth=30, channel_width=45,
                            hull='八角形分块空心承台；四格底、顶和侧壁，不填满内部无用体积')


def cooling_tower(index, center):
    p = Part('tower:' + str(index)); cx, cz = center
    a = np.arange(-13,14); z,x = np.meshgrid(a,a,indexing='ij')
    r = np.maximum.reduce([np.abs(x), np.abs(.5*x+.8660254*z), np.abs(.5*x-.8660254*z)])
    for h in range(40):
        width = 10.825 - (2 if 6 < h < 29 else 0)
        mask = (r<=width)&((r>=width-2)|(h<3)|(h>36))
        p.points(np.c_[x[mask]+cx,np.full(mask.sum(),65+h),z[mask]+cz],WHITE if h%12<3 else M.TURBINE)
        window = mask & (np.abs(x)<3) & (h>7)&(h<30)
        p.points(np.c_[x[window]+cx,np.full(window.sum(),65+h),z[window]+cz],GLASS)
    p.box([cx-5,102,cz-5],[cx+5,104,cz+5],M.VENT)
    return p.finish()


def core():
    p=Part('core'); phi=(1+math.sqrt(5))/2
    vertices=[]
    for a in (-1,1):
        for b in (-phi,phi): vertices.extend([[0,a,b],[a,b,0],[b,0,a]])
    vertices=np.array(vertices,float); vertices/=np.linalg.norm(vertices[0])
    hull=ConvexHull(vertices)
    edges=sorted({tuple(sorted((int(f[i]),int(f[(i+1)%3])))) for f in hull.simplices for i in range(3)})
    assert len(vertices)==12 and len(hull.simplices)==20 and len(edges)==30
    for radius in (42.5,35):
        for a,b in edges:
            p.beam(CORE+vertices[a]*radius,CORE+vertices[b]*radius,1.7,M.GOLD)
        for vertex in vertices:p.sphere(CORE+vertex*radius,3,BLACK)
    p.sphere(CORE,22.5,M.LIGHT,True)
    q=np.arange(-23,24);xyz=np.array(np.meshgrid(q,q,q,indexing='ij')).reshape(3,-1).T
    r=np.linalg.norm(xyz,axis=1)
    mask=(r<=22.5)&(r>20.5)&((xyz[:,0]%9==0)|(xyz[:,1]%9==0)|(xyz[:,2]%9==0))
    p.points(CORE+xyz[mask],CYAN)
    p.sphere(CORE,12,VIOLET,True)
    return p.finish(),dict(center=CORE.tolist(),cage_diameter=85,cage_layers=2,vertices=12,faces=20,edges=30,logic_diameter=45)


def cannon(side):
    p=Part('cannon:'+str(side))
    for t in range(180):
        z=246+side*(55+t)
        for quadrant in range(4):
            theta=np.linspace(quadrant*math.pi/2+.16,(quadrant+1)*math.pi/2-.16,88)
            for depth in range(5):
                radius=1-depth*.035
                points=np.c_[324+32.5*radius*np.cos(theta),140+35*radius*np.sin(theta),np.full(len(theta),z)]
                p.points(points,WHITE if depth<3 else BLACK)
            if t%20<3:
                p.points(np.c_[324+33*np.cos(theta),140+35.5*np.sin(theta),np.full(len(theta),z)],M.GOLD)
        if t%12<3:
            for x in (-17,17):p.box([324+x-2,130,z],[324+x+2,150,z],COIL)
        for x in (-27,27):p.box([324+x-1,136,z],[324+x+1,144,z],M.ATOMIC)
    return p.finish()


def wing(side,index):
    p=Part(f'wing:{side}:{index}')
    angle=math.radians([-15,0,15,30,45,60][index])
    root=np.array([324+side*175,125+index*10,76+index*68],float)
    v=np.array([side*math.cos(angle),math.sin(angle),0])
    u=np.array([0,0,1]);w=np.cross(v,u)
    p.sphere(root,12,BLACK);p.sphere(root,10,M.GOLD,True)
    ss,nn=np.meshgrid(np.arange(-17,18),np.arange(-6,7),indexing='ij')
    for t in range(160):
        half=17*min(1,(160-t)/35)
        inside=np.abs(ss)<=half
        shell=inside&((np.abs(nn)>=4)|(np.abs(ss)>=half-1.5))
        position=root+v*t+w*(4*math.sin(math.pi*t/159))
        points=position+ss[shell,None]*u+nn[shell,None]*w
        p.points(points,WHITE)
        edge=shell&(np.abs(ss)>=half-1.5)&(np.abs(nn)>=4)
        p.points(position+ss[edge,None]*u+nn[edge,None]*w,M.GOLD)
        if t%16<3:
            mask=inside&(np.abs(nn)<=1)&(np.abs(ss)<=half-3)
            p.points(position+ss[mask,None]*u+nn[mask,None]*w,COIL)
        if t%12 in (0,6):
            for s in range(-12,13,6):p.beam(position+u*s-w*3,position+u*(s+3)+w*3,.7,GLASS)
    tip=root+159*v
    for y in range(round(tip[1])-45,round(tip[1])+1):
        radius=3.5
        q=np.arange(-4,5);xx,zz=np.meshgrid(q,q,indexing='ij');mask=xx*xx+zz*zz<=radius*radius
        p.points(np.c_[tip[0]+xx[mask],np.full(mask.sum(),y),tip[2]+zz[mask]],GLASS)
    product=tip+[0,-60,0]
    if index%3==0:
        ring(p,product,13,2,2)
        for i in range(12):
            th=i*math.pi/6;p.sphere(product+[15*math.cos(th),0,15*math.sin(th)],2,M.GOLD)
    elif index%3==1:
        for x in (-9,9):
            for y in (-9,9):p.beam(product+[x,y,-9],product+[x,y,9],1.4,M.ATOMIC)
        for y in (-9,9):
            for z in (-9,9):p.beam(product+[-9,y,z],product+[9,y,z],1.4,WHITE)
        p.sphere(product,6,CYAN)
    else:
        p.sphere(product,10,WHITE,True);ring(p,product,12,1,1,tilt_x=90,glass=True)
    return p.finish(),dict(side=side,index=index+1,length=160,width=35,thickness=12,
        angle_degrees=math.degrees(angle),root=root.tolist(),tip=tip.tolist(),waterfall_height=45,
        product_center=product.tolist(),product=['半成品齿轮环','戴森组件框架','反物质容器模型'][index%3])


def build():
    parts={};basepart,foundation=base();parts[basepart.name]=basepart
    towers=[]
    for sx in (-1,1):
        for sz in (-1,1):
            for ix,x in enumerate((70,128,186,244)):
                for iz,z in enumerate((55,103,151,199)):
                    center=[324+sx*x,246+sz*z];i=len(towers)+1
                    part=cooling_tower(i,center);parts[part.name]=part
                    towers.append(dict(id=i,center_xz=center,height=40,diameter=25,base_y=65))
    pipe=Part('coolant-network')
    for sx in (-1,1):
        for sz in (-1,1):
            for z in (55,103,151,199):
                pipe.beam([324+sx*70,69,246+sz*z],[324+sx*244,69,246+sz*z],2,M.STEEL_PIPE)
                pipe.beam([324+sx*70,72,246+sz*z+7],[324+sx*244,72,246+sz*z+7],1,CYAN)
            for x in (70,128,186,244):pipe.beam([324+sx*x,69,246+sz*55],[324+sx*x,69,246+sz*199],2,M.STEEL_PIPE)
    parts[pipe.name]=pipe.finish()
    part,coreinfo=core();parts[part.name]=part
    injection=Part('eight-compute-cables');cables=[]
    for i in range(8):
        th=(i+.5)*math.pi/4;v=np.array([math.cos(th),0,math.sin(th)])
        start=CORE+v*76+[0,-76,0];end=CORE+v*30+[0,-30,0]
        injection.beam(start,end,6,BLACK);injection.beam(start+[0,2,0],end+[0,2,0],1.5,CYAN)
        injection.sphere(start,8,M.GOLD,True);cables.append(dict(start=start.tolist(),end=end.tolist(),diameter=12,angle_degrees=45))
    parts[injection.name]=injection.finish()
    laser=Part('axial-laser-channel');laser.beam([324,140,0],[324,140,492],7.5,GLASS)
    laser.beam([324,140,0],[324,140,492],1.5,M.LIGHT);parts[laser.name]=laser.finish()
    for side in (-1,1):
        part=cannon(side);parts[part.name]=part
    arms=[];wings=[]
    for side in (-1,1):
        arm=Part('C-arm:'+str(side));theta=np.linspace(-math.pi/2,math.pi/2,600)
        line=np.c_[324+side*(175+55*np.cos(theta)),155+90*np.sin(theta),np.full(len(theta),246)]
        for a,b in zip(line[:-1:3],line[3::3]):arm.beam(a,b,6,M.ATOMIC)
        for i in range(6):
            part,info=wing(side,i);parts[part.name]=part;wings.append(info)
            joint=np.array(info['root']);nearest=line[np.argmin(np.linalg.norm(line-joint,axis=1))]
            arm.beam(nearest,joint,3,M.GOLD)
        parts[arm.name]=arm.finish();arms.append(dict(side=side,height=180,center_y=155))
    crown=[]
    for i,(radius,tx,tz,width,height) in enumerate([(190,0,0,7.5,10),(130,25,0,3,3),(70,0,-25,2,2)]):
        part=Part('crown:'+str(i));center=np.array([324.,250.,246.]);rotation=ring(part,center,radius,width,height,tx,tz,glass=i==2)
        if i==0:
            for j in range(32):
                th=j*math.pi/16;start=center+[radius*math.cos(th),-12,radius*math.sin(th)]
                direction=(CORE-start)/np.linalg.norm(CORE-start)
                part.beam(start,start+direction*9,3,BLACK);part.sphere(start+direction*10,2,CYAN)
        if i==1:
            for j in range(60):
                th=j*math.pi/30;at=center+np.array([122*math.cos(th),0,122*math.sin(th)])@rotation.T
                part.sphere(at,2,M.GOLD)
        if i==2:
            for phase in (0,math.pi):
                points=[center+np.array([58*math.cos(phase+j*2*math.pi/3),0,58*math.sin(phase+j*2*math.pi/3)])@rotation.T for j in range(3)]
                for a,b in zip(points,points[1:]+points[:1]):part.beam(a,b,1,M.LIGHT)
        parts[part.name]=part.finish();crown.append(dict(radius=radius,diameter=radius*2,center=center.tolist(),tilt_x_deg=tx,tilt_z_deg=tz,radial_half=width,axial_half=height))
    front=Part('south-command-platform')
    for z in range(484,521):
        half=36-round((z-484)*.3)
        front.box([324-half,24,z],[324+half,29,z],BLACK)
        front.box([324-half,30,z],[324-half+2,32,z],WHITE)
        front.box([324+half-2,30,z],[324+half,32,z],WHITE)
    x,y=np.mgrid[-25:26,-25:26]
    h=np.maximum.reduce([np.abs(x),np.abs(.5*x+.8660254*y),np.abs(.5*x-.8660254*y)])
    for z in (518,519,520):
        mask=h<=25;front.points(np.c_[324+x[mask],32+y[mask],np.full(mask.sum(),z)],BLACK if z<520 else GLASS)
        edge=mask&(h>=23);front.points(np.c_[324+x[edge],32+y[edge],np.full(edge.sum(),z)],WHITE)
    controller=[324,32,520];front.points([controller],M.CONTROL)
    ports=[]
    for y in (28,36):
        for x in (311,317,331,337):
            at=[x,y,520];front.points([at],M.PORT);ports.append(dict(id='通用接口'+str(len(ports)+1),pos=at,face='south'))
    parts[front.name]=front.finish()
    low=np.min([p.p.min(0) for p in parts.values()],axis=0);high=np.max([p.p.max(0) for p in parts.values()],axis=0)
    size=high-low+1;cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    assert len(parts)<256
    owner=np.zeros_like(cube);overlaps=[];bounds={}
    for index,part in enumerate(parts.values(),1):
        at=part.p-low;prior=owner[at[:,1],at[:,2],at[:,0]]
        for previous,count in zip(*np.unique(prior[prior>0],return_counts=True)):
            previous_name=list(parts)[previous-1]
            expected=((previous_name=='base' and part.name.startswith(('tower:','C-arm:','eight-compute','south-command'))) or
                      (previous_name.startswith('tower:') and part.name=='coolant-network') or
                      (previous_name.startswith('wing:') and part.name.startswith('C-arm:')) or
                      (previous_name=='core' and part.name=='axial-laser-channel'))
            overlaps.append(dict(first=previous_name,second=part.name,overlap_voxels=int(count),
                                 kind='设计接合' if expected else '待协调干涉',
                                 disposition='保持原几何，合成文件同格按生成顺序取后者；独立构件原坐标另存，未用移位或削减消冲突'))
        cube[at[:,1],at[:,2],at[:,0]]=part.states;owner[at[:,1],at[:,2],at[:,0]]=index
        bounds[part.name]=dict(min=part.p.min(0).tolist(),max=part.p.max(0).tolist(),blocks=len(part.p))
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    assert np.all(counts[1:]),[(s,int(n)) for s,n in zip(STATES,counts[1:]) if not n]
    log=ROOT/'logs/w02-bunny-dock-v3-20261108';log.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(log/'original-components.npz',**{n+'__p':p.p for n,p in parts.items()},**{n+'__s':p.states for n,p in parts.items()})
    np.savez_compressed(log/'final-geometry.npz',cube=cube)
    offset=-low
    conflicts=[dict(issue='原文称尺寸精确649×493×303，同时给出X=649、Z=493等含端点坐标；本版以中心324/246生成649×493基座，外围柱与南台可越界。',handling='名义尺寸仅作参考，保留完整实际边界。'),
               dict(issue='中环中心Y250、半径130、X倾25°时中心线顶高304.94，含装甲更高，与最高Y303冲突。',handling='保留直径260、倾角25°与中心Y250，不压扁或降低。'),
               dict(issue='160格翼长、+60°翼角与上层翼根高度共同超出Y260翼区，亦可超过总高303。',handling='保留完整六种角度与翼长；翼根位置为本版明确的坐标转译，待原作者复核。'),
               dict(issue='“每边6片”与“六对/十二翼”按12片执行；25格冷却塔按四象限各4×4共64座执行。',handling='保持可计数构件完整，不按规模指标增删。'),
               dict(issue='原案新材质、流体、Emissive、CTM、滚动公式与运行演出未提供实际注册资源。',handling='已有真实方块替代；玻璃是静态实体，不冒充动态流体或完整Shader。')]
    data=dict(key='w02',name='hk3gtl-w02-bunny-dock-v3-20261108',title='理之律者 · 万象·自律工业矩阵 · Gemini十二翼重构船坞 V3',
        candidate_version='V3-Gemini重装小兔十二翼船坞',size=size.tolist(),nominal_size_xyz=[649,303,493],
        blueprint_bounds_xyz=dict(min=low.tolist(),max=high.tolist()),blueprint_to_export_offset_xyz=offset.tolist(),
        controller=(np.array(controller)+offset).tolist(),controller_face='south',
        ports=[dict(v,pos=(np.array(v['pos'])+offset).tolist()) for v in ports],pipe_routes=[],paths=[],
        zones=[dict(name=n,pos=(np.array(p)+offset).tolist()) for n,p in [('万象重构奇点',[324,140,246]),('十二翼解析重构阵列',[149,200,246]),('三重真理星环',[324,250,246]),('南侧主控平台',[324,32,520])]],
        description='以重装小兔与真理武装解构为母题：四象限64座六角冷却塔、双层二十面体核心、双180格轨道炮、十二片160格浮游翼、三重冠冕。',
        purpose='按负责人提供Gemini新原案重建W02；原文参数保留，坐标缺省与冲突明确记录，未批准或部署。',
        foundation=foundation,towers=towers,core=coreinfo,cables=cables,cannons=dict(count=2,length=180,cross_section=[65,70],axis='Z'),
        wings=wings,arms=arms,crowns=crown,source_conflicts=conflicts,component_bounds_blueprint=bounds,component_overlaps=overlaps,
        coordinate_interpretation=dict(wing_roots='左右X149/499，Y125+10i，Z76+68i；六角-15/0/15/30/45/60，翼长160，原文无逐翼坐标。',
            base='Y0–65包端点；侧壳与顶底4格，交叉槽宽45、底Y35；空心承台属于体素转译。',
            crown='三环共心(324,250,246)；外环水平，中环绕X+25°，内环绕Z-25°。',
            palette='原作者幻想材质名映射现有方块；配比不作硬性计数约束。'),
        dynamic_effects=dict(implemented=False,requirements=['核心体素重构扫描与金色散光','三环反转与十二翼呼吸悬浮','翼尖至物流槽六角光束','周界30格全息公式幕'],
                             boundary='本轮为实体建筑原案预览，不以静态发光方块冒充已实现运行演出。'),
        motion_identity='W02理之律者；真理武装为外观参考，不改变角色实体、研究门槛或运行WSV职责。')
    return cube,data
