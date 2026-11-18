# -*- coding: utf-8 -*-
"""I36双叉谐振稳相井：开敞基准叉、沉井锚芯与纵向阻尼机列。"""
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_erosion

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 201, 151, 181, 100
NAME = 'hk3gtl-i36-reality-anchor-v1-20261027'
TITLE = '崩坏能现实稳定锚 · 双叉谐振稳相井'


class Material:
    QSV = 'hk3gtl:voltage_machine_casing_qsv'
    PORT = 'hk3gtl:industrial_port_casing'
    CONTROL = 'minecraft:diamond_block'
    ROBUST = 'gtceu:robust_machine_casing'
    CLEAN = 'gtceu:clean_machine_casing'
    ASSEMBLY = 'gtceu:assembly_line_casing'
    VIBRATION = 'gtceu:vibration_safe_casing'
    STRESS = 'gtceu:stress_proof_casing'
    TUNG_PIPE = 'gtceu:tungstensteel_pipe_casing'
    STEEL_PIPE = 'gtceu:steel_pipe_casing'
    POWER = 'gtceu:high_power_casing'
    COMPUTER = 'gtceu:advanced_computer_casing'
    VENT = 'gtceu:computer_heat_vent'
    GEAR = 'gtceu:tungstensteel_gearbox'
    TURBINE = 'gtceu:stainless_steel_turbine_casing'
    GRATE = 'gtceu:assembly_line_grating'
    INSULATE = 'gtceu:nonconducting_casing'
    FROST = 'gtceu:frostproof_machine_casing'
    INERT = 'gtceu:inert_machine_casing'
    GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
    BLUE_GLASS = 'minecraft:light_blue_stained_glass'
    BLACK_GLASS = 'minecraft:black_stained_glass'
    LIGHT = 'minecraft:sea_lantern'
    GOLD = 'minecraft:gold_block'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = dict(zip(STATES, [s.split(':')[1] for s in STATES]))
ROLES.update({material.QSV: '双叉、沉井环梁及冷却机列的QSV主承力外壳',
    material.PORT: '本体内嵌物料、资料、能量与介质接口占位', material.CONTROL: '前端标定室中线主控标记',
    material.ROBUST: '基准叉后缘与斜向阻尼撑杆的承力骨架', material.CLEAN: '叉尖护棱与沉井检修压边',
    material.ASSEMBLY: '检修走道和机列托架', material.VIBRATION: '与沉井连接的弹性隔振支座',
    material.STRESS: '叉根预紧带与撑杆端部受力节点', material.TUNG_PIPE: '沉井锚芯及稳定介质主干',
    material.STEEL_PIPE: '左右冷却回流管廊', material.POWER: '前端连续供能变换装置',
    material.COMPUTER: '标定室顶部覆盖状态与耗材监测设备', material.VENT: '侧列设备的分段冷却排风面',
    material.GEAR: '后斜撑的可调预紧机构', material.TURBINE: '侧列循环介质泵组', material.GRATE: '井口开放检修格栅',
    material.INSULATE: '基准叉内壁的分段绝缘标定面', material.FROST: '低位热交换设备',
    material.INERT: '稳定耗材的封闭接触仓', material.GLASS: '标定室及介质观察窗',
    material.BLUE_GLASS: '基准叉内侧窄幅稳相读数光带', material.BLACK_GLASS: '主控室遮光读出窗',
    material.LIGHT: '井口、维护面与标定室照明', material.GOLD: '少量实际标定接点'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(lo, hi, state, t):
        box(lo, hi, state)
        box(tuple(v + t for v in lo), tuple(v - t for v in hi), None)

    def beam(a, b, state, r):
        steps = max(abs(a[i] - b[i]) for i in range(3))
        for n in range(steps + 1):
            p = [round(a[i] + (b[i] - a[i]) * n / max(steps, 1)) for i in range(3)]
            box(tuple(max(0, v - r) for v in p), tuple(min(s - 1, v + r) for v, s in zip(p, (W, H, D))), state)

    # 开敞沉井围住锚芯，中央保留真实空腔，不铺整片大底台。
    zz, xx = np.mgrid[:D, :W]
    radius = np.sqrt((xx - CX) ** 2 + (zz - 110) ** 2)
    for y in range(33):
        outer = 70 if y < 12 else 66
        inner = 49 if y < 9 else 54
        ring = (radius <= outer) & (radius >= inner)
        cube[y, ring] = IDS[material.QSV]
        if y in (0, 1, 29, 30, 31, 32):
            cube[y, ring] = IDS[material.CLEAN if y > 1 else material.VIBRATION]
    # 井内锚芯有逐层缩窄的贯地端，顶部与叉根相连。
    for y in range(56):
        r = 5 + min(y, 30) * .65
        mask = (abs(xx - CX) <= r) & (abs(zz - 110) <= r) & (abs(xx - CX) + abs(zz - 110) <= r * 1.65)
        cube[y, mask] = IDS[material.TUNG_PIPE if y % 13 < 3 else material.QSV]
    for x in (70, 121):
        box((x, 24, 102), (x + 9, 30, 118), material.STRESS)

    # 音叉形体：下半圆整体承座过渡成两根开顶长叉，顶端没有封闭横梁。
    yy, xx2 = np.mgrid[:H, :W]
    r2 = (xx2 - CX) ** 2 + (yy - 92) ** 2
    fork = ((r2 <= 66 ** 2) & (r2 >= 35 ** 2) & (yy <= 92)) | (
        (yy >= 92) & (((xx2 >= 34) & (xx2 <= 65)) | ((xx2 >= 135) & (xx2 <= 166))))
    edge = fork & ~binary_erosion(fork, iterations=3, border_value=1)
    for z in range(83, 128):
        cube[:, z, :][fork] = IDS[material.QSV]
        if z in (83, 84, 85, 125, 126, 127):
            # 内外边缘压条，保留大面积主机壳的识别色。
            cube[:, z, :][edge] = IDS[material.CLEAN]
    for x in (34, 159):
        box((x, 92, 88), (x + 7, 150, 122), material.ROBUST)
    for x in (44, 143):
        box((x, 146, 83), (x + 13, 150, 127), material.CLEAN)
        box((x + 4, 147, 81), (x + 9, 149, 82), material.GOLD)
    # 内壁窄光尺与分段绝缘座，留白本身成为工作区。
    for y in (88, 104, 120, 136):
        for x in (61, 135):
            box((x, y, 88), (x + 4, y + 8, 122), material.INSULATE)
            box((x + (4 if x == 61 else 0), y + 2, 91), (x + (4 if x == 61 else 0), y + 6, 119), material.BLUE_GLASS)
    for y in (64, 80):
        for x in (39, 147):
            box((x, y, 82), (x + 14, y + 5, 84), material.STRESS)

    # 后倾阻尼拉杆把高叉传来的力落到地面预紧座，避免悬空叉体。
    for x in (49, 151):
        beam((x, 119, 128), (x, 16, 174), material.ROBUST, 5)
        beam((x, 116, 132), (x, 18, 177), material.CLEAN, 2)
        box((x - 17, 0, 161), (x + 17, 12, 180), material.QSV)
        box((x - 11, 13, 163), (x + 11, 24, 179), material.GEAR)

    # 两侧低位冷却机列分段布置，机列与井壳通过管廊接合。
    for x in (21, 179):
        for z in (23, 73, 123):
            box((x - 21, 0, z - 14), (x + 21, 6, z + 14), material.VIBRATION)
        for z in range(14, 151):
            for y in range(7, 46):
                r = math.sqrt((y - 26) ** 2)
                half = max(1, math.floor(math.sqrt(max(0, 19 ** 2 - r ** 2))))
                cube[y, z, x - half:x + half + 1] = IDS[material.QSV]
        for z in (18, 49, 80, 111, 143):
            box((x - 18, 12, z - 2), (x + 18, 40, z + 2), material.CLEAN)
        for z in (30, 63, 96, 129):
            box((x - 12, 40, z - 8), (x + 12, 45, z + 8), material.VENT)
        box((x - 10, 16, 7), (x + 10, 35, 13), material.TURBINE)
        box((x - 10, 16, 151), (x + 10, 35, 157), material.FROST)
        box((min(x, CX), 8, 65), (max(x, CX), 16, 73), material.STEEL_PIPE)
        box((x - 18, 5, 40), (x + 18, 8, 149), material.ASSEMBLY)

    # 中线标定室是实在的房体；侧列供能与耗材设备共享其维护空间。
    shell((64, 0, 0), (136, 37, 45), material.QSV, 6)
    box((64, 0, 0), (136, 4, 45), material.VIBRATION)
    box((64, 36, 0), (136, 38, 45), material.CLEAN)
    box((64, 5, 8), (136, 28, 15), material.QSV)
    box((73, 14, 0), (127, 22, 7), None)
    box((82, 29, 0), (118, 33, 0), material.BLACK_GLASS)
    box((64, 14, 20), (64, 28, 35), material.GLASS)
    box((136, 14, 20), (136, 28, 35), material.GLASS)
    for x in (75, 111):
        box((x, 39, 17), (x + 14, 47, 33), material.POWER)
        box((x + 2, 48, 19), (x + 12, 51, 31), material.COMPUTER)
        box((x + 3, 52, 20), (x + 11, 53, 30), material.LIGHT)
        box((x, 6, 47), (x + 14, 22, 60), material.INERT)
        box((x + 2, 20, 48), (x + 12, 23, 59), material.GLASS)
    box((64, 5, 40), (136, 9, 83), material.QSV)
    box((65, 10, 43), (135, 12, 81), material.GRATE)
    for x in (64, 133):
        box((x, 13, 43), (x + 3, 15, 80), material.CLEAN)

    controller = [CX, 18, 8]
    ports = [dict(id='基础稳定耗材补充', pos=[84, 18, 8], face='north'),
        dict(id='用后耗材回收', pos=[116, 18, 8], face='north'),
        dict(id='标定与工况资料输入', pos=[76, 18, 8], face='north'),
        dict(id='覆盖状态与记录输出', pos=[124, 18, 8], face='north'),
        dict(id='西侧持续供能', pos=[64, 18, 12], face='west'),
        dict(id='东侧持续供能', pos=[136, 18, 12], face='east'),
        dict(id='稳定介质补给', pos=[64, 18, 39], face='west'),
        dict(id='用后介质回流', pos=[136, 18, 39], face='east')]
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；正式能力和运行链另验'
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data = dict(key='i36', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports,
        paths=[dict(name='前端主控及耗材通廊', min=[73, 14, 0], max=[127, 22, 7])],
        zones=[dict(name='开顶双叉现实基准', pos=[50, 140, 105]),
            dict(name='沉井贯地锚芯', pos=[100, 18, 110]),
            dict(name='整体弧形叉根承座', pos=[100, 42, 105]),
            dict(name='后倾阻尼预紧座', pos=[49, 15, 172]),
            dict(name='分段冷却与介质机列', pos=[21, 26, 60]),
            dict(name='前端覆盖标定室', pos=[100, 35, 25])],
        description='一体弧形叉根从开敞沉井升起，分成两根开顶长叉，内壁稳相光尺围住留白的现实基准区。井内锚芯向下收尖，后倾阻尼撑杆落入独立预紧座；两侧低位冷却机列与前端标定室构成持续运行设备，不设围院或抓取中央物件的四爪。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图从0起算。',
            anchor='推荐世界Y=-60，最高实体Y=90；沉井与锚芯均为实体设计，不自动挖掘地形。',
            boundary='仅表达现实稳定覆盖设备；不新增跨维传送、免费能源、世界创建或全维保护。',
            approval='I35 V3已确认归档；本I36 V1为独立待审候选，未实装。'))
    return cube, data
