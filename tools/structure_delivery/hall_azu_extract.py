"""读取用户原始Anvil存档；不启动游戏，不修改压缩包或存档。

去背景口径只排除超平坦生成设置明确的对应高度/方块；其余全部保留。
"""
import gzip
import hashlib
import io
import json
import math
import re
import struct
import time
import zipfile
import zlib
from collections import Counter
from pathlib import Path

import nbtlib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/Users/OWNER/下載/永恒的礼堂_Azu.zip')
OUT = ROOT / 'output/hall-azu-analysis'
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}


def parse_nbt(raw):
    return nbtlib.File.parse(io.BytesIO(raw))


def state_string(item):
    name = str(item['Name'])
    props = item.get('Properties', {})
    return name + ('[' + ','.join(f'{key}={props[key]}' for key in sorted(props)) + ']' if props else '')


def decode_section(data, count):
    if count == 1:
        return np.zeros(4096, dtype=np.uint16)
    bits = max(4, (count - 1).bit_length())
    per_long = 64 // bits
    words = np.asarray(data, dtype=np.int64).view(np.uint64)
    assert len(words) == math.ceil(4096 / per_long), (len(words), count, bits)
    shifts = np.arange(per_long, dtype=np.uint64) * np.uint64(bits)
    values = ((words[:, None] >> shifts) & np.uint64((1 << bits) - 1)).reshape(-1)[:4096].astype(np.uint16)
    assert int(values.max()) < count
    return values


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.time()
    palette, lookup, counts, background_counts, heights = [], {}, Counter(), Counter(), Counter()
    positions, states = [], []
    chunks = sections = entities = invalid = 0
    gross = Counter()
    ix = np.arange(4096)
    local = np.stack([ix % 16, ix // 256, (ix // 16) % 16], axis=1).astype(np.int32)
    with zipfile.ZipFile(SOURCE) as archive:
        infos = archive.infolist()
        level_info = next(row for row in infos if row.filename.endswith('/level.dat'))
        level = parse_nbt(gzip.decompress(archive.read(level_info)))['Data']
        settings = level['WorldGenSettings']['dimensions']['minecraft:overworld']['generator']['settings']
        assert str(level['WorldGenSettings']['dimensions']['minecraft:overworld']['generator']['type']) == 'minecraft:flat'
        background_by_y = {}
        y = -64
        for layer in settings['layers']:
            for _ in range(int(layer['height'])):
                background_by_y[y] = str(layer['block'])
                y += 1
        regions = [row for row in infos if re.search(r'/region/r\.-?\d+\.-?\d+\.mca$', row.filename) and row.file_size]
        for region_number, region in enumerate(regions):
            data = archive.read(region)
            for index in range(1024):
                at = int.from_bytes(data[index * 4:index * 4 + 3], 'big') * 4096
                if not at:
                    continue
                length = struct.unpack_from('>I', data, at)[0]
                compression = data[at + 4]
                raw = data[at + 5:at + 4 + length]
                assert compression in [1, 2, 3], compression
                raw = gzip.decompress(raw) if compression == 1 else zlib.decompress(raw) if compression == 2 else raw
                chunk = parse_nbt(raw)
                cx, cz = int(chunk['xPos']), int(chunk['zPos'])
                chunks += 1
                entities += len(chunk.get('block_entities', []))
                for section in chunk.get('sections', []):
                    block_states = section.get('block_states')
                    if not block_states:
                        continue
                    block_palette = [state_string(row) for row in block_states['palette']]
                    if all(s in AIR for s in block_palette):
                        continue
                    sy = int(section['Y'])
                    sections += 1
                    values = decode_section(block_states.get('data'), len(block_palette))
                    used, amounts = np.unique(values, return_counts=True)
                    global_ids = []
                    for state in block_palette:
                        if state not in lookup:
                            lookup[state] = len(palette)
                            palette.append(state)
                        global_ids.append(lookup[state])
                    ids = np.asarray(global_ids, dtype=np.uint16)[values]
                    keep = np.ones(4096, dtype=bool)
                    for value, count in zip(used.tolist(), amounts.tolist()):
                        state = block_palette[value]
                        if state in AIR:
                            keep[values == value] = False
                            continue
                        gross[state] += count
                        block = state.split('[', 1)[0]
                        for wy in range(sy * 16, sy * 16 + 16):
                            if background_by_y.get(wy) == block:
                                # 数据中水的level=0亦按生成背景；不同状态水不自动去除。
                                if block == 'minecraft:water' and state != 'minecraft:water[level=0]':
                                    continue
                                mask = (values == value) & (local[:, 1] == wy - sy * 16)
                                background_counts[state] += int(mask.sum())
                                keep[mask] = False
                    if not keep.any():
                        continue
                    point = local[keep] + np.array([cx * 16, sy * 16, cz * 16], dtype=np.int32)
                    kept = ids[keep]
                    positions.append(point)
                    states.append(kept)
                    unique, amounts = np.unique(kept, return_counts=True)
                    counts.update({palette[int(k)]: int(n) for k, n in zip(unique, amounts)})
                    unique, amounts = np.unique(point[:, 1], return_counts=True)
                    heights.update({int(k): int(n) for k, n in zip(unique, amounts)})
            if region_number % 8 == 0:
                print(json.dumps({'region': region_number + 1, 'of': len(regions), 'chunks': chunks, 'retained_blocks': sum(counts.values()), 'seconds': round(time.time() - start, 1)}), flush=True)
    position = np.concatenate(positions) if positions else np.empty((0, 3), dtype=np.int32)
    state = np.concatenate(states) if states else np.empty(0, dtype=np.uint16)
    used_ids = np.unique(state)
    remap = np.zeros(len(palette), dtype=np.uint16)
    remap[used_ids] = np.arange(len(used_ids), dtype=np.uint16)
    palette = [palette[int(i)] for i in used_ids]
    state = remap[state]
    assert len(position) == len(state) == sum(counts.values())
    assert sum(gross.values()) - sum(background_counts.values()) == len(state)
    np.savez_compressed(OUT / 'scene.npz', positions=position, states=state)
    (OUT / 'palette.json').write_text(json.dumps(palette, ensure_ascii=False, indent=2), encoding='utf-8')
    block_counts = Counter()
    for item, count in counts.items():
        block_counts[item.split('[', 1)[0]] += count
    report = {
        'source': str(SOURCE), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'source_kind': 'Minecraft Java Anvil world', 'minecraft_version': str(level['Version']['Name']),
        'data_version': int(level['DataVersion']), 'archive_entries': len(infos),
        'projection_files': [], 'nonempty_region_files': len(regions), 'chunks_read': chunks,
        'non_air_sections': sections, 'block_entities_in_saved_chunks': entities,
        'saved_world_non_air_blocks': sum(gross.values()), 'excluded_background_blocks': sum(background_counts.values()),
        'retained_blocks': len(state), 'block_types': len(block_counts), 'block_states': len(counts),
        'bounds_min_xyz': position.min(axis=0).tolist(), 'bounds_max_xyz': position.max(axis=0).tolist(),
        'size_xyz': (position.max(axis=0) - position.min(axis=0) + 1).tolist(),
        'background_by_y': background_by_y, 'excluded_background_counts': dict(background_counts),
        'counts_by_state': dict(counts.most_common()), 'counts_by_block': dict(block_counts.most_common()),
        'counts_by_height': dict(sorted(heights.items())), 'elapsed_seconds': round(time.time() - start, 2),
        'scope': '完整读取主世界已保存区块；仅按世界生成层排除对应高度与状态的背景方块。保留集合不等于已裁定的主体/外塔边界。定位层及单塔投影未提供，不推算主体加13塔避免重复。',
    }
    (OUT / 'world-analysis.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['retained_blocks', 'block_types', 'block_states', 'size_xyz', 'elapsed_seconds']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
