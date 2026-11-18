# -*- coding: utf-8 -*-
"""四阶同轴采集塔的独立入口、同尺度立面与实际材质投影。"""
import base64
import html
import io
import json
from PIL import Image, ImageDraw, ImageFont
from i01_i08_v7_gallery import draw_sheet


def orthographic(data, materials, out):
    w, h, d = data['size']
    textures = {}
    for m in materials:
        for face in ('north', 'up'):
            textures[m['state'], face] = Image.open(io.BytesIO(base64.b64decode(
                m['faces'][face].split(',', 1)[1]))).convert('RGBA').resize((16, 16), Image.Resampling.NEAREST)
    front = Image.new('RGBA', (w*16, h*16), '#131a28')
    plan = Image.new('RGBA', (w*16, d*16), '#131a28')
    for b in sorted(data['blocks'], key=lambda b: b['pos'][2], reverse=True):
        x, y, _ = b['pos']
        front.alpha_composite(textures[b['state'], 'north'], (x*16, (h-1-y)*16))
    for b in sorted(data['blocks'], key=lambda b: b['pos'][1]):
        x, _, z = b['pos']
        plan.alpha_composite(textures[b['state'], 'up'], (x*16, z*16))
    front.convert('RGB').save(out/'正面立面.png')
    plan.convert('RGB').save(out/'俯视布局.png')


def comparison(out, entries, plan=False):
    picture = Image.new('RGB', (1920, 690 if plan else 790), '#101622')
    draw = ImageDraw.Draw(picture)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    heading = 'I01 · 四阶同轴布局 / 同尺度俯视' if plan else 'I01 · 四阶正交生长 / 同尺度立面'
    draw.text((35, 25), heading, font=font, fill='#edf1f6')
    source = '俯视布局.png' if plan else '正面立面.png'
    for j, e in enumerate(entries):
        left = 25+j*475
        draw.rounded_rectangle((left, 90, left+455, picture.height-30), 12,
                               fill='#192233', outline='#394158')
        im = Image.open(out/e['key']/source).convert('RGB')
        im = im.resize((round(im.width*7/16), round(im.height*7/16)), Image.Resampling.NEAREST)
        bottom = picture.height-135
        top = 135+(371-im.height)//2 if plan else bottom-im.height
        picture.paste(im, (left+(455-im.width)//2, top))
        draw.text((left+20, picture.height-108), e['title'], font=small, fill='#edf1f6')
        w, h, d = e['size']
        draw.text((left+20, picture.height-70), f'{w} × {d} × {h} · {e["blocks"]:,} 方块',
                  font=small, fill='#a9bbcf')
    picture.save(out/('四阶俯视.png' if plan else '四阶正面.png'))


def gallery(out, entries):
    cards = []
    for e in entries:
        w, h, d = e['size']
        key = e['key']
        cards.append(f'''<article><a href="{key}/三维评审.html" class="picture"><img src="{key}/等轴预览.png" alt="{html.escape(e['title'])}"></a>
<div class="copy"><small>{key.upper()} / {w} × {d} × {h}</small><h2>{html.escape(e['title'])}</h2><p>{html.escape(e['description'])}</p>
<nav><a class="button" href="{key}/三维评审.html">旋转与剖切 ↗</a><a href="{key}/{e['name']}.schem">Schematic</a><a href="{key}/{e['name']}.nbt">NBT</a></nav></div></article>''')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01 · 四阶正交采集塔</title><style>
*{box-sizing:border-box}body{margin:0;background:#101622;color:#edf1f6;font:15px/1.8 'Microsoft YaHei',sans-serif}header,footer,.compare{max-width:1580px;margin:auto;padding:36px 32px}header small{color:#a7c2e7;letter-spacing:3px}h1{font-size:40px;margin:12px 0;line-height:1.35}header p{color:#b7c4d5;max-width:1050px}a{color:#b7cfed;text-decoration:none}a:hover{color:white}.note{background:#202b40;border-left:3px solid #93b6db;padding:12px 20px}.grid{max-width:1580px;margin:auto;padding:0 32px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{border:1px solid #394158;border-radius:14px;overflow:hidden;background:#192233;display:flex;flex-direction:column}.picture{height:420px;background:#131a28;display:block}.picture img{width:100%;height:100%;object-fit:contain}.copy{padding:24px;flex:1;display:flex;flex-direction:column}h2{font-size:23px;margin:8px 0 12px}.copy small{color:#9fb2cd;letter-spacing:2px}.copy p{color:#b7c4d5;flex:1;margin:0 0 24px}nav{display:flex;gap:22px;align-items:center;flex-wrap:wrap}.button{padding:9px 14px;border:1px solid #94b4df;border-radius:6px}.compare img{width:100%;display:block;border-radius:10px;margin:20px 0}.compare p,footer{color:#a9bbcf}footer a{margin-right:24px}@media(max-width:850px){.grid{grid-template-columns:1fr}h1{font-size:30px}.picture{height:350px}}
</style></head><body><header><small>HK3GTL / I01 / V8</small><h1>同一座塔，向四面与天空生长。</h1><p>中央采集核心始终在原位。液态冷凝塔、左右固态副塔、四向气态集气架和外围能量冠架，沿南北东西轴线逐阶展开。</p><p class="note">四阶逐次保留已有方块，主控与核心在世界中的位置固定。结构文件包含不同阶段的粘贴偏移；使用同一主控锚点升级。外观候选，游戏内成型与运行待验收。</p><p>点开每阶可旋转、俯视、查看正面和剖切。尺寸为宽 × 深 × 高。</p></header><main class="grid">'''+''.join(cards)+'''</main><section class="compare"><h2>同尺度查看四阶演进</h2><p>立面比较向上的层次，俯视比较围绕同一核心的扩建布局。</p><a href="四阶正面.png"><img src="四阶正面.png" alt="四阶同尺度正面立面"></a><a href="四阶俯视.png"><img src="四阶俯视.png" alt="四阶同尺度俯视布局"></a></section><footer><a href="I01四阶演进.png">等轴总览</a><a href="I01_V8_四阶结构与预览.zip">下载结构与预览包</a><a href="http://127.0.0.1:8367/index.html">I02–I08 预览</a><span>2026-10-14 · V8 外观候选</span></footer></body></html>'''
    (out/'index.html').write_text(page, encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    draw_sheet(out, entries, 'I01四阶演进.png', 'I01 · 四阶正交采集塔', 2)
    comparison(out, entries)
    comparison(out, entries, True)
