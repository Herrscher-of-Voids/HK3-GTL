import sys
from zipfile import ZipFile

import deliver_0000_100_full_20261118 as base


shared = base.shared
ROOT = base.ROOT
WORK = shared.Path('C:/Users/OWNER/.codex/builds/0000-release-1.0.0-compact-campus-20261118-full')
SOURCE = WORK / 'source'
LOG = ROOT / 'logs/0000-release-1.0.0-compact-campus-20261118'
OUT = ROOT / 'deliveries/HK3GTL-1.0.0_资源无损压缩_20261118'
PREVIOUS = ROOT / 'deliveries/HK3GTL-1.0.0_物品64_20261118/HK3GTL-1.0.0.jar'
for module in (base, base.full):
    module.WORK, module.SOURCE, module.LOG, module.OUT = WORK, SOURCE, LOG, OUT


def freeze():
    LOG.mkdir(parents=True, exist_ok=True)
    inventory = shared.json.loads((ROOT / 'logs/0000-release-1.0.0-item64-20261118/dialogue-inventory.json').read_text('utf8'))
    inventory['current_scope'] = '保留完整统合与64像素物品资源，接入建筑和场景无损编码，补齐W07正式预览及预设园区登记。'
    shared.save(LOG / 'dialogue-inventory.json', inventory)
    base.freeze()


def finish():
    verification_path = LOG / 'scene-content-verification.json'
    verification = shared.json.loads(verification_path.read_text('utf8'))
    scene_report = shared.json.loads((SOURCE / 'build/reports/runtime-scenes.json').read_text('utf8'))
    verified_report = ROOT / 'logs/0000-scene-codec-20261118/runtime-scenes.json'
    if not verification['all_passed'] or scene_report != shared.json.loads(verified_report.read_text('utf8')):
        raise RuntimeError('场景生成结果与逐值还原核对记录不一致。')
    base.finish()
    receipt = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    for name in ('runtime-textures.json', 'runtime-blueprints.json', 'runtime-scenes.json'):
        shared.shutil.copy2(SOURCE / 'build/reports' / name, LOG / name)
    receipt['resource_encoding'] = {name: shared.json.loads((LOG / ('runtime-' + name + '.json')).read_text('utf8'))
        for name in ('blueprints', 'scenes')}
    receipt['scene_content_verification'] = dict(path=str(verification_path),
        sha256=shared.digest(verification_path), runtime_report_sha256=shared.digest(verified_report),
        all_passed=verification['all_passed'], scenes=len(verification['scenes']),
        integer_values=sum(item['integer_values'] for item in verification['scenes']))
    receipt['size_reduction'] = dict(previous_jar=str(PREVIOUS), previous_sha256=shared.digest(PREVIOUS),
        previous_bytes=PREVIOUS.stat().st_size, current_bytes=receipt['bytes'],
        saved_bytes=PREVIOUS.stat().st_size - receipt['bytes'])
    with ZipFile(receipt['delivery_jar']) as jar:
        receipt['largest_entries'] = [dict(path=item.filename, bytes=item.file_size, compressed_bytes=item.compress_size)
            for item in sorted(jar.infolist(), key=lambda item: item.compress_size, reverse=True)[:20]]
    shared.save(LOG / 'build-receipt.json', receipt)
    base.refresh()
    print(shared.json.dumps(receipt['size_reduction'], ensure_ascii=False), flush=True)


def cleanup():
    receipt = shared.json.loads((LOG / 'snapshot-archive.json').read_text('utf8'))
    built = shared.json.loads((LOG / 'build-receipt.json').read_text('utf8'))
    if shared.digest(shared.Path(built['delivery_jar'])) != built['sha256']:
        raise RuntimeError('清理前交付JAR哈希不匹配。')
    if WORK.resolve() != shared.Path('C:/Users/OWNER/.codex/builds/0000-release-1.0.0-compact-campus-20261118-full').resolve():
        raise RuntimeError('本轮临时目录不匹配。')
    shared.shutil.rmtree(WORK)
    receipt['temporary_work_removed'] = True
    shared.save(LOG / 'snapshot-archive.json', receipt)


if __name__ == '__main__':
    {'freeze': freeze, 'build': base.build, 'finish': finish, 'archive': base.archive,
        'cleanup': cleanup, 'refresh': base.refresh}[sys.argv[1]]()
