# -*- coding: utf-8 -*-
"""I30独立几何：六脊稳界深井、黑色模拟世界泡与双回路稳定设施。

【变更记录 #1】2026-10-27：从空白坐标构图；仅生成外观候选，不改游戏资源。
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
W, H, D = 365, 223, 365
CX, CZ = 182, 182
NAME = 'hk3gtl-i30-simulated-world-stabilizer-v1-20261027'
TITLE = '模拟世界泡稳定控制器 · 六脊稳界深井'
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
BUBBLE_CENTER = (CX, 140, CZ)
BUBBLE_RADIUS = 52
PALETTE_ROLES = {
    ICV: '稳界深井、六道约束脊与服务厂房的ICV主体机壳',
    PORT: '齐平嵌入原生设备外墙的候选接口占位', CONTROL: '正面负载控制厅中轴主控坐标标记',
    ROBUST: '中空井基箱梁、径向承重梁与约束脊脚座', CLEAN: '深井层台边缘、约束肋与窗框银灰包边',
    ASSEMBLY: '服务厂房分层机房楼板', COMPUTER: '模型负载运算机柜与稳态控制阵列',
    ATOMIC: '世界泡底托场发生器及六向磁约束端头', POWER: '约束脊独立供能调节机组',
    LASER: '磁约束脊内侧的局部状态读取面', TURBINE: '双回路换热与循环泵机组壳体',
    MACERATOR: '废介质夹带固体的分离设备', VENT: '换热设备百叶与控制厅散热风道',
    GEAR: '约束钳爪检修传动段', TUNG_PIPE: '约束磁场供能母线', STEEL_PIPE: '稳定介质双回路封闭管路',
    GRATE: '井沿检修走道与设备维护平台', IRIDIUM: '球底托架及约束端局部屏蔽',
    PROCESS: '载体交接、批次状态封装与废介质分流设备', DIMENSION: '批次状态与空间载体交接设备',
    MULTI: '多模型负载调节机柜', LAFIUM: '稳定介质循环计量及伺服设备', GLASS: '服务厂房隔离观察窗',
    FILTER: '废介质净化前的筛分与污染检测设备', INERT: '模拟载体隔离缓冲舱',
    HEATPROOF: '热介质一次回路的设备屏蔽', INSULATE: '磁约束供能机组绝缘底架',
    FROST: '冷介质二次回路的循环换热设备', STABLE: '稳定介质缓冲及压力调节设备',
    SOLID: '重型换热设备基础机壳', INTAKE: '换热设备进气百叶', STRESS: '六脊钳形支座承压面',
    MIXING: '稳定介质补给与回用介质计量混合设备', VIBRATION: '循环泵与批次交接设备减振壳体',
    PLASCRETE: '控制与载体交接厂房内部洁净操作地坪',
    BLUE_GLASS: '约束端与球体之间连续连接的静态磁场示意', BLACK_GLASS: '黑色世界泡赤道观测窄带',
    BLACK: '三轴等半径模拟世界泡薄壳', LIGHT: '井沿、机房及设备维护照明',
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
    """沿各轴补齐采样点，保证斜撑在六邻接意义下不断开。"""
    steps = max(abs(a[i] - b[i]) for i in range(3))
    p = list(a)
    for k in range(steps + 1):
        q = [round(a[i] + (b[i] - a[i]) * k / max(1, steps)) for i in range(3)]
        for axis in range(3):
            while p[axis] != q[axis]:
                p[axis] += 1 if q[axis] > p[axis] else -1
                box(tuple(v - radius for v in p), tuple(v + radius for v in p), state, replace)
        box(tuple(v - radius for v in q), tuple(v + radius for v in q), state, replace)


def radial(angle, radius, y):
    return (round(CX + math.cos(angle) * radius), round(y), round(CZ + math.sin(angle) * radius))


def ring(y0, y1, inner, outer, state, replace=False):
    for z in range(CZ - outer, CZ + outer + 1):
        for x in range(CX - outer, CX + outer + 1):
            r2 = (x - CX) ** 2 + (z - CZ) ** 2
            if inner * inner <= r2 <= outer * outer:
                for y in range(y0, y1 + 1):
                    put(x, y, z, state, replace)


def foundation_pad(x0, x1, z0, z1):
    for y in range(24):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                edge = min(x - x0, x1 - x, z - z0, z1 - z)
                beam = (x - x0) % 27 < 3 or (z - z0) % 30 < 3
                if y < 2 or y >= 22 or edge < 3 or beam:
                    put(x, y, z, ROBUST if y in (0, 3, 20, 23) else ICV)


def deep_well():
    # 井基为多层环形箱梁；中央保留深井净空，只有球底托座贯穿井底。
    for y in range(24):
        for z in range(CZ - 146, CZ + 147):
            for x in range(CX - 146, CX + 147):
                dx, dz = x - CX, z - CZ
                r2 = dx * dx + dz * dz
                if r2 > 146 ** 2:
                    continue
                beam = abs(dx) % 30 < 3 or abs(dz) % 30 < 3
                shell = 64 ** 2 <= r2 and (y < 2 or y >= 22 or r2 >= 143 ** 2 or beam)
                if shell or (y < 2 and r2 < 64 ** 2):
                    put(x, y, z, ROBUST if y in (0, 3, 20, 23) else ICV)
    for y0, y1, inner, outer in ((24, 29, 62, 146), (30, 43, 121, 138),
                                (44, 48, 74, 146), (49, 65, 120, 135), (66, 72, 88, 143)):
        ring(y0, y0 + 1, inner, outer, ICV)
        ring(y1 - 1, y1, inner, outer, ICV)
        ring(y0 + 2, y1 - 2, inner, inner + 2, ICV)
        ring(y0 + 2, y1 - 2, outer - 2, outer, ICV)
        ring(y1, y1, outer - 3, outer, CLEAN, True)
        ring(y1 + 1, y1 + 1, outer - 10, outer - 5, GRATE)
    # 六条径向承重梁将井沿、底托与约束脊连为同一工程体系。
    for k in range(6):
        a = math.pi * k / 3
        line(radial(a, 29, 31), radial(a, 132, 31), ROBUST, 5)
        line(radial(a, 30, 35), radial(a, 119, 35), ICV, 4)
    ring(4, 63, 0, 29, ICV)
    ring(64, 76, 0, 38, ICV)
    ring(76, 80, 0, 38, ATOMIC, True)
    ring(81, 90, 0, 17, STABLE)
    for k in range(6):
        a = math.pi * k / 3
        line(radial(a, 34, 77), radial(a, 36, 103), IRIDIUM, 3, True)


def service_hall(x0, x1, z0, z1, kind, top=89):
    foundation_pad(x0, x1, z0, z1)
    for y in range(24, top + 1):
        floor = (y - 24) % 22 < 2 or y >= top - 1
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                edge = min(x - x0, x1 - x, z - z0, z1 - z)
                if floor:
                    put(x, y, z, ICV if edge < 7 or (x - x0) % 18 < 4 else ASSEMBLY, True)
                elif edge < 2:
                    along = (z - z0) if min(x - x0, x1 - x) < 2 else (x - x0)
                    window = edge == 0 and along % 24 in range(7, 18) and (y - 24) % 22 in range(12, 18)
                    s = GLASS if window else ICV
                    if edge == 0 and (y - 24) % 22 in (4, 19):
                        s = CLEAN
                    put(x, y, z, s, True)
    machines = (COMPUTER, MULTI, DIMENSION, POWER) if kind == 'control' else (FILTER, PROCESS, MACERATOR, MIXING)
    for y in range(26, top - 10, 22):
        for i, x in enumerate(range(x0 + 9, x1 - 13, 19)):
            for j, z in enumerate(range(z0 + 10, z1 - 14, 23)):
                box((x, y, z), (x + 9, y + 11, z + 12), machines[(i + j) % len(machines)], True)
                box((x, y + 12, z), (x + 9, y + 12, z + 12), VENT, True)
    for z in range(z0 + 10, z1 - 13, 26):
        box((x0 + 7, top + 1, z), (x1 - 7, top + 5, z + 11), ICV)
        box((x0 + 10, top + 6, z + 2), (x1 - 10, top + 6, z + 9), VENT)


def service_districts():
    for x0, x1 in ((0, 83), (281, 364)):
        service_hall(x0, x1, 38, 149, 'control')
        service_hall(x0, x1, 215, 326, 'waste', 79)
    service_hall(125, 239, 12, 66, 'control', 67)
    service_hall(125, 239, 298, 352, 'waste', 67)
    foundation_pad(125, 239, 0, 11)
    foundation_pad(125, 239, 353, 364)
    # 井沿与厂房之间保留上下分层的管线廊，承重梁落到井基和机房墙体。
    for z in (104, 256):
        box((70, 24, z), (294, 28, z + 8), ROBUST)
        box((70, 29, z + 2), (294, 33, z + 6), ICV)
        box((70, 34, z), (294, 34, z + 8), GRATE)
    for z0, z1 in ((60, 114), (250, 304)):
        box((165, 24, z0), (199, 29, z1), ICV)
        box((165, 30, z0), (199, 30, z1), GRATE)
    for x0 in (135,):
        box((x0, 26, 21), (x0 + 94, 26, 57), PLASCRETE, True)
        box((x0, 26, 307), (x0 + 94, 26, 343), PLASCRETE, True)
    # 两段宽梯沿井缘升至最高检修台，连接分层走道而非另立楼梯塔。
    for angle in (math.pi * 5 / 6, math.pi * 7 / 6):
        previous = None
        for step in range(43):
            p = radial(angle, 141 - step * 0.8, 30 + step)
            if previous:
                line(previous, p, ROBUST, 2, True)
            box((p[0] - 3, p[1], p[2] - 3), (p[0] + 3, p[1], p[2] + 3), CLEAN, True)
            previous = p


def six_clamps():
    # 六道相互分离的弯脊从井沿脚座合拢；223格高度来自完整钳形约束设备。
    for k in range(6):
        angle = math.pi * k / 3
        foot = radial(angle, 111, 42)
        box((foot[0] - 13, 28, foot[2] - 13), (foot[0] + 13, 58, foot[2] + 13), ICV)
        box((foot[0] - 10, 40, foot[2] - 10), (foot[0] + 10, 52, foot[2] + 10), STRESS, True)
        box((foot[0] - 14, 54, foot[2] - 14), (foot[0] + 14, 58, foot[2] + 14), GEAR, True)
        last = None
        for step in range(101):
            t = step / 100
            radius = 112 - 96 * t ** 1.7
            y = 35 + 183 * math.sin(t * math.pi / 2)
            p = radial(angle, radius, y)
            if last is not None:
                line(last, p, ICV, 4, True)
            else:
                box(tuple(v - 4 for v in p), tuple(v + 4 for v in p), ICV, True)
            # 两条细银边随弯脊曲率连续，不以颜色把球面切成分区。
            for side in (-1, 1):
                edge = (round(p[0] - math.sin(angle) * side * 4), p[1], round(p[2] + math.cos(angle) * side * 4))
                box(tuple(v - 1 for v in edge), tuple(v + 1 for v in edge), CLEAN, True)
            if step in (18, 36, 54, 72, 90):
                box(tuple(v - 3 for v in p), tuple(v + 3 for v in p), POWER, True)
                inner = radial(angle, radius - 5, y)
                box(tuple(v - 2 for v in inner), tuple(v + 2 for v in inner), LASER, True)
            last = p
        # 磁场端头与球面均有连续实体接触；两层约束束表示持续稳定作用。
        for y in (140, 172):
            t = math.asin((y - 35) / 183) * 2 / math.pi
            source = 112 - 96 * t ** 1.7
            surface = math.sqrt(BUBBLE_RADIUS ** 2 - (y - BUBBLE_CENTER[1]) ** 2)
            line(radial(angle, surface - 1, y), radial(angle, source, y), BLUE_GLASS, 1, True)
            end = radial(angle, source - 3, y)
            box(tuple(v - 4 for v in end), tuple(v + 4 for v in end), ATOMIC, True)


def heat_exchangers():
    # 前后两条独立介质回路环井布置，泵房与约束脚座之间用连续管路连接。
    for z0 in (83, 253):
        for x0 in (85, 236):
            box((x0, 36, z0), (x0 + 43, 40, z0 + 24), ICV)
            box((x0 + 3, 41, z0 + 3), (x0 + 40, 45, z0 + 21), INSULATE)
            box((x0 + 5, 46, z0 + 5), (x0 + 38, 65, z0 + 19), HEATPROOF)
            box((x0 + 8, 66, z0 + 7), (x0 + 35, 74, z0 + 17), TURBINE)
            box((x0 + 10, 75, z0 + 8), (x0 + 33, 75, z0 + 16), INTAKE)
            box((x0 + 1, 42, z0 + 1), (x0 + 7, 70, z0 + 23), FROST, True)
            box((x0 + 36, 42, z0 + 1), (x0 + 42, 70, z0 + 23), FROST, True)
            box((x0 + 15, 46, z0 + 8), (x0 + 27, 54, z0 + 16), SOLID, True)
            box((x0 + 12, 41, z0 + 7), (x0 + 31, 44, z0 + 17), VIBRATION, True)
            line((x0 + 5, 57, z0), (x0 + 5, 57, z0 + 28), STEEL_PIPE, 2, True)
            line((x0 + 38, 57, z0), (x0 + 38, 57, z0 + 28), STEEL_PIPE, 2, True)
    for k in range(6):
        angle = math.pi * k / 3
        line(radial(angle, 88, 49), radial(angle, 111, 49), TUNG_PIPE, 2, True)
        p = radial(angle, 99, 49)
        box((p[0] - 4, 38, p[2] - 4), (p[0] + 4, 48, p[2] + 4), LAFIUM, True)
        line(radial(angle, 100, 35), radial(angle, 100, 49), ICV, 2)
    # 缓冲罐分三层：实体设备内芯、双回路壳体、独立检修上盖。
    for x in (100, 264):
        for z in (164, 200):
            box((x - 10, 29, z - 10), (x + 10, 33, z + 10), ICV)
            box((x - 8, 34, z - 8), (x + 8, 55, z + 8), STABLE)
            box((x - 6, 56, z - 6), (x + 6, 59, z + 6), INERT)
            box((x - 9, 60, z - 9), (x + 9, 60, z + 9), GRATE)
            box((x - 3, 61, z - 3), (x + 3, 63, z + 3), LIGHT)


def bubble():
    r = BUBBLE_RADIUS
    for dy in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                rr = dx * dx + dy * dy + dz * dz
                if (r - 3) ** 2 <= rr <= r ** 2:
                    put(CX + dx, BUBBLE_CENTER[1] + dy, CZ + dz, BLACK_GLASS if abs(dy) <= 1 else BLACK, True)


def markers():
    control = [CX, 35, 12]
    ports = [
        dict(id='未稳定模拟载体输入', purpose='接收I29独立模拟批次及状态载体', pos=[158, 35, 12], face='north'),
        dict(id='模型与负载参数', purpose='接收对应批次的模型、研究许可及负载参数', pos=[206, 35, 12], face='north'),
        dict(id='西侧稳定介质输入', purpose='新鲜稳定介质与循环补充介质的候选入口', pos=[0, 35, 104], face='west'),
        dict(id='东侧稳定介质输入', purpose='镜像介质回路的候选入口', pos=[364, 35, 104], face='east'),
        dict(id='西侧持续供能', purpose='稳界磁场与模型运算的持续用能候选位', pos=[0, 35, 256], face='west'),
        dict(id='东侧持续供能', purpose='镜像稳界回路的持续用能候选位', pos=[364, 35, 256], face='east'),
        dict(id='可终止模拟载体输出', purpose='交给I31受控终止的模拟批次，不在本机结算随机资源', pos=[158, 35, 352], face='south'),
        dict(id='运行档案输出', purpose='输出独立模拟来源及运行状态档案，供研究与批次审计', pos=[206, 35, 352], face='south'),
        dict(id='废介质排出', purpose='用后稳定介质经独立流体出口交给既有再生工艺', pos=[134, 35, 352], face='south'),
        dict(id='热回流排出', purpose='稳定回路热流体经独立流体出口交给换热工艺', pos=[230, 35, 352], face='south'),
    ]
    for marker in [dict(pos=control, face='north', state=CONTROL)] + [dict(p, state=PORT) for p in ports]:
        x, y, z = marker['pos']
        if marker['face'] in ('north', 'south'):
            box((x - 2, y - 2, z), (x + 2, y + 2, z), ICV, True)
        else:
            box((x, y - 2, z - 2), (x, y + 2, z + 2), ICV, True)
        put(x, y, z, marker['state'], True)
    paths = [dict(name='正面主控与载体接入通廊', min=[148, 25, 0], max=[216, 43, 11]),
             dict(name='后侧批次与废介质交接通廊', min=[148, 25, 353], max=[216, 43, 364])]
    for path in paths:
        for y in range(path['min'][1], path['max'][1] + 1):
            for z in range(path['min'][2], path['max'][2] + 1):
                for x in range(path['min'][0], path['max'][0] + 1):
                    CELLS.pop((x, y, z), None)
    return control, ports, paths


def build():
    CELLS.clear()
    deep_well()
    service_districts()
    six_clamps()
    heat_exchangers()
    bubble()
    controller, ports, paths = markers()
    # 左半侧为唯一材质来源，中心列完整保留，消除圆弧离散化产生的左右偏差。
    for p in list(CELLS):
        if p[0] > CX:
            del CELLS[p]
    for (x, y, z), state in list(CELLS.items()):
        if x < CX:
            CELLS[(W - 1 - x, y, z)] = state
    return dict(key='i30', name=NAME, title=TITLE, size=[W, H, D], controller=controller, ports=ports, paths=paths,
                zones=[dict(name='六脊钳形约束设备', pos=[CX + 111, 42, CZ]),
                       dict(name='正球体模拟世界泡', pos=[CX, 140, CZ - 52]),
                       dict(name='井底托架与场发生器', pos=[CX, 78, CZ]),
                       dict(name='负载控制运算厅', pos=[125, 35, 38]),
                       dict(name='双回路稳定介质换热设备', pos=[90, 48, 88]),
                       dict(name='载体交接及废介质分流厅', pos=[125, 35, 326])],
                description='以六道从井基连续生长的钳形磁约束脊围护黑色正球体，稳定介质双回路、负载运算厅和载体交接设施围绕多层深井组织；承接I29批次，持续消耗介质与供能，输出供I31受控终止的批次、运行档案及废介质。',
                construction_notes={'orientation': '主控朝北/-Z；蓝图坐标从0起算。',
                                    'anchor': '本地[0,0,0]；推荐世界Y=-60，最高Y=162。',
                                    'boundary': '结构仅表达稳定工序；等待恢复、持久化状态、无复制和I31结算逻辑仍须另行实现验收。',
                                    'approval': '独立外观候选，未获负责人批准，不接入实例。'},
                blocks=[dict(pos=list(p), state=s) for p, s in sorted(CELLS.items(), key=lambda t: (t[0][1], t[0][2], t[0][0]))])


if __name__ == '__main__':
    from collections import Counter
    data = build()
    counts = Counter(block['state'] for block in data['blocks'])
    assert counts[CONTROL] == 1 and counts[ICV] == max(counts.values())
    assert len(CELLS) > 1779878 and len({s.split('[')[0] for s in counts}) > 37
    assert math.prod((W, H, D)) > 23281645 and H > 205
    assert all(CELLS.get((W - 1 - x, y, z)) == s for (x, y, z), s in CELLS.items())
    assert all(tuple(zone['pos']) in CELLS for zone in data['zones'])
    print(dict(blocks=len(CELLS), materials=len(counts), size_xyz=data['size'], icv=counts[ICV]), flush=True)
