import hashlib
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'deliveries/0002贴图材质_工艺重构_R3_20261114'
REVIEW = ROOT / 'logs/textures-redraw-0002-v2-20261114/art-review.json'
PROCESS = ROOT / 'logs/textures-redraw-0002-r3-20261114/process/design-process.json'
CHAT_ID = '01a1d68a-a994-7ac0-a48a-54c0f98fd54e'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def collect_designs():
    records = {}
    for name, category in (('world', '世界泡与研究'), ('engineering', '高维工程材料')):
        source = DELIVERY / f'design-{name}.json'
        for item in read_json(source)['items']:
            records[item['id']] = {
                'name': item['name'], 'category': category,
                'code_facts': [item['function_process_facts']], 'project_contract': [],
                'art_interpretation': [{'label': '形制与材质推导', 'text': item['new_visual_interpretation']}],
                'evidence': [{'path': p, 'locator': item['text_evidence_locator']} for p in item['text_evidence_paths']],
                'design_source': source.relative_to(ROOT).as_posix(),
            }
    for item in read_json(PROCESS):
        evidence = item['text_evidence']
        records[item['id']] = {
            'name': item['name'], 'category': '魂钢与纳米工艺',
            'code_facts': [item['function']], 'project_contract': [],
            'art_interpretation': [{'label': '形制与材质推导', 'text': item['design_inference']}],
            'evidence': [{'path': evidence['path'], 'locator': evidence['recipe']}],
            'design_source': PROCESS.relative_to(ROOT).as_posix(),
        }
    source = DELIVERY / 'design-keys.json'
    for item in read_json(source)['items']:
        records[item['id']] = {
            'name': item['name'], 'category': '神之键与封装',
            'code_facts': item['actual_function']['code_facts'],
            'project_contract': item['actual_function']['project_contract'],
            'art_interpretation': [{'label': k, 'text': v} for k, v in zip(
                ('形制', '材质', '装配', '美术选择与边界'), item['visual_derivation'].values())],
            'evidence': [{'path': e['path'], 'locator': e['selector']} for e in item['evidence']],
            'design_source': source.relative_to(ROOT).as_posix(),
        }
    groups = {
        '空间观测与作业': ['spatial_probe', 'industrial_work_drone', 'worn_resource_probe', 'worn_work_drone', 'drone_disassembly_scrap'],
        '样本与结晶': ['analyzed_honkai_sample', 'honkai_reference_sample', 'honkai_crystal_seed', 'directional_crystallization_matrix', 'concentrated_honkai_impurity', 'separation_residue', 'honkai_energy_crystal'],
        '燃料与回收': ['fuel_matrix', 'fuel_blending_residue', 'fuel_encapsulation_part', 'rejected_fuel_rod', 'depleted_dense_honkai_fuel_rod', 'broken_honkai_fuel_rod', 'broken_dense_honkai_fuel_rod', 'recovered_fuel_casing_material', 'inactive_fuel_residue', 'dense_honkai_fuel_rod'],
        '舰船与档案': ['imitation_hyperion_blueprint', 'hyperion_keel_segment', 'hyperion_bridge_module', 'ship_engineering_archive'],
    }
    for category, ids in groups.items():
        for ident in ids:
            records[ident]['category'] = category
    return records


def contact_sheet(items):
    cell_w, cell_h, columns, header = 184, 184, 8, 78
    sheet = Image.new('RGB', (cell_w * columns, header + cell_h * math.ceil(len(items) / columns)), '#17232b')
    d = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 12)
    d.text((20, 10), f'0002 · 贴图材质 R3 · {len(items)} 张工艺重构候选', font=title, fill='#f1e7cb')
    d.text((20, 47), f'64×64 原生像素  |  未批准 · 未构建 · 未安装  |  对话 ID {CHAT_ID}', font=small, fill='#bac8cc')
    for n, item in enumerate(items):
        x, y = (n % columns) * cell_w, header + (n // columns) * cell_h
        for cy in range(8):
            for cx in range(8):
                color = '#42535b' if (cx + cy) % 2 else '#35464e'
                d.rectangle((x + 28 + cx * 16, y + cy * 16, x + 43 + cx * 16, y + 15 + cy * 16), fill=color)
        with Image.open(DELIVERY / item['image']) as im:
            tile = im.resize((128, 128), Image.Resampling.NEAREST)
            sheet.paste(tile, (x + 28, y), tile)
        lines = [item['name'][i:i + 11] for i in range(0, len(item['name']), 11)]
        label = f'{n + 1:02d} ' + '\n   '.join(lines)
        d.multiline_text((x + 10, y + 136), label, font=font, fill='#edf0e8', spacing=3)
    sheet.save(DELIVERY / 'contact-sheet.png')


PAGE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · R3贴图工艺重构 · 59张新图</title>
<style>
:root{color-scheme:dark;--bg:#111b22;--panel:#192832;--line:#344751;--text:#e9eee9;--muted:#adbdc2;--gold:#e4c17d;--blue:#8ecbd2}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}button,input{font:inherit}button,a,input{outline-offset:4px}a{color:var(--blue);text-underline-offset:3px}button{cursor:pointer}main{max-width:1520px;margin:auto;padding:32px 28px 50px}.eyebrow{color:var(--gold);letter-spacing:.1em;font-size:13px}h1{font-size:clamp(28px,4vw,44px);line-height:1.2;letter-spacing:-.02em;margin:12px 0}h2{font-size:23px;line-height:1.35;margin:0 0 8px}h3{font-size:16px;margin:24px 0 10px;color:var(--gold)}p{margin:9px 0}.sub{color:var(--muted)}.chat{font:12px/1.6 ui-monospace,Consolas,monospace;color:var(--muted);overflow-wrap:anywhere}.status{display:inline-flex;align-items:center;padding:5px 11px;border:1px solid #7b6542;border-radius:5px;color:#f0d9aa;font-size:13px;background:#3a3022}.hero{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}.links{display:flex;flex-wrap:wrap;gap:16px;font-size:13px;margin-top:17px}.stats{display:flex;gap:20px;white-space:nowrap;padding-top:8px}.stats strong{display:block;font-size:32px;font-weight:600;line-height:1.2}.stats span{font-size:12px;color:var(--muted)}.tools{position:sticky;top:0;z-index:2;margin:28px -4px 20px;padding:12px 4px;background:var(--bg);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.searchrow{display:flex;gap:15px;align-items:center}input{width:100%;max-width:670px;background:#22343f;border:1px solid #4b626d;border-radius:6px;padding:11px 14px;color:var(--text)}input::placeholder{color:#bac6ca}.count{font-size:13px;white-space:nowrap;color:var(--muted)}.categories{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}.chip{border:1px solid var(--line);background:transparent;color:var(--muted);padding:5px 11px;border-radius:5px;font-size:12px}.chip[aria-pressed=true]{border-color:var(--gold);background:#3a3327;color:#f4ddb0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}.card{display:flex;flex-direction:column;align-items:stretch;text-align:left;background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:7px;padding:15px}.card:hover{border-color:#bfa773;background:#20323c}.card h2{font-size:16px;margin:13px 0 4px}.card .id{font:11px/1.5 ui-monospace,Consolas,monospace;color:#a2b5bd;overflow-wrap:anywhere;min-height:33px}.card .category{color:#cbb888;font-size:11px;margin-top:10px}.preview{display:flex;align-items:center;justify-content:center;height:150px}.checker{background-color:#344750;background-image:linear-gradient(45deg,#42565f 25%,transparent 25%),linear-gradient(-45deg,#42565f 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#42565f 75%),linear-gradient(-45deg,transparent 75%,#42565f 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}.pixel{image-rendering:pixelated;image-rendering:crisp-edges;object-fit:contain}.card img{height:128px;width:128px}.empty{padding:60px;text-align:center;color:var(--muted)}details{margin-top:28px;border-top:1px solid var(--line);padding:18px 0;color:var(--muted)}summary{cursor:pointer;color:var(--text)}.retained{columns:3;column-gap:32px;padding-left:20px;font-size:13px}.retained li{break-inside:avoid;margin:7px 0}footer{margin-top:20px;color:var(--muted);font-size:12px}dialog{border:1px solid #536b76;border-radius:10px;background:#15232c;color:var(--text);width:min(1050px,calc(100vw - 32px));max-height:calc(100vh - 36px);padding:26px}dialog::backdrop{background:#050b11d9}.modalhead{display:flex;align-items:start;justify-content:space-between;gap:15px}.close{border:1px solid #56717d;background:#243b47;color:var(--text);border-radius:5px;padding:6px 12px}.modalbody{display:grid;grid-template-columns:360px 1fr;gap:30px;margin-top:20px}.views{display:flex;flex-wrap:wrap;align-items:start;gap:16px;position:sticky;top:0}.views figure{margin:0}.views figcaption{font-size:12px;color:var(--muted);margin-top:8px}.native{display:flex;align-items:center;justify-content:center;width:80px;height:80px}.native img{width:64px;height:64px}.large{width:256px;height:256px}.large img{width:256px;height:256px}.source{font-size:11px;overflow-wrap:anywhere;line-height:1.55}.detail ul{padding-left:19px}.detail li{margin-bottom:7px}.art{padding-left:14px;border-left:2px solid #977b47}.art b{color:#d7bc83;font-size:13px}dialog .links{margin-top:15px}.legend{display:flex;gap:18px;flex-wrap:wrap;margin-top:15px;font-size:12px;color:var(--muted)}.legend b{color:var(--gold);font-weight:500}
@media(max-width:850px){main{padding:22px 16px}.hero{display:block}.stats{margin-top:20px}.modalbody{grid-template-columns:1fr}.views{position:static}.retained{columns:2}}@media(max-width:470px){.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.card{padding:10px}.card img{width:112px;height:112px}.card h2{font-size:14px}.card .id{font-size:10px}.searchrow{align-items:start;flex-direction:column;gap:7px}.retained{columns:1}dialog{padding:17px}.stats{gap:16px}.views{gap:12px}.large,.large img{width:256px;height:256px}}
</style></head><body><main>
<header><div class="eyebrow">HK3GTL · 对话2 · 编号0002 · 贴图材质</div><div class="hero"><div><h1>R3 · 从工艺重构实物</h1><p class="sub">59张新图，以名称、实际用途与当前工艺为设计起点。</p><p><span class="status">候选未批准 · 未构建 · 未安装</span></p><p class="chat">对话 ID：01a1d68a-a994-7ac0-a48a-54c0f98fd54e</p></div><div class="stats"><div><strong>59</strong><span>本轮新图</span></div><div><strong>64×64</strong><span>原生透明PNG</span></div><div><strong>20</strong><span>认可项文字保留</span></div></div></div>
<div class="links"><a href="contact-sheet.png" target="_blank">查看59张总览图</a><a href="manifest.json" target="_blank">查看清单与设计依据</a></div><div class="legend"><span><b>代码事实</b>：当前注册、配方与调用</span><span><b>项目约定</b>：文本明确的用途及限制</span><span><b>美术解释</b>：形制、材质与装配推导</span></div></header>
<section class="tools" aria-label="筛选贴图"><div class="searchrow"><input id="search" type="search" placeholder="搜索名称、ID、功能、工艺或材料" aria-label="搜索名称、ID、功能、工艺或材料"><span class="count" id="count" aria-live="polite"></span></div><nav class="categories" id="categories" aria-label="贴图分类"></nav></section>
<section class="grid" id="grid" aria-label="59张本轮新图"></section><p class="empty" id="empty" hidden>没有匹配的贴图，请调整关键词或分类。</p>
<details><summary>已认可20项：沿用原文件，仅列文字保留说明</summary><p class="sub">这20项不参与本轮重绘，本页不读取或展示其图片。</p><ul class="retained" id="retained"></ul></details>
<footer>0002 · R3 · 2026-11-14。本页只展示本轮贴图候选及设计依据；外观等待负责人评审，未构建、未安装，也不代表游戏验收。</footer>
</main><dialog id="detail"><div class="modalhead"><div><h2 id="detail-name"></h2><div class="chat" id="detail-id"></div></div><button type="button" class="close" id="close">关闭 ×</button></div><div class="modalbody"><div><div class="views"><figure><div class="checker native"><img id="native" class="pixel" alt="原生尺寸贴图"></div><figcaption>原生 · 64×64</figcaption></figure><figure><div class="checker large"><img id="large" class="pixel" alt="四倍像素放大贴图"></div><figcaption>4倍 · 256×256 · 最近邻</figcaption></figure></div><div class="links"><a id="raw" target="_blank">打开PNG原图</a></div><p class="source sub" id="hash"></p></div><div class="detail" id="detail-text"></div></div></dialog>
<script id="manifest-data" type="application/json">__DATA__</script>
<script>
const data=JSON.parse(document.getElementById('manifest-data').textContent),grid=document.getElementById('grid'),search=document.getElementById('search'),dialog=document.getElementById('detail');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let category='全部';
const categories=['全部',...new Set(data.items.map(x=>x.category))];
document.getElementById('categories').innerHTML=categories.map(c=>`<button type="button" class="chip" data-category="${esc(c)}" aria-pressed="${c===category}">${esc(c)} · ${c==='全部'?data.items.length:data.items.filter(x=>x.category===c).length}</button>`).join('');
function render(){const term=search.value.trim().toLocaleLowerCase();const items=data.items.filter(x=>(category==='全部'||x.category===category)&&JSON.stringify(x).toLocaleLowerCase().includes(term));grid.innerHTML=items.map(x=>`<button type="button" class="card" data-id="${x.id}" aria-label="查看${esc(x.name)}原生与四倍像素图"><span class="preview checker"><img src="${x.image}" alt="${esc(x.name)}" class="pixel" loading="lazy" width="128" height="128"></span><h2>${esc(x.name)}</h2><span class="id">${x.id}</span><span class="category">${esc(x.category)} · 点击查看设计</span></button>`).join('');document.getElementById('count').textContent=`显示 ${items.length} / ${data.items.length} 张`;document.getElementById('empty').hidden=items.length>0;}
function list(title,items){return `<h3>${title}</h3><ul>${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;}
function openItem(id){const x=data.items.find(x=>x.id===id);document.getElementById('detail-name').textContent=x.name;document.getElementById('detail-id').textContent=`${x.id} · ${x.category}`;for(const id of ['native','large'])document.getElementById(id).src=x.image;document.getElementById('raw').href=x.image;document.getElementById('hash').textContent=`SHA256 ${x.sha256}`;document.getElementById('detail-text').innerHTML=list('代码事实与当前工艺',x.code_facts)+(x.project_contract.length?list('项目文本约定',x.project_contract):'')+`<h3>美术解释 · 本轮形制推导</h3><div class="art">${x.art_interpretation.map(a=>`<p><b>${esc(a.label)}</b><br>${esc(a.text)}</p>`).join('')}</div><h3>文本证据</h3><ul class="source">${x.evidence.map(e=>`<li><a href="../../${encodeURI(e.path)}" target="_blank">${esc(e.path)}</a><br>${esc(e.locator)}</li>`).join('')}</ul>`;dialog.showModal();dialog.scrollTop=0;}
search.addEventListener('input',render);document.getElementById('categories').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;category=b.dataset.category;for(const chip of document.querySelectorAll('.chip'))chip.setAttribute('aria-pressed',String(chip===b));render();});grid.addEventListener('click',e=>{const b=e.target.closest('[data-id]');if(b)openItem(b.dataset.id);});document.getElementById('close').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});document.getElementById('retained').innerHTML=data.retained_items.map(x=>`<li>${esc(x.name)}<br><span class="chat">${x.id}</span></li>`).join('');render();
</script></body></html>'''


def publish():
    review = read_json(REVIEW)
    for ident in review['pending_redraw_ids']:
        filename = f'{ident}.png'
        shutil.copyfile(ROOT / 'src/main/resources/assets/hk3gtl/textures/item' / filename,
                        DELIVERY / 'textures/item' / filename)
    shutil.copyfile(PROCESS, DELIVERY / 'design-process.json')
    designs = collect_designs()
    items = []
    for ident in review['pending_redraw_ids']:
        path = DELIVERY / f'textures/item/{ident}.png'
        with Image.open(path) as im:
            size = list(im.size)
        items.append({'id': ident, **designs[ident], 'image': path.relative_to(DELIVERY).as_posix(),
                      'native_size': size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {
        'revision': 'R3', 'date': '2026-11-14', 'conversation_number': '0002', 'conversation_id': CHAT_ID,
        'art_approved': False, 'jar_built': False, 'installed': False, 'game_tested': False,
        'reference_policy': '只读取本轮R3新图；以名称、功能、当前配方和工艺重新推导。',
        'review_source': REVIEW.relative_to(ROOT).as_posix(), 'new_image_count': len(items),
        'retained_items': [{'id': x['id'], 'name': x['name'], 'note': '已认可，沿用原文件；本页不读取原图。'} for x in review['accepted_assets']],
        'items': items,
    }
    (DELIVERY / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')
    (DELIVERY / 'index.html').write_text(PAGE.replace('__DATA__', payload), encoding='utf-8')
    contact_sheet(items)
    return {'new_images': len(items), 'retained_text_entries': len(manifest['retained_items']), 'page': str(DELIVERY / 'index.html')}


if __name__ == '__main__':
    print(json.dumps(publish(), ensure_ascii=False))
