"""恢复当前工业与研究结构表皮，历史批准交付保持不动。"""
from collections import Counter
import gzip
import hashlib
import json
import mmap
from pathlib import Path
import re
import shutil
import struct
import sys

import numpy as np
import build_late_approved_resources_20261026 as nbt

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
LOG = ROOT / 'logs/default-port-removal-20261113'
PORT = 'hk3gtl:industrial_port_casing'
FIELDS = ('surface_state', 'replaced_surface_state', 'replaced_state', 'new_position_replaced_state')
CELL = re.compile(rb'\{"pos":\[([0-9]+),([0-9]+),([0-9]+)\],"state":"([^"]+)"\}')
ROW = np.dtype([('pos', '>i4'), ('state', '>u2'), ('bytes', '>i4')])


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def value(mapped, key):
    at = mapped.find(('"' + key + '"').encode())
    if at < 0:
        return None
    at = mapped.find(b':', at) + 1
    return json.JSONDecoder().raw_decode(mapped[at:at + 2_000_000].decode('utf8').lstrip())[0]


def current_path(text):
    return ROOT / text.replace('\\', '/').split('HK3GTL/')[-1]


def recorded_surfaces(data, result):
    if isinstance(data, dict):
        if 'pos' in data:
            for field in FIELDS:
                state = data.get(field)
                if state and state not in (PORT, 'minecraft:diamond_block'):
                    result[tuple(data['pos'])] = (state, field)
        for item in data.values():
            recorded_surfaces(item, result)
    elif isinstance(data, list):
        for item in data:
            recorded_surfaces(item, result)


def cell(mapped, pos, near=None):
    needle = ('{"pos":[' + ','.join(map(str, pos)) + '],"state":"').encode()
    at = mapped.find(needle, max(0, near - 400_000), near + 400_000) if near is not None else mapped.find(needle)
    if at < 0:
        return None
    match = CELL.match(mapped, at)
    return match[4].decode('ascii'), match.start(4), match.end(4), at


def plan(key):
    path = RES / 'approved_architecture' / (key + '.json')
    meta = json.loads((RES / 'structures/approved' / (key + '.json')).read_text('utf8'))
    records = {}
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
        ports = value(mapped, 'ports')
        approved = value(mapped, 'approved_source') or {}
        source_path = ROOT / approved['blueprint'] if 'blueprint' in approved else current_path(meta['source_metadata'])
        with source_path.open('rb') as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as source_map:
            for field in ('ports', 'integration_revision', 'integration_revision_history', 'filter_port_revision'):
                recorded_surfaces(value(source_map, field), records)
        changes = []
        for port in ports:
            pos = tuple(port['pos'])
            before, _, _, at = cell(mapped, pos)
            if pos in records:
                state, field = records[pos]
                evidence = {'kind': 'recorded_surface', 'source': source_path.relative_to(ROOT).as_posix(), 'field': field}
            else:
                tangent = (2, 1) if port['face'] in ('west', 'east') else (0, 1)
                support = []
                for axis in tangent:
                    for delta in (-1, 1):
                        q = list(pos); q[axis] += delta
                        found = cell(mapped, q, at)
                        if found and found[0] != PORT and found[0].split('[')[0] != meta['machine']:
                            support.append({'pos': q, 'state': found[0]})
                counts = Counter(item['state'] for item in support)
                state = counts.most_common(1)[0][0]
                evidence = {'kind': 'matching_adjacent_surface', 'supports': support}
            changes.append({'id': port['id'], 'pos': list(pos), 'from': before, 'to': state, 'evidence': evidence})
    return {'key': key, 'changes': changes}


def backup(path):
    target = LOG / 'before' / path.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(path, target)


def rewrite(path, edits):
    temporary = path.with_suffix(path.suffix + '.ports.tmp')
    with path.open('rb') as source, mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as mapped, temporary.open('wb') as out:
        previous = 0
        for start, end, replacement in sorted(edits):
            while previous < start:
                following = min(start, previous + 1024 * 1024)
                out.write(mapped[previous:following]); previous = following
            out.write(replacement); previous = end
        while previous < len(mapped):
            following = min(len(mapped), previous + 1024 * 1024)
            out.write(mapped[previous:following]); previous = following
    temporary.replace(path)


def layout(record):
    path = RES / 'approved_architecture' / (record['key'] + '.json')
    backup(path)
    edits = []
    with path.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
        for change in record['changes']:
            _, start, end, _ = cell(mapped, change['pos'])
            edits.append((start, end, change['to'].encode()))
        at = mapped.find(b'"ports"'); start = mapped.find(b'[', at)
        ports = value(mapped, 'ports')
        text = mapped[start:start + 2_000_000].decode('utf8')
        _, consumed = json.JSONDecoder().raw_decode(text)
        end = start + len(text[:consumed].encode('utf8'))
        edits.append((start, end, b'[]'))
    rewrite(path, edits)
    return path


def patch_nbt(record):
    path = RES / 'structures/approved' / (record['key'] + '.nbt')
    backup(path)
    raw = bytearray(gzip.decompress(path.read_bytes()))
    start = raw.find(b'\x09\x00\x07palette') + 10
    end = nbt.skip(raw, start, 9)
    palette = nbt.palette(raw, (start, end))
    removals = []
    for change in record['changes']:
        if change['to'] not in palette:
            palette.append(change['to'])
        target = b'\x09\x00\x03pos\x03\x00\x00\x00\x03' + struct.pack('>3i', *change['pos'])
        at = raw.find(target)
        _, _, _, _, state_at, entity = nbt.block(raw, at)
        struct.pack_into('>i', raw, state_at, palette.index(change['to']))
        if entity is not None:
            removals.append((entity - 6, nbt.skip(raw, entity, 10), b''))
    replacements = [(start, end, b'\x0a' + struct.pack('>i', len(palette)) + b''.join(nbt.palette_tag(state) for state in palette)), *removals]
    with path.open('wb') as out, gzip.GzipFile(fileobj=out, mode='wb', compresslevel=6, mtime=0) as zipped:
        previous = 0
        for at, stop, data in sorted(replacements):
            zipped.write(memoryview(raw)[previous:at]); zipped.write(data); previous = stop
        zipped.write(memoryview(raw)[previous:])


def patch_preview(record):
    path = RES / 'structures/approved_preview' / (record['key'] + '.bin.gz')
    if not path.exists():
        return
    backup(path)
    raw = bytearray(gzip.decompress(path.read_bytes()))
    header = list(struct.unpack_from('>9iH', raw)); at = 38; palette = []
    for _ in range(header[-1]):
        length = struct.unpack_from('>H', raw, at)[0]; at += 2
        palette.append(bytes(raw[at:at + length]).decode('ascii')); at += length
    changes = {(item['pos'][0] * header[3] + item['pos'][1]) * header[4] + item['pos'][2]: item['to'] for item in record['changes']}
    for state in changes.values():
        if state not in palette:
            palette.append(state)
    edits = []; remaining = header[-2]
    while remaining:
        count = min(65536, remaining, (len(raw) - at) // 10)
        rows = np.frombuffer(raw, ROW, count=count, offset=at)
        entities = np.flatnonzero(rows['bytes'])
        plain = int(entities[0]) if len(entities) else count
        if plain:
            for pos in changes.keys() & set(map(int, rows['pos'][:plain])):
                index = int(np.flatnonzero(rows['pos'][:plain] == pos)[0])
                rows['state'][index] = palette.index(changes[pos])
            at += plain * 10; remaining -= plain
        else:
            pos, _, length = struct.unpack_from('>iHi', raw, at)
            if pos in changes:
                struct.pack_into('>H', raw, at + 4, palette.index(changes[pos]))
                struct.pack_into('>i', raw, at + 6, 0)
                edits.append((at + 10, at + 10 + length))
            at += 10 + length; remaining -= 1
    header[-1] = len(palette)
    with path.open('wb') as out, gzip.GzipFile(fileobj=out, mode='wb', compresslevel=6, mtime=0) as zipped:
        zipped.write(struct.pack('>9iH', *header))
        for state in palette:
            text = state.encode('ascii'); zipped.write(struct.pack('>H', len(text)) + text)
        cursor = 38
        for _ in range(struct.unpack_from('>H', raw, 36)[0]):
            length = struct.unpack_from('>H', raw, cursor)[0]; cursor += 2 + length
        for start, end in edits:
            zipped.write(memoryview(raw)[cursor:start]); cursor = end
        zipped.write(memoryview(raw)[cursor:])


def apply(record):
    path = layout(record)
    patch_nbt(record)
    patch_preview(record)
    meta_path = RES / 'structures/approved' / (record['key'] + '.json')
    backup(meta_path)
    meta = json.loads(meta_path.read_text('utf8'))
    meta.update(ports=[], installed_hatches={}, sha256=sha(path), template_sha256=sha(meta_path.with_suffix('.nbt')),
                default_ports_removed='2026-11-13', default_surface_restoration=record['changes'],
                port_positions_faces_purposes_preserved=False,
                geometry_changes='旧接口格恢复建筑表面；默认蓝图不预放工业接口或实际仓室')
    if 'template_ports' in meta:
        meta['template_ports'] = '无固定接口；实体非主控格由玩家选择合法通用接口'
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', 'utf8')
    archive = ROOT / 'source_archives/approved_architecture' / (record['key'] + '.json.gz')
    backup(archive)
    with path.open('rb') as source, archive.open('wb') as out, gzip.GzipFile(fileobj=out, mode='wb', compresslevel=6, mtime=0) as zipped:
        shutil.copyfileobj(source, zipped, length=1024 * 1024)
    return {'key': record['key'], 'restored': len(record['changes']), 'sha256': sha(path), 'archive_sha256': sha(archive),
            'bytes': path.stat().st_size, 'archive_bytes': archive.stat().st_size}


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    plan_path = LOG / 'restoration-plan.json'
    if sys.argv[1:2] == ['--plan']:
        records = []
        for path in sorted((RES / 'approved_architecture').glob('*.json')):
            record = plan(path.stem); records.append(record)
            print(path.stem, len(record['changes']), flush=True)
        plan_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', 'utf8')
        print(json.dumps({'structures': len(records), 'positions': sum(len(item['changes']) for item in records),
                          'evidence': dict(Counter(change['evidence']['kind'] for item in records for change in item['changes']))}))
        return
    records = json.loads(plan_path.read_text('utf8'))
    manifest_path = ROOT / 'source_archives/approved_architecture/manifest.json'
    backup(manifest_path)
    manifest = json.loads(manifest_path.read_text('utf8')); results = []
    for record in records:
        result = apply(record); results.append(result)
        entry = next(item for item in manifest['files'] if Path(item['path']).stem == result['key'])
        entry.update({key: result[key] for key in ('sha256', 'archive_sha256', 'bytes', 'archive_bytes')})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
        (LOG / 'applied.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', 'utf8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
