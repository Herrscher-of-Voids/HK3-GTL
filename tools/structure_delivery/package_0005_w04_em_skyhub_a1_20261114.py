# -*- coding: utf-8 -*-
"""以现有材质打包0005鸣霆天枢独立构图。"""
from copy import deepcopy
from html import escape
from pathlib import Path
import base64
import gzip
import hashlib
import json
import re
import shutil

import numpy as np

from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs
from restore_w04_review_ui_20261110 import install

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w04-em-skyhub-a1-20261114'
OUT = ROOT / 'deliveries/0005_W04_鸣霆超导电磁天枢_构图A1_20261114'
SOURCE = ROOT / 'deliveries/W04_现存材质与通用接口_P4_20261112'
NAME = '0005-w04-em-skyhub-a1-20261114'
TITLE = '0005 · W04 鸣霆·超导电磁天枢 · 构图 A1'
HRV = 'hk3gtl:voltage_machine_casing_hrv'
GALLERY = ['正面', '侧面', '俯视', '龙首近景', '七雷近景', '磁环近景']


def load(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def materials_for(states):
    encoded = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    library = {item['state']: item for item in payload['materials']}
    materials = [deepcopy(library[state]) for state in states]
    model_path = ROOT / 'src/main/resources/assets/hk3gtl/models/block/voltage_machine_casing_hrv.json'
    texture_id = load(model_path)['textures']['all']
    namespace, texture_name = texture_id.split(':')
    texture_path = ROOT / 'src/main/resources/assets' / namespace / 'textures' / (texture_name + '.png')
    texture = texture_path.read_bytes()
    url = 'data:image/png;base64,' + base64.b64encode(texture).decode()
    for material in materials:
        if material['state'] == HRV:
            material['faces'] = {face: url for face in material['faces']}
    sources = dict(
        embedded_materials=(SOURCE / 'data.js').relative_to(ROOT).as_posix(),
        current_hrv_model=model_path.relative_to(ROOT).as_posix(),
        current_hrv_texture=texture_path.relative_to(ROOT).as_posix(),
        current_hrv_texture_sha256=hashlib.sha256(texture).hexdigest(),
        resource_access='非HRV材质复用P4内嵌真实贴图；HRV六面读取当前项目模型指定贴图；未访问游戏实例。',
    )
    return materials, sources


def make_previews(parts, owner, surfaces, low, size, states):
    previews = []
    quads = 0
    flat_owner = owner.ravel()
    for index, part in enumerate(parts, 1):
        at = part['p'] - low
        visible = owner[at[:, 1], at[:, 2], at[:, 0]] == index
        world = part['p'][visible]
        start = world.min(0)
        extent = world.max(0) - start + 1
        origin = start - low
        groups = [[[] for _ in range(6)] for _ in states]
        for material, faces in enumerate(surfaces):
            for face, indices in enumerate(faces):
                indices = np.asarray(indices, dtype=np.int64)
                indices = indices[flat_owner[indices] == index]
                x = indices % size[0] - origin[0]
                y = indices // (size[0] * size[2]) - origin[1]
                z = indices // size[0] % size[2] - origin[2]
                groups[material][face] = ((y * extent[2] + z) * extent[0] + x).tolist()
        starts, lengths, merged = merge_surface_runs(groups, extent.tolist())
        quads += merged['rendered_quads']
        previews.append(dict(id=part['id'], asset=part['asset'], origin=origin.tolist(),
                             size=extent.tolist(), starts=starts, lengths=lengths, blocks=len(world)))
        print('打包构件', part['id'], len(world), flush=True)
    return previews, quads


def install_review(scene):
    shutil.copy2(SOURCE / '生成脚本/viewer.mjs', OUT / '生成脚本/viewer.mjs')
    metadata = install(OUT)
    metadata.update(candidate='0005 W04 构图A1', geometry_unchanged=False,
                    scope='新构图合并后的真实方块材料表；与完整NBT和Schematic共用同一整数格数据。主控为红石块占位。')
    save(OUT / 'review-ui.json', metadata)
    page_path = OUT / '三维布局.html'
    page = page_path.read_text('utf8')
    page = re.sub(r'(<div class="candidate-note">).*?(</div>)',
                  lambda match: match[1] + escape(scene['summary']) + match[2], page)
    replacements = {
        '(0,18,419)': '(0,18,329)',
        '体素磁环／双塔／母线／电弧': '三层水平磁环／左右储能塔／超导母线',
        '真实方块底盘／雷池／储能列／鸟居': '现有方块底盘／下沉雷池／冷却设施／检修前庭',
        '>环塔<': '>磁环与双塔<',
        '>鸟居<': '>检修前庭<',
        '原候选离线核验': '离线生成记录',
        '原摆位与尺寸': '本候选坐标与尺寸',
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    page = re.sub(r'(<script id="reviewMetadata" type="application/json">).*?(</script>)',
                  lambda match: match[1] + json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c') + match[2],
                  page, flags=re.S)
    page_path.write_text(page, 'utf8')
    viewer_path = OUT / '生成脚本/viewer.mjs'
    viewer = viewer_path.read_text('utf8')
    viewer = viewer.replace("field:'环塔近景'", "field:'水平磁环与储能塔'")
    viewer = viewer.replace("controller:'主控与接口位置'", "controller:'主控占位位置'")
    viewer = viewer.replace("torii:'三进鸟居'", "torii:'检修前庭'")
    viewer = viewer.replace("magnet:'托卡马克磁轭'", "magnet:'水平超导磁环'")
    viewer_path.write_text(viewer, 'utf8')


def make_index(scene, manifest):
    style = re.search(r'<style>(.*?)</style>', (SOURCE / 'index.html').read_text('utf8'), re.S)[1]
    width, height, depth = manifest['actual_scene_size_xyz']
    gallery = ''.join(f'<figure><img src="{name}.png" alt="{name}"><figcaption>{name}</figcaption></figure>'
                      for name in GALLERY)
    issues = ''.join('<p>' + escape(item) + '</p>' for item in manifest['known_issues'])
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{style}</style>
<p>0005 多方块设计 · W04 雷之律者 · 独立构图候选</p><h1>鸣霆·超导电磁天枢<br>现有材料构图 A1</h1>
<p class="note">{escape(scene['summary'])}</p><p><a href="三维布局.html">打开统一界面三维评审</a> · <a href="../{SOURCE.name}/index.html">P4历史候选</a></p>
<img src="整体斜视.png" alt="鸣霆天枢构图A1整体斜视"><p>实际宽{width}×深{depth}×高{height}格，{manifest['block_count']:,}个真实方块，{manifest['components']}个构件，{manifest['palette_count']}种现存材质。名义最低697×565×343仅为构图基准，完整构件生成后计算实际边界。</p>
<p>三层水平超导磁环承托中央反应腔，左右储能塔与母线连入环体；七雷置于左前，俱利伽罗龙首位于右上。采用当前项目HRV绯雷红机壳贴图与P4内嵌的原版真实方块材质；无新增方块，无运行时缩放或建筑草模。</p>
<div class="grid">{gallery}</div><div class="note">{issues}</div>
<p><a href="{NAME}.nbt">完整整机NBT</a> · <a href="{NAME}.schem">完整整机Schematic</a> · <a href="材料清单.json">材料清单</a> · <a href="manifest.json">坐标与材料来源</a> · <a href="verification.json">离线生成记录</a></p></html>''', 'utf8')


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    scene = load(LOG / 'scene.json')
    source = np.load(LOG / 'components.npz')
    parts = [dict(**part, p=source[part['id'] + '__p'], states=source[part['id'] + '__states'])
             for part in scene['parts']]
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
    save(OUT / '材料清单.json', [dict(state=state, count=int(counts[index]))
                              for index, state in enumerate(states, 1)])
    materials, material_sources = materials_for(states)
    print('完整导出', size.tolist(), block_count, flush=True)
    exported = export_dense(cube, states, NAME, OUT)
    previews, quads = make_previews(parts, owner, exported.pop('surface_groups'), low, size, states)
    controller = np.asarray(scene['controller_world'])
    data = dict(name=NAME, title=TITLE, size=size.tolist(), blueprint_to_export_offset_xyz=(-low).tolist(),
                center_blueprint=((low + high) / 2).tolist(), detail_views=scene['detail_views'],
                controller=(controller - low).tolist(), ports=[])
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=previews)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(),
                                           compresslevel=6, mtime=0)).decode()
    (OUT / 'data.js').write_text('window.W04_STATIC_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    issues = [
        '本候选仅为0005独立外观构图，外观待评审，保留D4、S1、P3和P4历史。',
        'W04功能主控尚未接入；(0,18,329)的红石块仅用于标示主控位置，不代表GT控制器。',
        '没有固定八接口面板；玩家可按现行规则在实体非主控位置替换合法通用接口。',
        '构件接合与视觉遮挡保留供评审，不以导出成功宣称全构图无干涉或无遮挡。',
        '全静态；未安装JAR，未操作游戏、活动实例或存档，未进行游戏搭建、成型或运行验收。',
    ]
    manifest = dict(name=NAME, title=TITLE, conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
                    nominal_size_xzy=[697, 565, 343], actual_scene_size_xyz=size.tolist(),
                    bounds_world=dict(min=low.tolist(), max=high.tolist()),
                    blueprint_to_export_offset_xyz=(-low).tolist(), whole_integer_voxel=True,
                    components=len(parts), block_count=block_count, palette_count=len(states),
                    source_component_blocks=sum(len(part['p']) for part in parts),
                    merge_rule='清单后者覆盖前者；全部独立构件源体素保留于日志components.npz，未按名义范围裁切。',
                    source_geometry=(LOG / 'components.npz').relative_to(ROOT).as_posix(),
                    scene_source=(LOG / 'scene.json').relative_to(ROOT).as_posix(), transforms=scene['transforms'],
                    materials=dict(states=states, resource_sources=material_sources),
                    controller_world=controller.tolist(), controller_placeholder_state='minecraft:redstone_block',
                    controller_registered=False, ports_world=[], runtime_model_scale=[1, 1, 1],
                    runtime_model_rotation=[0, 0, 0], scenery_geometry_count=0, new_block_ids=[],
                    animation_enabled=False, approved=False, game_verified=False, known_issues=issues)
    save(OUT / 'manifest.json', manifest)
    record = dict(stage='离线体素打包', size_xyz=size.tolist(), block_count=block_count,
                  components=len(parts), viewer_rendered_quads=quads, export=exported,
                  materials=material_sources, browser_visual_review='待生成截图', game_verified=False)
    save(OUT / 'verification.json', record)
    save(LOG / 'packaging.json', record)
    install_review(scene)
    make_index(scene, manifest)
    shutil.copy2(__file__, OUT / '生成脚本' / Path(__file__).name)
    shutil.copy2(ROOT / 'tools/structure_delivery/geometry_0005_w04_em_skyhub_a1_20261114.py',
                 OUT / '生成脚本/geometry_0005_w04_em_skyhub_a1_20261114.py')
    print(json.dumps(dict(directory=str(OUT), size_xyz=size.tolist(), blocks=block_count,
                         components=len(parts), rendered_quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
