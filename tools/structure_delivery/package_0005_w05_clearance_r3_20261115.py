import base64
from collections import Counter
from datetime import datetime
import gzip
import json
from pathlib import Path
import shutil

import numpy as np

import package_0005_w05_author_blueprint_20261115 as original
import geometry_0005_w05_network_clearance_r3_20261115 as network
import geometry_0005_w05_tower_clearance_r3_20261115 as towers


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
OUT = ROOT / 'deliveries/0005_W05_七处穿模修订_R3_20261115'
LOG = ROOT / 'logs/0005-w05-clearance-r3-20261115'
NOTE = 'R3按负责人认可的七项方案修订：管网局部绕塔，百叶局部避让，副塔叶轮半径38→35，跨盘斜撑外拱，实体双螺旋上下分段并由轮毂中孔细光流连接。保留已认可的5种现有方块、左右镜像、中轴与王冠；删除的12根主梁不恢复。'


def read(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    packed = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].removesuffix(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(packed)))
    archive = dict(np.load(SOURCE / '原始构件数据.npz'))
    materials = read(SOURCE / 'materials/materials.json')
    replacements = []
    for side in (-1, 1):
        replacements.extend([network.mobius(side), network.guide_blades(side)])
        for index in range(3):
            replacements.extend([towers.tower(side, index), towers.lift_rotor(side, index), towers.vortex(side, index)])
    replacements = {p.name: p for p in replacements}
    previews = []
    for p in payload['parts']:
        name = p['id']
        if name in replacements:
            new = replacements[name]
            archive[name + '_xyz'], archive[name + '_materials'] = new.p, new.states
            p, _, quads = original.mesh_part(new, materials)
            print(f'更新构件 {name} {len(new.p):,}格 / {quads:,}面', flush=True)
        previews.append(p)
    np.savez_compressed(OUT / '原始构件数据.npz', **archive)
    low = np.min([archive[p['id'] + '_xyz'].min(0) for p in previews], axis=0)
    high = np.max([archive[p['id'] + '_xyz'].max(0) for p in previews], axis=0)
    w, h, d = map(int, high - low + 1)
    owner = np.zeros(w * h * d, np.uint8)
    counts = np.zeros(8, np.int64)
    overlaps = []
    for i, p in enumerate(previews, 1):
        q = archive[p['id'] + '_xyz'] - low
        keys = (q[:, 1] * d + q[:, 2]) * w + q[:, 0]
        previous = owner[keys]
        hit = previous > 0
        ids, amounts = np.unique(previous[hit], return_counts=True)
        overlaps.extend(dict(first_component=previews[int(j) - 1]['id'], later_component=p['id'], coincident_voxels=int(n)) for j, n in zip(ids, amounts))
        owner[keys[~hit]] = i
        counts += np.bincount(archive[p['id'] + '_materials'], minlength=8)
    unique = int(np.count_nonzero(owner))
    del owner
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    revision = dict(id='R3', created_at=now, source_delivery=str(SOURCE.relative_to(ROOT)),
        user_quote='可以，你给我一个预览看看吧', note=NOTE, modified_components=list(replacements),
        palette_preserved=True, new_game_blocks=0, new_game_textures=0,
        authorization_scope='仅独立预览；没有批准替换运行资源、安装或游戏验收。')
    data = payload['data']
    data.update(bounds=dict(min=low.tolist(), max=high.tolist()), revision=revision)
    data['views'].update(
        fronttower=dict(label='前副塔与绕行管网', center=[-175, 145, -170], direction=[-1, .75, -.8], half=[70, 98, 75]),
        reartower=dict(label='后副塔上口净空', center=[-175, 195, 190], direction=[-1, .95, 1], half=[76, 63, 76]),
        rotor=dict(label='叶轮·外拱撑·分段风柱', center=[-175, 128, 10], direction=[-.6, .65, -.8], half=[50, 54, 50]))
    data['interpretations'].append(dict(section='负责人批准的R3七处避让修订', preview_sampling=NOTE))
    original.OUT = OUT
    packed_bytes = original.write_payload(data, previews, materials)
    manifest = read(SOURCE / 'manifest.json')
    components = [{k: v for k, v in p.items() if k not in ('starts', 'lengths')} for p in previews]
    block_counts = Counter()
    for m in materials:
        block_counts[m['state']] += int(counts[m['id']])
    manifest.update(candidate='R3 · 七处穿模修订预览', created_at=now, revision=revision,
        size_wdh=[w, d, h], occupied_bounds_xyz=data['bounds'], components=components,
        source_component_voxels=int(counts.sum()), unique_occupied_voxels=unique,
        overlap_extra_memberships=int(counts.sum()) - unique,
        material_counts={str(i): int(counts[i]) for i in range(1, 8)}, existing_block_counts=dict(block_counts),
        geometry_unchanged_from_r1=False, coordinates_preserved=False,
        geometry_constraints='仅按负责人批准的七项方案局部修订；完整生成，不以名义尺寸裁切。',
        appearance_approved=False, palette_approved=True, game_code_modified=False,
        game_resources_modified=False, jar_built=False, installed=False, game_started=False, game_verified=False)
    manifest['preview'].update(payload_gzip_bytes=packed_bytes,
        rendered_surface_faces=sum(sum(sum(f) for f in m) for p in previews for m in p['lengths']),
        merged_quads=sum(sum(len(f) for f in m) for p in previews for m in p['starts']))
    constraints = read(SOURCE / 'constraints.json')
    constraints['revision_override'] = revision
    mapping = read(SOURCE / '原文落实记录.json')
    mapping.update(components=components, interpretations=data['interpretations'], revision=revision)
    overlap_record = dict(note='包含正常嵌接的首占归因；独立净空测量另见净空检查，不将总重合计作缺陷数量。',
        unique_occupied_voxels=unique, extra_component_memberships=int(counts.sum()) - unique, pairs=overlaps)
    for name, value in [('manifest.json', manifest), ('constraints.json', constraints), ('原文落实记录.json', mapping),
                        ('修订记录.json', revision), ('构件重合记录.json', overlap_record)]:
        save(OUT / name, value)
    for name in ('作者原文.md', 'Three许可.txt', '材质来源.json', '现有方块映射.json'):
        shutil.copy2(SOURCE / name, OUT / name)
    material_mapping = read(OUT / '现有方块映射.json')
    for row in material_mapping:
        row['component_voxels'] = int(counts[row['slot']])
    save(OUT / '现有方块映射.json', material_mapping)
    detail_views = ('fronttower', 'reartower', 'rotor')
    original.VIEWS = {k: v for k, v in data['views'].items() if k not in detail_views}
    original.html_pages(data, previews, manifest, constraints, data['interpretations'], materials)
    note_before = '按原文保留双翼莫比乌斯风洞、中轴风暴炉、480×680底座及指定主控坐标。原文没给出的曲线、角度与叶数属于预览取样，已逐项公开。'
    warning_before = '原文自身的尺寸差异与构件重合照实保留，未通过移位、删件或裁切处理。独立分组可逐一隐藏。重合记录包含正常连接，不能直接当作全部碰撞错误。'
    for name in ('index.html', '三维评审.html', '原文与取样.html'):
        html = (OUT / name).read_text('utf8')
        html = html.replace('作者蓝图预览', 'R3 · 七处穿模修订').replace('作者原案独立预览', 'R3 · 七处穿模修订预览').replace('作者蓝图原案 · 独立预览', 'R3 · 七处穿模修订预览')
        html = html.replace('7种预览专用材质', '5种已有方块 · 7个用途槽').replace('七种专用预览材质', '已认可的现有方块配色')
        html = html.replace(note_before, NOTE).replace(warning_before, '本页是R3几何修订候选，待负责人评审。正常安装嵌接单列，离线净空结果不等同游戏成型、运行或实装验收。')
        html = html.replace('材质贴图与动态均仅供本网页预览；尚未注册游戏方块或BER。', '5种现有方块沿用R2认可配色，零新增方块或游戏材质。动画仅为网页演示。')
        html = html.replace('原文坐标、数量、外观分区与七种材料身份保留。未明确给出的逐格曲线和倾角为可追溯预览取样；原文冲突未私自修正。没有覆盖既有W05 A4，也未进行游戏实装。', NOTE)
        html = html.replace('<a href="manifest.json">', '<a href="../' + SOURCE.name + '/三维评审.html">R2修改前对照</a> · <a href="净空检查.json">R3净空检查</a> · <a href="manifest.json">', 1)
        html = html.replace('加载完整作者蓝图…', '加载R3七处避让构图…').replace('完整构图 · 待机状态', 'R3完整构图 · 待机状态')
        detail_buttons = ''.join(f'<button data-view="{k}">{data["views"][k]["label"]}</button>' for k in detail_views)
        html = html.replace('<button id="reset">', detail_buttons + '<button id="towerCutaway">只看中副塔净空</button><button id="reset">')
        if name == 'index.html':
            details = ''.join(f'<figure><img loading="lazy" src="{data["views"][k]["label"]}.png"><figcaption>{data["views"][k]["label"]}</figcaption></figure>' for k in detail_views)
            html = html.replace('<div class="grid">', '<figure><img src="副塔净空剖视.png"><figcaption>只显示中副塔：叶轮、外拱撑与上下分段风柱</figcaption></figure><div class="grid">' + details, 1)
        (OUT / name).write_text(html, 'utf8')
    save(LOG / 'generation.json', manifest)
    for name in ('geometry_0005_w05_network_clearance_r3_20261115.py', 'geometry_0005_w05_tower_clearance_r3_20261115.py', Path(__file__).name):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(output=str(OUT), parts=len(previews), changed=len(replacements), size_wdh=[w, d, h], voxels=int(counts.sum())), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
