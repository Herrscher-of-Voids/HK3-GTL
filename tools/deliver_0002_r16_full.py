from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-industrial-handoff-0002-r16-20261116'
BUILD = LOG / 'full-build-r1'
SNAPSHOT = BUILD / 'source'
OUT = ROOT / 'deliveries/0002贴图材质_全电压产业_R16_20261116'
VERSION = '0.5.0-textures-r16'
NAME = '0002贴图材质-' + VERSION + '.jar'
JAVA_HOME = 'C:/Program Files/Java/jdk-21'
COMMAND = ".\\gradlew.bat --no-daemon --no-build-cache --max-workers=2 --project-cache-dir ../project-cache '-Parchives_base_name=0002贴图材质' '-Pmod_version=" + VERSION + "' remapJar -x check -x test --console=plain"
DIRECTORIES = ['src', 'tools', 'source_archives', 'libs', 'gradle', 'kubejs']
FILES = ['build.gradle', 'settings.gradle', 'gradle.properties', 'gradlew', 'gradlew.bat',
    'package.json', 'package-lock.json', 'generator-voltage-tier-builds.mjs', 'AGENTS.md',
    'rule/系统角色设定.md', 'rule/当前多方块设计规则.md', 'LICENSE.txt', 'CREDITS.txt']
TASKS = ['extractCgseCompileJar', 'compileJava', 'hk3gtlRestoreSourceBlueprints',
    'hk3gtlCompactStructures', 'processResources', 'hk3gtlSyncDevResourcesToClasses',
    'hk3gtlWriteModsTomlToClasses', 'classes', 'jar', 'remapJar']
RESOURCE_COUNTS = dict(png=184, item_models=128, mcmeta=56)


def now():
    return datetime.now().astimezone().isoformat()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def inventory(root):
    paths = [root / name for name in FILES]
    for name in DIRECTORIES:
        paths.extend(path for path in (root / name).rglob('*')
            if path.is_file() and '__pycache__' not in path.parts)
    return {path.relative_to(root).as_posix(): dict(bytes=path.stat().st_size, sha256=digest(path))
        for path in sorted(set(paths))}


def differences(before, after):
    result = []
    for path in sorted(before.keys() | after.keys()):
        if path not in before:
            result.append(dict(path=path, kind='added', current=after[path]))
        elif path not in after:
            result.append(dict(path=path, kind='deleted', snapshot=before[path]))
        elif before[path] != after[path]:
            result.append(dict(path=path, kind='modified', snapshot=before[path], current=after[path]))
    return result


def freeze():
    BUILD.mkdir(parents=True)
    (BUILD / 'project-cache').mkdir()
    adoption = json.loads((LOG / 'adoption.json').read_text('utf8'))
    save(BUILD / 'resource-adoption.json', adoption)
    started, attempts = now(), []
    while True:
        SNAPSHOT.mkdir()
        before = inventory(ROOT)
        for index, relative in enumerate(before, 1):
            target = SNAPSHOT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
            if index % 500 == 0:
                print(f'复制输入 {index}/{len(before)}', flush=True)
        after, copied = inventory(ROOT), inventory(SNAPSHOT)
        changed = differences(before, after)
        copy_changes = differences(before, copied)
        attempts.append(dict(finished_at=now(), source_changes=changed, copy_changes=copy_changes))
        if not changed and not copy_changes:
            break
        print('输入复制期间有改动，重新固定完整快照。', flush=True)
        if SNAPSHOT.resolve() != (BUILD.resolve() / 'source'):
            raise RuntimeError('快照路径超出本次独立构建目录。')
        shutil.rmtree(SNAPSHOT)
    resource_changes = [item['target'] for item in adoption['resources']
        if copied[item['target']]['sha256'] != item['sha256']]
    if resource_changes:
        raise RuntimeError('正式资源与接入清单不一致：' + ', '.join(resource_changes))
    manifest = dict(started_at=started, frozen_at=now(), source_root=str(ROOT),
        snapshot_root=str(SNAPSHOT), input_directories=DIRECTORIES, input_files=FILES,
        all_saved_production_inputs_included=True, prior_outputs_copied=False,
        snapshot_consistent=True, attempts=attempts,
        files=[dict(path=path, **entry) for path, entry in copied.items()])
    save(BUILD / 'input-manifest.json', manifest)
    save(BUILD / 'build-command.json', dict(command=COMMAND, working_directory=str(SNAPSHOT),
        java_home=JAVA_HOME, project_cache=str(BUILD / 'project-cache'),
        initial_build_output_empty=not (SNAPSHOT / 'build').exists(),
        initial_project_cache_empty=not any((BUILD / 'project-cache').iterdir()),
        input_manifest_sha256=digest(BUILD / 'input-manifest.json'),
        adoption_sha256=digest(BUILD / 'resource-adoption.json')))
    script = "$env:JAVA_HOME = '" + JAVA_HOME + "'\n"
    script += "$env:Path = $env:JAVA_HOME + '/bin;' + $env:Path\n"
    script += "Set-Location -LiteralPath (Join-Path $PSScriptRoot 'source')\n"
    script += COMMAND + " 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'build.log')\n"
    script += "$buildExit = $LASTEXITCODE\n"
    script += "Set-Content -LiteralPath (Join-Path $PSScriptRoot 'exit-code.txt') -Value $buildExit\n"
    script += "exit $buildExit\n"
    (BUILD / 'build-command.ps1').write_text(script, 'utf-8-sig')
    print(json.dumps(dict(snapshot=str(SNAPSHOT), files=len(copied),
        bytes=sum(item['bytes'] for item in copied.values()), attempts=len(attempts),
        command_script=str(BUILD / 'build-command.ps1')), ensure_ascii=False), flush=True)


def finish():
    manifest = json.loads((BUILD / 'input-manifest.json').read_text('utf8'))
    command = json.loads((BUILD / 'build-command.json').read_text('utf8'))
    adoption = json.loads((BUILD / 'resource-adoption.json').read_text('utf8'))
    build_log_bytes = (BUILD / 'build.log').read_bytes()
    build_log = build_log_bytes.decode('utf16' if build_log_bytes.startswith(b'\xff\xfe') else 'utf-8-sig')
    task_result = next(line.strip() for line in build_log.splitlines() if line.startswith('BUILD SUCCESSFUL'))
    tasks = re.findall(r'^> Task :([^\s]+)', build_log, re.M)
    if int((BUILD / 'exit-code.txt').read_text('utf-8-sig').strip()) or not set(TASKS).issubset(tasks):
        raise RuntimeError('完整生产任务未全部成功，停止交付。')
    jar = SNAPSHOT / 'build/libs' / NAME
    with ZipFile(jar) as archive:
        names = set(archive.namelist())
        metadata = archive.read('META-INF/mods.toml').decode('utf8')
        mod = next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', block.split('[[')[0]))
        version = re.search(r'version\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        config = json.loads(archive.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ('mixins', 'client', 'server') for name in config.get(key, [])]
        plugin = config['plugin'].replace('.', '/') + '.class'
        checked = []
        for item in adoption['resources']:
            relative = Path(item['target']).relative_to('src/main/resources').as_posix()
            data = archive.read(relative)
            actual = hashlib.sha256(data).hexdigest()
            checked.append(dict(path=relative, bytes=len(data), sha256=actual,
                matches_adoption=actual == item['sha256'],
                matches_snapshot=actual == digest(SNAPSHOT / item['target'])))
        counts = dict(png=sum(item['path'].endswith('.png') for item in checked),
            item_models=sum('/models/item/' in item['path'] and item['path'].endswith('.json') for item in checked),
            mcmeta=sum(item['path'].endswith('.mcmeta') for item in checked))
        package = dict(mod_id='hk3gtl', version=version, mods_toml=metadata,
            mixin_config='hk3gtl.mixins.json', mixin_classes=len(mixins),
            mixins_complete=all(name in names for name in mixins),
            mixin_plugin_present=plugin in names, refmap=config['refmap'],
            refmap_present=config['refmap'] in names, resource_counts=counts, resources=checked)
    if not all([version == VERSION, package['mixins_complete'], package['mixin_plugin_present'],
                package['refmap_present'], all(counts[key] >= value for key, value in RESOURCE_COUNTS.items()),
                all(item['matches_adoption'] and item['matches_snapshot'] for item in checked)]):
        raise RuntimeError('完整构建产物的版本、Mixin或正式资源核对失败。')
    OUT.mkdir(parents=True, exist_ok=True)
    artifact = OUT / NAME
    shutil.copy2(jar, artifact)
    built_hash, delivery_hash = digest(jar), digest(artifact)
    if built_hash != delivery_hash:
        raise RuntimeError('交付副本与完整构建产物SHA-256不一致。')
    before = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256']) for item in manifest['files']}
    receipt = dict(recorded_at=now(), conversation='0002',
        conversation_id='01a1d68a-a994-7ac0-a48a-54c0f98fd54e', version=VERSION,
        source_snapshot=str(SNAPSHOT), frozen_at=manifest['frozen_at'],
        input_manifest=str(BUILD / 'input-manifest.json'),
        input_manifest_sha256=digest(BUILD / 'input-manifest.json'),
        input_files=len(before), input_bytes=sum(item['bytes'] for item in before.values()),
        command=COMMAND, java_home=JAVA_HOME, project_cache=str(BUILD / 'project-cache'),
        initial_build_output_empty=command['initial_build_output_empty'],
        initial_project_cache_empty=command['initial_project_cache_empty'],
        snapshot_consistent=manifest['snapshot_consistent'], full_production_source_set=True,
        build_successful=True, task_result=task_result, production_tasks=tasks,
        build_log=str(BUILD / 'build.log'), direct_official_remap_copy=True,
        jar_repacked=False, post_build_jar_mutation=False, built_jar=str(jar),
        delivery_jar=str(artifact), bytes=jar.stat().st_size, sha256=built_hash,
        delivery_sha256=delivery_hash, both_hashes_equal=True,
        package_verification=package,
        post_snapshot_changes_not_included=differences(before, inventory(ROOT)),
        automated_tests_run=False, installed=False, game_started=False)
    save(BUILD / 'build-receipt.json', receipt)
    save(OUT / '完整构建回执.json', receipt)
    print(json.dumps(dict(delivery=str(artifact), sha256=built_hash,
        resources=counts, post_snapshot_changes=len(receipt['post_snapshot_changes_not_included'])),
        ensure_ascii=False), flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'finish': finish}[sys.argv[1]]()
