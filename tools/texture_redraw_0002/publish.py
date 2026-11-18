# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/textures-redraw-0002-v2-20261114'
OUT = ROOT / 'deliveries/0002贴图材质_全量重绘_V2_20261114'
GROUPS = {'world': '世界泡与探针', 'key': '核心与神之键', 'process': '样本与燃料工艺',
          'engineering': '工业模块与舰体', 'record': '档案与研究模块'}
FONT = 'C:/Windows/Fonts/msyh.ttc'
REVIEW = json.loads((LOG / 'art-review.json').read_text(encoding='utf-8'))
ACCEPTED = set(REVIEW['accepted_ids'])
EXCLUDED = set(REVIEW['excluded_item_ids'])
STATUS = {'accepted': '已认可 · 锁定', 'excluded': '不再保留 · 不再重画', 'pending': '待下一轮重画'}


def sheet(rows, path, cols=8):
    cw, ch, top = 190, 232, 90
    im = Image.new('RGB', (cols * cw, ((len(rows) + cols - 1) // cols) * ch + top), '#171e28')
    d = ImageDraw.Draw(im)
    title = ImageFont.truetype(FONT, 25)
    font = ImageFont.truetype(FONT, 14)
    small = ImageFont.truetype(FONT, 11)
    d.text((16, 10), '0002 · 物品贴图全量重绘 R2', font=title, fill='#f0e8d7')
    d.text((17, 50), 'R2评审 · 20张认可锁定 / 9种核心退出后续贴图 / 59张待重画 · 原生64×64', font=font, fill='#afc0ca')
    for i, row in enumerate(rows):
        x, y = (i % cols) * cw, (i // cols) * ch + top
        d.rectangle((x + 4, y + 3, x + cw - 5, y + ch - 5), fill='#2d3640', outline='#44505a')
        d.text((x + 12, y + 9), f'{row["number"]:02}  {row["group_name"]}', font=small, fill='#b3c3cc')
        sprite = Image.open(OUT / row['path']).resize((128, 128), Image.Resampling.NEAREST)
        im.paste(sprite, (x + 31, y + 30), sprite)
        text, lines = '', []
        for char in row['name']:
            if d.textlength(text + char, font=font) > cw - 22:
                lines.append(text)
                text = ''
            text += char
        lines.append(text)
        for n, line in enumerate(lines):
            d.text((x + 11, y + 165 + n * 19), line, font=font, fill='#eeeade')
        d.text((x + 11, y + 210), STATUS[row['review_status']], font=small,
               fill='#c6dda1' if row['review_status'] == 'accepted' else '#b9bbc2')
    im.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    names = {row['id']: row['name'] for row in prior['items']}
    rows, gallery = [], []
    for group, label in GROUPS.items():
        data = json.loads((ROOT / f'logs/item-texture-refresh-20261112/{group}-manifest.json').read_text(encoding='utf-8'))
        entries = data['changed'] if isinstance(data, dict) else data
        for entry in entries:
            ident = entry['id']
            if ident == 'imitation_void_archives':
                continue
            path = entry['path']
            old = (LOG / 'before' / path).read_bytes()
            target = OUT / path
            new = target.read_bytes()
            sprite = Image.open(target)
            row = {'number': len(rows) + 1, 'id': ident, 'name': names[ident],
                   'group': group, 'group_name': label, 'path': path,
                   'changed': old != new, 'size': list(sprite.size), 'mode': sprite.mode,
                   'review_status': 'accepted' if ident in ACCEPTED else 'excluded' if ident in EXCLUDED else 'pending',
                   'before_sha256': hashlib.sha256(old).hexdigest(), 'after_sha256': hashlib.sha256(new).hexdigest()}
            rows.append(row)
            gallery.append({**row, 'old': base64.b64encode(old).decode(), 'new': base64.b64encode(new).decode()})
    manifest = {'revision': 'R2', 'conversation_number': '0002',
                'conversation_id': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'updated_at': datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
                'status': 'R2累计20张认可锁定，9种未封装律者核心退出后续贴图，59张待下一轮重画。',
                'accepted_count': len(ACCEPTED), 'excluded_item_count': len(EXCLUDED),
                'pending_redraw_count': REVIEW['pending_redraw_count'],
                'art_review': 'logs/textures-redraw-0002-v2-20261114/art-review.json',
                'redrawn_count': sum(r['changed'] for r in rows), 'preserved_count': sum(not r['changed'] for r in rows),
                'style': 'Minecraft像素实物、GregTech工业材质、崩坏3形制与身份配色；原生64×64透明PNG。',
                'reference': 'logs/textures-redraw-0002-v2-20261114/gt-references.png',
                'preserved': ['world_mining_legacy_record', 'imitation_void_archives复用原普通虚空万藏贴图'],
                'installed': False, 'game_tested': False, 'art_approved': False, 'items': rows}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (LOG / 'resource-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet(rows, OUT / 'texture-contact-sheet.png')
    for group in GROUPS:
        sheet([r for r in rows if r['group'] == group], OUT / f'{group}-contact-sheet.png', 5)
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002贴图材质 · R2全量重绘</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#171e28;color:#ede8db;font:15px 'Microsoft YaHei',system-ui}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:28px;margin:0 0 10px}p{color:#afc0ca;line-height:1.7;margin:8px 0}a{color:#cbb4f4}header{border-bottom:1px solid #44505a;padding-bottom:18px}nav{position:sticky;top:0;background:#171e28f5;z-index:2;padding:14px 0;display:flex;gap:8px;flex-wrap:wrap}button,input,select{font:inherit;color:inherit;background:#2d3640;border:1px solid #56626c;padding:9px 12px;border-radius:5px}button{cursor:pointer}button.active{border-color:#cfb3f7;background:#40344f}input{flex:1;min-width:200px}small,code{color:#afc0ca}code{font-size:11px;overflow-wrap:anywhere}#count{margin:0 0 12px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(176px,1fr));gap:10px}.item{background:#2d3640;border:1px solid #44505a;border-radius:6px;padding:12px;display:flex;flex-direction:column;align-items:center;cursor:pointer}.item[hidden]{display:none}.item h2{font-size:14px;line-height:1.5;min-height:42px;text-align:center;margin:12px 0 5px}.item small{align-self:flex-start;font-size:11px}.pixels{image-rendering:pixelated;image-rendering:crisp-edges;object-fit:contain;background:var(--stage,#323940)}.item img{width:128px;height:128px;margin-top:10px}.item .old{display:none}.pairview .item .old{display:block}.pairview .item img{width:96px;height:96px}.pairview .thumbs{display:flex;gap:6px}.oldview .item .new{display:none}.oldview .item .old{display:block}.badge{color:#c6dda1;font-size:11px}dialog{max-width:min(900px,96vw);width:860px;background:#212b35;color:#eee8db;border:1px solid #63717e;border-radius:8px;padding:24px}dialog::backdrop{background:#080c12d9}.zoom{display:flex;justify-content:center;gap:22px;flex-wrap:wrap}.zoom figure{margin:0;text-align:center}.zoom img{width:min(320px,37vw);height:min(320px,37vw)}figcaption{margin:10px;color:#afc0ca}#close{float:right}#detail h2{margin:0 50px 8px 0}#detail code{display:block;margin-bottom:18px}footer{margin-top:24px;padding-top:15px;border-top:1px solid #44505a;font-size:12px}@media(max-width:520px){main{padding:16px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.item{padding:8px}.item img{width:112px;height:112px}.pairview .item img{width:60px;height:60px}h1{font-size:22px}}
</style><main><header><h1>0002贴图材质 · R2全量重绘</h1><p>87张重新绘制，1张原样保留。原生64×64透明PNG；本轮候选待你评审。</p><p>保留“真实采掘遗留资料”。仿制虚空万藏继续复用原普通虚空万藏贴图，不计入这88张。</p><p><a href="texture-contact-sheet.png">88张总览原图</a> · <a href="manifest.json">逐图清单</a> · <a href="0002贴图材质-0.5.0-R2.jar">本对话R2候选JAR</a></p></header>
<nav id="filters"><input id="search" placeholder="搜索中文名 / 物品ID" aria-label="搜索贴图"><select id="view" aria-label="对照模式"><option value="newview">新版</option><option value="pairview">新旧对照</option><option value="oldview">旧版</option></select><select id="background" aria-label="预览底色"><option value="#323940">深灰底</option><option value="#b6b5ac">浅灰底</option><option value="#161b20">暗色底</option></select><button class="active" data-group="all">全部</button>__BUTTONS__</nav><p id="count"></p><div class="grid" id="grid"></div><footer>对话2 / 0002 · 对话ID：01a1d68a-a994-7ac0-a48a-54c0f98fd54e<br>候选JAR仅替换本对话上一版已编译包的87张PNG；不是其他并行对话更新的整合包。未安装、未进行游戏验收。</footer></main>
<dialog id="detail"><button id="close">关闭 ×</button><h2 id="name"></h2><code id="ident"></code><div class="zoom"><figure><img id="oldbig" class="pixels" alt="旧版"><figcaption>旧版</figcaption></figure><figure><img id="newbig" class="pixels" alt="新版"><figcaption id="newlabel">R2新版</figcaption></figure></div><p id="meta"></p></dialog>
<script>
const items=__DATA__,grid=document.querySelector('#grid'),detail=document.querySelector('#detail');
const labels={accepted:'已认可 · 锁定',excluded:'不再保留 · 不再重画',pending:'待下一轮重画'};
let group='all';
const src=b=>'data:image/png;base64,'+b;
items.forEach(r=>{const card=document.createElement('article');card.className='item';card.dataset.group=r.group;card.dataset.search=(r.name+' '+r.id).toLowerCase();card.innerHTML=`<small>${String(r.number).padStart(2,'0')} · ${r.group_name}</small><div class="thumbs"><img class="old pixels" alt="旧版" src="${src(r.old)}"><img class="new pixels" alt="R2新版" src="${src(r.new)}"></div><h2>${r.name}</h2><code>${r.id}</code><span class="badge" style="color:${r.review_status==='accepted'?'#c6dda1':'#b9bbc2'}">${labels[r.review_status]}</span>`;card.tabIndex=0;card.onclick=()=>open(r);card.onkeydown=e=>{if(e.key==='Enter')open(r)};grid.append(card)});
function open(r){document.querySelector('#name').textContent=r.name;document.querySelector('#ident').textContent=r.id;document.querySelector('#oldbig').src=src(r.old);document.querySelector('#newbig').src=src(r.new);document.querySelector('#newlabel').textContent=r.changed?'R2新版':'原样保留';document.querySelector('#meta').textContent=`${r.number} / 88 · ${r.group_name} · 64×64 RGBA · ${labels[r.review_status]}`;detail.showModal()}
function filter(){const q=document.querySelector('#search').value.trim().toLowerCase();let n=0;grid.querySelectorAll('.item').forEach(c=>{c.hidden=(group!=='all'&&c.dataset.group!==group)||!c.dataset.search.includes(q);n+=!c.hidden});document.querySelector('#count').textContent=`显示 ${n} / 88 · 点击贴图查看放大对照`}
document.querySelector('#filters').addEventListener('click',e=>{if(!e.target.dataset.group)return;group=e.target.dataset.group;document.querySelectorAll('[data-group].active').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');filter()});
document.querySelector('#search').oninput=filter;document.querySelector('#view').onchange=e=>grid.className='grid '+e.target.value;document.querySelector('#background').onchange=e=>document.documentElement.style.setProperty('--stage',e.target.value);document.querySelector('#close').onclick=()=>detail.close();detail.onclick=e=>{if(e.target===detail)detail.close()};filter();
</script></html>'''
    buttons = ''.join(f'<button data-group="{key}">{value}</button>' for key, value in GROUPS.items())
    page = page.replace('__BUTTONS__', buttons).replace('__DATA__', json.dumps(gallery, ensure_ascii=False, separators=(',', ':')))
    page = page.replace('87张重新绘制，1张原样保留。原生64×64透明PNG；本轮候选待你评审。',
                        'R2累计20张认可锁定，9种未封装律者核心退出后续贴图，59张待下一轮重画。本页保留R2历史图，原候选JAR未修改。')
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'redrawn': manifest['redrawn_count'], 'preserved': manifest['preserved_count']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
