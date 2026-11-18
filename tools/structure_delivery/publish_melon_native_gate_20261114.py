import difflib
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from publish_industrial_datagen_r269_20261113 import replace_element


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/melon-native-gate-20261114'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
DELIVERY = ROOT / 'deliveries/西瓜ARG_玩家自建星门_20261114'
RECEIPT = 'logs/melon-native-gate-20261114/completion.json'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    now = datetime.now().astimezone()
    stamp = now.isoformat()
    backup = OUT / ('audit-before-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    for name in ('index.html', 'current-summary.json'):
        shutil.copy2(AUDIT / name, backup / name)
    summary = json.loads((backup / 'current-summary.json').read_text('utf8'))
    page = (backup / 'index.html').read_text('utf8')

    DELIVERY.mkdir(parents=True, exist_ok=True)
    artifact = DELIVERY / 'hk3gtl-0.5.0-melon-native-gate-candidate.jar'
    shutil.copy2(ROOT / 'build/libs/hk3gtl-0.5.0.jar', artifact)
    candidate = dict(path=artifact.relative_to(ROOT).as_posix(),
                     sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                     bytes=artifact.stat().st_size, installed=False)
    source_backup = OUT / 'before-from-r283-sources'
    source_archive = json.loads((source_backup / 'archive.json').read_text('utf8'))
    patch = []
    changed_files = []
    for name in source_archive['files']:
        before = source_backup / name
        relative = ('src/main/resources/' if name.startswith('assets/') else 'src/main/java/') + name
        after = ROOT / relative
        current = after.read_text('utf8') if after.exists() else ''
        patch.extend(difflib.unified_diff(before.read_text('utf8').splitlines(True),
                     current.splitlines(True), fromfile='R283/' + relative,
                     tofile=relative if after.exists() else '/dev/null'))
        changed_files.append(relative)
    (OUT / 'changes.patch').write_text(''.join(patch), encoding='utf8')
    build = dict(command='.\\gradlew.bat build -x check -x test --console=plain',
                 exit_code=0, result='BUILD SUCCESSFUL', elapsed='1m 11s',
                 log='logs/melon-native-gate-20261114/build.log', automated_tests_executed=False)
    write_json(OUT / 'build-result.json', build)
    implementation = [
        '删除手机“准备来信之门”按钮、cipher gate子命令及专用门桩物品、注册、模型和中英文文案。',
        '删除玩家出发门自动生成、台账、手机代拨与免费供能；由玩家按GTL进度自行造门、供能、拨号。',
        '航行档案保留该存档原生目的地址；不新增强制毕业状态校验。',
        '保留目的维度星门、个人解谜资格、真实入境门记录、原生返程拨号及返程石。',
        '解谜、实地残页、终点来信与收件人身份逻辑保持；未改写旧跨模组ARG候选。']
    receipt = dict(updated_at=stamp, status='西瓜ARG送门按钮及免费出发门路径已删除，构建成功；新候选未安装，实例沿用此前已安装的R283。',
                   artifact=candidate, build=build, implementation=implementation,
                   changed_files=changed_files, source_baseline=source_archive,
                   source_patch='logs/melon-native-gate-20261114/changes.patch',
                   packaged_resources='构建JAR无Hk3MelonItems或melon_gate_key残留；中英文送门按钮文案已删，返程文案保留。',
                   installed_baseline=summary['repository_candidate'],
                   runtime=dict(installed=False, game_started=False, active_instance_modified=False,
                                active_save_modified=False, player_acceptance='尚未执行；由负责人本人解密。'),
                   scoring='37域、全部能力分母及研发／原验收分数保持，本轮不加分。')
    write_json(OUT / 'completion.json', receipt)
    write_json(DELIVERY / 'candidate.json', receipt)

    summary['previous_repository_candidate'] = summary['repository_candidate']
    summary['repository_candidate'] = candidate
    summary['melon_native_gate_20261114_completion'] = receipt
    summary['current_work'] = dict(system='西瓜ARG：玩家自建星门拨号', state=receipt['status'],
        scope='仅仓库代码、资源、构建与归档；未操作游戏、桌面、活动实例或存档。',
        remaining=['负责人本人解谜与实际通行尚未执行。', '旧跨模组七段草案仍未冻结、未实装；其他系统原缺项保持。'], evidence=RECEIPT)
    for system in summary['systems']:
        if system['id'] in ('N09', 'N14'):
            system['melon_native_gate_20261114_review'] = dict(updated_at=stamp,
                implemented='送门按钮与免费出发门路径已删；保留目的地址、玩家自有星门入境及返程。',
                remaining='新候选未安装；负责人本人解谜与实际通行尚未执行。旧跨模组ARG草案保持。',
                evidence=RECEIPT, score_changed=False)
            system['updated_at'] = stamp
    summary['updated_at'] = summary['report_updated_at'] = stamp
    dev = summary['development_metric']['overall_percent']
    acceptance = summary['overall_percent']
    notice = (f'<section id="offline-maximize-current"><h2>西瓜ARG · 玩家自建星门拨号候选</h2>'
        f'<section class="metrics"><div>研发完成度 · 37域等权<b>{dev:.2f}%</b></div>'
        '<div>本轮计分增量<b>0.00个百分点</b></div>'
        f'<div>研发满分系统<b>{summary["development_metric"]["completed_domains"]} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{acceptance:.2f}%</b></div></section>'
        '<p>“准备来信之门”按钮、门桩物品、自动造出发门及免费供能路径已删除。解谜只留下目的地址，玩家毕业后使用自行制造、供能的原生星门拨号；目的门及既有返程保留。</p>'
        '<p>新候选构建成功、尚未安装；对应实例沿用此前已安装的R283。未操作游戏、桌面、活动实例或存档，未清理旧存档中的门。</p>'
        '<p>负责人本人解谜与实际通行尚未执行；旧跨模组ARG草案继续保留。本轮37域及全部分数、分母保持。</p>'
        f'<p><a href="../melon-native-gate-20261114/completion.json">本轮构建与改动回执</a> · '
        '<a href="../melon-adventure-r283-install-20261114/installation.json">R283既有安装记录</a> · '
        f'<a href="../{backup.relative_to(ROOT / "logs").as_posix()}/index.html">修改前历史</a> · {stamp}</p></section>')
    page = replace_element(page, 'section', 'offline-maximize-current', notice)
    for system_id in ('N09', 'N14'):
        start = page.index(f'id="system-{system_id}"')
        end = page.index('</summary>', start) + len('</summary>')
        page = page[:end] + (f'<section class="notice" id="melon-native-gate-20261114-{system_id}">'
            '<h3>2026-11-14 · 删除送门路径</h3><p>删除“准备来信之门”按钮、门桩及自动造门／免费供能；仅保留目的地址，由玩家自建星门拨号，既有返程保留。'
            '构建成功，新候选未安装；实例仍为此前已安装的R283。分数不变。</p>'
            '<p><a href="../melon-native-gate-20261114/completion.json">本轮回执</a></p></section>') + page[end:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    page = replace_element(page, 'script', 'audit-data', '<script type="application/json" id="audit-data">' + payload + '</script>')
    write_json(AUDIT / 'current-summary.json', summary)
    (AUDIT / 'index.html').write_text(page, encoding='utf8')
    write_json(OUT / 'audit-publication.json', dict(updated_at=stamp, backup=backup.relative_to(ROOT).as_posix(),
        development_percent=dev, acceptance_percent=acceptance, domain_count=summary['domain_count'], score_changed=False))
    print(json.dumps(dict(artifact=candidate, development_percent=dev, acceptance_percent=acceptance)))


if __name__ == '__main__':
    main()
