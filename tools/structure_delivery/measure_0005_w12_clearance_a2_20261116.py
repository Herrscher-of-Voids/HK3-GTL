from datetime import datetime
import hashlib
from itertools import combinations
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W12_三环分层扩腔_A2_20261116'
LOG = ROOT / 'logs/0005-w12-clearance-a2-20261116'
CENTER = np.array([531, 180, 423], np.int32)


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def radial_interval(points):
    minimum, maximum = np.inf, -np.inf
    for start in range(0, len(points), 262144):
        q = points[start:start + 262144] - CENTER
        near = np.maximum(np.maximum(q, -q - 1), 0)
        far = np.maximum(abs(q), abs(q + 1))
        lo = np.sum(near * near, axis=1)
        hi = np.sum(far * far, axis=1)
        i, j = lo.argmin(), hi.argmax()
        if lo[i] < minimum:
            minimum, nearest = int(lo[i]), points[start + i].tolist()
        if hi[j] > maximum:
            maximum, farthest = int(hi[j]), points[start + j].tolist()
    return dict(min_radius_squared=minimum, max_radius_squared=maximum,
                min_radius=float(np.sqrt(minimum)), max_radius=float(np.sqrt(maximum)),
                nearest_block_xyz=nearest, farthest_block_xyz=farthest)


def main():
    geometry_path = OUT / 'geometry.json'
    archive_path = OUT / '修订构件数据.npz'
    geometry = json.loads(geometry_path.read_text('utf-8-sig'))
    archive = np.load(archive_path)
    shells, moving, fixed = {}, [], []
    for name, info in geometry['components'].items():
        shell = radial_interval(archive[name + '_xyz'])
        shell.update(blocks=info['blocks'], label=info['label'])
        shells[name] = shell
        (moving if info['metadata'].get('motion_speed') else fixed).append(name)
        print(name, shell['min_radius'], shell['max_radius'], flush=True)
    moving_pairs = []
    for a, b in combinations(moving, 2):
        ra, rb = shells[a], shells[b]
        gap = max(ra['min_radius'] - rb['max_radius'], rb['min_radius'] - ra['max_radius'])
        moving_pairs.append(dict(a=a, b=b, clearance_lower_bound=gap,
                                 all_phases_separated=gap > 0))
    outer_radius = max(shells[name]['max_radius'] for name in moving)
    fixed_pairs = []
    for name in fixed:
        shell = shells[name]
        gaps = {motion: shell['min_radius'] - shells[motion]['max_radius'] for motion in moving}
        fixed_pairs.append(dict(component=name, label=shell['label'],
            min_radius=shell['min_radius'], nearest_block_xyz=shell['nearest_block_xyz'],
            outside_all_moving_shells_by=shell['min_radius'] - outer_radius,
            clearance_lower_bounds=gaps, all_phases_separated=min(gaps.values()) > 0))
    fixed_pairs.sort(key=lambda item: item['outside_all_moving_shells_by'])
    moving_min = min(item['clearance_lower_bound'] for item in moving_pairs)
    fixed_min = min(item['outside_all_moving_shells_by'] for item in fixed_pairs)
    result = dict(candidate='W12 A2', updated_at=datetime.now().astimezone().isoformat(),
        scope='核心三环、旋转白洞与全部原始固定构件的连续运动净空',
        unit_cube='每个整数p表示完整闭合单位立方体[p,p+(1,1,1)]；枢轴为(531,180,423)。',
        center=CENTER.tolist(),
        method=dict(
            complete_geometry='读取NPZ中的全部独立原始方块，包含静态覆盖前的构件内部重叠。',
            radius_min='q=p-C；最近坐标距离为max(q,-q-1,0)，各轴平方和给完整立方体最小半径平方。',
            radius_max='各轴远端距离为max(abs(q),abs(q+1))，各轴平方和给完整立方体最大半径平方。',
            continuous_proof='绕同一枢轴旋转保持任一点到枢轴的距离。两个径向区间严格分离时，任意独立转角、转速、相位的实体间距均不小于区间间隙。',
            fixed_proof='全部固定方块最近点均在运动外包球之外，固定最小半径减运动最大半径即全相位净空下界。',
            phase_sampling=False, owner_cutouts_used=False),
        shells=shells, moving_components=moving,
        motion_definitions={name: {key: geometry['components'][name]['metadata'][key]
            for key in ('pivot', 'motion_axis', 'motion_speed')} for name in moving},
        moving_pairs=moving_pairs,
        fixed_components=fixed_pairs,
        summary=dict(moving_pair_min_clearance_lower_bound=moving_min,
            fixed_min_clearance_lower_bound=fixed_min,
            closest_fixed_component=fixed_pairs[0]['component'],
            all_core_motion_pairs_proven=all(item['all_phases_separated'] for item in moving_pairs),
            all_fixed_pairs_proven=all(item['all_phases_separated'] for item in fixed_pairs),
            all_phase_separation_proven=moving_min > 0 and fixed_min > 0),
        remaining_scope=dict(
            fixed_corridors='原案双廊重叠、核心净空以外的固定件交叠，按A2修订记录继续单列。',
            chains='锁链的固定端锚接及核心以外链链、链廊交叠，按A2修订记录继续单列。',
            crown='冠环与第2/3/6/7塔、光丝与墙塔的原案冲突继续保留。',
            whole_machine_clearance_approved=False),
        source={str(path.relative_to(ROOT)).replace('\\', '/'): dict(bytes=path.stat().st_size,
                sha256=digest(path)) for path in (geometry_path, archive_path)},
        measurement_kind='负责人要求的实际几何测量', game_verified=False, scores_changed=False)
    LOG.mkdir(parents=True, exist_ok=True)
    for directory in (OUT, LOG):
        (directory / 'continuous-clearance.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(result['summary']), flush=True)


if __name__ == '__main__':
    main()
