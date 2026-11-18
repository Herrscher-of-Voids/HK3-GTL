# -*- coding: utf-8 -*-
from pathlib import Path
import math

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116/模型补充'


def picture(view):
    rgb = np.asarray(Image.open(REF / f'official-mmd-case-{view}.png').convert('RGB'))
    mask = np.max(np.abs(rgb.astype(int) - rgb[0, 0].astype(int)), axis=2) > 4
    mask[1740:] = False
    return rgb, mask


def material(rgb):
    r, g, b = map(int, rgb)
    if r > g * 1.55 and r > 72:
        return 5 if r > 130 else 6
    if r > 173 and g > 150:
        return 3
    if r > 137 and g > 120 and b > 125:
        return 4
    if b > r * 1.08 and b > g * 1.04:
        return 13
    return 1 if max(r, g, b) < 58 else 12


def build():
    front, mask = picture('front')
    back, _ = picture('back')
    side, side_mask = picture('right')
    rows, columns = np.nonzero(mask)
    scale = 626 / (rows.max() - rows.min())
    ymin, xmin = int(rows.min()), int(columns.min())
    width = math.ceil((columns.max() - xmin) * scale)
    voxels = {}
    distances = cv2.distanceTransform(mask.astype('uint8'), cv2.DIST_L2, 5)
    side_rows = np.flatnonzero(side_mask.any(axis=1))
    projected_x = np.rint((columns - xmin) * scale).astype(int)
    projected_y = np.rint((rows - ymin) * scale).astype(int)
    cells, samples = np.unique(projected_y * (width + 1) + projected_x, return_index=True)
    present = np.zeros((627, width + 1), bool)
    source_y = np.zeros_like(present, dtype=int)
    source_x = np.zeros_like(present, dtype=int)
    present.flat[cells] = True
    source_y.flat[cells], source_x.flat[cells] = rows[samples], columns[samples]
    for y in range(627):
        py = round(ymin + y / scale)
        side_y = int(side_rows[np.argmin(abs(side_rows - py))])
        side_columns = np.flatnonzero(side_mask[side_y])
        center = (int(side_columns[0]) + int(side_columns[-1])) / 2
        for x in np.flatnonzero(present[y]):
            px = round(xmin + x / scale)
            sy, sx = (py, px) if mask[py, px] else (source_y[y, x], source_x[y, x])
            thickness = max(1, round((len(side_columns) - 1) * scale / 2 *
                min(1, distances[sy, sx] * scale / 2.5)))
            offset = round((center - 900) * scale)
            face = material(front[sy, sx])
            reverse = material(back[sy, 1799 - sx])
            for z in range(offset - thickness, offset + thickness + 1):
                side_x = round(center - (z - offset) / scale)
                color = face if z == offset + thickness else reverse if z == offset - thickness else material(side[side_y, side_x])
                voxels[int(x) - width // 2, y, z] = color
    voxels = {(x, 626 - y, z): value for (x, y, z), value in voxels.items()}
    return [dict(id='case', title='大剑形武器匣 · 双面太极云火纹', voxels=voxels,
        features=['依据官方公开MMD正交观察图重建，修正旧照片透视造成的轮廓偏移。',
            '正背两面分别取样太极、云火纹与圆晶，背面恢复完整饰纹。',
            '每层厚度按右侧投影生成，红色中脊、灰紫壳体和收薄边缘均为实体格。',
            '方块材质逐格重复，原始模型网格与贴图仅用于观察。'],
        references=['MMD-case-front','MMD-case-back','MMD-case-right','MMD-case-oblique',
            'MMD-case_roundels-front','MMD-case_tip-oblique'],
        views=dict(taiji=dict(target=[-12, 249, 17], radius=60),
            tip=dict(target=[3, 559, 0], radius=75),
            rim=dict(target=[17, 390, 0], radius=72)))]
