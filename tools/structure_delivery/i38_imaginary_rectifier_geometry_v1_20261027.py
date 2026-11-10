# -*- coding: utf-8 -*-
"""I38双极脉冲换流站：开放阀列、分段母线与前端合法结算控制室。"""
# 【变更记录 #1】2026-10-27（本轮候选，实际生成时间见交付manifest）
# 删除：无。新增：独立换流站几何与逐格状态。修改：不沿用既有围院/球体造型。
# 用途：表达HKE整流设备及合法记账边界；不接入运行逻辑或实例。
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 561, 283, 501, 280
NAME = 'hk3gtl-i38-imaginary-rectifier-v1-20261027'
TITLE = '虚数能量整流中枢 · 双极脉冲换流站'


class Material:
    IWV = 'hk3gtl:voltage_machine_casing_iwv'
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
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = {state: '换流阀底部的独立辅助保护与介质处理器件' for state in STATES}
ROLES.update({material.IWV: '十二组串联换流阀架、模块托盘与变压设备主体',
    material.INSULATE: '逐级阀模块之间的绝缘隔盘与母线支柱',
    material.ROBUST: '阀列承力支柱、阀架端梁及设备地梁',
    material.CLEAN: '阀模块护边、检修门与变压器压盖',
    material.POWER: '分级换流功率芯及前端输入变压机组',
    material.TUNG_PIPE: '分段高压母线与两极汇流端',
    material.STEEL_PIPE: '设备间冷却介质供回管廊',
    material.VENT: '变压机组散热片与后部排热百叶',
    material.GRATE: '地面维护栈道与阀列检查平台',
    material.PLASCRETE: '各设备分离的浅承台，不铺满场地',
    material.COMPUTER: '前端整流调节、合法结算与状态监测机柜',
    material.FILTER: '输入能流的边界过滤与异常隔离单元',
    material.DIMENSION: '虚数能流边界耦合端子，不承担维度传送',
    material.BLUE_GLASS: '少量阀模块状态读数条',
    material.GLASS: '控制室观察窗与冷却介质读数窗',
    material.BLACK_GLASS: '控制室遮光读数窗',
    material.GOLD: '分级阀触点及校准接点',
    material.LIGHT: '设备检修照明和连续小幅状态灯',
    material.PORT: '连续控制室墙体中齐平工业接口占位',
    material.CONTROL: '前端控制室中轴主控标记'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(lo, hi, state, t=2):
        box(lo, hi, state)
        if all(hi[i] - lo[i] + 1 > 2 * t for i in range(3)):
            box(tuple(v + t for v in lo), tuple(v - t for v in hi), None)

    def beam(a, b, state, r=1):
        count = max(abs(a[i] - b[i]) for i in range(3))
        for n in range(count + 1):
            p = [round(a[i] + (b[i] - a[i]) * n / max(1, count)) for i in range(3)]
            box(tuple(max(0, v - r) for v in p),
                tuple(min(s - 1, v + r) for v, s in zip(p, (W, H, D))), state)

    # 双极阀列分置中央检修大道两边，浅承台及连接栈道替代大底座。
    for x in (84, 189, 371, 476):
        box((x - 41, 0, 122), (x + 41, 8, 462), material.PLASCRETE)
        box((x - 39, 9, 122), (x + 39, 12, 462), material.IWV)
        for dx in (-38, 35):
            box((x + dx, 13, 123), (x + dx + 3, 15, 461), material.GRATE)
    box((43, 0, 105), (517, 5, 121), material.PLASCRETE)
    box((43, 6, 106), (517, 8, 119), material.GRATE)
    box((43, 0, 462), (517, 5, 479), material.PLASCRETE)
    box((43, 6, 463), (517, 8, 477), material.GRATE)
    for x in (233, 316):
        box((x, 0, 81), (x + 11, 4, 478), material.PLASCRETE)
        box((x, 5, 88), (x + 11, 7, 478), material.ASSEMBLY)
    # 每座阀塔由31层薄托盘和空心阀室组成，真实串联高度构成主轮廓。
    centers = [(x, z) for x in (84, 189, 371, 476) for z in (169, 289, 409)]
    for x, z in centers:
        box((x - 37, 13, z - 37), (x + 37, 18, z + 37), material.VIBRATION)
        box((x - 34, 19, z - 34), (x + 34, 21, z + 34), material.STRESS)
        for level in range(31):
            y = 22 + level * 8
            box((x - 35, y, z - 35), (x + 35, y, z + 35), material.IWV)
            box((x - 33, y + 1, z - 33), (x + 33, y + 6, z + 33), material.IWV)
            box((x - 31, y + 1, z - 31), (x + 31, y + 6, z + 31), None)
            box((x - 35, y + 7, z - 35), (x + 35, y + 7, z + 35), material.INSULATE)
            # 独立功率芯与冷却导流槽位于阀室内部，避免实心填满模块。
            for dx in (-19, 10):
                box((x + dx, y + 3, z - 25), (x + dx + 9, y + 6, z + 25), material.POWER)
            if level % 4 == 1:
                box((x - 25, y + 3, z - 34), (x + 25, y + 4, z - 34), material.BLUE_GLASS)
                box((x - 24, y + 4, z - 33), (x + 24, y + 4, z - 33), material.GOLD)
        for dx in (-32, 29):
            for dz in (-32, 29):
                box((x + dx, 19, z + dz), (x + dx + 3, 273, z + dz + 3), material.ROBUST)
        box((x - 37, 270, z - 37), (x + 37, 274, z + 37), material.IWV)
        box((x - 39, 275, z - 12), (x + 39, 279, z + 12), material.TUNG_PIPE)
        # 阀列背面竖向冷却管与底部巡检护边相连。
        box((x - 5, 16, z + 36), (x + 5, 271, z + 40), material.STEEL_PIPE)
        box((x - 38, 13, z + 35), (x + 38, 16, z + 42), material.IWV)
        for y in (47, 111, 175, 239):
            box((x - 38, y, z - 38), (x + 38, y + 2, z - 33), material.CLEAN)
    # 两条分段主母线在阀塔顶梁上落座，分极不交叉，最高点是汇流端而非补塔。
    for x in (136, 424):
        for z in (169, 289, 409):
            for xx in (x - 52, x + 53):
                box((min(xx, x), 275, z - 4), (max(xx, x), 282, z + 4), material.TUNG_PIPE)
        box((x - 4, 275, 151), (x + 4, 282, 449), material.TUNG_PIPE)
        for z in (214, 334):
            shell((x - 8, 270, z - 12), (x + 8, 282, z + 12), material.INSULATE, 2)
        # 低位极性汇流屏与长母线竖向落地端共同承载输入连接。
        box((x - 6, 32, 145), (x + 6, 275, 153), material.TUNG_PIPE)
        for y in range(44, 249, 16):
            box((x - 12, y, 139), (x + 12, y + 2, 159), material.INSULATE)
        box((x - 18, 9, 131), (x + 18, 32, 162), material.IWV)
    # 前端两座输入变压机组使用散热片、瓷柱和箱式绕组形成独立工程识别。
    for x in (106, 454):
        box((x - 65, 0, 12), (x + 65, 8, 105), material.PLASCRETE)
        box((x - 54, 9, 20), (x + 54, 14, 100), material.ROBUST)
        shell((x - 47, 15, 25), (x + 47, 93, 94), material.IWV, 3)
        box((x - 51, 94, 22), (x + 51, 97, 97), material.CLEAN)
        for dx in (-34, 0, 34):
            box((x + dx - 6, 98, 44), (x + dx + 6, 126, 57), material.INSULATE)
            for y in (101, 109, 117):
                box((x + dx - 11, y, 39), (x + dx + 11, y + 2, 62), material.CLEAN)
            box((x + dx - 5, 127, 45), (x + dx + 5, 130, 55), material.GOLD)
        for dx in (-63, 51):
            for z in range(28, 94, 5):
                box((x + dx, 17, z), (x + dx + 12, 84, z + 1), material.VENT)
            box((x + dx, 14, 24), (x + dx + 12, 23, 96), material.STEEL_PIPE)
        # 绕组读数侧窗与前端油枕，普通材料不取代本阶主壳。
        box((x - 24, 45, 24), (x + 24, 67, 24), material.BLACK)
        box((x - 21, 48, 24), (x + 21, 64, 24), material.GLASS)
        shell((x - 38, 72, 78), (x + 38, 105, 105), material.IWV, 2)
        box((x - 38, 84, 105), (x + 38, 94, 110), material.POWER)
        box((min(x, 136 if x < CX else 424) - 5, 27, 100),
            (max(x, 136 if x < CX else 424) + 5, 34, 145), material.TUNG_PIPE)
    # 西东侧绝缘出线和相连承台定义真实宽度，不用孤立标记拉大边界。
    for x in (0, 536):
        box((x, 0, 107), (x + 24, 7, 124), material.PLASCRETE)
        box((x, 8, 111), (x + 24, 20, 120), material.IWV)
    box((0, 21, 112), (560, 25, 118), material.INSULATE)
    box((0, 26, 113), (560, 30, 117), material.TUNG_PIPE)
    # 后部仅一列低矮冷却设备，纵向维护管廊实际连接每座阀塔。
    shell((39, 0, 477), (521, 48, 500), material.IWV, 2)
    box((39, 0, 477), (521, 6, 500), material.PLASCRETE)
    for x in range(51, 501, 25):
        box((x, 16, 498), (x + 13, 39, 500), material.VENT)
        box((x + 2, 46, 480), (x + 11, 49, 497), material.INTAKE)
    for x in (84, 189, 371, 476):
        box((x - 5, 10, 125), (x + 5, 15, 480), material.FROST)
    # 前端控制室是统一墙体，主控与接口不外接面板；中央大道通向其后门。
    shell((210, 0, 0), (350, 60, 88), material.IWV, 2)
    box((210, 0, 0), (350, 5, 88), material.PLASCRETE)
    box((210, 59, 0), (350, 62, 88), material.CLEAN)
    box((215, 63, 8), (345, 64, 81), material.COMPUTER)
    box((219, 65, 10), (341, 65, 15), material.LIGHT)
    box((232, 35, 0), (328, 51, 0), material.BLACK)
    box((237, 38, 0), (323, 48, 0), material.BLACK_GLASS)
    for x in (210, 350):
        box((x, 30, 16), (x, 48, 72), material.GLASS)
    # 将器件材料按功能分配为短小可检修单元，连接同一控制室底板。
    equipment = [s for s in STATES if s not in {material.IWV, material.PORT, material.CONTROL,
        material.ROBUST, material.CLEAN, material.INSULATE, material.POWER, material.TUNG_PIPE,
        material.STEEL_PIPE, material.VENT, material.GRATE, material.PLASCRETE, material.VIBRATION,
        material.STRESS, material.BLUE_GLASS, material.GOLD, material.GLASS, material.BLACK,
        material.BLACK_GLASS, material.FROST, material.INTAKE, material.COMPUTER, material.LIGHT,
        material.ASSEMBLY}]
    for i, state in enumerate(equipment):
        z = 12 + (i % 6) * 11
        y = 8 + (i // 6) * 14
        for x in (221, 331):
            box((x - 3, y - 2, z - 3), (x + 3, y - 1, z + 3), material.ASSEMBLY)
            box((x - 3, y, z - 3), (x + 3, y + 7, z + 3), state)
    for x in (218, 338):
        box((x, 6, 8), (x + 4, 52, 79), material.ROBUST)
    controller = [CX, 20, 0]
    ports = [dict(id='西侧能量态崩坏能输入', pos=[224, 20, 0], face='north'),
        dict(id='东侧能量态崩坏能输入', pos=[336, 20, 0], face='north'),
        dict(id='稳定介质供给', pos=[238, 20, 0], face='north'),
        dict(id='用后介质回流', pos=[322, 20, 0], face='north'),
        dict(id='整流参数与来源凭据输入', pos=[252, 20, 0], face='north'),
        dict(id='合法记账与测量记录输出', pos=[308, 20, 0], face='north'),
        dict(id='西侧已整流HKE交付', pos=[266, 20, 0], face='north'),
        dict(id='东侧已整流HKE交付', pos=[294, 20, 0], face='north'),
        dict(id='辅助供能西端', pos=[210, 20, 42], face='west'),
        dict(id='辅助供能东端', pos=[350, 20, 42], face='east')]
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；正式能力、供能合同与合法记账另验'
    # 同材质镜像锁定双极场区的几何中轴，不通过复制旧机器获得造型。
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data = dict(key='i38', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='中央检修大道', min=[250, 8, 123], max=[310, 32, 461])],
        zones=[dict(name='双极串联换流阀列', pos=[49, 262, 169]),
            dict(name='顶置分段脉冲母线', pos=[136, 282, 289]),
            dict(name='输入变压与绝缘出线', pos=[106, 94, 50]),
            dict(name='后部低位排热机列', pos=[280, 48, 486]),
            dict(name='前端整流与合法结算控制室', pos=[280, 60, 40])],
        description='两极各由六座串联换流阀塔组成，薄托盘、空心阀室、分级绝缘盘和背面冷却立管把高度组织成真实换流层级。高位分段脉冲母线沿两条阀列汇流，前端变压机组与后端低位排热机列围绕中央维护大道分工；整流调节和合法记账控制室位于前方中轴，不设围院、大底座或抓取中央物件的四爪。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图从0起算；X=280为第281格。',
            anchor='推荐世界Y=-60，最高实体Y=222；Schematic Offset为局部坐标，不是世界粘贴位置。',
            boundary='只表达HKE整流与合法记账设备；不采集能量，不发放免费HKE，不代替I41文明负载调度。',
            approval='I38 V1为独立待审建筑候选，未获批准、未实装；结构完成后再做双平台性能验收。'))
    return cube, data

