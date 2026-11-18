# -*- coding: utf-8 -*-
"""将新绘流体原图接为全尺寸平铺动画，并生成评审页。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo
import json
import os
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'output/imagegen/fluids-0002-r11'
LOG = ROOT / 'logs/textures-fluid-redraw-0002-r11-20261115'
OUT = ROOT / 'deliveries/0002贴图材质_全流体重绘_R11_20261115'
TEXTURES = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/fluids'
FONT = 'C:/Windows/Fonts/msyh.ttc'
GASES = {'gaseous_honkai_energy': (22, 142), 'soulium_protective_gas': (12, 104),
         'spent_soulium_process_gas': (30, 160), 'hot_soulium_exhaust': (24, 152)}
CLEAR = {'clarified_honkai_mother_liquor', 'honkai_separation_medium', 'honkai_analysis_reagent',
         'soulium_process_solvent', 'honkai_coolant', 'stable_transport_medium', 'copper_electrolyte',
         'secondary_heat_transfer_medium', 'warm_secondary_heat_transfer_medium',
         'hot_secondary_heat_transfer_medium', 'phase_modulation_medium', 'bubble_confinement_medium'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def link(path):
    return quote(os.path.relpath(path, OUT).replace('\\', '/'), safe='/.:')


def periodic(image):
    pixels = np.asarray(image.convert('RGB'), dtype=np.float32).copy()
    band = image.width // 16
    weight = (1 + np.cos(np.linspace(0, np.pi, band))) / 2
    for axis in (1, 0):
        for i, blend in enumerate(weight):
            a, b = [slice(None)] * 3, [slice(None)] * 3
            a[axis], b[axis] = i, -1-i
            av, bv = pixels[tuple(a)].copy(), pixels[tuple(b)].copy()
            middle = (av + bv) / 2
            pixels[tuple(a)] = av * (1-blend) + middle * blend
            pixels[tuple(b)] = bv * (1-blend) + middle * blend
    return pixels.clip(0, 255).astype(np.uint8)


def package(row):
    ident = row['id']
    folder = OUT / ident
    folder.mkdir(parents=True, exist_ok=True)
    raw = ROOT / row['apiOriginal']
    shutil.copy2(raw, folder / 'api-original.png')
    shutil.copy2(ROOT / row['promptFile'], folder / 'prompt.txt')
    with Image.open(raw) as original:
        width, height = original.size
        rgb = periodic(original)
    alpha = np.full((height, width, 1), 232 if ident in CLEAR else 255, np.uint8)
    if ident in GASES:
        low, high = GASES[ident]
        density = rgb.astype(np.float32).mean(axis=2)
        density = (density-density.min()) / (density.max()-density.min())
        alpha[:, :, 0] = (low + density * (high-low)).astype(np.uint8)
    rgba = np.concatenate([rgb, alpha], axis=2)
    Image.fromarray(rgba).save(folder / 'tile.png')
    textures = []
    for flow in (False, True):
        source = rgba[:, (np.arange(width) * 2) % width] if flow else rgba
        offsets = [(0, 0), (0, height//4), (0, height//2), (0, 3*height//4)] if flow else [(0, 0), (width//80, 0), (width//80, height//80), (0, height//80)]
        frames = [Image.fromarray(np.roll(source, (y, x), axis=(0, 1))) for x, y in offsets]
        strip = Image.new('RGBA', (width, height * len(frames)))
        for i, frame in enumerate(frames):
            strip.paste(frame, (0, i * height))
        path = TEXTURES / ('fluid.' + ident + ('_flow' if flow else '') + '.png')
        meta = path.with_suffix('.png.mcmeta')
        before = {}
        for target in (path, meta):
            if target.exists():
                backup = LOG / 'before' / target.relative_to(ROOT)
                backup.parent.mkdir(parents=True, exist_ok=True)
                if not backup.exists():
                    shutil.copy2(target, backup)
                before[target.suffix] = digest(backup)
        strip.save(path)
        animation = {'width': width, 'height': height, 'frametime': 5, 'interpolate': True, 'frames': [0, 1, 2, 3]}
        meta.write_text(json.dumps({'animation': animation}, separators=(',', ':')), encoding='utf-8')
        stem = 'flow' if flow else 'still'
        previews = [f.resize((192, 192), Image.Resampling.NEAREST) for f in frames]
        previews[0].save(folder / (stem + '.png'))
        previews[0].save(folder / (stem + '.apng'), format='PNG', save_all=True, append_images=previews[1:], duration=250, loop=0)
        tile = Image.new('RGBA', (384, 384))
        for y in (0, 192):
            for x in (0, 192):
                tile.paste(previews[0], (x, y))
        tile.save(folder / (stem + '-tiled.png'))
        textures.append({'kind': 'flow' if flow else 'still', 'path': path.relative_to(ROOT).as_posix(),
                         'resource': 'hk3gtl:block/fluids/' + path.stem, 'size': list(strip.size),
                         'frameSize': [width, height], 'frameCount': len(frames), 'mode': strip.mode,
                         'sha256': digest(path), 'beforeSha256': before.get('.png'),
                         'metadataPath': meta.relative_to(ROOT).as_posix(), 'animation': animation,
                         'alphaRange': [int(alpha.min()), int(alpha.max())],
                         'preview': f'{ident}/{stem}.apng', 'tiledPreview': f'{ident}/{stem}-tiled.png'})
    return {**row, 'apiOriginal': (folder / 'api-original.png').relative_to(ROOT).as_posix(),
            'apiOriginalSha256': digest(raw), 'actualApiSize': [width, height], 'textures': textures}


PAGE = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · 全流体重绘 R11</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#111820;color:#e5eef5;font:15px/1.6 "Microsoft YaHei",sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:29px;margin:0 0 12px}h2{font-size:18px;margin:0}a{color:#98d8ed}code{font:12px Consolas,monospace;overflow-wrap:anywhere}p{margin:10px 0;color:#b6c6d1}.notice{border-left:3px solid #b6a1e2;padding:12px 16px;background:#202b3a}nav{position:sticky;top:0;z-index:2;background:#111820ed;display:flex;gap:10px;padding:15px 0;flex-wrap:wrap}input,select,button{font:inherit;color:inherit;background:#202d3b;border:1px solid #43566c;padding:9px;border-radius:4px}input{flex:1;min-width:220px}button{cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}article{border:1px solid #35465b;background:#1b2735;padding:16px;border-radius:6px}article[hidden]{display:none}.pair{display:flex;gap:12px;margin:14px 0}figure{margin:0;flex:1;min-width:0}img{width:100%;image-rendering:pixelated;background:repeating-conic-gradient(#a8b4c0 0 25%,#d8e0e6 0 50%) 50%/16px 16px}figcaption{font-size:12px;color:#b6c6d1;text-align:center}details{font-size:13px;margin-top:12px}summary{cursor:pointer;color:#c0afe6}.tile{max-width:384px}.tag{font-size:12px;color:#94c8d2}footer{margin-top:28px;color:#9cabb8;font-size:12px}li{margin:6px 0}</style><main>
<h1>全流体重绘 · R11</h1><p class="notice">上一轮55项删除已撤销，旧贴图与原引用恢复保留。本轮重绘47种流体，包含新增9种工业介质；共94张静止／流动动画PNG，接入源码，APPROVAL_STATUS。</p>
<p>每种独立调用绑定生图API，全尺寸原图与提示词均保留；不参考旧图。动画使用新图像素完成边缘接缝、流向与四帧循环，未缩成64或16像素。气体按新图密度配置透明度，液体按工艺选用透明度。此页缩略图仅用于预览。</p>
<p>API实际尺寸：API_SIZES；每张动画高为单帧的4倍。预览APNG保留透明度，但不模拟Minecraft帧间插值；可打开实际PNG及mcmeta核对。APPROVAL_NOTICE；未构建JAR、未安装、未启动游戏。</p>
<p><a href="overview.png">47种总览</a> · <a href="manifest.json">完整清单与提示词</a> · <a href="INVENTORY_LINK">全库材质清单</a> · <a href="REPORT_LINK">固定进度报告</a></p>
<nav><input id="search" type="search" placeholder="搜索名称、ID或工艺" aria-label="搜索流体"><select id="family" aria-label="工艺分类"><option value="">全部工艺</option>FAMILIES</select><button id="play">暂停预览</button><span id="count">47种流体</span></nav><section class="grid">CARDS</section>
<footer>0002贴图材质 · 对话ID 01a1d68a-a994-7ac0-a48a-54c0f98fd54e · UPDATED<br>47种内含4种气体、43种液体。负载与失活崩坏能分离介质目前仅有注册，未找到实际配方；外观按名称设计，不宣称已完成工艺闭环。</footer>
<script>let playing=true;const cards=[...document.querySelectorAll('article')],search=document.getElementById('search'),family=document.getElementById('family');function filter(){const q=search.value.trim().toLowerCase();cards.forEach(c=>c.hidden=!(c.textContent.toLowerCase().includes(q)&&(!family.value||c.dataset.family===family.value)));document.getElementById('count').textContent=cards.filter(c=>!c.hidden).length+'种流体'}search.oninput=filter;family.onchange=filter;document.getElementById('play').onclick=e=>{playing=!playing;document.querySelectorAll('img[data-animation]').forEach(i=>i.src=playing?i.dataset.animation:i.dataset.still);e.target.textContent=playing?'暂停预览':'播放预览'};</script></main></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    rows = read(INPUT / 'prompts.json')
    scope = read(LOG / 'fluid-scope.json')
    approval = read(LOG / 'art-approval.json')
    approval_status = '已认可采用' if approval['artApproved'] else '待美术评审'
    approval_notice = '美术已认可并采用' if approval['artApproved'] else '美术未批准'
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(package, rows))
    facts = {r['id']: r for r in scope['fluids']}
    for row in records:
        row['codeFacts'] = facts[row['id']]
        row['artApproved'] = approval['artApproved']
    now = datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(timespec='seconds')
    manifest = {'revision': 'R11', 'conversation': '0002', 'conversationId': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'updatedAt': now, 'fluidCount': len(records), 'textureCount': sum(len(r['textures']) for r in records),
                'originalsPreserved': True, 'originalImagesResized': False, 'runtimeFramesResized': False,
                'referenceImagesUploaded': 0, 'apiModelAlias': 'gpt-image-2.6-sunburst',
                'animationMethod': '新绘原图的窄边缘混合、UV重排与位移四帧；未程序生成液面纹样。',
                'artApproved': approval['artApproved'], 'approvalDecision': approval['approvalDecision'],
                'approvedAt': approval['approvedAt'], 'sourceApplied': True, 'jarBuilt': False, 'installed': False, 'gameTested': False,
                'restorationReceipt': 'logs/textures-fluid-redraw-0002-r11-20261115/restoration.json', 'records': records}
    for path in (OUT / 'manifest.json', LOG / 'manifest.json'):
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    cards = []
    for row in records:
        ident = row['id']
        figures = []
        for texture in row['textures']:
            kind = texture['kind']
            label = '静止' if kind == 'still' else '流动'
            figures.append(f'<figure><a href="{link(ROOT / texture["path"])}"><img loading="lazy" src="{ident}/{kind}.apng" data-animation="{ident}/{kind}.apng" data-still="{ident}/{kind}.png" alt="{escape(row["name"])}{label}动画"></a><figcaption>{label} · {texture["frameSize"][0]}² ×4帧</figcaption></figure>')
        paths = ''.join('<p><code>' + escape(t['path']) + '</code></p>' for t in row['textures'])
        cards.append(f'<article data-family="{escape(row["family"])}"><h2>{escape(row["name"])}</h2><code>hk3gtl:{ident}</code><p class="tag">{escape(row["family"])} · {approval_status}</p><div class="pair">{"".join(figures)}</div><p>{escape(row["design"])}</p><p><a href="{ident}/api-original.png">API完整原图</a> · <a href="{ident}/prompt.txt">本项提示词</a></p><details><summary>查看平铺与材质路径</summary><div class="pair"><figure><img loading="lazy" src="{ident}/still-tiled.png" alt="静止2×2平铺"><figcaption>静止2×2平铺</figcaption></figure><figure><img loading="lazy" src="{ident}/flow-tiled.png" alt="流动2×2平铺"><figcaption>流动2×2平铺</figcaption></figure></div>{paths}</details></article>')
    sizes = '、'.join(f'{w}×{h}' for w, h in sorted({tuple(r['actualApiSize']) for r in records}))
    families = ''.join(f'<option>{escape(f)}</option>' for f in dict.fromkeys(r['family'] for r in records))
    page = PAGE.replace('CARDS', ''.join(cards)).replace('FAMILIES', families).replace('API_SIZES', sizes).replace('UPDATED', now)
    page = page.replace('APPROVAL_STATUS', approval_status).replace('APPROVAL_NOTICE', approval_notice)
    page = page.replace('INVENTORY_LINK', link(ROOT / 'deliveries/0002贴图材质_全库材质清单_R10采用_20261115/index.html')).replace('REPORT_LINK', link(ROOT / 'logs/beta5-completion-audit-20261030/index.html'))
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    sheet = Image.new('RGB', (1400, 70 + ((len(records)+5)//6)*213), '#17212d')
    draw = ImageDraw.Draw(sheet)
    title, font = ImageFont.truetype(FONT, 28), ImageFont.truetype(FONT, 14)
    draw.text((20, 14), '0002 · R11全流体重绘 · 47种 · 约1K原图保留', font=title, fill='#e5eef5')
    for i, row in enumerate(records):
        x, y = 14 + i % 6 * 233, 65 + i // 6 * 213
        with Image.open(OUT / row['id'] / 'still.png') as preview:
            sheet.paste(preview, (x+18, y), preview)
        draw.text((x, y+192), row['name'], font=font, fill='#d8e2ed')
    sheet.save(OUT / 'overview.png')
    print(json.dumps({'fluids': len(records), 'textures': manifest['textureCount'], 'sizes': sizes, 'review': str(OUT / 'index.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
