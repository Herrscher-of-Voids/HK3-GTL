from copy import deepcopy
from datetime import datetime
from html import escape
from pathlib import Path
import base64
import gzip
import json
import re
import shutil

import numpy as np

import geometry_0005_w05_wendy_wings_a2_20261115 as geometry
import package_0005_i37_suspended_test_dock_a2_20261115 as shared
from material_resources import Resources


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W05_温蒂风翼渴望之心_A2_20261115'
LOG = ROOT / 'logs/0005-w05-wendy-wings-a2-20261115'
SOURCE = ROOT / 'deliveries/0005_W04_七雷取能天枢_构图A3_20261114'
VIEWS = [('front', '前左全景', '整体预览.png'), ('right', '前右全景', '前右预览.png'),
         ('orthofront', '正面', '正面预览.png'), ('side', '侧面', '侧面预览.png'),
         ('back', '背面', '背面预览.png'), ('top', '俯视', '俯视预览.png'),
         ('core', '渴望之心', '核心近景.png'), ('wing', '风翼羽片', '风翼近景.png'),
         ('controller', '主控位置', '主控近景.png')]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def install_viewer(data, counts):
    core = (SOURCE / '生成脚本/viewer.mjs').read_text('utf8').split('/* W04统一评审界面适配开始 */', 1)[0]
    core = core.replace('W04', 'W05').replace("renderer.setClearColor('#18101c')", "renderer.setClearColor('#0d1919')")
    core = core.replace('controls.target.copy(target);camera.up.set',
                        'if(detail?.position)direction.set(...detail.position).sub(new THREE.Vector3(...detail.center));\n    controls.target.copy(target);camera.up.set')
    adapter = (ROOT / 'tools/structure_delivery/w04_review_ui_20261110.mjs').read_text('utf8').replace('W04', 'W05')
    names = 'const names=' + json.dumps({key: label for key, label, _ in VIEWS}, ensure_ascii=False) + ';'
    adapter = re.sub(r'const names=\{.*?\};', lambda _: names, adapter, count=1, flags=re.S)
    adapter = adapter.replace('原评审界面 · 整机真实方块 · 全静态', 'W05温蒂风翼候选 · 整机真实方块 · 全静态')
    (OUT / '生成脚本/viewer.mjs').write_text(core + '\n' + adapter, 'utf8')
    metadata = dict(candidate=data['title'], source_voxels=sum(counts.values()), whole_integer_voxel=True,
                    materials=[dict(state=s, count=n, label=geometry.NAMES[s]) for s, n in counts.items()],
                    scope='预览与完整结构共用整数格几何；红石块只定位主控；本候选尚未替换W05运行蓝图。')
    save(OUT / 'review-ui.json', metadata)
    return metadata


def pages(data, parts, metadata, manifest):
    css = re.search(r'<style>(.*?)</style>', (SOURCE / '三维布局.html').read_text('utf8'), re.S)[1]
    css += '.candidate-note{border-color:#48c9a3;background:#19362f}.review{grid-template-columns:minmax(0,1fr) 340px}pre{white-space:pre-wrap;overflow-wrap:anywhere}.clearance{color:#a9dfca}'
    title = escape(data['title'])
    w, h, d = data['size']
    buttons = ''.join(f'<button data-view="{key}">{label}</button>' for key, label, _ in VIEWS)
    part_rows = ''.join(f'<label class="asset-row"><input type="checkbox" checked data-part="{escape(p["id"])}">{escape(p["label"])} · {p["blocks"]:,}块</label>' for p in parts)
    material_rows = ''.join(f'<p><b>{escape(geometry.NAMES[s])}</b>：{escape(geometry.ROLES[s])}</p>' for s in manifest['material_counts'])
    clearance = escape(json.dumps(data['geometry_clearance'], ensure_ascii=False, indent=2))
    status = 'W05已有真实GT主控；红石块仅标记本候选主控位置。本轮只评审静态外观，尚未替换运行蓝图，未构建、安装或运行游戏。'
    meta_json = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 三维评审</title><style>{css}</style>
<header><a href="index.html">← 候选总览</a><h1>{title}</h1><div>0005 · W05 · 运行目标WSV · {w}×{d}×{h}（宽×深×高） · {manifest['block_count']:,}方块 · 全静态</div></header>
<main class="review"><section id="stage" aria-label="W05完整静态三维评审"><div id="loading">加载完整静态构件与真实方块材质…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">{escape(data['summary'])}</div>
<div class="candidate-note clearance">构件体素交叠与净空距离见<a href="净空记录.json">本候选几何记录</a>；可切换侧面、背面、俯视及剖切检查。无动画。</div>
<div class="locator"><b>主控位置 {data['controller']}</b><p>{status}</p><button data-view="controller">定位主控</button><label><input id="ports" type="checkbox">主控定位框</label></div>
<div>{buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 Y=<b id="layerValue">{h}</b><output id="layerLabel">{h}</output><input id="layer" type="range" min="0" max="{h}" value="{h}"></label>
<label><input id="glass" type="checkbox" checked>显示玻璃</label><label><input id="showGrid" type="checkbox">参考网格</label><p><button id="reset">复位全景</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏查看</button></p><p id="counts"></p><p id="stats"></p><p id="status"></p>
<details open><summary>构件分组</summary>{part_rows}</details><details><summary>真实材料筛选</summary><p id="materialCounts"></p><input id="materialSearch" type="search" placeholder="材料名或方块ID"><div id="materials"></div></details>
<details><summary>材料用途</summary>{material_rows}</details><details><summary>构件净空原始记录</summary><pre>{clearance}</pre></details><details><summary>候选状态与文件</summary><p>{status}</p><p>风翼、风车和宝石的建筑形体为原创转译；宝石几何不宣称官方实体复刻。剖切和隐藏材料不补画内部切面。</p><p><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">完整Schematic</a> · <a href="材料清单.json">材料与用途</a> · <a href="材质来源.json">真实材质来源</a> · <a href="manifest.json">坐标与生成记录</a></p></details>
</aside></main><script id="reviewMetadata" type="application/json">{meta_json}</script><script src="data.js"></script><script src="viewer.bundle.js"></script></html>'''
    (OUT / '三维评审.html').write_text(page, 'utf8')
    gallery = ''.join(f'<figure><img src="{file}" alt="{label}" loading="lazy"><figcaption>{label}</figcaption></figure>' for _, label, file in VIEWS[1:])
    index = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{max-width:1500px;margin:30px auto;padding:0 22px;background:#0d1a1b;color:#e3f3ee;font:16px/1.8 "Microsoft YaHei",sans-serif}}a{{color:#9be2ca}}img{{width:100%}}.note{{padding:15px;border-left:3px solid #48c9a3;background:#19362f}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}figure{{margin:0}}figcaption{{padding:7px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}</style>
<p>0005 多方块设计 · W05 · 独立静态外观候选 A2</p><h1>{title}</h1><p class="note">宽{w}×深{d}×高{h}格 · {manifest['block_count']:,}方块 · {manifest['material_count']}种现存材料 · {len(parts)}个可独立显隐构件。</p>
<p>{escape(data['summary'])}</p><p><a href="三维评审.html">打开统一三维评审 →</a> · <a href="净空记录.json">构件交叠与净空记录</a> · <a href="材料清单.json">真实材料与用途</a> · <a href="manifest.json">完整设计记录</a></p><img src="整体预览.png" alt="W05温蒂风翼与渴望之心完整预览">
<p class="note">{status} 静态预览与离线几何记录不代替游戏成型、运行验收，不增加验收分；旧W05候选保留。</p><div class="grid">{gallery}</div><p><a href="{data['name']}.nbt">完整NBT</a> · <a href="{data['name']}.schem">完整Schematic</a> · <a href="材质来源.json">真实材质来源</a></p></html>'''
    (OUT / 'index.html').write_text(index, 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    shared.OUT, shared.geometry = OUT, geometry
    cube, owners, original_data = geometry.build()
    data = deepcopy(original_data)
    h, d, w = cube.shape
    low, high = shared.bounds(cube != 0)
    tally = np.zeros(len(geometry.STATES) + 1, np.int64)
    for layer in cube:
        tally += np.bincount(layer.ravel(), minlength=len(tally))
    counts = {state: int(tally[index]) for index, state in enumerate(geometry.STATES, 1)}
    block_count = int(tally[1:].sum())
    print('导出完整结构', [w, h, d], block_count, flush=True)
    files = shared.export(cube, geometry.STATES, data['name'], block_count)
    resources = Resources(instance=shared.INSTANCE, client=shared.CLIENT, project_resources=ROOT / 'src/main/resources')
    materials = [resources.material(state) for state in geometry.STATES]
    save(OUT / '材质来源.json', dict(instance=str(shared.INSTANCE), client=str(shared.CLIENT),
         project_resources='src/main/resources', resources=resources.sources,
         rendering='解析既有方块状态、父模型与六面PNG；动画贴图取静态首帧。'))
    resources.close()
    parts, faces, quads = shared.preview_parts(cube, owners, materials)
    data.update(size=[w, h, d], blueprint_to_export_offset_xyz=[0, 0, 0],
                center_blueprint=[(low[i] + high[i]) / 2 for i in range(3)])
    data['detail_views']['controller'] = dict(center=data['controller'], half=[48, 32, 38])
    payload = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=parts)
    packed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)
    (OUT / 'data.js').write_text('window.W05_STATIC_PAYLOAD=' + json.dumps(base64.b64encode(packed).decode()) + ';', 'utf8')
    manifest = dict(title=data['title'], name=data['name'], candidate='A2', machine='W05', target_voltage='WSV',
                    conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
                    created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
                    size_xyz=[w, h, d], size_wdh=[w, d, h], occupied_bounds_xyz=dict(min=low, max=high),
                    block_count=block_count, material_count=sum(n > 0 for n in counts.values()), material_counts=counts,
                    parts=[dict(id=p['id'], name=p['label'], origin=p['origin'], size=p['size'], blocks=p['blocks']) for p in parts],
                    controller=data['controller'], controller_registered=True, preview_marker='minecraft:redstone_block',
                    palette_identity=data['palette_identity'], geometry_clearance=data['geometry_clearance'],
                    files=files, preview=dict(unit_faces=faces, merged_quads=quads, payload_gzip_bytes=len(packed),
                    static=True, real_block_textures=True), appearance_approved=False, runtime_blueprint_modified=False,
                    jar_built=False, installed=False, game_started=False, game_verified=False,
                    automated_tests_run=False, acceptance_score_changed=False)
    save(OUT / 'manifest.json', manifest)
    save(OUT / '净空记录.json', data['geometry_clearance'])
    save(LOG / 'geometry-clearance.json', data['geometry_clearance'])
    save(OUT / '材料清单.json', [dict(state=s, name=geometry.NAMES[s], role=geometry.ROLES[s], count=n) for s, n in counts.items()])
    metadata = install_viewer(data, counts)
    pages(data, parts, metadata, manifest)
    shutil.copy2(Path('C:/Users/OWNER/.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE'), OUT / 'Three许可.txt')
    for source in (Path(__file__), Path(geometry.__file__)):
        shutil.copy2(source, OUT / '生成脚本' / source.name)
    save(LOG / 'generation.json', manifest)
    print(json.dumps(dict(output=str(OUT), size_wdh=[w, d, h], blocks=block_count,
          materials=manifest['material_count'], parts=len(parts), merged_quads=quads), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
