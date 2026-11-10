# -*- coding: utf-8 -*-
"""I34 V2明确批准：源交付全字节保留，外部记录批准并计入batch-09。"""
import copy
import datetime as dt
import hashlib
import html
import json
import shutil
import sys
import zipfile
from pathlib import Path

import archive_i23_v8_approval_20261025 as common
import i34_open_observatory_geometry_20261027 as geometry
from i34_open_observatory_export_20261027 import verify_dense

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I34_虚数之树观测阵列_开穹悬弦观测仪_V2_20261027'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
LOG = ROOT / 'logs/i34-open-observatory-v2-20261027'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-27_06-22-33_I34V2批准归档与I35候选继续.html'
SESSION = Path('C:/Users/OWNER/.codex/sessions/2026/10/26/rollout-2026-10-26T16-20-05-01a158c2-319f-7ad2-b0ce-2e04979e5e4e_01a1774b-9781-76b1-8b30-d7cfb5fd01da.jsonl')
MESSAGE = 'msg_01a17a4e-e5a8-7941-9999-5dec7b2eab07'
APPROVED_AT = '2026-10-27T06:22:33.384+08:00'
QUOTE = 'I34 V2非常的好，直接到下一台'
SCOPE = '批准I34 V2开穹悬弦观测仪建筑外观、对应完整结构文件及已确认金白非实体树影；正式控制器、Pattern、工艺、研究、生存获取与游戏运行未验收。'


def main():
    before = INDEX.read_bytes(); index = json.loads(before)
    assert index['approved_structure_forms'] == index['formal_structure_forms'] == 41
    assert index['pending_batch']['id'] == 'batch-09' and index['pending_batch']['count'] == 0
    assert not any(row['id'] == 'I34' for row in index['entries']), '拒绝重复增加批准台数'
    assert index['latest_deployment']['formal_shapes'] == 41 and index['latest_deployment']['game_files_installed']
    source_hashes = common.file_hashes(SOURCE)
    assert source_hashes == json.loads((LOG / 'delivery-files-sha256.json').read_text(encoding='utf-8'))
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['candidate_version'] == 'V2' and manifest['approved'] is False
    assert check['passed'] and manifest['size'] == [481, 251, 381]
    assert manifest['blocks'] == 7464621 and manifest['unique_materials'] == 40
    assert manifest['controller'] == [240, 43, 18] and len(manifest['ports']) == 10
    cube, data = geometry.build()
    assert data['size'] == manifest['size'] and data['controller'] == manifest['controller']
    nbt_file, = (SOURCE / 'i34').glob('*.nbt')
    schem_file, = (SOURCE / 'i34').glob('*.schem')
    readback = verify_dense(cube, geometry.STATES, nbt_file, schem_file)
    del cube
    assert readback['blocks'] == manifest['blocks']
    verified = dict(readback, size_wdh=check['size_wdh'], controller=manifest['controller'],
        port_count=10, baseline_wdh=check['baseline_check']['baseline_wdh'],
        bilateral_symmetry=check['bilateral_symmetry'], connectivity=check['connectivity'],
        nbt_file=str(nbt_file.relative_to(SOURCE)), schem_file=str(schem_file.relative_to(SOURCE)),
        nbt_sha256=common.digest(nbt_file), schem_sha256=common.digest(schem_file),
        source_geometry_rerun_for_readback_only=True, source_files_written=False, game_verified=False)
    assert verified['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
    assert verified['schem_sha256'] == check['nbt_schem_sha256']['schem']
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES / (now.strftime('%Y%m%d_%H%M%S_%f') + '_batch-09_01of05_I34_V2_IRV_外观已确认')
    evidence = snapshot / 'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence / 'previous-current-index.json').write_bytes(before)
    shutil.copy2(__file__, evidence / Path(__file__).name)
    messages = [json.loads(line) for line in SESSION.open(encoding='utf-8') if MESSAGE in line]
    message, = [r for r in messages if r.get('type') == 'response_item' and r.get('payload', {}).get('id') == MESSAGE]
    assert message['timestamp'] == '2026-10-26T22:22:33.384Z'
    assert QUOTE in message['payload']['content'][0]['text']
    common.write_json(evidence / 'approval-message-evidence.json', dict(message_id=MESSAGE,
        timestamp=message['timestamp'], user_text=QUOTE, source_session=str(SESSION)))
    target = snapshot / SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == source_hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I34'], count=1, required=5,
        deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
        game_files_installed=False, game_verified=False,
        deployment_blockers=['尚未达到每5台明确批准的结构接入阈值，当前1/5。'])
    row = dict(id='I34', key='i34', candidate_key='i34', approved_version='V2', candidate_version='V2',
        target_voltage_appearance='IRV', status='appearance_approved_archived_waiting_batch',
        approved_at=APPROVED_AT, approval_quote=QUOTE, approval_message_id=MESSAGE, approval_scope=SCOPE,
        source=str(SOURCE), archive=str(target), discussion_record=str(DISCUSSION), counts_as_new_machine=True,
        source_candidate_approved_field=False, external_approval_is_authoritative=True,
        formal_resource_present=False, game_files_installed=False, game_verified=False,
        size_xyz=manifest['size'], block_count=manifest['blocks'], unique_materials=40,
        controller=manifest['controller'], port_count=10, structure_checks=verified,
        approved_nbt=str(target / nbt_file.relative_to(SOURCE)), approved_nbt_sha256=verified['nbt_sha256'],
        nbt_sha256=verified['nbt_sha256'])
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong',
        original_user_message_time=APPROVED_AT, entries=[row], accepted_design_scope=SCOPE,
        source_files_sha256=source_hashes, original_source_files_sha256=source_hashes,
        source_all_bytes_unchanged=True, source_candidate_status_preserved=True,
        external_approval_is_authoritative=True, previous_index_sha256=hashlib.sha256(before).hexdigest(),
        pending_batch_after_archive=pending, game_files_installed=False, game_verified=False)
    common.write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I34 V2批准归档</title>
<style>body{{max-width:1050px;margin:32px auto;padding:0 24px;font:16px/1.8 system-ui}}a{{overflow-wrap:anywhere}}</style>
<h1>I34 V2 · 开穹悬弦观测仪已批准</h1><p>{html.escape(SCOPE)}</p><p>负责人原话：{QUOTE}（{APPROVED_AT}）。</p>
<p>481×381×251格；7,464,621个实体、40种材料、10处接口。主控[240,43,18]，整宽第241格。NBT及Schematic已逐格回读一致。金白树影为非实体，不计方块或Pattern。</p>
<p>批准由本清单记录；原交付16个文件全字节保留，内部“待审候选”是批准前历史状态。当前batch-09为1/5，正式已装仍41种，未改实例。</p>
<p><a href="确认与校验清单.json">确认与校验清单</a> · <a href="{SOURCE.name}/index.html">获批现物</a> · <a href="{SOURCE.name}/i34/三维评审.html">三维评审</a></p></html>''', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for name in package_hashes: package.write(snapshot / name, name)
    checked = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(checked['sha256'] + '\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == source_hashes and INDEX.read_bytes() == before
    row.update(approval_manifest=str(snapshot / '确认与校验清单.json'), archive_zip=str(bundle), archive_zip_sha256=checked['sha256'])
    index['entries'].append(row); index['approved_structure_forms'] = 42
    index.update(updated_at=now.isoformat(), pending_batch=pending, approved_undeployed_count=1,
        approved_undeployed_machine_ids=['I34'],
        scope='I34 V2外观及完整结构已批准归档，batch-09为1/5；正式已装仍41种，游戏成型运行未验收。I35为下一台待审候选。')
    index['batch_rule'] = '每累计5台新批准未接入机器再接入；当前batch-09为1/5，I35候选尚未计数。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=checked['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence / 'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records']) + 1, time=now.isoformat(),
        reason='负责人明确批准I34 V2并继续下一台', deleted='无', added='I34获批现物快照、ZIP、批准证据',
        modified='batch-09由0/5推进1/5；原交付与正式41种保持原字节', purpose='区分建筑批准、候选历史和实例接入'))
    common.write_json(INDEX, index)
    result = dict(snapshot=str(snapshot), archive=str(target), zip=str(bundle), zip_sha256=checked['sha256'],
        archive_zip_validation=checked, verified_structure=verified, source_all_bytes_unchanged=True,
        original_source_files_sha256=source_hashes, pending_batch=pending, approved_structure_forms=42,
        formal_structure_forms=41, game_files_installed=False, game_verified=False)
    common.write_json(LOG / 'approval-v2-result.json', result)
    print(json.dumps({k: result[k] for k in ('snapshot', 'zip', 'zip_sha256', 'approved_structure_forms', 'formal_structure_forms', 'pending_batch')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
