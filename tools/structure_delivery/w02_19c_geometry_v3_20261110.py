# -*- coding: utf-8 -*-
"""沿用V2姿态，按多视角参考细化19C装甲与机械接合。"""
from copy import deepcopy
import math
from pathlib import Path
import numpy as np
import w02_19c_geometry_v2_20261110 as b
from w02_19c_geometry_v2_20261110 import (
    WHITE,BLACK,BLUE,PALE,DARK,SILVER,LIGHT,GLASS,ORANGE,TRIM,
    panel,basis,annulus,tube,hull,encode)

ROOT=b.ROOT
OUT=ROOT/'deliveries/W02_理之律者19C_多视角细化_V3_20261110'
LOG=ROOT/'logs/w02-19c-detail-v3-20261110'
AMBER,ETCH='minecraft:orange_stained_glass','minecraft:orange_terracotta'
STATES=b.STATES+[AMBER,ETCH];IDS={state:i+1 for i,state in enumerate(STATES)}
ROLES={**b.ROLES,AMBER:'橙色罩体表层',ETCH:'橙罩刻纹与局部提示标识'}


class Part(b.Part):
    def points(self,points,state):
        points=np.rint(points).astype(np.int32).reshape(-1,3)
        if not len(points):return
        assert np.all(np.abs(points)<2048),'完整生成，只报越界、不裁切'
        self.chunks.append(points);self.values.append(np.full(len(points),IDS[state],np.uint8))


def seeded(source,keep=None):
    p=Part(source.name)
    mask=np.ones(len(source.p),bool) if keep is None else keep
    p.chunks.append(source.p[mask].copy());p.values.append(source.states[mask].copy())
    return p


def surface(source,front=True):
    """在已有表面刻线，不把线条悬空铺成第二层外壳。"""
    xy,at=np.unique(source.p[:,:2],axis=0,return_inverse=True)
    z=np.full(len(xy),-4096 if front else 4096,dtype=np.int32)
    (np.maximum.at if front else np.minimum.at)(z,at,source.p[:,2])
    return np.c_[xy,z]


def stroke(p,face,path,state,width=.65,allowed=None):
    xy=face[:,:2];distance=np.full(len(face),np.inf)
    for start,end in zip(path[:-1],path[1:]):
        start,end=np.array(start,float),np.array(end,float);v=end-start
        t=np.clip((xy-start)@v/max(float(v@v),.001),0,1)
        distance=np.minimum(distance,np.linalg.norm(xy-start-t[:,None]*v,axis=1))
    mask=distance<=width
    if allowed is not None:mask&=allowed
    p.points(face[mask],state)


def torso():
    source=b.torso();old_fins=Part('旧短鳍')
    for side in (-1,1):
        hull(old_fins,[(side*23,263,5),(side*34,289,-4),(side*29,293,-8),
                       (side*15,269,-4),(side*23,263,-2)],WHITE)
    old_fins.finish()
    keep=~(np.isin(encode(source.p),encode(old_fins.p))&(source.states==IDS[WHITE]))
    p=seeded(source,keep);face=surface(source)
    # 原薄鳍在体素化后出现孤立尖点，改成有连续内脊的渐细棱刃。
    for side in (-1,1):
        start,end=np.array([side*20,266,-1.]),np.array([side*31,293,-6.])
        axis,u,w=basis(end-start)
        for t in np.linspace(0,1,55):
            center=start+(end-start)*t;rx=6*(1-t)+1.1;rz=2.5*(1-t)+1.1
            xx,zz=np.meshgrid(np.arange(-math.ceil(rx),math.ceil(rx)+1),np.arange(-3,4))
            mask=abs(xx)/rx+abs(zz)/rz<=1
            p.points(center+xx[mask,None]*u+zz[mask,None]*w,WHITE)
        p.beam(start,end,1.3,WHITE)
    x,y,z=face.T
    # R01、R10：罩体有分面和刻纹，中央白线不能当成长眼缝。
    p.points(face[(abs(x)<=2)&(y>=241)&(y<=274)&(z>=36)],ORANGE)
    cap=(abs(x)<=12)&(y>=239)&(y<=278)&(z>=30)
    p.points(face[cap&(abs(x)>=8)&(y<268)],AMBER)
    for side in (-1,1):
        stroke(p,face,[(side*3,274),(side*7,265),(side*5,254)],ETCH,.55,cap)
        stroke(p,face,[(side*8,260),(side*9,251),(side*5,242)],ETCH,.5,cap)
        stroke(p,face,[(side*6,244),(0,239)],ETCH,.55,cap)
        # R04、R31：V形白甲分片、细长的双排黑色通风孔。
        for cy in [183,197]:
            p.box([side*9-2,cy-3,30],[side*9+2,cy+3,32],WHITE)
            panel(p,[(side*8,cy-5),(side*11,cy-4),(side*11,cy+5),(side*8,cy+5)],30,32,SILVER,0)
            panel(p,[(side*8,cy-4),(side*10,cy-3),(side*10,cy+4),(side*8,cy+4)],32,33,BLACK,0)
        for path in [[(6,248),(19,246),(30,250)],[(6,237),(19,234),(32,240)],[(3,174),(13,185),(15,203)]]:
            stroke(p,face,[(side*a,c) for a,c in path],SILVER,.55,(z>=23)&~cap)
        stroke(p,face,[(side*39,251),(side*44,240),(side*35,223)],DARK,.7)
        points=[np.array([side*a,c,d]) for a,c,d in [(12,280,23),(22,271,26),(26,254,28),(23,241,30)]]
        tube(p,points,1.25,GLASS)
        p.beam([side*7,232,36],[side*2,229,37],.8,LIGHT)
    # 以小面积蓝色顶甲打散V2的整块深灰上盖。
    for side in (-1,1):
        panel(p,[(side*7,282),(side*16,274),(side*21,267),(side*15,272)],-1,16,BLUE,1)
    stroke(p,face,[(0,217),(0,206),(0,164)],SILVER,.45,(z>=26)&~cap)
    return p.finish()


def back():
    source=b.back();p=seeded(source)
    for side in (-1,1):
        # R25、R27配合R59：分片侧甲包住轴系，中间保留机械脊柱。
        outline=[(side*a,c) for a,c in [(16,250),(34,241),(37,222),(30,205),(21,185),(17,195),(24,220)]]
        panel(p,outline,-40,-36,SILVER,1)
        tube(p,[np.array([side*a,c,d]) for a,c,d in [(20,246,-41),(31,234,-42),(32,221,-42),(23,201,-41)]],1.4,BLUE)
        for cy in [208,220,232,244]:p.box([side*26-2,cy-2,-43],[side*26+2,cy+2,-40],BLACK)
    annulus(p,np.array([0,226,-46]),[0,0,-1],18,14,2,SILVER)
    annulus(p,np.array([0,226,-48]),[0,0,-1],14,11,1,BLACK)
    annulus(p,np.array([0,226,-49]),[0,0,-1],11,9,1,BLUE)
    for angle in np.arange(8)*math.pi/4:
        c=np.array([16*math.cos(angle),226+16*math.sin(angle),-48])
        p.sphere(c,1,SILVER)
    for cy in [174,184,194]:
        hull(p,[(-6,cy+4,-34),(6,cy+4,-34),(8,cy,-40),(0,cy-5,-41),(-8,cy,-40)],BLACK)
        p.beam([-4,cy,-41],[4,cy,-41],.8,SILVER)
    return p.finish()


def wheel(side):
    p=Part(f'03_{side:+d}_肩侧轮组')
    center=np.array([side*59,227,-3]);axis=np.array([side*.95,0,.31]);v,u,w=basis(axis)
    # R07、R08、R11：胎肩倒角和跨胎宽的斜纹，不能只用一个直筒。
    for depth in range(-7,8):
        radius=34-1.6*(abs(depth)/7)**2
        annulus(p,center+v*depth,v,radius,25,1,BLACK)
    for angle in np.linspace(0,2*math.pi,40,endpoint=False):
        r=math.cos(angle)*u+math.sin(angle)*w;t=-math.sin(angle)*u+math.cos(angle)*w
        p.beam(center+r*33.2-v*6-t*1.4,center+r*33.2+v*6+t*1.4,.75,DARK)
    annulus(p,center+v*8,v,30,27,2,DARK)
    annulus(p,center+v*9,v,28,26,1,SILVER)
    annulus(p,center+v*10,v,26,24.5,1,LIGHT)
    annulus(p,center+v*6,v,24,0,4,BLACK)
    annulus(p,center+v*8,v,21,19,1,BLUE)
    # 三片宽辐板与中心轴盖，对照R04的蓝色侧轮，而非细辐自行车轮。
    for angle in np.arange(3)*2*math.pi/3:
        vertices=[]
        for depth in [8,11]:
            for radius,delta in [(6,-.4),(21,-.15),(23,.17),(10,.42)]:
                vertices.append(center+v*depth+radius*(math.cos(angle+delta)*u+math.sin(angle+delta)*w))
        hull(p,vertices,BLUE)
    annulus(p,center+v*12,v,10,0,3,BLUE)
    annulus(p,center+v*14,v,7,5,1,SILVER)
    annulus(p,center+v*15,v,5,0,1,BLACK)
    for angle in np.arange(6)*math.pi/3:
        p.sphere(center+v*12+15*(math.cos(angle)*u+math.sin(angle)*w),1,SILVER)
    p.beam([side*34,230,-4],center,8,BLACK)
    return p.finish()


def arm(side):
    p=Part(f'04_{side:+d}_曲臂与重型前臂装甲');q=lambda a,c,d:np.array([side*a,c,d],float)
    shoulder,elbow,wrist=q(83,235,-2),q(123,211,8),q(157,147,30)
    p.beam(shoulder,elbow,7,BLACK)
    for delta in [-5,5]:p.beam(shoulder+q(0,delta,3),elbow+q(-4,delta,3),2,SILVER)
    hull(p,[q(87,240,0),q(106,238,0),q(118,224,8),q(107,222,15),q(86,234,12)],WHITE)
    p.sphere(elbow,13,BLACK);annulus(p,elbow+[0,0,12],[0,0,1],10,7,3,SILVER)
    annulus(p,elbow+[0,0,14],[0,0,1],6,0,2,BLUE)
    p.beam(elbow,wrist,5,BLACK)
    b.forearm_shell(p,side,elbow,wrist)
    for delta in [-5,5]:
        tube(p,[shoulder+q(0,delta,10),q(105,238+delta,18),q(124,221+delta,22)],1.6,BLUE if delta<0 else SILVER)
    panel(p,[(side*a,c) for a,c in [(104,234),(124,232),(135,215),(119,212),(110,221)]],12,25,WHITE,2)
    # R05、R12、R31：前臂有锐角分体甲与向手腕收束的蓝色护片。
    panel(p,[(side*a,c) for a,c in [(127,215),(143,199),(161,166),(170,153),(158,154),(139,178)]],28,36,BLUE,1)
    panel(p,[(side*a,c) for a,c in [(141,187),(151,176),(164,157),(156,160)]],36,38,SILVER,1)
    panel(p,[(side*a,c) for a,c in [(145,184),(150,179),(157,165),(151,171)]],38,39,BLACK,0)
    p.sphere(wrist,11,BLACK)
    for d in [-7,7]:p.beam(wrist+q(d,4,4),wrist+q(d,-11,10),2.5,SILVER)
    panel(p,[(side*a,c) for a,c in [(148,163),(165,164),(174,143),(164,146),(157,137),(144,148)]],26,39,BLUE,2)
    source=p.finish();source.states[source.states==IDS[PALE]]=IDS[BLUE]
    p=seeded(source);front=surface(source);rear=surface(source,False)
    for trace in [[(129,205),(136,197),(148,179)],[(139,199),(146,188),(153,177)]]:
        stroke(p,front,[(side*a,c) for a,c in trace],SILVER,.55)
    stroke(p,rear,[(side*134,201),(side*145,180),(side*156,157)],BLACK,2.2)
    stroke(p,rear,[(side*128,202),(side*139,183),(side*149,165)],SILVER,.7)
    stroke(p,front,[(side*132,209),(side*135,205)],ETCH,.9)
    return p.finish()


def finger(p,points):
    a,c,d,tip=points
    for start,end,width in [(a,c,4.2),(c,d,3.8)]:
        p.beam(start,end,width,BLACK)
        v,u,w=basis(end-start);front=np.array([0,0,1.])
        vertices=[]
        for center,radius in [(start,width),(end,width*.8)]:
            for du,dz in [(-radius,0),(radius,0),(-radius*.7,5),(radius*.7,5)]:
                vertices.append(center+u*du+front*dz)
        hull(p,vertices,BLUE)
        annulus(p,end,[1,0,0],width,width-1.2,2,SILVER)
    p.sphere(d,3.6,BLACK)
    hull(p,[d+[-3,2,-1],d+[3,2,-1],d+[-3,-3,5],d+[3,-3,5],tip],BLUE)
    p.beam(d+[0,0,4],tip,.5,SILVER)


def hand(side):
    p=Part(f'05_{side:+d}_长指机械手');q=lambda a,c,d:np.array([side*a,c,d],float)
    panel(p,[(side*a,c) for a,c in [(144,143),(167,147),(178,126),(174,109),(150,109),(138,125)]],28,49,BLACK,3)
    panel(p,[(side*a,c) for a,c in [(149,141),(165,143),(175,126),(168,113),(149,115),(143,125)]],48,53,BLUE,2)
    annulus(p,q(160,128,54),[0,0,1],8,5,1,SILVER)
    annulus(p,q(160,128,55),[0,0,1],5,0,1,LIGHT)
    for angle in np.arange(3)*2*math.pi/3:
        p.beam(q(160+2*math.cos(angle),128+2*math.sin(angle),56),q(160+5*math.cos(angle),128+5*math.sin(angle),56),.5,BLACK)
    # R02、R12：五指长短不同，指尖向前弯曲；不用等长平行圆杆。
    for i,(length,spread) in enumerate([(33,-8),(42,-3),(45,3),(35,8)]):
        x=144+i*9;y=114+abs(i-1.5)*2
        a,c,d,tip=q(x,y,40),q(x+spread*.25,y-15,46),q(x+spread*.65,y-length+7,57),q(x+spread,y-length,70)
        p.sphere(a,5,BLACK);finger(p,[a,c,d,tip])
    a,c,d,tip=q(143,132,42),q(127,122,47),q(125,110,59),q(132,104,69)
    p.sphere(a,6,BLACK);finger(p,[a,c,d,tip])
    # 掌侧伸缩腱同样保留为实体。
    for i in range(4):
        x=144+i*9
        p.beam(q(x,139,30),q(x,116,29),.8,SILVER)
    return p.finish()


def floating_module(side):
    p=Part(f'06_{side:+d}_背上双轨浮游模块');cx=side*91
    for y in [280,296]:
        vertices=[(cx-12,y-2,-61),(cx+12,y-2,-61),(cx+15,y-2,24),(cx+8,y-2,66),
                  (cx,y-1,78),(cx-8,y-2,66),(cx-15,y-2,24),
                  (cx-10,y+3,-56),(cx+10,y+3,-56),(cx+11,y+3,21),(cx,y+3,70)]
        hull(p,vertices,BLUE)
        hull(p,[(cx-7,y+3,-45),(cx+7,y+3,-45),(cx+6,y+3,28),(cx,y+3,48),
                (cx-6,y+3,28),(cx-5,y+4,-40),(cx+5,y+4,-40),(cx,y+4,40)],BLACK)
        for x in [-9,9]:p.beam([cx+x,y+3,-42],[cx+x*.65,y+3,40],.7,SILVER)
        p.beam([cx,y+3,52],[cx,y+1,73],.8,WHITE)
    for z in [-42,-15]:annulus(p,np.array([cx,288,z]),[0,0,1],5,3,4,BLACK)
    annulus(p,np.array([cx,288,20]),[0,0,1],8,5,3,SILVER)
    annulus(p,np.array([cx,288,22]),[0,0,1],6,4,1,BLUE)
    annulus(p,np.array([cx,288,23]),[0,0,1],4,0,1,LIGHT)
    p.box([cx-9,281,-57],[cx+9,296,-50],BLACK)
    # R58双轨俯视：深色中槽、后端罩体、小面积发光刻度。
    for z in [-20,-16,-12]:p.box([cx-6,300,z],[cx-5,300,z+1],LIGHT)
    for y,radius in [(300,7),(301,7),(302,6),(303,6),(304,5),(305,4)]:
        annulus(p,np.array([cx,y,-43]),[0,1,0],radius,0,1,WHITE)
    annulus(p,np.array([cx,306,-43]),[0,1,0],4,0,1,SILVER)
    p.box([cx-3,300,-35],[cx+3,301,-27],BLACK)
    p.box([cx-2,301,-31],[cx+2,302,-28],LIGHT)
    return p.finish()


def chain():
    p=Part('07_背下方弯曲节链');p.beam([0,174,-31],[0,166,-27],3,DARK)
    last=None
    for i in range(24):
        t=i/23;c=np.array([8*math.sin(t*3.2),166-155*t,-27-18*t+6*math.sin(t*4)])
        along=np.array([0.,1.,.12]);along/=np.linalg.norm(along)
        across=np.array([1.,0,0]) if i%2 else np.cross(along,[1.,0,0])
        radius=4*(1-t*.6)
        vertices=[c+along*4.5,c+across*radius,c-along*4.5,c-across*radius,c+along*4.5]
        tube(p,vertices,.8,BLACK if i%2 else DARK)
        if last is not None:p.beam(last,c,.65,BLACK)
        last=c
    hull(p,[last+[-2,1,-2],last+[2,1,-2],last+[2,1,2],last+[-2,1,2],last+[0,-7,1]],BLACK)
    return p.finish()


def build():
    _,prior,oldparts=b.build()
    parts=[torso(),back(),wheel(-1),wheel(1),arm(-1),arm(1),hand(-1),hand(1),floating_module(-1),floating_module(1),chain()]
    assert [p.name for p in parts]==[p.name for p in oldparts]
    points=np.concatenate([p.p for p in parts]);low,high=points.min(0),points.max(0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    changes=[];overlaps=[]
    for p,old in zip(parts,oldparts):
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states
        changed=len(np.setxor1d(encode(p.p),encode(old.p)))
        assert changed>0,p.name+'没有实际几何细化'
        changes.append(dict(component=p.name,previous_blocks=len(old.p),current_blocks=len(p.p),position_difference=changed))
    for i,a in enumerate(parts):
        for c in parts[i+1:]:
            shared=np.intersect1d(encode(a.p),encode(c.p),assume_unique=True)
            if len(shared):overlaps.append(dict(first=a.name,second=c.name,shared_voxels=len(shared),classification='机械接合或待审干涉，未宣称全面无穿模'))
    data=deepcopy(prior)
    data.update(name='hk3gtl-w02-19c-detail-v3-20261110',title='理之律者 · 重装小兔19C · 多视角细化V3',
        candidate_version='19C-V3多视角细化',display_version='V3',size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        component_overlaps=overlaps,geometry_delta_vs_v2=changes,base_candidate=OUT.parent.joinpath(b.OUT.name,'index.html').relative_to(ROOT).as_posix(),
        summary='沿用V2姿态，细化罩体刻纹与胸甲、倒角轮胎和三辐板轮毂、分片臂甲、错落弯曲的五指、背部轴系、双轨中槽及镂空节链。')
    data['detail_changes']=[
        dict(component='胸甲与罩体',references=['R01','R04','R10','R31'],change='取消白色长眼缝，增加橙罩刻纹、下颌细光缝、分片线与细长胸甲开孔'),
        dict(component='肩侧轮组',references=['R04','R07','R08','R11'],change='胎肩倒角、斜向胎纹、内外轮圈与宽三辐板轮毂分层'),
        dict(component='曲臂与前臂',references=['R05','R12','R24','R31'],change='上臂活塞、前臂锐角护片、后侧装甲槽和腕部护甲'),
        dict(component='五指机械手',references=['R02','R05','R12'],change='四指长短与张角错开，独立拇指、两段指节、铰链轴和前弯尖指'),
        dict(component='背部与节链',references=['R25','R27','R28','R59'],change='背部侧甲与轴承分层、下脊椎片及交错镂空链节；二创仅辅助遮挡处'),
        dict(component='双轨模块',references=['R28','R32','R46','R53','R58'],change='上下装甲中槽、主环形开口与后部罩体；俯视细节含二创结构转译')]
    data['source_conflicts'][2]='沿用V2双臂下垂的静态姿态；手指按官方展开特写调整，不宣称是官方精确待机姿态。'
    data['source_conflicts'][3]='装甲刻线、关节深度和模块内部按可见参考进行体素转译，仍待外观评审；未声称逐处复刻。'
    return cube,data,parts
