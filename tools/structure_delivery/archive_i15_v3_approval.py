# -*- coding: utf-8 -*-
"""Archive approved I15 V3 and advance the pending five-machine batch."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIVERIES = ROOT / 'deliveries'
ARCHIVES = DELIVERIES / '多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
I14_ARCHIVE = ARCHIVES / '20261015_111144_056795_batch-06_01of05_I14_V4' / 'confirmed_v4'
I15_SOURCE = DELIVERIES / 'I15_魂钢重构退火炉_三钟回转炉院_V3_20261016'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_sha(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha(path)
            for path in sorted(root.rglob('*')) if path.is_file()}


def main() -> None:
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    current = index['pending_batch']
    ids = list(current['approved_machine_ids'])
    if ids != ['I14']:
        raise RuntimeError(f'unexpected pending batch state: {ids}')
    i15_manifest = json.loads((I15_SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    if i15_manifest.get('candidate_version') != 'V3 三钟回转炉院':
        raise RuntimeError('I15 source is not the expected V3 candidate')
    i15_zip = next(I15_SOURCE.glob('I15_*结构与预览.zip'))

    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')
    snapshot = ARCHIVES / f'{stamp}_batch-06_02of05_I14-I15'
    snapshot.mkdir(parents=True, exist_ok=False)
    shutil.copy2(INDEX, snapshot / 'previous-current-index.json')
    shutil.copytree(I14_ARCHIVE, snapshot / 'I14')
    shutil.copytree(I15_SOURCE, snapshot / 'I15')

    i14_manifest = json.loads((ARCHIVES / '20261015_111144_056795_batch-06_01of05_I14_V4' /
                               '确认与校验清单.json').read_text(encoding='utf-8'))
    approval = {
        'batch': 'batch-06',
        'batch_position': '02/05',
        'created_at': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
        'timezone': 'Asia/Hong_Kong',
        'status': 'approved_archived_waiting_batch',
        'approval_quote': '嗯，这一台可以了',
        'approval_scope': 'I15 三钟回转炉院 V3 的建筑外观与对应结构文件；不表示正式 Pattern、配方或游戏内成型验收。',
        'entries': [
            {'id': 'I14', 'version': 'V4 正梁锻心',
             'status': 'approved_archived_waiting_batch',
             'source_archive': str(I14_ARCHIVE),
             'source_zip_sha256': i14_manifest['source_zip_sha256'],
             'nbt_sha256': i14_manifest['structure_checks']['nbt_sha256'],
             'size_xyz': i14_manifest['structure_checks']['size_xyz']},
            {'id': 'I15', 'version': 'V3 三钟回转炉院',
             'status': 'approved_archived_waiting_batch',
             'approval_quote': '嗯，这一台可以了',
             'source_archive': str(I15_SOURCE),
             'source_zip_sha256': sha(i15_zip),
             'nbt_sha256': i15_manifest['hashes']['nbt'],
             'size_xyz': i15_manifest['size_xyz']},
        ],
        'files_sha256': {'I14/' + name: value for name, value in files_sha(I14_ARCHIVE).items()},
        'i15_source_files_sha256': files_sha(I15_SOURCE),
        'pending_batch_after_archive': {
            'id': 'batch-06', 'approved_machine_ids': ['I14', 'I15'],
            'count': 2, 'required': 5, 'deployment_eligible': False,
        },
        'game_files_installed': False,
        'game_verified': False,
        'immutability': 'I14 原确认目录与 I15 候选源目录均逐文件复制；本快照包含独立结构和审计证据。',
    }
    (snapshot / '确认与校验清单.json').write_text(
        json.dumps(approval, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    bundle = ARCHIVES / f'{snapshot.name}.zip'
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(snapshot.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(snapshot).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for name, digest in approval['files_sha256'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
        for name, digest in approval['i15_source_files_sha256'].items():
            name = 'I15/' + name
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name

    i15_entry = {
        'id': 'I15', 'key': 'i15', 'version': 'V3 三钟回转炉院',
        'status': 'approved_archived_waiting_batch',
        'archive': str(snapshot / 'I15'),
        'approval_manifest': str(snapshot / '确认与校验清单.json'),
        'approval_quote': '嗯，这一台可以了',
        'archive_zip': str(bundle), 'archive_zip_sha256': sha(bundle),
        'source_zip_sha256': approval['entries'][1]['source_zip_sha256'],
        'nbt_sha256': i15_manifest['hashes']['nbt'],
        'size_xyz': i15_manifest['size_xyz'],
        'formal_resource_present': False, 'game_files_installed': False, 'game_verified': False,
    }
    index['entries'].append(i15_entry)
    index['approved_structure_forms'] += 1
    index['pending_batch'] = approval['pending_batch_after_archive']
    index['snapshot'] = str(snapshot)
    index['zip'] = str(bundle)
    index['zip_sha256'] = sha(bundle)
    index['updated_at'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle),
                      'zip_sha256': sha(bundle), 'index': str(INDEX),
                      'pending_batch': index['pending_batch']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
