# -*- coding: utf-8 -*-
"""结构候选与建筑文件批次的固定审计同步；评分与既有范围保持原样。"""
from datetime import datetime,timezone,timedelta
from html import escape
import json
import re
from max_structure_review import ROOT,REPORT,INDEX,read,save,publisher


def publish(work,state,detail,refs,next_turn,design=None,approved_design=None,report_date=None):
    originals={p:p.read_bytes() for p in (REPORT/'current-summary.json',REPORT/'index.html')}
    history=work/'before-report';history.mkdir(exist_ok=False)
    for p,b in originals.items():(history/p.name).write_bytes(b)
    old=json.loads(originals[REPORT/'current-summary.json'].decode('utf8'))
    summary=json.loads(originals[REPORT/'current-summary.json'].decode('utf8'))
    row=next(s for s in summary['systems'] if s['id']=='multiblocks');index=read(INDEX)
    now=report_date or datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    counts=f"批准{index['approved_structure_forms']}／正式{index['formal_structure_forms']}；{index['pending_batch']['id']}为{index['pending_batch']['count']}/5。"
    row.update(coverage=state+' '+counts,updated_at=now)
    if design is not None:row['structure_design_candidate']=design;summary['current_work']['design_candidate']=design
    if approved_design is not None:
        entries=row.setdefault('approved_structure_designs',[])
        assert not any(r['id']==approved_design['id'] for r in entries)
        entries.append(approved_design);summary['current_work']['approved_structure_designs']=entries
        if row.get('structure_design_candidate',{}).get('id')==approved_design['id']:
            row['structure_design_candidate']=approved_design;summary['current_work']['design_candidate']=approved_design
    cap=row['capabilities'][3];cap['reason']+=' '+detail
    cap['evidence']=list(dict.fromkeys(cap.get('evidence',[])+refs))
    summary['current_work'].update(state=state,structure_batch=index['pending_batch'],next_turn=next_turn)
    summary['work_order']['current'][0]=state+' '+counts
    summary['report_updated_at']=now;summary['systems'].sort(key=lambda s:s['percent'])
    assert [(s['id'],s['percent'],s['earned'],s['possible']) for s in summary['systems']]==[(s['id'],s['percent'],s['earned'],s['possible']) for s in old['systems']]
    assert all(s==o for s,o in zip(summary['systems'],old['systems']) if s['id']!='multiblocks')
    assert summary['overall_percent']==old['overall_percent'] and summary['multiblock_scope']==old['multiblock_scope']
    html=originals[REPORT/'index.html'].decode('utf8');card=re.search(r'<details class="system" data-id="multiblocks".*?</details>',html,re.S).group()
    changed,n=re.subn(r'(<div class="bar">.*?</div><p>).*?(</p>)',lambda m:m[1]+escape(now+' · '+row['coverage'])+m[2],card,count=1,flags=re.S);assert n==1
    pattern=r'(<tr><td>'+re.escape(escape(cap['claim']))+r'</td><td>)(.*?)(</td><td>).*?(</td></tr>)'
    links=' · '.join('<a href="'+escape((ROOT/p).as_uri(),quote=True)+'">'+escape(p.split('/')[-1])+'</a>' for p in cap['evidence'])
    changed,n=re.subn(pattern,lambda m:m[1]+m[2]+m[3]+escape(cap['reason'])+'<p class="evidence">'+links+'</p>'+m[4],changed,count=1,flags=re.S);assert n==1
    html=html.replace(card,changed,1)
    notice='<p class="notice" id="mx-c01-design">'+escape(now+' · '+state+' '+counts)
    if design:notice+=' <a href="../../'+design['preview']+'">打开最新外观候选</a>。'
    notice+=' 系统分数及74项范围不变，建筑文件接入不代替正式Pattern或游戏验收。</p>'
    html,n=re.subn(r'<p class="notice" id="mx-c01-design">.*?</p>',lambda _:notice,html,count=1,flags=re.S);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S).group(1))==summary
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in summary['systems']]
    publisher().publish_transaction({REPORT/'current-summary.json':json.dumps(summary,ensure_ascii=False,indent=2)+'\n',REPORT/'index.html':html},originals)
    receipt=dict(passed=True,scores_unchanged=True,other_systems_unchanged=35,ascending_order=True,
        overall_percent=summary['overall_percent'],approved_forms=index['approved_structure_forms'],formal_forms=index['formal_structure_forms'],state=state)
    save(work/'report-publication.json',receipt);return receipt
