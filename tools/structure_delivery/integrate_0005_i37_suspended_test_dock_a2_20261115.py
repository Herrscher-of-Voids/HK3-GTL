from datetime import datetime, timedelta, timezone
from pathlib import Path
import gzip
import hashlib
import json
import mmap
import shutil
import struct
import zipfile

import numpy as np

import build_late_approved_resources_20261026 as nbt
from build_batch10_approved_resources_20261030 import FIXED, header


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_I37_世界维系试验平台_悬箱稳界试验坞_A2_20261115'
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/0005-i37-a2-runtime-20261115'
MACHINE = 'hk3gtl:i37_world_maintenance_trial_platform'
ROW = np.dtype([('pos', '>i4'), ('state', '>u2'), ('bytes', '>i4')])
RUN = struct.Struct('>iiiHi')


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def archive(manifest, now):
    target = ROOT / 'deliveries/多方块确认归档' / (now.strftime('%Y%m%d_%H%M%S_%f') + '_0005_I37_A2_外观已确认')
    target.mkdir()
    candidate_files = ['manifest.json', manifest['name'] + '.nbt', manifest['name'] + '.schem',
                       '正面预览.png', '整体预览.png', '对称回执.json', '材料清单.json', '材质来源.json']
    sources = [Path('tools/structure_delivery') / name for name in (
        'geometry_0005_i37_suspended_test_dock_a1_20261115.py',
        'geometry_0005_i37_suspended_test_dock_a2_20261115.py',
        'package_0005_i37_suspended_test_dock_a2_20261115.py', Path(__file__).name)]
    files = [(SOURCE / name, Path('candidate') / name) for name in candidate_files]
    files += [(ROOT / name, name) for name in sources]
    for source, relative in files:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    approval = dict(machine='I37', key='i37', approved_version='A2', appearance_approved=True,
                    conversation='0005', conversation_id=manifest['conversation_id'], recorded_at=now.isoformat(),
                    approval_quote='实装，然后咱们去弄W05', external_approval_is_authoritative=True,
                    scope='批准A2外观并接入仓库原生GT完整蓝图；构建、安装、成型与运行验收分别记录。',
                    source_candidate=str(SOURCE), source_manifest_approved_field_preserved=True,
                    size_xyz=manifest['size_xyz'], controller=manifest['controller'],
                    blocks=manifest['block_count'], game_verified=False,
                    source_files_sha256={str(relative).replace('\\', '/'): nbt.sha(target / relative)
                                         for _, relative in files})
    save(target / 'approval.json', approval)
    packed = target.with_suffix('.zip')
    with zipfile.ZipFile(packed, 'x', compression=zipfile.ZIP_STORED) as output:
        for path in sorted(target.rglob('*')):
            if path.is_file():
                output.write(path, path.relative_to(target))
    digest = nbt.sha(packed)
    packed.with_suffix('.zip.sha256').write_text(digest + '  ' + packed.name + '\n', 'utf8')
    for path in target.rglob('*'):
        if path.is_file():
            path.chmod(0o444)
    return target, packed, digest


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    snapshot, packed, archive_sha = archive(manifest, now)
    source = snapshot / 'candidate' / (manifest['name'] + '.nbt')
    size, controller = manifest['size_xyz'], manifest['controller']
    LOG.mkdir(parents=True, exist_ok=True)
    expanded = LOG / 'i37-source.tasktmp'
    with gzip.open(source, 'rb') as inp, expanded.open('wb') as output:
        shutil.copyfileobj(inp, output, 4 * 1024 * 1024)
    destination = RES / 'structures/compact/i37.bin.gz'
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.gz.tasktmp')
    canonical = hashlib.sha256()
    runs = emitted = replacements = 0
    with expanded.open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as raw:
        fields, blocks_start, count = header(raw)
        palette = nbt.palette(raw, fields['palette']) + [MACHINE + '[facing=north]']
        counts = np.zeros(len(palette), dtype=np.int64)
        entity = b'\x0a\x00\x00' + nbt.string_tag('id', MACHINE) + b'\x00'
        with temporary.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', compresslevel=9, mtime=0) as stream:
            stream.write(struct.pack('>9iH', 0x484b3350, 2, *size, *controller, count, len(palette)))
            for state in palette:
                encoded = state.encode('ascii')
                stream.write(struct.pack('>H', len(encoded)) + encoded)

            def emit(positions, states, tag=b''):
                nonlocal runs, emitted
                rows = np.zeros(len(positions), dtype=ROW)
                rows['pos'], rows['state'], rows['bytes'] = positions, states, len(tag)
                canonical.update(rows.tobytes())
                canonical.update(tag)
                if tag:
                    stream.write(RUN.pack(int(positions[0]), 0, 1, int(states[0]), len(tag)) + tag)
                    runs += 1
                else:
                    delta = np.diff(positions)
                    changes = np.flatnonzero((states[1:] != states[:-1]) | np.r_[False, delta[1:] != delta[:-1]]) + 1
                    for start, end in zip(np.r_[0, changes], np.r_[changes, len(positions)]):
                        length = int(end - start)
                        step = int(positions[start + 1] - positions[start]) if length > 1 else 0
                        stream.write(RUN.pack(int(positions[start]), step, length, int(states[start]), 0))
                        runs += 1
                emitted += len(positions)

            for offset in range(0, count, 65536):
                number = min(65536, count - offset)
                records = np.frombuffer(raw, dtype=FIXED, count=number, offset=blocks_start + 5 + offset * 36)
                positions, states = records['pos'].copy(), records['state'].copy()
                linear = (positions[:, 0].astype(np.int64) * size[1] + positions[:, 1]) * size[2] + positions[:, 2]
                replaced = np.flatnonzero((positions == controller).all(axis=1))
                if len(replaced):
                    at = int(replaced[0])
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
                del records
    expanded.unlink()
    temporary.replace(destination)
    material_counts = {state: int(amount) for state, amount in zip(palette[:-1], counts[:-1]) if amount}
    metadata = dict(key='i37', machine=MACHINE, approved_version='A2', target_voltage='WFV',
                    size=size, size_xyz=size, controller=controller, ports=[], blocks=emitted,
                    materials=len(material_counts), material_counts=material_counts,
                    layout_state_overrides={}, compact_records_sha256=canonical.hexdigest(),
                    compact_sha256=nbt.sha(destination), source_nbt=str(source), source_nbt_sha256=nbt.sha(source),
                    source_snapshot=str(snapshot), source_metadata=str(snapshot / 'candidate/manifest.json'),
                    approval_manifest=str(snapshot / 'approval.json'),
                    source_manifest_approved_field_preserved=True, external_approval_is_authoritative=True,
                    runtime_format='HK3P/2; original-order arithmetic runs; full entity NBT',
                    required_abilities=['item_input', 'item_output', 'fluid_input', 'fluid_output'],
                    installed_hatches={}, controller_nbt_blockentity_id=MACHINE,
                    changes=[dict(pos=controller, role='controller', **{'from':manifest['controller_marker']},
                                  to=MACHINE + '[facing=north]', block_entity_id=MACHINE)],
                    interface_policy='非主控实体位置允许合法通用接口替换；空气区仍完整检查。',
                    game_verified=False)
    save(RES / 'compact_architecture/i37.json', metadata)
    save(LOG / 'integration.json', dict(recorded_at=now.isoformat(), archive=str(snapshot),
         archive_zip=str(packed), archive_zip_sha256=archive_sha,
         compact_resource=str(destination), compact_sha256=metadata['compact_sha256'],
         blocks=emitted, runs=runs, controller_replacements=replacements,
         block_entities=1, size_xyz=size, controller=controller,
         runtime_metadata=str(RES / 'compact_architecture/i37.json'),
         runtime_metadata_sha256=nbt.sha(RES / 'compact_architecture/i37.json'),
         source_manifest_sha256=nbt.sha(SOURCE / 'manifest.json'),
         jar_built=False, installed=False, game_started=False, game_verified=False,
         automated_tests_run=False, acceptance_score_changed=False))
    print(json.dumps(dict(blocks=emitted, runs=runs, controller_replacements=replacements,
                          compact_bytes=destination.stat().st_size, archive=str(snapshot)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
