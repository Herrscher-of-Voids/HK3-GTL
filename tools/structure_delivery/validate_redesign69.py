"""变更#1：2026-09-28，核对69座交付与全量数据，并生成可逐页检查的联系图。"""
from pathlib import Path
import json, gzip, base64, re, datetime, collections
from urllib.parse import unquote
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01'
LOG=ROOT/'logs/structure-redesign-20260928/preview01'
entries=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
briefs=json.loads((LOG.parent/'briefs69.json').read_text(encoding='utf-8'))['briefs']
assert {e['key'].upper() for e in entries}=={e['id'] for e in briefs} and len(entries)==69
materials=set(); isolated={}; total=0; htmls=0
for e in entries:
 p=BASE/e['key']; meta=json.loads((p/'设计与检查.json').read_text(encoding='utf-8'))
 for name in ['complete.json','data.js','等轴预览.png','详细方案.html','三维评审.html',e['name']+'.nbt',e['name']+'.schem']:assert (p/name).is_file(),p/name
 raw=(p/'data.js').read_text(encoding='utf-8').split('window.HK3_PAYLOAD=',1)[1].rstrip(';\n')
 payload=json.loads(gzip.decompress(base64.b64decode(json.loads(raw))))
 assert payload['data']==meta['data'] and payload['audit']==meta['audit']
 assert sum(map(len,payload['groups']))==e['blocks']==sum(meta['audit']['palette'].values())
 w,h,d=e['size']; seen=set()
 for state,group in zip(payload['palette'],payload['groups']):
  assert len(group)==meta['audit']['palette'][state]
  for k in group:assert 0<=k<w*h*d and k not in seen;seen.add(k)
 assert len(seen)==e['blocks']
 materials.update(payload['palette']); total+=e['blocks']
 if meta['audit']['isolated_blocks']:isolated[e['key']]=meta['audit']['isolated_blocks']
for p in BASE.rglob('*.html'):
 htmls+=1
 for target in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
  if target.startswith(('http:','https:','data:','#')):continue
  assert (p.parent/unquote(target.split('#')[0])).exists(),(p,target)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',15)
sheets=[]
groups=[('工业-'+str(i//12+1),[e for e in entries if e['key'].startswith('i')][i:i+12]) for i in range(0,48,12)]
groups += [('研究所',[e for e in entries if e['key'].startswith('s')]),('奇观-1',[e for e in entries if e['key'].startswith('w')][:8]),('奇观-2',[e for e in entries if e['key'].startswith('w')][8:]),('旗舰',[e for e in entries if e['key'].startswith('h')])]
for name,group in groups:
 cols=min(3,len(group));rows=(len(group)+cols-1)//cols
 canvas=Image.new('RGB',(cols*510,rows*380+48),'#111b29');draw=ImageDraw.Draw(canvas)
 draw.text((18,10),name+' · 实体草稿01（材质投影，非游戏截图）',font=font,fill='#e5eef6')
 for i,e in enumerate(group):
  x=(i%cols)*510;y=(i//cols)*380+48
  im=Image.open(BASE/e['key']/'等轴预览.png').convert('RGB');im.thumbnail((498,292))
  canvas.paste(im,(x+(510-im.width)//2,y+(292-im.height)//2))
  title=e['key'].upper()+' '+e['title']
  draw.text((x+10,y+297),title[:25],font=font,fill='#e5eef6')
  draw.text((x+10,y+327),'×'.join(map(str,[e['size'][0],e['size'][2],e['size'][1]]))+' · '+str(e['blocks'])+' 方块',font=small,fill='#b4ced9')
 out=BASE/(name+'总览.png');canvas.save(out);sheets.append(str(out.relative_to(ROOT)))
result={'time':datetime.datetime.now().astimezone().isoformat(),'structures':len(entries),'html_pages':htmls,'blocks':total,'unique_states':len(materials),'states':sorted(materials),'isolated_blocks_for_visual_review':isolated,'sheets':sheets,'checks':['69项与总表ID完全一致','逐机数据解压、坐标唯一及范围、材料数和元数据一致','139页本地href/src依赖存在','NBT及Sponge全量回读检查见各机audit'],'not_tested':['浏览器交互','游戏成型','正式端口能力','性能实测']}
(LOG/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('states','sheets')},ensure_ascii=False))
