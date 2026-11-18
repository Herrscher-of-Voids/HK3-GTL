import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from datetime import datetime
import json
from pathlib import Path
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
LOG = ROOT / 'logs/0005-w05-interference-r2-20261115'
LOG.mkdir(exist_ok=True)
manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
parts = manifest['components']
archive = np.load(SOURCE / '原始构件数据.npz')
xyz = [archive[p['id'] + '_xyz'].astype(float) for p in parts]
motions = [p['metadata'].get('motion') for p in parts]
moving = [i for i, m in enumerate(motions) if m]
origins = [a.min(0) for a in xyz]
sizes = [(a.max(0) - a.min(0) + 1).astype(int) for a in xyz]
grids = []
for a, origin, size in zip(xyz, origins, sizes):
    grid = np.zeros(tuple(size), dtype=bool)
    grid[tuple((a - origin).astype(int).T)] = True
    grids.append(grid)


def envelope(a, motion):
    if not motion:
        return a.min(0) - .5, a.max(0) + .5
    pivot = np.array(motion['pivot'])
    if motion['kind'] == 'core':
        return a.min(0) - [.5, 1.7, .5], a.max(0) + [.5, 1.7, .5]
    axis = np.array(motion['axis'], dtype=float)
    axis /= np.linalg.norm(axis)
    local = a - pivot
    axial = np.outer(local @ axis, axis)
    radial = np.sqrt((local - axial) ** 2 + np.cross(axis, local) ** 2)
    return (pivot + axial - radial).min(0) - .866026, (pivot + axial + radial).max(0) + .866026


def transform(motion, t, work):
    if not motion:
        return np.eye(3), np.zeros(3)
    pivot = np.array(motion['pivot'])
    if motion['kind'] == 'core':
        return np.eye(3), np.array([0, np.sin(t * .6) * 1.2, 0])
    speeds = dict(turbine=.8 if work else .12, gyro=.12, crown=1.75 if work else 0, vortex=.9 if work else .22)
    theta = t * motion.get('speed', speeds[motion['kind']]) * motion.get('sign', 1)
    axis = np.array(motion['axis'], dtype=float)
    axis /= np.linalg.norm(axis)
    x, y, z = axis
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    matrix = np.eye(3) * np.cos(theta) + (1 - np.cos(theta)) * np.outer(axis, axis) + np.sin(theta) * cross
    return matrix, pivot - matrix @ pivot


bounds = [envelope(a, m) for a, m in zip(xyz, motions)]
candidates = {i: [j for j in range(len(parts)) if i != j and
    np.all(bounds[i][1] > bounds[j][0]) and np.all(bounds[j][1] > bounds[i][0])] for i in moving}
times = np.arange(0, 60.001, .25)
records = []
started = time.monotonic()
for mode in ('idle', 'work'):
    stats = {(i, j): dict(positive_samples=0, max_center_hits=0) for i in moving for j in candidates[i]}
    for t in times:
        poses = [transform(m, t, mode == 'work') for m in motions]
        for i in moving:
            rotation, offset = poses[i]
            points = xyz[i] @ rotation.T + offset
            lo, hi = points.min(0) - .866026, points.max(0) + .866026
            for j in candidates[i]:
                if np.any(hi <= bounds[j][0]) or np.any(lo >= bounds[j][1]):
                    continue
                rj, tj = poses[j]
                local = (points - tj) @ rj
                rounded = np.floor(local + .5).astype(int)
                grid_points = rounded - origins[j].astype(int)
                valid = np.all((grid_points >= 0) & (grid_points < sizes[j]), axis=1)
                valid &= np.all(np.abs(local - rounded) < .5 - 1e-8, axis=1)
                indices = np.flatnonzero(valid)
                indices = indices[grids[j][tuple(grid_points[indices].T)]]
                if len(indices):
                    stat = stats[i, j]
                    stat['positive_samples'] += 1
                    if len(indices) > stat['max_center_hits']:
                        k = int(indices[0])
                        stat.update(max_center_hits=len(indices), time_s=float(t),
                            source_voxel=xyz[i][k].astype(int).tolist(), target_voxel=rounded[k].tolist(),
                            source_center_world=points[k].tolist(),
                            target_local_point=local[k].tolist())
        if t % 15 == 0:
            print(f'{mode} {t:.0f}s / 60s; elapsed {time.monotonic() - started:.1f}s', flush=True)
    records.extend(dict(mode=mode, source=parts[i]['id'], target=parts[j]['id'], **stat)
                   for (i, j), stat in stats.items())
result = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
    source_delivery=str(SOURCE.relative_to(ROOT)), moving_component_count=len(moving),
    compared_component_count=len(parts), modes=['idle', 'work'], time_range_s=[0, 60], step_s=.25,
    samples_per_mode=len(times), method='源实体格中心依照网页同一变换后，严格落入目标实体格内部；记录肯定体积交叠的下界。',
    limits='未命中不代表零穿模：可能仅有边角相交、帧间相交；不解析框架/玻璃贴图的alpha孔洞，不把模型包络重叠自动等同可见遮挡。',
    source_geometry_changed=False, automated_unit_tests_added=False, desktop_used=False, game_started=False,
    elapsed_s=round(time.monotonic() - started, 2), records=records)
(LOG / 'motion-sampled-center-witnesses.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
print(json.dumps(dict(candidate_directions=len(records) // 2, positive_directions=sum(r['positive_samples'] > 0 for r in records),
    elapsed_s=result['elapsed_s']), ensure_ascii=False))
