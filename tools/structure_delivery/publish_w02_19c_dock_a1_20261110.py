# -*- coding: utf-8 -*-
"""发布19C船坞组合预览，同步固定审计而不增加系统分数。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json
import re
import shutil
import numpy as np
import w02_19c_dock_scene_a1_20261110 as g
from publish_w02_19c_v3_20261110 import load,sha,relative,save
from max_structure_review import publisher


def main():
    m,v,qa,refs=[load(p) for p in [g.OUT/'manifest.json',g.OUT/'verification.json',g.LOG/'viewer-qa.json',g.LOG/'reference-qa.json']]
    assert v['passed'] and v['readback']['passed'] and v['no_nominal_clipping']
    assert qa['passed'] and qa['no_idle_redraw'] and qa['scene_modes_verified'] and qa['screenshots']==11
    assert refs['passed'] and refs['unique_images']==60
    assert m['robot_geometry_preserved'] and m['robot_components_preserved']==11 and not m['robot_scene_shared_voxels']
    assert m['industrial_scene_layout_complete'] and not any(m[k] for k in ['approved','animation_enabled','installed','game_verified','matrix_layout_complete'])
    assert m['added_components']==15 and m['size']==[649,365,493]
    with np.load(g.robot.LOG/'v6-original-components.npz') as source,np.load(g.LOG/'a1-original-components.npz') as combined:
        for key in source.files:
            expected=source[key]+g.SHIFT if key.endswith('__p') else source[key]
            assert np.array_equal(combined[key],expected),'19C原形未完整保留：'+key
    report=g.ROOT/'logs/beta5-completion-audit-20261030';baseline=g.LOG/'report-baseline'
    assert not baseline.exists(),'不覆盖本轮更新前历史'
    baseline.mkdir()
    rule,agents=g.ROOT/'rule/当前多方块设计规则.md',g.ROOT/'AGENTS.md'
    paths=[report/'index.html',report/'current-summary.json',rule,agents]
    originals={p:p.read_bytes() for p in paths}
    for p in paths:shutil.copy2(p,baseline/p.name)
    preserved={relative(p):sha(p) for folder in g.OUT.parent.glob('W02_理之律者19C_*_20261110') for p in folder.rglob('*') if p.is_file()}
    save(g.LOG/'prior-candidates-preserved-sha256.json',preserved)
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    receipt=dict(id='W02',candidate='19C自律构造船坞组合草案A1',kind='19C与自律工业矩阵的静态构图候选',
        status='U形船坞、双手半成品与前后工序已生成，11幅视角核对完成，外观待评审',
        approved=False,installed=False,game_verified=False,matrix_layout_complete=False,industrial_scene_layout_complete=True,
        animation_enabled=False,no_idle_redraw=True,reference_fidelity_verified=False,scene_inventions=True,
        size_xyz=m['size'],blocks=m['blocks'],palette_identity=m['palette_identity'],
        robot_geometry_preserved=True,robot_translation_xyz=m['robot_translation_xyz'],robot_components_preserved=11,
        added_components=15,robot_scene_shared_voxels=0,reference_images=60,official_reference_images=32,fan_assistance_images=28,
        previous_candidates_preserved=True,detail_changes=m['detail_changes'],
        preview=relative(g.OUT/'index.html'),verification=relative(g.OUT/'verification.json'),
        viewer_qa=relative(g.LOG/'viewer-qa.json'),reference_qa=relative(g.LOG/'reference-qa.json'),
        remaining='前控与接口为视觉示意；未注册机器能力、配方、研究或毕业链，未完成W02功能实现、成型、运行与性能实测。新增设施接合未做全面净空分类。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02已生成保留V6原形的19C自律构造船坞组合草案A1；静态预览待评审，未游戏实装。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(p for p in before['systems'] if p['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02 19C构造船坞组合A1</p>',text,count=1);assert n==1
    text=text.replace('id="w02-19c-v6-current"','id="w02-19c-v6-history"')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=('2026-11-10 · 负责人要求把19C与自律工业矩阵直接做成可见组合。A1保持V6全部11个构件原形，仅整体平移；'
          '新增六站U形供料船坞、双手半成品、装配床、开放维护架与链井、沿现有炮口的处理靶台、升降转运架及前控出货轨。'
          '实际宽649×深493×高365，完整生成后取边界，无动画。新增设施与19C无共享体素；原构件接合记录保留。'
          '六个整体、五个局部镜头、三种组合显隐、空闲不重绘、图库与导出逐格回读通过。'
          '组合设施为本项目创作，前控及接口仅视觉示意；外观待评审，未游戏实装，不增加分数或批准数量。')
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-dock-a1-current">'+escape(note)+' <a href="../../'+relative(g.OUT/'index.html')+'">19C与工业矩阵组合预览</a></p>',1)
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    note_rule='''

## 2026-11-10 W02 19C与自律工业矩阵组合草案A1

- 负责人在讨论19C与矩阵的联系后要求“直接弄一个”。生成独立静态组合候选A1：保留V6全部11个构件原形，仅整体平移(0,+40,-70)，不缩放或调整肢体；新增六站U形供料船坞、双手半成品、装配床、背部维护架与节链井、双炮处理靶台、升降转运架及前控出货轨。
- 组合设施与工业分工为本项目创作，不冒充官方场景。普通理律、构造蓝、无动画继续；实际宽649×深493×高365，完整生成后求边界。新增设施与19C无共享体素，旧构件接合记录保留，新增设施之间的有意接合未做全面净空分类。
- 候选：deliveries/W02_19C自律构造船坞_组合草案_A1_20261110/index.html；证据：logs/w02-19c-dock-scene-a1-20261110/。六个整体、五个局部镜头、完整／小兔／船坞三种显隐、空闲不重绘、图库及导出逐格回读为离线证据。前控与接口仅视觉示意；未注册功能完整W02或实装测试，不增加分数、既定74项或批准／正式数量。旧19C候选完整保留。
'''
    note_agents='''

## 2026-11-10 W02 19C构造船坞组合A1候选

- 负责人要求直接制作19C与自律工业矩阵组合预览。当前候选：deliveries/W02_19C自律构造船坞_组合草案_A1_20261110/index.html；V6小兔11构件只整体平移，原形保留；新增U形六站船坞、双手半成品与前后工序设施。
- 静态构图候选，非官方场景，外观待评审；无动画、无游戏实装测试。前控和接口仅视觉示意，系统分数与批准数量不变，旧19C候选完整保留。
'''
    publisher().publish_transaction({report/'index.html':text,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+note_rule,agents:originals[agents].decode('utf8')+note_agents},originals)
    assert all(sha(g.ROOT/p)==value for p,value in preserved.items())
    shutil.copy2(__file__,g.OUT/'生成脚本'/Path(__file__).name)
    save(g.LOG/'publication-verification.json',dict(passed=True,overall_percent=data['overall_percent'],scores_unchanged=len(data['systems']),
        other_systems_unchanged=len(data['systems'])-1,scope_and_approval_counts_preserved=True,
        prior_candidates_preserved=True,robot_original_npz_per_voxel_equal_after_translation=True,
        ascending_order=True,html_json_synced=True,game_test=False,report_sha256=sha(report/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],candidate_only=True),ensure_ascii=False))


if __name__=='__main__':main()
