# -*- coding: utf-8 -*-
"""I42 V1明确批准封存：候选原字节保留，batch-10由2/5推进3/5。

变更记录 #1（2026-10-28）：核对实际用户消息、完整结构与ZIP，更新批准索引；不部署实例。
"""
import argparse
import copy
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import archive_i41_v3_approval_20261028 as previous
import i42_prefabrication_geometry_v1_20261028 as geometry
import i42_prefabrication_audit_v1_20261028 as checks
from i34_open_observatory_export_20261027 import verify_dense

ROOT, ARCHIVES, INDEX, HTML_INDEX = previous.ROOT, previous.ARCHIVES, previous.INDEX, previous.HTML_INDEX
INSTANCE, QUOTE, common = previous.INSTANCE, previous.QUOTE, previous.common
SOURCE = ROOT/'deliveries/I42_奇观构件预制工厂_巨构龙骨与步进预制船坞_V1_20261028'
LOG = ROOT/'logs/i42-approval-batch10-20261028'
SCOPE = ('批准I42 V1「巨构龙骨与步进预制船坞」建筑外观及对应完整实体结构；'
         '不包含RAM或优化方案、专用配方、研究、生存获取、正式控制器/Pattern或游戏运行验收。')


def index_html(index):
    text = previous.index_html(index)
    changes = {
        'batch-10：I40 V1、I41 V3，共2/5': 'batch-10：I40 V1、I41 V3、I42 V1，共3/5',
        'I41本轮批准仅含V3完整建筑，不含V1/V2、前轮六项优化方案或任何RAM测试结论。':
            'I42本轮批准仅含V1完整建筑，不含RAM、优化方案、配方、研究、正式控制器或游戏运行验收。',
        'I41 V3批准证据与封存现物': 'I42 V1批准证据与封存现物',
        '例如 I41、V3、待批次': '例如 I42、V1、待批次',
    }
    for old, new in changes.items():
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text


def link_check(pages):
    tested, broken = 0, []
    for page in pages:
        for ref in re.findall(r'(?:href|src)="([^"#]+)"', page.read_text(encoding='utf-8')):
            parsed = urlsplit(html.unescape(ref))
            if parsed.scheme:
                continue
            tested += 1
            target = page.parent/unquote(parsed.path)
            if not target.exists():
                broken.append(dict(page=str(page), reference=ref))
    assert not broken, broken
    return dict(passed=True, pages=len(pages), verified_pages=list(map(str, pages)),
                local_references=tested, broken_links=broken)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', required=True, type=Path)
    parser.add_argument('--message-id', required=True)
    parser.add_argument('--dialogue', required=True, type=Path)
    args = parser.parse_args()
    message = previous.approval_message(args.session, args.message_id)
    assert args.message_id == 'msg_01a18336-005b-7ee0-81c3-2b970e3f9767'
    assert message['approved_at_hong_kong'] == '2026-10-28T23:51:56.763+08:00'
    dialogue = args.dialogue.resolve()
    assert dialogue.is_relative_to((ROOT/'doc/HK3GTL-内测5/完整对话归档').resolve())
    assert QUOTE in dialogue.read_text(encoding='utf-8')
    before = INDEX.read_bytes(); index = json.loads(before)
    old_entries = copy.deepcopy(index['entries'])
    assert index['approved_structure_forms'] == 48 and index['formal_structure_forms'] == 46
    assert index['pending_batch']['id'] == 'batch-10' and index['pending_batch']['count'] == 2
    assert index['pending_batch']['approved_machine_ids'] == index['approved_undeployed_machine_ids'] == ['I40', 'I41']
    assert index['approved_undeployed_count'] == 2
    assert not any(row['id'] in ('I37', 'I42') for row in old_entries)
    installed = Path(index['latest_deployment']['target'])
    assert installed.parent == INSTANCE/'mods'
    installed_hash = common.digest(installed)
    assert installed_hash == index['latest_deployment']['sha256']
    version = json.loads((INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    source_hashes = common.file_hashes(SOURCE)
    manifest = json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE/'verification.json').read_text(encoding='utf-8'))
    browser = json.loads((SOURCE/'browser-verification.json').read_text(encoding='utf-8'))
    assert manifest['name'] == 'hk3gtl-i42-prefabrication-dock-v1-20261028'
    assert manifest['candidate_version'] == 'V1' and manifest['approved'] is False
    assert manifest['size'] == [641, 295, 449] and manifest['controller'] == [320, 26, 0]
    assert manifest['target_voltage'] == 'WFV' and len(manifest['ports']) == 8
    assert manifest['blocks'] == 14747313 and manifest['unique_materials'] == 44 and manifest['ordinary_materials'] == 42
    assert check['passed'] and check['viewer_rendered_quads'] == 336400
    assert browser['passed'] and browser['blocks'] == 14747313 and browser['rendered_quads'] == 336400
    assert check['voltage_progression']['approval_index_sha256'] == hashlib.sha256(before).hexdigest()
    print('I42 V1现物与2/5批次已核对；只读重建并逐格回读。', flush=True)
    cube, data = geometry.build(); rerun = checks.audit(cube, data)
    assert all(data[key] == manifest[key] for key in data)
    for key in ('blocks', 'unique_materials', 'ordinary_materials', 'palette', 'baseline_check',
                'connectivity', 'controller', 'port_checks', 'voltage_progression'):
        assert rerun[key] == check[key], key
    nbt_file, = (SOURCE/'i42').glob('*.nbt'); schem_file, = (SOURCE/'i42').glob('*.schem')
    readback = verify_dense(cube, geometry.STATES, nbt_file, schem_file); del cube
    verified = dict(readback, controller=manifest['controller'], port_count=8, ordinary_materials=42,
        connectivity=check['connectivity'], wfv_casing_count=check['wfv_casing_count'],
        voltage_progression=check['voltage_progression'], nbt_file=str(nbt_file.relative_to(SOURCE)),
        schem_file=str(schem_file.relative_to(SOURCE)), nbt_sha256=common.digest(nbt_file),
        schem_sha256=common.digest(schem_file), source_geometry_rerun_for_readback_only=True,
        source_files_written=False, game_verified=False)
    assert verified['nbt_sha256'] == check['nbt_schem_sha256']['nbt']
    assert verified['schem_sha256'] == check['nbt_schem_sha256']['schem']
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES/(now.strftime('%Y%m%d_%H%M%S_%f')+'_batch-10_03of05_I42_V1_WFV_外观已确认')
    evidence = snapshot/'evidence'; evidence.mkdir(parents=True, exist_ok=False)
    (evidence/'previous-current-index.json').write_bytes(before)
    shutil.copy2(HTML_INDEX, evidence/'previous-current-index.html')
    shutil.copy2(__file__, evidence/Path(__file__).name)
    common.write_json(evidence/'approval-message-evidence.json', message)
    common.write_json(evidence/'instance-identity.json', dict(instance=str(INSTANCE), version=version,
        installed_target=str(installed), installed_sha256=installed_hash, instance_files_written=False))
    target = snapshot/SOURCE.name; shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == source_hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I40', 'I41', 'I42'], count=3, required=5,
        deployment_eligible=False, status='approved_archived_waiting_five_machine_threshold',
        game_files_installed=False, game_verified=False,
        deployment_blockers=['尚未累计五台明确批准结构，当前3/5；I37未批准且留到最后，不计数。'])
    row = dict(id='I42', key='i42', candidate_key='i42', approved_version='V1', candidate_version='V1',
        target_voltage_appearance='WFV', status='appearance_approved_archived_waiting_batch',
        approved_at=message['approved_at_hong_kong'], approval_quote=QUOTE, approval_message_id=args.message_id,
        approval_scope=SCOPE, source=str(SOURCE), archive=str(target), dialogue_archive=str(dialogue),
        counts_as_new_machine=True, source_candidate_approved_field=False, external_approval_is_authoritative=True,
        formal_resource_present=False, game_files_installed=False, game_verified=False,
        size_xyz=manifest['size'], block_count=manifest['blocks'], unique_materials=44, ordinary_materials=42,
        controller=manifest['controller'], port_count=8, structure_checks=verified,
        approved_nbt=str(target/nbt_file.relative_to(SOURCE)), approved_nbt_sha256=verified['nbt_sha256'],
        nbt_sha256=verified['nbt_sha256'])
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong',
        original_user_message_time=message['approved_at_hong_kong'], entries=[copy.deepcopy(row)],
        dialogue_archive=str(dialogue), accepted_design_scope=SCOPE, source_files_sha256=source_hashes,
        original_source_files_sha256=source_hashes, source_all_bytes_unchanged=True,
        source_candidate_status_preserved=True, external_approval_is_authoritative=True,
        previous_index_sha256=hashlib.sha256(before).hexdigest(), pending_batch_after_archive=pending,
        source_instance=str(INSTANCE), instance_version=version, game_files_installed=False, game_verified=False)
    common.write_json(snapshot/'确认与校验清单.json', approval)
    (snapshot/'确认接入.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I42 V1批准归档</title>
<style>body{{max-width:1160px;margin:32px auto;padding:0 24px;background:#111b28;color:#e8edf4;font:16px/1.8 system-ui}}a{{color:#acdce7}}img{{width:100%}}</style>
<h1>I42 V1 · 巨构龙骨与步进预制船坞已批准</h1><p>{html.escape(SCOPE)}</p>
<p>负责人原话：{QUOTE}（{message['approved_at_hong_kong']}）。实际消息ID：{html.escape(args.message_id)}。</p>
<p>641×449×295（宽×长×高）；14,747,313实体，44种材料、42种普通材料；WFV主体机壳6,619,923格。主控[320,26,0]位于整宽第321格，8处齐平接口。NBT与Schematic重新逐格回读一致，45个已批准低阶比较通过。</p>
<p>八类工位和在制龙骨是建筑表达；不增加万能构件、一键建造或已实现配方。原候选{len(source_hashes)}个文件全字节不变，内部“待审”保留为批准前历史；当前批准以外部清单为准。</p>
<p>batch-10为I40 V1、I41 V3、I42 V1，共3/5；批准49种，正式安装仍46种。未达到五台阈值，本次未改实例、正式资源、Pattern或I37；I37继续留最后。</p>
<p><a href="确认与校验清单.json">确认清单</a> · <a href="{SOURCE.name}/index.html">获批现物</a> · <a href="{SOURCE.name}/i42/三维评审.html">MC材质三维评审</a> · <a href="../当前归档索引.html">当前归档索引</a></p><img src="{SOURCE.name}/完整预览.png" alt="获批I42 V1完整建筑"></html>''', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip'); package_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for name in package_hashes:
            package.write(snapshot/name, name)
    zip_check = common.verify_zip(bundle, package_hashes)
    bundle.with_suffix('.zip.sha256').write_text(zip_check['sha256']+'\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == source_hashes and INDEX.read_bytes() == before
    assert common.digest(installed) == installed_hash
    row.update(approval_manifest=str(snapshot/'确认与校验清单.json'), archive_zip=str(bundle),
               archive_zip_sha256=zip_check['sha256'])
    index['entries'].append(row)
    assert index['entries'][:-1] == old_entries
    index.update(approved_structure_forms=49, updated_at=now.isoformat(), pending_batch=pending,
        approved_undeployed_count=3, approved_undeployed_machine_ids=['I40', 'I41', 'I42'],
        scope='I40 V1、I41 V3、I42 V1明确批准并完整归档，batch-10为3/5，未部署；正式仍46种；I37留最后，继续I43。')
    index['batch_rule'] = '每累计5台新批准未接入机器先接入再做下一台；当前batch-10为3/5，I37未批准、不计数。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=zip_check['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence/'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records'])+1, time=now.isoformat(),
        reason='负责人明确批准I42 V1并要求下一台', deleted='无', added='I42 V1现物快照、ZIP、真实用户消息及逐格回读证据',
        modified='batch-10由2/5推进3/5；批准49种，正式46种与实例不变；不连带批准RAM、优化、配方或研究',
        purpose='封存明确批准的I42建筑版本，继续I43'))
    common.write_json(INDEX, index)
    HTML_INDEX.write_text(index_html(index), encoding='utf-8')
    links = link_check([HTML_INDEX, snapshot/'确认接入.html', SOURCE/'index.html', target/'i42/三维评审.html'])
    result = dict(passed=True, snapshot=str(snapshot), archive=str(target), zip=str(bundle),
        zip_sha256=zip_check['sha256'], archive_zip_validation=zip_check, verified_structure=verified,
        source_file_count=len(source_hashes), source_all_bytes_unchanged=True,
        original_source_files_sha256=source_hashes, pending_batch=pending, approved_structure_forms=49,
        formal_structure_forms=46, game_files_installed=False, game_verified=False,
        approval_message_id=args.message_id, approved_at=message['approved_at_hong_kong'],
        dialogue_archive=str(dialogue), instance_version=version, instance_jar_unchanged=True,
        previous_entries_unchanged=True, index_sha256=common.digest(INDEX), html_index=str(HTML_INDEX),
        html_index_sha256=common.digest(HTML_INDEX), link_validation=links)
    LOG.mkdir(parents=True, exist_ok=True)
    common.write_json(LOG/'approval-v1-result.json', result)
    print(json.dumps({key:result[key] for key in ('snapshot','zip_sha256','index_sha256','source_file_count',
        'approved_structure_forms','formal_structure_forms','pending_batch','link_validation')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
