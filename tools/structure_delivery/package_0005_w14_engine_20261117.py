import base64
from datetime import datetime, timezone
import gzip
import hashlib
from html import escape
import json
import shutil

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w14_engine_common_20261117 import ROOT, OUT, LOG, CONTROLLER, NOZZLE, materials, save
from w14_engine_body_20261117 import build as build_engine
from w14_engine_bubbles_20261117 import build as build_bubbles


NBT_NAME = 'W14-行星发动机基座-E1.nbt'


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([item['state'] for item in palette], (h, d, w), len(keys))
    with gzip.open(OUT / NBT_NAME, 'wb', compresslevel=6) as stream:
        stream.write(header)
        for offset in range(0, len(keys), 65536):
            current = keys[offset:offset + 65536]
            raw = np.tile(np.frombuffer(RECORD, np.uint8), (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[offset:offset + 65536].astype(np.int32) - 1
            stream.write(raw.tobytes())
        stream.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def reference_page():
    save(OUT / 'references/设计对应.json', dict(engine=dict(reference='MOREVFX正式发动机资产', radial_legs=7,
        overall_diameter=1249, design_height=331, emitter_reference_diameter=395,
        elements=['七辐装甲斜腿与拱洞', '中央开口叠层筒', '顶部密集竖鳍', '七组出挑机械臂', '喷口径向叶片', '连续圆坝与竖肋']),
        adaptation=['原作米制尺寸按比例转为方块', '内部布置为格雷科技检修面板与模组WSV月华紫细带',
                    '世界泡、进料桥与喷流联动为HK3GTL设计，原作没有该组世界泡', '本次为W14下层候选，上层轮回主体待后续融合']))
    images = sorted((OUT / 'references').glob('[0-9][0-9]-*'))
    figures = ''.join(f'<figure><a href="references/{escape(p.name)}"><img src="references/{escape(p.name)}" loading="lazy"></a><figcaption>{escape(p.stem)}</figcaption></figure>' for p in images)
    (OUT / 'references.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W14行星发动机原作参考</title><style>body{{background:#14202d;color:#e4ebf5;font:15px/1.7 system-ui;margin:24px}}a{{color:#c3b0f4}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px}}figure{{margin:0}}img{{width:100%}}</style><h1>W14 行星发动机参考</h1><p>24张制作方资产、过程与成片图，包含同视角制作阶段，完整来源见清单。</p><p><a href="index.html">方块模型</a> · <a href="references/sources.json">图片来源</a> · <a href="references/设计对应.json">形体对应</a> · <a href="https://www.morevfx.com/showcase/%E6%B5%81%E6%B5%AA%E5%9C%B0%E7%90%83/">MOREVFX制作方原文</a></p><main>{figures}</main></html>''', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    palette = materials()
    save(OUT / 'materials.json', palette)
    parts = build_engine()
    bubbles, bubble_info = build_bubbles()
    parts += bubbles
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    values = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    source_blocks = len(keys)
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    del chosen
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    del xyz
    save(OUT / 'world-bubbles.json', bubble_info)
    counts = np.bincount(owners, minlength=len(parts))
    packed, components, quads = [], [], 0
    for index, part in enumerate(parts):
        current = owners == index
        selected = keys[current]
        part.p = np.c_[selected % w, selected // (w * d), selected // w % d].astype(np.int32) + low
        part.states = values[current]
        item, count = mesh_part(part, palette)
        item['modelId'] = part.metadata['group']
        packed.append(item)
        quads += count
        components.append(dict(id=part.name, label=part.label, group=part.metadata['group'], blocks=int(counts[index]),
                               bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist())))
        print(f'外露方块面 {index + 1}/{len(parts)} {part.name}: {count:,}', flush=True)
    models = [dict(id='engine', label='行星发动机', views={}, features=['七条放射状斜腿、镂空桁架与大拱洞', '中央叠层开口发射器、84组竖鳍与七组出挑机械臂',
                  '连续圆形坝体与196道竖肋；前侧圆坝为唯一主控检修位置', '真实整数格与原生GT、模组像素贴图']),
              dict(id='bubbles', label='七类世界泡', views={}, features=['森林、海洋、冰原、沙漠、火山、结晶与荒原遗迹', '透明背半球、可见内景与悬托约束环',
                  '世界泡为供料视觉候选，实际世界泡生命周期沿用现行生产规则']),
              dict(id='feed', label='进料桥与托座', views={}, features=['七条进料桥沿斜腿间隙连接外坝', '支架托座连接世界泡与坝体，运行粒子向中心汇聚'])]
    data = dict(title='W14 行星发动机基座', candidate='E1', nbt_file=NBT_NAME, bounds=dict(min=low.tolist(), max=high.tolist()),
                sizeXYZ=size, blocks=len(keys), models=models, effects=dict(nozzle=NOZZLE, bubble_centers=[b['center'] for b in bubble_info]),
                views=dict(pixels=dict(label='像素细节', center=[0, 184, 316], half=[23, 23, 23], direction=[-.7, .6, 1.3]),
                           controller=dict(label='主控位置', center=CONTROLLER, half=[46, 33, 50], direction=[-.6, .6, 1.3]),
                           leg=dict(label='斜腿桁架', center=[0, 130, 375], half=[100, 80, 130], direction=[-1, .4, .6])))
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W14_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    print('导出完整静态方块NBT', flush=True)
    nbt(keys, values, size, palette)
    save(OUT / 'geometry.json', dict(components=components, surface_quads=quads, bounds=data['bounds']))
    save(OUT / 'manifest.json', dict(machine='W14', candidate='E1', state='下层模块外观待审', generated_at=datetime.now(timezone.utc).isoformat(),
        actual_size_wdh=[w, d, h], blocks=len(keys), source_component_blocks=source_blocks, components=len(parts), surface_quads=quads,
        controller=dict(source=CONTROLLER, normalized=(np.array(CONTROLLER) - low).tolist(), facing='south', policy='仅主控固定，其余实体格可换合法接口'),
        engine_reference=dict(diameter_blocks=1249, height_blocks=331, radial_legs=7, source='MOREVFX正式制作资产'), world_bubbles=bubble_info,
        material_counts=[dict(state=m['state'], label=m['label'], blocks=int((values == i + 1).sum())) for i, m in enumerate(palette)],
        nbt=dict(file=NBT_NAME, bytes=(OUT / NBT_NAME).stat().st_size, sha256=digest(OUT / NBT_NAME)),
        scope='行星发动机下层与外围供料世界泡候选；上层轮回主体待后续融合，喷流与供料运动为网页特效演示'))
    reference_page()
    for path in [*ROOT.joinpath('tools/structure_delivery').glob('*w14_engine*20261117*')]:
        shutil.copy2(path, OUT / '生成脚本' / path.name)
    save(LOG / 'generation.json', dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), components=len(parts), quads=quads))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads)))


if __name__ == '__main__':
    main()
