# -*- coding: utf-8 -*-
"""I41宇宙能源港：空心环城、约束笼、调度法庭及熵流监测设施。

变更记录 #1（2026-10-28）：独立几何候选；复用材质合同，不复用旧版建筑。
"""
import math
from pathlib import Path
import numpy as np
import i41_material_roles_geometry_v2_20261028 as palette_source

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 529, 289, 529, 264
NAME = 'hk3gtl-i41-cosmic-customs-v3-20261028'
TITLE = '文明能源调度中枢 · 宇宙海关与十二港约束环城'
CHANGES = dict(ATOMIC='gtceu:black_large_metal_sheet', TURBINE='gtceu:black_metal_sheet',
               LASER='gtceu:purple_large_metal_sheet', TUNG_PIPE='gtceu:bronze_pipe_casing')
Material = type('Material', (), {k: CHANGES.get(k, v) for k, v in
    vars(palette_source.Material).items() if k.isupper()})
material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i+1 for i, s in enumerate(STATES)}
assert len(STATES) == len(IDS) == 43
ROLES = {getattr(material, k): role for k, role in {
    'IWV':'环城分层舱室、承载甲板、相位配平环与调度大厅主体',
    'CONTROL':'调度大厅正面中轴主控预览标记', 'PORT':'嵌入大厅外壳的计划接口占位',
    'ROBUST':'环城承力肋、上环斜撑与约束骨架', 'PLASCRETE':'环形设备基础与码头承载座',
    'POWER':'铜母线护槽与分配环屏蔽层', 'TUNG_PIPE':'沿径向能源廊延伸的铜色服务管路',
    'ATOMIC':'中央约束笼黑色主梁', 'TURBINE':'约束笼细格栅与锁定环',
    'LASER':'约束节点及少量紫色相位标记', 'COMPUTER':'授权、配额与历史回执仪表阵列',
    'GRATE':'检修层、维护栈桥与港口吊运横梁', 'GLASS':'调度城区暗色观察窗',
    'LAMINATED':'稳定能流河道观察面', 'BLUE_GLASS':'支线状态观察带',
    'BLACK_GLASS':'黑色世界泡展示核外层', 'FUSION_GLASS':'冷却支路小型观察口',
    'LIGHT':'协议灯及河道间隔照明', 'INSULATE':'能源廊绝缘背衬',
    'CLEAN':'调度法庭门廊和白色协议边框', 'ASSEMBLY':'法庭外墙浅色腰线',
    'LAFIUM':'调度厅窗台与裁定席浅色边缘', 'IRON':'门廊浅色竖向构件',
    'GEAR':'相位配平环的耦合器', 'STEEL_PIPE':'维护廊银灰色接地标线',
    'IRIDIUM':'庭院与检修平台铺面', 'PROCESS':'入口阶梯和维护踏步',
    'DIMENSION':'展示核局部相位裂纹', 'MULTI':'清算档案馆的深色门框',
    'MACERATOR':'熵流监测池的深色承托', 'VENT':'排放设施格栅',
    'FILTER':'熵流监测设施隔片', 'INERT':'仪表绝缘底座',
    'HEATPROOF':'排放口灰色薄鳍片', 'FROST':'冷却支路浅色绝热套',
    'STABLE':'维护设备矮基础', 'SOLID':'后勤入口踏步侧壁',
    'INTAKE':'维护机组进风标识', 'STRESS':'维护机组隔振短柱',
    'MIXING':'检修工位防滑标线', 'VIBRATION':'设备承座减振垫',
    'GOLD':'少量许可校准触点', 'OBSIDIAN':'黑色世界泡展示核实体壳'
}.items()}


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)
    zz, xx = np.ogrid[:D, :W]
    radius = np.sqrt((xx-CX)**2 + (zz-CX)**2)
    angle = np.degrees(np.arctan2(xx-CX, CX-zz))
    zones = []

    def box(a, b, state):
        x,y,z = map(int,a); X,Y,Z = map(int,b)
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (a,b)
        cube[y:Y+1,z:Z+1,x:X+1] = IDS[state] if state else 0

    def point(r, theta, y):
        t = math.radians(theta)
        return round(CX+r*math.sin(t)), round(y), round(CX-r*math.cos(t))

    def mask(r1, r2, theta=None, half=180):
        m = (radius >= r1) & (radius <= r2)
        if theta is not None:
            m &= np.abs((angle-theta+180)%360-180) <= half
        return m

    def fill(y1,y2,state,m):
        assert 0 <= y1 <= y2 < H
        cube[y1:y2+1,m] = IDS[state] if state else 0

    def band(r1,r2,y1,y2,state,theta=None,half=180):
        fill(y1,y2,state,mask(r1,r2,theta,half))

    def beam(a,b,state,r=2):
        n=max(abs(b[i]-a[i]) for i in range(3))
        for j in range(n+1):
            p=[round(a[i]+(b[i]-a[i])*j/max(1,n)) for i in range(3)]
            box(tuple(max(0,v-r) for v in p),tuple(min(s-1,v+r) for v,s in zip(p,(W,H,D))),state)

    def unit(theta,r,y,kind):
        x,_,z=point(r,theta,y)
        box((x-8,y,z-7),(x+8,y+2,z+7),material.VIBRATION)
        box((x-7,y+3,z-6),(x+7,y+5,z+6),material.STABLE)
        if kind==0:
            box((x-6,y+6,z-5),(x+6,y+18,z+5),material.INERT)
            box((x-5,y+8,z-6),(x+5,y+15,z-5),material.COMPUTER)
            box((x-4,y+16,z-6),(x+4,y+17,z-5),material.GLASS)
            box((x-2,y+19,z-3),(x+2,y+20,z+3),material.GOLD)
        elif kind==1:
            box((x-6,y+6,z-5),(x+6,y+8,z+5),material.MACERATOR)
            for dx in (-5,-1,3):
                box((x+dx,y+9,z-5),(x+dx+1,y+22,z+5),material.HEATPROOF)
            box((x-6,y+9,z-6),(x+6,y+10,z-5),material.FILTER)
            box((x-6,y+23,z-5),(x+6,y+24,z+5),material.VENT)
            box((x-2,y+12,z+5),(x+2,y+19,z+6),material.FUSION_GLASS)
            box((x-6,y+12,z+6),(x-4,y+19,z+7),material.FROST)
        else:
            for dx in (-5,3):
                box((x+dx,y+6,z-5),(x+dx+2,y+14,z+5),material.STRESS)
            box((x-6,y+15,z-5),(x+6,y+18,z+5),material.INTAKE)
            box((x-6,y+19,z-5),(x+6,y+20,z+5),material.SOLID)
            box((x-6,y+6,z+6),(x+6,y+7,z+7),material.MIXING)
            box((x-3,y+21,z-3),(x+3,y+23,z+3),material.STEEL_PIPE)

    # 空心环基与下部熵流环；中央保留贯通的巨大空腔。
    band(142,264,0,7,material.PLASCRETE)
    band(142,264,8,12,material.IWV)
    band(147,158,13,21,material.POWER)
    band(160,172,13,18,material.MACERATOR)
    band(160,172,19,20,material.HEATPROOF)
    band(258,264,13,17,material.ROBUST)
    for y in range(24,205,20):
        band(136,150,y,y+4,material.IWV)
        band(169,176,y,y+4,material.IWV)
        if y in (44,104,164):
            band(150,169,y,y+4,material.IWV)
        else:
            for theta in range(0,360,30):
                band(149,170,y,y+2,material.GRATE,theta,1.4)
        band(137,139,y+5,y+7,material.GRATE)
        band(169,172,y+5,y+7,material.POWER)

    # 十二个有退台、层板和真实空腔的调度城区，按职能成对布局。
    heights=(84,124,168,220,196,172,236,172,196,220,168,124)
    zone_names=('调度法庭与授权大厅','宇宙港接驳泊位','整流状态测控城区','熵流监测与清算设施',
                '跨维协议中继城区','无人维护港','历史回执与清算档案馆',
                '无人维护港','跨维协议中继城区','熵流监测与清算设施','整流状态测控城区','宇宙港接驳泊位')
    for k,top in enumerate(heights):
        theta=k*30
        outer=mask(177,258,theta,13)
        inner=mask(181,254,theta,11.7)
        fill(13,top,material.IWV,outer)
        fill(19,top-5,None,inner)
        for y in range(18,top-4,20):
            fill(y,y+3,material.IWV,outer)
            band(178,181,y+6,min(y+8,top),material.ROBUST,theta,13)
            band(255,258,y+6,min(y+8,top),material.ROBUST,theta,13)
            if y+10 <= top:
                band(255,258,y+8,min(y+16,top),material.GLASS,theta,10.5)
                for delta in (-9,-4.5,0,4.5,9):
                    band(255,258,y+8,min(y+16,top),material.ROBUST,theta+delta,0.35)
        band(177,258,top-2,top+2,material.GRATE,theta,13)
        band(186,248,top+3,top+4,material.IWV,theta,11.5)
        for delta in (-9,0,9):
            unit(theta+delta,220,top+5,min(k,12-k)%3)
        # 三层退台设备街，屋顶机房与细柱廊道区分城区和巨型整壳。
        for r in (194,244):
            for delta in (-7,7):
                x,_,z=point(r,theta+delta,top+5)
                box((x-7,top+5,z-7),(x+7,top+18,z+7),material.IWV)
                box((x-5,top+7,z-5),(x+5,top+16,z+5),None)
                box((x-6,top+9,z-7),(x+6,top+14,z-6),material.GLASS)
                box((x-8,top+19,z-8),(x+8,top+20,z+8),material.GRATE)
        for y in range(38,top-15,40):
            unit(theta,205,y,0)
        x,y,z=point(234,theta,14)
        zones.append(dict(name=f'{k+1:02d}区 · {zone_names[k]}',pos=[x,y,z]))
        # 两层能源河与检修桥连通内外环，铜护岸包住窄青色观察带。
        for y in (52,112):
            beam(point(85,theta,y),point(191,theta,y),material.IWV,5)
            beam(point(87,theta,y+6),point(187,theta,y+6),material.INSULATE,3)
            beam(point(87,theta,y+8),point(187,theta,y+8),material.LAMINATED,2)
            for delta in (-2.2,2.2):
                beam(point(87,theta+delta,y+5),point(190,theta+delta,y+5),material.TUNG_PIPE,1)
        # 配平环斜撑扎入城体，避免用脱节高塔凑高度。
        beam(point(244,theta,16),point(216,theta,282),material.ROBUST,3)
        beam(point(192,theta,24),point(216,theta,282),material.IWV,3)
        for y in range(44,271,28):
            r1=244+(216-244)*(y-16)/266
            r2=192+(216-192)*(y-24)/258
            beam(point(r1,theta,y),point(r2,theta,y),material.GRATE,1)
        # 接驳港的起重门架、悬吊约束舱和中间空泊位，保持正在运行的港口感。
        if k in (1,5,7,11):
            band(114,177,24,28,material.IWV,theta,8)
            band(114,119,29,31,material.POWER,theta,8)
            for delta in (-7,7):
                beam(point(156,theta+delta,29),point(156,theta+delta,83),material.ROBUST,2)
                beam(point(126,theta+delta,29),point(126,theta+delta,78),material.GRATE,1)
                beam(point(126,theta+delta,78),point(174,theta+delta,83),material.ROBUST,2)
            beam(point(156,theta-7,83),point(156,theta+7,83),material.GRATE,3)
            beam(point(156,theta,83),point(137,theta,83),material.TUNG_PIPE,2)
            beam(point(137,theta,83),point(137,theta,59),material.TURBINE,0)
            x,_,z=point(137,theta,45)
            for dx in (-9,9):
                for dz in (-9,9):
                    beam((x+dx,45,z+dz),(x+dx,59,z+dz),material.ATOMIC,1)
            for y in (45,59):
                for dx in (-9,9):
                    beam((x+dx,y,z-9),(x+dx,y,z+9),material.ATOMIC,1)
                for dz in (-9,9):
                    beam((x-9,y,z+dz),(x+9,y,z+dz),material.ATOMIC,1)
            box((x-5,46,z-5),(x+5,56,z+5),material.BLACK_GLASS)
            box((x-2,58,z-2),(x+2,59,z+2),material.LASER)
        # 内环维护舱：薄平台、银色地线和分路阀组有各自职能。
        unit(theta,154,29,2)
        x,_,z=point(149,theta,49)
        box((x-5,49,z-5),(x+5,51,z+5),material.IRIDIUM)
        box((x-4,52,z-4),(x+4,54,z+4),material.PROCESS)
        box((x-3,55,z-3),(x+3,58,z+3),material.GEAR)
        box((x-2,59,z-2),(x+2,61,z+2),material.BLUE_GLASS)

    # 顶部配平环不是盖板，保持大孔洞与分层铜母线。
    band(206,229,276,282,material.IWV)
    band(207,211,283,288,material.ROBUST)
    band(225,229,283,287,material.POWER)
    band(215,220,283,285,material.COMPUTER)
    for k in range(12):
        band(211,225,283,287,material.GEAR,k*30,1.7)
        band(212,224,288,288,material.LIGHT,k*30,0.8)

    # 黑色约束笼：多层锁环、纵向细栅和三道子午框，而非发光球。
    for y in (52,106,139,171,203,236):
        band(80,88,y,y+3,material.ATOMIC)
        band(82,86,y+4,y+5,material.TURBINE)
    for k in range(24):
        theta=k*15
        beam(point(84,theta,52),point(84,theta,241),material.ATOMIC,1)
        for y in (108,173,238):
            x,_,z=point(84,theta,y)
            box((x-2,y,z-2),(x+2,y+3,z+2),material.LASER)
    for plane in (0,60,120):
        points=[point(96*math.cos(math.radians(a)),plane,171+96*math.sin(math.radians(a))) for a in range(361)]
        for a,b in zip(points,points[1:]):
            beam(a,b,material.ROBUST,2)
    # 世界泡采用正球壳，展示而不赋予捕获、产能或记账功能。
    for y in range(118,225):
        r2=53**2-(y-171)**2
        if r2<0: continue
        outer=(radius*radius<=r2)
        inner=(radius*radius<max(0,49**2-(y-171)**2))
        fill(y,y,material.OBSIDIAN,outer & ~inner)
        if y%13==0:
            fill(y,y,material.DIMENSION,(outer & ~inner) & (np.abs((angle+12)%60-30)<1.2))
    for theta in range(0,360,60):
        beam(point(51,theta,171),point(84,theta,171),material.TURBINE,1)
        beam(point(51,theta,172),point(80,theta,172),material.BLACK_GLASS,0)

    # 北端调度法庭与主入口融入环城，不外挂主控面板。
    box((CX-78,0,0),(CX+78,12,87),material.PLASCRETE)
    box((CX-74,13,0),(CX+74,68,79),material.IWV)
    box((CX-69,18,5),(CX+69,62,74),None)
    box((CX-69,39,5),(CX+69,43,74),material.IWV)
    for x in (CX-74,CX-51,CX-28,CX+26,CX+49,CX+72):
        box((x,13,0),(x+2,67,2),material.CLEAN)
    for y in (18,36,56):
        box((CX-70,y,0),(CX+70,y+2,1),material.ASSEMBLY)
    for x in (CX-62,CX-39,CX-16,CX+7,CX+30,CX+53):
        box((x,43,0),(x+11,54,0),material.LAMINATED)
        box((x,42,0),(x+11,42,1),material.LAFIUM)
    for dx in (-47,45):
        box((CX+dx,13,1),(CX+dx+2,34,3),material.IRON)
    for dx in (-34,34):
        box((CX+dx-6,13,0),(CX+dx+6,18,4),None)
        box((CX+dx-8,19,0),(CX+dx+8,21,2),material.MULTI)
    for dx in (-64,64):
        box((CX+dx-4,13,3),(CX+dx+4,17,16),material.PROCESS)
    box((CX-61,64,5),(CX+61,65,71),material.IRIDIUM)
    # 主控标记及六接口只改外墙的一格，周围、内背板与外侧净空独立核验。
    ports=[]
    labels=('I38合法入账记录','绑定人授权输入','已登记负载输入','授权调度回执','告警与历史查询','维护物资交接')
    for name,dx in zip(labels,(-66,-44,-22,22,44,66)):
        box((CX+dx-2,22,0),(CX+dx+2,26,3),material.IWV)
        box((CX+dx,24,0),(CX+dx,24,0),material.PORT)
        ports.append(dict(id=name,pos=[CX+dx,24,0],face='north',purpose='外观占位；正式能力另行验收'))
    box((CX-2,22,0),(CX+2,26,3),material.IWV)
    box((CX,24,0),(CX,24,0),material.CONTROL)
    data=dict(key='i41',name=NAME,title=TITLE,candidate_version='V3',size=[W,H,D],
        controller=[CX,24,0],controller_face='north',ports=ports,paths=[],zones=zones,
        description='中央黑色世界泡被多层约束笼与子午框编号封存，十二条窄青色能源河连接退台环城；底部熵流环、顶部配平环及前端调度法庭形成宇宙海关式能源基础设施。保留大量空腔、真实检修层和用途不同的城区，不把整座做成实心反应堆。',
        construction_notes=dict(concept='宇宙能源港＋调度法庭＋约束监狱＋熵债清算所的建筑隐喻。',
            function='I41仍只负责授权负载调度；笼、港、清算所均为外观表达，不新增捕获、产能或熵债规则。',
            materials='IWV机壳主导；GT承力和铜母线分工，少量原版辅材用于厅体、观察窗和维护细部。',
            sectors='12个内部建筑分区，不新增12个正式控制器；正式成型仍须完整建筑校验。'))
    return cube,data


if __name__=='__main__':
    cube,data=build()
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    print(dict(size=data['size'],blocks=int(counts[1:].sum()),unused=[s for s in STATES if counts[IDS[s]]==0],
        iwv=int(counts[IDS[material.IWV]]),max_material=int(counts[1:].max())),flush=True)
