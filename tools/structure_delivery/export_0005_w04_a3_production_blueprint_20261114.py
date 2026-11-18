"""将0005的W04 A3静态整机流式转为生产蓝图，仅替换主控格。"""
from datetime import datetime
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import struct

import numpy as np

from i34_open_observatory_export_20261027 import _headers


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W04_七雷取能天枢_构图A3_20261114'
LOG = ROOT / 'logs/0005-w04-a3-game-20261114'
DESTINATION = ROOT / 'src/main/resources/data/hk3gtl/structures/w04_candidate.bin.gz'
CONTROLLER = 'hk3gtl:w04_thunder_superconducting_axis[facing=south]'
RECORD = np.dtype([('position', '>i4'), ('step', '>i4'), ('length', '>i4'),
                   ('state', '>u2'), ('entity', '>i4')])


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def export():
    LOG.mkdir(parents=True, exist_ok=True)
    backup = LOG / ('w04_candidate.before-a3.' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.bin.gz')
    shutil.copy2(DESTINATION, backup)
    manifest_path = SOURCE / 'manifest.json'
    meta = json.loads(manifest_path.read_text('utf8'))
    source = SOURCE / (meta['name'] + '.schem')
    w, h, d = meta['actual_scene_size_xyz']
    palette = ['minecraft:air'] + meta['materials']['states']
    header = _headers(palette[1:], (h, d, w), meta['block_count'])[1]
    positions, states = [], []
    with gzip.open(source, 'rb') as handle:
        if handle.read(len(header)) != header:
            raise ValueError('A3 Schematic头与清单不一致')
        offset = 0
        # A3调色板共14项，BlockData每格恰好一个字节。
        while offset < w * h * d:
            chunk = handle.read(min(4 * 1024 * 1024, w * h * d - offset))
            cells = np.frombuffer(chunk, dtype=np.uint8)
            index = np.flatnonzero(cells).astype(np.uint32)
            states.append(cells[index])
            index += offset
            positions.append((index % w * h + index // (w * d)) * d + (index // w) % d)
            offset += len(chunk)
    positions = np.concatenate(positions)
    states = np.concatenate(states)
    order = np.argsort(positions)
    positions = positions[order]
    states = states[order]
    del order
    cx, cy, cz = (np.array(meta['controller_world']) + meta['blueprint_to_export_offset_xyz']).tolist()
    controller_index = int(np.searchsorted(positions, (cx * h + cy) * d + cz))
    previous_controller_state = palette[int(states[controller_index])]
    states[controller_index] = len(palette)
    palette.append(CONTROLLER)
    count = len(positions)
    cuts = np.r_[0, np.flatnonzero((positions[1:] != positions[:-1] + 1)
                                  | (states[1:] != states[:-1])
                                  | (positions[1:] % d == 0)) + 1, count]
    runs = np.empty(len(cuts) - 1, dtype=RECORD)
    runs['position'] = positions[cuts[:-1]]
    runs['step'] = 1
    runs['length'] = np.diff(cuts)
    runs['state'] = states[cuts[:-1]]
    runs['entity'] = 0
    output_path = LOG / 'w04_candidate.a3.bin.gz'
    with output_path.open('wb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=9, mtime=0) as output:
            output.write(struct.pack('>9iH', 0x484b3350, 2, w, h, d, cx, cy, cz, count, len(palette)))
            for state in palette:
                value = state.encode('utf8')
                output.write(struct.pack('>H', len(value)) + value)
            for start in range(0, len(runs), 65536):
                output.write(runs[start:start + 65536].tobytes())
    shutil.copy2(output_path, DESTINATION)
    receipt = {
        'conversation_id': meta['conversation_id'],
        'created_at': datetime.now().astimezone().isoformat(),
        'format': 'HK3P v2 RLE，X→Y→Z，Z行内连续游程',
        'size_xyz': [w, h, d],
        'controller_world': meta['controller_world'],
        'controller_export_xyz': [cx, cy, cz],
        'controller_previous_state': previous_controller_state,
        'controller_state': CONTROLLER,
        'block_count': count,
        'rle_record_count': len(runs),
        'palette': palette,
        'source_manifest': str(manifest_path.relative_to(ROOT)),
        'source_manifest_sha256': digest(manifest_path),
        'source_schematic': str(source.relative_to(ROOT)),
        'source_schematic_sha256': digest(source),
        'backup': str(backup.relative_to(ROOT)),
        'backup_sha256': digest(backup),
        'destination': str(DESTINATION.relative_to(ROOT)),
        'destination_bytes': DESTINATION.stat().st_size,
        'destination_sha256': digest(DESTINATION),
        'exporter_sha256': digest(Path(__file__)),
        'game_verified': False,
    }
    (LOG / 'blueprint-export.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(receipt, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    export()
