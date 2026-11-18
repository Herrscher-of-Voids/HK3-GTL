import base64
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

import numpy as np

from package_0005_i37_suspended_test_dock_a2_20261115 import RECORD, RECORD_DTYPE, headers


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W10_引力奇点刑架_作者蓝图_A1_20261116'
OUT = ROOT / 'deliveries/0005_W10_引力奇点刑架_工业材质_A2_20261116'
LOG = ROOT / 'logs/0005-w10-material-a2-20261116'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def gt_material(candidate):
    with ZipFile(candidate['jar']) as archive:
        png = archive.read(candidate['texture'])
    properties = candidate['properties']
    state = candidate['id'] + ('[' + ','.join(f'{k}={v}' for k, v in properties.items()) + ']' if properties else '')
    texture = 'data:image/png;base64,' + base64.b64encode(png).decode()
    return dict(state=state, label=candidate['label'], role=candidate['role'],
        faces={face: texture for face in ('east', 'west', 'south', 'north', 'down', 'up')},
        transparent=False, emissive='lamp' in candidate['id'],
        source=dict(archive=candidate['jar'], entry=candidate['texture'], png_sha256=candidate['png_sha256'],
                    model=candidate.get('selected_model', candidate['model']),
                    emissive_entry=candidate.get('emissive_png'), texture_mode='原生像素贴图，无额外染色'))


def hk_black():
    path = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/casings/casing_colored_black.png'
    png = path.read_bytes()
    texture = 'data:image/png;base64,' + base64.b64encode(png).decode()
    return dict(state='hk3gtl:casing_colored_black', label='黑色机壳', role='深黑主装甲',
        faces={face: texture for face in ('east', 'west', 'south', 'north', 'down', 'up')},
        transparent=False, emissive=False,
        source=dict(file=str(path), png_sha256=hashlib.sha256(png).hexdigest(),
            model='assets/hk3gtl/models/block/casing/casing_colored_black.json',
            registration='src/main/java/com/sirin/hk3gtl/common/block/CasingBlocks.java', texture_mode='原生像素贴图，无额外染色'))


def export_nbt(config, old_materials, materials):
    data = config['data']
    w, h, d = data['sizeXYZ']
    block_count = config['audit']['blocks']
    old_header, _ = headers([m['state'] for m in old_materials], (h, d, w), block_count)
    header, _ = headers([m['state'] for m in materials], (h, d, w), block_count)
    offset = data['blueprint_to_export_offset_xyz']
    changed = 0
    with gzip.open(SOURCE / 'W10-引力奇点刑架-A1.nbt', 'rb') as source, gzip.open(OUT / 'W10-引力奇点刑架-A2.nbt', 'wb', compresslevel=6) as target:
        source.read(len(old_header))
        target.write(header)
        for start in range(0, block_count, 65536):
            count = min(65536, block_count - start)
            raw = bytearray(source.read(count * len(RECORD)))
            rows = np.frombuffer(raw, RECORD_DTYPE)
            x, y, z = rows['x'] - offset[0], rows['y'] - offset[1], rows['z'] - offset[2]
            void = (x * x + (y - 222) ** 2 + z * z <= 625) | ((y == 0) & (x * x + z * z <= 576))
            selected = (rows['state'] == 0) & ~void
            rows['state'][selected] = 12
            changed += int(selected.sum())
            target.write(raw)
        shutil.copyfileobj(source, target)
    return changed


def main():
    encoded = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';\n'))
    config = json.loads(gzip.decompress(base64.b64decode(encoded)))
    old_materials = deepcopy(config['materials'])
    materials = config['materials']
    candidates = json.loads((LOG / 'gt-candidates.json').read_text('utf8'))
    choices = {c['id']: c for c in candidates['candidates']}
    replacements = {1: 'gtceu:black_studs', 5: 'gtceu:yellow_borderless_lamp', 11: 'gtceu:white_lamp'}
    for index, state in replacements.items():
        materials[index] = gt_material(choices[state])
    materials.append(hk_black())

    for part in config['parts']:
        for key in ('starts', 'lengths', 'spans'):
            part[key].append([[] for _ in range(6)])
            if part['metadata'].get('visual') != 'void':
                part[key][-1], part[key][0] = part[key][0], [[] for _ in range(6)]
    config['data']['candidate'] = 'A2'
    config['data']['stage'] = '工业材质方块预览待审'
    config['data']['material_revision'] = '保留A1全部几何及黑金、冷白、琥珀、紫黑配色'
    converted = export_nbt(config, old_materials, materials)
    payload = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT / 'data.js').write_text('window.W10_STATIC_PAYLOAD=' + json.dumps(payload) + ';\n', 'utf8')
    save(OUT / 'materials.json', materials)

    source_archive = np.load(SOURCE / '原案构件数据.npz')
    archive = {}
    void_names = {p['id'] for p in config['parts'] if p['metadata'].get('visual') == 'void'}
    for name in source_archive.files:
        values = source_archive[name]
        if name.endswith('_materials') and name[:-10] not in void_names:
            values[values == 1] = 13
        archive[name] = values
    np.savez_compressed(OUT / '工业材质构件数据.npz', **archive)

    geometry = json.loads((SOURCE / 'geometry.json').read_text('utf8'))
    old_counts = [geometry['material_counts'][m['state']] for m in old_materials]
    counts = [*old_counts, converted]
    counts[0] -= converted
    swaps = [dict(from_state=old_materials[i]['state'], to_state=materials[i]['state'], blocks=counts[i]) for i in replacements]
    swaps.append(dict(from_state=old_materials[0]['state'], to_state=materials[12]['state'], blocks=converted, scope='排除纯黑奇点及井底虚空面'))
    note = 'A2保留A1全部整数坐标、62构件、合并表面、运动与特效。主黑甲换HK黑色机壳，黑石砖换GT黑色铆钉板，金色线圈光源换GT无框黄灯，白热视界光源换GT白灯；黄金、琥珀介质及紫黄红玻璃沿用A1，纯黑奇点和井底继续使用黑色混凝土。'
    geometry.update(candidate='A2', stage='工业材质方块预览待审', unique_block_types=13,
        material_counts={m['state']: n for m, n in zip(materials, counts)},
        material_replacements=swaps, geometry_source=str(SOURCE / 'geometry.json'), geometry_positions_modified=False,
        non_vanilla_blocks=sum(n for m, n in zip(materials, counts) if not m['state'].startswith('minecraft:')))
    geometry['source_notes'].append(note)
    geometry['source_notes'].append('GT灯采用bloom=true,inverted=true,lit=true,powered=false，无红石时发光15；灯块的真实红石行为遵循GTCEu已有规则。')
    save(OUT / 'geometry.json', geometry)
    save(LOG / 'generation.json', geometry)
    save(OUT / '材质替换.json', dict(replacements=swaps, preserved_colors=['黑金', '冷白', '琥珀', '紫黑'], new_registered_blocks=0, new_textures=0))
    conflicts = json.loads((SOURCE / 'conflicts.json').read_text('utf8'))
    conflicts['notes'].append(note)
    save(OUT / 'conflicts.json', conflicts)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    files = ['data.js', 'materials.json', 'geometry.json', 'conflicts.json', '材质替换.json', '工业材质构件数据.npz', 'W10-引力奇点刑架-A2.nbt']
    save(OUT / 'manifest.json', dict(machine='W10', candidate='A2', status='工业材质预览与NBT，外观待审',
        actual_size_wdh=geometry['actual_size_wdh'], blocks=geometry['blocks'],
        files={name: dict(bytes=(OUT / name).stat().st_size, sha256=hashlib.sha256((OUT / name).read_bytes()).hexdigest()) for name in files}))
    print(json.dumps(dict(blocks=geometry['blocks'], converted_black_armor=converted, material_types=13,
        non_vanilla_blocks=geometry['non_vanilla_blocks'], replacements=swaps), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
