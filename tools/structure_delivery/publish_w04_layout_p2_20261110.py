# -*- coding: utf-8 -*-
"""归档P2局部体素、构图与未协调交叠证据，保持系统分数不变。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json,re,shutil
import w04_layout_p2_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

REPORT=g.g.ROOT/'logs/beta5-completion-audit-20261030'
load=lambda p:json.loads(p.read_text('utf8'))


def main():
    manifest=load(g.OUT/'manifest.json');qa=load(g.OUT/'verification.json');geometry=load(g.LOG/'geometry-qa.json')
    assert qa['passed'] and qa['static'] and qa['screenshots']==12
    assert geometry['new_voxel_export']['geometry_nbt_schematic_per_block_equal']
    assert {p.name:hashes(p) for p in [g.P1,g.g.OUT,g.g.SWORD]}==load(g.LOG/'sources-before.json')
    assert manifest['controller_world']==[0,18,419] and len(manifest['ports_world'])==8
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    history=g.LOG/('p2-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(g.g.ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='中轴七雷与三巴纹磁环P2',preview=(g.OUT/'index.html').relative_to(g.g.ROOT).as_posix(),
        scope='静态整机摆位与新增环塔局部体素，不是完整整机体素或游戏实装',
        actual_scene_size_xyz=manifest['actual_scene_size_xyz'],sword_scale=.72,dragon_scale=1,
        new_voxel_components=10,new_voxel_blocks=manifest['new_voxel_blocks'],
        new_voxel_readback_passed=True,collision_free=qa['collision_free'],
        collision_report=geometry['collision_report'],remaining=manifest['known_issues']+['外观待负责人评审，未注册、未游戏成型或运行验收。'],
        source_models_unchanged=True,p1_retained=True,approved=False,game_verified=False,updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_layout_p2']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_layout_p2']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    count=item['collision_report']['unexpected_pairs'];width,height,depth=item['actual_scene_size_xyz']
    note=f'{now} · W04 P2：七雷72%中轴倒悬，D4龙体原位保留；新增三巴纹双轨磁环、鬼角双塔、链环、母线和螺旋电弧共10个体素构件，局部NBT／Schematic逐格回读与12张视图通过。完整布局{width}×{depth}×{height}格，未裁切。中轴刀正面遮挡部分龙首，仍有{count}组待协调交叠；底盘与鸟居仍为草模，不能记为整机无穿模或游戏实装。分数不变。'
    page=(history/'index.html').read_text('utf8');anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in page
    page=re.sub(r'<p class="notice" id="w04-p2-current">.*?</p>','',page,flags=re.S)
    page=page.replace(anchor,anchor+'<p class="notice" id="w04-p2-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">P2与遮挡对照</a></p>',1)
    page,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04 P2候选</p>',page,count=1);assert n==1
    page,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),page,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',page,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',page)==[s['id'] for s in data['systems']]
    note='\n\n## 2026-11-10 W04中轴七雷与三巴纹磁环P2候选\n\n'
    note+='- 根据负责人提供的P1评审，先制作中轴刀与环塔布局，未直接整机体素化。七雷仅在组合中缩放72%、绕Z旋转90°，刀尖锚点(0,95,235)，雷池核心(0,75,235)；D4龙体保持1:1与原位置，源模型和P1完整保留。\n'
    note+='- 新增三道三巴纹双轨磁环、双侧鬼角电容塔、链环、母线廊桥与螺旋电弧共10个真实体素构件；HRV绯雷红配色、局部NBT／Schematic逐格回读。底盘、低压塔、鸟居仍保留草模，鬼手未制作，不宣称完整整机可导出或实装。控制器位置与同面3×3周围8接口保持。\n'
    note+=f'- 预览：{item["preview"]}；证据logs/w04-layout-p2-20261110/。完整场景{width}×{depth}×{height}格，无动画、完整取景，12张视图含隐藏七雷／环塔对照。中轴刀正面遮挡龙首，仍有{count}组待协调交叠，保留原坐标见交叠记录.json；不是无穿模通过，外观待评审、未游戏实装。系统分数与批准数量不变。\n'
    for path in [g.g.ROOT/'AGENTS.md',g.g.ROOT/'rule/当前多方块设计规则.md']:
        content=path.read_text('utf8');marker='## 2026-11-10 W04中轴七雷与三巴纹磁环P2候选'
        content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:note,content,flags=re.S) if marker in content else content+note
        path.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(page,'utf8')
    receipt=dict(passed=True,history=str(history),systems=len(data['systems']),overall_percent=data['overall_percent'],
        scores_unchanged=True,html_json_synced=True,ascending_order=True,collision_free=qa['collision_free'],game_verified=False)
    save(g.LOG/'p2-audit-update.json',receipt);shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt))


if __name__=='__main__':main()
