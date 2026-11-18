import sys
from zipfile import ZipFile, ZIP_DEFLATED

import deliver_0001_r22_full as full


shared = full.shared
ROOT = full.ROOT
fixes = {
    '--fluid-fix': (4, 'fluid-color', '流体颜色修复_', '0005-mx-uuid-recipe-20261119'),
    '--circuit-fix': (5, 'controller-circuit', '控制器电路修复_', '0005-mx-uuid-fluid-color-20261119'),
    '--campus-fix': (6, 'campus-catalog', '园区目录修复_', '0005-mx-uuid-controller-circuit-20261119'),
}
revision, slug, label, prior_release = 3, 'recipe', '', '0005-mx-uuid-20261119'
if sys.argv[1:2] and sys.argv[1] in fixes:
    revision, slug, label, prior_release = fixes[sys.argv.pop(1)]
FLUID_FIX = revision >= 4
release = f'0005-mx-uuid-{slug}-20261119'
WORK = shared.Path('C:/Users/OWNER/.codex/builds') / (release + '-full')
SOURCE = WORK / 'source'
LOG = ROOT / 'logs' / release / 'full-build'
OUT = ROOT / 'deliveries' / f'0005多方块设计_UUID复制系统_{label}20261119'
VERSION = f'1.2.1-mx-uuid.{revision}'
NAME = '0005多方块设计-' + VERSION + '.jar'
COMMAND = ['gradlew.bat', '--no-daemon', '--no-build-cache', '--max-workers=2',
    '--project-cache-dir', '../project-cache', '-Parchives_base_name=0005多方块设计',
    '-Pmod_version=' + VERSION, 'remapJar', '-x', 'check', '-x', 'test', '--console=plain']
index_path = ROOT / 'deliveries/多方块确认归档/当前归档索引.json'
index = shared.json.loads(index_path.read_text('utf-8-sig'))
shared.DIRECTORIES += [shared.Path(entry['approved_nbt']).parents[2].relative_to(ROOT).as_posix()
    for entry in index['entries'] if entry['id'].startswith('MX-C')]
shared.FILES += ['deliveries/多方块确认归档/当前归档索引.json',
    'logs/0005-mx-uuid-20261119/source-integration.json']
if FLUID_FIX:
    shared.FILES += [f'deliveries/0003_40台工业内容补全_20261119/{stage}-{kind}.json'
        for stage in ('early', 'world', 'late') for kind in ('assets', 'links')]
full.WORK, full.SOURCE, full.LOG, full.OUT = WORK, SOURCE, LOG, OUT
full.VERSION, full.NAME, full.COMMAND = VERSION, NAME, COMMAND
save, digest, now = shared.save, shared.digest, shared.now
build, archive, refresh = full.build, full.archive, full.refresh
original_inventory = full.inventory


def inventory(root, cache):
    if root == ROOT and not cache:
        prior_log = ROOT / 'logs' / prior_release / 'full-build'
        prior = shared.json.loads((prior_log / 'input-manifest.json').read_text('utf8'))
        stamps = shared.json.loads((prior_log / 'input-stamps.json').read_text('utf8'))
        for item in prior['files']:
            cache[str((ROOT / item['path']).resolve())] = (tuple(stamps[item['path']]),
                dict(bytes=item['bytes'], sha256=item['sha256']))
    return original_inventory(root, cache)


full.inventory = inventory


def freeze():
    full.freeze()
    save_input_stamps()


def save_input_stamps():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    save(LOG / 'input-stamps.json', {item['path']: [item['bytes'], (SOURCE / item['path']).stat().st_mtime_ns]
        for item in manifest['files']})


def retry():
    attempt = len(list(LOG.glob('failed-attempt-*-records.zip'))) + 1
    names = ['input-manifest.json', 'input-stamps.json', 'freeze-progress.json',
        'build-command.json', 'build.log', 'exit-code.txt', 'archive.log', 'snapshot-archive.json']
    records = LOG / ('failed-attempt-' + str(attempt) + '-records.zip')
    with ZipFile(records, 'w', ZIP_DEFLATED, compresslevel=6) as zipped:
        for name in names:
            zipped.write(LOG / name, name)
    with ZipFile(records) as zipped:
        for name in names:
            if zipped.read(name) != (LOG / name).read_bytes():
                raise RuntimeError('失败构建记录压缩核对失败。')
    archived = shared.json.loads((LOG / 'snapshot-archive.json').read_text('utf8'))
    old_archive = shared.Path(archived['archive'])
    if digest(old_archive) != archived['sha256']:
        raise RuntimeError('失败构建输入归档哈希不匹配。')
    failed_input = LOG / ('failed-attempt-' + str(attempt) + '-input.7z')
    old_archive.rename(failed_input)
    archived['archive'] = str(failed_input)
    save(LOG / ('failed-attempt-' + str(attempt) + '-input-archive.json'), archived)
    save(LOG / ('failed-attempt-' + str(attempt) + '.json'), dict(recorded_at=now(),
        reason=sys.argv[2], records=str(records), records_sha256=digest(records),
        original_record_bytes=sum((LOG / name).stat().st_size for name in names),
        compressed_record_bytes=records.stat().st_size, input_archive=str(failed_input),
        input_archive_sha256=archived['sha256'], old_outputs_reused=False))
    (LOG / 'snapshot-archive.json').unlink()
    for directory in (SOURCE / 'build', WORK / 'project-cache'):
        if directory.resolve() not in ((WORK / 'source/build').resolve(), (WORK / 'project-cache').resolve()):
            raise RuntimeError('清理目录超出本轮独立工作目录。')
        shared.shutil.rmtree(directory)
    freeze()


def finish():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    command = shared.json.loads((LOG / 'build-command.json').read_text('utf8'))
    log = (LOG / 'build.log').read_text('utf8')
    tasks = shared.re.findall(r'^> Task :([^\s]+)', log, shared.re.M)
    if int((LOG / 'exit-code.txt').read_text('utf8')) or not set(shared.TASKS).issubset(tasks):
        raise RuntimeError('完整生产构建未成功。')
    jar = SOURCE / 'build/libs' / NAME
    resources = ['data/hk3gtl/tags/items/replication_excluded.json']
    fluid_path = 'data/hk3gtl/catalog/industrial_expansion_fluids.json'
    if FLUID_FIX:
        resources.append(fluid_path)
    resources += ['data/hk3gtl/structures/mx_c0' + str(i) + ext for i in range(1, 5) for ext in ['.nbt', '.json']]
    resources += ['assets/hk3gtl/lang/zh_cn.json', 'assets/hk3gtl/lang/en_us.json']
    library_path = 'data/hk3gtl/catalog/multiblock_pattern_library.json'
    resources += [library_path, 'assets/hk3gtl/ftbquests/chapters/hk3_multiblock_patterns.snbt']
    package_dir = SOURCE / 'src/main/java/com/sirin/hk3gtl/common/machine/replication'
    classes = ['common/machine/replication/' + p.stem for p in package_dir.glob('*.java')]
    with ZipFile(jar) as zipped:
        names = set(zipped.namelist())
        metadata = zipped.read('META-INF/mods.toml').decode('utf8')
        mod = next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if shared.re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', block.split('[[')[0]))
        version = shared.re.search(r'version\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        config = shared.json.loads(zipped.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ['mixins', 'client', 'server'] for name in config.get(key, [])]
        shared.json.loads(zipped.read(config['refmap']))
        library = {entry['key']: entry['controller'] for entry in shared.json.loads(zipped.read(library_path))}
        patterns = {key: library[key] for key in ('mx_c01', 'mx_c02', 'mx_c03', 'mx_c04')}
        for key, controller in patterns.items():
            if controller != shared.json.loads(zipped.read('data/hk3gtl/structures/' + key + '.json'))['machine']:
                raise RuntimeError('建材目录与正式主控不一致：' + key)
        checked = []
        for name in resources:
            raw = zipped.read(name)
            actual = shared.hashlib.sha256(raw).hexdigest()
            expected = digest(SOURCE / 'build/resources/main' / name)
            checked.append(dict(path=name, bytes=len(raw), sha256=actual,
                processed_snapshot_sha256=expected, matches_processed_snapshot=actual == expected))
        package = dict(mod_id='hk3gtl', version=version, refmap=config['refmap'], refmap_valid=True,
            mixins_complete=all(name in names for name in mixins),
            mixin_plugin_present=config['plugin'].replace('.', '/') + '.class' in names,
            replication_classes_complete=all('com/sirin/hk3gtl/' + name + '.class' in names for name in classes),
            replication_classes=sorted(classes), physical_patterns=len(patterns), pattern_library=patterns,
            target_source=shared.json.loads((SOURCE / 'logs/0005-mx-uuid-20261119/source-integration.json').read_text('utf8'))['target_source'],
            storage='server overworld SavedData / player UUID', resources=checked)
        if FLUID_FIX:
            fluids = shared.json.loads(zipped.read(fluid_path))
            polish = next(row['color'] for row in fluids if row['id'] == 'tree_optical_polish')
            if polish != 0x9B73DC or not all(type(row['color']) is int and 0 <= row['color'] <= 0xFFFFFF for row in fluids):
                raise RuntimeError('包内工业流体颜色必须为 RGB 整数且保留抛光液原色。')
            package['industrial_fluid_colors'] = dict(rgb24_integers=len(fluids), tree_optical_polish=polish)
    if not all([version == VERSION, package['mixins_complete'], package['mixin_plugin_present'],
            package['replication_classes_complete'], all(item['matches_processed_snapshot'] for item in checked)]):
        raise RuntimeError('产物版本、Mixin或复制系统正式资源核对失败。')
    OUT.mkdir(parents=True, exist_ok=True)
    artifact = OUT / NAME
    shared.shutil.copy2(jar, artifact)
    built_hash, delivery_hash = digest(jar), digest(artifact)
    if built_hash != delivery_hash:
        raise RuntimeError('交付副本SHA-256不一致。')
    before = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256']) for item in manifest['files']}
    snapshot = original_inventory(SOURCE, {})
    snapshot_changes = shared.differences(before, snapshot)
    if snapshot_changes:
        raise RuntimeError('完整构建期间原始输入有变化：' + str(snapshot_changes))
    stamps = shared.json.loads((LOG / 'input-stamps.json').read_text('utf8'))
    cache = {str((ROOT / path).resolve()): (tuple(stamps[path]), entry) for path, entry in before.items()}
    receipt = dict(recorded_at=now(), conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', version=VERSION,
        frozen_at=manifest['frozen_at'], source_snapshot=str(SOURCE),
        input_manifest=str(LOG / 'input-manifest.json'), input_manifest_sha256=digest(LOG / 'input-manifest.json'),
        input_files=len(before), input_bytes=sum(item['bytes'] for item in before.values()),
        snapshot_consistent=manifest['snapshot_consistent'], snapshot_unchanged_after_build=True,
        full_production_source_set=True, command=COMMAND, java_home=shared.JAVA_HOME,
        project_cache=str(WORK / 'project-cache'), initial_build_output_empty=command['initial_build_output_empty'],
        initial_project_cache_empty=command['initial_project_cache_empty'], build_successful=True,
        task_result=next(line for line in log.splitlines() if line.startswith('BUILD SUCCESSFUL')),
        production_tasks=tasks, build_log=str(LOG / 'build.log'), direct_official_remap_copy=True,
        jar_repacked=False, post_build_jar_mutation=False, built_jar=str(jar), delivery_jar=str(artifact),
        bytes=jar.stat().st_size, sha256=built_hash, delivery_sha256=delivery_hash, both_hashes_equal=True,
        package_verification=package, post_snapshot_changes_not_included=shared.differences(before, inventory(ROOT, cache)),
        automated_tests_run=False, installed=False, game_started=False, game_verified=False)
    save(LOG / 'build-receipt.json', receipt)
    save(OUT / '完整构建回执.json', receipt)
    print(shared.json.dumps(dict(delivery=str(artifact), sha256=built_hash, bytes=receipt['bytes']), ensure_ascii=False), flush=True)


def cleanup():
    record = shared.json.loads((LOG / 'snapshot-archive.json').read_text('utf8'))
    receipt = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    if WORK.resolve() != (shared.Path('C:/Users/OWNER/.codex/builds') / (release + '-full')).resolve():
        raise RuntimeError('本轮临时目录不匹配。')
    if digest(shared.Path(record['archive'])) != record['sha256'] or digest(shared.Path(receipt['delivery_jar'])) != receipt['sha256']:
        raise RuntimeError('清理前归档或交付产物哈希不匹配。')
    shared.shutil.rmtree(WORK)
    record['temporary_work_removed'] = True
    save(LOG / 'snapshot-archive.json', record)
    print('本轮临时展开快照已清理。', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    {'freeze': freeze, 'retry': retry, 'build': build, 'finish': finish, 'archive': archive,
        'refresh': refresh, 'cleanup': cleanup}[sys.argv[1]]()
