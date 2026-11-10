# -*- coding: utf-8 -*-
"""Archive the explicitly approved I23 V6 candidate without changing its source."""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib

from structure_size_baseline import ROOT, require


ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I23_崩坏能相变释能机_相变舱原位接口与I22式审阅页_V6_20261024'
SOURCE_ZIP = ROOT / 'deliveries/I23_崩坏能相变释能机_相变舱原位接口与I22式审阅页_V6_20261024.zip'
STRUCTURE = SOURCE / 'i23/hk3gtl-i23-flush-phase-v6-20261024.nbt'
SCHEM = SOURCE / 'i23/hk3gtl-i23-flush-phase-v6-20261024.schem'
DISCUSSIONS = ROOT / 'doc/HK3GTL-内测5/讨论记录'
RULES = (
    'rule/rules.md', 'rule/系统角色设定.md',
    'rule/崩坏三-gtl (hk3gtl) 项目规则.md',
    'rule/hk3gtl java文件变更备注规范.md',
    'rule/当前多方块设计规则.md', 'rule/巨构提示词.txt',
)


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


def main() -> None:
    index_before = INDEX.read_bytes()
    index = json.loads(index_before.decode('utf-8'))
    pending = index['pending_batch']
    if pending['id'] != 'batch-07' or pending['approved_machine_ids'] != ['I22']:
        raise ValueError('batch-07 已变化；拒绝重复或错批归档。')
    if any(row['id'] == 'I23' for row in index['entries']):
        raise ValueError('索引已存在 I23，拒绝重复计数。')

    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('key') != 'i23' or manifest.get('candidate_version') != '相变舱原位接口 V6・待审':
        raise ValueError('I23 来源身份或版本不符合预期。')
    source_hashes = file_hashes(SOURCE)
    if not SOURCE_ZIP.is_file() or not STRUCTURE.is_file() or not SCHEM.is_file():
        raise FileNotFoundError('I23 来源 ZIP、NBT 或 Schem 缺失。')
    with zipfile.ZipFile(SOURCE_ZIP) as package:
        if package.testzip() is not None:
            raise ValueError('I23 来源 ZIP CRC 校验失败。')
        names = package.namelist()
        for relative, expected in source_hashes.items():
            matches = [name for name in names if name.endswith('/' + relative)]
            if len(matches) != 1 or hashlib.sha256(package.read(matches[0])).hexdigest() != expected:
                raise ValueError(f'I23 来源 ZIP 与候选原件不一致：{relative}')

    nbt = nbtlib.load(STRUCTURE)
    size_check = require({
        'key': 'I23', 'size': [int(v) for v in nbt['size']],
        'blocks': [{'pos': [int(v) for v in b['pos']]} for b in nbt['blocks']],
    })
    size_check.update({
        'nbt_file': STRUCTURE.relative_to(SOURCE).as_posix(),
        'nbt_sha256': digest(STRUCTURE), 'schem_sha256': digest(SCHEM),
        'block_count': len(nbt['blocks']),
        'check_scope': '重新读取来源NBT并核对69座占地总表；不代表游戏成型。',
    })

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_batch-07_02of05_I23_QCV_已确认'
    snapshot.mkdir(parents=True, exist_ok=False)
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(index_before)
    rules = []
    for relative in RULES:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, evidence / source.name)
        rules.append({'path': relative, 'sha256': digest(source),
                      'lines': len(source.read_text(encoding='utf-8').splitlines())})
    target = snapshot / SOURCE.name
    shutil.copytree(SOURCE, target)
    if file_hashes(target) != source_hashes or file_hashes(SOURCE) != source_hashes:
        raise ValueError('I23 原候选在复制期间变化。')
    shutil.copy2(SOURCE_ZIP, evidence / SOURCE_ZIP.name)

    blockers = [
        'batch-07 当前为2/5，未达到结构接入门槛。',
        'I23 获批范围仅含 V6 外观与对应结构文件；Pattern、配方、研究/生存闭环和游戏运行尚未验收。',
    ]
    next_pending = dict(pending, approved_machine_ids=['I22', 'I23'], count=2,
                        required=5, deployment_eligible=False,
                        deployment_blockers=blockers)
    discussion_path = DISCUSSIONS / f'{now:%Y-%m-%d_%H-%M-%S}_I23V6明确批准与I24候选继续.html'
    discussion_html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I23 V6明确批准与I24候选继续</title>
<style>body{{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}}section{{border-top:1px solid #ccd6d8;padding:16px 0}}code{{overflow-wrap:anywhere}}</style></head><body>
<h1>I23 V6 明确批准与 I24 候选继续</h1><p>记录时间：{html.escape(now.isoformat())}（Asia/Hong_Kong）。</p>
<section><h2>负责人原话</h2><p><q>i23 ok</q></p><p><q>下一台吧</q></p>
<p>“i23 ok”按本轮上下文登记为对 I23 当前 V6 候选外观及对应结构文件的明确批准；“下一台吧”授权继续制作既有规划中的 I24 候选。</p></section>
<section><h2>I23 批准边界</h2><p>批准来源为 <a href="../../../deliveries/{html.escape(SOURCE.name)}/index.html">I23 V6 原候选交付页</a>；候选原件和 ZIP 保持原字节，并复制到本目录的不可变快照。</p>
<p>确认仅涉及 V6 建筑外观与对应结构文件，不代表正式 Pattern、配方、研究/生存获取或游戏运行验收。</p></section>
<section><h2>批次状态</h2><p>batch-07 由 1/5 更新为 2/5，未达到接入条件；未写入正式资源或游戏实例。</p></section>
<p>逐文件身份、规则哈希、来源 ZIP、NBT 与批次状态见 <a href="../../../deliveries/多方块确认归档/{html.escape(snapshot.name)}/确认与校验清单.json">确认与校验清单</a>。</p></body></html>\n'''
    DISCUSSIONS.mkdir(parents=True, exist_ok=True)
    discussion_path.write_text(discussion_html, encoding='utf-8')

    row = {
        'id': 'I23', 'key': 'i23', 'candidate_key': 'i23',
        'candidate_version': manifest['candidate_version'],
        'status': 'approved_archived_waiting_batch',
        'approval_quote': 'i23 ok', 'continuation_quote': '下一台吧',
        'approval_scope': 'I23当前V6外观及对应结构文件；未批准正式Pattern、游戏运行、配方或生存闭环。',
        'source': str(SOURCE), 'archive': str(target),
        'source_zip': str(SOURCE_ZIP), 'source_zip_sha256': digest(SOURCE_ZIP),
        'source_files_sha256': source_hashes, 'structure_checks': size_check,
        'source_candidate_approved_field': manifest.get('candidate_approved'),
        'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
    }
    approval = {
        'record': 1, 'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
        'discussion_record': str(discussion_path), 'batch': 'batch-07',
        'batch_position': '02/05', 'entries': [row],
        'rule_read_record': {'read_at': now.isoformat(), 'files': rules},
        'previous_index_sha256': hashlib.sha256(index_before).hexdigest(),
        'pending_batch_after_archive': next_pending,
        'source_metadata_boundary': '来源 manifest 的待审状态作为历史元数据原样保留；批准只记在外部确认记录。',
        'accepted_design_scope': row['approval_scope'],
        'game_files_installed': False, 'game_verified': False,
    }
    write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I23 V6 外观批准归档</title>'
        '<style>body{max-width:960px;margin:32px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}'
        'section{border-top:1px solid #ccd6d8;padding:16px 0}</style>'
        f'<h1>I23 V6 外观批准归档 · batch-07 2/5</h1><p>{html.escape(now.isoformat())}（Asia/Hong_Kong）</p>'
        '<p>负责人明确表示“i23 ok”；批准对象为当前 V6 候选外观和对应结构文件。</p>'
        '<p>候选原件逐文件 SHA256、来源 ZIP CRC 与内容、NBT 实体范围已核验。</p>'
        '<section><p>本批未达到接入门槛，尚未部署。Pattern、配方、研究/生存获取与游戏运行尚未验收。</p><ul>'
        + ''.join(f'<li>{html.escape(item)}</li>' for item in blockers)
        + '</ul></section><p>详情见 <a href="确认与校验清单.json">确认与校验清单</a>。</p></html>\n',
        encoding='utf-8')

    archived_hashes = file_hashes(snapshot)
    bundle = ARCHIVES / f'{snapshot.name}.zip'
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in archived_hashes:
            package.write(snapshot / name, name)
    with zipfile.ZipFile(bundle) as package:
        if package.testzip() is not None:
            raise ValueError('确认归档 ZIP CRC 校验失败。')
        for name, expected in archived_hashes.items():
            if hashlib.sha256(package.read(name)).hexdigest() != expected:
                raise ValueError(f'确认归档 ZIP 内容校验失败：{name}')
    archive_sha = digest(bundle)
    index['entries'].append({
        'id': 'I23', 'key': 'i23', 'candidate_key': 'i23',
        'candidate_version': manifest['candidate_version'],
        'status': 'approved_archived_waiting_batch',
        'archive': str(target), 'approval_manifest': str(snapshot / '确认与校验清单.json'),
        'approval_quote': 'i23 ok', 'approval_scope': row['approval_scope'],
        'discussion_record': str(discussion_path),
        'archive_zip': str(bundle), 'archive_zip_sha256': archive_sha,
        'source_zip_sha256': digest(SOURCE_ZIP), 'nbt_sha256': size_check['nbt_sha256'],
        'size_xyz': size_check['declared_xyz'], 'controller': manifest['controller'],
        'port_count': len(manifest['ports']), 'block_count': size_check['block_count'],
        'target_voltage_appearance': 'QCV', 'formal_resource_present': False,
        'game_files_installed': False, 'game_verified': False,
    })
    index['approved_structure_forms'] += 1
    index['pending_batch'] = next_pending
    index['updated_at'] = now.isoformat()
    index['scope'] = '21种既有正式形态及batch-06五台部署状态保留；I22/I23外观获批并归档，batch-07为2/5，未部署。'
    index['batch_rule'] = '每累计5台明确批准后按各自归档接入2.9；负责人更新后再检查2.9.2。当前batch-07为2/5。'
    index['latest_approval_snapshot'] = {'snapshot': str(snapshot), 'zip': str(bundle),
                                         'zip_sha256': archive_sha}
    index.setdefault('_change_records', []).append({
        'record': len(index.get('_change_records', [])) + 1, 'time': now.isoformat(),
        'reason': '负责人明确表示“i23 ok”，并要求继续下一台',
        'deleted': '无；保留原索引、I23 V6候选原件与ZIP',
        'added': 'I23 V6外观批准与不可变归档；batch-07由1/5推进为2/5；I24继续制作',
        'modified': '仅推进批准索引，不变更正式资源或游戏文件',
        'purpose': '记录结构外观批准，并将其与游戏功能验收区分'})
    if INDEX.read_bytes() != index_before:
        raise ValueError('归档期间当前索引被其他任务修改；拒绝覆盖索引。')
    write_json(INDEX, index)
    print(json.dumps({
        'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': archive_sha,
        'discussion': str(discussion_path), 'files': len(archived_hashes),
        'source_zip_sha256': digest(SOURCE_ZIP), 'size_xyz': size_check['declared_xyz'],
        'blocks': size_check['block_count'], 'pending_batch': next_pending,
        'verified': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
