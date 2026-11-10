# -*- coding: utf-8 -*-
"""69座建筑预览的完整方块构件与独立布局。
变更#1 2026-09-28 03:21:36：新增分区记录、可见工艺构件及规划通道；仅写候选，不改生产Pattern。
尺寸单位为方块，输入宽高深；主控朝-Z，分区坐标随实际几何记录。
"""
import math,json,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P={
 'floor':'gtceu:clean_machine_casing','frame':'gtceu:clean_machine_casing',
 'wall':'gtlcore:iridium_casing','rib':'gtlcore:lafium_mechanical_casing',
 'glass':'gtlcore:hsss_reinforced_borosilicate_glass','energyglass':'gtlcore:rhenium_reinforced_energy_glass',
 'pipe':'gtceu:tungstensteel_pipe_casing','gear':'gtceu:tungstensteel_gearbox',
 'vent':'gtceu:computer_heat_vent','grate':'gtceu:assembly_line_grating',
 'power':'gtceu:high_power_casing','panel':'gtceu:advanced_computer_casing',
 'compute':'gtlcore:super_computation_component[active=false]','cool':'gtlcore:super_cooler_component[active=false]',
 'filter':'gtlcore:law_filter_casing','process':'gtlcore:process_machine_casing',
 'chemical':'gtceu:corrosion_proof_casing','arm':'gtlcore:manipulator',
 'precision':'gtlcore:multi_functional_casing','assembly':'gtlcore:advanced_assembly_line_unit[active=false]',
 'field':'gtlcore:graviton_field_constraint_casing','injection':'gtlcore:dimension_injection_casing',
 'connection':'gtlcore:dimension_connection_casing','echo':'gtlcore:echo_casing',
 'star':'gtlcore:stellar_containment_casing','cold':'gtlcore:cold_ice_casing',
 'coil':'kubejs:starmetal_coil_block[active=false]','hotcoil':'kubejs:titansteel_coil_block[active=false]',
 'eternity':'kubejs:eternity_coil_block[active=false]','alloycoil':'kubejs:naquadriatictaranium_coil_block[active=false]',
 'controller':'minecraft:diamond_block','port':'minecraft:diamond_ore'}

class Build:
 def __init__(self,brief):
  self.brief=brief;w,d,h=brief['minimum_wdh'];self.w=w;self.d=d;self.h=h;self.cx=w//2;self.cz=d//2
  self.b={};self.zones=[];self.links=[];self.paths=[];self.roles=collections.defaultdict(set)
 def set(self,x,y,z,m):
  x,y,z=round(x),round(y),round(z)
  if not (0<=x<self.w and 0<=y<self.h and 0<=z<self.d):raise ValueError((self.brief['id'],x,y,z,m))
  self.b[(x,y,z)]=P.get(m,m);self.roles[P.get(m,m)].add(m)
 def box(self,a,b,m,shell=False):
  a=tuple(map(round,a));b=tuple(map(round,b))
  if any(b[i]<a[i] for i in range(3)):return
  if shell:
   for y in (a[1],b[1]):self.box((a[0],y,a[2]),(b[0],y,b[2]),m)
   for x in (a[0],b[0]):self.box((x,a[1],a[2]),(x,b[1],b[2]),m)
   for z in (a[2],b[2]):self.box((a[0],a[1],z),(b[0],b[1],z),m)
  else:
   for x in range(a[0],b[0]+1):
    for y in range(a[1],b[1]+1):
     for z in range(a[2],b[2]+1):self.set(x,y,z,m)
 def line(self,a,b,m,width=1):
  a=tuple(map(round,a));b=tuple(map(round,b));n=max(abs(b[i]-a[i]) for i in range(3));old=a
  for j in range(n+1):
   p=tuple(round(a[i]+(b[i]-a[i])*j/max(n,1)) for i in range(3));t=list(old)
   for axis in range(3):
    while t[axis]!=p[axis]:t[axis]+=1 if t[axis]<p[axis] else -1;self.set(*t,m)
   self.set(*p,m)
   if width>1:
    r=(width-1)//2;self.box((max(0,p[0]-r),max(0,p[1]-r),max(0,p[2]-r)),(min(self.w-1,p[0]+r),min(self.h-1,p[1]+r),min(self.d-1,p[2]+r)),m)
   old=p
 def ring(self,c,rx,rz,m,width=1):
  for rr in range(width):
   n=max(64,round(max(rx,rz)*8));points=[(c[0]+(rx-rr)*math.cos(i*math.tau/n),c[1],c[2]+(rz-rr)*math.sin(i*math.tau/n)) for i in range(n+1)]
   for a,b in zip(points,points[1:]):self.line(a,b,m)
 def platform(self,a,b):
  self.box((max(0,a[0]-1),0,max(0,a[2]-1)),(min(self.w-1,b[0]+1),0,min(self.d-1,b[2]+1)),'floor')
 def feet(self,a,b):
  for x in (a[0],b[0]):
   sx=x if abs(x-self.cx)>1 else self.cx+(3 if x>=self.cx else -3)
   for z in (a[2],b[2]):
    self.box((sx,1,z),(sx,max(1,a[1]),z),'rib')
    if sx!=x:self.line((sx,a[1],z),(x,a[1],z),'rib')
 def module(self,kind,rect,top,label,role='process',bottom=None):
  # 归一化坐标只用于独立布局描述；展开后逐格生成，不缩放材质。
  x0=min(self.w-4,max(1,round(rect[0]*(self.w-1))));x1=min(self.w-2,round(rect[2]*(self.w-1)))
  z0=min(self.d-4,max(6,round(6+rect[1]*(self.d-8))));z1=min(self.d-2,round(6+rect[3]*(self.d-8)))
  x1=max(x0+2,x1);z1=max(z0+2,z1)
  y0=bottom if bottom is not None else (6 if x0<=self.cx+1 and x1>=self.cx-1 else 1)
  y1=max(y0+3,min(self.h-1,round(top*(self.h-1))))
  a=(x0,y0,z0);b=(x1,y1,z1);self.platform(a,b);self.feet(a,b)
  before=set(self.roles);cx=(x0+x1)//2;cz=(z0+z1)//2
  if kind in ('tank','tower','reactor'):
   rx=max(1,(x1-x0)//2);rz=max(1,(z1-z0)//2)
   for y in range(y0,y1+1):
    mat='rib' if y in (y0,y1) or (y-y0)%max(4,(y1-y0)//4)==0 else role
    self.ring((cx,y,cz),rx,rz,mat,2 if rx>8 else 1)
   for y in (y0,y1):
    for x in range(x0,x1+1):
     for z in range(z0,z1+1):
      if ((x-cx)/rx)**2+((z-cz)/rz)**2<=1:self.set(x,y,z,'grate' if y==y1 else 'power')
   self.box((cx,max(y0,y0+2),z0),(cx,y1-2,z0),'energyglass' if kind=='reactor' else 'glass')
   for x in (x0,x1):self.box((x,y0,cz),(x,y1,cz),'pipe')
   if kind=='reactor':
    for y in range(y0+2,y1-1,3):self.ring((cx,y,cz),max(1,rx-2),max(1,rz-2),'hotcoil')
  elif kind in ('hall','lab','archive','cooler'):
   self.box(a,b,role,True)
   # 窗、承重肋与进深一致；门洞在生成墙面前预留，低位中央通道不穿主体。
   if x1-x0>5 and y1-y0>5:
    self.box((x0+2,y0+2,z0),(x1-2,min(y1-2,y0+5),z0),'glass')
    self.box((x0+2,y0+2,z1),(x1-2,min(y1-2,y0+5),z1),'glass')
   for x in range(x0,x1+1,max(4,(x1-x0)//4)):
    for z in (z0,z1):self.box((x,y0,z),(x,y1,z),'frame')
    self.box((x,y1,z0),(x,y1,z1),'rib')
   for z in range(z0+2,z1-1,max(4,(z1-z0)//5)):
    self.box((x0+1,y1,z),(x1-1,y1,z),'vent' if kind=='cooler' else 'grate')
   if x1-x0>=5 and z1-z0>=5:
    self.box((x0+2,y0+1,z0+2),(x0+2,min(y0+3,y1-1),z1-2),'compute' if kind=='archive' else 'precision')
    self.box((x1-2,y0+1,z0+2),(x1-2,min(y0+3,y1-1),z1-2),'cool' if kind=='cooler' else 'panel')
   if kind=='lab':
    self.box((cx,y0+1,cz),(cx,min(y1-1,y0+3),cz),'arm');self.set(cx,y1,cz,'filter')
  elif kind in ('bed','rail','dock'):
   deck=y0+max(1,(y1-y0)//5);self.box(a,(x1,deck,z1),'wall',True)
   for x in (x0+1,x1-1):self.box((x,deck+1,z0),(x,deck+1,z1),'gear')
   for z in range(z0+2,z1,max(4,(z1-z0)//4)):
    self.box((x0,deck,z),(x0,y1,z),'power');self.box((x1,deck,z),(x1,y1,z),'power')
    self.box((x0,y1,z),(x1,y1,z),'assembly' if kind=='bed' else 'connection')
    self.box((cx,deck+1,z),(cx,max(deck+1,y1-1),z),'arm' if kind=='bed' else 'field')
  elif kind=='gate':
   for x in (x0,x1):self.box((x,y0,z0),(x,y1,z1),'field',True)
   self.box((x0,y1-1,z0),(x1,y1,z1),'connection',True)
   self.box((x0+1,y0,z0),(x0+1,y1-2,z1),'injection');self.box((x1-1,y0,z0),(x1-1,y1-2,z1),'injection')
  elif kind=='fin':
   self.box(a,(x1,y0+1,z1),'power')
   for z in range(z0,z1+1,3):self.box((x0,y0+2,z),(x1,y1,z),'cool',True)
   self.box((cx,y0+1,z0),(cx,y1,z1),'pipe')
  elif kind=='dish':
   self.box((cx,y0,cz),(cx,y1,cz),'power')
   surface={}
   for x in range(x0,x1+1):
    for z in range(z0,z1+1):
     nx=(x-cx)/max(1,(x1-x0)/2);nz=(z-cz)/max(1,(z1-z0)/2);r=nx*nx+nz*nz
     if r<=1:
      yy=round(y1-(1-r)*min(8,(y1-y0)/3));surface[(x,z)]=(yy,'echo' if r<.7 else 'frame');self.set(x,yy,z,surface[(x,z)][1])
   for (x,z),(yy,mat) in surface.items():
    for q in ((x-1,z),(x,z-1)):
     if q in surface:
      qy=surface[q][0];self.box((x,min(yy,qy),z),(x,max(yy,qy),z),mat)
   self.box((cx,y0,cz),(cx,y1,cz),'injection')
  elif kind=='core':
   self.box(a,b,'energyglass',True)
   self.box((cx,y0,cz),(cx,y1,cz),role)
   for y in (y0,y1,(y0+y1)//2):self.box((x0,y,z0),(x1,y,z0),'rib');self.box((x0,y,z1),(x1,y,z1),'rib')
  else:raise ValueError(kind)
  # 外侧服务带：接线箱、过滤/冷却接口、传动检查口对应真实设备维护面。
  # 不沿中央通道放脚；小设备采用单格面板，大设备用成组柜列。
  sx=x0 if cx<self.cx else x1
  if abs(sx-self.cx)<=1:sx=x0 if abs(x0-self.cx)>1 else x1
  service=['panel','filter','gear','vent','precision','cool','power','compute']
  slots=min(8,max(3,z1-z0-1));ys=min(y1-1,y0+2)
  for j in range(slots):
   zz=z0+1+round(j*max(0,z1-z0-2)/max(1,slots-1))
   self.set(sx,ys,zz,service[j])
   if y1-y0>8:self.set(sx,ys+1,zz,service[j])
  self.zones.append({'name':label,'kind':kind,'min':list(a),'max':list(b),'pos':[cx,y1,cz],'role':role,'service_face':'西侧' if sx==x0 else '东侧','description':{'tank':'分段罐体、观察窗、外接立管与顶端格栅','tower':'多段处理柱，竖直管路与分层约束','reactor':'内线圈与双层约束罐，外围设备单独布置','hall':'完整围护、周期承重肋与屋顶设备带','lab':'独立仪器台、维护侧柜与观察窗','archive':'记录柜墙与上层资料干线','cooler':'冷却柜组、散热屋顶与管汇','bed':'加工床、门式操作梁及端部驱动','rail':'双侧导向床和跨接约束架','dock':'装置整备台与分段调度架','gate':'厚约束门柱与横梁，中央场区留空','fin':'重复散热片组与贯穿管汇','dish':'有曲率的观测面与馈源支撑','core':'透明屏蔽室与内部核心柱'}[kind]+'；外侧接线、过滤、传动和散热维护带'})
  return a,b
 def connect(self,i,j,role='pipe'):
  a=self.zones[i];b=self.zones[j];p=[a['pos'][0],max(6,min(a['max'][1],b['max'][1])-1),a['pos'][2]];q=[b['pos'][0],p[1],b['pos'][2]]
  self.line(p,(q[0],p[1],p[2]),role);self.line((q[0],p[1],p[2]),q,role)
  self.links.append({'from':a['name'],'to':b['name'],'material':P[role],'route':[p,[q[0],p[1],p[2]],q]})
 def dome(self,cx,cz,r,ybase,top,label):
  # 分瓣椭球壳，玻璃与承重脊有明确重复节奏；实际壳顶达到指定高度。
  ry=top-ybase;surface={}
  for x in range(cx-r,cx+r+1):
   for z in range(cz-r,cz+r+1):
    rr=((x-cx)**2+(z-cz)**2)/(r*r)
    if rr<=1:
     y=round(ybase+ry*math.sqrt(1-rr));theta=math.atan2(z-cz,x-cx)
     rib=abs(math.sin(theta*8))<.09 or (x-cx)**2+(z-cz)**2<9
     self.set(x,y,z,'rib' if rib else 'glass')
     surface[(x,z)]=(y,'rib' if rib else 'glass')
     if rib and y>ybase:self.set(x,y-1,z,'frame')
  # 相邻采样柱补齐阶梯立面，避免曲率陡处仅斜向接触而出现漏壳。
  for (x,z),(y,mat) in surface.items():
   for q in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
    if q in surface:
     qy=surface[q][0]
     if qy<y:self.box((x,qy,z),(x,y,z),mat)
  self.ring((cx,ybase,cz),r,r,'frame',2)
  for i in range(16):
   x=round(cx+r*math.cos(i*math.tau/16));z=round(cz+r*math.sin(i*math.tau/16))
   if abs(x-self.cx)<=1:x+=3 if x>=self.cx else -3
   self.box((x,1,z),(x,ybase,z),'field')
  self.zones.append({'name':label,'kind':'dome','min':[cx-r,ybase,cz-r],'max':[cx+r,top,cz+r],'pos':[cx,top,cz],'role':'glass','description':'十六分瓣完整穹顶壳，玻璃扇区、双层承重脊及独立落地场柱'})
 def finish(self):
  # 统一白色基础，紧凑机器为整齐平台；巨构仅铺设备基础、维护环与连接道。
  if max(self.w,self.d)<=140:self.box((0,0,0),(self.w-1,0,self.d-1),'floor')
  else:
   for x0,x1 in ((0,3),(self.w-4,self.w-1),(self.cx-3,self.cx+3)):self.box((x0,0,0),(x1,0,self.d-1),'floor')
   for z0,z1 in ((0,5),(self.d-5,self.d-1),(self.cz-3,self.cz+3)):self.box((0,0,z0),(self.w-1,0,z1),'floor')
  c=self.cx
  self.box((c-5,1,1),(c+5,4,1),'frame');ports=[]
  for y in (2,3):
   for x in range(c-4,c+5):
    if (x,y)==(c,2):continue
    self.set(x,y,1,'port');ports.append({'id':str(len(ports)+1),'pos':[x,y,1],'face':'north','purpose':'接口候选；正式能力与最低数量须按配方确认，可用既定接口机械方块填充'})
  self.set(c,2,1,'controller')
  path={'name':'中央低位检修主道','min':[c-1,1,4],'max':[c+1,4,self.d-2]};self.paths.append(path)
  collisions=[p for p in self.b if c-1<=p[0]<=c+1 and 1<=p[1]<=4 and 4<=p[2]<=self.d-2]
  if collisions:raise ValueError(('通道需重新规划，不允许后切',self.brief['id'],collisions[:4]))
  actual=[max(p[i] for p in self.b)-min(p[i] for p in self.b)+1 for i in range(3)]
  assert actual==[self.w,self.h,self.d],(self.brief['id'],actual,[self.w,self.h,self.d])
  return {'key':self.brief['id'].lower(),'name':'hk3gtl-'+self.brief['id'].lower()+'-redesign-01','title':self.brief['title'],'size':[self.w,self.h,self.d],'controller':[c,2,1],'ports':ports,'paths':self.paths,'zones':self.zones,'links':self.links,'description':self.brief['form']+'；'+self.brief['flow'],'brief':self.brief,'role_materials':{k:sorted(v) for k,v in self.roles.items()},'blocks':[{'pos':list(p),'state':s} for p,s in sorted(self.b.items())]}

# 独立工业布局：种类、归一化矩形、相对高度、功能材质。对应分区名称从逐台草案读取。
INDUSTRIAL={
'I01-1':[('tower',(.38,.2,.62,.72),1,'field'),('tank',(.04,.42,.29,.83),.36,'chemical'),('fin',(.73,.30,.94,.80),.4,'cool')],
'I01-2':[('core',(.31,.3,.69,.69),.7,'alloycoil'),('fin',(.02,.08,.24,.8),1,'cool'),('fin',(.76,.08,.98,.8),.88,'cool'),('tank',(.32,.77,.68,.98),.38,'chemical')],
'I01-3':[('tower',(.1,.12,.35,.51),1,'chemical'),('tower',(.65,.42,.90,.83),.85,'chemical'),('tank',(.08,.65,.31,.96),.4,'process'),('hall',(.59,.02,.93,.24),.3,'panel')],
'I01-4':[('core',(.34,.32,.66,.65),1,'injection'),('gate',(.03,.09,.97,.14),.65,'field'),('gate',(.03,.86,.97,.91),.65,'field'),('fin',(.02,.28,.23,.72),.35,'cool'),('hall',(.78,.25,.97,.72),.4,'power')],
'I02':[('lab',(.06,.05,.4,.38),.48,'precision'),('rail',(.13,.45,.87,.67),.8,'echo'),('tower',(.66,.05,.92,.35),1,'panel'),('cooler',(.12,.76,.88,.97),.35,'cool')],
'I03':[('tank',(.08,.13,.42,.62),1,'process'),('tank',(.60,.35,.95,.83),.82,'chemical'),('bed',(.07,.7,.38,.96),.30,'filter'),('hall',(.62,.02,.94,.24),.35,'panel')],
'I04':[('tower',(.32,.2,.68,.8),1,'chemical'),('fin',(.04,.2,.21,.83),.55,'cool'),('fin',(.79,.2,.96,.83),.65,'cool'),('tank',(.3,.85,.7,.99),.32,'process')],
'I05':[('tower',(.58,.45,.93,.90),1,'chemical'),('tank',(.06,.13,.38,.52),.66,'process'),('bed',(.05,.63,.36,.92),.32,'filter'),('cooler',(.63,.04,.95,.28),.35,'cool')],
'I06':[('tank',(.05,.06,.30,.29),.48,'chemical'),('tank',(.05,.43,.30,.66),.55,'chemical'),('tank',(.54,.22,.94,.72),1,'process'),('tank',(.08,.76,.34,.97),.42,'chemical')],
'I07':[('lab',(.04,.06,.39,.45),.65,'precision'),('lab',(.62,.5,.96,.95),.70,'precision'),('rail',(.16,.48,.86,.65),.5,'echo'),('tower',(.70,.03,.93,.28),1,'panel')],
'I08':[('reactor',(.22,.21,.77,.78),1,'field'),('hall',(.02,.01,.28,.2),.35,'precision'),('fin',(.79,.25,.98,.9),.58,'cool'),('lab',(.04,.8,.36,.98),.32,'panel')],
'I09':[('tank',(.03,.1,.28,.40),.55,'chemical'),('tank',(.04,.6,.29,.91),.55,'chemical'),('tank',(.52,.2,.94,.77),1,'process'),('bed',(.6,.82,.95,.97),.32,'filter')],
'I10':[('hall',(.03,.12,.34,.9),.58,'precision'),('tower',(.7,.23,.95,.65),1,'chemical'),('bed',(.40,.14,.6,.82),.4,'assembly'),('tank',(.72,.77,.95,.97),.36,'filter')],
'I11':[('bed',(.05,.08,.36,.9),.62,'assembly'),('bed',(.65,.08,.95,.9),.7,'assembly'),('gate',(.08,.72,.92,.86),1,'panel'),('hall',(.38,.10,.61,.33),.35,'precision')],
'I12':[('lab',(.04,.08,.37,.38),.58,'precision'),('lab',(.63,.08,.96,.38),.65,'precision'),('lab',(.04,.60,.37,.94),.74,'precision'),('archive',(.64,.59,.97,.94),1,'compute')],
'I13':[('rail',(.3,.04,.7,.93),1,'chemical'),('tank',(.03,.18,.24,.51),.45,'chemical'),('tank',(.76,.50,.97,.82),.45,'chemical'),('fin',(.03,.59,.24,.94),.35,'cool')],
'I14':[('bed',(.27,.26,.74,.92),1,'assembly'),('reactor',(.02,.04,.26,.37),.73,'hotcoil'),('hall',(.78,.44,.97,.90),.38,'process'),('tank',(.71,.03,.95,.27),.44,'chemical')],
'I15':[('hall',(.29,.05,.71,.93),.67,'process'),('fin',(.03,.2,.21,.6),1,'cool'),('fin',(.79,.45,.97,.9),.70,'cool'),('tank',(.05,.72,.23,.96),.4,'chemical')],
'I16':[('bed',(.04,.05,.36,.82),.62,'assembly'),('bed',(.64,.18,.96,.94),.7,'precision'),('tower',(.37,.76,.61,.97),1,'panel'),('hall',(.4,.06,.6,.32),.3,'process')],
'I17':[('tower',(.05,.12,.3,.63),1,'chemical'),('tower',(.66,.37,.92,.88),.85,'process'),('tank',(.06,.7,.35,.96),.35,'chemical'),('tank',(.61,.04,.95,.28),.35,'chemical')],
'I18':[('hall',(.25,.03,.74,.96),.7,'precision'),('lab',(.02,.25,.2,.68),1,'panel'),('fin',(.81,.17,.97,.70),.42,'cool')],
'I19':[('reactor',(.16,.21,.62,.81),1,'star'),('fin',(.72,.20,.97,.84),.58,'cool'),('hall',(.04,.02,.39,.16),.3,'panel')],
'I20':[('reactor',(.3,.22,.7,.75),1,'star'),('fin',(.02,.18,.22,.85),.7,'cool'),('fin',(.78,.18,.98,.85),.7,'cool'),('hall',(.27,.83,.72,.98),.3,'power')],
'I21':[('reactor',(.3,.3,.7,.71),1,'star'),('tower',(.04,.05,.23,.29),.60,'chemical'),('tower',(.77,.05,.96,.29),.60,'chemical'),('tower',(.04,.76,.23,.97),.68,'chemical'),('tower',(.77,.76,.96,.97),.68,'chemical')],
'I22':[('reactor',(.32,.29,.68,.73),1,'star'),('fin',(.02,.15,.23,.56),.5,'cool'),('fin',(.78,.38,.98,.82),.6,'cool'),('hall',(.05,.73,.29,.98),.35,'power'),('hall',(.71,.03,.95,.26),.4,'panel')],
'I23':[('core',(.32,.3,.68,.7),1,'hotcoil'),('fin',(.03,.04,.26,.43),.58,'cool'),('fin',(.75,.56,.97,.95),.7,'cool'),('tank',(.03,.64,.24,.91),.35,'chemical')],
'I24':[('dish',(.04,.04,.35,.34),1,'echo'),('dish',(.64,.66,.96,.97),.9,'echo'),('archive',(.05,.61,.31,.94),.4,'compute'),('hall',(.66,.08,.96,.34),.32,'power')],
'I25':[('core',(.32,.25,.68,.7),1,'connection'),('archive',(.04,.07,.27,.93),.57,'compute'),('archive',(.75,.15,.97,.86),.66,'compute')],
'I26':[('dock',(.04,.04,.39,.46),.40,'assembly'),('dock',(.61,.53,.96,.94),.5,'precision'),('tower',(.69,.05,.94,.34),1,'panel'),('hall',(.03,.63,.34,.95),.34,'process')],
'I27':[('gate',(.12,.25,.88,.40),1,'field'),('gate',(.2,.60,.8,.72),.8,'connection'),('hall',(.02,.45,.10,.85),.28,'power'),('hall',(.90,.06,.98,.43),.34,'panel')],
'I28':[('core',(.31,.2,.71,.61),1,'field'),('rail',(.04,.54,.25,.96),.5,'process'),('rail',(.77,.56,.97,.96),.5,'power'),('hall',(.04,.06,.28,.34),.35,'panel')],
'I29':[('core',(.32,.24,.68,.72),1,'eternity'),('archive',(.04,.10,.27,.47),.6,'compute'),('archive',(.73,.55,.96,.92),.6,'compute'),('hall',(.04,.62,.27,.94),.45,'precision')],
'I30':[('rail',(.04,.13,.28,.91),.88,'field'),('rail',(.73,.13,.97,.91),1,'field'),('core',(.34,.31,.66,.76),.65,'connection'),('hall',(.32,.02,.69,.19),.32,'panel')],
'I31':[('rail',(.07,.08,.37,.73),.65,'process'),('rail',(.64,.08,.94,.73),.72,'precision'),('archive',(.1,.81,.9,.98),1,'panel')],
'I32':[('lab',(.05,.05,.38,.45),.5,'precision'),('lab',(.62,.05,.95,.45),.58,'echo'),('archive',(.16,.61,.84,.96),1,'compute')],
'I33':[('bed',(.29,.06,.71,.95),.78,'assembly'),('lab',(.02,.40,.23,.88),.5,'precision'),('lab',(.77,.14,.97,.55),1,'field')],
'I34':[('dish',(.03,.03,.29,.36),.8,'echo'),('dish',(.69,.61,.96,.95),.7,'echo'),('tower',(.36,.35,.63,.67),1,'panel'),('archive',(.03,.67,.29,.96),.4,'compute')],
'I35':[('gate',(.05,.08,.95,.18),.72,'field'),('gate',(.12,.78,.88,.89),.85,'field'),('core',(.34,.32,.66,.66),1,'injection'),('hall',(.02,.38,.23,.68),.3,'power')],
'I36':[('tower',(.35,.22,.65,.76),1,'field'),('gate',(.12,.40,.88,.48),.68,'field'),('fin',(.03,.15,.22,.83),.36,'cool'),('hall',(.77,.2,.96,.8),.3,'panel')],
'I37':[('bed',(.03,.08,.38,.92),.62,'precision'),('bed',(.63,.08,.98,.92),.7,'field'),('gate',(.16,.44,.84,.53),1,'echo'),('hall',(.41,.76,.59,.96),.4,'panel')],
'I38':[('tower',(.35,.29,.65,.74),1,'power'),('rail',(.03,.18,.26,.87),.5,'hotcoil'),('rail',(.74,.18,.97,.87),.5,'alloycoil'),('fin',(.31,.82,.70,.98),.35,'cool')],
'I39':[('tower',(.05,.12,.32,.40),1,'injection'),('tower',(.69,.60,.95,.91),.87,'connection'),('dock',(.60,.02,.95,.45),.35,'assembly'),('hall',(.04,.60,.36,.97),.45,'precision')],
'I40':[('bed',(.03,.05,.36,.43),.65,'assembly'),('reactor',(.65,.07,.96,.4),1,'hotcoil'),('bed',(.04,.62,.35,.96),.7,'field'),('lab',(.64,.6,.96,.97),.75,'precision')],
'I41':[('archive',(.03,.12,.32,.93),.6,'wall'),('archive',(.67,.12,.97,.93),.68,'wall'),('hall',(.37,.23,.63,.67),1,'panel')],
'I42':[('bed',(.04,.06,.39,.94),.65,'assembly'),('bed',(.61,.05,.96,.94),.75,'precision'),('gate',(.08,.68,.92,.79),1,'power')],
'I43':[('lab',(.03,.08,.31,.50),.65,'precision'),('lab',(.69,.08,.97,.5),.7,'field'),('lab',(.03,.64,.31,.98),.5,'process'),('archive',(.52,.62,.95,.97),1,'compute')],
'I44':[('tower',(.38,.22,.62,.78),1,'injection'),('tower',(.06,.10,.26,.34),.45,'field'),('tower',(.73,.65,.93,.92),.55,'field'),('archive',(.07,.69,.3,.94),.3,'compute')],
'I45':[('hall',(.28,.06,.71,.93),.73,'wall'),('core',(.30,.03,.69,.16),1,'panel'),('rail',(.04,.19,.19,.86),.25,'connection'),('reactor',(.76,.63,.95,.91),.65,'power')]
}

def industrial(brief):
 a=Build(brief);specs=INDUSTRIAL[brief['id']]
 for i,(kind,rect,h,role) in enumerate(specs):a.module(kind,rect,h,brief['zones'][i%len(brief['zones'])],role)
 for i in range(1,len(a.zones)):a.connect(i-1,i,'connection' if brief['family'] in ('space','research') else 'pipe')
 # 剩余工艺分区用实际端部设备说明，避免文字分区无任何对应。
 for label in brief['zones'][len(specs):]:a.zones[-1]['description']+='；包含'+label
 return a.finish()

def research(brief):
 a=Build(brief);n=int(brief['id'][1:]);count=2**(n-1)
 if n==1:
  a.module('lab',(.06,.08,.4,.77),.65,'独立实验工作位','precision');a.module('archive',(.64,.20,.94,.94),1,'记录与计算壁','compute');a.connect(0,1,'connection')
 else:
  rows=count//2 if n<5 else 4
  for i in range(count):
   side=i%2;row=(i//2)%rows;level=1 if n==4 and i>=4 else 0
   if n==4:row=(i//2)%2;rows=2
   if n==5:
    side=i%4;row=i//4;x0=.04+side*.245;x1=x0+.18
    if side==1:x1=.45
    if side==2:x0=.55
    z0=.10+row*.205;z1=z0+.155;top=.26+(.06 if row%2 else 0);bottom=6
   else:
    x0=.04 if side==0 else .64;x1=.36 if side==0 else .96
    z0=.10+row*.74/rows;z1=z0+.58/rows;top=(.42 if n<4 else .40+level*.29);bottom=1 if not level else round(a.h*.44)
   a.module('lab',(x0,z0,x1,z1),top,'实验工作位'+str(i+1),'precision' if i%2==0 else 'process',bottom)
  a.module('archive',(.35,.87,.65,.98),.7 if n==5 else 1,'共享资料与计算中枢','compute',6)
  for i in range(count):a.connect(i,count,'connection')
  if n==5:a.dome(a.cx,round(a.d*.53),min(a.w//2-5,round(a.d*.43)),round(a.h*.37),a.h-1,'十六分瓣资料穹顶')
  else:
   for side in (.02,.89):a.module('fin',(side,.42,side+.09,.79),.55,'独立冷却庭','cool')
 return a.finish()

def wonder(brief):
 a=Build(brief);n=int(brief['id'][1:]);labels=brief['zones']
 def mod(kind,rect,h,label,role):return a.module(kind,rect,h,label,role)
 if n in (1,3,5,14):
  # 星庭、双锚环、流场及轮回双核心各有独立空间组织。
  if n==1:
   mod('core',(.42,.38,.58,.61),1,labels[1],'eternity')
   for i in range(8):
    t=i*math.tau/8;x=.5+.35*math.cos(t);z=.5+.35*math.sin(t)
    mod('dish',(x-.06,z-.06,x+.06,z+.06),.5+(i%2)*.15,labels[2]+str(i+1),'echo')
    a.connect(0,len(a.zones)-1,'connection')
  elif n==3:
   for yy,r in ((a.h*.45,a.w*.36),(a.h*.69,a.w*.27)):
    a.ring((a.cx,round(yy),a.cz),round(r),round(r),'connection',4)
   for i,(x,z) in enumerate(((.06,.40),(.80,.40),(.40,.05),(.40,.80))):
    mod('gate',(x,z,x+.14,z+.14),1 if i==2 else .78,labels[0]+str(i+1),'field')
   for i in range(1,len(a.zones)):a.connect(0,i,'injection')
  elif n==5:
   mod('core',(.4,.36,.60,.66),1,labels[2],'alloycoil')
   for yy in (.22,.52):
    a.ring((a.cx,round(a.h*yy),a.cz),round(a.w*.39),round(a.d*.34),'pipe',4)
   for i,(x,z) in enumerate(((.05,.08),(.76,.08),(.05,.76),(.76,.76))):
    mod('tank',(x,z,x+.18,z+.17),.6,labels[4]+str(i+1),'chemical');a.connect(0,len(a.zones)-1,'pipe')
  else:
   mod('reactor',(.06,.25,.39,.72),1,labels[1],'eternity');mod('core',(.61,.25,.94,.72),.9,labels[2],'injection')
   mod('gate',(.21,.06,.79,.17),.7,labels[4],'field');a.connect(0,1,'connection');a.connect(1,2,'power')
 elif n in (2,11,13):
  rows=3 if n in (2,13) else 4
  for side in range(2):
   for i in range(rows):
    x=.04 if side==0 else .63;z=.04+i*.9/rows
    mod('bed' if n==2 else 'lab' if n==13 else 'hall',(x,z,x+.30,z+.72/rows),(.42+.12*((i+side)%3)),labels[i%len(labels)]+str(side*rows+i+1),'assembly' if n==2 else 'precision' if n==13 else 'process')
  mod('archive',(.39,.32,.60,.69),1,labels[2],'compute')
  for i in range(len(a.zones)-1):a.connect(i,len(a.zones)-1,'connection')
 elif n==4:
  for i,(x,z) in enumerate(((.07,.12),(.69,.54))):mod('tower',(x,z,x+.24,z+.32),1 if i==0 else .9,'对向电极'+str(i+1),'hotcoil')
  mod('rail',(.4,.06,.6,.95),.32,labels[2],'power')
  for x,z in ((.04,.66),(.73,.04)):mod('fin',(x,z,x+.23,z+.25),.55,labels[0],'cool')
  a.connect(0,3,'power');a.connect(1,4,'power')
 elif n==6:
  for i in range(4):
   x=.04+i*.235;mod('fin',(x,.42,x+.17,.92),.4+i*.2,labels[1]+str(i+1),'cold')
  mod('hall',(.12,.06,.88,.28),.33,labels[2],'cold')
  for i in range(4):a.connect(i,4,'pipe')
 elif n==7:
  for i in range(5):
   span=.17 if i in (0,4) else .27;mod('hall',(.5-span,.04+i*.18,.5+span,.19+i*.18),1 if i==2 else .45+i*.05,labels[i],'precision' if i%2 else 'chemical')
  for x in (.04,.82):mod('bed',(x,.23,x+.14,.81),.35,'侧翼回收工坊','assembly')
  for i in range(1,5):a.connect(i-1,i,'pipe')
 elif n==8:
  mod('reactor',(.3,.31,.7,.72),1,labels[0],'star')
  for i,(x,z) in enumerate(((.03,.05),(.69,.05),(.03,.73),(.69,.73))):
   mod('bed',(x,z,x+.26,z+.24),.4,labels[2]+str(i+1),'hotcoil');a.connect(0,i+1,'pipe')
 elif n==9:
  for side in range(2):
   for j in range(3):
    x=.04 if side==0 else .67;mod('archive',(x,.04+j*.31,x+.28,.29+j*.31),.45+j*.16,labels[j%len(labels)]+str(side*3+j+1),'compute')
  mod('hall',(.37,.73,.63,.96),1,'共同记录汇集厅','echo')
  for i in range(6):a.connect(i,6,'connection')
 elif n==10:
  mod('tower',(.28,.23,.73,.77),1,'竖向重力铸造井','field')
  for yy in (.20,.48,.75):a.ring((a.cx,round(a.h*yy),a.cz),round(a.w*.32),round(a.d*.30),'alloycoil',3)
  for x in (.04,.79):mod('bed',(x,.14,x+.17,.87),.30,'取件与回收平台','assembly')
  a.connect(0,1,'power');a.connect(0,2,'power')
 elif n==12:
  for side in (0,1):
   for j in range(6):
    x=.07 if side==0 else .75;mod('gate',(x,.03+j*.155,x+.18,.16+j*.155),1 if j==3 else .7+(j%2)*.16,'约束壁段'+str(side*6+j+1),'field')
  for side in (0,1):
   for j in range(5):a.connect(side*6+j,side*6+j+1,'power')
 elif n==15:
  # 朝觐轴沿纵向递进；不同高度门庭与侧域建筑有明确入口关系。
  for i,(z,span,height) in enumerate(((.12,.36,.28),(.33,.29,.43),(.54,.23,.62),(.80,.18,1))):
   mod('gate' if i<3 else 'hall',(.5-span,z,.5+span,z+.10),height,labels[min(i,len(labels)-1)],'field' if i<3 else 'echo')
  for side in (0,1):
   for j in range(3):
    x=.04 if side==0 else .78;mod('archive',(x,.14+j*.27,x+.17,.32+j*.27),.3+j*.14,'外庭记录与观测域'+str(side*3+j+1),'compute' if j%2 else 'precision')
  for i in range(4,len(a.zones)):a.connect(i,3,'connection')
 # 每座巨构补少量有用途的辅助设备，与主体有实线连接。
 if len(a.zones)>1 and not a.links:
  for i in range(1,len(a.zones)):a.connect(0,i,'power')
 return a.finish()

def hyperion(brief):
 a=Build(brief);folder=ROOT/'src/main/java/com/sirin/hk3gtl/common/multiblock/hyperion'
 files=sorted(folder.glob('HyperionLayerPart*.java'),key=lambda p:int(re.search(r'Part(\d+)',p.name)[1]));layers=[]
 for f in files:
  text=f.read_text(encoding='utf-8')
  for m in re.finditer(r'String\[\]\s+LAYER_\d+\s*=\s*\{(.*?)\};',text,re.S):layers.append(re.findall(r'"([^"\r\n]*)"',m[1]))
 assert len(layers)==201 and len(layers[0])==94 and len(layers[0][0])==536
 # 原体素坐标保持；完整方块换材是本轮候选，薄片/楼梯原轮廓不会假装原样保留。
 a.w=537;a.h=96;a.d=209;a.cx=a.w//2;a.cz=a.d//2
 counts=collections.Counter();sourcepoints=0
 for z,layer in enumerate(layers):
  for y,row in enumerate(layer):
   for x,ch in enumerate(row):
    if ch==' ':continue
    role='wall'
    if ch in '567;A':role='glass'
    elif ch in 'CDE8':role='power'
    elif ch in '9:?':role='rib'
    elif ch in '<=>@':role='compute'
    elif ch in './0123':role='grate'
    a.set(x,y+1,z+7,role);counts[ch]+=1;sourcepoints+=1
 # 现有舰体挂在规划维护船坞上；支撑不改舰体占据坐标。
 for x in (12,100,200,335,435,522):
  for z in (40,160):
   ys=[p[1] for p in a.b if abs(p[0]-x)<=3 and abs(p[2]-z)<=3]
   if ys:a.box((x,1,z),(x,min(ys),z),'power')
 for z in (6,a.d-1):a.box((0,0,z),(a.w-1,0,z),'floor')
 # 前侧舰桥服务台、后侧维护梁达到总表外包；不靠一根针凑高。
 a.box((a.cx-18,88,110),(a.cx+18,95,122),'panel',True)
 for x in (a.cx-18,a.cx+18):a.box((x,6,110),(x,88,110),'rib')
 a.zones=[{'name':'既有旗舰舰体完整体素换材候选','kind':'imported','min':[0,1,7],'max':[535,94,207],'pos':[268,94,107],'role':'wall','description':'逐层读取现有201×94×536字符布局，保持非空气位置；薄片与楼梯占位映射为完整机壳，外观变化需审批。原始位置数'+str(sourcepoints)},
 {'name':'舰桥资料与服务舱','kind':'archive','min':[a.cx-18,88,110],'max':[a.cx+18,95,122],'pos':[a.cx,95,116],'role':'panel','description':'新增上部舰桥服务段，与落地维护船坞连接；不是已实现舰载功能'}]
 # 原舰体可能占据中轴低位，单独使用舰体下方维护甲板，禁止删除原坐标。
 collisions=[p for p in a.b if a.cx-1<=p[0]<=a.cx+1 and 1<=p[1]<=4 and p[2]>=4]
 if collisions:
  a.b={(x,y+5,z):s for (x,y,z),s in a.b.items()};a.h+=5
  for zone in a.zones:
   for field in ('min','max','pos'):zone[field][1]+=5
  a.zones[0]['description']+='；为保留舰体下方检修净空，舰体与服务舱统一抬高5格，区内相对位置保持'
  for x in (12,a.w-13):a.box((x,1,7),(x,6,7),'power')
 return a.finish()

def build(brief):
 key=brief['id']
 return industrial(brief) if key.startswith('I') else research(brief) if key.startswith('S') else wonder(brief) if key.startswith('W') else hyperion(brief)
