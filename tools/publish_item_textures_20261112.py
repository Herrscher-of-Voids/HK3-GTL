"""汇总本轮物品像素原稿、前后对照及独立资源包。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LOG = ROOT / 'logs/item-texture-refresh-20261112'
OUT = ROOT / 'deliveries/物品材质补全_R259_20261112'
GROUPS = {'world': '世界泡与探针', 'key': '核心与神之键', 'process': '样本与燃料工艺', 'engineering': '工业模块与舰体', 'record': '档案与研究模块'}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, models = [], []
    for group, label in GROUPS.items():
        data = json.loads((LOG / (group + '-manifest.json')).read_text(encoding='utf-8'))
        entries = data['changed'] if isinstance(data, dict) else data
        rows.extend({**r, 'group': group, 'group_name': label} for r in entries)
        if isinstance(data, dict): models.extend(data.get('model_changes', []))
    cards = []
    names = json.loads((ASSETS / 'lang/zh_cn.json').read_text(encoding='utf-8-sig'))
    sheet = Image.new('RGB', (1200, ((len(rows) + 4) // 5) * 160), '#162132')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 12)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 10)
    for i, row in enumerate(rows):
        rel = row['path']
        name = names.get('item.hk3gtl.' + row['id'], row['name'])
        target = OUT / 'after' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ASSETS / rel, target)
        old = LOG / 'before/assets/hk3gtl' / rel
        old_html = '<span class="empty">原来借用其他图标</span>'
        if old.exists():
            target = OUT / 'before' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old, target)
            old_html = f'<img loading="lazy" src="before/{rel}" alt="原图">'
        cards.append(f'<article data-group="{row["group"]}"><h2>{html.escape(name)}</h2><small>{row["group_name"]}</small><div class="pair"><figure>{old_html}<figcaption>原图</figcaption></figure><figure><img loading="lazy" src="after/{rel}" alt="新版"><figcaption>新版</figcaption></figure></div><code>{row["id"]}</code><p>{html.escape(row["design"])}</p></article>')
        x, y = (i % 5) * 240, (i // 5) * 160
        draw.text((x + 8, y + 6), name[:17], font=font, fill='#e7edf7')
        for offset, path in ((10, old), (125, ASSETS / rel)):
            if path.exists():
                image = Image.open(path).convert('RGBA')
                frame = image.crop((0, 0, image.width, image.width)).resize((80, 80), Image.Resampling.NEAREST)
                sheet.paste(frame, (x + offset, y + 32), frame)
        draw.text((x + 30, y + 117), '原图', font=font, fill='#9cb0cb')
        draw.text((x + 145, y + 117), '新版', font=font, fill='#9cb0cb')
        draw.text((x + 5, y + 140), row['id'][:38], font=small, fill='#869bb6')
    sheet.save(OUT / '物品材质新旧总览.png')
    buttons = ''.join(f'<button data-group="{key}">{value}</button>' for key, value in GROUPS.items())
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HK3GTL · 物品材质补全 R259</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;padding:26px;background:#101722;color:#e6edf7;font:15px system-ui}main{max-width:1450px;margin:auto}h1{font-size:27px}h2{font-size:17px;margin:0 0 8px}p{color:#b7c5d8;line-height:1.6}a{color:#a8c9fc}.notice{border-left:3px solid #b3a0d8;padding:10px 16px;background:#22283a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}article{padding:18px;border-radius:10px;background:#192335;border:1px solid #34415a;overflow:hidden}article[hidden]{display:none}small,code{color:#9eb1cc;font-size:11px}code{overflow-wrap:anywhere}.pair{display:flex;gap:18px;margin:18px 0}figure{flex:1;margin:0;text-align:center}img{width:100%;max-width:112px;aspect-ratio:1;image-rendering:pixelated;object-fit:contain;background:repeating-conic-gradient(#2c384b 0% 25%,#1e293b 0% 50%) 50%/14px 14px}figcaption{font-size:12px;color:#a9bad3;margin-top:8px}.empty{display:grid;place-items:center;height:112px;font-size:12px;border:1px dashed #455571}nav{position:sticky;top:0;display:flex;gap:8px;flex-wrap:wrap;padding:13px 0;background:#101722f5;z-index:2}button,input{padding:10px;border:1px solid #465778;background:#22324c;color:#e2eaf8;border-radius:6px}button{cursor:pointer}input{flex:1;min-width:180px}#count{padding:10px;color:#a9bad3}</style><main>
<h1>物品材质补全 · R259候选</h1><p class="notice">本页补齐遗漏的工业物品，占位图不再局限于上一批7件。实例已按负责人要求先安装R258；本页R259尚未覆盖实例。</p>
<p>86张旧通用图重画，另为3件借用纸张／处理器的物品绘制专用图，共89件。世界泡、容器、探针、纳米件、燃料件、电路、舰船模块和未封装核心按用途区分轮廓与颜色。全部16×16、静态透明底；87个研究试件继续复用原有样本链。</p>
<p>保留此前精修物品、231项已批准主材及上一批7功能件、38种流体。已删除的93个方块保持删除。</p><p><a href="物品材质资源包_R259.zip">本批资源包</a> · <a href="物品材质新旧总览.png">总览图</a> · <a href="manifest.json">清单</a> · <a href="../功能件与流体材质_R258_20261112/index.html">R258材质</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p>
<nav><button data-group="all">全部</button>'''+buttons+'''<input type="search" aria-label="搜索物品" placeholder="搜索名称或ID"><span id="count"></span></nav><div class="grid">'''+''.join(cards)+'''</div></main><script>let group='all';const cards=[...document.querySelectorAll('article')],q=document.querySelector('input');function filter(){let count=0;for(const card of cards){card.hidden=(group!=='all'&&card.dataset.group!==group)||!card.textContent.toLowerCase().includes(q.value.trim().toLowerCase());if(!card.hidden)count++}document.querySelector('#count').textContent=count+'件'}for(const b of document.querySelectorAll('[data-group]'))if(b.tagName==='BUTTON')b.onclick=()=>{group=b.dataset.group;filter()};q.oninput=filter;filter();</script></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps({'revision': 259, 'changed': rows, 'model_changes': models, 'installed': False}, ensure_ascii=False, indent=2), encoding='utf-8')
    with zipfile.ZipFile(OUT / '物品材质资源包_R259.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr('pack.mcmeta', json.dumps({'pack': {'pack_format': 15, 'description': 'HK3GTL R259 · 工业物品材质补全'}}, ensure_ascii=False))
        for row in rows: z.write(ASSETS / row['path'], 'assets/hk3gtl/' + row['path'])
        for ident in ('world_mining_legacy_record', 'ship_engineering_archive', 'erosion_research_module'):
            rel = 'models/item/' + ident + '.json'
            z.write(ASSETS / rel, 'assets/hk3gtl/' + rel)
    print(json.dumps({'count': len(rows), 'review': str(OUT / 'index.html')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
