from datetime import datetime, timedelta, timezone
from pathlib import Path
import copy
import hashlib
import html
import json
import re
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115'
LOG = ROOT / 'logs/0005-w05-a4-approval-20261115'
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
QUOTE = '就这个吧，先实装到游戏，下一台W06吧'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat(timespec='seconds')
    token = now.strftime('%Y%m%d_%H%M%S_%f')
    LOG.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    if any(entry['id'] == 'W05' for entry in index['entries']):
        raise ValueError('W05已在批准索引中，不重复归档或计数。')
    backup = LOG / ('before-approval-' + token)
    backup.mkdir()
    for path in (INDEX, INDEX.with_suffix('.html')):
        shutil.copy2(path, backup / path.name)
    previous_count = index['approved_structure_forms']
    archive = INDEX.parent / (token + '_0005_W05_A4_外观已确认')
    archive.mkdir()
    candidate = archive / 'candidate'
    shutil.copytree(SOURCE, candidate)
    shutil.copy2(Path(__file__), archive / Path(__file__).name)
    files = {str(path.relative_to(archive)).replace('\\', '/'): sha(path)
             for path in sorted(archive.rglob('*')) if path.is_file()}
    scope = '批准W05 A4建筑外观并授权先接入游戏，再推进W06；本次仅冻结批准，构建、安装、GT成型、运行与特效按独立回执记录。'
    approval = dict(machine='W05', key='w05', approved_version='A4', appearance_approved=True,
        conversation='0005', conversation_id=manifest['conversation_id'], recorded_at=stamp,
        approval_quote=QUOTE, scope=scope, external_approval_is_authoritative=True,
        source_candidate=str(SOURCE), snapshot_directory=str(candidate),
        source_candidate_approval_field='appearance_approved',
        source_candidate_approved_field=manifest['appearance_approved'],
        source_manifest_approved_field_preserved=True, source_candidate_bytes_preserved=True,
        source_manifest_sha256=sha(SOURCE / 'manifest.json'),
        size_xyz=manifest['size_xyz'], size_wdh=manifest['size_wdh'],
        controller=manifest['controller'], blocks=manifest['block_count'],
        material_count=manifest['material_count'], source_files_sha256=files,
        runtime_integration_authorized=True, installation_authorized=True,
        game_verified=False, acceptance_score_changed=False)
    save(archive / 'approval.json', approval)
    confirmation = (
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W05 A4 · 外观已批准</title>'
        '<style>body{max-width:1200px;margin:30px auto;background:#101926;color:#e5edf7;'
        'font:17px/1.7 system-ui}a{color:#89d7ef}img{width:100%;height:auto}</style>'
        '<h1>W05 · 温蒂风翼与渴望之心 A4 · 外观已批准</h1>'
        '<p>负责人原话：“' + html.escape(QUOTE) + '”。</p>'
        '<p>批准时间：' + stamp + '；对话0005，ID：' + manifest['conversation_id'] + '。</p>'
        '<p>宽1001×深841×高407格，21,746,510块；HDV风息绿外观、WSV运行身份，全静态。'
        '此页记录外观批准和游戏接入授权，构建、安装、GT成型、运行及特效验收分别记录。</p>'
        '<p>candidate目录为完整原候选冻结副本，原manifest中的appearance_approved=false保留批准前历史；'
        '本页与外部approval.json记录当前批准，定位红石标记不等于真实GT主控。</p>'
        '<p><a href="candidate/index.html">冻结候选三维评审</a> · '
        '<a href="approval.json">批准及SHA256清单</a> · '
        '<a href="../当前归档索引.html">当前批准索引</a></p>'
        '<img src="candidate/整体预览.png" alt="W05 A4冻结候选整体预览"></html>'
    )
    (archive / '确认接入.html').write_text(confirmation, encoding='utf-8')
    packed = archive.with_suffix('.zip')
    with zipfile.ZipFile(packed, 'x', compression=zipfile.ZIP_STORED) as output:
        for path in sorted(archive.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(archive))
    digest = sha(packed)
    packed.with_suffix('.zip.sha256').write_text(digest + '  ' + packed.name + '\n', encoding='utf-8')
    entry = dict(id='W05', key='w05', candidate_key='w05_0005_wendy_wings_a4_20261115',
        approved_version='0005-A4', appearance_approved=True, approved_at=stamp,
        status='appearance_approved_game_integration_authorized_pending_receipts',
        approval_quote=QUOTE, approval_scope=scope,
        conversation='0005', conversation_id=manifest['conversation_id'],
        source=str(SOURCE), archive=str(candidate), approval_manifest=str(archive / 'approval.json'),
        archive_zip=str(packed), archive_zip_sha256=digest,
        external_approval_is_authoritative=True, source_candidate_approved_field=False,
        source_candidate_approval_field='appearance_approved', source_candidate_bytes_preserved=True,
        counts_as_new_machine=True, current_baseline=True,
        size_xyz=manifest['size_xyz'], block_count=manifest['block_count'],
        unique_materials=manifest['material_count'], controller=manifest['controller'], port_count=0,
        target_voltage_appearance='HDV', target_voltage='WSV', animation_enabled=False,
        formal_resource_present=False, runtime_integration_authorized=True, installation_authorized=True,
        game_files_installed=False, game_verified=False,
        approved_nbt=str(candidate / (manifest['name'] + '.nbt')),
        approved_nbt_sha256=sha(candidate / (manifest['name'] + '.nbt')),
        current_review_entry=str(archive / '确认接入.html'))
    index['entries'].append(entry)
    index['approved_structure_forms'] = len(index['entries'])
    index['approved_undeployed_machine_ids'].append('W05')
    index['approved_undeployed_count'] = len(index['approved_undeployed_machine_ids'])
    batch = index['pending_batch']
    batch['approved_machine_ids'].append('W05')
    batch['count'] = len(batch['approved_machine_ids'])
    batch['deployment_eligible'] = batch['count'] >= batch['required']
    batch['note'] = '外观批准4/5；W04历史单独安装及I37源码接入记录保留。负责人另授权W05 A4先接入游戏；构建安装回执待补，不因此部署其他建筑。'
    index['historical_approval_snapshots'].append(copy.deepcopy(index['latest_approval_snapshot']))
    index['latest_approval_snapshot'] = dict(snapshot=str(archive), approval=str(archive / 'approval.json'),
        zip=str(packed), zip_sha256=digest, kind='W05 A4首次外观批准与游戏接入授权')
    index['latest_new_machine_approval'] = entry
    index['scope'] = '批准61／传统JSON正式资源52／Hk3ApprovedArchitecture.IDS及正式compact53；batch-12为4/5。W05 A4外观已批准并授权先接入游戏，构建安装另据回执；W02当前批准基线为11月10日19C船坞A2。'
    index['_change_records'].append(dict(record=index['_change_records'][-1]['record'] + 1,
        time=stamp, reason=QUOTE, previous_index=str(backup / INDEX.name),
        added='W05 A4首次外观批准与完整不可变候选归档，授权先接入游戏。',
        modified='批准60→61、batch-12由3/5→4/5；传统JSON52及IDS/compact53保持，构建安装和实机状态不在本归档任务认定。'))
    index['updated_at'] = stamp
    current_html = INDEX.with_suffix('.html').read_text(encoding='utf-8')
    current_html = re.sub(r'(<h1>当前批准索引</h1><p>).*?(</p>)',
        lambda match: match.group(1) + html.escape(index['scope']) + match.group(2),
        current_html, count=1, flags=re.S)
    link = archive.name + '/确认接入.html'
    row = ('<tr><td>W05</td><td><a href="' + html.escape(link) + '">0005-A4（外观已批准）</a></td>'
        '<td>HDV外观／WSV运行</td><td>外观已批准；授权先接入游戏，构建安装另据回执</td><td>False</td></tr>')
    current_html = current_html.replace('</tbody>', row + '</tbody>', 1)
    notice = ('<p id="0005-w05-a4-current">' + stamp + ' · W05 A4外观已获批准；'
        '<a href="' + html.escape(link) + '">完整冻结候选与批准记录</a>。'
        '本次新增1台，批准61；传统JSON52、正式compact53保持，batch-12为4/5。原候选批准前字段原样保留。</p>')
    current_html = current_html.replace('<input ', notice + '<input ', 1)
    save(INDEX, index)
    INDEX.with_suffix('.html').write_text(current_html, encoding='utf-8')
    receipt = dict(recorded_at=stamp, archive=str(archive), candidate_snapshot=str(candidate),
        approval_manifest=str(archive / 'approval.json'), archive_zip=str(packed),
        archive_zip_sha256=digest, approval_quote=QUOTE, conversation='0005',
        conversation_id=manifest['conversation_id'], previous_index=str(backup / INDEX.name),
        approved_before=previous_count, approved_after=index['approved_structure_forms'],
        traditional_json_formal_count=index['formal_structure_forms'],
        formal_compact_count=index['formal_compact_forms'], pending_batch_count=batch['count'],
        copied_candidate_files=len(files) - 1, source_manifest_sha256=approval['source_manifest_sha256'],
        original_candidate_modified=False, runtime_modified=False, jar_built=False,
        installed=False, game_verified=False, acceptance_score_changed=False,
        shared_audit_agents_rules_modified=False)
    save(LOG / 'receipt.json', receipt)
    for path in archive.rglob('*'):
        if path.is_file():
            path.chmod(0o444)
    packed.chmod(0o444)
    packed.with_suffix('.zip.sha256').chmod(0o444)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
