# -*- coding: utf-8 -*-
"""I24 V2批准归档，保留候选原件并向batch-07新增一台。

【变更记录 #1】2026-10-25 00:44:47（结构批准记录，不增加模组修订）
删除：无，保留I23 V8批准和I24待审来源。
新增：I24修复版逐格核验、时间戳快照、ZIP和外部批准记录。
修改：batch-07由I22/I23的2/5推进为I22/I23/I24的3/5。
用途：记录用户明确批准；不修改正式Pattern、候选原件或游戏实例。
"""
from __future__ import annotations

import base64
import gzip
import re
from collections import Counter

import nbtlib
from structure_size_baseline import require

import copy
import datetime as dt
import hashlib
import html
import json
import os
import shutil
import zipfile
from pathlib import Path
from project_paths import project_path

import archive_i23_v8_approval_20261025 as previous_tools

ROOT = previous_tools.ROOT
ARCHIVES = previous_tools.ARCHIVES
INDEX = previous_tools.INDEX
SOURCE = ROOT / 'deliveries/I24_量子异常观测阵列_三碟长基线天文庭院_V2_20261025'
SOURCE_ZIP = SOURCE.with_suffix('.zip')
EXPECTED_ZIP = '719e4b4ad2778e837f6281febfdb4be26d71e665c0dcb9fbbaee8d95f78cbd6d'
APPROVAL_QUOTE = 'i24 ok'
CONTINUATION_QUOTE = '下一台吧'
SCOPE = 'I24当前三碟长基线天文庭院V2外观及对应结构文件，含已修复的真实钻石主控和工业接口预览；正式Pattern、配方、研究/生存闭环和游戏运行另行验收。'
digest = previous_tools.digest
file_hashes = previous_tools.file_hashes
write_json = previous_tools.write_json
verify_zip = previous_tools.verify_zip


def verify_structure(manifest: dict) -> dict:
    nbt_path, = (SOURCE / 'i24').glob('*.nbt')
    schem_path, = (SOURCE / 'i24').glob('*.schem')
    nbt = nbtlib.load(nbt_path)
    size = [int(v) for v in nbt['size']]
    palette = [previous_tools.state_name(item) for item in nbt['palette']]
    cells = {}
    for block in nbt['blocks']:
        pos = tuple(int(v) for v in block['pos'])
        if pos in cells or not all(0 <= pos[i] < size[i] for i in range(3)):
            raise ValueError('NBT 存在重复或越界坐标。')
        cells[pos] = palette[int(block['state'])]
    if any(state == 'minecraft:air' for state in cells.values()):
        raise ValueError('NBT 实体列表不应包含空气。')
    if size != [117, 66, 149] or manifest['size_xyz'] != size or len(cells) != 85154:
        raise ValueError('NBT 尺寸或实际方块数不符。')
    if manifest['block_count'] != len(cells) or manifest['palette'] != dict(Counter(cells.values())):
        raise ValueError('NBT 实际方块统计与 manifest 不符。')
    if digest(nbt_path) != manifest['nbt_sha256'] or digest(schem_path) != manifest['schem_sha256']:
        raise ValueError('结构文件 SHA256 与 manifest 不符。')
    size_check = require({'key': 'I24', 'size': size,
                          'blocks': [{'pos': list(pos)} for pos in cells]})

    payload_text = (SOURCE / 'data.js').read_text(encoding='utf-8')
    encoded, = re.findall(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', payload_text)
    payload = json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)))
    view = payload['data']
    if (view['key'] != 'i24' or view['candidate_version'] != manifest['candidate_version']
            or view['size'] != size or view['block_count'] != len(cells)
            or view['controller'] != manifest['controller'] or view['ports'] != manifest['ports']):
        raise ValueError('三维预览元数据与 manifest 不符。')
    w, h, d = size
    viewer_cells = {}
    if len(payload['groups']) != len(payload['palette']):
        raise ValueError('三维预览材质组长度不符。')
    for state, group in zip(payload['palette'], payload['groups']):
        for packed in group:
            y, remainder = divmod(packed, w * d)
            z, x = divmod(remainder, w)
            if (x, y, z) in viewer_cells:
                raise ValueError('三维预览存在重复坐标。')
            viewer_cells[x, y, z] = state
    if viewer_cells != cells:
        raise ValueError('NBT 与三维预览逐格内容不同。')

    schem = nbtlib.load(schem_path)
    if [int(schem[k]) for k in ('Width', 'Height', 'Length')] != size:
        raise ValueError('Schematic 尺寸不同。')
    schem_palette = {int(value): key for key, value in schem['Palette'].items()}
    values, value, shift = [], 0, 0
    for byte in schem['BlockData']:
        byte = int(byte) & 255
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
            if shift > 28:
                raise ValueError('Schematic VarInt 过长。')
        else:
            values.append(value)
            value, shift = 0, 0
    if shift or len(values) != w * h * d:
        raise ValueError('Schematic 体素数量或 VarInt 结束状态异常。')
    schematic_cells = {}
    for packed, state_id in enumerate(values):
        state = schem_palette[state_id]
        if state != 'minecraft:air':
            y, remainder = divmod(packed, w * d)
            z, x = divmod(remainder, w)
            schematic_cells[x, y, z] = state
    if schematic_cells != cells:
        raise ValueError('NBT 与 Schematic 逐格内容不同。')

    controller = tuple(manifest['controller'])
    ports = manifest['ports']
    if (controller != (58, 8, 0) or controller[0] != w // 2
            or cells.get(controller) != 'minecraft:diamond_block'
            or list(cells.values()).count('minecraft:diamond_block') != 1
            or view['controller_face'] != 'north'):
        raise ValueError('主控标记、居中位置或朝向不符。')
    expected_ports = {tuple(port['pos']) for port in ports}
    actual_ports = {pos for pos, state in cells.items() if state == 'hk3gtl:industrial_port_casing'}
    if len(ports) != 4 or len(expected_ports) != 4 or actual_ports != expected_ports:
        raise ValueError('接口数量或实际位置不符。')
    project_states = sorted({state for state in cells.values() if state.startswith('hk3gtl:')})
    if project_states != ['hk3gtl:industrial_port_casing', 'hk3gtl:voltage_machine_casing_qev']:
        raise ValueError('出现白名单之外的 HK3GTL 项目方块。')
    materials = {m['state']: m for m in payload['materials']}
    for marker in ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing'):
        assert materials[marker]['faces'] != materials['hk3gtl:voltage_machine_casing_qev']['faces']
    return dict(size_check, preview_marker_materials_distinct_from_qev=True, nbt_file=nbt_path.relative_to(SOURCE).as_posix(),
                schem_file=schem_path.relative_to(SOURCE).as_posix(),
                nbt_sha256=digest(nbt_path), schem_sha256=digest(schem_path),
                viewer_data_sha256=digest(SOURCE / 'data.js'), block_count=len(cells),
                reread_nbt=True, nbt_schematic_per_block_equal=True,
                nbt_viewer_per_block_equal=True, schematic_volume=w * h * d,
                manifest_palette_equals_actual=True, controller=list(controller),
                controller_face='north', controller_marker_unique=True,
                port_count=len(ports), port_positions_exact=True,
                project_states=project_states, project_whitelist_passed=True,
                check_scope='真实回读 NBT、Schematic 与压缩三维预览，逐格核验；静态文件一致不代表游戏成型。')


def main():
    before = INDEX.read_bytes()
    index = json.loads(before.decode('utf-8'))
    pending = index['pending_batch']
    assert pending['id'] == 'batch-07' and pending['approved_machine_ids'] == ['I22','I23']
    assert pending['count'] == 2 and pending['required'] == 5
    assert not any(e['id'] == 'I24' for e in index['entries'])
    previous_hashes = {e['id']:digest(project_path(e['archive_zip'])) for e in index['entries'] if e['id'] in ('I22','I23')}
    hashes = file_hashes(SOURCE)
    manifest = json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['key'] == 'i24' and manifest['candidate_version'] == '三碟长基线天文庭院 V2・待审'
    assert manifest['candidate_approved'] is False and manifest['target_voltage'] == 'QEV'
    assert digest(SOURCE_ZIP) == EXPECTED_ZIP
    zip_check = verify_zip(SOURCE_ZIP, hashes, SOURCE.name+'/')
    check = verify_structure(manifest)
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES/f'{now:%Y%m%d_%H%M%S_%f}_batch-07_03of05_I24_V2_QEV_已确认'
    snapshot.mkdir(exist_ok=False)
    evidence = snapshot/'evidence'; evidence.mkdir()
    (evidence/'previous-current-index.json').write_bytes(before)
    rules=[]
    for relative in previous_tools.RULES:
        path = ROOT/relative
        shutil.copy2(path,evidence/path.name)
        rules.append({'path':relative,'sha256':digest(path),'lines':len(path.read_text(encoding='utf-8').splitlines())})
    shutil.copy2(Path(__file__),evidence/Path(__file__).name)
    shutil.copy2(SOURCE_ZIP,evidence/SOURCE_ZIP.name)
    target=snapshot/SOURCE.name
    shutil.copytree(SOURCE,target)
    assert file_hashes(target) == hashes
    next_pending=dict(pending,approved_machine_ids=['I22','I23','I24'],count=3,required=5,
        deployment_eligible=False,deployment_blockers=['batch-07当前为3/5，未达到五台接入门槛。','建筑外观批准与正式功能/游戏验收分别记录。'])
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M-%S}_I24V2明确批准归档与I25候选继续.html'
    def link(path): return html.escape(os.path.relpath(path,discussion.parent).replace('\\','/'))
    summary=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I24 V2批准归档与I25继续</title><style>body{{max-width:980px;margin:32px auto;padding:0 20px;font:16px/1.8 'Microsoft YaHei',sans-serif}}code{{overflow-wrap:anywhere}}</style><h1>I24 V2批准归档与I25继续</h1><p>实际记录时间：{now.isoformat()}（Asia/Hong_Kong）；原用户发送时间未知。</p><h2>用户已确认</h2><p>原话：“{APPROVAL_QUOTE}”“{CONTINUATION_QUOTE}”。当前I24 V2外观与对应结构文件明确批准，下一台继续既有规划I25「世界泡坐标解析中心」。I25尚未获批。</p><h2>实际实施与核验</h2><p>I24 117×66×149（X×Y×Z），85,154实际方块，主控[58,8,0]、4口。批准对象含真实钻石块主控和工业接口预览修复。NBT、Schematic、压缩三维数据逐格一致；来源与归档ZIP文件集合、CRC及逐文件SHA256均复核。</p><p>候选原件及其candidate_approved=false/待审字段原字节保留，批准写在外部清单。此前I23 V8不重复计数；batch-07为I22、I23、I24共3/5，未部署。</p><h2>范围与下一步</h2><p>{SCOPE}</p><p>I25按QEV/V07提案映射、41×49×33最低宽长高和本体接口要求独立设计；本摘要不声称其已完成或批准。</p><p>无被删除的旧批准，I24 V1作为历史候选保留；本页是决策摘要，不冒充完整对话原文。</p><p><a href="{link(SOURCE/'index.html')}">I24原候选</a> · <a href="{link(snapshot/'确认与校验清单.json')}">批准与校验清单</a></p></html>'''
    discussion.write_text(summary,encoding='utf-8'); (evidence/discussion.name).write_text(summary,encoding='utf-8')
    row={'id':'I24','key':'i24','candidate_key':'i24','approved_version':'V2','candidate_version':manifest['candidate_version'],
        'status':'approved_archived_waiting_batch','approval_quote':APPROVAL_QUOTE,'continuation_quote':CONTINUATION_QUOTE,
        'approval_scope':SCOPE,'approved_at':now.isoformat(),'source':str(SOURCE),'archive':str(target),'source_zip':str(SOURCE_ZIP),
        'source_zip_sha256':zip_check['sha256'],'source_files_sha256':hashes,'structure_checks':check,
        'source_candidate_approved_field':False,'counts_as_new_machine':True,'formal_resource_present':False,'game_files_installed':False,'game_verified':False}
    approval={'record':1,'created_at':now.isoformat(),'timezone':'Asia/Hong_Kong','original_user_message_time':None,
        'discussion_record':str(discussion),'batch':'batch-07','batch_position':'03/05','entries':[row],
        'rule_snapshot_record':{'created_at':now.isoformat(),'files':rules},'source_zip_validation':zip_check,
        'previous_index_sha256':hashlib.sha256(before).hexdigest(),'previous_approved_zip_sha256':previous_hashes,
        'pending_batch_after_archive':next_pending,'source_metadata_boundary':'来源待审状态和candidate_approved=false原字节保留；批准另记。',
        'accepted_design_scope':SCOPE,'game_files_installed':False,'game_verified':False}
    write_json(snapshot/'确认与校验清单.json',approval)
    (snapshot/'确认接入.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I24 V2批准归档</title><h1>I24 V2外观批准归档 · batch-07 3/5</h1><p>{now.isoformat()}</p><p>{html.escape(SCOPE)}</p><p>85,154方块；117×66×149 XYZ。来源/ZIP与三维逐格核验通过；原候选不变，未部署。</p><p><a href="确认与校验清单.json">确认与校验清单</a></p></html>',encoding='utf-8')
    archive_hashes=file_hashes(snapshot); bundle=snapshot.with_suffix('.zip')
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in archive_hashes:z.write(snapshot/name,name)
    archive_check=verify_zip(bundle,archive_hashes)
    bundle.with_suffix('.zip.sha256').write_text(archive_check['sha256']+'\n',encoding='ascii')
    assert file_hashes(SOURCE)==hashes and digest(SOURCE_ZIP)==EXPECTED_ZIP
    assert all(digest(project_path(e['archive_zip']))==previous_hashes[e['id']] for e in index['entries'] if e['id'] in previous_hashes)
    entry={k:v for k,v in row.items() if k!='source_files_sha256'}
    entry.update(approval_manifest=str(snapshot/'确认与校验清单.json'),discussion_record=str(discussion),archive_zip=str(bundle),
        archive_zip_sha256=archive_check['sha256'],nbt_sha256=check['nbt_sha256'],size_xyz=manifest['size_xyz'],controller=manifest['controller'],
        port_count=4,block_count=85154,target_voltage_appearance='QEV')
    index['entries'].append(entry);index['approved_structure_forms']+=1;index['pending_batch']=next_pending;index['updated_at']=now.isoformat()
    index['scope']='既有正式形态及部署状态保留；I22/I23V8/I24V2外观获批，batch-07为3/5，未部署。'
    index['batch_rule']='每累计5台明确批准后按归档接入实际2.9实例；当前batch-07为3/5。'
    index['latest_approval_snapshot']={'snapshot':str(snapshot),'zip':str(bundle),'zip_sha256':archive_check['sha256']}
    index.setdefault('historical_previous_indices',[]).append(copy.deepcopy(index.get('previous_index',{})))
    index['previous_index']={'preserved_copy':str(evidence/'previous-current-index.json'),'sha256':hashlib.sha256(before).hexdigest()}
    index.setdefault('_change_records',[]).append({'record':len(index.get('_change_records',[]))+1,'time':now.isoformat(),
        'reason':'用户明确批准I24并继续下一台','deleted':'无；候选原件、既有批准及旧索引保留',
        'added':'I24 V2含标记预览修复版外观批准归档，I25继续制作授权','modified':'batch-07由2/5推进3/5；正式资源及实例不变',
        'purpose':'准确保存第三台外观批准，区分结构文件和游戏功能验收'})
    assert INDEX.read_bytes()==before
    write_json(INDEX,index)
    print(json.dumps({'snapshot':str(snapshot),'zip':str(bundle),'zip_sha256':archive_check['sha256'],'discussion':str(discussion),
        'source_zip_sha256':EXPECTED_ZIP,'structure_checks':check,'pending_batch':next_pending,'source_unchanged':True,'verified':True},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
