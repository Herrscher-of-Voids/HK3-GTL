# -*- coding: utf-8 -*-
"""I37实体核验，纳入已批准待装结构作为低阶比较基线。"""
import json
import math
from pathlib import Path
from project_paths import project_path

import numpy as np
from scipy import ndimage

import i37_world_maintenance_geometry_v1_20261027 as geometry
from i34_open_observatory_export_20261027 import digest
from build_i34_imaginary_tree_array_v1_20261027 import stream_form
from structure_size_baseline import baselines

ROOT = geometry.ROOT
TIERS = {n: i + 14 for i, n in enumerate('MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}


def progression(metrics):
    evidence = ROOT / 'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/verification.json'
    reference = json.loads(evidence.read_text(encoding='utf-8'))['voltage_progression']
    forms = []
    for row in reference['lower_forms']:
        for key in ('metadata', 'blueprint'):
            assert digest(ROOT / row[key]) == row[key + '_sha256']
        forms.append(dict(row, status='formal_installed'))
    source = ROOT / reference['source']
    assert len(list(source.glob('*.json'))) == 41
    for row in reference['all_forms']:
        if not 25 <= row['tier'] < 27:
            continue
        key = row['id'].lower().replace('-', '_')
        meta_path = source / (key + '.json')
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        assert meta['target_voltage'] == row['voltage']
        blueprint = ROOT / 'src/main/resources/data/hk3gtl/approved_architecture' / (key + '.json')
        size, total, counts, sha = stream_form(blueprint, meta)
        forms.append(dict(id=row['id'], voltage=row['voltage'], tier=row['tier'], status='formal_installed',
            metrics=dict(blocks=total, materials=len({s.split('[')[0] for s in counts}), volume=math.prod(size), height=size[1]),
            metadata=str(meta_path.relative_to(ROOT)), metadata_sha256=digest(meta_path),
            blueprint=str(blueprint.relative_to(ROOT)), blueprint_sha256=sha))
    assert len(forms) == 39
    index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
    index = json.loads(index_path.read_text(encoding='utf-8'))
    assert index['pending_batch']['approved_machine_ids'] == ['I34', 'I35', 'I36']
    assert index['pending_batch']['count'] == 3 and index['formal_structure_forms'] == 41
    for row in index['entries']:
        if row['id'] not in index['pending_batch']['approved_machine_ids']:
            continue
        tier = TIERS[row['target_voltage_appearance']]
        assert tier < 27 and row['external_approval_is_authoritative']
        archive = project_path(row['archive'])
        verification = archive / 'verification.json'
        check = json.loads(verification.read_text(encoding='utf-8'))
        manifest = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
        assert digest(project_path(row['approved_nbt'])) == row['approved_nbt_sha256']
        assert digest(project_path(row['archive_zip'])) == row['archive_zip_sha256']
        assert check['passed'] and check['readback']['geometry_nbt_schematic_per_block_equal']
        assert manifest['target_voltage'] == row['target_voltage_appearance']
        assert check['blocks'] == row['block_count'] and check['size_xyz'] == row['size_xyz']
        forms.append(dict(id=row['id'], voltage=row['target_voltage_appearance'], tier=tier,
            status='approved_archived_waiting_batch', metrics=dict(blocks=check['blocks'], materials=check['unique_materials'],
                volume=check['bounding_box_volume'], height=check['height']),
            verification=str(verification), verification_sha256=digest(verification),
            approval_manifest=row['approval_manifest'], approval_manifest_sha256=digest(project_path(row['approval_manifest'])),
            archive_zip_sha256=row['archive_zip_sha256'], nbt_sha256=row['approved_nbt_sha256']))
    assert len(forms) == len({f['id'] for f in forms}) == 42
    maxima = {k: dict(value=max(f['metrics'][k] for f in forms),
        ids=[f['id'] for f in forms if f['metrics'][k] == max(r['metrics'][k] for r in forms)]) for k in metrics}
    passes = {k: metrics[k] > maxima[k]['value'] for k in metrics}
    assert all(passes.values()), (metrics, maxima)
    return dict(source=reference['source'], formal_metadata_count=41, lower_form_count=len(forms),
        formal_lower_count=39, approved_pending_lower_count=3, lower_forms=forms, metrics=metrics,
        lower_maxima=maxima, passes=passes, target_voltage='WFV', target_tier=27,
        approval_index_sha256=digest(index_path),
        comparison='比较39种正式低阶形态及I34/I35/I36三台已批准待装形态；同阶与高阶不按编号递增。')


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
    minimum = baselines()['I37']['size']
    assert all(actual[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    assert np.array_equal(cube, cube[:, :, ::-1]), '几何与材质不对称'
    labels, components = ndimage.label(occupied)
    assert components == 1, ('实体未连通', components)
    del labels, occupied
    assert counts[geometry.IDS[geometry.material.CONTROL]] == 1
    assert counts[geometry.IDS[geometry.material.PORT]] == len(data['ports']) == 10
    assert palette[geometry.material.WFV] == max(palette.values())
    assert {s for s in palette if s.startswith('hk3gtl:')} == {geometry.material.WFV, geometry.material.PORT}
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
        unique_materials=len(palette), palette=palette, wfv_casing_count=palette[geometry.material.WFV],
        bounding_box_volume=metrics['volume'], height=h, baseline_check=dict(passed=True, baseline_wdh=minimum),
        bilateral_symmetry=dict(passed=True, axis=f'X={(w - 1) // 2}'), connectivity=dict(passed=True, components=1),
        controller=dict(position=data['controller'], ordinal_from_left=data['controller'][0] + 1), port_checks=markers,
        voltage_progression=progression(metrics),
        checks=['42种较低电压批准形态的实体数、材料数、包围盒及实际高度四项比较100%通过。',
            '全体六邻接单连通、左右几何和材质严格镜像；WFV主壳为最大单一材料。',
            '钻石主控居中，10接口嵌入真实控制室连续面，有背板及五格外侧净空。'],
        not_verified=['候选待负责人批准，未实装；batch-09现为I34/I35/I36，3/5。',
            '正式控制器、Pattern、维系工况、配方、真实运行事实和游戏运行未在本轮验收。',
            '材料/研究的完整生存获取链未验；历史ICV暂定工单不能替代WFV映射。'])
