# -*- coding: utf-8 -*-
"""Archive the explicitly approved I22 candidate without changing its source."""
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
SOURCE = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023'
SOURCE_ZIP = ROOT / 'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023.zip'
STATIC_REVIEW = ROOT / 'logs/i22-wsv-ultimate-v1-20261023/final-static-review.json'
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
    if pending['id'] != 'batch-07' or pending['approved_machine_ids']:
        raise ValueError('batch-07 已变化；拒绝重复或错批归档。')
    if any(row['id'] == 'I22' for row in index['entries']):
        raise ValueError('索引已存在 I22，拒绝重复计数。')

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_batch-07_01of05_I22_WSV_已确认'
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

    source_hashes = file_hashes(SOURCE)
    manifest_path = SOURCE / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('key') != 'i22' or manifest.get('candidate_approved') is not False:
        raise ValueError('I22 来源身份或历史候选状态不符合预期。')
    structure_path = SOURCE / 'i22/i22-wsv-ultimate-isolated-field-v1.nbt'
    schem_path = SOURCE / 'i22/i22-wsv-ultimate-isolated-field-v1.schem'
    nbt = nbtlib.load(structure_path)
    size_check = require({
        'key': 'I22', 'size': [int(v) for v in nbt['size']],
        'blocks': [{'pos': [int(v) for v in b['pos']]} for b in nbt['blocks']],
    })
    size_check.update({'nbt_file': structure_path.relative_to(SOURCE).as_posix(),
                       'nbt_sha256': digest(structure_path),
                       'schem_sha256': digest(schem_path),
                       'block_count': len(nbt['blocks']),
                       'check_scope': '重新读取来源NBT并核对69座占地总表；不代表游戏成型。'})

    if not SOURCE_ZIP.is_file() or not STATIC_REVIEW.is_file():
        raise FileNotFoundError('I22 完成交付 ZIP 或静态复核凭据缺失。')
    with zipfile.ZipFile(SOURCE_ZIP) as package:
        if package.testzip() is not None:
            raise ValueError('I22 来源 ZIP CRC 校验失败。')
        names = package.namelist()
        for wanted in (structure_path.name, schem_path.name, 'manifest.json'):
            candidates = [name for name in names if name == wanted or name.endswith('/' + wanted)]
            if len(candidates) != 1:
                raise ValueError(f'来源 ZIP 中 {wanted} 路径不唯一或不存在。')
            data = package.read(candidates[0])
            expected = source_hashes.get(wanted)
            if wanted == structure_path.name:
                expected = source_hashes['i22/' + wanted]
            elif wanted == schem_path.name:
                expected = source_hashes['i22/' + wanted]
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f'来源 ZIP 中 {wanted} 与候选原件不一致。')

    target = snapshot / SOURCE.name
    shutil.copytree(SOURCE, target)
    if file_hashes(target) != source_hashes or file_hashes(SOURCE) != source_hashes:
        raise ValueError('候选原件在复制期间变化，拒绝写入索引。')
    shutil.copy2(SOURCE_ZIP, evidence / SOURCE_ZIP.name)
    shutil.copy2(STATIC_REVIEW, evidence / STATIC_REVIEW.name)

    blockers = ['batch-07 当前为1/5，未达到结构接入门槛。',
                'I22 的外观与本版本结构文件获批；未批准Pattern、控制器注册、工艺闭环或游戏运行。']
    next_pending = dict(pending, approved_machine_ids=['I22'], count=1,
                        required=5, deployment_eligible=False,
                        deployment_blockers=blockers)
    discussion_name = f'{now:%Y-%m-%d_%H-%M-%S}_I22明确批准与I23候选继续.html'
    discussion_path = DISCUSSIONS / discussion_name
    discussion_path.parent.mkdir(parents=True, exist_ok=True)
    discussion_html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I22明确批准与I23候选继续</title>
<style>body{{max-width:960px;margin:32px auto;padding:0 20px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}}section{{border-top:1px solid #ccd6d8;padding:16px 0}}code{{overflow-wrap:anywhere}}</style></head><body>
<h1>I22 明确批准与 I23 候选继续</h1><p>记录时间：{html.escape(now.isoformat())}（Asia/Hong_Kong）。</p>
<section><h2>负责人原话</h2><p><q>i22 ok</q></p><p><q>下一台吧</q></p>
<p>“i22 ok”按本轮上下文登记为对 I22 当前候选外观及对应结构文件的明确批准；“下一台吧”授权继续制作 I23 候选，不代表批准 I23。</p></section>
<section><h2>I22 批准边界</h2><p>获批来源为 <a href="../../../deliveries/{html.escape(SOURCE.name)}/index.html">I22 原候选交付页</a>，原候选目录与 ZIP 保持原字节，并复制到
<a href="../../../deliveries/多方块确认归档/{html.escape(snapshot.name)}/确认与校验清单.json">本次确认归档</a>。</p>
<p>候选实体范围 402×250×346（X×Y×Z），1,408,427 方块；原静态复核与尺寸检查随归档保存。索引将 batch-07 从0/5推进为1/5。</p>
<p>本次批准接受当前 I22 建筑版本。它不批准正式 Pattern、注册控制器、配方、研究/生存获取链或游戏运行状态；尚未部署。</p></section>
<section><h2>I23 状态</h2><p>开始制作崩坏能相变释能机的独立待审候选。候选完成、预览审查或本记录均不等于外观批准。</p></section>
<p>逐文件身份、规则哈希、来源 ZIP、NBT 与批次状态见上述确认清单。</p></body></html>\n'''
    discussion_path.write_text(discussion_html, encoding='utf-8')

    row = {
        'id': 'I22', 'key': 'i22', 'candidate_key': 'i22',
        'candidate_version': manifest['candidate_version'],
        'status': 'approved_archived_waiting_batch',
        'approval_quote': 'i22 ok', 'continuation_quote': '下一台吧',
        'approval_message_time': '本轮上下文记录时间见归档时间；用户消息精确发送时间不可用。',
        'approval_scope': 'I22当前候选外观及对应结构文件；接受本版本架构。未批准正式Pattern、游戏运行、配方或生存闭环。',
        'source': str(SOURCE), 'archive': str(target),
        'source_zip': str(SOURCE_ZIP), 'source_zip_sha256': digest(SOURCE_ZIP),
        'source_files_sha256': source_hashes, 'structure_checks': size_check,
        'candidate_candidate_approved_field': False,
        'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
    }
    approval = {
        'record': 1, 'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
        'discussion_record': str(discussion_path),
        'batch': 'batch-07', 'batch_position': '01/05', 'entries': [row],
        'rule_read_record': {'read_at': now.isoformat(), 'files': rules},
        'previous_index_sha256': hashlib.sha256(index_before).hexdigest(),
        'pending_batch_after_archive': next_pending,
        'source_metadata_boundary': '来源manifest的candidate_approved=false作为历史元数据原样保留；当前批准只记在外部确认记录。',
        'accepted_design_scope': 'I22当前四堆隔离外场建筑版本；不将该批准外推为功能、Pattern或游戏验收。',
        'game_files_installed': False, 'game_verified': False,
        '_change_record': {'record': 1, 'time': now.isoformat(), 'deleted': '无',
                           'added': 'I22明确批准凭据、不可变原件、源ZIP与NBT几何核验',
                           'modified': 'batch-07批准数量由0/5推进为1/5；正式资源与游戏状态不变',
                           'purpose': '记录用户批准范围，并继续逐台结构审核'},
    }
    write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I22 外观批准归档</title>'
        '<style>body{max-width:960px;margin:32px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#23343d}'
        'section{border-top:1px solid #ccd6d8;padding:16px 0}</style>'
        f'<h1>I22 外观批准归档 · batch-07 1/5</h1><p>{html.escape(now.isoformat())}（Asia/Hong_Kong）</p>'
        '<p>负责人明确表示“i22 ok”；批准对象为当前候选建筑外观和对应结构文件。</p>'
        '<p>候选原件按文件SHA256逐份复制，来源ZIP CRC及结构文件身份已核验；NBT实体范围重新解析通过。</p>'
        '<section><p>尚未部署。批准不代表正式Pattern、控制器注册、配方、研究/生存获取或游戏运行已经验收。</p><ul>'
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
        'id': 'I22', 'key': 'i22', 'candidate_key': 'i22',
        'candidate_version': manifest['candidate_version'],
        'status': 'approved_archived_waiting_batch',
        'archive': str(target), 'approval_manifest': str(snapshot / '确认与校验清单.json'),
        'approval_quote': 'i22 ok', 'approval_scope': row['approval_scope'],
        'discussion_record': str(discussion_path),
        'archive_zip': str(bundle), 'archive_zip_sha256': archive_sha,
        'source_zip_sha256': digest(SOURCE_ZIP),
        'nbt_sha256': size_check['nbt_sha256'], 'size_xyz': size_check['declared_xyz'],
        'controller': manifest['controller'], 'port_count': len(manifest['ports']),
        'block_count': size_check['block_count'], 'target_voltage_appearance': 'WSV',
        'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
    })
    index['approved_structure_forms'] += 1
    index['pending_batch'] = next_pending
    index['updated_at'] = now.isoformat()
    index['scope'] = '21种既有正式形态及batch-06五台部署状态保留；I22外观获批并归档，batch-07为1/5，未部署。'
    index['batch_rule'] = '每累计5台明确批准后按各自归档接入2.9；负责人更新后再检查2.9.2。当前batch-07为1/5。'
    index['latest_approval_snapshot'] = {'snapshot': str(snapshot), 'zip': str(bundle),
                                         'zip_sha256': archive_sha}
    index.setdefault('_change_records', []).append({
        'record': len(index.get('_change_records', [])) + 1, 'time': now.isoformat(),
        'reason': '负责人明确表示“i22 ok”，并要求继续下一台',
        'deleted': '无；旧索引、I22候选原件与既有批准归档均保留',
        'added': 'I22外观批准与不可变归档；batch-07由0/5推进为1/5；I23继续制作',
        'modified': '仅推进批准索引，不变更正式资源或游戏文件',
        'purpose': '逐台记录外观审批，区分候选批准与游戏功能验收'})
    if INDEX.read_bytes() != index_before:
        raise ValueError('归档期间当前索引被其他任务修改；保留生成的证据，但拒绝覆盖索引。')
    write_json(INDEX, index)
    print(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle),
                      'zip_sha256': archive_sha, 'discussion': str(discussion_path),
                      'files': len(archived_hashes), 'source_zip_sha256': digest(SOURCE_ZIP),
                      'size_xyz': size_check['declared_xyz'], 'blocks': size_check['block_count'],
                      'pending_batch': next_pending, 'verified': True},
                     ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
