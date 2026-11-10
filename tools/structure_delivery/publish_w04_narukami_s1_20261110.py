# -*- coding: utf-8 -*-
"""交付独立鸣雷见候选；保存审计历史，保持系统分数与旧候选不变。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import hashlib
import json
import re
import shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import w04_narukami_s1_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(path):return json.loads(path.read_text('utf8'))


def comparison():
    background=(23,19,34)
    model=Image.open(g.OUT/'正面.png').convert('RGB');pixels=np.asarray(model)
    yy,xx=np.nonzero(np.any(pixels!=background,axis=2))
    bounds=[max(0,int(xx.min())-30),max(0,int(yy.min())-30),min(model.width,int(xx.max())+31),min(model.height,int(yy.max())+31)]
    cropped=model.crop(bounds);cropped.save(g.OUT/'完整预览.png')
    ref=Image.open(g.OUT/'轮廓取样源.png').convert('RGBA')
    canvas=Image.new('RGB',(1700,780),background);draw=ImageDraw.Draw(canvas)
    title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
    draw.text((45,22),'涤罪七雷·鸣雷见｜参考与独立静态小样 S1',font=title,fill='#f1e7f8')
    draw.text((45,82),'参考侧廓：545×320透明展示图转正；放大不增加细节',font=font,fill='#c0aecf')
    ref.thumbnail((1580,240));ref=ref.resize((1580,round(ref.height*1580/ref.width)),Image.Resampling.LANCZOS)
    canvas.paste(ref,(60,132),ref)
    draw.text((45,390),'体素小样：楔形刃厚、环形刀镡、圆截面握柄；无动画',font=font,fill='#c0aecf')
    cropped.thumbnail((1580,270));canvas.paste(cropped,((1700-cropped.width)//2,438))
    draw.text((45,727),'背面细纹与精确厚度仍为参考转译；未进行游戏实装测试',font=font,fill='#c0aecf')
    canvas.save(g.OUT/'轮廓对照.png')
    save(g.LOG/'s1-comparison-layout.json',dict(full_screenshot=[model.width,model.height],
        model_non_background_bounds=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],
        illustration_crop=bounds,all_visible_pixels_preserved=True))


def main():
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'s1-viewer-qa.json');verification=load(g.OUT/'verification.json')
    references=load(g.OUT/'参考图清单.json')
    assert qa['passed'] and qa['screenshots']==12 and qa['static']
    assert verification['readback']['geometry_nbt_schematic_per_block_equal']
    assert hashes(g.PRIOR)==load(g.LOG/'b2-before-hashes.json')
    assert references['count']==48 and references['rotation_samples']==30
    for r in references['images']:
        assert hashlib.sha256((g.OUT/'参考图'/r['file']).read_bytes()).hexdigest()==r['sha256']
    comparison()
    page=(g.OUT/'index.html').read_text('utf8')
    page=page.replace('<img src="正面.png" alt="鸣雷见独立小样正面">','<img src="轮廓对照.png" alt="鸣雷见参考与小样并排对照">')
    (g.OUT/'index.html').write_text(page,'utf8')
    history=g.LOG/('s1-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='超限涤罪七雷·鸣雷见独立静态S1',scope='只制作武器，不修改龙或整座W04',
        preview=str((g.OUT/'index.html').relative_to(g.ROOT)).replace('\\','/'),
        references=str((g.OUT/'参考图总览.html').relative_to(g.ROOT)).replace('\\','/'),
        reference_images=48,continuous_turntable_samples=30,other_video_frames=16,community_stills=2,
        size_xyz=manifest['size'],blocks=manifest['blocks'],components=5,static=True,approved=False,
        installed=False,game_verified=False,previous_b2_retained=True,previous_b2_rejected_as_current=True,
        offline_verification='logs/w04-narukami-study-20261110/s1-viewer-qa.json',
        remaining=['外观待负责人评审。','未找到官方三视尺寸图，精确刃厚、背面细纹与隐藏连接仍是参考转译。',
            '独立细节比例尚未安放到W04整机。','未注册、未在游戏搭建或验证成型／运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_narukami_independent_s1']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_narukami_independent_s1']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    html=(history/'index.html').read_text('utf8')
    note=f'{now} · W04改为逐部件制作；负责人选定超限涤罪七雷·鸣雷见。独立静态S1：48张分源参考（同一转台30角度＋16辅助原帧＋2社区图），5个部件，长{manifest["size"][0]}×刀面跨度{manifest["size"][1]}×厚{manifest["size"][2]}，{manifest["blocks"]:,}实体；十二视角、连通与开孔检查、NBT／Schematic逐格回读通过。背纹和精确厚度待核对，未批准或游戏实装；旧B2留档，系统分数不变。'
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=re.sub(r'<p class="notice" id="w04-narukami-s1-current">.*?</p>','',html,flags=re.S)
    html=html.replace(anchor,anchor+'<p class="notice" id="w04-narukami-s1-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">鸣雷见独立小样</a> · <a href="../../'+item['references']+'">48张参考</a></p>',1)
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04鸣雷见独立候选</p>',html,count=1);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    rules=g.ROOT/'rule/当前多方块设计规则.md';shutil.copy2(rules,history/'design-rules.txt')
    text=rules.read_text('utf8');marker='## 2026-11-10 W04先逐部件制作超限鸣雷见S1'
    if marker not in text:
        text+='\n\n'+marker+'\n\n'
        text+='- 负责人否定B2造型，要求数十张不同视角参考并逐个制作；当前先只做涤罪七雷，明确选择超限「涤罪七雷·鸣雷见」。不混入基础鸣，不继续同时堆龙与整机；B2历史完整保留，退出当前武器修改基线。\n'
        text+='- 独立静态S1按真实侧廓重做弯太刀、不对称镂空刃根、小型环状刀镡、黑柄白缠带及尖叶紫晶柄尾。48张参考为一轮转台30角度采样、16张跨来源辅助原帧及2张社区转存图，不宣称48个独立机位。社区透明图545×320，插值不增加精度。\n'
        text+=f'- 独立细节比例长{manifest["size"][0]}×刀面跨度{manifest["size"][1]}×最大厚度{manifest["size"][2]}，{manifest["blocks"]:,}实体、5个部件；完整包围盒生成，无名义尺寸裁切。十二视角、六向连通、刃根开孔与NBT／Schematic逐格回读通过；精确厚度、背面细纹与隐藏连接仍为转译，外观待评审。\n'
        text+='- 无动画，未安放进W04、未注册或游戏实装，不增加分数或批准数量；本轮不修改r242代码、游戏实例及W04龙体。入口：deliveries/W04_涤罪七雷鸣雷见_独立小样_S1_20261110/index.html；参考同目录参考图总览.html；证据logs/w04-narukami-study-20261110/。\n'
        rules.write_text(text,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(html,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,
        reference_images=48,b2_unchanged=True,game_verified=False)
    save(g.LOG/'s1-audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
