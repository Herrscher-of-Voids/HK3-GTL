# -*- coding: utf-8 -*-
"""以现有材质打包俱利伽罗单主景A2，沿用0005统一评审界面。"""
from copy import deepcopy
from html import escape
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re
import shutil
from zipfile import ZipFile

import numpy as np

from i34_open_observatory_export_20261027 import export_dense
from package_0005_w04_em_skyhub_a1_20261114 import load, save, materials_for as inherited_materials_for, make_previews
from restore_w04_review_ui_20261110 import install

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-kurikara-a2-20261114'
OUT = ROOT / 'deliveries/0005_W04_俱利伽罗原作校准_构图A2_20261114'
SOURCE = ROOT / 'deliveries/0005_W04_鸣霆超导电磁天枢_构图A1_20261114'
NAME = '0005-w04-kurikara-a2-20261114'
TITLE = '0005 · W04 俱利伽罗原作校准 · 构图 A2'
REFERENCE = '参考图总览.html'
GALLERY = ['正面', '侧面', '背面', '俯视', '龙体正面', '龙体侧面', '龙体背面', '龙体俯视', '龙首近景', '磁环近景']
VANILLA_JAR = Path('C:/Users/OWNER/.gradle/caches/fabric-loom/1.20.1/minecraft-client.jar')
VANILLA_ADDITIONS = {'minecraft:gray_concrete', 'minecraft:white_terracotta', 'minecraft:white_concrete'}


def materials_for(states):
    inherited, sources = inherited_materials_for([state for state in states if state not in VANILLA_ADDITIONS])
    library = {material['state']: material for material in inherited}
    textures = {}
    with ZipFile(VANILLA_JAR) as archive:
        for state in states:
            if state in VANILLA_ADDITIONS:
                name = state.split(':')[1]
                entry = f'assets/minecraft/textures/block/{name}.png'
                raw = archive.read(entry)
                url = 'data:image/png;base64,' + base64.b64encode(raw).decode()
                library[state] = dict(state=state, faces={face: url for face in ['east', 'west', 'up', 'down', 'south', 'north']},
                                      transparent=False, texture_alpha=False, animations={},
                                      model=f'minecraft:block/{name}', complete_cube=True, tinted=False)
                textures[state] = dict(entry=entry, png_sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    sources.update(vanilla_archive=VANILLA_JAR.as_posix(),
                   vanilla_archive_sha256=hashlib.sha256(VANILLA_JAR.read_bytes()).hexdigest(),
                   added_vanilla_textures=textures,
                   resource_access='既有材质复用P4内嵌真实贴图，HRV使用当前项目模型指定贴图；新增三种原版材质读取1.20.1构建缓存JAR原生PNG并映射六面，未访问游戏实例。')
    return [library[state] for state in states], sources


def install_review(scene):
    shutil.copy2(SOURCE / '生成脚本/viewer.mjs', OUT / '生成脚本/viewer.mjs')
    metadata = install(OUT)
    metadata.update(candidate='0005 W04 俱利伽罗构图A2', geometry_unchanged=False,
                    reference_page=REFERENCE,
                    scope='俱利伽罗单主景与工业构图的真实方块材料表；与完整NBT和Schematic共用同一整数格数据。主控为红石块占位。')
    save(OUT / 'review-ui.json', metadata)
    page_path = OUT / '三维布局.html'
    page = page_path.read_text('utf8')
    page = re.sub(r'(<div class="candidate-note">).*?(</div>)',
                  lambda m: m[1] + escape(scene['summary']) + m[2], page, flags=re.S)
    page = re.sub(r'<button data-view="sword">.*?</button>', '', page)
    page = re.sub(r'<label class="asset-row"><input type="checkbox" data-asset="sword" checked>.*?</label>', '', page)
    controller = '(' + ','.join(map(str, scene['controller_world'])) + ')'
    replacements = {
        '(0,18,419)': controller,
        '俱利伽罗 D4': '俱利伽罗 A2',
        '体素磁环／双塔／母线／电弧': '水平磁环／储能塔／超导母线',
        '真实方块底盘／雷池／储能列／鸟居': '现有方块底盘／雷池／冷却设施／检修前庭',
        '>环塔<': '>磁环与双塔<',
        '>鸟居<': '>检修前庭<',
        '原候选离线核验': '离线生成记录',
        '原摆位与尺寸': '本候选坐标与尺寸',
        '<a href="index.html">← 候选总览</a>': '<a href="index.html">← 候选总览</a> · <a href="' + REFERENCE + '">多角度参考与模型来源</a>',
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    extra_views = [('dragonfront', '龙体正面'), ('dragonside', '龙体侧面'),
                   ('dragonback', '龙体背面'), ('dragontop', '龙体俯视')]
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label in extra_views)
    page = page.replace('<button data-view="dragon">龙体</button>', '<button data-view="dragon">龙体</button>' + buttons)
    page = re.sub(r'(<script id="reviewMetadata" type="application/json">).*?(</script>)',
                  lambda m: m[1] + json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c') + m[2],
                  page, flags=re.S)
    page_path.write_text(page, 'utf8')
    viewer_path = OUT / '生成脚本/viewer.mjs'
    viewer = viewer_path.read_text('utf8')
    viewer = re.sub(r"sword:'[^']*',", '', viewer)
    viewer = viewer.replace("dragon:'龙体近景',", "dragon:'龙体近景',dragonfront:'龙体正面',dragonside:'龙体侧面',dragonback:'龙体背面',dragontop:'龙体俯视',")
    viewer = viewer.replace("if(name==='dragonside')direction.set(1,0,0);",
                            "if(name==='dragonside')direction.set(1,0,0);\n    if(name==='dragonback')direction.set(0,.1,-1);\n    if(name==='dragontop')direction.set(0,1,.001);")
    for old, new in [("field:'环塔近景'", "field:'水平磁环与储能塔'"),
                     ("controller:'主控与接口位置'", "controller:'主控占位位置'"),
                     ("torii:'三进鸟居'", "torii:'检修前庭'"),
                     ("magnet:'托卡马克磁轭'", "magnet:'水平超导磁环'")]:
        viewer = viewer.replace(old, new)
    viewer_path.write_text(viewer, 'utf8')


def make_index(scene, manifest):
    style = re.search(r'<style>(.*?)</style>', (SOURCE / 'index.html').read_text('utf8'), re.S)[1]
    width, height, depth = manifest['actual_scene_size_xyz']
    gallery = ''.join(f'<figure><img src="{name}.png" alt="{name}"><figcaption>{name}</figcaption></figure>' for name in GALLERY)
    issues = ''.join('<p>' + escape(item) + '</p>' for item in manifest['known_issues'])
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{style}</style>
<p>0005 多方块设计 · W04 雷之律者 · 独立构图候选</p><h1>俱利伽罗原作校准<br>单主景构图 A2</h1>
<p class="note">{escape(scene['summary'])}</p><p><a href="三维布局.html">打开统一界面三维评审</a> · <a href="{REFERENCE}">多角度参考与模型来源</a> · <a href="../{SOURCE.name}/index.html">A1历史候选</a></p>
<img src="整体斜视.png" alt="俱利伽罗A2整体斜视"><p>实际宽{width}×深{depth}×高{height}格，{manifest['block_count']:,}个真实方块，{manifest['components']}个构件，{manifest['palette_count']}种现存材质。名义最低697×565×343仅为构图基准，完整构件生成后计算实际边界。</p>
<p>俱利伽罗作为唯一角色主景；全静态整数格构件，采用项目当前HRV绯雷红机壳与现有真实方块材质。形体校准依据、引用与待确认细节以参考页标注为准。</p>
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
    for view in ['dragonfront', 'dragonside', 'dragonback', 'dragontop']:
        details[view] = deepcopy(details['dragon'])
    data = dict(name=NAME, title=TITLE, size=size.tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
                center_blueprint=((low + high) / 2).tolist(), detail_views=details,
                controller=(controller - low).tolist(), ports=[])
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=previews)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)).decode()
    (OUT / 'data.js').write_text('window.W04_STATIC_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    issues = [
        '本候选为0005俱利伽罗单主景构图A2，原作校准结果待负责人评审，A1与更早历史保留。',
        '引用、模型来源与未确定细节见参考图总览；不以候选标题宣称逐格精确复刻或获得外观批准。',
        'W04功能主控尚未接入；红石块仅标示主控位置，不代表GT控制器。',
        '没有固定八接口面板；玩家可按现行规则在实体非主控位置替换合法通用接口。',
        '构件接合与视觉遮挡保留供评审，不以导出成功宣称全构图无干涉或无遮挡。',
        '全静态；未安装JAR，未操作游戏、活动实例或存档，未进行游戏搭建、成型或运行验收。',
    ]
    manifest = dict(name=NAME, title=TITLE, conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
                    nominal_size_xzy=[697, 565, 343], actual_scene_size_xyz=size.tolist(),
                    bounds_world=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
                    whole_integer_voxel=True, components=len(parts), block_count=block_count, palette_count=len(states),
                    source_component_blocks=sum(len(part['p']) for part in parts),
                    merge_rule='清单后者覆盖前者；全部独立构件源体素保留于日志components.npz，未按名义范围裁切。',
                    source_geometry=(LOG / 'components.npz').relative_to(ROOT).as_posix(),
                    scene_source=(LOG / 'scene.json').relative_to(ROOT).as_posix(), transforms=scene['transforms'],
                    source_models=scene['source_models'], source_quantization=scene['source_quantization'], reference_page=REFERENCE,
                    materials=dict(states=states, resource_sources=material_sources),
                    controller_world=controller.tolist(), controller_placeholder_state='minecraft:redstone_block',
                    controller_registered=False, ports_world=[], runtime_model_scale=[1, 1, 1], runtime_model_rotation=[0, 0, 0],
                    scenery_geometry_count=0, new_block_ids=[], animation_enabled=False, approved=False, game_verified=False, known_issues=issues)
    save(OUT / 'manifest.json', manifest)
    record = dict(stage='离线体素打包', size_xyz=size.tolist(), block_count=block_count, components=len(parts),
                  viewer_rendered_quads=quads, export=exported, materials=material_sources,
                  reference_page=REFERENCE, browser_visual_review='待生成截图', game_verified=False)
    save(OUT / 'verification.json', record)
    save(LOG / 'packaging.json', record)
    install_review(scene)
    make_index(scene, manifest)
    for path in [Path(__file__), ROOT / 'tools/structure_delivery/package_0005_w04_em_skyhub_a1_20261114.py',
                 ROOT / 'tools/structure_delivery/geometry_0005_w04_kurikara_a2_20261114.py',
                 ROOT / 'tools/structure_delivery/kurikara_original_head_0005_a2_20261114.py']:
        shutil.copy2(path, OUT / '生成脚本' / path.name)
    print(json.dumps(dict(directory=str(OUT), size_xyz=size.tolist(), blocks=block_count,
                         components=len(parts), rendered_quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
