# -*- coding: utf-8 -*-
"""以当前实装证据更新固定入口，保留原分母、历史基线和未验差距。"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import json,re
from max_structure_review import publisher

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/w03-c9-controller-r231-20261109'

def main():
    paths=[ROOT/'logs/beta5-completion-audit-20261030/index.html',ROOT/'logs/beta5-completion-audit-20261030/current-summary.json',ROOT/'deliveries/多方块确认归档/当前归档索引.json']
    before={p:p.read_bytes() for p in paths};data=json.loads(before[paths[1]]);original=deepcopy(data);index=json.loads(before[paths[2]])
    stamp=datetime.now(timezone.utc);when=stamp.isoformat();backup=LOG/('before-report-'+stamp.strftime('%Y%m%dT%H%M%S%fZ'))
    for p,value in before.items():
        out=backup/p.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
    deployment=json.loads((LOG/'deployment.json').read_text(encoding='utf8'))
    results=json.loads((LOG/'client-results.json').read_text(encoding='utf8')) if (LOG/'client-results.json').exists() else {}
    formed=results.get('formation_verified',False);fx=results.get('formation_linked_fx_verified',False)
    status=results.get('status','r231真实GT主控已安装；空主控检查拒绝成型，完整664万格搭建测试进行中')
    evidence=dict(revision=deployment['revision'],updated_at=when,status=status,controller_integrated=True,
        registered_controller='hk3gtl:void_anchor_ring',size_xyz=[833,636,833],blocks=6642464,
        world_structure_built=results.get('world_structure_built',False),formation_verified=formed,
        formation_linked_fx_verified=fx,production_verified=False,implementation_test_passed=False,
        creative_field_test_verified=results.get('creative_field_test_verified',False),
        build_passed=True,blueprint_mask_test_passed=True,installed=True,jar_sha256=deployment['sha256'],
        negative_empty_structure_rejected=True,scope='增强版3.5真实GT控制器、完整实体、成型与创造场调试；生产/研究/毕业链路未开放。',
        evidence='logs/w03-c9-controller-r231-20261109/client-results.json',deployment='logs/w03-c9-controller-r231-20261109/deployment.json',
        remaining=results.get('remaining','完整搭建、成型、动态替换画面及破坏/停机回归仍在测试；生产、研究、毕业、多人及低端设备待验。'))
    for key in ('performance','snow_test_verified','snow_test_position','pause_verified','entity_replacement_invalidated','r233_final_regression_verified','reload_revalidation_verified','screenshots'):
        if key in results:evidence[key]=deepcopy(results[key])
    system=next(s for s in data['systems'] if s['id']=='multiblocks');system['w03_c9_controller_test']=deepcopy(evidence);system['updated_at']=when
    motion=data['current_work']['wonder_motion'];motion.update(evidence)
    system['wonder_motion_review']=deepcopy(motion)
    data['current_work']['next_step']=('C9创造场调试验收已通过，返回W02 Gemini V3原案；保留10组待协调干涉，不自动批准或实装W02。'
        if results.get('r233_final_regression_verified',False) else '完成C9真实结构与特效验收后返回W02 Gemini V3；不自动批准W02。')
    entry=next(e for e in index['entries'] if e['id']=='W03');entry.update(controller_integrated=True,world_structure_built=evidence['world_structure_built'],formation_verified=formed,formation_linked_fx_verified=fx,controller_test=evidence)
    index['updated_at']=when;data['report_updated_at']=when;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==original['overall_percent']
    assert [(s['id'],s['percent']) for s in data['systems']]==[(s['id'],s['percent']) for s in original['systems']]
    notice='2026-11-09 · W03 C9外观已批准；'+status+'。'+evidence['remaining']+' 批准58／正式52、74项范围与36系统分数保持。'
    html=before[paths[0]].decode('utf8')
    html,n=re.subn(r'(<p class="notice" id="w03-c9-native-current">).*?(</p>)',lambda m:m[1]+notice+m[2],html,count=1,flags=re.S);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+when+' · W03 C9真实主控测试</p>',html,count=1);assert n==1
    publisher().publish_transaction({paths[0]:html,paths[1]:json.dumps(data,ensure_ascii=False,indent=2)+'\n',paths[2]:json.dumps(index,ensure_ascii=False,indent=2)+'\n'},before)
    print(notice)

if __name__=='__main__':main()
