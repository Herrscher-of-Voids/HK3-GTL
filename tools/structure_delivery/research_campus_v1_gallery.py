# -*- coding: utf-8 -*-
"""研究所五阶的建筑演进、真实纹理立面和浏览入口。"""
import html
import json
from PIL import Image, ImageDraw, ImageFont
from i01_i08_v7_gallery import draw_sheet


def comparison(out, entries, plan=False):
    picture = Image.new('RGB', (2400, 900), '#101b24')
    draw = ImageDraw.Draw(picture)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    draw.text((35, 25), '五阶研究所 · 同尺度'+('俯视布局' if plan else '正面立面'), font=font, fill='#edf4f2')
    source = '俯视布局.png' if plan else '正面立面.png'
    for j, entry in enumerate(entries):
        left = 25+j*475
        draw.rounded_rectangle((left, 90, left+455, 870), 12, fill='#192a33', outline='#3c5661')
        im = Image.open(out/entry['key']/source).convert('RGB')
        im = im.resize((round(im.width*3.25/16), round(im.height*3.25/16)), Image.Resampling.NEAREST)
        top = 180+(430-im.height)//2 if plan else 680-im.height
        picture.paste(im, (left+(455-im.width)//2, top))
        draw.text((left+20, 728), entry['key'].upper()+' · '+entry['title'], font=small, fill='#edf4f2')
        w, h, d = entry['size']
        draw.text((left+20, 780), f'{w} × {d} × {h} · {entry["blocks"]:,} 方块', font=small, fill='#a8c1c7')
    picture.save(out/('五阶俯视.png' if plan else '五阶正面.png'))


def gallery(out, entries):
    cards = []
    for entry in entries:
        key = entry['key']
        w, h, d = entry['size']
        inherited = entry['upgrade_contract']['preserved_non_controller_blocks']
        label = '最初的实验楼' if not inherited else f'保留前阶 {inherited:,} 个非主控方块'
        cards.append(f'''<article><a class="picture" href="{key}/三维评审.html"><img src="{key}/等轴预览.png" alt="{entry['title']}"></a><div class="copy"><small>{key.upper()} · {w} × {d} × {h}</small><h2>{entry['title']}</h2><p>{html.escape(entry['description'])}</p><p class="inherit">{label}</p><nav><a class="button" href="{key}/三维评审.html">进入院区 · 旋转与剖切 ↗</a><a href="{key}/{entry['name']}.schem">Schematic</a><a href="{key}/{entry['name']}.nbt">NBT</a></nav></div></article>''')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五阶研究所 · 从实验楼到文明院区</title><style>
*{box-sizing:border-box}body{margin:0;background:#101b24;color:#edf4f2;font:15px/1.85 'Microsoft YaHei',sans-serif}header,footer,.compare{max-width:1580px;margin:auto;padding:38px 32px}header small{color:#a3d3ca;letter-spacing:3px}h1{font-size:40px;margin:12px 0;line-height:1.4}header p{color:#b3c6cc;max-width:1100px}a{color:#b4dfd6;text-decoration:none}a:hover{color:white}.note{border-left:3px solid #8bbdb1;background:#20343d;padding:14px 20px}.grid{max-width:1580px;margin:auto;padding:0 32px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#192a33;border:1px solid #3c5661;border-radius:12px;overflow:hidden;display:flex;flex-direction:column}.picture{height:440px;display:block;background:#131a28}.picture img{width:100%;height:100%;object-fit:contain}.copy{padding:25px;flex:1;display:flex;flex-direction:column}.copy small{color:#9cb9c1;letter-spacing:2px}h2{font-size:24px;margin:8px 0 12px}.copy p{color:#b3c6cc;margin:0 0 20px;flex:1}.copy .inherit{color:#acd9c8;font-size:13px;flex:0}nav{display:flex;align-items:center;gap:22px;flex-wrap:wrap}.button{border:1px solid #88bcaf;border-radius:5px;padding:9px 14px}.compare img{width:100%;border-radius:10px;display:block;margin:20px 0}.compare p,footer{color:#a3bbc4}footer a{margin-right:24px}@media(max-width:850px){.grid{grid-template-columns:1fr}h1{font-size:30px}.picture{height:350px}}
</style></head><body><header><small>HK3GTL / RESEARCH CAMPUS / S01—S05</small><h1>从一座实验楼，生长为文明的研究院区。</h1><p>水平窗带、独立实验翼、超算机房、液冷附楼与空中连廊，逐步围绕最初的研究楼展开。第五阶以透光穹顶覆盖中央共享空间，前四阶的建筑仍在其中。</p><p class="note">每一级在上一级的基础上扩建。主控、六个接口、旧建筑及维护通道保留原位；四次升级逐格核对。尺寸为宽 × 深 × 高。</p><p>选择一阶进入三维评审，可旋转、俯视、剖切和查看原有建筑。当前为外观候选，游戏内成型与运行待验收。</p></header><main class="grid">'''+''.join(cards)+'''</main><section class="compare"><h2>同尺度看院区如何生长</h2><p>下列立面和俯视均采用同一比例。每阶三维图另按适合观察的大小显示。</p><a href="五阶正面.png"><img src="五阶正面.png" alt="五阶同尺度正面"></a><a href="五阶俯视.png"><img src="五阶俯视.png" alt="五阶同尺度俯视"></a></section><footer><a href="研究所五阶演进.png">等轴总览</a><a href="S01-S05_研究所五阶_结构与预览.zip">下载结构与预览包</a><a href="http://127.0.0.1:8368/index.html">已确认的采集塔四阶</a><span>2026-10-14 · 原地扩建 V1</span></footer></body></html>'''
    (out/'index.html').write_text(page, encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    draw_sheet(out, entries, '研究所五阶演进.png', 'S01–S05 · 逐阶原地扩建的研究所', 2)
    comparison(out, entries)
    comparison(out, entries, True)
