# -*- coding: utf-8 -*-
"""I34开敞观测仪：密集阵列流式导出，逐格回读NBT、Schematic和外露面。

变更记录 #1（2026-10-27）：新增候选导出器，不改正式结构或实例。
"""
from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
import struct
import tempfile

import numpy as np

from build_redesign69 import integer, listint, palette_nbt, tag


CHUNK = 65536
RECORD = listint('pos', [0, 0, 0]) + integer('state', 0) + b'\x00'
RECORD_DTYPE = np.dtype(dict(names=['x', 'y', 'z', 'state'], formats=['>i4'] * 4,
                            offsets=[11, 15, 19, 31], itemsize=36))
assert len(RECORD) == RECORD_DTYPE.itemsize == 36


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def exact(handle, count):
    data = handle.read(count)
    if len(data) != count:
        raise ValueError('结构文件截断')
    return data


def _headers(states, shape, block_count):
    h, d, w = shape
    nbt = tag(10, '') + integer('DataVersion', 3465) + listint('size', [w, h, d])
    nbt += tag(9, 'palette') + b'\x0a' + struct.pack('>i', len(states))
    nbt += b''.join(palette_nbt(state) for state in states)
    nbt += tag(9, 'blocks') + b'\x0a' + struct.pack('>i', block_count)
    schem = tag(10, 'Schematic') + integer('Version', 2) + integer('DataVersion', 3465)
    for key, value in zip(('Width', 'Height', 'Length'), (w, h, d)):
        schem += tag(2, key) + struct.pack('>h', value)
    schem += tag(11, 'Offset') + struct.pack('>i3i', 3, 0, 0, 0)
    schem += integer('PaletteMax', len(states) + 1) + tag(10, 'Palette')
    schem += integer('minecraft:air', 0)
    schem += b''.join(integer(state, i + 1) for i, state in enumerate(states))
    schem += b'\x00' + tag(7, 'BlockData') + struct.pack('>i', w * h * d)
    return nbt, schem


def _validate(cube, states):
    if not isinstance(cube, np.ndarray) or cube.dtype != np.uint8 or cube.ndim != 3:
        raise ValueError('cube必须为uint8[h,d,w]数组')
    if not cube.flags.c_contiguous:
        raise ValueError('cube必须按C顺序连续存储')
    if not 0 < len(states) < 127 or len(set(states)) != len(states):
        raise ValueError('调色板须唯一且有1至126种非空气方块')
    if any(state == 'minecraft:air' for state in states):
        raise ValueError('空气只能使用索引0，不可列入states')
    if any(not isinstance(state, str) or ':' not in state for state in states):
        raise ValueError('方块必须使用完整命名空间ID')
    if any(not 0 < n <= 32767 for n in cube.shape):
        raise ValueError('Sponge v2轴长超出正short范围')
    if cube.size > 2147483647 or int(cube.max()) > len(states):
        raise ValueError('方块索引或总网格大小超出导出范围')
    counts = np.bincount(cube.ravel(), minlength=len(states) + 1)
    if not np.all(counts[1:]):
        raise ValueError('states包含未使用的方块')
    return counts


def surface_groups(cube, states):
    """仅导出与空气/边界接触的六向表面，索引保持Y、Z、X递增。"""
    occupied = cube != 0
    groups = [[[] for _ in range(6)] for _ in states]
    # 朝向依次为east、west、south、north、down、up，与现有三维查看器一致。
    for face, axis, sign in ((0, 2, 1), (1, 2, -1), (2, 1, 1),
                             (3, 1, -1), (4, 0, -1), (5, 0, 1)):
        neighbor = np.zeros_like(occupied)
        destination = [slice(None)] * 3
        source = [slice(None)] * 3
        destination[axis] = slice(None, -1) if sign > 0 else slice(1, None)
        source[axis] = slice(1, None) if sign > 0 else slice(None, -1)
        neighbor[tuple(destination)] = occupied[tuple(source)]
        exposed = occupied & ~neighbor
        indices = np.flatnonzero(exposed.ravel())
        ids = cube.ravel()[indices]
        for material in range(len(states)):
            groups[material][face] = indices[ids == material + 1].tolist()
    return groups


def verify_dense(cube, states, nbt_path, schem_path):
    """回读每条结构记录及Schematic整幅数组，不构造百万个Python方块对象。"""
    counts = _validate(cube, states)
    count = int(counts[1:].sum())
    h, d, w = cube.shape
    expected_nbt, expected_schem = _headers(states, cube.shape, count)
    flat = cube.ravel()
    read_counts = np.zeros(len(states) + 1, dtype=np.int64)
    previous = -1
    with gzip.open(nbt_path, 'rb') as handle:
        assert exact(handle, len(expected_nbt)) == expected_nbt, 'NBT头、尺寸或调色板不同'
        for start in range(0, count, CHUNK):
            n = min(CHUNK, count - start)
            data = exact(handle, n * len(RECORD))
            raw = np.frombuffer(data, dtype=np.uint8).reshape(n, len(RECORD))
            assert np.all(raw[:, :11] == np.frombuffer(RECORD[:11], dtype=np.uint8))
            assert np.all(raw[:, 23:31] == np.frombuffer(RECORD[23:31], dtype=np.uint8))
            assert np.all(raw[:, 35] == 0), 'NBT记录结束标签不符'
            records = np.frombuffer(data, dtype=RECORD_DTYPE)
            x, y, z, mid = (records[key].astype(np.int64) for key in ('x', 'y', 'z', 'state'))
            assert np.all((0 <= x) & (x < w) & (0 <= y) & (y < h) & (0 <= z) & (z < d))
            assert np.all((0 <= mid) & (mid < len(states)))
            indices = (y * d + z) * w + x
            assert indices[0] > previous and np.all(indices[1:] > indices[:-1]), 'NBT重复或未按索引递增'
            assert np.array_equal(flat[indices], mid + 1), 'NBT逐格与原几何不同'
            previous = int(indices[-1])
            read_counts += np.bincount(mid + 1, minlength=len(states) + 1)
        tail = tag(9, 'entities') + b'\x0a' + struct.pack('>i', 0) + b'\x00'
        assert exact(handle, len(tail)) == tail and not handle.read(1), 'NBT尾部不符'
    assert np.array_equal(read_counts[1:], counts[1:]), 'NBT材料数量或总块数不同'
    with gzip.open(schem_path, 'rb') as handle:
        assert exact(handle, len(expected_schem)) == expected_schem, 'Schematic头、尺寸或调色板不同'
        for start in range(0, flat.size, 1024 * 1024):
            expected = flat[start:start + 1024 * 1024]
            assert exact(handle, expected.size) == expected.tobytes(), 'Schematic逐格与原几何不同'
        assert exact(handle, 1) == b'\x00' and not handle.read(1), 'Schematic尾部不符'
    return dict(passed=True, geometry_nbt_schematic_per_block_equal=True,
                size_xyz=[w, h, d], blocks=count, palette_count=len(states))


def export_dense(cube, states, name, out_dir):
    """导出完整标准结构与Sponge文件；返回哈希、表面组和实际块数。"""
    counts = _validate(cube, states)
    if not name or Path(name).name != name or name in ('.', '..'):
        raise ValueError('name必须是单个文件名，不得包含路径')
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    nbt_path, schem_path = out_dir / (name + '.nbt'), out_dir / (name + '.schem')
    count = int(counts[1:].sum())
    nbt_header, schem_header = _headers(states, cube.shape, count)
    h, d, w = cube.shape
    flat = cube.ravel()
    indices = np.flatnonzero(flat)
    template = np.frombuffer(RECORD, dtype=np.uint8)
    with gzip.open(nbt_path, 'wb', compresslevel=6) as handle:
        handle.write(nbt_header)
        for start in range(0, count, CHUNK):
            current = indices[start:start + CHUNK]
            raw = np.tile(template, (len(current), 1))
            records = raw.view(RECORD_DTYPE).reshape(-1)
            records['x'] = current % w
            records['y'] = current // (w * d)
            records['z'] = current // w % d
            records['state'] = flat[current].astype(np.int32) - 1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a' + struct.pack('>i', 0) + b'\x00')
    del indices
    with gzip.open(schem_path, 'wb', compresslevel=6) as handle:
        handle.write(schem_header)
        for start in range(0, flat.size, 1024 * 1024):
            handle.write(flat[start:start + 1024 * 1024].tobytes())
        handle.write(b'\x00')
    readback = verify_dense(cube, states, nbt_path, schem_path)
    groups = surface_groups(cube, states)
    return dict(hashes={'nbt': digest(nbt_path), 'schem': digest(schem_path)},
                surface_groups=groups, block_count=count, readback=readback)


def self_check():
    import nbtlib
    states = ['minecraft:stone', 'minecraft:oak_log[axis=x]']
    cube = np.ones((5, 4, 6), dtype=np.uint8)
    cube[1:4, 1:3, 1:5] = 0
    cube[2, 1, 3] = 2
    cube[0, 0, 0] = 0
    with tempfile.TemporaryDirectory(prefix='i34-export-selfcheck-') as folder:
        result = export_dense(cube, states, 'sample', folder)
        loaded = nbtlib.load(Path(folder) / 'sample.nbt')
        independent = np.zeros_like(cube)
        for block in loaded['blocks']:
            x, y, z = map(int, block['pos'])
            assert independent[y, z, x] == 0
            independent[y, z, x] = int(block['state']) + 1
        assert np.array_equal(independent, cube)
        assert str(loaded['palette'][1]['Properties']['axis']) == 'x'
        loaded = nbtlib.load(Path(folder) / 'sample.schem')
        assert np.array_equal(np.asarray(loaded['BlockData']).view(np.uint8), cube.ravel())
        assert {str(key): int(value) for key, value in loaded['Palette'].items()} == {
            'minecraft:air': 0, states[0]: 1, states[1]: 2}
        expected = [[[] for _ in range(6)] for _ in states]
        for y, z, x in zip(*np.nonzero(cube)):
            index = (int(y) * cube.shape[1] + int(z)) * cube.shape[2] + int(x)
            for face, (dx, dy, dz) in enumerate(((1, 0, 0), (-1, 0, 0), (0, 0, 1),
                                                (0, 0, -1), (0, -1, 0), (0, 1, 0))):
                xx, yy, zz = x + dx, y + dy, z + dz
                if not (0 <= yy < cube.shape[0] and 0 <= zz < cube.shape[1] and 0 <= xx < cube.shape[2]) or not cube[yy, zz, xx]:
                    expected[int(cube[y, z, x]) - 1][face].append(index)
        assert expected == result['surface_groups']
        return dict(passed=True, blocks=result['block_count'],
                    surface_faces=sum(len(face) for group in expected for face in group),
                    independent_nbtlib_readback=True)


if __name__ == '__main__':
    import json
    print(json.dumps(self_check(), ensure_ascii=False))
