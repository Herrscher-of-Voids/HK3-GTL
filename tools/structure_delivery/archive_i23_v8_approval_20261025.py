# -*- coding: utf-8 -*-
"""归档 I23 V8 的明确批准，只替换当前选择，不重复增加批次台数。"""
from __future__ import annotations

import base64
import copy
import datetime as dt
import gzip
import hashlib
import html
import json
import os
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from project_paths import project_path

import nbtlib

from structure_size_baseline import ROOT, require


ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I23_崩坏能相变释能机_双瓣相界锻炉_V8_20261024'
SOURCE_ZIP = SOURCE.with_suffix('.zip')
DISCUSSIONS = ROOT / 'doc/HK3GTL-内测5/讨论记录'
RULES = (
    'rule/rules.md', 'rule/系统角色设定.md',
    'rule/崩坏三-gtl (hk3gtl) 项目规则.md',
    'rule/hk3gtl java文件变更备注规范.md',
    'rule/当前多方块设计规则.md', 'rule/巨构提示词.txt',
)
APPROVAL_QUOTE = 'i23 v8 ok'
CONTINUATION_QUOTE = '下一台吧'
SCOPE = 'I23 V8「双瓣相界锻炉」建筑外观及对应结构文件；Pattern、Controller tier、配方、研究/生存获取及游戏运行尚未验收。'


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify_zip(path: Path, hashes: dict[str, str], prefix: str = '') -> dict:
    with zipfile.ZipFile(path) as package:
        names = [item.filename for item in package.infolist() if not item.is_dir()]
        expected = {prefix + name: value for name, value in hashes.items()}
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError(f'ZIP 文件集合或唯一性不符：{path}')
        if package.testzip() is not None:
            raise ValueError(f'ZIP CRC 校验失败：{path}')
        for name, value in expected.items():
            if hashlib.sha256(package.read(name)).hexdigest() != value:
                raise ValueError(f'ZIP 内容 SHA256 不符：{name}')
    return {'file_count': len(hashes), 'exact_file_set': True,
            'crc_passed': True, 'all_files_sha256_passed': True, 'sha256': digest(path)}


def state_name(entry) -> str:
    name = str(entry['Name'])
    properties = entry.get('Properties', {})
    return name + ('[' + ','.join(f'{k}={v}' for k, v in sorted(properties.items())) + ']'
                   if properties else '')


def verify_structure(manifest: dict) -> dict:
    nbt_path, = (SOURCE / 'i23').glob('*.nbt')
    schem_path, = (SOURCE / 'i23').glob('*.schem')
    nbt = nbtlib.load(nbt_path)
    size = [int(v) for v in nbt['size']]
    palette = [state_name(item) for item in nbt['palette']]
    cells = {}
    for block in nbt['blocks']:
        pos = tuple(int(v) for v in block['pos'])
        if pos in cells or not all(0 <= pos[i] < size[i] for i in range(3)):
            raise ValueError('NBT 存在重复或越界坐标。')
        cells[pos] = palette[int(block['state'])]
    if any(state == 'minecraft:air' for state in cells.values()):
        raise ValueError('NBT 实体列表不应包含空气。')
    if size != [89, 57, 102] or manifest['size_xyz'] != size or len(cells) != 58011:
        raise ValueError('NBT 尺寸或实际方块数不符。')
    if manifest['block_count'] != len(cells) or manifest['palette'] != dict(Counter(cells.values())):
        raise ValueError('NBT 实际方块统计与 manifest 不符。')
    if digest(nbt_path) != manifest['nbt_sha256'] or digest(schem_path) != manifest['schem_sha256']:
        raise ValueError('结构文件 SHA256 与 manifest 不符。')
    size_check = require({'key': 'I23', 'size': size,
                          'blocks': [{'pos': list(pos)} for pos in cells]})

    payload_text = (SOURCE / 'data.js').read_text(encoding='utf-8')
    encoded, = re.findall(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', payload_text)
    payload = json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)))
    view = payload['data']
    if (view['key'] != 'i23' or view['candidate_version'] != manifest['candidate_version']
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
    if (controller != (44, 8, 0) or controller[0] != w // 2
            or cells.get(controller) != 'minecraft:diamond_block'
            or list(cells.values()).count('minecraft:diamond_block') != 1
            or view['controller_face'] != 'north'):
        raise ValueError('主控标记、居中位置或朝向不符。')
    expected_ports = {tuple(port['pos']) for port in ports}
    actual_ports = {pos for pos, state in cells.items() if state == 'hk3gtl:industrial_port_casing'}
    if len(ports) != 6 or len(expected_ports) != 6 or actual_ports != expected_ports:
        raise ValueError('接口数量或实际位置不符。')
    project_states = sorted({state for state in cells.values() if state.startswith('hk3gtl:')})
    if project_states != ['hk3gtl:industrial_port_casing', 'hk3gtl:voltage_machine_casing_qcv']:
        raise ValueError('出现白名单之外的 HK3GTL 项目方块。')
    return dict(size_check, nbt_file=nbt_path.relative_to(SOURCE).as_posix(),
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


def main() -> None:
    index_before = INDEX.read_bytes()
    index = json.loads(index_before.decode('utf-8'))
    pending = index['pending_batch']
    if (pending['id'] != 'batch-07' or pending['approved_machine_ids'] != ['I22', 'I23']
            or pending['count'] != 2 or pending['required'] != 5):
        raise ValueError('batch-07 已变化，拒绝错批或重复计数。')
    positions = [i for i, row in enumerate(index['entries']) if row['id'] == 'I23']
    if len(positions) != 1:
        raise ValueError('当前索引必须只有一个 I23。')
    position, = positions
    previous = copy.deepcopy(index['entries'][position])
    if previous['candidate_version'] != '相变舱原位接口 V6・待审':
        raise ValueError('I23 当前版本已变化，拒绝重复或覆盖新批准。')
    previous_bundle = project_path(previous['archive_zip'])
    if digest(previous_bundle) != previous['archive_zip_sha256']:
        raise ValueError('旧 V6 确认 ZIP 的历史哈希不符。')
    previous_snapshot = project_path(previous['approval_manifest']).parent
    previous_hashes = file_hashes(previous_snapshot)
    source_hashes = file_hashes(SOURCE)
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest['key'] != 'i23' or manifest['candidate_version'] != '双瓣相界锻炉 V8・待审'
            or manifest['candidate_approved'] is not False or manifest['target_voltage'] != 'QCV'):
        raise ValueError('V8 来源身份或历史候选元数据不符。')
    source_zip_check = verify_zip(SOURCE_ZIP, source_hashes, SOURCE.name + '/')
    checks = verify_structure(manifest)

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES / f'{now:%Y%m%d_%H%M%S_%f}_batch-07_02of05_I23_V8_QCV_已确认'
    snapshot.mkdir(parents=True, exist_ok=False)
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(index_before)
    rules = []
    for relative in RULES:
        path = ROOT / relative
        shutil.copy2(path, evidence / path.name)
        rules.append({'path': relative, 'sha256': digest(path),
                      'lines': len(path.read_text(encoding='utf-8').splitlines())})
    shutil.copy2(Path(__file__), evidence / Path(__file__).name)
    shutil.copy2(SOURCE_ZIP, evidence / SOURCE_ZIP.name)
    target = snapshot / SOURCE.name
    shutil.copytree(SOURCE, target)
    if file_hashes(target) != source_hashes or file_hashes(SOURCE) != source_hashes:
        raise ValueError('候选原件或归档副本发生变化。')
    if digest(evidence / SOURCE_ZIP.name) != source_zip_check['sha256']:
        raise ValueError('归档来源 ZIP 与原件不一致。')
    blockers = ['batch-07 当前仍为2/5，未达到结构接入门槛。',
                'I23 V8 获批范围仅为建筑外观与对应结构文件，正式功能与游戏验收单独处理。']
    next_pending = dict(pending, count=2, required=5, deployment_eligible=False,
                        deployment_blockers=blockers)
    discussion = DISCUSSIONS / f'{now:%Y-%m-%d_%H-%M-%S}_I23V8明确批准替代V6与I24继续.html'
    relative_link = lambda path: html.escape(os.path.relpath(path, discussion.parent).replace('\\', '/'))
    discussion_html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I23 V8明确批准替代V6与I24继续</title><style>body{{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}}section{{border-top:1px solid #ccd6d8;padding:16px 0}}code{{overflow-wrap:anywhere}}pre{{white-space:pre-wrap}}</style></head><body>
<h1>I23 V8 明确批准替代 V6，与 I24 继续</h1><p>实际记录时间：{now.isoformat()}（Asia/Hong_Kong，UTC+08:00）。用户原消息精确发送时间未提供；不以记录时间冒充发送时间。</p>
<section><h2>用户已确认</h2><pre>{APPROVAL_QUOTE}\n{CONTINUATION_QUOTE}</pre><p>本轮明确批准当前 I23 V8「双瓣相界锻炉」外观及对应结构文件，V8 替代 V6 成为 I23 当前批准选择。<a href="{relative_link(project_path(previous['discussion_record']))}">V6 旧批准摘要</a>及其不可变快照、ZIP 和索引历史继续保留，不撤除原始证据。</p></section>
<section><h2>实际已实施与已验证</h2><p>已保存独立时间戳快照和 ZIP；原候选全部 {len(source_hashes)} 文件及来源 ZIP 原字节保留，manifest 内 candidate_approved=false 和“待审”文本仅作为候选生成时的历史元数据。实际 NBT 为 58,011 方块，89×57×102（X×Y×Z），主控 [44,8,0]，6 个工业接口占位，主体目标 QCV。</p><p>重新读取 NBT、Schematic 与 data.js 三维数据，核对逐格一致；来源 ZIP 和归档 ZIP 均逐文件核对 SHA256、集合与 CRC。静态验证不等于实机验收。</p></section>
<section><h2>批准与部署边界</h2><p>{html.escape(SCOPE)}</p><p>这是同一台 I23 的版本替换，不是新增一台；batch-07 仍为 I22、I23 共 2/5，未部署。未写入游戏实例或正式结构。</p></section>
<section><h2>下一台与待定事项</h2><p>“下一台吧”授权继续既有规划 I24「量子异常观测阵列」的重设计候选，不是新增 I25 或新多方块批准。I24 候选制作由主任务继续，本摘要不宣称已完成或已获批准。</p><p>V8 的正式 Pattern、Controller tier、可执行配方、材料首建可达性及游戏运行仍待各自验收。此页为决策摘要，不冒充完整对话逐字档案。</p></section>
<p><a href="{relative_link(SOURCE / 'index.html')}">V8 原候选</a> · <a href="{relative_link(snapshot / '确认与校验清单.json')}">批准及校验清单</a></p></body></html>\n'''
    DISCUSSIONS.mkdir(parents=True, exist_ok=True)
    discussion.write_text(discussion_html, encoding='utf-8')
    (evidence / discussion.name).write_text(discussion_html, encoding='utf-8')
    row = {
        'id': 'I23', 'key': 'i23', 'candidate_key': 'i23', 'approved_version': 'V8',
        'candidate_version': manifest['candidate_version'], 'status': 'approved_archived_waiting_batch',
        'approval_quote': APPROVAL_QUOTE, 'continuation_quote': CONTINUATION_QUOTE,
        'approval_scope': SCOPE, 'approved_at': now.isoformat(),
        'source': str(SOURCE), 'archive': str(target),
        'source_zip': str(SOURCE_ZIP), 'source_zip_sha256': source_zip_check['sha256'],
        'source_files_sha256': source_hashes, 'structure_checks': checks,
        'source_candidate_approved_field': manifest['candidate_approved'],
        'supersedes_current_version': 'V6', 'same_machine_replacement': True,
        'counts_as_new_machine': False, 'previous_approved_entry': previous,
        'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
    }
    approval = {
        'record': 1, 'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
        'original_user_message_time': None, 'discussion_record': str(discussion),
        'batch': 'batch-07', 'batch_position': '02/05', 'entries': [row],
        'replacement_boundary': 'V8替代当前I23选择，V6历史批准与原件保留；同机版本替换不计为第3台。',
        'rule_snapshot_record': {'created_at': now.isoformat(), 'files': rules},
        'source_zip_validation': source_zip_check,
        'previous_index_sha256': hashlib.sha256(index_before).hexdigest(),
        'previous_v6_snapshot_files_sha256': previous_hashes,
        'previous_v6_archive_zip_sha256': previous['archive_zip_sha256'],
        'pending_batch_after_archive': next_pending,
        'source_metadata_boundary': '来源待审状态与candidate_approved=false原字节保留，批准只记在外部确认记录。',
        'accepted_design_scope': SCOPE, 'game_files_installed': False, 'game_verified': False,
    }
    write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I23 V8 外观批准归档</title>'
        '<style>body{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}</style>'
        f'<h1>I23 V8 外观批准归档 · batch-07 2/5</h1><p>{now.isoformat()}（Asia/Hong_Kong）</p>'
        '<p>用户原话：“i23 v8 ok”“下一台吧”。V8 替代当前 V6 选择；V6 历史批准快照保持原样。</p>'
        '<p>同台版本替换不重复计数；本批仍为 I22、I23 共2/5，尚未部署。</p>'
        '<p>已重新回读 NBT、Schematic、三维数据并逐格核验；来源与归档 ZIP 均验证文件集合、CRC 和逐文件 SHA256。</p>'
        f'<p>{html.escape(SCOPE)}</p><p>来源 manifest 的待审字段保留为历史元数据。</p>'
        '<p><a href="确认与校验清单.json">确认与校验清单</a></p></html>\n', encoding='utf-8')
    archived_hashes = file_hashes(snapshot)
    bundle = snapshot.with_suffix('.zip')
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in archived_hashes:
            package.write(snapshot / name, name)
    archive_check = verify_zip(bundle, archived_hashes)
    bundle.with_suffix('.zip.sha256').write_text(archive_check['sha256'] + '\n', encoding='ascii')
    if (file_hashes(SOURCE) != source_hashes or digest(SOURCE_ZIP) != source_zip_check['sha256']
            or file_hashes(previous_snapshot) != previous_hashes
            or digest(previous_bundle) != previous['archive_zip_sha256']):
        raise ValueError('来源或旧V6不可变归档在处理期间变化，拒绝更新索引。')

    entry = {key: value for key, value in row.items()
             if key not in ('source_files_sha256', 'previous_approved_entry')}
    entry.update({
        'approval_manifest': str(snapshot / '确认与校验清单.json'),
        'discussion_record': str(discussion), 'archive_zip': str(bundle),
        'archive_zip_sha256': archive_check['sha256'], 'nbt_sha256': checks['nbt_sha256'],
        'size_xyz': checks['declared_xyz'], 'controller': manifest['controller'],
        'port_count': 6, 'block_count': checks['block_count'], 'target_voltage_appearance': 'QCV',
        'previous_approved_versions': [previous],
    })
    index['entries'][position] = entry
    index['pending_batch'] = next_pending
    index['updated_at'] = now.isoformat()
    index['scope'] = '既有正式形态与部署状态保留；I22/I23外观批准，I23当前选择更新为V8并保留V6历史；batch-07仍为2/5，未部署。'
    index['latest_approval_snapshot'] = {'snapshot': str(snapshot), 'zip': str(bundle),
                                         'zip_sha256': archive_check['sha256']}
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = {'preserved_copy': str(evidence / 'previous-current-index.json'),
                               'sha256': hashlib.sha256(index_before).hexdigest()}
    index.setdefault('_change_records', []).append({
        'record': len(index.get('_change_records', [])) + 1, 'time': now.isoformat(),
        'reason': '用户明确表示“i23 v8 ok”，并要求“下一台吧”',
        'deleted': '无；V6批准快照、旧索引原字节、V8候选及来源ZIP保留',
        'added': 'I23 V8独立批准快照、逐格与ZIP核验、V6历史选择及I24继续授权',
        'modified': '同台I23当前选择由V6替换为V8；批准总数不变，batch-07仍2/5',
        'purpose': '准确记录外观版本批准，不重复计数，不冒充正式功能或游戏验收',
    })
    if INDEX.read_bytes() != index_before:
        raise ValueError('归档期间当前索引变化，拒绝覆盖。')
    write_json(INDEX, index)
    print(json.dumps({
        'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': archive_check['sha256'],
        'discussion': str(discussion), 'source_files': len(source_hashes),
        'archive_files': len(archived_hashes), 'source_zip_sha256': source_zip_check['sha256'],
        'nbt_sha256': checks['nbt_sha256'], 'schem_sha256': checks['schem_sha256'],
        'size_xyz': checks['declared_xyz'], 'blocks': checks['block_count'],
        'approved_structure_forms': index['approved_structure_forms'],
        'pending_batch': next_pending, 'archive_zip_validation': archive_check,
        'source_unchanged': True, 'previous_v6_unchanged': True,
        'nbt_schematic_viewer_per_block_equal': True, 'verified': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
