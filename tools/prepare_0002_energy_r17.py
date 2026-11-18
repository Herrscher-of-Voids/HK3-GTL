from datetime import datetime
from hashlib import sha256
from html import escape
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliveries/0002贴图材质_发电补充_R17_20261116'
LOG = ROOT / 'logs/textures-energy-handoff-0002-r17-20261116'


def main():
    items = json.loads((OUT / 'item-manifest.json').read_text('utf-8-sig'))
    fluids = json.loads((OUT / 'fluid-manifest.json').read_text('utf-8-sig'))
    records = sorted(items['records'], key=lambda r: r['firstTier']) + sorted(fluids['records'], key=lambda r: r['firstTier'])
    resources = items['resources'] + fluids['resources']
    updated = datetime.now().astimezone().isoformat()
    manifest = dict(revision='R17', conversation='0002', conversationId='01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
        updatedAt=updated, status='候选待评审', itemCount=4, fluidCount=4, pngCount=12, itemModelCount=4,
        animationMetadataCount=8, candidateResourceCount=len(resources),
        sourceHandoff='deliveries/0003_全剩余电压工业链与材质交接_20261116/energy-handoff.json',
        inputFiles=json.loads((LOG / 'intake.json').read_text('utf8'))['inputFiles'],
        itemAdapter='tools/invoke_image_relay.ps1 -Mode Generate -RelayResponse',
        originalCanvasPreserved=True, referenceImagesUploaded=0,
        artApproved=False, sourceApplied=False, jarBuilt=False, installed=False,
        records=records, resources=resources)
    data = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    (OUT / 'manifest.json').write_text(data, 'utf8')
    (LOG / 'manifest.json').write_text(data, 'utf8')

    sheet = Image.new('RGB', (1280, 760), '#14202c')
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 28)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    draw.text((24, 14), '0002 · R17 发电补充材质 · 候选待评审', font=title, fill='#edf3ff')
    draw.text((24, 56), '四套工装与对应燃料液；原图、透明PNG与轻量动画分别保留', font=small, fill='#b8c9dc')
    for index, record in enumerate(records):
        x, y = 24 + index % 4 * 314, 96 + index // 4 * 330
        path = record['preview'] if record['kind'] == 'item' else record['staticPreview']
        with Image.open(OUT / path) as source:
            tile = source.convert('RGB').resize((264, 264), Image.Resampling.NEAREST)
        sheet.paste(tile, (x, y))
        draw.text((x, y + 272), record['name'], font=font, fill='#edf3ff')
        draw.text((x, y + 302), f"Tier{record['firstTier']} · {'工装' if record['kind'] == 'item' else '流体'}", font=small, fill='#b8c9dc')
    sheet.save(OUT / 'overview.png', optimize=True)

    cards = []
    for record in records:
        links = [(record['image'], '材质PNG')]
        if record['kind'] == 'item':
            links.extend([(record['original'], 'API原图'), (record['promptFile'], '提示词')])
            size = record['size']
            note = f'{size[0]}×{size[1]}透明PNG，保留实际原画布。'
        else:
            links.extend((t['image'], t['kind'] + ' PNG') for t in record['textures'] if t['image'] != record['image'])
            note = '静止64×64、流动128×128单帧；4帧、6tick、关闭插值。'
        anchors = ' · '.join(f'<a href="{escape(path)}" target="_blank">{escape(label)}</a>' for path, label in links)
        facts = ''.join('<p>' + escape(fact) + '</p>' for fact in record['facts'])
        targets = ''.join('<code>' + escape(path) + '</code>' for path in record['targets'])
        cards.append(f'<article><span>Tier{record["firstTier"]} · {"物品" if record["kind"] == "item" else "流体"}</span>'
            f'<h2>{escape(record["name"])}</h2><code>hk3gtl:{escape(record["id"])}</code>'
            f'<a class="art" href="{escape(record["image"])}" target="_blank"><img src="{escape(record["preview"])}" alt="{escape(record["name"])}"></a>'
            f'<p>{escape(record["designZh"])}</p><p class="muted">{note}</p><p>{anchors}</p>'
            f'<details><summary>工艺依据与目标路径</summary>{facts}{targets}</details></article>')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · 发电补充材质 R17</title><style>
:root{color-scheme:dark;font:15px/1.65 "Microsoft YaHei",system-ui;color:#eaf1f8;background:#101722}*{box-sizing:border-box}body{margin:0}main{max-width:1500px;margin:auto;padding:28px}h1{font-size:30px}h2{font-size:19px;margin:7px 0}p{color:#b3c5d8}a{color:#cfb8f4}nav{display:flex;gap:18px;flex-wrap:wrap;margin:20px 0}.notice{background:#202a39;border-left:3px solid #bfa0e9;padding:13px 18px}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px;margin-top:24px}article{padding:15px;background:#182333;border:1px solid #344254;border-radius:8px;min-width:0}article span{font-size:12px;color:#c8a9ed}code{display:block;font:11px/1.7 Consolas,monospace;color:#9fb3cb;overflow-wrap:anywhere}.art{display:block;aspect-ratio:1;margin:15px 0;background:repeating-conic-gradient(#e2e7eb 0 25%,#c5ced5 0 50%) 0/20px 20px}.art img{display:block;width:100%;height:100%;object-fit:contain;image-rendering:pixelated}article p,details{font-size:13px}.muted,footer{color:#91a9c1}summary{cursor:pointer;color:#d3bcea}.overview{width:100%;display:block;margin:25px 0}footer{margin-top:28px;font-size:13px}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){main{padding:14px}.grid{gap:8px}article{padding:9px}h2{font-size:15px}h1{font-size:25px}}
</style><main><h1>R17 · 发电补充材质</h1><p>四套燃料工装与四种含能燃料液，按0003交接的制造、用途及工艺阶段分别设计。</p>
<div class="notice">候选待评审。物品保留API原画布、透明PNG和提示词；流体沿用R15/R16的轻量动画规格。</div>
<nav><a href="overview.png">八项总览</a><a href="manifest.json">完整材质记录</a><a href="../0003_全剩余电压工业链与材质交接_20261116/handoff.html">0003工艺交接</a><a href="../../logs/beta5-completion-audit-20261030/index.html">固定报告</a></nav>
<div class="grid">CARDS</div><footer>0002贴图材质 · 对话ID 01a1d68a-a994-7ac0-a48a-54c0f98fd54e<br>本批候选尚待采用；正式源码、构建和安装状态见manifest.json。</footer></main></html>'''
    (OUT / 'index.html').write_text(page.replace('CARDS', ''.join(cards)), 'utf8')
    completion = dict(updated_at=updated, conversation='0002', revision='R17', status='8项材质候选已完成，待负责人评审。',
        item_count=4, fluid_count=4, pngs=12, item_models=4, animation_metadata=8,
        gallery=str(OUT / 'index.html'), manifest=str(OUT / 'manifest.json'),
        manifest_sha256=sha256((OUT / 'manifest.json').read_bytes()).hexdigest(),
        original_canvas_preserved=True, fluid_frames=4, fluid_frametime_ticks=6, fluid_interpolation=False,
        source_applied=False, jar_built=False, installed=False, game_started=False, scores_changed=False)
    (LOG / 'completion.json').write_text(json.dumps(completion, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(completion, ensure_ascii=False))


if __name__ == '__main__':
    main()
