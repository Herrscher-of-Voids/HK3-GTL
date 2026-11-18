# -*- coding: utf-8 -*-
"""整理全电压产业材质候选与评审页面。"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import shutil

from PIL import Image, ImageDraw, ImageFont
from package_0002_item_r12 import candidate, thumbnail

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'output/imagegen/industrial-0002-r16'
LOG = ROOT / 'logs/textures-industrial-handoff-0002-r16-20261116'
OUT = ROOT / 'deliveries/0002贴图材质_全电压产业_R16_20261116'

PAGE = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 · 全电压产业材质 R16</title>
<style>
:root{color-scheme:dark;font:15px/1.7 "Microsoft YaHei",system-ui;color:#eaf1f8;background:#101722}*{box-sizing:border-box}body{margin:0}main{max-width:1480px;margin:auto;padding:32px}h1{font-size:34px;margin:5px 0 12px}h2{font-size:18px;margin:12px 0 3px}p{color:#adbed1}a{color:#cfbbfc}header{padding-bottom:22px;border-bottom:1px solid #344254}.eyebrow{color:#be9fe8;font-size:12px;letter-spacing:.12em}.notice{background:#202a39;border-left:3px solid #be9fe8;padding:12px 18px;margin:20px 0}nav,.toolbar,.pager{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:20px 0}button,input,select{font:inherit;color:inherit;background:#1c2738;border:1px solid #44526a;border-radius:5px;padding:7px 12px}button{cursor:pointer}button[aria-pressed=true]{background:#423153;border-color:#be9fe8}input{flex:1;min-width:220px}button:disabled{opacity:.35;cursor:default}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}.card{border:1px solid #344254;background:#182333;border-radius:9px;overflow:hidden;min-width:0}.art{display:block;background:#202b3b;aspect-ratio:1}.art img{width:100%;height:100%;object-fit:contain;image-rendering:pixelated}.body{padding:14px}code{font:11px/1.7 Consolas,monospace;overflow-wrap:anywhere;color:#91a9c1}.body p,.body details{font-size:13px}.body p{min-height:42px}.links{display:flex;gap:14px;margin-top:12px;font-size:12px}.badge{font-size:11px;border:1px solid #66537c;padding:2px 5px;border-radius:3px;color:#d6c2ed}.overview{display:block;width:100%;height:auto}.pager{justify-content:center}summary{cursor:pointer;color:#ceb9ed}footer{color:#93a7bf;margin-top:32px}dialog{max-width:92vw;background:#141d2a;color:inherit;border:1px solid #596078;border-radius:10px}dialog::backdrop{background:#000a}dialog img{display:block;max-width:min(78vw,900px);max-height:76vh;object-fit:contain;background:repeating-conic-gradient(#e2e7eb 0 25%,#c5ced5 0 50%) 0/20px 20px}dialog button{float:right;margin-bottom:8px}@media(max-width:1000px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:680px){main{padding:16px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.body{padding:9px}h1{font-size:25px}h2{font-size:15px}.links{gap:8px;flex-wrap:wrap}}
</style><main><header><span class="eyebrow">HK3GTL / 0002 / R16</span><h1>全电压产业材质候选</h1>
<p>128种物品 · 28种流体。逐项依据0003交接的制造、用途、接口与工艺状态设计。</p>
<div class="notice">待负责人评审。物品保留API原画布与透明PNG；流体采用原生64像素、4帧、6tick、无插值。交接所列64×64物品规格与本对话此前保留大尺寸原图的决定分别记录。</div>
<nav><a href="../0003_全剩余电压工业链与材质交接_20261116/handoff.html">0003工艺交接</a><a href="manifest.json">完整材质记录</a><a href="item-overview-1.png">物品总览1</a><a href="item-overview-2.png">物品总览2</a><a href="fluid-overview.png">流体总览</a><a href="../../logs/beta5-completion-audit-20261030/index.html">固定报告</a></nav>
</header><div class="toolbar"><button data-kind="all" aria-pressed="true">全部</button><button data-kind="item" aria-pressed="false">物品</button><button data-kind="fluid" aria-pressed="false">流体</button><select id="tier" aria-label="首用电压"><option value="all">全部电压</option></select><input id="search" placeholder="搜索中文名称、ID或工艺用途" aria-label="搜索材质"><span id="count"></span></div><div id="cards" class="grid"></div><div class="pager"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></div><footer>对话0002 · 贴图材质 · 01a1d68a-a994-7ac0-a48a-54c0f98fd54e<br>原图、透明候选、提示词及来源配方均保留在本交付目录。</footer></main><dialog id="viewer"><button id="close">关闭</button><h2 id="view-title"></h2><img id="view-image" alt="材质原图"></dialog>
<script type="application/json" id="data">DATA_JSON</script><script>
const records=JSON.parse(document.querySelector('#data').textContent),cards=document.querySelector('#cards'),search=document.querySelector('#search'),tier=document.querySelector('#tier'),viewer=document.querySelector('#viewer');let kind='all',page=0;const perPage=24;
for(const value of [...new Set(records.map(x=>x.firstTier))].sort((a,b)=>a-b)){const option=document.createElement('option');option.value=value;option.textContent='Tier'+value;tier.append(option)}
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function draw(){const q=search.value.trim().toLowerCase(),rows=records.filter(r=>(kind==='all'||r.kind===kind)&&(tier.value==='all'||String(r.firstTier)===tier.value)&&[r.name,r.id,r.designZh,...r.facts].join(' ').toLowerCase().includes(q)),pages=Math.max(1,Math.ceil(rows.length/perPage));page=Math.min(page,pages-1);cards.innerHTML=rows.slice(page*perPage,(page+1)*perPage).map(r=>`<article class="card"><a href="${esc(r.image)}" class="art" data-view="${esc(r.id)}"><img src="${esc(r.preview)}" loading="lazy" alt="${esc(r.name)}"></a><div class="body"><span class="badge">${r.kind==='item'?'物品':'流体'} · Tier${r.firstTier}</span><h2>${esc(r.name)}</h2><code>hk3gtl:${esc(r.id)}</code><p>${esc(r.designZh)}</p><details><summary>制造、用途与资源路径</summary>${r.facts.map(f=>'<p>'+esc(f)+'</p>').join('')}${r.targets.map(p=>'<code>'+esc(p)+'</code><br>').join('')}<p>${esc(r.resolutionNote)}</p></details><div class="links"><a href="${esc(r.image)}" target="_blank">透明PNG</a>${r.original?'<a href="'+esc(r.original)+'" target="_blank">API原图</a>':''}${r.promptFile?'<a href="'+esc(r.promptFile)+'" target="_blank">提示词</a>':''}</div></div></article>`).join('');document.querySelector('#count').textContent=rows.length+'项';document.querySelector('#page').textContent=(page+1)+' / '+pages;document.querySelector('#prev').disabled=page===0;document.querySelector('#next').disabled=page===pages-1}
for(const b of document.querySelectorAll('[data-kind]'))b.onclick=()=>{kind=b.dataset.kind;page=0;for(const x of document.querySelectorAll('[data-kind]'))x.setAttribute('aria-pressed',String(x===b));draw()};search.oninput=tier.onchange=()=>{page=0;draw()};document.querySelector('#prev').onclick=()=>{page--;draw()};document.querySelector('#next').onclick=()=>{page++;draw()};cards.onclick=e=>{const link=e.target.closest('[data-view]');if(link){e.preventDefault();const r=records.find(x=>x.id===link.dataset.view);document.querySelector('#view-title').textContent=r.name;document.querySelector('#view-image').src=r.image;viewer.showModal()}};document.querySelector('#close').onclick=()=>viewer.close();draw();
</script></html>'''


def main():
    contexts = []
    for group in ('items-a', 'items-b', 'fluids'):
        contexts.extend(json.loads((LOG / f'{group}-context.json').read_text(encoding='utf-8')))
    byid = {r['id'].split(':')[1]: r for r in contexts}
    specs = []
    for group in ('a', 'b'):
        specs.extend(json.loads((RAW / f'specs-{group}.json').read_text(encoding='utf-8-sig')))
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    sheets = [Image.new('RGB', (1408, 2060), '#172333') for _ in range(2)]
    records = []
    for index, spec in enumerate(specs):
        identity = spec['id'].split(':')[-1]
        context = byid[identity]
        folder = OUT / 'items' / identity
        folder.mkdir(parents=True, exist_ok=True)
        original = RAW / f'{identity}.png'
        image = candidate(spec, original, folder / 'texture.png')
        preview = thumbnail(image, 160)
        preview.save(folder / 'preview.png')
        shutil.copy2(original, folder / 'api-original.png')
        shutil.copy2(RAW / f'{identity}.txt', folder / 'prompt.txt')
        for target in context['targets']:
            path = OUT / 'candidate-assets' / Path(target).relative_to('src/main/resources')
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == '.png':
                shutil.copy2(folder / 'texture.png', path)
            else:
                model = {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'hk3gtl:item/{identity}'}}
                path.write_text(json.dumps(model, indent=2) + '\n', encoding='utf-8')
        sheet = sheets[index // 64]
        local = index % 64
        x, y = local % 8 * 176 + 8, local // 8 * 250 + 48
        sheet.paste(preview, (x, y))
        draw = ImageDraw.Draw(sheet)
        name = spec['name']
        for line in range((len(name) + 10) // 11):
            draw.text((x, y + 164 + line * 21), name[line * 11:(line + 1) * 11], font=font, fill='#eaf1f8')
        records.append({**spec, 'id': identity, 'firstTier': context['firstTier'],
                        'targets': context['targets'], 'image': f'items/{identity}/texture.png',
                        'preview': f'items/{identity}/preview.png', 'original': f'items/{identity}/api-original.png',
                        'promptFile': f'items/{identity}/prompt.txt', 'size': list(image.size), 'mode': image.mode,
                        'sha256': sha256((folder / 'texture.png').read_bytes()).hexdigest(),
                        'originalSha256': sha256(original.read_bytes()).hexdigest(),
                        'resolutionNote': f'API实际{image.width}×{image.height}，原画布与透明候选同尺寸。',
                        'artApproved': False, 'sourceApplied': False})
    for number, sheet in enumerate(sheets, 1):
        ImageDraw.Draw(sheet).text((12, 12), f'0002 · R16 · 物品候选 {number}/2 · 待评审', font=font, fill='#eaf1f8')
        sheet.save(OUT / f'item-overview-{number}.png')
    fluids = json.loads((OUT / 'fluid-manifest.json').read_text(encoding='utf-8'))
    for fluid in fluids['records']:
        identity = fluid['id'].split(':')[-1]
        context = byid[identity]
        still = fluid['textures'][0]
        records.append({**fluid, 'id': identity, 'firstTier': context['firstTier'],
                        'targets': context['targets'], 'image': still['image'],
                        'resolutionNote': '静止单帧64×64；流动单帧128×128，4帧、6tick、无插值。',
                        'artApproved': False, 'sourceApplied': False})
    manifest = {'revision': 'R16', 'conversation': '0002',
                'conversationId': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'updatedAt': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(timespec='seconds'),
                'itemCount': len(specs), 'fluidCount': len(fluids['records']), 'records': records,
                'sourceHandoff': 'deliveries/0003_全剩余电压工业链与材质交接_20261116/texture-handoff.json',
                'inputFiles': json.loads((LOG / 'intake.json').read_text(encoding='utf-8'))['inputFiles'],
                'itemAdapter': 'tools/invoke_image_relay.ps1 -Mode Generate -RelayResponse',
                'originalCanvasPreserved': True, 'referenceImagesUploaded': 0,
                'artApproved': False, 'sourceApplied': False, 'jarBuilt': False, 'installed': False}
    serialized = json.dumps(manifest, ensure_ascii=False, indent=2)
    (OUT / 'manifest.json').write_text(serialized + '\n', encoding='utf-8')
    (LOG / 'manifest.json').write_text(serialized + '\n', encoding='utf-8')
    page = PAGE.replace('DATA_JSON', json.dumps(records, ensure_ascii=False).replace('</', '<\\/'))
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps({'items': len(specs), 'fluids': len(fluids['records']), 'gallery': str(OUT / 'index.html')}))


if __name__ == '__main__':
    main()
