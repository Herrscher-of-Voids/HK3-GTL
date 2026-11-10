# -*- coding: utf-8 -*-
"""I34独立几何：树冠式长基线接收阵列与分层观测机房。

【变更记录 #1】2026-10-27：从空白设计IRV观测院，不改正式结构与实例。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 451, 251, 431
CX, CZ = 225, 215
NAME = 'hk3gtl-i34-imaginary-tree-array-v1-20261027'
TITLE = '虚数之树观测阵列 · 树冠干涉观测院'
IRV = 'hk3gtl:voltage_machine_casing_irv'
PORT = 'hk3gtl:industrial_port_casing'
CONTROL = 'minecraft:diamond_block'
ROBUST = 'gtceu:robust_machine_casing'
CLEAN = 'gtceu:clean_machine_casing'
ASSEMBLY = 'gtceu:assembly_line_casing'
COMPUTER = 'gtceu:advanced_computer_casing'
ATOMIC = 'gtceu:atomic_casing'
POWER = 'gtceu:high_power_casing'
LASER = 'gtceu:laser_safe_engraving_casing'
TURBINE = 'gtceu:stainless_steel_turbine_casing'
MACERATOR = 'gtceu:secure_maceration_casing'
VENT = 'gtceu:computer_heat_vent'
GEAR = 'gtceu:tungstensteel_gearbox'
TUNG_PIPE = 'gtceu:tungstensteel_pipe_casing'
STEEL_PIPE = 'gtceu:steel_pipe_casing'
GRATE = 'gtceu:assembly_line_grating'
IRIDIUM = 'gtlcore:iridium_casing'
PROCESS = 'gtlcore:process_machine_casing'
DIMENSION = 'gtlcore:dimension_connection_casing'
MULTI = 'gtlcore:multi_functional_casing'
LAFIUM = 'gtlcore:lafium_mechanical_casing'
GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
FILTER = 'gtlcore:law_filter_casing'
INERT = 'gtceu:inert_machine_casing'
HEATPROOF = 'gtceu:heatproof_machine_casing'
INSULATE = 'gtceu:nonconducting_casing'
FROST = 'gtceu:frostproof_machine_casing'
STABLE = 'gtceu:stable_machine_casing'
SOLID = 'gtceu:solid_machine_casing'
INTAKE = 'gtceu:engine_intake_casing[active=false]'
STRESS = 'gtceu:stress_proof_casing'
MIXING = 'gtceu:reaction_safe_mixing_casing'
VIBRATION = 'gtceu:vibration_safe_casing'
PLASCRETE = 'gtceu:plascrete'
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
BLACK_GLASS = 'minecraft:black_stained_glass'
BLACK = 'minecraft:black_concrete'
LIGHT = 'minecraft:sea_lantern'
GOLD = 'minecraft:gold_block'

PALETTE_ROLES = {
 IRV:'树冠分枝天线、相关运算机房及档案厅的主体机壳',
 PORT:'真实工艺设备表面预留的接口标记',CONTROL:'前侧档案接入厅整宽中轴主控标记',
 ROBUST:'三层设备基座、天线承座和连续承重箱梁',CLEAN:'接收器边缘、分枝桁架和机房银灰护边',
 ASSEMBLY:'探针维护工位与分层观测机房的设备楼板',COMPUTER:'多基线相关运算、误差拟合及资料归档设备',
 ATOMIC:'天线局部相位标定头',POWER:'接收阵列和运算厅分路电源柜',LASER:'干涉光路测距头与探针读出设备',
 TURBINE:'闭式冷却循环的旋转换热机组',MACERATOR:'空间探针回收后外壳表面维护设备',
 VENT:'运算机房与分层设备基座散热百叶',GEAR:'接收镜方位、俯仰转轴与天线检修关节',
 TUNG_PIPE:'接收阵列屏蔽信号母线',STEEL_PIPE:'观测机房冷却水分路',GRATE:'中央仪器检修桥与接收器维修走台',
 IRIDIUM:'高精度接收面的局部参考标靶',PROCESS:'空间探针检测、维护及校准工位',
 DIMENSION:'世界泡对照档案及联系测量数据接入设备',MULTI:'多路观测数据交叉核验设备',
 LAFIUM:'闭式冷却机组伺服设备',GLASS:'运算机房与档案厅的连续观察窗',FILTER:'对照档案噪声筛选设备',
 INERT:'空间探针隔离交接仓',HEATPROOF:'运算电源热端隔离箱',INSULATE:'接收器及运算设备绝缘底座',
 FROST:'低噪声接收前端冷端设备',STABLE:'恒温回路压力缓冲仓',SOLID:'重型接收器地脚和仪器承台',
 INTAKE:'设备基座和机房屋顶进气口',STRESS:'主天线分叉承力节点',MIXING:'恒温标定介质调理设备',
 VIBRATION:'天线、相关运算机柜和空间探针检测台的减振座',PLASCRETE:'设备基座内维护层地坪',
 BLUE_GLASS:'沿接收分枝与光学测距路径嵌入的窄导光槽',BLACK_GLASS:'遮光测距窗口',
 BLACK:'接收面消杂光挡板',LIGHT:'维护走道、接收器内缘与观测工位照明',
 GOLD:'相位参考连接器的小量镀金接点',
}
CELLS = {}


def put(x,y,z,state,replace=False):
    p=(int(x),int(y),int(z))
    assert 0<=p[0]<W and 0<=p[1]<H and 0<=p[2]<D,p
    if replace or p not in CELLS: CELLS[p]=state


def box(lo,hi,state,replace=False):
    for y in range(lo[1],hi[1]+1):
        for z in range(lo[2],hi[2]+1):
            for x in range(lo[0],hi[0]+1):put(x,y,z,state,replace)


def line(a,b,state,radius=0,replace=False):
    steps=max(abs(a[i]-b[i]) for i in range(3));p=list(a)
    for k in range(steps+1):
        q=[round(a[i]+(b[i]-a[i])*k/max(1,steps)) for i in range(3)]
        for axis in range(3):
            while p[axis]!=q[axis]:
                p[axis]+=1 if q[axis]>p[axis] else -1
                box(tuple(v-radius for v in p),tuple(v+radius for v in p),state,replace)
        box(tuple(v-radius for v in q),tuple(v+radius for v in q),state,replace)


def foundation():
    # 三层连续设备基座承载冷却、电源和信号母线；中空楼层保留可进入的维护空间。
    for y in range(30):
        floor=y%10<4
        for z in range(D):
            for x in range(W):
                edge=min(x,W-1-x,z,D-1-z)
                if floor or edge<3 or x%43<3 or z%41<3:
                    state=IRV if floor or edge<2 else ROBUST
                    if y in (3,13,23):state=PLASCRETE if edge>5 else CLEAN
                    if not floor and edge==0 and 8<x%43<32 and 8<z%41<30:state=VENT
                    put(x,y,z,state)
    for x in (154,296):
        box((x-3,30,63),(x+3,33,368),TUNG_PIPE)
        box((x-1,34,63),(x+1,34,368),LIGHT,True)


def hall(x0,x1,z0,z1,top):
    for y in range(30,top+1):
        floor=(y-30)%16<4 or y>=top-3
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                edge=min(x-x0,x1-x,z-z0,z1-z)
                if floor:
                    put(x,y,z,IRV if edge<6 or y%16!=0 else ASSEMBLY,True)
                elif edge<3:
                    along=z-z0 if min(x-x0,x1-x)<3 else x-x0
                    window=edge==0 and 6<(y-30)%16<13 and 6<along%29<23
                    put(x,y,z,GLASS if window else CLEAN if along%29<3 else IRV,True)
    for z in range(z0+12,z1-9,29):
        box((x0+8,top+1,z),(x1-8,top+3,z+5),VENT)
        for x in (x0+6,x1-7):box((x,top,z-2),(x+1,top+4,z+7),CLEAN,True)


def buildings():
    for z0,z1,top in ((74,166,94),(168,263,110),(265,357,94)):
        hall(0,139,z0,z1,top)
        hall(311,450,z0,z1,top)
    hall(93,357,8,70,78)
    hall(93,357,360,422,78)
    # 中轴圆形承台用同心承重环衔接两翼机房；中心不是被制造的虚数之树。
    for y in range(30,51):
        radius=78 if y<39 else 70
        for z in range(CZ-radius,CZ+radius+1):
            for x in range(CX-radius,CX+radius+1):
                r=math.hypot(x-CX,z-CZ)
                if r<=radius and (y<34 or y>45 or r>radius-6):
                    put(x,y,z,IRV if y>33 else ROBUST,True)
    for x in (CX-55,CX+55):
        box((x-5,30,67),(x+5,46,364),IRV)
        box((x-3,47,67),(x+3,48,364),GRATE)
    for z in (152,278):
        box((135,30,z-8),(315,42,z+8),IRV)
        box((137,43,z-5),(313,44,z+5),GRATE)


def receiver(cx,cz):
    # 抛物面接收器：实体立轴、俯仰承座、碗内径向筋和有支撑的馈源。
    box((cx-18,30,cz-18),(cx+18,109,cz+18),IRV,True)
    box((cx-22,104,cz-22),(cx+22,115,cz+22),GEAR,True)
    for z in range(cz-44,cz+45):
        for x in range(cx-44,cx+45):
            r=math.hypot(x-cx,z-cz)
            if r>44:continue
            y=116+round((r/44)**2*22)
            for dy in range(4):put(x,y+dy,z,IRV if r<40 else CLEAN,True)
            if 17<r<36 and (abs(x-cx)<2 or abs(z-cz)<2):put(x,y+4,z,IRIDIUM,True)
            elif r<39:put(x,y+4,z,BLACK,True)
            if 40<r<42:put(x,y+4,z,LIGHT,True)
    for side in (-1,1):
        line((cx+side*40,135,cz),(cx,166,cz),CLEAN,1,True)
        line((cx,135,cz+side*40),(cx,166,cz),CLEAN,1,True)
    box((cx-5,163,cz-5),(cx+5,170,cz+5),LASER,True)
    box((cx-2,162,cz-2),(cx+2,162,cz+2),GOLD,True)


def leaf(a,b,z,halfdepth):
    # 叶片实为窄条相控接收面，留出条带间隔与可识别的桁架，避免实心墙遮住分枝。
    steps=max(abs(a[0]-b[0]),abs(a[1]-b[1]))
    for k in range(steps+1):
        x=round(a[0]+(b[0]-a[0])*k/steps);y=round(a[1]+(b[1]-a[1])*k/steps)
        for dz in range(-halfdepth,halfdepth+1):
            if abs(dz)>halfdepth-3 or dz%7<4:
                box((x-2,y-1,z+dz),(x+2,y+2,z+dz),IRV,True)
                if abs(dz)>halfdepth-2:put(x,y+3,z+dz,CLEAN,True)
                elif dz%7==0:put(x,y+3,z+dz,BLUE_GLASS,True)
    line((a[0],a[1]-3,z),(b[0],b[1]-3,z),ROBUST,2)
    for x,y in (a,b):
        box((x-3,y-4,z-halfdepth),(x+3,y+2,z+halfdepth),IRV,True)
        box((x-2,y+3,z-halfdepth),(x+2,y+3,z+halfdepth),CLEAN,True)


def crown(z):
    box((CX-29,30,z-24),(CX+29,58,z+24),ROBUST,True)
    box((CX-23,51,z-20),(CX+23,66,z+20),VIBRATION,True)
    for y in range(67,121):
        half=23-(y-67)//6
        box((CX-half,y,z-13),(CX+half,y,z+13),IRV,True)
        for x in (CX-half,CX+half):box((x,y,z-15),(x,y,z+15),CLEAN,True)
        box((CX-2,y,z-14),(CX+2,y,z-14),BLUE_GLASS,True)
    for side in (-1,1):
        nodes=[(CX,108,z),(CX+side*51,153,z),(CX+side*101,200,z),(CX+side*153,244,z)]
        for a,b in zip(nodes,nodes[1:]):
            line(a,b,IRV,6,True)
            line((a[0],a[1]+2,z-7),(b[0],b[1]+2,z-7),CLEAN,1,True)
            line((a[0],a[1]-2,z-8),(b[0],b[1]-2,z-8),BLUE_GLASS,1,True)
        for x,y,_ in nodes[1:]:
            box((x-8,y-7,z-9),(x+8,min(H-1,y+7),z+9),STRESS,True)
            box((x-6,y-5,z-10),(x+6,y+5,z-10),IRV,True)
        # 每级主枝都分出一条向上内收的次枝，形成真正树冠，而非附加的垂直装饰塔。
        for a,b in ((nodes[1],(CX+side*31,205,z)),(nodes[2],(CX+side*80,244,z))):
            line(a,b,IRV,4,True)
            line((a[0],a[1],z+6),(b[0],b[1],z+6),CLEAN,1,True)
            leaf((b[0]-side*15,b[1]-12),(b[0]+side*16,min(247,b[1]+3)),z,20)
        leaf((CX+side*45,154),(CX+side*102,174),z,23)
        leaf((CX+side*101,201),(CX+side*153,221),z,25)
        leaf((CX+side*116,229),(CX+side*153,247),z,25)
        line((CX+side*18,90,z),(CX+side*61,40,z),IRV,5)
        box((CX+side*61-10,30,z-17),(CX+side*61+10,46,z+17),SOLID,True)
    line((CX,118,z),(CX,237,z),IRV,4)
    leaf((CX-24,218),(CX,239),z,18)
    leaf((CX,239),(CX+24,218),z,18)
    box((CX-5,210,z-8),(CX+5,220,z+8),ATOMIC,True)
    box((CX-2,221,z-3),(CX+2,223,z+3),IRIDIUM,True)


def instruments():
    crown(171);crown(259)
    # 两扇天线的同轴桁架和有落地支撑的检修桥，不依靠悬空构件维持整体。
    for y in (82,117):
        box((CX-7,y,171),(CX+7,y+4,259),IRV)
        box((CX-4,y+5,171),(CX+4,y+5,259),GRATE)
    for x in (70,380):
        for z in (120,310):receiver(x,z)
    # 前后两条校准基线沿机房屋面穿行，低矮测距设备保持中轴视野。
    for z in (51,379):
        box((120,79,z-4),(330,83,z+4),IRV,True)
        box((123,84,z-2),(327,84,z+2),BLACK_GLASS,True)
        for x in (126,324):box((x-5,84,z-6),(x+5,97,z+6),LASER,True)


def equipment():
    # 小量专用材料只用于有用途的机组、接点与隔离仓，不大面积拼色。
    equipment_states=[COMPUTER,POWER,PROCESS,DIMENSION,MULTI,FILTER,INERT,HEATPROOF,
                      INSULATE,FROST,STABLE,INTAKE,MIXING,LAFIUM,TURBINE,MACERATOR]
    for i,state in enumerate(equipment_states):
        z=88+(i%8)*36;y=114 if 168<=z<=263 else 98
        for x in (25+74*(i//8),425-74*(i//8)):
            box((x-12,y-4,z-10),(x+12,y+2,z+10),VIBRATION,True)
            box((x-10,y+3,z-8),(x+10,y+13,z+8),state,True)
            box((x-10,y+14,z-8),(x+10,y+15,z+8),IRV,True)
            if i>=8:box((x-9,y+4,z-9),(x+9,y+10,z-9),state,True)
    for x in (132,318):
        box((x-2,35,81),(x+2,39,350),STEEL_PIPE,True)
        box((x-4,40,82),(x+4,42,349),IRV)
    # 机房内的成排相关运算柜、冷却分路和探针检修床使楼层拥有实际用途。
    for x in (38,72,106,344,378,412):
        for z in range(89,349,36):
            for y in (39,55,71):
                box((x-5,y,z-6),(x+5,y+6,z+6),COMPUTER)
                box((x-3,y+7,z-5),(x+3,y+7,z+5),VENT)
    for x in (176,274):
        box((x-9,30,30),(x+9,40,52),INERT,True)
        box((x-7,41,32),(x+7,46,50),PROCESS,True)


def markers():
    controller=[CX,45,8]
    ports=[dict(id='世界泡对照档案输入',purpose='接收世界泡对照档案供观测拟合',pos=[201,45,8],face='north'),
           dict(id='空间探针输入',purpose='空间探针隔离检查与交接',pos=[249,45,8],face='north'),
           dict(id='西侧观测供能',purpose='西侧接收器与相关机房供能候选',pos=[0,45,103],face='west'),
           dict(id='东侧观测供能',purpose='东侧接收器与相关机房供能候选',pos=[450,45,103],face='east'),
           dict(id='西侧冷却输入',purpose='低噪声接收设备冷却回路候选',pos=[0,45,327],face='west'),
           dict(id='东侧冷却回流',purpose='低噪声接收设备冷却回路候选',pos=[450,45,327],face='east'),
           dict(id='树与世界联系图输出',purpose='输出供后续工程使用的联系图',pos=[201,45,422],face='south'),
           dict(id='虚数观测资料输出',purpose='输出观测资料及误差记录，供I35/S04',pos=[249,45,422],face='south'),
           dict(id='观测探针回收',purpose='已用探针的维护回收候选',pos=[177,45,422],face='south'),
           dict(id='复测档案交付',purpose='锚定前后联系变化复测档案候选',pos=[273,45,422],face='south')]
    for m in [dict(pos=controller,face='north',state=CONTROL)]+[dict(p,state=PORT) for p in ports]:
        x,y,z=m['pos']
        if m['face'] in ('north','south'):
            dz=1 if m['face']=='north' else -1
            box((x-2,y-2,min(z,z+dz)),(x+2,y+2,max(z,z+dz)),IRV,True)
        else:
            dx=1 if m['face']=='west' else -1
            box((min(x,x+dx),y-2,z-2),(max(x,x+dx),y+2,z+2),IRV,True)
        put(x,y,z,m['state'],True)
    paths=[dict(name='前侧档案与空间探针接入通廊',min=[166,30,0],max=[284,58,7]),
           dict(name='后侧联系图与观测资料交付通廊',min=[166,30,423],max=[284,58,430])]
    for path in paths:
        lo,hi=path['min'],path['max']
        for y in range(lo[1],hi[1]+1):
            for z in range(lo[2],hi[2]+1):
                for x in range(lo[0],hi[0]+1):CELLS.pop((x,y,z),None)
    return controller,ports,paths


def build():
    CELLS.clear()
    foundation();buildings();instruments();equipment()
    controller,ports,paths=markers()
    # 先固定几何，再按中轴镜像材质与细节；功能语义可以不同，外观仍严格对称。
    for p in list(CELLS):
        if p[0]>CX:del CELLS[p]
    for (x,y,z),state in list(CELLS.items()):
        if x<CX:CELLS[(W-1-x,y,z)]=state
    return dict(key='i34',name=NAME,title=TITLE,size=[W,H,D],controller=controller,controller_face='north',ports=ports,paths=paths,
        zones=[dict(name='双扇分枝式相控接收冠',pos=[CX,108,171]),dict(name='四基线抛物面接收器',pos=[70,170,120]),
               dict(name='中央减振承台与仪器维护桥',pos=[CX,122,CZ]),dict(name='多层相关运算与观测机房',pos=[0,45,216]),
               dict(name='档案与空间探针隔离接入厅',pos=[93,45,40]),dict(name='联系图及观测资料交付厅',pos=[93,45,390])],
        description='青铜IRV机壳组成双扇分枝相控接收冠，银灰桁架与窄冰蓝导光槽呈现仪器层级。四只真实立轴抛物面接收器构成长基线，围合中央减振承台；下方阶梯机房、档案厅和三层设备基座通过检修桥、屏蔽母线及冷却回路连成完整观测院。',
        construction_notes=dict(orientation='主控朝北/-Z，蓝图坐标从0起算。',anchor='本地[0,0,0]；推荐世界Y=-60，最高Y=190。',
            boundary='只观测树与世界联系并记录误差，不制造或操纵整棵虚数之树；普通计算硬件交GT。观测资料不代替实体锚件或I35工程。RN-IOP开放本机，首次真实初观证据支持RN-ILE，不以前置I35/S04形成循环。',
            approval='独立外观候选，未获负责人批准、未接入实例。'),
        blocks=[dict(pos=list(p),state=s) for p,s in sorted(CELLS.items(),key=lambda t:(t[0][1],t[0][2],t[0][0]))])


if __name__=='__main__':
    from collections import Counter
    data=build();counts=Counter(b['state'] for b in data['blocks'])
    assert counts[CONTROL]==1 and counts[PORT]==10 and counts[IRV]==max(counts.values())
    assert all(tuple(z['pos']) in CELLS for z in data['zones'])
    assert len(CELLS)>5624362 and len(counts)>39 and math.prod((W,H,D))>31519789 and H>229
    print(dict(blocks=len(CELLS),materials=len(counts),size_xyz=data['size'],irv=counts[IRV]),flush=True)
