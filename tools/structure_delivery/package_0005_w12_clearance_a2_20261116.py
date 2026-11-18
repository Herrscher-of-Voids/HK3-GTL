import base64
from copy import copy
from datetime import datetime
import gzip
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from package_0005_w12_author_blueprint_20261116 import digest, mesh_part, save
import w12_core_a2_20261116 as core
import w12_adjacent_a2_20261116 as adjacent


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'deliveries/0005_W12_作者蓝图原案_A1_20261116'
OUT = ROOT / 'deliveries/0005_W12_三环分层扩腔_A2_20261116'
LOG = ROOT / 'logs/0005-w12-clearance-a2-20261116'


def export_nbt(keys, states, size, materials):
    w, h, d = size
    header, _ = headers([m['state'] for m in materials], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / 'W12-全域能量约束壁-A2.nbt', 'wb', compresslevel=6) as handle:
        handle.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            handle.write(raw.tobytes())
        handle.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    old = json.loads((OLD / 'geometry.json').read_text('utf8'))
    materials = json.loads((OLD / 'materials.json').read_text('utf8'))
    source = np.load(OLD / '原案构件数据.npz')
    parts = [SimpleNamespace(name=name, label=item['label'], metadata=item['metadata'],
        p=source[name + '_xyz'], states=source[name + '_materials']) for name, item in old['components'].items()]
    current, notes = core.build()
    neighbors, neighbor_notes = adjacent.build()
    replacements = {p.name: p for p in current + neighbors}
    parts = [replacements.get(p.name, p) for p in parts]
    notes += neighbor_notes
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    all_states = np.concatenate([p.states for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(all_states) - chosen - 1
    states = all_states[chosen]
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])[chosen]
    del all_states, chosen
    archive, packed, quads = {}, [], 0
    for index, part in enumerate(parts):
        archive[part.name + '_xyz'], archive[part.name + '_materials'] = part.p, part.states
        current_keys = keys[owners == index]
        visible = copy(part)
        visible.p = np.c_[current_keys % w, current_keys // (w * d), current_keys // w % d].astype(np.int32) + low
        visible.states = states[owners == index]
        item, count = mesh_part(visible, materials)
        item['source_blocks'] = len(part.p)
        packed.append(item)
        quads += count
        print(f'表面 {index + 1}/{len(parts)} {part.name} {count:,}', flush=True)
    old_payload = (OLD / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';\n')
    data = json.loads(gzip.decompress(base64.b64decode(json.loads(old_payload))))['data']
    data.update(candidate='A2', sizeXYZ=size, size=size, bounds=dict(min=low.tolist(), max=high.tolist()),
        blueprint_to_export_offset_xyz=(-low).tolist())
    data['views']['coreClose'] = dict(label='三环分层近景', direction=[-.85, .62, -1.2], center=[531, 180, 423], half=[64, 64, 64])
    data['views']['coreFront'] = dict(label='核心正面', direction=[0, .001, -1], center=[531, 180, 423], half=[105, 130, 100])
    spears = replacements['twelve_binding_lances'].metadata
    data['effects']['lance_directions'] = spears['beam_directions']
    data['effects']['lance_energy_radii'] = [spears['beam_inner_radius'], spears['beam_outer_radius']]
    counts = {m['state']: int((states == i + 1).sum()) for i, m in enumerate(materials)}
    mod_count = sum(v for k, v in counts.items() if not k.startswith('minecraft:'))
    geometry = dict(old, candidate='A2', stage='三环分层扩腔方块候选待审', actual_size_xyz=size,
        actual_size_wdh=[w, d, h], bounds=data['bounds'], blocks=len(keys), footprint_area=w * d,
        bounding_box_volume=w * d * h, actual_height=h, unique_block_types=len(np.unique(states)),
        source_component_blocks=sum(len(p.p) for p in parts), overlap_extra_memberships=sum(len(p.p) for p in parts) - len(keys),
        surface_quads=quads, material_counts=counts, non_vanilla_blocks=mod_count, non_vanilla_percent=100 * mod_count / len(keys),
        components={p.name: dict(label=p.label, blocks=len(p.p), bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist()), metadata=p.metadata) for p in parts},
        source_notes=notes, parent_candidate=str(OLD.relative_to(ROOT)), changed_components=list(replacements))
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads, blocks=len(keys)), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W12_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    np.savez_compressed(OUT / '修订构件数据.npz', **archive)
    export_nbt(keys, states, size, materials)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    shutil.copy2(OLD / 'materials.json', OUT / 'materials.json')
    shutil.copy2(OLD / '原文.txt', OUT / '原文.txt')
    save(OUT / 'changes.json', dict(candidate='A2', decision='保留三环转动，分层半径并扩大核心空腔', notes=notes,
        pending=['双长廊中央静态交叠与完整汇合设计', '锁链中段相交及穿长廊', '冠环与四内塔、垂丝与墙塔', '占地递增仍比W10少240格']))
    for name in [Path(__file__).name, 'w12_core_a2_20261116.py', 'w12_adjacent_a2_20261116.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    save(OUT / 'manifest.json', dict(machine='W12', candidate='A2', updated_at=datetime.now().astimezone().isoformat(),
        status='三环分层扩腔方块候选待审', actual_size_wdh=[w, d, h], blocks=len(keys)))
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads)), flush=True)


if __name__ == '__main__':
    main()
