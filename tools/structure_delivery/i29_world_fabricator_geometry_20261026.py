# -*- coding: utf-8 -*-
"""I29独立构图：双瓣坐标模腔、球形模拟胚与两翼编译工厂。

【变更记录 #1】2026-10-26：从空白坐标生成新候选；不读取旧I29几何，不修改游戏资源。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 381, 223, 361
CX, CZ = 190, 180
NAME = 'hk3gtl-i29-simulated-world-fabricator-v1-20261026'
TITLE = '模拟世界泡构筑机 · 双瓣造界工厂'
ICV = 'hk3gtl:voltage_machine_casing_icv'
PORT = 'hk3gtl:industrial_port_casing'
CONTROL = 'minecraft:diamond_block'
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
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
BLACK_GLASS = 'minecraft:black_stained_glass'
BLACK = 'minecraft:black_concrete'
LIGHT = 'minecraft:sea_lantern'
PALETTE_ROLES = {
    ICV: '双瓣模腔、编译厂房及承重箱梁的ICV主体机壳',
    PORT: '齐平嵌入设备外墙的候选接口占位', CONTROL: '控制厅中轴主控位置标记',
    ROBUST: '地下箱梁、模腔底架与基础边缘', CLEAN: '模腔包边、厂房窗框与检修台外饰',
    ASSEMBLY: '机房楼板及模组装配设备', COMPUTER: '世界模型编译与误差记录计算阵列',
    ATOMIC: '世界种子约束与场发生端', POWER: '造界供能变换设备', LASER: '模腔内壁的坐标写入阵列',
    TURBINE: '冷却设备完整壳体', MACERATOR: '原料预处理设备', VENT: '散热百叶与风道上盖',
    GEAR: '模腔开合传动与机械检修段', TUNG_PIPE: '高能传递封闭管路',
    STEEL_PIPE: '双回路冷却封闭管路', GRATE: '检修平台与风道栅格', IRIDIUM: '种子夹持环与局部屏蔽',
    PROCESS: '物质编织与批次封装设备', DIMENSION: '模腔空间坐标整形设备',
    MULTI: '厂房内综合控制机组', LAFIUM: '同步伺服设备面', GLASS: '隔离观测窗',
    FILTER: '模型误差检核与批次审计机组', INERT: '种子隔离设备', HEATPROOF: '热端母线屏蔽',
    INSULATE: '高能设备绝缘底架', FROST: '冷端循环设备', STABLE: '种子场稳定辅助机组',
    SOLID: '原料设备基础机壳', INTAKE: '冷却机组进气面', STRESS: '模腔合拢承压支座',
    MIXING: '原料分配与物质预混设备', VIBRATION: '两翼计量设备减振壳体',
    PLASCRETE: '设备间洁净地坪，仅用于实际厂房内部',
    BLUE_GLASS: '静态坐标写入光路示意', BLACK_GLASS: '模拟胚边缘观测表层',
    BLACK: '等半径黑色模拟世界泡薄壳', LIGHT: '维护通道与写入端照明',
}
CELLS = {}


def put(x, y, z, state, replace=False):
    p = (int(x), int(y), int(z))
    assert 0 <= p[0] < W and 0 <= p[1] < H and 0 <= p[2] < D, p
    if replace or p not in CELLS:
        CELLS[p] = state


def box(lo, hi, state, replace=False):
    for y in range(lo[1], hi[1] + 1):
        for z in range(lo[2], hi[2] + 1):
            for x in range(lo[0], hi[0] + 1):
                put(x, y, z, state, replace)


def line(a, b, state, radius=0, replace=False):
    """逐轴连接采样点；斜撑在六邻接意义下连续。"""
    steps = max(abs(a[i] - b[i]) for i in range(3))
    p = list(a)
    for k in range(steps + 1):
        q = [round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3)]
        for axis in range(3):
            while p[axis] != q[axis]:
                p[axis] += 1 if q[axis] > p[axis] else -1
                box(tuple(v - radius for v in p), tuple(v + radius for v in p), state, replace)
        box(tuple(v - radius for v in q), tuple(v + radius for v in q), state, replace)


def foundation():
    # 箱梁层间留空；两翼厂房和中央模腔分别有连续基础，前后廊连接。
    footprints = ((0, 100, 38, 322), (280, 380, 38, 322), (72, 308, 20, 340))
    for x0, x1, z0, z1 in footprints:
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rim = min(x - x0, x1 - x, z - z0, z1 - z) < 4
                beam = (x - x0) % 24 < 5 or (z - z0) % 28 < 5
                for y in range(24):
                    if y < 4 or y >= 20 or rim or beam:
                        put(x, y, z, ROBUST if y in (0, 3, 19, 23) else ICV)
    # 中轴到正面入口的双层检修引桥是建筑的可读入口。
    box((156, 0, 0), (224, 23, 27), ICV)
    box((156, 24, 0), (224, 24, 27), GRATE)
    box((156, 0, 333), (224, 23, 360), ICV)
    box((156, 24, 333), (224, 24, 360), GRATE)


def hall(x0, x1, z0, z1, ymax, kind):
    """四层可维护厂房；厚壁含机柜/母线夹层，屋面设备服务内部楼层。"""
    for y in range(24, ymax + 1):
        floor = (y - 24) % 19 < 3 or y >= ymax - 3
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                edge = min(x - x0, x1 - x, z - z0, z1 - z)
                if floor:
                    s = ICV if edge < 7 or (x - x0) % 18 < 4 else ASSEMBLY
                    put(x, y, z, s, True)
                elif edge < 5:
                    along = (z - z0) if min(x - x0, x1 - x) < 5 else (x - x0)
                    window = edge == 0 and along % 24 in range(7, 18) and (y - 24) % 19 in range(7, 14)
                    s = GLASS if window else ICV
                    if edge == 0 and (y - 24) % 19 in (3, 16):
                        s = CLEAN
                    put(x, y, z, s, True)
    states = (COMPUTER, FILTER, MULTI, DIMENSION) if kind == 'compiler' else (PROCESS, MIXING, MACERATOR, VIBRATION)
    for floor_y in range(27, ymax - 12, 19):
        for i, x in enumerate(range(x0 + 9, x1 - 10, 17)):
            for j, z in enumerate(range(z0 + 9, z1 - 10, 22)):
                box((x, floor_y, z), (x + 7, floor_y + 9, z + 10), states[(i + j) % len(states)], True)
                box((x, floor_y + 10, z), (x + 7, floor_y + 10, z + 10), VENT, True)
    for z in range(z0 + 12, z1 - 10, 26):
        box((x0 + 8, ymax + 1, z), (x1 - 8, ymax + 7, z + 8), ICV)
        box((x0 + 10, ymax + 8, z + 1), (x1 - 10, ymax + 8, z + 7), VENT)


def factory_wings():
    hall(2, 87, 50, 310, 101, 'compiler')
    hall(293, 378, 50, 310, 101, 'compiler')
    # 模型与种子在前控制厅汇流，成品批次从后封装厅输出。
    hall(113, 267, 21, 65, 64, 'control')
    hall(113, 267, 295, 339, 64, 'process')
    for side in (0, 1):
        for z in (79, 150, 221):
            x0 = 10 if side == 0 else 309
            x1 = x0 + 61
            box((x0, 110, z), (x1, 114, z + 39), ICV)
            box((x0 + 4, 115, z + 4), (x1 - 4, 127, z + 35), FROST)
            box((x0 + 7, 128, z + 7), (x1 - 7, 133, z + 32), TURBINE)
            box((x0 + 9, 134, z + 9), (x1 - 9, 135, z + 30), INTAKE)
            for x in range(x0 + 3, x1 - 2, 12):
                box((x, 110, z), (x + 3, 133, z + 39), ICV, True)
                box((x, 134, z), (x + 3, 134, z + 39), STEEL_PIPE)
            box((x0 + 20, 102, z + 13), (x0 + 41, 109, z + 26), INSULATE)
    # 桥内包含实际封闭的信号干线；跨越检修通道的空间留空。
    for z in (83, 277):
        box((82, 60, z), (298, 65, z + 7), ROBUST)
        box((82, 66, z + 2), (298, 70, z + 5), COMPUTER)
        box((82, 71, z), (298, 72, z + 7), GRATE)


def mould_support():
    # 八角回转基座与四条承重鞍座，留出中央球胚的观察净空。
    for y in range(24, 43):
        for z in range(CZ - 113, CZ + 114):
            for x in range(CX - 113, CX + 114):
                r = max(abs(x - CX), abs(z - CZ), (abs(x - CX) + abs(z - CZ)) / 1.44)
                if 58 <= r <= 113 and (y in range(24, 29) or y >= 38 or int(r) % 19 < 5):
                    put(x, y, z, CLEAN if y in (28, 38, 42) else ICV, True)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, z0 = CX + sx * 80, CZ + sz * 52
            box((x0 - 12, 28, z0 - 16), (x0 + 12, 74, z0 + 16), ICV)
            box((x0 - 9, 43, z0 - 13), (x0 + 9, 64, z0 + 13), STRESS, True)
            box((x0 - 14, 70, z0 - 18), (x0 + 14, 74, z0 + 18), GEAR, True)
    # 胚体由底部场发生器托举，光路确实连接发生器与样本下缘。
    for y in range(28, 79):
        for z in range(CZ - 31, CZ + 32):
            for x in range(CX - 31, CX + 32):
                r2 = (x - CX) ** 2 + (z - CZ) ** 2
                if (24 <= y <= 35 and r2 <= 31 ** 2) or (r2 <= 21 ** 2 and y <= 53):
                    put(x, y, z, ATOMIC if y in (35, 53) else ICV, True)
                elif 17 ** 2 <= r2 <= 21 ** 2 and y > 53:
                    put(x, y, z, BLUE_GLASS, True)
    # Four exposed cradle beams connect the field generator to the outer bearing ring.
    for side in (-1, 1):
        xa, xb = sorted((CX + side * 22, CX + side * 58))
        box((xa, 28, CZ - 4), (xb, 32, CZ + 4), ICV, True)
        box((xa, 28, CZ - 5), (xb, 28, CZ - 5), ROBUST, True)
        box((xa, 28, CZ + 5), (xb, 28, CZ + 5), ROBUST, True)
        za, zb = sorted((CZ + side * 22, CZ + side * 58))
        box((CX - 4, 28, za), (CX + 4, 32, zb), ICV, True)
        box((CX - 5, 28, za), (CX - 5, 28, zb), ROBUST, True)
        box((CX + 5, 28, za), (CX + 5, 28, zb), ROBUST, True)


def curved_moulds():
    # 两瓣为同一球面的左右凹模，前后留口；银色连续边框、金色蒙皮、内壁写入片分工明确。
    cy = 126
    for dz in range(-92, 93):
        for dy in range(-83, 93):
            radial = dy * dy + dz * dz
            for dx in range(31, 100):
                r2 = dx * dx + radial
                skin = 92 ** 2 <= r2 <= 99 ** 2
                lining = 84 ** 2 <= r2 <= 88 ** 2
                rib = (abs(dz) % 23 < 4 or abs(dy + 83) % 25 < 4) and 84 ** 2 <= r2 <= 99 ** 2
                if not (skin or lining or rib):
                    continue
                edge = dx <= 34 or abs(dz) >= 89 or dy <= -80
                state = CLEAN if edge else ICV
                if lining and not rib and not skin:
                    state = LASER if (dy + 83) % 25 < 18 and abs(dz) % 23 < 17 else IRIDIUM
                elif rib and not skin:
                    state = ROBUST
                for side in (-1, 1):
                    put(CX + side * dx, cy + dy, CZ + dz, state, True)
    # 上部两道坐标定位拱来自瓣体支座，最高223格由工艺拱本身形成。
    for zc in (CZ - 40, CZ + 40):
        for y in range(110, 223):
            for x in range(CX - 111, CX + 112):
                radius2 = (x - CX) ** 2 + (y - 112) ** 2
                if 105 ** 2 <= radius2 <= 110 ** 2:
                    for z in range(zc - 5, zc + 6):
                        edge = z in (zc - 5, zc + 5) or radius2 <= 106 ** 2
                        put(x, y, z, CLEAN if edge else ICV, True)
        for x in (CX - 109, CX + 109):
            box((x - 2, 40, zc - 5), (x + 2, 112, zc + 5), ICV)
    # 两瓣背部的实体母线通向翼楼供能夹层。
    for side in (-1, 1):
        for dz in (-57, 0, 57):
            line((CX + side * 91, 119, CZ + dz), (CX + side * 118, 96, CZ + dz), TUNG_PIPE, 3)
            box((CX + side * 119 - 8, 61, CZ + dz - 7), (CX + side * 119 + 8, 101, CZ + dz + 7), ICV)
            box((CX + side * 119 - 6, 69, CZ + dz - 6), (CX + side * 119 + 6, 94, CZ + dz + 6), POWER, True)


def embryo():
    # 三轴同半径；黑色表层是薄壳，绝不以实心球堆料。
    r, cy = 43, 126
    for dy in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                rr = dx * dx + dy * dy + dz * dz
                if (r - 2) ** 2 <= rr <= r ** 2:
                    put(CX + dx, cy + dy, CZ + dz, BLACK_GLASS if abs(dy) <= 1 else BLACK, True)
    # 静态写入束均从内凹模面伸至样本表面，双侧相同，避免无端悬浮。
    for side in (-1, 1):
        for dy, dz in ((0, 0), (18, -18), (-18, 18), (18, 18), (-18, -18)):
            sample_x = round(math.sqrt(r * r - dy * dy - dz * dz))
            source_x = round(math.sqrt(85 * 85 - dy * dy - dz * dz))
            line((CX + side * sample_x, cy + dy, CZ + dz),
                 (CX + side * source_x, cy + dy, CZ + dz), BLUE_GLASS, 1, True)
            box((CX + side * source_x - 3, cy + dy - 3, CZ + dz - 3),
                (CX + side * source_x + 3, cy + dy + 3, CZ + dz + 3), ATOMIC, True)


def service_plants():
    # 前后四排物质整形与批次封装设备，有穿行巷道，不用重复空壳凑材料数。
    states = (INERT, HEATPROOF, SOLID, STABLE, MIXING, PROCESS)
    for row, z in enumerate((74, 273)):
        for col, x in enumerate((106, 134, 162, 182)):
            box((x, 25, z), (x + 15, 28, z + 14), ICV)
            box((x + 2, 29, z + 2), (x + 13, 42, z + 12), states[(col + row) % len(states)])
            box((x + 3, 43, z + 3), (x + 12, 46, z + 11), LAFIUM)
            box((x + 2, 47, z + 2), (x + 13, 48, z + 12), VENT)
            line((x + 8, 38, z + 13), (x + 8, 38, z + 20), STEEL_PIPE, 1)
    # 厂房内洁净操作地坪，量少且用途固定。
    for x0 in (11, 304):
        box((x0, 27, 60), (x0 + 64, 27, 300), PLASCRETE, True)
    # 同步光路按设备内壁埋设，冷却与能量回路保持可读。
    for x in (94, 286):
        box((x - 2, 35, 49), (x + 2, 40, 311), STEEL_PIPE, True)
        for z in range(65, 307, 32):
            box((x - 4, 33, z), (x + 4, 42, z + 7), ICV, True)
            box((x - 3, 43, z + 1), (x + 3, 43, z + 6), LIGHT, True)


def markers():
    control = [CX, 33, 21]
    ports = [
        dict(id='世界模型输入', purpose='控制厅接收有效世界模型与模型参数', pos=[168, 33, 21], face='north'),
        dict(id='真实种子输入', purpose='隔离供料设备接收真实世界泡种子', pos=[212, 33, 21], face='north'),
        dict(id='西翼物质输入', purpose='编织原料计量与预处理', pos=[2, 33, 128], face='west'),
        dict(id='东翼耗材输入', purpose='写入耗材与封装介质', pos=[378, 33, 128], face='east'),
        dict(id='西翼控制能源', purpose='编译与造界场持续用能候选位', pos=[2, 33, 232], face='west'),
        dict(id='东翼冷却流体', purpose='冷端循环与设备散热', pos=[378, 33, 232], face='east'),
        dict(id='未稳定批次输出', purpose='独立模拟批次交给I30稳定，不直接产资源', pos=[168, 33, 339], face='south'),
        dict(id='模型误差记录', purpose='输出模型偏差与构筑审计记录', pos=[212, 33, 339], face='south'),
    ]
    put(*control, CONTROL, True)
    for p in ports:
        put(*p['pos'], PORT, True)
    paths = [dict(name='正面主控操作通道', min=[158, 25, 13], max=[222, 38, 20]),
             dict(name='后侧批次交接通道', min=[158, 25, 340], max=[222, 38, 347])]
    for p in paths:
        for y in range(p['min'][1], p['max'][1] + 1):
            for z in range(p['min'][2], p['max'][2] + 1):
                for x in range(p['min'][0], p['max'][0] + 1):
                    CELLS.pop((x, y, z), None)
    return control, ports, paths


def build():
    CELLS.clear()
    foundation()
    factory_wings()
    mould_support()
    curved_moulds()
    embryo()
    service_plants()
    controller, ports, paths = markers()
    # 以中轴左半侧为材质来源统一重建右半侧；中央列与接口坐标保留。
    for y in range(H):
        for z in range(D):
            for x in range(CX + 1, W):
                CELLS.pop((x, y, z), None)
    for y in range(H):
        for z in range(D):
            for x in range(CX):
                state = CELLS.get((x, y, z))
                if state is not None:
                    CELLS[(W - 1 - x, y, z)] = state
    return dict(key='i29', name=NAME, title=TITLE, size=[W, H, D], controller=controller, ports=ports,
                paths=paths, zones=[
                    dict(name='双瓣坐标模腔', pos=[98, 126, 180]),
                    dict(name='等半径模拟世界泡胚', pos=[190, 168, 180]),
                    dict(name='西翼模型编译工厂', pos=[40, 106, 105]),
                    dict(name='东翼模型校核工厂', pos=[340, 106, 105]),
                    dict(name='种子与模型汇流控制厅', pos=[115, 32, 34]),
                    dict(name='未稳定批次封装与交接厅', pos=[115, 32, 308]),
                ], description='以世界模型和真实种子为输入，在双瓣坐标模腔内构筑独立模拟批次。中央黑色球胚、坐标写入束、曲面模腔和两翼编译工厂构成同一工程体系；未稳定批次交给I30。',
                construction_notes={'orientation': '主控朝北/-Z；蓝图坐标从0起算。',
                                    'anchor': '本地[0,0,0]；推荐世界Y=-60，最高Y=162。',
                                    'approval': '独立外观候选，尚未获负责人批准，不接入实例。'},
                blocks=[dict(pos=list(p), state=s) for p, s in sorted(CELLS.items(), key=lambda t: (t[0][1], t[0][2], t[0][0]))])


if __name__ == '__main__':
    from collections import Counter
    data = build()
    counts = Counter(b['state'] for b in data['blocks'])
    print(len(data['blocks']), len(counts), counts.most_common(8), flush=True)
