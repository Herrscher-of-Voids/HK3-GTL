# -*- coding: utf-8 -*-
from pathlib import Path
import math

import cv2
import numpy as np
from PIL import Image

import senti_sword_spear_20261116 as old


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116/模型补充'


def material(rgb):
    red, green, blue = map(int, rgb)
    if red > green * 1.55 and red > blue * 1.45:
        return 5 if red > 100 else 6
    if red > 100 and green > 90 and blue < green * 1.04:
        return 3 if red > 190 else 4
    return 9 if red > green * 1.16 else 2


def observed_shape(identity, height, shaft_start):
    images = {view: np.asarray(Image.open(REFERENCE / f'official-mmd-{identity}-{view}.png').convert('RGB'))
              for view in ['front', 'back', 'left']}
    masks = {view: np.abs(rgb.astype(int) - rgb[0, 0].astype(int)).sum(2) > 24
             for view, rgb in images.items()}
    for mask in masks.values():
        mask[:80] = False
        mask[1720:] = False
    vertical = {view: np.nonzero(mask)[0] for view, mask in masks.items()}
    limits = {view: (int(rows.min()), int(rows.max())) for view, rows in vertical.items()}
    rows, columns = np.nonzero(masks['front'])
    top, bottom = int(rows.min()), int(rows.max())
    pitch = (bottom - top) / (height - 1)
    radius = math.ceil(max(abs(columns - 900)) / pitch)
    distance = cv2.distanceTransform(masks['front'].astype('uint8'), cv2.DIST_L2, 5) / pitch
    voxels = {}
    for y in range(height):
        py = round(top + y * pitch)
        sy = round(limits['left'][0] + y * (limits['left'][1] - limits['left'][0]) / (height - 1))
        by = round(limits['back'][0] + y * (limits['back'][1] - limits['back'][0]) / (height - 1))
        side = np.flatnonzero(masks['left'][sy])
        z_low, z_high = round((side[0] - 900) / pitch), round((side[-1] - 900) / pitch)
        width = np.flatnonzero(masks['front'][py])
        center_x = ((width[0] + width[-1]) / 2 - 900) / pitch
        half_x = max(.5, (width[-1] - width[0]) / (2 * pitch))
        for x in range(-radius, radius + 1):
            px = round(900 + x * pitch)
            if masks['front'][py, px]:
                front = material(images['front'][py, px])
                back = material(images['back'][by, 1800 - px])
                if y >= shaft_start:
                    fraction = min(1, abs(x - center_x) / half_x)
                    depth = max(1, round(max(abs(z_low), abs(z_high)) * math.sqrt(1 - fraction * fraction)))
                else:
                    depth = max(1, math.ceil(distance[py, px] * .9))
                low, high = max(z_low, -depth), min(z_high, depth)
                for z in range(low, high + 1):
                    side_rgb = images['left'][sy, round(900 + z * pitch)]
                    voxels[x, y, z] = front if z == high else back if z == low else material(side_rgb)
    return voxels


def sword():
    model = old.sword()
    model.update(voxels=observed_shape('sword', 324, 246), features=[
        '依据官方公开模型正、背、侧视逐格采样细长红黑刃，保持完整色区。',
        '骨白双卷外缘包围灰黑三瓣中心，护手的上尖、下卷与深色凹面分别保留。',
        '红白菱纹圆柄、骨白柄尾与卷形护手按同一比例重建。',
        '刃、护手及柄部以侧视厚度生成整数格截面，原生方块纹理逐格重复。',
    ], references=['R2-M-sword-front', 'R2-M-sword-back', 'R2-M-sword-left', 'R2-CG1', 'R15', 'R18'],
        views=dict(guard=dict(target=[0, 218, 0], radius=43),
                   grip=dict(target=[0, 281, 0], radius=44),
                   blade=dict(target=[0, 108, 0], radius=99)))
    return model


def spear():
    model = old.spear()
    model.update(voxels=observed_shape('spear', 552, 278), features=[
        '依据官方公开模型重建长叶枪头、红色交叉束带、左右卷叉与细长收颈。',
        '骨白枪头的浅色刃脊和深色内卷按正面原像素定位，分段长度保持同一比例。',
        '红黑圆杆、骨白长套帽和尾尖按官方正侧视重建，保留环绕缠纹。',
        '正背面色区独立采样，圆杆与枪头厚度随官方侧视轮廓变化。',
    ], references=['R2-M-spear-front', 'R2-M-spear-back', 'R2-M-spear-left', 'R2-CG1', 'R22', 'R23'],
        views=dict(head=dict(target=[0, 139, 0], radius=154),
                   shaft=dict(target=[0, 384, 0], radius=106),
                   cap=dict(target=[0, 508, 0], radius=52)))
    return model


def build():
    models = [sword(), spear()]
    for model in models:
        axes = list(zip(*model['voxels']))
        model['dimensionsXYZ'] = [max(axis) - min(axis) + 1 for axis in axes]
        top = max(axes[1])
        model['voxels'] = {(x, top - y, z): material for (x, y, z), material in model['voxels'].items()}
        for view in model['views'].values():
            view['target'][1] = top - view['target'][1]
    return models
