# -*- coding: utf-8 -*-
"""I01四阶正交重设计独立交付；不覆盖已交付V7或其他机器。"""
import argparse
import base64
import collections
import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
import nbtlib
import build_i07_calibration_preview as preview_package
from build_i09_i13_redesign_v6 import lodestone_export
from redesign69_geometry import ROOT
from i01_v8_gallery import gallery, orthographic

OUT = ROOT/'deliveries/I01_采集塔四阶_正交重设计_V8_20261014'
LOG = ROOT/'logs/i01-orthogonal-v8'
TEST_INSTANCE = Path.home()/'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'
KEYS = [f'i01-{n}' for n in range(1, 5)]


def save_record(out, record):
    (out/'设计与检查.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    encoded = json.loads((out/'data.js').read_text(encoding='utf-8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    payload['data'] = record['data']
    payload['audit'] = record['audit']
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False,
        separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (out/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    return payload


def build_one(key):
    import i01_chain_v8
    data = getattr(i01_chain_v8, key.replace('-', '_'))()
    controller = data['controller']
    offset = [-q for q in controller]
    data['construction_notes'] = {
        'orientation': 'X向东、Y向上、Z向南；主控正面朝北。',
        'origin': [0, 0, 0], 'paste_anchor': controller, 'schematic_offset': offset,
        'anchor_rule': '四阶使用同一个世界主控锚点；局部坐标因向四周扩建而平移。',
        'recommended_bottom_world_y': -60, 'recommended_controller_world_y': -60+controller[1],
        'world_height_range': [-60, -60+data['size'][1]-1],
        'status': 'V8外观候选，待用户审阅。'}
    out = OUT/key
    preview_package.TEST_INSTANCE = TEST_INSTANCE
    preview_package.package(data, out, key, ['围绕同一竖直核心沿正交轴线扩建',
                            '逐阶保留非主控方块；固定世界锚点', '北向接口与连续维护入口'])
    sha = lodestone_export(data, out, LOG)
    schem_path = out/(data['name']+'.schem')
    schem = nbtlib.load(schem_path)
    schem['Offset'] = nbtlib.IntArray(offset)
    schem.save(schem_path, gzipped=True)
    assert list(map(int, nbtlib.load(schem_path)['Offset'])) == offset
    record = json.loads((out/'设计与检查.json').read_text(encoding='utf-8'))
    audit = record['audit']
    audit['hashes'] = {'nbt': sha, 'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest()}
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    counts = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    ordinary = sum(counts.values())
    audit.update(namespace_counts=dict(counts),
        namespace_percent={k: round(v/ordinary*100, 2) for k, v in counts.items()},
        design_markers=dict(collections.Counter(b['state'] for b in data['blocks'] if b['state'] in markers)),
        approval='待用户外观确认', reference_report='../建筑参考.json', schematic_offset=offset)
    audit['checks'] += ['Lodestone重新导出NBT并逐格回读一致', 'Schematic粘贴偏移与主控锚点对应']
    assert audit['design_markers'] == {'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
    payload = save_record(out, record)
    orthographic(data, payload['materials'], out)
    page = (out/'三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="设计与检查.json"', 'href="../index.html"').replace('← 设计与检查', '← 采集塔四阶')
    page = page.replace('src="viewer.bundle.js"', 'src="../viewer.bundle.js"').replace('自由设计候选', 'V8 正交重设计候选')
    anchor_note = '<details open><summary>扩建与粘贴锚点</summary><p>四阶共用同一世界主控位置。'
    anchor_note += f'本阶局部主控：{controller}；Schematic Offset：{offset}。'
    anchor_note += f'推荐世界主控高度 Y={-60+controller[1]}，对应底部 Y=-60。'
    anchor_note += 'NBT 本身没有粘贴偏移，需按上述局部主控坐标对齐。新一阶所有旧方块位置及状态保留。</p></details>'
    page = page.replace('<details><summary>实际检查</summary>', anchor_note+'<details><summary>实际检查</summary>')
    (out/'三维评审.html').write_text(page, encoding='utf-8')
    viewer = (out/'viewer.bundle.js').read_text(encoding='utf-8')
    old_panel = 'panel:{pos:[m,6,-45],target:[m,2,3]'
    new_panel = 'panel:{pos:[r.controller[0]+.5,r.controller[1]+3,r.controller[2]-45],target:[r.controller[0]+.5,r.controller[1],r.controller[2]+.5]'
    assert viewer.count(old_panel) == 1
    viewer = viewer.replace(old_panel, new_panel)
    (OUT/'viewer.bundle.js').write_text(viewer, encoding='utf-8')
    (out/'viewer.bundle.js').unlink()
    entry = {k: data[k] for k in ('key', 'name', 'title', 'size', 'description')}
    entry.update(blocks=len(data['blocks']), materials=len(audit['palette']), sha256_nbt=sha,
                 controller=controller, form=data['brief']['form'], actual_xyz=audit['size_baseline']['actual_xyz'])
    (out/'complete.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    return entry


def bundle():
    target = OUT/'I01_V8_四阶结构与预览.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))


def copy_generators():
    sources = OUT/'生成脚本'
    sources.mkdir(exist_ok=True)
    names = ('build_i01_orthogonal_v8.py', 'i01_v8_gallery.py', 'i01_chain_v8.py',
             'i01_i08_v7_gallery.py', 'i09_i13_v6_common.py', 'check_i01_upgrade.py', 'verify_i01_orthogonal_v8.py',
             'build_i09_i13_redesign_v6.py', 'l1-review89-recipe.mjs',
             'build_i07_calibration_preview.py', 'build_i03_centrifuge_preview.py',
             'build_i01_tidal_preview.py',
             'build_i01_tianming_preview.py', 'build_redesign69.py',
             'redesign69_geometry.py', 'material_resources.py', 'structure_size_baseline.py')
    for name in names:
        source = ROOT/'tools/structure_delivery'/name
        shutil.copy2(source, sources/name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', nargs='*')
    args = parser.parse_args()
    if set(args.keys)-set(KEYS):
        parser.error('编号只支持 i01-1 至 i01-4')
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    for key in args.keys or KEYS:
        build_one(key)
    reference = LOG/'reference-study.json'
    if reference.exists():
        shutil.copy2(reference, OUT/'建筑参考.json')
    entries = [json.loads((OUT/key/'complete.json').read_text(encoding='utf-8'))
               for key in KEYS if (OUT/key/'complete.json').exists()]
    if len(entries) == 4:
        gallery(OUT, entries)
    copy_generators()
    bundle()


if __name__ == '__main__':
    main()
