# -*- coding: utf-8 -*-
"""同步I34树影与W03远景实测事实，系统分数和批准数量保持。"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from html import escape
import json,re,sys
from max_structure_review import publisher
ROOT=Path(__file__).resolve().parents[2]
REVISION=int(sys.argv[1]) if len(sys.argv)>1 else 234
assert REVISION in (234,235,236,237,238)
LOG=ROOT/f'logs/i34-native-fx-r{REVISION}-20261109'

def main():
    paths=[ROOT/'logs/beta5-completion-audit-20261030/index.html',ROOT/'logs/beta5-completion-audit-20261030/current-summary.json',ROOT/'deliveries/多方块确认归档/当前归档索引.json']
    before={p:p.read_bytes() for p in paths};data=json.loads(before[paths[1]]);original=deepcopy(data);index=json.loads(before[paths[2]])
    stamp=datetime.now(timezone.utc);when=stamp.isoformat();backup=LOG/('before-report-'+stamp.strftime('%Y%m%dT%H%M%S%fZ'))
    for p,value in before.items():
        out=backup/p.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
    result=json.loads((LOG/'client-results.json').read_text(encoding='utf8'));deployment=json.loads((LOG/'deployment.json').read_text(encoding='utf8'))
    evidence=deepcopy(result);evidence.update(updated_at=when,installed_revision=deployment['revision'],jar_sha256=deployment['sha256'],evidence=f'logs/i34-native-fx-r{REVISION}-20261109/client-results.json',source='已确认I34树影V1；71948曲线顶点、15567光点、720光流，原位0.9倍')
    system=next(s for s in data['systems'] if s['id']=='multiblocks');system['i34_tree_projection_test']=deepcopy(evidence);system['updated_at']=when
    data['current_work']['i34_tree_projection_test']=deepcopy(evidence)
    data['current_work']['next_step']='I34树影真实主控、成型与工况特效补测；W03远距渲染核验。完成后返回W02 Gemini V3。'
    if result.get('fx_regression_verified',False):data['current_work']['next_step']='I34工况切换已补测；优先修复与原HTML的树影外观差异，客户端对照通过后再返回W02 Gemini V3。'
    if result.get('visual_correction_pending',False):data['current_work']['next_step']='优先复核I34金白树影、完整根干及远景遮挡修复；通过客户端对照后再返回W02 Gemini V3。'
    if result.get('visual_comparison_passed',False):data['current_work']['next_step']='I34金白树影、完整根干及远景遮挡修复已完成客户端对照；外观确认保留负责人决定，返回W02 Gemini V3原案。生产验收仍未完成。'
    entry=next(e for e in index['entries'] if e['id']=='I34');entry['tree_projection_test']=deepcopy(evidence)
    data['report_updated_at']=when;index['updated_at']=when;data['systems'].sort(key=lambda s:s['percent'])
    assert data['overall_percent']==original['overall_percent']
    assert [(s['id'],s['percent']) for s in data['systems']]==[(s['id'],s['percent']) for s in original['systems']]
    notice='2026-11-09 · I34树影补测：'+result['status']+'。'+result['remaining']+' 批准58／正式52、74项范围及36系统分数保持。'
    html=before[paths[0]].decode('utf8');marker='<p class="notice" id="i34-tree-native-current">'
    if marker in html:html,n=re.subn(r'(<p class="notice" id="i34-tree-native-current">).*?(</p>)',lambda m:m[1]+escape(notice)+m[2],html,count=1,flags=re.S);assert n==1
    else:
        anchor='<p class="notice" id="w03-c9-native-current">';assert anchor in html;html=html.replace(anchor,marker+escape(notice)+'</p>'+anchor,1)
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    html,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+when+' · I34树影实测</p>',html,count=1);assert n==1
    publisher().publish_transaction({paths[0]:html,paths[1]:json.dumps(data,ensure_ascii=False,indent=2)+'\n',paths[2]:json.dumps(index,ensure_ascii=False,indent=2)+'\n'},before)
    print(notice)
if __name__=='__main__':main()
