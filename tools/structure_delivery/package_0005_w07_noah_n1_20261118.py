import base64
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import struct

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import mesh_part
from w07_ark_common_20261118 import ROOT, OUT, LOG, CONTROLLER, materials, save
from w07_ark_hull_20261118 import hull, dock
from w07_ark_decks_20261118 import build as decks


NBT_NAME = 'W07-黑白生息方舟-N1.nbt'
GROUPS = [('dock', '工业干船坞'), ('hull_dark', '凋亡黑船壳'), ('hull_white', '创生白船壳'),
    ('spine', '共用龙骨肋架'), ('deck_dark', '破损黑甲板'), ('deck_white', '完整白甲板'),
    ('life', '生命舱与种植槽'), ('machinery', '分解再造设备')]


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            sha.update(block)
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
        stream.write(tag(9, 'entities') + b'\x0a' + struct.pack('>i', 0) + b'\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    palette = materials()
    save(OUT / 'materials.json', palette)
    print('生成黑白船壳、共用龙骨及干船坞', flush=True)
    parts = hull() + dock()
    print('生成三层船屋、生命舱及船腹设备', flush=True)
    parts += decks()
    low = np.min([part.p.min(0) for part in parts], axis=0)
    high = np.max([part.p.max(0) for part in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((part.p[:, 1].astype(np.int64) - low[1]) * d + part.p[:, 2] - low[2]) * w + part.p[:, 0] - low[0] for part in parts])
    values = np.concatenate([part.states for part in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(part.p) for part in parts])
    source_blocks = len(keys)
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(values) - chosen - 1
    values, owners = values[chosen], owners[chosen]
    del chosen
    xyz = np.c_[keys % w, keys // (w * d), keys // w % d].astype(np.int32)
    np.savez_compressed(OUT / '完整整数格模型.npz', xyz=xyz, states=values, origin=low, size=size, owners=owners)
    del xyz
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
        components.append(dict(id=part.name, label=part.label, group=part.metadata['group'], blocks=len(selected),
            bounds=dict(min=part.p.min(0).tolist(), max=part.p.max(0).tolist())))
        print(f'外露方块面 {index + 1}/{len(parts)} {part.name}: {count:,}', flush=True)
    features = {
        'dock': ['两侧工业干船坞与横向承托架', '前方中央操作台保留唯一主控位置'],
        'hull_dark': ['黑色分段船壳，三处大破口露出肋架', '外部裂口与甲板缺损共同表现凋亡'],
        'hull_white': ['完整白色分段装甲、银灰板缝与连续舷窗'],
        'spine': ['黑白两舷共用龙骨与对应横肋，中轴灯线贯穿船体'],
        'deck_dark': ['黑色船屋与半毁阶梯屋顶', '船体固定，黑色碎屑为网页运行示意'],
        'deck_white': ['三层完整船屋，白装甲与银灰边框', '船首抬高，船腹保持深吃水轮廓'],
        'life': ['白框玻璃温室、完整树冠与白花种植槽'],
        'machinery': ['船腹分选、分解与再制造设备，对应W07有损物质再生工艺']}
    data = dict(title='W07 黑白双舷诺亚方舟', candidate='N1', nbt_file=NBT_NAME,
        bounds=dict(min=low.tolist(), max=high.tolist()), sizeXYZ=size, blocks=len(keys),
        models=[dict(id=key, label=label, views={}, features=features[key]) for key, label in GROUPS],
        effects=dict(center=[0, 160, 0]),
        views=dict(oblique=dict(label='黑白双舷全景', center=[0, 130, 20], half=[300, 175, 580], direction=[-.78, .95, 1.25]),
            dark_breach=dict(label='黑舷大破口', center=[-126, 140, -12], half=[126, 100, 195], direction=[-1, .48, .45]),
            greenhouse=dict(label='白舷生命舱', center=[138, 210, -2], half=[79, 51, 207], direction=[1, .6, .75]),
            pixels=dict(label='像素近景', center=[-168, 163, 118], half=[19, 18, 25], direction=[-1, .48, .8]),
            controller=dict(label='主控候选位置', center=CONTROLLER, half=[65, 48, 76], direction=[-.7, .8, 1.3])))
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W07_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    print('导出完整整数格NBT', flush=True)
    nbt(keys, values, size, palette)
    save(OUT / 'geometry.json', dict(components=components, surface_quads=quads, bounds=data['bounds']))
    source_names = [Path(__file__).name, 'w07_ark_common_20261118.py', 'w07_ark_hull_20261118.py', 'w07_ark_decks_20261118.py']
    sources = []
    for name in source_names:
        source = ROOT / 'tools/structure_delivery' / name
        shutil.copy2(source, scripts / name)
        sources.append(dict(path=str(source.relative_to(ROOT)), sha256=digest(source)))
    manifest = dict(machine='W07', candidate='N1', state='外观待审', generated_at=datetime.now(timezone.utc).isoformat(),
        actual_size_wdh=[w, d, h], blocks=len(keys), source_component_blocks=source_blocks,
        components=len(parts), surface_quads=quads, source_files=sources,
        controller=dict(source=CONTROLLER, normalized=(np.array(CONTROLLER) - low).tolist(), facing='south', policy='仅主控固定，其余实体格可换合法接口'),
        material_counts=[dict(state=material['state'], label=material['label'], blocks=int((values == index + 1).sum())) for index, material in enumerate(palette)],
        entities=dict(count=0), nbt=dict(file=NBT_NAME, bytes=(OUT / NBT_NAME).stat().st_size, sha256=digest(OUT / NBT_NAME)),
        scope='黑白双舷诺亚方舟独立外观候选；真实整数格与像素贴图，网页粒子为运行示意',
        appearance_approved=False, game_code_modified=False, jar_built=False, installed=False)
    save(OUT / 'manifest.json', manifest)
    save(LOG / 'generation.json', dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), components=len(parts), quads=quads))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads)))


if __name__ == '__main__':
    main()
