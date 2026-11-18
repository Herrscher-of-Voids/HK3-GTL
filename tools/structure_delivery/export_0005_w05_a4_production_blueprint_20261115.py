"""将已批准W05 A4完整NBT接入生产蓝图，仅替换主控标记。"""
from datetime import datetime
from pathlib import Path
import gzip
import hashlib
import json
import struct

import numpy as np

from build_late_approved_resources_20261026 import string_tag
from package_0005_i37_suspended_test_dock_a2_20261115 import headers, RECORD_DTYPE


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115'
LOG = ROOT / 'logs/0005-w05-a4-runtime-20261115'
DESTINATION = ROOT / 'src/main/resources/data/hk3gtl/structures/w05_candidate.bin.gz'
METADATA = DESTINATION.with_name('w05_approved.json')
MACHINE = 'hk3gtl:w05_ideal_fluid_circulation_array'
RUN = struct.Struct('>iiiHi')


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    manifest_path = SOURCE / 'manifest.json'
    meta = json.loads(manifest_path.read_text('utf8'))
    source = SOURCE / meta['files']['nbt']['file']
    source_sha256 = digest(source)
    if source_sha256 != meta['files']['nbt']['sha256']:
        raise ValueError('W05 A4 NBT与清单SHA256不符')
    size, controller = meta['size_xyz'], meta['controller']
    w, h, d = size
    source_palette = list(meta['material_counts'])
    palette = source_palette + [MACHINE + '[facing=south]']
    expected_header = headers(source_palette, (h, d, w), meta['block_count'])[0]
    previous_sha256 = digest(DESTINATION)
    temporary = DESTINATION.with_suffix('.gz.tasktmp')
    entity = b'\x0a\x00\x00' + string_tag('id', MACHINE) + b'\x00'
    counts = np.zeros(len(palette), dtype=np.int64)
    emitted = runs = replacements = 0
    previous_marker = ''

    with gzip.open(source, 'rb') as inp, temporary.open('wb') as output:
        if inp.read(len(expected_header)) != expected_header:
            raise ValueError('W05 A4 NBT头与清单不符')
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', compresslevel=9, mtime=0) as stream:
            stream.write(struct.pack('>9iH', 0x484b3350, 2, *size, *controller, meta['block_count'], len(palette)))
            for state in palette:
                encoded = state.encode('utf8')
                stream.write(struct.pack('>H', len(encoded)) + encoded)

            def emit(positions, states, tag=b''):
                nonlocal emitted, runs
                if tag:
                    stream.write(RUN.pack(int(positions[0]), 0, 1, int(states[0]), len(tag)) + tag)
                    runs += 1
                else:
                    delta = np.diff(positions)
                    changes = np.flatnonzero((states[1:] != states[:-1]) |
                        (delta != np.r_[delta[:1], delta[:-1]])) + 1
                    for start, end in zip(np.r_[0, changes], np.r_[changes, len(positions)]):
                        length = int(end - start)
                        step = int(positions[start + 1] - positions[start]) if length > 1 else 0
                        stream.write(RUN.pack(int(positions[start]), step, length, int(states[start]), 0))
                        runs += 1
                emitted += len(positions)

            for offset in range(0, meta['block_count'], 65536):
                number = min(65536, meta['block_count'] - offset)
                rows = np.frombuffer(inp.read(number * 36), dtype=RECORD_DTYPE)
                positions = np.column_stack([rows['x'], rows['y'], rows['z']])
                linear = (positions[:, 0].astype(np.int64) * h + positions[:, 1]) * d + positions[:, 2]
                states = rows['state'].copy()
                marker = np.flatnonzero((positions == controller).all(axis=1))
                if len(marker):
                    at = int(marker[0])
                    previous_marker = source_palette[int(states[at])]
                    states[at] = len(palette) - 1
                    if at:
                        emit(linear[:at], states[:at])
                    emit(linear[at:at + 1], states[at:at + 1], entity)
                    if at + 1 < number:
                        emit(linear[at + 1:], states[at + 1:])
                    replacements += 1
                else:
                    emit(linear, states)
                counts += np.bincount(states, minlength=len(palette))

    temporary.replace(DESTINATION)
    metadata = dict(id='W05', version='0005-A4', controller=MACHINE,
        blueprint='hk3gtl:structures/w05_candidate.bin.gz', conversation='0005',
        conversation_id=meta['conversation_id'], appearance_approved=True,
        approval_basis='负责人批准W05 A4并要求先接入游戏，再推进W06。',
        source=str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        source_manifest_sha256=digest(manifest_path), source_nbt_sha256=source_sha256,
        source_manifest_approved_field_preserved=True, external_approval_is_authoritative=True,
        size_xyz=size, size_wdh=meta['size_wdh'], controller_xyz=controller,
        source_facing='south', block_count=emitted, full_geometry=True,
        fixed_interface_positions=[], production_recipe='hk3gtl:wonder_ideal_flow_exchange_matrix',
        target_voltage='WSV', research='RN-IFF',
        interface_policy='保留既有自由通用接口规则；本蓝图不预装固定仓室。',
        material_counts={state: int(amount) for state, amount in zip(palette, counts) if amount},
        controller_previous_state=previous_marker, controller_state=palette[-1],
        controller_nbt_blockentity_id=MACHINE, controller_replacements=replacements,
        runtime_format='HK3P/2；完整NBT源顺序等差游程；主控原生方块实体NBT',
        rle_record_count=runs, blueprint_sha256=digest(DESTINATION), game_verified=False)
    save(METADATA, metadata)
    LOG.mkdir(parents=True, exist_ok=True)
    receipt = dict(recorded_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        **metadata, source_nbt=str(source.relative_to(ROOT)).replace('\\', '/'),
        destination=str(DESTINATION.relative_to(ROOT)).replace('\\', '/'),
        destination_bytes=DESTINATION.stat().st_size, previous_blueprint_sha256=previous_sha256,
        runtime_metadata=str(METADATA.relative_to(ROOT)).replace('\\', '/'),
        runtime_metadata_sha256=digest(METADATA), exporter_sha256=digest(Path(__file__)),
        jar_built=False, installed=False, game_started=False, automated_tests_run=False)
    save(LOG / 'blueprint-export.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
