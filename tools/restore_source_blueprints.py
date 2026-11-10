# -*- coding: utf-8 -*-
"""按校验清单恢复压缩蓝图，不覆盖本地修改。"""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import json
import os
import re
import tempfile


SOURCE_DIR = 'src/main/resources/data/hk3gtl/approved_architecture'
ARCHIVE_DIR = 'source_archives/approved_architecture'
CHUNK = 1024 * 1024


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(CHUNK), b''):
            result.update(data)
    return result.hexdigest()


def checked_path(root, value, directory):
    if not isinstance(value, str) or '\\' in value or ':' in value:
        raise ValueError('蓝图路径必须是仓库内的相对路径')
    relative = PurePosixPath(value)
    if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != value:
        raise ValueError('蓝图路径越界：' + value)
    path = root.joinpath(*relative.parts).resolve()
    if path.parent != root / directory:
        raise ValueError('蓝图路径不在指定目录内：' + value)
    return path


def matches(path, entry):
    return path.is_file() and path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256']


def restore(root):
    root = root.resolve()
    manifest = root / ARCHIVE_DIR / 'manifest.json'
    if not manifest.exists():
        return dict(manifest_found=False, restored=0, unchanged=0)
    data = json.loads(manifest.read_text('utf8'))
    if (not isinstance(data, dict) or type(data.get('version')) is not int
            or data['version'] != 1 or not isinstance(data.get('files'), list)):
        raise ValueError('不支持的蓝图归档清单')
    entries = []
    seen = set()
    for entry in data['files']:
        if not isinstance(entry, dict):
            raise ValueError('蓝图归档条目必须是对象')
        target = checked_path(root, entry.get('path'), SOURCE_DIR)
        archive = checked_path(root, entry.get('archive'), ARCHIVE_DIR)
        if target.suffix != '.json' or archive.name != target.name + '.gz' or target in seen:
            raise ValueError('蓝图归档文件名不匹配或重复：' + str(target))
        if type(entry.get('bytes')) is not int or entry['bytes'] < 0:
            raise ValueError('蓝图字节数无效：' + str(target))
        for key in ['sha256', 'archive_sha256']:
            if not isinstance(entry.get(key), str) or not re.fullmatch('[0-9a-f]{64}', entry[key]):
                raise ValueError('蓝图校验值无效：' + key)
        if not archive.is_file() or digest(archive) != entry['archive_sha256']:
            raise ValueError('压缩蓝图缺失或校验失败：' + str(archive))
        if target.exists() and not matches(target, entry):
            raise ValueError('保留本地修改，拒绝覆盖蓝图：' + str(target))
        seen.add(target)
        entries.append((entry, target, archive))
    restored = unchanged = 0
    for entry, target, archive in entries:
        if target.exists():
            unchanged += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(prefix=target.name + '.', suffix='.tmp', dir=target.parent)
        temporary = Path(temporary)
        try:
            count = 0
            result = hashlib.sha256()
            with os.fdopen(handle, 'wb') as output, gzip.open(archive, 'rb') as source:
                while True:
                    block = source.read(min(CHUNK, entry['bytes'] - count + 1))
                    if not block:
                        break
                    count += len(block)
                    if count > entry['bytes']:
                        raise ValueError('蓝图解压大小超出清单：' + str(archive))
                    result.update(block)
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
            if count != entry['bytes'] or result.hexdigest() != entry['sha256']:
                raise ValueError('蓝图原始字节校验失败：' + str(archive))
            checked_path(root, entry['path'], SOURCE_DIR)
            if target.exists():
                if not matches(target, entry):
                    raise ValueError('恢复期间出现本地修改，拒绝覆盖：' + str(target))
                unchanged += 1
            else:
                os.replace(temporary, target)
                restored += 1
        finally:
            if temporary.exists():
                temporary.unlink()
    return dict(manifest_found=True, restored=restored, unchanged=unchanged)


def self_test():
    def fixture(root):
        raw = b'{"blocks": [{"pos": [0, 1, 2], "state": "minecraft:stone"}]}\n'
        archive = root / ARCHIVE_DIR / 'i01.json.gz'
        archive.parent.mkdir(parents=True)
        archive.write_bytes(gzip.compress(raw, mtime=0))
        entry = dict(path=SOURCE_DIR + '/i01.json', archive=ARCHIVE_DIR + '/i01.json.gz',
            bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), archive_sha256=digest(archive))
        return raw, archive, entry

    def publish(root, entry):
        (root / ARCHIVE_DIR / 'manifest.json').write_text(
            json.dumps(dict(version=1, files=[entry])), 'utf8')

    def rejected(root):
        try:
            restore(root)
        except (ValueError, OSError, EOFError):
            assert not list(root.rglob('*.tmp'))
            return
        raise AssertionError('应拒绝损坏或越界的蓝图')

    with tempfile.TemporaryDirectory(prefix='hk3gtl-blueprint-test-') as folder:
        base = Path(folder)
        assert restore(base)['manifest_found'] is False
        root = base / 'valid'
        raw, archive, entry = fixture(root)
        publish(root, entry)
        assert restore(root)['restored'] == 1
        target = root / entry['path']
        assert target.read_bytes() == raw
        stamp = target.stat().st_mtime_ns
        assert restore(root)['unchanged'] == 1 and target.stat().st_mtime_ns == stamp
        target.write_bytes(b'local edit')
        rejected(root)
        assert target.read_bytes() == b'local edit'
        for case in ['archive_hash', 'invalid_gzip', 'raw_hash', 'size', 'path', 'archive_path']:
            root = base / case
            raw, archive, entry = fixture(root)
            if case == 'archive_hash':
                archive.write_bytes(archive.read_bytes() + b'changed')
            elif case == 'invalid_gzip':
                archive.write_bytes(b'not gzip')
                entry['archive_sha256'] = digest(archive)
            elif case == 'raw_hash':
                entry['sha256'] = '0' * 64
            elif case == 'size':
                entry['bytes'] -= 1
            elif case == 'path':
                entry['path'] = '../outside.json'
            else:
                entry['archive'] = ARCHIVE_DIR + '/../outside.json.gz'
            publish(root, entry)
            rejected(root)
            assert not (root / SOURCE_DIR / 'i01.json').exists()
    print('蓝图恢复自测通过：字节回读、幂等、修改保护、压缩与原文校验、大小限制及越界拒绝。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='仅在临时目录自测，不读取真实蓝图')
    if parser.parse_args().self_test:
        self_test()
    else:
        try:
            print(json.dumps(restore(Path(__file__).resolve().parents[1])))
        except (ValueError, OSError, EOFError) as error:
            raise SystemExit('蓝图恢复失败：' + str(error))
