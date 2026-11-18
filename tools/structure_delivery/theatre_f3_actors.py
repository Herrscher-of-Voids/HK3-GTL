import json
from types import SimpleNamespace

import numpy as np

from package_0005_w12_author_blueprint_20261116 import mesh_part
from theatre_f2_actors import DOMINION, ROOT_POSITION, build_actors as build_f2, expand


ROOT = DOMINION.parents[1]
POSITION = np.array([0, 21, -850])
REFERENCES = ROOT/'deliveries/0005_千人人偶_剧情动作参考_F3_20261117'


def build_actors():
    parts, palette, rig, archive = build_f2()
    parts = [part for part in parts if part['id'] not in ('arm_-1', 'arm_1')]
    shift = ROOT_POSITION-POSITION
    for part in parts:
        if part['id'].startswith('floating_hand_'):
            part['origin'] = (np.array(part['origin'])+shift).tolist()
            part['metadata']['pivot'] = (np.array(part['metadata']['pivot'])+shift).tolist()
            archive[part['id']+'_offset'] += shift
        if part['id'] == 'dominion_p2_head':
            part['metadata']['pivot'] = [0, 1536, 0]
    for hand in rig['hands'].values():
        hand['points'] = (np.array(hand['points'])+shift).tolist()
    source = np.load(DOMINION/'完整整数格模型.npz')
    for side, owner in [(-1, 5), (1, 6)]:
        selected = source['owners'] == owner
        xyz, states = source['xyz'][selected], source['states'][selected]
        cuts = [('upper', xyz[:, 1] >= 289, [side*148, 325, -3]),
                ('forearm', (xyz[:, 1] >= 150) & (xyz[:, 1] < 289), [side*169, 262, 14]),
                ('hand', xyz[:, 1] < 150, [side*188, 142, 39])]
        for name, mask, pivot in cuts:
            part_id = f'main_{name}_{side}'
            metadata = dict(actor='dominion', parent='root', section='arms')
            part = SimpleNamespace(name=part_id, label={'upper':'主上臂', 'forearm':'金球肘与前臂', 'hand':'撑墙手掌'}[name],
                                   p=xyz[mask], states=states[mask], metadata=metadata)
            item, _ = mesh_part(part, palette)
            item = expand(item, 4, np.zeros(3, int))
            item['metadata']['pivot'] = (np.array(pivot)*4).tolist()
            parts.append(item)
            archive[part_id+'_unit_xyz'] = part.p
            archive[part_id+'_materials'] = part.states
            archive[part_id+'_expansion'] = np.array([4])
    rig['actor_root']['dominion'] = POSITION.tolist()
    rig['giant_pose'] = dict(waist=[0, 920, 0], waist_degrees=65, head_degrees=8.4,
                             wall_top=619, wrist=[480, 731, 80], palm_rotation_degrees=[90, 0, 0])
    rig['poses'] = json.loads((REFERENCES/'poses.json').read_text('utf8'))['poses']
    rig['pose_references'] = '../'+REFERENCES.name+'/index.html'
    return parts, palette, rig, archive
