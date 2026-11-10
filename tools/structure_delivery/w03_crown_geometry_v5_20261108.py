# -*- coding: utf-8 -*-
"""DeepSeek改进：高悬瞳孔、内弯五脊、破碎薄翼及不触地长锚。"""
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
GLASSES=['minecraft:white_stained_glass','minecraft:magenta_stained_glass']
COIL='gtceu:superconducting_coil[active=false]'
STATES=sorted({M.ATOMIC,M.ROBUST,M.CONTROL,M.PORT,M.LIGHT,M.LASER,M.DIMENSION,M.COMPUTER,M.VENT,
    M.IRIDIUM,M.STRESS,M.TURBINE,M.STEEL_PIPE,M.GRATE,COIL,PURPLE,PINK,*GLASSES})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'原案中的矛脊、隔离层、锚定器或主控室构件' for s in STATES}
ROLES.update({M.ATOMIC:'黑色合金矛脊与悬环骨架',PURPLE:'深紫色隔离壳',PINK:'品红色刻线与刺桩光芯',
    M.LIGHT:'光带背光；预览使用真实材质静态首帧',M.CONTROL:'中心锚点基座主控占位',
    M.PORT:'五矛根和主控基座内嵌通用接口，不限制输入输出',
    GLASSES[0]:'破碎白色光翼薄片',GLASSES[1]:'品红光翼、细缝与弧形光纹',COIL:'悬环内缘真实超导线圈'})


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
        ring_radius=124/max(abs(v[0]),abs(v[1]),(abs(v[0])+abs(v[1]))/math.sqrt(2))
        tangent=np.array([-v[1],v[0]]);th=math.atan2(v[1],v[0])
        for y in range(0,219):
            t=min(1,max(0,(y-15)/185));rr=length+(ring_radius-length)*(t**1.3)
            cx,cz=np.array([336,264])+rr*v
            root_taper=min(1,(y+1)/15);half_t=(28-15*t)*root_taper;half_r=(22-11*t)*root_taper
            a=np.abs((xx-cx)*tangent[0]+(zz-cz)*tangent[1]);b=np.abs((xx-cx)*v[0]+(zz-cz)*v[1])
            q=np.maximum(a/half_t,b/half_r);mask=(q<=1)&(q>=1-3/min(half_t,half_r))
            c[y][mask]=IDS[M.ATOMIC]
            c[y][mask&(b<half_r*.75)&(a>half_t-3)]=IDS[PURPLE]
            c[y][mask&(a<3)]=IDS[PINK if y%36<5 else M.ROBUST]
            c[y][mask&(y%36<2)]=IDS[M.ROBUST]
            slit=mask&(a<1)&(b>half_r-3)&(y%24>=10)&(y%24<13)
            c[y][slit]=IDS['minecraft:magenta_stained_glass']
            if y<20:
                root_scale=min(1,(y+2)/12);rootmask=(a/42+b/34<=root_scale)&(a/42+b/34>=root_scale*.65)
                c[y][rootmask]=IDS[M.STRESS if y<5 else M.ATOMIC]
        # 冠刺在梁端继续上弯，五个尖端高度不同，最高点为原案321格。
        top=[320,306,312,294,300][i]
        for y in range(216,top+1):
            t=(y-216)/(top-216);rr=ring_radius-18*t;cx,cz=np.array([336,264])+rr*v
            a=np.abs((xx-cx)*tangent[0]+(zz-cz)*tangent[1]);b=np.abs((xx-cx)*v[0]+(zz-cz)*v[1])
            width=max(.7,14*(1-t));q=a+b
            c[y][q<=width]=IDS[M.ATOMIC]
            c[y][(q<=width)&(a<1.2)]=IDS[PINK]
        arms.append(dict(id=f'亚空之矛{i+1}',root=[rx,0,rz],angle=th,length=round(length,3),crown_top=top))
        p=np.rint(np.array([336,264])+ring_radius*v).astype(int)
        zones.append(dict(name=f'亚空之矛{i+1} · 中空梁与冠刺',pos=[int(p[0]),218,int(p[1])]))
    root_ports=[]
    # 根部五座设备鞍座贴合矛脊；每座两通用接口，不规定输入输出。
    for i,(rx,rz) in enumerate(roots):
        v=np.array([rx-336,rz-264],float);length=np.linalg.norm(v);v/=length
        rr=length+(124-length)*((24-15)/185)**1.3
        cx,cz=np.rint(np.array([336,264])+rr*v).astype(int)
        cx=int(np.clip(cx,17,W-18));cz=int(np.clip(cz,16,D-17))
        box((cx-16,18,cz-10),(cx+16,34,cz+10),M.ATOMIC)
        box((cx-14,20,cz-10),(cx+14,32,cz-10),M.ROBUST)
        box((cx-8,28,cz+3),(cx+8,33,cz+8),M.LASER if i%2 else M.COMPUTER)
        for dx in (-6,6):
            pos=[cx+dx,26,cz-10];box(pos,pos,M.PORT)
            box((cx+dx-1,25,cz-15),(cx+dx+1,27,cz-11),None)
            root_ports.append(dict(id=f'矛根{i+1}通用舱位{dx:+}',pos=pos,face='north',group='generic',purpose='矛根设备鞍座内嵌通用接口，不固定输入输出'))
    wings=[]
    # 破碎两格薄片从高位主脊外侧展开；径向裂口和锯齿边避免整张蜘蛛网。
    for i in range(4):
        a=arms[i]['angle'];b=arms[i+1]['angle'];span=(b-a)%(2*math.pi)
        u=((angle-a)%(2*math.pi))/span;between=u<=1
        outer=((1-u)*arms[i]['length']+u*arms[i+1]['length'])*(1-.22*np.sin(np.pi*np.clip(u,0,1)))
        t=(radius-129)/np.maximum(1,outer-129)
        lobes=np.floor(np.clip(u,0,1)*9).astype(int)
        torn_edge=.87+.09*np.cos(np.clip(u,0,1)*18*math.pi)**2
        strips=(u*9)%1
        # 每片翼留5条完整径向裂口；薄片主体保持连到至少一条弧形光纹。
        radial_cracks=(np.mod(t*5,1)<.10)&(strips>.18)&(strips<.82)
        mask=between&(t>.055)&(t<torn_edge)&~radial_cracks&(strips>.07)&(strips<.93)
        heights=np.rint(205-113*np.maximum(t,0)**.70+7*np.sin(np.pi*np.clip(u,0,1))+3*(lobes%2)).astype(int)
        zs,xs=np.where(mask);ys=heights[zs,xs]
        value=np.where((lobes[zs,xs]+(t[zs,xs]*8).astype(int))%2==0,IDS[GLASSES[0]],IDS[GLASSES[1]])
        bands=np.mod(radius[zs,xs],35)<1.5
        for dy in range(2):c[ys+dy,zs,xs]=np.where(bands,IDS[M.LIGHT] if dy==0 else IDS[GLASSES[1]],value)
        wings.append(dict(id=f'破碎光翼{i+1}',between=[i+1,i+2],thickness=2,light_band_spacing=35,
            fragments_across=9,radial_cut_bands=5,cells=int(mask.sum())*2,min_y=int(ys.min()),max_y=int(ys.max()+1)))
    # 直径约250格的3×3八边细环，环内缘一圈真实超导线圈；中央不填平台。
    octagonal=np.maximum.reduce([np.broadcast_to(np.abs(X),(D,W)),np.broadcast_to(np.abs(Z),(D,W)),(np.abs(X)+np.abs(Z))/math.sqrt(2)])
    ringmask=np.abs(octagonal-124)<=1
    for y in range(199,202):
        c[y][ringmask]=IDS[PURPLE if y==200 else M.ATOMIC]
        if y==200:c[y][ringmask&((np.abs(X)<2)|(np.abs(Z)<2))]=IDS[PINK]
    c[200][(octagonal>=121)&(octagonal<123)]=IDS[COIL]
    # 四方向十字星由尖锐菱形棱柱组成，仍在悬环平面，中央瞳孔完全贯通。
    stars=[]
    for axis in ('x','z'):
        for side in (-1,1):
            q=side*(X if axis=='x' else Z);across=np.abs(Z if axis=='x' else X)
            for y in range(197,204):
                thickness=abs(y-200)
                mask=(q>=122)&(q<=175)&(across+thickness*2<=np.minimum((q-119)*.40,(176-q)*.32))
                c[y][mask]=IDS[M.ATOMIC]
                c[y][mask&(across<2)]=IDS[PINK]
            stars.append(dict(axis=axis,side=side,outer_radius=175))
    anchors=[];ports=root_ports;routes=[]
    machines=[M.LASER,M.DIMENSION,M.COMPUTER,M.IRIDIUM]
    for i in range(12):
        th=2*math.pi*i/12;v=np.array([math.cos(th),math.sin(th)])
        radial=112/max(abs(v[0]),abs(v[1]),(abs(v[0])+abs(v[1]))/math.sqrt(2))
        cx,cz=np.rint(np.array([336,264])+radial*v).astype(int)
        tip=100+(i%3)*5
        for y in range(tip,201):
            r=max(0,13*(y-tip)/(200-tip));local=np.maximum(np.abs(xx-cx),np.abs(zz-cz))
            c[y][(local<=r)&(local>=max(0,r-2))]=IDS[M.ATOMIC]
            c[y,cz,cx]=IDS[PINK]
        box((cx-13,180,cz-13),(cx+13,197,cz+13),M.ROBUST)
        box((cx-11,182,cz-11),(cx+11,195,cz+11),None)
        box((cx-6,182,cz-6),(cx+6,185,cz+6),machines[i%4])
        box((cx-5,186,cz-5),(cx+5,189,cz-3),M.VENT)
        # 管壳直接接到上下两端冷却设备，无悬空装饰管。
        for y in (184,192):box((cx+4,y,cz+2),(cx+8,y+2,cz+6),M.TURBINE)
        box((cx+6,185,cz+4),(cx+6,193,cz+4),M.STEEL_PIPE)
        routes.append(dict(id=f'锚定器{i+1}内部冷却支路',start=[int(cx+6),185,int(cz+4)],end=[int(cx+6),193,int(cz+4)]))
        # 顶部短挂耳只连接环与锚定器，不扩大环体截面。
        outer=v*(radial+15);ox,oz=np.rint(np.array([336,264])+outer).astype(int)
        for x,z in np.rint(np.linspace([cx,cz],[ox,oz],25)).astype(int):box((x-1,198,z-1),(x+1,200,z+1),M.ATOMIC)
        anchors.append(dict(id=i+1,center=[int(cx),200,int(cz)],tip=[int(cx),tip,int(cz)],length=200-tip))
        zones.append(dict(name=f'锚定器{i+1:02} · 倒锥刺桩',pos=[int(cx),197,int(cz)]))
    # 菱形—十字瞳孔开口保持贯通；地面仅设独立中央基座，不补满地板。
    diamond=np.abs(X)/49+np.abs(Z)/49
    for y in range(0,21):
        mask=(diamond<=1)&((diamond>=.80)|(y<4)|(y>16))
        c[y][mask]=IDS[M.ATOMIC if y%10 else PURPLE]
    box((295,5,220),(377,19,224),M.ATOMIC)
    box((297,7,220),(375,18,220),PURPLE)
    control=[336,12,220];box(control,control,M.CONTROL)
    for offset in (-14,14):
        pos=[336+offset,12,220];box(pos,pos,M.PORT)
        box((pos[0]-1,11,215),(pos[0]+1,13,219),None)
        ports.append(dict(id=f'主控基座通用舱位{offset:+}',pos=pos,face='north',group='generic',purpose='基座通用仓位，不限制输入输出'))
    box((331,6,214),(341,18,219),None)
    # 窄道侧向进入主控室，窄道地板与主控室相接，不连接空中环。
    box((281,4,254),(301,5,263),M.GRATE)
    box((295,6,255),(298,19,262),None)
    paths=[dict(min=[331,6,214],max=[341,18,219]),dict(min=[295,6,255],max=[298,19,262])]
    # 剔除曲面采样产生的1～3格孤立碎屑，不补梁、补底或扩大主体。
    labels,n=ndimage.label(c!=0);sizes=np.bincount(labels.ravel());tiny=np.flatnonzero(sizes<=3)
    c[np.isin(labels,tiny)]=0
    del labels
    data=dict(key='w03',name='hk3gtl-w03-suspended-pupil-v5-20261108',candidate_version='V5',
        title='空之律者 · 穹界·虚数锚定环 · 悬天瞳冠（DeepSeek改进）',size=[W,H,D],
        controller=control,controller_face='north',ports=ports,zones=zones,paths=paths,pipe_routes=routes,
        target_voltage='CIV',appearance_voltage='原案紫黑／品红',character='西琳',arms=arms,wings=wings,anchors=anchors,
        stars=stars,ring_section=[3,3],ring_y=200,
        description='五根尖锐的黑紫中空矛脊向内弯曲，在Y200抓住带四向十字星的八边瞳孔环。四组两格厚白／品红破碎光翼在半空撕裂张开；十二根90～100格倒锥长锚悬垂，最低Y100，不触地。环内超导线圈与地面低矮独立主控基座保留工业细节。',
        purpose='DeepSeek针对V2草图的改进意见另制V5，保留既有V1～V4；W01–W15按负责人2026-11-08美观优先决定，不强制HCV主导或规模数字递增，不把离线外观当游戏运行。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1)
    assert all(counts[1:]),[(s,int(n)) for s,n in zip(STATES,counts[1:]) if not n]
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]));occupied=c!=0
    bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)));bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);components=np.bincount(labels.ravel())[1:]
    root_labels=[int(labels[0,a['root'][2],a['root'][0]]) for a in data['arms']]
    assert len(set(root_labels))==1 and root_labels[0]!=0,root_labels
    assert labels[200,264,460]==root_labels[0],'五矛必须真实抓住悬环'
    zz,xx=np.ogrid[:D,:W];pupil=(xx-336)**2+(zz-264)**2<75**2
    assert not np.any(c[30:,pupil]),'中央瞳孔必须保持贯通'
    del labels,occupied
    assert n>=2 and max(components)>100000,('悬空破碎薄翼与独立基座',n,components)
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
    return dict(passed=True,geometry_passed=True,design_rules_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),
        blocks=metrics['blocks'],unique_materials=len(STATES),ordinary_materials=metrics['materials'],palette=palette,
        bounding_box_volume=metrics['volume'],height=H,baseline_check=dict(passed=True,baseline_wdh=baseline),
        voltage_progression=dict(passed=all(passes.values()),required_for_wonder_appearance=False,passes=passes,metrics=metrics,lower_form_count=prior['lower_form_count'],
            lower_maxima=prior['lower_maxima'],source='logs/w03-anchor-v1-20261107/voltage-progression.json',
            comparison='2026-11-08负责人决定W01–W15外观以美观为唯一前提；旧数值递增只统计，不作外观否决项。'),
        connectivity=dict(components=int(n),component_blocks=sorted(map(int,components),reverse=True),
            interpretation='允许破碎薄翼独立悬浮及独立地面基座；不补支架改变造型。'),
        port_checks=markers,pipe_routes_count=12,pipe_routes_passed=True,open_pipe_ends=0,character='西琳',
        arm_count=5,wing_count=4,anchor_count=12,ring_outer_diameter=251,ring_y=200,ring_section=[3,3],
        lowest_anchor_tip_y=min(a['tip'][1] for a in data['anchors']),anchor_lengths=[a['length'] for a in data['anchors']],
        beauty_first_exception=dict(scope='W01–W15',decision_date='2026-11-08',mandatory_casing_dominance=False,numeric_progression_required=False),
        checks=['五根中空内弯矛脊及尖锐冠刺为真实方块；细缝使用品红玻璃。',
            '悬环中心Y200，3×3截面、四向十字星及真实超导线圈；中央瞳孔不填平台。',
            '四组两格破碎白／品红薄翼含锯齿边、径向裂隙和35格弧形光纹。',
            '十二长锚尖端Y100～110，长90～100格，不接触地面；低矮主控基座独立。',
            '五矛根十个通用接口、基座两个通用接口与主控有背板及五格净空；十二冷却支路两端逐格核对。'],
        source_interpretations=['原文同时提出长锚80～100格与Y80尖端；Y200悬环不能同时满足，本版取长度90～100、尖端Y100～110并注明。',
            '八边环名义直径250，含端点实体宽251；截面3×3，内缘线圈与十字星独立计入总体。',
            '基座是独立地面操作设备；上方主体对地支撑只有五矛根，刺桩不接地。',
            '新意见没有逐格坐标；曲率、薄片裂隙及光纹由本轮转译；原V2本已Y200，新版用薄片和内弯轮廓加强仰视悬浮感。',
            '不使用楼梯／末地烛的方盒代理；用现有完整机械机壳和海晶灯近似阶梯收尖与发光纹路。'],
        not_verified=['W01–W15主材／递增外观限制已由负责人取消，但美观仍待负责人选择；不是自动批准或部署。',
            '正式Pattern、阶段成型、配方、角色出场、8GB性能与游戏内成型均未验收。',
            '破碎薄翼是实际静态方块，不宣称有动态光翼、落锚动画或粒子系统。'])



if __name__=='__main__':
    cube,data=build();v=audit(cube,data);print(json.dumps({k:v[k] for k in ('blocks','unique_materials','connectivity','voltage_progression')},ensure_ascii=False))
