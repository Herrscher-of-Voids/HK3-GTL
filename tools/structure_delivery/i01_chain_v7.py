# -*- coding: utf-8 -*-
"""I01 四阶采集群：固定控制坞，沿东南加建，不移动或改写旧阶方块。

2026-10-14：液态旋吸塔→固态晶体夹持叉→气态采集鳍→能量态场翼。
仅生成外观候选数据；不改机器、配方、旧归档或游戏实例。
"""
import collections
import copy
import hashlib
import json
import math

from redesign69_geometry import Build
from i09_i13_v6_common import zone, route, PORT, DIAMOND

WHITE = 'gtceu:clean_machine_casing'
BASE = 'gtceu:solid_machine_casing'
PIPE = 'gtceu:steel_pipe_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
PANEL = 'gtceu:advanced_computer_casing'
GLASS = 'gtceu:tempered_glass'
ENERGY = 'gtlcore:rhenium_reinforced_energy_glass'
RIB = 'gtlcore:lafium_mechanical_casing'
POWER = 'gtceu:high_power_casing'
SHELLS = {1: 'hk3gtl:voltage_machine_casing_hbv',
          2: 'hk3gtl:voltage_machine_casing_hdv',
          3: 'hk3gtl:voltage_machine_casing_civ',
          4: 'hk3gtl:voltage_machine_casing_qcv'}
SIZES = {1: (17, 33, 17), 2: (25, 37, 25),
         3: (37, 45, 37), 4: (53, 61, 53)}
CONTROLLER = (8, 3, 1)
PURPOSES = [('INPUT', '采集介质输入候选'), ('COOLANT', '冷却液输入候选'),
            ('POWER', '电能输入候选'), ('OUTPUT', '当阶采集物输出候选'),
            ('RECOVERY', '介质回收输出候选'), ('RETURN', '旁路回流候选')]


class Additive(Build):
    """保护已建方块与已声明维护净空，新增构件可以贴合旧设备。"""
    def __init__(self, stage, previous=None):
        w, h, d = SIZES[stage]
        phase = ('液态', '固态', '气态', '能量态')[stage-1]
        super().__init__({'id': 'I01-%d' % stage,
                          'title': '%d阶崩坏能采集塔 · %s' % (stage, phase),
                          'minimum_wdh': [w, d, h],
                          'form': '沿东南方向逐级长出的采集群落',
                          'flow': '采集介质→当阶处理→回收或输出'})
        self.stage = stage
        self.previous = previous
        self.frozen = {}
        self.protected = set()
        self.overlaps_preserved = 0
        if previous:
            self.frozen = {tuple(q['pos']): q['state'] for q in previous['blocks']}
            self.b.update(self.frozen)
            self.zones = copy.deepcopy(previous['zones'])
            self.paths = copy.deepcopy(previous['paths'])
            self.links = copy.deepcopy(previous['links'])
            for state in self.frozen.values():
                self.roles[state].add(state)
            for path in self.paths:
                self._protect(path['min'], path['max'])

    def _protect(self, lo, hi):
        for x in range(lo[0], hi[0]+1):
            for y in range(lo[1], hi[1]+1):
                for z in range(lo[2], hi[2]+1):
                    self.protected.add((x, y, z))

    def path(self, name, lo, hi):
        self.paths.append({'name': name, 'min': list(lo), 'max': list(hi)})
        self._protect(lo, hi)

    def set(self, x, y, z, material):
        pos = (round(x), round(y), round(z))
        if pos in self.frozen:
            self.overlaps_preserved += 1
            return
        if pos in self.protected:
            return
        super().set(*pos, material)


def disk(cx, cz, radius):
    return {(x, z) for x in range(cx-radius, cx+radius+1)
            for z in range(cz-radius, cz+radius+1)
            if (x-cx)**2 + (z-cz)**2 <= radius**2}


def vessel(a, cx, cz, profile, shell, glass, bands):
    """根据相邻层体积构成闭合曲面，肩部和底盖也有完整实体。"""
    disks = {y: disk(cx, cz, r) for y, r in profile.items()}
    for y, cells in disks.items():
        for x, z in cells:
            edge = any((x+dx, z+dz) not in cells
                       for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            if edge or (x, z) not in disks.get(y-1, set()) or (x, z) not in disks.get(y+1, set()):
                material = shell if y in bands or abs(x-cx) <= 1 else glass
                a.set(x, y, z, material)


def curve(a, points, material, width=3):
    for p, q in zip(points, points[1:]):
        a.line(p, q, material, width)


def bearer(a, cx, cz, radius, shell):
    """三格厚的局部鞍座连接，不铺连续整板。"""
    for x, z in disk(cx, cz, radius):
        if abs(x-cx) <= 1 or abs(z-cz) <= 1 or (x-cx)**2+(z-cz)**2 >= (radius-2)**2:
            a.box((x, 0, z), (x, 1, z), BASE)
    for x, z in ((cx-radius+1, cz), (cx+radius-1, cz), (cx, cz+radius-1)):
        a.box((x-1, 2, z-1), (x+1, 4, z+1), shell)


def dock(a):
    # 所有接口和主控位于同一块白色正面，北侧保留三格高连续净空。
    a.path('固定北向控制坞检修带', (0, 1, 0), (16, 4, 0))
    a.path('一阶前场观察入口', (7, 1, 3), (9, 4, 6))
    a.box((0, 0, 0), (16, 0, 2), GRATE)
    # 端墙拆成六个独立接口门框与两根边柱，避免用一面实心大板伪造机壳。
    for x in (0, 16):
        a.box((x, 1, 1), (x, 4, 2), WHITE)
    for x in (2, 4, 6, 10, 12, 14):
        a.box((x-1, 1, 1), (x+1, 1, 2), WHITE)
        a.box((x-1, 4, 1), (x+1, 4, 2), WHITE)
        a.box((x-1, 1, 2), (x-1, 4, 2), RIB)
        a.box((x+1, 1, 2), (x+1, 4, 2), RIB)
    a.box((7, 1, 1), (9, 4, 1), SHELLS[1])
    for x in (7, 9):
        a.box((x, 2, 1), (x, 4, 1), WHITE)
    for y in (2, 4):
        a.box((7, y, 1), (9, y, 1), WHITE)
    for x in (2, 4, 6, 10, 12, 14):
        a.box((x, 2, 1), (x, 4, 1), SHELLS[1])
        a.box((x, 2, 2), (x, 4, 2), SHELLS[1])
        a.set(x, 3, 1, PORT)
    a.set(*CONTROLLER, DIAMOND)
    a.box((7, 0, 3), (9, 0, 7), GRATE)
    route(a, '固定控制坞', '液态旋吸塔',
          [(12, 1, 2), (12, 1, 7), (8, 1, 7), (8, 1, 11)], PIPE)


def finish(a, description, references):
    ports = [{'id': key, 'pos': [x, 3, 1], 'face': 'north', 'purpose': purpose}
             for x, (key, purpose) in zip((2, 4, 6, 10, 12, 14), PURPOSES)]
    blocks = [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]
    preserved = len(a.frozen)-1 if a.previous else 0
    fingerprint = hashlib.sha256(json.dumps(
        [(p, s) for p, s in sorted(a.b.items()) if p != CONTROLLER],
        separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
    return {'key': a.brief['id'].lower(), 'name': a.brief['id'].lower()+'-collector-v7',
            'title': a.brief['title'], 'size': [a.w, a.h, a.d],
            'controller': list(CONTROLLER), 'ports': ports, 'paths': a.paths,
            'zones': a.zones, 'links': a.links, 'brief': a.brief,
            'description': description, 'references': references,
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': blocks,
            'upgrade_contract': {'previous': a.previous['key'] if a.previous else None,
                                 'fixed_local_anchor': list(CONTROLLER),
                                 'preserved_non_controller_blocks': preserved,
                                 'added_blocks': len(a.b)-len(a.frozen),
                                 'coordinate_shift': [0, 0, 0],
                                 'non_controller_sha256': fingerprint},
            'paste_anchor': list(CONTROLLER), 'recommended_bottom_y': -60}


def i01_1():
    a = Additive(1)
    dock(a)
    a.path('一阶后侧泵座维护带', (4, 1, 16), (12, 3, 16))
    bearer(a, 8, 11, 5, SHELLS[1])
    profile = {y: (2 if y in (5, 21) else 3 if y in (6, 7, 19, 20) else 4)
               for y in range(5, 22)}
    vessel(a, 8, 11, profile, SHELLS[1], GLASS, (5, 8, 17, 21))
    a.box((8, 5, 11), (8, 28, 11), PIPE)
    for y in (10, 14, 18):
        a.box((6, y, 10), (10, y, 12), GEAR)
    # 三片粗螺旋吸流爪从釜肩展开，再旋向高处中心；没有水平大圈。
    for angle in (0, math.pi*2/3, math.pi*4/3):
        points = []
        for t in range(11):
            radius = 6 if t < 4 else 6-(t-3)*.58
            theta = angle+t*.10
            x = min(15, max(1, round(8+radius*math.cos(theta))))
            z = min(15, max(5, round(11+radius*math.sin(theta))))
            points.append((x, 18+t, z))
        curve(a, points, WHITE)
        curve(a, [(p[0], p[1], p[2]) for p in points[2:9]], SHELLS[1], 1)
    vessel(a, 8, 11, {29: 2, 30: 2, 31: 1, 32: 1}, RIB, ENERGY, (29, 32))
    a.box((8, 28, 11), (8, 31, 11), POWER)
    # 小型回流分离器、连续散热齿与后侧泵座让一阶已有完整液态工艺。
    a.box((13, 0, 6), (16, 2, 13), BASE)
    vessel(a, 14, 9, {3: 1, 4: 2, 5: 2, 6: 2, 7: 2, 8: 1}, SHELLS[1], GLASS, (3, 8))
    for z in (7, 10, 13):
        a.box((13, 9, z), (15, 11, z), VENT)
    a.box((13, 8, 7), (15, 8, 13), PIPE)
    route(a, '液态旋吸塔', '回流分离器', [(11, 13, 11), (14, 13, 11), (14, 8, 11)], PIPE)
    route(a, '回流分离器', '液态旋吸塔', [(14, 4, 7), (11, 4, 7), (11, 4, 11)], PIPE)
    a.box((4, 0, 15), (12, 0, 16), GRATE)
    zone(a, '液态旋吸塔', (2, 0, 6), (14, 32, 16), '三爪旋吸、曲面凝结釜、内轴回流', 'liquid_collector')
    zone(a, '回流分离器', (12, 0, 6), (16, 13, 13), '凝结液分离、冷却与回流', 'condenser')
    return finish(a, '深蓝液态旋吸塔：白色三爪在釜肩张开后旋向顶端，透明曲面釜露出内轴；右侧小分离器与散热齿接入回流。控制坞固定在北侧，为以后升级保留前场。',
                  ['GTLcore LARGE_CHEMICAL_PLANT：反应内核、观察窗与外围管带',
                   'GTCEu LARGE_CHEMICAL_REACTOR：耐蚀壳、内管与热区分工；旋吸爪为原创构图'])


def i01_2():
    a = Additive(2, i01_1())
    a.path('二阶晶体分选南侧维护带', (14, 1, 24), (24, 4, 24))
    bearer(a, 19, 19, 5, SHELLS[2])
    a.box((14, 0, 24), (24, 0, 24), GRATE)
    curve(a, [(8, 0, 11), (19, 0, 11), (19, 0, 19)], BASE, 3)
    vessel(a, 19, 19, {y: 3 if 7 <= y <= 15 else 2 for y in range(5, 18)},
           SHELLS[2], ENERGY, (5, 9, 17))
    a.box((18, 3, 18), (20, 6, 20), GEAR)
    a.box((19, 7, 19), (19, 26, 19), POWER)
    # 两支弯曲夹持叉围绕晶体柱，收拢顶部，二阶是独立工艺而非放大一阶。
    for sign in (-1, 1):
        points = [(19+sign*4, 3, 19), (19+sign*4, 12, 19),
                  (19+sign*4, 21, 19), (19+sign*3, 29, 19),
                  (19+sign*2, 35, 19)]
        curve(a, points, WHITE)
        a.box((19+sign*4, 14, 18), (19+sign*4, 22, 20), SHELLS[2])
        a.box((19+sign*2-1, 34, 18), (19+sign*2+1, 36, 20), RIB)
        a.line((19+sign*4, 25, 19), (19, 25, 19), GEAR)
    vessel(a, 19, 19, {23: 2, 24: 3, 25: 3, 26: 2, 27: 1}, SHELLS[2], ENERGY, (23, 27))
    a.box((19, 28, 19), (19, 33, 19), PIPE)
    # 偏置低位晶种送料螺杆，顶面齿形纹理与夹持叉分别识别输送/约束。
    a.box((18, 0, 7), (24, 2, 13), BASE)
    a.box((19, 3, 8), (23, 7, 12), SHELLS[2], True)
    a.box((20, 8, 9), (22, 9, 11), GEAR)
    route(a, '晶种送料螺杆', '固态夹持叉', [(21, 6, 12), (21, 6, 16), (19, 6, 16)], PIPE)
    route(a, '液态旋吸塔', '固态夹持叉', [(12, 16, 11), (19, 16, 11), (19, 16, 16)], PIPE)
    zone(a, '固态夹持叉', (14, 0, 14), (24, 36, 24), '晶体柱、双叉夹持、分选与收束', 'solid_collector')
    zone(a, '晶种送料螺杆', (18, 0, 7), (24, 9, 13), '固态晶种送料及计量', 'feed')
    return finish(a, '一阶完整保留；东南增加青绿色双叉晶体分选塔，白色双叉绕开晶体柱，在高处夹持闭合。偏置晶种送料机与一阶回流管相连，形成液态先级、固态后级的递进轮廓。',
                  ['GTLcore NANO_FORGE_1：细长核心、分段约束与空气内核',
                   'GTLcore PCB_FACTORY：不同高度的分离工段与少量连接管'])


def i01_3():
    a = Additive(3, i01_2())
    a.path('三阶气流鳍南侧维护带', (25, 1, 36), (36, 4, 36))
    bearer(a, 29, 29, 7, SHELLS[3])
    curve(a, [(19, 0, 19), (29, 0, 19), (29, 0, 29)], BASE, 3)
    a.box((25, 0, 36), (36, 0, 36), GRATE)
    vessel(a, 29, 29, {y: 4 if 7 <= y <= 16 else 3 for y in range(5, 20)},
           SHELLS[3], GLASS, (5, 10, 19))
    a.box((28, 2, 28), (30, 22, 30), PIPE)
    a.box((27, 20, 27), (31, 23, 31), GEAR)
    # 两片三格厚的气流采集鳍，高低错开且有曲线前缘和机械百叶内面。
    for y in range(4, 44):
        t = (y-4)/39
        outside = round(29+6*math.sin(t*math.pi*.82))
        inside = max(27, outside-3)
        for u in range(inside, outside+1):
            a.box((u, y, 28), (u, y, 30), SHELLS[3] if y % 7 else WHITE)
        if y % 4 == 0 and 12 <= y <= 36:
            a.box((inside-2, y, 26), (outside, y+1, 27), VENT)
    for y in range(4, 37):
        t = (y-4)/32
        outside = round(29+6*math.sin(t*math.pi*.85))
        a.box((28, y, outside-3), (30, y, outside), SHELLS[3] if y % 6 else WHITE)
        if y % 4 == 0 and 12 <= y <= 32:
            a.box((26, y, outside-2), (27, y+1, outside), VENT)
    a.box((31, 41, 28), (33, 44, 30), RIB)
    a.box((28, 35, 31), (30, 38, 33), RIB)
    # 高位气流弧管跨在旧阶后方，保留旧晶体叉的完整剪影。
    curve(a, [(29, 22, 29), (29, 26, 25), (25, 29, 25),
              (25, 31, 19), (22, 31, 19)], WHITE)
    route(a, '气态采集鳍', '固态夹持叉', [(29, 10, 25), (29, 10, 20), (24, 10, 20)], PIPE)
    route(a, '气态采集鳍', '气液分离回流', [(29, 6, 25), (25, 6, 25), (25, 6, 13), (23, 6, 13)], PIPE)
    zone(a, '气态采集鳍', (22, 0, 22), (36, 44, 36), '双曲面厚鳍、机械百叶、气液分离腔', 'gas_collector')
    return finish(a, '前两阶原样保留；东南增加蓝青色高低双采集鳍，外缘弯曲、内侧分段百叶，脚部连接透明气液分离腔。高位弧形气流管把新工段接回晶体叉，三阶形成沿对角线抬升的采集谱系。',
                  ['GTCEu HPCA：组件和连续排热面分工',
                   'GTLcore PCB_FACTORY：高低错位工段与外围回流；曲面厚鳍为原创'])


def i01_4():
    a = Additive(4, i01_3())
    bearer(a, 41, 41, 7, SHELLS[4])
    curve(a, [(29, 0, 29), (41, 0, 29), (41, 0, 41)], BASE, 3)
    a.box((37, 0, 52), (49, 0, 52), GRATE)
    a.path('四阶能量场南侧维护带', (37, 1, 52), (49, 4, 52))
    # 细颈能量中继连接底座与上方场核，三组厚弧翼有各自承重脚。
    vessel(a, 41, 41, {y: 2 if y < 23 else 3 for y in range(5, 30)},
           SHELLS[4], ENERGY, (5, 13, 22, 29))
    a.box((40, 3, 40), (42, 34, 42), POWER)
    vessel(a, 41, 41, {y: 3 if y in (30, 31, 43, 44) else 5 for y in range(30, 45)},
           RIB, ENERGY, (30, 36, 44))
    a.box((40, 35, 40), (42, 41, 42), SHELLS[4])
    wings = [([(49, 2, 41), (50, 18, 41), (50, 35, 41), (48, 48, 41),
               (45, 55, 41), (41, 59, 41)], (50, 41)),
             ([(41, 2, 49), (41, 17, 50), (41, 31, 50), (41, 43, 48),
               (41, 52, 45), (41, 58, 41)], (41, 50)),
             ([(35, 2, 35), (33, 16, 33), (33, 29, 33), (35, 43, 35),
               (38, 52, 38), (41, 57, 41)], (34, 34))]
    for index, (points, foot) in enumerate(wings):
        a.box((foot[0]-2, 0, foot[1]-2), (foot[0]+2, 2, foot[1]+2), BASE)
        curve(a, points, WHITE, 5)
        curve(a, [(p[0], p[1], p[2]) for p in points[1:]], SHELLS[4], 3)
        for p in points[1:4]:
            a.box((p[0]-2, p[1]-1, p[2]-2), (p[0]+2, p[1]+1, p[2]+2), RIB, True)
        curve(a, [points[2], (41, 38+index*2, 41)], POWER, 3)
    # 芯顶透镜与翼冠共同汇聚，三翼高度不同，保持开放的非圆环焦点。
    vessel(a, 41, 41, {52: 3, 53: 4, 54: 4, 55: 3, 56: 2, 57: 1},
           SHELLS[4], ENERGY, (52, 57))
    a.box((41, 44, 41), (41, 53, 41), PIPE)
    # 放射供场总线沿后场连接三阶气流鳍，旧三阶最高轮廓保持可见。
    route(a, '气态采集鳍', '能量场核', [(35, 24, 29), (41, 24, 29), (41, 24, 36)], POWER)
    route(a, '能量场核', '能量回流与抽取', [(44, 14, 41), (47, 14, 41), (47, 5, 41)], PIPE)
    a.box((45, 0, 31), (51, 2, 36), BASE)
    a.box((46, 3, 32), (50, 8, 35), SHELLS[4], True)
    for x in (46, 48, 50):
        a.box((x, 9, 32), (x, 12, 35), VENT)
    route(a, '能量回流与抽取', '场翼冷却组', [(47, 5, 41), (47, 5, 35)], PIPE)
    zone(a, '能量态场翼', (31, 0, 31), (52, 60, 52), '三片厚弧翼、悬置场核、芯顶透镜和外围回流', 'energy_collector')
    zone(a, '场翼冷却组', (45, 0, 31), (51, 12, 36), '约束场散热与能量回流抽取', 'cooling')
    return finish(a, '前三阶坐标与状态逐格保留；末端新建紫蓝色三片厚弧场翼，白色外缘从独立承重脚向不同高度弯拢，紫色透明场核悬在相互连接的功率桥之间。四阶从北侧控制坞到后场能量冠形成连续、上升的工业群落。',
                  ['GTLsupb MICROCOSM_FOUNDRY / MicrocosmPatternLayers：核心、弧架和空气间隙',
                   'GTLsupb RANK_DERIVATION_ASSEMBLY_MATRIX：核心与外围场约束的层级',
                   '不复制终局阵列尺寸；厚弧场翼与逐阶对角生长为原创工程构图'])


def validate_chain():
    """检查实际实体边界、六面连通、接口和逐格升级，不替代建筑审美。"""
    results, previous = [], None
    offsets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for fn in (i01_1, i01_2, i01_3, i01_4):
        data = fn()
        blocks = {tuple(q['pos']): q['state'] for q in data['blocks']}
        lo = [min(p[i] for p in blocks) for i in range(3)]
        hi = [max(p[i] for p in blocks) for i in range(3)]
        assert lo == [0, 0, 0] and [hi[i]+1 for i in range(3)] == data['size'], (data['key'], lo, hi)
        remain = set(blocks)
        todo = collections.deque([next(iter(remain))])
        remain.remove(todo[0])
        while todo:
            p = todo.popleft()
            for delta in offsets:
                q = tuple(p[i]+delta[i] for i in range(3))
                if q in remain:
                    remain.remove(q)
                    todo.append(q)
        assert not remain, (data['key'], '不连通', len(remain))
        assert blocks[CONTROLLER] == DIAMOND
        for port in data['ports']:
            assert blocks[tuple(port['pos'])] == PORT
        for path in data['paths']:
            assert not any(all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3)) for p in blocks), path['name']
        mismatches = [] if not previous else [p for p, s in previous.items() if p != CONTROLLER and blocks.get(p) != s]
        assert not mismatches, (data['key'], '升级改写', mismatches[:5])
        results.append({'key': data['key'], 'size': data['size'], 'blocks': len(blocks),
                        'inherited_non_controller': len(previous)-1 if previous else 0,
                        'upgrade_mismatches': len(mismatches), 'connected': True,
                        'paths_clear': True, 'ports': len(data['ports'])})
        previous = blocks
    return results


if __name__ == '__main__':
    print(json.dumps(validate_chain(), ensure_ascii=False, indent=2))
