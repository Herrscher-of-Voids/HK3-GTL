# -*- coding: utf-8 -*-
"""五阶研究所独立候选交付；按固定世界主控逐阶增建，不覆盖生产结构。"""
import argparse
import collections
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
import nbtlib
import build_i07_calibration_preview as preview_package
from build_i09_i13_redesign_v6 import lodestone_export
from build_i01_orthogonal_v8 import save_record
from i01_v8_gallery import orthographic
from redesign69_geometry import ROOT
from research_campus_v1_gallery import gallery

OUT = ROOT/'deliveries/S01-S05_研究所五阶_原地扩建_V1_20261014'
LOG = ROOT/'logs/research-campus-additive-v1'
KEYS = [f's{n:02}' for n in range(1, 6)]
ZIP_NAME = 'S01-S05_研究所五阶_结构与预览.zip'
TEST_INSTANCE = Path.home()/'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'


def generate(key):
    import research_campus_early_v1 as early
    import research_campus_late_v1 as late
    return getattr(early if int(key[1:]) <= 3 else late, key)()


def build_one(key):
    from research_campus_common_v1 import validate
    data = generate(key)
    previous = generate(KEYS[KEYS.index(key)-1]) if key != KEYS[0] else None
    geometry = validate(data, previous)
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG/(key+'-geometry.json')).write_text(json.dumps(geometry, ensure_ascii=False, indent=2), encoding='utf-8')
    controller = data['controller']
    offset = [-q for q in controller]
    data['construction_notes'] = {
        'orientation': 'X向东、Y向上、Z向南；主控正面朝北。',
        'origin': [0, 0, 0], 'paste_anchor': controller, 'schematic_offset': offset,
        'anchor_rule': '五阶使用同一个世界主控锚点；新增建筑向四周及上方扩建。',
        'recommended_bottom_world_y': -60,
        'recommended_controller_world_y': -60+controller[1],
        'world_height_range': [-60, -60+data['size'][1]-1],
        'status': '原地扩建外观候选，待用户审阅。'}
    out = OUT/key
    preview_package.TEST_INSTANCE = TEST_INSTANCE
    preview_package.package(data, out, key, ['中央研究楼、主控及旧入口原位保留',
        '四次扩建逐格继承旧非主控方块', '研究、超算、液冷和共享资料空间分区'])
    sha = lodestone_export(data, out, LOG)
    schem_path = out/(data['name']+'.schem')
    schem = nbtlib.load(schem_path)
    schem['Offset'] = nbtlib.IntArray(offset)
    schem.save(schem_path, gzipped=True)
    record = json.loads((out/'设计与检查.json').read_text(encoding='utf-8'))
    audit = record['audit']
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    counts = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    audit.update(hashes={'nbt': sha, 'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest()},
        namespace_counts=dict(counts), namespace_percent={k: round(v/sum(counts.values())*100, 2) for k, v in counts.items()},
        design_markers=dict(collections.Counter(b['state'] for b in data['blocks'] if b['state'] in markers)),
        approval='待用户外观确认', reference_report='../建筑参考.json', schematic_offset=offset,
        additive_geometry=geometry)
    audit['checks'] += ['Lodestone导出NBT并逐格回读一致', 'Schematic按固定主控锚点对齐', '已声明通道具有实体地板与至少两格净高']
    payload = save_record(out, record)
    orthographic(data, payload['materials'], out)
    page = (out/'三维评审.html').read_text(encoding='utf-8')
    page = re.sub(r'<title>.*?</title>', '<title>'+data['title']+' · 原地扩建候选</title>', page, count=1)
    page = re.sub(r'<h1>.*?</h1>', '<h1>'+data['title']+'</h1>', page, count=1)
    page = page.replace('href="设计与检查.json"', 'href="../index.html"').replace('← 设计与检查', '← 五阶研究所')
    page = page.replace('src="viewer.bundle.js"', 'src="../viewer.bundle.js"').replace('自由设计候选', '原地扩建候选')
    note = '<details open><summary>原地扩建与粘贴锚点</summary><p>五阶使用同一世界主控位置。'
    note += f'本阶局部主控：{controller}；Schematic Offset：{offset}。底部建议 Y=-60。'
    note += 'NBT 没有粘贴偏移，需按局部主控坐标对齐。新一阶保留全部旧非主控方块及旧通道。</p></details>'
    page = page.replace('<details><summary>实际检查</summary>', note+'<details><summary>实际检查</summary>')
    (out/'三维评审.html').write_text(page, encoding='utf-8')
    viewer = (out/'viewer.bundle.js').read_text(encoding='utf-8')
    old = 'panel:{pos:[m,6,-45],target:[m,2,3]'
    new = 'panel:{pos:[r.controller[0]+.5,r.controller[1]+3,r.controller[2]-45],target:[r.controller[0]+.5,r.controller[1],r.controller[2]+.5]'
    assert viewer.count(old) == 1
    (OUT/'viewer.bundle.js').write_text(viewer.replace(old, new), encoding='utf-8')
    (out/'viewer.bundle.js').unlink()
    entry = {k: data[k] for k in ('key', 'name', 'title', 'size', 'description')}
    entry.update(blocks=len(data['blocks']), materials=len(audit['palette']), sha256_nbt=sha,
        controller=controller, form=data['brief']['form'], actual_xyz=audit['size_baseline']['actual_xyz'],
        upgrade_contract=data['upgrade_contract'])
    (out/'complete.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{key}: {len(data["blocks"]):,} 方块，导出完成', flush=True)
    return entry


def bundle():
    target = OUT/ZIP_NAME
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != target:
                archive.write(path, path.relative_to(OUT))


def copy_generators():
    target = OUT/'生成脚本'
    target.mkdir(exist_ok=True)
    names = ('build_research_campus_additive_v1.py', 'research_campus_v1_gallery.py',
        'research_campus_common_v1.py', 'research_campus_early_v1.py', 'research_campus_late_v1.py',
        'verify_research_campus_additive_v1.py', 'record_research_campus_v1.py', 'build_i01_orthogonal_v8.py',
        'i01_v8_gallery.py', 'i01_i08_v7_gallery.py', 'check_i01_upgrade.py',
        'build_i09_i13_redesign_v6.py', 'i09_i13_v6_common.py', 'l1-review89-recipe.mjs',
        'build_i07_calibration_preview.py', 'build_i03_centrifuge_preview.py',
        'build_i01_tidal_preview.py', 'build_i01_tianming_preview.py',
        'build_redesign69.py', 'redesign69_geometry.py', 'material_resources.py', 'structure_size_baseline.py')
    for name in names:
        shutil.copy2(ROOT/'tools/structure_delivery'/name, target/name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keys', nargs='*')
    args = parser.parse_args()
    if set(args.keys)-set(KEYS):
        parser.error('编号只支持 s01 至 s05')
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    for key in args.keys or KEYS:
        build_one(key)
    if (LOG/'reference-study.json').exists():
        shutil.copy2(LOG/'reference-study.json', OUT/'建筑参考.json')
    entries = [json.loads((OUT/key/'complete.json').read_text(encoding='utf-8'))
        for key in KEYS if (OUT/key/'complete.json').exists()]
    if len(entries) == 5:
        gallery(OUT, entries)
    copy_generators()
    bundle()


if __name__ == '__main__':
    main()
