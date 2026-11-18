# -*- coding: utf-8 -*-
"""只读核验I14 V4文件同源性、冲程净空与维护道；不执行游戏验收。
变更#1 2026-10-15 10:33:00：新建V4导出核验，覆盖实际文件及候选构图。
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import zipfile

import nbtlib
from i14_press_v4 import build
from build_i14_press_v4 import OUT, LOG, ARCHIVE, INSTANCE
from build_i07_calibration_preview import audit_geometry
from verify_i14_press_v3 import read_structure, sponge


def main():
    data = build()
    p = OUT/(data['name']+'.nbt')
    s = OUT/(data['name']+'.schem')
    blueprint = json.loads((OUT/'blueprint.json').read_text(encoding='utf-8'))
    blocks = {tuple(q['pos']): q['state'] for q in blueprint['blocks']}
    assert blocks == read_structure(p) == sponge(s) == {tuple(q['pos']): q['state'] for q in data['blocks']}
    assert list(map(int, nbtlib.load(p)['size'])) == data['size']
    assert list(map(int, nbtlib.load(s)['Offset'])) == [-v for v in data['controller']]
    audit_geometry(data)
    record = json.loads((OUT/'设计与检查.json').read_text(encoding='utf-8'))
    a = record['audit']
    assert a['size_baseline']['passed'] and a['instance'] == str(INSTANCE)
    assert a['design_markers'] == {'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
    assert a['hashes'] == {'nbt': hashlib.sha256(p.read_bytes()).hexdigest(), 'schem': hashlib.sha256(s.read_bytes()).hexdigest()}
    encoded = json.loads((OUT/'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    assert payload['data'] == record['data'] and payload['audit'] == a
    assert all(q['complete_cube'] for q in payload['materials'])
    assert sum(map(len, payload['groups'])) == len(blocks)
    for path in data['paths']:
        lo, hi = path['min'], path['max']
        assert all((x, lo[1]-1, z) in blocks
                   for x in range(lo[0], hi[0]+1) for z in range(lo[2], hi[2]+1))
    gap = data['geometry_contract']['open_stroke']
    lo, hi = gap['min'], gap['max']
    assert all((x, y, z) not in blocks for x in range(lo[0], hi[0]+1)
               for y in range(lo[1], hi[1]+1) for z in range(lo[2], hi[2]+1))
    x, y, z = data['controller']
    assert blocks[x, y, z] == 'minecraft:diamond_block'
    assert all(blocks[x+dx, y+dy, z] == 'gtceu:clean_machine_casing'
               for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0))
    for page in OUT.glob('*.html'):
        for href in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding='utf-8')):
            if not href.startswith(('http:', 'https:', '#', 'data:')):
                assert (page.parent/href).is_file(), href
    archive = OUT/ARCHIVE
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and all(z.read(n) == (OUT/n).read_bytes() for n in z.namelist())
    result = {'passed': True, 'nbt_schem_blueprint_equal': True, 'blocks': len(blocks),
              'size_baseline': a['size_baseline'], 'materials_full_cube': len(payload['materials']),
              'ports': len(data['ports']), 'stroke_clear': True, 'paths_clear_and_grounded': True,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'archive_bytes': archive.stat().st_size,
              'status': 'V4外观候选；未批准、未接入正式Pattern或游戏验收'}
    LOG.mkdir(exist_ok=True)
    (LOG/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
