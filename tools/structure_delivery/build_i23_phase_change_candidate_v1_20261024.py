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

from build_redesign69 import export
from structure_size_baseline import ROOT, require


OUT = ROOT / 'deliveries/I23_崩坏能相变释能机_相态压缩换热列车_V2_20261024'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01/i23'
OLD_PAGE = SOURCE / '三维评审.html'
OLD_DATA = SOURCE / 'data.js'
VIEWER = SOURCE.parent / 'viewer.bundle.js'
NAME = 'hk3gtl-i23-phase-change-v2-20261024'
W, H, D = 33, 35, 37

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


def build() -> dict:
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
        if not any((p[0]+ax,p[1]+ay,p[2]+az) in occupied
                   for ax,ay,az in direction.values()):
            raise ValueError(f'接口没有贴合设备外壳：{port["id"]}')
    if (16, 4, 9) in occupied:
        raise ValueError('主控前侧没有可达空间。')
    component_count = components(set(occupied))
    if component_count != 1:
        raise ValueError(f'存在分离结构组件：{component_count}')
    palette = collections.Counter(block['state'] for block in data['blocks'])
    return {'size_check': size_check, 'blocks': len(data['blocks']),
            'component_count': component_count, 'port_count': len(port_positions),
            'ports_are_embedded_and_exposed': True, 'controller_centered_and_accessible': True,
            'diamond_ore_count': 0, 'voltage_casing_count': 0,
            'walkable_paths_clear': True, 'palette': dict(sorted(palette.items())),
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
    draw.text((18,8),'I23 崩坏能相变释能机 · 相态压缩换热列车 V2',font=font,fill=(234,243,246))
    draw.text((18,image.height-39),'33 × 37 × 35 (W × L × H)  |  6 embedded ports  |  target voltage pending',
              font=font,fill=(178,208,210))
    image.save(path)


def make_page(data: dict, verification: dict) -> str:
    ports=''.join(f'<li><code>{html.escape(p["id"])}</code> · {html.escape(p["purpose"])} · <code>{p["pos"]}</code></li>'
                  for p in data['ports'])
    zones=''.join(f'<details><summary>{html.escape(z["name"])}</summary><p>{html.escape(z["description"])}</p>'
                  f'<p class="muted">范围 <code>{z["min"]}</code> 至 <code>{z["max"]}</code></p></details>'
                  for z in data['zones'])
    mats=''.join(f'<li><code>{html.escape(state)}</code> × {count:,}</li>'
                 for state,count in verification['palette'].items())
    not_verified=''.join(f'<li>{html.escape(item)}</li>' for item in verification['not_verified'])
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I23 崩坏能相变释能机 · V2</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#101a23;color:#e5edf0;font:14px/1.65 "Microsoft YaHei",sans-serif}}a{{color:#8ddbd0}}header{{height:74px;padding:10px 18px;border-bottom:1px solid #40525a;display:flex;align-items:center;justify-content:space-between;gap:16px}}h1{{font-size:22px;margin:0}}.sub{{color:#aec1c3}}main{{display:grid;grid-template-columns:minmax(0,1fr) 350px;height:calc(100vh - 74px)}}#stage{{position:relative;overflow:hidden;min-height:500px}}#stage canvas{{position:absolute;inset:0}}#labels{{position:absolute;inset:0;pointer-events:none}}#loading{{position:absolute;z-index:2;top:14px;left:14px;background:#172832;padding:9px 12px}}aside{{overflow:auto;padding:16px;border-left:1px solid #40525a}}section{{border-top:1px solid #34454c;padding:12px 0}}h2{{font-size:15px;margin:0 0 7px}}button{{background:#273a40;color:#e5edf0;border:1px solid #597178;padding:6px 8px;margin:2px;cursor:pointer}}input{{accent-color:#71c3b7}}details{{border-bottom:1px solid #34454c;padding:8px 0}}summary{{cursor:pointer}}.muted{{color:#a7b9bb}}code{{overflow-wrap:anywhere;color:#a8d6ca}}ul{{padding-left:19px}}li{{margin:5px 0}}.notice{{color:#f0d4a0}}@media(max-width:900px){{main{{height:auto;grid-template-columns:1fr}}#stage{{height:65vh;min-height:420px}}aside{{border-left:0;border-top:1px solid #40525a;max-height:none}}header{{height:auto;min-height:74px;align-items:flex-start;flex-direction:column}}}}</style></head><body>
<header><div><h1>崩坏能相变释能机 · 相态压缩换热列车 V2</h1><span class="sub">待审候选 · 33 × 37 × 35（宽 × 长 × 高） · {verification['blocks']:,} 方块</span></div><span class="notice">目标电压未定</span></header>
<main><section id="stage"><div id="loading">正在载入本地逐格结构与材质…</div><div id="labels"></div></section><aside>
<section><h2>结构视角</h2><div><button data-view="front">前左</button><button data-view="right">前右</button><button data-view="back">后侧</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div><label>剖切高度 <b id="layerValue">34</b><input id="layer" type="range" min="0" max="34" value="34" style="width:100%"></label><p><label><input id="showGlass" type="checkbox" checked>玻璃</label> <label><input id="showPorts" type="checkbox" checked>接口</label> <label><input id="showPaths" type="checkbox">净空</label> <label><input id="showZones" type="checkbox" checked>分区</label></p><button id="reset">重置</button><button id="saveImage">保存视角</button><p id="counts"></p><p id="status"></p></section>
<section><h2>工艺分区</h2>{zones}<p>工艺路线只用于表达设备空间关系，不代表已注册配方或能量收支。</p></section>
<section><h2>接口占位</h2><ul>{ports}</ul><p class="muted">使用 <code>hk3gtl:industrial_port_casing</code>，无功能方块；正式Pattern须按配方能力替换并复核。</p></section>
<section><h2>目标电压</h2><p>未定。当前无 I23 可执行生产配方；QCV/V06 仅在待审映射提案中出现，本候选不写入电压机壳。</p></section>
<section><h2>材料用量</h2><ul>{mats}</ul></section>
<section><h2>静态检查</h2><p>尺寸：通过；实际范围 <code>{verification['size_check']['actual_xyz']}</code><br>连通组件：{verification['component_count']}<br>接口：{verification['port_count']} 个均嵌入外壳、外侧无遮挡<br>中心主控：x=16，前侧可达<br>diamond_ore：0；电压机壳：0</p><h2>未验证</h2><ul>{not_verified}</ul></section>
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
    draw_preview(data, materials, OUT/'等轴预览.png')
    verification['hashes'] = hashes
    verification['source_geometry_reference'] = {
        'path': str(SOURCE/'设计与检查.json'),
        'role': '只参考功能分区和材料灵感；本候选由新布局独立生成。',
        'source_nbt_sha256': hashlib.sha256((SOURCE/'hk3gtl-i23-redesign-01.nbt').read_bytes()).hexdigest(),
    }
    verification['viewer_material_note'] = 'industrial_port_casing在浏览器材质图中借用钢机壳贴图作识别预览；NBT使用真实占位方块ID。'
    (OUT/'设计与检查.json').write_text(json.dumps({'data': {k:v for k,v in data.items() if k != 'blocks'},
                                                   'audit': verification},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'index.html').write_text(make_page(data,verification),encoding='utf-8')
    script_name=Path(__file__).name.replace('_v1_', '_v2_')
    shutil.copy2(Path(__file__), scripts_dir/script_name)

    source_nbt=SOURCE/'hk3gtl-i23-redesign-01.nbt'
    manifest={
        'key':'i23','title':'崩坏能相变释能机','candidate_version':data['candidate_version'],
        'status':'candidate_waiting_user_review','candidate_approved':False,
        'supersedes_internal_draft':{'version':'相态压缩换热列车V1','submitted_for_review':False,
                                     'reason':'收掉空置外框，以功能管路和设备模块落实尺寸边界；V1不作为当前审阅对象。'},
        'target_voltage':None,'target_voltage_status':data['target_voltage_status'],
        'size_xyz':data['size'],'size_wdh':[33,37,35],'block_count':len(data['blocks']),
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
