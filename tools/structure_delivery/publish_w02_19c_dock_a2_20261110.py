# -*- coding: utf-8 -*-
"""发布双炮双掌聚焦A2，保留旧候选与所有完成度分数。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json
import re
import shutil
import numpy as np
import w02_19c_dock_scene_a2_20261110 as g
from publish_w02_19c_v3_20261110 import load,sha,relative,save
from max_structure_review import publisher


def main():
    m,v,qa,aim=[load(p) for p in [g.OUT/'manifest.json',g.OUT/'verification.json',g.LOG/'viewer-qa.json',g.LOG/'aim-and-clearance.json']]
    assert v['passed'] and v['readback']['passed'] and v['no_nominal_clipping']
    assert qa['passed'] and qa['no_idle_redraw'] and qa['scene_modes_verified'] and qa['screenshots']==11
    assert aim['passed'] and len(aim['hands'])==2 and len(aim['cannons'])==2
    assert all(r['axis_miss']<1e-8 for r in aim['hands']+aim['cannons'])
    assert m['unchanged_components_from_a1']==20 and not any(m[k] for k in ['approved','animation_enabled','installed','game_verified'])
    with np.load(g.prior.LOG/'a1-original-components.npz') as a,np.load(g.LOG/'a2-original-components.npz') as b:
        for record in aim['component_checks']:
            name=record['component'];same=all(np.array_equal(a[name+'__'+k],b[name+'__'+k]) for k in ['p','states'])
            assert same==record['unchanged'],name
    report=g.ROOT/'logs/beta5-completion-audit-20261030';baseline=g.LOG/'report-baseline'
    assert not baseline.exists(),'不能覆盖更新前历史'
    baseline.mkdir()
    rule,agents=g.ROOT/'rule/当前多方块设计规则.md',g.ROOT/'AGENTS.md'
    paths=[report/'index.html',report/'current-summary.json',rule,agents]
    originals={p:p.read_bytes() for p in paths}
    for p in paths:shutil.copy2(p,baseline/p.name)
    preserved={relative(p):sha(p) for folder in g.OUT.parent.glob('W02_*19C*') if folder!=g.OUT for p in folder.rglob('*') if p.is_file()}
    save(g.LOG/'prior-candidates-preserved-sha256.json',preserved)
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    receipt=dict(id='W02',candidate='19C构造船坞双炮双掌聚焦A2',kind='静态组合外观候选',
        status='双炮与掌心炮对准同一核心；11幅视角、四条轴线及改动构件净空离线核验通过，外观待评审',
        approved=False,installed=False,game_verified=False,matrix_layout_complete=False,animation_enabled=False,
        no_idle_redraw=True,size_xyz=m['size'],blocks=m['blocks'],unchanged_components_from_a1=20,
        cannon_translation_from_a1=[0,20,60],target_blueprint=[0,211,68],detail_changes=m['detail_changes'],
        preview=relative(g.OUT/'index.html'),verification=relative(g.OUT/'verification.json'),
        viewer_qa=relative(g.LOG/'viewer-qa.json'),aim_and_clearance=relative(g.LOG/'aim-and-clearance.json'),
        previous_candidates_preserved=True,remaining='外观候选；前控与接口仅视觉示意，未注册功能完整W02，未完成游戏成型、运行与性能实测。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02 A2双炮与双掌聚焦中央核心，纯静态；其他20构件保留A1，待外观评审。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(p for p in before['systems'] if p['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02双炮双掌聚焦A2</p>',text,count=1);assert n==1
    text=text.replace('id="w02-19c-dock-a1-current"','id="w02-19c-dock-a1-history"')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note='2026-11-10 · W02组合候选A2：双炮内指核心，双手绕腕部转掌向内，光束从掌心炮口发射。原炮位内转干涉肩轮，炮座前移60格并抬高20格；其他20构件逐格保留A1。实际宽649×深493×高368，无动画。四条轴线及射线净空、改动炮手干涉、11幅视角和导出回读为离线证据；未游戏实装，不增加系统分数或批准数量。'
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-dock-a2-current">'+escape(note)+' <a href="../../'+relative(g.OUT/'index.html')+'">双炮双掌聚焦A2</a></p>',1)
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    note_rule='\n\n## 2026-11-10 W02双炮双掌聚焦A2候选\n\n- 负责人要求双炮指向中央核心、双掌朝内，并从掌心炮口发射构造线。基于A1生成独立静态候选A2；炮型保留，原位内转会碰肩轮，炮座前移60格、抬高20格后统一瞄准(0,211,68)；双掌绕腕转向核心。其余20构件逐格保持A1。\n- 候选：deliveries/W02_19C自律构造船坞_双炮双掌聚焦_A2_20261110/index.html；证据：logs/w02-19c-dock-focus-a2-20261110/。实际宽649×深493×高368，无裁切、无动画；四轴交汇、静态射线净空与改动构件干涉、11幅视角及导出回读通过。外观待评审，未游戏实装，不增加分数或批准／正式数量，旧候选保留。\n'
    publisher().publish_transaction({report/'index.html':text,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+note_rule,agents:originals[agents].decode('utf8')+note_rule},originals)
    assert all(sha(g.ROOT/p)==value for p,value in preserved.items())
    shutil.copy2(__file__,g.OUT/'生成脚本'/Path(__file__).name)
    save(g.LOG/'publication-verification.json',dict(passed=True,overall_percent=data['overall_percent'],scores_unchanged=len(data['systems']),
        prior_candidates_preserved=len(preserved),unchanged_components_per_voxel=20,ascending_order=True,html_json_synced=True,game_test=False))
    print(json.dumps(dict(passed=True,candidate='A2',size=m['size'],blocks=m['blocks'],overall_percent=data['overall_percent'])))


if __name__=='__main__':main()
