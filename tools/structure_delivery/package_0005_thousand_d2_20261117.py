import base64
from copy import copy
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

from thousand_d2_model import MODEL_NOTES, build_model
from dominion_p2_export import write_vox
from package_0005_w12_author_blueprint_20261116 import mesh_part


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117'
LOG = ROOT/'logs/0005-thousand-d2-20261117'
LABELS = dict(head='头与发壳', body='黑金连体衣', arms='黑袖双臂', hands='金色五指手', legs='深色机械腿')
NOTES = [*MODEL_NOTES, 'miHoYo原作，神帝宇整理／编辑，本次负责整数格转换。']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def make_views(parts):
    presets = {}
    details = dict(head=('face', '蒙眼与额纹', [-.15, .03, 1.5]),
                   body=('body', '黑金连体衣', [-.4, .1, 1.5]),
                   hands=('hands', '分节金手', [-.5, .2, 1.5]),
                   legs=('legs', '深色机械腿', [-.4, .1, 1.5]))
    for section, (name, label, direction) in details.items():
        subset = [p for p in parts if p.name == 'hand_l'] if section == 'hands' else [p for p in parts if p.metadata['section'] == section]
        points = np.concatenate([p.p for p in subset])
        low, high = points.min(0), points.max(0)+1
        center, half = (low+high)/2, (high-low)/2+3
        presets[name] = dict(label=label, direction=direction, center=center.tolist(), half=half.tolist())
        if section == 'head':
            presets['hair'] = dict(label='后脑与双锥', direction=[-.7, .15, -1.2], center=center.tolist(), half=half.tolist())
            front = points[points[:, 2] == high[2]-1][0]
            presets['pixels'] = dict(label='整数格近景', direction=[-.6, .25, 1.5],
                                     center=front.tolist(), half=[12, 12, 10])
    return presets


def prepare_viewer():
    old = ROOT/'deliveries/0005_千人人偶_独立像素模型_D1_20261117'
    viewer = (old/'生成脚本/viewer.mjs').read_text('utf8').replace('千人人偶-D1-', '千人人偶-D2-')
    (OUT/'生成脚本/viewer.mjs').write_text(viewer, 'utf8')
    shutil.copyfile(old/'style.css', OUT/'style.css')
    shutil.copyfile(Path(__file__).with_name('thousand_d2_index.html'), OUT/'index.html')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    (OUT/'生成脚本').mkdir(exist_ok=True)
    parts, palette = build_model()
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
    sections = dict.fromkeys(p.metadata['section'] for p in parts)
    views = make_views(parts)
    models = [dict(id=k, title=LABELS[k], views=views) for k in sections]
    rig = dict(coordinates='X宽、Y高、+Z正脸；pivot采用世界坐标；保留原始A姿势',
               joints=[dict(id=p.name, label=p.label, **p.metadata) for p in parts])
    save(OUT/'关节.json', rig)
    data = dict(title='千人人偶 · 游戏剧情形态 D2', sizeXYZ=[w, h, d], bounds=dict(min=low.tolist(), max=high.tolist()),
                total_blocks=len(keys), models=models, views=views, design=NOTES, rig=rig)
    payload = base64.b64encode(gzip.compress(json.dumps(dict(data=data, materials=palette, parts=packed),
                                    ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (OUT/'data.js').write_text('window.PUPPET_PAYLOAD='+json.dumps(payload)+';\n', 'utf8')
    vox = OUT/'千人人偶-游戏剧情形态-D2.vox'
    tiles = write_vox(vox, parts, palette, title='千人人偶游戏剧情形态整数格转换')
    source_receipt = json.loads((OUT/'references/mesh/source-receipt.json').read_text('utf8'))
    conversion = json.loads((OUT/'体素转换记录.json').read_text('utf8'))
    manifest = dict(title=data['title'], conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
                    generated_at=datetime.now().astimezone().isoformat(), candidate='D2', status='独立人偶外观待审',
                    size_wdh=[w, d, h], bounds_xyz=data['bounds'], blocks=len(keys), surface_quads=quads,
                    colors=[dict(id=m['id'], label=m['label'], color=m['color']) for m in palette],
                    components=[dict(id=p.name, label=p.label, blocks=len(p.p), metadata=p.metadata) for p in final_parts],
                    detail_notes=NOTES, source_credit='miHoYo原作；神帝宇整理／编辑；本次整数格转换',
                    source_record='references/mesh/source-receipt.json', source=source_receipt['source'],
                    source_permissions=source_receipt['permissions'], conversion_record='体素转换记录.json', conversion=conversion,
                    reference_catalogue='参考图册.html', reference_records=['references/animation/references.json', 'references/game/sources.json', 'references/game/study.json'],
                    reference_counts=dict(candidate_images=454, accepted_images=329, game_and_auxiliary=117,
                                          animation_variant=212, previous_auxiliary=8,
                                          note='含相邻连续帧，图片数不等于独立角度数；动画裙装形态仅比对。'),
                    vox=dict(file=vox.name, sha256=hashlib.sha256(vox.read_bytes()).hexdigest(), scene_tiles=tiles, axes='VOX的X/Y/Z对应模型X/Z/Y'),
                    vox_assembly='各关节保留完整连接体积，完整整数格模型.npz保存同格去重结果。',
                    integer_cubes=True, original_pose='A姿势', appearance_approved=False, formal_machine_modified=False, jar_built=False)
    save(OUT/'manifest.json', manifest)
    save(LOG/'generation.json', manifest)
    prepare_viewer()
    for name in ['package_0005_thousand_d2_20261117.py', 'preview_0005_thousand_d2_20261117.mjs',
                 'voxelize_0005_thousand_d2_20261117.py', 'thousand_d2_index.html',
                 'catalogue_0005_thousand_d2_20261117.py', 'thousand_d2_catalogue.html', 'dominion_p2_export.py']:
        shutil.copyfile(Path(__file__).with_name(name), OUT/'生成脚本'/name)
    for source in Path(__file__).parent.glob('thousand_d2*.py'):
        shutil.copyfile(source, OUT/'生成脚本'/source.name)
    print(json.dumps(dict(size_wdh=[w, d, h], blocks=len(keys), components=len(parts),
                          vox_tiles=tiles, quads=quads)), flush=True)


if __name__ == '__main__':
    main()
