# -*- coding: utf-8 -*-
"""I40 V1明确批准归档：保持源候选不变，batch-10从0/5推进1/5。
变更记录 #1（2026-10-28）：新增现物快照、消息证据、完整回读与批次记账；不部署实例。
"""
import copy
import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import archive_i23_v8_approval_20261025 as common
import i40_cascade_foundry_geometry_20261028 as geometry
from i40_cascade_foundry_audit_20261028 import audit
from i34_open_observatory_export_20261027 import verify_dense

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I40_文明奇观材料合成中心_四系贯流合成工场_V1_20261028'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
LOG = ROOT / 'logs/i40-approval-batch10-20261028'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-28_17-48-52_I40V1批准归档并制作I41.html'
SESSION = Path('C:/Users/OWNER/.codex/sessions/2026/10/28/rollout-2026-10-28T16-54-50-01a158c2-319f-7ad2-b0ce-2e04979e5e4e_01a181b8-21b4-7a21-b0ca-9eb31b2ea291.jsonl')
MESSAGE = 'msg_01a181e9-9b45-7430-96c8-cc20b37b3de3'
APPROVED_AT = '2026-10-28T17:48:52.933+08:00'
QUOTE = '这一台也可以，接着进行下一台的制作'
SCOPE = '批准I40 V1四系贯流合成工场的建筑外观与对应完整实体结构；正式控制器、Pattern、四系工艺与成分回流、研究、生存获取及游戏运行未在本次验收。'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    before = INDEX.read_bytes(); index = json.loads(before)
    assert index['approved_structure_forms'] == index['formal_structure_forms'] == 46
    assert index['pending_batch']['id'] == 'batch-10'
    assert index['pending_batch']['count'] == 0 and index['pending_batch']['approved_machine_ids'] == []
    assert not any(row['id'] in ('I37', 'I40') for row in index['entries']), '拒绝重复批准或连带批准I37'
    assert index['approved_undeployed_count'] == 0
    version = json.loads((INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    installed_target = Path(index['latest_deployment']['target'])
    assert installed_target.parent == INSTANCE / 'mods'
    installed_hash = common.digest(installed_target)
    assert installed_hash == index['latest_deployment']['sha256']
    source_hashes = common.file_hashes(SOURCE)
    common.write_json(LOG / 'approval-source-files-sha256.json', source_hashes)
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
    assert manifest['candidate_version'] == 'V1' and manifest['approved'] is False
    assert check['passed'] and manifest['size'] == [601, 291, 481]
    assert manifest['blocks'] == 12697362 and manifest['unique_materials'] == 44 and manifest['ordinary_materials'] == 42
    assert manifest['controller'] == [300, 27, 0] and len(manifest['ports']) == 12
    assert check['voltage_progression']['approval_index_sha256'] == hashlib.sha256(before).hexdigest()
    print('I40源候选与batch-10状态已核对；重新构造实体仅用于独立回读校验。', flush=True)
    cube, data = geometry.build(); rerun = audit(cube, data)
    assert data['size'] == manifest['size'] and data['controller'] == manifest['controller']
    for key in ('blocks', 'unique_materials', 'ordinary_materials', 'palette', 'baseline_check',
                'connectivity', 'port_checks', 'voltage_progression'):
        assert rerun[key] == check[key], key
    nbt_file, = (SOURCE / 'i40').glob('*.nbt')
    schem_file, = (SOURCE / 'i40').glob('*.schem')
    readback = verify_dense(cube, geometry.STATES, nbt_file, schem_file); del cube
    assert readback['blocks'] == manifest['blocks']
    verified = dict(readback, size_wdh=check['size_wdh'], controller=manifest['controller'],
        port_count=12, marker_checks_passed=13, baseline_wdh=check['baseline_check']['baseline_wdh'],
        connectivity=check['connectivity'], wfv_casing_count=check['wfv_casing_count'],
        voltage_progression=check['voltage_progression'], ordinary_materials=42, unique_materials=44,
        nbt_file=str(nbt_file.relative_to(SOURCE)), schem_file=str(schem_file.relative_to(SOURCE)),
        nbt_sha256=common.digest(nbt_file), schem_sha256=common.digest(schem_file),
        source_geometry_rerun_for_readback_only=True, source_files_written=False, game_verified=False)
    assert verified['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
    assert verified['schem_sha256'] == check['nbt_schem_sha256']['schem']
    messages = [json.loads(line) for line in SESSION.open(encoding='utf-8') if MESSAGE in line]
    message, = [row for row in messages if row.get('type') == 'response_item' and row.get('payload', {}).get('id') == MESSAGE]
    assert message['timestamp'] == '2026-10-28T09:48:52.933Z'
    visible_text = message['payload']['content'][0]['text'].split('## My request:', 1)[-1].strip()
    assert visible_text == QUOTE and message['payload']['role'] == 'user'
    assert dt.datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00')).astimezone(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='milliseconds') == APPROVED_AT
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES / (now.strftime('%Y%m%d_%H%M%S_%f') + '_batch-10_01of05_I40_V1_WFV_外观已确认')
    evidence = snapshot / 'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence / 'previous-current-index.json').write_bytes(before)
    shutil.copy2(__file__, evidence / Path(__file__).name)
    common.write_json(evidence / 'approval-message-evidence.json', dict(message_id=MESSAGE, timestamp=message['timestamp'],
        user_text=QUOTE, source_session=str(SESSION), ambient_ui_excluded=True))
    common.write_json(evidence / 'instance-identity.json', dict(instance=str(INSTANCE), version=version,
        installed_target=str(installed_target), installed_sha256=installed_hash, instance_files_written=False))
    target = snapshot / SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == source_hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I40'], count=1, required=5,
        deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
        game_files_installed=False, game_verified=False,
        deployment_blockers=['尚未累计五台明确批准结构，当前1/5；I37未批准且留到最后，不计数。'])
    row = dict(id='I40', key='i40', candidate_key='i40', approved_version='V1', candidate_version='V1',
        target_voltage_appearance='WFV', status='appearance_approved_archived_waiting_batch',
        approved_at=APPROVED_AT, approval_quote=QUOTE, approval_message_id=MESSAGE, approval_scope=SCOPE,
        source=str(SOURCE), archive=str(target), discussion_record=str(DISCUSSION), counts_as_new_machine=True,
        source_candidate_approved_field=False, external_approval_is_authoritative=True,
        formal_resource_present=False, game_files_installed=False, game_verified=False,
        size_xyz=manifest['size'], block_count=manifest['blocks'], unique_materials=44, ordinary_materials=42,
        controller=manifest['controller'], port_count=12, structure_checks=verified,
        approved_nbt=str(target / nbt_file.relative_to(SOURCE)), approved_nbt_sha256=verified['nbt_sha256'], nbt_sha256=verified['nbt_sha256'])
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong', original_user_message_time=APPROVED_AT,
        entries=[row], accepted_design_scope=SCOPE, source_files_sha256=source_hashes, original_source_files_sha256=source_hashes,
        source_all_bytes_unchanged=True, source_candidate_status_preserved=True, external_approval_is_authoritative=True,
        previous_index_sha256=hashlib.sha256(before).hexdigest(), pending_batch_after_archive=pending,
        source_instance=str(INSTANCE), instance_version=version, game_files_installed=False, game_verified=False)
    common.write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I40 V1批准归档</title>
<style>body{{max-width:1100px;margin:32px auto;padding:0 24px;background:#111a29;color:#e9edf5;font:16px/1.8 system-ui}}a{{color:#c9b5dc;overflow-wrap:anywhere}}img{{width:100%}}</style>
<h1>I40 V1 · 四系贯流合成工场已批准</h1><p>{html.escape(SCOPE)}</p><p>负责人原话：{QUOTE}（{APPROVED_AT}）。</p>
<p>601×481×291格（宽×长×高）；12,697,362实体、42种普通材料，另有主控/接口两种标记。主控[300,27,0]，整宽第301格，12处齐平接口。完整NBT与Schematic重新逐格回读一致。</p>
<p>导能、约束、重构、认知四条独立工艺线，只共享检测采样桥。WFV机壳主导反应塔和工艺长廊，正式工艺与获取链另验。</p>
<p>本外部清单记录批准；源候选{len(source_hashes)}个文件全字节保留，内部“待审”是批准前历史状态。当前batch-10为I40共1/5，尚未满足五台先接入阈值；批准总数47，正式已装仍46。本次未改实例JAR、正式Pattern或世界。I37留到最后，下一台制作I41。</p>
<p><a href="确认与校验清单.json">批准与校验清单</a> · <a href="{SOURCE.name}/index.html">获批现物</a> · <a href="{SOURCE.name}/i40/三维评审.html">MC材质三维评审</a></p>
<img src="{SOURCE.name}/完整预览.png" alt="获批I40 V1完整外观"></html>''', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for name in package_hashes: package.write(snapshot / name, name)
    checked = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(checked['sha256'] + '\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == source_hashes and INDEX.read_bytes() == before
    assert common.digest(installed_target) == installed_hash
    row.update(approval_manifest=str(snapshot / '确认与校验清单.json'), archive_zip=str(bundle), archive_zip_sha256=checked['sha256'])
    index['entries'].append(row)
    index.update(approved_structure_forms=47, updated_at=now.isoformat(), pending_batch=pending,
        approved_undeployed_count=1, approved_undeployed_machine_ids=['I40'],
        scope='I40 V1已明确批准并独立归档，batch-10为1/5，未部署；已装正式形态仍46，I37留到最后且未批准，继续制作I41。')
    index['batch_rule'] = '每累计5台新批准未接入机器先接入再做下一台；当前batch-10为1/5，I37未批准、不计数。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=checked['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence / 'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records']) + 1, time=now.isoformat(),
        reason='负责人明确批准I40 V1并要求下一台', deleted='无', added='I40 V1现物快照、ZIP、原始消息证据与完整回读',
        modified='batch-10由0/5推进1/5；I37留到最后；本次不部署，原交付与正式46形态保持原字节',
        purpose='按明确批准计数，保持现物身份和实例状态可核对'))
    common.write_json(INDEX, index)
    result = dict(snapshot=str(snapshot), archive=str(target), zip=str(bundle), zip_sha256=checked['sha256'],
        archive_zip_validation=checked, verified_structure=verified, source_all_bytes_unchanged=True,
        original_source_files_sha256=source_hashes, pending_batch=pending, approved_structure_forms=47,
        formal_structure_forms=46, game_files_installed=False, game_verified=False, approval_message_id=MESSAGE,
        approved_at=APPROVED_AT, instance_version=version, instance_jar_unchanged=True)
    common.write_json(LOG / 'approval-v1-result.json', result)
    print(json.dumps({key: result[key] for key in ('snapshot', 'zip', 'zip_sha256', 'approved_structure_forms',
        'formal_structure_forms', 'pending_batch')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
