import base64
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np

from package_0005_w08_author_blueprint_20261116 import mesh_part
from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers, tag
from w08_sword_reactor_20261116 import star_body


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W08_薪炎恒星熔铸炉_作者蓝图_A1_20261116'
OUT = ROOT / 'deliveries/0005_W08_恒星核心放大_日珥特效_A2_20261116'
LOG = ROOT / 'logs/0005-w08-star-a2-20261116'
NBT_NAME = 'W08-恒星核心-A2.nbt'


def save(file, data):
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def export_nbt(keys, states, size, materials):
    w, h, d = size
    header, _ = headers([m['state'] for m in materials], (h, d, w), len(keys))
    record = np.frombuffer(RECORD, np.uint8)
    with gzip.open(OUT / NBT_NAME, 'wb', compresslevel=6) as file:
        file.write(header)
        for start in range(0, len(keys), 65536):
            current = keys[start:start + 65536]
            raw = np.tile(record, (len(current), 1))
            rows = raw.view(RECORD_DTYPE).reshape(-1)
            rows['x'], rows['y'], rows['z'] = current % w, current // (w * d), current // w % d
            rows['state'] = states[start:start + 65536].astype(np.int32) - 1
            file.write(raw.tobytes())
        file.write(tag(9, 'entities') + b'\x0a\x00\x00\x00\x00\x00')


def main():
    previous = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    archive = np.load(SOURCE / '原案构件数据.npz')
    star = star_body(90)
    star.metadata['source'] = '负责人2026-11-16要求只保留恒星核心并放大恒星本体。'
    parts = [star]
    kept = []
    for name, info in previous['components'].items():
        if name.startswith('star_ring_') or name.startswith('star_dimension_fragment_'):
            parts.append(SimpleNamespace(name=name, label=info['label'], metadata=info['metadata'],
                                         p=archive[name + '_xyz'], states=archive[name + '_materials']))
            kept.append(name)
    archive.close()
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    size = (high - low + 1).tolist()
    w, h, d = size
    counts = [len(p.p) for p in parts]
    all_keys = np.concatenate([((p.p[:, 1].astype(np.int64) - low[1]) * d + p.p[:, 2] - low[2]) * w + p.p[:, 0] - low[0] for p in parts])
    all_states = np.concatenate([p.states for p in parts])
    keys, chosen = np.unique(all_keys[::-1], return_index=True)
    chosen = len(all_states) - chosen - 1
    states = all_states[chosen]
    del all_keys, all_states, chosen
    used = np.unique(states)
    mapping = np.zeros(len(materials) + 1, np.uint8)
    mapping[used] = np.arange(1, len(used) + 1)
    materials = [materials[int(i) - 1] for i in used]
    states = mapping[states]
    packed, arrays, quads = [], {}, 0
    for index, part in enumerate(parts):
        part.states = mapping[part.states]
        arrays[part.name + '_xyz'], arrays[part.name + '_materials'] = part.p, part.states
        item, count = mesh_part(part, materials)
        packed.append(item)
        quads += count
        print(f'{index + 1}/{len(parts)} {part.name} {count:,}', flush=True)
    v = lambda label, direction, **options: dict(label=label, direction=direction, **options)
    views = dict(front=v('整体斜视', [-.8, .55, -1.2]), right=v('反侧斜视', [1, .6, -.9]),
                 orthofront=v('正面', [0, .001, -1]), side=v('侧面', [1, .001, 0]),
                 back=v('背面', [.8, .55, 1.2]), top=v('俯视', [0, 1, .001]),
                 star=v('恒星本体', [-.65, .4, -1.2], center=[489, 150, 460], half=[100, 100, 100]),
                 corona=v('日珥特效', [-.8, .5, -1.2], center=[489, 150, 460], half=[152, 152, 152]),
                 blocks=v('逐格近景', [-.8, .4, -1.1], center=[458, 150, 375], half=[10, 10, 10]))
    data = dict(machine_id='W08', title='劫焰·恒星核心', candidate='A2', size=size,
                bounds=dict(min=low.tolist(), max=high.tolist()), blueprint_to_export_offset_xyz=(-low).tolist(),
                controller_blueprint=None, star_center=[489, 150, 460], star_radius=90, corona_radius=150,
                views=views, runtime_voltage='CIV', research='RN-SFF',
                interface_rule='主控最终位置待后续确定；其他全部实体方块可自由替换合法通用接口并自选朝向。')
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode())).decode()
    (OUT / 'data.js').write_text('window.W08_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    save(OUT / 'materials.json', materials)
    np.savez_compressed(OUT / '恒星核心构件数据.npz', **arrays)
    export_nbt(keys, states, size, materials)
    geometry = dict(candidate='A2', stage='按负责人截图删件、恒星放大与日珥特效预览',
                    actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'],
                    blocks=len(keys), source_component_blocks=sum(counts), overlap_extra_memberships=sum(counts) - len(keys),
                    surface_quads=quads, star_nominal_diameter=180, previous_star_nominal_diameter=160,
                    star_actual_size_xyz=(star.p.max(0) - star.p.min(0) + 1).tolist(), star_scale=1.125,
                    unchanged_components=kept, removed_components=[name for name in previous['components'] if name not in kept and name != star.name],
                    components={p.name: dict(label=p.label, blocks=len(p.p), metadata=p.metadata,
                                            bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist())) for p in parts},
                    materials=[m['state'] for m in materials], controller_blueprint=None, interface_rule=data['interface_rule'],
                    prominence=dict(representation='纯粒子特效，未作为实体方块导出', count=12, radial_extension=60),
                    appearance_approved=False, game_code_modified=False, game_resources_modified=False,
                    instance_access=False, jar_built=False, installed=False, game_verified=False)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    decision = dict(direction='只保留截图中的恒星、三道拘束环和外围碎片；恒星放大，日珥改特效，舰桥删除。',
                    star_diameter='名义160→180，增大12.5%；球面端点完整保留，实际181格。',
                    preserved='39个环与碎片直接复用A1原始构件数据，位置、材料与形状保持。',
                    removed='巨剑、翼披风、浮游炮、全部底盘和注入槽、圣堂舰桥、原主控定位及12条实体日珥。',
                    controller='原舰桥主控随构件删除，最终位置后续设计；当前候选不加入新的定位格。',
                    scale='此版遵循负责人删件方向；正式电压规模递增仍待后续设计，不以旧底盘空气范围冒充当前尺寸。',
                    effects='12条卷曲流动日珥为网页粒子特效，NBT及NPZ只包含实体恒星、三环和外围碎片。')
    save(OUT / '修改记录.json', decision)
    for name in [Path(__file__).name, 'w08_sword_reactor_20261116.py', 'w08_common_20261116.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(size_wdh=[w, d, h], parts=len(parts), blocks=len(keys), quads=quads,
                          nbt_sha256=hashlib.sha256((OUT / NBT_NAME).read_bytes()).hexdigest())), flush=True)


if __name__ == '__main__':
    main()
