# -*- coding: utf-8 -*-
"""保留R12原画布，导出透明候选与独立评审页，不改游戏资源。"""
from datetime import datetime
from hashlib import sha256
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'output/imagegen/items-0002-r12'
OUT = ROOT / 'deliveries/0002贴图材质_指定物品与研究计算机_R12_20261115'
LOG = ROOT / 'logs/textures-redraw-0002-r12-20261115'
FONT = 'C:/Windows/Fonts/msyh.ttc'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def candidate(spec, source, target):
    image = Image.open(source).convert('RGBA')
    rgb = np.asarray(image.convert('RGB')).astype(np.int16)
    if spec['kind'] == 'item':
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        if spec.get('chromaKey', 'green') == 'magenta':
            keyed = (r > 180) & (b > 180) & (g < 100)
            contaminated = (r > g + 8) & (b > g + 8)
        else:
            keyed = ((g > 180) & (g > r + 70) & (g > b + 45)) | ((g > r + 65) & (g > b + 65))
            contaminated = (g > r + 8) & (g > b + 8)
        border = np.asarray(Image.fromarray(keyed).filter(ImageFilter.MaxFilter(9)))
        alpha = np.asarray(image.getchannel('A')).copy()
        alpha[keyed | (border & contaminated)] = 0
        image.putalpha(Image.fromarray(alpha))
    image.save(target)
    return image


def thumbnail(image, side=210):
    preview = image.copy()
    preview.thumbnail((side, side), Image.Resampling.LANCZOS)
    tile = Image.new('RGB', (side, side), '#e2e7eb')
    draw = ImageDraw.Draw(tile)
    for y in range(0, side, 15):
        for x in range(0, side, 15):
            if (x // 15 + y // 15) % 2:
                draw.rectangle((x, y, x + 14, y + 14), fill='#c5ced5')
    tile.paste(preview, ((side-preview.width)//2, (side-preview.height)//2), preview)
    return tile


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    specs = read(RAW / 'prompts.json')
    records, cards, item_previews, faces = [], [], [], {}
    for spec in specs:
        identity = spec['generationId']
        folder = OUT / identity
        folder.mkdir(exist_ok=True)
        raw, png = RAW / (identity + '.png'), folder / 'texture.png'
        image = candidate(spec, raw, png)
        shutil.copy2(raw, folder / 'api-original.png')
        (folder / 'prompt.txt').write_text(spec['promptEn'], encoding='utf-8')
        thumb = thumbnail(image)
        thumb.save(folder / 'preview.png')
        bindings = []
        for path in spec['sourcePaths']:
            target = OUT / 'candidate-assets' / Path(path).relative_to('src/main/resources')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png, target)
            bindings.append({'sourcePath': path, 'candidatePath': target.relative_to(OUT).as_posix(),
                             'originalSha256': digest(ROOT / path), 'candidateSha256': digest(png)})
        record = {**spec, 'image': identity+'/texture.png', 'original': identity+'/api-original.png',
                  'preview': identity+'/preview.png', 'size': list(image.size), 'mode': image.mode,
                  'sha256': digest(png), 'originalApiSha256': digest(raw), 'targets': bindings,
                  'artApproved': False, 'sourceApplied': False,
                  'processing': '原画布与RGB不变；物品仅增加色键透明通道，方块面保持不透明。'}
        records.append(record)
        if spec['kind'] == 'block-face':
            faces[spec['face']] = record['image']
        else:
            item_previews.append((spec['name'], thumb))
        facts = ''.join('<li>'+escape(x)+'</li>' for x in spec['facts'])
        paths = ''.join('<code>'+escape(x)+'</code>' for x in spec['sourcePaths'])
        search = escape(' '.join([spec['name'], identity, *spec['sourcePaths']]), quote=True)
        cards.append(f'<article id="{identity}" data-kind="{spec["kind"]}" data-search="{search}"><h2>{escape(spec["name"])}</h2>'
                     f'<p class="muted">{escape(spec["category"])}</p>'
                     f'<a href="{record["image"]}" target="_blank"><img loading="lazy" src="{record["image"]}" alt="{escape(spec["name"])}"></a>'
                     f'<p>{image.width}×{image.height} RGBA · 待评审</p>'
                     f'<p>{escape(spec["designZh"])}</p><details><summary>用途、工艺与路径</summary><ul>{facts}</ul>{paths}'
                     f'<p>{escape(spec["usageNote"])}</p></details><p><a href="{record["image"]}">候选PNG</a> · '
                     f'<a href="{record["original"]}">API原图</a> · <a href="{identity}/prompt.txt">提示词</a></p></article>')
    columns, cell, step = 7, 226, 258
    sheet = Image.new('RGB', (columns*cell, 88+((len(item_previews)+columns-1)//columns)*step), '#edf2f5')
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 14), '0002 · 指定物品重绘 R12 · 44种新造型 / 46条物品路径', font=ImageFont.truetype(FONT, 25), fill='#253945')
    font = ImageFont.truetype(FONT, 13)
    for index, (name, thumb) in enumerate(item_previews):
        x, y = index % columns*cell+8, 76+index//columns*step
        sheet.paste(thumb, (x,y))
        draw.text((x,y+214), name, font=font, fill='#253945')
    sheet.save(OUT/'overview.png')
    manifest = {'revision':'R12','conversation':'0002','conversationId':'01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'updatedAt':datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(timespec='seconds'),
                'itemPathCount':46,'computerFaceCount':4,'candidatePathCount':sum(len(r['targets']) for r in records),
                'newApiImageCount':len(records),'uniqueItemDesignCount':len(item_previews),
                'apiModelAlias':'gpt-image-2.6-sunburst','requestedApiSize':[1024,1024],
                'actualApiSizes':sorted({tuple(r['size']) for r in records}),
                'apiAdapter':'tools/invoke_image_relay.ps1 -Mode Generate -RelayResponse',
                'originalCanvasPreserved':True,'resized':False,'oldTexturesUsedAsReference':False,
                'referenceImagesUploaded':0,'artApproved':False,'sourceApplied':False,
                'jarBuilt':False,'installed':False,'gameTested':False,
                'computerSharedModelWarning':'研究点计算机与AE天枢共用原方块模型；本轮仅候选，未覆盖共享材质。',
                'records':records}
    data = json.dumps(manifest,ensure_ascii=False,indent=2)
    (OUT/'manifest.json').write_text(data,encoding='utf-8')
    (LOG/'manifest.json').write_text(data,encoding='utf-8')
    cube = ''.join('<div class="face '+face+'" style="background-image:url('+faces[texture]+')"></div>' for face,texture in [('front','front'),('back','back'),('right','side'),('left','side'),('top','top'),('bottom','side')])
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · 指定物品与研究计算机 R12</title><style>
body{margin:0;color:#e7edf1;background:#131c24;font:15px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1450px;padding:28px;margin:auto}h1{font-size:29px;margin:0 0 10px}h2{font-size:19px}p{margin:8px 0}a{color:#8ad8d1}code{display:block;font-size:11px;overflow-wrap:anywhere}.muted,summary{color:#acc0cd}nav{display:flex;flex-wrap:wrap;gap:18px;margin:20px 0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(285px,1fr));gap:16px}article{padding:17px;border:1px solid #354854;border-radius:5px;background:#1c2933;min-width:0}article img{display:block;width:100%;aspect-ratio:1;object-fit:contain;background:repeating-conic-gradient(#d8e0e5 0 25%,#b4c1cb 0 50%) 0/24px 24px}article h2{min-height:30px;margin-top:0}article ul{padding-left:20px;font-size:13px}article>p{font-size:13px}button,input{font:inherit;color:inherit;background:#293f4d;border:1px solid #517185;padding:7px 12px;border-radius:4px}button{cursor:pointer}.hero{display:flex;gap:32px;flex-wrap:wrap;align-items:center;border:1px solid #354854;padding:20px;margin:24px 0}.scene{perspective:1200px;width:400px;height:390px;display:grid;place-items:center;overflow:hidden}.cube{width:220px;height:220px;position:relative;transform-style:preserve-3d;transform:rotateX(-22deg) rotateY(-33deg)}.face{position:absolute;width:220px;height:220px;background-size:100% 100%;backface-visibility:hidden;image-rendering:pixelated}.front{transform:translateZ(110px)}.back{transform:rotateY(180deg) translateZ(110px)}.right{transform:rotateY(90deg) translateZ(110px)}.left{transform:rotateY(-90deg) translateZ(110px)}.top{transform:rotateX(90deg) translateZ(110px)}.bottom{transform:rotateX(-90deg) translateZ(110px)}.controls{max-width:680px}.overview{width:100%;height:auto}details{font-size:13px}summary{cursor:pointer}footer{margin-top:25px;color:#acc0cd}input[type=search]{width:min(440px,100%)}@media(max-width:600px){main{padding:16px}.scene{width:100%;height:340px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}article{padding:10px}article h2{font-size:15px}article p{font-size:12px}}
</style><main><h1>0002 · 指定物品与研究计算机 R12</h1>
<p>46条物品贴图路径＋研究点计算机4面，共50条目标路径。两组重名魂钢坯分别共用同族新设计；实际独立生图48张。</p>
<p>本轮均为独立待审候选，原游戏资源与既有批准保持。物品保留API原画布并增加透明通道；计算机为画满的不透明面纹理。未构建或安装JAR。</p>
<nav><a href="#computer">先看研究点计算机</a><a href="#items">物品新稿</a><a href="overview.png">物品总览大图</a><a href="manifest.json">完整事实与路径</a></nav>
<section class="hero" id="computer"><div class="scene"><div class="cube" id="cube">CUBE_FACES</div></div><div class="controls"><h2>MAX研究点计算机 · 四面映射预览</h2><p>实际新面纹理组成立方体；这是离线预览，不是游戏截图。</p><p><button id="turn">转90°</button> <button id="reset">正面视角</button></p><p>俯仰 <input id="pitch" type="range" min="-75" max="75" value="-22"></p><p>前面为运算屏与插拔卡槽；后面电源和数据接口；侧面散热片；顶部加强筋与格栅。</p><p class="muted">原模型也由AE天枢共用。本轮只展示候选，后续采用时须明确共享或拆分范围。</p></div></section>
<img class="overview" src="overview.png" alt="44种物品新稿总览"><h2 id="items">逐项候选</h2><p><input type="search" id="search" placeholder="按名称、ID或路径筛选"></p><div class="grid">CARDS</div><footer>对话0002 · ID 01a1d68a-a994-7ac0-a48a-54c0f98fd54e · 不缩成64／16像素；只有浏览器与总览缩略显示。<br>两神之键按原作参考形制独立转译；未确认背面细纹不冒充精确复刻。</footer>
<script>let yaw=-33;const cube=document.getElementById('cube'),pitch=document.getElementById('pitch');function rotate(){cube.style.transform='rotateX('+pitch.value+'deg) rotateY('+yaw+'deg)'}document.getElementById('turn').onclick=()=>{yaw-=90;rotate()};document.getElementById('reset').onclick=()=>{yaw=-33;pitch.value=-22;rotate()};pitch.oninput=rotate;document.getElementById('search').oninput=e=>{const q=e.target.value.trim().toLowerCase();document.querySelectorAll('article').forEach(x=>x.hidden=!x.dataset.search.toLowerCase().includes(q))};</script></main></html>'''
    (OUT/'index.html').write_text(page.replace('CUBE_FACES',cube).replace('CARDS',''.join(cards)),encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='records'},ensure_ascii=True))


if __name__ == '__main__':
    main()
