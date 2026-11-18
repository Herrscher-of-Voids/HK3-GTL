import base64
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from package_0005_w14_engine_20261117 import digest
from w14_engine_common_e2_20261117 import ROOT, OUT, LOG, E1, CONTROLLER, NOZZLE, materials, save
from w14_engine_dimensions_e2_20261117 import build as build_dimensions


NBT_NAME = 'W14-行星发动机维度基座-E2.nbt'


def engine():
    with np.load(E1 / '完整整数格模型.npz') as source:
        xyz, values, owners = source['xyz'] + source['origin'], source['states'], source['owners']
    components = json.loads((E1 / 'geometry.json').read_text('utf8'))['components']
    return [SimpleNamespace(name=item['id'], label=item['label'], metadata=dict(group='engine'),
                p=xyz[owners == index], states=values[owners == index])
            for index, item in enumerate(components) if item['group'] == 'engine']


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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    palette = materials()
    save(OUT / 'materials.json', palette)
    parts = engine()
    print('沿用E1七辐发动机整数格', flush=True)
    dimensions, dimension_info = build_dimensions()
    parts += dimensions
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
    save(OUT / 'dimensions.json', dimension_info)
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
    models = [
        dict(id='engine', label='行星发动机', views={}, features=['E1七辐斜腿、开口叠层喷嘴及圆坝', 'GT灰黑金属、蓝色管线与WSV淡紫细带', '唯一主控沿用正面圆坝检修台']),
        dict(id='dimensions', label='七个维度球', views={}, features=['主世界、末地、地狱、月球、火星、金星、银河系', '维度球分别与同方向的地貌扇区对应', '七球为维度供料的视觉候选']),
        dict(id='sectors', label='七扇区地貌', views={}, features=['七条腿之间覆盖对应维度地貌', '地形从底盘顶面接起，边缘避让装甲斜腿', '主世界植被水域、末地黑曜石柱与地狱熔岩', '月面环坑、火星红土、金星岩脊云带及立体银河旋臂']),
        dict(id='feed', label='维度供料连接', views={}, features=['七条供料桥与七组托座', '运行时粒子向喷口汇聚']),
    ]
    data = dict(title='W14 行星发动机维度基座', candidate='E2', nbt_file=NBT_NAME,
        bounds=dict(min=low.tolist(), max=high.tolist()), sizeXYZ=size, blocks=len(keys), models=models,
        effects=dict(nozzle=NOZZLE, bubble_centers=[b['center'] for b in dimension_info]),
        views=dict(pixels=dict(label='像素细节', center=[0, 184, 316], half=[23, 23, 23], direction=[-.7, .6, 1.3]),
                   controller=dict(label='主控位置', center=CONTROLLER, half=[46, 33, 50], direction=[-.6, .6, 1.3]),
                   leg=dict(label='斜腿桁架', center=[0, 130, 375], half=[100, 80, 130], direction=[-1, .4, .6])))
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W14_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    print('导出完整静态方块NBT', flush=True)
    nbt(keys, values, size, palette)
    save(OUT / 'geometry.json', dict(components=components, surface_quads=quads, bounds=data['bounds']))
    save(OUT / 'manifest.json', dict(machine='W14', candidate='E2', state='下层模块外观待审', generated_at=datetime.now(timezone.utc).isoformat(),
        actual_size_wdh=[w, d, h], blocks=len(keys), source_component_blocks=source_blocks, components=len(parts), surface_quads=quads,
        controller=dict(source=CONTROLLER, normalized=(np.array(CONTROLLER) - low).tolist(), facing='south', policy='仅主控固定，其余实体格可换合法接口'),
        dimensions=dimension_info, material_counts=[dict(state=m['state'], label=m['label'], blocks=int((values == i + 1).sum())) for i, m in enumerate(palette)],
        nbt=dict(file=NBT_NAME, bytes=(OUT / NBT_NAME).stat().st_size, sha256=digest(OUT / NBT_NAME)),
        scope='W14下层候选：七维度球、七扇区地貌与火箭尾焰网页演示；上层主体待融合，实际维度与生产规则未修改'))
    relative = '../' + E1.name + '/references.html'
    (OUT / 'references.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>W14参考</title><body><h1>行星发动机原作参考</h1><p><a href="{relative}">沿用E1的24张制作参考与来源</a></p><p>七维度球与扇区地貌为本项目方块设计；月球、火星、金星为艺术化维度景观，银河采用缩微旋臂星海。</p><a href="index.html">返回E2</a></body></html>', 'utf8')
    scripts = [Path(__file__), ROOT / 'tools/structure_delivery/w14_engine_common_20261117.py',
        ROOT / 'tools/structure_delivery/w14_engine_common_e2_20261117.py', ROOT / 'tools/structure_delivery/w14_engine_dimensions_e2_20261117.py']
    for path in scripts:
        shutil.copy2(path, OUT / '生成脚本' / path.name)
    save(LOG / 'generation.json', dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), components=len(parts), quads=quads))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads)))


if __name__ == '__main__':
    main()
