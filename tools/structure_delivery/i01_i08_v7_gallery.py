# -*- coding: utf-8 -*-
"""八台新稿与I01四阶升级的浏览入口、真实纹理联系图。"""
import html
import json
import math
from PIL import Image, ImageDraw, ImageFont


def gallery(out, entries):
    cards = []
    for e in entries:
        key = e['key']
        w, h, d = e['size']
        cards.append(f'''<article><a class="picture" href="{key}/三维评审.html"><img src="{key}/等轴预览.png" alt="{html.escape(e['title'])}"></a>
<div class="copy"><small>{key.upper()} · {w} × {d} × {h} 方块</small><h2>{html.escape(e['title'])}</h2><p>{html.escape(e['description'])}</p>
<nav><a class="button" href="{key}/三维评审.html">旋转与剖切 ↗</a><a href="{key}/{e['name']}.schem">Schematic</a><a href="{key}/{e['name']}.nbt">NBT</a></nav></div></article>''')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I01–I08 · 新工业轮廓</title><style>
*{box-sizing:border-box}body{margin:0;background:#101622;color:#edf1f6;font:15px/1.75 'Microsoft YaHei',sans-serif}header,footer{max-width:1600px;margin:auto;padding:42px 32px 30px}header small{color:#b2a6d2;letter-spacing:3px}h1{font-size:40px;line-height:1.25;margin:14px 0}header p{max-width:1050px;color:#aebbd0;margin:10px 0}a{color:#c5b9e4;text-decoration:none}a:hover{color:white}main{max-width:1600px;margin:auto;padding:0 32px 24px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#192233;border:1px solid #394158;border-radius:14px;overflow:hidden;display:flex;flex-direction:column}.picture{display:block;height:400px;background:#131a28}.picture img{width:100%;height:100%;object-fit:contain}.copy{padding:24px;display:flex;flex-direction:column;flex:1}.copy small{color:#a9bbcf;letter-spacing:1px}h2{font-size:23px;margin:9px 0 12px}.copy p{color:#b7c4d5;flex:1;margin:0 0 22px}nav{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.button{padding:9px 14px;border:1px solid #a293c4;border-radius:6px}footer{color:#98a9c0;padding-top:12px}footer a{margin-right:25px}.chain{border:1px solid #665b80;padding:16px 20px;border-radius:8px;max-width:1050px;background:#24243a}@media(max-width:850px){main{grid-template-columns:1fr}.picture{height:330px}h1{font-size:30px}}
</style></head><body><header><small>HK3GTL / INDUSTRIAL STUDIES / V7</small><h1>前八台，重新长出自己的形状。</h1>
<p>从四阶采集群落，到光谱扇阵、卧式离心机、稳定叉塔、滤芯再生塔、开放调配床、标定光路与悬置棱晶。设备的功能关系决定轮廓，管路、夹架和散热结构成为建筑的一部分。</p>
<p class="chain">I01 单独展示四阶：每次升级保留上一阶全部非主控方块，再向新区域扩建。其余七台各有独立结构。</p>
<p>点开机器可旋转、缩放和逐层剖切。尺寸为宽 × 深 × 高。I09–I13 已确认版本保留。</p></header><main>'''+''.join(cards)+'''</main><footer><a href="八机总览.png">八机总览图</a><a href="I01四阶演进.png">I01四阶演进图</a><a href="I01-I08_V7_结构与预览.zip">结构与预览包</a><span>2026-10-14 · V7 外观候选</span></footer></body></html>'''
    (out/'index.html').write_text(page, encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    main = [e for e in entries if e['key'] == 'i01-4' or not e['key'].startswith('i01-')]
    draw_sheet(out, main, '八机总览.png', 'I01–I08 · 八种工业轮廓', 2)
    chain = [e for e in entries if e['key'].startswith('i01-')]
    draw_sheet(out, chain, 'I01四阶演进.png', 'I01 · 四阶无拆除扩建', 2)


def draw_sheet(out, entries, filename, heading, columns):
    rows = max(1, math.ceil(len(entries)/columns))
    result = Image.new('RGB', (1800, 120+rows*560), '#101622')
    draw = ImageDraw.Draw(result)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 44)
    label = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
    draw.text((40, 30), heading, font=title, fill='#edf1f6')
    for j, e in enumerate(entries):
        x, y = 40+j%columns*870, 115+j//columns*560
        draw.rounded_rectangle((x, y, x+830, y+530), radius=12, fill='#192233', outline='#394158')
        im = Image.open(out/e['key']/'等轴预览.png').convert('RGB')
        im.thumbnail((800, 405), Image.Resampling.LANCZOS)
        result.paste(im, (x+(830-im.width)//2, y+12+(405-im.height)//2))
        draw.text((x+22, y+429), f"{e['key'].upper()}  {e['title']}", font=label, fill='#edf1f6')
        w, h, d = e['size']
        draw.text((x+22, y+475), f'{w} × {d} × {h}  |  {e["blocks"]:,} 方块', font=small, fill='#a9bbcf')
    result.save(out/filename)
