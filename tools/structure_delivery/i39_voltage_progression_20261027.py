# -*- coding: utf-8 -*-
"""I39低阶比较：复用逐格计数前逐项核对正式源和批准归档身份。
变更记录 #1 2026-10-27T21:53:42+08:00（香港时间）：删除无；新增ICV比较、当前索引及批准证据校验；
修改无；用途为独立候选审计，不解析超大蓝图，不修改历史证据或实例。
"""
import hashlib
import json
import zipfile
from pathlib import Path
from project_paths import project_path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I38_虚数能量整流中枢_双极脉冲换流站_V1_20261027/verification.json'
SOURCE_SHA256 = 'df21359bb0c29a58ca48bc3716a597213c72c92741d789c9c3955a6451500429'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
INDEX_SHA256 = '936b40474547cb4a480c3dac0459b02fd52f586e4c696e7a5c891c55a483b649'
TIERS = {n: i + 14 for i, n in enumerate('MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}
KEYS = ('blocks', 'materials', 'volume', 'height')
MINIMUM = dict(blocks=1891200, materials=38, volume=23281646, height=206)


def resolve(path):
    value = project_path(path)
    assert value.exists(), (str(path), '证据文件不存在')
    return value


def digest(path):
    value = hashlib.sha256()
    with project_path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def lower_evidence():
    assert digest(SOURCE) == SOURCE_SHA256, '逐格计数来源身份变化，须重新审计'
    assert digest(INDEX) == INDEX_SHA256, '批准索引已变化，须重新确认比较范围'
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    assert index['approved_structure_forms'] == 45 and index['formal_structure_forms'] == 41
    assert index['pending_batch']['approved_machine_ids'] == ['I34', 'I35', 'I36', 'I38']
    assert index['pending_batch']['count'] == 4 and not index['pending_batch']['deployment_eligible']
    reference = json.loads(SOURCE.read_text(encoding='utf-8'))['voltage_progression']
    original = ROOT / reference['evidence']
    assert digest(original) == reference['evidence_sha256'], '原始逐格审计证据变化'
    original_rows = json.loads(original.read_text(encoding='utf-8'))['voltage_progression']['lower_forms']
    rows = [dict(r) for r in reference['lower_forms'] if r['tier'] < TIERS['ICV']]
    assert rows == [r for r in original_rows if r['tier'] < TIERS['ICV']]
    formal = ROOT / reference['source']
    metas = list(formal.glob('*.json'))
    assert len(metas) == 41
    known = {r['metadata']: r for r in reference['lower_forms'] if 'metadata' in r}
    expected_formal = set()
    for path in metas:
        meta = json.loads(path.read_text(encoding='utf-8'))
        relative = str(path.relative_to(ROOT))
        voltage = meta.get('target_voltage') or (known[relative]['voltage'] if relative in known else None)
        assert voltage in TIERS, (relative, '缺少正式电压依据')
        if TIERS[voltage] < TIERS['ICV']:
            expected_formal.add(relative)
    entries = {e['id']: e for e in index['entries']}
    actual_formal, pending, checks, hashed_bytes = set(), [], [], 0
    verified_files, formal_archives = {}, []

    def verify_file(path, expected):
        nonlocal hashed_bytes
        path = project_path(path)
        if str(path) in verified_files:
            assert verified_files[str(path)] == expected
            return expected
        actual = digest(path)
        assert actual == expected, (str(path), 'SHA256变化')
        hashed_bytes += path.stat().st_size
        verified_files[str(path)] = actual
        return actual

    for row in rows:
        assert row['tier'] == TIERS[row['voltage']] < TIERS['ICV']
        if row['status'] == 'formal_installed':
            actual_formal.add(row['metadata'])
            meta = json.loads((ROOT / row['metadata']).read_text(encoding='utf-8'))
            assert meta.get('target_voltage', row['voltage']) == row['voltage']
            assert meta.get('blocks', row['metrics']['blocks']) == row['metrics']['blocks']
            # 旧正式元数据是声明外包，I13/I17包含空边；比较仍用已逐格核验的真实边界。
            assert all(a >= b for a, b in zip(meta.get('size_xyz', row['actual_xyz']), row['actual_xyz']))
            for key in ('metadata', 'blueprint'):
                verify_file(ROOT / row[key], row[key + '_sha256'])
            assert meta['sha256'] == row['blueprint_sha256']
            if 'approval_manifest' in meta:
                verify_file(ROOT / meta['approval_manifest'], meta['approval_manifest_sha256'])
            entry = entries[row['id']]
            assert entry['formal_resource_present'] and entry['game_files_installed']
            metadata_matches_index = entry.get('formal_metadata_sha256', row['metadata_sha256']) == row['metadata_sha256']
            assert metadata_matches_index or row['id'] == 'I05', (row['id'], '索引正式元数据身份冲突')
            if entry.get('formal_architecture_sha256'):
                assert entry['formal_architecture_sha256'] == row['blueprint_sha256']
            archive_check = dict(id=row['id'], approval_quote=entry['approval_quote'],
                index_formal_metadata_current=metadata_matches_index)
            if not metadata_matches_index:
                archive_check['historical_index_metadata_sha256'] = entry['formal_metadata_sha256']
                archive_check['current_verified_metadata_sha256'] = row['metadata_sha256']
            if entry.get('archive_zip'):
                package_path = resolve(entry['archive_zip'])
                verify_file(package_path, entry['archive_zip_sha256'])
                approval_path = resolve(entry['approval_manifest'])
                approved_hash = entry.get('approved_nbt_sha256') or entry['nbt_sha256']
                expected_hash = meta.get('approved_nbt_sha256') or meta['source_nbt_sha256']
                assert approved_hash == expected_hash
                nbt_path = resolve(entry['approved_nbt']) if entry.get('approved_nbt') else None
                if nbt_path is None:
                    matches = [p for p in resolve(entry['archive']).rglob('*.nbt') if digest(p) == approved_hash]
                    assert len(matches) == 1, (row['id'], '批准NBT身份不唯一')
                    nbt_path = matches[0]
                verify_file(nbt_path, approved_hash)
                with zipfile.ZipFile(package_path) as package:
                    for path in (approval_path, nbt_path):
                        relative = path.relative_to(approval_path.parent).as_posix()
                        candidates = [name for name in package.namelist() if name == relative or name.endswith('/' + relative)]
                        assert len(candidates) == 1, (row['id'], relative, '归档成员不唯一')
                        hasher = hashlib.sha256()
                        with package.open(candidates[0]) as handle:
                            for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
                                hasher.update(chunk)
                        assert hasher.hexdigest() == digest(path), (row['id'], relative, 'ZIP与外部证据不符')
                archive_check.update(nbt_sha256=approved_hash, zip_sha256=entry['archive_zip_sha256'],
                    approval_manifest_sha256=digest(approval_path), zip_members_hash_equal=True)
            else:
                # I19至I21的现行索引保留直接实装授权及源NBT，不虚构不存在的独立归档ZIP。
                source = project_path(meta['source_snapshot'])
                matches = [p for p in source.glob('*.nbt') if digest(p) == meta['source_nbt_sha256']]
                assert len(matches) == 1
                verify_file(matches[0], meta['source_nbt_sha256'])
                assert entry['approval_message_id'] and entry['approval_quote'] == '那现在弄呗，直接实装'
                archive_check.update(nbt_sha256=meta['source_nbt_sha256'],
                    approval_message_id=entry['approval_message_id'], independent_archive_zip_present=False)
            formal_archives.append(archive_check)
        else:
            assert row['status'] == 'approved_archived_waiting_batch' and row['id'] == 'I36'
            entry = entries[row['id']]
            assert entry['id'] in index['pending_batch']['approved_machine_ids']
            assert entry['external_approval_is_authoritative']
            assert entry['target_voltage_appearance'] == row['voltage']
            for key in ('verification', 'approval_manifest'):
                verify_file(row[key], row[key + '_sha256'])
            approval_path = project_path(row['approval_manifest'])
            approval = json.loads(approval_path.read_text(encoding='utf-8'))
            approved, = [e for e in approval['entries'] if e['id'] == row['id']]
            assert approved['approval_message_id'] == entry['approval_message_id']
            assert approved['approval_quote'] == entry['approval_quote']
            check = json.loads(project_path(row['verification']).read_text(encoding='utf-8'))
            manifest_path = project_path(entry['archive']) / 'manifest.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            assert check['passed'] and check['readback']['geometry_nbt_schematic_per_block_equal']
            assert manifest['target_voltage'] == row['voltage']
            assert check['blocks'] == entry['block_count'] == row['metrics']['blocks']
            assert check['unique_materials'] == row['metrics']['materials']
            assert check['bounding_box_volume'] == row['metrics']['volume']
            assert check['height'] == row['metrics']['height']
            assert check['size_xyz'] == entry['size_xyz']
            nbt = project_path(entry['approved_nbt'])
            verify_file(nbt, entry['approved_nbt_sha256'])
            assert entry['approved_nbt_sha256'] == row['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
            schem = project_path(entry['archive']) / entry['structure_checks']['schem_file']
            verify_file(schem, check['nbt_schem_sha256']['schem'])
            archive = project_path(entry['archive_zip'])
            verify_file(archive, entry['archive_zip_sha256'])
            assert entry['archive_zip_sha256'] == row['archive_zip_sha256']
            message_path = approval_path.parent / 'evidence/approval-message-evidence.json'
            message = json.loads(message_path.read_text(encoding='utf-8'))
            assert message['message_id'] == entry['approval_message_id'] and message['user_text'] == entry['approval_quote']
            source_message = None
            with project_path(message['source_session']).open(encoding='utf-8') as handle:
                for line in handle:
                    if message['message_id'] in line:
                        event = json.loads(line)
                        if event.get('type') == 'response_item' and event.get('payload', {}).get('id') == message['message_id']:
                            source_message = event
                            break
            assert source_message and source_message['timestamp'] == message['timestamp']
            assert message['user_text'] in source_message['payload']['content'][0]['text']
            with zipfile.ZipFile(archive) as package:
                for path in (message_path, project_path(row['verification']), manifest_path, nbt, schem):
                    name = path.relative_to(approval_path.parent).as_posix()
                    hasher = hashlib.sha256()
                    with package.open(name) as handle:
                        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
                            hasher.update(chunk)
                    assert hasher.hexdigest() == digest(path), (row['id'], name, 'ZIP内外身份不符')
            checks.append(dict(id=row['id'], approval_message_id=message['message_id'],
                approval_message_evidence_sha256=digest(message_path), source_message_matched=True,
                zip_selected_members_hash_equal=True, manifest_sha256=digest(manifest_path)))
            pending.append(row['id'])
    assert expected_formal == actual_formal and len(actual_formal) == 34
    assert pending == ['I36'] and len(rows) == len({r['id'] for r in rows}) == 35
    maxima = {k: dict(value=max(r['metrics'][k] for r in rows),
        ids=[r['id'] for r in rows if r['metrics'][k] == max(x['metrics'][k] for x in rows)]) for k in KEYS}
    minimum = {k: maxima[k]['value'] + 1 for k in KEYS}
    assert minimum == MINIMUM
    assert digest(INDEX) == INDEX_SHA256, '比较期间批准索引发生变化'
    return dict(source=reference['source'], formal_metadata_count=41, target_voltage='ICV', target_tier=24,
        lower_form_count=35, formal_lower_count=34, approved_pending_lower_count=1, lower_forms=rows,
        lower_maxima=maxima, minimum_strict_metrics=minimum, approval_index_sha256=INDEX_SHA256,
        evidence=str(SOURCE.relative_to(ROOT)), evidence_sha256=SOURCE_SHA256,
        original_per_block_evidence=str(original.relative_to(ROOT)), original_per_block_evidence_sha256=reference['evidence_sha256'],
        approval_checks=checks, formal_archive_checks=formal_archives, hashed_source_bytes=hashed_bytes,
        evidence_method='34份正式元数据/蓝图流式SHA256与原逐格计数证据相同；正式批准NBT与可用归档ZIP/清单成员核对，I19至I21直接授权源无独立ZIP，如实单列；I36批准清单、NBT、Schematic、ZIP及原始批准消息逐项核对；不解析超大蓝图。',
        exclusions=['同阶ICV的I29/I30/I31不比较；S04为更高IRV，也不比较。', 'I34/I35/I38已批准但电压较高，不比较；I37未批准且为更高WFV，不比较。'],
        comparison='严格超过34种正式较低电压形态及I36已批准待装形态；不按机器编号递增。')


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
