# -*- coding: utf-8 -*-
"""I39偏馈碟阵与双轨整备站：完整实体几何候选，不接入运行逻辑。"""
# 【变更记录 #1】2026-10-27：新增独立碟面、信号馈源、双轨航路及低位整备设施。
import math
from pathlib import Path

import numpy as np



ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 381, 211, 301, 190
NAME = 'hk3gtl-i39-unmanned-relay-v1-20261027'
TITLE = '无人跨界航路中继站 · 偏馈碟阵与双轨整备站'


class Material:
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
    GOLD = 'minecraft:gold_block'
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = {state: '航路中继站独立设备组件' for state in STATES}
ROLES.update({
    material.ICV: 'ICV主体机壳、天线反射单元、航路整备库及结构框架',
    material.PORT: '连续调度室正立面齐平接口占位，不提供真实仓室能力',
    material.CONTROL: '调度室中轴主控标记，仅用于预览',
    material.INSULATE: '碟阵反射背衬、极化隔片与设备绝缘罩',
    material.ROBUST: '碟阵支承弦杆、库房地梁与滑轨立柱',
    material.CLEAN: '双轨检修盖板与中继舱外护板',
    material.ASSEMBLY: '分层整备平台和服务设备托架',
    material.COMPUTER: '航路测控、授权核验与任务状态台架',
    material.POWER: '短程发射功率柜与接收整形单元',
    material.TUNG_PIPE: '碟阵波导、馈源短管与接收线路',
    material.STEEL_PIPE: '整备库之间的介质管线与冷却回路',
    material.GRATE: '无人装置滑轨踏面及高架维护通道',
    material.VENT: '发射柜与整备舱散热鳍片',
    material.GLASS: '中轴调度室观察窗',
    material.BLUE_GLASS: '碟阵相位读数及轨道状态窗',
    material.BLACK_GLASS: '调度室遮光观测带',
    material.GOLD: '偏馈焦点校准件与锁定触点',
    material.LIGHT: '双轨泊位状态灯',
})


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
        steps = max(abs(a[i] - b[i]) for i in range(3))
        for n in range(steps + 1):
            p = [round(a[i] + (b[i] - a[i]) * n / max(1, steps)) for i in range(3)]
            box(tuple(max(0, v - r) for v in p),
                tuple(min(s - 1, v + r) for v, s in zip(p, (W, H, D))), state)

    def dish_depth(x, y):
        radius2 = (x - CX) ** 2 + (y - 108) ** 2
        return round(225 + 0.0045 * radius2 + 0.11 * (y - 108))

    # 反射面以逐格抛物线求深，后缘由同一曲面分层背衬。
    for x in range(CX - 102, CX + 1):
        dx = x - CX
        for y in range(6, 211):
            dy = y - 108
            r2 = dx * dx + dy * dy
            if r2 > 102 * 102:
                continue
            depth = dish_depth(x, y)
            ring = int(math.sqrt(r2)) // 16
            panel = material.INSULATE if ring % 3 else material.ICV
            if ring in (1, 4) and abs(dy) % 19 < 2:
                panel = material.BLUE_GLASS
            if dx % 23 == 0 and ring % 2:
                panel = material.CLEAN
            cube[y, depth, x] = IDS[panel]
            cube[y, depth + 1, x] = IDS[material.ICV]
            if r2 > 86 * 86:
                cube[y, depth - 1, x] = IDS[material.ROBUST]
    # 一体外缘、弧形背弦与四道径向承力肋。
    for x in range(CX - 102, CX + 1):
        dx = x - CX
        for y in range(6, 211):
            dy = y - 108
            r2 = dx * dx + dy * dy
            if 98 * 98 <= r2 <= 102 * 102:
                cube[y, dish_depth(x, y) - 1, x] = IDS[material.ICV]
    for sign in (1,):
        for dy in range(-99, 100):
            dx = round(math.sqrt(max(0, 98 * 98 - dy * dy)))
            x = CX - dx
            y = 108 + dy
            z = dish_depth(x, y) - 2
            box((x - 1, y, z), (x + 1, y, z + 2), material.TUNG_PIPE)
        for y in range(9, 209):
            dx = round(math.sqrt(max(0, 94 * 94 - (y - 108) ** 2)))
            x = CX - dx
            z = dish_depth(x, y) - 2
            box((x - 2, y, z), (x + 2, y, z + 2), material.ROBUST)

    # 四段封闭式低位设备库：两类航路各自整备、交接，保持中轴通行。
    halls = [((15, 0, 22), (178, 75, 91)), ((15, 0, 95), (178, 75, 164))]
    for lo, hi in halls:
        x0, y0, z0 = lo; x1, y1, z1 = hi
        shell(lo, hi, material.ICV, 2)
        for y in (0, 12, 24, 36, 48, 60, 72):
            box((x0 + 3, y, z0 + 3), (x1 - 3, y + 1, z1 - 3), material.ICV)
            for x in range(x0 + 9, x1 - 5, 18):
                box((x, y + 1, z0 + 4), (x + 2, y + 4, z1 - 4), material.GRATE)
        for x in range(x0 + 14, x1 - 8, 27):
            box((x, 3, z0 + 3), (x + 2, y1 - 3, z0 + 5), material.ROBUST)
            box((x, 3, z1 - 5), (x + 2, y1 - 3, z1 - 3), material.ROBUST)
        # 多层无人装置泊位，以空腔、承架和可达检修层组织空间。
        for y in (3, 15, 27, 39, 51, 63):
            for z in (z0 + 13, z0 + 39, z0 + 56):
                shell((x0 + 10, y, z), (x0 + 25, y + 10, z + 15), material.CLEAN, 1)
                box((x0 + 15, y + 2, z + 2), (x0 + 20, y + 7, z + 13), material.POWER)
                box((x0 + 12, y + 8, z + 6), (x0 + 23, y + 9, z + 9), material.DIMENSION)
                box((x0 + 11, y + 4, z + 4), (x0 + 11, y + 6, z + 11), material.LIGHT)
        for y in (10, 22, 34, 46, 58):
            for x in (x0 + 31, x0 + 62, x0 + 93, x0 + 124):
                box((x, y, z0 + 8), (x + 2, y + 9, z1 - 8), material.VENT)
                box((x + 3, y + 2, z0 + 8), (x + 6, y + 7, z1 - 8), material.STEEL_PIPE)
        # 分层空心整备卡匣，平台承接机匣，内腔与轨侧检修空间保留。
        for y in (3, 15, 27, 39, 51, 63):
            for x in range(x0 + 39, x1 - 12, 21):
                for z in (z0 + 9, z0 + 32, z0 + 51):
                    shell((x, y, z), (x + 14, y + 8, z + 13), material.ICV, 2)
                    box((x + 3, y + 3, z + 3), (x + 11, y + 5, z + 10), material.POWER)
                    box((x + 6, y + 1, z + 5), (x + 8, y + 4, z + 8), material.POWER)
                    box((x + 2, y + 8, z + 3), (x + 12, y + 8, z + 10), material.CLEAN)
                    box((x + 4, y + 5, z), (x + 10, y + 6, z), material.BLUE_GLASS)
        # 小型配电、滤波与信号诊断件，材料只作对应功能构件。
        parts = [s for s in STATES if s not in {material.ICV, material.PORT, material.CONTROL,
            material.ASSEMBLY, material.GRATE, material.ROBUST, material.CLEAN, material.POWER,
            material.DIMENSION, material.LIGHT, material.VENT, material.STEEL_PIPE,
            material.INSULATE, material.BLUE_GLASS}]
        for i, state in enumerate(parts):
            x = x0 + 30 + (i % 5) * 25
            z = z0 + 9 + (i // 5) * 13
            y = 6 + (i % 3) * 17
            box((x, y, z), (x + 4, y + 5, z + 4), state)
            box((x, 0, z), (x, y, z), material.ASSEMBLY)

    # 整备库外立面按泊位分节，窄窗、门洞和外露承力肋使双轨侧易于辨识。
    for lo, hi in halls:
        x0, _, z0 = lo; x1, y1, z1 = hi
        for x in range(x0 + 9, x1 - 10, 26):
            for z in (z0, z1):
                box((x, 0, z - 1), (x + 2, y1, z + 1), material.ROBUST)
                for y in (17, 41, 65):
                    box((x + 4, y, z), (x + 21, y + 4, z), material.BLACK)
                    box((x + 5, y + 1, z), (x + 20, y + 3, z), material.GLASS)
        for y in (11, 35, 59):
            box((x0, y, z0), (x1, y + 1, z0), material.CLEAN)
            box((x0, y, z1), (x1, y + 1, z1), material.CLEAN)
        for z in (z0 + 18, z0 + 47):
            # 内侧门退一格，外框与分段卷闸仍为完整实体，不改变仓内层架。
            box((x1, 3, z - 10), (x1, 31, z + 10), None)
            box((x1 - 1, 3, z - 10), (x1 - 1, 31, z + 10), material.COMPUTER)
            for y in range(5, 30, 5):
                box((x1 - 1, y, z - 9), (x1 - 1, y + 1, z + 9), material.CLEAN)
            for dz in (-11, 11):
                box((x1, 1, z + dz), (x1 + 1, 34, z + dz), material.ROBUST)
            box((x1, 32, z - 11), (x1 + 1, 34, z + 11), material.ICV)
            box((x1, 35, z - 5), (x1, 35, z + 5), material.LIGHT)
        for x in (x0 + 27, x0 + 67, x0 + 107):
            # 屋面低矮排风帽与间隔检修带，不扩展最高点或制造新塔。
            shell((x, y1 + 1, z0 + 20), (x + 18, y1 + 7, z0 + 43), material.ICV, 1)
            box((x + 2, y1 + 7, z0 + 22), (x + 16, y1 + 8, z0 + 41), material.VENT)
            for z in range(z0 + 24, z0 + 41, 6):
                box((x + 1, y1 + 2, z), (x + 17, y1 + 2, z + 1), material.STEEL_PIPE)
        for x in (x0 + 6, x0 + 147):
            box((x, y1 + 1, z0 + 5), (x + 3, y1 + 1, z1 - 5), material.GRATE)
    # 镜像右侧两条泊位库，外部各留一条维护轨架。
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    for x in (2, 8, 370, 376):
        box((x, 0, 25), (x + 1, 5, 170), material.ICV)
        box((x - 2, 6, 40), (x + 3, 7, 164), material.GRATE)
        for z in range(31, 170, 12):
            box((x - 2, 2, z), (x + 3, 7, z + 1), material.ROBUST)
    for x in (0, 380):
        box((x, 0, 26), (x, 3, 170), material.ICV)
    box((0, 0, 22), (380, 3, 26), material.ICV)
    box((15, 0, 162), (178, 2, 173), material.ICV)

    # 调度室和正面齐平接口，主控位于中轴；连续墙体提供实体背板。
    shell((94, 0, 0), (286, 49, 23), material.ICV, 2)
    box((97, 0, 1), (283, 3, 21), material.PLASCRETE)
    box((99, 6, 2), (281, 8, 21), material.ASSEMBLY)
    box((107, 13, 0), (273, 38, 0), material.ICV)
    box((113, 14, 0), (267, 15, 0), material.COMPUTER)
    box((113, 35, 0), (267, 36, 0), material.CLEAN)
    box((116, 23, 0), (264, 29, 0), material.BLACK)
    box((120, 24, 0), (260, 28, 0), material.BLACK_GLASS)
    for x in (110, 270):
        box((x, 15, 0), (x, 34, 0), material.GLASS)
    controller = [CX, 22, 0]
    ports = [dict(id=name, pos=[CX - dx, 22, 0], face='north')
        for dx, name in zip((22, 38, 54, 70, 86), ('发射任务输入', '信标坐标输入', '无人设备送入', '维护物资补给', '辅助供能输入'))]
    ports += [dict(id=name, pos=[CX + dx, 22, 0], face='north')
        for dx, name in zip((22, 38, 54, 70, 86), ('返航装置交接', '任务状态回执', '异常维护处置', '用后材料输出', '辅助供能回路'))]
    for port in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = port['pos']
        cube[y, z, x] = IDS[material.CONTROL if port['id'] == '主控' else material.PORT]
        port['purpose'] = port['id'] + '候选；实际调度、权限及传输能力另验'

    # 馈源位于碟面焦点，成对馈臂及宽距支撑与主体航路架相接。
    focus = (CX, 108, 180)
    shell((CX - 9, 99, 174), (CX + 9, 117, 187), material.ICV, 2)
    box((CX - 4, 104, 168), (CX + 4, 112, 173), material.POWER)
    for y in (105, 111):
        box((CX - 3, y, 163), (CX + 3, y, 168), material.TUNG_PIPE)
    beam((CX + 88, 108, 270), focus, material.TUNG_PIPE, 1)
    beam((CX + 60, 180, 275), focus, material.ROBUST, 1)
    beam((CX + 66, 37, 274), focus, material.ROBUST, 1)
    beam((CX + 85, 22, 260), (CX + 74, 0, 196), material.ICV, 2)
    beam((CX + 84, 45, 277), (CX + 104, 0, 199), material.ROBUST, 1)
    # 双轨分开发射与返航；低位支架和导向槽一直连至天线测控平台。
    for x in (170, 174):
        box((x, 4, 71), (x + 2, 7, 198), material.TUNG_PIPE)
        box((x - 2, 3, 75), (x + 4, 4, 194), material.GRATE)
        for z in range(83, 195, 12):
            box((x - 2, 0, z), (x + 4, 6, z + 1), material.ROBUST)
    for x in (112, 132, 152, 169):
        shell((x, 0, 102), (x + 11, 35, 136), material.ICV, 2)
        box((x + 4, 6, 99), (x + 7, 30, 103), material.POWER)
        box((x + 2, 32, 107), (x + 9, 34, 130), material.VENT)
    # 中央调度至碟阵的实体维护跨接，避开贯通主走道。
    beam((CX - 44, 46, 148), (CX - 20, 86, 199), material.ROBUST, 2)
    beam((CX - 20, 86, 199), focus, material.INSULATE, 2)
    beam((CX - 66, 14, 157), (CX - 44, 46, 148), material.ICV, 2)
    for y in (26, 31, 36, 41):
        box((CX - 24, y, 153), (CX + 24, y + 1, 159), material.MULTI)
    box((CX - 18, 10, 143), (CX + 18, 27, 155), material.COMPUTER)
    box((CX - 14, 28, 148), (CX + 14, 30, 153), material.BLUE_GLASS)

    # 后部俯仰轴承和波导整形机匣构成碟阵后座，实体设备确定最深边界。
    shell((CX - 43, 0, 245), (CX + 43, 86, 300), material.ICV, 2)
    box((CX - 42, 0, 246), (CX + 42, 4, 299), material.PLASCRETE)
    for y in (7, 22, 37, 52, 67):
        box((CX - 40, y, 248), (CX + 40, y + 1, 297), material.ICV)
        for x in range(CX - 34, CX + 30, 18):
            shell((x, y + 2, 251), (x + 12, y + 13, 290), material.ICV, 2)
            box((x + 3, y + 5, 254), (x + 9, y + 9, 287), material.GEAR)
            box((x + 5, y + 1, 260), (x + 7, y + 6, 262), material.GEAR)
    for x in (CX - 40, CX + 40):
        box((x, 2, 248), (x + 1, 84, 297), material.ROBUST)
    for y in range(12, 79, 11):
        box((CX - 35, y, 299), (CX + 35, y + 2, 300), material.VENT)
    beam((CX, 86, 270), (CX, 108, 226), material.ROBUST, 3)
    beam((CX - 43, 22, 263), (CX - 80, 42, 275), material.ICV, 3)
    beam((CX - 43, 3, 246), (CX - 43, 3, 164), material.ICV, 3)
    beam((CX - 20, 108, 225), (CX - 44, 46, 148), material.ROBUST, 2)
    # 对称轨道支承由中继机架承接，连接设备库、碟阵馈源与外部泊位。
    for x in (CX - 16, CX + 16):
        beam((x, 5, 166), (x, 65, 178), material.ROBUST, 1)
        beam((x, 65, 178), (CX + (1 if x > CX else -1) * 13, 104, 179), material.TUNG_PIPE, 1)
    for x in (CX - 32, CX + 32):
        box((x, 0, 164), (x + 2, 73, 167), material.ICV)
        for y in range(8, 69, 12):
            box((x - 3, y, 161), (x + 5, y + 2, 170), material.CLEAN)

    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    assert np.array_equal(cube, cube[:, :, ::-1]), 'I39左右镜像失败'
    data = dict(key='i39', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='中轴检修与任务交接通道', min=[184, 9, 30], max=[196, 13, 130])],
        zones=[dict(name='偏馈抛物碟面', pos=[CX, 108, 225]),
            dict(name='发射整备库', pos=[15, 20, 58]),
            dict(name='返航回收库', pos=[47, 50, 130]),
            dict(name='低位测控与馈源', pos=[CX, 108, 180]),
            dict(name='返航双轨与维护栈桥', pos=[170, 5, 120]),
            dict(name='中轴航路调度室', pos=[CX, 49, 12])],
        description='后置偏馈抛物面碟阵由曲面反射单元、径向承力肋、偏置馈源与外伸馈臂组成，碟面朝向低位测控机房。前场分为无人装置发射线和返航交接线，两侧设备库按泊位分层整备；中央维护通道贯通调度室与碟阵，不设置高塔、围院或四爪托举物。',
        construction_notes=dict(orientation='主控北向/-Z；蓝图从0起算；X=190为整宽第191格。',
            anchor='推荐世界Y=-60；最高实体Y=150；外部世界坐标须按结构锚点另行定位。',
            boundary='仅表达获授权的无人设备航路排程、发射与返航交接；不创建资源倍率、不传送实体，不替代I26初始任务。',
            approval='I39 V1为独立待审外观候选；实际控制器、无人实体与任务服务另行验收。'))
    return cube, data


if __name__ == '__main__':
    blocks = build()[0]
    counts = np.bincount(blocks.ravel())
    print({'blocks': int(counts[1:].sum()), 'materials': int((counts[1:] > 0).sum()),
           'icv': int(counts[IDS[material.ICV]]), 'bbox': [W, D, H]})
