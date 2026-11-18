import gzip
import lzma
from pathlib import Path
from shutil import copyfileobj
import sys


root = Path(sys.argv[1])
for pattern in ('assets/hk3gtl/models/scene/*.scene.bin.gz',
                'data/hk3gtl/structures/w*_candidate.bin.gz',
                'data/hk3gtl/structures/compact/*.bin.gz'):
    for path in sorted(root.glob(pattern)):
        before = path.stat().st_size
        if before < 384 * 1024:
            continue
        target = path.with_suffix('.xz')
        with gzip.open(path, 'rb') as source, lzma.open(target, 'wb', preset=6) as output:
            copyfileobj(source, output, 1024 * 1024)
        after = target.stat().st_size
        if after < before:
            path.unlink()
            print(f'{target.relative_to(root).as_posix()}: {before} -> {after}', flush=True)
        else:
            target.unlink()
