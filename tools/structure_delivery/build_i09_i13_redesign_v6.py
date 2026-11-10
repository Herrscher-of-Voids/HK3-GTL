# -*- coding: utf-8 -*-
"""I09–I13 三模组参考重设计：独立批次交付和真实纹理三维评审。

变更记录 2026-10-14：新增五种独立机器形体与版本目录；只制作建筑候选。
"""
import argparse
import base64
import collections
import datetime
import gzip
import hashlib
import html
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import nbtlib
from PIL import Image, ImageDraw, ImageFont
from build_i07_calibration_preview import package
from redesign69_geometry import ROOT

OUT = ROOT / 'deliveries/I09-I13_重设计_V6_20261014'
LOG = ROOT / 'logs/i09-i13-redesign-v6'
SKILL = Path.home() / '.codex/skills/minecraft-builder-skill'
GENERATORS = {'i09': 'i09_i10_v6', 'i10': 'i09_i10_v6',
              'i11': 'i11_i12_v6', 'i12': 'i11_i12_v6', 'i13': 'i13_v6'}


def lodestone_export(data, out, log=LOG):
    """使用已安装技能生成NBT，并回读逐格状态核对同源性。"""
    blueprint = out / 'blueprint.json'
    blueprint.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    env = {**os.environ, 'HK3_REVIEW_BLUEPRINT': str(blueprint)}
    result = subprocess.run(['node', str(SKILL / 'scripts/run-build.mjs'),
                             str(ROOT / 'tools/structure_delivery/l1-review89-recipe.mjs'),
                             '--out-dir', str(out), '--name', data['name'],
                             '--data-version', '3465', '--no-block-state-updates', '--json'],
                            cwd=SKILL, env=env, check=True, capture_output=True, text=True, encoding='utf-8')
    loaded = nbtlib.load(out / (data['name']+'.nbt'))
    palette = []
    for state in loaded['palette']:
        properties = state.get('Properties', {})
        suffix = '[' + ','.join(f'{k}={v}' for k, v in sorted(properties.items())) + ']' if properties else ''
        palette.append(str(state['Name'])+suffix)
    decoded = {tuple(map(int, b['pos'])): palette[int(b['state'])] for b in loaded['blocks']}
    assert decoded == {tuple(b['pos']): b['state'] for b in data['blocks']}
    assert list(map(int, loaded['size'])) == data['size']
    (log / (data['key']+'-lodestone.json')).write_text(result.stdout, encoding='utf-8')
    return hashlib.sha256((out/(data['name']+'.nbt')).read_bytes()).hexdigest()


def build_one(key):
    data = getattr(importlib.import_module(GENERATORS[key]), key)()
    data['construction_notes'] = {
        'orientation': 'X向东、Y向上、Z向南；主控正面朝-Z。',
        'origin': [0, 0, 0], 'paste_anchor': [0, 0, 0], 'recommended_world_y': -60,
        'world_height_range': [-60, -60+data['size'][1]-1],
        'status': '本轮外观候选，待用户审阅。',
    }
    out = OUT / key
    package(data, out, key, ['独立主轮廓与功能分区', '局部设备基础与实际检修路线',
                            'GTCEu、GTLCore、GTLsupb结构参考；保留正式名称'])
    sha = lodestone_export(data, out)
    record = json.loads((out/'设计与检查.json').read_text(encoding='utf-8'))
    record['audit']['hashes']['nbt'] = sha
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    counts = collections.Counter(b['state'].split(':')[0] for b in data['blocks']
                                 if b['state'] not in markers)
    ordinary = sum(counts.values())
    record['audit']['namespace_counts'] = dict(counts)
    record['audit']['namespace_percent'] = {k: round(v/ordinary*100, 2) for k, v in counts.items()}
    record['audit']['design_markers'] = dict(collections.Counter(b['state'] for b in data['blocks']
                                                                if b['state'] in markers))
    record['audit']['checks'].append('Minecraft Builder/Lodestone重新导出NBT并逐格回读一致')
    record['audit']['reference_report'] = str((LOG/'reference-study.json').relative_to(ROOT))
    record['audit']['approval'] = '待用户外观确认'
    review_file = LOG/'browser-review.json'
    if review_file.exists():
        browser_review = json.loads(review_file.read_text(encoding='utf-8')).get('machines', {}).get(key)
        if browser_review and browser_review['sha256_nbt'] == sha:
            record['audit']['browser_review'] = browser_review
            record['audit']['checks'].append('浏览器实际载入、视角切换及剖切检查通过')
            record['audit']['not_verified'] = ['待用户外观确认', '未接入正式Pattern与配方',
                                               '未进行Minecraft实际成型与运行验收', '生存材料可达性尚未完整核验']
    (out/'设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    encoded = json.loads((out/'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = record['audit']
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (out/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    page = (out/'三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="设计与检查.json"', 'href="../index.html"').replace('← 设计与检查', '← 五台新设计')
    page = page.replace('src="viewer.bundle.js"', 'src="../viewer.bundle.js"')
    page = page.replace('自由设计候选', 'V6 重设计候选')
    if 'browser_review' in record['audit']:
        page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。', '三维载入与剖切检查通过；正式游戏成型与运行仍待验收。')
    (out/'三维评审.html').write_text(page, encoding='utf-8')
    shutil.copy2(out/'viewer.bundle.js', OUT/'viewer.bundle.js')
    (out/'viewer.bundle.js').unlink()
    entry = {k: data[k] for k in ('key', 'name', 'title', 'size', 'description')}
    entry.update(blocks=len(data['blocks']), materials=len(record['audit']['palette']), sha256_nbt=sha,
                 form=data['brief']['form'], actual_xyz=record['audit']['size_baseline']['actual_xyz'])
    (out/'complete.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    return entry


def gallery(entries):
    cards = []
    for e in entries:
        key = e['key']
        w, h, d = e['size']
        cards.append(f'''<article><a class="picture" href="{key}/三维评审.html"><img src="{key}/等轴预览.png" alt="{html.escape(e['title'])}"></a>
<div class="copy"><small>{key.upper()} · {w} × {d} × {h} 方块</small><h2>{html.escape(e['title'])}</h2>
<p>{html.escape(e['description'])}</p><nav><a class="button" href="{key}/三维评审.html">旋转查看结构 ↗</a>
<a href="{key}/{e['name']}.schem">Schematic</a><a href="{key}/{e['name']}.nbt">NBT</a></nav></div></article>''')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>I09–I13 · 五种工业轮廓</title><style>
*{box-sizing:border-box}body{margin:0;background:#0e1622;color:#eef2f4;font:15px/1.75 'Microsoft YaHei',sans-serif}
header{max-width:1500px;margin:auto;padding:48px 32px 32px}header small{color:#8fb5c5;letter-spacing:3px}h1{font-size:40px;line-height:1.25;margin:12px 0 16px}
header p{max-width:900px;color:#adbcca;margin:8px 0}a{color:#aad3d9;text-decoration:none}a:hover{color:white}main{max-width:1500px;margin:auto;padding:0 32px 48px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}
article{background:#172231;border:1px solid #344355;border-radius:14px;overflow:hidden;display:flex;flex-direction:column}.picture{display:block;background:#131a28;height:360px;overflow:hidden}.picture img{width:100%;height:100%;object-fit:contain;transition:transform .3s}.picture:hover img{transform:scale(1.04)}
.copy{padding:24px;flex:1;display:flex;flex-direction:column}.copy small{color:#95b5c2;letter-spacing:1px}.copy h2{margin:8px 0 12px;font-size:24px}.copy p{margin:0 0 24px;color:#bdcbd6;flex:1}nav{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.button{border:1px solid #77aeb5;border-radius:6px;padding:9px 14px;color:#d0eef1}
footer{max-width:1500px;padding:0 32px 48px;margin:auto;color:#9aabba}footer a{margin-right:24px}@media(max-width:900px){main{grid-template-columns:1fr}.picture{height:320px}h1{font-size:32px}header{padding-top:32px}}
</style></head><body><header><small>HK3GTL / INDUSTRIAL STUDIES / V6</small><h1>五台机器，五种工业轮廓。</h1>
<p>珍珠形配制釜、共轴合成线、折肘装配工场、双翼编程晶舱、立式磁控包覆环。参考 GTCEu、GTLCore 与 GTLsupb 的实际多方块，把各自的加工过程落实到轮廓、支撑与连接关系。</p>
<p>点开任意机器即可旋转、缩放和逐层剖切。尺寸按宽 × 深 × 高显示。</p></header><main>'''+''.join(cards)+'''</main><footer>
<a href="五机总览.png">五机总览图</a><a href="I09-I13_V6_结构与预览.zip">下载结构与预览包</a><span>2026-10-14 · 外观候选，待审阅</span></footer></body></html>'''
    (OUT/'index.html').write_text(page, encoding='utf-8')
    overview = Image.new('RGB', (1800, 1860), '#0e1622')
    draw = ImageDraw.Draw(overview)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 44)
    label = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
    draw.text((40, 30), 'I09–I13  ·  五种工业轮廓', font=title, fill='#edf3f8')
    for j, e in enumerate(entries):
        x, y = 40+(j%2)*870, 115+(j//2)*560
        draw.rounded_rectangle((x, y, x+830, y+530), radius=12, fill='#172231', outline='#354559')
        im = Image.open(OUT/e['key']/'等轴预览.png').convert('RGB')
        im.thumbnail((800, 405), Image.Resampling.LANCZOS)
        overview.paste(im, (x+(830-im.width)//2, y+12+(405-im.height)//2))
        draw.text((x+22, y+429), f"{e['key'].upper()}  {e['title']}", font=label, fill='#eef2f4')
        w, h, d = e['size']
        draw.text((x+22, y+475), f'{w} × {d} × {h}  |  {e["blocks"]:,} 方块', font=small, fill='#9cb9c5')
    overview.save(OUT/'五机总览.png')
    (OUT/'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')


def bundle():
    target = OUT/'I09-I13_V6_结构与预览.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', nargs='*', metavar='i09…i13')
    args = parser.parse_args()
    if set(args.keys)-set(GENERATORS):
        parser.error('编号只支持 i09 至 i13')
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    for key in args.keys or GENERATORS:
        build_one(key)
    entries = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('*/complete.json'))]
    if (LOG/'reference-study.json').exists():
        shutil.copy2(LOG/'reference-study.json', OUT/'结构参考.json')
    gallery(entries)
    bundle()


if __name__ == '__main__':
    main()
