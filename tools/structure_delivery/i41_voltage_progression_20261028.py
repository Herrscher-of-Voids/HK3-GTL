# -*- coding: utf-8 -*-
"""I41 IWV递增比较：复用已逐格审计证据，流式复核当前批准文件身份。

变更记录 #1 2026-10-28 Asia/Hong_Kong：新增I41独立比较；普通材料不计主控和工业接口标记。
"""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / 'src/main/resources/data/hk3gtl/structures/approved'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MAPPING = ROOT / 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html'
AUDIT = ROOT / 'logs/i40-cascade-foundry-20261028/lower-voltage-evidence.json'
AUDIT_SHA256 = 'c4947414b01b97a9389a8c6565aa062aa5b0ba61e5097a69d63e0fd27253a312'
TIERS = {name: i + 14 for i, name in enumerate(
    'MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}
KEYS = ('blocks', 'materials', 'volume', 'height')


def _stamp(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def _snapshot(path):
    before = _stamp(path)
    data = path.read_bytes()
    if before != _stamp(path):
        raise ValueError(('读取期间文件变化，请重新核验', str(path)))
    return data, hashlib.sha256(data).hexdigest(), before


def _digest(path):
    before = _stamp(path)
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    if before != _stamp(path):
        raise ValueError(('哈希期间源文件变化，请重新核验', str(path)))
    return value.hexdigest(), before


def _resolve(value):
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / ('src/main/resources' if str(value).replace('\\', '/').startswith('data/hk3gtl/') else '') / value
    if not path.exists():
        raise ValueError(('正式证据文件不存在', str(path)))
    return path.resolve()


def _mapping(data):
    result = {}
    for voltage, body in re.findall(r'<tr><td class="tier">([A-Z]+)<br>(.*?)</tr>', data.decode('utf-8'), re.S):
        if voltage in TIERS:
            for machine in re.findall(r'<span class="chip">([ISHW]\d+(?:-\d+)?)\s', body):
                if machine in result:
                    raise ValueError(('正式映射重复', machine))
                result[machine] = voltage
    if result.get('I41') != 'IWV':
        raise ValueError('I41正式映射已变化，须重新确认比较目标')
    return result


def lower_evidence():
    index_data, index_sha, index_stamp = _snapshot(INDEX)
    mapping_data, mapping_sha, mapping_stamp = _snapshot(MAPPING)
    audit_data, audit_sha, audit_stamp = _snapshot(AUDIT)
    if audit_sha != AUDIT_SHA256:
        raise ValueError('已逐格审计证据的SHA256变化，不能沿用原统计')
    audit = json.loads(audit_data)
    if mapping_sha != audit['voltage_mapping_sha256']:
        raise ValueError('电压映射已变化，原逐格证据须重新审查')
    index, mapping = json.loads(index_data), _mapping(mapping_data)
    entries = {entry['key']: entry for entry in index['entries']}
    if len(entries) != len(index['entries']) or len({entry['id'] for entry in entries.values()}) != len(entries):
        raise ValueError('当前批准索引存在重复key或形态ID')
    for entry in entries.values():
        voltage = entry.get('target_voltage_appearance') or entry.get('target_voltage') or mapping.get(entry['id'])
        if voltage not in TIERS or voltage != mapping.get(entry['id']):
            raise ValueError(('当前批准索引电压冲突或缺失', entry['id'], voltage))
    metas, watched = {}, {INDEX: index_stamp, MAPPING: mapping_stamp, AUDIT: audit_stamp}
    for path in sorted(FORMAL.glob('*.json')):
        data, sha, stamp = _snapshot(path)
        meta = json.loads(data)
        if meta['key'] in metas:
            raise ValueError(('正式元数据key重复', meta['key']))
        metas[meta['key']] = path, meta, sha
        watched[path] = stamp
    expected_formal = {key for key, entry in entries.items() if entry.get('formal_resource_present')}
    if len(metas) != index['formal_structure_forms'] or set(metas) != expected_formal:
        raise ValueError('当前正式元数据与批准索引覆盖不符')
    rows = [row for row in audit['lower_forms'] if TIERS[mapping[row['id']]] < TIERS['IWV']]
    expected = {entry['id'] for entry in entries.values() if TIERS[mapping[entry['id']]] < TIERS['IWV']}
    if len(rows) != len({row['id'] for row in rows}) or {row['id'] for row in rows} != expected or not rows:
        raise ValueError(('当前已批准低阶形态与逐格证据不符，须补审', sorted(expected - {row['id'] for row in rows})))
    hashed_bytes = 0
    for row in rows:
        entry = entries[row['key']]
        path, meta, metadata_sha = metas[row['key']]
        if entry['id'] != row['id'] or row['voltage'] != mapping[row['id']] or row['tier'] != TIERS[row['voltage']]:
            raise ValueError(('逐格证据身份或电压与当前索引不符', row['id']))
        if not entry.get('game_files_installed') or entry.get('approval_quote') != row['approval_quote']:
            raise ValueError(('低阶批准或安装状态发生变化', row['id']))
        if path.resolve() != _resolve(row['metadata']) or metadata_sha != row['metadata_sha256']:
            raise ValueError(('正式元数据已变化，须重新逐格审计', row['id']))
        blueprint = _resolve(meta['source'])
        if blueprint != _resolve(row['blueprint']) or meta['sha256'] != row['blueprint_sha256']:
            raise ValueError(('正式蓝图身份与审计证据不符', row['id']))
        sha, stamp = _digest(blueprint)
        if sha != row['blueprint_sha256']:
            raise ValueError(('正式蓝图内容已变化，须重新逐格审计', row['id']))
        watched[blueprint] = stamp
        hashed_bytes += stamp[0] + watched[path][0]
        metrics, size = row['metrics'], row['actual_xyz']
        bounds = row['bounds_xyz']
        if (set(metrics) != set(KEYS) or any(type(metrics[key]) is not int or metrics[key] <= 0 for key in KEYS)
                or size != [high - low + 1 for low, high in zip(bounds['min'], bounds['max'])]
                or metrics['height'] != size[1] or metrics['volume'] != math.prod(size)
                or metrics['materials'] != len(set(row['ordinary_states']))
                or row['excluded_marker_cells']['controller'] != 1
                or any(state.split('[', 1)[0] == 'hk3gtl:industrial_port_casing' for state in row['ordinary_states'])):
            raise ValueError(('逐格证据指标或普通材料口径不符', row['id']))
        for declared in (meta.get('size_xyz') or meta.get('size'), entry.get('size_xyz')):
            if declared and (len(declared) != 3 or any(actual > limit for actual, limit in zip(size, declared))):
                raise ValueError(('真实边界超出当前声明尺寸', row['id']))
        for count in (meta.get('blocks'), entry.get('block_count')):
            if count is not None and count != metrics['blocks']:
                raise ValueError(('实体数与当前元数据或索引不符', row['id']))
    if set(FORMAL.glob('*.json')) != {value[0] for value in metas.values()} or any(_stamp(path) != stamp for path, stamp in watched.items()):
        raise ValueError('核验期间索引、映射或正式源发生变化，请重新运行')
    if _snapshot(INDEX)[1] != index_sha or _snapshot(MAPPING)[1] != mapping_sha:
        raise ValueError('核验期间批准索引或电压映射内容变化，请重新运行')
    maxima = {key: dict(value=max(row['metrics'][key] for row in rows),
        ids=[row['id'] for row in rows if row['metrics'][key] == max(item['metrics'][key] for item in rows)]) for key in KEYS}
    excluded = [dict(id=entry['id'], voltage=mapping[entry['id']],
        reason='同阶' if TIERS[mapping[entry['id']]] == TIERS['IWV'] else '更高阶', status=entry['status'])
        for entry in entries.values() if TIERS[mapping[entry['id']]] >= TIERS['IWV']]
    if 'I37' not in {entry['id'] for entry in entries.values()}:
        excluded.append(dict(id='I37', reason='未批准，不读取旧草稿'))
    return dict(source=str(FORMAL.relative_to(ROOT)), formal_metadata_count=len(metas),
        target_voltage='IWV', target_tier=26, lower_form_count=len(rows), formal_lower_count=len(rows),
        approved_pending_lower_count=0, lower_forms=rows, lower_maxima=maxima,
        minimum_strict_metrics={key: maxima[key]['value'] + 1 for key in KEYS},
        approval_index_sha256=index_sha, voltage_mapping=str(MAPPING.relative_to(ROOT)),
        voltage_mapping_sha256=mapping_sha, source_audit=str(AUDIT.relative_to(ROOT)), source_audit_sha256=audit_sha,
        hashed_source_bytes=hashed_bytes, exclusions=excluded,
        material_count_scope=audit['material_count_scope'],
        evidence_method='复用已逐格审计的普通材料、实体和真实边界；逐份流式SHA256复核当前正式元数据和完整蓝图，按当前批准索引快照核对覆盖，未重新扫描体素。',
        comparison='严格超过全部已批准较低电压形态；同阶I01-4/I38、更高阶I40等与未批准I37不作为递增基线。')


def _compare(metrics, evidence):
    if set(metrics) != set(KEYS) or not all(type(metrics[key]) is int and metrics[key] > 0 for key in KEYS):
        raise ValueError('必须提供blocks/materials/volume/height四项正整数实际指标；materials为排除标记的普通材料数')
    passes = {key: metrics[key] > evidence['lower_maxima'][key]['value'] for key in KEYS}
    if not all(passes.values()):
        raise ValueError(('IWV候选未严格超过全部较低阶', metrics, evidence['lower_maxima']))
    return dict(evidence, metrics=dict(metrics), passes=passes, passed=True)


def progression(metrics):
    return _compare(metrics, lower_evidence())


def self_check():
    evidence = lower_evidence()
    minimum = evidence['minimum_strict_metrics']
    assert evidence['lower_form_count'] == 42
    assert minimum == dict(blocks=9720449, materials=41, volume=78989382, height=282)
    assert _compare(minimum, evidence)['passed']
    for key in KEYS:
        invalid = dict(minimum, **{key: minimum[key] - 1})
        try:
            _compare(invalid, evidence)
        except ValueError:
            continue
        raise AssertionError(('等于低阶最大值必须拒绝', key))
    return dict(passed=True, lower_form_count=evidence['lower_form_count'], minimum_strict_metrics=minimum,
        approval_index_sha256=evidence['approval_index_sha256'], hashed_source_bytes=evidence['hashed_source_bytes'],
        exclusions=evidence['exclusions'])


if __name__ == '__main__':
    import sys
    result = self_check() if sys.argv[1:] == ['--self-check'] else progression(json.loads(sys.argv[1])) if sys.argv[1:] else lower_evidence()
    print(json.dumps(result, ensure_ascii=False, indent=2))
