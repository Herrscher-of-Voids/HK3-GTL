"""按既定工艺分区生成W06–W15完整静态候选，不修改正式批准资源。"""
import base64
import gzip
import json
import math
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import package_w05_wind_circuit_a1_20261112 as package
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W06-W15_完整静态蓝图_A1_20261113'
LOG = ROOT / 'logs/w06-w15-blueprints-20261113'
WHITE, GRAY, METAL, BLACK, LIGHT, GLASS, CONTROL = [
    'minecraft:' + s for s in ['white_concrete', 'light_gray_concrete', 'iron_block',
                               'black_concrete', 'sea_lantern', 'cyan_stained_glass', 'redstone_block']]
ENTRIES = [
    ('W06', '永霜·极低温凝态工厂', 'QSV', '#91DCEB', '阶梯冷凝山、密封凝态室与分离热端'),
    ('W07', '生息·物质再生方舟', 'QCV', '#5969C8', '长轴再生舟、双翼回收工坊与开放维护甲板'),
    ('W08', '劫焰·恒星熔铸炉', 'QEV', '#E56A38', '开放式恒星坩埚、锻铸前庭与四向热端'),
    ('W09', '万象·文明共识矩阵', 'QAV', '#B8524A', '双卷档案翼、共识议场与低位交织廊'),
    ('W10', '坠星·引力奇点铸造井', 'IMV', '#9B75CA', '下沉铸造井、四向斜撑与引力冠架'),
    ('W11', '千律·分布式工业统御阵', 'ICV', '#B68A4F', '错落节点厂城、低位调度网与物资中转庭'),
    ('W12', '戒律·全域能量约束壁', 'IRV', '#CECDA2', '分段双壁、中央试验域与外侧检修环'),
    ('W13', '蚀界·自演算研究母机', 'IWV', '#CE54A8', '交错演算翼、独立样本舱与封闭回收廊'),
    ('W14', '终序·世界泡轮回引擎', 'WSV', '#BDA9F3', '等体量双循环核、交叉回收桥与前置门廊'),
    ('W15', '凌霄·树海朝觐圣座', 'CEV', '#DCC17B', '原方案朝觐轴、十四证据庭、空席与分枝冠架')]
RUNTIME_TARGET = dict(W06='WSV', W07='CIV', W08='CIV', W09='CEV', W10='CIV', W11='CEV', W12='CIV', W13='CEV', W14='CEV', W15='CEV')
COLOR = ''
STATES = []
IDS = {}


class Part:
    def __init__(self, name):
        self.name, self.chunks, self.values = name, [], []

    def points(self, points, state):
        a = np.rint(points).astype(np.int32).reshape(-1, 3)
        self.chunks.append(a)
        self.values.append(np.full(len(a), IDS[state], np.uint8))

    def box(self, a, b, state):
        a, b = np.rint(a).astype(int), np.rint(b).astype(int)
        y, z, x = np.mgrid[a[1]:b[1]+1, a[2]:b[2]+1, a[0]:b[0]+1]
        self.points(np.c_[x.ravel(), y.ravel(), z.ravel()], state)

    def beam(self, a, b, radius, state):
        a, b = np.asarray(a, float), np.asarray(b, float)
        lo, hi = np.floor(np.minimum(a, b)-radius).astype(int), np.ceil(np.maximum(a, b)+radius).astype(int)
        z, x = np.mgrid[lo[2]:hi[2]+1, lo[0]:hi[0]+1]
        v = b-a
        for y in range(lo[1], hi[1]+1):
            q = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
            t = np.clip((q-a)@v/(v@v), 0, 1)
            self.points(q[np.linalg.norm(q-a-t[:, None]*v, axis=1) <= radius], state)

    def ring(self, c, radius, inner, depth, state, vertical=False):
        u, v = np.mgrid[-radius:radius+1, -radius:radius+1]
        mask = (u*u+v*v <= radius*radius) & (u*u+v*v >= inner*inner)
        u, v = u[mask], v[mask]
        for k in range(depth):
            a = np.c_[u+c[0], v+c[1], np.full(len(u), c[2]+k)] if vertical else np.c_[u+c[0], np.full(len(u), c[1]+k), v+c[2]]
            self.points(a, state)

    def finish(self):
        p, s = np.concatenate(self.chunks)[::-1], np.concatenate(self.values)[::-1]
        low = p.min(0)
        size = p.max(0)-low+1
        q = p-low
        _, at = np.unique((q[:, 1]*size[2]+q[:, 2])*size[0]+q[:, 0], return_index=True)
        self.p, self.states = p[at], s[at]
        return self


def deck(w, d):
    p = Part('01_承台与外围维护廊')
    x, z = np.meshgrid(np.arange(-w//2, w//2+1), np.arange(-d//2, d//2+1))
    keep = abs(x)+abs(z) <= (w+d)//2-28
    q = np.c_[x[keep], np.zeros(keep.sum()), z[keep]]
    for y in [0, 1, 2, 8, 9]:
        p.points(q+[0, y, 0], BLACK if y < 3 else GRAY)
    for x0 in [-w//2+10, w//2-10]:
        p.box([x0-2, 10, -d//2+30], [x0+2, 12, d//2-30], COLOR)
    for z0 in [-d//2+10, d//2-10]:
        p.box([-w//2+30, 10, z0-2], [w//2-30, 12, z0+2], COLOR)
    for x0 in range(-w//2+40, w//2-39, 48):
        p.box([x0-2, 3, -d//2+28], [x0+2, 7, d//2-28], BLACK)
    return p


def module(p, x, z, w, d, height):
    p.box([x-w//2, 10, z-d//2], [x+w//2, 15, z+d//2], BLACK)
    for side in [-1, 1]:
        p.box([x+side*(w//2-3)-2, 16, z-d//2+3], [x+side*(w//2-3)+2, height-4, z+d//2-3], COLOR)
    p.box([x-w//2+5, 16, z-d//2], [x+w//2-5, height-7, z-d//2+4], WHITE)
    p.box([x-w//2+5, 16, z+d//2-4], [x+w//2-5, height-7, z+d//2], WHITE)
    p.box([x-w//2+9, 23, z+d//2], [x+w//2-9, height-14, z+d//2+1], GLASS)
    p.box([x-w//2-2, height-3, z-d//2-2], [x+w//2+2, height, z+d//2+2], WHITE)
    p.box([x-w//2+3, height+1, z-d//2+3], [x+w//2-3, height+3, z+d//2-3], COLOR)
    for dx in range(-w//2+10, w//2-9, 12):
        p.box([x+dx, height+4, z-d//2+9], [x+dx+3, height+6, z+d//2-9], METAL)
    p.box([x-7, 18, z+d//2+2], [x+7, 20, z+d//2+2], LIGHT)


def control(p, c):
    x, y, z = c
    p.box([x-14, 10, z-7], [x+14, y+8, z-1], COLOR)
    p.box([x-7, y-3, z], [x+7, y+4, z], GRAY)
    p.box([x-6, y+5, z], [x+6, y+5, z], LIGHT)
    p.box(c, c, CONTROL)


def w06():
    parts = [deck(352, 390)]
    for i, (z, w, h) in enumerate([(-112, 130, 145), (-38, 190, 108), (36, 244, 72)]):
        p = Part(f'02_{i}_退台深冷阵列')
        module(p, 0, z, w, 68, h)
        for side in [-1, 1]:
            p.beam([side*(w//2-9), 17, z+20], [side*(w//2-9), h+11, z-18], 4, METAL)
        parts.append(p)
    p = Part('03_密封凝态室与冷媒回路')
    module(p, 0, 118, 142, 76, 63)
    for side in [-1, 1]:
        for y in [24, 38]:
            p.beam([side*77, y, 124], [side*151, y, 124], 5, COLOR)
            p.beam([side*151, y, 124], [side*151, y, -135], 5, COLOR)
        for z in [-112, -38, 36]:
            p.box([side*151-12, 17, z-14], [side*151+12, 49, z+14], METAL)
            for dz in range(-12, 13, 4): p.box([side*151-15, 22, z+dz], [side*151+15, 45, z+dz+1], WHITE)
    parts.append(p)
    return parts, [0, 20, 177]


def w07():
    parts = [deck(388, 440)]
    p = Part('02_舟形物质主舱')
    for z in range(-185, 186):
        span = int(56+42*(1-(abs(z)/186)**1.6))
        for y in [17, 18, 19]: p.box([-span, y, z], [span, y, z], BLACK)
        for side in [-1, 1]:
            p.box([side*span-3, 20, z], [side*span+3, 33, z], COLOR)
    for z, h in [(-115, 78), (-30, 102), (68, 90)]: module(p, 0, z, 112, 68, h)
    for side in [-1, 1]:
        p.beam([side*62, 20, 130], [side*34, 126, -80], 5, WHITE)
        p.beam([side*34, 126, -80], [0, 151, -142], 4, COLOR)
    parts.append(p)
    for side in [-1, 1]:
        p = Part(f'03_{side:+d}_侧翼回收工坊')
        for z, h in [(-102, 54), (0, 64), (102, 48)]:
            module(p, side*147, z, 64, 72, h)
            p.box([min(side*147, 0), 18, z-6], [max(side*147, 0), 22, z+6], WHITE)
        p.box([side*147-5, 23, -135], [side*147+5, 25, 135], COLOR)
        parts.append(p)
    return parts, [0, 24, 202]


def w08():
    parts = [deck(388, 412)]
    p = Part('02_恒星坩埚与环形锻铸室')
    for y, r, inner, depth, state in [(10, 117, 0, 8, BLACK), (18, 114, 93, 18, COLOR), (36, 108, 89, 29, METAL), (65, 106, 85, 26, COLOR), (91, 113, 82, 7, WHITE), (98, 112, 91, 6, COLOR)]:
        p.ring([0, y, -24], r, inner, depth, state)
    p.ring([0, 35, -24], 76, 0, 4, GLASS)
    p.ring([0, 39, -24], 38, 0, 5, LIGHT)
    for a in np.arange(8)*math.pi/4:
        v = np.array([math.cos(a), 0, math.sin(a)])
        p.beam(v*132+[0, 10, -24], v*96+[0, 100, -24], 7, BLACK)
        p.beam(v*132+[0, 18, -24], v*99+[0, 102, -24], 3, WHITE)
    parts.append(p)
    for x, z in [(-144, -90), (144, -90), (-144, 58), (144, 58)]:
        p = Part(f'03_{x}_{z}_热端回收塔')
        module(p, x, z, 58, 64, 136)
        for y in range(28, 125, 10): p.box([x-31, y, z-29], [x+31, y+2, z+29], METAL)
        parts.append(p)
    p = Part('04_铸流前庭与连续锻床')
    for x in [-60, 0, 60]:
        p.box([x-15, 12, 91], [x+15, 26, 178], BLACK)
        p.box([x-8, 27, 96], [x+8, 28, 173], COLOR)
        for z in [116, 154]:
            p.box([x-24, 12, z-6], [x-17, 68, z+6], WHITE)
            p.box([x+17, 12, z-6], [x+24, 68, z+6], WHITE)
            p.box([x-24, 69, z-8], [x+24, 74, z+8], METAL)
    parts.append(p)
    return parts, [0, 20, 191]


def w09():
    parts = [deck(410, 390)]
    for side in [-1, 1]:
        p = Part(f'02_{side:+d}_卷轴档案翼')
        for i, z in enumerate(range(-132, 133, 22)):
            x = side*(91+int(31*math.sin((z+132)/264*math.pi)))
            h = 58+int(47*math.sin((z+132)/264*math.pi))
            p.box([x-33, 13, z-8], [x+33, h, z+8], BLACK)
            p.box([x-35, h+1, z-10], [x+35, h+4, z+10], WHITE)
            for y in range(23, h-6, 13):
                p.box([x-30, y, z+9], [x+30, y+4, z+10], COLOR)
                p.box([x-27, y+5, z+9], [x+27, y+6, z+9], LIGHT)
            p.box([x-32, 14, z-9], [x+32, 19, z-9], METAL)
        parts.append(p)
    p = Part('03_共识议场与交织廊')
    p.ring([0, 11, 0], 71, 0, 7, WHITE)
    p.ring([0, 18, 0], 65, 58, 5, COLOR)
    p.ring([0, 18, 0], 39, 0, 4, GLASS)
    for z in [-110, -44, 44, 110]: p.box([-174, 11, z-5], [174, 15, z+5], WHITE)
    for side in [-1, 1]:
        p.box([side*170-4, 16, -145], [side*170+4, 20, 145], COLOR)
        p.beam([side*57, 14, -95], [side*50, 119, -105], 5, METAL)
    p.box([-52, 83, -108], [52, 126, -102], WHITE)
    p.box([-45, 90, -101], [45, 119, -101], COLOR)
    for x in range(-36, 37, 12): p.box([x, 93, -100], [x+3, 116, -100], LIGHT)
    parts.append(p)
    return parts, [0, 20, 177]


def w10():
    parts = [deck(394, 394)]
    p = Part('02_下沉奇点井与铸造环')
    for y, r, inner, depth, state in [(10, 119, 93, 10, BLACK), (20, 115, 94, 20, WHITE), (40, 109, 90, 20, COLOR), (60, 102, 86, 20, METAL), (80, 100, 80, 10, COLOR), (90, 115, 80, 8, WHITE)]:
        p.ring([0, y, 0], r, inner, depth, state)
    p.ring([0, 14, 0], 83, 0, 3, GLASS)
    p.ring([0, 17, 0], 28, 0, 4, LIGHT)
    for side in [-1, 1]:
        for axis in [0, 2]:
            a = np.array([0, 15, 0]); a[axis] = side*168
            b = np.array([0, 174, 0]); b[axis] = side*78
            p.beam(a, b, 10, BLACK)
            p.beam(a+[0, 4, 0], b+[0, 2, 0], 4, COLOR)
    p.ring([0, 166, 0], 89, 77, 8, WHITE)
    p.ring([0, 174, 0], 84, 80, 4, COLOR)
    parts.append(p)
    p = Part('03_四域铸造站与维护桥')
    for x, z in [(-143, -114), (143, -114), (-143, 114), (143, 114)]: module(p, x, z, 68, 70, 57)
    for x in [-130, 130]: p.box([x-5, 11, -156], [x+5, 15, 156], METAL)
    for z in [-130, 130]: p.box([-156, 11, z-5], [156, 15, z+5], WHITE)
    parts.append(p)
    return parts, [0, 20, 183]


def w11():
    parts = [deck(420, 420)]
    for iz, z in enumerate([-135, -45, 45, 135]):
        for ix, x in enumerate([-140, 0, 140]):
            p = Part(f'02_{iz}_{ix}_独立工业节点')
            h = 48+((iz*3+ix)*23)%64
            module(p, x, z, 68+(ix%2)*12, 62, h)
            p.box([x-4, h+7, z-4], [x+4, h+18, z+4], COLOR)
            p.box([x-2, h+19, z-2], [x+2, h+21, z+2], LIGHT)
            parts.append(p)
    p = Part('03_低位调度母线与中转庭')
    for x in [-91, 91]:
        p.box([x-7, 11, -174], [x+7, 17, 174], WHITE)
        p.box([x-2, 18, -174], [x+2, 19, 174], COLOR)
    for z in [-180, -90, 0, 90, 180]:
        p.box([-180, 11, z-5], [180, 15, z+5], METAL)
        p.box([-180, 16, z-1], [180, 17, z+1], COLOR)
    parts.append(p)
    return parts, [0, 20, 194]


def w12():
    parts = [deck(390, 490)]
    for side in [-1, 1]:
        p = Part(f'02_{side:+d}_分段能量约束壁')
        x = side*112
        p.box([x-18, 10, -210], [x+18, 23, 210], BLACK)
        for i, z in enumerate(range(-180, 181, 60)):
            p.box([x-11, 24, z-24], [x+11, 99, z+24], COLOR)
            p.box([x-14, 100, z-27], [x+14, 106, z+27], WHITE)
            p.box([x-13, 34, z-18], [x+13, 89, z+18], GLASS)
            for dy in [27, 94]: p.box([x-16, dy, z-27], [x+16, dy+3, z+27], METAL)
            p.box([x-18, 24, z-3], [x+18, 113, z+3], WHITE)
            p.box([x-19, 47, z-2], [x+19, 79, z+2], LIGHT)
        p.box([x-34, 11, -217], [x-23, 15, 217], WHITE)
        p.box([x+23, 11, -217], [x+34, 15, 217], WHITE)
        parts.append(p)
    p = Part('03_中央试验域与端部门廊')
    p.box([-73, 10, -174], [73, 13, 174], METAL)
    for z in [-211, 211]:
        for side in [-1, 1]:
            p.box([side*91-8, 10, z-8], [side*91+8, 139, z+8], WHITE)
        p.box([-99, 140, z-9], [99, 147, z+9], COLOR)
        p.box([-78, 148, z-5], [78, 150, z+5], LIGHT)
    parts.append(p)
    return parts, [0, 20, 231]


def w13():
    parts = [deck(392, 420)]
    p = Part('02_中央控制中枢与闭合回收廊')
    module(p, 0, 0, 102, 108, 128)
    for x in [-150, 150]:
        p.box([x-10, 11, -164], [x+10, 16, 164], WHITE)
        p.box([x-11, 17, -164], [x-8, 35, 164], COLOR)
        p.box([x+8, 17, -164], [x+11, 35, 164], COLOR)
        p.box([x-7, 36, -164], [x+7, 38, 164], GLASS)
    for z in [-164, 164]:
        p.box([-160, 11, z-10], [160, 16, z+10], WHITE)
        p.box([-160, 36, z-10], [160, 38, z+10], GLASS)
    parts.append(p)
    for side in [-1, 1]:
        p = Part(f'03_{side:+d}_交错演算实验翼')
        for i, z in enumerate([-101, -22, 67]):
            x = side*(83+(i%2)*23)
            module(p, x, z, 62, 60, 72+i*12)
            p.box([min(x, 0), 18, z-5], [max(x, 0), 23, z+5], METAL)
            p.ring([x, 24, z], 17, 12, 15, COLOR)
            p.ring([x, 39, z], 16, 0, 2, LIGHT)
        parts.append(p)
    p = Part('04_后场样本隔离与可替换模块座')
    for x in [-84, 0, 84]:
        module(p, x, -145, 57, 48, 57)
        p.box([x-15, 58, -156], [x+15, 67, -134], GLASS)
        p.box([x-17, 68, -158], [x+17, 71, -132], COLOR)
    parts.append(p)
    return parts, [0, 20, 194]


def w14():
    parts = [deck(414, 470)]
    for i, z in enumerate([-105, 105]):
        p = Part('02_循环核心' if i == 0 else '03_回收核心')
        p.ring([0, 11, z], 98, 0, 8, BLACK)
        p.ring([0, 19, z], 94, 75, 15, WHITE)
        p.ring([0, 34, z], 89, 73, 18, COLOR)
        p.ring([0, 52, z], 89, 72, 11, METAL)
        p.ring([0, 63, z], 96, 75, 7, WHITE)
        p.ring([0, 24, z], 69, 0, 3, GLASS)
        p.ring([0, 61, z-3], 58, 51, 7, COLOR, True)
        p.ring([0, 62, z-3], 43, 35, 7, WHITE, True)
        for side in [-1, 1]:
            p.beam([side*77, 13, z], [side*48, 126, z], 6, BLACK)
            p.beam([side*77, 18, z], [side*48, 126, z], 3, COLOR)
        p.box([-20, 31, z-17], [20, 46+i*8, z+17], COLOR if i else LIGHT)
        parts.append(p)
    p = Part('04_交叉轮回桥与分流站')
    for side in [-1, 1]:
        p.beam([side*111, 35, -126], [-side*111, 35, 126], 6, WHITE)
        p.beam([side*110, 41, -126], [-side*110, 41, 126], 2, COLOR)
        module(p, side*151, 0, 63, 72, 82)
        p.box([min(side*151, 0), 29, -5], [max(side*151, 0), 34, 5], METAL)
    parts.append(p)
    return parts, [0, 20, 216]


def w15():
    rows = json.loads((LOG/'w15-source-boxes.json').read_text('utf8'))
    palettes = dict(dark=BLACK, white=WHITE, blue=COLOR, gold=COLOR, light=LIGHT, glass=GLASS, metal=METAL, marker=WHITE)
    parts = {}
    names = dict(foundation='01_八角承台', axis='02_朝觐轴与三重门', evidence='03_十四证据庭', sea='04_量子海井', throne='05_空席圣座', tree='06_双干分枝与根系', crown='07_冠环与六支尖塔', service='08_后场汇聚翼')
    for group, x, y, z, w, h, d, mat in rows:
        p = parts.setdefault(group, Part(names[group]))
        p.box([x, y, z], [x+w-1, y+h-1, z+d-1], palettes[mat])
    p = parts['throne']
    p.box([252, 33, 300], [260, 36, 300], GRAY)
    p.box([256, 34, 300], [256, 34, 300], CONTROL)
    return list(parts.values()), [256, 34, 300]


def material_cache(tier):
    cached = json.loads((ROOT/'logs/w05-wind-circuit-a1-20261112/material-cache.json').read_text('utf8'))
    by_state = {m['state']: m for m in cached['materials']}
    template = dict(by_state['hk3gtl:voltage_machine_casing_hdv'])
    image = ROOT/f'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/{tier.lower()}/casing.png'
    url = 'data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()
    template.update(state=COLOR, model=f'hk3gtl:block/voltage_machine_casing_{tier.lower()}', faces={f: url for f in ['east', 'west', 'south', 'north', 'up', 'down']})
    by_state[COLOR] = template
    return [by_state[s] for s in STATES]


def build(entry):
    global COLOR, STATES, IDS
    role, title, tier, color, summary = entry
    COLOR = 'hk3gtl:voltage_machine_casing_'+tier.lower()
    STATES = [COLOR, WHITE, GRAY, METAL, BLACK, LIGHT, GLASS, CONTROL]
    IDS = {s: i+1 for i, s in enumerate(STATES)}
    parts, controller = globals()[role.lower()]()
    if role != 'W15':
        controller[1] = 12
        p = Part('99_前庭嵌墙主控')
        control(p, controller)
        parts.append(p)
    parts = [p.finish() for p in parts]
    points = np.concatenate([p.p for p in parts])
    low, high = points.min(0), points.max(0)
    size = high-low+1
    cube = np.zeros((size[1], size[2], size[0]), np.uint8)
    owner = np.zeros_like(cube)
    for i, p in enumerate(parts, 1):
        at = p.p-low
        cube[at[:, 1], at[:, 2], at[:, 0]] = p.states
        owner[at[:, 1], at[:, 2], at[:, 0]] = i
    name = role.lower()+'-full-candidate-a1-20261113'
    data = dict(name=name, machine_id=role, title=title+' · A1', display_version='A1', size=size.tolist(),
                actual_scene_size_xyz=size.tolist(), blueprint_bounds=dict(min=low.tolist(), max=high.tolist()),
                blueprint_to_export_offset_xyz=(-low).tolist(), controller=(np.array(controller)-low).tolist(),
                controller_blueprint=controller, ports=[], center_blueprint=((low+high)//2).tolist(),
                detail_views={}, palette_identity=dict(tier=tier, color=color, runtime_voltage=RUNTIME_TARGET[role]),
                current_registered_voltage=RUNTIME_TARGET[role],
                summary=summary, approved=False, installed=False, game_verified=False, controller_registered=True,
                controller_marker_only=True, animation_enabled=False, whole_integer_voxel=True, no_nominal_clipping=True,
                design_basis='doc/HK3GTL-内测5/03_机器结构/机器与文明级奇观.html',
                source_conflicts=['原方案工艺分区转译为本轮原创几何；W15保留旧方案逐个体量坐标并撤销旧接口标记。',
                                  '控制器身份已注册；本包使用红石块标明主控，未批准、未挂接正式Pattern。',
                                  '不增加固定接口、孔位或浮空仓；玩家可替换实体非主控位置为合法通用工业接口。',
                                  '构件接合按生成顺序合并，尚未独立验收穿模、美观、搭建成型、运行或性能。'])
    return cube, owner, data, parts


def publish(entry):
    role, title, tier, color, summary = entry
    folder = OUT/role.lower()
    folder.mkdir(parents=True, exist_ok=True)
    cube, owner, data, parts = build(entry)
    result = export_dense(cube, STATES, data['name'], folder)
    surfaces = result.pop('surface_groups')
    size, offset = np.array(data['size']), np.array(data['blueprint_to_export_offset_xyz'])
    flat_owner = owner.ravel()
    previews = []
    for i, p in enumerate(parts, 1):
        low, high = p.p.min(0), p.p.max(0)
        local_size, origin = high-low+1, low+offset
        groups = []
        for material in surfaces:
            faces = []
            for face in material:
                indices = np.asarray(face, dtype=np.int64)
                indices = indices[flat_owner[indices] == i]
                local = ((indices//(size[0]*size[2])-origin[1])*local_size[2]+indices//size[0]%size[2]-origin[2])*local_size[0]+indices%size[0]-origin[0]
                faces.append(local.tolist())
            groups.append(faces)
        starts, lengths, _ = merge_surface_runs(groups, local_size.tolist())
        previews.append(dict(id=p.name, origin=origin.tolist(), size=local_size.tolist(), starts=starts, lengths=lengths, blocks=int(np.count_nonzero(flat_owner == i)), source_blocks=len(p.p)))
    data['blocks'] = result['block_count']
    data['component_bounds_blueprint'] = {p.name: dict(min=p.p.min(0).tolist(), max=p.p.max(0).tolist(), blocks=len(p.p)) for p in parts}
    audit = dict(**result, no_nominal_clipping=True, animation_enabled=False, game_verified=False, approved=False,
                 interface_count=0, scope='既有结构导出器的文件回读结果；不新增测试，不等于外观批准或游戏验收。')
    audit['viewer_rendered_quads'] = sum(len(face) for part in previews for material in part['starts'] for face in material)
    payload = dict(data=data, audit=audit, materials=material_cache(tier), parts=previews)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), 6)).decode()
    (folder/'data.js').write_text('window.W05_STATIC_PAYLOAD='+json.dumps(encoded)+';', 'utf8')
    counts = np.bincount(cube.ravel(), minlength=len(STATES)+1)
    bom = [dict(state=s, count=int(counts[i+1]), role='主控占位' if s == CONTROL else '建筑实体材料') for i, s in enumerate(STATES)]
    for name, value in [('manifest.json', data), ('verification.json', audit), ('材料清单.json', bom)]:
        (folder/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')
    scripts = folder/'生成脚本'
    scripts.mkdir(exist_ok=True)
    package.g = SimpleNamespace(ROOT=ROOT)
    package.viewer(scripts)
    ui = scripts/'w05-review-ui.mjs'
    ui.write_text(ui.read_text('utf8').replace("link.download='W05-长风环流阵.png'", "link.download=config.data.machine_id+'-完整静态候选.png'"), 'utf8')
    page = package.review_page(data, parts, bom).replace('W05', role).replace('长风·理想流体环流阵', title)
    page = page.replace('风息绿', tier+'律者色').replace('#48C9A3', color)
    page = page.replace('风之律者 · ', role+' · ').replace('双层闭合回流', '完整静态候选')
    page = page.replace('HDV '+tier+'律者色', tier+'律者色').replace('原创工业风洞', '既定工艺分区')
    page = page.replace('整流核心', '核心').replace('主控接口', '主控定位')
    page = page.replace('主控红石块是未注册控制器的明确占位', '红石块仅标明已注册主控的候选坐标')
    page = page.replace('运行目标 WSV', '运行目标 '+data['palette_identity']['runtime_voltage'])
    page = page.replace(f'href="index.html">← {role}方案与状态', 'href="../index.html">← 十座候选总览')
    (folder/'index.html').write_text(page, 'utf8')
    print(json.dumps(dict(role=role, size=data['size'], blocks=data['blocks'], parts=len(parts)), ensure_ascii=False), flush=True)
    return dict(role=role, title=title, size=data['size'], blocks=data['blocks'], parts=len(parts), approved=False,
                preview=f'{role.lower()}/index.html', nbt=f'{role.lower()}/{data["name"]}.nbt')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    selected = [e for e in ENTRIES if len(sys.argv) == 1 or e[0] in sys.argv[1:]]
    rows = [publish(e) for e in selected]
    (LOG/'candidate-builds.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', 'utf8')


if __name__ == '__main__':
    main()
