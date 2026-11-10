# -*- coding: utf-8 -*-
"""I20中型崩坏能反应堆的原位扩建候选几何，不写正式资源或游戏实例。

【文件职责】读取I19原蓝图，在东侧及南侧新增QSV第二机组；保留全部原块、颜色和接口。
【变更记录 #1】2026-10-23 17:02:11（候选制作，不增加模组修订）
删除：无。新增：QSV冷却塔、圆顶核岛、燃料/泵房、联合仪控与透平厅。
修改：在原空气区扩建，新增主控置于整宽第136格的实际仪控厅墙面。
用途：表达累积工程演进；位置标记、管路与设备造型不代表真实能源功能。
【变更记录 #2】2026-10-23 17:11:00（静态通行与壳体检查）
删除：无。新增：QSV燃料热室西侧操作路面。修改：圆顶高斜率层增加搭接壳厚。
用途：消除顶部悬空环并让燃料接口从连续路面可达；不改变任何I19方块。
【变更记录 #3】2026-10-23 18:09:49（设备连接及屋架复核）
删除：透平回流与设备之间的空气缺口。新增：两只燃料容器接主转运管的支线、透平厅横向门架。
修改：回流端接入第三段透平上壳；用途：使管线接到实际设备，并明确拱面屋顶的承重节奏。
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
import math

import numpy as np
from scipy.ndimage import label

from build_i19_hbv_coastal_station_v3 import STATES as OLD_STATES
from build_i19_hbv_coastal_station_v3 import AIR, HBV, WHITE, STEEL, VESSEL, GLASS, PIPE, GRATE, VENT, PANEL, GEAR, PORT, CORE
from redesign69_geometry import ROOT
from structure_size_baseline import require

OUT = ROOT / 'deliveries/I20_中型崩坏能反应堆_双岛复合厂区扩建候选_V1_20261023'
LOG = ROOT / 'logs/i20-next-candidate-20261023'
BASE = ROOT / 'deliveries/I19_小型崩坏能反应堆_单塔蓝湾独立候选_V3_20261023/i19/blueprint.json'
W, H, D = 271, 155, 223
NAME = 'i20-qsv-second-unit-v1'
STATES = OLD_STATES + ['hk3gtl:voltage_machine_casing_qsv']
QSV = len(OLD_STATES)


class Extension:
    """数组只在新区域落块，旧体素若发生异材覆盖立即拒绝。"""
    def __init__(self, before):
        self.cells = np.zeros((H, D, W), dtype=np.uint8)
        for block in before['blocks']:
            x, y, z = block['pos']
            self.cells[y, z, x] = STATES.index(block['state'])
        self.original = self.cells.copy()
        self.ports = copy.deepcopy(before['ports'])
        self.zones = copy.deepcopy(before['zones'])
        self.paths = copy.deepcopy(before['paths'])

    def box(self, lo, hi, mat, shell=False):
        x0, y0, z0 = map(int, lo); x1, y1, z1 = map(int, hi)
        assert 0 <= x0 <= x1 < W and 0 <= y0 <= y1 < H and 0 <= z0 <= z1 < D, (lo, hi)
        if shell:
            for y in (y0, y1): self.box((x0, y, z0), (x1, y, z1), mat)
            for x in (x0, x1): self.box((x, y0, z0), (x, y1, z1), mat)
            for z in (z0, z1): self.box((x0, y0, z), (x1, y1, z), mat)
            return
        original = self.original[y0:y1+1, z0:z1+1, x0:x1+1]
        assert not np.any((original != AIR) & (original != mat)), ('覆盖I19原块', lo, hi, STATES[mat])
        self.cells[y0:y1+1, z0:z1+1, x0:x1+1] = mat

    def ring(self, cx, cz, y, radius, thick, mat, filled=False):
        r = math.ceil(radius)
        x0, x1 = max(0, cx-r), min(W-1, cx+r)
        z0, z1 = max(0, cz-r), min(D-1, cz+r)
        zz, xx = np.ogrid[z0:z1+1, x0:x1+1]
        square = (xx-cx)**2+(zz-cz)**2
        mask = square <= radius**2
        if not filled: mask &= square >= max(0, radius-thick)**2
        original = self.original[y, z0:z1+1, x0:x1+1]
        assert not np.any(mask & (original != AIR) & (original != mat)), '环体覆盖I19原块'
        self.cells[y, z0:z1+1, x0:x1+1][mask] = mat

    def tube(self, points, mat=PIPE, radius=1):
        for a, b in zip(points, points[1:]):
            assert sum(a[i] != b[i] for i in range(3)) <= 1
            self.box(tuple(min(a[i], b[i])-radius for i in range(3)),
                     tuple(max(a[i], b[i])+radius for i in range(3)), mat)

    def hall(self, lo, hi):
        x0, y0, z0 = lo; x1, y1, z1 = hi
        self.box((x0, 0, z0), (x1, 1, z1), STEEL)
        self.box(lo, hi, QSV, True)
        for y in (5, y1-4):
            self.box((x0, y, z0), (x1, y, z0), WHITE)
            self.box((x0, y, z1), (x1, y, z1), WHITE)
        for x in range(x0+4, x1-4, 11):
            for z in (z0, z1): self.box((x, 9, z), (x+5, min(16, y1-6), z), GLASS)
        for x in range(x0+2, x1, 12):
            self.box((x, 2, z0), (x+1, y1, z0+1), QSV)
            self.box((x, 2, z1-1), (x+1, y1, z1), QSV)

    def port(self, code, pos, face, purpose):
        self.box(pos, pos, PORT)
        self.ports.append({'id': code, 'pos': list(pos), 'face': face, 'purpose': purpose})


def build():
    before = json.loads(BASE.read_text(encoding='utf-8'))
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == 'd3ad9dce1bc5543c91beb88de82957dc05d0970d3699e0dc80d511dcb4c78bc7'
    a = Extension(before)
    # 原热室东侧保留四格宽连续操作路，新设备不堵原F1/F2。
    for lo, hi in [((191, 0, 0), (195, 0, 222)), ((191, 0, 0), (270, 0, 6)),
                   ((0, 0, 175), (270, 0, 183)), ((0, 0, 218), (270, 0, 222)),
                   ((0, 0, 175), (5, 0, 217)), ((266, 0, 0), (270, 0, 222))]:
        a.box(lo, hi, STEEL)
    a.paths += [{'name': '保留I19燃料接口操作通廊', 'min': [191, 1, 96], 'max': [194, 4, 155]},
                {'name': '两代机组南侧联合检修路', 'min': [6, 1, 178], 'max': [263, 4, 182]},
                {'name': 'QSV外侧操作道', 'min': [266, 1, 184], 'max': [270, 4, 222]}]

    # 新塔的实体池、通风支腿和双曲壳全部属于QSV第二冷却回路。
    cx, cz = 233, 50
    for y in (0, 1): a.ring(cx, cz, y, 37, 1, STEEL, True)
    a.ring(cx, cz, 2, 36, 3, WHITE)
    a.ring(cx, cz, 2, 32, 1, GLASS, True)
    for angle in range(0, 360, 20):
        t = math.radians(angle)
        x, z = round(cx+31*math.cos(t)), round(cz+31*math.sin(t))
        a.box((x-1, 3, z-1), (x+1, 13, z+1), QSV)
    for y in range(13, H):
        radius = math.sqrt(23**2+((y-99)/(3.8 if y <= 99 else 3.1))**2)
        a.ring(cx, cz, y, radius, 2.2, WHITE if y in (13, 14, 98, 99, 153, 154) else QSV)
    a.ring(cx, cz, 11, 32, 3, PIPE)
    a.ring(cx, cz, 6, 30, 2, VESSEL)
    a.tube([(233, 6, 21), (233, 6, 50), (233, 6, 79)])
    a.zones.append({'name': 'QSV第二回路敞口冷却塔', 'pos': [233, 154, 50]})

    # 圆顶二重屏蔽核岛，与前代方舱核岛形成可读的技术演进。
    for y in (0, 1): a.ring(234, 143, y, 33, 1, STEEL, True)
    for y in range(2, 78):
        a.ring(234, 143, y, 32, 3, QSV)
        a.ring(234, 143, y, 29, 2, STEEL)
        if y in (9, 10, 43, 44, 73, 74): a.ring(234, 143, y, 32.3, 2, WHITE)
    for y in range(78, 98):
        radius = math.sqrt(max(1, 32**2-((y-77)*1.55)**2))
        following = math.sqrt(max(1, 32**2-((y-76)*1.55)**2)) if y < 97 else 8
        a.ring(234, 143, y, radius, max(3.2, radius-following+2), QSV)
    a.ring(234, 143, 98, 8, 1, QSV, True)
    for y in range(5, 64): a.ring(234, 143, y, 13, 2, VESSEL)
    for y in (4, 64): a.ring(234, 143, y, 13, 1, VESSEL, True)
    a.box((232, 5, 141), (236, 62, 145), QSV)
    a.box((234, 32, 143), (234, 32, 143), CORE)
    for z in (124, 160):
        a.box((248, 2, z-3), (254, 40, z+3), VESSEL, True)
        a.tube([(251, 41, z), (234, 41, z), (234, 41, 131 if z == 124 else 155)])
    a.zones.append({'name': 'QSV圆顶屏蔽核岛及双列换热器', 'pos': [234, 98, 143]})

    # 燃料热室与泵房均有完整体积、实际内部设备和独立外侧操作位。
    a.hall((200, 2, 95), (219, 22, 111))
    a.box((196, 0, 90), (199, 0, 112), STEEL)
    for z in (99, 106):
        a.box((204, 2, z-1), (214, 10, z+1), VESSEL, True)
        a.box((201, 3, z), (207, 3, z), VESSEL)
    a.port('F3', (200, 3, 99), 'west', '浓缩燃料棒输入候选')
    a.port('F4', (200, 3, 106), 'west', '浓缩乏燃料棒输出候选')
    a.box((216, 6, 109), (224, 13, 122), QSV, True)
    a.tube([(211, 3, 103), (211, 7, 103), (222, 7, 103), (222, 7, 143)], VESSEL, 0)
    a.tube([(207, 3, 99), (211, 3, 99), (211, 3, 106), (207, 3, 106)], VESSEL, 0)
    a.box((221, 2, 105), (223, 5, 116), STEEL, True)
    a.hall((242, 2, 89), (265, 22, 105))
    for x in (248, 258):
        a.box((x-3, 2, 93), (x+3, 10, 101), VESSEL, True)
        a.box((x-1, 11, 95), (x+1, 13, 98), GEAR)
    for z in (93, 101): a.box((259, 3, z), (264, 3, z), PIPE)
    a.port('C3', (265, 3, 93), 'east', 'QSV崩坏冷却剂输入候选')
    a.port('C4', (265, 3, 101), 'east', 'QSV热崩坏冷却剂输出候选')
    a.zones += [{'name': 'QSV燃料热室', 'pos': [209, 23, 103]}, {'name': 'QSV泵房', 'pos': [253, 23, 97]}]

    # 两线错层绕行，分别到达塔底集水环、布水环和核岛内部换热器。
    a.tube([(252, 8, 97), (258, 8, 97), (258, 8, 124), (251, 8, 124)])
    a.tube([(258, 8, 97), (258, 8, 87), (233, 8, 87), (233, 6, 87), (233, 6, 79)])
    a.tube([(251, 13, 160), (263, 13, 160), (263, 13, 110), (243, 13, 110), (243, 13, 88), (233, 13, 88), (233, 11, 88), (233, 11, 81)])
    for z in (115, 136, 157): a.box((262, 2, z-1), (264, 11, z+1), QSV)
    for x in (238, 252): a.box((x, 2, 86), (x+1, 6, 88), QSV)
    for z in (96, 108): a.box((242, 2, z), (244, 11, z+1), QSV)

    # 后侧真实控制厅跨过整宽中线，留出室内仪控工位和检修走廊。
    a.hall((108, 2, 184), (171, 23, 222))
    for x in (119, 132, 145, 158):
        a.box((x, 2, 188), (x+8, 5, 191), PANEL, True)
        a.box((x, 2, 207), (x+8, 5, 210), PANEL, True)
        a.box((x, 2, 217), (x+8, 10, 219), VENT, True)
    a.box((112, 2, 184), (117, 7, 184), AIR)
    a.box((135, 3, 185), (135, 3, 191), PANEL)
    a.box((135, 3, 184), (135, 3, 184), CORE)
    a.box((172, 0, 198), (174, 1, 207), STEEL)
    a.box((171, 2, 198), (175, 12, 207), QSV, True)
    a.box((171, 2, 201), (175, 7, 204), AIR)
    a.zones.append({'name': '两代机组联合仪控厅・主控第136格', 'pos': [135, 24, 201]})

    # 新透平厅采用连续拱形薄屋面；完整内部透平与送出母线不靠接口柱表达。
    a.hall((175, 2, 184), (264, 42, 222))
    a.box((176, 42, 185), (263, 42, 221), AIR)
    for z in range(185, 222):
        roof = 42+round(6*math.sin(math.pi*(z-184)/38))
        a.box((175, roof-1, z), (264, roof, z), QSV)
        for x in (175, 264): a.box((x, 42, z), (x, roof, z), QSV)
    for x in (184, 204, 224, 244, 260):
        for z in (187, 219): a.box((x, 2, z), (x+1, 42, z+1), QSV)
        for z in range(187, 221):
            roof = 42+round(6*math.sin(math.pi*(z-184)/38))
            a.box((x, roof-3, z), (x+1, roof-2, z), WHITE)
    for x in (186, 208, 230):
        a.box((x-2, 2, 192), (x+18, 3, 215), STEEL)
        a.box((x, 4, 196), (x+15, 13, 210), VESSEL, True)
        a.box((x+2, 14, 198), (x+13, 16, 208), QSV, True)
        a.box((x+5, 7, 195), (x+9, 11, 195), GEAR)
        a.box((x-1, 4, 192), (x+16, 4, 193), GRATE)
    a.tube([(234, 22, 156), (234, 22, 179), (238, 22, 179), (238, 22, 202), (238, 17, 202)])
    a.tube([(243, 15, 202), (251, 15, 202), (251, 15, 153)])
    a.box((232, 0, 176), (236, 20, 177), QSV, True)
    a.box((237, 0, 176), (239, 20, 177), QSV, True)
    a.box((250, 0, 176), (252, 13, 177), QSV, True)
    # 蒸汽管廊在通道上方跨越，支撑不占声明净空。
    for z in (188, 198, 208, 216):
        a.box((259, 2, z-2), (264, 9, z+2), VESSEL, True)
        a.box((260, 3, z-1), (264, 6, z+1), PANEL)
        a.box((259, 2, z-2), (259, 8, z+2), VENT)
        a.port('E'+str(5+(z-188)//10 if z != 216 else 8), (264, 3, z), 'east', 'QSV电力送出候选分组')
    a.box((258, 3, 187), (258, 3, 219), PANEL)
    a.box((248, 3, 202), (263, 3, 202), PANEL)
    a.zones.append({'name': 'QSV三段透平与侧壁电力送出', 'pos': [218, 49, 203]})

    frozen = a.original != AIR
    assert np.array_equal(a.cells[frozen], a.original[frozen]), 'I19原块或状态改变'
    assert np.all(a.cells[20:, 46:55, 229:238] == AIR), 'QSV塔口误封闭'
    for path in a.paths:
        x0, y0, z0 = path['min']; x1, y1, z1 = path['max']
        assert np.all(a.cells[y0:y1+1, z0:z1+1, x0:x1+1] == AIR), path
    yy, zz, xx = np.nonzero(a.cells)
    blocks = [{'pos': [int(x), int(y), int(z)], 'state': STATES[int(a.cells[y, z, x])]} for y, z, x in zip(yy, zz, xx)]
    data = {'key': 'i20', 'name': NAME, 'title': '中型崩坏能反应堆', 'candidate_version': '双岛复合厂区扩建V1・待审',
            'size': [W, H, D], 'controller': [135, 3, 184], 'controller_face': 'north', 'ports': a.ports,
            'zones': a.zones, 'paths': a.paths, 'links': [], 'blocks': blocks, 'block_count': len(blocks),
            'description': '保留HBV单塔厂区，向东增加QSV敞口塔与圆顶核岛，向南增加联合仪控及三段透平厅。',
            'integration_revision': {'principle': '主控嵌真实联合仪控厅北墙；新燃料、冷却及电力接口分别嵌热室、泵房与透平送出设备。'},
            'controller_centering': {'center_column_1based': 136, 'center_x_0based': 135, 'summary': '整宽271，唯一中线第136格；旧I19主控保留为前阶段子机标记。'},
            'construction_notes': {'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'recommended_world_y': -60,
                                   'world_height_range': [-60, 94], 'orientation': 'X东/Y上/Z南，主控朝北；保留前阶段坐标原点。',
                                   'status': '待用户批准；累计五台明确批准后先实装2.9，2.9.2由负责人升级后核验。'}}
    components, count = label(a.cells != AIR)
    if count != 1:
        details = []
        for index in range(1, count+1):
            yy0, zz0, xx0 = np.nonzero(components == index)
            details.append({'count': len(xx0), 'min': [int(xx0.min()), int(yy0.min()), int(zz0.min())],
                            'max': [int(xx0.max()), int(yy0.max()), int(zz0.max())]})
        raise AssertionError(details)
    sizes = require(data)
    assert all(v >= n for v, n in zip(sizes['actual_xyz'], (270, 154, 222)))
    additions = int(np.count_nonzero((a.original == AIR) & (a.cells != AIR)))
    inheritance = {'source': str(BASE), 'source_sha256': hashlib.sha256(BASE.read_bytes()).hexdigest(),
                   'source_approval': 'I19为前阶段待审候选，不把继承当成用户批准', 'preserved_blocks': len(before['blocks']),
                   'added_blocks': additions, 'removed_blocks': 0, 'different_state_overwrites': 0,
                   'old_controller_retained': [95, 3, 20], 'original_origin_preserved': True}
    return data, {'size_check': sizes, 'components': count, 'tower_open': True, 'paths_clear': True,
                  'controller_centered': True, 'inheritance': inheritance}


if __name__ == '__main__':
    data, geometry = build()
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG/'geometry-preview.json').write_text(json.dumps(geometry, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'blocks': data['block_count'], **geometry}, ensure_ascii=False, indent=2))
