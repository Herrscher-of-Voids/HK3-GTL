import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from dominion_p2_body import build_body
from dominion_p2_head import build_head
from dominion_p2_hands import build_hands
from dominion_p2_export import write_vox
from package_0005_w12_author_blueprint_20261116 import mesh_part


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_乌合之众_原作像素重建_P3_20261117'
LOG = ROOT/'logs/0005-dominion-p3-20261117'
COLORS = [('黑色凹腔', '#101420'), ('深蓝灰装甲', '#292f43'), ('蓝紫灰装甲', '#434b69'), ('装甲亮面', '#616d92'),
          ('浅金', '#e4ca91'), ('原色金', '#bba16b'), ('暗金', '#796345'), ('红眼', '#e52342'), ('眼光高亮', '#ff6475'), ('装甲接缝', '#202737')]
VIEWS = {
    'body': dict(label='站立本体', direction=[-.4, .12, 1.5], center=[0, 224, 0], half=[196, 226, 84]),
    'head': dict(label='头盔近景', direction=[-.5, .15, 1.5], center=[0, 398, 4], half=[48, 36, 42]),
    'head_side': dict(label='头盔侧后', direction=[-1.5, .18, -.5], center=[0, 400, -2], half=[49, 41, 48]),
    'back_detail': dict(label='背甲近景', direction=[-.45, .18, -1.5], center=[0, 309, -5], half=[88, 96, 53]),
    'hand_back': dict(label='掌背指节', direction=[-.4, .25, -1.5], center=[-311, 363, 75], half=[82, 86, 70]),
    'chest': dict(label='胸肩近景', direction=[-.55, .25, 1.4], center=[0, 339, 0], half=[165, 108, 56]),
    'hands': dict(label='悬浮手近景', direction=[.2, .14, 1.5], center=[-311, 363, 75], half=[82, 86, 65]),
    'wrist': dict(label='腕筒与金叶', direction=[1, -.05, -.5], center=[-300, 348, 72], half=[75, 80, 78]),
    'arms': dict(label='主臂与金球肘', direction=[-.5, .22, 1.5], center=[-146, 220, 21], half=[53, 108, 54]),
    'legs': dict(label='双尖盾腿甲', direction=[-.5, .18, 1.5], center=[0, 128, 0], half=[113, 137, 49]),
    'pixels': dict(label='整数格近景', direction=[-.8, .48, 1.2], center=[-18, 322, 39], half=[27, 29, 22]),
}
NOTES = ['头盔：斜口金眉下补足后颅厚度，细分眼槽、侧颊与下缘卷曲。',
         '躯干：细修肩壳弧面、肩背接缝、腿背叠片与肘腕关节。',
         '浮手：收细分节指甲，增加掌背起伏、叶形窄槽、拇指根座与分瓣腕口。',
         '原色与整数格立方体继续用于独立模型；参考图册沿用217张有效原帧。']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def materials():
    result = []
    for index, (label, color) in enumerate(COLORS):
        rgb = np.array([int(color[i:i+2], 16) for i in [1, 3, 5]])
        y, x = np.mgrid[:16, :16]
        noise = ((x*13+y*7+x*y*3) % 5)-2
        noise[(x == 0) | (y == 0)] -= 2
        noise[(x == 15) | (y == 15)] += 1
        pixels = np.clip(rgb[None, None, :]+noise[:, :, None], 0, 255).astype(np.uint8)
        png = io.BytesIO()
        Image.fromarray(pixels).save(png, format='PNG')
        texture = 'data:image/png;base64,'+base64.b64encode(png.getvalue()).decode()
        result.append(dict(id=index+1, label=label, color=color, state=f'pixel:color_{index+1}',
                           faces={face: texture for face in ['east', 'west', 'south', 'north', 'down', 'up']},
                           transparent=False, emissive=index in [7, 8]))
    return result


def prepare_viewer():
    previous = ROOT/'deliveries/0005_W11_支配人偶多角度重塑_P1_20261117'
    source = (previous/'生成脚本/viewer.mjs').read_text('utf8')
    source = source.replace('W11_VOXEL_PAYLOAD', 'DOMINION_PAYLOAD').replace('W11_READY', 'DOMINION_READY').replace('W11Viewer', 'DominionViewer')
    source = source.replace("'#202126'", "'#151922'").replace('AmbientLight(0xffffff,1.15)', 'AmbientLight(0xffffff,.85)')
    source = source.replace('DirectionalLight(0xfff5e9,1.25)', 'DirectionalLight(0xfff8ef,1.35)').replace('DirectionalLight(0xffffff,.6)', 'DirectionalLight(0xcad8ff,.4)')
    source = source.replace('emissive:info.emissive?0xffffff:0', 'emissive:info.emissive?info.color:0')
    source = source.replace('乌合之众-P1-', '乌合之众-P3-').replace("id==='all'||g.userData.modelId===id", "id==='all'||(id==='main'?g.userData.modelId!=='hands':g.userData.modelId===id)")
    source = source.replace("id==='all'?data.title:modelById.get(id).title", "id==='all'?data.title:id==='main'?'乌合之众 · 站立本体':modelById.get(id).title")
    source = source.replace("[{id:'all',title:'完整人偶'},...data.models]", "[{id:'all',title:'完整模型'},{id:'main',title:'站立本体'},...data.models]")
    (OUT/'生成脚本/viewer.mjs').write_text(source, 'utf8')
    css = (previous/'style.css').read_text('utf8')
    css += '\nheader{padding:10px 24px}header h1{font-size:22px}.ref-image{width:100%;display:block;margin:8px 0}aside h2{font-size:14px}.scope{color:#b9c4de}#features p{font-size:12px}header .eyebrow{color:#cab482}\n'
    (OUT/'style.css').write_text(css, 'utf8')
    (OUT/'index.html').write_text('''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,">
<link rel="stylesheet" href="style.css">
<title>乌合之众 · 原作细节修整 P3</title>
</head>
<body>
<header>
<div class="eyebrow">0005 / 独立原作模型 / P3</div>
<h1>乌合之众 · 原作细节修整</h1>
<p>蓝紫灰装甲 · 金色叶饰 · 红眼 · <span id="actualSize">
</span>
</p>
</header>
<main>
<section id="stage">
<div id="loading">载入整数格方块模型…</div>
<div id="legend">
<b id="modelName">
</b>
<br>左键旋转 · 右键平移 · 滚轮缩放</div>
</section>
<aside>
<section class="controls">
<div id="models" class="row">
</div>
<p id="stats">
</p>
<a class="referenceLink" href="../0005_乌合之众_原作像素重建_P2_20261117/参考图册.html" target="_blank">217张有效原帧 · 打开对照图册 ↗</a>
<p>
<a href="../0005_乌合之众_原作像素重建_P2_20261117/index.html" target="_blank">打开上一稿 P2</a>
</p>
</section>
<section class="controls">
<h2>观察视角</h2>
<div id="views" class="row">
</div>
<div class="row">
<button id="reset">完整复位</button>
<button id="screenshot">保存截图</button>
<button id="fullscreen">全屏</button>
</div>
</section>
<section class="controls">
<h2>方块剖切</h2>
<div class="slice">
<select id="axis">
<option value="y">Y 高度</option>
<option value="x">X 宽度</option>
<option value="z">Z 深度</option>
</select>
<output id="layerLabel">
</output>
</div>
<input id="layer" type="range" step="1">
<button id="fullLayer">显示全部</button>
</section>
<details open>
<summary>本轮细修与原作对照</summary>
<div id="features">
</div>
<a href="../0005_乌合之众_原作像素重建_P2_20261117/references/animation/frames/A134-153.800s.jpg" target="_blank">
<img class="ref-image" src="../0005_乌合之众_原作像素重建_P2_20261117/references/animation/frames/A134-153.800s.jpg" alt="官方动画胸肩与头盔参考">
</a>
<p>
<a href="../0005_乌合之众_原作像素重建_P2_20261117/references/animation/frames/A179-304.400s.jpg" target="_blank">头盔侧面原帧</a> · <a href="../0005_乌合之众_原作像素重建_P2_20261117/references/animation/frames/A181-305.200s.jpg" target="_blank">后颅与关节原帧</a>
</p>
</details>
<details>
<summary>原色调色板</summary>
<div id="materials">
</div>
</details>
<p class="links">
<a href="乌合之众-原色像素模型-P3.vox">原色VOX模型</a> · <a href="完整整数格模型.npz">整数格数据</a> · <a href="manifest.json">模型记录</a>
</p>
</aside>
</main>
<script src="data.js">
</script>
<script src="viewer.bundle.js">
</script>
</body>
</html>''', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT/'生成脚本').mkdir(exist_ok=True)
    palette = materials()
    parts = [*build_body(), *build_head(), *build_hands()]
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    w, h, d = map(int, high-low+1)
    keys = np.concatenate([((p.p[:, 1].astype(np.int64)-low[1])*d+p.p[:, 2]-low[2])*w+p.p[:, 0]-low[0] for p in parts])
    states = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(states)-chosen-1
    states, owners = states[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys//(w*d), keys//w % d].astype(np.int32)+low
    np.savez_compressed(OUT/'完整整数格模型.npz', xyz=xyz, states=states, owners=owners, origin=low, size=[w, h, d])
    packed, final_parts, quads = [], [], 0
    for index, part in enumerate(parts):
        current = copy(part)
        selected = owners == index
        current.p, current.states = xyz[selected], states[selected]
        item, count = mesh_part(current, palette)
        item['modelId'] = part.metadata['section']
        packed.append(item)
        final_parts.append(current)
        quads += count
        print(f'{part.label}: {len(current.p):,}格 / {count:,}面', flush=True)
    labels = dict(body='胸腹与背甲', shoulders='包覆肩壳', head='V尖头盔', arms='本体双臂', legs='双尖盾腿', hands='10只悬浮手')
    models = [dict(id=key, title=label, views=VIEWS) for key, label in labels.items()]
    data = dict(title='乌合之众 · 独立像素模型 P3', sizeXYZ=[w, h, d], bounds=dict(min=low.tolist(), max=high.tolist()), total_blocks=len(keys), models=models, views=VIEWS, design=NOTES)
    payload = base64.b64encode(gzip.compress(json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'data.js').write_text('window.DOMINION_PAYLOAD='+json.dumps(payload)+';\n', 'utf8')
    vox = OUT/'乌合之众-原色像素模型-P3.vox'
    tiles = write_vox(vox, final_parts, palette)
    manifest = dict(title=data['title'], conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', generated_at=datetime.now().astimezone().isoformat(),
                    candidate='P3', previous_candidate='P2', status='独立原作像素模型细修待审', detail_changes=NOTES,
                    size_wdh=[w, d, h], bounds_xyz=data['bounds'], blocks=len(keys), surface_quads=quads,
                    floating_hands=10, main_hands=2, colors=[dict(id=i+1, label=label, color=color) for i, (label, color) in enumerate(COLORS)],
                    components=[dict(id=p.name, label=p.label, blocks=len(p.p), metadata=p.metadata) for p in final_parts],
                    reference=dict(reviewed_candidates=414, selected_frames=217, shot_groups=30, catalogue='../0005_乌合之众_原作像素重建_P2_20261117/参考图册.html', main_source='https://www.youtube.com/watch?v=n1rjfW-5HAE'),
                    vox=dict(file=vox.name, sha256=hashlib.sha256(vox.read_bytes()).hexdigest(), scene_tiles=tiles, axes='VOX的X/Y/Z对应模型X/Z/Y'),
                    integer_cubes=True, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(OUT/'materials.json', palette)
    save(LOG/'generation.json', manifest)
    prepare_viewer()
    for name in ['package_0005_dominion_p3_20261117.py', 'dominion_p2_body.py', 'dominion_p2_head.py', 'dominion_p2_hands.py', 'dominion_p2_export.py', 'author_w05_shapes_20261115.py']:
        shutil.copyfile(Path(__file__).parent/name, OUT/'生成脚本'/name)
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), components=len(parts), vox_tiles=tiles, quads=quads)), flush=True)


if __name__ == '__main__':
    main()
