import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from thousand_d2_model import palette as puppet_palette


ROOT = Path(__file__).resolve().parents[2]
DOMINION = ROOT/'deliveries/0005_乌合之众_原作像素重建_P3_20261117'
PUPPET = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117'
HAND_PIVOTS = {'floating_hand_f03': [-297, 354, 80], 'floating_hand_f08': [300, 356, 66]}
HAND_POINTS = {
    'puppet_l': ('floating_hand_f03', [[-378, 374, 63], [-381, 400, 63], [-376, 417, 72],
                                     [-352, 422, 87], [-363, 354, 79]]),
    'puppet_r': ('floating_hand_f08', [[346, 428, 63], [369, 424, 50], [384, 410, 48],
                                     [383, 382, 51], [329, 414, 82]]),
}


def _point(point, scale):
    return np.rint(np.asarray(point)*scale).astype(int).tolist()


def _resample(points, states, scale):
    points = np.rint(points*scale).astype(np.int32)
    _, index = np.unique(points[::-1], axis=0, return_index=True)
    index = len(points)-index-1
    return points[index], states[index].astype(np.uint16)


def build_actors():
    parts = []
    palette = json.loads((DOMINION/'materials.json').read_text('utf8'))
    palette += [{**material, 'id': material['id']+10} for material in puppet_palette()]
    source = np.load(DOMINION/'完整整数格模型.npz')
    xyz, states, owners = source['xyz'], source['states'], source['owners']
    manifest = json.loads((DOMINION/'manifest.json').read_text('utf8'))
    for index, component in enumerate(manifest['components']):
        selected = owners == index
        points, values = _resample(xyz[selected], states[selected], .68)
        metadata = component['metadata'].copy()
        pivot = HAND_PIVOTS.get(component['id'], metadata['center']) if metadata['section'] == 'hands' else [0, 0, 0]
        metadata.update(actor='dominion', parent='root', pivot=_point(pivot, .68))
        parts.append(SimpleNamespace(name=component['id'], label=component['label'],
                                     p=points, states=values, metadata=metadata))

    source = np.load(PUPPET/'完整整数格模型.npz')
    xyz, states, owners = source['xyz'], source['states'], source['owners']
    joints = json.loads((PUPPET/'关节.json').read_text('utf8'))['joints']
    joint_by_id = {joint['id']: joint for joint in joints}
    feet = [index for index, joint in enumerate(joints) if joint['id'] in ('foot_l', 'foot_r')]
    foot_pivots = np.array([joints[index]['pivot'] for index in feet])
    strays = np.flatnonzero((xyz[:, 0] == 0) & (xyz[:, 1] == 7) & np.isin(xyz[:, 2], (-9, -8)))
    for index in strays:
        owners[index] = feet[np.sum((foot_pivots-xyz[index])**2, axis=1).argmin()]
    for index, joint in enumerate(joints):
        selected = owners == index
        points, values = _resample(xyz[selected], states[selected], .25)
        metadata = {key: value for key, value in joint.items() if key not in ('id', 'label')}
        metadata.update(actor='puppet', pivot=_point(joint['pivot'], .25))
        parts.append(SimpleNamespace(name=joint['id'], label=joint['label'], p=points,
                                     states=values+10, metadata=metadata))

    rig = dict(
        coordinates='整数格演员本地坐标；actor_root为世界偏移；所有pivot采用演员本地坐标',
        actor_root=dict(dominion=[0, 21, 300], puppet_l=[-252, 90, 420], puppet_r=[246, 90, 420]),
        source_scale=dict(dominion=.68, puppet=.25),
        hands={actor: dict(part=hand, points=[_point(point, .68) for point in points])
               for actor, (hand, points) in HAND_POINTS.items()},
        puppet_targets=[dict(part='head', point=_point([0, 383, 0], .25)),
                        *[dict(part=name, point=_point(joint_by_id[name]['pivot'], .25))
                          for name in ('hand_l', 'hand_r', 'shin_l', 'shin_r')]],
    )
    return parts, palette, rig
