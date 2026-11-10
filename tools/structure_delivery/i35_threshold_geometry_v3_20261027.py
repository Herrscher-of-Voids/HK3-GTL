# -*- coding: utf-8 -*-
"""I35 V3：保留本维度桥头，悬索桥穿入虚数空间锚定界面。"""
import numpy as np

import i35_suspension_geometry_v2_20261027 as bridge

ROOT, STATES, IDS, material = bridge.ROOT, bridge.STATES, bridge.IDS, bridge.material
ROLES = dict(bridge.ROLES)
ROLES[material.IRV] = '本维度锚室、桥塔、箱梁及虚数界面承力门框'
ROLES[material.GOLD] = '门框少量精密场耦合接点'
W, H, D, CX = 401, 281, 701, 200


def build():
    old, data = bridge.build()
    cube = np.zeros((H, D, W), dtype=np.uint8)
    cube[:old.shape[0], :490] = old[:, :490]
    del old

    def box(lo, hi, state):
        x, y, z = lo; X, Y, Z = hi
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def beam(a, b, state, r):
        steps = max(abs(a[i] - b[i]) for i in range(3))
        for k in range(steps + 1):
            p = [round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3)]
            box(tuple(max(0, v - r) for v in p), tuple(min(n - 1, v + r) for v, n in zip(p, (W, H, D))), state)

    # 远端桥面完整穿过界面；框后留有九十格实体纵深。
    for x in (106, 263):
        box((x, 66, 490), (x + 31, 112, 700), material.IRV)
        box((x + 7, 73, 490), (x + 24, 105, 700), None)
        box((x - 3, 64, 490), (x + 34, 68, 700), material.ROBUST)
        box((x - 3, 111, 490), (x + 34, 115, 700), material.CLEAN)
    box((92, 86, 490), (308, 97, 700), material.IRV)
    box((92, 98, 490), (308, 100, 700), material.ASSEMBLY)
    for z in range(518, 690, 38):
        box((88, 70, z), (312, 85, z + 10), material.IRV)
        box((88, 68, z), (312, 71, z + 10), material.ROBUST)
    for x in (95, 301):
        box((x, 101, 490), (x + 5, 105, 700), material.GRATE)
        box((x, 106, 490), (x + 5, 107, 700), material.CLEAN)
    box((192, 98, 490), (208, 100, 700), material.BLACK)
    box((198, 101, 490), (202, 102, 700), material.BLUE_GLASS)

    # 门框是有厚度的八角环，内区保持敞开，不填实体玻璃背板。
    yy, xx = np.mgrid[:H, :W]
    dx, dy = abs(xx - CX), abs(yy - 140)
    outer = (dx <= 172) & (dy <= 140) & (dx / 172 + dy / 140 <= 1.62)
    inner = (dx <= 145) & (dy <= 128) & (dx / 145 + dy / 128 <= 1.62)
    rim = outer & ~inner
    for z in range(578, 643):
        layer = cube[:, z, :]
        layer[rim] = IDS[material.IRV]
        if z in (578, 579, 580, 581, 639, 640, 641, 642):
            layer[rim] = IDS[material.CLEAN]
        if z in (587, 588, 632, 633):
            layer[rim] = IDS[material.ROBUST]
    # 两侧框脚接地，横向结合桥桁；不增设整片厚底座。
    for x in (80, 284):
        box((x, 0, 570), (x + 36, 15, 650), material.PLASCRETE)
    for y in (66, 112):
        box((28, y, 598), (111, y + 9, 622), material.IRV)
        box((289, y, 598), (372, y + 9, 622), material.IRV)
    for x in (32, 361):
        for y in (96, 166):
            box((x, y, 577), (x + 7, y + 7, 578), material.GOLD)
    for x in (137, 255):
        box((x, 270, 583), (x + 8, 274, 637), material.DIMENSION)

    # 原主缆连续抬升至八角框斜肩的实体索鞍，再进入门后空间。
    for side in (-1, 1):
        a = (CX + side * 111, round(137 + 103 * ((489 - 350) / 175) ** 2), 489)
        b = (CX + side * 130, 245, 610)
        c = (CX + side * 111, 231, 700)
        beam(a, b, material.ROBUST, 5)
        beam(b, c, material.ROBUST, 5)
        x = b[0]
        box((x - 11, 237, 594), (x + 11, 252, 626), material.GEAR)
        for z in range(511, 700, 24):
            t = (z - 489) / 121 if z <= 610 else (z - 610) / 90
            point = tuple(round((a if z <= 610 else b)[i] + ((b if z <= 610 else c)[i] - (a if z <= 610 else b)[i]) * t) for i in range(3))
            x, y, _ = point
            box((x - 2, 100, z - 2), (x + 2, y, z + 2), material.CLEAN)
            beam((x, 100, z), (CX + side * 105, 100, z), material.STRESS, 3)

    # 供能与冷却在近端侧墙分区，输出回到近端锚室后壁。
    controller = [CX, 28, 8]
    ports = [dict(p) for p in data['ports'][:6]]
    ports += [dict(id='西侧稳定介质', pos=[0, 28, 80], face='west'),
        dict(id='东侧介质回流', pos=[400, 28, 80], face='east'),
        dict(id='合格锚定组件输出', pos=[152, 28, 97], face='south'),
        dict(id='锚定状态与记录输出', pos=[248, 28, 97], face='south')]
    for item in [dict(id='主控', pos=controller, face='north')] + ports:
        x, y, z = item['pos']
        cube[y, z, x] = IDS[material.CONTROL if item['id'] == '主控' else material.PORT]
        item['purpose'] = item['id'] + '候选；全部位于本维度可操作设备面，真实仓室能力另验'
    cube[:, :, CX + 1:] = cube[:, :, :CX][:, :, ::-1]
    data.update(name='hk3gtl-i35-threshold-anchor-v3-20261027', title='虚数空间锚定阵列 · 越界悬索桥',
        size=[W, H, D], controller=controller, ports=ports, paths=data['paths'][:1],
        zones=[dict(name='本维度主缆锚碇与标定室', pos=[CX, 78, 36]),
            dict(name='本维度连续门式索塔', pos=[CX, 245, 175]),
            dict(name='连续主缆与垂直吊杆', pos=[89, 137, 350]),
            dict(name='轴向锚桩验证阵列', pos=[CX, 40, 358]),
            dict(name='八角虚数界面承力框', pos=[CX, 279, 610]),
            dict(name='穿入虚数空间的桥面', pos=[CX, 99, 685])],
        portal=dict(center=[200, 140, 610], halfWidth=145, halfHeight=128, depth=90,
            bridgeY=102, bridgeHalfWidth=108, visual_only=True,
            boundary='黑金空间、流纹和隐没桥影仅为HTML非实体效果；不导出NBT、Schematic或Pattern，不提供传送功能。'),
        description='本维度的锚室与单站索塔拉住长桥，桥面和连续主缆穿越厚实八角界面，伸入黑金虚数空间。远端不再出现普通桥头，空间纵深与逐渐隐没的桥影表达锚入另一维度；全部物料与状态接口保留在近端实体设备内。',
        construction_notes=dict(orientation='主控北向/-Z，蓝图坐标从0起算。', anchor='推荐世界Y=-60，最高实体Y=220。',
            boundary='虚数界面为锚定工况的视觉表达；本机不新增传送或维度通行。',
            approval='V2桥概念获肯定后继续修订；V3为独立待审候选，未计入批次、未接入实例。'))
    return cube, data
