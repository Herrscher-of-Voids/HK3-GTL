# -*- coding: utf-8 -*-
"""根据60张分源参考重建普通理律19C静态候选，不沿用V1外形。"""
import math
from pathlib import Path
import numpy as np
from w02_19c_study_20261110 import Part as StudyPart, encode, hull

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W02_理之律者19C_多视角重制_V2_20261110'
LOG=ROOT/'logs/w02-19c-reference-study-20261110'
WHITE,BLACK,BLUE,PALE=('minecraft:white_concrete','minecraft:gray_concrete',
                       'minecraft:light_blue_concrete','minecraft:blue_ice')
DARK,SILVER,LIGHT='minecraft:deepslate_tiles','minecraft:light_gray_concrete','minecraft:sea_lantern'
GLASS,ORANGE,TRIM='minecraft:cyan_stained_glass','minecraft:orange_concrete','minecraft:blue_concrete'
STATES=[WHITE,BLACK,BLUE,PALE,DARK,SILVER,LIGHT,GLASS,ORANGE,TRIM]
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES=dict(zip(STATES,['白色装甲分片','深灰机械内构','理律构造蓝装甲','冰蓝装甲切面','暗色轮胎与节链',
                      '轴承与金属接合','静态发光节点','青蓝观察窗','橙色罩体','深蓝窄边']))


class Part(StudyPart):
    def points(self,points,state):
        p=np.rint(points).astype(np.int32).reshape(-1,3)
        if not len(p):return
        assert np.all(np.abs(p)<2048),'越界报错，不裁切'
        self.chunks.append(p);self.values.append(np.full(len(p),IDS[state],np.uint8))


def panel(p,outline,back,front,state,bevel=1):
    """保留凹轮廓的装甲薄片；V形间隙不能被凸包填死。"""
    vertices=np.asarray(outline,float);low=np.floor(vertices.min(0)).astype(int);high=np.ceil(vertices.max(0)).astype(int)
    xx,yy=np.meshgrid(np.arange(low[0],high[0]+1),np.arange(low[1],high[1]+1))
    x,y=xx.ravel(),yy.ravel();inside=np.zeros(x.shape,bool)
    edge=np.full(x.shape,np.inf)
    for a,b in zip(vertices,np.roll(vertices,-1,axis=0)):
        cross=((a[1]>y)!=(b[1]>y)) & (x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1]+1e-12)+a[0])
        inside^=cross
        v=b-a;t=np.clip(((x-a[0])*v[0]+(y-a[1])*v[1])/max(float(v@v),.001),0,1)
        edge=np.minimum(edge,np.hypot(x-a[0]-t*v[0],y-a[1]-t*v[1]))
    for z in range(round(back),round(front)+1):
        m=inside & (edge>=max(0,z-(front-bevel)))
        p.points(np.c_[x[m],y[m],np.full(m.sum(),z)],state)


def basis(axis):
    v=np.array(axis,float);v/=np.linalg.norm(v)
    ref=[0,1,0] if abs(v[1])<.9 else [0,0,1]
    u=np.cross(v,ref);u/=np.linalg.norm(u)
    return v,u,np.cross(v,u)


def annulus(p,center,axis,radius,inner,depth,state):
    v,u,w=basis(axis);q=np.arange(-math.ceil(radius),math.ceil(radius)+1)
    x,z=np.meshgrid(q,q);mask=(x*x+z*z<=radius*radius)&(x*x+z*z>=inner*inner)
    cross=x[mask,None]*u+z[mask,None]*w
    for t in np.arange(-depth/2,depth/2+.1):p.points(center+cross+v*t,state)


def tube(p,path,radius,state):
    for a,b in zip(path[:-1],path[1:]):p.beam(a,b,radius,state)


def torso():
    p=Part('01_尖盾主躯干与橙色罩体')
    # R04、R10、R31：主机体是窄长尖盾，不能挤成宽胸矩形。
    rings=[]
    for y,rx,rz,cz in [(145,2,2,5),(174,22,18,-2),(200,39,28,-5),
                       (231,44,27,-5),(260,29,18,-9),(285,7,9,-10)]:
        angles=np.arange(8)*math.pi/4
        rings.append(np.c_[np.cos(angles)*rx,np.full(8,y),np.sin(angles)*rz+cz])
    for a,b in zip(rings[:-1],rings[1:]):hull(p,np.vstack([a,b]),BLACK)
    for side in (-1,1):
        mirror=lambda pts:[(side*x,y) for x,y in pts]
        panel(p,mirror([(4,253),(30,262),(40,236),(29,214),(2,225),(15,238)]),12,24,WHITE,3)
        panel(p,mirror([(0,221),(29,233),(39,234),(26,209),(0,194)]),23,28,BLUE,2)
        panel(p,mirror([(0,197),(26,211),(30,211),(22,174),(0,151)]),13,25,TRIM,2)
        panel(p,mirror([(0,205),(22,216),(19,179),(0,160)]),26,30,WHITE,2)
        panel(p,mirror([(25,258),(39,266),(47,241),(40,217),(31,209),(38,243)]),2,13,SILVER,2)
        panel(p,mirror([(28,242),(32,255),(37,242),(29,213),(24,216)]),15,20,BLUE,1)
        for y in [180,193]:p.box([side*9-2,y,30],[side*9+2,y+6,32],DARK)
        panel(p,mirror([(0,158),(25,180),(20,165),(0,144)]),18,26,BLUE,2)
        # R31左右上扬短鳍；不扩写成十二翼。
        hull(p,[(side*23,263,5),(side*34,289,-4),(side*29,293,-8),
                (side*15,269,-4),(side*23,263,-2)],WHITE)
        tube(p,[np.array([side*x,y,z]) for x,y,z in [(26,273,18),(35,257,20),(39,237,21),(29,217,22)]],1.5,PALE)
    hull(p,[(0,281,24),(-14,264,25),(-10,245,30),(0,229,34),
            (10,245,30),(14,264,25),(0,258,42)],DARK)
    hull(p,[(0,279,27),(-11,263,30),(-8,246,34),(0,235,37),
            (8,246,34),(11,263,30),(0,257,44)],ORANGE)
    p.box([-5,227,34],[5,231,35],GLASS)
    p.beam([-1,273,39],[-1,242,43],.8,WHITE)
    panel(p,[(-11,233),(0,225),(11,233),(7,222),(0,216),(-7,222)],29,34,WHITE)
    return p.finish()


def back():
    p=Part('02_背部轴系与散热脊柱')
    for y in range(164,260,12):
        width=12 if y<195 else 22
        p.box([-width,y,-34],[width,y+7,-30],BLACK)
        for x in range(-width+3,width-2,6):p.box([x,y+1,-37],[x+2,y+6,-34],DARK)
    annulus(p,np.array([0,226,-40]),[0,0,1],20,12,5,DARK)
    annulus(p,np.array([0,226,-44]),[0,0,1],15,12,2,BLUE)
    annulus(p,np.array([0,226,-46]),[0,0,1],8,0,2,BLACK)
    for side in (-1,1):
        path=[np.array([side*x,y,z]) for x,y,z in [(21,258,-24),(40,248,-30),(49,226,-22),(51,215,-10)]]
        tube(p,path,3.5,DARK);tube(p,[a+[0,0,-3] for a in path],1,SILVER)
        hull(p,[(side*9,205,-33),(side*28,230,-26),(side*36,201,-21),
                (side*17,176,-31),(side*9,181,-36)],TRIM)
    return p.finish()


def wheel(side):
    p=Part(f'03_{side:+d}_肩侧轮组')
    center=np.array([side*59,227,-3]);axis=np.array([side*.95,0,.31]);axis/=np.linalg.norm(axis)
    v,u,w=basis(axis)
    annulus(p,center,v,34,25,15,DARK)
    annulus(p,center+v*9,v,30,26,2,BLACK)
    annulus(p,center+v*10,v,27,25,1,BLUE)
    annulus(p,center+v*11,v,26,24,1,LIGHT)
    annulus(p,center,v,24,0,11,BLACK)
    annulus(p,center+v*7,v,13,0,5,BLUE)
    annulus(p,center+v*10,v,8,0,2,PALE)
    for theta in np.linspace(0,2*math.pi,30,endpoint=False):
        r=math.cos(theta)*u+math.sin(theta)*w
        p.beam(center+r*32-v*6,center+r*34+v*5,1,BLACK)
    for theta in np.arange(3)*2*math.pi/3:
        r=math.cos(theta)*u+math.sin(theta)*w
        p.beam(center+r*9+v*8,center+r*23+v*8,3,BLUE)
    p.beam([side*34,230,-4],center,8,BLACK)
    return p.finish()


def forearm_shell(p,side,a,b):
    axis=(b-a)/np.linalg.norm(b-a);front=np.array([0.,0.,1.])
    w=front-axis*np.dot(front,axis);w/=np.linalg.norm(w);u=np.cross(axis,w)
    length=np.linalg.norm(b-a)
    q=np.arange(-30,31);xx,zz=np.meshgrid(q,q)
    for step in range(math.ceil(length)+1):
        t=step/length;center=a+(b-a)*t
        rx=float(np.interp(t,[0,.18,.65,1],[15,24,27,16]));rz=float(np.interp(t,[0,.2,.7,1],[12,20,22,13]))
        rr=(xx/rx)**2+(zz/rz)**2
        mask=(rr<=1)&((rr>=.70)|(step<2)|(step>length-2))
        local_x,local_z=xx[mask],zz[mask];coords=center+local_x[:,None]*u+local_z[:,None]*w
        # R05、R31、R37：蓝白包边、内侧黑甲，不是整块蓝色平板。
        state=np.full(len(coords),IDS[BLACK],np.uint8)
        state[(local_z<0)&(local_x*side<rx*.25)]=IDS[WHITE]
        state[(np.abs(local_x)>rx*.65)]=IDS[BLUE]
        state[(local_x*side<-rx*.82)&(local_z>0)]=IDS[PALE]
        face=(local_z>rz*.35)
        diagonal=local_x*side/rx-(.7-1.4*t)
        state[face&(diagonal>.10)&(diagonal<.38)]=IDS[WHITE]
        state[face&(np.abs(diagonal-.42)<.06)]=IDS[BLUE]
        for seam in [.23,.68]:
            state[face&(abs(t-seam)<.012)&(local_x*side/rx>-.4)]=IDS[DARK]
        if .47<t<.50:state[np.abs(local_x)>rx*.55]=IDS[DARK]
        for s in np.unique(state):p.points(coords[state==s],STATES[int(s)-1])
    # 一整片沿臂延伸的蓝白包边；不使用无依据的等距环箍。
    for flank in [-1,1]:
        vertices=[]
        for t,rx,rz in [(0,15,12),(.3,25,20),(.76,24,20),(1,16,13)]:
            c=a+(b-a)*t
            for f in [.73,1.02]:vertices.append(c+u*rx*f*flank+w*rz*.45)
        hull(p,vertices,WHITE if flank*side>0 else BLUE)


def arm(side):
    p=Part(f'04_{side:+d}_曲臂与重型前臂装甲')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    shoulder,elbow,wrist=q(83,235,-2),q(123,211,8),q(157,147,30)
    p.beam(shoulder,elbow,7,BLACK)
    for t in np.linspace(.15,.9,5):
        c=shoulder+(elbow-shoulder)*t;p.sphere(c,9,DARK)
        p.box(c-[3,4,4],c+[3,4,4],SILVER)
    p.sphere(elbow,13,BLACK)
    annulus(p,elbow+[0,0,12],[0,0,1],9,3,3,BLUE)
    forearm_shell(p,side,elbow,wrist)
    for delta in [-5,5]:
        path=[shoulder+q(0,delta,10),q(105,238+delta,18),q(124,221+delta,22)]
        tube(p,path,1.6,BLUE if delta<0 else SILVER)
    # 顶部肘甲和前臂外侧的锐边，按正面参考单独保留折面。
    panel(p,[(side*x,y) for x,y in [(104,234),(124,232),(135,215),(119,212),(110,221)]],12,25,WHITE,2)
    p.sphere(wrist,11,BLACK)
    for d in [-7,7]:p.beam(wrist+q(d,4,4),wrist+q(d,-11,10),2.5,SILVER)
    return p.finish()


def hand(side):
    p=Part(f'05_{side:+d}_长指机械手')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    plate=[(side*x,y) for x,y in [(144,143),(167,147),(178,126),(174,109),(150,109),(138,125)]]
    panel(p,plate,28,49,BLACK,3)
    panel(p,[(side*x,y) for x,y in [(156,143),(167,140),(174,124),(168,113),(153,116)]],48,53,BLUE,2)
    annulus(p,q(160,128,54),[0,0,1],7,4,1,BLUE)
    annulus(p,q(160,128,55),[0,0,1],4,0,1,LIGHT)
    for i in range(4):
        x=144+i*9;y=113+abs(i-1.5)*2
        a,b,c,d=q(x,y,40),q(x-2,94-i%2*3,46),q(x-5,80-i%2*4,55),q(x-9,76-i%2*4,60)
        p.sphere(a,5.3,SILVER);p.beam(a,b,4.6,BLACK)
        p.beam(a+[0,0,4],b+[0,0,4],3.3,BLUE);p.sphere(b,4.6,BLACK)
        hull(p,[b+q(-3,1,-2),b+q(3,1,-2),b+q(-3,-2,4),b+q(3,-2,4),
                c+q(-2,0,-1),c+q(2,0,-1),c+q(-2,-1,3),c+q(2,-1,3)],BLUE)
        p.sphere(c,3.8,DARK)
        hull(p,[c+q(-3,2,-2),c+q(3,2,-2),c+q(3,-3,3),c+q(-3,-3,3),d],BLUE)
    a,b,c=q(141,129,39),q(125,116,46),q(127,100,57)
    p.sphere(a,6,BLACK);p.beam(a,b,5,BLUE);p.sphere(b,5,DARK);p.beam(b,c,3.5,BLUE)
    return p.finish()


def floating_module(side):
    p=Part(f'06_{side:+d}_背上双轨浮游模块')
    cx=side*91
    # R30、R32、R44至R60：只有两组纵向模块，上下分体装甲夹住场发生器。
    for y in [280,296]:
        vertices=[(cx-12,y-2,-61),(cx+12,y-2,-61),(cx+15,y-2,24),(cx+8,y-2,66),
                  (cx,y-1,78),(cx-8,y-2,66),(cx-15,y-2,24),
                  (cx-10,y+3,-56),(cx+10,y+3,-56),(cx+11,y+3,21),(cx,y+3,70)]
        hull(p,vertices,BLUE)
        p.beam([cx,y+4,-48],[cx,y+4,43],1.5,SILVER)
        p.beam([cx-10,y+2,-45],[cx-8,y+2,42],1,WHITE)
        p.beam([cx+10,y+2,-45],[cx+8,y+2,42],1,WHITE)
    for z in [-43,-15,16]:
        annulus(p,np.array([cx,288,z]),[0,0,1],6,3,5,BLACK)
        annulus(p,np.array([cx,288,z+3]),[0,0,1],4,2,1,LIGHT)
    p.box([cx-9,281,-57],[cx+9,296,-50],BLACK)
    p.sphere([cx,299,-43],7,WHITE)
    p.box([cx-4,299,-34],[cx+4,302,-29],LIGHT)
    return p.finish()


def chain():
    p=Part('07_背下方弯曲节链')
    p.beam([0,174,-31],[0,166,-27],3,DARK)
    last=None
    for i in range(24):
        t=i/23;c=np.array([8*math.sin(t*3.2),166-155*t,-27-18*t+6*math.sin(t*4)])
        if last is not None:p.beam(last,c,1.5,BLACK)
        radius=4*(1-t*.65);twist=i*.85
        corners=[]
        for dy in [-2,2]:
            for theta in np.arange(4)*math.pi/2+twist:
                corners.append(c+[radius*math.cos(theta),dy,radius*math.sin(theta)])
        hull(p,corners,DARK if i%2 else BLACK)
        last=c
    hull(p,[last+[-2,1,-2],last+[2,1,-2],last+[2,1,2],last+[-2,1,2],last+[0,-7,1]],BLACK)
    return p.finish()


def build():
    parts=[torso(),back(),wheel(-1),wheel(1),arm(-1),arm(1),hand(-1),hand(1),
           floating_module(-1),floating_module(1),chain()]
    allpoints=np.concatenate([p.p for p in parts]);low,high=allpoints.min(0),allpoints.max(0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states
    overlaps=[]
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            shared=np.intersect1d(encode(a.p),encode(b.p),assume_unique=True)
            if len(shared):overlaps.append(dict(first=a.name,second=b.name,shared_voxels=len(shared),
                classification='接合或待审干涉，保留完整部件，不冒充无穿模'))
    bounds={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts}
    for a in parts:
        for b in parts:
            if a.name.startswith('05_-') and b.name.startswith('05_+'):
                assert not len(np.intersect1d(encode(a.p),encode(b.p)))
    data=dict(name='hk3gtl-w02-19c-multiview-v2-20261110',title='理之律者 · 重装小兔19C · 多视角重制V2',
        candidate_version='19C-V2多视角重制',size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        center_blueprint=[0,218,5],controller=None,ports=[],animation_enabled=False,
        nominal_matrix_size_xzy=[649,493,303],matrix_layout_complete=False,
        approved=False,installed=False,game_verified=False,reference_fidelity_verified=False,
        palette_identity=dict(tier='HBV',name='构造蓝',color='#428DFF',runtime_voltage='WSV'),
        references=dict(count=60,official=32,fan_assistance=28,source_videos=3,manifest='../参考图清单.json'),
        component_bounds_blueprint=bounds,component_overlaps=overlaps,
        scope='普通理之律者19C；V1不继承为外形基线；无真理形态、十二翼或运动',
        source_conflicts=['60张参考是不同时间点、姿态与部位，不等于60个独立机位。',
            '官方画面优先校准配色和轮廓，二创模型只辅助背、侧、俯仰与局部连接，不继承红色重贴图。',
            '当前选择双臂下垂、长指伸展的静态姿态；不是把舞蹈动作定为官方待机。',
            '背上两组双轨模块与肩侧轮组依据新增参考重建；前臂和接合深度仍是体素转译，未达逐处复刻验收。',
            '当前只复刻19C主体，不包含布洛妮娅人物、摩托变形或完整W02工业船坞。',
            '现有纹理近似构造蓝身份色#428DFF，不声称每块材质与目标RGB完全相同。'])
    data['reference_correspondence']=[
        dict(component='尖盾躯干、橙色罩体与短鳍',references=['R01','R04','R10','R31'],status='官方校准轮廓；前后深度仍为体素转译'),
        dict(component='肩侧轮组',references=['R04','R07','R08','R11','R30','R31'],status='官方轮形与侧向朝向；含摩托变形辅助帧'),
        dict(component='重型曲臂与机械手',references=['R02','R04','R05','R12','R24','R31'],status='保留关节、装甲分片、蓝色长指；姿态作静态转译'),
        dict(component='背部轴系与节链',references=['R17','R18','R25','R26','R27','R28','R59'],status='官方为主、二创补遮挡；未验收逐处复刻'),
        dict(component='背上双轨模块',references=['R25','R28','R29','R32','R44','R46','R56','R58'],status='官方核对双模块身份；二创辅助观察分体结构')]
    return cube,data,parts
