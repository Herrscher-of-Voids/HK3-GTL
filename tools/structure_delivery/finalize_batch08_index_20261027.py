# -*- coding: utf-8 -*-
"""以真实安装收据推进第8批索引；保留旧索引及批准快照。"""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'deliveries/多方块确认归档/当前归档索引.json'
LOG=ROOT/'logs/batch08-install-20261027'
receipt_path=LOG/'deployment.json'
receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
review_path=ROOT/'logs/batch08-review-20261027/installed-review.json'
review=json.loads(review_path.read_text(encoding='utf-8'))
assert receipt['status']=='installed' and receipt['revision']==180 and review['passed']
assert receipt['formal_shapes']==41 and receipt['game_verified'] is False
before=INDEX.read_bytes();index=json.loads(before)
assert index['pending_batch']['id']=='batch-08' and index['pending_batch']['count']==5
ids=['I29','I30','I31','I32','I33']
assert index['pending_batch']['approved_machine_ids']==ids
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')
evidence=LOG/'index-finalization';evidence.mkdir(exist_ok=True)
backup=evidence/'previous-current-index.json';assert not backup.exists();backup.write_bytes(before)
details=dict(receipt= str(receipt_path),receipt_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    installed_at=receipt['installed_at_hong_kong'],revision=180,sha256=receipt['sha256'],formal_shapes=41,
    game_files_installed=True,formal_controller_installed=True,formal_pattern_installed=True,
    complete_game_preview_installed=True,game_verified=False,provisional_processes_unlocked=0,
    target=receipt['target'],target_pack_version='2.9.2',backup=receipt['backup'])
completed=dict(index['pending_batch'],**details)
completed.update(status='formal_controllers_patterns_full_architecture_installed_game_unverified',
                 completed_at=now,deployment_blockers=[])
index['completed_batches'].append(completed)
for row in index['entries']:
    if row['id'] in ids:
        row.update(status=completed['status'],formal_resource_present=True,**details)
index.setdefault('historical_formal_deployments',[]).append(index['latest_formal_controller_installation'])
index['latest_formal_controller_installation']=dict(details,machine_ids=ids)
index['latest_deployment']=dict(details,machine_ids=ids)
index['latest_structure_installation']=dict(details,machine_ids=ids)
index['formal_keys']=sorted(p.stem for p in (ROOT/'src/main/resources/data/hk3gtl/structures/approved').glob('*.json'))
assert len(index['formal_keys'])==41
index.update(formal_structure_forms=41,approved_undeployed_machine_ids=[],approved_undeployed_count=0,
    updated_at=now,scope='I29–I33批准V1已正式接入增强版2.9.2，累计41种形态；游戏成型运行未验收。I34为下一台待审候选。',
    pending_batch=dict(id='batch-09',approved_machine_ids=[],count=0,required=5,deployment_eligible=False,
       status='waiting_explicit_appearance_approvals',game_files_installed=False,game_verified=False,
       deployment_blockers=['尚无新批次明确批准结构，当前0/5。']),
    batch_rule='每累计5台新批准未接入结构先实装；batch-08已正式安装，batch-09当前0/5，候选不计数。')
index.setdefault('historical_previous_indices',[]).append(index['previous_index'])
index['previous_index']=dict(preserved_copy=str(backup),sha256=hashlib.sha256(before).hexdigest())
index['_change_records'].append(dict(record=len(index['_change_records'])+1,time=now,deleted='无，旧索引原字节保留',
    added='第8批真实安装及独立JAR核对证据；开启batch-09',modified='I29–I33更新为已正式安装，累计41形态',
    purpose='区分外观批准、文件安装和游戏成型运行验收'))
INDEX.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(evidence/'result.json').write_text(json.dumps(dict(passed=True,batch='batch-08',ids=ids,next_batch='batch-09',
   new_count=0,old_index_sha256=hashlib.sha256(before).hexdigest(),new_index_sha256=hashlib.sha256(INDEX.read_bytes()).hexdigest(),
   receipt=str(receipt_path),independent_review=str(review_path)),ensure_ascii=False,indent=2),encoding='utf-8')
print('batch-08 installed; batch-09 0/5; formal shapes 41; game_verified=false')
