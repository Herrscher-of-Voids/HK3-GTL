import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  const bytes=Uint8Array.from(atob(window.THEATRE_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.THEATRE_PAYLOAD=null;
  const stage=document.getElementById('stage'),modelById=new Map(data.models.map(m=>[m.id,m]));
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#151922');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,.85));
  const sun=new THREE.DirectionalLight(0xfff8ef,1.35);sun.position.set(-450,650,800);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xcad8ff,.4);fill.position.set(500,150,-650);scene.add(fill);
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
  const groups=[],meshes=[];
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  let renderedQuads=0,frames=0;
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.userData.modelId=part.modelId;group.position.set(...part.origin);scene.add(group);groups.push(group);
    group.userData.bounds=new THREE.Box3(group.position.clone(),group.position.clone().add(new THREE.Vector3(...part.size)));
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
      const key=`${material}:${face}`;
      if(!materialCache.has(key)){
        const info=materials[material];
        materialCache.set(key,new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.5:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:info.emissive?info.color:0,emissiveIntensity:info.emissive?.2:0}));
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=material;group.add(mesh);meshes.push(mesh);renderedQuads+=starts.length;
    }
    document.getElementById('loading').textContent=`完整方块表面 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }


  let activeModel='all',activeView='oblique',axis='y',shellMode='cutaway',fitZoom=1,fitBox=new THREE.Box3();
  const basicViews={oblique:{label:'前方斜视',direction:[-.55,.38,1.5]},front:{label:'正面',direction:[0,0,1]},back:{label:'背面',direction:[0,0,-1]},left:{label:'左侧',direction:[-1,0,0]},right:{label:'右侧',direction:[1,0,0]},top:{label:'顶部',direction:[0,1,0]}};
  const layerInput=document.getElementById('layer');
  function bounds(){const box=new THREE.Box3();groups.filter(g=>g.visible).forEach(g=>box.union(g.userData.bounds));return box;}
  function draw(){camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
    }
    return .88/limit;
  }
  function setView(name){
    activeView=name;const preset={...basicViews,...data.views}[name],box=bounds();
    const target=preset.center?new THREE.Vector3(...preset.center):box.getCenter(new THREE.Vector3());
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):box;
    const direction=new THREE.Vector3(...preset.direction).normalize();camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(preset.distance||2000));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));
  }
  function setLayer(value){
    const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;
    layerInput.value=value;document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const box=bounds(),index='xyz'.indexOf(value);
    layerInput.min=Math.floor(box.min.getComponent(index));layerInput.max=Math.ceil(box.max.getComponent(index))-1;setLayer(+layerInput.max);
  }
  function setModel(id){
    activeModel=id;
    groups.forEach(g=>{
      const omitted=['roof','front'].includes(g.userData.modelId)||g.name==='side_wall_-1'||g.name.startsWith('side_niche_-1_')||g.name.startsWith('wall_pier_-1_');
      g.visible=id==='all'?(shellMode==='full'||!omitted):g.userData.modelId===id;
    });setAxis(axis);setView('oblique');
    document.querySelectorAll('[data-model]').forEach(b=>b.classList.toggle('active',b.dataset.model===id));
    const size=id==='all'?new THREE.Vector3(...data.sizeXYZ):bounds().getSize(new THREE.Vector3());document.getElementById('actualSize').textContent=`宽 ${size.x} × 深 ${size.z} × 高 ${size.y} 格`;
    document.getElementById('modelName').textContent=id==='all'?data.title:modelById.get(id).title;
  }
  function setShellMode(mode){
    shellMode=mode;setModel('all');
    document.getElementById('shellFull').classList.toggle('active',mode==='full');
    document.getElementById('shellCutaway').classList.toggle('active',mode==='cutaway');
  }
  for(const model of [{id:'all',title:'剧场总览'},...data.models]){
    const b=document.createElement('button');b.textContent=model.title;b.dataset.model=model.id;b.onclick=()=>setModel(model.id);document.getElementById('models').append(b);
  }
  for(const [name,view] of Object.entries({...basicViews,...data.views})){
    const b=document.createElement('button');b.textContent=view.label;b.dataset.view=name;b.onclick=()=>setView(name);document.getElementById('views').append(b);
  }
  for(const note of data.design){const p=document.createElement('p');p.textContent=note;document.getElementById('features').append(p);}
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;
    input.onchange=()=>{meshes.filter(m=>m.userData.material===index).forEach(m=>m.visible=input.checked);draw();};
    label.append(input,info.label);document.getElementById('materials').append(label);
  });
  document.getElementById('axis').onchange=e=>setAxis(e.target.value);layerInput.oninput=e=>setLayer(+e.target.value);
  document.getElementById('fullLayer').onclick=()=>setAxis(axis);document.getElementById('reset').onclick=()=>setShellMode('cutaway');
  document.getElementById('shellFull').onclick=()=>setShellMode('full');document.getElementById('shellCutaway').onclick=()=>setShellMode('cutaway');
  document.getElementById('screenshot').onclick=()=>{draw();const a=document.createElement('a');a.download=`支配剧场-T2-${activeView}.png`;a.href=renderer.domElement.toDataURL();a.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();
    if(window.THEATRE_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);
  window.TheatreViewer={setModel,setView,setAxis,setLayer,setShellMode,views:data.views,snapshot:()=>({activeModel,activeView,axis,shellMode,frames,renderedQuads,parts:parts.length,blocks:data.total_blocks,camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom},staticGeometry:true})};
  document.getElementById('stats').textContent=`${data.total_blocks.toLocaleString()} 个方块 · ${parts.length} 个构件`;
  document.getElementById('loading').remove();resize();setShellMode('cutaway');window.THEATRE_READY=true;
  window.addEventListener('pagehide',()=>{observer.disconnect();controls.dispose();meshes.forEach(m=>m.geometry.dispose());materialCache.forEach(m=>m.dispose());textureCache.forEach(async p=>(await p).dispose());renderer.dispose();},{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
