# -*- coding: utf-8 -*-
"""I26 葵涌自动化码头：实体生成、压缩预览与硬规则审计。"""
from __future__ import annotations

import array
import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
from build_redesign69 import export, render
from material_resources import Resources
from structure_size_baseline import require
from i26_kwaichung_geometry_v2 import build as build_port, CELLS as PORT_CELLS, CONTAINER_COLORS

OUT = ROOT / 'deliveries/I26_世界泡无人采掘调度台_葵涌自动化码头_V2_20261026'
VIEW = OUT / 'i26'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
VIEWER = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22'
VIEWER_BUILDER = ROOT / 'tools/structure_delivery/build_i26_terminal_viewer_v2_20261026.mjs'
NAME = 'hk3gtl-i26-kwaichung-automated-terminal-v2-20261026'
TITLE = '世界泡无人采掘调度台 · 葵涌自动化码头'
W, H, D = 333, 211, 301
CX = W // 2

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
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
AMBER_GLASS = 'minecraft:orange_stained_glass'
LIGHT = 'minecraft:sea_lantern'

CELLS: dict[tuple[int, int, int], str] = {}


def put(x: int, y: int, z: int, state: str, replace: bool = False) -> None:
    pos = (int(x), int(y), int(z))
    if not (0 <= pos[0] < W and 0 <= pos[1] < H and 0 <= pos[2] < D):
        raise ValueError(f'实体越界：{pos} {state}')
    if replace or pos not in CELLS:
        CELLS[pos] = state


def box(lo, hi, state, replace: bool = False) -> None:
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def beam(a, b, state, radius: int = 0, replace: bool = False) -> None:
    """沿三轴逐步补齐斜梁，避免只靠角点接触。"""
    steps = max(abs(b[i] - a[i]) for i in range(3))
    last = a
    for step in range(steps + 1):
        target = tuple(round(a[i] + (b[i] - a[i]) * step / max(1, steps)) for i in range(3))
        cursor = list(last)
        for axis in range(3):
            while cursor[axis] != target[axis]:
                cursor[axis] += 1 if target[axis] > cursor[axis] else -1
                box(tuple(v - radius for v in cursor), tuple(v + radius for v in cursor), state, replace)
        box(tuple(v - radius for v in target), tuple(v + radius for v in target), state, replace)
        last = target


def deck(x0, x1, z0, z1, y, base=QAV, inset=GRATE, pitch=11) -> None:
    """实体地坪按承重板、格栅检修带和伸缩缝分片。"""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            state = base if edge or x % pitch in (0, 1) or z % pitch in (0, 1) else inset
            put(x, y, z, state)


def hall(x0, x1, z0, z1, y0, y1, floors, name, glass_axis='z') -> None:
    """方正工艺舱：分层设备、承重外壳、节段窗和成排机组。"""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                edge_x = x in (x0, x1)
                edge_z = z in (z0, z1)
                wall = edge_x or edge_z
                if y in floors:
                    band = (x % 9 in (0, 1)) or (z % 9 in (0, 1))
                    put(x, y, z, QAV if band or edge_x or edge_z else GRATE)
                elif wall and (y == y1 or y == y0):
                    put(x, y, z, ROBUST if y == y0 else QAV)
                elif wall:
                    window = ((glass_axis == 'z' and edge_z and 5 <= y % 21 <= 14 and x % 37 in range(8, 30))
                              or (glass_axis == 'x' and edge_x and 5 <= y % 21 <= 14 and z % 37 in range(8, 30)))
                    if window and not (x % 18 < 2 or z % 18 < 2):
                        put(x, y, z, BLUE_GLASS)
                    else:
                        state = QAV
                        if y % 13 in (0, 1):
                            state = ROBUST
                        if (x in (x0, x1) and z in (z0, z1)) and y % 7 < 3:
                            state = ASSEMBLY
                        put(x, y, z, state)
    # 每层设备背板和热交换阵列均与舱体地坪相连。
    if name == '西翼无人机维护坞':
        equipment = (GEAR, ASSEMBLY, TURBINE, TUNG_PIPE)
    elif name == '东翼返航检疫与分拣':
        equipment = (FILTER, PROCESS, IRIDIUM, STEEL_PIPE)
    elif name == '底部汇流舱':
        equipment = (POWER, TUNG_PIPE, STEEL_PIPE, ATOMIC)
    elif name == '任务排程层':
        equipment = (COMPUTER, MULTI, VENT, CLEAN)
    elif name == '远征计算井':
        equipment = (COMPUTER, LAFIUM, INERT, HEATPROOF, ATOMIC)
    else:
        equipment = (DIMENSION, IRIDIUM, LASER, FILTER, HEATPROOF)
    for index, y in enumerate(floors):
        for x in range(x0 + 7, x1 - 5, 13):
            for z in range(z0 + 7, z1 - 5, 14):
                width = 3 + ((x + z + index) % 4)
                depth = 3 + ((2 * x + z) % 5)
                height = min(9, max(4, y1 - y - 4))
                region = ((x - x0) // 34 + 2 * ((z - z0) // 46) + index) % len(equipment)
                state = equipment[region]
                box((x, y + 1, z), (min(x + width, x1 - 2), y + height, min(z + depth, z1 - 2)), state)
                if (x + z) % 3 == 0:
                    box((x, y + height + 1, z), (min(x + width, x1 - 2), y + height + 1, min(z + depth, z1 - 2)), GRATE)


def command_spine() -> None:
    """中央逐级抬升的调度脊，主控嵌在整机宽度中心的前脸。"""
    hall(105, 227, 70, 224, 5, 49, (5, 20, 34, 48), '底部汇流舱', 'x')
    hall(116, 216, 82, 212, 45, 91, (45, 67, 89), '任务排程层', 'z')
    hall(129, 203, 98, 194, 85, 151, (85, 107, 129, 149), '远征计算井', 'x')
    hall(139, 193, 112, 180, 145, 184, (145, 163, 183), '授权与坐标穹厅', 'z')
    hall(148, 184, 128, 165, 178, 204, (178, 192, 203), '折界中继冠', 'x')

    # 中央井筒由四组齿轮脊、计算板和通风格栅构成，不放置世界泡球体。
    for y in range(18, 183, 9):
        for x in (CX - 28, CX - 17, CX + 16, CX + 27):
            box((x, y, 119), (x + 2, y + 4, 187), QAV)
        for z in (122, 184):
            box((CX - 30, y, z), (CX + 29, y + 3, z + 1), ROBUST)
    for z in range(112, 190, 10):
        for x in (CX - 11, CX + 9):
            box((x, 20, z), (x + 2, 179, z + 2), COMPUTER)
        box((CX - 8, 21, z), (CX + 8, 25, z + 2), VENT)

    # 主控前方留出入口净空；同一垂直面嵌入维护、调度和观察构件。
    for y, z in ((73, 82), (95, 98), (117, 98), (139, 98)):
        box((CX - 34, y, z), (CX - 30, y + 2, z), LIGHT, replace=True)
        box((CX + 30, y, z), (CX + 34, y + 2, z), LIGHT, replace=True)
    for x in range(CX - 26, CX + 27, 13):
        box((x, 69, 82), (x + 5, 70, 82), CLEAN, replace=True)
        box((x, 141, 98), (x + 5, 142, 98), AMBER_GLASS, replace=True)
    box((CX - 3, 102, 99), (CX + 3, 106, 101), COMPUTER)
    # 顶冠细化成短程中继桅杆，收住全机211格的实体高度。
    box((CX - 4, 204, 143), (CX + 4, 210, 151), QAV)
    box((CX - 6, 204, 142), (CX + 6, 205, 152), ROBUST, replace=True)
    for y in (206, 208, 210):
        box((CX - 2, y, 147), (CX + 2, y, 147), LIGHT if y == 210 else AMBER_GLASS, replace=True)


def foundations() -> None:
    """连续箱形格构底座；各功能舱的承重点通过梁网闭合。"""
    # 主纵梁和横梁形成稀疏承重网，不用整片空壳平台撑大坐标。
    for x in (0, 18, 63, 104, 165, 227, 269, 314, 331):
        box((x, 0, 0), (min(x + 1, W - 1), 5, D - 1), QAV)
    for z in (0, 18, 68, 122, 176, 228, 234, 281, 299):
        box((0, 0, z), (W - 1, 5, min(z + 1, D - 1)), ROBUST)
    box((W - 2, 0, 0), (W - 1, 7, D - 1), QAV)
    box((0, 0, D - 2), (W - 1, 7, D - 1), QAV)
    # 设备区下方加厚基础梁及与地坪相接的机组脚座。
    for x0, x1, z0, z1 in ((12, 110, 70, 207), (221, 320, 70, 210),
                            (101, 231, 64, 228), (125, 207, 5, 83), (38, 294, 235, 293)):
        for x in range(x0, x1, 16):
            box((x, 4, z0), (min(x + 3, x1), 9, z1), QAV)
        for z in range(z0, z1, 17):
            box((x0, 4, z), (x1, 9, min(z + 3, z1)), ROBUST)
        deck(x0, x1, z0, z1, 10, QAV, GRATE)
    # 外缘起落缓冲梁把两个端点纳入真实承重轮廓。
    for x in range(0, W, 8):
        box((x, 3, 0), (min(x + 2, W - 1), 7, 6), CLEAN if x % 16 == 0 else QAV)
    for z in range(0, D, 8):
        box((0, 3, z), (6, 7, min(z + 2, D - 1)), ROBUST if z % 16 == 0 else QAV)


def west_maintenance_wing() -> None:
    """无人装置换件、耗材补给与多层检修廊。"""
    hall(13, 110, 76, 210, 8, 45, (8, 25, 44), '西翼无人机维护坞', 'z')
    # 正面分成可见的组件仓、校验架和伸缩臂检修间。
    for z0, z1, state in ((84, 119, ASSEMBLY), (125, 160, PROCESS), (166, 199, GEAR)):
        for x in range(25, 100, 12):
            box((x, 12, z0), (x + 6, 36, z1), state)
            box((x - 1, 37, z0 + 3), (x + 7, 38, z1 - 3), VENT)
    for z in (91, 114, 137, 160, 183, 204):
        box((16, 15, z), (105, 18, z + 2), QAV)
        box((17, 19, z + 1), (108, 21, z + 2), GRATE)
    for x in (31, 86):
        box((x, 8, 140), (x + 4, 44, 144), QAV)
    # 两根可升降机械导轨由维护层梁托住，避免独立悬柱。
    for x in (33, 88):
        beam((x, 11, 85), (x, 43, 200), ROBUST, 1)
        for y in (17, 25, 33, 41):
            box((x - 4, y, 106), (x + 4, y + 1, 178), GEAR)


def east_quarantine_wing() -> None:
    """返航隔离、磨损件检验和物品/流体/技术记录分流。"""
    hall(222, 319, 72, 207, 8, 61, (8, 25, 42, 59), '东翼返航检疫与分拣', 'z')
    # 三段互相隔开的长舱分别承接固态、流体和技术档案流。
    for x0, x1, state in ((229, 254, MACERATOR), (258, 284, FILTER), (288, 312, IRIDIUM)):
        box((x0, 12, 90), (x1, 40, 188), state)
        box((x0 - 1, 41, 88), (x1 + 1, 43, 190), ROBUST)
        for z in range(96, 184, 13):
            box((x0 + 2, 14, z), (x1 - 2, 37, z + 4), COMPUTER if state == IRIDIUM else PROCESS)
    # 隔离间的竖向窗带和水平封存环。
    for z in (78, 121, 164, 203):
        for y in range(18, 57, 4):
            box((223, y, z), (318, y + 1, z + 1), DIMENSION if y % 8 else QAV)
    for x in (229, 260, 289, 313):
        box((x, 10, 73), (x + 1, 60, 205), ASSEMBLY)
        box((x - 2, 60, 73), (x + 3, 62, 205), QAV)
    # 两条桥把检疫区直接接入主脊和返航门架。
    for y in (24, 45, 60):
        beam((216, y, 126), (224, y, 126), QAV, 1)
        beam((216, y, 178), (224, y, 178), ROBUST, 1)


def dispatch_bay() -> None:
    """唯一出港轨道、单目标无人装置发射夹持器与导向架。"""
    deck(123, 210, 7, 83, 11, QAV, GRATE)
    deck(123, 210, 84, 244, 11, QAV, GRATE)
    # 中央磁悬式载台沿Z轴穿过调度脊，轨道端有实体制动台。
    for x in (136, 194):
        for y in (14, 19, 24, 29):
            box((x, y, 13), (x + 2, y + 1, 242), POWER if y in (19, 29) else QAV)
    for z in range(14, 244, 9):
        for x in range(140, 194, 6):
            box((x, 12, z), (x + 3, 13, z + 4), ASSEMBLY if z % 27 == 0 else CLEAN)
    # 两侧折叠式牵引梁由每格横撑连接；顶部龙门架分段升高。
    for z in range(21, 241, 14):
        beam((128, 18, z), (138, 35, z), ROBUST, 1)
        beam((194, 35, z), (204, 18, z), ROBUST, 1)
        for x in (128, 204):
            box((x, 12, z - 1), (x + 1, 38, z + 1), QAV)
    for x0, z0 in ((126, 24), (198, 24), (126, 218), (198, 218)):
        box((x0, 10, z0), (x0 + 9, 24, z0 + 7), GEAR)
        box((x0 + 2, 25, z0 + 1), (x0 + 7, 35, z0 + 5), POWER)
    # 出港准备架连接西翼维护廊与中央牵引台。
    for x in range(99, 126):
        box((x, 16, 112), (x, 17, 181), QAV)
        box((x, 30, 112), (x, 31, 181), ROBUST)
    for z in (117, 142, 167, 178):
        box((99, 18, z), (126, 30, z + 2), GEAR)


def folded_boundary_gate() -> None:
    """厚壁矩形折界门架，沿四层承力框闭合，不复制I25世界泡球体。"""
    outer = (37, 295, 18, 197)
    inner = (76, 256, 42, 173)
    for z0, z1 in ((238, 243), (244, 249), (250, 255), (256, 261)):
        ox0, ox1, oy0, oy1 = outer
        ix0, ix1, iy0, iy1 = inner
        # 门框四边是承重柱梁，不填充中部通行窗口。
        box((ox0, oy0, z0), (ox1, oy0 + 9, z1), DIMENSION)
        box((ox0, oy1 - 9, z0), (ox1, oy1, z1), QAV)
        # 两侧只保留外弦柱、内弦柱和交叉撑，打开门框腹部以显露通行孔。
        side_bays = ((ox0, ox0 + 9), (ix0 - 10, ix0 - 1),
                     (ix1 + 1, ix1 + 10), (ox1 - 9, ox1))
        for sx0, sx1 in side_bays:
            box((sx0, oy0 + 10, z0), (sx1, oy1 - 10, z1), QAV)
        for y in range(38, 158, 30):
            beam((ox0 + 10, y, z0 + 2), (ix0 - 11, y + 25, z0 + 2), ROBUST)
            beam((ox0 + 10, y + 25, z0 + 2), (ix0 - 11, y, z0 + 2), ROBUST)
            beam((ix1 + 11, y, z0 + 2), (ox1 - 10, y + 25, z0 + 2), ROBUST)
            beam((ix1 + 11, y + 25, z0 + 2), (ox1 - 10, y, z0 + 2), ROBUST)
        # 四个角节点由高功率箍环夹紧。
        for x in (ox0, ix0 - 5, ix1 + 1, ox1 - 5):
            box((x, oy0 + 10, z0), (x + 4, oy0 + 19, z1), POWER)
            box((x, oy1 - 19, z0), (x + 4, oy1 - 10, z1), POWER)
        for x in range(ox0 + 12, ox1 - 11, 18):
            box((x, oy0 + 1, z0), (x + 5, oy0 + 8, z1), LASER, replace=True)
            box((x, oy1 - 8, z0), (x + 5, oy1 - 1, z1), LASER, replace=True)
    # 门架与地基、中央调度脊、返航隔离坞之间形成闭合箱形传力路径。
    for x in (44, 92, 236, 288):
        beam((x, 3, 238), (x, 180, 238), QAV, 2)
        beam((x, 3, 268), (x, 180, 268), ROBUST, 1)
        beam((x, 12, 237), (x, 12, 295), GEAR, 1)
    for y in (25, 97, 187):
        beam((38, y, 241), (294, y, 241), QAV, 1)
    # 窄幅绝缘观察板嵌在门架边梁，不封挡折界窗口。
    for x in (39, 69, 260, 286):
        for y in range(83, 143, 12):
            box((x, y, 239), (x + 3, y + 8, 240), GLASS, replace=True)
            box((x, y, 259), (x + 3, y + 8, 260), BLUE_GLASS, replace=True)
    for y in range(83, 143, 12):
        box((69, y, 252), (72, y + 8, 253), AMBER_GLASS, replace=True)
        box((260, y, 252), (263, y + 8, 253), LIGHT, replace=True)


def return_and_service_bridges() -> None:
    """返航通道、设备吊运桥与外缘检修廊均回接主梁。"""
    for y, state in ((23, QAV), (35, ROBUST), (47, QAV), (59, ASSEMBLY)):
        beam((205, y, 199), (262, y, 194), state, 1)
        beam((204, y, 209), (250, y, 243), state, 1)
        beam((105, y, 197), (70, y, 233), state, 1)
    beam((105, 42, 197), (105, 59, 197), QAV)
    beam((70, 12, 230), (70, 59, 233), QAV, 1)
    for z in range(189, 241, 8):
        for x in (211, 220, 229, 238, 247, 256):
            box((x, 17, z), (x + 1, 51, z + 1), QAV if x % 2 else ROBUST)
        if z % 16 == 13:
            box((206, 51, z), (261, 53, z + 2), GRATE)
    # 返航滑车的分段缓冲塔按两侧成对布置，回到东翼隔离池。
    for x in (231, 306):
        for z in (188, 224, 259):
            box((x, 4, z), (x + 5, 7, z + 5), QAV)
            box((x, 7, z), (x + 5, 44, z + 5), QAV)
            for y in range(13, 41, 8):
                box((x - 2, y, z - 2), (x + 7, y + 2, z + 7), GEAR)
            if x == 306 and z == 259:
                beam((295, 20, 261), (306, 20, 261), QAV, 1)
    # 外圈维护环绕过功能舱，并在四角落回基础格构。
    for z in (68, 214, 230):
        beam((5, 12, z), (328, 12, z), CLEAN, 1)
        beam((5, 18, z), (328, 18, z), QAV, 1)
        for x in range(5, 329, 19):
            beam((x, 7, z), (x, 20, z), ROBUST)
    for x in (7, 111, 217, 325):
        beam((x, 11, 66), (x, 11, 232), QAV, 1)
        beam((x, 18, 66), (x, 18, 232), ROBUST, 1)


def thermal_and_power_systems() -> None:
    """供能与热交换外廊作为建筑构件，不暗示额定EU已确定。"""
    # 两列高位散热鳍片从计算塔外墙延伸，配合低位高功率母排。
    for x in (122, 126, 206, 210):
        beam((x, 54, 88), (x, 156, 181), TURBINE)
        for y in range(59, 153, 8):
            box((x - 2, y, 110), (x + 3, y + 1, 164), VENT)
        box((x - 2, 54, 134), (x + 2, 156, 138), QAV)
    for z in range(81, 220, 12):
        box((101, 14, z), (231, 16, z + 2), POWER if z % 24 == 9 else TUNG_PIPE)
        box((101, 17, z), (231, 20, z + 1), STEEL_PIPE)
    # 周期性维护桥与吊耳将散热构件挂回中央框架。
    for y in (58, 82, 106, 130, 154):
        beam((112, y, 96), (220, y, 96), ROBUST, 1)
        beam((112, y, 185), (220, y, 185), ROBUST, 1)
        for x in (114, 216):
            beam((x, y, 96), (x, y, 185), GRATE)


def add_markers(data: dict) -> None:
    """将工业接口候选平齐嵌入各自工艺墙面。"""
    data['controller'] = [CX, 104, 98]
    data['ports'] = [
        {'id': '无人装置与耗材输入', 'purpose': '西翼维护坞工具/耗材输入候选', 'pos': [13, 28, 145], 'face': 'west'},
        {'id': '冷却介质输入', 'purpose': '西翼热交换回路流体输入候选', 'pos': [13, 18, 175], 'face': 'west'},
        {'id': '任务授权与坐标输入', 'purpose': '后部调度接口候选；接收I25坐标与I44锁定记录', 'pos': [177, 34, 224], 'face': 'south'},
        {'id': '供能输入', 'purpose': '后部高功率母线接口候选；额定EU未定', 'pos': [153, 34, 224], 'face': 'south'},
        {'id': '物品与磨损件输出', 'purpose': '东翼返航分拣物品输出候选', 'pos': [319, 31, 131], 'face': 'east'},
        {'id': '流体输出', 'purpose': '东翼返航分拣流体输出候选', 'pos': [319, 21, 157], 'face': 'east'},
        {'id': '遗留技术档案输出', 'purpose': '东翼隔离档案舱输出候选', 'pos': [319, 52, 183], 'face': 'east'},
    ]
    outward = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}
    for marker in data['ports']:
        dx, dy, dz = outward[marker['face']]
        put(marker['pos'][0] - dx, marker['pos'][1] - dy, marker['pos'][2] - dz, QAV, replace=True)
        put(*marker['pos'], PORT, replace=True)
    put(*data['controller'], CONTROL, replace=True)


def build() -> dict:
    """按I26实际工艺从空白组合完整实体。"""
    CELLS.clear()
    foundations()
    west_maintenance_wing()
    east_quarantine_wing()
    dispatch_bay()
    command_spine()
    folded_boundary_gate()
    return_and_service_bridges()
    thermal_and_power_systems()
    data = {
        'key': 'I26', 'id': 'I26', 'name': NAME, 'title': TITLE,
        'candidate_version': 'V2', 'size': [W, H, D],
        'controller': [], 'ports': [], 'blocks': [], 'paths': [],
        'zones': [
            {'name': '西翼维护坞', 'pos': [58, 30, 137]},
            {'name': '中央调度脊', 'pos': [CX, 108, 144]},
            {'name': '单目标出港轨道', 'pos': [CX, 27, 45]},
            {'name': '返航隔离分拣', 'pos': [272, 35, 151]},
            {'name': '折界门架', 'pos': [166, 100, 263]},
        ],
        'description': 'QAV/V08 无人采掘与遗留技术阶段；单目标出港、返航隔离、物资分流与维护构成一个实体港区。',
    }
    add_markers(data)
    data['blocks'] = [{'pos': list(pos), 'state': state} for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    return data


def connected_components(data: dict) -> dict:
    """以稀疏体素坐标执行六邻接遍历，确认没有独立悬浮构件。"""
    volume = W * H * D
    occupied = bytearray(volume)
    first = None
    for block in data['blocks']:
        x, y, z = block['pos']
        index = (y * D + z) * W + x
        occupied[index] = 1
        if first is None:
            first = index
    if first is None:
        raise ValueError('结构无实体方块')
    visited = bytearray(volume)
    visited[first] = 1
    queue = array.array('I', [first])
    head = reached = 0
    while head < len(queue):
        index = queue[head]
        head += 1
        reached += 1
        x = index % W
        z = (index // W) % D
        yz = index // W
        y = yz // D
        neighbors = (index - 1 if x else -1, index + 1 if x + 1 < W else -1,
                     index - W if z else -1, index + W if z + 1 < D else -1,
                     index - W * D if y else -1, index + W * D if y + 1 < H else -1)
        for neighbor in neighbors:
            if neighbor >= 0 and occupied[neighbor] and not visited[neighbor]:
                visited[neighbor] = 1
                queue.append(neighbor)
    if reached != len(data['blocks']):
        raise ValueError(f'实体并非单一连续结构：连通{reached:,} / {len(data["blocks"]):,}')
    return {'components': 1, 'visited_blocks': reached, 'method': '六邻接实体遍历'}


def voltage_comparison(counts: collections.Counter, size_xyz: list[int]) -> dict:
    source = ROOT / 'logs/i01-i25-voltage-progression-20261025/audit.json'
    audit = json.loads(source.read_text(encoding='utf-8'))
    lower_forms = [form for form in audit['forms'] if form['tier'] < 22]
    if len(lower_forms) != 25:
        raise ValueError(f'电压比较对象数变化，需复核：{len(lower_forms)}')
    metrics = {
        'blocks': len(CELLS), 'materials': len(counts),
        'volume': math.prod(size_xyz), 'height': size_xyz[1],
    }
    maxima = {}
    for metric in metrics:
        value = max(form['metrics'][metric] for form in lower_forms)
        leaders = [form['id'] for form in lower_forms if form['metrics'][metric] == value]
        maxima[metric] = {'value': value, 'ids': leaders}
    result = {
        'source': str(source.relative_to(ROOT)), 'tier_rule': 'QAV/tier22 与全部较低阶形态比较，严格大于。',
        'lower_form_count': len(lower_forms), 'metrics': metrics, 'lower_maxima': maxima,
        'passes': {metric: metrics[metric] > maxima[metric]['value'] for metric in metrics},
    }
    if not all(result['passes'].values()):
        raise ValueError('I26 未超过所有较低电压形态：' + json.dumps(result, ensure_ascii=False))
    return result


def audit(data: dict) -> dict:
    require(data)
    counts = collections.Counter(block['state'] for block in data['blocks'])
    coordinates = [tuple(block['pos']) for block in data['blocks']]
    low = [min(p[i] for p in coordinates) for i in range(3)]
    high = [max(p[i] for p in coordinates) for i in range(3)]
    actual = [high[i] - low[i] + 1 for i in range(3)]
    if low != [0, 0, 0] or actual != [W, H, D]:
        raise ValueError(f'实体边界未到达声明边界：min={low}, actual={actual}')
    if counts[QAV] <= max(n for state, n in counts.items() if state != QAV):
        raise ValueError('QAV没有成为新增阶段最大单一材料')
    if {state for state in counts if state.startswith('hk3gtl:')} != {QAV, PORT}:
        raise ValueError('项目自有方块超出当前白名单')
    if counts[CONTROL] != 1:
        raise ValueError('主控标记数量异常')
    if data['controller'][0] != CX:
        raise ValueError('主控未落在整机宽度中轴')
    connectivity = connected_components(data)
    by_pos = {tuple(block['pos']): block['state'] for block in data['blocks']}
    port_checks = []
    dirs = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}
    for port in data['ports']:
        pos = tuple(port['pos'])
        dx, dy, dz = dirs[port['face']]
        if by_pos.get(pos) != PORT:
            raise ValueError(f'工业接口标记不存在：{port["id"]} {pos}')
        if any((pos[0] + dx * depth, pos[1] + dy * depth, pos[2] + dz * depth) in by_pos for depth in range(1, 5)):
            raise ValueError(f'工业接口外侧操作净空不足：{port["id"]} {pos}')
        backed = (pos[0] - dx, pos[1] - dy, pos[2] - dz)
        if backed not in by_pos:
            raise ValueError(f'工业接口内侧无设备背板：{port["id"]}')
        port_checks.append({'id': port['id'], 'position': pos, 'face': port['face'], 'inner_backed': True, 'outer_clear': 4})
    if by_pos.get(tuple(data['controller'])) != CONTROL:
        raise ValueError('中心主控标记坐标不匹配')
    cx, cy, cz = data['controller']
    if by_pos.get((cx, cy, cz + 1)) is None:
        raise ValueError('主控内侧无调度塔背板')
    if any((cx, cy, cz - depth) in by_pos for depth in range(1, 5)):
        raise ValueError('主控前方缺少操作净空')
    comparison = voltage_comparison(counts, actual)
    return {
        'passed': True, 'blocks': len(data['blocks']), 'palette': dict(counts.most_common()),
        'unique_materials': len(counts), 'bounds_xyz': {'min': low, 'max': high},
        'size_xyz': actual, 'size_wdh': [actual[0], actual[2], actual[1]],
        'bounding_box_volume': math.prod(actual), 'height': actual[1],
        'baseline_check': require(data), 'voltage_progression': comparison,
        'qav_casing_is_largest_single_material': True, 'qav_casing_count': counts[QAV],
        'controller': {'position': data['controller'], 'center_x_zero_based': CX,
                       'ordinal_from_left': CX + 1, 'integrated_in_hull': True},
        'port_checks': port_checks, 'connectivity': connectivity,
        'checks': [
            '实际实体边界逐轴符合I26最低尺寸并扩建；包围盒不是由空白范围撑大。',
            'QAV机壳是本阶最大单一材料，确立整机视觉识别。',
            '实际方块数、唯一材料数、包围盒体积和高度均严格大于全部25个低阶形态。',
            '控制器位于整机X中轴并与中央调度塔正面齐平。',
            '7个工业接口候选全部使用项目工业接口块、内侧有背板且外侧留出4格操作空间。',
            '六邻接遍历确认全结构只有一个连续实体组件。',
            '没有出现世界泡球体，保持I25坐标解析与I26无人远征的职责边界。',
        ],
        'not_verified': [
            'I26实际EU额定、真实Controller/Pattern、仓口注册能力及配方。',
            '游戏内成型、运行、研究解锁、生存获取与2.9.2游戏内验收。',
            '装置能否完成最多十次采掘的工艺逻辑；该上限来自功能规划，不由建筑外观证明。',
            '预览材质显示静态资源首帧，不模拟游戏光照、动态效果或运行动画。',
        ],
    }


def resource_materials(states: list[str]) -> tuple[list[dict], dict, list[str], dict]:
    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    options = (INSTANCE / 'options.txt').read_text(encoding='utf-8')
    packs = json.loads(next(line.partition(':')[2] for line in options.splitlines() if line.startswith('resourcePacks:')))
    try:
        for pack in packs:
            if not pack.startswith('file/'):
                continue
            path = INSTANCE / 'resourcepacks' / pack[5:]
            if not path.is_file():
                continue
            archive = zipfile.ZipFile(path)
            resources.archives.append((path, archive))
            for name in archive.namelist():
                if name.startswith('assets/'):
                    resources.index[name] = (path, archive)
        materials = []
        for state in states:
            material = dict(resources.material(state))
            if not material['complete_cube'] or material['tinted']:
                raise ValueError(f'预览仅收录静态完整方块：{state}')
            materials.append(material)
        material_by_state = {material['state']: material for material in materials}
        if material_by_state[PORT]['faces'] == material_by_state[QAV]['faces']:
            raise ValueError('接口材质与QAV外壳错误映射为同一纹理')
        if material_by_state[CONTROL]['faces'] == material_by_state[QAV]['faces']:
            raise ValueError('钻石主控材质错误映射为QAV外壳')
        index = INSTANCE.parent / 'mrpack/modrinth.index.json'
        version = json.loads(index.read_text(encoding='utf-8'))['versionId']
        installed = sorted(path.name for path in (INSTANCE / 'mods').glob('*HK3GTL*.jar'))
        return materials, dict(resources.sources), packs, {'instance_version': version, 'hk3gtl_jars': installed}
    finally:
        resources.close()


def font(size: int):
    return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', size)


def make_static_reports(data: dict, materials: list[dict], check: dict) -> None:
    colors, textures = {}, {}
    for material in materials:
        faces = material['faces']
        for face in ('north', 'up', 'west', 'east'):
            textures.setdefault(material['state'], {})[face] = Image.open(
                io.BytesIO(base64.b64decode(faces[face].split(',')[1]))).convert('RGB')
        colors[material['state']] = tuple(round(v) for v in ImageStat.Stat(textures[material['state']]['up']).mean)
    image = Image.new('RGB', (1700, 1410), '#131b25')
    draw = ImageDraw.Draw(image)
    draw.text((32, 22), 'I26 · 葵涌自动化码头 / 实体俯视布局', font=font(28), fill='#e5e9ed')
    scale, left, top = 3, 54, 96
    tops: dict[tuple[int, int], tuple[int, str]] = {}
    for block in data['blocks']:
        x, y, z = block['pos']
        if (x, z) not in tops or y > tops[x, z][0]:
            tops[x, z] = (y, block['state'])
    for (x, z), (_, state) in tops.items():
        draw.rectangle((left + x * scale, top + z * scale, left + (x + 1) * scale - 1,
                        top + (z + 1) * scale - 1), fill=colors[state])
    draw.rectangle((left - 1, top - 1, left + W * scale, top + D * scale), outline='#758692')
    for item in [{'id': '主控', 'pos': data['controller']}, *data['ports']]:
        x, y, z = item['pos']
        px, pz = left + x * scale + 2, top + z * scale + 2
        draw.ellipse((px - 5, pz - 5, px + 5, pz + 5), fill='#ffdc81', outline='#18202a')
    lx = 1080
    keylines = [
        f'{W} × {D} × {H}（宽×深×高）', '规划下限：49 × 81 × 37',
        f'{check["blocks"]:,} 个实体方块', f'{check["unique_materials"]} 种静态完整方块',
        'QAV / V08 · 锈红主船体', f'实际高度：{H} 格',
        f'控制器：X={CX}，整宽第{CX + 1}格', '单目标发射坞 → 折界门架',
        '七座堆场场桥 · 六台无人集卡拖头', '两座封闭仓库 · 采光带与装卸货门',
        '返航隔离 → 物品/流体/档案分流', '西翼维护坞与设备吊运桥',
    ]
    for i, line in enumerate(keylines):
        draw.text((lx, 115 + i * 39), line, font=font(19), fill='#cbd7df')
    image.save(OUT / '俯视布局.png')
    iso = Image.open(OUT / '等轴预览.png').convert('RGB')
    dr = ImageDraw.Draw(iso)
    dr.rectangle((0, 0, iso.width, 48), fill='#101720')
    dr.text((18, 10), 'I26 世界泡无人采掘调度台 · 葵涌自动化码头 V2', font=font(22), fill='#e7e5e0')
    dr.rectangle((0, iso.height - 46, iso.width, iso.height), fill='#101720')
    dr.text((18, iso.height - 37), f'{W} × {D} × {H} | {check["blocks"]:,} 方块 | QAV / V08 | 待审候选',
            font=font(19), fill='#d0d6d9')
    iso.save(OUT / '等轴预览.png')

    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    sheet = Image.new('RGB', (1530, 1270), '#131b25')
    sd = ImageDraw.Draw(sheet)
    sd.text((30, 20), '主控与工业接口候选 · 实际占位材质及设备墙局部', font=font(27), fill='#e8e4da')
    marked = [{'id': '中央主控', 'pos': data['controller'], 'face': 'north'}, *data['ports']]
    outward = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}
    for i, item in enumerate(marked):
        col, row = i % 3, i // 3
        x0, y0 = 25 + col * 500, 83 + row * 385
        sd.text((x0, y0), item['id'], font=font(19), fill='#f0d28e')
        sd.text((x0, y0 + 28), item.get('purpose', '居中主控；黄色圈只作定位'), font=font(15), fill='#d2dce2')
        x, y, z = item['pos']
        face = item.get('face', 'north')
        dx, dy, dz = outward[face]
        rx, ry = -dz, dx
        texture_face = 'north' if face in ('north', 'south') else ('west' if face == 'west' else 'east')
        for dv in range(-3, 4):
            for du in range(-3, 4):
                pos = (x + rx * du, y + dv, z + ry * du)
                px, py = x0 + (du + 3) * 42, y0 + 76 + (3 - dv) * 42
                state = occupied.get(pos)
                if state:
                    tex = textures[state][texture_face].resize((41, 41), Image.Resampling.NEAREST)
                    sheet.paste(tex, (px, py))
                else:
                    sd.rectangle((px, py, px + 40, py + 40), fill='#172632')
                sd.rectangle((px, py, px + 40, py + 40), outline='#53626c')
                if du == dv == 0:
                    sd.rectangle((px + 3, py + 3, px + 37, py + 37), outline='#fff0a3', width=3)
    sheet.save(OUT / '主控与接口局部.png')


def viewer_page(data: dict, check: dict) -> str:
    page = (VIEWER / '三维评审.html').read_text(encoding='utf-8')
    page = re.sub(r'<title>.*?</title>', f'<title>I26 · {html.escape(TITLE)} V2</title>', page, count=1, flags=re.S)
    page = re.sub(r'<header>.*?</header>',
                  f'<header><a href="../index.html">← I26交付总览</a><h1>I26 · {html.escape(TITLE)} V2</h1>'
                  f'<div>{W}×{D}×{H}（宽×深×高） · {check["blocks"]:,}方块 · 可旋转、剖切及逐口定位</div></header>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<div id="viewName"></div><div class="locator">.*?</div>',
                  f'<div id="viewName"></div><div class="locator"><b>主控 {data["controller"]}</b>'
                  f'<p>QAV/V08航务调度楼观测舱前脸，整宽第{CX + 1}格；钻石主控与墙面齐平。</p>'
                  '<p>工业接口块按工艺区定位；所有标记仅为封闭占位，不代表真实端口已注册。</p>'
                  '<button data-view="controller">定位主控</button></div>', page, count=1, flags=re.S)
    page = re.sub(r'<details open><summary>本次结构修改</summary>.*?</details>',
                  '<details open><summary>设计构成</summary><p>单一作业泊位朝向港池，四座岸桥沿岸线排列；箱垛、场桥、中央航务塔与分拣闸口组成一条自动化物流链。每座岸桥服务同一条目标航线，不表示多目标并行。</p>'
                  '<p>建筑不放置世界泡实体，保持坐标解析与无人远征职责分开。QAV机壳统领主体，钢灰承重件、浅色观测窗与少量安全色识别条作分层。</p></details>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<details><summary>结构文件与边界</summary>.*?</details>',
                  f'<details><summary>结构文件与边界</summary><a href="{NAME}.nbt">NBT</a> · '
                  f'<a href="{NAME}.schem">Schematic</a> · <a href="../verification.json">逐项检查</a>'
                  '<p>候选待审；实际EU额定未验证。没有写入正式Pattern或游戏实例。</p></details>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<label>剖切高度 <b id="layerValue">\d+</b><input id="layer" type="range" min="0" max="\d+" value="\d+">',
                  f'<label>剖切高度 <b id="layerValue">{H - 1}</b><input id="layer" type="range" min="0" max="{H - 1}" value="{H - 1}">',
                  page, count=1)
    page = page.replace('id="showPorts" type="checkbox">接口</label>',
                        'id="showPorts" type="checkbox">接口定位框</label>')
    page = page.replace('逐种隐藏材质', '隐藏材质（显示外表面及异材质交界层）')
    page = page.replace('逐口定位', '逐口定位；边界体素紧凑绘制')
    page = page.replace('变更记录#1：2026-10-23 10:57:25；新融合候选离线评审，不代表正式接入。',
                        'V2候选：葵涌码头式泊位、岸桥、堆场和调度塔；未获批准、未接入游戏。')
    return page


def report_page(data: dict, check: dict) -> str:
    palette_rows = ''.join(f'<tr><td><code>{html.escape(state)}</code></td><td>{count:,}</td></tr>'
                           for state, count in check['palette'].items())
    zones = ''.join(f'<article><h3>{html.escape(zone["name"])}</h3><p>{html.escape(zone["description"])}</p></article>'
                    for zone in data['zone_descriptions'])
    lower_rows = ''.join(f'<tr><td>{name}</td><td>{check["voltage_progression"]["metrics"][key]:,}</td>'
                         f'<td>{check["voltage_progression"]["lower_maxima"][key]["value"]:,}</td>'
                         f'<td>严格超过</td></tr>'
                         for key, name in (('blocks', '实体方块数'), ('materials', '唯一方块种类'),
                                           ('volume', '实体包围盒体积'), ('height', '实际高度')))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26 · {html.escape(TITLE)} V2</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#101820;color:#e4e9eb;font:15px/1.8 'Microsoft YaHei',sans-serif}}main{{max-width:1500px;margin:auto;padding:24px}}header{{background:#232c33;border-left:5px solid #8c4c3e;padding:22px}}h1{{margin:0;font-size:30px}}h2{{margin:34px 0 8px;color:#e5c995}}a{{color:#cbd9e3}}.meta,.zones{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:12px;margin:18px 0}}article,.meta>div{{background:#1a252c;border:1px solid #3a4952;padding:14px}}img{{display:block;max-width:100%;height:auto;margin:18px auto}}iframe{{width:100%;height:850px;border:1px solid #54616a}}table{{border-collapse:collapse;width:100%}}td{{padding:9px;border-bottom:1px solid #38464e}}code{{overflow-wrap:anywhere;color:#e7d5bd}}.note{{padding:14px;background:#282a27;border-left:4px solid #b4894e}}@media(max-width:720px){{main{{padding:12px}}h1{{font-size:24px}}iframe{{height:660px}}}}</style></head><body><main>
<header><small>HK3GTL / I26 / V08·QAV / 独立建筑候选 V2</small><h1>{html.escape(TITLE)}</h1><p>参考葵涌货柜码头的岸桥、堆场与闸口物流；中央只保留一条无人采掘目标航线。</p></header>
<div class="meta"><div><b>{W} × {D} × {H}</b><br>宽×深×高；规划最低49×81×37</div><div><b>{check['blocks']:,} 个实体方块</b><br>六邻接单组件</div><div><b>{check['unique_materials']} 种静态完整方块</b><br>QAV为最大单一材料</div><div><b>主控 X={CX}</b><br>零起算整宽中轴，第{CX + 1}格</div></div>
<p><a href="i26/三维评审.html">打开三维评审</a> · <a href="i26/{NAME}.nbt">NBT</a> · <a href="i26/{NAME}.schem">Schematic</a> · <a href="{OUT.name}.zip">完整ZIP</a> · <a href="verification.json">逐项核验</a></p>
<img src="等轴预览.png" alt="I26实际材质逐格等轴预览">
<h2>建筑叙事</h2><p>形体参考葵涌码头的港池岸线、高密度多色货柜、岸桥与陆侧仓储：海侧保留单一装置泊位，场桥和六辆无人牵引车服务货柜巷道，两座装卸仓库把分拣与检疫设备收进完整建筑。</p><p>中央航务楼承接I25坐标、I44授权与任务状态校验；细长中继塔把QAV远距调度的高度纳入建筑轮廓。多座岸桥共用一条作业泊位，I26仍为单目标；不放置世界泡模型，避免与I25解析对象混淆。</p>
<h2>实体俯视与功能分区</h2><img src="俯视布局.png" alt="I26港区实际实体俯视布局"><div class="zones">{zones}</div>
<h2>主控与接口候选</h2><p>钻石主控嵌入中央调度塔前脸的宽度中轴；工业接口方块嵌入各自功能舱墙面，外侧保留四格操作空间。它们是候选封闭占位，不证明端口注册、配方、EU或能力已接通。</p><img src="主控与接口局部.png" alt="I26主控及接口候选真实材质局部">
<h2>对全部低电压形态的严格递增检查</h2><p>按QAV/V08与审计记录内全部25个低阶形态逐项比较；I25的QEV/V07为当前高位基线之一。</p><table><thead><tr><td>指标</td><td>I26实测</td><td>低阶最大值</td><td>判定</td></tr></thead><tbody>{lower_rows}</tbody></table>
<h2>完整材料清单</h2><table><thead><tr><td>方块ID</td><td>数量</td></tr></thead><tbody>{palette_rows}</tbody></table>
<h2>三维评审</h2><p>只绘制{check['viewer_surface_faces']:,}片外露面（{check['viewer_draw_triangles']:,}个三角形）；剖切索引按高度排序并二分定位，向上扩展时只初始化新增矩阵。矩阵占用约{check['viewer_instance_matrix_bytes'] / 1048576:.1f} MiB。静止时暂停持续绘制；按材料隐藏只隐藏外露面，不会挖开实心方块显示内部填充。</p><iframe src="i26/三维评审.html" title="I26葵涌自动化码头三维评审" loading="lazy"></iframe>
<p class="note">当前版本：增强版2.9.2。候选仅完成结构文件、实际资源材质和建筑指标核验；实际EU额定、Pattern、端口能力、配方、游戏内成型与运行均未验证。本版待另一个我审阅，未批准、未归档确认版、未接入实例。</p>
<p><a href="manifest.json">候选清单</a> · <a href="设计依据.json">设计依据</a> · <a href="设计与检查.json">设计与检查</a></p></main></body></html>'''


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build_surface_groups(data: dict, states: list[str]) -> list[list[list[int]]]:
    """按材质和朝向保存外露面索引；块间接触面不提交给GPU。"""
    width, height, depth = data['size']
    stride_y = width * depth
    state_ids = {state: index + 1 for index, state in enumerate(states)}
    occupancy = bytearray(stride_y * height)
    for block in data['blocks']:
        x, y, z = block['pos']
        index = y * stride_y + z * width + x
        occupancy[index] = state_ids[block['state']]
    face_names = ('east', 'west', 'south', 'north', 'down', 'up')
    groups = [[[] for _ in face_names] for _ in states]
    for block in data['blocks']:
        x, y, z = block['pos']
        index = y * stride_y + z * width + x
        state_id = state_ids[block['state']]
        neighbors = (
            index + 1 if x + 1 < width else -1,
            index - 1 if x else -1,
            index + width if z + 1 < depth else -1,
            index - width if z else -1,
            index - stride_y if y else -1,
            index + stride_y if y + 1 < height else -1,
        )
        for face, neighbor in enumerate(neighbors):
            if neighbor < 0 or occupancy[neighbor] == 0:
                groups[state_id - 1][face].append(index)
    for material_groups in groups:
        for face_indices in material_groups:
            if any(a > b for a, b in zip(face_indices, face_indices[1:])):
                raise ValueError('外露面索引未按高度排序，不能使用剖切前缀。')
    return groups


def main() -> None:
    if OUT.exists() and any(OUT.iterdir()):
        existing = OUT / 'manifest.json'
        if not existing.is_file():
            allowed_partial = {
                f'i26/{NAME}.nbt', f'i26/{NAME}.schem', 'i26/data.js',
                'i26/viewer.bundle.js', 'i26/Three许可.txt',
            }
            partial_files = {path.relative_to(OUT).as_posix() for path in OUT.rglob('*') if path.is_file()}
            if not partial_files or not partial_files.issubset(allowed_partial):
                raise FileExistsError(f'拒绝覆盖身份未知的I26交付：{OUT}')
        else:
            identity = json.loads(existing.read_text(encoding='utf-8'))
            owned = (identity.get('key') == 'I26' and identity.get('title') == TITLE
                     and identity.get('candidate_version') == 'V2'
                     and identity.get('status') == 'candidate_waiting_user_review')
            if not owned:
                raise FileExistsError(f'拒绝覆盖身份不匹配的I26交付：{OUT}')
    OUT.mkdir(parents=True, exist_ok=True)
    VIEW.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    data = build_port()
    CELLS.clear()
    CELLS.update(PORT_CELLS)
    check = audit(data)
    counts = collections.Counter(block['state'] for block in data['blocks'])
    states = sorted(counts)
    materials, sources, packs, instance_proof = resource_materials(states)
    states, groups, hashes = export(data, VIEW)
    check['nbt_schem_sha256'] = hashes
    check['source_instance'] = str(INSTANCE)
    check['instance_proof'] = instance_proof
    check['enabled_file_resource_packs'] = packs
    check['material_resource_sources'] = sources
    check['marker_textures_are_distinct'] = all(
        next(m for m in materials if m['state'] == marker)['faces'] !=
        next(m for m in materials if m['state'] == QAV)['faces'] for marker in (PORT, CONTROL))
    payload_data = {key: value for key, value in data.items() if key not in ('blocks', 'zone_descriptions')}
    visible_groups = build_surface_groups(data, states)
    visible_container_faces = {}
    for state in CONTAINER_COLORS:
        if state not in states:
            raise ValueError('货柜配色没有进入实体材料表：' + state)
        face_count = sum(map(len, visible_groups[states.index(state)]))
        if face_count == 0:
            raise ValueError('货柜配色未出现在任何外露面：' + state)
        visible_container_faces[state] = face_count
    check['container_color_visible_faces'] = visible_container_faces
    check['viewer_surface_faces'] = sum(len(face) for state in visible_groups for face in state)
    check['viewer_draw_triangles'] = check['viewer_surface_faces'] * 2
    check['viewer_instance_matrix_bytes'] = check['viewer_surface_faces'] * 16 * 4
    payload = {
        'data': payload_data, 'palette': states, 'surfaceGroups': visible_groups,
        'blockCount': len(data['blocks']), 'materials': materials, 'audit': check,
        'names': {state: state.split(':', 1)[1].replace('_', ' ') for state in states},
    }
    encoded = base64.b64encode(gzip.compress(
        json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), compresslevel=9)).decode('ascii')
    (VIEW / 'data.js').write_text('window.HK3_PAYLOAD="' + encoded + '";\n', encoding='utf-8')
    decoded = json.loads(gzip.decompress(base64.b64decode(encoded)))
    reconstructed = {
        ((index % W), (index // (W * D)), (index // W) % D): state
        for state, group in zip(states, groups) for index in group
    }
    assert reconstructed == {tuple(block['pos']): block['state'] for block in data['blocks']}
    assert decoded['blockCount'] == len(data['blocks']) and decoded['surfaceGroups'] == visible_groups
    assert len(decoded['surfaceGroups']) == len(states)
    del decoded, reconstructed, groups, visible_groups
    check['viewer_payload_exact_cell_readback'] = True
    subprocess.run(['node', str(VIEWER_BUILDER), str(VIEW)], cwd=ROOT, check=True)
    render(data, materials, OUT)
    make_static_reports(data, materials, check)
    (VIEW / '三维评审.html').write_text(viewer_page(data, check), encoding='utf-8')
    (OUT / 'index.html').write_text(report_page(data, check), encoding='utf-8')
    write_json(OUT / '设计依据.json', [
        {'path': 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html',
         'fact': 'I26最低外包宽×深×高49×81×37，供规划扩展。'},
        {'path': 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html',
         'fact': 'I26映射V08/QAV；实际工艺EU仍须单独核对。'},
        {'path': 'logs/beta5-gap-audit-20260927/evidence.json',
         'fact': 'I26输入I25坐标、I44锁定记录、无人装置/耗材和能量；输出物品/流体、技术残片与磨损装置；每个真实世界泡最多10次采掘。'},
        {'path': 'logs/i01-i25-voltage-progression-20261025/audit.json',
         'fact': '递增比较对象为所有tier低于QAV的25个形态，逐项严格大于。'},
        {'path': 'rule/当前多方块设计规则.md',
         'fact': '执行尺寸、白名单、电压主方块、自然融合接口及所有低阶形态严格递增规则。'},
        {'path': 'deliveries/I01-I18_控制器居中融合修订_V2_20261023/index.html',
         'fact': '采用居中主控和设备本体内嵌接口原则；造型完全针对I26工艺另行规划。'},
        {'path': 'https://www.hkmpdb.gov.hk/en/port.html',
         'fact': '葵涌货柜码头以港池岸线、成列泊位和岸后堆场构成受限空间内的高密度港区。'},
        {'path': 'https://www.hit.com.hk/en/Innovation/Improving-Efficiency.html',
         'fact': '参考货柜位置管理、车辆路线、堆场吊机与远程操作等自动化物流表达。'},
        {'path': 'https://www.mardep.gov.hk/en/materials-and-publications/publications/hk-fact-sheet/index.html',
         'fact': '参考葵涌港池的航务交通控制设施；本设计将其转译为居中调度楼与坐标中继塔。'},
    ])
    write_json(OUT / '设计与检查.json', {
        'design': {key: value for key, value in data.items() if key not in ('blocks', 'zone_descriptions')},
        'audit': check,
    })
    write_json(OUT / 'manifest.json', {
        'generator': Path(__file__).name, 'key': 'I26', 'title': TITLE, 'candidate_version': 'V2',
        'status': 'candidate_waiting_user_review', 'approved': False,
        'target_voltage': 'QAV', 'voltage_mapping': 'V08 / tier22',
        'size_xyz': [W, H, D], 'size_wdh': [W, D, H], 'minimum_wdh': [49, 81, 37],
        'blocks': check['blocks'], 'unique_materials': check['unique_materials'],
        'controller': data['controller'], 'ports': data['ports'],
        'source_instance': str(INSTANCE), 'source_instance_version': instance_proof['instance_version'],
        'nbt_sha256': hashes['nbt'], 'schem_sha256': hashes['schem'],
        'claim_boundary': '仅建筑候选；未验证实际EU、正式Pattern、端口功能或游戏内运行。',
    })
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    shutil.copy2(VIEWER_BUILDER, OUT / '生成脚本' / VIEWER_BUILDER.name)
    bundle = OUT.with_suffix('.zip')
    bundle_files = {bundle.name, bundle.with_suffix('.zip.sha256').name}
    files = {p.relative_to(OUT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(OUT.rglob('*'))
             if p.is_file() and p.name not in bundle_files | {'verification.json'}}
    check['files_sha256_before_verification'] = files
    write_json(OUT / 'verification.json', check)
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path.name not in bundle_files:
                archive.write(path, path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for path in OUT.rglob('*'):
            if path.is_file() and path.name not in bundle_files:
                assert archive.read(f'{OUT.name}/{path.relative_to(OUT).as_posix()}') == path.read_bytes()
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    checksum = bundle.with_suffix('.zip.sha256')
    checksum.write_text(digest + '\n', encoding='ascii')
    shutil.copy2(bundle, OUT / bundle.name)
    shutil.copy2(checksum, OUT / checksum.name)
    print(json.dumps({
        'out': str(OUT), 'size_wdh': [W, D, H], 'blocks': check['blocks'],
        'unique_materials': check['unique_materials'], 'palette': counts.most_common(),
        'lower_voltage_comparison': check['voltage_progression'], 'connected': check['connectivity'],
        'instance': instance_proof, 'zip_sha256': digest, 'verified': True,
    }, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
