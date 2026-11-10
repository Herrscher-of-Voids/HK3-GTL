# -*- coding: utf-8 -*-
"""原案还原：五矛、四翼、八边悬环和十二刺桩；不为递增指标增料。"""
import json,math
from pathlib import Path
import numpy as np
from scipy import ndimage
from i42_prefabrication_geometry_v1_20261028 import Material
from structure_size_baseline import baselines

ROOT=Path(__file__).resolve().parents[2]
W,H,D=673,321,529
M=Material()
PURPLE='minecraft:purple_concrete';PINK='minecraft:magenta_concrete'
GLASSES=['minecraft:purple_stained_glass','minecraft:pink_stained_glass','minecraft:white_stained_glass']
STATES=sorted({M.ATOMIC,M.ROBUST,M.CONTROL,M.PORT,M.LIGHT,M.LASER,M.DIMENSION,M.COMPUTER,M.VENT,
    M.IRIDIUM,M.STRESS,M.TURBINE,M.STEEL_PIPE,M.GRATE,PURPLE,PINK,'minecraft:magenta_stained_glass',*GLASSES})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'原案中的矛脊、隔离层、锚定器或主控室构件' for s in STATES}
ROLES.update({M.ATOMIC:'黑色合金矛脊与悬环骨架',PURPLE:'深紫色隔离壳',PINK:'品红色刻线与刺桩光芯',
    M.LIGHT:'光带背光；预览使用真实材质静态首帧',M.CONTROL:'中心锚点基座主控占位',
    M.PORT:'十二锚定器内的通用接口占位，不限制输入输出',
    GLASSES[0]:'光翼内侧深紫玻璃',GLASSES[1]:'光翼中段粉色玻璃',GLASSES[2]:'光翼外缘白色玻璃'})


def build():
    c=np.zeros((H,D,W),np.uint8);zz,xx=np.ogrid[:D,:W];X=xx-336;Z=zz-264
    radius=np.sqrt(X*X+Z*Z);angle=np.arctan2(Z,X)
    def box(a,b,s):
        x,y,z=map(int,a);x1,y1,z1=map(int,b)
        assert 0<=x<=x1<W and 0<=y<=y1<H and 0<=z<=z1<D,(a,b)
        c[y:y1+1,z:z1+1,x:x1+1]=IDS[s] if s else 0
    roots=[(336,0),(672,200),(540,528),(0,442),(28,48)]
    arms=[];zones=[]
    # 五条中空矛梁随高度向内收束；每条保留独立矛根和上弯冠刺。
    for i,(rx,rz) in enumerate(roots):
        v=np.array([rx-336,rz-264],float);length=np.linalg.norm(v);v/=length
        tangent=np.array([-v[1],v[0]]);th=math.atan2(v[1],v[0])
        for y in range(0,219):
            t=max(0,(y-15)/203);rr=length+(132-length)*(t**.82)
            cx,cz=np.array([336,264])+rr*v
            half_t=31-17*t;half_r=24-12*t
            a=np.abs((xx-cx)*tangent[0]+(zz-cz)*tangent[1]);b=np.abs((xx-cx)*v[0]+(zz-cz)*v[1])
            q=np.maximum(a/half_t,b/half_r);mask=(q<=1)&(q>=1-3/min(half_t,half_r))
            c[y][mask]=IDS[M.ATOMIC]
            c[y][mask&(b<half_r*.75)&(a>half_t-3)]=IDS[PURPLE]
            c[y][mask&(a<3)]=IDS[PINK if y%36<5 else M.ROBUST]
            c[y][mask&(y%36<2)]=IDS[M.LIGHT]
            if y<20:
                rootmask=(a/42+b/34<=1)&(a/42+b/34>=.50)
                c[y][rootmask]=IDS[M.STRESS if y<5 else M.ATOMIC]
        # 冠刺在梁端继续上弯，五个尖端高度不同，最高点为原案321格。
        top=[320,306,312,294,300][i]
        for y in range(216,top+1):
            t=(y-216)/(top-216);rr=132-20*t;cx,cz=np.array([336,264])+rr*v
            a=np.abs((xx-cx)*tangent[0]+(zz-cz)*tangent[1]);b=np.abs((xx-cx)*v[0]+(zz-cz)*v[1])
            width=max(.7,14*(1-t));q=a+b
            c[y][q<=width]=IDS[M.ATOMIC]
            c[y][(q<=width)&(a<1.2)]=IDS[PINK]
        arms.append(dict(id=f'亚空之矛{i+1}',root=[rx,0,rz],angle=th,length=round(length,3),crown_top=top))
        p=np.rint(np.array([336,264])+132*v).astype(int)
        zones.append(dict(name=f'亚空之矛{i+1} · 中空梁与冠刺',pos=[int(p[0]),218,int(p[1])]))
    wings=[]
    # 四张独立扇面为三格薄壳；染色玻璃分带和35格光带均按实体导出。
    for i in range(4):
        a=arms[i]['angle'];b=arms[i+1]['angle'];span=(b-a)%(2*math.pi)
        u=((angle-a)%(2*math.pi))/span;between=u<=1
        outer=((1-u)*arms[i]['length']+u*arms[i+1]['length'])*(1-.20*np.sin(np.pi*np.clip(u,0,1)))
        t=(radius-131)/np.maximum(1,outer-131)
        pupil=(np.abs(X)+np.abs(Z)<175)|((np.abs(X)<17)&(np.abs(Z)<173))|((np.abs(Z)<17)&(np.abs(X)<173))
        mask=between&(t>=0)&(t<=.97)&~pupil
        heights=np.rint(204-180*np.maximum(t,0)**.82+8*np.sin(np.pi*np.clip(u,0,1))).astype(int)
        zs,xs=np.where(mask);ys=heights[zs,xs]
        values=np.asarray([IDS[s] for s in GLASSES],np.uint8)[np.minimum(2,(t[zs,xs]*3).astype(int))]
        bands=(np.mod(radius[zs,xs],35)<2.2)
        for dy in range(3):
            val=np.where(bands,IDS['minecraft:magenta_stained_glass'] if dy else IDS[M.LIGHT],values)
            c[ys+dy,zs,xs]=val
        wings.append(dict(id=f'光翼{i+1}',between=[i+1,i+2],thickness=3,light_band_spacing=35,cells=int(mask.sum())*3))
    # 八边形中心线半径135、外径275；5×5管壳内留3×3空腔。
    octagonal=np.maximum.reduce([np.broadcast_to(np.abs(X),(D,W)),np.broadcast_to(np.abs(Z),(D,W)),(np.abs(X)+np.abs(Z))/math.sqrt(2)])
    ringmask=np.abs(octagonal-135)<=2
    for y in range(198,203):
        mask=ringmask if y in (198,202) else ringmask&(np.abs(octagonal-135)>1)
        c[y][mask]=IDS[PURPLE if y%2 else M.ATOMIC]
        c[y][mask&(np.abs(X)<2)]=IDS[PINK]
        c[y][mask&(np.abs(Z)<2)]=IDS[PINK]
    anchors=[];ports=[];routes=[]
    machines=[M.LASER,M.DIMENSION,M.COMPUTER,M.IRIDIUM]
    for i in range(12):
        th=2*math.pi*i/12;v=np.array([math.cos(th),math.sin(th)])
        radial=123/max(abs(v[0]),abs(v[1]),(abs(v[0])+abs(v[1]))/math.sqrt(2))
        cx,cz=np.rint(np.array([336,264])+radial*v).astype(int)
        tip=80+(i%3)*10
        for y in range(tip,201):
            r=max(0,10*(y-tip)/(200-tip));local=np.maximum(np.abs(xx-cx),np.abs(zz-cz))
            c[y][(local<=r)&(local>=max(0,r-2))]=IDS[M.ATOMIC]
            c[y,cz,cx]=IDS[PINK]
        box((cx-10,180,cz-10),(cx+10,197,cz+10),M.ROBUST)
        box((cx-8,182,cz-8),(cx+8,195,cz+8),None)
        box((cx-6,182,cz-6),(cx+6,185,cz+6),machines[i%4])
        box((cx-5,186,cz-5),(cx+5,189,cz-3),M.VENT)
        # 管壳直接接到上下两端冷却设备，无悬空装饰管。
        for y in (184,192):box((cx+4,y,cz+2),(cx+8,y+2,cz+6),M.TURBINE)
        box((cx+6,185,cz+4),(cx+6,193,cz+4),M.STEEL_PIPE)
        routes.append(dict(id=f'锚定器{i+1}内部冷却支路',start=[int(cx+6),185,int(cz+4)],end=[int(cx+6),193,int(cz+4)]))
        # 顶部短挂耳只连接环与锚定器，不扩大环体截面。
        outer=v*(radial+15);ox,oz=np.rint(np.array([336,264])+outer).astype(int)
        for x,z in np.rint(np.linspace([cx,cz],[ox,oz],25)).astype(int):box((x-1,198,z-1),(x+1,200,z+1),M.ATOMIC)
        pos=[int(cx),190,int(cz-10)];box(pos,pos,M.PORT)
        box((cx-2,188,cz-15),(cx+2,192,cz-11),None)
        ports.append(dict(id=f'锚定器{i+1:02}通用舱位',pos=pos,face='north',group='generic',purpose='原案高位锚定器内部舱位；不限制物品、流体或能源输入输出'))
        anchors.append(dict(id=i+1,center=[int(cx),200,int(cz)],tip=[int(cx),tip,int(cz)],length=200-tip))
        zones.append(dict(name=f'锚定器{i+1:02} · 倒锥刺桩',pos=[int(cx),197,int(cz)]))
    # 菱形—十字瞳孔开口保持贯通；地面仅设独立中央基座，不补满地板。
    diamond=np.abs(X)/49+np.abs(Z)/49
    for y in range(0,41):
        mask=(diamond<=1)&((diamond>=.80)|(y<4)|(y>36))
        c[y][mask]=IDS[M.ATOMIC if y%10 else PURPLE]
    box((295,8,220),(377,25,224),M.ATOMIC)
    box((297,10,220),(375,23,220),PURPLE)
    control=[336,16,220];box(control,control,M.CONTROL)
    box((331,9,214),(341,23,219),None)
    # 窄道侧向进入主控室，窄道地板与主控室相接，不连接空中环。
    box((281,4,254),(301,5,263),M.GRATE)
    box((295,6,255),(298,19,262),None)
    paths=[dict(min=[331,9,214],max=[341,23,219]),dict(min=[295,6,255],max=[298,19,262])]
    # 剔除曲面采样产生的1～3格孤立碎屑，不补梁、补底或扩大主体。
    labels,n=ndimage.label(c!=0);sizes=np.bincount(labels.ravel());tiny=np.flatnonzero(sizes<=3)
    c[np.isin(labels,tiny)]=0
    del labels
    data=dict(key='w03',name='hk3gtl-w03-falling-crown-v2-20261107',candidate_version='V2',
        title='空之律者 · 穹界·虚数锚定环 · 坠落冠冕（DeepSeek原案）',size=[W,H,D],
        controller=control,controller_face='north',ports=ports,zones=zones,paths=paths,pipe_routes=routes,
        target_voltage='CIV',appearance_voltage='原案紫黑／品红',character='西琳',arms=arms,wings=wings,anchors=anchors,
        description='五根不等长的亚空之矛从五处地面矛根向内上弯，抓住Y200的八边悬环；四张三格厚渐变光翼在矛脊之间张开。十二根80～120格倒锥刺桩向下悬垂，五根高低不同的冠刺围成未闭合冠冕。中央空域保留菱形—十字瞳孔意象与独立地面主控基座。',
        purpose='忠于负责人提供的DeepSeek文字方案，供与独立V1比较；保留空心矛梁、薄光翼、5×5悬环与紫黑品红配色，不按递增规则增料，不把阶段成型、传送或实体表现当作已实现。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1)
    assert all(counts[1:]),[(s,int(n)) for s,n in zip(STATES,counts[1:]) if not n]
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]));occupied=c!=0
    bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)));bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);components=np.bincount(labels.ravel())[1:];del labels,occupied
    assert n==2 and min(components)>100000,('原案空中主体与独立地面基座',n,components)
    assert palette[M.CONTROL]==1 and palette[M.PORT]==12
    markers=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        x,y,z=item['pos'];assert c[y,z+1,x]
        assert all(c[y+dy,z,x+dx] for dx,dy in ((-1,0),(1,0),(0,1),(0,-1)))
        assert not np.any(c[y,z-5:z,x]);markers.append(dict(id=item['id'],position=item['pos'],flush_shell=True,inner_backed=True,outer_clear=5))
    for path in data['paths']:
        x,y,z=path['min'];x1,y1,z1=path['max'];assert not np.any(c[y:y1+1,z:z1+1,x:x1+1])
    for r in data['pipe_routes']:
        x,y,z=r['start'];x1,y1,z1=r['end'];assert (x,z)==(x1,z1)
        assert np.all(c[y:y1+1,z,x]==IDS[M.STEEL_PIPE])
        assert c[y,z,x+1]==IDS[M.TURBINE] and c[y1,z,x+1]==IDS[M.TURBINE]
    baseline=baselines()['W03']['size'];metrics=dict(blocks=int(counts[1:].sum()),materials=len(STATES)-2,volume=W*H*D,height=H)
    prior=json.loads((ROOT/'logs/w03-anchor-v1-20261107/voltage-progression.json').read_text(encoding='utf8'))
    passes={k:metrics[k]>v['value'] for k,v in prior['lower_maxima'].items()}
    return dict(passed=True,geometry_passed=True,design_rules_passed=False,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),
        blocks=metrics['blocks'],unique_materials=len(STATES),ordinary_materials=metrics['materials'],palette=palette,
        bounding_box_volume=metrics['volume'],height=H,baseline_check=dict(passed=True,baseline_wdh=baseline),
        voltage_progression=dict(passed=all(passes.values()),passes=passes,metrics=metrics,lower_form_count=prior['lower_form_count'],
            lower_maxima=prior['lower_maxima'],source='logs/w03-anchor-v1-20261107/voltage-progression.json',
            comparison='仅记录原案与现行规则差距；负责人要求暂不改变方块量，不为递增指标改造原案。'),
        connectivity=dict(components=int(n),component_blocks=sorted(map(int,components),reverse=True),
            interpretation='空中主体与独立地面主控基座两部分；不以连接补料改写原案。'),
        port_checks=markers,pipe_routes_count=12,pipe_routes_passed=True,open_pipe_ends=0,character='西琳',
        arm_count=5,wing_count=4,anchor_count=12,ring_outer_diameter=275,ring_y=200,ring_section=[5,5],
        original_estimated_blocks=[800000,1500000],block_count_in_original_estimate=800000<=metrics['blocks']<=1500000,
        checks=['五根不等长矛脊、四片三格薄翼、十二根倒锥刺桩及五根高低冠刺均为实际方块。',
            '八边悬环位于Y200，外径275，管状截面5×5并保留内腔。','中央基座主控宽度居中，十二个高位接口均通用并保留五格净空。',
            '十二条内部冷却支路逐格核对两端设备。','原案紫黑／品红配色与空心薄壳保留，不为递增规则加料。'],
        not_verified=['本版是DeepSeek原案还原预览，不满足既定HCV主材与规模递增规则；不是可接入正式候选。',
            '阶段成型、12～16渲染分区、配方解锁、8GB性能、游戏注册及运行均未实现或验收。',
            '原文对刺桩触地与五矛根触地描述有冲突；采用后文基座与五矛根触地、刺桩悬垂。',
            '原文未给逐格坐标，曲线、玻璃分带、设备细节与五向角度为本次几何解释；并非DeepSeek直接输出的施工图。'])


if __name__=='__main__':
    cube,data=build();v=audit(cube,data);print(json.dumps({k:v[k] for k in ('blocks','unique_materials','connectivity','voltage_progression')},ensure_ascii=False))
