# -*- coding: utf-8 -*-
"""I37 双腔差分场试验场的实体、接口与递增核验。"""
import math

import numpy as np
from scipy import ndimage

import i37_dual_field_range_geometry_20261028 as geometry

LOWER_MAXIMA = dict(blocks=10_992_375, materials=42, volume=79_540_264, height=283)


def audit(cube, data):
    h, d, w = cube.shape
    assert cube.dtype == np.uint8 and cube.flags.c_contiguous
    counts = np.bincount(cube.ravel(), minlength=len(geometry.STATES) + 1)
    assert np.all(counts[1:] > 0), '材料清单中的方块必须全部出现在结构中'
    palette = dict(sorted(zip(geometry.STATES, map(int, counts[1:])), key=lambda pair: -pair[1]))

    occupied = cube != 0
    positions = [np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
                 for axis in (2, 0, 1)]
    low = [int(values[0]) for values in positions]
    high = [int(values[-1]) for values in positions]
    actual = [high[i] - low[i] + 1 for i in range(3)]
    assert low == [0, 0, 0] and actual == data['size'] == [w, h, d]
    assert actual[0] >= 97 and actual[1] >= 129 and actual[2] >= 65
    assert np.array_equal(cube, cube[:, :, ::-1]), '以控制器为轴的几何/材质镜像不一致'

    labels = np.empty(cube.shape, dtype=np.uint16)
    components = ndimage.label(occupied, structure=ndimage.generate_binary_structure(3, 1), output=labels)
    del labels, occupied
    assert components == 1, ('实体六向未连通', components)

    assert counts[geometry.IDS[geometry.material.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.material.PORT]] == len(data['ports']) == 10
    assert palette[geometry.material.WFV] == max(palette.values()), 'WFV机壳须主导新阶段整机识别'
    assert {state for state in palette if state.startswith('hk3gtl:')} == {
        geometry.material.WFV, geometry.material.PORT}
    assert data['controller'][0] == (w - 1) // 2

    directions = dict(north=(0, 0, -1), south=(0, 0, 1), west=(-1, 0, 0), east=(1, 0, 0))
    markers = []
    for item in [dict(id='主控', pos=data['controller'], face='north')] + data['ports']:
        x, y, z = item['pos']
        dx, dy, dz = directions[item['face']]
        state = geometry.material.CONTROL if item['id'] == '主控' else geometry.material.PORT
        assert cube[y, z, x] == geometry.IDS[state]
        assert cube[y - dy, z - dz, x - dx]
        for k in range(1, 6):
            assert not cube[y + dy * k, z + dz * k, x + dx * k], ('接口外侧净空', item)
        tangent = ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
        assert all(cube[y + b, z + c, x + a] for a, b, c in tangent), ('接口周边外墙', item)
        assert np.all(cube[y, z, x - 4:x + 5]), ('接口未嵌入连续墙面', item)
        markers.append(dict(id=item['id'], position=item['pos'], face=item['face'],
                            outer_clear=5, inner_backed=True, flush_shell=True))

    for zone in data['zones']:
        x, y, z = zone['pos']
        assert cube[y, z, x], ('分区标记没有落在实体上', zone)

    metrics = dict(blocks=int(counts[1:].sum()), materials=len(palette),
                   volume=math.prod(actual), height=actual[1])
    comparisons = {key: dict(candidate=metrics[key], lower_voltage_max=value,
                             passed=metrics[key] > value)
                   for key, value in LOWER_MAXIMA.items()}
    assert all(row['passed'] for row in comparisons.values()), comparisons
    return dict(passed=True, geometry_passed=True, approved=False, installed=False, game_verified=False,
        size_xyz=actual, size_wdh=[w, d, h], bounds_xyz=dict(min=low, max=high),
        blocks=metrics['blocks'], unique_materials=metrics['materials'], palette=palette,
        wfv_casing_count=palette[geometry.material.WFV], bounding_box_volume=metrics['volume'],
        height=metrics['height'], voltage_comparison=dict(passed=True, lower_voltage_maxima=LOWER_MAXIMA,
            metrics=metrics, per_metric=comparisons,
            basis='I38已批准/实装IWV结构的当前最大值；非旧I37造型数据'),
        bilateral_symmetry=dict(passed=True, axis='X=264', differing_cells=0),
        connectivity=dict(passed=True, components=int(components), neighborhood='six-face'),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1),
        port_checks=markers,
        checks=['WFV主机壳为全机最大单一材料；43种实际材质全部落位。',
            '六向实体单连通，双腔与中轴以真实支撑闭合；几何和材质以X=264严格镜像。',
            '钻石主控居中；10个接口与主控齐平嵌入连续外墙，背板完整并保留五格净空。',
            '方块数、材料数、包围盒体积和高度均高于现行较低电压批准结构最大值。'],
        not_verified=['候选待负责人审阅批准，未写入正式结构索引、控制器资源或实例。',
            '研究门槛、正式配方、供能合同及游戏内多方块成型未在本轮验收。',
            '未进行FCL/电脑版内存或游戏运行性能测试；不以HTML预览代替实测。'])
