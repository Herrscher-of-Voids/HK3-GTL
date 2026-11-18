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
from w08_sword_reactor_20261116 import STAR_CENTER, star_ring


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W08_随机日珥_橙色恒星_A3_20261116'
ORIGINAL = ROOT / 'deliveries/0005_W08_薪炎恒星熔铸炉_作者蓝图_A1_20261116'
OUT = ROOT / 'deliveries/0005_W08_三环分层扩径_A4_20261116'
LOG = ROOT / 'logs/0005-w08-star-a4-20261116'
NBT_NAME = 'W08-恒星核心-A4.nbt'


def save(file, data):
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def cube_envelope(part):
    delta = part.p - STAR_CENTER
    near = np.maximum(np.maximum(delta, -delta - 1), 0)
    far = np.maximum(abs(delta), abs(delta + 1))
    return dict(min=float(np.linalg.norm(near, axis=1).min()), max=float(np.linalg.norm(far, axis=1).max()))


def effect_mask(part):
    axis = int(np.argmax(abs(np.array(part.metadata['motion_axis']))))
    plane = [i for i in range(3) if i != axis]
    delta = part.p - STAR_CENTER
    near = np.maximum(np.maximum(delta, -delta - 1), 0)
    far = np.maximum(abs(delta), abs(delta + 1))
    return dict(radial_min=float(np.linalg.norm(near[:, plane], axis=1).min()),
                radial_max=float(np.linalg.norm(far[:, plane], axis=1).max()),
                axial_min=float(delta[:, axis].min()), axial_max=float(delta[:, axis].max() + 1))


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
    OUT.mkdir(exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    LOG.mkdir(exist_ok=True)
    previous = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    archive = np.load(SOURCE / '恒星核心构件数据.npz')
    materials = json.loads((SOURCE / 'materials.json').read_text('utf8'))
    old_materials = json.loads((ORIGINAL / 'materials.json').read_text('utf8'))
    material_ids = {item['state']: i + 1 for i, item in enumerate(materials)}
    ring_mapping = np.zeros(len(old_materials) + 1, np.uint8)
    for i in (1, 2, 3, 8):
        ring_mapping[i] = material_ids[old_materials[i - 1]['state']]
    name = 'star_compressed_supergiant'
    info = previous['components'][name]
    star = SimpleNamespace(name=name, label=info['label'], metadata=dict(info['metadata']),
                           p=archive[name + '_xyz'], states=archive[name + '_materials'])
    parts = [star]
    for index, offset in enumerate((8, 56, 104)):
        ring = star_ring(index, offset)
        ring.states = ring_mapping[ring.states]
        ring.metadata.update(radial_offset=offset, effect_mask=effect_mask(ring))
        parts.append(ring)
    for index in range(36):
        name = f'star_dimension_fragment_{index + 1:02d}'
        info = previous['components'][name]
        angle = (index % 12) * np.pi / 6 + (index // 12) * .19
        latitude = [-.62, .04, .66][index // 12]
        normal = np.array([np.cos(latitude) * np.cos(angle), np.sin(latitude), np.cos(latitude) * np.sin(angle)])
        shift = np.rint(116 * normal).astype(np.int32)
        metadata = dict(info['metadata'], previous_center_radius=140, center_radius=256,
                        translation_xyz=shift.tolist(), translation_rule='沿原球面法线整体平移116格，整数平移量四舍五入。')
        parts.append(SimpleNamespace(name=name, label=info['label'], metadata=metadata,
                                     p=archive[name + '_xyz'] + shift, states=archive[name + '_materials']))
    archive.close()
    envelopes = {part.name: cube_envelope(part) for part in parts}
    fragment_min = min(envelopes[part.name]['min'] for part in parts[4:])
    gaps = dict(star_to_inner_ring=envelopes[parts[1].name]['min'] - envelopes[star.name]['max'],
                inner_to_middle_ring=envelopes[parts[2].name]['min'] - envelopes[parts[1].name]['max'],
                middle_to_outer_ring=envelopes[parts[3].name]['min'] - envelopes[parts[2].name]['max'],
                outer_ring_to_fragments=fragment_min - envelopes[parts[3].name]['max'])
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
    packed, arrays, quads = [], {}, 0
    for index, part in enumerate(parts):
        arrays[part.name + '_xyz'], arrays[part.name + '_materials'] = part.p, part.states
        item, count = mesh_part(part, materials)
        packed.append(item)
        quads += count
        print(f'{index + 1}/{len(parts)} {part.name} {count:,}', flush=True)
    raw = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';\n'))
    old_payload = json.loads(gzip.decompress(base64.b64decode(raw)))
    data = dict(old_payload['data'], candidate='A4', size=size, bounds=dict(min=low.tolist(), max=high.tolist()),
                blueprint_to_export_offset_xyz=(-low).tolist(), ring_outer_radii=[128, 176, 224],
                fragment_center_radius=256, clearance_spherical_shells=gaps)
    config = dict(data=data, audit=dict(viewer_rendered_quads=quads), materials=materials, parts=packed)
    encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode())).decode()
    (OUT / 'data.js').write_text('window.W08_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
    save(OUT / 'materials.json', materials)
    np.savez_compressed(OUT / '恒星核心构件数据.npz', **arrays)
    export_nbt(keys, states, size, materials)
    geometry = dict(candidate='A4', stage='三道拘束环分层扩径与外围维度片外移',
                    actual_size_xyz=size, actual_size_wdh=[w, d, h], bounds=data['bounds'],
                    blocks=len(keys), source_component_blocks=sum(counts), overlap_extra_memberships=sum(counts) - len(keys),
                    surface_quads=quads, star_nominal_diameter=180,
                    star_actual_size_xyz=previous['star_actual_size_xyz'], star_unchanged_from='A3逐格复制太阳坐标和材料',
                    replaced_black_blocks=previous['replaced_black_blocks'], replaced_dark_red_blocks=previous['replaced_dark_red_blocks'],
                    ring_outer_radii=[128, 176, 224], ring_radial_offsets=[8, 56, 104], fragment_center_radius=256,
                    radial_measurement='相对中心(489,150,460)测量每个完整单位立方体的最小/最大欧氏半径；刚体绕中心旋转保持此半径包络。',
                    component_cube_radial_envelopes=envelopes, clearance_spherical_shells=gaps,
                    components={p.name: dict(label=p.label, blocks=len(p.p), metadata=p.metadata,
                                            cube_radial_envelope=envelopes[p.name],
                                            bounds=dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist())) for p in parts},
                    materials=[m['state'] for m in materials], controller_blueprint=None, interface_rule=data['interface_rule'],
                    prominence=previous['prominence'], w07_status='负责人叫停，继续停止',
                    appearance_approved=False, game_code_modified=False, game_resources_modified=False,
                    instance_access=False, jar_built=False, installed=False, game_verified=False)
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / '径向净空.json', dict(component_cube_radial_envelopes=envelopes, clearance_spherical_shells=gaps,
                                   requested_minimum=dict(star_to_inner_ring=8, inner_to_middle_ring=4,
                                                          middle_to_outer_ring=4, outer_ring_to_fragments=12)))
    decision = dict(direction='太阳保持，三环整体分层扩径；外围维度片整体外移。',
                    star='A3橙色太阳逐格复制，名义直径180、完整181格，内部热层保持。',
                    rings='三环主环外半径128/176/224；全部喷头、冷却管、白金结构与外徽记同向径向外移8/56/104，截面厚度和材料保持。',
                    fragments='36片维度片按原球面法线整体外移116格，中心名义半径140→256；每片平移向量四舍五入到整数格，形状、材料、朝向保持。',
                    clearance=gaps, controller='当前不增加定位格，最终主控位置待后续设计，全实体自由接口规则保持。',
                    effects='保留A3随机表面触发日珥；太阳表面出生点、方向、寿命和间隔随机，三环运动仍绕各自法线，粒子局部避让由预览器处理。',
                    export='NBT及NPZ仅含完整实体构件，真实负Y完整导出，预览效果另行处理。')
    save(OUT / '修改记录.json', decision)
    for name in [Path(__file__).name, 'w08_sword_reactor_20261116.py', 'w08_common_20261116.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(size_wdh=[w, d, h], bounds=data['bounds'], parts=len(parts), blocks=len(keys), quads=quads,
                          clearance=gaps, overlap_extra_memberships=sum(counts) - len(keys),
                          nbt_sha256=hashlib.sha256((OUT / NBT_NAME).read_bytes()).hexdigest())), flush=True)


if __name__ == '__main__':
    main()
