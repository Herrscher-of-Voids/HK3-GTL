import base64
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_f1_actors import build_actors


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_提线共演_F1_20261117'
LOG = ROOT/'logs/0005-theatre-f1-20261117'
THEATRE = ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    scripts = OUT/'生成脚本'
    scripts.mkdir(exist_ok=True)
    parts, palette, rig = build_actors()
    packed, components, archive, quads = [], [], {}, 0
    for part in parts:
        item, count = mesh_part(part, palette)
        packed.append(item)
        archive[part.name+'_xyz'] = part.p
        archive[part.name+'_materials'] = part.states
        components.append(dict(id=part.name, label=part.label, blocks=len(part.p), metadata=part.metadata))
        quads += count
        print(f'{part.name}: {len(part.p):,}格，{count:,}面', flush=True)
    np.savez_compressed(OUT/'演员整数格构件.npz', **archive)
    atlas = Image.new('RGB', (192, 192))
    for i, material in enumerate(palette):
        source = Image.open(io.BytesIO(base64.b64decode(material['faces']['south'].split(',')[1])))
        atlas.paste(source, (i % 12*16, i//12*16))
    png = io.BytesIO()
    atlas.save(png, format='PNG')
    texture = 'data:image/png;base64,'+base64.b64encode(png.getvalue()).decode()
    payload = dict(parts=packed, materials=palette, rig=rig, atlas=texture, atlas_columns=12)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'actors.js').write_text('window.ACTOR_PAYLOAD='+json.dumps(encoded)+';\n', 'utf8')
    save(OUT/'提线骨架.json', rig)
    save(OUT/'演员色板.json', palette)
    source = Path(__file__).parent
    shutil.copyfile(source/'theatre_f1_index.html', OUT/'index.html')
    shutil.copyfile(THEATRE/'style.css', OUT/'style.css')
    for name in ['theatre_f1_viewer.mjs', 'theatre_f1_animation.mjs', 'theatre_f1_actors.py',
                 'theatre_f1_index.html', 'package_0005_theatre_f1_20261117.py', 'preview_0005_theatre_f1_20261117.mjs']:
        shutil.copyfile(source/name, scripts/name)
    theatre = json.loads((THEATRE/'manifest.json').read_text('utf8'))
    counts = {actor: sum(len(p.p) for p in parts if p.metadata['actor'] == actor) for actor in ('dominion', 'puppet')}
    manifest = dict(title='支配剧场 · 提线共演 F1', candidate='F1', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', generated_at=datetime.now(timezone.utc).isoformat(),
        theatre='../'+THEATRE.name+'/manifest.json', theatre_data_sha256=hashlib.sha256((THEATRE/'data.js').read_bytes()).hexdigest(),
        size_wdh=theatre['size_wdh'], theatre_blocks=theatre['blocks'], actor_blocks={**counts, 'puppet_instances': 2},
        actor_surface_quads=quads, components=components, rig=rig,
        notes=['T2剧情大厅中轴放置P3乌合之众，F03与F08悬浮手各牵引一只D2剧情版千人人偶。',
               '演员按0.68与0.25重新采样为整数格；所有立方体边长仍为一格。动画绕关节旋转体素构件。',
               '指尖连接头顶、双腕与双膝，共十条金色提线；人偶动作由对应手势延迟0.18秒驱动。',
               '演员pixel:*为原模型预览色板；真实方块映射、W11正式结构与游戏动画接入另行制作。'],
        animation=True, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    print(json.dumps(dict(out=str(OUT), counts=counts, quads=quads)), flush=True)


if __name__ == '__main__':
    main()
