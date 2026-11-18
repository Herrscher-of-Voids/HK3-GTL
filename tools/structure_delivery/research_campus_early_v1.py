# -*- coding: utf-8 -*-
"""科研院区前三阶：独立研究楼、双实验翼、中庭超算与档案。

变更记录 #1 2026-10-14：新增原位保留的独立候选；不改旧版或生产文件。
"""
from research_campus_common_v1 import (
    Campus, finish, validate, WHITE, BASE, PIPE, PANEL, COMPUTER, VENT, GRATE, GLASS)

BLUE = 'hk3gtl:voltage_machine_casing_hbv'
GREEN = 'hk3gtl:voltage_machine_casing_hdv'
CYAN = 'hk3gtl:voltage_machine_casing_civ'
GEAR = 'gtceu:steel_gearbox'
REFERENCES = ['中国科学院及现实科研院区：低层研究楼、双侧实验翼、庭院、水平窗带与遮阳肋的建筑秩序',
              '超算机房：规则机柜列、维护冷通道、屋顶散热及集中供电；不宣称模组计算功能已接入',
              '已确认研究任务：S01承载ALE/OPR实验表达，S02起独立隔离演算；建筑不承担通用生产机器',
              'doc/HK3GTL-内测5/讨论记录/2026-09-28_16-07-59_八项工艺合并及研究所实验任务确认.html',
              'doc/HK3GTL-内测5/讨论记录/2026-09-28_22-23-43_R03至R06整体批准与研究所命名.html']


def walk(a, name, lo, hi, floor=GRATE):
    """先保留真实可步行空间，再放实体地板；全部通路随升级永久保护。"""
    a.path(name, lo, hi)
    a.box((lo[0], lo[1]-1, lo[2]), (hi[0], lo[1]-1, hi[2]), floor)


def room(a, lo, hi, accent=BLUE):
    """能进入的研究楼层；水平玻璃带被深灰垂直遮阳脊规律分隔。"""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    a.box(lo, hi, WHITE, True)
    a.box((x0, y0, z0), (x1, y0, z1), BASE)
    for x in (x0, x1):
        for z in range(z0, z1+1):
            rib = z in (z0, z1) or (z-z0) % 4 == 0
            a.box((x, y0+1, z), (x, y1-1, z), BASE if rib else WHITE)
            if not rib:
                a.box((x, y0+3, z), (x, min(y1-2, y0+5), z), GLASS)
        a.box((x, y1-1, z0+1), (x, y1-1, z1-1), accent)
    for z in (z0, z1):
        for x in range(x0, x1+1):
            rib = x in (x0, x1) or (x-x0) % 4 == 0
            a.box((x, y0+1, z), (x, y1-1, z), BASE if rib else WHITE)
            if not rib:
                a.box((x, y0+3, z), (x, min(y1-2, y0+5), z), GLASS)
        a.box((x0+1, y1-1, z), (x1-1, y1-1, z), accent)


def stair(a, name, x0, x1, z0, direction, floor, rise=8):
    """完整方块逐格台阶；每步保留三格头部空间，能够跳步上下。"""
    for i in range(rise+1):
        z, y = z0+direction*i, floor+i
        a.path(name+' · 第%d步' % i, (x0, y+1, z), (x1, y+3, z))
        a.box((x0, floor, z), (x1, y, z), BASE)


def bench(a, lo, hi, material=PANEL):
    a.box(lo, hi, BASE)
    a.box((lo[0], hi[1]+1, lo[2]), (hi[0], hi[1]+1, hi[2]), material)


def s01():
    a = Campus(1)
    # 控制立面居中；研究楼入口走其两侧开放检修廊，不让主控挡住入楼动线。
    a.box((-8, 0, -12), (8, 0, -7), GRATE)
    for x in (-8, 8):
        walk(a, '控制坞%s侧入楼廊' % ('西' if x < 0 else '东'), (x, 1, -12), (x, 3, -7))
    walk(a, '研究楼前场横向通廊', (-8, 1, -8), (8, 3, -7))
    walk(a, '一楼中央实验走廊与前后门', (-1, 1, -7), (1, 3, 12), BASE)
    walk(a, '一楼东西预留实验翼门洞', (-6, 1, -1), (6, 3, 1), BASE)
    walk(a, '二楼中央阅览走廊', (-1, 9, -5), (1, 11, 6), BASE)
    walk(a, '二楼东西连廊预留门洞', (-6, 9, -1), (6, 11, 1), BASE)
    walk(a, '二楼西侧室外楼梯入口', (-8, 9, 3), (-1, 11, 4), BASE)
    stair(a, '一二楼西侧折边露天楼梯', -8, -7, 12, -1, 0)
    room(a, (-6, 0, -6), (6, 7, 7))
    room(a, (-6, 8, -6), (6, 14, 7))
    a.box((-6, 0, 8), (8, 0, 12), GRATE)
    # 四组实验桌面避开中轴和侧门，建筑内能分辨样本与观察位置。
    for x0 in (-4, 3):
        for z0 in (-4, 3):
            bench(a, (x0, 1, z0), (x0+1, 2, z0+1))
            a.set(x0, 4, z0, GLASS)
    for x0 in (-4, 2):
        bench(a, (x0, 9, -4), (x0+2, 10, -3), COMPUTER)
        bench(a, (x0, 9, 5), (x0+2, 10, 6), PANEL)
    for x in (-5, 5):
        a.box((x, 1, -9), (x, 4, -9), WHITE)
    a.box((-6, 5, -9), (6, 5, -6), WHITE)
    a.box((-2, 15, -3), (2, 16, 3), GLASS, True)
    for z in (-3, 3):
        a.box((-2, 16, z), (2, 16, z), VENT)
    a.box((7, 1, 2), (8, 4, 7), WHITE, True)
    a.box((8, 2, 3), (8, 3, 6), VENT)
    a.route('研究楼空调与样本隔离柜', '东侧微型冷却站', [(6, 2, 6), (7, 2, 6)], PIPE)
    bench(a, (3, 1, 10), (6, 2, 11), GLASS)
    a.box((3, 1, 12), (8, 3, 12), WHITE)
    a.box((4, 2, 12), (7, 3, 12), GLASS)
    a.zone('中央基础实验楼', (-6, 0, -6), (6, 14, 7),
           '一楼四实验桌对应样本观察、ALE与OPR实验表达；二楼小型阅览与分析室', 'laboratory')
    a.zone('西侧可步行全立方楼梯', (-8, 0, 3), (-7, 11, 12), '逐格台阶接入二楼真实门洞', 'stairs')
    a.zone('后院样本观察廊', (-6, 0, 8), (8, 3, 12), '后门直通观察桌和低矮透明陈列墙', 'courtyard')
    a.zone('屋顶窄带采光与排热监视器', (-2, 14, -3), (2, 16, 3), '长条采光顶与两端排热，构成小研究楼最高轮廓', 'skylight')
    return finish(a, '两层银白研究楼以深灰遮阳肋、长条玻璃带和少量蓝色腰线形成科研建筑身份。四组实验桌、二楼阅览台、西侧可步行方块楼梯、后院观察廊和屋顶采光条均有清楚位置；东西预留门洞供后阶扩建，固定主控白框和六工业接口在北侧前场。', REFERENCES)


def s02():
    a = Campus(2, s01())
    # 两翼与前阶保持安全缝，只有真实门洞、走廊和建筑楼板相接。
    walk(a, '南院中央研究步道', (-1, 1, 13), (1, 3, 18), BASE)
    walk(a, '南院横向学术通廊', (-16, 1, 14), (16, 3, 16))
    for side in (-1, 1):
        x0, x1 = (-16, -10) if side < 0 else (10, 16)
        xc = side*13
        walk(a, '实验翼北侧入楼廊%d' % side, (min(side*8, xc), 1, -8),
             (max(side*8, xc), 3, -7))
        walk(a, '实验翼地面中廊%d' % side, (xc-1, 1, -6), (xc+1, 3, 16), BASE)
        walk(a, '实验翼与旧核心地面连廊%d' % side, (min(side*6, side*12), 1, -1),
             (max(side*6, side*12), 3, 1), BASE)
        walk(a, '二楼实验翼与旧阅览室连廊%d' % side, (min(side*6, xc), 9, -1),
             (max(side*6, xc), 11, 1), BASE)
        for floor in (8, 16):
            walk(a, '实验翼上层中廊%d-%d' % (side, floor), (xc-1, floor+1, -6),
                 (xc+1, floor+3, 11), BASE)
        if side > 0:
            walk(a, '东实验翼顶层通往研讨厅门洞', (8, 17, 2), (12, 19, 3), BASE)
        low_run = (x0+1, x0+2)
        high_run = (x1-2, x1-1)
        walk(a, '北维护轴通往实验翼楼梯底入口%d' % side,
             (min(side*7, low_run[0]), 1, -16), (max(side*7, low_run[1]), 3, -16), BASE)
        stair(a, '实验翼独立首段楼梯%d' % side, *low_run, -16, 1, 0)
        walk(a, '实验翼八格楼梯转折平台%d' % side, (x0+1, 9, -8), (x1-1, 11, -8), BASE)
        walk(a, '实验翼二楼楼梯平台至门洞联络廊%d' % side,
             (xc, 9, -8), (xc, 11, -6), BASE)
        stair(a, '实验翼独立第二段楼梯%d' % side, *high_run, -8, -1, 8)
        walk(a, '实验翼顶层楼梯转折平台%d' % side, (x0+1, 17, -16), (x1-1, 19, -16), BASE)
        walk(a, '实验翼顶层空中通廊%d' % side, (xc, 17, -15), (xc, 19, -6), BASE)
        for floor in (0, 8, 16):
            room(a, (x0, floor, -6), (x1, floor+7, 12), GREEN)
            for z in (-4, 3, 9):
                bench(a, (x0+1, floor+1, z), (x0+1, floor+2, z+1))
                bench(a, (x1-1, floor+1, z), (x1-1, floor+2, z+1), COMPUTER)
        # 竖向遮阳脊包住楼梯外侧，开放折返梯可从前场观察到。
        for x in (x0, x1):
            a.box((x, 0, -18), (x, 19, -8), WHITE)
            for z in range(-17, -8, 3):
                a.box((x, 3, z), (x, 15, z+1), GLASS)
        a.box((x0, 0, -18), (x1, 0, -16), GRATE)
        a.box((x0, 20, -18), (x1, 20, -8), WHITE)
        a.box((x0, 19, -18), (x1, 19, -18), GREEN)
        # 轻量屋顶冷却设备直接坐在翼楼顶板上，避免楼顶空白。
        a.box((x0+1, 24, 5), (x1-1, 25, 10), VENT, True)
        a.box((xc, 24, 5), (xc, 26, 10), PIPE)
        a.box((x0+1, 26, 6), (x1-1, 26, 9), GRATE)
        a.zone('西侧材料实验翼' if side < 0 else '东侧隔离演算实验翼',
               (x0, 0, -18), (x1, 26, 12),
               '三层实验室、水平玻璃带、独立折返梯与屋顶冷却；中廊接旧核心', 'research_wing')
    walk(a, '三楼东翼至中央研讨厅的高位连廊', (5, 17, 2), (8, 19, 3), BASE)
    walk(a, '中央研讨厅东侧高位入口', (3, 18, 2), (4, 20, 3), BASE)
    walk(a, '中央研讨厅中轴', (-1, 18, -3), (1, 20, 3), BASE)
    walk(a, '中央研讨厅西侧后阶楼梯预留口', (-5, 18, -3), (-1, 20, -2), BASE)
    room(a, (-4, 17, -4), (4, 25, 4), GREEN)
    for x in (-4, 4):
        for z in (-4, 4):
            a.box((x, 15, z), (x, 16, z), BASE)
    for x in (-3, 2):
        bench(a, (x, 18, 0), (x+1, 19, 0), COMPUTER)
    a.box((-2, 26, -2), (2, 26, 2), GLASS)
    a.box((-8, 0, 13), (8, 0, 18), GRATE)
    for side in (-1, 1):
        a.box((side*5-1, 1, 17), (side*5+1, 2, 18), WHITE)
        a.box((side*5-1, 3, 18), (side*5+1, 3, 18), GREEN)
    a.zone('中央退台研讨厅', (-5, 15, -4), (4, 26, 4),
           '旧研究楼上方独立研讨厅，由东翼顶层真实连廊进入；西侧保留后阶楼梯口', 'seminar')
    a.zone('双翼之间的南侧研究中庭', (-9, 0, 8), (9, 3, 18),
           '旧后院完整保留，新增横向学术通廊与低矮院景坐台', 'courtyard')
    return finish(a, '前阶两层小研究楼完整保留；东西新增三层绿调实验翼，独立折返楼梯、水平窗带和竖向遮阳脊构成研究院双翼。南侧中庭用横向通廊联系两翼，中央退台研讨厅经东侧真实高位连廊到达，屋顶冷却柜体现实验楼功能。')


def s03():
    a = Campus(3, s02())
    # 前侧两座低层办公分院围合仪式性的北入口；保持十五格宽主控维护轴。
    for side in (-1, 1):
        x0, x1 = (-24, -18) if side < 0 else (18, 24)
        xc = side*21
        walk(a, '北侧办公分院入口%d' % side, (min(side*7, xc), 1, -23),
             (max(side*7, xc), 3, -21), BASE)
        walk(a, '北侧办公分院地面走廊%d' % side, (xc-1, 1, -23), (xc+1, 3, -14), BASE)
        walk(a, '办公分院二楼与旧实验翼楼梯联络廊%d' % side, (side*13, 9, -20),
             (side*13, 11, -8), BASE)
        walk(a, '办公分院上层横向廊%d' % side, (min(xc, side*13), 9, -20),
             (max(xc, side*13), 11, -19), BASE)
        for floor in (0, 8):
            room(a, (x0, floor, -24), (x1, floor+6, -13), CYAN)
            bench(a, (x0+1, floor+1, -17), (x0+1, floor+2, -15), COMPUTER)
            bench(a, (x1-1, floor+1, -17), (x1-1, floor+2, -15), PANEL)
        a.zone('北侧%s研究办公分院' % ('西' if side < 0 else '东'), (x0, 0, -24), (x1, 14, -13),
               '低层办公与研究交流，水平窗带围合主入口，二楼接旧楼梯转折区', 'administration')
    walk(a, '南部超算与档案之间的中庭走廊', (-1, 1, 19), (1, 3, 28), BASE)
    walk(a, '超算与档案厅前侧公共横廊', (-23, 1, 14), (23, 3, 16), BASE)
    walk(a, '超算大厅中央冷通道', (-14, 1, 16), (-11, 3, 27), BASE)
    walk(a, '超算大厅前侧横通道', (-23, 1, 19), (-2, 3, 19), BASE)
    walk(a, '超算大厅后侧维护横廊', (-23, 1, 27), (-3, 3, 27), BASE)
    room(a, (-24, 0, 19), (-2, 20, 28), CYAN)
    # 五组柜列留出中央冷通道、前后横廊，透过长条立面窗可看到计算机柜。
    for x in (-21, -17, -9, -5):
        a.box((x, 1, 20), (x+1, 8, 26), COMPUTER)
        a.box((x, 2, 19), (x+1, 7, 19), PANEL)
        a.box((x, 9, 20), (x+1, 9, 26), VENT)
        a.route('超算机柜', '屋顶液冷总管', [(x, 9, 26), (x, 18, 26), (x, 18, 28)], PIPE)
    # 三条独立屋顶液冷银行和竖向散热片沿低矮超算大厅排列。
    for x0, x1 in ((-22, -17), (-15, -10), (-8, -3)):
        a.box((x0, 21, 18), (x1, 24, 26), BASE, True)
        a.box((x0, 22, 18), (x1, 23, 18), VENT)
        for x in range(x0, x1+1, 2):
            a.box((x, 25, 19), (x, 31, 25), VENT)
        a.box((x0, 25, 22), (x1, 25, 23), PIPE)
    a.route('超算屋顶冷却银行', '实验翼公共冷却回路', [(-13, 21, 27), (-13, 21, 12), (-13, 25, 12)], PIPE)
    a.zone('西侧超算机房', (-24, 0, 19), (-2, 20, 28),
           '规则柜列、中央冷通道、前后横向检修通道和透窗机房', 'supercomputer')
    a.zone('超算屋顶液冷与散热银行', (-22, 21, 18), (-3, 31, 27),
           '三个直接坐在屋面的液冷箱与七格高散热片，回路接旧实验翼', 'cooling')
    # 四层档案厅逐层朝中庭退台；楼梯在东侧，藏书柜与访问通道错开。
    for floor in (0, 8, 16, 24):
        walk(a, '档案厅第%d层中央阅览通道' % (floor//8+1), (11, floor+1, 20), (13, floor+3, 28), BASE)
        landing = 20 if floor % 16 == 0 else 28
        walk(a, '档案厅第%d层东侧楼梯联络廊' % (floor//8+1), (12, floor+1, landing), (23, floor+3, landing), BASE)
    walk(a, '档案厅地面前侧横廊与中庭入口', (2, 1, 19), (23, 3, 19), BASE)
    for floor, xs, z0, direction in ((0, (20, 21), 20, 1), (8, (17, 18), 28, -1),
                                    (16, (20, 21), 20, 1), (24, (17, 18), 28, -1)):
        stair(a, '档案楼层折返梯%d' % floor, *xs, z0, direction, floor)
        z = z0+direction*8
        walk(a, '档案楼层折返平台%d' % floor, (17, floor+9, z), (21, floor+11, z), BASE)
    for floor, x0, z0 in ((0, 2, 19), (8, 2, 19), (16, 4, 20), (24, 7, 20)):
        room(a, (x0, floor, z0), (24, floor+7, 28), CYAN)
        for x in (max(x0+2, 7), 15):
            a.box((x, floor+1, 21), (x+1, floor+5, 25), COMPUTER)
            a.box((x, floor+6, 21), (x+1, floor+6, 25), WHITE)
    walk(a, '档案屋顶阅读厅入口与阅览轴', (17, 33, 18), (18, 35, 20), BASE)
    walk(a, '档案屋顶阅览横廊', (8, 33, 20), (18, 35, 20), BASE)
    room(a, (6, 32, 20), (20, 36, 26), CYAN)
    for x in (8, 12):
        bench(a, (x, 33, 21), (x+2, 34, 22), PANEL)
    a.zone('东侧退台档案与阅览楼', (2, 0, 16), (24, 36, 28),
           '四层退台档案柜、东侧全立方折返梯与顶部透明阅览厅', 'archive')
    # 旧核心中央轴上增建真正的研究决策室，而非机器柱；西侧楼梯上来可进入。
    stair(a, '中央决策室西侧增建楼梯', -7, -6, -3, 1, 17, 9)
    walk(a, '中央决策室楼梯顶平台与入口', (-5, 28, 5), (1, 30, 6), BASE)
    walk(a, '中央决策室中轴', (-1, 28, -4), (1, 30, 5), BASE)
    room(a, (-7, 27, -5), (7, 35, 6), CYAN)
    for x in (-4, 3):
        bench(a, (x, 28, -2), (x+1, 29, 2), PANEL)
    for x in (-4, 4):
        for z in (-4, 4):
            a.box((x, 26, z), (x, 26, z), BASE)
    a.box((-3, 36, -2), (3, 36, 3), GLASS)
    a.zone('中央量子研究决策室', (-7, 26, -5), (7, 36, 6),
           '原研究楼上方更宽的退台综合研究室，西侧真实楼梯接旧研讨厅，屋顶玻璃采光', 'research_core')
    return finish(a, '旧研究楼、双实验翼和中庭逐块保留；新前侧办公分院围合入口，西南低矮超算机房显露柜列、冷通道与三条屋顶液冷银行，东南档案楼朝中庭逐层退台并以顶部透明阅览厅收束。旧核心顶端增建可进入的综合研究决策室，整体从双翼研究楼成长为完整科研院区。')


if __name__ == '__main__':
    import json
    previous, result = None, []
    for fn in (s01, s02, s03):
        data = fn()
        result.append(validate(data, previous))
        previous = data
    print(json.dumps(result, ensure_ascii=False, indent=2))
