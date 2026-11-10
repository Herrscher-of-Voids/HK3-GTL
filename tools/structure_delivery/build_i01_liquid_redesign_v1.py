# -*- coding: utf-8 -*-
"""生成 I01-1 液态采集塔独立重设计候选；不修改已确认版本或正式实例。"""
import base64
import collections
import datetime
import gzip
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

import nbtlib

from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import Build, ROOT
from review_controller_integration_20261023 import front_image
from structure_size_baseline import require


OUT = ROOT / 'deliveries/I01-1_崩坏能采集塔液态_分层集流塔_V1_20261025'
SYMMETRIC_OUT = ROOT / 'deliveries/I01-1_崩坏能采集塔液态_左右对称修订_V2_20261025'
REDLINE_OUT = ROOT / 'deliveries/I01-1_崩坏能采集塔液态_接口竖梁对位_V3_20261025'
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
PORT = 'hk3gtl:industrial_port_casing'
CONTROLLER = 'minecraft:diamond_block'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
S = {
    'steel': 'gtceu:solid_machine_casing',
    'robust': 'gtceu:robust_machine_casing',
    'bronze': 'gtceu:bronze_machine_casing',
    'liquid': 'gtceu:corrosion_proof_casing',
    'pipe': 'gtceu:steel_pipe_casing',
    'glass': 'gtceu:tempered_glass',
    'vent': 'gtceu:computer_heat_vent',
    'grate': 'gtceu:assembly_line_grating',
    'gear': 'gtceu:tungstensteel_gearbox',
    'power': 'gtceu:high_power_casing',
    'clean': 'gtceu:clean_machine_casing',
}
TARGET = {'blocks': 4179, 'materials': 11, 'volume': 52675, 'height': 43}


def hring(a, x0, x1, z0, z1, y, material):
    for x in range(x0, x1 + 1):
        a.set(x, y, z0, material)
        a.set(x, y, z1, material)
    for z in range(z0 + 1, z1):
        a.set(x0, y, z, material)
        a.set(x1, y, z, material)


def box_shell(a, x0, x1, y0, y1, z0, z1, material):
    a.box((x0, y0, z0), (x1, y1, z1), material, True)


def wall_ribs(a, x0, x1, y0, y1, z0, z1):
    for x in range(x0 + 2, x1, 4):
        a.box((x, y0 + 1, z0), (x, y1 - 1, z0), S['robust'])
        a.box((x, y0 + 1, z1), (x, y1 - 1, z1), S['robust'])
    for z in range(z0 + 3, z1, 5):
        a.box((x0, y0 + 1, z), (x0, y1 - 1, z), S['robust'])
        a.box((x1, y0 + 1, z), (x1, y1 - 1, z), S['robust'])


def shaft(a):
    # 主轴以 HBV 机壳形成连续塔身，观察窗留在外壁而非外挂观察舱。
    for y in range(3, 54):
        hring(a, 14, 28, 14, 28, y, HBV)
    for x in (14, 15, 27, 28):
        for z in (14, 15, 27, 28):
            a.box((x, 3, z), (x, 53, z), S['robust'])
    for y in (3, 9, 17, 26, 36, 45, 53):
        hring(a, 14, 28, 14, 28, y, S['steel'])
    a.box((14, 48, 14), (28, 48, 28), S['steel'])
    for y in range(12, 31):
        for x in range(19, 24):
            a.set(x, y, 14, S['glass'])
        for x in range(19, 24):
            a.set(x, y, 28, S['glass'])
    for y in range(13, 29):
        for z in range(19, 24):
            a.set(14, y, z, S['glass'])
            a.set(28, y, z, S['glass'])
    # 液態下行管束與分段密封槽可從四面觀察窗辨認。
    for x in (19, 20, 22, 23):
        a.box((x, 7, 19), (x, 45, 19), S['pipe'])
        a.box((x, 7, 23), (x, 45, 23), S['pipe'])
    for y in (7, 17, 27, 37):
        hring(a, 19, 23, 19, 23, y, S['liquid'])
    for y in range(8, 45):
        a.set(21, y, 21, S['glass'] if y % 4 in (0, 1) else S['liquid'])
    # 塔頂收束帽與主軸共體，形成最高輪廓點。
    for y in range(49, 55):
        hring(a, 16, 26, 16, 26, y, HBV if y % 2 else S['steel'])
    a.box((17, 53, 17), (25, 53, 25), S['steel'])
    for x in range(18, 25, 2):
        for z in range(18, 25, 2):
            a.set(x, 54, z, S['vent'])


def condenser(a, side):
    if side == 'west':
        x0, x1 = 2, 12
        window_x = range(5, 10)
        port_x = (5, 9)
    else:
        x0, x1 = 30, 40
        window_x = range(33, 38)
        port_x = (33, 37)
    z0, z1, y0, y1 = 14, 29, 3, 24
    box_shell(a, x0, x1, y0, y1, z0, z1, S['steel'])
    wall_ribs(a, x0, x1, y0, y1, z0, z1)
    a.box((x0 + 1, 4, z0 + 1), (x1 - 1, 4, z1 - 1), S['liquid'])
    for y in range(8, 19):
        for x in window_x:
            a.set(x, y, z0, S['glass'])
    # 设备顶面的重复散热阵列；周边承重梁与管汇保持完整。
    for x in range(x0 + 2, x1 - 1, 2):
        for z in (17, 20, 23, 26):
            a.set(x, 25, z, S['vent'])
    for x in port_x:
        a.set(x, 5, z0, PORT)
        a.set(x, 5, z0 + 1, S['liquid'])
    for x in range(x0 + 3, x1 - 2, 3):
        a.box((x, 5, 18), (x + 1, 5, 20), S['steel'])
        a.box((x, 6, 18), (x + 1, 8, 20), S['gear'])
        a.box((x - 1, 9, 17), (x + 2, 9, 21), S['bronze'])
    # 两级管汇把低位冷凝肩舱直接接入中央处理塔。
    for y in (9, 17):
        a.box((12, y, 20), (14, y + 1, 22), S['pipe'])
        a.box((28, y, 20), (30, y + 1, 22), S['pipe'])
    mast_x = 7 if side == 'west' else 35
    box_shell(a, mast_x - 2, mast_x + 2, 24, 45, 19, 23, HBV)
    for y in (25, 34, 42):
        hring(a, mast_x - 2, mast_x + 2, 19, 23, y, S['bronze'] if y == 29 else S['robust'])
    return {'name': f'{side}侧冷凝肩舱', 'kind': 'condenser',
            'min': [x0, y0, z0], 'max': [x1, 35, z1],
            'pos': [(x0 + x1) // 2, 19, 21], 'role': '液态冷凝、换热与回流',
            'service_face': '北侧设备外壁', 'mast': [mast_x, 30, 21]}


def process_bay(a, north=True):
    z0, z1 = (3, 12) if north else (31, 40)
    y1 = 13 if north else 12
    box_shell(a, 14, 28, 3, y1, z0, z1, S['clean'] if north else S['steel'])
    wall_ribs(a, 14, 28, 3, y1, z0, z1)
    # 检修入口和后墙开口连成一条直达主控的操作通道。
    if north:
        for z in (z0, z1):
            for x in range(19, 24):
                for y in range(3, 9):
                    a.b.pop((x, y, z), None)
        a.box((16, 4, 5), (18, 6, 7), S['power'])
        a.box((24, 4, 5), (26, 6, 7), S['gear'])
        a.box((19, 3, 8), (23, 3, 10), S['liquid'])
        mast = (21, 7)
    else:
        a.box((17, 4, 34), (19, 7, 36), S['gear'])
        a.box((23, 4, 34), (25, 7, 36), S['liquid'])
        for x in (17, 19, 23, 25):
            a.set(x, 11, 35, S['vent'])
        mast = (21, 36)
    box_shell(a, mast[0] - 2, mast[0] + 2, y1 - 1, 45, mast[1] - 2, mast[1] + 2, HBV)
    for y in (y1, y1 + 5, 41, 44):
        hring(a, mast[0] - 2, mast[0] + 2, mast[1] - 2, mast[1] + 2, y, S['robust'])
    return {'name': '前置充填与控制工段' if north else '后置回收泵房',
            'kind': 'process', 'min': [14, 3, z0], 'max': [28, y1, z1],
            'pos': [21, 9, (z0 + z1) // 2],
            'role': '入口调节、泵送与介质回收' if north else '液体回流及残液回收',
            'service_face': '北侧' if north else '南侧', 'mast': [mast[0], 29, mast[1]]}


def collector_head(a, cx, cz):
    box_shell(a, cx - 3, cx + 3, 44, 49, cz - 3, cz + 3, S['robust'])
    for x in range(cx - 2, cx + 3):
        a.set(x, 46, cz - 3, S['glass'])
    for x in range(cx - 2, cx + 3):
        a.set(x, 48, cz + 3, S['glass'])
    for x in range(cx - 2, cx + 3, 2):
        for z in range(cz - 2, cz + 3, 2):
            a.set(x, 49, z, S['vent'])
    hring(a, cx - 4, cx + 4, cz - 4, cz + 4, 44, HBV)


def build():
    brief = {'id': 'I01-1', 'title': '1阶崩坏能采集塔·液态', 'minimum_wdh': [43, 43, 55],
             'form': '中心液態採集塔、雙側冷凝肩艙、前後泵送工段與四向高位集流頭',
             'flow': '高位集流→主軸液態下行→雙側冷凝→前端控制與後端回收'}
    a = Build(brief)

    # 分段承重基座只落在設備、檢修軸與四向受力線，不鋪滿整張地板。
    a.box((0, 0, 19), (42, 0, 23), S['steel'])
    a.box((19, 0, 0), (23, 0, 42), S['steel'])
    for x0, x1 in ((2, 12), (30, 40), (14, 28)):
        for z0, z1 in (((14, 29),) if x1 != 28 or x0 != 14 else ((3, 12), (31, 40))):
            a.box((x0, 0, z0), (x1, 2, z1), S['robust'])
    a.box((14, 0, 14), (28, 2, 28), S['steel'])
    for x0, x1, z0, z1 in ((0, 2, 19, 23), (40, 42, 19, 23),
                            (19, 23, 0, 2), (19, 23, 40, 42)):
        a.box((x0, 0, z0), (x1, 1, z1), S['robust'])

    shaft(a)
    west = condenser(a, 'west')
    east = condenser(a, 'east')
    front = process_bay(a, True)
    rear = process_bay(a, False)

    # Two service galleries circle the tower and attach to the four process masses.
    for y in (12, 27):
        for x in range(12, 31):
            for z in range(12, 31):
                if x in (12, 13, 29, 30) or z in (12, 13, 29, 30):
                    a.set(x, y, z, S['grate'])
        for x, z in ((12, 12), (12, 30), (30, 12), (30, 30)):
            a.box((x, 1, z), (x + (1 if x == 12 else 0), y, z + (1 if z == 12 else 0)), S['robust'])
    a.box((19, 14, 3), (23, 14, 14), S['grate'])
    a.box((19, 13, 2), (23, 13, 3), S['steel'])

    # The four elevated intakes rise from real equipment roofs and join the collector crown.
    for cx, cz, y0 in ((7, 21, 24), (35, 21, 24), (21, 7, 13), (21, 36, 12)):
        collector_head(a, cx, cz)
        if cz == 21:
            a.box((min(cx, 21), 41, 19), (max(cx, 21), 44, 23), S['steel'])
            a.box((min(cx, 21), 45, 21), (max(cx, 21), 45, 21), S['pipe'])
        else:
            a.box((19, 41, min(cz, 21)), (23, 44, max(cz, 21)), S['steel'])
            a.box((21, 45, min(cz, 21)), (21, 45, max(cz, 21)), S['pipe'])
        if y0 < 24:
            a.box((cx - 2, y0, cz - 2), (cx + 2, 44, cz + 2), S['pipe'], True)

    # 主控与六个占位接口嵌入塔身及冷凝舱自身的北向外壁。
    controller = [21, 5, 14]
    a.set(*controller, CONTROLLER)
    a.set(21, 5, 15, S['robust'])
    ports = [
        {'id': 'INPUT', 'pos': [18, 5, 14], 'face': 'north', 'purpose': '液态崩坏能输入候选', 'host': '主塔北侧液态工段外壁'},
        {'id': 'OUTPUT', 'pos': [24, 5, 14], 'face': 'north', 'purpose': '液态崩坏能输出候选', 'host': '主塔北侧液态工段外壁'},
        {'id': 'COOLANT', 'pos': [5, 5, 14], 'face': 'north', 'purpose': '冷却介质输入候选', 'host': '西侧冷凝肩舱北壁'},
        {'id': 'RECOVERY', 'pos': [9, 5, 14], 'face': 'north', 'purpose': '回收介质输出候选', 'host': '西侧冷凝肩舱北壁'},
        {'id': 'POWER', 'pos': [33, 5, 14], 'face': 'north', 'purpose': '能源输入候选', 'host': '东侧冷凝肩舱北壁'},
        {'id': 'RETURN', 'pos': [37, 5, 14], 'face': 'north', 'purpose': '旁路回流候选', 'host': '东侧冷凝肩舱北壁'},
    ]
    for port in ports:
        x, y, z = port['pos']
        a.set(x, y, z, PORT)
        a.set(x, y, z + 1, S['liquid'])

    data = {
        'key': 'i01-1', 'name': 'i01-1-hbv-liquid-collector-v1', 'title': brief['title'],
        'size': [43, 55, 43], 'controller': controller, 'ports': ports,
        'paths': [{'name': '北向主控与工段检修轴', 'min': [19, 3, 0], 'max': [23, 6, 13]},
                  {'name': '下層西側檢修廊', 'min': [12, 13, 14], 'max': [13, 14, 28]},
                  {'name': '下層東側檢修廊', 'min': [29, 13, 14], 'max': [30, 14, 28]},
                  {'name': '下層南北檢修廊', 'min': [14, 13, 12], 'max': [28, 14, 13]},
                  {'name': '上層西側檢修廊', 'min': [12, 28, 14], 'max': [13, 29, 28]},
                  {'name': '上層東側檢修廊', 'min': [29, 28, 14], 'max': [30, 29, 28]},
                  {'name': '上層南北檢修廊', 'min': [14, 28, 12], 'max': [28, 29, 13]}],
        'zones': [
            {'name': 'HBV液态采集主塔', 'kind': 'tower', 'min': [14, 3, 14], 'max': [28, 54, 28], 'pos': [21, 52, 21], 'role': '液态采集与下行稳流', 'service_face': '四面观察窗'},
            west, east, front, rear,
            {'name': '四向高位集流头', 'kind': 'collector', 'min': [3, 44, 3], 'max': [39, 49, 39], 'pos': [21, 47, 21], 'role': '分向收集并汇入中心塔', 'service_face': '上层检修廊'},
        ],
        'links': [{'from': z['name'], 'to': 'HBV液态采集主塔', 'material': S['pipe'], 'route': [[z['mast'][0], 46, z['mast'][2]], [21, 46, 21]]}
                  for z in (west, east, front, rear)],
        'description': '贯穿全体的HBV液态采集主塔，两侧冷凝肩舱与前后泵送工段共同承载四向高位集流头；液态管束沿可视主轴下行，两层检修廊紧贴塔身。主控位于塔身北壁全宽中线，六个接口齐平嵌入实际设备外壁。',
        'brief': brief,
        'blocks': [{'pos': list(pos), 'state': state} for pos, state in sorted(a.b.items())],
        'construction_notes': {
            'orientation': 'X向东、Y向上、Z向南；主控与接口朝北（-Z）。',
            'origin': [0, 0, 0], 'paste_anchor': controller,
            'schematic_offset': [-controller[0], -controller[1], -controller[2]],
            'recommended_bottom_world_y': -60, 'recommended_controller_world_y': -55,
            'world_height_range': [-60, -6],
            'status': '新重设计候选，待外观确认；未接入正式Pattern或实例。',
        },
    }
    data['role_materials'] = {state: [state] for state in sorted({b['state'] for b in data['blocks']})}
    return data


def connected_block_count(blocks):
    points = {tuple(b['pos']) for b in blocks}
    start = next(iter(points))
    reached = {start}
    stack = [start]
    while stack:
        x, y, z = stack.pop()
        for p in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if p in points and p not in reached:
                reached.add(p)
                stack.append(p)
    return len(reached), len(points)


def mirror_x(data):
    width = data['size'][0]
    assert width % 2 == 1, '左右镜像要求奇数宽度并以中列为轴'
    center = (width - 1) // 2
    source = {tuple(block['pos']): block['state'] for block in data['blocks']}
    mirrored = {}
    for (x, y, z), state in source.items():
        if x == center:
            mirrored[(x, y, z)] = state
            continue
        pair = (width - 1 - x, y, z)
        other = source.get(pair)
        chosen = state if x < center or other is None else other
        mirrored[(x, y, z)] = chosen
        mirrored[pair] = chosen

    result = dict(data)
    result['name'] = 'i01-1-hbv-liquid-collector-v2-symmetric'
    result['blocks'] = [{'pos': list(pos), 'state': state}
                        for pos, state in sorted(mirrored.items())]
    result['description'] += ' 全部实体沿X=21中轴逐格镜像。'
    result['brief'] = dict(data['brief'], form='中心采集塔与左右镜像冷凝舱、前后泵送工段及四向集流头')
    result['construction_notes'] = dict(data['construction_notes'],
        status='左右镜像修订候选，待外观确认；未接入正式Pattern或实例。')
    changed_states = sum(1 for (x, y, z), state in mirrored.items()
                         if x > center and (x, y, z) in source and source[(x, y, z)] != state)
    result['symmetry'] = {'axis': 'X=21', 'exact': True,
                          'source_blocks': len(source), 'mirrored_blocks': len(mirrored),
                          'added_blocks': len(mirrored) - len(source),
                          'changed_mirror_states': changed_states}
    return result


def move_interface_ribs(data):
    occupied = {tuple(block['pos']): block['state'] for block in data['blocks']}
    source_x = (4, 8, 34, 38)
    target_x = (5, 9, 33, 37)
    ports = {tuple(port['pos']) for port in data['ports']}

    for x in source_x:
        for y in range(4, 24):
            pos = (x, y, 14)
            if occupied.get(pos) == S['robust']:
                occupied[pos] = S['steel']

    for x in target_x:
        for y in range(4, 24):
            pos = (x, y, 14)
            if pos in ports:
                assert occupied[pos] == PORT
                continue
            occupied[pos] = S['robust']

    result = dict(data)
    result['name'] = 'i01-1-hbv-liquid-collector-v3-interface-ribs'
    result['blocks'] = [{'pos': list(pos), 'state': state}
                        for pos, state in sorted(occupied.items())]
    result['description'] += ' 北立面冷凝窗的四条坚固机壳竖梁移至接口同列；接口方块保持原位。'
    result['brief'] = dict(data['brief'], form='中心采集塔、左右镜像冷凝舱、接口同列竖梁与前后泵送工段')
    result['construction_notes'] = dict(data['construction_notes'],
        status='接口竖梁对位候选，待外观确认；未接入正式Pattern或实例。')
    result['interface_ribs'] = {
        'face_z': 14, 'source_x': list(source_x), 'target_x': list(target_x),
        'y_range': [4, 23], 'ports_preserved': True,
        'port_positions': [list(pos) for pos in sorted(ports)],
    }
    return result


def main(symmetric=False, redlines=False):
    out = REDLINE_OUT if redlines else SYMMETRIC_OUT if symmetric else OUT
    out.mkdir(parents=True, exist_ok=True)
    data = build()
    if symmetric or redlines:
        data = mirror_x(data)
    if redlines:
        data = move_interface_ribs(data)
    size_audit = require(data)
    blocks = data['blocks']
    bounds = [[min(b['pos'][axis] for b in blocks), max(b['pos'][axis] for b in blocks)] for axis in range(3)]
    counts = collections.Counter(b['state'] for b in blocks)
    volume = size_audit['actual_xyz'][0] * size_audit['actual_xyz'][1] * size_audit['actual_xyz'][2]
    reached, total = connected_block_count(blocks)
    assert reached == total, f'存在不相連的結構方塊：{reached}/{total}'
    assert len(blocks) > TARGET['blocks'] and len(counts) > TARGET['materials']
    assert volume > TARGET['volume'] and size_audit['actual_xyz'][1] > TARGET['height']
    assert data['controller'][0] == (data['size'][0] - 1) // 2
    occupied = {tuple(b['pos']): b['state'] for b in blocks}
    if symmetric or redlines:
        width = data['size'][0]
        assert all(occupied.get((width - 1 - x, y, z)) == state
                   for (x, y, z), state in occupied.items()), '存在未镜像的方块或材质'
        port_positions = {tuple(p['pos']) for p in data['ports']}
        assert all((width - 1 - x, y, z) in port_positions
                   for x, y, z in port_positions), '接口坐标未左右成对'
    if redlines:
        for x in data['interface_ribs']['target_x']:
            for y in range(4, 24):
                pos = (x, y, 14)
                assert occupied[pos] == (PORT if pos in {tuple(p['pos']) for p in data['ports']} else S['robust'])
    assert occupied[tuple(data['controller'])] == CONTROLLER
    assert sum(n for state, n in counts.items() if state == HBV) > max(counts.values()) / 4
    for p in data['ports']:
        x, y, z = p['pos']
        assert occupied[(x, y, z)] == PORT and (x, y, z - 1) not in occupied
    for pos in ((21, 5, 14), *[tuple(p['pos']) for p in data['ports']]):
        x, y, z = pos
        assert (x, y, z - 1) not in occupied

    resources = Resources(instance=INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = []
        source_map = {}
        for state in sorted(counts):
            before = set(resources.sources)
            materials.append(resources.material(state))
            source_map[state] = {key: value for key, value in resources.sources.items() if key not in before}
        assert all(m.get('complete_cube') for m in materials)
    finally:
        resources.close()

    states, groups, hashes = export(data, out)
    schem_path = out / (data['name'] + '.schem')
    schem = nbtlib.load(schem_path)
    offset = [-p for p in data['controller']]
    schem['Offset'] = nbtlib.IntArray(offset)
    schem.save(schem_path, gzipped=True)
    check_schem = nbtlib.load(schem_path)
    assert int(check_schem['Version']) == 2
    assert [int(check_schem[k]) for k in ('Width', 'Height', 'Length')] == data['size']
    assert list(map(int, check_schem['Offset'])) == offset
    hashes['schem'] = hashlib.sha256(schem_path.read_bytes()).hexdigest()
    render(data, materials, out)
    if symmetric or redlines:
        front_image(data, materials).save(out / '北立面.png')

    namespace = collections.Counter()
    for state, count in counts.items():
        namespace[state.split(':', 1)[0]] += count
    total_blocks = sum(counts.values())
    audit = {
        'time': datetime.datetime.now().astimezone().isoformat(),
        'palette': dict(counts), 'namespace_counts': dict(namespace),
        'namespace_percent': {key: round(value / total_blocks * 100, 2) for key, value in namespace.items()},
        'actual_bounds_xyz': bounds, 'actual_size_wdh': size_audit['actual_xyz'],
        'actual_volume': volume, 'unique_material_count': len(counts), 'block_count': len(blocks),
        'connected_blocks': reached, 'hashes': hashes, 'size_baseline': size_audit,
        'voltage_thresholds_exclusive': TARGET,
        'voltage_thresholds_passed': {'blocks': len(blocks) > TARGET['blocks'],
             'materials': len(counts) > TARGET['materials'], 'volume': volume > TARGET['volume'],
             'height': size_audit['actual_xyz'][1] > TARGET['height']},
        'resource_instance': str(INSTANCE), 'asset_sources': source_map,
        'controller_center': {'x': data['controller'][0], 'width': data['size'][0], 'centered': True},
        'port_positions': data['ports'], 'schematic_offset': offset,
        'checks': ['尺寸下限与实体包围盒均按69座占地表实测',
                   '所有结构方块均以六方向连续相邻，构成单一整体',
                   'NBT及Sponge v2逐格数据回读；主控锚点偏移已记录',
                   '主控位于全宽中线；六个接口齐平替换设备外壳，前方操作净空',
                   '指定实例中使用的实际方块模型均解析为完整立方体',
                   '方块数、种类数、实体体积及高度均超过MAX组严格门槛'],
        'not_verified': ['华丽度、复杂度、细节和现实工程感待负责人目视审核',
                         '普通材料在HBV阶段的生存可达性与完整配方前置未逐项核验',
                         '资源包覆盖纹理未套入静态材质投影',
                         '尚未接入正式Pattern、配方或游戏实例，未做游戏成型和运行测试',
                         'I01-2至I01-4尚未按新候选逐格验证累积扩建'],
        'approval': '待负责人外观审核；新候选，不计入已批准批次。',
    }
    if symmetric:
        audit['left_right_symmetry'] = data['symmetry']
        audit['checks'].append('逐格按X=21镜像；所有镜像位置方块状态一致')
    if redlines:
        audit['left_right_symmetry'] = data['symmetry']
        audit['interface_ribs'] = data['interface_ribs']
        audit['checks'].append('北立面四条坚固机壳竖梁移至接口同列，工业接口方块未被覆盖')
        audit['checks'].append('修改后仍逐格按X=21镜像，全部结构方块保持六向连通')
    metadata = {k: v for k, v in data.items() if k != 'blocks'}
    payload = {'data': metadata, 'palette': states, 'groups': groups,
               'materials': materials, 'audit': audit, 'names': {}}
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (out / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(packed) + ';', encoding='utf-8')
    (out / '设计与检查.json').write_text(json.dumps({'data': metadata, 'audit': audit},
        ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copy2(SOURCE / 'viewer.bundle.js', out / 'viewer.bundle.js')
    page = (SOURCE / 'i01-1/三维评审.html').read_text(encoding='utf-8')
    page = page.replace('<title>1阶崩坏能采集塔 · 液态 · 实体草稿01</title>',
                        '<title>I01-1 崩坏能采集塔·液态 · V1重设计候选</title>')
    page = page.replace('<h1>1阶崩坏能采集塔 · 液态</h1>',
                        '<h1>I01-1 崩坏能采集塔·液态</h1>')
    page = page.replace('href="../index.html">← 全部69座',
                        'href="../../logs/i01-i24-redesign-plan-20261025/index.html">← I01–I24重设计计划')
    page = page.replace(' · <a href="详细方案.html">详细施工方案</a>', '')
    page = page.replace('17×17×33（宽×长×高） · 1,123个实体 · 待审预览',
                        f'43×43×55（宽×深×高） · {len(blocks):,}个实体 · 待审候选')
    page = page.replace('id="layerValue">32', 'id="layerValue">54')
    page = page.replace('id="layer" type="range" min="0" max="32" value="32"',
                        'id="layer" type="range" min="0" max="54" value="54"')
    page = page.replace('竖向采集桅杆与低位冷凝肩舱；集流头经竖直干管落入侧置冷凝腔，检修道从另一侧绕柱到达仪表座',
                        data['description'])
    page = page.replace('<a href="详细方案.html">查看每区坐标、尺寸、用材与连接路线 →</a>',
                        '<p>HBV为新增主体识别色；钢灰承重、透明观察窗与少量青铜压环按功能分配。</p>')
    voltage_check = (f'<details open><summary>电压递增门槛</summary><p>MAX 当前比较基线：'
        f'{TARGET["blocks"]:,}块 / {TARGET["materials"]}种 / {TARGET["volume"]:,}格³ / H{TARGET["height"]}。</p>'
        f'<p>本候选：{len(blocks):,}块 / {len(counts)}种 / {volume:,}格³ / H{size_audit["actual_xyz"][1]}；四项数值均严格超过基线。</p>'
        '<p class="muted">数值通过不等于外观批准、材料生存可达性闭环或游戏内成型运行通过。</p></details>')
    page = page.replace('<details><summary>实际检查</summary>', voltage_check + '<details><summary>实际检查</summary>')
    page = page.replace('实体草稿01', 'V1重设计候选')
    page = page.replace('未实测浏览器交互或游戏', '游戏内成型与运行尚未验收')
    page = page.replace('i01-1-redesign-01.nbt', data['name'] + '.nbt')
    page = page.replace('i01-1-redesign-01.schem', data['name'] + '.schem')
    page = page.replace('href="hk3gtl-' + data['name'], 'href="' + data['name'])
    page = page.replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
    if symmetric or redlines:
        page = page.replace('<a href="等轴预览.png">静态图</a>',
                            '<a href="等轴预览.png">等轴图</a> · <a href="北立面.png">北立面</a>')
    if symmetric or redlines:
        page = page.replace('V1重设计候选', 'V2左右对称候选')
        page = page.replace('两侧冷凝肩舱', '左右镜像冷凝肩舱')
    if redlines:
        page = page.replace('V2左右对称候选', 'V3接口竖梁对位候选')
        page = page.replace('冷凝窗的四条坚固机壳竖梁移至接口同列；接口方块保持原位。',
            '冷凝窗外侧两组坚固机壳竖梁移入窗面，沿四个工业接口所在竖列贯穿；接口方块保留。')
    viewer = (out / 'viewer.bundle.js').read_text(encoding='utf-8')
    old_panel = 'panel:{pos:[m,6,-45],target:[m,2,3]'
    new_panel = 'panel:{pos:[r.controller[0]+.5,r.controller[1]+3,r.controller[2]-38],target:[r.controller[0]+.5,r.controller[1],r.controller[2]+.5]'
    assert viewer.count(old_panel) == 1
    (out / 'viewer.bundle.js').write_text(viewer.replace(old_panel, new_panel), encoding='utf-8')
    (out / 'index.html').write_text(page, encoding='utf-8')
    (out / '三维评审.html').write_text(page, encoding='utf-8')
    for stale_name in ('\u8a2d\u8a08\u8207\u6aa2\u67e5.json', '\u4e09\u7dad\u8a55\u5be9.html'):
        (out / stale_name).unlink(missing_ok=True)
    print(json.dumps({'out': str(out), 'blocks': len(blocks), 'materials': len(counts),
        'volume': volume, 'height': size_audit['actual_xyz'][1], 'bounds': bounds,
        'thresholds': audit['voltage_thresholds_passed'], 'png': str(out / '等轴预览.png')}, ensure_ascii=False))


if __name__ == '__main__':
    main(symmetric='--symmetric' in sys.argv[1:], redlines='--redlines' in sys.argv[1:])
