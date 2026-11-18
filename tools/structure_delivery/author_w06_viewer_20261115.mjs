import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {makeEffects} from './author_w06_effects_20261115.mjs';

async function main(){
  const bytes=Uint8Array.from(atob(window.W06_AUTHOR_PAYLOAD),c=>c.charCodeAt(0));
  const config=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W06_AUTHOR_PAYLOAD=null;
  const {data,parts,materials}=config,stage=document.getElementById('stage');
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor('#08131f');renderer.localClippingEnabled=true;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.96;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.background=new THREE.Color('#07111f');
  scene.add(new THREE.HemisphereLight('#d8f8ff','#263246',2));
  for(const [position,intensity,color] of [[[-400,900,-500],3,'#f5fbff'],[[900,520,640],2.2,'#a7d9f4'],[[400,620,1100],1.4,'#f4d68b']]){
    const lamp=new THREE.DirectionalLight(color,intensity);lamp.position.set(...position);scene.add(lamp);
  }
  const camera=new THREE.OrthographicCamera(-500,500,400,-400,.1,8000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  const loader=new THREE.TextureLoader();
  const maps=await Promise.all(materials.map(async info=>{
    const map=await loader.loadAsync(info.texture);map.colorSpace=THREE.SRGBColorSpace;
    map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestMipmapLinearFilter;
    map.wrapS=map.wrapT=THREE.RepeatWrapping;map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return map;
  }));
  const materialObjects=materials.map((info,i)=>new THREE.MeshStandardMaterial({map:maps[i],color:'#ffffff',
    roughness:i===1?.36:i===3?.28:.66,metalness:i===1||i===3||i===4?.52:.18,
    transparent:info.transparent,opacity:info.opacity,depthWrite:!info.transparent,
    alphaTest:info.alphaTest||.01,emissive:info.emissive,emissiveMap:maps[i],
    emissiveIntensity:info.emissiveIntensity,side:THREE.DoubleSide,clippingPlanes:[plane]}));
  const normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],
    [[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],
    [[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],order=[0,1,2,0,2,3];let quads=0;
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.userData=part;
    const pivot=new THREE.Vector3(...(part.metadata.motion?.pivot||part.origin));
    group.position.copy(pivot);scene.add(group);groups.push(group);
    const [w,,d]=part.size;
    for(let m=0;m<materials.length;m++){
      const count=part.starts[m].reduce((n,starts)=>n+starts.length,0);
      if(count===0)continue;
      const positions=new Float32Array(count*18),ns=new Float32Array(count*18),uvs=new Float32Array(count*12);let j=0;
      for(let face=0;face<6;face++)part.starts[m][face].forEach((index,k)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d],repeat=part.lengths[m][face][k],axis=face<2?2:0;
        for(let v=0;v<6;v++){
          const c=corners[face][order[v]];
          for(let a=0;a<3;a++){
            positions[j*18+v*3+a]=c[a]*(a===axis?repeat:1)+start[a]+part.origin[a]-pivot.getComponent(a)-.5;
            ns[j*18+v*3+a]=normals[face][a];
          }
          uvs[j*12+v*2]=face<4?(c[axis]?repeat:0):(c[0]?repeat:0);
          uvs[j*12+v*2+1]=face<4?c[1]:c[2];
        }
        j++;
      });
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.computeBoundingSphere();
      const mesh=new THREE.Mesh(geometry,materialObjects[m]);mesh.userData.material=m;group.add(mesh);quads+=count;
    }
    document.getElementById('loading').textContent=`载入原文构件 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const center=data.center||[(data.bounds.min[0]+data.bounds.max[0])/2,0,(data.bounds.min[2]+data.bounds.max[2])/2];
  const fx=makeEffects(scene,plane,center);
  const bounds=new THREE.Box3(new THREE.Vector3(...data.bounds.min).addScalar(-.5),new THREE.Vector3(...data.bounds.max).addScalar(.5));
  const nominalBounds=data.nominal_bounds_xyz;
  const nominal=new THREE.Box3Helper(new THREE.Box3(new THREE.Vector3(...nominalBounds.min).addScalar(-.5),new THREE.Vector3(...nominalBounds.max).addScalar(.5)),0xe5c866);
  nominal.visible=false;scene.add(nominal);
  const grid=new THREE.GridHelper(900,45,0x55718a,0x30445d);grid.position.set(center[0],nominalBounds.min[1]-1,center[2]);grid.visible=false;scene.add(grid);
  const marker=new THREE.Group();marker.visible=false;scene.add(marker);
  const controller=data.controller;
  marker.add(new THREE.Box3Helper(new THREE.Box3(new THREE.Vector3(...controller).addScalar(-.5),new THREE.Vector3(...controller).addScalar(.5)),0xffd86e));
  const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
  const bloom=new UnrealBloomPass(new THREE.Vector2(1000,800),.34,.4,1.05);composer.addPass(bloom);composer.addPass(new OutputPass());
  let time=0,playing=true,running=false,fixed=false,activeView='front';
  const clock=new THREE.Clock(),hiddenMaterials=new Set();
  function pose(){
    for(const group of groups){
      const motion=group.userData.metadata.motion;if(!motion)continue;
      const speed=motion.speed??(running?.025:.008);
      group.quaternion.setFromAxisAngle(new THREE.Vector3(...motion.axis).normalize(),time*speed*(motion.sign||1));
    }
    maps[7].offset.set(time*.018,Math.sin(time*.23)*.04);
    fx.update(time,running);fx.root.visible=document.getElementById('effects').checked;
    document.getElementById('timeValue').textContent=time.toFixed(1)+' s';
    if(fixed)document.getElementById('time').value=time;
  }
  function draw(){pose();composer.render();}
  function fit(view){
    activeView=view;const item=data.views[view],target=new THREE.Vector3(...item.center),direction=new THREE.Vector3(...item.direction).normalize();
    const box=item.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...item.half)),target.clone().add(new THREE.Vector3(...item.half))):bounds;
    controls.target.copy(target);camera.up.copy(Math.abs(direction.y)>.98?new THREE.Vector3(0,0,-1):new THREE.Vector3(0,1,0));camera.position.copy(target).addScaledVector(direction,2500);
    camera.zoom=1;controls.update();camera.updateMatrixWorld();camera.updateProjectionMatrix();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
    }
    camera.zoom=.9/limit;camera.updateProjectionMatrix();document.getElementById('viewName').textContent=item.label;
    document.querySelectorAll('[data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===view));draw();
  }
  function resize(){
    const {width,height}=stage.getBoundingClientRect();renderer.setSize(width,height);composer.setSize(width,height);
    camera.left=-500*width/height;camera.right=500*width/height;camera.top=500;camera.bottom=-500;camera.updateProjectionMatrix();fit(activeView);
  }
  function visibility(){
    let visible=0;
    for(const group of groups){
      group.visible=document.querySelector(`[data-part="${group.name}"]`).checked;
      for(const mesh of group.children)mesh.visible=!hiddenMaterials.has(mesh.userData.material);
      if(group.visible)visible++;
    }
    document.getElementById('counts').textContent=`${visible}/${groups.length} 个独立构件 · ${quads.toLocaleString()} 个表面`;
    draw();
  }
  function mode(value){
    running=value==='work';document.getElementById('mode').value=value;
    materialObjects[5].emissiveIntensity=running?1.65:materials[5].emissiveIntensity;
    document.getElementById('modeName').textContent=running?'工作 · 冰蓝主束与金丝贯通':'待机 · 冰晶与极光环境';draw();
  }
  document.querySelectorAll('[data-view]').forEach(e=>e.onclick=()=>fit(e.dataset.view));
  document.querySelectorAll('[data-part]').forEach(e=>e.onchange=visibility);
  document.querySelectorAll('[data-material]').forEach(e=>e.onchange=()=>{e.checked?hiddenMaterials.delete(+e.dataset.material):hiddenMaterials.add(+e.dataset.material);visibility();});
  document.getElementById('allParts').onclick=()=>{document.querySelectorAll('[data-part]').forEach(e=>e.checked=true);visibility();};
  document.getElementById('mode').onchange=e=>mode(e.target.value);
  document.getElementById('pause').onclick=e=>{playing=!playing;fixed=!playing;e.target.textContent=playing?'暂停动画':'继续动画';};
  document.getElementById('time').oninput=e=>{time=+e.target.value;playing=false;fixed=true;document.getElementById('pause').textContent='继续动画';draw();};
  document.getElementById('layer').oninput=e=>{plane.constant=+e.target.value+.51;document.getElementById('layerValue').textContent=e.target.value;draw();};
  document.getElementById('bloom').onchange=e=>{bloom.enabled=e.target.checked;draw();};
  document.getElementById('effects').onchange=draw;
  document.getElementById('showGrid').onchange=e=>{grid.visible=e.target.checked;draw();};
  document.getElementById('showBounds').onchange=e=>{nominal.visible=e.target.checked;draw();};
  document.getElementById('ports').onchange=e=>{marker.visible=e.target.checked;draw();};
  document.getElementById('reset').onclick=()=>{hiddenMaterials.clear();document.querySelectorAll('[data-part],[data-material]').forEach(e=>e.checked=true);plane.constant=data.bounds.max[1]+1;document.getElementById('layer').value=data.bounds.max[1];visibility();fit('front');};
  document.getElementById('saveImage').onclick=()=>{draw();const link=document.createElement('a');link.download='W06作者原案-'+(running?'工作':'待机')+'.png';link.href=renderer.domElement.toDataURL();link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():stage.requestFullscreen();
  controls.addEventListener('change',draw);new ResizeObserver(resize).observe(stage);
  renderer.setAnimationLoop(()=>{const dt=clock.getDelta();if(playing){time=(time+dt)%60;draw();}});
  document.getElementById('loading').remove();resize();visibility();fit('front');
  window.W06Author={config,scene,renderer,camera,controls,groups,fx,composer,fit,mode,
    freeze(t=12){time=t;playing=false;fixed=true;document.getElementById('pause').textContent='继续动画';draw();},
    render:draw,snapshot(){return {time,running,parts:groups.length,quads,bounds:data.bounds,
      transforms:groups.filter(g=>g.userData.metadata.motion).map(g=>({id:g.name,position:g.position.toArray(),quaternion:g.quaternion.toArray()}))};}};
  window.W06_AUTHOR_READY=true;
}
main();
