# -*- coding: utf-8 -*-
"""以刚体不变量和连续角度上界核验C7，不以有限帧抽样冒充连续净空。"""
import json
import math
from pathlib import Path
import shutil
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/w03-coherent-motion-c7-20261108'
OUT = ROOT / 'deliveries/W03_C7_同步立体净空修订_20261108'


def load(path): return json.loads(path.read_text('utf8'))
def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def rotation(component, t):
    result = np.eye(3)
    for r in component['rotations']:
        angle = r['amplitude_degrees'] * math.sin(2 * math.pi * t / r['period_seconds']) if 'period_seconds' in r else t * r['degrees_per_second']
        result = result @ Rotation.from_rotvec(np.array(r['axis']) * math.radians(angle)).as_matrix()
    return result


def main():
    manifest = load(OUT / 'manifest.json')
    with np.load(LOG / 'moving-parts.npz') as raw:
        parts = {n: raw[n] for n in raw.files}
    components = manifest['components']
    assert list(parts) == [c['id'] for c in components]
    assert all(c['rotations'] == components[0]['rotations'] and c['pivot_blueprint'] == manifest['pivot_blueprint']
               and c['render_translation_xyz'] == [0, 64, 0] for c in components)
    source = load(ROOT / 'deliveries/W03_C4_五环锁芯与立体晶云_20261108/manifest.json')
    bounds = source['clearance']['part_bounds_blueprint']
    trees = {n: cKDTree(p) for n, p in parts.items()}
    minima = 1e9
    pair_count, queried = 0, 0
    for i, (a, p) in enumerate(parts.items()):
        for b, q in list(parts.items())[i + 1:]:
            pair_count += 1
            lower = float(np.maximum(0, np.maximum(p.min(0) - q.max(0), q.min(0) - p.max(0))).max())
            if lower >= 8:
                continue
            queried += 1
            distance = float(trees[b].query(p, p=np.inf, workers=4)[0].min())
            assert distance >= 8, (a, b, distance)
            minima = min(minima, distance)
    assert minima >= 8 and pair_count == 528
    pivot = np.array(manifest['source_pivot_blueprint'])
    floating = np.concatenate(list(parts.values())).astype(float) - pivot
    h = np.linalg.norm(floating[:, [0, 2]], axis=1)
    r = np.linalg.norm(floating, axis=1)
    delta = math.radians(sum(c['amplitude_degrees'] for c in components[0]['rotations'] if 'amplitude_degrees' in c))
    lower = np.where(np.arctan2(h, -floating[:, 1]) <= delta, -r,
                     floating[:, 1] * math.cos(delta) - h * math.sin(delta))
    static_max = max(bounds[n]['max'][1] for n in ['base'] + ['anchor:' + str(i) for i in range(8)]) + 1
    moving_min = float(lower.min() + manifest['pivot_blueprint'][1] - math.sqrt(3))
    vertical_gap = moving_min - static_max
    assert vertical_gap >= 8
    # 共同刚体变换保持任意两点距离；体素以完整单位立方体包住，任意表面间距至少8−√3。
    internal_gap = 8 - math.sqrt(3)
    worst_upward = 1
    for s in source['spears']:
        direction = -np.array(s['tail_axis'])
        min_y = direction[1] * math.cos(delta) - np.linalg.norm(direction[[0, 2]]) * math.sin(delta)
        worst_upward = min(worst_upward, float(min_y))
    assert worst_upward > 0
    # 按实际矩阵复查周期、指向、包络，连续碰撞结论仍来自上面的不变量与角度界。
    maximum_aim_miss, sampled_min_y = 0, 1e9
    for t in np.linspace(0, 360, 721):
        matrix = rotation(components[0], float(t))
        assert np.max(np.abs(matrix.T @ matrix - np.eye(3))) < 1e-12
        for s in source['spears']:
            tip = matrix @ (np.array(s['tip']) - pivot)
            tail = matrix @ (np.array(s['tail']) - pivot)
            v = (tip - tail) / np.linalg.norm(tip - tail)
            maximum_aim_miss = max(maximum_aim_miss, float(np.linalg.norm(np.cross(-tip, v))))
            assert v[1] > 0 and np.dot(-tip, v) > 0
        sampled_min_y = min(sampled_min_y, float((floating @ matrix.T)[:, 1].min() + manifest['pivot_blueprint'][1]))
    assert np.max(np.abs(rotation(components[0], 360) - np.eye(3))) < 1e-12
    # C6回归：内环与固定光柱的内切球相交，可确认实体穿模而非仅包络重叠。
    c6 = load(ROOT / 'deliveries/W03_C6_球形全动试转_20261108/manifest.json')
    old_ring = next(c for c in c6['components'] if c['id'] == 'ring:82')
    beam = parts['core'][parts['core'][:, 1] > 424] + .5
    beam_tree = cKDTree(beam)
    regression = None
    for t in range(1, 361):
        q = (parts['ring:82'] + .5 + old_ring['render_translation_xyz'] - pivot) @ rotation(old_ring, t).T + pivot
        d, at = beam_tree.query(q)
        i = int(d.argmin())
        if d[i] < 1:
            regression = dict(seconds=t, pair=['ring:82', '天顶固定光柱'], center_distance=float(d[i]),
                              rotating_voxel_center=q[i].tolist(), beam_voxel_center=beam[at[i]].tolist(),
                              proof='完整单位立方体的内切球半径各为0.5，球心距离小于1，确认体积相交。')
            break
    assert regression is not None
    result = dict(passed=True, continuous_dynamic_clearance=True,
        method='全部浮空构件共用同一刚体矩阵；528组间距不变；连续摆转总偏角≤16°；底座与八锚塔以完整高度上界排除。',
        independent_component_pairs=pair_count, full_voxel_nearest_queries=queried,
        minimum_center_chebyshev_distance=minima, guaranteed_internal_surface_gap=internal_gap,
        guaranteed_lowest_moving_surface_y=moving_min, highest_static_surface_y=static_max,
        guaranteed_static_vertical_gap=vertical_gap, all_frames_and_between_frames=True,
        original_geometry_voxels_preserved=sum(len(p) for p in parts.values()),
        original_relative_layout_preserved=True, explicit_floating_translation=[0, 64, 0],
        independent_speeds_removed=True, all_33_transforms_identical=True,
        maximum_spear_aim_miss=maximum_aim_miss, continuous_upward_direction_y_lower_bound=worst_upward,
        matrix_samples=721, sampled_minimum_voxel_point_y=sampled_min_y, full_cycle_seconds=360,
        reference_matrices={str(t): rotation(components[0], t).tolist() for t in [0, 19, 47, 137, 271, 360]},
        c6_confirmed_collision_regression=regression, game_implemented=False, game_verified=False)
    save(OUT / 'verification.json', result)
    save(LOG / 'continuous-clearance.json', result)
    shutil.copy2(__file__, OUT / '生成脚本' / Path(__file__).name)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__': main()
