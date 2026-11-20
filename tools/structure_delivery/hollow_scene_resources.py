"""同步空心蓝图的场景剖切、材料统计与动态遮罩。"""
import gzip
import io
import json
from pathlib import Path
import struct
import tempfile

import numpy as np

from .hollow_blueprint import FALLING_REPLACEMENTS


SCENES = {
    'w03': 'w03_c9', 'w05': 'w05_r3', 'w06': 'w06_author', 'w07': 'w07_n2',
    'w08': 'w08_a5', 'w10': 'w10_a3', 'w11': 'w11_f5', 'w12': 'w12_a3',
    'w13': 'w13_t2_m1', 'w14': 'w14_e3', 'w15': 'w15_b1',
}
MASKS = {'w03', 'w05', 'w06', 'w08', 'w10', 'w11', 'w12', 'w13'}


def scene_protected_linear(resources, key, shape):
    name = SCENES.get(key.lower())
    if name is None:
        return np.empty(0, dtype=np.int64)
    path = Path(resources) / 'assets/hk3gtl/models/scene' / (name + '_meta.json')
    if not path.exists():
        return np.empty(0, dtype=np.int64)
    data = json.loads(path.read_text('utf8'))
    offset = data['blueprint_to_export_offset_xyz']
    _, height, depth = shape
    return np.array([((block['pos'][0] + offset[0]) * height + block['pos'][1] + offset[1]) * depth
                     + block['pos'][2] + offset[2] for block in data.get('native_blocks', [])], dtype=np.int64)


class _Removed:
    def __init__(self, hollow, directory):
        width, self.height, self.depth = hollow.shape
        self.bits = np.memmap(Path(directory) / 'removed.bits', mode='w+', dtype=np.uint8,
                              shape=(width, (self.height * self.depth + 7) // 8))
        for x, mask in hollow.iter_removed_x():
            self.bits[x] = np.packbits(mask, bitorder='little')

    def at(self, x, y, z):
        linear = y * self.depth + z
        return (self.bits[x, linear >> 3] >> (linear & 7) & 1).astype(bool)

    def rectangle(self, x, y, z, width, depth):
        return self.at(np.arange(x, x + width, dtype=np.int64)[:, None], y,
                       np.arange(z, z + depth, dtype=np.int64)[None, :])

    def close(self):
        self.bits._mmap.close()


def _rectangles(material, x, z, keep):
    result, active = [], {}
    for row, cells in enumerate(keep):
        edges = np.flatnonzero(np.diff(np.pad(cells.astype(np.int8), (1, 1))))
        current = {}
        for start, end in zip(edges[::2].tolist(), edges[1::2].tolist()):
            span = (start, end)
            current[span] = active.pop(span, row)
        for (start, end), first in active.items():
            result.append([material, x + first, z + start, row - first, end - start])
        active = current
    for (start, end), first in active.items():
        result.append([material, x + first, z + start, len(keep) - first, end - start])
    return result


def _write_json(path, value):
    if path.suffix == '.gz':
        with path.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=9,
                                                  filename='', mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding='utf8') as stream:
                json.dump(value, stream, ensure_ascii=False, separators=(',', ':'))
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n', 'utf8')


def _w14_replacements(data, hollow):
    palette = data['palette']
    sources = {target: palette.index(source) for source, target in FALLING_REPLACEMENTS.items()
               if source in palette}
    ox, oy, oz = data['blueprint_to_export_offset_xyz']
    replacements = {}
    for position, state in hollow.replacements.items():
        x, yz = divmod(position, hollow.height * hollow.depth)
        y, z = divmod(yz, hollow.depth)
        target = hollow.palette[state]
        materials = sources[target], palette.index(target)
        replacements.setdefault(materials, []).append((x - ox, y - oy, z - oz))
    return replacements


def _replace_surfaces(scene, replacements):
    replaced = 0
    for part in scene['parts']:
        origin = np.array(part['origin'])
        width, height, depth = part['size']
        strides = (1, width * depth, width)
        for (source, target), points in replacements.items():
            local = np.asarray(points) - origin
            local = local[((local >= 0) & (local < (width, height, depth))).all(axis=1)]
            if not len(local):
                continue
            for face, (normal, axis, cross) in enumerate(((0, 2, 1), (0, 2, 1), (2, 0, 1),
                                                          (2, 0, 1), (1, 0, 2), (1, 0, 2))):
                planes = {}
                for point in local:
                    planes.setdefault(point[normal], []).append((point[axis], point[cross]))
                starts, lengths, spans = (part[key][source][face] for key in ('starts', 'lengths', 'spans'))
                target_starts, target_lengths, target_spans = (
                    part[key][target][face] for key in ('starts', 'lengths', 'spans'))
                retained = []
                for start, length, span in zip(starts, lengths, spans):
                    cell = (start % width, start // (width * depth), start // width % depth)
                    a, b = cell[axis], cell[cross]
                    hits = [(u - a, v - b) for u, v in planes.get(cell[normal], ())
                            if a <= u < a + length and b <= v < b + span]
                    if not hits:
                        retained.append((start, length, span))
                        continue
                    keep = np.ones((span, length), dtype=bool)
                    for u, v in hits:
                        keep[v, u] = False
                        target_starts.append(int(start + u * strides[axis] + v * strides[cross]))
                        target_lengths.append(1)
                        target_spans.append(1)
                    for _, v, u, new_span, new_length in _rectangles(source, 0, 0, keep):
                        retained.append((start + u * strides[axis] + v * strides[cross], new_length, new_span))
                    replaced += len(hits)
                starts[:], lengths[:], spans[:] = map(list, zip(*retained)) if retained else ([], [], [])
    return replaced


def _layers(scene, removed, replacements):
    data = scene['data']
    ox, oy, oz = data['blueprint_to_export_offset_xyz']
    counts = data['material_counts']
    before = sum(len(layer['rectangles']) for layer in scene['layers'])
    discarded = [0] * len(counts)
    adjusted = [0] * len(counts)
    placements = {}
    for (source, target), points in replacements.items():
        for x, y, z in points:
            placements.setdefault((y, source), []).append((x, z, target))
    for layer in scene['layers']:
        rectangles = []
        y = layer['y'] + oy
        for rectangle in layer['rectangles']:
            material, x, z, width, depth = rectangle
            mask = removed.rectangle(x + ox, y, z + oz, width, depth)
            count = int(np.count_nonzero(mask))
            discarded[material] += count
            for sx, sz, target in placements.get((layer['y'], material), ()):
                if x <= sx < x + width and z <= sz < z + depth:
                    mask[sx - x, sz - z] = True
                    rectangles.append([target, sx, sz, 1, 1])
                    adjusted[material] -= 1
                    adjusted[target] += 1
                    count += 1
            if not count:
                rectangles.append(rectangle)
            elif count < width * depth:
                rectangles.extend(_rectangles(material, x, z, ~mask))
        layer['rectangles'] = rectangles
    data['material_counts'] = [count - removed_count + change
                               for count, removed_count, change in zip(counts, discarded, adjusted)]
    return dict(rectangles_before=before,
                rectangles_after=sum(len(layer['rectangles']) for layer in scene['layers']),
                removed_by_material=discarded, replaced_blocks=sum(max(0, change) for change in adjusted),
                material_counts_before=counts,
                material_counts_after=data['material_counts'])


def _mask(path, removed):
    with gzip.open(path, 'rb') as stream:
        magic, count = struct.unpack('>II', stream.read(8))
        records = stream.read()
    kept = bytearray()
    count_after = blocks_before = blocks_after = 0
    bit_indices = np.arange(4096, dtype=np.int64)
    for at in range(count):
        record = memoryview(records)[at * 520:(at + 1) * 520]
        key = struct.unpack_from('>Q', record)[0]
        words = np.frombuffer(record[8:], dtype='>u8').astype(np.uint64)
        enabled = bit_indices[((words[bit_indices >> 6] >> (bit_indices & 63).astype(np.uint64)) & 1) != 0]
        blocks_before += len(enabled)
        x = (key >> 38) * 16 + (enabled & 15)
        y = (key & 4095) * 16 + (enabled >> 8)
        z = ((key >> 12) & 0x3ffffff) * 16 + ((enabled >> 4) & 15)
        enabled = enabled[~removed.at(x, y, z)]
        blocks_after += len(enabled)
        if not len(enabled):
            continue
        bits = np.zeros(64, dtype=np.uint64)
        np.bitwise_or.at(bits, enabled >> 6, np.uint64(1) << (enabled & 63).astype(np.uint64))
        kept.extend(record[:8])
        kept.extend(bits.astype('>u8').tobytes())
        count_after += 1
    with path.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=9,
                                              filename='', mtime=0) as stream:
        stream.write(struct.pack('>II', magic, count_after))
        stream.write(kept)
    return dict(mask_sections_before=count, mask_sections_after=count_after,
                mask_blocks_before=blocks_before, mask_blocks_after=blocks_after)


def sync_scene_resources(resources, key, hollow):
    key = key.lower()
    name = SCENES.get(key)
    if name is None:
        return dict(paths=[])
    resources = Path(resources)
    directory = resources / 'assets/hk3gtl/models/scene'
    path = directory / (name + ('.json' if key == 'w03' else '.json.gz'))
    result = dict(paths=[])
    with tempfile.TemporaryDirectory(prefix='hk3-hollow-scene-') as temporary:
        removed = _Removed(hollow, temporary)
        if key in {'w07', 'w11', 'w13', 'w14', 'w15'}:
            scene = json.loads(gzip.decompress(path.read_bytes()))
            replacements = _w14_replacements(scene['data'], hollow) if key == 'w14' else {}
            result.update(_layers(scene, removed, replacements))
            if replacements:
                result['replaced_surface_faces'] = _replace_surfaces(scene, replacements)
            _write_json(path, scene)
            result['paths'].append(path.relative_to(resources).as_posix())
            metadata = directory / (name + '_meta.json')
            data = json.loads(metadata.read_text('utf8'))
            data['material_counts'] = scene['data']['material_counts']
            _write_json(metadata, data)
            result['paths'].append(metadata.relative_to(resources).as_posix())
        if key in MASKS:
            mask = resources / 'data/hk3gtl/structures' / (name + '_mask.bin.gz')
            result.update(_mask(mask, removed))
            result['paths'].append(mask.relative_to(resources).as_posix())
        removed.close()
    return result
