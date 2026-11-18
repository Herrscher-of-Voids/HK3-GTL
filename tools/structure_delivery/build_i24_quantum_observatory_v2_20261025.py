# -*- coding: utf-8 -*-
"""I24 三碟长基线天文庭院：生成实体、离线评审及逐格校验。

【变更记录 #1】2026-10-25 00:16:38（建筑候选 V2，不增加模组修订）
删除：不删除或覆盖 I24 V1 与既有确认原件。
新增：三座抛物接收碟、双翼计量舱、中央拱厅、原位主控及四个齐平接口。
修改：独立重建 I24 几何，复用标准 NBT/Schematic 编码和 I22 离线评审器。
用途：落实 I23 V8 确认后继续重设计 I24；只输出待审候选，不写游戏实例。

【变更记录 #2】2026-10-25 00:33:14（预览标记纠正，不增加模组修订）
删除：预览把工业接口和钻石主控改显为QEV壳的材质替换及局部图纯色代显。
新增：实际占位块材质核验、真实贴图局部图及只刷新预览的导出保留模式。
修改：三维、等轴与局部预览均显示industrial_port_casing和diamond_block真实纹理。
用途：执行已有标记规则；不改变建筑几何、标记位置或已导出结构文件。
"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import importlib.util
import io
import json
import math
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
from build_redesign69 import export, render
from material_resources import Resources
from structure_size_baseline import require

OUT = ROOT / 'deliveries/I24_量子异常观测阵列_三碟长基线天文庭院_V2_20261025'
NAME = 'hk3gtl-i24-three-dish-long-baseline-v2-20261025'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
VIEWER = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22'
W, H, D = 117, 66, 149
CX = W // 2
QEV = 'hk3gtl:voltage_machine_casing_qev'
PORT = 'hk3gtl:industrial_port_casing'
CONTROL = 'minecraft:diamond_block'
WHITE = 'gtceu:clean_machine_casing'
POWER = 'gtceu:high_power_casing'
COMPUTER = 'gtceu:advanced_computer_casing'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
GEAR = 'gtceu:tungstensteel_gearbox'
GLASS = 'minecraft:cyan_stained_glass'
LIGHT = 'minecraft:sea_lantern'
CELLS: dict[tuple[int, int, int], str] = {}
DISHES = [(25, 42, 23, 23, 15), (91, 42, 23, 23, 15), (58, 113, 35, 39, 23)]


def put(x, y, z, state, replace=False):
    pos = (int(x), int(y), int(z))
    if not (0 <= pos[0] < W and 0 <= pos[1] < H and 0 <= pos[2] < D):
        raise ValueError(f'实体越界：{pos} {state}')
    if replace or pos not in CELLS:
        CELLS[pos] = state


def box(lo, hi, state, replace=False):
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def beam(a, b, state, radius=0, replace=False):
    """用逐轴补齐的整方块折线表达斜梁，避免仅角接的悬浮体。"""
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


def disk(cx, cz, radius, y, state, inner=0, replace=False):
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            rr = (x - cx) ** 2 + (z - cz) ** 2
            if inner * inner <= rr <= radius * radius:
                put(x, y, z, state, replace)


def hall():
    """有实际计算栈的低位拱顶厅；主控替换它的正面皮肤。"""
    for x in range(43, 74):
        roof = 15 + round(11 * math.sqrt(max(0, 1 - ((x - CX) / 15) ** 2)))
        for z in range(0, 39):
            put(x, 0, z, GRATE)
            for y in range(1, roof + 1):
                edge = x in (43, 73) or z in (0, 38)
                if edge or y >= roof - 1:
                    state = QEV
                    if y in (3, 14) or (y >= roof - 1 and z % 10 in (0, 1)):
                        state = POWER
                    if edge and 16 <= y <= roof - 3 and abs(x - CX) <= 9:
                        state = GLASS
                    if x in (43, 73) and 6 <= y <= 11 and 7 <= z <= 31 and z % 8 > 1:
                        state = GLASS
                    if abs(x - CX) <= 1 and y == roof:
                        state = WHITE
                    put(x, y, z, state)
        # 拱顶每次高度跳变用实体竖面封闭。
        if x > 43:
            previous = 15 + round(11 * math.sqrt(max(0, 1 - ((x - 1 - CX) / 15) ** 2)))
            for y in range(min(roof, previous), max(roof, previous) + 1):
                for z in range(39):
                    put(x, y, z, QEV)
    for x in (48, 53, 63, 68):
        for z in range(7, 34, 6):
            box((x, 1, z), (x + 1, 12, z + 2), COMPUTER)
            box((x, 13, z), (x + 1, 13, z + 2), VENT)
    for x in (45, 71):
        beam((x, 2, 1), (x, 2, 37), LIGHT)
    # 控制器和输入口内部由真实计算背板接住。
    for x in (50, 58):
        beam((x, 8, 1), (x, 8, 13), COMPUTER)
    beam((66, 8, 37), (66, 8, 26), COMPUTER)


def baseline(cx):
    """135格长的连续仪器舱，包含122格净空参考轴和两端校准单元。"""
    for z in range(0, 135):
        for x in range(cx - 6, cx + 7):
            roof = 12 + round(4 * math.sqrt(max(0, 1 - ((x - cx) / 6) ** 2)))
            for y in range(roof + 1):
                if y == 0:
                    put(x, y, z, GRATE)
                elif x in (cx - 6, cx + 6) or z in (0, 134) or y >= roof - 1:
                    state = QEV
                    if z % 16 in (0, 1) or y in (3, 12):
                        state = POWER
                    if x in (cx - 6, cx + 6) and 6 <= y <= 10 and z % 16 in range(4, 13):
                        state = GLASS
                    put(x, y, z, state)
        # 参考轴留净空，仅端点有实际接收器；同步纹带位于屋脊而非接口托柱。
        put(cx, 17, z, WHITE if z % 8 == 0 else QEV)
        for x in (cx - 5, cx + 5):
            put(x, 1, z, LIGHT if z % 16 < 2 else GRATE)
    for z in (4, 130):
        box((cx - 3, 1, z), (cx + 3, 4, z + 1), QEV)
        box((cx - 3, 5, z), (cx + 3, 11, z + 1), COMPUTER)
        box((cx - 1, 7, z), (cx + 1, 9, z), GLASS, True)


def dish(cx, cz, radius, vertex, focal):
    """有厚度的抛物碟：铜背壳、银白反射面、三叉馈源及承重转台。"""
    pedestal = 10 if radius < 30 else 13
    for y in range(vertex - 1):
        rad = pedestal if y < 4 else max(5, pedestal - (y - 4) // 4)
        if y in (4, 5, vertex - 5, vertex - 4):
            rad += 2
        for x in range(cx - rad, cx + rad + 1):
            for z in range(cz - rad, cz + rad + 1):
                rr = (x - cx) ** 2 + (z - cz) ** 2
                if rr <= rad * rad and (rr >= (rad - 2) ** 2 or y in (0, 3, vertex - 2)):
                    put(x, y, z, POWER if y in (4, vertex - 4) else QEV)
    # 旋转齿圈和中轴属于接收碟本身，不承担任何接口。
    for y in (vertex - 5, vertex - 4):
        disk(cx, cz, pedestal + 2, y, GEAR, pedestal - 1, True)
        beam((cx-pedestal-2,y,cz),(cx+pedestal+2,y,cz),GEAR,replace=True)
        beam((cx,y,cz-pedestal-2),(cx,y,cz+pedestal+2),GEAR,replace=True)
    box((cx - 2, 1, cz - 2), (cx + 2, vertex, cz + 2), GEAR)
    for x in range(cx - radius, cx + radius + 1):
        for z in range(cz - radius, cz + radius + 1):
            r2 = (x - cx) ** 2 + (z - cz) ** 2
            if r2 > radius * radius:
                continue
            r = math.sqrt(r2)
            y = vertex + round(r2 / (4 * focal))
            # 主壳厚三格，内表面是反射片；径向铜肋贯穿各片。
            for yy in range(y - 3, y):
                put(x, yy, z, QEV, True)
            angle = math.atan2(z - cz, x - cx)
            rib = abs(math.sin(angle * 6)) < .065 and r > 5
            surface = QEV if rib or r >= radius - 1.6 else WHITE
            if radius - 5 < r < radius - 3.7:
                surface = POWER
            if r < 3:
                surface = GLASS
            put(x, y, z, surface, True)
            if r > radius - 1.1:
                put(x, y + 1, z, QEV, True)
    # 四条承力弧梁连接转台与碟背，受力路径从地基到反射碟连续可见。
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        endr = round(radius * .78)
        endy = vertex + round(endr * endr / (4 * focal)) - 3
        beam((cx + dx * 5, 8, cz + dz * 5),
             (cx + dx * endr, endy, cz + dz * endr), QEV, 1)
    focus = vertex + focal
    for angle in (-math.pi / 2, math.pi / 6, math.pi * 5 / 6):
        rx, rz = round(math.cos(angle) * (radius - 1)), round(math.sin(angle) * (radius - 1))
        rim_y = vertex + round((rx * rx + rz * rz) / (4 * focal))
        beam((cx + rx, rim_y, cz + rz), (cx, focus, cz), POWER)
        beam((cx + rx, rim_y + 1, cz + rz), (cx, focus + 1, cz), QEV)
    for y in range(focus - 2, focus + 4):
        disk(cx, cz, 3 if y in (focus - 2, focus + 3) else 2, y,
             QEV if y in (focus - 2, focus + 3) else GLASS, replace=True)
    put(cx, focus + 3, cz, LIGHT, True)
    # 馈源线是整方块暗色槽，落在背壳与中轴内部。
    beam((cx, 2, cz), (cx, vertex - 2, cz), COMPUTER, replace=True)


def build():
    CELLS.clear()
    hall()
    for cx in (14, 102):
        baseline(cx)
    # 连接前厅与双翼的低位有顶横廊，不另建接口面板。
    for x0, x1 in ((20, 43), (73, 96)):
        for x in range(x0, x1 + 1):
            for z in range(12, 21):
                put(x, 0, z, GRATE)
                for y in range(1, 13):
                    if z in (12, 20) or y >= 11:
                        put(x, y, z, GLASS if z in (12, 20) and 5 <= y <= 9 else QEV)
    for spec in DISHES:
        dish(*spec)
    # 设备环道、真实检修走廊与支承地梁组成稀疏基础，不铺满大平台。
    for spec in DISHES:
        cx, cz, radius, vertex, focal = spec
        disk(cx, cz, 15 if radius < 30 else 19, 0, GRATE, 11 if radius < 30 else 15)
    for cx, cz in ((25, 42), (91, 42), (58, 113)):
        bx = 14 if cx < CX else 102
        beam((cx, 0, cz), (bx, 0, cz), GRATE, 0)
        for dz in (-1, 0, 1):
            beam((cx, 0, cz + dz), (bx, 0, cz + dz), GRATE)
        beam((cx, 5, cz), (bx, 5, cz), COMPUTER)
    for x in (20, 96):
        beam((x, 0, 115), (CX, 0, 115), GRATE)
        beam((x, 5, 115), (CX, 5, 115), COMPUTER)
    # 两个仪器端厅吸纳探针和电能；外立面是完整舱体皮肤。
    for x0, x1, material in ((0, 20, QEV), (96, 116, QEV)):
        for x in range(x0, x1 + 1):
            for z in range(82, 105):
                for y in range(21):
                    if y in (0, 19, 20) or x in (x0, x1) or z in (82, 104):
                        state = material
                        if y in (3, 17):
                            state = POWER
                        if y == 20 and z % 5 < 2:
                            state = VENT
                        put(x, y, z, state, True)
        box((x0 + 3, 2, 85), (x1 - 3, 12, 100), COMPUTER)
    # 校准端厅内的计算硬件给参考光路让出完整3×3直通通道。
    for cx in (14, 102):
        for x in range(cx-1,cx+2):
            for y in range(7,10):
                for z in range(7,129):
                    CELLS.pop((x,y,z),None)
    ports = [
        {'id': 'PROBE-IN', 'pos': [0, 8, 93], 'face': 'west', 'surface_state': QEV,
         'purpose': '探针耗材与参考样本输入候选'},
        {'id': 'DATA-IN', 'pos': [50, 8, 0], 'face': 'north', 'surface_state': QEV,
         'purpose': '空间实验数据载体输入候选'},
        {'id': 'OBSERVATION-OUT', 'pos': [66, 8, 38], 'face': 'south', 'surface_state': QEV,
         'purpose': '量子异常谱与观测记录输出候选'},
        {'id': 'ENERGY-IN', 'pos': [116, 8, 93], 'face': 'east', 'surface_state': QEV,
         'purpose': '阵列仪器与校准供能候选'},
    ]
    for port in ports:
        x, y, z = port['pos']
        if port['face'] == 'west':
            beam((1, y, z), (8, y, z), COMPUTER, replace=True)
        if port['face'] == 'east':
            beam((115, y, z), (108, y, z), COMPUTER, replace=True)
        if CELLS.get((x, y, z)) != QEV:
            raise ValueError(f'接口未替换实际外壳：{port}')
        put(x, y, z, PORT, True)
    controller = [CX, 8, 0]
    assert CELLS[tuple(controller)] == QEV
    put(*controller, CONTROL, True)
    blocks = [{'pos': list(p), 'state': s} for p, s in sorted(CELLS.items(), key=lambda it: (it[0][1], it[0][2], it[0][0]))]
    zones = [
        {'name': '中央拱顶观测记录厅', 'min': [43, 0, 0], 'max': [73, 26, 38], 'pos': [58, 26, 19],
         'description': '低位铜壳拱厅内有四列计算栈。主控占整机第59格，和输入/输出口直接替换厅体外壳。'},
        {'name': '西翼长基线与探针校准舱', 'min': [0, 0, 0], 'max': [26, 20, 134], 'pos': [14, 20, 92],
             'description': '135格连续计量舱包覆122格净空参考轴，端厅接收探针耗材；与39格长的计算厅形成长短层级。'},
        {'name': '东翼长基线与供能舱', 'min': [90, 0, 0], 'max': [116, 20, 134], 'pos': [102, 20, 92],
         'description': '第二条独立观测基线参与交叉校验。供能口嵌在仪器端厅的东侧连续QEV外壳。'},
    ]
    for i, (cx, cz, r, vertex, focal) in enumerate(DISHES):
        zones.append({'name': ['西前端复测接收碟', '东前端交叉校验碟', '后场主异常谱接收碟'][i],
                      'min': [cx-r, 0, cz-r], 'max': [cx+r, vertex+focal+3, cz+r],
                      'pos': [cx, vertex+focal+3, cz],
                      'description': '厚铜背壳与分瓣银白反射面形成真实抛物曲面，三叉馈源臂收拢至焦点；承重转台和弧梁自地基连续接入碟背。'})
    return {'key': 'i24', 'name': NAME, 'title': '量子异常观测阵列',
            'candidate_version': '三碟长基线天文庭院 V2・待审', 'size': [W, H, D], 'blocks': blocks,
            'block_count': len(blocks), 'controller': controller, 'controller_face': 'north',
            'controller_surface': QEV, 'ports': ports, 'zones': zones,
            'paths': [{'name': '中央厅操作走廊', 'min': [55, 1, 2], 'max': [61, 5, 35]}],
            'links': [{'name': '西翼观测信号回传', 'points': [[14,5,113],[14,5,16],[43,5,16],[58,5,16]]},
                      {'name': '东翼观测信号回传', 'points': [[102,5,113],[102,5,16],[73,5,16],[58,5,16]]}],
            'description': '三座仰天接收碟与两翼远距基线复测异常，中央拱厅生成异常谱与观测记录；不直接产资源，不正式锁定坐标。',
            'target_voltage_appearance': 'QEV/V07，按负责人决定使用映射提案。'}


def audit(data):
    size = require(data)
    occupied = {tuple(b['pos']): b['state'] for b in data['blocks']}
    assert size['actual_xyz'] == data['size'] and size['min_pos'] == [0, 0, 0]
    remaining = set(occupied)
    component_sizes = []
    offsets = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    while remaining:
        todo = [remaining.pop()]
        count = 0
        while todo:
            x,y,z = todo.pop(); count += 1
            for dx,dy,dz in offsets:
                p = (x+dx,y+dy,z+dz)
                if p in remaining:
                    remaining.remove(p); todo.append(p)
        component_sizes.append(count)
    if len(component_sizes) != 1:
        raise ValueError(f'存在断开部件：{component_sizes}')
    faces = {'north': (0,0,-1), 'south': (0,0,1), 'west': (-1,0,0), 'east': (1,0,0)}
    ports = []
    for item in [*data['ports'], {'id':'CONTROLLER', 'pos':data['controller'], 'face':'north', 'surface_state':QEV}]:
        x,y,z = item['pos']; dx,dy,dz = faces[item['face']]
        neighbors = [(x+sx,y+sy,z) for sx,sy in ((-1,0),(1,0),(0,-1),(0,1))] if dz else [(x,y+sy,z+sz) for sy,sz in ((-1,0),(1,0),(0,-1),(0,1))]
        same = sum(occupied.get(p) == QEV for p in neighbors)
        assert same == 4, (item['id'], '四邻非连续原壳', same)
        assert (x-dx,y-dy,z-dz) in occupied, (item['id'], '无内部背板')
        for depth in range(1, 5):
            assert (x+dx*depth,y,z+dz*depth) not in occupied, (item['id'], '外侧不净空')
        ports.append({'id':item['id'], 'pos':item['pos'], 'same_shell_neighbors':same, 'inner_backed':True, 'outside_clear_depth':4})
    assert data['controller'][0] == W//2
    for cx in (14, 102):
        assert all((cx,8,z) not in occupied for z in range(7, 129)), '内部参考轴被阻挡'
    counts = collections.Counter(occupied.values())
    assert {s for s in counts if s.startswith('hk3gtl:')} == {QEV, PORT}
    assert counts[QEV] > max(n for s,n in counts.items() if s != QEV), 'QEV应为单一最多主体机壳'
    floor_ratio = sum(y == 0 for x,y,z in occupied)/(W*D)
    assert floor_ratio < .5
    return {'passed':True, 'blocks':len(occupied), 'size_check':size, 'component_count':1,
            'palette':dict(counts.most_common()), 'port_count':len(data['ports']), 'port_checks':ports,
            'controller_ordinal':W//2+1, 'floor_coverage_ratio':round(floor_ratio,4),
            'baseline_axis_clear_length':122, 'baseline_enclosure_length':135, 'computing_hall_length':39,
            'checks':['实际实体边界与声明一致，逐轴超过内测5最低尺寸。','全结构仅一个面连接组件，无独立悬浮部件。',
                      '两翼122格内部参考轴净空；基线舱135格，长于39格计算厅。','主控在整宽117的第59格，嵌于中央拱厅正面。',
                      '主控和四个接口四邻均为原QEV壳、内侧有背板、外侧连续4格可操作。',
                      '项目新增块仅使用QEV电压机壳与工业接口；所有材质模型必须为完整立方体。'],
            'paste_y':-60, 'highest_world_y':-60+H-1,
            'not_verified':['正式Controller/Pattern、实际电压能力与端口注册。','配方、研究执行、生存获取与首建材料闭环。',
                            '游戏内成型、运行及2.9.2兼容性。','本地file页面在浏览器中的实际交互；本轮只进行资源、数据和语法检查。']}


def resource_materials(states):
    resources = Resources(instance=INSTANCE, project_resources=ROOT/'src/main/resources')
    packs = json.loads(next(line.partition(':')[2] for line in (INSTANCE/'options.txt').read_text(encoding='utf-8').splitlines() if line.startswith('resourcePacks:')))
    try:
        for pack in packs:
            if not pack.startswith('file/'):
                continue
            path = INSTANCE/'resourcepacks'/pack[5:]
            archive = zipfile.ZipFile(path)
            resources.archives.append((path,archive))
            for name in archive.namelist():
                if name.startswith('assets/'):
                    resources.index[name] = (path,archive)
        materials = []
        for state in states:
            # 每种方块显示自身实际纹理；自然融合指位置齐平，不得把标记伪装成外壳。
            material = dict(resources.material(state))
            assert material['complete_cube'] and not material['tinted']
            assert material['state'] == state
            materials.append(material)
        by_state = {material['state']: material for material in materials}
        for marker in (PORT, CONTROL):
            assert by_state[marker]['faces'] != by_state[QEV]['faces'], '标记纹理不得被QEV外壳替代'
        return materials, dict(resources.sources), packs
    finally:
        resources.close()


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)


def report_images(data, materials, check):
    colors = {}
    textures = {}
    for material in materials:
        texture = Image.open(io.BytesIO(base64.b64decode(material['faces']['north'].split(',')[1]))).convert('RGB')
        colors[material['state']] = tuple(round(c) for c in ImageStat.Stat(texture).mean)
        textures[material['state']] = {
            face: Image.open(io.BytesIO(base64.b64decode(material['faces'][face].split(',')[1]))).convert('RGB')
            for face in ('north','south','west','east')}
    image = Image.new('RGB',(1640,1390),'#14212d'); draw = ImageDraw.Draw(image)
    draw.text((42,28),'I24 · 三碟长基线天文庭院 / 实体俯视布局',font=font(30),fill='#eaf0f3')
    scale,left,top = 8,60,108
    tops = {}
    for block in data['blocks']:
        x,y,z = block['pos']
        if (x,z) not in tops or y > tops[x,z][0]: tops[x,z] = (y,block['state'])
    for (x,z),(y,state) in tops.items():
        draw.rectangle((left+x*scale,top+z*scale,left+(x+1)*scale-1,top+(z+1)*scale-1),fill=colors[state])
    draw.rectangle((left-1,top-1,left+W*scale,top+D*scale),outline='#69818b')
    lx=1055
    for i,item in enumerate([{'id':'主控','purpose':'中央拱厅原位主壳','pos':data['controller']},*data['ports']]):
        x,y,z=item['pos']; px,pz=left+x*scale+4,top+z*scale+4
        draw.ellipse((px-6,pz-6,px+6,pz+6),fill='#ffcf6b',outline='#17212a',width=2)
        draw.text((lx,125+i*94),item['id'],font=font(20),fill='#ffcf6b')
        draw.text((lx,154+i*94),item['purpose'],font=font(17),fill='#e6ecee')
        draw.text((lx,179+i*94),str(item['pos']),font=font(17),fill='#afc4cd')
    for i,line in enumerate(['117 × 149 × 66（宽×长×高）','最低标准：65 × 81 × 49',f'{check["blocks"]:,} 个实际方块','QEV / V07 · 深铜棕主壳','双翼基线舱：135格','中央记录厅：39格','主控：整宽第59格','前双碟：直径47格','后主碟：直径71格','无整块大平台；分段设备基础']):
        draw.text((lx,660+i*40),line,font=font(19),fill='#c7d6df')
    image.save(OUT/'俯视布局.png')
    iso=Image.open(OUT/'等轴预览.png').convert('RGB'); dr=ImageDraw.Draw(iso)
    dr.rectangle((0,0,iso.width,45),fill='#101925');dr.text((20,9),'I24 量子异常观测阵列 · 三碟长基线天文庭院 V2',font=font(22),fill='#e9e1d8')
    dr.rectangle((0,iso.height-43,iso.width,iso.height),fill='#101925')
    dr.text((20,iso.height-36),f'117 × 149 × 66 | {check["blocks"]:,} 方块 | QEV / V07 | 建筑候选待审',font=font(20),fill='#c8bbb0')
    iso.save(OUT/'等轴预览.png')
    # 各接口只画真实外壳7×7局部，检查图上的黄色框不导出成建筑。
    sheet=Image.new('RGB',(1500,1130),'#14212d');sd=ImageDraw.Draw(sheet)
    items=[{'id':'CONTROLLER','purpose':'主控 / 整机宽度第59格','pos':data['controller'],'face':'north'},*data['ports']]
    occupied={tuple(b['pos']):b['state'] for b in data['blocks']}
    sd.text((35,22),'主控与接口 · 在真实设备外壳内齐平替换',font=font(28),fill='#f0e1c9')
    for i,item in enumerate(items):
        left=30+(i%3)*490;top=90+(i//3)*500
        sd.text((left,top),item['id'],font=font(22),fill='#ffcf6b')
        sd.text((left,top+34),item['purpose'],font=font(17),fill='#d3dfe7')
        sd.text((left,top+62),f'{item["pos"]} · {item["face"]}',font=font(17),fill='#afc4cd')
        x,y,z=item['pos']
        for dy in range(-3,4):
            for u in range(-3,4):
                pos=(x+u,y+dy,z) if item['face'] in ('north','south') else (x,y+dy,z+u)
                px,py=left+(u+3)*48,top+110+(3-dy)*48
                state = occupied.get(pos)
                if state:
                    sheet.paste(textures[state][item['face']].resize((47,47),Image.Resampling.NEAREST),(px,py))
                else:
                    sd.rectangle((px,py,px+46,py+46),fill=(22,37,47))
                sd.rectangle((px,py,px+46,py+46),outline='#53606a')
                if u==dy==0:sd.rectangle((px+3,py+3,px+43,py+43),outline='#fff1a8',width=3)
    sheet.save(OUT/'主控与接口局部.png')


def viewer_page(data,check):
    page=(VIEWER/'三维评审.html').read_text(encoding='utf-8')
    page=re.sub(r'<title>.*?</title>','<title>I24 · 三碟长基线天文庭院 V2</title>',page,count=1,flags=re.S)
    page=re.sub(r'<header>.*?</header>',f'<header><a href="index.html">← I24交付总览</a><h1>I24 · 量子异常观测阵列 · 三碟长基线天文庭院 V2</h1><div>{W}×{D}×{H}（宽×长×高） · {check["blocks"]:,}方块 · 可旋转、剖切及逐口定位</div></header>',page,count=1,flags=re.S)
    page=re.sub(r'<div id="viewName"></div><div class="locator">.*?</div>',f'<div id="viewName"></div><div class="locator"><b>主控 {data["controller"]}</b><p>117格整宽的第59格，朝北嵌入中央拱顶记录厅。主控显示钻石块，接口显示本模组工业接口块，均齐平替换其设备外壳。</p><p>黄色轮廓只作定位，不替代方块真实材质。</p><button data-view="controller">定位主控</button></div>',page,count=1,flags=re.S)
    page=re.sub(r'<details open><summary>本次结构修改</summary>.*?</details>','<details open><summary>本次结构修改</summary><p>重建为三座仰天抛物面接收碟、两翼长基线仪器舱与低位中央拱厅。QEV深铜棕外壳统领银白反射面和青色观察窗。</p></details>',page,count=1,flags=re.S)
    page=re.sub(r'<details><summary>结构文件与边界</summary>.*?</details>',f'<details><summary>结构文件与边界</summary><a href="i24/{NAME}.nbt">NBT</a> · <a href="i24/{NAME}.schem">Schematic</a> · <a href="verification.json">检查</a><p>待审建筑候选，QEV/V07；未接入Pattern、配方或实例。</p></details>',page,count=1,flags=re.S)
    page=re.sub(r'<label>剖切高度 <b id="layerValue">\d+</b><input id="layer" type="range" min="0" max="\d+" value="\d+">',f'<label>剖切高度 <b id="layerValue">{H-1}</b><input id="layer" type="range" min="0" max="{H-1}" value="{H-1}">',page,count=1)
    page=page.replace('变更记录#1：2026-10-23 10:57:25；新融合候选离线评审，不代表正式接入。','变更记录#1：2026-10-25 00:16:38；I24全新三碟候选，未接入游戏。')
    page=page.replace('id="showPorts" type="checkbox">接口</label>','id="showPorts" type="checkbox">接口定位框</label>')
    return page.replace('</html>','<!-- 变更记录#2：2026-10-25 00:33:14；主控与接口恢复显示真实钻石块及工业接口块材质。 --></html>')


def report_page(data,check):
    zones=''.join(f'<article><h3>{html.escape(z["name"])}</h3><p>{html.escape(z["description"])}</p></article>' for z in data['zones'])
    palette=''.join(f'<tr><td><code>{html.escape(s)}</code></td><td>{n:,}</td></tr>' for s,n in check['palette'].items())
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I24 · 三碟长基线天文庭院 V2</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#111b26;color:#e4e9ed;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1450px;margin:auto;padding:28px}}header{{border-left:5px solid #bd8059;background:#29313b;padding:25px}}h1{{margin:0}}a{{color:#e7bc96}}.meta,.zones{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin:20px 0}}article,.meta>div{{background:#1c2a36;padding:16px;border:1px solid #3f505c}}img{{display:block;max-width:100%;height:auto;margin:18px auto}}iframe{{width:100%;height:850px;border:1px solid #6c645a}}.note{{padding:14px;background:#333529;border-left:4px solid #bd9e62}}table{{border-collapse:collapse;width:100%}}td{{padding:9px;border-bottom:1px solid #3f505c}}code{{overflow-wrap:anywhere}}@media(max-width:700px){{main{{padding:12px}}iframe{{height:650px}}}}</style></head><body><main>
<header><small>HK3GTL / I24 / 全新候选 V2</small><h1>量子异常观测阵列</h1><p>三碟长基线天文庭院：前部双碟独立复测，后部大型主碟捕获异常谱；两翼计量舱将远端信号送回低位拱顶记录厅。</p></header>
<div class="meta"><div><b>117 × 149 × 66</b><br>宽×长×高；最低标准65×81×49</div><div><b>{check['blocks']:,} 实体方块</b><br>一体连通 · 分段基础</div><div><b>QEV / V07</b><br>实际深铜棕机壳为主</div><div><b>主控 [58,8,0]</b><br>整宽第59格 · 4个齐平接口</div></div>
<p><a href="三维评审.html">打开三维评审</a> · <a href="i24/{NAME}.nbt">NBT</a> · <a href="i24/{NAME}.schem">Schematic</a> · <a href="../{OUT.with_suffix('.zip').name}">完整ZIP</a> · <a href="verification.json">结构检查</a></p>
<img src="等轴预览.png" alt="I24 V2实际逐格材质等轴预览">
<h2>从量子异常观测出发的建筑</h2><p>三座碟形接收器是本机的视觉主体。反射面有曲率、厚背壳、径向分瓣、边缘束环与焦点馈源；下方转台和承力弧梁接入实体基础。前端双碟与后端主碟构成长短基线，计算建筑收低，让接收设施保持清楚的天际线。</p>
<p>QEV铜棕皮肤包覆碟背、转台、计量舱和中央拱厅；银白机壳作为反射片，青色玻璃作为仪器观察窗。所有形体均由完整1×1×1方块构成。</p>
<h2>俯视与功能分区</h2><img src="俯视布局.png" alt="三碟与双翼基线的实际俯视布局"><div class="zones">{zones}</div>
<h2>主控与接口融入设备本体</h2><p>主控直接替换中央拱厅正面中间的一格QEV外壳；数据入口同在前墙，记录出口位于后墙。探针入口和供能口分别置于两翼的真实仪器端厅侧墙。五处标记四周均为连续原壳、内侧有设备背板，外面留有操作净空。</p><img src="主控与接口局部.png" alt="主控与四个接口的真实外壳局部">
<p>预览与结构文件一致：主控使用钻石块 <code>minecraft:diamond_block</code>，四个接口使用本模组工业方块 <code>hk3gtl:industrial_port_casing</code>；显示各自真实材质，黄色轮廓仅用于定位。</p>
<h2>离线三维评审</h2><p>沿用旋转、剖切、分区、逐口定位和保存视角操作。<a href="三维评审.html">单独打开</a></p><iframe src="三维评审.html" title="I24 V2三维评审" loading="lazy"></iframe>
<h2>材料</h2><table>{palette}</table><p>材质来自当前增强版2.9实例及其已启用file资源包；项目QEV机壳取当前源码资源。静态材质预览不模拟游戏光照。</p>
<p class="note">I24 V2 为待审建筑候选。职责仅是发现、复测并输出异常谱和观测记录；由I25解析、I44锁定坐标。本交付未写入正式Pattern或游戏实例，游戏成型、研究/配方、生存获取及2.9.2兼容性仍待相应接入验收。</p>
<p><a href="manifest.json">候选清单</a> · <a href="设计依据.json">设计依据</a> · <a href="设计与检查.json">设计与检查</a></p></main><!-- 变更记录#1：2026-10-25 00:16:38；新增I24三碟长基线候选评审。 --><!-- 变更记录#2：2026-10-25 00:33:14；预览标记恢复真实工业接口块及钻石块材质。 --></body></html>'''


def retained_exports(data):
    """仅修预览时回读已有结构，确认逐格一致后保留原文件及哈希。"""
    import nbtlib
    import numpy as np
    states = sorted({b['state'] for b in data['blocks']})
    indices = {state:index for index,state in enumerate(states)}
    expected = {tuple(b['pos']):b['state'] for b in data['blocks']}
    manifest = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    hashes = {}
    for kind in ('nbt','schem'):
        path = OUT/'i24'/f'{NAME}.{kind}'
        hashes[kind] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert hashes[kind] == manifest[kind+'_sha256']
    nbt = nbtlib.load(OUT/'i24'/f'{NAME}.nbt')
    assert list(map(int,nbt['size'])) == data['size']
    palette = []
    for entry in nbt['palette']:
        properties = entry.get('Properties',{})
        palette.append(str(entry['Name']) + ('['+','.join(f'{k}={v}' for k,v in sorted(properties.items()))+']' if properties else ''))
    assert {tuple(map(int,b['pos'])):palette[int(b['state'])] for b in nbt['blocks']} == expected
    groups = [[] for _ in states]
    dense = np.zeros(W*H*D,dtype=np.uint8)
    for block in data['blocks']:
        x,y,z = block['pos']; index = (y*D+z)*W+x; sid=indices[block['state']]
        groups[sid].append(index); dense[index] = sid+1
    schem = nbtlib.load(OUT/'i24'/f'{NAME}.schem')
    assert [int(schem[k]) for k in ('Width','Height','Length')] == data['size']
    assert {str(k):int(v) for k,v in schem['Palette'].items()} == {'minecraft:air':0,**{s:i+1 for s,i in indices.items()}}
    assert np.array_equal(np.asarray(schem['BlockData']).view(np.uint8),dense)
    return states,groups,hashes


def main():
    data=build(); check=audit(data)
    if OUT.exists():
        manifest=OUT/'manifest.json'
        if not manifest.is_file() or json.loads(manifest.read_text(encoding='utf-8')).get('generator') != Path(__file__).name:
            raise FileExistsError(f'拒绝覆盖未知目录：{OUT}')
    OUT.mkdir(exist_ok=True); (OUT/'i24').mkdir(exist_ok=True); (OUT/'生成脚本').mkdir(exist_ok=True)
    if '--refresh-preview' in sys.argv:
        states,groups,hashes=retained_exports(data)
    else:
        # 先写来源身份，后续视觉迭代只准覆盖本生成器自己产生的候选。
        (OUT/'manifest.json').write_text(json.dumps({'generator':Path(__file__).name},ensure_ascii=False),encoding='utf-8')
        states,groups,hashes=export(data,OUT/'i24')
    materials,sources,packs=resource_materials(states)
    check['hashes']=hashes;check['material_resource_sources']=sources;check['enabled_file_resource_packs']=packs
    check['material_complete_cube']=all(m['complete_cube'] and not m['tinted'] for m in materials)
    check['marker_preview_identity']={
        'passed':True,'controller':CONTROL,'interfaces':PORT,
        'display':'三维及静态图使用方块自身实际纹理，不映射到周围机壳。',
        'texture_sha256':{m['state']:{face:hashlib.sha256(base64.b64decode(texture.split(',')[1])).hexdigest() for face,texture in m['faces'].items()} for m in materials if m['state'] in (PORT,CONTROL)}}
    reference=[
        {'path':'doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html','fact':'I24最低宽长高65×81×49；远距观测基线长于计算舱两翼。'},
        {'path':'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json','fact':'异常发现与复测、多来源异常谱校验、世界泡候选信号筛选；产观测数据，不直接产资源或正式锁坐标。'},
        {'path':'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html','fact':'按负责人决定采用QEV/V07作为结构制作映射。'},
        {'path':'deliveries/I01-I18_控制器居中融合修订_V2_20261023','fact':'居中主控、设备承载接口与有体量的功能分区。'},
        {'path':'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023','fact':'沿用已确认的离线评审布局与实体层级，不复制反应堆主题。'},
        {'path':'deliveries/I23_崩坏能相变释能机_双瓣相界锻炉_V8_20261024','fact':'承接负责人确认的完整设备皮肤、强主体和自然接口融合要求，I24采用不同的观测器轮廓。'},
        {'path':'rule/当前多方块设计规则.md','fact':'最低尺寸扩展、整方块、主控居中、接口本体融合、项目自有块白名单。'}]
    def write_json(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    payload={'data':{k:v for k,v in data.items() if k!='blocks'},'palette':states,'groups':groups,'materials':materials,'audit':check,'names':{}}
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),compresslevel=9)).decode('ascii')
    (OUT/'data.js').write_text('window.HK3_PAYLOAD="'+encoded+'";\n',encoding='utf-8')
    # 真实解码预览逐格索引，与已回读的NBT/Schematic源位置完全比较。
    read=json.loads(gzip.decompress(base64.b64decode(encoded)))
    decoded={((index%W),(index//(W*D)),(index//W)%D):state for state,group in zip(read['palette'],read['groups']) for index in group}
    assert decoded == {tuple(b['pos']):b['state'] for b in data['blocks']}
    check['nbt_schem_viewer_exact_cell_readback']=True
    shutil.copy2(VIEWER/'viewer.bundle.js',OUT/'viewer.bundle.js')
    render(data,materials,OUT);report_images(data,materials,check)
    (OUT/'三维评审.html').write_text(viewer_page(data,check),encoding='utf-8')
    (OUT/'index.html').write_text(report_page(data,check),encoding='utf-8')
    write_json('设计依据.json',reference)
    write_json('设计与检查.json',{'data':{k:v for k,v in data.items() if k!='blocks'},'audit':check})
    write_json('manifest.json',{'generator':Path(__file__).name,'key':'i24','title':data['title'],'candidate_version':data['candidate_version'],
        'status':'candidate_waiting_user_review','candidate_approved':False,'target_voltage':'QEV','target_voltage_mapping':'V07',
        'size_xyz':[W,H,D],'size_wdh':[W,D,H],'baseline_wdh':[65,81,49],'block_count':check['blocks'],
        'controller':data['controller'],'controller_face':'north','ports':data['ports'],'palette':check['palette'],
        'nbt_sha256':hashes['nbt'],'schem_sha256':hashes['schem'],
        'source_instance':str(INSTANCE),'supersedes':'I24 V1被要求重设计，保留V1历史文件。',
        'claim_boundary':'仅建筑候选；未部署、未获批准、未声称Pattern/配方/生存与游戏运行通过。'})
    shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    files={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='verification.json'}
    check['files_sha256_before_verification']=files
    write_json('verification.json',check)
    bundle=OUT.with_suffix('.zip')
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as package:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():package.write(p,p.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(bundle) as package:
        assert package.testzip() is None
        assert set(package.namelist()) == {f'{OUT.name}/{p.relative_to(OUT).as_posix()}' for p in OUT.rglob('*') if p.is_file()}
        for p in OUT.rglob('*'):
            if p.is_file():assert package.read(f'{OUT.name}/{p.relative_to(OUT).as_posix()}')==p.read_bytes()
    digest=hashlib.sha256(bundle.read_bytes()).hexdigest();bundle.with_suffix('.zip.sha256').write_text(digest+'\n',encoding='ascii')
    print(json.dumps({'out':str(OUT),'size_xyz':[W,H,D],'blocks':check['blocks'],'palette':check['palette'],'zip_sha256':digest,'verified':True},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
