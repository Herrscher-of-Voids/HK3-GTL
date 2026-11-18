# -*- coding: utf-8 -*-
"""汇总保留功能件与流体重绘，提供原帧、动画和连续平铺评审。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LOG = ROOT / 'logs/fluid-texture-refresh-20261112'
OUT = ROOT / 'deliveries/功能件与流体材质_R258_20261112'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fluids = json.loads((LOG / 'fluid-manifest.json').read_text(encoding='utf-8'))
    functional = json.loads((ROOT / 'logs/texture-refresh-20261112/functional-manifest.json').read_text(encoding='utf-8'))
    names = json.loads((ASSETS / 'lang/zh_cn.json').read_text(encoding='utf-8-sig'))
    files = [row['path'] for row in fluids] + [row['path'] for row in functional]
    files += [row['path'] + '.mcmeta' for row in fluids]
    for rel in files:
        dest = OUT / 'after' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS / rel, dest)
    for row in fluids:
        if row['before_sha256']:
            rel = row['path']
            dest = OUT / 'before' / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(LOG / 'before' / rel, dest)
    widgets = []
    sprites = []
    for row in fluids:
        rel = row['path']
        if rel.endswith('_flow.png'):
            continue
        ident = Path(rel).stem.removeprefix('fluid.')
        label = names.get('material.hk3gtl.' + ident, '魂钢熔体' if ident == 'soulium' else ident)
        old = f'<figure><canvas data-sprite="before/{rel}"></canvas><figcaption>原材质</figcaption></figure>' if row['before_sha256'] else f'<figure class="empty">{"原用GT金属默认图" if ident == "soulium" else "原来缺少贴图"}</figure>'
        flow = rel.removesuffix('.png') + '_flow.png'
        meta = json.loads((ASSETS / (rel + '.mcmeta')).read_text(encoding='utf-8'))['animation']
        widgets.append(f'<article class="fluid" data-id="{ident}"><h2>{html.escape(label)}</h2><code>hk3gtl:{ident}</code><div class="images">{old}<figure><canvas data-sprite="after/{rel}" data-animate="true" data-time="{meta["frametime"]}" data-interpolate="{str(meta.get("interpolate", False)).lower()}"></canvas><figcaption>静止纹理</figcaption></figure><figure><canvas data-sprite="after/{flow}" data-animate="true" data-time="{meta["frametime"]}" data-interpolate="{str(meta.get("interpolate", False)).lower()}"></canvas><figcaption>流动纹理</figcaption></figure></div><details><summary>查看连续平铺与四帧</summary><div class="images"><figure><canvas data-sprite="after/{rel}" data-repeat="3" data-animate="true" data-time="{meta["frametime"]}"></canvas><figcaption>静止3×3</figcaption></figure><figure><canvas data-sprite="after/{flow}" data-repeat="3" data-animate="true" data-time="{meta["frametime"]}"></canvas><figcaption>流动3×3</figcaption></figure><figure><img class="strip" src="after/{rel}" alt="四帧原图"><figcaption>原帧序列</figcaption></figure></div></details></article>')
        sprites.append((ident, label, rel))
    cards = []
    for row in functional:
        rel = row['path']
        ident = Path(rel).stem
        cards.append(f'<article class="functional"><h2>{html.escape(names.get("item.hk3gtl." + ident, ident))}</h2><code>hk3gtl:{ident}</code><img class="item" src="after/{rel}" alt="保留的功能件"></article>')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HK3GTL · 功能件与流体材质 R258</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:26px;background:#101722;color:#e6edf7;font:15px system-ui}main{max-width:1450px;margin:auto}h1{font-size:27px}h2{font-size:17px;margin:0 0 9px}p{color:#b7c5d8;line-height:1.65}a{color:#a8c9fc}.notice{border-left:3px solid #b3a0d8;padding:10px 16px;background:#22283a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px;margin-top:18px}article{padding:18px;border-radius:10px;background:#192335;border:1px solid #34415a;overflow:hidden}article[hidden]{display:none}code{font-size:11px;color:#a9b9d5;overflow-wrap:anywhere}.images{display:flex;gap:12px;align-items:center;margin-top:18px}figure{flex:1;min-width:0;margin:0;text-align:center}.empty{font-size:12px;color:#a9bad3;padding:28px 5px;align-self:stretch;border:1px dashed #455571}canvas,img.item{width:100%;max-width:128px;aspect-ratio:1;image-rendering:pixelated;object-fit:contain;background:repeating-conic-gradient(#2c384b 0% 25%,#1e293b 0% 50%) 50%/14px 14px}figcaption{font-size:12px;color:#a9bad3;margin-top:7px}.strip{height:128px;width:32px;image-rendering:pixelated}details{margin-top:18px}summary{cursor:pointer;color:#b9c8df;font-size:13px}.item{display:block;margin:18px auto 0}nav{position:sticky;top:0;display:flex;gap:9px;flex-wrap:wrap;padding:13px 0;background:#101722ed;z-index:2}button,input{padding:10px;border:1px solid #465778;background:#22324c;color:#e2eaf8;border-radius:6px}button{cursor:pointer}button[aria-pressed=true]{background:#725390}input{flex:1;min-width:180px}</style><main>
<h1>保留7件功能物品 · 重画38种流体</h1><p class="notice">负责人要求删除的93个方块已从注册、模型及资源中移除，本页只包含保留的7件功能物品和本轮流体。活动实例与存档未修改。</p><p>38种液体／气体，各含静止与流动纹理，共76张。每张16×64，由四幅16×16帧组成；现有动画元数据保持。净化含能母液补齐缺图；魂钢熔体接入专用纹理。默认暂停，可逐帧查看或启动动画，平铺使用同一张实际资源。</p><p><a href="材质更新资源包_R258.zip">独立材质包</a> · <a href="manifest.json">本批资源清单</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a>。候选未安装，未进行游戏画面验收；方块删除及魂钢注册改动需使用对应候选JAR。</p>
<nav><button id="animation" aria-pressed="false">播放动画</button><button id="step">下一帧</button><button data-group="all">全部</button><button data-group="functional">保留功能件7</button><button data-group="fluid">流体38</button><input aria-label="搜索材质" type="search" placeholder="搜索名称或ID"></nav><div class="grid">'''
    page += ''.join(cards + widgets) + '''</div></main><script>
let running=false,frame=0,start=performance.now(),group='all';const query=document.querySelector('input'),sprites=[];for(const canvas of document.querySelectorAll('canvas')){const repeat=+(canvas.dataset.repeat||1);canvas.width=canvas.height=16*repeat;const image=new Image();const sprite={canvas,image,repeat};image.onload=()=>{sprites.push(sprite);draw(sprite,0)};image.src=canvas.dataset.sprite}function draw({canvas,image,repeat},elapsed){if(canvas.closest('article').hidden||canvas.closest('details:not([open])'))return;const ctx=canvas.getContext('2d'),animate=canvas.dataset.animate==='true',tick=elapsed/(+(canvas.dataset.time||5)*50),phase=running&&animate?tick:frame,a=Math.floor(phase)%4,b=(a+1)%4,weight=running&&canvas.dataset.interpolate==='true'?phase%1:0;ctx.clearRect(0,0,canvas.width,canvas.height);for(let y=0;y<repeat;y++)for(let x=0;x<repeat;x++){ctx.globalAlpha=1;ctx.drawImage(image,0,(animate?a:0)*16,16,16,x*16,y*16,16,16);if(weight){ctx.globalAlpha=weight;ctx.drawImage(image,0,b*16,16,16,x*16,y*16,16,16)}}ctx.globalAlpha=1}function redraw(t=performance.now()){sprites.forEach(s=>draw(s,t-start))}function loop(t){redraw(t);if(running)requestAnimationFrame(loop)}document.querySelector('#animation').onclick=e=>{running=!running;e.target.setAttribute('aria-pressed',running);e.target.textContent=running?'暂停动画':'播放动画';start=performance.now()-frame*250;if(running)requestAnimationFrame(loop);else redraw()};document.querySelector('#step').onclick=()=>{if(running)document.querySelector('#animation').click();frame=(frame+1)%4;redraw()};function filter(){for(const card of document.querySelectorAll('article'))card.hidden=(group!=='all'&&!card.classList.contains(group))||!card.textContent.toLowerCase().includes(query.value.toLowerCase().trim());redraw()}for(const b of document.querySelectorAll('[data-group]'))b.onclick=()=>{group=b.dataset.group;filter()};query.oninput=filter;for(const d of document.querySelectorAll('details'))d.ontoggle=()=>redraw();</script></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps({'functional': functional, 'fluids': fluids, 'deleted_blocks_receipt': 'logs/fluid-texture-refresh-20261112/deleted-block-assets.json'}, ensure_ascii=False, indent=2), encoding='utf-8')
    with zipfile.ZipFile(OUT / '材质更新资源包_R258.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr('pack.mcmeta', json.dumps({'pack': {'pack_format': 15, 'description': 'HK3GTL R258 · 7功能件与38种流体'}}, ensure_ascii=False))
        for rel in files:
            archive.write(ASSETS / rel, 'assets/hk3gtl/' + rel)
    selected = ['liquid_honkai_energy', 'crude_honkai_energy', 'honkai_coolant', 'hot_honkai_coolant', 'soulium', 'circuit_growth_medium', 'gaseous_honkai_energy', 'crystallization_residual_liquid']
    sheet = Image.new('RGB', (1152, 500), '#121b2b')
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    for i, ident in enumerate(selected):
        _, label, rel = next(s for s in sprites if s[0] == ident)
        x, y = i % 4 * 288, i // 4 * 250
        d.text((x + 12, y + 12), label, font=font, fill='#e6edf7')
        old = LOG / 'before' / rel
        for j, path in enumerate((old, ASSETS / rel)):
            if path.exists():
                tile = Image.open(path).convert('RGBA').crop((0, 0, 16, 16)).resize((112, 112), Image.Resampling.NEAREST)
                sheet.paste(tile, (x + 12 + j * 140, y + 53), tile)
        d.text((x + 37, y + 185), '原图' if old.exists() else '原用GT图', font=font, fill='#a8bad4')
        d.text((x + 177, y + 185), '重绘', font=font, fill='#a8bad4')
    sheet.save(OUT / '流体新旧对照.png')
    print(json.dumps({'fluid_textures': len(fluids), 'functional': len(functional), 'review': str(OUT / 'index.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
