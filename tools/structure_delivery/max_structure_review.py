# -*- coding: utf-8 -*-
"""MAX结构的外部批准归档与固定审计更新；候选原件和既有分数保持不变。"""
from html.parser import HTMLParser
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'logs/beta5-completion-audit-20261030'
INDEX=ROOT/'deliveries/多方块确认归档/当前归档索引.json'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p,data):
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def publisher():
    spec=importlib.util.spec_from_file_location('audit_publisher',ROOT/'logs/review-completion-20261104/publish_report.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def approve(out,work,quote):
    manifest=read(out/'manifest.json');check=read(out/'verification.json');qa=read(out/'viewer-qa.json')
    assert qa['passed'] and check['readback']['geometry_nbt_schematic_per_block_equal']
    assert not manifest['installed'] and not qa['desktop_used']
    key=manifest['key'];identity=key.upper();version=manifest['candidate_version']
    original=INDEX.read_bytes();index=json.loads(original.decode('utf-8'))
    assert not any(e['id']==identity for e in index['entries']), '已批准，禁止重复计数'
    assert index['pending_batch']['count']<5, '本批已满五台，须先接入再开始下一批'
    before=work/'before-approval';before.mkdir(parents=True,exist_ok=False)
    (before/INDEX.name).write_bytes(original)
    snapshot=INDEX.parent/f'20261107_{identity}_{version}_外观已确认'
    snapshot.mkdir(exist_ok=False)
    archived=snapshot/out.name;shutil.copytree(out,archived)
    files={p.relative_to(snapshot).as_posix():digest(p) for p in sorted(snapshot.rglob('*')) if p.is_file()}
    approval=dict(quote=quote,decision_date='2026-11-07',recorded_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        scope='仅确认该版本建筑外观；正式名称、工艺、Pattern、生存获取和游戏运行另验。')
    approval_manifest=snapshot/'确认与校验清单.json'
    save(approval_manifest,dict(id=identity,internal_requirement_id=key.startswith('mx-'),version=version,approval=approval,
        approved=True,installed=False,game_verified=False,external_approval_is_authoritative=True,
        source_candidate_approved_field=manifest['approved'],source=str(out),files=files,
        source_zip=str(out.with_suffix('.zip')),source_zip_sha256=digest(out.with_suffix('.zip')),
        readback=check['readback']))
    bundle=snapshot.with_suffix('.zip')
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(snapshot.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(snapshot).as_posix())
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for p in snapshot.rglob('*'):
            if p.is_file():assert z.read(p.relative_to(snapshot).as_posix())==p.read_bytes()
    nbt=archived/key/f'{manifest["name"]}.nbt';nbt_sha=digest(nbt)
    assert nbt_sha==check['nbt_schem_sha256']['nbt']
    archive_sha=digest(bundle)
    index['entries'].append(dict(id=identity,key=key,candidate_key=key,internal_requirement_id=key.startswith('mx-'),
        approved_version=version,status='appearance_approved_pending_batch',approval_quote=quote,
        approval_scope=approval['scope'],approved_at=approval['recorded_at'],source=str(out),archive=str(archived),
        external_approval_is_authoritative=True,source_candidate_approved_field=manifest['approved'],
        counts_as_new_machine=True,formal_resource_present=False,game_files_installed=False,game_verified=False,
        size_xyz=manifest['size'],block_count=check['blocks'],unique_materials=check['unique_materials'],
        ordinary_materials=check['unique_materials']-2,port_count=len(manifest['ports']),controller=manifest['controller'],
        target_voltage_appearance=manifest.get('appearance_voltage',manifest.get('target_voltage','MAX')),
        target_voltage=manifest.get('target_voltage','MAX'),approved_nbt=str(nbt),approved_nbt_sha256=nbt_sha,nbt_sha256=nbt_sha,
        approval_manifest=str(approval_manifest),archive_zip=str(bundle),archive_zip_sha256=archive_sha))
    index['approved_structure_forms']+=1
    index['approved_undeployed_machine_ids'].append(identity);index['approved_undeployed_count']+=1
    batch=index['pending_batch'];batch['approved_machine_ids'].append(identity);batch['count']+=1
    assert batch['count']==len(batch['approved_machine_ids'])==index['approved_undeployed_count']
    # W02作为第五台进入批次；批准原件与游戏接入仍分别记账。
    batch['deployment_eligible']=batch['count']==batch['required']
    batch['status']='ready_for_deployment' if batch['deployment_eligible'] else 'waiting_new_approvals'
    batch['note']=f"本批已有{batch['count']}台外观确认；{batch['count']}/5，未部署。"
    index['updated_at']=approval['recorded_at']
    index['scope']=f"既有批准原件保留；共{index['approved_structure_forms']}批准形态、{index['formal_structure_forms']}正式结构资源。batch-11为{batch['count']}/5；游戏验收另计，I37留最后。"
    index['batch_rule']=f"每累计5台新批准未接入结构按确认归档接入；当前batch-11为{batch['count']}/5。客户端测试等待负责人明确恢复。"
    index['latest_approval_snapshot']=dict(snapshot=str(snapshot),zip=str(bundle),zip_sha256=archive_sha)
    index['_change_records'].append(dict(record=len(index['_change_records'])+1,time=approval['recorded_at'],
        reason=f'负责人明确认可{identity} {version}并要求继续下一台。',previous_index=str(before/INDEX.name),
        added=f'{identity}外观批准与不可变归档',modified='仅批准台账，未部署实例。'))
    publisher().publish_transaction({INDEX:json.dumps(index,ensure_ascii=False,indent=2)+'\n'},{INDEX:original})
    receipt=dict(passed=True,approved=True,installed=False,game_verified=False,system_completed=False,
        id=identity,version=version,blocks=check['blocks'],materials=check['unique_materials'],size_xyz=manifest['size'],
        preview=(out/'index.html').relative_to(ROOT).as_posix(),title=manifest['title'],
        archive=str(snapshot),zip=str(bundle),zip_sha256=archive_sha,approval=approval,
        batch=batch['id'],batch_count=batch['count'],receipt=(work/'approval-status.json').relative_to(ROOT).as_posix())
    save(work/'approval-status.json',receipt)
    return receipt


def publish_status(work,design,detail,state,next_turn):
    originals={p:p.read_bytes() for p in [REPORT/'current-summary.json',REPORT/'index.html']}
    before=work/'before-report';before.mkdir(parents=True,exist_ok=False)
    for p,b in originals.items():(before/p.name).write_bytes(b)
    old=json.loads(originals[REPORT/'current-summary.json'].decode('utf-8'))
    summary=json.loads(originals[REPORT/'current-summary.json'].decode('utf-8'))
    row=next(r for r in summary['systems'] if r['id']=='multiblocks')
    index=read(INDEX);count=index['pending_batch']['count']
    approved=row.get('approved_structure_designs',[])
    if design['approved'] and not any(r['id']==design['id'] for r in approved):approved.append(design)
    row['approved_structure_designs']=approved;row['structure_design_candidate']=design
    row['coverage']=f'r216 ADD兼容已安装；{state} 当前批准批次{count}/5，正式资源52份。'
    cap=row['capabilities'][3];old_reason=cap['reason'];cap['reason']+=' '+detail
    cap.setdefault('evidence',[]).append(design['receipt'])
    summary['current_work'].update(state=state,design_candidate=design,approved_structure_designs=approved,next_turn=next_turn)
    summary['work_order']['current'][0]=state+f' 当前批准批次{count}/5；未接入。'
    summary['report_updated_at']='2026-11-07'
    assert [(r['id'],r['percent'],r['earned'],r['possible']) for r in summary['systems']]==[(r['id'],r['percent'],r['earned'],r['possible']) for r in old['systems']]
    assert all(r==o for r,o in zip(summary['systems'],old['systems']) if r['id']!='multiblocks')
    assert summary['overall_percent']==old['overall_percent'] and summary['multiblock_scope']==old['multiblock_scope']
    text=originals[REPORT/'index.html'].decode('utf-8')
    pattern=r'(<details class="system" data-id="multiblocks"[\s\S]*?<div class="bar">[\s\S]*?</div><p>)[\s\S]*?(</p>)'
    text,n=re.subn(pattern,lambda m:m[1]+'2026-11-07 · '+row['coverage']+m[2],text,count=1);assert n==1
    assert old_reason in text;text=text.replace(old_reason,cap['reason'],1)
    notice=f'<p class="notice" id="mx-c01-design">2026-11-07：<a href="../../{design["preview"]}">{design["title"]}</a>。{state} 批准批次{count}/5；未部署。十周年预案与西瓜ARG保留，客户端实测继续暂停；系统分数与74项分母不变。</p>'
    text,n=re.subn(r'<p class="notice" id="mx-c01-design">[\s\S]*?</p>',lambda _:notice,text,count=1);assert n==1
    text,n=re.subn(r'(<script type="application/json" id="audit-data">)[\s\S]*?(</script>)',lambda m:m[1]+json.dumps(summary,ensure_ascii=False).replace('</','<\\/')+m[2],text,count=1);assert n==1
    assert json.loads(re.search(r'id="audit-data">([\s\S]*?)</script>',text)[1])==summary
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[r['id'] for r in summary['systems']]
    assert [r['percent'] for r in summary['systems']]==sorted(r['percent'] for r in summary['systems'])
    publisher().publish_transaction({REPORT/'current-summary.json':json.dumps(summary,ensure_ascii=False,indent=2)+'\n',REPORT/'index.html':text},originals)
    save(work/'report-publication.json',dict(passed=True,ascending_order=True,scores_unchanged=True,
        overall_percent=summary['overall_percent'],approved_forms=index['approved_structure_forms'],
        formal_forms=index['formal_structure_forms'],batch_count=count,design=design))


def package_candidate(out,work,state,detail,next_turn):
    class Links(HTMLParser):
        def __init__(self):
            super().__init__();self.links=[]

        def handle_starttag(self,tag,attrs):
            self.links.extend(v for k,v in attrs if k in ('href','src') and v and not v.startswith(('http:','https:','data:','#')))

    manifest=read(out/'manifest.json');check=read(out/'verification.json');qa=read(work/'viewer-qa.json')
    assert qa['passed'] and not qa['desktop_used'] and not qa['game_started']
    assert manifest['blocks']==check['blocks']==qa['blocks']
    assert manifest['unique_materials']==check['unique_materials']==qa['materials']
    assert check['pipe_routes_passed'] and check['open_pipe_ends']==0
    assert check['readback']['geometry_nbt_schematic_per_block_equal']
    assert not manifest['approved'] and not manifest['installed']
    for page in [out/'index.html',out/manifest['key']/'三维评审.html']:
        links=Links();links.feed(page.read_text(encoding='utf-8'))
        assert all((page.parent/link.split('?',1)[0]).exists() for link in links.links)
    assert all((out/name).stat().st_size>10000 for name in ['完整预览.png','后侧设备.png','俯视布局.png','主控材质近景.png','逐层剖切.png'])
    shutil.copy2(work/'viewer-qa.json',out/'viewer-qa.json')
    for p in [ROOT/'tools/structure_delivery'/f'capture_{work.name.replace("-","_")}.mjs',
              ROOT/'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs']:
        assert p.is_file();shutil.copy2(p,out/'生成脚本'/p.name)
    bundle=out.with_suffix('.zip')
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(out.parent).as_posix())
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for p in out.rglob('*'):
            if p.is_file():assert z.read(p.relative_to(out.parent).as_posix())==p.read_bytes()
    sha=digest(bundle);bundle.with_suffix('.zip.sha256').write_text(sha+'\n',encoding='ascii')
    receipt=read(work/'package-status.json')
    receipt.update(zip=bundle.relative_to(ROOT).as_posix(),zip_sha256=sha,viewer_qa_passed=True,local_links_passed=True)
    save(work/'package-status.json',receipt)
    index_bytes=INDEX.read_bytes()
    candidate=dict(id=manifest['key'].upper(),version=manifest['candidate_version'],title=manifest['title'],
        status='candidate_waiting_user_review',approved=False,installed=False,game_verified=False,survival_stage_verified=False,
        size_xyz=manifest['size'],blocks=check['blocks'],materials=check['unique_materials'],
        pipe_routes=check['pipe_routes_count'],open_pipe_ends=0,
        preview=(out/'index.html').relative_to(ROOT).as_posix(),receipt=(work/'package-status.json').relative_to(ROOT).as_posix(),zip_sha256=sha)
    if 'arm_count' in check:candidate['arm_count']=check['arm_count']
    if 'ordinary_materials' in check:
        candidate.update(ordinary_materials=check['ordinary_materials'],target_voltage=manifest['target_voltage'],
            appearance_voltage=manifest.get('appearance_voltage',manifest['target_voltage']),
            baseline_check=check['baseline_check'],voltage_progression_passed=check['voltage_progression']['passed'],
            lower_form_count=check['voltage_progression']['lower_form_count'])
    publish_status(work,candidate,detail,state,next_turn)
    assert INDEX.read_bytes()==index_bytes,'待审候选不得改变批准台账'
    return candidate
