# -*- coding: utf-8 -*-
"""五阶科研院区的固定原位坐标、接口、可步行空间与逐格继承合同。

变更记录 #1 2026-10-14：新增独立候选生成器；旧交付、生产定义和实例不改。
"""
import collections
import copy
import hashlib
import json

from redesign69_geometry import Build
from structure_size_baseline import require

WHITE = 'gtceu:clean_machine_casing'
BASE = 'gtceu:solid_machine_casing'
PIPE = 'gtceu:steel_pipe_casing'
PANEL = 'gtceu:advanced_computer_casing'
COMPUTER = 'gtceu:computer_casing'
VENT = 'gtceu:computer_heat_vent'
GRATE = 'gtceu:assembly_line_grating'
GLASS = 'gtceu:laminated_glass'
PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
SIZES = {1: (17, 17, 25), 2: (33, 27, 37), 3: (49, 37, 57),
         4: (73, 55, 73), 5: (129, 105, 129)}
CONTROLLER = (0, 3, -11)
TITLES = {1: '崩坏现象研究所', 2: '物质重构研究所', 3: '量子域研究所',
          4: '世界维系研究所', 5: '文明认知穹顶'}
PORT_X = (-6, -4, -2, 2, 4, 6)
PURPOSES = [('SAMPLE', '研究样件输入候选'), ('MATERIAL', '研究材料输入候选'),
            ('POWER', '科研供电候选'), ('RESULT', '研究证据输出候选'),
            ('COOLANT', '冷却介质输入候选'), ('RETURN', '冷却回流候选')]


def add(p, q):
    return [p[i]+q[i] for i in range(3)]


class Campus(Build):
    """可扩建院区；前阶实体与已声明的门洞、通道全部冻结。"""
    def __init__(self, stage, previous=None):
        w, h, d = SIZES[stage]
        title = TITLES[stage]
        super().__init__({'id': 'S%02d' % stage, 'title': title, 'minimum_wdh': [w, d, h],
                          'form': '固定中央研究楼与逐阶原位增建的正交科研院区',
                          'flow': '实验观察→独立实验翼→超算档案→跨域科研→文明认知'})
        self.stage, self.previous = stage, previous
        self.frozen, self.protected = {}, set()
        self.references = []
        if previous:
            origin = previous['signed_origin']
            self.frozen = {tuple(add(q['pos'], origin)): q['state'] for q in previous['blocks']}
            self.b.update(self.frozen)
            for state in self.frozen.values():
                self.roles[state].add(state)
            self.references = list(previous.get('references', []))
            for key in ('zones', 'paths', 'links'):
                items = copy.deepcopy(previous[key])
                setattr(self, key, items)
                for item in items:
                    for field in ('min', 'max', 'pos'):
                        if field in item:
                            item[field] = add(item[field], origin)
                    if 'route' in item:
                        item['route'] = [add(p, origin) for p in item['route']]
            for path in self.paths:
                self.protect(path['min'], path['max'])
        self.path('北向控制坞维护轴 · 第%d阶' % stage, (-7, 1, -(d//2)), (7, 4, -12))
        self.box((-7, 0, -(d//2)), (7, 0, -12), GRATE)
        if stage == 1:
            self.dock()

    def protect(self, lo, hi):
        self.protected.update((x, y, z) for x in range(lo[0], hi[0]+1)
                              for y in range(lo[1], hi[1]+1) for z in range(lo[2], hi[2]+1))

    def path(self, name, lo, hi):
        lo, hi = list(lo), list(hi)
        assert all(lo[i] <= hi[i] for i in range(3)), (name, lo, hi)
        assert not any(all(lo[i] <= p[i] <= hi[i] for i in range(3)) for p in self.b), name
        self.paths.append({'name': name, 'min': lo, 'max': hi, 'kind': 'walk',
                           'floor_y': lo[1]-1, 'headroom': hi[1]-lo[1]+1})
        self.protect(lo, hi)

    def set(self, x, y, z, material):
        p = tuple(round(v) for v in (x, y, z))
        w, h, d = SIZES[self.stage]
        assert -w//2+1 <= p[0] <= w//2 and 0 <= p[1] < h and -d//2+1 <= p[2] <= d//2, p
        if p in self.frozen or p in self.protected:
            return
        self.b[p] = material
        self.roles[material].add(material)

    def line(self, lo, hi, material, width=1):
        assert width == 1, '粗梁请用显式 box，避免负坐标裁剪'
        assert sum(lo[i] != hi[i] for i in range(3)) <= 1, '院区连接只能沿正交轴'
        super().line(lo, hi, material, width=1)

    def zone(self, name, lo, hi, role, kind='equipment'):
        self.zones.append({'name': name, 'min': list(lo), 'max': list(hi),
                           'pos': [(lo[0]+hi[0])//2, hi[1], (lo[2]+hi[2])//2],
                           'role': role, 'kind': kind, 'service_face': '门洞与相邻院区通道'})

    def route(self, source, target, points, material=PIPE):
        for p, q in zip(points, points[1:]):
            self.line(p, q, material)
        self.links.append({'from': source, 'to': target, 'route': [list(p) for p in points]})

    def dock(self):
        """固定白框主控立面，背板接科研楼；框内六接口都是无功能占位。"""
        self.box((-8, 0, -11), (8, 0, -9), GRATE)
        self.box((-7, 1, -10), (7, 4, -10), BASE)
        self.box((-7, 1, -11), (7, 1, -11), WHITE)
        self.box((-7, 4, -11), (7, 4, -11), WHITE)
        for x in (-7, -1, 1, 7):
            self.box((x, 2, -11), (x, 3, -11), WHITE)
        for x in PORT_X:
            self.set(x, 2, -11, PANEL)
            self.set(x, 3, -11, PORT)
        self.set(0, 2, -11, WHITE)
        self.set(*CONTROLLER, DIAMOND)


def finish(a, description, references=None):
    """所有几何和说明字段一并转至局部；粘贴锚始终是原位主控。"""
    lo = [min(p[i] for p in a.b) for i in range(3)]
    hi = [max(p[i] for p in a.b) for i in range(3)]
    shift, size = [-v for v in lo], [hi[i]-lo[i]+1 for i in range(3)]
    collections_out = {}
    for key in ('zones', 'paths', 'links'):
        items = copy.deepcopy(getattr(a, key))
        collections_out[key] = items
        for item in items:
            for field in ('min', 'max', 'pos'):
                if field in item:
                    item[field] = add(item[field], shift)
            if 'route' in item:
                item['route'] = [add(p, shift) for p in item['route']]
            if 'floor_y' in item:
                item['floor_y'] += shift[1]
    c = add(CONTROLLER, shift)
    previous_shift = a.previous['coordinate_shift'] if a.previous else [0, 0, 0]
    ordinary = collections.Counter(s.split(':')[0] for s in a.b.values() if s not in (DIAMOND, PORT))
    total = sum(ordinary.values())
    refs = list(dict.fromkeys(a.references + list(references or [])))
    contract = {'previous': a.previous['key'] if a.previous else None,
                'preserved_non_controller_blocks': len(a.frozen)-1 if a.previous else 0,
                'added_blocks': len(a.b)-len(a.frozen), 'coordinate_shift': shift,
                'relative_local_shift': [shift[i]-previous_shift[i] for i in range(3)],
                'signed_origin': lo, 'fixed_signed_controller': list(CONTROLLER),
                'inheritance_basis': '逐块减去 paste_anchor 对比，前阶非主控全部保持坐标与状态',
                'signed_non_controller_sha256': hashlib.sha256(json.dumps(
                    [(p, s) for p, s in sorted(a.b.items()) if p != CONTROLLER],
                    ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()}
    return {'key': a.brief['id'].lower(), 'name': a.brief['id'].lower()+'-research-campus-v1',
            'title': a.brief['title'], 'size': size, 'controller': c, 'paste_anchor': c,
            'coordinate_shift': shift, 'signed_origin': lo, 'world_min': lo, 'world_max': hi,
            'fixed_signed_controller': list(CONTROLLER), **collections_out,
            'ports': [{'id': key, 'pos': add((x, 3, -11), shift), 'face': 'north', 'purpose': purpose}
                      for x, (key, purpose) in zip(PORT_X, PURPOSES)],
            'brief': a.brief, 'description': description, 'references': refs,
            'role_materials': {k: sorted(v) for k, v in a.roles.items()},
            'blocks': [{'pos': add(p, shift), 'state': s} for p, s in sorted(a.b.items())],
            'upgrade_contract': contract, 'recommended_bottom_y': -60,
            'material_usage': {'ordinary_namespace_counts': dict(ordinary), 'ordinary_total': total,
                               'gt_share_percent': round((ordinary['gtceu']+ordinary['gtlcore'])/total*100, 2),
                               'controller_markers': 1, 'industrial_port_placeholders': 6,
                               'survival_stage': '用户本轮明确不限生存阶段；不声明配方可达性'},
            'coordinate_conversion': {'signed_to_local': 'local = signed + coordinate_shift',
                                      'local_to_signed': 'signed = local + signed_origin',
                                      'paste': 'world = local - paste_anchor + target_anchor'}}


def validate(data, previous=None):
    """独立核查六面连通、真实尺寸、接口和每条可步行通道的地板。"""
    states = {tuple(q['pos']): q['state'] for q in data['blocks']}
    lo = [min(p[i] for p in states) for i in range(3)]
    hi = [max(p[i] for p in states) for i in range(3)]
    assert lo == [0, 0, 0] and [v+1 for v in hi] == data['size']
    assert data['size'] == list(SIZES[int(data['key'][1:])]), (data['key'], data['size'])
    baseline = require(data)
    remain = set(states)
    todo = collections.deque([next(iter(remain))])
    remain.remove(todo[0])
    while todo:
        p = todo.popleft()
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = tuple(p[i]+d[i] for i in range(3))
            if q in remain:
                remain.remove(q)
                todo.append(q)
    assert not remain, (data['key'], '不连通', len(remain), sorted(remain)[:8])
    c = tuple(data['controller'])
    assert c == tuple(data['paste_anchor']) and states[c] == DIAMOND
    assert sum(s == DIAMOND for s in states.values()) == 1
    for port in data['ports']:
        x, y, z = port['pos']
        assert states[(x, y, z)] == PORT and (x, y, z-1) not in states
        assert (x, y-1, z) in states and (x, y, z+1) in states
    for path in data['paths']:
        low, high = path['min'], path['max']
        assert not any(all(low[i] <= p[i] <= high[i] for i in range(3)) for p in states), path
        assert high[1]-low[1] >= 1, ('不足两格净高', path)
        assert all((x, low[1]-1, z) in states for x in range(low[0], high[0]+1)
                   for z in range(low[2], high[2]+1)), ('通道缺地板', path)
    relative = {tuple(p[i]-c[i] for i in range(3)): s for p, s in states.items()}
    if previous:
        pc = previous['controller']
        old = {tuple(q['pos'][i]-pc[i] for i in range(3)): q['state'] for q in previous['blocks']}
        assert all(relative.get(p) == s for p, s in old.items() if p != (0, 0, 0)), '继承改变'
    return {'key': data['key'], 'size_xyz': data['size'], 'blocks': len(states),
            'six_face_connected': True, 'paths_clear_with_floor': True,
            'ports': 6, 'controller': data['controller'], 'baseline': baseline['passed'],
            'inherited_non_controller': data['upgrade_contract']['preserved_non_controller_blocks'],
            'upgrade_mismatches': 0, 'material_usage': data['material_usage']}
