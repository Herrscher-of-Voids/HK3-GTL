# -*- coding: utf-8 -*-
"""I41 V3明确批准归档；候选原字节保留，batch-10由1/5推进2/5。

变更记录 #1（2026-10-28）：记录实际用户消息时间，封存完整候选与ZIP，更新当前JSON/HTML索引；不部署实例。
"""
import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import os
import shutil
import zipfile
from pathlib import Path
from project_paths import project_path
from urllib.parse import quote

import archive_i23_v8_approval_20261025 as common
import i41_cosmic_customs_geometry_v3_20261028 as geometry
import i41_fan_dispatch_audit_20261028 as checks
from i34_open_observatory_export_20261027 import verify_dense

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I41_文明能源调度中枢_宇宙海关与十二港约束环城_V3_20261028'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
HTML_INDEX = INDEX.with_suffix('.html')
LOG = ROOT / 'logs/i41-approval-batch10-20261028'
DIALOGUE = ROOT / 'doc/HK3GTL-内测5/完整对话归档/2026-10-28_23-19-06_I41V3批准并制作I42_dea9f124a7.html'
INSTANCE = project_path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
QUOTE = '这一台也可以，接着进行下一台的制作'
SCOPE = ('批准I41 V3「宇宙海关与十二港约束环城」建筑外观及对应完整实体结构；'
         '不批准V1/V2，不包含前轮六项优化方案、RAM结果、正式控制器/Pattern、调度功能、研究、生存获取或游戏运行验收。')


def approval_message(session, message_id):
    found = []
    for line in session.open(encoding='utf-8'):
        if message_id not in line:
            continue
        row = json.loads(line)
        payload = row.get('payload', {})
        if row.get('type') == 'response_item' and payload.get('id') == message_id:
            found.append(row)
    message, = found
    payload = message['payload']
    assert payload['role'] == 'user'
    text = '\n'.join(part['text'] for part in payload['content'] if part.get('type') in ('input_text', 'text'))
    assert text.split('## My request:', 1)[-1].strip() == QUOTE
    approved_at = dt.datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00')).astimezone(
        dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='milliseconds')
    return dict(message_id=message_id, timestamp=message['timestamp'], approved_at_hong_kong=approved_at,
                user_text=QUOTE, source_session=str(session), ambient_ui_excluded=True)


def index_html(index):
    def existing_path(path):
        return project_path(path)

    def link(path):
        return quote(os.path.relpath(path, ARCHIVES).replace(os.sep, '/'), safe='/')
    rows = []
    for row in index['entries']:
        candidate = existing_path(row.get('archive', ''))
        choices = [candidate/'index.html', candidate/'三维评审.html']
        choices.extend(existing_path(row[key]) for key in ('approval_manifest', 'approved_nbt', 'source') if row.get(key))
        page = next((item for item in choices if item.is_file()), INDEX)
        version = row.get('approved_version') or row.get('candidate_version') or '按当前清单'
        voltage = row.get('target_voltage_appearance') or row.get('target_voltage') or '见原清单'
        state = '文件已安装；运行未验收' if row.get('game_files_installed') else '外观已批准；待批次接入'
        rows.append(f'<tr><td><a href="{html.escape(link(page))}">{html.escape(row["id"])}</a></td>'
                    f'<td>{html.escape(version)}</td><td>{html.escape(voltage)}</td><td>{state}</td></tr>')
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HK3GTL当前多方块确认归档索引</title><style>body{{max-width:1180px;margin:32px auto;padding:0 24px;background:#111b28;color:#e8edf4;font:16px/1.8 system-ui}}a{{color:#a9dce8}}table{{border-collapse:collapse;width:100%}}td,th{{padding:9px;text-align:left;border-bottom:1px solid #425466}}.note{{padding:14px;background:#263445;border-left:3px solid #bda2ce}}input{{padding:9px;width:100%;box-sizing:border-box;background:#1c2b3c;color:white;border:1px solid #547088}}</style>
<h1>当前多方块确认归档</h1><p class="note">外观已批准{index['approved_structure_forms']}种形态；正式文件已安装{index['formal_structure_forms']}种。batch-10：I40 V1、I41 V3，共2/5，尚未达到五台先接入阈值。I37留最后，未批准、不计数。</p>
<p>I41本轮批准仅含V3完整建筑，不含V1/V2、前轮六项优化方案或任何RAM测试结论。原候选内的“待审”保留为历史，当前批准以外部清单为准。</p>
<p><a href="当前归档索引.json">完整JSON索引</a> · <a href="{html.escape(link(project_path(index['latest_approval_snapshot']['snapshot'])/'确认接入.html'))}">I41 V3批准证据与封存现物</a></p>
<label>查找编号、版本或状态<input id="filter" placeholder="例如 I41、V3、待批次"></label><table><thead><tr><th>编号与现物</th><th>批准版本</th><th>电压</th><th>状态</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>更新于{html.escape(index['updated_at'])}；实例、正式资源与Pattern未在本次归档中改动。</p>
<script>document.getElementById('filter').oninput=e=>{{const q=e.target.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));}};</script></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', required=True, type=Path)
    parser.add_argument('--message-id', required=True)
    args = parser.parse_args()
    message = approval_message(args.session, args.message_id)
    assert DIALOGUE.is_file() and QUOTE in DIALOGUE.read_text(encoding='utf-8')
    assert message['approved_at_hong_kong'] == '2026-10-28T23:19:06.286+08:00'
    LOG.mkdir(parents=True, exist_ok=True)
    before = INDEX.read_bytes(); index = json.loads(before)
    assert index['approved_structure_forms'] == 47 and index['formal_structure_forms'] == 46
    assert index['pending_batch']['id'] == 'batch-10'
    assert index['pending_batch']['count'] == 1 and index['pending_batch']['approved_machine_ids'] == ['I40']
    assert index['approved_undeployed_count'] == 1 and index['approved_undeployed_machine_ids'] == ['I40']
    assert not any(row['id'] in ('I37', 'I41') for row in index['entries'])
    version = json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    installed = project_path(index['latest_deployment']['target'])
    assert installed.parent == INSTANCE/'mods'
    installed_hash = common.digest(installed)
    assert installed_hash == index['latest_deployment']['sha256']
    source_hashes = common.file_hashes(SOURCE)
    manifest = json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE/'verification.json').read_text(encoding='utf-8'))
    assert manifest['name'] == 'hk3gtl-i41-cosmic-customs-v3-20261028'
    assert manifest['candidate_version'] == 'V3' and manifest['approved'] is False
    assert check['passed'] and manifest['size'] == [529, 289, 529]
    assert manifest['blocks'] == 12119638 and manifest['unique_materials'] == 43 and manifest['ordinary_materials'] == 41
    assert manifest['controller'] == [264, 24, 0] and len(manifest['ports']) == 6 and len(manifest['zones']) == 12
    assert check['voltage_progression']['approval_index_sha256'] == hashlib.sha256(before).hexdigest()
    print('I41 V3现物及batch-10为1/5已核对；重新构造仅用于独立逐格回读。', flush=True)
    cube, data = geometry.build(); checks.geometry = geometry; rerun = checks.audit(cube, data)
    assert data['size'] == manifest['size'] and data['controller'] == manifest['controller']
    for key in ('blocks', 'unique_materials', 'ordinary_materials', 'palette', 'baseline_check',
                'connectivity', 'port_checks', 'voltage_progression'):
        assert rerun[key] == check[key], key
    nbt_file, = (SOURCE/'i41').glob('*.nbt'); schem_file, = (SOURCE/'i41').glob('*.schem')
    readback = verify_dense(cube, geometry.STATES, nbt_file, schem_file); del cube
    verified = dict(readback, controller=manifest['controller'], port_count=6,
        connectivity=check['connectivity'], iwv_casing_count=check['iwv_casing_count'],
        voltage_progression=check['voltage_progression'], ordinary_materials=41,
        nbt_file=str(nbt_file.relative_to(SOURCE)), schem_file=str(schem_file.relative_to(SOURCE)),
        nbt_sha256=common.digest(nbt_file), schem_sha256=common.digest(schem_file),
        source_geometry_rerun_for_readback_only=True, source_files_written=False, game_verified=False)
    assert verified['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
    assert verified['schem_sha256'] == check['nbt_schem_sha256']['schem']
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES/(now.strftime('%Y%m%d_%H%M%S_%f')+'_batch-10_02of05_I41_V3_IWV_外观已确认')
    evidence = snapshot/'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence/'previous-current-index.json').write_bytes(before)
    if HTML_INDEX.exists(): shutil.copy2(HTML_INDEX, evidence/'previous-current-index.html')
    shutil.copy2(__file__, evidence/Path(__file__).name)
    common.write_json(evidence/'approval-message-evidence.json', message)
    common.write_json(evidence/'instance-identity.json', dict(instance=str(INSTANCE), version=version,
        installed_target=str(installed), installed_sha256=installed_hash, instance_files_written=False))
    target = snapshot/SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == source_hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I40', 'I41'], count=2, required=5,
        deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
        game_files_installed=False, game_verified=False,
        deployment_blockers=['尚未累计五台明确批准结构，当前2/5；I37未批准且留到最后，不计数。'])
    row = dict(id='I41', key='i41', candidate_key='i41', approved_version='V3', candidate_version='V3',
        target_voltage_appearance='IWV', status='appearance_approved_archived_waiting_batch',
        approved_at=message['approved_at_hong_kong'], approval_quote=QUOTE,
        approval_message_id=args.message_id, approval_scope=SCOPE, source=str(SOURCE), archive=str(target),
        dialogue_archive=str(DIALOGUE),
        counts_as_new_machine=True, source_candidate_approved_field=False, external_approval_is_authoritative=True,
        formal_resource_present=False, game_files_installed=False, game_verified=False,
        size_xyz=manifest['size'], block_count=manifest['blocks'], unique_materials=43, ordinary_materials=41,
        controller=manifest['controller'], port_count=6, structure_checks=verified,
        approved_nbt=str(target/nbt_file.relative_to(SOURCE)), approved_nbt_sha256=verified['nbt_sha256'],
        nbt_sha256=verified['nbt_sha256'])
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong',
        original_user_message_time=message['approved_at_hong_kong'], entries=[copy.deepcopy(row)],
        dialogue_archive=str(DIALOGUE),
        accepted_design_scope=SCOPE, source_files_sha256=source_hashes, original_source_files_sha256=source_hashes,
        source_all_bytes_unchanged=True, source_candidate_status_preserved=True, external_approval_is_authoritative=True,
        previous_index_sha256=hashlib.sha256(before).hexdigest(), pending_batch_after_archive=pending,
        source_instance=str(INSTANCE), instance_version=version, game_files_installed=False, game_verified=False)
    common.write_json(snapshot/'确认与校验清单.json', approval)
    (snapshot/'确认接入.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I41 V3批准归档</title>
<style>body{{max-width:1160px;margin:32px auto;padding:0 24px;background:#111b28;color:#e8edf4;font:16px/1.8 system-ui}}a{{color:#acdce7;overflow-wrap:anywhere}}img{{width:100%}}</style>
<h1>I41 V3 · 宇宙海关与十二港约束环城已批准</h1><p>{html.escape(SCOPE)}</p><p>负责人原话：{QUOTE}（{message['approved_at_hong_kong']}）。实际原始消息ID：{html.escape(args.message_id)}。</p>
<p>529×529×289（宽×长×高）；12,119,638实体、41种普通材料，另有主控/接口两种标记。主控[264,24,0]，整宽第265格，6处齐平接口、12个建筑分区。完整NBT与Schematic重新逐格回读一致。</p>
<p>展示核、约束笼、配平环与清算设施是外观表达；不新增产能、捕获、账户限额或熵债。十二分区不等于新增十二个正式控制器。I41仍只承担授权负载登记、调度及历史异常回执。</p>
<p>原候选{len(source_hashes)}个文件全字节保持不变，内部“待审”保留为批准前历史。外部确认清单记录V3已批准；V1/V2没有连带批准。batch-10为I40 V1与I41 V3，共2/5；批准48种、正式安装仍46种。未到五台阈值，本次不改实例、正式资源、Pattern或I37。</p>
<p><a href="确认与校验清单.json">确认与校验清单</a> · <a href="{SOURCE.name}/index.html">获批现物</a> · <a href="{SOURCE.name}/i41/三维评审.html">真实MC材质三维预览</a> · <a href="../当前归档索引.html">当前归档索引</a></p><img src="{SOURCE.name}/完整预览.png" alt="批准的I41 V3完整建筑"></html>''', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for name in package_hashes: package.write(snapshot/name, name)
    checked = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(checked['sha256']+'\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == source_hashes and INDEX.read_bytes() == before
    assert common.digest(installed) == installed_hash
    row.update(approval_manifest=str(snapshot/'确认与校验清单.json'), archive_zip=str(bundle),
               archive_zip_sha256=checked['sha256'])
    index['entries'].append(row)
    index.update(approved_structure_forms=48, updated_at=now.isoformat(), pending_batch=pending,
        approved_undeployed_count=2, approved_undeployed_machine_ids=['I40', 'I41'],
        scope='I40 V1与I41 V3明确批准并完整归档，batch-10为2/5，未部署；正式安装仍46种；I37未批准且留最后，继续制作I42。')
    index['batch_rule'] = '每累计5台新批准未接入机器先接入再做下一台；当前batch-10为2/5，I37未批准、不计数。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=checked['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence/'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records'])+1, time=now.isoformat(),
        reason='负责人明确批准I41 V3并要求下一台', deleted='无', added='I41 V3现物快照、ZIP、实际用户消息及逐格回读证据',
        modified='batch-10由1/5推进2/5；仅V3获批，正式46种及实例不变；不连带批准六项优化和RAM结果',
        purpose='按明确外观批准计数，封存版本身份，继续I42'))
    common.write_json(INDEX, index)
    HTML_INDEX.write_text(index_html(index), encoding='utf-8')
    result = dict(passed=True, snapshot=str(snapshot), archive=str(target), zip=str(bundle), zip_sha256=checked['sha256'],
        archive_zip_validation=checked, verified_structure=verified, source_file_count=len(source_hashes),
        source_all_bytes_unchanged=True, original_source_files_sha256=source_hashes, pending_batch=pending,
        approved_structure_forms=48, formal_structure_forms=46, game_files_installed=False, game_verified=False,
        approval_message_id=args.message_id, approved_at=message['approved_at_hong_kong'], instance_version=version,
        instance_jar_unchanged=True, index_sha256=common.digest(INDEX), html_index=str(HTML_INDEX),
        html_index_sha256=common.digest(HTML_INDEX))
    common.write_json(LOG/'approval-v3-result.json', result)
    print(json.dumps({key: result[key] for key in ('snapshot', 'zip', 'zip_sha256', 'source_file_count',
        'approved_structure_forms', 'formal_structure_forms', 'pending_batch')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
