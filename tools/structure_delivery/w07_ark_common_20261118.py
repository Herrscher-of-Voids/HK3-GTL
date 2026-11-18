# -*- coding: utf-8 -*-
from copy import deepcopy
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from author_w05_shapes_20261115 import Part
from w08_common_20261116 import rod
from w14_engine_common_20261117 import png_material, save


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W07_黑白生息方舟_N1_20261118'
LOG = ROOT / 'logs/0005-w07-noah-n1-20261118'
DARK, RIB, ASH, SILVER, CLEAN, WHITE, GRATE, MACHINE, GLASS, LIGHT, LOG_BLOCK, LEAVES, MOSS, SOIL, FLOWER, CORE, CONTROL = range(1, 18)
CONTROLLER = [0, 21, 553]


def materials():
    old = json.loads((ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118/materials.json').read_text('utf8'))
    states = ['gtceu:black_metal_sheet', 'gtceu:black_studs', 'gtceu:gray_metal_sheet',
        'gtceu:light_gray_metal_sheet', 'gtceu:clean_machine_casing', 'gtceu:white_metal_sheet',
        'gtceu:computer_heat_vent', 'gtceu:computer_casing', 'minecraft:glass',
        'gtceu:white_lamp[bloom=true,inverted=true,lit=true,powered=false]',
        'minecraft:oak_log[axis=y]', 'minecraft:oak_leaves[distance=1,persistent=true,waterlogged=false]',
        'minecraft:moss_block', 'minecraft:dirt', 'minecraft:calcite']
    palette = [deepcopy(next(m for m in old if m['state'] == state)) for state in states]
    labels = ['凋亡黑色装甲', '承力铆钉肋架', '失活灰色机械板', '银灰结构包边', '洁净再造机壳',
        '创生白色装甲', '分解散热格栅', '分选重编程机匣', '生命舱观察玻璃', '再制造白色灯带',
        '原生木质枝干', '生命舱绿色树冠', '生态甲板苔地', '封闭种植土层', '白花方块花瓣']
    for m, label in zip(palette, labels):
        m['label'] = label
    path = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/civ/casing.png'
    palette.append(png_material('hk3gtl:voltage_machine_casing_civ', '文明工程压再生机壳', path.read_bytes(),
        dict(kind='hk', entry=str(path.relative_to(ROOT)))))
    palette.append(deepcopy(next(m for m in old if m['state'] == 'minecraft:redstone_block')))
    return palette


def width_at(z):
    t = abs(z) / (505 if z >= 0 else 600)
    return 195 * max(0, 1 - t ** (1.7 if z >= 0 else 2)) ** .65


def bottom_at(z):
    return 43 + round(105 * (abs(z) / 505) ** 3)


def deck_at(z):
    t = abs(z) / 505
    return 184 + round(21 * t ** 4 + (20 * t ** 6 if z > 0 else 0))


def radius_at(y, z):
    u = np.clip((np.asarray(y) - bottom_at(z)) / (deck_at(z) - bottom_at(z)), 0, 1)
    return 9 + (width_at(z) - 9) * u ** .6


def polyline(part, points, radius, state):
    for a, b in zip(points[:-1], points[1:]):
        rod(part, a, b, radius, state)


def framed_box(part, low, high, shell, frame, thickness=3):
    x0, y0, z0 = low
    x1, y1, z1 = high
    part.box(low, [x1, y0 + thickness - 1, z1], shell)
    part.box([x0, y1 - thickness + 1, z0], high, shell)
    for x in [x0, x1 - thickness + 1]:
        part.box([x, y0, z0], [x + thickness - 1, y1, z1], frame)
    for z in [z0, z1 - thickness + 1]:
        part.box([x0, y0, z], [x1, y1, z + thickness - 1], frame)
