# -*- coding: utf-8 -*-
"""第9批索引只在安装收据与独立部署回读通过后推进；I37继续待审。"""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
LOG = ROOT / 'logs/batch09-install-20261027'
IDS = ['I34', 'I35', 'I36', 'I38', 'I39']


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''): value.update(chunk)
    return value.hexdigest()


def main():
    receipt_path = LOG / 'deployment.json'; receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    review_path = ROOT / 'logs/batch09-review-20261027/installed-review.json'; review = json.loads(review_path.read_text(encoding='utf-8'))
    assert receipt['status'] == 'installed' and receipt['revision'] == 181 and receipt['formal_shapes'] == 46
    assert receipt['batch'] == 'batch-09' and receipt['new_machine_ids'] == IDS and receipt['game_verified'] is False
    assert review['passed'] and review['revision'] == 181 and review['formal_shape_count'] == 46 and review['game_verified'] is False
    assert receipt['sha256'] == review['installed_jar_sha256'] == sha(Path(receipt['target']))
    assert receipt['target'] == review['target'] and review['previous_jar_sha256'] == receipt['old_sha256']
    assert review['third_party_jars_unchanged'] and review['instance_metadata_unchanged'] and review['old_language_keys_unchanged']
    assert [r['key'].upper() for r in review['structures']] == IDS
    before = INDEX.read_bytes(); index = json.loads(before)
    assert index['pending_batch']['id'] == 'batch-09' and index['pending_batch']['count'] == 5
    assert index['pending_batch']['approved_machine_ids'] == IDS and index['approved_structure_forms'] == 46 and index['formal_structure_forms'] == 41
    assert not any(r['id'] == 'I37' for r in index['entries']), '不得将I37自动批准'
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')
    formal_keys = sorted(p.stem for p in (ROOT / 'src/main/resources/data/hk3gtl/structures/approved').glob('*.json'))
    assert len(formal_keys) == 46 and 'i37' not in formal_keys
    evidence = LOG / 'index-finalization'; evidence.mkdir(exist_ok=True)
    backup = evidence / 'previous-current-index.json'; assert not backup.exists(); backup.write_bytes(before)
    details = dict(receipt=str(receipt_path), receipt_sha256=sha(receipt_path), installed_at=receipt['installed_at_hong_kong'],
        revision=181, sha256=receipt['sha256'], formal_shapes=46, game_files_installed=True, formal_controller_installed=True,
        formal_pattern_installed=True, complete_game_preview_installed=True, game_verified=False, provisional_processes_unlocked=0,
        target=receipt['target'], target_pack_version='2.9.2', backup=receipt['backup'],
        independent_review=str(review_path), independent_review_sha256=sha(review_path))
    completed = dict(index['pending_batch'], **details)
    completed.update(status='formal_controllers_patterns_full_architecture_installed_game_unverified', completed_at=now, deployment_blockers=[])
    index['completed_batches'].append(completed)
    for row in index['entries']:
        if row['id'] in IDS: row.update(status=completed['status'], formal_resource_present=True, **details)
    index.setdefault('historical_formal_deployments', []).append(index['latest_formal_controller_installation'])
    index['latest_formal_controller_installation'] = dict(details, machine_ids=IDS)
    index['latest_deployment'] = dict(details, machine_ids=IDS)
    index['latest_structure_installation'] = dict(details, machine_ids=IDS)
    index.update(formal_keys=formal_keys, formal_structure_forms=46, approved_undeployed_machine_ids=[], approved_undeployed_count=0,
        updated_at=now, scope='第9批I34 V2、I35 V3、I36 V1、I38 V1、I39 V1已接入增强版2.9.2，累计46形态；游戏成型运行未验收。先接入已完成，随后回I37制作，I37未批准。',
        pending_batch=dict(id='batch-10', approved_machine_ids=[], count=0, required=5, deployment_eligible=False,
            status='waiting_explicit_appearance_approvals', game_files_installed=False, game_verified=False, deployment_blockers=['尚无新批次明确批准结构，当前0/5。']),
        batch_rule='每累计5台明确批准的新结构先实装；batch-09已安装，batch-10当前0/5，I37等候选不计数。')
    index.setdefault('historical_previous_indices', []).append(index['previous_index'])
    index['previous_index'] = dict(preserved_copy=str(backup), sha256=hashlib.sha256(before).hexdigest())
    index['_change_records'].append(dict(record=len(index['_change_records']) + 1, time=now, deleted='无，旧索引原字节保留',
        added='第9批真实安装及独立JAR核对证据；开启batch-10', modified='本批五台更新为文件已安装，累计46形态；I37未批准', purpose='按先实装后I37的负责人顺序执行，文件安装不冒充游戏运行验收'))
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + chr(10), encoding='utf-8')
    result = dict(passed=True, batch='batch-09', ids=IDS, next_batch='batch-10', new_count=0,
        old_index_sha256=hashlib.sha256(before).hexdigest(), new_index_sha256=sha(INDEX), receipt=str(receipt_path), independent_review=str(review_path))
    (evidence / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('batch-09 installed; batch-10 0/5; formal shapes 46; I37 unapproved; game_verified=false')


if __name__ == '__main__':
    main()
