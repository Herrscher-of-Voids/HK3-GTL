# -*- coding: utf-8 -*-
"""I41扇形负载调度港：六路测控廊、弧幕母线与前置调度厅。
变更记录 #1（2026-10-28）：新增独立几何；不沿用合成工场或旧I37造型，不接入运行逻辑。
"""
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 591, 285, 471, 295
NAME = 'hk3gtl-i41-fan-dispatch-v1-20261028'
TITLE = '文明能源调度中枢 · 弧幕母线与扇形负载港'


class Material:
    IWV = 'hk3gtl:voltage_machine_casing_iwv'
    CONTROL = 'minecraft:diamond_block'
    PORT = 'hk3gtl:industrial_port_casing'
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
    LAMINATED = 'gtceu:laminated_glass'
    FUSION_GLASS = 'gtceu:fusion_glass'
    BLUE_GLASS = 'minecraft:light_blue_stained_glass'
    BLACK_GLASS = 'minecraft:black_stained_glass'
    LIGHT = 'minecraft:sea_lantern'
    GOLD = 'minecraft:gold_block'
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i+1 for i, s in enumerate(STATES)}
ROLES = {s: '负载测控、隔离保护与检修设备构件' for s in STATES}
ROLES.update({material.IWV: '弧幕测控脊、六路负载廊及调度厅主体',
    material.CONTROL: '前端调度厅居中主控预览标记', material.PORT: '嵌入设备外墙的接口占位，无实际仓室功能',
    material.INSULATE: '各路测控分隔与母线绝缘层', material.COMPUTER: '个人账本投影读数、授权核验和回执记录机柜',
    material.ROBUST: '弧幕承力肋、落地检修架和母线分段框', material.POWER: '负载供能状态测量及保护机匣',
    material.GRATE: '调度廊的检修环梁和可达维护层', material.TUNG_PIPE: '分路测量与介质服务线路',
    material.GOLD: '少量校准触点', material.OBSIDIAN: '读数标定用黑体片',
    material.GLASS: '母线屏蔽观察窗口', material.LAMINATED: '调度大厅连续观察带',
    material.FUSION_GLASS: '上层隔离测量观察孔', material.PLASCRETE: '六路条形设备基础和后部承重基础'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(a, b, state):
        x, y, z = a; X, Y, Z = b
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (a, b)
        cube[y:Y+1, z:Z+1, x:X+1] = IDS[state] if state else 0

    def shell(a, b, state, t=3):
        box(a, b, state)
        if all(b[k]-a[k]+1 > t*2 for k in range(3)):
            box(tuple(v+t for v in a), tuple(v-t for v in b), None)

    def beam(a, b, state, r=2):
        n = max(abs(a[k]-b[k]) for k in range(3))
        for i in range(n+1):
            p = [round(a[k]+(b[k]-a[k])*i/max(1, n)) for k in range(3)]
            box(tuple(max(0, v-r) for v in p), tuple(min(s-1, v+r) for v, s in zip(p, (W, H, D))), state)

    zones, routes = [], []
    # 后部弧幕：主体的曲面屏蔽、分层测控设备与检修空间同时确定高度。
    for x in range(W):
        top = round(138+146*(1-((x-CX)/CX)**2))
        for z in (319, 365, 411, 457):
            box((x, 0, z), (x, 9, min(D-1, z+13)), material.PLASCRETE)
            box((x, 10, z), (x, top, min(D-1, z+1)), material.IWV)
        # 弧顶是实际连续母线屏蔽槽，四幕通过端板和层板连为一体。
        box((x, top-3, 319), (x, top, 470), material.IWV)
        box((x, top-2, 328), (x, top-1, 462), material.INSULATE)
        for y in range(26, top-15, 28):
            box((x, y, 320), (x, y, 468), material.IWV)
    for x in range(0, W, 33):
        X = min(x+8, W-1)
        top = min(round(138+146*(1-((v-CX)/CX)**2)) for v in (x, X))
        box((x, 0, 315), (X, top-1, 324), material.ROBUST)
        box((x, 0, 461), (X, top-1, 470), material.ROBUST)
        for y in range(40, top-18, 28):
            box((x, y, 312), (X, y+2, 468), material.GRATE)
    # 每层都有独立的保护机匣、测量内衬与维护间隔，避免实心整块堆料。
    for x in range(12, W-23, 33):
        top = min(round(138+146*(1-((v-CX)/CX)**2)) for v in (x, x+23))
        for z in (331, 377, 423):
            for y in range(20, top-30, 28):
                shell((x, y, z), (x+23, y+23, z+30), material.IWV, 2)
                shell((x+5, y+1, z+6), (x+18, y+17, z+24), material.POWER, 2)
                box((x+6, y+16, z+3), (x+17, y+20, z+7), material.COMPUTER)
        for y in range(32, top-34, 28):
            box((x+3, y, 319), (x+18, y+6, 321), material.GLASS)
    # 六条测控支线朝前扇形展开；每条由入口窄端渐扩为独立负载泊位。
    fronts = (45, 145, 245, 345, 445, 545)
    rears = (130, 196, 262, 328, 394, 460)
    for branch, (front, rear) in enumerate(zip(fronts, rears)):
        def center(z):
            return round(front+(rear-front)*(z-30)/284)
        for z in range(28, 315):
            cx = center(z); t = (z-28)/286
            radius = round(43-17*t)
            top = round(55+65*t)
            box((cx-radius, 0, z), (cx+radius, 5, z), material.PLASCRETE)
            box((cx-radius, 6, z), (cx+radius, 11, z), material.IWV)
            for x in (cx-radius, cx+radius-3):
                box((x, 12, z), (x+3, top, z), material.IWV)
            box((cx-radius, top-4, z), (cx+radius, top, z), material.IWV)
            # 三层服务母线沿真实支线延伸；路由终点接入后部弧幕。
            for dx in (-radius+8, radius-8):
                box((cx+dx-2, 14, z), (cx+dx+2, 19, z), material.TUNG_PIPE)
        for z in range(35, 305, 27):
            cx = center(z); radius = round(43-17*((z-28)/286)); top=round(55+65*((z-28)/286))
            box((cx-radius-2, 6, z), (cx+radius+2, 12, z+5), material.ROBUST)
            box((cx-radius-2, top-4, z), (cx+radius+2, top+4, z+5), material.ROBUST)
            for x in (cx-radius-2, cx+radius-2):
                box((x, 12, z), (x+4, top, z+5), material.IWV)
            # 负载监测机架在中间留出人员通道，横梁与顶部有实体支承。
            for sign in (-1, 1):
                x0 = cx-radius+5 if sign<0 else cx+8
                x1 = cx-8 if sign<0 else cx+radius-5
                shell((x0, 20, z+6), (x1, top-8, z+23), material.IWV, 2)
                shell((x0+3, 21, z+9), (x1-3, top-13, z+19), material.ATOMIC if branch%2==0 else material.INSULATE, 2)
                box((x0+2, top-14, z+7), (x1-2, top-10, z+9), material.COMPUTER)
            box((cx-radius+5, top+1, z+9), (cx+radius-5, top+4, z+14), material.LAMINATED)
            for dx in (-radius+2, radius-3):
                box((cx+dx, 30, z+9), (cx+dx+1, 41, z+19), material.BLACK_GLASS)
                box((cx+dx, 10, z+9), (cx+dx+1, 29, z+10), material.IWV)
                box((min(cx,cx+dx), 10, z+9), (max(cx,cx+dx)+1, 11, z+10), material.IWV)
        # 泊位末端的保护联锁机匣；它们只表达授权负载状态，不是免费电源。
        cx = center(285)
        shell((cx-24, 10, 280), (cx+24, 142, 316), material.IWV, 5)
        box((cx-18, 44, 280), (cx+18, 80, 282), material.BLUE_GLASS)
        for dx in (-19, 15):
            box((cx+dx, 12, 286), (cx+dx+4, 130, 312), material.CLEAN)
        beam((cx, 137, 297), (rear, 170, 338), material.TUNG_PIPE, 3)
        zones.append(dict(name=f'第{branch+1}路授权负载测控廊', pos=[front, 8, 30]))
        routes.append((front, rear))
    # 前侧调度大厅与中轴检修廊是真实使用空间，控制器直接嵌入大厅外墙。
    shell((188, 6, 0), (402, 76, 67), material.IWV, 4)
    box((194, 41, 0), (396, 56, 0), material.LAMINATED)
    box((CX-19, 17, 0), (CX+19, 37, 4), material.IWV)
    for x in range(202, 391, 24):
        box((x, 10, 9), (x+12, 33, 24), material.COMPUTER)
        box((x+3, 27, 7), (x+9, 34, 10), material.GLASS)
    for z in (0, 64):
        box((188, 6, z), (402, 12, min(67,z+3)), material.ROBUST)
    # 中轴服务脊接至后场大厅，维护通路与授权数据各有连续端点。
    box((CX-8, 0, 65), (CX+8, 12, 328), material.IWV)
    for x in (CX-8, CX+7):
        box((x, 13, 65), (x+1, 17, 327), material.GRATE)
    for z in range(80, 318, 25):
        box((CX-4, 12, z), (CX+4, 14, z+3), material.LIGHT)
    # 分层维护与介质设备按功能使用少量不同材料，避免七彩拼接。
    detail_states = [material.ASSEMBLY, material.LASER, material.TURBINE, material.MACERATOR,
        material.VENT, material.GEAR, material.STEEL_PIPE, material.IRIDIUM, material.PROCESS,
        material.DIMENSION, material.MULTI, material.LAFIUM, material.FILTER, material.INERT,
        material.HEATPROOF, material.FROST, material.STABLE, material.SOLID, material.INTAKE,
        material.STRESS, material.MIXING, material.VIBRATION, material.FUSION_GLASS,
        material.GOLD, material.IRON, material.OBSIDIAN]
    for i, state in enumerate(detail_states):
        x = 15+(i%17)*33; y=23+(i//17)*56
        box((x, y, 332), (x+14, y+11, 350), state)
        box((x+4, 20, 334), (x+10, y, 344), material.IWV)
    controller = [CX, 27, 0]
    ports = []
    for dx, label in ((-72,'I38合法入账记录'),(-48,'绑定人授权输入'),(-24,'已登记负载输入'),
                      (24,'授权调度回执'),(48,'告警与历史查询'),(72,'维护物资交接')):
        p=[CX+dx,27,0]; cube[p[1],p[2],p[0]]=IDS[material.PORT]
        ports.append(dict(id=label,pos=p,face='north',purpose='计划接口占位；正式能力需独立验收'))
    cube[27,0,CX]=IDS[material.CONTROL]
    zones += [dict(name='文明负载登记与手动调度大厅',pos=[CX,76,30]),
              dict(name='弧幕母线与分层授权测控机架',pos=[CX,284,365])]
    data=dict(key='i41',name=NAME,title=TITLE,size=[W,H,D],controller=controller,controller_face='north',
        ports=ports,paths=[],zones=zones,target_voltage='IWV',
        description='连续抛物弧顶的四层母线屏蔽幕形成后部调度主脊，六条测控廊向前扇形展开；廊内保护机架、回执记录和检修空间分层组织。前置低位调度厅沿整宽中轴嵌入主控，以IWV机壳统一主体，绝缘隔板、灰银承力肋及少量观察窗建立设备层次。',
        construction_notes=dict(orientation='主控北向/-Z；蓝图从0起算；X=295为整宽第296格。',
            anchor='结构底部建议世界Y=-60，最高实体Y=224；Schematic Offset并非绝对世界坐标。',
            boundary='I41只负责获授权的文明负载登记、查看与调度回执；不制造能源，不替代I01-4采集或I38整流记账。',
            approval='独立待审候选；未批准、未实装。'))
    return cube,data


if __name__=='__main__':
    cube,data=build(); counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    print(dict(blocks=int(counts[1:].sum()),materials=int((counts[1:]>0).sum()),
        iwv=int(counts[IDS[material.IWV]]),unused=[s for s in STATES if not counts[IDS[s]]],
        size_xyz=data['size'],volume=math.prod(data['size'])))
