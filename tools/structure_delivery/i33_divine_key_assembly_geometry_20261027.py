# -*- coding: utf-8 -*-
"""I33独立几何：圣匣铸键工坊，以开合式装配机、侧翼校验线与移载轨道组织空间。

【变更记录 #1】2026-10-27：从空白生成QCV外观候选，不修改正式资源或实例。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 251, 173, 241
CX, CZ = 125, 120
NAME = 'hk3gtl-i33-divine-key-assembly-v1-20261027'
TITLE = '仿制神之键装配中心 · 圣匣铸键工坊'
QCV = 'hk3gtl:voltage_machine_casing_qcv'
PORT = 'hk3gtl:industrial_port_casing'
CONTROL = 'minecraft:diamond_block'
ROBUST = 'gtceu:robust_machine_casing'
CLEAN = 'gtceu:clean_machine_casing'
ASSEMBLY = 'gtceu:assembly_line_casing'
COMPUTER = 'gtceu:advanced_computer_casing'
ATOMIC = 'gtceu:atomic_casing'
POWER = 'gtceu:high_power_casing'
LASER = 'gtceu:laser_safe_engraving_casing'
VENT = 'gtceu:computer_heat_vent'
GEAR = 'gtceu:tungstensteel_gearbox'
TUNG_PIPE = 'gtceu:tungstensteel_pipe_casing'
STEEL_PIPE = 'gtceu:steel_pipe_casing'
GRATE = 'gtceu:assembly_line_grating'
IRIDIUM = 'gtlcore:iridium_casing'
PROCESS = 'gtlcore:process_machine_casing'
DIMENSION = 'gtlcore:dimension_connection_casing'
MULTI = 'gtlcore:multi_functional_casing'
GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
INERT = 'gtceu:inert_machine_casing'
INSULATE = 'gtceu:nonconducting_casing'
FROST = 'gtceu:frostproof_machine_casing'
VIBRATION = 'gtceu:vibration_safe_casing'
PLASCRETE = 'gtceu:plascrete'
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
LIGHT = 'minecraft:sea_lantern'

PALETTE_ROLES = {
 QCV:'装配圣匣、校验工段、核心封装厅的主体机壳',PORT:'嵌入工艺设备外壁的仓室位置标记',
 CONTROL:'核心接入厅整宽中轴主控位置标记',ROBUST:'连续箱梁基础、载荷地轨及圣匣承重结构',
 CLEAN:'圣匣轮廓、精密装配臂与洁净窗框',ASSEMBLY:'封装移载托盘和侧翼装配线地板',
 COMPUTER:'研究许可核验及核心装配参数柜',ATOMIC:'仿制核心场校准压头',POWER:'分区装配机和工况校验供能设备',
 LASER:'核心封装刻写、精度检测头及工况验证窗口',VENT:'校验工段屋顶通风百叶',
 GEAR:'圣匣铰座、机械臂转轴及移载驱动',TUNG_PIPE:'校准电力母线和屏蔽管道',
 STEEL_PIPE:'工段冷却介质分路',GRATE:'设备维护步道与圣匣检修平台',IRIDIUM:'仿制键体封装壳和精密夹具',
 PROCESS:'侧翼封装与维护工位',DIMENSION:'千界一乘控制组件场校验工位',MULTI:'三种物品神之键的装配参数校验设备',
 GLASS:'侧翼隔离观察窗、封装厅采光带',INERT:'核心封装前隔离接入舱',INSULATE:'核心校准托盘绝缘座',
 FROST:'冷却回路换热设备',VIBRATION:'精密装配线减振支座',PLASCRETE:'连续生产厅地坪',
 BLUE_GLASS:'装配机的静态场校准能量导光片',LIGHT:'工位照明和移载轨道引导灯',
}
CELLS = {}


def put(x, y, z, state, replace=False):
    p = (int(x), int(y), int(z))
    assert 0 <= p[0] < W and 0 <= p[1] < H and 0 <= p[2] < D, p
    if replace or p not in CELLS:
        CELLS[p] = state


def box(lo, hi, state, replace=False):
    for y in range(lo[1], hi[1] + 1):
        for z in range(lo[2], hi[2] + 1):
            for x in range(lo[0], hi[0] + 1):
                put(x, y, z, state, replace)


def line(a, b, state, radius=0, replace=False):
    steps = max(abs(a[i]-b[i]) for i in range(3))
    p = list(a)
    for k in range(steps+1):
        q = [round(a[i]+(b[i]-a[i])*k/max(1,steps)) for i in range(3)]
        for axis in range(3):
            while p[axis] != q[axis]:
                p[axis] += 1 if q[axis] > p[axis] else -1
                box(tuple(v-radius for v in p),tuple(v+radius for v in p),state,replace)
        box(tuple(v-radius for v in q),tuple(v+radius for v in q),state,replace)


def foundation():
    for y in range(12):
        for z in range(D):
            for x in range(W):
                edge = min(x,W-1-x,z,D-1-z)
                if y in (0,1,10,11) or edge<3 or x%31<3 or z%29<3:
                    put(x,y,z,ROBUST if y in (0,11) else QCV)
    # 双轨移载线贯通接入、封装、场校准和成品交接。
    for x in (CX-19,CX+19):
        box((x-5,12,32),(x+5,15,217),VIBRATION)
        box((x-3,16,32),(x+3,18,217),ROBUST)
        box((x-1,19,32),(x+1,20,217),CLEAN)
    for z in (46,79,121,162,203):
        box((CX-28,12,z-8),(CX+28,18,z+8),QCV,True)
        box((CX-25,19,z-7),(CX+25,21,z+7),ASSEMBLY,True)
        for x in (CX-26,CX+26):
            box((x-3,17,z-5),(x+3,23,z+5),GEAR,True)
        box((CX-5,22,z-5),(CX+5,24,z+5),INSULATE,True)
    for z in range(38,218,15):
        box((CX-1,12,z),(CX+1,12,z+2),LIGHT,True)


def hall(x0,x1,z0,z1,top):
    for y in range(12,top+1):
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                edge = min(x-x0,x1-x,z-z0,z1-z)
                floor = (y-12)%19<3 or y>=top-2
                if floor:
                    put(x,y,z,QCV if edge<5 or y>=top-2 else ASSEMBLY,True)
                elif edge<3:
                    along=z-z0 if min(x-x0,x1-x)<3 else x-x0
                    window=edge==0 and 5<(y-12)%19<15 and 6<along%24<18
                    put(x,y,z,GLASS if window else (CLEAN if along%24<3 else QCV),True)
    for z in range(z0+9,z1-7,24):
        box((x0+6,top+1,z),(x1-6,top+3,z+5),VENT)
        box((x0+5,top,z-1),(x0+6,top+4,z+6),CLEAN,True)
        box((x1-6,top,z-1),(x1-5,top+4,z+6),CLEAN,True)


def production_wings():
    # 分段阶梯屋面保留中央高挑装配机的视线，校验线拥有连续落地墙体。
    for x0,x1 in ((0,58),(192,250)):
        for z0,z1,top in ((39,88,62),(89,148,81),(149,211,100)):
            hall(x0,x1,z0,z1,top)
        for z in (61,116,178):
            x=(x0+x1)//2
            box((x-10,15,z-10),(x+10,19,z+10),VIBRATION,True)
            box((x-8,20,z-8),(x+8,31,z+8),PROCESS,True)
            box((x-6,32,z-6),(x+6,39,z+6),MULTI if z==61 else DIMENSION,True)
            box((x-3,40,z-3),(x+3,44,z+3),LASER,True)
        # 内侧两层走廊与工艺母线有实柱支撑。
        inner=x1 if x0==0 else x0
        reach=73 if x0==0 else 177
        for y in (35,62):
            box((min(inner,reach),y,45),(max(inner,reach),y+2,211),QCV)
            box((min(inner,reach),y+3,45),(max(inner,reach),y+3,211),GRATE)
        for z in (49,99,153,207):
            box((reach-3,12,z-4),(reach+3,67,z+4),QCV)
        box((reach-1,68,45),(reach+1,70,211),TUNG_PIPE)
    hall(62,188,8,30,43)
    hall(62,188,220,232,43)
    # 许可柜与隔离接入舱设置在工艺接入厅内部。
    for x in (81,105,145,169):
        box((x-5,15,15),(x+5,25,23),INERT,True)
        box((x-4,26,16),(x+4,34,22),COMPUTER,True)
        box((x-5,15,223),(x+5,25,229),PROCESS,True)
    # 两条侧翼工况验证线分别拥有供能/冷却，而不是仅堆砌材料。
    for x0,x1 in ((3,17),(233,247)):
        for z,state in ((52,POWER),(110,FROST),(166,COMPUTER),(194,INERT)):
            box((x0,15,z),(x1,27,z+12),state,True)
            box((x0+2,28,z+2),(x1-2,30,z+10),VENT,True)
        box((x0+5,14,44),(x0+7,16,204),STEEL_PIPE,True)


def petal(side,z0,z1):
    # 上段向核心合拢的开合式圣匣：连续的机壳、银灰边棱和齿轮铰座。
    for y in range(24,166):
        offset=52 if y<102 else round(52-(y-102)*.48)
        x=CX+side*offset
        thick=8 if y<110 else 6
        for z in range(z0,z1+1):
            for dx in range(-thick,thick+1):
                shell=abs(dx)>=thick-2 or z-z0<3 or z1-z<3 or y%23<3
                if shell:
                    put(x+dx,y,z,QCV,True)
        for z in (z0,z1):
            box((x-thick,y,z),(x+thick,y,z+1),CLEAN,True)
        if y%23<3:
            box((x-thick-2,y,z0-1),(x+thick+2,y,z1+1),QCV,True)
    x=CX+side*52
    box((x-13,12,z0-6),(x+13,25,z1+6),ROBUST,True)
    box((x-10,26,z0-4),(x+10,36,z1+4),GEAR,True)
    # 内凹导光槽嵌在壳体里，贯穿式横梁使其与精密校准机相接。
    for z in (z0+5,z1-5):
        line((x-side*8,38,z),(x-side*8,99,z),BLUE_GLASS,1,True)
        line((x-side*8,99,z),(CX+side*17,164,z),BLUE_GLASS,1,True)


def reliquary():
    for side in (-1,1):
        for z0,z1 in ((89,115),(145,171)):
            petal(side,z0,z1)
    # 两套圣匣的冠梁和纵向移载脊形成整体设备，而非孤立高塔。
    for z in (102,158):
        box((CX-28,157,z-14),(CX+28,165,z+14),QCV,True)
        box((CX-24,166,z-12),(CX+24,169,z+12),CLEAN,True)
        box((CX-13,170,z-8),(CX+13,172,z+8),QCV,True)
        box((CX-8,146,z-8),(CX+8,156,z+8),GEAR,True)
        box((CX-6,132,z-6),(CX+6,145,z+6),ATOMIC,True)
        box((CX-4,119,z-4),(CX+4,131,z+4),LASER,True)
    box((CX-5,154,102),(CX+5,162,158),QCV,True)
    box((CX-3,163,102),(CX+3,164,158),GRATE,True)
    # 开口圣匣中央是一枚被夹持的封装坯件，不赋予其新增神之键种类。
    box((CX-17,12,121),(CX+17,27,149),ROBUST,True)
    box((CX-13,28,124),(CX+13,32,146),INSULATE,True)
    for y in range(33,118):
        half=12 if y<98 else max(3,12-(y-98)//2)
        box((CX-half,y,127),(CX+half,y,143),IRIDIUM,True)
        if y%17<3:
            box((CX-half-2,y,125),(CX+half+2,y,145),CLEAN,True)
        box((CX-3,y,126),(CX+3,y,126),BLUE_GLASS,True)
    box((CX-28,53,129),(CX+28,61,141),IRIDIUM,True)
    box((CX-30,55,131),(CX+30,59,139),ATOMIC,True)
    # 四只机械臂从有承重脚的侧轨进入核心封装面。
    for side in (-1,1):
        for z in (103,163):
            x=CX+side*40
            box((x-8,12,z-8),(x+8,30,z+8),QCV,True)
            box((x-6,31,z-6),(x+6,39,z+6),GEAR,True)
            elbow=(CX+side*34,72,z)
            line((x,39,z),elbow,CLEAN,3,True)
            box(tuple(v-5 for v in elbow),tuple(v+5 for v in elbow),GEAR,True)
            end=(CX+side*16,84,131 if z==103 else 141)
            line(elbow,end,QCV,3,True)
            box(tuple(v-4 for v in end),tuple(v+4 for v in end),LASER,True)
            line((end[0],end[1],end[2]),(CX+side*10,83,135),BLUE_GLASS,1,True)
    # 后部的场校准屏、侧翼与中央圣匣通过实梁/维护桥相接。
    for y in (36,67,98):
        box((CX-50,y,178),(CX+50,y+3,187),QCV)
        box((CX-47,y+4,180),(CX+47,y+4,185),GRATE)
    for x in (CX-49,CX+49):
        box((x-3,12,179),(x+3,102,186),QCV)
    for y in range(43,98):
        for x in range(CX-39,CX+40):
            if x%17<3 or y%19<3:
                put(x,y,184,COMPUTER,True)
    # 与主体同色的底部折线飞扶壁，力流回到连续生产地坪。
    for side in (-1,1):
        for z in (92,164):
            line((CX+side*55,89,z),(CX+side*83,16,z),QCV,4)
            line((CX+side*55,91,z-5),(CX+side*83,18,z-5),CLEAN,1,True)
            box((CX+side*83-7,12,z-9),(CX+side*83+7,18,z+9),ROBUST,True)


def markers():
    controller=[CX,25,8]
    ports=[
      dict(id='仿制核心输入',purpose='接收I08交付的既有获批仿制核心',pos=[101,25,8],face='north'),
      dict(id='研究许可核验',purpose='已有研究许可候选接入口；不自动解锁',pos=[149,25,8],face='north'),
      dict(id='西侧装配供能',purpose='侧翼封装和工况校验设备供能',pos=[0,25,65],face='west'),
      dict(id='东侧装配供能',purpose='镜像侧翼封装和工况校验设备供能',pos=[250,25,65],face='east'),
      dict(id='西侧冷却输入',purpose='精密封装工段冷却介质候选入口',pos=[0,25,178],face='west'),
      dict(id='东侧冷却回流',purpose='冷却回路候选回流接口',pos=[250,25,178],face='east'),
      dict(id='仿制神之键交付',purpose='交付既有三种物品神之键，使用工况不消耗',pos=[101,25,232],face='south'),
      dict(id='魂钢部件输入',purpose='接收I16与GT既有结构、电子和机械分件',pos=[149,25,232],face='south'),
      dict(id='列车信标组件交付',purpose='第二神之键输出列车或信标控制组件',pos=[77,25,232],face='south'),
      dict(id='测试残件输出',purpose='保留维护及非消耗工况验证产生的测试残件',pos=[173,25,232],face='south'),
    ]
    for m in [dict(pos=controller,face='north',state=CONTROL)]+[dict(p,state=PORT) for p in ports]:
        x,y,z=m['pos']
        if m['face'] in ('north','south'):
            dz=1 if m['face']=='north' else -1
            box((x-2,y-2,min(z,z+dz)),(x+2,y+2,max(z,z+dz)),QCV,True)
        else:
            dx=1 if m['face']=='west' else -1
            box((min(x,x+dx),y-2,z-2),(max(x,x+dx),y+2,z+2),QCV,True)
        put(x,y,z,m['state'],True)
    paths=[dict(name='前侧核心与研究许可接入通廊',min=[67,12,0],max=[183,35,7]),
           dict(name='后侧神之键及测试残件交付通廊',min=[67,12,233],max=[183,35,240])]
    for path in paths:
        lo,hi=path['min'],path['max']
        for y in range(lo[1],hi[1]+1):
            for z in range(lo[2],hi[2]+1):
                for x in range(lo[0],hi[0]+1): CELLS.pop((x,y,z),None)
    return controller,ports,paths


def build():
    CELLS.clear()
    foundation();production_wings();reliquary()
    controller,ports,paths=markers()
    for p in list(CELLS):
        if p[0]>CX:del CELLS[p]
    for (x,y,z),state in list(CELLS.items()):
        if x<CX:CELLS[(W-1-x,y,z)]=state
    return dict(key='i33',name=NAME,title=TITLE,size=[W,H,D],controller=controller,controller_face='north',ports=ports,paths=paths,
      zones=[dict(name='开合式圣匣装配机',pos=[CX,172,102]),dict(name='核心封装坯件与四臂夹持台',pos=[CX,80,135]),
             dict(name='双轨移载与绝缘托盘',pos=[CX,23,79]),dict(name='双侧分级装配校验工段',pos=[0,25,116]),
             dict(name='核心接入及研究许可核验厅',pos=[62,25,20]),dict(name='成品与测试残件交接厅',pos=[62,25,226])],
      description='深蓝QCV圣匣围合被夹持的银灰封装坯件，四臂装配机、冠部校准压头与贯通双轨协同；两翼阶梯工段承接既有仿制神之键的封装、校验和维护，形成有完整承重与工艺流线的铸键工坊。',
      construction_notes=dict(orientation='主控朝北/-Z，蓝图坐标从0起算。',anchor='本地[0,0,0]；推荐世界Y=-60，最高Y=112。',
        boundary='限既有四种仿制神之键及既有核心；普通分件交GT与I16，使用工况不消耗神之键。中央坯件是装配过程的静态表达，不新增神之键或律者种类。',
        approval='独立外观候选，未获负责人批准、未接入实例。'),
      blocks=[dict(pos=list(p),state=s) for p,s in sorted(CELLS.items(),key=lambda t:(t[0][1],t[0][2],t[0][0]))])


if __name__=='__main__':
    from collections import Counter
    data=build(); counts=Counter(b['state'] for b in data['blocks'])
    assert counts[CONTROL]==1 and counts[PORT]==10 and counts[QCV]==max(counts.values())
    assert all(tuple(z['pos']) in CELLS for z in data['zones'])
    assert len(CELLS)>522531 and len(counts)>17 and math.prod((W,H,D))>9787165 and H>155
    print(dict(blocks=len(CELLS),materials=len(counts),size_xyz=data['size'],qcv=counts[QCV]),flush=True)
