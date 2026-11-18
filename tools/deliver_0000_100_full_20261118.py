import sys
from struct import unpack
from zipfile import ZipFile

import deliver_0001_r22_full as full


shared = full.shared
ROOT = full.ROOT
WORK = shared.Path('C:/Users/OWNER/.codex/builds/0000-release-1.0.0-item64-20261118-full')
SOURCE = WORK / 'source'
LOG = ROOT / 'logs/0000-release-1.0.0-item64-20261118'
OUT = ROOT / 'deliveries/HK3GTL-1.0.0_物品64_20261118'
VERSION = '1.0.0'
NAME = 'HK3GTL-1.0.0.jar'
COMMAND = ['gradlew.bat', '--no-daemon', '--no-build-cache', '--max-workers=2',
    '--project-cache-dir', '../project-cache', '-Parchives_base_name=HK3GTL',
    '-Pmod_version=1.0.0', '-Pmod_name=HK3GTL', 'remapJar',
    '-x', 'check', '-x', 'test', '--console=plain']
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
    published_root = SOURCE / 'build/resources/main'
    texture_report_path = SOURCE / 'build/reports/runtime-textures.json'
    texture_report = shared.json.loads(texture_report_path.read_text('utf8'))
    runtime_report_paths = [SOURCE / 'build/reports' / name for name in ('runtime-blueprints.json', 'runtime-scenes.json')]
    runtime_reports = [shared.json.loads(path.read_text('utf8')) for path in runtime_report_paths if path.exists()]
    runtime_items = [item for report in runtime_reports for item in report.get('resources', report.get('scenes', []))]
    runtime_by_path = {item['path']: item for item in runtime_items}
    resources = ['assets/hk3gtl/lang/zh_cn.json', 'assets/hk3gtl/lang/en_us.json',
        'data/hk3gtl/guide/quest_catalog.json']
    for directory in ('assets/hk3gtl/ftbquests', 'data/hk3gtl/research'):
        resources.extend(path.relative_to(resource_root).as_posix()
            for path in (resource_root / directory).rglob('*') if path.is_file())
    for role in ('w07', 'w13', 'w14', 'w15'):
        resources.extend('data/hk3gtl/structures/' + role + suffix
            for suffix in ('_approved.json', '_candidate.bin.gz'))
    compiled_root = SOURCE / 'build/classes/java/main'
    classes = sorted(path.relative_to(compiled_root).as_posix()
        for path in compiled_root.rglob('*.class'))
    with ZipFile(jar) as zipped:
        names = set(zipped.namelist())
        metadata = zipped.read('META-INF/mods.toml').decode('utf8')
        mod = next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if shared.re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]', block.split('[[')[0]))
        mod_id = shared.re.search(r'modId\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        version = shared.re.search(r'version\s*=\s*["\x27]([^"\x27]+)', mod).group(1)
        jar_manifest = zipped.read('META-INF/MANIFEST.MF').decode('utf8')
        config = shared.json.loads(zipped.read('hk3gtl.mixins.json'))
        mixins = [config['package'].replace('.', '/') + '/' + name.replace('.', '/') + '.class'
            for key in ('mixins', 'client', 'server') for name in config.get(key, [])]
        plugin = config['plugin'].replace('.', '/') + '.class'
        shared.json.loads(zipped.read(config['refmap']))
        checked = [dict(path=name, sha256=shared.hashlib.sha256(zipped.read(name)).hexdigest(),
            matches_snapshot=(shared.hashlib.sha256(zipped.read(name)).hexdigest() == runtime_by_path[name]['runtime_sha256']
                and digest(resource_root / name) == runtime_by_path[name]['source_sha256']) if name in runtime_by_path
                else zipped.read(name) == (published_root / name).read_bytes())
            for name in sorted(set(resources))]
        chapters = [shared.json.loads(zipped.read(name)) for name in sorted(names)
            if name.startswith('assets/hk3gtl/ftbquests/chapters/') and name.endswith('.snbt')]
        compact = [name for name in names if '/structures/compact/' in name and name.endswith('.bin.gz')]
        textures = []
        for item in texture_report['textures']:
            source = (resource_root / item['path']).read_bytes()
            runtime = zipped.read(item['path'])
            textures.append(dict(path=item['path'],
                source_sha256=shared.hashlib.sha256(source).hexdigest(),
                source_matches_report=shared.hashlib.sha256(source).hexdigest() == item['source_sha256'],
                runtime_sha256=shared.hashlib.sha256(runtime).hexdigest(),
                runtime_matches_report=shared.hashlib.sha256(runtime).hexdigest() == item['runtime_sha256'],
                source_size=list(unpack('>II', source[16:24])),
                runtime_size=list(unpack('>II', runtime[16:24])),
                sizes_match_report=list(unpack('>II', source[16:24])) == item['source_size']
                    and list(unpack('>II', runtime[16:24])) == item['runtime_size']))
            if 'metadata' in item:
                meta = item['metadata']
                source_meta = (resource_root / meta['path']).read_bytes()
                runtime_meta = zipped.read(meta['path'])
                source_animation = shared.json.loads(source_meta)['animation']
                runtime_animation = shared.json.loads(runtime_meta)['animation']
                textures[-1]['animation_correct'] = all([
                    shared.hashlib.sha256(source_meta).hexdigest() == meta['source_sha256'],
                    shared.hashlib.sha256(runtime_meta).hexdigest() == meta['runtime_sha256'],
                    [runtime_animation['width'], runtime_animation['height']] == [64, 64],
                    {k: v for k, v in source_animation.items() if k not in ('width', 'height')}
                        == {k: v for k, v in runtime_animation.items() if k not in ('width', 'height')},
                    item['source_size'][1] // source_animation['height']
                        == item['runtime_size'][1] // runtime_animation['height']])
        item_sizes = [list(unpack('>II', zipped.read(name)[16:24])) for name in sorted(names)
            if name.startswith('assets/hk3gtl/textures/item/') and name.endswith('.png')]
        texture_verification = dict(report=str(texture_report_path),
            report_sha256=digest(texture_report_path), count=len(textures),
            item_frame_size=texture_report['item_frame_size'],
            large_texture_size=texture_report['large_texture_size'],
            item_textures=len(item_sizes), item_widths_at_most_64=all(size[0] <= 64 for size in item_sizes),
            textures=textures)
        runtime_data = []
        for item in runtime_items:
            relative = item.get('source_path', item['path'])
            original = resource_root / relative
            if not original.exists():
                original = SOURCE / 'build/generated/compactResources' / relative
            runtime_data.append(dict(path=item['path'], source_matches_report=digest(original) == item['source_sha256'],
                runtime_matches_report=shared.hashlib.sha256(zipped.read(item['path'])).hexdigest() == item['runtime_sha256'],
                **(dict(raw_content_equal=item['raw_sha256'] == item['restored_sha256'])
                    if 'raw_sha256' in item else dict(geometry_sha256=item['geometry_sha256'])),
                replaced_source_absent=relative not in names if 'source_path' in item else True))
        package = dict(mod_id=mod_id, version=version, runtime_data=runtime_data,
            implementation_version_correct='Implementation-Version: 1.0.0' in jar_manifest,
            mixin_classes=len(mixins), mixins_complete=all(name in names for name in mixins),
            mixin_plugin_present=plugin in names, refmap=config['refmap'], refmap_valid=True,
            enhancedcore_range='[5.1.1,6.0.0)',
            enhancedcore_range_in_plugin=b'[5.1.1,6.0.0)' in zipped.read(plugin),
            compiled_classes=len(classes), all_compiled_classes_present=all(name in names for name in classes),
            chapters=len(chapters), quests=sum(len(chapter['quests']) for chapter in chapters),
            native_tasks=sum(len(q['tasks']) for chapter in chapters for q in chapter['quests']),
            compact_resources=len(compact), resources=checked, runtime_textures=texture_verification)
    if not all([mod_id == 'hk3gtl', version == VERSION, package['implementation_version_correct'],
            package['mixins_complete'], package['mixin_plugin_present'], package['enhancedcore_range_in_plugin'],
            package['all_compiled_classes_present'], classes, compact,
            all(item['matches_snapshot'] for item in checked),
            all(item['source_matches_report'] and item['runtime_matches_report'] and item.get('raw_content_equal', True)
                and item['replaced_source_absent'] for item in runtime_data),
            texture_report['item_frame_size'] == [64, 64], texture_verification['item_widths_at_most_64'],
            all(item['source_matches_report'] and item['runtime_matches_report']
                and item['sizes_match_report'] and item.get('animation_correct', True)
                for item in textures)]):
        raise RuntimeError('产物版本、完整编译类、Mixin、正式资源或运行贴图核对失败。')
    OUT.mkdir(parents=True)
    artifact = OUT / NAME
    shared.shutil.copy2(jar, artifact)
    built_hash, delivery_hash = digest(jar), digest(artifact)
    if built_hash != delivery_hash:
        raise RuntimeError('交付副本SHA-256不一致。')
    receipt = dict(recorded_at=now(), conversation='0000',
        conversation_id='01a1d6a1-e812-7c21-b745-d9775cbc92cc', version=VERSION,
        naming_authorization='负责人本轮明确指定HK3GTL-1.0.0.jar',
        source_snapshot=str(SOURCE), frozen_at=manifest['frozen_at'],
        input_manifest=str(LOG / 'input-manifest.json'),
        input_manifest_sha256=digest(LOG / 'input-manifest.json'),
        dialogue_inventory=str(LOG / 'dialogue-inventory.json'),
        dialogue_inventory_sha256=digest(LOG / 'dialogue-inventory.json'),
        input_files=len(manifest['files']), input_bytes=sum(item['bytes'] for item in manifest['files']),
        command=COMMAND, java_home=shared.JAVA_HOME, project_cache=str(WORK / 'project-cache'),
        initial_build_output_empty=command['initial_build_output_empty'],
        initial_project_cache_empty=command['initial_project_cache_empty'],
        snapshot_consistent=True, full_production_source_set=True, build_successful=True,
        task_result=result, production_tasks=tasks, build_log=str(LOG / 'build.log'),
        build_log_sha256=digest(LOG / 'build.log'), direct_official_remap_copy=True,
        jar_repacked=False, post_build_jar_mutation=False, built_jar=str(jar), delivery_jar=str(artifact),
        bytes=jar.stat().st_size, sha256=built_hash, delivery_sha256=delivery_hash, both_hashes_equal=True,
        package_verification=package, automated_tests_run=False, installed=False, game_started=False,
        instance_script_changes=False)
    save(LOG / 'build-receipt.json', receipt)
    refresh()
    print(shared.json.dumps(dict(delivery=str(artifact), bytes=jar.stat().st_size,
        sha256=built_hash, compiled_classes=len(classes), chapters=package['chapters'],
        quests=package['quests']), ensure_ascii=False), flush=True)


def cleanup():
    receipt = shared.json.loads((LOG / 'snapshot-archive.json').read_text('utf8'))
    built = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    if digest(shared.Path(built['delivery_jar'])) != built['sha256']:
        raise RuntimeError('清理前交付JAR哈希不匹配。')
    if WORK.resolve() != shared.Path('C:/Users/OWNER/.codex/builds/0000-release-1.0.0-item64-20261118-full').resolve():
        raise RuntimeError('本轮临时目录不匹配。')
    shared.shutil.rmtree(WORK)
    receipt['temporary_work_removed'] = True
    save(LOG / 'snapshot-archive.json', receipt)
    print('本轮已核对归档的临时展开副本已清理。', flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'build': build, 'finish': finish, 'archive': archive,
        'cleanup': cleanup, 'refresh': refresh}[sys.argv[1]]()
