# -*- coding: utf-8 -*-
"""I08 悬置棱晶结晶炉；2026-10-14 新增独立建筑候选。"""
from i09_i13_v6_common import start, zone, route, finish, PIPE, GEAR, GRATE, PANEL

WHITE = 'gtceu:clean_machine_casing'
FRAME = 'gtceu:solid_machine_casing'
LILAC = 'hk3gtl:voltage_machine_casing_wsv'
CORE = 'hk3gtl:voltage_machine_casing_imv'
GLASS = 'gtceu:tempered_glass'
VENT = 'gtceu:computer_heat_vent'
POWER = 'gtceu:high_power_casing'


def polygon(a, cx, y, cz, radius, material, width=1):
    """切角方形截面；与连续竖向棱线一起构成棱晶。"""
    cut = max(1, radius//2)
    points = [(cx-radius+cut, y, cz-radius), (cx+radius-cut, y, cz-radius),
              (cx+radius, y, cz-radius+cut), (cx+radius, y, cz+radius-cut),
              (cx+radius-cut, y, cz+radius), (cx-radius+cut, y, cz+radius),
              (cx-radius, y, cz+radius-cut), (cx-radius, y, cz-radius+cut)]
    for p, q in zip(points, points[1:]+points[:1]):
        a.line(p, q, material, width)


def i08():
    a = start('i08', '仿制核心结晶反应室', [45, 40, 43],
              '悬置棱晶、四爪冷端夹架、开放式结晶炉',
              '前驱体计量→下端种晶→透明棱晶生长→顶部冷端约束→前侧取晶')
    cx, cz = 22, 25
    # 局部承台和四条窄工艺基础，中央不用整块铺地。
    a.box((12, 0, 16), (32, 1, 34), FRAME)
    a.box((7, 0, 7), (37, 0, 9), WHITE)
    a.box((20, 0, 8), (24, 0, 17), WHITE)
    for x in (7, 35):
        a.box((x, 0, 9), (x+2, 0, 38), WHITE)
    a.box((7, 0, 36), (37, 0, 38), WHITE)
    for x in (10, 34):
        for z in (14, 36):
            a.box((x-2, 0, z-2), (x+2, 2, z+2), WHITE)
            a.box((x-1, 3, z-1), (x+1, 9, z+1), FRAME)
            # 弯折撑臂向外倾斜，再向内夹持；四爪留出可读的空隙。
            outer_x = 5 if x < cx else 39
            outer_z = 11 if z < cz else 39
            a.line((x, 9, z), (outer_x, 24, outer_z), WHITE, 3)
            a.line((outer_x, 24, outer_z), (x, 35, z), WHITE, 3)
            a.line((x, 35, z), (cx-4 if x < cx else cx+4, 39, cz), FRAME)
            a.box((x-1, 32, z-1), (x+1, 35, z+1), LILAC)
            a.line((x, 9, z), (outer_x, 24, outer_z), LILAC)
    # 生长容器是两端收束的切角棱晶，最大截面位于中段。
    radii = {}
    for y in range(7, 32):
        radius = min(9, 3+(y-7)//2, 3+(31-y)//2)
        radii[y] = radius
        polygon(a, cx, y, cz, radius, GLASS)
        if y in (7, 12, 19, 26, 31):
            polygon(a, cx, y, cz, radius, LILAC)
    # 细长纵棱接在截面四个轴向端点，不把窗格切成厚重楼层。
    for axis, sign in ((0, -1), (0, 1), (2, -1), (2, 1)):
        points = []
        for y, radius in radii.items():
            p = [cx, y, cz]
            p[axis] += sign*radius
            points.append(tuple(p))
        for p, q in zip(points, points[1:]):
            a.line(p, q, WHITE)
    a.box((19, 3, 22), (25, 6, 28), GEAR)
    a.box((20, 6, 23), (24, 8, 27), WHITE)
    # 晶核有独立种晶座和渐收的顶尖，透明腔体内仍留连续空气层。
    for y in range(9, 29):
        radius = 1 if y < 12 or y > 25 else (3 if 16 <= y <= 21 else 2)
        for dx in range(-radius, radius+1):
            for dz in range(-radius, radius+1):
                if abs(dx)+abs(dz) <= radius:
                    a.set(cx+dx, y, cz+dz, CORE)
        a.set(cx, y, cz, POWER)
    a.box((20, 31, 23), (24, 33, 27), PIPE)
    a.box((20, 34, 23), (24, 36, 27), POWER)
    a.box((21, 37, 24), (23, 39, 26), GEAR)
    # 前侧的窄取晶床保留入口，背侧种晶管与下端生长座相连。
    a.box((19, 1, 9), (25, 3, 19), FRAME, True)
    for x in (19, 25):
        a.box((x, 4, 10), (x, 4, 21), GEAR)
    for z in range(10, 22, 3):
        a.box((20, 4, z), (24, 4, z), GRATE)
    a.box((20, 5, 16), (24, 7, 19), PANEL)
    route(a, '种晶与取晶床', '棱晶生长容器', [(22, 5, 19), (22, 5, 22)], GEAR)
    # 左侧两组低位计量器，用不同高度表达供料与回流。
    for z, height in ((16, 11), (29, 15)):
        a.box((1, 0, z-3), (8, 2, z+3), WHITE)
        a.box((2, 3, z-2), (7, height, z+2), FRAME, True)
        a.box((3, 5, z-2), (6, height-2, z-2), GLASS)
        a.box((2, height, z-2), (7, height+1, z+2), LILAC)
        a.box((4, height+2, z-1), (5, height+3, z+1), GEAR)
        route(a, '前驱体计量器', '棱晶生长容器', [(7, 6, z), (13, 6, z), (13, 6, 25), (19, 6, 25)])
    # 右侧竖向冷却片挂在共同集管上，错落的顶端避免方盒轮廓。
    a.box((36, 0, 16), (43, 2, 35), WHITE)
    for z, height in ((18, 19), (23, 24), (28, 27), (33, 22)):
        a.box((37, 3, z), (42, height, z+1), VENT)
        a.box((37, height+1, z), (42, height+1, z+1), LILAC)
    a.box((42, 3, 18), (43, 5, 34), PIPE)
    a.box((37, 3, 31), (38, 30, 33), PIPE)
    route(a, '上部冷端夹架', '侧置冷却片组', [(24, 35, 25), (30, 35, 25), (30, 30, 25), (37, 30, 25), (37, 30, 32)])
    # 后侧泵头承担回收和支架基础衔接，不占据中央观察窗。
    a.box((17, 1, 35), (28, 5, 41), FRAME, True)
    for x in (18, 24):
        a.box((x, 4, 40), (x+2, 9, 41), GEAR)
        a.box((x, 7, 39), (x+2, 9, 39), PANEL)
    route(a, '棱晶生长容器', '母液回收泵', [(22, 6, 28), (22, 6, 37)], PIPE)
    zone(a, '悬置棱晶生长容器', (13, 3, 16), (31, 39, 34), '种晶、晶体生长、冷端收束', 'growth')
    zone(a, '四爪冷端夹架', (4, 0, 10), (40, 39, 40), '承重、夹持和热隔离', 'support')
    zone(a, '种晶与取晶床', (19, 1, 9), (25, 7, 21), '定位种晶与成品转移', 'transport')
    zone(a, '前驱体计量器', (1, 0, 13), (8, 18, 32), '计量与回流缓冲', 'feed')
    zone(a, '侧置冷却片组', (36, 0, 16), (43, 30, 35), '独立冷却循环与热回收', 'cooling')
    zone(a, '母液回收泵', (17, 1, 35), (28, 9, 41), '回收母液和副产物', 'recovery')
    return finish(a, 'i08-faceted-crystal-furnace-v7',
                  '银白四爪夹架托住一枚两端收束的透明棱晶，紫色晶核从种晶座向冷端生长；斜撑留出观察间隙，正面窄取晶床、左侧计量器、右侧冷却片与背面母液泵围绕晶体组织。淡紫仅落在夹持节点与容器节环，设备没有整板底座。',
                  [('PRECURSOR', '核心前驱体输入'), ('MEDIUM', '结晶介质输入'), ('POWER', '供能候选'),
                   ('COOLANT', '冷却回路候选'), ('CRYSTAL', '仿制核心晶体输出'), ('RESIDUE', '母液与副产物输出')],
                  WHITE, ['GTLCore LARGE_CHEMICAL_PLANT：空腔与外框分离、侧置工艺管路',
                          'GTLsupb MICROCOSM_FOUNDRY：弧形支撑与独立核心间的空气层',
                          'GTCEu ASSEMBLY_LINE：连续床轴与可辨认的取样端'])
