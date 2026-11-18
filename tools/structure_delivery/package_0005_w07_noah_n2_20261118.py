import base64
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import shutil

import numpy as np

from package_0005_w07_noah_n1_20261118 import digest, mesh_part
from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from w07_ark_common_20261118 import ROOT, Part, DARK, CLEAN, SILVER, LIGHT, CONTROL, deck_at, materials, save
from w07_ark_hull_20261118 import hull
from w07_ark_decks_20261118 import build as decks


OUT = ROOT / 'deliveries/0005_W07_无底座扩大方舟_N2_20261118'
LOG = ROOT / 'logs/0005-w07-noah-n2-20261118'
NBT_NAME = 'W07-无底座扩大方舟-N2.nbt'
PLATFORM_Y = deck_at(444) + 1
CONTROLLER = (np.array([0, PLATFORM_Y + 1, 430]) * 5 // 4).tolist()
GROUPS = [('hull_dark', '凋亡黑船壳'), ('hull_white', '创生白船壳'), ('spine', '共用龙骨肋架'),
    ('deck_dark', '破损黑甲板'), ('deck_white', '完整白甲板'), ('life', '生命舱与种植槽'), ('machinery', '分解再造设备')]


def enlarge(part):
    low = part.p * 5 // 4
    extent = (part.p + 1) * 5 // 4 - low
    points, states = [], []
    for x in range(2):
        for y in range(2):
            for z in range(2):
                delta = np.array([x, y, z])
                selected = np.all(extent > delta, axis=1)
                points.append(low[selected] + delta)
                states.append(part.states[selected])
    part.p, part.states = np.concatenate(points), np.concatenate(states)
    return part


def bow_platform():
    part = Part('bow_controller_deck', '船首甲板主控踏面', group='spine')
    for z in range(410, 445):
        part.box([-23, deck_at(z), z], [-1, PLATFORM_Y, z], DARK)
        part.box([1, deck_at(z), z], [23, PLATFORM_Y, z], CLEAN)
        part.box([0, deck_at(z), z], [0, PLATFORM_Y, z], SILVER)
    for x in [-22, 22]:
        part.box([x, PLATFORM_Y, 416], [x, PLATFORM_Y, 437], LIGHT)
    return enlarge(part.finish())


def export_nbt(keys, states, size, palette):
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
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    palette = materials()
    save(OUT / 'materials.json', palette)
    print('生成独立方舟并按整数格扩大25%', flush=True)
    parts = [enlarge(part) for part in hull() + decks()]
    platform = bow_platform()
    platform.p = np.vstack([platform.p, CONTROLLER])
    platform.states = np.r_[platform.states, np.uint8(CONTROL)]
    parts.append(platform)
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
    baseline = json.loads((ROOT / 'deliveries/0005_W07_黑白生息方舟_N1_20261118/manifest.json').read_text('utf8'))
    features = {
        'hull_dark': ['船体按整数格扩大25%，黑侧三处破口露出肋架', '已移除全部外部底座、斜撑及承托座'],
        'hull_white': ['白侧完整装甲、银灰板缝与连续舷窗'],
        'spine': ['黑白两舷共用龙骨及横肋', '唯一主控候选位置移至船首甲板中央'],
        'deck_dark': ['黑侧三层船屋、半毁坡顶与破损甲板'],
        'deck_white': ['白侧三层完整船屋，船首与船尾上翘'],
        'life': ['五座白框玻璃生命舱及完整树冠、白花种植槽'],
        'machinery': ['船腹分解与再制造设备，黑白粒子为网页运行示意']}
    old_data = json.loads(gzip.decompress(base64.b64decode(json.loads((ROOT / 'deliveries/0005_W07_黑白生息方舟_N1_20261118/data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';')))))['data']
    views = old_data['views']
    for view in views.values():
        view['center'] = [value * 1.25 for value in view['center']]
        view['half'] = [value * 1.25 for value in view['half']]
    views['oblique'].update(center=[0, 209, 26], half=[260, 174, 670])
    views['controller'].update(center=CONTROLLER, half=[54, 37, 69])
    data = dict(title='W07 无底座黑白生息方舟', candidate='N2', nbt_file=NBT_NAME,
        bounds=dict(min=low.tolist(), max=high.tolist()), sizeXYZ=size, blocks=len(keys),
        models=[dict(id=key, label=label, views={}, features=features[key]) for key, label in GROUPS],
        effects=dict(center=[0, 200, 0]), views=views)
    payload = json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode()
    (OUT / 'data.js').write_text('window.W07_VOXEL_PAYLOAD=' + json.dumps(base64.b64encode(gzip.compress(payload, compresslevel=6)).decode()) + ';\n', 'utf8')
    print('导出扩大方舟完整NBT', flush=True)
    export_nbt(keys, values, size, palette)
    save(OUT / 'geometry.json', dict(components=components, surface_quads=quads, bounds=data['bounds']))
    source_names = [Path(__file__).name, 'w07_ark_common_20261118.py', 'w07_ark_hull_20261118.py', 'w07_ark_decks_20261118.py']
    sources = []
    for name in source_names:
        source = ROOT / 'tools/structure_delivery' / name
        shutil.copy2(source, scripts / name)
        sources.append(dict(path=str(source.relative_to(ROOT)), sha256=digest(source)))
    manifest = dict(machine='W07', candidate='N2', state='外观待审', generated_at=datetime.now(timezone.utc).isoformat(),
        actual_size_wdh=[w, d, h], blocks=len(keys), source_component_blocks=source_blocks,
        components=len(parts), surface_quads=quads, source_files=sources, scale_xyz=[1.25, 1.25, 1.25],
        external_base=False, removed_components=['工业干船坞', '底部框架', '外部斜撑', '承托座', '坞侧落板'],
        previous_candidate=dict(candidate='N1', size_with_dock_wdh=baseline['actual_size_wdh']),
        controller=dict(source=CONTROLLER, normalized=(np.array(CONTROLLER) - low).tolist(), facing='south', policy='船首甲板唯一主控，其余实体格可换合法接口'),
        material_counts=[dict(state=material['state'], label=material['label'], blocks=int((values == index + 1).sum())) for index, material in enumerate(palette)],
        entities=dict(count=0), nbt=dict(file=NBT_NAME, bytes=(OUT / NBT_NAME).stat().st_size, sha256=digest(OUT / NBT_NAME)),
        scope='移除外部底座、船体真实整数格扩大25%；独立外观候选，网页粒子为运行示意',
        appearance_approved=False, game_code_modified=False, jar_built=False, installed=False)
    save(OUT / 'manifest.json', manifest)
    save(LOG / 'generation.json', dict(output=str(OUT), size_wdh=[w, d, h], blocks=len(keys), components=len(parts), quads=quads))
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), parts=len(parts), quads=quads, controller=CONTROLLER)))


if __name__ == '__main__':
    main()
