# -*- coding: utf-8 -*-
import numpy as np

MATERIALS = [
    ('hk3gtl:voltage_machine_casing_wfv', 'WFV水晶粉机壳', '加载架、试验床身与悬箱外装甲'),
    ('gtceu:robust_machine_casing', '坚固机械方块', '承重骨架与桥架导轨'),
    ('gtceu:clean_machine_casing', '洁净机械方块', '舱体白色封边与检修盖板'),
    ('gtceu:assembly_line_casing', '装配线方块', '样件交换滑台'),
    ('gtceu:advanced_computer_casing', '高级计算机机壳', '前控与后部记录柜'),
    ('gtceu:atomic_casing', '原子机械方块', '受控样件盒的内胆'),
    ('gtceu:high_power_casing', '高功率机械方块', '侧面脉冲加载电源柜'),
    ('gtceu:laser_safe_engraving_casing', '防激光机械方块', '桥上测量光路遮光壳'),
    ('gtceu:stainless_steel_turbine_casing', '不锈钢涡轮机壳', '后部循环介质动力段'),
    ('gtceu:secure_maceration_casing', '安全研磨机械方块', '退役试件拆解回收柜'),
    ('gtceu:computer_heat_vent', '计算机散热口', '加载电源与记录柜散热面'),
    ('gtceu:tungstensteel_gearbox', '钨钢齿轮箱', '纵向加载头驱动机构'),
    ('gtceu:tungstensteel_pipe_casing', '钨钢管道方块', '加载头供压管'),
    ('gtceu:steel_pipe_casing', '钢管道方块', '介质回收总管'),
    ('gtceu:assembly_line_grating', '装配线格栅', '侧面检修廊与桥架踏道'),
    ('gtlcore:iridium_casing', '铱机械方块', '悬吊拉杆与样件夹座'),
    ('gtlcore:process_machine_casing', '工艺机械方块', '后部介质处理柜'),
    ('gtlcore:dimension_connection_casing', '维度连接机壳', '试件箱连接颈部'),
    ('gtlcore:multi_functional_casing', '多功能机壳', '工况控制机组'),
    ('gtlcore:lafium_mechanical_casing', '拉菲姆机械方块', '高载荷横向导向滑座'),
    ('gtlcore:hsss_reinforced_borosilicate_glass', 'HSSS强化硼硅玻璃', '悬箱大面积观察窗'),
    ('gtlcore:law_filter_casing', '律法过滤机壳', '用后介质过滤机组'),
    ('gtceu:inert_machine_casing', '惰性机械方块', '稳定介质洁净储腔'),
    ('gtceu:heatproof_machine_casing', '耐热机械方块', '热端工况换热器'),
    ('gtceu:nonconducting_casing', '绝缘机械方块', '加载电源隔离层'),
    ('gtceu:frostproof_machine_casing', '防冻机械方块', '冷端工况换热器'),
    ('gtceu:stable_machine_casing', '稳定机械方块', '参考态样件座'),
    ('gtceu:solid_machine_casing', '坚实机械方块', '加载头底座'),
    ('gtceu:engine_intake_casing[active=false]', '引擎进气方块', '后部通风机组'),
    ('gtceu:stress_proof_casing', '抗应力机械方块', '床身隔振承座'),
    ('gtceu:reaction_safe_mixing_casing', '防反应混合机械方块', '稳定介质调理机组'),
    ('gtceu:vibration_safe_casing', '防振机械方块', '测量桥隔振节点'),
    ('gtceu:plascrete', '塑性混凝土', '四角承载支脚'),
    ('minecraft:light_blue_stained_glass', '淡蓝色染色玻璃', '样件盒隔离窗'),
    ('minecraft:black_stained_glass', '黑色染色玻璃', '前控记录窗'),
    ('minecraft:black_concrete', '黑色混凝土', '观察窗密封衬与光路遮光槽'),
    ('minecraft:sea_lantern', '海晶灯', '检修照明与测量头灯'),
    ('minecraft:gold_block', '金块', '样件校准接点'),
    ('minecraft:copper_block', '铜块', '接地母排与介质泵接头'),
    ('minecraft:iron_block', '铁块', '试件更换夹爪'),
    ('minecraft:obsidian', '黑曜石', '扰动态样件隔离托座'),
    ('minecraft:redstone_block', '红石块', '待接入主控的位置标记'),
    ('minecraft:quartz_block', '石英块', '计量基准尺与防护条'),
    ('hk3gtl:casing_colored_cyan', '青色机壳', '桥架测量线与介质流向细线'),
]
STATES = [row[0] for row in MATERIALS]
NAMES = {state: name for state, name, role in MATERIALS}
ROLES = {state: role for state, name, role in MATERIALS}
(WFV, FRAME, WHITE, EXCHANGE, COMPUTER, ATOMIC, POWER, LASER, TURBINE,
 RECYCLE, VENT, GEAR, PRESSURE, PIPE, GRATE, IRIDIUM, PROCESS, DIMENSION,
 MULTI, LAFIUM, GLASS, FILTER, INERT, HOT, INSULATE, COLD, STABLE,
 SOLID, INTAKE, STRESS, MIXING, VIBRATION, CONCRETE, BLUE, DARKGLASS,
 BLACK, LIGHT, GOLD, COPPER, IRON, OBSIDIAN, CONTROL, QUARTZ, CYAN) = range(1, 45)
PARTS = [
    dict(id='bed', name='分叉隔振床身'),
    dict(id='frames', name='双门承力加载架'),
    dict(id='heads', name='前后纵向加载头'),
    dict(id='suspended', name='中央悬吊试件箱'),
    dict(id='samples', name='双态样件与交换台'),
    dict(id='side-load', name='四组侧向加载器'),
    dict(id='measure', name='上置扫描测量桥'),
    dict(id='conditioning', name='介质调理与电源机组'),
    dict(id='service', name='前控与检修廊'),
]


def build():
    w, h, d = 561, 321, 681
    a = np.zeros((h, d, w), np.uint8)
    owners = np.zeros_like(a)
    current = 1

    def box(lo, hi, material=WFV):
        x, y, z = lo
        X, Y, Z = hi
        a[y:Y + 1, z:Z + 1, x:X + 1] = material
        owners[y:Y + 1, z:Z + 1, x:X + 1] = current if material else 0

    def shell(lo, hi, material=WFV, t=8):
        box(lo, hi, material)
        box(tuple(v + t for v in lo), tuple(v - t for v in hi), 0)

    def beam(p, q, radius, material=FRAME):
        p, q = np.array(p), np.array(q)
        for t in np.linspace(0, 1, int(np.linalg.norm(q - p) * 1.4) + 1):
            c = np.rint(p * (1 - t) + q * t).astype(int)
            box(c - radius, c + radius, material)

    def tank(cx, cz, radius, bottom, top, material):
        zz, xx = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        circle = xx * xx + zz * zz <= radius * radius
        for y in range(bottom, top + 1):
            a[y, cz-radius:cz+radius+1, cx-radius:cx+radius+1][circle] = material
            owners[y, cz-radius:cz+radius+1, cx-radius:cx+radius+1][circle] = current

    for x in (22, 412):
        shell((x, 8, 72), (x + 126, 69, 628), t=4)
        for z in (84, 216, 418, 590):
            box((x + 9, 0, z), (x + 117, 19, z + 24), STRESS)
        box((x + 12, 66, 82), (x + 114, 72, 618), WHITE)
        box((x + 20, 72, 91), (x + 106, 74, 609), FRAME)
        for z in range(100, 610, 44):
            box((x + 2, 23, z), (x + 5, 54, z + 18), FRAME)
            box((x + 121, 23, z), (x + 124, 54, z + 18), FRAME)
    shell((164, 7, 120), (396, 55, 582), t=4)
    for z in (138, 237, 437, 549):
        shell((130, 12, z), (430, 50, z + 25), t=5)
        box((138, 47, z + 7), (422, 54, z + 18), FRAME)
    for x in (4, 500):
        for z in (96, 558):
            box((x, 0, z), (x + 56, 14, z + 58), CONCRETE)
    for x in (0, 522):
        for z in (104, 566):
            box((x, 15, z), (x + 38, 31, z + 42), STRESS)
    for x in (197, 343):
        box((x, 56, 111), (x + 20, 68, 579), FRAME)
        box((x + 5, 69, 117), (x + 15, 72, 573), IRIDIUM)
    box((205, 9, 0), (355, 29, 119))
    box((221, 30, 7), (339, 34, 119), EXCHANGE)
    box((233, 35, 7), (242, 38, 119), IRON)
    box((318, 35, 7), (327, 38, 119), IRON)

    current = 2
    for z in (190, 470):
        for x in (52, 508):
            inner = 125 if x < 280 else 435
            beam((x, 72, z), (inner, 283, z), 26, WFV)
            beam((x, 72, z), (inner, 283, z), 19, 0)
            beam((x, 72, z - 28), (inner, 283, z - 28), 6, FRAME)
            beam((x, 72, z + 28), (inner, 283, z + 28), 6, WHITE)
            beam((x, 72, z - 30), (inner, 283, z - 30), 2, CYAN)
            box((x - 31, 58, z - 39), (x + 31, 91, z + 39), WFV)
            box((inner - 28, 268, z - 36), (inner + 28, 304, z + 36), VIBRATION)
        shell((99, 278, z - 39), (461, 320, z + 39), t=6)
        box((111, 315, z - 36), (449, 320, z - 26), WHITE)
        box((111, 315, z + 26), (449, 320, z + 36), WHITE)
        box((113, 280, z - 40), (447, 286, z - 35), CYAN)
        for x in range(124, 446, 41):
            box((x, 287, z - 40), (x + 16, 307, z - 35), FRAME)
    for x in (124, 423):
        box((x, 285, 218), (x + 13, 299, 442), FRAME)
        box((x + 3, 300, 218), (x + 10, 303, 442), WHITE)

    current = 3
    for z in (108, 516):
        shell((173, 68, z), (387, 183, z + 55), t=7)
        box((184, 75, z + 4), (376, 90, z + 51), SOLID)
        box((185, 164, z + 3), (375, 179, z + 52), WHITE)
        for x in (195, 343):
            box((x, 95, z - 6), (x + 22, 152, z + 61), GEAR)
        face = z + 56 if z < 300 else z - 1
        inner = 222 if z < 300 else 458
        for x in (222, 318):
            beam((x, 126, face), (x, 126, inner), 15, PRESSURE)
            box((x - 20, 103, inner - 10), (x + 20, 149, inner + 10), LAFIUM)
        for x in range(242, 315, 24):
            box((x, 108, z - 2), (x + 10, 147, z + 3), VENT)
        box((205, 184, z + 17), (355, 189, z + 39), BLACK)
        for x in (216, 339):
            box((x, 185, z + 20), (x + 5, 188, z + 36), LIGHT)

    current = 4
    shell((161, 99, 225), (399, 243, 455), t=4)
    for y in (109, 231):
        box((169, y, 225), (391, y + 3, 455), WHITE)
    for x in (161, 393):
        box((x, 117, 241), (x + 6, 227, 439), BLACK)
        box((x, 121, 245), (x + 6, 223, 435), GLASS)
        for z in (277, 337, 397):
            box((x, 117, z), (x + 6, 227, z + 4), WHITE)
    for z in (225, 449):
        box((175, 116, z), (385, 228, z + 6), BLACK)
        box((179, 120, z), (381, 224, z + 6), GLASS)
        for x in (222, 276, 330):
            box((x, 116, z), (x + 5, 228, z + 6), WHITE)
    box((175, 237, 239), (385, 243, 441), BLACK)
    box((184, 238, 248), (376, 243, 432), GLASS)
    for z in (255, 327, 399):
        box((175, 238, z), (385, 248, z + 12), WFV)
        box((178, 249, z + 4), (382, 251, z + 8), WHITE)
    for x in (178, 382):
        for z in (246, 434):
            box((x - 7, 246, z - 7), (x + 7, 281, z + 7), IRIDIUM)
            box((x - 14, 242, z - 14), (x + 14, 255, z + 14), DIMENSION)
            beam((x, 279, z), (130 if x < 280 else 430, 285, z), 8, FRAME)
    for z in range(244, 438, 32):
        box((169, 106, z), (174, 109, z + 12), LIGHT)
        box((386, 106, z), (391, 109, z + 12), LIGHT)

    current = 5
    shell((211, 74, 174), (349, 94, 506), EXCHANGE, t=5)
    for x in (215, 339):
        box((x, 95, 180), (x + 6, 98, 500), IRON)
    for x in (195, 300):
        for z in (260, 365):
            seat = STABLE if x < 280 else OBSIDIAN
            box((x, 111, z), (x + 65, 126, z + 65), seat)
            shell((x + 5, 127, z + 5), (x + 60, 208, z + 60), ATOMIC, t=3)
            box((x + 5, 138, z + 5), (x + 60, 196, z + 5), BLUE)
            box((x + 5, 138, z + 60), (x + 60, 196, z + 60), BLUE)
            for y in (143, 165, 187):
                box((x + 16, y, z + 16), (x + 49, y + 5, z + 49), DIMENSION)
                box((x + 21, y + 1, z + 21), (x + 44, y + 4, z + 44), CYAN)
            for xx in (x + 7, x + 52):
                box((xx, 129, z + 7), (xx + 6, 135, z + 13), GOLD)
            box((x + 17, 209, z + 15), (x + 48, 214, z + 50), IRON)

    current = 6
    for x in (96, 464):
        left = x < 280
        for z in (284, 396):
            shell((x - 29, 77, z - 33), (x + 29, 173, z + 33), WFV, t=6)
            box((x - 24, 169, z - 29), (x + 24, 180, z + 29), WHITE)
            box((x - 23, 95, z - 35), (x + 23, 151, z - 30), GEAR)
            beam((x, 149, z), (148 if left else 412, 149, z), 17, PRESSURE)
            target = 153 if left else 407
            box((target - 7, 126, z - 23), (target + 7, 174, z + 23), LAFIUM)
            box((target - 9, 131, z - 14), (target + 9, 169, z + 14), IRIDIUM)
            beam((x, 86, z), (x, 119, z + 45), 5, PRESSURE)
        for z in (323, 351):
            box((x - 12, 79, z), (x + 12, 151, z + 6), INSULATE)

    current = 7
    shell((188, 258, 318), (372, 278, 362), LASER, t=6)
    box((177, 279, 312), (383, 287, 368), WFV)
    box((184, 288, 322), (376, 290, 358), GRATE)
    for x in (197, 244, 291, 338):
        box((x, 254, 328), (x + 22, 259, 352), BLACK)
        box((x + 4, 251, 333), (x + 18, 253, 347), LIGHT)
    for x in (174, 380):
        box((x, 287, 300), (x + 6, 300, 380), QUARTZ)
        for z in range(303, 379, 12):
            box((x, 294, z), (x + 6, 299, z + 3), BLACK)

    current = 8
    for x in (38, 438):
        shell((x, 77, 523), (x + 84, 177, 627), POWER, t=5)
        box((x - 4, 75, 516), (x + 88, 88, 634), INSULATE)
        box((x + 3, 178, 526), (x + 81, 187, 624), WFV)
        for z in range(534, 619, 18):
            box((x - 1, 103, z), (x + 3, 164, z + 9), VENT)
            box((x + 81, 103, z), (x + 85, 164, z + 9), VENT)
        for xx in (x + 12, x + 60):
            box((xx, 92, 515), (xx + 13, 150, 521), COPPER)
            box((xx - 2, 151, 514), (xx + 15, 160, 522), INSULATE)
    for cx in (175, 385):
        tank(cx, 616, 27, 64, 151, INERT)
        tank(cx, 616, 30, 65, 74, WFV)
        tank(cx, 616, 30, 141, 150, WFV)
        tank(cx, 616, 22, 152, 160, WHITE)
        beam((cx, 62, 594), (cx, 62, 499), 7, PIPE)
        box((cx - 15, 161, 607), (cx + 15, 170, 625), COPPER)
    shell((218, 60, 587), (342, 171, 667), WFV, t=12)
    shell((228, 67, 598), (332, 161, 657), PROCESS, t=5)
    for x, mat in ((231, MIXING), (269, FILTER), (307, MULTI)):
        box((x, 76, 668), (x + 23, 155, 680), mat)
    for x, mat in ((147, COLD), (366, HOT)):
        box((x, 66, 534), (x + 47, 121, 572), mat)
        for z in (539, 552, 565):
            box((x - 2, 72, z), (x + 49, 116, z + 3), VENT)
    for x, mat in ((231, TURBINE), (282, INTAKE)):
        box((x, 172, 606), (x + 46, 194, 648), mat)
    box((247, 71, 560), (313, 116, 582), RECYCLE)
    box((255, 78, 558), (305, 107, 560), WHITE)

    current = 9
    for x in (134, 400):
        box((x, 77, 90), (x + 26, 81, 625), FRAME)
        box((x + 2, 82, 94), (x + 24, 84, 621), GRATE)
        for z in range(98, 625, 50):
            box((x, 85, z), (x + 2, 97, z + 2), WHITE)
            box((x + 24, 85, z), (x + 26, 97, z + 2), WHITE)
            box((x + 4, 84, z), (x + 8, 85, z + 7), LIGHT)
        box((x, 96, 94), (x + 2, 98, 621), WHITE)
        box((x + 24, 96, 94), (x + 26, 98, 621), WHITE)
    for z in (89, 620):
        box((135, 78, z), (425, 82, z + 22), FRAME)
        box((139, 83, z + 3), (421, 85, z + 19), GRATE)
    for x in (140, 400):
        for k in range(12):
            box((x, 8 + k * 6, 20 + k * 5), (x + 20, 13 + k * 6, 25 + k * 5), WHITE)
    box((241, 30, 18), (319, 54, 65), COMPUTER)
    box((235, 30, 24), (325, 37, 68), WFV)
    box((239, 55, 25), (321, 60, 66), WHITE)
    box((247, 40, 17), (313, 50, 18), DARKGLASS)
    box((278, 40, 17), (282, 46, 18), CYAN)
    box((280, 42, 17), (280, 42, 17), CONTROL)
    for x in (247, 301):
        box((x, 46, 16), (x + 12, 48, 16), LIGHT)
    box((248, 61, 34), (312, 65, 58), COMPUTER)
    for x in range(251, 311, 15):
        box((x, 66, 38), (x + 8, 67, 53), VENT)
    for x in (222, 334):
        box((x, 31, 0), (x + 4, 34, 6), QUARTZ)

    data = dict(title='世界维系试验平台 · 悬箱稳界试验坞 A1',
        name='0005-i37-suspended-test-dock-a1', size=[w, h, d],
        controller=[280, 42, 17], controller_face='north', ports=[], paths=[],
        zones=[
            dict(name='悬吊双态样件箱', min=[161, 99, 225], max=[399, 251, 455], pos=[280, 247, 340]),
            dict(name='前加载头与样件交换轨', min=[173, 35, 108], max=[387, 189, 222], pos=[280, 194, 140]),
            dict(name='侧向加载器', min=[67, 77, 251], max=[125, 180, 429], pos=[96, 185, 340]),
            dict(name='测量桥', min=[174, 251, 300], max=[386, 300, 380], pos=[280, 306, 340]),
            dict(name='介质回收与工况机组', min=[145, 60, 534], max=[416, 194, 680], pos=[280, 203, 620]),
            dict(name='主控台', min=[235, 30, 16], max=[325, 67, 68], pos=[280, 77, 37]),
        ], detail_views=[dict(id='core', name='悬箱与样件', target=[280, 177, 340], position=[450, 225, 165])])
    return a, owners, data


if __name__ == '__main__':
    a, owners, data = build()
    counts = np.bincount(a.ravel(), minlength=len(STATES) + 1)
    print(dict(size=data['size'], blocks=int(counts[1:].sum()), materials=int((counts[1:] > 0).sum()),
               wfv=int(counts[WFV]), parts=[int(((owners == i) & (a != 0)).sum()) for i in range(1, len(PARTS) + 1)]))
