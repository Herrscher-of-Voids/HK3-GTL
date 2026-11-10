# -*- coding: utf-8 -*-
"""I22究极崩坏能反应堆：在I21全厂区之外新增WSV文明级多堆协同设施。

【文件职责】读取I21候选快照，保护HBV/QSV/IMV全部既有方块，在新区域生成WSV环箍堆塔、六室冷凝阵列、燃料轮换厅和六列透平。
【变更记录 #1】2026-10-23 21:03:39（建筑候选V1，不增加模组修订号）
删除：无。新增：四堆隔离外场、WSV环箍屏蔽塔、六室冷凝阵列、长周期燃料轮换厅、六列协同透平厅。
修改：新阶段主体统一采用现存WSV完整机壳；主控继续沿用I19原位[95,3,20]。
用途：表达奇观级持续供能与多机组风险隔离；不注册机器、配方或真实能源能力。

【变更记录 #2】2026-10-23 21:26:26（建筑候选V1修订，不增加模组修订号）
删除：无。新增：两台稳界冷媒蓄能器及回流总管连接，明确南侧格栅回转区的设备用途。
修改：燃料转运管终点改接燃料缓冲箱西端实际壳体[337,8,132]，不再指向箱体内部空气。
用途：补足扩建区的检修与冷媒缓冲功能，并让燃料接口管线落在真实设备方块上；不改变I21既有快照。

【变更记录 #3】2026-10-23 21:35:00（建筑候选V1支撑修订，不增加模组修订号）
删除：无。新增：两台蓄能器下方Y=1的完整钢制承重层。
修改：蓄能器由“Y=0格栅—Y=2设备”改为连续的地面、承重层、设备三段连接。
用途：消除设备悬空一格的实体缺口；不覆盖I21既有方块。
"""
import collections, copy, hashlib, json, math
import numpy as np
from scipy.ndimage import label
from build_i21_imv_cogeneration_v1 import ROOT, AIR, WHITE, STEEL, VESSEL, GLASS, PIPE, GRATE, VENT, PANEL, GEAR, PORT, CORE
from structure_size_baseline import require

OUT=ROOT/'deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023'
LOG=ROOT/'logs/i22-wsv-ultimate-v1-20261023'
BASE=ROOT/'deliveries/I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023/i21/blueprint.json'
BASE_SHA='ddd8e631d7875ecbf387a4a61cbbb3631281162e566b840b7da94ff5aaed06c1'
NAME='i22-wsv-ultimate-isolated-field-v1'; W,H,D=402,250,346
from build_i21_imv_cogeneration_v1 import STATES as OLD_STATES
STATES=OLD_STATES+['hk3gtl:voltage_machine_casing_wsv']; WSV=len(OLD_STATES)

class Site:
 def __init__(self,before):
  self.cells=np.zeros((H,D,W),dtype=np.uint8)
  for b in before['blocks']:
   x,y,z=b['pos'];self.cells[y,z,x]=STATES.index(b['state'])
  self.original=self.cells.copy();self.ports=copy.deepcopy(before['ports']);self.paths=copy.deepcopy(before['paths']);self.zones=copy.deepcopy(before['zones'])
 def box(self,lo,hi,mat,shell=False):
  x0,y0,z0=lo;x1,y1,z1=hi;assert 0<=x0<=x1<W and 0<=y0<=y1<H and 0<=z0<=z1<D,(lo,hi)
  if shell:
   for y in (y0,y1):self.box((x0,y,z0),(x1,y,z1),mat)
   for x in (x0,x1):self.box((x,y0,z0),(x,y1,z1),mat)
   for z in (z0,z1):self.box((x0,y0,z),(x1,y1,z),mat)
   return
  old=self.original[y0:y1+1,z0:z1+1,x0:x1+1];assert not np.any((old!=AIR)&(old!=mat)),('覆盖I21原块',lo,hi,STATES[mat])
  self.cells[y0:y1+1,z0:z1+1,x0:x1+1]=mat
 def ring(self,cx,cz,y,r,t,mat,filled=False):
  rr=math.ceil(r);x0=max(0,cx-rr);x1=min(W-1,cx+rr);z0=max(0,cz-rr);z1=min(D-1,cz+rr);zz,xx=np.ogrid[z0:z1+1,x0:x1+1];s=(xx-cx)**2+(zz-cz)**2;m=s<=r*r
  if not filled:m &= s>=max(0,r-t)**2
  old=self.original[y,z0:z1+1,x0:x1+1];assert not np.any(m&(old!=AIR)&(old!=mat))
  self.cells[y,z0:z1+1,x0:x1+1][m]=mat
 def tube(self,points,mat=PIPE,r=1):
  for a,b in zip(points,points[1:]):
   assert sum(a[i]!=b[i] for i in range(3))<=1
   self.box(tuple(min(a[i],b[i])-r for i in range(3)),tuple(max(a[i],b[i])+r for i in range(3)),mat)
 def hall(self,lo,hi):
  x0,y0,z0=lo;x1,y1,z1=hi;self.box((x0,0,z0),(x1,1,z1),STEEL);self.box(lo,hi,WSV,True)
  for y in (5,y1-4):
   for z in (z0,z1):self.box((x0,y,z),(x1,y,z),WHITE)
  for x in range(x0+5,x1-5,17):
   for z in (z0,z1):self.box((x,10,z),(x+7,min(20,y1-7),z),GLASS)
 def port(self,code,pos,face,purpose):self.box(pos,pos,PORT);self.ports.append({'id':code,'pos':list(pos),'face':face,'purpose':purpose})

def build():
 assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
 before=json.loads(BASE.read_text('utf-8'));a=Site(before)
 # 外围路直接衔接I21旧边界，全部前阶段道路原位保留。
 for lo,hi in [((326,0,0),(401,0,6)),((397,0,0),(401,0,345)),((0,0,286),(5,0,345)),((0,0,341),(401,0,345))]:a.box(lo,hi,STEEL)
 for lo,hi in [((326,0,7),(333,0,340)),((394,0,7),(396,0,340)),((6,0,286),(396,0,294)),((6,0,334),(396,0,340))]:a.box(lo,hi,GRATE)
 # 四腔承压筒处于双层环箍屏蔽壳之内，底座、顶罩及约束环共同组成完整堆塔。
 cx,cz=364,79
 for y in range(3):a.ring(cx,cz,y,31,1,STEEL,True)
 for y in range(3,219):
  a.ring(cx,cz,y,30,3,WSV);a.ring(cx,cz,y,27,2,STEEL)
 for y in (12,48,84,120,156,192,218):
  for yy in (y,y+1):a.ring(cx,cz,yy,32,3,WHITE)
 for angle in range(0,360,45):
  t=math.radians(angle);x=round(cx+29*math.cos(t));z=round(cz+29*math.sin(t));a.box((x-1,3,z-1),(x+1,218,z+1),WSV)
 for y in range(219,243):a.ring(cx,cz,y,max(8,30-(y-219)),3,WSV)
 a.ring(cx,cz,242,8,1,WSV,True);a.box((360,243,75),(368,249,83),WSV,True)
 core_centers=((352,67),(376,67),(352,91),(376,91))
 for q,(x,z) in enumerate(core_centers,1):
  for y in range(6,209):a.ring(x,z,y,9,2,VESSEL)
  for y in (5,209):a.ring(x,z,y,9,1,VESSEL,True)
  a.box((x-1,6,z-1),(x+1,208,z+1),WSV);a.box((x,32,z),(x,32,z),CORE)
  a.tube([(x,16,z),(cx,16,z),(cx,16,cz)],VESSEL,0)
  a.zones.append({'name':'WSV隔离承压腔'+str(q),'pos':[x,209,z]})
 a.box((362,3,77),(366,208,81),WSV)
 # 塔脚南侧供料/强冷却泵房；冷却接口直接落在泵组端壳上。
 a.box((333,0,118),(396,0,171),GRATE);a.hall((335,2,122),(392,34,166))
 for z in (132,155):
  a.box((337,3,z-3),(351,13,z+3),VESSEL,True)
  a.box((374,3,z-3),(392,13,z+3),VESSEL,True)
  a.box((381,14,z-1),(387,17,z+1),GEAR)
  a.box((385,3,z-1),(392,7,z+1),PANEL)
 a.port('C7',(392,3,132),'east','WSV强冷却介质入口（计划）');a.port('C8',(392,3,155),'east','WSV降载热排流出口（计划）')
 a.box((335,2,140),(335,9,146),AIR)
 a.tube([(380,8,132),(380,8,113),(376,8,113),(376,8,100)],PIPE)
 a.tube([(352,18,100),(352,18,155),(380,18,155),(380,13,155)],PIPE)
 a.zones.append({'name':'WSV四腔环箍屏蔽堆塔','pos':[364,249,79]});a.zones.append({'name':'WSV燃料缓冲与强冷却泵房','pos':[364,34,144]})
 # 六室冷凝阵列，三格走廊把各换热室与维护门相接。
 a.hall((335,2,183),(392,47,255))
 for z in (190,201,212,223,234,245):
  a.box((341,2,z-3),(382,5,z+3),STEEL);a.box((343,6,z-3),(379,18,z+3),VESSEL,True);a.box((351,19,z-2),(370,22,z+2),WSV)
  a.tube([(379,12,z),(385,12,z)],PIPE)
 a.tube([(385,12,190),(385,12,245)],PIPE);a.box((335,2,216),(335,9,221),AIR)
 a.tube([(380,18,155),(387,18,155),(387,18,190),(379,18,190)],PIPE)
 a.box((333,0,172),(393,0,182),GRATE);a.box((333,0,256),(393,0,280),GRATE)
 # 256--280 区域不是空白预留：两台稳界冷媒蓄能器占据检修回转区，
 # 以回流总管为唯一接口，避免把大面积格栅做成没有用途的空板。
 for x in (346,365):
  a.box((x-7,1,262),(x+7,1,276),STEEL)
  a.box((x-7,2,262),(x+7,3,276),STEEL)
  a.box((x-6,4,263),(x+6,18,275),VESSEL,True)
  a.box((x-4,19,265),(x+4,22,273),WSV)
  a.tube([(x,22,269),(x,12,269),(390,12,269)],PIPE)
 a.zones.append({'name':'WSV稳界冷媒蓄能与检修回转区','pos':[355,22,269]})
 a.zones.append({'name':'WSV六室冷凝与降载阵列','pos':[364,47,218]})
 # 长周期燃料轮换厅：四组装卸/分类床、连续吊车梁及东端转运接口。
 a.hall((12,2,296),(133,42,333))
 for x in (24,50,76,102):
  a.box((x-7,2,304),(x+8,4,326),STEEL);a.box((x-5,5,307),(x+6,16,323),VESSEL,True);a.box((x-2,17,310),(x+3,20,320),WSV);a.box((x+8,5,312),(x+14,12,320),PANEL)
 for x in (14,130):
  for z in (303,330):a.box((x,2,z),(x+1,27,z+1),WSV)
 for z in (305,330):a.box((14,27,z),(131,28,z+1),STEEL)
 a.box((66,29,305),(68,30,331),WSV);a.box((65,29,315),(69,33,319),GEAR);a.tube([(67,28,317),(67,20,317)],PIPE,0)
 a.box((120,6,316),(133,14,324),VESSEL,True)
 for code,x,purpose in (('F7',24,'WSV高阶燃料棒批量装入（计划）'),('F8',102,'WSV废棒长周期分类交付（计划）')):
  a.box((x,3,296),(x,8,298),PANEL);a.box((x,8,298),(x,8,307),PANEL);a.box((x,6,307),(x,8,307),PANEL);a.port(code,(x,3,296),'north',purpose)
 a.box((36,2,296),(42,9,296),AIR)
 a.zones.append({'name':'WSV长周期燃料轮换厅','pos':[68,42,317]})
 # 六跨穹拱透平厅：六列机组与端壳一体化电能口，保持前侧完整检修通廊。
 a.hall((140,2,296),(394,58,333));a.box((141,58,297),(393,58,332),AIR)
 for z in range(296,334):
  roof=58+round(12*math.sin(math.pi*(z-296)/37));a.box((140,roof-1,z),(394,roof,z),WSV)
  for x in (140,394):a.box((x,58,z),(x,roof,z),WSV)
  if 309<=z<=321:
   for x in (157,197,237,277,317,357):a.box((x,roof,z),(x+7,roof,z),GLASS)
 for x in (140,181,222,263,304,345,392):
  for z in (296,332):a.box((x,2,z),(x+2,58,z+1),WSV)
  for z in range(297,333):
   roof=58+round(12*math.sin(math.pi*(z-296)/37));a.box((x,roof-3,z),(x+2,roof-2,z),WHITE)
 for n,x in enumerate((150,190,230,270,310,350),13):
  a.box((x-2,2,303),(x+38,4,327),STEEL);a.box((x,5,305),(x+27,17,323),VESSEL,True);a.box((x+5,18,308),(x+22,21,320),WSV);a.box((x+28,5,309),(x+35,14,321),GEAR,True);a.box((x+32,2,320),(x+38,12,333),VESSEL,True);a.box((x+34,3,320),(x+36,7,332),PANEL)
  a.port('E'+str(n),(x+35,3,333),'south','WSV第'+str(n-12)+'列协同电能输出（计划）');a.box((x+5,2,296),(x+11,9,297),AIR)
 a.zones.append({'name':'WSV六列协同透平厅','pos':[270,70,317]})
 # 主蒸汽、回流和燃料转运管分别接实际机壳；跨路段有支撑且低位通道保持净空。
 assert a.cells[40,100,376]==VESSEL
 a.tube([(376,40,100),(376,40,278),(362,40,278),(362,40,317),(362,21,317)],PIPE)
 a.tube([(162,24,317),(362,24,317)],PIPE)
 for x in (162,202,242,282,322,362):a.tube([(x,24,317),(x,21,317)],PIPE)
 a.tube([(385,12,245),(390,12,245),(390,12,317),(385,12,317)],PIPE)
 for x,z in ((376,174),(376,263),(362,280)):
  for sx in (x-3,x+3):a.box((sx,0,z),(sx+1,37,z+1),WSV)
  a.box((x-3,38,z),(x+4,38,z+1),STEEL)
 assert a.cells[8,132,337]==VESSEL
 a.tube([(133,8,320),(137,8,320),(137,8,290),(334,8,290),(334,8,132),(337,8,132)],VESSEL,0)
 for x,z in ((137,320),(334,174),(334,263)):
  a.box((x,0,z),(x,7,z),WSV)
 for x in (175,225,275,325):
  a.box((x,0,295),(x,6,295),WSV);a.box((x,7,290),(x,7,295),STEEL)
 a.paths += [{'name':'WSV西侧新厂纵道','min':[326,1,7],'max':[332,4,285]}, {'name':'WSV东侧闭合外围路','min':[397,1,0],'max':[401,4,345]},
  {'name':'WSV南侧八格装卸净空','min':[6,1,286],'max':[396,4,293]}, {'name':'WSV后墙七格维护带','min':[6,1,334],'max':[396,4,340]},
  {'name':'WSV南侧完整外围路','min':[0,1,341],'max':[401,4,345]}, {'name':'WSV轮换厅北侧通道','min':[18,3,299],'max':[127,6,302]},
  {'name':'WSV透平厅前维护通廊','min':[145,3,298],'max':[390,6,302]}]
 for p in a.paths:
  x0,y0,z0=p['min'];x1,y1,z1=p['max'];assert np.all(a.cells[y0:y1+1,z0:z1+1,x0:x1+1]==AIR),('通道堵塞',p)
 frozen=a.original!=AIR;assert np.array_equal(a.cells[frozen],a.original[frozen]);_,components=label(a.cells!=AIR);assert components==1,components
 yy,zz,xx=np.nonzero(a.cells);blocks=[{'pos':[int(x),int(y),int(z)],'state':STATES[int(a.cells[y,z,x])]} for y,z,x in zip(yy,zz,xx)]
 data={k:copy.deepcopy(v) for k,v in before.items() if k not in ('blocks','perimeter_revision')};data.update(key='i22',title='究极崩坏能反应堆',name=NAME,candidate_version='四堆隔离外场候选V1・待审',size=[W,H,D],blocks=blocks,block_count=len(blocks),paths=a.paths,ports=a.ports,zones=a.zones,description='保留I19/I20/I21三阶段全厂，WSV新增四堆隔离外场、六室冷凝阵列、燃料轮换厅与六列透平。')
 data['controller_centering']['summary']='沿用I19原宽191的第96格[95,3,20]朝北；I22扩建不移动主控。';data['integration_revision']['principle']='主控原位；旧24口原位，新10口嵌燃料轮换设备、循环泵组与六列透平端壳。';data['construction_notes']['world_height_range']=[-60,189]
 data['perimeter_revision']={'south_road_z':[341,345],'clear_strip_z':[334,340],'east_road_x':[397,401],'rear_wall_max_z':333,'old_i21_road_preserved':True,'encloses_all_halls':True}
 size=require(data);geometry={'size_check':size,'user_target_xyz':[402,250,346],'components':int(components),'paths_checked':len(a.paths),'paths_clear':True,'inheritance':{'source':str(BASE),'source_sha256':BASE_SHA,'retained_blocks':len(before['blocks']),'added_blocks':len(blocks)-len(before['blocks']),'removed_blocks':0,'replaced_blocks':0},'new_stage_palette':dict(collections.Counter(STATES[int(i)] for i in a.cells[(a.original==AIR)&(a.cells!=AIR)])),'ports_old':24,'ports_new':10,'controller_unchanged':data['controller']==[95,3,20]}
 return data,geometry

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True);(OUT/'i22').mkdir(exist_ok=True);d,g=build();(OUT/'i22/blueprint.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8');(LOG/'geometry-preview.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'blocks':d['block_count'],'size':d['size'],'checks':g},ensure_ascii=False))
