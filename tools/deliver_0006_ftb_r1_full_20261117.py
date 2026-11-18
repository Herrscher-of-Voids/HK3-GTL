import sys
from collections import Counter
from zipfile import ZipFile

import deliver_0001_r22_full as full


shared = full.shared
ROOT = full.ROOT
WORK = shared.Path('C:/Users/OWNER/.codex/builds/0006-ftb-r1-20261117-full')
SOURCE = WORK / 'source'
LOG = ROOT / 'logs/0006-ftb-integration-20261117/full-build-r1'
OUT = ROOT / 'deliveries/0006文案设计_FTB正式接入_R1_20261117'
VERSION = '0.5.0-ftb-r1'
NAME = '0006文案设计-' + VERSION + '.jar'
COMMAND = ['gradlew.bat', '--no-daemon', '--no-build-cache', '--max-workers=2',
    '--project-cache-dir', '../project-cache', '-Parchives_base_name=0006文案设计',
    '-Pmod_version=' + VERSION, 'remapJar', '-x', 'check', '-x', 'test', '--console=plain']
shared.DIRECTORIES = [*shared.DIRECTORIES, 'deliveries/0006文案设计_FTB逐章审核_20261116']
shared.FILES = [*shared.FILES, 'logs/0006-ftb-integration-20261117/completion.json']
full.WORK, full.SOURCE, full.LOG, full.OUT = WORK, SOURCE, LOG, OUT
full.VERSION, full.NAME, full.COMMAND = VERSION, NAME, COMMAND
save, digest, now = shared.save, shared.digest, shared.now
freeze, build, archive, refresh = full.freeze, full.build, full.archive, full.refresh


def finish():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    command = shared.json.loads((LOG / 'build-command.json').read_text('utf8'))
    build_log = (LOG / 'build.log').read_text('utf8')
    tasks = shared.re.findall(r'^> Task :([^\s]+)', build_log, shared.re.M)
    if int((LOG / 'exit-code.txt').read_text('utf8')) or not set(shared.TASKS).issubset(tasks):
        raise RuntimeError('完整生产任务未成功。')
    result = next(line for line in build_log.splitlines() if line.startswith('BUILD SUCCESSFUL'))
    jar = SOURCE / 'build/libs' / NAME
    resource_root = SOURCE / 'src/main/resources'
    resources = ['assets/hk3gtl/lang/zh_cn.json', 'assets/hk3gtl/lang/en_us.json',
        'data/hk3gtl/guide/quest_catalog.json']
    for directory in ('assets/hk3gtl/ftbquests', 'data/hk3gtl/research'):
        resources.extend(path.relative_to(resource_root).as_posix()
            for path in (resource_root / directory).rglob('*') if path.is_file())
    classes = ['common/integration/FtbQuestsIntegration', 'common/integration/Hk3QuestCatalog',
        'common/integration/Hk3QuestEvents', 'common/integration/Hk3QuestProgressBridge',
        'common/research/Hk3ResearchRecipeRuntime', 'common/research/Hk3ProductionOutput',
        'common/research/Hk3RecipeAccess', 'common/research/Hk3ProcessReceipts',
        'common/recipe/Hk3ResearchProcessRecipes', 'common/compat/stargate/Hk3StargateQuestEvents',
        'mixin/stargate/Hk3ClassicStargateActivationMixin', 'mixin/stargate/Hk3DhdQuestOperatorMixin']
    with ZipFile(jar) as zipped:
        names = set(zipped.namelist())
        metadata = zipped.read('META-INF/mods.toml').decode('utf8')
        mod = next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if shared.re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', block.split('[[')[0]))
        mod_id = shared.re.search(r'modId\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        version = shared.re.search(r'version\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        config = shared.json.loads(zipped.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ('mixins', 'client', 'server') for name in config.get(key, [])]
        plugin = config['plugin'].replace('.', '/') + '.class'
        shared.json.loads(zipped.read(config['refmap']))
        checked = []
        for name in sorted(resources):
            actual = shared.hashlib.sha256(zipped.read(name)).hexdigest()
            expected = digest(resource_root / name)
            checked.append(dict(path=name, sha256=actual, snapshot_sha256=expected,
                matches_snapshot=actual == expected))
        chapters = [shared.json.loads(zipped.read(name)) for name in sorted(names)
            if name.startswith('assets/hk3gtl/ftbquests/chapters/') and name.endswith('.snbt')]
        catalog = shared.json.loads(zipped.read('data/hk3gtl/guide/quest_catalog.json'))
        required = ['com/sirin/hk3gtl/' + name + '.class' for name in classes]
        nested = sorted(path.relative_to(SOURCE / 'build/classes/java/main').as_posix()
            for stem in classes for path in (SOURCE / 'build/classes/java/main/com/sirin/hk3gtl').glob(stem + '$*.class'))
        compact = [name for name in names if '/structures/compact/' in name and name.endswith('.bin.gz')]
        package = dict(mod_id=mod_id, version=version, mixin_classes=len(mixins),
            mixins_complete=all(name in names for name in mixins), mixin_plugin_present=plugin in names,
            refmap=config['refmap'], refmap_valid=True, required_classes=required + nested,
            required_classes_present=all(name in names for name in required + nested),
            chapters=len(chapters), quests=sum(len(c['quests']) for c in chapters),
            native_tasks=sum(len(q['tasks']) for c in chapters for q in c['quests']),
            catalog_entries=len(catalog['entries']), catalog_kinds=dict(Counter(e['kind'] for e in catalog['entries'])),
            compact_resources=len(compact), resources=checked)
    if not all([mod_id == 'hk3gtl', version == VERSION, package['mixins_complete'],
            package['mixin_plugin_present'], package['required_classes_present'], compact,
            (package['chapters'], package['quests'], package['native_tasks'], package['catalog_entries']) == (23, 1040, 1067, 402),
            all(item['matches_snapshot'] for item in checked)]):
        raise RuntimeError('产物版本、Mixin或正式任务资源核对失败。')
    OUT.mkdir(parents=True, exist_ok=True)
    artifact = OUT / NAME
    shared.shutil.copy2(jar, artifact)
    built_hash, delivery_hash = digest(jar), digest(artifact)
    if built_hash != delivery_hash:
        raise RuntimeError('交付副本SHA-256不一致。')
    before = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256']) for item in manifest['files']}
    stamps = shared.json.loads((LOG / 'input-stamps.json').read_text('utf8'))
    cache = {str((ROOT / path).resolve()): (tuple(stamps[path]), entry) for path, entry in before.items()}
    receipt = dict(recorded_at=now(), conversation='0006',
        conversation_id='01a1e042-4c60-7c83-8cba-7fef452a1cd5', version=VERSION,
        source_snapshot=str(SOURCE), frozen_at=manifest['frozen_at'],
        input_manifest=str(LOG / 'input-manifest.json'), input_manifest_sha256=digest(LOG / 'input-manifest.json'),
        input_files=len(before), input_bytes=sum(item['bytes'] for item in before.values()),
        command=COMMAND, java_home=shared.JAVA_HOME, project_cache=str(WORK / 'project-cache'),
        initial_build_output_empty=command['initial_build_output_empty'],
        initial_project_cache_empty=command['initial_project_cache_empty'],
        snapshot_consistent=manifest['snapshot_consistent'], full_production_source_set=True,
        build_successful=True, task_result=result, production_tasks=tasks,
        build_log=str(LOG / 'build.log'), direct_official_remap_copy=True,
        jar_repacked=False, post_build_jar_mutation=False, built_jar=str(jar), delivery_jar=str(artifact),
        bytes=jar.stat().st_size, sha256=built_hash, delivery_sha256=delivery_hash, both_hashes_equal=True,
        package_verification=package, post_snapshot_changes_not_included=shared.differences(before, full.inventory(ROOT, cache)),
        automated_tests_run=False, installed=False, game_started=False, game_verified=False)
    save(LOG / 'build-receipt.json', receipt)
    save(OUT / '完整构建回执.json', receipt)
    print(shared.json.dumps(dict(delivery=str(artifact), sha256=built_hash,
        post_snapshot_changes=len(receipt['post_snapshot_changes_not_included'])), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'archive': archive, 'build': build, 'finish': finish, 'refresh': refresh}[sys.argv[1]]()
