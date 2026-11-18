import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W11_支配人偶多角度重塑_P1_20261117'


def load(folder, name):
    return json.loads((OUT / 'references' / folder / name).read_text(encoding='utf-8'))


def image_form(item):
    number = int(item['id'][1:])
    if number == 1 or number == 10:
        return '游戏四模块战斗形态'
    if number == 11:
        return '游戏人形战斗形态'
    return '金发蒙眼普通人偶'


video = load('video', 'references.json')
game = load('game', 'references.json')
images = load('images', 'manifest.json')
items = []
excluded = []
supplemental = []
seen = {}

for folder, records in [('video', video['references']), ('game', game['references']), ('images', images['items'])]:
    for original in records:
        file = 'references/' + folder + '/' + original['file']
        digest = hashlib.sha256((OUT / file).read_bytes()).hexdigest()
        number = int(original['id'][1:])
        if folder == 'video':
            category = '官方动画与预告原帧'
            form = '动画巨型本体与悬浮手'
            if number in [8, 9, 15, 19, 20, 21, 22, 23]:
                form = '金发蒙眼普通人偶'
            if number in [18, 25]:
                form = '战斗型机械人偶'
            subject = original['subject']
            observations = original['observations']
            authority = original['authority']
            limits = '原始视频透视与动画动作会改变可见比例。'
        elif folder == 'game':
            category = '玩家游戏原帧'
            form = '战斗型机械人偶' if number >= 11 else '游戏四模块战斗形态'
            subject = original['subject']
            observations = [original['notes']]
            authority = '玩家公开实机录像'
            limits = original['quality']
        else:
            category = '官网静态图' if number == 1 else ('社区模型展示' if 3 <= number <= 9 else '社区引用截图')
            form = image_form(original)
            subject = original['entity']
            observations = original['features']
            authority = original['kind']
            limits = original['limits']
        width, height = original.get('resolution', [original.get('width'), original.get('height')])
        item = {
            'id': original['id'], 'file': file,
            'thumbnail': 'references/' + folder + '/' + original['thumbnail'] if 'thumbnail' in original else file,
            'title': subject + ' · ' + original['angle'], 'category': category, 'form': form,
            'subject': subject, 'angle': original['angle'], 'observations': observations,
            'source_url': original['source_url'], 'source_title': original.get('source_title', authority),
            'publisher': original['publisher'], 'authority': authority,
            'time_seconds': original.get('time_seconds'), 'width': width, 'height': height,
            'sha256': digest, 'limits': limits, 'reviewed': True,
        }
        if item['id'] in ['I02', 'I12']:
            item['reason'] = '动画正面聚合巨人场景与官方原帧重合；社区合成、裁切与水印版本作为补充来源，不计入精选图片。'
            supplemental.append(item)
            continue
        if digest in seen:
            excluded.append({'id': item['id'], 'duplicate_of': seen[digest], 'reason': 'SHA-256相同'})
            continue
        seen[digest] = item['id']
        items.append(item)

form_order = ['动画巨型本体与悬浮手', '游戏四模块战斗形态', '游戏人形战斗形态', '战斗型机械人偶', '金发蒙眼普通人偶']
items.sort(key=lambda i: form_order.index(i['form']))

missing = [
    '动画巨型本体完整无遮挡侧立面。',
    '动画巨型本体背面表面近图；V16提供迎光背部轮廓。',
    '动画巨型本体全身无遮挡正交俯视及头顶正投影。',
    '悬浮手腕内部、肩背连接和腹腔内部截面。',
    '各手指标准正交图；已用掌心、掌背、斜侧与屈曲动作补充外观。',
]
findings = [
    'W11中央本体采用动画聚合巨人。可见形态为一对本体主臂，外围独立悬浮手各带短袖口。',
    '动画巨人具有极宽肩、窄腰、小型尖脊头盔、红眼、双叶上胸金纹和并列长盾腿甲。',
    '悬浮掌保留筒状腕口、花叶形掌根、分节金指及指间黑缝；部分关节可见短圆柱造型。',
    '游戏四模块围绕中轴球体展开，与动画站立巨人的构件连接分别记录。',
    '卵头金X面的战斗型机械人偶，与金发状甲、黑眼带、黑金裙的普通人偶分别记录。',
    '原作蓝灰金用于辨认形制；W11按负责人指定黑白金红进行工业材质映射。',
]
manifest = {
    'created_at': datetime.now(timezone.utc).isoformat(),
    'title': 'W11 支配人偶多角度参考图册', 'count': len(items),
    'counting': '按精选原图计数，图片数与独立观察方向数分开。联系图、扫描候选、缩略图、裁切和重复场景不重复计入。近似角度补充不同部位细节。',
    'category_counts': dict(Counter(i['category'] for i in items)),
    'form_counts': dict(Counter(i['form'] for i in items)),
    'references': items, 'supplemental': supplemental,
    'excluded_exact_duplicates': excluded,
    'excluded_source_candidates': {'video': video['excluded'], 'images': images['excluded']},
    'shape_findings': findings, 'missing_views': missing,
}
(OUT / '参考清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

page = '''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W11 支配人偶参考图册</title>
<style>
:root{color-scheme:dark;font-family:"Microsoft YaHei",sans-serif;background:#101113;color:#e9e5dc}*{box-sizing:border-box}body{margin:0}header,main{max-width:1500px;margin:auto;padding:24px}header{padding-bottom:8px}h1{font-size:27px;margin:0 0 12px}p{line-height:1.65;color:#bbb8ae}a{color:#dcc583;text-underline-offset:3px}.facts{border-left:3px solid #9d3a3a;padding-left:16px}.filters{display:flex;gap:10px;flex-wrap:wrap;position:sticky;top:0;padding:14px 0;background:#101113ee;z-index:2}select,input,button{font:inherit;background:#232426;color:#e9e5dc;border:1px solid #595348;border-radius:5px;padding:10px}input{flex:1;min-width:180px}button{cursor:pointer}#count{align-self:center;font-size:13px;color:#c5b37d}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}article{background:#1b1c1f;border:1px solid #3e3c38;border-radius:7px;overflow:hidden}.photo{display:block;width:100%;border:0;padding:0;border-radius:0;background:#090a0b}.photo img{width:100%;height:205px;object-fit:contain;display:block}.info{padding:15px}.tag{font-size:12px;color:#d1b87d}h2{font-size:16px;margin:9px 0;line-height:1.6}.info p{font-size:13px;margin:8px 0}.meta{color:#99958c;font-size:12px;line-height:1.6}.source{display:inline-block;margin-top:8px;font-size:13px}.notes{margin:28px 0;padding:18px;background:#1b1c1f;border:1px solid #4a4032;border-radius:7px}.notes h2{font-size:18px}.notes li{font-size:14px;color:#c5c1b6;line-height:1.8}details{margin-top:20px}.extras a{display:block;padding:8px 0}dialog{padding:0;max-width:95vw;width:1450px;max-height:96vh;background:#141517;color:#eee;border:1px solid #8b7544;border-radius:7px}dialog::backdrop{background:#000d}.modalbar{display:flex;justify-content:space-between;gap:14px;padding:12px;align-items:center}.modalbar strong{font-size:16px}.modalimg{width:100%;max-height:70vh;object-fit:contain;display:block;background:#070809}.modaltext{padding:0 18px 16px}.modaltext p{margin:7px 0;font-size:14px}.nav{display:flex;gap:7px}.nav button{padding:7px 11px}.empty{padding:35px;color:#aaa}@media(max-width:650px){header,main{padding:14px}.modalbar{align-items:flex-start}h1{font-size:22px}}
</style>
<header><h1>W11 支配人偶多角度参考图册</h1><p id="intro"></p><p class="facts">动画巨型本体、游戏战斗形态、卵头机械人偶、金发蒙眼普通人偶分别核对。原始图片保留原作配色，W11模型按黑白金红映射。</p><p><a href="index.html">返回方块模型预览</a> · <a href="参考清单.json">完整来源与SHA-256清单</a></p></header>
<main><div class="filters"><select id="category" aria-label="按来源筛选"><option value="">全部来源</option></select><select id="form" aria-label="按形态筛选"><option value="">全部形态</option></select><input id="search" placeholder="搜索头盔、掌心、背面、时间……" aria-label="搜索参考"><span id="count"></span></div><div id="grid" class="grid"></div><section class="notes"><h2>可见构件</h2><ul id="findings"></ul><h2>待补视面</h2><ul id="missing"></ul><details><summary>补充来源与去重说明</summary><p>社区合成图与引用裁切复用了已收录的动画正面巨人场景，保留来源，移出精选计数。相近观察方向的图片按各自新增细节记录。</p><div class="extras" id="extras"></div></details></section></main>
<dialog id="viewer"><div class="modalbar"><strong id="modalTitle"></strong><div class="nav"><button id="prev" aria-label="上一张">←</button><button id="next" aria-label="下一张">→</button><button id="close" aria-label="关闭">×</button></div></div><img class="modalimg" id="modalImage" alt=""><div class="modaltext" id="modalText"></div></dialog>
<script id="data" type="application/json">__DATA__</script>
<script>
const data=JSON.parse(document.querySelector('#data').textContent),$=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let filtered=data.references,active=0;
function timestamp(n){return n===null?'静态图':`${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`}
function meta(i){return `${i.publisher} · ${timestamp(i.time_seconds)} · ${i.width}×${i.height}`}
for(const [id,counts] of [['category',data.category_counts],['form',data.form_counts]])for(const [key,n]of Object.entries(counts))$("#"+id).insertAdjacentHTML('beforeend',`<option value="${esc(key)}">${esc(key)} (${n})</option>`);
$('#intro').textContent=`精选${data.count}张图片，其中动画巨型本体与悬浮手${data.form_counts['动画巨型本体与悬浮手']}张。${data.counting}`;
$('#findings').innerHTML=data.shape_findings.map(t=>`<li>${esc(t)}</li>`).join('');
$('#missing').innerHTML=data.missing_views.map(t=>`<li>${esc(t)}</li>`).join('');
$('#extras').innerHTML=data.supplemental.map(i=>`<a href="${esc(i.source_url)}" target="_blank" rel="noopener">${esc(i.id+' · '+i.publisher+' · '+i.title)}</a>`).join('');
function render(){const q=$('#search').value.trim().toLowerCase();filtered=data.references.filter(i=>(!$('#category').value||i.category===$('#category').value)&&(!$('#form').value||i.form===$('#form').value)&&JSON.stringify(i).toLowerCase().includes(q));$('#count').textContent=`${filtered.length} / ${data.count} 张`;$('#grid').innerHTML=filtered.map((i,n)=>`<article><button class="photo" data-index="${n}" aria-label="放大 ${esc(i.id+' '+i.title)}"><img src="${esc(i.thumbnail)}" alt="${esc(i.title)}" loading="lazy"></button><div class="info"><span class="tag">${esc(i.id+' · '+i.category)}</span><h2>${esc(i.title)}</h2><p>${esc(i.observations.join('；'))}</p><div class="meta">${esc(i.form)}<br>${esc(meta(i))}<br>${esc(i.limits)}</div><a class="source" href="${esc(i.source_url)}" target="_blank" rel="noopener">查看原始来源${i.time_seconds===null?'':'与时间'}</a></div></article>`).join('')||'<p class="empty">没有匹配的图片。</p>'}
function show(n){active=(n+filtered.length)%filtered.length;const i=filtered[active];$('#modalTitle').textContent=i.id+' · '+i.title;$('#modalImage').src=i.file;$('#modalImage').alt=i.title;$('#modalText').innerHTML=`<p>${esc(i.observations.join('；'))}</p><p>${esc(meta(i))}</p><p>${esc(i.authority+'；'+i.limits)}</p><a href="${esc(i.source_url)}" target="_blank" rel="noopener">${esc(i.source_title)} · 原始来源</a>`;if(!$('#viewer').open)$('#viewer').showModal()}
$('#grid').onclick=e=>{const b=e.target.closest('[data-index]');if(b)show(Number(b.dataset.index))};
for(const id of ['category','form','search'])$('#'+id).addEventListener('input',render);
$('#prev').onclick=()=>show(active-1);$('#next').onclick=()=>show(active+1);$('#close').onclick=()=>$('#viewer').close();
$('#viewer').onclick=e=>{if(e.target===$('#viewer'))$('#viewer').close()};document.addEventListener('keydown',e=>{if($('#viewer').open&&e.key==='ArrowLeft')show(active-1);if($('#viewer').open&&e.key==='ArrowRight')show(active+1)});render();
</script></html>'''
(OUT / '参考图册.html').write_text(page.replace('__DATA__', json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
print(json.dumps({'count': len(items), 'categories': manifest['category_counts'], 'forms': manifest['form_counts'], 'supplemental': len(supplemental), 'exact_duplicates': len(excluded)}, ensure_ascii=False))
