# -*- coding: utf-8 -*-
"""I01–I08 新造型批次；2026-10-14 新增，旧结构和确认归档独立保留。"""
import argparse
import base64
import collections
import datetime
import gzip
import importlib
import json
import shutil
import zipfile
from pathlib import Path
import build_i07_calibration_preview as preview_package
from build_i09_i13_redesign_v6 import lodestone_export
from redesign69_geometry import ROOT
from i01_i08_v7_gallery import gallery

OUT = ROOT/'deliveries/I01-I08_重设计_V7_20261014'
LOG = ROOT/'logs/i01-i08-redesign-v7'
GENERATORS = {**{f'i01-{n}': ('i01_chain_v7', f'i01_{n}') for n in range(1, 5)},
              **{f'i0{n}': ('i02_i04_v7', f'i0{n}') for n in range(2, 5)},
              **{f'i0{n}': ('i05_i07_v7', f'i0{n}') for n in range(5, 8)},
              'i08': ('i08_v7', 'i08')}
TEST_INSTANCE = Path.home()/'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'


def build_one(key):
    module, method = GENERATORS[key]
    data = getattr(importlib.import_module(module), method)()
    assert data['key'] == key
    if not key.startswith('i01-'):
        cx, cy, cz = data['controller']
        for block in data['blocks']:
            x, y, z = block['pos']
            if z == cz and cx-3 <= x <= cx+3 and cy-2 <= y <= cy+2 and (abs(x-cx) == 3 or abs(y-cy) == 2):
                block['state'] = 'gtceu:clean_machine_casing'
    data['construction_notes'] = {'orientation': 'X向东、Y向上、Z向南；主控正面朝-Z。',
        'origin': [0, 0, 0], 'paste_anchor': data['controller'], 'recommended_bottom_world_y': -60,
        'world_height_range': [-60, -60+data['size'][1]-1], 'status': 'V7外观候选，待用户审阅。'}
    out = OUT/key
    preview_package.TEST_INSTANCE = TEST_INSTANCE
    preview_package.package(data, out, key, ['重做主体轮廓与工艺分区', '局部承台、连接管路与维护空间',
                            '正式名称保持；I09–I13确认版独立保留'])
    sha = lodestone_export(data, out, LOG)
    record = json.loads((out/'设计与检查.json').read_text(encoding='utf-8'))
    record['audit']['hashes']['nbt'] = sha
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    counts = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    ordinary = sum(counts.values())
    record['audit'].update(namespace_counts=dict(counts),
        namespace_percent={k: round(v/ordinary*100, 2) for k, v in counts.items()},
        design_markers=dict(collections.Counter(b['state'] for b in data['blocks'] if b['state'] in markers)),
        approval='待用户外观确认', reference_report='结构参考.json')
    record['audit']['checks'].append('Minecraft Builder/Lodestone重新导出NBT并逐格回读一致')
    assert record['audit']['design_markers'] == {'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
    review_file = LOG/'browser-review.json'
    if review_file.exists():
        review = json.loads(review_file.read_text(encoding='utf-8')).get('machines', {}).get(key)
        if review and review['sha256_nbt'] == sha:
            record['audit']['browser_review'] = review
            record['audit']['checks'].append('浏览器实际载入、旋转及剖切检查通过')
            record['audit']['not_verified'] = ['待用户外观确认', '未接入正式Pattern与配方',
                '未进行Minecraft实际成型与运行验收', '生存材料可达性尚未完整核验']
    (out/'设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    encoded = json.loads((out/'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['audit'] = record['audit']
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (out/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    page = (out/'三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="设计与检查.json"', 'href="../index.html"').replace('← 设计与检查', '← 八台新设计')
    page = page.replace('src="viewer.bundle.js"', 'src="../viewer.bundle.js"').replace('自由设计候选', 'V7 重设计候选')
    if 'browser_review' in record['audit']:
        page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。', '三维载入与剖切检查通过；游戏成型与运行仍待验收。')
    (out/'三维评审.html').write_text(page, encoding='utf-8')
    shutil.copy2(out/'viewer.bundle.js', OUT/'viewer.bundle.js')
    (out/'viewer.bundle.js').unlink()
    entry = {k: data[k] for k in ('key', 'name', 'title', 'size', 'description')}
    entry.update(blocks=len(data['blocks']), materials=len(record['audit']['palette']), sha256_nbt=sha,
                 form=data['brief'].get('form', ''), actual_xyz=record['audit']['size_baseline']['actual_xyz'])
    (out/'complete.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    return entry


def bundle():
    target = OUT/'I01-I08_V7_结构与预览.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))


def copy_generators():
    sources = OUT/'生成脚本'
    sources.mkdir(exist_ok=True)
    names = ('build_i01_i08_redesign_v7.py', 'i01_i08_v7_gallery.py', 'i01_chain_v7.py',
             'i02_i04_v7.py', 'i05_i07_v7.py', 'i08_v7.py', 'i09_i13_v6_common.py',
             'build_i09_i13_redesign_v6.py', 'l1-review89-recipe.mjs',
             'build_i07_calibration_preview.py', 'build_i03_centrifuge_preview.py',
             'build_i01_tidal_preview.py', 'build_i01_free_preview.py',
             'build_i01_tianming_preview.py', 'build_redesign69.py',
             'redesign69_geometry.py', 'material_resources.py', 'structure_size_baseline.py')
    for name in names:
        source = ROOT/'tools/structure_delivery'/name
        if source.exists():
            shutil.copy2(source, sources/name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', nargs='*')
    args = parser.parse_args()
    if set(args.keys)-set(GENERATORS):
        parser.error('编号只支持i01四阶与i02至i08')
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    for key in args.keys or GENERATORS:
        build_one(key)
    reference = ROOT/'logs/i09-i13-redesign-v6/reference-study.json'
    if reference.exists():
        shutil.copy2(reference, OUT/'结构参考.json')
    entries = [json.loads((OUT/key/'complete.json').read_text(encoding='utf-8')) for key in GENERATORS if (OUT/key/'complete.json').exists()]
    gallery(OUT, entries)
    copy_generators()
    bundle()


if __name__ == '__main__':
    main()
