# -*- coding: utf-8 -*-
"""Gemini 2.0曲线翼、双轨桁架与深渊反应池；旧候选保持原样。"""
import math
import numpy as np
from w03_celestial_geometry_v3_20261107 import (M,STATES,IDS,WHITE,PURPLE,MAGENTA,ORANGE,COIL,W,H,D,audit as prior_audit)

ROLES={s:'Gemini 2.0静态实体构件，沿用目标增强版3.0已有方块资源' for s in STATES}
ROLES.update({WHITE:'圣白装甲、弧形翼刃和分体矛刃',M.GOLD:'窄镶边、交叉桁架、矛脊与舰桥护栏',
    M.ATOMIC:'分块基座、空间飘带与核心黑框',MAGENTA:'三层八面体壳、沿轨旋转晶体与能量管',
    M.CONTROL:'V字舰桥居中主控占位',M.PORT:'八个通用接口，不区分输入输出'})


def build():
    c=np.zeros((H,D,W),np.uint8);zz,xx=np.ogrid[:D,:W];X=xx-336;Z=zz-264
    def box(a,b,s):
        a=np.asarray(a,int);b=np.asarray(b,int)
        assert np.all(a>=0) and np.all(b<[W,H,D]) and np.all(a<=b),(a,b)
        x,y,z=a;x1,y1,z1=b;c[y:y1+1,z:z1+1,x:x1+1]=IDS[s] if s else 0
    def points(p,s):
        p=np.unique(np.rint(np.asarray(p)).astype(int),axis=0)
        assert np.all(p>=0) and np.all(p<[W,H,D]),(p.min(0),p.max(0))
        c[p[:,1],p[:,2],p[:,0]]=IDS[s]
    def beam(a,b,s,r=1):
        a=np.asarray(a,float);b=np.asarray(b,float)
        for p in np.rint(np.linspace(a,b,max(2,int(max(abs(b-a))*2)+1))).astype(int):
            box(p-r,p+r,s)
    def frame(v):
        v=np.asarray(v,float);v/=np.linalg.norm(v);ref=[0,1,0] if abs(v[1])<.9 else [0,0,1]
        u=np.cross(v,ref);u/=np.linalg.norm(u);return v,u,np.cross(v,u)
    def ellipse(t,rx=210,ry=113,center=(336,159,264),tilt=None):
        if tilt is None:return np.array(center)+[rx*math.cos(t),ry*math.sin(t),0]
        return np.array(center)+[rx*math.cos(t),ry*math.sin(t)*math.sin(tilt),ry*math.sin(t)*math.cos(tilt)]

    # 深45格的阶梯反应池；外圈保留分块承重装甲。
    for y in range(50):
        shrink=(y//8)*7;ax=250-shrink;az=225-shrink
        octagon=(np.abs(X)<=ax)&(np.abs(Z)<=az)&(np.abs(X)/ax+np.abs(Z)/az<=1.45)
        radius=100+min(5,(max(y,5)-5)//8)*8
        hole=(X*X+Z*Z<radius*radius) if y>=5 else np.zeros((D,W),bool)
        c[y][octagon&~hole]=IDS[M.ATOMIC if y%8 else M.STRESS]
        if y in (5,14,23,32,41,49):
            r=np.sqrt(X*X+Z*Z);rim=(r>=radius)&(r<radius+2)
            c[y][rim]=IDS[M.GOLD if y%2 else WHITE]
    R=np.sqrt(X*X+Z*Z)
    for radius in (28,48,68,88):
        band=(R>=radius-2)&(R<=radius+2)
        c[4][band]=IDS[M.LIGHT];c[5][band]=IDS[MAGENTA if radius%40 else M.GOLD]
    ribs=[]
    for i in range(48):
        th=i*math.pi/24;vx,vz=math.cos(th),math.sin(th)
        end=min(248/max(abs(vx),.001),223/max(abs(vz),.001),1.45/(abs(vx)/250+abs(vz)/225))
        for r in np.arange(144,end+.01,.7):
            for y in range(49,-1,-1):
                ax=250-(y//8)*7;az=225-(y//8)*7
                if abs(r*vx)<=ax and abs(r*vz)<=az and abs(r*vx)/ax+abs(r*vz)/az<=1.45:break
            offsets=np.arange(-4,5)
            for surface_y in range(max(0,y-7),y+1):
                p=np.c_[336+r*vx-offsets*vz,np.full(9,surface_y),264+r*vz+offsets*vx]
                points(p,WHITE);points(p[[0,-1]],M.GOLD)
        ribs.append(dict(angle_deg=i*7.5,width=8))
    anchors=[]
    for i in range(8):
        th=(i+.5)*math.pi/4;v=np.array([math.cos(th),math.sin(th)])
        root=np.array([336,264])+v*[205,183]
        for y in range(12,77):
            cx,cz=root-(y-12)*.30*v
            a=np.abs((xx-cx)*v[0]+(zz-cz)*v[1]);b=np.abs(-(xx-cx)*v[1]+(zz-cz)*v[0])
            mask=(a<=8)&(b<=8);c[y][mask]=IDS[M.ATOMIC]
            c[y][mask&(a>5)]=IDS[WHITE];c[y][mask&(b>6)]=IDS[M.GOLD if y%18<2 else M.ROBUST]
        anchors.append(dict(id=i+1,root=root.tolist(),height=65))

    # 两根窄轨之间保留16个空气体素；三环均用独立轨道与周期性X桁架。
    rings=[]
    def truss_ring(radius,tilt,outer=False):
        center=np.array([336.,159.,264.]);rx,ry=(210,113) if outer else (radius,radius)
        U=np.array([1.,0,0]);V=np.array([0.,1,0]) if outer else np.array([0,math.sin(tilt),math.cos(tilt)])
        N=np.cross(U,V);radial_half=13 if outer else 5
        offsets,depths=np.meshgrid(np.arange(-radial_half,radial_half+1),np.arange(-2,3));offsets=offsets.ravel();depths=depths.ravel()
        rail_cells=[]
        for th in np.linspace(0,2*math.pi,2201):
            radial=math.cos(th)*U+math.sin(th)*V;p=center+rx*math.cos(th)*U+ry*math.sin(th)*V
            for side in (-10,11):
                q=p+offsets[:,None]*radial+(depths+side)[:,None]*N
                if outer:rail_cells.append(np.rint(q).astype(np.int16))
                points(q,WHITE)
                edge=np.abs(offsets)>=radial_half-1;points(q[edge],M.GOLD)
                groove=(np.abs(offsets)<3)&(depths==(-2 if side<0 else 2));points(q[groove],M.ATOMIC)
        color_share=None
        if outer:
            cells=np.unique(np.concatenate(rail_cells),axis=0);count=np.bincount(c[cells[:,1],cells[:,2],cells[:,0]],minlength=len(STATES)+1)
            color_share={s:float(count[IDS[s]]/len(cells)) for s in (WHITE,M.GOLD,M.ATOMIC)}
            assert color_share[WHITE]>=.75 and color_share[M.GOLD]<=.2,color_share
        for i in range(24):
            th=i*math.pi/12;radial=math.cos(th)*U+math.sin(th)*V
            p=center+rx*math.cos(th)*U+ry*math.sin(th)*V
            beam(p-7*radial-8*N,p+7*radial+9*N,M.GOLD,0)
            beam(p+7*radial-8*N,p-7*radial+9*N,M.GOLD,0)
            beam(p-8*N,p+9*N,MAGENTA,0)
            if outer:beam(p-5*radial-6*N,p+5*radial-6*N,COIL,0)
        rings.append(dict(radius_x=rx,radius_y=ry,tilt_from_horizontal_deg=None if outer else math.degrees(tilt),
            rail_offsets=[-10,11],rail_depth=5,clear_air_cells=16,truss_count=24,rail_color_share_before_crossing_parts=color_share))
    truss_ring(210,None,True);truss_ring(142,math.radians(24));truss_ring(91,math.radians(-42))
    # 浮游晶柱与环保持12格几何间距；上下极点向纵深倾斜以守住321格总高。
    cannons=[]
    for i in range(24):
        th=i*math.pi/12;p=ellipse(th)
        v,u,w=frame([math.cos(th),.65*math.sin(th),.76*math.sin(th)])
        a,b=np.meshgrid(np.arange(-5,6),np.arange(-5,6));a=a.ravel();b=b.ravel()
        for t in np.linspace(0,44,100):
            half=5*(1-abs(t-22)/22);mask=np.abs(a)+np.abs(b)<=half+.1
            q=p+(26+t)*v+a[mask,None]*u+b[mask,None]*w
            points(q,WHITE)
            edge=(np.abs(a[mask])>half-1.05)&(np.abs(b[mask])<.1);points(q[edge],M.GOLD)
            if 12<t<32:points([p+(26+t)*v],MAGENTA)
        cannons.append(dict(id=i+1,length=45,maximum_width=10,minimum_ring_gap=12))

    # 十根二次贝塞尔翼刃，根部菱形12×6，末端收为单格尖端。
    feathers=[]
    for i in range(10):
        y=90+i*2;x=336-210*math.sqrt(1-((y-159)/113)**2)-13-25
        start=np.array([x,y,245+13*math.sin(i*.8)])
        tip=np.array([i*6.2,183+i*14.3,245+35*math.sin(i*.7)])
        control=start*.48+tip*.52+np.array([-23,-9,18*math.sin(i*.8)+27*i/9])
        a,b=np.meshgrid(np.arange(-6,7),np.arange(-3,4));a=a.ravel();b=b.ravel()
        for t in np.linspace(0,1,601):
            p=(1-t)**2*start+2*(1-t)*t*control+t*t*tip
            tangent=2*(1-t)*(control-start)+2*t*(tip-control);v,u,w=frame(tangent)
            taper=(1-t)**.55;metric=np.abs(a)/6+np.abs(b)/3
            mask=metric<=taper+.025
            q=p+a[mask,None]*u+b[mask,None]*w;points(q,WHITE)
            # 单侧金脊，保留主体圣白；不再包满整片金边。
            gold=(np.abs(a[mask])<.1)&(b[mask]>=max(0,3*taper-1));points(q[gold],M.GOLD)
        t=np.linspace(0,1,1001)[:,None];curve=(1-t)**2*start+2*(1-t)*t*control+t*t*tip
        length=float(np.linalg.norm(np.diff(curve,axis=0),axis=1).sum())
        feathers.append(dict(id=i+1,curve='quadratic_bezier',start=start.tolist(),control=control.tolist(),tip=tip.tolist(),
            root_diamond_cross_section=[12,6],suspended_root_gap=25,curve_length=length))

    # 两条非闭合空间飘带；晶体沿轨递减、旋转，不再随机散布。
    ribbons=[];cubes=[]
    def ribbon_curve(t,phase):
        return np.array([450+222*t+12*math.sin(2*math.pi*t+phase)*math.sin(math.pi*t),
            58+232*t+18*math.sin(3*math.pi*t+phase)*math.sin(math.pi*t),
            264+79*math.sin(2.4*math.pi*t+phase)])
    for i,phase in enumerate((0,math.pi)):
        for t in np.linspace(0,1,1601):
            p=ribbon_curve(t,phase);tangent=ribbon_curve(t+.0001,phase)-ribbon_curve(t-.0001,phase)
            v,u,w=frame(tangent);a,b=np.meshgrid(np.arange(-12,13),np.arange(-3,4));a=a.ravel();b=b.ravel()
            taper=min(1,(1-t)*20+.01,max(0,(W-1-p[0])/(12*abs(u[0])+3*abs(w[0])+.001)))
            q=p+taper*(a[:,None]*u+b[:,None]*w)
            points(q,M.ATOMIC);points(q[np.abs(a)>10],M.GOLD)
            points(q[(np.abs(a)<2)&(b==-3)],PURPLE)
        ribbons.append(dict(id=i+1,curve='sinusoidal_3d_open_stream',phase=phase,cross_section=[24,6],closed=False))
        for j,t in enumerate(np.linspace(.06,.94,12)):
            size=int(round(28-22*j/11));p=ribbon_curve(t,phase)
            v,u,w=frame(ribbon_curve(t+.001,phase)-ribbon_curve(t-.001,phase));p=p+u*(22 if i==0 else -22)
            angles=np.radians([15+j*11,10+j*17,18+j*23]);ax,ay,az=angles
            rx=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
            ry=np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
            rz=np.array([[math.cos(az),-math.sin(az),0],[math.sin(az),math.cos(az),0],[0,0,1]])
            rotation=rz@ry@rx;half=(size-1)/2;extent=np.abs(rotation).sum(1)*half
            p=np.minimum(np.maximum(p,extent+1),np.array([W-2,H-2,D-2])-extent)
            r=int(math.ceil(size*.9));offsets=np.indices((2*r+1,)*3).reshape(3,-1).T-r
            local=offsets@rotation;q=np.max(np.abs(local),axis=1)
            points(p+offsets[(q<=half)&(q>=half-1.25)],MAGENTA)
            cubes.append(dict(ribbon=i+1,position_on_curve=float(t),size=size,euler_degrees=np.degrees(angles).tolist(),center=p.tolist()))

    # 六柄分体宽刃矛；80格剑刃、10格断口、18格八面水晶与开放C形护手。
    core=np.array([336.,170.,264.]);spears=[]
    def octa(center,radius,state,thickness=None):
        r=int(math.ceil(radius));off=np.indices((2*r+1,)*3).reshape(3,-1).T-r
        q=np.abs(off).sum(1);mask=q<=radius
        if thickness is not None:mask&=q>radius-thickness
        points(np.asarray(center)+off[mask],state)
    for i in range(6):
        th=(i+.25)*math.pi/3;v,u,w=frame([math.cos(th),.22*math.sin(th*2),math.sin(th)])
        tip=core+70*v;a,b=np.meshgrid(np.arange(-18,19),np.arange(-4,5));a=a.ravel();b=b.ravel()
        for t in np.linspace(0,79,180):
            half=max(.01,18*min(t/63,(95-t)/16));thick=4*min(1,t/45)
            mask=np.abs(a)/half+np.abs(b)/max(.1,thick)<=1
            q=tip+t*v+a[mask,None]*u+b[mask,None]*w;points(q,WHITE)
            ridge=(np.abs(a[mask])<=1)&(b[mask]>=max(0,thick-1));points(q[ridge],M.GOLD)
        octa(tip+99*v,9,MAGENTA)
        for side in (-1,1):
            last=None
            for phi in np.linspace(-math.pi*.72,math.pi*.72,150):
                p=tip+(113+14*math.sin(phi))*v+side*(16+10*math.cos(phi))*u
                if last is not None:beam(last,p,M.GOLD,1)
                last=p
        for t in np.linspace(122,204,200):
            p=tip+t*v;r=max(0,3*(204-t)/82);aa,bb=np.meshgrid(np.arange(-3,4),np.arange(-3,4));mask=aa*aa+bb*bb<=r*r+.05
            points(p+aa[mask,None]*u+bb[mask,None]*w,M.ATOMIC)
            if t<196:points([p+r*(math.cos(t*.17)*u+math.sin(t*.17)*w)],M.GOLD)
        spears.append(dict(id=i+1,tip=tip.tolist(),axis=v.tolist(),length=205,blade_length=80,gap=10,crystal_diameter=18))
    vertices=[core+v for v in ([54,0,0],[-54,0,0],[0,57,0],[0,-57,0],[0,0,54],[0,0,-54])]
    for i,a in enumerate(vertices):
        for b in vertices[i+1:]:
            if np.dot(a-core,b-core)==0:
                beam(a,b,M.ATOMIC,2);beam(a+[0,0,-2],b+[0,0,-2],M.GOLD,0)
    for radius in (43,32,21):octa(core,radius,MAGENTA,1.5)
    for y in range(158,183):
        r=X*X+Z*Z+(y-170)**2;c[y][r<=12**2]=IDS[ORANGE];c[y][r<=8**2]=IDS[M.LIGHT]

    # 轻薄天顶冠冕，保留真实最高层而不另加无功能的高度标记。
    for i in range(12):
        th=i*math.pi/6;p=np.array([336+54*math.cos(th),299,264+54*math.sin(th)])
        for y in range(294,321):
            half=5*(1-abs(y-307)/14);a,b=np.meshgrid(np.arange(-5,6),np.arange(-5,6));mask=np.abs(a)+np.abs(b)<=max(0,half)
            points(np.c_[p[0]+a[mask],np.full(mask.sum(),y),p[2]+b[mask]],WHITE)
        beam(p+[0,-3,0],p+[0,16,0],M.GOLD,0)
    beam([336,229,264],[336,304,264],ORANGE,1)

    # V字双塔舰桥与24格白色天桥，主控嵌在黑金祭坛前面。
    box((324,47,0),(347,49,264),WHITE)
    for x in (323,348):beam([x,51,0],[x,51,264],M.GOLD,0)
    for side in (-1,1):
        for y in range(20,56):
            t=(y-20)/35;cx=336+side*(25+18*t);cz=72-43*t
            box(np.rint([cx-4,y,cz-4]),np.rint([cx+4,y,cz+4]),M.ATOMIC)
            box(np.rint([cx-3,y,cz-5]),np.rint([cx+3,y,cz-5]),WHITE)
            points([[cx+side*4,y,cz-5]],M.GOLD)
        beam([336+side*22,24,35],[336+side*43,55,29],WHITE,2)
    box((314,22,35),(358,33,41),M.ATOMIC)
    for y in range(22,34):
        for x in range(330,343):
            if abs(x-336)+abs(y-27)<=5:c[y,35,x]=IDS[M.GOLD]
    beam([314,34,35],[358,34,35],M.GOLD,0)
    for x in (314,358):beam([x,22,35],[x,33,35],WHITE,0)
    control=[336,27,35];box(control,control,M.CONTROL);ports=[]
    for i,offset in enumerate((-18,-14,-10,-6,6,10,14,18)):
        p=[336+offset,27,35];box(p,p,M.PORT)
        ports.append(dict(id=f'舰桥通用舱位{i+1:02}',pos=p,face='north',group='generic',purpose='物品、流体或能源通用接口，不固定输入输出'))
    box((314,23,30),(358,32,34),None)
    # 四条池底导管分别接入两端设备，不留悬空的断头管。
    routes=[]
    for axis,span in [('x',86),('z',86)]:
        for side in (-1,1):
            a=[336,9,264];b=a.copy();a[0 if axis=='x' else 2]+=side*29;b[0 if axis=='x' else 2]+=side*span
            a,b=(a,b) if side>0 else (b,a)
            for p in (a,b):box(np.array(p)-2,np.array(p)+2,M.TURBINE)
            path=np.rint(np.linspace(a,b,58)).astype(int);points(path,M.GOLD)
            routes.append(dict(id=f'反应池{axis}{side:+}导管',start=a,end=b,path=path.tolist(),endpoint_state=M.TURBINE))
    # 后部线圈汇流节点延伸至总纵深边界，属于反应池设备而非空气扩边。
    beam([336,15,460],[336,38,524],M.ROBUST,2);octa([336,38,524],4,MAGENTA)
    box((333,12,457),(339,18,463),M.VENT)
    zones=[dict(name='双轨桁架三环与24枚浮游晶柱',pos=[336,159,264]),dict(name='秩序翼 · 十片曲线刀锋',pos=[90,180,264]),
        dict(name='虚数翼 · 双飘带与沿轨递减星流',pos=[560,200,264]),dict(name='六柄分体主矛与三层八面核心',pos=[336,170,264]),
        dict(name='45格深反应池与V字舰桥',pos=[336,35,200])]
    data=dict(key='w03',name='hk3gtl-w03-celestial-reforged-v4-20261107',candidate_version='V4',
        title='空之律者 · 穹界·虚数锚定环 · 曲翼深渊神殿（Gemini 2.0）',size=[W,H,D],controller=control,controller_face='north',
        ports=ports,zones=zones,paths=[dict(min=[314,23,30],max=[358,32,34])],pipe_routes=routes,target_voltage='CIV',
        appearance_voltage='原案圣白／黑紫',character='西琳',anchors=anchors,feathers=feathers,ribbons=ribbons,cubes=cubes,spears=spears,
        rings=rings,cannons=cannons,ribs=ribs,
        description='十片曲线菱形翼刃与两条黑紫空间飘带形成不对称双翼，沿轨旋转晶体由28格递减至6格。三重双轨桁架环、24枚浮游晶柱和六柄分体宽刃矛围住三层紫晶八面体，底部45格深反应池与V字双塔舰桥取代黑色实心台阶和白盒门。',
        purpose='Gemini 2.0改进意见的离线造型候选；保留V1～V3，不为递增门槛增料，不改为HCV主材，不新增方块或运行特效。')
    return c,data


def audit(c,data):
    result=prior_audit(c,data)
    # 复用逐格边界、主控净空、管路和旧电压基线核验，版本专属语义以本轮数据为准。
    result.update(feather_count=len(data['feathers']),ribbon_count=len(data['ribbons']),virtual_cube_count=len(data['cubes']),
        spear_count=len(data['spears']),ring_count=len(data['rings']),floating_cannon_count=len(data['cannons']),
        base_rib_count=len(data['ribs']),pool_depth=45,source_author='Gemini 2.0',
        source_geometry_conflicts=[
            '正八面体与旋转立方体不是同一几何。本版选择原文明确提出的正八面体黑金框及三层同心菱形壳，不伪称旋转方块变成八面体。',
            '选择六柄205格分体主矛的分支；不同时叠加另一个四柄300格方案。',
            '保持673×529×321总边界，主环采用420×226名义椭圆；上下浮游晶柱向纵深倾斜，避免45格晶柱越过建高。',
            '两道轨中心距21格，各厚5格，轨间含16个空气体素；保留24处X桁架与紫晶接管。',
            '翼刃由下至上严格递增长度，约160～220格，根部菱形截面12×6；实际体素与连续几何含离散误差。',
            '既有资源近似圣白黑紫；未注册新机壳、CTM、着色器或动态能量场。'],
        checks=['实际实体边界673×529×321；未用空气冒充尺寸。','十片非矩形二次贝塞尔翼刃，两条非闭合空间飘带，24枚沿轨递减旋转晶体。',
            '三环均为双轨与周期X桁架；24枚浮游晶柱替代贴环圆锥刺。','六柄80格宽刃、10格断口、18格晶体与C形护手的主矛。',
            '深45格阶梯反应池、48道白金散热肋与V字双塔舰桥。','八个通用接口齐平有背板和五格净空；四条池底导管两端连接设备。'],
        not_verified=['仅Gemini 2.0造型候选，HCV主材及既定规模递增尚未符合或获豁免；未批准、未部署。',
            '运行特效、动态、实体角色、成型、配方与8GB工况均未实现或验收。',
            '曲线控制点、倾角、分支方案与既有材质近似由本轮转译，文字不是逐格施工图。'])
    assert [v['size'] for v in data['cubes'][:12]]==sorted([v['size'] for v in data['cubes'][:12]],reverse=True)
    assert result['feather_count']==10 and result['ribbon_count']==2 and result['spear_count']==6
    assert all(a['curve_length']<b['curve_length'] for a,b in zip(data['feathers'],data['feathers'][1:]))
    # 池中心从顶缘到池底上方必须有连续45格空腔，避开天桥与设备路线。
    assert not np.any(c[5:50,264+20,336+55])
    assert c[49,264+139,336]==0 and c[49,264+140,336]!=0
    result.update(pool_depth_check_passed=True,pool_top_diameter=280,pool_clear_column=dict(x=391,z=284,min_y=5,max_y=49))
    return result


if __name__=='__main__':
    import json
    cube,data=build();v=audit(cube,data)
    print(json.dumps({k:v[k] for k in ('blocks','unique_materials','connectivity')},ensure_ascii=False))
