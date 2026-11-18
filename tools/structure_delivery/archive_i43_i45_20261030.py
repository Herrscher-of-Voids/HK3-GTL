"""按本轮真实决定封存 I43 V1、I44 站台 V2、I45 黑金列车 V2。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import copy
import hashlib
import html
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
LOG = ROOT / 'logs/i43-i45-terminal-demolition-20261030'
INDEX = ARCHIVES / '当前归档索引.json'
USER = 'msg_01a18bd4-3a0c-75a1-b57c-5975c0a9b625'
VERSIONS = {'I43': 'V1', 'I44': 'V2', 'I45': 'V2'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    sys.path.insert(0, str(ROOT / 'tools/conversation_archive'))
    import archive_dialogue as dialogue
    from archive_i40_turn_20261028 import load_current_window, THREAD
    records, _, _ = load_current_window()
    segment = next(s for s in dialogue.segment_dialogue(records, THREAD) if s['messages'][0]['id'] == USER)
    message = segment['messages'][0]
    assert message['text'].strip() == 'i43到 i45，落实一下'
    index = json.loads(INDEX.read_text(encoding='utf8'))
    if all(any(e['id'] == k for e in index['entries']) for k in VERSIONS):
        print('三台已按本轮消息封存；不重复追加。'); return
    assert index['approved_structure_forms'] == 49 and index['formal_structure_forms'] == 46
    assert index['pending_batch']['approved_machine_ids'] == ['I40', 'I41', 'I42']
    LOG.mkdir(parents=True, exist_ok=True)
    save(LOG / 'before-approval-index.json', index)
    resources = ROOT / 'src/main/resources'
    old = {}
    for pattern in ('data/hk3gtl/approved_architecture/*', 'data/hk3gtl/structures/approved/*',
                    'data/hk3gtl/structures/approved_preview/*', 'assets/hk3gtl/textures/block/overlay/**/*.png'):
        for p in resources.glob(pattern):
            if p.is_file(): old[p.relative_to(resources).as_posix()] = sha(p)
    save(LOG / 'existing-resources-before.json', old)
    now = datetime.now(timezone(timedelta(hours=8)))
    snapshot = ARCHIVES / (now.strftime('%Y%m%d_%H%M%S_%f') + '_I43V1_I44V2_I45V2_负责人要求落实')
    snapshot.mkdir(exist_ok=False)
    evidence = dict(message_id=USER, user_text=message['text'], actual_user_time=message['timestamp'],
        recorded_at=now.isoformat(), thread_id=THREAD,
        decision='采用当前最新候选并落实接入；不批准新配方、旅行权能、终审维度绕过或未测性能。')
    save(snapshot / 'approval-message-evidence.json', evidence)
    rows = []
    for key, version in VERSIONS.items():
        source, = (p for p in (ROOT / 'deliveries').glob(key + '_*' + version + '_*') if p.is_dir())
        meta = json.loads((source / 'manifest.json').read_text(encoding='utf8'))
        check = json.loads((source / 'verification.json').read_text(encoding='utf8'))
        assert meta['candidate_version'] == version and check['passed'] and check['geometry_passed']
        nbt, = source.rglob('*.nbt'); schem, = source.rglob('*.schem')
        assert sha(nbt) == check['nbt_schem_sha256']['nbt']
        assert sha(schem) == check['nbt_schem_sha256']['schem']
        hashes = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*') if p.is_file()}
        target = snapshot / source.name
        shutil.copytree(source, target)
        assert all(sha(target / name) == digest for name, digest in hashes.items())
        row = dict(id=key, key=key.lower(), candidate_key=key.lower(), approved_version=version,
            candidate_version=version, target_voltage_appearance=meta['target_voltage'],
            status='appearance_approved_archived_pending_formal_install', approved_at=message['timestamp'],
            approval_quote=message['text'], approval_message_id=USER,
            approval_scope='当前最新完整建筑、正式控制器/Pattern/完整JEI预览及统一搭建入口接入；运行工艺另验。',
            source=str(source), archive=str(target), counts_as_new_machine=True,
            source_candidate_approved_field=meta['approved'], external_approval_is_authoritative=True,
            formal_resource_present=False, game_files_installed=False, game_verified=False,
            size_xyz=meta['size'], block_count=meta['blocks'], controller=meta['controller'],
            unique_materials=meta.get('unique_materials'), ordinary_materials=meta.get('ordinary_materials'),
            port_count=len(meta['ports']), approved_nbt=str(target / nbt.relative_to(source)),
            approved_nbt_sha256=sha(nbt), nbt_sha256=sha(nbt), approval_manifest=str(snapshot / (key + '-approval.json')))
        save(Path(row['approval_manifest']), dict(entries=[copy.deepcopy(row)], source_files_sha256=hashes,
            source_all_bytes_unchanged=True, source_candidate_status_preserved=True,
            external_approval_is_authoritative=True, approval_evidence=evidence, game_verified=False))
        rows.append(row)
    bundle = snapshot.with_suffix('.zip')
    package_hashes = {p.relative_to(snapshot).as_posix(): sha(p) for p in snapshot.rglob('*') if p.is_file()}
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in package_hashes: z.write(snapshot / name, name)
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for name, digest in package_hashes.items(): assert hashlib.sha256(z.read(name)).hexdigest() == digest
    digest = sha(bundle)
    for row in rows: row.update(archive_zip=str(bundle), archive_zip_sha256=digest)
    index['entries'].extend(rows)
    index.update(approved_structure_forms=52, approved_undeployed_count=6,
        approved_undeployed_machine_ids=['I40', 'I41', 'I42', 'I43', 'I44', 'I45'], updated_at=now.isoformat(),
        scope='本轮落实I43 V1、I44站台V2、I45黑金列车V2；第10批I40–I44满5台，I45按明确要求同期额外接入。I37留最后。')
    index['pending_batch'] = dict(id='batch-10', approved_machine_ids=['I40','I41','I42','I43','I44'],
        count=5, required=5, deployment_eligible=True, status='ready_for_install', game_files_installed=False,
        game_verified=False, deployment_blockers=[])
    index['additional_authorized_install'] = dict(machine_ids=['I45'], user_message_id=USER,
        reason='负责人明确要求I43至I45落实；不是将第11批伪记为满5台。')
    index.setdefault('_change_records', []).append(dict(record=len(index.get('_change_records', []))+1,
        time=now.isoformat(), reason='负责人要求I43到I45落实', added='三份批准快照与ZIP校验',
        modified='批准形态49→52，第10批满5台；I45明确授权同期接入，正式安装计数待部署核验。', deleted='无'))
    save(INDEX, index)
    save(LOG / 'approval.json', dict(passed=True, evidence=evidence, entries=rows, zip_sha256=digest,
        old_resources=len(old), approved_structure_forms=52, formal_structure_forms=46, game_verified=False))
    print(json.dumps(dict(approved=[r['id'] for r in rows], snapshot=str(snapshot), zip_sha256=digest), ensure_ascii=True))


if __name__ == '__main__': main()
