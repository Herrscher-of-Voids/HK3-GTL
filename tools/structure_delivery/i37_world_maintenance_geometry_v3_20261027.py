# -*- coding: utf-8 -*-
"""I37恒界精密试验机：封闭工作舱、计量龙门与一体化工况机柜。"""
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 461, 291, 781, 230
NAME = 'hk3gtl-i37-world-maintenance-v3-20261027'
TITLE = '世界维系试验平台 · 恒界精密试验机'


class Material:
    WFV = 'hk3gtl:voltage_machine_casing_wfv'
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
    COPPER = 'minecraft:copper_block'
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {state: '后部工况机柜内的样件标定、供能、介质处理与温度控制单元' for state in STATES}
ROLES.update({material.WFV: '隔振床身、封闭试验舱及前后工况机身主体',
    material.ROBUST: '床身承力横梁、龙门计量柱与滑台导轨',
    material.CLEAN: '可拆检修盖板、洁净内壁及机舱封边',
    material.ASSEMBLY: '样件交换轨及移动工作台', material.STRESS: '隔振床身承座与龙门受力节点',
    material.GEAR: '滑台丝杠及夹具驱动仓', material.VENT: '后部工况机柜热交换窗口',
    material.GRATE: '舱内纵向检修踏道', material.GLASS: '侧门观察窗与正面试验观察窗',
    material.BLUE_GLASS: '计量头窄幅观测指示带', material.BLACK: '舱窗垫框及试验区遮光内衬',
    material.IRON: '可更换精密试样夹具', material.OBSIDIAN: '局部扰动试件隔离夹座',
    material.PORT: '机身连续外壳内的工业接口占位', material.CONTROL: '正面居中主控标记',
    material.PLASCRETE: '整体床身下的短隔振承座', material.GOLD: '计量基准的少量标定触点',
    material.COPPER: '前端测控柜内的少量接地母排触点，与金色标定点分别承担电连接及计量用途',
    material.COMPUTER: '前端测控与后端试验记录机柜', material.LIGHT: '工作舱照明与检修状态细灯带'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(lo, hi, state, thickness):
        box(lo, hi, state)
        box(tuple(v + thickness for v in lo), tuple(v - thickness for v in hi), None)

    # 箱式隔振床身承接全机，内部留腔并以横隔梁分担工作舱荷载。
    shell((14, 0, 14), (446, 61, 766), material.WFV, 3)
    for z in range(52, 746, 86):
        box((25, 11, z), (435, 50, z + 3), material.WFV)
    for x in (60, 181, 272, 393):
        shell((x, 12, 26), (x + 7, 48, 754), material.ROBUST, 2)
    for x in (36, 374):
        for z in (36, 247, 458, 704):
            box((x, 0, z), (x + 51, 14, z + 42), material.PLASCRETE)
            box((x + 5, 15, z + 4), (x + 46, 20, z + 38), material.STRESS)

    # 中央封闭压力舱高于两侧交换舱，承力柱与横梁把三段接成一台设备。
    shell((0, 47, 166), (460, 179, 585), material.WFV, 4)
    shell((48, 166, 166), (412, 290, 585), material.WFV, 4)
    for z in (205, 370, 535):
        for x in (4, 408):
            box((x, 158, z), (x + 48, 174, z + 5), material.ROBUST)
    shell((46, 0, 0), (414, 173, 165), material.WFV, 4)
    shell((36, 48, 586), (424, 228, 780), material.WFV, 4)
    box((0, 59, 166), (460, 61, 585), material.CLEAN)
    box((36, 59, 586), (424, 61, 780), material.WFV)
    # 前后设备腔与主工作舱以实体床身、轨道和隔离壁衔接。
    box((170, 50, 154), (290, 121, 185), material.WFV)
    box((170, 50, 568), (290, 121, 605), material.WFV)
    box((181, 66, 154), (279, 109, 185), None)
    box((181, 66, 568), (279, 109, 605), None)
    # 外壳白色盖板按检修门分段，WFV仍构成连贯机身而非一圈点缀。
    for z in (183, 320, 457):
        for x in (60, 276):
            box((x, 289, z), (x + 124, 290, z + 2), material.CLEAN)
            box((x, 289, z + 108), (x + 124, 290, z + 110), material.CLEAN)
            box((x, 289, z), (x + 2, 290, z + 110), material.CLEAN)
            box((x + 122, 289, z), (x + 124, 290, z + 110), material.CLEAN)
            for xx in (x + 6, x + 30, x + 90, x + 122):
                box((xx, 283, z + 16), (xx + 3, 290, z + 92), material.WFV)
    for x in (0, 450):
        box((x, 71, 187), (x + 1, 94, 564), material.CLEAN)
        box((x, 237, 187), (x + 1, 262, 564), material.CLEAN)
        for z in (208, 332, 456):
            box((x, 103, z), (x + 1, 171, z + 111), material.CLEAN)
            box((x, 122, z + 9), (x + 1, 164, z + 102), material.BLACK)
            box((x, 128, z + 15), (x + 1, 158, z + 96), material.GLASS)
            # 齐平门把手与下方设备检修口。
            box((x, 107, z + 13), (x + 1, 114, z + 35), material.ROBUST)
            box((x, 55, z + 13), (x + 1, 67, z + 96), material.VENT)
    # 主舱正前及后端高位观察窗，低位为封闭样件交换通道。
    for z in (166, 581):
        box((92, 182, z), (368, 264, z + 1), material.CLEAN)
        box((103, 191, z), (357, 253, z + 1), material.BLACK)
        box((112, 198, z), (348, 246, z + 1), material.GLASS)
    # 前端短机头与可拆式白色交换仓盖，正面主控沿整宽中轴内退。
    for x in (67, 294):
        box((x, 56, 0), (x + 99, 145, 1), material.CLEAN)
        box((x + 10, 72, 0), (x + 89, 125, 1), material.BLACK)
        box((x + 16, 78, 0), (x + 83, 119, 1), material.GLASS)
        box((x + 12, 172, 22), (x + 87, 173, 145), material.CLEAN)
    box((176, 58, 0), (284, 150, 10), material.WFV)
    box((190, 70, 0), (270, 137, 10), material.COMPUTER)
    box((198, 77, 0), (262, 129, 4), material.BLACK_GLASS)
    box((180, 45, 0), (280, 49, 10), material.CLEAN)
    box((126, 15, 8), (334, 45, 13), material.WFV)
    box((126, 18, 0), (334, 42, 7), None)

    # 真正的两柱龙门位于机舱内部：横梁与导轨支承计量头和移动试样台。
    for x in (76, 349):
        shell((x, 62, 292), (x + 35, 251, 472), material.ROBUST, 3)
        box((x, 73, 304), (x + 4, 231, 460), material.CLEAN)
        box((x, 88, 322), (x + 4, 215, 445), material.WFV)
    shell((76, 232, 308), (384, 266, 458), material.WFV, 3)
    for z in (319, 435):
        box((76, 249, z), (384, 259, z + 10), material.ROBUST)
    box((187, 215, 330), (273, 247, 437), material.ASSEMBLY)
    shell((197, 151, 345), (263, 214, 421), material.ATOMIC, 3)
    box((206, 139, 356), (254, 155, 410), material.IRIDIUM)
    box((215, 128, 369), (245, 140, 397), material.BLUE_GLASS)
    for x in (119, 325):
        box((x, 62, 230), (x + 16, 82, 542), material.ROBUST)
        box((x + 4, 83, 230), (x + 12, 89, 542), material.STEEL_PIPE)
    shell((126, 89, 291), (334, 112, 482), material.ASSEMBLY, 4)
    box((140, 113, 305), (320, 120, 469), material.CLEAN)
    box((181, 121, 350), (279, 127, 424), material.OBSIDIAN)
    box((200, 128, 367), (260, 132, 407), material.IRON)
    for x in (154, 287):
        for z in (320, 438):
            box((x, 121, z), (x + 19, 131, z + 17), material.GEAR)
            box((x + 5, 132, z + 4), (x + 14, 135, z + 13), material.IRON)
    # 中央低位移载轨贯穿前后交换口；维护踏道在两侧连续可达。
    for x in (185, 264):
        box((x, 62, 23), (x + 11, 76, 726), material.ASSEMBLY)
    for x in (31, 411):
        box((x, 62, 196), (x + 18, 65, 562), material.GRATE)
    for x in (47, 397):
        for z in (205, 370, 535):
            box((x, 57, z), (x + 18, 61, z + 3), material.ROBUST)
        box((x, 59, 207), (x + 2, 61, 559), material.STEEL_PIPE)
    for x in (53, 399):
        box((x, 273, 198), (x + 8, 279, 557), material.LIGHT)
        for z in (208, 374, 540):
            box((x + 3, 280, z), (x + 5, 286, z + 2), material.ROBUST)
    for x in (144, 308):
        box((x, 121, 317), (x + 8, 124, 462), material.GOLD)

    # 后部成排工况机柜：供能、介质、回流和温控各有独立检修盖与散热面。
    for z in (598, 660, 722):
        for x in (36, 413):
            box((x, 73, z), (x + 1, 207, z + 47), material.CLEAN)
            box((x, 112, z + 7), (x + 1, 186, z + 40), material.VENT)
            box((x, 87, z + 8), (x + 1, 98, z + 39), material.WFV)
        box((62, 227, z), (398, 228, z + 45), material.CLEAN)
        for x in (90, 294):
            box((x, 227, z + 8), (x + 76, 228, z + 35), material.VENT)
    box((86, 66, 779), (374, 211, 780), material.CLEAN)
    for x in (101, 281):
        box((x, 95, 779), (x + 78, 182, 780), material.VENT)
    # 内部专用设备按用途分配，少量复杂材料不铺满整座机身。
    equipment = [s for s in STATES if s not in (material.WFV, material.PORT, material.CONTROL,
        material.ROBUST, material.CLEAN, material.ASSEMBLY, material.STRESS, material.GEAR,
        material.VENT, material.GRATE, material.GLASS, material.BLUE_GLASS, material.BLACK,
        material.BLACK_GLASS, material.IRON, material.OBSIDIAN, material.PLASCRETE,
        material.COMPUTER, material.LIGHT, material.GOLD, material.COPPER, material.ATOMIC, material.IRIDIUM, material.STEEL_PIPE)]
    for i, state in enumerate(equipment):
        z = 605 + (i % 5) * 30
        y = 80 + (i // 5) * 33
        for x in (115, 345):
            box((x - 18, y - 3, z - 10), (x + 18, y - 1, z + 13), material.WFV)
            shell((x - 16, y, z - 9), (x + 16, y + 20, z + 12), state, 1)
    for x in (87, 365):
        box((x, 62, 600), (x + 8, 176, 748), material.TUNG_PIPE)
    for x in (97, 130, 327, 360):
        box((x, 62, 594), (x + 3, 207, 745), material.WFV)
    # 前机身内部的测控机柜接在同一隔振床上。
    for x in (81, 331):
        box((x, 0, 47), (x + 8, 11, 131), material.ROBUST)
        shell((x, 12, 47), (x + 48, 140, 131), material.WFV, 3)
        shell((x + 8, 52, 56), (x + 40, 115, 122), material.COMPUTER, 2)
        box((x + 18, 4, 78), (x + 20, 52, 80), material.ROBUST)
        box((x + 14, 12, 130), (x + 17, 16, 166), material.ROBUST)

    for x in (105, 353):
        box((x, 14, 61), (x + 2, 15, 68), material.COPPER)

    # 屋盖由独立薄检修盖、内凹分缝和贯穿屋面的采光观察条组成。
    box((22, 286, 184), (438, 290, 566), None)
    box((22, 286, 184), (438, 287, 566), material.WFV)
    for z in (189, 326, 463):
        for x in (26, 309):
            box((x, 289, z), (x + 125, 290, z + 102), material.CLEAN)
            # 盖板上的锁紧棱和检修把手只做窄线，不填成厚白盖。
            for zz in (z + 12, z + 86):
                box((x + 9, 290, zz), (x + 116, 290, zz + 2), material.ROBUST)
        for x in (159, 279):
            box((x, 286, z + 3), (x + 22, 290, z + 91), material.BLACK)
            box((x + 3, 286, z + 6), (x + 19, 290, z + 88), None)
            box((x + 3, 289, z + 6), (x + 19, 290, z + 88), material.GLASS)
    # 四角小型锁扣连接六片可拆顶盖，凹槽保持敞开，不以整块实心板填平。
    for z in (193, 278, 330, 415, 467, 552):
        for x in (31, 146, 314, 429):
            box((x, 288, z), (x + 2, 288, z + 2), material.ROBUST)
    shell((188, 278, 184), (272, 290, 566), material.WFV, 2)
    for z in (201, 338, 475):
        box((202, 287, z), (258, 290, z + 61), material.BLACK)
        box((207, 287, z + 5), (253, 290, z + 56), None)
        box((207, 289, z + 5), (253, 290, z + 56), material.GLASS)

    # 侧门窗穿过四格结构壁，窗框与观察玻璃按真实厚度分开。
    for z in (208, 332, 456):
        box((0, 122, z + 9), (3, 213, z + 102), material.BLACK)
        box((0, 128, z + 15), (3, 207, z + 96), None)
        box((0, 128, z + 15), (1, 207, z + 96), material.GLASS)
        box((0, 98, z - 3), (2, 235, z - 1), material.ROBUST)
        box((0, 98, z + 113), (2, 235, z + 115), material.ROBUST)
    for y in (98, 232):
        box((0, y, 188), (3, y + 2, 564), material.WFV)
    for z in (208, 332, 456):
        box((0, 213, z + 55), (3, 237, z + 57), material.ROBUST)
    box((112, 198, 166), (348, 246, 169), None)
    box((112, 198, 166), (348, 246, 167), material.GLASS)

    controller = [CX, 30, 8]
    ports = [dict(id='真实维系试件输入', pos=[166, 30, 8], face='north'),
        dict(id='合格工程样件输出', pos=[294, 30, 8], face='north'),
        dict(id='I35锚定组件输入', pos=[190, 30, 8], face='north'),
        dict(id='失效试件隔离输出', pos=[270, 30, 8], face='north'),
        dict(id='锚定记录及负载资料输入', pos=[142, 30, 8], face='north'),
        dict(id='维系试验报告输出', pos=[318, 30, 8], face='north'),
        dict(id='西侧连续供能', pos=[46, 30, 95], face='west'),
        dict(id='东侧连续供能', pos=[414, 30, 95], face='east'),
        dict(id='稳定介质输入', pos=[46, 30, 145], face='west'),
        dict(id='用后介质回流', pos=[414, 30, 145], face='east')]
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；正式仓室与运行事实另验'
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data = dict(key='i37', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='前端样件交换与主控通廊', min=[126, 18, 0], max=[334, 42, 7]),
            dict(name='西舱内维护通道', min=[31, 66, 197], max=[49, 91, 561]),
            dict(name='东舱内维护通道', min=[411, 66, 197], max=[429, 91, 561])],
        zones=[dict(name='前端样件交换与测控机头', pos=[230, 145, 8]),
            dict(name='全封闭精密试验舱', pos=[230, 290, 340]),
            dict(name='两柱龙门计量梁', pos=[230, 266, 380]),
            dict(name='移动试样台与隔离夹具', pos=[230, 128, 380]),
            dict(name='后部工况与介质机柜', pos=[115, 80, 605]),
            dict(name='箱式隔振床身', pos=[230, 1, 380])],
        description='纵向一体的精密试验机由前端样件交换机头、中央封闭工作舱和后部工况机柜组成。舱内两柱龙门悬挂计量头，下方移动台承载真实局部维系样件；观察门、分块检修盖板、温控散热面与箱式隔振床身形成完整设备语言。EUV设备只作为工程外观参考，本机职责仍是受控世界维系试验。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图从0起算。',
            anchor='推荐世界Y=-60，最高实体Y=230。Schematic Offset为局部坐标，不是世界粘贴位置。',
            boundary='受控局部样件维系，不是半导体光刻配方；不制造世界，不破坏玩家地形，不替代I43验收或自动完成研究。',
            approval='I37 V1书本形轮廓已被负责人否决；本V3为独立待审候选，薄检修盖板、内凹分缝及贯穿观察窗形成可见设备细节；空腔机柜减少无功能堆料，未获批准、未实装。'))
    return cube, data


