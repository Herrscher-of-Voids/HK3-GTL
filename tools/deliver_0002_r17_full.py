import sys
import json
import shutil
import deliver_0002_r16_full as full


full.LOG = full.ROOT / 'logs/textures-energy-handoff-0002-r17-20261116'
full.BUILD = full.LOG / 'full-build-r2'
full.SNAPSHOT = full.BUILD / 'source'
full.OUT = full.ROOT / 'deliveries/0002贴图材质_发电补充_R17_20261116'
full.VERSION = '0.5.0-textures-r17'
full.NAME = '0002贴图材质-' + full.VERSION + '.jar'
full.COMMAND = full.COMMAND.replace('0.5.0-textures-r16', full.VERSION)
full.RESOURCE_COUNTS = dict(png=12, item_models=4, mcmeta=8)


def inventory_after_snapshot(root=full.ROOT):
    manifest = json.loads((full.BUILD / 'input-manifest.json').read_text('utf8'))
    frozen = {item['path']: dict(bytes=item['bytes'], sha256=item['sha256'])
        for item in manifest['files']}
    while True:
        paths = [root / name for name in full.FILES if (root / name).is_file()]
        for name in full.DIRECTORIES:
            paths.extend(path for path in (root / name).rglob('*')
                if path.is_file() and '__pycache__' not in path.parts)
        result = {}
        try:
            for path in sorted(set(paths)):
                relative = path.relative_to(root).as_posix()
                before = path.stat()
                stamp = (before.st_size, before.st_mtime_ns)
                if relative in frozen:
                    snapshot = (full.SNAPSHOT / relative).stat()
                    if stamp == (snapshot.st_size, snapshot.st_mtime_ns):
                        result[relative] = frozen[relative]
                        continue
                while True:
                    sha256 = full.digest(path)
                    after = path.stat()
                    if stamp == (after.st_size, after.st_mtime_ns):
                        result[relative] = dict(bytes=after.st_size, sha256=sha256)
                        break
                    stamp = (after.st_size, after.st_mtime_ns)
            return result
        except FileNotFoundError:
            continue


def finish():
    original_inventory = full.inventory
    full.inventory = inventory_after_snapshot
    try:
        full.finish()
    finally:
        full.inventory = original_inventory


def freeze():
    full.BUILD.mkdir(parents=True, exist_ok=True)
    resumed = full.SNAPSHOT.exists()
    full.SNAPSHOT.mkdir(exist_ok=True)
    project_cache = full.BUILD / 'project-cache'
    project_cache.mkdir(exist_ok=True)
    if (full.SNAPSHOT / 'build').exists() or any(project_cache.iterdir()):
        raise RuntimeError('本次构建输出与独立项目缓存须初始为空。')
    adoption = json.loads((full.LOG / 'adoption.json').read_text('utf8'))
    full.save(full.BUILD / 'resource-adoption.json', adoption)
    cache = {}

    def record(path):
        absolute = str(path.resolve())
        while True:
            before = path.stat()
            stamp = (before.st_size, before.st_mtime_ns)
            if absolute in cache and cache[absolute][0] == stamp:
                return cache[absolute][1]
            sha256 = full.digest(path)
            after = path.stat()
            if stamp == (after.st_size, after.st_mtime_ns):
                entry = dict(bytes=after.st_size, sha256=sha256)
                cache[absolute] = (stamp, entry)
                return entry

    def inventory(root):
        while True:
            paths = [root / name for name in full.FILES
                if root == full.ROOT or (root / name).is_file()]
            for name in full.DIRECTORIES:
                paths.extend(path for path in (root / name).rglob('*')
                    if path.is_file() and '__pycache__' not in path.parts)
            try:
                return {path.relative_to(root).as_posix(): record(path) for path in sorted(set(paths))}
            except FileNotFoundError:
                continue

    started, attempts = full.now(), []
    snapshot_root = full.SNAPSHOT.resolve()
    print('读取完整输入与已有快照SHA-256，后续仅重读变化文件。', flush=True)
    while True:
        attempt_started = full.now()
        before = inventory(full.ROOT)
        prior = inventory(full.SNAPSHOT)
        synchronized = full.differences(prior, before)
        for item in synchronized:
            target = (full.SNAPSHOT / item['path']).resolve()
            if not target.is_relative_to(snapshot_root):
                raise RuntimeError('快照文件路径超出本次独立构建目录。')
            cache.pop(str(target), None)
            if item['kind'] == 'deleted':
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(full.ROOT / item['path'], target)
                except FileNotFoundError:
                    continue
        after, copied = inventory(full.ROOT), inventory(full.SNAPSHOT)
        changed = full.differences(before, after)
        copy_changes = full.differences(before, copied)
        attempts.append(dict(started_at=attempt_started, finished_at=full.now(),
            synchronized_paths=[dict(path=item['path'], kind=item['kind']) for item in synchronized],
            source_changes=changed, copy_changes=copy_changes))
        full.save(full.BUILD / 'freeze-progress.json', dict(started_at=started, attempts=attempts))
        print(f'快照第{len(attempts)}轮：同步{len(synchronized)}项，源变化{len(changed)}项，副本差异{len(copy_changes)}项。', flush=True)
        if not changed and not copy_changes:
            break
    resource_changes = [item['target'] for item in adoption['resources']
        if copied[item['target']]['sha256'] != item['sha256']]
    if resource_changes:
        raise RuntimeError('正式资源与接入清单不一致：' + ', '.join(resource_changes))
    manifest = dict(started_at=started, frozen_at=full.now(), source_root=str(full.ROOT),
        snapshot_root=str(full.SNAPSHOT), input_directories=full.DIRECTORIES, input_files=full.FILES,
        all_saved_production_inputs_included=True, prior_outputs_copied=False,
        snapshot_consistent=True, attempts=attempts, resumed_partial_snapshot=resumed,
        hash_cache_key='absolute_path,size,mtime_ns', initial_sha256_read=True,
        copied_target_cache_invalidated=True,
        preceding_freeze_interruption=dict(process_id=30176, session_id=43522, exit_code=1,
            input_manifest_fixed=False, build_started=False,
            reason='完整重复制期间并行源码持续保存，停止旧进程后复用本次未固定的部分快照。'),
        files=[dict(path=path, **entry) for path, entry in copied.items()])
    full.save(full.BUILD / 'input-manifest.json', manifest)
    full.save(full.BUILD / 'build-command.json', dict(command=full.COMMAND,
        working_directory=str(full.SNAPSHOT), java_home=full.JAVA_HOME,
        project_cache=str(project_cache), initial_build_output_empty=True,
        initial_project_cache_empty=True,
        input_manifest_sha256=full.digest(full.BUILD / 'input-manifest.json'),
        adoption_sha256=full.digest(full.BUILD / 'resource-adoption.json')))
    script = "$env:JAVA_HOME = '" + full.JAVA_HOME + "'\n"
    script += "$env:Path = $env:JAVA_HOME + '/bin;' + $env:Path\n"
    script += "Set-Location -LiteralPath (Join-Path $PSScriptRoot 'source')\n"
    script += full.COMMAND + " 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'build.log')\n"
    script += "$buildExit = $LASTEXITCODE\n"
    script += "Set-Content -LiteralPath (Join-Path $PSScriptRoot 'exit-code.txt') -Value $buildExit\n"
    script += "exit $buildExit\n"
    (full.BUILD / 'build-command.ps1').write_text(script, 'utf-8-sig')
    print(json.dumps(dict(snapshot=str(full.SNAPSHOT), files=len(copied),
        bytes=sum(item['bytes'] for item in copied.values()), attempts=len(attempts),
        command_script=str(full.BUILD / 'build-command.ps1')), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    {'freeze': freeze, 'finish': finish}[sys.argv[1]]()
