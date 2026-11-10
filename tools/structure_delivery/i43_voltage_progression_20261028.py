# -*- coding: utf-8 -*-
"""I43 WSV递进：流式复核正式证据，并核对I40至I42批准归档。

变更记录 #1 2026-10-28 Asia/Hong_Kong：普通材料排除主控和接口标记；不读取未批准草稿。
"""
import json
import math
from pathlib import Path
import i41_voltage_progression_20261028 as shared

ROOT, FORMAL, INDEX, MAPPING = shared.ROOT, shared.FORMAL, shared.INDEX, shared.MAPPING
AUDIT, AUDIT_SHA256, TIERS, KEYS = shared.AUDIT, shared.AUDIT_SHA256, shared.TIERS, shared.KEYS
_snapshot, _digest, _resolve, _stamp = shared._snapshot, shared._digest, shared._resolve, shared._stamp


def _metrics_valid(metrics, size, bounds, ordinary):
    return (set(metrics) == set(KEYS)
        and all(type(metrics[key]) is int and metrics[key] > 0 for key in KEYS)
        and len(size) == 3 and size == [b-a+1 for a, b in zip(bounds['min'], bounds['max'])]
        and metrics['height'] == size[1] and metrics['volume'] == math.prod(size)
        and metrics['materials'] == len(set(ordinary))
        and all(state.split('[', 1)[0] not in {'hk3gtl:industrial_port_casing', 'minecraft:air',
            'minecraft:cave_air', 'minecraft:void_air'} for state in ordinary))


def _approved_pending(entry, watched):
    identity = {"I40": ("V1", "WFV"), "I41": ("V3", "IWV"), "I42": ("V1", "WFV")}
    if entry["id"] not in identity:
        raise ValueError(("待安装低阶尚未补审", entry["id"]))
    version, voltage = identity[entry["id"]]
    key = entry["id"].lower()
    if (entry['key'] != key or entry.get('approved_version') != version
            or not entry.get('external_approval_is_authoritative') or not entry.get('approval_quote')
            or entry.get('formal_resource_present') or entry.get('game_files_installed')):
        raise ValueError('待安装低阶须为已核实版本、明确批准且独立归档；不能读取候选冒充批准')
    archive = _resolve(entry['archive'])
    if not archive.is_relative_to((ROOT / 'deliveries/多方块确认归档').resolve()):
        raise ValueError('低阶证据必须取自批准归档')
    approval_path = _resolve(entry['approval_manifest'])
    raw, approval_sha, watched[approval_path] = _snapshot(approval_path)
    approval = json.loads(raw)
    records = [e for e in approval['entries'] if e['key'] == entry['key']]
    if len(records) != 1 or any(records[0].get(key) != entry.get(key) for key in
            ('id', 'approved_version', 'approval_quote', 'approval_message_id', 'archive')):
        raise ValueError('低阶批准索引与独立确认清单不一致')
    if not approval.get('external_approval_is_authoritative') or not approval.get('source_all_bytes_unchanged'):
        raise ValueError('低阶归档未确认外部批准及源文件保持不变')
    hashes = approval['source_files_sha256']

    def document(name):
        path = archive / name
        raw, sha, watched[path] = _snapshot(path)
        if hashes.get(name) != sha:
            raise ValueError(('低阶归档文档与批准哈希不一致', name))
        return path, json.loads(raw), sha

    manifest_path, meta, manifest_sha = document('manifest.json')
    verification_path, verify, verification_sha = document('verification.json')
    if (meta['key'] != key or meta.get('candidate_version') != version
            or meta.get('target_voltage') != voltage or not verify.get('passed')
            or not verify.get('geometry_passed') or not verify.get('readback', {}).get('passed')
            or not verify['readback'].get('geometry_nbt_schematic_per_block_equal')):
        raise ValueError('低阶归档缺少正确身份、电压或NBT/Schematic逐格一致核验')
    size, bounds, palette = verify['size_xyz'], verify['bounds_xyz'], verify['palette']
    ordinary = sorted(s for s in palette if s not in {'minecraft:diamond_block', 'hk3gtl:industrial_port_casing'})
    metrics = dict(blocks=verify['blocks'], materials=verify['ordinary_materials'],
        volume=verify['bounding_box_volume'], height=verify['height'])
    if (not _metrics_valid(metrics, size, bounds, ordinary)
            or any(type(count) is not int or count <= 0 for count in palette.values())
            or sum(palette.values()) != metrics['blocks'] or len(palette) != verify['unique_materials']
            or palette.get('minecraft:diamond_block') != 1
            or palette.get('hk3gtl:industrial_port_casing') != len(meta['ports'])
            or meta['size'] != size or entry['size_xyz'] != size
            or verify['controller']['position'] != meta['controller'] or entry['controller'] != meta['controller']
            or entry['block_count'] != metrics['blocks'] or entry['ordinary_materials'] != metrics['materials']
            or meta['blocks'] != metrics['blocks'] or meta['ordinary_materials'] != metrics['materials']
            or entry['unique_materials'] != len(palette) or entry['port_count'] != len(meta['ports'])
            or verify['readback']['palette_count'] != len(palette)
            or verify['readback']['blocks'] != metrics['blocks'] or verify['readback']['size_xyz'] != size):
        raise ValueError('低阶归档实体、边界、普通材料或标记统计冲突')
    bytes_hashed = watched[manifest_path][0] + watched[verification_path][0] + watched[approval_path][0]
    binary_hashes = {}
    for suffix in ('nbt', 'schem'):
        relative = f"{key}/{meta['name']}.{suffix}"
        path = archive / relative
        sha, watched[path] = _digest(path)
        expected = verify['nbt_schem_sha256'][suffix]
        if sha != expected or hashes.get(relative) != sha:
            raise ValueError(('低阶归档结构二进制与逐格核验及批准哈希不一致', suffix))
        if suffix == 'nbt' and (path.resolve() != _resolve(entry['approved_nbt'])
                or entry['approved_nbt_sha256'] != sha or entry.get('nbt_sha256', sha) != sha):
            raise ValueError('低阶索引指定的批准NBT与归档不一致')
        binary_hashes[suffix] = sha
        bytes_hashed += watched[path][0]
    archive_zip = _resolve(entry['archive_zip'])
    zip_sha, watched[archive_zip] = _digest(archive_zip)
    if zip_sha != entry['archive_zip_sha256']:
        raise ValueError('低阶批准归档ZIP的SHA256变化')
    bytes_hashed += watched[archive_zip][0]
    row = dict(id=entry['id'], key=key, voltage=voltage, tier=TIERS[voltage], status=entry['status'],
        metadata=str(manifest_path.relative_to(ROOT)), metadata_sha256=manifest_sha,
        verification=str(verification_path.relative_to(ROOT)), verification_sha256=verification_sha,
        approval_manifest=str(approval_path.relative_to(ROOT)), approval_manifest_sha256=approval_sha,
        approved_nbt=str(_resolve(entry['approved_nbt']).relative_to(ROOT)), approved_nbt_sha256=binary_hashes['nbt'],
        approved_schematic_sha256=binary_hashes['schem'], archive_zip=str(archive_zip.relative_to(ROOT)),
        archive_zip_sha256=zip_sha, approval_quote=entry['approval_quote'], actual_xyz=size, bounds_xyz=bounds,
        metrics=metrics, total_palette_count=len(palette), ordinary_states=ordinary,
        excluded_marker_cells=dict(controller=1, industrial_ports=len(meta['ports'])),
        evidence_method='批准清单锁定归档manifest、逐格NBT/Schematic回读统计及两份结构文件；重新流式核对结构和ZIP哈希。')
    return row, bytes_hashed


def lower_evidence():
    index_data, index_sha, index_stamp = _snapshot(INDEX)
    mapping_data, mapping_sha, mapping_stamp = _snapshot(MAPPING)
    audit_data, audit_sha, audit_stamp = _snapshot(AUDIT)
    if audit_sha != AUDIT_SHA256:
        raise ValueError('原已逐格审计证据发生变化，须重新确认')
    index, audit, mapping = json.loads(index_data), json.loads(audit_data), shared._mapping(mapping_data)
    if mapping.get('I43') != 'WSV' or mapping_sha != audit['voltage_mapping_sha256']:
        raise ValueError('I43映射或原审计映射发生变化')
    entries = {entry['key']: entry for entry in index['entries']}
    if len(entries) != len(index['entries']) or len({e['id'] for e in entries.values()}) != len(entries):
        raise ValueError('批准索引存在重复key或形态ID')
    for entry in entries.values():
        voltage = entry.get('target_voltage_appearance') or entry.get('target_voltage') or mapping.get(entry['id'])
        if voltage not in TIERS or voltage != mapping.get(entry['id']):
            raise ValueError(('当前批准索引电压冲突', entry['id']))
    watched = {INDEX: index_stamp, MAPPING: mapping_stamp, AUDIT: audit_stamp}
    metas = {}
    for path in sorted(FORMAL.glob('*.json')):
        raw, sha, watched[path] = _snapshot(path)
        meta = json.loads(raw)
        if meta['key'] in metas:
            raise ValueError('正式元数据key重复')
        metas[meta['key']] = path, meta, sha
    if (len(metas) != index['formal_structure_forms']
            or set(metas) != {key for key, entry in entries.items() if entry.get('formal_resource_present')}):
        raise ValueError('正式元数据与批准索引覆盖不一致')
    rows = [dict(row) for row in audit['lower_forms'] if TIERS[mapping[row['id']]] < TIERS['WSV']]
    formal_expected = {entry['id'] for entry in entries.values()
        if entry.get('formal_resource_present') and TIERS[mapping[entry['id']]] < TIERS['WSV']}
    if len(rows) != len({row['id'] for row in rows}) or {row['id'] for row in rows} != formal_expected:
        raise ValueError('现役WSV低阶集合与原逐格证据不一致，须补审')
    hashed_bytes = 0
    for row in rows:
        entry = entries[row['key']]
        path, meta, metadata_sha = metas[row['key']]
        if (entry['id'] != row['id'] or row['voltage'] != mapping[row['id']] or row['tier'] != TIERS[row['voltage']]
                or not entry.get('game_files_installed') or entry.get('approval_quote') != row['approval_quote']
                or path.resolve() != _resolve(row['metadata']) or metadata_sha != row['metadata_sha256']):
            raise ValueError(('正式低阶身份、批准或元数据变化', row['id']))
        blueprint = _resolve(meta['source'])
        if blueprint != _resolve(row['blueprint']) or meta['sha256'] != row['blueprint_sha256']:
            raise ValueError(('正式蓝图身份与原证据冲突', row['id']))
        sha, watched[blueprint] = _digest(blueprint)
        if sha != row['blueprint_sha256']:
            raise ValueError(('正式蓝图内容变化，须重新逐格审计', row['id']))
        hashed_bytes += watched[path][0] + watched[blueprint][0]
        if (not _metrics_valid(row['metrics'], row['actual_xyz'], row['bounds_xyz'], row['ordinary_states'])
                or row['excluded_marker_cells']['controller'] != 1):
            raise ValueError(('正式实体、边界或普通材料口径冲突', row['id']))
        for declared in (meta.get('size_xyz') or meta.get('size'), entry.get('size_xyz')):
            if declared and any(actual > limit for actual, limit in zip(row['actual_xyz'], declared)):
                raise ValueError(('真实边界超出当前声明', row['id']))
        for count in (meta.get('blocks'), entry.get('block_count')):
            if count is not None and count != row['metrics']['blocks']:
                raise ValueError(('正式实体数与索引冲突', row['id']))
    formal_count = len(rows)
    pending = [entry for entry in entries.values() if not entry.get('formal_resource_present')
        and TIERS[mapping[entry['id']]] < TIERS['WSV']]
    if {entry['id'] for entry in pending} != {'I40', 'I41', 'I42'}:
        raise ValueError('本轮须纳入归档I40 V1、I41 V3、I42 V1；新增待安装低阶时须补审')
    for entry in sorted(pending, key=lambda item: item['id']):
        row, added_bytes = _approved_pending(entry, watched)
        rows.append(row)
        hashed_bytes += added_bytes
    expected = {entry['id'] for entry in entries.values() if TIERS[mapping[entry['id']]] < TIERS['WSV']}
    if {row['id'] for row in rows} != expected:
        raise ValueError('全部已批准WSV低阶未覆盖完整')
    if (set(FORMAL.glob('*.json')) != {value[0] for value in metas.values()}
            or any(_stamp(path) != stamp for path, stamp in watched.items())
            or _snapshot(INDEX)[1] != index_sha or _snapshot(MAPPING)[1] != mapping_sha):
        raise ValueError('核验期间批准索引、映射或证据文件变化，请重新运行')
    maxima = {key: dict(value=max(row['metrics'][key] for row in rows),
        ids=[row['id'] for row in rows if row['metrics'][key] == max(r['metrics'][key] for r in rows)]) for key in KEYS}
    excluded = [dict(id=e['id'], voltage=mapping[e['id']], status=e['status'],
        reason='同阶' if TIERS[mapping[e['id']]] == TIERS['WSV'] else '更高阶')
        for e in entries.values() if TIERS[mapping[e['id']]] >= TIERS['WSV']]
    if 'I37' not in {e['id'] for e in entries.values()}:
        excluded.append(dict(id='I37', reason='未批准，不读取旧草稿'))
    return dict(source=str(FORMAL.relative_to(ROOT)), target_voltage='WSV', target_tier=28,
        formal_metadata_count=len(metas), formal_lower_count=formal_count, approved_pending_lower_count=len(pending),
        lower_form_count=len(rows), lower_forms=rows, lower_maxima=maxima,
        minimum_strict_metrics={key: maxima[key]['value']+1 for key in KEYS},
        approval_index_sha256=index_sha, voltage_mapping=str(MAPPING.relative_to(ROOT)), voltage_mapping_sha256=mapping_sha,
        source_audit=str(AUDIT.relative_to(ROOT)), source_audit_sha256=audit_sha, hashed_source_bytes=hashed_bytes,
        exclusions=excluded, material_count_scope=audit['material_count_scope'],
        evidence_method='复用原逐格证据，流式复核全部现役低阶蓝图；追加本轮批准I40 V1、I41 V3、I42 V1归档逐格回读及批准/结构/ZIP哈希，核对当次索引完整覆盖。',
        comparison='比较全部已批准较低电压形态，包括已批准待安装I40、I41、I42；同阶I22、更高阶S05及未批准I37排除。')


def _compare(metrics, evidence):
    if set(metrics) != set(KEYS) or not all(type(metrics[key]) is int and metrics[key] > 0 for key in KEYS):
        raise ValueError('须提供blocks/materials/volume/height四项正整数实际指标；materials排除主控和接口标记')
    passes = {key: metrics[key] > evidence['lower_maxima'][key]['value'] for key in KEYS}
    if not all(passes.values()):
        raise ValueError(('WSV候选未严格超过全部已批准低阶', metrics, evidence['lower_maxima']))
    return dict(evidence, metrics=dict(metrics), passes=passes, passed=True)


def progression(metrics):
    return _compare(metrics, lower_evidence())


def self_check():
    evidence = lower_evidence()
    assert evidence['lower_form_count'] == 47 and evidence['formal_lower_count'] == 44
    assert evidence['approved_pending_lower_count'] == 3
    assert {r['id'] for r in evidence['lower_forms'] if 'approval_manifest' in r} == {'I40', 'I41', 'I42'}
    minimum = evidence['minimum_strict_metrics']
    assert minimum == dict(blocks=14747314, materials=43, volume=84903656, height=296)
    assert _compare(minimum, evidence)['passed']
    for key in KEYS:
        try:
            _compare(dict(minimum, **{key: minimum[key]-1}), evidence)
        except ValueError:
            continue
        raise AssertionError(('等于下限最大值必须拒绝', key))
    return dict(passed=True, lower_form_count=evidence['lower_form_count'], minimum_strict_metrics=minimum,
        formal_lower_count=evidence['formal_lower_count'], approved_pending_lower_count=3,
        approval_index_sha256=evidence['approval_index_sha256'], hashed_source_bytes=evidence['hashed_source_bytes'])


if __name__ == '__main__':
    import sys
    result = self_check() if sys.argv[1:] == ['--self-check'] else progression(json.loads(sys.argv[1])) if sys.argv[1:] else lower_evidence()
    print(json.dumps(result, ensure_ascii=False, indent=2))
