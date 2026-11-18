import hashlib
import json
import shutil
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from publish_industrial_datagen_r269_20261113 import replace_element


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/melon-cipher-r282-20261114'
DELIVERY = ROOT / 'deliveries/西瓜ARG_残页译码_玩家体验_R282_20261114'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
RECEIPT = OUT / 'completion.json'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    now = datetime.now(ZoneInfo('Asia/Hong_Kong'))
    stamp = now.isoformat()
    backup = OUT / ('audit-before-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    for name in ('index.html', 'current-summary.json'):
        shutil.copy2(AUDIT / name, backup / name)
    artifact = DELIVERY / 'hk3gtl-0.5.0-melon-cipher-r282-candidate.jar'
    shutil.copy2(ROOT / 'build/libs/hk3gtl-0.5.0.jar', artifact)
    world = DELIVERY / '世界/西瓜来信_残页译码'
    archive = Path(shutil.make_archive(str(DELIVERY / '西瓜来信_残页译码'), 'zip', world.parent, world.name))
    candidate = dict(path=artifact.relative_to(ROOT).as_posix(),
                     sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                     bytes=artifact.stat().st_size, installed=False)
    receipt = dict(
        revision='R282', updated_at=stamp,
        status='手机残页译码与独立玩家地图候选已构建；未安装，等待负责人亲自解密。',
        artifact=candidate,
        build=dict(command='.\\gradlew.bat build -x check -x test --console=plain',
                   exit_code=0, result='BUILD SUCCESSFUL', elapsed='1m 11s',
                   automated_tests_executed=False),
        implementation=[
            '五段连续文字密码；前一段明文作为后续钥匙，未解答案不放进页面回包。',
            '手机桌面真实入口、译文输入提交、正文翻页、已解回看、按需提示与手动译码工作台。',
            '个人解题与提示记录保存到服务端SavedData；草稿与工作台保留至断开连接。',
            '最终来信持久投递个人手机收件箱；不改研究、毕业、旧专属礼包或维度资格。',
            '13项桌面统一绘制、命中、拖动与提示行距。'],
        world=dict(path=world.relative_to(ROOT).as_posix(), archive=archive.relative_to(ROOT).as_posix(),
                   sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                   preparation='全新独立平坦存档；首次进入布置档案室并发满电手机、纸笔、引导书、食物与时钟。',
                   progress='没有预置手机安装、解题、研究、收藏或通关状态。'),
        player_acceptance=dict(owner='负责人本人', status='尚未执行',
                               assistant_game_run=False, assistant_solved=False,
                               existing_instance_or_save_modified=False),
        scope='本次候选覆盖手机文字解密至最终来信；完整西瓜维度、星门地址和旧跨模组路线仍未冻结、未实现。',
        scoring='固定37域、原能力分母及全部研发/历史验收分值保持，不把构建与地图准备计为玩家验收。')
    write_json(RECEIPT, receipt)
    summary = json.loads((backup / 'current-summary.json').read_text('utf8'))
    page = (backup / 'index.html').read_text('utf8')
    summary['previous_installed_candidate'] = summary['repository_candidate']
    summary['repository_candidate'] = candidate
    summary['melon_cipher_r282_completion'] = receipt
    summary['current_work'] = dict(
        system='西瓜来信：手机残页译码与独立玩家体验地图', state=receipt['status'],
        scope='仅仓库源码、构建及独立存档准备；未操作桌面或游戏，未修改现有实例或活动存档，未安装JAR。',
        remaining=['负责人本人完整解密尚未执行。', receipt['scope'],
                   '全库其余16个研发未满分系统保留既有分数和缺项。'],
        evidence=RECEIPT.relative_to(ROOT).as_posix())
    for system in summary['systems']:
        if system['id'] in ('N09', 'N14'):
            system['melon_cipher_r282_review'] = dict(updated_at=stamp,
                implemented='手机连续文字谜题及最终来信候选，已离线构建；独立地图与用品已备。',
                remaining='待负责人亲自解密；不等于完整西瓜维度ARG或游戏验收通过。',
                evidence=RECEIPT.relative_to(ROOT).as_posix(), score_changed=False)
            system['updated_at'] = stamp
    summary['updated_at'] = summary['report_updated_at'] = stamp
    dev = summary['development_metric']['overall_percent']
    acceptance = summary['overall_percent']
    notice = (f'<section id="offline-maximize-current"><h2>西瓜来信 · 玩家解密候选 R282</h2>'
        f'<section class="metrics"><div>研发完成度 · 37域等权<b>{dev:.2f}%</b></div>'
        f'<div>本轮计分增量<b>0.00个百分点</b></div>'
        f'<div>研发满分系统<b>{summary["development_metric"]["completed_domains"]} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{acceptance:.2f}%</b></div></section>'
        f'<p>{escape(receipt["status"])}</p><p>{escape(receipt["scope"])}</p>'
        '<p>本人亲自从首张残页解密；助手只准备程序、独立档案室与用品，没有代通关、游戏操作或安装。'
        '其余发布前实机、联机与性能测试取消决定保持，不能把本次例外扩为助手测试授权。</p>'
        '<p><a href="../melon-cipher-r282-20261114/completion.json">候选与地图回执（无谜底）</a> · '
        f'<a href="../{backup.relative_to(ROOT / "logs").as_posix()}/index.html">修改前历史</a> · {stamp}</p></section>')
    page = replace_element(page, 'section', 'offline-maximize-current', notice)
    for system_id in ('N09', 'N14'):
        marker = f'id="system-{system_id}"'
        start = page.index(marker)
        end = page.index('</summary>', start) + len('</summary>')
        page = page[:end] + ('<section class="notice"><h3>2026-11-14 · 残页译码候选</h3>'
            '<p>五段文字解密、手机输入与持久进度、最终来信和独立地图已备；构建成功，未安装。'
            '待负责人本人从零解密。完整维度与跨模组路线未实现，本轮不加分。</p>'
            '<a href="../melon-cipher-r282-20261114/completion.json">R282交付回执</a></section>') + page[end:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    page = replace_element(page, 'script', 'audit-data', '<script type="application/json" id="audit-data">' + payload + '</script>')
    write_json(AUDIT / 'current-summary.json', summary)
    (AUDIT / 'index.html').write_text(page, encoding='utf8')
    write_json(OUT / 'audit-publication.json', dict(updated_at=stamp,
        backup=backup.relative_to(ROOT).as_posix(), development_percent=dev,
        acceptance_percent=acceptance, domain_count=summary['domain_count'], score_changed=False))
    print(json.dumps(dict(artifact=candidate, world=receipt['world'], development_percent=dev,
                         acceptance_percent=acceptance), ensure_ascii=False))


if __name__ == '__main__':
    main()
