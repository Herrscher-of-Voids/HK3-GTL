# -*- coding: utf-8 -*-
"""I41辅材职能修订V2：保留弧幕与扇形布局，去除同形辅材盒。

变更记录 #1（2026-10-28）：GT工业机壳承担基础、承力及青铜母线屏蔽；少量原版材质用于厅体、标定及隔振细部。
"""
import numpy as np
import i41_fan_dispatch_geometry_20261028 as base

ROOT, W, H, D, CX = base.ROOT, base.W, base.H, base.D, base.CX
NAME = 'hk3gtl-i41-material-roles-v2-20261028'
TITLE = '文明能源调度中枢 · 铜母线与分区材质修订'
REPLACEMENTS = dict(
    ROBUST='gtceu:titanium_turbine_casing', PLASCRETE='gtceu:steel_brick_casing',
    POWER='gtceu:bronze_brick_casing', TUNG_PIPE='gtceu:bronze_gearbox',
    ATOMIC='ae2:smooth_sky_stone_block', CLEAN='minecraft:smooth_quartz',
    ASSEMBLY='minecraft:calcite', LASER='minecraft:amethyst_block',
    TURBINE='minecraft:polished_blackstone', MACERATOR='minecraft:polished_blackstone_bricks',
    VENT='minecraft:chiseled_deepslate', GEAR='minecraft:lodestone',
    STEEL_PIPE='minecraft:iron_block', IRIDIUM='minecraft:smooth_stone',
    PROCESS='minecraft:polished_andesite', DIMENSION='minecraft:crying_obsidian',
    MULTI='minecraft:chiseled_polished_blackstone', LAFIUM='minecraft:polished_diorite',
    GLASS='minecraft:tinted_glass', FILTER='minecraft:quartz_bricks',
    INERT='minecraft:black_concrete', HEATPROOF='minecraft:gray_concrete',
    FROST='minecraft:white_concrete', STABLE='minecraft:deepslate_bricks',
    SOLID='minecraft:stone_bricks', INTAKE='minecraft:chiseled_stone_bricks',
    STRESS='minecraft:basalt[axis=y]', MIXING='minecraft:polished_granite',
    VIBRATION='minecraft:cracked_deepslate_tiles', LAMINATED='minecraft:cyan_stained_glass',
    FUSION_GLASS='minecraft:blue_stained_glass', IRON='minecraft:quartz_pillar[axis=y]')
Material = type('Material', (), {key: REPLACEMENTS.get(key, value)
    for key, value in vars(base.Material).items() if key.isupper()})
material = Material()
STATES = sorted(value for key, value in vars(Material).items() if key.isupper())
assert len(STATES) == len(set(STATES)) == 43
IDS = {state: i+1 for i, state in enumerate(STATES)}
ROLES = {getattr(material, key): base.ROLES[value]
    for key, value in vars(base.Material).items() if key.isupper()}
ROLES.update({material.ROBUST: '钛承力肋与落地检修框架', material.PLASCRETE: '钢制条形设备基础',
    material.POWER: '青铜色母线屏蔽及保护机匣外层', material.TUNG_PIPE: '青铜分路保护机壳',
    material.ATOMIC: '深色负载机架隔离内胆', material.CLEAN: '浅色调度厅边框及末端设备护罩',
    material.ASSEMBLY: '调度厅窗带下沿与分层腰线', material.LASER: '少量光谱校准晶体',
    material.TURBINE: '圆形散热风道外框', material.MACERATOR: '散热机组承托座',
    material.VENT: '散热器分列排气栅', material.GEAR: '母线接头的金属耦合件',
    material.STEEL_PIPE: '检修廊不锈钢色分路标线', material.IRIDIUM: '标定台背板',
    material.PROCESS: '检修入口踏步', material.DIMENSION: '孤立测试读数参考片',
    material.MULTI: '联锁仪表面框', material.LAFIUM: '调度厅观察带浅色窗台',
    material.GLASS: '弧幕暗色观察窗口', material.FILTER: '进风百叶装饰隔片',
    material.INERT: '绝缘设备低台', material.HEATPROOF: '散热器鳍片',
    material.FROST: '冷却支路标识套管', material.STABLE: '固定设备矮基础',
    material.SOLID: '检修入口侧壁', material.INTAKE: '进风口阵列',
    material.STRESS: '竖向减振承力短柱', material.MIXING: '检修入口边缘防滑色带',
    material.VIBRATION: '母线支座下隔振垫', material.LAMINATED: '调度大厅青色连续观察带',
    material.FUSION_GLASS: '小型蓝色冷却液位观察口', material.IRON: '厅体入口两侧浅色门柱'})


def _remove_old_detail_boxes(cube):
    # 原盒覆盖了内层机匣；按原绘制次序局部还原，不能直接清空或用实心块填补。
    for i in range(26):
        left, y = 15+(i % 17)*33, 23+(i // 17)*56
        low, high = (left, 20, 332), (left+14, y+11, 350)

        def box(a, b, state):
            lo = tuple(max(a[k], low[k]) for k in range(3))
            hi = tuple(min(b[k], high[k]) for k in range(3))
            if all(lo[k] <= hi[k] for k in range(3)):
                cube[lo[1]:hi[1]+1, lo[2]:hi[2]+1, lo[0]:hi[0]+1] = base.IDS[state] if state else 0

        def shell(a, b, state, thickness=2):
            box(a, b, state)
            box(tuple(v+thickness for v in a), tuple(v-thickness for v in b), None)

        box(low, high, None)
        for x in range(low[0], high[0]+1):
            top = round(138+146*(1-((x-CX)/CX)**2))
            for floor in range(26, top-15, 28):
                box((x, floor, 320), (x, floor, 468), base.material.IWV)
        for x in range(0, W, 33):
            top = min(round(138+146*(1-((v-CX)/CX)**2)) for v in (x, min(x+8, W-1)))
            for floor in range(40, top-18, 28):
                box((x, floor, 312), (min(x+8, W-1), floor+2, 468), base.material.GRATE)
        for x in range(12, W-23, 33):
            top = min(round(138+146*(1-((v-CX)/CX)**2)) for v in (x, x+23))
            for floor in range(20, top-30, 28):
                shell((x, floor, 331), (x+23, floor+23, 361), base.material.IWV)
                shell((x+5, floor+1, 337), (x+18, floor+17, 355), base.material.POWER)
                box((x+6, floor+16, 334), (x+17, floor+20, 338), base.material.COMPUTER)


def build():
    cube, data = base.build()
    _remove_old_detail_boxes(cube)
    remap = np.zeros(len(base.STATES)+1, dtype=np.uint8)
    for key, value in vars(base.Material).items():
        if key.isupper():
            remap[base.IDS[value]] = IDS[getattr(material, key)]
    cube = remap[cube]

    def box(a, b, state):
        x, y, z = a; X, Y, Z = b
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D
        cube[y:Y+1, z:Z+1, x:X+1] = IDS[state] if state else 0

    # 前部弧幕的铜总线齐贴原承力框；接头、绝缘垫及检修层各有实际位置。
    for x in range(9, W-9):
        top = round(138+146*(1-((x-CX)/CX)**2))
        for y in range(28, top-14, 56):
            box((x, y, 312), (x, y+2, 318), material.POWER)
    for x in range(33, W-20, 66):
        top = round(138+146*(1-((x-CX)/CX)**2))
        for y in range(28, top-14, 56):
            box((x, y-3, 312), (x+6, y-1, 318), material.VIBRATION)
            box((x+1, y, 310), (x+5, y+3, 313), material.GEAR)
    # 调度厅仅局部使用浅色石材；大面积基础和支撑仍是GT钢与钛。
    for a, b in (((188, 13, 0), (191, 72, 2)), ((399, 13, 0), (402, 72, 2)),
                 ((192, 70, 0), (398, 73, 2))):
        box(a, b, material.CLEAN)
    for y in (39, 57):
        box((194, y, 0), (396, y+1, 1), material.ASSEMBLY)
    box((194, 58, 0), (396, 59, 1), material.LAFIUM)
    for x in (275, 313):
        box((x, 13, 1), (x+2, 37, 3), material.IRON)
    box((199, 20, 0), (200, 35, 0), material.FUSION_GLASS)
    for x in (284, 304):
        box((x, 65, 0), (x+2, 66, 0), material.GOLD)
    # 下部检修入口：踏步、侧壁、隔振短柱与不同用途的护栏构成一组设备入口。
    for x in (51, 515):
        box((x, 10, 306), (x+24, 13, 318), material.STABLE)
        for step in range(3):
            box((x+2, 14+step*2, 308+step*3), (x+22, 15+step*2, 310+step*3), material.PROCESS)
        for dx in (0, 22):
            box((x+dx, 14, 309), (x+dx+2, 27, 318), material.SOLID)
            box((x+dx, 28, 313), (x+dx+2, 40, 318), material.STRESS)
        box((x+3, 14, 307), (x+21, 15, 307), material.MIXING)
        box((x+3, 26, 315), (x+21, 28, 318), material.STEEL_PIPE)
    # 两侧散热组以圆形风道和薄鳍片表达设备职能，不再循环摆放同尺寸材料盒。
    for cx in (108, 482):
        box((cx-19, 10, 306), (cx+19, 13, 318), material.MACERATOR)
        box((cx-17, 14, 311), (cx+17, 18, 318), material.INERT)
        for x in range(cx-16, cx+17):
            for y in range(23, 56):
                radius = (x-cx)**2+(y-39)**2
                if 12**2 <= radius <= 16**2:
                    box((x, y, 313), (x, y, 318), material.TURBINE)
        box((cx-2, 19, 316), (cx+2, 55, 318), material.HEATPROOF)
        for dx in (-9, -3, 3, 9):
            box((cx+dx, 26, 314), (cx+dx+1, 51, 318), material.VENT)
        box((cx-10, 19, 315), (cx+10, 22, 318), material.INTAKE)
        for dx in (-12, 10):
            box((cx+dx, 20, 312), (cx+dx+2, 54, 315), material.FILTER)
        box((cx-11, 56, 316), (cx+11, 59, 318), material.FROST)
    # 光谱标定与隔离测试读数台：薄片、晶体和仪表框围绕已有调度脊分工使用。
    for cx in (225, 365):
        box((cx-18, 98, 315), (cx+18, 103, 318), material.IRIDIUM)
        box((cx-17, 104, 316), (cx+17, 121, 318), material.MULTI)
        box((cx-13, 106, 314), (cx-2, 118, 316), material.OBSIDIAN)
        box((cx+3, 106, 314), (cx+13, 118, 316), material.DIMENSION)
        for dx in (-10, 6):
            box((cx+dx, 104, 311), (cx+dx+3, 109, 315), material.LASER)
    data.update(name=NAME, title=TITLE, candidate_version='V2',
        description='保留六路扇形负载港与连续弧幕。GT钢基础、钛承力肋、青铜色母线屏蔽及分路保护壳按职责分区；浅色调度厅窗带、散热风道、检修入口和光谱标定台使用少量必要辅材，不再用26种材料轮流堆同尺寸盒子。')
    data['construction_notes']['materials'] = 'GT工业材料承担主体、基础和承重；原版仅辅助厅体、玻璃、隔振、标定与风道细节，预览标记不提供功能。'
    return cube, data


if __name__ == '__main__':
    from scipy import ndimage
    cube, data = build()
    counts = np.bincount(cube.ravel(), minlength=len(STATES)+1)
    blocks = int(counts[1:].sum())
    assert np.all(counts[1:]) and 9720448 < blocks < 12697362
    assert counts[IDS[material.IWV]] == counts[1:].max()
    assert counts[IDS[material.CONTROL]] == 1 and counts[IDS[material.PORT]] == 6
    assert data['size'] == [591, 285, 471] and data['controller'] == [295, 27, 0]
    labels, components = ndimage.label(cube != 0)
    assert components == 1, ('存在游离件', components)
    vanilla = sum(int(counts[IDS[s]]) for s in STATES if s.startswith('minecraft:') and s != material.CONTROL)
    print(dict(blocks=blocks, ordinary_materials=len(STATES)-2, total_materials=len(STATES),
        iwv=int(counts[IDS[material.IWV]]), components=components, vanilla=vanilla,
        vanilla_share=vanilla/(blocks-7), size_xyz=data['size'], controller=data['controller']))
