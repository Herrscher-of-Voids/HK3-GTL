# -*- coding: utf-8 -*-
"""读取已交付结构，制作控制器与接口融合审查证据；不改写任何源结构。

【变更记录 #1】2026-10-23 10:32:00（专项审查工具，不增加模组修订）
- 删除：无。新增：21形态来源身份、北立面材质投影、标记及审查页面。
- 修改：仅在独立日志目录生成证据，不修改蓝图、NBT、正式资源或游戏实例。
- 用途：以实际方块及已嵌入纹理核对外挂面板和支柱；图像不是游戏截图。
输入：当前有效交付的blueprint.json/data.js与三份人工审查结果；输出：logs下专项证据。
【变更记录 #2】2026-10-23 10:40:00（专项审查合并与复核）
- 删除：无。新增：三组人工结论合并、21份NBT逐格比较和图文审查页。
- 修改：明确预览标记与真实机器能力的边界，清理建议串接的重复标点。
- 用途：交付可复查的逐台发现；不将结构外观问题审查当作修订已完成。
【变更记录 #3】2026-10-23 10:42:31（讨论记录与索引收口）
- 删除：无。新增：讨论记录与规则修改后身份落盘。
- 修改：旁栏索引从最终合并结果更新；用途为保持讨论、页面和索引一致。
"""
from pathlib import Path
import base64
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont
import nbtlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/controller-integration-review-20261023'
RULES = ['rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt']
FONT = 'C:/Windows/Fonts/msyh.ttc'


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def sources():
    base = ROOT / 'deliveries/多方块确认归档/20261020_005209_151059_21形态_电压主色修订_已确认/confirmed_voltage_r172'
    entries = [(f'i01-{n}', base / f'i01-{n}', 'R172批准配色') for n in range(1, 5)]
    entries += [(f'i{n:02}', base / f'i{n:02}', 'R172批准配色') for n in range(2, 14)]
    prefixes = [
        ('i14', 'I14_魂钢聚合压铸机_正梁锻心重设计_V4_20261015', 'V4历史批准'),
        ('i15', 'I15_魂钢重构退火炉_三钟回转炉院_V3_20261016', 'V3历史批准'),
        ('i16', 'I16_魂钢精密加工中心_双门架定轴校准_V3_HDV_20261021', 'V3 HDV批准'),
        ('i17', 'I17_浓缩崩坏能燃料精制厂_阶梯精馏园区_V1_QSV_20261021', 'V1 QSV批准'),
        ('i18', 'I18_崩坏能燃料棒封装阵列_蓝脊热室与并列封装线_V1_HBV_20261022', 'V1 HBV待审'),
    ]
    return entries + [(key, ROOT / 'deliveries' / directory, status) for key, directory, status in prefixes]


def front_image(data, materials):
    """北立面按由远到近绘制纹理，保留真实x/y比例并标出全部接口和主控。"""
    w, h, depth = data['size']
    scale, margin, top = 14, 35, 65
    image = Image.new('RGB', (w * scale + margin * 2, h * scale + top + 40), '#131a28')
    draw = ImageDraw.Draw(image)
    draw.text((margin, 10), data['key'].upper() + ' 北立面 · 材质投影',
              font=ImageFont.truetype(FONT, 18), fill='#edf2ff')
    textures = {}
    for material in materials:
        url = material['faces']['north']
        textures[material['state']] = Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA').resize((scale, scale), Image.Resampling.NEAREST)
    for b in sorted(data['blocks'], key=lambda b: -b['pos'][2]):
        x, y, z = b['pos']
        texture = textures[b['state']]
        image.paste(texture, (margin + x * scale, top + (h - 1 - y) * scale), texture)
    draw = ImageDraw.Draw(image)
    marks = [(p['pos'], False) for p in data['ports']] + [(data['controller'], True)]
    for (x, y, z), control in marks:
        x0, y0 = margin + x * scale, top + (h - 1 - y) * scale
        color = '#ffdf61' if control else '#f19b64'
        draw.rectangle((x0 - 2, y0 - 2, x0 + scale + 2, y0 + scale + 2), outline=color, width=2)
        if control:
            draw.line((x0 + scale // 2, y0, x0 + scale // 2, y0 - 26), fill=color, width=2)
            draw.text((max(margin, x0 - 60), y0 - 49), '主控 ' + str([x, y, z]), font=ImageFont.truetype(FONT, 15), fill=color, stroke_width=1, stroke_fill='#131a28')
    draw.text((margin, image.height - 30), '黄框：主控位置　橙框：接口位置　北为 −Z', font=ImageFont.truetype(FONT, 15), fill='#bac9de')
    return image


def evidence():
    OUT.mkdir(parents=True, exist_ok=True)
    checkpoint = OUT / 'rules-read.json'
    if not checkpoint.exists():
        save(checkpoint, {'recorded_at': now(), 'note': '主任务已完整读取六份当前规则；本记录为读后身份汇总，不伪造各次读取的精确时间。',
            'files': [{'path': 'rule/' + name, 'sha256': sha(ROOT / 'rule' / name), 'lines': len((ROOT / 'rule' / name).read_text(encoding='utf-8').splitlines())} for name in RULES]})
    items = []
    for key, source, status in sources():
        data = json.loads((source / 'blueprint.json').read_text(encoding='utf-8'))
        packed = re.search(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', (source / 'data.js').read_text(encoding='utf-8'))
        payload = json.loads(gzip.decompress(base64.b64decode(packed[1])))
        assert payload['data']['controller'] == data['controller']
        assert payload['data']['size'] == data['size']
        occupied = {tuple(b['pos']): b['state'] for b in data['blocks']}
        assert tuple(data['controller']) in occupied
        assert all(occupied[tuple(p['pos'])] == 'hk3gtl:industrial_port_casing' for p in data['ports'])
        picture = front_image(data, payload['materials'])
        picture.save(OUT / (key + '-north.png'))
        nbt_paths = list(source.glob('*.nbt'))
        assert len(nbt_paths) == 1
        items.append({'key': key, 'title': data['title'], 'status': status, 'source': source.relative_to(ROOT).as_posix(),
            'controller': data['controller'], 'ports': data['ports'], 'size': data['size'], 'image': key + '-north.png',
            'sha256': {'blueprint': sha(source / 'blueprint.json'), 'nbt': sha(nbt_paths[0])}, 'nbt': nbt_paths[0].name})
    save(OUT / 'sources.json', {'recorded_at': now(), 'scope': 'I01四阶和I02–I18，共21形态', 'items': items})
    sheet = Image.new('RGB', (1320, 7 * 330 + 75), '#131a28')
    draw = ImageDraw.Draw(sheet)
    draw.text((25, 18), 'I01–I18 控制器与接口 · 21形态北立面', font=ImageFont.truetype(FONT, 25), fill='#edf2ff')
    for i, item in enumerate(items):
        im = Image.open(OUT / item['image'])
        im.thumbnail((425, 312))
        x, y = (i % 3) * 440, 70 + (i // 3) * 330
        sheet.paste(im, (x + (440 - im.width) // 2, y))
    sheet.save(OUT / '21形态北立面对照.png')
    print('已生成21形态材质北立面及来源身份；没有修改结构。', flush=True)


def href(path):
    return html.escape(os.path.relpath(path, OUT).replace('\\', '/'), quote=True)


def report():
    """合并三个分工的人工结论，保留原始证据，逐格核验来源后生成可复查页面。"""
    metadata = json.loads((OUT / 'sources.json').read_text(encoding='utf-8'))
    a = json.loads((OUT / 'i01-i08.json').read_text(encoding='utf-8'))['findings']
    b = json.loads((OUT / 'i09-i15.json').read_text(encoding='utf-8'))['items']
    c = json.loads((OUT / 'i16-i18.json').read_text(encoding='utf-8'))['machines']
    findings = {}
    for entry in a:
        findings[entry['key'].lower()] = {'verdict': entry['classification'], 'finding': entry['visual_finding'], 'suggestion': entry['proposal_only'], 'raw': 'i01-i08.json'}
    for entry in b:
        findings[entry['id'].lower()] = {'verdict': entry['classification'], 'finding': entry['assessment'], 'suggestion': entry['suggestion'], 'raw': 'i09-i15.json'}
    for entry in c:
        findings[entry['id'].lower()] = {'verdict': entry['classification'], 'finding': entry['visual_judgement'], 'suggestion': '；'.join(s.rstrip('。；') for s in entry['recommendations']) + '。', 'raw': 'i16-i18.json'}
    assert len(findings) == 21
    items = []
    for item in metadata['items']:
        source = ROOT / item['source']
        assert sha(source / 'blueprint.json') == item['sha256']['blueprint']
        assert sha(source / item['nbt']) == item['sha256']['nbt']
        data = json.loads((source / 'blueprint.json').read_text(encoding='utf-8'))
        saved = nbtlib.load(source / item['nbt'])
        states = []
        for state in saved['palette']:
            props = sorted((str(k), str(v)) for k, v in state.get('Properties', {}).items())
            states.append(str(state['Name']) + ('[' + ','.join(k + '=' + v for k, v in props) + ']' if props else ''))
        expected = {tuple(block['pos']): block['state'] for block in data['blocks']}
        actual = {tuple(map(int, block['pos'])): states[int(block['state'])] for block in saved['blocks']}
        assert actual == expected, item['key']
        item.update(findings[item['key']])
        item['category'] = '明显问题' if item['key'] not in ['i15', 'i16'] else ('局部需改善' if item['key'] == 'i15' else '基本融入，主控细化')
        items.append(item)
    save(OUT / 'review.json', {'recorded_at': now(), 'scope': 'I01四阶及I02–I18', 'summary': {'forms': 21, 'machines': 18, 'obvious_forms': 19, 'obvious_machines': 16, 'partial': ['I15'], 'largely_integrated': ['I16']},
        'method': '21张有效版本等轴图人工审视、蓝图/NBT逐格一致性、北立面投影、生成器与实际三维坐标；连通不作为融合通过标准。',
        'limits': '建筑审查；所示主控/接口为交付预览标记位置，钻石、机壳及industrial_port_casing不等同可运行控制器或仓室；I14–I17未正式接入Pattern，I18待审。未做游戏内成型、仓室能力、生存或配方验收；新布局建议未生成也未批准。', 'items': items})
    esc = html.escape
    sections = []
    for item in items:
        source = ROOT / item['source']
        key = item['key']
        ports = '；'.join(p['id'] + ' ' + str(p['pos']) for p in item['ports'])
        sections.append(f'''<article id="{key}" data-category="{item['category']}">
<div class="row"><h2>{key.upper()} · {esc(item['title'])}</h2><span class="tag {'warn' if key not in ['i15', 'i16'] else 'mutedtag'}">{item['category']}</span></div>
<p class="meta">版本：{esc(item['status'])}　主控 XYZ：<code>{item['controller']}</code>　接口 {len(item['ports'])} 个</p>
<p class="finding">{esc(item['finding'])}</p>
<div class="images"><figure><a href="{href(source / '等轴预览.png')}"><img loading="lazy" src="{href(source / '等轴预览.png')}" alt="{key}有效版本等轴图"></a><figcaption>有效版本等轴图 · 点击放大，辨认前后关系</figcaption></figure>
<figure><a href="{item['image']}"><img loading="lazy" src="{item['image']}" alt="{key}北立面与标记"></a><figcaption>同源北立面投影 · 黄框主控 / 橙框接口</figcaption></figure></div>
<p><strong>改造方向（建议，尚未制作）：</strong>{esc(item['suggestion'])}</p>
<details><summary>查看接口坐标与来源证据</summary><p><code>{esc(ports)}</code></p>
<p><a href="{href(source / 'blueprint.json')}">来源蓝图</a> · <a href="{href(source / item['nbt'])}">来源NBT</a> · <a href="{href(source / '三维评审.html')}">原三维预览</a> · <a href="{item['raw']}">详细审查证据</a></p>
<p class="meta">NBT SHA256：{item['sha256']['nbt']}</p></details></article>''')
    nav = ''.join(f'<a href="#{item["key"]}">{item["key"].upper()}</a>' for item in items)
    document = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01–I18 控制器与接口融合审查</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#eef1f3;color:#23313a;font:16px/1.75 "Microsoft YaHei",sans-serif}}main{{max-width:1360px;margin:auto;padding:30px 24px}}header{{background:#1b303b;color:#f4f7fa;padding:26px 30px}}h1{{font-size:28px;line-height:1.4;margin:0 0 14px}}h2{{font-size:21px;margin:0}}a{{color:#176486}}header a{{color:#d6e7ed}}p{{margin:12px 0}}.lead{{font-size:18px}}.meta,figcaption{{font-size:13px;color:#61717e}}.meta code{{font-size:14px}}.metrics{{display:flex;flex-wrap:wrap;gap:24px;padding:22px 0;border-bottom:1px solid #c9d1d6}}.metrics b{{font-size:24px}}.note{{background:#fff5e6;padding:18px 22px;margin:20px 0;border-left:4px solid #ab7136}}nav{{display:flex;flex-wrap:wrap;gap:7px;margin:22px 0}}nav a{{background:#fff;padding:4px 11px;text-decoration:none;border:1px solid #c8d4d9}}article{{background:#fff;padding:24px;margin:24px 0;border:1px solid #d0d8de;scroll-margin-top:20px}}.row{{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}}.tag{{font-size:13px;padding:4px 9px;white-space:nowrap}}.warn{{background:#faead9;color:#814a1f}}.mutedtag{{background:#e9f0f1;color:#355963}}.finding{{font-size:17px}}.images{{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:18px 0}}figure{{margin:0;min-width:0}}figure a{{display:flex;background:#131a28;height:420px;align-items:center;justify-content:center}}img{{max-width:100%;max-height:100%;object-fit:contain}}figcaption{{padding:7px 0}}details{{border-top:1px solid #d7dfe3;padding-top:12px}}summary{{cursor:pointer}}code{{font-family:Consolas,monospace;overflow-wrap:anywhere}}.toolbar{{display:flex;gap:12px;flex-wrap:wrap;align-items:center}}input,select{{font:inherit;padding:7px;border:1px solid #aebec5}}footer{{padding:25px 0;font-size:13px;color:#61717e}}[hidden]{{display:none!important}}@media(max-width:800px){{.images{{grid-template-columns:1fr}}main{{padding:15px}}figure a{{height:350px}}}}</style></head><body><main>
<header><h1>I01–I18 控制器与接口融合审查</h1><p class="lead">明显问题集中在 I01–I14、I17、I18；I15 的接口已融入炉壁，问题在主控挂盒；I16 接口基本融入北墙，主控仍可下移细化。</p><p>来源：当前有效交付及已批准归档 · {now()} · Asia/Hong_Kong</p></header>
<div class="metrics"><div><b>18 台 / 21 形态</b><br>包含 I01 四阶</div><div><b>16 台 / 19 形态</b><br>明显外挂问题</div><div><b>I15</b><br>主控挂盒局部改善</div><div><b>I16</b><br>基本融入，主控细化</div></div>
<section class="note"><strong>本轮判断标准：</strong>控制器与接口是否属于机器自身的设备表面、支撑和维护组织。主色一致、与地板连通或背后有管线，都不足以证明自然融合。没有把工艺塔、吸风柱、夹架等主体设备误算为接口柱。</section>
<p>I01 四阶继承同一15×4×2前置白框板。I02–I14反复使用中央7×6×2主控盒和六个3×5×3接口矮墩。I17另立六根窄柱和一副主控架；I18另立11×5集中面板。形成问题的主要原因是先完成主体，再统一追加接口载体。</p>
<p><a href="21形态北立面对照.png">打开21形态北立面对照长图</a> · <a href="review.json">全部结论和来源身份</a> · <a href="rules-read.json">六规则读取身份</a> · <a href="{href(ROOT / 'rule/当前多方块设计规则.md')}">现有设计规则新增 #9</a></p>
<p class="meta">投影为已交付逐格数据与嵌入纹理生成，非游戏截图。北立面可能让不同Z位置叠在一起；独立性判断另用等轴图、实际坐标与去底板组件核对。所有21份NBT与蓝图逐格一致，来源SHA256检查通过。</p>
<p class="meta">所示主控和接口是交付预览中的标记位置；钻石、机壳及industrial_port_casing均不等同可运行控制器或仓室。I14–I17尚未正式接入Pattern，I18为待审候选；本页只判断外观融合。</p>
<nav>{nav}</nav><div class="toolbar"><input id="search" aria-label="搜索机器" placeholder="搜索编号、机器或问题"><select id="category" aria-label="筛选结论"><option value="">全部结论</option><option>明显问题</option><option>局部需改善</option><option>基本融入，主控细化</option></select><span id="count">21 / 21 形态</span></div>
{''.join(sections)}
<footer>【变更记录 #1】{now()}：删除无；新增21形态专项证据、逐台问题与建议；修改仅现有设计规则追加自然融合要求。未改结构、批准归档、正式资源或实例；未生成修订候选，未进行Pattern、仓室能力、配方或生存验收。本轮不重评全系统完成度。</footer>
</main><script>const articles=[...document.querySelectorAll('article')];function apply(){{const q=document.querySelector('#search').value.trim().toLowerCase(),c=document.querySelector('#category').value;let n=0;for(const a of articles){{a.hidden=!(a.textContent.toLowerCase().includes(q)&&(!c||a.dataset.category===c));if(!a.hidden)n++;}}document.querySelector('#count').textContent=n+' / 21 形态';}}document.querySelector('#search').addEventListener('input',apply);document.querySelector('#category').addEventListener('change',apply);</script></body></html>'''
    (OUT / 'index.html').write_text(document, encoding='utf-8')
    print('21份NBT逐格比对与来源保护检查通过，报告已写入。', flush=True)


def finalize():
    stamp = now()
    review = json.loads((OUT / 'review.json').read_text(encoding='utf-8'))
    canvas = Path('C:/Users/OWNER/.cursor/projects/c-Users-OWNER-Desktop-progrem-complate-progrem-hk3gtl/canvases/HK3GTL-controller-integration-review.canvas.tsx')
    content = canvas.read_text(encoding='utf-8')
    rows = [{k: row[k] for k in ['key', 'title', 'status', 'category', 'finding', 'suggestion', 'controller', 'source']} for row in review['items']]
    content = re.sub(r'^const rows=.*;$', lambda _: 'const rows=' + json.dumps(rows, ensure_ascii=False) + ';', content, flags=re.M)
    content = content.replace(' * 用途：在旁栏复查人工判断；不代表新候选、正式Pattern或游戏验收。',
        ' * 用途：在旁栏复查人工判断；不代表新候选、正式Pattern或游戏验收。\n * 【变更记录 #2】' + stamp + '：删除无；新增标记边界；修改建议标点；用途为与已复核HTML一致。')
    content = content.replace('本轮只审查并追加现有设计规则#9。', '主控与接口坐标是预览标记位置，不代表运行控制器或仓室。本轮只审查并追加现有设计规则#9。')
    canvas.write_text(content, encoding='utf-8')
    quote = '控制器以及接口要自然的融合到多方块结构里，不要再像现在一样那么突兀的弄一块面板在那了，我们重看一下  I01到I18的所有多方块结构，看看有没有哪台多方块结构是单独弄一块面板出来，或者是单独弄一样与多方块结构本身风格不对应的柱子出来顶着那些接口'
    document = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01–I18控制器接口自然融合要求与逐台审查</title><style>body{{max-width:1050px;margin:32px auto;padding:0 24px;font:16px/1.8 'Microsoft YaHei',sans-serif;color:#233b46;background:#f1f4f5}}section,header{{padding:20px 26px;background:white;margin:18px 0;border:1px solid #cdd9df}}header{{background:#1b303b;color:white}}h1{{font-size:26px}}h2{{font-size:21px}}a{{color:#176486}}code{{overflow-wrap:anywhere}}</style></head><body>
<header><h1>I01–I18控制器与接口自然融合要求及逐台审查</h1><p>记录时间：{stamp}，Asia/Hong_Kong（UTC+08:00）。原用户消息精确发送时间未知，采用实际记录时间。</p></header>
<section><h2>用户要求与确认</h2><p>用户原话：“{quote}”。</p><p>已确认：控制器与接口应自然融入机器本身，避免突兀面板或托举柱。本轮执行逐台审查；具体重设计布局尚未选定，新候选尚未生成或批准。</p></section>
<section><h2>有效版本及方法</h2><p>I01四阶、I02–I13采用10月20日批准的R172配色归档；I14用V4、I15用V3历史批准（不采用已否决V4）；I16用V3 HDV、I17用V1 QSV并核对10月22日批准归档；I18用V1 HBV待审候选。18台共21形态。</p><p>六份当前规则完整读取、截断补读并保留身份；读取10月20日配色批准、10月21日控制器核查及10月22日I16/I17批准和I18候选讨论。21形态有效等轴图及北立面均已实际审视，另核实际坐标、生成器及去底板组件；同色、连通或管线存在均不代表融合通过。</p></section>
<section><h2>逐台结论</h2><ul><li>I01四阶：继承15×4×2前置白框板，明显问题。</li><li>I02–I14：通用中央7×6×2主控盒与六个3×5×3接口矮墩，整排29×6×3；主体不同但接口套模板，明显问题。</li><li>I15：六接口嵌入三座炉座，主控另挂院门浅色盒，局部需改善。</li><li>I16：六接口融入连续北墙，没有独立接口柱；主控在雨棚顶，基本融合但可下移细化。</li><li>I17：六根各6方块的独立接口小柱及单独主控架，去底板后与主体分离，明显问题。</li><li>I18：11×5白框面板独立前置，虽后方有连接仍是外挂牌面，明显问题。</li></ul><p>合计16台／19形态明显问题，I15局部改善，I16基本融合。未将工艺塔、吸风柱与夹架误算为接口托柱。</p></section>
<section><h2>实际执行与覆盖关系</h2><p>21份NBT与蓝图逐格一致，21份源蓝图与NBT的SHA256未改变。独立复核确认数量、来源、133个本地链接目标与各台结论一致。结果已落HTML与旁栏索引。</p><p>rule/当前多方块设计规则.md已追加#9，覆盖旧“主控居中、白框、框内其余为接口”被机械解释为必须另立统一面板的做法。保留主控易识别、接口可达、必要能力、尺寸、电压、累积扩建与审批要求。旧批准文件和讨论不删除。</p><p>助手改造建议：I01接口并入塔身工艺裙座并统一规划四阶；I02–I14按每台实际工艺分区安排；I17取消专用接口柱与牌架；I18将接口分配到热室、闸室、抽气及检测设施本体。I15/I16优先局部调整主控，不据此推倒有效主体。</p><p>上述是待评审方向；没有修改结构、源交付、不可变批准归档、正式Pattern、配方或游戏实例；没有新修订号、部署、游戏成型或生存验收。本轮不重评原全系统分数。</p></section>
<section><h2>报告、下一步与变更记录</h2><p><a href="../../../logs/controller-integration-review-20261023/index.html">逐台图文审查</a> · <a href="../../../logs/controller-integration-review-20261023/review.json">合并结论</a> · <a href="../../../logs/controller-integration-review-20261023/21形态北立面对照.png">21形态立面对照</a> · <a href="../../../logs/controller-integration-review-20261023/rules-read.json">六规则读取身份</a> · <a href="../../../rule/当前多方块设计规则.md">设计规则#9</a></p><p>分审证据：同目录i01-i08.json、i09-i15.json、i16-i18.json。复现工具：tools/structure_delivery/review_controller_integration_20261023.py。</p><p>下一步按本轮发现制作独立融合修订候选并逐台评审；问题确认不等于新布局批准。I01应从新一阶候选开始统一规划累积扩建，旧批准归档保留。</p><p>【变更记录 #1】{stamp}：删除无；新增控制器接口融合要求、21形态审查证据与讨论；修改现有规则追加#9以覆盖统一外挂面板的旧解释；用途为后续修订建立依据，未修改游戏功能或结构。</p></section></body></html>'''
    discussion = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (stamp[:19].replace('T', '_').replace(':', '-') + '_I01-I18控制器接口自然融合要求与逐台审查.html')
    assert not discussion.exists()
    discussion.write_text(document, encoding='utf-8')
    save(OUT / 'rule-change-identity.json', {'time': stamp, 'purpose': '读取后规则追加身份，与读前checkpoint区分', 'path': 'rule/当前多方块设计规则.md', 'sha256': sha(ROOT / 'rule/当前多方块设计规则.md')})
    print(discussion.as_posix(), flush=True)


if __name__ == '__main__':
    if '--finalize' in sys.argv:
        finalize()
    elif '--report' in sys.argv:
        report()
    else:
        evidence()

# 【变更记录 #4】2026-10-23 23:41:24（内测5名称统一维护）：删除旧项目名引用；新增本条维护记录；修改项目路径、启动标识或纹理目录为 HK3GTL 对应名称；用途为统一工具与构建引用，保留原有业务逻辑。
