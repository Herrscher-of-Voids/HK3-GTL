# -*- coding: utf-8 -*-
"""I42巨构龙骨与步进预制船坞：按构件流向组织的独立建筑。

变更记录 #1（2026-10-28）：新增完整候选几何，不修改批准结构或实例。
"""
import math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
W,H,D,CX=641,295,449,320
NAME='hk3gtl-i42-prefabrication-dock-v1-20261028'
TITLE='奇观构件预制工厂 · 巨构龙骨与步进预制船坞'


class Material:
    WFV='hk3gtl:voltage_machine_casing_wfv'
    CONTROL='minecraft:diamond_block'
    PORT='hk3gtl:industrial_port_casing'
    ROBUST='gtceu:titanium_turbine_casing'
    CLEAN='gtceu:clean_machine_casing'
    ASSEMBLY='gtceu:assembly_line_casing'
    COMPUTER='gtceu:advanced_computer_casing'
    ATOMIC='gtceu:black_large_metal_sheet'
    POWER='gtceu:bronze_brick_casing'
    LASER='gtceu:laser_safe_engraving_casing'
    TURBINE='gtceu:stainless_steel_turbine_casing'
    MACERATOR='gtceu:secure_maceration_casing'
    VENT='gtceu:computer_heat_vent'
    GEAR='gtceu:tungstensteel_gearbox'
    TUNG_PIPE='gtceu:tungstensteel_pipe_casing'
    STEEL_PIPE='gtceu:steel_pipe_casing'
    GRATE='gtceu:assembly_line_grating'
    IRIDIUM='gtlcore:iridium_casing'
    PROCESS='gtlcore:process_machine_casing'
    DIMENSION='gtlcore:dimension_connection_casing'
    MULTI='gtlcore:multi_functional_casing'
    LAFIUM='gtlcore:lafium_mechanical_casing'
    GLASS='gtlcore:hsss_reinforced_borosilicate_glass'
    FILTER='gtlcore:law_filter_casing'
    INERT='gtceu:inert_machine_casing'
    HEATPROOF='gtceu:heatproof_machine_casing'
    INSULATE='gtceu:nonconducting_casing'
    FROST='gtceu:frostproof_machine_casing'
    STABLE='gtceu:stable_machine_casing'
    SOLID='gtceu:solid_machine_casing'
    INTAKE='gtceu:engine_intake_casing[active=false]'
    STRESS='gtceu:stress_proof_casing'
    MIXING='gtceu:reaction_safe_mixing_casing'
    VIBRATION='gtceu:vibration_safe_casing'
    PLASCRETE='gtceu:steel_brick_casing'
    LAMINATED='gtceu:laminated_glass'
    FUSION_GLASS='gtceu:fusion_glass'
    STEEL='gtceu:steel_machine_casing'
    BLUE_GLASS='minecraft:light_blue_stained_glass'
    BLACK_GLASS='minecraft:black_stained_glass'
    LIGHT='minecraft:sea_lantern'
    GOLD='minecraft:gold_block'
    IRON='minecraft:iron_block'
    OBSIDIAN='minecraft:obsidian'


material=Material()
STATES=sorted(v for k,v in vars(Material).items() if k.isupper())
IDS={s:i+1 for i,s in enumerate(STATES)}
assert len(STATES)==len(IDS)==44
ROLES={s:'分段预制、模具、吊运或维护构件' for s in STATES}
ROLES.update({getattr(material,k):v for k,v in dict(
    WFV='多层加工厂房、步进装配梁与分段构件的主体识别机壳',
    CONTROL='中轴工艺控制桥楼的主控预览标记',PORT='连续外墙内嵌的计划工艺接口占位',
    ROBUST='龙门吊立柱、斜撑及船坞承力肋',CLEAN='隔离装配段与桥楼浅色门框',
    ASSEMBLY='导轨、定位台和加工机匣',COMPUTER='工艺计量、图样和构件身份检查台',
    ATOMIC='龙骨装配定位胎架和模具的黑色接触面',POWER='铜色接地干线与导能母排构件',
    LASER='精密接头与认知载体框刻写工位',TURBINE='通风与冷却设备金属罩',
    MACERATOR='模具去边加工设备底座',VENT='厂房屋顶排热格栅',GEAR='行走小车和模具转位传动箱',
    TUNG_PIPE='分段检修流体汇接管路',STEEL_PIPE='工位供气与冷却支路',GRATE='吊运检修通道及屋顶栈桥',
    IRIDIUM='精密定位台的台面',PROCESS='压力成形与分段压合机匣',DIMENSION='空间接头工位屏蔽层',
    MULTI='八类预制工位的组合装配机匣',LAFIUM='重载承座与龙骨对接枢纽',GLASS='厂房长窗及工位安全观察面',
    FILTER='隔离壁预制工位的分层滤栅',INERT='认知载体框的绝缘衬层',HEATPROOF='热端壳段预制模具',
    INSULATE='母排和工作腔隔离内衬',FROST='冷端壳段预制模具',STABLE='定位台低基础',
    SOLID='坞内阶梯与设备基础',INTAKE='通风工位进气端',STRESS='重型承力骨架定位柱',
    MIXING='汇接件工位反应安全衬板',VIBRATION='机床与装配胎架隔振座',PLASCRETE='两侧条形基础和坞底承载带',
    LAMINATED='调度桥楼及精密装配窗带',FUSION_GLASS='重构工作腔的窄观察条',STEEL='坞内轮轨与吊具钢梁',
    BLUE_GLASS='冷却支路液位和检修导向',BLACK_GLASS='图样读取台暗色观察面',LIGHT='坞底导向灯和检修照明',
    GOLD='精密接头少量标定触点',IRON='桥楼门廊浅色金属边框',OBSIDIAN='检定台黑体标定面').items()})


def build():
    cube=np.zeros((H,D,W),dtype=np.uint8)

    def box(a,b,state):
        x,y,z=map(int,a);X,Y,Z=map(int,b)
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D,(a,b)
        cube[y:Y+1,z:Z+1,x:X+1]=IDS[state] if state else 0

    def shell(a,b,state,t=3):
        box(a,b,state)
        if all(b[k]-a[k]+1>2*t for k in range(3)):
            box(tuple(v+t for v in a),tuple(v-t for v in b),None)

    def beam(a,b,state,r=2):
        n=max(abs(b[i]-a[i]) for i in range(3))
        for j in range(n+1):
            p=[round(a[i]+(b[i]-a[i])*j/max(1,n)) for i in range(3)]
            box(tuple(max(0,v-r) for v in p),tuple(min(s-1,v+r) for v,s in zip(p,(W,H,D))),state)

    def hoop(z,y,r,state,t=3,half=False):
        yy,xx=np.ogrid[:H,:W]
        distance=(xx-CX)**2+(yy-y)**2
        mask=(distance<=r*r)&(distance>=(r-t)**2)
        if half: mask&=yy>=y
        for depth in range(z-3,z+4):
            layer=cube[:,depth,:]
            layer[mask]=IDS[state]

    zones=[]
    # 两侧有真实工艺层与厂房空腔，中央保留贯通的开放式船坞。
    for left,right in ((0,139),(501,640)):
        box((left,0,0),(right,11,D-1),material.PLASCRETE)
        shell((left,12,0),(right,203,D-1),material.WFV,4)
        for y in range(16,196,30):
            box((left+4,y,4),(right-4,y+2,D-5),material.WFV)
            for z in range(14,D-25,40):
                for x in (left+17,left+72):
                    shell((x,y+3,z),(x+42,y+17,z+24),material.ASSEMBLY,2)
                    box((x+3,y+11,z-1),(x+38,y+14,z+1),material.COMPUTER)
                    box((x+4,y+7,z+22),(x+37,y+10,z+25),material.GLASS)
            for x in (left,left+136):
                box((x,y+8,12),(x+3,y+15,D-13),material.GLASS)
        for z in range(0,D,32):
            box((left,12,z),(left+5,207,min(D-1,z+5)),material.ROBUST)
            box((right-5,12,z),(right,207,min(D-1,z+5)),material.ROBUST)
            box((left,202,z),(right,207,min(D-1,z+5)),material.GRATE)
        # 屋顶服务街：冷却鳍片、风口、检修廊与供气管有各自形体。
        for z in range(24,425,56):
            shell((left+17,208,z),(right-17,226,z+27),material.WFV,3)
            box((left+21,227,z+3),(right-21,229,z+24),material.VENT)
            for dx in range(23,114,15):
                box((left+dx,209,z+2),(left+dx+2,225,z+5),material.HEATPROOF)
            box((left+8,208,z),(left+12,217,z+27),material.STEEL_PIPE)
            box((right-12,208,z),(right-8,217,z+27),material.TURBINE)
        box((left+58,208,0),(left+81,211,D-1),material.GRATE)
        # 端墙延续楼层、承力肋和装配门，避免变成不分节的整幅机壳。
        for z0,z1 in ((0,3),(D-4,D-1)):
            for dx in (5,45,90,130):
                box((left+dx,14,z0),(left+dx+4,201,z1),material.ROBUST)
            for y in range(42,196,30):
                box((left+5,y,z0),(right-5,y+3,z1),material.CLEAN)
            for y in range(54,187,30):
                for a,b in ((12,38),(52,83),(98,123)):
                    box((left+a,y,z0),(left+b,y+11,z1),material.LAMINATED)
            box((left+43,19,z0),(left+47,40,z1),material.CLEAN)
            box((left+93,19,z0),(left+97,40,z1),material.CLEAN)
            box((left+43,41,z0),(left+97,45,z1),material.CLEAN)
            box((left+48,19,z0),(left+92,40,z1),None)
            box((left+48,19,z0+1),(left+92,39,z0+1),material.GLASS)
            for y in (24,31,38):
                box((left+48,y,z0+1),(left+92,y,z0+1),material.STEEL)
        zones.append(dict(name='西侧分层部件加工厂' if left==0 else '东侧分层部件加工厂',pos=[left+10,18,25]))

    # 坞底为条形承台，不以整幅实心大底座填充包围盒。
    for x in (152,200,296,344,432,480):
        box((x-7,0,0),(x+7,13,D-1),material.PLASCRETE)
        box((x-5,14,0),(x+5,17,D-1),material.STEEL)
        for z in range(18,D,32):
            box((x-3,18,z),(x+3,19,min(D-1,z+3)),material.LIGHT)
    for z in (0,24,104,184,264,344,424,442):
        box((136,0,z),(504,9,min(D-1,z+6)),material.PLASCRETE)
        box((141,10,z),(499,13,min(D-1,z+5)),material.ROBUST)

    # 连续步进龙门：九组门架共用纵向轨道，斜撑与厂房相连。
    for z in range(22,439,52):
        for x,inner in ((147,173),(493,467)):
            box((x-7,0,z-7),(x+7,246,z+7),material.ROBUST)
            box((x-4,247,z-6),(x+4,279,z+6),material.WFV)
            beam((x,24,z),(inner,238,z),material.WFV,5)
            for y in range(38,236,28):
                beam((x,y,z),(inner,y+18,z),material.GRATE,1)
            beam((x,218,z),(CX,282,z),material.WFV,5)
        box((141,280,z-8),(499,287,z+8),material.WFV)
        box((141,288,z-5),(499,291,z+5),material.GRATE)
        box((153,292,z-2),(487,294,z+2),material.STEEL)
        # 横移小车与双索吊钩，不把构件悬空摆放。
        box((CX-23,267,z-10),(CX+23,279,z+10),material.ASSEMBLY)
        box((CX-18,262,z-7),(CX+18,266,z+7),material.GEAR)
        for dx in (-14,14):
            beam((CX+dx,263,z),(CX+dx,188,z),material.ATOMIC,1)
        box((CX-18,183,z-5),(CX+18,188,z+5),material.TURBINE)
    for x in (147,493):
        box((x-5,245,15),(x+5,253,D-1),material.ASSEMBLY)
        box((x-4,254,15),(x+4,257,D-1),material.POWER)

    # 一条在制巨构龙骨，纵向逐段长出承力肋和隔离壳，而非完整飞船替身。
    for x in (CX-65,CX,CX+65):
        box((x-7,86,50),(x+7,98,407),material.LAFIUM)
        box((x-4,99,50),(x+4,103,407),material.WFV)
    for z in range(65,405,42):
        box((CX-96,76,z-5),(CX+96,85,z+5),material.WFV)
        for x in (CX-83,CX+83):
            box((x-7,19,z-9),(x+7,75,z+9),material.STRESS)
            box((x-11,18,z-12),(x+11,23,z+12),material.VIBRATION)
        r=80 if z<190 else 65 if z<310 else 48
        hoop(z,104,r,material.WFV,8)
        hoop(z,104,r-10,material.CLEAN,3)
        box((CX-r-5,100,z-4),(CX+r+5,108,z+4),material.WFV)
        if z>180:
            for dx in (-r+12,r-12):
                box((CX+dx-2,107,z-3),(CX+dx+2,145,z+3),material.FILTER)
        if z>300:
            box((CX-r+10,150,z-4),(CX+r-10,156,z+4),material.FUSION_GLASS)
        zones.append(dict(name=f'在制龙骨分段 {1+(z-65)//42}',pos=[CX,101,z]))

    # 八类预制工位两侧成对，模具、立柱、母排、工作腔各有实际形体。
    names=('承力骨架定位','导能母排预制','隔离壁叠层','重构工作腔压合',
           '认知载体框刻写','冷热壳段成形','专用核心安装座','检修流体汇接')
    for side in (-1,1):
        x=176 if side<0 else 464
        for k,z in enumerate(range(36,421,52)):
            a,b=x-22,x+22
            box((a,17,z-16),(b,23,z+16),material.VIBRATION)
            box((a+3,24,z-13),(b-3,28,z+13),material.STABLE)
            if k==0:
                for xx in (a+5,b-5):
                    box((xx-3,29,z-10),(xx+3,68,z+10),material.STRESS)
                beam((a+5,68,z),(b-5,68,z),material.WFV,4)
            elif k==1:
                for dz in (-9,0,9):
                    box((a+4,29,z+dz-2),(b-4,34,z+dz+2),material.INSULATE)
                    box((a+4,35,z+dz-1),(b-4,38,z+dz+1),material.POWER)
            elif k==2:
                for dz in (-10,-4,2,8):
                    box((a+4,29,z+dz),(b-4,61,z+dz+2),material.FILTER)
                box((a+2,62,z-12),(b-2,65,z+12),material.INERT)
            elif k==3:
                shell((a+3,29,z-12),(b-3,62,z+12),material.DIMENSION,3)
                box((a+5,40,z-12),(b-5,48,z-10),material.FUSION_GLASS)
            elif k==4:
                shell((a+3,29,z-12),(b-3,64,z+12),material.LASER,3)
                box((a+7,36,z-13),(b-7,51,z-11),material.BLACK_GLASS)
                box((a+8,30,z-8),(b-8,32,z+8),material.OBSIDIAN)
                box((a+10,52,z-12),(b-10,54,z-10),material.GOLD)
            elif k==5:
                for xx,state in ((a+9,material.HEATPROOF),(b-9,material.FROST)):
                    shell((xx-6,29,z-12),(xx+6,62,z+12),state,2)
                box((a+4,63,z-9),(b-4,65,z+9),material.INTAKE)
            elif k==6:
                box((a+4,29,z-11),(b-4,34,z+11),material.MACERATOR)
                shell((a+7,35,z-9),(b-7,54,z+9),material.PROCESS,3)
                box((a+9,55,z-7),(b-9,58,z+7),material.IRIDIUM)
            else:
                shell((a+3,29,z-12),(b-3,47,z+12),material.MIXING,3)
                for dz in (-8,8):
                    box((a+4,48,z+dz-2),(b-4,53,z+dz+2),material.TUNG_PIPE)
                box((a+8,36,z-13),(b-8,43,z-10),material.BLUE_GLASS)
            box((a,24,z-18),(a+4,44,z-14),material.MULTI)
            box((a+1,37,z-19),(a+3,41,z-18),material.COMPUTER)
            box((a+5,18,z+16),(b-5,22,z+21),material.SOLID)
            zones.append(dict(name=('西' if side<0 else '东')+'侧 · '+names[k],pos=[x,20,z]))

    # 中轴前端工艺桥楼：主控与接口嵌入连续外墙，不另立一块面板。
    box((CX-115,0,0),(CX+115,13,48),material.PLASCRETE)
    shell((CX-112,14,0),(CX+112,68,48),material.WFV,4)
    box((CX-109,38,1),(CX+109,42,46),material.WFV)
    for dx in (-108,-83,-58,-33,31,56,81,106):
        box((CX+dx,14,0),(CX+dx+2,66,2),material.CLEAN)
    box((CX-108,39,0),(CX+108,41,2),material.IRON)
    for dx in range(-100,100,25):
        box((CX+dx,43,0),(CX+dx+17,57,0),material.LAMINATED)
    box((CX-113,69,0),(CX+113,72,49),material.GRATE)
    # 桥楼借横向设备廊连到两侧厂房，预留中央开放船坞。
    for x0,x1 in ((129,211),(429,511)):
        box((x0,18,8),(x1,23,34),material.WFV)
        shell((x0,24,8),(x1,53,34),material.WFV,3)
        box((x0+3,35,8),(x1-3,44,9),material.GLASS)
    box((CX-2,24,0),(CX+2,28,3),material.WFV)
    box((CX,26,0),(CX,26,0),material.CONTROL)
    labels=('魂钢精密骨架输入','I40专用材料输入','导能元件输入','预制工艺介质输入',
            '专用预制构件交接','边角料分类回收','图样与授权核验','维护及流体汇接')
    ports=[]
    for name,dx in zip(labels,(-96,-72,-48,-24,24,48,72,96)):
        box((CX+dx-2,24,0),(CX+dx+2,28,3),material.WFV)
        box((CX+dx,26,0),(CX+dx,26,0),material.PORT)
        ports.append(dict(id=name,pos=[CX+dx,26,0],face='north',purpose='计划工艺接口占位，正式能力另行验收'))
    return cube,dict(key='i42',name=NAME,title=TITLE,candidate_version='V1',size=[W,H,D],
        controller=[CX,26,0],controller_face='north',ports=ports,paths=[],zones=zones,
        description='单一开放纵向船坞内，逐段长出的承力肋和隔离壳固定在真实胎架上；九组步进龙门吊共用连续轨道，双索吊具对应在制龙骨。两侧分层加工厂房与八类预制工位完成材料到专用大型构件的交接，桥楼主控沿中轴嵌入连续外墙。',
        construction_notes=dict(materials='WFV主体机壳，钛承力架、铜母排和黑色胎架按功能分工。',
            function='八类预制构件按W01–W15各取组合，不是万能构件或一键建造器。',
            stage='仅建筑候选；WFV映射不代表正式配方、控制器或研究已验收。'))


if __name__=='__main__':
    cube,data=build()
    counts=np.bincount(cube.ravel(),minlength=len(STATES)+1)
    print(dict(size=data['size'],blocks=int(counts[1:].sum()),wfv=int(counts[IDS[material.WFV]]),
        unused=[s for s in STATES if not counts[IDS[s]]]),flush=True)
