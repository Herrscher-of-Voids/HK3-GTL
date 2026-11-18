import os
import subprocess
import sys
from zipfile import ZipFile
import deliver_0002_r16_full as shared


ROOT = shared.ROOT
LOG = ROOT / 'logs/ae-nexus-fixes-20261117/full-build-r22'
WORK = shared.Path('C:/Users/OWNER/.codex/builds/0001-ae-r22-20261117-full')
SOURCE = WORK / 'source'
OUT = ROOT / 'deliveries/0001ae优化_天枢修复_R22_20261117'
VERSION = '0.5.0-ae-r22'
NAME = '0001ae优化-' + VERSION + '.jar'
COMMAND = ['gradlew.bat', '--no-daemon', '--no-build-cache', '--max-workers=2',
    '--project-cache-dir', '../project-cache', '-Parchives_base_name=0001ae优化',
    '-Pmod_version=' + VERSION, 'remapJar', '-x', 'check', '-x', 'test', '--console=plain']
SEVEN_ZIP = 'C:/Program Files/7-Zip/7z.exe'
save, digest, now = shared.save, shared.digest, shared.now


def inventory(root, cache):
    while True:
        paths = [root / name for name in shared.FILES if (root / name).is_file()]
        for name in shared.DIRECTORIES:
            paths.extend(path for path in (root / name).rglob('*')
                if path.is_file() and '__pycache__' not in path.parts)
        result = {}
        try:
            for path in sorted(set(paths)):
                key = str(path.resolve())
                while True:
                    before = path.stat()
                    stamp = (before.st_size, before.st_mtime_ns)
                    if key in cache and cache[key][0] == stamp:
                        entry = cache[key][1]
                        break
                    entry = dict(bytes=before.st_size, sha256=digest(path))
                    after = path.stat()
                    if stamp == (after.st_size, after.st_mtime_ns):
                        cache[key] = (stamp, entry)
                        break
                result[path.relative_to(root).as_posix()] = entry
            return result
        except FileNotFoundError:
            continue


def freeze():
    LOG.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir(exist_ok=True)
    (WORK / 'project-cache').mkdir(exist_ok=True)
    if (SOURCE / 'build').exists() or any((WORK / 'project-cache').iterdir()):
        raise RuntimeError('本轮构建输出和项目缓存须为空。')
    started, attempts, cache = now(), [], {}
    if (LOG / 'input-manifest.json').exists():
        prior = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
        stamps = shared.json.loads((LOG / 'input-stamps.json').read_text('utf8'))
        for item in prior['files']:
            entry = dict(bytes=item['bytes'], sha256=item['sha256'])
            for root in (ROOT, SOURCE):
                cache[str((root / item['path']).resolve())] = (tuple(stamps[item['path']]), entry)
    print('读取完整构建输入与SHA-256。', flush=True)
    while True:
        before = inventory(ROOT, cache)
        prior = inventory(SOURCE, cache)
        changes = shared.differences(prior, before)
        print('同步完整输入：' + str(len(changes)) + '项。', flush=True)
        for index, item in enumerate(changes, 1):
            target = SOURCE / item['path']
            cache.pop(str(target.resolve()), None)
            if item['kind'] == 'deleted':
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shared.shutil.copy2(ROOT / item['path'], target)
            if index % 500 == 0:
                print('复制输入 ' + str(index) + '/' + str(len(changes)), flush=True)
        after, copied = inventory(ROOT, cache), inventory(SOURCE, cache)
        changed, mismatch = shared.differences(before, after), shared.differences(before, copied)
        attempts.append(dict(finished_at=now(), source_changes=changed, copy_changes=mismatch))
        save(LOG / 'freeze-progress.json', dict(started_at=started, attempts=attempts))
        if not changed and not mismatch:
            break
        print('输入有变化，重新同步一致快照。', flush=True)
    manifest = dict(started_at=started, frozen_at=now(), source_root=str(ROOT),
        snapshot_root=str(SOURCE), input_directories=shared.DIRECTORIES,
        input_files=shared.FILES, all_saved_production_inputs_included=True,
        prior_outputs_copied=False, snapshot_consistent=True, attempts=attempts,
        files=[dict(path=path, **entry) for path, entry in copied.items()])
    save(LOG / 'input-manifest.json', manifest)
    save(LOG / 'build-command.json', dict(command=COMMAND, working_directory=str(SOURCE),
        java_home=shared.JAVA_HOME, project_cache=str(WORK / 'project-cache'),
        initial_build_output_empty=not (SOURCE / 'build').exists(),
        initial_project_cache_empty=not any((WORK / 'project-cache').iterdir()),
        input_manifest_sha256=digest(LOG / 'input-manifest.json')))
    print('完整快照已固定：' + str(len(copied)) + '项。', flush=True)


def retry():
    from zipfile import ZIP_DEFLATED
    backup = LOG / 'failed-attempt-1-records.zip'
    names = ['input-manifest.json', 'input-stamps.json', 'freeze-progress.json',
        'build-command.json', 'build.log', 'exit-code.txt']
    with ZipFile(backup, 'w', ZIP_DEFLATED, compresslevel=6) as zipped:
        for name in names:
            zipped.write(LOG / name, name)
    with ZipFile(backup) as zipped:
        for name in names:
            if zipped.read(name) != (LOG / name).read_bytes():
                raise RuntimeError('失败构建记录压缩核对失败。')
    save(LOG / 'failed-attempt-1.json', dict(recorded_at=now(), archive=str(backup),
        sha256=digest(backup), reason='并行保存期间远景调用已更新为6参数，配套实现随后保存；最新共享源码已一致',
        original_bytes=sum((LOG / name).stat().st_size for name in names),
        compressed_bytes=backup.stat().st_size, old_outputs_reused=False))
    for directory in (SOURCE / 'build', WORK / 'project-cache'):
        if directory.resolve() not in ((WORK / 'source/build').resolve(), (WORK / 'project-cache').resolve()):
            raise RuntimeError('待清理目录超出本轮工作目录。')
        shared.shutil.rmtree(directory)
    freeze()


def build():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    save(LOG / 'input-stamps.json', {item['path']: [
        (SOURCE / item['path']).stat().st_size, (SOURCE / item['path']).stat().st_mtime_ns]
        for item in manifest['files']})
    env = os.environ.copy()
    env['JAVA_HOME'] = shared.JAVA_HOME
    env['PATH'] = shared.JAVA_HOME + '/bin;' + env['PATH']
    with (LOG / 'build.log').open('w', encoding='utf8') as output:
        process = subprocess.Popen(COMMAND, cwd=SOURCE, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding='utf8', errors='replace')
        for line in process.stdout:
            output.write(line)
            output.flush()
            print(line, end='', flush=True)
        code = process.wait()
    (LOG / 'exit-code.txt').write_text(str(code), 'utf8')
    if code:
        raise RuntimeError('完整构建失败，退出码：' + str(code))


def finish():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    command = shared.json.loads((LOG / 'build-command.json').read_text('utf8'))
    build_log = (LOG / 'build.log').read_text('utf8')
    tasks = shared.re.findall(r'^> Task :([^\s]+)', build_log, shared.re.M)
    if int((LOG / 'exit-code.txt').read_text('utf8')) or not set(shared.TASKS).issubset(tasks):
        raise RuntimeError('完整生产任务未成功。')
    result = next(line for line in build_log.splitlines() if line.startswith('BUILD SUCCESSFUL'))
    jar = SOURCE / 'build/libs' / NAME
    resources = ['data/hk3gtl/research/approved_industrial_processes.json',
        'data/hk3gtl/research/industrial_processes.json',
        'assets/hk3gtl/lang/zh_cn.json', 'assets/hk3gtl/lang/en_us.json',
        'assets/hk3gtl/textures/gui/nexus/background_r8.png',
        'assets/hk3gtl/models/block/ae_nexus_controller_r13.json',
        'assets/hk3gtl/textures/block/ae_nexus_controller_r13/front.png']
    classes = ['common/machine/ae/Hk3NexusMachine', 'mixin/ae/Hk3NexusMatrixUploadMixin',
        'mixin/ae/Hk3NexusGtMatrixUploadMixin', 'mixin/ae/Hk3InfinityBigIntegerCellMixin']
    with ZipFile(jar) as archive:
        names = set(archive.namelist())
        metadata = archive.read('META-INF/mods.toml').decode('utf8')
        mod = next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if shared.re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', block.split('[[')[0]))
        version = shared.re.search(r'version\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        config = shared.json.loads(archive.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ('mixins', 'client', 'server') for name in config.get(key, [])]
        plugin = config['plugin'].replace('.', '/') + '.class'
        shared.json.loads(archive.read(config['refmap']))
        checked = [dict(path=name, sha256=shared.hashlib.sha256(archive.read(name)).hexdigest(),
            matches_snapshot=archive.read(name) == (SOURCE / 'src/main/resources' / name).read_bytes())
            for name in resources]
        required = ['com/sirin/hk3gtl/' + name + '.class' for name in classes]
        compact = [name for name in names if '/structures/compact/' in name and name.endswith('.bin.gz')]
        package = dict(mod_id='hk3gtl', version=version, mixin_classes=len(mixins),
            mixins_complete=all(name in names for name in mixins),
            mixin_plugin_present=plugin in names, refmap=config['refmap'],
            refmap_valid=True, ae_classes_present=all(name in names for name in required),
            compact_resources=len(compact), resources=checked,
            excluded_eco_patch_absent=not any('Hk3NeoEcoStorageListingMixin' in name for name in names))
    if not all([version == VERSION, package['mixins_complete'], package['mixin_plugin_present'],
            package['ae_classes_present'], compact, package['excluded_eco_patch_absent'],
            all(item['matches_snapshot'] for item in checked)]):
        raise RuntimeError('产物版本、Mixin或资源核对失败。')
    OUT.mkdir(parents=True)
    artifact = OUT / NAME
    shared.shutil.copy2(jar, artifact)
    built_hash, delivery_hash = digest(jar), digest(artifact)
    if built_hash != delivery_hash:
        raise RuntimeError('交付副本SHA-256不一致。')
    before = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256']) for item in manifest['files']}
    cache = {}
    for item in manifest['files']:
        stat = (SOURCE / item['path']).stat()
        cache[str((ROOT / item['path']).resolve())] = ((stat.st_size, stat.st_mtime_ns), before[item['path']])
    receipt = dict(recorded_at=now(), conversation='0001',
        conversation_id='01a1d38f-c0ec-7192-83fc-49ca15a1d25f', version=VERSION,
        source_snapshot=str(SOURCE), frozen_at=manifest['frozen_at'],
        input_manifest=str(LOG / 'input-manifest.json'),
        input_manifest_sha256=digest(LOG / 'input-manifest.json'),
        input_files=len(before), input_bytes=sum(item['bytes'] for item in before.values()),
        command=COMMAND, java_home=shared.JAVA_HOME, project_cache=str(WORK / 'project-cache'),
        initial_build_output_empty=command['initial_build_output_empty'],
        initial_project_cache_empty=command['initial_project_cache_empty'],
        snapshot_consistent=True, full_production_source_set=True, build_successful=True,
        task_result=result, production_tasks=tasks, build_log=str(LOG / 'build.log'),
        direct_official_remap_copy=True, jar_repacked=False, post_build_jar_mutation=False,
        built_jar=str(jar), delivery_jar=str(artifact), bytes=jar.stat().st_size,
        sha256=built_hash, delivery_sha256=delivery_hash, both_hashes_equal=True,
        package_verification=package, post_snapshot_changes_not_included=shared.differences(before, inventory(ROOT, cache)),
        automated_tests_run=False, installed=False, game_started=False)
    save(LOG / 'build-receipt.json', receipt)
    save(OUT / '完整构建回执.json', receipt)
    print(shared.json.dumps(dict(delivery=str(artifact), sha256=built_hash,
        post_snapshot_changes=len(receipt['post_snapshot_changes_not_included'])), ensure_ascii=False), flush=True)


def archive():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    listing = LOG / 'input-files.txt'
    listing.write_text('\n'.join(item['path'] for item in manifest['files']) + '\n', 'utf8')
    target = LOG / 'complete-input.7z'
    with (LOG / 'archive.log').open('w', encoding='utf8') as output:
        subprocess.run([SEVEN_ZIP, 'a', '-t7z', '-mx=1', '-mmt=2', '-scsUTF-8',
            str(target), '@' + str(listing)], cwd=SOURCE, stdout=output, stderr=subprocess.STDOUT, check=True)
        subprocess.run([SEVEN_ZIP, 't', str(target)], stdout=output, stderr=subprocess.STDOUT, check=True)
    details = subprocess.check_output([SEVEN_ZIP, 'l', '-slt', '-sccUTF-8', str(target)]).decode('utf8').replace('\r\n', '\n')
    entries = {}
    for block in details.split('----------', 1)[1].strip().split('\n\n'):
        fields = dict(line.split(' = ', 1) for line in block.splitlines() if ' = ' in line)
        entries[fields['Path'].replace('\\', '/')] = int(fields['Size'])
    expected = {item['path']: item['bytes'] for item in manifest['files']}
    if entries != expected:
        raise RuntimeError('压缩归档输入清单不一致。')
    receipt = dict(recorded_at=now(), archive=str(target), sha256=digest(target),
        files=len(manifest['files']), original_bytes=sum(item['bytes'] for item in manifest['files']),
        compressed_bytes=target.stat().st_size, integrity_check='7z t及逐文件路径和大小核对通过',
        archived_from=str(SOURCE), temporary_work_removed=False)
    save(LOG / 'snapshot-archive.json', receipt)
    print('完整输入已压缩归档并核对。', flush=True)


def cleanup():
    receipt = shared.json.loads((LOG / 'snapshot-archive.json').read_text('utf8'))
    build_receipt = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    if digest(shared.Path(build_receipt['delivery_jar'])) != build_receipt['sha256']:
        raise RuntimeError('清理前交付JAR哈希不匹配。')
    if WORK.resolve() != shared.Path('C:/Users/OWNER/.codex/builds/0001-ae-r22-20261117-full').resolve():
        raise RuntimeError('临时工作目录不匹配。')
    shared.shutil.rmtree(WORK)
    receipt['temporary_work_removed'] = True
    save(LOG / 'snapshot-archive.json', receipt)
    print('本轮临时展开副本已清理。', flush=True)


def refresh():
    manifest = shared.json.loads((LOG / 'input-manifest.json').read_text('utf8'))
    stamps = shared.json.loads((LOG / 'input-stamps.json').read_text('utf8'))
    before = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256']) for item in manifest['files']}
    cache = {str((ROOT / path).resolve()): (tuple(stamps[path]), entry) for path, entry in before.items()}
    receipt = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    receipt['post_snapshot_changes_not_included'] = shared.differences(before, inventory(ROOT, cache))
    receipt['post_snapshot_changes_recorded_at'] = now()
    save(LOG / 'build-receipt.json', receipt)
    save(OUT / '完整构建回执.json', receipt)
    print('冻结后未纳入改动：' + str(len(receipt['post_snapshot_changes_not_included'])), flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'retry': retry, 'build': build, 'finish': finish,
        'archive': archive, 'cleanup': cleanup, 'refresh': refresh}[sys.argv[1]]()
