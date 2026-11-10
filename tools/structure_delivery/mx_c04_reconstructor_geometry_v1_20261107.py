# -*- coding: utf-8 -*-
"""精密重构机：双门架、四组实体机械臂及开放式中央重构台。"""
from collections import deque
import numpy as np

W,H,D=53,33,61
NAME='hk3gtl-mx-c04-reconstructor-v1-20261107'
TITLE='崩坏能精密重构机（暂名）· 四臂重构工坊'
STATES=[
    'gtlcore:component_assembly_line_casing_max','gtceu:assembly_line_casing',
    'gtceu:solid_machine_casing','gtceu:tungstensteel_gearbox',
    'gtceu:steel_pipe_casing','gtceu:high_power_casing',
    'gtceu:nonconducting_casing','gtceu:laser_safe_engraving_casing',
    'gtceu:vibration_safe_casing','gtceu:computer_casing','gtceu:computer_heat_vent',
    'gtceu:tempered_glass','gtceu:assembly_line_grating',
    'hk3gtl:industrial_port_casing','minecraft:diamond_block','minecraft:sea_lantern',
]
C,A,S,K,P,U,I,L,T,E,V,G,R,PORT,CONTROL,LIGHT=range(1,17)
ROLES=dict(zip(STATES,[
    'MAX原生机壳：门架、机械臂承力段、前舱与主体平台',
    '中央重构台定位面与维护设备底板','门架加强肋与臂座底梁',
    '四组机械臂的肩轴与转折关节','循环侧舱至臂座的四路连续管道',
    '门架顶部供能母线与后场功率模块','中央重构台与前舱绝缘层',
    '四组工具头及重构台，仅作设备造型','中央台座隔振基础',
    '前舱工艺监测与后场控制面','侧舱与后场设备散热',
    '前舱观察窗和台面屏护','两侧检修通道与台面防滑层',
    '通用接口占位，不固定输入输出','居中北向控制器占位',
    '工具透镜与检修照明，仅作静态建筑表达',
]))


def build():
    a=np.zeros((H,D,W),dtype=np.uint8)

    def box(x,y,z,X,Y,Z,m):
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D
        a[y:Y+1,z:Z+1,x:X+1]=m

    def shell(x,y,z,X,Y,Z,m):
        box(x,y,z,X,Y,Z,m)
        box(x+1,y+1,z+1,X-1,Y-1,Z-1,0)

    def segment(start,end):
        current=list(start);result=[current.copy()]
        # 将斜梁中心线展开为六邻接阶梯，不能只在角上接触。
        while current!=list(end):
            for axis in (0,1,2):
                if current[axis]!=end[axis]:
                    current[axis]+=1 if end[axis]>current[axis] else -1
                    result.append(current.copy())
        return result

    box(14,0,0,38,0,16,C)
    box(0,0,17,52,0,54,C)
    box(12,0,55,40,0,60,C)
    for x in (14,35):box(x,1,18,x+3,1,51,R)
    for x in (0,52):
        box(x,1,18,x,1,53,S)
        for z in (19,30,41,52):box(x,2,z,x,2,z,LIGHT)

    shell(19,1,5,33,7,13,C)
    box(19,1,6,33,4,6,C)
    box(22,5,5,30,6,5,G)
    for x in (20,21,31,32):box(x,5,5,x,6,5,E)
    box(20,8,6,32,8,12,C)
    box(20,1,12,32,1,14,I)

    # 两座完整落地门架承托顶部设备与共轴服务梁。
    for z in (20,44):
        for x in (7,41):
            box(x,1,z,x+4,29,z+4,C)
            for y in (5,11,17,23):box(x,y,z,x+4,y+1,z,S)
            box(x-1,1,z-1,x+5,2,z+5,S)
        box(7,29,z,45,31,z+4,C)
        box(11,32,z+1,41,32,z+3,U)
        for x in (12,38):box(x,29,z,x+2,30,z+4,K)
    box(24,29,24,28,30,44,C)
    box(25,31,24,27,31,44,U)

    # 八角隔振台保留开放工作空间，工具头与台面之间留出加工间隙。
    zz,xx=np.ogrid[:D,:W];dx,dz=abs(xx-26),abs(zz-34)
    plinth=(np.maximum(dx,dz)<=8)&(dx+dz<=12)
    for y,material in ((1,T),(2,C),(3,R)):a[y][plinth]=material
    box(20,4,28,32,4,40,A)
    box(22,5,30,30,5,38,I)
    box(23,6,31,29,7,37,L)
    box(25,8,33,27,8,35,G)
    box(24,5,28,28,5,29,R)

    arms=[];routes=[]
    for left in (True,False):
        anchor_x=11 if left else 41
        for front in (True,False):
            anchor_z=24 if front else 44
            bend_z=27 if front else 41
            tool_z=30 if front else 38
            elbow_x=17 if left else 35;tool_x=22 if left else 30
            box(anchor_x-2,1,anchor_z-2,anchor_x+2,10,anchor_z+2,C)
            box(anchor_x-3,1,anchor_z-3,anchor_x+3,2,anchor_z+3,S)
            points=[[anchor_x,10,anchor_z],[anchor_x,18,anchor_z],
                    [elbow_x,21,bend_z],[tool_x,18,tool_z],[tool_x,12,tool_z]]
            centers=[points[0]]
            for start,end in zip(points,points[1:]):centers.extend(segment(start,end)[1:])
            for x,y,z in centers:box(x-1,y-1,z-1,x+1,y+1,z+1,C)
            for x,y,z in points[1:4]:box(x-1,y-1,z-1,x+1,y+1,z+1,K)
            box(tool_x-1,10,tool_z-1,tool_x+1,12,tool_z+1,L)
            box(tool_x,10,tool_z,tool_x,10,tool_z,LIGHT)
            label=('左' if left else '右')+('前' if front else '后')+'重构臂'
            arms.append(dict(name=label,base_contact=[anchor_x,8,anchor_z],
                             centers=centers,tool=[tool_x,10,tool_z]))
            # 供料侧舱和臂座有明确接点，管路不以底座单连通代替设备连接。
            pod_x=1 if left else 47;z=25 if front else 43
            box(pod_x,1,z-2,pod_x+4,7,z+2,C)
            box(pod_x,3,z-2,pod_x+4,5,z-2,U)
            box(pod_x,6,z+2,pod_x+4,6,z+2,V)
            xs=list(range(5,12)) if left else list(range(47,40,-1))
            for x in xs:box(x,5,z,x,5,z,P)
            routes.append(dict(cells=[[x,5,z] for x in xs],
                source_contact=[4 if left else 48,5,z],target_contact=[12 if left else 40,5,z]))

    shell(19,1,52,33,10,59,C)
    box(21,3,59,31,7,59,E)
    box(22,11,53,30,11,58,U)
    for x in (19,32):box(x,3,55,x+1,8,59,V)
    controller=[26,2,5];a[2,5,26]=CONTROL
    ports=[]
    for number,x in enumerate((20,22,24,28,30,32),1):
        a[2,5,x]=PORT
        ports.append(dict(id=f'通用接口{number}',pos=[x,2,5],face='north',
            purpose='任意物品／流体输入输出候选位；实际能力以正式仓室及Pattern为准'))
    data=dict(key='mx-c04',name=NAME,title=TITLE,size=[W,H,D],controller=controller,
        controller_face='north',ports=ports,arms=arms,cooling_routes=routes,
        description='前后双门架与顶部服务梁围合开放工坊，四组关节机械臂对准中央隔振重构台；两侧循环舱、检修道及后端控制设备分别布置。',
        purpose='既定职责方案为消耗许可图样、重构介质及定标成本执行物品重构，建筑模式复用工程搭建流水线。本版仅制作外观，未实装机械臂动画、物品复制或自动建造，不新增免费资源与毕业前置。',
        zones=[dict(name=n,pos=p) for n,p in [('工艺与主控',[26,8,9]),('中央重构台',[26,9,34]),('四臂工坊',[26,23,34]),('服务门架',[26,32,46]),('后端控制',[26,11,55])]],
        paths=[dict(min=[17,1,0],max=[35,4,4]),dict(min=[15,2,18],max=[17,4,51]),
               dict(min=[35,2,18],max=[37,4,51]),dict(min=[20,2,14],max=[32,4,20])])
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
        x,y,z=item['pos'];assert a[y,z+1,x] and np.all(a[y-1:y+2,z,x-1:x+2])
        assert not np.any(a[1:5,z-5:z,x-1:x+2]),'正面接线空间不足'
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max']
        assert not np.any(a[y:Y+1,z:Z+1,x:X+1]),'检修通道被占用'
    for arm in data['arms']:
        assert all(a[y,z,x] in (C,K,L) for x,y,z in arm['centers'])
        assert all(sum(abs(u-v) for u,v in zip(p,q))==1 for p,q in zip(arm['centers'],arm['centers'][1:]))
        x,y,z=arm['base_contact'];assert a[y,z,x]==C
        x,y,z=arm['tool'];assert a[y,z,x]==LIGHT
    expected=set()
    for route in data['cooling_routes']:
        cells=route['cells'];assert all(a[y,z,x]==P for x,y,z in cells)
        assert all(sum(abs(u-v) for u,v in zip(p,q))==1 for p,q in zip(cells,cells[1:]))
        for field,endpoint in [('source_contact',cells[0]),('target_contact',cells[-1])]:
            x,y,z=route[field];assert a[y,z,x]==C
            assert sum(abs(u-v) for u,v in zip(endpoint,[x,y,z]))==1
        expected.update(tuple(p) for p in cells)
    actual={(int(x),int(y),int(z)) for y,z,x in zip(*np.nonzero(a==P))}
    assert actual==expected,'发现未接入指定设备的管段'
    return dict(blocks=len(coords),unique_materials=len(STATES),palette={s:int(counts[i+1]) for i,s in enumerate(STATES)},
        actual_size_xyz=[W,H,D],connected=True,mirrored=True,controller_centered=True,
        universal_ports=True,clearance_passed=True,arm_paths_passed=True,arm_count=4,
        pipe_routes_passed=True,pipe_routes_count=4,open_pipe_ends=0,
        minimum_size_baseline=None,minimum_size_note='既定四台MAX需求不在原69项尺寸表中，无已冻结尺寸下限。',
        voltage_progression=dict(voltage='MAX',tier=14,lower_forms=[],status='范围内无低阶比较对象，不计通过率'),
        approved=False,installed=False,game_verified=False,survival_stage_verified=False,
        checks=['实际边界与声明尺寸相同，MAX机壳为最大单材','全部实体六邻接单连通且左右镜像','双门架落地，四臂从臂座至工具头的中心线逐格连续','四路循环管全部接入指定侧舱与臂座，无断头或额外管段','居中主控与六个通用接口保持五格接线净空','两侧检修道与前端工艺通道净空通过'])


if __name__=='__main__':
    cube,data=build();check=audit(cube,data)
    broken=cube.copy();broken[5,25,8]=0
    try:audit(broken,data)
    except AssertionError:pass
    else:raise AssertionError('未拒绝断管反例')
    print(f"四臂工坊几何、机械臂及循环管路通过：{check['blocks']}方块；断管反例已拒绝。")
