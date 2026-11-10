# -*- coding: utf-8 -*-
"""收束已批准21形态接入，更新既有HTML审计，不重新生成建筑或物品资源。
【变更记录 #1】2026-10-20 00:47:37（修订172）
删除：当前审计中21形态仍待批的失效描述，更新前原字节另存。
新增：批准、63正式资源、构建及停机部署证据链接和机壳原6项末项重评。
修改：只改机壳域及页首当前状态，其余33域正文与评分保持。
用途：区分已批准接入、游戏验收及仍待批的39燃料贴图，不能平均成全模组完成率。
【变更记录 #2】2026-10-20T01:04:05+08:00（修订172收束校正）
删除：只匹配id为首属性的文章选择条件；新增：33篇其他正文不变断言、真实部署索引状态和中断接续保护。
修改：允许原有data-full属性出现在id之前，失败后复用原快照而不重复追加索引记录；用途：准确更新现有HTML，不影响游戏JAR。
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from structure_delivery.project_paths import project_path
import hashlib
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/voltage-architecture-r172'
AUDIT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html'
REPORT = LOG / '21形态批准接入与验证.html'
OLD_REVIEW = ROOT / 'logs/energy-production-r172/部件与机壳逐能力复核.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def link(origin, target, label):
    rel = os.path.relpath(target, origin.parent).replace('\\', '/')
    return f'<a href="{html.escape(rel, quote=True)}">{html.escape(label)}</a>'


def report(stamp, install, package, deploy):
    """按实际收据生成HTML，不把文件部署描述为游戏成型或实际发电。"""
    rows = ''.join(f'<tr><td>{html.escape(s["key"].upper())}</td><td>{html.escape(s["voltage"])}</td><td>{" × ".join(map(str,s["size_xyz"]))}</td><td>{s["blocks"]:,}</td></tr>' for s in install['structures'])
    inheritance = ''.join(f'<li>{html.escape(s["from"])} → {html.escape(s["to"])}：保留前阶{s["preserved"]:,}个非主控方块，逐格一致。</li>' for s in install['inheritance_checks'])
    refs = ' · '.join(link(REPORT, LOG / name, label) for name,label in (
        ('formal-installation.json','正式接入收据'), ('formal-installation-postcheck.json','接入后逐格复核'),
        ('package-verification.json','最终包核验'), ('deployment.json','备份与部署'),
        ('build-final.log','完整构建日志'), ('机壳能力更新.json','机壳原6项复核')))
    proof = link(REPORT, project_path(install['approval_manifest']), '新确认清单')+' · '+link(REPORT, project_path(install['archive_zip']), '新确认归档ZIP')
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>21形态批准接入与验证</title><style>body{{max-width:1100px;margin:30px auto;padding:0 24px;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;background:#eff5f4;color:#193f49}}header{{background:#173f48;color:white;padding:26px;border-radius:12px}}section{{margin:20px 0;padding:20px;background:white;border:1px solid #ccdddd;border-radius:10px}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid #c9dbdd;padding:8px;text-align:left}}th{{background:#e4f1f1}}a{{color:#08717d}}code{{overflow-wrap:anywhere}}.note{{background:#fff1e4}}</style></head><body><header><h1>21形态新配色：批准、正式接入与部署</h1><p>{stamp} · Asia/Hong_Kong · 修订172</p></header>
<section><h2>实际完成</h2><p>负责人明确答复“采用整批21形态新配色”。原消息精确发送时间未知；批准接入收据实际时间为{install['time']}。本批已建立新的独立确认归档，替换21份Pattern逐格布局、21份游戏放置NBT和21份元数据，并完成完整clean check build、最终包身份核验及增强版2.9停机部署。</p><p>{proof}</p><p>原候选、旧批准档案均保持字节不变，核对旧归档文件{install['old_archive_files_checked']:,}份。新ZIP SHA-256：<code>{install['archive_zip_sha256']}</code>。</p></section>
<section><h2>已部署包</h2><p>目标：<code>{html.escape(deploy['target'])}</code>；文件{deploy['bytes']:,}字节。SHA-256：<code>{deploy['sha256']}</code>。</p><p>替换前保存原包至<code>{html.escape(deploy['backup'])}</code>；其他模组JAR保持不变。游戏未启动，本修订的成型、实际运行及单人/多人自然流程尚未验收。</p><p>{refs}</p></section>
<section><h2>21形态与主色电压</h2><p>下表尺寸顺序为X×Y×Z，即宽×高×深。对应电压机壳承担主识别色；MAX采用现有GTCEu MAX机械机壳。未新增机壳或方块。</p><table><thead><tr><th>形态</th><th>主色电压</th><th>导出尺寸</th><th>实体方块</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>原地扩建</h2><ul>{inheritance}</ul><p>正式控制器及真实仓室沿用原合同；NBT与Pattern中只有指定主控/接口转换允许不同于建筑审批标记。I14/I15等待新批次、I16候选的状态保持。</p></section>
<section class="note"><h2>未冒充完成的内容</h2><p>本次是建筑主色映射接入，控制器旧名义MAX注册和玩家电网档位仍未逐台重构；没有改变配方EU/t或实际功率限制。机壳原6项实现现为6/6，此分数仅覆盖原审计定义，不是84台机器全部完成或全模组发布率。</p><p>39项燃料贴图仍待单独审批，未写入正式资源。15种燃料与60工况仍为设计候选，能源系统能力维持2/16。反应堆结构、真实发电、热量与废物生命周期仍待完成；最终整包8GB以下、12视距和可开光影的验收按负责人决定最后执行。</p><p>本页做本地链接、内容及收据检查，不宣称浏览器3D交互或游戏视觉验收通过。</p></section><footer>【记录 #1】{stamp}：新增本批真实批准、归档、构建、部署和未验收边界；保留历史证据，不改待审批资产。</footer></body></html>'''
    REPORT.write_text(body, encoding='utf-8')


def main():
    stamp = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    install = read(LOG / 'formal-installation.json')
    package = read(LOG / 'package-verification.json')
    deploy = read(LOG / 'deployment.json')
    assert package['status'] == 'passed' and package['revision'] == 172
    assert deploy['revision'] == 172 and deploy['sha256'] == package['sha256']
    assert deploy['third_party_jars_unchanged'] is True
    assert install['shape_count'] == 21 and install['formal_files_written'] == 63
    assert install['approval_quote'] == '采用整批21形态新配色'
    assert len(install['inheritance_checks']) == 7 and all(x['passed'] for x in install['inheritance_checks'])
    index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
    old_index_bytes = index_path.read_bytes()
    index = read(index_path)
    pending_before = json.dumps(index['pending_batch'], sort_keys=True, ensure_ascii=False)
    excluded_before = {x['key']: json.dumps(x, sort_keys=True, ensure_ascii=False) for x in index['entries'] if x['key'] in ('i14','i15')}
    keys = {x['key'] for x in install['structures']}
    assert len(keys) == 21
    index_changed = False
    for entry in index['entries']:
        if entry['key'] in keys:
            assert entry['formal_resource_present'] is True
            if entry['game_files_installed']:
                assert entry['deployed_revision'] == 172 and entry['deployed_jar_sha256'] == deploy['sha256']
                continue
            index_changed = True
            entry.update(status='approved_formal_deployed_game_unverified', game_files_installed=True,
                         game_verified=False, deployed_revision=172, deployed_jar_sha256=deploy['sha256'],
                         deployment_receipt=str((LOG/'deployment.json').relative_to(ROOT)).replace('\\','/'))
    if index_changed:
        index['updated_at'] = stamp
        records = index.setdefault('_change_records', [])
        records.append({'record':len(records)+1,'time':stamp,'reason':'21形态修订172已实际停机部署',
                        'changes':'删除失效的未部署当前状态；新增真实部署身份和未游戏验收边界；旧确认归档、I14/I15及待满批对象不变。'})
    assert json.dumps(index['pending_batch'], sort_keys=True, ensure_ascii=False) == pending_before
    assert {x['key']:json.dumps(x,sort_keys=True,ensure_ascii=False) for x in index['entries'] if x['key'] in ('i14','i15')} == excluded_before
    if index_changed:
        (LOG/'归档索引部署前快照.json').write_bytes(old_index_bytes)
        index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report(stamp, install, package, deploy)
    # 同名收束不可覆盖旧页；后续重审应先核对现有记录和最新证据。
    snapshot = LOG / '主审计接入前快照.html'
    if snapshot.exists():
        assert snapshot.read_bytes() == AUDIT.read_bytes(), '已有快照与当前页不同，须检查后再接续'
    else:
        snapshot.write_bytes(AUDIT.read_bytes())
    source = AUDIT.read_text(encoding='utf-8')
    pattern = r'<article\b[^>]*\bid="([^"]+)"[^>]*>.*?</article>'
    originals = {m[1]: m[0] for m in re.finditer(pattern, source, re.S)}
    assert len(originals) == 34
    review = read(OLD_REVIEW)
    casing = next(s for s in review['systems'] if s['id'] == 'casings')
    casing.update(numerator=6, denominator=6, percent=100, full=6, partial=0, missing=0)
    feature = casing['features'][-1]
    feature.update(score=1,
        finding='负责人明确采用整批21形态新配色，现已新建不可变确认归档，并替换21份Pattern布局、21份放置NBT和21份元数据；7组原地扩建继承及包内逐文件身份均已核验。',
        remaining='此项完成仅覆盖已有正式21形态；不代表84台机器全部建成，也不代表游戏成型、完整生存或多人已验收。',
        evidence=['logs/voltage-architecture-r172/formal-installation.json',
                  'logs/voltage-architecture-r172/package-verification.json',
                  'logs/voltage-architecture-r172/deployment.json'])
    evidence = {'updated_at': stamp, 'scope': '保留原6项分母，仅将已批准21形态正式替换末项0.5改为1',
                'previous_review': str(OLD_REVIEW.relative_to(ROOT)), 'previous_sha256': sha(OLD_REVIEW),
                'system': casing, 'game_verified': False,
                '_record': f'【记录 #1】{stamp}：批准与工程接入已经完成，未把游戏验收计为完成。'}
    (LOG / '机壳能力更新.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    items = []
    for f in casing['features']:
        refs = ' · '.join(link(AUDIT, ROOT / p.split(':')[0], project_path(p.split(':')[0]).name) for p in f['evidence'])
        items.append(f'<li><span class="state">实现 · 1</span> <strong>{html.escape(f["name"])}</strong><p>{html.escape(f["finding"])}</p><p>边界：{html.escape(f["remaining"] or "本项实现已完成，完整自然流程与多人验收分别记录。")}</p><p class="evidence">{refs}</p></li>')
    article = f'<article id="casings" data-system="casings" data-full="true"><h3>机壳配方与建筑主配色 · 6/6（100.00%）</h3><p class="good">{stamp}：16种八板机壳与MAX自举保留，21形态新配色已明确批准并完成正式接入和2.9停机部署。</p><p class="small">此分数是原6项代码/资源能力，不是全模组发布率。{link(AUDIT, LOG/"机壳能力更新.json", "逐能力证据")} · {link(AUDIT, REPORT, "批准接入与验证")}</p><details><summary>展开原6项及验收边界</summary><ol>{"".join(items)}</ol></details></article>'
    source, count = re.subn(r'<article id="casings".*?</article>', lambda _: article, source, count=1, flags=re.S)
    assert count == 1
    row = '<tr data-system="casings"><td><a href="#casings"><strong>机壳配方与建筑主配色</strong></a></td><td><span class="pct">100.00%</span><div class="bar"><i style="width:100%"></i></div></td><td>6 / 6<br><span class="small">完整6 · 部分0 · 缺失0</span></td><td>原6项实现已闭合</td><td>21正式形态已停机部署<br><span class="small">游戏成型、生存与多人仍待验收</span></td></tr>'
    source, count = re.subn(r'<tr data-system="casings".*?</tr>', lambda _: row, source, count=1, flags=re.S)
    assert count == 1
    def sorted_rows(match):
        rows = re.findall(r'<tr.*?</tr>', match[1], re.S)
        assert len(rows) == 34
        rows.sort(key=lambda r: float(re.search(r'class="pct[^\"]*">([\d.]+)%', r)[1]))
        return '<tbody>'+''.join(rows)+'</tbody>'
    source = re.sub(r'<tbody>(.*?)</tbody>', sorted_rows, source, count=1, flags=re.S)
    source = re.sub(r'(<header><h1>.*?</h1>)<p>.*?</p>', lambda m: m[1]+f'<p>本轮更新 {stamp} · 增强版2.9已部署修订172；21正式结构新配色接入，机壳原6项完成。其余33域分值保留前次快照。</p>', source, count=1, flags=re.S)
    source = re.sub(r'<div class="metric"><strong>修订171</strong><span>.*?</span></div>', '<div class="metric"><strong>修订172</strong><span>21形态新配色已批准、归档、完整clean check build并部署；游戏验收待完成</span></div>', source, count=1, flags=re.S)
    current = f'21形态新配色已获明确批准，63份正式资源已更新并部署至增强版2.9；机壳能力6/6。{link(AUDIT,REPORT,"本批归档、构建与部署证据")}。39项燃料贴图仍待批准；能源仍2/16，60份燃料工况仍为设计候选。'
    source = re.sub(r'<div class="alert">.*?</div>', lambda _: '<div class="alert"><strong>当前进展：</strong>'+current+'其他33域未重评分；整包内存优化仍最后执行。</div>', source, count=1, flags=re.S)
    first = f'<h2 id="first-system">本轮完成：21形态电压主色正式接入</h2><div class="box"><p>{current}</p><p>I01四阶段HBV→QSV→QCV→IWV；研究所MAX→HDV→QEV→IRV→CIV。前阶建筑继续保留，旧批准归档字节不变；I14/I15待批次、I16候选的状态保持。</p><p>下一开发系统仍为能源生产：需要真实燃料定量平衡、控制器与已批准Pattern、实际发电/余热/废物生命周期。当前包未新增这些能力，未启动本修订的单人或多人验收。</p></div>'
    source = re.sub(r'<h2 id="first-system">.*?</h2><div class="box">.*?</div>', lambda _:first, source, count=1, flags=re.S)
    source = source.replace('</footer>', '</footer>'+f'<p class="muted" id="revision172-approved-palette">【追加记录 #10】{stamp}：用户采用整批21形态新配色；只将机壳原末项0.5改为1，其余33域正文与分值不变。{link(AUDIT,snapshot,"本次更新前快照")}。本页历史段落保留各自原时刻状态，以页首本轮状态为准。</p>', 1)
    afters = {m[1]:m[0] for m in re.finditer(pattern, source, re.S)}
    unchanged = [key for key in originals if key != 'casings' and afters.get(key) == originals[key]]
    assert len(unchanged) == 33 and len(afters) == 34
    AUDIT.write_text(source, encoding='utf-8')
    (LOG / '主审计更新.json').write_text(json.dumps({'updated_at':stamp, 'score':'6/6', 'unchanged_articles':unchanged, 'sha256':sha(AUDIT)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'updated_at':stamp, 'casings':'6/6', 'other_articles_unchanged':33}, ensure_ascii=False))


if __name__ == '__main__':
    main()
