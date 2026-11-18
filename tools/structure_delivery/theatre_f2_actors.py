import base64
from copy import deepcopy
import gzip
import json
from types import SimpleNamespace

import numpy as np

from dominion_p2_hands import ORIGIN, hand_volume
from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_f1_actors import DOMINION, PUPPET, _resample
from thousand_d2_model import palette as puppet_palette


ROOT_POSITION = np.array([0, 21, -1000])
TIPS = np.array([[-31, 61, 11], [-11, 79, 10], [10, 82, 16], [31, 61, 21], [-36, 32, 23]])


def expand(part, factor, offset):
    part = deepcopy(part)
    old_w, _, old_d = part['size']
    part['origin'] = (np.array(part['origin'])*factor+offset).tolist()
    part['size'] = (np.array(part['size'])*factor).tolist()
    w, _, d = part['size']
    for material in range(len(part['starts'])):
        for face in range(6):
            starts = np.array(part['starts'][material][face], np.int64)
            xyz = np.c_[starts % old_w, starts//(old_w*old_d), starts//old_w % old_d]*factor
            if face in (0, 2, 5):
                xyz[:, {0: 0, 2: 2, 5: 1}[face]] += factor-1
            part['starts'][material][face] = ((xyz[:, 1]*d+xyz[:, 2])*w+xyz[:, 0]).tolist()
            part['lengths'][material][face] = (np.array(part['lengths'][material][face], int)*factor).tolist()
            part['spans'][material][face] = (np.array(part['spans'][material][face], int)*factor).tolist()
    part['blocks'] *= factor**3
    part['metadata'].update(actor='dominion', parent='root', pivot=[0, 0, 0], integer_expansion=factor)
    return part


def build_actors():
    encoded = json.loads((DOMINION/'data.js').read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    original = json.loads(gzip.decompress(base64.b64decode(encoded)))
    palette = original['materials']+[{**m, 'id': m['id']+10} for m in puppet_palette()]
    packed = []
    for source in original['parts']:
        if source['metadata']['section'] == 'hands':
            continue
        part = expand(source, 4, np.zeros(3, int))
        for name in ('starts', 'lengths', 'spans'):
            part[name] += [[[] for _ in range(6)] for _ in range(128)]
        packed.append(part)
    volume = hand_volume('舒展')
    coordinates = np.argwhere(volume)
    states = volume[tuple(coordinates.T)]
    coordinates += ORIGIN
    hands, archive = {}, {}
    for side, actor, code in [(-1, 'puppet_l', 'f03'), (1, 'puppet_r', 'f08')]:
        points = coordinates[:, [0, 2, 1]]*np.array([side, -1, 1])
        offset = np.array([side*235, 800, 20])-ROOT_POSITION
        metadata = dict(actor='dominion', parent='root', pivot=[0, 0, 0], section='hands')
        source = SimpleNamespace(name='floating_hand_'+code, label='平掌提线手', p=points, states=states, metadata=metadata)
        item, _ = mesh_part(source, palette)
        item = expand(item, 3, offset)
        pivot = np.array([0, 0, -23])*3+offset
        item['metadata']['pivot'] = pivot.tolist()
        packed.append(item)
        hands[actor] = dict(part=item['id'], points=(TIPS[:, [0, 2, 1]]*np.array([side, -1, 1])*3+offset).tolist())
        archive[item['id']+'_unit_xyz'] = points
        archive[item['id']+'_materials'] = states
        archive[item['id']+'_expansion'] = np.array([3])
        archive[item['id']+'_offset'] = offset
    data = np.load(PUPPET/'完整整数格模型.npz')
    xyz, values, owners = data['xyz'], data['states'], data['owners']
    joints = json.loads((PUPPET/'关节.json').read_text('utf8'))['joints']
    feet = [i for i, joint in enumerate(joints) if joint['id'] in ('foot_l', 'foot_r')]
    for index in np.flatnonzero((xyz[:, 0] == 0) & (xyz[:, 1] == 7) & np.isin(xyz[:, 2], (-9, -8))):
        owners[index] = feet[np.sum((np.array([joints[i]['pivot'] for i in feet])-xyz[index])**2, axis=1).argmin()]
    for i, joint in enumerate(joints):
        selected = owners == i
        points, colors = _resample(xyz[selected], values[selected], .4)
        metadata = dict(joint, actor='puppet', pivot=np.rint(np.array(joint['pivot'])*.4).astype(int).tolist())
        part = SimpleNamespace(name=joint['id'], label=joint['label'], p=points, states=colors+10, metadata=metadata)
        item, _ = mesh_part(part, palette)
        packed.append(item)
        archive[part.name+'_xyz'], archive[part.name+'_materials'] = points, part.states
    by_id = {joint['id']: joint for joint in joints}
    rig = dict(actor_root=dict(dominion=ROOT_POSITION.tolist(), puppet_l=[-235, 70, 230], puppet_r=[235, 70, 230]),
        source_scale=dict(dominion=4, control_hands=3, puppet=.4), hands=hands,
        puppet_targets=[dict(part='head', point=[0, 153, 0]),
            *[dict(part=name, point=np.rint(np.array(by_id[name]['pivot'])*.4).astype(int).tolist()) for name in ('hand_l', 'hand_r', 'shin_l', 'shin_r')]],
        integer_expansion='每个源体素展开为factor³个一格立方体，合并面与重复像素纹理保留单位格边界')
    return packed, palette, rig, archive
