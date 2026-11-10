# -*- coding: utf-8 -*-
"""保存旧候选，发布静态机甲兽V4并同步固定审计，分数保持。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json
import re
import shutil
from w02_19c_geometry_v4_20261110 import ROOT,OUT,LOG,PRIOR
from publish_w02_19c_v3_20261110 import load,sha,relative,save
from max_structure_review import publisher


def main(geometry=None):
    if geometry is not None:ROOT,OUT,LOG,PRIOR=geometry.ROOT,geometry.OUT,geometry.LOG,geometry.PRIOR
    else:
        from w02_19c_geometry_v4_20261110 import ROOT,OUT,LOG,PRIOR
    m,v,qa,refs=[load(p) for p in [OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json',LOG/'reference-qa.json']]
    restored=m.get('torso_restored_from_v3',False)
    back_restored=m.get('other_components_unchanged_from_v5')==9
    version=m['display_version'];assert version in ['V4','V5','V6']
    assert v['passed'] and v['no_nominal_clipping'] and v['readback']['passed']
    assert qa['passed'] and qa['no_idle_redraw'] and qa['screenshots']==11
    assert refs['passed'] and refs['unique_images']==60
    assert not any(m[k] for k in ['animation_enabled','game_verified','matrix_layout_complete'])
    if back_restored:
        changes=m['geometry_delta_vs_v5']
        assert len(changes)==11 and sum(r['unchanged_from_v5'] for r in changes)==9
        assert {r['component'] for r in changes if not r['unchanged_from_v5']}=={'02_背部轴系与散热脊柱','07_背下方弯曲节链'}
        assert len(m['restored_components_from_v3'])==3
    elif restored:
        changes=m['geometry_delta_vs_v4']
        assert len(changes)==11 and changes[0]['position_difference']>0
        assert all(r['unchanged_from_v4'] and r['position_difference']==0 for r in changes[1:])
        assert m['other_components_unchanged_from_v4']==10
    else:assert len(m['geometry_delta_vs_v3'])==11 and all(r['position_difference'] for r in m['geometry_delta_vs_v3'])
    assert not any(r['first'].startswith('06_') or r['second'].startswith('06_') for r in m['component_overlaps'])
    report=ROOT/'logs/beta5-completion-audit-20261030';baseline=LOG/'report-baseline'
    assert not baseline.exists(),'不覆盖本轮更新前历史'
    baseline.mkdir()
    rule,agents=ROOT/'rule/当前多方块设计规则.md',ROOT/'AGENTS.md'
    paths=[report/'index.html',report/'current-summary.json',agents,rule]
    originals={p:p.read_bytes() for p in paths}
    for p in paths:shutil.copy2(p,baseline/p.name)
    preserved={relative(p):sha(p) for root in {PRIOR,ROOT/'deliveries/W02_理之律者19C_多视角重制_V2_20261110',ROOT/'deliveries/W02_理之律者19C_多视角细化_V3_20261110',ROOT/'deliveries/W02_理之律者19C_机甲兽体态_V4_20261110'} for p in root.rglob('*') if p.is_file()}
    save(LOG/'prior-candidates-preserved-sha256.json',preserved)
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    receipt=dict(id='W02',candidate='普通理之律者19C机甲兽体态V4',kind='独立静态造型候选',
        status='按机甲兽体态重做主体、曲臂与双炮，11幅静态视角核对完成，外观待评审',
        approved=False,installed=False,game_verified=False,matrix_layout_complete=False,
        reference_fidelity_verified=False,animation_enabled=False,no_idle_redraw=True,
        size_xyz=m['size'],blocks=m['blocks'],palette_identity=m['palette_identity'],
        reference_images=60,official_reference_images=32,fan_assistance_images=28,source_videos=3,
        detail_changes=m['detail_changes'],previous_v2_preserved=True,previous_v3_preserved=True,
        preview=relative(OUT/'index.html'),verification=relative(OUT/'verification.json'),
        viewer_qa=relative(LOG/'viewer-qa.json'),reference_qa=relative(LOG/'reference-qa.json'),
        remaining='比例、屈臂与双炮错角属于参考转译，外观待评审；其他构件接合与潜在干涉仍保留记录。未完成整座W02、控制器注册、成型、运行及性能实测。',
        updated_at=now)
    if restored:
        receipt.update(candidate='普通理之律者19C恢复原躯干V5',
            status='主躯干逐格恢复V3，其余十个构件逐格保持V4；11幅静态视角核对完成，外观待评审',
            previous_v4_preserved=True,torso_restored_from_v3=True,other_components_unchanged_from_v4=10)
    if back_restored:
        receipt.pop('other_components_unchanged_from_v4',None)
        receipt.update(candidate='普通理之律者19C恢复原背部节链V6',
            status='背部轴系与散热脊柱、节链逐格恢复V3，其余九个构件保持V5；11幅静态视角核对完成，外观待评审',
            previous_v5_preserved=True,restored_components_from_v3=m['restored_components_from_v3'],
            other_components_unchanged_from_v5=9)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02普通理律19C根据机甲兽反馈重做静态V4，旧V2／V3保留对照，外观待评审。'
    if restored:work['state']='W02普通理律19C仅恢复V3主躯干，V4其余十个构件不变；独立静态V5待评审，旧候选保留。'
    if back_restored:work['state']='W02普通理律19C主躯干、背部与节链恢复V3，其余构件保持；独立静态V6待评审，旧候选保留。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(p for p in before['systems'] if p['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02理律19C'+version+'</p>',text,count=1);assert n==1
    previous='v5' if back_restored else 'v4' if restored else 'v3'
    text=text.replace('id="w02-19c-'+previous+'-current"','id="w02-19c-'+previous+'-history"')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=('2026-11-10 · 负责人指出V3偏人形、手臂不够细、双炮呆板。独立静态V4缩短并前倾主体、前探下颌与前爪、背甲隆起、节链后摆；'
          '曲臂改为三段锐角护甲、收尖棱线及双活塞；双炮改为厚后舱、分叉导轨、内置炮膛和橙色后端推进罩，左右错高外撇。'
          '六个整体视角、五个局部镜头、静态空闲不重绘、60图参考与NBT／Schematic逐格回读通过；旧V2／V3文件保持不变。'
          '宽333×深327×高174，完整生成后取边界，无动画；外观未批准，非完整W02，未实装，不增加分数或批准数量。')
    if restored:
        note=('2026-11-10 · 负责人要求身体恢复之前状态、其他地方保留。独立静态V5主躯干逐格恢复V3；'
              'V4背甲、轮组、曲臂、前爪、双炮和尾链共十个构件，坐标及材质逐格一致。'
              '六个整体视角、五个局部镜头、静态空闲不重绘、参考图库和导出回读通过。'
              '宽333×深327×高174，完整生成后取边界；无动画，旧V2／V3／V4保持不变。'
              '外观待评审，非完整W02，未实装，不增加系统分数或批准数量。')
    if back_restored:
        note=('2026-11-10 · 负责人进一步要求背部轴系与散热脊柱、背下方弯曲节链也恢复之前状态。'
              '独立静态V6将这两个构件逐格恢复V3，其余九个构件逐格保持V5；主躯干仍为V3，轮组、双臂、机械手及双炮保留。'
              '六个整体视角、五个局部镜头、静态空闲不重绘、参考图库与导出逐格回读通过。'
              '实际宽333×深211×高312，完整生成后取边界，无动画；旧候选完整保留。'
              '外观待评审，非完整W02，未实装，不增加系统分数或批准数量。')
    comparison='V6与V5多视角对照' if back_restored else 'V5与V4多视角对照' if restored else 'V4与V3多视角对照'
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-'+version.lower()+'-current">'+escape(note)+' <a href="../../'+relative(OUT/'index.html')+'">'+comparison+'</a></p>',1)
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    note_rule='''

## 2026-11-10 W02 19C机甲兽体态V4

- 负责人反馈V3“身子长的像人形机甲了，应该是机甲兽的感觉；手臂线条细化不够；两杆炮看着好呆”。据此制作独立静态V4，V2／V3完整保留对照。
- 主体缩短前倾、下颌与前爪前探、背甲隆起、节链后摆；曲臂改三段锐角护甲、肘腕连接、双活塞与收尖棱线；双炮改厚后舱、分叉导轨、内置炮膛、后端橙色推进罩及左右错高外撇。机甲兽比例和姿态是参考转译，不宣称官方精确待机或逐处复刻。
- 沿用60张分源参考，保持普通理律、构造蓝及无动画。实际宽333×深327×高174，完整生成后取边界，不按名义矩阵裁切；六个整体视角、五个局部镜头、静态不重绘、参考图库及NBT／Schematic逐格回读为离线证据。双炮与其他部件无共享体素，其他接合及待审干涉如实记录，不宣称全部无穿模。
- 当前候选：deliveries/W02_理之律者19C_机甲兽体态_V4_20261110/index.html；证据：logs/w02-19c-beast-v4-20261110/。外观待评审，未完成整座W02矩阵或实装测试；系统分数、既定74项及批准／正式数量保持。
'''
    note_agents='''

## 2026-11-10 W02 19C机甲兽V4候选

- 根据负责人对人形体态、手臂与双炮的反馈，当前独立静态候选为deliveries/W02_理之律者19C_机甲兽体态_V4_20261110/index.html；V2／V3完整保留。
- V4主体前探下压，分段锐角臂甲与前爪前伸，双炮改厚后舱及分叉导轨。普通理律、构造蓝、无动画继续；外观待评审，比例姿态属参考转译，未完成整座W02或游戏实装测试。
'''
    if restored:
        note_rule='''

## 2026-11-10 W02 19C仅恢复主躯干V5

- 负责人要求“将身体返回之前的那个状态，然后其他地方保留”。仅主躯干逐格恢复V3，V4背甲、轮组、曲臂、前爪、双炮与尾链共十个构件的坐标和材质逐格保持，不顺带调整其他部分。
- 独立静态V5：deliveries/W02_理之律者19C_恢复原躯干_V5_20261110/index.html；证据：logs/w02-19c-torso-restore-v5-20261110/。V2／V3／V4完整保留对照；实际宽333×深327×高174，完整生成后取边界，无动画。六个整体和五个局部视角、图库及导出逐格回读为离线证据，外观待评审，未完成完整W02或实装测试；分数、既定74项及批准／正式数量不变。
'''
        note_agents='''

## 2026-11-10 W02 19C恢复原躯干V5候选

- 负责人要求只恢复身体、保留其他地方。当前候选：deliveries/W02_理之律者19C_恢复原躯干_V5_20261110/index.html；主躯干逐格恢复V3，其他十个构件逐格保持V4，旧候选保留。
- 保持普通理律、构造蓝及无动画；独立静态候选未批准，未进行游戏实装测试。
'''
    if back_restored:
        note_rule='''

## 2026-11-10 W02 19C恢复原背部节链V6

- 负责人进一步要求“背部的轴系和散热脊柱以及背下方弯曲的节链，也要返回之前的那个状态”。V6将02背部轴系与散热脊柱、07背下方弯曲节链逐格恢复V3；其余九个构件逐格保持V5，包含已恢复V3的主躯干和保留V4的轮组、双臂、机械手与双炮。
- 当前独立静态候选：deliveries/W02_理之律者19C_恢复原背部节链_V6_20261110/index.html；证据：logs/w02-19c-back-chain-restore-v6-20261110/。旧候选完整保留；实际宽333×深211×高312，完整生成后取边界，无动画。六个整体、五个局部视角与参考图库、导出逐格回读为离线证据，外观待评审，未完成整座W02或实装测试；分数、既定74项及批准／正式数量不变。
'''
        note_agents='''

## 2026-11-10 W02 19C恢复原背部节链V6候选

- 负责人要求背部轴系与散热脊柱、背下方弯曲节链也恢复之前状态。当前候选：deliveries/W02_理之律者19C_恢复原背部节链_V6_20261110/index.html；两处逐格恢复V3，其余九个构件保持V5，主躯干继续V3、轮组和双臂双炮继续V4。
- 普通理律、构造蓝、无动画继续；旧候选保留，外观未批准，未进行游戏实装测试。
'''
    publisher().publish_transaction({report/'index.html':text,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+note_rule,agents:originals[agents].decode('utf8')+note_agents},originals)
    assert all(sha(ROOT/p)==value for p,value in preserved.items())
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,overall_percent=data['overall_percent'],scores_unchanged=len(data['systems']),
        other_systems_unchanged=len(data['systems'])-1,scope_and_approval_counts_preserved=True,
        previous_candidates_preserved=True,ascending_order=True,html_json_synced=True,game_test=False,
        report_sha256=sha(report/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],candidate_only=True),ensure_ascii=False))


if __name__=='__main__':main()
