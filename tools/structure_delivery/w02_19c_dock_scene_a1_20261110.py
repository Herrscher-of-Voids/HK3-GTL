# -*- coding: utf-8 -*-
"""V6原形整体平移，组合静态U形自律构造船坞。"""
from copy import deepcopy
import math
import numpy as np
import w02_19c_geometry_v6_20261110 as robot
from w02_19c_geometry_v4_20261110 import (
    SolidPart as Part,WHITE,BLACK,BLUE,PALE,DARK,SILVER,LIGHT,GLASS,ORANGE,TRIM,
    STATES,IDS,ROLES,hull,tube,solid_annulus as annulus,encode,basis)

ROOT=robot.ROOT
OUT=ROOT/'deliveries/W02_19C自律构造船坞_组合草案_A1_20261110'
LOG=ROOT/'logs/w02-19c-dock-scene-a1-20261110'
PRIOR=robot.OUT
REFERENCE_BASE=robot.REFERENCE_BASE
VERSION='A1'
PREVIOUS_VERSION='V6'
PRESENTATION_TITLE='19C自律构造船坞 · 组合草案A1'
SHIFT=np.array([0,40,-70],np.int32)
EXPECTED_PARTS=26
CLAIM_BOUNDARY='19C与工业矩阵的完整构图候选；组合设施为本项目创作，非官方场景、非功能完整W02、非实装测试。'
CAMERA_VIEWS={
    'detail_chest':dict(label='双手与半成品',center=[0,230,45],half=[175,112,106],direction=[-.45,.25,1.6],file='双手构造场.png'),
    'detail_wheel':dict(label='两侧加工列',center=[244,77,15],half=[78,58,192],direction=[1.3,.9,1.2],file='加工模块.png'),
    'detail_hand':dict(label='前控与出货轨',center=[0,62,187],half=[112,63,80],direction=[-.7,.65,1.6],file='前控出货.png'),
    'detail_back':dict(label='背部维护与链井',center=[0,191,-132],half=[138,174,70],direction=[.6,.3,-1.5],file='背部维护.png'),
    'detail_module':dict(label='双炮处理靶台',center=[0,326,2],half=[167,45,147],direction=[-.65,.55,1.6],file='双炮工序.png')}


def plate(p,outline,low,high,state):
    hull(p,[(x,y,z) for y in [low,high] for x,z in outline],state)


def deck():
    p=Part('08_U形切角船坞与承重肋')
    zz,xx=np.mgrid[-246:247,-324:325];ax,az=abs(xx),abs(zz)
    outside=(ax+az<=530)
    footprint=outside&((ax>=194)|(zz<=-156))
    # 开口和底部镂空属于船坞设计，不是名义边界裁切。
    for y in range(37):
        rim=(ax>=317)|(az>=239)|(ax+az>=522)|((ax<=201)&(zz>-159))|((zz>=-163)&(ax<202))
        ribs=((zz+210)%40<5)|(ax%38<4)
        keep=footprint&((y<=3)|(y>=30)|rim|((y<24)&ribs))
        state=WHITE if y in [30,31,32] else BLACK
        coords=np.c_[xx[keep],np.full(keep.sum(),y),zz[keep]];p.points(coords,state)
        if y in [34,35,36]:
            edge=footprint&rim;p.points(np.c_[xx[edge],np.full(edge.sum(),y),zz[edge]],BLUE if y==35 else SILVER)
    for s in [-1,1]:
        for z in range(-180,225,40):
            p.box([s*302-7,6,z-9],[s*302+7,29,z+9],WHITE)
            p.box([s*302-4,13,z-5],[s*302+4,16,z+5],BLUE)
        tube(p,[[s*185,12,-195],[s*185,12,200],[s*260,12,238]],4,BLACK)
        tube(p,[[s*185,17,-195],[s*185,17,200],[s*260,17,238]],1.5,BLUE)
    return p.finish()


def process_module(side,index,z):
    p=Part(f'09_{side:+d}_{index}_解析与加工模块');cx=side*247
    height=[88,73,60][index];top=40+height
    q=lambda x,y,d:np.array([cx+side*x,y,z+d],float)
    outline=[(-48,-37),(-33,-48),(33,-48),(48,-33),(48,33),(33,48),(-33,48),(-48,33)]
    outline=[(cx+side*x,z+d) for x,d in outline]
    plate(p,outline,37,45,BLACK);plate(p,outline,45,48,BLUE)
    # 成对斜面外壳包住设备，中央贯穿开口留出真实内构。
    for flank in [-1,1]:
        hull(p,[q(flank*x,y,d) for x,y,d in [(38,48,-35),(44,54,-28),(41,top-10,-22),(26,top,-28),
            (29,top,28),(42,top-12,34),(43,54,35),(29,49,25)]],WHITE)
        tube(p,[q(flank*41,55,-30),q(flank*38,top-11,-22),q(flank*28,top,0),q(flank*38,top-11,27)],2,BLUE)
        for d in [-22,-8,6,20]:p.beam(q(flank*32,52,d),q(flank*34,top-17,d),2,DARK)
    cy=69+(height-60)*.35
    for d in [-23,0,23]:
        annulus(p,q(0,cy,d),[0,0,1],23,18,5,BLACK)
        annulus(p,q(0,cy,d+3),[0,0,1],20,18,2,BLUE)
        annulus(p,q(0,cy,d+4),[0,0,1],17,15,1,SILVER)
    p.beam(q(0,cy,-40),q(0,cy,40),7,DARK)
    for d in [-33,33]:p.beam(q(-11,cy,d),q(11,cy,d),2,LIGHT)
    for d in [-16,0,16]:
        p.beam(q(-8,top-2,d),q(8,top-2,d),2,BLACK)
    p.beam(q(-20,53,47),q(20,53,47),1.3,BLUE)
    p.sphere(q(26,58,39),2,ORANGE)
    return p.finish()


def supply_rails():
    p=Part('10_六站供料轨与中央汇流桥')
    for s in [-1,1]:
        for x in [s*222,s*272]:
            p.box([x-3,47,-220],[x+3,51,220],BLACK)
            p.box([x-1,52,-219],[x+1,53,219],BLUE)
        for z in range(-209,222,15):p.beam([s*222,48,z],[s*272,48,z],1,SILVER)
        for z in [-110,15,140]:
            path=[[s*198,55,z],[s*179,55,z],[s*179,64,110],[s*85,64,110]]
            tube(p,path,5,BLACK);tube(p,[np.array(a)+[0,4,0] for a in path],1.6,BLUE)
        # 汇流桥低于机械手，通向中央装配床。
        for z in [42,108]:
            p.beam([s*194,80,z],[s*76,121,z],4,BLACK)
            p.beam([s*194,84,z],[s*76,125,z],1.8,WHITE)
            p.beam([s*194,86,z],[s*76,127,z],.9,BLUE)
    return p.finish()


def assembly_bed():
    p=Part('11_中央悬挑装配床')
    outline=[(-78,9),(-56,-13),(56,-13),(78,9),(78,116),(54,142),(-54,142),(-78,116)]
    plate(p,outline,124,129,BLACK);plate(p,outline,129,132,SILVER)
    # 观察窗和框架各自有厚度，保留对下方空间的视线。
    for s in [-1,1]:
        for z in [17,115]:
            hull(p,[(s*66,40,z-9),(s*77,40,z-6),(s*69,121,z+4),(s*59,121,z+8)],BLACK)
            p.beam([s*67,43,z],[s*64,121,z],2,BLUE)
        p.beam([s*76,134,14],[s*76,134,115],2,WHITE)
        p.beam([s*72,135,17],[s*72,135,115],1,LIGHT)
    for radius,state in [(48,BLUE),(39,BLACK),(31,LIGHT)]:
        annulus(p,[0,134,66],[0,1,0],radius,radius-2,2,state)
    return p.finish()


def half_product():
    p=Part('12_双手之间的半成品机械核心');center=np.array([0,211,68])
    q=np.arange(-46,47);x,y,z=np.meshgrid(q,q,q,indexing='ij');r=np.sqrt(x*x+y*y+z*z)
    shell=(r<=43)&(r>=37)&(y<=0)
    coords=np.c_[x[shell],y[shell],z[shell]]+center
    p.points(coords,WHITE)
    belt=(r<=44)&(r>=40)&(y<=0)&((abs(x)<5)|(abs(z)<5))
    p.points(np.c_[x[belt],y[belt],z[belt]]+center,BLUE)
    p.sphere(center,12,BLACK);annulus(p,center+[0,0,12],[0,0,1],9,5,2,BLUE)
    # 完成部分为齿轮机壳，上半部只保留蓝色构造框。
    for radius,cy in [(35,-15),(43,-4)]:
        annulus(p,center+[0,cy,0],[0,1,0],radius,radius-4,4,DARK)
        for angle in np.linspace(0,2*math.pi,16,endpoint=False):
            c=center+[radius*math.cos(angle),cy,radius*math.sin(angle)];p.box(c-2,c+2,SILVER)
    for angle in np.linspace(0,2*math.pi,8,endpoint=False):
        path=[center+[43*math.cos(a)*math.cos(angle),43*math.sin(a),43*math.cos(a)*math.sin(angle)] for a in np.linspace(0,math.pi/2,26)]
        tube(p,path,1.3,BLUE)
    for height in [13,27,38]:
        radius=math.sqrt(43**2-height**2)
        annulus(p,center+[0,height,0],[0,1,0],radius,radius-1.5,1.6,GLASS)
    for dx,dy,dz,n in [(-25,32,5,6),(17,35,15,5),(34,18,-3,7),(-15,24,-31,4),(1,45,-8,5)]:
        c=center+[dx,dy,dz];p.box(c-n/2,c+n/2,GLASS)
        p.beam(c+[-n/2,n/2,-n/2],c+[n/2,n/2,-n/2],1,BLUE)
    return p.finish()


def maintenance():
    p=Part('13_背部开放检修支架')
    for s in [-1,1]:
        outline=[(s*126,-187),(s*90,-187),(s*86,-139),(s*115,-139)]
        plate(p,outline,36,47,BLACK)
        path=[[s*108,43,-153],[s*108,293,-153],[s*75,333,-153],[s*25,349,-153]]
        tube(p,path,6,BLACK);tube(p,[np.array(a)+[0,0,7] for a in path],2.5,WHITE)
        tube(p,[np.array(a)+[0,0,10] for a in path],1,BLUE)
        for y in range(70,294,28):p.beam([s*99,y,-157],[s*117,y+10,-157],1.4,SILVER)
        # 管线止于背部后方，留下间隙，不改19C任何方块。
        for y in [245,280]:
            path=[[s*106,y,-148],[s*74,y+8,-143],[s*29,y+8,-128]]
            tube(p,path,3,BLACK);tube(p,[np.array(a)+[0,2,0] for a in path],1,BLUE)
    p.beam([-25,349,-153],[25,349,-153],6,BLACK)
    p.beam([-24,351,-145],[24,351,-145],2,BLUE)
    annulus(p,[0,266,-148],[0,0,1],36,31,5,WHITE)
    annulus(p,[0,266,-144],[0,0,1],32,30,2,BLUE)
    return p.finish()


def chain_well():
    p=Part('14_节链下方约束井')
    for y,radius in [(6,22),(14,25),(26,28),(39,29)]:
        annulus(p,[0,y,-107],[0,1,0],radius,radius-3,4,WHITE if y==39 else BLACK)
        annulus(p,[0,y+2,-107],[0,1,0],radius-1,radius-2,1,BLUE)
    for x in [-25,25]:p.box([x-3,6,-125],[x+3,37,-89],BLACK)
    annulus(p,[0,4,-107],[0,1,0],17,0,1,GLASS)
    annulus(p,[0,5,-107],[0,1,0],13,11,1,LIGHT)
    return p.finish()


def treatment_targets():
    p=Part('15_双炮前方材料处理靶台')
    for s in [-1,1]:
        yaw=math.radians(s*(9 if s<0 else 14));pitch=math.radians(-5 if s<0 else 3)
        forward=np.array([math.sin(yaw)*math.cos(pitch),math.sin(pitch),math.cos(yaw)*math.cos(pitch)])
        origin=np.array([s*92,286+(7 if s>0 else -2),-47])+SHIFT
        center=origin+forward*184
        annulus(p,center,forward,14,11,4,BLACK)
        annulus(p,center+forward*3,forward,13,10,2,WHITE)
        annulus(p,center+forward*5,forward,10,8,1,BLUE)
        annulus(p,center+forward*2,forward,7,0,2,GLASS)
        _,u,w=basis(forward)
        for a in np.arange(4)*math.pi/2:
            r=u*math.cos(a)+w*math.sin(a);p.beam(center+r*14,center+r*20,2,WHITE)
        # 光束只跨越炮口后的短净空，靶台是静态构图设施。
        p.beam(origin+forward*148,center-forward*4,.85,GLASS)
    return p.finish()


def construct_lines():
    p=Part('16_双掌构造线与下方扫描框')
    for s in [-1,1]:
        start=np.array([s*108,208,44]);end=np.array([s*43,215,66])
        for dy in [-5,5]:p.beam(start+[0,dy,0],end+[0,dy,0],.7,GLASS)
        p.beam([s*55,145,17],[s*55,156,17],1.5,BLUE)
        p.beam([s*55,156,17],[s*55,156,114],1,GLASS)
    p.beam([-55,156,114],[55,156,114],1,GLASS)
    return p.finish()


def front_control():
    p=Part('17_前控舰桥与出货轨道')
    outline=[(-55,204),(-35,190),(35,190),(55,204),(45,246),(-45,246)]
    plate(p,outline,0,7,BLACK);plate(p,outline,7,10,WHITE)
    for s in [-1,1]:
        hull(p,[(s*38,10,214),(s*50,10,228),(s*42,43,226),(s*30,34,213)],WHITE)
        p.beam([s*34,15,215],[s*39,39,224],2,BLUE)
        for x in [s*15,s*25]:
            p.box([x-3,18,228],[x+3,25,232],BLACK)
            p.box([x-2,20,233],[x+2,23,234],SILVER)
    p.box([-8,14,227],[8,31,233],BLACK)
    p.box([-6,17,234],[6,29,235],BLUE)
    p.box([-2,21,236],[2,25,236],LIGHT)
    # 升降转运架连接高位装配床与低位出货轨，避免两段工序悬空脱节。
    for x in [-32,32]:
        p.box([x-5,0,132],[x+5,5,161],WHITE)
        for z in [137,155]:
            p.box([x-2,5,z-2],[x+2,133,z+2],BLACK)
            p.box([x-1,8,z+3],[x+1,131,z+3],BLUE)
            for y in range(16,131,19):p.beam([x-3,y,z+3],[x+3,y,z+3],1,SILVER)
    p.box([-32,130,132],[32,133,158],BLACK)
    p.box([-30,134,138],[30,135,145],SILVER)
    p.box([-28,55,135],[28,58,157],BLACK)
    for x in [-25,25]:p.beam([x,59,135],[x,59,157],1,BLUE)
    for z in range(141,202):
        y=round(57-(z-141)*.53)
        p.box([-27,y-3,z],[27,y,z],BLACK)
        for x in [-25,25]:p.box([x-1,y+1,z],[x+1,y+2,z],WHITE)
        for x in [-14,14]:p.box([x-1,y+1,z],[x+1,y+1,z],BLUE)
        if z%10==0:p.beam([-20,y+1,z],[20,y+1,z],1,SILVER)
    # 静态成品托盘，让中央加工区与前方出口有明确联系。
    for x in [-15,15]:p.beam([x,67,159],[x,67,179],4,WHITE)
    p.box([-17,60,157],[17,63,181],BLACK)
    annulus(p,[0,70,169],[0,1,0],12,8,5,BLUE)
    return p.finish()


def build():
    _,prior,source=robot.build();parts=[]
    for old in source:
        p=Part(old.name);p.points(old.p+SHIFT,STATES[0]);p=p.finish();p.states=old.states.copy()
        assert np.array_equal(p.p-SHIFT,old.p) and np.array_equal(p.states,old.states),'19C原形发生变化'
        parts.append(p)
    robot_count=len(parts)
    parts+=[deck()]+[process_module(s,i,z) for s in [-1,1] for i,z in enumerate([-110,15,140])]
    parts += [supply_rails(),assembly_bed(),half_product(),maintenance(),chain_well(),treatment_targets(),construct_lines(),front_control()]
    assert len(parts)==EXPECTED_PARTS
    protected=np.concatenate([encode(p.p) for p in parts[:robot_count]])
    intersections=[]
    for p in parts[robot_count:]:
        shared=np.intersect1d(protected,encode(p.p))
        if len(shared):intersections.append(dict(component=p.name,shared_voxels=len(shared)))
    assert not intersections,intersections
    points=np.concatenate([p.p for p in parts]);low,high=points.min(0),points.max(0);size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        at=p.p-low;cube[at[:,1],at[:,2],at[:,0]]=p.states
    data=deepcopy(prior)
    for key in list(data):
        if key.startswith('geometry_delta') or key.startswith('other_components_unchanged'):data.pop(key)
    data.update(name='hk3gtl-w02-19c-dock-scene-a1-20261110',title='理之律者 · 万象·自律工业矩阵 · 19C构造船坞A1',
        candidate_version='W02-19C构造船坞-A1',display_version=VERSION,size=size.tolist(),blocks=int(np.count_nonzero(cube)),
        blueprint_to_export_offset_xyz=(-low).tolist(),blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),
        component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
        component_overlaps=deepcopy(prior['component_overlaps']),base_candidate=PRIOR.relative_to(ROOT).as_posix()+'/index.html',center_blueprint=[0,211,68],
        robot_geometry_preserved=True,robot_translation_xyz=SHIFT.tolist(),robot_components_preserved=robot_count,
        added_components=len(parts)-robot_count,robot_scene_shared_voxels=intersections,industrial_scene_layout_complete=True,
        original_robot_component_overlaps_retained=True,scene_junctions_not_exhaustively_classified=True,
        scene_inventions=True,animation_enabled=False,approved=False,installed=False,game_verified=False,matrix_layout_complete=False,
        controller=None,ports=[],controller_visual_marker=[0,23,236],
        summary='V6重装小兔整体平移，原形与材质不变；六站U形供料船坞围绕双手间的半成品核心，背后开放维护架与节链井、双炮前方处理靶台、前方出货轨和控制舰桥组成同一条构造工序。')
    data['detail_changes']=[
        dict(component='19C原形保留',references=['V6'],change='11个构件只整体平移(0,+40,-70)，不缩放、不改姿态或颜色。'),
        dict(component='U形工业船坞',references=['本轮组合设计'],change='两侧各三座低矮加工模块、供料轨和汇流桥，中前方保持敞开视线。'),
        dict(component='双手构造场',references=['本轮组合设计'],change='双掌之间的半成品机械核心，下半为实体齿轮甲壳，上半为蓝色构造框。'),
        dict(component='背部与工序联系',references=['本轮组合设计'],change='开放维护架、链尖下方约束井、沿现有炮口布置的处理靶台、前控与出货轨。')]
    data['source_conflicts']=[
        '重装小兔V6造型保留，沿用60张分源参考；不同时间点不等于60个独立机位。',
        '船坞、中央半成品与工序分工为本项目创作，不冒充官方19C场景或原作新增设定。',
        '19C原形只整体平移，名义649×493×303不作为裁切窗口；实际尺寸由完整构件求得。',
        '静态光线、构造框及半成品均为真实候选方块，没有动画或粒子演出。',
        '前控为视觉示意，没有注册机器控制器、接口能力、配方与研究链；未进行游戏实装测试。',
        '新增设施与19C无共享体素；新增设施之间的供料连接属于有意接合，未宣称全部净空验收。']
    return cube,data,parts
