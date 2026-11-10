# -*- coding: utf-8 -*-
"""Read-only integrity checks for the I15 V4 palette revision package."""
import base64
import gzip
import hashlib
import json
import re
import zipfile
from pathlib import Path

import nbtlib

from build_i07_calibration_preview import audit_geometry
from build_i15_soulsteel_anneal_v4_palette import ARCHIVE, DIAMOND, LOG, OUT, PORT, build


def read_nbt(path):
    root = nbtlib.load(path)
    palette = []
    for row in root['palette']:
        props = row.get('Properties', {})
        suffix = '[' + ','.join(f'{key}={value}' for key, value in sorted(props.items())) + ']' if props else ''
        palette.append(str(row['Name']) + suffix)
    blocks = {tuple(map(int, row['pos'])): palette[int(row['state'])] for row in root['blocks']}
    return root, blocks


def read_sponge(path):
    root = nbtlib.load(path)
    assert root.root_name == 'Schematic' and int(root['Version']) == 2
    assert int(root['DataVersion']) == 3465
    width, height, length = [int(root[key]) for key in ('Width', 'Height', 'Length')]
    palette = {int(index): str(state) for state, index in root['Palette'].items()}
    raw = bytes(int(value) & 255 for value in root['BlockData'])
    values, value, shift = [], 0, 0
    for byte in raw:
        value |= (byte & 127) << shift
        if byte & 128:
            shift += 7
        else:
            values.append(value)
            value = shift = 0
    assert len(values) == width * height * length and shift == 0
    return {(i % width, i // (width * length), i // width % length): palette[state]
            for i, state in enumerate(values) if palette[state] != 'minecraft:air'}


def main():
    data = build()
    nbt_path = OUT / (data['name'] + '.nbt')
    schem_path = OUT / (data['name'] + '.schem')
    nbt_root, nbt_blocks = read_nbt(nbt_path)
    schem_blocks = read_sponge(schem_path)
    blueprint_record = json.loads((OUT / 'blueprint.json').read_text(encoding='utf-8'))
    blueprint = {tuple(row['pos']): row['state'] for row in blueprint_record['blocks']}
    generated = {tuple(row['pos']): row['state'] for row in data['blocks']}
    assert nbt_blocks == schem_blocks == blueprint == generated
    assert list(map(int, nbt_root['size'])) == data['size']
    assert list(map(int, nbtlib.load(schem_path)['Offset'])) == [0, 0, 0]
    size_audit = audit_geometry(data)
    assert size_audit['passed'] and size_audit['actual_xyz'] == data['size']

    counts = {}
    for state in generated.values():
        counts[state] = counts.get(state, 0) + 1
    assert counts[DIAMOND] == 1 and counts[PORT] == 6
    for x, y, z in (tuple(row['pos']) for row in data['ports']):
        assert generated[x, y, z] == PORT
        assert (x, y, z + 1) in generated and (x, y - 1, z) in generated
        assert (x, y, z - 1) not in generated
    cx, cy, cz = data['controller']
    assert generated[cx, cy, cz] == DIAMOND
    assert all(generated[cx + dx, cy + dy, cz] == 'gtceu:clean_machine_casing'
               for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    assert (cx, cy, cz - 1) not in generated

    record = json.loads((OUT / '设计与检查.json').read_text(encoding='utf-8'))
    audit = record['audit']
    assert audit['size_baseline'] == size_audit
    assert audit['design_markers'] == {DIAMOND: 1, PORT: 6}
    assert audit['hashes'] == {
        'nbt': hashlib.sha256(nbt_path.read_bytes()).hexdigest(),
        'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest(),
    }
    materials = json.loads((OUT / '材料依据.json').read_text(encoding='utf-8'))['materials']
    assert all(row['complete_cube'] for row in materials)
    encoded = json.loads((OUT / 'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    assert payload['audit'] == audit and payload['data'] == record['data']
    assert all(row['complete_cube'] for row in payload['materials'])
    assert sum(map(len, payload['groups'])) == len(generated)

    for page in OUT.glob('*.html'):
        for link in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding='utf-8')):
            if not link.startswith(('http:', 'https:', '#', 'data:')):
                assert (page.parent / link).is_file(), f'{page.name}: {link}'
    pack_check = json.loads((OUT / '2.8实例与崩溃复核.json').read_text(encoding='utf-8'))
    assert pack_check['manifest_version'] == '2.8'
    assert not pack_check['missing_manifest_jars']

    archive_path = OUT / ARCHIVE
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert all(archive.read(name) == (OUT / name).read_bytes() for name in archive.namelist())
    result = {
        'passed': True,
        'nbt_schematic_blueprint_build_equal': True,
        'size_xyz': data['size'], 'actual_xyz': size_audit['actual_xyz'],
        'blocks': len(generated), 'materials_full_cube': len(materials),
        'zones': len(data['zones']), 'ports': len(data['ports']),
        'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'archive_bytes': archive_path.stat().st_size,
        'local_page_links': 'passed',
        'status': 'V4 配色修订候选；几何沿用已批准 V3，未批准、未部署、未接入正式 Pattern 或游戏验收',
    }
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
