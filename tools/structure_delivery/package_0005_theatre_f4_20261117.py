import base64
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

from theatre_f4_actors import SOURCE, build_actors


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_向内搭手_F4_20261117'
LOG = ROOT/'logs/0005-theatre-f4-20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    scripts = OUT/'生成脚本'
    scripts.mkdir(exist_ok=True)
    parts, palette, rig, archive, atlas = build_actors()
    np.savez_compressed(OUT/'演员整数格构件.npz', **archive)
    payload = dict(parts=parts, materials=palette, rig=rig, atlas=atlas)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'actors.js').write_text('window.ACTOR_PAYLOAD='+json.dumps(encoded)+';\n', 'utf8')
    save(OUT/'提线骨架.json', rig)
    for name in ['theatre.js', 'style.css', '演员色板.json', '整数格展开.json', '建筑改造.json', '剧情动作依据.json']:
        shutil.copyfile(SOURCE/name, OUT/name)
    source = Path(__file__).parent
    shutil.copyfile(source/'theatre_f4_index.html', OUT/'index.html')
    names = ['theatre_f4_actors.py', 'theatre_f4_viewer.mjs', 'theatre_f4_giant.mjs',
        'theatre_f4_animation.mjs', 'theatre_f4_index.html', 'package_0005_theatre_f4_20261117.py',
        'preview_0005_theatre_f4_20261117.mjs']
    for name in names:
        shutil.copyfile(source/name, scripts/name)
    original = json.loads((SOURCE/'manifest.json').read_text('utf8'))
    manifest = dict(title='支配剧场 · 向内搭手 F4', candidate='F4', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        generated_at=datetime.now(timezone.utc).isoformat(), source=str(SOURCE),
        theatre=original['theatre'], actor_blocks={actor: sum(p['blocks'] for p in parts if p['metadata']['actor']==actor)
            for actor in ['dominion', 'puppet']}, rig=rig,
        geometry_changes=dict(wrist_targets=[[-516, 671, 80], [516, 671, 80]],
            palm_contact_y=619, inner_roof_edge=390,
            finger_source_ceiling='源Y≥110的接触区最大体素Z为51；越过内缘后按源Y下扣，完整保留指节截面厚度',
            forearms='新肩腕两段IK保持原骨长，手与前臂共用同一新腕轴'),
        notes=['主手手背朝上，掌面向下，左指朝+X、右指朝-X，近节沿墙面展开后在屋顶内缘下扣。',
            '巨像前倾65度、头俯8.4度、双人偶剧情动作及正面敞开建筑沿用F3。'],
        animation=True, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    print(json.dumps(dict(out=str(OUT), actor_blocks=manifest['actor_blocks'])), flush=True)


if __name__ == '__main__':
    main()
