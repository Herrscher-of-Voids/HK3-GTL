# -*- coding: utf-8 -*-
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import hashlib
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律武器多角度参考_20261116'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w09-reference-videos')
SOURCES = {
    'guide': dict(title='识之律者作战指南', kind='官方指南', url='https://bh3.mihoyo.com/gl/article/14032'),
    'ykNXZuPW-j0': dict(title='[Herrscher of Sentience] Tutorial Video', kind='官方游戏演示'),
    '1KqkQL4--dM': dict(title='Honkai Impact 3rd v4.6 [Unequaled, Unrivaled] Trailer', kind='官方版本预告'),
    'Lor5aVmdiUE': dict(title='《崩壞3rd》《識之律者》角色設計揭密', kind='官方设计访谈'),
    'NQdVJcEE0m4': dict(title='Shattered Samsara / 渡尘（日配）', kind='官方动画'),
    'XE9nwM0tKpY': dict(title='Herrscher Of Sentience Moveset - Honkai Impact 3rd Beta 4.6v1', kind='玩家测试服录像'),
    'QjLnwUFVLXo': dict(title='识之律者三兵慢镜，霍-Moira作品转载', kind='玩家剪辑转载', original_author_url='https://space.bilibili.com/12344893/video'),
    'sketchfab': dict(title='宝剑·言多必弑', kind='玩家模型展示', author='爆炒腰花', url='https://sketchfab.com/3d-models/none-047e13859d714d8cbeabf91fbde5f8c1', image_url='https://media.sketchfab.com/models/047e13859d714d8cbeabf91fbde5f8c1/thumbnails/361a732943ca43a9be33df63474a06dd/d771a1d7986a4f63a95cc60c34fec377.jpeg'),
    'purinmods': dict(title='Senti / Herrscher of Sentience MMD展示', kind='玩家MMD展示', author='purinmods', url='https://www.deviantart.com/purinmods/art/Senti---Herrscher-of-Sentience-DL-1213419278', image_url='https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/4d7b8f05-69f4-4a09-bbc4-fc631a719773/dk2fsb2-e81ea5d5-650a-42d1-bcd1-8e3ba75499ae.png/v1/fill/w_782,h_1022/senti_herrscher_of_sentience_dl_by_purinmods_dk2fsb2-pre.png'),
}
SELECTION = [
    ('组合设定', 'Lor5aVmdiUE', 129.75, '设计工作屏幕', '右侧屏幕可对照细长宝剑与宽大匣体的轮廓。'),
    ('组合设定', '1KqkQL4--dM', 44.25, '官方组合立绘', '集中查看剑、枪、链刃和太极纹匣体的配色关系。'),
    ('武器匣', 'Lor5aVmdiUE', 132.25, '后侧边缘', '窄侧面可见匣体厚度、下沿和悬浮姿态。'),
    ('武器匣', 'Lor5aVmdiUE', 134.25, '后斜侧', '对照黑色宽面、乳白边缘和红色侧壁。'),
    ('武器匣', 'Lor5aVmdiUE', 136.25, '宽面斜视', '太极圆纹、上部环状装饰与下端尖形完整可见。'),
    ('武器匣', 'Lor5aVmdiUE', 139.75, '前斜侧', '查看前端收尖、侧面层次和柄端伸出方向。'),
    ('武器匣', 'ykNXZuPW-j0', 34, '站姿正斜面', '武器匣与人物同框，便于理解整体长度和悬置位置。'),
    ('武器匣', 'ykNXZuPW-j0', 40, '动作背斜面', '宽面、边框和匣体下沿随视角分开显露。'),
    ('武器匣', 'ykNXZuPW-j0', 49, '上端近景', '集中观察太极纹与红色圆形装饰周围的轮廓。'),
    ('武器匣', 'ykNXZuPW-j0', 58.5, '水平低侧面', '滑行时能看到匣体窄侧、厚度和下表面。'),
    ('武器匣', 'ykNXZuPW-j0', 95, '背斜侧全长', '查看匣体宽面与手中细长宝剑的相对位置。'),
    ('武器匣', 'purinmods', '公开模型图/purinmods-case.png', '玩家MMD正面', '作者称模型来自官方MMD；用于辅助观察纹样与侧壁。'),
    ('宝剑', 'ykNXZuPW-j0', 52, '奔跑侧面', '手中细长剑体与剑柄在侧面姿势下显露。'),
    ('宝剑', 'ykNXZuPW-j0', 64, '直立正斜面', '前景直立宝剑适合核对红黑剑身、白色护手和缠柄。'),
    ('宝剑', 'ykNXZuPW-j0', 69, '肩后近景', '近距离查看剑身红黑分区、护手与柄端。'),
    ('宝剑', 'ykNXZuPW-j0', 90, '挥剑斜俯视', '查看持握与挥出后的细长轮廓。'),
    ('宝剑', 'ykNXZuPW-j0', 93, '背面斜持', '辅助核对斜持宝剑与身后武器匣的尺寸关系。'),
    ('宝剑', '1KqkQL4--dM', 38.25, '抽剑俯视', '从上方查看剑脊、缠柄及持握位置。'),
    ('宝剑', 'QjLnwUFVLXo', 15, '水平侧面', '侧面持剑画面补充剑刃的长宽与指向。'),
    ('宝剑', 'XE9nwM0tKpY', 51.75, '背斜侧起势', '测试服画面补充剑身侧面和起势姿态。'),
    ('宝剑', 'sketchfab', '公开模型图/sketchfab-sword.jpg', '玩家模型侧面', '独立模型展示护手与剑刃；材质处理按玩家展示单独记录。'),
    ('长枪', 'ykNXZuPW-j0', 74, '正面横持', '红黑长杆、两端及护手位置可同框观察。'),
    ('长枪', 'ykNXZuPW-j0', 76, '侧面全长', '长枪横贯身体，便于对照杆身与尖端比例。'),
    ('长枪', 'ykNXZuPW-j0', 105, '突刺后斜视', '查看突刺时杆身方向、两端形状与握持距离。'),
    ('长枪', 'ykNXZuPW-j0', 109, '握杆背斜视', '下方可见白色尖端与红色缠绕杆身。'),
    ('长枪', 'QjLnwUFVLXo', 27, '竖持全长', '长枪竖直展开，完整观察两端和中部杆身。'),
    ('长枪', 'QjLnwUFVLXo', 31, '斜向下刺', '斜侧动作显露尾端、握点及向下突刺方向。'),
    ('长枪', 'QjLnwUFVLXo', 37, '收势正面', '正面画面补充枪杆的缠绕纹样与柄端。'),
    ('长枪', 'XE9nwM0tKpY', 63, '竖杆背面', '测试服背面姿势补充杆体与头部的连接方向。'),
    ('链刃', 'ykNXZuPW-j0', 44, '横向展开', '观察链节曲线与连接段，左侧端部未完整入镜。'),
    ('链刃', 'ykNXZuPW-j0', 55, '斜俯视', '从上方查看武器与人物的空间关系。'),
    ('链刃', 'ykNXZuPW-j0', 113, '侧后方甩出', '查看链刃伸出方向与回收侧的位置。'),
    ('链刃', 'ykNXZuPW-j0', 132, '背面举刃', '单端举起近景，另一端与连接段未完整显露。'),
    ('链刃', 'XE9nwM0tKpY', 70.5, '双端高举', '测试服画面可分辨两段刚性杆刃与中间连接。'),
    ('链刃', 'XE9nwM0tKpY', 109, '甩刃背斜视', '补充自由端的指向与连接段弯折。'),
    ('链刃', 'QjLnwUFVLXo', 91, '侧上方挥动', '侧上方机位显示两端展开后的轮廓。'),
    ('链刃', 'QjLnwUFVLXo', 99, '侧面收放', '横向动作补充杆刃、手部和连接段的位置。'),
    ('链刃', 'QjLnwUFVLXo', 129, '前斜侧持握', '武器靠近镜头，可查看端部白色边缘与红黑分区。'),
    ('链刃', 'QjLnwUFVLXo', 131, '正俯视双端', '从上方查看左右两端、握持与连接走向。'),
    ('链刃', 'QjLnwUFVLXo', 137, '后斜侧横展', '补充一端横置、另一端垂落的形态。'),
    ('链刃', 'QjLnwUFVLXo', 141, '正面横展', '正面补充双端分离的距离与杆刃长度关系。'),
    ('动画补充', 'NQdVJcEE0m4', 59.5, '薄刃面部近景', '官方动画中的细长剑体，动画造型单独比较。'),
    ('动画补充', 'NQdVJcEE0m4', 64.5, '上举持剑近景', '官方动画中的剑身与持握姿态，剑柄部分出画。'),
    ('动画补充', 'NQdVJcEE0m4', 75.5, '大剑斜正面', '官方动画中的深色大剑面、环形纹样与下缘轮廓。'),
    ('动画补充', 'NQdVJcEE0m4', 82.5, '宽体武器斜前方', '观察黑金宽体与持握姿态，左侧红白斩击特效单独比较。'),
]
EXCLUDED = {
    13: '无可辨识手持宝剑，主体为身后武器匣。',
    16: '宝剑被动作与特效遮挡。',
    31: '武器过小，细节不足。',
    40: '品类有疑义，连续长杆与两端形状更接近长枪。',
    41: '动作残影为主，双端实形不可辨。',
    44: '大剑主体被橙色弹道遮挡。',
}
FINDINGS = [
    '原版三兵分别为宝剑、长枪、链刃，官方教程与作战指南明确列出三种攻击方式。',
    '宽大的太极纹武器匣与抽出的细长宝剑分别记录。匣体可见黑色宽面、乳白装饰、红色侧壁和明显厚度。',
    '长枪以细长杆身、红黑缠绕和两端结构形成轮廓；链刃须分别观察两端刚性部分与中间柔性连接。',
    '主形参考优先使用官方游戏画面和设计访谈，玩家模型、测试服与动画各自标明来源。',
]


def collect(item):
    index, (subject, source_id, time_or_file, view, note) = item
    source = SOURCES[source_id]
    if isinstance(time_or_file, (int, float)):
        seconds = time_or_file
        filename = f'参考原帧/{index:02d}-{source_id}-{seconds:g}s.jpg'
        target = OUT / filename
        if not target.exists():
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(seconds), '-i', str(CACHE / f'{source_id}.mp4'), '-frames:v', '1', '-q:v', '2', '-y', str(target)], check=True)
        url = source['url'] + f'&t={int(seconds)}s'
    else:
        seconds = None
        filename = time_or_file
        target = OUT / filename
        url = source['url']
    original = Image.open(target)
    thumb = Image.new('RGB', (640, 360), '#111318')
    small = original.convert('RGBA')
    small.thumbnail((640, 360))
    thumb.paste(small, ((640 - small.width) // 2, (360 - small.height) // 2), small)
    thumbnail = f'缩略图/{index:02d}.jpg'
    thumb.save(OUT / thumbnail, quality=91)
    return dict(id=f'R{index:02d}', subject=subject, source=source_id, kind=source['kind'], view=view, note=note, seconds=seconds, source_url=url, file=filename, thumbnail=thumbnail, resolution=list(original.size), sha256=hashlib.sha256(target.read_bytes()).hexdigest())


def main():
    for folder in ['参考原帧', '缩略图', '联系图']:
        (OUT / folder).mkdir(exist_ok=True)
    for key, source in SOURCES.items():
        if len(key) == 11:
            info = json.loads((CACHE / f'{key}.info.json').read_text(encoding='utf-8'))
            source.update(url=f'https://www.youtube.com/watch?v={key}', upload_date=info['upload_date'], channel_id=info['channel_id'], channel='崩壞3rd' if key == 'Lor5aVmdiUE' else '原神·攻略君' if key == 'QjLnwUFVLXo' else info['channel'], duration=info['duration'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        references = list(pool.map(collect, ((i, item) for i, item in enumerate(SELECTION, 1) if i not in EXCLUDED)))
    counts = dict(Counter(r['subject'] for r in references))
    manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), thread_id='01a1e02a-4d20-7d81-bdab-70404f66086d', task='W09改造第1步：识之律者武器图片参考', count=len(references), counts=counts, sources=SOURCES, references=references, findings=FINDINGS,
        selection_note=f'{len(references)}幅选用画面包含不同视角、距离与动作阶段；同一转台的相邻角度属于同一镜头组。缩略图与联系图不重复计数。视频帧保留原尺寸，未绘制辅助线。',
        excluded=[dict(id=f'R{i:02d}', reason=reason) for i, reason in EXCLUDED.items()],
        excluded_note='先前下载的官方指南9张静图为角色横幅、拳套与队伍推荐，均未计入武器多角度参考。',
        official_model=dict(page='https://www.bilibili.com/blackboard/activity-bhxcyx.html', url='https://activity.hdslb.com/blackboard/static/20210129/20780030fd6f6f94ac205810f269cf4d/shizhilvzhe.zip', sha256='3217177da64b945291373a7a8bc528c7f2d6697947ab3f585f7c5e00811558b6', relevant_files=['武器.pmx', '识之律者.pmx', '剑.png', '剑1.png', '剑盒.png', '大剑.png', '枪.png'], status='已读取目录与使用规则，本交付只记录来源链接；PMX与贴图未复制进模组或图册。'))
    (OUT / '参考清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
    for offset in range(0, len(references), 12):
        sheet = Image.new('RGB', (1920, 1230), '#12151b')
        draw = ImageDraw.Draw(sheet)
        for i, ref in enumerate(references[offset:offset + 12]):
            x, y = i % 3 * 640, i // 3 * 306
            im = Image.open(OUT / ref['thumbnail']).resize((480, 270))
            sheet.paste(im, (x + 80, y))
            draw.text((x + 12, y + 273), f"{ref['id']} · {ref['subject']} · {ref['view']}", font=font, fill='#e8d8b7')
        sheet.save(OUT / f'联系图/武器参考-{offset // 12 + 1:02d}.jpg', quality=91)
    picks = ['R03', 'R05', 'R14', 'R15', 'R21', 'R22', 'R26', 'R34', 'R39']
    overview = Image.new('RGB', (1920, 918), '#12151b')
    draw = ImageDraw.Draw(overview)
    by_id = {ref['id']: ref for ref in references}
    for i, ref_id in enumerate(picks):
        ref = by_id[ref_id]
        x, y = i % 3 * 640, i // 3 * 306
        overview.paste(Image.open(OUT / ref['thumbnail']).resize((480, 270)), (x + 80, y))
        draw.text((x + 12, y + 273), f"{ref['id']} · {ref['subject']} · {ref['view']}", font=font, fill='#e8d8b7')
    overview.save(OUT / '武器参考选览.jpg', quality=93)
    cards = []
    for i, r in enumerate(references):
        time = f"{r['seconds']:g}s" if r['seconds'] is not None else '静图'
        cards.append(f'''<article data-index="{i}" data-subject="{r['subject']}" data-kind="{r['kind']}"><button class="picture" data-open="{i}"><img src="{r['thumbnail']}" loading="lazy" alt="{r['subject']}，{r['view']}"></button><div class="caption"><small>{r['id']} / {r['kind']} / {time}</small><h2>{r['subject']} · {r['view']}</h2><p>{r['note']}</p><a href="{r['source_url']}" target="_blank" rel="noreferrer">查看来源 ↗</a><a href="{r['file']}" target="_blank">原尺寸 {r['resolution'][0]}×{r['resolution'][1]} ↗</a></div></article>''')
    source_links = ''.join(f'<li><span>{escape(s["kind"])}</span> <a href="{s["url"]}" target="_blank" rel="noreferrer">{escape(s["title"])}</a></li>' for s in SOURCES.values())
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>W09 · 识之律者武器参考</title><style>
    :root{color-scheme:dark;--ink:#101217;--line:#31343d;--gold:#dbbd80;--red:#d64d53}*{box-sizing:border-box}body{margin:0;background:var(--ink);color:#e8e8eb;font:15px/1.65 "Microsoft YaHei",sans-serif}a{color:var(--gold)}header,main,footer{max-width:1600px;margin:auto;padding:30px}header{padding-top:45px;border-bottom:1px solid var(--line)}.eyebrow{color:var(--gold);letter-spacing:.15em;font-size:12px}h1{font-size:34px;margin:8px 0 12px;font-weight:650}header p{color:#b4b8c3;max-width:1050px;margin:8px 0}.count{color:#eee3ce;font-size:18px}.facts{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:22px 0 0}.facts p{border-left:2px solid var(--red);padding-left:14px;margin:0;color:#d2d3db;font-size:14px}.tools{display:flex;gap:12px;align-items:center;flex-wrap:wrap;position:sticky;top:0;z-index:2;background:#101217f5;padding:15px 0;margin-bottom:20px;border-bottom:1px solid var(--line)}select,input,button{font:inherit}select,input{padding:9px 12px;color:#eee;background:#1b1e25;border:1px solid var(--line);border-radius:5px}input{flex:1;min-width:190px}#shown{color:#adb1bd}#gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}article{background:#191c23;border:1px solid #2d3039;border-radius:8px;overflow:hidden}article[hidden]{display:none}.picture{width:100%;display:block;background:#0c0e12;border:0;padding:0;cursor:zoom-in}.picture img{display:block;aspect-ratio:16/9;width:100%;object-fit:contain}.caption{padding:15px 17px 18px}.caption small{color:#a2a6b2;font-size:11px}.caption h2{font-size:17px;margin:6px 0}.caption p{font-size:13px;color:#bec1cc;min-height:44px;margin:5px 0 14px}.caption a{font-size:12px;margin-right:15px}footer{border-top:1px solid var(--line);color:#b3b7c2;font-size:13px}footer h2{font-size:18px;color:#ddd}footer ul{padding-left:20px}footer li{margin:9px 0}footer li span{display:inline-block;min-width:130px;color:#a7a9b1}dialog{background:#11141b;color:#eee;border:1px solid #525764;border-radius:8px;width:min(1500px,96vw);max-height:96vh;padding:15px}dialog::backdrop{background:#000d}#large{display:block;max-height:73vh;width:100%;object-fit:contain;background:#07090d}#modalTitle{margin:10px 0 2px;font-size:18px}#modalNote{font-size:14px;color:#c2c6d2;margin:4px 0}.nav{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.nav button{color:#eee;background:#252a34;border:1px solid #454b59;border-radius:4px;padding:5px 14px;cursor:pointer}#close{margin-left:auto}.nav a{font-size:13px}@media(max-width:1050px){#gallery{grid-template-columns:repeat(2,1fr)}h1{font-size:28px}}@media(max-width:680px){header,main,footer{padding:20px}.facts{grid-template-columns:1fr}#gallery{grid-template-columns:1fr}.caption p{min-height:0}}
    </style><header><div class="eyebrow">0005 / W09 改造 · 第1步</div><h1>识之律者 · 三兵与武器匣</h1><div class="count">__COUNT__ 幅精选画面 · 6 段视频 · 2 张公开模型图</div><p>覆盖正斜面、背斜面、侧面、俯视、持握与展开。官方游戏画面、设计访谈、动画和玩家展示逐张标明。点击图片放大，原尺寸入口保留完整画面。</p><p>同一转台按不同角度取帧；其余包含不同距离与动作阶段。__COUNT__幅画面按文件计数，同镜头组与局部细节分别说明。</p><div class="facts">__FACTS__</div></header><main><div class="tools"><label>武器 <select id="subject"><option value="">全部</option>__SUBJECTS__</select></label><label>来源 <select id="kind"><option value="">全部</option>__KINDS__</select></label><input id="search" placeholder="搜索角度、纹样、厚度……" aria-label="搜索参考图"><span id="shown"></span></div><div id="gallery">__CARDS__</div></main><footer><h2>可追溯来源</h2><ul>__SOURCES__</ul><p>形体优先依据官方游戏与设计访谈。玩家MMD展示图的模型来源为发布者说明；Sketchfab图按玩家模型记录。动画画面单独归组，测试服逐张注明版本。</p><p><a href="https://www.bilibili.com/blackboard/activity-bhxcyx.html" target="_blank" rel="noreferrer">官方MMD活动页</a> · <a href="参考清单.json" target="_blank">逐图清单与来源</a> · <a href="武器参考选览.jpg" target="_blank">参考选览</a></p><p>官方模型包已核对含武器.pmx、剑、枪与剑盒贴图，图册记录下载链接和目录。先前指南中的拳套、角色横幅和队伍推荐图退出本轮武器计数。</p></footer><dialog id="modal"><div class="nav"><button id="prev">← 上一张</button><button id="next">下一张 →</button><a id="original" target="_blank">打开原尺寸 ↗</a><a id="origin" target="_blank" rel="noreferrer">查看来源 ↗</a><button id="close">关闭 ×</button></div><img id="large" alt=""><h2 id="modalTitle"></h2><p id="modalNote"></p></dialog><script>
    const refs=__DATA__, cards=[...document.querySelectorAll('article')], subject=document.querySelector('#subject'), kind=document.querySelector('#kind'), search=document.querySelector('#search'), modal=document.querySelector('#modal');let visible=refs.map((_,i)=>i),current=0;
    function filter(){const q=search.value.trim().toLowerCase();visible=[];cards.forEach((card,i)=>{const r=refs[i],show=(!subject.value||r.subject===subject.value)&&(!kind.value||r.kind===kind.value)&&(!q||`${r.id} ${r.subject} ${r.view} ${r.note} ${r.kind}`.toLowerCase().includes(q));card.hidden=!show;if(show)visible.push(i)});document.querySelector('#shown').textContent=`${visible.length} / ${refs.length} 幅`}
    function show(i){current=i;const r=refs[i];document.querySelector('#large').src=r.file;document.querySelector('#large').alt=`${r.subject} ${r.view}`;document.querySelector('#original').href=r.file;document.querySelector('#origin').href=r.source_url;document.querySelector('#modalTitle').textContent=`${r.id} · ${r.subject} · ${r.view}`;document.querySelector('#modalNote').textContent=`${r.kind} · ${r.seconds===null?'静图':r.seconds+'s'} · ${r.resolution.join('×')} · ${r.note}`;if(!modal.open)modal.showModal()}
    function step(delta){show(visible[(visible.indexOf(current)+delta+visible.length)%visible.length])}document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>show(Number(b.dataset.open)));[subject,kind,search].forEach(el=>el.addEventListener('input',filter));document.querySelector('#close').onclick=()=>modal.close();document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.addEventListener('keydown',e=>{if(modal.open&&e.key==='ArrowLeft')step(-1);if(modal.open&&e.key==='ArrowRight')step(1)});filter();
    </script></html>'''
    html = html.replace('__COUNT__', str(len(references))).replace('__FACTS__', ''.join(f'<p>{escape(f)}</p>' for f in FINDINGS)).replace('__SUBJECTS__', ''.join(f'<option>{k}</option>' for k in counts)).replace('__KINDS__', ''.join(f'<option>{k}</option>' for k in dict.fromkeys(r['kind'] for r in references))).replace('__CARDS__', ''.join(cards)).replace('__SOURCES__', source_links).replace('__DATA__', json.dumps(references, ensure_ascii=False))
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    print(json.dumps(dict(out=str(OUT), count=len(references), counts=counts), ensure_ascii=False))


if __name__ == '__main__':
    main()
