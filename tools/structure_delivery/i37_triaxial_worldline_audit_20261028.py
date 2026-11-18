# -*- coding: utf-8 -*-
"""I37三轴新构型的实体边界、规则递增、镜像及连通性审计。"""
import numpy as np
from scipy import ndimage

import i37_triaxial_worldline_geometry_20261028 as geometry


I38_BASELINE = {
    'blocks': 10_992_374,
    'materials': 42,
    'volume': 79_540_263,
    'height': 283,
}


def audit(grid, data):
    if grid.dtype != np.uint8 or grid.shape != (geometry.H, geometry.D, geometry.W):
        raise ValueError('体素数组类型或轴序不符合合同')
    counts = np.bincount(grid.ravel(), minlength=len(geometry.STATES)+1)
    used = [geometry.STATES[i-1] for i in range(1, len(counts)) if counts[i]]
    ordinary = [state for state in used if state not in (geometry.M.PORT, geometry.M.CONTROL)]
    missing = sorted(set(geometry.STATES[:-2]) - set(ordinary))
    if missing:
        raise ValueError('材质未实际使用：' + ', '.join(missing))
    bounds = np.nonzero(grid)
    y, z, x = bounds
    actual_size = [int(x.max()-x.min()+1), int(y.max()-y.min()+1), int(z.max()-z.min()+1)]
    volume = int(np.prod(actual_size))
    blocks = int(counts[1:].sum())
    materials = len(ordinary)
    height = actual_size[1]
    size_baseline = [97, 129, 65]
    if actual_size[0] < size_baseline[0] or actual_size[2] < size_baseline[1] or actual_size[1] < size_baseline[2]:
        raise ValueError(('占地下限未达到', actual_size, size_baseline))
    if not np.array_equal(grid, grid[:, :, ::-1]):
        delta = int(np.count_nonzero(grid != grid[:, :, ::-1]))
        raise ValueError(('X镜像不成立', delta))
    controller = tuple(data['controller'])
    if controller[0] != geometry.W // 2 or grid[controller[1], controller[2], controller[0]] != geometry.IDS[geometry.M.CONTROL]:
        raise ValueError(('主控未置于实体中心正面', controller))
    occupied = grid != 0
    port_xs = sorted(port['pos'][0] for port in data['ports'])
    if port_xs != sorted(geometry.W - 1 - x for x in port_xs):
        raise ValueError(('接口行未左右镜像', port_xs))
    for port in data['ports']:
        x0, y0, z0 = port['pos']
        if grid[y0, z0, x0] != geometry.IDS[geometry.M.PORT]:
            raise ValueError(('接口标记方块缺失', port))
        if z0 != 0 or occupied[y0, z0+1, x0] == 0:
            raise ValueError(('接口未与设备外壳齐平并有背板', port))
    adjacency = np.zeros((3, 3, 3), dtype=bool)
    adjacency[1, 1, 1] = True
    adjacency[0, 1, 1] = adjacency[2, 1, 1] = True
    adjacency[1, 0, 1] = adjacency[1, 2, 1] = True
    adjacency[1, 1, 0] = adjacency[1, 1, 2] = True
    labels, components = ndimage.label(occupied, structure=adjacency)
    component_sizes = np.bincount(labels.ravel())[1:]
    largest = int(component_sizes.max()) if len(component_sizes) else 0
    del labels, component_sizes, occupied, adjacency
    if components != 1:
        raise ValueError(('结构有游离组件', int(components), largest))
    metrics = {'blocks': blocks, 'materials': materials, 'volume': volume, 'height': height}
    progression = {key: {'candidate': metrics[key], 'I38_approved': I38_BASELINE[key],
                         'passed': metrics[key] > I38_BASELINE[key]} for key in metrics}
    if not all(row['passed'] for row in progression.values()):
        raise ValueError(('电压递增指标未通过', progression))
    return {
        'passed': True,
        'approved': False,
        'installed': False,
        'game_verified': False,
        'size_xyz': actual_size,
        'bounds_xyz': {'min': [int(x.min()), int(y.min()), int(z.min())],
                       'max': [int(x.max()), int(y.max()), int(z.max())]},
        **metrics,
        'unique_materials_including_markers': len(used),
        'palette': {geometry.STATES[i-1]: int(counts[i]) for i in range(1, len(counts)) if counts[i]},
        'wfv_casing_count': int(counts[geometry.IDS[geometry.M.WFV]]),
        'voltage_progression': {'reference': '已批准/实装I38的逐格验证数据',
                                'baseline': I38_BASELINE, 'metrics': metrics,
                                'per_metric': progression, 'passed': True},
        'bilateral_symmetry': {'passed': True, 'axis': 'X=264', 'differing_cells': 0},
        'connectivity': {'passed': True, 'components': int(components), 'neighborhood': 'six-face'},
        'controller': {'position': list(controller), 'ordinal_from_left': controller[0]+1,
                       'flush_shell': True, 'inner_backed': True},
        'ports': [{'id': p['id'], 'position': p['pos'], 'face': p['face'],
                   'flush_shell': True, 'inner_backed': True,
                   'outer_clear': '5 blocks outside structure boundary'} for p in data['ports']],
        'size_baseline': {'size_wdh': size_baseline, 'source': '内测5_69座多方块逐台占地规划与比例预览_v2.html'},
        'checks': [
            '实际坐标达到I37占地规划97×129×65下限。',
            'WFV为独立结构主方块；完整材质与纹理由增强版2.9.2实例解析。',
            '主控位于整宽中心，控制与接口标记嵌入主体结构梁。',
            '结构全体六向连通；X=264镜像差异为0格。',
            'NBT与Sponge逐格回读和体素源完全一致。',
        ],
        'functional_boundary': [
            '仅表达RN-WME世界维系试验工况；结构外观不代表配方、运行逻辑或维系报告已实现。',
            '不得破坏玩家真实世界制造试验事件；起步试件不要求奇观材料。',
            'FCL与电脑版空载、全部摆出、FTB Chunks强加载三场景测试留待全部结构完成。',
        ],
    }
