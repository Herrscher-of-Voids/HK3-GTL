# -*- coding: utf-8 -*-
"""W02万象矩阵：中央分层构造塔、六座独立装配院与贯通干线。"""
import math
import numpy as np
from scipy import ndimage
from i42_prefabrication_geometry_v1_20261028 import Material
from structure_size_baseline import baselines

W,H,D=649,303,493
M=Material()
M.WFV='hk3gtl:voltage_machine_casing_hbv'
STATES=sorted({M.WFV if k=='WFV' else v for k,v in vars(Material).items() if k.isupper()}|{'gtceu:computer_casing'})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'六院工艺机组、承载结构或维护构件' for s in STATES}
ROLES.update({M.WFV:'HBV蓝色主体；外观映射不改变WSV运行电压',M.CONTROL:'北侧中轴主控预览占位',
    M.PORT:'通用接口预览占位；不限定输入输出',M.PLASCRETE:'条形承载基础',M.ASSEMBLY:'分层装配平台与导轨',
    M.COMPUTER:'矩阵算力机柜',M.VENT:'算力柜排热面',M.GLASS:'装配院观察窗',M.ROBUST:'跨院龙门与承载框架',
    M.STEEL_PIPE:'已接通设备的冷却支路',M.TUNG_PIPE:'中央冷却干管',M.GRATE:'巡检栈桥',
    'gtceu:computer_casing':'六院本地调度机柜'})


def build():
    c=np.zeros((H,D,W),np.uint8)
    def box(a,b,s):
        x,y,z=a;X,Y,Z=b
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D,(a,b)
        c[y:Y+1,z:Z+1,x:X+1]=IDS[s] if s else 0
    def shell(a,b,s,t=4):
        box(a,b,s)
        box(tuple(v+t for v in a),tuple(v-t for v in b),None)
    zones=[];routes=[];paths=[]
    # 地基沿机体与运输干线分布，院间保留通行空地。
    box((202,0,0),(446,11,492),M.PLASCRETE)
    box((258,12,6),(390,26,42),M.WFV)
    box((263,16,6),(385,22,10),M.CLEAN)
    box((266,17,6),(382,21,8),M.WFV)
    control=[324,19,6];box(control,control,M.CONTROL)
    ports=[]
    for i,x in enumerate((274,286,298,310,338,350,362,374),1):
        p=[x,19,6];box(p,p,M.PORT)
        ports.append(dict(id=f'通用接口{i:02}',pos=p,face='north',purpose='物品、流体或能源能力按接入舱室决定；不预设方向',group='generic'))
    paths.append(dict(min=[258,17,1],max=[390,24,5]))
    # 中央十二层构造矩阵，楼板内是连续服务夹层，层间保留设备与检修空间。
    for level,y in enumerate(range(12,301,24)):
        inset=(level//4)*8
        x0,x1=211+inset,437-inset;z0,z1=48+inset,444-inset
        box((x0,y,z0),(x1,min(y+6,302),z1),M.WFV)
        if level<12:
            box((310,y,z0+34),(338,y+6,z1-34),None)
        if level==12:continue
        for x in (x0,x1-8):
            box((x,y,z0),(x+8,min(y+23,302),z1),M.WFV)
            box((x,y+10,z0+7),(x+8,min(y+15,302),z1-7),M.GLASS)
        for x in (x0+23,x1-55):
            for z in range(z0+16,z1-42,56):
                shell((x,y+7,z),(x+32,y+22,z+39),M.WFV,3)
                box((x+3,y+9,z),(x+29,y+18,z+2),M.COMPUTER)
                box((x+3,y+19,z),(x+29,y+21,z+2),M.VENT)
                box((x+3,y+10,z+38),(x+29,y+17,z+40),M.FUSION_GLASS)
        for x in (294,350):
            box((x,y+7,z0),(x+4,y+10,z1),M.GRATE)
    # 实心立柱和贯穿式调度核心承接每层；最高层是承载完整矩阵的顶框。
    for x in (240,282,358,400):
        for z in (90,180,304,394):
            box((x,12,z),(x+8,302,z+8),M.WFV)
            box((x+2,15,z),(x+6,299,z),M.ROBUST)
    shell((300,12,202),(348,302,290),M.WFV,6)
    for y in range(20,290,24):
        box((300,y,214),(302,y+12,278),M.BLACK_GLASS)
        box((346,y,214),(348,y+12,278),M.BLUE_GLASS)
    zones.append(dict(name='中央十二层构造矩阵与贯通调度核心',pos=[324,298,246]))
    # 六院分别配置加工、热处理、混配、精密、算力与空间构件机组。
    process=[(M.MACERATOR,M.GEAR,M.SOLID,M.STEEL),(M.HEATPROOF,M.INSULATE,M.TURBINE,M.INTAKE),
        (M.MIXING,M.INERT,M.FROST,M.FILTER),(M.LASER,M.IRIDIUM,M.LAFIUM,M.LAMINATED),
        ('gtceu:computer_casing',M.COMPUTER,M.MULTI,M.NONCONDUCTING if hasattr(M,'NONCONDUCTING') else M.INSULATE),
        (M.DIMENSION,M.PROCESS,M.STRESS,M.VIBRATION)]
    names=['加工院','热工院','混配院','精密院','算力院','构件院']
    for side,(x0,x1) in enumerate(((0,198),(450,648))):
        for row,z0 in enumerate((10,176,342)):
            z1=z0+140;idx=side*3+row;a,b,lining,accent=process[idx]
            box((x0,0,z0),(x1,11,z1),M.PLASCRETE)
            shell((x0,12,z0),(x1,155,z1),M.WFV,5)
            for y in (20,46,72,98,124):
                box((x0+5,y,z0+5),(x1-5,y+5,z1-5),M.WFV)
                # 设备行列之间留出连续检修通道。
                for x in (x0+18,x0+78,x0+138):
                    for z in (z0+17,z0+82):
                        box((x,y+6,z),(x+39,y+8,z+39),M.VIBRATION)
                        shell((x,y+9,z),(x+39,y+23,z+39),a,4)
                        box((x+4,y+9,z+4),(x+35,y+12,z+35),lining)
                        box((x+4,y+13,z),(x+35,y+20,z+2),b)
                        box((x+4,y+14,z+38),(x+35,y+20,z+40),M.GLASS)
                        box((x+2,y+21,z+4),(x+37,y+23,z+7),accent)
                for z in (z0,z1-4):
                    box((x0+10,y+10,z),(x1-10,y+18,z+4),M.GLASS)
                for x in (x0,x1-4):
                    box((x,y+10,z0+9),(x+4,y+18,z1-9),M.GLASS)
            # 外露龙门有四根落地立柱；蓝色主机体与桥架保持明确层级。
            for x in (x0+14,x1-20):
                for z in (z0+10,z1-16):box((x,12,z),(x+6,174,z+6),M.ROBUST)
                for z in (z0+10,z1-16):box((x,168,z),(x+6,177,z+6),M.GEAR)
                box((x,169,z0+10),(x+6,175,z1-10),M.ROBUST)
            box((x0+14,169,z0+67),(x1-14,176,z0+73),M.ASSEMBLY)
            box((x0+89,157,z0+60),(x0+109,168,z0+80),M.LAFIUM)
            for x in (x0+34,x0+84,x0+134):
                box((x,156,z0+18),(x+27,163,z0+44),M.VENT)
                box((x,156,z1-44),(x+27,163,z1-18),M.TURBINE)
            # 四层跨院桥连接中央楼板，同时承载传送带及冷却干管。
            for y in (36,84,132,156):
                left,right=(193,235) if side==0 else (413,455)
                box((left,y,z0+57),(right,y+5,z0+83),M.WFV)
                box((left,y+6,z0+58),(right,y+8,z0+62),M.ASSEMBLY)
                box((left,y+6,z0+78),(right,y+8,z0+82),M.GRATE)
            # 指定设备的两端点与轴对齐路由；不允许留下装饰断管。
            left,right=(190,240) if side==0 else (408,458)
            z=z0+70;y=144
            for x in (left,right):box((x-4,132,z-5),(x+4,151,z+5),M.TURBINE)
            box((left,142,z-1),(right,146,z+1),M.STEEL_PIPE)
            routes.append(dict(id=f'{names[idx]}冷却联络',start=[left,y,z],end=[right,y,z],
                path=[[x,y,z] for x in range(left,right+1)],state=M.STEEL_PIPE,endpoint_state=M.TURBINE))
            zones.append(dict(name=names[idx]+' · 五层分布式装配场',pos=[x0+100,153,z0+70]))
    # 中央物料和算力纵向双干线，前后均落入端站。
    for x in (274,374):
        box((x-5,12,27),(x+5,32,465),M.ASSEMBLY)
        box((x-2,33,27),(x+2,36,465),M.STEEL)
        for z in (25,457):box((x-12,12,z),(x+12,44,z+9),M.WFV)
    # 六院共同服务设备；每种材料有实际职责，避免靠零散装饰凑调色板。
    equipment=[M.ATOMIC,M.POWER,M.TUNG_PIPE,M.STABLE,M.CLEAN,M.IRON,M.OBSIDIAN,M.GOLD,M.LIGHT]
    for i,s in enumerate(equipment):
        x=220+(i%3)*73;z=8+(i//3)*9
        box((x,12,z),(x+15,20,z+6),s)
    data=dict(key='w02',name='hk3gtl-w02-autonomous-matrix-v1-20261107',
        title='理之律者 · 万象·自律工业矩阵 · 六院构造中庭',size=[W,H,D],controller=control,
        controller_face='north',ports=ports,zones=zones,paths=paths,pipe_routes=routes,
        target_voltage='WSV',appearance_voltage='HBV',
        description='中央十二层构造矩阵统合六院：加工、热工、混配、精密、算力与构件。四层跨院桥与纵向双干线连接全部院落，顶框和龙门都有连续承重路径。',
        purpose='保留W02既定名称与中央矩阵＋六座分布式装配场职责；角色实体、配方、自动建造与运行能力不由外观候选代替验收。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1);assert np.all(counts[1:])
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]))
    occupied=c!=0;bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)))
        bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);assert n==1,('六邻接游离件',n)
    del labels,occupied
    assert palette[M.WFV]==max(palette.values())
    assert {s for s in STATES if s.startswith('hk3gtl:')}=={M.WFV,M.PORT}
    assert palette[M.CONTROL]==1 and palette[M.PORT]==len(data['ports'])==8
    markers=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        x,y,z=item['pos'];assert c[y,z+1,x]
        assert all(c[y+dy,z,x+dx] for dx,dy in ((-1,0),(1,0),(0,1),(0,-1)))
        assert not np.any(c[y,z-5:z,x])
        markers.append(dict(id=item['id'],position=item['pos'],flush_shell=True,inner_backed=True,outer_clear=5))
    for route in data['pipe_routes']:
        p=route['path'];assert p[0]==route['start'] and p[-1]==route['end']
        assert all(sum(abs(a-b) for a,b in zip(p[i],p[i+1]))==1 for i in range(len(p)-1))
        assert all(c[y,z,x]==IDS[route['state']] for x,y,z in p)
        for x,y,z in (p[0],p[-1]):assert c[y+3,z,x]==IDS[route['endpoint_state']]
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max'];assert not np.any(c[y:Y+1,z:Z+1,x:X+1])
    for zone in data['zones']:
        x,y,z=zone['pos'];assert c[y,z,x],zone
    baseline=baselines()['W02']['size'];assert all(a>=b for a,b in zip((W,D,H),baseline))
    metrics=dict(blocks=int(counts[1:].sum()),materials=len(STATES)-2,volume=W*H*D,height=H)
    from w02_voltage_progression_20261107 import progression
    voltage=progression(metrics)
    return dict(passed=True,geometry_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),
        blocks=metrics['blocks'],unique_materials=len(STATES),ordinary_materials=metrics['materials'],palette=palette,
        bounding_box_volume=metrics['volume'],height=H,hbv_casing_count=palette[M.WFV],
        baseline_check=dict(passed=True,baseline_wdh=baseline),voltage_progression=voltage,
        connectivity=dict(passed=True,components=1,neighborhood=6),controller=dict(position=data['controller']),
        port_checks=markers,pipe_routes_count=6,pipe_routes_passed=True,open_pipe_ends=0,
        checks=['实际边界逐轴超过W02总表下限。','运行WSV；HBV蓝色为最大单一主体材料。',
            '六邻接单连通；主控居中，八处通用接口齐平、有背板和五格净空。',
            '六院冷却联络逐格六邻接，两端接入指定设备。','实体数、普通材料种类、边界体积与高度严格超过全部已批准低阶。'],
        not_verified=['本轮仅外观；未批准、未接入正式Pattern、未部署或游戏验收。',
            '角色实体归属、研究工艺、生存获取与8GB全建筑运行目标另行验收。'])
