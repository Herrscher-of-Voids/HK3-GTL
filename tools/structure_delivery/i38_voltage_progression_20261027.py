# -*- coding: utf-8 -*-
"""I38低阶电压基线：复用已逐格核验的计数，逐份校验当前源文件身份。
变更记录 #1 2026-10-27 17:47:16 Asia/Hong_Kong：删除无；新增IWV较低阶比较及SHA256校验；
修改无；用途为I38独立候选审计，避免再次解析百万格蓝图，不修改批准或实例文件。
"""
import hashlib
import json
from pathlib import Path
from project_paths import project_path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I37_世界维系试验平台_恒界精密试验机_V2_20261027/verification.json'
SOURCE_SHA256 = 'a6d21a5165816ab9eeb72991a31124cc60e529370de0efbf4629ec07c0696d64'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
TIERS = {n: i + 14 for i, n in enumerate('MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}
KEYS = ('blocks', 'materials', 'volume', 'height')


def digest(path):
    value = hashlib.sha256()
    with project_path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def lower_evidence():
    assert digest(SOURCE) == SOURCE_SHA256, '已核验计数证据身份变化，须重新审计'
    reference = json.loads(SOURCE.read_text(encoding='utf-8'))['voltage_progression']
    assert digest(INDEX) == reference['approval_index_sha256'], '批准索引已变化，须更新比较范围'
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    assert index['formal_structure_forms'] == 41
    assert index['pending_batch']['approved_machine_ids'] == ['I34', 'I35', 'I36']
    assert index['pending_batch']['count'] == 3
    rows = [dict(r) for r in reference['lower_forms'] if r['tier'] < TIERS['IWV']]
    formal = ROOT / reference['source']
    metas = list(formal.glob('*.json'))
    assert len(metas) == 41
    reference_formal = {r['metadata']: r for r in reference['lower_forms'] if 'metadata' in r}
    expected_formal = set()
    for path in metas:
        meta = json.loads(path.read_text(encoding='utf-8'))
        relative = str(path.relative_to(ROOT))
        voltage = meta.get('target_voltage') or reference_formal[relative]['voltage']
        if TIERS[voltage] < TIERS['IWV']:
            expected_formal.add(relative)
    actual_formal = set()
    entries = {e['id']: e for e in index['entries']}
    hashed_bytes = 0
    for row in rows:
        assert row['tier'] == TIERS[row['voltage']]
        if row['status'] == 'formal_installed':
            actual_formal.add(row['metadata'])
            meta = json.loads((ROOT / row['metadata']).read_text(encoding='utf-8'))
            assert meta.get('target_voltage', row['voltage']) == row['voltage']
            for key in ('metadata', 'blueprint'):
                path = ROOT / row[key]
                assert digest(path) == row[key + '_sha256'], (row['id'], key, 'SHA256变化')
                hashed_bytes += path.stat().st_size
        else:
            assert row['status'] == 'approved_archived_waiting_batch'
            entry = entries[row['id']]
            assert entry['id'] in index['pending_batch']['approved_machine_ids']
            assert entry['external_approval_is_authoritative']
            assert entry['target_voltage_appearance'] == row['voltage']
            for key in ('verification', 'approval_manifest'):
                path = project_path(row[key])
                assert digest(path) == row[key + '_sha256'], (row['id'], key, 'SHA256变化')
                hashed_bytes += path.stat().st_size
            check = json.loads(project_path(row['verification']).read_text(encoding='utf-8'))
            manifest = json.loads((project_path(entry['archive']) / 'manifest.json').read_text(encoding='utf-8'))
            assert check['passed'] and check['readback']['geometry_nbt_schematic_per_block_equal']
            assert manifest['target_voltage'] == row['voltage']
            assert check['blocks'] == entry['block_count'] == row['metrics']['blocks']
            assert check['unique_materials'] == row['metrics']['materials']
            assert check['bounding_box_volume'] == row['metrics']['volume']
            assert check['height'] == row['metrics']['height']
            assert check['size_xyz'] == entry['size_xyz']
            for path_key, hash_key, evidence_key in (
                ('approved_nbt', 'approved_nbt_sha256', 'nbt_sha256'),
                ('archive_zip', 'archive_zip_sha256', 'archive_zip_sha256')):
                path = project_path(entry[path_key])
                assert digest(path) == entry[hash_key] == row[evidence_key], (row['id'], path_key, 'SHA256变化')
                hashed_bytes += path.stat().st_size
    assert expected_formal == actual_formal and len(actual_formal) == 38
    assert len(rows) == len({r['id'] for r in rows}) == 41
    maxima = {k: dict(value=max(r['metrics'][k] for r in rows),
        ids=[r['id'] for r in rows if r['metrics'][k] == max(x['metrics'][k] for x in rows)]) for k in KEYS}
    return dict(source=reference['source'], formal_metadata_count=41, target_voltage='IWV', target_tier=26,
        lower_form_count=41, formal_lower_count=38, approved_pending_lower_count=3, lower_forms=rows,
        lower_maxima=maxima, minimum_strict_metrics={k: maxima[k]['value'] + 1 for k in KEYS},
        approval_index_sha256=digest(INDEX), evidence=str(SOURCE.relative_to(ROOT)), evidence_sha256=SOURCE_SHA256,
        evidence_method='已逐格核验的计数仅在当前38份正式蓝图/元数据及3份批准归档身份逐项SHA256相同后复用；本次不解析超大蓝图。',
        hashed_source_bytes=hashed_bytes,
        exclusions=['I01-4为同阶IWV，不比较；I22/S05为较高阶，不比较。',
                    'I37 V2为未批准WFV候选，不因机器编号或旧审计证据来源而纳入比较。'],
        comparison='逐项严格超过38种正式较低电压形态及I34/I35/I36三台已批准待装形态；不按机器编号递增。')


def progression(metrics):
    assert set(metrics) == set(KEYS), '必须提供blocks/materials/volume/height四项实际指标'
    assert all(isinstance(metrics[k], int) and not isinstance(metrics[k], bool) and metrics[k] > 0 for k in KEYS)
    result = lower_evidence()
    passes = {k: metrics[k] > result['lower_maxima'][k]['value'] for k in KEYS}
    assert all(passes.values()), (metrics, result['lower_maxima'])
    result.update(metrics=metrics, passes=passes)
    return result


if __name__ == '__main__':
    import sys
    result = lower_evidence() if len(sys.argv) == 1 else progression(json.loads(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
