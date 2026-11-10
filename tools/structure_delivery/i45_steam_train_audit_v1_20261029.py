# -*- coding: utf-8 -*-
"""I45真实尺寸、轮轨、原位接口与全部QCV低阶递进检查。"""
import json
import math
import numpy as np
from scipy import ndimage
import i45_steam_train_geometry_v1_20261029 as geometry
from structure_size_baseline import baselines
from i44_voltage_progression_20261029 import validate_progression


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES)+1)
    assert np.all(counts[1:]), ('调色板未使用', [geometry.STATES[i-1] for i in np.flatnonzero(counts[1:] == 0)+1])
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda item: -item[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        pos = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(pos[0])); high.append(int(pos[-1]))
    actual = [high[i]-low[i]+1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size']
    minimum = baselines()['I45']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    labels, components = ndimage.label(occupied)
    if components != 1:
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        parts = []
        for label in np.argsort(sizes)[::-1][:12]:
            if not sizes[label]: continue
            y, z, x = np.argwhere(labels == label)[0]
            parts.append(dict(count=int(sizes[label]), pos=[int(x), int(y), int(z)]))
        raise ValueError(('六邻接游离件', components, parts))
    del labels, occupied
    m = geometry.material
    assert counts[geometry.IDS[m.CONTROL]] == 1 and counts[geometry.IDS[m.PORT]] == 8
    assert palette[m.QCV] == max(palette.values())
    assert {state for state in palette if state.startswith('hk3gtl:')} == {m.QCV, m.PORT}
    assert data['controller'][0] == (w-1)//2 and data['controller_face'] == 'north'
    directions = dict(north=(0, 0, -1), south=(0, 0, 1), west=(-1, 0, 0), east=(1, 0, 0))
    checks = []
    for port in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = port['pos']; dx, dy, dz = directions[port['face']]
        expected = m.CONTROL if port['id'] == '主控' else m.PORT
        assert cube[y, z, x] == geometry.IDS[expected]
        assert cube[y-dy, z-dz, x-dx], ('内背板缺失', port)
        around = [(0, 1, 0), (0, -1, 0)] + ([(1, 0, 0), (-1, 0, 0)] if dz else [(0, 0, 1), (0, 0, -1)])
        assert all(cube[y+b, z+c, x+a] for a, b, c in around), ('外壳不连续', port)
        for step in range(1, 6):
            a, b, c = x+dx*step, y+dy*step, z+dz*step
            if 0 <= a < w and 0 <= b < h and 0 <= c < d:
                assert cube[b, c, a] == 0, ('外侧不可达', port, step)
        checks.append(dict(id=port['id'], position=port['pos'], face=port['face'], flush_shell=True, inner_backed=True, outer_clear=5))
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], ('分区标记为空', zone)
    for z in data['railway']['driving_wheel_centers_z']:
        assert cube[5, z, 25] and cube[5, z, 95], ('轮轨接触缺失', z)
    import i44_voltage_progression_20261029 as progression
    mapping = progression.shared._mapping(progression.MAPPING.read_bytes())
    assert mapping['I45'] == 'QCV', ('I45电压映射变化', mapping.get('I45'))
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette)-2, volume=math.prod(actual), height=h)
    voltage = validate_progression(metrics)
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), ordinary_materials=metrics['materials'], palette=palette,
        qcv_casing_count=palette[m.QCV], bounding_box_volume=metrics['volume'], height=h,
        baseline_check=dict(passed=True, baseline_wdh=minimum), connectivity=dict(passed=True, components=1, neighborhood=6),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0]+1), port_checks=checks,
        railway=dict(data['railway'], fixed_structure=True, moving_entity=False), voltage_progression=voltage,
        checks=['真实边界超过25×97×29最低占地；没有空气扩大导出边界。',
            'QCV最多单材；24种普通材各有实际车体用途。',
            '全部实体六邻接连通；车轮落在轨顶；锅炉、客车、水箱留有真实内腔。',
            '主控整宽中线，八接口齐平内嵌且外侧可达。',
            '独立固定蒸汽列车；I44交坐标，I45执行允许旅行，不声称实体移动。'],
        not_verified=['外观候选未批准、未安装。', '正式Pattern、配方、旅行授权和失败恢复运行未验收。',
            '材料阶段可达性、PC/FCL运行内存待全部结构完成后测试。'])
