# -*- coding: utf-8 -*-
"""Build a review-only I23 gas-to-solid phase-change machine candidate."""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import json
import math
import shutil
import zipfile
from pathlib import Path

import nbtlib
from PIL import Image, ImageDraw, ImageFont

from build_redesign69 import export, render as render_preview
from structure_size_baseline import ROOT, require


OUT = ROOT / 'deliveries/I23_崩坏能相变释能机_虚数相界双环炉院_V3_20261024'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01/i23'
OLD_PAGE = SOURCE / '三维评审.html'
OLD_DATA = SOURCE / 'data.js'
VIEWER = SOURCE.parent / 'viewer.bundle.js'
NAME = 'hk3gtl-i23-imaginary-phase-dualring-v3-20261024'
W, H, D = 57, 59, 65

AIR = 'minecraft:air'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
FLOOR = 'gtceu:clean_machine_casing'
FRAME = 'gtlcore:lafium_mechanical_casing'
POWER = 'gtceu:high_power_casing'
PIPE = 'gtceu:tungstensteel_pipe_casing'
CHEM = 'gtceu:corrosion_proof_casing'
GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
REINFORCED_GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
RIB = 'gtlcore:lafium_mechanical_casing'
FILTER = 'gtlcore:law_filter_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
PRECISION = 'gtlcore:multi_functional_casing'
COOL = 'gtlcore:super_cooler_component[active=false]'
COIL = 'kubejs:titansteel_coil_block[active=false]'
GRATE = 'gtceu:assembly_line_grating'
COMPUTER = 'gtceu:advanced_computer_casing'
COMPUTE = 'gtlcore:super_computation_component[active=false]'

CELLS: dict[tuple[int, int, int], str] = {}


def put(x: int, y: int, z: int, state: str, replace: bool = False) -> None:
    if not (0 <= x < W and 0 <= y < H and 0 <= z < D):
        raise ValueError(f'越界方块 {x,y,z}: {state}')
    p = (x, y, z)
    if replace or p not in CELLS:
        CELLS[p] = state


def box(lo: tuple[int, int, int], hi: tuple[int, int, int], state: str,
        replace: bool = False) -> None:
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def line(a: tuple[int, int, int], b: tuple[int, int, int], state: str) -> None:
    x, y, z = a
    dx = (b[0] > x) - (b[0] < x)
    dy = (b[1] > y) - (b[1] < y)
    dz = (b[2] > z) - (b[2] < z)
    if sum(v != 0 for v in (dx, dy, dz)) > 1:
        raise ValueError(f'线段不是轴向：{a} -> {b}')
    while True:
        put(x, y, z, state)
        if (x, y, z) == b:
            break
        x, y, z = x + dx, y + dy, z + dz


def route(points: list[tuple[int, int, int]], state: str = PIPE) -> None:
    for a, b in zip(points, points[1:]):
        line(a, b, state)


def ring_y(x0: int, x1: int, z0: int, z1: int, y: int, state: str) -> None:
    line((x0, y, z0), (x1, y, z0), state)
    line((x1, y, z0), (x1, y, z1), state)
    line((x1, y, z1), (x0, y, z1), state)
    line((x0, y, z1), (x0, y, z0), state)


def vertical_ring(cx: int, cz: int, y0: int, y1: int, radius: int, state: str) -> None:
    for x, z in ((cx-radius, cz-radius), (cx+radius, cz-radius),
                 (cx+radius, cz+radius), (cx-radius, cz+radius)):
        line((x, y0, z), (x, y1, z), state)
    for y in (y0, y1):
        ring_y(cx-radius, cx+radius, cz-radius, cz+radius, y, state)


def build_v2_reference() -> dict:
    CELLS.clear()

    # Discrete foundations leave the center and service sides open for access.
    box((0, 0, 8), (1, 2, 12), FRAME)
    line((0, 1, 10), (2, 1, 10), GRATE)

    # Gas intake and two-stage compression gantry, west of the phase chamber.
    ring_y(2, 9, 4, 16, 1, FRAME)
    ring_y(2, 9, 4, 16, 3, POWER)
    ring_y(2, 9, 4, 16, 19, FRAME)
    for x in (2, 9):
        for z in (4, 16):
            line((x, 2, z), (x, 19, z), POWER)
    for y in range(4, 19, 3):
        line((2, y, 4), (9, y, 4), FRAME)
        line((2, y, 16), (9, y, 16), FRAME)
    for y in (6, 9, 12, 15):
        line((2, y, 4), (9, y, 4), POWER)
    line((2, 4, 5), (2, 4, 15), POWER)
    for x, z in ((4, 8), (7, 12)):
        vertical_ring(x, z, 3, 16, 2, CHEM)
        for y in (5, 8, 11, 14, 17):
            ring_y(x-2, x+2, z-2, z+2, y, GEAR if y in (8, 14) else POWER)
        line((x, 4, z), (x, 18, z), PIPE)
        put(x, 7, z, COIL, True)
        put(x, 12, z, COIL, True)
        put(x, 16, z, COMPUTER, True)
    for x in range(3, 9, 2):
        line((x, 4, 5), (x, 18, 5), RIB)
    line((2, 8, 4), (2, 8, 8), FRAME)
    line((2, 8, 8), (4, 8, 8), FRAME)
    line((7, 8, 12), (9, 8, 12), FRAME)
    line((9, 8, 12), (9, 8, 16), FRAME)
    line((3, 20, 5), (8, 20, 5), POWER)
    line((3, 20, 15), (8, 20, 15), POWER)
    for x in range(3, 9, 2):
        line((x, 20, 5), (x, 20, 15), PIPE)
    route([(4, 4, 4), (4, 4, 0)], PIPE)

    # Pressure vessel: a framed transparent shell around the visible phase-change core.
    ring_y(11, 21, 10, 26, 8, FRAME)
    ring_y(11, 21, 10, 26, 27, FRAME)
    for x in (11, 21):
        for z in (10, 26):
            line((x, 8, z), (x, 27, z), FRAME)
    for y in range(10, 27):
        for x in (11, 21):
            put(x, y, 18, GLASS)
        for z in (10, 26):
            put(16, y, z, GLASS)
    for z in (10, 26):
        for x in (13, 19):
            line((x, 9, z), (x, 27, z), RIB)
    for x in (11, 21):
        for z in (14, 22):
            line((x, 9, z), (x, 27, z), RIB)
    for y in (12, 18, 24):
        ring_y(11, 21, 10, 26, y, POWER)
    vertical_ring(16, 18, 10, 25, 4, COIL)
    box((15, 12, 17), (17, 24, 19), GLASS, True)
    put(16, 18, 18, DIAMOND, True)
    line((11, 18, 18), (15, 18, 18), COIL)
    line((17, 18, 18), (21, 18, 18), COIL)
    # The one-block controller sits at the centerline on the chamber's accessible front flange.
    box((14, 2, 10), (18, 6, 10), POWER)
    for x in (14, 18):
        line((x, 2, 10), (x, 7, 10), FRAME)
    ring_y(14, 18, 10, 10, 7, FRAME)
    put(16, 4, 10, DIAMOND, True)

    # Gas feed enters the vessel; coolant and heat lines terminate at the exchanger.
    route([(7, 12, 12), (10, 12, 12), (11, 12, 12), (11, 12, 18)])
    route([(21, 16, 18), (23, 16, 18), (23, 12, 18), (23, 12, 16), (24, 12, 16)], CHEM)
    route([(25, 9, 19), (23, 9, 19), (22, 9, 19), (21, 9, 19)], PIPE)

    # Cooling bank with exposed fins and two distinguishable thermal headers.
    ring_y(24, 30, 11, 22, 1, FRAME)
    ring_y(24, 30, 11, 22, 15, FRAME)
    for x in (24, 30):
        for z in (11, 22):
            line((x, 2, z), (x, 15, z), POWER)
    for z in (13, 16, 19):
        for x in (25, 26, 27, 28, 29):
            line((x, 4, z), (x, 12, z), COOL)
        line((25, 13, z), (29, 13, z), VENT)
    for y in (4, 8, 12):
        line((24, y, 12), (30, y, 12), FRAME)
        line((24, y, 21), (30, y, 21), FRAME)
    line((30, 5, 13), (30, 5, 20), POWER)
    line((30, 9, 13), (30, 9, 20), POWER)
    line((29, 3, 16), (32, 3, 16), CHEM)
    line((32, 3, 16), (32, 12, 16), VENT)
    line((25, 14, 12), (29, 14, 12), PIPE)
    line((25, 14, 21), (29, 14, 21), CHEM)
    line((27, 12, 12), (27, 14, 12), PIPE)
    line((27, 12, 21), (27, 14, 21), CHEM)

    # Solid separator and collection vessels, with an exterior discharge chute.
    ring_y(3, 10, 25, 33, 1, FRAME)
    ring_y(3, 10, 25, 33, 10, FRAME)
    for x in (3, 10):
        for z in (25, 33):
            line((x, 2, z), (x, 10, z), POWER)
    for x, z, radius in ((5, 28, 2), (8, 31, 1)):
        vertical_ring(x, z, 2, 8, radius, CHEM)
        for y in (3, 6, 8):
            ring_y(x-radius, x+radius, z-radius, z+radius, y, POWER)
        line((x, 2, z), (x, 8, z), PIPE)
    line((5, 5, 28), (3, 5, 28), PIPE)
    line((3, 5, 25), (3, 5, 28), PIPE)
    box((5, 2, 30), (8, 3, 32), FILTER)
    box((5, 4, 31), (8, 7, 32), GLASS)
    route([(13, 8, 25), (13, 8, 28), (10, 8, 28), (8, 8, 28), (8, 8, 31)], CHEM)

    # Energy recovery turbine house at the rear, separated from the hot-side exchanger.
    ring_y(23, 30, 25, 34, 1, FRAME)
    ring_y(23, 30, 25, 34, 12, FRAME)
    for x in (23, 30):
        for z in (25, 34):
            line((x, 2, z), (x, 12, z), POWER)
    line((23, 5, 34), (30, 5, 34), POWER)
    line((30, 2, 34), (30, 2, 36), PIPE)
    line((30, 2, 36), (30, 12, 36), VENT)
    for z in (27, 31):
        line((24, 4, z), (29, 4, z), GEAR)
        line((24, 8, z), (29, 8, z), GEAR)
        for x in (25, 28):
            vertical_ring(x, z, 3, 9, 1, POWER)
            put(x, 6, z, COIL, True)
            line((x, 6, z), (x-1, 6, z), GEAR)
            line((x-1, 6, z), (x-1, 6, z-1), GEAR)
        for x in range(24, 30):
            put(x, 10, z, GLASS)
    box((26, 3, 28), (28, 7, 30), COMPUTER)
    box((25, 9, 32), (29, 10, 32), REINFORCED_GLASS)
    route([(21, 8, 23), (22, 8, 23), (22, 8, 25), (23, 8, 25), (24, 8, 25), (24, 8, 27)])

    # Raised service gantry, overhead pressure loop and maintenance ladders.
    ring_y(9, 23, 8, 28, 30, FRAME)
    for x in (9, 23):
        for z in (8, 28):
            line((x, 25, z), (x, 30, z), FRAME)
    for x in (10, 15, 20, 22):
        line((x, 28, 8), (x, 30, 8), GRATE)
        line((x, 28, 28), (x, 30, 28), GRATE)
    route([(9, 30, 18), (9, 32, 18), (23, 32, 18), (23, 30, 18)], PIPE)
    vertical_ring(16, 18, 30, 34, 2, COMPUTE)
    ring_y(14, 18, 16, 20, 34, FRAME)
    ring_y(14, 18, 16, 20, 32, PIPE)
    for x, z in ((11, 10), (21, 10), (11, 26), (21, 26)):
        line((x, 27, z), (x, 30, z), FRAME)
        for y in (28, 29):
            line((x-1, y, z), (x+1, y, z), GRATE)
    for x,z,edge_z in ((11,10,8),(21,10,8),(11,26,28),(21,26,28)):
        line((x,30,z),(x,30,edge_z),FRAME)
    line((3, 19, 5), (3, 20, 5), FRAME)

    # Six process interfaces replace casing blocks on the equipment surfaces.
    ports = [
        {'id': 'G-IN', 'pos': [4, 6, 4], 'face': 'north', 'purpose': 'I01-3气态崩坏能输入候选'},
        {'id': 'EU-IN', 'pos': [2, 4, 10], 'face': 'west', 'purpose': '气体压缩能量输入候选'},
        {'id': 'C-IN', 'pos': [30, 5, 15], 'face': 'east', 'purpose': '冷却介质输入候选'},
        {'id': 'SOLID-OUT', 'pos': [5, 4, 33], 'face': 'south', 'purpose': '固态崩坏能输出候选'},
        {'id': 'EU-OUT', 'pos': [27, 5, 34], 'face': 'south', 'purpose': '计量后的回收能量输出候选'},
        {'id': 'HEAT-OUT', 'pos': [30, 9, 20], 'face': 'east', 'purpose': '废热排出候选'},
    ]
    for item in ports:
        put(*item['pos'], PORT, True)

    zones = [
        {'name': '气态进料与双级压缩架', 'min': [2, 1, 4], 'max': [9, 20, 16], 'pos': [6, 20, 8],
         'description': '接收I01-3气态样本，沿双级压缩柱送入相变舱；压缩能量单独接入。'},
        {'name': '受约束相变反应舱', 'min': [11, 8, 10], 'max': [21, 30, 26], 'pos': [16, 28, 18],
         'description': '透明承压壳内设置约束线圈与可见核心，机体正面中轴集成主控。'},
        {'name': '固态析出与收集单元', 'min': [3, 1, 25], 'max': [10, 10, 33], 'pos': [7, 10, 29],
         'description': '分离舱、观察仓和收集罐连接固态产品输出。'},
        {'name': '分区换热与冷却鳍组', 'min': [24, 1, 11], 'max': [30, 15, 22], 'pos': [27, 15, 16],
         'description': '多片竖向换热鳍分开布置冷却介质入口与热排出口。'},
        {'name': '计量回收透平厅', 'min': [23, 1, 25], 'max': [30, 12, 34], 'pos': [27, 12, 30],
         'description': '相变释能经管道进入独立透平组；能量输出不代表实装发电行为。'},
    ]
    routes = [
        {'name': '压缩气体至相变舱', 'points': [[8, 12, 9], [10, 12, 9], [10, 12, 14], [11, 12, 14]]},
        {'name': '冷却/热回流至换热鳍组', 'points': [[21, 16, 18], [23, 16, 18], [23, 12, 18], [24, 12, 18]]},
        {'name': '热侧回路至换热接口', 'points': [[24, 9, 14], [22, 9, 14], [22, 9, 23], [21, 9, 23]]},
        {'name': '固态析出至收集单元', 'points': [[13, 8, 25], [13, 8, 28], [10, 8, 28]]},
        {'name': '计量释能至回收透平', 'points': [[21, 8, 23], [22, 8, 23], [22, 8, 27], [23, 8, 27]]},
    ]
    blocks = [{'pos': list(pos), 'state': state}
              for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    data = {
        'key': 'i23', 'name': NAME, 'title': '崩坏能相变释能机',
        'candidate_version': '相态压缩换热列车V2・待审',
        'size': [W, H, D], 'blocks': blocks, 'block_count': len(blocks),
        'controller': [16, 4, 10], 'controller_face': 'north', 'ports': ports,
        'paths': [{'name': '中轴主控访问通道', 'min': [15, 1, 2], 'max': [17, 4, 9]},
                  {'name': '西侧设备维护带', 'min': [1, 1, 4], 'max': [1, 4, 33]},
                  {'name': '东侧换热维护带', 'min': [31, 1, 10], 'max': [31, 4, 24]}],
        'zones': zones, 'links': routes,
        'description': '气态接收、压缩、受控气固相变、固态析出、计量释能回收及废热换出。',
        'target_voltage': None,
        'target_voltage_status': '未定；QCV/V06只见于待审映射，当前无I23可执行生产配方。',
        'role_materials': {FLOOR: ['基础与检修带'], FRAME: ['承重框架'], POWER: ['压缩与承压设备'],
                           PIPE: ['气体与能量路线'], CHEM: ['耐蚀介质管路与收集仓'],
                           GLASS: ['相变舱观察窗'], COOL: ['换热鳍'], COIL: ['相变约束/转子线圈'],
                           GEAR: ['压缩传动与透平轴系'], PORT: ['工艺接口占位'], DIAMOND: ['核心/控制器候选标记']},
        'construction_notes': {
            'orientation': '宽度沿X轴，前侧为-Z；实体范围33×35×37（X×Y×Z），对应总表宽×长×高33×37×35。',
            'interfaces': '六个工业接口占位块嵌入压缩机、换热器、固态收集单元和透平机壳。',
            'controller': '主控占位位于宽度中线x=16、相变舱前沿下部，与设备机身相连并从前方可达。',
            'voltage': '暂不采用hk3gtl:voltage_machine_casing_*；待逐机工业线及实际配方定阶后再作新版本。',
            'flow': '工艺线仅是空间组织表达；预览不证明配方、损耗、研究或机器能力已接通。',
        },
    }
    return data


def build() -> dict:
    """Create a full-scale, review-only dual-ring imaginary phase foundry."""
    CELLS.clear()

    # A continuous foundation ties the widely separated process buildings together.
    box((0, 0, 0), (W - 1, 0, D - 1), FLOOR)

    # Central pressure tower: a framed outer vessel, a second transparent shell,
    # twin restraint rings, and a visible phase core beneath a beacon mast.
    ring_y(16, 40, 19, 43, 5, FRAME)
    ring_y(16, 40, 19, 43, 50, FRAME)
    for x, z in ((16, 19), (40, 19), (16, 43), (40, 43)):
        line((x, 1, z), (x, 50, z), POWER)
    for y in (8, 15, 23, 31, 39, 46):
        ring_y(16, 40, 19, 43, y, FRAME if y in (8, 46) else POWER)
    for x in (20, 36):
        for z in (19, 43):
            line((x, 8, z), (x, 46, z), RIB)
    for x in (16, 40):
        for z in (24, 38):
            line((x, 8, z), (x, 46, z), RIB)
    for y in range(10, 45):
        for x in (17, 39):
            put(x, y, 31, GLASS)
        for z in (20, 42):
            put(28, y, z, REINFORCED_GLASS)
        for x in range(18, 39):
            put(x, y, 20, GLASS)
            put(x, y, 42, GLASS)
        for z in range(21, 42):
            put(17, y, z, GLASS)
            put(39, y, z, GLASS)
    for y in (13, 20, 28, 36, 43):
        ring_y(17, 39, 20, 42, y, GLASS)
    vertical_ring(28, 31, 8, 45, 8, COIL)
    vertical_ring(28, 31, 12, 42, 5, REINFORCED_GLASS)
    for y in (11, 17, 24, 32, 39, 44):
        ring_y(20, 36, 23, 39, y, COIL if y in (17, 32, 44) else GEAR)
    for x in (20, 36):
        line((x, 12, 31), (x, 43, 31), POWER)
    for z in (23, 39):
        line((28, 12, z), (28, 43, z), POWER)
    box((26, 24, 29), (30, 33, 33), GLASS)
    put(28, 28, 31, DIAMOND, True)
    for x in range(22, 35, 3):
        line((x, 7, 31), (x, 12, 31), PIPE)
    for z in range(25, 39, 3):
        line((28, 7, z), (28, 12, z), PIPE)
    # Keep the north-facing controller socket visible from the front approach.
    box((25, 3, 22), (31, 7, 22), POWER)
    for x in (25, 31):
        line((x, 3, 22), (x, 8, 22), FRAME)
    ring_y(25, 31, 22, 22, 8, FRAME)
    put(28, 5, 22, DIAMOND, True)
    # Crown and beacon, making the machine legible above the process halls.
    ring_y(14, 42, 17, 45, 51, POWER)
    ring_y(18, 38, 21, 41, 54, FRAME)
    for x, z in ((18, 21), (38, 21), (18, 41), (38, 41)):
        line((x, 50, z), (x, 54, z), RIB)
    vertical_ring(28, 31, 50, 57, 3, COIL)
    for y in (52, 55, 57):
        ring_y(25, 31, 28, 34, y, POWER if y == 57 else GEAR)
    line((28, 51, 31), (28, 58, 31), PIPE)
    put(28, 56, 31, COMPUTER, True)
    box((26, 57, 29), (30, 58, 33), REINFORCED_GLASS)

    # Gas intake and paired compression galleries on the front-west quadrant.
    ring_y(3, 15, 5, 20, 5, FRAME)
    ring_y(3, 15, 5, 20, 29, FRAME)
    for x in (3, 9, 15):
        for z in (5, 20):
            line((x, 1, z), (x, 29, z), POWER)
    for y in (9, 15, 21, 27):
        line((3, y, 5), (15, y, 5), FRAME)
        line((3, y, 20), (15, y, 20), FRAME)
    for x, z in ((6, 9), (12, 16)):
        vertical_ring(x, z, 6, 24, 2, CHEM)
        for y in (8, 12, 16, 20, 24):
            ring_y(x - 2, x + 2, z - 2, z + 2, y, GEAR if y in (12, 20) else POWER)
        line((x, 7, z), (x, 25, z), PIPE)
        put(x, 12, z, COIL, True)
        put(x, 18, z, COIL, True)
        put(x, 23, z, COMPUTER, True)
    for x in (4, 8, 12, 14):
        line((x, 7, 5), (x, 27, 5), RIB)
    ring_y(2, 16, 4, 21, 30, FRAME)
    for x in (3, 9, 15):
        line((x, 29, 5), (x, 30, 5), FRAME)
        line((x, 29, 20), (x, 30, 20), FRAME)
    for x in range(4, 16, 2):
        line((x, 30, 4), (x, 30, 21), GRATE)
    gas_compression_points = [[28, 5, 1], [28, 4, 1], [6, 4, 1], [6, 4, 9],
                              [7, 4, 9], [7, 17, 9], [6, 17, 9],
                              [7, 17, 9], [7, 26, 9], [12, 26, 9],
                              [12, 17, 9], [12, 17, 16]]
    route([tuple(point) for point in gas_compression_points], PIPE)
    phase_feed_points = [[12, 17, 16], [13, 17, 16], [13, 22, 16],
                         [18, 22, 16], [18, 22, 31], [18, 18, 31]]
    route([tuple(point) for point in phase_feed_points], PIPE)
    put(18, 22, 20, PIPE, True)

    # West cooling towers: paired fin banks with independent headers.
    for cx, cz, radius, top in ((5, 30, 4, 36), (8, 39, 3, 32)):
        x0, x1, z0, z1 = cx - radius, cx + radius, cz - radius, cz + radius
        ring_y(x0, x1, z0, z1, 5, FRAME)
        ring_y(x0, x1, z0, z1, top, FRAME)
        for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
            line((x, 1, z), (x, top, z), POWER)
        for y in range(8, top - 1, 5):
            ring_y(x0, x1, z0, z1, y, RIB)
        for x in range(x0 + 1, x1, 2):
            line((x, 8, z0), (x, top - 4, z0), COOL)
            line((x, 8, z1), (x, top - 4, z1), COOL)
        for z in range(z0 + 1, z1, 2):
            line((x0, 8, z), (x0, top - 4, z), COOL)
            line((x1, 8, z), (x1, top - 4, z), COOL)
        for y in (8, top - 3):
            line((x0, y, cz), (x1, y, cz), PIPE)
            line((cx, y, z0), (cx, y, z1), CHEM)
    # Water/coolant distribution mast is inside the tower envelope.
    line((1, 6, 32), (4, 6, 32), CHEM)
    line((4, 6, 32), (4, 18, 32), CHEM)
    route([(4, 18, 32), (11, 18, 32), (16, 18, 32), (18, 18, 32)], CHEM)
    route([(4, 12, 32), (4, 12, 39), (9, 12, 39), (15, 12, 39), (18, 12, 39)], PIPE)

    # East thermal exchange court, built as a deep, multi-stage fin house.
    ring_y(43, 55, 23, 43, 5, FRAME)
    ring_y(43, 55, 23, 43, 34, FRAME)
    for x in (43, 49, 55):
        for z in (23, 43):
            line((x, 1, z), (x, 34, z), POWER)
    for y in (10, 17, 24, 31):
        line((43, y, 23), (55, y, 23), FRAME)
        line((43, y, 43), (55, y, 43), FRAME)
    for x in (46, 50, 54):
        for z in (26, 31, 36, 40):
            line((x, 7, z), (x, 28, z), COOL)
            for y in (9, 15, 21, 27):
                line((x - 1, y, z), (x + 1, y, z), VENT)
    for y in (7, 14, 21, 28):
        line((44, y, 25), (54, y, 25), PIPE)
        line((44, y, 41), (54, y, 41), CHEM)
    # Twin stack towers visually separate hot exhaust from recovered coolant.
    for cx, cz in ((46, 28), (52, 38)):
        vertical_ring(cx, cz, 8, 42, 2, POWER)
        for y in (12, 20, 28, 36, 42):
            ring_y(cx - 2, cx + 2, cz - 2, cz + 2, y, FRAME)
        line((cx, 7, cz), (cx, 43, cz), PIPE)
        for x in range(cx - 1, cx + 2):
            line((x, 15, cz - 2), (x, 34, cz - 2), VENT)
    route([(39, 18, 31), (42, 18, 31), (43, 18, 31)], CHEM)
    route([(39, 13, 36), (43, 13, 36), (48, 13, 36)], PIPE)

    # Rear crystallization and collection house with four visible buffer silos.
    ring_y(3, 20, 48, 62, 5, FRAME)
    ring_y(3, 20, 48, 62, 29, FRAME)
    for x in (3, 11, 20):
        for z in (48, 62):
            line((x, 1, z), (x, 29, z), POWER)
    for y in (11, 18, 25):
        line((3, y, 48), (20, y, 48), RIB)
        line((3, y, 62), (20, y, 62), RIB)
    for cx, cz, radius, top in ((6, 52, 2, 25), (11, 52, 2, 25),
                                (6, 58, 2, 25), (11, 58, 2, 25)):
        vertical_ring(cx, cz, 6, top, radius, CHEM)
        for y in (8, 13, 18, 23, top):
            ring_y(cx - radius, cx + radius, cz - radius, cz + radius, y,
                   REINFORCED_GLASS if y == 13 else POWER)
        line((cx, 6, cz), (cx, top, cz), PIPE)
        for x in (cx - 1, cx + 1):
            for z in (cz - 1, cz + 1):
                line((x, 6, z), (x, top - 1, z), RIB)
    box((14, 7, 51), (18, 12, 59), FILTER)
    box((14, 13, 52), (18, 21, 58), GLASS)
    box((14, 22, 52), (18, 25, 58), REINFORCED_GLASS)
    route([(18, 18, 31), (18, 18, 48), (15, 18, 48), (15, 18, 52)], CHEM)
    route([(15, 12, 52), (15, 12, 58)], PIPE)
    route([(15, 12, 58), (15, 12, 62), (20, 12, 62)], PIPE)
    solid_outlet_points = [[20, 12, 62], [20, 12, 61], [20, 6, 61]]
    put(20, 12, 62, PIPE, True)
    route([tuple(point) for point in solid_outlet_points], PIPE)

    # Rear metering turbine hall, distinct from the hot-side exhaust yard.
    ring_y(37, 54, 48, 63, 5, FRAME)
    ring_y(37, 54, 48, 63, 31, FRAME)
    for x in (37, 45, 54):
        for z in (48, 63):
            line((x, 1, z), (x, 31, z), POWER)
    for y in (12, 20, 28):
        line((37, y, 48), (54, y, 48), RIB)
        line((37, y, 63), (54, y, 63), RIB)
    for z in (52, 57, 61):
        line((39, 9, z), (52, 9, z), GEAR)
        line((39, 22, z), (52, 22, z), GEAR)
        for x in (41, 46, 50):
            vertical_ring(x, z, 8, 23, 2, POWER)
            put(x, 15, z, COIL, True)
            line((x, 15, z), (x + 1, 15, z), GEAR)
        line((39, 26, z), (52, 26, z), GLASS)
    box((43, 10, 54), (48, 18, 59), COMPUTER)
    box((41, 23, 56), (50, 27, 59), REINFORCED_GLASS)
    route([(39, 13, 36), (39, 13, 45), (44, 13, 45), (44, 13, 48)], PIPE)
    route([(44, 20, 48), (44, 20, 63), (40, 20, 63), (40, 6, 63)], PIPE)

    # High process bridges and service gantries bind each hall into one machine.
    route([(8, 36, 30), (8, 40, 30), (16, 40, 30), (16, 40, 31)], PIPE)
    route([(38, 37, 31), (44, 37, 31), (44, 34, 31)], PIPE)
    route([(12, 29, 18), (12, 35, 18), (45, 35, 18), (45, 35, 23)], CHEM)
    route([(18, 29, 56), (23, 29, 56), (23, 36, 56), (37, 36, 56)], PIPE)
    ring_y(15, 41, 19, 43, 48, FRAME)
    for x, z in ((15, 19), (41, 19), (15, 43), (41, 43)):
        line((x, 46, z), (x, 48, z), FRAME)
    for x in range(17, 41, 4):
        line((x, 48, 19), (x, 48, 43), GRATE)
    vertical_ring(28, 31, 47, 50, 10, COMPUTE)

    # Paneled pressure and process-hall skins keep the equipment readable.
    box((4, 6, 5), (14, 11, 5), CHEM, True)
    box((4, 12, 5), (14, 20, 5), GLASS, True)
    box((4, 21, 5), (14, 27, 5), CHEM, True)
    for x in (4, 8, 12, 14):
        line((x, 6, 5), (x, 27, 5), RIB)
    for z in (49, 61):
        box((4, 6, z), (19, 12, z), FRAME, True)
        box((4, 13, z), (19, 21, z), REINFORCED_GLASS, True)
        box((4, 22, z), (19, 27, z), CHEM, True)
        for x in (4, 11, 19):
            line((x, 6, z), (x, 27, z), POWER)
    for z in (24, 42):
        box((44, 6, z), (54, 12, z), FRAME, True)
        box((44, 13, z), (54, 24, z), GLASS, True)
        box((44, 25, z), (54, 31, z), CHEM, True)
        for x in (44, 49, 54):
            line((x, 6, z), (x, 31, z), RIB)
    for x in (37, 53):
        box((x, 6, 49), (x, 12, 62), FRAME, True)
        box((x, 13, 49), (x, 23, 62), REINFORCED_GLASS, True)
        box((x, 24, 49), (x, 29, 62), CHEM, True)
        for z in (50, 56, 61):
            line((x, 6, z), (x, 29, z), POWER)

    # Give each exposed interface a direct structural connection to its machine.
    line((4, 6, 12), (4, 10, 12), POWER)
    line((1, 6, 32), (1, 7, 32), CHEM)
    line((19, 5, 62), (19, 7, 62), FRAME)
    line((40, 5, 63), (40, 7, 63), FRAME)
    line((55, 5, 32), (55, 10, 32), POWER)

    ports = [
        {'id': 'G-IN', 'pos': [28, 5, 0], 'face': 'north', 'purpose': 'I01-3气态崩坏能输入候选'},
        {'id': 'EU-IN', 'pos': [3, 6, 12], 'face': 'west', 'purpose': '双级气体压缩的能量输入候选'},
        {'id': 'C-IN', 'pos': [0, 7, 32], 'face': 'west', 'purpose': '冷端循环介质输入候选'},
        {'id': 'SOLID-OUT', 'pos': [20, 6, 62], 'face': 'south', 'purpose': '结晶固态崩坏能输出候选'},
        {'id': 'EU-OUT', 'pos': [40, 6, 64], 'face': 'south', 'purpose': '计量透平回收能量输出候选'},
        {'id': 'HEAT-OUT', 'pos': [56, 8, 32], 'face': 'east', 'purpose': '独立热端总廊废热排出候选'},
    ]
    for port in ports:
        put(*port['pos'], PORT, True)

    paths = [
        {'name': '正面主控及进料通道', 'min': [26, 1, 3], 'max': [30, 4, 18]},
        {'name': '西侧冷端检修带', 'min': [12, 1, 22], 'max': [14, 4, 47]},
        {'name': '东侧热端检修带', 'min': [41, 1, 22], 'max': [42, 4, 47]},
        {'name': '后场物流与透平检修通道', 'min': [24, 1, 49], 'max': [32, 4, 62]},
    ]
    bridge_count = bridge_disconnected(paths, ports, [28, 5, 22], 'north')

    zones = [
        {'name': '气态进料门与双级压缩廊', 'min': [2, 1, 4], 'max': [16, 30, 21], 'pos': [9, 30, 10],
         'description': '前廊以双列压缩机、传动环和架空进料管组织气态崩坏能，独立接入压缩能量。'},
        {'name': '虚数相界双笼承压塔', 'min': [14, 1, 17], 'max': [42, 58, 45], 'pos': [28, 57, 31],
         'description': '两道同轴承压笼壳构成双环轮廓：外笼布置三层约束环架，内笼采用高强观察壁包围相变核心；冠部计量框与高塔让相界成为厂区视觉中心。'},
        {'name': '西侧冷端塔院', 'min': [0, 1, 26], 'max': [13, 36, 42], 'pos': [7, 35, 34],
         'description': '两座不同高度的方形塔分别布置完整方块冷却组件和冷热集管，避免冷却端混入热排廊。'},
        {'name': '东侧多级换热与热排总廊', 'min': [43, 1, 23], 'max': [56, 42, 43], 'pos': [50, 41, 33],
         'description': '纵深换热鳍列、竖向热排塔和多层集管构成独立热端厂房，向外排出相变废热。'},
        {'name': '后场结晶分离与缓冲仓', 'min': [3, 1, 48], 'max': [20, 29, 62], 'pos': [11, 28, 57],
         'description': '四座可视化缓冲筒围绕过滤分离箱排列；固体产品经架空料线送至独立输出口。'},
        {'name': '后场计量透平厅', 'min': [37, 1, 48], 'max': [54, 31, 64], 'pos': [46, 30, 57],
         'description': '三列透平转子、玻璃计量梁和独立控制箱表现释能回收流程，并与热端废热塔保持空间分区。'},
    ]
    links = [
        {'name': '气态进料依次通过两级压缩器', 'points': gas_compression_points},
        {'name': '二级压缩出口至中央相界', 'points': phase_feed_points},
        {'name': '冷却与回流集管', 'points': [[4, 18, 32], [11, 18, 32], [18, 18, 32], [18, 18, 31]]},
        {'name': '释能流至换热庭院', 'points': [[38, 37, 31], [44, 37, 31], [44, 34, 31]]},
        {'name': '固态析出至缓冲筒', 'points': [[18, 18, 48], [15, 18, 48], [15, 18, 52], [15, 12, 52], [15, 12, 58]]},
        {'name': '固态产品至南侧输出口', 'points': solid_outlet_points},
        {'name': '计量释能至透平厅', 'points': [[39, 13, 36], [39, 13, 45], [44, 13, 45], [44, 13, 48]]},
        {'name': '透平回收能量输出', 'points': [[44, 20, 48], [44, 20, 63], [40, 20, 63], [40, 6, 63]]},
    ]
    blocks = [{'pos': list(pos), 'state': state}
              for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    data = {
        'key': 'i23', 'name': NAME, 'title': '崩坏能相变释能机',
        'candidate_version': '虚数相界·双环炉院V3・待审',
        'size': [W, H, D], 'blocks': blocks, 'block_count': len(blocks),
        'controller': [28, 5, 22], 'controller_face': 'north', 'ports': ports,
        'paths': paths,
        'zones': zones, 'links': links,
        'description': '气态接收、双级压缩、受控气固相变、固态析出、计量释能回收及冷热分区排放。',
        'target_voltage': None,
        'target_voltage_status': '未定；QCV/V06只见于待审映射，当前无I23可执行生产配方。',
        'role_materials': {FLOOR: ['连续厂区承台'], FRAME: ['深色主承力骨架'], POWER: ['高强承压环与设备立柱'],
                           PIPE: ['气态进料、释能及电能回收路线'], CHEM: ['耐蚀冷却、结晶与热侧路线'],
                           GLASS: ['中央相界观察壳与透平计量梁'], REINFORCED_GLASS: ['双层承压窗与缓冲仓观察壁'],
                           COOL: ['西侧冷端塔鳍及东侧换热鳍列'], COIL: ['外笼三层约束环与计量转子'],
                           GEAR: ['压缩传动、环级节点与透平轴系'], PORT: ['六个工艺接口占位'],
                           DIAMOND: ['核心/控制器候选标记'], GRATE: ['高位维护栈桥'],
                           COMPUTER: ['设备控制箱/塔冠模块'], COMPUTE: ['顶部环形计算节点'],
                           FILTER: ['固态析出过滤单元'], VENT: ['换热鳍汇流片']},
        'construction_notes': {
            'orientation': '宽度沿X轴，正面为-Z；实体范围57×59×65（X×Y×Z），对应占地表宽×长×高57×65×59；最低标准33×37×35。',
            'concept': '以崩坏能相变释能机的气态压缩、虚数相界约束、结晶析出和释能计量为造型主题；借鉴崩坏3的虚数空间意象与GregTech大型设备分区、骨架、管廊和检修庭院语言。',
            'interfaces': '六个industrial_port_casing占位块分别嵌入压缩、冷端、固态缓冲、计量透平及热端设备边界。',
            'controller': '主控占位位于宽度中线x=28、承压塔正面下缘，可从-Z方向的净空通道抵达。',
            'phase_vessel': '双环指同轴外侧线圈笼与内侧承压观察笼；三层约束环位于外笼，未宣称存在两套独立线圈。',
            'gas_path': '进料主线由G-IN接入第一级压缩器轴管，再经上跨管廊进入第二级压缩器轴管，最后送入中央相界。',
            'voltage': '暂不采用hk3gtl:voltage_machine_casing_*；待逐机工业线及实际配方定阶后再作新版本。',
            'flow': '工艺线仅是空间组织表达；预览不证明配方、损耗、研究或机器能力已接通。',
            'walkability': '正面、两侧与后场均留出贯通检修带；完整厂区基座位于y=0，不占检修净空层。',
        },
    }
    return data


def state_from_palette(entry) -> str:
    name = str(entry['Name'])
    props = entry.get('Properties', {})
    if props:
        pairs = sorted((str(k), str(v)) for k, v in props.items())
        return name + '[' + ','.join(f'{k}={v}' for k, v in pairs) + ']'
    return name


def components(occupied: set[tuple[int, int, int]]) -> int:
    remaining = set(occupied)
    count = 0
    while remaining:
        count += 1
        todo = [remaining.pop()]
        while todo:
            x, y, z = todo.pop()
            for nxt in ((x-1,y,z),(x+1,y,z),(x,y-1,z),(x,y+1,z),(x,y,z-1),(x,y,z+1)):
                if nxt in remaining:
                    remaining.remove(nxt)
                    todo.append(nxt)
    return count


def bridge_disconnected(paths: list[dict], ports: list[dict], controller: list[int],
                        controller_face: str) -> int:
    """Tie decorative subassemblies into the load-bearing frame without blocking access."""
    directions = ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0),
                  (0, 0, 1), (0, 0, -1))
    path_cells = set()
    for path in paths:
        lo, hi = path['min'], path['max']
        path_cells.update((x, y, z)
                          for x in range(lo[0], hi[0] + 1)
                          for y in range(lo[1], hi[1] + 1)
                          for z in range(lo[2], hi[2] + 1))
    faces = {'north': (0, 0, -1), 'south': (0, 0, 1),
             'east': (1, 0, 0), 'west': (-1, 0, 0)}
    reserved = set(path_cells)
    for port in ports:
        p = port['pos']
        delta = faces[port['face']]
        reserved.add(tuple(p[i] + delta[i] for i in range(3)))
    delta = faces[controller_face]
    reserved.add(tuple(controller[i] + delta[i] for i in range(3)))

    def groups() -> list[set[tuple[int, int, int]]]:
        remaining = set(CELLS)
        found = []
        while remaining:
            seed = remaining.pop()
            group = {seed}
            todo = [seed]
            while todo:
                x, y, z = todo.pop()
                for dx, dy, dz in directions:
                    q = (x + dx, y + dy, z + dz)
                    if q in remaining:
                        remaining.remove(q)
                        group.add(q)
                        todo.append(q)
            found.append(group)
        return found

    bridges = 0
    while True:
        parts = groups()
        if len(parts) == 1:
            return bridges
        main = max(parts, key=len)
        part = min((group for group in parts if group is not main), key=len)
        occupied = set(CELLS)
        queue = collections.deque(sorted(part))
        previous = {p: None for p in part}
        found = None
        while queue and found is None:
            current = queue.popleft()
            for dx, dy, dz in directions:
                q = (current[0] + dx, current[1] + dy, current[2] + dz)
                if q in main:
                    found = current
                    break
                if not (0 <= q[0] < W and 0 <= q[1] < H and 0 <= q[2] < D):
                    continue
                if q in occupied or q in reserved or q in previous:
                    continue
                previous[q] = current
                queue.append(q)
        if found is None:
            raise ValueError('找不到避开维护通道与接口净空的结构连接路径。')
        while found is not None and found not in part:
            put(*found, RIB)
            bridges += 1
            found = previous[found]


def audit(data: dict) -> dict:
    size_check = require(data)
    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    if any(state == 'minecraft:diamond_ore' for state in occupied.values()):
        raise ValueError('禁止使用 diamond_ore 作为接口标记。')
    if any('voltage_machine_casing_' in state for state in occupied.values()):
        raise ValueError('I23目标电压未确定，结构不得放入电压机壳。')
    if data['controller'][0] != W // 2 or occupied[tuple(data['controller'])] != DIAMOND:
        raise ValueError('主控候选必须在宽度中线并使用既定控制器标记。')
    for path in data['paths']:
        lo, hi = path['min'], path['max']
        blocked = [p for p in occupied if all(lo[i] <= p[i] <= hi[i] for i in range(3))]
        if blocked:
            raise ValueError(f'维护空间被占用：{path["name"]} {blocked[:3]}')
    direction = {'north': (0,0,-1), 'south': (0,0,1), 'east': (1,0,0), 'west': (-1,0,0)}
    port_positions = set()
    for port in data['ports']:
        p = tuple(port['pos'])
        if p in port_positions or occupied.get(p) != PORT:
            raise ValueError(f'接口不是唯一工业占位块：{port}')
        port_positions.add(p)
        dx,dy,dz = direction[port['face']]
        outward = (p[0]+dx,p[1]+dy,p[2]+dz)
        if outward in occupied:
            raise ValueError(f'接口前方无遮挡检查失败：{port["id"]} -> {outward}')
        inward = (p[0]-dx,p[1]-dy,p[2]-dz)
        if inward not in occupied:
            raise ValueError(f'接口内侧背接缺失：{port["id"]} -> {inward}')
    gas_link = next(link for link in data['links']
                    if link['name'] == '气态进料依次通过两级压缩器')
    phase_link = next(link for link in data['links']
                      if link['name'] == '二级压缩出口至中央相界')
    solid_link = next(link for link in data['links']
                      if link['name'] == '固态产品至南侧输出口')
    gas_points = [tuple(point) for point in gas_link['points']]
    if (6, 17, 9) not in gas_points or gas_points[-1] != (12, 17, 16):
        raise ValueError('气态主线没有依次接入两级压缩器的轴管。')
    for link in (gas_link, phase_link, solid_link):
        points = [tuple(point) for point in link['points']]
        for a, b in zip(points, points[1:]):
            dx = (b[0] > a[0]) - (b[0] < a[0])
            dy = (b[1] > a[1]) - (b[1] < a[1])
            dz = (b[2] > a[2]) - (b[2] < a[2])
            if sum(value != 0 for value in (dx, dy, dz)) > 1:
                raise ValueError(f'工艺主线不是轴向管路：{link["name"]} {a} -> {b}')
            cursor = a
            while True:
                if occupied.get(cursor) != PIPE:
                    raise ValueError(f'工艺主线在{cursor}处不连续：{link["name"]}')
                if cursor == b:
                    break
                cursor = (cursor[0] + dx, cursor[1] + dy, cursor[2] + dz)
    face = data['controller_face']
    dx, dy, dz = direction[face]
    controller = tuple(data['controller'])
    outward = (controller[0] + dx, controller[1] + dy, controller[2] + dz)
    if outward in occupied:
        raise ValueError(f'主控朝向没有可达空间：{face} -> {outward}')
    component_count = components(set(occupied))
    if component_count != 1:
        raise ValueError(f'存在分离结构组件：{component_count}')
    palette = collections.Counter(block['state'] for block in data['blocks'])
    marker_count = palette[PORT] + palette[DIAMOND]
    regular_count = sum(palette.values()) - marker_count
    source_counts = {'GT': 0, '整合包自定义': 0, '其他模组': 0, '原版建材': 0}
    for state, count in palette.items():
        if state in (PORT, DIAMOND):
            continue
        namespace = state.split(':', 1)[0]
        if namespace in ('gtceu', 'gtlcore'):
            source_counts['GT'] += count
        elif namespace in ('kubejs', 'hk3gtl'):
            source_counts['整合包自定义'] += count
        elif namespace == 'minecraft':
            source_counts['原版建材'] += count
        else:
            source_counts['其他模组'] += count
    material_sources = {
        key: {'count': count, 'share': round(count / regular_count, 4) if regular_count else 0}
        for key, count in source_counts.items()
    }
    return {'size_check': size_check, 'blocks': len(data['blocks']),
            'component_count': component_count, 'port_count': len(port_positions),
            'ports_are_embedded_and_exposed': True, 'controller_centered_and_accessible': True,
            'diamond_ore_count': 0, 'voltage_casing_count': 0,
            'walkable_paths_clear': True, 'palette': dict(sorted(palette.items())),
            'material_sources': {'ordinary_blocks': material_sources, 'denominator': regular_count,
                                 'excluded_markers': {'count': marker_count,
                                                      'states': {PORT: palette[PORT], DIAMOND: palette[DIAMOND]}}},
            'target_voltage': None, 'target_voltage_reason': '当前没有I23可执行生产配方；QCV/V06尚属待审映射。',
            'not_verified': ['正式Pattern与控制器注册', '输入输出能力与配方工艺',
                             '压缩能耗、转换损耗、回收量与热平衡数值',
                             '研究执行与生存模式材料可达', '游戏成型和运行']}


def load_old_payload() -> dict:
    encoded = OLD_DATA.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';').strip('"')
    return json.loads(gzip.decompress(base64.b64decode(encoded)).decode('utf-8'))


def draw_preview(data: dict, materials: list[dict], path: Path) -> None:
    textures = {}
    for material in materials:
        faces = material.get('faces', {})
        for face, value in faces.items():
            if not isinstance(value, str) or not value.startswith('data:image'):
                continue
            try:
                raw = base64.b64decode(value.split(',', 1)[1])
                with Image.open(__import__('io').BytesIO(raw)) as texture:
                    textures[(material['state'], face)] = tuple(
                        round(channel) for channel in texture.convert('RGB').resize((1,1)).getpixel((0,0)))
            except Exception:
                pass
    def color(state: str, face: str) -> tuple[int, int, int]:
        value = textures.get((state, face), textures.get((state, 'up'), (100, 118, 130)))
        return value
    def shade(c: tuple[int,int,int], factor: float) -> tuple[int,int,int]:
        return tuple(max(0,min(255,round(x*factor))) for x in c)
    scale, tile = 12, 6
    coords = [b['pos'] for b in data['blocks']]
    projected = []
    for x,y,z in coords:
        for px,py in ((x-z,(x+z)*tile-y*scale),
                      (x+1-z,(x+1+z)*tile-y*scale),
                      (x-(z+1),(x+z+1)*tile-y*scale),
                      (x-z,(x+z)*tile-(y+1)*scale),
                      (x+1-z,(x+1+z)*tile-(y+1)*scale),
                      (x-(z+1),(x+z+1)*tile-(y+1)*scale)):
            projected.append((px*scale, py))
    min_x=min(p[0] for p in projected); max_x=max(p[0] for p in projected)
    min_y=min(p[1] for p in projected); max_y=max(p[1] for p in projected)
    margin=110
    image=Image.new('RGB',(max_x-min_x+margin*2,max_y-min_y+margin*2),(17,27,39))
    draw=ImageDraw.Draw(image)
    ox=margin-min_x; oy=margin-min_y
    def proj(x: int,y: int,z: int) -> tuple[int,int]:
        return (ox+(x-z)*scale, oy+(x+z)*tile-y*scale)
    materials_by_state={m['state']:m for m in materials}
    for block in sorted(data['blocks'],key=lambda b:(b['pos'][0]+b['pos'][2],b['pos'][1],b['pos'][0])):
        x,y,z=block['pos']; state=block['state']
        top=[proj(x,y+1,z),proj(x+1,y+1,z),proj(x+1,y+1,z+1),proj(x,y+1,z+1)]
        east=[proj(x+1,y+1,z),proj(x+1,y+1,z+1),proj(x+1,y,z+1),proj(x+1,y,z)]
        south=[proj(x,y+1,z+1),proj(x+1,y+1,z+1),proj(x+1,y,z+1),proj(x,y,z+1)]
        draw.polygon(top,fill=color(state,'up'))
        draw.polygon(east,fill=shade(color(state,'east'),0.76))
        draw.polygon(south,fill=shade(color(state,'south'),0.58))
    font_path=Path('C:/Windows/Fonts/msyh.ttc')
    font=ImageFont.truetype(str(font_path),20) if font_path.exists() else ImageFont.load_default()
    draw.rectangle((0,0,image.width,42),fill=(11,17,25))
    w, d, h = data['size'][0], data['size'][2], data['size'][1]
    draw.text((18,8),'I23 崩坏能相变释能机 · 虚数相界·双环炉院 V3',font=font,fill=(234,243,246))
    draw.text((18,image.height-39),f'{w} × {d} × {h} (W × L × H)  |  6 embedded ports  |  target voltage pending',
              font=font,fill=(178,208,210))
    image.save(path)


def make_page(data: dict, verification: dict) -> str:
    w, d, h = data['size'][0], data['size'][2], data['size'][1]
    layer = h - 1
    ports=''.join(f'<li><code>{html.escape(p["id"])}</code> · {html.escape(p["purpose"])} · <code>{p["pos"]}</code></li>'
                  for p in data['ports'])
    zones=''.join(f'<details><summary>{html.escape(z["name"])}</summary><p>{html.escape(z["description"])}</p>'
                  f'<p class="muted">范围 <code>{z["min"]}</code> 至 <code>{z["max"]}</code></p></details>'
                  for z in data['zones'])
    mats=''.join(f'<li><code>{html.escape(state)}</code> × {count:,}（{count / verification["blocks"]:.2%}）</li>'
                 for state,count in verification['palette'].items())
    sources=verification['material_sources']
    source_summary=''.join(f'<li>{html.escape(name)}：{values["count"]:,}（{values["share"]:.2%}）</li>'
                           for name,values in sources['ordinary_blocks'].items())
    not_verified=''.join(f'<li>{html.escape(item)}</li>' for item in verification['not_verified'])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I23 崩坏能相变释能机 · V3</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#101a23;color:#e5edf0;font:14px/1.65 "Microsoft YaHei",sans-serif}}a{{color:#8ddbd0}}header{{height:74px;padding:10px 18px;border-bottom:1px solid #40525a;display:flex;align-items:center;justify-content:space-between;gap:16px}}h1{{font-size:22px;margin:0}}.sub{{color:#aec1c3}}main{{display:grid;grid-template-columns:minmax(0,1fr) 350px;height:calc(100vh - 74px)}}#stage{{position:relative;overflow:hidden;min-height:500px}}#stage canvas{{position:absolute;inset:0}}#labels{{position:absolute;inset:0;pointer-events:none}}#loading{{position:absolute;z-index:2;top:14px;left:14px;background:#172832;padding:9px 12px}}aside{{overflow:auto;padding:16px;border-left:1px solid #40525a}}section{{border-top:1px solid #34454c;padding:12px 0}}h2{{font-size:15px;margin:0 0 7px}}button{{background:#273a40;color:#e5edf0;border:1px solid #597178;padding:6px 8px;margin:2px;cursor:pointer}}input{{accent-color:#71c3b7}}details{{border-bottom:1px solid #34454c;padding:8px 0}}summary{{cursor:pointer}}.muted{{color:#a7b9bb}}code{{overflow-wrap:anywhere;color:#a8d6ca}}ul{{padding-left:19px}}li{{margin:5px 0}}.notice{{color:#f0d4a0}}@media(max-width:900px){{main{{height:auto;grid-template-columns:1fr}}#stage{{height:65vh;min-height:420px}}aside{{border-left:0;border-top:1px solid #40525a;max-height:none}}header{{height:auto;min-height:74px;align-items:flex-start;flex-direction:column}}}}</style></head><body>
<header><div><h1>崩坏能相变释能机 · 虚数相界·双环炉院 V3</h1><span class="sub">待审候选 · {w} × {d} × {h}（宽 × 长 × 高） · {verification['blocks']:,} 方块</span></div><span class="notice">目标电压未定</span></header>
<main><section id="stage"><div id="loading">正在载入本地逐格结构与材质…</div><div id="labels"></div></section><aside>
<section><h2>结构视角</h2><div><button data-view="front">前左</button><button data-view="right">前右</button><button data-view="back">后侧</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div><label>剖切高度 <b id="layerValue">{layer}</b><input id="layer" type="range" min="0" max="{layer}" value="{layer}" style="width:100%"></label><p><label><input id="showGlass" type="checkbox" checked>玻璃</label> <label><input id="showPorts" type="checkbox" checked>接口</label> <label><input id="showPaths" type="checkbox">净空</label> <label><input id="showZones" type="checkbox" checked>分区</label></p><button id="reset">重置</button><button id="saveImage">保存视角</button><p id="counts"></p><p id="status"></p></section>
<section><h2>工艺分区</h2>{zones}<p>工艺路线只用于表达设备空间关系，不代表已注册配方或能量收支。</p></section>
<section><h2>接口占位</h2><ul>{ports}</ul><p class="muted">使用 <code>hk3gtl:industrial_port_casing</code>，无功能方块；正式Pattern须按配方能力替换并复核。</p></section>
<section><h2>目标电压</h2><p>未定。当前无 I23 可执行生产配方；QCV/V06 仅在待审映射提案中出现，本候选不写入电压机壳。</p></section>
<section><h2>材料用量</h2><p>普通建材分母 {sources['denominator']:,}；指定钻石核心与接口标记另列，共 {sources['excluded_markers']['count']}</p><ul>{source_summary}</ul><ul>{mats}</ul></section>
<section><h2>静态检查</h2><p>尺寸：通过；实际范围 <code>{verification['size_check']['actual_xyz']}</code>，总表最低 <code>{verification['size_check']['baseline_wdh']}</code><br>连通组件：{verification['component_count']}<br>接口：{verification['port_count']} 个朝内背接、朝外无遮挡<br>中心主控：x={data['controller'][0]}，前侧可达<br>diamond_ore：0；电压机壳：0</p><h2>未验证</h2><ul>{not_verified}</ul></section>
<section><h2>文件</h2><a href="i23/{NAME}.nbt">NBT</a> · <a href="i23/{NAME}.schem">Sponge v2</a> · <a href="设计与检查.json">检查清单</a> · <a href="等轴预览.png">静态预览</a></section>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    structure_dir = OUT / 'i23'
    structure_dir.mkdir(exist_ok=True)
    scripts_dir = OUT / '生成脚本'
    scripts_dir.mkdir(exist_ok=True)

    data = build()
    verification = audit(data)
    _, _, hashes = export(data, structure_dir)
    old_payload = load_old_payload()
    old_materials = {item['state']: item for item in old_payload['materials']}
    if PORT not in old_materials:
        port_material = dict(old_materials[FRAME])
        port_material['state'] = PORT
        port_material['model'] = 'preview:industrial_port_casing_neutral'
        old_materials[PORT] = port_material
    states = sorted(verification['palette'])
    materials = [old_materials[state] for state in states]
    grouped = [[] for _ in states]
    state_ids = {state: i for i, state in enumerate(states)}
    for block in data['blocks']:
        x,y,z=block['pos']
        grouped[state_ids[block['state']]].append((y*D+z)*W+x)
    payload = {
        'data': {k:v for k,v in data.items() if k != 'blocks'},
        'palette': states, 'groups': grouped, 'materials': materials,
        'audit': verification, 'names': {},
    }
    encoded = base64.b64encode(gzip.compress(json.dumps(payload,separators=(',',':'),ensure_ascii=False).encode('utf-8'),compresslevel=9)).decode('ascii')
    (OUT/'data.js').write_text('window.HK3_PAYLOAD="'+encoded+'";\n',encoding='utf-8')
    shutil.copy2(VIEWER, OUT/'viewer.bundle.js')
    render_preview(data, materials, OUT)
    verification['hashes'] = hashes
    verification['source_geometry_reference'] = {
        'path': str(SOURCE/'设计与检查.json'),
        'role': '只参考功能分区和材料灵感；本候选由新布局独立生成。',
        'source_nbt_sha256': hashlib.sha256((SOURCE/'hk3gtl-i23-redesign-01.nbt').read_bytes()).hexdigest(),
    }
    verification['viewer_material_note'] = 'industrial_port_casing在浏览器材质图中借用钢机壳贴图作识别预览；NBT使用真实占位方块ID。'
    verification['preview_renderer'] = 'tools/structure_delivery/build_redesign69.py:render，读取项目材质逐面贴图并保留透明纹理。'
    (OUT/'设计与检查.json').write_text(json.dumps({'data': {k:v for k,v in data.items() if k != 'blocks'},
                                                   'audit': verification},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'index.html').write_text(make_page(data,verification),encoding='utf-8')
    script_name=Path(__file__).name
    shutil.copy2(Path(__file__), scripts_dir/script_name)

    source_nbt=SOURCE/'hk3gtl-i23-redesign-01.nbt'
    manifest={
        'key':'i23','title':'崩坏能相变释能机','candidate_version':data['candidate_version'],
        'status':'candidate_waiting_user_review','candidate_approved':False,
        'supersedes_internal_drafts':[{'version':'相态压缩换热列车V1','submitted_for_review':False},
                                      {'version':'相态压缩换热列车V2','submitted_for_review':False}],
        'supersedes_reason':'按用户最新要求将内测五占地尺寸作为最低标准进行大幅扩建；V1/V2均为内部迭代稿，V3是当前唯一待审版本。',
        'target_voltage':None,'target_voltage_status':data['target_voltage_status'],
        'size_xyz':data['size'],'size_wdh':[W,D,H],
        'baseline_wdh':verification['size_check']['baseline_wdh'],'block_count':len(data['blocks']),
        'controller':data['controller'],'ports':data['ports'],'palette':verification['palette'],
        'source_cache_nbt_sha256':hashlib.sha256(source_nbt.read_bytes()).hexdigest(),
        'nbt_sha256':hashes['nbt'],'schem_sha256':hashes['schem'],
        'claim_boundary':'候选外观与结构文件待审；未声明Pattern、配方、研究、生存获取或游戏运行通过。',
    }
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='verification.json'}
    verification['files_sha256_before_verification'] = files
    (OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    zip_path=OUT.with_suffix('.zip')
    if zip_path.exists():
        raise FileExistsError(f'拒绝覆盖已有候选ZIP：{zip_path}')
    with zipfile.ZipFile(zip_path,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                archive.write(path,path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError('候选 ZIP CRC 校验失败。')
        for name,expected in files.items():
            entries=[entry for entry in archive.namelist() if entry.endswith('/'+name)]
            if len(entries)!=1 or hashlib.sha256(archive.read(entries[0])).hexdigest()!=expected:
                raise ValueError(f'候选ZIP文件校验失败：{name}')
    zip_sha256=hashlib.sha256(zip_path.read_bytes()).hexdigest()
    receipt=zip_path.with_suffix('.zip.sha256')
    receipt.write_text(zip_sha256+'\n',encoding='ascii')
    print(json.dumps({'out':str(OUT),'zip':str(zip_path),'blocks':len(data['blocks']),
                      'size_xyz':data['size'],'components':verification['component_count'],
                      'target_voltage':None,'nbt_sha256':hashes['nbt'],'schem_sha256':hashes['schem'],
                      'zip_sha256':zip_sha256,'verified':True},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
