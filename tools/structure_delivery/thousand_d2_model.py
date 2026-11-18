import base64
import io
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117'
MODEL_NOTES = [
    '负责人选定游戏剧情形态：金发蒙眼、黑金连体衣、深色长腿。',
    '沿miHoYo原作、神帝宇整理的公开预览网格等比体素化，保留原A姿态。',
    '头脸、侧发、双锥发饰、蒙眼折面、白衬衣、黑金胯甲与五指均按原网格取形。',
    '原UV对应原贴图逐面采样，128色保留额纹、胸纹、金边和机械指节。',
    '表面与内部全部为整数格立方体，构件按原关节位置分区。',
]


def palette():
    values = json.loads((OUT/'原贴图色板.json').read_text('utf8'))
    result = []
    for i, rgb in enumerate(values):
        pixels = np.tile(np.array(rgb, np.int16), (16, 16, 1))
        pixels[0, :] -= 3
        pixels[:, 0] -= 3
        pixels[-1, :] -= 7
        pixels[:, -1] -= 7
        png = io.BytesIO()
        Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8)).save(png, format='PNG')
        texture = 'data:image/png;base64,'+base64.b64encode(png.getvalue()).decode()
        color = '#'+''.join(f'{c:02x}' for c in rgb)
        result.append(dict(id=i+1, label=f'原贴图色 {i+1:03} {color}', color=color,
                           state=f'pixel:original_{i+1:03}', transparent=False, emissive=False,
                           faces={face: texture for face in ('east', 'west', 'south', 'north', 'down', 'up')}))
    return result


def build_model():
    data = np.load(OUT/'原网格整数体素.npz')
    xyz, states, material = data['xyz'], data['states'], data['material']
    record = json.loads((OUT/'体素转换记录.json').read_text('utf8'))
    scale = record['scale']
    source = xyz/scale
    x, y = np.abs(source[:, 0]), source[:, 1]
    owners = np.zeros(len(xyz), np.uint8)
    head = np.isin(material, [1, 2, 3, 5, 6, 7, 8]) | ((y >= 15.7) & (x < 1.8))
    owners[head] = 1
    parts = [dict(id='body', label='白衬衣与黑金连体衣', section='body', pivot=[0, 11.2, -.33872], parent='root'),
             dict(id='head', label='原作头脸、蒙眼与双锥发饰', section='head', pivot=[0, 15.3734, .0611386], parent='body')]
    for side, suffix in ((1, 'l'), (-1, 'r')):
        selected = (~head) & (np.sign(source[:, 0]) == side)
        arm = selected & (x >= 1.7) & (y >= 10.1)
        arm_regions = [arm & (x < 3.33716), arm & (x >= 3.33716) & (x < 5.39027), arm & (x >= 5.39027)]
        arm_definitions = [('arm', '黑袖上臂与肘甲', 'arms', [side*1.28073, 14.8692, .061979], 'body'),
                           ('forearm', '黑袖前臂', 'arms', [side*3.33716, 13.3428, .112456], f'arm_{suffix}'),
                           ('hand', '金色机械五指手', 'hands', [side*5.39027, 11.8216, -.00259867], f'forearm_{suffix}')]
        leg = selected & ~arm & ((y < 9.4) | ((y < 10.3815) & (x >= .45)))
        leg_regions = [leg & (y >= 6.26083), leg & (y < 6.26083) & (y >= 1.89844), leg & (y < 1.89844)]
        leg_definitions = [('thigh', '深色大腿与髋部关节', 'legs', [side*.814937, 10.3815, -.236867], 'body'),
                           ('shin', '深色膝甲与小腿', 'legs', [side*.824818, 6.26083, -.0532002], f'thigh_{suffix}'),
                           ('foot', '黑金厚底鞋', 'legs', [side*.783812, 1.89844, .428896], f'shin_{suffix}')]
        for region, (name, label, section, pivot, parent) in zip(arm_regions+leg_regions, arm_definitions+leg_definitions):
            owners[region] = len(parts)
            parts.append(dict(id=f'{name}_{suffix}', label=('左' if side == 1 else '右')+label,
                              section=section, pivot=pivot, parent=parent))
    result = []
    for index, definition in enumerate(parts):
        definition = definition.copy()
        pivot = np.array(definition.pop('pivot'))*scale
        pivot[2] *= -1
        metadata = dict(section=definition.pop('section'), pivot=pivot.tolist(), parent=definition.pop('parent'),
                        source='原网格对应关节附近的静态体素分区')
        mask = owners == index
        result.append(SimpleNamespace(name=definition['id'], label=definition['label'], p=xyz[mask], states=states[mask], metadata=metadata))
    return result, palette()
