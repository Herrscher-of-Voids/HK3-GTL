# -*- coding: utf-8 -*-
"""Gemini W04原案的独立静态转译：完整巨刃、鬼手、雷环及机甲雷龙，不按名义包络裁切。"""
from pathlib import Path
import math
import numpy as np
from scipy.interpolate import CubicSpline
from w02_19c_geometry_v4_20261110 import SolidPart,hull,tube,solid_annulus as annulus,basis,bezier

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_Gemini_俱利伽罗盘枢_B1_20261110'
LOG=ROOT/'logs/w04-gemini-dragon-b1-20261110'
BLACK='minecraft:deepslate_tiles'
DARK='minecraft:black_concrete'
RED='hk3gtl:voltage_machine_casing_hrv'
GOLD='minecraft:gold_block'
SILVER='minecraft:light_gray_concrete'
LIGHT='minecraft:sea_lantern'
GLASS='minecraft:red_stained_glass'
VIOLET='minecraft:magenta_stained_glass'
STATES=[BLACK,DARK,RED,GOLD,SILVER,LIGHT,GLASS,VIOLET]
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES=dict(zip(STATES,['玄黑分节装甲与机械甲脊','黑色凹槽及鸟居内构','HRV绯雷红#C93F63身份装甲及超导绕组',
    '金色导体、三巴纹及细边','刃口、液压拉杆与机械指节','绯红玻璃内的真实发光芯','雷翼栅格、绯雷锁链及炮束','少量绯紫电浆层']))
CENTER=np.array([0.,195.,0.])


class Part(SolidPart):
    def points(self,points,state):
        a=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(a):
            assert np.all(abs(a)<2048),'完整构件越过编码范围，只报错，不能裁切'
            self.chunks.append(a);self.values.append(np.full(len(a),IDS[state],np.uint8))


def octagon(rx,rz,cut=.23):
    return [(-rx+rx*cut,-rz),(rx-rx*cut,-rz),(rx,-rz+rz*cut),(rx,rz-rz*cut),
        (rx-rx*cut,rz),(-rx+rx*cut,rz),(-rx,rz-rz*cut),(-rx,-rz+rz*cut)]


def slab(p,outline,y0,y1,state):
    hull(p,[(x,y,z) for y in [y0,y1] for x,z in outline],state)


def loft(p,sections,state):
    for a,b in zip(sections[:-1],sections[1:]):hull(p,np.vstack([a,b]),state)


def trace(p,path,r,state):
    tube(p,np.asarray(path,float),r,state)


def polar(radius,angle,y=0):
    return np.array([radius*math.cos(angle),y,radius*math.sin(angle)])


def taper(p,path,widths,state,flat=1):
    sections=[]
    for i,(c,r) in enumerate(zip(path,widths)):
        axis=np.asarray(path[min(i+1,len(path)-1)])-path[max(0,i-1)]
        _,u,w=basis(axis)
        sections.append(np.array([np.asarray(c)+u*x*r+w*z*r*flat for x,z in octagon(1,1)]))
    loft(p,sections,state)


def pool():
    p=Part('01_鸣神托卡马克八角雷池')
    # 分层露台保留中央环形下沉槽；不把整个底盘实心填到68格。
    for rx,rz,low,high in [(348,282,0,6),(331,267,7,13),(312,250,14,19)]:
        outline=octagon(rx,rz)
        for a,b in zip(outline,np.roll(outline,-1,axis=0)):
            inner=np.array([a,b])*.79
            slab(p,[a,b,*inner[::-1]],low,high,BLACK)
    annulus(p,[0,13,0],[0,1,0],190,0,8,DARK)
    annulus(p,[0,21,0],[0,1,0],180,121,4,RED)
    annulus(p,[0,33,0],[0,1,0],174,132,3,GLASS)
    for r in [132,151,170]:
        annulus(p,[0,35,0],[0,1,0],r,r-3,3,LIGHT)
        annulus(p,[0,39,0],[0,1,0],r+1,r-4,2,GLASS)
    for r,y in [(190,43),(202,50),(214,56)]:
        annulus(p,[0,y,0],[0,1,0],r,r-8,5,BLACK)
        annulus(p,[0,y+3,0],[0,1,0],r-1,r-3,2,RED)
    for a in np.linspace(0,2*math.pi,16,endpoint=False):
        path=[polar(r,a,y) for r,y in [(124,30),(125,56),(146,68),(174,64),(190,45)]]
        trace(p,path,6,BLACK);trace(p,[v+[0,1,0] for v in path],2,RED)
        for r in [134,158,182]:
            c=polar(r,a,24);p.beam(c,c+[0,12,0],3,GOLD)
    for s in [-1,1]:
        for z in [-228,-154,-80,0,80,154,228]:
            p.box([s*275-22,18,z-12],[s*275+22,26,z+12],DARK)
            p.box([s*275-19,27,z-10],[s*275+19,30,z+10],RED)
            for dx in [-13,0,13]:p.box([s*275+dx-1,31,z-9],[s*275+dx+1,33,z+9],GOLD)
    return p.finish()


def torii():
    p=Part('02_三重鸟居与通用接口前庭')
    slab(p,[(-90,160),(90,160),(90,282),(-90,282)],0,7,BLACK)
    for z in range(167,281,5):
        y=8+(281-z)//10;p.box([-88,y-2,z],[88,y,z+4],BLACK)
        for s in [-1,1]:p.box([s*88-1,y,z],[s*88+1,y+1,z+4],RED)
    for z,top,width in [(265,48,64),(220,58,72),(180,68,80)]:
        for s in [-1,1]:
            x=s*(width-15)
            p.box([x-9,8,z-10],[x+9,13,z+10],BLACK)
            p.box([x-6,14,z-5],[x+6,top-4,z+5],RED)
            for dx in [-5,5]:p.box([x+dx-1,15,z+6],[x+dx+1,top-5,z+7],GOLD)
        p.box([-width+6,top-11,z-6],[width-6,top-7,z+6],GOLD)
        path=[[-width-8,top+5,z],[-width*.68,top+1,z],[0,top-1,z],[width*.68,top+1,z],[width+8,top+5,z]]
        trace(p,path,4.5,BLACK);trace(p,[np.array(v)+[0,-2,5] for v in path],1.3,RED)
        p.box([-9,top-20,z+5],[9,top-6,z+8],BLACK)
        p.box([-4,top-17,z+9],[4,top-9,z+9],GOLD)
    # 主鸟居下的主控神龛及两侧平整厢房，仅是外观位，不冒充已注册W04控制器。
    p.box([-9,10,260],[9,24,271],BLACK);p.box([-4,16,272],[4,23,272],RED)
    p.points([[0,20,273]],LIGHT)
    for s in [-1,1]:
        p.box([s*71-14,10,250],[s*71+14,32,269],BLACK)
        for dx in [-7,0,7]:
            p.box([s*71+dx-2,15,270],[s*71+dx+2,21,270],SILVER)
            p.box([s*71+dx-2,24,270],[s*71+dx+2,28,270],RED)
    return p.finish()


def sword():
    p=Part('03_倒悬涤罪七雷巨刃')
    stations=[(55,0,.55),(80,-4,9),(119,-8,20),(171,-6,30),(224,0,38),(265,1,42),(274,0,34)]
    sections=[]
    for y,x,r in stations:
        z=min(8,max(.55,r*.3))
        sections.append(np.array([[x-r,y,-z],[x+r,y,-z],[x+r,y,z],[x-r,y,z]]))
    loft(p,sections,DARK)
    for flank in [-1,1]:
        for (y,x,r),(yb,xb,rb) in zip(stations[:-1],stations[1:]):
            hull(p,[(x-r*.64,y,flank*8),(x+r*.7,y,flank*8),(x+r*.7,y,flank*11),(x-r*.64,y,flank*11),
                (xb-rb*.64,yb,flank*8),(xb+rb*.7,yb,flank*8),(xb+rb*.7,yb,flank*11),(xb-rb*.64,yb,flank*11)],RED)
        trace(p,[[x+r,y,flank*8] for y,x,r in stations],1.4,SILVER)
        trace(p,[[x-r*.7,y,flank*12] for y,x,r in stations],1.2,GOLD)
        trace(p,[[x+2,y,flank*12] for y,x,r in stations[1:]],2.2,LIGHT)
        trace(p,[[x+2,y,flank*14] for y,x,r in stations[1:]],3.1,GLASS)
    for y in range(116,264,12):
        r=float(np.interp(y,[a[0] for a in stations],[a[2] for a in stations]))
        p.box([-r-7,y-2,-10],[-r+1,y+2,10],BLACK)
        p.beam([-r-7,y,11],[-r+1,y,11],1,GOLD)
    annulus(p,[0,279,0],[0,1,0],65,19,8,BLACK)
    annulus(p,[0,284,0],[0,1,0],63,58,2,GOLD)
    for i in range(3):
        a=i*2*math.pi/3;c=polar(34,a,285)
        p.sphere(c,8,RED)
        path=[polar(34-17*t,a+.95*t,285) for t in np.linspace(0,1,15)]
        taper(p,path,np.linspace(7,1,len(path)),GOLD,.38)
    annulus(p,[0,293,0],[0,1,0],13,0,18,BLACK)
    p.box([-9,300,-9],[9,335,9],DARK)
    for y in range(302,335,5):
        annulus(p,[0,y,0],[0,1,0],12,9,2,RED)
        p.beam([-9,y,10],[9,y+4,10],.8,GOLD)
    annulus(p,[0,338,0],[0,1,0],16,0,4,RED)
    hull(p,[[-12,340,-10],[12,340,-10],[-12,340,10],[12,340,10],[0,343,0]],GOLD)
    return p.finish()


def ring_basis(index):
    # 原文只给倾角，未给倾斜轴；逐环采用X/Y/斜轴，作为公开转译参数。
    a=math.radians([18,-22,35][index]);b=math.radians([0,38,-20][index])
    rx=np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    mat=ry@rx
    return mat[:,0],mat[:,1],mat[:,2]


def thunder_ring(index):
    r=[110,145,175][index];u,v,n=ring_basis(index)
    p=Part(f'04_{index+1}_三巴纹雷鼓磁环_直径{2*r}')
    annulus(p,CENTER,n,r,r-12,10,BLACK)
    for d in [-6,6]:
        annulus(p,CENTER+n*d,n,r-1,r-4,2,RED)
        annulus(p,CENTER+n*(d+math.copysign(1,d)),n,r-10,r-12,1.8,GOLD)
    for j in range(12):
        a=j*math.pi/6;rad=u*math.cos(a)+v*math.sin(a);tangent=-u*math.sin(a)+v*math.cos(a)
        c=CENTER+rad*(r-6)
        annulus(p,c+n*8,n,10,0,8,RED)
        annulus(p,c+n*13,n,9,6,2,GOLD)
        p.sphere(c+n*15,3,LIGHT)
        for flank in [-1,1]:
            path=[c+rad*7+n*flank*7,c+rad*21+n*flank*14,c+rad*31+n*flank*11]
            taper(p,path,[4,3,.55],BLACK)
            trace(p,path,1,RED)
        if j%4==0:
            c2=CENTER+rad*(r-32)+n*12;p.sphere(c2,10,GOLD)
            path=[CENTER+(u*math.cos(a+t*.85)+v*math.sin(a+t*.85))*(r-32-24*t)+n*12 for t in np.linspace(0,1,14)]
            taper(p,path,np.linspace(9,.7,len(path)),GOLD,.35)
    return p.finish()


def tower(side):
    p=Part(f'05_{side:+d}_鬼面电容斜塔')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    slab(p,[(side*x,z) for x,z in [(251,-103),(330,-103),(348,-77),(348,-5),(273,16),(245,-25)]],18,48,BLACK)
    path=[q(300,48,-50),q(307,135,-64),q(290,227,-62),q(275,285,-44)]
    taper(p,path,[31,33,24,17],BLACK,.75)
    for y in range(66,253,20):
        x=300-(y-120)*.12;c=q(x,y,-38)
        p.box(c- [17,4,4],c+[17,4,6],RED)
        p.box(c- [12,1,5],c+[12,1,8],GOLD)
    # 鬼胄面甲：双斜眼、向下獠牙与向上长角。
    hull(p,[q(251,252,-22),q(291,259,-23),q(303,284,-25),q(276,308,-28),q(247,289,-23)],DARK)
    for x in [256,284]:
        p.beam(q(x,281,-18),q(x+8,288,-18),2,RED)
        taper(p,[q(x,266,-17),q(x+2,252,-6),q(x+5,243,-7)],[5,3,.5],GOLD)
    for x,z in [(254,-42),(291,-45)]:
        taper(p,[q(x,289,z),q(x-8,313,z-4),q(x-23,330,z-17)],[10,7,.55],RED)
    return p.finish()


def arm(side):
    p=Part(f'06_{side:+d}_建御雷机械臂与五指鬼手')
    z=85 if side<0 else -85
    q=lambda x,y,d:np.array([side*x,y,z+d],float)
    shoulder,elbow,wrist=q(286,176,-122),q(245,118,-68),q(188,177,0)
    for a,b,r in [(shoulder,elbow,22),(elbow,wrist,26)]:
        p.beam(a,b,r,BLACK)
        for d in [-18,18]:
            p.beam(a+[0,8,d],b+[0,8,d],3,SILVER)
            p.beam(a+[0,12,d],b+[0,12,d],1,RED)
    for c in [shoulder,elbow,wrist]:
        p.sphere(c,24,BLACK);annulus(p,c+[0,0,23],[0,0,1],20,12,4,RED)
        annulus(p,c+[0,0,26],[0,0,1],14,10,2,GOLD)
    taper(p,[elbow+(wrist-elbow)*t for t in [.12,.42,.72,.94]],[28,32,27,17],RED,.65)
    hull(p,[q(x,y,d) for x,y,d in [(182,163,-37),(182,210,-37),(182,216,28),(182,166,38),
        (153,163,-33),(153,210,-33),(153,216,25),(153,166,34)]],BLACK)
    hull(p,[q(x,y,d) for x,y,d in [(151,174,-28),(151,203,-28),(151,206,22),(151,173,29),
        (148,179,-22),(148,201,-22),(148,201,19),(148,178,23)]],RED)
    annulus(p,q(146,190,0),[side,0,0],15,10,4,GOLD)
    ends=[]
    for i,d in enumerate([-27,-9,9,27]):
        path=[q(163,208,d),q(149,231+(i%2)*5,d),q(126,246+(i%2)*6,d-2),q(114,231+(i%2)*4,d-4)]
        for j,(a,b) in enumerate(zip(path[:-1],path[1:])):
            p.beam(a,b,7-j*.8,BLACK);p.sphere(a,8,GOLD)
            p.beam(a+[0,2,0],b+[0,2,0],3.7,RED)
        taper(p,[path[-2],path[-1],path[-1]+[-side*7,-12,1]],[5,4,.5],SILVER)
        ends.append(path[-1]+[-side*7,-12,1])
    path=[q(170,178,33),q(148,166,46),q(124,176,49),q(116,194,44)]
    for a,b in zip(path[:-1],path[1:]):p.beam(a,b,8,BLACK);p.sphere(a,9,GOLD)
    trace(p,path,3,RED);ends.append(path[-1])
    return p.finish(),ends


def chains(side,ends):
    p=Part(f'07_{side:+d}_五指赤金超导锁链')
    u,v,n=ring_basis(2)
    for j,start in enumerate(ends):
        angle=math.radians((145 if side<0 else 10)+j*8)
        end=CENTER+(u*math.cos(angle)+v*math.sin(angle))*168+n*(12 if side<0 else -12)
        direction=end-start;_,across,up=basis(direction)
        route=[start+direction*t+np.array([0,-12*math.sin(math.pi*t),0]) for t in np.linspace(0,1,24)]
        trace(p,route,1.8,GLASS)
        for k,t in enumerate(np.linspace(.03,.97,max(3,round(np.linalg.norm(direction)/12)))):
            c=start+direction*t+[0,-12*math.sin(math.pi*t),0]
            tangent=direction/np.linalg.norm(direction);cross=across if k%2 else up
            shape=[c+tangent*6*math.cos(a)+cross*3.5*math.sin(a) for a in np.linspace(0,2*math.pi,17)]
            trace(p,shape,1.4,GOLD)
    return p.finish()


def dragon_curve():
    controls=np.array([[-112,75,-250],[-158,101,-215],[-122,153,-139],[15,169,-125],
        [136,144,-89],[157,192,-11],[92,257,22],[17,260,52],[0,242,90]],float)
    t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(controls,axis=0),axis=1))];t/=t[-1]
    curve=CubicSpline(t,controls,axis=0,bc_type='natural')
    return curve


def dragon_body():
    p=Part('08_俱利伽罗S形分节骨甲龙躯');curve=dragon_curve();stations=np.linspace(0,1,73)
    radii=lambda t:float(np.interp(t,[0,.12,.4,.65,.8,1],[3,12,25,31,30,20]))
    def section(t,scale=1):
        c=curve(t);_,u,w=basis(curve(t,1));r=radii(t)*scale
        return np.array([c+u*x*r+w*z*r*.83 for x,z in octagon(1,1)])
    loft(p,[section(t,.72) for t in stations],DARK)
    for a,b in zip(stations[:-1:2],stations[1::2]):
        loft(p,[section(a),section((a+b)/2,1.04),section(b)],BLACK)
        c=curve(a);axis,u,w=basis(curve(a,1));r=radii(a)
        annulus(p,c,axis,r*.76,r*.65,3,RED)
        # 腹甲沿局部下侧，背脊使用独立尖片，不包成一根光滑管。
        for flank in [-1,1]:
            trace(p,[curve(t)+np.array([flank*radii(t)*.56,-radii(t)*.55,0]) for t in np.linspace(a,b,4)],2.5,RED)
        spine=[c+[0,r*.72,0],c+[0,r+14,0]-axis*7,c+[0,r*.8,0]-axis*15]
        hull(p,[v+u*d for v in spine for d in [-3,3]],RED)
        trace(p,[spine[0],spine[1]],1,GOLD)
    # 下腹两条可见绯红高压导流缆。
    for side in [-1,1]:
        trace(p,[curve(t)+[side*radii(t)*.45,-radii(t)*.6,0] for t in np.linspace(.04,.96,90)],2,RED)
    sample=curve(np.linspace(0,1,1001));length=float(np.linalg.norm(np.diff(sample,axis=0),axis=1).sum())
    assert length>650,'完整龙躯中心线必须超过650格'
    return p.finish(),length


def dragon_wing(side):
    p=Part(f'09_{side:+d}_俱利伽罗折角机械雷翼')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    root=q(24,250,31);elbow=q(139,303,-26)
    trace(p,[root,elbow,q(260,308,-95)],7,BLACK)
    trace(p,[root+[0,4,0],elbow+[0,4,0],q(260,312,-95)],2,RED)
    tips=[q(260,308,-95),q(254,246,-53),q(229,204,-5),q(174,191,32)]
    for k,tip in enumerate(tips):
        shoulder=elbow if k<3 else root*.35+elbow*.65
        mid=shoulder*.35+tip*.65+[0,14,0]
        taper(p,[shoulder,mid,tip],[6,4,.55],BLACK,.7)
        trace(p,[shoulder+[0,2,0],mid+[0,2,0],tip],1.2,GOLD)
    for j,(a,b) in enumerate(zip(tips[:-1],tips[1:])):
        # 分块薄膜有真实破口；不把所有指骨之间糊成实心红平板。
        for t0,t1 in [(0,.29),(.32,.63),(.66,.98)]:
            c=elbow*.9+root*.1
            outera=a*(1-t0)+b*t0;outerb=a*(1-t1)+b*t1
            innera=c*.8+outera*.2;innerb=c*.8+outerb*.2
            hull(p,[v+[0,dy,0] for v in [innera,innerb,outerb,outera] for dy in [-1,1]],GLASS)
            trace(p,[innera,outera],1,RED)
        for t in [.28,.56,.8]:
            trace(p,[elbow*(1-t)+a*t,elbow*(1-t)+b*t],.8,RED)
    return p.finish()


def dragon_head():
    p=Part('10_俱利伽罗鬼角龙首与张开双颚')
    # 双颚分离，炮束从口腔中心伸出；两侧眼眶、鬃鳍和角冠保持可辨轮廓。
    sections=[]
    for z,rx,low,high in [(74,19,233,260),(96,31,233,271),(125,24,236,258),(155,14,231,246)]:
        sections.append(np.array([[-rx,low,z],[rx,low,z],[rx,high,z],[-rx,high,z]]))
    loft(p,sections,BLACK)
    jaw=[np.array([[-r,y-4,z],[r,y-4,z],[r,y+3,z],[-r,y+3,z]]) for z,r,y in [(83,20,218),(115,25,205),(154,12,211)]]
    loft(p,jaw,BLACK)
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        hull(p,[q(12,264,91),q(32,264,101),q(24,250,135),q(15,246,146),q(26,270,113)],RED)
        trace(p,[q(27,250,113),q(22,249,132),q(15,243,146)],2.8,LIGHT)
        trace(p,[q(29,251,113),q(24,250,132),q(17,244,146)],3,GLASS)
        taper(p,[q(23,265,91),q(38,304,70),q(28,330,52)],[10,7,.55],RED,.72)
        trace(p,[q(29,273,89),q(40,305,69),q(28,330,52)],1.2,GOLD)
        for x,y,z in [(30,247,94),(24,235,87)]:
            taper(p,[q(x,y,z),q(x+25,y+22,z-12),q(x+37,y+31,z-32)],[7,4,.5],RED,.5)
        for z in [119,133,145]:
            taper(p,[q(17-(z-119)*.14,234,z),q(15-(z-119)*.14,224,z+2)],[3,.5],SILVER)
            taper(p,[q(17-(z-119)*.14,213,z),q(15-(z-119)*.14,221,z+2)],[2.8,.5],SILVER)
        trace(p,[q(23,215,111),q(13,216,149)],2,RED)
    annulus(p,[0,226,143],[0,-.5,1],10,7,5,GOLD)
    return p.finish()


def dragon_claw(side):
    p=Part(f'11_{side:+d}_俱利伽罗扣环机械前爪')
    q=lambda x,y,z:np.array([side*x,y,z],float)
    path=[q(24,240,68),q(85,205,84),q(128,225,90)]
    for a,b in zip(path[:-1],path[1:]):
        p.beam(a,b,11,BLACK);p.beam(a+[0,5,2],b+[0,5,2],4,RED)
    for c in path:p.sphere(c,13,BLACK);annulus(p,c+[0,0,12],[0,0,1],11,8,3,GOLD)
    for d in [-12,0,12]:
        finger=[q(126,226,90+d),q(148,239,91+d),q(156,221,96+d),q(148,210,99+d)]
        trace(p,finger,4.5,BLACK);trace(p,[finger[-2],finger[-1]],2,SILVER)
    taper(p,[q(123,218,78),q(111,203,80),q(126,207,86)],[5,4,.5],SILVER)
    return p.finish()


def breath():
    p=Part('12_龙口绯雷螺旋等离子主炮束')
    start=np.array([0.,225.,147.]);end=np.array([0.,43.,231.]);axis,u,v=basis(end-start)
    p.beam(start,end,5,LIGHT)
    p.beam(start,end,9,GLASS)
    for phase in [0,math.pi]:
        route=[start+(end-start)*t+(u*math.cos(7*math.pi*t+phase)+v*math.sin(7*math.pi*t+phase))*10 for t in np.linspace(0,1,180)]
        trace(p,route,1.6,RED)
    annulus(p,end,[0,1,0],23,19,3,VIOLET)
    return p.finish()


def rear_anchor():
    p=Part('13_后方龙尾破渊锚座与尾部推进器')
    slab(p,[(-155,-282),(-70,-282),(-57,-236),(-83,-212),(-150,-221),(-166,-248)],14,34,BLACK)
    annulus(p,[-112,38,-249],[0,1,0],35,20,7,RED)
    annulus(p,[-112,43,-249],[0,1,0],32,24,3,GOLD)
    trace(p,[[-112,43,-249],[-112,62,-249],[-112,75,-250]],8,BLACK)
    for s in [-1,1]:
        x=-112+s*35
        taper(p,[[x,34,-251],[x,64,-252],[x-s*18,77,-250]],[8,7,2],BLACK,.7)
        trace(p,[[x,36,-260],[x,62,-260],[x-s*15,74,-255]],1.4,RED)
        annulus(p,[x,45,-268],[0,0,1],12,6,15,BLACK)
        annulus(p,[x,45,-277],[0,0,1],10,7,3,GOLD)
        annulus(p,[x,45,-278],[0,0,1],6,0,2,LIGHT)
        annulus(p,[x,45,-280],[0,0,1],7,0,2,GLASS)
    return p.finish()


def build():
    factories=[pool,torii,sword]+[lambda i=i:thunder_ring(i) for i in range(3)]+[lambda s=s:tower(s) for s in [-1,1]]
    parts=[]
    for factory in factories:
        part=factory();parts.append(part);print(part.name,len(part.p),flush=True)
    for s in [-1,1]:
        part,ends=arm(s);parts.extend([part,chains(s,ends)]);print(part.name,len(part.p),flush=True)
    body,length=dragon_body();parts.append(body);print(body.name,len(body.p),flush=True)
    for factory in [lambda:dragon_wing(-1),lambda:dragon_wing(1),dragon_head,lambda:dragon_claw(-1),lambda:dragon_claw(1),breath,rear_anchor]:
        part=factory();parts.append(part);print(part.name,len(part.p),flush=True)
    lo=np.min([p.p.min(0) for p in parts],axis=0);hi=np.max([p.p.max(0) for p in parts],axis=0);size=hi-lo+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        a=p.p-lo;cube[a[:,1],a[:,2],a[:,0]]=p.states
    conflicts=[
        '原文名义高343，同时指定Y=0至343；本版保留端点，不把344层压成343层。',
        '太刀局部X±42与直径130刀锷矛盾；刀锷半径65完整保留，冷却鳍片也不裁切。',
        '双塔分区Y48至268仅220格，正文却要求高260格；本版从48延伸至308，鬼角完整保留至330。',
        '三环倾角给出18/-22/35度但未指定轴、环宽与电极尺寸；本版轴矩阵、12格径向环宽、10格厚及31格鬼角电极均为转译参数，真实边界包含电极。',
        '第三雷环外伸电极超过343标高，实际最高体素Y366；该超界保留，没有向内缩放。龙翼中心线翼尖±260，实体骨梁截面略向外延伸。',
        '原文将520格翼展写为撑满697格总宽的构件之一；龙翼仍按±260设计，697横宽由双塔及底盘承担，不拉伸龙翼。',
        '标题称千米级，正文要求龙躯超过650格；本版按正文以S形中心线长度核验，不宣称实际超过1000格。',
        '原文只提供大部件范围，没有完整逐格坐标、机械指节与龙首模型；曲线控制点、关节姿态、膜面碎片、鸟居高度为本版明确转译，不宣称官方资产复刻。',
        '龙爪扣环、锁链钳环、龙躯穿环是原案接合；所有独立构件交叠另行输出，不移动构件掩盖未协调相交。',
        '光束、锁链和能量膜使用静态实体方块表达；无流动动画，无GPU球形转动，未注册或实装W04。']
    data=dict(name='hk3gtl-w04-gemini-dragon-b1-20261110',title='雷之律者 · 鸣霆·超导电磁天枢 · Gemini俱利伽罗盘枢B1',
        size=size.tolist(),blocks=int(np.count_nonzero(cube)),blueprint_bounds=dict(min=lo.tolist(),max=hi.tolist()),
        blueprint_to_export_offset_xyz=(-lo).tolist(),center_blueprint=[0,239,113],controller=None,ports=[],
        control_visual_blueprint=[0,20,273],interface_visual_count=12,display_version='B1',animation_enabled=False,
        approved=False,installed=False,game_verified=False,palette_identity=dict(name='绯雷红',color='#C93F63',tier='HRV',runtime_voltage='WSV'),
        nominal_reference_xzy=[697,565,343],no_nominal_clipping=True,design_original=False,author='Gemini原案／Codex体素转译',
        dragon_centerline_length=length,source_conflicts=conflicts,
        ring_axis_vectors=[ring_basis(i)[2].tolist() for i in range(3)],
        counts=dict(torii=3,magnets=16,thunder_rings=3,ring_diameters=[220,290,350],horn_electrode_pairs_per_ring=12,
            towers=2,mechanical_hands=2,fingers_per_hand=5,chains=10,dragon_wings=2,dragon_foreclaws=2),
        detail_views=dict(dragon=dict(center=[0,260,110],half=[74,85,83]),
            hand=dict(center=[-166,202,88],half=[95,85,86]),sword=dict(center=[0,202,0],half=[87,148,86])),
        summary='三重鸟居引入下沉托卡马克雷池；倒悬巨刃穿过三道三巴纹雷鼓，两侧鬼手机械臂以十道赤金锁链钳环，俱利伽罗以S形分节甲躯盘枢、展开折角雷翼并从张开的龙口喷出绯雷主炮。')
    return cube,data,parts


if __name__=='__main__':
    _,data,_=build();print(data['size'],data['blocks'])
