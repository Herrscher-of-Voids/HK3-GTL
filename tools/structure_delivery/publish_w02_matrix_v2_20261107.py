# -*- coding: utf-8 -*-
"""封装W02 V2并保存历史后同步固定审计；不改变分数、范围与批准台账。"""
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import json
import re
from build_w02_matrix_v2_20261107 import ROOT,OUT,LOG
import max_structure_review as review


def publish_status(work,design,detail,state,next_turn):
    report=review.REPORT
    originals={p:p.read_bytes() for p in [report/'current-summary.json',report/'index.html']}
    before=work/'before-report';before.mkdir(exist_ok=True)
    for p,content in originals.items():
        snapshot=before/p.name
        if snapshot.exists():assert snapshot.read_bytes()==content,'审计已变化，拒绝覆盖历史基线'
        else:snapshot.write_bytes(content)
    old=json.loads(originals[report/'current-summary.json'].decode('utf8'))
    summary=json.loads(originals[report/'current-summary.json'].decode('utf8'))
    row=next(r for r in summary['systems'] if r['id']=='multiblocks')
    index=review.read(review.INDEX)
    assert (index['approved_structure_forms'],index['formal_structure_forms'],index['pending_batch']['count'])==(56,52,4)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    row.update(structure_design_candidate=design,updated_at=now,
        coverage='r216 ADD兼容已安装；W02递归构造环V2完整外观候选待审。批准56／正式52；batch-11为4/5。')
    cap=row['capabilities'][3];cap['reason']+=' '+detail
    cap['evidence']=list(dict.fromkeys(cap.get('evidence',[])+[design['receipt']]))
    summary['current_work'].update(state=state,design_candidate=design,next_turn=next_turn)
    summary['work_order']['current'][0]=state+' 批准56／正式52，batch-11为4/5；候选未接入。'
    summary['report_updated_at']=now;summary['systems'].sort(key=lambda s:s['percent'])
    assert [(r['id'],r['percent'],r['earned'],r['possible']) for r in summary['systems']]==[(r['id'],r['percent'],r['earned'],r['possible']) for r in old['systems']]
    assert all(r==o for r,o in zip(summary['systems'],old['systems']) if r['id']!='multiblocks')
    assert summary['overall_percent']==old['overall_percent'] and summary['multiblock_scope']==old['multiblock_scope']
    html=originals[report/'index.html'].decode('utf8')
    card=re.search(r'<details class="system" data-id="multiblocks".*?</details>',html,re.S).group()
    changed,n=re.subn(r'(<div class="bar">.*?</div><p>).*?(</p>)',lambda m:m[1]+escape(now+' · '+row['coverage'])+m[2],card,count=1,flags=re.S)
    assert n==1
    claim=escape(cap['claim']);pattern=r'(<tr><td>'+re.escape(claim)+r'</td><td>)(.*?)(</td><td>).*?(</td></tr>)'
    links=' · '.join('<a href="'+escape((ROOT/p).as_uri(),quote=True)+'">'+escape(p.split('/')[-1])+'</a>' for p in cap['evidence'])
    changed,n=re.subn(pattern,lambda m:m[1]+m[2]+m[3]+escape(cap['reason'])+'<p class="evidence">'+links+'</p>'+m[4],changed,count=1,flags=re.S)
    assert n==1;html=html.replace(card,changed,1)
    notice='<p class="notice" id="mx-c01-design">'+escape(now)+'：<a href="../../'+design['preview']+'">W02递归构造环V2 · 完整外观候选</a>。'+escape(state)+' 批准56／正式52，batch-11为4/5；未部署。本次仅离线结构与预览核验，既有实机证据、十周年预案和西瓜ARG保留；系统分数与74项分母不变。</p>'
    html,n=re.subn(r'<p class="notice" id="mx-c01-design">.*?</p>',lambda _:notice,html,count=1,flags=re.S);assert n==1
    html,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(summary,ensure_ascii=False).replace('<','\\u003c'),html,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',html,re.S).group(1))==summary
    assert re.findall(r'<details class="system" data-id="([^"]+)"',html)==[s['id'] for s in summary['systems']]
    review.publisher().publish_transaction({report/'current-summary.json':json.dumps(summary,ensure_ascii=False,indent=2)+'\n',report/'index.html':html},originals)
    review.save(work/'report-publication.json',dict(passed=True,ascending_order=True,scores_unchanged=True,other_systems_unchanged=35,
        overall_percent=summary['overall_percent'],approved_forms=56,formal_forms=52,batch_count=4,design=design))


if __name__=='__main__':
    baseline=review.read(LOG/'baseline.json')
    assert all(review.digest(Path(p))==sha for p,sha in baseline['unchanged_files'].items())
    review.publish_status=publish_status
    check=review.read(OUT/'verification.json')
    review.package_candidate(OUT,LOG,
        state='W02递归构造环V2已完成完整外观候选，等待负责人审阅；V1原件保留。',
        detail=f"2026-11-07生成W02递归构造环V2：649×493×303，{check['blocks']:,}实体、45种材料（普通43种）；运行WSV，HBV为最大单材。中央意识统合六院三重递归环，不对称喉口与左偏高位奇点由玻璃信息束连接。主控宽度居中、八个通用接口、六条桥内冷却联络；六邻接连通、五格接口净空、53个批准低阶四项递增、完整NBT/Schematic逐格回读与真实材质离线预览核验通过。未增加成型发奖、粒子或非欧空间逻辑；候选未批准、未部署，游戏验收与8GB目标另验，系统分数不变。",
        next_turn='先处理负责人对W02 V2的外观反馈；明确批准后才计入batch-11第五台。V1历史、批准56／正式52、74项范围和既有研究反绕过实测断点保留。')
    assert all(review.digest(Path(p))==sha for p,sha in baseline['unchanged_files'].items())
    print(json.dumps(review.read(LOG/'report-publication.json'),ensure_ascii=False))
