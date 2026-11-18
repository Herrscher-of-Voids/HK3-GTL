from pathlib import Path
from types import SimpleNamespace
import base64
import gzip
import json
import re
import shutil
import struct

import numpy as np
from PIL import Image
from i34_open_observatory_export_20261027 import RECORD_DTYPE, _headers, digest, exact

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/remove-fixed-ports-r266-20261113'
PORT = 'hk3gtl:industrial_port_casing'
POLICY = '实体建筑位置由玩家自行选择通用接口，主控制器与空气除外；无默认接口位置。'


def load(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def payload(path):
    encoded = json.loads(path.read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    return json.loads(gzip.decompress(base64.b64decode(encoded)))


def restore_w03():
    resource = ROOT / 'src/main/resources/data/hk3gtl/structures/w03_c9.bin.gz'
    texture = ROOT / 'src/main/resources/assets/hk3gtl/textures/effect/w03_c9_atlas.png'
    before = LOG / 'before-w03'
    before.mkdir(exist_ok=True)
    for path in (resource, texture):
        if not (before / path.name).exists():shutil.copy2(path, before / path.name)
    data = gzip.decompress((before / resource.name).read_bytes())
    header = struct.unpack('>9iH', data[:38])
    cursor, states = 38, []
    for _ in range(header[-1]):
        length = struct.unpack_from('>H', data, cursor)[0]
        cursor += 2
        states.append(data[cursor:cursor + length].decode())
        cursor += length
    records = np.frombuffer(bytearray(data[cursor:]), dtype=[
        ('index', '>i4'), ('dy', '>i4'), ('length', '>i4'), ('state', '>u2'), ('delta', '>i4')])
    old = states.index(PORT)
    selected = records['state'] == old
    restored = int(records['length'][selected].sum())
    records['state'][selected] = states.index('gtceu:black_large_metal_sheet')
    records['state'][records['state'] > old] -= 1
    states.pop(old)
    with gzip.open(resource, 'wb', compresslevel=9) as target:
        target.write(struct.pack('>9iH', *header[:-1], len(states)))
        for state in states:
            encoded = state.encode()
            target.write(struct.pack('>H', len(encoded)) + encoded)
        target.write(records.tobytes())
    source = ROOT / 'deliveries/W03_C9_C5外环下移净空修订_20261108'
    model = payload(source / 'w03/data.js')
    materials = [material['state'] for material in model['materials']]
    old_slot = materials.index(PORT) * 6
    new_slot = materials.index('gtceu:black_large_metal_sheet') * 6
    atlas = Image.open(texture).convert('RGBA')
    edge = atlas.width // 16
    for face in range(6):
        source_slot, target_slot = new_slot + face, old_slot + face
        sx, sy = source_slot % 16 * edge, source_slot // 16 * edge
        atlas.paste(atlas.crop((sx, sy, sx + edge, sy + edge)),
                    (target_slot % 16 * edge, target_slot // 16 * edge))
    atlas.save(texture, optimize=True)
    return dict(restored_blocks=restored, restored_state='gtceu:black_large_metal_sheet',
                controller=list(header[5:8]), block_count=header[8], palette_count=len(states),
                mask_geometry_unchanged=True, fx_geometry_unchanged=True, fx_atlas_faces_replaced=6,
                resource_sha256=digest(resource), atlas_sha256=digest(texture),
                source_candidate=str(source.relative_to(ROOT)), game_verified=False)


def migrate_exports(source, output, old_name, name, old_states, states, lut, size, count):
    width, height, depth = size
    old_headers = _headers(old_states, (height, depth, width), count)
    headers = _headers(states, (height, depth, width), count)
    counts = np.zeros(len(states), np.int64)
    source_hashes = {}
    for extension, old_header, header in zip(('nbt', 'schem'), old_headers, headers):
        original_path = next(source.rglob(f'{old_name}.{extension}'))
        source_hashes[extension] = digest(original_path)
        remaining = count if extension == 'nbt' else width * height * depth
        step = 262144 if extension == 'nbt' else 1048576
        with gzip.open(original_path, 'rb') as original, gzip.open(output / f'{name}.{extension}', 'wb', compresslevel=6) as target:
            exact(original, len(old_header))
            target.write(header)
            for start in range(0, remaining, step):
                n = min(step, remaining - start)
                if extension == 'nbt':
                    raw = bytearray(exact(original, n * RECORD_DTYPE.itemsize))
                    records = np.frombuffer(raw, dtype=RECORD_DTYPE)
                    records['state'] = lut[records['state']]
                    counts += np.bincount(records['state'], minlength=len(states))
                    target.write(raw)
                else:
                    values = np.frombuffer(exact(original, n), dtype=np.uint8)
                    schem_lut = np.concatenate(([0], lut + 1)).astype(np.uint8)
                    target.write(schem_lut[values].tobytes())
            target.write(original.read())
        print(output.name, extension, flush=True)
    return counts, source_hashes


def migrate_candidate(folder, key, restored_state):
    source = ROOT / 'deliveries' / folder
    output = LOG / key
    output.mkdir(exist_ok=True)
    manifest = load(source / 'manifest.json')
    model = payload(source / 'data.js')
    old_states = [material['state'] for material in model['materials']]
    states = list(dict.fromkeys(restored_state if state == PORT else state for state in old_states))
    lut = np.array([states.index(restored_state if state == PORT else state) for state in old_states])
    size = model['data']['size']
    old_name = manifest['name']
    name = old_name + '-freeports-r266'
    original_bom = load(source / '材料清单.json')
    count = sum(item['count'] for item in original_bom)
    restored = next(item['count'] for item in original_bom if item['state'] == PORT)
    counts, source_hashes = migrate_exports(source, output, old_name, name, old_states, states, lut, size, count)
    by_state = {material['state']: material for material in model['materials']}
    model['materials'] = [by_state[state] for state in states]
    for part in model['parts']:
        for field in ('starts', 'lengths'):
            groups = [[[] for _ in range(6)] for _ in states]
            for old, faces in enumerate(part[field]):
                for face, values in enumerate(faces):
                    groups[lut[old]][face].extend(values)
            part[field] = groups
    model['data'].update(name=name, ports=[], interface_policy=POLICY)
    note = '主控保留原占位；' + POLICY
    if key == 'w05':
        model['data']['source_conflicts'] = [item for item in model['data']['source_conflicts'] if 'industrial_port_casing' not in item] + [note]
    model['audit'].update(interface_count=0, game_verified=False)
    model['audit']['source_audit_only'] = True
    encoded = base64.b64encode(gzip.compress(json.dumps(model, ensure_ascii=False, separators=(',', ':')).encode(), 6)).decode()
    (output / 'data.js').write_text(f'window.{key.upper()}_STATIC_PAYLOAD=' + json.dumps(encoded) + ';', 'utf8')
    bom = [dict(state=state, count=int(n)) for state, n in zip(states, counts)]
    save(output / '材料清单.json', bom)
    manifest.update(name=name, source_candidate=str(source.relative_to(ROOT)), ports=[], ports_world=[],
                    interface_policy=POLICY, fixed_port_replacements=dict(count=restored, state=restored_state),
                    palette_count=len(states), game_verified=False, installed=False)
    if key == 'w04':
        manifest['materials']['states'] = states
        manifest['known_issues'][0] = 'W04正式控制器尚未注册；' + note
        metadata = load(source / 'review-ui.json')
        labels = {item['state']: item['label'] for item in metadata['materials']}
        metadata['materials'] = [dict(**row, label=labels[row['state']]) for row in bom]
        metadata['candidate'] = 'W04 P4 · 旧接口恢复 R266'
        save(output / 'review-ui.json', metadata)
        html = (source / '三维布局.html').read_text('utf8')
        html = re.sub(r'(<script id="reviewMetadata" type="application/json">).*?(</script>)',
                      lambda match: match[1] + json.dumps(metadata, ensure_ascii=False) + match[2], html, flags=re.S)
        html = html.replace('同平面3×3周围8接口；尚未注册为游戏控制器。', note)
        html = html.replace('定位主控与接口', '定位主控').replace('接口定位框', '主控定位框')
        html = html.replace(load(source / 'manifest.json')['known_issues'][0], manifest['known_issues'][0])
        html = html.replace('P4仅更新现存HRV材质与八处通用接口', 'R266将旧接口恢复为HRV机壳')
        page = '三维布局.html'
    else:
        from package_w05_wind_circuit_a1_20261112 import review_page
        manifest['source_conflicts'] = model['data']['source_conflicts']
        html = review_page(model['data'], [SimpleNamespace(name=part['id']) for part in model['parts']],
                           [dict(**row, role='恢复原建筑方块' if row['state'] == restored_state else '') for row in bom])
        page = '三维评审.html'
    (output / page).write_text(html, 'utf8')
    shutil.copy2(source / 'viewer.bundle.js', output / 'viewer.bundle.js')
    save(output / 'manifest.json', manifest)
    result = dict(source_candidate=str(source.relative_to(ROOT)), source_export_sha256=source_hashes,
                  restored_blocks=restored, restored_state=restored_state, size_xyz=size, block_count=count,
                  palette_count=len(states), controller=model['data']['controller'], default_port_count=0,
                  coordinates_unchanged=True, animation_unchanged=True, historical_deliveries_unmodified=True,
                  game_verified=False, interface_policy=POLICY, review=str((output / page).relative_to(ROOT)),
                  export_sha256={suffix: digest(output / f'{name}.{suffix}') for suffix in ('nbt', 'schem')})
    save(output / 'revision.json', result)
    save(output / 'verification.json', dict(**result, scope='原导出记录的材质迁移；历史验收不转记为本次新验收。', gui_test_performed=False))
    (output / 'index.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{key.upper()} 旧接口恢复 R266</title><h1>{key.upper()} 旧接口恢复 R266</h1><p>{restored}格旧接口恢复为{restored_state}。{POLICY}</p><p>建筑坐标、主控、实体总数及动画保持；未进行游戏验收。</p><p><a href="{page}">原界面三维预览</a> · <a href="manifest.json">候选记录</a> · <a href="revision.json">变更来源</a> · <a href="{name}.nbt">NBT</a> · <a href="{name}.schem">Schematic</a></p></html>', 'utf8')
    return result


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    result = dict(w03=restore_w03())
    result['w04'] = migrate_candidate('W04_现存材质与通用接口_P4_20261112', 'w04', 'hk3gtl:voltage_machine_casing_hrv')
    result['w05'] = migrate_candidate('W05_长风理想流体环流阵_双层回流_A1_20261112', 'w05', 'minecraft:black_concrete')
    save(LOG / 'wonder-restoration.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
