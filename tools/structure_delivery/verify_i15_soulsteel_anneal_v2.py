# -*- coding: utf-8 -*-
"""只读核验 I15 V2 候选的文件同源性、接口与交付包。"""
import base64
import gzip
import hashlib
import json
import re
import zipfile

import nbtlib

from build_i07_calibration_preview import audit_geometry
from build_i15_soulsteel_anneal_v2 import ARCHIVE, INSTANCE, LOG, OUT, build
from verify_i14_press_v3 import read_structure, sponge


def main():
    data = build()
    nbt = OUT / (data['name'] + '.nbt')
    schem = OUT / (data['name'] + '.schem')
    record = json.loads((OUT / '设计与检查.json').read_text(encoding='utf-8'))
    blueprint_json = json.loads((OUT / 'blueprint.json').read_text(encoding='utf-8'))
    blueprint = {tuple(q['pos']): q['state'] for q in blueprint_json['blocks']}
    generated = {tuple(q['pos']): q['state'] for q in data['blocks']}
    assert blueprint == generated == read_structure(nbt) == sponge(schem)
    assert list(map(int, nbtlib.load(nbt)['size'])) == data['size']
    assert list(map(int, nbtlib.load(schem)['Offset'])) == [0, 0, 0]
    audit_geometry(data)

    audit = record['audit']
    assert record['data'] == {key: value for key, value in blueprint_json.items() if key != 'blocks'}
    assert audit['instance'] == str(INSTANCE)
    assert audit['size_baseline']['passed']
    assert audit['design_markers'] == {
        'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
    assert audit['hashes'] == {
        'nbt': hashlib.sha256(nbt.read_bytes()).hexdigest(),
        'schem': hashlib.sha256(schem.read_bytes()).hexdigest()}

    encoded = json.loads((OUT / 'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    assert payload['data'] == record['data'] and payload['audit'] == audit
    assert all(material['complete_cube'] for material in payload['materials'])
    assert sum(map(len, payload['groups'])) == len(blueprint)

    x, y, z = data['controller']
    assert data['core_marker'] == data['controller']
    assert blueprint[x, y, z] == 'minecraft:diamond_block'
    assert all(blueprint[x + dx, y + dy, z] == 'gtceu:clean_machine_casing'
               for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0))
    assert data['visual_core'] == [26, 30, 35]
    for page in OUT.glob('*.html'):
        for href in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding='utf-8')):
            if not href.startswith(('http:', 'https:', '#', 'data:')):
                assert (page.parent / href).is_file(), href

    archive = OUT / ARCHIVE
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(name) == (OUT / name).read_bytes() for name in bundle.namelist())
    result = {
        'passed': True,
        'nbt_schem_blueprint_build_equal': True,
        'blocks': len(blueprint),
        'size_xyz': data['size'],
        'size_baseline': audit['size_baseline'],
        'materials_full_cube': len(payload['materials']),
        'controller': data['controller'],
        'visual_core': data['visual_core'],
        'ports': len(data['ports']),
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'archive_bytes': archive.stat().st_size,
        'status': 'V2外观候选；未批准、未接入正式Pattern或游戏验收',
    }
    LOG.mkdir(exist_ok=True)
    (LOG / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
