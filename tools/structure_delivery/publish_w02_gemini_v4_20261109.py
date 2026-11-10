# -*- coding: utf-8 -*-
"""候选交付记录同步固定审计；保留各系统分数、正式资源与批准台账。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import json
from pathlib import Path
import re
import shutil
from PIL import Image
from build_w02_gemini_v4_20261109 import ROOT,OUT,LOG,save,sha
from max_structure_review import publisher

REPORT=ROOT/'logs/beta5-completion-audit-20261030'


def load(p):return json.loads(p.read_text('utf8'))


def main():
    m,v,qa=[load(p) for p in (OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json')]
    assert v['passed'] and qa['passed'] and v['readback']['geometry_nbt_schematic_per_block_equal']
    assert len(m['wings'])==12 and len(m['wells'])==4 and len(m['cables'])==8 and len(m['crowns'])==3
    for path,digest in load(LOG/'old-v3-sha256.json').items():assert sha(ROOT/path)==digest,path
    for extension,digest in v['nbt_schem_sha256'].items():assert sha(OUT/'w02'/(m['name']+'.'+extension))==digest
    for path,digest in v['resource_file_sha256'].items():assert sha(Path(path))==digest,path
    frames=[]
    for p in sorted((LOG/'frames').glob('*.png')):
        with Image.open(p) as image:frames.append(image.convert('RGB').resize((1044,690),Image.Resampling.LANCZOS))
    assert len(frames)==24
    frames[0].save(OUT/'原案动画.webp',save_all=True,append_images=frames[1:],duration=120,loop=0,quality=78,method=4)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    original={REPORT/name:(LOG/'report-baseline'/name).read_bytes() for name in ('index.html','current-summary.json')}
    assert all(path.read_bytes()==value for path,value in original.items()),'报告发生并行更新，需合并基线'
    before=json.loads(original[REPORT/'current-summary.json']);data=deepcopy(before)
    receipt=dict(id='W02',candidate='Gemini半构造星核船坞V4',status='完整原案转译与网页动画候选待审',
        approved=False,installed=False,game_verified=False,dynamic_clearance_verified=False,
        size_xyz=m['size'],blocks=m['blocks'],materials=m['unique_materials'],wells=4,wings=12,cannons=2,cables=8,crowns=3,
        source_conflicts_recorded=True,overlap_pairs=len(m['component_overlaps']),exact_geometry_roundtrip=True,
        old_v3_bytes_preserved=True,no_nominal_clipping=True,
        preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        verification=str((OUT/'verification.json').relative_to(ROOT)).replace('\\','/'),
        viewer_qa=str((LOG/'viewer-qa.json').relative_to(ROOT)).replace('\\','/'),
        remaining='原案坐标冲突与静态、动态干涉待协调；机器注册、完整成型、加工、游戏特效及性能未验收。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        if key in work:work.setdefault(history,[]).append(deepcopy(work[key]))
        work[key]=deepcopy(receipt)
    work['state']='W02 Gemini最新原案V4：完整几何与网页动画候选已交付，待审未部署。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(p for p in before['systems'] if p['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    allowed={'design_candidate','design_candidate_history','w02_rebuild','w02_rebuild_history','state'}
    assert all(work.get(k)==value for k,value in before['current_work'].items() if k not in allowed)
    description=(f'2026-11-09 · W02 Gemini新原案V4：四重力井、十二弯刀翼、双炮、半构造星核与三重星环；'
        f'实际{m["size"][0]}×{m["size"][2]}×{m["size"][1]}（宽深高），{m["blocks"]:,}实体方块。'
        '完整NBT／Schematic逐格回读、39个独立构件与六视角、网页动画及控件核验通过。'
        f'原案尺寸冲突与{len(m["component_overlaps"])}对共享体素照实保留；动态净空未通过验收。'
        '旧V3原件保留；未批准、未部署、未进行新的游戏实测，36系统分数与既定74项、批准台账不变。')
    html=original[REPORT/'index.html'].decode('utf8')
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02 Gemini V4候选</p>',html,count=1);assert n==1
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in html
    html=html.replace(anchor,anchor+'<p class="notice" id="w02-gemini-v4-current">'+escape(description)+
        ' <a href="../../deliveries/W02_Gemini_半构造星核船坞_V4_20261109/index.html">W02 V4完整预览</a></p>',1)
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT/'index.html':html,REPORT/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'},original)
    rule=ROOT/'rule/当前多方块设计规则.md';shutil.copy2(rule,LOG/'rule-before-v4.backup')
    note=f'''\n\n## 2026-11-09 W02 Gemini最新原案V4候选\n\n- 负责人提供新的半构造星核船坞原案；据此单独生成V4，旧V3全部文件哈希保持。四井代替旧V3的64座冷却塔，12翼用贝塞尔弯刀形，星核外笼为60顶点、90棱、32面的截角二十面体；两炮各12道线圈，三重冠冕和八通用接口保留。W02仍为理之律者，真理武装仅作外观参考。\n- 名义649×493×303不作裁切窗口；实际{m['size'][0]}×{m['size'][2]}×{m['size'][1]}（宽深高）、{m['blocks']:,}实体方块、{m['unique_materials']}种当前增强版3.5资源转译。原文炮长含端点差异、翼尖/角度/长度矛盾、核心分区重叠、星环顶高及八缆45度问题记录于原案参数与冲突.json，不自动压扁或截断。\n- 原文未给逐构件施工图；四井、翼根、打印站、母架及主控开口的缺省转译全部公开。八根缆连向八个不同真实笼顶点，八接口与主控背衬及五格外接线空间离线核验。\n- {len(m['component_overlaps'])}对静态构件共享体素，接合与待协调干涉未完成逐对验收。独立原坐标完整归档，三维预览保留双方完整构件；组合导出同格按后生成者取值，不用文件回读通过冒充无穿模。\n- 网页可播放中内环复合旋转、星笼及体素转动、十二翼轻浮与四站扫描；默认静止，支持暂停、拖动、分层、玻璃与独立构件显隐。动画的完整扫掠取景核验不等于动态净空或游戏性能通过。\n- 完整NBT／Schematic逐格回读、39构件完整表面重展、六视角与网页控件核验通过；尚未批准、未部署、未进行注册控制器、完整搭建、成型、加工与游戏特效实测。固定审计按完成度低到高同步，36系统原分、74项范围与批准台账保持。\n- 入口：deliveries/W02_Gemini_半构造星核船坞_V4_20261109/index.html；证据：logs/w02-gemini-v4-20261109/。\n'''
    rule.write_bytes(rule.read_bytes()+note.encode('utf8'))
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,old_v3_all_files_unchanged=True,
        scores_unchanged=36,other_systems_unchanged=35,ascending_order=True,embedded_json_matches=True,
        scope_and_approval_counts_preserved=True,overall_percent=data['overall_percent'],new_game_test=False,
        summary_sha256=sha(REPORT/'current-summary.json'),html_sha256=sha(REPORT/'index.html')))
    print(json.dumps(dict(passed=True,overall_percent=data['overall_percent'],blocks=m['blocks'],size=m['size']),ensure_ascii=False))


if __name__=='__main__':main()
