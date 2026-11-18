import base64
import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from author_w05_shapes_20261115 import Part
from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_t2_ceiling import GOLD, TRIM, WHITE


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117'
OPENING = dict(x=[-390, 390], z=[-100, 430], inclusive=True)


def _keys(points, low, size):
    local = points.astype(np.int64)-low
    return (local[:, 1]*size[2]+local[:, 2])*size[0]+local[:, 0]


def _frame():
    part = Part('roof_puppetry_opening_frame', '提线天窗奶白细金收边', section='roof',
                design='开口外侧五格窄框，沿用T2奶白金属板与细金材料')
    edges = [((-395, -105), (-391, 435)), ((391, -105), (395, 435)),
             ((-390, -105), (390, -101)), ((-390, 431), (390, 435))]
    for (x0, z0), (x1, z1) in edges:
        part.box((x0, 618, z0), (x1, 618, z1), TRIM)
        part.box((x0, 619, z0), (x1, 619, z1), WHITE)
    for x in (-393, 393):
        part.box((x, 620, -103), (x, 620, 433), GOLD)
    for z in (-103, 433):
        part.box((-393, 620, z), (393, 620, z), GOLD)
    return part.finish()


def build_theatre(out):
    out = Path(out)
    encoded = json.loads((SOURCE/'data.js').read_text('utf8').split('=', 1)[1].strip().removesuffix(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    manifest = json.loads((SOURCE/'manifest.json').read_text('utf8'))
    archive = np.load(SOURCE/'完整整数格模型.npz')
    xyz, states, owners = archive['xyz'], archive['states'], archive['owners']
    roof_indices = [i for i, part in enumerate(manifest['components']) if part['metadata']['section'] == 'roof']
    roof = np.isin(owners, roof_indices)
    points, values, roof_owners = xyz[roof], states[roof], owners[roof]
    low, size = archive['origin'], archive['size']
    archive.close()
    del xyz, states, owners, roof
    opening = ((points[:, 0] >= -390) & (points[:, 0] <= 390) &
               (points[:, 2] >= -100) & (points[:, 2] <= 430))
    removed = int(opening.sum())
    frame = _frame()
    covered = np.isin(_keys(points, low, size), _keys(frame.p, low, size))
    keep = ~opening & ~covered
    packed = []
    for index, (component, original) in enumerate(zip(manifest['components'], payload['parts'])):
        if component['metadata']['section'] != 'roof':
            packed.append(original)
            continue
        selected = keep & (roof_owners == index)
        if not selected.any():
            continue
        part = SimpleNamespace(name=component['id'], label=component['label'], metadata=component['metadata'],
                               p=points[selected], states=values[selected])
        item, _ = mesh_part(part, payload['materials'])
        item['modelId'] = 'roof'
        packed.append(item)
    item, _ = mesh_part(frame, payload['materials'])
    item['modelId'] = 'roof'
    packed.append(item)
    blocks = sum(part['blocks'] for part in packed)
    lower = np.min([part['origin'] for part in packed], axis=0)
    upper = np.max([np.asarray(part['origin'])+part['size']-1 for part in packed], axis=0)
    payload['parts'] = packed
    payload['data'].update(title='支配剧场 · 外置巨像提线 F2', candidate='F2', total_blocks=blocks,
                           sizeXYZ=(upper-lower+1).tolist(), bounds=dict(min=lower.tolist(), max=upper.tolist()),
                           roof_opening=OPENING)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
    (out/'theatre.js').write_text('window.THEATRE_PAYLOAD='+json.dumps(encoded)+';\n', 'utf8')
    info = dict(removed_blocks=removed, added_blocks=blocks-manifest['blocks']+removed,
                roof_opening=OPENING, blocks=blocks, parts=len(packed))
    record = dict(source=str(SOURCE), **info, frame_blocks=len(frame.p), replaced_roof_blocks=int(covered.sum()),
                  frame_materials=dict(trim=TRIM, white=WHITE, gold=GOLD),
                  note='指定范围的屋顶实体已删除；奶白细金框全部位于开口外侧。非屋顶构件沿用T2。')
    (out/'屋顶改造.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    return info
