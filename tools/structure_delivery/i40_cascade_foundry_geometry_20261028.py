# -*- coding: utf-8 -*-
"""I40四系贯流合成工场：独立反应、稳定与成品线的完整体素候选。
变更记录 #1（2026-10-28）：新增独立造型；不修改正式Pattern、实例或既有批准结构。
"""
from pathlib import Path
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 601, 291, 481, 300
NAME = 'hk3gtl-i40-cascade-foundry-v1-20261028'
TITLE = '文明奇观材料合成中心 · 四系贯流合成工场'


class Material:
    WFV = 'hk3gtl:voltage_machine_casing_wfv'
    CONTROL = 'minecraft:diamond_block'
    PORT = 'hk3gtl:industrial_port_casing'
    ROBUST = 'gtceu:robust_machine_casing'
    CLEAN = 'gtceu:clean_machine_casing'
    ASSEMBLY = 'gtceu:assembly_line_casing'
    COMPUTER = 'gtceu:advanced_computer_casing'
    ATOMIC = 'gtceu:atomic_casing'
    POWER = 'gtceu:high_power_casing'
    LASER = 'gtceu:laser_safe_engraving_casing'
    TURBINE = 'gtceu:stainless_steel_turbine_casing'
    MACERATOR = 'gtceu:secure_maceration_casing'
    VENT = 'gtceu:computer_heat_vent'
    GEAR = 'gtceu:tungstensteel_gearbox'
    TUNG_PIPE = 'gtceu:tungstensteel_pipe_casing'
    STEEL_PIPE = 'gtceu:steel_pipe_casing'
    GRATE = 'gtceu:assembly_line_grating'
    IRIDIUM = 'gtlcore:iridium_casing'
    PROCESS = 'gtlcore:process_machine_casing'
    DIMENSION = 'gtlcore:dimension_connection_casing'
    MULTI = 'gtlcore:multi_functional_casing'
    LAFIUM = 'gtlcore:lafium_mechanical_casing'
    GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
    FILTER = 'gtlcore:law_filter_casing'
    INERT = 'gtceu:inert_machine_casing'
    HEATPROOF = 'gtceu:heatproof_machine_casing'
    INSULATE = 'gtceu:nonconducting_casing'
    FROST = 'gtceu:frostproof_machine_casing'
    STABLE = 'gtceu:stable_machine_casing'
    SOLID = 'gtceu:solid_machine_casing'
    INTAKE = 'gtceu:engine_intake_casing[active=false]'
    STRESS = 'gtceu:stress_proof_casing'
    MIXING = 'gtceu:reaction_safe_mixing_casing'
    VIBRATION = 'gtceu:vibration_safe_casing'
    PLASCRETE = 'gtceu:plascrete'
    LAMINATED = 'gtceu:laminated_glass'
    FUSION_GLASS = 'gtceu:fusion_glass'
    STEEL = 'gtceu:steel_machine_casing'
    BLUE_GLASS = 'minecraft:light_blue_stained_glass'
    BLACK_GLASS = 'minecraft:black_stained_glass'
    LIGHT = 'minecraft:sea_lantern'
    GOLD = 'minecraft:gold_block'
    IRON = 'minecraft:iron_block'
    OBSIDIAN = 'minecraft:obsidian'


material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {state: i + 1 for i, state in enumerate(STATES)}
ROLES = {state: '按四系工艺分配的合成设备构件' for state in STATES}
ROLES.update({material.WFV: '反应塔三层屏蔽、成品机匣与工艺长廊的主体机械外壳',
    material.PORT: '齐平嵌入工艺机匣的接口占位，无真实仓室功能',
    material.CONTROL: '中轴质检桥楼主控位置，非正式控制器',
    material.ROBUST: '独立反应塔的承重环梁、斜向加料架与检修桥',
    material.CLEAN: '独立稳定化冷却廊的隔离罩与检修盖板',
    material.INSULATE: '约束陶瓷烧结内衬及导能线绝缘层',
    material.COMPUTER: '认知信息载体刻写阵列与共享质检设备',
    material.LASER: '认知载体精密刻写机匣',
    material.GRATE: '炉肩检修环、设备间维护栈道',
    material.PLASCRETE: '四条设备条基，不铺设整幅实心底板',
    material.GOLD: '导能晶片接点，仅用于少量功能细节',
    material.FUSION_GLASS: '合成窗口的耐场透明观察层',
    material.LAMINATED: '前部共享质检桥楼窗带',
})


def build():
    grid = np.zeros((H, D, W), dtype=np.uint8)

    def box(a, b, state):
        x, y, z = a; X, Y, Z = b
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (a, b)
        grid[y:Y+1, z:Z+1, x:X+1] = IDS[state] if state else 0

    def shell(a, b, state, t=3):
        box(a, b, state)
        if all(b[k]-a[k]+1 > 2*t for k in range(3)):
            box(tuple(v+t for v in a), tuple(v-t for v in b), None)

    def beam(a, b, state, r=2):
        n = max(abs(a[k]-b[k]) for k in range(3))
        for i in range(n+1):
            p = [round(a[k]+(b[k]-a[k])*i/max(n, 1)) for k in range(3)]
            box(tuple(max(0, v-r) for v in p),
                tuple(min(s-1, v+r) for v, s in zip(p, (W, H, D))), state)

    def ring(cx, cz, y0, y1, radius, thickness, state, shape='round'):
        zz, xx = np.ogrid[-radius:radius+1, -radius:radius+1]
        distance = np.sqrt(xx*xx+zz*zz) if shape == 'round' else np.maximum(np.maximum(abs(xx), abs(zz)), (abs(xx)+abs(zz))*.707107)
        mask = (distance <= radius) & (distance > radius-thickness)
        for y in range(y0, y1+1):
            section = grid[y, cz-radius:cz+radius+1, cx-radius:cx+radius+1]
            section[mask] = IDS[state]

    centers = (78, 226, 374, 522)
    branches = ('导能晶片与带材', '约束陶瓷与隔离件', '自组织复材与预制件', '认知信息载体与传感阵列')
    zones = []
    # 四条条基、贯通的工作巷道与前侧质检桥，不以实心总底座堆料。
    for cx in centers:
        left, right = max(0, cx-74), min(W-1, cx+74)
        box((left, 0, 4), (right, 4, D-1), material.PLASCRETE)
        box((left+2, 5, 10), (right-2, 9, D-3), material.WFV)
        for x in (cx-67, cx+67):
            box((x, 10, 13), (x+2, 12, D-8), material.GRATE)
            for z in range(22, 465, 30):
                box((x, 10, z), (x+2, 13, z+3), material.LIGHT)
    box((0, 0, 0), (W-1, 6, 26), material.WFV)
    # 四系各自拥有三层分隔反应器、回流内衬与空置反应腔。
    for index, cx in enumerate(centers):
        top = 290 if index in (0, 3) else 272
        shape = 'round' if index in (0, 3) else 'octagon'
        cz = 389
        lining = (material.ATOMIC, material.INSULATE, material.INERT, material.LASER)[index]
        for y in range(12, top-14):
            if y < 55: radius = 70
            elif y < 110: radius = round(70-(y-55)*.18)
            elif y < 205: radius = 60
            else: radius = max(34, round(60-(y-205)*.33))
            ring(cx, cz, y, y, radius, 4, material.WFV, shape)
            ring(cx, cz, y, y, radius-12, 3, material.WFV, shape)
            ring(cx, cz, y, y, radius-23, 3, lining, shape)
        ring(cx, cz, top-14, top, 34, 10, material.WFV, shape)
        ring(cx, cz, top-4, top-1, 36, 4, material.ROBUST, shape)
        # 炉肩检修环、法兰和沿壁的介质分配器，每层均附着塔体。
        for y, radius in ((22, 73), (52, 73), (108, 64), (158, 64), (204, 64), (245, 50)):
            ring(cx, cz, y, y+3, radius, 13, material.ROBUST, shape)
            ring(cx, cz, y+4, y+4, radius, 6, material.GRATE, shape)
        for dx in (-28, 28):
            box((cx+dx-3, 13, 316), (cx+dx+3, 203, 324), material.TUNG_PIPE)
            for y in range(32, 200, 23):
                box((cx+dx-5, y, 313), (cx+dx+5, y+4, 328), material.WFV)
        # 反应腔内的工艺层板从压力内衬向中央伸入，中央保留贯流空间。
        for y in range(25, top-25, 18):
            ring(cx, cz, y, y+4, 39 if y < 210 else 28, 12, lining, shape)
            ring(cx, cz, y, y+2, 43 if y < 210 else 31, 4, material.PROCESS, shape)
            radius = 70 if y < 55 else round(70-(y-55)*.18) if y < 110 else 60 if y < 205 else max(34, round(60-(y-205)*.33))
            box((cx-radius, y, cz-1), (cx+radius, y+1, cz+1), material.ROBUST)
            box((cx-1, y, cz-radius), (cx+1, y+1, cz+radius), material.ROBUST)
        # 侧视开窗允许辨识三层屏蔽和中空腔，不把塔体画成纯实心柱。
        for y in (76, 130, 180):
            box((cx-13, y, 329), (cx+13, y+9, 334), material.FUSION_GLASS)
            box((cx-14, y-2, 327), (cx+14, y-1, 335), material.IRIDIUM)
        # 四条独立的斜向加料桥；高端接入炉颈，低端接后部投料机匣。
        shell((cx-27, 10, 454), (cx+27, 65, 480), material.WFV, 5)
        for dx in (-18, 18):
            beam((cx+dx, 55, 461), (cx+dx, top-20, 410), material.ROBUST, 3)
        beam((cx, 56, 461), (cx, top-20, 410), material.ASSEMBLY, 7)
        for y in range(64, top-24, 16):
            z = round(461-(y-56)*51/(top-76))
            box((cx-8, y, z-8), (cx+8, y+4, z+8), material.WFV)
        # 前向分段稳定化设备廊：各系物料独立，不交叉混料。
        shell((cx-60, 10, 35), (cx+60, 91, 308), material.WFV, 3)
        box((cx-53, 17, 42), (cx+53, 23, 301), material.CLEAN)
        for z in range(45, 300, 35):
            box((cx-62, 10, z), (cx+62, 16, z+5), material.ROBUST)
            box((cx-62, 83, z), (cx+62, 94, z+5), material.ROBUST)
            for x in (cx-62, cx+57):
                box((x, 17, z), (x+5, 82, z+5), material.WFV)
            box((cx-49, 91, z+9), (cx+49, 94, z+15), material.GLASS)
        # 屋脊散热箱和分区开口让长廊具有设备层次，而不是四个光滑盒子。
        for z in range(51, 290, 35):
            shell((cx-24, 91, z), (cx+24, 112, z+19), material.WFV, 3)
            box((cx-20, 110, z+3), (cx+20, 112, z+16), material.VENT)
            for x in (cx-60, cx+59):
                box((x, 35, z), (x+1, 65, z+17), material.BLACK_GLASS)
        # 中央物料床、分级机架和实心设备芯均有可辨认用途。
        for z in range(52, 295, 26):
            box((cx-43, 24, z), (cx+43, 30, z+15), material.WFV)
            box((cx-25, 31, z+2), (cx+25, 42, z+13), (material.POWER, material.HEATPROOF, material.MIXING, material.COMPUTER)[index])
            for x in (cx-44, cx+38):
                box((x, 25, z), (x+6, 67, z+15), material.WFV)
            box((cx-44, 65, z), (cx+44, 72, z+15), material.WFV)
            box((cx-34, 68, z+3), (cx+34, 73, z+11), lining)
        for dx in (-47, 47):
            box((cx+dx-3, 27, 43), (cx+dx+3, 30, 314), material.STEEL_PIPE)
        shell((cx-47, 10, 270), (cx+47, 121, 327), material.WFV, 3)
        box((cx-38, 38, 270), (cx+38, 93, 273), material.BLUE_GLASS)
        for dx in (-38, 30):
            box((cx+dx, 12, 278), (cx+dx+8, 105, 319), material.STABLE)
        zones.extend([dict(name=branches[index]+'独立反应塔', pos=[cx, 158, 326]),
                      dict(name=branches[index]+'稳定化与分级长廊', pos=[cx, 91, 80])])
    # 共享的只是采样检测桥；四条物料床与回流线互不合流。
    shell((112, 12, 0), (488, 62, 32), material.WFV, 4)
    box((120, 40, 0), (480, 50, 0), material.LAMINATED)
    box((CX-22, 18, 0), (CX+22, 38, 7), material.WFV)
    for x in range(128, 480, 24):
        box((x, 16, 8), (x+10, 37, 24), material.COMPUTER)
        box((x+2, 34, 7), (x+8, 38, 10), material.GLASS)
    # 小型专用器件按工艺职责布置，材料多样性不靠大量杂色铺砌。
    details = [(material.TURBINE, '介质循环泵'), (material.MACERATOR, '分级破碎机'),
        (material.GEAR, '成品辊系'), (material.DIMENSION, '空间标定模块'),
        (material.MULTI, '多段介质处理'), (material.LAFIUM, '耐蚀稳定槽'),
        (material.FILTER, '分流过滤器'), (material.FROST, '低温冷却器'),
        (material.SOLID, '基础泵座'), (material.INTAKE, '循环进气口'),
        (material.STRESS, '压延隔振座'), (material.VIBRATION, '精密隔振台'),
        (material.STEEL, '维护设备罩'), (material.LIGHT, '检验光源'),
        (material.GOLD, '导能接点'), (material.IRON, '标定试片'),
        (material.OBSIDIAN, '黑体标定片')]
    for n, (state, _) in enumerate(details):
        cx = centers[n % 4]; z = 55+(n//4)*42
        box((cx-9, 43, z), (cx+9, 49, z+13), state)
    # 零散接点、设备状态窗均附着实体；不用彩色分区代替工业结构。
    for cx in centers:
        box((cx-17, 72, 47), (cx+17, 76, 56), material.INSULATE)
        box((cx-12, 77, 47), (cx+12, 77, 52), material.BLACK_GLASS)
    controller = [CX, 27, 0]
    ports = []
    for i, cx in enumerate(centers):
        for dx, purpose in ((-60, branches[i]+'进料'), (60, branches[i]+'成品交接')):
            p = [cx+dx, 28, 65 if dx < 0 else 200]
            grid[p[1], p[2], p[0]] = IDS[material.PORT]
            ports.append(dict(id=purpose, pos=p, face='west' if dx < 0 else 'east', purpose='该系独立接口占位；实际能力待验'))
    for dx, purpose in ((-72, '合法供能'), (-48, '稳定介质'), (48, '质检记录'), (72, '维护回执')):
        p = [CX+dx, 27, 0]
        grid[p[1], p[2], p[0]] = IDS[material.PORT]
        ports.append(dict(id=purpose, pos=p, face='north', purpose='共享质检与设备服务接口占位'))
    grid[27, 0, CX] = IDS[material.CONTROL]
    # 外侧设备条基与桥楼共同确定真实包围盒，不扩张空白导出范围。
    box((0, 0, 4), (4, 4, 480), material.ROBUST)
    box((596, 0, 4), (600, 4, 480), material.ROBUST)
    description = '四条贯流生产轴由后部高耸的三层反应塔，接入前部稳定化、精密加工及成品分级长廊。圆肩与八角塔体、分段冷却机匣、斜向加料桥和落地检修环表达重型工业合成；四系分别处理导能、约束、重构与认知材料，仅共享前侧质检桥。WFV机壳统一主体，灰银承力环与克制的透明观察带建立工业层次。'
    data = dict(key='i40', name=NAME, title=TITLE, size=[W, H, D], controller=controller,
        controller_face='north', ports=ports, paths=[], zones=zones,
        description=description, target_voltage='WFV', branch_names=list(branches),
        construction_notes=dict(orientation='主控北向/-Z；蓝图从0起算；X=300为整宽第301格。',
            anchor='结构底部建议世界Y=-60，最高实体Y=230；Schematic Offset不是绝对世界坐标。',
            boundary='四系各自备料、合成、稳定化、分级与成分回流；认知材料不等于量产意识。',
            approval='独立候选；未批准、未实装，不冒充正式工艺运行。'))
    return grid, data


if __name__ == '__main__':
    cube, data = build()
    counts = np.bincount(cube.ravel(), minlength=len(STATES)+1)
    print({'blocks': int(counts[1:].sum()), 'materials': int((counts[1:] > 0).sum()),
        'wfv': int(counts[IDS[material.WFV]]), 'unused': [s for s in STATES if not counts[IDS[s]]],
        'size_xyz': data['size'], 'volume': math.prod(data['size'])})
