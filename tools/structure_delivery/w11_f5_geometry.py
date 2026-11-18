import base64
from dataclasses import dataclass
import gzip
import json

import numpy as np
from scipy.ndimage import affine_transform

from theatre_f1_actors import DOMINION
from theatre_f2_roof import _frame
from w11_f5_materials import ROOT, SOURCE, load_materials


CONTROLLER = np.array([0, 20, 500])
ROOT_POSITION = np.array([0, 21, -850])


def unpack(name):
    value = json.loads((SOURCE/name).read_text('utf8').split('=', 1)[1].strip().rstrip(';'))
    return json.loads(gzip.decompress(base64.b64decode(value)))


def translation(point):
    matrix = np.eye(4)
    matrix[:3, 3] = point
    return matrix


def rotation(angles):
    x, y, z = angles
    cx, cy, cz, sx, sy, sz = np.cos(x), np.cos(y), np.cos(z), np.sin(x), np.sin(y), np.sin(z)
    matrix = np.eye(4)
    matrix[:3, :3] = np.array([[cy*cz, -cy*sz, sy],
        [cx*sz+sx*sy*cz, cx*cz-sx*sy*sz, -sx*cy],
        [sx*sz-cx*sy*cz, sx*cz+cx*sy*sz, cx*cy]])
    return matrix


def aligned(a, b):
    a, b = a/np.linalg.norm(a), b/np.linalg.norm(b)
    x, y, z = np.cross(a, b)
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    matrix = np.eye(4)
    matrix[:3, :3] += cross+cross@cross/(1+np.dot(a, b))
    return matrix


def motion(time, index):
    phase = time*.72+index*np.pi
    return dict(phase=phase, pull=np.sin(phase), roll=np.sin(phase+.5), sway=np.sin(phase*.73+.2),
                forward=np.sin(phase*.85-.4), twist=np.sin(phase*.5+.3))


def rest_matrices(payload):
    rig = payload['rig']
    waist, head = np.array([0, 920, 0]), np.array([0, 1536, 0])
    body = translation(ROOT_POSITION)@translation(waist)@rotation(np.deg2rad([65, 0, 0]))@translation(-waist)
    matrices = {name: body for name in ('torso', 'shoulder_-1', 'shoulder_1')}
    matrices['dominion_p2_head'] = body@translation(head)@rotation(np.deg2rad([8.4, 0, 0]))@translation(-head)
    for side in (-1, 1):
        matrices[f'leg_{side}'] = translation(ROOT_POSITION)
        s, e, w = (np.array(p)*4 for p in ([side*148, 325, -3], [side*169, 262, 14], [side*188, 142, 39]))
        shoulder = (body@np.r_[s, 1])[:3]
        wrist = np.array([side*516, 671, 80])
        upper, forearm = e-s, w-e
        direction = wrist-shoulder
        distance = np.linalg.norm(direction)
        direction = direction/distance
        outward = np.array([float(side), 0, 0])-direction*np.dot([side, 0, 0], direction)
        outward /= np.linalg.norm(outward)
        along = (np.dot(upper, upper)-np.dot(forearm, forearm)+distance**2)/(2*distance)
        elbow = shoulder+direction*along+outward*np.sqrt(np.dot(upper, upper)-along**2)
        matrices[f'main_upper_{side}'] = translation(shoulder)@aligned(upper, elbow-shoulder)@translation(-s)
        matrices[f'main_forearm_{side}'] = translation(elbow)@aligned(forearm, wrist-elbow)@translation(-e)
        hand = np.eye(4)
        hand[:3, :3] = [[-1, 0, 0], [0, 0, -1], [0, -1, 0]]
        matrices[f'main_hand_{side}'] = translation(wrist)@hand@translation(-w)
    by_id = {p['id']: p for p in payload['parts']}
    metadata = {}
    for index, actor in enumerate(('puppet_l', 'puppet_r')):
        hand_id = rig['hands'][actor]['part']
        pivot = np.array(by_id[hand_id]['metadata']['pivot'])
        hand_motion = motion(0, index)
        offset = np.array([hand_motion['sway']*8, hand_motion['pull']*12, hand_motion['forward']*10])
        angles = [hand_motion['forward']*.065, hand_motion['twist']*.055,
                  (-1 if index == 0 else 1)*hand_motion['roll']*.07]
        matrices[hand_id] = translation(ROOT_POSITION)@translation(pivot+offset)@rotation(angles)@translation(-pivot)
        pose = next(p for p in rig['poses'] if p['actor'] == actor)
        values = {p['id']: np.deg2rad(pose['angles_degrees'].get(p['id'], [0, 0, 0])) for p in payload['parts'] if p['metadata']['actor'] == 'puppet'}
        pm = motion(-.18, index)
        root_angles = np.deg2rad(pose['angles_degrees']['root'])+np.array([pm['forward']*.035, pm['twist']*.05, pm['sway']*.03])
        root_point = np.array(rig['actor_root'][actor])+[pm['sway']*12, pm['pull']*10, pm['forward']*14]
        bones = {'root': translation(root_point)@rotation(root_angles)}
        values['body'] += [pm['forward']*.03, pm['twist']*.08, -pm['sway']*.025]
        values['head'] += [pm['pull']*.03, pm['twist']*.035, pm['roll']*(.05 if index == 0 else .025)]
        for suffix, direction in [('l', 1), ('r', -1)]:
            knee = np.sin(pm['phase']+(0 if direction == 1 else np.pi))
            values['arm_'+suffix] += [pm['forward']*.04, 0, pm['roll']*.04]
            values['forearm_'+suffix] += [pm['pull']*.035, 0, direction*pm['roll']*.03]
            values['hand_'+suffix] += [pm['roll']*.06, pm['twist']*.04, 0]
            values['thigh_'+suffix] += [knee*.06, 0, direction*pm['sway']*.018]
            values['shin_'+suffix] += [knee*.08, 0, 0]
            values['foot_'+suffix] += [-.04-knee*.03, 0, 0]
        for part in payload['parts']:
            info = part['metadata']
            if info['actor'] != 'puppet':
                continue
            name, parent = part['id'], info['parent']
            pivot = np.array(info['pivot'])
            parent_pivot = np.zeros(3) if parent == 'root' else np.array(by_id[parent]['metadata']['pivot'])
            bones[name] = bones[parent]@translation(pivot-parent_pivot)@rotation(values[name])
            key = actor+'_'+name
            matrices[key] = bones[name]@translation(-pivot)
            metadata[key] = dict(actor=actor, bone=name, parent=parent, pivot=pivot.tolist(),
                                 base_rotation=np.deg2rad(pose['angles_degrees'].get(name, [0, 0, 0])).tolist())
    return matrices, metadata


@dataclass
class Model:
    id: str
    cube: np.ndarray
    origin: np.ndarray
    factor: int
    matrix: np.ndarray
    metadata: dict
    owner: int
    low: np.ndarray
    high: np.ndarray


def model(name, points, states, factor, matrix, metadata, owner):
    origin, high = points.min(0), points.max(0)
    cube = np.zeros(tuple(high-origin+1), np.uint8)
    cube[tuple((points-origin).T)] = states
    transformed = points@matrix[:3, :3].T*factor+matrix[:3, 3]
    low = transformed.min(0)+np.minimum(matrix[:3, :3], 0).sum(1)*factor
    high = transformed.max(0)+np.maximum(matrix[:3, :3], 0).sum(1)*factor
    return Model(name, cube, origin, factor, matrix, metadata, owner,
                 np.ceil(low-.5).astype(int), np.ceil(high-.5).astype(int)-1)


def read_sources():
    materials, mapping, records = load_materials()
    payload = unpack('actors.js')
    matrices, puppet_metadata = rest_matrices(payload)
    models, owners = [], {1: dict(id='static', actor='static', dynamic=False)}
    with np.load(DOMINION/'完整整数格模型.npz') as source:
        xyz, states, component = source['xyz'], source['states'], source['owners']
    manifest = json.loads((DOMINION/'manifest.json').read_text('utf8'))
    indices = {p['id']: i for i, p in enumerate(manifest['components'])}
    with np.load(SOURCE/'演员整数格构件.npz') as archive:
        for part in payload['parts']:
            if part['metadata']['actor'] != 'dominion':
                continue
            name, info = part['id'], part['metadata']
            factor = int(info['integer_expansion'])
            if name.startswith(('main_', 'floating_hand')):
                points, values = archive[name+'_unit_xyz'], archive[name+'_materials']
            else:
                selected = component == indices[name]
                points, values = xyz[selected], states[selected]
            matrix = matrices[name].copy()
            if name.startswith('floating_hand'):
                matrix = matrix@translation(archive[name+'_offset'])
                owner = len(owners)+1
                metadata = dict(id=name, actor='dominion', bone=name, parent='root', pivot=info['pivot'], base_rotation=[0, 0, 0], dynamic=True,
                                rest_matrix=matrices[name].T.ravel().tolist())
                owners[owner] = metadata
            else:
                owner, metadata = 1, owners[1]
            models.append(model(name, points, mapping[values], factor, matrix, metadata, owner))
        for actor in ('puppet_l', 'puppet_r'):
            for part in payload['parts']:
                if part['metadata']['actor'] != 'puppet':
                    continue
                key = actor+'_'+part['id']
                metadata = dict(id=key, **puppet_metadata[key], dynamic=True, rest_matrix=matrices[key].T.ravel().tolist())
                owner = len(owners)+1
                owners[owner] = metadata
                models.append(model(key, archive[part['id']+'_xyz'], mapping[archive[part['id']+'_materials']],
                                    1, matrices[key], metadata, owner))
    source = ROOT/'deliveries/0005_支配剧场_细节精修_T2_20261117'
    manifest = json.loads((source/'manifest.json').read_text('utf8'))
    with np.load(source/'完整整数格模型.npz') as archive:
        points, values, component = archive['xyz'], archive['states'], archive['owners']
    front = [i for i, p in enumerate(manifest['components']) if p['metadata']['section'] == 'front']
    roof = [i for i, p in enumerate(manifest['components']) if p['metadata']['section'] == 'roof']
    opening = np.isin(component, roof)&(points[:, 0] >= -390)&(points[:, 0] <= 390)&(points[:, 2] >= -100)&(points[:, 2] <= 430)
    keep = ~np.isin(component, front)&~opening
    points, values = points[keep], values[keep]
    low = np.min([np.array([-500, 14, -489]), *[m.low for m in models]], axis=0)
    high = np.max([np.array([500, 620, 507]), *[m.high for m in models]], axis=0)
    theatre_origin, theatre_size = np.array([-500, 14, -489]), np.array([1001, 607, 997])
    local = points-theatre_origin
    keys = (local[:, 0]*theatre_size[1]+local[:, 1])*theatre_size[2]+local[:, 2]
    order = np.argsort(keys)
    theatre = dict(keys=keys[order], states=values[order], origin=theatre_origin, size=theatre_size, frame=_frame())
    return dict(models=models, owners=owners, theatre=theatre, materials=materials, mapping=records,
                low=low, high=high, rig=payload['rig'])


def rasterize(scene, x0, x1):
    low, high = scene['low'], scene['high']
    shape = (x1-x0, high[1]-low[1]+1, high[2]-low[2]+1)
    states, owners = np.zeros(shape, np.uint8), np.zeros(shape, np.uint8)
    theatre = scene['theatre']
    origin, size, keys = theatre['origin'], theatre['size'], theatre['keys']
    a, b = np.searchsorted(keys, [(x0-origin[0])*size[1]*size[2], (x1-origin[0])*size[1]*size[2]])
    current = keys[a:b]
    x, y, z = current//(size[1]*size[2])+origin[0]-x0, current//size[2]%size[1]+origin[1]-low[1], current%size[2]+origin[2]-low[2]
    states[x, y, z], owners[x, y, z] = theatre['states'][a:b], 1
    frame = theatre['frame']
    selected = (frame.p[:, 0] >= x0)&(frame.p[:, 0] < x1)
    p = frame.p[selected]-np.array([x0, low[1], low[2]])
    states[tuple(p.T)], owners[tuple(p.T)] = frame.states[selected], 1
    for item in scene['models']:
        first, last = np.maximum(item.low, [x0, low[1], low[2]]), np.minimum(item.high+1, [x1, high[1]+1, high[2]+1])
        if np.any(last <= first):
            continue
        inverse = item.matrix[:3, :3].T/item.factor
        offset = inverse@(first+.5-item.matrix[:3, 3])-item.origin-.5
        sampled = affine_transform(item.cube, inverse, offset, tuple(last-first), order=0, mode='grid-constant', cval=0, prefilter=False)
        target = tuple(slice(a, b) for a, b in zip(first-[x0, low[1], low[2]], last-[x0, low[1], low[2]]))
        occupied = sampled != 0
        states[target][occupied], owners[target][occupied] = sampled[occupied], item.owner
    return states, owners
