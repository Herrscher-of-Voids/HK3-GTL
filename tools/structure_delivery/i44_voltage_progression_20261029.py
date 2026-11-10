# -*- coding: utf-8 -*-
"""I44 QCV候选：按当前批准索引复核24个较低电压形态。

变更记录 #1（2026-10-29）：复用既有逐格统计并重新核对正式实体哈希，不读取旧I44草稿。
"""
import json
import math
from pathlib import Path

import i41_voltage_progression_20261028 as shared

ROOT, INDEX, MAPPING = shared.ROOT, shared.INDEX, shared.MAPPING
AUDIT = ROOT / 'logs/i43-environment-acceptance-v1-20261028/lower-voltage-evidence.json'
AUDIT_SHA256 = '010f09bd4ad3b1f38e92bbc2913074ace2f7a253347fa728283757c3b0494f74'
TARGET_VOLTAGE, TARGET_TIER = 'QCV', shared.TIERS['QCV']
KEYS = shared.KEYS


def lower_evidence():
    index_raw, index_sha, index_stamp = shared._snapshot(INDEX)
    mapping_raw, mapping_sha, mapping_stamp = shared._snapshot(MAPPING)
    audit_raw, audit_sha, audit_stamp = shared._snapshot(AUDIT)
    if audit_sha != AUDIT_SHA256:
        raise ValueError('逐格原审计证据已变化，须重新确认')
    index, audit = json.loads(index_raw), json.loads(audit_raw)
    mapping = shared._mapping(mapping_raw)
    if mapping.get('I44') != TARGET_VOLTAGE or mapping_sha != audit['voltage_mapping_sha256']:
        raise ValueError('I44电压或原审计映射发生变化')
    entries = {entry['id']: entry for entry in index['entries']}
    if len(entries) != len(index['entries']) or len({e['key'] for e in entries.values()}) != len(entries):
        raise ValueError('当前批准索引存在重复ID或key')
    for entry in entries.values():
        voltage = entry.get('target_voltage_appearance') or entry.get('target_voltage') or mapping.get(entry['id'])
        if voltage not in shared.TIERS or voltage != mapping.get(entry['id']):
            raise ValueError(('批准索引与电压映射冲突', entry['id']))
    expected = {key for key in entries if shared.TIERS[mapping[key]] < TARGET_TIER}
    rows = [dict(row) for row in audit['lower_forms'] if shared.TIERS[row['voltage']] < TARGET_TIER]
    if not rows or len(rows) != len({r['id'] for r in rows}) or {r['id'] for r in rows} != expected:
        raise ValueError('全部已批准QCV低阶未被原逐格审计完整覆盖')
    watched = {INDEX: index_stamp, MAPPING: mapping_stamp, AUDIT: audit_stamp}
    hashed_bytes = 0
    for row in rows:
        entry = entries[row['id']]
        if (row['key'] != entry['key'] or row['voltage'] != mapping[row['id']]
                or row['tier'] != shared.TIERS[row['voltage']]
                or not entry.get('formal_resource_present') or not entry.get('game_files_installed')
                or row['approval_quote'] != entry.get('approval_quote')):
            raise ValueError(('QCV低阶身份、正式状态或批准变化', row['id']))
        meta_path = shared._resolve(row['metadata'])
        if not meta_path.is_relative_to(shared.FORMAL.resolve()):
            raise ValueError('低阶元数据不在正式资源目录')
        meta_raw, meta_sha, watched[meta_path] = shared._snapshot(meta_path)
        meta = json.loads(meta_raw)
        blueprint = shared._resolve(meta['source'])
        if (meta_sha != row['metadata_sha256'] or meta['key'] != row['key']
                or blueprint != shared._resolve(row['blueprint']) or meta['sha256'] != row['blueprint_sha256']):
            raise ValueError(('低阶正式元数据或蓝图身份变化', row['id']))
        blueprint_sha, watched[blueprint] = shared._digest(blueprint)
        if blueprint_sha != row['blueprint_sha256']:
            raise ValueError(('低阶蓝图逐格原证据失效', row['id']))
        metrics, size, bounds, ordinary = row['metrics'], row['actual_xyz'], row['bounds_xyz'], row['ordinary_states']
        if (set(metrics) != set(KEYS) or any(type(metrics[k]) is not int or metrics[k] <= 0 for k in KEYS)
                or len(size) != 3 or size != [b-a+1 for a, b in zip(bounds['min'], bounds['max'])]
                or metrics['height'] != size[1] or metrics['volume'] != math.prod(size)
                or metrics['materials'] != len(set(ordinary))
                or row['total_palette_count'] != metrics['materials'] + 2
                or row['excluded_marker_cells']['controller'] != 1
                or any(s.split('[', 1)[0] in {'hk3gtl:industrial_port_casing',
                    'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'} for s in ordinary)):
            raise ValueError(('低阶数量、边界或普通材料统计冲突', row['id']))
        for declared in (meta.get('size_xyz') or meta.get('size'), entry.get('size_xyz')):
            if declared and any(actual > limit for actual, limit in zip(size, declared)):
                raise ValueError(('低阶实际边界超出声明', row['id']))
        for count in (meta.get('blocks'), entry.get('block_count')):
            if count is not None and count != metrics['blocks']:
                raise ValueError(('低阶方块数与正式元数据冲突', row['id']))
        hashed_bytes += watched[meta_path][0] + watched[blueprint][0]
    if any(shared._stamp(path) != stamp for path, stamp in watched.items()):
        raise ValueError('核验期间批准索引、映射或正式证据变化')
    maxima = {key: dict(value=max(r['metrics'][key] for r in rows),
        ids=[r['id'] for r in rows if r['metrics'][key] == max(q['metrics'][key] for q in rows)]) for key in KEYS}
    total_max = max(r['total_palette_count'] for r in rows)
    return dict(target_voltage=TARGET_VOLTAGE, target_tier=TARGET_TIER,
        lower_form_count=len(rows), formal_lower_count=len(rows), approved_pending_lower_count=0,
        lower_forms=rows, lower_maxima=maxima,
        lower_total_palette_maximum=dict(value=total_max,
            ids=[r['id'] for r in rows if r['total_palette_count'] == total_max]),
        minimum_strict_metrics={key: maxima[key]['value'] + 1 for key in KEYS},
        approval_index_sha256=index_sha, voltage_mapping=str(MAPPING.relative_to(ROOT)),
        voltage_mapping_sha256=mapping_sha, source_audit=str(AUDIT.relative_to(ROOT)),
        source_audit_sha256=audit_sha, hashed_source_bytes=hashed_bytes,
        material_count_scope='普通材料排除钻石主控和工业接口；总材料数另列，不能以重复状态凑种类。',
        evidence_method='复用已逐格审计的实际实体数据，按当次批准索引和映射过滤全部QCV低阶，重新流式核验正式元数据及蓝图哈希。',
        comparison='只比较已批准且电压低于QCV的24形态；同阶、更高阶与未批准草稿不计入。')


def validate_progression(metrics):
    if set(metrics) != set(KEYS) or any(type(metrics[k]) is not int or metrics[k] <= 0 for k in KEYS):
        raise ValueError('须提供blocks/materials/volume/height四项实际正整数；materials排除主控和接口标记')
    evidence = lower_evidence()
    checks = {key: metrics[key] > evidence['lower_maxima'][key]['value'] for key in KEYS}
    if not all(checks.values()):
        raise ValueError(('QCV候选未严格超过全部已批准低阶', metrics, evidence['lower_maxima'], checks))
    return dict(evidence, metrics=dict(metrics), strict_checks=checks, passes=checks, passed=True)


progression = validate_progression
