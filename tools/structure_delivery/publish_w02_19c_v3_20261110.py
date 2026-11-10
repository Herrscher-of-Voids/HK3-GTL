# -*- coding: utf-8 -*-
"""保存V2历史，发布无动画V3细化候选，不增加系统分数。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from w02_19c_geometry_v3_20261110 import ROOT,OUT,LOG
from max_structure_review import publisher


def load(path):return json.loads(path.read_text('utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):return path.relative_to(ROOT).as_posix()
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    m,v,qa,refs=[load(p) for p in [OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json',LOG/'reference-qa.json']]
    assert qa['passed'] and qa['no_idle_redraw'] and qa['screenshots']==11
    assert refs['passed'] and refs['unique_images']==60
    assert not m['animation_enabled'] and not m['game_verified'] and not m['matrix_layout_complete']
    assert len(m['geometry_delta_vs_v2'])==11 and all(r['position_difference'] for r in m['geometry_delta_vs_v2'])
    report=ROOT/'logs/beta5-completion-audit-20261030';baseline=LOG/'report-baseline'
    assert not baseline.exists(),'不覆盖本轮审计历史'
    baseline.mkdir()
    paths=[report/'index.html',report/'current-summary.json',ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']
    originals={p:p.read_bytes() for p in paths}
    for p in paths:shutil.copy2(p,baseline/p.name)
    prior=ROOT/'deliveries/W02_理之律者19C_多视角重制_V2_20261110'
    preserved={relative(p):sha(p) for p in prior.rglob('*') if p.is_file()}
    save(LOG/'v2-preserved-sha256.json',preserved)
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    receipt=dict(id='W02',candidate='普通理之律者19C多视角细化V3',kind='沿用V2姿态的独立静态造型候选',
        status='多视角细节已细化，11幅取景核对完成，外观待评审',approved=False,installed=False,
        game_verified=False,matrix_layout_complete=False,reference_fidelity_verified=False,animation_enabled=False,
        no_idle_redraw=True,size_xyz=m['size'],blocks=m['blocks'],palette_identity=m['palette_identity'],
        reference_images=60,official_reference_images=32,fan_assistance_images=28,source_videos=3,
        detail_changes=m['detail_changes'],previous_v2_preserved=True,previous_v2_rejected=False,
        preview=relative(OUT/'index.html'),verification=relative(OUT/'verification.json'),
        viewer_qa=relative(LOG/'viewer-qa.json'),reference_qa=relative(LOG/'reference-qa.json'),
        remaining='关节深度及遮挡细节仍为参考转译，未验收逐处还原；未完成W02矩阵、控制器注册、成型、运行及性能实测。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02普通理律19C沿用V2进行静态细化，V3已交付；V2保留对照，外观待评审。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(p for p in before['systems'] if p['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02理律19C静态细化V3</p>',text,count=1);assert n==1
    text=text.replace('id="w02-19c-v2-current"','id="w02-19c-v2-history"')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=('2026-11-10 · 根据负责人要求沿用60张多视角参考继续细化19C，保留V2姿态。'
        'V3增加橙罩刻纹、胸甲开孔、倒角胎纹与三辐板轮毂、分片臂甲、错落弯曲五指、背部轴系、双轨中槽及镂空节链。'
        '六个整体视角与五个局部镜头、静态不重绘、图库与导出回读通过；V2保持字节不变。'
        '外观仍待评审，未完成整座W02或实装测试，无动画，不增加任何系统分数或批准数量。')
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-v3-current">'+escape(note)+' <a href="../../'+relative(OUT/'index.html')+'">V3细节与V2对照</a></p>',1)
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    rule=ROOT/'rule/当前多方块设计规则.md';agents=ROOT/'AGENTS.md'
    note_rule='''

## 2026-11-10 W02 19C沿用V2多视角细化V3

- 负责人要求“能够再根据不同视角的图片再细化一下细节吗？”。沿用V2静态姿态与现有60张分源参考，生成独立V3；这不是否定V2，也不代表批准V3外观。
- 细化橙罩刻纹与下颌光缝、白甲分片和细长开孔、倒角轮胎与斜纹及三辐板轮毂、上臂活塞和前臂护片、错落弯曲的五指关节、背部轴系、双轨模块中槽和镂空节链。官方依据与二创辅助逐项标注，遮挡深度仍是体素转译，不宣称逐处复刻。
- V2完整文件保留并逐文件哈希核对，V3提供同角度前后对照和5个局部镜头。实际宽359×深140×高301，完整生成后取边界，不按名义矩阵裁切；六个整体视角、五个局部镜头、静态不重绘、60图加载筛选及NBT／Schematic回读均为离线证据。
- 保持普通理律、构造蓝身份、无动画。V3仍为独立造型候选，未完成整座W02矩阵，未注册控制器或实装测试；分数、既定74项及批准／正式数量保持。
- 入口：deliveries/W02_理之律者19C_多视角细化_V3_20261110/index.html；证据：logs/w02-19c-detail-v3-20261110/。固定审计同步并保留本轮更新前历史。
'''
    note_agents='''

## 2026-11-10 W02 19C静态细化V3

- 负责人要求继续按不同视角细化。当前候选为deliveries/W02_理之律者19C_多视角细化_V3_20261110/index.html；沿用V2姿态，旧V2完整保留对照，不记作被否定。
- V3细化装甲、轮毂、手指关节、背部与双轨模块，保留普通理律、构造蓝、无动画及独立候选边界。外观未批准，未进行游戏实装测试。
'''
    publisher().publish_transaction({report/'index.html':text,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+note_rule,agents:originals[agents].decode('utf8')+note_agents},originals)
    assert all(sha(ROOT/p)==value for p,value in preserved.items())
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,overall_percent=data['overall_percent'],scores_unchanged=len(data['systems']),
        other_systems_unchanged=len(data['systems'])-1,scope_and_approval_counts_preserved=True,
        v2_preserved=True,ascending_order=True,html_json_synced=True,game_test=False,report_sha256=sha(report/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],candidate_only=True),ensure_ascii=False))


if __name__=='__main__':main()
