# -*- coding: utf-8 -*-
"""C2保留C1构件，改成立式正圆并按独立体素构件留出净空。"""
import ast
import json
import math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import w03_celestial_geometry_v4_20261107 as original
import w03_void_spear_c1_20261108 as c1
import audit_wonder_clipping_20261108 as clipping
from audit_wonder_clipping_20261108 import ExpandBuild, LogicalGrid

STATES, ROLES = c1.STATES, c1.ROLES
PAD = 160
ACTIVE = None


def mark(name):
    ACTIVE.part = name


class Slice:
    def __init__(self, grid, y): self.grid, self.y = grid, y
    def __setitem__(self, mask, value):
        z, x = np.nonzero(mask)
        self.grid[self.y, z-PAD, x-PAD] = value


class Capture(LogicalGrid):
    def __init__(self, shape, pad):
        global ACTIVE
        super().__init__(shape, pad)
        self.part, self.parts = 'base', {}
        ACTIVE = self

    def indices(self, key):
        t = self.key(key)
        if any(isinstance(v, slice) for v in t):
            axes = [np.arange(0 if v.start is None else v.start, self.array.shape[i] if v.stop is None else v.stop)
                    if isinstance(v, slice) else np.atleast_1d(v) for i, v in enumerate(t)]
            t = np.ix_(*axes)
        return np.ravel_multi_index(np.broadcast_arrays(*t), self.array.shape)

    def __setitem__(self, key, value):
        if self.part == 'base': super().__setitem__(key, value)
        else:
            cells = self.parts.setdefault(self.part, {})
            cells.update(dict.fromkeys(np.atleast_1d(self.indices(key)).ravel().tolist(), int(value)))

    def __getitem__(self, key):
        if self.part == 'base': return super().__getitem__(key)
        if isinstance(key, int): return Slice(self, key)
        flat = self.indices(key)
        cells = self.parts.get(self.part, {})
        return np.fromiter((cells.get(int(i), 0) for i in flat.ravel()), np.uint8).reshape(flat.shape)


def local_frame(v):
    v = np.asarray(v, float); v /= np.linalg.norm(v)
    u = np.cross(v, [0, 1, 0] if abs(v[1]) < .9 else [0, 0, 1]); u /= np.linalg.norm(u)
    return v, u, np.cross(v, u)


def draw_spears(points, beam, frame, core):
    result = []
    coords = np.array(list(c1.LOCAL), float); states = np.array(list(c1.LOCAL.values()))
    for i in range(6):
        mark('spear:'+str(i)); th = (i+.25)*math.pi/3
        v, u, w = frame([math.cos(th), .22*math.sin(th*2), math.sin(th)])
        tip = core+70*v
        for state in dict.fromkeys(states):
            p = coords[states == state]
            points(tip+p[:, :1]*v+p[:, 1:2]*u+p[:, 2:3]*w, str(state))
        result.append(dict(id=i+1, tip=tip.tolist(), axis=v.tolist(), length=206))
    return result


def capture(circle=False):
    tree = ast.parse(Path(original.__file__).read_text('utf8'))
    build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build')
    body = []
    for n in build.body:
        text = ast.unparse(n)
        prefix = None
        if isinstance(n, ast.FunctionDef) and n.name == 'truss_ring':
            n.body[:0] = ast.parse("mark('ring:'+str(radius))").body
        if isinstance(n, ast.For):
            it = ast.unparse(n.iter)
            labels = {'range(8)': "'anchor:'+str(i)", 'range(24)': "'cannon:'+str(i)",
                      'range(10)': "'feather:'+str(i)", 'range(12)': "'crown:'+str(i)"}
            if it in labels: n.body[:0] = ast.parse('mark('+labels[it]+')').body
            if it == 'enumerate((0, math.pi))':
                n.body[:0] = ast.parse("mark('ribbon:'+str(i))").body
                cube_loop = next(q for q in n.body if isinstance(q, ast.For) and 'enumerate(np.linspace' in ast.unparse(q.iter))
                cube_loop.body[:0] = ast.parse("mark('cube:'+str(i)+':'+str(j))").body
            if it == 'range(6)': n = ast.parse('spears=draw_spears(points,beam,frame,core)').body[0]
        if text.startswith('vertices ='): prefix = "mark('core')"
        if text.startswith('beam([336, 229, 264]'): prefix = "mark('core')"
        if text.startswith('box((324, 47, 0)'): prefix = "mark('base')"
        if prefix: body += ast.parse(prefix).body
        body.append(n)
    build.body = body
    if circle:
        class Circle(ast.NodeTransformer):
            def visit_FunctionDef(self, n):
                if n.name == 'ellipse': n.args.defaults[1] = ast.Constant(210)
                return self.generic_visit(n)
            def visit_Assign(self, n):
                s = ast.unparse(n.value)
                if isinstance(n.value, ast.IfExp) and ast.unparse(n.value.body) == '(210, 113)':
                    n.value.body.elts[1] = ast.Constant(210)
                if s.startswith('frame([math.cos(th), 0.65 * math.sin(th)'):
                    n.value = ast.parse('frame([math.cos(th),math.sin(th),0])', mode='eval').body
                return self.generic_visit(n)
        tree = Circle().visit(tree)
    previous_pad = clipping.PAD
    try:
        clipping.PAD = PAD
        tree = ast.fix_missing_locations(ExpandBuild().visit(tree))
    finally: clipping.PAD = previous_pad
    env = dict(original.__dict__, LogicalGrid=Capture, PAD=PAD, IDS=c1.IDS, STATES=STATES,
               mark=mark, draw_spears=draw_spears, __name__='w03_c2_capture')
    exec(compile(tree, str(original.__file__)+' (C2独立构件)', 'exec'), env)
    env.update(IDS=c1.IDS, STATES=STATES)
    grid, data = env['build']()
    parts = {}
    y, z, x = np.nonzero(grid.array)
    parts['base'] = Part('base', np.c_[x-PAD, y-PAD, z-PAD], grid.array[y, z, x])
    del y, z, x
    for name, cells in grid.parts.items():
        flat = np.fromiter(cells, np.int64); y, z, x = np.unravel_index(flat, grid.array.shape)
        parts[name] = Part(name, np.c_[x-PAD, y-PAD, z-PAD], np.fromiter(cells.values(), np.uint8))
    grid.parts.clear(); grid.array = None
    return parts, data


class Part:
    def __init__(self, name, points, states):
        self.name, self.p, self.states = name, np.asarray(points, np.int32), np.asarray(states, np.uint8)
        self.tree = None; self._bounds = None; self.translation = np.zeros(3, int)
    def move(self, delta):
        delta = np.rint(delta).astype(np.int32)
        self.p += delta; self.translation += delta; self.tree = None; self._bounds = None
    @property
    def bounds(self):
        if self._bounds is None: self._bounds = self.p.min(0), self.p.max(0)
        return self._bounds
    def nearest(self, other, limit):
        a, b = self.bounds; c, d = other.bounds
        if np.max(np.maximum(a-d, c-b)) >= limit: return math.inf, 0
        if other.tree is None: other.tree = cKDTree(other.p)
        dist = other.tree.query(self.p, p=np.inf, distance_upper_bound=limit, workers=1)[0]
        return float(dist.min()), int(np.count_nonzero(dist == 0))


def connections(name): return 'architecture' if name == 'base' or name.startswith('anchor:') else name


def collisions(parts, gap=8):
    values = list(parts.values()); results = []
    for i, a in enumerate(values):
        for b in values[:i]:
            if connections(a.name) == connections(b.name): continue
            distance, count = a.nearest(b, gap)
            if distance < gap: results.append(dict(a=a.name, b=b.name, min_chebyshev_distance=distance, overlap_cells=count))
    return results


def place(part, settled, direction=None, gap=8):
    movement = np.zeros(3, int)
    for attempt in range(121):
        failures = [(q.name, part.nearest(q, gap)[0]) for q in settled
                    if connections(part.name) != connections(q.name)]
        failures = [(name, distance) for name, distance in failures if distance < gap]
        if not failures: settled.append(part); return movement.tolist()
        assert direction is not None, (part.name, failures)
        step = np.rint(np.asarray(direction)*4).astype(int)
        assert np.any(step)
        part.move(step); movement += step
    raise AssertionError((part.name, '无法获得构件净空', failures))


def build():
    def raw(circle):
        cache = Path(__file__).resolve().parents[2]/'logs/w03-clearance-c2-20261108'/('raw-circle.npz' if circle else 'raw-c1.npz')
        if cache.exists():
            with np.load(cache, allow_pickle=False) as f:
                data = json.loads(str(f['metadata']))
                return {name:Part(name,f[name+'__p'],f[name+'__s']) for name in json.loads(str(f['names']))},data
        parts,data = capture(circle)
        payload = {name+suffix:value for name,p in parts.items() for suffix,value in [('__p',p.p),('__s',p.states)]}
        np.savez_compressed(cache, metadata=json.dumps(data,ensure_ascii=False), names=json.dumps(list(parts)), **payload)
        return parts,data
    old, _ = raw(False)
    before = collisions(old)
    print('C1构件接触／不足净空对：'+str(len(before)), flush=True)
    del old
    parts, data = raw(True)
    ring_lo, ring_hi = parts['ring:210'].bounds
    assert ring_hi[0]-ring_lo[0] == ring_hi[1]-ring_lo[1] == 446, (ring_lo,ring_hi)
    shifts = {}; rise = 196
    for name, p in parts.items():
        if connections(name) != 'architecture': p.move([0, rise, 0])
    # 六矛保持同一个C1局部模型，改为朝核心俯刺的锥形阵列，避开两层内环。
    local = np.array(list(c1.LOCAL), float); ids = np.array([c1.IDS[s] for s in c1.LOCAL.values()], np.uint8)
    core = np.array([336., 170.+rise, 264.]); spears = []
    for i in range(6):
        th = (i+.25)*math.pi/3; v, u, w = local_frame([math.cos(th), .85, math.sin(th)])
        tip = core+85*v
        p = np.rint(tip+local[:, :1]*v+local[:, 1:2]*u+local[:, 2:3]*w).astype(int)
        parts['spear:'+str(i)] = Part('spear:'+str(i), p, ids)
        spears.append(dict(id=i+1, tip=tip.tolist(), axis=v.tolist(), local_frame_u=u.tolist(), local_frame_w=w.tolist(), length=206))
    settled = []
    for name in ['base']+['anchor:'+str(i) for i in range(8)]+['ring:210','ring:142','ring:91','core']:
        place(parts[name], settled)
    for i in range(12):
        name = 'crown:'+str(i); shifts[name] = place(parts[name], settled, [0, 1, 0])
    for i in range(6):
        name = 'spear:'+str(i); shifts[name] = place(parts[name], settled, spears[i]['axis'])
        spears[i]['tip'] = (np.array(spears[i]['tip'])+shifts[name]).tolist()
    for i in range(24):
        name = 'cannon:'+str(i); th = i*math.pi/12
        shifts[name] = place(parts[name], settled, [math.cos(th), math.sin(th), 0], 12)
    for i, item in enumerate(data['feathers']):
        name = 'feather:'+str(i); z = 264+(i-4.5)*24
        start = np.array([item['start'][0]-55,item['start'][1]+rise,z])
        control = np.array([item['control'][0]-55,item['control'][1]+rise,z+6])
        tip = np.array([item['tip'][0]-55,item['tip'][1]+rise,z+8])
        a,b = np.meshgrid(np.arange(-6,7),np.arange(-3,4));a,b = a.ravel(),b.ravel()
        cells = {}
        for t in np.linspace(0,1,601):
            p = (1-t)**2*start+2*(1-t)*t*control+t*t*tip
            _,u,w = local_frame(2*(1-t)*(control-start)+2*t*(tip-control))
            taper = (1-t)**.55; mask = np.abs(a)/6+np.abs(b)/3 <= taper+.025
            q = np.rint(p+a[mask,None]*u+b[mask,None]*w).astype(int)
            gold = (np.abs(a[mask])<.1)&(b[mask]>=max(0,3*taper-1))
            for at, value in zip(q,np.where(gold,c1.IDS[original.M.GOLD],c1.IDS[original.WHITE])):cells[tuple(at)] = int(value)
        parts[name] = Part(name,list(cells),list(cells.values()))
        item.update(start=start.tolist(),control=control.tolist(),tip=tip.tolist(),depth_layer_spacing=24)
        t=np.linspace(0,1,1001)[:,None];curve=(1-t)**2*start+2*(1-t)*t*control+t*t*tip
        item['curve_length']=float(np.linalg.norm(np.diff(curve,axis=0),axis=1).sum())
        item.pop('suspended_root_gap',None)
        shifts[name] = place(parts[name], settled, [0,0,1])
    for i in range(2):
        name = 'ribbon:'+str(i); parts[name].move([55, 0, 35 if i == 0 else -35])
        shifts[name] = place(parts[name], settled, [1, 0, 1 if i == 0 else -1])
    for i in range(2):
        for j in range(12):
            name = f'cube:{i}:{j}'; ribbon = 'ribbon:'+str(i)
            delta = np.array([55, 0, 35 if i == 0 else -35])+np.array(shifts[ribbon])
            # 整颗晶体刚性外移，保留旋转壳；不删除与飘带相交的半边。
            direction = np.array([.7, .1, 1 if i == 0 else -1])
            parts[name].move(delta+direction*(20+(28-22*j/11)*.5))
            shifts[name] = place(parts[name], settled, direction)
    after = collisions(parts)
    assert not after, after
    for i, item in enumerate(data['feathers']):
        for key in ('start','control','tip'):
            item[key] = (np.array(item[key])+parts['feather:'+str(i)].translation).tolist()
    for item in data['cubes']:
        name = f"cube:{item['ribbon']-1}:{round((item['position_on_curve']-.06)/.08)}"
        item['center'] = (np.array(item['center'])+parts[name].translation).tolist()
    for item in data['rings']: item['center_blueprint'] = [336,159+rise,264]
    lo = np.min([p.p.min(0) for p in settled], axis=0); hi = np.max([p.p.max(0) for p in settled], axis=0)
    size = hi-lo+1; cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    for part in settled:
        p = part.p-lo; cube[p[:, 1], p[:, 2], p[:, 0]] = part.states
    for item in data['ports']+data['zones']: item['pos'] = (np.array(item['pos'])-lo).tolist()
    for item in data['paths']:
        for k in ('min','max'): item[k] = (np.array(item[k])-lo).tolist()
    for item in data['pipe_routes']:
        for k in ('start','end','path'): item[k] = (np.array(item[k])-lo).tolist()
    data['controller'] = (np.array(data['controller'])-lo).tolist()
    data['rings'][0].update(radius_x=210, radius_y=210, plane='vertical_XY', center_blueprint=[336,159+rise,264])
    data.update(size=size.tolist(), name='hk3gtl-w03-clearance-round-c2-20261108', candidate_version='C2-正圆与构件净空',
        title='空之律者 · 穹界·虚数锚定环 · C2正圆与净空', spears=spears,
        nominal_size_xyz=[673,321,529], blueprint_bounds_xyz=dict(min=lo.tolist(), max=hi.tolist()),
        blueprint_to_export_offset_xyz=(-lo).tolist(),
        part_metadata_coordinates='构件、控制曲线与净空边界为原蓝图坐标；主控、接口、分区、通道、管路为导出坐标',
        description='外主环改为半径210格的立式正圆；保留六柄C1黑白橙亚空之矛及全部曲翼、双飘带和晶体，重新布置独立构件净空。',
        purpose='按负责人红圈反馈制作的独立外观候选；不裁切构件，不部署。',
        clearance=dict(before=before, after=after, gap_rule='独立体素构件中心切比雪夫距离至少8，浮游柱到先置主体至少12；基础与锚桩为有意连接的同一建筑组件。',
            shifts=shifts, upper_assembly_rise=rise, round_ring=dict(radius_u=210,radius_v=210,diameter=420,vertical=True),
            part_count=len(parts), intersection_pairs_after=0, min_nonconnection_distance=8,
            part_bounds_blueprint={name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist(),translation=p.translation.tolist()) for name,p in parts.items()},
            architectural_joints=['基座、舰桥、锚桩、主控、通用接口及池底导管为同一承重组件', '核心外框、晶壳和光柱为同一核心组件'],
            source='C1红圈反馈；负责人本轮明确授权修正相交，不替换历史原案',
            standard_overworld_build_height_exceeded=bool(size[1]>384)))
    data['zones'] = [dict(name='420格立式正圆与双轨桁架',pos=(np.array([336,159+rise,264])-lo).tolist()),
                     dict(name='黑白橙六矛与三层律者核心',pos=(core-lo).astype(int).tolist()),
                     dict(name='V字舰桥与八处通用接口',pos=data['controller'])]
    return cube, data
