# -*- coding: utf-8 -*-
"""MAX供料机独立外观候选；不注册机器、介质或配方。"""
from collections import deque
import numpy as np

W, H, D = 41, 31, 53
NAME = 'hk3gtl-mx-c01-converter-v1-20261107'
TITLE = '崩坏能物质转化器（暂名）· 双罐脉冲转化厂'
STATES = [
    'gtlcore:component_assembly_line_casing_max',
    'gtceu:solid_machine_casing', 'gtceu:steel_pipe_casing',
    'gtceu:heatproof_machine_casing', 'gtceu:computer_heat_vent',
    'gtceu:computer_casing', 'gtceu:high_power_casing',
    'gtceu:tempered_glass', 'gtceu:nonconducting_casing',
    'gtceu:fusion_glass', 'hk3gtl:industrial_port_casing',
    'minecraft:diamond_block', 'minecraft:sea_lantern',
]
C, S, P, T, V, E, U, G, I, F, PORT, CONTROL, LIGHT = range(1, 14)
ROLES = dict(zip(STATES, [
    'MAX原生装配线机壳：转化腔、双罐与控制舱主体',
    '承力底梁、罐座和检修平台', '双罐汇流管及冷却回路',
    '转化腔内衬及热交换板', '后置散热器与功率舱通风面',
    '前舱监测与计量面板', '脉冲供能组件', '储罐与前舱观察窗',
    '转化腔绝缘环和支座隔离垫', '转化腔观察环',
    '通用接口位置标记，不限定物品或流体输入输出',
    '居中北向控制器位置标记', '检修照明与状态指示',
]))


def build():
    a = np.zeros((H, D, W), dtype=np.uint8)

    def box(x, y, z, X, Y, Z, m):
        assert 0 <= x <= X < W and 0 <= y <= Y < H and 0 <= z <= Z < D
        a[y:Y+1, z:Z+1, x:X+1] = m

    def shell(x, y, z, X, Y, Z, m):
        box(x, y, z, X, Y, Z, m)
        box(x+1, y+1, z+1, X-1, Y-1, Z-1, 0)

    # 分区平台保留敞开的两侧检修路，不用整块实心地基淹没设备轮廓。
    box(10, 0, 0, 30, 0, 16, C)
    box(0, 0, 17, 40, 0, 47, C)
    box(9, 0, 48, 31, 0, 52, C)
    for x in (0, 40):
        box(x, 1, 18, x, 1, 46, S)
        for z in range(19, 47, 6):
            box(x, 2, z, x, 2, z, LIGHT)
    for x in (10, 30):
        box(x, 1, 0, x, 1, 16, S)
    for z in (17, 24, 41, 47):
        box(1, 1, z, 39, 1, z, S)

    # 控制舱就是主体前端：接口直接嵌墙，内部背板连续，北侧留出五格接线空间。
    shell(13, 1, 5, 27, 7, 14, C)
    box(13, 1, 6, 27, 4, 6, C)
    for x in (14, 15, 25, 26):
        box(x, 5, 5, x, 6, 5, E)
    box(17, 5, 5, 23, 6, 5, G)
    box(13, 8, 6, 27, 8, 13, C)
    for x in (13, 27):
        box(x, 3, 8, x, 5, 12, G)
    box(18, 1, 14, 22, 5, 20, C)
    box(19, 4, 15, 21, 4, 19, E)

    # 中轴卧式转化腔：厚壁筒体、绝缘环、上下观察带及落地鞍座。
    yy, xx = np.ogrid[:H, :W]
    radius = (xx-20)**2 + (yy-17)**2
    for z in range(20, 43):
        ring = (radius <= 9**2) & (radius >= 7**2)
        a[:, z, :][ring] = C
        lining = (radius < 7**2) & (radius >= 6**2)
        a[:, z, :][lining] = T
        if z in (20, 21, 27, 28, 35, 36, 41, 42):
            outer = (radius <= 11**2) & (radius >= 9**2)
            a[:, z, :][outer] = I if z in (21, 28, 36, 41) else C
        elif z in (24, 25, 31, 32, 38, 39):
            a[:, z, :][ring] = F
    for z in (20, 42):
        a[:, z, :][radius < 7**2] = C
        a[:, z, :][radius < 4**2] = U
        a[:, z, :][radius < 2**2] = LIGHT
    for z in (22, 39):
        box(13, 1, z, 27, 5, z+1, C)
        box(14, 6, z, 26, 7, z+1, S)
    # 沿筒顶布置共轴供能母线；最高点来自真实连续设备，不另插孤立高塔。
    box(19, 28, 20, 21, 29, 42, U)
    box(20, 30, 23, 20, 30, 39, P)
    box(20, 26, 20, 20, 28, 21, C)
    box(20, 26, 41, 20, 28, 42, C)

    # 双储罐和对称汇流管；不赋予未注册介质任何真实存储能力。
    zz, xx = np.ogrid[:D, :W]
    for cx in (6, 34):
        r = (xx-cx)**2 + (zz-31)**2
        for y in range(2, 24):
            outer = 5 if 5 <= y <= 20 else 4
            mask = (r <= outer**2) & (r >= (outer-1)**2)
            a[y][mask] = C
            if y in (2, 3, 22, 23):
                a[y][r <= outer**2] = C
            if y in (7, 8, 15, 16):
                a[y][mask] = G
        for x in (cx-3, cx+3):
            box(x, 1, 28, x, 4, 34, S)
        for z in (25, 37):
            box(cx-2, 5, z, cx+2, 6, z, P)
        box(cx, 3, 18, cx, 3, 26, P)
        box(cx, 4, 18, cx, 10, 18, P)
        box(min(cx,20), 10, 18, max(cx,20), 10, 18, P)
        box(cx, 10, 24, cx, 18, 24, P)
        box(cx, 18, 24, cx, 18, 26, P)
        # 双罐计量与循环泵组。
        shell(cx-3, 1, 19, cx+3, 5, 23, C)
        box(cx-2, 2, 19, cx+2, 3, 19, U)
        box(cx-1, 4, 19, cx+1, 4, 19, E)

    # 后场冷却模块有独立风道和进出管线，与前场维护路线分开。
    for x in (12, 25):
        shell(x, 1, 45, x+3, 12, 50, C)
        for y in range(3, 12, 2):
            box(x, y, 50, x+3, y, 50, V)
            box(x, y, 45, x+3, y, 45, T)
        box(x+1, 1, 43, x+2, 3, 44, P)
    box(13, 13, 46, 27, 13, 47, P)
    box(13, 8, 43, 13, 13, 46, P)
    box(27, 8, 43, 27, 13, 46, P)
    box(13, 8, 42, 13, 8, 43, P)
    box(27, 8, 42, 27, 8, 43, P)
    controller = [20, 2, 5]
    a[2, 5, 20] = CONTROL
    ports = []
    for index, x in enumerate((14, 16, 18, 22, 24, 26), 1):
        a[2, 5, x] = PORT
        ports.append(dict(id=f'通用接口{index}', pos=[x,2,5], face='north',
                          purpose='任意物品／流体输入输出位置候选；实际能力由正式Pattern与仓室决定'))
    data = dict(key='mx-c01', name=NAME, title=TITLE, size=[W,H,D],
                controller=controller, controller_face='north', ports=ports,
                description='中轴卧式脉冲转化腔配双储罐、前端计量控制舱及后置热交换器，主机壳采用增强版原生MAX装配线机壳。',
                zones=[dict(name=n,pos=p) for n,p in [('计量与主控',[20,8,9]),('脉冲转化腔',[20,30,31]),('左储罐',[6,23,31]),('右储罐',[34,23,31]),('热交换',[20,13,48])]],
                paths=[dict(min=[11,1,0],max=[29,4,4]),dict(min=[10,2,7],max=[12,4,16]),dict(min=[28,2,7],max=[30,4,16])])
    return a, data


def audit(a, data):
    coords = np.argwhere(a)
    assert coords.min(axis=0).tolist() == [0,0,0]
    assert coords.max(axis=0).tolist() == [H-1,D-1,W-1]
    counts = np.bincount(a.ravel(), minlength=len(STATES)+1)
    assert np.all(counts[1:]) and counts[C] == max(counts[1:])
    assert counts[CONTROL] == 1 and counts[PORT] == len(data['ports'])
    visited = np.zeros_like(a, dtype=bool)
    queue = deque([tuple(coords[0])]); visited[tuple(coords[0])] = True
    while queue:
        y,z,x = queue.popleft()
        for Y,Z,X in ((y+1,z,x),(y-1,z,x),(y,z+1,x),(y,z-1,x),(y,z,x+1),(y,z,x-1)):
            if 0 <= Y < H and 0 <= Z < D and 0 <= X < W and a[Y,Z,X] and not visited[Y,Z,X]:
                visited[Y,Z,X] = True; queue.append((Y,Z,X))
    assert int(visited.sum()) == len(coords), '存在悬空设备或未连接管线'
    assert np.array_equal(a, a[:,:,::-1]), '左右几何与材料必须对称'
    assert data['controller'][0] == W//2
    for item in [dict(pos=data['controller']), *data['ports']]:
        x,y,z = item['pos']
        assert a[y,z+1,x] and np.all(a[y-1:y+2,z,x-1:x+2])
        assert not np.any(a[1:5,z-5:z,x-1:x+2]), '正面接线净空不足'
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max']
        assert not np.any(a[y:Y+1,z:Z+1,x:X+1]), '检修路线被占用'
    return dict(blocks=len(coords), unique_materials=len(STATES),
                palette={s:int(counts[i+1]) for i,s in enumerate(STATES)},
                actual_size_xyz=[W,H,D], connected=True, mirrored=True,
                controller_centered=True, universal_ports=True, clearance_passed=True,
                minimum_size_baseline=None,
                minimum_size_note='四台MAX为原69项之外的既定需求，无已冻结尺寸下限；本版尺寸为外观候选。',
                voltage_progression=dict(voltage='MAX',tier=14,lower_forms=[],status='范围内无低阶比较对象，不计通过率'),
                approved=False, installed=False, game_verified=False, survival_stage_verified=False,
                checks=['实际包围盒与声明尺寸相同','主体最大单材为原生MAX装配线机壳','全部实体六邻接单连通且左右镜像','主控居中，六个通用接口嵌入连续外墙','北侧五格接线空间与前端检修路净空通过'])
