import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  let bytes=Uint8Array.from(atob(window.W07_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W07_VOXEL_PAYLOAD=null;bytes=null;
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

  const center=new THREE.Vector3(...data.effects.center),particleCount=224,dummy=new THREE.Object3D();
  const particleGeometry=new THREE.BoxGeometry(1,1,1);
  const darkMaterial=new THREE.MeshBasicMaterial({color:0x26212a,transparent:true,opacity:.9,clippingPlanes:[plane]});
  const whiteMaterial=new THREE.MeshBasicMaterial({color:0xfff6df,transparent:true,opacity:.86,depthWrite:false,clippingPlanes:[plane]});
  const darkParticles=new THREE.InstancedMesh(particleGeometry,darkMaterial,particleCount),whiteParticles=new THREE.InstancedMesh(particleGeometry,whiteMaterial,particleCount);
  for(const effect of [darkParticles,whiteParticles]){effect.instanceMatrix.setUsage(THREE.DynamicDrawUsage);effect.frustumCulled=false;scene.add(effect);}
  for(let i=0;i<particleCount;i++){darkParticles.setColorAt(i,new THREE.Color(i%5?0x27212b:0x64516a));whiteParticles.setColorAt(i,new THREE.Color(i%5?0xfff8eb:0xe6d095));}
  let activeModel='all',activeView='oblique',axis='y',layer=0,disposed=false,fitBox=new THREE.Box3(),fitZoom=1,mode='idle',paused=false,time=0;
  const layerInput=document.getElementById('layer'),hullHalfWidth=data.sizeXYZ[0]*.44;
  const middleZ=(data.bounds.min[2]+data.bounds.max[2]+1)/2;
  const basicViews={
    oblique:{label:'整体斜视',direction:[-.85,.75,1.65]},
    front:{label:'船首',direction:[0,.14,1]},
    back:{label:'船尾',direction:[0,.2,-1]},
    left:{label:'腐朽左舷',direction:[-1,.22,0]},
    right:{label:'生命右舷',direction:[1,.22,0]},
    top:{label:'俯视',direction:[0,1,0]},
    belly:{label:'船腹剖切',direction:[-.75,.6,1.25]},
    pixels:{label:'像素近景',center:[-data.sizeXYZ[0]*.3,center.y,data.sizeXYZ[2]*.22+middleZ],half:[38,32,38],direction:[-.8,.65,1.2]}
  };
  function effectGroup(ids){return ids.some(id=>(activeModel==='all'||activeModel===id)&&!hiddenModels.has(id));}
  function updateAnimation(){
    const running=document.getElementById('effects').checked&&mode==='work';
    darkParticles.visible=running&&effectGroup(['hull_dark','deck_dark','spine']);
    whiteParticles.visible=running&&effectGroup(['hull_white','deck_white','life','spine']);
    for(let i=0;i<particleCount;i++){
      const t=(time*.095+i/particleCount)%1,stripe=((i*53)%227)/227,z=middleZ+(stripe-.5)*data.sizeXYZ[2]*.78;
      const radius=hullHalfWidth*(.28+((i*37)%223)/223*.7),y=center.y-25+((i*29)%71);
      const size=1.3+(i%4)*.65;
      dummy.position.set(-radius*(1-t)-3,y+(center.y-y)*t+Math.sin(t*Math.PI)*13,z+Math.sin(t*Math.PI)*9);
      dummy.rotation.set(i*.7+t*.4,i*.3+t*.8,i*.2);dummy.scale.setScalar(size*(1-.4*t));dummy.updateMatrix();darkParticles.setMatrixAt(i,dummy.matrix);
      dummy.position.set(3+radius*t,center.y+(y-center.y)*t+Math.sin(t*Math.PI)*18,z-Math.sin(t*Math.PI)*9);
      dummy.rotation.set(i*.4-t*.5,i*.8,i*.3+t*.3);dummy.scale.setScalar(size*(.65+.35*t));dummy.updateMatrix();whiteParticles.setMatrixAt(i,dummy.matrix);
    }
    darkParticles.instanceMatrix.needsUpdate=true;whiteParticles.instanceMatrix.needsUpdate=true;
    materialCache.forEach(material=>{if(material.emissiveIntensity)material.emissiveIntensity=running?.24+Math.sin(time*1.2)*.035:.2;});
  }
  function modelBounds(){const bounds=new THREE.Box3();groups.filter(group=>activeModel==='all'||group.userData.modelId===activeModel).forEach(group=>bounds.union(group.userData.bounds));return bounds;}
  function draw(){if(disposed)return;updateAnimation();camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function views(){return {...basicViews,...data.views,...(activeModel==='all'?{}:modelById.get(activeModel).views)};}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));}
    return .82/limit;
  }
  function setView(name){
    const previousView=activeView;activeView=name;
    const preset=views()[name],bounds=modelBounds();
    if(name==='belly'){setAxis('y');setLayer(Math.floor(bounds.min.y+(bounds.max.y-bounds.min.y)*.42));bounds.max.y=layer+1;}
    else if(previousView==='belly')setAxis(axis);
    const target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3()),direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(6000));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    document.getElementById('modelName').textContent=all?data.title:model.label;
    document.getElementById('actualSize').textContent='宽 '+data.sizeXYZ[0]+' × 深 '+data.sizeXYZ[2]+' × 高 '+data.sizeXYZ[1]+' 格';
    document.getElementById('modelStats').textContent=(all?data.blocks:modelBlocks.get(activeModel)).toLocaleString()+' 个实体方块 · 当前宽'+size[0]+'×深'+size[2]+'×高'+size[1];
    const features=document.getElementById('features');features.replaceChildren();
    for(const text of all?data.models.flatMap(item=>item.features):model.features){const item=document.createElement('li');item.textContent=text;features.append(item);}
    axes.position.copy(bounds.min);
  }
  function updateViewButtons(){
    const host=document.getElementById('views');host.replaceChildren();
    for(const [name,preset] of Object.entries(views())){const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);}
  }
  function setLayer(value){
    layer=value;layerInput.value=value;const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;
    document.getElementById('layerLabel').textContent=axis.toUpperCase()+' = '+value;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(axis),bounds=modelBounds();
    layerInput.min=Math.floor(bounds.min.getComponent(index));layerInput.max=Math.ceil(bounds.max.getComponent(index))-1;setLayer(+layerInput.max);
  }
  function applyGroups(){groups.forEach(group=>group.visible=(activeModel==='all'||group.userData.modelId===activeModel)&&!hiddenModels.has(group.userData.modelId));}
  function setModel(id){
    activeModel=id;
    if(id!=='all'){hiddenModels.delete(id);document.querySelector('[data-group="'+id+'"]').checked=true;}
    applyGroups();document.querySelectorAll('[data-model]').forEach(button=>button.classList.toggle('active',button.dataset.model===id));
    updateDetails();updateViewButtons();setAxis(axis);setView('oblique');
  }
  function setMode(value){mode=value;document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;document.getElementById('pause').textContent=paused?'继续':'暂停';document.getElementById('pause').setAttribute('aria-pressed',String(paused));draw();}
  function setTime(value){
    time=value;const input=document.getElementById('time');input.max=Math.max(60,Math.ceil(time));input.value=time;
    document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();
  }
  for(const model of [{id:'all',label:'整体'},...data.models]){
    const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.label;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);
  }
  for(const model of data.models){
    const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.group=model.id;label.append(input,' '+model.label);
    input.onchange=()=>{input.checked?hiddenModels.delete(model.id):hiddenModels.add(model.id);applyGroups();draw();};document.getElementById('groups').append(label);
  }
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');
    label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;input.type='checkbox';input.checked=true;code.textContent=info.state;
    input.onchange=()=>{input.checked?visibleMaterials.add(index):visibleMaterials.delete(index);meshes.forEach(mesh=>mesh.visible=visibleMaterials.has(mesh.userData.material));draw();};
    label.append(input,code);document.getElementById('materials').append(label);
  });
  document.getElementById('materialSearch').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(query));};
  document.getElementById('axis').onchange=event=>setAxis(event.target.value);layerInput.oninput=event=>setLayer(+event.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};document.getElementById('axes').onchange=event=>{axes.visible=event.target.checked;draw();};
  document.getElementById('effects').onchange=draw;document.getElementById('mode').onchange=event=>setMode(event.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);
  document.getElementById('timeZero').onclick=()=>setTime(0);document.getElementById('time').oninput=event=>setTime(+event.target.value);
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};
  document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download='W07-N1-'+activeModel+'-'+activeView+'.png';link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-1000*w/h;camera.right=1000*w/h;camera.top=1000;camera.bottom=-1000;camera.updateProjectionMatrix();
    if(window.W07_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);let last=performance.now();
  function animate(now){if(disposed)return;const elapsed=Math.min((now-last)/1000,.1);last=now;if(!paused&&mode==='work')setTime(time+elapsed);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({
    activeModel,activeView,axis,layer,frames,renderedQuads,mode,paused,time,animationWebOnly:true,darkParticlesVisible:darkParticles.visible,whiteParticlesVisible:whiteParticles.visible,
    hiddenModels:[...hiddenModels],models:data.models.map(model=>({id:model.id,blocks:modelBlocks.get(model.id)})),visibleParts:groups.filter(group=>group.visible).map(group=>group.name),
    camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom}
  });
  window.W07Viewer={setModel,setView,setAxis,setLayer,setMode,setPaused,setTime,draw,snapshot,availableViews:()=>Object.keys(views())};
  document.getElementById('stats').textContent=parts.length+' 件完整构件 · '+renderedQuads.toLocaleString()+' 个合并表面 · '+materials.length+' 项原生材质';document.getElementById('nbtLink').href=data.nbt_file;
  document.getElementById('loading').remove();resize();setModel('all');setTime(0);window.W07_READY=true;
  window.addEventListener('pagehide',()=>{
    disposed=true;observer.disconnect();controls.dispose();meshes.forEach(mesh=>mesh.geometry.dispose());materialCache.forEach(material=>material.dispose());textureCache.forEach(async value=>(await value).dispose());
    grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();particleGeometry.dispose();darkMaterial.dispose();whiteMaterial.dispose();renderer.dispose();
  },{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent='预览载入失败：'+error.message;});
