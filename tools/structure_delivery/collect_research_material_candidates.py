# -*- coding: utf-8 -*-
"""变更#1 2026-09-28：扩展研究所材质调查，按真实方块状态解析四类来源并输出原图候选。
只读两套实例；静态模型不作为注册或成型证明；不改现有结构。
"""
from pathlib import Path
import json,re,collections,base64,io,datetime
from PIL import Image,ImageDraw,ImageFont
from material_resources import Resources

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'logs/research-labs-preview-20260928/material-expansion'
INST=Path.home()/'AppData/Roaming/PrismLauncher/instances'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    resources=[Resources(INST/n/'minecraft') for n in ('GregTech-Leisure-1.4.5.2','GregTech Leisure-增强版「巨构时代」 2.1')]
    original,enhanced=resources
    paths=set(original.index)
    paths.update(p.relative_to(original.instance/'kubejs').as_posix() for p in (original.instance/'kubejs/assets').rglob('*.json'))
    candidates={};rejected=[];accepted=[]
    for path in sorted(paths):
        m=re.fullmatch(r'assets/(gtceu|gtlcore|gtladditions|gtladd|kubejs)/blockstates/(.+)\.json',path)
        if not m:continue
        ns,key=m.groups()
        if ns=='gtceu' and not re.search('casing|coil|glass|computer|grating|filter|fusion|vent',key):continue
        block=ns+':'+key
        try:
            raw=json.loads(original.read(path));variants=raw.get('variants',{})
            # 从真实变体挑选无旋转且优先关闭的状态，不编造属性。
            options=[(k,v) for k,v in variants.items() if isinstance(v,dict) and not v.get('x',0) and not v.get('y',0)]
            options.sort(key=lambda x:('true' in x[0],x[0]))
            if not options:raise ValueError('没有可静态解析的单一无旋转变体')
            cond=options[0][0]
            candidates[block]=block+('['+cond+']' if cond else '')
        except Exception as e:rejected.append({'id':block,'reason':str(e)})
    for block in original.declarations:candidates.setdefault(block,block)
    for block,state in sorted(candidates.items()):
        try:
            mat=original.material(state)
        except Exception as e:
            rejected.append({'id':block,'reason':str(e)});continue
        try:
            other=enhanced.material(state);dual=True;reason='';same=mat['faces']==other['faces']
        except Exception as e:dual=False;reason=str(e);same=False
        accepted.append({'id':block,'state':state,'namespace':block.split(':')[0],'dual_static':dual,'same_faces':same,'enhanced_gap':reason,'material':mat})
    for r in resources:r.close()
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',14)
    sheets=[]
    for ns in sorted({r['namespace'] for r in accepted}):
        rows=[r for r in accepted if r['namespace']==ns]
        # 优先展示工业建材；其余静态完整模型仍保留于清单。
        rows.sort(key=lambda r:(not bool(re.search('casing|coil|glass|module|component|field|energy|fusion|machine|cool|compute|frame',r['id'])),not r['dual_static'],r['id']))
        show=rows[:24]
        picture=Image.new('RGB',(1440,1250),'#141d2b');draw=ImageDraw.Draw(picture)
        draw.text((20,12),ns+' · 实际材质候选（未应用结构）',font=font,fill='white')
        draw.text((20,45),'正面 / 顶面原始纹理首帧；绿：双包静态通过；橙：增强版待核对。非游戏截图。',font=font,fill='#bccad8')
        for i,row in enumerate(show):
            x=i%4*360;y=i//4*192+88
            for j,face in enumerate(('north','up')):
                im=Image.open(io.BytesIO(base64.b64decode(row['material']['faces'][face].split(',')[1]))).convert('RGBA').resize((100,100),Image.Resampling.NEAREST)
                picture.paste(im,(x+15+j*115,y),im)
            label=row['id']
            for line in range(2):draw.text((x+12,y+107+line*18),label[line*39:(line+1)*39],font=small,fill='white')
            draw.text((x+12,y+148),'双包静态通过' if row['dual_static'] else '增强版待核对',font=font,fill='#91d5aa' if row['dual_static'] else '#ffc079')
        name=ns+'-candidates.png';picture.save(OUT/name);sheets.append({'namespace':ns,'file':name,'shown':[r['state'] for r in show]})
    report={'time':datetime.datetime.now().astimezone().isoformat(),'accepted':accepted,'rejected':rejected,'sheets':sheets,
            'limits':['静态资源与模型调查，不是完整注册表或游戏成型验证','未修改结构，不将贴图存在等同于双包可用','未解析的动态KubeJS声明需另核对'],
            'unresolved_scripts':original.unresolved_scripts}
    (OUT/'catalog.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'counts':dict(collections.Counter(r['namespace'] for r in accepted)),'dual_counts':dict(collections.Counter(r['namespace'] for r in accepted if r['dual_static'])),'rejected':len(rejected),'sheets':sheets},ensure_ascii=False))
if __name__=='__main__':main()
