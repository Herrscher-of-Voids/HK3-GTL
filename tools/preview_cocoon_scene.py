# -*- coding: utf-8 -*-
"""变更记录 #1：2026-10-01 20:00:40（修订146）。同源几何旋转预览及离线截图。
不启动游戏；软件合成图用于核对轮廓，不能证明游戏透明排序与光照正确。
"""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'deliveries/修订146_终焉之茧球体'
data=json.loads((OUT/'cocoon_review.json').read_text(encoding='utf-8'))
three=(ROOT/'node_modules/three/build/three.module.min.js').read_text(encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>终焉之茧 · 一审场景</title>
<style>body{margin:0;background:#0a0618;color:#f2eafd;font:16px system-ui}header{position:absolute;top:24px;left:28px;pointer-events:none}h1{font-size:28px;margin:0 0 10px}p{color:#b9a9d1;line-height:1.7;margin:0}nav{position:absolute;bottom:24px;left:28px;display:flex;gap:10px}button{padding:12px 18px;border:1px solid #765593;border-radius:8px;background:#241633;color:#f1e7fb;cursor:pointer}canvas{display:block;touch-action:none}#state{position:absolute;right:24px;bottom:32px;color:#b9a9d1}</style>
<header><h1>终焉之茧</h1><p>直径200格 · 约111倍玩家身高 · 六重菱形光纹<br>拖动旋转 · 滚轮缩放 · 右键平移<br>游戏同源几何预览；光照与透明效果以游戏为准。</p></header>
<nav><button id="front">正面</button><button id="side">侧面</button><button id="back">背面</button><button id="pause">暂停动画</button><button id="shell">隐藏球壳</button></nav><span id="state">加载…</span>
<script id="three" type="text/plain">__THREE__</script><script type="module">
const THREE=await import(URL.createObjectURL(new Blob([document.querySelector('#three').textContent],{type:'text/javascript'})));
const data=__DATA__, scene=new THREE.Scene();scene.background=new THREE.Color('#0a0618');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;document.body.append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.1,4000),cocoon=new THREE.Group();scene.add(cocoon);
const parts=[];for(const part of data.parts){
 const pos=[],colors=[];for(const tri of part.triangles){pos.push(...tri.slice(0,9));for(let i=0;i<3;i++){const c=new THREE.Color(tri[9]/255,tri[10]/255,tri[11]/255);c.convertSRGBToLinear();colors.push(c.r,c.g,c.b)}}
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.computeVertexNormals();
 const material=new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,transparent:part.kind==='glow',opacity:part.kind==='glow'?.28:1,depthWrite:part.kind!=='glow'});
 const mesh=new THREE.Mesh(geometry,material);mesh.position.fromArray(part.origin);cocoon.add(mesh);parts.push({mesh,part});
}
let azimuth=0,elevation=.06,distance=data.radius*4.375,target=new THREE.Vector3(0,0,0),playing=true,time=0,last=0,visible=true;
function cameraUpdate(){camera.position.set(target.x+distance*Math.sin(azimuth)*Math.cos(elevation),target.y+distance*Math.sin(elevation),target.z-distance*Math.cos(azimuth)*Math.cos(elevation));camera.lookAt(target)}
function resize(){renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix()}addEventListener('resize',resize);resize();
let drag=null;renderer.domElement.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,button:e.button};renderer.domElement.setPointerCapture(e.pointerId)};
renderer.domElement.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(drag.button===2){target.x-=dx*.25;target.y+=dy*.25}else{azimuth-=dx*.006;elevation=Math.max(-1.3,Math.min(1.3,elevation+dy*.006))}drag.x=e.clientX;drag.y=e.clientY};
renderer.domElement.onpointerup=()=>drag=null;renderer.domElement.onpointercancel=()=>drag=null;renderer.domElement.oncontextmenu=e=>e.preventDefault();renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();distance=Math.max(130,Math.min(1200,distance*Math.exp(e.deltaY*.001)))},{passive:false});
document.querySelector('#front').onclick=()=>{azimuth=0;elevation=.06;target.set(0,0,0)};document.querySelector('#side').onclick=()=>{azimuth=Math.PI/2;elevation=.06};document.querySelector('#back').onclick=()=>{azimuth=Math.PI;elevation=.06};
document.querySelector('#pause').onclick=()=>{playing=!playing;document.querySelector('#pause').textContent=playing?'暂停动画':'继续动画'};
document.querySelector('#shell').onclick=()=>{visible=!visible;parts[0].mesh.visible=visible;document.querySelector('#shell').textContent=visible?'隐藏球壳':'显示球壳'};
document.querySelector('#state').textContent='球体直径 '+data.radius*2+' 格 · 同源场景模型';
function frame(now){if(last&&playing)time+=(now-last)/1000;last=now;const wave=Math.sin(time*Math.PI*2/data.animation.period_seconds);cocoon.position.y=data.animation.body_bob*wave;cocoon.rotation.y=data.animation.yaw_amplitude*wave;
 for(const {mesh,part} of parts){mesh.position.y=part.origin[1]+part.bob*Math.sin(time*.55+part.phase);mesh.rotation.y=part.speed?time*part.speed+part.phase:0;const bright=part.kind==='pulse'?.91+.09*wave:1;mesh.material.color.setRGB(bright,bright,bright);if(part.kind==='glow')mesh.material.opacity=(72+18*wave)/255}
 cameraUpdate();renderer.render(scene,camera);requestAnimationFrame(frame)}requestAnimationFrame(frame);
</script></html>'''.replace('__THREE__',three).replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')))
(OUT/'终焉之茧模型预览.html').write_text(html,encoding='utf-8')
log=ROOT/'logs/cocoon-r146';log.mkdir(parents=True,exist_ok=True);(log/'viewer-check.mjs').write_text(html.split('<script type="module">')[1].split('</script>')[0],encoding='utf-8')

def render(yaw,path):
 import numpy as np
 w,h=1400,1000;im=Image.new('RGB',(w,h),'#0a0618');draw=ImageDraw.Draw(im);polys=[]
 def project(v):
  x,y,z=[a/(data['radius']/8) for a in v];xx=x*math.cos(yaw)+z*math.sin(yaw);zz=-x*math.sin(yaw)+z*math.cos(yaw);s=1000/(zz+36)
  return (w/2+xx*s,h*.55-y*s),zz
 for p in data['parts']:
  if p['kind']=='glow':continue
  for t in p['triangles']:
   pts=[];zs=[]
   for i in range(0,9,3):
    v=list(t[i:i+3]);a=p['phase'] if p['speed'] else 0;x,z=v[0],v[2];v[0]=x*math.cos(a)+z*math.sin(a);v[2]=-x*math.sin(a)+z*math.cos(a)
    xy,depth=project([v[j]+p['origin'][j] for j in range(3)]);pts.append(xy);zs.append(depth)
   polys.append((zs,pts,tuple(t[9:])))
 # 光冠置于球体后，软光仅作离线示意，不冒充实机后处理。
 glow=Image.new('RGB',(w,h));gd=ImageDraw.Draw(glow)
 for radius,color in [(260,(31,4,61)),(246,(66,15,109)),(237,(107,34,165))]:gd.ellipse((w/2-radius,h*.55-radius,w/2+radius,h*.55+radius),outline=color,width=15)
 glow=glow.filter(ImageFilter.GaussianBlur(12));from PIL import ImageChops
 im=ImageChops.add(im,glow);pixels=np.array(im);depth=np.full((h,w),np.inf)
 # 深度缓冲逐像素比较，避免软件画家排序把曲面上的细裂纹错误遮挡。
 for zs,pts,color in polys:
  a,b,c=pts;x0=max(0,int(min(p[0] for p in pts)));x1=min(w,int(max(p[0] for p in pts))+1);y0=max(0,int(min(p[1] for p in pts)));y1=min(h,int(max(p[1] for p in pts))+1)
  denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if x0>=x1 or y0>=y1 or abs(denominator)<1e-9:continue
  yy,xx=np.mgrid[y0:y1,x0:x1];xx=xx+.5;yy=yy+.5
  wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/denominator
  wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/denominator;wc=1-wa-wb
  inside=(wa>=0)&(wb>=0)&(wc>=0)
  inv=wa/(zs[0]+36)+wb/(zs[1]+36)+wc/(zs[2]+36);z=1/np.maximum(inv,1e-9)
  take=inside&(z<depth[y0:y1,x0:x1]);depth[y0:y1,x0:x1][take]=z[take];pixels[y0:y1,x0:x1][take]=color
 im=Image.fromarray(pixels);draw=ImageDraw.Draw(im)
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
 draw.text((42,32),'终焉之茧 · 200格球体',font=font,fill='#ede2ff');draw.text((42,78),'六重菱形光纹 / 紫色裂壳 / 约111倍玩家身高',font=small,fill='#b6a3cd')
 draw.text((42,h-55),'同源几何离线示意 · 不是游戏截图；柔光为示意处理。',font=small,fill='#b6a3cd');im.save(path)
render(0,OUT/'球体正面.png');render(.65,OUT/'球体侧面.png')
print(str(OUT/'终焉之茧模型预览.html'))

# 变更记录 #2：2026-10-01 20:04:51（修订146追加），按用户纠正改为纵向菱形核心，直径200格，增加球壳网格密度并调整同源查看器尺度。

# 变更记录 #3：2026-10-01 20:08:28（修订146近图），同源显示六重菱形光纹与放射裂纹，不再展示实心宝石。
