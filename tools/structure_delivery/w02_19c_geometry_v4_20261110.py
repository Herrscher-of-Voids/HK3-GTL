# -*- coding: utf-8 -*-
"""把19C静态体态改为前探机甲兽，重做曲臂和分叉炮舱。"""
from copy import deepcopy
import math
import numpy as np
from scipy.ndimage import distance_transform_edt,map_coordinates
import w02_19c_geometry_v3_20261110 as b
from w02_19c_geometry_v3_20261110 import (
    Part,WHITE,BLACK,BLUE,PALE,DARK,SILVER,LIGHT,GLASS,ORANGE,TRIM,AMBER,ETCH,
    STATES,IDS,ROLES,panel,basis,annulus,tube,hull,encode)

ROOT=b.ROOT
OUT=ROOT/'deliveries/W02_理之律者19C_机甲兽体态_V4_20261110'
LOG=ROOT/'logs/w02-19c-beast-v4-20261110'
PRIOR=b.OUT
REFERENCE_BASE=b.b.OUT
VERSION='V4'
BODY_MATRIX=np.array([[1.04,0,0],[0,.48,-.18],[0,-.35,1.3]])
BODY_SHIFT=np.array([0,246,12])-BODY_MATRIX@np.array([0,238,5])


class SolidPart(Part):
    def beam(self,start,end,radius,state):
        a,c=np.asarray(start,float),np.asarray(end,float);v=c-a
        if np.linalg.norm(v)<.01:return self.sphere(a,radius,state)
        lo=np.floor(np.minimum(a,c)-radius).astype(int);hi=np.ceil(np.maximum(a,c)+radius).astype(int)
        zz,xx=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
        for y in range(lo[1],hi[1]+1):
            coords=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()]
            t=np.clip((coords-a)@v/(v@v),0,1)
            self.points(coords[np.linalg.norm(coords-a-t[:,None]*v,axis=1)<=radius],state)


def solid_annulus(p,center,axis,radius,inner,depth,state):
    axis=np.asarray(axis,float);axis/=np.linalg.norm(axis);center=np.asarray(center,float)
    extent=np.sqrt(1-axis*axis)*radius+abs(axis)*depth/2
    lo=np.floor(center-extent).astype(int);hi=np.ceil(center+extent).astype(int)
    zz,xx=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
    for y in range(lo[1],hi[1]+1):
        coords=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()];relative=coords-center
        axial=relative@axis;radial=np.linalg.norm(relative-axial[:,None]*axis,axis=1)
        p.points(coords[(abs(axial)<=depth/2+.01)&(radial<=radius)&(radial>=inner)],state)


def transformed(source,matrix,shift,name=None):
    """保留中心采样，并补入有足够覆盖率的薄甲边缘，不删除构件。"""
    low,high=source.p.min(0)-1,source.p.max(0)+1
    size=high-low+1;dense=np.zeros(tuple(size),np.uint8)
    dense[tuple((source.p-low).T)]=source.states
    corners=np.array([[x,y,z] for x in [low[0]-.5,high[0]+.5] for y in [low[1]-.5,high[1]+.5] for z in [low[2]-.5,high[2]+.5]])
    bounds=corners@matrix.T+shift;lo=np.floor(bounds.min(0)).astype(int);hi=np.ceil(bounds.max(0)).astype(int)
    zz,xx=np.meshgrid(np.arange(lo[2],hi[2]+1),np.arange(lo[0],hi[0]+1),indexing='ij')
    inverse=np.linalg.inv(matrix);p=Part(name or source.name)
    coverage=(dense>0).astype(np.float32)
    nearest=distance_transform_edt(dense==0,return_distances=False,return_indices=True)
    nearest_material=dense[tuple(nearest)]
    for y in range(lo[1],hi[1]+1):
        world=np.c_[xx.ravel(),np.full(xx.size,y),zz.ravel()]
        local=(world-shift)@inverse.T-low;sample=np.floor(local+.5).astype(int)
        inside=np.all((sample>=0)&(sample<size),axis=1)
        values=np.zeros(len(world),np.uint8);values[inside]=dense[tuple(sample[inside].T)]
        edge=(values==0)&(map_coordinates(coverage,local.T,order=1,mode='constant',cval=0,prefilter=False)>.22)
        values[edge]=map_coordinates(nearest_material,local[edge].T,order=0,mode='nearest',prefilter=False)
        for value in np.unique(values[values>0]):p.points(world[values==value],STATES[int(value)-1])
    return p.finish()


def body(source):
    t=transformed(source,BODY_MATRIX,BODY_SHIFT)
    p=b.seeded(t)
    # 白蓝下颌前伸，保留19C罩体和尖盾身份，不补人形腰腹。
    for side in (-1,1):
        hull(p,[(side*7,218,54),(side*31,232,45),(side*39,223,59),(side*29,212,79),
                (side*13,207,85),(side*6,213,74)],WHITE)
        p.beam([side*12,214,78],[side*28,219,73],1,BLUE)
        p.beam([side*12,218,74],[side*28,224,65],.9,BLACK)
    return p.finish()


def dorsal(source):
    t=transformed(source,BODY_MATRIX,BODY_SHIFT);p=b.seeded(t)
    # R25、R27的背部轴系，转译成前低后高的分片背甲。
    for z,y,width in [(-39,263,20),(-24,275,23),(-9,277,19)]:
        hull(p,[(-width,y-10,z-10),(width,y-10,z-10),(width*.8,y,z),
                (0,y+6,z-2),(-width*.8,y,z),(0,y-8,z+12)],BLACK)
        p.beam([-width*.6,y,z],[0,y+4,z-2],1,BLUE)
        p.beam([0,y+4,z-2],[width*.6,y,z],1,BLUE)
    return p.finish()


def bezier(points,t):
    a,c,d,e=np.asarray(points,float);return (1-t)**3*a+3*t*(1-t)**2*c+3*t*t*(1-t)*d+t**3*e


def arm(side):
    p=SolidPart(f'04_{side:+d}_曲臂与重型前臂装甲');q=lambda x,y,z:np.array([side*x,y,z],float)
    shoulder,elbow,wrist=q(81,242,-10),q(126,226,1),q(145,185,88)
    p.beam(shoulder,elbow,6.5,BLACK)
    for dy in [-5,5]:p.beam(shoulder+q(2,dy,6),elbow+q(-6,dy,8),2,SILVER)
    for angle in [0,math.pi]:
        p.beam(shoulder+[0,3*math.cos(angle),3*math.sin(angle)],elbow,1,BLUE)
    hull(p,[q(85,248,-4),q(105,245,1),q(119,233,7),q(109,228,14),q(86,238,9)],WHITE)
    p.sphere(elbow,13,BLACK);solid_annulus(p,elbow+[0,0,12],[0,0,1],10,6,3,SILVER)
    solid_annulus(p,elbow+[0,0,14],[0,0,1],6,0,2,BLUE)
    path=[elbow,q(141,225,26),q(152,201,58),wrist]
    def section(t):
        c=bezier(path,t);t0=max(0,t-.002);t1=min(1,t+.002)
        axis=bezier(path,t1)-bezier(path,t0);axis/=np.linalg.norm(axis)
        u=q(1,0,0);u-=axis*(u@axis);u/=np.linalg.norm(u);w=np.cross(axis,u)*side
        rx=float(np.interp(t,[0,.20,.55,.84,1],[13,21,20,14,10]))
        rz=float(np.interp(t,[0,.20,.55,1],[10,15,14,9]))
        return c,u,w,rx,rz
    def points(t,profile):
        c,u,w,rx,rz=section(t)
        return np.array([c+u*x*rx+w*z*rz for x,z in profile])
    stations=np.linspace(0,1,17)
    profile=[(-.8,-.5),(-.55,.8),(.4,1),(.9,.4),(.7,-.65),(-.25,-.85)]
    for a,c in zip(stations[:-1],stations[1:]):
        hull(p,np.vstack([points(a,profile),points(c,profile)]),BLACK)
    # 肘端宽、腕端窄，三片锐角护甲之间保留真正的机械接缝。
    for start,end in [(.08,.38),(.40,.71),(.73,.98)]:
        middle=(start+end)/2
        for profile,state in [([(-1,-.2),(-.88,.65),(-.34,1.12),(.32,.95),(.14,.65),(-.5,.25)],WHITE),
                              ([(.30,.97),(.84,.57),(1.12,.04),(.91,-.57),(.69,-.50),(.70,.32)],BLUE)]:
            hull(p,np.vstack([points(start,profile),points(middle,profile),points(end,[(x*.62,z*.82) for x,z in profile])]),state)
        for lateral,state in [(-.47,SILVER),(.73,PALE)]:
            tube(p,[points(t,[(lateral,.8)])[0] for t in np.linspace(start,end-.025,12)],1,state)
    # 双活塞与凹槽沿内侧贯通，外侧用两条收尖棱线分开大甲面。
    for lateral in [-.36,.28]:
        tube(p,[points(t,[(lateral,-.74)])[0] for t in np.linspace(.12,.9,25)],1.6,SILVER)
    for a,c in [(.17,.31),(.47,.65),(.79,.9)]:
        tube(p,[points(t,[(.92,.14)])[0] for t in np.linspace(a,c,12)],1.3,DARK)
    c,u,w,rx,rz=section(.27)
    p.beam(c+u*rx*.96-w*2,c+u*rx*.96+w*2,1,ETCH)
    tube(p,[q(83,248,7),q(106,246,19),q(129,231,24)],1.7,BLUE)
    p.sphere(wrist,10,BLACK)
    for d in [-6,6]:p.beam(wrist+q(d,4,0),wrist+q(d,-8,15),2,SILVER)
    return p.finish()


def hand(side):
    source=b.hand(side)
    matrix=np.array([[.95,0,0],[0,.65,.35],[0,-.55,.9]])
    shift=np.array([side*145,176,96])-matrix@np.array([side*160,128,45])
    return transformed(source,matrix,shift)


def cannon(side, target=None, origin=None):
    p=SolidPart(f'06_{side:+d}_背上双轨浮游模块')
    yaw=math.radians(side*(9 if side<0 else 14));pitch=math.radians(-5 if side<0 else 3)
    forward=np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch)])
    shift=np.array([side*92,286+(7 if side>0 else -2),-47]) if origin is None else np.asarray(origin,float)
    if target is not None:
        forward=np.asarray(target,float)-shift;forward/=np.linalg.norm(forward)
    across=np.cross([0,1,0],forward);across/=np.linalg.norm(across);up=np.cross(forward,across)
    roll=math.radians(-side*7);matrix=np.column_stack([across*math.cos(roll)+up*math.sin(roll),
        up*math.cos(roll)-across*math.sin(roll),forward])
    world=lambda vertices:np.asarray(vertices)@matrix.T+shift
    solid=lambda vertices,state:hull(p,world(vertices),state)
    line=lambda a,c,r,state:p.beam(world(a),world(c),r,state)
    trace=lambda vertices,r,state:tube(p,world(vertices),r,state)
    ring=lambda center,radius,inner,depth,state:solid_annulus(p,world(center),forward,radius,inner,depth,state)
    box=lambda lo,hi,state:solid([[x,y,z] for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]],state)
    # R32外轮廓配合R46、R53俯侧结构：后部炮舱、分叉导轨、前窄后厚。
    rings=[]
    for z,rx,ry in [(-9,9,10),(0,17,14),(20,19,15),(39,15,13),(54,12,9)]:
        angle=np.arange(8)*math.pi/4;rings.append(np.c_[np.cos(angle)*rx,np.sin(angle)*ry,np.full(8,z)])
    for a,c in zip(rings[:-1],rings[1:]):solid(np.vstack([a,c]),BLACK)
    for side_armor in [-1,1]:
        solid([(side_armor*11,-5,-3),(side_armor*19,-3,12),(side_armor*18,7,27),
                (side_armor*12,11,38),(side_armor*9,3,43),(side_armor*12,-6,25)],WHITE)
        line([side_armor*18,1,11],[side_armor*13,6,34],1.4,BLUE)
    for sign,tip in [(1,143),(-1,129)]:
        stations=[]
        for z,rx,y,thickness in [(25,15,sign*12,4),(47,17,sign*15,4),(76,12,sign*14,3),
                                  (106,7,sign*11,2),(tip,1,sign*5,1)]:
            station=np.array([[-rx,y-thickness,z],[rx,y-thickness,z],[rx,y+thickness,z],[-rx,y+thickness,z]])
            stations.append(station)
        for a,c in zip(stations[:-1],stations[1:]):solid(np.vstack([a,c]),BLUE)
        for edge in [-1,1]:
            trace([np.array([edge*rx,y+sign*th,z]) for z,rx,y,th in [(27,14,sign*12,4),(47,16,sign*15,4),
                (76,11,sign*14,3),(106,6,sign*11,2),(tip,0,sign*5,1)]],.9,WHITE)
        solid([(-7,sign*18,43),(7,sign*18,43),(5,sign*16,78),(0,sign*11,112),
                (-5,sign*16,78),(0,sign*19,55)],BLACK)
        line([0,sign*19,46],[0,sign*16,78],.8,SILVER)
    line([0,0,30],[0,0,83],4.5,BLACK)
    for z,radius in [(36,8),(54,7),(72,5)]:
        ring([0,0,z],radius,radius-2,4,SILVER)
        ring([0,0,z+3],radius-1,radius-2,1,BLUE)
    ring([0,0,38],5,0,1,LIGHT)
    for z in [5,10,15]:box([-5,15,z],[5,16,z+2],DARK)
    # 橙色集中在后端推进罩，取消像帽子的顶部凸锥。
    ring([0,2,-8],8,4,5,ORANGE)
    ring([0,2,-11],6,3,1,ETCH)
    line([-5,15,5],[5,15,5],1,ORANGE)
    for s in [-1,1]:
        solid([(s*12,-2,7),(s*26,0,20),(s*23,-2,35),(s*13,-8,27),(s*12,-5,16)],BLUE)
        line([s*17,1,17],[s*23,0,24],.7,PALE)
    box([-3,16,25],[3,17,29],GLASS)
    return p.finish()


def tail():
    p=Part('07_背下方弯曲节链');path=[[0,229,-56],[0,201,-75],[13,180,-122],[17,179,-166]]
    previous=None
    for i,t in enumerate(np.linspace(0,1,29)):
        c=bezier(path,t);axis=bezier(path,min(1,t+.002))-bezier(path,max(0,t-.002));axis/=np.linalg.norm(axis)
        _,u,w=basis(axis);cross=u if i%2 else w;r=4*(1-t*.55)
        tube(p,[c+axis*4.5,c+cross*r,c-axis*4.5,c-cross*r,c+axis*4.5],1,BLACK if i%2 else DARK)
        if previous is not None:p.beam(previous,c,.8,BLACK)
        previous=c
    p.beam([0,234,-51],[0,229,-56],3,DARK)
    hull(p,[previous+[-2,1,-2],previous+[2,1,-2],previous+[2,-1,2],previous+[-2,-1,2],previous+[0,-1,-9]],BLUE)
    return p.finish()


def build():
    _,prior,oldparts=b.build();old={p.name:p for p in oldparts}
    parts=[body(oldparts[0]),dorsal(oldparts[1])]
    for side in [-1,1]:
        source=old[f'03_{side:+d}_肩侧轮组']
        parts.append(transformed(source,np.eye(3),np.array([side*2,12,-7])))
    parts.extend([arm(-1),arm(1),hand(-1),hand(1),cannon(-1),cannon(1),tail()])
    assert [p.name for p in parts]==[p.name for p in oldparts]
    points=np.concatenate([p.p for p in parts]);low,high=points.min(0),points.max(0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8);overlaps=[];changes=[]
    for p,previous in zip(parts,oldparts):
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states
        delta=len(np.setxor1d(encode(p.p),encode(previous.p)));assert delta>0
        changes.append(dict(component=p.name,previous_blocks=len(previous.p),current_blocks=len(p.p),position_difference=delta))
    for i,a in enumerate(parts):
        for c in parts[i+1:]:
            count=len(np.intersect1d(encode(a.p),encode(c.p),assume_unique=True))
            if count:overlaps.append(dict(first=a.name,second=c.name,shared_voxels=count,classification='接合或待审干涉，不宣称全部无穿模'))
    body_extent=parts[0].p.max(0)-parts[0].p.min(0)+1
    assert body_extent[1]<105 and body_extent[2]>100,'主体需要前探，不能恢复长人形胸甲'
    assert min(p.p[:,2].max() for p in parts if p.name.startswith('05_'))>140,'前爪没有探出'
    for p in parts:
        if p.name.startswith('06_'):
            assert not any(set([a['first'],a['second']])==set([p.name,other.name]) for a in overlaps for other in parts if other.name!=p.name),'炮舱与其他构件干涉'
    data=deepcopy(prior)
    data.update(name='hk3gtl-w02-19c-beast-v4-20261110',title='理之律者 · 重装小兔19C · 机甲兽体态V4',
        candidate_version='19C-V4机甲兽体态',display_version=VERSION,size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        component_overlaps=overlaps,geometry_delta_vs_v3=changes,base_candidate=PRIOR.relative_to(ROOT).as_posix()+'/index.html',
        center_blueprint=[0,240,20],summary='缩短直立胸甲，主体前探下压、背甲隆起；屈臂分成三段锐角护甲，露出双活塞与收尖棱线；双炮改为后厚前尖的分叉炮舱，左右错高并外撇；节链向后摆。')
    data['detail_changes']=[
        dict(component='机甲兽体态',references=['R04','R25','R31','R32'],change='依据负责人反馈进行比例与姿态转译：缩短直立盾形胸腹、前探下颌、隆起背甲；保留19C双臂、轮组与橙罩'),
        dict(component='曲臂轮廓',references=['R05','R12','R24','R31'],change='屈肘前探，三段锐角护甲向腕端收尖；双活塞、凹槽、银蓝棱线与独立肘节，减弱等宽圆弧套筒感'),
        dict(component='前爪与尾链',references=['R02','R12','R25','R59'],change='保留五指细节，前掌与尖指前探；节链后摆，取消直立人形双臂垂落的轮廓'),
        dict(component='双炮',references=['R28','R32','R46','R53'],change='厚后舱、分层楔形护壳、不等长分叉导轨与内置环形膛口；左右错高、微外撇，纯静态')]
    data['source_conflicts'][2]='V4按负责人要求强调机甲兽体态，前探与屈臂、双炮错角为姿态转译，不宣称官方精确待机或逐处复刻。'
    data['reference_correspondence'][0]['status']='官方19C身份元素保留；主体比例按负责人要求重新转译为机甲兽感觉'
    return cube,data,parts


CAMERA_VIEWS={
    'detail_chest':dict(label='兽形主体',center=[0,240,25],half=[55,48,70],direction=[-.5,.25,1.6],file='胸甲细节.png'),
    'detail_wheel':dict(label='曲臂线条',center=[136,211,43],half=[43,48,70],direction=[1.1,.3,1.4],file='轮组细节.png'),
    'detail_hand':dict(label='前爪细节',center=[145,169,115],half=[39,38,46],direction=[.7,.45,1.5],file='机械手细节.png'),
    'detail_back':dict(label='背甲与后摆节链',center=[0,232,-68],half=[59,62,107],direction=[.8,.4,-1.5],file='背部细节.png'),
    'detail_module':dict(label='分叉炮舱',center=[105,296,18],half=[42,43,91],direction=[1.1,.8,1.5],file='模块细节.png')}
