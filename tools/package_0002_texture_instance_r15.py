"""在实际安装主包上叠加R15批准材质与H01路径绑定。"""
from copy import copy
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-runtime-fixes-0002-r15-20261116'
OUT = ROOT / 'deliveries/0002贴图材质_运行绑定与流体轻量_R15_20261116'
VERSION = '0.5.0-textures-r15'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(data):
    return sha256(data).hexdigest()


def main():
    frozen = read(LOG / 'base-freeze.json')
    controllers = read(LOG / 'controller-adoption.json')
    fluids = read(LOG / 'fluid-adoption.json')
    items = read(LOG / 'item-adoption.json')
    source = Path(controllers['actual_base_jar'])
    if digest(source.read_bytes()) != frozen['sha256']:
        raise RuntimeError('实际主包已变化，须重新冻结当前主包后叠加。')
    resources = controllers['resources'] + fluids['resources'] + items['resources']
    payload = {}
    for resource in resources:
        data = (ROOT / resource['source_path']).read_bytes()
        if digest(data) != resource['sha256']:
            raise RuntimeError('批准资源已变化：' + resource['source_path'])
        payload[resource['jar_entry']] = data
    deleted = set(items['deleteEntries'])
    target = OUT / ('0002贴图材质-' + VERSION + '.jar')
    changes, preserved = [], {}
    with zipfile.ZipFile(ROOT / frozen['frozenBase']) as base:
        patch = controllers['runtime_class_patch']
        data = base.read(patch['class'])
        start = patch['length_offset']
        replacement = patch['new_value'].encode()
        payload[patch['class']] = (data[:start] + struct.pack('>H', len(replacement))
                                   + replacement + data[start + 2 + patch['old_utf8_length']:])
        old_version = re.search(rb'^version = "([^"]+)"', base.read('META-INF/mods.toml'), re.M)[1]
        for entry in ('META-INF/mods.toml', 'META-INF/MANIFEST.MF'):
            payload[entry] = base.read(entry).replace(old_version, VERSION.encode())
        existing = set(base.namelist())
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as result:
            result.comment = base.comment
            for info in base.infolist():
                if info.filename in deleted:
                    continue
                data = base.read(info.filename)
                result.writestr(copy(info), payload.get(info.filename, data))
                if info.filename not in payload:
                    preserved[info.filename] = digest(data)
            for entry in sorted(payload.keys() - existing):
                result.writestr(entry, payload[entry])
        for entry, data in payload.items():
            old = base.read(entry) if entry in existing else None
            changes.append({'entry': entry, 'beforeSha256': digest(old) if old is not None else None,
                            'sha256': digest(data), 'bytes': len(data)})
    with zipfile.ZipFile(target) as built:
        mismatches = [entry for entry, data in payload.items() if built.read(entry) != data]
        mismatches += [entry for entry, value in preserved.items() if digest(built.read(entry)) != value]
        if mismatches:
            raise RuntimeError('候选包条目不一致：' + ', '.join(mismatches))
    receipt = {'updatedAt': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(timespec='seconds'),
               'conversation': '0002', 'version': VERSION, 'base': frozen,
               'approval': '负责人批准R15：行吧，就这一套吧。',
               'method': '仅叠本轮批准资源、H01类资源路径常量与版本元数据；其余条目逐字节保持。',
               'jar': target.relative_to(ROOT).as_posix(), 'sha256': digest(target.read_bytes()),
               'bytes': target.stat().st_size, 'patchEntryCount': len(payload),
               'resourceCount': len(resources), 'changes': changes, 'deleteEntries': sorted(deleted),
               'preservedEntryCount': len(preserved), 'preservedAllBytes': True,
               'fullWorkspaceRebuilt': False, 'installed': False, 'gameTested': False}
    (LOG / 'package.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('base', 'changes')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
