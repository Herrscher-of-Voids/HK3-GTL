import base64
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

from theatre_t1_model import GT, MC


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'deliveries/0005_支配剧场_四指向前撑墙_F5_20261117'
LOG = ROOT/'logs/0005-w11-f5-production-20261117'
FACES = ('east', 'west', 'south', 'north', 'down', 'up')
MACHINE = 'hk3gtl:w11_distributed_industrial_command'


def material(state, png, label, entry, emissive=False):
    url = 'data:image/png;base64,'+base64.b64encode(png).decode()
    return dict(state=state, label=label, faces=dict.fromkeys(FACES, url), transparent=False,
                emissive=emissive, color='#ffffff', source=dict(entry=entry, texture_mode='原生像素贴图'))


def average(item):
    png = base64.b64decode(item['faces']['south'].split(',')[1])
    return np.asarray(Image.open(BytesIO(png)).convert('RGB')).reshape(-1, 3).mean(0)


def load_materials():
    theatre = json.loads((ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117/materials.json').read_text('utf8'))
    actors = json.loads((SOURCE/'演员色板.json').read_text('utf8'))
    candidates = {m['state']: deepcopy(m) for m in theatre if not m['transparent'] and not m['emissive']}
    for state, file in [('gtceu:black_metal_sheet', 'metalsheet_black'), ('gtceu:black_studs', 'studs_black'),
                        ('gtceu:gray_metal_sheet', 'metalsheet_gray'), ('gtceu:bronze_gearbox', None)]:
        for path in (ROOT/'deliveries').glob('*/materials.json'):
            values = json.loads(path.read_text('utf8'))
            found = next((m for m in values if m.get('state') == state), None) if isinstance(values, list) else None
            if found:
                candidates[state] = found
                break
    colors = ('white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
              'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black')
    with ZipFile(MC) as archive:
        names = [color+'_'+kind for kind in ('concrete', 'terracotta') for color in colors]
        names += ['obsidian', 'raw_iron_block', 'gold_block', 'iron_block', 'bone_block_side',
                  'quartz_block_side', 'sandstone_top', 'deepslate_tiles', 'polished_blackstone_bricks']
        states = dict(bone_block_side='bone_block[axis=y]', quartz_block_side='quartz_block', sandstone_top='smooth_sandstone')
        for name in names:
            entry = 'assets/minecraft/textures/block/'+name+'.png'
            state = 'minecraft:'+states.get(name, name)
            candidates[state] = material(state, archive.read(entry), name, entry)
    for color in colors:
        path = ROOT/f'src/main/resources/assets/hk3gtl/textures/block/casings/casing_colored_{color}.png'
        state = 'hk3gtl:casing_colored_'+color
        candidates[state] = material(state, path.read_bytes(), color+'色机壳', str(path.relative_to(ROOT)))
    with ZipFile(GT) as archive:
        entry = 'assets/gtceu/textures/block/lamps/red_borderless.png'
        state = 'gtceu:red_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]'
        candidates[state] = material(state, archive.read(entry), '红色无框工业灯', entry, True)
    major = ['minecraft:obsidian', 'minecraft:gray_concrete', 'minecraft:blue_terracotta',
             'minecraft:light_blue_terracotta', 'minecraft:smooth_sandstone', 'minecraft:raw_iron_block',
             'gtceu:bronze_gearbox', 'hk3gtl:casing_colored_red', state, 'gtceu:black_studs']
    choices = [m for m in candidates.values() if not m['emissive']]
    means = np.array([average(m) for m in choices])
    selected = major.copy()
    for item in actors[10:]:
        rgb = np.array([int(item['color'][k:k+2], 16) for k in (1, 3, 5)])
        selected.append(choices[int(np.argmin(np.sum((means-rgb)**2, axis=1)))]['state'])
    materials = deepcopy(theatre)
    lookup = {m['state']: i+1 for i, m in enumerate(materials)}
    mapping, records = [0], []
    for original, state in zip(actors, selected):
        if state not in lookup:
            lookup[state] = len(materials)+1
            materials.append(deepcopy(candidates[state]))
        mapping.append(lookup[state])
        records.append(dict(source_id=original['id'], source_color=original['color'], source_state=original['state'],
                            state=state, palette_index=lookup[state]-1,
                            texture_average_rgb=np.rint(average(candidates[state])).astype(int).tolist()))
    return materials, np.array(mapping, np.uint8), records


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    materials, mapping, records = load_materials()
    for name, value in [('materials.json', materials), ('actor-material-map.json', records)]:
        (LOG/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(dict(materials=len(materials), with_controller=len(materials)+1,
                         actors=len(set(mapping[1:].tolist())), mapping=str(LOG/'actor-material-map.json')), ensure_ascii=False))


if __name__ == '__main__':
    main()
