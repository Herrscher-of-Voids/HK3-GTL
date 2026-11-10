# -*- coding: utf-8 -*-
"""I32独立几何：遗构剖析院，以扫描拱、拆解地轨与分层实验室表达逆向研究。

【变更记录 #1】2026-10-27：空白构图；只生成外观候选，不修改正式资源。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 263, 197, 253
CX, CZ = 131, 126
NAME = 'hk3gtl-i32-relic-reverse-lab-v1-20261027'
TITLE = '遗留技术逆向实验室 · 遗构剖析院'
QAV = 'hk3gtl:voltage_machine_casing_qav'
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
 QAV:'扫描拱、分层实验室及档案比对厅的主电压机壳',
 PORT:'齐平嵌入样本/档案/制样设备的接口候选',CONTROL:'正面批次接入实验厅中轴主控标记',
 ROBUST:'中空箱梁基础、扫描拱脚与检修行车承重件',CLEAN:'扫描拱银灰轮廓、观察窗框和洁净设备护边',
 ASSEMBLY:'洁净制样地板与拆解装配工位',COMPUTER:'技术档案交叉比对与遗留结构解析运算柜',
 ATOMIC:'高跨断层扫描头及成分解析端头',POWER:'扫描与制样机组的独立供能设备',
 LASER:'遗构断面读取面与失效样件检测设备',VENT:'分层实验室及制样厅屋顶散热百叶',
 GEAR:'扫描头定位行车、拆解架的传动机构',TUNG_PIPE:'断层读取供能母线与屏蔽管道',
 STEEL_PIPE:'制样试剂和废液分路管线',GRATE:'高跨扫描拱检修步道、机房通道及行车维护面',
 IRIDIUM:'未知遗留装置的银灰装甲碎片与样本屏蔽夹具',
 PROCESS:'拆解、制样与失败样件缺陷诊断工位',DIMENSION:'真实与模拟来源档案的隔离核验设备',
 MULTI:'多源档案交叉验证和既有舰船蓝图比对设备',GLASS:'实验室隔离观察窗及屋顶观察带',
 FILTER:'样本污染控制与废试剂检测设备',INERT:'遗留技术残片密闭接入和隔离舱',
 INSULATE:'断层扫描供能与洁净制样机组的绝缘底架',FROST:'样本冷保存和制样温控设备',
 STABLE:'试剂供给与废试剂回收缓冲设备',VIBRATION:'精密制样台与拆解地轨减振底座',
 PLASCRETE:'样本/档案实验厅的洁净地坪',BLUE_GLASS:'断面扫描头至样本的静态测量束',
 BLACK:'遗留装置断面内部的暗色空腔和未知核心',LIGHT:'扫描架、工位及检修平台照明',
}
CELLS={}


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
    # 贯穿全院的中空箱梁托起拆解轨道及实验室，工位不悬空。
    for y in range(15):
        for z in range(D):
            for x in range(W):
                edge=min(x,W-1-x,z,D-1-z)
                beam=x%29<3 or z%31<3
                if y<2 or y>=13 or edge<3 or beam:
                    put(x,y,z,ROBUST if y in (0,3,12,14) else QAV)
    for x in (CX-26,CX+26):
        box((x-6,15,37),(x+6,18,215),VIBRATION)
        box((x-4,19,37),(x+4,21,215),ROBUST)
        box((x-1,22,37),(x+1,23,215),CLEAN,True)
    for z in (64,103,151,190):
        box((CX-51,15,z-6),(CX+51,19,z+6),QAV,True)
        box((CX-45,20,z-5),(CX+45,23,z+5),ASSEMBLY,True)
        box((CX-37,24,z-4),(CX+37,25,z+4),GEAR,True)


def lab_hall(x0,x1,z0,z1,top,role):
    for y in range(15,top+1):
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                edge=min(x-x0,x1-x,z-z0,z1-z)
                floor=(y-15)%21<2 or y>=top-1
                if floor:
                    put(x,y,z,QAV if edge<5 or x%23<4 else ASSEMBLY,True)
                elif edge<3:
                    along=z-z0 if min(x-x0,x1-x)<3 else x-x0
                    window=edge==0 and 5<=along%22<=16 and 8<=(y-15)%21<=15
                    state=GLASS if window else QAV
                    if edge==0 and (y-15)%21 in (3,18):state=CLEAN
                    put(x,y,z,state,True)
    sets={'sample':(PROCESS,FILTER,FROST,INERT),'archive':(COMPUTER,MULTI,DIMENSION,COMPUTER)}
    for y in range(18,top-9,21):
        for i,x in enumerate(range(x0+7,x1-10,18)):
            for j,z in enumerate(range(z0+7,z1-10,22)):
                box((x,y-1,z),(x+8,y-1,z+11),QAV,True)
                box((x,y,z),(x+8,y+8,z+11),sets[role][(i+j)%4],True)
                box((x,y+9,z),(x+8,y+9,z+11),VENT,True)
    for z in range(z0+6,z1-8,22):
        box((x0+4,top+1,z),(x1-4,top+4,z+11),QAV)
        box((x0+6,top+5,z+2),(x1-6,top+5,z+9),VENT)
    for x in range(x0+7,x1-6,18):
        box((x,17,z0+6),(x+2,17,z1-6),LIGHT,True)


def laboratories():
    # 低层翼楼与高层窄廊共同承接扫描拱脚，形成一座可读的拆解实验院。
    lab_hall(0,49,44,208,78,'sample')
    lab_hall(213,262,44,208,78,'sample')
    lab_hall(29,49,57,195,113,'archive')
    lab_hall(213,233,57,195,113,'archive')
    lab_hall(57,205,8,43,57,'archive')
    lab_hall(57,205,209,244,57,'sample')
    for x0 in (58,186):
        for z in (57,91,125,159,193):
            box((x0,15,z),(x0+18,16,z+15),QAV,True)
            box((x0,17,z),(x0+18,21,z+15),INSULATE,True)
            box((x0+2,22,z+2),(x0+16,33,z+13),STABLE,True)
            box((x0+4,34,z+4),(x0+14,37,z+11),FILTER,True)
            line((x0+6,25,z-5),(x0+6,25,z+18),STEEL_PIPE,1,True)
    for z in (46,198):
        box((47,29,z),(215,33,z+8),QAV)
        box((47,34,z),(215,34,z+8),GRATE)
    for z0 in (14,215):
        box((64,17,z0),(198,17,z0+22),PLASCRETE,True)


def arch_point(theta,z):
    return (round(CX+88*math.cos(theta)),round(97+94*math.sin(theta)),z)


def scanning_vault():
    # 三道高跨扫描拱是完整断层设备，高度来自本体而非单独的塔。
    for z in (70,126,182):
        for x in (CX-88,CX+88):
            box((x-7,15,z-9),(x+7,101,z+9),QAV,True)
            box((x-10,15,z-12),(x+10,29,z+12),ROBUST,True)
            box((x-8,91,z-10),(x+8,99,z+10),GEAR,True)
        last=None
        for i in range(181):
            theta=math.pi*i/180
            p=arch_point(theta,z)
            if last:line(last,p,QAV,5,True)
            else:box(tuple(v-5 for v in p),tuple(v+5 for v in p),QAV,True)
            for dz in (-5,5):
                edge=(p[0],p[1],z+dz)
                box(tuple(v-1 for v in edge),tuple(v+1 for v in edge),CLEAN,True)
            last=p
        # 下悬扫描头有实体传动架和电力连接，测量束接触样本。
        box((CX-9,178,z-8),(CX+9,188,z+8),POWER,True)
        box((CX-7,167,z-7),(CX+7,177,z+7),COMPUTER,True)
        box((CX-10,159,z-10),(CX+10,166,z+10),ATOMIC,True)
        box((CX-7,158,z-7),(CX+7,158,z+7),LASER,True)
        line((CX,158,z),(CX,100,z),BLUE_GLASS,1,True)
    # 两翼的曲面屋面保留中央拆解天井，让内部遗构与高跨设备可见。
    for z in range(59,194):
        for i in list(range(0,49))+list(range(132,181)):
            theta=math.pi*i/180
            p=arch_point(theta,z)
            if z%18<3 or i%13<3:
                box((p[0]-2,p[1]-2,z),(p[0]+2,p[1]+2,z),QAV)
            elif i%13 in (3,4):
                box((p[0]-1,p[1]-1,z),(p[0]+1,p[1]+1,z),GLASS)
    # 拱脚间两侧悬挂检修行车，连续柱脚落在实验室结构上。
    for x in (CX-68,CX+68):
        box((x-4,118,54),(x+4,125,198),QAV)
        box((x-5,126,54),(x+5,127,198),GRATE)
        line((x,121,54),(x,121,198),TUNG_PIPE,1,True)
        for z in (58,126,194):
            line((x,118,z),(CX-88 if x<CX else CX+88,98,z),ROBUST,2)
        for z in (84,168):
            box((x-6,114,z-6),(x+6,126,z+6),GEAR,True)
            line((x,113,z),(x,61,z),ROBUST,1)
            box((x-8,54,z-8),(x+8,60,z+8),CLEAN,True)
    # 拱顶纵梁贯通三套扫描架，顶部维护面构成实际最高197格。
    box((CX-4,184,64),(CX+4,193,188),QAV,True)
    box((CX-6,194,64),(CX+6,196,188),GRATE,True)


def relic_specimen():
    # 遗构是拆开的未知机械，不是另一枚世界泡：双轨托架、断裂装甲和裸露内骨架。
    for z0,z1,width in ((60,85,25),(91,116,31),(122,147,37),(153,178,29),(184,201,21)):
        for side in (-1,1):
            box((CX+side*8-3,15,(z0+z1)//2-4),(CX+side*8+3,46,(z0+z1)//2+4),ROBUST,True)
        for z in range(z0,z1+1):
            for y in range(43,102):
                half=max(5,round(width*(1-abs(y-71)/35)))
                for x in range(CX-half,CX+half+1):
                    edge=min(x-(CX-half),(CX+half)-x)
                    rib=(z-z0)%13<3
                    armor=edge<3 or y in (43,44,99,100,101)
                    if armor or rib:
                        s=IRIDIUM if armor else ROBUST
                        if rib and edge<4:s=CLEAN
                        put(x,y,z,s,True)
        # 切口保留暗色内腔、独立运算核心和可辨认的断面。
        for z in (z0,z1):
            box((CX-12,43,z),(CX+12,46,z),IRIDIUM,True)
            for side in (-1,1):
                box((CX+side*10-2,44,z),(CX+side*10+2,100,z),ROBUST,True)
            box((CX-8,54,z),(CX+8,91,z),BLACK,True)
            box((CX-5,63,z),(CX+5,81,z),DIMENSION,True)
            box((CX-2,67,z),(CX+2,77,z),BLUE_GLASS,True)
        for side in (-1,1):
            line((CX+side*22,25,z0+3),(CX+side*(width+1),53,z0+7),ROBUST,3)
            box((CX+side*22-5,20,z0+1),(CX+side*22+5,29,z0+11),GEAR,True)
    # 几片卸下的遗留装甲放在原生工位上，边缘呈剖开/分离状态。
    for z in (88,148,194):
        for side in (-1,1):
            x=CX+side*52
            box((x-12,17,z-9),(x+12,20,z+9),VIBRATION,True)
            box((x-9,21,z-6),(x+9,26,z+6),CLEAN,True)
            box((x-7,27,z-4),(x+7,45,z+4),IRIDIUM,True)
            box((x-5,46,z-3),(x+5,47,z+3),LASER,True)
    # 正面制样台与后侧档案实验台保留清楚的分工。
    for x in (83,111,139,167):
        box((x,18,23),(x+11,22,33),PROCESS,True)
        box((x+2,23,25),(x+9,28,31),MULTI,True)
        box((x,18,219),(x+11,22,231),FROST,True)
        box((x+2,23,221),(x+9,29,229),INERT,True)


def markers():
    controller=[CX,28,8]
    ports=[
      dict(id='遗留技术残片输入',purpose='残片接入隔离核验及成分/结构解析工位',pos=[107,28,8],face='north'),
      dict(id='真实模拟日志输入',purpose='真实和模拟档案独立来源交叉验证',pos=[155,28,8],face='north'),
      dict(id='西侧实验供能',purpose='断层扫描及精密制样设备供能候选位',pos=[0,28,91],face='west'),
      dict(id='东侧实验供能',purpose='镜像实验供能支路候选位',pos=[262,28,91],face='east'),
      dict(id='西侧试剂输入',purpose='消耗性实验试剂及制样介质入口候选位',pos=[0,28,159],face='west'),
      dict(id='东侧废试剂输出',purpose='实验后废试剂独立输出候选位',pos=[262,28,159],face='east'),
      dict(id='逆向档案输出',purpose='交研究系统判定证据，不能自动解锁或自动毕业',pos=[107,28,244],face='south'),
      dict(id='复现样件输出',purpose='耗费实验材料完成的可复现样件交付',pos=[155,28,244],face='south'),
      dict(id='失败样件输出',purpose='失败件保留并送缺陷诊断，不伪装成研究成功',pos=[83,28,244],face='south'),
      dict(id='实验材料输入',purpose='复现与制样真实消耗材料，不开放免费蓝图复制',pos=[179,28,244],face='south'),
    ]
    for m in [dict(pos=controller,face='north',state=CONTROL)]+[dict(p,state=PORT) for p in ports]:
        x,y,z=m['pos']
        if m['face'] in ('north','south'):
            box((x-2,y-2,z),(x+2,y+2,z),QAV,True)
            dz=1 if m['face']=='north' else -1
            box((x-2,y-2,z+dz),(x+2,y+2,z+dz),QAV,True)
        else:
            box((x,y-2,z-2),(x,y+2,z+2),QAV,True)
            dx=1 if m['face']=='west' else -1
            box((x+dx,y-2,z-2),(x+dx,y+2,z+2),QAV,True)
        put(x,y,z,m['state'],True)
    paths=[dict(name='前侧样本及档案接入通廊',min=[73,16,0],max=[189,38,7]),
           dict(name='后侧样件与研究档案交接通廊',min=[73,16,245],max=[189,38,252])]
    for path in paths:
        lo,hi=path['min'],path['max']
        for y in range(lo[1],hi[1]+1):
            for z in range(lo[2],hi[2]+1):
                for x in range(lo[0],hi[0]+1):CELLS.pop((x,y,z),None)
    return controller,ports,paths


def build():
    CELLS.clear()
    foundation();laboratories();scanning_vault();relic_specimen()
    controller,ports,paths=markers()
    for p in list(CELLS):
        if p[0]>CX:del CELLS[p]
    for (x,y,z),s in list(CELLS.items()):
        if x<CX:CELLS[(W-1-x,y,z)]=s
    return dict(key='i32',name=NAME,title=TITLE,size=[W,H,D],controller=controller,controller_face='north',ports=ports,paths=paths,
      zones=[dict(name='三跨断层扫描拱',pos=[CX,190,126]),dict(name='分段遗留装置剖析台',pos=[CX,72,60]),
             dict(name='拆解地轨与装甲工位',pos=[CX-26,21,103]),dict(name='分层样本制备实验室',pos=[0,28,126]),
             dict(name='真实模拟档案比对厅',pos=[57,28,24]),dict(name='失败样件及逆向档案交接厅',pos=[57,28,226])],
      description='锈红QAV机壳构成三道高跨断层扫描拱，围护分段拆开的遗留装置；下方双轨拆解工位与行车、两侧分层实验室、前后档案比对与样件交接厅，共同组成一座可辨认的逆向研究设施。',
      construction_notes=dict(orientation='主控朝北/-Z，蓝图坐标从0起算。',anchor='本地[0,0,0]；推荐世界Y=-60，最高Y=136。',
        boundary='真实/模拟日志、技术残片和实验材料换成研究证据及耗材复现样件；不自动解锁、不替代普通量产，不把43条静态配方当作运行通过。',
        approval='独立外观候选，未获负责人批准、未接入实例。'),
      blocks=[dict(pos=list(p),state=s) for p,s in sorted(CELLS.items(),key=lambda t:(t[0][1],t[0][2],t[0][0]))])


if __name__=='__main__':
    from collections import Counter
    d=build();c=Counter(b['state'] for b in d['blocks'])
    assert c[CONTROL]==1 and c[PORT]==10 and c[QAV]==max(c.values())
    assert all(tuple(z['pos']) in CELLS for z in d['zones'])
    assert len(CELLS)>539129 and len({s.split('[')[0] for s in c})>19
    assert math.prod((W,H,D))>11970190 and H>190
    print(dict(blocks=len(CELLS),materials=len(c),size_xyz=d['size'],qav=c[QAV]),flush=True)
