# -*- coding: utf-8 -*-
"""I11 / I12 独立第六版形体；只返回候选，不写确认归档或游戏实例。

2026-10-14：以折肘机器人精密工厂、双翼分面编程晶舱替换旧龙门厅和三舱穹顶。
尺寸以宽、高、深记录。所有支撑在设计时放置，不用事后落地修补。
"""
from i09_i13_v6_common import start, zone, route, finish, PIPE, GEAR, GRATE, PANEL, DIAMOND

CLEAN = 'gtceu:clean_machine_casing'
POWER = 'gtceu:high_power_casing'
COMPUTER = 'gtceu:computer_casing'
VENT = 'gtceu:computer_heat_vent'
GLASS = 'gtlcore:hsss_reinforced_borosilicate_glass'
ENERGY_GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
ARM = 'gtlcore:manipulator'
PRECISION = 'gtlcore:multi_functional_casing'
ASSEMBLY = 'gtlcore:advanced_assembly_line_unit[active=false]'
COMPUTE = 'gtlcore:super_computation_component[active=false]'
COOLER = 'gtlcore:super_cooler_component[active=false]'
I11_SHELL = 'hk3gtl:voltage_machine_casing_hbv'
I12_SHELL = 'hk3gtl:voltage_machine_casing_civ'


def _octagon(dx, dz, radius):
    return max(abs(dx), abs(dz)) <= radius and abs(dx) + abs(dz) <= radius + radius // 2


def _octagonal_plate(a, cx, cz, radius, y0, y1, material):
    for x in range(cx-radius, cx+radius+1):
        for z in range(cz-radius, cz+radius+1):
            if _octagon(x-cx, z-cz, radius):
                a.box((x, y0, z), (x, y1, z), material)


def _robot(a, side, z, index):
    """有落地转台、肩轴、两段粗臂、腕轴和下压工具的六面连通折肘机器人。"""
    left = side == 'left'
    x0, x1 = (3, 10) if left else (44, 51)
    shoulder, elbow, wrist = (7, 13, 19) if left else (47, 41, 35)
    a.box((x0, 0, z-3), (x1, 2, z+3), CLEAN)
    a.box((x0+1, 3, z-2), (x1-1, 5, z+2), I11_SHELL)
    a.box((shoulder-1, 6, z-1), (shoulder+1, 11, z+1), ARM)
    a.box((shoulder-2, 9, z-2), (shoulder+2, 11, z+2), GEAR)
    # 不同工序有不同肘高，轮廓沿 U 线逐级展开。
    elbow_y = 16 + index
    wrist_y = 11 + index
    a.line((shoulder, 11, z), (elbow, elbow_y, z), I11_SHELL, 3)
    a.box((elbow-1, elbow_y-1, z-2), (elbow+1, elbow_y+1, z+2), GEAR)
    a.line((elbow, elbow_y, z), (wrist, wrist_y, z), CLEAN, 3)
    a.box((wrist-1, wrist_y-1, z-1), (wrist+1, wrist_y+1, z+1), ARM)
    a.box((wrist, 8, z), (wrist, wrist_y-2, z), PRECISION)
    a.box((wrist-3, 0, z-3), (wrist+3, 2, z+3), CLEAN)
    a.box((wrist-3, 3, z-2), (wrist+3, 4, z+2), I11_SHELL)
    a.box((wrist-2, 5, z-2), (wrist+2, 5, z+2), ASSEMBLY)
    a.box((wrist-1, 6, z-1), (wrist+1, 6, z+1), PRECISION)
    # 肩部接线汇流与工位供料支线各接实际设备。
    outward = x0 if left else x1
    a.box((outward, 2, z-1), (outward, 4, z+1), PANEL)
    route(a, 'U 形送料轨', f'{"左" if left else "右"}侧折肘工位 {index+1}',
          [(12 if left else 42, 3, z), (wrist, 3, z)], PIPE)
    zone(a, f'{"左" if left else "右"}侧折肘工位 {index+1}',
         (x0 if left else wrist-3, 0, z-3),
         (wrist+3 if left else x1, elbow_y+1, z+3),
         ['本体定位', '核心植入', '精密装配'][index] if left else
         ['电性校准', '视觉检测', '合格分流'][2-index], 'articulated_robot')


def i11():
    a = start('I11', '纳米机器人装配阵列', (55, 31, 45),
              'U 形精密工厂、六台折肘机器人、上升维护脊梁与偏心悬臂吊点',
              '左侧上料沿 U 形轨进入三道装配工位，后方精密转台集中校准，右侧检验并输出')
    # U 形基础只托起机器人、轨道和后方设备；中央前场是实际检修入口。
    a.box((3, 0, 6), (51, 0, 10), GRATE)
    a.box((3, 0, 10), (13, 0, 38), CLEAN)
    a.box((41, 0, 10), (51, 0, 38), CLEAN)
    a.box((0, 0, 38), (54, 1, 44), CLEAN)
    a.box((24, 0, 0), (30, 0, 25), GRATE)
    for z in (14, 24, 33):
        a.box((12, 0, z-3), (22, 0, z+3), GRATE)
        a.box((32, 0, z-3), (42, 0, z+3), GRATE)
    a.box((21, 0, 25), (33, 1, 38), CLEAN)
    # 明确的 U 形输送床，少量齿轮节拍表达载具定位。
    for lo, hi in [((10, 1, 10), (14, 3, 36)),
                   ((10, 1, 34), (44, 3, 38)),
                   ((40, 1, 10), (44, 3, 36))]:
        a.box(lo, hi, I11_SHELL)
        a.box((lo[0]+1, 4, lo[2]), (hi[0]-1, 4, hi[2]), GRATE)
    for z in range(12, 35, 5):
        for x in (12, 42):
            a.set(x, 4, z, GEAR)
    for x in range(17, 39, 5):
        a.set(x, 4, 36, GEAR)
    zone(a, 'U 形送料轨', (10, 1, 10), (44, 4, 38), '定位载具沿开口朝前的 U 形轨转运', 'horseshoe_logistics')
    for index, z in enumerate((14, 24, 33)):
        _robot(a, 'left', z, index)
        _robot(a, 'right', z, index)
    # 中央集成转台比机械臂低：保留周围空隙，使工位和核心都有层级。
    a.box((25, 2, 29), (29, 5, 33), POWER)
    _octagonal_plate(a, 27, 31, 6, 6, 7, I11_SHELL)
    a.ring((27, 8, 31), 5, 5, ASSEMBLY)
    a.ring((27, 9, 31), 4, 4, PRECISION)
    a.box((25, 8, 29), (29, 11, 33), ENERGY_GLASS, True)
    a.box((26, 8, 30), (28, 10, 32), ARM)
    a.set(27, 11, 31, DIAMOND)
    for x, z in ((22, 29), (22, 33), (32, 29), (32, 33)):
        a.box((x, 2, z), (x, 6, z), CLEAN)
    zone(a, '后方精密校准转台', (21, 0, 25), (33, 11, 38), '植入后进行集成校准与搬运', 'assembly_dais')
    # 后置维护脊梁是递升分段设备廊，玻璃仅为窄观察带。
    # 脊梁实体以支柱、薄设备背板和步进顶带构成，内部不是实心墙。
    stages = [(0, 8, 10), (9, 17, 13), (18, 26, 16),
              (27, 35, 19), (36, 44, 22), (45, 54, 25)]
    for index, (x0, x1, top) in enumerate(stages):
        a.box((x0, 2, 42), (x0+1, top, 44), CLEAN)
        a.box((x1-1, 2, 42), (x1, top, 44), CLEAN)
        a.box((x0, top-1, 40), (x1, top, 44), I11_SHELL)
        a.box((x0+2, 3, 43), (x1-2, top-2, 43), COMPUTER)
        a.box((x0+2, 6, 42), (x1-2, 8, 42), GLASS)
        a.box((x0+2, 3, 40), (x1-2, 4, 42), PANEL)
        for x in range(x0+2, x1-1, 2):
            a.box((x, top+1 if top < 25 else top, 42),
                  (x, top+2 if top < 25 else top+1, 43), VENT)
        if index:
            prev = stages[index-1]
            a.box((x0-1, prev[2]-1, 40), (x0, top, 41), CLEAN)
    zone(a, '递升维护脊梁', (0, 0, 38), (54, 26, 44), '数据、洁净处理与工具维护沿阶梯脊梁集成', 'terraced_backbone')
    # 一座右后偏心吊机承担转台维护，不给整个厂区盖大顶板。
    a.box((48, 2, 39), (50, 28, 41), CLEAN)
    a.box((47, 26, 38), (51, 28, 42), GEAR)
    a.box((27, 28, 37), (49, 30, 39), I11_SHELL)
    a.box((27, 28, 30), (29, 30, 37), I11_SHELL)
    a.line((48, 22, 39), (39, 28, 39), CLEAN, 3)
    a.box((27, 26, 30), (29, 27, 32), GEAR)
    a.box((28, 17, 31), (28, 25, 31), ARM)
    a.box((27, 16, 30), (29, 17, 32), PRECISION)
    zone(a, '偏心悬臂维护吊机', (27, 2, 30), (51, 30, 42), '只覆盖校准转台与背部维护区的吊运范围', 'cantilever_crane')
    # 低矮供料抽屉与成品检验台保持开放正面，不抹平六个机器人。
    for x in (7, 45):
        a.box((x-2, 1, 7), (x+2, 3, 10), I11_SHELL)
        a.box((x-1, 4, 8), (x+1, 5, 10), PANEL)
    route(a, '本体输入', 'U 形送料轨', [(14, 2, 6), (14, 2, 9), (12, 2, 9), (12, 2, 11)])
    route(a, '核心输入', '后方精密校准转台', [(18, 2, 6), (18, 2, 9), (24, 2, 9), (24, 2, 28)])
    route(a, '供能', '递升维护脊梁', [(22, 2, 6), (22, 2, 9), (23, 2, 9), (23, 2, 41)])
    route(a, '装配辅材输入', 'U 形送料轨', [(32, 2, 6), (32, 2, 9), (42, 2, 9), (42, 2, 11)])
    route(a, 'U 形送料轨', '成品机器人输出', [(42, 2, 11), (36, 2, 11), (36, 2, 6)])
    route(a, 'U 形送料轨', '余料回收', [(42, 1, 13), (40, 1, 13), (40, 1, 6)])
    a.paths.append({'name': '中央工位检修入口', 'min': [25, 1, 8], 'max': [29, 4, 22]})
    purposes = [('BODY', '本体载具输入候选'), ('CORE', '纳米核心输入候选'),
                ('POWER', '电能输入候选'), ('MATERIAL', '装配辅材输入候选'),
                ('ROBOT', '装配后机器人输出候选'), ('SCRAP', '余料回收候选')]
    return finish(a, 'i11-nanobot-array-v6',
                  '海军蓝 U 形精密工厂：六台有肩轴、折肘与腕轴的机器人围绕低位工艺留白展开；后方维护脊梁逐段升起，一座偏心吊机只服务精密校准转台。窄玻璃观察带、连续供料轨和独立检修入口让装配流程直接可读。',
                  purposes, I11_SHELL,
                  ['GTCEu ASSEMBLY_LINE（GTMachines.java:940）：连续输送与不同进出料端',
                   'GTLCore COMPONENT_ASSEMBLY_LINE（MultiBlockMachineAStructureD.java:23）：分段工位、观察带与上层设备脊',
                   'GTLsupb RANK_DERIVATION_ASSEMBLY_MATRIX（RankDerivationAssemblyMatrixPatternLayers.java）：集中核心与外围骨架层级'])


def _crystal_radius(y):
    if y <= 13:
        return 4 + (y-5) * 6 // 8
    if y <= 21:
        return 10
    return max(0, 10 - (y-21) * 10 // 15)


def _programming_crystal(a):
    cx, cz = 22, 23
    # 从完整体积求两格厚外壳；斜切面与收尖台阶有共同实体截面。
    volume = {(cx+dx, y, cz+dz)
              for y in range(5, 37)
              for dx in range(-_crystal_radius(y), _crystal_radius(y)+1)
              for dz in range(-_crystal_radius(y), _crystal_radius(y)+1)
              if _octagon(dx, dz, _crystal_radius(y))}
    neighbours = tuple((dx*n, dy*n, dz*n)
                       for n in (1, 2)
                       for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0),
                                         (0, -1, 0), (0, 0, 1), (0, 0, -1)))
    for x, y, z in sorted(volume):
        if any((x+dx, y+dy, z+dz) not in volume for dx, dy, dz in neighbours):
            radius = _crystal_radius(y)
            dx, dz = x-cx, z-cz
            cardinal_rib = (dx == 0 and abs(dz) == radius) or (dz == 0 and abs(dx) == radius)
            bevel_rib = abs(dx) + abs(dz) == radius+radius//2 and (abs(dx) == radius or abs(dz) == radius)
            a.set(x, y, z, I12_SHELL if cardinal_rib or bevel_rib or y in (5, 13, 21, 29, 36) else ENERGY_GLASS)
    # 中心轴与三层感应/运算环都经实体径向桥相连，透明舱可读出内部密度。
    a.box((21, 6, 22), (23, 31, 24), POWER)
    for y, radius in ((12, 4), (18, 5), (24, 4)):
        a.ring((cx, y, cz), radius, radius, COMPUTE)
        a.ring((cx, y+1, cz), radius, radius, I12_SHELL)
        for x, z in ((cx-radius, cz), (cx+radius, cz), (cx, cz-radius), (cx, cz+radius)):
            a.line((cx, y, cz), (x, y, z), COMPUTER)
        for x in (cx-2, cx+2):
            a.box((x, y-1, cz-2), (x, y+1, cz+2), COOLER)
    for y in (16, 18, 20):
        a.set(22, y, 22, DIAMOND)
    a.box((21, 30, 22), (23, 32, 24), COMPUTE)
    a.box((22, 33, 23), (22, 35, 23), I12_SHELL)
    zone(a, '分面自组织编程晶舱', (12, 5, 13), (32, 36, 33), '三层同轴数据感应环在闭合分面屏蔽舱内围绕核心编程', 'faceted_programming_chamber')


def _server_wing(a, left):
    """根部低、外缘高的双层折翼；层间有共同体素，六面连续。"""
    root = 14 if left else 30
    outer = 0 if left else 44
    for offset in range(15):
        x = root-offset if left else root+offset
        top = 10+offset
        z0 = 18-offset*8//14
        z1 = 28+offset*10//14
        for z in range(z0, z1+1):
            material = I12_SHELL if z in (z0, z1) or offset in (0, 14) else (VENT if z % 4 == 0 else CLEAN)
            a.box((x, top-1, z), (x, top, z), material)
        # 有节奏的服务器鳍向下折回，每列都直接附着到连续翼面。
        if offset % 3 == 1:
            for z in range(z0+2, z1-1, 4):
                a.box((x, top-5, z), (x, top-2, z+1), COMPUTE)
                a.set(x, top-5, z, COOLER)
    a.box((root-1, 0, 20), (root+1, 9, 26), COMPUTER)
    # 斜向机械支撑从主根部到外翼；每个转折使用完整 3 格厚截面。
    a.line((root, 6, 23), (outer+2 if left else outer-2, 18, 23), I12_SHELL, 3)
    a.line((outer+2 if left else outer-2, 18, 23), (outer+2 if left else outer-2, 22, 23), CLEAN, 3)
    x0, x1 = (0, 10) if left else (34, 44)
    a.box((x0, 0, 10), (x1, 1, 38), CLEAN)
    # 外侧低位数据仓与散热条低于折翼，和高位晶体形成明确主次。
    for z in (12, 20, 28, 36):
        a.box((x0+2, 2, z-1), (x1-2, 4, z+1), COMPUTER)
        a.box((x0+2, 5, z), (x1-2, 5, z), PANEL)
        a.box((x0, 2, z-1), (x0+1, 3, z+1), COOLER)
    side = '左' if left else '右'
    zone(a, side+'侧扫掠服务器翼', (min(root, outer), 0, 10),
         (max(root, outer), 24, 38), '低位模板数据仓、抬升服务器鳍与根部数据汇聚', 'swept_server_wing')
    route(a, side+'侧扫掠服务器翼', '分面自组织编程晶舱',
          [(root, 6, 23), (22, 6, 23)], PANEL)


def i12():
    a = start('I12', '纳米自组织编程舱', (45, 37, 39),
              '收尖分面晶舱、双侧扫掠服务器折翼与低位数据岛',
              '前方输入模板和样本，双翼缓存及运算，晶舱内三层感应环实施自组织，前方回写与输出')
    # 前方控制坞、中央门槛和设备基础彼此接通，未铺空白整板。
    a.box((6, 0, 6), (38, 0, 10), GRATE)
    a.box((20, 0, 0), (24, 0, 18), GRATE)
    _octagonal_plate(a, 22, 23, 7, 0, 2, CLEAN)
    _octagonal_plate(a, 22, 23, 5, 3, 4, I12_SHELL)
    a.ring((22, 0, 23), 12, 12, GRATE, 2)
    a.box((15, 0, 36), (29, 0, 38), GRATE)
    for x in (10, 34):
        a.box((x-1, 0, 20), (x+1, 0, 26), GRATE)
    # 四个低位支座承托收尖舱底；中央透明体积没有随意落地柱。
    for x, z in ((18, 23), (26, 23), (22, 19), (22, 27)):
        a.box((x, 3, z), (x, 5, z), POWER)
    _programming_crystal(a)
    _server_wing(a, True)
    _server_wing(a, False)
    # 维护环在设备基础之外，不把管线切进观察路径。
    route(a, '电能输入', '分面自组织编程晶舱',
          [(17, 2, 6), (17, 2, 9), (16, 2, 9), (16, 2, 23), (18, 2, 23)], POWER)
    route(a, '程序模板输入', '左侧扫掠服务器翼',
          [(9, 2, 6), (9, 2, 9), (6, 2, 9), (6, 2, 12)], PANEL)
    route(a, '纳米样本输入', '分面自组织编程晶舱',
          [(13, 2, 6), (13, 2, 9), (18, 2, 9), (18, 2, 22)], PIPE)
    route(a, '并行数据输入', '右侧扫掠服务器翼',
          [(27, 2, 6), (27, 2, 9), (38, 2, 9), (38, 2, 12)], PANEL)
    route(a, '分面自组织编程晶舱', '编程单元输出',
          [(26, 2, 23), (26, 2, 11), (31, 2, 11), (31, 2, 6)], PIPE)
    route(a, '右侧扫掠服务器翼', '回写数据输出',
          [(38, 2, 12), (35, 2, 12), (35, 2, 6)], PANEL)
    a.paths.append({'name': '中央晶舱观察入口', 'min': [20, 1, 8], 'max': [24, 3, 14]})
    a.paths.append({'name': '后方核心维护横带', 'min': [15, 1, 36], 'max': [29, 3, 38]})
    purposes = [('TEMPLATE', '程序模板输入候选'), ('SAMPLE', '纳米样本输入候选'),
                ('POWER', '电能输入候选'), ('DATA', '并行数据输入候选'),
                ('NANITE', '编程完成的纳米单元输出候选'), ('RETURN', '回写数据输出候选')]
    return finish(a, 'i12-nanobot-programming-v6',
                  '青蓝分面编程晶舱：中央屏蔽体下窄上尖，透明八面折面显露三层运算感应环；两翼从低根部向外上扬，服务器鳍与下层数据仓形成高低对照。端口、正面观察入口和后方维护横带各有明确去向。',
                  purposes, I12_SHELL,
                  ['GTCEu HIGH_PERFORMANCE_COMPUTING_ARRAY（GTResearchMachines.java:80）：计算组件与连续排热面分离',
                   'GTLsupb RANK_DERIVATION_ASSEMBLY_MATRIX（RankDerivationAssemblyMatrixPatternLayers.java）：中心运算体、外围骨架与逐渐收束的上段'])
