# -*- coding: utf-8 -*-
"""I01 V8：固定竖轴与正交工段的四阶原位扩建，导出时平移至局部原点。

变更记录 #1 2026-10-14：取消对角生长；液态塔→双晶体塔→四吸风塔→八柱能量冠。
仅生成独立建筑候选；旧 V7、生产源码、实例、配方和机器定义均不改动。
"""
import collections
import copy
import hashlib
import json

from redesign69_geometry import Build
from i09_i13_v6_common import PORT, DIAMOND
from structure_size_baseline import require

WHITE = 'gtceu:clean_machine_casing'
BASE = 'gtceu:solid_machine_casing'
PIPE = 'gtceu:steel_pipe_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
PANEL = 'gtceu:advanced_computer_casing'
GLASS = 'gtceu:tempered_glass'
ENERGY = 'gtlcore:rhenium_reinforced_energy_glass'
POWER = 'gtceu:high_power_casing'
SHELLS = {1: 'hk3gtl:voltage_machine_casing_hbv',
          2: 'hk3gtl:voltage_machine_casing_hdv',
          3: 'hk3gtl:voltage_machine_casing_civ',
          4: 'hk3gtl:voltage_machine_casing_qcv'}
SIZES = {1: (17, 33, 17), 2: (25, 37, 25), 3: (37, 45, 37), 4: (53, 81, 53)}
CONTROLLER = (0, 3, -7)
PORT_X = (-6, -4, -2, 2, 4, 6)
PURPOSES = [('INPUT', '采集介质输入候选'), ('COOLANT', '冷却液输入候选'),
            ('POWER', '电能输入候选'), ('OUTPUT', '当阶采集物输出候选'),
            ('RECOVERY', '介质回收输出候选'), ('RETURN', '旁路回流候选')]


def add(p, q):
    return [p[i]+q[i] for i in range(3)]


class SignedBuild(Build):
    """固定 signed 原地坐标；旧实体及旧维护净空是禁止改写的区域。"""
    def __init__(self, stage, previous=None):
        w, h, d = SIZES[stage]
        phase = ('液态', '固态', '气态', '能量态')[stage-1]
        super().__init__({'id': 'I01-%d' % stage,
                          'title': '%d阶崩坏能采集塔 · %s' % (stage, phase),
                          'minimum_wdh': [w, d, h],
                          'form': '同一竖直主轴与南北东西正交增建的采集设施',
                          'flow': '液态凝结→固态压榨→气态吸风→能量态约束采集'})
        self.stage, self.previous = stage, previous
        self.frozen, self.protected = {}, set()
        if previous:
            origin = previous['signed_origin']
            self.frozen = {tuple(add(q['pos'], origin)): q['state'] for q in previous['blocks']}
            self.b.update(self.frozen)
            for state in self.frozen.values():
                self.roles[state].add(state)
            for collection in ('zones', 'paths', 'links'):
                setattr(self, collection, copy.deepcopy(previous[collection]))
                for item in getattr(self, collection):
                    for field in ('min', 'max', 'pos'):
                        if field in item:
                            item[field] = add(item[field], origin)
                    if 'route' in item:
                        item['route'] = [add(p, origin) for p in item['route']]
            for path in self.paths:
                self.protect(path['min'], path['max'])
        # 主控前的中间直通维护轴逐阶向北延伸；两侧工段可以更靠北。
        self.path('北向主控直通维护轴 · 第%d阶' % stage,
                  (-7, 1, -d//2+1), (7, 4, -8))

    def protect(self, lo, hi):
        self.protected.update((x, y, z) for x in range(lo[0], hi[0]+1)
                              for y in range(lo[1], hi[1]+1) for z in range(lo[2], hi[2]+1))

    def path(self, name, lo, hi):
        self.paths.append({'name': name, 'min': list(lo), 'max': list(hi)})
        self.protect(lo, hi)

    def set(self, x, y, z, material):
        p = (round(x), round(y), round(z))
        w, h, d = SIZES[self.stage]
        assert -w//2+1 <= p[0] <= w//2 and 0 <= p[1] < h and -d//2+1 <= p[2] <= d//2, p
        if p in self.frozen or p in self.protected:
            return
        self.b[p] = material
        self.roles[material].add(material)

    def line(self, lo, hi, material, width=1):
        assert width == 1, '有符号坐标的粗梁须显式 box，不使用裁剪宽度'
        super().line(lo, hi, material, width=1)

    def zone(self, name, lo, hi, role, kind='equipment'):
        self.zones.append({'name': name, 'min': list(lo), 'max': list(hi),
                           'pos': [(lo[0]+hi[0])//2, hi[1], (lo[2]+hi[2])//2],
                           'role': role, 'kind': kind, 'service_face': '工段外侧'})

    def route(self, source, target, points, material=PIPE):
        for p, q in zip(points, points[1:]):
            assert sum(p[i] != q[i] for i in range(3)) <= 1, (p, q)
            self.line(p, q, material)
        self.links.append({'from': source, 'to': target, 'route': [list(p) for p in points]})


def square_ring(a, half, y, material, thickness=1, cx=0, cz=0):
    a.box((cx-half, y, cz-half), (cx+half, y, cz-half+thickness-1), material)
    a.box((cx-half, y, cz+half-thickness+1), (cx+half, y, cz+half), material)
    a.box((cx-half, y, cz-half), (cx-half+thickness-1, y, cz+half), material)
    a.box((cx+half-thickness+1, y, cz-half), (cx+half, y, cz+half), material)


def vessel(a, cx, cz, profile, shell, glass=GLASS):
    """切角方柱闭合壳；横向端盘和四根主脊贯穿透明观察面。"""
    cells = {y: {(x, z) for x in range(cx-r, cx+r+1) for z in range(cz-r, cz+r+1)
                 if abs(x-cx)+abs(z-cz) <= r*3//2+1} for y, r in profile.items()}
    for y, section in cells.items():
        for x, z in section:
            edge = any((x+dx, z+dz) not in section for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            below, above = cells.get(y-1, set()), cells.get(y+1, set())
            cap = (x, z) not in below or (x, z) not in above
            # 半径变化的立面至少厚一格到相邻层边缘，防止封头只能斜向相触。
            if below != section or above != section:
                cap = cap or any((x+dx, z+dz) not in below or (x+dx, z+dz) not in above
                                 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge or cap:
                a.set(x, y, z, shell if cap or abs(x-cx) <= 1 or z == cz else glass)


def dock(a):
    a.box((-8, 0, -8), (8, 0, -5), GRATE)
    a.box((-1, 0, -5), (1, 0, -2), GRATE)
    a.box((-7, 1, -6), (7, 4, -6), BASE)
    a.box((-7, 1, -7), (7, 1, -7), WHITE)
    a.box((-7, 4, -7), (7, 4, -7), WHITE)
    for x in (-7, -1, 1, 7):
        a.box((x, 2, -7), (x, 3, -7), WHITE)
    for x in PORT_X:
        a.box((x, 2, -7), (x, 3, -7), SHELLS[1])
        a.set(x, 3, -7, PORT)
    a.set(*CONTROLLER, DIAMOND)
    a.set(0, 2, -7, WHITE)
    a.path('核心前场观察入口', (-1, 1, -5), (1, 4, -4))


def finish(a, description):
    lo = [min(p[i] for p in a.b) for i in range(3)]
    hi = [max(p[i] for p in a.b) for i in range(3)]
    shift = [-v for v in lo]
    size = [hi[i]-lo[i]+1 for i in range(3)]
    transformed = {}
    for collection in ('zones', 'paths', 'links'):
        transformed[collection] = copy.deepcopy(getattr(a, collection))
        for item in transformed[collection]:
            for field in ('min', 'max', 'pos'):
                if field in item:
                    item[field] = add(item[field], shift)
            if 'route' in item:
                item['route'] = [add(p, shift) for p in item['route']]
    controller = add(CONTROLLER, shift)
    previous_shift = a.previous['coordinate_shift'] if a.previous else [0, 0, 0]
    contract = {'previous': a.previous['key'] if a.previous else None,
                'preserved_non_controller_blocks': len(a.frozen)-1 if a.previous else 0,
                'added_blocks': len(a.b)-len(a.frozen),
                'coordinate_shift': shift,
                'relative_local_shift': [shift[i]-previous_shift[i] for i in range(3)],
                'signed_origin': lo, 'fixed_signed_controller': list(CONTROLLER),
                'inheritance_basis': '逐块减去该阶 paste_anchor 后比较坐标及状态，除主控外禁止替换或移除'}
    blocks = [{'pos': add(p, shift), 'state': s} for p, s in sorted(a.b.items())]
    contract['signed_non_controller_sha256'] = hashlib.sha256(json.dumps(
        [(p, s) for p, s in sorted(a.b.items()) if p != CONTROLLER],
        ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'key': a.brief['id'].lower(), 'name': a.brief['id'].lower()+'-collector-v8',
            'title': a.brief['title'], 'size': size, 'controller': controller,
            'paste_anchor': controller, 'coordinate_shift': shift, 'signed_origin': lo,
            'world_min': lo, 'world_max': hi, 'fixed_signed_controller': list(CONTROLLER),
            'ports': [{'id': key, 'pos': add((x, 3, -7), shift), 'face': 'north', 'purpose': purpose}
                      for x, (key, purpose) in zip(PORT_X, PURPOSES)],
            **transformed, 'brief': a.brief, 'description': description,
            'references': ['ITER Tokamak Complex：中央设备区与侧工艺区共同围绕同一核心；https://www.iter.org/project/projects-underway/tokamak-complex',
                           'NASA Mobile Launcher：竖直服务塔与分层正交服务臂；https://www.nasa.gov/blogs/groundsystems/2017/03/22/first-umbilical-installed-on-mobile-launcher-for-nasas-space-launch-system-and-orion/',
                           'Battersea Power Station：中央空间、双侧体量和外围高构件；https://wilkinsoneyre.com/projects/battersea-power-station',
                           '现实参考记录：logs/i01-orthogonal-v8/reference-study.json；只转译构图，不复制建筑工程或机器功能',
                           'GTLcore LARGE_CHEMICAL_PLANT：内核、观察窗、管带与外围空气层',
                           'GTLcore NANO_FORGE_1：细长核心、分段约束及收口',
                           'GTLsupb RANK_DERIVATION_ASSEMBLY_MATRIX：核心与外围支承/约束的视觉层级；不复制终局材料',
                           '现实工业蒸馏塔、吸风塔及能源设施的正交服务秩序；本方案为原创建筑表达'],
            'role_materials': {k: sorted(v) for k, v in a.roles.items()}, 'blocks': blocks,
            'upgrade_contract': contract, 'recommended_bottom_y': -60,
            'coordinate_conversion': {'signed_to_local': 'local = signed + coordinate_shift',
                                      'local_to_signed': 'signed = local + signed_origin',
                                      'paste': '以同一世界主控位置作锚，world = local - paste_anchor + target_anchor'}}


def i01_1():
    a = SignedBuild(1)
    dock(a)
    a.box((-5, 0, -3), (5, 1, 3), BASE)
    a.box((-3, 0, -5), (3, 1, 6), BASE)
    a.box((-5, 0, 6), (5, 0, 8), GRATE)
    a.path('液态塔后侧泵座维护带', (-4, 1, 7), (4, 3, 8))
    vessel(a, 0, 0, {y: 3 if 5 <= y <= 22 else 2 for y in range(3, 27)}, SHELLS[1])
    a.box((0, 2, 0), (0, 32, 0), PIPE)
    for y in (9, 16, 23):
        a.box((-2, y, -1), (2, y, 1), GEAR)
    for x, z in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        a.box((x, 2, z), (x, 25, z), BASE)
    # 顶部十字集液头与四个正交吸口没有旋转或倾斜生长。
    a.box((-1, 27, -1), (1, 29, 1), GEAR)
    a.box((-6, 30, -1), (6, 31, 1), SHELLS[1])
    a.box((-1, 30, -6), (1, 31, 6), SHELLS[1])
    for x, z in ((-6, 0), (6, 0), (0, -6), (0, 6)):
        a.box((x-1, 30, z-1), (x+1, 32, z+1), BASE, True)
        a.set(x, 31, z, VENT)
    a.box((0, 32, 0), (0, 32, 0), POWER)
    a.box((4, 2, 1), (6, 7, 5), SHELLS[1], True)
    a.box((5, 3, 1), (5, 6, 1), GLASS)
    a.box((5, 8, 2), (5, 11, 4), VENT)
    a.route('中央液态冷凝塔', '右侧回流分离泵', [(3, 13, 0), (5, 13, 0), (5, 13, 3), (5, 7, 3)])
    a.route('固定控制坞', '中央液态冷凝塔', [(6, 2, -6), (6, 2, -3), (0, 2, -3), (0, 2, 0)])
    a.zone('中央液态冷凝塔', (-3, 2, -3), (3, 32, 3), '固定竖轴、液态凝结腔、内部整流节', 'liquid')
    a.zone('四向正交吸口', (-7, 27, -7), (7, 32, 7), '四向进气/集液头，正交十字汇入中央轴', 'intake')
    a.zone('液态回流分离泵', (4, 2, 1), (6, 13, 5), '低位液态分离、冷却及回流', 'buffer')
    return finish(a, '蓝银色细长液态冷凝塔立在固定中央竖轴上；顶部四向正交吸口形成清楚十字冠。透明观察面显示整流节，右后回流泵和前侧固定白框控制坞各有功能。')


def i01_2():
    a = SignedBuild(2, i01_1())
    for side in (-1, 1):
        x = side*10
        a.box((x-2, 0, -12), (x+2, 0, 12), GRATE)
        a.box((x-2, 1, -3), (x+2, 2, 3), BASE)
        vessel(a, x, 0, {y: 2 if 5 <= y <= 21 else 1 for y in range(3, 26)}, SHELLS[2], ENERGY)
        a.box((x, 3, 0), (x, 32, 0), PIPE)
        for y in (8, 15, 22):
            a.box((x-1, y, -1), (x+1, y+1, 1), GEAR)
            a.box((x-2 if side < 0 else x+1, y, -1), (x-1 if side < 0 else x+2, y+2, 1), BASE)
        a.box((x-1, 26, -1), (x+1, 28, 1), GEAR)
        a.box((x-2, 29, -2), (x+2, 30, 2), SHELLS[2], True)
        a.box((x-1, 31, -1), (x+1, 32, 1), WHITE)
        for z in (-10, 10):
            a.box((x-2, 1, z-2), (x+2, 3, z+2), BASE)
            a.box((x-1, 4, z-1), (x+1, 7, z+1), SHELLS[2], True)
            a.box((x, 8, z-1), (x, 10, z+1), GEAR)
        a.route('晶体送料与分选', '晶体采集副塔', [(x, 7, -10), (x, 7, -3), (x, 7, 0)])
        a.route('晶体采集副塔', '液态冷凝塔', [(x, 17, 0), (side*4, 17, 0)], GEAR)
        a.box((min(x, side*3), 18, 2), (max(x, side*3), 18, 3), GRATE)
        a.zone('西侧晶体采集塔' if side < 0 else '东侧晶体采集塔', (x-2, 2, -2), (x+2, 32, 2),
               '绿调透明晶体压榨柱、三层压榨节、上下送料分选', 'solid')
    a.box((-10, 0, 6), (10, 0, 6), GRATE)
    a.box((-10, 0, -5), (-8, 0, -5), GRATE)
    a.box((8, 0, -5), (10, 0, -5), GRATE)
    vessel(a, 0, 0, {33: 1, 34: 2, 35: 2, 36: 1}, SHELLS[2], ENERGY)
    a.box((0, 33, 0), (0, 36, 0), GEAR)
    a.zone('中央晶体驱动延伸段', (-2, 33, -2), (2, 36, 2), '原轴顶端附加晶体驱动；保留原十字吸口', 'drive')
    return finish(a, '原中央蓝银塔完整保留，两座绿调晶体副塔在东西两侧对称增建；三层压榨节和前后送料分选机通过正交机械横桥服务旧核心。主轴仅在原冠顶上继续拔高，工段没有沿对角线串排。')


def i01_3():
    a = SignedBuild(3, i01_2())
    for x, z, name in ((-15, 0, '西'), (15, 0, '东'), (0, -15, '北'), (0, 15, '南')):
        a.box((x-3, 0, z-3), (x+3, 1, z+3), BASE)
        a.box((x-2, 2, z-2), (x+2, 31, z+2), SHELLS[3], True)
        for dx in (-2, 2):
            for dz in (-2, 2):
                a.box((x+dx, 2, z+dz), (x+dx, 31, z+dz), BASE)
        a.box((x, 2, z), (x, 39, z), PIPE)
        for y in range(5, 30, 5):
            a.box((x-1, y, z-3), (x+1, y+1, z-3), VENT)
            a.box((x-1, y, z+3), (x+1, y+1, z+3), VENT)
        a.box((x-3, 32, z-3), (x+3, 34, z+3), BASE, True)
        a.box((x-2, 35, z-2), (x+2, 38, z+2), SHELLS[3], True)
        a.box((x-1, 39, z-1), (x+1, 40, z+1), VENT)
        # 地面连接走设备两侧，北向直通控制坞的中轴不设矮墙或横管。
        if x:
            a.box((min(x, 0), 0, 6), (max(x, 0), 0, 8), GRATE)
            a.box((x-1, 0, 3), (x+1, 0, 6), GRATE)
        elif z > 0:
            a.box((-1, 0, 8), (1, 0, z-3), GRATE)
        else:
            a.box((-7, 0, -18), (7, 0, -9), GRATE)
            # 北向吸风体跨过维护通道，两个外置支脚托住完整设备，地面中轴可直通。
            for sx in (-8, 8):
                a.box((sx-1, 0, -16), (sx+1, 1, -14), BASE)
                a.box((sx, 2, -15), (sx, 31, -15), BASE)
            a.box((-8, 32, -16), (8, 32, -14), PIPE)
        a.zone(name+'向垂直吸风塔', (x-3, 0, z-3), (x+3, 40, z+3),
               '垂直进气塔、双面机械百叶和高位汇气头', 'gas')
    for y in (33, 34):
        square_ring(a, 15, y, BASE if y == 33 else SHELLS[3], 2)
    for x in (-15, 15):
        a.box((x, 2, -15), (x, 32, -15), BASE)
        a.box((x, 2, 15), (x, 32, 15), BASE)
        a.box((x, 0, -15), (x, 1, 15), GRATE)
    for z in (-15, 15):
        a.box((-15, 0, z), (15, 0, z), GRATE)
    vessel(a, 0, 0, {y: 2 for y in range(37, 44)}, SHELLS[3])
    a.box((0, 37, 0), (0, 44, 0), PIPE)
    for x in (-15, 15):
        a.route('东西吸风汇流', '中央高位气液集流', [(x, 40, 0), (0, 40, 0)], PIPE)
    for z in (-15, 15):
        a.route('南北吸风汇流', '中央高位气液集流', [(0, 40, z), (0, 40, 0)], PIPE)
    a.box((-2, 44, -2), (2, 44, 2), BASE)
    a.path('东侧气态塔维护路径', (18, 2, -12), (18, 4, 12))
    a.box((16, 1, -12), (18, 1, 12), GRATE)
    a.zone('方形高位集气桁架', (-16, 33, -16), (16, 34, 16), '四向吸风塔经方形环梁连接，空中十字管汇入中央旧轴', 'gas_header')
    a.zone('中央高位气液集流', (-2, 37, -2), (2, 44, 2), '竖直原轴继续拔高，四向气态汇流', 'collector')
    return finish(a, '前两阶完整保留；南北东西四座青色垂直吸风塔组成十字秩序，高位方形集气桁架围绕旧核心而中央持续拔高。四向百叶、塔顶汇气头和空中十字管各有明确去向；控制坞北侧保持直通维护轴。')


def i01_4():
    a = SignedBuild(4, i01_3())
    pairs = [(x, z) for x in (-13, 13) for z in (-24, 24)]
    pairs += [(x, z) for x in (-24, 24) for z in (-13, 13)]
    for index, (x, z) in enumerate(pairs, 1):
        a.box((x-2, 0, z-2), (x+2, 2, z+2), BASE)
        a.box((x-2, 3, z-2), (x+2, 53, z+2), BASE, True)
        a.box((x, 3, z), (x, 57, z), POWER)
        # 紫蓝只占外骨架的竖直功率脊和颈节，不把巨柱涂成大白框。
        a.box((x-1, 3, z-2), (x+1, 53, z-2), SHELLS[4])
        a.box((x-1, 3, z+2), (x+1, 53, z+2), SHELLS[4])
        for y in (13, 27, 41, 54):
            a.box((x-2, y, z-2), (x+2, y+1, z+2), PIPE, True)
        a.box((x-2, 55, z-2), (x+2, 57, z+2), SHELLS[4], True)
        a.zone('外围能量支承巨柱%d' % index, (x-2, 0, z-2), (x+2, 57, z+2),
               '固定竖直支承、紫蓝功率脊和四层实体节点', 'exoskeleton')
    # 周边地面服务环为巨柱冷却和维护，不铺空白整板。
    square_ring(a, 24, 0, GRATE, 3)
    for x in (-15, 15):
        a.box((x-1, 0, 15), (x+1, 0, 24), GRATE)
    a.box((-7, 0, -26), (7, 0, -19), GRATE)
    for y in range(56, 61):
        square_ring(a, 25, y, SHELLS[4] if y in (57, 58) else BASE, 3)
    # 巨型能量冠沿四正交方向伸入核心，上方与下方空气保持通透。
    for x in (-24, 24):
        a.box((min(0, x), 50, -1), (max(0, x), 51, 1), PIPE)
        a.box((x, 50, -13), (x, 51, 13), POWER)
    for z in (-24, 24):
        a.box((-1, 50, min(0, z)), (1, 51, max(0, z)), PIPE)
        a.box((-13, 50, z), (13, 51, z), POWER)
    vessel(a, 0, 0, {45: 1, 46: 2, 47: 3, 48: 4, 49: 5, 50: 5,
                      51: 5, 52: 4, 53: 3, 54: 2, 55: 1}, SHELLS[4], ENERGY)
    a.box((0, 45, 0), (0, 55, 0), POWER)
    a.box((-1, 56, -1), (1, 58, 1), GEAR)
    for x in (-24, 24):
        a.route('外围四对巨柱', '中央开放晶核', [(x, 57, 0), (0, 57, 0)], SHELLS[4])
    for z in (-24, 24):
        a.route('外围四对巨柱', '中央开放晶核', [(0, 57, z), (0, 57, 0)], SHELLS[4])
    a.box((-20, 1, -20), (-18, 1, 20), GRATE)
    a.path('西侧外围能量冠维护轴', (-20, 2, -20), (-18, 4, 20))
    a.zone('巨型方形能量冠', (-25, 56, -25), (25, 60, 25), '由四对巨柱承托的五层厚方冠，内部全部留空', 'energy_crown')
    a.zone('中央开放晶核', (-5, 45, -5), (5, 58, 5), '原竖轴顶端开放透明晶核、四向正交功率耦合臂', 'energy_collector')
    # 在已完成的第四阶上方只增建；连本阶原有晶核、横臂和方冠也不允许覆盖。
    existing = dict(a.b)
    a.protected.update(existing)
    a.box((-1, 59, -1), (1, 62, 1), GEAR)
    # 四向厚臂分三次抬升，低端接外围冠、高端接透镜座；空中保留大片透空。
    for axis in (0, 2):
        for side in (-1, 1):
            def arm(lo, hi, bottom, top, material):
                p, q = [-2, bottom, -2], [2, top, 2]
                p[axis], q[axis] = sorted((side*lo, side*hi))
                a.box(p, q, material)
            arm(22, 24, 59, 62, POWER)
            arm(9, 24, 61, 62, PIPE)
            arm(7, 11, 63, 64, BASE)
            arm(5, 8, 65, 66, POWER)
            points = []
            for distance, y in ((24, 60), (24, 62), (9, 62), (9, 64),
                                (7, 64), (7, 66), (0, 66)):
                p = [0, y, 0]
                p[axis] = side*distance
                points.append(p)
            a.route('外围方冠高位承托', '中央能量收集透镜', points, POWER)
    # 凹槽透镜座逐层退台，并非再叠一个普通塔筒或另一圈巨型方框。
    for y, half, material, thick in ((62, 9, BASE, 1), (63, 9, SHELLS[4], 2),
                                    (64, 8, BASE, 2), (65, 7, POWER, 2), (66, 6, BASE, 2)):
        square_ring(a, half, y, material, thick)
    profile = {59: 1, 60: 2, 61: 3, 62: 4, **{y: 5 for y in range(63, 76)}}
    vessel(a, 0, 0, profile, BASE, ENERGY)
    a.box((0, 59, 0), (0, 75, 0), POWER)
    # 上冠用实体透明棱晶逐层收束；主观察面保持连续十余格高度，晶尖最高。
    for y, radius in ((76, 4), (77, 3), (78, 2), (79, 1), (80, 0)):
        for x in range(-radius, radius+1):
            for z in range(-radius, radius+1):
                if abs(x)+abs(z) <= radius*3//2+1:
                    a.set(x, y, z, ENERGY)
    a.zone('四向分层透镜承臂', (-24, 59, -24), (24, 66, 24),
           '四个正交厚承臂分三层向中央抬升，回接既有外围方冠', 'lens_support')
    a.zone('退台凹槽集能透镜座', (-9, 59, -9), (9, 66, 9),
           '五层内缩方形槽座，托住中央竖直能量透镜；外圈与晶体之间留有空气层', 'lens_crown')
    a.zone('中央高位能量收集透镜', (-5, 59, -5), (5, 80, 5),
           '同一固定竖轴上升；透明切角棱晶主面和五层透明收束冠重新成为最高焦点', 'energy_lens')
    assert all(a.b[p] == material for p, material in existing.items()), '第四阶既有实体被改写'
    return finish(a, '前三阶和本阶原有八柱、方冠及低位晶核逐块保留。中央竖轴从旧晶核上方继续升至81格总高，四向厚承臂分层抬升，接入五层退台凹槽透镜座；连续透明棱晶主面与收束晶尖从外围方冠开口高高露出，重新成为采集塔最高焦点。北向控制坞保持直通维护通道。')


def validate_chain():
    """用相对粘贴锚点逐格证明继承，同时复核实际范围、标记、通道和连通。"""
    results, previous = [], None
    offsets = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for fn in (i01_1, i01_2, i01_3, i01_4):
        data = fn()
        blocks = {tuple(q['pos']): q['state'] for q in data['blocks']}
        lo, hi = [min(p[i] for p in blocks) for i in range(3)], [max(p[i] for p in blocks) for i in range(3)]
        assert lo == [0, 0, 0] and [hi[i]+1 for i in range(3)] == data['size']
        sizeaudit = require(data)
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
        assert not remain, (data['key'], '不连通', len(remain), sorted(remain)[:5])
        c = tuple(data['controller'])
        assert c == tuple(data['paste_anchor']) and blocks[c] == DIAMOND
        assert sum(s == DIAMOND for s in blocks.values()) == 1
        for port in data['ports']:
            x, y, z = port['pos']
            assert blocks[(x, y, z)] == PORT and (x, y, z-1) not in blocks
            assert (x, y-1, z) in blocks and (x, y, z+1) in blocks
        for path in data['paths']:
            assert not any(all(path['min'][i] <= p[i] <= path['max'][i] for i in range(3)) for p in blocks), path
        relative = {tuple(p[i]-c[i] for i in range(3)): s for p, s in blocks.items()}
        mismatches = [] if previous is None else [p for p, s in previous.items() if p != (0, 0, 0) and relative.get(p) != s]
        assert not mismatches, (data['key'], '升级移动或改写', mismatches[:5])
        results.append({'key': data['key'], 'size_xyz': data['size'], 'blocks': len(blocks),
                        'inherited_non_controller': len(previous)-1 if previous else 0,
                        'added_blocks': data['upgrade_contract']['added_blocks'],
                        'coordinate_shift': data['coordinate_shift'], 'signed_origin': data['signed_origin'],
                        'paste_anchor': data['paste_anchor'], 'upgrade_mismatches': len(mismatches),
                        'connected': True, 'paths_clear': True, 'ports': 6, 'baseline': sizeaudit['passed']})
        previous = relative
    return results


if __name__ == '__main__':
    print(json.dumps(validate_chain(), ensure_ascii=False, indent=2))
