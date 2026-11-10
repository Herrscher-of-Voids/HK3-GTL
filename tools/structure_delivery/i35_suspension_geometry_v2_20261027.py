# -*- coding: utf-8 -*-
"""I35 V2悬索界桥：桥塔、连续主缆和轴向锚桩阵列，从空白建立几何。"""
import math
from pathlib import Path

import numpy as np


class Material:
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


material = Material()

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 401, 251, 701
CX = 200
NAME = 'hk3gtl-i35-suspension-anchor-v2-20261027'
TITLE = '虚数空间锚定阵列 · 悬索界桥'
STATES = sorted(value for name, value in vars(Material).items() if name.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = {state: '端部锚室内的标定、负载复验或稳定介质设备' for state in STATES}
ROLES.update({material.IRV: '桥塔、纵向箱梁和端部锚碇的主体IRV机壳',
    material.ROBUST: '主缆、吊杆、桥桁及锚碇连续承力骨架',
    material.CLEAN: '桥塔护棱、索鞍、检修廊及锚桩防护边',
    material.STRESS: '箱梁端部节点与主缆锚固接点',
    material.ASSEMBLY: '桥面设备轨道和锚室检修层楼板',
    material.GRATE: '桥上步行检修廊', material.GLASS: '桥头锚室内观察窗',
    material.BLACK_GLASS: '锚室遮光读出窗口', material.BLUE_GLASS: '锚桩工作态与缆索测距的窄导光槽',
    material.CONTROL: '北端锚室整宽中线主控标记', material.PORT: '实际锚室外壳内嵌接口占位',
    material.LIGHT: '端部锚室与桥面维护照明', material.BLACK: '轴向空间基准槽遮光衬层',
    material.GOLD: '小量精密标定接点', material.PLASCRETE: '独立桥墩与锚碇接地承台'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = 0 if state is None else IDS[state]

    def shell(lo, hi, state, t=5):
        box(lo, hi, state)
        if all(hi[i] - lo[i] >= 2 * t for i in range(3)):
            box(tuple(v + t for v in lo), tuple(v - t for v in hi), None)

    def beam(a, b, state, r):
        steps = max(abs(a[i] - b[i]) for i in range(3))
        for k in range(steps + 1):
            p = tuple(round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3))
            box(tuple(v - r for v in p), tuple(v + r for v in p), state)

    # 两端空腔锚碇承担主缆拉力；中间没有连续地台。
    for z0 in (0, 603):
        shell((0, 0, z0), (400, 78, z0 + 97), material.IRV, 9)
        for z in range(z0 + 12, z0 + 91, 26):
            box((8, 8, z), (392, 69, z + 5), material.IRV)
        for x in range(22, 380, 44):
            box((x, 9, z0 + 9), (x + 7, 69, z0 + 88), material.IRV)
        box((4, 37, z0 + 4), (396, 44, z0 + 93), material.ASSEMBLY)
        box((0, 0, z0), (400, 5, z0 + 97), material.PLASCRETE)
        box((0, 74, z0), (400, 78, z0 + 97), material.CLEAN)
        # 观察带与实墙交错，不用玻璃覆盖整个桥头。
        for x in range(14, 382, 46):
            for face_z in (z0, z0 + 97):
                box((x, 20, face_z), (x + 29, 31, face_z), material.GLASS)
                box((x, 51, face_z), (x + 29, 61, face_z), material.VENT)
        for x in (79, 297):
            shell((x, 64, z0 + 14), (x + 24, 111, z0 + 83), material.IRV, 5)
            box((x - 3, 108, z0 + 10), (x + 27, 115, z0 + 87), material.STRESS)

    # 一对可检修的纵向封闭箱梁，顶层是窄轨道、内层承受弯矩。
    for x in (106, 263):
        shell((x, 66, 38), (x + 31, 112, 662), material.IRV, 7)
        box((x - 3, 64, 38), (x + 34, 68, 662), material.ROBUST)
        box((x - 3, 111, 38), (x + 34, 115, 662), material.CLEAN)
        for z in range(104, 620, 43):
            box((x, 70, z), (x + 31, 108, z + 5), material.IRV)
    # 桥面与下层横隔梁，各有真实结构用途，桥下大部分空间保持贯通。
    box((92, 86, 32), (308, 97, 668), material.IRV)
    box((92, 98, 32), (308, 100, 668), material.ASSEMBLY)
    for z in range(100, 637, 38):
        box((88, 70, z), (312, 85, z + 10), material.IRV)
        box((88, 68, z), (312, 71, z + 10), material.ROBUST)
    for x in (95, 301):
        box((x, 101, 36), (x + 5, 105, 664), material.GRATE)
        box((x, 106, 36), (x + 5, 107, 664), material.CLEAN)
    # 中轴只保留连续标定轨与低密度导光，阵列不是抓取单个中央物件。
    box((192, 98, 45), (208, 100, 655), material.BLACK)
    box((198, 101, 45), (202, 102, 655), material.BLUE_GLASS)

    # 两座连续门式索塔，双塔站位沿桥轴展开，索鞍负责实际主缆转向。
    for z in (175, 525):
        for y in range(H):
            inset = min(15, y // 15)
            for x in (67 + inset, 301 - inset):
                box((x, y, z - 24), (x + 32, y, z + 24), material.IRV)
                if 8 < y < 236:
                    box((x + 9, y, z - 15), (x + 23, y, z + 15), None)
                box((x, y, z - 24), (x + 3, y, z - 21), material.CLEAN)
                box((x + 29, y, z - 24), (x + 32, y, z - 21), material.CLEAN)
        for y in (76, 141, 238):
            box((74, y, z - 22), (326, min(250, y + 12), z + 22), material.IRV)
            box((74, y, z - 23), (326, y + 2, z - 20), material.CLEAN)
        for x in (56, 284):
            box((x, 0, z - 35), (x + 60, 12, z + 35), material.PLASCRETE)
        for x in (89, 311):
            box((x - 12, 233, z - 30), (x + 12, 246, z + 30), material.GEAR)

    def cable_y(z):
        if z < 175:
            t = (z - 42) / 133
            return 109 + 131 * t
        if z > 525:
            t = (658 - z) / 133
            return 109 + 131 * t
        return 137 + 103 * ((z - 350) / 175) ** 2

    # 主缆跨过索鞍后直接落入两端锚碇，成排吊杆连接桥桁。
    for x in (89, 311):
        last = None
        for z in range(42, 659):
            point = (x, round(cable_y(z)), z)
            if last: beam(last, point, material.ROBUST, 5)
            last = point
        for z in range(103, 616, 24):
            y = round(cable_y(z))
            box((x - 2, 100, z - 2), (x + 2, y, z + 2), material.CLEAN)
            box((x - 5, 97, z - 5), (x + 5, 104, z + 5), material.STRESS)
        for z in (42, 658):
            box((x - 14, 75, z - 16), (x + 14, 113, z + 16), material.IRV)
            box((x - 17, 109, z - 18), (x + 17, 117, z + 18), material.STRESS)

    # 九个工作锚桩沿轴线成排分布，由桥梁上的工装逐段标定与加载。
    xx, zz = np.mgrid[:W, :D]
    for z in range(126, 595, 58):
        for y in range(0, 87):
            r = 11 if y < 18 else 18 if y < 65 else 25
            mask = (abs(xx - CX) + abs(zz - z) <= r * 1.45) & (abs(xx - CX) <= r) & (abs(zz - z) <= r)
            cube[y, mask.T] = IDS[material.IRV]
            if y in (18, 19, 58, 59, 76, 77):
                cube[y, mask.T] = IDS[material.CLEAN]
        box((CX - 2, 20, z - 19), (CX + 2, 56, z - 19), material.BLUE_GLASS)
        box((CX - 29, 80, z - 27), (CX + 29, 85, z + 27), material.GEAR)
        for x in (CX - 28, CX + 19):
            box((x, 101, z - 10), (x + 9, 108, z + 10), material.DIMENSION)

    # 端部锚室容纳工艺设备，专用材质以小量、有用途的装置使用。
    equipment = [s for s in STATES if s not in (material.IRV, material.ROBUST, material.CLEAN,
        material.ASSEMBLY, material.STRESS, material.GLASS, material.BLACK_GLASS, material.BLUE_GLASS,
        material.GRATE, material.BLACK, material.PLASCRETE, material.GEAR, material.PORT, material.CONTROL)]
    for i, state in enumerate(equipment):
        local = i % 15
        x = 25 + (local % 5) * 34; y = 11 if i < 15 else 47
        z = 19 + (local // 5) * 25
        for X in (x, W - 1 - x):
            for Z in (z, D - 1 - z):
                box((X - 8, y - 3, Z - 8), (X + 8, y - 1, Z + 8), material.IRV)
                box((X - 7, y, Z - 7), (X + 7, y + 14, Z + 7), state)
    box((CX - 31, 52, 0), (CX + 31, 61, 0), material.BLACK_GLASS)
    # 中线主控在北锚碇的连续外壳内，接口按物料/资料/冷却分区。
    controller = [CX, 28, 8]
    ports = [dict(id='魂钢锚件输入', pos=[CX - 48, 28, 8], face='north'),
        dict(id='空间核心组件输入', pos=[CX + 48, 28, 8], face='north'),
        dict(id='I34校准资料输入', pos=[CX - 72, 28, 8], face='north'),
        dict(id='锚定验证资料输入', pos=[CX + 72, 28, 8], face='north'),
        dict(id='西侧锚定供能', pos=[0, 28, 56], face='west'),
        dict(id='东侧锚定供能', pos=[400, 28, 56], face='east'),
        dict(id='西侧稳定介质', pos=[0, 28, 645], face='west'),
        dict(id='东侧介质回流', pos=[400, 28, 645], face='east'),
        dict(id='合格锚定组件输出', pos=[CX - 48, 28, 692], face='south'),
        dict(id='锚定状态与记录输出', pos=[CX + 48, 28, 692], face='south')]
    # 前后锚室立面在内退八格处形成真实检修通廊，端口没有独立托板。
    for z in (8, 692):
        box((111, 12, z if z == 8 else z - 8), (289, 36, z + 8 if z == 8 else z), material.IRV)
        box((114, 37, z), (286, 39, z), material.LIGHT)
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；真实仓室能力另验'
    paths = [dict(name='北锚室主控通廊', min=[112, 25, 0], max=[288, 31, 7]),
        dict(name='南锚室输出通廊', min=[112, 25, 693], max=[288, 31, 700])]
    for p in paths: box(p['min'], p['max'], None)
    # 成对装置与主结构严格镜像，主控/接口语义不同而材质相同。
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data = dict(key='i35', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports, paths=paths,
        zones=[dict(name='北端主缆锚碇与标定室', pos=[CX, 78, 36]),
            dict(name='前站连续门式索塔', pos=[CX, 245, 175]),
            dict(name='连续主缆与垂直吊杆', pos=[89, 137, 350]),
            dict(name='轴向沉降锚桩阵列', pos=[CX, 40, 358]),
            dict(name='南端锚碇与物料证据交付', pos=[CX, 78, 660])],
        description='两端锚碇将主缆拉力传入独立承台，纵向双索塔与悬链主缆托起连续箱梁。九个沉降锚桩沿桥轴分布，构成逐段标定和负载复验阵列；桥下留出贯通空间，实体设备收进两端锚室。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图坐标从0起算。', anchor='推荐世界Y=-60，最高实体Y=190。',
            boundary='阵列表达组件标定、稳定工况与负载复验，不提供传送、免费实物或维度通行。',
            approval='V1已被负责人否决；本V2为独立待审候选，未接入实例。'))
    return cube, data
