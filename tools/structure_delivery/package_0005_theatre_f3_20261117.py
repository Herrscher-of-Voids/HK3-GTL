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

from theatre_f3_actors import DOMINION, REFERENCES, build_actors
from theatre_f3_front import build_theatre


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_俯身撑墙操偶_F3_20261117'
LOG = ROOT/'logs/0005-theatre-f3-20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    scripts = OUT/'生成脚本'
    scripts.mkdir(exist_ok=True)
    theatre = build_theatre(OUT)
    parts, palette, rig, archive = build_actors()
    np.savez_compressed(OUT/'演员整数格构件.npz', **archive)
    atlas = Image.new('RGB', (192, 192))
    for i, material in enumerate(palette):
        tile = Image.open(io.BytesIO(base64.b64decode(material['faces']['south'].split(',')[1])))
        atlas.paste(tile, (i % 12*16, i//12*16))
    png = io.BytesIO()
    atlas.save(png, format='PNG')
    payload = dict(parts=parts, materials=palette, rig=rig, atlas='data:image/png;base64,'+base64.b64encode(png.getvalue()).decode())
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'actors.js').write_text('window.ACTOR_PAYLOAD='+json.dumps(encoded)+';\n', 'utf8')
    shutil.copyfile(REFERENCES/'poses.json', OUT/'剧情动作依据.json')
    save(OUT/'提线骨架.json', rig)
    save(OUT/'演员色板.json', palette)
    save(OUT/'整数格展开.json', dict(source='../'+DOMINION.name+'/完整整数格模型.npz',
        source_sha256=hashlib.sha256((DOMINION/'完整整数格模型.npz').read_bytes()).hexdigest(),
        body_part_ids=[p['id'] for p in parts if p['metadata']['actor']=='dominion' and p['metadata']['section']!='hands'],
        body_expansion=4, unit_block_size=1, root=rig['actor_root']['dominion'], hands_and_puppets='演员整数格构件.npz'))
    source = Path(__file__).parent
    shutil.copyfile(source/'theatre_f3_index.html', OUT/'index.html')
    shutil.copyfile(ROOT/'deliveries/0005_支配剧场_提线共演_F1_20261117/style.css', OUT/'style.css')
    for name in ['theatre_f3_actors.py', 'theatre_f3_front.py', 'theatre_f3_viewer.mjs', 'theatre_f3_animation.mjs',
                 'theatre_f3_index.html', 'theatre_f3_giant.mjs', 'package_0005_theatre_f3_20261117.py', 'preview_0005_theatre_f3_20261117.mjs']:
        shutil.copyfile(source/name, scripts/name)
    bounds_min = np.min([np.array(p['origin'])+np.array(rig['actor_root']['dominion']) for p in parts if p['metadata']['actor']=='dominion'], axis=0)
    bounds_max = np.max([np.array(p['origin'])+np.array(p['size'])-1+np.array(rig['actor_root']['dominion']) for p in parts if p['metadata']['actor']=='dominion'], axis=0)
    counts = {actor: sum(p['blocks'] for p in parts if p['metadata']['actor']==actor) for actor in ('dominion', 'puppet')}
    manifest = dict(title='支配剧场 · 俯身撑墙操偶 F3', candidate='F3', conversation='0005',
        conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d', generated_at=datetime.now(timezone.utc).isoformat(),
        theatre=theatre, actor_blocks={**counts, 'puppet_instances':2}, giant_rest_bounds=dict(min=bounds_min.tolist(), max=bounds_max.tolist()),
        rig=rig, actor_components=[dict(id=p['id'], blocks=p['blocks'], metadata=p['metadata']) for p in parts],
        notes=['腰部前倾65度，头部追加8.4度俯视，双主臂按原骨长弯肘撑在左右墙沿。',
               '两只悬浮平掌继续提线操偶；左侧歪头曲肘，右侧单臂高举，姿态依据剧情原帧。',
               '前墙与前端二层横廊实体删除，完整建筑模式默认正面敞开；沿用F2屋顶开口。',
               '演员pixel:*为原色板预览；W11正式结构、方块映射与游戏动画接入分别记录。'],
        animation=True, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    print(json.dumps(dict(out=str(OUT), counts=counts, giant_bounds=manifest['giant_rest_bounds'])), flush=True)


if __name__ == '__main__':
    main()
