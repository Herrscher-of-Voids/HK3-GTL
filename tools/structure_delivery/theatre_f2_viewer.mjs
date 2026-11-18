import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {setupPuppetry} from './theatre_f2_animation.mjs';

async function unpack(value){
  const bytes=Uint8Array.from(atob(value),c=>c.charCodeAt(0));
  return JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
}

async function main(){
  const [{data,materials,parts},actors]=await Promise.all([unpack(window.THEATRE_PAYLOAD),unpack(window.ACTOR_PAYLOAD)]);
  window.THEATRE_PAYLOAD=null;window.ACTOR_PAYLOAD=null;
  const stage=document.getElementById('stage'),renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#151922');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,.85));
  const sun=new THREE.DirectionalLight(0xfff8ef,1.35);sun.position.set(-450,650,800);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xcad8ff,.4);fill.position.set(500,150,-650);scene.add(fill);
  const camera=new THREE.PerspectiveCamera(45,1,1,16000),controls=new OrbitControls(camera,renderer.domElement);
  const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map();
  const textures=await Promise.all(materials.map(async info=>{
    const maps={};await Promise.all(Object.entries(info.faces).map(async([face,url])=>{
      if(!textureCache.has(url))textureCache.set(url,loader.loadAsync(url));
      const texture=await textureCache.get(url);texture.colorSpace=THREE.SRGBColorSpace;
      texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestMipmapLinearFilter;texture.wrapS=texture.wrapT=THREE.RepeatWrapping;
      texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());maps[face]=texture;
    }));return maps;
  }));
  const atlas=await loader.loadAsync(actors.atlas);atlas.colorSpace=THREE.SRGBColorSpace;atlas.magFilter=atlas.minFilter=THREE.NearestFilter;atlas.generateMipmaps=false;atlas.flipY=false;
  const actorMaterial=new THREE.MeshLambertMaterial({map:atlas,side:THREE.DoubleSide});
  actorMaterial.onBeforeCompile=shader=>{
    shader.vertexShader='attribute float tile; varying float vTile;\n'+shader.vertexShader.replace('#include <uv_vertex>','#include <uv_vertex>\nvTile=tile;');
    shader.fragmentShader='varying float vTile;\n'+shader.fragmentShader.replace('#include <map_fragment>',`vec2 tilePosition=vec2(mod(vTile,12.0),floor(vTile/12.0));
      vec2 atlasUv=(tilePosition*16.0+fract(vMapUv)*15.0+0.5)/192.0;
      diffuseColor*=texture2D(map,atlasUv);`);
  };
  const faceNames=['east','west','south','north','down','up'],normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],meshes=[],geometries=new Set(),plane=new THREE.Plane(new THREE.Vector3(0,-1,0),621);
  let renderedQuads=0,frames=0;
  function geometryFor(part,entries){
    const count=entries.reduce((sum,[m,f])=>sum+part.starts[m][f].length,0),positions=new Float32Array(count*12),ns=new Float32Array(count*12),uvs=new Float32Array(count*8),tiles=new Float32Array(count*4),indices=new Uint32Array(count*6);
    const [w,,d]=part.size;let j=0;
    for(const [material,face] of entries){
      const starts=part.starts[material][face],lengths=part.lengths[material][face],spans=part.spans[material][face],axis=face<2?2:0,cross=face<4?1:2;
      starts.forEach((index,i)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d],repeat=lengths[i],span=spans[i];
        for(let v=0;v<4;v++){
          const corner=corners[face][v];
          for(let k=0;k<3;k++){positions[j*12+v*3+k]=start[k]+corner[k]*(k===axis?repeat:k===cross?span:1);ns[j*12+v*3+k]=normals[face][k];}
          uvs[j*8+v*2]=corner[axis]*repeat;uvs[j*8+v*2+1]=corner[cross]*span;tiles[j*4+v]=material;
        }
        indices.set([j*4,j*4+1,j*4+2,j*4,j*4+2,j*4+3],j*6);j++;
      });
    }
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setAttribute('tile',new THREE.BufferAttribute(tiles,1));geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingSphere();geometries.add(geometry);renderedQuads+=count;return geometry;
  }
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.userData.modelId=part.modelId;group.position.set(...part.origin);scene.add(group);groups.push(group);
    group.userData.bounds=new THREE.Box3(group.position.clone(),group.position.clone().add(new THREE.Vector3(...part.size)));
    for(let m=0;m<materials.length;m++)for(let f=0;f<6;f++){
      if(!part.starts[m][f].length)continue;
      const key=`${m}:${f}`,info=materials[m];
      if(!materialCache.has(key))materialCache.set(key,new THREE.MeshLambertMaterial({map:textures[m][faceNames[f]],transparent:info.transparent,opacity:info.transparent?.5:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:info.emissive?info.color:0,emissiveIntensity:info.emissive?.2:0}));
      const mesh=new THREE.Mesh(geometryFor(part,[[m,f]]),materialCache.get(key));group.add(mesh);meshes.push(mesh);
    }
    document.getElementById('loading').textContent=`剧场构件 ${groups.length}/${parts.length}`;await new Promise(resolve=>setTimeout(resolve,0));
  }
  const actorMeshes=new Map();
  for(const part of actors.parts){
    const entries=[];for(let m=0;m<actors.materials.length;m++)for(let f=0;f<6;f++)if(part.starts[m][f].length)entries.push([m,f]);
    actorMeshes.set(part.id,new THREE.Mesh(geometryFor(part,entries),actorMaterial));
  }
  function makeActor(type,name){
    const root=new THREE.Group();root.name=name;root.position.set(...actors.rig.actor_root[name]);scene.add(root);
    const selected=actors.parts.filter(p=>p.metadata.actor===type),bones=new Map();
    for(const part of selected){const bone=new THREE.Group();bone.name=part.id;bone.userData.pivot=part.metadata.pivot;bones.set(part.id,bone);}
    for(const part of selected){
      const bone=bones.get(part.id),pivot=new THREE.Vector3(...part.metadata.pivot),parent=part.metadata.parent==='root'?root:bones.get(part.metadata.parent);
      bone.position.copy(pivot);if(parent!==root)bone.position.sub(new THREE.Vector3(...parent.userData.pivot));parent.add(bone);
      const mesh=actorMeshes.get(part.id).clone();mesh.position.copy(new THREE.Vector3(...part.origin).sub(pivot));bone.add(mesh);
    }
    return {root,bones};
  }
  const dominion=makeActor('dominion','dominion'),puppets={puppet_l:makeActor('puppet','puppet_l'),puppet_r:makeActor('puppet','puppet_r')};
  const puppetry=setupPuppetry({THREE,scene,dominion,puppets,rig:actors.rig});
  let activeModel='all',activeView='ensemble',axis='y',shellMode='cutaway',fitZoom=1,fitBox=new THREE.Box3(),playing=true,time=0,speed=1,last=performance.now();
  const views={
    ensemble:{label:'巨像与剧场',direction:[-.24,.19,1],center:[0,850,-320],half:[920,950,1000],distance:5400},
    front:{label:'正面操偶全景',direction:[0,.02,1],center:[0,860,-350],half:[900,960,1000],distance:5600},
    low:{label:'低位仰望巨像',direction:[0,-.4,1],center:[0,870,-450],half:[860,920,930],distance:4300},
    stageEye:{label:'厅内仰视',position:[0,65,490],center:[0,1040,-600],distance:1,fixed:true},
    leftHand:{label:'左侧平掌与长线',direction:[-.32,.06,1],center:[-235,475,160],half:[235,425,275],distance:2200},
    rightHand:{label:'右侧平掌与长线',direction:[.32,.06,1],center:[235,475,160],half:[235,425,275],distance:2200},
    palms:{label:'两掌俯视',direction:[-.24,1,.7],center:[0,800,80],half:[480,105,300],distance:2200},
    puppets:{label:'厅内双人偶',direction:[0,.04,1],center:[0,150,230],half:[310,110,70],distance:1700},
    dominion:{label:'巨像上身',direction:[-.2,.05,1],center:[0,1290,-1000],half:[850,525,290],distance:3500},
    oblique:{label:'剧场与敞口',direction:[-.5,.7,1],center:[0,320,0],half:[530,340,520],distance:2400},
    top:{label:'整体俯视',direction:[0,1,0],center:[0,850,-350],half:[950,950,1000],distance:5000}
  };
  const layerInput=document.getElementById('layer');
  function draw(){camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}
    return .9/limit;
  }
  function setView(name){
    activeView=name;const preset=views[name],target=preset.center?new THREE.Vector3(...preset.center):new THREE.Vector3(0,315,10);
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):new THREE.Box3(new THREE.Vector3(...data.bounds.min),new THREE.Vector3(...data.bounds.max));
    const direction=preset.position?new THREE.Vector3(...preset.position).sub(target).normalize():new THREE.Vector3(...preset.direction).normalize();camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);controls.target.copy(target);camera.position.copy(preset.position?new THREE.Vector3(...preset.position):target.clone().add(direction.multiplyScalar(preset.distance)));controls.update();fitZoom=preset.fixed?.68:zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));
  }
  function setLayer(value){const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;layerInput.value=value;document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();}
  function setAxis(value){axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(value);layerInput.min=data.bounds.min[index];layerInput.max=data.bounds.max[index];setLayer(+layerInput.max);}
  function setModel(id){
    activeModel=id;groups.forEach(g=>{const omitted=g.userData.modelId==='front'||g.name==='side_wall_-1'||g.name.startsWith('side_niche_-1_')||g.name.startsWith('wall_pier_-1_');g.visible=id==='all'&&(shellMode==='full'||!omitted);});
    dominion.root.visible=['all','ensemble','dominion'].includes(id);Object.values(puppets).forEach(a=>a.root.visible=['all','ensemble','puppets'].includes(id));puppetry.strings.visible=['all','ensemble','strings'].includes(id);
    document.querySelectorAll('[data-model]').forEach(b=>b.classList.toggle('active',b.dataset.model===id));document.getElementById('modelName').textContent='支配剧场 · 外置巨像操偶 F2';draw();
  }
  function setShellMode(mode){shellMode=mode;setModel('all');document.getElementById('shellFull').classList.toggle('active',mode==='full');document.getElementById('shellCutaway').classList.toggle('active',mode==='cutaway');}
  function setPlaying(value){playing=value;last=performance.now();document.getElementById('play').textContent=value?'暂停':'播放';document.getElementById('play').classList.toggle('active',value);}
  function setTime(value){time=value;puppetry.update(time);document.getElementById('time').value=time%16;document.getElementById('timeValue').textContent=`${(time%16).toFixed(1)} 秒`;draw();}
  for(const [id,label] of [['all','剧场共演'],['ensemble','仅演员与提线'],['dominion','乌合之众'],['puppets','两只人偶'],['strings','提线']]){const b=document.createElement('button');b.textContent=label;b.dataset.model=id;b.onclick=()=>setModel(id);document.getElementById('models').append(b);}
  for(const [id,view] of Object.entries(views)){const b=document.createElement('button');b.textContent=view.label;b.dataset.view=id;b.onclick=()=>setView(id);document.getElementById('views').append(b);}
  document.getElementById('play').onclick=()=>setPlaying(!playing);document.getElementById('rest').onclick=()=>{setPlaying(false);setTime(0);};document.getElementById('time').oninput=e=>{setPlaying(false);setTime(+e.target.value);};document.getElementById('speed').onchange=e=>speed=+e.target.value;
  document.getElementById('axis').onchange=e=>setAxis(e.target.value);layerInput.oninput=e=>setLayer(+e.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('reset').onclick=()=>{setShellMode('cutaway');setView('ensemble');setTime(0);};document.getElementById('shellFull').onclick=()=>setShellMode('full');document.getElementById('shellCutaway').onclick=()=>setShellMode('cutaway');
  document.getElementById('screenshot').onclick=()=>{draw();const a=document.createElement('a');a.download=`外置巨像-F2-${activeView}.png`;a.href=renderer.domElement.toDataURL();a.click();};document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  controls.addEventListener('change',draw);
  function resize(){const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();if(window.THEATRE_READY){fitZoom=views[activeView].fixed?.68:zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}}
  const observer=new ResizeObserver(resize);observer.observe(stage);
  window.TheatreViewer={setModel,setView,setAxis,setLayer,setShellMode,setPlaying,setTime,views,snapshot:()=>({activeModel,activeView,axis,shellMode,frames,renderedQuads,playing,time,animation:puppetry.snapshot(),drawCalls:renderer.info.render.calls,camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom}})};
  document.getElementById('actualSize').textContent='剧场宽1001格 · 巨像本体高1780格';
  document.getElementById('stats').textContent=`${data.total_blocks.toLocaleString()} 个建筑方块 · 乌合之众与双人偶 · 十条提线`;
  document.getElementById('loading').remove();resize();setShellMode('cutaway');setAxis('y');setTime(0);window.THEATRE_READY=true;setView('ensemble');
  let request;function animate(now){const delta=(now-last)/1000;last=now;if(playing)setTime(time+delta*speed);request=requestAnimationFrame(animate);}request=requestAnimationFrame(animate);
  window.addEventListener('pagehide',()=>{cancelAnimationFrame(request);observer.disconnect();controls.dispose();geometries.forEach(g=>g.dispose());materialCache.forEach(m=>m.dispose());actorMaterial.dispose();atlas.dispose();textureCache.forEach(async p=>(await p).dispose());renderer.dispose();},{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
