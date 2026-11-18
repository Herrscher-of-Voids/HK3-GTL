# -*- coding: utf-8 -*-
"""I35 V3明确批准：独立快照保留候选原字节，batch-09推进至2/5。"""
import copy
import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import archive_i23_v8_approval_20261025 as common
import i35_threshold_geometry_v3_20261027 as geometry
from i34_open_observatory_export_20261027 import verify_dense

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I35_虚数空间锚定阵列_越界悬索桥_V3_20261027'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
LOG = ROOT / 'logs/i35-threshold-v3-20261027'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-27_08-39-36_I35V3批准归档与I36候选继续.html'
SESSION = Path('C:/Users/OWNER/.codex/sessions/2026/10/26/rollout-2026-10-26T16-20-05-01a158c2-319f-7ad2-b0ce-2e04979e5e4e_01a1774b-9781-76b1-8b30-d7cfb5fd01da.jsonl')
MESSAGE = 'msg_01a17acc-6024-7553-b7d8-16c85cfff547'
APPROVED_AT = '2026-10-27T08:39:36.740+08:00'
QUOTE = '下一台I36吧，这台ok'
SCOPE = '批准I35 V3越界悬索桥建筑外观、完整实体结构及黑金虚数空间HTML非实体效果；正式控制器、Pattern、工艺、研究、生存获取、真实跨维能力与游戏运行未在本次验收。'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')


def main():
    before = INDEX.read_bytes(); index = json.loads(before)
    assert index['approved_structure_forms'] == 42 and index['formal_structure_forms'] == 41
    assert index['pending_batch']['id'] == 'batch-09'
    assert index['pending_batch']['count'] == 1 and index['pending_batch']['approved_machine_ids'] == ['I34']
    assert not any(row['id'] == 'I35' for row in index['entries']), '拒绝重复增加批准台数'
    assert index['latest_deployment']['formal_shapes'] == 41 and index['latest_deployment']['game_files_installed']
    version = json.loads((INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    installed_target = Path(index['latest_deployment']['target'])
    assert installed_target.parent == INSTANCE / 'mods'
    installed_hash = common.digest(installed_target)
    assert installed_hash == index['latest_deployment']['sha256']
    source_hashes = common.file_hashes(SOURCE)
    assert source_hashes == json.loads((LOG / 'delivery-files-sha256.json').read_text(encoding='utf-8'))
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['candidate_version'] == 'V3' and manifest['approved'] is False
    assert check['passed'] and manifest['size'] == [401, 281, 701]
    assert manifest['blocks'] == 9720448 and manifest['unique_materials'] == 40
    assert manifest['controller'] == [200, 28, 8] and len(manifest['ports']) == 10
    cube, data = geometry.build()
    assert data['size'] == manifest['size'] and data['controller'] == manifest['controller']
    assert data['portal'] == manifest['portal']
    nbt_file, = (SOURCE / 'i35').glob('*.nbt')
    schem_file, = (SOURCE / 'i35').glob('*.schem')
    readback = verify_dense(cube, geometry.STATES, nbt_file, schem_file)
    del cube
    assert readback['blocks'] == manifest['blocks']
    verified = dict(readback, size_wdh=check['size_wdh'], controller=manifest['controller'],
        port_count=10, baseline_wdh=check['baseline_check']['baseline_wdh'],
        bilateral_symmetry=check['bilateral_symmetry'], connectivity=check['connectivity'],
        threshold_checks=check['threshold_checks'], portal_visual_only=manifest['portal'],
        nbt_file=str(nbt_file.relative_to(SOURCE)), schem_file=str(schem_file.relative_to(SOURCE)),
        nbt_sha256=common.digest(nbt_file), schem_sha256=common.digest(schem_file),
        source_geometry_rerun_for_readback_only=True, source_files_written=False, game_verified=False)
    assert verified['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
    assert verified['schem_sha256'] == check['nbt_schem_sha256']['schem']
    messages = [json.loads(line) for line in SESSION.open(encoding='utf-8') if MESSAGE in line]
    message, = [r for r in messages if r.get('type') == 'response_item' and r.get('payload', {}).get('id') == MESSAGE]
    assert message['timestamp'] == '2026-10-27T00:39:36.740Z'
    assert QUOTE in message['payload']['content'][0]['text']
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES / (now.strftime('%Y%m%d_%H%M%S_%f') + '_batch-09_02of05_I35_V3_IRV_外观已确认')
    evidence = snapshot / 'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence / 'previous-current-index.json').write_bytes(before)
    shutil.copy2(__file__, evidence / Path(__file__).name)
    common.write_json(evidence / 'approval-message-evidence.json', dict(message_id=MESSAGE,
        timestamp=message['timestamp'], user_text=QUOTE, source_session=str(SESSION)))
    common.write_json(evidence / 'instance-identity.json', dict(instance=str(INSTANCE), version=version,
        installed_target=str(installed_target), installed_sha256=installed_hash, instance_files_written=False))
    target = snapshot / SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == source_hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I34', 'I35'], count=2, required=5,
        deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
        game_files_installed=False, game_verified=False,
        deployment_blockers=['尚未达到每5台明确批准的结构接入阈值，当前2/5。'])
    row = dict(id='I35', key='i35', candidate_key='i35', approved_version='V3', candidate_version='V3',
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
        pending_batch_after_archive=pending, source_instance=str(INSTANCE), instance_version=version,
        game_files_installed=False, game_verified=False)
    common.write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I35 V3批准归档</title>
<style>body{{max-width:1050px;margin:32px auto;padding:0 24px;font:16px/1.8 system-ui}}a{{overflow-wrap:anywhere}}</style>
<h1>I35 V3 · 越界悬索桥已批准</h1><p>{html.escape(SCOPE)}</p><p>负责人原话：{QUOTE}（{APPROVED_AT}）。</p>
<p>401×701×281格；9,720,448个实体、40种材料、10处接口。主控[200,28,8]，整宽第201格。NBT及Schematic已逐格回读一致。</p>
<p>近端连接本维度实体锚室，桥面及主缆穿过八角虚数界面；黑金空间、流纹、星芒及门后隐没为HTML非实体效果，不计方块或Pattern，不代表真实传送能力。</p>
<p>批准由本清单记录；原交付{len(source_hashes)}个文件全字节保留，内部“待审候选”是批准前历史状态。当前batch-09为2/5，正式已装仍41种；增强版2.9.2实例JAR哈希不变。</p>
<p><a href="确认与校验清单.json">确认与校验清单</a> · <a href="{SOURCE.name}/index.html">获批现物</a> · <a href="{SOURCE.name}/i35/三维评审.html">三维评审</a></p></html>''', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for name in package_hashes: package.write(snapshot / name, name)
    checked = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(checked['sha256'] + '\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == source_hashes and INDEX.read_bytes() == before
    assert common.digest(installed_target) == installed_hash
    row.update(approval_manifest=str(snapshot / '确认与校验清单.json'), archive_zip=str(bundle), archive_zip_sha256=checked['sha256'])
    index['entries'].append(row); index['approved_structure_forms'] = 43
    index.update(updated_at=now.isoformat(), pending_batch=pending, approved_undeployed_count=2,
        approved_undeployed_machine_ids=['I34', 'I35'],
        scope='I34 V2与I35 V3外观及完整结构已批准归档，batch-09为2/5；正式已装仍41种，游戏成型运行未验收。I36为下一台。')
    index['batch_rule'] = '每累计5台新批准未接入机器再接入；当前batch-09为2/5，I36尚未批准、不计数。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=checked['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence / 'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records']) + 1, time=now.isoformat(),
        reason='负责人明确批准I35 V3并继续I36', deleted='无', added='I35 V3获批现物快照、ZIP、批准证据',
        modified='batch-09由1/5推进2/5；原交付与正式41种保持原字节', purpose='区分建筑批准、候选历史和实例接入'))
    common.write_json(INDEX, index)
    result = dict(snapshot=str(snapshot), archive=str(target), zip=str(bundle), zip_sha256=checked['sha256'],
        archive_zip_validation=checked, verified_structure=verified, source_all_bytes_unchanged=True,
        original_source_files_sha256=source_hashes, pending_batch=pending, approved_structure_forms=43,
        formal_structure_forms=41, game_files_installed=False, game_verified=False,
        approval_message_id=MESSAGE, approved_at=APPROVED_AT, instance_version=version, instance_jar_unchanged=True)
    common.write_json(LOG / 'approval-v3-result.json', result)
    print(json.dumps({k: result[k] for k in ('snapshot', 'zip', 'zip_sha256', 'approved_structure_forms', 'formal_structure_forms', 'pending_batch')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
