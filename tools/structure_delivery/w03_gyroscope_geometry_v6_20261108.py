# -*- coding: utf-8 -*-
"""Claude原文坐标转译，保留相交与越界，不为名义尺寸改形。"""
import math
import numpy as np
from audit_wonder_clipping_20261108 import LogicalGrid,PAD
from i42_prefabrication_geometry_v1_20261028 import Material
from build_wonder_boundary_repairs_20261108 import generic_audit

M=Material();W,H,D=673,321,529
B1=M.ATOMIC;B2=M.GOLD;B3='minecraft:purple_stained_glass';B4='minecraft:crying_obsidian'
B5='minecraft:purple_concrete';B7='gtceu:superconducting_coil[active=false]'
B8='minecraft:quartz_block';B9='minecraft:black_concrete';B10='minecraft:white_stained_glass'
STATES=sorted({B1,B2,B3,B4,B5,B7,B8,B9,B10,M.CONTROL,M.PORT,M.LIGHT})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={B1:'B1虚数锚定机壳的现有黑色金属板代理',B2:'B2金框、B5金色纹章线与B6实体链节代理',
 B3:'B3虚空玻璃与B6链芯的静态紫玻璃代理，非动态星空',B4:'B4裂隙的哭泣黑曜石真实材质代理',
 B5:'B5纹章的紫色底板代理',B7:'B7导流线圈的已有超导线圈代理',B8:'B8核心白金晶面的石英代理',
 B9:'B9奇点黑色标记，未实现吸光渲染',B10:'B10光环晶片的白玻璃代理',
 M.CONTROL:'南向主控占位，原蓝图坐标[336,30,484]',M.PORT:'所有位置均为通用接口，不沿用原文的输入输出分区',
 M.LIGHT:'朝圣阶梯灯具的已有海晶灯代理'}


def build():
    grid=LogicalGrid((H,D,W),PAD)
    def box(a,b,s):
        x,y,z=np.asarray(a,int);x1,y1,z1=np.asarray(b,int)
        assert x<=x1 and y<=y1 and z<=z1
        grid[y:y1+1,z:z1+1,x:x1+1]=IDS[s] if s else 0
    def points(p,s):
        p=np.unique(np.rint(p).astype(int).reshape(-1,3),axis=0)
        grid[p[:,1],p[:,2],p[:,0]]=IDS[s]
    def beam(a,b,s,r=0):
        a=np.array(a,float);b=np.array(b,float)
        for p in np.rint(np.linspace(a,b,max(2,int(np.max(np.abs(b-a))*2)+1))).astype(int):box(p-r,p+r,s)
    def plane(y,mask,s):
        a,b=np.where(mask);grid[y,a,b]=IDS[s]
    zz,xx=np.ogrid[:D,:W];X=xx-336;Z=zz-264
    # 十二级两格阶梯：完整底皮、台阶立面和顶面，内部按原文留空。
    for k in range(12):
        a,b=336-4*k,264-4*k;ellipse=(X/a)**2+(Z/b)**2<=1
        rim=ellipse&((X/(a-2))**2+(Z/(b-2))**2>=1)
        next_ellipse=(X/(a-4))**2+(Z/(b-4))**2<=1
        for y in (2*k,2*k+1):plane(y,rim,B1)
        plane(2*k+1,ellipse&~next_ellipse if k<11 else ellipse,B1)
        plane(2*k+1,rim,B2)
        if k==0:plane(0,ellipse,B1)
    platform=(X/292)**2+(Z/220)**2<=1
    glyph=np.abs(X)/80+np.abs(Z)/60
    plane(23,(glyph<=1)&platform,B5);plane(23,(glyph<=1)&(glyph>.91),B2)
    plane(23,platform&(((np.abs(X)<=1)&(np.abs(Z)>=60))|((np.abs(Z)<=1)&(np.abs(X)>=80))),B2)
    for i in range(16):
        th=(i+.5)*math.pi/8;length=40+(i*17)%51
        for j in range(length):
            radius=110+j;angle=th+.015*math.sin(j*.24+i)+.012*math.sin(j*.51)
            p=[336+radius*math.cos(angle),23,264+radius*.75*math.sin(angle)]
            q=np.rint(p).astype(int);r=0 if i%3 else 1
            box(q-[r,0,r],q+[r,0,r],B4)
    # 宽41格的南阶梯仍保持原文中轴，不为南塔挡视线而挪动。
    for z in range(484,529):
        y=round((528-z)*23/44);box([316,max(0,y-1),z],[356,y,z],B1)
        for x in (314,358):
            box([x,y+1,z],[x,y+3,z],B2)
            if (z-484)%8==0:box([x,y+4,z],[x,y+6,z],M.LIGHT)
    towers=[];ports=[];chains=[]
    for i in range(8):
        th=i*math.pi/4;cx=round(336+275*math.cos(th));cz=round(264+205*math.sin(th))
        zlocal,xlocal=np.ogrid[cz-12:cz+13,cx-12:cx+13];q=np.abs(xlocal-cx)+np.abs(zlocal-cz)
        for y in range(24,261):
            r=max(4,10-(y-24)//40)
            if y>=241:r=4*(260-y)/19
            mask=q<=r;zs,xs=np.where(mask);points(np.c_[xs+cx-12,np.full(len(xs),y),zs+cz-12],B1)
            edge=mask&((np.abs(xlocal-cx)<1)|(np.abs(zlocal-cz)<1))
            zs,xs=np.where(edge);points(np.c_[xs+cx-12,np.full(len(xs),y),zs+cz-12],B2)
            slit=mask&(q>=r-1)&(np.abs(np.abs(xlocal-cx)-np.abs(zlocal-cz))<1.1)
            if 45<=y<=200:
                zs,xs=np.where(slit);points(np.c_[xs+cx-12,np.full(len(xs),y),zs+cz-12],B4)
        box([cx,260,cz],[cx,260,cz],B9)
        inward=-np.array([math.cos(th),0,math.sin(th)]);tangent=np.array([-math.sin(th),0,math.cos(th)])
        for j in range(4):
            p=np.array([cx,222+8*(j//2),cz])+tangent*(-4 if j%2 else 4)
            beam(p,p+inward*12-[0,4,0],B2,1);beam(p+inward*12-[0,4,0],p+inward*9-[0,11,0],B2)
        for dx,dz in ((5,5),(-5,5),(-5,-5),(5,-5)):
            p=[cx+dx,34,cz+dz];box(p,p,M.PORT)
            ports.append(dict(id=f'锚塔{i+1}通用舱位{len(ports)%4+1}',pos=p,face='south' if dz>0 else 'north',group='generic',purpose='通用仓位；不按方位限制输入输出或能源'))
        towers.append(dict(id=i+1,base=[cx,24,cz],tip=[cx,260,cz],angle_degrees=i*45))
        for side in (-1,1):
            angle=th+side*.035;normal=np.array([math.cos(angle)/230,0,math.sin(angle)/170]);normal/=np.linalg.norm(normal)
            start=np.array([cx,230,cz])+tangent*side*3
            end=np.array([336+230*math.cos(angle),182,264+170*math.sin(angle)])+normal*16
            v=end-start;length=np.linalg.norm(v);v/=length
            u=np.cross(v,[0,1,0]);u/=np.linalg.norm(u);n=np.cross(v,u)
            beam(start,end,B3)
            for j,t in enumerate(np.arange(0,length+1,6)):
                center=start+min(t,length)*v;across=u if j%2 else n
                phi=np.linspace(0,2*math.pi,40)
                points(center+3.2*np.cos(phi[:,None])*v+2.0*np.sin(phi[:,None])*across,B2)
            chains.append(dict(tower=i+1,start=start.tolist(),end=end.tolist()))
    # 椭圆管采用最近点法求法向距离；几何范围来自230/170与截面，不取总包围盒裁切。
    theta=np.arctan2(Z/170,X/230);theta=np.broadcast_to(theta,(D,W)).copy()
    for _ in range(6):
        co=np.cos(theta);si=np.sin(theta);px=230*co;pz=170*si
        f=(px-X)*(-230*si)+(pz-Z)*(170*co)
        df=(230*si)**2+(170*co)**2+(px-X)*(-230*co)+(pz-Z)*(-170*si)
        theta-=np.divide(f,df,out=np.zeros_like(f),where=np.abs(df)>1e-8)
    co=np.cos(theta);si=np.sin(theta);nx=co/230;nz=si/170;norm=np.sqrt(nx*nx+nz*nz)
    distance=(X-230*co)*nx/norm+(Z-170*si)*nz/norm
    eligible=(np.abs(X)<250)&(np.abs(Z)<190)
    ribs=np.abs(np.angle(np.exp(1j*theta*72)))<.38
    for y in range(150,183):
        dy=abs(y-166);r=np.abs(distance)
        outer=eligible&(r<=16)&(r+dy<=27)
        inner=(r<14)&(dy<14)&(r+dy<23)
        shell=outer&~inner;plane(y,shell,B1)
        plane(y,shell&(ribs|((dy>=14)&(r>=27-dy-2))),B2)
        plane(y,eligible&(r<=5)&(dy<=5),B1);plane(y,eligible&(r<=4)&(dy<=4),B7)
    doors=[]
    for i in range(24):
        th=math.radians(7.5+15*i);n=np.array([math.cos(th)/230,0,math.sin(th)/170]);n/=np.linalg.norm(n)
        tangent=np.array([-n[2],0,n[0]]);p=np.array([336+230*math.cos(th),166,264+170*math.sin(th)])-16*n
        for dy in range(-12,13):
            for dx in range(-7,8):
                q=abs(dx)/7+abs(dy)/12
                if q<=1:
                    for depth in (0,-1):points([p+dx*tangent+[0,dy,0]+depth*n],B2 if q>.72 else B3)
        points([p+[0,13,0],p+[0,14,0]],B2)
        doors.append(dict(id=i+1,angle_degrees=7.5+15*i,center=p.tolist(),width=15,height=25))
    # 两个原位纵环，中心线148、实体13×13、每10度15×15箍；顶箍超过320也保留。
    for axis in ('x','z'):
        for y in range(12,321):
            dy=y-166
            for u in range(-154,155):
                rr=math.sqrt(u*u+dy*dy)
                if abs(rr-148)<=6:
                    for depth in range(-6,7):
                        p=[336+u,y,264+depth] if axis=='x' else [336+depth,y,264+u]
                        points([p],B4 if abs(rr-148)<=1 and abs(depth)<=1 else B1)
        for i in range(36):
            th=math.radians(i*10);radial=np.array([math.cos(th),math.sin(th),0]) if axis=='x' else np.array([0,math.sin(th),math.cos(th)])
            normal=np.array([0,0,1]) if axis=='x' else np.array([1,0,0]);center=np.array([336,166,264])+148*radial
            a,b=np.meshgrid(np.arange(-7,8),np.arange(-7,8));mask=(np.abs(a)==7)|(np.abs(b)==7)
            points(center+a[mask,None]*radial+b[mask,None]*normal,B2)
    for z in (110,418):
        box([324,154,z-12],[348,178,z+12],B2)
        box([326,156,z-10],[346,176,z+10],None)
        # 原文接合舱只规定外形，保持中空，不挪动接触位置。
        p=[348,166,z+12 if z==110 else z-12];box(p,p,M.PORT)
        ports.append(dict(id=f'接合舱{z}通用舱位',pos=p,face='south' if z==110 else 'north',group='generic',purpose='原维护位仍为通用接口'))
    # 六根5×5支撑保留，明确不为40格净空条款自行删梁。
    for a,b in [([356,166,264],[484,166,264]),([316,166,264],[188,166,264]),
                ([336,166,284],[336,166,412]),([336,166,244],[336,166,116]),
                ([336,186,264],[336,314,264]),([336,146,264],[336,18,264])]:beam(a,b,B2,2)
    for y in range(146,187):
        q=np.abs(X)+abs(y-166)+np.abs(Z)
        plane(y,q==20,B8);plane(y,(q==20)&((X==0)|(Z==0)|(y==166)),B2)
        plane(y,(q>=18)&(q<=19),B3)
        # 核心空腔是明确几何，支撑只到六个顶点。
        a,b=np.where((q>=2)&(q<=17));grid[y,a,b]=0
        plane(y,q<=1,B9)
    R=np.sqrt(X*X+Z*Z);plane(230,(R>=38)&(R<=40),B10)
    for i in range(24):
        th=i*math.pi/12;beam([336+40*math.cos(th),230,264+40*math.sin(th)],
            [336+46*math.cos(th),236,264+46*math.sin(th)],B2)
    box([333,314,263],[339,320,265],B2);box([335,314,261],[337,320,267],B2);points([[336,320,264]],B9)
    # 南侧尖拱与两侧方尖碑，完全保留原坐标及南锚塔遮挡。
    for x in range(306,367):
        top=round(64-36*(abs(x-336)/30)**1.6)
        for y in range(24,top+1):box([x,y,480],[x,y,484],B2 if top-y<3 or abs(x-336)>=28 else B1)
    for x in (300,372):
        box([x-3,24,478],[x+3,58,484],B1)
        for dx in (-3,3):box([x+dx,24,484],[x+dx,57,484],B2)
        points([[x,58,481]],B9)
    for y in range(24,37):
        for x in range(330,343):
            q=abs(x-336)+abs(y-30)
            if q<=6:box([x,y,484],[x,y,484],B2 if q>=5 else B5)
    control=[336,30,484];box(control,control,M.CONTROL)
    for dx in (-26,-21,-16,-11,11,16,21,26):
        p=[336+dx,30,484];box(p,p,M.PORT)
        ports.append(dict(id=f'正门通用舱位{dx:+}',pos=p,face='south',group='generic',purpose='通用仓位，不固定输出'))
    full=grid.array;occupied=full!=0;low=[];high=[]
    for axis in range(3):
        a=np.flatnonzero(np.any(occupied,axis=tuple(j for j in range(3) if j!=axis)));low.append(int(a[0]));high.append(int(a[-1])+1)
    assert all(a>0 and b<full.shape[i] for i,(a,b) in enumerate(zip(low,high))),'安全域不足；拒绝裁切'
    cube=full[tuple(slice(a,b) for a,b in zip(low,high))].copy();origin=[low[2]-PAD,low[0]-PAD,low[1]-PAD];offset=-np.array(origin)
    for item in ports:item['pos']=(np.array(item['pos'])+offset).tolist()
    data=dict(key='w03',name='hk3gtl-w03-eight-anchor-gyroscope-v6-20261108',candidate_version='V6',
        title='空之律者 · 穹界·虚数锚定环 · 八锚穹仪（Claude原案）',size=[cube.shape[2],cube.shape[0],cube.shape[1]],
        nominal_size_xyz=[673,321,529],blueprint_bounds_xyz=dict(min=origin,max=[high[2]-PAD-1,high[0]-PAD-1,high[1]-PAD-1]),
        blueprint_to_export_offset_xyz=offset.tolist(),controller=(np.array(control)+offset).tolist(),controller_face='south',ports=ports,
        zones=[dict(name='水平椭圆主环与24门',pos=[336,166,94]),dict(name='双轴纵环与天顶冠',pos=[336,314,264]),dict(name='菱形律者核心',pos=[336,166,264])],
        paths=[],pipe_routes=[],target_voltage='CIV',character='西琳',towers=towers,chains=chains,doors=doors,
        description='十二级椭圆基台、八根锚塔和十六条真实链节拉住Y166水平椭圆主环；24扇菱形门沿内缘排列，两个半径148的正交纵环包围六向支撑的菱形核心，Y230白金光环悬空。',
        purpose='严格保留负责人转交Claude原稿的主要坐标、尺寸及相交，不为名义673×529×321裁切；B1–B10用现有方块代理，动态演出与新方块注册待后续实装。')
    return cube,data


def audit(c,data):
    check=generic_audit(c,data,STATES)
    assert len(data['towers'])==8 and len(data['chains'])==16 and len(data['doors'])==24
    assert data['controller']==[336,30,484] and data['controller_face']=='south'
    assert data['size']==[673,322,529],data['size']
    assert all(p['outer_clear']==5 for p in check['port_checks'])
    check.update(source_author='Claude Opus 5.5（负责人转交署名）',no_nominal_clipping=True,nominal_size_xyz=[673,321,529],
        blueprint_bounds_xyz=data['blueprint_bounds_xyz'],tower_count=8,chain_count=16,door_count=24,ring_count=3,
        core_center=[336,166,264],ring_cross_section=[33,33],vertical_ring_radius=148,static_only=True,
        beauty_first_exception=dict(scope='W01–W15',mandatory_casing_dominance=False,numeric_progression_required=False),
        source_conflicts_preserved=['纵环15×15金箍保留到Y321，实际高度322，名义高度321不作裁切窗。',
            '南锚塔[336,24～260,469]仍在正门与中心之间，不移动来消除视线遮挡。',
            '六根5×5支撑梁按原文保留，未为40格净空条款删梁。',
            '核心最外层完整白金面仍保留；不自行开窗来展示里面的玻璃与奇点。'],
        not_verified=['外观候选未批准或部署；新B1–B10专用机壳、CTM、动态星空、旋转纵环、门内武器、粒子与天顶光柱均未实装。',
            '保持原文静态方块与预案分层；本轮没有改动游戏渲染器、隐藏实体方块、Pattern、配方、区块加载或性能逻辑。'])
    return check
