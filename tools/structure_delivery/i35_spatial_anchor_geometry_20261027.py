# -*- coding: utf-8 -*-
"""I35四爪沉楔锚台：十字反力基座、四向液压锁爪与穿界锚芯。

变更记录 #1（2026-10-27）：独立新候选，未修改正式建筑、控制器或实例。
"""
import math
from pathlib import Path

import numpy as np
import i34_imaginary_tree_array_geometry_20261027 as material

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 451, 241, 401
CX, CZ = 225, 200
NAME = 'hk3gtl-i35-spatial-anchor-v1-20261027'
TITLE = '虚数空间锚定阵列 · 四爪沉楔锚台'
STATES = sorted(material.PALETTE_ROLES)
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = dict(material.PALETTE_ROLES)
ROLES.update({material.IRV: '十字反力台、锁爪外壳及沉楔锚芯的主体IRV机壳',
             material.ROBUST: '反力台主梁、沉楔锁座与受力轴承',
             material.CLEAN: '锁爪齿边、锚芯防护棱与检修走台护边',
             material.COMPUTER: '锚定状态、载荷误差及复验记录读出',
             material.PROCESS: '魂钢锚件接收与实体校准工位',
             material.DIMENSION: '空间核心组件安装与工作态标定工位',
             material.GLASS: '反力台维护层观察窗',
             material.GOLD: '少量工作态标定接点'})


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (lo, hi)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state]

    def beam(a, b, state, r):
        steps = max(abs(a[i] - b[i]) for i in range(3))
        for k in range(steps + 1):
            p = tuple(round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3))
            box(tuple(v - r for v in p), tuple(v + r for v in p), state)

    zz, xx = np.mgrid[:D, :W]
    dx, dz = abs(xx - CX), abs(zz - CZ)
    # 反力基座采用十字长梁与中央八角锁井，端部收尖而不围成厂区。
    for y in range(65):
        setback = (y // 22) * 5
        cross = (((dx <= 225 - setback) & (dz <= 83 - setback) & (dx + dz < 274 - setback)) |
                 ((dx <= 87 - setback) & (dz <= 200 - setback) & (dx + dz < 267 - setback)) |
                 ((np.maximum(dx, dz) < 139 - setback) & (dx + dz < 212 - setback)))
        skin = cross & ~(((dx < 219 - setback) & (dz < 77 - setback)) |
                         ((dx < 81 - setback) & (dz < 194 - setback)) |
                         ((np.maximum(dx, dz) < 133 - setback) & (dx + dz < 204 - setback)))
        # 三层厚反力楼板夹着检修层，厚度服务巨大锁爪的受力传递。
        floor = y < 16 or 24 <= y < 39 or 47 <= y
        if floor:
            cube[y, cross] = IDS[material.IRV]
        else:
            ribs = cross & ((dx % 34 < 8) | (dz % 38 < 8) | (abs(dx - dz) < 8))
            cube[y, ribs | skin] = IDS[material.IRV]
            if y in (19, 20, 42, 43):
                cube[y, skin & (dx % 34 > 10) & (dz % 38 > 11)] = IDS[material.GLASS]
        if y in (15, 38, 64):
            cube[y, cross & ~skin] = IDS[material.ASSEMBLY]
            cube[y, skin] = IDS[material.ROBUST]
        if y in (3, 25, 48):
            cube[y, cross & ((dx < 12) | (dz < 12))] = IDS[material.ROBUST]
        if y in (16, 39):
            cube[y, cross & (dx % 34 < 7)] = IDS[material.PLASCRETE]
    # 四只低位反力铰座与交叉斜撑，向内咬住中央锚芯而不是支撑外圈厂房。
    for sx in (-1, 1):
        for sz in (-1, 1):
            foot = (CX + sx * 124, 64, CZ + sz * 108)
            shoulder = (CX + sx * 41, 167, CZ + sz * 37)
            box((foot[0] - 26, 25, foot[2] - 24), (foot[0] + 26, 76, foot[2] + 24), material.IRV)
            box((foot[0] - 29, 65, foot[2] - 27), (foot[0] + 29, 78, foot[2] + 27), material.GEAR)
            beam(foot, shoulder, material.IRV, 18)
            # 双侧洁净护边沿实际受力方向延伸，冷蓝槽仅作细窄工作态导光。
            for offset in (-17, 17):
                a = (foot[0] + offset, foot[1] + 4, foot[2])
                b = (shoulder[0] + offset, shoulder[1] + 4, shoulder[2])
                beam(a, b, material.CLEAN, 2)
            beam((foot[0], 80, foot[2] - sz * 9),
                 (shoulder[0], 183, shoulder[2] - sz * 9), material.ROBUST, 6)
            beam((foot[0], 83, foot[2] - sz * 9),
                 (shoulder[0], 186, shoulder[2] - sz * 9), material.BLUE_GLASS, 2)
            # 多段液压压套和内向钩齿，关节和梁是一体连续构造。
            for k in (1, 3, 5):
                t = k / 6
                p = tuple(round(foot[i] + (shoulder[i] - foot[i]) * t) for i in range(3))
                box((p[0] - 23, p[1] - 5, p[2] - 22), (p[0] + 23, p[1] + 5, p[2] + 22), material.STRESS)
                box((p[0] - 20, p[1] + 6, p[2] - 18), (p[0] + 20, p[1] + 8, p[2] + 18), material.IRV)
            beam(shoulder, (CX + sx * 17, 181, CZ + sz * 17), material.IRV, 13)
            beam((CX + sx * 17, 181, CZ + sz * 17),
                 (CX + sx * 14, 151, CZ + sz * 14), material.CLEAN, 6)

    # 中央八角沉楔：上端为多级锁头，下端向工作井内收尖；无世界球或树影复用。
    radius = np.maximum(dx, dz) + np.minimum(dx, dz) * .43
    for y in range(56, H):
        if y < 109:
            r = 8 + (y - 56) * .39
        elif y < 196:
            r = 30 + (y - 109) * .08
        else:
            r = 47 if y < 222 else 40 if y < 233 else 32
        mask = radius <= r
        cube[y, mask] = IDS[material.IRV]
        edges = mask & (radius > r - 3)
        cube[y, edges] = IDS[material.CLEAN]
        if y < 198 and y % 21 < 4:
            cube[y, mask] = IDS[material.ROBUST]
        # 八角锚芯中轴开出窄工作态槽，避免整根成为无细节实心柱。
        for side in (-1, 1):
            z = CZ + side * round(r - 2)
            box((CX - 4, y, z), (CX + 4, y, z), material.BLACK_GLASS)
            if y % 21 > 5:
                box((CX - 1, y, z + side), (CX + 1, y, z + side), material.BLUE_GLASS)
    # 锚芯下方的方位锁盘是实体工装，工作平面不代表新增传送能力。
    for y in range(65, 77):
        outer = (radius < 73) & (radius >= 37)
        cube[y, outer] = IDS[material.ROBUST if y < 69 else material.IRV]
    for direction in range(4):
        angle = direction * math.pi / 2
        for j in range(5):
            r = 47 + j * 4
            x = round(CX + math.cos(angle) * r); z = round(CZ + math.sin(angle) * r)
            box((x - 5, 77, z - 5), (x + 5, 80, z + 5), material.CLEAN if j % 2 else material.GEAR)
    # 四条径向检修脊与真实负载/冷却设备，全部收在反力梁内或梁顶。
    equipment = [material.COMPUTER, material.POWER, material.PROCESS, material.DIMENSION,
                 material.MULTI, material.FILTER, material.INERT, material.HEATPROOF,
                 material.INSULATE, material.FROST, material.STABLE, material.INTAKE,
                 material.MIXING, material.LAFIUM, material.TURBINE, material.MACERATOR,
                 material.VENT, material.TUNG_PIPE, material.STEEL_PIPE, material.IRIDIUM,
                 material.SOLID, material.VIBRATION, material.LASER, material.ATOMIC,
                 material.BLACK, material.GOLD, material.GRATE]
    for i, state in enumerate(equipment):
        x = CX - 61 if i % 2 else CX - 103
        z = 80 + (i % 9) * 30
        y = 17 if i < 9 else 40 if i < 18 else 65
        for mx in (x, W - 1 - x):
            box((mx - 7, y, z - 7), (mx + 7, y + 6, z + 7), state)
            box((mx - 8, y - 1, z - 8), (mx + 8, y - 1, z + 8), material.VIBRATION)
            box((mx - 7, y + 7, z - 7), (mx + 7, y + 8, z + 7), material.IRV)
    # 一体北向锚件接收鼻台；主控和接口在同一连续实体外墙上齐平嵌入。
    box((CX - 62, 5, 8), (CX + 62, 43, 73), material.IRV)
    box((CX - 59, 44, 8), (CX + 59, 46, 73), material.CLEAN)
    box((CX - 57, 19, 8), (CX + 57, 30, 8), material.BLACK_GLASS)
    box((CX - 55, 32, 8), (CX + 55, 32, 8), material.LIGHT)
    # 后端为合格组件与状态记录的分别交付区，与反力梁连成一体。
    box((CX - 62, 5, D - 74), (CX + 62, 43, D - 9), material.IRV)
    box((CX - 59, 44, D - 74), (CX + 59, 46, D - 9), material.CLEAN)
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    controller = [CX, 24, 8]
    ports = [dict(id='魂钢锚件输入', pos=[CX - 24, 24, 8], face='north'),
             dict(id='空间核心组件输入', pos=[CX + 24, 24, 8], face='north'),
             dict(id='I34校准资料输入', pos=[CX - 48, 24, 8], face='north'),
             dict(id='锚定验证资料输入', pos=[CX + 48, 24, 8], face='north'),
             dict(id='西侧锚定供能', pos=[5, 28, CZ - 25], face='west'),
             dict(id='东侧锚定供能', pos=[W - 6, 28, CZ - 25], face='east'),
             dict(id='西侧稳定介质', pos=[5, 28, CZ + 25], face='west'),
             dict(id='东侧介质回流', pos=[W - 6, 28, CZ + 25], face='east'),
             dict(id='合格锚定组件输出', pos=[CX - 24, 24, D - 9], face='south'),
             dict(id='锚定状态与记录输出', pos=[CX + 24, 24, D - 9], face='south')]
    direction = {'north': (0, 1), 'south': (0, -1), 'west': (1, 0), 'east': (-1, 0)}
    for item in [dict(pos=controller, face='north', id='主控')] + ports:
        x, y, z = item['pos']; ix, iz = direction[item['face']]
        box((x - 2 if not ix else min(x, x + ix), y - 2, z - 2 if ix else min(z, z + iz)),
            (x + 2 if not ix else max(x, x + ix), y + 2, z + 2 if ix else max(z, z + iz)), material.IRV)
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        for k in range(1, 6):
            ox, oz = x - ix * k, z - iz * k
            if 0 <= ox < W and 0 <= oz < D:
                cube[y, oz, ox] = 0
        item['purpose'] = item['id'] + '候选；真实能力按正式Pattern另验'
    paths = [dict(name='锚件接收操作通廊', min=[CX - 59, 21, 3], max=[CX + 59, 27, 7]),
             dict(name='物料与证据交付通廊', min=[CX - 59, 21, D - 8], max=[CX + 59, 27, D - 4])]
    for route in paths:
        x, y, z = route['min']; X, Y, Z = route['max']
        cube[y:Y + 1, z:Z + 1, x:X + 1] = 0
    missing = [s for s, ident in IDS.items() if not np.any(cube == ident)]
    assert not missing, ('设备材料没有放置', missing)
    data = dict(key='i35', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
                controller_face='north', ports=ports, paths=paths,
                zones=[dict(name='中央八角沉楔锚芯', pos=[CX + 15, 215, CZ]),
                       dict(name='四向内收液压锁爪', pos=[CX - 80, 120, CZ - 72]),
                       dict(name='十字反力梁与层间检修空间', pos=[CX, 64, 100]),
                       dict(name='魂钢锚件及空间核心接收台', pos=[CX, 43, 30]),
                       dict(name='组件与状态分离交付台', pos=[CX, 43, D - 30])],
                description='十字反力梁向四个方向展开，四套斜向液压锁爪从落地铰座收拢，咬合中央向下贯入锁井的八角沉楔锚芯。多级夹头、轴承、载荷读出和冷却回路围绕实际受力路线组织；前后鼻台承担物料与证据的分别交接，整机没有外围厂房围墙。',
                construction_notes=dict(orientation='主控北向/-Z，蓝图坐标从0起算。', anchor='推荐世界Y=-60，实体最高Y=180。',
                    boundary='接收真实魂钢锚件、空间核心、I34校准资料、能源及稳定介质；标定和验证，物料与证据分别输出。不制造免费锚件、不新增传送能力，不绕过I44/I45或终审维度禁行。',
                    approval='独立建筑候选，未获负责人批准、未接入实例。'))
    return cube, data


if __name__ == '__main__':
    c, d = build()
    print(dict(size=d['size'], blocks=int(np.count_nonzero(c)), materials=len(np.unique(c)) - 1,
               irv=int(np.count_nonzero(c == IDS[material.IRV]))), flush=True)
