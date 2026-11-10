# -*- coding: utf-8 -*-
"""归档P3完整真实方块离线证据，系统分数及游戏验收状态保持。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json,re,shutil
from package_w04_voxel_p3_20261110 import ROOT,OUT,LOG,SOURCES
from package_w04_gemini_b1_20261110 import save,hashes

REPORT=ROOT/'logs/beta5-completion-audit-20261030'
load=lambda p:json.loads(p.read_text('utf8'))


def main():
    manifest=load(OUT/'manifest.json');qa=load(OUT/'verification.json');geometry=load(LOG/'geometry-qa.json')
    assert qa['passed'] and qa['whole_machine_voxel'] and qa['integer_vertices'] and qa['original_review_ui']
    assert geometry['export']['readback']['geometry_nbt_schematic_per_block_equal']
    assert {p.name:hashes(p) for p in SOURCES}==load(LOG/'sources-before.json')
    assert manifest['controller_registered'] is False and manifest['game_verified'] is False
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    history=LOG/('audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='完整真实方块P3',preview=(OUT/'三维布局.html').relative_to(ROOT).as_posix(),
        scope='完整静态整数格方块、真实材质、整机NBT／Schematic与原界面预览；未游戏实装',
        actual_scene_size_xyz=manifest['actual_scene_size_xyz'],blocks=manifest['block_count'],components=manifest['components'],
        materials=manifest['palette_count'],full_machine_voxel_export=True,readback_passed=True,
        whole_integer_voxel=True,runtime_scale=[1,1,1],no_scenery_meshes=True,original_review_ui=True,
        unexpected_collision_pairs=geometry['collision_report']['unexpected_pairs'],collision_free=qa['collision_free'],
        ring_ring_and_middle_ring_chain_collision_pairs=len(geometry['collision_report']['ring_ring_or_middle_ring_chain_pairs']),
        head_obscured_percent=manifest['head_visibility']['obscured_percent'],remaining=manifest['known_issues'],
        evidence='logs/w04-voxel-p3-20261110/viewer-qa.json',source_models_unchanged=True,
        controller_registered=False,controller_placeholder_state=manifest['controller_placeholder_state'],
        approved=False,game_verified=False,updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_voxel_p3']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_voxel_p3']=deepcopy(item);data['current_work']['w04_current_preview']=item['preview'];data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    width,height,depth=item['actual_scene_size_xyz'];pending=item['unexpected_collision_pairs']
    note=f'{now} · W04 P3：底盘、雷池、储能列与三进鸟居全部真实方块化，七雷64%与X倾22°后重新量化；整机{item["blocks"]:,}块，{width}×{depth}×{height}格，完整NBT／Schematic逐格回读、真实模型贴图及原评审界面核验通过。原环—环和中环—链端交叠清零；整机仍有{pending}组待协调交叠，正面龙首仍被刀遮挡{item["head_obscured_percent"]}%。W04主控为红石块占位，八接口为外观方块；未注册、未游戏成型或运行验收。分数不变。'
    page=(history/'index.html').read_text('utf8');anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in page
    page=re.sub(r'<p class="notice" id="w04-p3-current">.*?</p>','',page,flags=re.S)
    page=page.replace(anchor,anchor+'<p class="notice" id="w04-p3-current">'+escape(note)+' <a href="../../'+item['preview']+'">整机真实方块P3</a></p>',1)
    page,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04完整真实方块P3</p>',page,count=1);assert n==1
    page,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),page,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',page,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',page)==[s['id'] for s in data['systems']]
    rule='\n\n## 2026-11-10 W04完整真实方块P3候选\n\n'
    rule+='- 负责人指出仍有普通像素／纯色草模。P3将底盘、下沉雷池、十座储能塔和三进鸟居完整生成真实方块，七雷64%并绕Z90°、X22°后重新体素化，预览全部1×1×1整数格、无运行时模型缩放／旋转、无建筑草模、无动画。龙平移(0,185,-40)，源形状保持；本候选主甲换HRV绯雷红机壳、黑石砖、深板岩及金属，D4／S1／P2历史未改。\n'
    rule+=f'- 候选{item["preview"]}；整机{item["blocks"]:,}块、29构件，实际宽{width}×深{depth}×高{height}，名义尺寸未裁切。真实完整方块模型及贴图来源、完整NBT／Schematic逐格回读和13张视图证据见logs/w04-voxel-p3-20261110/；沿用原W03／休伯利安评审界面。主控坐标(0,18,419)与同面周围8接口保持，并预留前庭下沉检修通道。\n'
    rule+=f'- 三环半径105／142／190，链内端X=±198；原环—环及中环—链端交叠清零。完整整机仍有{pending}组交叠待协调（刀与外环、电弧与中环、前庭与池沿），全部记录；正面刀／磁环仍遮挡龙首{item["head_obscured_percent"]}%，不得宣称无穿模／无遮挡。巨手未制作。\n'
    rule+='- W04正式控制器未注册，主控使用红石块明确占位，周围wonder_thunder_interface只是外观接口方块；离线候选不等于游戏成型或运行，未增加批准／正式数量或系统分数。\n'
    for file in [ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']:
        content=file.read_text('utf8');marker='## 2026-11-10 W04完整真实方块P3候选'
        content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:rule,content,flags=re.S) if marker in content else content+rule
        file.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(page,'utf8')
    receipt=dict(passed=True,history=str(history),systems=len(data['systems']),overall_percent=data['overall_percent'],
        scores_unchanged=True,html_json_synced=True,ascending_order=True,game_verified=False)
    save(LOG/'audit-update.json',receipt);shutil.copy2(Path(__file__),OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt))


if __name__=='__main__':main()
