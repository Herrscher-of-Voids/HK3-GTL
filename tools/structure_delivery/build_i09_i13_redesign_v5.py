# -*- coding: utf-8 -*-
"""内测5 I09、I11、I12、I13 重制版结构生成器。

变更记录 #1 2026-10-02 06:18:00（内测5结构重制）
- 删除：四台机器旧的同质化底板、方盒外壳和重复顶板构图。
- 新增：竖向化工树、双线龙门装配厅、三舱数据穹顶、放射式包覆转盘四种独立几何。
- 修改：端口统一使用 industrial_port_casing；主体采用已在测试包中核对过的 GTCEu/GTLCore 完整方块。
- 用途：只生成预览与 Sponge 结构候选，不宣称正式 Pattern、配方或游戏运行逻辑已经接入。
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_i07_calibration_preview import package
from redesign69_geometry import Build, ROOT

PORT = 'hk3gtl:industrial_port_casing'
FLOOR = 'ad_astra:ostrum_plating'
BASE = 'gtlcore:space_elevator_mechanical_casing'
RIB = 'gtlcore:lafium_mechanical_casing'
GLASS = 'gtlcore:rhenium_reinforced_energy_glass'
GLASS2 = 'hk3gtl:glass_honkai_stabilized'
PANEL = 'gtceu:advanced_computer_casing'
POWER = 'gtceu:high_power_casing'
RAIL = 'gtceu:assembly_line_grating'
PIPE = 'gtceu:tungstensteel_pipe_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
FIELD = 'gtlcore:graviton_field_constraint_casing'
INJECT = 'gtlcore:dimension_injection_casing'
STAR = 'gtlcore:stellar_containment_casing'
ARM = 'gtlcore:manipulator'
PRECISION = 'gtlcore:multi_functional_casing'


def common(brief, size):
    a = Build(brief)
    a.w, a.h, a.d = size
    a.cx, a.cz = size[0] // 2, size[2] // 2
    a.box((0, 0, 0), (a.w - 1, 0, a.d - 1), FLOOR)
    return a


def ground_all(a):
    """Connect every visible equipment island to the continuous service deck.

    The preview audit intentionally requires one six-face connected structure.
    The designs use separated towers, gantries and pods for readability, so
    their supports are added after the equipment geometry is laid out. Existing
    blocks are never replaced; a support stops when it meets another member.
    """
    occupied = set(a.b)
    seen = set()
    directions = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for start in sorted(occupied):
        if start in seen or start[1] == 0:
            continue
        component = {start}
        queue = [start]
        seen.add(start)
        for current in queue:
            for dx, dy, dz in directions:
                neighbour = (current[0] + dx, current[1] + dy, current[2] + dz)
                if neighbour in occupied and neighbour not in seen:
                    seen.add(neighbour)
                    component.add(neighbour)
                    queue.append(neighbour)
        # Components touching the deck already have a physical foundation.
        if any(y == 0 for _, y, _ in component):
            continue
        x, y, z = min(component, key=lambda p: (p[1], p[0], p[2]))
        # A narrow service column is less intrusive than filling the gaps
        # between deliberately separated machines.
        for yy in range(0, y):
            if (x, yy, z) not in a.b:
                a.set(x, yy, z, BASE)
        occupied = set(a.b)


def front_interfaces(a, controller, ports):
    # 端口位于 z=2，z=1 保持为空，满足工业接口前方净空审计。
    # 控制器保留钻石块作为主机标记；industrial_port_casing 只用于仓室接口。
    a.set(*controller, 'minecraft:diamond_block')
    for _, pos, purpose in ports:
        x, y, z = pos
        a.set(x, y, z, PORT)
        a.set(x, y - 1, z, PANEL)
        a.set(x, y, z + 1, PANEL)
    ground_all(a)
    return [{'id': key, 'pos': pos, 'face': 'north', 'purpose': purpose} for key, pos, purpose in ports]


def i09():
    brief = {'id': 'I09', 'title': '魂钢前驱体配制釜', 'minimum_wdh': [21, 25, 25],
             'catalog_minimum_wdh': [21, 25, 25], 'form': '竖向化工树与悬臂加料塔',
             'flow': '粉体加料、溶剂计量、魂钢前驱体混合、底部排放'}
    a = common(brief, (39, 43, 37))
    # 中央高位配制釜：窄底、膨胀肩、顶部冷凝冠，轮廓类似真实化工塔而非方盒。
    for y, rx, rz, mat in ((3, 7, 7, POWER), (7, 9, 9, RIB), (11, 11, 11, POWER),
                            (16, 11, 11, RIB), (22, 10, 10, FIELD), (28, 8, 8, RIB)):
        a.ring((19, y, 18), rx, rz, mat, 2)
    a.box((13, 3, 12), (25, 28, 24), GLASS, True)
    a.box((17, 5, 16), (21, 26, 20), GLASS2, True)
    a.line((19, 3, 18), (19, 33, 18), STAR, 1)
    for y in (9, 15, 21, 27):
        a.ring((19, y, 18), 7, 7, INJECT, 1)
        a.set(19, y, 11, GEAR); a.set(19, y, 25, GEAR)
    # 两座不对称加料塔：左侧粉体斗，右侧液体计量塔。
    a.box((2, 7, 5), (10, 20, 13), PANEL, True)
    a.box((4, 9, 7), (8, 17, 11), GLASS, True)
    a.box((28, 5, 5), (36, 24, 13), POWER, True)
    a.box((30, 7, 7), (34, 20, 11), GLASS2, True)
    for x, z in ((5, 9), (33, 9)):
        a.line((x, 2, z), (x, 31, z), RIB)
        a.box((x - 2, 18, z - 2), (x + 2, 20, z + 2), GEAR)
        a.line((x, 20, z), (19, 24, 18), PIPE)
    # 斜向输送桥与釜底排放总管，明确表达工艺流向。
    a.line((8, 17, 9), (13, 17, 16), PIPE, 2)
    a.line((30, 20, 9), (25, 20, 16), PIPE, 2)
    a.line((19, 3, 18), (19, 3, 33), PIPE, 2)
    a.box((14, 32, 13), (24, 34, 23), RAIL, True)
    for x in range(15, 25, 3): a.line((x, 34, 18), (x, 40, 18), RIB)
    a.box((17, 39, 16), (21, 41, 20), POWER, True)
    # 地面管廊只在两侧布置，正面接口前保持开放。
    a.box((1, 1, 28), (11, 3, 35), PANEL)
    a.box((27, 1, 28), (37, 3, 35), PANEL)
    controller = [19, 5, 2]
    ports_raw = [('POWDER', [6, 5, 2], '粉体前驱物输入'), ('SOLVENT', [11, 5, 2], '溶剂输入'),
                 ('POWER', [16, 5, 2], '供能'), ('CATALYST', [22, 5, 2], '催化剂输入'),
                 ('PRODUCT', [27, 5, 2], '魂钢前驱体输出'), ('RESIDUE', [32, 5, 2], '残液排放')]
    ports = front_interfaces(a, controller, ports_raw)
    return {'key': 'i09', 'name': 'i09-soulium-precursor-v5', 'title': brief['title'],
            'size': [a.w, a.h, a.d], 'controller': controller, 'ports': ports, 'paths': [],
            'zones': [{'name': '中央分段配制釜', 'kind': 'reactor', 'min': [8, 3, 7], 'max': [30, 34, 29], 'pos': [19, 28, 18], 'role': '魂钢前驱体混合与约束', 'service_face': '四周'},
                      {'name': '双塔计量站', 'kind': 'feed_towers', 'min': [2, 5, 5], 'max': [36, 24, 13], 'pos': [19, 24, 9], 'role': '粉体与液体分路计量', 'service_face': '前侧'},
                      {'name': '顶部冷凝冠', 'kind': 'condenser', 'min': [14, 32, 13], 'max': [24, 41, 23], 'pos': [19, 41, 18], 'role': '冷凝、回流与维护吊点', 'service_face': '顶部'}],
            'links': [], 'brief': brief, 'description': 'I09 重制为竖向化工树：中央分段配制釜由双塔计量站供料，斜向管桥汇入釜肩，底部总管排放，顶部冷凝冠负责回流与检修。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}


def i11():
    brief = {'id': 'I11', 'title': '纳米机器人装配阵列', 'minimum_wdh': [33, 37, 25],
             'catalog_minimum_wdh': [33, 37, 25], 'form': '双线龙门装配厅',
             'flow': '本体上料、核心植入、双线装配、汇合检测与成品分流'}
    a = common(brief, (55, 35, 43))
    # 两条平行生产线，中间留出人员/物流走廊，构图完全横向展开。
    for z, shell in ((12, 'hk3gtl:voltage_machine_casing_hdv'), (30, 'hk3gtl:voltage_machine_casing_hcv')):
        a.box((4, 2, z), (50, 4, z + 5), RAIL)
        a.box((4, 5, z), (50, 6, z), shell)
        a.box((4, 5, z + 5), (50, 6, z + 5), shell)
        for x in (8, 16, 24, 32, 40, 48):
            a.box((x, 5, z + 1), (x + 1, 5, z + 4), GEAR)
    # 六座跨线龙门，每座都有上下两层机械臂，不是重复的封闭舱。
    for x in (9, 17, 25, 33, 41, 49):
        a.box((x, 7, 10), (x + 2, 24, 10), RIB)
        a.box((x, 7, 35), (x + 2, 24, 35), RIB)
        a.box((x, 22, 10), (x + 2, 24, 35), PANEL)
        a.box((x + 1, 9, 13), (x + 1, 20, 17), ARM)
        a.box((x + 1, 9, 31), (x + 1, 20, 35), ARM)
        a.box((x - 1, 20, 16), (x + 3, 21, 18), PRECISION)
        a.box((x - 1, 20, 30), (x + 3, 21, 32), PRECISION)
    # 末端合流检测塔和高位吊运梁。
    a.box((45, 8, 17), (52, 28, 27), FIELD, True)
    a.box((47, 10, 19), (50, 25, 25), GLASS, True)
    a.box((48, 12, 20), (49, 23, 24), STAR)
    a.box((6, 27, 10), (50, 29, 35), RAIL)
    for x in (10, 20, 30, 40, 48):
        a.box((x, 29, 10), (x + 1, 32, 35), BASE)
    a.box((23, 30, 17), (31, 32, 27), POWER, True)
    a.box((26, 31, 20), (28, 33, 24), GLASS2, True)
    # 上料缓冲仓与右端检测塔通过实体地面底座连接。
    a.box((2, 7, 15), (7, 22, 27), PANEL, True)
    a.box((3, 9, 17), (6, 20, 25), GLASS, True)
    controller = [27, 5, 2]
    ports_raw = [('BODY', [7, 5, 2], '机器人本体输入'), ('CORE', [13, 5, 2], '核心输入'),
                 ('POWER', [19, 5, 2], '供能'), ('MATERIAL', [35, 5, 2], '装配材料输入'),
                 ('ROBOT', [41, 5, 2], '成品机器人输出'), ('SCRAP', [47, 5, 2], '残余输出')]
    ports = front_interfaces(a, controller, ports_raw)
    return {'key': 'i11', 'name': 'i11-nanobot-array-v5', 'title': brief['title'], 'size': [a.w, a.h, a.d],
            'controller': controller, 'ports': ports, 'paths': [],
            'zones': [{'name': '双线装配床', 'kind': 'parallel_lines', 'min': [4, 2, 12], 'max': [50, 24, 35], 'pos': [27, 24, 22], 'role': '两条并行纳米装配线', 'service_face': '前后两侧'},
                      {'name': '六座跨线龙门', 'kind': 'gantry', 'min': [8, 7, 10], 'max': [51, 24, 35], 'pos': [29, 24, 22], 'role': '核心植入与机械臂装配', 'service_face': '上下两侧'},
                      {'name': '汇合检测塔', 'kind': 'inspection_tower', 'min': [45, 8, 17], 'max': [52, 28, 27], 'pos': [49, 28, 22], 'role': '成品检测与分流', 'service_face': '东侧'},
                      {'name': '高位吊运梁', 'kind': 'crane', 'min': [6, 27, 10], 'max': [50, 33, 35], 'pos': [28, 33, 22], 'role': '工位维护与载具转运', 'service_face': '顶部'}],
            'links': [], 'brief': brief, 'description': 'I11 重制为双线龙门装配厅：两条平行输送床由六座跨线龙门完成不同工序，末端合流进入透明检测塔，高位吊运梁负责维护和载具转运。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}


def i12():
    brief = {'id': 'I12', 'title': '纳米自组织编程舱', 'minimum_wdh': [25, 29, 29],
             'catalog_minimum_wdh': [25, 29, 29], 'form': '三舱数据穹顶',
             'flow': '程序模板分发、三舱并行编程、中央自组织、数据回写'}
    a = common(brief, (43, 37, 43))
    # 三个独立编程舱呈三角布置，中央是低位数据井，顶部穹顶是回写节点。
    pods = [(11, 10, 'hk3gtl:voltage_machine_casing_hdv'), (31, 10, 'hk3gtl:voltage_machine_casing_hcv'), (21, 29, 'hk3gtl:voltage_machine_casing_hbv')]
    for x, z, shell in pods:
        a.box((x - 7, 4, z - 6), (x + 7, 20, z + 6), shell, True)
        a.box((x - 5, 6, z - 4), (x + 5, 18, z + 4), GLASS, True)
        a.box((x - 2, 8, z - 2), (x + 2, 16, z + 2), STAR, True)
        a.line((x, 7, z), (x, 19, z), ARM)
        a.box((x - 6, 20, z - 5), (x + 6, 21, z + 5), RAIL)
    # 中央数据井与三条桥相连，保留大面积可读留白。
    a.ring((21, 8, 20), 9, 9, INJECT, 2)
    a.ring((21, 14, 20), 7, 7, FIELD, 1)
    a.box((18, 4, 17), (24, 25, 23), PANEL, True)
    a.box((20, 6, 19), (22, 23, 21), GLASS2, True)
    a.line((21, 6, 20), (21, 24, 20), STAR)
    for x, z in ((11, 10), (31, 10), (21, 29)):
        a.line((21, 8, 20), (x, 8, z), PIPE, 2)
        a.line((21, 14, 20), (x, 14, z), RIB)
    # 顶部数据穹顶与落地四柱，取和谐之眼/空间站的穹顶语言。
    for x in range(11, 32):
        for z in range(10, 31):
            dx, dz = x - 21, z - 20
            if dx * dx + dz * dz <= 100:
                y = 26 + round(7 * (1 - (dx * dx + dz * dz) / 100) ** 0.5)
                a.set(x, y, z, RIB if abs(dx) in (0, 5, 10) or abs(dz) in (0, 5, 10) else GLASS)
    for x, z in ((11, 10), (31, 10), (11, 30), (31, 30)):
        a.line((x, 1, z), (x, 26, z), BASE)
    a.box((5, 1, 1), (37, 3, 5), PANEL)
    controller = [21, 5, 2]
    ports_raw = [('TEMPLATE', [8, 5, 2], '程序模板输入'), ('SAMPLE', [14, 5, 2], '纳米样本输入'),
                 ('POWER', [18, 5, 2], '供能'), ('DATA', [24, 5, 2], '数据输入'),
                 ('NANITE', [30, 5, 2], '纳米单元输出'), ('RETURN', [36, 5, 2], '回写数据输出')]
    ports = front_interfaces(a, controller, ports_raw)
    return {'key': 'i12', 'name': 'i12-nanobot-programming-v5', 'title': brief['title'], 'size': [a.w, a.h, a.d],
            'controller': controller, 'ports': ports, 'paths': [],
            'zones': [{'name': '三组独立编程舱', 'kind': 'programming_pods', 'min': [4, 4, 24], 'max': [38, 21, 35], 'pos': [21, 21, 20], 'role': '三路并行编程与校准', 'service_face': '外侧'},
                      {'name': '中央数据井', 'kind': 'data_well', 'min': [12, 4, 11], 'max': [30, 25, 29], 'pos': [21, 25, 20], 'role': '自组织核心与数据汇聚', 'service_face': '四周'},
                      {'name': '高位回写穹顶', 'kind': 'dome', 'min': [11, 26, 10], 'max': [31, 33, 30], 'pos': [21, 33, 20], 'role': '程序回写与远程维护', 'service_face': '顶部'}],
            'links': [], 'brief': brief, 'description': 'I12 重制为三舱数据穹顶：三组独立编程舱围绕中央数据井呈三角布局，三条实体数据桥汇聚到高位回写穹顶，形成实验设施而非横向方盒。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}


def i13():
    brief = {'id': 'I13', 'title': '崩坏抗性包覆阵列', 'minimum_wdh': [25, 37, 29],
             'catalog_minimum_wdh': [25, 37, 29], 'form': '放射式包覆转盘与固化塔',
             'flow': '基板上料、六工位包覆、环形回流、固化检测与成品分流'}
    a = common(brief, (49, 43, 47))
    # 中央旋转处理盘：六个处理臂从中心放射，轮廓与 I09/I11/I12 完全不同。
    a.ring((24, 8, 23), 14, 14, BASE, 2)
    a.ring((24, 14, 23), 11, 11, RIB, 2)
    a.ring((24, 20, 23), 8, 8, FIELD, 1)
    a.box((20, 4, 19), (28, 25, 27), POWER, True)
    a.box((22, 6, 21), (26, 23, 25), GLASS, True)
    a.box((23, 8, 22), (25, 21, 24), GLASS2, True)
    a.line((24, 6, 23), (24, 27, 23), STAR)
    for i in range(6):
        import math
        ang = i * math.tau / 6
        ex, ez = round(24 + 14 * math.cos(ang)), round(23 + 14 * math.sin(ang))
        mx, mz = round(24 + 8 * math.cos(ang)), round(23 + 8 * math.sin(ang))
        a.line((mx, 10, mz), (ex, 10, ez), PIPE, 2)
        a.line((mx, 16, mz), (ex, 16, ez), INJECT)
        a.box((ex - 3, 6, ez - 3), (ex + 3, 21, ez + 3),
              [POWER, 'hk3gtl:voltage_machine_casing_hdv', 'hk3gtl:voltage_machine_casing_hcv', FIELD, PANEL, PRECISION][i], True)
        a.box((ex - 2, 9, ez - 2), (ex + 2, 18, ez + 2), GLASS2, True)
        a.box((ex - 1, 12, ez - 1), (ex + 1, 16, ez + 1), ARM, True)
    # 东侧独立固化/测厚塔与西侧上料廊。
    a.box((38, 5, 15), (46, 30, 31), PRECISION, True)
    a.box((40, 7, 17), (44, 26, 29), GLASS, True)
    a.box((41, 10, 19), (43, 23, 27), STAR, True)
    a.box((2, 6, 17), (10, 20, 29), PANEL, True)
    a.box((4, 8, 8), (8, 18, 27), RAIL)
    a.line((8, 14, 23), (12, 14, 23), PIPE, 2)
    a.box((10, 27, 8), (38, 29, 38), RAIL)
    for x in (13, 21, 29, 37):
        a.box((x, 29, 8), (x + 1, 35, 38), BASE)
    a.box((18, 31, 18), (30, 34, 28), POWER, True)
    a.box((22, 34, 21), (26, 37, 25), GLASS2, True)
    controller = [24, 5, 2]
    ports_raw = [('SUBSTRATE', [7, 5, 2], '基板输入'), ('COATING', [13, 5, 2], '包覆介质输入'),
                 ('POWER', [19, 5, 2], '供能'), ('PLASMA', [29, 5, 2], '等离子输入'),
                 ('PRODUCT', [35, 5, 2], '成品输出'), ('REJECT', [41, 5, 2], '残液与不合格件输出')]
    ports = front_interfaces(a, controller, ports_raw)
    return {'key': 'i13', 'name': 'i13-coating-array-v5', 'title': brief['title'], 'size': [a.w, a.h, a.d],
            'controller': controller, 'ports': ports, 'paths': [],
            'zones': [{'name': '六工位放射式包覆盘', 'kind': 'carousel', 'min': [7, 4, 6], 'max': [41, 21, 40], 'pos': [24, 21, 23], 'role': '六路喷涂、浸润与能量包覆', 'service_face': '环向'},
                      {'name': '东侧固化测厚塔', 'kind': 'curing_tower', 'min': [38, 5, 15], 'max': [46, 30, 31], 'pos': [42, 30, 23], 'role': '固化、测厚与分流', 'service_face': '东侧'},
                      {'name': '西侧基板上料廊', 'kind': 'feed_gallery', 'min': [2, 6, 8], 'max': [10, 20, 29], 'pos': [6, 20, 23], 'role': '基板清洗与上料', 'service_face': '西侧'},
                      {'name': '高位维护吊桥', 'kind': 'maintenance_bridge', 'min': [10, 27, 8], 'max': [38, 37, 38], 'pos': [24, 37, 23], 'role': '喷头更换与回流管线维护', 'service_face': '顶部'}],
            'links': [], 'brief': brief, 'description': 'I13 重制为放射式包覆转盘：六个不同材料的处理工位围绕中央透明处理腔展开，西侧上料、东侧固化测厚，高位吊桥承担维护与回流。',
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}


if __name__ == '__main__':
    for data, out, key, checks in [
        (i09(), ROOT / 'deliveries/I09_魂钢前驱体配制釜_自由设计预览', 'i09', ['竖向化工树与双塔计量站', '接口前方净空']),
        (i11(), ROOT / 'deliveries/I11_纳米机器人装配阵列_自由设计预览', 'i11', ['双线龙门装配厅', '接口前方净空']),
        (i12(), ROOT / 'deliveries/I12_纳米自组织编程舱_自由设计预览', 'i12', ['三舱数据穹顶', '接口前方净空']),
        (i13(), ROOT / 'deliveries/I13_崩坏抗性包覆阵列_自由设计预览', 'i13', ['放射式包覆转盘与固化塔', '接口前方净空']),
    ]:
        package(data, out, 'i07', checks)
