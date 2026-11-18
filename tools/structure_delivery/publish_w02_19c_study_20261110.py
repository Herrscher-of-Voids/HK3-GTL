# -*- coding: utf-8 -*-
"""记录普通理律身份纠正、奇观配色约束及静态小样，不增加完成分。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from w02_19c_study_20261110 import ROOT,OUT,LOG
from max_structure_review import publisher


def load(path):return json.loads(path.read_text('utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    m,v,qa=[load(p) for p in [OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json']]
    assert qa['passed'] and qa['animation_removed'] and qa['no_idle_redraw']
    assert not m['matrix_layout_complete'] and not v['game_verified']
    report=ROOT/'logs/beta5-completion-audit-20261030'
    baseline=LOG/'report-baseline'
    assert not baseline.exists(),'本次发布已记录，不重复替换基线'
    baseline.mkdir()
    for n in ['index.html','current-summary.json']:shutil.copy2(report/n,baseline/n)
    for path in [ROOT/'AGENTS.md',ROOT/'rule/当前多方块设计规则.md']:
        shutil.copy2(path,LOG/(path.name+'.before-19c.backup'))
    old=ROOT/'deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109'
    hashes={str(p.relative_to(ROOT)):sha(p) for p in old.rglob('*') if p.is_file()}
    save(LOG/'old-v4s-sha256.json',hashes)
    palette=ROOT/'deliveries/已完成多方块_电压与配色逐台核对_20261029/index.html'
    source=palette.read_text('utf8');source=source[source.index('id="wonder-palette"'):]
    rows=[]
    for row in re.findall(r'<tr[^>]*>.*?</tr>',source,re.S):
        text=re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',row)).strip()
        if re.match(r'W\d{2}\b',text):rows.append(text)
    assert len(rows)==15
    assert any('W02' in r and '#428DFF' in r and 'HBV' in r for r in rows)
    save(LOG/'wonder-palette-source.json',dict(source=str(palette.relative_to(ROOT)),sha256=sha(palette),rows=rows,
        interpretation='只继承律者颜色身份，不恢复指定主机壳、材料最多或电压改档。'))
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    originals={report/n:(baseline/n).read_bytes() for n in ['index.html','current-summary.json']}
    before=json.loads(originals[report/'current-summary.json']);data=deepcopy(before)
    receipt=dict(id='W02',candidate='普通理之律者19C静态造型小样V1',kind='独立造型研究，非完整工业矩阵',
        status='普通理律身份与配色已纠正；复刻细节待核对',approved=False,installed=False,game_verified=False,
        matrix_layout_complete=False,reference_fidelity_verified=False,animation_enabled=False,
        no_idle_redraw=True,size_xyz=m['size'],blocks=m['blocks'],palette_identity=m['palette_identity'],
        previous_twelve_wing_candidate='仅保留历史，不作为当前修改基线',
        preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        verification=str((OUT/'verification.json').relative_to(ROOT)).replace('\\','/'),
        viewer_qa=str((LOG/'viewer-qa.json').relative_to(ROOT)).replace('\\','/'),
        remaining='顶部、背面及遮挡关节须完整参考图复核；未完成649×493×303矩阵布局、控制器注册、成型、运行与性能实测。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02改为普通理之律者19C静态造型研究；十二翼退出基线；W01–W15配色对应各自律者。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(b for b in before['systems'] if b['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    text=originals[report/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02普通理律19C静态小样</p>',text,count=1);assert n==1
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    note=('2026-11-10 · W02纠正为普通理之律者19C，不能与羽化后的真理之律者混用；此前十二翼没有造型依据，退出当前基线，仅保留历史。'
          '静态独立小样已导出并检查五视角；顶部、背面与遮挡处仍须参考核对，尚非完整工业矩阵。'
          'W01–W15可自由选材，但须遵守各自律者配色；W02为HBV构造蓝#428DFF，WSV运行目标保持。无新增游戏验收，全部分数保持。')
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-19c-study-current">'+escape(note)+
        ' <a href="../../deliveries/W02_理之律者19C_静态造型小样_V1_20261110/index.html">19C静态造型小样</a></p>',1)
    text=text.replace('id="w02-static-v4s-current"','id="w02-static-v4s-history"')
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    rule=ROOT/'rule/当前多方块设计规则.md';agents=ROOT/'AGENTS.md'
    rule_note='''\n\n## 2026-11-10 W02普通理之律者19C与奇观配色纠正\n\n- 负责人明确：真理之律者是理之律者羽化后的版本，本次W02只采用普通理之律者及其重装小兔19C，不使用真理之律者形态。此前“十二翼是真理之律者标志”的判断无图片依据，不再作为造型事实；旧十二翼船坞候选仅保留历史，退出当前修改基线。\n- W01–W15不强制对应电压机壳主导，但整体配色必须对应各自律者。依据：deliveries/已完成多方块_电压与配色逐台核对_20261029/index.html#wonder-palette。只继承律者颜色身份，不恢复“指定机壳必须最多单材”，不更改运行电压。\n- W02对应HBV构造蓝#428DFF，白色装甲、深色机械骨架作辅色；参考图中的小面积橙色晶核可以保留。WSV仍是其运行目标，不能据此选用WSV月华紫作理律识别色。\n- 19C首版只做独立纯静态造型小样：胸甲、分节双臂与机械手；参考正面截图顶部被截断，背面与遮挡处尚缺完整依据，须明确转译与未验收范围，不宣称逐处还原。没有顶部参考时不补造耳翼、肩炮或十二翼。\n- 本次小样不代表649×493×303工业矩阵布局完成。动画继续取消；未注册机器、未部署、无新增游戏成型或运行实测。完成度、既定74项与批准数量保持。\n- 入口：deliveries/W02_理之律者19C_静态造型小样_V1_20261110/index.html；证据：logs/w02-19c-static-20261110/。\n'''
    agents_note='''\n\n## 2026-11-10 奇观律者配色与W02形态身份（负责人最新纠正）\n\n- W01–W15可自由选用外观材料，但配色必须符合各自律者；以deliveries/已完成多方块_电压与配色逐台核对_20261029/index.html#wonder-palette为颜色身份依据。不恢复指定机壳必须主导或最多单材，也不改变运行电压。\n- W02仅对应普通理之律者及重装小兔19C，禁止混用羽化后的真理之律者造型；此前十二翼没有图片依据，退出当前修改基线，旧候选保留历史。W02外观HBV构造蓝#428DFF，运行目标仍为WSV。\n- W02保持无动画。19C独立造型小样不等于完整工业矩阵；缺少参考的顶部、背面和遮挡处必须标明待核对，不宣称逐处复刻或实装通过。\n'''
    originals[rule]=rule.read_bytes();originals[agents]=agents.read_bytes()
    publisher().publish_transaction({report/'index.html':text,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        rule:originals[rule].decode('utf8')+rule_note,agents:originals[agents].decode('utf8')+agents_note},originals)
    assert all(sha(ROOT/p)==digest for p,digest in hashes.items())
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,scores_unchanged=36,other_systems_unchanged=35,
        overall_percent=data['overall_percent'],scope_and_approval_counts_preserved=True,
        ascending_order=True,html_json_synced=True,old_v4s_preserved=True,rule_identity_corrected=True,
        current_candidate_is_study_only=True,game_test=False,report_sha256=sha(report/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],study_only=True),ensure_ascii=False))


if __name__=='__main__':main()
