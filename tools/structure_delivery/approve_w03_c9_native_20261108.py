# -*- coding: utf-8 -*-
"""归档负责人C9批准与特效试装授权，不把渲染资源当成正式Pattern。"""
from copy import deepcopy
from datetime import datetime,timezone
import json
import re
import shutil
from build_w03_outer_c5_down_c9_20261108 import ROOT,OUT,load,save,sha
from max_structure_review import publisher


def main():
    log=ROOT/'logs/w03-c9-native-r221-20261108';index_path=ROOT/'deliveries/多方块确认归档/当前归档索引.json'
    report=ROOT/'logs/beta5-completion-audit-20261030';rule=ROOT/'rule/当前多方块设计规则.md';agents=ROOT/'AGENTS.md'
    paths=[index_path,report/'index.html',report/'current-summary.json',rule,agents]
    before={p:p.read_bytes() for p in paths};backup=log/'before-approval';backup.mkdir(exist_ok=False)
    for p,b in before.items():q=backup/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
    index=load(index_path);assert not any(e['id']=='W03' for e in index['entries'])
    quote='W03 C9版本十分的可以就用这个，先实装到游戏里面看一下特效，如果没问题的话就返回 W02 gemini版本'
    stamp=datetime.now(timezone.utc).isoformat();archive=ROOT/'deliveries/多方块确认归档/20261108_W03_C9_外观已确认'
    shutil.copytree(OUT,archive/OUT.name)
    files={str(p.relative_to(archive)).replace('\\','/'):sha(p) for p in archive.rglob('*') if p.is_file()}
    approval=dict(id='W03',version='C9',approved=True,approval_quote=quote,approved_at=stamp,
        scope='批准C9外观，并授权先做增强版3.5游戏内特效试装；GT整机成型、工艺与性能独立验收。',
        external_approval_is_authoritative=True,source_candidate_approved_field=False,archive=str(archive),files=files)
    save(archive/'确认与校验清单.json',approval);save(log/'approval-status.json',approval)
    m=load(OUT/'manifest.json')
    index['entries'].append(dict(id='W03',key='w03',candidate_key='w03',approved_version='C9',
        status='appearance_approved_fx_install_authorized',approval_quote=quote,approval_scope=approval['scope'],approved_at=stamp,
        source=str(OUT),archive=str(archive/OUT.name),external_approval_is_authoritative=True,source_candidate_approved_field=False,
        counts_as_new_machine=True,formal_resource_present=False,game_files_installed=False,native_fx_installed=False,game_verified=False,
        size_xyz=m['size'],block_count=m['blocks'],unique_materials=m['unique_materials'],controller=m['controller'],port_count=len(m['ports']),
        approved_nbt=str(archive/OUT.name/'w03'/f"{m['name']}.nbt"),approved_nbt_sha256=sha(OUT/'w03'/f"{m['name']}.nbt"),approval_manifest=str(archive/'确认与校验清单.json')))
    index['approved_structure_forms']+=1;assert index['approved_structure_forms']==58
    index['approved_undeployed_machine_ids'].append('W03');index['approved_undeployed_count']+=1
    batch=index['pending_batch'];assert batch['id']=='batch-12' and batch['count']==0
    batch['approved_machine_ids'].append('W03');batch['count']=1;batch['status']='waiting_new_approvals';batch['deployment_eligible']=False
    batch['note']='batch-12外观批准1/5；负责人另授权W03先做特效试装，正式结构接入另验。'
    index['scope']='批准58／正式52；batch-12为1/5（W03 C9），已授权游戏内特效试装，正式Pattern另验。'
    index['updated_at']=stamp
    index['_change_records'].append(dict(record=len(index['_change_records'])+1,time=stamp,reason=quote,previous_index=str(backup/index_path.relative_to(ROOT)),added='W03 C9外观批准与不可变归档',modified='批准58／正式52；仅特效试装授权，不冒充完整多方块实装。'))
    old=load(report/'current-summary.json');data=deepcopy(old);work=data['current_work']
    receipt=work['wonder_motion'];assert receipt['code']=='C9';receipt.update(approved=True,approval_quote=quote,approval_archive=str(archive),native_fx_install_authorized=True,updated_at=stamp)
    work['next_step']='先实装并实测W03 C9原生特效；通过后返回W02 Gemini V3，不自动批准W02。'
    system=next(s for s in data['systems'] if s['id']=='multiblocks');system['wonder_motion_review']=deepcopy(receipt);system['updated_at']=stamp
    system['coverage']=system['coverage'].replace('批准57／正式52','批准58／正式52')
    work['state']=str(work.get('state','')).replace('批准57／正式52','批准58／正式52')
    data['report_updated_at']=stamp;data['systems'].sort(key=lambda s:s['percent'])
    state='2026-11-08 · 负责人批准W03 C9外观，并授权先在增强版3.5试装原生特效；通过后返回W02 Gemini版本。已保存C9不可变批准归档。批准58／正式52，batch-12为1/5；仅显示特效不等于整机成型，36系统分数与74项分母保持。'
    h=before[report/'index.html'].decode('utf8');anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>'
    h=h.replace('id="w03-c9-current"','id="w03-c9-candidate-history"',1).replace(anchor,anchor+'<p class="notice" id="w03-c9-native-current">'+state+'</p>',1)
    h,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+stamp+' · W03 C9批准及特效试装</p>',h,count=1);assert n==1
    h,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),h,count=1,flags=re.S);assert n==1
    note='\n\n## 2026-11-08 W03 C9外观批准与游戏特效试装授权\n\n- 负责人原话：“'+quote+'”。C9外观正式确认；先接入增强版3.5原生特效并实测，没问题后返回W02 Gemini V3。W02仍未批准。\n- C9原候选和此前离线证据保持，批准使用外部不可变归档记录。批准58／正式52，batch-12为1/5；本轮先做完整外观的客户端GPU运动试装，不伪造GT成型、不授予研究或毕业资格。\n'
    changes={index_path:json.dumps(index,ensure_ascii=False,indent=2)+'\n',report/'index.html':h,report/'current-summary.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n',rule:before[rule].decode('utf8')+note,agents:before[agents].decode('utf8')+note}
    publisher().publish_transaction(changes,before)
    assert data['overall_percent']==old['overall_percent'] and [(s['id'],s['percent']) for s in data['systems']]==[(s['id'],s['percent']) for s in old['systems']]
    print('W03 C9批准已归档；批准58／正式52，审计分数保持。')


if __name__=='__main__':main()
