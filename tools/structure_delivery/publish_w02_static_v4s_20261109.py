# -*- coding: utf-8 -*-
"""同步W02取消动画的负责人决定与静态候选，不增加系统完成分。"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from html import escape
import json
from pathlib import Path
import re
import shutil
from prepare_w02_static_v4s_20261109 import ROOT,SOURCE,OUT,LOG,REPORT,save,sha
from max_structure_review import publisher


def load(p):return json.loads(p.read_text('utf8'))


def main():
    m,v,qa=[load(p) for p in (OUT/'manifest.json',OUT/'verification.json',LOG/'viewer-qa.json')]
    review=load(OUT/'静态交叠复核.json')
    assert v['animation_removed'] and qa['passed'] and qa['animation_removed'] and qa['no_idle_redraw']
    assert qa['component_transforms_unchanged'] and v['geometry_unchanged_from_v4']
    for path,digest in load(LOG/'old-v4-sha256.json').items():assert sha(ROOT/path)==digest,path
    for ext,digest in v['nbt_schem_sha256'].items():assert sha(SOURCE/'w02'/(m['name']+'.'+ext))==digest
    assert not list(OUT.glob('*.webp'))
    for file in (OUT/'index.html',OUT/'w02/三维评审.html'):
        text=file.read_text('utf8')
        assert not any(s in text for s in ('id="play"','id="time"','原案动画.webp'))
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    original={REPORT/n:(LOG/'report-baseline'/n).read_bytes() for n in ('index.html','current-summary.json')}
    assert all(p.read_bytes()==b for p,b in original.items()),'固定报告已有并行修改，需合并新基线'
    before=json.loads(original[REPORT/'current-summary.json']);data=deepcopy(before)
    receipt=dict(id='W02',candidate='Gemini半构造星核船坞V4S纯静态',status='取消动画，静态几何待修订',
        approved=False,installed=False,game_verified=False,animation_enabled=False,animation_removed=True,
        geometry_unchanged_from_v4=True,static_clearance_verified=False,size_xyz=m['size'],blocks=m['blocks'],materials=m['unique_materials'],
        overlap_pairs=review['total_pairs'],independent_intersection_pairs=9,floating_joint_review_pairs=12,
        no_idle_redraw=True,original_coordinate_transforms_verified=True,old_v4_bytes_preserved=True,
        preview=str((OUT/'index.html').relative_to(ROOT)).replace('\\','/'),
        verification=str((OUT/'verification.json').relative_to(ROOT)).replace('\\','/'),
        viewer_qa=str((LOG/'viewer-qa.json').relative_to(ROOT)).replace('\\','/'),
        overlap_review=str((OUT/'静态交叠复核.json').relative_to(ROOT)).replace('\\','/'),
        remaining='9对独立实体相交及12处翼根悬浮连接待修订；保留原几何，未进行游戏注册、成型、运行与性能验收。',updated_at=now)
    work=data['current_work']
    for key,history in [('design_candidate','design_candidate_history'),('w02_rebuild','w02_rebuild_history')]:
        work.setdefault(history,[]).append(deepcopy(work[key]));work[key]=deepcopy(receipt)
    work['state']='W02 V4S纯静态预览：已取消动画与播放入口；静态穿模已定位，待修订未部署。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w02_rebuild_review']=deepcopy(receipt);system['updated_at']=now
    data['report_updated_at']=now;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==before['overall_percent'] and data['multiblock_scope']==before['multiblock_scope']
    assert [(s['id'],s['earned'],s['possible'],s['percent']) for s in data['systems']]==[(s['id'],s['earned'],s['possible'],s['percent']) for s in before['systems']]
    assert all(s==next(b for b in before['systems'] if b['id']==s['id']) for s in data['systems'] if s['id']!='multiblocks')
    changed={'design_candidate','design_candidate_history','w02_rebuild','w02_rebuild_history','state'}
    assert all(work.get(k)==value for k,value in before['current_work'].items() if k not in changed)
    text=original[REPORT/'index.html'].decode('utf8')
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W02 V4S取消动画</p>',text,count=1);assert n==1
    note=('2026-11-09 · W02 V4S纯静态：按负责人要求移除全部演出位移、转动、播放与时间轴；39构件保持原蓝图坐标，'
          '空闲不连续重绘。取消动画没有修复静态交叠：9对独立构件实体相交、12处翼根悬浮连接待修订。'
          '几何、452万实体方块及组合NBT保持V4，旧候选按历史保留；未批准、未部署、无新增游戏实测，系统分数保持。')
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in text
    text=text.replace(anchor,anchor+'<p class="notice" id="w02-static-v4s-current">'+escape(note)+
        ' <a href="../../deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109/index.html">W02当前静态预览</a></p>',1)
    text=text.replace('id="w02-gemini-v4-current"','id="w02-gemini-v4-history"')
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    publisher().publish_transaction({REPORT/'index.html':text,REPORT/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'},original)
    rule=ROOT/'rule/当前多方块设计规则.md'
    note='''\n\n## 2026-11-09 W02取消动画，改用V4S静态候选\n\n- 负责人原话：“你先把动画删掉，我不要动画”。当前W02取消全部环转动、星笼与体素旋转、脉动、翼浮动和扫描位移，不再把原文演出作为本版待实现要求；其他奇观动画不受本次决定影响。\n- V4S移除运动数据、播放与时间轴控件及演出循环，不只是默认暂停；保留鼠标镜头旋转、缩放、剖切、玻璃和独立构件显隐。39个构件固定在原始蓝图坐标，空闲无持续重绘；旧V4完整字节保留为历史，当前评审入口切换V4S。\n- 取消动画不代表修复静态穿模。本轮按独立原始体素复核45对重叠：9对独立构件实体相交（最低翼与底座2对、翼与打印站4对、中环与母架或前炮3对），12对翼根连接须复核原案14格悬浮间隙，其余24对为设计连接或过渡，未将其全部判为材质无冲突。共享坐标及包围盒见静态交叠复核.json。\n- 本轮只移除动画与复核交叠；几何、完整边界664×508×304、4,519,823实体方块和NBT／Schematic保持V4，不移动、裁切或删实体掩盖问题。已验证六视角、完整静态取景、原坐标、镜头及显隐剖切；未批准、未部署、未进行新的实装测试，36系统分数、既定74项与批准台账不变。\n- 入口：deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109/index.html；证据：logs/w02-static-v4s-20261109/。\n'''
    rule.write_bytes(rule.read_bytes()+note.encode('utf8'))
    shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    save(LOG/'publication-verification.json',dict(passed=True,animation_removed=True,source_candidate_unchanged=True,
        scores_unchanged=36,other_systems_unchanged=35,scope_and_approval_counts_preserved=True,ascending_order=True,
        overall_percent=data['overall_percent'],html_json_synced=True,
        html_sha256=sha(REPORT/'index.html'),summary_sha256=sha(REPORT/'current-summary.json')))
    print(json.dumps(dict(passed=True,animation_removed=True,overall_percent=data['overall_percent']),ensure_ascii=False))


if __name__=='__main__':main()
