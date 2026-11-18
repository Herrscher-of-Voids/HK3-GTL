# -*- coding: utf-8 -*-
"""I09 / I10 v6：闭合曲面配制釜与共轴纳米合成器的独立完整方块造型。"""
import math

from i09_i13_v6_common import start, zone, route, finish, PIPE, GEAR, GRATE, PANEL

CHEMICAL = 'gtceu:corrosion_proof_casing'
CLEAN = 'gtceu:clean_machine_casing'
FRAME = 'gtceu:solid_machine_casing'
SHIELD = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
GLASS = 'gtceu:fusion_glass'
ENERGY_GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
POWER = 'gtceu:high_power_casing'
PRECISION = 'gtlcore:multi_functional_casing'
AUX_PIPE = 'gtceu:ptfe_pipe_casing'


def disk_points(cx, cz, radius):
    return {(x, z) for x in range(cx-radius, cx+radius+1)
            for z in range(cz-radius, cz+radius+1)
            if (x-cx)**2 + (z-cz)**2 <= radius**2}


def pear_vessel(a, cx, cz, profile, shell):
    """逐层闭合壳；肩部与封头填补半径变化，玻璃沿真正曲面布置。"""
    disks = {y: disk_points(cx, cz, radius) for y, radius in profile.items()}
    for y, cells in disks.items():
        below = disks.get(y-1, set())
        above = disks.get(y+1, set())
        for x, z in cells:
            edge = any((x+dx, z+dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            if edge or (x, z) not in below or (x, z) not in above:
                # 三片曲面观察窗能读到内部搅拌轴，实心纵脊保持釜体轮廓。
                window = 15 <= y <= 25 and z < cz-3 and abs(x-cx) not in (0, 7, 8)
                material = GLASS if window else shell
                if y in (12, 23, 30) or (abs(x-cx) <= 1 and z < cz):
                    material = FRAME
                a.set(x, y, z, material)


def round_column(a, cx, cz, y0, y1, radius, shell, bands):
    cells = disk_points(cx, cz, radius)
    for y in range(y0, y1+1):
        for x, z in cells:
            edge = any((x+dx, z+dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            if edge or y in (y0, y1):
                a.set(x, y, z, FRAME if y in bands else shell)


def i09():
    shell = 'hk3gtl:voltage_machine_casing_hcv'
    a = start('I09', '魂钢前驱体配制釜', (43, 41, 39),
              '珍珠形密闭配制釜、双层环廊、偏心冷凝塔与悬臂粉体漏斗',
              '左侧冷凝回流与右侧定量粉体分别进入曲面釜；中轴搅拌，锥底排出前驱体')

    # 分叉基础只铺到具体承重点；曲面主体下方保留明显的空气与排放锥。
    a.box((6, 0, 6), (36, 0, 8), SHIELD)
    a.box((19, 0, 0), (23, 0, 8), GRATE)
    a.box((1, 0, 22), (10, 1, 32), SHIELD)
    a.box((37, 0, 12), (42, 1, 25), SHIELD)
    for x0, x1, z0, z1 in ((14, 18, 20, 26), (30, 34, 20, 26),
                           (21, 27, 11, 16), (21, 27, 30, 35)):
        a.box((x0, 0, z0), (x1, 1, z1), SHIELD)
    a.box((9, 0, 7), (11, 0, 33), GRATE)
    a.box((10, 0, 33), (33, 0, 35), GRATE)
    a.box((33, 0, 7), (35, 0, 34), GRATE)
    a.box((18, 0, 35), (28, 0, 38), GRATE)
    a.box((0, 0, 23), (10, 0, 25), GRATE)
    a.box((34, 0, 17), (42, 0, 19), GRATE)

    # 大腹、缩颈、弧形冠和尖锥底以真实闭合壳表达，取消方形玻璃盒。
    profile = {5: 1, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8,
               13: 9, 14: 10, 15: 10, 16: 11, 17: 11, 18: 11, 19: 11,
               20: 11, 21: 11, 22: 11, 23: 11, 24: 10, 25: 10,
               26: 9, 27: 9, 28: 8, 29: 7, 30: 6, 31: 5, 32: 4, 33: 3, 34: 2}
    pear_vessel(a, 24, 23, profile, CLEAN)
    a.box((23, 35, 22), (25, 37, 24), GEAR)
    a.box((22, 38, 21), (26, 40, 25), shell, True)
    a.box((23, 39, 20), (25, 39, 20), PANEL)
    a.box((24, 6, 23), (24, 38, 23), PIPE)
    for y, radius in ((12, 4), (18, 6), (24, 5)):
        a.line((24-radius, y, 23), (24+radius, y, 23), GEAR)
        a.line((24, y, 23-radius), (24, y, 23+radius), PRECISION)
        for x in (24-radius, 24+radius):
            a.box((x, y, 22), (x, y+1, 24), CHEMICAL)
    zone(a, '梨形配制釜', (13, 5, 12), (35, 34, 34), '密闭混合壳、曲面观察窗、尖锥排放', 'reactor')
    zone(a, '中轴搅拌驱动', (18, 6, 17), (30, 40, 29), '封顶驱动与三层搅拌桨', 'drive')

    # 四条承重腿进入肩部节点；支承对象清晰而不把釜底填成实心方台。
    for x, z, target in ((16, 23, (16, 12, 23)), (32, 23, (32, 12, 23)),
                          (24, 15, (24, 12, 15)), (24, 31, (24, 12, 31))):
        a.box((x-1, 2, z-1), (x+1, 4, z+1), POWER)
        a.box((x, 5, z), (x, 11, z), FRAME)
        a.line((x, 11, z), target, FRAME)
    for y, r, inner in ((13, 13, 9), (25, 12, 10)):
        a.ring((24, y, 23), r, r, GRATE, 2)
        for angle in (0, math.pi/2, math.pi, math.pi*3/2):
            p = (round(24+inner*math.cos(angle)), y, round(23+inner*math.sin(angle)))
            q = (round(24+r*math.cos(angle)), y, round(23+r*math.sin(angle)))
            a.line(p, q, FRAME)
    # 左侧环廊与检修升降柱、冷凝塔之间有两条平齐的维护桥。
    a.box((10, 1, 31), (11, 27, 32), shell, True)
    for y in (13, 25):
        a.box((9, y, 29), (13, y, 31), GRATE)
        a.box((9, y, 29), (9, y+2, 31), FRAME)
    zone(a, '双层釜体检修环廊', (9, 13, 10), (37, 27, 36), '肩部与上封头维护、左侧升降检修柱', 'maintenance')

    # 冷凝塔刻意比釜瘦，带露出的蛇形换热总管和半高分液罐。
    round_column(a, 5, 27, 2, 32, 3, shell, (2, 9, 17, 25, 32))
    for y in (5, 13, 21, 29):
        a.box((2, y, 24), (8, y, 24), AUX_PIPE)
    a.box((2, 3, 23), (2, 31, 23), AUX_PIPE)
    a.box((8, 3, 23), (8, 31, 23), AUX_PIPE)
    a.box((2, 3, 24), (2, 31, 24), GLASS)
    a.box((8, 3, 24), (8, 31, 24), GLASS)
    round_column(a, 5, 33, 2, 10, 2, CHEMICAL, (2, 10))
    route(a, '冷凝回流塔', '分液缓冲罐', [(5, 4, 30), (5, 4, 33)], AUX_PIPE)
    route(a, '梨形配制釜', '冷凝回流塔', [(19, 31, 23), (11, 31, 23), (11, 31, 27), (8, 31, 27)], AUX_PIPE)
    route(a, '冷凝回流塔', '梨形配制釜', [(8, 12, 27), (15, 12, 27), (15, 16, 27)], AUX_PIPE)
    zone(a, '冷凝回流塔', (2, 2, 23), (8, 32, 30), '窄高冷凝柱、双侧换热立管与回流支路', 'condenser')
    zone(a, '分液缓冲罐', (3, 2, 31), (7, 10, 35), '冷凝液分离缓冲罐', 'buffer')

    # 右侧为真正收口的料斗，其低位驱动机座和输粉悬臂组成另一条轮廓。
    a.box((38, 2, 16), (41, 7, 22), shell, True)
    a.box((39, 8, 18), (40, 18, 20), GEAR)
    for y, r in ((19, 1), (20, 1), (21, 2), (22, 2), (23, 3), (24, 3), (25, 3), (26, 3)):
        cells = disk_points(39, 18, r)
        for x, z in cells:
            edge = any((x+dx, z+dz) not in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            if edge or y == 19:
                a.set(x, y, z, CHEMICAL if y < 26 else FRAME)
    for x in (37, 42):
        a.box((x, 2, 18), (x, 26, 18), FRAME)
    a.box((37, 26, 15), (42, 26, 21), GRATE, True)
    route(a, '粉体定量料斗', '梨形配制釜', [(39, 18, 18), (33, 18, 18), (33, 26, 18), (31, 26, 18)], PIPE)
    zone(a, '粉体定量料斗', (36, 2, 15), (42, 26, 22), '敞口收口料斗、计量螺杆、悬臂输粉管', 'hopper')

    # 六接口的共同低位支管都落在实体背面，前方检修带保持净空。
    for x in (8, 12, 16, 26, 30, 34):
        a.box((x, 1, 7), (x, 3, 7), AUX_PIPE)
    a.box((8, 1, 7), (34, 1, 7), AUX_PIPE)
    route(a, '溶剂输入接口', '梨形配制釜', [(12, 3, 6), (12, 3, 9), (18, 3, 9), (18, 3, 23), (24, 3, 23), (24, 5, 23)], AUX_PIPE)
    route(a, '前驱体输出接口', '锥底排放', [(30, 3, 6), (30, 3, 10), (28, 3, 10), (28, 3, 23), (24, 3, 23), (24, 5, 23)], PIPE)
    route(a, '粉体输入接口', '粉体定量料斗', [(16, 3, 6), (16, 3, 8), (38, 3, 8), (38, 3, 16)], PIPE)
    route(a, '清洗输入接口', '冷凝回流塔', [(8, 3, 6), (8, 3, 9), (2, 3, 9), (2, 3, 27)], AUX_PIPE)
    route(a, '供能接口', '中轴搅拌驱动', [(26, 3, 6), (26, 3, 11), (28, 3, 11), (28, 28, 11), (28, 28, 18), (28, 36, 18), (24, 36, 18), (24, 36, 23)], POWER)
    a.paths.append({'name': '左侧设备维护通道', 'min': [9, 1, 10], 'max': [11, 3, 21]})

    return finish(a, 'i09-soulium-precursor-v6',
                  '以闭合珍珠形压力容器为主轮廓：下锥收料、上部弧形封头、三片曲面观察窗内露出搅拌轴和三层桨叶。琥珀色窄高冷凝塔与偏心收口粉斗打破对称，双层环形检修廊和低位实体管网明确服务于各设备。',
                  [('WASH', '清洗液输入候选'), ('SOLVENT', '溶剂输入候选'), ('POWDER', '前驱粉体输入候选'),
                   ('POWER', '搅拌与计量供能候选'), ('PRECURSOR', '魂钢前驱体输出候选'), ('RECOVERY', '冷凝回收输出候选')],
                  shell, ['GTCEu 1.4.4 LARGE_CHEMICAL_REACTOR（GTMachines.java:882）：耐蚀外壳与 PTFE 管路分工',
                          'GTLcore 1.2.3.2-fix2 LARGE_CHEMICAL_PLANT（MultiBlockMachineAStructureA.java:39）：反应体、观察窗、管带与外框之间的空气层',
                          'GTLsupb 3.7 ABYSSAL_CHEMICAL_ERODER（GTLSupbMachines.java:157）：厚重主体与轻盈附件的体量对比；不复制终局材料',
                          '参考记录：logs/i09-i13-redesign-v6/reference-study.json；新釜外形为原创工程表达'])


def octagon_cells(cy, cz, radius):
    # 平直侧面与明确的四条斜切角，不以圆环替代每一种约束轮廓。
    limit = round(radius*1.42)
    return {(y, z) for y in range(cy-radius, cy+radius+1)
            for z in range(cz-radius, cz+radius+1)
            if abs(y-cy)+abs(z-cz) <= limit}


def octagon_ring(a, x0, x1, cy, cz, outer, inner, material):
    cells = octagon_cells(cy, cz, outer) - octagon_cells(cy, cz, inner)
    for x in range(x0, x1+1):
        for y, z in cells:
            a.set(x, y, z, material)


def i10():
    shell = 'hk3gtl:voltage_machine_casing_hdv'
    a = start('I10', '纳米基元合成器', (51, 33, 43),
              '横向玻璃反应轴与四个不同直径的厚八角共振夹环，尾部偏置高位冷却列',
              '左端分流定量进料，中央共轴约束合成，右端压缩收集；顶部旁路换热循环')
    cy, cz = 15, 24

    # 两条设备轨梁、局部鞍座和前后检修道形成轻透的工业基础。
    a.box((0, 0, 20), (50, 1, 22), SHIELD)
    a.box((0, 0, 26), (50, 1, 28), SHIELD)
    a.box((9, 0, 6), (41, 0, 8), SHIELD)
    a.box((23, 0, 0), (27, 0, 8), GRATE)
    a.box((2, 0, 9), (48, 0, 11), GRATE)
    a.box((2, 0, 36), (48, 0, 38), GRATE)
    a.box((2, 0, 10), (4, 0, 37), GRATE)
    a.box((46, 0, 10), (48, 0, 37), GRATE)
    a.box((33, 0, 38), (43, 0, 42), GRATE)

    # 主反应管八角剖面，透明管内有轴芯与分段整流桨；开阔外壳留出视线。
    octagon_ring(a, 5, 45, cy, cz, 5, 4, GLASS)
    for x in (5, 45):
        for y, z in octagon_cells(cy, cz, 5):
            a.set(x, y, z, SHIELD)
    a.box((5, 14, 23), (45, 16, 25), PRECISION)
    for x in (10, 17, 25, 34, 42):
        a.box((x, 13, 22), (x, 17, 26), ENERGY_GLASS, True)
        a.box((x, 15, 20), (x, 15, 28), AUX_PIPE)
    zone(a, '玻璃共轴反应管', (5, 10, 19), (45, 20, 29), '玻璃管壳、贯穿整流轴芯与五个反应节点', 'reactor')

    # 四个夹环的厚度、直径和轴向间距不重复，形成递增再压缩的工艺节奏。
    collars = [(10, 12, 8), (19, 22, 10), (30, 33, 11), (39, 40, 7)]
    for index, (x0, x1, radius) in enumerate(collars, 1):
        octagon_ring(a, x0, x1, cy, cz, radius, 5, shell)
        for x in (x0, x1):
            octagon_ring(a, x, x, cy, cz, radius, radius-1, FRAME)
            octagon_ring(a, x, x, cy, cz, 6, 5, POWER)
        # 悬起的八角夹环依赖两条可识别的分叉鞍座，不额外补随机落地柱。
        for z in (cz-radius+2, cz+radius-2):
            a.box((x0-1, 0, z-1), (x1+1, 2, z+1), SHIELD)
            a.box((x0, 3, z), (x1, 6, z), POWER)
            a.line((x0, 6, z), (x0, cy-radius+3, z), FRAME)
        a.box((x0, cy, cz-radius-1), (x1, cy+2, cz-radius-1), PANEL)
        a.box((x0, cy-1, cz+radius+1), (x1, cy+1, cz+radius+1), POWER)
        zone(a, '第%d级八角共振夹环' % index, (x0, cy-radius, cz-radius-1),
             (x1, cy+radius, cz+radius+1), '厚夹环、内侧功率环和双分叉鞍座', 'resonator')
    for z in (20, 28):
        a.box((10, 21, z), (40, 21, z), PIPE)
    # 高位连接梁在反应管上方，夹环顶端与驱动功率节之间具有明确连接。
    a.box((19, 26, 23), (33, 26, 25), SHIELD)
    a.box((25, 27, 23), (27, 29, 25), GEAR)
    zone(a, '共振驱动脊梁', (10, 21, 20), (40, 29, 28), '夹环间贯穿约束总管与高位共振驱动', 'drive')

    # 左端供料舱更大且更机械，右端输出喉管收缩；端部轮廓明显不同。
    octagon_ring(a, 0, 4, cy, cz, 7, 2, CLEAN)
    for x in (0, 4):
        octagon_ring(a, x, x, cy, cz, 7, 6, shell)
    a.box((0, 13, 22), (4, 17, 26), GEAR)
    a.box((1, 1, 21), (3, 9, 22), FRAME)
    a.box((1, 1, 26), (3, 9, 27), FRAME)
    a.box((1, 6, 21), (3, 8, 27), POWER)
    octagon_ring(a, 46, 50, cy, cz, 4, 2, shell)
    a.box((46, 14, 23), (50, 16, 25), GEAR)
    a.box((47, 1, 21), (49, 12, 22), FRAME)
    a.box((47, 1, 26), (49, 12, 27), FRAME)
    zone(a, '进料分流端', (0, 1, 17), (4, 22, 31), '宽口机械分流、定量进料及端部承重', 'feed')
    zone(a, '基元收集端', (46, 1, 20), (50, 19, 28), '缩口收集轴、传动和封闭输出腔', 'collector')

    # 偏置于后上方的冷却列与透明轴错开，八根散热齿形成清楚的背部剪影。
    a.box((24, 26, 34), (44, 26, 39), GRATE)
    for x in (25, 43):
        for z in (35, 38):
            a.box((x, 1, z), (x, 25, z), FRAME)
    a.box((25, 27, 35), (43, 28, 38), AUX_PIPE)
    for x in range(25, 44, 3):
        a.box((x, 29, 35), (x+1, 31, 38), CLEAN)
        a.box((x, 30, 35), (x+1, 30, 35), PANEL)
    a.box((42, 29, 36), (43, 32, 37), shell)
    a.box((25, 26, 29), (27, 26, 35), GRATE)
    route(a, '共振合成反应管', '偏置冷却列', [(30, 26, 24), (30, 28, 24), (30, 28, 34), (30, 28, 36)], AUX_PIPE)
    route(a, '偏置冷却列', '基元收集端', [(43, 28, 36), (46, 28, 36), (46, 21, 36), (48, 21, 36), (48, 21, 24), (48, 19, 24)], AUX_PIPE)
    zone(a, '偏置冷却列', (24, 26, 34), (44, 32, 39), '高位换热总管、成组散热齿与尾端排气立柱', 'cooling')

    # 独立的供料旁路和产物旁路绕过通道，不把接口摆到设备背后。
    for x in (12, 16, 20, 30, 34, 38):
        a.box((x, 1, 7), (x, 3, 7), AUX_PIPE)
    a.box((12, 1, 7), (38, 1, 7), AUX_PIPE)
    route(a, '液态前驱体输入接口', '进料分流端', [(12, 3, 6), (12, 3, 8), (6, 3, 8), (6, 9, 8), (6, 9, 24), (4, 9, 24)], AUX_PIPE)
    route(a, '模板输入接口', '进料分流端', [(16, 3, 6), (16, 5, 6), (8, 5, 6), (8, 17, 6), (8, 17, 18), (4, 17, 18)], PIPE)
    route(a, '供能接口', '共振驱动脊梁', [(20, 3, 6), (20, 3, 8), (22, 3, 8), (22, 24, 8), (22, 24, 18), (22, 25, 18)], POWER)
    route(a, '纳米基元输出接口', '基元收集端', [(30, 3, 6), (30, 3, 8), (44, 3, 8), (44, 9, 8), (44, 9, 24), (48, 9, 24), (48, 11, 24)], PIPE)
    route(a, '尾气回收接口', '偏置冷却列', [(38, 3, 6), (38, 3, 8), (45, 3, 8), (45, 3, 39), (43, 3, 39), (43, 26, 39)], AUX_PIPE)
    a.paths.append({'name': '横轴前侧检修长廊', 'min': [10, 1, 9], 'max': [41, 3, 11]})
    a.paths.append({'name': '左端横向维护联络道', 'min': [2, 1, 10], 'max': [4, 3, 16]})

    return finish(a, 'i10-nano-basic-unit-v6',
                  '深青色四级厚八角夹环围绕长水平玻璃反应轴，夹环外径逐段扩大后收束，轴向间距和厚度也随处理阶段改变。左端宽口机械分流、右端缩口收集、高位偏置散热列与分叉鞍座构成清楚的共轴工业设备轮廓。',
                  [('PRECURSOR', '液态前驱体输入候选'), ('TEMPLATE', '纳米模板输入候选'), ('POWER', '共振合成供能候选'),
                   ('NANO_UNIT', '纳米基元输出候选'), ('COOLANT', '循环冷却液接口候选'), ('TAIL_GAS', '尾气回收输出候选')],
                  shell, ['GTLcore 1.2.3.2-fix2 PRECISION_ASSEMBLER（MultiBlockMachineAStructureA.java:26）：双侧玻璃展示连续加工通道',
                          'GTLcore 1.2.3.2-fix2 NANO_FORGE_1（AdvancedMultiBlockMachineStructureB.java:17）：分段约束、长空气内核与收口；改为原创水平轴',
                          'GTLsupb 3.7 MICROCOSM_FOUNDRY（GTLSupbMachines.java:170）：核心与弧状支架间的空气层；不复制终局材料',
                          '参考记录：logs/i09-i13-redesign-v6/reference-study.json；厚八角夹环、鞍座与冷却回路为原创工程表达'])
