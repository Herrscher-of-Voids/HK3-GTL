# -*- coding: utf-8 -*-
"""I44 V2：负责人指定的车站式信标，独立建筑几何。"""
from pathlib import Path
import math
import numpy as np
from i44_beacon_geometry_v1_20261029 import Material

ROOT = Path(__file__).resolve().parents[2]
W, H, D, CX = 281, 209, 741, 140
NAME = 'hk3gtl-i44-station-v2-20261029'
TITLE = '仿制的千界一乘·信标 · 穹顶站台与坐标调度总站'
material = Material()
STATES = sorted(v for k, v in vars(Material).items() if k.isupper())
IDS = {s: i + 1 for i, s in enumerate(STATES)}
ROLES = {getattr(material, k): v for k, v in dict(
    QCV='站房、拱顶承力带、站台边墙与调度机房的主机壳',
    CONTROL='站房正面中央坐标登记柜的唯一预览主控',
    PORT='坐标登记、复测、联锁、供能与冷却设备的内嵌接口',
    CLEAN='拱梁、檐口、门窗和站台候车棚的浅银金属框',
    FRAME='轨道床、承台、站房柱脚和雨棚承力构件',
    VIBRATION='坐标测定工位的独立隔振支座',
    ASSEMBLY='进站坐标校准导向座与联锁设备架',
    VENT='侧翼调度机房与冷却设备的散热百叶',
    INSULATE='双轨间隔离层和坐标配电柜绝缘内衬',
    GEAR='道岔联锁和站台测量装置的机械锁定箱',
    PIPE='侧翼冷却水循环管和站台维护支路',
    GRATE='站台检修带、渡线桥和设备维护步道',
    HOT_PIPE='调度机房独立闭式回路主管',
    FROST='冷却机房低温隔离舱',
    TURBINE='侧翼换热设备外罩',
    POWER='供能机房及站台联锁配电设备',
    INERT='目的地资料交接与坐标登记柜内衬',
    STRESS='长跨雨棚的拱脚和抗侧向位移支座',
    GLASS='拱顶透光带、端部拱窗和调度室观测窗',
    COMPUTER='目的地复测、班次联锁与无人任务记录机架',
    LASER='轨道两端的坐标复测光学头',
    BLUE_GLASS='沿站台少量许可目标指示光窗',
    BLACK_GLASS='站钟底盘、站台指示板和调度暗屏',
    GOLD='站钟刻度、少量门楣和信标锁定标识',
    LIGHT='站房、雨棚、候车区和维护通道照明'
).items()}


def build():
    cube = np.zeros((H, D, W), dtype=np.uint8)
    m = material

    def box(a, b, state):
        x, y, z = a; X, Y, Z = b
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D, (a, b)
        cube[y:Y + 1, z:Z + 1, x:X + 1] = IDS[state] if state else 0

    def shell(a, b, state, t=4):
        box(a, b, state)
        if all(b[i] - a[i] + 1 > 2*t for i in range(3)):
            box(tuple(v+t for v in a), tuple(v-t for v in b), None)

    def line(a, b, state, radius=1):
        a, b = np.asarray(a), np.asarray(b)
        for p in np.rint(np.linspace(a, b, max(abs(b-a))+1)).astype(int):
            lo = np.maximum(p-radius, 0); hi = np.minimum(p+radius, [W-1, H-1, D-1])
            box(tuple(lo), tuple(hi), state)

    # Station foundations are split between the head house and the open railway hall.
    box((0, 0, 0), (280, 3, 100), m.FRAME)
    box((30, 0, 101), (250, 3, 740), m.FRAME)
    box((0, 4, 0), (280, 7, 99), m.QCV)
    # Two raised passenger platforms leave the central railway bed open.
    for a, b in ((38, 78), (202, 242)):
        box((a, 4, 100), (b, 17, 740), m.QCV)
        box((a, 18, 100), (b, 21, 740), m.CLEAN)
        edge = b-2 if a < CX else a+2
        box((edge, 21, 107), (edge+1, 21, 734), m.GOLD)
        box((a+8, 21, 107), (a+11, 21, 734), m.GRATE)
    # Railway sleepers, rails, and the deliberately visible central track well.
    box((85, 4, 100), (195, 6, 740), m.INSULATE)
    for z in range(105, 739, 12):
        box((91, 7, z), (189, 9, z+4), m.FRAME)
    for x in (104, 174):
        box((x, 7, 100), (x+2, 12, 740), m.STRESS)
        box((x, 13, 100), (x+2, 14, 740), m.CLEAN)
    # The two head-house wings carry coordinate administration and real equipment.
    for a, b in ((0, 83), (197, 280)):
        shell((a, 8, 16), (b, 72, 100), m.QCV, 5)
        box((a, 73, 12), (b, 77, 105), m.CLEAN)
        box((a+5, 78, 20), (b-5, 83, 100), m.QCV)
        for y in (26, 50):
            for x in range(a+13, b-8, 22):
                box((x, y, 16), (x+11, y+13, 20), m.GLASS)
                box((x-2, y-2, 15), (x+13, y-1, 20), m.CLEAN)
        for x in (a+5, b-10):
            box((x, 9, 12), (x+5, 72, 21), m.CLEAN)
        box((a+10, 33, 25), (b-10, 36, 91), m.GRATE)
        for z in (35, 68):
            box((a+14, 9, z), (a+34, 16, z+14), m.VIBRATION)
            box((a+14, 17, z), (a+34, 27, z+14), m.COMPUTER)
            box((a+14, 28, z), (a+34, 29, z+14), m.BLACK_GLASS)
        # An attached, lower cooling/maintenance room, not a decorative tower.
        xx = a+10
        shell((xx, 8, 108), (xx+53, 43, 174), m.FROST, 4)
        box((xx, 44, 108), (xx+53, 47, 174), m.TURBINE)
        for z in range(114, 171, 12):
            box((xx+4, 48, z), (xx+49, 51, z+4), m.VENT)
        for x in (xx+8, xx+40):
            box((x, 9, 92), (x+4, 17, 178), m.PIPE)
        box((xx+23, 9, 92), (xx+29, 22, 178), m.HOT_PIPE)
        box((a+8, 4, 100), (a+68, 7, 178), m.FRAME)
    # Central head house: two flanking entrance doors and a centered coordinate desk.
    shell((84, 8, 16), (196, 88, 100), m.QCV, 5)
    for a, b in ((89, 117), (163, 191)):
        box((a, 9, 16), (b, 46, 20), m.GLASS)
        box((a, 47, 14), (b, 50, 21), m.CLEAN)
    box((121, 9, 16), (159, 37, 23), m.QCV)
    box((124, 23, 15), (156, 33, 20), m.BLACK_GLASS)
    box((124, 35, 15), (156, 36, 20), m.GOLD)
    # Broad, supported entrance canopy; the controller remains on the station wall.
    box((82, 40, 0), (198, 43, 27), m.QCV)
    box((82, 44, 0), (198, 46, 27), m.CLEAN)
    for x in (84, 193):
        box((x, 8, 5), (x+3, 39, 8), m.CLEAN)
    for x in range(95, 190, 18):
        box((x, 39, 8), (x+4, 39, 18), m.LIGHT)
    # Cathedral-like industrial train shed: actual curved, ribbed roof, not a box.
    roof = {}
    for x in range(36, 245):
        y = min(208, int(round(95+113*math.sqrt(max(0, 1-((x-CX)/104)**2)))))
        roof[x] = y
        lower = min(y, roof.get(x-1, y))-3
        upper = max(y, roof.get(x-1, y))
        for z in range(86, 735):
            rib = (z-86)%42 < 5 or z < 93 or z > 728
            # Indigo longitudinal strips ensure a coherent QCV frame; glass skylights remain subordinate.
            state = m.QCV if rib or (abs(x-CX)//13)%3 != 1 else m.GLASS
            box((x, lower, z), (x, upper, z), state)
        if x in (36, 37, 243, 244):
            box((x, 22, 86), (x, y-4, 734), m.QCV)
    for z in range(86, 735, 42):
        for x, y in roof.items():
            box((x, y-6, z), (x, y-4, min(z+4,734)), m.CLEAN)
        for x in (36, 240):
            box((x, 4, z), (x+4, 95, z+4), m.QCV)
            box((x-1, 4, z), (x+5, 14, z+4), m.STRESS)
        # Cantilever brackets are connected to the posts and roof spring line.
        line((40, 47, z+2), (55, roof[55]-6, z+2), m.CLEAN, 2)
        line((240, 47, z+2), (225, roof[225]-6, z+2), m.CLEAN, 2)
    # The glazed front arch and clock make the head house legible as a terminus.
    for x, y in roof.items():
        if 62 <= x <= 218 and y > 89:
            box((x, 89, 86), (x, y-7, 90), m.GLASS)
    for x in range(64, 219, 22):
        if roof[x] > 89:
            box((x, 84, 84), (x+2, roof[x]-8, 92), m.CLEAN)
    box((80, 84, 83), (200, 89, 93), m.QCV)
    # Clock is a flat assembly within the entrance gable, not an appended high tower.
    for x in range(121, 160):
        for y in range(112, 151):
            r2=(x-CX)**2+(y-131)**2
            if r2 <= 19**2:
                box((x,y,81), (x,y,87), m.GOLD if r2>=16**2 else m.BLACK_GLASS)
    line((140,131,79),(140,144,79),m.CLEAN,1)
    line((140,131,79),(150,125,79),m.CLEAN,1)
    box((138,129,79),(142,133,82),m.GOLD)
    # Interior crosswalk, destination boards, seating and small industrial workstations.
    for z in (135, 345, 555):
        for a,b in ((43,73),(207,237)):
            box((a, 22, z), (b, 25, z+10), m.QCV)
            box((a+3, 26, z+7), (b-3, 34, z+10), m.CLEAN)
        for x in (59,219):
            box((x, 21, z+20), (x+3, 62, z+23), m.QCV)
            box((x-7, 49, z+20), (x+10, 62, z+25), m.BLACK_GLASS)
            box((x-7, 63, z+20), (x+10, 65, z+25), m.GOLD)
            box((x-3, 45, z+20), (x+6, 47, z+25), m.LIGHT)
    for z in (118, 692):
        for x in (62,208):
            box((x, 22, z), (x+10, 29, z+16), m.VIBRATION)
            box((x, 30, z), (x+10, 48, z+16), m.ASSEMBLY)
            box((x+2, 49, z+3), (x+8, 59, z+12), m.LASER)
            box((x+3, 38, z-1), (x+7, 45, z+2), m.BLUE_GLASS)
    for a,b in ((8,73),(207,272)):
        shell((a, 9, 47), (b, 29, 88), m.INERT, 4)
        for x in range(a+5,b-8,18):
            box((x,30,58),(x+10,42,78),m.POWER)
            box((x,43,58),(x+10,45,78),m.VENT)
    for x in (50,225):
        for z in range(192, 715, 84):
            box((x, 22, z), (x+5, 30, z+6), m.GEAR)
            box((x, 31, z), (x+5, 32, z+6), m.LIGHT)
    # Eight real wall positions with external access, in the two station wings.
    ports=[]
    labels=('坐标数据登记','有效坐标复测','无人任务调度','站场供能',
            '冷却介质输入','冷却介质返回','I45目的地联锁','观测设备维护')
    for i,(x,y) in enumerate(((19,14),(63,14),(19,42),(63,42),
                               (217,14),(261,14),(217,42),(261,42))):
        box((x-2,y-2,16),(x+2,y+2,21),m.QCV)
        box((x,y,16),(x,y,16),m.PORT)
        ports.append(dict(id=labels[i],pos=[x,y,16],face='north',purpose='候选设备位置；能力与仓室替换另验'))
    box((137,11,16),(143,17,23),m.QCV)
    box((140,14,16),(140,14,16),m.CONTROL)
    zones=[dict(name='车站坐标登记与主控',pos=[140,14,16]),
           dict(name='目的地复测调度厅',pos=[30,19,45]),
           dict(name='许可联锁与无人任务机房',pos=[230,19,45]),
           dict(name='拱顶雨棚与双侧站台',pos=[50,20,345]),
           dict(name='贯通股道与进站测定',pos=[100,14,690])]
    # Markers are anchored to tangible constructions, never arbitrary label air.
    for zone in zones:
        x,y,z=zone['pos']
        if not cube[y,z,x]:
            zone['pos']=[x,7,z] if z<100 else [50,20,z]
    data=dict(key='i44',name=NAME,title=TITLE,candidate_version='V2',size=[W,H,D],
        controller=[140,14,16],controller_face='north',ports=ports,paths=[],zones=zones,
        railway=dict(rail_centers_x=[105,175],gauge_blocks=70,rail_top_y=14,
            platform_inner_edges_x=[78,202],clear_body_width=123),
        description='车站式坐标信标：前部有站钟的站房负责登记、复测与联锁，后部大跨度弧形雨棚覆盖双侧站台和中央股道；深靛蓝QCV承力带与浅银拱肋组织轮廓。I45蒸汽列车是独立固定多方块，可接收本站交接的有效目的地。',
        design_decision='负责人2026-10-29指定：信标做火车站，千界一乘列车做蒸汽火车。',
        original_reference=dict(source='https://comic.bh3.com/book/1021',
            confirmed='保留千界一乘的列车身份，车站作为本项目坐标信标的建筑转译。',
            limit='车站造型为负责人指定的项目设计，不宣称是原作信标建筑复刻。'),
        construction_notes=dict(materials='QCV主机壳主导；浅银拱肋、少量暖金站钟、真实MC玻璃透光带。',
            function='I44登记、复测、锁定与调度目的地；I45固定蒸汽列车执行既定获准旅行。',
            boundary='两个独立多方块，不新增神之键、维度、非法目标或实际移动列车实体。'))
    return cube,data


if __name__=='__main__':
    cube,data=build()
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    print(dict(size=data['size'],blocks=int(counts[1:].sum()),materials=len(STATES),
        qcv=int(counts[IDS[material.QCV]]),unused=[s for s in STATES if not counts[IDS[s]]]),flush=True)
