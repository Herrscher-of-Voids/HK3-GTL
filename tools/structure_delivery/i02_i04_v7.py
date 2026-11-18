# -*- coding: utf-8 -*-
"""I02–I04 原创工程轮廓：光谱扇阵、卧式离心分离机与叉形稳定塔。

变更记录 #1 2026-10-14：重新组织三台的主体、承重点、工艺内核与检修空间。
只提供候选结构数据；不修改旧交付、配方、正式 Pattern 或实例。
"""
import math

from i09_i13_v6_common import start, zone, route, finish

STEEL = 'gtceu:solid_machine_casing'
SILVER = 'gtceu:clean_machine_casing'
BRONZE = 'gtceu:bronze_machine_casing'
GLASS = 'gtceu:tempered_glass'
PIPE = 'gtceu:steel_pipe_casing'
PTFE = 'gtceu:ptfe_pipe_casing'
GEAR = 'gtceu:steel_gearbox'
COMPUTER = 'gtceu:computer_casing'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'


def disk(c0, c1, radius):
    return {(u, v) for u in range(c0-radius, c0+radius+1)
            for v in range(c1-radius, c1+radius+1)
            if (u-c0)**2+(v-c1)**2 <= radius**2}


def boundary(cells, p):
    return any((p[0]+du, p[1]+dv) not in cells
               for du in (-1, 0, 1) for dv in (-1, 0, 1))


def common_ground(a):
    """北侧接口的实体汇流梁与检修入口；主体基础再按设备布置。"""
    c = a.w//2
    a.box((c-14, 0, 7), (c+14, 0, 8), STEEL)
    a.box((c-2, 0, 0), (c+2, 0, 8), GRATE)
    for x in (c-13, c-9, c-5, c+5, c+9, c+13):
        a.box((x, 1, 7), (x, 3, 7), PIPE)
    a.box((c-13, 1, 7), (c+13, 1, 7), PIPE)


def horizontal_shell(a, profiles, cy, cz, casing):
    """沿 X 轴的闭合转鼓；前上部玻璃观察带展示内部螺旋。"""
    slices = {x: disk(cy, cz, r) for x, r in profiles.items()}
    for x, cells in slices.items():
        left, right = slices.get(x-1, set()), slices.get(x+1, set())
        for y, z in cells:
            if boundary(cells, (y, z)) or (y, z) not in left or (y, z) not in right:
                window = 13 <= x <= 30 and z < cz-2 and cy <= y <= cy+4
                material = GLASS if window else casing
                if x in (12, 24, 33):
                    material = STEEL
                a.set(x, y, z, material)


def i02():
    cyan = 'hk3gtl:voltage_machine_casing_civ'
    a = start('I02', '样本光谱分析阵列', (39, 25, 35),
              '以样本为焦点的七片阶梯光谱探测鳍，弧形背脊与放射光学导管',
              '右前独立基准源照射低位样本棱镜；七个不同视角的探测鳍汇总至后侧分析脊')
    common_ground(a)
    a.box((17, 0, 8), (21, 0, 16), GRATE)
    a.box((13, 0, 13), (25, 1, 21), STEEL)
    a.box((0, 0, 12), (7, 0, 18), GRATE)
    a.box((31, 0, 12), (38, 0, 18), GRATE)
    a.box((4, 0, 8), (6, 0, 17), GRATE)
    a.box((32, 0, 8), (34, 0, 17), GRATE)
    a.box((9, 0, 32), (29, 0, 34), GRATE)

    # 样本台不是房间：八角低台与透明棱镜围住可见的进样座。
    for y, r in ((2, 5), (3, 5), (4, 4), (5, 3)):
        for x, z in disk(19, 17, r):
            a.set(x, y, z, cyan if y in (3, 4) else SILVER)
    a.box((18, 6, 16), (20, 7, 18), GEAR)
    for y, r in ((8, 3), (9, 3), (10, 2), (11, 2), (12, 1)):
        for x, z in disk(19, 17, r):
            if boundary(disk(19, 17, r), (x, z)):
                a.set(x, y, z, GLASS)
    a.box((19, 8, 17), (19, 11, 17), COMPUTER)
    zone(a, '低位样本棱镜台', (14, 2, 12), (24, 12, 22), '进样座、透明棱镜、七向光学焦点', 'sample')

    # 探测鳍由两侧向中央升高，七个设备共享一个弧形脊梁。
    nodes = []
    for index, degree in enumerate((0, 30, 60, 90, 120, 150, 180)):
        theta = math.radians(degree)
        x, z = round(19+15*math.cos(theta)), round(17+15*math.sin(theta))
        top = (12, 16, 20, 24, 20, 16, 12)[index]
        nodes.append((x, z, top))
        a.box((x-2, 0, z-2), (x+2, 1, z+2), STEEL)
        a.box((x-1, 2, z), (x+1, top, z+1), cyan)
        a.box((x, 3, z), (x, top-1, z), COMPUTER)
        a.box((x-1, 3, z+1), (x-1, top, z+1), STEEL)
        a.box((x+1, 3, z+1), (x+1, top, z+1), STEEL)
        for yy in range(5, top-2, 4):
            a.box((x-1, yy, z-1), (x+1, yy+1, z-1), GLASS)
        a.box((x-2, top, z), (x+2, top, z+2), VENT)
        a.line((19, 9, 17), (x, 9, z-1), STEEL)
        a.line((19, 10, 17), (x, 10, z-1), GLASS)
        zone(a, '光谱探测鳍%d' % (index+1), (x-2, 0, z-2), (x+2, top, z+2),
             '独立波段检测、向样本内收的窗口与顶部排热面', 'detector')
    for left, right in zip(nodes, nodes[1:]):
        p, q = (left[0], 2, left[1]+1), (right[0], 2, right[1]+1)
        a.line(p, q, STEEL)
        a.line((p[0], 7, p[2]), (q[0], 7, q[2]), cyan)
        a.line((p[0], 0, p[2]), (q[0], 0, q[2]), GRATE)
    zone(a, '弧形探测分析背脊', (2, 2, 16), (36, 24, 34), '阶梯检测轮廓与连续信号汇流脊', 'analysis')

    # 偏心基准光源只有一个真实焦点，单侧悬臂与样本保持明确视线。
    a.box((33, 1, 9), (37, 2, 14), STEEL)
    a.box((34, 3, 10), (36, 6, 13), COMPUTER)
    a.box((35, 7, 12), (35, 15, 12), STEEL)
    a.box((31, 15, 11), (36, 16, 13), cyan)
    a.box((30, 15, 11), (30, 16, 13), GLASS)
    route(a, '基准光源', '低位样本棱镜台', [(30, 15, 12), (23, 15, 12), (23, 15, 17), (23, 10, 17)], PTFE)
    zone(a, '偏心基准光源', (30, 1, 9), (37, 16, 14), '单侧光源驱动柱与光学悬臂', 'source')
    route(a, '样本输入接口', '低位样本棱镜台', [(10, 3, 7), (10, 3, 9), (14, 3, 9), (14, 3, 17)], PIPE)
    route(a, '基准输入接口', '基准光源', [(14, 3, 7), (14, 5, 7), (14, 5, 8), (35, 5, 8), (35, 5, 10)], PIPE)
    route(a, '检测数据接口', '弧形探测分析背脊', [(24, 3, 7), (24, 3, 8), (30, 3, 8), (30, 3, 31), (27, 3, 31)], PIPE)
    a.paths.append({'name': '进样台正面操作路径', 'min': [17, 1, 8], 'max': [21, 3, 11]})
    return finish(a, 'i02-spectral-fan-v7',
                  '七片青色探测鳍在弧形背脊上由两侧逐级升高，全部光学导管朝向低位透明样本棱镜，形成明确扇形焦点。右前仅设一座基准光源和悬臂，灰色信号汇流与青色检测模块各自连续，中央前方保留进样操作空间。',
                  [('STANDARD', '标准样本输入候选'), ('SAMPLE', '待测样本输入候选'), ('REFERENCE', '基准介质输入候选'),
                   ('DATA', '光谱读出候选'), ('RETURN', '检测样本回收候选'), ('POWER', '检测与光源供能候选')],
                  cyan, ['GTLcore PRECISION_ASSEMBLER：玻璃展示真实加工空腔与连续视线',
                         'GTLsupb RANK_DERIVATION_ASSEMBLY_MATRIX：核心、骨架、外围约束的视觉层级；不沿用其终局材料',
                         '光谱扇阵、七个波段探测鳍和单侧基准光源为原创工程表达'])


def i03():
    brass = 'hk3gtl:voltage_machine_casing_icv'
    a = start('I03', '崩坏能离心分离中心', (41, 29, 39),
              '巨大开孔驱动飞轮与单侧卧式收缩转鼓，内部螺旋转子及尾端轻重相分流',
              '右后母液定量进料，横轴螺旋驱动离心分离，尾端双出口分别排出轻相和重相')
    common_ground(a)
    a.box((1, 0, 21), (39, 1, 25), STEEL)
    a.box((0, 0, 17), (4, 1, 29), STEEL)
    a.box((2, 0, 8), (4, 0, 30), GRATE)
    a.box((2, 0, 9), (38, 0, 11), GRATE)
    a.box((38, 0, 10), (40, 0, 32), GRATE)
    a.box((5, 0, 34), (37, 0, 36), GRATE)
    a.box((29, 0, 31), (37, 1, 38), STEEL)

    # 驱动飞轮为有八根机械辐条的开孔薄轮，绝不是另一座玻璃圆塔。
    cy, cz = 15, 23
    outer, inner = disk(cy, cz, 13), disk(cy, cz, 11)
    for x in (6, 7, 8):
        for y, z in outer-inner:
            a.set(x, y, z, STEEL if x in (6, 8) else brass)
    for index in range(8):
        theta = index*math.tau/8
        q = (7, round(cy+12*math.sin(theta)), round(cz+12*math.cos(theta)))
        a.line((7, cy, cz), q, BRONZE)
    a.box((5, 13, 21), (9, 17, 25), GEAR)
    a.box((2, 3, 21), (4, 8, 25), brass, True)
    a.box((2, 4, 20), (4, 7, 20), VENT)
    a.box((3, 9, 22), (3, 15, 24), GEAR)
    a.box((3, 14, 22), (10, 16, 24), GEAR)
    for z in (19, 27):
        a.box((5, 1, z-1), (9, 3, z+1), STEEL)
        a.box((7, 4, z), (7, 6, z), GEAR)
    zone(a, '开孔驱动飞轮', (5, 2, 10), (9, 28, 36), '巨大开孔飞轮、八辐条、轴承与前侧驱动机', 'drive')

    profile = {11: 4, 12: 6, **{x: 7 for x in range(13, 25)},
               25: 6, 26: 6, 27: 6, 28: 5, 29: 5, 30: 5,
               31: 4, 32: 4, 33: 4, 34: 3, 35: 3, 36: 3, 37: 2}
    horizontal_shell(a, profile, cy, cz, BRONZE)
    a.box((9, 15, 23), (38, 15, 23), GEAR)
    # 内转子为连续螺旋叶，横向窗口能读到真实机械路径。
    points = []
    for step in range(97):
        x = 13+step*23/96
        radius = min(4, max(1, (37-x)/5))
        theta = step*math.tau/24
        points.append((x, cy+radius*math.sin(theta), cz+radius*math.cos(theta)))
    for p, q in zip(points, points[1:]):
        a.line(p, q, GEAR)
    for x in range(14, 36, 3):
        a.line((x, cy, cz), (x, cy+min(4, (37-x)//4), cz), STEEL)
    for x, radius in ((14, 7), (23, 7), (33, 4)):
        a.box((x-1, 0, 18), (x+1, 2, 28), STEEL)
        for z in (18, 28):
            a.line((x, 3, z), (x, cy-radius, cz), STEEL)
        a.box((x-1, 3, 22), (x+1, cy-radius-1, 24), brass)
    zone(a, '收缩离心转鼓', (11, 8, 16), (37, 22, 30), '卧式闭合铜色鼓、收缩尾锥、前上观察带与连续螺旋转子', 'centrifuge')

    # 尾端处理器低于飞轮，双分流管各通到独立集液筒。
    a.box((32, 2, 32), (36, 5, 37), brass, True)
    a.box((33, 6, 33), (35, 10, 36), GLASS, True)
    a.box((33, 11, 33), (35, 12, 36), STEEL)
    a.box((32, 13, 33), (36, 14, 36), COMPUTER)
    route(a, '母液缓冲箱', '收缩离心转鼓', [(34, 12, 34), (34, 20, 34), (26, 20, 34), (26, 20, 28)], PIPE)
    route(a, '收缩离心转鼓', '轻相输出管', [(37, 16, 23), (39, 16, 23), (39, 6, 23), (39, 6, 17), (35, 6, 17)], PIPE)
    route(a, '收缩离心转鼓', '重相输出管', [(36, 13, 23), (36, 5, 23), (36, 5, 29), (30, 5, 29)], PIPE)
    a.box((32, 1, 15), (37, 2, 19), STEEL)
    a.box((33, 3, 16), (36, 6, 18), GLASS, True)
    a.box((28, 1, 28), (32, 2, 31), STEEL)
    a.box((29, 3, 29), (31, 5, 30), brass, True)
    zone(a, '尾端轻重相分流', (28, 1, 15), (40, 16, 31), '上支路排轻相、低支路排重相，独立缓冲腔', 'separation')
    zone(a, '母液缓冲与计量', (32, 2, 32), (36, 20, 37), '透明缓冲箱、高位计量进料、前后管路分层', 'feed')
    for z in (33, 36):
        a.box((14, 2, z), (25, 4, z), COMPUTER)
        a.box((14, 5, z), (25, 5, z), VENT)
    a.box((14, 0, 33), (25, 1, 36), STEEL)
    route(a, '驱动轴承', '低位冷却器', [(9, 15, 25), (10, 15, 25), (10, 5, 25), (10, 5, 34), (14, 5, 34)], PIPE)
    route(a, '母液输入接口', '母液缓冲与计量', [(11, 3, 7), (11, 3, 8), (37, 3, 8), (37, 3, 34), (36, 3, 34)], PIPE)
    route(a, '轻相输出接口', '轻相输出管', [(25, 3, 7), (25, 3, 8), (35, 3, 8), (35, 3, 16)], PIPE)
    route(a, '重相输出接口', '重相输出管', [(29, 3, 7), (29, 5, 7), (29, 5, 8), (30, 5, 8), (30, 5, 29)], PIPE)
    a.paths.append({'name': '卧式转鼓前侧检修廊', 'min': [12, 1, 9], 'max': [33, 3, 11]})
    return finish(a, 'i03-decanter-centrifuge-v7',
                  '单侧巨大开孔八辐飞轮驱动一条卧式铜色离心转鼓，鼓体从宽腹收为锥尾，前上玻璃观察带显示连续螺旋叶。尾部高低两支排放管、独立缓冲腔和低位轴承冷却器让轻重相分离关系可读。铜棕与石墨灰构成厚重机械气质。',
                  [('SOLVENT', '清洗/溶剂输入候选'), ('MOTHER_LIQUID', '待分离母液输入候选'), ('POWER', '离心驱动供能候选'),
                   ('LIGHT_PHASE', '轻相液体输出候选'), ('HEAVY_PHASE', '重相液体输出候选'), ('RESIDUE', '固相残渣输出候选')],
                  brass, ['GTLcore PCB_FACTORY：高低分离设备以有意义的低位管路连接',
                          'GTLcore PRECISION_ASSEMBLER：玻璃揭示内部真实加工路径',
                          '卧式螺旋离心机的驱动飞轮、收缩转鼓、螺旋叶与双分流为原创工程表达'])


def i04():
    wine = 'hk3gtl:voltage_machine_casing_hrv'
    a = start('I04', '液态崩坏能稳定塔', (35, 43, 35),
              '两条向上内收的酒红色承压叉臂，中央银白透明分段稳定脊与低位闭合换热回路',
              '下部混合液进入三段透明稳定脊逐级处理，顶部约束头回流至偏心缓冲筒，前方换热列带走热量')
    common_ground(a)
    a.box((5, 0, 18), (29, 1, 25), STEEL)
    a.box((3, 0, 8), (5, 0, 24), GRATE)
    a.box((29, 0, 8), (31, 0, 24), GRATE)
    a.box((3, 0, 27), (31, 0, 29), GRATE)
    a.box((16, 0, 25), (18, 0, 34), GRATE)
    a.box((13, 0, 30), (21, 1, 34), STEEL)

    # 两条宽叉臂有连续斜率、厚度和底脚，外侧银白护边围出修长负空间。
    for side in (-1, 1):
        previous = None
        for y in range(2, 41):
            if y <= 17:
                offset = 11
            elif y <= 28:
                offset = 11-round((y-17)*3/11)
            else:
                offset = max(1, 8-round((y-28)*7/12))
            x = 17+side*offset
            a.box((x-1, y, 20), (x+1, y, 24), wine)
            a.box((x+side, y, 20), (x+side, y, 20), SILVER)
            a.box((x+side, y, 24), (x+side, y, 24), SILVER)
            if previous is not None:
                a.line((previous, y-1, 22), (x, y, 22), STEEL)
            previous = x
        a.box((5 if side < 0 else 26, 1, 19), (8 if side < 0 else 29, 4, 25), STEEL)
    a.box((15, 40, 20), (19, 41, 24), GEAR)
    a.box((15, 42, 20), (19, 42, 24), SILVER)
    zone(a, '内收承压叉臂', (5, 1, 19), (29, 42, 25), '双叉臂承重、上端约束头、连续银白护边', 'support')

    # 三段窗口尺寸逐级收细；实体内核与玻璃空腔有明确可见的深度。
    a.box((15, 2, 20), (19, 6, 24), wine, True)
    a.box((17, 3, 22), (17, 39, 22), PTFE)
    chambers = [(7, 15, 4), (17, 25, 3), (27, 35, 2)]
    for index, (y0, y1, radius) in enumerate(chambers, 1):
        for y in range(y0, y1+1):
            # 菱形剖面避免塔楼般的直角房间；封头和底盘接入内核。
            limit = radius if y not in (y0, y1) else max(1, radius-1)
            for dx in range(-limit, limit+1):
                for dz in range(-limit, limit+1):
                    if abs(dx)+abs(dz) > limit+1:
                        continue
                    edge = abs(dx)+abs(dz) >= limit or y in (y0, y1)
                    if edge:
                        a.set(17+dx, y, 22+dz, SILVER if y in (y0, y1) else GLASS)
        a.box((16, y0+2, 22), (18, y0+3, 22), GEAR)
        zone(a, '第%d段稳定观察腔' % index, (17-radius, y0, 22-radius),
             (17+radius, y1, 22+radius), '菱形透明处理腔、逐级收细、银白端盘与内部整流节', 'stabilization')
    for y, x0, x1 in ((7, 8, 26), (16, 8, 26), (26, 11, 23), (36, 14, 20)):
        a.box((x0, y, 21), (x1, y, 23), STEEL)
        a.box((16, y, 20), (18, y+1, 24), SILVER)
    a.box((16, 36, 21), (18, 39, 23), GEAR)
    zone(a, '三段透明稳定脊', (13, 2, 18), (21, 39, 26), '下宽上窄的三级稳定腔与贯穿耐蚀流路', 'process')

    # 前方矮换热梳与后方缓冲筒使塔的下半部形成明确功能关系。
    a.box((3, 0, 9), (31, 1, 13), STEEL)
    a.box((4, 2, 10), (30, 2, 12), PIPE)
    for x in range(4, 30, 4):
        a.box((x, 3, 10), (x+1, 7, 12), SILVER)
        a.box((x, 4, 10), (x+1, 6, 10), VENT)
    a.box((4, 8, 10), (29, 8, 12), wine)
    for x0, x1 in ((0, 2), (32, 34)):
        a.box((x0, 0, 9), (x1, 1, 13), STEEL)
        a.box((x0, 2, 10), (x1, 5, 12), GEAR)
    a.box((2, 4, 11), (4, 4, 11), PIPE)
    a.box((29, 4, 11), (32, 4, 11), PIPE)
    zone(a, '低位换热梳', (3, 1, 9), (31, 8, 13), '连续热交换总管、独立散热齿与前侧维护面', 'cooling')
    for y in range(2, 13):
        cells = disk(17, 32, 2)
        for x, z in cells:
            if boundary(cells, (x, z)) or y in (2, 12):
                a.set(x, y, z, wine if y in (2, 12) else SILVER)
    a.box((16, 4, 30), (18, 10, 30), GLASS)
    a.box((16, 13, 31), (18, 15, 33), GEAR)
    zone(a, '后侧稳定液缓冲筒', (15, 2, 30), (19, 15, 34), '稳定液缓冲、前面液位窗、顶部回流泵', 'buffer')
    route(a, '顶端约束头', '后侧稳定液缓冲筒', [(17, 40, 24), (17, 40, 28), (17, 15, 28), (17, 15, 32)], PTFE)
    route(a, '后侧稳定液缓冲筒', '低位换热梳', [(19, 5, 32), (27, 5, 32), (27, 5, 14), (27, 5, 12)], PIPE)
    route(a, '低位换热梳', '三段透明稳定脊', [(7, 5, 12), (7, 5, 16), (17, 5, 16), (17, 5, 20)], PIPE)
    route(a, '液态能输入接口', '三段透明稳定脊', [(8, 3, 7), (8, 5, 7), (8, 5, 8), (12, 5, 8), (12, 5, 20), (15, 5, 20)], PTFE)
    route(a, '稳定液输出接口', '后侧稳定液缓冲筒', [(22, 3, 7), (22, 3, 8), (25, 3, 8), (25, 3, 30), (19, 3, 30)], PTFE)
    a.box((10, 1, 14), (13, 1, 18), GRATE)
    a.paths.append({'name': '叉臂内侧巡视路径', 'min': [10, 2, 14], 'max': [13, 4, 18]})
    a.paths.append({'name': '后侧缓冲泵维护带', 'min': [13, 1, 27], 'max': [21, 3, 29]})
    return finish(a, 'i04-forked-stabilizer-v7',
                  '酒红色双叉臂先直立再向上内收，在顶端托住同一个约束头，中央留出修长负空间。银白端盘连接下宽上窄的三段菱形透明稳定腔，前侧矮换热梳、后侧液位缓冲筒与连续回流管形成完整的稳定循环。',
                  [('WASH', '清洗介质输入候选'), ('LIQUID_ENERGY', '液态崩坏能输入候选'), ('STABILIZER', '稳定剂输入候选'),
                   ('STABLE_LIQUID', '稳定液输出候选'), ('COOLANT', '冷却回路接口候选'), ('POWER', '稳定处理供能候选')],
                  wine, ['GTCEu LARGE_CHEMICAL_REACTOR：耐蚀壳与 PTFE 管路围绕封闭工艺核心',
                         'GTLcore LARGE_CHEMICAL_PLANT：外框与反应体之间的空气层和玻璃观察位置',
                         'GTLsupb ABYSSAL_CHEMICAL_ERODER：高塔核心、分段约束节点与轻盈辅助件；不复制终局材料'])
