import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from thousand_d1_common import COLORS
from thousand_d1_body import build_body
from thousand_d1_head import build_head
from thousand_d1_limbs import build_limbs
from dominion_p2_export import write_vox
from package_0005_w12_author_blueprint_20261116 import mesh_part


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_独立像素模型_D1_20261117'
LOG = ROOT/'logs/0005-thousand-d1-20261117'
VIEWS = {
    'face': dict(label='蒙眼与三叶额纹', direction=[-.3, .05, 1.5], center=[0, 177, 3], half=[39, 36, 28]),
    'hair': dict(label='后脑与双锥发髻', direction=[-.9, .2, -1.2], center=[0, 180, -2], half=[39, 34, 27]),
    'dress': dict(label='黑金裙纹', direction=[-.5, .15, 1.5], center=[0, 113, 0], half=[42, 34, 28]),
    'hands': dict(label='金手与指节', direction=[-.45, .2, 1.5], center=[-40, 80, 5], half=[17, 25, 16]),
    'knees': dict(label='白瓷机械腿', direction=[-.7, .15, 1.5], center=[0, 47, 1], half=[27, 47, 20]),
    'pixels': dict(label='真实方块近景', direction=[-.7, .35, 1.2], center=[-8, 185, 17], half=[12, 12, 10]),
}
NOTES = ['形制依据：《薪炎永燃》动画里的金发裙装千人人偶。',
         '头部：奶金分片后脑壳、双锥发髻、长侧发、白瓷脸、黑蒙眼与金三叶额纹。',
         '服装：黑色收腰伞裙、白色胸片与衬裙、金色叶瓣纹和腹扣。',
         '四肢：白瓷球关节、细长黑袖、分节金色五指手与白瓷机械腿。',
         '独立构件保存世界坐标、旋转中心及父子关系；肩、腕、背部保存提线连接点。']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def make_materials():
    palette = []
    for index, (label, color) in enumerate(COLORS):
        rgb = np.array([int(color[i:i+2], 16) for i in [1, 3, 5]])
        y, x = np.mgrid[:16, :16]
        noise = ((x*13+y*7+x*y*3) % 5)-2
        noise[(x == 0) | (y == 0)] -= 3
        pixels = np.clip(rgb+noise[:, :, None], 0, 255).astype(np.uint8)
        png = io.BytesIO()
        Image.fromarray(pixels).save(png, format='PNG')
        texture = 'data:image/png;base64,'+base64.b64encode(png.getvalue()).decode()
        palette.append(dict(id=index+1, label=label, color=color, state=f'pixel:color_{index+1}',
                            faces={f: texture for f in ['east', 'west', 'south', 'north', 'down', 'up']},
                            transparent=False, emissive=False))
    return palette


def prepare_viewer():
    source_dir = ROOT/'deliveries/0005_乌合之众_原作像素重建_P3_20261117'
    source = (source_dir/'生成脚本/viewer.mjs').read_text('utf8')
    source = source.replace('DOMINION_PAYLOAD', 'PUPPET_PAYLOAD').replace('DOMINION_READY', 'PUPPET_READY').replace('DominionViewer', 'PuppetViewer')
    source = source.replace('乌合之众-P3-', '千人人偶-D1-')
    source = source.replace("[{id:'all',title:'完整模型'},{id:'main',title:'站立本体'},...data.models]", "[{id:'all',title:'完整模型'},...data.models]")
    source = source.replace("id==='all'||(id==='main'?g.userData.modelId!=='hands':g.userData.modelId===id)", "id==='all'||g.userData.modelId===id")
    source = source.replace("id==='all'?data.title:id==='main'?'乌合之众 · 站立本体':modelById.get(id).title", "id==='all'?data.title:modelById.get(id).title")
    source = source.replace('direction:[-.8,.4,1.4]', 'direction:[-.55,.12,1.6]')
    (OUT/'生成脚本/viewer.mjs').write_text(source, 'utf8')
    shutil.copyfile(source_dir/'style.css', OUT/'style.css')
    shutil.copyfile(Path(__file__).with_name('thousand_d1_index.html'), OUT/'index.html')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT/'生成脚本').mkdir(exist_ok=True)
    palette = make_materials()
    parts = [*build_body(), *build_limbs(), *build_head()]
    low = np.min([p.p.min(0) for p in parts], axis=0)
    high = np.max([p.p.max(0) for p in parts], axis=0)
    w, h, d = map(int, high-low+1)
    keys = np.concatenate([((p.p[:, 1].astype(np.int64)-low[1])*d+p.p[:, 2]-low[2])*w+p.p[:, 0]-low[0] for p in parts])
    states = np.concatenate([p.states for p in parts])
    owners = np.repeat(np.arange(len(parts), dtype=np.uint16), [len(p.p) for p in parts])
    keys, chosen = np.unique(keys[::-1], return_index=True)
    chosen = len(states)-chosen-1
    states, owners = states[chosen], owners[chosen]
    xyz = np.c_[keys % w, keys//(w*d), keys//w % d].astype(np.int32)+low
    np.savez_compressed(OUT/'完整整数格模型.npz', xyz=xyz, states=states, owners=owners, origin=low, size=[w, h, d])
    archive, packed, final_parts, quads = {}, [], [], 0
    for index, part in enumerate(parts):
        archive[part.name+'_xyz'], archive[part.name+'_materials'] = part.p, part.states
        current = copy(part)
        selected = owners == index
        current.p, current.states = xyz[selected], states[selected]
        item, count = mesh_part(current, palette)
        item.update(modelId=part.metadata['section'], pivot=part.metadata['pivot'], parent=part.metadata['parent'])
        packed.append(item)
        final_parts.append(current)
        quads += count
        print(f'{part.label}: {len(current.p):,}格', flush=True)
    np.savez_compressed(OUT/'独立关节构件.npz', **archive)
    labels = dict(head='头与发壳', body='黑金裙装', arms='黑袖双臂', hands='金色五指手', legs='白瓷机械腿')
    models = [dict(id=k, title=v, views=VIEWS) for k, v in labels.items()]
    rig = dict(coordinates='右手坐标；X宽、Y高、+Z正面；pivot为世界坐标',
               joints=[dict(id=p.name, label=p.label, **p.metadata) for p in parts],
               anchors=[dict(id='back', part='body', point=[0, 136, -13]),
                        dict(id='shoulder_l', part='body', point=[-25, 144, 0]),
                        dict(id='shoulder_r', part='body', point=[25, 144, 0]),
                        dict(id='wrist_l', part='hand_l', point=[-39, 88, 2]),
                        dict(id='wrist_r', part='hand_r', point=[39, 88, 2])],
               w11_intent='乌合之众位于支配剧场中央；两手以丝线悬吊两只小千人人偶，手与人偶联动。')
    save(OUT/'关节与提线.json', rig)
    data = dict(title='千人人偶 · 独立方块模型 D1', sizeXYZ=[w, h, d], bounds=dict(min=low.tolist(), max=high.tolist()),
                total_blocks=len(keys), models=models, views=VIEWS, design=NOTES, rig=rig)
    payload = base64.b64encode(gzip.compress(json.dumps(dict(data=data, materials=palette, parts=packed), ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'data.js').write_text('window.PUPPET_PAYLOAD='+json.dumps(payload)+';\n', 'utf8')
    vox = OUT/'千人人偶-独立方块模型-D1.vox'
    tiles = write_vox(vox, parts, palette, title='千人人偶独立方块模型')
    manifest = dict(title=data['title'], conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
                    generated_at=datetime.now().astimezone().isoformat(), candidate='D1', status='独立人偶外观待审',
                    size_wdh=[w, d, h], bounds_xyz=data['bounds'], blocks=len(keys), surface_quads=quads,
                    colors=[dict(id=i+1, label=label, color=color) for i, (label, color) in enumerate(COLORS)],
                    components=[dict(id=p.name, label=p.label, blocks=len(p.p), metadata=p.metadata) for p in final_parts],
                    detail_notes=NOTES, reference_source='https://www.youtube.com/watch?v=n1rjfW-5HAE',
                    reference_catalogue='参考图册.html', reference_records=['references/animation/references.json', 'references/game/sources.json', 'references/design/observations.json'],
                    vox=dict(file=vox.name, sha256=hashlib.sha256(vox.read_bytes()).hexdigest(), scene_tiles=tiles, axes='VOX的X/Y/Z对应模型X/Z/Y'),
                    vox_assembly='各关节保留完整连接体积，完整整数格模型.npz保存同格去重结果。',
                    future_layout=rig['w11_intent'], integer_cubes=True, appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    prepare_viewer()
    for name in ['package_0005_thousand_d1_20261117.py', 'thousand_d1_common.py', 'thousand_d1_body.py', 'thousand_d1_head.py', 'thousand_d1_limbs.py',
                 'dominion_p2_export.py', 'author_w05_shapes_20261115.py', 'thousand_d1_index.html']:
        shutil.copyfile(Path(__file__).with_name(name), OUT/'生成脚本'/name)
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), components=len(parts), vox_tiles=tiles, quads=quads)), flush=True)


if __name__ == '__main__':
    main()
