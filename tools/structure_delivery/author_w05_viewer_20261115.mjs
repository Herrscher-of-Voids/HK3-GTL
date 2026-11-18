import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {makeEffects} from './author_w05_effects_20261115.mjs';

async function main() {
  const bytes=Uint8Array.from(atob(window.W05_AUTHOR_PAYLOAD),c=>c.charCodeAt(0));
  const config=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W05_AUTHOR_PAYLOAD=null;
  const {data,parts,materials}=config,stage=document.getElementById('stage');
  const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor('#0b161b');renderer.localClippingEnabled=true;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.92;stage.append(renderer.domElement);
  const scene=new THREE.Scene();
  scene.add(new THREE.HemisphereLight('#d5fff4','#213436',2));
  for(const [position,intensity,color] of [[[-500,800,-600],2.9,'#f0fff9'],[[600,450,500],2,'#a3dced'],[[100,300,-700],.7,'#d3fbe8']]) {
    const lamp=new THREE.DirectionalLight(color,intensity);lamp.position.set(...position);scene.add(lamp);
  }
  const camera=new THREE.OrthographicCamera(-500,500,400,-400,.1,7000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  const loader=new THREE.TextureLoader();
  const maps=await Promise.all(materials.map(async info=>{
    const map=await loader.loadAsync(info.texture);map.colorSpace=THREE.SRGBColorSpace;
    map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestMipmapLinearFilter;
    map.wrapS=map.wrapT=THREE.RepeatWrapping;map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return map;
  }));
  const materialObjects=materials.map((info,i)=>new THREE.MeshStandardMaterial({map:maps[i],color:'#ffffff',
    roughness:i===1?.37:.7,metalness:i===1?.45:.22,transparent:info.transparent,opacity:info.opacity,
    depthWrite:!info.transparent||i===6,alphaTest:info.alphaTest || .01,
    emissive:info.emissive,emissiveMap:maps[i],emissiveIntensity:info.emissiveIntensity,
    side:THREE.DoubleSide,clippingPlanes:[plane]}));
  const normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],
    [[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],
    [[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],meshes=[],order=[0,1,2,0,2,3];let quads=0;
  for(const part of parts) {
    const group=new THREE.Group();group.name=part.id;group.userData=part;
    const pivot=new THREE.Vector3(...(part.metadata.motion?.pivot || part.origin));
    group.position.copy(pivot);scene.add(group);groups.push(group);
    const [w,,d]=part.size;
    for(let m=0;m<materials.length;m++) {
      const count=part.starts[m].reduce((n,starts)=>n+starts.length,0);
      if(count===0)continue;
      const positions=new Float32Array(count*18),ns=new Float32Array(count*18),uvs=new Float32Array(count*12);let j=0;
      for(let face=0;face<6;face++)part.starts[m][face].forEach((index,k)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d],repeat=part.lengths[m][face][k],axis=face<2?2:0;
        for(let v=0;v<6;v++) {
          const c=corners[face][order[v]];
          for(let a=0;a<3;a++) {
            positions[j*18+v*3+a]=c[a]*(a===axis?repeat:1)+start[a]+part.origin[a]-pivot.getComponent(a)-.5;
            ns[j*18+v*3+a]=normals[face][a];
          }
          uvs[j*12+v*2]=face<4?(c[axis]?repeat:0):(c[0]?repeat:0);
          uvs[j*12+v*2+1]=face<4?c[1]:c[2];
        }j++;
      });
      const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(positions,3));
      g.setAttribute('normal',new THREE.BufferAttribute(ns,3));g.setAttribute('uv',new THREE.BufferAttribute(uvs,2));g.computeBoundingSphere();
      const mesh=new THREE.Mesh(g,materialObjects[m]);mesh.userData.material=m;
      group.add(mesh);meshes.push(mesh);quads+=count;
    }
    document.getElementById('loading').textContent=`载入原案构件 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const fx=makeEffects(scene,parts,groups,plane);
  const bounds=new THREE.Box3(new THREE.Vector3(...data.bounds.min).addScalar(-.5),new THREE.Vector3(...data.bounds.max).addScalar(.5));
  const nominal=new THREE.Box3Helper(new THREE.Box3(new THREE.Vector3(-277,0,-350),new THREE.Vector3(277,320,350)),0xe1b566);
  nominal.visible=false;scene.add(nominal);
  const grid=new THREE.GridHelper(800,40,0x40595b,0x20373a);grid.position.y=-1;grid.visible=false;scene.add(grid);
  const marker=new THREE.Group();marker.visible=false;scene.add(marker);
  const controllerBox=new THREE.Box3Helper(new THREE.Box3(new THREE.Vector3(-1.5,10.5,-346.5),new THREE.Vector3(1.5,13.5,-343.5)),0xffca66);marker.add(controllerBox);
  const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
  const bloom=new UnrealBloomPass(new THREE.Vector2(1000,800),.3,.4,1.15);composer.addPass(bloom);composer.addPass(new OutputPass());
  let time=0,playing=true,running=false,fixed=false,activeView='front';
  const clock=new THREE.Clock();
  const hiddenMaterials=new Set();
  function pose() {
    for(const group of groups) {
      const m=group.userData.metadata.motion;
      if(!m)continue;
      const speeds={turbine:running?.8:.12,gyro:.12,crown:running?1.75:0,vortex:running?.9:.22,core:0};
      const speed=m.speed ?? speeds[m.kind];
      if(m.axis)group.quaternion.setFromAxisAngle(new THREE.Vector3(...m.axis).normalize(),time*speed*(m.sign || 1));
      if(m.kind==='core')group.position.y=m.pivot[1]+Math.sin(time*.6)*1.2;
    }
    maps[5].offset.set(time*.025,Math.sin(time*.3)*.06);
    fx.update(time,running);
    fx.root.visible=document.getElementById('effects').checked;
    document.getElementById('timeValue').textContent=time.toFixed(1)+' s';
    if(fixed)document.getElementById('time').value=time;
  }
  function draw(){pose();composer.render();}
  function fit(view) {
    activeView=view;
    const item=data.views[view],target=new THREE.Vector3(...item.center),direction=new THREE.Vector3(...item.direction).normalize();
    const box=item.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...item.half)),target.clone().add(new THREE.Vector3(...item.half))):bounds;
    controls.target.copy(target);camera.up.set(0,1,0);camera.position.copy(target).addScaledVector(direction,1800);
    camera.zoom=1;controls.update();camera.updateMatrixWorld();camera.updateProjectionMatrix();
    let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]) {
      const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
    }
    camera.zoom=.9/limit;camera.updateProjectionMatrix();
    document.getElementById('viewName').textContent=item.label;
    document.querySelectorAll('[data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===view));draw();
  }
  function resize() {
    const {width,height}=stage.getBoundingClientRect();renderer.setSize(width,height);composer.setSize(width,height);
    camera.left=-500*width/height;camera.right=500*width/height;camera.top=500;camera.bottom=-500;camera.updateProjectionMatrix();fit(activeView);
  }
  function visibility() {
    let count=0;
    for(const group of groups) {
      group.visible=document.querySelector(`[data-part="${group.name}"]`).checked;
      for(const mesh of group.children)mesh.visible=!hiddenMaterials.has(mesh.userData.material);
      if(group.visible)count++;
    }
    document.getElementById('counts').textContent=`${count}/${groups.length} 个原案构件 · ${quads.toLocaleString()} 个表面`;
    draw();
  }
  function mode(value) {
    running=value==='work';document.getElementById('mode').value=value;
    const core=materialObjects[5];core.emissive.set(running?'#ffffff':materials[5].emissive);
    core.emissiveIntensity=running?2.2:materials[5].emissiveIntensity;
    core.map=core.emissiveMap=running?null:maps[5];core.needsUpdate=true;
    document.getElementById('modeName').textContent=running?'工作 · MAX+满载':'待机 · 缓速运行';draw();
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
  document.getElementById('reset').onclick=()=>{hiddenMaterials.clear();document.querySelectorAll('[data-part],[data-material]').forEach(e=>e.checked=true);
    plane.constant=data.bounds.max[1]+1;document.getElementById('layer').value=data.bounds.max[1];visibility();fit('front');};
  document.getElementById('saveImage').onclick=()=>{draw();const link=document.createElement('a');link.download='W05作者原案-'+(running?'工作':'待机')+'.png';link.href=renderer.domElement.toDataURL();link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():stage.requestFullscreen();
  controls.addEventListener('change',draw);new ResizeObserver(resize).observe(stage);
  renderer.setAnimationLoop(()=>{const dt=clock.getDelta();if(playing){time=(time+dt)%60;draw();}});
  document.getElementById('loading').remove();resize();visibility();fit('front');
  window.W05Author={config,scene,renderer,camera,controls,groups,fx,composer,fit,mode,
    freeze(t=12){time=t;playing=false;fixed=true;document.getElementById('pause').textContent='继续动画';draw();},
    render:draw,snapshot(){return {time,running,parts:groups.length,quads,bounds:data.bounds,
      transforms:groups.filter(g=>g.userData.metadata.motion).map(g=>({id:g.name,position:g.position.toArray(),quaternion:g.quaternion.toArray()}))};}};
  window.W05_AUTHOR_READY=true;
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=error.message;});
