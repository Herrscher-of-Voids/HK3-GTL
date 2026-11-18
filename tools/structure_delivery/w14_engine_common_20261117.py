import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from author_w05_shapes_20261115 import Part
from w08_common_20261116 import rod


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W14_行星发动机基座_E1_20261117'
LOG = ROOT / 'logs/0005-w14-planet-engine-e1-20261117'
BLACK, STUDS, GRAY, SILVER, VENT, CLEAN, WHITE, YELLOW, BLUE, CYAN_GLASS, LIGHT, COMPUTER, ADVANCED, WSV, CONTROL, BLUE_LIGHT, PURPLE_LIGHT, GLASS, STONE, MOSS, DIRT, LOG_BLOCK, LEAVES, SAND, ICE, SNOW, MAGMA, OBSIDIAN, WATER, SEA_LIGHT, AMETHYST, END_STONE, GREEN_LIGHT, RED_LIGHT = range(1, 35)
CONTROLLER = [0, 44, 610]
NOZZLE = [0, 330, 0]
FACES = ['east', 'west', 'south', 'north', 'down', 'up']


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def png_material(state, label, png, source, transparent=False, emissive=False):
    return dict(state=state, label=label, faces={face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in FACES},
                transparent=transparent, emissive=emissive, source={**source, 'png_sha256': hashlib.sha256(png).hexdigest()})


def materials():
    old = json.loads((ROOT / 'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117/materials.json').read_text('utf8'))
    selected = [0, 1, 2, 3, 10, 11, 12, 18, 30, 31, 32, 33, 34]
    result = [deepcopy(old[i]) for i in selected]
    names = ['深色承力装甲', '黑色铆钉骨架', '灰色分节机械板', '浅灰金属包边', '散热百叶', '洁净机械面板', '白色检修标识', '琥珀警示灯',
             '蓝色冷却管壳', '青色观察窗', '白色状态灯', '分布控制模组', '中心运算机匣']
    for item, name in zip(result, names):
        item['label'] = name
    path = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/wsv/casing.png'
    result.append(png_material('hk3gtl:voltage_machine_casing_wsv', '世界维系压月华紫机壳', path.read_bytes(), dict(kind='hk', entry=str(path.relative_to(ROOT)))))
    result.append(deepcopy(old[35]))
    gt = Path(old[0]['source']['archive'])
    with ZipFile(gt) as archive:
        for color, label in [('light_blue', '浅蓝聚变辉光'), ('purple', '紫色轮回指示')]:
            entry = f'assets/gtceu/textures/block/lamps/{color}_borderless.png'
            result.append(png_material(f'gtceu:{color}_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]', label, archive.read(entry), dict(kind='gt', archive=str(gt), entry=entry), emissive=True))
    mc = Path(old[15]['source']['archive'])
    blocks = [('glass', '世界泡透明外壳', True), ('stone', '山岩世界地层', False), ('moss_block', '森林世界苔地', False),
              ('dirt', '世界泡土层', False), ('oak_log', '森林树干', False), ('azalea_leaves', '森林树冠', False),
              ('sand', '沙漠世界沙层', False), ('packed_ice', '冰原世界冰层', False), ('snow_block', '冰原积雪', False),
              ('magma_block', '熔融世界裂隙', False), ('obsidian', '熔融世界黑岩', False), ('blue_stained_glass', '海洋世界水面', True),
              ('sea_lantern', '海洋与进料照明', False), ('amethyst_block', '结晶世界晶岩', False), ('end_stone', '荒原世界浅岩', False)]
    with ZipFile(mc) as archive:
        for block, label, transparent in blocks:
            texture = {'oak_log': 'oak_log', 'magma_block': 'magma', 'snow_block': 'snow'}.get(block, block)
            entry = f'assets/minecraft/textures/block/{texture}.png'
            state = 'minecraft:' + block
            if block == 'oak_log':
                state += '[axis=y]'
            if block == 'azalea_leaves':
                state += '[distance=1,persistent=true,waterlogged=false]'
            result.append(png_material(state, label, archive.read(entry), dict(kind='mc', archive=str(mc), entry=entry), transparent, block in ['magma_block', 'sea_lantern']))
    with ZipFile(gt) as archive:
        for color, label in [('green', '森林供料指示'), ('red', '退役世界供料指示')]:
            entry = f'assets/gtceu/textures/block/lamps/{color}_borderless.png'
            result.append(png_material(f'gtceu:{color}_borderless_lamp[bloom=true,inverted=true,lit=true,powered=false]', label, archive.read(entry), dict(kind='gt', archive=str(gt), entry=entry), emissive=True))
    return result


def radial(u, y, v, angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([u * c - v * s, y, u * s + v * c])


def radial_box(part, u0, u1, v0, v1, y0, y1, angle, state):
    corners = np.array([radial(u, 0, v, angle) for u in [u0, u1] for v in [v0, v1]])
    low, high = np.floor(corners.min(0)).astype(int), np.ceil(corners.max(0)).astype(int)
    z, x = np.mgrid[low[2]:high[2] + 1, low[0]:high[0] + 1]
    u, v = x * np.cos(angle) + z * np.sin(angle), -x * np.sin(angle) + z * np.cos(angle)
    inside = (u >= u0) & (u <= u1) & (v >= v0) & (v <= v1)
    xx, zz = x[inside], z[inside]
    for y in range(y0, y1 + 1):
        part.points(np.c_[xx, np.full(len(xx), y), zz], state)


def ring_slice(part, y, outer, inner, state, start=0, end=2 * np.pi):
    angles = [start, end, *[i * np.pi / 2 for i in range(5) if start < i * np.pi / 2 < end]]
    corners = np.array([[r * np.cos(a), r * np.sin(a)] for a in angles for r in [inner, outer]])
    low, high = np.floor(corners.min(0)).astype(int), np.ceil(corners.max(0)).astype(int)
    z, x = np.mgrid[low[1]:high[1] + 1, low[0]:high[0] + 1]
    r2 = x * x + z * z
    theta = np.mod(np.arctan2(z, x), 2 * np.pi)
    mask = (r2 <= outer * outer) & (r2 >= inner * inner) & (theta >= start) & (theta < end)
    part.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]], state)
