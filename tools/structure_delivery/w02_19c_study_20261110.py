# -*- coding: utf-8 -*-
"""普通理之律者19C静态造型小样；未与毕业船坞合并。"""
from pathlib import Path
import math
import numpy as np
from scipy.spatial import ConvexHull
from w02_bunny_dock_geometry_v3_20261108 import Part as BasePart, encode

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W02_理之律者19C_静态造型小样_V1_20261110'
LOG = ROOT / 'logs/w02-19c-static-20261110'
WHITE, BLACK, BLUE, PALE = ('minecraft:white_concrete', 'minecraft:deepslate_tiles',
                           'minecraft:light_blue_concrete', 'minecraft:blue_ice')
GRAY, SILVER, LIGHT = 'minecraft:gray_concrete', 'minecraft:light_gray_concrete', 'minecraft:sea_lantern'
GLASS, ORANGE = 'minecraft:blue_stained_glass', 'minecraft:orange_stained_glass'
STATES = [WHITE, BLACK, BLUE, PALE, GRAY, SILVER, LIGHT, GLASS, ORANGE]
IDS = {s: i+1 for i, s in enumerate(STATES)}
ROLES = dict(zip(STATES, ['白色外装甲', '深色关节及装甲内衬', '构造蓝主装甲', '浅蓝切面',
                        '机械骨架', '关节轴承', '静态发光节点', '构造蓝观察窗', '小面积橙色核心']))


class Part(BasePart):
    def points(self, points, state):
        p = np.rint(points).astype(np.int32).reshape(-1, 3)
        if not len(p):
            return
        assert np.all(np.abs(p) < 2048), '坐标只验证、不裁切'
        self.chunks.append(p)
        self.values.append(np.full(len(p), IDS[state], np.uint8))


def hull(part, vertices, state, hollow=0):
    vertices = np.array(vertices, float)
    equations = ConvexHull(vertices).equations
    low, high = np.floor(vertices.min(0)).astype(int), np.ceil(vertices.max(0)).astype(int)
    z, x = np.mgrid[low[2]:high[2]+1, low[0]:high[0]+1]
    for y in range(low[1], high[1]+1):
        p = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        distance = p @ equations[:, :3].T + equations[:, 3]
        keep = np.max(distance, axis=1) <= .001
        if hollow:
            keep &= np.max(distance, axis=1) >= -hollow
        part.points(p[keep], state)


def plate(part, outline, back, front, state, bevel=0):
    xy = np.array(outline, float)
    center = xy.mean(0)
    inset = center+(xy-center)*.87 if bevel else xy
    vertices = np.vstack([np.c_[xy, np.full(len(xy), back)],
                          np.c_[xy, np.full(len(xy), front-bevel)],
                          np.c_[inset, np.full(len(xy), front)]])
    hull(part, vertices, state)


def disk(part, center, radius, depth, state, hole=0):
    x, y, z = center
    yy, zz = np.mgrid[-math.ceil(radius):math.ceil(radius)+1, -math.ceil(radius):math.ceil(radius)+1]
    r2 = yy*yy+zz*zz
    mask = (r2 <= radius*radius) & (r2 >= hole*hole)
    for xx in np.arange(x-depth/2, x+depth/2+.1):
        part.points(np.c_[np.full(mask.sum(), xx), yy[mask]+y, zz[mask]+z], state)


def chest():
    p = Part('19C胸甲与悬浮下机体')
    outline = [(-72,267), (72,267), (83,242), (57,200), (38,161), (0,125), (-38,161), (-57,200), (-83,242)]
    plate(p, outline, -47, 7, BLACK, 9)
    # 正面参考中可见的V形胸甲与尖下颌；背面厚度属于待核对转译。
    for side in (-1, 1):
        panel = [(side*x, y) for x,y in [(8,258),(68,268),(77,246),(47,203),(8,179),(27,217)]]
        plate(p, panel, 5, 22, WHITE, 5)
        for y,x in [(250,51),(235,49),(220,34)]:
            p.beam([side*x,y,23],[side*(x-15),y-7,23],.9,SILVER)
        for x,y in [(61,247),(49,228),(31,209)]:
            p.sphere([side*x,y,23],1.5,GRAY)
        blue = [(side*x,y) for x,y in [(8,184),(47,207),(36,175),(0,141)]]
        plate(p, blue, 8, 27, BLUE, 4)
        edge = [(side*x,y) for x,y in [(0,149),(36,179),(25,164),(0,137)]]
        plate(p, edge, 26, 30, PALE)
        plate(p, [(side*x,y) for x,y in [(52,231),(82,253),(91,244),(62,215)]], -37, -14, BLUE, 4)
        for y in range(178,239,13):
            p.box([side*48-2,y,-49],[side*48+2,y+5,-45],SILVER)
        for dx in range(17,42,9):
            p.box([side*dx-2,167,-40],[side*dx+2,178,-26],BLACK)
        # 下方短装甲荚不补成人形双腿。
        plate(p, [(side*x,y) for x,y in [(22,177),(49,180),(55,156),(29,140),(18,150)]], -45,-10,WHITE,4)
        p.box([side*35-7,143,-34],[side*35+7,146,-18],LIGHT)
    plate(p,[(-24,252),(0,264),(24,252),(0,200)],20,29,GRAY,3)
    hull(p,[(0,259,31),(-15,246,31),(15,246,31),(0,211,31),(0,242,40)],ORANGE)
    p.box([-6,236,30],[6,250,31],LIGHT)
    plate(p,[(-13,164),(0,177),(13,164),(0,150)],30,33,WHITE,2)
    hull(p,[(0,172,34),(-6,164,34),(6,164,34),(0,155,34),(0,164,38)],ORANGE)
    return p.finish()


def arm(side):
    p = Part('19C'+('左' if side<0 else '右')+'分节机械臂与装甲')
    def q(v):
        return np.array(v)*[side,1,1]
    shoulder, elbow, wrist = q([86,249,-21]), q([140,211,-8]), q([164,156,48])
    for c,r in [(shoulder,22),(elbow,18),(wrist,13)]:
        p.sphere(c,r,BLACK)
        disk(p,c,r*.79,12,SILVER,hole=r*.5)
        disk(p,c+[side*7,0,0],r*.49,3,BLUE,hole=r*.28)
    for a,b,segments in [(shoulder,elbow,5),(elbow,wrist,6)]:
        p.beam(a,b,6,GRAY)
        for t in np.linspace(.1,.9,segments):
            c=a+(b-a)*t
            p.sphere(c,10,BLACK)
            p.box(c-[6,4,8],c+[6,4,8],GRAY)
            p.box(c+[-5,-2,8],c+[5,2,10],SILVER)
        p.beam(a+[0,0,9],b+[0,0,9],1.4,SILVER)
    panel=[(side*x,y) for x,y in [(131,209),(151,218),(182,182),(177,143),(154,151),(144,180)]]
    plate(p,panel,16,41,BLUE,5)
    ridge=[(side*x,y) for x,y in [(149,211),(155,205),(173,172),(165,158),(155,180)]]
    plate(p,ridge,40,46,PALE,2)
    inset=[(side*x,y) for x,y in [(141,202),(146,200),(154,174),(148,175)]]
    plate(p,inset,41,44,BLACK)
    return p.finish()


def hand(side):
    p = Part('19C'+('左' if side<0 else '右')+'展开机械手')
    mirror = np.array([side,1,1])
    center = np.array([163.,132.,69.])
    # 手掌留出各指间的透空；不以实体大拳头替代分节机械手。
    plate(p,[(side*x,y) for x,y in [(142,155),(179,158),(193,134),(178,111),(148,116),(137,134)]],49,82,BLACK,4)
    plate(p,[(side*x,y) for x,y in [(160,153),(178,153),(188,134),(176,117),(161,119)]],80,88,BLUE,2)
    disk(p,[side*181,135,68],12,5,GRAY,hole=7)
    for i in range(4):
        root=center+[-13+8*i, -9, 9]
        joint=root+[-12+4*i,-18,16]
        tip=joint+[-14+4*i,2,16]
        root,joint,tip=[v*mirror for v in [root,joint,tip]]
        p.beam(root,joint,4.4,BLACK)
        p.sphere(joint,5.4,GRAY)
        p.beam(joint,tip,4,BLUE)
        p.beam(tip,tip+[side*(-4+i),2,5],2.5,PALE)
    a=np.array([143,139,80])*mirror
    b=np.array([124,125,91])*mirror
    c=np.array([129,111,108])*mirror
    p.beam(a,b,5,BLACK);p.sphere(b,6,GRAY);p.beam(b,c,5,BLUE)
    return p.finish()


def build():
    parts=[chest(),arm(-1),arm(1),hand(-1),hand(1)]
    points=np.concatenate([p.p for p in parts]);low,high=points.min(0),points.max(0)
    size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for part in parts:
        at=part.p-low
        cube[at[:,1],at[:,2],at[:,0]]=part.states
    overlaps=[]
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            shared=np.intersect1d(encode(a.p),encode(b.p),assume_unique=True)
            if not len(shared):
                continue
            is_joint=('胸甲' in a.name and '机械臂' in b.name) or ('机械臂' in a.name and a.name[3]==b.name[3] and '机械手' in b.name)
            overlaps.append(dict(first=a.name,second=b.name,shared_voxels=len(shared),
                                 classification='机械接合，尚未逐材质验收' if is_joint else '待核对交叠'))
    data=dict(name='hk3gtl-w02-19c-study-v1-20261110',title='理之律者 · 重装小兔19C · 静态造型小样',
              candidate_version='19C-V1造型小样',size=size.tolist(),blueprint_to_export_offset_xyz=(-low).tolist(),
              blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),animation_enabled=False,
              blocks=int(np.count_nonzero(cube)),controller=None,ports=[],
              center_blueprint=[0,195,10],palette_identity=dict(tier='HBV',name='构造蓝',color='#428DFF',runtime_voltage='WSV'),
              component_bounds_blueprint={p.name:dict(min=p.p.min(0).tolist(),max=p.p.max(0).tolist()) for p in parts},
              component_overlaps=overlaps,source_conflicts=[
                  '本件为独立19C造型研究，不是已完成的649×493×303毕业工业矩阵。',
                  '正面截图顶部被取景截断；未补造耳翼、肩炮或十二翼。',
                  '背面、遮挡处关节与手指深度采用体素转译，仍需完整19C多视图核对。',
                  '构造蓝#428DFF是身份基准；现有浅蓝混凝土与蓝冰为可用材质近似，不声称纹理像素等于该色值。',
                  '胸甲橙色晶核仅作参考图的小面积点缀；不是空律配色或金色主装甲。'],
              scope='普通理之律者；不采用真理之律者造型，不继承十二翼候选',
              nominal_matrix_size_xzy=[649,493,303],matrix_layout_complete=False,
              approved=False,installed=False,game_verified=False)
    return cube,data,parts
