import base64
from copy import copy
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_t1_model import ANCHORS, MODEL_NOTES, VIEWS, build_model


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_原作方块搭建_T1_20261117'
LOG = ROOT/'logs/0005-theatre-t1-20261117'
LABELS = dict(floor='红毯与大厅地面', stairs='双侧楼梯', walls='厅壁与金框立柱',
              window='金框圆窗', roof='顶部与悬吊框架', front='前端围护')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_nbt(keys, states, size, palette):
    w, h, d = size
    header, _ = headers([m['state'] for m in palette], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    path = OUT/'支配剧场-剧情大厅-T1.nbt'
    with gzip.open(path, 'wb', compresslevel=6) as handle:
        handle.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start+65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current//(w*d), current//w % d
            rows['state'] = states[start:start+65536].astype(np.int32)-1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities')+b'\x0a\x00\x00\x00\x00\x00')
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    scripts = OUT/'生成脚本'
    scripts.mkdir(exist_ok=True)
    parts, palette = build_model()
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high-low+1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64)-low[1])*d+p.p[:, 2]-low[2])*w+p.p[:, 0]-low[0] for p in parts])
    states = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(states)-chosen-1
    states, owners = states[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys//(w*d), keys//w % d].astype(np.int32)+low
    np.savez_compressed(OUT/'完整整数格模型.npz', xyz=xyz, states=states, owners=owners, origin=low, size=size)
    packed, components, quads = [], [], 0
    for index, part in enumerate(parts):
        selected = owners == index
        current = copy(part)
        current.p, current.states = xyz[selected], states[selected]
        item, count = mesh_part(current, palette)
        item['modelId'] = part.metadata['section']
        packed.append(item)
        components.append(dict(id=part.name, label=part.label, blocks=int(selected.sum()), metadata=part.metadata))
        quads += count
        print(f'{part.label}: {int(selected.sum()):,}格，{count:,}面', flush=True)
    sections = dict.fromkeys(p.metadata['section'] for p in parts)
    models = [dict(id=section, title=LABELS[section]) for section in sections]
    data = dict(title='支配剧场 · 剧情大厅 T1', candidate='T1', sizeXYZ=size,
                bounds=dict(min=low.tolist(), max=high.tolist()), total_blocks=len(keys),
                models=models, views=VIEWS, design=MODEL_NOTES)
    payload = base64.b64encode(gzip.compress(json.dumps(dict(data=data, materials=palette, parts=packed),
                                 ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'data.js').write_text('window.THEATRE_PAYLOAD='+json.dumps(payload)+';\n', 'utf8')
    save(OUT/'materials.json', palette)
    save(OUT/'锚点.json', dict(coordinates='X宽、Y高、+Z正面；使用模型世界坐标', anchors=ANCHORS))
    nbt = export_nbt(keys, states, size, palette)
    source = Path(__file__).parent
    shutil.copyfile(source/'theatre_t1_index.html', OUT/'index.html')
    shutil.copyfile(source/'theatre_t1_viewer.mjs', scripts/'viewer.mjs')
    shutil.copyfile(ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117/style.css', OUT/'style.css')
    for path in [*source.glob('theatre_t1*.py'), source/'theatre_t1_index.html',
                 source/'theatre_t1_viewer.mjs', source/'package_0005_theatre_t1_20261117.py',
                 source/'preview_0005_theatre_t1_20261117.mjs']:
        shutil.copyfile(path, scripts/path.name)
    files = ['data.js', 'materials.json', '完整整数格模型.npz', '锚点.json', nbt.name,
             'index.html', 'style.css', '生成脚本/viewer.mjs']
    manifest = dict(title=data['title'], conversation='0005',
                    conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
                    generated_at=datetime.now(timezone.utc).isoformat(), candidate='T1',
                    status='独立剧情剧场方块模型待审', size_wdh=[w, d, h], bounds_xyz=data['bounds'],
                    blocks=len(keys), surface_quads=quads, components=components,
                    material_counts={m['state']: int((states == i+1).sum()) for i, m in enumerate(palette)},
                    notes=MODEL_NOTES, views=VIEWS, anchors='锚点.json',
                    reference_catalogue='references/scene/index.html',
                    integer_cubes=True, coordinates='NPZ为模型世界坐标；NBT坐标为模型坐标减bounds.min；+Z正面',
                    nbt=nbt.name, actors_included=False, animation=False,
                    appearance_approved=False, formal_machine_modified=False, jar_built=False,
                    files={name: dict(bytes=(OUT/name).stat().st_size, sha256=digest(OUT/name)) for name in files})
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    print(json.dumps(dict(out=str(OUT), size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
