# -*- coding: utf-8 -*-
"""I41实体、连通性、接口净空和电压比较；不代表运行验收。"""
import math
import numpy as np
from scipy import ndimage
import i41_fan_dispatch_geometry_20261028 as geometry
from structure_size_baseline import baselines
from i41_voltage_progression_20261028 import progression


def audit(cube, data):
    h, d, w = cube.shape
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES)+1)
    assert np.all(counts[1:]), '调色板包含未使用材料'
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda row: -row[1]))
    occupied = cube != 0
    low, high = [], []
    for axis in (2, 0, 1):
        positions = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        low.append(int(positions[0])); high.append(int(positions[-1]))
    actual = [high[i]-low[i]+1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size']
    minimum = baselines()['I41']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    labels, components = ndimage.label(occupied)
    if components != 1:
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        order = np.argsort(sizes)[::-1][:12]
        samples = []
        for label in order:
            if not sizes[label]: continue
            y, z, x = np.argwhere(labels == label)[0]
            samples.append(dict(size=int(sizes[label]), pos=[int(x), int(y), int(z)]))
        raise ValueError(('六邻接实体存在游离件', components, samples))
    del labels, occupied
    m = geometry.material
    assert counts[geometry.IDS[m.CONTROL]] == 1
    assert counts[geometry.IDS[m.PORT]] == len(data['ports']) == 6
    assert palette[m.IWV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {m.IWV, m.PORT}
    markers = []
    directions = dict(north=(0, 0, -1), west=(-1, 0, 0), east=(1, 0, 0))
    for item in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = item['pos']; dx, dy, dz = directions[item['face']]
        state = m.CONTROL if item['id'] == '主控' else m.PORT
        assert cube[y, z, x] == geometry.IDS[state]
        assert cube[y-dy, z-dz, x-dx], ('接口没有内背板', item)
        for k in range(1, 6):
            X, Y, Z = x+dx*k, y+dy*k, z+dz*k
            if 0 <= X < w and 0 <= Y < h and 0 <= Z < d:
                assert not cube[Y, Z, X], ('接口外侧净空', item, k)
        tangent = ((0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if dx else ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
        assert all(cube[y+b, z+c, x+a] for a, b, c in tangent), ('接口周边不齐平', item)
        markers.append(dict(id=item['id'], position=item['pos'], face=item['face'],
            flush_shell=True, inner_backed=True, outer_clear=5))
    assert data['controller'][0] == (w-1)//2
    for zone in data['zones']:
        x, y, z = zone['pos']; assert cube[y, z, x], zone
    assert -60+h-1 <= 236
    ordinary = len(palette)-2
    metrics = dict(blocks=int(counts[1:].sum()), materials=ordinary, volume=math.prod(actual), height=h)
    voltage = progression(metrics)
    # I40已获批且为更高WFV，不让新低阶候选反超其四项规模。
    assert all(metrics[k] < v for k, v in dict(blocks=12697362, materials=42, volume=84122571, height=291).items())
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high), blocks=metrics['blocks'],
        unique_materials=len(palette), ordinary_materials=ordinary, material_count_basis='43种含主控与接口标记；普通材料41种，按排除标记的统一口径比较。',
        palette=palette, iwv_casing_count=palette[m.IWV], bounding_box_volume=metrics['volume'], height=h,
        baseline_check=dict(passed=True, baseline_wdh=minimum), connectivity=dict(passed=True, components=1, neighborhood=6),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0]+1), port_checks=markers,
        voltage_progression=voltage,
        checks=['实际边界逐轴达到49×49×57占地下限。', 'IWV为最多的单一材料；仅使用允许的项目自有方块。',
            '弧幕分层机架和六路扇形廊只表达授权负载测控，不产生能源或篡改账本。',
            '六邻接单连通；主控整宽居中，6处接口齐平、有内背板和5格外侧净空。'],
        not_verified=['候选未获批准，未接入正式控制器/Pattern或游戏实例。',
            '手动开停、RN-ELC优先级告警、个人账本授权与完整生存获取链未在本轮验收。',
            'FCL与电脑版三场景内存测试在全部结构完成后进行，本轮未测试。'])
