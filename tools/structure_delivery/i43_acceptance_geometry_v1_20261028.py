# -*- coding: utf-8 -*-
"""I43开瓣环境穹舱与六轴验收台；所有实体来自同一份几何。

变更记录 #1（2026-10-28）：新增独立建筑候选，不改批准结构或实例。
"""
from pathlib import Path
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
W,H,D,CX=641,297,481,320
NAME='hk3gtl-i43-environment-acceptance-v1-20261028'
TITLE='文明工程验收中心 · 开瓣环境穹舱与六轴验收台'


class Material:
    WSV='hk3gtl:voltage_machine_casing_wsv'
    CONTROL='minecraft:diamond_block'
    PORT='hk3gtl:industrial_port_casing'
    FRAME='gtceu:titanium_turbine_casing'
    CLEAN='gtceu:clean_machine_casing'
    ASSEMBLY='gtceu:assembly_line_casing'
    COMPUTER='gtceu:advanced_computer_casing'
    DARK='gtceu:black_large_metal_sheet'
    COPPER='gtceu:bronze_brick_casing'
    LASER='gtceu:laser_safe_engraving_casing'
    TURBINE='gtceu:stainless_steel_turbine_casing'
    VENT='gtceu:computer_heat_vent'
    GEAR='gtceu:tungstensteel_gearbox'
    FINISH='gtceu:secure_maceration_casing'
    TUNG_PIPE='gtceu:tungstensteel_pipe_casing'
    STEEL_PIPE='gtceu:steel_pipe_casing'
    GRATE='gtceu:assembly_line_grating'
    IRIDIUM='gtlcore:iridium_casing'
    PROCESS='gtlcore:process_machine_casing'
    DIMENSION='gtlcore:dimension_connection_casing'
    MULTI='gtlcore:multi_functional_casing'
    LAFIUM='gtlcore:lafium_mechanical_casing'
    GLASS='gtlcore:hsss_reinforced_borosilicate_glass'
    FILTER='gtlcore:law_filter_casing'
    INERT='gtceu:inert_machine_casing'
    HEATPROOF='gtceu:heatproof_machine_casing'
    INSULATE='gtceu:nonconducting_casing'
    FROST='gtceu:frostproof_machine_casing'
    STABLE='gtceu:stable_machine_casing'
    SOLID='gtceu:solid_machine_casing'
    INTAKE='gtceu:engine_intake_casing[active=false]'
    STRESS='gtceu:stress_proof_casing'
    MIXING='gtceu:reaction_safe_mixing_casing'
    VIBRATION='gtceu:vibration_safe_casing'
    BASE='gtceu:steel_brick_casing'
    LAMINATED='gtceu:laminated_glass'
    FUSION_GLASS='gtceu:fusion_glass'
    STEEL='gtceu:steel_machine_casing'
    BLUE_GLASS='minecraft:light_blue_stained_glass'
    BLACK_GLASS='minecraft:black_stained_glass'
    LIGHT='minecraft:sea_lantern'
    GOLD='minecraft:gold_block'
    IRON='minecraft:iron_block'
    OBSIDIAN='minecraft:obsidian'
    QUARTZ='minecraft:quartz_block'


material=Material()
STATES=sorted(v for k,v in vars(Material).items() if k.isupper())
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'计量、环境隔离、试验载荷或检修构件' for s in STATES}
ROLES.update({getattr(material,k):v for k,v in dict(
    WSV='环境试验拱壳、开合门、承载试验台与控制前厅的主体机壳',
    CONTROL='前厅正面中轴的主控预览标记',PORT='连续外墙内嵌的计划工艺接口占位',
    FRAME='拱壳承力环、开门铰座及外框',DARK='消声吸波尖劈与热辐射屏蔽内衬',
    CLEAN='门封、独立洁净计量走廊及观察室框',ASSEMBLY='门轨和试件交接定位轨',
    COMPUTER='计量读出、故障记录和报告复核工作台',COPPER='受检负载电流与接地母排',
    LASER='独立光学校准基线与测头',TURBINE='换热机组金属罩',VENT='梯级机房散热顶盖',
    GEAR='开门传动箱与六轴加载执行器关节',TUNG_PIPE='热工介质主管',STEEL_PIPE='冷却与供气支路',
    FINISH='复测隔离台的精密护罩',
    GRATE='计量维护栈桥',IRIDIUM='精密定位台基准面',PROCESS='压力与供能联试设备',
    DIMENSION='维系/空间环境校核侧台屏蔽层',MULTI='联试工位机匣',LAFIUM='六轴试验台承载枢纽',
    GLASS='计量廊与流体设备观察窗',FILTER='试验介质净化与隔离滤栅',INERT='样品隔离柜衬层',
    HEATPROOF='热端环境机组及管路隔离',INSULATE='电载荷试验绝缘层',FROST='冷端环境机组',
    STABLE='计量基准座',SOLID='平台定位基础',INTAKE='试验舱循环进气口',STRESS='六轴加载支腿承力段',
    MIXING='介质处理柜安全内衬',VIBRATION='样品台和仪器隔振基础',BASE='试验舱基础与门轨承台',
    LAMINATED='独立计量观察面',FUSION_GLASS='空间环境读出窄窗',STEEL='承载台、门轨及维修钢梁',
    BLUE_GLASS='冷却储罐液位窗',BLACK_GLASS='验收记录暗屏',LIGHT='门封、轨道和维护照明',
    GOLD='少量精密计量标定触点',IRON='前厅金属边框',OBSIDIAN='热辐射黑体标定块',
    QUARTZ='光学标定参考块').items()})


def build():
    cube=np.zeros((H,D,W),dtype=np.uint8)
    m=material

    def box(a,b,state):
        x,y,z=map(int,a);X,Y,Z=map(int,b)
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D,(a,b)
        cube[y:Y+1,z:Z+1,x:X+1]=IDS[state] if state else 0

    def shell(a,b,state,t=3):
        box(a,b,state)
        if all(b[k]-a[k]+1>2*t for k in range(3)):
            box(tuple(v+t for v in a),tuple(v-t for v in b),None)

    def beam(a,b,state,r=2):
        n=max(abs(b[i]-a[i]) for i in range(3))
        for j in range(n+1):
            p=[round(a[i]+(b[i]-a[i])*j/max(1,n)) for i in range(3)]
            box(tuple(max(0,v-r) for v in p),tuple(min(s-1,v+r) for v,s in zip(p,(W,H,D))),state)

    zones=[]
    # 基础分为试验舱、独立计量廊、两扇门的实际承台，不填整幅空地。
    box((82,0,92),(558,9,D-1),m.BASE)
    box((104,10,106),(536,17,D-1),m.WSV)
    box((104,22,106),(536,28,D-1),m.WSV)
    for x in range(110,532,52):
        box((x,18,108),(x+8,21,D-1),m.BASE)
    for x0,x1 in ((0,90),(550,640)):
        box((x0,0,0),(x1,13,454),m.BASE)
    for z in (8,42,76):
        box((0,0,z),(640,12,z+8),m.BASE)

    # 低阶梯环境机房承接冷/热、介质净化与循环设备。
    for left,right in ((5,85),(555,635)):
        for k,(z0,z1,top) in enumerate(((104,216,92),(224,336,119),(344,472,146))):
            shell((left,14,z0),(right,top,z1),m.WSV,4)
            for y in range(22,top-9,22):
                box((left+4,y,z0+4),(right-4,y+3,z1-4),m.WSV)
                box((left,y+8,z0+9),(left+3,y+13,z1-9),m.GLASS)
                box((right-3,y+8,z0+9),(right,y+13,z1-9),m.GLASS)
            box((left+7,top+1,z0+7),(right-7,top+4,z1-7),m.GRATE)
            for z in range(z0+13,z1-14,27):
                casing=(m.FROST,m.FILTER,m.HEATPROOF)[k]
                shell((left+14,top+5,z),(right-14,top+27,z+19),casing,3)
                box((left+18,top+28,z+3),(right-18,top+30,z+16),m.VENT)
                box((left+9,top+5,z+3),(left+13,top+18,z+16),m.TURBINE)
                box((right-13,top+5,z+3),(right-9,top+18,z+16),m.INTAKE)
            for y in (top-23,top-10):
                box((left+8,y,z0),(right-8,y+3,z0+3),m.CLEAN)
        x=right-9 if left<100 else left+9
        box((x,22,88),(x+4,27,472),m.TUNG_PIPE)
        zones.append(dict(name='冷端循环与介质净化' if left<100 else '热端循环与负载机房',pos=[left+9,23,110]))

    # 舱顶是等半径半圆拱，低区竖直壁与舱底相接；前端保持敞开。
    yy,xx=np.ogrid[:H,:W]
    radius=220;cy=76
    distance=(xx-CX)**2+(yy-cy)**2
    arch=(distance<=radius**2)&(distance>=(radius-12)**2)&(yy>=cy)
    for z in range(112,D):
        cube[:,z,:][arch]=IDS[m.WSV]
    for x0,x1 in ((100,119),(521,540)):
        box((x0+4,29,112),(x1-4,76,D-1),m.WSV)
    inside=(distance<=(radius-22)**2)&(distance>=(radius-27)**2)&(yy>=cy)
    for z in range(122,D-9):
        cube[:,z,:][inside]=IDS[m.DARK]
    # 外肋按真实截面包裹拱壳；末端有完整试验屏蔽墙和检修窗带。
    rib=(distance<=(radius+0)**2)&(distance>=(radius-7)**2)&(yy>=cy)
    for z in range(112,D,40):
        for Z in range(z,min(z+7,D)):
            cube[:,Z,:][rib]=IDS[m.FRAME]
        for x0,x1 in ((100,119),(521,540)):
            box((x0,29,z),(x1,76,min(z+6,D-1)),m.FRAME)
    end=(distance<=radius**2)&(yy>=cy)
    for z in range(D-9,D):
        cube[:,z,:][end]=IDS[m.WSV]
    box((100,29,D-9),(540,76,D-1),m.WSV)
    for y in (85,132,179):
        box((190,y,D-4),(450,y+8,D-1),m.GLASS)
        box((185,y-3,D-5),(455,y-1,D-1),m.CLEAN)

    # 断面相连的内衬尖劈，体现消声/热辐射隔离，而非装饰色格。
    for z in range(142,455,34):
        for side in (-1,1):
            wall=126 if side<0 else 514
            for y in range(52,155,29):
                for step in range(0,16,3):
                    x=wall+side*step
                    beam((x,y-step//2,z-step//2),(x,y+10+step//2,z+10+step//2),m.DARK,2)

    # 敞开的双瓣厚门沿斜向地轨展开，门叶、铰座、锁封和传动自成整体。
    for side in (-1,1):
        start=(108 if side<0 else 532,116)
        finish=(6 if side<0 else 634,8)
        for j in range(109):
            t=j/108;x=round(start[0]+(finish[0]-start[0])*t);z=round(start[1]+(finish[1]-start[1])*t)
            top=round(236-65*t)
            box((x-6,14,max(0,z-6)),(x+6,top,min(D-1,z+6)),m.WSV)
            for y in (22,58,94,130,166):
                if y+4<top: box((x-6,y,max(0,z-6)),(x+6,y+3,min(D-1,z+6)),m.FRAME)
            if j%21<4:
                box((x-6,26,max(0,z-6)),(x+6,top,min(D-1,z+6)),m.CLEAN)
            box((x-6,14,max(0,z-7)),(x+6,18,min(D-1,z+7)),m.ASSEMBLY)
        x=start[0]
        box((x-12,14,103),(x+12,242,127),m.FRAME)
        box((x-15,14,101),(x+15,18,129),m.SOLID)
        for y in (23,80,137,194):
            box((x-14,y,101),(x+14,y+18,129),m.GEAR)
        beam((start[0],239,116),(finish[0],173,8),m.CLEAN,3)
        beam((start[0],243,116),(finish[0],177,8),m.LIGHT,1)
        zones.append(dict(name='西侧开门铰座' if side<0 else '东侧开门铰座',pos=[x,40,114]))

    # 独立计量走廊以实体栈桥联到舱底，与样品台分开承载。
    for x0,x1 in ((134,192),(448,506)):
        box((x0,29,122),(x1,36,458),m.BASE)
        box((x0+3,37,122),(x1-3,43,458),m.STABLE)
        shell((x0,44,128),(x1,88,455),m.CLEAN,3)
        box((x0+3,53,128),(x1-3,73,130),m.LAMINATED)
        for z in range(147,443,37):
            box((x0+4,47,z),(x1-4,64,z+13),m.COMPUTER)
            box((x0+9,65,z+3),(x1-9,67,z+10),m.BLACK_GLASS)
            box((x0+3,78,z),(x1-3,81,z+4),m.LIGHT)
        for x in (x0,x1-2):
            box((x,54,136),(x+2,72,448),m.LAMINATED)
        box((x0+6,89,132),(x1-6,92,451),m.GRATE)
        zones.append(dict(name='独立西计量基线廊' if x0<200 else '独立东计量基线廊',pos=[x0+6,40,140]))

    # 六轴加载台支腿逐根相连；承载的是待测工程样件，不是世界泡。
    box((210,29,172),(430,37,398),m.SOLID)
    box((221,38,183),(419,44,387),m.VIBRATION)
    for side in (-1,1):
        for z in (208,284,360):
            a=(CX+side*75,45,z);b=(CX+side*50,98,z+(-16 if z<284 else 16))
            beam(a,b,m.STRESS,8)
            beam((a[0],a[1]+4,a[2]),(b[0],b[1]-4,b[2]),m.LAFIUM,5)
            box((a[0]-11,42,a[2]-11),(a[0]+11,50,a[2]+11),m.GEAR)
            box((b[0]-10,94,b[2]-10),(b[0]+10,104,b[2]+10),m.GEAR)
    box((238,102,184),(402,112,398),m.WSV)
    box((242,113,188),(398,117,394),m.IRIDIUM)
    for x in (254,382):
        box((x-4,118,193),(x+4,123,389),m.ASSEMBLY)
    # 跨度不同的框式工程样件，有负载、热端和相位读出端。
    for z in (217,280,343):
        shell((267,118,z-12),(373,177,z+12),m.WSV,8)
        box((272,126,z-13),(368,135,z-11),m.COPPER)
        box((272,163,z-13),(368,167,z-11),m.INSULATE)
    box((300,118,207),(340,130,356),m.WSV)
    box((306,131,211),(334,139,352),m.PROCESS)
    for x,state in ((267,m.HEATPROOF),(368,m.FROST)):
        box((x,137,204),(x+5,145,356),state)
    box((306,140,270),(334,153,290),m.DIMENSION)
    box((309,141,269),(331,150,270),m.FUSION_GLASS)
    zones.append(dict(name='六轴加载台与受检工程样件',pos=[CX,114,278]))

    # 仪器门架从舱底承托，校准光路横贯样品，而非悬空装饰。
    for z in (161,413):
        for x in (204,436):
            box((x-5,29,z-5),(x+5,188,z+5),m.CLEAN)
            box((x-7,82,z-7),(x+7,98,z+7),m.LASER)
            box((x-6,126,z-7),(x+6,141,z+7),m.MULTI)
        box((199,189,z-6),(441,196,z+6),m.WSV)
        box((CX-17,180,z-8),(CX+17,188,z+8),m.LASER)
        box((CX-8,174,z-8),(CX+8,179,z+8),m.QUARTZ)
        for x in (212,422):
            box((x,29,z-7),(x+6,46,z+7),m.OBSIDIAN)
            box((x+1,47,z-4),(x+5,49,z+4),m.GOLD)

    # 舱后联试介质柜与隔离复测台各有专用外观。
    for k,x in enumerate(range(208,418,42)):
        shell((x,29,437),(x+32,74,467),(m.FILTER,m.INERT,m.MIXING,m.INSULATE,m.PROCESS)[k],3)
        box((x+5,38,436),(x+27,54,439),m.BLUE_GLASS if k%2==0 else m.GLASS)
        box((x+3,75,444),(x+29,79,460),m.STEEL_PIPE)
        box((x+8,80,449),(x+24,84,455),m.TUNG_PIPE)
    for x in (199,436):
        shell((x,29,215),(x+6,49,230),m.FINISH,2)
        box((x+2,34,214),(x+4,42,215),m.COMPUTER)
    for x in (204,432):
        box((x,29,128),(x+4,34,432),m.STEEL)
        for z in range(141,433,28):
            box((x,35,z),(x+4,37,z+3),m.LIGHT)

    # 低前厅与舱底用真实交接通道连接；主控及接口嵌入完整连续墙。
    box((CX-118,0,0),(CX+118,13,130),m.BASE)
    shell((CX-115,14,0),(CX+115,57,58),m.WSV,4)
    box((CX-112,58,0),(CX+112,62,59),m.CLEAN)
    box((CX-44,14,59),(CX+44,31,130),m.WSV)
    for dx in (-104,-76,-48,-20,8,36,64,92):
        box((CX+dx,39,0),(CX+dx+17,50,0),m.LAMINATED)
    box((CX-110,35,0),(CX+110,37,2),m.IRON)
    ports=[]
    labels=('工程样件输入','热工测试介质','流体测试介质','供能负载接入',
            '计量校准输入','故障样件交接','运行记录核验','报告与档案交接')
    for name,dx in zip(labels,(-96,-72,-48,-24,24,48,72,96)):
        box((CX+dx-2,22,0),(CX+dx+2,26,3),m.WSV)
        box((CX+dx,24,0),(CX+dx,24,0),m.PORT)
        ports.append(dict(id=name,pos=[CX+dx,24,0],face='north',purpose='仅计划能力位置；正式控制器与实际能力另行验收'))
    box((CX-2,22,0),(CX+2,26,3),m.WSV)
    box((CX,24,0),(CX,24,0),m.CONTROL)
    zones.extend([dict(name='主控前厅与验收记录复核',pos=[CX,16,8]),
                  dict(name='舱后介质隔离与故障复测',pos=[320,30,444])])
    return cube,dict(key='i43',name=NAME,title=TITLE,candidate_version='V1',size=[W,H,D],
        controller=[CX,24,0],controller_face='north',ports=ports,paths=[],zones=zones,
        description='一座上部半圆拱壳的环境联试舱以两扇厚门沿地轨展开，露出中央六轴加载台和框式工程样件；两侧独立计量廊隔振承载，低阶梯机房组织冷热循环与测试介质。前厅复核真实运行记录，不以报告制造资源或替代独立工程的运行验收。',
        construction_notes=dict(materials='WSV主体机壳、钛承力环、暗色内衬与洁净计量廊按功能组织。',
            function='建筑表达样件接收、环境联试、独立测量和故障复测；正式执行逻辑另行验收。',
            stage='仅独立建筑候选；研究方法证据不替代真实工程运行，最终资格由W15汇总。'))


if __name__=='__main__':
    cube,data=build()
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    print(dict(size=data['size'],blocks=int(counts[1:].sum()),materials=len(STATES),
        wsv=int(counts[IDS[material.WSV]]),unused=[s for s in STATES if not counts[IDS[s]]]),flush=True)
