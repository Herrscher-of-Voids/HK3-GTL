# -*- coding: utf-8 -*-
"""Gork原案：四锚、中轴、错层环系与破损穹盖；完整域生成。"""
import math
import numpy as np
from audit_wonder_clipping_20261108 import LogicalGrid,PAD
from i42_prefabrication_geometry_v1_20261028 import Material

M=Material();W,H,D=673,321,529
BLACK='minecraft:black_concrete';PURPLE='minecraft:purple_concrete'
CRYSTAL='minecraft:amethyst_block';GLASS='minecraft:purple_stained_glass'
WHITE='minecraft:white_stained_glass';HALO='minecraft:light_blue_stained_glass'
STATES=sorted({M.ATOMIC,M.IRON,M.GRATE,M.LIGHT,M.CONTROL,M.PORT,BLACK,PURPLE,CRYSTAL,GLASS,WHITE,HALO})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={M.ATOMIC:'深空黑结构装甲、环与锚盘外壳',M.IRON:'星核银白桁架、轮廓与大纹样代理',
 M.GRATE:'基础汇聚阵列格栅',M.LIGHT:'能量沟背光的现有海晶灯代理',BLACK:'黑色虚空中轴与奇点球',
 PURPLE:'虚空紫坐标纹路与导槽衬层',CRYSTAL:'12格厚晶格的蜂窝骨架代理',GLASS:'晶格、观测窗、能量管与穹顶薄板',
 WHITE:'白紫能量芯与闪电连接的静态实体代理',HALO:'奇点三重薄光环；预览演示时用旋转线环替换显示',
 M.CONTROL:'南侧防护壁内嵌主控占位',M.PORT:'四节点八处与南壁八处通用接口，不限定输入输出'}


def wave(t):return 7*math.sin(t)+3*math.sin(2*t)


def build():
    c=LogicalGrid((H,D,W),PAD);zz,xx=np.ogrid[-PAD:D+PAD,-PAD:W+PAD];X=xx-336;Z=zz-264
    R=np.sqrt(X*X+Z*Z);A=np.arctan2(Z,X);flows=[];conduits=[]
    def box(a,b,s):
        x,y,z=np.rint(a).astype(int);x1,y1,z1=np.rint(b).astype(int);assert x<=x1 and y<=y1 and z<=z1
        c[y:y1+1,z:z1+1,x:x1+1]=IDS[s] if s else 0
    def points(p,s):
        p=np.unique(np.rint(np.asarray(p)).astype(int).reshape(-1,3),axis=0)
        c[p[:,1],p[:,2],p[:,0]]=IDS[s]
    def plane(y,mask,s):c[y][mask]=IDS[s]
    def line(a,b,s,r=0):
        a=np.array(a,float);b=np.array(b,float)
        for p in np.rint(np.linspace(a,b,max(2,int(np.max(np.abs(b-a))*2)+1))).astype(int):box(p-r,p+r,s)
    def flow(name,path,kind='conduit'):
        p=np.array(path,float);flows.append(dict(name=name,kind=kind,path=np.round(p,4).tolist()))
    def circle(radius,y,tilt=0,phase=0):
        t=np.linspace(0,2*math.pi,361);return np.c_[336+radius*np.cos(t),y+radius*np.sin(t)*math.sin(tilt),264+radius*np.sin(t)*math.cos(tilt)]
    def tube(path,r=4):
        p=np.asarray(path,float);offset=np.indices((2*r+1,)*3).reshape(3,-1).T-r
        # 球截面扫掠避免斜向体素漏缝；白紫芯与银白壳均是实际方块。
        radius=np.sqrt((offset*offset).sum(1));shell=offset[radius<=r+.1];core=offset[radius<r-1.5]
        for start in range(0,len(p),60):
            q=p[start:start+60];points(q[:,None,:]+shell[None,:,:],M.IRON)
            points(q[:,None,:]+core[None,:,:],GLASS)
        points(p,WHITE)
    # 35格厚椭圆平台，真实外壳与上下表皮，内部留空。
    outer=(X/336)**2+(Z/276)**2<=1;inner=(X/332)**2+(Z/272)**2<1
    for y in range(35):plane(y,outer if y<3 or y>31 else outer&~inner,M.ATOMIC)
    rim=outer&((X/330)**2+(Z/270)**2>=1)
    window=(np.abs(np.sin(A*8))>.40)
    for y in range(35,70):
        plane(y,rim,M.ATOMIC)
        plane(y,rim&window&(y>=44)&(y<=61),GLASS)
        if y in (35,36,68,69):plane(y,rim,M.IRON)
    for radius in (65,110,160,215,265):
        band=np.abs(R-radius)<=2;plane(34,band,M.LIGHT);plane(35,band,GLASS)
    for i in range(16):
        th=i*math.pi/8;extent=1/math.sqrt((math.cos(th)/326)**2+(math.sin(th)/266)**2)
        end=[336+extent*math.cos(th),36,264+extent*math.sin(th)]
        line([336,36,264],end,GLASS,1);line([336,35,264],np.array(end)-[0,1,0],M.GRATE,2)
        flow(f'基础汇聚线{i+1}',np.linspace(end,[336,36,264],140),'foundation')
    # 波浪主环：外600×480，内480×360；两条长轴尺寸分别对应原文外／内径。
    outside=(X/300)**2+(Z/240)**2<=1;hole=(X/240)**2+(Z/180)**2<1
    band=outside&~hole;t=np.arctan2(Z/210,X/270);height=166+7*np.sin(t)+3*np.sin(2*t)
    outer_skin=outside&((X/297)**2+(Z/237)**2>=1)
    inner_skin=(~hole)&((X/243)**2+(Z/183)**2<=1)
    middle=np.sqrt((X/270)**2+(Z/210)**2);groove=np.abs(middle-1)<.016
    for y in range(136,197):
        dy=np.abs(y-height);body=band&(dy<=20)
        skin=body&((dy>=17)|outer_skin|inner_skin)
        plane(y,skin,M.ATOMIC);plane(y,body&inner_skin&(dy<14),GLASS)
        plane(y,body&groove&(dy<=4),PURPLE);plane(y,body&groove&(dy<=2),GLASS)
        plane(y,body&groove&(dy<.6),M.LIGHT)
        ribs=skin&(np.abs(np.sin(t*16))<.035);plane(y,ribs,M.IRON)
    theta=np.linspace(0,2*math.pi,721)
    main=np.c_[336+270*np.cos(theta),166+7*np.sin(theta)+3*np.sin(2*theta),264+210*np.sin(theta)]
    flow('主环连续能量导槽',main,'main')
    # 大型虚空之眼纹样，按曲面外轮廓展开，不贴细碎噪点。
    for i in range(12):
        a=i*math.pi/6
        for dy in range(-11,12):
            for du in range(-17,18):
                q=abs(du)/17+abs(dy)/11
                if .86<=q<=1.05 or (du*du+dy*dy<=9):
                    th=a+du/275;p=[336+300*math.cos(th),166+wave(th)+dy,264+240*math.sin(th)]
                    points([p],M.IRON if q>.86 else CRYSTAL)
    # 四处80格节点、250格工形锚桩与上下100格锚盘。
    nodes=[];anchors=[];ports=[]
    for i in range(4):
        th=i*math.pi/2;v=np.rint([math.cos(th),0,math.sin(th)]);u=np.array([-v[2],0,v[0]])
        center=np.array([336+270*v[0],round(166+wave(th)),264+210*v[2]]);cx,cy,cz=map(int,center)
        dx=xx-cx;dz=zz-cz;local=np.sqrt(dx*dx+dz*dz)
        for y in range(cy-15,cy+16):
            mask=(local<=40)&((local>=37)|(abs(y-cy)>=12));plane(y,mask,M.ATOMIC)
            plane(y,mask&((abs(y-cy)>=14)|(local>=39)),M.IRON)
        for y in range(35,285):
            body=(np.abs(dx)<=18)&(np.abs(dz)<=18)&((np.abs(dx)>=12)|(np.abs(dz)<=4))
            plane(y,body,M.ATOMIC)
            plane(y,body&((np.abs(dx)>=17)|(np.abs(dz)>=17)),M.IRON)
            rune=body&((np.abs(dx+dz+((y//16)%3)*3)%17)<2)&(y%16<11)
            plane(y,rune,CRYSTAL if y%32<16 else PURPLE)
        for y0 in (29,279):
            for y in range(y0,y0+12):
                mask=(local<=50)&((local>=47)|(y-y0<2)|(y-y0>9))
                plane(y,mask,M.ATOMIC);plane(y,mask&(local>=49),M.IRON)
            for j in range(12):
                a=j*math.pi/6;line([cx,y0+11,cz],[cx+48*math.cos(a),y0+11,cz+48*math.sin(a)],GLASS,1)
        for y in (54,263):
            line(center+[0,y-cy,0]-u*30,center+[0,y-cy,0]+u*30,M.IRON,3)
        # 节点外端的连续设备面板，与原80格圆盘真实接续。
        panel=center+v*40
        corners=np.array([panel+u*a+v*b+[0,d,0] for a in (-11,11) for b in (-4,0) for d in (-7,7)])
        box(corners.min(0),corners.max(0),M.ATOMIC)
        face=['east','south','west','north'][i]
        for delta in (-6,6):
            p=np.rint(panel+u*delta).astype(int).tolist();points([p],M.PORT)
            ports.append(dict(id=f'节点{i+1}通用舱位{delta:+}',pos=p,face=face,group='generic',purpose='节点通用接口，不限制物品、流体或能源输入输出'))
        nodes.append(dict(center=center.tolist(),diameter=80));anchors.append(dict(center_xz=[cx,cz],shaft_y=[35,284],disc_diameter=100))
    # 280格中轴：黑色内柱与厚12格断续蜂窝紫晶壳。
    axis=R<=20;lattice=(R>20)&(R<=32);s=A*32
    for y in range(35,315):
        plane(y,axis,BLACK)
        hex_u=np.abs((s+(y//16%2)*8+8)%16-8);hex_v=abs(y%16-8)
        frame=(hex_u+.58*hex_v>7)&(hex_u+.58*hex_v<9)
        missing=((np.floor((A+math.pi)*9/math.pi)+y//31)%13)==0
        shell=lattice&~missing;plane(y,shell,GLASS);plane(y,shell&frame,CRYSTAL)
        plane(y,shell&(hex_u<.8)&(hex_v<5),WHITE)
    for y in range(138,195):plane(y,(R*R+(y-166)**2<=28**2),BLACK)
    # 四圈9格导管汇聚到中轴，上下各两圈，16条粗导管接四节点。
    collectors=[]
    for j,(y,radius) in enumerate(((122,86),(140,66),(192,66),(210,86))):
        curve=circle(radius,y);tube(curve,4);flow(f'奇点汇聚圈{j+1}',curve,'collector')
        collectors.append(dict(y=y,radius=radius,diameter=9))
        for i,node in enumerate(nodes):
            p=np.array(node['center'],float);p[1]+=(-8 if y<166 else 8)
            th=i*math.pi/2;end=np.array([336+31*math.cos(th),y,264+31*math.sin(th)])
            curve=np.linspace(p,end,int(np.linalg.norm(end-p)*2)+1);tube(curve,4)
            conduits.append(dict(id=f'汇聚圈{j+1}节点{i+1}',start=p.tolist(),end=end.tolist(),node=i+1))
            flow(conduits[-1]['id'],curve[::max(1,len(curve)//180)],'conduit')
    # 奇点三层极薄环，独立材质供概念旋转预览；实体蓝图保留初始姿态。
    halo_paths=[]
    for i,(radius,tilt) in enumerate(((34,.35),(40,1.05),(45,-.65))):
        curve=circle(radius,166,tilt);points(curve,HALO)
        halo_paths.append(dict(radius=radius,tilt=tilt,center=[336,166,264]))
        for j in range(6):
            th=j*math.pi/3;p=curve[j*60];q=np.array([336+28*math.cos(th),166,264+28*math.sin(th)])
            middle=(p+q)/2+[0,3 if j%2 else -3,0];line(p,middle,WHITE);line(middle,q,WHITE)
    # 上下各两圈辅助环；比主环截面低，按原文保留上下两组。
    auxiliary=[]
    for i,(radius,y) in enumerate(((150,86),(200,120),(200,220),(150,255))):
        heights=y+5*np.sin(A+i*.6);radial=np.abs(R-radius)
        for yy in range(y-12,y+13):
            dy=np.abs(yy-heights);mask=(radial<=6)&(dy<=6)
            shell=mask&((radial>=4)|(dy>=4));plane(yy,shell,M.ATOMIC);plane(yy,shell&(radial>=5),M.IRON)
            plane(yy,mask&(radial<2)&(dy<2),GLASS)
        t=np.linspace(0,2*math.pi,361);curve=np.c_[336+radius*np.cos(t),y+5*np.sin(t+i*.6),264+radius*np.sin(t)]
        flow(f'辅助环{i+1}',curve,'auxiliary');auxiliary.append(dict(radius=radius,y=y,phase=i*.6))
    def bridge(a,b):
        a=np.array(a);b=np.array(b);v=b-a;u=np.cross(v,[0,1,0]);u/=np.linalg.norm(u)
        line(a,b,GLASS,1)
        for side in (-1,1):line(a+u*5,b+u*5,M.IRON)
        for t in np.linspace(0,1,9):line(a+v*t-u*5,a+v*t+u*5,M.IRON)
        flow('环间桁架能流',np.linspace(a,b,80),'bridge')
    for i in range(8):
        th=i*math.pi/4
        targets=[]
        for ring in auxiliary:
            targets.append([336+ring['radius']*math.cos(th),ring['y']+5*math.sin(th+ring['phase']),264+ring['radius']*math.sin(th)])
        mid=[336+270*math.cos(th),166+wave(th),264+210*math.sin(th)]
        for a,b in ((targets[0],targets[1]),(targets[1],mid),(mid,targets[2]),(targets[2],targets[3])):bridge(a,b)
    # 40格浅穹顶由12片弧形晶格板构成，保留宽角隙与中央孔。
    roof_r=np.sqrt((X/320)**2+(Z/260)**2);roof_a=np.arctan2(Z/260,X/320)%(2*math.pi)
    sector=roof_a%(math.pi/6);roof_mask=(roof_r>=.1)&(roof_r<=1)&(sector>.055)&(sector<math.pi/6-.055)
    roof_y=np.rint(315+40*(1-roof_r*roof_r)).astype(int)
    zs,xs=np.where(roof_mask);ys=roof_y[zs,xs];wx=xs-PAD;wz=zs-PAD
    lattice_edge=(sector[zs,xs]<.085)|(sector[zs,xs]>math.pi/6-.085)|(np.mod(roof_r[zs,xs]*10,1)<.055)
    for dy in (0,1):
        c[ys+dy,wz,wx]=np.where(lattice_edge,IDS[M.IRON] if dy==1 else IDS[CRYSTAL],IDS[GLASS])
    cables=[]
    for i in range(24):
        th=(i+.5)*math.pi/12;r=.74
        start=np.array([336+320*r*math.cos(th),315+40*(1-r*r),264+260*r*math.sin(th)])
        end=np.array([336+270*math.cos(th),184+wave(th),264+210*math.sin(th)])
        line(start,end,GLASS,1);flow(f'穹盖垂索{i+1}',np.linspace(start,end,110),'cable')
        cables.append(dict(start=start.tolist(),end=end.tolist()))
    for i in range(8):
        th=(i+.5)*math.pi/4;r=.2
        start=[336+320*r*math.cos(th),315+40*(1-r*r),264+260*r*math.sin(th)]
        end=[336+31*math.cos(th),265,264+31*math.sin(th)]
        line(start,end,GLASS,1);flow(f'中轴垂索{i+1}',np.linspace(start,end,85),'cable');cables.append(dict(start=start,end=end))
    # 南防护壁的主控设备湾连续嵌入曲面外壳。
    box([284,42,536],[388,63,540],M.ATOMIC)
    for x in (284,285,387,388):box([x,42,540],[x,63,540],M.IRON)
    control=[336,52,540];points([control],M.CONTROL)
    for dx in (-36,-28,-20,-12,12,20,28,36):
        p=[336+dx,52,540];points([p],M.PORT);ports.append(dict(id=f'南壁通用舱位{dx:+}',pos=p,face='south',group='generic',purpose='防护壁设备湾通用接口'))
    full=c.array;occupied=full!=0;low=[];high=[]
    for axis in range(3):
        p=np.flatnonzero(np.any(occupied,axis=tuple(j for j in range(3) if j!=axis)));low.append(int(p[0]));high.append(int(p[-1])+1)
    assert all(a>0 and b<full.shape[i] for i,(a,b) in enumerate(zip(low,high))),'安全域不足，禁止裁切'
    cube=full[tuple(slice(a,b) for a,b in zip(low,high))].copy()
    origin=np.array([low[2]-PAD,low[0]-PAD,low[1]-PAD]);offset=-origin
    for p in ports:p['pos']=(np.array(p['pos'])+offset).tolist()
    for item in flows:item['path']=(np.array(item['path'])+offset).tolist()
    for item in halo_paths:item['center']=(np.array(item['center'])+offset).tolist()
    data=dict(key='w03',name='hk3gtl-w03-four-anchor-canopy-v7-20261108',candidate_version='V7',
        title='空之律者 · 穹界·虚数锚定环 · 四锚穹盖（Gork原案）',size=[cube.shape[2],cube.shape[0],cube.shape[1]],
        nominal_size_xyz=[673,321,529],blueprint_bounds_xyz=dict(min=origin.tolist(),max=[high[2]-PAD-1,high[0]-PAD-1,high[1]-PAD-1]),
        blueprint_to_export_offset_xyz=offset.tolist(),controller=(np.array(control)+offset).tolist(),controller_face='south',ports=ports,
        zones=[dict(name='主环与四个加厚节点',pos=(np.array([336,166,24])+offset).tolist()),dict(name='280格晶格中轴与奇点',pos=(np.array([336,166,264])+offset).tolist()),
               dict(name='12片破损穹盖与32条垂索',pos=(np.array([336,355,264])+offset).tolist())],
        paths=[],pipe_routes=[],target_voltage='CIV',character='西琳',anchors=anchors,nodes=nodes,collectors=collectors,energy_conduits=conduits,
        auxiliary_rings=auxiliary,dome_panels=12,dome_cables=cables,preview_flows=flows,preview_halos=halo_paths,
        description='深空黑椭圆主环以四座250格工形锚桩锁住280格蜂窝晶格中轴；上下各两层辅助环错落环绕，三重奇点薄环位于核心中段。破损浅穹盖以32条细索悬接环与轴，下方35格厚平台含放射汇聚阵列与带观测窗的防护壁。',
        purpose='负责人提供Gork原案的独立V7转译；不沿用673×529×321裁切窗。流动能量与旋转薄环是可关闭的概念预览，实体NBT／Schem记录静态初始姿态，游戏动态与工艺另行实装。')
    return cube,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1);assert all(counts[1:])
    h,d,w=c.shape;directions=dict(north=(0,0,-1),south=(0,0,1),east=(1,0,0),west=(-1,0,0))
    def cell(p):
        x,y,z=map(int,p);return int(c[y,z,x]) if 0<=x<w and 0<=y<h and 0<=z<d else 0
    ports=[]
    for item in [dict(id='主控',pos=data['controller'],face='south')]+data['ports']:
        p=np.array(item['pos']);v=np.array(directions[item['face']]);assert cell(p) and cell(p-v),item
        assert all(not cell(p+j*v) for j in range(1,6)),item
        ports.append(dict(id=item['id'],position=p.tolist(),inner_backed=True,outer_clear=5))
    offset=np.array(data['blueprint_to_export_offset_xyz'])
    for route in data['energy_conduits']:
        a=np.array(route['start']);b=np.array(route['end']);node=np.array(data['nodes'][route['node']-1]['center'])
        assert np.linalg.norm((a-node)[[0,2]])<1 and abs(a[1]-node[1])==8
        assert abs(np.linalg.norm((b-[336,0,264])[[0,2]])-31)<1e-5
        assert all(cell(np.rint(p+offset)) for p in np.linspace(a,b,int(np.linalg.norm(b-a)*2)+1))
    assert len(data['anchors'])==4 and len(data['auxiliary_rings'])==4 and len(data['collectors'])==4 and len(data['dome_cables'])==32
    assert len(data['ports'])==16 and data['size'][0]>=673 and data['size'][1]>=321 and data['size'][2]>=529
    return dict(passed=True,geometry_passed=True,design_rules_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=data['size'],size_wdh=[w,d,h],blocks=int(counts[1:].sum()),unique_materials=len(STATES),palette=dict(zip(STATES,map(int,counts[1:]))),
        bounds_xyz=dict(min=[0,0,0],max=[w-1,h-1,d-1]),no_nominal_clipping=True,nominal_size_xyz=[673,321,529],
        blueprint_bounds_xyz=data['blueprint_bounds_xyz'],port_checks=ports,pipe_routes_count=0,pipe_routes_passed=True,open_pipe_ends=0,
        energy_conduits_count=16,energy_conduit_attachments_passed=True,visual_only_no_fluid_pipelines=True,
        anchors=4,auxiliary_rings=4,collectors=4,core_halos=3,dome_panels=12,dome_cables=32,
        beauty_first_exception=dict(scope='W01–W15',mandatory_casing_dominance=False,numeric_progression_required=False),
        checks=['扩展坐标域完整生成、实际包围盒裁出；无越界点过滤、端点夹边或为尺寸压扁构件。',
            '600×480外椭圆、480×360内椭圆、约40格高主环保留波浪起伏；16条粗能量管逐点核对四节点和中轴接续。',
            '四锚桩250格、上下100格锚盘；中轴280格，直径约40的内柱外包12格断续晶格。',
            '四层辅助环、三层奇点薄环、12片浅穹盖与32根悬索、35格基础和观测壁均为实际方块。',
            '主控及16处通用接口有背板和至少5格外部接线净空，导出范围以外按空气处理。'],
        not_verified=['W03外观候选未批准、未部署；Pattern、研究、工艺、角色实体和游戏性能均另验。',
            '已有方块近似原文虚空合金与星核材料；未注册新方块或着色器。能流与薄环旋转仅为浏览器概念演示。',
            '虚空腔体是原文的场景设想，未在世界内挖掘或修改地形。'])
