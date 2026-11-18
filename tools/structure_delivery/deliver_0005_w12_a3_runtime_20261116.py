from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w12-a3-runtime-20261116'
BUILD = LOG / 'full-build-01'
SNAPSHOT = BUILD / 'source'
OUT = ROOT / 'deliveries/0005_W12_A3_游戏接入_r1_20261116'
INSTANCE = Path('E:/Prism/instances/GregTech Leisure-增强版/minecraft')
VERSION = '0.5.0-W12A3-r1'
NAME = '0005多方块设计-' + VERSION + '.jar'
COMMAND = ".\\gradlew.bat --no-daemon --max-workers=2 --project-cache-dir ../project-cache '-Parchives_base_name=0005多方块设计' '-Pmod_version=" + VERSION + "' remapJar -x check -x test --console=plain"


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def active_jars():
    selected = []
    for path in (INSTANCE / 'mods').glob('*.jar'):
        with ZipFile(path) as jar:
            if 'META-INF/mods.toml' in jar.namelist():
                text = jar.read('META-INF/mods.toml').decode('utf8')
                if any(re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', item.split('[[')[0])
                       for item in text.split('[[mods]]')[1:]):
                    selected.append(path)
    return selected


def freeze():
    SNAPSHOT.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now().astimezone().isoformat()
    directories = ['src', 'tools', 'source_archives', 'libs', 'gradle', 'kubejs',
        'deliveries/0005_W12_三环翻转_A3_20261116', 'deliveries/0005_W12_A3_批准接入_20261116']
    files = ['build.gradle', 'settings.gradle', 'gradle.properties', 'gradlew', 'gradlew.bat',
        'package.json', 'package-lock.json', 'generator-voltage-tier-builds.mjs', 'AGENTS.md',
        'rule/系统角色设定.md', 'rule/当前多方块设计规则.md', 'LICENSE.txt', 'CREDITS.txt']
    inputs = [ROOT / name for name in files]
    for name in directories:
        inputs.extend(p for p in (ROOT / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    records, changed = [], []
    for index, path in enumerate(sorted(set(inputs))):
        relative = path.relative_to(ROOT)
        target = SNAPSHOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        before = path.stat()
        shutil.copy2(path, target)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            changed.append(str(relative))
        records.append(dict(path=str(relative).replace('\\', '/'), bytes=target.stat().st_size, sha256=digest(target)))
        if index % 500 == 0:
            print(f'复制输入 {index + 1}/{len(inputs)}', flush=True)
    manifest = dict(started_at=started, frozen_at=datetime.now().astimezone().isoformat(),
        source_root=str(ROOT), snapshot_root=str(SNAPSHOT), input_directories=directories,
        input_files=files, all_production_sources_included=True, prior_outputs_copied=False,
        changed_during_copy=changed, files=records)
    save(BUILD / 'input-manifest.json', manifest)
    current, = active_jars()
    save(LOG / 'before-install.json', dict(path=str(current), sha256=digest(current), bytes=current.stat().st_size))
    save(LOG / 'active-build.json', dict(snapshot=str(SNAPSHOT), command=COMMAND,
        manifest_sha256=digest(BUILD / 'input-manifest.json')))
    print(json.dumps(dict(snapshot=str(SNAPSHOT), files=len(records), bytes=sum(r['bytes'] for r in records), changed=changed)), flush=True)


def finish():
    manifest = json.loads((BUILD / 'input-manifest.json').read_text('utf8'))
    build_log = (BUILD / 'build.log').read_text('utf-8-sig')
    task_result = next(line.strip() for line in build_log.splitlines() if line.startswith('BUILD SUCCESSFUL'))
    jar = SNAPSHOT / 'build/libs' / NAME
    artifact = OUT / NAME
    shutil.copy2(jar, artifact)
    resources = ['data/hk3gtl/structures/w12_candidate.bin.gz', 'data/hk3gtl/structures/w12_approved.json',
        'data/hk3gtl/structures/w12_a3_mask.bin.gz', 'assets/hk3gtl/models/scene/w12_a3.json.gz',
        'assets/hk3gtl/textures/effect/w12_a3_atlas.png']
    resources += [str(p.relative_to(SNAPSHOT / 'src/main/resources')).replace('\\', '/')
        for p in (SNAPSHOT / 'src/main/resources/assets/hk3gtl/shaders/core').glob('w12*')]
    with ZipFile(jar) as archive:
        names = archive.namelist()
        config = json.loads(archive.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ('mixins', 'client', 'server') for name in config.get(key, [])]
        checked = [dict(path=name, bytes=len(archive.read(name)),
            sha256=hashlib.sha256(archive.read(name)).hexdigest(),
            matches_snapshot=hashlib.sha256(archive.read(name)).hexdigest() == digest(SNAPSHOT / 'src/main/resources' / name))
            for name in resources]
        package = dict(mods_toml=archive.read('META-INF/mods.toml').decode('utf8'),
            mixins_complete=all(name in names for name in mixins),
            refmap=config.get('refmap'), refmap_present=config.get('refmap') in names,
            w12_machine='com/sirin/hk3gtl/common/machine/w12/Hk3W12Machine.class' in names,
            w12_renderer='com/sirin/hk3gtl/client/wonder/Hk3W12FxRenderer.class' in names,
            prior_w08_w10_retained=all('assets/hk3gtl/models/scene/' + name in names for name in ('w08_a5.json.gz', 'w10_a3.json.gz')),
            compact_metadata=sum(n.startswith('data/hk3gtl/compact_architecture/') and n.endswith('.json') for n in names),
            resources=checked)
    if not all([package['mixins_complete'], package['refmap_present'], package['w12_machine'],
                package['w12_renderer'], package['prior_w08_w10_retained'],
                all(item['matches_snapshot'] for item in checked)]):
        raise RuntimeError('构建产物缺少正式类或资源，停止安装。')
    changes = [dict(path=item['path'], kind='modified_or_removed', snapshot_sha256=item['sha256'])
        for item in manifest['files'] if not (ROOT / item['path']).is_file() or digest(ROOT / item['path']) != item['sha256']]
    build = dict(recorded_at=datetime.now().astimezone().isoformat(),
        version=VERSION, conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        source_snapshot=str(SNAPSHOT), input_manifest=str(BUILD / 'input-manifest.json'),
        input_manifest_sha256=digest(BUILD / 'input-manifest.json'), frozen_at=manifest['frozen_at'],
        input_files=len(manifest['files']), input_bytes=sum(r['bytes'] for r in manifest['files']),
        command=COMMAND, build_successful=True, task_result=task_result,
        snapshot_consistent=not manifest['changed_during_copy'], full_production_source_set=True,
        initial_build_output_empty=True, project_cache=str(BUILD / 'project-cache'),
        java_home='C:/Program Files/Java/jdk-21', build_log=str(BUILD / 'build.log'),
        production_tasks=re.findall(r'^> Task :([^\s]+)', build_log, re.M),
        direct_official_remap_copy=True, jar_repacked=False, post_build_jar_mutation=False,
        built_jar=str(jar), delivery_jar=str(artifact), sha256=digest(jar), bytes=jar.stat().st_size,
        package_verification=package, post_snapshot_changes_not_included=changes,
        automated_tests_run=False, game_started=False)
    save(BUILD / 'build-receipt.json', build)
    before = json.loads((LOG / 'before-install.json').read_text('utf8'))
    current, = active_jars()
    if str(current) != before['path'] or digest(current) != before['sha256']:
        raise RuntimeError('当前实例主包已由其他对话更新，需以最新安装记录核对后再替换。')
    backup = LOG / ('before-install-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir()
    destination = INSTANCE / 'mods' / NAME
    pending = destination.with_suffix('.jar.pending')
    shutil.copy2(artifact, pending)
    shutil.move(str(current), str(backup / current.name))
    pending.replace(destination)
    installed = dict(recorded_at=datetime.now().astimezone().isoformat(), version=VERSION,
        authorization='可以，没问题，但是你控制器打算放哪，那就实装一下 A3，也就是 W12',
        instance=str(INSTANCE), installed_jar=str(destination), backup_jar=str(backup / current.name),
        sha256=digest(destination), all_three_hashes_equal=digest(destination) == digest(artifact) == digest(jar),
        installed=True, restart_required=True, game_started=False, saves_modified=False,
        desktop_used=False, game_verified=False, automated_tests_run=False)
    save(LOG / 'install-receipt.json', installed)
    save(OUT / '安装回执.json', installed)
    print(json.dumps(dict(installed=str(destination), sha256=installed['sha256'], equal=installed['all_three_hashes_equal'])), flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'finish': finish}[sys.argv[1]]()
