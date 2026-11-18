import base64
import gzip
import json
from types import SimpleNamespace

import numpy as np

from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_f2_actors import DOMINION, expand


SOURCE = DOMINION.parent/'0005_支配剧场_俯身撑墙操偶_F3_20261117'


def build_actors():
    encoded = json.loads((SOURCE/'actors.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    parts, palette, rig = payload['parts'], payload['materials'], payload['rig']
    with np.load(SOURCE/'演员整数格构件.npz') as data:
        archive = {name: data[name] for name in data.files}
    source = np.load(DOMINION/'完整整数格模型.npz')
    for side, owner in [(-1, 5), (1, 6)]:
        mask = (source['owners'] == owner) & (source['xyz'][:, 1] < 150)
        points, states = source['xyz'][mask].copy(), source['states'][mask]
        trim = (points[:, 1] == 149) & (np.abs(points[:, 0]) >= 178) & (np.abs(points[:, 0]) <= 182) & (points[:, 2] >= 55)
        points, states = points[~trim], states[~trim]
        for y in np.unique(points[:, 1]):
            row = points[:, 1] == y
            ceiling = int(51+max(110-int(y), 0)*1.2)
            if y < 136:
                points[row, 2] -= max(int(points[row, 2].max())-ceiling, 0)
        part_id = f'main_hand_{side}'
        metadata = dict(actor='dominion', parent='root', section='arms')
        part = SimpleNamespace(name=part_id, label='掌心压墙、指端朝内下扣',
                               p=points, states=states, metadata=metadata)
        item, _ = mesh_part(part, palette)
        item = expand(item, 4, np.zeros(3, int))
        item['metadata']['pivot'] = [side*752, 568, 156]
        parts[parts.index(next(part for part in parts if part['id'] == part_id))] = item
        archive[part_id+'_unit_xyz'] = points
        archive[part_id+'_materials'] = states
    rig['giant_pose'] = dict(waist=[0, 920, 0], waist_degrees=65, head_degrees=8.4,
        wall_top=619, wrist=[516, 671, 80], palm_normal=[0, -1, 0],
        finger_direction='左右主手分别朝中心X轴，手背向上，近节沿墙顶展开，指端越过屋顶内缘后下扣',
        inner_roof_edge=390, finger_bend_source_y=110)
    return parts, palette, rig, archive, payload['atlas']
