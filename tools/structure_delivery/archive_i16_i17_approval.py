# -*- coding: utf-8 -*-
"""保存 I16/I17 明确外观批准的不可变副本，并只推进 batch-06 批次索引。

【变更记录 #1】2026-10-22 22:34:39（结构批准归档，不增加模组修订号）
- 删除：无；不改候选交付原件、旧确认归档及正式游戏资源。
- 新增：两台批准证据、源文件及生成器身份、NBT 实体尺寸复核和归档 ZIP 回读。
- 修改：当前索引按唯一机器编号累计批准数量；旧索引先按原字节保存。
- 用途：落实负责人 I16/I17 的明确批准，同时保留电压首建、Pattern 与实机未验收边界。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib

from archive_reviewed_structures import digest
from structure_size_baseline import ROOT, require


ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
RULES = (
    'rule/rules.md', 'rule/系统角色设定.md',
    'rule/崩坏三-gtl (hk3gtl) 项目规则.md',
    'rule/hk3gtl java文件变更备注规范.md',
    'rule/当前多方块设计规则.md', 'rule/巨构提示词.txt',
)
ITEMS = (
    {
        'id': 'I16', 'key': 'i16', 'version': 'V3 HDV 双门架定轴校准',
        'folder': 'I16_魂钢精密加工中心_双门架定轴校准_V3_HDV_20261021',
        'quote': 'i16 ok\n继续下一步', 'voltage': 'HDV',
        'package': 'I16_V3_HDV双门架定轴校准_结构与预览.zip',
        'generator': 'build_i16_hdv_precision_center_v3.py',
    },
    {
        'id': 'I17', 'key': 'i17', 'version': 'V1 QSV 阶梯精馏园区',
        'folder': 'I17_浓缩崩坏能燃料精制厂_阶梯精馏园区_V1_QSV_20261021',
        'quote': 'i17 ok\n继续下一步', 'voltage': 'QSV',
        'package': 'I17_V1_QSV阶梯精馏园区_控制器定位修订_结构与预览.zip',
        'generator': 'build_i17_qsv_concentration_refinery_v1.py',
    },
)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def structure_check(source: Path, machine: str) -> dict:
    paths = list(source.glob('*.nbt'))
    if len(paths) != 1:
        raise ValueError(f'{machine} 结构数量不是一份：{paths}')
    data = nbtlib.load(paths[0])
    result = require({
        'key': machine, 'size': [int(v) for v in data['size']],
        'blocks': [{'pos': [int(v) for v in b['pos']]} for b in data['blocks']],
    })
    result.update({'nbt_file': paths[0].name, 'nbt_sha256': digest(paths[0]),
                   'block_count': len(data['blocks']),
                   'check_scope': '重新解析批准原件 NBT 并核对逐轴实体范围；不代表游戏成型。'})
    return result


def main() -> None:
    index_before = INDEX.read_bytes()
    index = json.loads(index_before.decode('utf-8'))
    pending = index['pending_batch']
    if pending['id'] != 'batch-06':
        raise ValueError('当前不是 batch-06，停止以防推进错误批次。')
    ids = list(pending['approved_machine_ids'])
    if len(ids) != len(set(ids)):
        raise ValueError('批次已有重复编号，停止。')
    present = {entry['id']: entry for entry in index['entries']}
    items = [item for item in ITEMS if item['id'] not in present]
    if not items:
        print(json.dumps({'status': '两台均已归档，不重复计数', 'pending_batch': pending}, ensure_ascii=False))
        return
    if ids != ['I14', 'I15'] or any(item['id'] in ids for item in items):
        raise ValueError('批次状态与首次补记预期不同，停止；已有批准不得重复累计。')

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_batch-06_04of05_I16-I17_已确认'
    snapshot.mkdir(parents=True, exist_ok=False)
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(index_before)
    rule_identities = []
    for name in RULES:
        source = ROOT / name
        shutil.copy2(source, evidence / source.name)
        rule_identities.append({'path': name, 'sha256': digest(source),
                                'lines': len(source.read_text(encoding='utf-8').splitlines())})

    rows = []
    for item in items:
        source = ROOT / 'deliveries' / item['folder']
        before = file_hashes(source)
        manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
        if manifest['candidate_version'] != item['version']:
            raise ValueError(f'{item["id"]} 的候选版本不匹配，停止。')
        structure = structure_check(source, item['id'])
        source_package = source / item['package']
        with zipfile.ZipFile(source_package) as package:
            if package.testzip() is not None:
                raise ValueError('批准来源包 ZIP 校验失败。')
            for name in (structure['nbt_file'], 'index.html', '三维评审.html'):
                if hashlib.sha256(package.read(name)).hexdigest() != before[name]:
                    raise ValueError(f'{item["id"]} 当前交付与批准来源包的 {name} 不一致。')
        target = snapshot / item['id']
        shutil.copytree(source, target)
        if file_hashes(target) != before or file_hashes(source) != before:
            raise ValueError('复制后源文件或归档内容发生变化，停止更新索引。')
        generator = ROOT / 'tools/structure_delivery' / item['generator']
        shutil.copy2(generator, evidence / generator.name)
        rows.append({
            'id': item['id'], 'key': item['key'], 'version': item['version'],
            'status': 'approved_archived_waiting_batch',
            'approval_quote': item['quote'], 'approval_message_time': '原消息精确时间未核实；本次按当前记录时间补记。',
            'approval_scope': '建筑外观及对应结构文件；不自动批准电压映射、首建阶段或游戏功能验收。',
            'source': str(source), 'archive': str(target),
            'preferred_source_package': item['package'], 'source_zip_sha256': digest(source_package),
            'structure_checks': structure, 'source_files_sha256': before,
            'target_voltage_appearance': item['voltage'],
            'candidate_controller': 'I16 为 [24,10,4] 的 HDV 机壳；I17 为 [24,8,4] 的 QSV 机壳。候选标记不是已注册运行控制器。',
            'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
        })

    ids.extend(row['id'] for row in rows)
    blocking = [
        '批次仅4/5，尚未达到每5台接入阈值。',
        'I14/I15 尚未完成符合现行工业线电压主机壳的修订确认；保留历史批准，不据此直接部署。',
        'I15 V4 的新增彩色机壳已被负责人否决，不得作为当前版本或混入实装；当前历史获批仅 V3。',
        'I17 外观使用 QSV，但来源记录当前可执行配方最低为 MAX；最低档首建规则与控制器/机壳获取链仍需闭合。',
        'I16/I17 的控制器、正式 Pattern、仓室能力、生存可达及配方运行未因外观批准而通过。',
    ]
    next_pending = dict(pending, approved_machine_ids=ids, count=len(ids), required=5,
                        deployment_eligible=False, deployment_blockers=blocking)
    approval = {
        'record': 1, 'created_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
        'discussion': '负责人历史明确批准 I16，并在本次明确批准 I17；按批准原件补记，不修改其来源。',
        'batch': 'batch-06', 'batch_position': '04/05', 'entries': rows,
        'rule_read_record': {'read_at': now.isoformat(), 'files': rule_identities},
        'previous_index_sha256': hashlib.sha256(index_before).hexdigest(),
        'pending_batch_after_archive': next_pending,
        'source_metadata_boundary': '来源 manifest 中待审状态作为历史原字节保留；当前批准状态只写于本外部确认清单。',
        'i15_state': '保留 V3 既有批准；V4 仅为被否决草稿，不计作新批准，部署阻塞保留。',
        'game_files_installed': False, 'game_verified': False,
        '_change_record': {'record': 1, 'time': now.isoformat(), 'deleted': '无',
                          'added': 'I16/I17 明确批准证据和不可变交付副本',
                          'modified': '批次批准数量从2/5推进为4/5，保留全部旧条目',
                          'purpose': '按确认版本接续结构审核，候选与正式功能分别验收'},
    }
    write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(
        '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I16/I17 外观批准归档</title>'
        '<style>body{max-width:960px;margin:32px auto;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#183b42}'
        'section{padding:18px;border:1px solid #bdd1d2;margin:14px 0}code{overflow-wrap:anywhere}</style>'
        f'<h1>I16 / I17 外观批准归档 · batch-06 4/5</h1><p>记录时间：{now.isoformat()}（Asia/Hong_Kong）。</p>'
        '<section><p>I16 V3 HDV 双门架定轴校准、I17 V1 QSV 阶梯精馏园区已获明确外观批准。'
        'I17 包含控制器定位修订版及原始 ZIP；源文件完整保留，不改写其中历史待审元数据。</p>'
        '<p>已按原字节复制，重新解析 NBT 核对实体尺寸，并回读归档 ZIP 验证全部文件 SHA256。</p></section>'
        '<section><p>尚未部署；外观批准不表示正式控制器、Pattern 成型、仓室、配方运行或生存首建验收。</p><ul>'
        + ''.join(f'<li>{html.escape(text)}</li>' for text in blocking)
        + '</ul></section><p>逐文件身份见 <a href="确认与校验清单.json">确认与校验清单</a>。</p></html>\n', encoding='utf-8')
    archived_hashes = file_hashes(snapshot)
    bundle = ARCHIVES / f'{snapshot.name}.zip'
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in archived_hashes:
            package.write(snapshot / name, name)
    with zipfile.ZipFile(bundle) as package:
        assert package.testzip() is None
        for name, expected in archived_hashes.items():
            assert hashlib.sha256(package.read(name)).hexdigest() == expected, name
    archive_sha = digest(bundle)
    for row in rows:
        index['entries'].append({
            'id': row['id'], 'key': row['key'], 'version': row['version'], 'status': row['status'],
            'archive': row['archive'], 'approval_manifest': str(snapshot / '确认与校验清单.json'),
            'approval_quote': row['approval_quote'], 'approval_scope': row['approval_scope'],
            'archive_zip': str(bundle), 'archive_zip_sha256': archive_sha,
            'source_zip_sha256': row['source_zip_sha256'],
            'nbt_sha256': row['structure_checks']['nbt_sha256'],
            'size_xyz': row['structure_checks']['declared_xyz'],
            'target_voltage_appearance': row['target_voltage_appearance'],
            'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
        })
    index['approved_structure_forms'] += len(rows)
    index['pending_batch'] = next_pending
    index['updated_at'] = now.isoformat()
    index['scope'] = '21种既有正式形态仍采用已批准电压改色；I14至I17外观批准归档，batch-06为4/5，未部署。'
    index['batch_rule'] = '每累计5台明确批准后按对应归档接入；当前batch-06为4/5，既有电压主色与首建闭环缺口仍须解决。'
    index['latest_approval_snapshot'] = {'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': archive_sha}
    index.setdefault('_change_records', []).append({
        'record': len(index.get('_change_records', [])) + 1, 'time': now.isoformat(),
        'reason': '补记 I16 明确批准与本次 I17 明确批准，保留逐份原件并继续审核 I18',
        'deleted': '无；旧索引原字节已保存，I15被否决V4未接入',
        'added': 'I16/I17外观批准、归档SHA256、4/5计数与现行部署阻塞',
        'modified': '仅推进外观确认索引，不改变正式资源、游戏文件或现行电压映射',
        'purpose': '使结构审核进度可追溯，防止把外观批准当作游戏闭环'},
    )
    if INDEX.read_bytes() != index_before:
        raise ValueError('当前索引在归档期间被其他任务修改，保留归档但拒绝覆盖索引。')
    write_json(INDEX, index)
    print(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': archive_sha,
                      'files': len(archived_hashes), 'entries': [
                          {'id': r['id'], 'nbt_sha256': r['structure_checks']['nbt_sha256'],
                           'size_xyz': r['structure_checks']['declared_xyz']} for r in rows],
                      'pending_batch': next_pending, 'verified': True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
