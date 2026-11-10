# -*- coding: utf-8 -*-
"""回读五阶研究所，核验四次原地扩建、真实导出、通道与浏览证据。"""
import argparse
import datetime
import hashlib
import json
import re
import zipfile
import nbtlib
from build_research_campus_additive_v1 import OUT, LOG, KEYS, ZIP_NAME, save_record, bundle, copy_generators
from research_campus_common_v1 import validate
from check_i01_upgrade import read_structure, check_upgrade


def sponge_blocks(path):
    root = nbtlib.load(path)
    assert root.root_name == 'Schematic' and int(root['Version']) == 2
    assert int(root['DataVersion']) == 3465 and int(root['Palette']['minecraft:air']) == 0
    w, h, d = [int(root[k]) for k in ('Width', 'Height', 'Length')]
    palette = {int(v): str(k) for k, v in root['Palette'].items()}
    encoded = bytes(int(v)&255 for v in root['BlockData'])
    values, value, shift = [], 0, 0
    for byte in encoded:
        value |= (byte&127) << shift
        if byte&128:
            shift += 7
            assert shift <= 28
        else:
            values.append(value)
            value, shift = 0, 0
    assert shift == 0 and len(values) == w*h*d
    blocks = {}
    for index, value in enumerate(values):
        state = palette[value]
        if state != 'minecraft:air':
            blocks[index%w, index//(w*d), index//w%d] = state
    return root, blocks


def verify(browser=False):
    entries = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    assert [e['key'] for e in entries] == KEYS
    review = json.loads((LOG/'browser-review.json').read_text(encoding='utf-8')) if browser else None
    previous, previous_blueprint, summaries, upgrades = None, None, [], []
    for e in entries:
        out = OUT/e['key']
        blueprint = json.loads((out/'blueprint.json').read_text(encoding='utf-8'))
        record = json.loads((out/'设计与检查.json').read_text(encoding='utf-8'))
        audit = record['audit']
        validate(blueprint, previous_blueprint)
        previous_blueprint = blueprint
        nbt_path, schem_path = [out/(e['name']+suffix) for suffix in ('.nbt', '.schem')]
        blocks = read_structure(nbt_path)
        assert blocks == {tuple(b['pos']): b['state'] for b in blueprint['blocks']}
        root, saved = sponge_blocks(schem_path)
        assert saved == blocks
        controller = tuple(blueprint['controller'])
        offset = tuple(map(int, root['Offset']))
        assert offset == tuple(-q for q in controller)
        assert blueprint['paste_anchor'] == list(controller)
        assert audit['hashes'] == {suffix: hashlib.sha256(path.read_bytes()).hexdigest()
            for suffix, path in (('nbt', nbt_path), ('schem', schem_path))}
        assert audit['hashes']['nbt'] == e['sha256_nbt'] and audit['size_baseline']['passed']
        assert blocks[controller] == 'minecraft:diamond_block'
        cx, cy, cz = controller
        white = [(cx+x, cy+y, cz) for x in (-1, 0, 1) for y in (-1, 0, 1) if x or y]
        assert all(blocks[p] == 'gtceu:clean_machine_casing' for p in white)
        assert audit['design_markers'] == {'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
        if previous:
            errors = check_upgrade(previous[0], previous[1], blocks, controller)
            assert not errors, errors[:5]
            old_global = {tuple(p[i]+previous[2][i] for i in range(3)): s for p, s in previous[0].items()}
            new_global = {tuple(p[i]+offset[i] for i in range(3)): s for p, s in saved.items()}
            assert all(new_global[p] == s for p, s in old_global.items() if p != (0, 0, 0))
            upgrades.append({'stage': e['key'], 'preserved_non_controller': len(previous[0])-1,
                             'removed_or_changed': 0, 'added': len(blocks)-len(previous[0]),
                             'same_schematic_anchor': True})
        previous = blocks, controller, offset
        if browser:
            evidence = review['machines'][e['key']]
            assert evidence['sha256_nbt'] == e['sha256_nbt']
            assert all(evidence[k] for k in ('loaded', 'rotation_checked', 'section_checked', 'panel_checked'))
            audit['browser_review'] = evidence
            audit['checks'].append('浏览器实际载入、正面/俯视、旋转、剖切与主控近景核对')
            audit['not_verified'] = ['待用户外观确认', '未接入正式Pattern与配方',
                                    '未进行Minecraft实际成型与运行验收', '本轮材料不限生存阶段；未声明配方可达性']
        payload = save_record(out, record)
        assert payload['audit'] == audit and payload['data'] == record['data']
        assert sum(map(len, payload['groups'])) == len(blocks)
        w, h, d = blueprint['size']
        rendered = {(index%w, index//(w*d), index//w%d): material['state']
                    for material, group in zip(payload['materials'], payload['groups']) for index in group}
        assert rendered == blocks, '预览载荷与结构坐标或状态不一致'
        assert all(m['complete_cube'] for m in payload['materials'])
        page = (out/'三维评审.html').read_text(encoding='utf-8')
        if browser:
            page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。',
                                '三维操作已检查；游戏成型与运行待验收。')
            (out/'三维评审.html').write_text(page, encoding='utf-8')
        for link in re.findall(r'(?:href|src)="([^"]+)"', page):
            if not link.startswith(('data:', 'http', '#')):
                assert (out/link).is_file(), (e['key'], link)
        height = [-60+min(p[1] for p in blocks), -60+max(p[1] for p in blocks)]
        assert height[1] <= 236
        summaries.append({'id': e['key'], 'blocks': len(blocks),
            'size_xyz': e['size'], 'controller_local': list(controller), 'schematic_offset': list(offset),
            'world_height_range': height, 'source_counts': audit['namespace_counts'], 'browser_review': browser})
    for link in re.findall(r'(?:href|src)="([^"]+)"', (OUT/'index.html').read_text(encoding='utf-8')):
        if not link.startswith(('data:', 'http', '#')):
            assert (OUT/link).is_file(), link
    copy_generators()
    bundle()
    target = OUT/ZIP_NAME
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert sum(n.endswith('.nbt') for n in archive.namelist()) == 5
        assert sum(n.endswith('.schem') for n in archive.namelist()) == 5
        for name in archive.namelist():
            assert archive.read(name) == (OUT/name).read_bytes(), name
    result = {'time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'passed': True, 'browser_review': browser, 'machines': summaries, 'upgrades': upgrades,
              'archive_bytes': target.stat().st_size, 'archive_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    (LOG/'final-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', action='store_true')
    verify(parser.parse_args().browser)
