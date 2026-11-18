"""安装0005七雷A3独立构建，记录批准、生产蓝图与实际安装状态。"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-a3-game-20261114'
OUT = ROOT / 'deliveries/0005_W04_七雷A3_游戏接入_20261114'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
APPROVAL = ROOT / 'deliveries/多方块确认归档/20261114_064616_790687_0005_W04_A3_仅外观已确认'
PREVIEW = 'deliveries/0005_W04_七雷取能天枢_构图A3_20261114'
NAME = '0005多方块设计-0.5.0-W04A3-r1.jar'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
KEY = 'w04_0005_seven_thunders_a3'
QUOTE = '不是，这一台你要实装到游戏里呀，先实装，然后再下一台'


def load(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def active_jars():
    result = []
    for path in (INSTANCE / 'mods').glob('*.jar'):
        with zipfile.ZipFile(path) as jar:
            if 'META-INF/mods.toml' not in jar.namelist():
                continue
            text = jar.read('META-INF/mods.toml').decode('utf8')
        records = re.findall(r'^\[\[mods\]\]\s*(.*?)(?=^\[\[|\Z)', text, re.M | re.S)
        if any(re.search(r'^modId\s*=\s*[\"\x27]hk3gtl[\"\x27]', record, re.M) for record in records):
            result.append(path)
    return result


def install():
    moment = datetime.now(timezone(timedelta(hours=8)))
    OUT.mkdir(exist_ok=True)
    backup = LOG / ('before-install-' + moment.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir()
    artifact = OUT / NAME
    shutil.copy2(ROOT / 'build/libs' / NAME, artifact)
    resource_name = 'data/hk3gtl/structures/w04_candidate.bin.gz'
    with zipfile.ZipFile(artifact) as jar:
        packaged_sha = sha256(jar.read(resource_name)).hexdigest()
        metadata = json.loads(jar.read('data/hk3gtl/structures/w04_approved.json'))
    resource_sha = digest(ROOT / 'src/main/resources' / resource_name)
    if packaged_sha != resource_sha:
        raise RuntimeError('JAR内七雷A3蓝图与生产资源不同，停止安装')
    destination = INSTANCE / 'mods' / NAME
    staged = destination.with_suffix('.jar.pending')
    shutil.copy2(artifact, staged)
    replaced = []
    for path in active_jars():
        previous = dict(path=str(path), backup=str(backup / path.name), sha256=digest(path))
        shutil.move(str(path), str(backup / path.name))
        replaced.append(previous)
    staged.replace(destination)
    receipt = dict(installed_at=moment.isoformat(timespec='seconds'), conversation='0005',
                   conversation_id=metadata['conversation_id'], authorization=QUOTE,
                   instance=str(INSTANCE), instance_version='增强版3.5', jar=str(artifact), target=str(destination),
                   sha256=digest(artifact), installed_sha256=digest(destination), bytes=artifact.stat().st_size,
                   replaced=replaced, active_hk3gtl_jars=[str(path) for path in active_jars()],
                   blueprint_sha256=resource_sha, packaged_blueprint_sha256=packaged_sha,
                   blueprint_export=load(LOG / 'blueprint-export.json'), metadata=metadata,
                   build_log=str(LOG / 'build.log'), build_succeeded=True,
                   registered_controller='hk3gtl:w04_thunder_superconducting_axis',
                   shared_source='终端搭建、完整实体检查及自家JEI共用w04_candidate.bin.gz',
                   production='沿用RN-SEM、WSV、冷却剂与正式极化材料工艺；取能构图不新增免费发电',
                   appearance_approved=True, installed=True, game_started=False, game_verified=False,
                   automated_tests_run=False, saves_modified=False,
                   parallel_scope='本工作区现状的0005独立构建，不宣称包含其他对话尚未合并的更新')
    save(LOG / 'installation.json', receipt)
    save(OUT / '安装回执.json', receipt)
    shutil.copy2(APPROVAL / '确认与校验清单.json', OUT / '外观批准.json')
    print(json.dumps(dict(installed=str(destination), sha256=receipt['sha256'],
                          active=receipt['active_hk3gtl_jars']), ensure_ascii=False), flush=True)


def publish():
    receipt = load(LOG / 'installation.json')
    approval = load(APPROVAL / '归档回执.json')
    moment = datetime.now(timezone(timedelta(hours=8)))
    now = moment.isoformat(timespec='seconds')
    history = LOG / ('before-publish-' + moment.strftime('%Y%m%d-%H%M%S-%f'))
    history.mkdir()
    index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
    index_html = index_path.with_suffix('.html')
    paths = [index_path, index_html, REPORT / 'index.html', REPORT / 'current-summary.json',
             ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']
    for path in paths:
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    index = load(index_path)
    entry = dict(id='W04', key='w04', candidate_key=KEY, approved_version='0005-A3',
                 status='appearance_approved_runtime_blueprint_installed_game_unverified',
                 approved_at=approval['recorded_at'], approval_quote='就这个吧，我们下一台吧，没时间了，有问题之后再改吧',
                 implementation_quote=QUOTE, conversation_id=receipt['conversation_id'],
                 source=PREVIEW, archive=approval['snapshot'], approval_manifest=approval['approval_manifest'],
                 archive_zip=approval['zip'], archive_zip_sha256=approval['zip_sha256'],
                 external_approval_is_authoritative=True, source_candidate_approved_field=False,
                 counts_as_new_machine=True, size_xyz=[841, 594, 781], block_count=10536136,
                 unique_materials=13, controller=[420, 18, 739], port_count=0,
                 formal_resource_present=True, game_files_installed=True, game_verified=False,
                 installed_jar=receipt['target'], installed_jar_sha256=receipt['installed_sha256'],
                 installation_receipt='logs/0005-w04-a3-game-20261114/installation.json')
    index['entries'].append(entry)
    index['approved_structure_forms'] += 1
    batch = index['pending_batch']
    batch['approved_machine_ids'].append('W04')
    batch['count'] += 1
    batch['individually_authorized_installed_ids'] = ['W04']
    batch['note'] = '外观批准2/5；负责人单独授权W04 A3接入及安装，其他待批结构不随之安装。'
    index['scope'] = '批准59／传统正式架构52；batch-12为2/5。W04 A3另以完整奇观蓝图接入并安装，未游戏验收。'
    index['approved_blueprint_bindings'] = [entry]
    index['latest_appearance_revision_approval'] = entry
    index['updated_at'] = now
    index['_change_records'].append(dict(record=len(index['_change_records']) + 1, time=now,
                                        reason=QUOTE, previous_index=str(history / index_path.relative_to(ROOT)),
                                        added='W04七雷A3批准及增强版3.5安装',
                                        modified='批准59；传统正式架构52及验收分数保持，奇观完整蓝图单列。'))
    save(index_path, index)
    page = index_html.read_text('utf8')
    page = re.sub(r'(<h1>当前批准索引</h1>)<p>.*?</p>',
                  lambda m: m[1] + '<p>' + escape(index['scope']) + '</p>', page, count=1, flags=re.S)
    rows = ''.join('<tr><td>' + escape(str(e['id'])) + '</td><td>'
                   + escape(str(e.get('approved_version', '历史记录'))) + '</td><td>'
                   + escape(str(e.get('target_voltage', ''))) + '</td><td>'
                   + escape(str(e.get('status', ''))) + '</td><td>'
                   + str(e.get('game_verified', False)) + '</td></tr>' for e in index['entries'])
    page = re.sub(r'<tbody>.*?</tbody>', '<tbody>' + rows + '</tbody>', page, count=1, flags=re.S)
    index_html.write_text(page, 'utf8')

    data = load(REPORT / 'current-summary.json')
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    item = system[KEY]
    item['preview_controller_placeholder_state'] = item.pop('controller_placeholder_state')
    item.update(approved=True, appearance_approved=True, approval_quote=entry['approval_quote'],
                scope='A3完整实体蓝图已接入真实主控并安装；刀身取能构图与既定极化材料生产分别记录',
                approval_archive=approval['archive'], controller_registered=True,
                controller_id=receipt['registered_controller'], runtime_controller_xyz=[420, 18, 739],
                runtime_blueprint='src/main/resources/data/hk3gtl/structures/w04_candidate.bin.gz',
                runtime_blueprint_sha256=receipt['blueprint_sha256'], runtime_blueprint_integrated=True,
                production_implemented=True, installed=True, installed_jar=receipt['target'],
                installed_jar_sha256=receipt['sha256'], game_verified=False, updated_at=now,
                installation_receipt=entry['installation_receipt'],
                remaining=['未执行游戏搭建、成型与运行验收；不补验收分。',
                           '刀身取能为外观叙事；正式极化材料生产仍消耗既定EU、HW及冷却剂。',
                           '建筑高594格，须使用已启用足够建高合同的世界；不缩放或裁切。'])
    system['updated_at'] = now
    data['current_work'][KEY] = deepcopy(item)
    data['current_work']['w04_0005_a3_installation'] = receipt
    data['current_work']['w04_0005_next_step'] = '七雷A3接入及安装已完成，接下来评审W05风之律者双层回流A1。'
    data['updated_at'] = now
    data['report_updated_at'] = now
    data['systems'].sort(key=lambda s: s['percent'])
    page = (REPORT / 'index.html').read_text('utf8')
    note = (now + ' · 0005 W04七雷A3外观已批准；完整10,536,136块蓝图已接真实主控、终端搭建、'
            '整体验证与JEI，并以独立命名JAR安装增强版3.5。未启动游戏或执行成型运行验收；'
            '37域评分及能力分母保持。')
    page = re.sub(r'<p class="notice" id="0005-w04-a3">.*?</p>',
                  lambda m: '<p class="notice" id="0005-w04-a3">' + escape(note)
                  + ' <a href="../../' + PREVIEW + '/三维布局.html">七雷A3</a> · '
                  '<a href="../0005-w04-a3-game-20261114/installation.json">安装回执</a></p>',
                  page, count=1, flags=re.S)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    page = re.sub(r'(<script\b[^>]*\bid="audit-data"[^>]*>).*?(</script>)',
                  lambda m: m[1] + payload + m[2], page, count=1, flags=re.S)
    save(REPORT / 'current-summary.json', data)
    (REPORT / 'index.html').write_text(page, 'utf8')
    rule = ('\n\n## 2026-11-14 对话0005：W04七雷A3批准并先接入游戏\n\n'
            '- 仅适用于对话ID `01a1d6b8-bd81-79d3-a6f4-4f590806cc8e`（0005多方块设计）及委派任务。'
            '负责人批准七雷A3，并明确要求“' + QUOTE + '”；先接入和安装本台，再推进W05。\n'
            '- A3批准原件保留；外部批准归档：`' + approval['archive'] + '`。'
            '完整841×781×594、10,536,136块蓝图替换旧W04生产资源，主控仅替换锚点一格，'
            '终端搭建、完整实体检查及自家JEI共用源。非主控实体位置沿用自由通用接口。\n'
            '- 真实主控 `hk3gtl:w04_thunder_superconducting_axis`；沿用RN-SEM、WSV及正式极化材料工艺，'
            '不把取能构图擅改为免费EU/HW发电。594格高度依赖既有世界建高合同，不裁切、缩放或改旧存档。\n'
            '- 独立JAR `' + NAME + '` 已构建并安装增强版3.5，旧包已备份；'
            '本次具体安装授权不恢复助手桌面、游戏或实机测试。未启动游戏，未修改存档，未执行自动化测试。'
            '安装不等于整机搭建、成型、运行及特效验收。\n'
            '- 回执：`logs/0005-w04-a3-game-20261114/installation.json`。'
            '批准59、传统正式架构52；本台完整奇观蓝图另列，不改37域评分、能力分母与历史证据。\n')
    for path in [ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']:
        with path.open('a', encoding='utf8') as stream:
            stream.write(rule)
    save(LOG / 'publication.json', dict(updated_at=now, history=str(history), systems=len(data['systems']),
                                       overall_percent=data['overall_percent'], multiblocks_percent=system['percent'],
                                       approved_structure_forms=index['approved_structure_forms'],
                                       formal_structure_forms=index['formal_structure_forms'], game_verified=False))
    print(json.dumps(dict(published=True, report=str(REPORT / 'index.html'),
                          systems=len(data['systems']), overall_percent=data['overall_percent']), ensure_ascii=False))


if __name__ == '__main__':
    install()
    publish()
