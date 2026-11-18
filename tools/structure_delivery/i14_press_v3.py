# -*- coding: utf-8 -*-
"""I14 V3：四柱曲冠压铸机，工艺内核外露，独立候选不改实装。"""
import math
from i09_i13_v6_common import start, finish, zone, route, PIPE, GEAR, GRATE, PANEL

WHITE = 'gtceu:clean_machine_casing'
BASE = 'gtceu:solid_machine_casing'
POWER = 'gtceu:high_power_casing'
HOT = 'hk3gtl:voltage_machine_casing_hcv'
GLASS = 'gtceu:laminated_glass'
COIL = 'kubejs:titansteel_coil_block[active=false]'
PRECISION = 'gtlcore:multi_functional_casing'
VENT = 'gtceu:computer_heat_vent'
CHEMICAL = 'gtceu:corrosion_proof_casing'


def disk(cx, cz, r):
    return {(x, z) for x in range(cx-r, cx+r+1) for z in range(cz-r, cz+r+1)
            if (x-cx)**2+(z-cz)**2 <= r*r}


def vessel(a, cx, cz, profile, shell, window=False):
    """封闭变径壳以邻层缺口封头，观察缝沿真实容器壁。"""
    disks = {y: disk(cx, cz, r) for y, r in profile.items()}
    for y, cells in disks.items():
        for x, z in cells:
            edge = any((x+dx, z+dz) not in cells for dx in (-1,0,1) for dz in (-1,0,1))
            if edge or (x,z) not in disks.get(y-1,set()) or (x,z) not in disks.get(y+1,set()):
                mat = GLASS if window and abs(x-cx) <= 1 and z < cz and 7 <= y <= 17 else shell
                a.set(x,y,z,mat)


def build():
    a = start('I14','魂钢聚合压铸机',(51,43,47),
              '四柱收腰承力架、双道拱形压梁、中央外露冲头和直线脱模床',
              '左侧熔料保温→低位定量注入下模→四柱液压聚合压铸→后向冷却脱模；右侧蓄压与换热独立')
    # 局部承重基础与输送床；避免用整块空白地板放大占地。
    a.box((19,0,0),(31,0,46),BASE)
    a.box((19,1,9),(31,2,43),POWER)
    for x in (14,36):
        a.box((x-4,0,13),(x+4,1,35),BASE)
    a.box((0,0,28),(10,1,40),BASE)
    a.box((41,0,20),(48,1,30),BASE)
    a.box((42,0,33),(50,1,42),BASE)
    a.box((8,0,6),(42,0,8),BASE)
    a.box((7,0,6),(10,0,26),GRATE)
    a.box((40,0,6),(43,0,16),GRATE)
    a.box((6,0,27),(18,0,29),GRATE)
    a.box((38,0,27),(47,0,29),BASE)
    a.box((38,0,35),(47,0,37),BASE)

    # 四根立柱在受力方向收腰，再向上梁展开；两道梁间保留透视间隙。
    for x in (14,36):
        for z in (17,31):
            a.box((x-3,2,z-3),(x+3,5,z+3),POWER)
            for y in range(6,35):
                radius = 2 if y < 10 or y > 27 else 1
                a.box((x-radius,y,z-1),(x+radius,y,z+1),BASE)
                a.box((x-radius,y,z-1),(x-radius,y,z+1),WHITE)
                a.box((x+radius,y,z-1),(x+radius,y,z+1),WHITE)
            a.box((x-3,31,z-2),(x+3,35,z+2),POWER)
            a.box((x-3,33,z-2),(x+3,33,z+2),HOT)
            # 外侧导压轴和可辨认的上下轴套与主柱保持接触。
            outside = x-3 if x < 25 else x+3
            a.box((outside,5,z),(outside,31,z),PIPE)
            for y in (6,15,25):
                a.box((outside-1,y,z-1),(outside+1,y+1,z+1),GEAR)
    for z0,z1 in ((16,19),(29,32)):
        for x in range(11,40):
            lower = 33+round(7*max(0,1-((x-25)/14)**2))
            a.box((x,lower,z0),(x,min(42,lower+2),z1),POWER)
            a.box((x,lower,z0),(x,lower,z0),WHITE)
            a.box((x,lower,z1),(x,lower,z1),WHITE)
            a.box((x,min(42,lower+2),z0),(x,min(42,lower+2),z1),HOT)
    a.box((22,38,19),(28,41,29),POWER)
    a.box((22,40,20),(28,40,28),WHITE)
    zone(a,'四柱承力与双道曲冠',(10,0,13),(40,42,35),
         '四个独立脚座、收腰柱、双道上拱梁，中央留空展示压铸内核','load_frame')

    # 冲头、移动压板、下模各占独立高度；夹紧位置从侧面即可辨认。
    a.box((23,29,22),(27,38,26),POWER)
    a.box((24,17,23),(26,32,25),PIPE)
    for y in (19,26,32):
        a.box((23,y,22),(27,y+1,26),GEAR)
    a.box((18,14,18),(32,16,30),POWER)
    a.box((18,17,18),(32,17,30),WHITE)
    a.box((20,14,20),(30,14,28),PRECISION)
    a.box((22,13,21),(28,13,27),PRECISION)
    a.box((20,5,19),(30,7,29),POWER)
    a.box((20,8,19),(30,8,29),WHITE)
    a.box((21,9,20),(29,10,28),PRECISION,True)
    a.box((23,9,22),(27,9,26),COIL)
    for x in (18,32):
        a.box((x,3,20),(x,6,28),GEAR)
        a.box((x,7,21),(x,8,27),HOT)
        a.line((x,8,24),(20 if x < 25 else 30,8,24),PRECISION)
    zone(a,'中央聚合压铸工位',(18,3,18),(32,38,30),
         '主液压缸、冲杆、移动压板、中央模具与左右夹紧驱动；无封闭玻璃箱','press')

    # 两条床轨与成组滚子承担直线入料和后向冷却脱模，不把空间装饰成建筑厂房。
    for z0,z1 in ((8,18),(31,46)):
        for x in (21,29):
            a.box((x,3,z0),(x,4,z1),WHITE)
        a.box((22,2,z0),(28,2,z1),BASE)
        for z in range(z0,z1+1,3):
            a.box((22,3,z),(28,3,z),GEAR)
        for x in (23,27):
            a.box((x,5,z0),(x,5,z1),PIPE)
    a.box((23,4,38),(27,4,42),PRECISION)
    for x in (20,30):
        a.box((x,3,39),(x,9,43),BASE)
        a.box((x,9,38),(x,10,44),VENT)
    a.box((20,10,44),(30,10,44),PANEL)
    zone(a,'前向定量入料床',(21,2,8),(29,5,18),'保温模坯与定位滚床','feed')
    zone(a,'后向冷却脱模床',(20,2,31),(30,10,46),'开阔滚床、冷却侧箱和末端质量读出桥','demould')

    # 偏置低矮熔料坩埚：宽腹、收口、感应圈和保温观察缝。
    profile = {2:3,3:4,4:5,5:5,6:5,7:5,8:5,9:5,10:5,11:5,
               12:5,13:5,14:5,15:5,16:5,17:4,18:4,19:3,20:3,21:2}
    vessel(a,5,34,profile,HOT,True)
    a.box((4,22,33),(6,24,35),WHITE)
    for y in (5,11,17):
        a.ring((5,y,34),5,5,COIL)
    a.box((4,3,33),(6,18,35),COIL)
    a.box((3,2,27),(7,5,28),GEAR)
    route(a,'保温熔料坩埚','中央聚合压铸工位',
          [(8,6,30),(8,6,27),(18,6,27),(20,6,27)],PIPE)
    # 坩埚外侧排气脊有基座与帽，不使用孤立排烟装饰。
    a.box((1,2,37),(2,21,38),CHEMICAL)
    a.box((0,20,36),(3,22,39),VENT)
    a.box((1,21,37),(2,24,38),WHITE)
    zone(a,'保温熔料坩埚',(0,0,27),(10,24,40),
         '琥珀变径保温炉、三道感应圈、窄观察缝与短程熔料导管','melter')

    # 银色蓄压缸与一列倾阶散热翼组成右侧服务设备。
    accum_profile = {y:3 for y in range(3,21)}
    accum_profile.update({2:2,21:2,22:1})
    vessel(a,45,25,accum_profile,WHITE)
    for y in (3,10,17,21):
        a.ring((45,y,25),3,3,BASE)
    a.box((44,23,24),(46,25,26),GEAR)
    a.box((43,7,23),(43,18,23),PANEL)
    a.box((45,2,25),(45,23,25),PIPE)
    route(a,'液压蓄压缸','四柱承力与双道曲冠',
          [(42,9,25),(39,9,25),(39,29,25),(36,29,25),(36,29,31)],PIPE)
    a.box((43,2,34),(49,3,41),POWER)
    for x in range(43,51,2):
        top = 16-(x-43)
        a.box((x,4,34),(x,top,41),WHITE)
        a.box((x,top,34),(x,top,41),VENT)
    a.box((43,4,40),(49,6,41),PIPE)
    route(a,'后向冷却脱模床','倾阶换热翼',[(30,5,40),(42,5,40),(43,5,40)],PIPE)
    route(a,'倾阶换热翼','液压蓄压缸',[(47,4,34),(47,4,28),(45,4,28)],PIPE)
    zone(a,'液压蓄压缸',(41,0,20),(48,25,30),'分段轴套的储压罐、侧置读出脊与通向压梁的供压管','pressure')
    zone(a,'倾阶换热翼',(42,0,33),(50,16,42),'高度递减的散热片与共用回流总管','cooling')

    # 检修道在设备边缘，净空真实存在；横管从上方或后侧绕行。
    a.paths += [
        {'name':'左侧压柱检修通道','min':[7,1,9],'max':[9,3,26]},
        {'name':'右侧前压柱维护通道','min':[41,1,9],'max':[43,3,16]},
    ]
    purposes=[('NANO_GROUP','抗性纳米群输入候选'),('BINDER','聚合介质输入候选'),
              ('POWER','压铸驱动供能候选'),('PRODUCT','粗魂钢输出候选'),
              ('COOLANT','冷却液输入候选'),('SCRAP','浇口余料输出候选')]
    data=finish(a,'i14-soulium-press-v3',
        '四根收腰巨柱托起两道上拱曲冠，中央液压冲杆、压板与下模直接暴露在空气中。琥珀保温坩埚偏置左后，银色蓄压罐与递减散热翼位于右侧；前入料、后脱模沿同一直线展开，局部承重脚座和两侧维护道使受力与工艺关系可读。',
        purposes,BASE,[
          'GTCEu ASSEMBLY_LINE：加工床、驱动和顶部机械分层；本稿改为单一压铸冲程。',
          'GTLCore PCB_FACTORY：独立工段以明确低位总管连接，不将全部设备包在一间箱房。',
          'GTLsupb MICROCOSM_FOUNDRY：核心与弧形支撑之间的空气间隙；本稿为原创四柱曲冠。',
          '参考依据：logs/i09-i13-redesign-v6/reference-study.json；未复制Pattern或声明运行。'])
    # 主控用白色框，六接口仍为封闭工业占位壳。
    states={tuple(q['pos']):q['state'] for q in data['blocks']}
    for x in range(22,29):
        for y in range(1,6):
            if x in (22,28) or y in (1,5):states[x,y,5]=WHITE
    for x,y in ((24,2),(24,3),(24,4),(25,2),(25,4),(26,2),(26,3),(26,4)):
        states[x,y,5]=WHITE
    data['blocks']=[{'pos':list(p),'state':s} for p,s in sorted(states.items())]
    data['brief']['minimum_wdh']=[33,37,29]
    data['paste_anchor']=data['controller']
    data['recommended_bottom_y']=-60
    return data
