import base64
from copy import copy
from datetime import datetime
import gzip
import json
from pathlib import Path
import shutil

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w11_puppet_p1_20261117 import build, VIEWS, NOTES


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W11_支配人偶多角度重塑_P1_20261117'
SOURCE = ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117'
LOG = ROOT / 'logs/0005-w11-puppet-p1-20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    palette = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    parts = build()
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    states = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(states) - chosen - 1
    states, owners = states[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格人偶.npz', xyz=xyz, states=states, owners=owners, origin=low, size=size)
    packed, quads = [], 0
    for i, part in enumerate(parts):
        selected = owners == i
        current = copy(part)
        current.p, current.states = xyz[selected] + low, states[selected]
        item, count = mesh_part(current, palette)
        item['modelId'] = part.metadata['section']
        packed.append(item)
        quads += count
        print(f'{part.label}: {len(current.p):,}格 / {count:,}表面', flush=True)
    models = []
    labels = dict(body='躯干与分片腿甲', arms='主臂与分节五指', crown='独立悬浮掌与袖口', head='头盔与红眼')
    for group, title in labels.items():
        subset = [p for p in packed if p['modelId'] == group]
        lo = np.min([p['origin'] for p in subset], axis=0)
        hi = np.max([np.array(p['origin']) + p['size'] for p in subset], axis=0)
        models.append(dict(id=group, title=title, origin=lo.tolist(), sizeXYZ=(hi - lo).tolist(), blocks=sum(p['blocks'] for p in subset), views=VIEWS))
    data = dict(title='W11 乌合之众 · 方块人偶 P1', candidate='P1', sizeXYZ=size, bounds=dict(min=low.tolist(), max=high.tolist()), total_blocks=len(keys), models=models, views=VIEWS, design=NOTES)
    config = dict(data=data, materials=palette, parts=packed)
    payload = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W11_VOXEL_PAYLOAD=' + json.dumps(payload) + ';\n', 'utf8')
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W11-乌合之众-方块人偶-P1.nbt', 'wb', compresslevel=6) as handle:
        handle.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')
    counts = {m['state']: int((states == i + 1).sum()) for i, m in enumerate(palette) if (states == i + 1).any()}
    manifest = dict(machine='W11', candidate='P1', status='原作多角度形制重塑待审', generated_at=datetime.now().astimezone().isoformat(), actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys), surface_quads=quads, components=[dict(id=p.name, label=p.label, blocks=len(p.p), metadata=p.metadata) for p in parts], material_counts=counts, notes=NOTES, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT / 'manifest.json', manifest)
    save(OUT / 'materials.json', palette)
    save(LOG / 'generation.json', manifest)
    for name in [Path(__file__).name, 'w11_puppet_p1_20261117.py', 'w11_common_20261117.py']:
        shutil.copyfile(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
