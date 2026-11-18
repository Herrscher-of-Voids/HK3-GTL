import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  let bytes=Uint8Array.from(atob(window.W14_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W14_VOXEL_PAYLOAD=null;bytes=null;
  const stage=document.getElementById('stage'),modelById=new Map(data.models.map(model=>[model.id,model]));
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setClearColor('#14202d');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,1.35));
  const sun=new THREE.DirectionalLight(0xffffff,1.8);sun.position.set(-950,1600,1300);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xffffff,.85);fill.position.set(1100,550,-950);scene.add(fill);
  const camera=new THREE.OrthographicCamera(-1000,1000,1000,-1000,.1,20000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map();
  const textures=await Promise.all(materials.map(async info=>{
    const maps={};await Promise.all(Object.entries(info.faces).map(async([face,url])=>{
      if(!textureCache.has(url))textureCache.set(url,loader.loadAsync(url));
      const texture=await textureCache.get(url);texture.colorSpace=THREE.SRGBColorSpace;texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestMipmapLinearFilter;
      texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.generateMipmaps=true;texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());maps[face]=texture;
    }));return maps;
  }));
  const faceNames=['east','west','south','north','down','up'],normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],meshes=[],hiddenModels=new Set(),visibleMaterials=new Set(materials.map((_,index)=>index));
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  let renderedQuads=0,frames=0;
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.position.set(...part.origin);
    group.userData={modelId:part.modelId,bounds:new THREE.Box3(new THREE.Vector3(...part.origin),new THREE.Vector3(...part.origin).add(new THREE.Vector3(...part.size)))};
    groups.push(group);scene.add(group);const [w,,d]=part.size;
    for(let material=0;material<materials.length;material++)for(let face=0;face<6;face++){
      const starts=part.starts[material][face],lengths=part.lengths[material][face],spans=part.spans[material][face];
      if(!starts.length)continue;
      const positions=new Float32Array(starts.length*12),ns=new Float32Array(starts.length*12),uvs=new Float32Array(starts.length*8),indices=new Uint32Array(starts.length*6);
      const axis=face<2?2:0,cross=face<4?1:2;
      starts.forEach((index,j)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d];
        for(let v=0;v<4;v++){
          const corner=corners[face][v];
          for(let k=0;k<3;k++){positions[j*12+v*3+k]=start[k]+corner[k]*(k===axis?lengths[j]:k===cross?spans[j]:1);ns[j*12+v*3+k]=normals[face][k];}
          uvs[j*8+v*2]=corner[axis]*lengths[j];uvs[j*8+v*2+1]=corner[cross]*spans[j];
        }indices.set([j*4,j*4+1,j*4+2,j*4,j*4+2,j*4+3],j*6);
      });
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingSphere();
      const key=`${material}:${face}`;
      if(!materialCache.has(key)){
        const info=materials[material];materialCache.set(key,new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.48:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:info.emissive?0xffffff:0,emissiveMap:textures[material][faceNames[face]],emissiveIntensity:info.emissive?.2:0}));
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=material;group.add(mesh);meshes.push(mesh);renderedQuads+=starts.length;
    }
    delete part.starts;delete part.lengths;delete part.spans;
    document.getElementById('loading').textContent=`完整方块表面 ${groups.length}/${parts.length}`;await new Promise(resolve=>setTimeout(resolve,0));
  }
  const gridSize=Math.ceil(Math.max(data.sizeXYZ[0],data.sizeXYZ[2])/16)*16,grid=new THREE.GridHelper(gridSize,gridSize/16,0x738399,0x2f4052);
  grid.position.set((data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]-.5,(data.bounds.min[2]+data.bounds.max[2]+1)/2);grid.visible=false;scene.add(grid);
  const axes=new THREE.AxesHelper(48);axes.visible=false;scene.add(axes);
  const modelBlocks=new Map(data.models.map(model=>[model.id,parts.filter(part=>part.modelId===model.id).reduce((sum,part)=>sum+part.blocks,0)]));
  const nozzle=new THREE.Vector3(...data.effects.nozzle),bubbleCenters=data.effects.bubble_centers.map(point=>new THREE.Vector3(...point));
  const particleGeometry=new THREE.BoxGeometry(1,1,1),dummy=new THREE.Object3D(),streamColor=new THREE.Color();
  const particleMaterial=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.72,depthWrite:false});
  const flameMaterials=[
    new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.92,depthWrite:false}),
    new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.68,depthWrite:false}),
    new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.76,depthWrite:false})
  ];
  const flameLayers=[{slices:26,points:20,height:300,radius:40},{slices:44,points:28,height:500,radius:78},{slices:48,points:24,height:680,radius:108}];
  const flameMeshes=flameLayers.map((layer,index)=>new THREE.InstancedMesh(particleGeometry,flameMaterials[index],layer.slices*layer.points));
  flameMeshes.forEach((mesh,index)=>mesh.renderOrder=3-index);
  const plume=new THREE.InstancedMesh(particleGeometry,particleMaterial,192),feed=new THREE.InstancedMesh(particleGeometry,particleMaterial,bubbleCenters.length*9);
  for(const effect of [...flameMeshes,plume,feed]){effect.instanceMatrix.setUsage(THREE.DynamicDrawUsage);effect.frustumCulled=false;scene.add(effect);}
  const dimensionNames=['主世界','末地','地狱','月球','火星','金星','银河系'],dimensionColors=[0x8de7b1,0xcf9cff,0xff7435,0xcce6ff,0xff9262,0xffda79,0xd4b5ff];
  for(let i=0;i<192;i++)plume.setColorAt(i,new THREE.Color(i%3?0xffba56:0xaedcff));
  for(let i=0;i<bubbleCenters.length*9;i++)feed.setColorAt(i,new THREE.Color(dimensionColors[Math.floor(i/9)]));
  let activeModel='all',activeView='oblique',axis='y',layer=0,disposed=false,fitBox=new THREE.Box3(),fitZoom=1,mode='idle',paused=false,time=0;
  const layerInput=document.getElementById('layer');
  const workingHeight=nozzle.y+730-data.bounds.min[1],workingCenter=[(data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]+workingHeight/2,(data.bounds.min[2]+data.bounds.max[2]+1)/2];
  const sectorViews=Object.fromEntries(bubbleCenters.map((point,index)=>['sector_'+index,{label:dimensionNames[index]+'扇区',center:[point.x*.5,58,point.z*.5],half:[235,96,235],direction:[point.x/820,.82,point.z/820]}]));
  const basicViews={oblique:{label:'整体斜视',direction:[-.95,.88,1.3]},front:{label:'正面',direction:[0,.16,1]},back:{label:'背面',direction:[0,.3,-1]},left:{label:'侧面',direction:[-1,.26,0]},top:{label:'俯视',direction:[0,1,0]},nozzle:{label:'喷口',center:nozzle.toArray(),half:[240,180,240],direction:[-.9,.9,1.2]},flame:{label:'火箭尾焰',center:[nozzle.x,nozzle.y+320,nozzle.z],half:[300,385,300],direction:[-.9,.24,1.2]},fuel:{label:'维度供料球',center:bubbleCenters[0].toArray(),half:[175,160,175],direction:[-.8,.5,1.25]},pixels:{label:'像素细节',center:[0,100,data.bounds.max[2]*.48],half:[32,28,32],direction:[-.7,.5,1.25]},running:{label:'运行全景',center:workingCenter,half:[data.sizeXYZ[0]*.52,workingHeight*.52,data.sizeXYZ[2]*.52],direction:[-.95,.5,1.3]},...sectorViews};
  function effectGroup(id){return (activeModel==='all'||activeModel===id)&&!hiddenModels.has(id);}
  function updateAnimation(){
    const running=document.getElementById('effects').checked&&mode==='work';
    plume.visible=running&&effectGroup('engine');flameMeshes.forEach(mesh=>mesh.visible=plume.visible);feed.visible=running&&(effectGroup('dimensions')||effectGroup('feed'));
    if(plume.visible){
      flameLayers.forEach((layer,layerIndex)=>{
        const mesh=flameMeshes[layerIndex],pulse=1+.035*Math.sin(time*9.5+layerIndex);
        for(let slice=0;slice<layer.slices;slice++)for(let point=0;point<layer.points;point++){
          const index=slice*layer.points+point,t=(slice+.16*Math.sin(time*12+point*.9))/layer.slices,angle=point*2.399963+slice*.37+time*.24;
          const wave=1+Math.min(1,t*12)*(.09*Math.sin(t*35-time*8)+.055*Math.cos(point*1.7+time*11)),profile=(1-.97*t)*(1+.27*Math.exp(-(((t-.16)/.105)**2)));
          const radial=layerIndex===0?Math.sqrt((point+.5)/layer.points):.87+.13*((point*17)%41)/41;
          const radius=layer.radius*profile*radial*wave*pulse,cell=(layerIndex===0?19:layerIndex===1?18:17)*(1-.72*t);
          dummy.position.set(nozzle.x+Math.cos(angle)*radius+Math.sin(t*6+time*2)*11*t,nozzle.y+4+Math.max(0,t)*layer.height,nozzle.z+Math.sin(angle)*radius+Math.cos(t*7+time*1.6)*8*t);
          dummy.scale.set(cell,layer.height/layer.slices*(layerIndex===2?1.17:1.35),cell);dummy.updateMatrix();mesh.setMatrixAt(index,dummy.matrix);
          if(layerIndex===0)streamColor.setRGB(.72+.23*(1-t),.87+.13*(1-t),1);
          else if(layerIndex===1)streamColor.setRGB(.045+.08*t,.33+.23*(1-t),.94);
          else streamColor.setRGB(1,.15+.39*(1-t),.012+.025*(1-t));
          streamColor.multiplyScalar(.83+.17*Math.sin(point*1.3+slice*.73-time*6));mesh.setColorAt(index,streamColor);
        }
        mesh.instanceMatrix.needsUpdate=true;mesh.instanceColor.needsUpdate=true;
      });
      for(let i=0;i<192;i++){
        const t=(time*.24+i/192)%1,angle=i*2.399963+time*.16,radius=(148-100*t)*(.6+.4*((i*37)%193)/193),size=(4+i%5)*(1-.5*t);
        dummy.position.set(nozzle.x+Math.cos(angle)*radius+18*Math.sin(t*5+time)*t,nozzle.y+35+t*680,nozzle.z+Math.sin(angle)*radius);dummy.scale.set(size,size*(1.8+2*t),size);dummy.updateMatrix();plume.setMatrixAt(i,dummy.matrix);
      }plume.instanceMatrix.needsUpdate=true;
    }
    if(feed.visible){bubbleCenters.forEach((center,index)=>{
      const destination=new THREE.Vector3(center.x*.57,42,center.z*.57);
      for(let j=0;j<9;j++){
        const t=(time*.16+j/9+index*.11)%1,point=center.clone().lerp(destination,t);point.y+=Math.sin(t*Math.PI)*31;
        dummy.position.copy(point);dummy.scale.setScalar(2.7+Math.sin(t*Math.PI)*2);dummy.updateMatrix();feed.setMatrixAt(index*9+j,dummy.matrix);
      }
    });feed.instanceMatrix.needsUpdate=true;}
    materialCache.forEach(material=>{if(material.emissiveIntensity)material.emissiveIntensity=running?.25+Math.sin(time*1.4)*.045:.2;});
  }
  function modelBounds(){const bounds=new THREE.Box3();groups.filter(group=>activeModel==='all'||group.userData.modelId===activeModel).forEach(group=>bounds.union(group.userData.bounds));return bounds;}
  function draw(){if(disposed)return;updateAnimation();camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function views(){return {...basicViews,...data.views,...(activeModel==='all'?{}:modelById.get(activeModel).views)};}
  function zoomForBox(box){camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));}return .82/limit;}
  function setView(name){
    activeView=name;const preset=views()[name],bounds=modelBounds(),target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3()),direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(6000));controls.update();fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    document.getElementById('modelName').textContent=all?data.title:model.label;document.getElementById('actualSize').textContent=`宽 ${data.sizeXYZ[0]} × 深 ${data.sizeXYZ[2]} × 高 ${data.sizeXYZ[1]} 格`;
    document.getElementById('modelStats').textContent=`${(all?data.blocks:modelBlocks.get(activeModel)).toLocaleString()} 个实体方块 · 当前宽${size[0]}×深${size[2]}×高${size[1]}`;
    const features=document.getElementById('features');features.replaceChildren();for(const text of all?data.models.flatMap(item=>item.features):model.features){const item=document.createElement('li');item.textContent=text;features.append(item);}axes.position.copy(bounds.min);
  }
  function updateViewButtons(){const host=document.getElementById('views');host.replaceChildren();for(const [name,preset] of Object.entries(views())){const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);}}
  function setLayer(value){layer=value;layerInput.value=value;const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();}
  function setAxis(value){axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(axis),bounds=modelBounds();layerInput.min=Math.floor(bounds.min.getComponent(index));layerInput.max=Math.ceil(bounds.max.getComponent(index))-1;setLayer(+layerInput.max);}
  function applyGroups(){groups.forEach(group=>group.visible=(activeModel==='all'||group.userData.modelId===activeModel)&&!hiddenModels.has(group.userData.modelId));}
  function setModel(id){activeModel=id;if(id!=='all'){hiddenModels.delete(id);document.querySelector(`[data-group="${id}"]`).checked=true;}applyGroups();document.querySelectorAll('[data-model]').forEach(button=>button.classList.toggle('active',button.dataset.model===id));updateDetails();updateViewButtons();setAxis(axis);setView('oblique');}
  function setMode(value){mode=value;document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;document.getElementById('pause').textContent=paused?'继续':'暂停';document.getElementById('pause').setAttribute('aria-pressed',String(paused));draw();}
  function setTime(value){time=value;const input=document.getElementById('time');input.max=Math.max(60,Math.ceil(time));input.value=time;document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();}
  for(const model of [{id:'all',label:'整体'},...data.models]){const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.label;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);}
  for(const model of data.models){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.group=model.id;label.append(input,' '+model.label);input.onchange=()=>{input.checked?hiddenModels.delete(model.id):hiddenModels.add(model.id);applyGroups();draw();};document.getElementById('groups').append(label);}
  materials.forEach((info,index)=>{const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;input.type='checkbox';input.checked=true;code.textContent=info.state;input.onchange=()=>{input.checked?visibleMaterials.add(index):visibleMaterials.delete(index);meshes.forEach(mesh=>mesh.visible=visibleMaterials.has(mesh.userData.material));draw();};label.append(input,code);document.getElementById('materials').append(label);});
  document.getElementById('materialSearch').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(query));};
  document.getElementById('axis').onchange=event=>setAxis(event.target.value);layerInput.oninput=event=>setLayer(+event.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};document.getElementById('axes').onchange=event=>{axes.visible=event.target.checked;draw();};
  document.getElementById('effects').onchange=draw;document.getElementById('mode').onchange=event=>setMode(event.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);document.getElementById('timeZero').onclick=()=>setTime(0);document.getElementById('time').oninput=event=>setTime(+event.target.value);
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download=`W14-E2-${activeModel}-${activeView}.png`;link.href=renderer.domElement.toDataURL('image/png');link.click();};document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();controls.addEventListener('change',draw);
  function resize(){const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-1000*w/h;camera.right=1000*w/h;camera.top=1000;camera.bottom=-1000;camera.updateProjectionMatrix();if(window.W14_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}}
  const observer=new ResizeObserver(resize);observer.observe(stage);let last=performance.now();
  function animate(now){if(disposed)return;const elapsed=Math.min((now-last)/1000,.1);last=now;if(!paused&&mode==='work')setTime(time+elapsed);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({activeModel,activeView,axis,layer,frames,renderedQuads,mode,paused,time,animationWebOnly:true,flameStyle:'voxel-rocket-white-blue-orange',flameLayers:flameLayers.map(layer=>({slices:layer.slices,points:layer.points,height:layer.height})),plumeVisible:plume.visible,feedVisible:feed.visible,hiddenModels:[...hiddenModels],models:data.models.map(model=>({id:model.id,blocks:modelBlocks.get(model.id)})),visibleParts:groups.filter(group=>group.visible).map(group=>group.name),camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom}});
  window.W14Viewer={setModel,setView,setAxis,setLayer,setMode,setPaused,setTime,draw,snapshot,availableViews:()=>Object.keys(views())};document.getElementById('stats').textContent=`${parts.length} 件完整构件 · ${renderedQuads.toLocaleString()} 个合并表面 · ${materials.length} 项原生材质`;document.getElementById('nbtLink').href=data.nbt_file;
  document.getElementById('loading').remove();resize();setModel('all');setTime(0);window.W14_READY=true;
  window.addEventListener('pagehide',()=>{disposed=true;observer.disconnect();controls.dispose();meshes.forEach(mesh=>mesh.geometry.dispose());materialCache.forEach(material=>material.dispose());textureCache.forEach(async value=>(await value).dispose());grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();particleGeometry.dispose();particleMaterial.dispose();flameMaterials.forEach(material=>material.dispose());renderer.dispose();},{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
