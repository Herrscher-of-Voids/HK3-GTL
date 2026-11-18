# -*- coding: utf-8 -*-
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116/模型补充'


def projection(view, width):
    pixels = np.asarray(Image.open(SOURCE / f'official-mmd-chain-{view}.png').convert('RGB'))[:1740]
    mask = np.max(np.abs(pixels.astype(int) - pixels[0, 0]), axis=2) > 8
    ys, xs = np.nonzero(mask)
    bounds = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    image = Image.fromarray(pixels).crop(bounds)
    silhouette = Image.fromarray(mask.astype('uint8') * 255).crop(bounds)
    colors = np.array(image.resize((width, 360), Image.Resampling.BOX))
    dark = Image.fromarray((pixels.max(axis=2) < 45).astype('uint8') * 255).crop(bounds)
    colors[np.asarray(dark.resize((width, 360), Image.Resampling.BOX)) > 32] = 24
    occupied = np.asarray(silhouette.resize((width, 360), Image.Resampling.NEAREST)) > 0
    return colors, occupied


def material(color):
    r, g, b = map(int, color)
    if r > g * 1.5 and r > b * 1.3:
        return 5 if r > 145 else 6
    if max(r, g, b) < 56:
        return 1
    if r > 145 and g > 125:
        return 3 if r > 200 else 4
    return 13 if r > 105 and b > r + 5 else 12


def build():
    front, front_mask = projection('front', 48)
    back, back_mask = projection('back', 48)
    side, side_mask = projection('right', 18)
    voxels = {}
    for row in range(360):
        columns = np.flatnonzero(front_mask[row] | back_mask[row])
        depth = np.flatnonzero(side_mask[row])
        left, right = columns[0], columns[-1]
        for column in columns:
            edge = min(column - left, right - column)
            inset = int(edge < 1 and len(depth) > 4)
            first, last = depth[0] + inset, depth[-1] - inset
            face = material(front[row, column])
            rear = material(back[row, 47 - column])
            if row < 230:
                first += int(rear == 1)
                last -= int(face == 1)
            for level in range(first, last + 1):
                value = material(side[row, level])
                if level == first:
                    value = rear
                if level == last:
                    value = face
                voxels[int(column) - 24, 359 - row, int(level) - 9] = value
    return [dict(
        id='chain', title='链剑 · 九段收束态', voxels=voxels,
        features=[
            '按官方公开MMD的正面、背面与右侧轮廓逐格采样，保留扁平截面和实际层叠边缘。',
            '九段灰黑斜片相互交叠，八处红色V形节间与根部红色X形束带分别呈现。',
            '黑色菱形护手、双侧白纹、骨白卷叉与红白交缠圆柄完整保留。',
            '全长360格，宽48格、厚18格；整数格尺寸按官方模型比例1.892899∶14.316109∶0.728778换算。',
            '此件为官方模型静态收束态；立绘中的红片展开状态单列参考。',
        ],
        references=['MMD-chain-front', 'MMD-chain-back', 'MMD-chain-right',
                    'MMD-chain-oblique', 'MMD-chain_hilt-front', 'MMD-chain_joint-front'],
        views=dict(
            chain=dict(target=[0, 180, 0], radius=190),
            chain_tip=dict(target=[0, 336, 0], radius=30),
            chain_links=dict(target=[0, 220, 0], radius=55),
            chain_grip=dict(target=[0, 63, 0], radius=62),
        ),
    )]
