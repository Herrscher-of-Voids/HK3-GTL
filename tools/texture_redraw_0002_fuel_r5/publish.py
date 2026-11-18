# -*- coding: utf-8 -*-
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_燃料棒_R5_20261114'
STATES = {'active': '活性', 'depleted': '乏燃料', 'broken': '破损', 'rejected': '不合格'}
RODS = (1, 4, 8, 16)
SPECS = {1: '单棒', 4: '4连棒', 8: '8连棒', 16: '16连棒'}
PREVIEW_IDS = ('honkai_fuel_rod', 'dense_honkai_fuel_rod', 'honkai_diamond_copper_fuel')


HTML = '''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · 燃料棒 R5 材质评审</title>
<style>
:root{color-scheme:dark;--bg:#171d24;--panel:#252e39;--text:#e9edf0;--muted:#aebcc8;--line:#526273;--tile:#293441;--a:#354351;--b:#2c3743;--accent:#d4b676}
body.light{color-scheme:light;--bg:#f0f0e9;--panel:#fffef7;--text:#222e39;--muted:#55616b;--line:#b1b9bc;--tile:#f6f5ee;--a:#eeeae0;--b:#dddcd4;--accent:#815a20}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 "Microsoft YaHei",sans-serif}
main{max-width:1300px;margin:auto;padding:28px 24px 80px}h1{margin:0 0 10px;font-size:29px}h2{margin:32px 0 12px;font-size:20px}h3{font-size:15px;margin:12px 0 8px;color:var(--muted)}
p{margin:7px 0}.muted{color:var(--muted)}a{color:var(--accent);text-underline-offset:3px}.links{display:flex;gap:18px;flex-wrap:wrap;margin:15px 0}
.notice{padding:14px 18px;border:1px solid var(--line);background:var(--panel);border-radius:8px}
.toolbar{position:sticky;top:0;z-index:3;display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 0;background:var(--bg);border-bottom:1px solid var(--line)}
button,select{font:inherit;color:var(--text);border:1px solid var(--line);border-radius:5px;background:var(--panel);padding:7px 12px}button{cursor:pointer}button:hover,a:hover{filter:brightness(1.15)}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}label{display:flex;gap:8px;align-items:center}#count{margin-left:auto;font-size:13px;color:var(--muted)}
.specs,.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.specs{margin:12px 0;color:var(--muted);text-align:center;font-size:13px}
.card{margin:0;padding:10px;background:var(--panel);border:1px solid var(--line);border-radius:7px;overflow:hidden}.open{border:0;padding:0;display:block;width:100%;border-radius:3px}
.checker{background-color:var(--a);background-image:linear-gradient(45deg,var(--b) 25%,transparent 25%),linear-gradient(-45deg,var(--b) 25%,transparent 25%),linear-gradient(45deg,transparent 75%,var(--b) 75%),linear-gradient(-45deg,transparent 75%,var(--b) 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}
.card img{display:block;width:100%;height:180px;object-fit:contain;image-rendering:pixelated;padding:14px}.card figcaption{margin:9px 0 3px;font-weight:600}.card p{font-size:12px;color:var(--muted);overflow-wrap:anywhere}.card a{font-size:13px}
dialog{max-width:94vw;max-height:95vh;padding:18px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--text)}dialog::backdrop{background:#000b}.modal-head{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:12px}
#large{display:block;width:min(70vmin,512px);height:min(70vmin,512px);object-fit:contain;image-rendering:pixelated;padding:20px}#detail{max-width:512px;overflow-wrap:anywhere;font-size:12px;color:var(--muted)}
@media(max-width:700px){main{padding:20px 12px 55px}.specs,.grid{gap:6px}.card{padding:5px}.card img{height:120px;padding:4px}.card figcaption{font-size:12px}.card p{display:none}h1{font-size:23px}#count{margin-left:0;width:100%}}
</style>
<main>
<h1>燃料棒 R5 · 15族材质评审</h1>
<p class="muted">对话0002 · 贴图材质 · 对话ID：01a1d68a-a994-7ac0-a48a-54c0f98fd54e</p>
<div class="notice"><p>本页只展示材质：15族 × 活性／乏燃料／破损 × 单／4／8／16连，共180张，另有不合格单棒1张。</p>
<p>0003已注册135个多联物品，0002已接通全部135个独立材质引用；外观仍待评审。66项已认可材质与神之键R6候选保持；未打包或安装JAR。</p>
<p>母图：<a href="references/honkai_fuel_rod_original.png">负责人指定的原始燃料棒PNG</a>。材质身份、现有物品标记、资源路径及供应链映射直接见清单。</p></div>
<nav class="links"><a href="manifest.json">查看材质与供应链映射清单</a><a href="0002贴图材质-R5-燃料棒资源.zip">材质资源ZIP</a><a href="active-contact-sheet.png">60张活性组图</a><a href="state-contact-sheet.png">15族三状态与不合格单棒</a><a href="preview.png">三族规格与15色总览</a></nav>
<div class="toolbar"><label>族<select id="family"><option value="all">全部15族</option></select></label>
<label>状态<select id="state"><option value="active">活性</option><option value="depleted">乏燃料</option><option value="broken">破损</option><option value="rejected">不合格</option><option value="all">全部状态</option></select></label>
<button id="theme" aria-pressed="false">切换为明色底</button><span id="count" aria-live="polite"></span></div>
<div class="specs"><span>单棒</span><span>4连棒</span><span>8连棒</span><span>16连棒</span></div><div id="gallery"></div>
</main>
<dialog id="viewer"><div class="modal-head"><strong id="title"></strong><button id="close" aria-label="关闭放大图">关闭</button></div><img id="large" class="checker" alt=""><p id="detail"></p><a id="download" download>打开／保存本地PNG</a></dialog>
<script>
const data=__DATA__, states={active:'活性',depleted:'乏燃料',broken:'破损',rejected:'不合格'}, specs={1:'单棒',4:'4连棒',8:'8连棒',16:'16连棒'};
const family=document.querySelector('#family'),state=document.querySelector('#state'),gallery=document.querySelector('#gallery'),viewer=document.querySelector('#viewer');
const rejected=data.items.find(it=>it.state==='rejected'),galleryFamilies=[...data.families,{id:rejected.family_id,name:rejected.name}];
for(const f of data.families){const o=document.createElement('option');o.value=f.id;o.textContent=f.name;family.append(o)}
function openImage(it){document.querySelector('#large').src=it.image;document.querySelector('#large').alt=it.name;document.querySelector('#title').textContent=it.name+' · '+specs[it.rods]+' · '+states[it.state];document.querySelector('#detail').textContent=it.texture+' · '+(it.existing_item?'现有物品':'仅材质候选')+' · SHA256 '+it.sha256;document.querySelector('#download').href=it.image;viewer.showModal()}
function card(it){const f=document.createElement('figure');f.className='card';const b=document.createElement('button');b.className='open checker';b.type='button';b.setAttribute('aria-label','放大查看'+it.name);const im=document.createElement('img');im.src=it.image;im.alt=it.name;im.loading='lazy';b.append(im);b.onclick=()=>openImage(it);f.append(b);const c=document.createElement('figcaption');c.textContent=specs[it.rods];f.append(c);const p=document.createElement('p');p.textContent=it.name+' · '+(it.existing_item?'现有物品':'仅材质候选');f.append(p);const a=document.createElement('a');a.href=it.image;a.download='';a.textContent='本地PNG';f.append(a);return f}
function render(){gallery.replaceChildren();let total=0;for(const f of galleryFamilies){if(family.value!=='all'&&family.value!==f.id)continue;const selected=data.items.filter(it=>it.family_id===f.id&&(state.value==='all'||it.state===state.value));if(!selected.length)continue;const sec=document.createElement('section'),h=document.createElement('h2');h.textContent=f.name;sec.append(h);for(const st of Object.keys(states)){const row=selected.filter(it=>it.state===st).sort((a,b)=>a.rods-b.rods);if(!row.length)continue;const title=document.createElement('h3');title.textContent=states[st];sec.append(title);const grid=document.createElement('div');grid.className='grid';for(const it of row)grid.append(card(it));sec.append(grid);total+=row.length}gallery.append(sec)}document.querySelector('#count').textContent='当前 '+total+' 张 / 清单 '+data.items.length+' 张'}
family.onchange=render;state.onchange=render;document.querySelector('#close').onclick=()=>viewer.close();viewer.onclick=e=>{if(e.target===viewer)viewer.close()};document.querySelector('#theme').onclick=e=>{const light=document.body.classList.toggle('light');e.currentTarget.textContent=light?'切换为暗色底':'切换为明色底';e.currentTarget.setAttribute('aria-pressed',String(light))};render();
</script></html>'''


def checker(draw, x, y, side):
    for yy in range(0, side, 8):
        for xx in range(0, side, 8):
            color = '#35414d' if (xx//8+yy//8)%2 else '#2c3743'
            draw.rectangle((x+xx,y+yy,x+xx+7,y+yy+7),fill=color)


def stamp(canvas, draw, item, x, y, side=128):
    checker(draw,x,y,side)
    im=Image.open(OUT/item['image']).convert('RGBA').resize((side,side),Image.Resampling.NEAREST)
    canvas.paste(im,(x,y),im)


def label(draw,text,x,y,font,fill='#e5e9eb',width=12):
    for i in range(0,len(text),width):
        draw.text((x,y+(i//width)*25),text[i:i+width],font=font,fill=fill)


def active_sheet(data, font, title_font, small):
    sheet=Image.new('RGB',(1048,112+len(data['families'])*166),'#1b222a')
    d=ImageDraw.Draw(sheet)
    d.text((24,15),'0002 · 燃料棒R5 · 15族 × 4规格活性材质',font=title_font,fill='#ede6d1')
    d.text((24,53),'原生64×64透明PNG · 135个多联模型已接图 · 外观待审／未打包安装',font=small,fill='#afbbc6')
    for col,rods in enumerate(RODS):
        d.text((282+col*192,81),SPECS[rods],font=font,fill='#bfcbd1')
    lookup={(it['family_id'],it['rods']):it for it in data['items'] if it['state']=='active'}
    for row,family in enumerate(data['families']):
        y=112+row*166
        d.rectangle((10,y,1037,y+157),fill='#252f39',outline='#52606a')
        label(d,family['name'],24,y+44,font,width=10)
        d.rectangle((24,y+130,40,y+145),fill=family['color'])
        for col,rods in enumerate(RODS):
            stamp(sheet,d,lookup[(family['id'],rods)],258+col*192,y+13)
    sheet.save(OUT/'active-contact-sheet.png')


def preview_sheet(data,font,title_font,small):
    sheet=Image.new('RGB',(1048,1050),'#1b222a')
    d=ImageDraw.Draw(sheet)
    d.text((24,16),'0002 · 燃料棒R5 · 规格与颜色预览',font=title_font,fill='#ede6d1')
    d.text((24,55),'普通／浓缩／铜骨架三族 × 单／4／8／16连',font=small,fill='#afbbc6')
    families={f['id']:f for f in data['families']}
    active={(it['family_id'],it['rods']):it for it in data['items'] if it['state']=='active'}
    for col,rods in enumerate(RODS):
        d.text((282+col*192,81),SPECS[rods],font=font,fill='#bfcbd1')
    for row,ident in enumerate(PREVIEW_IDS):
        y=112+row*166
        d.rectangle((10,y,1037,y+157),fill='#252f39',outline='#52606a')
        label(d,families[ident]['name'],24,y+45,font,width=10)
        for col,rods in enumerate(RODS):
            stamp(sheet,d,active[(ident,rods)],258+col*192,y+13)
    d.text((24,627),'15族单棒颜色总览',font=title_font,fill='#ede6d1')
    for i,family in enumerate(data['families']):
        col,row=i%5,i//5
        x,y=14+col*207,677+row*112
        d.rectangle((x,y,x+198,y+103),fill='#252f39',outline='#52606a')
        stamp(sheet,d,active[(family['id'],1)],x+5,y+8,64)
        label(d,family['name'],x+77,y+17,small,width=7)
        d.rectangle((x+78,y+78,x+93,y+91),fill=family['color'])
    d.text((24,1024),'母图与材质／供应链映射见同目录画廊及manifest.json；本轮未动已认可材质。',font=small,fill='#afbbc6')
    sheet.save(OUT/'preview.png')


def state_sheet(data,font,title_font,small):
    sheet=Image.new('RGB',(1048,112+(len(data['families'])+1)*166),'#1b222a')
    d=ImageDraw.Draw(sheet)
    d.text((24,15),'0002 · 燃料棒R5 · 单棒状态对照',font=title_font,fill='#ede6d1')
    d.text((24,53),'15族活性／乏燃料／破损单棒 · 末行为独立不合格单棒',font=small,fill='#afbbc6')
    states=('active','depleted','broken')
    for col,state in enumerate(states):
        d.text((305+col*250,81),STATES[state],font=font,fill='#bfcbd1')
    lookup={(it['family_id'],it['state']):it for it in data['items'] if it['rods']==1}
    for row,family in enumerate(data['families']):
        y=112+row*166
        d.rectangle((10,y,1037,y+157),fill='#252f39',outline='#52606a')
        label(d,family['name'],24,y+44,font,width=10)
        d.rectangle((24,y+130,40,y+145),fill=family['color'])
        for col,state in enumerate(states):
            stamp(sheet,d,lookup[(family['id'],state)],275+col*250,y+13)
    y=112+len(data['families'])*166
    rejected=next(it for it in data['items'] if it['state']=='rejected')
    d.rectangle((10,y,1037,y+157),fill='#252f39',outline='#52606a')
    label(d,'不合格燃料棒',24,y+45,font)
    stamp(sheet,d,rejected,275,y+13)
    label(d,'独立不合格状态；不属于15族的三种运行状态。',500,y+47,font,width=18)
    sheet.save(OUT/'state-contact-sheet.png')


def publish():
    data=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
    title_font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    (OUT/'index.html').write_text(HTML.replace('__DATA__',encoded),encoding='utf-8')
    active_sheet(data,font,title_font,small)
    preview_sheet(data,font,title_font,small)
    state_sheet(data,font,title_font,small)


if __name__=='__main__':
    publish()
