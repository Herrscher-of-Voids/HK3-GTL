# -*- coding: utf-8 -*-
"""完整原稿接入分批搭建，仅在舰艏中央替换真实主控。"""
from pathlib import Path
import gzip
import hashlib
import io
import json
import struct
import nbtlib
import numpy as np
from scipy.ndimage import binary_fill_holes

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'doc/HK3GTL-内测5/03_机器结构/休伯利安_原投影预览_20260929'
OUT = ROOT / 'src/main/resources/data/hk3gtl/structures/hyperion_construction.bin.gz'
LOG = ROOT / 'logs/remove-fixed-ports-r266-20261113/hyperion'
SHA = '2238856e3358f88802eb71f59a8d7765a50397fa6bf111d63e992bef2723b91c'
SIZE = (1145, 240, 549)
ANCHOR = (1061, 82, 274)


def raw_nbt(tag):
    out = io.BytesIO()
    nbtlib.File(tag).write(out)
    return out.getvalue()


def build_interior(cells):
    solid = np.zeros((SIZE[1], SIZE[2], SIZE[0]), dtype=bool)
    solid.reshape(-1)[cells] = True
    interior = binary_fill_holes(solid)
    interior.reshape(-1)[cells] = False
    packed = np.flatnonzero(interior).astype(np.uint32)
    cuts = np.flatnonzero(np.diff(packed) != 1) + 1
    runs = np.column_stack((np.r_[packed[0], packed[cuts]], np.r_[packed[cuts - 1], packed[-1]])).astype('>u4')
    target = OUT.with_name('hyperion_interior.bin.gz')
    with target.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', mtime=0) as stream:
        stream.write(struct.pack('>i', len(runs)))
        stream.write(runs.tobytes())
    receipt = {'source_sha256': SHA, 'size_xyz': SIZE, 'controller_source_xyz': ANCHOR,
               'enclosed_air_cells': len(packed), 'runs': len(runs),
               'resource': target.relative_to(ROOT).as_posix(),
               'resource_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'scope': '原稿实体六向封闭的内部空气；不含通向舰外的开放空间，不定义生活区'}
    log = ROOT / 'logs/flagship-real-jumps-20261113'
    log.mkdir(parents=True, exist_ok=True)
    (log / 'interior-resource.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return receipt


def main():
    assert hashlib.sha256((SOURCE / '休伯利安.litematic').read_bytes()).hexdigest() == SHA
    meta = json.loads((SOURCE / 'preview.json').read_text(encoding='utf-8'))
    cells = np.fromfile(SOURCE / 'cells.bin', dtype='<u4')
    states = np.fromfile(SOURCE / 'states.bin', dtype='u1')
    assert meta['size'] == [1145, 240, 549] and len(cells) == len(states) == 1469258
    assert np.all(cells[1:] > cells[:-1])
    palette = [p['name'] + ('[' + ','.join(k+'='+v for k, v in sorted(p['properties'].items())) + ']'
                          if p['properties'] else '') for p in meta['palette']]
    palette.append('hk3gtl:hyperion_flagship[facing=east]')
    tiles = {int(t['index']): raw_nbt(t['nbt']) for t in nbtlib.load(SOURCE / 'tiles.nbt')['tiles']}
    assert len(tiles) == 3402 and np.all(np.isin(list(tiles), cells))
    replacements = {(ANCHOR[1]*549+ANCHOR[2])*1145+ANCHOR[0]: len(palette)-1}
    assert np.all(np.isin(list(replacements), cells)) and not (tiles.keys() & replacements.keys())
    changes = []
    for linear, state in replacements.items():
        original = palette[int(states[np.searchsorted(cells, linear)])]
        assert original in ['minecraft:black_concrete', 'minecraft:gray_concrete']
        changes.append({'pos': [linear%1145, linear//(1145*549), linear//1145%549], 'before': original, 'after': palette[state]})
    header = struct.pack('>9iH', 0x484B3350, 1, *SIZE, *ANCHOR, len(cells), len(palette))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('wb') as target, gzip.GzipFile(fileobj=target, mode='wb', mtime=0) as stream:
        stream.write(header)
        for name in palette:
            encoded = name.encode('utf-8')
            stream.write(struct.pack('>H', len(encoded)) + encoded)
        for linear, material in zip(cells, states):
            linear = int(linear)
            x, y, z = linear % 1145, linear // (1145*549), linear // 1145 % 549
            payload = tiles.get(linear, b'')
            stream.write(struct.pack('>iHi', (x*SIZE[1]+y)*SIZE[2]+z, replacements.get(linear, int(material)), len(payload)))
            stream.write(payload)
    # 仅替换主控，其余状态及全部实体NBT与原稿逐格相等。
    with gzip.open(OUT, 'rb') as stream:
        assert stream.read(len(header)) == header
        for name in palette:
            size = struct.unpack('>H', stream.read(2))[0]
            assert stream.read(size).decode('utf-8') == name
        for linear, material in zip(cells, states):
            at, state, size = struct.unpack('>iHi', stream.read(10))
            x, y, z = at // SIZE[2] // SIZE[1], at // SIZE[2] % SIZE[1], at % SIZE[2]
            original = (y*549+z)*1145+x
            assert original == int(linear) and state == replacements.get(int(linear), int(material))
            assert stream.read(size) == tiles.get(original, b'')
        assert stream.read(1) == b''
    receipt = {'date': '2026-11-13', 'source_sha256': SHA, 'hull_size_xyz': [1145, 240, 549],
               'construction_bounds_xyz': SIZE, 'controller_source_xyz': ANCHOR, 'source_facing': 'east',
               'hull_blocks': len(cells), 'construction_records': len(cells), 'source_block_entities': len(tiles),
               'authorized_surface_substitutions': changes, 'ports_source_xyz': [],
               'original_source_file_unchanged': True, 'all_records_and_nbt_readback_equal_except_controller': True,
               'resource': OUT.relative_to(ROOT).as_posix(), 'resource_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
               'creative_only': True, 'full_formation_accepted': False,
               'interior': build_interior(cells)}
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / 'resource-verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, ensure_ascii=True))


if __name__ == '__main__':
    main()
