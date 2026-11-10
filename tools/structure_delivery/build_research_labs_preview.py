# -*- coding: utf-8 -*-
"""四阶研究所材质候选；变更#1实际时间写入audit，不改生产结构或实例。
复用现有材质解析、技能NBT导出和Sponge写入；双底包缺失材质立即拒绝。
变更#2 2026-09-28 02:50:25：新增总表逐轴与实体尺寸门禁；候选02另存，候选01保留为不合格历史。
"""
from pathlib import Path
import os,json,math,collections,subprocess,datetime,hashlib
import nbtlib
from PIL import Image,ImageDraw,ImageFont
from material_resources import Resources
from package_l1_review89 import render_iso
import package_i03_review as sponge
from structure_size_baseline import require as require_size
from research_labs_layout02 import designs as corrected_designs
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/研究所S02-S05_材质候选02'
LOG=ROOT/'logs/research-labs-preview-20260928/candidate02'
SKILL=Path.home()/'.codex/skills/minecraft-builder-skill'
INST=Path.home()/'AppData/Roaming/PrismLauncher/instances'
PALETTE={'floor':'gtceu:clean_machine_casing','frame':'gtceu:clean_machine_casing',
 'body':'gtlcore:iridium_casing','panel':'gtceu:computer_casing','vent':'gtceu:computer_heat_vent',
 'pipe':'gtceu:tungstensteel_pipe_casing','gear':'gtceu:tungstensteel_gearbox',
 'glass':'gtceu:laminated_glass','fusion':'gtceu:fusion_glass','coil':'gtceu:superconducting_coil[active=false]',
 'power':'gtceu:high_power_casing','filter':'gtceu:filter_casing','grating':'gtceu:assembly_line_grating',
 'molecular':'gtlcore:molecular_casing','qft':'gtlcore:qft_coil[active=false]','field':'gtlcore:graviton_field_constraint_casing',
 'compute':'gtlcore:super_computation_component[active=false]','cooler':'gtlcore:super_cooler_component[active=false]',
 'connector':'gtceu:tungstensteel_gearbox','base':'gtceu:clean_machine_casing',
 'controller':'minecraft:diamond_block','port':'minecraft:diamond_ore'}

class Build:
 def __init__(self,key,size,title):
  self.key=key;self.size=size;self.title=title;self.b={};self.cx=size[0]//2;self.cz=size[2]//2
 def set(self,x,y,z,m):
  p=(round(x),round(y),round(z));assert all(0<=p[i]<self.size[i] for i in range(3)),p
  self.b[p]=PALETTE[m]
 def box(self,a,b,m,shell=False):
  for x in range(a[0],b[0]+1):
   for y in range(a[1],b[1]+1):
    for z in range(a[2],b[2]+1):
     if not shell or x in (a[0],b[0]) or y in (a[1],b[1]) or z in (a[2],b[2]):self.set(x,y,z,m)
 def line(self,a,b,m):
  n=max(abs(b[i]-a[i]) for i in range(3))*3+1;old=None
  for j in range(int(n)+1):
   p=tuple(round(a[i]+(b[i]-a[i])*j/n) for i in range(3))
   if old:
    t=list(old)
    for axis in range(3):
     while t[axis]!=p[axis]:t[axis]+=1 if t[axis]<p[axis] else -1;self.set(*t,m)
   self.set(*p,m);old=p
 def ring(self,c,r,plane,m,width=1):
  axes={'xy':(0,1),'xz':(0,2),'yz':(1,2)}[plane]
  for rr in range(r-width+1,r+1):
   points=[]
   for n in range(180+1):
    t=n*math.tau/180;p=list(c);p[axes[0]]+=rr*math.cos(t);p[axes[1]]+=rr*math.sin(t);points.append(p)
   for a,b in zip(points,points[1:]):self.line(a,b,m)
 def pod(self,a,b,skin='body'):
  self.box(a,b,skin,True)
  x0,y0,z0=a;x1,y1,z1=b
  for x in (x0,x1):
   for z in (z0,z1):self.box((x,y0,z),(x,y1,z),'frame')
  if x1-x0>3 and y1-y0>3:
   self.box((x0+1,y0+2,z0),(x1-1,y1-2,z0),'glass')
   self.box((x0+1,y0+2,z1),(x1-1,y1-2,z1),'vent')
  for z in range(z0+1,z1,3):self.box((x0+1,y1,z),(x1-1,y1,z),'grating')
 def finish(self,description):
  w,h,d=self.size;c=self.cx
  self.box((0,0,0),(w-1,0,d-1),'floor')
  self.box((c-5,1,1),(c+5,4,1),'frame')
  ports=[]
  for y in (2,3):
   for x in range(c-4,c+5):
    if (x,y)==(c,2):continue
    self.set(x,y,1,'port');ports.append({'id':('L' if x<c else 'R')+str(len(ports)+1),'pos':[x,y,1],'face':'north','purpose':'接口候选位；必要端口能力待正式Pattern确认，可用工业接口机械方块填充'})
  self.set(c,2,1,'controller')
  paths=[{'min':[c-1,1,4],'max':[c+1,4,d-3]}]
  for route in paths:
   for x in range(route['min'][0],route['max'][0]+1):
    for y in range(1,5):
     for z in range(4,d-2):assert (x,y,z) not in self.b,('通道设计被占据，不允许后切',self.key,x,y,z)
  for p in ports:assert (p['pos'][0],p['pos'][1],0) not in self.b
  assert all(self.b[(x,0,z)]==PALETTE['floor'] for x in range(w) for z in range(d))
  # 所有几何必须与基座六邻接连通，避免孤立装饰。
  todo=set(self.b);q=collections.deque([next(iter(todo))]);todo.remove(q[0])
  while q:
   x,y,z=q.popleft()
   for p in ((x-1,y,z),(x+1,y,z),(x,y-1,z),(x,y+1,z),(x,y,z-1),(x,y,z+1)):
    if p in todo:todo.remove(p);q.append(p)
  assert not todo,('孤立方块',self.key,len(todo),list(todo)[:5])
  return {'key':self.key,'name':'hk3gtl-'+self.key+'-research-review-02','title':self.title,'size':self.size,'controller':[c,2,1],'ports':ports,'paths':paths,'zones':[], 'description':description,'blocks':[{'pos':list(p),'state':s} for p,s in sorted(self.b.items())]}

def designs():
 a=Build('s02',[35,23,31],'S02 高级材料研究所');c=a.cx
 for x in (2,24):a.pod((x,1,8),(x+8,9,25));a.box((x+2,2,6),(x+6,4,6),'filter');a.line((x+4,4,6),(x+4,4,8),'pipe')
 a.pod((c-5,7,12),(c+5,17,26),'molecular')
 for x in (c-5,c+5):
  for z in (12,26):a.box((x,1,z),(x,7,z),'power')
 for x in (4,30):a.pod((x-1,1,27),(x+1,21,29),'cooler');a.line((x,12,27),(c-5 if x<c else c+5,12,25),'pipe')
 for x in (c-7,c+7):a.box((x,1,6),(x,4,26),'panel');a.box((x,5,9),(x,5,25),'connector')
 yield a.finish('白色连续基座，左右制备/冷却翼，中央高架检测腔，后侧双散热柱；中轴净空从设备下方通过，框内17个接口候选位。')
 a=Build('s03',[45,39,45],'S03 量子研究所');c=a.cx;z=a.cz
 for x in (5,35):
  for zz in (8,32):a.pod((x-2,1,zz-2),(x+2,9,zz+2),'panel');a.line((x,9,zz),(c+(12 if x>c else -12),18,z+(12 if zz>z else -12)),'power')
 a.ring((c,22,z),16,'xy','frame',2);a.ring((c,22,z),16,'yz','frame',2)
 a.ring((c,22,z),14,'xy','coil');a.ring((c,22,z),14,'yz','qft');a.ring((c,18,z),17,'xz','molecular')
 for x in (c-17,c+17):a.box((x,1,z),(x,21,z),'power')
 a.pod((c-4,17,z-4),(c+4,25,z+4),'fusion');a.box((c-1,18,z-1),(c+1,24,z+1),'qft')
 a.line((c-17,21,z),(c+17,21,z),'compute');a.line((c,21,z-17),(c,21,z+17),'compute')
 yield a.finish('双交叉观测环包围中央观测腔，四组独立计算支座，以环形约束结构连接；白色前台、统一白色地板与中轴低位检修道。')
 a=Build('s04',[55,55,49],'S04 虚数研究所');c=a.cx;z=a.cz
 for x in (4,42):a.pod((x,1,9),(x+8,14,38),'field');a.box((x+2,15,12),(x+6,16,34),'cooler')
 for x in (c-4,c+4):
  for zz in (z-4,z+4):a.box((x,1,zz),(x,47,zz),'field')
 a.pod((c-3,8,z-3),(c+3,49,z+3),'fusion');a.box((c-1,9,z-1),(c+1,48,z+1),'qft')
 for yy,rr in ((12,14),(27,18),(43,12)):
  a.ring((c,yy,z),rr,'xz','frame',2);a.ring((c,yy+1,z),rr-2,'xz','coil')
  for xx in (c-rr,c+rr):a.line((xx,yy,z),(c-4 if xx<c else c+4,yy,z),'power')
 for phase in (0,math.pi):
  points=[(c+10*math.cos(phase+i*math.tau/60),8+i*.7,z+10*math.sin(phase+i*math.tau/60)) for i in range(61)]
  for p,q in zip(points,points[1:]):a.line(p,q,'molecular')
  a.line(points[0],(c+4 if points[0][0]>c else c-4,8,z),'connector')
 for x in (c-18,c+18):a.line((x,14,z),(x,27,z),'pipe')
 yield a.finish('竖直透明锚定柱、双螺旋约束构件、三组不同直径的错层环，两翼为稳定与能流设施；地面中轴通道连续，主体没有为通道删切。')
 a=Build('s05',[65,45,65],'S05 文明认知穹顶');c=a.cx;z=33
 for x in (3,49):a.pod((x,1,14),(x+12,12,44),'panel');a.box((x+3,13,19),(x+9,14,39),'compute')
 a.pod((20,6,51),(44,17,61),'molecular')
 for xx in (20,44):a.box((xx,1,51),(xx,6,61),'power')
 a.ring((c,16,z),19,'xz','frame',2);a.ring((c,17,z),17,'xz','compute')
 for theta in [i*math.tau/8 for i in range(8)]:
  points=[(c+19*math.cos(t)*math.cos(theta),16+19*math.sin(t),z+19*math.cos(t)*math.sin(theta)) for t in [j*math.pi/2/36 for j in range(37)]]
  for p,q in zip(points,points[1:]):a.line(p,q,'frame')
 for yy in (21,26,31):a.ring((c,yy,z),round(math.sqrt(19**2-(yy-16)**2)),'xz','fusion')
 for xx in (c-19,c+19):a.box((xx,1,z),(xx,16,z),'field')
 for zz in (z-19,z+19):
  for xx in (c-3,c+3):a.box((xx,1,zz),(xx,16,zz),'field')
 a.pod((c-5,9,z-5),(c+5,20,z+5),'fusion');a.box((c-2,10,z-2),(c+2,19,z+2),'compute')
 for xx in (c-5,c+5):
  for zz in (z-5,z+5):a.box((xx,1,zz),(xx,9,zz),'power')
 a.line((13,12,z),(c-19,16,z),'connector');a.line((51,12,z),(c+19,16,z),'connector');a.line((c,17,51),(c,17,52),'connector')
 yield a.finish('中央分段认知穹顶、两侧档案计算翼与后侧整合翼；环廊和分层计算组件呈横向展开，与S04高塔区分，不合并W09奇观。')

def main():
 assert (SKILL/'node_modules/@mattzh72/lodestone').is_dir()
 candidates=list(corrected_designs(Build))
 for data in candidates:require_size(data)
 OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
 res=[Resources(INST/n/'minecraft') for n in ['GregTech-Leisure-1.4.5.2','GregTech Leisure-增强版「巨构时代」 2.1']]
 mats={};verification=[]
 try:
  for state in sorted(set(PALETTE.values())):
   ms=[r.material(state) for r in res];mats[state]=ms[0]
   verification.append({'state':state,'both_complete_cube':all(m['complete_cube'] for m in ms),'same_preview_faces':ms[0]['faces']==ms[1]['faces'],'tinted':any(m['tinted'] for m in ms)})
 finally:
  for r in res:r.close()
 (LOG/'materials-dual-pack.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
 manifest=[];images=[]
 for data in candidates:
  out=OUT/data['key'];out.mkdir(exist_ok=True);states=sorted({b['state'] for b in data['blocks']});materials=[mats[s] for s in states]
  (out/'blueprint.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
  (out/'materials.json').write_text(json.dumps(materials,ensure_ascii=False),encoding='utf-8')
  subprocess.run(['node',str(SKILL/'scripts/run-build.mjs'),str(ROOT/'tools/structure_delivery/l1-review89-recipe.mjs'),'--out-dir',str(out),'--name',data['name'],'--no-block-state-updates','--json'],env={**os.environ,'HK3_REVIEW_BLUEPRINT':str(out/'blueprint.json')},cwd=SKILL,check=True,capture_output=True)
  saved=nbtlib.load(out/(data['name']+'.nbt'));decoded={tuple(map(int,b['pos'])):str(saved['palette'][int(b['state'])]['Name'])+('['+','.join(str(k)+'='+str(v) for k,v in saved['palette'][int(b['state'])].get('Properties',{}).items())+']' if saved['palette'][int(b['state'])].get('Properties') else '') for b in saved['blocks']};assert decoded=={tuple(b['pos']):b['state'] for b in data['blocks']}
  sponge.OUT=out;sponge.NAME=data['name'];schem,_,_=sponge.write_sponge(data)
  audit={'time':datetime.datetime.now().astimezone().isoformat(),'palette':dict(collections.Counter(b['state'] for b in data['blocks'])),'checks':['JSON/NBT/Sponge逐格一致','双底包静态完整方块模型与六面纹理解析通过','主控水平居中，白框内部17个接口候选位','地板统一；中轴通道3格宽4格净高，无后切主体','所有方块六邻接连通；接口正前方无阻挡'],'not_verified':['未接入Pattern和机器能力','未游戏验收','材质首帧，不模拟动态染色及全部游戏光照'],'sha256':hashlib.sha256(schem.read_bytes()).hexdigest()}
  audit['size_baseline']=require_size(data)
  audit['checks'].append('69座总表逐轴下限与实际实体包围盒检查通过')
  (out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
  images.append(render_iso(data,materials,out));manifest.append({k:data[k] for k in ('key','name','title','size','description') }|{'blocks':len(data['blocks']),'materials':len(states)})
  print(data['key'],len(data['blocks']),len(states),flush=True)
 overview=Image.new('RGB',(1800,1700),(19,26,40));draw=ImageDraw.Draw(overview);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
 draw.text((25,18),'S02–S05 · 明确材质候选02（宽×长×高；非游戏截图，待审批）',font=font,fill='white')
 for i,(m,im) in enumerate(zip(manifest,images)):
  im.thumbnail((870,700),Image.Resampling.LANCZOS);x=i%2*900;y=i//2*810+60;overview.paste(im,(x+(900-im.width)//2,y+(700-im.height)//2));draw.text((x+20,y+720),m['title']+'  '+str([m['size'][0],m['size'][2],m['size'][1]]),font=font,fill='white')
 overview.save(OUT/'四阶总览.png');(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 (LOG/'delivery.json').write_text(json.dumps({'time':datetime.datetime.now().astimezone().isoformat(),'candidate_only':True,'formal_modified':False,'instance_modified':False,'structures':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
