# -*- coding: utf-8 -*-
"""保存 I05 V5 外观批准，不改正式 Pattern 或五台批次计数。"""
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
from pathlib import Path

import nbtlib

from structure_size_baseline import ROOT, require


ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I05_稳定介质再生塔_HBV塔冠内置反应段_滤芯接口移至X6_V5_20261026'
RULES = (
    'rule/系统角色设定.md', 'rule/崩坏三-gtl (hk3gtl) 项目规则.md',
    'rule/当前多方块设计规则.md', 'rule/巨构提示词.txt',
)
QUOTE = 'i05 ok  , next'
SCOPE = 'I05 V5建筑外观及对应结构文件；只批准FILTER占位接口迁至[6,3,16]，不批准正式Pattern或实例文件更新。'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def state_name(tag) -> str:
    name = str(tag['Name'])
    properties = tag.get('Properties', {})
    return name + ('[' + ','.join(f'{k}={v}' for k, v in sorted(properties.items())) + ']'
                   if properties else '')


def decode_varints(raw: bytes) -> list[int]:
    values, value, shift = [], 0, 0
    for byte in raw:
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
            if shift > 28:
                raise ValueError('Schematic VarInt 超过长度上限。')
        else:
            values.append(value)
            value, shift = 0, 0
    if shift:
        raise ValueError('Schematic BlockData 截断。')
    return values


def verify() -> dict:
    design = json.loads((SOURCE / '设计与检查.json').read_text(encoding='utf-8'))
    blueprint = json.loads((SOURCE / 'blueprint.json').read_text(encoding='utf-8'))
    meta = design['data']
    if (meta['candidate_version'] != 'I05-HBV-H49-V5'
            or meta['controller'] != [20, 3, 16] or meta['size'] != [43, 49, 37]):
        raise ValueError('I05 V5 候选身份、主控或尺寸发生变化。')
    nbt_path, = SOURCE.glob('*.nbt')
    schem_path, = SOURCE.glob('*.schem')
    nbt = nbtlib.load(nbt_path)
    size = [int(v) for v in nbt['size']]
    palette = [state_name(item) for item in nbt['palette']]
    cells = {}
    for block in nbt['blocks']:
        pos = tuple(int(v) for v in block['pos'])
        if pos in cells or not all(0 <= pos[i] < size[i] for i in range(3)):
            raise ValueError('NBT 存在重复或越界坐标。')
        cells[pos] = palette[int(block['state'])]
    expected = {tuple(block['pos']): block['state'] for block in blueprint['blocks']}
    if cells != expected or size != [43, 49, 37] or len(cells) != 7519:
        raise ValueError('I05 V5 蓝图与 NBT 逐格不一致。')
    size_check = require({'key': 'I05', 'size': size,
                          'blocks': [{'pos': list(pos)} for pos in cells]})
    if cells.get((20, 3, 16)) != 'minecraft:diamond_block':
        raise ValueError('I05 主控标记位置不符。')
    ports = [p for p in meta['ports'] if p['id'] == 'FILTER']
    if len(ports) != 1 or ports[0]['pos'] != [6, 3, 16]:
        raise ValueError('FILTER 目标坐标不符。')
    if cells.get((6, 3, 16)) != 'hk3gtl:industrial_port_casing':
        raise ValueError('FILTER 新占位位置不符。')
    if cells.get((14, 3, 16)) != 'hk3gtl:voltage_machine_casing_hbv':
        raise ValueError('FILTER 旧位置没有恢复 HBV 外壳。')

    payload_text = (SOURCE / 'data.js').read_text(encoding='utf-8')
    encoded, = re.findall(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', payload_text)
    payload = json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)))
    viewer_cells = {}
    width, height, depth = size
    for state, group in zip(payload['palette'], payload['groups']):
        for packed in group:
            y, rem = divmod(packed, width * depth)
            z, x = divmod(rem, width)
            viewer_cells[(x, y, z)] = state
    if viewer_cells != cells:
        raise ValueError('I05 V5 三维预览与 NBT 逐格不一致。')

    schematic = nbtlib.load(schem_path)
    if [int(schematic[k]) for k in ('Width', 'Height', 'Length')] != size:
        raise ValueError('Schematic 尺寸与 NBT 不同。')
    schem_palette = {int(value): key for key, value in schematic['Palette'].items()}
    raw_values = bytes(int(v) & 255 for v in schematic['BlockData'])
    values = decode_varints(raw_values)
    if len(values) != width * height * depth:
        raise ValueError('Schematic BlockData 体积错误。')
    schematic_cells = {}
    for packed, state_id in enumerate(values):
        state = schem_palette[state_id]
        if state != 'minecraft:air':
            y, rem = divmod(packed, width * depth)
            z, x = divmod(rem, width)
            schematic_cells[(x, y, z)] = state
    if schematic_cells != cells:
        raise ValueError('Schematic 与 NBT 逐格不一致。')
    return {
        'size_baseline': size_check, 'size_xyz': size, 'block_count': len(cells),
        'palette_count': len(set(cells.values())), 'controller': [20, 3, 16],
        'ports': len(meta['ports']), 'filter_port': [6, 3, 16],
        'nbt_sha256': digest(nbt_path), 'schem_sha256': digest(schem_path),
        'nbt_blueprint_viewer_schematic_equal': True,
    }


def main() -> None:
    index_before = INDEX.read_bytes()
    index = json.loads(index_before.decode('utf-8'))
    entries = [row for row in index['entries'] if row['id'] == 'I05']
    if len(entries) != 1:
        raise ValueError('索引中必须有且仅有一个既有 I05 条目。')
    current = entries[0]
    if current.get('latest_appearance_approval', {}).get('version') == 'V5':
        raise ValueError('I05 V5 已归档，拒绝重复计入。')
    pending = copy.deepcopy(index['pending_batch'])
    if pending['id'] != 'batch-07' or pending['count'] != 3:
        raise ValueError('批次进度已变化，拒绝改写。')
    before_hashes = file_hashes(SOURCE)
    checks = verify()
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_I05_V5_HBV_外观已确认未接入'
    snapshot.mkdir(parents=True, exist_ok=False)
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(index_before)
    rule_hashes = {}
    for relative in RULES:
        source = ROOT / relative
        shutil.copy2(source, evidence / source.name)
        rule_hashes[relative] = digest(source)
    shutil.copy2(Path(__file__), evidence / Path(__file__).name)
    target = snapshot / SOURCE.name
    shutil.copytree(SOURCE, target)
    if file_hashes(target) != before_hashes or file_hashes(SOURCE) != before_hashes:
        raise ValueError('候选原件或快照逐文件哈希不一致。')

    discussions = ROOT / 'doc/HK3GTL-内测5/讨论记录'
    discussion = discussions / f'{now:%Y-%m-%d_%H-%M-%S}_I05V5外观批准与I06继续.html'
    rel = lambda path: html.escape(os.path.relpath(path, discussion.parent).replace('\\', '/'))
    summary = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I05 V5外观批准与I06继续</title><style>body{{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}}section{{border-top:1px solid #ccd6d8;padding:16px 0}}code{{overflow-wrap:anywhere}}</style></head><body><h1>I05 V5外观批准，与I06继续</h1><p>归档时间：{now.isoformat()}（Asia/Hong_Kong，UTC+08:00）；原消息时间取自本地会话记录，见完整对话档案。</p><section><h2>负责人决定</h2><p>原话：“{html.escape(QUOTE)}”。I05 V5滤芯接口移至X6外观与结构文件获准，继续下一台I06「崩坏能燃料调配厂」。</p></section><section><h2>归档与边界</h2><p>V5尺寸43×49×37（宽×高×深），7,519个实体方块、13种材料；主控[20,3,16]，FILTER接口[6,3,16]。NBT、Schematic、蓝图及三维预览逐格核对一致。</p><p>{html.escape(SCOPE)} V5以不可变快照保存；不改正式Pattern/实例，不作为新机器重复计入batch-07，批次仍为{pending['count']}/5。正式FILTER能力仍需另行验证。</p></section><p><a href="{rel(SOURCE / '三维评审.html')}">I05 V5原候选评审页</a> · <a href="{rel(target)}">不可变批准快照</a> · <a href="{rel(snapshot / '确认与校验清单.json')}">归档核验</a></p></body></html>'''
    discussions.mkdir(parents=True, exist_ok=True)
    discussion.write_text(summary, encoding='utf-8')
    (evidence / discussion.name).write_text(summary, encoding='utf-8')

    row = {
        'version': 'V5', 'candidate_version': 'I05-HBV-H49-V5',
        'status': 'approved_archived_not_deployed', 'approval_quote': QUOTE,
        'approved_at': now.isoformat(), 'approval_scope': SCOPE,
        'source': str(SOURCE), 'archive': str(target), 'files_sha256': before_hashes,
        'structure_checks': checks, 'source_candidate_metadata_preserved': True,
        'same_machine_revision': True, 'counts_as_new_machine': False,
        'formal_pattern_unchanged': True, 'game_files_installed': False,
        'game_verified': False, 'approval_manifest': str(snapshot / '确认与校验清单.json'),
        'discussion_record': str(discussion),
    }
    manifest = {
        'record': 1, 'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
        'original_user_message_time': '2026-10-26T00:25:14+08:00',
        'machine': 'I05', 'approval_type': 'same-machine appearance and structure revision',
        'source_files_sha256': before_hashes, 'rule_files_sha256': rule_hashes,
        'checks': checks, 'approved_revision': row,
        'formal_boundary': '既有正式Pattern仍保留原I05版本；V5只归档外观批准，不改模组资源或游戏实例。',
        'batch_before_after': {'before': pending, 'after': pending},
        'game_files_installed': False, 'game_verified': False,
    }
    write_json(snapshot / '确认与校验清单.json', manifest)
    (snapshot / '确认接入.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I05 V5外观批准归档</title>'
        '<style>body{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}</style>'
        f'<h1>I05 V5 外观批准归档 · {now.isoformat()}</h1>'
        '<p>用户原话：“i05 ok , next”。同机修订不增加批次台数；正式Pattern与实例未改。</p>'
        '<p>7,519方块，43×49×37（宽×高×深），主控[20,3,16]，FILTER[6,3,16]。蓝图、NBT、Schematic与三维数据逐格核验通过。</p>'
        '<p>外观批准不代表FILTER实际能力、配方或游戏运行已验收。</p>'
        '<p><a href="确认与校验清单.json">确认与校验清单</a></p></html>\n', encoding='utf-8')
    snapshot_hashes = file_hashes(snapshot)
    bundle = snapshot.with_suffix('.zip')
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in snapshot_hashes:
            package.write(snapshot / name, name)
    with zipfile.ZipFile(bundle) as package:
        if package.testzip() is not None:
            raise ValueError('批准归档 ZIP CRC 校验失败。')
        names = set(package.namelist())
        if names != set(snapshot_hashes):
            raise ValueError('批准归档 ZIP 文件集合错误。')
        if any(hashlib.sha256(package.read(name)).hexdigest() != digest_value
               for name, digest_value in snapshot_hashes.items()):
            raise ValueError('批准归档 ZIP 内容哈希不一致。')
    bundle_hash = digest(bundle)
    bundle.with_suffix('.zip.sha256').write_text(bundle_hash + '\n', encoding='ascii')
    row.update({'archive_zip': str(bundle), 'archive_zip_sha256': bundle_hash})
    idx_row = next(item for item in index['entries'] if item['id'] == 'I05')
    history = list(idx_row.get('approved_appearance_revisions', []))
    history.append(row)
    idx_row['approved_appearance_revisions'] = history
    idx_row['latest_appearance_approval'] = row
    idx_row['formal_resource_version_unchanged'] = idx_row.get('approved_version')
    index['latest_appearance_revision_approval'] = {
        'id': 'I05', 'version': 'V5', 'snapshot': str(snapshot),
        'zip': str(bundle), 'zip_sha256': bundle_hash,
    }
    index['updated_at'] = now.isoformat()
    index.setdefault('_change_records', []).append({
        'record': len(index.get('_change_records', [])) + 1, 'time': now.isoformat(),
        'reason': '用户明确批准 I05 V5 并要求继续下一台',
        'deleted': '无；I05 V2/V3/V4/V5来源候选与既有正式文件均保留',
        'added': 'I05 V5不可变外观批准快照、逐格校验与讨论记录',
        'modified': '只在I05索引行增加外观修订批准历史；正式资源及batch-07不变',
        'purpose': '记录同机修订获准，不把外观批准误记为实装或新增机器',
    })
    if INDEX.read_bytes() != index_before:
        raise ValueError('处理期间批准索引已变化，拒绝覆盖。')
    write_json(INDEX, index)
    print(json.dumps({
        'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': bundle_hash,
        'discussion': str(discussion), 'batch_unchanged': pending,
        'checks': checks, 'source_unchanged': file_hashes(SOURCE) == before_hashes,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
