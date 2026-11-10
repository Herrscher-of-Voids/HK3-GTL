# -*- coding: utf-8 -*-
"""终焉之茧的同源几何生成器：破裂球壳、发光内核、悬浮碎片和薄光环。
变更记录 #1：2026-10-01 19:57:23（修订146）。新增参考球体的手工参数化模型，
输出客户端场景资源；不裁切参考图、不生成机器结构、不改变一审判定。
三角面保存为九个坐标加三个色值；动画参数由游戏和预览共用。
"""
from pathlib import Path
from datetime import datetime
import math,json,random
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliveries/修订146_终焉之茧球体'
ASSETS=ROOT/'src/main/resources/assets/hk3gtl'
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return mul(a,1/math.sqrt(dot(a,a)))
def ico(level):
 t=(1+math.sqrt(5))/2
 vertices=[norm(v) for v in [(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),(0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]]
 faces=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
 for _ in range(level):
  cache={};next_faces=[]
  def midpoint(a,b):
   key=tuple(sorted((a,b)))
   if key not in cache:cache[key]=len(vertices);vertices.append(norm(add(vertices[a],vertices[b])))
   return cache[key]
  for a,b,c in faces:
   d,e,f=midpoint(a,b),midpoint(b,c),midpoint(c,a);next_faces.extend([(a,d,f),(b,e,d),(c,f,e),(d,e,f)])
  faces=next_faces
 return vertices,faces
def triangle(points,color):return [round(x,5) for p in points for x in p]+[int(max(0,min(255,c))) for c in color]
def part(name,kind,triangles,origin=(0,0,0),bob=0,phase=0,speed=0):
 return dict(name=name,kind=kind,origin=origin,bob=bob,phase=phase,speed=speed,triangles=triangles)
def generate():
 OUT.mkdir(parents=True,exist_ok=True);rng=random.Random(146)
 from cocoon_reference_mesh import build
 parts=build(ico,triangle,part)
 # 以玩家1.8格身高为线性基准：直径200格约111.1倍，几何密度同步增加。
 scale=12.5
 for p in parts:
  p['origin']=[round(x*scale,5) for x in p['origin']];p['bob']*=scale
  for tri in p['triangles']:
   for i in range(9):tri[i]=round(tri[i]*scale,5)
 data=dict(revision=146,recorded=datetime.now().isoformat(timespec='seconds'),description='参照用户两图及纠正：200格完整暗紫球体、六重内凹菱形光纹、放射分叉裂纹、白紫光冠与悬浮碎片；手工参数化近似，不使用原图纹理。',radius=100,player_height=1.8,diameter_to_player_height=200/1.8,scene_center=[.5,120,260.5],room_spacing=512,animation=dict(body_bob=1.75,yaw_amplitude=.035,period_seconds=12),parts=parts)
 resource=ASSETS/'models/scene/cocoon_review.json';resource.parent.mkdir(parents=True,exist_ok=True);resource.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 (OUT/'cocoon_review.json').write_bytes(resource.read_bytes())
 texture=ASSETS/'textures/effect/cocoon_white.png';texture.parent.mkdir(parents=True,exist_ok=True);Image.new('RGBA',(16,16),'white').save(texture)
 print(json.dumps(dict(parts=len(parts),triangles=sum(len(p['triangles']) for p in parts)),ensure_ascii=False))
if __name__=='__main__':generate()

# 变更记录 #2：2026-10-01 20:04:51（修订146追加），按用户纠正改为纵向菱形核心，直径200格，增加球壳网格密度并调整同源查看器尺度。

# 变更记录 #3：2026-10-01 20:08:28（修订146最新近图），移除实心菱形宝石与均匀拼板壳，改用六重内凹菱形光纹、放射深裂纹和白紫光冠。
