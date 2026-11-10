# -*- coding: utf-8 -*-
"""I20检修厂房与完整外围道路修订，只生成新的待审候选。

【文件职责】在V2西南空区增加检修厂房，将南侧外围路后退10格并接长两侧道路。
【变更记录 #1】2026-10-23 20:00:24（建筑候选V3，不增加模组修订号）
删除：西南空区内失去外围作用的旧南路地面，不拆任何I19方块。
新增：QSV检修厂房、桥式吊车、检修工位、备件架、卸件通廊及后侧维护通道。
修改：南路从Z218–222移到Z228–232，后墙外留Z223–227五格净空，主控继续沿用I19。
用途：落实负责人补厂房及外围路完整包住厂房的要求；设备造型不等于真实配方或机械功能。
"""
import copy
import hashlib
import json
import math

import numpy as np
from scipy.ndimage import label

from build_i20_qsv_second_unit_v1 import Extension, STATES, QSV, AIR, WHITE, STEEL, VESSEL, GLASS, PIPE, GRATE, VENT, PANEL, GEAR
from build_i20_qsv_inherited_controller_v2 import ROOT, BASE, build as build_v2
from structure_size_baseline import require

OUT = ROOT/'deliveries/I20_中型崩坏能反应堆_检修厂房与外围路修订_V3_20261023'
LOG = ROOT/'logs/i20-maintenance-v3-20261023'
NAME = 'i20-qsv-maintenance-workshop-v3'
W, H, D = 271, 155, 233
SOURCE_V2 = ROOT/'deliveries/I20_中型崩坏能反应堆_原位主控修订_V2_20261023/i20/blueprint.json'


class Site(Extension):
    """重用已核对的厂房词汇，写入时阻止任何I19异材覆盖。"""
    def __init__(self, before, inherited):
        self.cells = np.zeros((H, D, W), dtype=np.uint8)
        self.original = np.zeros_like(self.cells)
        for data, target in ((before, self.cells), (inherited, self.original)):
            for b in data['blocks']:
                x, y, z = b['pos']; target[y, z, x] = STATES.index(b['state'])
        self.ports = copy.deepcopy(before['ports'])
        self.paths = copy.deepcopy(before['paths'])
        self.zones = copy.deepcopy(before['zones'])

    def box(self, lo, hi, mat, shell=False):
        x0, y0, z0 = lo; x1, y1, z1 = hi
        assert 0 <= x0 <= x1 < W and 0 <= y0 <= y1 < H and 0 <= z0 <= z1 < D
        if shell:
            for y in (y0, y1): self.box((x0, y, z0), (x1, y, z1), mat)
            for x in (x0, x1): self.box((x, y0, z0), (x, y1, z1), mat)
            for z in (z0, z1): self.box((x0, y0, z), (x1, y1, z), mat)
            return
        old = self.original[y0:y1+1, z0:z1+1, x0:x1+1]
        assert not np.any((old != AIR) & (old != mat)), ('覆盖I19原块', lo, hi)
        self.cells[y0:y1+1, z0:z1+1, x0:x1+1] = mat


def build():
    before, geometry = build_v2()
    original = json.loads(BASE.read_text(encoding='utf-8'))
    a = Site(before, original)
    # 厂房原后墙在Z222，外围路退出建筑投影，五格宽的后侧维护带连续通行。
    a.box((0, 0, 218), (107, 0, 222), AIR)
    a.box((6, 0, 184), (107, 0, 227), GRATE)
    a.box((6, 0, 223), (265, 0, 227), GRATE)
    a.box((0, 0, 218), (5, 0, 232), STEEL)
    a.box((266, 0, 223), (270, 0, 232), STEEL)
    a.box((0, 0, 228), (270, 0, 232), STEEL)
    for path in a.paths:
        if path['name'] == 'QSV外侧操作道': path['max'][2] = 232

    # 检修厅采用低于透平厅的连续拱顶，天窗和门式框架共同表达机械车间。
    a.hall((12, 2, 186), (103, 31, 220))
    a.box((13, 31, 187), (102, 31, 219), AIR)
    for z in range(187, 220):
        roof = 31+round(6*math.sin(math.pi*(z-186)/34))
        for x0, x1 in ((12, 103),):
            a.box((x0, roof-1, z), (x1, roof, z), QSV)
        for x in (12, 103): a.box((x, 31, z), (x, roof, z), QSV)
        if 197 <= z <= 209:
            for x in (28, 60): a.box((x, roof, z), (x+7, roof, z), GLASS)
    for x in (12, 40, 68, 102):
        for z in (186, 219): a.box((x, 2, z), (x+1, 31, z+1), QSV)
        for z in range(187, 220):
            roof = 31+round(6*math.sin(math.pi*(z-186)/34))
            a.box((x, roof-3, z), (x+1, roof-2, z), WHITE)
    for x0, x1 in ((22, 33), (78, 89), (97, 101)):
        a.box((x0, 2, 186), (x1, 11 if x0 != 97 else 7, 187), AIR)

    # 两根连续吊车轨梁由厂房立柱托住，桥架、起升箱和吊具均有实体连接。
    for z in (191, 215): a.box((15, 23, z-1), (100, 24, z+1), STEEL)
    for x in (15, 40, 68, 100):
        for z in (188, 218):
            a.box((x, 2, z), (x+1, 23, z+1), QSV)
            a.box((x, 23, min(z, 191 if z == 188 else 215)),
                  (x+1, 23, max(z+1, 191 if z == 188 else 215)), STEEL)
    a.box((49, 25, 191), (51, 26, 215), QSV)
    a.box((48, 25, 201), (52, 28, 205), GEAR)
    a.box((50, 14, 203), (50, 24, 203), PIPE)
    a.box((49, 13, 202), (51, 14, 204), VESSEL)

    # 设备拆装床、三组待修泵转子及后墙备件架，留出真实的卸件和工位通廊。
    a.box((42, 2, 198), (57, 4, 209), STEEL)
    a.box((47, 5, 199), (53, 10, 208), VESSEL, True)
    a.box((49, 6, 199), (51, 9, 199), GEAR)
    for x in (24, 64, 82):
        a.box((x-4, 2, 194), (x+6, 3, 211), STEEL)
        a.box((x-2, 4, 198), (x+4, 9, 207), VESSEL, True)
        a.box((x-1, 5, 197), (x+2, 8, 197), GEAR)
        a.box((x-1, 10, 200), (x+3, 11, 205), QSV)
    for x0, x1 in ((22, 36), (72, 94)):
        for y in (2, 5, 8): a.box((x0, y, 217), (x1, y, 218), STEEL)
        for x in (x0, x1): a.box((x, 2, 217), (x, 9, 218), QSV)
        for x in range(x0+2, x1-2, 4):
            a.box((x, 3, 217), (x+1, 4, 218), PANEL)
            a.box((x, 6, 217), (x+1, 7, 218), VENT)
    a.box((103, 2, 198), (108, 12, 207), QSV, True)
    a.box((104, 0, 198), (107, 1, 207), STEEL)
    a.box((103, 2, 201), (108, 8, 204), AIR)
    a.paths += [
        {'name': '检修厂房北侧卸件通廊', 'min': [18, 3, 190], 'max': [99, 6, 192]},
        {'name': '检修厂房中央工位通道', 'min': [36, 3, 193], 'max': [41, 6, 215]},
        {'name': '检修厂房后侧工位通道', 'min': [22, 3, 213], 'max': [97, 6, 215]},
        {'name': '新旧附属厅连接通道', 'min': [99, 3, 201], 'max': [117, 6, 204]},
        {'name': '厂房后墙外五格维护带', 'min': [6, 1, 223], 'max': [265, 4, 227]},
        {'name': '后退十格的南侧完整外围路', 'min': [0, 1, 228], 'max': [270, 4, 232]},
        {'name': '西侧完整外围路', 'min': [0, 1, 184], 'max': [5, 4, 232]}]
    for path in a.paths:
        x0, y0, z0 = path['min']; x1, y1, z1 = path['max']
        assert np.all(a.cells[y0:y1+1, z0:z1+1, x0:x1+1] == AIR), path
    frozen = a.original != AIR
    assert np.array_equal(a.cells[frozen], a.original[frozen])
    _, components = label(a.cells != AIR)
    assert components == 1, components
    yy, zz, xx = np.nonzero(a.cells)
    blocks = [{'pos': [int(x), int(y), int(z)], 'state': STATES[int(a.cells[y, z, x])]}
              for y, z, x in zip(yy, zz, xx)]
    data = {k: copy.deepcopy(v) for k, v in before.items() if k != 'blocks'}
    data.update(name=NAME, candidate_version='检修厂房与外围路修订V3・待审', size=[W, H, D],
                blocks=blocks, block_count=len(blocks), paths=a.paths, ports=a.ports)
    data['zones'] = a.zones+[{'name': 'QSV桥式吊车检修厂房', 'pos': [57, 38, 203]}]
    data['description'] = '保留I19原厂区和主控，QSV第二机组新增检修厂房；外围路退至全体厂房之后形成完整闭环。'
    data['integration_revision']['principle'] = 'I19主控原位、16接口原位；在原西南空区补完整检修厂房，外围路包住全部厂房。'
    data['layout_gap'] = {'id': 'A', 'status': '按用户本轮要求补建检修厂房及卸件维护空间',
                          'workshop_min': [12, 0, 186], 'workshop_max': [103, 37, 220],
                          'equipment': ['连续桥式吊车', '中央拆装床', '三组待修泵转子', '后墙备件架'],
                          'connection': '东侧连廊接QSV仪控厅；北门接联合检修路；南后墙外接外围维护带'}
    data['perimeter_revision'] = {'old_south_road_z': [218, 222], 'new_south_road_z': [228, 232],
        'shift_blocks': 10, 'rear_wall_max_z': 222, 'clear_strip_z': [223, 227], 'clear_width': 5,
        'west_road_x': [0, 5], 'east_road_x': [266, 270], 'encloses_all_halls': True}
    size_check = require(data)
    geometry.update(size_check=size_check, components=int(components), paths_clear=True, paths_checked=len(a.paths),
                    layout_gap=data['layout_gap'], perimeter_revision=data['perimeter_revision'])
    geometry.pop('revision_from_v1', None)
    geometry['inheritance']['added_blocks'] = len(blocks)-len(original['blocks'])
    geometry['revision_source'] = {'path': str(SOURCE_V2), 'sha256': hashlib.sha256(SOURCE_V2.read_bytes()).hexdigest()}
    return data, geometry


if __name__ == '__main__':
    data, checks = build()
    LOG.mkdir(exist_ok=True)
    (LOG/'geometry-preview.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'blocks': data['block_count'], 'size': data['size'], 'controller': data['controller'], 'checks': checks}, ensure_ascii=False))
