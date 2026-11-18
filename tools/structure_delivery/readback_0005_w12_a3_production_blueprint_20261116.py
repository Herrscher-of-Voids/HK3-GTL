from datetime import datetime
import gzip
import json
from pathlib import Path
import struct

import numpy as np

from export_0005_w12_a3_production_blueprint_20261116 import BLUEPRINT, MASK, METADATA, OUT, ROOT, SCENE
from package_0005_w12_author_blueprint_20261116 import digest, save


LOG = ROOT / 'logs/0005-w12-a3-runtime-20261116'
RUN = struct.Struct('>iiiHi')


def main():
    metadata = json.loads(METADATA.read_text('utf8'))
    with gzip.open(BLUEPRINT, 'rb') as stream:
        header = struct.unpack('>9iH', stream.read(38))
        _, _, w, h, d, cx, cy, cz, declared_blocks, palette_count = header
        palette = [stream.read(struct.unpack('>H', stream.read(2))[0]).decode('utf8') for _ in range(palette_count)]
        runs, actual_blocks, controller_cells, entity_tags = 0, 0, [], []
        material_counts = [0] * palette_count
        while True:
            raw = stream.read(RUN.size)
            if not raw:
                break
            start, step, count, state, size = RUN.unpack(raw)
            tag = stream.read(size)
            runs += 1
            actual_blocks += count
            material_counts[state] += count
            if palette[state].startswith('hk3gtl:w12_global_energy_constraint_wall'):
                for index in range(count):
                    position = start + step * index
                    controller_cells.append([position // (h * d), position // d % h, position % d])
                entity_tags.append(dict(bytes=size, hex=tag.hex(), contains_blockentity_id=b'hk3gtl:w12_global_energy_constraint_wall' in tag))
    with gzip.open(MASK, 'rb') as stream:
        mask_magic, section_count = struct.unpack('>2i', stream.read(8))
        sections = np.frombuffer(stream.read(), dtype=np.dtype([('key', '>i8'), ('bits', 'u1', (512,))]))
    popcounts = np.array([bin(value).count('1') for value in range(256)], np.uint8)
    mask_blocks = int(popcounts[sections['bits']].sum())
    key = (cx >> 4) << 38 | (cz >> 4) << 12 | (cy >> 4)
    owner = sections[np.searchsorted(sections['key'], key)]
    bit = (((cy & 15) * 16 + (cz & 15)) * 16 + (cx & 15))
    word = struct.unpack_from('>Q', owner['bits'].tobytes(), (bit >> 6) * 8)[0]
    with gzip.open(SCENE, 'rt', encoding='utf8') as stream:
        scene = json.load(stream)
    rings = {part['id']: dict(axis=part['metadata']['motion_axis'], pivot=part['metadata']['pivot'],
             speed=part['metadata']['motion_speed'], normal=part['metadata']['ring_normal'])
             for part in scene['parts'] if part['id'].startswith('core_gyroscope_')}
    marker = next(i for i, material in enumerate(scene['materials']) if material['state'] == 'minecraft:redstone_block')
    receipt = dict(recorded_at=datetime.now().astimezone().isoformat(), candidate='W12 A3',
        purpose='生产交付资源读回核对', blueprint=dict(magic=hex(header[0]), version=header[1],
            size_xyz=[w, h, d], controller_xyz=[cx, cy, cz], declared_blocks=declared_blocks,
            actual_blocks=actual_blocks, runs=runs, controller_cells=controller_cells, entity_tags=entity_tags,
            material_counts={state: count for state, count in zip(palette, material_counts)}),
        mask=dict(magic=hex(mask_magic), declared_sections=section_count, actual_sections=len(sections),
            blocks=mask_blocks, controller_masked=bool(word & (1 << (bit & 63)))),
        scene=dict(parts=len(scene['parts']), controller_blueprint=scene['data']['controller_blueprint'],
            controller_export=scene['data']['controller_export'], rings=rings,
            marker_quads=sum(len(face) for part in scene['parts'] for face in part['starts'][marker]),
            quads=sum(len(face) for part in scene['parts'] for material in part['starts'] for face in material)),
        metadata=dict(appearance_approved=metadata['appearance_approved'], known_pending=metadata['known_pending']),
        sha256={str(path.relative_to(ROOT)).replace('\\', '/'): digest(path) for path in (BLUEPRINT, MASK, SCENE, METADATA)},
        automated_tests_run=False, game_verified=False)
    LOG.mkdir(parents=True, exist_ok=True)
    for directory in (OUT, LOG):
        save(directory / 'resource-readback.json', receipt)
    print(json.dumps(dict(blocks=actual_blocks, controller=controller_cells, runs=runs,
        mask_blocks=mask_blocks, controller_masked=receipt['mask']['controller_masked'],
        scene_parts=len(scene['parts']), rings=rings, marker_quads=receipt['scene']['marker_quads'])), flush=True)


if __name__ == '__main__':
    main()
