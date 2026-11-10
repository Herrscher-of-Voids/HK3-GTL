# -*- coding: utf-8 -*-
"""修订182：第十批完整建筑逐格提升；分块与位图避免巨型坐标对象集合。"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import mmap
from pathlib import Path
from project_paths import project_path
import shutil
import struct
import subprocess
import sys
import time

import numpy as np
import build_late_approved_resources_20261026 as nbt

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/i43-i45-terminal-demolition-20261030'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
MACHINES = {
    'I40': ('i40_civilization_wonder_material_synthesis_center', 'WFV'),
    'I41': ('i41_civilization_energy_dispatch_hub', 'IWV'),
    'I42': ('i42_wonder_component_prefabrication_factory', 'WFV'),
    'I43': ('i43_civilization_engineering_acceptance_center', 'WSV'),
    'I44': ('i44_imitation_thousand_realms_beacon', 'QCV'),
    'I45': ('i45_imitation_thousand_realms_train', 'QCV'),
}
VERSIONS = dict(I40='V1', I41='V3', I42='V1', I43='V1', I44='V2', I45='V2')
GROUPS = {
    'I40': {'导能晶片与带材进料':'item_input', '导能晶片与带材成品交接':'item_output',
        '约束陶瓷与隔离件进料':'item_input', '约束陶瓷与隔离件成品交接':'item_output',
        '自组织复材与预制件进料':'item_input', '自组织复材与预制件成品交接':'fluid_output',
        '认知信息载体与传感阵列进料':'item_input', '认知信息载体与传感阵列成品交接':'item_output',
        '合法供能':'energy_input', '稳定介质':'fluid_input', '质检记录':'item_output', '维护回执':'maintenance'},
    'I41': {'I38合法入账记录':'item_input', '绑定人授权输入':'item_input', '已登记负载输入':'item_input',
        '授权调度回执':'item_output', '告警与历史查询':'research', '维护物资交接':'maintenance'},
    'I42': {'魂钢精密骨架输入':'item_input', 'I40专用材料输入':'item_input', '导能元件输入':'item_input',
        '预制工艺介质输入':'fluid_input', '专用预制构件交接':'item_output', '边角料分类回收':'item_output',
        '图样与授权核验':'research', '维护及流体汇接':'fluid_output'},
    'I43': {'工程样件输入':'item_input', '热工测试介质':'fluid_input', '流体测试介质':'fluid_input',
        '供能负载接入':'energy_input', '计量校准输入':'item_input', '故障样件交接':'item_output',
        '运行记录核验':'research', '报告与档案交接':'item_output'},
    'I44': {'坐标数据登记':'item_input', '有效坐标复测':'item_input', '无人任务调度':'item_output',
        '站场供能':'energy_input', '冷却介质输入':'fluid_input', '冷却介质返回':'fluid_output',
        'I45目的地联锁':'research', '观测设备维护':'maintenance'},
    'I45': {'EU-IN':'energy_input', 'COAL-IN':'item_input', 'WATER-IN':'fluid_input',
        'STEAM-SERVICE':'maintenance', 'COORD-IN':'research', 'AUTH-IN':'research',
        'ARRIVAL-OUT':'item_output', 'RECOVERY-OUT':'item_output'},
}
CHUNK = 65536
FIXED = np.dtype([('head', 'V11'), ('pos', '>i4', (3,)), ('tag', 'V8'),
                  ('state', '>i4'), ('end', 'u1')])
PREVIEW = np.dtype([('linear', '>i4'), ('state', '>u2'), ('length', '>i4')])
HEAD = np.void(b'\x09\x00\x03pos\x03\x00\x00\x00\x03')
STATE = np.void(b'\x03\x00\x05state')


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def approved_source(ident):
    entries = json.loads(INDEX.read_text(encoding='utf-8'))['entries']
    rows = [row for row in entries if row['id'] == ident]
    assert len(rows) == 1 and rows[0]['approved_version'] == VERSIONS[ident]
    row = rows[0]
    assert row['counts_as_new_machine'] and (row['source_candidate_approved_field'] or
                                           row.get('external_approval_is_authoritative'))
    folder = project_path(row['archive'])
    approval = json.loads(project_path(row['approval_manifest']).read_text(encoding='utf-8'))
    for relative, digest in approval['source_files_sha256'].items():
        assert nbt.sha(folder / relative) == digest, ('批准档案发生变化', ident, relative)
    assert nbt.sha(row['archive_zip']) == row['archive_zip_sha256']
    meta = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    assert meta['target_voltage'] == MACHINES[ident][1]
    assert {port['id'] for port in meta['ports']} == set(GROUPS[ident])
    candidates = list(folder.rglob('*.nbt'))
    assert len(candidates) == 1
    assert nbt.sha(candidates[0]) == row['approved_nbt_sha256']
    return folder, meta, candidates[0], approval['source_files_sha256']


def header(raw):
    assert raw[0] == 10
    _, at = nbt.text(raw, 1)
    fields = {}
    while raw[at]:
        kind = raw[at]
        name, start = nbt.text(raw, at+1)
        if name == 'blocks':
            assert kind == 9 and raw[start] == 10
            return fields, start, nbt.I32.unpack_from(raw, start+1)[0]
        at = nbt.skip(raw, start, kind)
        fields[name] = (start, at)
    raise AssertionError('源NBT缺少blocks')


def chunks(raw, start, count):
    at = start+5
    for offset in range(0, count, CHUNK):
        number = min(CHUNK, count-offset)
        end = at+number*36
        records = np.frombuffer(raw, dtype=FIXED, count=number, offset=at) if end <= len(raw) else None
        if records is not None and (records['head'] == HEAD).all() and (records['tag'] == STATE).all() and not records['end'].any():
            yield offset, at, end, records['pos'].copy(), records['state'].copy(), None
            at = end
        else:
            # 可变记录逐格解析，完整保留任何实体复合标签，不能用固定步长跳过。
            records = None
            begin, positions, states, spans = at, [], [], []
            for _ in range(number):
                a, at, pos, state, state_at, entity = nbt.block(raw, at)
                positions.append(pos)
                states.append(state)
                spans.append((a, at, state_at, entity))
            yield offset, begin, at, np.asarray(positions, dtype=np.int32), np.asarray(states, dtype=np.int32), spans


def payloads(raw, start, end, positions, states, spans, targets, final_palette):
    changed = []
    for index, (pos, state) in enumerate(zip(positions.tolist(), states.tolist())):
        key = tuple(pos)
        if key not in targets:
            continue
        a, b, _, _, state_at, entity = nbt.block(raw, start+index*36) if spans is None else (*spans[index][:2], None, None, *spans[index][2:])
        target, face, role, palette_id = targets[key]
        original = bytearray(raw[a:b])
        nbt.I32.pack_into(original, state_at-a, palette_id)
        if target != 'hk3gtl:industrial_port_casing':
            assert entity is None, ('替换格已有实体NBT，需要明确迁移', key)
            original = original[:-1]+b'\x0a\x00\x03nbt'+nbt.string_tag('id', target)+b'\x00\x00'
        _, finish, actual_pos, actual_state, _, be = nbt.block(original, 0)
        assert finish == len(original) and actual_pos == key and actual_state == palette_id
        if target != 'hk3gtl:industrial_port_casing':
            assert original[be:nbt.skip(original, be, 10)] == nbt.string_tag('id', target)+b'\x00'
        changed.append((index, a, b, bytes(original)))
    pieces, at = [], start
    for _, a, b, replacement in changed:
        pieces.extend((raw[at:a], replacement))
        at = b
    pieces.append(raw[at:end])
    return b''.join(pieces), changed


def json_rows(positions, states, palette, offset):
    return ''.join((',' if offset+i else '')+'{"pos":['+str(x)+','+str(y)+','+str(z)+
                   '],"state":'+palette[state]+'}\n'
                   for i, ((x, y, z), state) in enumerate(zip(positions.tolist(), states.tolist()))).encode('utf-8')


def preview_rows(raw, start, positions, states, spans, changed, size):
    linear = (positions[:, 0].astype(np.int64)*size[1]+positions[:, 1])*size[2]+positions[:, 2]
    records = np.zeros(len(states), dtype=PREVIEW)
    records['linear'], records['state'] = linear, states
    entities = {}
    if spans is not None:
        for i, (_, _, _, entity) in enumerate(spans):
            if entity is not None:
                entities[i] = b'\x0a\x00\x00'+raw[entity:nbt.skip(raw, entity, 10)]
    for i, _, _, payload in changed:
        _, _, _, state, _, entity = nbt.block(payload, 0)
        records['state'][i] = state
        if entity is not None:
            entities[i] = b'\x0a\x00\x00'+payload[entity:nbt.skip(payload, entity, 10)]
    if not entities:
        return records.tobytes(), 0, linear
    pieces, at = [], 0
    for i in sorted(entities):
        records['length'][i] = len(entities[i])
        pieces.extend((records[at:i+1].tobytes(), entities[i]))
        at = i+1
    pieces.append(records[at:].tobytes())
    return b''.join(pieces), len(entities), linear


def build(ident):
    begin = time.monotonic()
    folder, meta, source, approval_hashes = approved_source(ident)
    key, machine = ident.lower(), 'hk3gtl:'+MACHINES[ident][0]
    size, controller = meta['size'], meta['controller']
    ports = [dict(port, group=GROUPS[ident][port['id']]) for port in meta['ports']]
    targets = {tuple(controller):(machine, meta.get('controller_face', 'north'), 'controller')}
    for port in ports:
        pos = tuple(port['pos'])
        assert pos not in targets
        targets[pos] = (nbt.HATCHES.get(port['group'], 'hk3gtl:industrial_port_casing'), port['face'], port['id'])
    LOG.mkdir(parents=True, exist_ok=True)
    expanded = LOG / (key+'-source.tasktmp')
    output = RES / 'structures/approved' / (key+'.nbt')
    layout = RES / 'approved_architecture' / (key+'.json')
    preview = RES / 'structures/approved_preview' / (key+'.bin.gz')
    for path in (output, layout, preview):
        path.parent.mkdir(parents=True, exist_ok=True)
    temps = [path.with_suffix(path.suffix+'.tasktmp') for path in (output, layout, preview)]
    source_sha = nbt.sha(source)
    try:
        with gzip.open(source, 'rb') as inp, expanded.open('wb') as out:
            shutil.copyfileobj(inp, out, 4*1024*1024)
        with ExitStack() as stack:
            inp = stack.enter_context(expanded.open('rb'))
            raw = stack.enter_context(mmap.mmap(inp.fileno(), 0, access=mmap.ACCESS_READ))
            fields, blocks_start, count = header(raw)
            assert count == meta['blocks']
            assert list(struct.unpack_from('>iii', raw, fields['size'][0]+5)) == size
            original_palette = nbt.palette(raw, fields['palette'])
            final_palette = original_palette.copy()
            for pos, (target, face, role) in list(targets.items()):
                state = target+('[facing='+face+']' if target != 'hk3gtl:industrial_port_casing' else '')
                if state not in final_palette:
                    final_palette.append(state)
                targets[pos] = (target, face, role, final_palette.index(state))
            assert len(final_palette) <= 65535
            prefix = (raw[:fields['palette'][0]]+b'\x0a'+nbt.I32.pack(len(final_palette))+
                      b''.join(nbt.palette_tag(state) for state in final_palette)+raw[fields['palette'][1]:blocks_start+5])
            js_header = ('{"key":'+json.dumps(key)+',"size":'+json.dumps(size)+',"controller":'+
                         json.dumps(controller)+',"blocks":[\n').encode('utf-8')
            js_tail = ('],"ports":'+json.dumps(ports, ensure_ascii=False, separators=(',', ':'))+'}').encode('utf-8')
            pv_header = b'HK3P'+nbt.I32.pack(1)+struct.pack('>6i', *size, *controller)+nbt.I32.pack(count)+nbt.U16.pack(len(final_palette))
            for state in final_palette:
                encoded = state.encode('ascii')
                pv_header += nbt.U16.pack(len(encoded))+encoded
            json_palette = [json.dumps(state, ensure_ascii=False) for state in original_palette]
            volume = int(np.prod(size))
            assert volume <= 2147483647
            occupied = np.zeros((volume+7)//8, dtype=np.uint8)
            counts = np.zeros(len(original_palette), dtype=np.int64)
            low, high = np.asarray(size), np.zeros(3, dtype=np.int32)
            found, changes, entities, records_digest = set(), [], 0, hashlib.sha256()
            out = stack.enter_context(gzip.open(temps[0], 'wb', compresslevel=6))
            js = stack.enter_context(temps[1].open('wb'))
            pv_file = stack.enter_context(temps[2].open('wb'))
            pv = stack.enter_context(gzip.GzipFile(fileobj=pv_file, mode='wb', compresslevel=6, mtime=0))
            out.write(prefix); js.write(js_header); pv.write(pv_header)
            for offset, a, b, pos, state, spans in chunks(raw, blocks_start, count):
                assert ((pos >= 0) & (pos < size)).all()
                assert ((state >= 0) & (state < len(original_palette))).all()
                low, high = np.minimum(low, pos.min(axis=0)), np.maximum(high, pos.max(axis=0))
                counts += np.bincount(state, minlength=len(original_palette))
                payload, changed = payloads(raw, a, b, pos, state, spans, targets, final_palette)
                compact, entity_count, linear = preview_rows(raw, a, pos, state, spans, changed, size)
                assert len(np.unique(linear)) == len(linear), '块内重复坐标'
                byte, bit = linear//8, (1 << (linear%8)).astype(np.uint8)
                assert not (occupied[byte] & bit).any(), '块间重复坐标'
                np.bitwise_or.at(occupied, byte, bit)
                rows_palette = json_palette
                json_state = state.copy()
                for i, _, _, replacement in changed:
                    position = tuple(pos[i].tolist())
                    assert position not in found
                    found.add(position)
                    target, _, role, palette_id = targets[position]
                    original = original_palette[state[i]]
                    assert original == ('minecraft:diamond_block' if position == tuple(controller) else 'hk3gtl:industrial_port_casing')
                    changes.append(dict(pos=list(position), role=role, **{'from':original},
                                        to=final_palette[palette_id], block_entity_id=target))
                    if position == tuple(controller):
                        if rows_palette is json_palette:
                            rows_palette = json_palette+[json.dumps(machine)]
                        json_state[i] = len(json_palette)
                out.write(payload); js.write(json_rows(pos, json_state, rows_palette, offset)); pv.write(compact)
                records_digest.update(compact); entities += entity_count
            assert found == set(targets)
            blocks_end = b
            at = blocks_end
            while raw[at]:
                kind = raw[at]; _, start = nbt.text(raw, at+1); at = nbt.skip(raw, start, kind)
            assert at+1 == len(raw)
            suffix = raw[blocks_end:]
            out.write(suffix); js.write(js_tail)
            out.close(); js.close(); pv.close(); pv_file.close()
            assert low.tolist() == [0, 0, 0] and (high+1).tolist() == size, '实体边界与声明尺寸不同'
            del occupied
            # 独立回读三种格式：逐块比对，包含未替换记录的每个原始NBT字节与全部实体标签。
            with gzip.open(temps[0], 'rb') as check, temps[1].open('rb') as json_check, gzip.open(temps[2], 'rb') as preview_check:
                assert check.read(len(prefix)) == prefix
                assert json_check.read(len(js_header)) == js_header
                assert preview_check.read(len(pv_header)) == pv_header
                verified = hashlib.sha256()
                for offset, a, b, pos, state, spans in chunks(raw, blocks_start, count):
                    payload, changed = payloads(raw, a, b, pos, state, spans, targets, final_palette)
                    assert check.read(len(payload)) == payload, ('正式NBT逐格字节不一致', offset)
                    json_state, rows_palette = state.copy(), json_palette
                    for i, _, _, _ in changed:
                        if tuple(pos[i]) == tuple(controller):
                            rows_palette = json_palette+[json.dumps(machine)]
                            json_state[i] = len(json_palette)
                    rows = json_rows(pos, json_state, rows_palette, offset)
                    assert json_check.read(len(rows)) == rows, ('JSON逐格几何状态不一致', offset)
                    compact, _, _ = preview_rows(raw, a, pos, state, spans, changed, size)
                    actual = preview_check.read(len(compact))
                    assert actual == compact, ('预览逐格坐标状态实体NBT不一致', offset)
                    verified.update(actual)
                assert check.read() == suffix and json_check.read() == js_tail and preview_check.read() == b''
                assert verified.hexdigest() == records_digest.hexdigest()
        assert nbt.sha(source) == source_sha
        for path, digest in approval_hashes.items():
            assert nbt.sha(folder / path) == digest, ('生成期间批准档案改变', path)
        for temporary, destination in zip(temps, (output, layout, preview)):
            temporary.replace(destination)
    finally:
        expanded.unlink(missing_ok=True)
    diamonds = int(counts[original_palette.index('minecraft:diamond_block')])
    record = dict(key=key, machine=machine, source='data/hk3gtl/approved_architecture/'+key+'.json',
        sha256=nbt.sha(layout), template_sha256=nbt.sha(output), source_snapshot=str(folder),
        source_metadata=str(folder / 'manifest.json'), source_nbt=str(source), source_nbt_sha256=source_sha,
        controller=controller, size_xyz=size, blocks=count, ports=ports, target_voltage=MACHINES[ident][1],
        installed_hatches={p['id']:p['group'] for p in ports if p['group'] in nbt.HATCHES},
        required_abilities=sorted({p['group'] for p in ports if p['group'] in nbt.HATCHES}),
        game_verified=False, revision=182, materials=int(np.count_nonzero(counts)), source_diamond_count=diamonds,
        preserved_other_diamonds=diamonds-1, changes=changes, geometry_nbt_json_per_block_verified=True,
        all_other_cells_unchanged=True, port_positions_faces_purposes_preserved=True, dense_volume_materialized=False,
        controller_nbt_blockentity_id=machine, approved_version=VERSIONS[ident], external_approval_is_authoritative=True,
        source_manifest_approved_field_preserved=True, actual_bounds_xyz=dict(min=low.tolist(), max=high.tolist()),
        process_scope='完整批准建筑、主控、原位物品流体仓与全高JEI预览；能源、维护和研究接口保留占位，不声明能源调度或旅行逻辑已实现。')
    save(output.with_suffix('.json'), record)
    save(LOG / (key+'-verification.json'), record)
    preview_record = dict(key=key, source_nbt_sha256=record['template_sha256'], preview_sha256=nbt.sha(preview),
        size_xyz=size, controller=controller, blocks=count, block_entities=entities, palette=len(final_palette),
        volume=volume, compressed_bytes=preview.stat().st_size, standard_array_references=volume,
        array_reference_bytes_at_4_bytes=volume*4, all_coordinates_states_and_entity_nbt_verified=True,
        records_sha256=records_digest.hexdigest())
    save(LOG / (key+'-compact-preview.json'), preview_record)
    print(json.dumps(dict(id=ident, blocks=count, seconds=round(time.monotonic()-begin, 2),
                          block_entities=entities, passed=True)), flush=True)


def write_summary():
    old = json.loads((LOG / 'existing-resources-before.json').read_text(encoding='utf-8'))
    assert sum('/structures/approved/' in name and name.endswith('.json') for name in old) == 46
    assert all(nbt.sha(ROOT / 'src/main/resources' / path) == digest for path, digest in old.items()), '既有46形态改变'
    rows = [json.loads((LOG / (ident.lower()+'-verification.json')).read_text(encoding='utf-8')) for ident in MACHINES]
    for ident, row in zip(MACHINES, rows):
        key = ident.lower()
        assert {port['id']:port['group'] for port in row['ports']} == GROUPS[ident]
        assert nbt.sha(RES / 'approved_architecture' / (key+'.json')) == row['sha256']
        assert nbt.sha(RES / 'structures/approved' / (key+'.nbt')) == row['template_sha256']
        assert json.loads((RES / 'structures/approved' / (key+'.json')).read_text(encoding='utf-8')) == row
        compact = json.loads((LOG / (key+'-compact-preview.json')).read_text(encoding='utf-8'))
        assert compact['source_nbt_sha256'] == row['template_sha256']
        assert nbt.sha(RES / 'structures/approved_preview' / (key+'.bin.gz')) == compact['preview_sha256']
    save(LOG / 'resource-generation.json', dict(status='passed', revision=182, package_revision=186,
        generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(), structures=rows,
        cells=sum(row['blocks'] for row in rows), existing_architecture_unchanged=True,
        existing_resource_sha256=old, existing_structure_forms_unchanged=46, complete_height_preserved=True,
        approved_versions=VERSIONS, game_verified=False, instance_modified_by_generator=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', choices=MACHINES)
    args = parser.parse_args()
    if args.key:
        build(args.key)
        return
    old = json.loads((LOG / 'existing-resources-before.json').read_text(encoding='utf-8'))
    assert all(nbt.sha(ROOT / 'src/main/resources' / path) == digest for path, digest in old.items())
    for ident in ('I45', 'I40', 'I41', 'I42', 'I43', 'I44'):
        subprocess.run([sys.executable, '-X', 'utf8', __file__, '--key', ident], check=True, cwd=ROOT)
    write_summary()


if __name__ == '__main__':
    main()
