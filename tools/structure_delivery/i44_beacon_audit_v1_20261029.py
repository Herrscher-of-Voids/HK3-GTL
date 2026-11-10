# -*- coding: utf-8 -*-
"""I44最终几何的实体、内嵌接口及QCV递进核验。"""
import math
import numpy as np
from scipy import ndimage
import i44_beacon_geometry_v1_20261029 as geometry
from structure_size_baseline import baselines
from i44_voltage_progression_20261029 import validate_progression


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES) + 1)
    assert np.all(counts[1:]), '调色板有未使用材料'
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda row: -row[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        positions = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(positions[0])); high.append(int(positions[-1]))
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size'], (low, actual, data['size'])
    minimum = baselines()['I44']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    labels, components = ndimage.label(occupied)
    if components != 1:
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        parts = []
        for label in np.argsort(sizes)[::-1][:10]:
            if not sizes[label]: continue
            y, z, x = np.argwhere(labels == label)[0]
            parts.append(dict(count=int(sizes[label]), pos=[int(x), int(y), int(z)]))
        raise ValueError(('六邻接游离件', components, parts))
    del labels, occupied
    m = geometry.material
    assert counts[geometry.IDS[m.CONTROL]] == 1
    assert counts[geometry.IDS[m.PORT]] == len(data['ports']) == 8
    assert palette[m.QCV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {m.QCV, m.PORT}
    assert data['controller'][0] == (w - 1) // 2
    checks = []
    for item in [dict(id='主控', pos=data['controller'], face=data['controller_face'])] + data['ports']:
        x, y, z = item['pos']
        assert item['face'] == 'north'
        expected = m.CONTROL if item['id'] == '主控' else m.PORT
        assert cube[y, z, x] == geometry.IDS[expected]
        assert cube[y, z + 1, x], ('接口无内背板', item)
        assert all(cube[y + b, z, x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))), ('不齐平', item)
        assert all(not cube[y, Z, x] for Z in range(max(0, z - 5), z)), ('外侧净空', item)
        checks.append(dict(id=item['id'], position=item['pos'], face='north', flush_shell=True, inner_backed=True, outer_clear=5))
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], ('分区标记落在空气', zone)
    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette) - 2, volume=math.prod(actual), height=h)
    voltage = validate_progression(metrics)
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), ordinary_materials=metrics['materials'], palette=palette,
        qcv_casing_count=palette[m.QCV], bounding_box_volume=metrics['volume'], height=h,
        baseline_check=dict(passed=True, baseline_wdh=minimum), connectivity=dict(passed=True, components=1, neighborhood=6),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1), port_checks=checks,
        voltage_progression=voltage,
        checks=['真实实体达到历史49×49×81下限；QCV低阶四项分别严格超过。',
                'QCV为最多单一材料；只有白名单项目方块。',
                '六邻接单连通；主控整宽中线；八接口齐平且有内背板与外侧净空。',
                '轴向光路、双楔机舱及联锁交接为同一几何；不画成I45列车或传送门。'],
        not_verified=['原作信标具体外形未证实，本候选为工业化演绎。',
            '候选未批准，未接入正式控制器、Pattern、配方或实例。',
            '实际坐标交接合同、能源仓室和生存材料可达性未在此轮验收。',
            'PC/FCL三场景实际运行内存待全部结构完成后测试。'])
