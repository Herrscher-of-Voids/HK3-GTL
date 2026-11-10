# -*- coding: utf-8 -*-
"""W02 Gemini新原案：完整构件先生成，实际边界后求，缺省转译公开。"""
import math
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull, distance_matrix
from w02_bunny_dock_geometry_v3_20261108 import Part, M, WHITE, BLACK, CYAN, GLASS, VIOLET, COIL, STATES, IDS, ring

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W02_Gemini_半构造星核船坞_V4_20261109'
LOG = ROOT / 'logs/w02-gemini-v4-20261109'
CORE = np.array([0., 148., 0.])
ROLES = {s: '增强版3.5实例现有资源的原案外观转译，非新增材质注册' for s in STATES}
ROLES.update({WHITE: '白瓷装甲', BLACK: '深黑承台', M.GOLD: '暗金框架的现有金块替代',
              GLASS: '静态青蓝逻辑玻璃', VIOLET: '量子紫构造体素', M.LIGHT: '真实海晶灯光路节点',
              M.CONTROL: '主控制器外观占位', M.PORT: '八处通用接口外观，不限定仓型'})


def foundation():
    p = Part('base')
    z, x = np.mgrid[-246:247, -324:325]
    channel = (np.abs(x) < 21) | (np.abs(z) < 21)
    wells = [(sx*150, sz*115) for sx in (-1, 1) for sz in (-1, 1)]
    wellmask = sum(((x-cx)**2+(z-cz)**2 <= 44**2).astype(int) for cx, cz in wells) > 0
    for y in range(59):
        inset = 3*(y//20)
        ax, az = 324-inset, 246-inset
        shape = (np.abs(x) <= ax) & (np.abs(z) <= az) & (np.abs(x)+np.abs(z) <= ax+az-72)
        inside = (np.abs(x) < ax-4) & (np.abs(z) < az-4) & (np.abs(x)+np.abs(z) < ax+az-79)
        mask = shape & (~inside | (y <= 3) | (y >= 55))
        mask &= ~((channel & (y > 30)) | (wellmask & (y > 34)))
        p.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], BLACK if y % 20 else M.STRESS)
        if y in (29, 30):
            m = shape & channel
            p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], M.LIGHT if y == 29 else GLASS)
        if y in (34, 35):
            for cx, cz in wells:
                r = np.sqrt((x-cx)**2+(z-cz)**2)
                m = (r <= 44) & (r >= 39 if y == 35 else r >= 0)
                state = BLACK if y == 34 else M.GOLD
                p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], state)
                if y == 34:
                    m = (r < 40) & ((r.astype(int) % 10) < 2)
                    p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], M.LIGHT)
        if y == 58:
            m = mask & ((np.abs(x) % 36 < 3) | (np.abs(z) % 36 < 3))
            p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], WHITE)
            m = mask & (np.abs(x)>270) & (np.abs(z)<80) & (z % 12<5)
            p.points(np.c_[x[m], np.full(m.sum(), y), z[m]], M.GRATE)
    polygon = [(-252,-246),(252,-246),(324,-174),(324,174),(252,246),(-252,246),(-324,174),(-324,-174)]
    perimeter = np.array(polygon + [polygon[0]], float)
    pillars = []
    for a, b in zip(perimeter[:-1], perimeter[1:]):
        length = np.linalg.norm(b-a)
        for t in np.arange(0, length, 36):
            cx, cz = np.rint(a+(b-a)*t/length).astype(int)
            if cz>230 and abs(cx)<52:continue
            p.box([cx-6,0,cz-6], [cx+7,58,cz+7], M.ATOMIC)
            for y in (6,27,48):
                for s in (-7,8):
                    p.box([cx-7,y,cz+s], [cx+8,y+2,cz+s], CYAN if y == 27 else M.GOLD)
                    p.box([cx+s,y,cz-7], [cx+s,y+2,cz+8], CYAN if y == 27 else M.GOLD)
            pillars.append([int(cx),0,int(cz)])
    bridges = []
    for axis, limit in [(0,324),(2,246)]:
        for t in range(-limit+28, limit, 28):
            if abs(t) < 35: continue
            for q in range(-21,22):
                at = [t,59+round(9*(1-(q/21)**2)),q] if axis == 0 else [q,59+round(9*(1-(q/21)**2)),t]
                p.box(np.array(at)-[1,0,1], np.array(at)+[1,1,1], M.GOLD)
            a,b = ([t-1,58,-21],[t+1,58,20]) if axis == 0 else ([-21,58,t-1],[20,58,t+1])
            p.box(a,b,GLASS)
            bridges.append(dict(axis=axis,coordinate=t))
    for axis in (0,2):
        for side in (-13,13):
            a,b = ([-324,32,side],[324,32,side]) if axis == 0 else ([side,32,-246],[side,32,246])
            p.beam(a,b,2,M.STEEL_PIPE)
    return p.finish(), dict(wells=wells,pillars=pillars,bridges=bridges,channel_width=42,channel_depth=28,
        interpretation='42格宽按半整数中心取整数格；四格承台顶底及侧壳，深井底Y34，物流槽底Y30；南面主控门口X±52不布置外围柱。')


def gravity_well(index, center):
    p = Part(f'well:{index}'); cx,cz = center
    rods = []
    for i in range(8):
        th = i*math.pi/4; unit = np.array([math.cos(th),0,math.sin(th)])
        start = np.array([cx,35,cz])+unit*35
        end = start + [0,28,0] - unit*(28*math.tan(math.pi/6))
        p.beam(start,end,3,M.ATOMIC)
        for t in np.linspace(.1,.9,5):
            p.sphere(start+(end-start)*t,3.6,COIL)
        p.sphere(end,3,M.LIGHT); rods.append(dict(start=start.tolist(),end=end.tolist()))
    return p.finish(), dict(center_xz=list(center),diameter=88,depth=24,rods=rods,tilt_from_vertical_degrees=30)


def star_core():
    phi = (1+math.sqrt(5))/2
    vertices = np.array([[0,a,b] for a in (-1,1) for b in (-phi,phi)] +
                        [[a,b,0] for a in (-1,1) for b in (-phi,phi)] +
                        [[b,0,a] for a in (-1,1) for b in (-phi,phi)],float)
    hull = ConvexHull(vertices)
    edges = sorted({tuple(sorted((int(f[i]),int(f[(i+1)%3])))) for f in hull.simplices for i in range(3)})
    truncated = np.array([vertices[a]+(vertices[b]-vertices[a])/3 for a,b in edges for a,b in [(a,b),(b,a)]])
    truncated *= 52/np.linalg.norm(truncated[0])
    distances = distance_matrix(truncated,truncated)
    edge_length = distances[distances>1e-5].min()
    links = np.argwhere(np.triu(np.isclose(distances,edge_length),1))
    assert len(truncated) == 60 and len(links) == 90
    cage = Part('core-cage')
    for a,b in links: cage.beam(CORE+truncated[a],CORE+truncated[b],1.4,M.GOLD)
    for at in truncated: cage.sphere(CORE+at,2.2,M.ATOMIC)
    body = Part('core-body')
    q = np.arange(-32,33); xyz = np.array(np.meshgrid(q,q,q,indexing='ij')).reshape(3,-1).T
    r = np.linalg.norm(xyz,axis=1); m = (r<=32)&(r>=29)&(xyz[:,0]+xyz[:,1]<=0)
    body.points(CORE+xyz[m],WHITE)
    for tilt_x,tilt_z in ((0,0),(90,0),(0,90)):
        ring(body,CORE,33,1.5,1,tilt_x,tilt_z)
    body.sphere(CORE,9,M.LIGHT)
    voxels = Part('core-voxels'); cubes=[]
    for i in range(80):
        y = 1-2*(i+.5)/80; a = i*math.pi*(3-math.sqrt(5)); rr = math.sqrt(1-y*y)
        direction = np.array([rr*math.cos(a),y,rr*math.sin(a)])
        if direction[0]+direction[1] <= .2: continue
        side = (4,6,8,10,12)[i%5]; at=CORE+direction*(30+(i%3)*4)
        low=np.rint(at-(side-1)/2).astype(int)
        voxels.box(low,low+side-1,GLASS if i%3 else VIOLET)
        cubes.append(dict(center=at.tolist(),size=side))
    return [cage.finish(),body.finish(),voxels.finish()],dict(center=CORE.tolist(),cage_diameter=104,
        vertices=60,edges=90,faces=32,cage_vertices=(CORE+truncated).tolist(),logic_diameter=64,voxel_cubes=cubes,
        interpretation='截角二十面体为12五边形+20六边形；实体/体素用x+y=0斜分界表达两种构造状态。')


def cannon(side):
    p=Part(f'cannon:{side}')
    for z0 in range(85,247):
        z=side*z0
        for quadrant in range(4):
            th=np.linspace(quadrant*math.pi/2+.16,(quadrant+1)*math.pi/2-.16,94)
            for layer in range(4):
                k=1-layer*.035
                points=np.c_[36*k*np.cos(th),148+34*k*np.sin(th),np.full(len(th),z)]
                p.points(points,WHITE if layer<2 else BLACK)
            if (z0-85)%18 < 2:
                p.points(np.c_[36*np.cos(th),148+34*np.sin(th),np.full(len(th),z)],M.GOLD)
        for x in (-26,26):p.box([x-1,145,z],[x+1,151,z],M.VENT if z0%8<3 else M.ATOMIC)
    for z0 in np.linspace(89,242,12):
        for i in range(8):
            a,b=i*math.pi/4,(i+1)*math.pi/4
            p.beam([22*math.cos(a),148+22*math.sin(a),side*z0],
                   [22*math.cos(b),148+22*math.sin(b),side*z0],1.5,COIL)
    return p.finish()


def wing(side,index):
    angle=math.radians([-10,5,18,32,46,60][index]); length=155+index*8
    root=np.array([side*149,80+index*7,-130+index*52.],float)
    v=np.array([side*math.cos(angle),math.sin(angle),0])
    b0=root; b1=root+v*length*.5+[side*12,0,20]; b2=root+v*length+[0,0,24]
    ts=np.linspace(0,1,2001); path=(1-ts[:,None])**2*b0+2*(1-ts[:,None])*ts[:,None]*b1+ts[:,None]**2*b2
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))]
    path=root+(path-root)*(length/arc[-1])
    p=Part(f'wing:{side}:{index}'); p.sphere(root,9,BLACK);p.sphere(root,7,M.GOLD,True)
    u=np.array([0,0,1.]); normal=np.cross(v,u); normal/=np.linalg.norm(normal)
    ss,nn=np.meshgrid(np.arange(-13,14),np.arange(-5,6),indexing='ij')
    for j in range(0,len(path),4):
        t=j/(len(path)-1); taper=min(1,max(.035,(1-t)/.23))
        diamond=np.abs(ss)/(13*taper)+np.abs(nn)/(5*taper)
        mask=diamond<=1
        edge=mask&(diamond>.9)
        p.points(path[j]+ss[mask,None]*u+nn[mask,None]*normal,WHITE)
        if t<.95:p.points(path[j]+ss[edge,None]*u+nn[edge,None]*normal,M.GOLD)
        if j%64<12:p.points(path[j]+ss[mask&(np.abs(nn)<1),None]*u,CYAN)
    return p.finish(),dict(side=side,index=index,root=root.tolist(),tip=path[-1].tolist(),
        angle_degrees=math.degrees(angle),arc_length=length,width=26,thickness=10,
        interpretation='翼根Y80+7i、Z−130+52i为缺省转译；贝塞尔曲线按完整弧长归一，不夹紧翼尖。')


def print_station(side,index):
    center=np.array([side*250.,105.,(-85,85)[index]])
    p=Part(f'print:{side}:{index}');scan=Part(f'scan:{side}:{index}')
    p.box(center+[-2,-40,-30],center+[-2,45,29],GLASS)
    scan.box(center+[-3,43,-30],center+[-1,44,29],CYAN)
    # 上半玻璃、下半实体，完整齿环与叶轮同源构造。
    for i in range(720):
        a=i*math.pi/360; radius=22+(3 if i%60<28 else 0)
        at=center+[radius*math.cos(a),radius*math.sin(a),0]
        p.sphere(at,1.8,GLASS if at[1]>105 else M.GOLD)
    p.beam(center+[0,0,-8],center+[0,0,8],4,M.TURBINE)
    for i in range(10):
        a=i*math.pi/5; tip=center+[18*math.cos(a),18*math.sin(a),0]
        p.beam(center,tip,1.5,GLASS if tip[1]>105 else WHITE)
    return p.finish(),scan.finish(),dict(center=center.tolist(),screen_width=60,y_range=[65,150],
        type='半构造齿环与涡轮转子',interpretation='原文未给逐件打印物坐标；每侧前后两站，共四站。')


def crowns():
    center=np.array([0.,242.,0.]); parts=[];info=[]
    for i in range(3):
        p=Part(f'crown:{i}')
        radius,tx,tz=(176,0,0) if i==0 else ((125,26,0) if i==1 else (80,0,-32))
        if i==0:
            ring(p,center+[0,-6,0],radius,4,2)
            ring(p,center+[0,6,0],radius,4,2)
            for j in range(24):
                a=j*math.pi/12;b=a+math.pi/12
                for aa,bb in ((a,b),(b,a)):
                    p.beam(center+[radius*math.cos(aa),-6,radius*math.sin(aa)],
                           center+[radius*math.cos(bb),6,radius*math.sin(bb)],1.1,M.GOLD)
                unit=np.array([math.cos(a),0,math.sin(a)])
                tangent=np.array([-math.sin(a),0,math.cos(a)])
                for t in range(-16,17):
                    half=3*(1-abs(t)/16)
                    p.beam(center+unit*(212+t)-tangent*half,center+unit*(212+t)+tangent*half,1,GLASS if abs(t)<10 else WHITE)
        else:
            x,z=math.radians(tx),math.radians(tz)
            rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
            rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
            rotation=rz@rx;normal=rotation@[0,1,0];separation=6 if i==1 else 4
            for sign in (-1,1):ring(p,center+normal*(sign*separation/2),radius,3 if i==1 else 2,2,tx,tz,glass=i==2)
            for j in range(12):
                a=j*math.pi/6;point=center+np.array([radius*math.cos(a),0,radius*math.sin(a)])@rotation.T
                p.beam(point-normal*separation/2,point+normal*separation/2,1,M.ATOMIC if i==1 else M.LIGHT)
            if i==1:
                for j in range(72):
                    a=j*math.pi/36;at=center+np.array([121*math.cos(a),0,121*math.sin(a)])@rotation.T
                    p.sphere(at,1.2,CYAN)
            else:
                for phase in (0,math.pi):
                    points=[center+np.array([73*math.cos(phase+j*2*math.pi/3),0,73*math.sin(phase+j*2*math.pi/3)])@rotation.T for j in range(3)]
                    for a,b in zip(points,points[1:]+points[:1]):p.beam(a,b,1,M.LIGHT)
        parts.append(p.finish());info.append(dict(diameter=[360,256,164][i],center=center.tolist(),tilt_x=tx,tilt_z=tz,
            rails=2,rail_separation=[12,6,4][i]))
    beam=Part('hex-light-cage')
    for j in range(6):
        a=j*math.pi/3;at=[12*math.cos(a),148,12*math.sin(a)]
        beam.beam(at,np.array(at)+[0,94,0],.9,GLASS)
    parts.append(beam.finish())
    return parts,info


def command():
    p=Part('south-command-platform')
    for z in range(200,247):
        half=45-round((z-200)*.38)
        p.box([-half,8,z],[half,12,z],M.ATOMIC)
        for s in (-1,1):
            p.box([s*half-2,13,z],[s*half+2,17,z],WHITE)
            p.points([[s*half,18,z]],M.GOLD)
    for s in (-1,1):
        p.beam([s*36,10,208],[s*28,35,239],5,WHITE)
        p.beam([s*36,10,208],[s*28,35,239],1,M.GOLD)
    xx,yy=np.mgrid[-16:17,-16:17]
    hexagon=np.maximum.reduce([np.abs(xx),np.abs(.5*xx+.8660254*yy),np.abs(.5*xx-.8660254*yy)])
    mask=hexagon<=16
    for z in (244,245,246):
        p.points(np.c_[xx[mask],18+yy[mask],np.full(mask.sum(),z)],BLACK if z<246 else GLASS)
    edge=mask&(hexagon>14)
    p.points(np.c_[xx[edge],18+yy[edge],np.full(edge.sum(),246)],M.GOLD)
    control=[0,18,246];p.points([control],M.CONTROL);ports=[]
    for x in (-21,-18,-12,-9,9,12,18,21):
        at=[x,18,246]
        p.box(np.array(at)-[1,1,2],np.array(at)+[1,1,0],WHITE)
        p.points([at],M.PORT);ports.append(dict(id=f'通用接口{len(ports)+1}',pos=at,face='south'))
    return p.finish(),control,ports


def build():
    parts=[];motions=[]
    def add(p,mode=None,pivot=None):
        parts.append(p)
        if mode:motions.append(dict(id=p.name,mode=mode,pivot_blueprint=list(pivot),amplitude=1.5))
    p,base=foundation();add(p);wellinfo=[]
    for i,at in enumerate(base['wells']):
        p,info=gravity_well(i,at);add(p);wellinfo.append(info)
    ps,core=star_core()
    for p in ps:add(p,{'core-cage':'cage','core-voxels':'voxels'}.get(p.name),CORE)
    cable=Part('eight-data-cables');cables=[];vertices=np.array(core['cage_vertices']);used=set()
    for cx,cz in base['wells']:
        for shift in (-12,12):
            start=np.array([cx+shift,58,cz],float)
            unit=start-CORE;unit/=np.linalg.norm(unit);target=CORE+unit*52
            vertex=next(int(i) for i in np.argsort(np.linalg.norm(vertices-target,axis=1)) if int(i) not in used)
            used.add(vertex);end=vertices[vertex]
            cable.beam(start,end,5,BLACK);cable.beam(start+[0,2,0],end+[0,2,0],1.1,CYAN)
            cables.append(dict(start=start.tolist(),end=end.tolist(),cage_vertex=vertex,diameter=10,
                elevation_degrees=math.degrees(math.atan2(end[1]-start[1],np.linalg.norm((end-start)[[0,2]])))))
    add(cable.finish())
    laser=Part('axial-construct-beam');laser.beam([0,148,-246],[0,148,246],7,GLASS)
    laser.beam([0,148,-246],[0,148,246],1,M.LIGHT);add(laser.finish())
    wings=[];stations=[]
    for side in (-1,1):
        add(cannon(side));arm=Part(f'C-arm:{side}')
        theta=np.linspace(-math.pi*.6,math.pi*.6,360)
        line=np.c_[side*(125+45*np.cos(theta)),139+81*np.sin(theta),np.zeros(len(theta))]
        for z in (-90,90):
            for a,b in zip(line[:-1:3],line[3::3]):arm.beam(a+[0,0,z],b+[0,0,z],3.2,M.ATOMIC)
        for t in range(0,len(line),24):arm.beam(line[t]+[0,0,-90],line[t]+[0,0,90],1.6,M.GOLD)
        for i in range(6):
            p,info=wing(side,i);add(p,'wing',info['root']);wings.append(info)
            root=np.array(info['root']);rails=np.r_[line+[0,0,-90],line+[0,0,90]]
            nearest=rails[np.argmin(np.linalg.norm(rails-root,axis=1))]
            delta=root-nearest;distance=np.linalg.norm(delta)
            if distance>14:arm.beam(nearest,root-delta/distance*14,2,M.GOLD)
            arm.beam(root-delta/max(distance,.01)*min(14,distance),root,1,GLASS)
        add(arm.finish())
        for i in range(2):
            p,scan,info=print_station(side,i);add(p);add(scan,'scan',info['center']);stations.append(info)
    ps,crowninfo=crowns()
    for p in ps:add(p,{'crown:1':'middle','crown:2':'inner'}.get(p.name),[0,242,0])
    p,control,ports=command();add(p)
    low=np.min([p.p.min(0) for p in parts],axis=0);high=np.max([p.p.max(0) for p in parts],axis=0)
    size=high-low+1;cube=np.zeros((size[1],size[2],size[0]),np.uint8);owner=np.zeros_like(cube)
    overlaps=[]
    for i,p in enumerate(parts):
        at=p.p-low;prior=owner[at[:,1],at[:,2],at[:,0]]
        for other in range(i):
            if np.all(p.p.max(0)>=parts[other].p.min(0)) and np.all(parts[other].p.max(0)>=p.p.min(0)):
                shared=np.intersect1d(encode(p.p),encode(parts[other].p),assume_unique=True).size
                if shared:overlaps.append(dict(first=parts[other].name,second=p.name,shared_voxels=int(shared),
                    kind='原案转译重叠，未自动削除',disposition='独立预览保留双方完整构件；组合NBT同格取后生成者。'))
        cube[at[:,1],at[:,2],at[:,0]]=p.states;owner[at[:,1],at[:,2],at[:,0]]=i+1
    LOG.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(LOG/'original-components.npz',**{p.name+'__p':p.p for p in parts},**{p.name+'__s':p.states for p in parts})
    np.savez_compressed(LOG/'final-geometry.npz',cube=cube)
    conflicts=[
        '原案给出炮段Z85..246且称161格；含端点实际162格，本版保留端点。',
        '195格翼长、60度仰角、X135..324及翼尖(324,265)不能共同满足；保留曲线完整弧长与角度，翼根坐标缺省转译公开。',
        '“下半球与左半球”和“上半球与右半球”覆盖区域互有重叠；采用x+y=0斜分界表达两种状态，待原作者复核。',
        '顶环中心Y242、外径256、倾26度与“最高Y302”不能精确同时满足；保留中心、直径与倾角，不夹顶点。',
        '8根数据缆从四座重力井到104格核心笼的既定位置不能全部保持45度；实际端点与倾角逐根记录，未移动井与核心。',
        '40/25/15/12/8为概念材质占比，非给定体素清单；现有资源转译不按比例强行增删构件。',
        '三环双轨完整保留；外环12格轨距遵原文，中环6格与内环4格轨距为缺省转译，待原作者复核。',
        '运行时内环翻转与核心运动可能扫过固定光束及其他部件；本轮仅原案动画试览，不声称动态净空通过。']
    data=dict(key='w02',name='hk3gtl-w02-gemini-half-construct-v4-20261109',
        title='理之律者 · 万象·自律工业矩阵 · Gemini半构造星核船坞 V4',candidate_version='V4',
        nominal_size_xyz=[649,303,493],size=size.tolist(),blueprint_bounds_xyz=dict(min=low.tolist(),max=high.tolist()),
        blueprint_to_export_offset_xyz=(-low).tolist(),controller=(np.array(control)-low).tolist(),controller_blueprint=control,
        controller_face='south',ports=[dict(p,pos=(np.array(p['pos'])-low).tolist()) for p in ports],paths=[],pipe_routes=[],zones=[],
        description='四座重力井、十二片贝塞尔弯刀翼、两门分体轨道炮、半构造星核、截角二十面体机械笼与三重演算冠冕。',
        purpose='按负责人提供的Gemini最新文字建立独立候选；坐标转译与冲突公开，未批准、未部署。',
        foundation=base,wells=wellinfo,core=core,cables=cables,wings=wings,stations=stations,crowns=crowninfo,
        cannons=dict(count=2,axis='Z',inclusive_length=162,coils_per_cannon=12,center_y=148),
        source_conflicts=conflicts,component_overlaps=overlaps,motions=motions,
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist(),blocks=len(p.p)) for p in parts},
        source_author='Gemini文字原案，由负责人本轮提供；几何脚本由当前Codex执行',
        coordinate_interpretation=dict(origin='底面中心(0,0,0)，X宽/Y高/Z深；导出偏移单列',
          wells='四井圆心(±150,±115)，8线圈柱底Y35，高28，朝井心倾30度。',
          cannons='两炮共用轴Y148；各段Z±85..±246，真实端点不调整。',
          wings='左右根X±149、Y80+7i、Z−130+52i；弧长155+8i，角−10/5/18/32/46/60；曲线宽26厚10，末段收尖。',
          material='真理武装只作外观参考；W02仍为理之律者，工艺、电压、研究及毕业身份不改变。'),
        approval=False,installed=False,game_verified=False,dynamic_clearance_verified=False)
    return cube,data,parts


def encode(p):
    q=p.astype(np.int64)+2048
    return (q[:,1]*4096+q[:,2])*4096+q[:,0]
