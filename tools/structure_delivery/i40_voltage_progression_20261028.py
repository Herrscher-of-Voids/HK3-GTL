# -*- coding: utf-8 -*-
"""I40 WFV候选的全部现役低电压结构比较，流式核对实际实体及源文件身份。

变更记录 #1 2026-10-28 Asia/Hong_Kong：新增独立WFV比较；不引用旧I37或未批准草稿。
普通材料不计主控所在格与工业接口标记；每种完整方块状态计一种，与体素源统计一致。
"""
import hashlib
import json
import math
import re
from functools import lru_cache
from pathlib import Path
from project_paths import project_path

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / 'src/main/resources/data/hk3gtl/structures/approved'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MAPPING = ROOT / 'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html'
TIERS = {name: i + 14 for i, name in enumerate(
    'MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split())}
KEYS = ('blocks', 'materials', 'volume', 'height')
CELL = re.compile(rb'\{\s*"pos"\s*:\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\]\s*,\s*"state"\s*:\s*"([^"\\]+)"\s*\}')
AIR = {b'minecraft:air', b'minecraft:cave_air', b'minecraft:void_air'}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def resolve(value):
    path = project_path(value)
    if path.exists():
        return path.resolve()
    if not Path(value).is_absolute() and str(value).replace('\\', '/').startswith('data/hk3gtl/'):
        path = ROOT / 'src/main/resources' / value
    if not path.exists():
        raise ValueError(('正式证据文件不存在', str(value)))
    return path


def _mapping():
    text = MAPPING.read_text(encoding='utf-8')
    result = {}
    for voltage, body in re.findall(r'<tr><td class="tier">([A-Z]+)<br>(.*?)</tr>', text, re.S):
        if voltage in TIERS:
            for machine in re.findall(r'<span class="chip">([ISHW]\d+(?:-\d+)?)\s', body):
                if machine in result:
                    raise ValueError(('正式映射重复', machine))
                result[machine] = voltage
    if result.get('I40') != 'WFV':
        raise ValueError('I40的正式候选映射已变化，须重新确认比较目标')
    return result


def _scan_blueprint(path, controller):
    value = hashlib.sha256()
    count, controller_count, port_count = 0, 0, 0
    minimum, maximum = [math.inf] * 3, [-math.inf] * 3
    ordinary, all_states, carry = set(), set(), b''
    controller = tuple(controller)
    with path.open('rb') as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            value.update(chunk)
            data = carry + chunk
            end = data.rfind(b'}') + 1
            if not end:
                carry = data
                continue
            for match in CELL.finditer(data, 0, end):
                x, y, z = int(match[1]), int(match[2]), int(match[3])
                state = match[4]
                base = state.split(b'[', 1)[0]
                if base in AIR:
                    continue
                count += 1
                position = (x, y, z)
                if x < minimum[0]: minimum[0] = x
                if y < minimum[1]: minimum[1] = y
                if z < minimum[2]: minimum[2] = z
                if x > maximum[0]: maximum[0] = x
                if y > maximum[1]: maximum[1] = y
                if z > maximum[2]: maximum[2] = z
                all_states.add(state)
                if position == controller:
                    controller_count += 1
                elif base == b'hk3gtl:industrial_port_casing':
                    port_count += 1
                else:
                    ordinary.add(state)
            carry = data[end:]
    if not count or controller_count != 1:
        raise ValueError(('正式蓝图未读取到唯一主控', str(path), count, controller_count))
    actual = [int(high - low + 1) for low, high in zip(minimum, maximum)]
    return {
        'sha256': value.hexdigest(), 'actual_xyz': actual,
        'bounds_xyz': {'min': minimum, 'max': maximum},
        'metrics': dict(blocks=count, materials=len(ordinary), volume=math.prod(actual), height=actual[1]),
        'total_palette_count': len(all_states),
        'ordinary_states': sorted(state.decode('utf-8') for state in ordinary),
        'excluded_marker_cells': {'controller': controller_count, 'industrial_ports': port_count},
    }


@lru_cache(maxsize=1)
def lower_evidence():
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    mapping = _mapping()
    entries = {entry['key']: entry for entry in index['entries']}
    metas = sorted(FORMAL.glob('*.json'))
    if len(metas) != index['formal_structure_forms']:
        raise ValueError(('正式元数据数与批准索引不符', len(metas), index['formal_structure_forms']))
    rows, excluded, hashed_bytes = [], [], 0
    for path in metas:
        meta = json.loads(path.read_text(encoding='utf-8'))
        entry = entries[meta['key']]
        machine = entry['id']
        voltage = meta.get('target_voltage') or entry.get('target_voltage_appearance') or entry.get('target_voltage') or mapping.get(machine)
        if voltage not in TIERS or voltage != mapping.get(machine):
            raise ValueError(('正式电压依据冲突或缺失', machine, voltage, mapping.get(machine)))
        if TIERS[voltage] >= TIERS['WFV']:
            excluded.append(dict(id=machine, voltage=voltage, reason='同阶或更高阶'))
            continue
        if not entry['formal_resource_present'] or not entry['game_files_installed']:
            raise ValueError(('索引并未确认现役安装', machine))
        blueprint = resolve(meta['source'])
        stats = _scan_blueprint(blueprint, meta['controller'])
        if stats.pop('sha256') != meta['sha256']:
            raise ValueError(('正式蓝图SHA256与元数据不符', machine, str(blueprint)))
        if meta.get('blocks', entry.get('block_count', stats['metrics']['blocks'])) != stats['metrics']['blocks']:
            raise ValueError(('正式蓝图实体数与元数据不符', machine))
        declared = meta.get('size_xyz') or meta.get('size')
        if declared and not all(a >= b for a, b in zip(declared, stats['actual_xyz'])):
            raise ValueError(('真实边界超出声明尺寸', machine, declared, stats['actual_xyz']))
        rows.append(dict(id=machine, key=meta['key'], voltage=voltage, tier=TIERS[voltage],
            status='formal_installed', metadata=str(path.relative_to(ROOT)), metadata_sha256=digest(path),
            blueprint=str(blueprint.relative_to(ROOT)), blueprint_sha256=meta['sha256'],
            approval_quote=entry['approval_quote'], **stats))
        hashed_bytes += blueprint.stat().st_size + path.stat().st_size
    if len(rows) != len({row['id'] for row in rows}) or not rows:
        raise ValueError('低阶比较集合为空或包含重复形态')
    expected = {entry['id'] for entry in index['entries']
        if mapping.get(entry['id']) in TIERS and TIERS[mapping[entry['id']]] < TIERS['WFV']}
    if {row['id'] for row in rows} != expected:
        raise ValueError(('已批准低阶集合存在未纳入的形态', sorted(expected - {row['id'] for row in rows})))
    maxima = {key: dict(value=max(row['metrics'][key] for row in rows),
        ids=[row['id'] for row in rows if row['metrics'][key] == max(r['metrics'][key] for r in rows)]) for key in KEYS}
    return dict(source=str(FORMAL.relative_to(ROOT)), formal_metadata_count=len(metas),
        target_voltage='WFV', target_tier=27, lower_form_count=len(rows), formal_lower_count=len(rows),
        approved_pending_lower_count=0, lower_forms=rows, lower_maxima=maxima,
        minimum_strict_metrics={key: maxima[key]['value'] + 1 for key in KEYS},
        approval_index_sha256=digest(INDEX), voltage_mapping=str(MAPPING.relative_to(ROOT)),
        voltage_mapping_sha256=digest(MAPPING), hashed_source_bytes=hashed_bytes, exclusions=excluded,
        material_count_scope='普通完整方块状态种类数；排除唯一主控格及hk3gtl:industrial_port_casing标记，不将二者计入材料递增。',
        evidence_method='逐份流式读取现役正式蓝图，重新统计实体、真实坐标边界、普通材料并同步核对SHA256；不读取未批准草稿。',
        comparison='严格超过全部现役较低电压形态；I37没有正式元数据且未批准，不计入。')


def progression(metrics):
    if set(metrics) != set(KEYS) or not all(type(metrics[key]) is int and metrics[key] > 0 for key in KEYS):
        raise ValueError('必须提供blocks/materials/volume/height四项正整数实际指标；materials须为排除标记的普通材料数')
    evidence = lower_evidence()
    passes = {key: metrics[key] > evidence['lower_maxima'][key]['value'] for key in KEYS}
    if not all(passes.values()):
        raise ValueError(('WFV候选未严格超过全部较低阶', metrics, evidence['lower_maxima']))
    return dict(evidence, metrics=dict(metrics), passes=passes, passed=True)


if __name__ == '__main__':
    import sys
    result = lower_evidence() if len(sys.argv) == 1 else progression(json.loads(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
