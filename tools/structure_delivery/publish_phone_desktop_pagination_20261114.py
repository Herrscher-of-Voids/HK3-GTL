import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from publish_industrial_datagen_r269_20261113 import replace_element

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/phone-desktop-pagination-20261114'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
DELIVERY = ROOT / 'deliveries/手机桌面九宫格分页_20261114'
RECEIPT = 'logs/phone-desktop-pagination-20261114/completion.json'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat()
    backup = OUT / ('audit-before-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    for name in ('index.html', 'current-summary.json'):
        shutil.copy2(AUDIT / name, backup / name)
    summary = json.loads((backup / 'current-summary.json').read_text('utf8'))
    page = (backup / 'index.html').read_text('utf8')
    DELIVERY.mkdir(parents=True, exist_ok=True)
    artifact = DELIVERY / 'hk3gtl-0.5.0-phone-desktop-pages-candidate.jar'
    shutil.copy2(ROOT / 'build/libs/hk3gtl-0.5.0.jar', artifact)
    candidate = dict(path=artifact.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(), bytes=artifact.stat().st_size, installed=False)
    state = '手机桌面改为3×3分页：首屏9项、次屏4项，保留应用顺序、拖动及原有入口；构建成功，新候选未安装。'
    completion = dict(updated_at=stamp, status=state, artifact=candidate,
        implementation=['桌面13项应用按每页9项显示，提供上一页、下一页与页码。', '桌面渲染、点击、提示和拖动统一使用分页索引，正文及子应用分页保持。'],
        changed_files=['src/main/java/com/sirin/hk3gtl/client/phone/Hk3PhoneDesktop.java', 'src/main/java/com/sirin/hk3gtl/client/phone/Hk3PhoneScreen.java'],
        build=dict(command='.\\gradlew.bat build -x check -x test --console=plain', exit_code=0, result='BUILD SUCCESSFUL', log='logs/phone-desktop-pagination-20261114/build.log', automated_tests_executed=False),
        runtime=dict(installed=False, game_started=False, active_instance_modified=False, active_save_modified=False, game_verified=False),
        installed_baseline='logs/melon-adventure-r283-install-20261114/installation.json',
        source_backup='logs/phone-desktop-pagination-20261114/before', report_backup=backup.relative_to(ROOT).as_posix(), scoring='37域、全部能力分母、研发及历史验收分数与排序保持。')
    write_json(OUT / 'completion.json', completion)
    write_json(DELIVERY / 'candidate.json', completion)
    summary['previous_repository_candidate'] = summary['repository_candidate']
    summary['repository_candidate'] = candidate
    summary['phone_desktop_pagination_20261114_completion'] = completion
    summary['current_work'] = dict(system='手机桌面九宫格分页', state=state, scope='仅仓库代码、构建与归档；实例沿用此前已安装的R283。', remaining=['本轮未进行游戏画面或操作验收；其余系统既有缺项保持。'], evidence=RECEIPT)
    system = next(system for system in summary['systems'] if system['id'] == 'N09')
    system['phone_desktop_pagination_20261114_review'] = dict(updated_at=stamp, implemented=state, remaining='新候选未安装、未实测；不增加原分。', evidence=RECEIPT, score_changed=False)
    system['updated_at'] = stamp
    summary['updated_at'] = summary['report_updated_at'] = stamp
    dev, acceptance = summary['development_metric']['overall_percent'], summary['overall_percent']
    notice = (f'<section id="offline-maximize-current"><h2>手机桌面 · 九宫格分页候选</h2><section class="metrics"><div>研发完成度 · 37域等权<b>{dev:.2f}%</b></div><div>本轮计分增量<b>0.00个百分点</b></div>'
        f'<div>研发满分系统<b>{summary["development_metric"]["completed_domains"]} / 37</b></div><div>原验收完成度 · 保留<b>{acceptance:.2f}%</b></div></section><p>{state}</p>'
        '<p>本轮未安装、未操作游戏、桌面、活动实例或存档，未进行游戏验收。实例沿用此前已安装的R283；全部37域分数、分母和排序保持。</p>'
        f'<p><a href="../phone-desktop-pagination-20261114/completion.json">本轮构建与分页回执</a> · <a href="../melon-adventure-r283-install-20261114/installation.json">R283既有安装记录</a> · <a href="../{backup.relative_to(ROOT / "logs").as_posix()}/index.html">修改前历史</a> · {stamp}</p></section>')
    page = replace_element(page, 'section', 'offline-maximize-current', notice)
    end = page.index('</summary>', page.index('id="system-N09"')) + len('</summary>')
    page = page[:end] + f'<section class="notice" id="phone-desktop-pages-20261114-N09"><h3>2026-11-14 · 手机桌面分页</h3><p>{state}</p><p>本轮未实测、未安装，既有研发100%及历史验收100%保持。<a href="../phone-desktop-pagination-20261114/completion.json">本轮回执</a></p></section>' + page[end:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    page = replace_element(page, 'script', 'audit-data', '<script type="application/json" id="audit-data">' + payload + '</script>')
    write_json(AUDIT / 'current-summary.json', summary)
    (AUDIT / 'index.html').write_text(page, encoding='utf8')
    print(json.dumps(dict(artifact=candidate, development_percent=dev, acceptance_percent=acceptance)))


if __name__ == '__main__':
    main()
