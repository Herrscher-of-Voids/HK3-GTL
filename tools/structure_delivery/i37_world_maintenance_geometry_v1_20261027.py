# -*- coding: utf-8 -*-
"""I37开卷式层界负载台：双斜实验翼、层状样件舱与中央隔离承力脊。"""
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 601, 291, 501, 300
NAME = 'hk3gtl-i37-world-maintenance-v1-20261027'
TITLE = '世界维系试验平台 · 开卷式层界负载台'


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
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {s: '中央承力脊内部试样标定、负载注入或失效隔离设备' for s in STATES}
ROLES.update({material.WFV: '斜置分层实验翼、隔离承力脊和施载支座主体',
    material.ROBUST: '翼背主肋、铰接承座与纵向实验轨道', material.CLEAN: '实验翼层间护边和检修压条',
    material.ASSEMBLY: '前端样件移载及纵向维护走道', material.STRESS: '分段施载机组受力端面',
    material.GEAR: '试验翼分段预紧与加载机构', material.VENT: '承力脊内部设备的热交换面',
    material.GRATE: '斜翼分级维护廊', material.GLASS: '翼面试样舱真实观察窗口',
    material.BLUE_GLASS: '翼面层界测量的细光尺', material.BLACK: '试样舱遮光内衬',
    material.IRON: '可更换标定样件的机械基准夹座', material.OBSIDIAN: '中央局部扰动隔离仓的耐冲击衬块',
    material.PORT: '真实控制室连续面内的接口占位', material.CONTROL: '前端控制室整宽中线主控',
    material.PLASCRETE: '独立施载缸接地承座', material.GOLD: '少量层界坐标标定接点'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(lo, hi, state, t):
        box(lo, hi, state)
        box(tuple(v + t for v in lo), tuple(v - t for v in hi), None)

    # 纵向承力脊容纳真实设备与隔离仓；下方只铺窄接地轨，不铺全场大底座。
    shell((230, 0, 0), (370, 104, 500), material.WFV, 16)
    box((234, 0, 0), (366, 7, 500), material.ROBUST)
    for z in range(32, 470, 59):
        box((240, 15, z), (360, 92, z + 8), material.WFV)
    for y in (35, 70):
        box((235, y, 14), (365, y + 6, 486), material.ASSEMBLY)
    box((292, 105, 42), (308, 109, 466), material.BLACK)
    for x in (276, 319):
        box((x, 105, 35), (x + 5, 108, 470), material.GRATE)

    # 两幅斜翼的多层舱室如展开的世界剖面，舱内留空，横肋承担施载。
    yy, xx = np.mgrid[:H, :W]
    dx = abs(xx - CX)
    top = np.rint(50 + .8 * dx).astype(int)
    depth = top - yy
    wing = (dx >= 55) & (depth >= 0) & (depth <= 69)
    skins = wing & ((depth <= 6) | (depth >= 61) | ((depth >= 23) & (depth <= 29)) | ((depth >= 43) & (depth <= 49)))
    ribs = wing & (((dx - 55) % 48 <= 9) | (dx >= 290))
    for z in range(66, 443):
        rib_z = (z - 66) % 47 < 10 or z >= 431
        layer = cube[:, z, :]
        layer[wing if rib_z else skins | ribs] = IDS[material.WFV]
        if z in (66, 67, 68, 69, 439, 440, 441, 442):
            layer[wing & ((depth <= 4) | (depth >= 65))] = IDS[material.CLEAN]
    # 翼面每个分舱都有遮光试样内衬、观察窗与窄校准尺，不铺整片彩玻璃。
    for x in range(0, 246):
        distance = CX - x
        y = round(50 + .8 * distance)
        for X in (x, W - 1 - x):
            if distance % 48 < 4 or distance >= 293:
                box((X, y - 4, 66), (X, y, 442), material.CLEAN)
            elif 14 < distance % 48 < 33:
                for z in range(83, 414, 47):
                    box((X, y - 3, z), (X, y - 1, z + 21), material.BLACK)
                    box((X, y, z), (X, y, z + 21), material.GLASS)
            if distance % 48 in (6, 7):
                box((X, y + 1, 75), (X, y + 1, 429), material.BLUE_GLASS)
    # 层间纵向检修廊沿翼面逐级分布，前后工作端均与承力脊连通。
    for distance in (76, 124, 172, 220, 268):
        y = round(50 + .8 * distance)
        for sign in (-1, 1):
            a, b = sorted((CX + sign * (distance - 3), CX + sign * (distance + 3)))
            box((a, y, 69), (b, min(H - 1, y + 2), 438), material.GRATE)
    # 前后斜肋兼作铰接预紧面，沿整幅板传力，不形成四爪抓取构图。
    for x in range(W):
        distance = abs(x - CX)
        if distance < 52: continue
        y = round(50 + .8 * distance)
        for z in (56, 443):
            box((x, max(0, y - 77), z), (x, y - 3, z + 9), material.ROBUST)
            box((x, y - 10, z), (x, y - 3, z + 11), material.CLEAN)

    # 六组实体施载缸位于实验翼背面，力路径从地面传到试验舱肋。
    zz, xz = np.mgrid[:D, :W]
    for x in (127, 473):
        for z in (110, 254, 398):
            radial = np.sqrt((xz - x) ** 2 + (zz - z) ** 2)
            for y in range(127):
                r = 30 if y < 14 else 23 if y < 88 else 18
                mask = radial <= r
                cube[y, mask] = IDS[material.PLASCRETE if y < 7 else material.WFV]
                if y in (14, 15, 82, 83, 118, 119):
                    cube[y, mask] = IDS[material.STRESS]
            box((x - 15, 120, z - 15), (x + 15, 143, z + 15), material.GEAR)
    # 背部供能及介质纵列均贴着承力脊设置，外侧留出机器间的检修空间。
    for x in (218, 373):
        box((x, 16, 40), (x + 9, 24, 472), material.TUNG_PIPE)
        for z in range(56, 440, 64):
            box((x - 8, 10, z), (x + 17, 38, z + 27), material.WFV)
            box((x - 6, 39, z + 2), (x + 15, 44, z + 25), material.VENT)

    # 前端实体测试控制室与中脊一体，预留内退通廊而不是外挂控制面板。
    box((206, 0, 0), (394, 61, 55), material.WFV)
    box((211, 56, 0), (389, 61, 55), material.CLEAN)
    box((228, 15, 0), (372, 32, 7), None)
    box((232, 40, 0), (368, 49, 0), material.BLACK_GLASS)
    for x in (213, 376):
        box((x, 22, 20), (x + 11, 47, 42), material.GLASS)
    for x in (235, 333):
        box((x, 62, 14), (x + 31, 72, 40), material.COMPUTER)
        box((x + 3, 73, 17), (x + 28, 75, 37), material.LIGHT)
    # 专用材质集中在脊内两层实验设备，按用途少量使用并有实体支座。
    equipment = [s for s in STATES if s not in (material.WFV, material.PORT, material.CONTROL,
        material.ROBUST, material.CLEAN, material.ASSEMBLY, material.TUNG_PIPE, material.VENT,
        material.GLASS, material.BLUE_GLASS, material.BLACK, material.BLACK_GLASS, material.GRATE,
        material.STRESS, material.GEAR, material.PLASCRETE, material.COMPUTER, material.LIGHT)]
    for i, state in enumerate(equipment):
        z = 74 + (i % 12) * 33
        y = 43 if i < 12 else 78
        for x in (262, 338):
            box((x - 11, y - 2, z - 11), (x + 11, y - 1, z + 11), material.WFV)
            box((x - 10, y, z - 10), (x + 10, y + 13, z + 10), state)
    # 测试翼上保留少量校准夹座和端部坐标接点。
    for x in (33, 567):
        y = round(50 + .8 * abs(x - CX))
        for z in (78, 416):
            box((x - 5, y - 3, z), (x + 5, y, z + 9), material.GOLD)

    controller = [CX, 24, 8]
    ports = [dict(id='真实维系试件输入', pos=[252, 24, 8], face='north'),
        dict(id='合格工程样件输出', pos=[348, 24, 8], face='north'),
        dict(id='I35锚定组件输入', pos=[276, 24, 8], face='north'),
        dict(id='失效试件隔离输出', pos=[324, 24, 8], face='north'),
        dict(id='锚定记录及负载资料输入', pos=[236, 24, 8], face='north'),
        dict(id='维系试验报告输出', pos=[364, 24, 8], face='north'),
        dict(id='西侧连续供能', pos=[206, 24, 15], face='west'),
        dict(id='东侧连续供能', pos=[394, 24, 15], face='east'),
        dict(id='稳定介质输入', pos=[206, 24, 46], face='west'),
        dict(id='用后介质回流', pos=[394, 24, 46], face='east')]
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；正式仓室与运行事实另验'
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data = dict(key='i37', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='前端测试控制与样件交接通廊', min=[228, 15, 0], max=[372, 32, 7])],
        zones=[dict(name='左斜分层维系试验翼', pos=[70, 232, 254]),
            dict(name='右斜分层维系试验翼', pos=[530, 232, 254]),
            dict(name='中央隔离承力脊', pos=[300, 103, 260]),
            dict(name='背部施载缸与预紧机组', pos=[127, 50, 254]),
            dict(name='前端控制与报告交接室', pos=[300, 55, 28]),
            dict(name='连续供能与介质维护列', pos=[220, 20, 180])],
        description='两幅斜置的层状实验翼如打开的世界剖面，从中央隔离承力脊向两侧升起。分层试样舱、观察窗口、校准尺及检修廊沿翼面展开，背部六组施载缸把试验载荷传入独立地基。前端测试控制室接真实样件和记录，失败限制在试件与装置内部。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图从0起算。',
            anchor='推荐世界Y=-60，最高实体Y=230。Schematic Offset为局部坐标，不是世界粘贴位置。',
            boundary='表达局部维系样件受控试验，不制造新世界，不破坏玩家地形，不替代I43工程验收或自动完成研究。',
            approval='本I37 V1为独立待审候选，尚未批准、未计入批次或实装。'))
    return cube, data
