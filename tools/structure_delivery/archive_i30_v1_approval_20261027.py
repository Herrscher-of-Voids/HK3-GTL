# -*- coding: utf-8 -*-
"""I30 V1明确批准归档；直接复制现物，不重跑已变更的几何生成器。"""
from __future__ import annotations

import collections
import copy
import datetime as dt
import gc
import gzip
import hashlib
import html
import json
import struct
import zipfile
from pathlib import Path

import numpy as np

import archive_i23_v8_approval_20261025 as common
import build_late_approved_resources_20261026 as nbt
from structure_size_baseline import baselines

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I30_模拟世界泡稳定控制器_六脊稳界深井_V1_20261027'
DIALOGUE = ROOT / 'doc/HK3GTL-内测5/完整对话归档/2026-10-27_01-33-31_我靠，I30非常的好，直接到下一台_04c4b1c8e4.html'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-27_01-33-31_I30批准并继续I31.html'
APPROVED_AT = '2026-10-27T01:33:31.043+08:00'
QUOTE = '我靠，I30非常的好，直接到下一台'
SCOPE = 'I30 V1六脊稳界深井的建筑外观与对应结构文件获明确批准；正式Pattern、控制器注册绑定、仓室能力、配方、研究/生存获取、模拟批次运行和游戏成型均未验收。'


def state_tag(raw, bounds):
    p = bounds[0]; result = {}
    while raw[p]:
        kind = raw[p]; name, value = nbt.text(raw, p + 1)
        assert kind == 3
        result[name] = nbt.I32.unpack_from(raw, value)[0]
        p = nbt.skip(raw, value, kind)
    return result


def inspect_structure():
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['candidate_version'] == 'V1' and manifest['size'] == [365, 223, 365]
    assert manifest['target_voltage'] == 'ICV' and manifest['blocks'] == 3466331
    assert check['passed'] and all(check['voltage_progression']['passes'].values())
    nbt_path, = (SOURCE / 'i30').glob('*.nbt')
    schem_path, = (SOURCE / 'i30').glob('*.schem')
    assert common.digest(nbt_path) == check['nbt_schem_sha256']['nbt']
    assert common.digest(schem_path) == check['nbt_schem_sha256']['schem']
    raw = gzip.decompress(nbt_path.read_bytes()); fields = nbt.top(raw)
    size = list(struct.unpack_from('>iii', raw, fields['size'][0] + 5))
    assert size == manifest['size'] and nbt.I32.unpack_from(raw, fields['DataVersion'][0])[0] == 3465
    palette = nbt.palette(raw, fields['palette']); assert len(palette) == 39
    count = nbt.I32.unpack_from(raw, fields['blocks'][0] + 1)[0]
    assert count == manifest['blocks']
    dense = np.zeros(np.prod(size), dtype=np.uint8); counts = collections.Counter()
    low = [min(size)] * 3; high = [-1] * 3; control = tuple(manifest['controller'])
    at = fields['blocks'][0] + 5; ports = set(); control_count = 0
    for _ in range(count):
        _, at, pos, state, _, entity = nbt.block(raw, at)
        assert entity is None and 0 <= state < len(palette)
        assert all(0 <= pos[i] < size[i] for i in range(3))
        x, y, z = pos; linear = (y * size[2] + z) * size[0] + x
        assert dense[linear] == 0, 'NBT重复坐标'
        dense[linear] = state + 1; name = palette[state]; counts[name] += 1
        for i in range(3): low[i] = min(low[i], pos[i]); high[i] = max(high[i], pos[i])
        if name == 'minecraft:diamond_block':
            control_count += 1; assert pos == control
        elif name == 'hk3gtl:industrial_port_casing': ports.add(pos)
    assert at == fields['blocks'][1] and low == [0, 0, 0] and [n + 1 for n in high] == size
    assert dict(counts) == check['palette'] and control_count == 1
    assert ports == {tuple(p['pos']) for p in manifest['ports']} and len(ports) == 10
    minimum = baselines()['I30']['size']; assert minimum == [49, 57, 43]
    assert all(size[i] >= minimum[j] for i, j in ((0, 0), (1, 2), (2, 1)))
    del raw, fields; gc.collect()
    schematic = gzip.decompress(schem_path.read_bytes()); f = nbt.top(schematic)
    assert nbt.I32.unpack_from(schematic, f['Version'][0])[0] == 2
    assert nbt.I32.unpack_from(schematic, f['DataVersion'][0])[0] == 3465
    assert [struct.unpack_from('>h', schematic, f[k][0])[0] for k in ('Width', 'Height', 'Length')] == size
    sp = state_tag(schematic, f['Palette']); assert sp == dict({'minecraft:air': 0}, **{s: i + 1 for i, s in enumerate(palette)})
    begin = f['BlockData'][0]; length = nbt.I32.unpack_from(schematic, begin)[0]
    values = np.frombuffer(schematic, dtype=np.uint8, count=length, offset=begin + 4)
    assert length == dense.size and np.array_equal(values, dense), 'Schematic逐格回读不符'
    result = dict(size_xyz=size, size_wdh=[size[0], size[2], size[1]], baseline_wdh=minimum,
                  actual_bounds_equal_declared=True, blocks=count, materials=len(palette), controller=list(control),
                  port_count=10, nbt_file=str(nbt_path.relative_to(SOURCE)), schem_file=str(schem_path.relative_to(SOURCE)),
                  nbt_sha256=common.digest(nbt_path), schem_sha256=common.digest(schem_path),
                  nbt_schematic_per_block_equal=True, source_geometry_rerun=False, game_verified=False)
    del dense, values, schematic; gc.collect()
    return manifest, check, result


def main():
    before = INDEX.read_bytes(); index = json.loads(before)
    assert not any(row['id'] == 'I30' for row in index['entries']), 'I30已经归档，拒绝重复增加台数'
    assert index['pending_batch']['id'] == 'batch-08' and index['pending_batch']['count'] == 1 and index['pending_batch']['approved_machine_ids'] == ['I29']
    for ident in ('I27', 'I28'):
        row, = [r for r in index['entries'] if r['id'] == ident]
        assert row['game_files_installed'] is True and row['formal_resource_present'] is True
    manifest, check, verified = inspect_structure()
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    status = dict(approved=True, approval_scope=SCOPE, approved_at=APPROVED_AT, approval_quote=QUOTE,
                  formal_controller_integrated=False, game_files_installed=False, game_verified=False)
    common.write_json(SOURCE / '外观批准记录.json', status)
    for name, message in [('index.html', 'I30 V1外观及结构文件已批准；未接入游戏，正式Pattern、控制器绑定、配方和游戏运行仍待验收。'),
                          ('i30/三维评审.html', 'I30 V1外观已批准；这是批准结构评审，不代表游戏成型或运行验收。')]:
        path = SOURCE / name; text = path.read_text(encoding='utf-8')
        banner = f'<aside id="appearance-approval" style="padding:14px;margin:16px;background:#253c31;color:#edf9ef">{message}</aside>'
        assert 'appearance-approval' not in text
        text = text.replace('<header>', banner + '<header>', 1) if name.startswith('i30/') else text.replace('<h1>', banner + '<h1>', 1)
        text = text.replace('外观候选尚未批准、未接入实例。', '建筑外观已批准、尚未接入实例。')
        text = text.replace('候选尚未批准、未接入实例；', '建筑外观已批准、尚未接入实例；')
        path.write_text(text, encoding='utf-8')
    manifest.update(approved=True, status='appearance_approved_archived_waiting_batch', approval_scope=SCOPE,
                    approved_at=APPROVED_AT, game_files_installed=False, game_verified=False)
    common.write_json(SOURCE / 'manifest.json', manifest)
    hashes = common.file_hashes(SOURCE)
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_batch-08_02of05_I30_V1_ICV_外观已确认'
    evidence = snapshot / 'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence / 'previous-current-index.json').write_bytes(before)
    shutil = __import__('shutil')
    shutil.copy2(__file__, evidence / Path(__file__).name)
    target = snapshot / SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I29', 'I30'], count=2, required=5,
                   deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
                   game_files_installed=False, game_verified=False,
                   deployment_blockers=['当前新批准未接入机器为I29、I30，共2/5；I27/I28已按此前直接授权接入，不重复计数。'])
    row = dict(id='I30', key='i30', candidate_key='i30', approved_version='V1', candidate_version='V1',
               target_voltage_appearance='ICV', status='approved_archived_waiting_five_machine_threshold',
               approved_at=APPROVED_AT, approval_quote=QUOTE, approval_scope=SCOPE, source=str(SOURCE), archive=str(target),
               discussion_record=str(DISCUSSION), dialogue_archive=str(DIALOGUE), counts_as_new_machine=True,
               source_candidate_approved_field=True, formal_resource_present=False, game_files_installed=False,
               game_verified=False, structure_checks=verified, size_xyz=manifest['size'], block_count=manifest['blocks'],
               controller=manifest['controller'], port_count=10, nbt_sha256=verified['nbt_sha256'])
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong', original_user_message_time=APPROVED_AT,
                    entries=[row], source_files_sha256=hashes, accepted_design_scope=SCOPE,
                    pending_batch_after_archive=pending, previous_index_sha256=hashlib.sha256(before).hexdigest(),
                    prior_i27_i28_not_recounted=True, geometry_generator_executed=False,
                    game_files_installed=False, game_verified=False)
    common.write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I30 V1外观确认</title><style>body{{max-width:1050px;margin:30px auto;padding:0 20px;font:16px/1.8 system-ui}}a{{overflow-wrap:anywhere}}</style><h1>I30 V1外观已确认</h1><p>{html.escape(SCOPE)}</p><p>负责人：{html.escape(QUOTE)}（{APPROVED_AT}）</p><p>365×365×223格（宽×长×高）；3,466,331个方块、39种材料。现有NBT与Schematic逐格回读相等；最低49×57×43及真实实体范围检查通过。未重跑几何生成器。</p><p>batch-08当前2/5：I29、I30。I27/I28已直接授权接入，不重复计数。</p><p><a href="确认与校验清单.json">确认与校验清单</a> · <a href="{SOURCE.name}/index.html">批准版交付</a> · <a href="{SOURCE.name}/i30/三维评审.html">批准版三维</a></p></html>', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in package_hashes: package.write(snapshot / name, name)
    checked = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(checked['sha256'] + '\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == hashes and INDEX.read_bytes() == before
    row.update(approval_manifest=str(snapshot / '确认与校验清单.json'), archive_zip=str(bundle), archive_zip_sha256=checked['sha256'])
    index['entries'].append(row); index['approved_structure_forms'] += 1
    index.update(pending_batch=pending, updated_at=now.isoformat(), approved_undeployed_machine_ids=['I29', 'I30'], approved_undeployed_count=2,
                 scope='既有正式结构保留；I29与I30 V1外观已批准归档，batch-08为2/5，未接入。')
    index['batch_rule'] = '每累计5台新批准未接入机器再接入；I27/I28此前按直接授权已装，不重复计；当前batch-08为2/5。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=checked['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence / 'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records']) + 1, time=now.isoformat(),
        reason='负责人明确批准I30 V1并继续I31', deleted='无', added='I30 V1不可变确认快照和ZIP校验',
        modified='batch-08推进2/5，I30仅外观批准', purpose='区分外观批准、五台接入与游戏验收'))
    common.write_json(INDEX, index)
    result = dict(snapshot=str(snapshot), archive=str(target), zip=str(bundle), zip_sha256=checked['sha256'],
                  archive_zip_validation=checked, verified_structure=verified, pending_batch=pending,
                  source_geometry_rerun=False, approved_undeployed_count=2, approved_undeployed_machine_ids=['I29', 'I30'])
    common.write_json(ROOT / 'logs/i30-design-20261027/approval-v1-result.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
