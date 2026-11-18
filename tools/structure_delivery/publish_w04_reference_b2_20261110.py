# -*- coding: utf-8 -*-
"""记录参考校准候选；保留审计历史、旧候选及全部系统分数。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
import json
import re
import shutil
import w04_reference_geometry_b2_20261110 as g
from package_w04_gemini_b1_20261110 import hashes

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(path):return json.loads(path.read_text('utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'viewer-qa.json');verification=load(g.OUT/'verification.json')
    references=load(g.OUT/'参考图清单.json');delta=load(g.LOG/'geometry-delta.json')
    assert qa['passed'] and qa['screenshots']==15 and qa['static']
    assert verification['readback']['geometry_nbt_schematic_per_block_equal']
    assert hashes(g.PRIOR)==load(g.LOG/'b1-before-hashes.json') and references['count']==44
    assert len(delta['unchanged'])==13 and len(delta['replaced'])==7
    history=g.LOG/('audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='俱利伽罗与七雷·图片校准B2',preview=str((g.OUT/'index.html').relative_to(g.ROOT)).replace('\\','/'),
        references=str((g.OUT/'参考图总览.html').relative_to(g.ROOT)).replace('\\','/'),
        reference_images=44,official_video_frames=20,player_video_frames=19,community_stills=5,
        size_xyz=manifest['size'],blocks=manifest['blocks'],static=True,approved=False,installed=False,game_verified=False,
        unchanged_components=delta['unchanged'],replaced_components=delta['replaced'],
        overlap_pairs=verification['overlap_pairs'],collision_free=False,b1_unchanged=True,
        offline_verification='logs/w04-reference-b2-20261110/viewer-qa.json',
        remaining=['外观未批准，背部及下腹遮挡细节仍待核对。','盘枢长尾、额外扣环前肢和工业连接属于场景转译。',
            '既有场景交叠照实保留，未完成无穿模验收。','未注册、未搭建游戏结构、未验证成型或运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_reference_calibration_b2']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_reference_calibration_b2']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent']
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before)
    html=(history/'index.html').read_text('utf8')
    note=f"{now} · W04图片校准B2：44张分源参考；重做7构件，其余13构件逐格保留B1。完整静态{manifest['size'][0]}×{manifest['size'][2]}×{manifest['size'][1]}，十五视角与逐格导出回读通过。遮挡细节及场景交叠待核对，未批准或游戏实装；r242与原系统分数保持。"
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=re.sub(r'<p class="notice" id="w04-reference-b2-current">.*?</p>','',html,flags=re.S)
    html=html.replace(anchor,anchor+'<p class="notice" id="w04-reference-b2-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">B2预览</a> · <a href="../../'+item['references']+'">44张参考</a></p>',1)
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04参考校准候选</p>',html,count=1);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    rules=g.ROOT/'rule/当前多方块设计规则.md';shutil.copy2(rules,history/'design-rules.txt')
    text=rules.read_text('utf8');marker='## 2026-11-10 W04俱利伽罗与七雷图片校准B2'
    if marker not in text:
        text+='\n\n'+marker+'\n\n'
        text+='- 负责人要求像19C一样上网收集俱利伽罗与涤罪七雷图片，否定没有参考的造型硬推。B1保留历史，新增独立静态B2，不自动批准或部署。\n'
        text+='- 已整理44张分源图片：20张官方教学原帧、19张玩家游戏原帧、5张社区转存图；保留来源、时间点、分辨率与哈希。不同姿态和局部不等于44个独立机位，两张低清社区图仅辅助。\n'
        text+='- 游戏界面核对基础形态为涤罪七雷·鸣、超限形态为涤罪七雷·鸣雷见；鸣雷神为技能名。B2按超限形态重做修长紫刃与镂空护手，替换原案宽三角巨剑和130格圆盘刀锷。\n'
        text+='- 重做龙首、长颈叠甲龙身、双侧红色刃状翼爪与双扣环前肢；其余十三场景构件逐格保持B1。白色长角、V形红面甲、暗色胸腹与翼爪有图片依据；盘枢长尾、额外扣环前肢和工业连接属于场景转译，遮挡处不宣称逐处复刻。\n'
        text+=f"- 实际宽{manifest['size'][0]}×深{manifest['size'][2]}×高{manifest['size'][1]}，{manifest['blocks']:,}实体；名义范围不裁切。十五视角、静态交互及NBT／Schematic逐格回读通过；{verification['overlap_pairs']}对构件交叠含预期接合与未协调干涉，未宣称无穿模。HRV绯雷红、WSV运行目标保持，无动画、未注册W04、未游戏实装，全部系统分数及批准数量不变。\n"
        text+='- 入口：deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110/index.html；参考入口同目录参考图总览.html；证据：logs/w04-reference-study-20261110/及logs/w04-reference-b2-20261110/。\n'
        rules.write_text(text,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(html,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,
        references=44,b1_unchanged=True,game_verified=False)
    save(g.LOG/'audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
