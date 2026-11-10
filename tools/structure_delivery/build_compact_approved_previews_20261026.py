"""修订178：从正式NBT生成无空气记录的流式预览，逐格回读并保留全部方块实体数据。"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
MODULE = Path(__file__).with_name('build_late_approved_resources_20261026.py')
spec = importlib.util.spec_from_file_location('approved_nbt', MODULE)
nbt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nbt)
RES = ROOT / 'src/main/resources/data/hk3gtl'
OUT = RES / 'structures/approved_preview'
LOG = ROOT / 'logs/controller-preview-fix-20261026'
I32 = struct.Struct('>i')
U16 = struct.Struct('>H')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(key):
    source = RES / 'structures/approved' / f'{key}.nbt'
    manifest = json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
    source_sha = sha(source)
    assert source_sha == manifest['template_sha256']
    raw = gzip.decompress(source.read_bytes())
    fields = nbt.top(raw)
    palette = nbt.palette(raw, fields['palette'])
    size, controller = manifest['size_xyz'], manifest['controller']
    count = I32.unpack_from(raw, fields['blocks'][0] + 1)[0]
    assert count == manifest['blocks'] and len(palette) <= 65535
    destination = OUT / f'{key}.bin.gz'
    temporary = destination.with_suffix('.tasktmp')
    OUT.mkdir(parents=True, exist_ok=True)
    expected = hashlib.sha256()
    occupied = set()
    entities = 0
    with temporary.open('wb') as file, gzip.GzipFile(fileobj=file, mode='wb', compresslevel=6, mtime=0) as out:
        out.write(b'HK3P' + I32.pack(1) + struct.pack('>6i', *size, *controller) + I32.pack(count))
        out.write(U16.pack(len(palette)))
        for state in palette:
            value = state.encode('ascii')
            out.write(U16.pack(len(value)) + value)
        at = fields['blocks'][0] + 5
        for _ in range(count):
            start, end, pos, state, _, entity = nbt.block(raw, at)
            at = end
            assert all(0 <= pos[axis] < size[axis] for axis in range(3))
            linear = (pos[0] * size[1] + pos[1]) * size[2] + pos[2]
            assert linear not in occupied
            occupied.add(linear)
            tag = b'\x0a\x00\x00' + raw[entity:nbt.skip(raw, entity, 10)] if entity is not None else b''
            entities += bool(tag)
            row = I32.pack(linear) + U16.pack(state) + I32.pack(len(tag)) + tag
            out.write(row)
            expected.update(row)
        assert at == fields['blocks'][1]
    # 独立回读：每个坐标、状态索引和完整NBT字节必须与正式模板一致。
    with gzip.open(temporary, 'rb') as verify:
        assert verify.read(8) == b'HK3P' + I32.pack(1)
        assert list(struct.unpack('>6i', verify.read(24))) == size + controller
        assert I32.unpack(verify.read(4))[0] == count
        assert U16.unpack(verify.read(2))[0] == len(palette)
        for state in palette:
            assert verify.read(U16.unpack(verify.read(2))[0]).decode('ascii') == state
        actual = hashlib.sha256(verify.read()).hexdigest()
        assert actual == expected.hexdigest()
    assert sha(source) == source_sha
    temporary.replace(destination)
    volume = size[0] * size[1] * size[2]
    return {'key': key, 'source_nbt_sha256': source_sha, 'preview_sha256': sha(destination),
            'size_xyz': size, 'controller': controller, 'blocks': count, 'block_entities': entities,
            'palette': len(palette), 'volume': volume, 'compressed_bytes': destination.stat().st_size,
            'standard_array_references': volume, 'array_reference_bytes_at_4_bytes': volume * 4,
            'all_coordinates_states_and_entity_nbt_verified': True, 'records_sha256': actual}


if __name__ == '__main__':
    records = [build(f'i{number}') for number in range(19, 29)]
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / 'compact-preview-verification.json').write_text(json.dumps({'revision': 178, 'structures': records},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'structures': len(records), 'blocks': sum(row['blocks'] for row in records),
                      'maximum_array_reference_bytes': max(row['array_reference_bytes_at_4_bytes'] for row in records)}, ensure_ascii=False))
