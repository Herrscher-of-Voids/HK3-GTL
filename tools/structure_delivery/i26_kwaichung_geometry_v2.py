# -*- coding: utf-8 -*-
"""I26 葵涌自动化码头式无人采掘调度台几何。"""
from __future__ import annotations

W, H, D = 333, 211, 301
CX = W // 2

QAV = 'hk3gtl:voltage_machine_casing_qav'
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
BLUE_GLASS = 'minecraft:light_blue_stained_glass'
AMBER_GLASS = 'minecraft:orange_stained_glass'
LIGHT = 'minecraft:sea_lantern'
YELLOW = 'minecraft:yellow_concrete'
CONTAINER_COLORS = (
    'minecraft:blue_concrete', 'minecraft:light_gray_concrete',
    'minecraft:green_concrete', 'minecraft:yellow_concrete',
    'minecraft:orange_concrete', 'minecraft:red_concrete',
)

CELLS: dict[tuple[int, int, int], str] = {}


def put(x: int, y: int, z: int, state: str, replace: bool = False) -> None:
    pos = (x, y, z)
    if not (0 <= x < W and 0 <= y < H and 0 <= z < D):
        raise ValueError(f'码头构件越界：{pos} {state}')
    if replace or pos not in CELLS:
        CELLS[pos] = state


def box(lo, hi, state, replace: bool = False) -> None:
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                put(x, y, z, state, replace)


def beam(a, b, state, radius=0) -> None:
    steps = max(abs(b[i] - a[i]) for i in range(3))
    last = a
    for step in range(steps + 1):
        target = tuple(round(a[i] + (b[i] - a[i]) * step / max(1, steps)) for i in range(3))
        cursor = list(last)
        for axis in range(3):
            while cursor[axis] != target[axis]:
                cursor[axis] += 1 if target[axis] > cursor[axis] else -1
                box(tuple(v - radius for v in cursor), tuple(v + radius for v in cursor), state)
        box(tuple(v - radius for v in target), tuple(v + radius for v in target), state)
        last = target


def base_grid() -> None:
    # 稀疏箱形承台把泊位、堆场、岸桥与塔楼接成同一座港区。
    for x in range(0, W, 18):
        box((x, 0, 0), (min(x + 1, W - 1), 4, D - 1), QAV)
    for z in range(0, D, 18):
        box((0, 0, z), (W - 1, 4, min(z + 1, D - 1)), ROBUST)
    box((W - 2, 0, 0), (W - 1, 5, D - 1), QAV)
    box((0, 0, D - 2), (W - 1, 5, D - 1), QAV)
    for x in range(18, W - 1, 18):
        for z in range(18, D - 1, 18):
            box((x, 4, z), (x + 1, 12, z + 1), QAV)


def quay_and_dispatch_berth() -> None:
    # 岸線朝向港池，中央保留單一深空無人裝置的出港作業泊位。
    for x in range(W):
        for z in range(70, 108):
            if z in (70, 71, 106, 107) or x % 22 in (0, 1):
                box((x, 12, z), (x, 14, z), QAV if z % 3 else ROBUST)
            elif z % 11 in (0, 1):
                put(x, 12, z, GRATE)
    for z in (74, 78, 96, 102):
        for x in range(0, W, 9):
            box((x, 12, z), (min(x + 8, W - 1), 14, z + 1), ROBUST)
            box((x, 15, z), (min(x + 8, W - 1), 17, z + 1), POWER if z in (78, 96) else CLEAN)
    box((140, 12, 15), (192, 15, 69), QAV)
    for x in (144, 188):
        box((x, 16, 20), (x + 2, 20, 67), ROBUST)
        box((x - 2, 21, 57), (x + 4, 24, 69), GEAR)
    for z in range(24, 67, 8):
        box((148, 16, z), (184, 17, z + 2), ASSEMBLY if z % 16 else CLEAN)
    # 前端识别门架标识唯一任务航路，不模拟或替代世界泡实体。
    for x in (137, 193):
        foot_x = x - 3
        box((foot_x, 4, 10), (foot_x + 10, 14, 14), QAV)
        box((foot_x, 4, 14), (foot_x + 10, 5, 18), ROBUST)
        box((x, 15, 10), (x + 4, 53, 12), QAV)
        box((x - 3, 48, 10), (x + 7, 53, 12), ROBUST)
    box((137, 37, 11), (200, 38, 12), ROBUST)
    box((140, 49, 11), (194, 52, 12), LASER)
    box((163, 37, 11), (169, 41, 12), BLUE_GLASS)


def container_yard() -> None:
    # 12×18货箱间保留10格集卡巷道；箱色用于识别不同承运批次。
    for z in range(116, 275, 28):
        support_z = round((z - 1) / 18) * 18
        box((0, 12, z - 2), (W - 1, 12, z - 1), ROBUST)
        for x in range(0, W, 18):
            beam((x, 12, support_z), (x, 12, z - 1), QAV)
    for x in range(12, 322, 17):
        for z in range(116, 275, 28):
            if 124 <= x <= 208 and 116 <= z <= 172:
                continue
            box((x, 12, z), (x + 11, 12, z + 17), QAV)
            for level, y in enumerate((13, 22, 31)):
                box((x, y, z), (x + 11, y + 7, z + 17), QAV)
                for dx in (0, 11):
                    for dz in (0, 17):
                        box((x + dx, y, z + dz), (x + dx, y + 7, z + dz), ROBUST)
                variant = (x // 17 + z // 28 + level) % len(CONTAINER_COLORS)
                color = CONTAINER_COLORS[variant]
                box((x, y + 1, z + 2), (x, y + 6, z + 15), color, replace=True)
                box((x + 11, y + 1, z + 2), (x + 11, y + 6, z + 15), color, replace=True)
                box((x + 2, y + 1, z), (x + 9, y + 6, z), color, replace=True)
                box((x + 2, y + 1, z + 17), (x + 9, y + 6, z + 17), color, replace=True)
                box((x + 1, y + 7, z + 1), (x + 10, y + 7, z + 16), color, replace=True)
                # Corrugations, corner posts and paired door leaves keep each box legible.
                for rib_z in (5, 9, 13):
                    for rib_x in (x, x + 11):
                        box((rib_x, y + 1, z + rib_z), (rib_x, y + 6, z + rib_z), CLEAN, replace=True)
                for rib_z in (z + 5, z + 9, z + 13):
                    box((x + 1, y + 7, rib_z), (x + 10, y + 7, rib_z), CLEAN, replace=True)
                for rib_x in (4, 7):
                    box((x + rib_x, y + 1, z + 17), (x + rib_x, y + 6, z + 17), ROBUST, replace=True)
                box((x + 5, y + 2, z + 17), (x + 6, y + 5, z + 17), BLUE_GLASS, replace=True)
                for rib_x in (x + 2, x + 9):
                    box((rib_x, y + 1, z), (rib_x, y + 6, z), CLEAN, replace=True)
                if (x + z + level) % 4 == 0:
                    box((x + 2, y + 7, z + 3), (x + 9, y + 7, z + 14), GRATE, replace=True)
            for y in (21, 30):
                box((x, y, z), (x + 11, y, z + 17), QAV)
    for z in (114, 141, 169, 197, 225, 253, 281):
        for x in range(10, W - 8, 18):
            box((x, 12, z), (x + 8, 13, z + 1), ROBUST)
            box((x + 1, 14, z), (x + 7, 15, z), LIGHT if z in (114, 281) else CLEAN)
    for lane_start in (134, 162, 190, 218, 246):
        box((0, 12, lane_start), (W - 1, 12, lane_start + 6), ROBUST)


def yard_gantry(x0: int, x1: int, row_start: int) -> None:
    """一座跨箱列场桥：支腿落在箱区巷道，吊具悬在箱垛顶面。"""
    z0, z1 = row_start - 4, row_start + 21
    center_x, center_z = (x0 + x1) // 2, (z0 + z1) // 2
    for x in (x0, x1 - 2):
        for z in (z0, z1 - 2):
            box((x, 13, z), (x + 2, 47, z + 2), QAV)
            box((max(0, x - 2), 14, max(0, z - 2)),
                (min(W - 1, x + 4), 16, min(D - 1, z + 4)), GEAR)
            for y in (22, 34, 44):
                box((x - 1, y, z - 1), (x + 3, y + 1, z + 3), ROBUST)
    for z in (z0, z1):
        beam((x0, 46, z), (x1, 46, z), ROBUST, 1)
        beam((x0, 43, z), (x1, 43, z), QAV)
    for x in (x0, x1):
        beam((x, 43, z0), (x, 43, z1), QAV)
    box((center_x - 5, 42, center_z - 4), (center_x + 5, 46, center_z + 4), ASSEMBLY)
    box((center_x - 2, 38, center_z), (center_x + 2, 41, center_z), TUNG_PIPE)
    box((center_x - 3, 37, center_z - 2), (center_x + 3, 38, center_z + 2), GEAR)


def yard_gantry_cranes() -> None:
    # 三段箱区按行配置场桥；中央两行避开航务塔的承重投影。
    spans = ((11, 109), (126, 207), (228, 331))
    for row_start in (116, 172, 228):
        for index, (x0, x1) in enumerate(spans):
            if row_start < 200 and index == 1:
                continue
            yard_gantry(x0, x1, row_start)


def terminal_tractor(x0: int, z0: int) -> None:
    """無人集卡牽引頭停在箱列間的交叉巷道。"""
    if any((x, y, z) in CELLS for x in range(x0, x0 + 5)
           for y in range(13, 20) for z in range(z0, z0 + 7)):
        raise ValueError(f'集卡通道被其他構件佔用：x={x0}, z={z0}')
    box((x0 + 1, 14, z0), (x0 + 3, 15, z0 + 6), YELLOW)
    for x in (x0, x0 + 3):
        for z in (z0 + 1, z0 + 5):
            box((x, 13, z), (x + 1, 15, z + 1), GEAR)
    box((x0 + 1, 16, z0 + 3), (x0 + 3, 18, z0 + 6), QAV)
    box((x0 + 1, 17, z0 + 6), (x0 + 3, 18, z0 + 6), BLUE_GLASS, replace=True)
    box((x0 + 1, 19, z0 + 4), (x0 + 3, 19, z0 + 5), CLEAN)
    box((x0 + 1, 16, z0), (x0 + 3, 16, z0 + 2), YELLOW)
    box((x0 + 2, 15, z0 + 2), (x0 + 2, 16, z0 + 3), GEAR)
    for x in (x0 + 1, x0 + 3):
        box((x, 16, z0 + 4), (x, 17, z0 + 5), BLUE_GLASS, replace=True)


def terminal_tractor_fleet() -> None:
    # 牽引頭依次停靠交叉巷道，輪距與車身不侵入箱體。
    for x, z in zip((24, 58, 75, 92, 245, 262), (134, 134, 162, 190, 218, 246)):
        terminal_tractor(x, z)


def warehouse(x0: int, x1: int) -> None:
    """低矮裝卸倉庫：框架、連續屋面、採光帶和三個貨門。"""
    z0, z1 = 279, 298
    for y in range(14, 34):
        for z in (z0, z1):
            for x in range(x0, x1 + 1):
                if 21 <= y <= 29 and x not in (x0, x1) and x % 18 not in (0, 1):
                    put(x, y, z, GLASS if x % 5 else BLUE_GLASS)
                else:
                    put(x, y, z, QAV if x in (x0, x1) or y in (14, 33) or x % 18 in (0, 1) else CLEAN)
        for x in (x0, x1):
            for z in range(z0 + 1, z1):
                put(x, y, z, ROBUST if y % 7 in (0, 1) else CLEAN)
    box((x0, 33, z0), (x1, 33, z1), CLEAN)
    for x in range(x0, x1 + 1, 8):
        box((x, 33, z0), (min(x + 1, x1), 36, z1), QAV)
        box((x + 2, 35, z0 + 1), (min(x + 5, x1 - 1), 35, z1 - 1), GRATE)
    for x in range(x0 + 5, x1 - 4, 24):
        box((x, 34, z0 + 2), (x + 2, 34, z1 - 2), BLUE_GLASS)
    for door_x in range(x0 + 14, x1 - 10, 28):
        for x in (door_x, door_x + 11):
            box((x, 15, z0), (x + 1, 30, z0 + 1), ROBUST)
        box((door_x, 29, z0), (door_x + 12, 31, z0 + 1), ASSEMBLY)
        box((door_x + 2, 16, z0), (door_x + 9, 28, z0), LIGHT, replace=True)
        box((door_x + 5, 16, z0), (door_x + 6, 28, z0), CLEAN, replace=True)
        box((door_x - 2, 13, z0 - 1), (door_x + 13, 14, z0 + 2), ROBUST)


def logistics_warehouses() -> None:
    warehouse(12, 103)
    warehouse(230, 321)


def ship_to_shore_crane(center_x: int) -> None:
    # 岸橋以海側長臂、岸側配重和成對高腿形成標準門式側影。
    x0, x1 = center_x - 9, center_x + 9
    for x in (x0, x1):
        for z in (77, 105):
            box((x, 12, z), (x + 2, 14, z + 2), ROBUST)
            box((x, 15, z), (x + 2, 106, z + 2), QAV)
            for y in range(26, 100, 18):
                box((x - 2, y, z - 2), (x + 4, y + 2, z + 4), ROBUST)
    for y, state in ((94, ROBUST), (100, QAV), (106, ROBUST)):
        beam((x0, y, 78), (x1, y, 106), state, 1 if y == 100 else 0)
    # 海側懸臂與雙導軌越過泊位；岸側短臂承托齒輪配重組。
    for x in (x0, x1):
        beam((x, 102, 78), (x, 102, 13), QAV, 1)
        beam((x, 102, 106), (x, 102, 128), ROBUST)
        for z in (21, 39, 57):
            box((x - 2, 100, z), (x + 3, 104, z + 2), POWER)
    box((center_x - 5, 94, 70), (center_x + 5, 101, 78), ASSEMBLY)
    box((center_x - 2, 71, 73), (center_x + 2, 93, 75), TUNG_PIPE)
    for z in (17, 45, 73, 101, 124):
        box((x0 - 2, 107, z), (x1 + 3, 109, z + 1), LASER if z == 73 else CLEAN)
        if z < 78:
            beam((x0, 106, z), (x0, 106, 78), QAV)
        else:
            beam((x1, 106, z), (x1, 106, 106), ROBUST)
    for x in (x0 - 3, x1 + 4):
        box((x, 15, 74), (x, 23, 108), GEAR)


def four_quay_cranes() -> None:
    # 岸橋按泊位節距成列，視覺上服務同一條中心出港航路。
    for center_x in (39, 124, 209, 294):
        ship_to_shore_crane(center_x)


def dispatch_control_tower() -> None:
    # 低位航務樓、玻璃觀測層與細長座標中继塔是一體承力結構。
    x0, x1, z0, z1 = 126, 206, 111, 174
    for y in range(13, 70):
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                if y % 13 in (0, 1):
                    put(x, y, z, ROBUST)
                elif x in (x0, x1) or x % 8 in (0, 1):
                    put(x, y, z, QAV)
                elif 24 <= y <= 58:
                    put(x, y, z, BLUE_GLASS)
            if x in (x0, x1):
                for z in range(z0 + 1, z1):
                    if y % 13 in (0, 1):
                        put(x, y, z, QAV)
                    elif y % 19 in range(7, 15):
                        put(x, y, z, BLUE_GLASS if z % 9 not in (0, 1) else GLASS)
                    elif z % 8 in (0, 1):
                        put(x, y, z, ROBUST)
    for y in (13, 27, 41, 55, 69):
        box((x0, y, z0), (x1, y + 1, z1), QAV)
        for x in range(x0 + 8, x1 - 5, 16):
            box((x, y + 2, z0 + 8), (x + 5, y + 5, z1 - 8), COMPUTER if y < 42 else MULTI)
    # 突出的观测舱包住塔身，不是独立外挂面板。
    box((139, 69, 119), (193, 71, 166), ROBUST)
    for y in range(72, 88):
        for x in range(139, 194):
            for z in (119, 166):
                if y in (72, 87) or x % 9 in (0, 1):
                    put(x, y, z, QAV if y in (72, 87) else CLEAN)
                else:
                    put(x, y, z, GLASS if x % 4 else BLUE_GLASS)
        for z in (119, 166):
            for x in (139, 193):
                put(x, y, z, ROBUST)
    for x in (139, 193):
        for z in (119, 166):
            box((x, 72, z), (x + 1, 88, z + 1), QAV)
    box((CX - 4, 72, 120), (CX + 4, 80, 123), COMPUTER)
    for y in (88, 95, 104, 113, 122, 131, 140, 149, 158, 167, 176, 185, 194, 203, 210):
        width = max(1, 12 - max(0, y - 130) // 10)
        box((CX - width, y, 137 - width), (CX + width, y, 158 + width), QAV)
    for x in (CX - 11, CX - 6, CX + 5, CX + 10):
        beam((x, 88, 137), (CX + (x - CX) // 2, 210, 147), ROBUST)
    for z in (139, 156):
        for x in (CX - 9, CX + 8):
            beam((x, 88, z), (x, 210, 148 + (z - 147)), QAV)
    for y in range(96, 204, 18):
        box((CX - 7, y, 140), (CX + 7, y + 1, 155), COMPUTER if y % 36 else DIMENSION)
    for y in (101, 119, 137, 155, 173, 191, 209):
        box((CX - 2, y, 146), (CX + 2, min(y + 2, H - 1), 146), LIGHT if y in (101, 209) else AMBER_GLASS)


def transfer_and_gate() -> None:
    # 堆場場橋、主物流脊、安檢閘口把貨櫃流接回單目標泊位。
    for z in (114, 171, 228, 281):
        beam((9, 18, z), (324, 18, z), QAV, 1)
        beam((9, 24, z), (324, 24, z), ROBUST)
        for x in range(14, 322, 18):
            box((x, 15, z - 2), (x + 1, 25, z + 2), GEAR)
    for x in (108, 219):
        for z in range(112, 285, 18):
            box((x, 12, z), (x + 2, 23, z + 7), QAV)
            box((x - 1, 24, z), (x + 3, 25, z + 7), GRATE)
    for x in (138, 194):
        box((x - 4, 12, 283), (x + 8, 13, 289), ROBUST)
        box((x, 14, 286), (x + 4, 48, 288), QAV)
        box((x - 3, 45, 286), (x + 7, 49, 288), ROBUST)
    box((138, 28, 285), (201, 28, 288), ROBUST)
    box((138, 45, 286), (201, 48, 288), LASER)
    for x in range(144, 194, 8):
        box((x, 29, 285), (x + 3, 35, 286), LIGHT if x % 16 else FILTER)


def service_blocks() -> None:
    # 檢疫、能源與耗材站嵌在堆場端部，保留不同工藝材料但不形成孤立柱體。
    stations = (
        (16, 48, 282, 297, FILTER), (66, 98, 282, 297, PROCESS),
        (234, 266, 282, 297, IRIDIUM), (284, 316, 282, 297, ATOMIC),
    )
    for x0, x1, z0, z1, equipment in stations:
        for y in range(13, 34):
            for x in range(x0, x1 + 1):
                for z in (z0, z1):
                    if y in (13, 33):
                        put(x, y, z, QAV)
                    elif x % 8 in (0, 1):
                        put(x, y, z, ROBUST)
                    elif 18 <= y <= 28 and z == z0:
                        put(x, y, z, BLUE_GLASS)
            for x in (x0, x1):
                for z in range(z0 + 1, z1):
                    put(x, y, z, QAV if y % 7 in (0, 1) else equipment)
        box((x0, 12, z0), (x1, 12, z1), ROBUST)
        for x in range(x0 + 4, x1 - 2, 8):
            box((x, 13, z0 + 4), (x + 3, 25, z1 - 4), equipment)
            box((x - 1, 26, z0 + 3), (x + 4, 27, z1 - 3), VENT)
    for x in range(24, 310, 18):
        box((x, 13, 108), (x + 4, 17, 111), TUNG_PIPE)
        box((x + 1, 18, 108), (x + 3, 21, 111), STEEL_PIPE)
    for x in (0, W - 3):
        box((x, 5, 126), (x + 2, 43, 258), QAV)
        for y in (15, 22, 29, 36):
            box((x, y, 128), (x + 2, y + 2, 256), ROBUST if y in (15, 36) else PROCESS)
    box((128, 5, D - 3), (204, 43, D - 1), QAV)
    for x in range(132, 202, 10):
        box((x, 16, D - 3), (x + 2, 32, D - 1), ROBUST if x % 20 else FILTER)
    box((122, 13, 106), (210, 15, 108), POWER)
    box((122, 16, 106), (210, 18, 108), INERT)
    box((123, 19, 106), (209, 20, 108), HEATPROOF)
    for z in (110, 173, 282):
        for x in (120, 212):
            box((x, 13, z), (x + 2, 41, z + 2), LAFIUM)
            box((x - 2, 28, z - 2), (x + 4, 30, z + 4), MACERATOR)
    for x in (118, 214):
        for y in (15, 22, 29, 36):
            box((x, y, 173), (x + 1, y + 3, 282), TURBINE)
    for x in range(129, 204, 12):
        for z in (108, 175):
            box((x, 12, z), (x + 4, 16, z + 2), DIMENSION)
            box((x + 1, 17, z), (x + 3, 23, z + 1), INERT)


def add_markers(data: dict) -> None:
    data['controller'] = [CX, 76, 119]
    data['ports'] = [
        {'id': '无人采掘装置与耗材输入', 'purpose': '西侧维护站接收装置和耗材', 'pos': [0, 25, 144], 'face': 'west'},
        {'id': '冷却介质输入', 'purpose': '西侧泊位设备冷却回路', 'pos': [0, 34, 184], 'face': 'west'},
        {'id': 'I25坐标与I44授权记录输入', 'purpose': '后部调度塔接入坐标和锁定记录', 'pos': [148, 29, 300], 'face': 'south'},
        {'id': '供能输入', 'purpose': '后部高压母线接口；额定EU待工艺核验', 'pos': [184, 29, 300], 'face': 'south'},
        {'id': '采掘物品与磨损件输出', 'purpose': '东侧返航分拣线输出', 'pos': [332, 24, 144], 'face': 'east'},
        {'id': '流体输出', 'purpose': '东侧封存管路输出', 'pos': [332, 31, 184], 'face': 'east'},
        {'id': '遗留技术档案输出', 'purpose': '东侧检疫舱档案出口', 'pos': [332, 28, 248], 'face': 'east'},
    ]
    dirs = {'west': (-1, 0, 0), 'east': (1, 0, 0), 'south': (0, 0, 1)}
    for port in data['ports']:
        dx, dy, dz = dirs[port['face']]
        x, y, z = port['pos']
        put(x - dx, y - dy, z - dz, QAV, replace=True)
        put(x, y, z, PORT, replace=True)
    put(*data['controller'], CONTROL, replace=True)


def build() -> dict:
    CELLS.clear()
    base_grid()
    quay_and_dispatch_berth()
    container_yard()
    four_quay_cranes()
    yard_gantry_cranes()
    terminal_tractor_fleet()
    dispatch_control_tower()
    transfer_and_gate()
    service_blocks()
    logistics_warehouses()
    data = {
        'key': 'I26', 'id': 'I26', 'name': 'hk3gtl-i26-kwaichung-automated-terminal-v2-20261026',
        'title': '世界泡无人采掘调度台 · 葵涌自动化码头', 'candidate_version': 'V2',
        'size': [W, H, D], 'controller': [], 'ports': [], 'blocks': [],
        'paths': [
            {'min': [140, 12, 18], 'max': [192, 26, 69]},
            {'min': [10, 12, 110], 'max': [322, 22, 113]},
        ],
        'zones': [
            {'name': '单目标出港泊位', 'pos': [166, 22, 49]},
            {'name': '岸桥装卸线', 'pos': [209, 74, 88]},
            {'name': '自动化集装箱堆场', 'pos': [274, 28, 215]},
            {'name': '箱场龙门架', 'pos': [274, 48, 215]},
            {'name': '无人集卡拖头通道', 'pos': [58, 20, 138]},
            {'name': '陆侧双仓装卸区', 'pos': [56, 37, 289]},
            {'name': '航务调度与坐标中继塔', 'pos': [166, 112, 148]},
            {'name': '检疫分拣与外部闸口', 'pos': [294, 20, 288]},
        ],
        'description': '单目标无人采掘港区：装置由中央泊位出港；多色货柜、岸桥、场桥、无人牵引车与后方装卸仓库沿单向物流脊汇入调度塔。',
    }
    add_markers(data)
    data['blocks'] = [
        {'pos': list(pos), 'state': state}
        for pos, state in sorted(CELLS.items(), key=lambda item: (item[0][1], item[0][2], item[0][0]))
    ]
    data['zone_descriptions'] = [
        {'name': '单目标出港泊位', 'description': '仅一条中央装置通道穿过海侧识别门架，不以多条岸桥暗示多目标并行。'},
        {'name': '岸桥装卸线', 'description': '四座成列的岸桥共享同一条深空作业泊位，吊具、配重和高位导轨形成连续港口轮廓。'},
        {'name': '自动化集装箱堆场', 'description': '蓝、灰、绿、黄、橙、红六色货柜区分承运批次；箱门、角柱、加强筋与箱顶标识组成可读箱型。'},
        {'name': '箱场龙门架', 'description': '七座跨箱列场桥分布在三段堆场，支腿避开集卡巷道，吊具对准箱垛。'},
        {'name': '无人集卡拖头通道', 'description': '六辆黄色牵引头沿箱列间五条连续转运车道行驶，车体净空经过生成器检查。'},
        {'name': '陆侧双仓装卸区', 'description': '两座封闭装卸仓库包含连续承重屋面、采光带、侧墙和多个货门，包入检疫与分拣设备。'},
        {'name': '航务调度与坐标中继塔', 'description': '居中钻石主控嵌入观测楼前脸；上部细塔承载长距坐标中继，不另设突兀接口面板。'},
        {'name': '检疫分拣与外部闸口', 'description': '两座装卸仓库包覆分拣、检疫与能源设备；物品、流体、磨损设备和遗留技术档案分线后由单向闸口汇出。'},
    ]
    return data
