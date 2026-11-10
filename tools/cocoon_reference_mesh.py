# -*- coding: utf-8 -*-
"""变更记录 #1：2026-10-01 20:06:38（修订146近图修正）。
按最新近图构建暗紫球面、放射分叉裂纹、内凹嵌套菱形与白紫光冠。
输入通用三角网格助手，输出同源场景分件；不将官方截图当作游戏贴图。
"""
import math,random

def build(ico,triangle,part):
 rng=random.Random(146);vertices,faces=ico(4)
 def surface(x,y,offset=0):
  length=math.hypot(x,y)
  if length>7.98:x*=7.98/length;y*=7.98/length
  z=-math.sqrt(max(.01,64-x*x-y*y));scale=(8+offset)/8
  return (x*scale,y*scale,z*scale)
 sphere=[]
 for face in faces:
  n=[sum(vertices[j][k] for j in face)/3 for k in range(3)]
  shade=.58+.42*max(0,(-.3*n[0]+.7*n[1]-n[2])/1.26)
  cloud=.94+.06*math.sin(n[0]*12+n[1]*9)*math.cos(n[1]*14-n[2]*8)
  sphere.append(triangle([tuple(x*8 for x in vertices[j]) for j in face],(47*shade*cloud,21*shade*cloud,110*shade*cloud)))
 parts=[part('完整暗紫球壳','solid',sphere)];dark=[];energy=[]
 def ribbon(points,widths,color,target,offset=.035,project=True):
  for i in range(len(points)-1):
   a,b=points[i],points[i+1];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
   if length<1e-7:continue
   nx,ny=-dy/length,dx/length
   xy=[(a[0]+nx*widths[i],a[1]+ny*widths[i]),(a[0]-nx*widths[i],a[1]-ny*widths[i]),(b[0]-nx*widths[i+1],b[1]-ny*widths[i+1]),(b[0]+nx*widths[i+1],b[1]+ny*widths[i+1])]
   ps=[surface(x,y,offset) if project else (x,y,offset) for x,y in xy]
   target.extend([triangle([ps[0],ps[1],ps[2]],color),triangle([ps[0],ps[2],ps[3]],color)])
 def boundary(angle,scale=1):
  # p<1形成参考图中微微内凹的菱形边，四尖保持清楚。
  p=.76;c,s=math.cos(angle),math.sin(angle)
  radius=(abs(c/2.35)**p+abs(s/3.6)**p)**(-1/p)*scale
  return radius*c,1+radius*s
 for i in range(15):
  angle=i*math.tau/15+.07;start=boundary(angle,1.08);end=(math.cos(angle)*7.55,math.sin(angle)*7.55);pts=[]
  for j in range(25):
   t=j/24;jitter=math.sin(j*1.7+i)*.07+math.sin(t*8+i)*.19
   pts.append((start[0]*(1-t)+end[0]*t-math.sin(angle)*jitter,start[1]*(1-t)+end[1]*t+math.cos(angle)*jitter))
  widths=[.16*(1-j/25)**.7+.016 for j in range(25)]
  ribbon(pts,widths,(13,5,34),dark)
  ribbon(pts[:8],[w*.095 for w in widths[:8]],(185,64,211),energy,.062)
  for j in [5,10,16]:
   origin=pts[j];side=-1 if (i+j)%2 else 1;direction=angle+side*rng.uniform(.35,.8);length=rng.uniform(.6,1.6)
   branch=[(origin[0]+math.cos(direction)*length*k/8+math.sin(k*2+i)*.055,origin[1]+math.sin(direction)*length*k/8+math.cos(k*1.6)*.04) for k in range(9)]
   ribbon(branch,[.065*(1-k/9)+.008 for k in range(9)],(19,6,43),dark,.04)
 parts.extend([part('向外分叉的深色裂纹','solid',dark),part('裂纹内缘紫粉光','pulse',energy)])
 # 多圈内凹菱形刻线；没有凸出的实心宝石晶体。
 count=192;back=[];rings=[]
 # 逐圈细分贴合球面，不能用跨越整个曲面的长三角扇，否则底光会陷入球壳。
 for band in range(1,21):
  outer=band/20*1.06;inner=(band-1)/20*1.06
  for j in range(count):
   a=j*math.tau/count;b=(j+1)*math.tau/count
   ps=[surface(*boundary(a,outer),.09),surface(*boundary(a,inner),.09),surface(*boundary(b,inner),.09),surface(*boundary(b,outer),.09)]
   if band>1:back.append(triangle([ps[0],ps[1],ps[2]],(238,116,232)))
   back.append(triangle([ps[0],ps[2],ps[3]],(238,116,232)))
 for index,scale in enumerate([1,.81,.63,.45,.28,.12]):
  outside=scale;inside=max(.025,scale-.038)
  for j in range(count):
   a=j*math.tau/count;b=(j+1)*math.tau/count
   ps=[surface(*boundary(a,outside),.13),surface(*boundary(a,inside),.13),surface(*boundary(b,inside),.13),surface(*boundary(b,outside),.13)]
   col=(255,213+min(35,index*6),252)
   rings.extend([triangle([ps[0],ps[1],ps[2]],col),triangle([ps[0],ps[2],ps[3]],col)])
 parts.extend([part('菱形紫粉底光','pulse',back),part('六重内凹菱形光纹','pulse',rings)])
 corona=[];halo=[]
 for j in range(128):
  a=j*math.tau/128;b=(j+1)*math.tau/128
  def ring(t,r):return (math.cos(t)*r,math.sin(t)*r,.9)
  outer=8.18+.8*(.5+.5*math.sin(j*2.399))**3;next_outer=8.18+.8*(.5+.5*math.sin((j+1)*2.399))**3
  ps=[ring(a,8.0),ring(a,outer),ring(b,8.0),ring(b,next_outer)]
  corona.extend([triangle([ps[0],ps[1],ps[2]],(230,195,255)),triangle([ps[2],ps[1],ps[3]],(245,218,255))])
  qs=[ring(a,8.2),ring(a,outer+.6),ring(b,8.2),ring(b,next_outer+.6)]
  halo.extend([triangle([qs[0],qs[1],qs[2]],(159,58,242)),triangle([qs[2],qs[1],qs[3]],(159,58,242))])
 lightning=[]
 for i in range(40):
  a=i*math.tau/40;pts=[]
  for j in range(12):
   r=8.2+j*.23;angle=a+math.sin(j*1.7+i)*.018
   pts.append((r*math.cos(angle),r*math.sin(angle)))
  ribbon(pts,[.018]*12,(159,86,233),lightning,1.3,False)
 parts.extend([part('白紫破碎光冠','pulse',corona),part('外层紫晕','glow',halo),part('外围细放电纹','glow',lightning)])
 sv,sf=ico(0)
 for i in range(30):
  a=i*2.39996;y=rng.uniform(-1,1);r=math.sqrt(1-y*y);direction=(r*math.cos(a),y,r*math.sin(a));origin=[v*rng.uniform(9.2,11.4) for v in direction];size=rng.uniform(.09,.32)
  tris=[]
  for face in sf:
   col=(175,146,208) if rng.random()<.25 else (93,68,141)
   tris.append(triangle([(sv[j][0]*size,sv[j][1]*size*.65,sv[j][2]*size*.35) for j in face],col))
  parts.append(part('悬浮碎片%02d'%i,'solid',tris,origin,rng.uniform(.07,.2),rng.random()*math.tau,rng.uniform(-.1,.1)))
 return parts
