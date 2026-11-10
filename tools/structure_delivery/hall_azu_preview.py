"""礼堂存档预览：真实原版模型，邻面剔除，按状态实例批次；不修改存档。"""
import base64
import gzip
import hashlib
import io
import json
import math
import re
import struct
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'output/hall-azu-analysis'
OUT = ROOT / 'deliveries/永恒的礼堂_Azu_预览与方块审计_20261029'
CLIENT = Path.home() / 'AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
FACE_NAMES = ['east', 'west', 'south', 'north', 'down', 'up']
DIRECTIONS = np.array([[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1], [0, -1, 0], [0, 1, 0]])
UV_U = np.array([[0,0,-1],[0,0,1],[1,0,0],[-1,0,0],[1,0,0],[1,0,0]])
UV_V = np.array([[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,0,1],[0,0,-1]])


class Models:
    def __init__(self):
        self.jar = zipfile.ZipFile(CLIENT)
        self.models = {}
        self.textures = {}
        self.notes = []

    def read(self, kind, value):
        ns, key = value.split(':') if ':' in value else ('minecraft', value)
        return json.loads(self.jar.read(f'assets/{ns}/{kind}/{key}.json'))

    def model(self, name):
        if name not in self.models:
            raw = self.read('models', name)
            parent = self.model(raw['parent']) if raw.get('parent') and not raw['parent'].startswith('builtin/') else {}
            self.models[name] = {**parent, **raw, 'textures': {**parent.get('textures', {}), **raw.get('textures', {})}}
        return self.models[name]

    def texture(self, name, tint=None):
        key = name + (':' + tint if tint else '')
        if key not in self.textures:
            ns, value = name.split(':') if ':' in name else ('minecraft', name)
            image = Image.open(io.BytesIO(self.jar.read(f'assets/{ns}/textures/{value}.png'))).convert('RGBA')
            if image.height != image.width:
                image = image.crop((0, 0, image.width, image.width))
            if tint:
                image = ImageChops.multiply(image, Image.new('RGBA', image.size, tint))
            data = io.BytesIO(); image.save(data, 'PNG')
            self.textures[key] = {'id': len(self.textures), 'url': 'data:image/png;base64,' + base64.b64encode(data.getvalue()).decode(),
                                  'transparent': image.getextrema()[3][0] < 255, 'tint': tint, 'source': name}
        return self.textures[key]['id']

    @staticmethod
    def matches(condition, props):
        if 'OR' in condition:
            return any(Models.matches(c, props) for c in condition['OR'])
        if 'AND' in condition:
            return all(Models.matches(c, props) for c in condition['AND'])
        return all(props.get(k) in str(v).split('|') for k, v in condition.items())

    @staticmethod
    def rotate(points, axis, degrees, origin=(8, 8, 8), rescale=False):
        result = np.asarray(points, dtype=float) - origin
        angle = math.radians(degrees); c, s = math.cos(angle), math.sin(angle)
        a, b = {'x': (1, 2), 'y': (2, 0), 'z': (0, 1)}[axis]
        before = result.copy()
        result[:, a] = before[:, a] * c - before[:, b] * s
        result[:, b] = before[:, a] * s + before[:, b] * c
        if rescale:
            result[:, [a, b]] /= c
        return result + origin

    def bake(self, state):
        block = state.split('[')[0]; props = dict(re.findall(r'(\w+)=([^,\]]+)', state))
        bs = self.read('blockstates', block)
        variants = []
        if 'variants' in bs:
            variants = [v for cond, v in bs['variants'].items() if self.matches(dict(re.findall(r'(\w+)=([^,]+)', cond)), props)]
        else:
            variants = [p['apply'] for p in bs['multipart'] if 'when' not in p or self.matches(p['when'], props)]
        if not variants:
            raise ValueError('无匹配模型')
        faces = []; full = False; uvlock = False
        for choice in variants:
            if isinstance(choice, list):
                choice = choice[0]
            model = self.model(choice['model'])
            elements = model.get('elements', [])
            if not elements:
                raise ValueError('方块实体／不可见模型，不以普通立方体替代')
            full = full or (len(elements) == 1 and elements[0]['from'] == [0, 0, 0] and elements[0]['to'] == [16, 16, 16] and not elements[0].get('rotation'))
            uvlock = uvlock or bool(choice.get('uvlock'))
            for element in elements:
                x1, y1, z1 = element['from']; x2, y2, z2 = element['to']
                vertices = {
                    'east': [[x2,y1,z2],[x2,y1,z1],[x2,y2,z1],[x2,y2,z2]],
                    'west': [[x1,y1,z1],[x1,y1,z2],[x1,y2,z2],[x1,y2,z1]],
                    'south': [[x1,y1,z2],[x2,y1,z2],[x2,y2,z2],[x1,y2,z2]],
                    'north': [[x2,y1,z1],[x1,y1,z1],[x1,y2,z1],[x2,y2,z1]],
                    'up': [[x1,y2,z2],[x2,y2,z2],[x2,y2,z1],[x1,y2,z1]],
                    'down': [[x1,y1,z1],[x2,y1,z1],[x2,y1,z2],[x1,y1,z2]]}
                default_uv = {'east':[16-z2,16-y2,16-z1,16-y1], 'west':[z1,16-y2,z2,16-y1],
                              'south':[x1,16-y2,x2,16-y1], 'north':[16-x2,16-y2,16-x1,16-y1],
                              'up':[x1,z1,x2,z2], 'down':[x1,16-z2,x2,16-z1]}
                for face, spec in element.get('faces', {}).items():
                    position = np.array(vertices[face], dtype=float)
                    if element.get('rotation'):
                        r = element['rotation']; position = self.rotate(position, r['axis'], r['angle'], r['origin'], r.get('rescale', False))
                    cull = FACE_NAMES.index(spec['cullface']) if 'cullface' in spec else -1
                    direction = DIRECTIONS[cull].astype(float).reshape(1, 3) if cull >= 0 else None
                    for axis in ['x', 'y']:
                        if choice.get(axis):
                            position = self.rotate(position, axis, -choice[axis])
                            if direction is not None:
                                direction = self.rotate(direction, axis, -choice[axis], (0,0,0))
                    if direction is not None:
                        cull = int(np.argmax(DIRECTIONS @ direction[0]))
                    tex = spec['texture']; seen = set()
                    while tex.startswith('#'):
                        if tex in seen: raise ValueError('纹理循环')
                        seen.add(tex); tex = model['textures'][tex[1:]]
                    tint = None
                    if spec.get('tintindex', -1) >= 0:
                        tint = '#77ab2f' if 'leaves' in block or 'vine' in block else '#91bd59'
                    texture = self.texture(tex, tint)
                    u1,v1,u2,v2 = spec.get('uv', default_uv[face])
                    uv = [[u1/16,1-v2/16],[u2/16,1-v2/16],[u2/16,1-v1/16],[u1/16,1-v1/16]]
                    turns = spec.get('rotation', 0)//90
                    if turns: uv = uv[turns:] + uv[:turns]
                    if choice.get('uvlock'):
                        face_id=FACE_NAMES.index(face)
                        basis=np.array([UV_U[face_id],UV_V[face_id],DIRECTIONS[face_id]],dtype=float)
                        for axis in ['x','y']:
                            if choice.get(axis): basis=self.rotate(basis,axis,-choice[axis],(0,0,0))
                        world_face=int(np.argmax(DIRECTIONS@basis[2]))
                        transform=np.array([[UV_U[world_face]@basis[0],UV_U[world_face]@basis[1]],
                                            [UV_V[world_face]@basis[0],UV_V[world_face]@basis[1]]])
                        uv=((np.asarray(uv)-.5)@transform.T+.5).round(7).tolist()
                    faces.append({'positions': (position/16).round(7).reshape(-1).tolist(), 'uv': sum(uv,[]), 'texture': texture, 'cull': cull})
        translucent = 'stained_glass' in block or block.endswith(':glass')
        opaque = full and not translucent and 'leaves' not in block and not any(self.texture_by_id(f['texture'])['transparent'] for f in faces)
        return {'state': state, 'faces': faces, 'full': full, 'opaque': opaque, 'translucent': translucent, 'uvlock': uvlock}

    def texture_by_id(self, idx):
        return next(v for v in self.textures.values() if v['id'] == idx)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    palette = json.loads((SOURCE/'palette.json').read_text(encoding='utf-8'))
    scene_file = SOURCE/'scene-main.npz'
    source = np.load(scene_file); positions = source['positions']; states = source['states']; parts = source['part_ids']
    assert len(positions) == len(states) == len(parts) and positions.shape[1] == 3
    assert set(np.unique(parts)) == set(range(14))
    part_bounds = {str(int(part)): [positions[parts==part].min(0).tolist(), positions[parts==part].max(0).tolist()] for part in np.unique(parts)}
    resources = Models(); models = []; missing = []
    cube=resources.bake('minecraft:smooth_quartz')
    slab=resources.bake('minecraft:smooth_quartz_slab[type=bottom,waterlogged=false]')
    assert cube['opaque'] and len(cube['faces']) == 6
    assert not slab['full'] and max(f['positions'][i] for f in slab['faces'] for i in [1,4,7,10]) == .5
    counts = np.bincount(states, minlength=len(palette))
    for i, state in enumerate(palette):
        try: model = resources.bake(state)
        except (ValueError, KeyError) as e:
            model = {'state':state, 'faces':[], 'full':False, 'opaque':False, 'translucent':False}
            missing.append({'state':state,'count':int(counts[i]),'reason':str(e)})
        models.append(model)
    print('Models',len(models),'textures',len(resources.textures),'unrendered',sum(x['count'] for x in missing),flush=True)
    low = positions.min(0); high = positions.max(0); size = high-low+3
    local = positions-low+1
    keys = (local[:,1].astype(np.int64)*int(size[2])+local[:,2])*int(size[0])+local[:,0]
    order = np.argsort(keys); keys=keys[order]; positions=positions[order]; states=states[order]; parts=parts[order]
    opaque = np.array([m['opaque'] for m in models], dtype=bool)
    base = [s.split('[')[0] for s in palette]; base_names = list(dict.fromkeys(base)); base_ids = np.array([base_names.index(s) for s in base])
    full = np.array([m['full'] for m in models],dtype=bool)
    masks = np.zeros(len(keys),dtype=np.uint8)
    for face, offset in enumerate([1,-1,int(size[0]),-int(size[0]),-int(size[0]*size[2]),int(size[0]*size[2])]):
        lookup = np.searchsorted(keys, keys+offset); np.minimum(lookup,len(keys)-1,out=lookup)
        exists = keys[lookup]==keys+offset; neighbor = states[lookup]
        hide = exists & (opaque[neighbor] | (full[states] & full[neighbor] & (base_ids[states]==base_ids[neighbor])))
        masks[hide] |= np.uint8(1 << face)
    groups=[]; chunks=[]; offset=0; hidden=0
    group_keys=states.astype(np.int32)*64+masks
    sorted_groups=np.argsort(group_keys,kind='stable'); grouped=group_keys[sorted_groups]
    boundaries=np.r_[0,np.flatnonzero(grouped[1:]!=grouped[:-1])+1,len(grouped)]
    for begin,end in zip(boundaries[:-1],boundaries[1:]):
        ids=sorted_groups[begin:end]; state=int(states[ids[0]]); mask=int(masks[ids[0]])
        if mask==63 or not models[state]['faces']:
            hidden+=len(ids);continue
        groups.append({'state':state,'mask':mask,'offset':offset,'count':len(ids)})
        points=np.column_stack((positions[ids],parts[ids])).astype('<i2'); chunks.append(points.tobytes());offset+=len(ids)
    blob=gzip.compress(b''.join(chunks),compresslevel=6)
    assert offset+hidden == len(positions)
    payload={'models':models,'textures':sorted(resources.textures.values(),key=lambda t:t['id']),'groups':groups,
             'bounds':[low.tolist(),high.tolist()],'focus':[low.tolist(),high.tolist()],'part_bounds':part_bounds,
             'source_blocks':len(positions),'render_instances':offset,'occluded_or_invisible':hidden,'unrendered':missing,
             'notes':['展示主礼堂区域：主体及13座外塔；排除远处样件与署名字，其计数仍列于总审计。',
                      '原版1.20.1真实模型/PNG用于1.20.4建筑；随机模型固定第一变体，材质动画取首帧；静态日光，不加载光影。',
                      '植物色调采用平原近似；招牌方块实体文字及不可见光源不绘制。水与自然生成海床由源分析单独处理。'],
             'binary':base64.b64encode(blob).decode()}
    (OUT/'hall-data.js').write_text('window.HALL_DATA='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
    verification={'source_blocks':len(positions),'render_instances':offset,'states':len(palette),'textures':len(resources.textures),
                  'batch_groups':len(groups),'unrendered':missing,'bounds':[low.tolist(),high.tolist()],
                  'source_geometry_modified':False,'per_block_matrix_buffers':False,'source_client':str(CLIENT),
                  'scene_npz_sha256':hashlib.sha256(scene_file.read_bytes()).hexdigest()}
    (OUT/'preview-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in verification.items() if k not in ['unrendered','scene_npz_sha256']},ensure_ascii=False))


if __name__=='__main__': main()
