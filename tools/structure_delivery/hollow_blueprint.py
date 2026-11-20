import gzip
import hashlib
import lzma
import shutil
import struct
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, generate_binary_structure


HK3P = 0x484B3350
HK3W = 0x484B3357
W01A = 0x57303141
HK3Z = 0x484B335A
RUN = np.dtype([('start', '>i4'), ('step', '>i4'), ('count', '>i4'),
    ('state', '>u2'), ('entity_bytes', '>i4')])
POINT = np.dtype([('start', '>i4'), ('state', '>u2'), ('entity_bytes', '>i4')])
WONDER = np.dtype([('x', '>i4'), ('y', '>i4'), ('z', '>i4'),
    ('count', 'u1'), ('state', '>u2')])
INTERVAL = np.dtype('<i4')
FACE_NEIGHBORS = generate_binary_structure(3, 1)
OPEN_BLOCKS = {
    'minecraft:air', 'minecraft:amethyst_cluster', 'minecraft:beacon', 'minecraft:daylight_detector',
    'minecraft:end_rod', 'minecraft:glass', 'minecraft:iron_bars', 'minecraft:light',
    'minecraft:piston_head', 'minecraft:soul_sand', 'minecraft:wall_torch',
    'gtceu:assembly_line_grating',
}
OPEN_SUFFIXES = ('_glass', '_pane', '_leaves', '_stairs', '_wall', '_fence', '_door', '_trapdoor', '_sign')
FALLING_REPLACEMENTS = {
    'minecraft:sand': 'minecraft:sandstone',
    'minecraft:red_sand': 'minecraft:red_sandstone',
    'minecraft:gravel': 'minecraft:stone',
    'ad_astra:moon_sand': 'ad_astra:moon_stone',
    'ad_astra:mars_sand': 'ad_astra:mars_stone',
    'ad_astra:venus_sand': 'ad_astra:venus_stone',
}


def _exposes_backing(state):
    block = state.split('[', 1)[0]
    if block in OPEN_BLOCKS or block.endswith(('_glass', '_frame')):
        return True
    return block.startswith('minecraft:') and (block.endswith(OPEN_SUFFIXES)
        or (block.endswith('_slab') and 'type=double' not in state)
        or (block in {'minecraft:piston', 'minecraft:sticky_piston'} and 'extended=true' in state))


class _PackedReader:
    def __init__(self, stream):
        self.stream = stream
        self.width, self.delta = struct.unpack('>B?', stream.read(2))
        self.buffer = bytearray()
        self.finished = False

    def read(self, size):
        while len(self.buffer) < size and not self.finished:
            length = struct.unpack('>I', self.stream.read(4))[0]
            if not length:
                self.finished = True
                break
            body = self.stream.read(length)
            rows, tail = divmod(length, self.width)
            matrix = np.frombuffer(body[:rows * self.width], dtype=np.uint8).reshape(self.width, rows).T
            if self.delta:
                matrix = np.cumsum(matrix, axis=0, dtype=np.uint8)
            self.buffer.extend(matrix.tobytes())
            self.buffer.extend(body[rows * self.width:])
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result


def read_header(path):
    path = Path(path)
    with path.open('rb') as raw:
        signature = raw.read(6)
    opener = gzip.open if signature[:2] == b'\x1f\x8b' else lzma.open if signature == b'\xfd7zXZ\x00' else open
    with opener(path, 'rb') as source:
        magic = struct.unpack('>I', source.read(4))[0]
        if magic == HK3Z:
            stream = _PackedReader(source)
        else:
            source.seek(0)
            stream = source
        header = struct.unpack('>9i', stream.read(36))
        if header[0] == HK3W:
            stream.read(4)
        palette = []
        for _ in range(struct.unpack('>H', stream.read(2))[0]):
            palette.append(stream.read(struct.unpack('>H', stream.read(2))[0]).decode('utf8'))
    return dict(magic=header[0], version=header[1], shape=tuple(header[2:5]),
        controller=tuple(header[5:8]), count=header[8], palette=palette)


def _unpack(source, target):
    with source.open('rb') as raw:
        signature = raw.read(6)
    opener = gzip.open if signature[:2] == b'\x1f\x8b' else lzma.open if signature == b'\xfd7zXZ\x00' else open
    with opener(source, 'rb') as stream, target.open('wb') as output:
        prefix = stream.read(4)
        if struct.unpack('>I', prefix)[0] != HK3Z:
            output.write(prefix)
            shutil.copyfileobj(stream, output, 1024 * 1024)
            return
        width, delta = struct.unpack('>B?', stream.read(2))
        while length := struct.unpack('>I', stream.read(4))[0]:
            body = stream.read(length)
            rows, tail = divmod(length, width)
            matrix = np.frombuffer(body[:rows * width], dtype=np.uint8).reshape(width, rows).T
            if delta:
                matrix = np.cumsum(matrix, axis=0, dtype=np.uint8)
            output.write(matrix.tobytes())
            output.write(body[rows * width:])


def _intervals(mask):
    changes = np.flatnonzero(np.diff(np.r_[False, mask, False]))
    return changes.astype(INTERVAL).reshape(-1, 2)


class HollowBlueprint:
    def __init__(self, path, work_dir, thickness=2, protected_linear=(), protected_states=()):
        self.path = Path(path)
        metadata = read_header(self.path)
        self.magic, self.version = metadata['magic'], metadata['version']
        self.shape, self.controller = metadata['shape'], metadata['controller']
        self.width, self.height, self.depth = self.shape
        self.plane = self.height * self.depth
        self.count = self.count_before = metadata['count']
        self.palette = metadata['palette']
        self.header = [self.magic, self.version, *self.shape, *self.controller, self.count_before]
        self.body_offset = 36 + (4 if self.magic == HK3W else 0) + len(self._palette_bytes())
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.raw_path = self.work_dir / 'source.raw'
        self.thickness = thickness
        self.protected_linear = np.asarray(protected_linear, dtype=np.int64)
        self.protected_states = set(protected_states)
        self.intervals = {}
        self.record_count = 0
        self.entity_count = 0
        self.replacements = {}
        self.falling_supports_kept = 0

    def _palette_bytes(self):
        output = bytearray(struct.pack('>H', len(self.palette)))
        for state in self.palette:
            raw = state.encode('utf8')
            output.extend(struct.pack('>H', len(raw)) + raw)
        return output

    def prepare(self):
        _unpack(self.path, self.raw_path)
        self.protected_palette = np.array([_exposes_backing(state) or state in self.protected_states
            or state.split('[', 1)[0] in self.protected_states for state in self.palette])
        falling_palette = np.array([state in FALLING_REPLACEMENTS for state in self.palette])
        has_falling = falling_palette.any()
        falling_runs = []
        self.counts_before = np.zeros(len(self.palette), dtype=np.int64)
        self.occupied = np.zeros(self.shape, dtype=np.bool_)
        self.protection = np.zeros(self.shape, dtype=np.bool_)
        protected = list(self.protected_linear)
        cx, cy, cz = self.header[5:8]
        protected.append((cx * self.height + cy) * self.depth + cz)
        for runs, entity in self._records():
            self.record_count += len(runs)
            self.counts_before += np.bincount(runs['state'], weights=runs['count'],
                minlength=len(self.palette)).astype(np.int64)
            self._mark(runs)
            if has_falling:
                falling_runs.append(runs[falling_palette[runs['state']]])
            if entity:
                protected.append(int(runs[-1]['start']))
                self.entity_count += 1
        self.protection.reshape(-1)[protected] = True
        self._hollow(falling_runs)
        self.counts_after = np.zeros(len(self.palette), dtype=np.int64)
        self.count_after = 0
        return self

    def _mark(self, runs):
        starts = runs['start'].astype(np.int64)
        counts = runs['count']
        single = counts == 1
        occupied = self.occupied.reshape(-1)
        protection = self.protection.reshape(-1)
        occupied[starts[single]] = True
        protected = single & self.protected_palette[runs['state']]
        protection[starts[protected]] = True
        for run in runs[~single]:
            start, step, count = (int(run[name]) for name in ('start', 'step', 'count'))
            positions = start + np.arange(count, dtype=np.int64) * step
            occupied[positions] = True
            if self.protected_palette[int(run['state'])]:
                protection[positions] = True

    def _records(self):
        dtype = RUN if self.magic == HK3P and self.version == 2 else POINT
        if self.magic == W01A:
            dtype = np.dtype('>u8')
        elif self.magic == HK3W:
            dtype = WONDER
        cells = 0
        with self.raw_path.open('rb') as source:
            source.seek(self.body_offset)
            while cells < self.count_before:
                offset = source.tell()
                body = source.read(min(65536, self.count_before - cells) * dtype.itemsize)
                native = np.frombuffer(body[:len(body) // dtype.itemsize * dtype.itemsize], dtype=dtype)
                entity = b''
                if self.magic == HK3P:
                    entities = np.flatnonzero(native['entity_bytes'])
                    if len(entities):
                        native = native[:entities[0] + 1]
                    source.seek(offset + len(native) * dtype.itemsize)
                    if len(entities):
                        entity = source.read(int(native[-1]['entity_bytes']))
                if self.magic == HK3P and self.version == 2:
                    runs = native
                else:
                    runs = np.zeros(len(native), dtype=RUN)
                    runs['step'] = 1
                    runs['count'] = 1
                    if self.magic == W01A:
                        x = native >> 36
                        y = (native >> 26) & 1023
                        z = (native >> 16) & 1023
                        runs['start'] = (x * self.height + y) * self.depth + z
                        runs['state'] = native & 65535
                    elif self.magic == HK3W:
                        runs['start'] = (native['x'].astype(np.int64) * self.height + native['y']) * self.depth + native['z']
                        runs['count'] = native['count']
                        runs['state'] = native['state']
                    else:
                        runs['start'] = native['start']
                        runs['state'] = native['state']
                        runs['entity_bytes'] = native['entity_bytes']
                cells += int(runs['count'].sum(dtype=np.int64))
                yield runs, entity

    def _hollow(self, falling_runs):
        radius = self.thickness
        removed = binary_erosion(self.occupied, FACE_NEIGHBORS, iterations=radius)
        if self.protection.any():
            removed &= ~binary_dilation(self.protection, FACE_NEIGHBORS, iterations=radius)
        if falling_runs:
            self._preserve_falling(np.concatenate(falling_runs), removed.reshape(-1))
        for x in range(self.width):
            self.intervals['removed', x] = _intervals(removed[x].reshape(-1))
            self.intervals['kept', x] = _intervals((self.occupied[x] & ~removed[x]).reshape(-1))
        self.occupied &= ~removed
        self.keep = self.occupied.reshape(-1)
        self.protection = None

    def _preserve_falling(self, runs, removed):
        indices, positions = self._expand(runs)
        below = positions - self.depth
        within = positions // self.depth % self.height != 0
        supported = within.copy()
        supported[within] = self.occupied.reshape(-1)[below[within]]
        supports = below[supported]
        self.falling_supports_kept = int(np.count_nonzero(removed[supports]))
        removed[positions] = False
        removed[supports] = False

        for state in np.unique(runs['state'][indices[~supported]]):
            replacement = FALLING_REPLACEMENTS[self.palette[state]]
            if replacement not in self.palette:
                self.palette.append(replacement)
                self.counts_before = np.append(self.counts_before, 0)
            points = positions[~supported & (runs['state'][indices] == state)]
            self.replacements.update(dict.fromkeys(map(int, points), self.palette.index(replacement)))
        if self.replacements:
            self.replacement_positions, self.replacement_states = np.array(sorted(self.replacements.items())).T

    def _ranges(self, kind, x):
        return self.intervals[kind, x]

    def _lookup(self, kind, x, yz):
        ranges = self._ranges(kind, x)
        indexes = np.searchsorted(ranges[:, 0], yz, side='right') - 1
        if not len(ranges):
            return np.zeros(np.shape(yz), dtype=np.bool_), indexes
        found = (indexes >= 0) & (yz < ranges[np.maximum(indexes, 0), 1])
        return found, indexes

    def _at(self, kind, x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        shape = x.shape
        x, yz = x.reshape(-1), (y * self.depth + z).reshape(-1)
        result = np.zeros(len(x), dtype=np.bool_)
        for value in np.unique(x):
            selected = x == value
            result[selected] = self._lookup(kind, int(value), yz[selected])[0]
        return result.reshape(shape)

    def removed_at(self, x, y, z):
        return self._at('removed', x, y, z)

    def keep_at(self, x, y, z):
        return self._at('kept', x, y, z)

    def removed_x(self, x):
        result = np.zeros(self.plane, dtype=np.bool_)
        for start, end in self._ranges('removed', x):
            result[start:end] = True
        return result

    def iter_removed_x(self):
        for x in range(self.width):
            yield x, self.removed_x(x)

    @staticmethod
    def _expand(runs):
        counts = runs['count'].astype(np.int64)
        indices = np.repeat(np.arange(len(runs)), counts)
        offsets = np.arange(int(counts.sum())) - np.repeat(np.cumsum(counts) - counts, counts)
        return indices, runs['start'][indices].astype(np.int64) + offsets * runs['step'][indices]

    def _replace_falling(self, positions, states):
        indices = np.searchsorted(self.replacement_positions, positions)
        np.minimum(indices, len(self.replacement_positions) - 1, out=indices)
        changed = self.replacement_positions[indices] == positions
        states[changed] = self.replacement_states[indices[changed]]

    def _filter(self, runs):
        if np.all(runs['count'] == 1):
            kept = runs[self.keep[runs['start']]]
            if self.replacements:
                self._replace_falling(kept['start'], kept['state'])
            return kept
        pieces = []
        cumulative = np.cumsum(runs['count'], dtype=np.int64)
        first = 0
        while first < len(runs):
            base = cumulative[first - 1] if first else 0
            end = max(first + 1, int(np.searchsorted(cumulative, base + 1_000_000, side='right')))
            batch = runs[first:end]
            indices, positions = self._expand(batch)
            keep = self.keep[positions]
            same = indices[1:] == indices[:-1]
            if self.replacements:
                states = batch['state'][indices]
                self._replace_falling(positions, states)
                same &= states[1:] == states[:-1]
            starts = np.flatnonzero(keep & np.r_[True, ~keep[:-1] | ~same])
            ends = np.flatnonzero(keep & np.r_[~keep[1:] | ~same, True]) + 1
            selected = batch[indices[starts]].copy()
            selected['start'] = positions[starts]
            selected['count'] = ends - starts
            if self.replacements:
                selected['state'] = states[starts]
            pieces.append(selected)
            first = end
        return np.concatenate(pieces)

    def _encode(self, runs):
        if self.magic == HK3P and self.version == 2:
            return runs.astype(RUN, copy=False).tobytes()
        positions = runs['start'].astype(np.int64)
        x, yz = np.divmod(positions, self.plane)
        y, z = np.divmod(yz, self.depth)
        if self.magic == W01A:
            return ((x.astype(np.uint64) << 36) | (y.astype(np.uint64) << 26)
                | (z.astype(np.uint64) << 16) | runs['state']).astype('>u8').tobytes()
        native = np.empty(len(runs), dtype=WONDER if self.magic == HK3W else POINT)
        if self.magic == HK3W:
            native['x'], native['y'], native['z'] = x, y, z
            native['count'] = runs['count']
        else:
            native['start'] = positions
            native['entity_bytes'] = runs['entity_bytes']
        native['state'] = runs['state']
        return native.tobytes()

    def write(self, target):
        body_path = self.work_dir / 'hollow.body'
        run_count = 0
        self.counts_after.fill(0)
        with body_path.open('wb') as body:
            for runs, entity in self._records():
                kept = self._filter(runs)
                run_count += len(kept)
                self.counts_after += np.bincount(kept['state'], weights=kept['count'],
                    minlength=len(self.palette)).astype(np.int64)
                body.write(self._encode(kept))
                body.write(entity)
        self.count_after = int(self.counts_after.sum())
        header = self.header.copy()
        header[8] = self.count_after
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as output:
            output.write(struct.pack('>9i', *header))
            if self.magic == HK3W:
                output.write(struct.pack('>i', run_count))
            output.write(self._palette_bytes())
            with body_path.open('rb') as body:
                shutil.copyfileobj(body, output, 1024 * 1024)
        digest = hashlib.sha256()
        with target.open('rb') as source:
            for block in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(block)
        return dict(before=self.count_before, after=self.count_after,
            removed=self.count_before - self.count_after, runs=run_count,
            entities=self.entity_count, falling_supports_kept=self.falling_supports_kept,
            unsupported_falling_replaced=len(self.replacements), bytes=target.stat().st_size, sha256=digest.hexdigest())
