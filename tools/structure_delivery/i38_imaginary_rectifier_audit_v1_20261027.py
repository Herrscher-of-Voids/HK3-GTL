# -*- coding: utf-8 -*-
"""I38双极换流站实体核验：完整坐标、嵌入接口及IWV低阶严格比较。
变更记录 #1（2026-10-27）：新增独立候选审核，不改正式结构或实例。"""
import math

import numpy as np
from scipy import ndimage

import i38_imaginary_rectifier_geometry_v1_20261027 as geometry
from structure_size_baseline import baselines
from i38_voltage_progression_20261027 import progression


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES) + 1)
    assert np.all(counts[1:] > 0)
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda r: -r[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        positions = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(positions[0])); high.append(int(positions[-1]))
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size'] == [w, h, d]
    minimum = baselines()['I38']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    assert np.array_equal(cube, cube[:, :, ::-1]), '几何与材质不对称'
    labels, components = ndimage.label(occupied)
    assert components == 1, ('实体未连通', components)
    del labels, occupied
    assert counts[geometry.IDS[geometry.material.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.material.PORT]] == len(data['ports']) == 10
    assert palette[geometry.material.IWV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {geometry.material.IWV, geometry.material.PORT}
    directions = dict(north=(0, 0, -1), south=(0, 0, 1), west=(-1, 0, 0), east=(1, 0, 0))
    markers = []
    for item in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = item['pos']; dx, dy, dz = directions[item['face']]
        state = geometry.material.CONTROL if item['id'] == '主控' else geometry.material.PORT
        assert cube[y, z, x] == geometry.IDS[state]
        assert cube[y - dy, z - dz, x - dx]
        for k in range(1, 6):
            X, Y, Z = x + dx * k, y + dy * k, z + dz * k
            if 0 <= X < w and 0 <= Y < h and 0 <= Z < d:
                assert not cube[Y, Z, X], ('接口外侧净空', item)
        tangent = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if dx else ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
        assert all(cube[y + b, z + c, x + a] for a, b, c in tangent), ('接口周边断面', item)
        span = cube[y, z - 4:z + 5, x] if dx else cube[y, z, x - 4:x + 5]
        assert np.all(span), ('独立接口面板', item)
        markers.append(dict(id=item['id'], position=item['pos'], face=item['face'], outer_clear=5, inner_backed=True, flush_shell=True))
    assert data['controller'][0] == (w - 1) // 2
    for route in data['paths']:
        x, y, z = route['min']; X, Y, Z = route['max']
        assert not np.any(cube[y:Y + 1, z:Z + 1, x:X + 1])
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], zone
    assert -60 + h - 1 <= 236
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette), volume=math.prod(actual), height=h)
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), palette=palette, iwv_casing_count=palette[geometry.material.IWV],
        bounding_box_volume=metrics['volume'], height=h, baseline_check=dict(passed=True, baseline_wdh=minimum),
        bilateral_symmetry=dict(passed=True, axis=f'X={(w - 1) // 2}'), connectivity=dict(passed=True, components=1),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1), port_checks=markers,
        voltage_progression=progression(metrics),
        checks=['41种较低电压批准形态的实体数、材料数、包围盒及实际高度四项比较100%通过。',
            '全体六邻接单连通、左右几何和材质严格镜像；IWV主壳为最大单一材料。',
            '钻石主控居中，10接口嵌入真实控制室连续面，有背板及五格外侧净空。'],
        not_verified=['候选待负责人批准，未实装；batch-09现为I34/I35/I36，3/5。',
            '正式控制器、Pattern、HKE整流与结算、供能合同和游戏运行未在本轮验收。',
            '材料和研究完整生存获取链未验；不以HTML预览代替FCL/PC性能验收。'])
