# -*- coding: utf-8 -*-
"""W02重建原案交付与固定审计同步；既有批准、正式资源与分数不变。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import re
import shutil
from max_structure_review import publisher

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W02_Gemini_十二翼重构船坞_V3_20261108'
LOG=ROOT/'logs/w02-bunny-dock-v3-20261108'
REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def load(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')


def main():
    m,v,qa=[load(p) for p in (OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json')]
    assert v['passed'] and qa['passed'] and v['readback']['geometry_nbt_schematic_per_block_equal']
    assert m['size']==[693,317,529] and m['blocks']==5874254
    assert (qa['info']['wings'],qa['info']['towers'],qa['info']['crowns'],qa['info']['cables'])==(12,64,3,8)
    for path,digest in load(LOG/'old-v2-sha256.json').items():assert sha(ROOT/path)==digest,path
    for ext,digest in v['nbt_schem_sha256'].items():assert sha(OUT/'w02'/(m['name']+'.'+ext))==digest
    conflicts=[p for p in m['component_overlaps'] if p['kind']=='待协调干涉']
    assert len(conflicts)==10
    save(OUT/'待协调干涉.json',dict(candidate_interference_pairs=10,planned_joint_pairs=145,
         pairs=conflicts,handling='本版原案坐标转译保留完整构件；待原作者或负责人决定修改，不自行缩短、裁切或移位。'))
    page=OUT/'index.html';text=page.read_text('utf8')
    text=text.replace('原案参数、坐标转译与冲突</a>','原案参数、坐标转译与冲突</a> · <a href="待协调干涉.json">10组待协调干涉</a>')
    text=text.replace('共有155对构件交叠记录，包含承台接合，也可能有原案构件干涉。',
        '本版坐标转译中有145组预期接合，以及10组待协调干涉：翼下打印物／瀑布与基座或冷却塔8组、两侧悬臂与外冠冕2组。')
    page.write_text(text,'utf8')
    for name in ['w02_bunny_dock_geometry_v3_20261108.py','build_w02_bunny_dock_v3_20261108.py',
                 'capture_w02_bunny_dock_v3_20261108.mjs','publish_w02_bunny_dock_v3_20261108.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    original={REPORT/n:(LOG/'report-baseline'/n).read_bytes() for n in ('index.html','current-summary.json')}
    assert all(p.read_bytes()==b for p,b in original.items()),'报告发生并行变化，需合并新基线'
    old=json.loads(original[REPORT/'current-summary.json']);data=deepcopy(old)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    receipt=dict(id='W02',candidate='Gemini重装小兔十二翼重构船坞V3',status='原案转译待审',
        approved=False,installed=False,game_verified=False,size_xyz=m['size'],blocks=m['blocks'],materials=m['unique_materials'],
        cooling_towers=64,wings=12,cannons=2,icosahedron_faces=20,compute_cables=8,crowns=3,
        source_conflicts_recorded=True,candidate_interference_pairs=10,planned_joint_pairs=145,
        exact_geometry_roundtrip=True,old_v2_bytes_preserved=True,no_nominal_clipping=True,
        preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        verification=str((OUT/'verification.json').relative_to(ROOT)).replace('\\','/'),
        viewer_qa=str((LOG/'viewer-qa.json').relative_to(ROOT)).replace('\\','/'),
        raw_components=str((LOG/'original-components.npz').relative_to(ROOT)).replace('\\','/'),
        remaining='10组几何干涉待协调；新材质与运行演出未实装，正式Pattern、生存获取、成型及性能待验。',updated_at=now)
    work=data['current_work'];work['design_candidate_history'].append(deepcopy(work['design_candidate']))
    work['design_candidate']=deepcopy(receipt)
    work['w02_rebuild_history']=[deepcopy(work['w02_rebuild'])]
    work['w02_rebuild']=deepcopy(receipt)
    work['state']='W02重建：Gemini十二翼重构船坞V3原案转译与完整离线预览已交付，待审未部署。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in old['systems']]==[
        (s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]
    assert all(s==next(o for o in old['systems'] if s['id']==o['id']) for s in data['systems'] if s['id']!='multiblocks')
    assert data['overall_percent']==old['overall_percent'] and data['multiblock_scope']==old['multiblock_scope']
    changed={'design_candidate_history','design_candidate','w02_rebuild_history','w02_rebuild','state'}
    assert all(work[k]==value for k,value in old['current_work'].items() if k not in changed)
    state=('2026-11-08 · W02重建Gemini原案V3：十二片160格浮游翼、64座六角冷却塔、双层二十面体核心、'
           '前后180格双炮、八根注入缆与三重冠冕。完整生成后实际693×529×317（宽深高），5,874,254方块、16种真实材料。'
           '完整NBT／Schematic逐格回读、真实材质与六视角控件核验通过。原案高度冲突及10组待协调干涉照实保留，'
           '145组预期接合另列，独立构件原坐标保存；不把复合文件回读一致宣称无穿模。'
           '旧W02 V2全部文件哈希不变。运行演出、新材质、正式Pattern与游戏测试未验收；本轮未批准、未部署，'
           '36系统分数及74项、批准57／正式52不变。')
    html=original[REPORT/'index.html'].decode('utf8')
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02 Gemini原案重建V3</p>',html,count=1);assert n==1
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=html.replace(anchor,anchor+'<p class="notice" id="w02-bunny-v3-current">'+escape(state)+
        ' <a href="../../deliveries/W02_Gemini_十二翼重构船坞_V3_20261108/index.html">W02 V3完整预览与冲突记录</a></p>',1)
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT/'index.html':html,REPORT/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'},original)
    rule=ROOT/'rule/当前多方块设计规则.md';shutil.copy2(rule,LOG/'rule-before-v3.backup')
    note='''

## 2026-11-08 W02 Gemini十二翼重构船坞V3原案转译

- 负责人提供Gemini重建方案：以重装小兔及真理武装的白黑金蓝机械船坞为外观母题。W02身份仍为理之律者、运行WSV；真理武装只作外观参考，不改研究、工艺或毕业职责。旧V2与批准历史保留，本轮不追加批准或部署。
- 完整保留四象限各16座六角冷却塔、8根12格直径斜注入缆、双层85格二十面体框架、45格逻辑球、前后各180格分体轨道炮、15格贯通激光通道、左右各6片160×35×12翼和380／260／140格三重冠冕。控制器位于南侧悬挑胸甲平台Y32，八个接口均通用。
- 原文未给逐翼、塔组和完整施工坐标；本版明确采用四象限4×4塔组、左右X149／499、Y125+10i及Z76+68i的翼根，六角-15／0／15／30／45／60度。中央(324,140,246)，冠冕共心(324,250,246)；空心承台四格顶底及侧壳、十字45格宽30格深槽。全部转译值与冲突公开，不宣称是原作者提供的逐格施工图。
- 原文的649×493×303不作裁切窗口；实际693×529×317（宽深高），5,874,254实体方块、16种已有真实材料，原点偏移(22,0,8)。中环顶至Y309、上扬翼超出Y260翼区；保持直径、长度、角度，不压扁或截断。
- 145组预期接合与10组待协调干涉分别记录；后者为翼下打印物／瀑布与承台或塔组8组、悬臂与外冠冕2组。独立构件原坐标存入original-components.npz；复合NBT同格依生成顺序取后者。此记录不等于已消除穿模，后续由原作者或负责人决定修改。
- 幻想材质暂用增强版3.0现有石英、黑色装甲、金块、青色玻璃与真实GT设备方块转译；不声称新增深渊钛黑／暗金机壳、CTM、动态流体或自发光光路。核心扫描、三环反转、翼悬浮、六角光柱与30格全息公式幕留作运行演出要求，本轮未实装。
- 完整NBT／Schematic逐格回读、合并表面重展、六视角与材质／玻璃／剖切控件通过离线核验；旧V2全部文件哈希不变。未操作游戏或桌面，不据此记成型、运行或性能通过；74项、批准57／正式52及36系统分数不变。
- 入口：deliveries/W02_Gemini_十二翼重构船坞_V3_20261108/index.html；证据：logs/w02-bunny-dock-v3-20261108/。W03 C5四环动态候选与既有AE实测证据保留，十周年预案仍封存。
'''
    rule.write_bytes(rule.read_bytes()+note.encode('utf8'))
    result=dict(passed=True,old_v2_all_files_unchanged=True,scores_unchanged=36,other_systems_unchanged=35,
        scope_and_approval_counts_preserved=True,overall_percent=data['overall_percent'],ascending_order=True,
        embedded_json_matches=True,candidate_interference_pairs=10,game_started=False,
        audit_summary_sha256=sha(REPORT/'current-summary.json'),audit_html_sha256=sha(REPORT/'index.html'))
    save(LOG/'publication-verification.json',result);print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
