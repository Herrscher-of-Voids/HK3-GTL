/** I34树影研究：曲线光脉、透明精灵和世界节点，不创建任何实体方块。 */
import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';
import {EffectComposer} from 'effect-composer';
import {RenderPass} from 'render-pass';
import {UnrealBloomPass} from 'bloom-pass';
import {OutputPass} from 'output-pass';

const host=document.querySelector('#scene'),notice=document.querySelector('#notice');
try {
const scene=new THREE.Scene();
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));
renderer.setClearColor(0x03070c,0);renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.13;host.append(renderer.domElement);
const camera=new THREE.PerspectiveCamera(39,1,.1,1800);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.07;controls.minDistance=105;controls.maxDistance=470;
controls.maxPolarAngle=Math.PI*.75;controls.autoRotateSpeed=.38;controls.autoRotate=true;
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
const bloom=new UnrealBloomPass(new THREE.Vector2(100,100),.62,.5,.37);
composer.addPass(bloom);composer.addPass(new OutputPass());
const tree=new THREE.Group();scene.add(tree);
const V=(x,y,z)=>new THREE.Vector3(x,y,z);
let seed=341027;
function random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
const range=(a,b)=>a+(b-a)*random();
const positions=[],colors=[],curves=[],tips=[],dust=[],dustSizes=[],dustSeeds=[];
const pale=new THREE.Color('#fff1c3'),gold=new THREE.Color('#d7a956');
function trace(curve,depth=0,root=false,fiber=false){
  const length=curve.getLength(),steps=Math.max(10,Math.ceil(length*1.7));
  curves.push({curve,depth,root});
  for(let i=0;i<steps;i++){
    const a=curve.getPoint(i/steps),b=curve.getPoint((i+1)/steps);
    positions.push(...a.toArray(),...b.toArray());
    const color=gold.clone().lerp(pale,root?.4:Math.max(.05,.85-depth*.13));
    color.multiplyScalar((fiber?.36:1)*Math.max(.22,1.25-depth*.14));
    colors.push(...color.toArray(),...color.toArray());
    if(i%(fiber?10:2)===0){dust.push(...a.toArray());dustSizes.push(fiber?range(.3,.6):root?range(.65,1.1):range(.5,1.7));dustSeeds.push(random()*6.28);}
  }
}
function fork(start,direction,length,depth,width=1){
  const end=start.clone().addScaledVector(direction,length);
  const bend=V(range(-1,1),range(-.15,.8),range(-1,1)).multiplyScalar(length*.19);
  const p1=start.clone().addScaledVector(direction,length*.32).add(bend);
  const p2=end.clone().addScaledVector(direction,-length*.27).add(bend.clone().multiplyScalar(.6));
  const curve=new THREE.CubicBezierCurve3(start,p1,p2,end);trace(curve,depth);
  if(depth>=5||length<3.8){tips.push(end);return;}
  const branches=depth<2?3:2;
  for(let i=0;i<branches;i++){
    const t=i===0?1:range(.66,.91),at=curve.getPoint(t),tangent=curve.getTangent(t);
    const azimuth=range(-1.1,1.1)+(i-(branches-1)/2)*.56;
    const child=tangent.clone().applyAxisAngle(V(0,1,0),azimuth);
    child.y+=range(-.08,.32);child.x+=range(-.28,.28);child.z+=range(-.28,.28);child.normalize();
    fork(at,child,length*range(.57,.76),depth+1,width*.7);
  }
}

// 同轴光丝形成有纵深的树干，冠部各枝与树干上的实际采样点相接。
const spine=new THREE.CubicBezierCurve3(V(-5,-5,0),V(9,25,-8),V(-9,51,7),V(3,79,-1));
for(let strand=0;strand<42;strand++){
  const coords=[];
  for(let k=0;k<=100;k++){
    const t=k/100,p=spine.getPoint(t),r=(1-t)*range(2.1,4.9)+.15;
    const angle=strand*2.39996+t*4.3;
    p.add(V(Math.cos(angle)*r,0,Math.sin(angle)*r));coords.push(p);
  }
  trace(new THREE.CatmullRomCurve3(coords),0,false,true);
}
const major=[];
for(let i=0;i<11;i++){
  const t=.28+i*.061,start=spine.getPoint(t),angle=i*2.399963+range(-.3,.3);
  const direction=V(Math.cos(angle)*range(.65,.95),range(.45,.9),Math.sin(angle)*range(.55,.85)).normalize();
  major.push({start,direction,length:range(40,61)*(1-.19*t)});
}
for(const branch of major)fork(branch.start,branch.direction,branch.length,0);
fork(spine.getPoint(1),V(.12,1,.03).normalize(),25,1);
// 根系像跨维度的金色流线，在观测平面下散开；不绘制土壤或植物叶片。
for(let i=0;i<20;i++){
  const angle=i*Math.PI*2/20+range(-.16,.16),r=range(24,53);
  const start=spine.getPoint(range(0,.04));
  const end=V(Math.cos(angle)*r,range(-26,-17),Math.sin(angle)*r*.73);
  const curve=new THREE.CubicBezierCurve3(start,V(start.x+Math.cos(angle)*8,-16,Math.sin(angle)*8),
    V(end.x*.66,-20,end.z*.66),end);trace(curve,1,true);
  for(let j=0;j<2;j++){
    const at=curve.getPoint(.65+j*.15);
    trace(new THREE.CubicBezierCurve3(at,at.clone().add(V(4,-3,2)),end.clone().add(V(5,-2,4)),end.clone().add(V(9,-3,8))),3,true);
  }
}
if(!positions.every(Number.isFinite)||curves.length<500||tips.length<200)throw new Error('树影几何自检失败');
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.computeBoundingSphere();
const lineMaterial=new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.55,depthWrite:false,blending:THREE.AdditiveBlending});
tree.add(new THREE.LineSegments(geometry,lineMaterial));

const uniforms={uTime:{value:0},uPower:{value:1},uPixel:{value:renderer.getPixelRatio()}};
const pointVertex=`attribute float aSize;attribute float aSeed;varying float vSeed;
uniform float uTime;uniform float uPower;uniform float uPixel;
void main(){vSeed=aSeed;vec4 p=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*p;
gl_PointSize=clamp(aSize*520.*uPixel/max(1.,-p.z),1.,26.);}`;
const pointFragment=`uniform float uTime;uniform float uPower;varying float vSeed;
void main(){float r=length(gl_PointCoord-.5)*2.;if(r>1.)discard;
float glow=exp(-r*r*7.5),core=exp(-r*r*70.);float pulse=.72+.28*sin(uTime*.8+vSeed);
vec3 color=mix(vec3(1.,.56,.16),vec3(1.,.95,.75),core);
gl_FragColor=vec4(color,(glow*.35+core*.8)*pulse*uPower);}`;
function makePoints(coords,sizes,seeds){
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));
  g.setAttribute('aSize',new THREE.Float32BufferAttribute(sizes,1));g.setAttribute('aSeed',new THREE.Float32BufferAttribute(seeds,1));
  const material=new THREE.ShaderMaterial({uniforms,vertexShader:pointVertex,fragmentShader:pointFragment,
    transparent:true,depthWrite:false,blending:THREE.AdditiveBlending});
  const points=new THREE.Points(g,material);tree.add(points);return points;
}
makePoints(dust,dustSizes,dustSeeds);
const nodeCoords=[],nodeSizes=[],nodeSeeds=[];
for(let i=0;i<tips.length;i++)if(i%3===0){nodeCoords.push(...tips[i].toArray());nodeSizes.push(range(5,8));nodeSeeds.push(random()*6.28);}
makePoints(nodeCoords,nodeSizes,nodeSeeds);

const flows=Array.from({length:720},()=>({branch:curves[Math.floor(random()*curves.length)],offset:random(),speed:range(.035,.1)}));
const flow=makePoints(new Float32Array(flows.length*3),flows.map(()=>range(1.5,3.4)),flows.map(()=>random()*6.28));
flow.frustumCulled=false;
function glowTexture(){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=128;
  const c=canvas.getContext('2d'),gradient=c.createRadialGradient(64,64,0,64,64,64);
  gradient.addColorStop(0,'rgba(255,247,204,.65)');gradient.addColorStop(.15,'rgba(255,195,82,.2)');gradient.addColorStop(1,'rgba(255,167,47,0)');
  c.fillStyle=gradient;c.fillRect(0,0,128,128);return new THREE.CanvasTexture(canvas);
}
const haloMap=glowTexture(),halos=new THREE.Group();tree.add(halos);
for(let i=0;i<9;i++){
  const p=spine.getPoint(i/9),material=new THREE.SpriteMaterial({map:haloMap,color:0xffd9a0,transparent:true,
    opacity:.23,depthWrite:false,blending:THREE.AdditiveBlending});
  const sprite=new THREE.Sprite(material);sprite.position.copy(p);sprite.scale.set(19-i*.6,25,1);halos.add(sprite);
}

// 细薄观测环只作投影的坐标参照，树影本身保持主视觉。
const reference=new THREE.Group();scene.add(reference);
for(const [r,y] of [[30,-7],[38,-7.1],[48,-7.2]]){
  const pts=Array.from({length:161},(_,i)=>V(Math.cos(i*Math.PI/80)*r,y,Math.sin(i*Math.PI/80)*r));
  const ring=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts),
    new THREE.LineBasicMaterial({color:0x8399aa,transparent:true,opacity:r===30?.22:.08,depthWrite:false}));reference.add(ring);
}
for(let i=0;i<64;i++){
  const a=i*Math.PI/32,r=38;
  const g=new THREE.BufferGeometry().setFromPoints([V(Math.cos(a)*r,-7,Math.sin(a)*r),V(Math.cos(a)*(r+(i%4===0?2:1)),-7,Math.sin(a)*(r+(i%4===0?2:1)))]);
  reference.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:0xaeb6b3,transparent:true,opacity:.2})));
}
const starPositions=[],starColors=[];
for(let i=0;i<1700;i++){
  const p=V(range(-460,460),range(-250,390),range(-430,-150));starPositions.push(...p.toArray());
  const color=new THREE.Color(i%13===0?'#dbb983':'#8192a5').multiplyScalar(range(.15,.55));starColors.push(...color.toArray());
}
const starGeo=new THREE.BufferGeometry();starGeo.setAttribute('position',new THREE.Float32BufferAttribute(starPositions,3));
starGeo.setAttribute('color',new THREE.Float32BufferAttribute(starColors,3));
scene.add(new THREE.Points(starGeo,new THREE.PointsMaterial({size:.7,vertexColors:true,transparent:true,opacity:.6,sizeAttenuation:true,depthWrite:false})));

let mode='running',paused=false,elapsed=0,last=performance.now(),speed=1,power=1,currentView='full';
const modeNames={running:'观测中',idle:'待机',off:'投影关闭'};
function setMode(value){
  mode=value;document.querySelectorAll('[data-mode]').forEach(button=>{button.classList.toggle('active',button.dataset.mode===value);button.setAttribute('aria-pressed',String(button.dataset.mode===value));});
  document.querySelector('#state').textContent=modeNames[value];
  document.querySelector('#state-dot').dataset.mode=value;
}
function view(name){
  geometry.computeBoundingBox();const bounds=geometry.boundingBox,size=bounds.getSize(V(0,0,0)),center=bounds.getCenter(V(0,0,0));
  const fullDistance=Math.max(size.y*.68,size.x*.65/camera.aspect,size.z*.65/camera.aspect)/Math.tan(THREE.MathUtils.degToRad(camera.fov/2));
  controls.maxDistance=Math.max(470,fullDistance*1.6);
  const direction=V(.48,.15,.86).normalize();
  const views={full:[center.clone().addScaledVector(direction,fullDistance),center],crown:[V(95,111,151),V(0,86,0)],roots:[V(87,19,125),V(0,-2,0)]};
  currentView=name;
  camera.position.copy(views[name][0]);controls.target.copy(views[name][1]);controls.update();
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('selected',b.dataset.view===name));
}
document.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>setMode(button.dataset.mode));
document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>view(button.dataset.view));
document.querySelector('#pause').onclick=()=>{
  paused=!paused;document.querySelector('#pause').textContent=paused?'继续动画':'暂停动画';
  document.querySelector('#pause').setAttribute('aria-pressed',String(paused));
};
document.querySelector('#orbit').onclick=()=>{
  controls.autoRotate=!controls.autoRotate;document.querySelector('#orbit').classList.toggle('selected',controls.autoRotate);
  document.querySelector('#orbit').setAttribute('aria-pressed',String(controls.autoRotate));
};
document.querySelector('#speed').oninput=event=>{speed=Number(event.target.value);document.querySelector('#speedValue').textContent=speed.toFixed(1)+'×';};
document.querySelector('#bloom').onclick=()=>{bloom.enabled=!bloom.enabled;document.querySelector('#bloom').classList.toggle('selected',bloom.enabled);document.querySelector('#bloom').setAttribute('aria-pressed',String(bloom.enabled));};
document.querySelector('#save').onclick=()=>{
  composer.render();const anchor=document.createElement('a');anchor.download='I34_虚数之树观测投影.png';anchor.href=renderer.domElement.toDataURL('image/png');anchor.click();
};
function resize(){
  const w=host.clientWidth,h=host.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();
  renderer.setSize(w,h);composer.setSize(w,h);
  view(currentView);
}
new ResizeObserver(resize).observe(host);resize();view('full');setMode('running');
document.querySelector('#loading').hidden=true;notice.textContent='投影效果候选 · 不含建筑结构 · 尚未接入游戏';
document.querySelector('#scene').setAttribute('aria-label','金白色虚数之树动态投影，金色光脉与世界节点分布在树冠和根系。');
const movingPosition=flow.geometry.attributes.position;
function frame(now){
  const dt=Math.min((now-last)/1000,.08);last=now;
  if(!document.hidden){
    if(!paused)elapsed+=dt*speed;
    const target=mode==='running'?1:mode==='idle'?.22:0;power+=Math.min(1,dt*3)*(target-power);
    uniforms.uTime.value=elapsed;uniforms.uPower.value=power;
    lineMaterial.opacity=.53*power;tree.visible=power>.001;
    halos.children.forEach((sprite,i)=>sprite.material.opacity=power*(.075+Math.sin(elapsed*.6+i)*.009));
    flow.visible=mode==='running';
    if(!paused&&mode==='running')for(let i=0;i<flows.length;i++){
      const item=flows[i],t=(elapsed*item.speed+item.offset)%1,p=item.branch.curve.getPoint(t);
      movingPosition.setXYZ(i,p.x,p.y,p.z);
    }
    movingPosition.needsUpdate=true;
    const orbit=controls.autoRotate;controls.autoRotate=orbit&&!paused;controls.update(dt);controls.autoRotate=orbit;
    composer.render();
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
renderer.domElement.addEventListener('webglcontextlost',event=>{event.preventDefault();notice.textContent='图形上下文已暂停，请刷新页面恢复。';});
} catch(error){
  document.querySelector('#loading').textContent='预览加载失败：'+error.message;
  notice.textContent='请使用支持WebGL的常规浏览器打开此HTML。';console.error(error);
}
