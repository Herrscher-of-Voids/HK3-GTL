import base64
import gzip
import json
from types import SimpleNamespace

import numpy as np

from author_w05_shapes_20261115 import Part, trace
from dominion_p2_body import BLUE, GOLD, PALE, SHADE, ellipsoid
from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_f2_actors import DOMINION, expand


SOURCE = DOMINION.parent/'0005_支配剧场_俯身撑墙操偶_F3_20261117'


def hand_model(side):
    palm = Part('palm', '撑墙掌背与腕套')
    ellipsoid(palm, (side*188, 133, 39), (17, 18, 12), BLUE)
    palm.ring((side*188, 142, 39), 13, 2, SHADE, depth=4)
    palm.ring((side*188, 145, 39), 13, 1.5, GOLD, depth=2)
    palm.beam((side*182, 141, 46), (side*199, 133, 45), 4, GOLD)
    groups = [(palm.finish(), False)]
    for finger in range(4):
        digit = Part('finger', '向前分节手指')
        x = side*(175+8*finger)
        path = [(x, 126, 47), (x, 113-finger%2*2, 49),
                (x, 104-finger%2*2, 50), (x, 100-finger%2*2, 54)]
        for j, (a, b) in enumerate(zip(path, path[1:])):
            digit.beam(a, b, 4.6 if j < 2 else 4, GOLD if j != 1 else PALE)
            digit.sphere(a, 4.8, SHADE)
        digit.sphere(path[-1], 3.7, GOLD)
        groups.append((digit.finish(), finger >= 2))
    thumb = Part('thumb', '向内舒展拇指')
    path = [(side*173, 136, 43), (side*164, 132, 49), (side*158, 129, 49)]
    trace(thumb, path, 5.2, GOLD)
    thumb.sphere(path[1], 5.4, SHADE)
    groups.append((thumb.finish(), False))
    coordinates, materials = [], []
    for part, bend in groups:
        points = part.p.copy()
        for y in np.unique(points[:, 1]):
            row = points[:, 1] == y
            ceiling = 51+int(max(110-int(y), 0)*.5) if bend else 51
            if y < 136:
                points[row, 2] -= max(int(points[row, 2].max())-ceiling, 0)
        coordinates.append(points)
        materials.append(part.states)
    points, states = np.concatenate(coordinates), np.concatenate(materials)
    selected = points[:, 1] < 150
    points, states = points[selected], states[selected]
    _, unique = np.unique(points[::-1], axis=0, return_index=True)
    points, states = points[::-1][unique], states[::-1][unique]
    points[:, 0] = side*376-points[:, 0]
    return points, states


def build_actors():
    encoded = json.loads((SOURCE/'actors.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded)))
    parts, palette, rig = payload['parts'], payload['materials'], payload['rig']
    with np.load(SOURCE/'演员整数格构件.npz') as data:
        archive = {name: data[name] for name in data.files}
    for side in [-1, 1]:
        points, states = hand_model(side)
        part_id = f'main_hand_{side}'
        metadata = dict(actor='dominion', parent='root', section='arms')
        part = SimpleNamespace(name=part_id, label='四指向前、拇指向内、掌心压墙',
                               p=points, states=states, metadata=metadata)
        item, _ = mesh_part(part, palette)
        item = expand(item, 4, np.zeros(3, int))
        item['metadata']['pivot'] = [side*752, 568, 156]
        parts[parts.index(next(part for part in parts if part['id'] == part_id))] = item
        archive[part_id+'_unit_xyz'] = points
        archive[part_id+'_materials'] = states
    rig['giant_pose'] = dict(waist=[0, 920, 0], waist_degrees=65, head_degrees=8.4,
        wall_top=619, wrist=[516, 671, 80], palm_normal=[0, -1, 0],
        finger_direction=[0, 0, 1], thumb_directions={'left': [1, 0, 0], 'right': [-1, 0, 0]},
        hand_basis=[[-1, 0, 0], [0, 0, -1], [0, -1, 0]],
        source_x_mirrored=True, finger_bend='内侧两指沿墙顶前伸，外侧两指末节轻扣')
    return parts, palette, rig, archive, payload['atlas']
