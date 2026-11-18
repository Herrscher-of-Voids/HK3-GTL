# -*- coding: utf-8 -*-
"""I27：从零构建锁界环、约束井及独立封存回收厅。"""
import collections
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 337, 205, 337
CX = CZ = 168
NAME = 'hk3gtl-i27-whole-world-capture-array-v1-20261026'
TITLE = '世界泡整体捕获阵列 · 锁界环形回收坞'
IMV = 'hk3gtl:voltage_machine_casing_imv'
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
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
BLACK_GLASS = 'minecraft:black_stained_glass'
BLACK = 'minecraft:black_concrete'
LIGHT = 'minecraft:sea_lantern'
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
    """逐轴补齐斜梁，使曲线及约束导束保持六邻接。"""
    steps = max(abs(b[i]-a[i]) for i in range(3))
    previous = list(a)
    for step in range(steps+1):
        target = [round(a[i]+(b[i]-a[i])*step/max(1,steps)) for i in range(3)]
        for axis in range(3):
            while previous[axis] != target[axis]:
                previous[axis] += 1 if target[axis] > previous[axis] else -1
                box(tuple(v-radius for v in previous),tuple(v+radius for v in previous),state,replace)
        box(tuple(v-radius for v in target),tuple(v+radius for v in target),state,replace)


def polar(radius, y, angle):
    return (round(CX+radius*math.cos(angle)),round(y),round(CZ+radius*math.sin(angle)))


def annulus(inner, outer, y0, y1, state):
    for z in range(max(0,CZ-outer),min(D,CZ+outer+1)):
        for x in range(max(0,CX-outer),min(W,CX+outer+1)):
            r2=(x-CX)**2+(z-CZ)**2
            if inner**2 <= r2 <= outer**2:
                for y in range(y0,y1+1):put(x,y,z,state)


def ring_foundation():
    # 两层环形工艺基座与中层检修廊；空心井口供约束场及封存转运使用。
    for y in (0,1,24,25):
        for z in range(D):
            for x in range(W):
                r=math.hypot(x-CX,z-CZ)
                if 79 <= r <= 168:
                    grid=(x%18 in (0,1) or z%18 in (0,1))
                    put(x,y,z,IMV if grid or y in (0,24) else GRATE)
    annulus(113,168,12,12,IMV)
    for z in range(D):
        for x in range(W):
            r=math.hypot(x-CX,z-CZ)
            if 166 <= r <= 168 or 79 <= r <= 82:
                a=math.atan2(z-CZ,x-CX)
                panel=int((a+math.pi)*72/(2*math.pi))
                for y in range(2,24):
                    window=y in range(5,10) or y in range(17,22)
                    state=BLUE_GLASS if window and panel%6 in (1,2,3) else IMV
                    if y in (2,11,13,23):state=ROBUST
                    put(x,y,z,state)
    # 十二条径向承重梁及其竖向肋柱，贯穿环廊并通向捕获井。
    for i in range(12):
        a=i*math.pi/6
        for radius in range(80,168):
            p=polar(radius,0,a)
            box((max(0,p[0]-1),2,max(0,p[2]-1)),(min(W-1,p[0]+1),3,min(D-1,p[2]+1)),ROBUST)
        for radius in (91,115,141,163):
            x,_,z=polar(radius,0,a)
            box((x-2,2,z-2),(x+2,23,z+2),IMV)
    annulus(0,79,0,1,IMV)
    for x in (154,180):box((x,2,151),(x+2,26,185),IMV)


def hall(x0,x1,z0,z1,y0,y1,role):
    # 同一紫色建筑语汇：完整墙体、分段观察窗、银色屋檐及有设备的屋面。
    for y in range(y0,y1+1):
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                edge=x in (x0,x1) or z in (z0,z1)
                if y in (y0,y0+14,y1):
                    put(x,y,z,IMV if edge or x%13 in (0,1) else GRATE,True)
                elif edge:
                    window=y0+5<=y<=y0+10 or y0+19<=y<=y1-4
                    on_pier=((x-x0)%17 in (0,1,2) if z in (z0,z1) else (z-z0)%17 in (0,1,2))
                    if x in (x0,x1) and z in (z0,z1):on_pier=True
                    state=BLUE_GLASS if window and not on_pier else IMV
                    if y in (y0+1,y0+13,y0+15,y1-1):state=ROBUST
                    put(x,y,z,state,True)
    rib_count=max(1,(x1-x0-8)//14+1)
    rib_start=(x0+x1-((rib_count-1)*14+4))//2
    for x in range(rib_start,rib_start+rib_count*14,14):
        box((x,y1+1,z0+4),(x+4,y1+3,z1-4),IMV)
        for z in range(z0+8,z1-5,16):
            box((x,y1+4,z),(x+4,y1+5,z+5),VENT)
    gear=(COMPUTER,MULTI,LAFIUM,STABLE) if role=='control' else (FILTER,PROCESS,MACERATOR,MIXING)
    for i,x in enumerate(range(x0+8,x1-8,15)):
        for j,z in enumerate(range(z0+8,z1-8,17)):
            box((x,y0+1,z),(x+5,y0+9,z+6),gear[(i+j)%len(gear)],True)
            box((x,y0+10,z),(x+5,y0+10,z+6),GRATE,True)


def service_halls():
    hall(121,215,18,76,26,57,'control')
    hall(121,215,250,322,26,62,'recovery')
    hall(12,67,119,217,26,59,'power')
    hall(269,324,119,217,26,59,'power')
    # 独立南向封存入口与井底交接隧道，轨道和地坪连续进入回收厅。
    for z in range(213,274):
        for x in range(155,182):
            put(x,25,z,IMV,True)
            put(x,26,z,GEAR if x in (159,177) else GRATE,True)
            if x in (155,181):
                box((x,27,z),(x,37,z),IMV,True)
        if z%12==0:box((155,38,z),(181,40,z),ROBUST)
    # 三座封存转运鞍座；不是复制世界泡或已工作的游戏容器。
    for x in (139,168,197):
        box((x-8,27,285),(x+8,29,307),GEAR,True)
        for y in range(30,47):
            for z in range(287,306):
                for px in range(x-6,x+7):
                    if px in (x-6,x+6) or z in (287,305) or y in (30,46):
                        state=IRIDIUM if y in (30,46) or z in (287,305) else IMV
                        put(px,y,z,state,True)
        box((x-4,35,286),(x+4,38,286),COMPUTER,True)
    # 主控操作平台、后侧容器装卸平台均与建筑外墙齐平。
    box((132,26,9),(204,34,17),IMV)
    box((132,34,9),(204,34,17),GRATE,True)
    box((140,26,323),(196,34,330),IMV)
    box((140,34,323),(196,34,330),GRATE,True)
    for y in range(26,35):
        z=1+(y-26)
        box((157,26,z),(179,y,z),CLEAN)


def lock_ring():
    # 竖向锁界主环本身决定205格高度，底部入井，两侧承力，不另加高塔。
    for y in range(20,205):
        for x in range(76,261):
            r=math.hypot(x-CX,y-112)
            if not 83<=r<=92:continue
            angle=math.atan2(y-112,x-CX)
            segment=int((angle+math.pi)*24/(2*math.pi))
            for z in range(158,179):
                state=IMV
                if z in (158,178):state=CLEAN
                elif r>90.5:state=ROBUST
                elif r<85:state=ATOMIC
                if segment%3==0 and r<87 and z in range(163,174):state=LAFIUM
                if segment%3==0 and 85<=r<86.2 and z in (161,175):state=LIGHT
                put(x,y,z,state,True)
    for side in (-1,1):
        # 从侧厅地脚抬升的三角扶壁，接到主环中腰。
        points=[(CX+side*126,26,CZ),(CX+side*111,65,CZ),(CX+side*94,112,CZ)]
        for a,b in zip(points,points[1:]):line(a,b,IMV,5,True)
        line((CX+side*131,26,CZ-8),(CX+side*95,108,CZ-8),CLEAN,1,True)
        line((CX+side*131,26,CZ+8),(CX+side*95,108,CZ+8),CLEAN,1,True)
        for y in range(34,107,12):
            x=round(CX+side*(126-(y-26)*.39))
            box((x-5,y,CZ-7),(x+5,y+2,CZ+7),ROBUST,True)


def cradle_and_clamps():
    annulus(72,120,47,49,IMV)
    annulus(73,76,50,52,CLEAN)
    annulus(113,120,50,53,IMV)
    annulus(79,81,50,51,ATOMIC)
    annulus(108,110,50,51,ROBUST)
    for i in range(12):
        a=i*math.pi/6
        x,_,z=polar(105,0,a)
        box((x-6,26,z-6),(x+6,46,z+6),IMV)
        box((x-4,30,z-7),(x+4,41,z-7),INTAKE,True)
        box((x-5,44,z-5),(x+5,46,z+5),GEAR,True)
        p=polar(88,54,a)
        box((p[0]-4,50,p[2]-4),(p[0]+4,58,p[2]+4),POWER)
        line(polar(88,59,a),polar(67,69,a),TUNG_PIPE,1)
        line(polar(67,69,a),polar(32,80,a),BLUE_GLASS,1)
    for angle in (45,135,225,315):
        a=math.radians(angle)
        points=[polar(r,y,a) for r,y in ((137,26),(120,70),(96,116),(67,147),(51,135))]
        for p,q in zip(points,points[1:]):line(p,q,IMV,4,True)
        for r,y in ((128,49),(111,87),(85,128),(67,147)):
            x,_,z=polar(r,y,a)
            box((x-6,y-2,z-6),(x+6,y+2,z+6),CLEAN,True)
            box((x-3,y-1,z-7),(x+3,y+1,z-7),ATOMIC,True)
        line(polar(51,135,a),polar(41,131,a),BLUE_GLASS,1,True)
        line(polar(134,28,a+.035),polar(69,143,a+.035),STEEL_PIPE,0)


def world_bubble():
    # 同半径正球壳，内部留空；黑色仅用于真实目标的建筑示意。
    radius=46
    for y in range(66,159):
        for z in range(CZ-radius,CZ+radius+1):
            for x in range(CX-radius,CX+radius+1):
                r2=(x-CX)**2+(y-112)**2+(z-CZ)**2
                if 43**2 <= r2 <= radius**2:
                    put(x,y,z,BLACK_GLASS if r2>45**2 else BLACK,True)
    # 底部约束点与极靴实接；不以孤立浮空方块假装工程结构。
    line((CX,53,CZ),(CX,65,CZ),BLUE_GLASS,1)
    box((CX-5,48,CZ-5),(CX+5,53,CZ+5),ATOMIC)
    for a in (0,math.pi/2,math.pi,3*math.pi/2):
        line(polar(72,48,a),(CX,48,CZ),IMV,2)


def auxiliary_equipment():
    # 设备仅布置在环形工艺廊，少量异材用于各自的换热、过滤和传动细节。
    states=(TURBINE,MACERATOR,VENT,GEAR,PROCESS,DIMENSION,MULTI,LAFIUM,GLASS,
            FILTER,INERT,HEATPROOF,INSULATE,FROST,STABLE,SOLID,STRESS,MIXING,LASER)
    for i in range(24):
        a=i*math.pi/12
        for floor in (2,13):
            x,_,z=polar(144,floor,a)
            state=states[(i+(floor//12)*7)%len(states)]
            box((x-4,floor,z-4),(x+4,floor+7,z+4),IMV)
            box((x-3,floor+1,z-5),(x+3,floor+5,z-5),state,True)
            box((x-3,floor+8,z-3),(x+3,floor+8,z+3),GRATE)
    for a in (math.radians(30),math.radians(150),math.radians(210),math.radians(330)):
        x,_,z=polar(140,0,a)
        box((x-12,26,z-9),(x+12,29,z+9),IMV)
        for dx in (-8,0,8):
            box((x+dx-2,30,z-6),(x+dx+2,47,z+6),FROST)
            box((x+dx-2,48,z-6),(x+dx+2,49,z+6),TURBINE)
            box((x+dx-2,31,z-7),(x+dx+2,44,z-7),VENT,True)
        line((x,29,z-9),polar(113,47,a),STEEL_PIPE,1)


def build():
    CELLS.clear()
    ring_foundation()
    service_halls()
    lock_ring()
    cradle_and_clamps()
    world_bubble()
    auxiliary_equipment()
    controller=[CX,35,18]
    ports=[{'id':'坐标数据输入','purpose':'接收I25有效目标坐标，前调度厅齐平接口','pos':[146,35,18],'face':'north'},
           {'id':'锁定与研究授权','purpose':'接收I44目标锁定及RN-WBC许可候选','pos':[190,35,18],'face':'north'},
           {'id':'西侧约束能源','purpose':'西侧脉冲供能厅外墙','pos':[12,35,140],'face':'west'},
           {'id':'西侧维护','purpose':'西侧场发生器维护通道','pos':[12,35,196],'face':'west'},
           {'id':'东侧约束能源','purpose':'东侧脉冲供能厅外墙','pos':[324,35,140],'face':'east'},
           {'id':'捕获异常与场衰减记录','purpose':'状态恢复与记录交换，东侧设备厅','pos':[324,35,196],'face':'east'},
           {'id':'空收容容器输入','purpose':'独立回收厅后侧容器交接，不代表世界泡可制造','pos':[154,35,322],'face':'south'},
           {'id':'封存世界泡输出','purpose':'保留真实目标UUID及已采次数，封存后送I28','pos':[182,35,322],'face':'south'}]
    normals={'north':(0,0,-1),'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
    for marker in [dict(pos=controller,face='north'),*ports]:
        x,y,z=marker['pos'];n=normals[marker['face']]
        # 外壳局部连续，标记替换外墙格，不附加独立接口载体。
        if n[2]:box((x-1,y-1,z),(x+1,y+1,z),IMV,True)
        else:box((x,y-1,z-1),(x,y+1,z+1),IMV,True)
        put(x-n[0],y,z-n[2],IMV,True)
        for step in range(1,5):
            for dy in range(4):CELLS.pop((x+n[0]*step,y+dy,z+n[2]*step),None)
        for step in range(1,5):put(x+n[0]*step,y-1,z+n[2]*step,GRATE,True)
    put(*controller,CONTROL,True)
    for p in ports:put(*p['pos'],PORT,True)
    return {'key':'I27','id':'I27','name':NAME,'title':TITLE,'size':[W,H,D],
            'target_voltage':'IMV','voltage_mapping':'V09 / tier23','candidate_version':'V1',
            'description':'竖向锁界环与四臂约束井夹持黑色正球世界泡；环形服务廊承接独立封存回收厅。',
            'controller':controller,'ports':ports,
            'world_bubble':{'center':[CX,112,CZ],'radius':46,'shell_inner_radius':43,'shape':'等半径正球壳','meaning':'捕获目标的静态建筑示意，不是世界泡复制品或运行实体'},
            'zones':[{'name':'竖向锁界主环','pos':[CX,199,CZ],'min':[76,20,158],'max':[260,204,178]},
                     {'name':'四臂牵引与约束井','pos':[CX,112,CZ],'min':[48,26,48],'max':[288,158,288]},
                     {'name':'前置目标调度厅','pos':[CX,62,47],'min':[121,26,18],'max':[215,62,76]},
                     {'name':'独立封存回收厅','pos':[CX,67,286],'min':[121,26,250],'max':[215,67,322]},
                     {'name':'西侧脉冲供能厅','pos':[40,64,CZ],'min':[12,26,119],'max':[67,64,217]},
                     {'name':'东侧脉冲供能厅','pos':[296,64,CZ],'min':[269,26,119],'max':[324,64,217]}],
            'paths':[{'name':'主控操作区','min':[157,35,14],'max':[179,38,17]},
                     {'name':'封存交接操作区','min':[146,35,323],'max':[190,38,326]}],
            'construction_notes':{'origin':'蓝图0起算，主控朝-Z；格位说明为坐标加1。','paste_y':-60,'world_top_y':144,
                                  'logic':'I25有效坐标与I44锁定→整体捕获→封存交接；不承担I26采掘或I28终止结算。'},
            'blocks':[{'pos':list(p),'state':s} for p,s in sorted(CELLS.items(),key=lambda e:(e[0][1],e[0][2],e[0][0]))]}


if __name__=='__main__':
    data=build()
    print(len(data['blocks']),len(set(CELLS.values())),collections.Counter(CELLS.values()).most_common(5))
