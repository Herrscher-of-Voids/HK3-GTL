# -*- coding: utf-8 -*-
"""生成 I23 低重心双瓣相界锻炉候选 V8。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V6_SCRIPT = ROOT / 'deliveries/I23_崩坏能相变释能机_相变舱原位接口与I22式审阅页_V6_20261024/生成脚本/build_i23_phase_change_candidate_v6_20261024.py'
SPEC = importlib.util.spec_from_file_location('i23_v6_export_helpers', V6_SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f'无法读取 I23 结构导出工具：{V6_SCRIPT}')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
ORIGINAL_REPORT_PAGE = builder.make_report_page
ORIGINAL_REVIEW_PAGE = builder.make_review_page
ORIGINAL_RELABEL_PREVIEW = builder.relabel_preview
ORIGINAL_RENDER_CONTROLLER = builder.render_controller_detail
ORIGINAL_BLOCK_COLOR = builder.block_color
ORIGINAL_AUDIT = builder.audit

OUT = ROOT / 'deliveries/I23_崩坏能相变释能机_双瓣相界锻炉_V8_20261024'
NAME = 'hk3gtl-i23-twin-lobe-phase-forge-v8-20261024'
W, H, D = 89, 57, 102
CX, CZ = W // 2, 45
LOBE_CENTERS = (28, 60)
CORE_FRONT = 0
REAR_SHIFT = 11

QCV = 'hk3gtl:voltage_machine_casing_qcv'
DIAMOND = 'minecraft:diamond_block'
FLOOR = 'gtceu:clean_machine_casing'
FRAME = 'gtlcore:lafium_mechanical_casing'
POWER = 'gtceu:high_power_casing'
PIPE = 'gtceu:tungstensteel_pipe_casing'
CHEM = 'gtceu:corrosion_proof_casing'
GLASS = 'minecraft:cyan_stained_glass'
REINFORCED_GLASS = 'minecraft:light_blue_stained_glass'
FILTER = 'gtlcore:law_filter_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
COOL = 'gtlcore:super_cooler_component[active=false]'
COIL = 'kubejs:titansteel_coil_block[active=false]'
CRYSTAL = 'minecraft:amethyst_block'
PHASE_GLASS = 'minecraft:purple_stained_glass'
LIGHT = 'minecraft:sea_lantern'
GRATE = 'gtceu:assembly_line_grating'
COMPUTER = 'gtceu:advanced_computer_casing'
COMPUTE = 'gtlcore:super_computation_component[active=false]'
PORT = 'hk3gtl:industrial_port_casing'

builder.ROOT = ROOT
builder.OUT = OUT
builder.NAME = NAME
builder.W, builder.H, builder.D = W, H, D
builder.CX, builder.CZ = CX, CZ
builder.X_SHIFT = builder.Z_SHIFT = 0
builder.SOURCE_W, builder.SOURCE_D = W, D
builder.base.ROOT = ROOT
builder.base.OUT = OUT
builder.base.NAME = NAME
builder.base.W, builder.base.H, builder.base.D = W, H, D


def put(x: int, y: int, z: int, state: str, replace: bool = False) -> None:
    builder.put(x, y, z, state, replace)


def line(a: tuple[int, int, int], b: tuple[int, int, int], state: str,
         replace: bool = False) -> None:
    builder.step_line(a, b, state, replace)


def oct_contains(cx: int, cz: int, rx: int, rz: int, x: int, z: int) -> bool:
    dx, dz = abs(x - cx), abs(z - cz)
    return dx <= rx and dz <= rz and dx * rz + dz * rx <= rx * rz * 1.48


def rear_z(value: int) -> int:
    return value + REAR_SHIFT


def profile_at(y: int) -> tuple[int, int]:
    profile = [(4, 12, 14), (8, 16, 19), (13, 17, 20),
               (39, 17, 20), (44, 15, 18), (49, 11, 14),
               (53, 7, 10), (56, 4, 7)]
    for (y0, rx0, rz0), (y1, rx1, rz1) in zip(profile, profile[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return round(rx0 + (rx1 - rx0) * t), round(rz0 + (rz1 - rz0) * t)
    return profile[0][1:] if y < profile[0][0] else profile[-1][1:]


def make_phase_vessel() -> None:
    """横向双瓣：独立穹肩、通透相界腔与低位连体承台。"""
    for lc in LOBE_CENTERS:
        other = LOBE_CENTERS[1] if lc == LOBE_CENTERS[0] else LOBE_CENTERS[0]
        for y in range(4, 57):
            rx, rz = profile_at(y)
            for x in range(lc-rx, lc+rx+1):
                for z in range(CZ-rz, CZ+rz+1):
                    if not oct_contains(lc, CZ, rx, rz, x, z):
                        continue
                    inside = oct_contains(lc, CZ, max(2,rx-2), max(2,rz-2), x,z)
                    if inside and y not in (4,56):
                        continue
                    if oct_contains(other,CZ,max(2,rx-2),max(2,rz-2),x,z) and y < 42:
                        continue
                    state = QCV
                    if 40 <= y <= 52:
                        state = FLOOR
                        # 蓝色纵肋把亮肩壳分成四块大曲面，顶部仍保留电压识别冠。
                        if abs(x-lc)<=2 or abs(z-CZ)<=2 or y in (44,49):
                            state=QCV
                        elif abs(x-lc)<=6 and abs(z-CZ)>=rz-1 and 42<=y<=48:
                            state=REINFORCED_GLASS
                    if y in (8,9,13,37,38,53):
                        state = FRAME if y in (8,13,37,44,53) else POWER
                    # 玻璃构成压力腔皮肤本身，内核从正面和斜侧均可见。
                    if 15 <= y <= 35:
                        if abs(x-lc) <= 10 and abs(z-CZ) >= rz-1:
                            state = GLASS
                        if abs(z-CZ) <= 8 and abs(x-lc) >= rx-1:
                            state = REINFORCED_GLASS
                        if abs(x-lc) > 10 and abs(z-CZ) > 8 and y % 11 not in (0,1):
                            state = GLASS
                    put(x,y,z,state)

        # 连续承台、两道亮色环箍与随穹肩收拢的纵向肋。
        for y in (2,3):
            builder.oct_ring(lc,CZ,17,20,y,FRAME if y==2 else QCV)
        for sx,sz in ((-1,-1),(1,-1),(-1,1),(1,1)):
            for y in range(4,54):
                rx,rz=profile_at(y)
                x=lc+sx*round(rx*.7)
                z=CZ+sz*round(rz*.78)
                line((x,y,z),(x,y+1,z),FRAME,True)
        # 颈部很短，顶端为开槽封顶，不形成巨大实心帽。
        for y in range(50,57):
            rx,rz=profile_at(y)
            for x in range(lc-rx,lc+rx+1):
                for z in range(CZ-rz,CZ+rz+1):
                    if y==56 and oct_contains(lc,CZ,rx,rz,x,z):
                        put(x,y,z,POWER if x in (lc-1,lc,lc+1) else QCV,True)
            line((lc-rx,y,CZ),(lc+rx,y,CZ),FRAME,True)

        # 上下错位的相界晶核与三层锻环均在透光舱内。
        for y in range(13,44):
            core_radius = max(1,5-abs(y-28)//4)
            for x in range(lc-core_radius,lc+core_radius+1):
                for z in range(CZ-core_radius,CZ+core_radius+1):
                    if abs(x-lc)+abs(z-CZ)<=core_radius:
                        put(x,y,z,CRYSTAL if (y//4)%2 else PHASE_GLASS)
        for yy in (16,26,36):
            builder.oct_ring(lc,CZ,9,11,yy,COIL)
            builder.oct_ring(lc,CZ,10,12,yy+1,FRAME)
            line((lc-16,yy,CZ),(lc+16,yy,CZ),FRAME)
            line((lc,yy,CZ-19),(lc,yy,CZ+19),FRAME)
            for x in (lc-9,lc+9):
                line((x,13,CZ),(x,43,CZ),POWER)
            for z in (CZ-10,CZ+10):
                line((lc,14,z),(lc,43,z),LIGHT)
        line((lc,4,CZ),(lc,14,CZ),GEAR)
        line((lc,43,CZ),(lc,56,CZ),FRAME)
    # 两瓣之间只有低位相界鞍梁，顶部保留明确双峰轮廓。
    for y in (3,8,13):
        for z in (CZ-10,CZ,CZ+10):
            line((28,y,z),(60,y,z),FRAME)


def room_shell(x0: int, x1: int, z0: int, z1: int, eave: int, ridge: int,
               wall: str, roof: str, floor: str = FLOOR) -> None:
    """构建带连续双坡屋顶和稀疏承台的封闭设备厅。"""
    for x in range(x0, x1 + 1):
        put(x, 0, z0, floor)
        put(x, 0, z1, floor)
    for z in range(z0, z1 + 1):
        put(x0, 0, z, floor)
        put(x1, 0, z, floor)
    mid = (x0 + x1) // 2
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            roof_y = eave + round((ridge - eave) * (1 - abs(x - mid) / max(1, mid - x0)))
            put(x, roof_y, z, roof)
            if roof_y > eave + 3 and x in (mid - 1, mid, mid + 1) and z % 8 == 0:
                put(x, roof_y, z, GLASS, True)
        for x in range(x0, x1):
            left_y = eave + round((ridge - eave) * (1 - abs(x - mid) / max(1, mid - x0)))
            right_y = eave + round((ridge - eave) * (1 - abs(x + 1 - mid) / max(1, mid - x0)))
            for y in range(min(left_y, right_y), max(left_y, right_y) + 1):
                put(x + 1, y, z, roof)
    for y in range(1, eave + 1):
        for x in range(x0, x1 + 1):
            put(x, y, z0, wall)
            put(x, y, z1, wall)
        for z in range(z0, z1 + 1):
            put(x0, y, z, wall)
            put(x1, y, z, wall)
    for x in range(x0 + 2, x1 - 1, 5):
        for z in (z0 + 2, z1 - 2):
            line((x, 1, z), (x, eave, z), FRAME, True)
    for z in range(z0 + 3, z1 - 2, 5):
        line((x0 + 2, 1, z), (x1 - 2, 1, z), FRAME)
    for x in range(x0 + 2, x1 - 2, 8):
        line((x, 1, z0 + 2), (x, 1, z1 - 2), FRAME)


def make_wings() -> None:
    """构建贴合主炉两侧的低矮八角换热舱。"""
    pz = CZ + 2

    def wing(cx: int, hot_side: bool) -> None:
        profile = [(1, 9, 14), (5, 12, 18), (16, 12, 18),
                   (25, 10, 16), (30, 8, 13)]

        def radius(y: int) -> tuple[int, int]:
            for (y0, rx0, rz0), (y1, rx1, rz1) in zip(profile, profile[1:]):
                if y0 <= y <= y1:
                    t = (y - y0) / (y1 - y0)
                    return round(rx0 + (rx1 - rx0) * t), round(rz0 + (rz1 - rz0) * t)
            return profile[0][1:] if y < profile[0][0] else profile[-1][1:]

        for y in range(1, 31):
            rx, rz = radius(y)
            irx, irz = max(2, rx - 2), max(2, rz - 2)
            for x in range(cx - rx, cx + rx + 1):
                for z in range(pz - rz, pz + rz + 1):
                    if oct_contains(cx, pz, rx, rz, x, z) and not oct_contains(cx, pz, irx, irz, x, z):
                        state = FRAME if y in (5,25) else QCV
                        if 9 <= y <= 22 and abs(x-cx)<=5 and abs(z-pz)>=rz-1:
                            state=GLASS
                        put(x,y,z,state)
        for y, rx, rz, state in ((0, 10, 16, FRAME), (3, 11, 17, QCV),
                                 (24, 10, 16, FRAME), (30, 8, 13, POWER)):
            builder.oct_ring(cx, pz, rx, rz, y, state)
        rx, rz = radius(31)
        for x in range(cx - rx, cx + rx + 1):
            for z in range(pz - rz, pz + rz + 1):
                if oct_contains(cx, pz, rx, rz, x, z):
                    put(x,31,z,FLOOR if abs(x-cx)>3 else QCV)

        # 两段连续玻璃观察窗显出封闭换热器内部，不使用密集金属格栅。
        outer_x = 0 if cx < CX else 88
        for y in range(10, 22):
            for z in (*range(pz - 8, pz - 3), *range(pz + 4, pz + 9)):
                put(outer_x, y, z, GLASS, True)
        for z in (pz - 8, pz - 3, pz + 3, pz + 8):
            line((outer_x, 9, z), (outer_x, 23, z), FRAME, True)

        bank_state = VENT if hot_side else COOL
        coil_state = COIL if hot_side else VENT
        for x in range(cx - 7, cx + 8, 4):
            for z in (pz - 5, pz, pz + 5):
                line((x, 7, z), (x, 24, z), bank_state)
                for y in (9, 14, 19, 23):
                    line((x - 1, y, z), (x + 1, y, z), coil_state)
        for x in (cx - 9, cx + 9):
            for z in (pz - 10, pz + 10):
                line((x, 4, z), (x, 27, z), FRAME)
        for x in range(cx - 7, cx + 8, 4):
            for z in (pz - 5, pz, pz + 5):
                line((x, 24, z), (x, 30, z), FRAME)
        for x in (cx - 9, cx + 9):
            line((x, 0, pz), (x, 2, pz), FRAME)

    wing(12, False)
    wing(76, True)


def make_front_compressor() -> None:
    """构建从前端并入主炉收腰处的宽低压缩瓣。"""
    fz = 13
    profile = [(0, 18, 10), (3, 22, 13), (17, 22, 13), (22, 19, 11), (24, 16, 9)]

    def radius(y: int) -> tuple[int, int]:
        for (y0, rx0, rz0), (y1, rx1, rz1) in zip(profile, profile[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / (y1 - y0)
                return round(rx0 + (rx1 - rx0) * t), round(rz0 + (rz1 - rz0) * t)
        return profile[0][1:] if y < profile[0][0] else profile[-1][1:]

    for y in range(1, 25):
        rx, rz = radius(y)
        irx, irz = max(3, rx - 2), max(3, rz - 2)
        for x in range(CX - rx, CX + rx + 1):
            for z in range(fz - rz, fz + rz + 1):
                if oct_contains(CX, fz, rx, rz, x, z) and not oct_contains(CX, fz, irx, irz, x, z):
                    put(x, y, z, POWER if y in (3, 18) else QCV)
    for y, rx, rz, state in ((0, 18, 10, QCV), (3, 22, 13, FRAME),
                             (18, 21, 12, POWER), (23, 18, 10, FRAME)):
        builder.oct_ring(CX, fz, rx, rz, y, state)

    # 两侧窄窗显出压缩瓣内部的进料导流叶片。
    for y in range(8, 20):
        rx, _ = radius(y)
        for side_x in (CX - rx, CX + rx):
            for z in range(fz - 3, fz + 4):
                if oct_contains(CX, fz, rx, radius(y)[1], side_x, z):
                    put(side_x, y, z, GLASS, True)
    for x in (CX - 12, CX - 6, CX + 6, CX + 12):
        line((x, 5, 5), (x, 17, 18), FRAME)
        line((x, 7, 6), (x, 19, 18), PIPE)
        line((x,17,18),(x,24,18),FRAME)

    # 压缩瓣的坡肩与通透顶盖收进双炉前沿。
    for x in range(CX-16,CX+17):
        for z in range(4,23):
            if oct_contains(CX,fz,16,9,x,z):
                put(x,24,z,GLASS if abs(x-CX)<=10 and abs(z-fz)<=5 else QCV,True)
    for x in (CX-12,CX,CX+12):
        line((x,24,6),(x,24,20),FRAME,True)


def make_rear_halls() -> None:
    """两跨不同屋面、条窗和端墙骨架让后场保持轻盈。"""
    for x0,x1,eave,ridge in ((13,41,24,30),(47,77,27,33)):
        room_shell(x0,x1,71,101,eave,ridge,QCV,QCV,QCV)
        line((x0,eave,99),(x1,eave,99),FRAME)
        for y in (4,eave):
            for z in (71,101):
                line((x0,y,z),(x1,y,z),FRAME,True)
            for x in (x0,x1):
                line((x,y,71),(x,y,101),FRAME,True)
        for x in (x0,x1):
            for z in (71,79,87,95,101):
                line((x,1,z),(x,eave,z),FRAME,True)
            for z in range(73,100):
                for y in range(9,eave-3):
                    if z%8 not in (0,7):
                        put(x,y,z,GLASS,True)
        for z in (71,101):
            for x in range(x0+2,x1-1):
                for y in range(14,eave-2):
                    put(x,y,z,GLASS,True)
            for x in range(x0+3,x1,7):
                line((x,5,z),(x,eave,z),FRAME,True)
        # 三条长天窗与屋面脊梁相间，无大面积深色屋顶。
        mid=(x0+x1)//2
        for x in range(x0+2,x1-1):
            roof_y=eave+round((ridge-eave)*(1-abs(x-mid)/(mid-x0)))
            for z in range(73,100):
                if abs(x-mid) in (3,4,5,8,9) and z%9 not in (0,1):
                    put(x,roof_y,z,REINFORCED_GLASS,True)
                if x in (x0+1,mid,x1-1):
                    put(x,roof_y,z,FLOOR,True)
                elif abs(x-mid) in (6,7,10,11):
                    put(x,roof_y,z,FRAME,True)
        for z in (71,80,90,101):
            for x in range(x0,x1+1):
                roof_y=eave+round((ridge-eave)*(1-abs(x-mid)/(mid-x0)))
                put(x,roof_y,z,FRAME,True)

    # 西跨是低位固相过滤床，东跨是三列余能回收转子。
    for cx in (21,28,35):
        line((cx,7,74),(cx,7,98),FILTER)
        for z in (75,82,89,96):
            for x in range(cx-2,cx+3):
                line((x,7,z),(x,18,z),FILTER if x in (cx-2,cx+2) else POWER)
            line((cx-2,19,z),(cx+2,19,z),FRAME)
            line((cx,1,z),(cx,7,z),FRAME)
    for cx in (53,62,71):
        line((cx,12,74),(cx,12,98),GEAR)
        for z in (75,96):
            line((cx,6,z),(cx,12,z),FRAME)
        for z in (75,82,89,96):
            for x in range(cx-3,cx+4):
                for y in range(7,18):
                    if abs(x-cx)+abs(y-12) in (4,5):
                        put(x,y,z,COIL if y in (10,14) else POWER)
            line((cx-3,6,z),(cx+3,6,z),FRAME)
            for x in (cx-3,cx+3):
                line((x,1,z),(x,12,z),FRAME)
    for x in range(22,34):
        for y in range(5,14):
            put(x,y,101,FILTER,True)
    for x in range(58,67):
        for y in range(5,14):
            put(x,y,101,QCV,True)


def make_couplings() -> None:
    # 前端进气喉道藏入压缩瓣肩部，封住压缩壳与左炉瓣间的短距离。
    for z in range(20,30):
        for x in range(25,32):
            for y in range(10,19):
                if x in (25,31) or y in (10,18):
                    put(x,y,z,QCV if y!=18 else POWER)
    # 两座通向后场的实体短颈，路线从内部穿过，外面只看见整块设备壳。
    for cx,route_y in ((28,20),(60,18)):
        for z in range(61,74):
            for x in range(cx-4,cx+5):
                for y in range(4,route_y+5):
                    if x in (cx-4,cx+4) or y in (4,route_y+4):
                        put(x,y,z,FRAME if y==route_y+4 else QCV)
            for x in (cx-4,cx+4):
                for y in range(12,route_y+2):
                    if z in (66,67,68,69):
                        put(x,y,z,GLASS,True)
        for z in (65,70):
            line((cx-4,4,z),(cx+4,4,z),FRAME)
    # 贴体换热舱与炉瓣共享连续承台，连接均位于实体壳体内部。
    for x0,x1 in ((10,28),(60,78)):
        for z in (36,47,58):
            line((x0,3,z),(x1,3,z),FRAME)
    for x in (28,60):
        line((x,3,22),(x,3,33),FRAME)

def build() -> dict:
    builder.base.CELLS.clear()
    make_phase_vessel()
    make_wings()
    make_front_compressor()
    make_rear_halls()
    make_couplings()

    # 以同材框边收口预定的主炉穿壳工艺喉口。
    front_throat_z = CZ - profile_at(14)[1]
    for pos, axis in (
        ((28, 14, front_throat_z), 'z'),
        ((60, 18, CZ + profile_at(18)[1]), 'z'),
        ((28, 20, CZ + profile_at(20)[1]), 'z'),
        ((28 - profile_at(15)[0], 15, CZ + 2), 'x'),
        ((60 + profile_at(15)[0], 15, CZ + 2), 'x'),
    ):
        x, y, z = pos
        if axis == 'z':
            frame_points = ((x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z))
        else:
            frame_points = ((x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1))
        for fx, fy, fz in frame_points:
            put(fx, fy, fz, FRAME, True)

    ports = [
        {'id': 'G-IN', 'pos': [CX + 9, 14, CORE_FRONT], 'face': 'north',
         'surface_state': QCV, 'purpose': '受控气态崩坏能输入候选'},
        {'id': 'EU-IN', 'pos': [77, 39, CZ], 'face': 'east',
         'surface_state': QCV, 'purpose': '相变装置驱动能量输入候选'},
        {'id': 'C-IN', 'pos': [0, 15, CZ + 2], 'face': 'west',
         'surface_state': QCV, 'purpose': '冷端循环介质输入候选'},
        {'id': 'SOLID-OUT', 'pos': [27, 8, D - 1], 'face': 'south',
         'surface_state': FILTER, 'purpose': '固态析出物输出候选'},
        {'id': 'EU-OUT', 'pos': [62, 8, D - 1], 'face': 'south',
         'surface_state': QCV, 'purpose': '余能回收输出候选'},
        {'id': 'HEAT-OUT', 'pos': [W - 1, 15, CZ + 2], 'face': 'east',
         'surface_state': QCV, 'purpose': '热端余热输出候选'},
    ]
    for port in ports:
        put(*port['pos'], PORT, True)

    routes = [
        ('气态进料至相变炉心', PIPE, [[CX + 9, 14, 1], [CX + 9, 14, 14], [28, 14, 14], [28, 14, CZ]]),
        ('驱动能量至炉心', POWER, [[76, 39, CZ], [60, 39, CZ], [60, 22, CZ]]),
        ('冷端循环至换热鳍翼', CHEM, [[1, 15, CZ + 2], [28, 15, CZ + 2]]),
        ('相变固态至过滤锁仓', FILTER, [[28, 20, CZ], [28, 20, 76], [27, 20, 76], [27, 8, 76], [27, 8, D - 2]]),
        ('余能汇入三跨回收厅', GEAR, [[60, 18, CZ], [60, 18, 78], [62, 18, 78], [62, 8, 78], [62, 8, D - 2]]),
        ('热端循环至东侧换热翼', PIPE, [[60, 15, CZ + 2], [76, 15, CZ + 2], [W - 2, 15, CZ + 2]]),
    ]
    links = []
    port_binding = {
        '气态进料至相变炉心': {'from_port': 'G-IN'},
        '驱动能量至炉心': {'from_port': 'EU-IN'},
        '冷端循环至换热鳍翼': {'from_port': 'C-IN'},
        '相变固态至过滤锁仓': {'to_port': 'SOLID-OUT'},
        '余能汇入三跨回收厅': {'to_port': 'EU-OUT'},
        '热端循环至东侧换热翼': {'to_port': 'HEAT-OUT'},
    }
    for name, state, points in routes:
        for a, b in zip(points, points[1:]):
            line(tuple(a), tuple(b), state, True)
        links.append({'name': name, 'state': state, 'points': points, **port_binding[name]})

    # 主控替换正面承力壳中线的一格，保持整机宽度居中。
    controller = [CX, 8, CORE_FRONT]
    put(*controller, DIAMOND, True)

    zones = [
        {'name': '横向双瓣相界炉心', 'description': '两个穹肩压力瓣在宽度方向并列，共享低位鞍梁；亮色环箍围住青玻璃相界腔，内部三层锻环约束紫色相变晶核。', 'min': [11, 2, 25], 'max': [77, 56, 65]},
        {'name': '前段气态压缩瓣', 'description': '低位压缩壳从整机前端并入主炉腰，气态候选接口和中线控制器直接替换同一体量的外壳方块。', 'min': [22, 0, 0], 'max': [66, 24, 26]},
        {'name': '西侧冷端换热瓣', 'description': '贴体八角舱内布置层叠冷端鳍片，观察窗与冷媒占位均在连续侧壳上。', 'min': [0, 0, 29], 'max': [24, 31, 65]},
        {'name': '东侧热端换热瓣', 'description': '对称外壳内收纳热端换热器，端口平齐落在舱体外侧面。', 'min': [64, 0, 29], 'max': [88, 31, 65]},
        {'name': '后段析出锁仓', 'description': '固相过滤床位于后场西跨，连续条窗与屋面天窗显出过滤设备，接口齐平嵌在后墙锁仓壳内。', 'min': [13, 0, rear_z(60)], 'max': [41, 30, rear_z(90)]},
        {'name': '后段余能回收厅', 'description': '三列回收转子位于后场东跨，独立封闭短颈接入右瓣；结构表达用途，不代表净能或配方验证。', 'min': [47, 0, rear_z(60)], 'max': [77, 33, rear_z(90)]},
    ]
    blocks = [{'pos': list(pos), 'state': state}
              for pos, state in sorted(builder.base.CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    return {
        'key': 'i23',
        'name': NAME,
        'title': '崩坏能相变释能机',
        'candidate_version': '双瓣相界锻炉 V8・待审',
        'size': [W, H, D],
        'blocks': blocks,
        'block_count': len(blocks),
        'controller': controller,
        'controller_face': 'north',
        'ports': ports,
        'paths': [],
        'links': links,
        'zones': zones,
        'target_voltage_status': '按负责人决定采用《多方块结构电压映射提案 V1》对应的 QCV / V06；该映射只作为结构制作依据，Controller tier、Pattern、配方和实机运行仍待验收。',
    }


def report_page(data: dict, verification: dict) -> str:
    page = ORIGINAL_REPORT_PAGE(data, verification)
    replacements = {
        'I23 崩坏能相变释能机 · V6': 'I23 崩坏能相变释能机 · V8',
        '建筑候选V6': '全新建筑候选V8',
        '待审候选 V6': '重新设计候选 V8',
        '相变舱原位接口': '双瓣相界锻炉',
        '错层相变舱作为主设备，双端换热、结晶过滤与三列计量透平按实际工艺分区展开；六个接口嵌在各设备自身的外壳表面。':
            '低重心双瓣QCV相变炉心统领整厂；左右贴体换热舱形成冷、热端对照，后场分设固相过滤锁仓与三跨余能回收厅。六个接口占位齐平嵌入对应设备壳体。',
        '中央相变舱由分段QCV承力环、观察壳与交叉约束架构成。前场缓冲筒和错层压缩塔接入主舱；两侧分置冷端换热与热端排热设备；后场设置结晶过滤、固态缓冲和透平回收厅。底座为各设备独立承台与检修连接梁。':
            '主设备由横向并列的两座穹肩压力瓣构成；两个独立肩冠之间保留凹谷，低位鞍梁将双瓣连成整体。青玻璃构成相界舱皮肤，亮色锻环与紫色晶核从外部可见。两侧低位换热舱、前端压缩瓣和后场天窗厂房逐级降低，控制器与六个接口齐平替换其设备外壳。',
        '主控在宽度中线，替换中央舱正面连续QCV承力环带的一格；接口分别替换缓冲筒、压缩机壳、冷端观察壳、过滤压床、透平厅观察壳和热端换热壳上的外表面方块。':
            '主控位于整机宽度中线，替换前端压缩壳的一格；接口分别齐平替换进料壳、炉心壳、冷端翼舱、过滤锁仓、回收厅和热端翼舱的设备表面方块。',
        'QCV承力环带': 'QCV承力外壳',
        '六个接口': '六个候选接口占位',
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    page = page.replace('六个候选接口占位占位齐平', '六个候选接口齐平')
    page = page.replace('I23 V6', 'I23 V8').replace('I23 V7', 'I23 V8')
    page = page.replace('V6 实际材质等轴预览', 'V8 实际材质等轴预览')
    page = page.replace('V6 三维评审', 'V8 三维评审')
    page = page.replace('V6 按实际方块高度生成的设备平面图', 'V8 按实际方块高度生成的设备平面图')
    page = page.replace('最高方块为Y=10',f'最高方块为Y={-60+H-1}')
    return page


def review_page(data: dict, verification: dict) -> str:
    page = ORIGINAL_REVIEW_PAGE(data, verification)
    for old, new in (('V6', 'V8'), ('V7', 'V8'), ('相变舱原位接口', '双瓣相界锻炉')):
        page = page.replace(old, new)
    return page


def relabel_preview(path: Path, data: dict) -> None:
    ORIGINAL_RELABEL_PREVIEW(path, data)
    image = builder.Image.open(path).convert('RGB')
    draw = builder.ImageDraw.Draw(image)
    font = builder.report_font(20)
    draw.rectangle((0, 0, image.width, 42), fill=(11, 17, 25))
    draw.text((18, 8), 'I23 崩坏能相变释能机 · 双瓣相界锻炉 V8', font=font, fill=(234, 243, 246))
    draw.rectangle((0, image.height - 39, image.width, image.height), fill=(11, 17, 25))
    draw.text((18, image.height - 34),
              f'{W} × {D} × {H} (宽 × 长 × 高)  |  6个候选接口  |  QCV / V06',
              font=font, fill=(178, 208, 210))
    image.save(path)


def block_color(state: str) -> tuple[int, int, int]:
    overrides = {GLASS:(97,163,181),REINFORCED_GLASS:(116,150,178),
                 PHASE_GLASS:(137,92,176),CRYSTAL:(171,125,207),LIGHT:(200,234,222)}
    return overrides.get(state,ORIGINAL_BLOCK_COLOR(state))


def render_plan(data: dict, out: Path) -> None:
    """按本版尺寸缩放，不沿用旧候选固定宽高导致裁切。"""
    image=builder.Image.new('RGB',(1600,1100),'#14212d')
    draw=builder.ImageDraw.Draw(image)
    font,small=builder.report_font(30),builder.report_font(17)
    scale,left,top=8,64,140
    draw.text((48,35),'I23 · 横向双瓣相界锻炉平面与接口位置',font=font,fill='#e5edf3')
    tops={}
    for block in data['blocks']:
        x,y,z=block['pos']
        if (x,z) not in tops or y>=tops[(x,z)][0]:
            tops[x,z]=(y,block['state'])
    for (x,z),(y,state) in tops.items():
        color=tuple(min(255,c+min(22,y//4)) for c in block_color(state))
        px,pz=left+x*scale,top+z*scale
        draw.rectangle((px,pz,px+scale-1,pz+scale-1),fill=color)
    draw.rectangle((left-1,top-1,left+W*scale,top+D*scale),outline='#8798a5',width=2)
    draw.text((left,top-32),'北 / 前端压缩瓣与居中主控',font=small,fill='#c4d0d8')
    draw.text((left,top+D*scale+12),'南 / 后场过滤锁仓与余能回收厅',font=small,fill='#c4d0d8')
    legend_x,legend_y=850,145
    draw.text((legend_x,legend_y),'设备壳上的齐平接口',font=builder.report_font(24),fill='#f0d4a0')
    for i,port in enumerate(data['ports']):
        x,_,z=port['pos'];px,pz=left+x*scale+scale//2,top+z*scale+scale//2
        draw.ellipse((px-5,pz-5,px+5,pz+5),fill='#f4c66c',outline='#17212a',width=1)
        ly=legend_y+44+i*62
        draw.text((legend_x,ly),f"{port['id']} · {port['purpose']}",font=small,fill='#e5edf3')
        draw.text((legend_x,ly+23),f"坐标 {port['pos']} · {port['face']}",font=small,fill='#aebfc8')
    ly=590
    draw.text((legend_x,ly),'89 × 102 × 57（宽 × 长 × 高）',font=builder.report_font(22),fill='#e5edf3')
    draw.text((legend_x,ly+40),'主控 X=44，即整机宽度第45格',font=small,fill='#c7d3d9')
    legend=[(QCV,'QCV承力壳'),(FLOOR,'亮色肩壳'),(GLASS,'青色相界观察壳'),
            (FRAME,'承力骨架'),(CRYSTAL,'相变晶核'),(FILTER,'过滤压床')]
    for i,(state,label) in enumerate(legend):
        yy=ly+90+i*36
        draw.rectangle((legend_x,yy,legend_x+24,yy+24),fill=block_color(state))
        draw.text((legend_x+36,yy+1),label,font=small,fill='#d5dfe4')
    image.save(out/'俯视布局.png')


def render_controller_detail(data: dict, out: Path) -> None:
    ORIGINAL_RENDER_CONTROLLER(data,out)
    path=out/'主控正立面.png'
    image=builder.Image.open(path).convert('RGB');draw=builder.ImageDraw.Draw(image)
    draw.rectangle((28,28,850,76),fill='#14212d')
    draw.text((38,36),'主控 · 前端压缩瓣原位壳体',font=builder.report_font(28),fill='#e5edf3')
    draw.rectangle((95,756,875,789),fill='#14212d')
    draw.text((105,762),'主控占整机第45格，替换连续QCV壳体；正面留空。',font=builder.report_font(17),fill='#d6e0e5')
    image.save(path)


def audit(data: dict) -> dict:
    result=ORIGINAL_AUDIT(data)
    result['checks']=[item.replace('承力环带','压缩瓣壳体') for item in result.get('checks',[])]
    allowed={QCV,PORT}
    project_states={block['state'] for block in data['blocks'] if block['state'].startswith('hk3gtl:')}
    if not project_states<=allowed:
        raise ValueError(f'使用了暂禁的项目新增方块：{project_states-allowed}')
    result['project_added_block_scope']={
        'passed':True,'allowed_project_states':sorted(allowed),'actual_project_states':sorted(project_states),
        'basis':'项目新增方块仅16电压机壳及工业方块可用；本候选仅使用QCV机壳及工业接口占位。'}
    result['coil_source_note']='titansteel线圈模型与材质读取原整合包GregTech-Leisure-1.4.5.2/kubejs/assets/kubejs；不是HK3GTL项目新增方块。'
    return result


def reference_records() -> list[dict]:
    return [
        {'series': 'I01-I18', 'path': 'deliveries/I01-I18_控制器居中融合修订_V2_20261023',
         'basis': '已确认结构的主体层级、功能分区、居中主控与设备承载接口；读取结构文件和检查资料。'},
        {'series': 'I18', 'path': 'deliveries/I18_崩坏能燃料棒封装阵列_蓝脊热室与并列封装线_V1_HBV_20261022',
         'basis': '连续屋脊、完整厂房皮肤和清楚的主次翼关系。'},
        {'series': 'I22', 'path': 'deliveries/多方块确认归档/20261024_010011_626135_batch-07_01of05_I22_WSV_已确认',
         'basis': '用户确认的近期结构：单一强地标、多座有实体体量的功能厂房、俯视可读分区；不复制其反应堆主题。'},
        {'series': 'I23职责与尺寸', 'path': 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html',
         'basis': 'I23正式名称及33×37×35（宽×长×高）最低占地。'},
        {'series': 'I23职责边界', 'path': 'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json',
         'basis': '受控气态到固态相变、余能/余热回收与不可净产能边界。'},
        {'series': 'I23电压映射', 'path': 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html',
         'basis': 'QCV/V06主体识别机壳；执行配方和Pattern仍待验收。'},
    ]


def finalize_package() -> dict:
    manifest_path = OUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['candidate_version'] = '双瓣相界锻炉 V8・待审'
    manifest['supersedes'] = '为用户要求重设计提出的新候选；I23 V6 已确认归档保持不变'
    manifest['supersedes_reason'] = '将主体重构为低重心双瓣相变炉、贴体换热舱、后置过滤锁仓与三跨回收厅；不修改V6确认归档。'
    manifest['redesign_basis'] = '本轮使用 I01-I22 有效结构/审阅资料及内测5职责、尺寸与QCV/V06映射；未使用I23早期旧候选贴图作为设计输入。'
    manifest['candidate_approved'] = False
    manifest['target_voltage'] = 'QCV'
    manifest['target_voltage_status'] = '结构目标采用提案映射 QCV/V06；实际 Pattern、Controller tier、配方及游戏运行未验收。'
    manifest['claim_boundary'] = '只交付待审建筑候选；接口为无功能占位块，路线是空间表达，未声称配方、能量结算或游戏运行通过。'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    verification_path = OUT / 'verification.json'
    verification = json.loads(verification_path.read_text(encoding='utf-8'))
    file_hashes = {p.relative_to(OUT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(OUT.rglob('*'))
                   if p.is_file() and p.name != 'verification.json'}
    verification['files_sha256_before_verification'] = file_hashes
    verification['design_basis'] = reference_records()
    verification['viewer_material_note'] = '本版渲染从当前项目/实例方块模型与纹理生成；未把I23旧候选图像用作设计输入。'
    verification_path.write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    zip_path = OUT.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError('候选 ZIP CRC 校验失败。')
        for relative, expected in file_hashes.items():
            entry = next((n for n in archive.namelist() if n.endswith('/' + relative)), None)
            if entry is None or hashlib.sha256(archive.read(entry)).hexdigest() != expected:
                raise ValueError(f'候选 ZIP 文件校验失败：{relative}')
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    zip_path.with_suffix('.zip.sha256').write_text(digest + '\n', encoding='ascii')
    return {'zip': str(zip_path), 'zip_sha256': digest,
            'files':len(file_hashes)+1,'hashed_files_excluding_verification':len(file_hashes)}


def main() -> None:
    builder.__file__ = str(Path(__file__).resolve())
    builder.OUT = OUT
    builder.NAME = NAME
    builder.W, builder.H, builder.D = W, H, D
    builder.CX, builder.CZ = CX, CZ
    builder.base.OUT = OUT
    builder.base.NAME = NAME
    builder.base.W, builder.base.H, builder.base.D = W, H, D
    builder.build = build
    builder.make_report_page = report_page
    builder.make_review_page = review_page
    builder.relabel_preview = relabel_preview
    builder.block_color = block_color
    builder.render_plan = render_plan
    builder.render_controller_detail = render_controller_detail
    builder.audit = audit
    builder.reference_records = reference_records
    builder.main()
    package = finalize_package()
    print(json.dumps(package, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
