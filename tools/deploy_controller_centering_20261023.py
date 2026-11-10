# -*- coding: utf-8 -*-
"""仅向实际增强版2.9部署获批居中融合V2的修订175。

默认只读预检实例、进程与批准归档，日志写项目logs。只有显式--apply并
提供修订175完整包通过收据，才备份唯一目标HK3包、暂存21份批准Sponge
文件并原子替换JAR。冻结全部第三方JAR及实例元数据；不读写存档或配置。
批准原件及ZIP、包收据、正式26份结构资源分别核对身份，任一不符停止。

【变更记录 #1】2026-10-23 13:37:48（内测5修订175部署工具）
- 删除：无；不清理旧结构、第三方模组、旧备份或其他实例。
- 新增：批准ZIP/源逐文件门禁、26结构资源包核验、旧JAR备份和21文件交付。
- 修改：复用已核实实际cwd的进程守卫；包替换前再次检查身份及停机状态。
- 用途：按负责人明确实装授权交付，日志仍将游戏运行验收标为未进行。
"""
from __future__ import annotations

import argparse
import configparser
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from structure_delivery.project_paths import project_path
import shutil
import zipfile

import deploy_industrial_build as base

ROOT, INSTANCE, SOURCE, TARGET = base.ROOT, base.INSTANCE, base.SOURCE, base.TARGET
GAME = INSTANCE / 'minecraft'
LOG = ROOT / 'logs/controller-centering-install-20261023'
RECEIPT = LOG / 'approval-archive.json'
REVISION = 175
KEYS = [f'i01-{n}' for n in range(1, 5)] + [f'i{n:02}' for n in range(2, 19)]
FORMAL_KEYS = ['i01', 'i01_2', 'i01_3', 'i01_4'] + [f'i{n:02}' for n in range(2, 19)] + [f's{n:02}' for n in range(1, 6)]
SCHEM_FOLDER = 'HK3GTL_centered_V2_20261023_r175'


def now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(project_path(path).read_text(encoding='utf-8-sig'))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def require(condition, text):
    if not condition:
        raise RuntimeError(text)


def inside(path, parent):
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=True))
        return True
    except (ValueError, OSError):
        return False


def target_identity():
    require(INSTANCE.is_dir() and GAME.is_dir() and TARGET.is_file(), '唯一目标实例或HK3包不存在')
    paths = [INSTANCE / 'instance.cfg', INSTANCE / 'mrpack/modrinth.index.json', INSTANCE / 'mmc-pack.json']
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(paths[0], encoding='utf-8-sig')
    pack, components = read(paths[1]), read(paths[2])['components']
    require(cfg.get('General', 'InstanceType', fallback='') == 'OneSix', '实例类型变化')
    require(cfg.get('General', 'name', fallback='') == 'GregTech Leisure-增强版', '实例名称变化')
    require(pack['versionId'] == '2.9' and pack['name'] == 'GregTech Leisure-增强版', '整合包名称或版本变化')
    require(pack['dependencies'] == {'minecraft': '1.20.1', 'forge': '47.4.16'}, '实例加载器或MC版本变化')
    by_id = {c['uid']: c['version'] for c in components}
    require(by_id.get('net.minecraft') == '1.20.1' and by_id.get('net.minecraftforge') == '47.4.16', 'Prism组件与整合包清单不一致')
    return {'instance': str(INSTANCE.resolve()), 'game': str(GAME.resolve()), 'name': pack['name'],
            'pack_version': pack['versionId'], 'dependencies': pack['dependencies'],
            'metadata_sha256': {p.name: sha(p) for p in paths}}


def mods_identity():
    return {p.name: sha(p) for p in sorted(TARGET.parent.glob('*.jar'))}


def approved_archive(receipt_path):
    receipt = read(receipt_path)
    require(receipt.get('verified') is True and receipt.get('structures') == 21, '批准归档收据未通过或数量不符')
    snapshot, source = project_path(receipt['snapshot']), project_path(receipt['source_root'])
    manifest_path, archive = project_path(receipt['approval_manifest']), project_path(receipt['zip'])
    require(inside(snapshot, ROOT / 'deliveries/多方块确认归档') and source.parent == snapshot,
            '批准快照不在项目不可变归档目录')
    require(manifest_path.parent == snapshot and archive == snapshot.with_suffix('.zip'), '批准清单或ZIP位置不符')
    require(sha(archive) == receipt['zip_sha256'], '批准ZIP SHA变化')
    files = {p.relative_to(snapshot).as_posix(): sha(p) for p in snapshot.rglob('*') if p.is_file()}
    with zipfile.ZipFile(archive) as bundle:
        require(bundle.testzip() is None, '批准ZIP无法完整解压')
        names = bundle.namelist()
        require(len(names) == len(set(names)) and set(names) == set(files), '批准快照与ZIP文件清单不一致')
        require(all(hashlib.sha256(bundle.read(name)).hexdigest() == digest for name, digest in files.items()), '批准快照与ZIP字节不一致')
    manifest = read(manifest_path)
    require(manifest.get('approval_quote') == '实装这一些吧', '当前整批明确实装批准原话不符')
    require(project_path(manifest['archived_source_root']) == source, '批准结构源根目录不符')
    rows = {r['candidate_key']: r for r in manifest['structures']}
    require(set(rows) == set(KEYS) and len(manifest['structures']) == 21, '批准21形态集合不符')
    schematics = []
    for key in KEYS:
        blueprint = source / key / 'blueprint.json'
        data = read(blueprint)
        require(sha(blueprint) == rows[key]['source_blueprint_sha256'], key + '批准蓝图SHA不符')
        require(data['controller'][0] == (data['size'][0] - 1) // 2, key + '主控中心列变化')
        nbt = source / key / rows[key]['source_nbt_name']
        require(sha(nbt) == rows[key]['source_nbt_sha256'], key + '批准NBT SHA不符')
        schem = source / key / (data['name'] + '.schem')
        expected = manifest['source_files_sha256'][schem.relative_to(source).as_posix()]
        require(sha(schem) == expected, key + '批准Sponge SHA不符')
        schematics.append({'key': key, 'title': data['title'], 'controller': data['controller'],
                           'source': str(schem), 'name': schem.name, 'sha256': expected})
    require(len({s['name'] for s in schematics}) == 21, 'Sponge文件名不唯一')
    return {'receipt': str(receipt_path), 'receipt_sha256': sha(receipt_path),
            'snapshot': str(snapshot), 'source_root': str(source), 'manifest': str(manifest_path),
            'manifest_sha256': sha(manifest_path), 'zip': str(archive), 'zip_sha256': receipt['zip_sha256'],
            'archive_files': len(files), 'structures': 21, 'schematics': schematics}


def verified_build(verification_path):
    verification = read(verification_path)
    require(verification.get('status') == 'passed' and verification.get('revision') == REVISION,
            '修订175完整包核验收据未通过')
    digest = sha(SOURCE)
    require(digest == verification.get('sha256'), '构建JAR与完整包核验收据SHA不一致')
    require(project_path(verification.get('source', verification.get('jar', ''))).resolve() == SOURCE.resolve(), '验证收据不是唯一主JAR')
    require(verification.get('approved_forms') == 21 and verification.get('formal_forms') == 26
            and verification.get('formal_resource_files') == 78, '完整包收据的结构数量不符')
    resources = {}
    for key in FORMAL_KEYS:
        for relative in (f'approved_architecture/{key}.json', f'structures/approved/{key}.nbt', f'structures/approved/{key}.json'):
            path = ROOT / 'src/main/resources/data/hk3gtl' / relative
            require(path.is_file(), '缺少正式资源：' + relative)
            resources['data/hk3gtl/' + relative] = path
    with zipfile.ZipFile(SOURCE) as bundle:
        require(bundle.testzip() is None, '构建JAR CRC核对失败')
        changelog = json.loads(bundle.read('assets/hk3gtl/changelog.json'))
        require(changelog['entries'][0]['revision'] == REVISION, '构建JAR修订不符')
        require(bundle.read('assets/hk3gtl/changelog.json') == (ROOT / 'src/main/resources/assets/hk3gtl/changelog.json').read_bytes(), '构建changelog与源码不一致')
        actual = {n for n in bundle.namelist() if n.startswith('data/hk3gtl/approved_architecture/') and n.endswith('.json')}
        require(actual == {f'data/hk3gtl/approved_architecture/{k}.json' for k in FORMAL_KEYS}, '构建正式26结构集合不符')
        require(all(bundle.read(name) == path.read_bytes() for name, path in resources.items()), '构建26结构JSON/NBT/附属数据与正式源字节不一致')
        require('com/sirin/hk3gtl/Hk3Gtl.class' in bundle.namelist(), '主JAR缺少模组入口')
    require(verification.get('resources') == {name: sha(path) for name, path in resources.items()}, '完整包收据资源身份与当前正式源不符')
    build = read(LOG / 'build-verification.json')
    require(build.get('status') == 'passed' and build.get('exit_code') == 0 and build.get('revision') == REVISION
            and build.get('sha256') == digest, '当前修订clean build收据未通过或主JAR身份变化')
    return {'source': str(SOURCE), 'sha256': digest, 'bytes': SOURCE.stat().st_size,
            'revision': REVISION, 'verification': str(verification_path), 'verification_sha256': sha(verification_path),
            'formal_structure_forms': 26, 'formal_resource_files_checked': len(resources)}


def preflight(receipt_path):
    identity, archive, guard = target_identity(), approved_archive(receipt_path), base.target_process_guard()
    result = {'recorded_at': now(), 'target_instance': identity, 'approval_archive': archive,
              'process_guard': guard, 'mods_before': mods_identity(), 'installed_hk3_sha256': sha(TARGET),
              'instance_written': False, 'game_started_or_stopped': False}
    return result


def install_schematics(archive, backup, guard_checks):
    """新建独立版本目录；不覆盖旧结构。每个目录内仅含本工具自己的平面文件。"""
    locations = [GAME / 'schematics' / SCHEM_FOLDER, GAME / 'config/worldedit/schematics' / SCHEM_FOLDER]
    stages, committed = [], []
    try:
        for destination in locations:
            require(inside(destination, GAME), 'Sponge目标越出唯一实例')
            stage = destination.with_name(destination.name + '.pending')
            require(not destination.exists() and not stage.exists(), '本次Sponge目录或暂存已存在，禁止覆盖')
            stage.mkdir(parents=True, exist_ok=False)
            stages.append(stage)
            for item in archive['schematics']:
                source = project_path(item['source'])
                require(sha(source) == item['sha256'], '复制前批准Sponge身份变化')
                target = stage / item['name']
                shutil.copy2(source, target)
                require(sha(target) == item['sha256'], 'Sponge复制校验失败')
            save(stage / 'manifest.json', {'recorded_at': now(), 'revision': REVISION,
                 'approval_zip_sha256': archive['zip_sha256'], 'structures': archive['schematics'],
                 'boundary': '批准外观Sponge文件；正式Pattern、仓室与配方运行须单独验收。',
                 '_change_records': [{'number': 1, 'time': now(), 'delete': '无', 'add': '21份批准Sponge及来源身份',
                                      'modify': '仅独立版本目录', 'purpose': '提供投影/粘贴文件，不写存档'}]})
        guard_checks['before_schematic_commit'] = base.target_process_guard()
        for stage, destination in zip(stages, locations):
            stage.rename(destination)
            committed.append(destination)
        return committed
    except Exception:
        # 只逐文件移除本次独立目录；出现未知目录项即保留现场，不递归删除。
        for folder in stages + committed:
            if folder.exists() and inside(folder, GAME):
                expected_names = {s['name'] for s in archive['schematics']} | {'manifest.json'}
                if all(p.is_file() and p.name in expected_names for p in folder.iterdir()):
                    for p in folder.iterdir():
                        p.unlink()
                    folder.rmdir()
        raise


def deploy(receipt_path, verification_path):
    require(verification_path is not None, '--apply必须提供完整包验证收据')
    state = preflight(receipt_path)
    package = verified_build(verification_path)
    require(read(verification_path).get('approval_zip_sha256') == state['approval_archive']['zip_sha256'], '包验证不对应当前批准ZIP')
    output = LOG / 'deployment.json'
    require(not output.exists(), '已有本轮部署收据，禁止重复替换')
    for pending in TARGET.parent.glob(TARGET.stem + '*pending*'):
        require(False, '存在未完成JAR暂存，保留现场：' + pending.name)
    for parent in [GAME / 'schematics', GAME / 'config/worldedit/schematics']:
        require(not (parent / SCHEM_FOLDER).exists() and not (parent / (SCHEM_FOLDER + '.pending')).exists(), '结构交付目录已存在')
    before = state['mods_before']
    expected_identity = state['target_instance']
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')
    backup = GAME / 'hk3gtl-mod-backups' / (stamp + '_controller_centering_r175')
    require(inside(backup, GAME), '备份目标越出唯一实例')
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(TARGET, backup / TARGET.name)
    require(sha(backup / TARGET.name) == before[TARGET.name], '原JAR备份SHA不一致')
    save(backup / 'before.json', state)
    pending = TARGET.with_suffix('.controller-centering-pending')
    guards, schematics, replaced = {'before_verification': state['process_guard']}, [], False
    try:
        shutil.copy2(SOURCE, pending)
        require(sha(pending) == package['sha256'] == sha(SOURCE), '主JAR暂存身份变化')
        require(target_identity() == expected_identity and mods_identity() == before, '暂存期间实例元数据或模组清单变化')
        schematics = install_schematics(state['approval_archive'], backup, guards)
        guards['before_atomic_jar_replace'] = base.target_process_guard()
        require(target_identity() == expected_identity and mods_identity() == before, '替换前实例元数据或模组清单变化')
        require(sha(SOURCE) == package['sha256'] == sha(pending), '替换前构建主JAR变化')
        require(sha(project_path(state['approval_archive']['zip'])) == state['approval_archive']['zip_sha256'], '替换前批准ZIP变化')
        os.replace(pending, TARGET)
        replaced = True
        after = mods_identity()
        require(before.keys() == after.keys(), '部署后模组文件清单变化')
        require(all(after[n] == h for n, h in before.items() if n != TARGET.name), '第三方JAR身份变化')
        require(sha(TARGET) == package['sha256'], '目标主JAR SHA不符')
        for folder in schematics:
            require(all(sha(folder / s['name']) == s['sha256'] for s in state['approval_archive']['schematics']), '部署后Sponge身份不符')
        result = {'recorded_at': now(), 'revision': REVISION, 'target_instance': expected_identity,
                  'target': str(TARGET), 'backup': str(backup), 'previous_sha256': before[TARGET.name],
                  'sha256': sha(TARGET), 'bytes': TARGET.stat().st_size, 'package': package,
                  'approval_archive': state['approval_archive'], 'process_guards': guards,
                  'third_party_jars_unchanged': True, 'mods_before': before, 'mods_after': after,
                  'schematic_locations': [str(p) for p in schematics], 'schematic_forms': 21,
                  'formal_structure_forms': 26, 'game_acceptance': '未启动游戏、未加载世界；运行验收尚未进行',
                  '_change_records': [{'number': 1, 'time': now(), 'delete': '无旧结构或第三方内容删除',
                       'add': '原HK3包备份及21份批准Sponge的两个独立目录', 'modify': '唯一实例HK3包更新为已核验修订175',
                       'purpose': '按负责人当前整批实装授权交付；不代表游戏运行通过'}]}
        save(output, result)
        save(backup / 'deployment.json', result)
        return result
    except Exception as error:
        save(LOG / 'deployment-failure.json', {'recorded_at': now(), 'jar_replaced': replaced,
             'backup': str(backup), 'schematic_locations': [str(p) for p in schematics],
             'error_type': type(error).__name__, 'reason': str(error),
             'action': '保留备份与已写文件供核查；不在未知运行状态下再次替换主包，不操作其他进程。'})
        raise
    finally:
        if pending.exists():
            pending.unlink()


def main():
    parser = argparse.ArgumentParser(description='当前批准V2的实例预检与停机部署；默认不写实例')
    parser.add_argument('--archive-receipt', type=Path, default=RECEIPT)
    parser.add_argument('--package-verification', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.apply:
        lock = LOG / 'deployment.lock'
        with lock.open('x', encoding='utf-8') as stream:
            stream.write(now() + '\n')
        try:
            result = deploy(args.archive_receipt, args.package_verification)
        finally:
            lock.unlink()
        print(json.dumps({'deployed': True, 'revision': REVISION, 'sha256': result['sha256'], 'receipt': str(LOG / 'deployment.json')}, ensure_ascii=False))
    else:
        result = preflight(args.archive_receipt)
        existing_path = LOG / 'deploy-preflight.json'
        existing = read(existing_path) if existing_path.exists() else {}
        existing['latest_readonly_preflight'] = result
        existing['deployment_entry'] = str(Path(__file__).resolve())
        existing['deployment_ready_requires'] = '根任务clean build与175完整包核验通过后，显式--apply和--package-verification收据'
        save(existing_path, existing)
        print(json.dumps({'preflight_passed': True, 'target_replace_allowed': result['process_guard']['target_replace_allowed'],
                          'instance_written': False, 'approval_zip_sha256': result['approval_archive']['zip_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
