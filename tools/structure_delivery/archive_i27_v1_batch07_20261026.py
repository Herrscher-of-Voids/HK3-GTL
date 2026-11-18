# -*- coding: utf-8 -*-
"""确认I27并准备第五批次原件；I26体积规则未解，不写入实例。"""
import base64
import collections
import copy
import datetime as dt
import gc
import gzip
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path
from project_paths import project_path

import nbtlib
import numpy as np

import archive_i23_v8_approval_20261025 as common
import build_i25_world_bubble_observatory_20261025 as assets
import build_i26_kwaichung_terminal_v2_20261026 as shared

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I27_世界泡整体捕获阵列_锁界环形回收坞_V1_20261026'
INSTANCE = assets.INSTANCE
IDS = ['I22', 'I23', 'I24', 'I26', 'I27']
APPROVED_AT = '2026-10-26T17:08:53.720+08:00'
QUOTE = '我靠，I27非常的好，直接到下一台'
DIALOGUE = ROOT / 'doc/HK3GTL-内测5/完整对话归档/2026-10-26_17-08-53_I27V1确认与I28启动_1ecfb298e7.html'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-26_17-08-53_I27V1确认与I28启动.html'
BLOCKERS = ['I26 V5实体包围盒体积11,025,630小于低阶I25的11,970,190；已批准的110格高度例外只豁免高度，未豁免体积。']


def save(path, value):
    common.write_json(path, value)


def zip_checked(folder, package=None):
    hashes = common.file_hashes(folder)
    package = package or folder.with_suffix('.zip')
    with zipfile.ZipFile(package, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name in hashes:output.write(folder / name, name)
    checked = common.verify_zip(package, hashes)
    package.with_suffix('.zip.sha256').write_text(checked['sha256']+'\n', encoding='ascii')
    return package, checked


def inspect_structure(folder, identity, expected):
    nbt_path, = folder.rglob('*.nbt')
    schem_path, = folder.rglob('*.schem')
    loaded = nbtlib.load(nbt_path)
    assert int(loaded['DataVersion']) == 3465
    states = [common.state_name(p) for p in loaded['palette']]
    size = list(map(int, loaded['size']))
    cells = {}
    for block in loaded['blocks']:
        pos = tuple(map(int, block['pos']))
        assert pos not in cells and all(0 <= pos[i] < size[i] for i in range(3))
        cells[pos] = states[int(block['state'])]
    del loaded
    counts = collections.Counter(cells.values())
    assert size == expected['size_xyz'] and len(cells) == expected['block_count']
    assert common.digest(nbt_path) == expected['nbt_sha256']
    assert [min(p[i] for p in cells) for i in range(3)] == [0,0,0]
    assert [max(p[i] for p in cells)+1 for i in range(3)] == size
    assert cells[tuple(expected['controller'])] == 'minecraft:diamond_block'
    if identity == 'I27':assert counts['minecraft:diamond_block'] == 1
    assert counts['hk3gtl:industrial_port_casing'] == expected['port_count']
    schematic = nbtlib.load(schem_path)
    assert int(schematic['Version']) == 2 and int(schematic['DataVersion']) == 3465
    assert [int(schematic[k]) for k in ('Width','Height','Length')] == size
    palette = {str(k):int(v) for k,v in schematic['Palette'].items()}
    assert palette['minecraft:air'] == 0 and set(palette) == set(states)|{'minecraft:air'}
    raw = np.asarray(schematic['BlockData']).view(np.uint8)
    if max(palette.values()) < 128:
        values = raw
    else:
        values=[];value=shift=0
        for byte in raw:
            value |= (int(byte)&127) << shift
            if byte&128:shift+=7
            else:values.append(value);value=shift=0
        assert shift == 0
        values=np.asarray(values,dtype=np.uint32)
    assert len(values) == int(np.prod(size))
    dense = np.zeros(len(values),dtype=values.dtype)
    for (x,y,z),state in cells.items():dense[(y*size[2]+z)*size[0]+x] = palette[state]
    assert np.array_equal(dense,values), identity
    result = dict(id=identity,size_xyz=size,blocks=len(cells),materials=len(states),controller=expected['controller'],
                  port_count=expected['port_count'],diamond_marker_count=counts['minecraft:diamond_block'],nbt_file=nbt_path.relative_to(folder).as_posix(),
                  schem_file=schem_path.relative_to(folder).as_posix(),nbt_sha256=common.digest(nbt_path),
                  schem_sha256=common.digest(schem_path),nbt_schematic_per_block_equal=True,
                  actual_bounds_equal_declared=True,states=states,palette=dict(counts),game_verified=False)
    del schematic,raw,values,dense
    if identity == 'I27':
        check=json.loads((folder/'verification.json').read_text(encoding='utf-8'))
        assert counts == check['palette'] and check['passed']
        assert all(check['voltage_progression']['passes'].values())
        assert result['schem_sha256'] == check['nbt_schem_sha256']['schem']
        encoded,=re.findall(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"',(folder/'i27/data.js').read_text(encoding='utf-8'))
        payload=json.loads(gzip.decompress(base64.b64decode(encoded,validate=True)))
        assert payload['blockCount'] == len(cells) and payload['palette'] == states
        data=dict(payload['data'],blocks=[{'pos':list(p),'state':s} for p,s in cells.items()])
        assert payload['surfaceGroups'] == shared.build_surface_groups(data,states)
        assert data['controller'] == expected['controller']
        assert {tuple(p['pos']) for p in data['ports']} == {p for p,s in cells.items() if s=='hk3gtl:industrial_port_casing'}
        result.update(nbt_viewer_surface_equal=True,quantitative_rules_passed=True)
        del payload,data
    del cells
    gc.collect()
    return result


def resources_for(states):
    version_path=INSTANCE.parent/'mrpack/modrinth.index.json'
    version=json.loads(version_path.read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    jars={p.name:common.digest(p) for p in (INSTANCE/'mods').glob('*HK3GTL*.jar')}
    assert jars
    results=[]
    # 分项核验保留失败详情，不能将单个资源缺口藏在批次通过中。
    for state in states:
        try:
            materials,sources,packs=assets.resource_materials([state]);m,=materials
            assert m['complete_cube'] and not m['tinted']
            results.append(dict(state=state,resource_passed=True,complete_cube=m['complete_cube'],
                                model=m.get('model'),transparent=m['transparent'],sources=sources))
        except Exception as error:
            results.append(dict(state=state,resource_passed=False,error=f'{type(error).__name__}: {error}'))
    return dict(instance=str(INSTANCE),instance_version=version,instance_index_sha256=common.digest(version_path),
                hk3gtl_jars=jars,states=results,all_resource_passed=all(r['resource_passed'] for r in results),
                scope='读取当前实例与启用资源包的静态模型及贴图；项目自有白名单资源允许读取当前项目资源。非运行时注册表、最终配方或生存可达性验收。')


def main():
    before=INDEX.read_bytes();index=json.loads(before)
    assert index['pending_batch']['approved_machine_ids'] == IDS[:-1]
    assert index['pending_batch']['count'] == 4 and not any(e['id']=='I27' for e in index['entries'])
    source_hashes=common.file_hashes(SOURCE)
    manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    check=json.loads((SOURCE/'verification.json').read_text(encoding='utf-8'))
    assert manifest['key']=='I27' and manifest['approved'] is False and manifest['target_voltage']=='IMV'
    expected=dict(size_xyz=manifest['size'],block_count=manifest['blocks'],controller=manifest['controller'],port_count=8,
                  nbt_sha256=check['nbt_schem_sha256']['nbt'])
    verification=inspect_structure(SOURCE,'I27',expected)
    resume=[]
    for candidate in ARCHIVES.glob('*_batch-07_05of05_I27_V1_IMV_已确认'):
        proof=json.loads((candidate/'确认与校验清单.json').read_text(encoding='utf-8'))
        if proof.get('original_user_message_time') == APPROVED_AT and proof.get('previous_index_sha256') == hashlib.sha256(before).hexdigest():
            resume.append((candidate,proof))
    assert len(resume)<=1, '存在多个同轮确认快照，须人工核对'
    now=dt.datetime.fromisoformat(resume[0][1]['created_at']) if resume else dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp=now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot=ARCHIVES/f'{stamp}_batch-07_05of05_I27_V1_IMV_已确认'
    evidence=snapshot/'evidence'
    if not resume:
        snapshot.mkdir(exist_ok=False);evidence.mkdir()
        (evidence/'previous-current-index.json').write_bytes(before)
        shutil.copy2(__file__,evidence/Path(__file__).name)
        for name in ('系统角色设定.md','崩坏三-gtl (hk3gtl) 项目规则.md','当前多方块设计规则.md','巨构提示词.txt'):
            shutil.copy2(ROOT/'rule'/name,evidence/name)
    target=snapshot/SOURCE.name
    if not resume:shutil.copytree(SOURCE,target)
    assert common.file_hashes(target)==source_hashes
    pending=dict(index['pending_batch'],approved_machine_ids=IDS,count=5,required=5,
                 deployment_eligible=False,deployment_blockers=BLOCKERS,
                 status='five_appearance_approvals_archived_deployment_blocked')
    scope='I27 V1锁界环形回收坞建筑外观与对应结构文件明确批准；保持原候选元数据。正式Pattern、配方、生存闭环及游戏运行另行验收。'
    row=dict(id='I27',key='i27',candidate_key='i27',approved_version='V1',candidate_version='V1',
             target_voltage_appearance='IMV',status='approved_archived_waiting_batch_rule_resolution',
             approval_quote=QUOTE,approval_scope=scope,approved_at=APPROVED_AT,source=str(SOURCE),archive=str(target),
             discussion_record=str(DISCUSSION),dialogue_archive=str(DIALOGUE),counts_as_new_machine=True,
             source_candidate_approved_field=False,formal_resource_present=False,game_files_installed=False,game_verified=False,
             structure_checks=verification,**expected)
    approval=dict(record=1,created_at=now.isoformat(),timezone='Asia/Hong_Kong',original_user_message_time=APPROVED_AT,
                  entries=[row],source_files_sha256=source_hashes,accepted_design_scope=scope,
                  pending_batch_after_archive=pending,previous_index_sha256=hashlib.sha256(before).hexdigest(),
                  source_metadata_boundary='原候选approved=false与待审文字原字节保留，批准写本外部清单。',
                  game_files_installed=False,game_verified=False)
    if not resume:
        save(snapshot/'确认与校验清单.json',approval)
        (snapshot/'确认接入.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I27 V1确认归档</title><style>body{{max-width:1080px;margin:30px auto;font:16px/1.8 system-ui;background:#121b2b;color:#e6ecf5}}img{{width:100%}}a{{color:#b1d7e7}}</style><h1>I27 V1外观已确认</h1><p>{scope}</p><p>337×337×205宽长高，1,201,924块，36种材料，主控蓝图[168,35,18]，8接口。四项低阶递增、标准NBT/Sponge及预览同源核验通过。</p><p>batch-07已达5/5；I26独立体积项仍冲突，本次不把满批计数当成规则豁免，也未安装实例。</p><p><a href="确认与校验清单.json">确认清单</a> · <a href="{SOURCE.name}/i27/三维评审.html">I27三维</a></p><img src="{SOURCE.name}/等轴预览.png" alt="I27完整等轴图"></html>',encoding='utf-8')
        bundle,bundle_check=zip_checked(snapshot)
    else:
        assert resume[0][0]==snapshot and resume[0][1]['source_files_sha256']==source_hashes
        bundle=snapshot.with_suffix('.zip');bundle_check=common.verify_zip(bundle,common.file_hashes(snapshot))
    row.update(approval_manifest=str(snapshot/'确认与校验清单.json'),archive_zip=str(bundle),archive_zip_sha256=bundle_check['sha256'])
    rows=[next(e for e in index['entries'] if e['id']==identity) for identity in IDS[:-1]]+[row]

    batch=ROOT/'deliveries/批次接入准备'/f'{stamp}_batch-07_五台结构预备包_待I26体积核定'
    if batch.exists():assert not any(batch.iterdir()), '已有非空预备包，拒绝覆盖'
    else:batch.mkdir(parents=True,exist_ok=False)
    batch_checks=[];all_states=set();archive_proofs=[];download_zips=[]
    for entry in rows:
        identity=entry['id'];folder=project_path(entry['archive'])
        archive_path=project_path(entry['archive_zip'])
        assert common.digest(archive_path)==entry['archive_zip_sha256']
        with zipfile.ZipFile(archive_path) as package:assert package.testzip() is None
        inspected=verification if identity=='I27' else inspect_structure(folder,identity,entry)
        batch_checks.append(inspected);all_states.update(inspected['states'])
        copied=batch/'machines'/identity;shutil.copytree(folder,copied)
        hashes=common.file_hashes(folder);assert common.file_hashes(copied)==hashes
        approval_source=project_path(entry['approval_manifest'])
        shutil.copy2(approval_source,copied/'外部批准清单.json')
        # 原确认网页含上级目录下载链接；补齐目标，不改网页原件。
        for link in re.findall(r'href="(\.\./[^"/]+\.zip)"',(copied/'index.html').read_text(encoding='utf-8')):
            original=ROOT/'deliveries'/project_path(link).name
            checked=common.verify_zip(original,hashes,prefix='' if identity=='I22' else folder.name+'/')
            download=copied.parent/original.name;shutil.copy2(original,download)
            assert common.digest(download)==checked['sha256']
            download_zips.append(dict(id=identity,path=download.relative_to(batch).as_posix(),sha256=checked['sha256']))
        archive_proofs.append(dict(id=identity,archive=str(folder),source_archive_zip=str(archive_path),
                                  source_archive_zip_sha256=entry['archive_zip_sha256'],source_files_sha256=hashes,
                                  batch_root=(project_path('machines')/identity).as_posix(),approved_at=entry.get('approved_at')))
        print(json.dumps({'verified_machine':identity,'blocks':inspected['blocks']},ensure_ascii=True),flush=True)
    resource_check=resources_for(sorted(all_states))
    if not resource_check['all_resource_passed']:
        pending['deployment_blockers'].append('当前2.9.2资源核验存在缺口，详见资源核验.json。')
    save(batch/'资源核验.json',resource_check)
    save(batch/'逐台结构核验.json',batch_checks)
    receipt=dict(created_at=now.isoformat(),timezone='Asia/Hong_Kong',batch='batch-07',approved_machine_ids=IDS,
                 count=5,required=5,appearance_approvals_complete=True,deployment_eligible=False,
                 deployment_blockers=pending['deployment_blockers'],source_approval_archives=archive_proofs,
                 linked_original_candidate_zips=download_zips,
                 target_instance=str(INSTANCE),target_pack_version='2.9.2',prepared_structure_files=10,
                 installed_files=[],formal_pattern_integrated=False,game_files_installed=False,game_verified=False,
                 boundary='该包是接入准备，不是安装收据；不向实例写入投影、模组JAR、正式Pattern或世界存档。')
    save(batch/'批次接入准备清单.json',receipt)
    links=''.join(f'<tr><td>{e["id"]}</td><td>{e["blocks"]:,}</td><td>{e["materials"]}</td><td><a href="machines/{e["id"]}/index.html">预览</a></td><td><a href="machines/{e["id"]}/{e["nbt_file"]}">NBT</a> · <a href="machines/{e["id"]}/{e["schem_file"]}">Schematic</a></td></tr>' for e in batch_checks)
    (batch/'index.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>batch-07五台结构接入准备</title><style>body{{max-width:1150px;margin:30px auto;font:16px/1.8 system-ui;background:#121b2b;color:#e5edf7}}a{{color:#b5d8ec}}td,th{{padding:12px;border-bottom:1px solid #47526a;text-align:left}}.note{{padding:14px;border-left:4px solid #d5b16c;background:#2d3144}}</style><h1>batch-07 五台外观已确认 · 接入准备包</h1><p>I22 / I23 / I24 / I26 / I27；当前增强版2.9.2，已达到5/5外观批准计数。</p><p class="note">{html.escape("；".join(pending["deployment_blockers"]))}<br>因此暂不把本批标记为可正式接入，不修改负责人选定的I26外观；也未写入游戏实例。</p><table><tr><th>机器</th><th>实际方块</th><th>材料</th><th>审阅</th><th>结构原件</th></tr>{links}</table><p><a href="批次接入准备清单.json">准备清单</a> · <a href="逐台结构核验.json">逐台回读及SHA</a> · <a href="资源核验.json">当前实例资源</a></p><p>全部文件读取各自不可变确认归档；标准NBT与Sponge逐格一致，复制后逐文件SHA核对。静态资源核验不能代替正式Pattern、配方、生存获取或游戏验收。</p></html>',encoding='utf-8')
    save(batch/'文件校验清单.json',common.file_hashes(batch))
    batch_zip,batch_zip_check=zip_checked(batch)
    assert common.file_hashes(SOURCE)==source_hashes and INDEX.read_bytes()==before
    assert {p.name:common.digest(p) for p in (INSTANCE/'mods').glob('*HK3GTL*.jar')} == resource_check['hk3gtl_jars']
    pending.update(prepared_package=str(batch),prepared_zip=str(batch_zip),prepared_zip_sha256=batch_zip_check['sha256'])
    index['entries'].append(row);index['approved_structure_forms']+=1
    index.update(pending_batch=pending,updated_at=now.isoformat(),target_pack_version='2.9.2',
                 scope='I27 V1外观确认归档，batch-07达5/5并完成五台接入预备包；I26体积规则未解，未实装。',
                 batch_rule='每累计五台明确批准后按确认原件接入；batch-07已5/5，五台包就绪，I26体积项阻塞保留。',
                 latest_approval_snapshot=dict(snapshot=str(snapshot),zip=str(bundle),zip_sha256=bundle_check['sha256']),
                 latest_deployment_preparation=dict(path=str(batch),zip=str(batch_zip),zip_sha256=batch_zip_check['sha256'],installed=False))
    index.setdefault('historical_previous_indices',[]).append(copy.deepcopy(index.get('previous_index',{})))
    index['previous_index']=dict(preserved_copy=str(evidence/'previous-current-index.json'),sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records',[]).append(dict(record=len(index['_change_records'])+1,time=now.isoformat(),
        reason='用户明确批准I27并继续I28',deleted='无；候选、旧确认归档与索引均保留',
        added='I27 V1不可变确认归档、五台完整结构接入预备包与2.9.2资源核对',
        modified='batch-07从4/5到5/5，保留I26体积阻塞，未写实例',purpose='完成已授权接入准备并准确保留剩余硬规则边界'))
    save(INDEX,index)
    print(json.dumps(dict(snapshot=str(snapshot),zip=str(bundle),zip_sha256=bundle_check['sha256'],batch=str(batch),
                         batch_zip=str(batch_zip),batch_zip_sha256=batch_zip_check['sha256'],
                         resources_passed=resource_check['all_resource_passed'],resource_states=len(all_states),
                         pending_batch=pending,game_files_installed=False),ensure_ascii=True),flush=True)


if __name__=='__main__':main()
