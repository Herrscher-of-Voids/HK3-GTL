import hashlib
import json
import shutil
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from publish_industrial_datagen_r269_20261113 import replace_element


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/melon-adventure-r283-20261114'
DELIVERY = ROOT / 'deliveries/西瓜ARG_完整籽海_玩家体验_R283_20261114'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    now = datetime.now(ZoneInfo('Asia/Hong_Kong'))
    stamp = now.isoformat()
    backup = OUT / ('audit-before-' + now.strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    for name in ('index.html', 'current-summary.json'):
        shutil.copy2(AUDIT / name, backup / name)
    artifact = DELIVERY / 'hk3gtl-0.5.0-melon-adventure-r283-candidate.jar'
    shutil.copy2(ROOT / 'build/libs/hk3gtl-0.5.0.jar', artifact)
    candidate = dict(path=artifact.relative_to(ROOT).as_posix(),
                     sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                     bytes=artifact.stat().st_size, installed=False)
    world = json.loads((DELIVERY / 'map-preparation.json').read_text('utf8'))
    build = json.loads((OUT / 'build-result.json').read_text('utf8'))
    receipt = dict(
        revision='R283', updated_at=stamp,
        status='西瓜维度完整游玩主线已接入仓库候选并构建，独立地图与补给已备；未安装，待负责人亲自解谜。',
        artifact=candidate, build=build, world=world,
        implementation=[
            '手机五题只解开外封，航行档案另行显示抵达、实地残页及终点状态。',
            '来信门桩放置真实Stargate Journey星门，手机手动拨号；地址由该存档原生网络生成。',
            '独立维度hk3gtl:melon_reality使用噪声地形、瓜皮岩与籽纹砂，不复用虚数或审判维度。',
            '入口庭、三处实地残页、瓜心穹顶及实际地表连接；地标按维度SavedData只布置一次。',
            '个人五题资格、抵达、线索、终点与实际来门分别持久保存；原生通行事件校验五题资格。',
            '集齐实地残页后在终点触发个人收件箱来信和一次性纪念书，不在手机解封时提前通关。',
            '服务端GameProfile名xiguamao取得专属原信，其他玩家取得同行者抄本；不重发旧礼包、不授研究或毕业。',
            '原生星门反向拨号返程，返程石不耗手机电量，并使用本人真实入境门及其朝向。',
            '专用星门使用原生能量容量、权限和地址注册，关闭本连接开启浪涌，不修改全局双向通行配置。'],
        player_acceptance=dict(owner='负责人本人', status='尚未执行',
                               assistant_game_run=False, assistant_solved=False,
                               existing_instance_or_save_modified=False),
        scope='本次已接入手机至独立西瓜维度、实地谜题、终点来信与往返主线；旧跨模组七段草案继续保留，未冻结、未实装。',
        scoring='固定37域、原能力分母及全部研发与历史验收分值保持；构建和独立地图准备不计作玩家验收。')
    receipt_path = OUT / 'completion.json'
    write_json(receipt_path, receipt)
    write_json(DELIVERY / 'candidate.json', receipt)
    summary = json.loads((backup / 'current-summary.json').read_text('utf8'))
    page = (backup / 'index.html').read_text('utf8')
    summary['previous_repository_candidate'] = summary['repository_candidate']
    summary['repository_candidate'] = candidate
    summary['melon_adventure_r283_completion'] = receipt
    summary['current_work'] = dict(
        system='西瓜来信：完整维度游玩主线与独立玩家地图', state=receipt['status'],
        scope='仅仓库源码、资源、构建及独立存档准备；未操作桌面、游戏、活动实例或现有活动存档，未安装JAR。',
        remaining=['负责人本人从零解密、星门往返和终点触发尚未执行。', receipt['scope'],
                   '全库其余研发缺项保留既有分数与依据。'],
        evidence=receipt_path.relative_to(ROOT).as_posix())
    for system in summary['systems']:
        if system['id'] in ('N09', 'N14'):
            system['melon_adventure_r283_review'] = dict(updated_at=stamp,
                implemented='手机五题、原生星门、独立维度、实地残页、终点来信与返程候选已接入并构建；独立地图及用品已备。',
                remaining='负责人亲自解密及游戏验收尚未执行；旧跨模组七段草案仍未实装。',
                evidence=receipt_path.relative_to(ROOT).as_posix(), score_changed=False)
            system['updated_at'] = stamp
    summary['updated_at'] = summary['report_updated_at'] = stamp
    dev = summary['development_metric']['overall_percent']
    acceptance = summary['overall_percent']
    notice = (f'<section id="offline-maximize-current"><h2>西瓜之海 · 完整游玩主线候选 R283</h2>'
        f'<section class="metrics"><div>研发完成度 · 37域等权<b>{dev:.2f}%</b></div>'
        f'<div>本轮计分增量<b>0.00个百分点</b></div>'
        f'<div>研发满分系统<b>{summary["development_metric"]["completed_domains"]} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{acceptance:.2f}%</b></div></section>'
        f'<p>{escape(receipt["status"])}</p>'
        '<p>五题解开外封 → 原生星门 → 独立籽海 → 三处实地残页 → 瓜心来信与纪念书 → 原生拨号或返程石。'
        '每位玩家独立保存进度，收件人身份读取服务端GameProfile，不由答案伪装。</p>'
        f'<p>{escape(receipt["scope"])}</p>'
        '<p>负责人本人从首张残页亲自游玩；助手未代解密、未运行游戏、未安装，未改活动实例及现有活动存档。'
        '构建与地图准备不替代实际触发验收。</p>'
        '<p><a href="../melon-adventure-r283-20261114/completion.json">候选与地图回执（无谜底）</a> · '
        f'<a href="../{backup.relative_to(ROOT / "logs").as_posix()}/index.html">修改前历史</a> · {stamp}</p></section>')
    page = replace_element(page, 'section', 'offline-maximize-current', notice)
    for system_id in ('N09', 'N14'):
        start = page.index(f'id="system-{system_id}"')
        end = page.index('</summary>', start) + len('</summary>')
        page = page[:end] + ('<section class="notice"><h3>2026-11-14 · 西瓜维度游玩主线候选 R283</h3>'
            '<p>五题解封后经真实星门进入独立维度，实地集页后展开终点来信，原生拨号与无电返程石已接。'
            '构建成功、地图已备，未安装，待负责人本人游玩；旧跨模组七段仍保留为候选，本轮分数不变。</p>'
            '<a href="../melon-adventure-r283-20261114/completion.json">R283交付回执</a></section>') + page[end:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace('<', '\\u003c')
    page = replace_element(page, 'script', 'audit-data', '<script type="application/json" id="audit-data">' + payload + '</script>')
    write_json(AUDIT / 'current-summary.json', summary)
    (AUDIT / 'index.html').write_text(page, encoding='utf8')
    write_json(OUT / 'audit-publication.json', dict(updated_at=stamp,
        backup=backup.relative_to(ROOT).as_posix(), development_percent=dev,
        acceptance_percent=acceptance, domain_count=summary['domain_count'], score_changed=False))
    print(json.dumps(dict(artifact=candidate, map=world['archive'], development_percent=dev,
                         acceptance_percent=acceptance), ensure_ascii=False))


if __name__ == '__main__':
    main()
