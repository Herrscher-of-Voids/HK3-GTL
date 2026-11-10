# -*- coding: utf-8 -*-
"""I28从零构图：横轴双闸终止室、渐缩捕获喉与分流回收厂。"""
import collections
import math
from pathlib import Path
from i27_capture_array_geometry_20261026 import (
    IMV,PORT,CONTROL,ROBUST,CLEAN,ASSEMBLY,COMPUTER,ATOMIC,POWER,LASER,
    TURBINE,MACERATOR,VENT,GEAR,TUNG_PIPE,STEEL_PIPE,GRATE,IRIDIUM,PROCESS,
    DIMENSION,MULTI,LAFIUM,GLASS,FILTER,INERT,HEATPROOF,INSULATE,FROST,
    STABLE,SOLID,INTAKE,STRESS,MIXING,BLUE_GLASS,BLACK_GLASS,BLACK,LIGHT)

ROOT=Path(__file__).resolve().parents[2]
W,H,D=301,201,361
CX,CZ=150,180
NAME='hk3gtl-i28-real-world-termination-reclaimer-v1-20261026'
TITLE='真实世界泡终止回收机 · 双闸断界归流炉'
CELLS={}


def put(x,y,z,state,replace=False):
    p=(int(x),int(y),int(z))
    assert 0<=p[0]<W and 0<=p[1]<H and 0<=p[2]<D,p
    if replace or p not in CELLS:CELLS[p]=state


def box(lo,hi,state,replace=False):
    for y in range(lo[1],hi[1]+1):
        for z in range(lo[2],hi[2]+1):
            for x in range(lo[0],hi[0]+1):put(x,y,z,state,replace)


def line(a,b,state,radius=0,replace=False):
    """逐轴补齐斜撑，保证连续承力与六邻接。"""
    steps=max(abs(a[i]-b[i]) for i in range(3));p=list(a)
    for step in range(steps+1):
        end=[round(a[i]+(b[i]-a[i])*step/max(1,steps)) for i in range(3)]
        for axis in range(3):
            while p[axis]!=end[axis]:
                p[axis]+=1 if end[axis]>p[axis] else -1
                box(tuple(v-radius for v in p),tuple(v+radius for v in p),state,replace)
        box(tuple(v-radius for v in end),tuple(v+radius for v in end),state,replace)


def oct_radius(x,y):
    dx,dy=abs(x-CX),abs(y-110)
    return max(dx,dy,(dx+dy)/1.42)


def foundation():
    zones=((47,253,0,360),(0,65,75,278),(235,300,75,278),(20,280,279,360))
    for x0,x1,z0,z1 in zones:
        for x in range(x0,x1+1):
            for z in range(z0,z1+1):
                rim=x in (x0,x1) or z in (z0,z1)
                for y in (0,1,18,19):
                    s=IMV if y in (0,18) or rim or x%20<2 or z%20<2 else GRATE
                    put(x,y,z,s)
                if rim:
                    for y in range(2,18):put(x,y,z,ROBUST if y in (2,17) else IMV)
    # 纵横箱梁承托工艺室，地坪下保留检修空间。
    for x in (49,71,104,149,194,227,249):
        box((x,2,0),(x+2,5,360),IMV)
        box((x,15,0),(x+2,17,360),IMV)
        for z in range(0,D,24):box((x,6,z),(x+2,14,min(z+2,D-1)),IMV)
    for z in range(0,D,24):
        box((47,2,z),(253,5,min(z+2,D-1)),ROBUST)
        box((47,15,z),(253,17,min(z+2,D-1)),ROBUST)
    for x in (0,298):box((x,0,75),(x+2,19,278),IMV)
    # 正面主控操作平台及后侧分流交接平台。
    box((112,20,0),(188,27,7),IMV)
    box((112,27,0),(188,27,7),GRATE,True)
    box((76,20,353),(224,27,360),IMV)
    box((76,27,353),(224,27,360),GRATE,True)


def hall(x0,x1,z0,z1,y0,y1,role):
    for y in range(y0,y1+1):
        for z in range(z0,z1+1):
            for x in range(x0,x1+1):
                wall=x in (x0,x1) or z in (z0,z1)
                if y in (y0,y0+15,y1):put(x,y,z,IMV if wall or x%16<3 else GRATE,True)
                elif wall:
                    along=x-x0 if z in (z0,z1) else z-z0
                    pier=along%18<3 or (x in (x0,x1) and z in (z0,z1))
                    window=(y0+5<=y<=y0+11 or y0+20<=y<=y1-5) and not pier
                    s=BLUE_GLASS if window else IMV
                    if y in (y0+1,y0+14,y0+16,y1-1):s=CLEAN
                    put(x,y,z,s,True)
    n=max(1,(x1-x0-8)//15+1);start=(x0+x1-((n-1)*15+4))//2
    for x in range(start,start+n*15,15):
        box((x,y1+1,z0+4),(x+4,y1+2,z1-4),IMV)
        for z in range(z0+8,z1-5,18):box((x,y1+3,z),(x+4,y1+5,z+5),VENT)
    equipment=(COMPUTER,MULTI,DIMENSION,LAFIUM) if role=='control' else (PROCESS,FILTER,MIXING,MACERATOR)
    for i,x in enumerate(range(x0+8,x1-8,16)):
        for j,z in enumerate(range(z0+8,z1-8,19)):
            box((x,y0+1,z),(x+6,y0+9,z+7),equipment[(i+j)%4],True)
            box((x,y0+10,z),(x+6,y0+10,z+7),GRATE,True)


def process_buildings():
    hall(101,199,8,62,20,56,'control')
    hall(0,54,102,244,20,59,'power')
    hall(246,300,102,244,20,59,'power')
    hall(76,224,282,352,20,61,'recovery')
    hall(20,72,282,345,20,49,'solids')
    hall(228,280,282,345,20,49,'fluids')
    # 输入与终止室之间的轨道托床，控制厅屋面留出容器交接通道。
    box((130,20,63),(170,23,88),IMV)
    for x in (135,163):box((x,24,58),(x+2,27,93),GEAR,True)
    for z in range(66,87,6):box((131,24,z),(169,25,z+1),ASSEMBLY)
    # 终止室两侧可读的维护桥，连接同风格的脉冲供能厅。
    for side in (-1,1):
        x0,x1=(50,86) if side<0 else (214,250)
        for z in (111,199):
            box((x0,62,z),(x1,63,z+11),IMV)
            box((x0,64,z),(x1,64,z),CLEAN)
            box((x0,64,z+11),(x1,64,z+11),CLEAN)
            box((x0+3,20,z+3),(x0+7,61,z+7),ROBUST)


def collar(z0,z1,outer,inner,secondary=False):
    for y in range(max(20,110-outer),min(H,111+outer)):
        for x in range(CX-outer,CX+outer+1):
            r=oct_radius(x,y)
            if not inner<=r<=outer:continue
            for z in range(z0,z1+1):
                state=ATOMIC if secondary else IMV
                if z in (z0,z1):state=CLEAN if not secondary else LAFIUM
                if r>=outer-1.5 and z not in (z0,z1):state=ROBUST
                if r<inner+1.2 and z0+2<=z<=z1-2:state=POWER if secondary else ATOMIC
                put(x,y,z,state,True)


def termination_chamber():
    # 双隔离框围绕横轴终止室；最前端大闸本体给出201格实际高度。
    collar(83,96,90,80)
    collar(102,107,75,69,True)
    collar(207,212,69,63,True)
    collar(218,231,82,72)
    # 后内闸由四个径向斜撑悬架接到外闸，保持双层隔离间距与承力连续。
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        line((CX+dx*66,110+dy*66,210),(CX+dx*77,110+dy*77,222),IMV,2)
    for z in (126,183):collar(z,z+4,87,82)
    # 纵向底舱与侧壳保留观察留白，分段框架有真实落地支撑。
    for y in range(25,168):
        for x in range(64,237):
            r=oct_radius(x,y)
            if 79<=r<=85 and (y<81 or abs(x-CX)>71):
                for z in range(97,218):
                    s=IMV if z%24<18 else ROBUST
                    if 87<=y<=137 and z%44 in range(9,30):s=BLUE_GLASS
                    put(x,y,z,s)
    for z in (88,128,185,224):
        for x in (83,209):
            box((x-6,20,z-8),(x+6,43,z+8),IMV,True)
            box((x-7,20,z-9),(x+7,22,z+9),CLEAN,True)
    # 开敞上部的两根主脊与斜肋呈现磁场压缩方向。
    for side in (-1,1):
        x=CX+side*60
        line((x,166,92),(x,166,224),IMV,3,True)
        line((x,170,92),(x,170,224),CLEAN,1,True)
        for z in (112,153,194):
            line((CX+side*81,62,z),(CX+side*63,165,z),IMV,3)
            line((CX+side*78,66,z-5),(CX+side*59,163,z-5),ROBUST,0)


def target_and_convergence():
    # 一只等半径黑色世界泡；静态目标示意，未实现终止动画。
    center=(CX,110,151);radius=43
    for y in range(67,154):
        for z in range(108,195):
            for x in range(CX-43,CX+44):
                r2=(x-CX)**2+(y-110)**2+(z-151)**2
                if 40**2<=r2<=radius**2:put(x,y,z,BLACK_GLASS if r2>42**2 else BLACK,True)
    # 下方磁靴连向球壳，物质流沿主轴进入渐缩收束喉。
    for x in (CX-24,CX+24):
        line((x,43,151),(x,75,151),BLUE_GLASS,1)
        box((x-5,37,146),(x+5,43,156),POWER,True)
        line((x,37,151),(x,22,151),IMV,2)
    line((CX,110,193),(CX,110,276),BLUE_GLASS,2)
    for z in range(234,278):
        outer=round(79-(z-234)*1.05);inner=outer-6
        for y in range(110-outer,111+outer):
            for x in range(CX-outer,CX+outer+1):
                r=oct_radius(x,y)
                if inner<=r<=outer:
                    # 轴向窗口避免成为看不见内腔的实心圆筒。
                    side=abs(x-CX)>abs(y-110)
                    s=IMV if z%11<8 else CLEAN
                    if side and z%22 in range(5,16):s=GLASS
                    put(x,y,z,s)
    # 物质捕获网连接收束端框，而非无支撑光点。
    collar(278,283,34,27,True)
    for x in range(CX-26,CX+27):
        for y in range(84,137):
            if oct_radius(x,y)<=28 and (x%9==0 or y%9==0):put(x,y,280,BLUE_GLASS,True)
    for side in (-1,1):
        line((CX+side*37,20,271),(CX+side*30,84,279),IMV,4)
        line((CX+side*31,110,283),(CX+side*61,87,314),TUNG_PIPE,2)
        line((CX+side*61,87,314),(CX+side*61,61,314),TUNG_PIPE,2)


def recovery_vessels():
    for cx in (107,193):
        for y in range(66,121):
            for z in range(295,332):
                for x in range(cx-18,cx+19):
                    r=math.hypot(x-cx,z-313)
                    if (16<=r<=18) or (r<=18 and y in (66,67,119,120)):
                        s=IMV
                        if y in (67,68,88,89,118,119):s=CLEAN
                        if y in range(75,84) and abs(z-313)>16:s=BLUE_GLASS
                        put(x,y,z,s)
        for dx in (-11,11):
            for dz in (-11,11):box((cx+dx-1,62,313+dz-1),(cx+dx+1,65,313+dz+1),ROBUST)
        for z in (303,323):
            line((cx-21,62,z),(cx-21,122,z),STEEL_PIPE,0)
            line((cx-21,122,z),(cx,122,z),STEEL_PIPE,0)
            line((cx,122,z),(cx,120,z),STEEL_PIPE,0)
        box((cx-4,121,309),(cx+4,124,317),TURBINE)
    # 回收厅与左右分流舱的侧向封闭输送带。
    box((63,35,308),(83,39,320),PROCESS,True)
    box((217,35,308),(237,39,320),FILTER,True)
    for x in (45,256):
        for z in (294,320):
            box((x-10,50,z-5),(x+10,53,z+5),GEAR)
            box((x-8,54,z-4),(x+8,59,z+4),MACERATOR if x<100 else MIXING)
            box((x-8,60,z-4),(x+8,60,z+4),GRATE)


def plant_details():
    states=(ASSEMBLY,COMPUTER,ATOMIC,LASER,TURBINE,MACERATOR,GEAR,IRIDIUM,
            PROCESS,DIMENSION,MULTI,LAFIUM,GLASS,FILTER,INERT,HEATPROOF,
            INSULATE,FROST,STABLE,SOLID,INTAKE,STRESS,MIXING)
    for side in (-1,1):
        for i,z in enumerate(range(88,275,22)):
            x=28 if side<0 else 272
            box((x-10,20,z-6),(x+10,23,z+6),IMV)
            # 管线设备布置在侧厅之后及屋面之上，不侵入内部作业空间。
            roof=65 if 102<=z<=244 else 24
            if roof==65:box((x-3,60,z-3),(x+3,64,z+3),IMV)
            state=states[(i+(0 if side<0 else 10))%len(states)]
            box((x-6,roof,z-4),(x+6,roof+11,z+4),IMV)
            box((x-5,roof+2,z-5),(x+5,roof+8,z-5),state,True)
            box((x-6,roof+12,z-4),(x+6,roof+12,z+4),VENT)
    # 带实际换热表面的冷却机组，不靠随机堆材增加种类。
    for x in (76,224):
        for i,z in enumerate((48,260,336)):
            box((x-9,20,z-10),(x+9,24,z+10),IMV)
            for dx in (-6,0,6):
                box((x+dx-1,25,z-8),(x+dx+1,49,z+8),FROST)
                box((x+dx-1,50,z-8),(x+dx+1,51,z+8),VENT)
            if z==260:
                line((x,24,z),(x,24,284),STEEL_PIPE,1)
            else:
                inlet=(101 if x<CX else 199) if z==48 else (100 if x<CX else 200)
                line((x,24,z),(inlet,24,z),STEEL_PIPE,1)
    # 隔离闸支座的减振垫、耐压箍与进气格口各有专用位置。
    for x in (83,209):
        for z in (88,224):
            box((x-4,23,z-6),(x+4,24,z+6),SOLID,True)
            box((x-5,27,z-9),(x+5,31,z-9),STRESS,True)
    for x in (25,275):box((x-5,45,101),(x+5,51,101),INTAKE,True)
    for z,y in ((84,194),(219,186)):
        box((CX-23,y,z),(CX+23,y,z+1),LIGHT,True)


def build():
    CELLS.clear();foundation();process_buildings();termination_chamber()
    target_and_convergence();recovery_vessels();plant_details()
    controller=[CX,28,8]
    ports=[{'id':'封存真实世界泡输入','purpose':'前置交接厅输入I27已封存的真实目标','pos':[128,28,8],'face':'north'},
           {'id':'终止耗材输入','purpose':'前置交接厅终止耗材与容器工装','pos':[172,28,8],'face':'north'},
           {'id':'西侧控制能源','purpose':'西侧脉冲控制与隔离供能','pos':[0,29,132],'face':'west'},
           {'id':'维护与隔离检查','purpose':'西侧供能厅维护区','pos':[0,29,213],'face':'west'},
           {'id':'东侧控制能源','purpose':'东侧脉冲控制与隔离供能','pos':[300,29,132],'face':'east'},
           {'id':'研究与终止授权','purpose':'真实目标注销和一次性结算授权候选','pos':[300,29,213],'face':'east'},
           {'id':'物品资源分流','purpose':'物品分流舱输出至现有GT后处理','pos':[20,29,312],'face':'west'},
           {'id':'流体资源分流','purpose':'流体分流舱输出至现有GT后处理','pos':[280,29,312],'face':'east'},
           {'id':'遗留档案与状态记录','purpose':'回收厅后侧输出终止状态与遗留档案','pos':[128,28,352],'face':'south'},
           {'id':'空容器残件输出','purpose':'回收厅后侧输出已注销目标的容器残件','pos':[172,28,352],'face':'south'}]
    directions={'north':(0,0,-1),'south':(0,0,1),'west':(-1,0,0),'east':(1,0,0)}
    for marker in [dict(pos=controller,face='north'),*ports]:
        x,y,z=marker['pos'];dx,_,dz=directions[marker['face']]
        if dz:box((x-1,y-1,z),(x+1,y+1,z),IMV,True)
        else:box((x,y-1,z-1),(x,y+1,z+1),IMV,True)
        put(x-dx,y,z-dz,IMV,True)
        for step in range(1,5):
            for dy in range(4):CELLS.pop((x+dx*step,y+dy,z+dz*step),None)
            # 外侧边界口的脚下通道不延伸导出边界；说明采用实例外部地坪。
            if 0<=x+dx*step<W and 0<=z+dz*step<D:put(x+dx*step,y-1,z+dz*step,GRATE,True)
    put(*controller,CONTROL,True)
    for port in ports:put(*port['pos'],PORT,True)
    return {'key':'I28','id':'I28','name':NAME,'title':TITLE,'size':[W,H,D],
            'target_voltage':'IMV','voltage_mapping':'V09 / tier23','candidate_version':'V1',
            'description':'双层八边隔离闸围绕横轴终止室；渐缩捕获喉将物质流送入后段分类回收厂。',
            'controller':controller,'ports':ports,
            'world_bubble':{'center':[CX,110,151],'radius':43,'shell_inner_radius':40,'shape':'等半径正球壳','meaning':'输入真实目标的静态示意，不表示新增或复制世界泡'},
            'zones':[{'name':'双层隔离终止室','pos':[CX,198,94],'min':[60,20,83],'max':[240,200,231]},
                     {'name':'渐缩物质捕获喉','pos':[CX,153,257],'min':[71,31,234],'max':[229,189,283]},
                     {'name':'封存目标交接与控制厅','pos':[CX,62,36],'min':[101,20,8],'max':[199,61,62]},
                     {'name':'物质稳定与档案回收厅','pos':[CX,127,314],'min':[76,20,282],'max':[224,124,352]},
                     {'name':'物品分流舱','pos':[46,65,312],'min':[20,20,282],'max':[72,60,345]},
                     {'name':'流体分流舱','pos':[254,65,312],'min':[228,20,282],'max':[280,60,345]}],
            'paths':[{'name':'主控操作区','min':[116,28,4],'max':[184,31,7]},
                     {'name':'后侧交接操作区','min':[116,28,353],'max':[184,31,356]}],
            'construction_notes':{'origin':'蓝图0起算，主控朝-Z；格位等于蓝图坐标加1。','paste_y':-60,'world_top_y':140,
                                  'logic':'I27封存目标→受控终止→物品/流体/档案/残件分流；一次结算、注销真实UUID，不重置已采次数。'},
            'blocks':[{'pos':list(p),'state':s} for p,s in sorted(CELLS.items(),key=lambda e:(e[0][1],e[0][2],e[0][0]))]}


if __name__=='__main__':
    data=build();print(len(CELLS),len(set(CELLS.values())),collections.Counter(CELLS.values()).most_common(4))
