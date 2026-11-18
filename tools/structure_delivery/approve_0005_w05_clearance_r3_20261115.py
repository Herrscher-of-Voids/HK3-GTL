"""冻结W05 R3外观批准，只替换同一台机器的当前基线。"""
from datetime import datetime
from pathlib import Path
import copy
import hashlib
import html
import json
import re
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_七处穿模修订_R3_20261115'
LOG = ROOT / 'logs/0005-w05-r3-runtime-20261115'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
QUOTE = '可以就这台吧，接入吧，你主控打算放哪里'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    now = datetime.now().astimezone()
    stamp = now.isoformat(timespec='seconds')
    token = now.strftime('%Y%m%d_%H%M%S_%f')
    LOG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    archive = INDEX.parent / (token + '_0005_W05_R3_外观已确认')
    candidate = archive / 'candidate'
    shutil.copytree(SOURCE, candidate)
    shutil.copy2(Path(__file__), archive / Path(__file__).name)
    files = {str(path.relative_to(archive)).replace('\\', '/'): sha(path)
             for path in sorted(archive.rglob('*')) if path.is_file()}
    size = [manifest['size_wdh'][i] for i in (0, 2, 1)]
    controller_source = [0, 12, -345]
    controller = [a - b for a, b in zip(controller_source, manifest['occupied_bounds_xyz']['min'])]
    scope = '批准W05 R3七处穿模修订外观并授权接入现有原生GT主控；替换A4当前基线，不新增机器或批准计数。构建、安装、成型、运行及原生动态分别记录。'
    approval = dict(machine='W05', key='w05', approved_version='0005-R3',
        appearance_approved=True, conversation='0005', conversation_id=manifest['conversation_id'],
        recorded_at=stamp, approval_quote=QUOTE, scope=scope,
        external_approval_is_authoritative=True, source_candidate=str(SOURCE),
        snapshot_directory=str(candidate), source_candidate_approval_field='appearance_approved',
        source_candidate_approved_field=manifest['appearance_approved'],
        source_manifest_approved_field_preserved=True, source_candidate_bytes_preserved=True,
        source_manifest_sha256=sha(SOURCE / 'manifest.json'), source_files_sha256=files,
        size_xyz=size, size_wdh=manifest['size_wdh'], controller=controller,
        controller_source_xyz=controller_source, blocks=manifest['unique_occupied_voxels'],
        component_voxels=manifest['source_component_voxels'],
        material_count=manifest['material_count'], preview_animation_enabled=True,
        native_animation_implementation_separately_recorded=True,
        runtime_integration_authorized=True, installation_authorized=False,
        counts_as_new_machine_this_round=False, game_verified=False,
        acceptance_score_changed=False)
    save(archive / 'approval.json', approval)
    confirmation = (
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W05 R3 · 外观已批准</title>'
        '<style>body{max-width:1200px;margin:30px auto;background:#101926;color:#e5edf7;'
        'font:17px/1.7 system-ui}a{color:#89d7ef}img{width:100%;height:auto}</style>'
        '<h1>W05 · 长风·理想流体环流阵 R3 · 外观已批准</h1>'
        '<p>负责人原话：“' + html.escape(QUOTE) + '”。</p>'
        '<p>批准时间：' + stamp + '；对话0005，ID：' + manifest['conversation_id'] + '。</p>'
        '<p>宽555×深701×高321格，6,646,726唯一占格、73构件、5种现有方块。'
        '保留七处净空修订、已批准配色和删除12根后掠主梁的决定。</p>'
        '<p>主控沿用正前方中轴控制台：原文坐标(0,12,-345)，蓝图归一化坐标(277,12,5)。'
        '运行电压WSV、研究RN-IFF及自由通用接口规则保持；不预装固定仓室。</p>'
        '<p>本次替换同一台W05的外观基线，不新增机器或批准计数。'
        '源候选manifest中的appearance_approved=false保留批准前历史；本页及approval.json记录当前批准。'
        '原生动态、构建及游戏验收分别记录，本批准不授权安装。</p>'
        '<p><a href="candidate/三维评审.html">冻结候选三维评审</a> · '
        '<a href="approval.json">批准及SHA256清单</a> · '
        '<a href="../当前归档索引.html">当前批准索引</a></p>'
        '<img src="candidate/整体预览.png" alt="W05 R3冻结候选整体预览"></html>')
    (archive / '确认接入.html').write_text(confirmation, 'utf8')
    packed = archive.with_suffix('.zip')
    with zipfile.ZipFile(packed, 'x', compression=zipfile.ZIP_STORED) as output:
        for path in sorted(archive.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(archive))
    digest = sha(packed)
    packed.with_suffix('.zip.sha256').write_text(digest + '  ' + packed.name + '\n', 'utf8')

    index = json.loads(INDEX.read_text('utf8'))
    previous = copy.deepcopy(next(entry for entry in index['entries'] if entry['id'] == 'W05'))
    backup = LOG / ('approval-before-' + token)
    backup.mkdir()
    for path in (INDEX, INDEX.with_suffix('.html')):
        shutil.copy2(path, backup / path.name)
    entry = dict(id='W05', key='w05', candidate_key='w05_0005_clearance_r3_20261115',
        approved_version='0005-R3', appearance_approved=True, approved_at=stamp,
        current_baseline=True, status='appearance_approved_runtime_integration_authorized_pending_receipts',
        approval_quote=QUOTE, approval_scope=scope, conversation='0005',
        conversation_id=manifest['conversation_id'], source=str(SOURCE), archive=str(candidate),
        approval_manifest=str(archive / 'approval.json'), archive_zip=str(packed),
        archive_zip_sha256=digest, external_approval_is_authoritative=True,
        source_candidate_approved_field=False, source_candidate_approval_field='appearance_approved',
        source_candidate_bytes_preserved=True, counts_as_new_machine=False,
        counts_as_new_machine_this_round=False, size_xyz=size,
        block_count=manifest['unique_occupied_voxels'], component_voxels=manifest['source_component_voxels'],
        unique_materials=manifest['material_count'], controller=controller,
        controller_source_xyz=controller_source, controller_id='hk3gtl:w05_ideal_fluid_circulation_array',
        port_count=0, fixed_interface_positions=[], target_voltage_appearance='HDV',
        target_voltage='WSV', research='RN-IFF',
        production_recipe='hk3gtl:wonder_ideal_flow_exchange_matrix',
        interface_policy='保留既有自由通用接口规则；本蓝图不预装固定仓室。',
        animation_enabled=False, preview_animation_enabled=True,
        animation_scope='原候选运动与特效为网页预览；原生游戏实现另行记录。',
        formal_resource_present=False, runtime_blueprint_integrated=False,
        runtime_integration_authorized=True, installation_authorized=False,
        game_files_installed=False, installed_this_round=False, game_verified=False,
        target_instance_version='增强版3.9', current_review_entry=str(archive / '确认接入.html'),
        retired_baseline=dict(candidate=previous['approved_version'], current_baseline=False,
            decision='R3取代A4作为当前设计和接入基线；A4批准、运行资源及安装回执保留历史。',
            historical_archive=previous['archive'], historical_approval_manifest=previous['approval_manifest']))
    index['historical_replaced_appearances'].append(previous)
    index['historical_appearance_revision_approvals'].append(copy.deepcopy(index['latest_appearance_revision_approval']))
    index['historical_approval_snapshots'].append(copy.deepcopy(index['latest_approval_snapshot']))
    position = next(n for n, old in enumerate(index['entries']) if old['id'] == 'W05')
    index['entries'][position] = entry
    index['latest_appearance_revision_approval'] = copy.deepcopy(entry)
    index['latest_approval_snapshot'] = dict(snapshot=str(archive), approval=str(archive / 'approval.json'),
        zip=str(packed), zip_sha256=digest, kind='W05 R3同机外观基线替换与仓库接入授权')
    index['scope'] = ('批准' + str(index['approved_structure_forms']) + '／传统JSON正式资源'
        + str(index['formal_structure_forms']) + '／Hk3ApprovedArchitecture.IDS及正式compact'
        + str(index['formal_compact_forms']) + '；batch-12为'
        + str(index['pending_batch']['count']) + '/' + str(index['pending_batch']['required'])
        + '。W05当前批准外观改为R3七处穿模修订，接入回执另记；A4历史安装保留，R3未安装。')
    index['_change_records'].append(dict(record=index['_change_records'][-1]['record'] + 1,
        time=stamp, reason=QUOTE, previous_index=str(backup / INDEX.name),
        added='W05 R3完整不可变批准快照；保留候选批准前字段及A4全量历史。',
        modified='同一台W05的当前外观基线A4→R3；批准数量、正式资源数量与batch计数保持，接入及构建另据回执。'))
    index['updated_at'] = stamp
    current_html = INDEX.with_suffix('.html').read_text('utf8')
    current_html = re.sub(r'(<h1>当前批准索引</h1><p>).*?(</p>)',
        lambda match: match.group(1) + html.escape(index['scope']) + match.group(2),
        current_html, count=1, flags=re.S)
    current_html = current_html.replace('id="0005-w05-a4-current"', 'id="0005-w05-a4-history"', 1)
    current_html = current_html.replace(' · W05 A4外观已批准，', ' · 历史记录：W05 A4外观曾批准，', 1)
    link = archive.name + '/确认接入.html'
    row = ('<tr><td>W05</td><td><a href="' + html.escape(link) + '">0005-R3（外观已批准）</a></td>'
        '<td>HDV配色／WSV运行</td><td>R3当前基线；仓库接入回执另记，未安装及游戏验收</td><td>False</td></tr>')
    current_html = re.sub(r'<tr><td>W05</td>.*?</tr>', lambda match: row, current_html, count=1, flags=re.S)
    notice = ('<p id="0005-w05-r3-current">' + stamp + ' · W05当前批准基线为R3七处穿模修订，'
        '<a href="' + html.escape(link) + '">冻结候选与批准记录</a>。'
        '主控原文(0,12,-345)，蓝图(277,12,5)。同机替换，不新增批准计数；R3未安装或游戏验收。</p>')
    current_html = current_html.replace('<input ', notice + '<input ', 1)
    save(INDEX, index)
    INDEX.with_suffix('.html').write_text(current_html, 'utf8')
    receipt = dict(recorded_at=stamp, approval_quote=QUOTE, archive=str(archive),
        candidate_snapshot=str(candidate), approval_manifest=str(archive / 'approval.json'),
        archive_zip=str(packed), archive_zip_sha256=digest, previous_index=str(backup / INDEX.name),
        approved_before=index['approved_structure_forms'], approved_after=index['approved_structure_forms'],
        traditional_json_formal_count=index['formal_structure_forms'],
        formal_compact_count=index['formal_compact_forms'], pending_batch_count=index['pending_batch']['count'],
        source_manifest_sha256=approval['source_manifest_sha256'], copied_candidate_files=len(files) - 1,
        source_candidate_modified=False, source_manifest_approved_field_preserved=True,
        current_baseline='0005-R3', previous_baseline='0005-A4',
        controller_source_xyz=controller_source, controller_xyz=controller,
        runtime_modified=False, jar_built=False, installed=False, game_verified=False,
        acceptance_score_changed=False, shared_audit_agents_rules_modified=False)
    save(LOG / 'approval.json', receipt)
    for path in archive.rglob('*'):
        if path.is_file():
            path.chmod(0o444)
    packed.chmod(0o444)
    packed.with_suffix('.zip.sha256').chmod(0o444)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
