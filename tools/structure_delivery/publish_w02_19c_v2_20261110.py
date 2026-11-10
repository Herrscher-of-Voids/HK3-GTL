# -*- coding: utf-8 -*-
"""发布19C多视角静态候选，保留被否定首版与固定审计分数。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from w02_19c_geometry_v2_20261110 import ROOT,OUT,LOG
from max_structure_review import publisher


def load(path):return json.loads(path.read_text('utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def relative(path):return path.relative_to(ROOT).as_posix()


def main():
    m,v,qa,refs=[load(path) for path in [OUT/'manifest.json',OUT/'verification.json',
        LOG/'viewer-qa.json',LOG/'reference-qa.json']]
    assert qa['passed'] and qa['animation_removed'] and qa['no_idle_redraw']
    assert refs['passed'] and refs['unique_images']==60 and refs['official']==32
    assert not m['animation_enabled'] and not m['matrix_layout_complete'] and not v['game_verified']
    report=ROOT/'logs/beta5-completion-audit-20261030'
    baseline=LOG/'report-baseline'
    assert not baseline.exists(),'已经发布，不覆盖历史基线'
    baseline.mkdir()
    paths=[report/'index.html',report/'current-summary.json',ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']
    originals={path:path.read_bytes() for path in paths}
    for path in paths:shutil.copy2(path,baseline/path.name)
    preserved={}
    for name in ['W02_理之律者19C_静态造型小样_V1_20261110','W02_Gemini_半构造星核船坞_V4S_静态_20261109']:
        folder=ROOT/'deliveries'/name
        assert folder.is_dir()
        preserved.update({relative(path):sha(path) for path in folder.rglob('*') if path.is_file()})
    save(LOG/'previous-candidates-sha256.json',preserved)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    receipt=dict(id='W02',candidate='普通理之律者19C多视角重制V2',kind='独立静态造型候选，非完整工业矩阵',
        status='V1被负责人否定；60张参考与V2已交付，外观待评审',approved=False,installed=False,
        game_verified=False,matrix_layout_complete=False,reference_fidelity_verified=False,
        animation_enabled=False,no_idle_redraw=True,size_xyz=m['size'],blocks=m['blocks'],
        palette_identity=m['palette_identity'],reference_images=60,official_reference_images=32,
        fan_assistance_images=28,source_videos=3,independent_camera_positions_claimed=False,
        previous_candidate_rejected='V1参考过少、外形不像；历史文件保留，退出当前修改基线',
        preview=relative(OUT/'index.html'),references=relative(OUT/'参考图总览.html'),
        verification=relative(OUT/'verification.json'),viewer_qa=relative(LOG/'viewer-qa.json'),
        reference_qa=relative(LOG/'reference-qa.json'),
        remaining='体素转译的前臂与接合深度尚待外观评审；未完成完整矩阵布局、控制器注册、成型、运行和性能实测。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02普通理律19C首版被否定；60张分源参考与无动画V2重制交付，尚待外观评审。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    scores=lambda d:[(s['id'],s['earned'],s['possible'],s['percent']) for s in d['systems']]
    assert scores(data)==scores(before)
    assert all(s==next(b for b in before['systems'] if b['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02理律19C多视角重制V2</p>',text,count=1);assert n==1
    text=text.replace('id="w02-19c-study-current"','id="w02-19c-study-history"')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=('2026-11-10 · 负责人否定19C首版外形，要求数十张多角度参考。现已整理60张原帧：32张官方、28张二创辅助，'
          '来自3段视频，非60个独立机位。V2重做11个静态部件，六视角、图库筛选及NBT／Schematic逐格回读通过。'
          '外观还原待评审，非完整649×493×303矩阵、未实装；无动画，构造蓝#428DFF身份和WSV运行目标保持。'
          '全部系统分数、既定74项及批准／正式数量保持。')
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-v2-current">'+escape(note)+
        ' <a href="../../'+relative(OUT/'index.html')+'">V2预览与参考对照</a></p>',1)
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    rule_note='''

## 2026-11-10 W02重装小兔19C首版否定与多视角重制

- 负责人原话：“你就不能多找几十张不同角度的图片，作为参考去制作重装小兔19C吗？你这两三张制作出来的，完全不是那回事啊”。V1退出当前修改基线，原候选文件与当时离线证据保留，不能改写成外观通过。
- 新参考60张：官方《Cyberangel: ZERO Exception》12张、官方《Herrscher of Reason Guide》20张、Nibor《Project Bunny Animation and Physics Demo》28张。保留原尺寸、来源、时间点和哈希；60张涵盖角度、姿态及局部，不宣称60个独立机位。二创作者声明重建、重贴图，只辅助遮挡结构，不继承红色改色或舞蹈姿态。
- V2重做尖盾躯干、橙色罩体、肩侧轮组、曲臂、长指机械手、双浮游模块及节链，共11个完整部件。配色仍为普通理律构造蓝、白甲、深灰内构与少量橙罩；无真理形态、无十二翼、无动画。完整几何生成后求边界，实际宽357×深140×高301，不裁切、不硬凑完整矩阵尺寸。
- 六视角取景、静态不重绘、显隐／剖切、60图加载与筛选、唯一哈希、来源时间点、NBT与Schematic逐格回读均已离线核对。前臂及关节深度仍是体素转译，部件交叠如实记录，不宣称逐处还原或全部无穿模。
- V2只为独立19C静态候选，外观待负责人评审。未完成649×493×303矩阵布局，未注册或部署控制器，无游戏成型／运行／性能实测，不增加分数、正式数量或批准数量。
- 入口：deliveries/W02_理之律者19C_多视角重制_V2_20261110/index.html；证据：logs/w02-19c-reference-study-20261110/。固定审计已保存发布前历史并同步候选状态。
'''
    agents_note='''

## 2026-11-10 W02 19C多视角重制基线

- 负责人否定19C首版外形并要求数十张多角度参考，V1退出当前修改基线，历史文件保留。当前候选为deliveries/W02_理之律者19C_多视角重制_V2_20261110/index.html，尚未获外观批准。
- 已整理60张参考（32官方、28二创辅助，3段视频），不同角度／动作／局部不能宣称60个独立机位；官方校准轮廓和配色，二创只辅助遮挡结构。继续普通理律身份、构造蓝配色和无动画要求；静态19C候选不等于完整W02或实装通过。
'''
    rule=ROOT/'rule/当前多方块设计规则.md';agents=ROOT/'AGENTS.md'
    publisher().publish_transaction({report/'index.html':text,
        report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+rule_note,agents:originals[agents].decode('utf8')+agents_note},originals)
    assert all(sha(ROOT/path)==digest for path,digest in preserved.items())
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,scores_unchanged=len(data['systems']),
        other_systems_unchanged=len(data['systems'])-1,overall_percent=data['overall_percent'],
        scope_and_approval_counts_preserved=True,ascending_order=True,html_json_synced=True,
        previous_candidates_preserved=True,game_test=False,report_sha256=sha(report/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],candidate_only=True),ensure_ascii=False))


if __name__=='__main__':main()
