# -*- coding: utf-8 -*-
"""I37实体核验，纳入已批准待装结构作为低阶比较基线。"""
import json
import math
from pathlib import Path
from project_paths import project_path

import numpy as np
from scipy import ndimage

import i37_world_maintenance_geometry_v3_20261027 as geometry
from i34_open_observatory_export_20261027 import digest
from build_i34_imaginary_tree_array_v1_20261027 import stream_form
from structure_size_baseline import baselines

ROOT = geometry.ROOT
TIERS = {n: i + 14 for i, n in enumerate('MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}


def progression(metrics):
    import hashlib
    import zipfile

    index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
    index_sha = digest(index_path)
    index = json.loads(index_path.read_text(encoding='utf-8'))
    assert index['formal_structure_forms'] == index['approved_structure_forms'] == 46
    assert index['pending_batch']['id'] == 'batch-10'
    assert index['pending_batch']['count'] == 0 and index['pending_batch']['approved_machine_ids'] == []
    deployed = index['latest_deployment']
    assert deployed['revision'] == 181 and deployed['game_files_installed']
    assert deployed['sha256'] == '34831bc169b5ac34694842c2a3c45dd5e18caf718aa62df5da1b64c556cbf55e'
    entries = {row['id']: row for row in index['entries']}
    assert 'I37' not in {r['id'] for r in index['entries'] if r.get('formal_resource_present')}

    def resolve(value):
        path = project_path(value)
        assert path.exists(), (str(value), '证据文件不存在')
        return path

    hashes, hashed_bytes = {}, 0

    def verify_file(value, expected):
        nonlocal hashed_bytes
        path = resolve(value)
        key = str(path.resolve()).lower()
        if key not in hashes:
            hashes[key] = digest(path)
            hashed_bytes += path.stat().st_size
        assert hashes[key] == expected, (str(path), 'SHA256变化')
        return path

    receipt_path = verify_file(deployed['receipt'], deployed['receipt_sha256'])
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    assert receipt['status'] == 'installed' and receipt['revision'] == 181
    assert receipt['sha256'] == deployed['sha256'] and receipt['formal_shapes'] == 46
    assert receipt['provisional_processes_unlocked'] == receipt['new_world_tasks_unlocked'] == 0
    old_path = ROOT / 'deliveries/I37_世界维系试验平台_恒界精密试验机_V2_20261027/verification.json'
    old_sha = 'a6d21a5165816ab9eeb72991a31124cc60e529370de0efbf4629ec07c0696d64'
    verify_file(old_path, old_sha)
    previous = json.loads(old_path.read_text(encoding='utf-8'))['voltage_progression']
    frozen = {r['id']: r for r in previous['lower_forms'] if r['status'] == 'formal_installed'}
    assert len(frozen) == 39
    new_hashes = {
        'I34': 'de499d625fe83f1b5b716cf8491ac8e53cd75445a0901aacfd3e0b32712f551f',
        'I35': '23d6ac8b8de8643a0bf08160d960ddb206784fbf2afc9715598142be1dcf5982',
        'I36': '0ff5dbe8b6bfc29ac674ec8fe4a666b3820b7784fa1721b39f14a4096e1189c5',
        'I38': 'df21359bb0c29a58ca48bc3716a597213c72c92741d789c9c3955a6451500429',
        'I39': 'e47edd9663e131d902a13e4dbaed59c4f35f8063cf171e2c532f20aac1413e18',
    }
    formal = ROOT / 'src/main/resources/data/hk3gtl/structures/approved'
    paths = sorted(formal.glob('*.json'))
    assert len(paths) == 46
    rows, approval_checks = [], []

    def zip_member(package, file):
        file = project_path(file)
        candidates = [n for n in package.namelist() if n.endswith('/' + file.name) or n == file.name]
        assert candidates, (str(file), 'ZIP成员不存在')
        expected = digest(file)
        matched = []
        for name in candidates:
            sha = hashlib.sha256()
            with package.open(name) as stream:
                for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                    sha.update(chunk)
            if sha.hexdigest() == expected:
                matched.append(name)
        assert matched, (str(file), 'ZIP成员SHA256不符')

    for meta_path in paths:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        key = meta_path.stem
        role = ('I01-' + key[-1] if key.startswith('i01_') else 'I01-1' if key == 'i01' else key.upper())
        entry = entries[role]
        assert entry['formal_resource_present'] and entry['game_files_installed']
        old = frozen.get(role)
        voltage = meta.get('target_voltage') or (old['voltage'] if old else None)
        assert voltage in TIERS, (role, '缺少正式电压依据')
        if TIERS[voltage] >= TIERS['WFV']:
            continue
        blueprint = ROOT / 'src/main/resources/data/hk3gtl/approved_architecture' / (key + '.json')
        if old:
            verify_file(meta_path, old['metadata_sha256'])
            verify_file(blueprint, old['blueprint_sha256'])
            actual = old.get('actual_xyz') or meta.get('size_xyz') or meta.get('size')
            values = dict(old['metrics'])
            assert values['blocks'] == entry.get('block_count', values['blocks'])
            assert meta.get('blocks', meta.get('block_count', values['blocks'])) == values['blocks']
            if actual:
                assert values['height'] == actual[1] and values['volume'] == math.prod(actual)
            else:
                actual = [0, values['height'], 0]
            evidence = dict(frozen_evidence=str(old_path.relative_to(ROOT)), frozen_evidence_sha256=old_sha)
        else:
            assert role in new_hashes and entry['external_approval_is_authoritative']
            verification = verify_file(project_path(entry['archive']) / 'verification.json', new_hashes[role])
            check = json.loads(verification.read_text(encoding='utf-8'))
            assert check['passed'] and check['readback']['geometry_nbt_schematic_per_block_equal']
            assert check['blocks'] == meta['blocks'] == entry['block_count']
            assert check['size_xyz'] == meta['size_xyz'] == entry['size_xyz']
            assert meta['geometry_nbt_json_per_block_verified'] and meta['all_other_cells_unchanged']
            assert meta['port_positions_faces_purposes_preserved']
            assert meta['target_voltage'] == entry['target_voltage_appearance'] == voltage
            actual = check['size_xyz']
            values = dict(blocks=check['blocks'], materials=check['unique_materials'],
                volume=check['bounding_box_volume'], height=check['height'])
            verify_file(blueprint, meta['sha256'])
            evidence = dict(verification=str(verification), verification_sha256=new_hashes[role])
        assert meta['sha256'] == hashes[str(blueprint.resolve()).lower()]
        expected_nbt = meta.get('approved_nbt_sha256') or meta['source_nbt_sha256']
        source_nbt = entry.get('approved_nbt') or meta.get('source_nbt')
        if not source_nbt:
            matches = [p for p in resolve(entry['archive']).rglob('*.nbt') if digest(p) == expected_nbt]
            assert len(matches) == 1, (role, '批准NBT身份不唯一')
            source_nbt = matches[0]
        nbt = verify_file(source_nbt, expected_nbt)
        if entry.get('approved_nbt_sha256'):
            assert entry['approved_nbt_sha256'] == expected_nbt
        approval = dict(id=role, nbt_sha256=expected_nbt)
        if entry.get('archive_zip'):
            archive = verify_file(entry['archive_zip'], entry['archive_zip_sha256'])
            approval_manifest = resolve(entry['approval_manifest'])
            if meta.get('approval_manifest_sha256'):
                verify_file(approval_manifest, meta['approval_manifest_sha256'])
            with zipfile.ZipFile(archive) as package:
                zip_member(package, nbt)
                zip_member(package, approval_manifest)
                if role in new_hashes:
                    zip_member(package, verification)
            approval.update(archive_zip_sha256=entry['archive_zip_sha256'],
                approval_manifest_sha256=digest(approval_manifest), zip_members_hash_equal=True)
        else:
            assert role in {'I19', 'I20', 'I21'}
            assert entry['approval_message_id'] and entry['approval_quote'] == '那现在弄呗，直接实装'
            approval.update(independent_archive_zip_present=False, approval_message_id=entry['approval_message_id'])
        approval_checks.append(approval)
        rows.append(dict(id=role, voltage=voltage, tier=TIERS[voltage], status='formal_installed',
            metrics=values, actual_xyz=actual, metadata=str(meta_path.relative_to(ROOT)), metadata_sha256=digest(meta_path),
            blueprint=str(blueprint.relative_to(ROOT)), blueprint_sha256=meta['sha256'], **evidence))
    assert len(rows) == len({r['id'] for r in rows}) == 44
    assert set(new_hashes) <= {r['id'] for r in rows}
    maxima = {key: dict(value=max(r['metrics'][key] for r in rows),
        ids=[r['id'] for r in rows if r['metrics'][key] == max(x['metrics'][key] for x in rows)]) for key in metrics}
    minimum = {key: maxima[key]['value'] + 1 for key in metrics}
    assert minimum == dict(blocks=10992375, materials=43, volume=79540264, height=284)
    passes = {key: metrics[key] > maxima[key]['value'] for key in metrics}
    assert all(passes.values()), (metrics, maxima)
    assert digest(index_path) == index_sha, '比较期间批准索引发生变化'
    return dict(source=str(formal.relative_to(ROOT)), formal_metadata_count=46, lower_form_count=44,
        formal_lower_count=44, approved_pending_lower_count=0, lower_forms=rows, metrics=metrics,
        lower_maxima=maxima, minimum_strict_metrics=minimum, passes=passes, target_voltage='WFV', target_tier=27,
        approval_index_sha256=index_sha, deployment_revision=181, deployment_sha256=deployed['sha256'],
        deployment_receipt_sha256=deployed['receipt_sha256'], approval_checks=approval_checks, hashed_source_bytes=hashed_bytes,
        evidence_method='44份现行正式元数据与蓝图、批准NBT与ZIP身份逐项SHA256相同后复用已逐格核验计数。',
        comparison='比较44种已批准并实装的较低电压形态；仅按电压排除I22 WSV、S05 CIV，不按机器编号比较。')

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
        checks=['44种较低电压正式形态的实体数、材料数、包围盒及实际高度四项比较100%通过。',
            '全体六邻接单连通、左右几何和材质严格镜像；WFV主壳为最大单一材料。',
            '钻石主控居中，10接口嵌入真实控制室连续面，有背板及五格外侧净空。'],
        not_verified=['候选待负责人批准，未实装；batch-09五台已实装，batch-10为0/5。',
            '正式控制器、Pattern、维系工况、配方、真实运行事实和游戏运行未在本轮验收。',
            '材料/研究的完整生存获取链未验；历史ICV暂定工单不能替代WFV映射。'])
