# -*- coding: utf-8 -*-
"""Build a review-only I24 long-baseline quantum observatory candidate."""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import json
import math
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from structure_size_baseline import ROOT, require

sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
from build_redesign69 import export, render as render_preview
from material_resources import Resources


OUT = ROOT / 'deliveries/I24_量子异常观测阵列_双基线干涉台与偏置数据厅_V1_20261024'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01/i24'
VIEWER_SOURCE = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22/三维评审.html'
VIEWER_BUNDLE = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22/viewer.bundle.js'
NAME = 'hk3gtl-i24-dual-baseline-observatory-v1-20261024'
W, H, D = 81, 61, 109

AIR = 'minecraft:air'
PORT = 'hk3gtl:industrial_port_casing'
CONTROLLER = 'minecraft:diamond_block'
FLOOR = 'gtceu:clean_machine_casing'
QEV = 'hk3gtl:voltage_machine_casing_qev'
DIMENSION = 'gtlcore:dimension_connection_casing'
INJECTION = 'gtlcore:dimension_injection_casing'
TRANSCENDENT = 'gtlcore:dimensionally_transcendent_casing'
GRAVITON = 'gtlcore:graviton_field_constraint_casing'
INFINITY = 'gtlcore:infinity_glass'
ECHO = 'gtlcore:echo_casing'
POWER = 'gtceu:high_power_casing'
COMPUTER = 'gtceu:advanced_computer_casing'
COMPUTE = 'gtlcore:super_computation_component[active=false]'
GEAR = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
REINFORCED_GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'

CELLS: dict[tuple[int, int, int], str] = {}


def put(x: int, y: int, z: int, state: str, replace: bool = False) -> None:
    if not (0 <= x < W and 0 <= y < H and 0 <= z < D):
        raise ValueError(f'越界方块 {(x, y, z)}: {state}')
    pos = (x, y, z)
    if replace or pos not in CELLS:
        CELLS[pos] = state


def box(lo: tuple[int, int, int], hi: tuple[int, int, int], state: str,
        replace: bool = False) -> None:
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def line(a: tuple[int, int, int], b: tuple[int, int, int], state: str,
         replace: bool = False) -> None:
    x, y, z = a
    dx = (b[0] > x) - (b[0] < x)
    dy = (b[1] > y) - (b[1] < y)
    dz = (b[2] > z) - (b[2] < z)
    if sum(value != 0 for value in (dx, dy, dz)) > 1:
        raise ValueError(f'线段不是轴向：{a} -> {b}')
    while True:
        put(x, y, z, state, replace)
        if (x, y, z) == b:
            break
        x, y, z = x + dx, y + dy, z + dz


def route(points: list[tuple[int, int, int]], state: str) -> None:
    for a, b in zip(points, points[1:]):
        line(a, b, state)


def ring_y(x0: int, x1: int, z0: int, z1: int, y: int, state: str) -> None:
    line((x0, y, z0), (x1, y, z0), state)
    line((x1, y, z0), (x1, y, z1), state)
    line((x1, y, z1), (x0, y, z1), state)
    line((x0, y, z1), (x0, y, z0), state)


def ring_z(x0: int, x1: int, y0: int, y1: int, z: int, state: str) -> None:
    line((x0, y0, z), (x1, y0, z), state)
    line((x1, y0, z), (x1, y1, z), state)
    line((x1, y1, z), (x0, y1, z), state)
    line((x0, y1, z), (x0, y0, z), state)


def aperture(cx: int, z: int) -> None:
    for radius, casing in ((7, DIMENSION), (5, QEV), (3, GRAVITON)):
        ring_z(cx - radius, cx + radius, 20 - radius, 20 + radius, z, casing)
    for outer, inner, material in ((7, 5, DIMENSION), (5, 3, QEV)):
        line((cx - outer, 20, z), (cx - inner, 20, z), material)
        line((cx + inner, 20, z), (cx + outer, 20, z), material)
        line((cx, 20 - outer, z), (cx, 20 - inner, z), material)
        line((cx, 20 + inner, z), (cx, 20 + outer, z), material)
    box((cx - 2, 18, z), (cx + 2, 22, z), INFINITY)


def station(cx: int, z0: int, z1: int, front_z: int, inner_z: int) -> None:
    x0, x1 = cx - 8, cx + 8
    box((x0, 0, z0), (x1, 2, z1), FLOOR)
    for y, material in ((4, DIMENSION), (15, QEV), (31, TRANSCENDENT), (34, DIMENSION)):
        ring_y(x0, x1, z0, z1, y, material)
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1),
                 (cx - 6, z0 + 3), (cx + 6, z0 + 3),
                 (cx - 6, z1 - 3), (cx + 6, z1 - 3)):
        line((x, 2, z), (x, 34, z), POWER)
    for x in (x0, x1):
        line((x, 5, z0), (x, 5, z1), QEV)
        for z in range(z0 + 4, z1 - 3):
            put(x, 6, z, QEV)
            put(x, 7, z, REINFORCED_GLASS)
            put(x, 8, z, REINFORCED_GLASS)
            put(x, 9, z, QEV)
        line((x, 11, z0), (x, 11, z1), DIMENSION)
        line((x, 25, z0), (x, 25, z1), QEV)
    for z in (z0 + 2, z1 - 2):
        for y in (5, 11, 26, 30):
            line((x0 + 1, y, z), (x1 - 1, y, z), DIMENSION if y in (11, 30) else QEV)
        aperture(cx, z)
    aperture(cx, front_z)
    aperture(cx, inner_z)
    for x in (cx - 6, cx + 6):
        line((x, 2, (z0 + z1) // 2), (x, 30, (z0 + z1) // 2), GRAVITON)
        for y in (9, 15, 21, 27):
            put(x, y, (z0 + z1) // 2, COMPUTE)
    for x in range(x0 + 2, x1 - 1, 3):
        line((x, 34, z0), (x, 34, z1), GRATE)


def build() -> dict:
    CELLS.clear()

    # Four precision apertures form two long, independent interferometer baselines.
    for cx in (12, 27):
        station(cx, 0, 22, 0, 20)
        station(cx, 87, 108, 108, 89)
        for x in (cx - 8, cx + 8):
            line((x, 5, 22), (x, 5, 87), DIMENSION)
            line((x, 16, 22), (x, 16, 87), QEV)
            line((x, 34, 22), (x, 34, 87), TRANSCENDENT)
            for z in range(28, 84, 14):
                line((x, 0, z), (x, 34, z), POWER)
            line((x, 18, 22), (x, 18, 87), GRAVITON)
        for x in (cx - 7, cx + 7):
            line((x, 34, 22), (x, 40, 22), DIMENSION)
            line((x, 34, 87), (x, 40, 87), DIMENSION)
        for z in range(29, 84, 14):
            line((cx - 8, 8, z), (cx + 8, 8, z), GRATE)
            line((cx - 8, 40, z), (cx + 8, 40, z), DIMENSION)
        for z in (28, 42, 56, 70, 84):
            for x in (cx - 5, cx + 5):
                ring_y(x - 1, x + 1, z - 1, z + 1, 18, GRAVITON)
                rail_x = cx - 8 if x < cx else cx + 8
                line((x, 18, z), (rail_x, 18, z), GRAVITON)
                line((x, 17, z), (x, 30, z), INJECTION)
                put(x, 24, z, COMPUTE)

    # The probe exchange room grows directly out of the north-west instrument house.
    box((0, 0, 7), (8, 3, 20), FLOOR)
    for y, material in ((4, DIMENSION), (18, QEV), (24, DIMENSION)):
        ring_y(0, 8, 7, 20, y, material)
    for z in (7, 20):
        line((0, 4, z), (0, 24, z), POWER)
        line((8, 4, z), (8, 24, z), POWER)
        box((1, 6, z), (7, 16, z), REINFORCED_GLASS)
    for y in (7, 8, 9, 10):
        line((0, y, 11), (0, y, 17), QEV, True)
    for y in range(5, 17):
        put(0, y, 11, QEV, True)
        put(0, y, 17, QEV, True)

    # Long transfer rails stay beside and above the clear optical axes.
    for cx in (12, 27):
        for x in (cx - 7, cx + 7):
            line((x, 12, 21), (x, 12, 88), INJECTION)
            line((x, 40, 21), (x, 40, 88), DIMENSION)
        for z in (24, 36, 48, 60, 72, 84):
            line((cx - 7, 12, z), (cx + 7, 12, z), GEAR)
            line((cx - 7, 40, z), (cx + 7, 40, z), TRANSCENDENT)

    # Offset data hall: its west wall sits on the overall width centreline.
    box((40, 0, 38), (75, 3, 72), FLOOR)
    for y, material in ((4, DIMENSION), (18, QEV), (34, TRANSCENDENT), (37, DIMENSION)):
        ring_y(40, 75, 38, 72, y, material)
    for x, z in ((40, 38), (75, 38), (40, 72), (75, 72),
                 (40, 55), (75, 55), (58, 38), (58, 72)):
        line((x, 3, z), (x, 37, z), POWER if x in (40, 75) else QEV)
    for z in (38, 72):
        box((42, 6, z), (73, 29, z), QEV)
        for x0 in (46, 64):
            box((x0, 13, z), (x0 + 5, 25, z), INFINITY, True)
            for x in (x0, x0 + 5):
                line((x, 12, z), (x, 26, z), DIMENSION, True)
    for x in (40, 75):
        box((x, 6, 40), (x, 30, 70), QEV)
    for z0, z1 in ((43, 49), (62, 68)):
        box((40, 14, z0), (40, 26, z1), INFINITY, True)
        for z in (z0 - 1, z1 + 1):
            line((40, 13, z), (40, 27, z), DIMENSION, True)
    for x in (42, 49, 56, 63, 70, 73):
        for z in (40, 70):
            line((x, 3, z), (x, 32, z), GRAVITON)
    for y in (9, 16, 23, 30):
        line((41, y, 40), (74, y, 40), DIMENSION)
        line((41, y, 72), (74, y, 72), DIMENSION)

    # Six computation stacks sit behind the observation wall and below the crown.
    for cx in (49, 58, 67):
        for cz in (47, 63):
            ring_y(cx - 3, cx + 3, cz - 3, cz + 3, 7, GEAR)
            ring_y(cx - 3, cx + 3, cz - 3, cz + 3, 26, DIMENSION)
            for x, z in ((cx - 3, cz - 3), (cx + 3, cz - 3),
                         (cx - 3, cz + 3), (cx + 3, cz + 3)):
                line((x, 3, z), (x, 7, z), POWER)
                line((x, 7, z), (x, 26, z), QEV)
            for x, z in ((cx - 3, cz), (cx + 3, cz),
                         (cx, cz - 3), (cx, cz + 3)):
                line((x, 7, z), (x, 26, z), QEV)
            for y in (10, 16, 22):
                ring_y(cx - 2, cx + 2, cz - 2, cz + 2, y, GRAVITON)
            box((cx - 1, 11, cz - 1), (cx + 1, 23, cz + 1), COMPUTE)
            put(cx, 17, cz, COMPUTER, True)
            line((cx - 3, 16, cz), (cx + 3, 16, cz), GRAVITON)
            line((cx, 16, cz - 3), (cx, 16, cz + 3), GRAVITON)
            put(cx - 3, 18, cz, VENT, True)
            put(cx + 3, 18, cz, VENT, True)

    # A stepped, offset zenith receiver makes the data hall the visual anchor.
    for x, z in ((49, 47), (59, 47), (69, 47), (49, 57), (69, 57),
                 (49, 67), (59, 67), (69, 67)):
        line((x, 3, z), (x, 37, z), POWER)
    ring_y(49, 69, 47, 67, 37, GRATE)
    ring_y(49, 69, 47, 67, 38, DIMENSION)
    for y, inset, material in ((41, 0, GRAVITON), (46, 2, QEV),
                               (51, 4, DIMENSION), (56, 6, TRANSCENDENT),
                               (60, 7, INJECTION)):
        ring_y(49 + inset, 69 - inset, 47 + inset, 67 - inset, y, material)
        if inset:
            for z in (47 + inset, 67 - inset):
                line((49, 37, z), (49 + inset, 37, z), DIMENSION)
                line((69 - inset, 37, z), (69, 37, z), DIMENSION)
            for x in (49 + inset, 69 - inset):
                line((x, 37, 47), (x, 37, 47 + inset), DIMENSION)
                line((x, 37, 67 - inset), (x, 37, 67), DIMENSION)
        for x in (49 + inset, 69 - inset):
            for z in (47 + inset, 67 - inset):
                line((x, 37, z), (x, y, z), POWER)
    for x, z in ((49, 47), (69, 47), (49, 67), (69, 67)):
        line((x, 38, z), (x, 60, z), TRANSCENDENT)
    ring_y(55, 63, 53, 61, 59, QEV)
    line((59, 40, 57), (59, 60, 57), GRAVITON)
    line((57, 40, 57), (61, 40, 57), INFINITY)
    line((57, 60, 57), (61, 60, 57), INFINITY)
    put(59, 60, 57, COMPUTE, True)
    for x in range(52, 67, 4):
        line((x, 37, 55), (x, 37, 59), GRATE)
    line((60, 37, 57), (60, 40, 57), QEV)
    line((55, 59, 57), (59, 59, 57), QEV)
    line((59, 59, 57), (63, 59, 57), QEV)

    # The upper data spine joins both baselines to the elevated analysis crown.
    for x in (19, 34):
        line((x, 39, 55), (x, 42, 55), POWER)
    line((19, 42, 55), (40, 42, 55), DIMENSION)
    line((34, 40, 55), (40, 40, 55), TRANSCENDENT)
    line((40, 37, 55), (40, 42, 55), QEV)
    line((40, 42, 55), (49, 42, 55), DIMENSION)

    # A shielded power and calibration annex is attached to the hall by a low service neck.
    box((66, 0, 78), (80, 3, 108), FLOOR)
    for y, material in ((4, DIMENSION), (18, POWER), (31, QEV), (35, DIMENSION)):
        ring_y(66, 80, 78, 108, y, material)
    for x, z in ((66, 78), (80, 78), (66, 108), (80, 108),
                 (73, 78), (73, 108), (66, 93), (80, 93)):
        line((x, 3, z), (x, 35, z), POWER)
    box((80, 6, 80), (80, 26, 107), POWER)
    for z in (82, 88, 98, 104):
        box((66, 7, z), (66, 26, z + 1), QEV)
        box((80, 7, z), (80, 26, z + 1), POWER)
    for cx, cz in ((70, 86), (76, 86), (70, 100), (76, 100)):
        ring_y(cx - 2, cx + 2, cz - 2, cz + 2, 6, GEAR)
        ring_y(cx - 2, cx + 2, cz - 2, cz + 2, 29, QEV)
        for x, z in ((cx - 2, cz - 2), (cx + 2, cz - 2),
                     (cx - 2, cz + 2), (cx + 2, cz + 2)):
            line((x, 2, z), (x, 29, z), POWER)
        for x, z in ((cx - 2, cz), (cx + 2, cz),
                     (cx, cz - 2), (cx, cz + 2)):
            line((x, 6, z), (x, 29, z), POWER)
        for y in (11, 18, 25):
            ring_y(cx - 1, cx + 1, cz - 1, cz + 1, y, GRAVITON)
        line((cx, 8, cz), (cx, 28, cz), COMPUTE)
        line((cx - 2, 18, cz), (cx + 2, 18, cz), GRAVITON)
        line((cx, 18, cz - 2), (cx, 18, cz + 2), GRAVITON)
    for z in range(80, 107, 4):
        line((67, 9, z), (79, 9, z), GRATE)
    route([(73, 12, 72), (73, 12, 76), (73, 12, 82)], DIMENSION)

    # Each marked surface has an interior equipment route immediately behind it.
    route([(1, 8, 14), (5, 8, 14), (12, 8, 14)], INJECTION)
    route([(58, 8, 39), (58, 8, 45), (58, 8, 51)], ECHO)
    route([(58, 8, 71), (58, 8, 65), (58, 8, 60)], ECHO)
    route([(79, 8, 93), (76, 8, 93), (73, 8, 93)], INJECTION)
    route([(41, 8, 55), (45, 8, 55)], DIMENSION)

    # Four candidate connections replace blocks in the actual instrument/equipment skins.
    ports = [
        {'id': 'PROBE-IN', 'pos': [0, 8, 14], 'face': 'west',
         'surface_state': QEV, 'purpose': '空间探针与参考样本输入候选'},
        {'id': 'DATA-IN', 'pos': [58, 8, 38], 'face': 'north',
         'surface_state': QEV, 'purpose': '空间实验数据载体输入候选'},
        {'id': 'OBSERVATION-OUT', 'pos': [58, 8, 72], 'face': 'south',
         'surface_state': QEV, 'purpose': '量子异常谱与观测记录载体输出候选'},
        {'id': 'ENERGY-IN', 'pos': [80, 8, 93], 'face': 'east',
         'surface_state': POWER, 'purpose': '阵列与校准设施供能输入候选'},
    ]
    for port in ports:
        put(*port['pos'], PORT, True)

    controller = [40, 8, 55]
    put(*controller, CONTROLLER, True)
    blocks = [{'pos': list(pos), 'state': state}
              for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))]
    return {
        'key': 'i24', 'name': NAME, 'title': '量子异常观测阵列',
        'candidate_version': '双基线干涉台与偏置数据厅 V1・待审',
        'size': [W, H, D], 'blocks': blocks, 'block_count': len(blocks),
        'controller': controller, 'controller_face': 'west', 'controller_surface': QEV,
        'ports': ports,
        'paths': [
            {'name': '西侧北南基线检修廊', 'min': [3, 3, 22], 'max': [20, 11, 87]},
            {'name': '东侧北南基线检修廊', 'min': [19, 3, 22], 'max': [35, 11, 87]},
            {'name': '主控与分析厅前场', 'min': [36, 3, 42], 'max': [40, 7, 68]},
            {'name': '供能 annex 服务通道', 'min': [68, 3, 73], 'max': [78, 7, 83]},
        ],
        'zones': [
            {'name': '双端平行基线观测站', 'min': [4, 0, 0], 'max': [35, 40, 108],
             'pos': [20, 40, 55],
             'description': '两条平行而独立的长基线分别连接前后端观测舱；四面嵌入式透镜框围绕空置光轴，框架、同步器与下层检修栈沿轴线布置。'},
            {'name': '探针接收与校准舱', 'min': [0, 0, 7], 'max': [8, 24, 20],
             'pos': [4, 23, 13],
             'description': '接收探针与参考样本的入口位于舱体连续QEV外壳，舱体直接嵌进北端观测站侧翼。'},
            {'name': '偏置量子计算与记录厅', 'min': [40, 0, 38], 'max': [75, 60, 72],
             'pos': [59, 60, 57],
             'description': '计算机壳、分层计算栈与高位接收冠偏置在两条观测轴以东；主控位于整机宽度中线的西立面，观察通道保持无遮挡。'},
            {'name': '屏蔽供能与场校准厅', 'min': [66, 0, 78], 'max': [80, 35, 108],
             'pos': [73, 34, 94],
             'description': '四组高功率校准单元置于屏蔽壳内，以低位服务颈接入数据厅；供能接口齐平嵌入东侧设备墙。'},
        ],
        'links': [
            {'name': '西基线原始观测信号', 'points': [[4, 12, 21], [4, 12, 55], [4, 12, 88]]},
            {'name': '东基线原始观测信号', 'points': [[35, 12, 21], [35, 12, 55], [35, 12, 88]]},
            {'name': '双路数据进入偏置计算厅', 'points': [[19, 42, 55], [34, 42, 55], [40, 42, 55], [49, 42, 55]]},
            {'name': '屏蔽供能接入设备厅', 'points': [[73, 12, 72], [73, 12, 76], [73, 12, 82]]},
        ],
        'description': '以两条拉开的平行干涉基线捕获、复测并交叉校验异常谱；偏置数据厅生成观测事实记录，交由I25解析、I44锁定。',
        'target_voltage_appearance': '按负责人决定采用《多方块结构电压映射提案 V1》对应条目：QEV / V07；Controller tier与实机运行仍待验收。',
        'role_materials': {
            FLOOR: ['各仪器、计算厅与服务附属设施的分段基础'],
            QEV: ['分析厅承力壳、观测站外壳与原位主控载体'],
            DIMENSION: ['基线联接梁、设备环箍与数据桥'],
            INJECTION: ['嵌入式探测元件和信号/校准节点'],
            TRANSCENDENT: ['上层空间测量框与结构转换环'],
            GRAVITON: ['镜组固定箍、同步阵列和计算栈精密框'],
            INFINITY: ['端点透镜、观测窗与中央接收元件'],
            POWER: ['屏蔽供能厅及长跨度承重塔架'],
            COMPUTE: ['偏置数据厅计算栈与高位接收器'],
            PORT: ['原设备壳表面的无功能接口候选标记'],
            CONTROLLER: ['QEV外壳宽度中线位置的控制器候选标记'],
        },
    }


def neighbor_components(occupied: set[tuple[int, int, int]]) -> int:
    remaining = set(occupied)
    components = 0
    offsets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            x, y, z = stack.pop()
            for dx, dy, dz in offsets:
                pos = (x + dx, y + dy, z + dz)
                if pos in remaining:
                    remaining.remove(pos)
                    stack.append(pos)
    return components


def audit(data: dict) -> dict:
    size_check = require(data)
    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    components = neighbor_components(set(occupied))
    face = {'west': (1, 0, 0), 'east': (-1, 0, 0),
            'north': (0, 0, 1), 'south': (0, 0, -1)}
    outside = {'west': (-1, 0, 0), 'east': (1, 0, 0),
               'north': (0, 0, -1), 'south': (0, 0, 1)}
    port_checks = []
    for port in data['ports']:
        x, y, z = port['pos']
        dx, dy, dz = face[port['face']]
        ox, oy, oz = outside[port['face']]
        if occupied.get((x, y, z)) != PORT:
            raise ValueError(f"接口标记缺失：{port['id']}")
        if port['face'] in ('north', 'south'):
            neighbors = [(x + sx, y + sy, z) for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        else:
            neighbors = [(x, y + sy, z + sz) for sy, sz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        same_shell = sum(occupied.get(pos) == port['surface_state'] for pos in neighbors)
        inward = (x + dx, y + dy, z + dz)
        outward = (x + ox, y + oy, z + oz)
        check = {
            'id': port['id'], 'surface_state': port['surface_state'],
            'continuous_casing_neighbors': same_shell,
            'inward_surface_route_backed': inward in occupied,
            'outward_clear': outward not in occupied,
        }
        if same_shell < 3 or inward not in occupied or outward in occupied:
            raise ValueError(f"接口未齐平融合或维护面受阻：{check}")
        port_checks.append(check)

    controller = tuple(data['controller'])
    if controller[0] != W // 2 or occupied.get(controller) != CONTROLLER:
        raise ValueError('主控未放在整机宽度中线或控制器标记缺失。')
    if (controller[0] - 1, controller[1], controller[2]) in occupied:
        raise ValueError('主控西侧操作空间受阻。')
    optical_axis = {
        str(cx): sum((cx, 20, z) in occupied for z in range(22, 88))
        for cx in (12, 27)
    }
    if any(optical_axis.values()):
        raise ValueError(f'观测轴净空检查失败：{optical_axis}')

    palette = collections.Counter(block['state'] for block in data['blocks'])
    floor_count = sum(block['pos'][1] == 0 for block in data['blocks'])
    if components != 1:
        raise ValueError(f'整机连通性检查失败：存在 {components} 个断开的结构群。')
    checks = [
        f'实际边界 {size_check["actual_xyz"]} 与声明尺寸一致，且逐轴达到最低标准。',
        f'整机连通性通过：{components} 个连续结构组件。',
        f'主控位于宽度中线 X={controller[0]}，西侧操作空间畅通。',
        f'{len(port_checks)} 个接口齐平嵌入设备外壳，内侧有设备连接且外向无遮挡。',
        '两条 y=20 观测光轴净空通过。',
    ]
    return {
        'time': dt.datetime.now().astimezone().isoformat(),
        'size_check': size_check, 'blocks': len(data['blocks']),
        'checks': checks,
        'component_count': components, 'controller_centered': True,
        'controller_accessible': True, 'controller_surface_state': data['controller_surface'],
        'port_count': len(port_checks), 'ports_are_flush_mounted_on_equipment_shells': True,
        'port_surface_checks': port_checks, 'optical_axis_blockers_at_y20': optical_axis,
        'palette': dict(palette), 'ground_footprint_blocks': floor_count,
        'ground_footprint_ratio': round(floor_count / len(data['blocks']), 4),
        'not_verified': [
            '正式Pattern、控制器注册与接口真实能力',
            'I24工艺配方、研究执行器注册与运行',
            'I24 Controller tier是否注册为QEV/V07及对应机器的游戏内运行',
            '生存模式材料可达性、游戏内成型与2.9.2兼容性',
            '管线与分区是建筑表达，不证明资源生产、坐标锁定或采掘功能已实现',
        ],
    }


def color(state: str | None) -> tuple[int, int, int]:
    palette = {
        FLOOR: (187, 195, 198), QEV: (53, 80, 139),
        DIMENSION: (76, 62, 121), INJECTION: (181, 72, 87),
        TRANSCENDENT: (90, 131, 163), GRAVITON: (104, 105, 145),
        INFINITY: (84, 176, 182), ECHO: (118, 110, 144), POWER: (62, 104, 141),
        COMPUTER: (144, 157, 174), COMPUTE: (139, 121, 181), GEAR: (103, 120, 135),
        VENT: (114, 165, 164), GRATE: (142, 153, 157), REINFORCED_GLASS: (119, 171, 183),
        PORT: (229, 186, 93), CONTROLLER: (236, 215, 143),
    }
    return palette.get(state, (92, 103, 114))


def font(size: int):
    path = Path('C:/Windows/Fonts/msyh.ttc')
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def render_report_images(data: dict, out: Path) -> None:
    width, height, depth = data['size']
    scale, left, top = 10, 58, 105
    image = Image.new('RGB', (1450, 1350), '#14212d')
    draw = ImageDraw.Draw(image)
    draw.text((44, 30), 'I24 · 双基线观测阵列 / 设备平面与齐平接口', font=font(28), fill='#e5edf3')
    tops: dict[tuple[int, int], tuple[int, str]] = {}
    for block in data['blocks']:
        x, y, z = block['pos']
        if (x, z) not in tops or y >= tops[(x, z)][0]:
            tops[(x, z)] = (y, block['state'])
    for (x, z), (y, state) in tops.items():
        base = color(state)
        lift = min(24, y // 3)
        draw.rectangle((left + x * scale, top + z * scale,
                        left + x * scale + scale - 1, top + z * scale + scale - 1),
                       fill=tuple(min(255, c + lift) for c in base))
    draw.rectangle((left - 1, top - 1, left + width * scale, top + depth * scale),
                   outline='#8798a5', width=2)
    draw.text((left, top - 31), '北 / 前端观测站', font=font(17), fill='#c4d0d8')
    draw.text((left, top + depth * scale + 8), '南 / 远端观测站', font=font(17), fill='#c4d0d8')
    legend_x, legend_y = 920, 120
    draw.text((legend_x, legend_y), '设备壳接口与宽度中线', font=font(22), fill='#f0d4a0')
    for index, port in enumerate(data['ports']):
        x, _, z = port['pos']
        px, pz = left + x * scale + scale // 2, top + z * scale + scale // 2
        draw.ellipse((px - 6, pz - 6, px + 6, pz + 6), fill='#f4c66c', outline='#17212a', width=2)
        draw.text((legend_x, legend_y + 40 + index * 46),
                  f"{port['id']} {port['purpose']} {port['pos']}", font=font(16), fill='#e5edf3')
    center_x = left + data['controller'][0] * scale + scale // 2
    draw.line((center_x, top, center_x, top + depth * scale), fill='#f0d477', width=2)
    draw.text((legend_x, legend_y + 40 + len(data['ports']) * 46 + 20),
              '黄色纵线：整机宽度中线；两条观测光轴在平面图中保持分离。',
              font=font(17), fill='#d5dfe4')
    image.save(out / '俯视布局.png')

    # Longitudinal silhouette shows the tall offset analysis crown and separated stations.
    elevation = Image.new('RGB', (1500, 820), '#14212d')
    ed = ImageDraw.Draw(elevation)
    cell, eleft, etop = 10, 110, 96
    ed.text((45, 30), 'I24 · 北南纵向立面 / 两条观测基线与偏置分析厅',
            font=font(27), fill='#e5edf3')
    profile: dict[tuple[int, int], str] = {}
    for block in data['blocks']:
        x, y, z = block['pos']
        key = (z, y)
        state = block['state']
        if key not in profile or state in (QEV, INFINITY, TRANSCENDENT, PORT, CONTROLLER):
            profile[key] = state
    for (z, y), state in profile.items():
        ed.rectangle((eleft + z * cell, etop + (H - 1 - y) * cell,
                      eleft + z * cell + cell - 1, etop + (H - y) * cell - 1),
                     fill=color(state))
    ed.text((eleft, etop + H * cell + 12), '前端 / Z=0', font=font(17), fill='#c4d0d8')
    ed.text((eleft + depth * cell - 130, etop + H * cell + 12), '远端 / Z=108',
            font=font(17), fill='#c4d0d8')
    elevation.save(out / '纵向立面.png')

    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    cx, cy, cz = data['controller']
    cell, left, top = 36, 110, 96
    detail = Image.new('RGB', (1000, 760), '#14212d')
    dd = ImageDraw.Draw(detail)
    dd.text((38, 28), '控制器候选位置 · 分析厅西立面局部', font=font(27), fill='#e5edf3')
    dd.text((38, 66), f'宽度中线 X={cx} · 坐标 {data["controller"]} · 面向西',
            font=font(18), fill='#b9c7ce')
    for y in range(0, 17):
        for x in range(cx - 11, cx + 6):
            state = occupied.get((x, y, cz))
            px, py = left + (x - (cx - 11)) * cell, top + (16 - y) * cell
            dd.rectangle((px, py, px + cell - 1, py + cell - 1),
                         fill=color(state) if state else (24, 38, 49), outline='#263a48')
    marker_x = left + 11 * cell
    dd.line((marker_x + cell // 2, top - 12, marker_x + cell // 2, top + 17 * cell),
            fill='#f0d477', width=2)
    dd.text((left, top + 17 * cell + 12), '标记嵌在连续QEV设备壳；面向检修前场留空。',
            font=font(17), fill='#d6e0e5')
    detail.save(out / '主控正立面.png')

    panel = Image.new('RGB', (1450, 870), '#14212d')
    pd = ImageDraw.Draw(panel)
    pd.text((42, 26), '四个候选接口 · 实际设备外壳齐平替换', font=font(27), fill='#e5edf3')
    cell, panel_w, panel_h = 330, 700, 375
    for i, port in enumerate(data['ports']):
        left, top = 35 + (i % 2) * panel_w, 82 + (i // 2) * panel_h
        pd.rounded_rectangle((left, top, left + panel_w - 24, top + panel_h - 25),
                             5, fill='#1b2a36', outline='#405565', width=2)
        pd.text((left + 18, top + 10), f"{port['id']} · {port['purpose']}",
                font=font(17), fill='#e5edf3')
        pd.text((left + 18, top + 38),
                f"{port['pos']} · {port['face']} · {port['surface_state']}",
                font=font(13), fill='#aebfc8')
        x, y, z = port['pos']
        if port['face'] in ('north', 'south'):
            coords = [((x + dx, y + dy, z), dx, dy)
                      for dy in range(3, -4, -1) for dx in range(-3, 4)]
        else:
            coords = [((x, y + dy, z + dz), dz, dy)
                      for dy in range(3, -4, -1) for dz in range(-3, 4)]
        grid_left, grid_top = left + 228, top + 78
        for pos, gx, gy in coords:
            px, py = grid_left + (gx + 3) * 38, grid_top + (3 - gy) * 38
            state = occupied.get(pos)
            pd.rectangle((px, py, px + 37, py + 37),
                         fill=color(state) if state else (24, 38, 49), outline='#344957')
            if pos == tuple(port['pos']):
                pd.rectangle((px + 3, py + 3, px + 34, py + 34), outline='#ffe18c', width=3)
    panel.save(out / '接口外壳立面.png')

    iso = Image.open(out / '等轴预览.png').convert('RGB')
    draw = ImageDraw.Draw(iso)
    draw.rectangle((0, 0, iso.width, 42), fill=(11, 17, 25))
    draw.text((18, 8), 'I24 量子异常观测阵列 · 双基线 V1', font=font(20), fill=(234, 243, 246))
    draw.rectangle((0, iso.height - 39, iso.width, iso.height), fill=(11, 17, 25))
    draw.text((18, iso.height - 34),
              f'{W} × {D} × {H} (W × L × H) | 4 flush-mounted interfaces | QEV / V07 target mapping',
              font=font(19), fill=(178, 208, 210))
    iso.save(out / '等轴预览.png')


def make_report_page(data: dict, check: dict) -> str:
    w, h, d = data['size']
    ports = ''.join(
        f"<tr><td><code>{html.escape(p['id'])}</code></td><td>{html.escape(p['purpose'])}</td>"
        f"<td><code>{p['pos']}</code></td><td>{html.escape(p['face'])}</td>"
        f"<td><code>{html.escape(p['surface_state'])}</code></td></tr>" for p in data['ports'])
    zones = ''.join(
        f"<details><summary>{html.escape(z['name'])}</summary><p>{html.escape(z['description'])}</p>"
        f"<p>范围 <code>{z['min']}</code> 至 <code>{z['max']}</code></p></details>"
        for z in data['zones'])
    materials = ''.join(
        f"<tr><td><code>{html.escape(state)}</code></td><td>{count:,}</td></tr>"
        for state, count in check['palette'].items())
    source_text = ''.join(f"<li>{html.escape(item)}</li>" for item in check['not_verified'])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I24 量子异常观测阵列 · V1</title>
<style>body{{margin:0;background:#14212d;color:#e5edf3;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1320px;margin:auto;padding:30px}}header{{padding:26px;background:#303954;border-left:5px solid #70bec0}}h1{{margin:0}}h2{{margin-top:34px}}a{{color:#b9dfdc}}img{{max-width:100%;height:auto}}iframe{{width:100%;height:850px;border:1px solid #69718a}}.notice{{background:#3c3827;border-left:4px solid #d0b872;padding:15px}}code{{overflow-wrap:anywhere}}small{{color:#b9c3d1}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}.grid>div{{background:#202d3c;padding:12px;border:1px solid #405066}}.scroll{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:800px}}th,td{{text-align:left;border-bottom:1px solid #405066;padding:9px}}@media(max-width:700px){{main{{padding:16px}}header{{padding:18px}}iframe{{height:680px}}}}</style></head><body><main>
<header><small>HK3GTL / I24 / 建筑候选V1</small><h1>量子异常观测阵列</h1><p>两条拉开的北南干涉基线连接四座端点观测站；偏置计算厅不穿过观测光轴，高位接收冠与屏蔽供能厅组成独立设备群。</p></header>
<div class="grid"><div>尺寸 XYZ <b>{w} × {h} × {d}</b><br>宽 × 长 × 高 {w} × {d} × {h}；最低标准 65 × 81 × 49</div><div>实体方块 <b>{check['blocks']:,}</b><br>连通组件 {check['component_count']}</div><div>主控 <b>{data['controller']}</b><br>朝西 · 宽度中线 X={data['controller'][0]}</div><div>接口 <b>{check['port_count']} 个</b><br>嵌入设备外壳 · 周边同壳体邻接 3 格以上</div></div>
<p class="notice">待审候选 V1。未计入批准批次，未接入正式 Pattern 或游戏实例。目标映射按负责人决定采用方案中的 QEV/V07，并以对应机械机壳构成主体识别色；静态结构检查不代表 Controller tier 注册、机器成型、配方、研究执行、生存材料链或游戏运行已通过。</p>
<p><a href="三维评审.html">打开三维评审</a> · <a href="i24/{NAME}.nbt">NBT</a> · <a href="i24/{NAME}.schem">Sponge Schematic</a> · <a href="../{OUT.with_suffix('.zip').name}">完整 ZIP</a> · <a href="设计与检查.json">设计与检查</a> · <a href="设计依据.json">设计依据</a></p>
<h2>俯视布局</h2><img src="俯视布局.png" alt="I24 实际方块俯视布局"><h2>建筑整体</h2><p>西、东两条观测基线沿南北方向分开布置，端点镜组直接嵌入观测舱；中段保留开敞光轴，信号梁走上层、检修廊贴基线两侧。计算厅偏置到东侧，并将主控置于整机宽度中线的西立面；供能和校准模块位于东南屏蔽厅。</p><img src="等轴预览.png" alt="I24 V1 实际材质等轴预览"><h2>纵向立面</h2><img src="纵向立面.png" alt="I24 北南纵向设备高度与观测端点"><h2>主控与接口</h2><p>控制器标记替换中线处计算厅外壳的一格，向西保留操作空间。四个接口标记分别替换探针舱、计算厅数据接收面、观测记录输出面和供能厅的原设备壳方块；三维图与邻接审计确认每个端口都有连续壳体邻格、内侧设备连接和外向可达空间。</p><img src="主控正立面.png" alt="中线控制器在计算厅外壳上的位置"><img src="接口外壳立面.png" alt="四个端口的设备外壳局部图"><div class="scroll"><table><thead><tr><th>接口</th><th>用途</th><th>坐标</th><th>朝向</th><th>原设备壳</th></tr></thead><tbody>{ports}</tbody></table></div>
<h2>设计分区</h2>{zones}<h2>三维评审</h2><p>下方是独立交互评审页，支持旋转、剖切及分区查看。建筑工艺路线仅表达空间组织。</p><iframe src="三维评审.html" title="I24 V1 三维评审" loading="lazy"></iframe>
<h2>材料清单</h2><div class="scroll"><table><thead><tr><th>实际方块 ID</th><th>数量</th></tr></thead><tbody>{materials}</tbody></table></div><h2>尚未验证</h2><ul>{source_text}</ul><p><a href="verification.json">结构检查</a> · <a href="manifest.json">候选清单</a></p></main></body></html>'''


def load_viewer_page(data: dict, check: dict) -> str:
    page = VIEWER_SOURCE.read_text(encoding='utf-8')
    page = page.replace('I22', 'I24').replace('WSV V14', 'QEV/V07提案 V1')
    page = re.sub(r'<title>.*?</title>',
                  '<title>I24 · 量子异常观测阵列 · 双基线 V1 候选评审</title>', page, count=1, flags=re.S)
    header = (f'<header><a href="index.html">← I24交付总览</a><h1>I24 · 量子异常观测阵列 · 双基线 V1候选</h1>'
              f'<div>{W}×{D}×{H}（宽×长×高） · {check["blocks"]:,}方块 · 可旋转、剖切及逐口定位</div></header>')
    page = re.sub(r'<header>.*?</header>', header, page, count=1, flags=re.S)
    controller = data['controller']
    locator = (f'<div id="viewName"></div><div class="locator"><b>主控 {controller}</b>'
               f'<p>控制器嵌入偏置数据厅西立面，位于整机宽度中线 X={controller[0]}；朝西，留有外侧操作空间。</p>'
               '<p>黄色轮廓为定位标记；NBT中的标记映射到原机壳材质。</p>'
               '<button data-view="controller">定位主控</button></div>')
    page = re.sub(r'<div id="viewName"></div><div class="locator">.*?</div>',
                  locator, page, count=1, flags=re.S)
    page = re.sub(r'<details open><summary>本次结构修改</summary>.*?</details>',
                  '<details open><summary>本次结构修改</summary><p>两条平行北南干涉基线、四座端点观测站、偏置计算记录厅、高位接收冠与屏蔽供能厅；控制器和接口嵌入相应设备壳体。</p></details>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<details><summary>结构文件与边界</summary>.*?</details>',
                  f'<details><summary>结构文件与边界</summary><a href="i24/{NAME}.nbt">NBT</a> · '
                  f'<a href="i24/{NAME}.schem">Schematic</a> · <a href="设计与检查.json">检查记录</a>'
                  '<p>目标映射按负责人决定采用方案中的 QEV/V07；待审候选不代表 Controller tier、Pattern、配方、研究或游戏运行已通过。</p></details>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<label>剖切高度 <b id="layerValue">\d+</b><input id="layer" type="range" min="0" max="\d+" value="\d+">',
                  f'<label>剖切高度 <b id="layerValue">{H-1}</b><input id="layer" type="range" min="0" max="{H-1}" value="{H-1}">',
                  page, count=1)
    return page


def main() -> None:
    data = build()
    check = audit(data)
    manifest_path = OUT / 'manifest.json'
    if OUT.exists():
        if not manifest_path.is_file():
            raise FileExistsError(f'拒绝覆盖未识别的候选目录：{OUT}')
        existing_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if existing_manifest.get('key') != 'i24' or existing_manifest.get('title') != '量子异常观测阵列':
            raise FileExistsError(f'拒绝覆盖非 I24 候选：{OUT}')
    elif OUT.with_suffix('.zip').exists():
        raise FileExistsError(f'拒绝覆盖缺少源目录的既有压缩包：{OUT.with_suffix(".zip")}')
    OUT.mkdir(parents=True, exist_ok=True)
    structure_dir = OUT / 'i24'
    structure_dir.mkdir(exist_ok=True)
    scripts_dir = OUT / '生成脚本'
    scripts_dir.mkdir(exist_ok=True)

    states, groups, hashes = export(data, structure_dir)
    resources = Resources(project_resources=ROOT / 'src/main/resources')
    try:
        materials_by_state = {state: resources.material(state) for state in states
                              if state not in (PORT, CONTROLLER)}
        resource_sources = dict(resources.sources)
    finally:
        resources.close()
    for port in data['ports']:
        surface = port['surface_state']
        marker = dict(materials_by_state[surface])
        marker['state'] = PORT
        materials_by_state[PORT] = marker
    controller_surface = data['controller_surface']
    controller_material = dict(materials_by_state[controller_surface])
    controller_material['state'] = CONTROLLER
    materials_by_state[CONTROLLER] = controller_material
    materials = [materials_by_state[state] for state in states]
    grouped = [[] for _ in states]
    state_ids = {state: index for index, state in enumerate(states)}
    for block in data['blocks']:
        x, y, z = block['pos']
        grouped[state_ids[block['state']]].append((y * D + z) * W + x)
    payload = {
        'data': {key: value for key, value in data.items() if key != 'blocks'},
        'palette': states, 'groups': grouped, 'materials': materials,
        'audit': check, 'names': {},
    }
    encoded = base64.b64encode(gzip.compress(
        json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8'),
        compresslevel=9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD="' + encoded + '";\n', encoding='utf-8')
    viewer_script = VIEWER_BUNDLE.read_text(encoding='utf-8')
    north_facing_locator = 'controller:{pos:[B[0],B[1]+1,B[2]-18],target:B'
    west_facing_locator = 'controller:{pos:[B[0]-18,B[1]+1,B[2]],target:B'
    if north_facing_locator not in viewer_script:
        raise ValueError('I22评审脚本中的控制器定位视角无法识别。')
    viewer_script = viewer_script.replace(north_facing_locator, west_facing_locator, 1)
    north_facing_label = '朝 -Z</small></span></div>`;for(let e of r.ports)'
    west_facing_label = '朝 -X</small></span></div>`;for(let e of r.ports)'
    if north_facing_label not in viewer_script:
        raise ValueError('I22评审脚本中的控制器朝向标签无法识别。')
    viewer_script = viewer_script.replace(north_facing_label, west_facing_label, 1)
    (OUT / 'viewer.bundle.js').write_text(viewer_script, encoding='utf-8')
    render_preview(data, materials, OUT)
    render_report_images(data, OUT)
    viewer_page = load_viewer_page(data, check)
    viewer_page = viewer_page.replace(
        '变更记录#1：2026-10-23 10:57:25；新融合候选离线评审，不代表正式接入。',
        '变更记录#1：2026-10-24；按负责人决定采用映射提案制作；待审候选，未正式接入。')
    (OUT / '三维评审.html').write_text(viewer_page, encoding='utf-8')
    (OUT / 'index.html').write_text(make_report_page(data, check), encoding='utf-8')

    reference = {
        'machine_id': 'I24', 'name': '量子异常观测阵列',
        'design_sources': [
            {'path': 'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html',
             'fact': '最低宽长高为65×81×49；远距观测基线须长于计算舱两翼。'},
            {'path': 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01/i24/设计与检查.json',
             'fact': '仅参考前端/远端观测站、基线桥、数据厅与屏蔽供能分区；旧几何、17个接口标记和旧主控位置均未复用。'},
            {'path': 'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json',
             'fact': 'I24生产观测事实载体，不能直接产资源或锁定坐标；I25解析、I44锁定。'},
            {'path': 'src/main/resources/data/hk3gtl/research/industrial_processes.json',
             'fact': 'industrial_quantum_observation仍为provisional；物品world_model_carrier作为观测事实载体，不代表资源产出。'},
            {'path': 'src/main/resources/data/hk3gtl/research/research_execution.json',
             'fact': '研究工程列I24为执行器，但本交付未验证运行；research tier不等于固定结构电压。'},
            {'path': 'rule/当前多方块设计规则.md#9',
             'fact': '控制器与接口自然融入设备外壳，不另立面板或托柱；本候选按设备壳面齐平标记并复核周边。'},
        ],
        'voltage_boundary': '按负责人2026-10-24决定，I24结构制作采用《多方块结构电压映射提案V1》的QEV/V07条目并使用对应机械机壳；这确定候选的设计目标，不宣称Controller tier、配方或Pattern已注册或游戏内运行已验收。',
    }
    (OUT / '设计依据.json').write_text(json.dumps(reference, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    check['hashes'] = hashes
    check['material_resource_sources'] = resource_sources
    check['design_basis'] = reference
    check['preview_renderer'] = 'build_redesign69.render：解析当前项目方块模型与实际纹理。'
    check['viewer_marker_note'] = '工业接口与控制器方块在交互预览中映射为所替换的设备壳材质；NBT保留真实候选标记ID。'
    (OUT / '设计与检查.json').write_text(
        json.dumps({'data': {key: value for key, value in data.items() if key != 'blocks'},
                    'audit': check}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    manifest = {
        'key': 'i24', 'title': data['title'], 'candidate_version': data['candidate_version'],
        'status': 'candidate_waiting_user_review', 'candidate_approved': False,
        'target_voltage_appearance': 'QEV / V07（按负责人批准的结构制作映射）',
        'target_voltage_status': data['target_voltage_appearance'],
        'size_xyz': data['size'], 'size_wdh': [W, D, H],
        'baseline_wdh': check['size_check']['baseline_wdh'],
        'block_count': check['blocks'], 'controller': data['controller'],
        'controller_face': data['controller_face'], 'ports': data['ports'],
        'palette': check['palette'], 'nbt_sha256': hashes['nbt'], 'schem_sha256': hashes['schem'],
        'claim_boundary': '仅交付待审建筑候选；结构制作目标映射为QEV/V07，未部署、未获外观批准，未声称Controller tier注册、Pattern、研究闭环或游戏运行通过。',
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    shutil.copy2(Path(__file__), scripts_dir / Path(__file__).name)

    file_hashes = {path.relative_to(OUT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in sorted(OUT.rglob('*'))
                   if path.is_file() and path.name != 'verification.json'}
    check['files_sha256_before_verification'] = file_hashes
    (OUT / 'verification.json').write_text(json.dumps(check, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    bundle = OUT.with_suffix('.zip')
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None:
            raise ValueError('候选ZIP CRC校验失败。')
        for relative, expected in file_hashes.items():
            entries = [entry for entry in archive.namelist() if entry.endswith('/' + relative)]
            if len(entries) != 1 or hashlib.sha256(archive.read(entries[0])).hexdigest() != expected:
                raise ValueError(f'候选ZIP文件校验失败：{relative}')
    zip_hash = hashlib.sha256(bundle.read_bytes()).hexdigest()
    bundle.with_suffix('.zip.sha256').write_text(zip_hash + '\n', encoding='ascii')
    print(json.dumps({
        'out': str(OUT), 'zip': str(bundle), 'blocks': check['blocks'],
        'size_xyz': data['size'], 'components': check['component_count'],
        'ports': check['port_count'], 'target_voltage_appearance': 'QEV/V07 per approved design mapping',
        'nbt_sha256': hashes['nbt'], 'schem_sha256': hashes['schem'],
        'zip_sha256': zip_hash, 'verified': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
