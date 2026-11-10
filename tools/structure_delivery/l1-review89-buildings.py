# -*- coding: utf-8 -*-
"""L1五机候选生成：只写独立评审目录，不替换正式Pattern、资源或游戏实例。

【变更记录 #1】2026-09-27（候选89）
删除：无。新增：五座不同构图的逐格候选、材料分层、接口与检修通道。
修改：本文件仅生成候选；精确执行时间写入blueprint与审计，不增加正式修订号。
用途：供负责人先看预览审核；实体、端口、连通检查不等于机器成型验收。
"""
from pathlib import Path
from datetime import datetime
from collections import Counter, deque
import json
import math

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89'
PALETTE = dict(C='gtceu:max_machine_casing', D='gtceu:computer_casing',
               H='gtceu:high_power_casing', K='gtceu:superconducting_coil[active=false]',
               G='gtceu:fusion_glass', L='gtceu:laminated_glass',
               M='gtlcore:molecular_casing', P='kubejs:neutronium_pipe_casing',
               R='kubejs:neutronium_gearbox')
# 变更记录 #2：负责人要求扩大整包选材。以下均从本轮完整模型与真实贴图扫描中选取，
# 分别承担骨架、通风、过滤、场约束、冷却、计算和连接职责，不以随机换色增加数量。
PALETTE.update(B='kubejs:module_base', E='gtlcore:enhance_hyper_mechanical_casing',
               S='gtlcore:iridium_casing', V='gtceu:computer_heat_vent',
               F='gtceu:filter_casing', U='gtceu:sterilizing_filter_casing',
               I='gtceu:engine_intake_casing[active=false]', Q='gtlcore:qft_coil[active=false]',
               W='gtlcore:rhenium_reinforced_energy_glass', T='gtlcore:graviton_field_constraint_casing',
               X='kubejs:dimensional_stability_casing', N='gtlcore:law_filter_casing',
               Y='kubejs:laser_cooling_casing', A='gtceu:advanced_computer_casing',
               Z='gtlcore:super_computation_component[active=false]', O='kubejs:module_connector',
               J='gtlcore:process_machine_casing', P2='kubejs:accelerated_pipeline',
               R2='kubejs:hollow_casing', T2='gtlcore:dimension_connection_casing',
               H2='gtlcore:hyper_core[active=false]', G2='gtlcore:hsss_reinforced_borosilicate_glass',
               K2='kubejs:molecular_coil', V2='gtceu:heat_vent[active=false]',
               Y2='gtlcore:super_cooler_component[active=false]')


class Building:
    def __init__(self, proposal):
        self.meta = proposal
        self.key = proposal['id']
        self.size = proposal['proposed_size']
        self.w, self.h, self.d = self.size
        self.cx, self.cz = self.w // 2, self.d // 2
        self.cells = {}
        self.ports = []
        self.zones = []
        self.paths = []
        self.controller = [self.cx, 2, 2]

    def put(self, x, y, z, material):
        x, y, z = int(x), int(y), int(z)
        assert 0 <= x < self.w and 0 <= y < self.h and 0 <= z < self.d, (self.key, x, y, z)
        self.cells[x, y, z] = PALETTE.get(material, material)

    def box(self, a, b, material):
        for x in range(a[0], b[0] + 1):
            for y in range(a[1], b[1] + 1):
                for z in range(a[2], b[2] + 1):
                    self.put(x, y, z, material)

    def line(self, points, material='P', width=1):
        # 数字折线路径逐轴连接，斜向桁架也保持六邻接，避免只有角点相触。
        for a, b in zip(points, points[1:]):
            steps = max(abs(b[i] - a[i]) for i in range(3))
            last = list(a)
            self.box(tuple(last), tuple(v + width - 1 for v in last), material)
            for k in range(1, steps + 1):
                dest = [round(a[i] + (b[i] - a[i]) * k / steps) for i in range(3)]
                for axis in range(3):
                    while last[axis] != dest[axis]:
                        last[axis] += 1 if last[axis] < dest[axis] else -1
                        self.box(tuple(last), tuple(v + width - 1 for v in last), material)

    @staticmethod
    def oct_distance(x, z):
        return max(abs(x), abs(z)) + .42 * min(abs(x), abs(z))

    def ring(self, cx, cz, r, y, material='D', thick=1):
        for x in range(cx-r, cx+r+1):
            for z in range(cz-r, cz+r+1):
                q = self.oct_distance(x-cx, z-cz)
                if r-thick < q <= r:
                    self.put(x, y, z, material)

    def disk(self, cx, cz, r, y, material):
        for x in range(cx-r, cx+r+1):
            for z in range(cz-r, cz+r+1):
                if self.oct_distance(x-cx, z-cz) <= r:
                    self.put(x, y, z, material)

    def vessel(self, cx, cz, radius, bottom, top, windows=True, taper=True):
        for y in range(bottom, top+1):
            r = radius - (1 if taper and y in (bottom, top) and radius > 2 else 0)
            if y in (bottom, top):
                self.disk(cx, cz, r, y, 'D')
            else:
                self.ring(cx, cz, r, y, 'D' if (y-bottom) % 6 == 0 else 'C')
                if taper and y in (bottom+1,top-1):self.ring(cx,cz,r,y,'D',2)
                if windows and (y-bottom) % 6 in (2, 3, 4):
                    for x, z in ((cx-r, cz), (cx+r, cz), (cx, cz-r), (cx, cz+r)):
                        self.put(x, y, z, 'G')
            if y in (bottom+2, top-2):
                self.ring(cx, cz, radius+1, y, 'D')
        for dx, dz in ((-radius+1, 0), (radius-1, 0), (0, -radius+1), (0, radius-1)):
            self.box((cx+dx, 1, cz+dz), (cx+dx, bottom, cz+dz), 'C')
        for y in range(bottom+3, top-1, 6):
            for dx, dz in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
                self.put(cx+dx, y, cz+dz, 'H')

    def cabinet(self, a, b, front='north', fill='C'):
        x0, y0, z0 = a; x1, y1, z1 = b
        self.box((x0,y0,z0), (x1,y0,z1), 'D')
        self.box((x0,y1,z0), (x1,y1,z1), 'D')
        self.box((x0,y0,z0), (x0,y1,z1), fill)
        self.box((x1,y0,z0), (x1,y1,z1), fill)
        self.box((x0,y0,z0), (x1,y1,z0), fill)
        self.box((x0,y0,z1), (x1,y1,z1), fill)
        # 窗内设置设备条带，不用玻璃包住空盒冒充分析舱。
        for y in range(y0+1,y1):
            for x in range(x0+1,x1):
                self.put(x,y,z0,'L' if front=='north' else fill)
            if (y-y0) % 3 == 1:
                self.box((x0+1,y,z0+1),(x1-1,y,z1-1),'K')

    def base(self):
        for x in range(self.w):
            for z in range(self.d):
                edge = min(x,self.w-1-x)+min(z,self.d-1-z)
                if edge < 3:
                    continue
                mat = 'D' if min(x,self.w-1-x,z,self.d-1-z) in (0,3) else 'C'
                if abs(x-self.cx)<=1 or z in (4,self.d-5): mat='D'
                self.put(x,0,z,mat)
        # 外圈承台只在设备立面形成厚度，入口和操作带保持通畅。
        for x in range(5,self.w-4,5):
            for z in (4,self.d-5):
                if abs(x-self.cx)>2:
                    self.box((x,1,z),(x+1,1,z+1),'C')

    def zone(self, name, pos):
        self.zones.append({'name':name,'pos':pos})

    def finish(self):
        # 三格宽主通道贯穿设备下部；接口步行可达单独核验。
        path = {'name':'贯穿式主检修通道','min':[self.cx-1,1,0],'max':[self.cx+1,4,self.d-1]}
        self.paths.append(path)
        for x in range(self.cx-1,self.cx+2):
            for z in range(self.d):
                for y in range(1,5): self.cells.pop((x,y,z),None)
        def port(pid,x,z,face,group,purpose):
            if face in ('north','south'):self.box((x-1,1,z),(x+1,3,z),'C')
            else:self.box((x,1,z-1),(x,3,z+1),'C')
            self.put(x,2,z,'minecraft:diamond_ore')
            self.ports.append({'id':pid,'pos':[x,2,z],'face':face,'group':group,'purpose':purpose})
        counts=self.meta['ports']
        xs=[4,self.w-5] if counts['item']==2 else [4,9,self.w-5] if counts['item']==3 else [4,9,self.w-10,self.w-5]
        for i,x in enumerate(xs,1):port('M'+str(i),x,2,'north','物品接口','物品输入／输出；同类互换，空余可封闭')
        if counts['fluid']==1:port('F1',self.w-3,self.d-5,'east','流体接口','采集液体输出，必须保留')
        elif counts['fluid']:
            each=counts['fluid']//2;zs=[8,16,25] if each==3 else [7,13,21,28]
            for i,z in enumerate(zs,1):
                port('F'+str(i),2,z,'west','流体接口','建议输入；同类互换，空余可封闭')
                port('F'+str(i+each),self.w-3,z,'east','流体接口','建议输出；同类互换，空余可封闭')
        if counts['parallel']:port('P1',self.w-3,5,'east','扩展接口','可选并行仓，最多1；空余用接口机械方块')
        # 控制台置于通道右侧，避免占用贯穿通道净空。
        self.controller=[self.cx+3,2,2]
        self.box((self.cx+2,1,2),(self.cx+4,3,2),'C')
        self.put(*self.controller,'minecraft:diamond_block')
        d={'key':self.key,'name':'hk3gtl-'+self.key+'-review89','title':self.key.upper()+' '+self.meta['design_name'],
           'description':self.meta['composition'],'details':self.meta['details'],'size':self.size,
           'controller':self.controller,'entrance':[self.cx,0],
           'blocks':[{'pos':list(p),'state':s} for p,s in sorted(self.cells.items())],
           'ports':self.ports,'paths':self.paths,'zones':self.zones,
           'status':'候选待审核，未接入正式机器','generated_at':datetime.now().isoformat()}
        return d


def i01(b):
    c=b.cx;z=b.cz;b.base()
    # 竖向汇聚井与四角压缩机，核心由外肋和内筒共同构成。
    b.vessel(c,z,3,7,30,True,False)
    for y in range(8,31):b.put(c,y,z,'M' if y%4 else 'H')
    for dx,dz in ((-7,-7),(7,-7),(-7,7),(7,7)):
        x,zz=c+dx,z+dz;b.cabinet((x-2,1,zz-2),(x+2,7,zz+2))
        b.line([(x,8,zz),(x,8,z),(c,8,z)],'P')
        for yy in (3,5,7):b.box((x-3,yy,zz-1),(x-3,yy,zz+1),'D')
    for side in range(4):
        def pt(radius,y,t=0):
            return [(c+t,y,z-radius),(c+radius,y,z+t),(c-t,y,z+radius),(c-radius,y,z-t)][side]
        # 冠瓣在高处向内弯折，实体厚度随高度变化；两侧银灰边肋包住深色面板。
        for y in range(5,40):
            rr=6 if y<20 else 6+min(5,(y-20)//3) if y<34 else 10-(y-34)
            half=1 if y<20 else 2 if y<27 else 3
            for t in range(-half,half+1):
                b.put(*pt(rr,y,t),'D' if abs(t)==half else 'C')
                if y>=21:b.put(*pt(rr+1,y,t),'C')
            if y%5==0:b.put(*pt(rr-1,y),'H')
        b.line([pt(6,5),pt(6,19),pt(10,31),pt(10,34),pt(5,39),pt(3,40)],'D')
        b.line([pt(6,10),pt(3,10)],'K')
        b.line([pt(9,29),pt(3,29)],'K')
    for y,r in [(6,6),(17,5),(29,4)]:b.ring(c,z,r,y,'D',2)
    b.disk(c,z,2,40,'K');b.box((c-1,41,z-1),(c+1,41,z+1),'M');b.put(c,42,z,'H')
    for x in (4,b.w-5):
        b.box((x,1,z-2),(x,13,z+2),'C')
        for yy in (4,7,10):b.box((x-1,yy,z-2),(x+1,yy,z+2),'K')
        b.line([(x,13,z),(c,13,z)],'P')
    b.zone('四瓣采集冠',[c,36,z]);b.zone('竖直汇聚井',[c,20,z]);b.zone('压缩与汇流设备',[7,7,7])


def i02(b):
    c=b.cx;b.base()
    # 横向分析轴穿过多层门架；顶层斜梁形成屏蔽拱，而非整片平屋顶。
    for z in (7,13,20,27):
        for x in (c-7,c+7):b.box((x,1,z),(x+1,16,z+1),'C')
        b.line([(c-7,16,z),(c-4,20,z),(c+4,20,z),(c+7,16,z)],'D',2)
        b.line([(c-5,7,z),(c-5,14,z),(c-2,17,z),(c+2,17,z),(c+5,14,z),(c+5,7,z)],'K')
        b.box((c-4,7,z),(c+4,7,z+1),'C');b.put(c,17,z,'H')
        b.box((c-1,8,z),(c+1,9,z),'O')
        for x in (c-3,c+3):b.box((x,8,z),(x,13,z),'D')
    for z in range(5,30):
        b.box((c-1,9,z),(c+1,9,z),'M' if z%6 else 'H')
        for x in (c-3,c+3):b.put(x,10,z,'G');b.put(x,12,z,'D');b.put(x,13,z,'S')
        if z%6 not in (0,1):b.box((c-2,13,z),(c+2,13,z),'G')
    for x,z,top in [(5,7,9),(5,18,12),(26,12,11),(26,24,8)]:
        b.cabinet((x-2,1,z-2),(x+2,top,z+3))
        b.line([(x,top+1,z),(x,top+1,z+2),(c-4 if x<c else c+4,top+1,z+2)],'P')
        for y in range(3,top,2):b.box((x-3,y,z-1),(x-3,y,z+2),'D')
    for x in (c-6,c+6):
        b.cabinet((x-2,1,29),(x+2,14,31))
        b.line([(x,15,30),(x,21,27),(c,21,27)],'C')
        b.put(x,22,27,'H')
    b.zone('分段准直门架',[c,20,13]);b.zone('样本分析轴',[c,12,20]);b.zone('探测与计算机舱',[26,13,12])


def i03(b):
    b.base()
    for x,z,r,top in [(10,22,5,35),(10,9,3,23),(28,25,4,28)]:
        b.vessel(x,z,r,6,top)
        # 两侧独立竖管、变径塔冠和悬挑设备平台。
        for xx in (x-r-2,x+r+2):
            b.line([(xx,1,z),(xx,top-2,z),(x,top-2,z)],'P')
            for yy in range(8,top-2,7):b.line([(x-r,yy,z),(xx,yy,z)],'D')
        for y in range(10,top-3,8):
            b.ring(x,z,r+1,y,'D',1)
            b.box((x-r-1,y,z-1),(x-r-1,y+1,z+1),'C')
        b.put(x,top+1,z,'R')
    # 水平净化舱沿X延伸，与左侧塔群形成不同轴向。
    for x in range(24,35):
        for y in range(5,12):
            for z in range(7,14):
                q=b.oct_distance(y-8,z-10)
                if q<=3 and (q>2 or x in (24,34)):
                    b.put(x,y,z,'D' if x%4==0 else 'G' if y==8 else 'C')
    for x in (25,32):b.box((x,1,8),(x,5,12),'C')
    for x in (23,28,33):b.cabinet((x-1,1,17),(x+1,7,19))
    b.line([(10,18,9),(10,18,16),(28,18,16),(28,18,25)],'P',2)
    b.line([(10,9,22),(18,9,22),(18,9,10),(24,9,10)],'P')
    b.line([(28,13,25),(34,13,25),(34,13,18),(34,7,18)],'P')
    for x in (17,21):b.box((x,1,16),(x,17,17),'C')
    b.box((7,36,21),(13,36,23),'D')
    b.zone('主分馏高塔',[10,34,22]);b.zone('母液回流与净化',[28,13,10]);b.zone('双层跨塔管廊',[20,19,16])


def i04(b):
    c=b.cx;z=b.cz;b.base()
    # 棱面内腔、独立外肋、变半径线圈；外甲间隙可直视核心。
    b.vessel(c,z,5,7,34,True,False)
    for y in range(9,34):
        b.box((c-1,y,z-1),(c+1,y,z+1),'M' if y%5 else 'H')
        if y%5 in (2,3):
            for dx,dz in ((-5,0),(5,0),(0,-5),(0,5)):
                b.put(c+dx,y,z+dz,'G')
    for side in range(4):
        def pt(r,y,t=0):return [(c+t,y,z-r),(c+r,y,z+t),(c-t,y,z+r),(c-r,y,z-t)][side]
        path=[pt(9,1),pt(12,8),pt(13,18),pt(12,28),pt(8,36),pt(4,40)]
        b.line(path,'C',2)
        b.line([pt(10,2,-1),pt(13,8,-1),pt(14,18,-1),pt(13,28,-1),pt(9,36,-1),pt(4,41,-1)],'D')
        for yy,rr in [(10,12),(18,13),(26,12),(34,9)]:
            b.line([pt(rr,yy),pt(6,yy)],'K')
            for t in (-2,-1,0,1,2):b.put(*pt(rr,yy+1,t),'H' if t==0 else 'D')
    for yy,rr in [(8,8),(18,10),(30,7)]:
        b.ring(c,z,rr,yy,'D',2)
        b.ring(c,z,rr,yy+1,'K',1)
    b.disk(c,z,4,40,'C');b.ring(c,z,4,41,'D');b.box((c-1,41,z-1),(c+1,41,z+1),'M');b.put(c,42,z,'H')
    for x in (6,28):
        b.vessel(x,27,2,4,22)
        for yy in range(6,22,4):b.ring(x,27,3,yy,'K')
        b.line([(x,23,27),(x,23,z),(c,23,z)],'P')
        b.line([(x,5,27),(c,5,27),(c,7,z)],'P')
    for x in (7,25):b.cabinet((x-2,1,6),(x+2,6,9))
    b.zone('裂瓣式约束外肋',[c,36,z]);b.zone('棱面稳定核心',[c,24,z]);b.zone('双路冷却塔',[28,22,27])


def i05(b):
    b.base()
    # 高解吸塔、低筒群、冷凝列与尾端处理舱分围中央院落。
    b.vessel(10,23,4,5,26)
    b.ring(10,23,3,27,'D');b.disk(10,23,1,27,'D');b.put(10,28,23,'H')
    for z in (9,19):b.vessel(30,z,3,5,15)
    for z in (7,12,17):
        b.box((5,1,z),(8,12,z+2),'C')
        for y in (3,5,7,9,11):b.box((4,y,z),(9,y,z+2),'K')
        b.line([(8,13,z+1),(12,13,z+1),(12,13,23)],'P')
    for x in (23,29,35):b.cabinet((x-2,1,27),(x+2,10,30))
    b.line([(10,20,23),(16,20,23),(16,20,30),(34,20,30),(34,16,19),(30,16,19)],'P',2)
    for x in (16,24,34):
        b.box((x,1,30),(x,19,31),'C')
        for y in (7,13):b.box((x-1,y,30),(x+1,y,31),'D')
    b.line([(30,16,9),(35,16,9),(35,16,19),(30,16,19)],'P')
    b.line([(10,6,23),(16,6,23),(16,6,9),(30,6,9)],'P')
    # 院落中设置有窗口的低位交换站，其余留作检修院与环廊。
    b.cabinet((14,1,6),(17,7,10))
    b.cabinet((24,1,5),(27,6,8))
    for z in (4,25):b.box((12,0,z),(28,0,z),'D')
    b.zone('解吸高塔',[10,27,23]);b.zone('分列冷凝阵列',[7,14,12]);b.zone('再生与废液处理',[30,16,22])


def validate(data):
    cells={tuple(b['pos']):b['state'] for b in data['blocks']}
    # 所有实体从承台起六邻接连通；候选无随机悬空碎块。
    start=min(cells,key=lambda p:p[1]);seen={start};queue=deque([start])
    while queue:
        p=queue.popleft()
        for axis in range(3):
            for sign in (-1,1):
                q=list(p);q[axis]+=sign;q=tuple(q)
                if q in cells and q not in seen:seen.add(q);queue.append(q)
    missing=set(cells)-seen
    assert not missing,(data['key'],'非连通实体',len(missing),list(missing)[:6])
    # 复用旧交付管线的完整步行路径检查，不以外观可见代替可到达。
    from package_i03_review import validate_paths
    accessible=validate_paths(data)
    c=Counter(cells.values())
    assert c['minecraft:diamond_block']==1
    assert c['minecraft:diamond_ore']==len(data['ports'])
    return {'connected_blocks':len(seen),'accessible_floor_cells':accessible,'palette':dict(c)}


def enrich(b):
    """按具体工艺位置选择材料；仅替换已存在的坐标，保持候选结构与路径。"""
    def replace_zone(lo,hi,old,new):
        for p,s in list(b.cells.items()):
            if s==PALETTE[old] and all(lo[i]<=p[i]<=hi[i] for i in range(3)):
                b.put(*p,new)
    def face(a,z,top,kind):
        # 设备正面纹理：每块本身有进气、滤网、计算或冷却图形。
        for x in range(a[0],a[1]+1):
            for y in range(2,top+1):
                if (x,y,z) in b.cells:b.put(x,y,z,kind)
    for p,s in list(b.cells.items()):
        x,y,z=p
        if y==0 and s==PALETTE['C']:b.put(x,y,z,'B')
        elif y==0 and s==PALETTE['D'] and abs(x-b.cx)>1:b.put(x,y,z,'S')
    if b.key=='i01':
        for dx,dz in ((-7,-7),(7,-7),(-7,7),(7,7)):
            x,z=b.cx+dx,b.cz+dz
            face((x-1,x+1),z-2,5,'I')
            face((x-1,x+1),z+2,5,'V')
            b.put(x,7,z,'H2')
            for y in (2,6):b.put(x-2,y,z,'O');b.put(x+2,y,z,'O')
        replace_zone((0,20,0),(b.w-1,42,b.d-1),'D','S')
        replace_zone((0,30,0),(b.w-1,42,b.d-1),'C','E')
        replace_zone((b.cx-3,8,b.cz-3),(b.cx+3,30,b.cz+3),'G','G2')
        for y in (10,15,20,25,30):b.put(b.cx,y,b.cz,'Q')
        for x in (4,b.w-5):
            for y in (4,7,10):b.put(x,y,b.cz-2,'Y2');b.put(x,y,b.cz+2,'Y2')
            b.put(x,12,b.cz,'X')
        for z in (7,21):b.put(b.cx-7,8,z,'P2');b.put(b.cx+7,8,z,'P2')
    elif b.key=='i02':
        replace_zone((0,14,0),(b.w-1,22,b.d-1),'C','E')
        replace_zone((b.cx-3,8,0),(b.cx+3,13,b.d-1),'G','W')
        replace_zone((b.cx-1,9,5),(b.cx+1,9,29),'M','K2')
        for x,z,top in [(5,7,9),(5,18,12),(26,12,11),(26,24,8)]:
            face((x-1,x+1),z-2,top-1,'A')
            face((x-1,x+1),z+3,top-1,'V')
            b.put(x,top,z,'T2');b.put(x,top-1,z+2,'Z')
        for x in (b.cx-6,b.cx+6):
            face((x-1,x+1),29,13,'Z');face((x-1,x+1),31,13,'Y2')
        for z in (7,13,20,27):b.put(b.cx,17,z,'T');b.put(b.cx,9,z,'Q')
    elif b.key=='i03':
        for x,z,r,top in [(10,22,5,35),(10,9,3,23),(28,25,4,28)]:
            replace_zone((x-r,6,z-r),(x+r,10,z+r),'C','J')
            replace_zone((x-r,top-3,z-r),(x+r,top,z+r),'D','S')
            b.put(x,top,z,'R2')
            for y in range(10,top,6):b.put(x-r,y,z,'O')
        for x in (23,28,33):face((x-1,x+1),17,6,'F');face((x-1,x+1),19,6,'N')
        replace_zone((24,5,7),(34,11,13),'C','E')
        replace_zone((24,5,7),(34,11,13),'G','G2')
        for x in (26,30,33):b.put(x,11,10,'Y');b.put(x,8,7,'U')
        for x in (10,18,28):b.put(x,18,16,'P2')
    elif b.key=='i04':
        replace_zone((0,8,0),(b.w-1,42,b.d-1),'C','E')
        replace_zone((0,8,0),(b.w-1,42,b.d-1),'D','S')
        replace_zone((b.cx-5,7,b.cz-5),(b.cx+5,34,b.cz+5),'G','W')
        replace_zone((0,0,0),(b.w-1,42,b.d-1),'H','T')
        for yy in (12,22,32):b.box((b.cx-1,yy,b.cz-1),(b.cx+1,yy,b.cz+1),'Q')
        for x in (6,28):
            for yy in (6,10,14,18,22):b.put(x-2,yy,27,'Y');b.put(x+2,yy,27,'Y2')
            b.put(x,23,27,'P2')
        for x in (7,25):face((x-1,x+1),6,5,'X');face((x-1,x+1),9,5,'V2')
        b.box((b.cx-1,41,b.cz-1),(b.cx+1,41,b.cz+1),'H2')
    else:
        for x,z in [(10,23),(30,9),(30,19)]:
            replace_zone((x-4,5,z-4),(x+4,9,z+4),'C','J')
        for z in (7,12,17):
            face((5,8),z,11,'Y2');face((5,8),z+2,11,'V2')
            b.put(8,13,z+1,'P2')
        for x in (23,29,35):
            face((x-1,x+1),27,9,'U');face((x-1,x+1),30,9,'N');b.put(x,10,28,'O')
        face((14,17),6,6,'A');face((24,27),5,5,'F')
        for z in (9,19):
            b.put(30,15,z,'H2');b.put(27,11,z,'R2');b.put(33,11,z,'Y')
        replace_zone((0,20,0),(b.w-1,28,b.d-1),'D','S')


if __name__=='__main__':
    proposal=json.loads((ROOT/'logs/revision89/design-proposal.json').read_text(encoding='utf-8'))
    for m in proposal['machines']:
        b=Building(m);globals()[m['id']](b);enrich(b);data=b.finish();audit=validate(data)
        out=OUT/m['id'];out.mkdir(parents=True,exist_ok=True)
        (out/'blueprint.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        (out/'geometry-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
        print(m['id'],data['size'],len(data['blocks']),'实体；连通与接口步行核验通过',flush=True)
