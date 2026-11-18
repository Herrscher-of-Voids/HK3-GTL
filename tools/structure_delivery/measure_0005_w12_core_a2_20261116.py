import json
from pathlib import Path

from w12_core_a2_20261116 import CAVITY_RADIUS, CENTER, RING_RADII, build, cube_shell


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w12-clearance-a2-20261116'


def main():
    parts, notes = build()
    shells = {part.name: cube_shell(part.p) for part in parts}
    rings = parts[3:6]
    clearances = []
    for index, first in enumerate(rings):
        for second in rings[index + 1:]:
            clearances.append(dict(a=first.name, b=second.name,
                                   continuous_clearance_lower_bound=shells[second.name][0] - shells[first.name][1]))
        for fixed in parts[:3] + [parts[6]]:
            clearances.append(dict(a=first.name, b=fixed.name,
                                   continuous_clearance_lower_bound=shells[fixed.name][0] - shells[first.name][1]))
        clearances.append(dict(a='white_singularity', b=first.name,
                               continuous_clearance_lower_bound=shells[first.name][0] - shells['white_singularity'][1]))
    clearances.append(dict(a='white_singularity', b='twelve_binding_lances',
                           continuous_clearance_lower_bound=shells['twelve_binding_lances'][0] - shells['white_singularity'][1]))
    data = dict(candidate='A2', scope='三环、纯白奇点、三十字及十二矛的完整方块连续运动净空',
                unit_cube='每个整数p代表闭合单位立方体[p,p+(1,1,1)]，旋转枢轴直接取(531,180,423)。',
                pivot=CENTER.tolist(), ring_nominal_radii=list(RING_RADII),
                cavity_origin_radius=CAVITY_RADIUS, cavity_nominal_diameter=2 * CAVITY_RADIUS,
                method='逐个完整立方体求枢轴至最近点及最远角点的精确距离；全部方块取最小、最大值得到封闭球壳。绕同一枢轴的任何旋转保持球心距离，内外球壳之间的径向间隔因此是任意相位、转速、待机及工作状态下的欧氏净空下界。',
                measurement_kind='负责人要求的几何净空计算，无测试或断言。',
                components={part.name: dict(label=part.label, blocks=len(part.p),
                            exact_radial_min=shells[part.name][0], exact_radial_max=shells[part.name][1],
                            bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist()),
                            metadata=part.metadata) for part in parts},
                clearances=clearances,
                minimum_ring_pair_clearance=min(row['continuous_clearance_lower_bound'] for row in clearances if row['a'].startswith('core_gyroscope_') and row['b'].startswith('core_gyroscope_')),
                minimum_listed_clearance=min(row['continuous_clearance_lower_bound'] for row in clearances),
                notes=notes,
                neighboring_parts_scope='链及长廊由相邻构件修订文件单独测量，外围冠环与垂丝沿用已登记残留问题。',
                source_code='tools/structure_delivery/w12_core_a2_20261116.py',
                appearance_approved=False, game_verified=False)
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / 'core-motion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(minimum_ring_pair_clearance=data['minimum_ring_pair_clearance'],
                          minimum_listed_clearance=data['minimum_listed_clearance'],
                          blocks=sum(len(part.p) for part in parts)), ensure_ascii=False))


if __name__ == '__main__':
    main()
