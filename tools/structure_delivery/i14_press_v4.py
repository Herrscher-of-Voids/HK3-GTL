# -*- coding: utf-8 -*-
"""I14 正梁锻心 V4：开放四柱压机及独立工段，仅生成外观候选。
变更#1 2026-10-15 10:29:00：新建直梁四柱方案，保留 V3 与正式批准建筑。
"""
from i09_i13_v6_common import start, finish, zone, route, PIPE, GEAR, GRATE, PANEL

BASE = 'gtceu:solid_machine_casing'
FRAME = 'gtlcore:lafium_mechanical_casing'
SILVER = 'gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing'
WHITE = 'gtceu:clean_machine_casing'
POWER = 'gtceu:high_power_casing'
HOT = 'hk3gtl:voltage_machine_casing_hcv'
COLD = 'hk3gtl:voltage_machine_casing_civ'
GLASS = 'gtceu:laminated_glass'
COIL = 'kubejs:titansteel_coil_block[active=false]'
PRECISION = 'gtlcore:multi_functional_casing'
VENT = 'gtceu:computer_heat_vent'
CHEMICAL = 'gtceu:corrosion_proof_casing'


def build():
    a = start('I14', '魂钢聚合压铸机', (47, 39, 43),
              '平直厚梁、四柱拉杆与开放冲程；深蓝灰承力框架托起银色液压缸，暖色模芯居中',
              '前方纳米群候选送进→中央聚合压铸→后方冷却读出；左侧前驱液保温，右侧蓄压与尾液回收')

    # 独立脚座通过低位地梁相连，不用大面积地板填充占地。
    a.box((19, 0, 0), (27, 0, 42), BASE)
    a.box((18, 0, 35), (28, 0, 39), BASE)
    a.box((8, 0, 6), (38, 0, 8), BASE)
    a.box((11, 0, 10), (35, 1, 34), BASE)
    a.box((0, 0, 19), (8, 1, 33), BASE)
    a.box((39, 0, 16), (46, 1, 25), BASE)
    a.box((39, 0, 29), (46, 1, 41), BASE)
    a.box((8, 0, 8), (10, 0, 18), GRATE)
    a.box((36, 0, 8), (38, 0, 34), GRATE)
    a.box((8, 0, 32), (12, 0, 34), BASE)
    a.box((35, 0, 22), (40, 0, 24), BASE)
    a.box((35, 0, 32), (40, 0, 34), BASE)
    a.box((38, 0, 24), (40, 0, 31), BASE)

    # 四根竖直主柱；深色柱身、银色面肋和上下锚座表达真实受力。
    for x in (14, 32):
        for z in (13, 31):
            a.box((x-3, 2, z-3), (x+3, 4, z+3), FRAME)
            a.box((x-2, 5, z-2), (x+2, 31, z+2), BASE)
            for side in (-2, 2):
                a.box((x+side, 5, z-2), (x+side, 31, z+2), FRAME)
            # 单根银色拉杆嵌在柱面，避免把整个柱体染成亮白色。
            a.box((x, 5, z-2), (x, 32, z-2), SILVER)
            a.box((x, 5, z+2), (x, 32, z+2), SILVER)
            for y in (5, 29):
                a.box((x-2, y, z-2), (x+2, y+1, z+2), GEAR, True)
            a.box((x-3, 32, z-3), (x+3, 35, z+3), FRAME)
            a.box((x-3, 33, z-3), (x+3, 33, z-3), HOT)
            a.box((x-3, 33, z+3), (x+3, 33, z+3), HOT)

    # 两道平直主梁和侧梁围出屋顶开口；中央横担只承托液压缸。
    for z0, z1 in ((10, 16), (28, 34)):
        a.box((11, 32, z0), (35, 36, z1), FRAME, True)
        for z in (z0, z1):
            a.box((11, 32, z), (35, 32, z), SILVER)
            a.box((11, 36, z), (35, 36, z), BASE)
            for x in (12, 17, 23, 29, 34):
                a.box((x, 33, z), (x, 35, z), BASE)
    for x0, x1 in ((12, 16), (30, 34)):
        a.box((x0, 33, 16), (x1, 35, 28), FRAME, True)
        a.box((x0, 33, 16), (x0, 33, 28), SILVER)
    a.box((15, 33, 20), (31, 35, 24), BASE)
    a.box((15, 35, 20), (31, 35, 20), SILVER)
    a.box((15, 35, 24), (31, 35, 24), SILVER)
    zone(a, '四柱直梁承力架', (11, 0, 10), (35, 36, 34),
         '四个锚座、竖直拉柱及平直横梁；梁间开口不封成天花板', 'load_frame')

    # 上缸、冲杆、移动压板、坯料、模具和砧座按竖直力线清晰分层。
    a.box((20, 28, 19), (26, 37, 25), SILVER, True)
    for y in (28, 32, 36):
        a.box((19, y, 18), (27, y, 26), FRAME, True)
    a.box((21, 38, 20), (25, 38, 24), BASE)
    a.box((22, 20, 21), (24, 34, 23), SILVER)
    a.box((21, 26, 20), (25, 27, 24), GEAR, True)
    a.box((16, 17, 17), (30, 19, 27), FRAME)
    a.box((16, 19, 17), (30, 19, 27), SILVER)
    a.box((18, 17, 19), (28, 17, 25), PRECISION)
    a.box((16, 2, 17), (30, 5, 27), FRAME)
    a.box((17, 6, 18), (29, 8, 26), BASE)
    a.box((17, 8, 18), (29, 8, 26), SILVER)
    a.box((19, 9, 19), (27, 11, 25), SILVER)
    a.box((19, 12, 19), (27, 12, 25), PRECISION)
    a.box((21, 12, 20), (25, 12, 24), HOT)
    a.box((22, 13, 21), (24, 14, 23), COIL)
    for x in (17, 29):
        a.box((x, 6, 21), (x, 10, 23), GEAR)
        a.box((x, 10, 21), (x, 10, 23), HOT)
    zone(a, '开放聚合压铸工位', (16, 2, 17), (30, 38, 27),
         '顶部液压缸—银色冲杆—移动压板—两层空气—暖色坯料—模具—砧座，纵向可读', 'press')

    # 低位滚床配正交升降托盘；上层短鼻桥接模具，所有支座实际落地。
    for z0, z1 in ((8, 16), (28, 42)):
        a.box((19, 5, z0), (27, 6, z1), BASE)
        for x in (19, 27):
            a.box((x, 7, z0), (x, 8, z1), SILVER)
            for z in (z0, z1):
                a.box((x, 1, z), (x, 4, z), BASE)
        for z in range(z0, z1+1, 2):
            a.box((20, 7, z), (26, 7, z), GEAR)
    for z0, z1 in ((14, 16), (28, 30)):
        for x in (19, 27):
            a.box((x, 7, z0), (x, 11, z1), BASE)
            a.box((x, 12, z0), (x, 13, z1), SILVER)
        for x in (20, 26):
            a.box((x, 8, z0+1), (x, 11, z0+1), PIPE)
        a.box((20, 11, z0), (26, 11, z1), FRAME)
        for z in (z0, z1):
            a.box((20, 12, z), (26, 12, z), GEAR)
    a.box((21, 12, 17), (25, 12, 18), SILVER)
    a.box((21, 12, 26), (25, 12, 27), SILVER)
    a.box((21, 8, 10), (25, 9, 13), PRECISION)
    for x in (18, 28):
        a.box((x, 1, 35), (x, 11, 39), BASE)
        a.box((x, 8, 35), (x, 10, 39), VENT)
        a.box((x, 11, 35), (x, 11, 39), COLD)
    a.box((18, 12, 39), (28, 12, 39), BASE)
    a.box((21, 12, 39), (25, 12, 39), PANEL)
    zone(a, '前向预混送进床', (19, 0, 8), (27, 14, 18),
         '低位纳米群候选送进床、成组滚子和正交升降托盘，短鼻桥与下模顶面同高', 'feed')
    zone(a, '后向冷却与读出床', (18, 0, 26), (28, 13, 42),
         '同轴升降托盘接出模坯，低位滚床、冷却侧箱与末端读出桥沿后方展开', 'demould')

    # 左侧保温炉为直立耐火壳，窄观察缝和三道感应腰带强调热工设备。
    a.box((1, 2, 20), (8, 4, 32), BASE)
    a.box((1, 5, 20), (8, 18, 32), HOT, True)
    for x in (1, 8):
        for z in (20, 32):
            a.box((x, 5, z), (x, 18, z), BASE)
    for y in (6, 12, 18):
        a.box((1, y, 20), (8, y, 32), BASE, True)
    a.box((3, 8, 20), (5, 16, 20), GLASS)
    a.box((3, 7, 21), (5, 16, 21), COIL)
    a.box((2, 19, 21), (7, 20, 31), BASE)
    a.box((3, 21, 23), (6, 23, 29), HOT)
    a.box((3, 24, 23), (6, 24, 29), VENT)
    a.box((0, 3, 29), (1, 21, 30), CHEMICAL)
    a.box((0, 20, 28), (2, 22, 31), VENT)
    a.box((8, 9, 23), (9, 11, 25), GEAR)
    route(a, '前驱液保温炉', '开放聚合压铸工位',
          [(8, 10, 24), (18, 10, 24), (19, 10, 24)])
    a.box((11, 1, 24), (11, 9, 24), BASE)
    zone(a, '前驱液保温炉', (0, 0, 19), (9, 24, 33),
         '宽腹耐火炉、暖色壳体、窄观察缝和短程保温管；仅表达候选工艺', 'melter')

    # 右侧双联竖直蓄压筒，供压管沿主柱外侧升至横梁。
    a.box((39, 2, 17), (46, 3, 24), BASE)
    for x in (41, 45):
        a.box((x-1, 4, 18), (x+1, 25, 20), SILVER)
        for y in (5, 12, 20, 25):
            a.box((x-1, y, 17), (x+1, y+1, 21), FRAME, True)
        a.box((x, 7, 17), (x, 23, 17), PIPE)
    a.box((40, 26, 18), (46, 27, 20), BASE)
    a.box((40, 28, 19), (46, 28, 19), PIPE)
    a.box((42, 5, 22), (44, 11, 23), PANEL)
    route(a, '双联液压蓄压站', '四柱直梁承力架',
          [(40, 22, 19), (37, 22, 19), (37, 34, 19), (32, 34, 19)])
    zone(a, '双联液压蓄压站', (39, 0, 16), (46, 28, 25),
         '两根竖直储压筒、四道压箍、上部共用总管和侧置控制柜', 'pressure')

    # 后侧开放冷却翅片和独立尾液集液槽，同高排列避免再做一座斜塔。
    a.box((39, 2, 29), (46, 4, 40), BASE)
    for x in (40, 42, 44, 46):
        a.box((x, 5, 30), (x, 14, 37), SILVER)
        a.box((x, 14, 30), (x, 14, 37), VENT)
        a.box((x, 7, 30), (x, 12, 30), COLD)
    a.box((39, 5, 38), (46, 6, 40), CHEMICAL, True)
    a.box((40, 7, 39), (45, 7, 39), PIPE)
    route(a, '后向冷却与读出床', '冷却与尾液回收段',
          [(28, 6, 37), (38, 6, 37), (38, 6, 39), (40, 6, 39)])
    route(a, '冷却与尾液回收段', '双联液压蓄压站',
          [(45, 5, 30), (45, 5, 24), (45, 5, 23)])
    zone(a, '冷却与尾液回收段', (39, 0, 29), (46, 14, 41),
         '四列平行散热板、后侧集液槽和回流总管；刻意露出板间空气', 'cooling')

    a.paths += [
        {'name': '左前压柱检修道', 'min': [8, 1, 8], 'max': [10, 4, 18]},
        {'name': '右侧连贯维护道', 'min': [36, 1, 8], 'max': [38, 4, 34]},
    ]
    purposes = [('NANO_GROUP', '纳米群送进候选'), ('PRECURSOR', '前驱液输入候选'),
                ('POWER', '压铸供能候选'), ('PRODUCT', '聚合产物输出候选'),
                ('TAIL_LIQUID', '尾液回收候选'), ('UTILITY', '维护或工艺辅助候选')]
    data = finish(a, 'i14-soulium-press-v4',
        '像一座露天的重型锻压工位：深蓝灰四柱撑起平直厚梁，银色液压缸和冲杆沿中央力线压向暖色魂钢坯芯；压板、冲程、下模与砧座彼此分明。前后低位滚床通过正交升降托盘接到模具，左侧保温炉与右侧双联蓄压筒形成高低有别的陪衬，低矮冷却翅片和集液槽收住后侧轮廓。',
        purposes, BASE, [
            '现实四柱液压锻压机的底座—拉柱—上梁—冲杆竖直受力关系；原创方块转译。',
            'GTCEu装配线：直线加工床、底部驱动、顶部机械分层；本稿为单一开放压铸工位。',
            'GTLCore PCB工厂：独立工段由清晰总管相连；本稿不复制Pattern。',
            '材料由增强版2.7的实际JAR与项目资源解析；不用未安装的GTLsupb方块。'])

    states = {tuple(q['pos']): q['state'] for q in data['blocks']}
    cx, cy, cz = data['controller']
    for x in range(cx-1, cx+2):
        for y in range(cy-1, cy+2):
            if (x, y, cz) != (cx, cy, cz):
                states[x, y, cz] = WHITE
    data['blocks'] = [{'pos': list(p), 'state': s} for p, s in sorted(states.items())]
    data['brief']['minimum_wdh'] = [33, 37, 29]
    data['paste_anchor'] = data['controller']
    data['recommended_bottom_y'] = -60
    data['candidate_version'] = 'V4 正梁锻心'
    data['geometry_contract'] = {
        'open_stroke': {'min': [21, 15, 20], 'max': [25, 16, 24]},
        'force_axis_xz': [23, 22],
        'transfer_lift_levels': {'roller_y': 7, 'upper_tray_y': 12, 'die_top_y': 12},
        'interfaces_are_candidates': True,
    }
    return data
