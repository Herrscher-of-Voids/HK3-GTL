# -*- coding: utf-8 -*-
"""按负责人照片和Spear of Void纹理重做C版六矛，其余生成语句保持原样。"""
import ast
import copy
import math
from pathlib import Path
import numpy as np
import w03_celestial_geometry_v4_20261107 as original
from audit_wonder_clipping_20261108 import ExpandBuild, LogicalGrid, PAD

ROOT = Path(__file__).resolve().parents[2]
BLACK = original.M.ATOMIC
WHITE = original.WHITE
AMBER = 'minecraft:orange_concrete'
STATES = original.STATES + [AMBER]
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = dict(original.ROLES, **{AMBER: '亚空之矛橙色律者晶核的实体晶面'})


def spear_voxels():
    """局部坐标：X沿矛尖到矛尾，Y为正面轮廓，Z为厚度。"""
    cells = {}

    def put(p, state):
        for q in np.rint(np.asarray(p)).astype(int):
            cells[tuple(q)] = state

    a, b = np.meshgrid(np.arange(-15, 16), np.arange(-5, 6))
    a, b = a.ravel(), b.ravel()
    for t in np.arange(0, 88.01, .4):
        half = np.interp(t, [0, 12, 64, 77, 88], [.1, 2.2, 10, 12, 5])
        thick = np.interp(t, [0, 24, 70, 88], [.1, 1.2, 3.5, 2])
        m = np.abs(a) / half + np.abs(b) / max(.1, thick) <= 1.08
        q = np.c_[np.full(m.sum(), t), a[m], b[m]]
        put(q, WHITE if t < 9 else BLACK)
        if 17 < t < 73:
            for side in (-1, 1):
                for face in (-1, 1):
                    put([[t, side * half * .52, face * thick * .5]], WHITE)

    def tube(curve, half=2.2, depth=2, state=WHITE):
        a, b = np.meshgrid(np.arange(-math.ceil(half), math.ceil(half) + 1), np.arange(-depth, depth + 1))
        a, b = a.ravel(), b.ravel()
        m = np.abs(a) / half + np.abs(b) / max(1, depth) <= 1.08
        for p in curve:
            put(p + np.c_[np.zeros(m.sum()), a[m], b[m]], state)

    def bezier(a, b, c):
        t = np.linspace(0, 1, 170)[:, None]
        return (1-t)**2*np.array(a)+2*(1-t)*t*np.array(b)+t*t*np.array(c)

    # 黑色开放笼架围住橙晶，保留可见的空气缝；不再用金色C环和紫色八面体。
    for side in (-1, 1):
        tube(bezier([80, side*5, 0], [100, side*19, 0], [126, side*10, 0]), 1.8, 2, BLACK)
    tube(bezier([122, 0, -4], [143, 0, -6], [163, 0, 0]), 1.2, 1, BLACK)
    for t in np.arange(93, 121.01, .4):
        radius = np.interp(t, [93, 105, 111, 121], [.1, 7.5, 6, .1])
        a, b = np.meshgrid(np.arange(-8, 9), np.arange(-6, 7))
        m = np.abs(a) + np.abs(b)*1.4 <= radius + .1
        q = np.c_[np.full(m.sum(), t), a[m], b[m]]
        put(q, AMBER)
        if radius > 2:
            put([[t, 0, radius/1.4]], original.ORANGE)

    # 白色护翼沿不同曲线展开；中央横翼为尖锐扁片，后部留黑色裸露脊柱。
    tube(bezier([111, 12, 0], [126, 26, 0], [143, 12, 0]), 3.2, 2)
    tube(bezier([117, -9, 0], [133, -27, 0], [161, -9, 0]), 3.4, 3)
    for t in np.arange(120, 133.01, .4):
        width = max(.2, 24*(1-abs(t-126.5)/6.6))
        a, b = np.meshgrid(np.arange(-4, 25), np.arange(-2, 3))
        m = (a >= -3) & (a <= width) & (np.abs(b) <= 1.6*(1-np.abs(a)/27))
        put(np.c_[np.full(m.sum(), t), a[m], b[m]+1], WHITE)
    tube(bezier([141, -16, 0], [155, -17, 0], [174, -2, 0]), 3.2, 3)
    for t in np.arange(158, 205.01, .35):
        half = np.interp(t, [158, 168, 184, 205], [4, 8, 4, .05])
        thick = np.interp(t, [158, 170, 205], [2.5, 3.5, .05])
        a, b = np.meshgrid(np.arange(-8, 9), np.arange(-4, 5))
        m = np.abs(a)/half + np.abs(b)/max(.1, thick) <= 1.05
        put(np.c_[np.full(m.sum(), t), a[m]-2*(205-t)/47, b[m]], WHITE)
    assert all(0 <= q[0] <= 205 for q in cells)
    assert AMBER in cells.values() and original.M.GOLD not in cells.values()
    return cells


LOCAL = spear_voxels()


def draw_spears(points, beam, frame, core):
    coords = np.array(list(LOCAL), float)
    states = np.array(list(LOCAL.values()))
    spears = []
    for i in range(6):
        th = (i+.25)*math.pi/3
        v, u, w = frame([math.cos(th), .22*math.sin(th*2), math.sin(th)])
        tip = core+70*v
        for state in dict.fromkeys(states):
            p = coords[states == state]
            points(tip+p[:, :1]*v+p[:, 1:2]*u+p[:, 2:3]*w, str(state))
        spears.append(dict(id=i+1, tip=tip.tolist(), axis=v.tolist(), length=206,
                           local_frame_u=u.tolist(), local_frame_w=w.tolist(),
                           reference='负责人实物图；Spear of Void 1.3.2纹理',
                           features=['银白尖端与黑色长刃', '开放黑笼与橙色泪晶', '白色不对称护翼', '黑色裸脊与白色长尾']))
    return spears


class TrackedGrid(LogicalGrid):
    def __init__(self, shape, pad):
        super().__init__(shape, pad)
        self.recording = False
        self.spear_cells = set()

    def __setitem__(self, key, value):
        translated = self.key(key)
        if self.recording:
            if any(isinstance(v, slice) for v in translated):
                axes = [np.arange(v.start, v.stop) if isinstance(v, slice) else np.atleast_1d(v) for v in translated]
                indices = np.meshgrid(*axes, indexing='ij')
                flat = np.ravel_multi_index(tuple(q.ravel() for q in indices), self.array.shape)
            else:
                flat = np.ravel_multi_index(translated, self.array.shape)
            self.spear_cells.update(np.atleast_1d(flat).tolist())
        self.array[translated] = value


def replay(revised):
    source = Path(original.__file__).read_text('utf8')
    tree = ast.parse(source)
    build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build')
    indices = [i for i, n in enumerate(build.body) if isinstance(n, ast.For) and ast.unparse(n.iter) == 'range(6)']
    assert len(indices) == 1
    i = indices[0]
    replacement = ast.parse('spears=draw_spears(points,beam,frame,core)').body if revised else [build.body[i]]
    build.body[i:i+1] = ast.parse('c.recording=True').body + replacement + ast.parse('c.recording=False').body
    patch = ExpandBuild()
    tree = ast.fix_missing_locations(patch.visit(tree))
    env = dict(original.__dict__, __name__='c_spear_refinement', LogicalGrid=TrackedGrid,
               PAD=PAD, IDS=IDS, STATES=STATES, draw_spears=draw_spears)
    exec(compile(tree, str(original.__file__)+' (仅六矛替换)', 'exec'), env)
    env.update(IDS=IDS, STATES=STATES)
    grid, data = env['build']()
    return grid, data


def build():
    old, _ = replay(False)
    new, data = replay(True)
    authorized = np.fromiter(old.spear_cells | new.spear_cells, dtype=np.int64)
    changed = np.flatnonzero(old.array.ravel() != new.array.ravel())
    assert np.isin(changed, authorized).all(), '非亚空之矛构件发生改动'
    # 与玩家选择的C交付文件逐格比对，不能把旧裁切版当作底稿。
    import gzip
    from i34_open_observatory_export_20261027 import _headers
    base = ROOT/'deliveries/W03_完整几何边界修复_20261108/V4'
    import json
    manifest = json.loads((base/'manifest.json').read_text('utf8'))
    shape = (321, 529, 674)
    header = _headers(original.STATES, shape, manifest['blocks'])[1]
    with gzip.open(base/'w03'/f"{manifest['name']}.schem", 'rb') as f:
        assert f.read(len(header)) == header
        prior = np.frombuffer(f.read(math.prod(shape)), np.uint8).reshape(shape)
        assert f.read() == b'\0'
    assert np.array_equal(prior, old.array[PAD:PAD+321, PAD:PAD+529, PAD:PAD+674])
    del old, prior
    occupied = new.array != 0
    lo, hi = [], []
    for axis in range(3):
        at = np.flatnonzero(np.any(occupied, axis=tuple(i for i in range(3) if i != axis)))
        lo.append(int(at[0])); hi.append(int(at[-1])+1)
    assert all(a > 0 and b < new.array.shape[i] for i, (a, b) in enumerate(zip(lo, hi)))
    c = new.array[tuple(slice(a, b) for a, b in zip(lo, hi))].copy()
    minimum = [lo[2]-PAD, lo[0]-PAD, lo[1]-PAD]
    offset = -np.array(minimum)
    for item in data['ports']+data['zones']:
        item['pos'] = (np.array(item['pos'])+offset).tolist()
    for item in data['paths']:
        for k in ('min', 'max'): item[k] = (np.array(item[k])+offset).tolist()
    for item in data['pipe_routes']:
        for k in ('start', 'end', 'path'): item[k] = (np.array(item[k])+offset).tolist()
    data['controller'] = (np.array(data['controller'])+offset).tolist()
    data.update(name='hk3gtl-w03-c-spear-refinement-c1-20261108', candidate_version='C1-亚空之矛优化',
                title='空之律者 · 穹界·虚数锚定环 · C1亚空之矛优化',
                size=[c.shape[2], c.shape[0], c.shape[1]], nominal_size_xyz=[673, 321, 529],
                blueprint_bounds_xyz=dict(min=minimum, max=[hi[2]-PAD-1, hi[0]-PAD-1, hi[1]-PAD-1]),
                blueprint_to_export_offset_xyz=offset.tolist(),
                part_metadata_coordinates='六矛等构件保留原蓝图坐标；主控、接口、分区、通道与管路使用导出坐标',
                description='保留C版曲翼、空间飘带、三重双轨环、八面体核心与深渊基座；仅将六柄矛改为黑刃银尖、橙晶黑笼、白色分体护翼和修长白尾。',
                purpose='玩家反馈选择C后的第一轮局部外观优化；未批准定稿、未部署。',
                refinement=dict(changed_final_cells=len(changed), authorized_spear_write_cells=len(authorized),
                                outside_spear_writes_changed=0, base_c_schematic_exact=True, no_nominal_clipping=True))
    return c, data
