# -*- coding: utf-8 -*-
"""交付独立静态龙体，保存审计历史并保持原分数与旧候选。"""
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
import w04_kurikara_d1_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(path):return json.loads(path.read_text('utf8'))


def comparison():
    canvas=Image.new('RGB',(1800,1500),(21,19,27));draw=ImageDraw.Draw(canvas)
    title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
    draw.text((38,20),'俱利伽罗 D1｜参考与静态体素小样',font=title,fill='#f1e7eb')
    draw.text((38,72),'左：官方教学局部　右：模型独立部位；角度不同，比例为参考转译',font=font,fill='#cbb7c1')
    for row,(ref,model,label) in enumerate([
        ('参考_龙首正面.jpg','龙首正面.png','龙首：长白角、灰色额冠与红色V形面甲'),
        ('参考_翼爪.jpg','翼爪近景.png','翼前肢：四片分体红刃、骨白边与白色嵌片')]):
        top=130+row*660
        draw.text((38,top),label,font=font,fill='#f1e7eb')
        for column,file in enumerate([ref,model]):
            im=Image.open(g.OUT/file).convert('RGB')
            if column:
                pixels=np.asarray(im);background=pixels[0,0]
                yy,xx=np.nonzero(np.any(pixels!=background,axis=2))
                im=im.crop((max(0,int(xx.min())-16),max(0,int(yy.min())-16),
                    min(im.width,int(xx.max())+17),min(im.height,int(yy.max())+17)))
            im.thumbnail((830,570),Image.Resampling.LANCZOS)
            canvas.paste(im,(40+column*900+(830-im.width)//2,top+50+(570-im.height)//2))
    canvas.save(g.OUT/'参考与小样对照.png')


def main():
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'viewer-qa.json')
    verification=load(g.OUT/'verification.json');references=load(g.OUT/'参考图清单.json')
    assert qa['passed'] and qa['screenshots']==14 and qa['static']
    assert verification['readback']['geometry_nbt_schematic_per_block_equal']
    assert {p.name:hashes(p) for p in [g.PRIOR,g.SWORD]}==load(g.LOG/'prior-before-hashes.json')
    assert references['count']==43 and references['official_frames']==34
    for r in references['images']:
        assert hashlib.sha256((g.OUT/'参考图'/r['file']).read_bytes()).hexdigest()==r['sha256']
    comparison()
    page=(g.OUT/'index.html').read_text('utf8')
    if '参考与小样对照.png' not in page:
        page=page.replace('<div class="grid">','<img src="参考与小样对照.png" alt="官方参考与D1模型龙首、翼爪并排对照"><div class="grid">',1)
    (g.OUT/'index.html').write_text(page,'utf8')
    history=g.LOG/('d1-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='俱利伽罗独立静态D1',scope='只制作龙本体，尚未与七雷或W04整机组合',
        preview=(g.OUT/'index.html').relative_to(g.ROOT).as_posix(),
        references=(g.OUT/'参考图总览.html').relative_to(g.ROOT).as_posix(),
        reference_images=43,official_frames=34,player_frames=8,community_stills=1,
        size_xyz=manifest['size'],blocks=manifest['blocks'],components=9,static=True,
        approved=False,installed=False,game_verified=False,previous_b2_retained=True,sword_s1_unchanged=True,
        offline_verification='logs/w04-kurikara-d1-20261110/viewer-qa.json',
        remaining=['外观待负责人评审。','无官方三视尺寸图，精确比例、背部骑乘位遮挡连接和部分翼膜背纹仍待核对。',
            '独立细节比例尚未安放进W04整机。','未注册、未在游戏搭建或验证成型／运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_kurikara_independent_d1']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_kurikara_independent_d1']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    html=(history/'index.html').read_text('utf8')
    note=f'{now} · W04俱利伽罗独立静态D1：43张分源参考（34官方教学原帧＋8玩家原帧＋1社区图，含相邻动作，非43个独立机位）；双翼前肢与一对后足、长角V甲、短躯弯颈及红脊白刺长尾。实际宽{manifest["size"][0]}×深{manifest["size"][2]}×高{manifest["size"][1]}，{manifest["blocks"]:,}实体、9个部件；14视角、静态显隐与剖切、真实凸包完整取景和NBT／Schematic逐格回读通过。比例与遮挡连接待核对，未批准或游戏实装；旧B2与鸣雷见S1未变，分数不变。'
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=re.sub(r'<p class="notice" id="w04-kurikara-d1-current">.*?</p>','',html,flags=re.S)
    html=html.replace(anchor,anchor+'<p class="notice" id="w04-kurikara-d1-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">俱利伽罗独立小样</a> · <a href="../../'+item['references']+'">43张参考</a></p>',1)
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04俱利伽罗独立候选</p>',html,count=1);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    rules=g.ROOT/'rule/当前多方块设计规则.md';shutil.copy2(rules,history/'design-rules.txt')
    text=rules.read_text('utf8');marker='## 2026-11-10 W04俱利伽罗独立静态D1候选'
    if marker not in text:
        text+='\n\n'+marker+'\n\n'
        text+='- 负责人要求下一步制作俱利伽罗；沿用逐个部件制作，先只做独立龙体，不与鸣雷见S1或W04整机合并，不加动画。旧B2与七雷S1原文件完整保留。\n'
        text+='- 当前D1按43张有效参考重做：34张官方教学原帧、8张玩家游戏原帧及1张社区转存图，含同镜头相邻动作，局部裁图不重复计数，不宣称43个独立机位。采用长白角与V形红甲、暗灰颈腹、两侧刃状翼前肢、一对收拢后足、短躯弯颈及红脊白刺长尾。\n'
        text+=f'- 实际宽{manifest["size"][0]}×深{manifest["size"][2]}×高{manifest["size"][1]}，{manifest["blocks"]:,}实体、9部件；完整生成后求边界，未按W04名义尺寸裁切。14视角、真实凸包完整取景、静态控件、连通及NBT／Schematic逐格回读通过。精确比例、背部遮挡连接与翼膜背纹仍为参考转译，外观待评审。\n'
        text+='- 本轮未注册、部署或进行游戏搭建、成型与运行验收；不增加系统分数或批准数量。预览：deliveries/W04_俱利伽罗_独立静态小样_D1_20261110/index.html；参考同目录参考图总览.html；离线证据logs/w04-kurikara-d1-20261110/。\n'
        rules.write_text(text,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(html,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,
        reference_images=43,b2_unchanged=True,sword_s1_unchanged=True,game_verified=False)
    save(g.LOG/'d1-audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
