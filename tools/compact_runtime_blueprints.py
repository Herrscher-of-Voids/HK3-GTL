"""将运行蓝图分块转置并压缩，源文件保持原样。"""
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

import numpy as np


def compact(path, root):
    with gzip.open(path, 'rb') as source:
        magic, version = struct.unpack('>II', source.read(8))
    widths = {(0x484B3350, 1): 10, (0x484B3350, 2): 18,
        (0x484B3357, 1): 15, (0x57303141, 1): 8}
    width = widths.get((magic, version))
    if width is None:
        return None
    delta = magic == 0x484B3350
    original = path.read_bytes()
    raw_hash, restored_hash = hashlib.sha256(), hashlib.sha256()
    raw_bytes = 0
    target = path.with_suffix('.packed')
    with gzip.open(path, 'rb') as source, target.open('wb') as output:
        with gzip.GzipFile(fileobj=output, mode='wb', filename='', compresslevel=9, mtime=0) as packed:
            packed.write(struct.pack('>IB?', 0x484B335A, width, delta))
            while raw := source.read(width * 65536):
                raw_hash.update(raw)
                raw_bytes += len(raw)
                rows, tail = divmod(len(raw), width)
                body = len(raw) - tail
                matrix = np.frombuffer(raw[:body], dtype=np.uint8).reshape(rows, width)
                if delta and rows:
                    differences = np.empty_like(matrix)
                    differences[0] = matrix[0]
                    np.subtract(matrix[1:], matrix[:-1], out=differences[1:])
                    matrix = differences
                encoded = matrix.T.tobytes() + raw[body:]
                packed.write(struct.pack('>I', len(raw)))
                packed.write(encoded)
                restored = np.frombuffer(encoded[:body], dtype=np.uint8).reshape(width, rows).T
                if delta:
                    restored = np.cumsum(restored, axis=0, dtype=np.uint8)
                restored_hash.update(restored.tobytes() + encoded[body:])
            packed.write(struct.pack('>I', 0))
    if raw_hash.digest() != restored_hash.digest():
        raise ValueError('蓝图压缩前后内容不一致：' + str(path))
    reduced = target.stat().st_size < len(original)
    if reduced:
        target.replace(path)
    else:
        target.unlink()
    runtime = path.read_bytes()
    return dict(path=path.relative_to(root).as_posix(), record_width=width, delta=delta,
        packed=reduced, source_bytes=len(original), runtime_bytes=len(runtime), raw_bytes=raw_bytes,
        source_sha256=hashlib.sha256(original).hexdigest(), runtime_sha256=hashlib.sha256(runtime).hexdigest(),
        raw_sha256=raw_hash.hexdigest(), restored_sha256=restored_hash.hexdigest())


def main():
    root, report = map(Path, sys.argv[1:])
    records = []
    for path in sorted((root / 'data/hk3gtl/structures').rglob('*.bin.gz')):
        item = compact(path, root)
        if item:
            records.append(item)
            print(json.dumps({k: item[k] for k in ('path', 'source_bytes', 'runtime_bytes')}, ensure_ascii=False), flush=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(dict(format='HK3Z/1', block_records=65536, resources=records,
        source_bytes=sum(item['source_bytes'] for item in records),
        runtime_bytes=sum(item['runtime_bytes'] for item in records)), ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    main()
