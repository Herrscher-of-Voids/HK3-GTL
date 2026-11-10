# -*- coding: utf-8 -*-
"""发布C9候选记录；保留旧稿、全库分数及未验收的游戏状态。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import re
import shutil
from PIL import Image
from max_structure_review import publisher
from build_w03_outer_c5_down_c9_20261108 import ROOT, OUT, LOG, BASE, load, save, sha, unpack, pack


def main():
    m=load(OUT/'manifest.json');v=load(OUT/'verification.json')
    proof=load(LOG/'continuous-clearance.json');qa=load(LOG/'viewer-qa.json')
    assert all(x['passed'] for x in [v,proof,qa,load(LOG/'geometry-partition.json')])
    assert v['readback']['geometry_nbt_schematic_per_block_equal'] and proof['pair_count']==528
    assert proof['global_surface_clearance_lower_bound']>2 and proof['moving_pair_minimum']>6
    assert m['blocks']==6642464 and m['size']==[833,636,833]
    assert all(sha(ROOT/name)==expected for name,expected in load(LOG/'preserved-files.json').items())
    with Image.open(OUT/'下移与转动演示.webp') as image:assert image.n_frames==32
    config=unpack(OUT/'w03/motion-data.js')
    config['historical_c6_conservative_shell_overlaps']=unpack(BASE/'w03/motion-data.js')['conservative_shell_overlaps']
    config['continuous_c9_clearance']=dict(passed=True,pair_count=528,minimum_gap=proof['global_surface_clearance_lower_bound'])
    pack(OUT/'w03/motion-data.js','W03_MOTION',config)
    m['removals']=load(BASE/'manifest.json')['removals']
    save(OUT/'manifest.json',m)
    payload=unpack(OUT/'w03/data.js');payload['data']['removals']=m['removals'];pack(OUT/'w03/data.js','HK3_PAYLOAD',payload)
    report=ROOT/'logs/beta5-completion-audit-20261030';rule=ROOT/'rule/当前多方块设计规则.md'
    paths=[report/'index.html',report/'current-summary.json',rule]
    originals={p:(LOG/'before'/p.relative_to(ROOT)).read_bytes() for p in paths}
    assert all(p.read_bytes()==b for p,b in originals.items()),'记录已改变，需重新合并而非覆盖'
    old=json.loads(originals[report/'current-summary.json']);data=deepcopy(old)
    work=data['current_work'];assert work['wonder_motion']['code']=='C8'
    previous=deepcopy(work['wonder_motion']);previous['follow_up_status']='C8原稿保留；C9按负责人方案修改外环运动并下移晶体与六矛。'
    work['wonder_motion_history'].append(previous)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat()
    relative=lambda p:str(p.relative_to(ROOT)).replace('\\','/')
    receipt=dict(code='C9',source='C6 via C8',status='外环C5式自转与下移净空候选待审',
        approved=False,installed=False,game_verified=False,selected_as_edit_base=True,
        discarded_design_not_reused='C7',removals_preserved_from_c8=m['removals'],
        blocks=m['blocks'],unique_materials=m['unique_materials'],size_xyz=m['size'],
        blueprint_bounds_xyz=m['blueprint_bounds_xyz'],blueprint_to_export_offset_xyz=m['blueprint_to_export_offset_xyz'],
        moving_components=32,moving_rings=5,moving_stars=24,moving_spears=6,self_rotating_crystals=24,
        outer_ring_motion='保持环面朝向，绕自身法线自转3度/秒；外24星同步',inner_four_c6_rotations_preserved=True,
        rotating_core=True,multi_axis_spherical_rotation=True,coherent_rigid_assembly=False,
        c6_component_shapes_preserved=True,c8_three_removals_preserved=True,
        crystal_shifts=m['crystal_shifts'],spear_shifts=m['spear_shifts'],
        full_cycle_seconds=360,frame_rate_limit=30,all_spears_target_core=True,
        maximum_spear_axis_miss=qa['spatial']['maximum_spear_miss'],
        source_instance_version='增强版3.5',material_resources_refreshed=True,
        nbt_schematic_and_preview_updated=True,complete_geometry_not_clipped=True,
        static_parts=['基座','八锚塔','控制器与通用接口'],
        continuous_dynamic_clearance=True,dynamic_clearance_fully_accepted=False,
        conservative_surface_clearance_lower_bound=proof['global_surface_clearance_lower_bound'],
        moving_pair_clearance_lower_bound=proof['moving_pair_minimum'],continuous_pair_checks=528,
        proof=relative(LOG/'continuous-clearance.json'),preview=relative(OUT/'index.html'),
        verification=relative(OUT/'verification.json'),
        remaining='候选预览几何的连续净空已证明；游戏内运动、投影、GT成型与增强版3.5客户端性能尚未验收。',updated_at=now)
    work['wonder_motion']=receipt
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['wonder_motion_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in old['systems']]
    assert all(s==next(t for t in old['systems'] if t['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    assert all(work[k]==value for k,value in old['current_work'].items() if k not in ['wonder_motion','wonder_motion_history'])
    assert data['overall_percent']==old['overall_percent'] and data['multiblock_scope']==old['multiblock_scope'] and data['target_instance']==old['target_instance']
    state=('2026-11-08 · W03 C9以C6/C8为基线：最外环改C5式保持环面绕自身法线自转，外24星同步；内四环保留C6独立立体翻转。'
        '9颗晶体仅沿Y下移1–175格，其他15颗保持原位；六矛沿背离核心轴线下移72–120格，持续向上锁定核心。'
        '完整结构扩为833×833×636，6,642,464格／14材质，未裁切。528对连续运动包络证明通过：动态构件间保守净空下界6.077格，含静态建筑2.279格。'
        '360秒周期、32组矩阵运动、取景和逐格回读通过；增强版3.5材质已重取，游戏内运动、成型与性能未验。C7继续弃用，既定74项、批准57／正式52、36系统分数保持。')
    html=originals[report/'index.html'].decode('utf8')
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+now+' · W03 C9外环自转与下移净空</p>',html,count=1);assert n==1
    html=html.replace('id="w03-c8-current"','id="w03-c8-history"',1)
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    link=f'<a href="../../{relative(OUT/"index.html")}">C9连续净空预览</a>'
    html=html.replace(anchor,anchor+'<p class="notice" id="w03-c9-current">'+state+' '+link+'</p>',1)
    start=html.index('<details class="system" data-id="multiblocks"');end=html.index('<div class="table-wrap">',start)
    html=html[:end]+'<p class="evidence">'+state+' '+link+'</p>'+html[end:]
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    note='''

## 2026-11-08 W03 C9：C5式外环与下移净空候选

- 负责人提出：最外圈换C5的转动方式，浓缩崩坏能晶体及亚空之矛往下避开第四层环。C9以C6经C8三处删除后的几何为基线；C7整套同步和整体抬高方案继续弃用。
- 最外环保持环面朝向，绕自身法线自转3度/秒，外24星同转；内四环继续C6独立立体翻转，核心继续独立转动。C5原稿最外环固定，本轮按负责人意图将C5内环的自法向旋转方式用于最外环，不把C5固定状态误写为旧功能。
- 保留24颗晶体原有大小、形状和X/Z位置：其中9颗沿Y下移1–175格以获得动态净空，其他15颗本就位于运动范围外；大幅下移的一颗落入中央坑上方，不穿地、不抬高其他晶体。六矛沿各自背离核心轴线下移72–120格，因此同时外扩，持续从下方向核心瞄准；不改矛形。
- 先完整生成再扩域，实际833×833×636（宽×深×高），蓝图边界[-80,0,-152]–[752,635,680]，导出偏移[80,0,152]。方块6,642,464格与14材质保持；控制器和通用接口的蓝图位置保持。C8三处删除保留，旧候选文件哈希不变。
- 按渲染器实际枢轴与旋转轴，使用完整球壳、环形圆柱、晶体包围球与六矛公转圆周证明528对关系的连续分离，包含方块角点半径：动态构件间净空下界6.077格，计入静态建筑下界2.279格；不是只抽样截图。360秒全周期、32组运动、六矛锁芯、完整取景及NBT/Schematic逐格回读通过。游戏内运动、GT成型与增强版3.5性能未验收；未批准、未部署，系统分数、74项分母和批准57／正式52不变。
- 入口：deliveries/W03_C9_C5外环下移净空修订_20261108/index.html；证据：logs/w03-c5-outer-down-c9-20261108/continuous-clearance.json及viewer-qa.json。
'''
    publisher().publish_transaction({report/'index.html':html,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',rule:originals[rule].decode('utf8')+note},originals)
    for pattern in ['*w03_outer_c5_down_c9_20261108.py','*w03_outer_c5_down_c9_20261108.mjs']:
        for path in (ROOT/'tools/structure_delivery').glob(pattern):shutil.copy2(path,OUT/'生成脚本'/path.name)
    save(LOG/'publication-verification.json',dict(passed=True,current_candidate='C9',base='C6 via C8',c7_still_rejected=True,
        all_scores_and_scope_preserved=True,other_systems_unchanged=35,current_work_other_fields_preserved=True,
        ascending_order=True,html_json_consistent=True,original_candidates_unchanged=True,
        continuous_geometry_clearance_proven=True,game_implemented=False,game_verified=False))
    print(json.dumps(dict(passed=True,active='C9',scores_unchanged=36,overall=data['overall_percent'],continuous_clearance=True),ensure_ascii=False))


if __name__=='__main__':main()
