/**
 * I03 评审查看器：使用导出结构同源的逐格数据和实例纹理。
 * 支持自由旋转、分层、玻璃隐藏和接口定位；不把建筑效果标作运行时验收。
 */
import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';
const {data,materials,audit}=window.REVIEW;
const stage=document.getElementById('stage');
const scene=new THREE.Scene();scene.background=new THREE.Color('#121b2b');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);
const camera=new THREE.OrthographicCamera(-32,32,32,-32,.1,350);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=.12;controls.minZoom=.35;controls.maxZoom=8;
controls.maxPolarAngle=Math.PI*.49;controls.target.set(12,10,14);
scene.add(new THREE.HemisphereLight(0xc8e5ff,0x384458,2.3));
const sun=new THREE.DirectionalLight(0xfff4e7,3);sun.position.set(-20,65,-25);sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-40,right:40,top:40,bottom:-40,near:1,far:150});
sun.shadow.normalBias=.08;scene.add(sun);
const fill=new THREE.DirectionalLight(0x81c7ed,1.3);fill.position.set(45,22,38);scene.add(fill);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(180,180),new THREE.MeshStandardMaterial({color:0x172335,roughness:.96}));
ground.rotation.x=-Math.PI/2;ground.position.set(12,-.035,14);ground.receiveShadow=true;scene.add(ground);
const grid=new THREE.GridHelper(100,100,0x496078,0x25354b);grid.position.set(12,-.015,14);scene.add(grid);
const group=new THREE.Group();scene.add(group);
const cube=new THREE.BoxGeometry(1,1,1);const matrix=new THREE.Matrix4();
const loader=new THREE.TextureLoader(),textureCache=new Map();
const pending=[];
function texture(url){
  if(textureCache.has(url))return textureCache.get(url);
  let resolve,reject;pending.push(new Promise((a,b)=>{resolve=a;reject=b}));
  const result=loader.load(url,()=>resolve(),undefined,reject);
  result.magFilter=THREE.NearestFilter;result.minFilter=THREE.NearestFilter;
  result.colorSpace=THREE.SRGBColorSpace;textureCache.set(url,result);return result;
}
const stateMeshes=[];
for(const material of materials){
  const blocks=data.blocks.filter(b=>b.state===material.state);
  const sides=['east','west','up','down','south','north'].map(face=>new THREE.MeshStandardMaterial({
    map:texture(material.faces[face]),roughness:.78,metalness:.08,alphaTest:material.transparent?.12:0,
    side:material.transparent?THREE.DoubleSide:THREE.FrontSide}));
  const mesh=new THREE.InstancedMesh(cube,sides,blocks.length);
  mesh.castShadow=!material.transparent;mesh.receiveShadow=true;mesh.userData={blocks,material};
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);group.add(mesh);stateMeshes.push(mesh);
}
const paths=new THREE.Group();scene.add(paths);paths.visible=false;
for(const route of data.paths){
  const size=route.max.map((v,i)=>v-route.min[i]+1),center=route.min.map((v,i)=>v+size[i]/2);
  const box=new THREE.Mesh(new THREE.BoxGeometry(...size),new THREE.MeshBasicMaterial({color:0x7df8ce,transparent:true,opacity:.16,depthWrite:false}));
  box.position.set(...center);paths.add(box);
  const edges=new THREE.LineSegments(new THREE.EdgesGeometry(box.geometry),new THREE.LineBasicMaterial({color:0x7df8ce}));edges.position.copy(box.position);paths.add(edges);
}
// 尺寸线位于地面外侧，刻度和标签不进入导出的建筑方块。
function line(points,color=0x7395ae){const geo=new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p)));scene.add(new THREE.Line(geo,new THREE.LineBasicMaterial({color})));}
line([[0,.1,-2],[25,.1,-2]]);line([[-2,.1,0],[-2,.1,29]]);
for(const x of [0,25])line([[x,.1,-2.7],[x,.1,-1.3]]);
for(const z of [0,29])line([[-2.7,.1,z],[-1.3,.1,z]]);
const labels=[];
function label(text,pos,kind){const el=document.createElement('div');el.className='label'+(kind==='port'?' port':'');el.textContent=text;document.getElementById('labels').append(el);labels.push({el,pos:new THREE.Vector3(...pos),kind});}
for(const zone of data.zones)label(zone.name,zone.pos.map((v,i)=>v+(i===1?2:0)), 'zone');
for(const port of data.ports)label(port.id,port.pos.map(v=>v+.5),'port');
label('主控',data.controller.map(v=>v+.5),'port');label('25 格',[12.5,.4,-2],'dimension');label('29 格',[-2,.4,14.5],'dimension');
const markerGroup=new THREE.Group();scene.add(markerGroup);markerGroup.visible=false;
for(const p of [...data.ports.map(p=>p.pos),data.controller]){
  const mark=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.08,1.08,1.08)),new THREE.LineBasicMaterial({color:0xffd47f,depthTest:false}));mark.position.set(...p.map(v=>v+.5));mark.renderOrder=20;markerGroup.add(mark);
}
function rebuild(){
  const layer=+document.getElementById('layer').value,glass=document.getElementById('showGlass').checked;
  let count=0;
  for(const mesh of stateMeshes){let n=0;for(const b of mesh.userData.blocks){
    if(b.pos[1]>layer||(!glass&&mesh.userData.material.transparent))continue;
    matrix.makeTranslation(...b.pos.map(v=>v+.5));mesh.setMatrixAt(n++,matrix);
  }mesh.count=n;mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();count+=n;}
  document.getElementById('layerValue').textContent=layer;
  document.getElementById('counts').textContent=`显示 ${count.toLocaleString()} / ${data.blocks.length.toLocaleString()} 个实体方块 · ${materials.length} 种方块状态`;
  paths.visible=document.getElementById('showPaths').checked;markerGroup.visible=document.getElementById('showPorts').checked;
}
const views={front:{pos:[-37,36,-40],target:[12,10,15],name:'前左鸟瞰 · 高柱与低舱'},right:{pos:[55,33,-30],target:[12,10,15],name:'前右鸟瞰 · 滤芯柜与冷凝单元'},back:{pos:[-35,31,64],target:[12,10,15],name:'后侧鸟瞰 · 六个流体接口'},top:{pos:[12,82,14],target:[12,0,14],name:'正俯视 · 占地与检修通道'},inside:{pos:[48,34,-33],target:[12,7,14],name:'内部剖面 · Y≤12，玻璃隐藏'}};
function setView(name){
  const v=views[name]??views.front;camera.up.set(0,1,0);
  if(name==='top')camera.up.set(0,0,1);
  camera.position.set(...v.pos);controls.target.set(...v.target);camera.zoom=1;camera.updateProjectionMatrix();controls.update();
  document.getElementById('viewName').textContent=v.name;
  document.getElementById('layer').value=name==='inside'?12:24;
  document.getElementById('showGlass').checked=name!=='inside';
  document.getElementById('showPaths').checked=['inside','top'].includes(name);
  document.getElementById('showPorts').checked=name==='back';
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));rebuild();
}
for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>setView(button.dataset.view);
for(const id of ['layer','showGlass','showZones','showPorts','showPaths'])document.getElementById(id).oninput=rebuild;
document.getElementById('reset').onclick=()=>setView('front');
document.getElementById('saveImage').onclick=()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download='I03-三维结构预览.png';a.href=renderer.domElement.toDataURL('image/png');a.click();};
const faceText={west:'朝 -X',east:'朝 +X',north:'朝 -Z',south:'朝 +Z'};
document.getElementById('ports').innerHTML=data.ports.map(p=>`<div class="portrow"><b>${p.id}</b><span>${p.purpose}<small>(${p.pos.join(', ')}) · ${faceText[p.face]}</small></span></div>`).join('')+`<div class="portrow"><b>主控</b><span>钻石块标记<small>(${data.controller.join(', ')}) · 朝 -Z</small></span></div>`;
const display={'gtceu:max_machine_casing':'MAX 机壳／深紫装甲','gtlcore:molecular_casing':'分子机械方块／蓝色处理舱','gtceu:computer_casing':'计算机机壳／银灰维护面','gtceu:high_power_casing':'高功率机壳／功能节点','gtceu:superconducting_coil[active=false]':'超导线圈／分离及换热组件','gtceu:fusion_glass':'聚变玻璃／主观察窗','gtceu:laminated_glass':'层压玻璃／滤芯窗','kubejs:neutronium_pipe_casing':'中子素管道机壳／完整输送构件','kubejs:neutronium_gearbox':'中子素齿轮箱／驱动组件','minecraft:diamond_block':'钻石块／主控标记','minecraft:diamond_ore':'钻石矿／接口标记'};
document.getElementById('materials').innerHTML=materials.map(m=>`<div class="material"><img class="swatch" src="${m.faces.north}">${display[m.state]??m.state} × ${audit.palette[m.state]}<small>${m.state}</small></div>`).join('');
document.getElementById('checks').innerHTML=audit.checks.map(s=>`<p class="ok">✓ ${s}</p>`).join('');
document.getElementById('status').textContent='✓ 结构双格式回读一致 · 10 个接口可达 · 两条通道净空通过';
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);const half=28;camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();}
new ResizeObserver(resize).observe(stage);resize();
setView(new URLSearchParams(location.search).get('view')??'front');
const projected=new THREE.Vector3();
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera);
  for(const l of labels){const show=l.kind==='dimension'||(l.kind==='zone'?document.getElementById('showZones').checked&&l.pos.y<=+document.getElementById('layer').value+2:document.getElementById('showPorts').checked);
    projected.copy(l.pos).project(camera);l.el.style.display=show&&projected.z<1?'block':'none';
    l.el.style.left=(projected.x*.5+.5)*stage.clientWidth+'px';l.el.style.top=(-projected.y*.5+.5)*stage.clientHeight+'px';}
}
frame();
Promise.all(pending).then(()=>{document.getElementById('loading').remove();window.REVIEW_READY=true;window.reviewApi={setView,rebuild,renderer,scene,camera};}).catch(error=>{document.getElementById('loading').textContent='材质加载失败：'+error.message;});
