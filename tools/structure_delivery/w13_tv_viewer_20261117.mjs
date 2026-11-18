import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  let bytes=Uint8Array.from(atob(window.W13_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W13_VOXEL_PAYLOAD=null;bytes=null;
  const stage=document.getElementById('stage'),modelById=new Map(data.models.map(m=>[m.id,m]));
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#17141b');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,1.1));
  const sun=new THREE.DirectionalLight(0xffffff,1.25);sun.position.set(-450,850,800);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xffffff,.6);fill.position.set(500,150,-650);scene.add(fill);
  const camera=new THREE.OrthographicCamera(-750,750,750,-750,.1,12000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map();
  const textures=await Promise.all(materials.map(async info=>{
    const maps={};await Promise.all(Object.entries(info.faces).map(async([face,url])=>{
      if(!textureCache.has(url))textureCache.set(url,loader.loadAsync(url));
      const texture=await textureCache.get(url);texture.colorSpace=THREE.SRGBColorSpace;
      texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestMipmapLinearFilter;
      texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.generateMipmaps=true;
      texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());maps[face]=texture;
    }));return maps;
  }));
  const faceNames=['east','west','south','north','down','up'];
  const normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],meshes=[],visibleMaterials=new Set(materials.map((_,i)=>i)),hiddenModels=new Set();
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  let renderedQuads=0,frames=0;
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.position.set(...part.origin);
    group.userData={modelId:part.modelId,bounds:new THREE.Box3(new THREE.Vector3(...part.origin),new THREE.Vector3(...part.origin).add(new THREE.Vector3(...part.size)))};
    scene.add(group);groups.push(group);const [w,,d]=part.size;
    for(let material=0;material<materials.length;material++)for(let face=0;face<6;face++){
      const starts=part.starts[material][face],lengths=part.lengths[material][face],spans=part.spans[material][face];
      if(!starts.length)continue;
      const positions=new Float32Array(starts.length*12),ns=new Float32Array(starts.length*12),uvs=new Float32Array(starts.length*8),indices=new Uint32Array(starts.length*6);
      const axis=face<2?2:0,cross=face<4?1:2;
      starts.forEach((index,j)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d],repeat=lengths[j],span=spans[j];
        for(let v=0;v<4;v++){
          const corner=corners[face][v];
          for(let k=0;k<3;k++){positions[j*12+v*3+k]=start[k]+corner[k]*(k===axis?repeat:k===cross?span:1);ns[j*12+v*3+k]=normals[face][k];}
          uvs[j*8+v*2]=corner[axis]*repeat;uvs[j*8+v*2+1]=corner[cross]*span;
        }indices.set([j*4,j*4+1,j*4+2,j*4,j*4+2,j*4+3],j*6);
      });
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));
      geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingSphere();
      const screen=part.modelId==='screen',key=`${material}:${face}:${screen}`;
      if(!materialCache.has(key)){
        const info=materials[material],emissive=screen||info.emissive;
        const mat=new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.54:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:emissive?0xffffff:0,emissiveMap:textures[material][faceNames[face]],emissiveIntensity:screen?.17:info.emissive?.22:0});
        mat.userData.screen=screen;materialCache.set(key,mat);
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=material;group.add(mesh);meshes.push(mesh);renderedQuads+=starts.length;
    }
    delete part.starts;delete part.lengths;delete part.spans;
    document.getElementById('loading').textContent=`完整方块表面 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const gridSize=Math.ceil(Math.max(data.sizeXYZ[0],data.sizeXYZ[2])/16)*16;
  const grid=new THREE.GridHelper(gridSize,gridSize/16,0x7e5c74,0x38323d);grid.position.set((data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]-.5,(data.bounds.min[2]+data.bounds.max[2]+1)/2);grid.visible=false;scene.add(grid);
  const axes=new THREE.AxesHelper(32);axes.visible=false;scene.add(axes);
  const modelBlocks=new Map(data.models.map(model=>[model.id,parts.filter(part=>part.modelId===model.id).reduce((sum,part)=>sum+part.blocks,0)]));
  const glitchGeometry=new THREE.BoxGeometry(1,1,1),glitchMaterial=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.35,depthWrite:false,clippingPlanes:[plane]});
  const glitch=new THREE.InstancedMesh(glitchGeometry,glitchMaterial,18),dummy=new THREE.Object3D(),eye=data.effects.eye_center,radius=data.effects.eye_radius;
  glitch.instanceMatrix.setUsage(THREE.DynamicDrawUsage);glitch.frustumCulled=false;scene.add(glitch);
  for(let i=0;i<18;i++)glitch.setColorAt(i,new THREE.Color(i%3?0xff53b2:0xffc7e8));
  let activeModel='all',activeView='oblique',axis='y',disposed=false,fitBox=new THREE.Box3(),fitZoom=1,mode='idle',paused=false,time=0;
  const layerInput=document.getElementById('layer');let layer=0;
  const basicViews={oblique:{label:'整体斜视',direction:[-.8,.5,1.35]},front:{label:'正面',direction:[0,.08,1]},back:{label:'背面',direction:[0,.2,-1]},left:{label:'左侧',direction:[-1,.15,0]},right:{label:'右侧',direction:[1,.15,0]},top:{label:'俯视',direction:[0,1,0]}};
  function updateAnimation(){
    const enabled=document.getElementById('effects').checked,screenVisible=(activeModel==='all'||activeModel==='screen')&&!hiddenModels.has('screen');
    glitch.visible=enabled&&mode==='work'&&screenVisible;
    materialCache.forEach(material=>{if(material.userData.screen)material.emissiveIntensity=enabled&&mode==='work'?.25+Math.sin(time*1.35)*.07:.17;});
    const step=Math.floor(time*5);
    for(let i=0;i<18;i++){
      const y=Math.floor((((i*37+step*29)%(radius*2))-radius)*.87),span=Math.floor(Math.sqrt(radius*radius-y*y)),width=3+(i*11+step*7)%27;
      const x=Math.floor(-span+width/2+((i*73+step*53)%(2*span-width)));
      dummy.position.set(eye[0]+x,eye[1]+y,eye[2]+1);dummy.scale.set(width,i%4===0?2:1,1);dummy.updateMatrix();glitch.setMatrixAt(i,dummy.matrix);
    }glitch.instanceMatrix.needsUpdate=true;
  }
  const modelBounds=()=>{const bounds=new THREE.Box3();groups.filter(group=>activeModel==='all'||group.userData.modelId===activeModel).forEach(group=>bounds.union(group.userData.bounds));return bounds;};
  function draw(){if(disposed)return;updateAnimation();camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function views(){return {...basicViews,...data.views,...(activeModel==='all'?{}:modelById.get(activeModel).views)};}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));}
    return .86/limit;
  }
  function setView(name){
    activeView=name;const preset=views()[name],bounds=modelBounds(),target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3()),direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(2500));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  }
  function updateViewButtons(){
    const host=document.getElementById('views');host.replaceChildren();for(const [name,preset] of Object.entries(views())){const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);}
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    document.getElementById('modelName').textContent=all?data.title:model.title;
    document.getElementById('actualSize').textContent=`宽 ${data.sizeXYZ[0]} × 深 ${data.sizeXYZ[2]} × 高 ${data.sizeXYZ[1]} 格`;
    document.getElementById('modelStats').textContent=`${(all?data.total_blocks:modelBlocks.get(activeModel)).toLocaleString()} 个实体方块 · 当前宽${size[0]}×深${size[2]}×高${size[1]}`;
    const features=document.getElementById('features');features.replaceChildren();for(const text of all?data.design:model.features){const item=document.createElement('li');item.textContent=text;features.append(item);}axes.position.copy(bounds.min);
  }
  function setLayer(value){layer=value;layerInput.value=value;const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();}
  function setAxis(value){axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(axis),bounds=modelBounds();layerInput.min=Math.floor(bounds.min.getComponent(index));layerInput.max=Math.ceil(bounds.max.getComponent(index))-1;setLayer(+layerInput.max);}
  function applyGroups(){groups.forEach(group=>group.visible=(activeModel==='all'||group.userData.modelId===activeModel)&&!hiddenModels.has(group.userData.modelId));}
  function setModel(id){activeModel=id;if(id!=='all'){hiddenModels.delete(id);document.querySelector(`[data-group="${id}"]`).checked=true;}applyGroups();document.querySelectorAll('[data-model]').forEach(button=>button.classList.toggle('active',button.dataset.model===id));updateDetails();updateViewButtons();setAxis(axis);setView('oblique');}
  function setMode(value){mode=value;document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;const button=document.getElementById('pause');button.textContent=paused?'继续':'暂停';button.setAttribute('aria-pressed',String(paused));draw();}
  function setTime(value){time=value;const input=document.getElementById('time');input.max=Math.max(60,Math.ceil(time));input.value=time;document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();}
  for(const model of [{id:'all',title:'整体'},...data.models]){const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.title;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);}
  for(const model of data.models){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.group=model.id;label.append(input,' '+model.title);input.onchange=()=>{input.checked?hiddenModels.delete(model.id):hiddenModels.add(model.id);applyGroups();draw();};document.getElementById('groups').append(label);}
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;input.type='checkbox';input.checked=true;code.textContent=info.state;
    input.onchange=()=>{input.checked?visibleMaterials.add(index):visibleMaterials.delete(index);meshes.forEach(mesh=>mesh.visible=visibleMaterials.has(mesh.userData.material));draw();};label.append(input,code);document.getElementById('materials').append(label);
  });
  document.getElementById('materialSearch').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(query));};
  document.getElementById('axis').onchange=event=>setAxis(event.target.value);layerInput.oninput=event=>setLayer(+event.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};document.getElementById('axes').onchange=event=>{axes.visible=event.target.checked;draw();};
  document.getElementById('effects').onchange=draw;document.getElementById('mode').onchange=event=>setMode(event.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);document.getElementById('timeZero').onclick=()=>setTime(0);document.getElementById('time').oninput=event=>setTime(+event.target.value);
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download=`W13-TV-${activeModel}-${activeView}-T1.png`;link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();controls.addEventListener('change',draw);
  function resize(){const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();if(window.W13_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}}
  const observer=new ResizeObserver(resize);observer.observe(stage);let last=performance.now();
  function animate(now){if(disposed)return;const elapsed=Math.min((now-last)/1000,.1);last=now;if(!paused&&mode==='work')setTime(time+elapsed);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({activeModel,activeView,axis,layer,frames,renderedQuads,mode,paused,time,animationWebOnly:true,glitchVisible:glitch.visible,hiddenModels:[...hiddenModels],models:data.models.map(model=>({id:model.id,blocks:modelBlocks.get(model.id)})),visibleParts:groups.filter(group=>group.visible).map(group=>group.name),camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom}});
  window.W13Viewer={setModel,setView,setAxis,setLayer,setMode,setPaused,setTime,snapshot,availableViews:()=>Object.keys(views())};
  document.getElementById('stats').textContent=`${parts.length} 件完整构件 · ${renderedQuads.toLocaleString()} 个合并表面 · ${materials.length} 项原生材质`;
  if(data.nbt_file)document.getElementById('nbtLink').href=data.nbt_file;
  document.getElementById('loading').remove();resize();setModel('all');setTime(0);window.W13_READY=true;
  window.addEventListener('pagehide',()=>{disposed=true;observer.disconnect();controls.dispose();meshes.forEach(mesh=>mesh.geometry.dispose());materialCache.forEach(material=>material.dispose());textureCache.forEach(async value=>(await value).dispose());grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();glitchGeometry.dispose();glitchMaterial.dispose();renderer.dispose();},{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
