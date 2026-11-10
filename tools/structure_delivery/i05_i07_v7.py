# -*- coding: utf-8 -*-
"""I05–I07 第七版独立形体，2026-10-14。

替换旧双圆塔、大车间盒、双屏蔽盒的构图；只返回候选数据，不修改实例或正式 Pattern。
"""
from i09_i13_v6_common import start, zone, route, finish, GRATE, GEAR, DIAMOND

CLEAN = 'gtceu:clean_machine_casing'
STEEL = 'gtceu:robust_machine_casing'
STAINLESS = 'gtceu:stainless_evaporation_casing'
CHEMICAL = 'gtceu:corrosion_proof_casing'
HEAT = 'gtceu:heatproof_machine_casing'
PIPE = 'gtceu:ptfe_pipe_casing'
TITANIUM_PIPE = 'gtceu:titanium_pipe_casing'
GLASS = 'gtceu:laminated_glass'
PANEL = 'gtceu:computer_casing'
CONTROL = 'gtceu:advanced_computer_casing'
VENT = 'gtceu:computer_heat_vent'
FILTER = 'gtceu:sterilizing_filter_casing'
I05_SHELL = 'hk3gtl:voltage_machine_casing_qav'
I06_SHELL = 'hk3gtl:voltage_machine_casing_qev'
I07_SHELL = 'hk3gtl:voltage_machine_casing_qcv'


def _front(a):
    c = a.w//2
    # 六个接口底座与中央主控从 z=7 连到设备坞，检修带上方留空。
    a.box((c-15, 0, 5), (c+15, 0, 9), GRATE)
    a.box((c-2, 0, 0), (c+2, 0, 2), GRATE)


def _oct(dx, dy, r):
    return max(abs(dx), abs(dy)) <= r and abs(dx)+abs(dy) <= r+r//2


def _tube(a, cx, cy, z0, z1, r, body, belt):
    """纵向八角壳：两格厚折面、端盖、外露机械轴和三组承重鞍座。"""
    for z in range(z0, z1+1):
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if _oct(dx, dy, r) and (not _oct(dx, dy, r-2) or z in (z0, z0+1, z1-1, z1)):
                    m = belt if z in (z0, z0+1, (z0+z1)//2, z1-1, z1) else body
                    a.set(cx+dx, cy+dy, z, m)
    for z in (z0+2, (z0+z1)//2, z1-2):
        a.box((cx-r-1, 0, z-1), (cx-r, cy, z+1), belt)
        a.box((cx+r, 0, z-1), (cx+r+1, cy, z+1), belt)
        a.box((cx-r, 1, z-1), (cx+r, 2, z+1), belt)
    a.box((cx-1, cy-1, z0-2), (cx+1, cy+1, z0), GEAR)
    a.box((cx-1, cy-1, z1), (cx+1, cy+1, z1+2), GEAR)


def i05():
    a = start('I05', '稳定介质再生塔', (43, 39, 37),
              '收肩滤芯塔、三层侧抽盒、低位回热束管与独立屏蔽回收坞',
              '介质经左侧可替换滤芯提升至塔冠，右侧回热器冷凝回流；废棒与固化物在后方屏蔽坞分开维护')
    _front(a)
    # 设备基础和相接维护回廊；底座只覆盖承重、滤芯拆装和换热服务区。
    a.box((0, 0, 13), (12, 0, 36), STEEL)
    a.box((13, 0, 16), (27, 1, 31), STAINLESS)
    a.box((29, 0, 13), (42, 0, 36), STEEL)
    a.box((0, 0, 10), (42, 0, 13), GRATE)
    a.box((0, 0, 33), (42, 0, 36), GRATE)
    for x in (10, 30):
        a.box((x, 0, 12), (x+2, 0, 34), GRATE)
    # 滤芯主塔使用厚框、透明狭缝与层间空腔。顶部收肩而非重复圆柱帽。
    for y0, y1, x0, x1, z0, z1 in ((2, 12, 13, 27, 16, 31),
                                   (13, 23, 14, 26, 17, 30),
                                   (24, 32, 16, 24, 19, 28)):
        a.box((x0, y0, z0), (x1, y1, z1), I05_SHELL, True)
        for x in (x0, x1):
            a.box((x, y0, z0), (x, y1, z0+1), STAINLESS)
            a.box((x, y0, z1-1), (x, y1, z1), STAINLESS)
        a.box((x0+3, y0+2, z0), (x1-3, y1-2, z0), GLASS)
        a.box((x0+3, y0+2, z1), (x1-3, y1-2, z1), GLASS)
        a.box((x0+2, y0+2, z0+2), (x1-2, y0+3, z1-2), FILTER)
        a.box((19, y0+1, 23), (21, y1-1, 25), CHEMICAL)
    a.box((17, 33, 20), (23, 35, 27), STAINLESS, True)
    a.box((19, 36, 22), (21, 38, 25), I05_SHELL)
    zone(a, '收肩介质再生主塔', (13, 0, 16), (27, 38, 31), '三个独立滤芯层、塔冠稳定处理及纵向回流', 'stepped_regeneration_tower')
    # 三个侧抽维护盒不是贴在塔面的装饰：实心承重臂连接到对应层的操作高度。
    for index, (z, y) in enumerate(((17, 7), (23, 17), (29, 27))):
        a.box((3, 0, z-2), (9, 1, z+2), STEEL)
        a.box((5, 2, z-1), (7, y, z+1), STAINLESS)
        a.box((2, y, z-2), (10, y+4, z+2), CHEMICAL, True)
        a.box((3, y+1, z-2), (8, y+3, z-2), FILTER)
        a.box((9, y, z-1), (16 if index==2 else 14, y+1, z+1), STAINLESS)
        route(a, f'侧抽滤芯维护盒 {index+1}', '收肩介质再生主塔',
              [(8, y+2, z), (16 if index==2 else 14, y+2, z)], PIPE)
        zone(a, f'侧抽滤芯维护盒 {index+1}', (2, 0, z-2), (10, y+4, z+2), '过滤介质拆装、洗涤及残留排放', 'filter_service_box')
    # 回热器水平展开，外部六组短鳍和独立出液头表现热交换。
    _tube(a, 35, 7, 15, 31, 4, CHEMICAL, STAINLESS)
    for z in range(17, 30, 3):
        a.box((39, 5, z), (41, 10, z), VENT)
    zone(a, '低位回热冷凝器', (29, 0, 13), (42, 11, 33), '热液回收与稳定介质冷凝缓冲', 'horizontal_reboiler')
    route(a, '收肩介质再生主塔', '低位回热冷凝器', [(24, 29, 24), (35, 29, 24), (35, 12, 24), (35, 11, 24)], TITANIUM_PIPE)
    a.box((34, 0, 24), (36, 28, 24), STAINLESS)
    # 后方回收工况独立，避免把失活燃料和介质混合成同一回路。
    a.box((15, 1, 33), (27, 5, 36), CHEMICAL, True)
    a.box((17, 2, 34), (25, 4, 35), FILTER)
    zone(a, '独立屏蔽回收坞', (15, 1, 33), (27, 5, 36), '失活棒拆解、残渣封存和固化维护位置；独立工况', 'isolated_recovery_dock')
    for x, endpoint in ((8, (6, 3, 17)), (12, (6, 3, 23)), (16, (19, 2, 23)),
                        (26, (21, 2, 34)), (30, (35, 3, 17)), (34, (35, 3, 31))):
        route(a, '正面接口坞', '对应处理单元', [(x, 2, 6), (x, 0, 6), (x, 0, 10), (endpoint[0], 0, 10), (endpoint[0], 0, endpoint[2]), endpoint])
    a.paths.append({'name': '主塔前观察与滤芯拆装横带', 'min': [17, 1, 10], 'max': [24, 3, 14]})
    purposes = [('FEED', '待再生介质/工况输入候选'), ('FILTER', '替换滤材或屏蔽试件输入候选'),
                ('POWER', '回热与再生供能候选'), ('RESIDUE', '固化残留物输出候选'),
                ('COOLANT', '换热循环介质接口候选'), ('PRODUCT', '再生稳定介质输出候选')]
    return finish(a, 'i05-regeneration-tower-v7',
                  '铁锈红再生设施以收肩滤芯塔为主角，三层可替换维护盒沿塔侧抬升；低位八角回热束管把热液回路横向展开，后方屏蔽回收坞独立服务废棒与固化工况。厚框、狭长观察面和层间空腔取代旧双筒塔的重复外壳。',
                  purposes, I05_SHELL, ['GTCEu 大型化学反应釜的耐蚀壳、管壳与独立工艺核心', 'GTLCore PCB 工厂的独立塔体、低槽和短管桥；GTLsupb 深渊化学蚀骸仪的收细主轴和轻附件层级'])


def i06():
    a = start('I06', '崩坏能燃料调配厂', (55, 29, 41),
              '三段阶梯料仓、露天双轴混合床、窄跨维护桁架与东侧灌装坞',
              '三种原料经左侧独立计量支路送入错位双轴混合床，沿后方回热管汇调温，再由东侧灌装坞输出')
    _front(a)
    a.box((0, 0, 10), (54, 0, 13), GRATE)
    a.box((0, 0, 13), (13, 1, 40), STEEL)
    a.box((15, 0, 15), (43, 1, 36), HEAT)
    a.box((44, 0, 10), (54, 1, 40), STEEL)
    a.box((0, 0, 37), (54, 0, 40), GRATE)
    # 三个上升高度的楔形料仓，凸出落料颈直接对着独立计量泵组。
    for index, z in enumerate((17, 25, 33)):
        top = 10+index*5
        a.box((2, 2, z-3), (10, top-3, z+3), CHEMICAL, True)
        a.box((3, top-2, z-2), (9, top, z+2), I06_SHELL, True)
        a.box((4, top+1, z-1), (8, top+2, z+1), STAINLESS)
        a.box((4, 2, z), (8, 4, z), GEAR)
        a.box((11, 2, z-1), (14, 5, z+1), PIPE)
        zone(a, f'原料计量仓 {index+1}', (2, 0, z-3), (14, top+2, z+3), '原料缓冲、落料与独立计量', 'stepped_feed_bin')
    # 两根露天滚筒沿工艺方向布置，错高错长提供清晰的混合床轮廓。
    _tube(a, 23, 11, 16, 32, 5, I06_SHELL, HEAT)
    _tube(a, 37, 9, 20, 34, 4, I06_SHELL, HEAT)
    a.box((22, 8, 16), (24, 14, 16), GLASS)
    a.box((36, 7, 20), (38, 11, 20), GLASS)
    zone(a, '错位双轴混合床', (16, 0, 14), (42, 16, 36), '一级混合、二级稳态调配及露天传动鞍座', 'open_blending_drums')
    route(a, '一级混合滚筒', '二级稳态滚筒', [(28, 11, 26), (33, 11, 26)], TITANIUM_PIPE)
    for z in (17, 25, 33):
        route(a, '独立原料计量仓', '错位双轴混合床', [(13, 4, z), (17, 4, z), (17, 10, z), (18, 10, z)], PIPE)
    # 后部热交换墙与一根窄维护梁，保留两筒顶面的绝大部分天空。
    a.box((15, 1, 37), (43, 3, 40), HEAT)
    for x in range(16, 43, 4):
        a.box((x, 4, 38), (x+1, 10, 39), VENT)
    route(a, '错位双轴混合床', '后部温控回路', [(23, 11, 34), (23, 11, 38), (40, 11, 38), (40, 9, 34)], TITANIUM_PIPE)
    zone(a, '后部热交换背墙', (15, 1, 37), (43, 11, 40), '热量交换与独立温控回路', 'heat_exchange_wall')
    for x in (16, 44):
        a.box((x, 1, 30), (x+1, 25, 32), STEEL)
    a.box((16, 25, 30), (45, 27, 32), STAINLESS)
    a.line((17, 20, 31), (24, 25, 31), STEEL, 3)
    a.line((44, 20, 31), (37, 25, 31), STEEL, 3)
    a.box((29, 25, 29), (32, 28, 33), GEAR)
    a.box((30, 19, 31), (31, 24, 31), TITANIUM_PIPE)
    zone(a, '窄跨维护桁架', (15, 1, 29), (45, 28, 33), '滚筒芯轴维护与更换吊点', 'narrow_service_gantry')
    # 灌装坞由三段小型压头组成，以低位导向床连接到前方输出。
    a.box((46, 2, 13), (52, 3, 37), I06_SHELL)
    for z in (17, 25, 33):
        a.box((46, 4, z-1), (47, 12, z+1), STAINLESS)
        a.box((51, 4, z-1), (52, 12, z+1), STAINLESS)
        a.box((46, 12, z-1), (52, 13, z+1), I06_SHELL)
        a.box((49, 7, z), (49, 11, z), GEAR)
        a.box((48, 4, z-1), (50, 6, z+1), CHEMICAL)
    zone(a, '东侧三段灌装坞', (44, 0, 10), (54, 13, 40), '产品缓冲、分流与灌装服务面', 'filling_dock')
    route(a, '错位双轴混合床', '东侧三段灌装坞', [(41, 9, 27), (46, 9, 27), (49, 9, 27), (49, 9, 25)])
    c=a.w//2
    for x, end in zip((c-13,c-9,c-5,c+5,c+9,c+13), ((6,2,17),(6,2,25),(16,2,30),(6,2,33),(49,3,17),(49,3,33))):
        route(a, '正面接口坞', '对应调配工位', [(x,2,6),(x,0,6),(x,0,10),(end[0],0,10),(end[0],0,end[2]),end])
    a.box((25,0,8),(29,0,14),GRATE)
    a.paths.append({'name':'双轴工艺前场观察入口','min':[25,1,8],'max':[29,4,14]})
    purposes=[('BASE','燃料基质输入候选'),('MEDIUM','稳定介质输入候选'),('POWER','调配供能候选'),
              ('CATALYST','催化剂输入候选'),('FUEL','调配燃料输出候选'),('RESIDUE','残余物输出候选')]
    return finish(a,'i06-fuel-blending-v7',
                  '铜橙调配厂以两根错位八角滚筒为主角：左侧阶梯料仓分路计量，后部短热交换墙负责温控，一根窄维护桁架横跨芯轴吊点；东侧三段灌装压头沿独立导向床收尾。中央工艺外露，原料、混合、冷却、输出都能在中距离辨认。',
                  purposes,I06_SHELL,['GTCEu 大型化学反应器的管壳与分路输入关系','GTLCore PCB 工厂的工段错台和精密装配机的可见工艺内核；GTLsupb 微观宇宙铸造厂的核心与支撑留空'])


def _aperture(a,z,y,r,mat):
    # 垂直八角光阑，用两格厚轮廓确保斜角六面连通，保留中心空气。
    for dx in range(-r,r+1):
        for dy in range(-r,r+1):
            if _oct(dx,dy,r) and not _oct(dx,dy,r-2):
                a.box((22+dx,y+dy,z),(22+dx,y+dy,z+1),mat)


def i07():
    a=start('I07','探测器精密校准台',(45,27,37),
            '开放光学长床、三组不同口径光阑、后置悬挑计量弧与侧翼读出架',
            '前方标准件与待测件定位，沿纵向光轴通过三组可见光阑，后方基准弧提供激励，侧架读出并分流')
    _front(a)
    a.box((0,0,10),(44,0,13),GRATE)
    a.box((15,0,15),(29,1,34),CLEAN)
    a.box((0,0,15),(10,1,36),STEEL)
    a.box((34,0,15),(44,1,36),STEEL)
    a.box((0,0,34),(44,0,36),GRATE)
    a.box((10,0,18),(15,0,23),GRATE)
    a.box((29,0,18),(34,0,23),GRATE)
    # 标定床两条导轨和三个可见夹具，光轴 y12 持续为空。
    a.box((16,2,15),(28,3,33),I07_SHELL)
    for x in (18,26):
        a.box((x,4,15),(x,5,33),GEAR)
    for z in (17,24,31):
        a.box((19,4,z-1),(25,7,z+1),CONTROL)
        a.box((21,8,z),(23,9,z),GLASS)
    zone(a,'纵向光学标定床',(15,0,13),(29,9,34),'标准件、待测件及三段机械定位夹具；上方光轴留空','optical_calibration_bed')
    for index,(z,r) in enumerate(((17,5),(24,6),(31,7))):
        _aperture(a,z,14,r,I07_SHELL)
        for x in (22-r,22+r):
            a.box((x,2,z),(x,14,z+1),CLEAN)
            a.box((x-1,2,z-1),(x+1,4,z+2),STEEL)
        zone(a,f'光阑与基准框 {index+1}',(22-r,2,z-1),(22+r,14+r,z+2),'机械基准、视场收束与校准观察；中心是连续光轴空气','open_aperture')
    # 后置悬挑测量弧比光阑高，用实际曲折梁围住后部信号源，避免两间大方盒。
    for x in (12,32):
        a.box((x,1,34),(x+1,19,36),CLEAN)
    a.line((13,19,35),(18,24,35),CLEAN,3)
    a.line((32,19,35),(27,24,35),CLEAN,3)
    a.box((18,24,34),(27,26,36),I07_SHELL)
    a.box((21,18,34),(23,23,36),PANEL)
    a.box((21,16,34),(23,17,36),GLASS)
    zone(a,'后置悬挑计量弧',(11,1,33),(33,26,36),'后端激励源与悬挑计量梁','cantilever_metrology_arch')
    # 左侧基准样本架与右側讀出架为不同低位设备，不把主体光轴藏进房间。
    for left in (True,False):
        x0,x1=(2,9) if left else (35,42)
        for z in (17,25,33):
            a.box((x0,2,z-2),(x1,5,z+2),I07_SHELL)
            a.box((x0+1,6,z-1),(x1-1,8,z+1),PANEL if left else CONTROL)
            a.box((x0+1,9,z),(x1-1,10,z),VENT)
        zone(a,'左侧标准件基准架' if left else '右侧数据读出架',(x0,0,15),(x1,10,36),
             '标准样本装填与对照' if left else '读数、数据整理及产品分流','reference_rack' if left else 'readout_rack')
    route(a,'左侧标准件基准架','纵向光学标定床',[(9,6,17),(15,6,17),(19,6,17)],PANEL)
    route(a,'纵向光学标定床','右侧数据读出架',[(25,6,31),(34,6,31),(34,6,33),(35,6,33)],PANEL)
    # 六个端口采用地面线路接各模块，检修入口避开线路，不临时后切主体。
    c=22
    for x,end in zip((9,13,17,27,31,35),((6,2,17),(19,3,17),(13,2,34),(39,2,25),(39,2,17),(39,2,33))):
        route(a,'正面接口坞','对应校准模块',[(x,2,6),(x,0,6),(x,0,10),(end[0],0,10),(end[0],0,end[2]),end],PANEL)
    a.box((20,0,8),(24,0,14),GRATE)
    a.paths.append({'name':'正面标定床观察入口','min':[20,1,8],'max':[24,4,14]})
    a.paths.append({'name':'光轴中心净空','min':[21,12,15],'max':[23,16,33]})
    purposes=[('REFERENCE','标准件输入候选'),('TEST_PIECE','待校准探测器输入候选'),('POWER','信号源供能候选'),
              ('READOUT','校准数据输出候选'),('PRODUCT','已校准探测器输出候选'),('REJECT','不合格件输出候选')]
    return finish(a,'i07-precision-calibration-v7',
                  '靛蓝校准台以暴露的纵向光轴组织空间：三组口径递增的八角光阑围住低位机械夹具，后置悬挑计量弧提供激励，标准件架和读出架分居两侧。光轴和观察入口始终为空，仪器台成为主体，旧双屏蔽方盒退为可读的开放基准框。',
                  purposes,I07_SHELL,['GTCEu HPCA 的仪表服务面与连续排热面分工','GTLCore 精密装配机的透明长轴与端部承重；GTLsupb 秩推衍装配矩阵的可见核心和空气约束层级'])
