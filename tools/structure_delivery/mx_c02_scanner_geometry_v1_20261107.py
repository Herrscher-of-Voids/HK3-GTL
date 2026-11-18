# -*- coding: utf-8 -*-
"""物质谱系扫描仪：三环扫描通道、样本轨道与侧置数据柜独立外观候选。"""
from collections import deque
import numpy as np

W, H, D = 45, 29, 61
NAME = 'hk3gtl-mx-c02-scanner-v1-20261107'
TITLE = '物质谱系扫描仪（暂名）· 三环谱系扫描台'
STATES = [
    'gtlcore:component_assembly_line_casing_max', 'gtceu:clean_machine_casing',
    'gtceu:assembly_line_grating', 'gtceu:laser_safe_engraving_casing',
    'gtceu:advanced_computer_casing', 'gtceu:computer_heat_vent',
    'gtceu:nonconducting_casing', 'gtceu:high_power_casing',
    'gtceu:laminated_glass', 'gtceu:steel_pipe_casing',
    'gtceu:assembly_line_casing', 'hk3gtl:industrial_port_casing',
    'minecraft:diamond_block', 'minecraft:sea_lantern',
]
C, S, R, L, E, V, I, U, G, P, A, PORT, CONTROL, LIGHT = range(1,15)
ROLES = dict(zip(STATES,[
    'MAX原生装配线机壳：扫描环框架、数据柜和主体平台',
    '扫描环支座与精密轨道衬板', '两侧检修踏面与样本台防滑面',
    '扫描头与样本夹具，仅作设备造型', '谱系分析数据柜与前端读数面板',
    '数据柜及后置功率模块散热', '扫描头隔离座与上部母线绝缘层',
    '扫描环顶部供能母线与后置电源', '前舱观察窗及样本屏护',
    '侧柜至扫描环的六路连续冷却管', '双轨样本输送床与定位横梁',
    '通用接口位置占位，不限定输入输出', '居中北向控制器占位',
    '扫描透镜与检修照明，仅作静态建筑表达',
]))


def build():
    a=np.zeros((H,D,W),dtype=np.uint8)

    def box(x,y,z,X,Y,Z,m):
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D
        a[y:Y+1,z:Z+1,x:X+1]=m

    def shell(x,y,z,X,Y,Z,m):
        box(x,y,z,X,Y,Z,m)
        box(x+1,y+1,z+1,X-1,Y-1,Z-1,0)

    box(12,0,0,32,0,16,C)
    box(0,0,17,44,0,49,C)
    box(8,0,50,36,0,60,C)
    for x in (0,44):
        box(x,1,18,x,1,48,S)
        for z in range(20,49,7):box(x,2,z,x,2,z,LIGHT)
    for x in (9,34):box(x,1,18,x+1,1,48,R)

    # 控制舱融入样本台前端，不单列白框机柜；接口前方保留五格接线空间。
    shell(15,1,5,29,7,13,C)
    box(15,1,6,29,4,6,C)
    box(18,5,5,26,6,5,G)
    for x in (16,17,27,28):box(x,5,5,x,6,5,E)
    box(16,8,6,28,8,12,C)
    box(20,1,14,24,3,17,A)

    # 双轨样本床穿过三组开放八角扫描框，样本和镜头均有实体支撑。
    box(17,1,17,27,1,50,C)
    box(18,2,17,26,2,50,S)
    for x in (19,25):box(x,3,16,x,3,50,A)
    for z in (18,25,36,47):box(19,3,z,25,3,z,A)
    box(18,4,29,26,4,35,R)
    box(20,5,30,24,5,34,I)
    box(21,6,31,23,8,33,L)
    box(20,9,30,24,9,34,G)
    for x in (20,24):box(x,5,30,x,8,30,G)

    yy,xx=np.ogrid[:H,:W]
    dx,dy=abs(xx-22),abs(yy-15)
    outer=(np.maximum(dx,dy)<=11)&(dx+dy<=16)
    inner=(np.maximum(dx,dy)<=8)&(dx+dy<=12)
    frame=outer&~inner
    rings=[]
    for z in (21,32,43):
        for Z in range(z-1,z+2):a[:,Z,:][frame]=C
        for x in (12,29):
            box(x,1,z-2,x+3,7,z+2,C)
            box(x,2,z-2,x+3,3,z-2,S)
        box(20,24,z-1,24,25,z+1,I)
        box(20,23,z-1,24,23,z+1,L)
        box(21,22,z,23,22,z,LIGHT)
        for x,X in ((13,16),(28,31)):
            box(x,13,z,X,17,z,L)
        box(16,14,z,16,16,z,LIGHT)
        box(28,14,z,28,16,z,LIGHT)
        rings.append(dict(z=z,center=[22,15,z],outer_radius=11))
    box(20,27,21,24,27,43,C)
    box(21,28,21,23,28,43,U)
    for z in (21,32,43):box(20,26,z-1,24,26,z+1,C)

    # 数据柜位于检修通道外侧；外立面的读数、散热面有实际柜体背衬。
    for x in (1,36):
        shell(x,1,20,x+7,9,47,C)
        outer_x=1 if x==1 else 43
        for z in (22,29,36,43):
            box(outer_x,2,z,outer_x,7,z+2,E)
            box(outer_x,8,z,outer_x,8,z+2,V)
        box(x+2,9,23,x+5,9,44,E)
    for x in (7,37):box(x,5,20,x,7,44,C)
    routes=[]
    for z in (21,32,43):
        for left in (True,False):
            xs=list(range(8,15)) if left else list(range(36,29,-1))
            for x in xs:box(x,6,z,x,6,z,P)
            routes.append(dict(name=('左' if left else '右')+f'第{(z-21)//11+1}环冷却',
                cells=[[x,6,z] for x in xs],cabinet_contact=[7 if left else 37,6,z],
                scanner_contact=[15 if left else 29,6,z]))

    # 后场负责供电与谱系数据交接，外形不冒充真实数据库或免费图样。
    shell(17,1,52,27,13,59,C)
    box(18,3,59,26,10,59,E)
    box(19,14,53,25,14,58,E)
    for x in (10,29):
        shell(x,1,52,x+5,9,57,C)
        box(x+1,2,57,x+4,6,57,U)
        box(x+1,8,57,x+4,8,57,V)
    controller=[22,2,5];a[2,5,22]=CONTROL
    ports=[]
    for number,x in enumerate((16,18,20,24,26,28),1):
        a[2,5,x]=PORT
        ports.append(dict(id=f'通用接口{number}',pos=[x,2,5],face='north',
            purpose='通用物品／流体接口候选位，不固定输入或输出；实际能力以正式仓室及Pattern为准'))
    data=dict(key='mx-c02',name=NAME,title=TITLE,size=[W,H,D],controller=controller,
        controller_face='north',ports=ports,rings=rings,coolant_routes=routes,
        description='三组开放八角扫描框沿双轨样本床排列，顶部设供能母线；两侧数据柜经六路完整冷却管接入扫描框，后场设置谱系分析与供电模块。',
        zones=[dict(name=n,pos=p) for n,p in [('样本与主控',[22,8,9]),('三环扫描',[22,27,32]),('左数据柜',[4,9,34]),('右数据柜',[40,9,34]),('谱系分析',[22,14,56])]],
        paths=[dict(min=[13,1,0],max=[31,4,4]),dict(min=[9,2,18],max=[10,4,48]),dict(min=[34,2,18],max=[35,4,48])])
    return a,data


def audit(a,data):
    coords=np.argwhere(a)
    assert coords.min(axis=0).tolist()==[0,0,0]
    assert coords.max(axis=0).tolist()==[H-1,D-1,W-1]
    counts=np.bincount(a.ravel(),minlength=len(STATES)+1)
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
        assert not np.any(a[1:5,z-5:z,x-1:x+2]),'接口正面接线空间不足'
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max']
        assert not np.any(a[y:Y+1,z:Z+1,x:X+1]),'检修通道被占用'
    all_pipe_cells=set()
    for route in data['coolant_routes']:
        cells=route['cells']
        assert all(a[y,z,x]==P for x,y,z in cells)
        assert all(sum(abs(p-q) for p,q in zip(u,v))==1 for u,v in zip(cells,cells[1:]))
        for field,end in [('cabinet_contact',cells[0]),('scanner_contact',cells[-1])]:
            x,y,z=route[field]
            assert a[y,z,x]==C and sum(abs(p-q) for p,q in zip(end,[x,y,z]))==1
        all_pipe_cells.update(tuple(p) for p in cells)
    actual_pipe_cells={(int(x),int(y),int(z)) for y,z,x in zip(*np.nonzero(a==P))}
    assert actual_pipe_cells==all_pipe_cells,'存在未纳入设备路径的管段'
    return dict(blocks=len(coords),unique_materials=len(STATES),palette={s:int(counts[i+1]) for i,s in enumerate(STATES)},
        actual_size_xyz=[W,H,D],connected=True,mirrored=True,controller_centered=True,
        universal_ports=True,clearance_passed=True,pipe_routes_passed=True,pipe_routes_count=6,open_pipe_ends=0,
        minimum_size_baseline=None,minimum_size_note='既定四台MAX需求不在原69项尺寸表中，无已冻结尺寸下限。',
        voltage_progression=dict(voltage='MAX',tier=14,lower_forms=[],status='范围内无低阶比较对象，不计通过率'),
        approved=False,installed=False,game_verified=False,survival_stage_verified=False,
        checks=['实体包围盒与声明尺寸一致','MAX原生机壳为最大单材','全部实体六邻接单连通且左右镜像','居中主控与六个通用接口具备五格接线净空','两侧检修通道净空通过','全部六路冷却管逐格连续，两端均接指定设备，无额外断头管'])


if __name__=='__main__':
    cube,data=build();result=audit(cube,data)
    broken=cube.copy();broken[6,21,11]=0
    try:audit(broken,data)
    except AssertionError:pass
    else:raise AssertionError('回归检查未识别断管')
    print(f"几何与六路设备管线通过：{result['blocks']}方块；断管反例已拒绝。")
