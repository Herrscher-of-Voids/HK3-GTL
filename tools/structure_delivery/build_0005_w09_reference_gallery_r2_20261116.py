# -*- coding: utf-8 -*-
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116'
FONT = 'C:/Windows/Fonts/msyh.ttc'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


refs = []
official = read('官方补充/官方补充清单.json')
for row in official['references']:
    r = dict(row)
    r.update(file='官方补充/' + row['file'], detail_file='官方补充/' + row['detail_file'],
             kind='官方设计访谈', group='Lor5aVmdiUE', collection='外网补充画面')
    r['subject'] = '链刃' if row['id'] == 'OF01' else '武器匣'
    r['note'] += ' ' + row['relationship_to_r1']
    r['part'] = {'OF01': '连接节', 'OF02': '宽面纹样', 'OF03': '侧面厚度', 'OF04': '宽面纹样',
                 'OF05': '护手握柄', 'OF06': '动作比例', 'OF07': '动作比例'}[r['id']]
    refs.append(r)

public = read('公开补充/sources.json')
for row in public['references']:
    refs.append(dict(id=row['id'], subject='组合设定' if row['id'] == 'R2-CG1' else '长枪',
                     view=row['view'], note='玩家3ds Max模型展示；保留原界面。' +
                     ('同一张图中分别陈列三兵与宽体武器。' if row['id'] == 'R2-CG1' else '四个视口合为一张来源图片，按一幅计数。'),
                     kind='玩家模型展示', file='公开补充/' + row['file'], source_url=public['source_url'],
                     image_url=row['image_url'], resolution=row['resolution'], group='CGJOY', seconds=None,
                     collection='外网补充画面', part='全形'))

excluded = []
for row in read('演示补充/references.json'):
    r = dict(row)
    if r['id'] == 'R2-G02':
        excluded.append(dict(id=r['id'], file=r['file'], source_url=r['source_url'],
                             reason='主要枪头和连接部位被强光遮挡，退出精选图册。'))
        continue
    if r['id'] == 'R2-G03':
        r.update(view='长枪远景与持握比例', note='远景仅对照枪杆、人物与持握比例，细节以近景及模型观察图核对。')
    if r['id'] == 'R2-G04':
        r.update(view='链刃尖端近身动作', note='可见局部尖端与近身挥动姿态，连接段和另一端未完整显露。红色轨迹单列为特效。')
    if r['id'] == 'R2-G05':
        r.update(view='太极与赤珠近身斜面', note='近身查看太极盘、赤珠和柄段的相对位置。')
    if r['id'] == 'R2-G08':
        r.update(view='角色菜单侧后方近景', note='角色菜单中可见骨白、朱红和黑色分区，按当帧朝向核对配色。')
    r['collection'] = '外网补充画面'
    r['part'] = '侧面厚度' if r['id'] in ('R2-G06', 'R2-G07') else '宽面纹样' if r['id'] in ('R2-G05', 'R2-G08') else '动作比例'
    refs.append(r)

model = read('模型补充/official-model-captures.json')
model_notes = {
    'sword': ('宝剑', '全形', '默认静态红黑渐变刃、旋卷护手与红白缠柄。'),
    'sword_guard': ('宝剑', '护手握柄', '局部观察骨白旋卷、灰紫三瓣曲面和护手厚度。'),
    'spear': ('长枪', '全形', '默认静态长枪；枪伸长等骨骼形态另与游戏展开帧对照。'),
    'spear_head': ('长枪', '枪头', '局部观察长叶尖、红X、骨白卷叉及收腰颈。'),
    'chain': ('链刃', '全形', '链剑材质组的默认收束态：单柄、灰紫分节刃与红色接头。'),
    'chain_joint': ('链刃', '连接节', '局部观察交叠扁箭形片、节间红色连接与侧厚。'),
    'chain_hilt': ('链刃', '护手握柄', '局部观察黑色菱形根部、红X、骨白护柄与红白缠带。'),
    'case': ('武器匣', '全形', '隔离大剑与剑柄材质组，两面太极与火纹、红色侧脊及黑紫壳体清楚。'),
    'case_roundels': ('武器匣', '宽面纹样', '局部观察太极盘、独立赤珠与骨白旋卷的前后层次。'),
    'case_tip': ('武器匣', '尖端', '局部观察尖端收薄、黑紫外壳与凸起红色侧脊。'),
    'inner_case': ('剑盒部件', '独立部件', '单独隔离PMX中名为剑盒的材质组，部件身份按原名称记录。'),
}
for row in model['captures']:
    stem = row['file'].removeprefix('official-mmd-').removesuffix('.png')
    key = stem.rsplit('-', 1)[0]
    if stem.endswith('rear_oblique'):
        key = stem.removesuffix('-rear_oblique')
    subject, part, note = model_notes[key]
    refs.append(dict(id='MMD-' + stem, subject=subject, view=row['label'].split('・')[-1], note=note,
                     kind='官方公开MMD离线观察', file='模型补充/' + row['file'], source_url=model['source'],
                     resolution=row['resolution'], group='official_model', seconds=None, part=part,
                     collection='模型离线观察', is_detail=row['is_detail'], materials=row['materials'],
                     sha256=row['sha256']))

for p in sorted((OUT / '公开补充').glob('storyboard*')):
    excluded.append(dict(file='公开补充/' + p.name, reason='低分辨率分镜拼图仅用于检索，退出独立参考图片计数。'))
analysis = read('模型补充/official-model-analysis.json')
excluded.extend(analysis['excluded'])

(OUT / '缩略图').mkdir(exist_ok=True)
for r in refs:
    r.setdefault('seconds', None)
    r['thumbnail'] = '缩略图/' + r['id'] + '.jpg'
    raw = (OUT / r['file']).read_bytes()
    r['sha256'] = hashlib.sha256(raw).hexdigest()
    r['bytes'] = len(raw)
    image = Image.open(OUT / r['file']).convert('RGB')
    thumb = ImageOps.contain(image, (640, 640), Image.Resampling.LANCZOS)
    thumb.save(OUT / r['thumbnail'], quality=90)

counts = dict(external_video_frames=14, external_stills=2, external_total=16, offline_observations=48,
              offline_full=30, offline_detail=18, displayed_references=len(refs), old_r1_not_recounted=39,
              official_detail_crops_not_recounted=7)
manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), task='W09武器补充参考R2', counts=counts,
                selection_note='外网补充按原帧或来源静图计数；原帧与局部、联系图与缩略图各计零次新增。48幅离线观察来自同一个官方公开MMD包，单列30全形与18局部。R1旧39幅保留独立入口，不纳入R2。',
                sources=[official['source'], dict(title=public['title'], url=public['source_url'], kind=public['kind']),
                         dict(title='官方活动公开MMD', url=model['source'], archive=model['archive'],
                              archive_sha256=model['archive_sha256'], kind=model['source_kind'])],
                references=refs, excluded=excluded)
write('参考清单.json', manifest)

font = ImageFont.truetype(FONT, 18)
title_font = ImageFont.truetype(FONT, 25)
contacts = []
for page in range(4):
    rows = refs[page * 16:(page + 1) * 16]
    sheet = Image.new('RGB', (1760, 1460), '#15171d')
    draw = ImageDraw.Draw(sheet)
    title = 'W09 R2 / 外网补充16幅' if page == 0 else f'W09 R2 / 官方公开MMD离线观察 {page}/3'
    draw.text((18, 15), title, font=title_font, fill='#e9d8b6')
    for i, r in enumerate(rows):
        x, y = (i % 4) * 440, 62 + (i // 4) * 346
        image = Image.open(OUT / r['thumbnail']).convert('RGB')
        image = ImageOps.contain(image, (430, 270), Image.Resampling.LANCZOS)
        sheet.paste(image, (x + (440 - image.width) // 2, y + (270 - image.height) // 2))
        draw.text((x + 8, y + 275), r['id'], font=font, fill='#e4d4b1')
        label = r['subject'] + ' / ' + r['view']
        draw.text((x + 8, y + 302), label[:24], font=font, fill='#bfc3ce')
    name = f'联系图-{page + 1:02d}.jpg'
    sheet.save(OUT / name, quality=93)
    contacts.append(name)
manifest['contact_sheets'] = contacts
write('参考清单.json', manifest)

def options(key):
    return '<option value="">全部</option>' + ''.join('<option>' + escape(v) + '</option>' for v in dict.fromkeys(r[key] for r in refs))


cards = []
for i, r in enumerate(refs):
    time = '' if r['seconds'] is None else ' · ' + str(r['seconds']) + '秒'
    detail = '<button class="text" data-open="' + str(i) + '" data-detail="1">局部</button>' if r.get('detail_file') else ''
    cards.append(f'''<article data-index="{i}" data-collection="{r['collection']}"><button class="picture" data-open="{i}"><img src="{r['thumbnail']}" loading="lazy" alt="{escape(r['subject'] + ' ' + r['view'])}"></button><div class="caption"><small>{r['id']} · {r['kind']}{time}</small><h2>{r['subject']} · {escape(r['view'])}</h2><p>{escape(r['note'])}</p><div class="links"><a href="{escape(r['source_url'])}" target="_blank" rel="noreferrer">来源 ↗</a><a href="{r['file']}" target="_blank">原尺寸 {r['resolution'][0]}×{r['resolution'][1]} ↗</a>{detail}</div></div></article>''')

html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W09 · 武器补充参考R2</title><style>
:root{color-scheme:dark;--bg:#111319;--panel:#1b1e26;--line:#353945;--gold:#ddc18a;--text:#e9e9ee}*{box-sizing:border-box}body{margin:0;color:var(--text);background:var(--bg);font:15px/1.65 'Microsoft YaHei',sans-serif}a{color:var(--gold)}header,main,footer{max-width:1640px;margin:auto;padding:28px}header{padding-top:42px;border-bottom:1px solid var(--line)}.eyebrow,small{color:#b9a57f}h1{font-size:32px;margin:6px 0 20px}header p{max-width:1140px;margin:8px 0;color:#bfc4d0}.numbers{display:flex;gap:28px;flex-wrap:wrap;margin:15px 0}.numbers strong{font-size:29px;color:#eee1c3}.numbers span{display:block;color:#abb2c2;font-size:13px}.tabs{display:flex;gap:9px;flex-wrap:wrap;margin:25px 0 0}button,input,select{font:inherit}button{cursor:pointer}.tabs button{color:#d2d5df;background:#20242d;border:1px solid var(--line);padding:10px 18px;border-radius:5px}.tabs button[aria-pressed="true"]{background:#594633;color:#fff0cd;border-color:#ad8b55}.tools{display:flex;gap:14px;flex-wrap:wrap;align-items:center;background:#111319f7;position:sticky;top:0;padding:14px 0;z-index:2;border-bottom:1px solid var(--line);margin-bottom:22px}input,select{color:#e6e8ee;background:#20242d;border:1px solid var(--line);border-radius:4px;padding:8px 10px}input{flex:1;min-width:180px}#shown{color:#aeb5c4}.gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}article{background:var(--panel);border:1px solid #303542;border-radius:7px;overflow:hidden}article[hidden]{display:none}.picture{display:block;border:0;padding:0;width:100%;background:#0e1015}.picture img{display:block;width:100%;height:300px;object-fit:contain}.caption{padding:15px 17px 18px}.caption small{font-size:11px}.caption h2{font-size:17px;margin:6px 0}.caption p{font-size:13px;color:#bfc5d3;margin:8px 0 13px}.links{display:flex;gap:16px;align-items:center;flex-wrap:wrap;font-size:12px}.text{padding:0;background:none;color:var(--gold);border:0;font-size:12px;text-decoration:underline}footer{border-top:1px solid var(--line);color:#aeb5c4;font-size:13px}footer p{margin:7px 0}dialog{width:min(1570px,96vw);max-height:97vh;background:#11141a;border:1px solid #5d6573;border-radius:7px;color:var(--text);padding:16px}dialog::backdrop{background:#000e}.nav{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:9px}.nav button{color:#eee;background:#252b35;border:1px solid #4c5564;border-radius:4px;padding:5px 12px}.nav a{font-size:13px}#close{margin-left:auto}#zoomArea{overflow:auto;max-height:70vh;background:#080a0e}#large{display:block;width:100%;max-height:70vh;object-fit:contain;margin:auto}#zoomArea.native #large{width:var(--native-width);max-width:none;max-height:none}#modalTitle{font-size:18px;margin:10px 0 3px}#modalNote{font-size:13px;color:#c0c7d5;margin:0}#empty{padding:40px;color:#b8bdca}#detail[hidden]{display:none}@media(max-width:1100px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}.picture img{height:270px}}@media(max-width:700px){header,main,footer{padding:19px}.gallery{grid-template-columns:1fr}h1{font-size:25px}.numbers{gap:20px}.tools{position:static}.picture img{height:310px}}
</style><header><div class="eyebrow">0005 / W09 改造参考 · R2</div><h1>识之律者 · 武器细节与厚度</h1><div class="numbers"><div><strong>16</strong><span>外网补充画面：14原帧＋2静图</span></div><div><strong>48</strong><span>官方公开MMD离线观察：30全形＋18局部</span></div><div><strong>39</strong><span>旧R1画面独立保留，本页不重计</span></div></div><p>外网画面与本地模型观察分别浏览。官方访谈7幅补帧中，5幅与R1属于同一原画或转台组；原帧与附属局部合计一幅。公开展示中的四视口合图按一张计数。</p><p>48幅模型图由同一个官方活动公开MMD包离线渲染，原始静态几何与贴图按材质组隔离显示；其中18幅为局部近景。骨骼展开形态与游戏动作帧分别核对。</p><p><a href="../0005_W09_识律武器多角度参考_20261116/index.html">旧R1图册 ↗</a> · <a href="参考清单.json">完整来源与排除记录 ↗</a> · CONTACT_LINKS</p><div class="tabs"><button data-tab="外网补充画面" aria-pressed="true">外网补充画面 · 16</button><button data-tab="模型离线观察" aria-pressed="false">模型离线观察 · 48</button><button data-tab="" aria-pressed="false">全部观察条目 · 64</button></div></header><main><div class="tools"><label>武器 <select id="subject">SUBJECT_OPTIONS</select></label><label>部位 <select id="part">PART_OPTIONS</select></label><label>来源 <select id="kind">KIND_OPTIONS</select></label><input id="search" aria-label="搜索参考" placeholder="搜索编号、纹样、角度……"><span id="shown"></span></div><div class="gallery">CARDS</div><div id="empty" hidden>当前筛选没有对应画面。</div></main><footer><p>模型来源：<a href="https://www.bilibili.com/blackboard/activity-bhxcyx.html" target="_blank" rel="noreferrer">崩坏3·新春影像大赏</a>，模型编辑神帝宇，版权miHoYo。离线图采用无光照材质观察原贴图；模型及原贴图保留在本地缓存。</p><p>链剑默认收束态可见灰紫分节刃与红色接头，展开连接另参照OF01。剑盒独立材质组按PMX原名记录。带局部入口的官方原帧，在放大窗口切换查看。</p><p>缩略图、联系图、附属裁图均为派生浏览图。G02强光遮挡帧、分镜拼图与无武器雕塑已记录排除原因。</p></footer><dialog id="modal"><div class="nav"><button id="prev" aria-label="上一幅">← 上一幅</button><button id="next" aria-label="下一幅">下一幅 →</button><button id="fit">适应窗口</button><button id="native">原像素</button><button id="detail" hidden>查看局部</button><a id="origin" target="_blank" rel="noreferrer">来源 ↗</a><a id="original" target="_blank">当前原图 ↗</a><button id="close">关闭 ✕</button></div><div id="zoomArea"><img id="large" alt=""></div><h2 id="modalTitle"></h2><p id="modalNote"></p></dialog><script>
const refs=REF_DATA,cards=[...document.querySelectorAll('article')],modal=document.querySelector('#modal'),zoomArea=document.querySelector('#zoomArea');let collection='外网补充画面',visible=[],current=0,detail=false;
function filter(){const subject=document.querySelector('#subject').value,part=document.querySelector('#part').value,kind=document.querySelector('#kind').value,q=document.querySelector('#search').value.trim().toLowerCase();visible=[];cards.forEach((card,i)=>{const r=refs[i],show=(!collection||r.collection===collection)&&(!subject||r.subject===subject)&&(!part||r.part===part)&&(!kind||r.kind===kind)&&(!q||`${r.id} ${r.subject} ${r.part} ${r.view} ${r.note} ${r.kind}`.toLowerCase().includes(q));card.hidden=!show;if(show)visible.push(i)});document.querySelector('#shown').textContent=`当前 ${visible.length} 幅`;document.querySelector('#empty').hidden=visible.length>0;}
function render(){const r=refs[current],file=detail?r.detail_file:r.file,size=detail?r.detail_resolution:r.resolution;document.querySelector('#large').src=file;document.querySelector('#large').alt=`${r.subject} ${r.view}`;zoomArea.style.setProperty('--native-width',size[0]+'px');document.querySelector('#origin').href=r.source_url;document.querySelector('#original').href=file;document.querySelector('#modalTitle').textContent=`${r.id} · ${r.subject} · ${r.view}${detail?' · 局部':''}`;document.querySelector('#modalNote').textContent=`${r.kind} · ${r.seconds===null?'静态观察':r.seconds+'秒'} · ${size.join('×')} · ${r.note}`;document.querySelector('#detail').hidden=!r.detail_file;document.querySelector('#detail').textContent=detail?'查看原帧':'查看局部';zoomArea.classList.remove('native');zoomArea.scrollTop=0;zoomArea.scrollLeft=0;}
function show(i,d=false){current=i;detail=d;render();if(!modal.open)modal.showModal();}function step(d){show(visible[(visible.indexOf(current)+d+visible.length)%visible.length]);}
document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>show(Number(b.dataset.open),b.dataset.detail==='1'));document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{collection=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(x=>x.setAttribute('aria-pressed',x===b));filter();});['subject','part','kind','search'].forEach(id=>document.querySelector('#'+id).addEventListener('input',filter));document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.querySelector('#close').onclick=()=>modal.close();document.querySelector('#fit').onclick=()=>zoomArea.classList.remove('native');document.querySelector('#native').onclick=()=>zoomArea.classList.add('native');document.querySelector('#detail').onclick=()=>{detail=!detail;render();};document.addEventListener('keydown',e=>{if(modal.open&&e.key==='ArrowLeft')step(-1);if(modal.open&&e.key==='ArrowRight')step(1);});filter();
</script></html>'''
for key, value in {'CONTACT_LINKS': ' · '.join(f'<a href="{p}">联系图{i + 1} ↗</a>' for i, p in enumerate(contacts)),
                   'SUBJECT_OPTIONS': options('subject'), 'PART_OPTIONS': options('part'), 'KIND_OPTIONS': options('kind'),
                   'CARDS': ''.join(cards), 'REF_DATA': json.dumps(refs, ensure_ascii=False)}.items():
    html = html.replace(key, value)
(OUT / 'index.html').write_text(html, encoding='utf-8')
print(json.dumps(dict(out=str(OUT), counts=counts, by_kind=dict(Counter(r['kind'] for r in refs))), ensure_ascii=False))
