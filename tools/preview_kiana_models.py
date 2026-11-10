# -*- coding: utf-8 -*-
"""修订142：从游戏实际几何和皮肤生成离线旋转查看器；不是游戏渲染截图。"""
# 变更记录 #2：2026-10-01 19:19:40（修订143），读取三层动画图集，新增拆层和暂停预览。
# 变更记录 #3：2026-10-01 19:31:08（修订144），五层实际间距，边缘只画侧面，半透明帧采用固定alpha插值。
# 变更记录 #4：2026-10-01 19:47:01（修订145），按参考重制轮廓读取尺寸元数据，默认合拢显示。
from pathlib import Path
import json, base64, re
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'deliveries/修订145_琪亚娜参考轮廓重制'
geometry=json.loads((out/'layers.json').read_text(encoding='utf-8'))
for layer in geometry['layers']:
    layer['image']=base64.b64encode((out/layer['texture']).read_bytes()).decode()
three=(ROOT/'node_modules/three/build/three.module.min.js').read_text(encoding='utf-8')
skin=base64.b64encode((out/'kiana_review.png').read_bytes()).decode()
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>琪亚娜 · 二审形象</title>
<style>body{margin:0;background:#141724;color:#f0eafa;font:16px system-ui}header{position:absolute;top:20px;left:26px;pointer-events:none}h1{font-size:26px;margin:0 0 10px}p{color:#b9b3ce;line-height:1.65;margin:4px 0}nav{position:absolute;bottom:22px;left:26px;display:flex;gap:10px}button{background:#2b2c46;color:white;border:1px solid #62567c;border-radius:9px;padding:12px 18px;cursor:pointer}button.active{background:#7860a6}#status{position:absolute;right:24px;bottom:28px;color:#b9b3ce}canvas{display:block;touch-action:none}</style>
<header><h1>终焉之律者 · 琪亚娜</h1><p>Alex 细手臂 · 128×128 原皮肤 · 紧凑参考翼形 · 五层星海 · 无武器</p><p>左键拖动旋转 · 滚轮缩放 · 右键拖动平移<br>读取游戏同源动画贴图；浏览器光照与游戏内可能不同。</p></header>
<nav><button data-mode="all" class="active">完整形象</button><button data-mode="wings">双翼</button><button id="split">拆开五层</button><button id="pause">暂停动画</button><button id="front">正面</button><button id="back">背面</button></nav><span id="status">加载几何…</span>
<script id="three" type="text/plain">__THREE__</script><script type="module">
const THREE=await import(URL.createObjectURL(new Blob([document.querySelector('#three').textContent],{type:'text/javascript'})));
const data=__DATA__, skinURL='data:image/png;base64,__SKIN__';
const scene=new THREE.Scene();scene.background=new THREE.Color('#141724');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));document.body.append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(38,innerWidth/innerHeight,.1,500);
scene.add(new THREE.HemisphereLight(0xe4d6ff,0x65517d,2.2));let light=new THREE.DirectionalLight(0xffffff,2);light.position.set(-35,65,-60);scene.add(light);
const actor=new THREE.Group();actor.scale.y=-1;actor.position.y=24;scene.add(actor);
const bones={body:new THREE.Group(),right_arm:new THREE.Group(),left_arm:new THREE.Group()};
bones.right_arm.position.set(-5,2.5,0);bones.left_arm.position.set(5,2.5,0);Object.values(bones).forEach(b=>actor.add(b));
const objects={},animations=[],layerGroups=[],texSize=data.texture_size;
const loadImage=src=>new Promise((ok,bad)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=bad;i.src=src});
for(const side of ['left','right']){let wing=new THREE.Group();bones.body.add(wing);objects['wing_'+side]=wing;wing.position.z=3.8;
 for(const layer of data.layers.filter(l=>l.side===side)){
  const source=await loadImage('data:image/png;base64,'+layer.image),canvas=document.createElement('canvas');canvas.width=canvas.height=texSize;const ctx=canvas.getContext('2d');ctx.drawImage(source,0,0,texSize,texSize,0,0,texSize,texSize);
  const tex=new THREE.CanvasTexture(canvas);tex.magFilter=THREE.NearestFilter;tex.minFilter=THREE.NearestFilter;tex.colorSpace=THREE.SRGBColorSpace;
  const material=layer.name.startsWith('frame')?new THREE.MeshStandardMaterial({map:tex,side:THREE.FrontSide,alphaTest:.01,transparent:layer.translucent,depthWrite:!layer.translucent,roughness:1}):new THREE.MeshBasicMaterial({map:tex,side:THREE.FrontSide,alphaTest:.01,transparent:layer.translucent,depthWrite:!layer.translucent});
  const group=new THREE.Group();wing.add(group);const index=['frame1','galaxy1','stars','galaxy2','frame2'].indexOf(layer.name);group.position.z=layer.z;layerGroups.push({group,index,z:layer.z});
  const geometry=new THREE.PlaneGeometry(data.layout.width,data.layout.width);const uv=geometry.attributes.uv;for(let j=0;j<uv.count;j++)uv.setY(j,1-uv.getY(j));
  for(const direction of [-1,1]){const geo=geometry.clone();if(direction<0){const ids=geo.index.array;for(let n=0;n<ids.length;n+=3)[ids[n+1],ids[n+2]]=[ids[n+2],ids[n+1]];geo.computeVertexNormals()}const mesh=new THREE.Mesh(geo,material);mesh.position.set(side==='left'?data.layout.center_x:-data.layout.center_x,data.layout.center_y,direction*layer.depth/2);group.add(mesh)}
  // 只连接边界侧面，禁止用方块再叠一份正反面，以免深度竞争。
  const pixels=ctx.getImageData(0,0,texSize,texSize).data;
  const opaque=(x,y)=>x>=0&&x<texSize&&y>=0&&y<texSize&&pixels[(y*texSize+x)*4+3]>0;
  const positions=[],uvs=[];const z0=-layer.depth/2,z1=layer.depth/2;
  function edge(points,u,v){for(const n of [0,1,2,0,2,3]){positions.push(...points[n]);uvs.push(u,v)}}
  for(let y=0;y<texSize;y++)for(let x=0;x<texSize;x++)if(opaque(x,y)){
   const step=data.layout.cell;const X=(side==='left'?data.layout.root_x:-data.layout.root_x-data.layout.width)+x*step,Y=data.layout.center_y+(y-texSize/2)*step,U=(x+.5)/texSize,V=1-(y+.5)/texSize;
   if(!opaque(x-1,y))edge([[X,Y,z0],[X,Y,z1],[X,Y+step,z1],[X,Y+step,z0]],U,V);
   if(!opaque(x+1,y))edge([[X+step,Y,z1],[X+step,Y,z0],[X+step,Y+step,z0],[X+step,Y+step,z1]],U,V);
   if(!opaque(x,y-1))edge([[X,Y,z1],[X,Y,z0],[X+step,Y,z0],[X+step,Y,z1]],U,V);
   if(!opaque(x,y+1))edge([[X,Y+step,z0],[X,Y+step,z1],[X+step,Y+step,z1],[X+step,Y+step,z0]],U,V);
  }
  const edges=new THREE.BufferGeometry();edges.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));edges.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));edges.computeVertexNormals();group.add(new THREE.Mesh(edges,material));
  if(layer.frames>1)animations.push({ctx,tex,source,...layer});
 }
}
let playing=true,elapsed=0,lastTime=0,split=false;
document.querySelector('#pause').onclick=()=>{playing=!playing;document.querySelector('#pause').textContent=playing?'暂停动画':'播放动画'};
document.querySelector('#split').onclick=()=>{split=!split;for(const l of layerGroups)l.group.position.z=l.z+(split?(l.index-2)*6:0);azimuth=split?.85:-.18;document.querySelector('#split').textContent=split?'合拢五层':'拆开五层'};
const image=await new Promise((ok,bad)=>{let i=new Image();i.onload=()=>ok(i);i.onerror=bad;i.src=skinURL});
const skinMeshes=[];
function skinCube(bone,pos,size,u,v,inflate=0){let [w,h,d]=size;
 // 标准玩家UV盒展开：右、左、顶、底、背、前，保留外层透明像素。
 const rects=[[u+d+w,v+d,d,h],[u,v+d,d,h],[u+d,v,w,d],[u+d+w,v,w,d],[u+2*d+w,v+d,w,h],[u+d,v+d,w,h]];
 const materials=rects.map(([x,y,a,b],i)=>{let canvas=document.createElement('canvas');canvas.width=a*2;canvas.height=b*2;let ctx=canvas.getContext('2d');ctx.drawImage(image,x*2,y*2,a*2,b*2,0,0,a*2,b*2);let t=new THREE.CanvasTexture(canvas);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;t.colorSpace=THREE.SRGBColorSpace;
 return new THREE.MeshStandardMaterial({map:t,side:THREE.DoubleSide,alphaTest:.05,roughness:1})});
 let [x,y,z]=pos.map(n=>n-inflate),W=w+2*inflate,H=h+2*inflate,D=d+2*inflate;
 let planes=[[[x+W,y,z],[x+W,y,z+D],[x+W,y+H,z+D],[x+W,y+H,z]],[[x,y,z+D],[x,y,z],[x,y+H,z],[x,y+H,z+D]],[[x,y,z+D],[x+W,y,z+D],[x+W,y,z],[x,y,z]],[[x,y+H,z],[x+W,y+H,z],[x+W,y+H,z+D],[x,y+H,z+D]],[[x+W,y,z+D],[x,y,z+D],[x,y+H,z+D],[x+W,y+H,z+D]],[[x,y,z],[x+W,y,z],[x+W,y+H,z],[x,y+H,z]]];
 let vertices=[],uvs=[],uv=[[0,1],[1,1],[1,0],[0,0]],geo=new THREE.BufferGeometry();
 planes.forEach((p,i)=>{geo.addGroup(i*6,6,i);for(const j of [0,1,2,0,2,3]){vertices.push(...p[j]);uvs.push(...uv[j])}});
 geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));geo.computeVertexNormals();
 let mesh=new THREE.Mesh(geo,materials);bone.add(mesh);skinMeshes.push(mesh);
}
skinCube(bones.body,[-4,-8,-4],[8,8,8],0,0);skinCube(bones.body,[-4,-8,-4],[8,8,8],32,0,.5);
skinCube(bones.body,[-4,0,-2],[8,12,4],16,16);skinCube(bones.body,[-4,0,-2],[8,12,4],16,32,.25);
skinCube(bones.body,[-4,12,-2],[4,12,4],0,16);skinCube(bones.body,[-4,12,-2],[4,12,4],0,32,.25);
skinCube(bones.body,[0,12,-2],[4,12,4],16,48);skinCube(bones.body,[0,12,-2],[4,12,4],0,48,.25);
skinCube(bones.right_arm,[-2,-2,-2],[3,12,4],40,16);skinCube(bones.right_arm,[-2,-2,-2],[3,12,4],40,32,.25);
skinCube(bones.left_arm,[-1,-2,-2],[3,12,4],32,48);skinCube(bones.left_arm,[-1,-2,-2],[3,12,4],48,48,.25);
const grid=new THREE.GridHelper(160,40,0x615275,0x303047);grid.position.y=0;scene.add(grid);
let mode='all',azimuth=-.18,elevation=.12,distance=105,target=new THREE.Vector3(0,16,0),drag=null;
function choose(m){mode=m;skinMeshes.forEach(o=>o.visible=m==='all');for(const [k,o]of Object.entries(objects))o.visible=m==='all'||(m==='wings'?k.startsWith('wing'):k===m);
 let box=new THREE.Box3(new THREE.Vector3(-31,0,-5),new THREE.Vector3(31,40,5));target.copy(box.getCenter(new THREE.Vector3()));distance=box.getSize(new THREE.Vector3()).length()*1.8;azimuth=-.18;elevation=.12;
 document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===m));}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>choose(b.dataset.mode));document.querySelector('#front').onclick=()=>{azimuth=0;elevation=0};document.querySelector('#back').onclick=()=>{azimuth=Math.PI;elevation=0};
const canvas=renderer.domElement;canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY,button:e.button};canvas.setPointerCapture(e.pointerId)};canvas.onpointerup=()=>drag=null;canvas.onpointermove=e=>{if(!drag)return;let dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(drag.button===2){target.x-=dx*.06;target.y+=dy*.06}else{azimuth+=dx*.008;elevation=Math.max(-1.35,Math.min(1.35,elevation+dy*.008))}drag.x=e.clientX;drag.y=e.clientY};canvas.onwheel=e=>{e.preventDefault();distance=Math.max(12,Math.min(250,distance*Math.exp(e.deltaY*.001)))};
function resize(){renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix()}onresize=resize;resize();choose('all');
document.querySelector('#status').textContent='默认合拢 · 每侧五层 · '+data.star_count_per_side+' 星点像素 · 4.8秒循环';
function frame(t){if(playing)elapsed+=Math.min(100,t-lastTime);lastTime=t;
objects.wing_left.rotation.y=.10+.035*Math.sin(elapsed*.0009);objects.wing_right.rotation.y=-objects.wing_left.rotation.y;
for(const a of animations){const f=elapsed/(a.ticks*50),n=Math.floor(f)%a.frames,next=(n+1)%a.frames,mix=f-Math.floor(f);a.ctx.clearRect(0,0,texSize,texSize);a.ctx.globalCompositeOperation='source-over';a.ctx.globalAlpha=1-mix;a.ctx.drawImage(a.source,0,n*texSize,texSize,texSize,0,0,texSize,texSize);a.ctx.globalCompositeOperation='lighter';a.ctx.globalAlpha=mix;a.ctx.drawImage(a.source,0,next*texSize,texSize,texSize,0,0,texSize,texSize);a.ctx.globalAlpha=1;a.ctx.globalCompositeOperation='source-over';a.tex.needsUpdate=true;}
camera.position.set(target.x+Math.sin(azimuth)*Math.cos(elevation)*distance,target.y+Math.sin(elevation)*distance,target.z-Math.cos(azimuth)*Math.cos(elevation)*distance);camera.lookAt(target);renderer.render(scene,camera);requestAnimationFrame(frame)}requestAnimationFrame(frame);
</script></html>'''
html=html.replace('__THREE__',three).replace('__DATA__',json.dumps(geometry)).replace('__SKIN__',skin)
(out/'琪亚娜模型预览.html').write_text(html,encoding='utf-8')
(ROOT/'logs/kiana-r145/viewer-check.mjs').write_text(re.search(r'<script type="module">(.*?)</script>',html,re.S).group(1),encoding='utf-8')
print(out/'琪亚娜模型预览.html')
