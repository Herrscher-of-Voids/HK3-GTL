"""安装四台原生格雷主控界面构建，并保存独立回执。"""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
import gzip
import json
import re
import shutil
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-four-wonders-native-gt-20261114'
OUT = ROOT / 'deliveries/0005_W01W02W03H01_原生格雷主控_20261114'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
NAME = '0005多方块设计-0.5.0-W01W02W03H01-r1.jar'
KEY = 'four_wonders_0005_native_gt_ui'
QUOTE = '你这个主控是不是格雷自己的主控，因为 W01、W02、W03以及休伯利安，你都没有实装成格雷自己的主控，你帮我将这4个多方块结构实装'
CONTROLLERS = [
    ('W01', 'w01_origin_stellar_concert_court', 'w01_hall.bin.gz'),
    ('W02', 'omnia_autonomous_industrial_matrix', 'w02_19c_a2.bin.gz'),
    ('W03', 'void_anchor_ring', 'w03_c9.bin.gz'),
    ('H01', 'hyperion_flagship', 'hyperion_construction.bin.gz'),
    ('W04', 'w04_thunder_superconducting_axis', 'w04_candidate.bin.gz'),
]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


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
    blueprints = []
    with zipfile.ZipFile(artifact) as jar:
        for role, controller, name in CONTROLLERS:
            resource = 'data/hk3gtl/structures/' + name
            source = ROOT / 'src/main/resources' / resource
            source_sha = digest(source)
            packaged_sha = sha256(jar.read(resource)).hexdigest()
            if source_sha != packaged_sha:
                raise RuntimeError(role + '发行蓝图与生产源不同，停止安装')
            with gzip.open(source, 'rb') as stream:
                _, version, w, h, d, x, y, z, count = struct.unpack('>9i', stream.read(36))
            blueprints.append(dict(role=role, controller='hk3gtl:' + controller, resource=resource,
                                   format_version=version, size_xyz=[w, h, d], anchor_xyz=[x, y, z],
                                   block_count=count, source_sha256=source_sha, packaged_sha256=packaged_sha))
    destination = INSTANCE / 'mods' / NAME
    staged = destination.with_suffix('.jar.pending')
    shutil.copy2(artifact, staged)
    replaced = []
    for path in active_jars():
        replaced.append(dict(path=str(path), backup=str(backup / path.name), sha256=digest(path)))
        shutil.move(str(path), str(backup / path.name))
    staged.replace(destination)
    receipt = dict(installed_at=moment.isoformat(timespec='seconds'), conversation='0005',
                   conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e', authorization=QUOTE,
                   artifact=str(artifact), target=str(destination), sha256=digest(artifact),
                   installed_sha256=digest(destination), bytes=artifact.stat().st_size,
                   instance=str(INSTANCE), instance_baseline='负责人指定增强版3.5路径，未启动客户端复核版本',
                   replaced=replaced, active_hk3gtl_jars=[str(path) for path in active_jars()],
                   blueprints=blueprints, build_log=str(LOG / 'build.log'), build_succeeded=True,
                   implementation='四台已有真实GT注册、完整实体检查与正式配方；本次恢复原生GT生产主页及部件分页，专用功能独立分页。',
                   hyperion='跃迁期间productionReady拒绝生产，保留全部原导航与操作权限。',
                   preserved=['W04七雷A3', '既有蓝图与特效', '研究、二审、物料、EU与HW门槛', '自由通用接口'],
                   game_started=False, game_verified=False, automated_tests_run=False, saves_modified=False,
                   parallel_scope='本工作区现状的0005独立构建，不宣称包含其他对话尚未合并的更新')
    save(LOG / 'installation.json', receipt)
    save(OUT / '安装回执.json', receipt)
    return receipt


def publish(receipt):
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    history = LOG / ('before-publish-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    for path in [REPORT / 'index.html', REPORT / 'current-summary.json',
                 ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']:
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    data = json.loads((REPORT / 'current-summary.json').read_text('utf8'))
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    item = dict(updated_at=now, controllers=receipt['blueprints'][:4],
                native_gt_registration_existing=True, native_gt_ui_integrated=True,
                production_existing=True, installed=True, game_verified=False,
                changes=['原生GT生产状态、能耗、电压、进度和失败原因', '保留GT部件分页，追加结构与专用功能分页',
                         '休伯利安跃迁中禁止生产'],
                installed_jar=receipt['target'], installed_sha256=receipt['installed_sha256'],
                receipt='logs/0005-four-wonders-native-gt-20261114/installation.json',
                remaining=['未执行新版的游戏内完整搭建、成型、生产与特效验收；不增加验收分。',
                           'W02外观批准状态、既有几何及其他待办保持。'])
    system[KEY] = item
    system['updated_at'] = now
    data['current_work'][KEY] = item
    data['updated_at'] = data['report_updated_at'] = now
    data['systems'].sort(key=lambda s: s['percent'])
    page = (REPORT / 'index.html').read_text('utf8')
    note = ('<section class="notice" id="0005-four-wonders-native-gt"><h3>0005 · 四台原生格雷主控页面已接入并安装</h3><p>'
            + escape(now) + ' · W01、W02、W03与休伯利安沿用真实GT注册、完整蓝图和正式配方；恢复原生生产诊断与部件页，'
            '建筑管理及舰船导航独立分页，跃迁期间禁止生产。保留W04七雷A3。未启动游戏、未修改存档、未执行自动化测试；'
            '37域原验收与研发分数、能力分母和外观批准数量保持。</p><p>'
            '<a href="../0005-four-wonders-native-gt-20261114/installation.json">构建与安装回执</a></p></section>')
    page = re.sub(r'(<details id="system-multiblocks"[^>]*><summary>.*?</summary>)',
                  lambda m: m[1] + note, page, count=1, flags=re.S)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    page = re.sub(r'(<script\b[^>]*\bid="audit-data"[^>]*>).*?(</script>)',
                  lambda m: m[1] + payload + m[2], page, count=1, flags=re.S)
    save(REPORT / 'current-summary.json', data)
    (REPORT / 'index.html').write_text(page, 'utf8')
    rule = ('\n\n## 2026-11-14 对话0005：W01／W02／W03／休伯利安原生格雷主控接入\n\n'
            '- 仅适用于对话ID `01a1d6b8-bd81-79d3-a6f4-4f590806cc8e`及委派任务。负责人要求将四台接成格雷主控；'
            '四台此前已有真实GT多方块注册、完整实体核验、通用接口与正式生产，本次补齐被旧自定义界面覆盖的原生入口。\n'
            '- 原生GT生产页显示工作状态、能耗、电压、进度及阻塞原因，保留GT仓室分页；搭建、完整检查、创造巡检和休伯利安导航改为专用分页。'
            '休伯利安跃迁期间拒绝生产。原蓝图、外观状态、特效、研究、二审、供能及资格规则保持，W04七雷A3继续保留。\n'
            '- 独立构建 `' + NAME + '` 已安装到负责人指定增强版实例路径，旧包已备份。'
            '未启动游戏、未修改存档、未执行自动化测试；构建安装不等于完整搭建、成型、运行及特效验收，不恢复实机测试授权。\n'
            '- 回执：`logs/0005-four-wonders-native-gt-20261114/installation.json`；固定报告已同步，37域原验收与研发分数、'
            '分母及批准／正式数量保持。\n')
    for path in [ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']:
        with path.open('a', encoding='utf8') as stream:
            stream.write(rule)
    save(LOG / 'publication.json', dict(updated_at=now, history=str(history), domain_count=len(data['systems']),
                                       overall_percent=data['overall_percent'], multiblocks_percent=system['percent'],
                                       multiblocks_development_percent=system['development_metric']['percent'],
                                       game_verified=False))


if __name__ == '__main__':
    receipt = install()
    publish(receipt)
    print(json.dumps(dict(installed=receipt['target'], sha256=receipt['installed_sha256'],
                          active=receipt['active_hk3gtl_jars']), ensure_ascii=False))
