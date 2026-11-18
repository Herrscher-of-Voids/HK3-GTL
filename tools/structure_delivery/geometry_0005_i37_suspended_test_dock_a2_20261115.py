# -*- coding: utf-8 -*-
import geometry_0005_i37_suspended_test_dock_a1_20261115 as a1
from geometry_0005_i37_suspended_test_dock_a1_20261115 import STATES, NAMES, ROLES

PARTS = [dict(part) for part in a1.PARTS]
PARTS[4]['name'] = '前后双态样件与交换台'


def build():
    a, owners, data = a1.build()
    a[111:127, 365:431, 195:261] = a1.OBSIDIAN
    heat = a[66:122, 554:573, 147:195]
    heat[heat == a1.COLD] = a1.HOT
    a[172:195, 626:649, 231:278] = a1.INTAKE
    a[116:156, 668:681, 231:255] = a1.MULTI
    a[:, :, 281:] = a[:, :, :280][:, :, ::-1]
    owners[:, :, 281:] = owners[:, :, :280][:, :, ::-1]
    data.update(
        title='世界维系试验平台 · 悬箱稳界试验坞 A2',
        name='0005-i37-suspended-test-dock-a2',
        symmetry=dict(axis='x', plane=280, source_half='left', mapping='x -> 560 - x'),
        sample_layout='前排双侧参考态，后排双侧扰动态；冷热调理与循环机组均成对镜像。',
    )
    return a, owners, data
