# -*- coding: utf-8 -*-
"""以现存材质打包七雷取能单主景A3，沿用0005统一评审界面。"""
from copy import deepcopy
from html import escape
from pathlib import Path
import base64
import gzip
import json
import re
import shutil

import numpy as np

from i34_open_observatory_export_20261027 import export_dense
from package_0005_w04_em_skyhub_a1_20261114 import load, save, make_previews
from package_0005_w04_kurikara_a2_20261114 import materials_for
from restore_w04_review_ui_20261110 import install

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-seven-thunders-a3-20261114'
OUT = ROOT / 'deliveries/0005_W04_七雷取能天枢_构图A3_20261114'
SOURCE = ROOT / 'deliveries/0005_W04_鸣霆超导电磁天枢_构图A1_20261114'
NAME = '0005-w04-seven-thunders-a3-20261114'
TITLE = '0005 · W04 七雷取能天枢 · 构图 A3'
GALLERY = ['正面', '侧面', '背面', '俯视', '七雷正面', '七雷侧面', '刀身近景', '磁环与取能装置', '雷能汇流设施', '主控占位']
VIEWS = [('front', '前左全景'), ('right', '前右全景'), ('orthofront', '正面'),
         ('side', '侧面'), ('back', '背面'), ('top', '俯视'), ('inside', '逐层剖切'),
         ('sword', '七雷全貌'), ('swordfront', '七雷正面'), ('swordside', '七雷侧面'),
         ('blade', '刀身近景'), ('field', '磁环与取能装置'), ('reactor', '雷能汇流设施'),
         ('casing', '单格机壳'), ('controller', '主控占位')]


def install_review(scene):
    shutil.copy2(SOURCE / '生成脚本/viewer.mjs', OUT / '生成脚本/viewer.mjs')
    metadata = install(OUT)
    metadata.update(candidate='0005 W04 七雷取能构图A3', geometry_unchanged=False,
                    energy_extraction_visual_only=True, mechanism_implemented=False,
                    scope='七雷为唯一主景，刀身取能仅为外观构图；合并后真实方块材料表与完整NBT和Schematic一致。主控为红石块占位，取能机制未实现。')
    save(OUT / 'review-ui.json', metadata)
    page_path = OUT / '三维布局.html'
    page = page_path.read_text('utf8')
    page = re.sub(r'(<div class="candidate-note">).*?(</div>)',
                  lambda m: m[1] + escape(scene['summary']) + m[2], page, flags=re.S)
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label in VIEWS)
    page = re.sub(r'<div><button data-view="front">.*?</div>', '<div>' + buttons + '</div>', page, count=1, flags=re.S)
    page = re.sub(r'<label class="asset-row"><input type="checkbox" data-asset="dragon" checked>.*?</label>', '', page)
    page = page.replace('<label class="asset-row"><input type="checkbox" data-asset="sword"',
        '<label class="asset-row"><input type="checkbox" data-asset="energy" checked>刃面导能弧与方向光节</label><label class="asset-row"><input type="checkbox" data-asset="sword"')
    controller = '(' + ','.join(map(str, scene['controller_world'])) + ')'
    for old, new in {
        '(0,18,419)': controller,
        '涤罪七雷·鸣雷见 S1': '涤罪七雷 · 静态重新量化',
        '体素磁环／双塔／母线／电弧': '多层取能环／导能弧／汇流设施',
        '真实方块底盘／雷池／储能列／鸟居': '现存方块底盘／汇流核心／检修前庭',
        '原候选离线核验': '离线生成记录',
        '原摆位与尺寸': '本候选坐标与尺寸',
    }.items():
        page = page.replace(old, new)
    page = re.sub(r'(<script id="reviewMetadata" type="application/json">).*?(</script>)',
                  lambda m: m[1] + json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c') + m[2],
                  page, flags=re.S)
    page_path.write_text(page, 'utf8')
    viewer_path = OUT / '生成脚本/viewer.mjs'
    viewer = viewer_path.read_text('utf8')
    viewer = viewer.replace("if(name==='orthofront'||name==='dragonfront')", "if(name==='orthofront'||name==='swordfront')")
    viewer = viewer.replace("if(name==='dragonside')", "if(name==='swordside')")
    names = 'const names=' + json.dumps(dict(VIEWS), ensure_ascii=False) + ';'
    viewer = re.sub(r"const names=\{front:.*?\};", lambda _: names, viewer, count=1, flags=re.S)
    viewer_path.write_text(viewer, 'utf8')


def make_index(scene, manifest):
    style = re.search(r'<style>(.*?)</style>', (SOURCE / 'index.html').read_text('utf8'), re.S)[1]
    width, height, depth = manifest['actual_scene_size_xyz']
    gallery = ''.join(f'<figure><img src="{name}.png" alt="{name}"><figcaption>{name}</figcaption></figure>' for name in GALLERY)
    issues = ''.join('<p>' + escape(item) + '</p>' for item in manifest['known_issues'])
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{style}</style>
<p>0005 多方块设计 · W04 雷之律者 · 独立构图候选</p><h1>七雷取能天枢<br>中央悬刀构图 A3</h1>
<p class="note">{escape(scene['summary'])}</p><p><a href="三维布局.html">打开统一界面三维评审</a> · <a href="../{SOURCE.name}/index.html">A1历史候选</a></p>
<img src="整体斜视.png" alt="七雷取能天枢A3整体斜视"><p>实际宽{width}×深{depth}×高{height}格，{manifest['block_count']:,}个真实方块，{manifest['components']}个构件，{manifest['palette_count']}种现存材质。名义最低697×565×343仅为构图基准，完整构件生成后计算实际边界。</p>
<p>涤罪七雷作为唯一主景悬空立于中央；多层取能环围绕刀身，导能弧将雷能引向两侧汇流与储能设施。七雷已静态重新量化，无运行时模型缩放。全静态整数格构件，使用项目现有真实方块材质。</p>
<p class="note">刀身取能是本候选的外观叙事，尚未实现游戏取能机制；红石块仅为主控位置占位。外观待评审，未进行游戏搭建、成型或运行。</p>
<div class="grid">{gallery}</div><div class="note">{issues}</div>
<p><a href="{NAME}.nbt">完整整机NBT</a> · <a href="{NAME}.schem">完整整机Schematic</a> · <a href="材料清单.json">材料清单</a> · <a href="manifest.json">坐标与材料来源</a> · <a href="verification.json">离线生成记录</a></p></html>''', 'utf8')


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    scene = load(LOG / 'scene.json')
    source = np.load(LOG / 'components.npz')
    parts = [dict(**part, p=source[part['id'] + '__p'], states=source[part['id'] + '__states']) for part in scene['parts']]
    low = np.min([part['p'].min(0) for part in parts], axis=0)
    high = np.max([part['p'].max(0) for part in parts], axis=0)
    size = high - low + 1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    owner = np.zeros_like(cube)
    for index, part in enumerate(parts, 1):
        at = part['p'] - low
        cube[at[:, 1], at[:, 2], at[:, 0]] = part['states']
        owner[at[:, 1], at[:, 2], at[:, 0]] = index
    used = np.unique(cube)
    used = used[used > 0]
    states = [scene['states'][int(index) - 1] for index in used]
    remap = np.zeros(len(scene['states']) + 1, np.uint8)
    remap[used] = np.arange(1, len(used) + 1)
    cube = remap[cube]
    counts = np.bincount(cube.ravel(), minlength=len(states) + 1)
    block_count = int(counts[1:].sum())
    save(OUT / '材料清单.json', [dict(state=state, count=int(counts[index])) for index, state in enumerate(states, 1)])
    materials, material_sources = materials_for(states)
    print('完整导出', size.tolist(), block_count, flush=True)
    exported = export_dense(cube, states, NAME, OUT)
    previews, quads = make_previews(parts, owner, exported.pop('surface_groups'), low, size, states)
    controller = np.asarray(scene['controller_world'])
    details = deepcopy(scene['detail_views'])
    details['swordfront'] = deepcopy(details['sword'])
    details['swordside'] = deepcopy(details['sword'])
    details['blade'] = details.get('blade', dict(center=details['sword']['center'], half=[n * .42 for n in details['sword']['half']]))
    data = dict(name=NAME, title=TITLE, size=size.tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
                center_blueprint=((low + high) / 2).tolist(), detail_views=details,
                controller=(controller - low).tolist(), ports=[])
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=previews)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)).decode()
    (OUT / 'data.js').write_text('window.W04_STATIC_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    issues = [
        '本候选为0005七雷取能天枢构图A3，涤罪七雷为唯一主景；A1、A2及更早历史保留。',
        '取能环、导能弧与汇流设施表达从刀身获取雷能的外观构图，不代表游戏取能机制已经实现。',
        '七雷仅静态重新量化，预览和导出均使用同一整数格数据，没有运行时缩放。',
        '红石块仅标示主控位置，不代表GT控制器；无固定八孔面板，实体非主控位置可按现行规则替换合法通用接口。',
        '构件接合与视觉遮挡保留供评审，不以导出成功宣称全构图无干涉或无遮挡。',
        '全静态、外观未获批准；未安装JAR，未操作游戏、活动实例或存档，未进行游戏搭建、成型或运行验收。',
    ]
    manifest = dict(name=NAME, title=TITLE, conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
                    nominal_size_xzy=[697, 565, 343], actual_scene_size_xyz=size.tolist(),
                    bounds_world=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
                    whole_integer_voxel=True, components=len(parts), block_count=block_count, palette_count=len(states),
                    source_component_blocks=sum(len(part['p']) for part in parts),
                    merge_rule='清单后者覆盖前者；全部独立构件源体素保留于日志components.npz，未按名义范围裁切。',
                    source_geometry=(LOG / 'components.npz').relative_to(ROOT).as_posix(),
                    scene_source=(LOG / 'scene.json').relative_to(ROOT).as_posix(), transforms=scene['transforms'],
                    source_models=scene['source_models'], source_quantization=scene['source_quantization'],
                    energy_design=scene['energy_design'],
                    single_subject='sword', energy_extraction_visual_only=True, mechanism_implemented=False,
                    materials=dict(states=states, resource_sources=material_sources),
                    controller_world=controller.tolist(), controller_placeholder_state='minecraft:redstone_block',
                    controller_registered=False, ports_world=[], runtime_model_scale=[1, 1, 1], runtime_model_rotation=[0, 0, 0],
                    scenery_geometry_count=0, new_block_ids=[], animation_enabled=False, approved=False, game_verified=False, known_issues=issues)
    save(OUT / 'manifest.json', manifest)
    record = dict(stage='离线体素打包', size_xyz=size.tolist(), block_count=block_count, components=len(parts),
                  viewer_rendered_quads=quads, export=exported, materials=material_sources,
                  energy_extraction_visual_only=True, mechanism_implemented=False,
                  browser_visual_review='待生成截图', game_verified=False)
    save(OUT / 'verification.json', record)
    save(LOG / 'packaging.json', record)
    install_review(scene)
    make_index(scene, manifest)
    for name in [Path(__file__).name, 'package_0005_w04_em_skyhub_a1_20261114.py',
                 'package_0005_w04_kurikara_a2_20261114.py', 'geometry_0005_w04_seven_thunders_a3_20261114.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(directory=str(OUT), size_xyz=size.tolist(), blocks=block_count,
                         components=len(parts), rendered_quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
