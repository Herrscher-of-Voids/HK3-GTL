# -*- coding: utf-8 -*-
"""Gemini文字原案几何转译；保留白金黑紫三环双翼，不为递增规则加料。"""
import json,math
from pathlib import Path
import numpy as np
from scipy import ndimage
from i42_prefabrication_geometry_v1_20261028 import Material
from structure_size_baseline import baselines

ROOT=Path(__file__).resolve().parents[2]
W,H,D=673,321,529
M=Material();WHITE='minecraft:quartz_block';PURPLE='minecraft:purple_concrete'
MAGENTA='minecraft:magenta_stained_glass';ORANGE='minecraft:orange_stained_glass'
COIL='gtceu:superconducting_coil[active=false]'
STATES=sorted({M.ATOMIC,M.ROBUST,M.CONTROL,M.PORT,M.LIGHT,M.GOLD,M.TURBINE,M.VENT,
    M.STRESS,WHITE,PURPLE,MAGENTA,ORANGE,COIL})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'Gemini原案中的实体机壳、承重骨架或能源视觉构件' for s in STATES}
ROLES.update({WHITE:'现有石英方块近似白金装甲；未新增专属机壳或CTM',M.ATOMIC:'黑色重型基座、黑翼及矛尾',
    M.GOLD:'金色边框、护手、冷却导管和王冠',MAGENTA:'紫红晶格、裂隙和分节环桥',ORANGE:'导流槽与中央瞳孔球体',
    COIL:'主环内缘暴露的真实超导线圈',M.CONTROL:'正前白金大门居中主控占位',M.PORT:'八个通用舱位，不按输入输出限制位置'})


def build():
    c=np.zeros((H,D,W),np.uint8);zz,xx=np.ogrid[:D,:W];X=xx-336;Z=zz-264
    def box(a,b,s):
        x,y,z=map(int,a);x1,y1,z1=map(int,b)
        assert 0<=x<=x1<W and 0<=y<=y1<H and 0<=z<=z1<D,(a,b)
        c[y:y1+1,z:z1+1,x:x1+1]=IDS[s] if s else 0
    def points(p,s):
        p=np.unique(np.rint(p).astype(int),axis=0)
        valid=np.all((p>=0)&(p<np.array([W,H,D])),axis=1);p=p[valid]
        c[p[:,1],p[:,2],p[:,0]]=IDS[s]
    def beam(a,b,s,r=1):
        a=np.asarray(a,float);b=np.asarray(b,float)
        for x,y,z in np.rint(np.linspace(a,b,max(2,int(max(abs(b-a))*2)+1))).astype(int):
            box(np.maximum([x-r,y-r,z-r],0),np.minimum([x+r,y+r,z+r],[W-1,H-1,D-1]),s)
    def frame(v):
        v=np.asarray(v,float);v/=np.linalg.norm(v);ref=[0,1,0] if abs(v[1])<.9 else [0,0,1]
        u=np.cross(v,ref);u/=np.linalg.norm(u);return v,u,np.cross(v,u)
    def blade(tip,v,length,width=12):
        v,u,w=frame(v);tip=np.asarray(tip,float);a,b=np.meshgrid(np.arange(-width,width+1),np.arange(-width,width+1));ab=np.c_[a.ravel(),b.ravel()]
        for t in range(length+1):
            p=tip+t*v
            if t<48:
                r=width*t/48;mask=np.abs(ab).sum(1)<=r
                points(p+ab[mask,0,None]*u+ab[mask,1,None]*w,WHITE)
                edge=mask&(np.abs(ab).sum(1)>r-1.3);points(p+ab[edge,0,None]*u+ab[edge,1,None]*w,M.GOLD)
            else:
                mask=(np.abs(ab[:,0])<=2)&(np.abs(ab[:,1])<=2)
                points(p+ab[mask,0,None]*u+ab[mask,1,None]*w,M.ATOMIC)
                if t>length-45:
                    r=max(3,width*(length-t)/45)
                    mask=((np.abs(ab[:,0])<=1)&(np.abs(ab[:,1])<=r))|((np.abs(ab[:,1])<=1)&(np.abs(ab[:,0])<=r))
                    points(p+ab[mask,0,None]*u+ab[mask,1,None]*w,PURPLE)
        for t in np.linspace(58,92,90):
            phi=(t-58)/34*math.pi*2;diamond=np.array([math.cos(phi),math.sin(phi)])
            diamond/=max(abs(diamond));p=tip+t*v+width*(diamond[0]*u+diamond[1]*w)
            beam(p,p,M.GOLD,1)
        sphere=tip+76*v
        offsets=np.indices((11,11,11)).reshape(3,-1).T-5
        points(sphere+offsets[(offsets*offsets).sum(1)<=25],MAGENTA)

    # 八角重型阶梯地基，十字槽留15格实际深度；不把全包围盒填成实体。
    for y in range(0,50):
        shrink=(y//8)*7;ax=250-shrink;az=225-shrink
        q=np.maximum(np.abs(X)/ax,np.abs(Z)/az)
        mask=(q<=1)&(np.abs(X)/ax+np.abs(Z)/az<=1.45)
        c[y][mask]=IDS[M.ATOMIC if y%8 else M.STRESS]
        if y>=34:c[y][mask&((np.abs(X)<12)|(np.abs(Z)<12))]=0
    channel=((np.abs(X)<12)&(np.abs(Z)<184))|((np.abs(Z)<12)&(np.abs(X)<208))
    c[34][channel]=IDS[M.LIGHT];c[35][channel]=IDS[ORANGE];c[49][channel]=IDS[MAGENTA]
    routes=[]
    for axis,span in [('x',190),('z',170)]:
        for side in (-1,1):
            a=[336,40,264];b=a.copy();a[0 if axis=='x' else 2]+=side*35;b[0 if axis=='x' else 2]+=side*span
            a,b=(a,b) if a[0 if axis=='x' else 2]<b[0 if axis=='x' else 2] else (b,a)
            for p in (a,b):box(np.array(p)-[2,2,2],np.array(p)+[2,2,2],M.TURBINE)
            path=np.rint(np.linspace(a,b,span-35+1)).astype(int)
            for p in path:points([p],M.GOLD)
            routes.append(dict(id=f'{axis}{side:+}金色冷却导管',start=a,end=b,path=path.tolist(),endpoint_state=M.TURBINE))
    anchors=[]
    for i in range(8):
        th=(i+.5)*math.pi/4;v=np.array([math.cos(th),math.sin(th)])
        root=np.array([336,264])+v*np.array([220,195])
        for y in range(0,66):
            cx,cz=root-y*.71*v;a=np.abs((xx-cx)*v[0]+(zz-cz)*v[1]);b=np.abs(-(xx-cx)*v[1]+(zz-cz)*v[0])
            mask=(a<=15)&(b<=15);c[y][mask]=IDS[M.ATOMIC]
            c[y][mask&((a>12)|(b>12))]=IDS[M.GOLD if y%14<4 else M.ROBUST]
        top=np.r_[root-65*.71*v,0];head=[float(top[0]),65,float(top[1])]
        target=[336+65*v[0],154,264+65*v[1]]
        beam(head,target,MAGENTA,2);beam(np.array(head)+[0,2,0],np.array(target)+[0,2,0],M.GOLD,1)
        anchors.append(dict(id=i+1,root=[float(root[0]),0,float(root[1])],top=head))
    # 第一环优先采用原文范围表：宽420、高280的直立椭圆，厚18。
    for y in range(20,321):
        r=(X/210)**2+((y-170)/140)**2
        mask=np.broadcast_to((r<=1)&(r>=.79),(D,W))&(np.abs(Z)<=9)
        c[y][mask]=IDS[WHITE]
        border=mask&((r>.97)|(r<.82));c[y][border]=IDS[M.GOLD]
        c[y][mask&(np.abs(Z)>6)&(r<.87)]=IDS[COIL]
        c[y][mask&(np.abs(Z)==9)&(r>.88)&(r<.91)]=IDS[MAGENTA]
    for i in range(12):
        th=i*math.pi/6;base=np.array([336+210*math.cos(th),170+140*math.sin(th),264.])
        v=np.array([math.cos(th),.28*math.sin(th),.96*math.sin(th)]);v/=np.linalg.norm(v)
        _,u,w=frame(v)
        for t in range(36):
            half=7*(1-t/35);a,b=np.meshgrid(np.arange(-7,8),np.arange(-7,8));mask=np.abs(a)+np.abs(b)<=half
            points(base+t*v+a[mask,None]*u+b[mask,None]*w,M.GOLD)
    # 第二环相对水平倾斜30度，12段装甲之间仅保留窄紫晶桥；第三环倾斜-45度。
    for y in range(45,291):
        Y=y-170
        for radius,tilt,width,depth in [(160,math.pi/6,9,7),(100,-math.pi/4,6,6)]:
            v=Y*math.sin(tilt)+Z*math.cos(tilt);normal=Y*math.cos(tilt)-Z*math.sin(tilt)
            radial=np.sqrt(X*X+v*v);phi=np.arctan2(v,X)%(2*math.pi)
            if radius==160:
                mask=(np.abs(radial-radius)<=width)&(np.abs(normal)<=depth)
                gap=(phi%(math.pi/6))<10/radius
                metal=mask&~gap;c[y][metal]=IDS[M.GOLD]
                c[y][metal&((phi//(math.pi/6)).astype(int)%2==1)]=IDS[M.ATOMIC]
                c[y][mask&gap&(np.abs(radial-radius)<=3)&(np.abs(normal)<=3)]=IDS[MAGENTA]
            else:
                mask=np.abs(radial-radius)+np.abs(normal)<=6;c[y][mask]=IDS[MAGENTA]
                c[y][mask&((phi%(math.pi/6))<.06)]=IDS[M.GOLD]
    # 左翼24片白金羽翎，5格厚、15格宽；各片经细金束连接主环。
    feathers=[]
    for i in range(24):
        row,col=divmod(i,4);length=80+row*8;th=math.radians(14+row*5)
        axis=np.array([-math.cos(th),math.sin(th),0]);across=np.array([math.sin(th),math.cos(th),0])
        start=np.array([length*math.cos(th)+col*29,92+row*24,264+(col-1.5)*25])
        offsets,thicks=np.meshgrid(np.arange(-7,8),np.arange(-2,3));offsets=offsets.ravel();thicks=thicks.ravel()
        for t in range(length+1):
            p=start+t*axis+offsets[:,None]*across+thicks[:,None]*np.array([0,0,1])
            points(p,WHITE);points(p[(np.abs(offsets)>5)|(t<2)|(t>length-2)],M.GOLD)
            points(p[(abs(t-length*.55)/12+np.abs(offsets)/6<1)&(thicks==-2)],MAGENTA)
        beam(start,[144,170,264],M.GOLD,1)
        feathers.append(dict(id=i+1,length=length,width=15,thickness=5,start=start.tolist()))
    # 右侧三条半扭转闭合带，中心线周长约251格，带宽25格、厚5格。
    ribbons=[];U=np.array([1.,0,0]);V=np.array([0,math.sqrt(3)/2,.5]);N=np.cross(U,V)
    for i,center in enumerate(([500,130,245],[560,195,280],[620,240,245])):
        center=np.asarray(center,float)
        for th in np.linspace(0,2*math.pi,1001):
            radial=math.cos(th)*U+math.sin(th)*V;along=-math.sin(th)*U+math.cos(th)*V
            across=math.cos(th/2)*radial+math.sin(th/2)*N;normal=np.cross(along,across)
            a,b=np.meshgrid(np.arange(-12,13),np.arange(-2,3));p=center+40*radial+a.reshape(-1,1)*across+b.reshape(-1,1)*normal
            points(p,M.ATOMIC)
            points(p[(np.abs(a).ravel()>10)|((int(th*40)%34)<3)],MAGENTA)
        ribbons.append(dict(id=i+1,center=center.tolist(),centerline_length=80*math.pi,width=25,thickness=5,half_twist=True))
    cubes=[]
    for i in range(32):
        cx=450+(i%8)*29;cy=90+(i//8)*50+(i%2)*12;cz=264+int(84*math.sin(i*2.39996))
        offsets=np.indices((15,15,15)).reshape(3,-1).T-7
        points(np.array([cx,cy,cz])+offsets[np.max(np.abs(offsets),axis=1)==7],MAGENTA)
        cubes.append(dict(center=[cx,cy,cz],size=15))
    # 前后护盾菱晶依原文表延展Z轴；端面晶体真实占满529格纵深。
    for cz in [4,47,90,133,176,219,309,352,395,438,481,524]:
        size=22 if cz in (4,524) else 12
        for y in range(160-size,161+size):
            q=np.abs(X)+abs(y-160);mask=np.broadcast_to(q<=size,(D,W))&(np.abs(zz-cz)<=4)
            c[y][mask]=IDS[MAGENTA];c[y][mask&(q>size-2)]=IDS[M.GOLD]
    # 外85格框架、内50格旋转玻璃立方体和25格橙金球体。
    corners=[np.array([336+dx,160+dy,264+dz]) for dx in (-40,40) for dy in (-40,40) for dz in (-40,40)]
    edges=0
    for i,a in enumerate(corners):
        for b in corners[i+1:]:
            if np.count_nonzero(a!=b)==1:beam(a,b,[WHITE,M.ATOMIC,M.GOLD][edges%3],2);edges+=1
    for y in range(125,196):
        u=(X+Z)/math.sqrt(2);v=(Z-X)/math.sqrt(2);q=np.maximum(np.maximum(np.abs(u),np.abs(v)),abs(y-160))
        c[y][(q<=25)&(q>=23)]=IDS[MAGENTA]
        r=X*X+Z*Z+(y-160)**2;c[y][r<=12**2]=IDS[ORANGE];c[y][r<=9**2]=IDS[M.LIGHT]
    spears=[]
    for i in range(12):
        th=i*math.pi/6;pitch=math.radians([0,18,30,20,0,-18,0,22,32,18,0,-18][i])
        v=np.array([math.cos(th)*math.cos(pitch),math.sin(pitch),math.sin(th)*math.cos(pitch)])
        tip_radius=42/max(abs(v))+15;tip=np.array([336,160,264])+tip_radius*v;length=180+(i%3)*10
        blade(tip,v,length)
        spears.append(dict(id=i+1,tip=tip.tolist(),axis=v.tolist(),length=length,width=25,tip_core_ray_gap=15))
    # 顶部120格王冠与实体向下光柱；321层的最高体素为局部Y320。
    for y in range(290,301):
        r=np.sqrt(X*X+Z*Z);mask=(r<=60)&(r>=56);c[y][mask]=IDS[M.GOLD if y%3 else MAGENTA]
    for i in range(12):
        th=i*math.pi/6;cx=336+int(round(58*math.cos(th)));cz=264+int(round(58*math.sin(th)))
        for y in range(299,321):
            r=max(0,(320-y)*.32);mask=np.abs(xx-cx)+np.abs(zz-cz)<=r;c[y][mask]=IDS[M.GOLD]
    box((334,202,262),(338,300,266),ORANGE);box((336,202,264),(336,300,264),M.LIGHT)
    # 正前45格白金门面，主控居中；八舱位继续保持通用能力。
    box((314,3,39),(358,22,55),WHITE)
    for y in range(4,22):
        for x in range(315,358):
            if abs(x-336)+abs(y-12)<=6:c[y,39,x]=IDS[M.GOLD]
    control=[336,12,39];box(control,control,M.CONTROL);ports=[]
    for i,offset in enumerate((-18,-14,-10,-6,6,10,14,18)):
        p=[336+offset,12,39];box(p,p,M.PORT)
        ports.append(dict(id=f'大门通用舱位{i+1:02}',pos=p,face='north',group='generic',purpose='通用物品、流体或能源仓位；不按左右限定输入输出'))
    box((314,8,34),(358,18,38),None)
    box((317,23,42),(355,25,53),M.GOLD)
    box((319,23,43),(353,24,52),M.VENT)
    # 导管位于地基内，主环穿入基础时优先保留其接续设备和通道。
    for route in routes:
        for p in (route['start'],route['end']):box(np.array(p)-[2,2,2],np.array(p)+[2,2,2],M.TURBINE)
        points(np.asarray(route['path']),M.GOLD)
    zones=[dict(name='三重穹界环与破碎超立方体',pos=[336,160,264]),dict(name='左翼 · 24片秩序白金羽翎',pos=[120,180,264]),
        dict(name='右翼 · 三条莫比乌斯带与32枚虚数立方体',pos=[560,195,280]),dict(name='天顶王冠 · 向下光柱',pos=[336,300,264])]
    data=dict(key='w03',name='hk3gtl-w03-celestial-wings-v3-20261107',candidate_version='V3',
        title='空之律者 · 穹界·虚数锚定环 · 三环双翼神殿（Gemini原案）',size=[W,H,D],controller=control,controller_face='north',
        ports=ports,zones=zones,paths=[dict(min=[314,8,34],max=[358,18,38])],pipe_routes=routes,target_voltage='CIV',
        appearance_voltage='原案白金／黑紫',character='西琳',anchors=anchors,feathers=feathers,ribbons=ribbons,cubes=cubes,spears=spears,
        description='八角阶梯锚盘与十字紫晶导流槽托起三重交错天体环。左侧24片白金羽翎，右侧三条黑紫莫比乌斯带及32枚虚数立方体形成不对称双翼；十二柄实体亚空之矛指向中心镂空超立方体，顶部王冠将光柱贯入橙金核心。',
        purpose='Gemini原案造型预览，供与V1及DeepSeek V2并排选择。使用现有石英、金、黑色机壳与真实玻璃近似原文材质，不新增专属方块，不为既定递增或HCV规则增料改色。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1);assert all(counts[1:]),[(s,int(n)) for s,n in zip(STATES,counts[1:]) if not n]
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]));occupied=c!=0;bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)));bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);sizes=np.bincount(labels.ravel())[1:];del labels,occupied
    assert palette[M.CONTROL]==1 and palette[M.PORT]==8 and data['controller'][0]==336
    markers=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        x,y,z=item['pos'];assert c[y,z+1,x] and not np.any(c[y,z-5:z,x])
        assert all(c[y+dy,z,x+dx] for dx,dy in ((-1,0),(1,0),(0,1),(0,-1)))
        markers.append(dict(id=item['id'],position=item['pos'],flush_shell=True,inner_backed=True,outer_clear=5))
    for route in data['pipe_routes']:
        assert all(c[y,z,x]==IDS[M.GOLD] for x,y,z in route['path'])
        for x,y,z in (route['start'],route['end']):assert c[y+1,z,x]==IDS[M.TURBINE]
    for path in data['paths']:
        x,y,z=path['min'];x1,y1,z1=path['max'];assert not np.any(c[y:y1+1,z:z1+1,x:x1+1])
    metrics=dict(blocks=int(counts[1:].sum()),materials=len(STATES)-2,volume=W*H*D,height=H)
    previous=json.loads((ROOT/'logs/w03-anchor-v1-20261107/voltage-progression.json').read_text(encoding='utf8'))
    passes={k:metrics[k]>v['value'] for k,v in previous['lower_maxima'].items()}
    return dict(passed=True,geometry_passed=True,design_rules_passed=False,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),blocks=metrics['blocks'],
        unique_materials=len(STATES),ordinary_materials=len(STATES)-2,palette=palette,bounding_box_volume=W*H*D,height=H,
        baseline_check=dict(passed=True,baseline_wdh=baselines()['W03']['size']),
        voltage_progression=dict(passed=all(passes.values()),passes=passes,metrics=metrics,lower_form_count=56,
            lower_maxima=previous['lower_maxima'],source='logs/w03-anchor-v1-20261107/voltage-progression.json',
            comparison='原案预览仅记录差距，不为递增门槛调整方块量或主色。'),
        connectivity=dict(components=int(n),largest_component_blocks=int(max(sizes)),
            interpretation='保留原文悬浮羽片、晶体与结构段；连通性只记录，不追加支架改写造型。'),
        controller=dict(position=data['controller']),port_checks=markers,pipe_routes_count=4,pipe_routes_passed=True,open_pipe_ends=0,
        character='西琳',anchor_count=8,feather_count=24,ribbon_count=3,virtual_cube_count=32,spear_count=12,ring_count=3,
        source_geometry_conflicts=['原文420格直立圆环与321格总高矛盾；按范围表取X±210、Y30～310，转为椭圆，未称真420直径圆。',
            '宽673、深529、高321是114,281,457格包围盒，不是实体方块量。',
            '局部Y0～320共321层；原文最高Y321按总高321解释，避免导出322层。',
            '原文新增专属机壳与当前禁新增规则冲突；本版使用现有方块近似，不宣称有新机壳或CTM。'],
        checks=['实际实体边界673×529×321，未扩大空白边界冒充尺寸。','24片15格宽、5格厚白金羽翎与三条25格宽半扭转闭合带均为真实方块。',
            '八根倾斜锚柱、三重交错环、十二柄矛、32枚虚数方块及中心85格框架均已生成。','八个正前通用接口有背板、齐平，保留五格净空。',
            '四条十字导流槽金色管路均核对两端设备。','所有静态光束与玻璃均取真实方块资源；不把静态几何称为运行特效。'],
        not_verified=['本版仅为Gemini原案几何转译；HCV主材与规模递增尚未整改或获豁免，未批准、未部署。',
            '动态旋转、Portal Shader、金色雷电、实体角色、成型、配方与8GB工况均未实现或验收。',
            '原文未给逐格坐标；翼片排列、倾角基准、矛轴位置、材质近似与局部比例由本次实现解释。'])


if __name__=='__main__':
    cube,data=build();v=audit(cube,data);print(json.dumps({k:v[k] for k in ('blocks','unique_materials','connectivity','voltage_progression')},ensure_ascii=False))
