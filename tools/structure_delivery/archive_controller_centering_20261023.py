# -*- coding: utf-8 -*-
"""将负责人批准的21个居中融合形态保存为不可变归档，正式资源另由接入器生成。

【变更记录 #1】2026-10-23 13:34:12（内测5修订175）
- 删除：无；候选、旧归档和旧索引原字节保留。
- 新增：当前明确批准证据、21份结构回读、全文件复制及ZIP身份校验。
- 修改：当前批准索引改指向V2；新机器批次由4/5达到5/5，既有正式资源状态单独保留。
- 用途：为正式Pattern接入提供带SHA256的批准来源，不把归档称为游戏验收。
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib

from structure_size_baseline import ROOT, require

ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
SOURCE = ROOT / 'deliveries/I01-I18_控制器居中融合修订_V2_20261023'
LOGS = ROOT / 'logs/controller-centering-install-20261023'
RULES = ['rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt']
KEYS = [f'i01-{n}' for n in range(1, 5)] + [f'i{n:02}' for n in range(2, 19)]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes(path):
    return {p.relative_to(path).as_posix(): digest(p) for p in sorted(path.rglob('*')) if p.is_file()}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    if (LOGS / 'approval-archive.json').exists():
        raise ValueError('已有本轮归档收据；禁止重复推进或覆盖。')
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    identity = json.loads((ROOT / 'logs/controller-centering-rework-20261023/archive-identity.json').read_text(encoding='utf-8'))
    source_zip = SOURCE.with_suffix('.zip')
    assert digest(source_zip) == identity['sha256']
    before = hashes(SOURCE)
    with zipfile.ZipFile(source_zip) as bundle:
        assert bundle.testzip() is None
        names = {name.split('/', 1)[1]: name for name in bundle.namelist() if not name.endswith('/')}
        assert set(names) == set(before)
        assert all(hashlib.sha256(bundle.read(names[n])).hexdigest() == h for n, h in before.items())
    index_raw = INDEX.read_bytes()
    index = json.loads(index_raw.decode('utf-8-sig'))
    assert index['pending_batch']['approved_machine_ids'] == ['I14', 'I15', 'I16', 'I17']
    rows = []
    for key in KEYS:
        folder = SOURCE / key
        data = json.loads((folder / 'blueprint.json').read_text(encoding='utf-8'))
        actual = nbtlib.load(next(folder.glob('*.nbt')))
        assert [int(v) for v in actual['size']] == data['size']
        palette = [str(p['Name']) + ('[' + ','.join(f'{k}={v}' for k, v in sorted(p['Properties'].items())) + ']'
                   if 'Properties' in p else '') for p in actual['palette']]
        decoded = {tuple(int(v) for v in b['pos']): palette[int(b['state'])] for b in actual['blocks']}
        expected = {tuple(b['pos']): b['state'] for b in data['blocks']}
        assert decoded == expected
        assert data['controller'][0] * 2 == data['size'][0] - 1
        assert expected[tuple(data['controller'])] == 'minecraft:diamond_block'
        assert all(expected[tuple(p['pos'])] == 'hk3gtl:industrial_port_casing' for p in data['ports'])
        check = require(dict(data, key=key.upper()))
        formal_key = {'i01-1': 'i01', 'i01-2': 'i01_2', 'i01-3': 'i01_3', 'i01-4': 'i01_4'}.get(key, key)
        rows.append({'id': key.upper(), 'key': formal_key, 'candidate_key': key,
                     'source_blueprint_sha256': digest(folder / 'blueprint.json'),
                     'source_nbt_sha256': digest(next(folder.glob('*.nbt'))),
                     'source_nbt_name': next(folder.glob('*.nbt')).name,
                     'size_xyz': data['size'], 'controller': data['controller'],
                     'port_count': len(data['ports']), 'block_count': len(data['blocks']),
                     'structure_checks': check})
    snapshot = ARCHIVES / (now.strftime('%Y%m%d_%H%M%S_%f') + '_I01-I18_主控居中融合V2_已确认')
    snapshot.mkdir(exist_ok=False)
    target = snapshot / 'confirmed_v2'
    shutil.copytree(SOURCE, target)
    assert hashes(target) == before
    evidence = snapshot / 'evidence'
    evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(index_raw)
    rule_identity = []
    for name in RULES:
        path = ROOT / 'rule' / name
        shutil.copy2(path, evidence / name)
        rule_identity.append({'path': 'rule/' + name, 'sha256': digest(path)})
    read_record = {'read_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong', 'files': rule_identity,
                   'discussion': '2026-10-23_11-48-08_I01-I18主控制器宽度轴置中V2.html',
                   'scope': '本轮已实际全文读取六规则及相关讨论；读取不代表业务验收。'}
    write(LOGS / 'rules-read.json', read_record)
    shutil.copy2(LOGS / 'rules-read.json', evidence / 'rules-read.json')
    for rel in ['approved_architecture', 'structures/approved']:
        shutil.copytree(ROOT / 'src/main/resources/data/hk3gtl' / rel, evidence / 'previous-formal-resources' / rel)
    manifest = {'recorded_at': now.isoformat(), 'timezone': 'Asia/Hong_Kong',
                'approval_quote': '实装这一些吧', 'approval_message_time': '原消息精确时间未知；此为实际归档时间。',
                'approval_scope': '当前I01四阶和I02–I18共21形态V2外观结构，批准归档及正式接入、构建和唯一实例部署。',
                'source_root': str(SOURCE), 'archived_source_root': str(target),
                'source_zip_sha256': digest(source_zip), 'source_files_sha256': before,
                'previous_index_sha256': hashlib.sha256(index_raw).hexdigest(),
                'structures': rows, 'rule_read_record': read_record,
                'boundary': ['来源待审字样按原字节作为历史保留，当前批准在本外部清单记载。',
                             '游戏成型、配方运行及生存获取尚未验收；不按外观推定电压。',
                             'I14/I15保留本次批准的既有材质；未批准的I15彩色V4不进入本轮。'],
                '_change_record': {'record': 1, 'time': now.isoformat(), 'deleted': '无',
                                   'added': '明确批准和不可变原件身份', 'modified': '批准对象推进至当前V2',
                                   'purpose': '按可核验来源实装21形态'}}
    manifest_path = snapshot / '确认与校验清单.json'
    write(manifest_path, manifest)
    archived = hashes(snapshot)
    archive_zip = snapshot.with_suffix('.zip')
    with zipfile.ZipFile(archive_zip, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name in archived:
            bundle.write(snapshot / name, name)
    with zipfile.ZipFile(archive_zip) as bundle:
        assert bundle.testzip() is None
        assert all(hashlib.sha256(bundle.read(n)).hexdigest() == h for n, h in archived.items())
    assert hashes(SOURCE) == before
    archive_hash = digest(archive_zip)
    entries = {r['key']: r for r in index['entries']}
    for row in rows:
        previous = copy.deepcopy(entries.get(row['key']))
        history = previous.pop('previous_approved_versions', []) if previous else []
        entry = dict(row, status='approved_archived_waiting_integration', archive=str(target / row['candidate_key']),
                     approved_nbt=str(target / row['candidate_key'] / row['source_nbt_name']),
                     approved_nbt_sha256=row['source_nbt_sha256'], approval_manifest=str(manifest_path),
                     approval_quote=manifest['approval_quote'], archive_zip=str(archive_zip), archive_zip_sha256=archive_hash,
                     formal_resource_present=False, game_files_installed=False, game_verified=False,
                     previous_approved_versions=history + ([previous] if previous else []))
        entries[row['key']] = entry
    index['entries'] = list(entries.values())
    index.update(updated_at=now.isoformat(), approved_structure_forms=len(entries),
                 scope='本次明确批准I01–I18共21个V2形态，已归档待正式接入；S01–S05既有正式资源保留。',
                 latest_approval_snapshot={'snapshot': str(snapshot), 'zip': str(archive_zip), 'zip_sha256': archive_hash})
    index['pending_batch'] = dict(index['pending_batch'], approved_machine_ids=['I14', 'I15', 'I16', 'I17', 'I18'],
                                   count=5, required=5, deployment_eligible=True,
                                   deployment_blockers=[], game_verified=False,
                                   scope='五台新机器达到结构接入阈值；工艺定阶及生存闭环单独核验。')
    index.setdefault('_change_records', []).append({'record': len(index.get('_change_records', [])) + 1,
        'time': now.isoformat(), 'reason': '负责人明确要求实装当前V2', 'deleted': '无；旧索引原字节已归档',
        'added': '21形态新批准来源及I18新批次计数', 'modified': '仅更新批准状态，正式接入另记',
        'purpose': '使批准、接入及游戏验证分别可追溯'})
    assert INDEX.read_bytes() == index_raw
    write(INDEX, index)
    receipt = {'recorded_at': now.isoformat(), 'source_root': str(target), 'approval_manifest': str(manifest_path),
               'snapshot': str(snapshot), 'zip': str(archive_zip), 'zip_sha256': archive_hash,
               'archive_files': len(archived), 'candidate_files': len(before), 'structures': 21,
               'verified': True, 'source_unchanged': True}
    write(LOGS / 'approval-archive.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
