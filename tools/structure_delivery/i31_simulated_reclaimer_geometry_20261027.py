# -*- coding: utf-8 -*-
"""I31独立几何：逆相沙漏回收庭，表达受控终止、收束及分流回收。

【变更记录 #1】2026-10-27：从空白布局构图；只生成外观候选，不改正式资源。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 371, 229, 371
CX, CZ = 185, 185
NAME = 'hk3gtl-i31-simulated-world-reclaimer-v1-20261027'
TITLE = '模拟世界泡终止回收机 · 逆相沙漏回收庭'
ICV = 'hk3gtl:voltage_machine_casing_icv'
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

PALETTE_ROLES = {
 ICV: '沙漏约束脊、终止冠环及回收厂房的主体电压机壳',
 PORT: '原生工艺外壳内的接口候选标记', CONTROL: '北侧批次控制厅中轴主控标记',
 ROBUST: '中空设备地基、沙漏承座及机房承重箱梁', CLEAN: '终止冠环、沙漏肋与回收厅的银灰护边',
 ASSEMBLY: '回收机组分层地板与设备装配面', COMPUTER: '批次一次性结算和来源核验的运算柜',
 ATOMIC: '终止场冠环与收束腰部的场发生器', POWER: '终止脉冲及收束场的分路电源机组',
 LASER: '受控消解与质量计量设备的局部读取面', TURBINE: '流体回收机组的分离旋转设备',
 MACERATOR: '终止残件的回收破碎处理设备', VENT: '长跨工艺厂房和控制厅屋顶散热百叶',
 GEAR: '沙漏冠环的径向锁扣及驱动检修箱', TUNG_PIPE: '终止能量母线与回收支路屏蔽管',
 STEEL_PIPE: '上下游封闭流体分离管路', GRATE: '环形检修走台、厂房维护通道及连接桥',
 IRIDIUM: '终止腰部与载体隔离室的局部屏蔽', PROCESS: '残件分级、物资封装与独立批次转运设备',
 DIMENSION: '模拟载体接入与终止后的状态封存设备', MULTI: '模拟日志校验及分流控制机组',
 LAFIUM: '流体回收计量与回收泵伺服设备', GLASS: '回收厂房和控制厅连续隔离观察窗',
 FILTER: '终止回收物的污染筛选和档案核验机组', INERT: '稳定模拟载体的隔离交接缓冲仓',
 HEATPROOF: '终止脉冲热端和高温回收支路的屏蔽壳', INSULATE: '终止能量机组的绝缘底架',
 FROST: '回收流体冷端换热壳体', STABLE: '流体回收缓存和回路压力调节设备',
 SOLID: '重型物资分级与回收分离设备基础', INTAKE: '长跨回收厂房屋顶进气百叶',
 STRESS: '沙漏约束脊承座与冠环径向锁扣承压件', MIXING: '回收流体缓冲及相容分流设备',
 VIBRATION: '分离旋转机组及固体回收线的减振底座', PLASCRETE: '批次核验及物资交接厂房洁净地坪',
 BLUE_GLASS: '从模拟世界泡至沙漏收束腰部的静态消解轨迹',
 BLACK_GLASS: '黑色模拟世界泡细窄观测缝', BLACK: '被受控终止的等半径模拟世界泡外壳',
 LIGHT: '维护走道、冠环操作位及回收厅照明',
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
    steps = max(abs(a[i] - b[i]) for i in range(3))
    p = list(a)
    for k in range(steps + 1):
        q = [round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3)]
        for axis in range(3):
            while p[axis] != q[axis]:
                p[axis] += 1 if q[axis] > p[axis] else -1
                box(tuple(v - radius for v in p), tuple(v + radius for v in p), state, replace)
        box(tuple(v - radius for v in q), tuple(v + radius for v in q), state, replace)


def radial(a, r, y):
    return (round(CX + math.cos(a) * r), int(y), round(CZ + math.sin(a) * r))


def ring(y0, y1, inner, outer, state, replace=False):
    for z in range(CZ - outer, CZ + outer + 1):
        for x in range(CX - outer, CX + outer + 1):
            rr = (x - CX) ** 2 + (z - CZ) ** 2
            if inner * inner <= rr <= outer * outer:
                for y in range(y0, y1 + 1):
                    put(x, y, z, state, replace)


def foundation():
    # 中空箱梁与三层作业地坪承担整座回收庭，不以实心底座凑材料。
    for y in range(25):
        for z in range(D):
            for x in range(W):
                rr = (x - CX) ** 2 + (z - CZ) ** 2
                district = x < 82 or x > 288 or z < 68 or z > 302
                on_plan = rr <= 148 ** 2 or district
                if not on_plan:
                    continue
                edge = min(x, W - 1 - x, z, D - 1 - z)
                beam = x % 31 < 3 or z % 31 < 3
                if y < 2 or y >= 23 or beam or edge < 2:
                    put(x, y, z, ROBUST if y in (0, 5, 21, 24) else ICV)
    for y in (25, 33, 39):
        ring(y, y + 1, 36, 146, ICV)
        ring(y + 2, y + 2, 141, 146, CLEAN, True)
    ring(27, 39, 139, 145, ICV)
    ring(28, 39, 34, 40, ICV)
    ring(42, 43, 125, 139, GRATE)
    # 八条下部出料地沟把沙漏腰部经分离机组接到回收庭。
    for k in range(8):
        a = math.pi * (k + .5) / 4
        line(radial(a, 27, 33), radial(a, 140, 33), ROBUST, 4)
        line(radial(a, 30, 40), radial(a, 138, 40), STEEL_PIPE, 2, True)


def hall(x0, x1, z0, z1, top, role):
    for y in range(25, top + 1):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                edge = min(x-x0, x1-x, z-z0, z1-z)
                floor = (y-25) % 22 < 2 or y >= top-1
                if floor:
                    put(x,y,z,ICV if edge < 6 or x % 23 < 4 else ASSEMBLY, True)
                elif edge < 3:
                    along = z-z0 if min(x-x0,x1-x)<3 else x-x0
                    s = GLASS if edge == 0 and 6 <= along % 27 <= 20 and 9 <= (y-25)%22 <= 16 else ICV
                    if edge == 0 and (y-25)%22 in (4,19): s = CLEAN
                    put(x,y,z,s,True)
    sets = {'solid':(MACERATOR,PROCESS,SOLID,FILTER), 'fluid':(TURBINE,MIXING,STABLE,FROST),
            'batch':(COMPUTER,DIMENSION,INERT,MULTI)}
    for y in range(28, top-10, 22):
        for i,x in enumerate(range(x0+9,x1-14,19)):
            for j,z in enumerate(range(z0+9,z1-14,23)):
                box((x,y-1,z),(x+11,y-1,z+13),ICV,True)
                box((x,y,z),(x+11,y+10,z+13),sets[role][(i+j)%4],True)
                box((x,y+11,z),(x+11,y+11,z+13),VENT,True)
    # 分段起伏的屋顶机房脊与采光带形成工业长跨厂房。
    for z in range(z0+7,z1-10,26):
        box((x0+5,top+1,z),(x1-5,top+6,z+15),ICV)
        box((x0+8,top+7,z+3),(x1-8,top+7,z+11),VENT)
        box((x0+7,top+2,z+15),(x1-7,top+4,z+15),GLASS,True)
    for z in range(z0+10,z1-6,52):
        box((x0+13,top+8,z),(x0+23,top+8,z+6),INTAKE)


def districts():
    hall(0,80,65,305,90,'solid')
    hall(290,370,65,305,90,'solid')
    hall(106,264,8,67,74,'batch')
    hall(106,264,303,362,74,'batch')
    # 外侧厂房内部分区，不改变镜像主体材料。
    for x0 in (15,302):
        for z in (95,165,235):
            box((x0,28,z),(x0+53,32,z+37),VIBRATION,True)
            box((x0+4,33,z+4),(x0+49,48,z+33),PROCESS,True)
            box((x0+10,49,z+9),(x0+43,57,z+28),TURBINE,True)
    for z0 in (51,291):
        box((154,25,z0),(216,28,z0+29),ICV,True)
        box((154,29,z0),(216,29,z0+29),GRATE,True)
    for z in (112,258):
        box((67,26,z),(303,31,z+10),ROBUST)
        box((67,32,z+1),(303,34,z+9),ICV)
        box((67,35,z),(303,35,z+10),GRATE)
    for z0 in (14,309):
        box((115,27,z0),(255,27,z0+46),PLASCRETE,True)


def crown_and_hourglass():
    # 双向沙漏轮廓：下部多路回收管展开，细腰锁定批次，上部冠环围护受控终止场。
    for y0,y1,ri,ro,s in ((44,49,105,122,ICV),(50,52,112,124,CLEAN),
                         (94,98,22,39,ICV),(99,109,20,34,IRIDIUM),
                         (110,114,21,38,ATOMIC),(115,118,24,41,ICV),
                         (213,219,73,96,ICV),(220,222,70,99,CLEAN),
                         (223,227,74,95,ICV),(228,228,78,92,GRATE)):
        ring(y0,y1,ri,ro,s,True)
    # 十二道粗细分层的约束脊连续落在底部承座，不额外添高塔。
    for k in range(12):
        a = math.pi * (k+.5) / 6
        last = None
        for y in range(46,219):
            r = 28 + 85*((106-y)/60)**1.3 if y <= 106 else 28+57*((y-106)/112)**.8
            p = radial(a,r,y)
            if last: line(last,p,ICV,3,True)
            else: box(tuple(v-3 for v in p),tuple(v+3 for v in p),ICV,True)
            for side in (-1,1):
                edge=(round(p[0]-math.sin(a)*side*3),y,round(p[2]+math.cos(a)*side*3))
                box(tuple(v-1 for v in edge),tuple(v+1 for v in edge),CLEAN,True)
            last=p
        foot=radial(a,113,46)
        box((foot[0]-9,34,foot[2]-9),(foot[0]+9,49,foot[2]+9),ICV,True)
        box((foot[0]-6,45,foot[2]-6),(foot[0]+6,49,foot[2]+6),STRESS,True)
        end=radial(a,84,217)
        box((end[0]-6,209,end[2]-6),(end[0]+6,218,end[2]+6),GEAR,True)
    # 腰部是有承重与隔离壁的狭窄设备，不是两座悬空拼接物。
    ring(90,120,0,22,ICV,True)
    for k in range(8):
        a=math.pi*(k+.5)/4
        line(radial(a,22,108),radial(a,105,49),TUNG_PIPE,3,True)
        line(radial(a,23,107),radial(a,104,51),BLUE_GLASS,1,True)
        p=radial(a,98,56)
        box((p[0]-8,40,p[2]-8),(p[0]+8,64,p[2]+8),LAFIUM,True)
        box((p[0]-7,65,p[2]-7),(p[0]+7,66,p[2]+7),LASER,True)
    for y,ri,ro in ((68,73,81),(145,41,48),(181,61,68)):
        ring(y,y+3,ri,ro,ICV)
        ring(y+4,y+4,ri,ro,CLEAN,True)


def bubble_and_decay():
    # 世界泡保持等半径正球体；终止由向腰部汇聚的流束表达，不做球面分区配色。
    r,cy=37,177
    for dy in range(-r,r+1):
        for dz in range(-r,r+1):
            for dx in range(-r,r+1):
                rr=dx*dx+dy*dy+dz*dz
                if (r-3)**2 <= rr <= r*r:
                    put(CX+dx,cy+dy,CZ+dz,BLACK_GLASS if abs(dy)<=1 else BLACK,True)
    ring(119,130,0,12,ATOMIC,True)
    line((CX,127,CZ),(CX,140,CZ),BLUE_GLASS,2,True)
    for k in range(8):
        a=math.pi*(k+.5)/4
        # 收束轨迹与球体外壳真实接触，底端汇入腰部终止腔。
        pts=[radial(a,31,157),radial(a,30,144),radial(a,18,129),radial(a,12,119)]
        for p,q in zip(pts,pts[1:]): line(p,q,BLUE_GLASS,1,True)
        line(radial(a,36,177),radial(a,66,181),BLUE_GLASS,1,True)
        p=radial(a,64,181)
        box((p[0]-4,177,p[2]-4),(p[0]+4,185,p[2]+4),ATOMIC,True)


def recovery_equipment():
    # 下部八瓣回收机组分别承接固体、流体和热端；配色由材料用途决定。
    for k in range(8):
        a=math.pi*(k+.5)/4
        p=radial(a,83,49); x,z=p[0],p[2]
        box((x-11,34,z-11),(x+11,39,z+11),INSULATE,True)
        box((x-9,40,z-9),(x+9,51,z+9),HEATPROOF,True)
        box((x-7,52,z-7),(x+7,60,z+7),SOLID,True)
        box((x-5,61,z-5),(x+5,69,z+5),MACERATOR,True)
        box((x-10,70,z-10),(x+10,71,z+10),GRATE,True)
        for offset,s in ((-6,FROST),(6,STABLE)):
            q=radial(a,117+offset,57)
            box((q[0]-5,35,q[2]-5),(q[0]+5,59,q[2]+5),s,True)
            box((q[0]-6,60,q[2]-6),(q[0]+6,61,q[2]+6),MIXING,True)
    for x in (84,286):
        for z in (118,252):
            box((x-8,30,z-11),(x+8,35,z+11),ICV,True)
            box((x-6,36,z-9),(x+6,57,z+9),POWER,True)
            box((x-7,58,z-10),(x+7,58,z+10),LIGHT,True)
    # 检修梯直接沿沙漏下肢连到环台，留出连续可读的维护路径。
    for side in (-1,1):
        for step in range(50):
            x=CX+side*(132-step)
            box((x-3,40+step,CZ-5),(x+3,40+step,CZ+5),ICV,True)
            box((x-3,41+step,CZ-5),(x+3,41+step,CZ+5),GRATE,True)
        line((CX+side*82,89,CZ),(CX+side*33,99,CZ),GRATE,2,True)


def markers():
    controller=[CX,36,8]
    ports=[
      dict(id='稳定模拟批次输入',purpose='接收I30同一持久化批次和状态载体，不创建第二个结算来源',pos=[161,36,8],face='north'),
      dict(id='批次核验及许可',purpose='核验模拟来源与批次状态；不替代正式研究许可',pos=[209,36,8],face='north'),
      dict(id='西侧终止供能',purpose='受控终止及分流回收的持续控制能量候选位',pos=[0,36,112],face='west'),
      dict(id='东侧终止供能',purpose='镜像终止供能支路候选位',pos=[370,36,112],face='east'),
      dict(id='西侧流体回收',purpose='同既定资源目录的随机流体独立输出候选位',pos=[0,36,258],face='west'),
      dict(id='东侧流体回收',purpose='镜像回收流体缓冲与交付候选位',pos=[370,36,258],face='east'),
      dict(id='随机物品输出',purpose='按已定目录和概率原则结算的随机物品输出',pos=[161,36,362],face='south'),
      dict(id='模拟日志输出',purpose='终止日志及模拟来源档案交I32研究，不能当作免费资源',pos=[209,36,362],face='south'),
      dict(id='残件交付',purpose='批次终止残件独立交付，不擅定种子返还或增产倍率',pos=[137,36,362],face='south'),
      dict(id='回收热流体排出',purpose='回收热端流体经独立管路交既有换热工艺',pos=[233,36,362],face='south'),
    ]
    for m in [dict(pos=controller,face='north',state=CONTROL)]+[dict(p,state=PORT) for p in ports]:
        x,y,z=m['pos']
        if m['face'] in ('north','south'):
            box((x-2,y-2,z),(x+2,y+2,z),ICV,True)
            delta=1 if m['face']=='north' else -1
            box((x-2,y-2,z+delta),(x+2,y+2,z+delta),ICV,True)
        else:
            box((x,y-2,z-2),(x,y+2,z+2),ICV,True)
            delta=1 if m['face']=='west' else -1
            box((x+delta,y-2,z-2),(x+delta,y+2,z+2),ICV,True)
        put(x,y,z,m['state'],True)
    paths=[dict(name='北侧批次接入与主控操作通廊',min=[127,26,0],max=[243,46,7]),
           dict(name='南侧物资及档案交接通廊',min=[127,26,363],max=[243,46,370])]
    for path in paths:
        lo,hi=path['min'],path['max']
        for y in range(lo[1],hi[1]+1):
            for z in range(lo[2],hi[2]+1):
                for x in range(lo[0],hi[0]+1): CELLS.pop((x,y,z),None)
    return controller,ports,paths


def build():
    CELLS.clear()
    foundation(); districts(); crown_and_hourglass(); bubble_and_decay(); recovery_equipment()
    controller,ports,paths=markers()
    for p in list(CELLS):
        if p[0]>CX: del CELLS[p]
    for (x,y,z),s in list(CELLS.items()):
        if x<CX: CELLS[(W-1-x,y,z)]=s
    return dict(key='i31',name=NAME,title=TITLE,size=[W,H,D],controller=controller,controller_face='north',ports=ports,paths=paths,
      zones=[dict(name='冠环受控终止场',pos=[CX,216,CZ-80]),dict(name='正球体模拟世界泡',pos=[CX,177,CZ-37]),
             dict(name='一次批次终止锁及沙漏腰腔',pos=[CX,106,CZ]),dict(name='八向物资分流回收机组',pos=[CX,40,CZ-110]),
             dict(name='长跨物资分级厂房',pos=[0,36,185]),dict(name='批次与模拟日志交接厅',pos=[106,36,332])],
      description='金棕ICV机壳构成十二道连续沙漏约束脊：上部冠环围护黑色模拟世界泡，冷蓝消解束收向窄腰终止腔，下部八向管路展开至物资分离与回收厂房；批次接入、受控终止、物品流体分流及模拟日志交接可从建筑辨认。',
      construction_notes=dict(orientation='主控朝北/-Z，蓝图从0起算。',anchor='本地[0,0,0]；推荐世界Y=-60，最高Y=168。',
        boundary='造型仅表达I31职责。模拟与真实独立记账，同一持久化批次只结算一次；不改既定随机目录、概率、真实十次计数或舰船保底。运行、断电维护、种子返还和增产倍率均未据此批准。',
        approval='独立外观候选，未获负责人批准，未接入游戏。'),
      blocks=[dict(pos=list(p),state=s) for p,s in sorted(CELLS.items(),key=lambda t:(t[0][1],t[0][2],t[0][0]))])


if __name__=='__main__':
    from collections import Counter
    d=build(); c=Counter(b['state'] for b in d['blocks'])
    assert c[CONTROL]==1 and c[PORT]==10 and c[ICV]==max(c.values())
    assert all(tuple(z['pos']) in CELLS for z in d['zones'])
    assert len(CELLS)>1779878 and len({s.split('[')[0] for s in c})>37
    assert math.prod((W,H,D))>23281645 and H>205
    print(dict(blocks=len(CELLS),materials=len(c),size_xyz=d['size'],icv=c[ICV]),flush=True)
