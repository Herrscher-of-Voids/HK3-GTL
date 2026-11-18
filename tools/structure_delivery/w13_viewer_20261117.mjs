import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  let bytes=Uint8Array.from(atob(window.W13_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W13_VOXEL_PAYLOAD=null;
  bytes=null;
  const stage=document.getElementById('stage'),modelById=new Map(data.models.map(m=>[m.id,m]));
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#19191f');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,1.1));
  const sun=new THREE.DirectionalLight(0xffffff,1.25);sun.position.set(-450,650,800);scene.add(sun);
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
  const groups=[],meshes=[],motions=[],visibleMaterials=new Set(materials.map((_,i)=>i));
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  const zPlane=new THREE.Plane(new THREE.Vector3(0,0,-1),data.bounds.max[2]+1);
  let renderedQuads=0,frames=0;
  for(const part of parts){
    const group=new THREE.Group(),content=new THREE.Group(),meta=part.metadata;
    group.name=part.id;group.userData={modelId:part.modelId,metadata:meta};
    if(meta.motion){
      group.position.set(...meta.pivot);content.position.fromArray(part.origin).sub(group.position);
      motions.push({group,meta,axis:meta.axis?new THREE.Vector3(...meta.axis).normalize():null,restY:group.position.y});
    }else group.position.set(...part.origin);
    group.add(content);scene.add(group);groups.push(group);
    group.userData.bounds=new THREE.Box3(new THREE.Vector3(...part.origin),new THREE.Vector3(...part.origin).add(new THREE.Vector3(...part.size)));
    const [w,,d]=part.size;
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
        }
        indices.set([j*4,j*4+1,j*4+2,j*4,j*4+2,j*4+3],j*6);
      });
      const geometry=new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));
      geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingSphere();
      const cuttable=part.modelId==='base',key=`${material}:${face}:${cuttable}`;
      if(!materialCache.has(key)){
        const info=materials[material];
        const mat=new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.54:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:cuttable?[plane,zPlane]:[plane],emissive:info.emissive?0xffffff:0,emissiveIntensity:info.emissive?.22:0});
        mat.userData.emissive=info.emissive;materialCache.set(key,mat);
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=material;content.add(mesh);meshes.push(mesh);renderedQuads+=starts.length;
    }
    delete part.starts;delete part.lengths;delete part.spans;
    document.getElementById('loading').textContent=`完整方块表面 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const gridSize=Math.ceil(Math.max(data.sizeXYZ[0],data.sizeXYZ[2])/16)*16;
  const grid=new THREE.GridHelper(gridSize,gridSize/16,0x7e5c74,0x38383f);
  grid.position.set((data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]-.5,(data.bounds.min[2]+data.bounds.max[2]+1)/2);grid.visible=false;scene.add(grid);
  const axes=new THREE.AxesHelper(32);axes.visible=false;scene.add(axes);
  const modelBlocks=new Map(data.models.map(model=>[model.id,parts.filter(part=>part.modelId===model.id).reduce((sum,part)=>sum+part.blocks,0)]));
  const coreCenter=new THREE.Vector3(...data.effects.core),laserTarget=new THREE.Vector3(...data.effects.laser_target),dummy=new THREE.Object3D();
  const laserGeometry=new THREE.BoxGeometry(1,1,1),laserMaterial=new THREE.MeshBasicMaterial({color:0xf23b8d,transparent:true,opacity:.65,depthWrite:false,clippingPlanes:[plane]});
  const laserGroup=new THREE.Group();
  for(const source of data.effects.laser_sources){
    const a=new THREE.Vector3(...source),direction=laserTarget.clone().sub(a),beam=new THREE.Mesh(laserGeometry,laserMaterial);
    beam.position.copy(a).add(laserTarget).multiplyScalar(.5);beam.scale.set(7,direction.length(),7);beam.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction.normalize());laserGroup.add(beam);
  }
  scene.add(laserGroup);
  const rainGeometry=new THREE.BoxGeometry(1.3,4,1.3),rainMaterial=new THREE.MeshBasicMaterial({color:0xff72bb,transparent:true,opacity:.86,depthWrite:false,clippingPlanes:[plane]});
  const rain=new THREE.InstancedMesh(rainGeometry,rainMaterial,data.effects.rain.length);rain.instanceMatrix.setUsage(THREE.DynamicDrawUsage);rain.frustumCulled=false;scene.add(rain);
  const cubeGeometry=new THREE.BoxGeometry(1,1,1),cubeMaterial=new THREE.MeshLambertMaterial({color:0x101017,clippingPlanes:[plane]});
  const cubes=new THREE.InstancedMesh(cubeGeometry,cubeMaterial,144);cubes.instanceMatrix.setUsage(THREE.DynamicDrawUsage);cubes.frustumCulled=false;scene.add(cubes);
  let activeModel='all',activeView='oblique',axis='y',layer=0,disposed=false,fitBox=new THREE.Box3(),fitZoom=1;
  let mode='idle',paused=false,time=0;
  const layerInput=document.getElementById('layer');
  const basicViews={oblique:{label:'整体斜视',direction:[-.8,.55,1.35]},front:{label:'正面',direction:[0,.13,1]},back:{label:'背面',direction:[0,.2,-1]},left:{label:'左侧',direction:[-1,.15,0]},right:{label:'右侧',direction:[1,.15,0]},top:{label:'俯视',direction:[0,1,0]}};
  function updateAnimation(){
    for(const {group,meta,axis:motionAxis,restY} of motions){
      if(meta.motion==='ring')group.quaternion.setFromAxisAngle(motionAxis,time*meta.speed);
      if(meta.motion==='obelisk')group.position.y=restY+Math.sin(time*.38)*Math.cos(meta.index)*4;
      if(meta.motion==='flower')group.scale.setScalar(1+Math.sin(time*1.6)*.025);
    }
    const effects=document.getElementById('effects').checked,all=activeModel==='all';
    laserGroup.visible=effects&&mode==='work'&&(all||activeModel==='base'||activeModel==='core');
    rain.visible=effects&&document.getElementById('roof').checked&&(all||activeModel==='canopy');
    cubes.visible=effects&&(all||activeModel==='core');
    data.effects.rain.forEach((route,i)=>{
      const phase=(i*.61803398875+time*.2)%1;
      dummy.position.set(route.top[0],route.top[1]-phase*route.length,route.top[2]);dummy.rotation.set(0,0,0);dummy.scale.set(1,mode==='work'?1.5:1,1);dummy.updateMatrix();rain.setMatrixAt(i,dummy.matrix);
    });rain.instanceMatrix.needsUpdate=true;
    for(let i=0;i<144;i++){
      const phase=(i*.61803398875+time*.025)%1,angle=i*2.3999632297+time*.018,radius=72+(i%13)*2.5;
      dummy.position.set(coreCenter.x+Math.cos(angle)*radius,coreCenter.y-67+phase*160,coreCenter.z+Math.sin(angle)*radius);
      dummy.rotation.set(0,0,0);dummy.scale.setScalar(1.8+(i%7)*.4);dummy.updateMatrix();cubes.setMatrixAt(i,dummy.matrix);
    }cubes.instanceMatrix.needsUpdate=true;
    laserMaterial.opacity=.54+Math.sin(time*2.4)*.1;
    materialCache.forEach(material=>{if(material.userData.emissive)material.emissiveIntensity=mode==='work'?.36+Math.sin(time*1.7)*.04:.22;});
  }
  const modelBounds=()=>{const bounds=new THREE.Box3();groups.filter(group=>group.visible).forEach(group=>bounds.union(group.userData.bounds));return bounds;};
  function draw(){if(disposed)return;updateAnimation();camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function views(){return {...basicViews,...data.views,...(activeModel==='all'?{}:modelById.get(activeModel).views)};}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));
    }return .86/limit;
  }
  function setView(name){
    activeView=name;const preset=views()[name],bounds=modelBounds(),target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3());
    const direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(2500));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  }
  function updateViewButtons(){
    const host=document.getElementById('views');host.replaceChildren();
    for(const [name,preset] of Object.entries(views())){const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);}
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    document.getElementById('modelName').textContent=all?data.title:model.title;
    document.getElementById('actualSize').textContent=`宽 ${data.sizeXYZ[0]} × 深 ${data.sizeXYZ[2]} × 高 ${data.sizeXYZ[1]} 格`;
    document.getElementById('modelStats').textContent=`${(all?data.total_blocks:modelBlocks.get(activeModel)).toLocaleString()} 个实体方块 · 当前宽${size[0]}×深${size[2]}×高${size[1]}`;
    const features=document.getElementById('features');features.replaceChildren();
    for(const text of all?data.design:model.features){const item=document.createElement('li');item.textContent=text;features.append(item);}
    axes.position.copy(bounds.min);
  }
  function setLayer(value){
    layer=value;layerInput.value=value;const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;
    document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(axis),bounds=modelBounds();
    layerInput.min=Math.floor(bounds.min.getComponent(index));layerInput.max=Math.ceil(bounds.max.getComponent(index))-1;setLayer(+layerInput.max);
  }
  function applyGroups(){groups.forEach(group=>group.visible=(activeModel==='all'||group.userData.modelId===activeModel)&&(!group.userData.metadata.canopy_grid||document.getElementById('roof').checked));}
  function setModel(id){
    activeModel=id;applyGroups();document.querySelectorAll('[data-model]').forEach(button=>button.classList.toggle('active',button.dataset.model===id));
    updateDetails();updateViewButtons();setAxis(axis);setView('oblique');
  }
  function setCanopy(value){document.getElementById('roof').checked=value;applyGroups();updateDetails();setView(activeView);}
  function setCutaway(value){document.getElementById('cutaway').checked=value;zPlane.constant=value?0:data.bounds.max[2]+1;draw();}
  function setEffects(value){document.getElementById('effects').checked=value;draw();}
  function setMode(value){mode=value;document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;const button=document.getElementById('pause');button.textContent=paused?'继续':'暂停';button.setAttribute('aria-pressed',String(paused));draw();}
  function setTime(value){time=value;const input=document.getElementById('time');input.max=Math.max(60,Math.ceil(time));input.value=time;document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();}
  for(const model of [{id:'all',title:'整体'},...data.models]){const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.title;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);}
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');
    label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;input.type='checkbox';input.checked=true;code.textContent=info.state;
    input.onchange=()=>{input.checked?visibleMaterials.add(index):visibleMaterials.delete(index);meshes.forEach(mesh=>mesh.visible=visibleMaterials.has(mesh.userData.material));draw();};
    label.append(input,code);document.getElementById('materials').append(label);
  });
  document.getElementById('materialSearch').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(query));};
  document.getElementById('axis').onchange=event=>setAxis(event.target.value);layerInput.oninput=event=>setLayer(+event.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};document.getElementById('axes').onchange=event=>{axes.visible=event.target.checked;draw();};
  document.getElementById('roof').onchange=event=>setCanopy(event.target.checked);document.getElementById('effects').onchange=event=>setEffects(event.target.checked);document.getElementById('cutaway').onchange=event=>setCutaway(event.target.checked);
  document.getElementById('mode').onchange=event=>setMode(event.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);document.getElementById('timeZero').onclick=()=>setTime(0);document.getElementById('time').oninput=event=>setTime(+event.target.value);
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};
  document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download=`W13-${activeModel}-${activeView}-A1.png`;link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();
    if(window.W13_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);let last=performance.now();
  function animate(now){if(disposed)return;const elapsed=Math.min((now-last)/1000,.1);last=now;if(!paused&&mode==='work')setTime(time+elapsed);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({activeModel,activeView,axis,layer,frames,renderedQuads,mode,paused,time,showCanopy:document.getElementById('roof').checked,cutaway:document.getElementById('cutaway').checked,effects:document.getElementById('effects').checked,animationWebOnly:true,laserCount:laserGroup.children.length,rainParticles:data.effects.rain.length,blackCubeParticles:144,models:data.models.map(model=>({id:model.id,blocks:modelBlocks.get(model.id)})),motionParts:motions.map(({group,meta})=>({id:group.name,motion:meta.motion,position:group.position.toArray(),quaternion:group.quaternion.toArray(),scale:group.scale.toArray()})),visibleParts:groups.filter(group=>group.visible).map(group=>group.name),camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom}});
  window.W13Viewer={setModel,setView,setAxis,setLayer,setCanopy,setCutaway,setEffects,setMode,setPaused,setTime,snapshot,availableViews:()=>Object.keys(views())};
  document.getElementById('stats').textContent=`${parts.length} 件完整构件 · ${renderedQuads.toLocaleString()} 个合并表面 · ${materials.length} 项原生材质`;
  document.getElementById('loading').remove();resize();setModel('all');setTime(0);window.W13_READY=true;
  window.addEventListener('pagehide',()=>{
    disposed=true;observer.disconnect();controls.dispose();meshes.forEach(mesh=>mesh.geometry.dispose());materialCache.forEach(material=>material.dispose());textureCache.forEach(async value=>(await value).dispose());
    grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();laserGeometry.dispose();laserMaterial.dispose();rainGeometry.dispose();rainMaterial.dispose();cubeGeometry.dispose();cubeMaterial.dispose();renderer.dispose();
  },{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
