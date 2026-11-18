from types import SimpleNamespace

import numpy as np
from scipy.ndimage import distance_transform_cdt

import geometry_0005_w05_wendy_wings_a2_20261115 as a2
from geometry_0005_w05_wendy_wings_a2_20261115 import STATES, NAMES, ROLES, PARTS


def deck():
    points, values = [], []
    tiers = [(500, 420, -24, -17), (485, 405, -16, -1), (470, 390, 0, 11)]
    for half_width, half_depth, bottom, top in tiers:
        z, x = np.mgrid[30-half_depth:31+half_depth, -half_width:half_width+1]
        edge = np.minimum.reduce([half_width-abs(x), half_depth-abs(z-30),
                                  (half_width+half_depth-68-abs(x)-abs(z-30))/2**.5])
        footprint = edge >= 0
        for y in range(bottom, top+1):
            mask = footprint.copy()
            state = np.full(x.shape, a2.IDS[a2.BLACK], np.uint8)
            if bottom == -24:
                if -20 <= y <= -18:
                    state[:] = a2.IDS[a2.GRAY]
            elif bottom == -16:
                mask &= (edge <= 14) | (abs(x) <= 12) | (abs(z-30) <= 12)
                if -12 <= y <= -10:
                    state[:] = a2.IDS[a2.WHITE]
                if -9 <= y <= -6:
                    state[:] = a2.IDS[a2.GREEN]
            else:
                if y >= 8:
                    state[:] = a2.IDS[a2.WHITE]
                if y >= 9:
                    state[edge >= 8] = a2.IDS[a2.GREEN]
                if y >= 10:
                    state[edge >= 18] = a2.IDS[a2.GRAY]
                if y == 11:
                    for side in (-1, 1):
                        for lane in (174, 320):
                            state[(abs(x-side*lane) <= 2) & (z >= -176) & (z <= 85)] = a2.IDS[a2.BLACK]
                        for marker in range(-294, 365, 28):
                            state[(abs(x-side*44) <= 2) & (z >= marker) & (z <= marker+12)] = a2.IDS[a2.WHITE]
                        for marker in range(-288, 370, 94):
                            state[(abs(x-side*431) <= 4) & (z >= marker) & (z <= marker+9)] = a2.IDS[a2.LIGHT]
                    state[(abs(x) <= 28) & (z >= 170) & (z <= 365)] = a2.IDS[a2.BLACK]
                    state[(abs(abs(x)-31) <= 1) & (z >= 170) & (z <= 366)] = a2.IDS[a2.WHITE]
            points.append(np.c_[x[mask], np.full(mask.sum(), y), z[mask]].astype(np.int32))
            values.append(state[mask])
    return SimpleNamespace(name='deck', p=np.concatenate(points), states=np.concatenate(values))


def build():
    old_deck = a2.deck
    a2.deck = deck
    cube, owners, data = a2.build()
    a2.deck = old_deck
    low = np.array(data['source_blueprint_bounds']['min'])
    footprint = owners[11-low[1]] == 1
    projection = (owners > 1).any(axis=0)
    outside = int(np.count_nonzero(projection & ~footprint))
    margin = int(distance_transform_cdt(footprint, metric='chessboard')[projection].min())-1
    if outside:
        raise ValueError('上部投影超出顶层底座：'+str(outside))
    PARTS[0]['name'] = '扩展三层承托基座'
    data.update(title='风之律者 · 长风 · 温蒂风翼与渴望之心 A3 · 扩展基座', name='0005-w05-wendy-wings-a3')
    data['summary'] = '三层基座扩大至1001×841格，顶层941×781格，向下增厚24格；中央宝石、十四片风翼、风车纹章及机组沿用A2原位，四周保留明确的承托外沿。全静态。'
    data['geometry_clearance']['base_projection'] = dict(
        bottom_size_wd=[1001, 841], middle_size_wd=[971, 811], top_size_wd=[941, 781],
        top_blueprint_y=11, bottom_blueprint_y=-24,
        upper_projected_columns=int(projection.sum()), outside_top_deck_columns=outside,
        minimum_projected_border_margin_voxels=margin,
        upper_geometry='沿用A2的全部上部构件函数和原蓝图坐标，仅替换deck；导出原点随底座范围调整。')
    data['geometry_clearance']['intentional_joins'] = '三层基座分占Y=-24..-17、-16..-1、0..11；上部落地构件仍从Y=12起按面相接。羽片及风车叶片的独立净距沿用A2。'
    print('底座投影核对', outside, '越界列，最小边缘余量', margin, '格', flush=True)
    return cube, owners, data
