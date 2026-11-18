# -*- coding: utf-8 -*-
"""研究所第四、第五阶：旧院区原位保留，实验分院与共享资料穹顶逐次增建。

变更记录 #1 2026-10-14：新增独立几何候选；不修改旧预览、正式定义或实例。
"""
import math

from research_campus_common_v1 import (Campus, finish, WHITE, BASE, PIPE,
                                     PANEL, COMPUTER, VENT, GRATE, GLASS)

RIB = 'gtlcore:lafium_mechanical_casing'
DOME_GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
ACCENT4 = 'hk3gtl:voltage_machine_casing_qsv'
ACCENT5 = 'hk3gtl:voltage_machine_casing_wsv'
REFS = ['中国科学院科研院区：分学科实验楼、共同服务设施与院内步行秩序；只转译空间关系',
        '超算中心：成列机柜、液冷管汇、屋顶散热和独立机电服务区',
        '科研校园：透明交流廊、分段实验翼及共享资料中庭；为原创建筑表达']


def box(a, x0, x1, y0, y1, z0, z1, material, shell=False):
    """便于阅读的有符号区间，不用斜向连线或负坐标粗线裁剪。"""
    a.box((min(x0, x1), y0, min(z0, z1)),
          (max(x0, x1), y1, max(z0, z1)), material, shell)


def fourth_stairs(a, side):
    """分院前侧的实体折返梯，从地面北支路逐层接入内廊。"""
    for level in range(4):
        floor = level*9
        lane = (31, 32) if level % 2 == 0 else (34, 35)
        xs = sorted((side*lane[0], side*lane[1]))
        start, direction = (-35, 1) if level % 2 == 0 else (-26, -1)
        for step in range(10):
            z, y = start+direction*step, floor+step
            a.path('分院折返梯%d-%d-%d' % (side, level, step),
                   (xs[0], y+1, z), (xs[1], y+3, z))
            box(a, xs[0], xs[1], floor, y, z, z, BASE)
        z, top = start+direction*9, floor+9
        xx = sorted((side*27, side*35))
        a.path('分院楼梯转折平台%d-%d' % (side, level),
               (xx[0], top+1, z), (xx[1], top+3, z))
        box(a, xx[0], xx[1], top, top, z, z, BASE)
        if level % 2:
            target = -26 if top < 36 else -9
            a.path('分院楼梯内廊联络%d-%d' % (side, level),
                   (side*33, top+1, -35), (side*33, top+3, target))
            box(a, side*33, side*33, top, top, -35, target, BASE)
            target_x = sorted((side*28, side*33))
            a.path('分院楼梯侧门%d-%d' % (side, level),
                   (target_x[0], top+1, target), (target_x[1], top+3, target))
            box(a, *target_x, top, top, target, target, BASE)
    xs = sorted((side*30, side*32))
    a.path('分院首段梯前场联络%d' % side, (xs[0], 1, -35), (xs[1], 3, -35))
    box(a, *xs, 0, 0, -35, -35, GRATE)
    a.path('分院首段梯前场侧路%d' % side, (side*30, 1, -35), (side*30, 3, -30))
    box(a, side*30, side*30, 0, 0, -35, -30, GRATE)
    box(a, side*29, side*30, 0, 0, -30, -30, GRATE)
    xs = sorted((side*27, side*35))
    a.zone('前侧实验分院折返楼梯%d' % side, (xs[0], 0, -35), (xs[1], 39, -9),
           '四个九格高实体折返梯段与逐层门洞，真正连通研究分院全部已声明内廊', 'stairs')


def lab_wing(a, side):
    """阶退台实验分院；连续内廊服务三段不同高度的研究空间。"""
    x0, x1 = sorted((side*26, side*36))
    corridor = sorted((side*27, side*29))
    prefix = '西侧' if side < 0 else '东侧'
    for floor in (0, 9, 18, 27):
        a.path(prefix+'实验分院第%d层内廊' % (floor//9+1),
               (corridor[0], floor+1, -26), (corridor[1], floor+3, 26))
    a.path(prefix+'上层研讨廊', (corridor[0], 37, -9), (corridor[1], 39, 9))
    a.path(prefix+'分院入口', (corridor[0], 1, -28), (corridor[1], 3, -26))
    box(a, corridor[0], corridor[1], 0, 0, -30, -26, GRATE)
    bx0, bx1 = sorted((side*7, side*29))
    a.path(prefix+'北场支路', (bx0, 1, -30), (bx1, 3, -28))
    box(a, bx0, bx1, 0, 0, -30, -28, GRATE)
    # 高低体量有连续承重立面，窗带和退台对应真正的楼层。
    for z0, z1, top in ((-26, -10, 31), (-9, 9, 45), (10, 26, 37)):
        for floor in range(0, top-3, 9):
            box(a, x0, x1, floor, floor, z0, z1, WHITE)
            for x in (x0, x1):
                box(a, x, x, floor+1, min(floor+7, top-1), z0, z1, GLASS)
                for z in range(z0, z1+1, 6):
                    box(a, x, x, floor+1, min(floor+8, top-1), z, z+1, BASE)
            for z in (z0, z1):
                box(a, x0, x1, floor+1, min(floor+7, top-1), z, z, GLASS)
            # 靠外研究台和机架留出三格宽内廊，不把房间填成实心盒。
            for z in range(z0+3, z1-1, 6):
                box(a, side*33, side*34, floor+1, floor+2, z, z+2, COMPUTER)
                box(a, side*32, side*35, floor+3, floor+3, z, z+2, WHITE)
                box(a, side*34, side*34, floor+4, floor+5, z+1, z+1, PANEL)
        for x in (x0, x1):
            box(a, x, x, 1, top, z0, z0+1, BASE)
            box(a, x, x, 1, top, z1-1, z1, BASE)
        box(a, x0, x1, top, top, z0, z1, WHITE)
        box(a, side*34, side*36, top-2, top-1, z0, z1, ACCENT4)
        for z in range(z0+3, z1-2, 6):
            box(a, side*32, side*34, top+1, top+2, z, z+2, VENT)
        a.zone(prefix+'实验分院 · '+('前' if z0 < -9 else '中' if z0 < 10 else '后')+'段',
               (x0, 0, z0), (x1, top+2, z1),
               '连续内廊、真实研究台、机柜和分层观察窗；屋顶有对应散热设备', 'research_lab')


def south_compute(a):
    """低长液冷中心与屋顶机电服务带，区别于高耸实验分院。"""
    a.path('后侧算力中心主廊', (-24, 1, 31), (24, 3, 33))
    for x in (-20, 20):
        a.path('后侧算力中心入口%d' % x, (x-1, 1, 29), (x+1, 3, 33))
        box(a, x-1, x+1, 0, 0, 29, 33, GRATE)
    box(a, -25, 25, 0, 0, 30, 36, WHITE)
    box(a, -25, 25, 20, 20, 30, 36, WHITE)
    for z in (30, 36):
        box(a, -25, 25, 1, 19, z, z, GLASS)
        for x in range(-25, 26, 10):
            box(a, x, x+1, 1, 20, z, z, BASE)
        for y in (8, 16):
            box(a, -25, 25, y, y+1, z, z, WHITE)
    for x in (-25, 25):
        box(a, x, x, 1, 19, 30, 36, BASE)
    for x in range(-22, 23, 6):
        box(a, x, x+2, 1, 6, 34, 35, PANEL)
        box(a, x, x+2, 9, 15, 34, 35, COMPUTER)
        box(a, x, x+2, 21, 23, 32, 35, BASE, True)
        box(a, x, x+2, 23, 24, 33, 34, VENT)
    box(a, -23, 23, 7, 7, 35, 35, PIPE)
    box(a, -23, 23, 17, 17, 35, 35, PIPE)
    box(a, -25, 25, 19, 19, 30, 30, ACCENT4)
    # 衔接两侧分院的地面服务廊，同时接到已有第三阶的后院。
    for side in (-1, 1):
        xs = sorted((side*20, side*29))
        a.path('后院横向服务廊%d' % side, (xs[0], 1, 29), (xs[1], 3, 29))
        box(a, xs[0], xs[1], 0, 0, 29, 29, GRATE)
        xx = sorted((side*27, side*29))
        a.path('分院后门服务廊%d' % side, (xx[0], 1, 26), (xx[1], 3, 29))
        box(a, xx[0], xx[1], 0, 0, 26, 29, GRATE)
    a.zone('后侧液冷算力中心', (-25, 0, 30), (25, 24, 36),
           '两层成列机柜、贯通液冷管汇、步行主廊和屋顶散热列', 'supercomputer')


def fourth_shared_tower(a):
    """旧中央研究楼上方的共享研究层；不用机器式巨柱包住整座院区。"""
    for y in (37, 45, 53):
        box(a, -7, 7, y, y, -5, 5, WHITE)
    for x in (-7, 7):
        box(a, x, x, 38, 52, -5, 5, GLASS)
        for z in (-5, 0, 5):
            box(a, x, x, 38, 53, z, z, BASE)
    for z in (-5, 5):
        box(a, -7, 7, 38, 52, z, z, GLASS)
        for x in (-7, -2, 2, 7):
            box(a, x, x, 38, 53, z, z, BASE)
    for floor in (37, 45):
        for x in (-4, 4):
            box(a, x, x+1, floor+1, floor+4, -2, 2, COMPUTER)
        box(a, -1, 1, floor+1, floor+2, -1, 1, PANEL)
    box(a, -6, 6, 54, 54, -4, 4, GLASS)
    box(a, -7, 7, 52, 52, -5, -5, ACCENT4)
    a.zone('中央共享研究层', (-7, 37, -5), (7, 54, 5),
           '在旧竖轴原位增建的两层公共研究室、仪器台与透明顶部观察面', 'shared_research')


def front_seminars(a):
    """前庭两座低位研讨展厅，让新增的北向尺度由真实公共空间承担。"""
    for side in (-1, 1):
        x0, x1 = sorted((side*11, side*23))
        xc = side*17
        a.path('前庭研讨厅入口%d' % side, (xc-1, 1, -34), (xc+1, 3, -29))
        box(a, x0, x1, 0, 0, -36, -29, WHITE)
        box(a, xc-1, xc+1, 0, 0, -34, -28, GRATE)
        for x in (x0, x1):
            box(a, x, x, 1, 13, -36, -29, GLASS)
            box(a, x, x, 1, 16, -36, -36, BASE)
            box(a, x, x, 1, 13, -29, -29, BASE)
        box(a, x0, x1, 1, 13, -36, -36, GLASS)
        box(a, x0, x1, 1, 13, -29, -29, GLASS)
        box(a, x0, x1, 14, 14, -36, -29, WHITE)
        box(a, x0+2, x1-2, 15, 16, -36, -33, ACCENT4)
        box(a, xc-3, xc+3, 1, 2, -35, -35, COMPUTER)
        box(a, xc-3, xc+3, 3, 3, -35, -35, WHITE)
        a.zone('前庭研讨展厅%d' % side, (x0, 0, -36), (x1, 16, -29),
               '面向前庭的低位玻璃研讨室、展示台与短挑檐，留出中央主入口', 'seminar')


def s04():
    from research_campus_early_v1 import s03
    a = Campus(4, s03())
    a.brief['title'] = '世界维系研究所'
    # 先冻结可走交流桥的净空，再生成栏侧、地板及承重构件。
    a.path('跨院架空学术交流廊', (-27, 28, -11), (27, 30, -9))
    for side in (-1, 1):
        fourth_stairs(a, side)
        lab_wing(a, side)
    front_seminars(a)
    box(a, -27, 27, 27, 27, -12, -8, GRATE)
    for z in (-12, -8):
        box(a, -27, 27, 28, 31, z, z, GLASS)
        box(a, -27, 27, 32, 32, z, z, WHITE)
    box(a, -27, 27, 32, 32, -11, -9, GLASS)
    for x in (-20, 20):
        box(a, x-1, x+1, 0, 26, -12, -12, BASE)
        box(a, x-1, x+1, 0, 26, -8, -8, BASE)
        box(a, x-2, x+2, 0, 0, -12, -8, GRATE)
    a.zone('跨院架空学术交流廊', (-27, 27, -12), (27, 32, -8),
           '实体楼板、透明侧面与六格净宽交流空间；下方入口和旧院区保持通透', 'bridge')
    south_compute(a)
    fourth_shared_tower(a)
    a.route('中央共享研究层', '架空学术交流廊',
            [(0, 38, -5), (0, 38, -10), (0, 32, -10)], PIPE)
    a.route('架空学术交流廊', '东西实验分院', [(-27, 32, -12), (27, 32, -12)], PIPE)
    a.route('后侧液冷算力中心', '东侧实验分院',
            [(23, 17, 35), (27, 17, 35), (27, 17, 20)], PIPE)
    return finish(a, '前三阶研究院区完整保留。东西两座阶退台实验分院围出内院，低长液冷算力中心安置在后侧；透明架空交流廊横跨两院，中央研究楼在同一竖轴上增加共享研究层。研究台、成列机柜、液冷与屋顶散热有真实位置，北向控制坞的地面入口连续通向外侧。', REFS)


def point(wing, u, y, v):
    """局部u沿翼楼长边，v是离院区中心的距离；全部正交变换。"""
    return {'北': (u, y, -v), '东': (v, y, u),
            '南': (u, y, v), '西': (-v, y, u)}[wing]


def obox(a, wing, u0, u1, y0, y1, v0, v1, material, shell=False):
    p, q = point(wing, u0, y0, v0), point(wing, u1, y1, v1)
    box(a, p[0], q[0], y0, y1, p[2], q[2], material, shell)


def opath(a, wing, name, u0, u1, floor, v0, v1, height=3):
    p, q = point(wing, u0, floor+1, v0), point(wing, u1, floor+height, v1)
    lo, hi = [min(p[i], q[i]) for i in range(3)], [max(p[i], q[i]) for i in range(3)]
    a.path(wing+'翼'+name, lo, hi)
    obox(a, wing, u0, u1, floor, floor, v0, v1, GRATE)


def fifth_stairs(a, wing, top):
    """开放门厅中的双侧折返梯，中央入口轴保持贯通。"""
    highest = ((top-4)//9)*9
    opath(a, wing, '门厅首段楼梯地面联络', -14, 2, 0, 55, 55)
    for floor in range(0, highest, 9):
        even = (floor//9) % 2 == 0
        lane = (-14, -12) if even else (12, 14)
        start, direction = (55, 1) if even else (64, -1)
        for step in range(10):
            y, v = floor+step, start+direction*step
            opath(a, wing, '门厅梯%d-%d' % (floor, step), *lane, y, v, v)
            obox(a, wing, *lane, floor, y, v, v, BASE)
        newfloor, end = floor+9, start+direction*9
        opath(a, wing, '门厅转折平台%d' % newfloor, -14, 14, newfloor, end, end)
    for floor in range(9, highest+1, 9):
        opath(a, wing, '上层门厅中轴%d' % floor, -1, 1, floor, 54, 64)
        opath(a, wing, '上层分馆横向联络%d' % floor, -10, 10, floor, 54, 54)
        for u in (-10, 10):
            opath(a, wing, '上层分馆侧门%d-%d' % (floor, u), u, u, floor, 49, 54)
        obox(a, wing, -10, 10, floor, floor, 48, 64, GRATE)


def knowledge_wing(a, wing, top):
    """分段外围研究楼，内侧读阅廊、外侧知识库和中央开放门厅。"""
    opath(a, wing, '院区入口轴', -2, 2, 0, 37, 64, 4)
    fifth_stairs(a, wing, top)
    for sign, bounds in ((-1, (-42, -10)), (1, (10, 42))):
        u0, u1 = bounds
        peak = top if sign > 0 else top-6
        for floor in range(0, peak-3, 9):
            opath(a, wing, '知识廊%d-%d' % (sign, floor), u0, u1, floor, 49, 51)
        opath(a, wing, '分馆门洞%d' % sign, u0, u1, 0, 47, 49)
        for floor in range(0, peak-3, 9):
            # 顶层向内退台；外层的真实研究室仍落实129格实体尺度。
            outer = 64 if floor < 18 else 61
            obox(a, wing, u0, u1, floor, floor, 48, outer, WHITE)
            for v in (48, outer):
                obox(a, wing, u0, u1, floor+1, min(peak-1, floor+7), v, v, GLASS)
                for u in range(u0, u1+1, 8):
                    obox(a, wing, u, min(u+1, u1), floor+1, min(peak, floor+8), v, v, BASE)
            for u in (u0, u1):
                obox(a, wing, u, u, floor+1, min(peak-1, floor+8), 48, outer, WHITE)
            for u in range(u0+4, u1-2, 7):
                obox(a, wing, u, u+2, floor+1, floor+5, 56, 58, COMPUTER)
                obox(a, wing, u, u+2, floor+6, floor+6, 56, 58, PANEL)
                obox(a, wing, u-1, u+3, floor+1, floor+2, 61, 62 if outer == 64 else 61, WHITE)
        for u in (u0, u1):
            obox(a, wing, u, u+1 if u == u0 else u, 0, peak, 48, 64, BASE)
        obox(a, wing, u0, u1, peak, peak, 48, 61, WHITE)
        obox(a, wing, u0, u1, 18, 18, 62, 64, GRATE)
        obox(a, wing, u0, u1, peak-1, peak-1, 61, 61, ACCENT5)
        for u in range(u0+4, u1-2, 8):
            obox(a, wing, u, u+2, peak+1, peak+2, 55, 58, VENT)
        p, q = point(wing, u0, 0, 48), point(wing, u1, peak+2, 64)
        a.zone(wing+'翼'+('左' if sign < 0 else '右')+'知识分馆',
               [min(p[i], q[i]) for i in range(3)], [max(p[i], q[i]) for i in range(3)],
               '错层研究室、资料柜列、读阅台与内侧连续廊；高层后退形成屋面平台', 'knowledge_library')
    # 四翼中央门厅分别留出地面出入轴；两侧资料升降核支承空中交流桥。
    obox(a, wing, -9, 9, 0, 0, 48, 64, GRATE)
    for u in (-9, 9):
        obox(a, wing, u, u, 1, 18, 48, 64, GLASS)
    obox(a, wing, -9, 9, 18, 18, 48, 64, GLASS)
    for u in (-6, 6):
        obox(a, wing, u-1, u+1, 0, 59, 50, 52, BASE)
        obox(a, wing, u, u, 6, 57, 49, 49, GLASS)
    obox(a, wing, -7, 7, 59, 59, 49, 52, WHITE)
    # 八个粗实体支座嵌入分馆，不用细线支架或封闭巨型白框。
    for u in (-18, 18):
        obox(a, wing, u-2, u+2, 0, 62, 53, 55, RIB)
        obox(a, wing, u-2, u+2, 60, 62, 49, 55, RIB)
        for y in (17, 35, 53):
            obox(a, wing, u-2, u+2, y, y+1, 53, 56, ACCENT5)
    p, q = point(wing, -9, 0, 48), point(wing, 9, 59, 64)
    a.zone(wing+'翼开放门厅与资料升降核',
           [min(p[i], q[i]) for i in range(3)], [max(p[i], q[i]) for i in range(3)],
           '北向保留直通总入口；其余三翼服务内院，双侧升降核接上层资料桥', 'campus_entrance')


def cognitive_dome(a):
    """透明完整立方体曲面，厚肋和连续阶面承接高架基座。"""
    radius, bottom, top = 54, 60, 104
    surface = {}
    for x in range(-radius, radius+1):
        for z in range(-radius, radius+1):
            rr = (x*x+z*z)/(radius*radius)
            if rr <= 1:
                y = round(bottom+(top-bottom)*math.sqrt(1-rr))
                theta = math.atan2(z, x)
                rib = abs(math.sin(theta*8)) < .20 or x*x+z*z <= 9
                band = y in (76, 77, 90, 91)
                surface[x, z] = y, WHITE if rib or band else DOME_GLASS
    for (x, z), (y, material) in surface.items():
        lower = min([surface[q][0] for q in ((x-1, z), (x+1, z), (x, z-1), (x, z+1))
                     if q in surface]+[y])-1
        if x*x+z*z >= 52*52:
            lower = bottom
        box(a, x, x, max(bottom, lower), y, z, z, material)
        if 51*51 <= x*x+z*z <= radius*radius:
            box(a, x, x, bottom, bottom+2, z, z, BASE if y > bottom else WHITE)
    a.zone('文明认知透明资料穹顶', (-54, 60, -54), (54, 104, 54),
           '高于旧院区屋面至少六格的大跨完整玻璃壳、十六条粗肋与两圈曲面束带；整个旧院区成为可辨内院', 'cognitive_dome')


def fifth_shared_library(a):
    """穹顶内的共享资料圆厅与四条正交高架资料桥。"""
    # 中轴只在第四阶屋顶以上增加支承，不替换旧研究室。
    box(a, -3, 3, 55, 74, -3, 3, GLASS, True)
    for x, z in ((-3, -3), (-3, 3), (3, -3), (3, 3)):
        box(a, x, x, 55, 75, z, z, BASE)
    for y in (59, 67, 75):
        for x in range(-12, 13):
            for z in range(-12, 13):
                if abs(x)+abs(z) <= 18:
                    a.set(x, y, z, WHITE if max(abs(x), abs(z)) > 10 else GRATE)
        for x in (-9, 9):
            for z in range(-7, 8, 7):
                box(a, x, x+1, y+1, min(y+4, 79), z-1, z+1, COMPUTER)
    for x in (-11, 11):
        box(a, x, x, 59, 79, -6, 6, GLASS)
        box(a, x, x, 59, 79, -7, -7, BASE)
        box(a, x, x, 59, 79, 7, 7, BASE)
    for wing in ('北', '东', '南', '西'):
        opath(a, wing, '高架资料交流桥', -2, 2, 59, 12, 51)
        a.paths[-1]['kind'] = 'lift_service'
        a.paths[-1]['access'] = '资料升降服务通道；不列为由地面步行到达的路线'
        for u in (-3, 3):
            obox(a, wing, u, u, 59, 63, 12, 51, GLASS)
            obox(a, wing, u, u, 64, 64, 12, 51, WHITE)
        obox(a, wing, -2, 2, 64, 64, 12, 51, GLASS)
        a.route(wing+'翼资料升降核', '中央共享资料圆厅',
                [point(wing, 3, 63, 51), point(wing, 3, 63, 12)], PIPE)
    a.zone('中央共享资料圆厅', (-12, 55, -12), (12, 79, 12),
           '固定中央研究轴上方三层读阅平台、资料柜和透明资料核心；四条实体正交桥通往外围四翼', 'shared_library')


def s05():
    a = Campus(5, s04())
    a.brief['title'] = '文明认知穹顶'
    for wing, top in (('北', 36), ('东', 42), ('南', 45), ('西', 39)):
        knowledge_wing(a, wing, top)
    # 周边横向服务廊围出真实院区而非空白整板，并从四翼接回旧院区。
    for sign in (-1, 1):
        a.path('外围东西服务廊%d' % sign, (-51, 1, sign*45), (51, 3, sign*45))
        box(a, -51, 51, 0, 0, sign*45, sign*45, GRATE)
        a.path('外围南北服务廊%d' % sign, (sign*45, 1, -51), (sign*45, 3, 51))
        box(a, sign*45, sign*45, 0, 0, -51, 51, GRATE)
        for u0, u1 in ((-42, -10), (10, 42)):
            box(a, u0, u1, 0, 0, sign*45, sign*47, GRATE)
            box(a, sign*45, sign*47, 0, 0, u0, u1, GRATE)
    fifth_shared_library(a)
    cognitive_dome(a)
    return finish(a, '前四阶原位完整保留，成为文明认知穹顶下方的科研内院。北、东、南、西四翼增建错层知识分馆与开放门厅，八个嵌入式粗支座把透明资料穹顶抬到60格以上；十六条有节奏的曲面粗肋收束至105格总高。中央资料圆厅与四条正交高架桥连接外围分馆，研究台、档案柜、资料核心和液冷中心各有所在，北向总入口始终直通旧控制坞。', REFS)
