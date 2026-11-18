# -*- coding: utf-8 -*-
"""构建图谱存储阵列：四组分层数据架、双翼检修道和中轴检索廊。"""
from collections import deque
import numpy as np

W,H,D=49,29,59
NAME='hk3gtl-mx-c03-atlas-v1-20261107'
TITLE='构建图谱存储阵列（暂名）· 双翼图谱库'
STATES=[
    'gtlcore:component_assembly_line_casing_max','gtceu:advanced_computer_casing',
    'gtceu:computer_casing','gtceu:computer_heat_vent',
    'gtlcore:super_computation_component[active=false]','gtceu:robust_machine_casing',
    'gtceu:assembly_line_grating','gtceu:high_power_casing',
    'gtceu:nonconducting_casing','gtceu:fusion_glass','gtceu:steel_pipe_casing',
    'gtceu:plascrete','hk3gtl:industrial_port_casing','minecraft:diamond_block','minecraft:sea_lantern',
]
C,E,N,V,K,S,R,U,I,G,P,T,PORT,CONTROL,LIGHT=range(1,16)
ROLES=dict(zip(STATES,[
    '原生MAX机壳：分层架、数据脊柱与主体平台',
    '图谱检索面板与版本目录设备', '分层数据柜与机架背板',
    '架体侧面的散热模块', '图谱处理单元，仅作建筑表达',
    '数据架支座与后舱承力框架', '两翼检修踏面', '顶部汇流母线与后舱电源',
    '机架层间隔离与母线绝缘', '前舱观察窗与数据架屏护',
    '冷却侧舱至数据架的四路短接管', '底座隔振衬块',
    '通用接口占位，不固定物品或流体输入输出', '居中北向控制器占位',
    '机架状态与检修照明，仅作静态建筑表达',
]))


def build():
    a=np.zeros((H,D,W),dtype=np.uint8)

    def box(x,y,z,X,Y,Z,m):
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D
        a[y:Y+1,z:Z+1,x:X+1]=m

    def shell(x,y,z,X,Y,Z,m):
        box(x,y,z,X,Y,Z,m)
        box(x+1,y+1,z+1,X-1,Y-1,Z-1,0)

    box(12,0,0,36,0,16,C)
    box(0,0,17,48,0,50,C)
    box(10,0,51,38,0,58,C)
    for x in (15,30):box(x,1,18,x+3,1,49,R)
    for x in (20,28):box(x,0,17,x,0,50,I)
    for z in (18,31,49):
        box(21,0,z,27,0,z,LIGHT)
    for x in (0,48):
        box(x,1,18,x,1,49,S)
        for z in (19,32,48):box(x,2,z,x,2,z,LIGHT)

    # 前端检索控制舱直接接在中轴廊口，端口齐平融入机体。
    shell(17,1,5,31,7,13,C)
    box(17,1,6,31,4,6,C)
    box(20,5,5,28,6,5,G)
    for x in (18,19,29,30):box(x,5,5,x,6,5,E)
    box(18,8,6,30,8,12,C)
    for x in (17,31):box(x,3,8,x,5,11,G)

    banks=[];routes=[]
    # 两翼各两组机架：四层数据抽屉、独立散热面与连续的承重立柱。
    for left in (True,False):
        lo,hi=(3,13) if left else (35,45)
        for z in (20,36):
            box(lo,1,z,hi,1,z+10,T)
            for x in (lo,hi):box(x,2,z,x,25,z+10,C)
            for Z in (z,z+10):box(lo,2,Z,hi,25,Z,C)
            for y in (2,8,14,20,26):
                box(lo,y,z,hi,y,z+10,C)
            for y in (3,9,15,21):
                box(lo+1,y,z+1,hi-1,y+3,z+9,N)
                box(lo+2,y,z,hi-2,y+3,z,E)
                box(lo+2,y,z+10,hi-2,y+3,z+10,E)
                box(lo+2,y+1,z+2,hi-2,y+2,z+8,K)
                outer=lo if left else hi
                box(outer,y,z+2,outer,y+3,z+8,V)
                box(lo+1,y+4,z+1,hi-1,y+4,z+9,I)
                box(lo+2,y+3,z,hi-2,y+3,z,G)
            for y in (7,13,19,25):
                box(lo+1,y,z,hi-1,y,z,C)
                box(lo+1,y,z+10,hi-1,y,z+10,C)
                box(lo+2,y,z,lo+2,y,z,LIGHT)
                box(hi-2,y,z,hi-2,y,z,LIGHT)
            banks.append(dict(name=('左' if left else '右')+('前' if z==20 else '后')+'图谱架',
                              min=[lo,1,z],max=[hi,26,z+10]))
            # 侧舱接点经三格短管进入机架，明确两端所接设备，不能靠底座连通蒙混通过。
            pod=0 if left else 46
            box(pod,1,z+3,pod+2,7,z+7,C)
            box(pod,3,z+3,pod+2,5,z+3,U)
            xs=[2,3,4] if left else [46,45,44]
            for x in xs:box(x,5,z+5,x,5,z+5,P)
            routes.append(dict(cells=[[x,5,z+5] for x in xs],
                source_contact=[1 if left else 47,5,z+5],
                target_contact=[5 if left else 43,5,z+5]))

    # 图谱汇流桥由两翼机架末端的数据脊柱承托；中轴检索廊保持通行。
    for x in (12,34):
        box(x,1,46,x+2,26,48,C)
        box(x,4,47,x+2,24,47,E)
    box(12,27,46,36,27,48,C)
    box(13,28,46,35,28,48,U)
    box(22,25,48,26,26,54,C)
    box(23,24,53,25,24,54,E)

    # 后端目录交接舱与电源两侧分开，数据设备始终有实体背衬。
    shell(18,1,52,30,22,57,C)
    box(20,3,57,28,18,57,E)
    box(21,23,53,27,23,56,C)
    box(23,24,54,25,24,54,E)
    for x in (10,32):
        shell(x,1,52,x+6,9,56,C)
        box(x+1,2,56,x+5,6,56,U)
        box(x+1,8,56,x+5,8,56,V)
        box(x,1,52,x+6,1,56,S)
    controller=[24,2,5];a[2,5,24]=CONTROL
    ports=[]
    for number,x in enumerate((18,20,22,26,28,30),1):
        a[2,5,x]=PORT
        ports.append(dict(id=f'通用接口{number}',pos=[x,2,5],face='north',
            purpose='任意物品／流体输入输出候选位；实际能力以正式仓室和Pattern为准'))
    data=dict(key='mx-c03',name=NAME,title=TITLE,size=[W,H,D],controller=controller,
        controller_face='north',ports=ports,banks=banks,cooling_routes=routes,
        description='四组分层图谱架组成双翼，中轴为检索通道；两翼各有独立检修道，顶部汇流桥把数据架接入后端目录交接舱。',
        purpose='保存与查询已获许可的物质图样、版本化建筑材料清单，并向AE开放制造订单接口。当前只制作建筑外观，不声称已完成数据库、AE对接或自动制造。',
        zones=[dict(name=n,pos=p) for n,p in [('检索与主控',[24,8,9]),('左翼图谱架',[8,26,33]),('右翼图谱架',[40,26,33]),('汇流桥',[24,28,47]),('目录交接',[24,23,55])]],
        paths=[dict(min=[15,1,0],max=[33,4,4]),dict(min=[15,2,18],max=[18,4,49]),
               dict(min=[30,2,18],max=[33,4,49]),dict(min=[20,1,14],max=[28,4,50])])
    return a,data


def audit(a,data):
    coords=np.argwhere(a);counts=np.bincount(a.ravel(),minlength=len(STATES)+1)
    assert coords.min(axis=0).tolist()==[0,0,0] and coords.max(axis=0).tolist()==[H-1,D-1,W-1]
    assert np.all(counts[1:]) and counts[C]==max(counts[1:])
    assert counts[CONTROL]==1 and counts[PORT]==6
    seen=np.zeros_like(a,dtype=bool);queue=deque([tuple(coords[0])]);seen[tuple(coords[0])]=True
    while queue:
        y,z,x=queue.popleft()
        for Y,Z,X in ((y+1,z,x),(y-1,z,x),(y,z+1,x),(y,z-1,x),(y,z,x+1),(y,z,x-1)):
            if 0<=Y<H and 0<=Z<D and 0<=X<W and a[Y,Z,X] and not seen[Y,Z,X]:
                seen[Y,Z,X]=True;queue.append((Y,Z,X))
    assert int(seen.sum())==len(coords),'存在悬空设备'
    assert np.array_equal(a,a[:,:,::-1]),'左右几何或材料不对称'
    assert data['controller'][0]==W//2
    for item in [dict(pos=data['controller']),*data['ports']]:
        x,y,z=item['pos']
        assert a[y,z+1,x] and np.all(a[y-1:y+2,z,x-1:x+2])
        assert not np.any(a[1:5,z-5:z,x-1:x+2]),'正面接线空间不足'
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max']
        assert not np.any(a[y:Y+1,z:Z+1,x:X+1]),'检修或检索通道被占用'
    expected=set()
    for route in data['cooling_routes']:
        cells=route['cells'];assert all(a[y,z,x]==P for x,y,z in cells)
        assert all(sum(abs(u-v) for u,v in zip(p,q))==1 for p,q in zip(cells,cells[1:]))
        for field,endpoint in [('source_contact',cells[0]),('target_contact',cells[-1])]:
            x,y,z=route[field]
            assert a[y,z,x] in (C,K) and sum(abs(u-v) for u,v in zip(endpoint,[x,y,z]))==1
        expected.update(tuple(p) for p in cells)
    actual={(int(x),int(y),int(z)) for y,z,x in zip(*np.nonzero(a==P))}
    assert actual==expected,'发现未接入指定设备的多余管道'
    return dict(blocks=len(coords),unique_materials=len(STATES),palette={s:int(counts[i+1]) for i,s in enumerate(STATES)},
        actual_size_xyz=[W,H,D],connected=True,mirrored=True,controller_centered=True,
        universal_ports=True,clearance_passed=True,pipe_routes_passed=True,pipe_routes_count=4,open_pipe_ends=0,
        minimum_size_baseline=None,minimum_size_note='既定四台MAX需求不在原69项尺寸表中，无已冻结尺寸下限。',
        voltage_progression=dict(voltage='MAX',tier=14,lower_forms=[],status='范围内无低阶比较对象，不计通过率'),
        approved=False,installed=False,game_verified=False,survival_stage_verified=False,
        checks=['实际边界与声明尺寸相同，MAX机壳为最大单材','全部实体六邻接单连通且左右镜像','四组图谱架、汇流桥和交接舱均有连续支撑','居中主控与六个通用接口保持五格接线净空','两翼检修道与中轴检索廊净空通过','四路冷却短管连续接到指定侧舱和机架，无断头或多余管段'])


if __name__=='__main__':
    cube,data=build();check=audit(cube,data)
    broken=cube.copy();broken[5,25,3]=0
    try:audit(broken,data)
    except AssertionError:pass
    else:raise AssertionError('未拒绝断管反例')
    print(f"图谱库几何、通道与四路设备管线通过：{check['blocks']}方块；断管反例已拒绝。")
