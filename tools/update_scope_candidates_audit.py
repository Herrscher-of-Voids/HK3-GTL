# -*- coding: utf-8 -*-
"""将本批已核事实与候选入口写回既有HTML主审计，保持原能力分母。
【变更记录 #1】2026-10-19 13:53:53（香港时间，候选文档批次172）
删除：当前页已失效的32部件缺制造/机壳钢配方结论，完整旧页另存历史快照。
新增：两域逐能力复核、新燃料授权、工艺/贴图/21形态候选及身份说明链接。
修改：只重评部件与机壳的既有6项；能源候选不涨分；用途为区分实现、审批与游戏验收。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT/'logs/energy-production-r172'
AUDIT = ROOT/'doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html'
FUEL = LOG/'燃料工艺与60工况候选_r172.html'
TEXTURES = ROOT/'deliveries/能源燃料工艺_39项贴图候选_R172_20261019/39项燃料贴图对照.html'
SHAPES = ROOT/'deliveries/21形态_电压主色修订候选_R172_20261019/index.html'


def link(path, label, prefix='../../../'):
    return f'<a href="{prefix}{html.escape(str(path.relative_to(ROOT)).replace(chr(92),chr(47)))}">{html.escape(label)}</a>'


def evidence(paths):
    values = []
    for raw in paths:
        relative = re.sub(r':\d+$', '', raw)
        target = ROOT/relative
        assert target.exists(), relative
        values.append(link(target, Path(relative).name))
    return ' · '.join(values)


def main():
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    review = json.loads((LOG/'部件与机壳逐能力复核.json').read_text(encoding='utf-8'))
    for path in [FUEL,TEXTURES,SHAPES]:
        assert path.is_file(), path
    source = AUDIT.read_text(encoding='utf-8')
    snapshot = LOG/'主审计更新前快照_r171.html'
    if not snapshot.exists():
        shutil.copy2(AUDIT,snapshot)
    article_pattern = r'<article\b(?=[^>]*\bid="([^"]+)")[^>]*>.*?</article>'
    original_articles = {m[1]:m[0] for m in re.finditer(article_pattern,source,re.S)}
    changed = []
    for system in review['systems']:
        key = system['id']
        assert len(system['features']) == system['denominator'] == 6
        assert sum(v['score'] for v in system['features']) == system['numerator']
        score, percent = system['numerator'],system['percent']
        items = []
        for feature in system['features']:
            amount=feature['score']
            state='实现' if amount==1 else ('部分' if amount else '缺失')
            items.append(f'<li><span class="state">{state} · {amount:g}</span> <strong>{html.escape(feature["name"])}</strong><p>{html.escape(feature["finding"])}</p><p>剩余：{html.escape(feature["remaining"] or "本项代码能力已实现；完整自然流程与多人验收分别记录。")}</p><p class="evidence">{evidence(feature["evidence"])}</p></li>')
        note = ('本轮重新核对128条现行制造，旧“WFV–CEV32件无制造”及重复Soulium配方描述已失效。上游魂钢研究阻断、六项CEV部件零消费和全阶复杂度递增仍未闭合。'
                if key=='components' else '16机壳当前均为8张对应主材板外圈、中心空、产1；HBV的MAX自举五工序无研究门槛。21形态改色仍是候选，尚未替换正式建筑。')
        current = f'<article id="{key}" data-system="{key}"><h3>{html.escape(system["name"])} · {score:g}/6（{percent:.2f}%）</h3><p class="good">{now} 原6项逐能力复核。{note}</p><p class="small">此分数反映该域代码能力，不是整个模组或自然生存完成率；缺实机不扣已有实现分。{link(LOG/"部件与机壳逐能力复核.json","本批逐项证据")} · {link(snapshot,"原失效描述历史快照")}</p><details><summary>展开能力明细、剩余差距和现行依据</summary><ol>{"".join(items)}</ol></details></article>'
        source, count = re.subn(r'<article id="'+key+r'".*?</article>',lambda _:current,source,count=1,flags=re.S)
        assert count == 1
        remainder = '2项能力仍部分，复杂度与真实用途未闭合' if key=='components' else '主体改色待审批，正式替换与游戏验收待完成'
        row = f'<tr data-system="{key}"><td><a href="#{key}"><strong>{html.escape(system["name"])}</strong></a></td><td><span class="pct">{percent:.2f}%</span><div class="bar"><i style="width:{percent}%"></i></div></td><td>{score:g} / 6<br><span class="small">完整{system["full"]} · 部分{system["partial"]} · 缺失{system["missing"]}</span></td><td>{remainder}</td><td>本批按现行128制造／16机壳重评<br><span class="small">单人自然流程和多人待验</span></td></tr>'
        source, count = re.subn(r'<tr data-system="'+key+r'".*?</tr>',lambda _:row,source,count=1,flags=re.S)
        assert count == 1
        changed.append(key)
    def sort_rows(match):
        rows = re.findall(r'<tr.*?</tr>',match[1],re.S)
        rows.sort(key=lambda row:float(re.search(r'class="pct[^\"]*">([\d.]+)%',row)[1]))
        assert len(rows)==34
        return '<tbody>'+''.join(rows)+'</tbody>'
    source=re.sub(r'<tbody>(.*?)</tbody>',sort_rows,source,count=1,flags=re.S)
    scope = ('用户已明确选择“扩展真实燃料工艺，仍要求每台15条独立配方；新贴图另行审批”。'
             '此前只保留两类燃料的上限已覆盖，不能再将范围决定列为未决。'
             '15种燃料、60份工况与39项贴图目前是可审阅候选，新增可执行配方仍为0；能源维持2/16。'
             '真实控制器、结构审批、数值平衡、热/废物生命周期和实际发电IO仍缺。')
    energy_note=f'<p class="good" id="energy-current-r172">{now}：{scope} {link(FUEL,"燃料工艺与60工况")} · {link(TEXTURES,"39项贴图对照")}。</p>'
    source = re.sub(r'<p class="good" id="energy-current-r17[12]">.*?</p>','',source,flags=re.S)
    source=source.replace('<article id="energy_production" data-system="energy_production">','<article id="energy_production" data-system="energy_production">'+energy_note,1)
    # 其余正文保留历史证据，页首与本轮开发区显示当前口径。
    source=re.sub(r'(<header><h1>.*?</h1>)<p>.*?</p>',lambda m:m[1]+f'<p>本轮更新 {now} · 增强版2.9正式游戏包仍为修订171 · 候选批次172；部件与机壳按现行代码重评，其余32域分数保留前次快照。</p>',source,count=1,flags=re.S)
    alert = f'<div class="alert"><strong>当前进展：</strong>部件现行128制造已核，能力5/6；机壳16种八板配方及MAX自举已核，能力5.5/6。能源范围已获确认，15种燃料／60工况和39贴图候选可审；能源仍2/16。21形态已按电压生成改色候选，未正式替换。{link(FUEL,"能源工艺")} · {link(TEXTURES,"贴图审阅")} · {link(SHAPES,"21形态主色审阅")}。未把候选数量计入实现分。</div>'
    source=re.sub(r'<div class="alert">.*?</div>',lambda _:alert,source,count=1,flags=re.S)
    first=f'<h2 id="first-system">本轮整批：能源工艺、21形态改色与现行能力复核</h2><div class="box"><p>{scope}</p><p>21形态改色遵循工业线电压和原地扩建继承；正式资源、批准归档和实例未被改写。{link(SHAPES,"整批结构预览")} · {link(TEXTURES,"39项完整原图与候选")} · {link(FUEL,"15种燃料与60合同")}。</p><p>部件原2.5/6更正为5/6，机壳原2.5/6更正为5.5/6，依据是此前已实现但旧页没有更新的代码和实际导出，不是本轮新增这些制造。{link(LOG/"部件与机壳逐能力复核.json","逐能力复核")}。其他32域分数未重算，不能平均为全模组完成率。</p></div>'
    source=re.sub(r'<h2 id="first-system">.*?</h2><div class="box">.*?</div>',lambda _:first,source,count=1,flags=re.S)
    source=re.sub(r'<p class="muted" id="revision172-candidates">.*?</p>','',source,flags=re.S)
    source=source.replace('</footer>','</footer>'+f'<p class="muted" id="revision172-candidates">【追加记录 #8】{now}：删除当前失效结论但保留{link(snapshot,"旧页快照")}；新增能源已批范围与候选入口；仅部件/机壳原分母重评。游戏包仍171，未构建部署。导出166为旧硬编码，{link(ROOT/"logs/machine-overview-r171/运行导出修订身份补充核对.json","部署与运行身份另有补充证据")}，原manifest保持不变。</p>',1)
    after = {m[1]:m[0] for m in re.finditer(article_pattern,source,re.S)}
    unchanged=[key for key,value in original_articles.items() if key not in {'components','casings','energy_production'} and after.get(key)==value]
    assert len(original_articles)==len(after)==34
    assert len(unchanged)==31, (len(unchanged),set(original_articles)-set(unchanged))
    AUDIT.write_text(source,encoding='utf-8')
    summary={'updated_at':now,'game_revision_unchanged':171,'candidate_batch':172,
             'systems':review['systems'],'energy_score_unchanged':'2/16',
             'other_31_articles_byte_identical':unchanged,'source_snapshot':str(snapshot),
             'main_html_sha256':hashlib.sha256(AUDIT.read_bytes()).hexdigest(),
             '_record':f'【记录 #1】{now}：仅重评两域原6项；能源范围与候选记账，不计算全模组比例。'}
    (LOG/'主审计本批更新.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'updated_at':now,'components':'5/6','casings':'5.5/6','energy':'2/16','other_articles_unchanged':31},ensure_ascii=False))


if __name__=='__main__':
    main()
