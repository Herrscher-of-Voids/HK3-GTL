# -*- coding: utf-8 -*-
"""I19小型崩坏能反应堆：独立单机组厂区的建筑候选。

【文件职责】以当前完整立方体资源生成同源蓝图、NBT、Sponge、纹理预览与外部接口记录。
所有输出限定在新候选及任务日志；不注册机器或配方，不向任何游戏实例写入。
【变更记录 #1】2026-10-23 16:18:53（建筑候选，不增加模组修订）
删除：无。新增：单塔、厚壁核岛、长跨透平厅、泵房、燃料热室及置中主控的原创布局。
修改：不复用被否决旧稿的厂区布局；以现存HBV机壳承担主体配色。
用途：交付下一台待审结构，并保留等待负责人升级2.9.2后的部署禁令。
【变更记录 #2】2026-10-23 16:25:25（候选静态复核）
删除：管廊共用末端。新增：两条独立冷却接点、端口后方输送/母线实体及透平蒸汽接点。
修改：主控和燃料/冷却接口降至Y3，便于地面操作；用途：让外部位置对应内部设备连接。
【变更记录 #3】2026-10-23 16:30:12（独立几何复核修正）
删除：透平屋顶无用途的实心夹层和高位冷却干线的穿塔捷径。
新增：泵组立管、穿屏蔽层换热接点、热室至堆体的封闭转运及对应支撑。
修改：高位主管绕塔，指定支线接布水环，透平屋面保留两格壳厚；用途：端点与建筑用途对应。
【变更记录 #4】2026-10-23 16:33:05（管廊支撑复核）
删除：无。新增：两段南北冷却主管的中途承重支架。
修改：侧置立柱避开检修轴，横梁贴合管底；用途：消除长距离无支撑跨段，不改变工艺分区。
"""
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
import subprocess
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label

from build_redesign69 import export, render
from build_i09_i13_redesign_v6 import lodestone_export
from build_i18_hbv_fuel_rod_encapsulation_v1 import stage_evidence
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require

OUT = ROOT / 'deliveries/I19_小型崩坏能反应堆_单塔蓝湾独立候选_V3_20261023'
LOG = ROOT / 'logs/i19-next-candidate-20261023'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
W, H, D = 191, 123, 175
NAME = 'i19-hbv-coastal-single-unit-v3'
STATES = ['minecraft:air', 'hk3gtl:voltage_machine_casing_hbv', 'gtceu:clean_machine_casing',
          'gtceu:steel_machine_casing', 'gtceu:stainless_steel_turbine_casing', 'gtceu:laminated_glass',
          'gtceu:titanium_pipe_casing', 'gtceu:assembly_line_grating', 'gtceu:computer_heat_vent',
          'gtceu:advanced_computer_casing', 'gtceu:titanium_gearbox',
          'hk3gtl:industrial_port_casing', 'minecraft:diamond_block']
AIR, HBV, WHITE, STEEL, VESSEL, GLASS, PIPE, GRATE, VENT, PANEL, GEAR, PORT, CORE = range(len(STATES))
ROLES = ['空气', 'HBV蓝色主壳：冷却塔、核岛围护、厂房承重与屋脊', '设备腰线、塔口和检修带',
         '设备基础、道路与屏蔽内衬', '透平壳、换热器、泵壳与母线舱', '观察窗、采光带及封闭静态冷却池',
         '完整方块冷却/蒸汽管廊', '检修平台与透平轨道', '通风百叶与散热面',
         '仪控工位及送出设备', '泵组和传动节点', '工业接口位置标记，无实际仓室能力',
         '主控或堆芯位置标记，不代表真实控制器']


class Station:
    """紧凑体素数组保留空气；所有构件逐坐标落盘。"""
    def __init__(self):
        self.cells = np.zeros((H, D, W), dtype=np.uint8)
        self.ports = []
        self.zones = []
        self.paths = []

    def box(self, lo, hi, material, shell=False):
        x0, y0, z0 = map(int, lo)
        x1, y1, z1 = map(int, hi)
        assert 0 <= x0 <= x1 < W and 0 <= y0 <= y1 < H and 0 <= z0 <= z1 < D, (lo, hi)
        if shell:
            for y in (y0, y1): self.box((x0, y, z0), (x1, y, z1), material)
            for x in (x0, x1): self.box((x, y0, z0), (x, y1, z1), material)
            for z in (z0, z1): self.box((x0, y0, z), (x1, y1, z), material)
        else:
            self.cells[y0:y1+1, z0:z1+1, x0:x1+1] = material

    def ring(self, cx, cz, y, radius, thickness, material, filled=False):
        r = math.ceil(radius)
        x0, x1 = max(0, cx-r), min(W-1, cx+r)
        z0, z1 = max(0, cz-r), min(D-1, cz+r)
        zz, xx = np.ogrid[z0:z1+1, x0:x1+1]
        rr = (xx-cx)**2+(zz-cz)**2
        mask = rr <= radius**2
        if not filled: mask &= rr >= max(0, radius-thickness)**2
        self.cells[y, z0:z1+1, x0:x1+1][mask] = material

    def tube(self, points, material=PIPE, radius=1):
        for a, b in zip(points, points[1:]):
            assert sum(a[i] != b[i] for i in range(3)) <= 1
            self.box(tuple(min(a[i], b[i])-radius for i in range(3)),
                     tuple(max(a[i], b[i])+radius for i in range(3)), material)

    def hall(self, lo, hi):
        x0, y0, z0 = lo; x1, y1, z1 = hi
        self.box((x0, 0, z0), (x1, 1, z1), STEEL)
        self.box(lo, hi, HBV, True)
        for y in (4, y1-5):
            self.box((x0, y, z0), (x1, y, z0), WHITE)
            self.box((x0, y, z1), (x1, y, z1), WHITE)
            self.box((x0, y, z0), (x0, y, z1), WHITE)
            self.box((x1, y, z0), (x1, y, z1), WHITE)
        for x in range(x0+4, x1-3, 10):
            self.box((x, 9, z0), (x+5, min(15, y1-7), z0), GLASS)
            self.box((x, 9, z1), (x+5, min(15, y1-7), z1), GLASS)
        for x in range(x0, x1+1, 10):
            self.box((x, 2, z0), (min(x+1, x1), y1, z0+1), HBV)
            self.box((x, 2, z1-1), (min(x+1, x1), y1, z1), HBV)
            self.box((x, y1-1, z0), (min(x+1, x1), y1, z1), WHITE)
        self.zones.append({'name': '透平与主仪控厅' if y1 > 25 else '泵房与水处理',
                           'pos': [(x0+x1)//2, y1, (z0+z1)//2]})

    def port(self, code, pos, face, purpose):
        x, y, z = pos
        self.cells[y, z, x] = PORT
        self.ports.append({'id': code, 'pos': list(pos), 'face': face, 'purpose': purpose})


def build():
    a = Station()
    # 连续厂区道路连接真实设备门区；不以整块空白地板填满占地。
    for lo, hi in [((0, 0, 0), (190, 0, 6)), ((0, 0, 0), (5, 0, 174)),
                   ((185, 0, 0), (190, 0, 174)), ((0, 0, 169), (190, 0, 174)),
                   ((0, 0, 14), (190, 0, 19)), ((61, 0, 7), (69, 0, 95)),
                   ((94, 0, 75), (104, 0, 174)), ((6, 0, 66), (103, 0, 75))]:
        a.box(lo, hi, STEEL)
    a.box((0, 0, 17), (190, 0, 17), WHITE)
    a.paths = [{'name': '厂前连续操作道', 'min': [0, 1, 14], 'max': [190, 4, 19]},
               {'name': '核岛与冷却塔检修轴', 'min': [97, 1, 76], 'max': [101, 4, 169]},
               {'name': '泵房到换热区道路', 'min': [62, 1, 20], 'max': [67, 4, 74]}]

    # 单座大尺度双曲面冷却塔。敞口、透空下部、集水池、布水环均为独立构件。
    cx, cz = 49, 122
    for y in (0, 1): a.ring(cx, cz, y, 47, 1, STEEL, True)
    a.ring(cx, cz, 2, 46, 3, WHITE)
    a.ring(cx, cz, 2, 42, 1, GLASS, True)
    for angle in range(0, 360, 20):
        t = math.radians(angle)
        x, z = round(cx+41*math.cos(t)), round(cz+41*math.sin(t))
        a.box((x-1, 3, z-1), (x+1, 12, z+1), HBV)
    for y in range(12, 123):
        # 连续半径从42收束到29，再向顶端张开为36；相邻层壳体重叠。
        radius = math.sqrt(29**2 + ((y-78)/2.16)**2) if y <= 78 else math.sqrt(29**2 + ((y-78)/2.06)**2)
        material = WHITE if y in (12, 13, 63, 64, 121, 122) else HBV
        a.ring(cx, cz, y, radius, 2.3, material)
    a.ring(cx, cz, 11, 41, 3, PIPE)
    a.ring(cx, cz, 6, 39, 2, VESSEL)
    for z in (105, 139):
        a.tube([(49, 6, z), (49, 6, 122)], PIPE)
    a.zones.append({'name': '敞口双曲面冷却塔', 'pos': [49, 123, 122]})

    # 透平厅跨过整宽中线：主控直接落在有内部仪控工位的真实墙上。
    a.hall((72, 2, 20), (181, 31, 72))
    a.box((73, 31, 21), (180, 31, 71), AIR)
    for x in range(73, 181):
        for z in range(21, 72):
            top = 31+max(0, 5-abs(z-46)//5)
            material = HBV if (x-72)%20 < 17 else GLASS
            a.box((x, top-1, z), (x, top, z), material)
    for z in range(21, 72):
        top = 31+max(0, 5-abs(z-46)//5)
        for x in (72, 181): a.box((x, 31, z), (x, top, z), HBV)
    for z in (32, 59):
        a.box((79, 2, z-7), (175, 3, z+7), STEEL)
        a.box((79, 4, z-7), (175, 4, z-6), GRATE)
        a.box((79, 4, z+6), (175, 4, z+7), GRATE)
        for x in (89, 109, 129, 149):
            a.box((x, 4, z-4), (x+15, 12, z+4), VESSEL, True)
            a.box((x+1, 12, z-3), (x+14, 14, z+3), HBV, True)
            a.box((x+6, 6, z-5), (x+8, 10, z-5), GEAR)
        a.tube([(88, 15, z), (165, 15, z), (165, 15, 80)], PIPE)
    for x in (82, 106, 130, 154, 176):
        for z in (23, 69): a.box((x, 2, z), (x+1, 27, z+1), HBV)
        a.box((x, 27, 23), (x+1, 28, 70), WHITE)
    for x in range(86, 106, 4):
        a.box((x, 2, 23), (x+2, 5, 25), PANEL)
    a.box((92, 3, 20), (98, 7, 20), HBV)
    a.box((95, 3, 21), (95, 3, 25), PANEL)
    a.box((95, 3, 20), (95, 3, 20), CORE)
    a.box((74, 2, 20), (79, 7, 20), AIR)

    # 厚壁方舱核岛及内部反应器：四边屏蔽墙与阶梯顶盖形成第二主形。
    a.box((108, 0, 94), (172, 1, 159), STEEL)
    for inset, mat in ((0, HBV), (1, HBV), (2, STEEL)):
        a.box((108+inset, 2, 94+inset), (172-inset, 52, 159-inset), mat, True)
    for y in (9, 33, 49):
        a.box((108, y, 94), (172, y+1, 95), WHITE)
        a.box((108, y, 158), (172, y+1, 159), WHITE)
        a.box((108, y, 94), (109, y+1, 159), WHITE)
        a.box((171, y, 94), (172, y+1, 159), WHITE)
    for x in range(111, 172, 12):
        a.box((x, 2, 92), (x+2, 51, 94), HBV)
        a.box((x, 2, 159), (x+2, 51, 161), HBV)
    for inset in range(7):
        a.box((110+inset, 53+inset, 96+inset), (170-inset, 53+inset, 157-inset), HBV)
    for z in (108, 140):
        a.box((117, 60, z), (163, 61, z+2), WHITE)
        for x in range(120, 163, 8): a.box((x, 60, z-3), (x+3, 63, z-1), VENT)
    for y in range(5, 43): a.ring(140, 127, y, 15, 2, VESSEL if y%10 else HBV)
    for y in (4, 43): a.ring(140, 127, y, 15, 1, VESSEL, True)
    a.box((139, 5, 126), (141, 42, 128), HBV)
    a.box((140, 24, 127), (140, 24, 127), CORE)
    for x in (118, 162):
        a.box((x-2, 2, 108), (x+2, 34, 112), VESSEL, True)
        a.tube([(x, 35, 110), (140, 35, 110), (140, 35, 113)])
    a.zones.append({'name': '厚壁屏蔽核岛', 'pos': [140, 65, 127]})

    # 独立燃料热室连到核岛侧壁；外侧墙同时承担真实燃料接口载体。
    a.hall((174, 2, 96), (190, 23, 155))
    a.zones[-1]['name'] = '燃料转运热室'
    a.box((171, 6, 119), (176, 13, 132), HBV, True)
    a.box((177, 2, 103), (187, 3, 148), STEEL)
    for z in (108, 122, 139):
        a.box((178, 4, z), (185, 13, z+5), VESSEL, True)
        a.box((180, 14, z), (183, 15, z+5), HBV)
    for z in (108, 139): a.box((185, 3, z), (189, 3, z), VESSEL)
    a.box((183, 3, 108), (185, 3, 139), GRATE)
    a.tube([(183, 3, 125), (183, 7, 125), (162, 7, 125), (162, 7, 127), (155, 7, 127)], VESSEL, 0)
    a.port('F1', (190, 3, 108), 'east', '普通燃料棒输入候选')
    a.port('F2', (190, 3, 139), 'east', '乏燃料棒输出候选')

    # 前左泵房、两条闭合冷却干线及侧旁水处理池。
    a.hall((8, 2, 26), (56, 20, 62))
    a.box((7, 0, 26), (57, 1, 63), STEEL)
    for x in (18, 35, 48):
        a.box((x-3, 2, 35), (x+3, 9, 55), VESSEL, True)
        a.box((x-1, 10, 40), (x+1, 12, 43), GEAR)
    a.box((8, 0, 64), (56, 1, 73), STEEL)
    a.box((9, 2, 65), (55, 2, 71), GLASS)
    for x in (9, 23, 38, 55): a.box((x, 2, 64), (x, 3, 72), WHITE)
    for z in (37, 53): a.box((9, 3, z), (15, 3, z), PIPE)
    a.port('C1', (8, 3, 37), 'west', '崩坏冷却剂输入候选')
    a.port('C2', (8, 3, 53), 'west', '热崩坏冷却剂输出候选')
    for x, z in ((36, 82), (45, 73)):
        nx, end_z = (95, 119) if x == 36 else (102, 138)
        level, tower_z = (8, 108) if x == 36 else (13, 84)
        a.tube([(x, 8, 55), (x, level, 55), (x, level, z), (nx, level, z), (nx, level, end_z), (118, level, end_z), (118, level, 112)])
        a.tube([(x, level, z), (x, level, tower_z), (49, level, tower_z)])
        if x == 45: a.tube([(49, 13, 84), (49, 11, 84), (49, 11, 82)])
        for sx in range(x+8, 94, 14):
            if x == 45 and 60 <= sx <= 70: continue
            a.box((sx, 0, z-2), (sx+1, level-2, z+2), HBV)
            a.box((sx, level-2, z-2), (sx+1, level-2, z+2), WHITE)
    for z in (100, 116):
        a.box((94, 0, z-1), (96, 5, z+1), HBV)
        a.box((94, 6, z-1), (96, 6, z+1), WHITE)
    for z in (93, 115, 137):
        a.box((103, 0, z-1), (104, 10, z+1), HBV)
        a.box((101, 11, z-1), (104, 11, z+1), WHITE)
    for x in (120, 158):
        a.tube([(x, 18, 95), (x, 18, 79), (x, 18, 70)])
        a.box((x-2, 0, 77), (x+2, 16, 81), HBV, True)
    a.tube([(120, 18, 70), (120, 18, 59), (120, 15, 59)])
    a.tube([(158, 18, 70), (158, 18, 32), (158, 15, 32)])
    a.tube([(120, 18, 95), (120, 18, 110)])
    a.tube([(158, 18, 95), (158, 18, 110), (160, 18, 110)])
    a.zones.append({'name': '闭环冷却干线', 'pos': [80, 10, 87]})

    # 送出设备是有体积和散热面的变电舱，接口不由无用途的柱子托举。
    a.box((108, 0, 7), (181, 1, 13), STEEL)
    for n, x in enumerate((116, 134, 152, 170), 1):
        a.box((x-4, 2, 8), (x+4, 7, 12), VESSEL, True)
        a.box((x-3, 3, 8), (x+3, 6, 8), PANEL)
        a.box((x-4, 4, 9), (x-4, 6, 11), VENT)
        a.box((x+4, 4, 9), (x+4, 6, 11), VENT)
        a.box((x-1, 3, 9), (x+1, 6, 11), PANEL)
        a.port('E'+str(n), (x, 4, 8), 'north', '电力送出候选分组'+str(n))
        a.tube([(x, 3, 12), (x, 3, 13), (x, 0, 13), (x, 0, 20), (x, 3, 20)], VESSEL, 0)
    a.zones.append({'name': '电力送出区', 'pos': [145, 8, 10]})

    # 边界由道路、热室及实体冷却塔共同形成，通行净空不额外改造主体。
    yy, zz, xx = np.nonzero(a.cells)
    blocks = [{'pos': [int(x), int(y), int(z)], 'state': STATES[int(a.cells[y, z, x])]}
              for y, z, x in zip(yy, zz, xx)]
    data = {'key': 'i19', 'name': NAME, 'title': '小型崩坏能反应堆', 'candidate_version': '独立厂区V3・单塔蓝湾',
            'size': [W, H, D], 'controller': [95, 3, 20], 'ports': a.ports, 'zones': a.zones,
            'paths': a.paths, 'links': [], 'blocks': blocks, 'block_count': len(blocks),
            'description': '单座敞口双曲面冷却塔与厚壁核岛构成双主形，长跨透平厅、泵房和侧置燃料热室组成完整单机组厂区。',
            'integration_revision': {'principle': '主控直接嵌入连续透平厅北墙，对应内部仪控工位；燃料、冷却和电力接口分别嵌入热室、泵房和送出舱。'},
            'controller_centering': {'center_column_1based': 96, 'center_x_0based': 95,
                                    'summary': '候选宽191格，主控位于唯一中线第96格；较旧目标190格增加1格，不将尺寸调整记作用户批准。'},
            'construction_notes': {'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'recommended_world_y': -60,
                                   'world_height_range': [-60, 62], 'orientation': 'X东、Y上、Z南；主控朝北。',
                                   'status': '待外观审批；本轮禁止部署2.9，等待负责人更新2.9.2后再处理。'}}
    assert a.cells[3, 20, 95] == CORE
    delta = {'north': (0, 0, -1), 'east': (1, 0, 0), 'west': (-1, 0, 0)}
    for p in a.ports+[{'pos': data['controller'], 'face': 'north'}]:
        x, y, z = p['pos']; dx, dy, dz = delta[p['face']]
        nx, ny, nz = x+dx, y+dy, z+dz
        assert not (0 <= nx < W and 0 <= ny < H and 0 <= nz < D) or a.cells[ny, nz, nx] == AIR, p
        assert a.cells[y-dy, z-dz, x-dx] != AIR, ('接口背接为空', p)
    assert np.all(a.cells[15:123, 117:128, 44:55] == AIR), '冷却塔喉口误封闭'
    sizes = require(data)
    assert all(v >= n for v, n in zip(sizes['actual_xyz'], (190, 122, 174)))
    components, count = label(a.cells != AIR)
    component_sizes = np.bincount(components.ravel())[1:]
    del components
    # 分离构件拒绝静默通过；此处仅作为建筑连接事实，不能当成功能验收。
    assert count == 1, sorted(component_sizes.tolist(), reverse=True)[:20]
    for route in a.paths:
        x0, y0, z0 = route['min']; x1, y1, z1 = route['max']
        assert np.all(a.cells[y0:y1+1, z0:z1+1, x0:x1+1] == AIR), route['name']
    return data, {'components': count, 'size_check': sizes, 'tower_open': True,
                  'controller_centered': True, 'port_faces_clear': True, 'paths_clear': True}


def plan_image(data, materials):
    colors = {}
    for m in materials:
        import io
        pic = Image.open(io.BytesIO(base64.b64decode(m['faces']['up'].split(',')[1]))).convert('RGB')
        colors[m['state']] = tuple(np.array(pic).mean(axis=(0, 1)).astype(int))
    image = Image.new('RGB', (W*6, D*6), '#132033')
    draw = ImageDraw.Draw(image)
    for b in sorted(data['blocks'], key=lambda b: b['pos'][1]):
        x, y, z = b['pos']; draw.rectangle((x*6, z*6, x*6+5, z*6+5), fill=colors[b['state']])
    draw.line((95*6+3, 0, 95*6+3, D*6), fill='#ffdf61', width=2)
    x, y, z = data['controller']; draw.ellipse((x*6-6, z*6-6, x*6+12, z*6+12), outline='#fff2a3', width=3)
    image.save(OUT / '俯视布局.png')


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    folder = OUT / 'i19'; folder.mkdir(exist_ok=True)
    data, geometry = build()
    print('几何完成', len(data['blocks']), flush=True)
    resources = Resources(INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(s) for s in sorted({b['state'] for b in data['blocks']})]
        resource_sources = dict(resources.sources)
    finally: resources.close()
    assert all(m['complete_cube'] for m in materials)
    states, groups, hashes = export(data, folder)
    print('NBT/Sponge回读完成', flush=True)
    counts = collections.Counter(b['state'] for b in data['blocks'])
    ordinary = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in (STATES[PORT], STATES[CORE]))
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
    audit = {'time': now, 'palette': dict(counts), 'hashes': hashes, 'geometry': geometry,
             'namespace_counts': dict(ordinary), 'namespace_percent': {k: round(100*v/sum(ordinary.values()), 2) for k, v in ordinary.items()},
             'markers': {STATES[PORT]: counts[STATES[PORT]], STATES[CORE]: counts[STATES[CORE]]},
             'target_voltage': 'HBV（已确认映射；运行能力与生存首建尚未验收）',
             'minimum_executable_recipe_voltage': None, 'approval': '待用户审批', 'deployment_allowed': False,
             'resource_environment': '增强版2.9既有资源只读，2.9.2尚待负责人升级后重新核验',
             'browser_review': {'verified': False, 'blocked_action': '浏览器自动打开本地file三维页',
                                'reason': '浏览器安全策略拒绝file协议，只允许http/https；未使用替代浏览器或其他绕过方式。'},
             'checks': ['真实模型全部完整立方体，真实纹理无原版代色', 'NBT与Sponge包括空气的同源逐格回读',
                        '实际尺寸覆盖69总表及190×122×174旧目标', '主控第96格并嵌透平厅实墙，无独立面板',
                        '八个接口均嵌对应设备，外向相邻位置留空', '单个六面连通结构，三条维护通道净空通过',
                        '冷却塔喉部和塔顶保持空气，未以盖板封口'],
             'not_verified': ['待外观审批', '2.9.2资源与最终配方需升级后重核', '全部建材祖先链、研究与HBV生存首建未实机验收',
                              'I19独立控制器、Pattern、真实仓室结算、热管理及发电生命周期未接入', '游戏成型、运行及多人验收未执行',
                              '浏览器自动检查本地file三维页被安全策略阻止，交互未实测']}
    evidence = stage_evidence()
    evidence['current_boundary'] = audit['resource_environment']
    evidence['ordinary_materials'] = [{'state': s, 'count': counts[s], 'role': ROLES[STATES.index(s)],
                                       'complete_cube': True, 'stage': 'HBV目标；完整生存祖先链待验收',
                                       'effective_recipe_evidence': evidence['materials'].get(s)} for s in states if s not in (STATES[PORT], STATES[CORE])]
    (OUT / '材料阶段依据.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '资源来源.json').write_text(json.dumps(resource_sources, ensure_ascii=False, indent=2), encoding='utf-8')
    meta = {k: v for k, v in data.items() if k != 'blocks'}
    record = {'data': meta, 'audit': audit}
    (folder / '设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    compressed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder / 'data.js').write_text('/* I19独立候选；同源逐格数据，不代表正式机器。 */\nwindow.HK3_PAYLOAD='+json.dumps(compressed)+';', encoding='utf-8')
    (folder / 'blueprint.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    render(data, materials, folder)
    print('真实纹理等轴图完成', flush=True)
    plan_image(data, materials)
    cut = {**data, 'blocks': [b for b in data['blocks'] if b['pos'][1] <= 18 and not
           (b['pos'][1] > 2 and (b['pos'][2] in (20, 72, 94, 95, 96, 157, 158, 159) or b['pos'][0] in (72, 108, 109, 110, 170, 171, 172, 181)))]}
    temp = LOG / 'cut-render'; temp.mkdir(exist_ok=True)
    render(cut, materials, temp); shutil.copy2(temp / '等轴预览.png', OUT / '内部剖切.png')
    # 通过技能的既有适配器再导出并逐格校对，仍限定候选目录。
    hashes['nbt'] = lodestone_export(data, folder, LOG)
    record['audit']['hashes'] = hashes
    (folder / '设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    payload['audit'] = record['audit']
    compressed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder / 'data.js').write_text('/* I19独立候选；同源逐格数据，不代表正式机器。 */\nwindow.HK3_PAYLOAD='+json.dumps(compressed)+';', encoding='utf-8')
    subprocess.run(['node', str(ROOT / 'tools/structure_delivery/package_integration_review.mjs'), str(OUT), '独立厂区V3・待审'], check=True)
    page = folder / '三维评审.html'
    text = page.read_text(encoding='utf-8').replace('全部21形态', 'I19交付总览').replace('href="../index.html#i19"', 'href="../index.html"')
    page.write_text(text, encoding='utf-8')
    manifest = {**meta, 'hashes': hashes, 'approval': '待用户审批', 'deployment_allowed': False,
                'hold': '先不实装2.9；等负责人更新2.9.2后再处理', 'generated_at': now, 'verification': geometry}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'verification.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = ''.join('<tr><td><code>'+html.escape(s)+'</code></td><td>'+f'{counts[s]:,}'+'</td><td>'+ROLES[STATES.index(s)]+'</td></tr>' for s in states)
    index = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I19 · 小型崩坏能反应堆 · 单塔蓝湾</title>
<style>body{{margin:0;background:#101c2c;color:#e6eff5;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1280px;margin:auto;padding:30px}}header{{padding:25px;background:#173d66;border-left:5px solid #8bc4fa}}h1{{margin:0}}a{{color:#aad8ff}}img{{max-width:100%}}.facts{{display:flex;gap:20px;flex-wrap:wrap}}.notice{{padding:15px;background:#3e3726;border-left:4px solid #dbc57f}}iframe{{width:100%;height:850px;border:1px solid #52718b}}table{{border-collapse:collapse;width:100%}}td,th{{padding:9px;text-align:left;border-bottom:1px solid #344b61}}code{{overflow-wrap:anywhere}}small{{color:#a5b7ca}}</style>
<main><header><small>HK3GTL / I19 / 独立建筑候选 V3</small><h1>小型崩坏能反应堆 · 单塔蓝湾</h1><p>敞口冷却塔、厚壁核岛、长跨透平厅与完整辅助设施。主控和接口从设备本体中长出来。</p></header>
<div class="facts"><p>宽×深×高 <b>191×175×123</b></p><p>实体 <b>{len(data['blocks']):,}</b></p><p>HBV主壳 <b>{counts[STATES[HBV]]:,}</b></p><p>接口标记 <b>8</b></p></div>
<p class="notice"><b>本轮只交付待审候选，先不实装到增强版2.9。</b>等负责人自行更新2.9.2后，再核对资源和正式接入。当前资源来自既有2.9只读调查；没有宣称已核验2.9.2。</p>
<p><a href="i19/三维评审.html">打开三维评审</a> · <a href="i19/三维评审.html?view=controller">定位居中主控</a> · <a href="i19/{NAME}.nbt">NBT</a> · <a href="i19/{NAME}.schem">Schematic</a> · <a href="../{OUT.name}.zip">完整ZIP</a></p>
<p>主控 [95,3,20]，第96格，朝北；直接嵌入透平厅北墙，对应内部仪控工位，可从地面操作。191格比旧目标190格增加1格，保证唯一中线。本候选独立新构图，未批准；旧稿及批准归档完整保留。</p>
<img src="i19/等轴预览.png" alt="真实方块纹理的等轴预览"><iframe src="i19/三维评审.html" title="I19独立三维评审"></iframe>
<h2>从工艺组织厂区</h2><p>后左冷却塔保留敞口、透空支腿、环形集水池和布水环。后右核岛采用三层围护和阶梯屏蔽顶盖；前部透平厅内含两列透平设备与检修轨道。前左泵房通过两条全方块管廊接到塔底与核岛；右侧燃料转运热室连接核岛，前沿变电舱负责电力送出。管廊和厂区道路具有真实端点。</p>
<p>F1/F2嵌燃料热室，C1/C2嵌泵房，E1–E4嵌送出设备。所有接口仍是无功能的位置标记，钻石块仅标主控和堆芯；没有独立控制面板、托接口异形柱、建筑内文字或非完整方块。</p>
<p><a href="俯视布局.png">厂区俯视与宽度中线</a> · <a href="内部剖切.png">内部设备剖切图</a> · <a href="i19/设计与检查.json">全部接口坐标与检查</a></p>
<h2>电压与材料边界</h2><p>HBV沿用已确认的能源映射；I19发电合同仍为provisional，没有独立可执行反应堆配方可用于宣称首建闭环，每台15条独立燃料工艺仍待实现。本轮不修改合同或新增配方。HBV主材首制有源码路线，GT辅材复用既有有效产出快照，但全部祖先链与生存研究仍待验收。</p>
<p>普通建材：{html.escape('；'.join(k+' '+str(v)+'（'+str(audit['namespace_percent'][k])+'%）' for k,v in ordinary.items()))}。原版普通建材为零；指定两类标记另计。<a href="材料阶段依据.json">逐材料依据</a> · <a href="资源来源.json">实际纹理和模型来源</a></p>
<table><tr><th>实际方块</th><th>用量</th><th>用途</th></tr>{rows}</table>
<h2>交付状态</h2><p>已检查完整立方体模型、实际三轴尺寸、逐格导出、主控中线、接口外向净空、维护道、六面连接和塔口空气。外观审阅、正式Pattern、仓室结算、热管理、发电与游戏运行分别验收，不把结构导出计作能源系统完成。</p>
<p>浏览器自动检查本地三维页被安全策略拒绝（只允许HTTP/HTTPS，禁止file协议），未改用其他方式绕过；静态纹理图可直接查看，三维交互未自动实测。</p><p>原点/粘贴锚点[0,0,0]，Offset为零；建议底部世界Y=-60，最高Y=62。结构文件仅留在项目交付目录。</p><small>变更记录 #1：{now}。新增独立候选及暂停部署说明；未修改正式模组、配方或游戏实例。</small></main></html>'''
    (OUT / 'index.html').write_text(index, encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    shutil.copy2(__file__, scripts / Path(__file__).name)
    shutil.copy2(ROOT / 'tools/structure_delivery/package_integration_review.mjs', scripts / 'package_integration_review.mjs')
    shutil.copy2(Path.home() / '.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE', OUT / 'Three许可.txt')
    print(json.dumps({'output': str(OUT), 'blocks': len(data['blocks']), 'hashes': hashes, 'geometry': geometry}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
