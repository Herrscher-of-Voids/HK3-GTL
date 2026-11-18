# -*- coding: utf-8 -*-
"""I21大型崩坏能反应堆：在I20 V3之外新增IMV闭式回路与多列透平设施。

【文件职责】读取不可变前阶段蓝图，在原空气区生成完整累积建筑及几何核对。
【变更记录 #1】2026-10-23 20:25:40（建筑候选V1，不增加模组修订号）
删除：无。新增：双筒闭式散热塔楼、双腔核岛、再生换热厅、燃料分类厅和四列透平厅。
修改：以IMV主机壳表达本阶段新增主体，主控仍为I19原位[95,3,20]。
用途：为高吞吐持续供能与分区检修提供建筑表达；不注册机器、配方或实际能力。
【变更记录 #2】2026-10-23 20:31:41（设备端点复核）
删除：三处在设备内部空腔提前停止的管线末端。新增：冷却进管接设备脊、换热回流接容器壳、燃料转运接屏蔽容器。
修改：延长新阶段管段至已有设备实体，不改旧块。用途：防止把穿墙但悬停于空气的末端当作已连接。
"""
import collections
import copy
import hashlib
import json
import math

import numpy as np
from scipy.ndimage import label

from build_i20_qsv_second_unit_v1 import STATES as OLD_STATES
from build_i19_hbv_coastal_station_v3 import AIR, WHITE, STEEL, VESSEL, GLASS, PIPE, GRATE, VENT, PANEL, GEAR, PORT, CORE
from redesign69_geometry import ROOT
from structure_size_baseline import require

OUT = ROOT/'deliveries/I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023'
LOG = ROOT/'logs/i21-imv-cogeneration-v1-20261023'
BASE = ROOT/'deliveries/I20_中型崩坏能反应堆_检修厂房与外围路修订_V3_20261023/i20/blueprint.json'
BASE_SHA = 'f9b3fe7818ea605318d9c10998e27a86fdcc2191c783efc8eda797f6e1247279'
NAME = 'i21-imv-closed-loop-cogeneration-v1'
W, H, D = 326, 194, 286
STATES = OLD_STATES + ['hk3gtl:voltage_machine_casing_imv']
IMV = len(OLD_STATES)


class Site:
    """逐次写入拒绝覆盖全部I20旧体素；空气内的新构件允许设计迭代。"""
    def __init__(self, before):
        self.cells = np.zeros((H, D, W), dtype=np.uint8)
        for b in before['blocks']:
            x,y,z=b['pos']; self.cells[y,z,x]=STATES.index(b['state'])
        self.original=self.cells.copy()
        self.ports=copy.deepcopy(before['ports'])
        self.paths=copy.deepcopy(before['paths'])
        self.zones=copy.deepcopy(before['zones'])

    def box(self, lo, hi, mat, shell=False):
        x0,y0,z0=lo; x1,y1,z1=hi
        assert 0<=x0<=x1<W and 0<=y0<=y1<H and 0<=z0<=z1<D,(lo,hi)
        if shell:
            for y in (y0,y1): self.box((x0,y,z0),(x1,y,z1),mat)
            for x in (x0,x1): self.box((x,y0,z0),(x,y1,z1),mat)
            for z in (z0,z1): self.box((x0,y0,z),(x1,y1,z),mat)
            return
        old=self.original[y0:y1+1,z0:z1+1,x0:x1+1]
        assert not np.any((old!=AIR)&(old!=mat)),('覆盖I20原块',lo,hi,STATES[mat])
        self.cells[y0:y1+1,z0:z1+1,x0:x1+1]=mat

    def ring(self,cx,cz,y,radius,thick,mat,filled=False):
        r=math.ceil(radius);x0=max(0,cx-r);x1=min(W-1,cx+r);z0=max(0,cz-r);z1=min(D-1,cz+r)
        zz,xx=np.ogrid[z0:z1+1,x0:x1+1];s=(xx-cx)**2+(zz-cz)**2
        mask=s<=radius**2
        if not filled:mask &= s>=max(0,radius-thick)**2
        old=self.original[y,z0:z1+1,x0:x1+1]
        assert not np.any(mask&(old!=AIR)&(old!=mat)), '环体覆盖前阶段'
        self.cells[y,z0:z1+1,x0:x1+1][mask]=mat

    def tube(self,points,mat=PIPE,radius=1):
        for a,b in zip(points,points[1:]):
            assert sum(a[i]!=b[i] for i in range(3))<=1,(a,b)
            self.box(tuple(min(a[i],b[i])-radius for i in range(3)),tuple(max(a[i],b[i])+radius for i in range(3)),mat)

    def hall(self,lo,hi):
        x0,y0,z0=lo;x1,y1,z1=hi
        self.box((x0,0,z0),(x1,1,z1),STEEL)
        self.box(lo,hi,IMV,True)
        for y in (5,y1-4):
            for z in (z0,z1):self.box((x0,y,z),(x1,y,z),WHITE)
        for x in range(x0+5,x1-5,15):
            for z in (z0,z1):self.box((x,10,z),(x+6,min(18,y1-7),z),GLASS)

    def port(self,code,pos,face,purpose):
        self.box(pos,pos,PORT);self.ports.append({'id':code,'pos':list(pos),'face':face,'purpose':purpose})


def build():
    assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
    before=json.loads(BASE.read_text('utf-8'));a=Site(before)
    # 外围道路完整包住本阶段建筑；I20后路转为厂区内部横向检修路并原样保留。
    for lo,hi in [((271,0,0),(325,0,6)),((321,0,0),(325,0,285)),
                  ((0,0,233),(5,0,285)),((0,0,281),(325,0,285))]: a.box(lo,hi,STEEL)
    for lo,hi in [((271,0,7),(277,0,280)),((318,0,7),(320,0,280)),
                  ((6,0,233),(320,0,240)),((6,0,274),(320,0,280))]: a.box(lo,hi,GRATE)

    # 双筒闭式换热器由完整门架包络，外露散热百叶取代又一座相同的敞口双曲塔。
    a.box((278,0,10),(317,2,75),STEEL)
    for cz in (29,57):
        a.ring(297,cz,3,15,1,STEEL,True)
        for y in range(4,176):
            a.ring(297,cz,y,14,2,VESSEL)
            if y in (22,55,88,121,154):a.ring(297,cz,y,15,2,PIPE)
        for y in range(176,187):
            r=max(4,math.sqrt(max(0,14**2-((y-175)*1.2)**2)))
            a.ring(297,cz,y,r,3,VESSEL)
        a.box((294,187,cz-3),(300,190,cz+3),PIPE,True)
    for x in (278,315):
        for z in (10,73):a.box((x,2,z),(x+2,189,z+2),IMV)
    for y in (18,50,82,114,146,178):
        for z in (10,73):a.box((278,y,z),(317,y+2,z+2),IMV)
        for x in (278,315):a.box((x,y,10),(x+2,y+2,75),IMV)
        # 成组散热盒有厚度、背接换热筒，保留连续竖向空气槽。
        for x in (279,313):
            for z in (17,33,49,65):a.box((x,y-10,z),(x+3,y-2,z+6),VENT)
    for z in (10,73):a.box((278,190,z),(317,193,z+2),IMV)
    for x in (278,315):a.box((x,190,10),(x+2,193,75),IMV)
    for z in (26,54):a.box((278,190,z),(317,193,z+6),IMV)
    # 每个散热层的完整管壳集流横臂连接外侧散热盒与内筒。
    for y in (12,44,76,108,140,172):
        for z in (20,36,52,68):a.tube([(281,y,z),(297,y,z),(315,y,z)],VESSEL,0)
    a.zones.append({'name':'IMV双筒闭式散热塔楼','pos':[297,193,43]})

    # 低位循环泵房与北侧塔楼、南侧核岛组成第三回路，接口嵌泵体侧壳。
    a.hall((278,2,80),(317,23,99))
    for z in (84,94):
        a.box((284,3,z-2),(312,11,z+2),VESSEL,True)
        a.box((292,12,z-1),(298,14,z+1),GEAR)
        a.box((308,3,z-1),(317,7,z+1),PANEL)
    a.port('C5',(317,3,84),'east','IMV第三回路冷却介质入口（计划）')
    a.port('C6',(317,3,94),'east','IMV第三回路热排流出口（计划）')
    a.box((279,2,80),(283,7,80),AIR)
    a.tube([(297,8,69),(297,8,84)])
    a.tube([(300,15,94),(310,15,94),(310,15,119)])

    # 双腔屏蔽核岛，内有分区压力容器与连续设备脊；不把钻石块当作装饰。
    a.hall((280,2,108),(317,104,174))
    a.box((281,104,109),(316,104,173),AIR)
    for z in range(108,175):
        roof=104+round(10*math.sin(math.pi*(z-108)/66))
        a.box((280,roof-2,z),(317,roof,z),IMV)
        for x in (280,317):a.box((x,104,z),(x,roof,z),IMV)
    for z in (108,140,172):
        for x in (280,315):a.box((x,2,z),(x+2,104,z+2),IMV)
        a.box((280,96,z),(317,99,z+2),WHITE)
    for cz in (126,156):
        for y in range(6,88):a.ring(299,cz,y,12,2,VESSEL)
        for y in (5,88):a.ring(299,cz,y,12,1,VESSEL,True)
        a.box((297,6,cz-2),(301,87,cz+2),IMV)
    a.tube([(299,36,126),(299,36,156)],PANEL)
    a.box((299,36,140),(299,36,140),CORE)
    a.box((280,2,135),(280,8,141),AIR)
    a.box((278,0,100),(279,0,179),GRATE)
    assert a.cells[15,126,299] == IMV
    a.tube([(310,15,119),(299,15,119),(299,15,126)],PIPE)
    a.tube([(299,20,163),(312,20,163),(312,20,94)],PIPE)
    a.zones.append({'name':'IMV分区双腔屏蔽核岛','pos':[299,114,140]})

    # 再生换热厅内有三组卧式换热器、轴承座和回流集管，西门通原东路。
    a.hall((278,2,183),(317,36,219))
    for z in (190,201,212):
        for x in (283,307):a.box((x,2,z-3),(x+3,5,z+3),STEEL)
        a.box((284,6,z-3),(309,16,z+3),VESSEL,True)
        a.box((291,17,z-2),(302,19,z+2),IMV)
        a.tube([(309,10,z),(313,10,z)],PIPE)
    a.tube([(313,10,190),(313,10,212)],PIPE)
    a.box((278,2,198),(278,8,204),AIR)
    a.box((278,0,180),(317,0,182),GRATE)
    a.zones.append({'name':'IMV再生换热厅','pos':[298,36,201]})

    # 南侧燃料分类与周转厅填入实际工艺设备和装卸空间，不留无说明空板。
    a.hall((12,2,241),(99,32,273))
    for x in (24,44,64,84):
        a.box((x-5,2,248),(x+7,4,266),STEEL)
        a.box((x-3,5,250),(x+5,12,260),VESSEL,True)
        a.box((x-1,13,252),(x+3,15,258),IMV)
        a.box((x,6,249),(x+2,9,249),GEAR)
    for x in (24,80):
        a.box((x,3,241),(x,6,250),PANEL)
    a.port('F5',(24,3,241),'north','IMV批量燃料棒送入分配设备（计划）')
    a.port('F6',(80,3,241),'north','IMV乏棒与损坏棒分类交付（计划）')
    a.box((36,2,241),(41,8,241),AIR)
    for x in (14,96):
        for z in (244,270):a.box((x,2,z),(x+1,25,z+1),IMV)
    for z in (245,270):a.box((14,24,z),(97,25,z+1),STEEL)
    a.box((55,26,245),(57,28,271),IMV)
    a.box((54,26,255),(58,30,260),GEAR)
    a.tube([(56,25,257),(56,16,257)],PIPE,0)
    a.box((94,4,253),(99,12,263),VESSEL,True)
    a.zones.append({'name':'IMV燃料分配与乏棒分类厅','pos':[55,32,257]})

    # 四列透平和一体发电机壳共享长跨厂房；四个能源口嵌发电机端壳。
    a.hall((110,2,241),(317,46,273))
    a.box((111,46,242),(316,46,272),AIR)
    for z in range(241,274):
        roof=46+round(9*math.sin(math.pi*(z-241)/32))
        a.box((110,roof-1,z),(317,roof,z),IMV)
        for x in (110,317):a.box((x,46,z),(x,roof,z),IMV)
        for x in (135,182,229,276):
            if 252<=z<=262:a.box((x,roof,z),(x+8,roof,z),GLASS)
    for x in (110,159,208,257,315):
        for z in (241,272):a.box((x,2,z),(x+2,46,z+1),IMV)
        for z in range(242,273):
            roof=46+round(9*math.sin(math.pi*(z-241)/32))
            a.box((x,roof-3,z),(x+2,roof-2,z),WHITE)
    for n,x in enumerate((120,167,214,261),9):
        a.box((x-2,2,248),(x+39,4,268),STEEL)
        a.box((x,5,250),(x+28,16,264),VESSEL,True)
        a.box((x+4,17,252),(x+23,20,262),IMV)
        a.box((x+29,5,253),(x+36,13,263),GEAR,True)
        a.box((x+32,2,263),(x+38,11,273),VESSEL,True)
        a.box((x+34,3,263),(x+36,6,272),PANEL)
        a.port('E'+str(n),(x+35,3,273),'south','IMV第'+str(n-8)+'列一体发电机电能输出（计划）')
        a.box((x+5,2,241),(x+11,9,241),AIR)
    a.zones.append({'name':'IMV四列长跨透平发电厅','pos':[214,55,257]})

    # 高架主管仅在新阶段范围内布置，跨路有净高且由端部及中途门架承托。
    a.tube([(299,48,168),(299,48,236),(284,48,236),(284,48,254),(284,20,254)])
    for x,z in ((299,177),(299,225),(284,237)):
        for sx in (x-3,x+3):a.box((sx,0,z),(sx+1,45,z+1),IMV)
        a.box((x-3,46,z),(x+4,46,z+1),STEEL)
    a.tube([(296,12,268),(312,12,268),(312,12,212)],PIPE)
    assert a.cells[10,168,299] == VESSEL
    a.tube([(313,10,190),(313,10,168),(299,10,168)],PIPE)
    # 分配支管在透平自身上方终止，各端确实接到机壳，不悬停在空气中。
    a.tube([(132,23,254),(284,23,254)],PIPE)
    for x in (132,179,226,273):a.tube([(x,23,254),(x,20,254)],PIPE)
    assert a.cells[8,138,299] == VESSEL
    a.tube([(99,8,257),(107,8,257),(107,8,236),(278,8,236),(278,8,138),(299,8,138)],VESSEL,0)
    # 侧置转运管廊不占用既有道路；支柱贴管底并避开人行门洞。
    for x,z in ((107,257),(107,244),(278,226),(278,178)):
        a.box((x,0,z),(x,7,z),IMV)
    for x in (150,200,250):
        a.box((x,0,240),(x,6,240),IMV)
        a.box((x,7,236),(x,7,240),STEEL)

    a.paths += [
        {'name':'IMV东区西侧纵向操作道','min':[271,1,7],'max':[276,4,232]},
        {'name':'IMV东侧外围路','min':[321,1,0],'max':[325,4,285]},
        {'name':'IMV南厂房前七格净空装卸通道','min':[6,1,233],'max':[270,4,239]},
        {'name':'IMV全部后墙外维护带','min':[6,1,274],'max':[320,4,280]},
        {'name':'IMV南侧完整外围路','min':[0,1,281],'max':[325,4,285]},
        {'name':'IMV分类厅进门通道','min':[36,3,241],'max':[41,6,247]},
        {'name':'IMV透平厅前维护通廊','min':[114,3,243],'max':[313,6,247]}]
    for p in a.paths:
        x0,y0,z0=p['min'];x1,y1,z1=p['max']
        assert np.all(a.cells[y0:y1+1,z0:z1+1,x0:x1+1]==AIR),('通道堵塞',p)
    frozen=a.original!=AIR
    assert np.array_equal(a.cells[frozen],a.original[frozen])
    _,components=label(a.cells!=AIR);assert components==1,components
    yy,zz,xx=np.nonzero(a.cells)
    blocks=[{'pos':[int(x),int(y),int(z)],'state':STATES[int(a.cells[y,z,x])]} for y,z,x in zip(yy,zz,xx)]
    data={k:copy.deepcopy(v) for k,v in before.items() if k not in ('blocks','layout_gap','perimeter_revision')}
    data.update(key='i21',title='大型崩坏能反应堆',name=NAME,candidate_version='闭式三回路联合厂区V1・待审',size=[W,H,D],blocks=blocks,
                block_count=len(blocks),paths=a.paths,ports=a.ports,zones=a.zones,
                description='原位保留I19/I20全部设备，IMV新增闭式散热塔楼、双腔核岛、再生换热和四列透平。')
    data['controller_centering']['summary']='沿用I19原宽191的第96格[95,3,20]朝北；扩建不移动主控。'
    data['integration_revision']['principle']='主控原位；旧16口原位，新8口嵌燃料分类设备、循环泵及一体发电机端壳。'
    data['construction_notes']['world_height_range']=[-60,133]
    data['perimeter_revision']={'south_road_z':[281,285],'clear_strip_z':[274,280],'east_road_x':[321,325],
                                'rear_wall_max_z':273,'old_i20_road_preserved':True,'encloses_all_halls':True}
    geometry={'size_check':require(data),'user_target_xyz':[326,194,286],'components':int(components),
              'paths_checked':len(a.paths),'paths_clear':True,
              'inheritance':{'source':str(BASE),'source_sha256':BASE_SHA,'retained_blocks':len(before['blocks']),
                             'added_blocks':len(blocks)-len(before['blocks']),'removed_blocks':0,'replaced_blocks':0},
              'new_stage_palette':dict(collections.Counter(STATES[int(i)] for i in a.cells[(a.original==AIR)&(a.cells!=AIR)])),
              'ports_old':16,'ports_new':8,'controller_unchanged':data['controller']==[95,3,20]}
    return data,geometry


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True);(OUT/'i21').mkdir(exist_ok=True)
    data,checks=build()
    (OUT/'i21/blueprint.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (LOG/'geometry-preview.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'blocks':data['block_count'],'size':data['size'],'checks':checks},ensure_ascii=False))
