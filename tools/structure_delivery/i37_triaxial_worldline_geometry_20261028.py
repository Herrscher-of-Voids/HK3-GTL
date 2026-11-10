# -*- coding: utf-8 -*-
"""I37三轴世界线干涉测量台的独立新构型。"""
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
W, H, D, C = 529, 285, 529, 264
NAME = 'hk3gtl-i37-triaxial-worldline-range'
TITLE = '世界维系试验平台 · 三轴世界线干涉测量台'


class Material:
    WFV = 'hk3gtl:voltage_machine_casing_wfv'
    PORT = 'hk3gtl:industrial_port_casing'
    CONTROL = 'minecraft:diamond_block'
    ROBUST = 'gtceu:robust_machine_casing'
    SOLID = 'gtceu:solid_machine_casing'
    STEEL = 'gtceu:steel_machine_casing'
    POWER = 'gtceu:high_power_casing'
    STRESS = 'gtceu:stress_proof_casing'
    SST_TURBINE = 'gtceu:stainless_steel_turbine_casing'
    STEEL_TURBINE = 'gtceu:steel_turbine_casing'
    HOT = 'gtceu:high_temperature_smelting_casing'
    WATERTIGHT = 'gtceu:watertight_casing'
    NONCONDUCTING = 'gtceu:nonconducting_casing'
    GEARBOX = 'gtceu:steel_gearbox'
    VIBRATION = 'gtceu:vibration_safe_casing'
    STABLE = 'gtceu:stable_machine_casing'
    CLEAN = 'gtceu:clean_machine_casing'
    ADVANCED_COMPUTER = 'gtceu:advanced_computer_casing'
    COMPUTER = 'gtceu:computer_casing'
    ASSEMBLY = 'gtceu:assembly_line_casing'
    FILTER = 'gtceu:filter_casing'
    LASER = 'gtceu:laser_safe_engraving_casing'
    TEMPERED_GLASS = 'gtceu:tempered_glass'
    CLEAN_GLASS = 'gtceu:cleanroom_glass'
    FUSION_GLASS = 'gtceu:fusion_glass'
    LAMINATED_GLASS = 'gtceu:laminated_glass'
    TINTED_GLASS = 'minecraft:tinted_glass'
    BLUE_GLASS = 'minecraft:light_blue_stained_glass'
    CALCITE = 'minecraft:calcite'
    QUARTZ = 'minecraft:smooth_quartz'
    DEEPSLATE = 'minecraft:polished_deepslate'
    BLACKSTONE = 'minecraft:polished_blackstone'
    DEEPSLATE_TILES = 'minecraft:deepslate_tiles'
    DEEPSLATE_BRICKS = 'minecraft:deepslate_bricks'
    ANDESITE = 'minecraft:polished_andesite'
    ROUGH_ANDESITE = 'minecraft:andesite'
    QUARTZ_BRICKS = 'minecraft:quartz_bricks'
    LIGHT_GRAY = 'minecraft:light_gray_concrete'
    GRAY = 'minecraft:gray_concrete'
    WHITE = 'minecraft:white_concrete'
    BLACK = 'minecraft:black_concrete'
    WARNING = 'minecraft:yellow_terracotta'
    IRON = 'minecraft:iron_block'
    COPPER = 'minecraft:copper_block'
    CHISELED_QUARTZ = 'minecraft:chiseled_quartz_block'


M = Material()
STATES = [
    M.WFV, M.ROBUST, M.SOLID, M.STEEL, M.POWER, M.STRESS, M.SST_TURBINE,
    M.STEEL_TURBINE, M.HOT, M.WATERTIGHT, M.NONCONDUCTING, M.GEARBOX,
    M.VIBRATION, M.STABLE, M.CLEAN, M.ADVANCED_COMPUTER, M.COMPUTER,
    M.ASSEMBLY, M.FILTER, M.LASER, M.TEMPERED_GLASS, M.CLEAN_GLASS,
    M.FUSION_GLASS, M.LAMINATED_GLASS, M.TINTED_GLASS, M.BLUE_GLASS,
    M.CALCITE, M.QUARTZ, M.DEEPSLATE, M.BLACKSTONE, M.DEEPSLATE_TILES,
    M.DEEPSLATE_BRICKS, M.ANDESITE, M.ROUGH_ANDESITE, M.QUARTZ_BRICKS,
    M.LIGHT_GRAY, M.GRAY, M.WHITE, M.BLACK,
    M.WARNING, M.IRON, M.COPPER, M.CHISELED_QUARTZ, M.PORT, M.CONTROL,
]
IDS = {state: index + 1 for index, state in enumerate(STATES)}

ROLES = {
    M.WFV: '整机三轴基线梁、核心测量框与可识别主壳',
    M.ROBUST: '承力轨床和三轴框架的主节点',
    M.SOLID: '基座内部的抗弯压实心梁',
    M.STEEL: '分段检修梁和测量滑台底板',
    M.POWER: '中心差分测量头与高能隔离节点',
    M.STRESS: '基线端部锚固座和应力传递接头',
    M.SST_TURBINE: '纵横基线的侧向承力护梁',
    M.STEEL_TURBINE: '高架测量框的弯矩梁',
    M.HOT: '扰动试件的热隔离夹套',
    M.WATERTIGHT: '稳定介质回收槽的密闭外壳',
    M.NONCONDUCTING: '基线绝缘支座和隔离垫',
    M.GEARBOX: '三轴端部的低速微调驱动盒',
    M.VIBRATION: '中央零点台的隔振层',
    M.STABLE: '参考态试件的隔振托座',
    M.CLEAN: '试件装载与洁净维护节点',
    M.ADVANCED_COMPUTER: '中心测量头的信号采集外壳',
    M.COMPUTER: '状态记录与校准单元外壳',
    M.ASSEMBLY: '滑台和十字标尺的连接件',
    M.FILTER: '输入隔离与介质过滤组件外壳',
    M.LASER: '光学标定刻线与读数窗座',
    M.TEMPERED_GLASS: '基线端部的耐冲击观察窗',
    M.CLEAN_GLASS: '装载区维护观察窗',
    M.FUSION_GLASS: '中心差分头的耐高能读数窗',
    M.LAMINATED_GLASS: '纵向观测槽的夹层窗',
    M.TINTED_GLASS: '相位零点遮光窗口',
    M.BLUE_GLASS: '少量参考信号状态窗',
    M.CALCITE: '陶瓷绝缘与低热传导衬座',
    M.QUARTZ: '精密滑台面与校准平台',
    M.DEEPSLATE: '低位隔振地梁',
    M.BLACKSTONE: '吸振和遮光内衬',
    M.DEEPSLATE_TILES: '轨床耐磨检修面',
    M.DEEPSLATE_BRICKS: '端部锚固台的抗压包边',
    M.ANDESITE: '测量桥栈道面',
    M.ROUGH_ANDESITE: '三轴端部的粗面检修踏台',
    M.QUARTZ_BRICKS: '零位台周边的精密校准垫层',
    M.LIGHT_GRAY: '读数标尺底色',
    M.GRAY: '设备分区和检修板',
    M.WHITE: '校准刻度和光学标尺',
    M.BLACK: '遮光背板',
    M.WARNING: '端部检修危险区的少量警示色',
    M.IRON: '滑台限位块和校准垫片',
    M.COPPER: '低温测量导体与接地排',
    M.CHISELED_QUARTZ: '控制梁和中轴零位基准块',
    M.PORT: '正式Pattern接口候选位置标记，不具备仓室能力',
    M.CONTROL: '正式控制器候选中心定位标记',
}


def _build_grid_dense_panel_layout():
    """构建开敞正交三轴床身；所有层、构件和点缀均关于X=264镜像。"""
    grid = np.zeros((H, D, W), dtype=np.uint8)

    def box(x0, x1, y0, y1, z0, z1, state):
        if not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H and 0 <= z0 < z1 <= D):
            raise ValueError(('坐标越界', (x0, x1, y0, y1, z0, z1), state))
        grid[y0:y1, z0:z1, x0:x1] = IDS[state]

    def t_deck(y0, y1, half, state):
        box(C-half, C+half+1, y0, y1, 0, D, state)
        box(0, W, y0, y1, C-half, C+half+1, state)

    def paired_longitudinal(half, thickness, y0, y1, state):
        box(C-half, C-half+thickness, y0, y1, 0, D, state)
        box(C+half-thickness+1, C+half+1, y0, y1, 0, D, state)

    def paired_transverse(half, thickness, y0, y1, state):
        box(0, W, y0, y1, C-half, C-half+thickness, state)
        box(0, W, y0, y1, C+half-thickness+1, C+half+1, state)

    # 三轴连续基座：纵向基线与横向参考/扰动基线正交相交，不铺方形大底板。
    t_deck(0, 8, 60, M.WFV)
    t_deck(8, 12, 56, M.DEEPSLATE)
    t_deck(12, 15, 52, M.ROBUST)
    t_deck(15, 18, 48, M.DEEPSLATE_TILES)
    box(0, W, 18, 20, C-44, C+45, M.QUARTZ_BRICKS)
    box(C-44, C+45, 18, 20, 0, D, M.QUARTZ_BRICKS)

    # 四条高深度箱梁组成开敞测量桥，宽度和层位按三轴工况逐级收束。
    paired_longitudinal(64, 10, 26, 274, M.WFV)
    paired_transverse(64, 10, 26, 274, M.WFV)
    paired_longitudinal(54, 6, 34, 250, M.ROBUST)
    paired_transverse(54, 6, 34, 250, M.ROBUST)
    paired_longitudinal(44, 5, 46, 230, M.SOLID)
    paired_transverse(44, 5, 46, 230, M.SOLID)

    # 跨层轨床是工作台而非整层楼板：每层逐步缩窄，让纵横基线保持可辨。
    decks = [
        (34, 37, 54, M.STEEL), (58, 61, 52, M.WFV),
        (82, 85, 48, M.STEEL_TURBINE), (106, 109, 44, M.WFV),
        (130, 133, 40, M.SST_TURBINE), (154, 157, 36, M.WFV),
        (178, 181, 32, M.HOT), (202, 205, 28, M.WFV),
        (226, 229, 24, M.QUARTZ), (250, 253, 20, M.WFV),
    ]
    for y0, y1, half, state in decks:
        t_deck(y0, y1, half, state)

    # 端站是嵌在床身中的设备岛，不另立四座塔。
    for x0, x1 in ((0, 96), (433, 529)):
        box(x0, x1, 26, 62, C-46, C+47, M.STRESS)
        box(x0+8, x1-8, 62, 92, C-38, C+39, M.POWER)
        box(x0+16, x1-16, 92, 116, C-30, C+31, M.GEARBOX)
        box(x0+24, x1-24, 116, 128, C-22, C+23, M.ADVANCED_COMPUTER)
    for z0, z1 in ((0, 96), (433, 529)):
        box(C-46, C+47, 26, 58, z0, z1, M.STRESS)
        box(C-38, C+39, 58, 90, z0+8, z1-8, M.FILTER)
        box(C-30, C+31, 90, 114, z0+16, z1-16, M.GEARBOX)
        box(C-22, C+23, 114, 126, z0+24, z1-24, M.COMPUTER)

    # 端站维护栈道与液压/低速调节支座，将设备岛直接接回主轨床。
    for sx in (0, W-72):
        box(sx, sx+72, 18, 26, C-50, C+51, M.ROUGH_ANDESITE)
        box(sx+8, sx+64, 26, 34, C-42, C+43, M.IRON)
    for sz in (0, D-72):
        box(C-50, C+51, 18, 26, sz, sz+72, M.ROUGH_ANDESITE)
        box(C-42, C+43, 26, 34, sz+8, sz+64, M.IRON)

    # 中央零位井用三组正交计量梁定姿；中央试件保持小而可见，不伪装成世界泡。
    t_deck(255, 263, 22, M.VIBRATION)
    box(C-42, C+43, 263, 271, C-42, C+43, M.NONCONDUCTING)
    box(C-30, C+31, 271, 277, C-30, C+31, M.LASER)
    box(C-12, C+13, 277, 284, C-12, C+13, M.TINTED_GLASS)
    box(C-4, C+5, 284, 285, C-4, C+5, M.FUSION_GLASS)

    # 三轴十字标尺与栈道顶梁由床身支撑，最高点由相连的正交横梁定义。
    paired_longitudinal(20, 8, 255, 285, M.ASSEMBLY)
    paired_transverse(20, 8, 255, 285, M.ASSEMBLY)
    t_deck(270, 276, 28, M.STEEL_TURBINE)
    paired_longitudinal(34, 6, 276, 284, M.WFV)
    paired_transverse(34, 6, 276, 284, M.WFV)
    t_deck(284, 285, 16, M.CHISELED_QUARTZ)

    # 中央信号采集与参考试件承台全部落在交叉基线，不在外侧追加独立立柱。
    for x_offset, z_offset in ((-32, -32), (33, 32)):
        x0 = C + x_offset - 8
        z0 = C - 8
        box(x0, x0+16, 26, 250, z0, z0+16, M.WFV)
        box(C-8, C+9, 26, 250, C+z_offset-8, C+z_offset+9, M.WFV)
    box(C-28, C+29, 63, 92, C-28, C+29, M.NONCONDUCTING)
    box(C-22, C+23, 92, 121, C-22, C+23, M.VIBRATION)
    box(C-15, C+16, 121, 150, C-15, C+16, M.STABLE)
    box(C-9, C+10, 150, 179, C-9, C+10, M.CLEAN)
    box(C-5, C+6, 179, 190, C-5, C+6, M.LIGHT_GRAY)

    # 观察窗嵌入梁腹板，玻璃仅用于读数、隔离和维护观察。
    window_states = [M.TEMPERED_GLASS, M.CLEAN_GLASS, M.FUSION_GLASS,
                     M.LAMINATED_GLASS, M.BLUE_GLASS]
    for index, state in enumerate(window_states):
        z0 = 40 + index * 88
        y0 = 72 + (index % 2) * 48
        for x0 in (C-64, C+55):
            box(x0, x0+10, y0, y0+18, z0, z0+26, state)
        x0 = 40 + index * 88
        for mirrored_x in (x0, W-x0-26):
            for z0 in (C-64, C+55):
                box(mirrored_x, mirrored_x+26, y0, y0+18, z0, z0+10, state)

    # 仪器节点按基线角色排布；节点间留出视线、吊装和检修空隙。
    instrument_states = [M.ADVANCED_COMPUTER, M.COMPUTER, M.ASSEMBLY,
                        M.FILTER, M.LASER, M.CALCITE, M.COPPER, M.WARNING]
    for index, state in enumerate(instrument_states):
        z = 44 + index * 60
        y = 40 + (index % 3) * 40
        x0 = C-42 if index % 2 == 0 else C+30
        for mirrored_x in (x0, W-x0-12):
            box(mirrored_x, mirrored_x+12, y, y+12, z, z+18, state)
        box(0, 12, y, y+12, C-38, C+39, state)
        box(W-12, W, y, y+12, C-38, C+39, state)

    # 绝缘、检修與承力细节沿三轴工作面分布，避免整机变成单材质色块。
    rail_states = [M.STEEL, M.SST_TURBINE, M.STEEL_TURBINE, M.HOT,
                   M.WATERTIGHT, M.NONCONDUCTING, M.SOLID, M.STRESS,
                   M.CALCITE, M.QUARTZ, M.DEEPSLATE, M.BLACKSTONE,
                   M.DEEPSLATE_TILES, M.DEEPSLATE_BRICKS, M.ANDESITE,
                   M.ROUGH_ANDESITE, M.QUARTZ_BRICKS,
                   M.LIGHT_GRAY, M.GRAY, M.WHITE, M.BLACK, M.IRON,
                   M.COPPER, M.CHISELED_QUARTZ]
    for index, state in enumerate(rail_states):
        z = 34 + (index % 13) * 37
        y = 28 + (index % 7) * 32
        width = 3 + index % 3
        # 每块饰面都是轨床检修盖、绝缘垫、刻度盘或框架接头的一部分。
        for x0 in (C-58, W-(C-58)-width):
            box(x0, x0+width, y, y+4, z, z+12, state)
        x0 = 34 + (index % 13) * 37
        for mirrored_x in (x0, W-x0-12):
            for z0 in (C-58, C+55-width):
                box(mirrored_x, mirrored_x+12, y, y+4, z0, z0+width, state)

    # 统一标尺、相位窗和危险边界：低饱和、限量点缀。
    for z in range(34, C-34, 16):
        box(C-3, C+4, 17, 19, z, z+2, M.WHITE)
        box(C-2, C+3, 19, 20, z, z+1, M.COPPER)
        mirrored_z = D - z - 2
        box(C-3, C+4, 17, 19, mirrored_z, mirrored_z+2, M.WHITE)
        box(C-2, C+3, 19, 20, mirrored_z, mirrored_z+1, M.COPPER)
    for x in range(34, C-34, 16):
        box(x, x+2, 17, 19, C-3, C+4, M.WHITE)
        mirrored_x = W - x - 2
        box(mirrored_x, mirrored_x+2, 17, 19, C-3, C+4, M.WHITE)

    # 主控及端口候选位嵌入纵向床身前端连续设备梁。
    controller = (C, 24, 0)
    box(C-64, C+65, 18, 34, 0, 36, M.COMPUTER)
    box(C-56, C+57, 16, 18, 0, 36, M.WFV)
    box(C-6, C+7, 18, 30, 1, 3, M.WFV)
    box(C-2, C+3, 20, 29, 0, 1, M.CONTROL)
    port_x = [C-60, C-48, C-36, C-24, C-12, C+12, C+24, C+36, C+48, C+60]
    port_names = ['参考态记录输入', '扰动态记录输入', '锚定校准输入', '稳定介质输入',
                  '试件与校准资料输入', '能量合同凭据输入', '参考态维系记录输出',
                  '扰动态响应记录输出', '合格试验样件输出', '用后介质回收输出']
    port_purposes = ['参考态原始读数与校准记录', '扰动态试验原始读数', 'I35锚定状态记录',
                     'I36稳定介质输入', '试件与校准资料输入', 'I38合同能量与稳定介质凭据',
                     '参考态维系报告输出', '扰动态响应报告输出', '合格试验样件输出',
                     '使用后稳定介质回收']
    ports = [{'id': name, 'purpose': purpose, 'pos': [x, 24, 0], 'face': 'north'}
             for x, name, purpose in zip(port_x, port_names, port_purposes)]
    for item in ports:
        x, y, z = item['pos']
        box(x, x+1, y, y+1, z, z+1, M.PORT)
    grid[controller[1], controller[2], controller[0]] = IDS[M.CONTROL]
    grid[:, :, :C] = grid[:, :, ::-1][:, :, :C]

    data = {
        'key': 'i37', 'name': NAME, 'title': TITLE,
        'size': [W, H, D],
        'description': '开敞的三条正交测量基线汇入中央零位井：纵向基线承担锚定输入与记录，两条横向基线对照参考态和扰动态；高架正交计量框由同一轨床承力。',
        'design': '三轴世界线干涉测量台',
        'controller': list(controller), 'controller_face': 'north', 'ports': ports,
        'paths': [],
        'zones': [
            {'name': '左侧参考态基线', 'pos': [80, 46, C]},
            {'name': '右侧扰动态基线', 'pos': [W-80, 46, C]},
            {'name': '纵向锚定与记录基线', 'pos': [C, 46, D-90]},
            {'name': '中央零位测量井', 'pos': [C, 198, C]},
            {'name': '嵌入式控制与接口梁', 'pos': [C, 34, 40]},
        ],
        'orientation': 'X=0至528左到右，Y=0为底部，Z=0为正面；主控位于整宽中心X=264。',
    }
    return grid, data


def build_grid():
    """构建开敞正交三轴干涉仪；全部方块关于X=264镜像。"""
    grid = np.zeros((H, D, W), dtype=np.uint8)

    def box(x0, x1, y0, y1, z0, z1, state):
        if not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H and 0 <= z0 < z1 <= D):
            raise ValueError(('坐标越界', (x0, x1, y0, y1, z0, z1), state))
        grid[y0:y1, z0:z1, x0:x1] = IDS[state]

    def strut(start, end, radius, state):
        steps = max(abs(end[i] - start[i]) for i in range(3))
        for step in range(steps + 1):
            point = [round(start[i] + (end[i] - start[i]) * step / steps) for i in range(3)]
            x, y, z = point
            box(x-radius, x+radius+1, y-radius, y+radius+1,
                z-radius, z+radius+1, state)

    # Four narrow runway rails form the shared, grounded X/Z measurement bed.
    for offset, state in ((-38, M.WFV), (-14, M.ROBUST), (14, M.ROBUST), (38, M.WFV)):
        box(0, W, 0, 12, C+offset-6, C+offset+6, state)
        box(C+offset-6, C+offset+6, 0, 12, 0, D, state)
        if abs(offset) == 38:
            box(0, W, 12, 42, C+offset-18, C+offset+18, state)
            box(C+offset-18, C+offset+18, 12, 42, 0, D, state)
        else:
            box(0, W, 12, 30, C+offset-12, C+offset+12, state)
            box(C+offset-12, C+offset+12, 12, 30, 0, D, state)
            if abs(offset) == 14:
                box(0, W, 42, 76, C+offset-20, C+offset+20, state)
                box(C+offset-20, C+offset+20, 42, 76, 0, D, state)
    box(C-50, C+51, 12, 14, C-50, C+51, M.ROBUST)
    box(C-46, C+47, 14, 16, C-46, C+47, M.SOLID)
    box(0, W, 12, 16, C-5, C+6, M.STEEL)
    box(C-5, C+6, 12, 16, 0, D, M.STEEL)
    for station in range(16, W-16, 32):
        box(station-5, station+5, 8, 18, C-50, C+51, M.SOLID)
        box(C-50, C+51, 8, 18, station-5, station+5, M.SOLID)
    for y, state in ((16, M.DEEPSLATE), (18, M.DEEPSLATE_TILES)):
        box(C-54, C+55, y, y+2, C-54, C-46, state)
        box(C-54, C+55, y, y+2, C+47, C+55, state)
        box(C-54, C-46, y, y+2, C-54, C+55, state)
        box(C+47, C+55, y, y+2, C-54, C+55, state)

    # Repeated open portals stand along each arm; the gaps stay clear for sight lines.
    stations = (112, 224)
    for axis in ('x', 'z'):
        for sign in (-1, 1):
            for distance in stations:
                station = C + sign * distance
                if axis == 'x':
                    for side in (-1, 1):
                        z = C + side * 70
                        box(station-12, station+12, 22, 250, z-12, z+12, M.WFV)
                        for y in (22, 78, 134, 190, 244):
                            box(station-11, station+11, y, y+5, z-11, z+11, M.ROBUST)
                    box(station-10, station+10, 20, 40, C-80, C+81, M.STRESS)
                    box(station-10, station+10, 0, 24, C-80, C+81, M.STRESS)
                    box(station-10, station+10, 126, 142, C-80, C+81, M.STEEL_TURBINE)
                    box(station-11, station+11, 246, 268, C-80, C+81, M.WFV)
                    strut((station, 44, C-70), (station, 224, C+70), 2, M.STEEL_TURBINE)
                    strut((station, 44, C+70), (station, 224, C-70), 2, M.STEEL_TURBINE)
                    for y in (54, 102, 158, 206):
                        box(station-8, station+8, y, y+10, C-80, C+81, M.WFV)
                else:
                    for side in (-1, 1):
                        x = C + side * 70
                        box(x-12, x+12, 22, 250, station-12, station+12, M.WFV)
                        for y in (22, 78, 134, 190, 244):
                            box(x-11, x+11, y, y+5, station-11, station+11, M.ROBUST)
                    box(C-80, C+81, 20, 40, station-10, station+10, M.STRESS)
                    box(C-80, C+81, 0, 24, station-10, station+10, M.STRESS)
                    box(C-80, C+81, 126, 142, station-10, station+10, M.STEEL_TURBINE)
                    box(C-80, C+81, 246, 268, station-11, station+11, M.WFV)
                    strut((C-70, 44, station), (C+70, 224, station), 2, M.STEEL_TURBINE)
                    strut((C+70, 44, station), (C-70, 224, station), 2, M.STEEL_TURBINE)
                    for y in (54, 102, 158, 206):
                        box(C-80, C+81, y, y+10, station-8, station+8, M.WFV)

    # Sparse cross rails carry the instrument carriages without becoming floors.
    for index, y in enumerate((38, 86, 134, 182, 230, 270)):
        state = M.WFV if index in (0, 5) else M.STEEL_TURBINE
        for offset in (-31, 31):
            box(0, W, y, y+10, C+offset-6, C+offset+6, state)
            box(C+offset-6, C+offset+6, y, y+10, 0, D, state)
    for y, half, thick, state in ((258, 84, 12, M.WFV), (272, 58, 10, M.STEEL_TURBINE),
                                  (282, 30, 3, M.CHISELED_QUARTZ)):
        box(C-half, C+half+1, y, y+thick, C-half, C-half+thick, state)
        box(C-half, C+half+1, y, y+thick, C+half-thick+1, C+half+1, state)
        box(C-half, C-half+thick, y, y+thick, C-half, C+half+1, state)
        box(C+half-thick+1, C+half+1, y, y+thick, C-half, C+half+1, state)

    # A four-post metrology cage supports the open zero well and elevated Y-axis.
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = C + sx*36, C + sz*36
            box(x-7, x+7, 18, 285, z-7, z+7, M.WFV)
            for y in (54, 110, 166, 222):
                box(x-9, x+9, y, y+5, z-9, z+9, M.ROBUST)
    for y, half, thick, state in ((64, 42, 8, M.ROBUST), (120, 36, 6, M.ASSEMBLY),
                                  (176, 36, 6, M.ASSEMBLY), (238, 42, 8, M.WFV)):
        box(C-half, C+half+1, y, y+thick, C-half, C-half+thick, state)
        box(C-half, C+half+1, y, y+thick, C+half-thick+1, C+half+1, state)
        box(C-half, C-half+thick, y, y+thick, C-half, C+half+1, state)
        box(C+half-thick+1, C+half+1, y, y+thick, C-half, C+half+1, state)

    # The test specimen sits on a real isolated pedestal inside the sighted aperture.
    box(C-28, C+29, 64, 70, C-28, C+29, M.QUARTZ_BRICKS)
    box(C-20, C+21, 70, 76, C-20, C+21, M.VIBRATION)
    box(C-10, C+11, 76, 94, C-10, C+11, M.NONCONDUCTING)
    box(C-6, C+7, 94, 106, C-6, C+7, M.STABLE)
    box(C-4, C+5, 106, 116, C-4, C+5, M.TINTED_GLASS)
    box(C-2, C+3, 116, 122, C-2, C+3, M.FUSION_GLASS)
    box(C-14, C+15, 122, 126, C-14, C-10, M.LASER)
    box(C-14, C+15, 122, 126, C+11, C+15, M.LASER)

    for y in (64, 120, 176, 238):
        strut((C-36, y+3, C), (C+36, y+3, C), 3, M.WFV)
        strut((C, y+3, C-36), (C, y+3, C+36), 3, M.WFV)

    # Four axial instrument heads are mounted directly to the rails and portal frames.
    for axis in ('x', 'z'):
        for sign in (-1, 1):
            if axis == 'x':
                x, z = C + sign*218, C
                box(x-15, x+16, 112, 120, z-15, z+16, M.CALCITE)
                box(x-11, x+12, 120, 142, z-11, z+12, M.POWER)
                box(x-7, x+8, 142, 150, z-7, z+8, M.CLEAN_GLASS)
                box(x-4, x+5, 150, 154, z-4, z+5, M.BLUE_GLASS)
            else:
                x, z = C, C + sign*218
                box(x-15, x+16, 112, 120, z-15, z+16, M.CALCITE)
                box(x-11, x+12, 120, 142, z-11, z+12, M.ADVANCED_COMPUTER)
                box(x-7, x+8, 142, 150, z-7, z+8, M.TEMPERED_GLASS)
                box(x-4, x+5, 150, 154, z-4, z+5, M.CLEAN_GLASS)
            box(x-17, x-12, 124, 130, z-17, z+18, M.IRON)
            box(x+13, x+18, 124, 130, z-17, z+18, M.IRON)
            box(x-3, x+4, 12, 114, z-3, z+4, M.WFV)

    # Calibrated sight marks run beside the rails in a restrained white/copper cadence.
    for station in range(24, C-32, 24):
        for sign in (-1, 1):
            x = C + sign*station
            box(x-2, x+2, 18, 21, C-47, C-43, M.WHITE)
            box(x-1, x+1, 21, 23, C-47, C-43, M.COPPER)
            z = C + sign*station
            box(C-47, C-43, 18, 21, z-2, z+2, M.WHITE)
            box(C-47, C-43, 21, 23, z-1, z+1, M.COPPER)

    # The controller and ten interfaces are flush-mounted in the front equipment beam.
    controller = (C, 24, 0)
    box(C-64, C+65, 18, 34, 0, 36, M.COMPUTER)
    box(C-56, C+57, 16, 18, 0, 36, M.WFV)
    box(C-6, C+7, 18, 30, 1, 3, M.WFV)
    box(C-2, C+3, 20, 29, 0, 1, M.COMPUTER)
    port_x = [C-60, C-48, C-36, C-24, C-12, C+12, C+24, C+36, C+48, C+60]
    port_names = ['参考态记录输入', '扰动态记录输入', '锚定校准输入', '稳定介质输入',
                  '试件与校准资料输入', '能量合同凭据输入', '参考态维系记录输出',
                  '扰动态响应记录输出', '合格试验样件输出', '用后介质回收输出']
    port_purposes = ['参考态原始读数与校准记录', '扰动态试验原始读数', 'I35锚定状态记录',
                     'I36稳定介质输入', '试件与校准资料输入', 'I38合同能量与稳定介质凭据',
                     '参考态维系报告输出', '扰动态响应报告输出', '合格试验样件输出',
                     '使用后稳定介质回收']
    ports = [{'id': name, 'purpose': purpose, 'pos': [x, 24, 0], 'face': 'north'}
             for x, name, purpose in zip(port_x, port_names, port_purposes)]
    for item in ports:
        x, y, z = item['pos']
        box(x, x+1, y, y+1, z, z+1, M.PORT)
    grid[controller[1], controller[2], controller[0]] = IDS[M.CONTROL]
    grid[:, :, :C] = grid[:, :, ::-1][:, :, :C]
    grid[controller[1], controller[2], controller[0]] = IDS[M.CONTROL]
    detail_index = 0
    for state in STATES[:-2]:
        if state in (M.WFV, M.ROBUST):
            continue
        y, z = 24 + detail_index*5, C + stations[-1]
        for x in (C-70, C+70):
            grid[y:y+3, z-1:z+2, x-1:x+2] = IDS[state]
        detail_index += 1
    grid[controller[1], controller[2], controller[0]] = IDS[M.CONTROL]

    # Tie any clipped casing remainder into the nearest main structure without floating voxels.
    labels, count = ndimage.label(grid != 0, structure=ndimage.generate_binary_structure(3, 1))
    sizes = np.bincount(labels.ravel())
    main_id = int(np.argmax(sizes[1:]) + 1)
    main_coords = np.argwhere(labels[::3, ::3, ::3] == main_id) * 3
    tree = cKDTree(main_coords)
    for label in range(1, count + 1):
        if label == main_id:
            continue
        coords = np.argwhere(labels == label)
        source = coords[len(coords)//2]
        if source[2] < C:
            continue
        _, nearest = tree.query(source)
        target = main_coords[int(nearest)].copy()
        current = source.copy()
        for axis in (0, 1, 2):
            while current[axis] != target[axis]:
                current[axis] += 1 if target[axis] > current[axis] else -1
                y, z, x = map(int, current)
                grid[y, z, x] = IDS[M.WFV]
                grid[y, z, W-1-x] = IDS[M.WFV]
    del labels, sizes, main_coords, tree

    data = {
        'key': 'i37', 'name': NAME, 'title': TITLE,
        'size': [W, H, D],
        'description': '三轴开敞门架沿X、Y、Z基线汇入中央零位井；端部计量头承接参考态、扰动态和锚定记录，所有门架落在连续梁轨床上。',
        'design': '三轴世界线干涉测量台',
        'controller': list(controller), 'controller_face': 'north', 'ports': ports,
        'paths': [],
        'zones': [
            {'name': '左侧参考态基线', 'pos': [80, 46, C]},
            {'name': '右侧扰动态基线', 'pos': [W-80, 46, C]},
            {'name': '纵向锚定与记录基线', 'pos': [C, 46, D-90]},
            {'name': '中央零位测量井', 'pos': [C, 110, C]},
            {'name': '嵌入式控制与接口梁', 'pos': [C, 34, 40]},
        ],
        'orientation': 'X=0至528左到右，Y=0为底部，Z=0为正面；主控位于整宽中心X=264。',
    }
    return grid, data


def build():
    grid, data = build_grid()
    blocks = grid != 0
    counts = np.bincount(grid.ravel(), minlength=len(STATES) + 1)
    data['material_counts'] = {STATES[i-1]: int(counts[i]) for i in range(1, len(STATES)+1)}
    data['block_count'] = int(counts[1:].sum())
    del blocks
    return grid, data
