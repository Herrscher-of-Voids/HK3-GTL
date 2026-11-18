# -*- coding: utf-8 -*-
"""以实际AE R19主包为基底，仅叠入最新版材质及必要绑定。"""
from datetime import datetime
from copy import copy
from pathlib import Path
import hashlib
import json
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-instance-adoption-0002-r14-20261115'
OUT = ROOT / 'deliveries/0002贴图材质_实例接入_R14_20261115'
VERSION = '0.5.0-textures-r14'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    frozen = read(LOG / 'base-freeze.json')
    scope = read(LOG / 'asset-scope.json')
    bindings = read(LOG / 'binding-scope.json')
    payload = {entry: (ROOT / 'src/main/resources' / entry).read_bytes()
               for entry in scope['patchEntries']}
    changes = []
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / ('0002贴图材质-' + VERSION + '.jar')
    with zipfile.ZipFile(ROOT / frozen['frozenBase']) as base:
        for patch in bindings['rendererConstantPatches']:
            entry = patch['entry']
            data = base.read(entry)
            start = patch['lengthOffset']
            replacement = patch['new'].encode()
            payload[entry] = (data[:start] + struct.pack('>H', len(replacement)) + replacement
                              + data[start + 2 + patch['oldByteLength']:])
        with zipfile.ZipFile(bindings['resourceSourceJar']) as production:
            for key in ('certificate', 'industrialFluids'):
                entry = bindings[key]['entry']
                payload[entry] = production.read(entry)
        toml = base.read('META-INF/mods.toml')
        old_version = re.search(rb'^version = "([^"]+)"', toml, re.M)[1]
        for entry in ('META-INF/mods.toml', 'META-INF/MANIFEST.MF'):
            payload[entry] = base.read(entry).replace(old_version, VERSION.encode())
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as result:
            result.comment = base.comment
            existing = set(base.namelist())
            for info in base.infolist():
                data = base.read(info.filename)
                result.writestr(copy(info), payload.get(info.filename, data))
            for entry in sorted(payload.keys() - existing):
                result.writestr(entry, payload[entry])
        for entry, data in payload.items():
            old = base.read(entry) if entry in existing else None
            changes.append({'entry': entry, 'beforeSha256': sha(old) if old is not None else None,
                            'sha256': sha(data), 'bytes': len(data)})
    receipt = {'updatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
               'conversation': '0002', 'version': VERSION, 'base': frozen,
               'method': '以冻结实际主包叠加284项资源、4个必要class及2项版本元数据；其余条目保持。',
               'jar': target.relative_to(ROOT).as_posix(), 'sha256': sha(target.read_bytes()),
               'bytes': target.stat().st_size, 'patchEntryCount': len(changes), 'changes': changes,
               'fullWorkspaceRebuilt': False, 'installed': False, 'gameTested': False}
    (LOG / 'package.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('base', 'changes')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
