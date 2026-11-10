/** W02原案独立构件试览：一次上传体素表面，每帧只改组矩阵。 */
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main() {
  const bytes=Uint8Array.from(atob(window.W02_V4_PAYLOAD),c=>c.charCodeAt(0));
  const config=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W02_V4_PAYLOAD=null;
  const {data,audit,materials}=config, stage=document.getElementById('stage');
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5)); renderer.setClearColor('#0b1624');
  stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xe8f4ff,1.1));
  const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(-600,1000,900);scene.add(sun);
  const fill=new THREE.DirectionalLight(0x8ed7ff,.9);fill.position.set(700,400,-600);scene.add(fill);
  const camera=new THREE.OrthographicCamera(-500,500,400,-400,.1,8000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  const offset=new THREE.Vector3(...data.blueprint_to_export_offset_xyz);
  const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map();
  const textures=await Promise.all(materials.map(async info=>{
    const maps={};
    await Promise.all(Object.entries(info.faces).map(async([face,url])=>{
      if(!textureCache.has(url))textureCache.set(url,loader.loadAsync(url));
      const texture=await textureCache.get(url);texture.colorSpace=THREE.SRGBColorSpace;
      texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestFilter;
      texture.wrapS=texture.wrapT=THREE.RepeatWrapping;maps[face]=texture;
    }));return maps;
  }));
  const normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const faceNames=['east','west','south','north','down','up'];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],
    [[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],
    [[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const groups=[],allMeshes=[],motions=new Map(data.motions.map(m=>[m.id,m]));
  let renderedQuads=0;
  for(const part of config.parts) {
    const group=new THREE.Group();group.name=part.id;
    const motion=motions.get(part.id), origin=new THREE.Vector3(...part.origin);
    const pivot=motion?new THREE.Vector3(...motion.pivot_blueprint).add(offset):origin.clone();
    group.position.copy(pivot);group.userData.pivot=pivot.clone();group.userData.motion=motion;
    scene.add(group);groups.push(group);
    const [w,,d]=part.size;
    for(let material=0;material<materials.length;material++)for(let face=0;face<6;face++) {
      const starts=part.starts[material][face],lengths=part.lengths[material][face];
      if(!starts.length)continue;
      const positions=new Float32Array(starts.length*18),ns=new Float32Array(starts.length*18),uvs=new Float32Array(starts.length*12);
      const order=[0,1,2,0,2,3];
      starts.forEach((index,j)=>{
        const start=[index%w,Math.floor(index/(w*d)),Math.floor(index/w)%d];
        const repeat=lengths[j],axis=face<2?2:0;
        for(let v=0;v<6;v++) {
          const corner=corners[face][order[v]],point=corner.map((n,k)=>n*(k===axis?repeat:1)+start[k]);
          for(let k=0;k<3;k++){positions[j*18+v*3+k]=point[k]+origin.getComponent(k)-pivot.getComponent(k);ns[j*18+v*3+k]=normals[face][k];}
          const u=face<4?(corner[axis]?repeat:0):(corner[0]?repeat:0);
          const vv=face<4?corner[1]:corner[2];uvs[j*12+v*2]=u;uvs[j*12+v*2+1]=vv;
        }
      });
      const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      geometry.setAttribute('normal',new THREE.BufferAttribute(ns,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));
      geometry.computeBoundingSphere();
      const key=material+':'+face;
      if(!materialCache.has(key)) {
        const info=materials[material],emits=info.state==='minecraft:sea_lantern';
        materialCache.set(key,new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],
          transparent:!!info.transparent,opacity:info.transparent?.42:1,depthWrite:!info.transparent,
          alphaTest:info.transparent?.01:.05,side:THREE.DoubleSide,
          emissive:emits?0x76f0ff:0x000000,emissiveIntensity:emits?.28:0}));
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));
      mesh.userData={material,glass:materials[material].transparent};group.add(mesh);allMeshes.push(mesh);renderedQuads+=starts.length;
    }
    // 给大构件加载一次事件循环机会，避免页面无响应。
    await new Promise(resolve=>setTimeout(resolve,0));
    document.getElementById('loading').textContent=`完整构件 ${groups.length}/${config.parts.length}`;
  }
  if(renderedQuads!==audit.viewer_rendered_quads)throw new Error('完整表面数量不同');
  const clippingPlane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.size[1]+1);
  renderer.localClippingEnabled=true;
  materialCache.forEach(m=>m.clippingPlanes=[clippingPlane]);
  const portsGroup=new THREE.Group();portsGroup.visible=false;scene.add(portsGroup);
  for(const item of [dictControl(),...data.ports]) {
    const box=new THREE.Box3(new THREE.Vector3(...item.pos).addScalar(-.8),new THREE.Vector3(...item.pos).addScalar(1.8));
    const helper=new THREE.Box3Helper(box,0xffcc55);portsGroup.add(helper);
  }
  function dictControl(){return {pos:data.controller};}
  let seconds=0,playing=false,sliced=false,disposed=false,timer=0,last=performance.now(),frames=0;
  const rotate=new THREE.Quaternion(),axisX=new THREE.Vector3(1,0,0),axisY=new THREE.Vector3(0,1,0),axisZ=new THREE.Vector3(0,0,1);
  function apply() {
    for(const group of groups) {
      group.position.copy(group.userData.pivot);group.quaternion.identity();group.scale.setScalar(1);const motion=group.userData.motion;
      if(!motion||sliced)continue;
      const deg=seconds*Math.PI/180;
      if(motion.mode==='middle')group.quaternion.setFromAxisAngle(axisY,deg*2).multiply(rotate.setFromAxisAngle(axisX,-deg*3));
      if(motion.mode==='inner')group.quaternion.setFromAxisAngle(axisX,deg*3).multiply(rotate.setFromAxisAngle(axisZ,deg*4));
      if(motion.mode==='cage')group.quaternion.setFromAxisAngle(axisY,-deg*2);
      if(motion.mode==='voxels') {
        group.quaternion.setFromAxisAngle(axisY,deg*3);group.scale.setScalar(1+Math.sin(seconds*Math.PI/4)*.025);
      }else group.scale.setScalar(1);
      if(motion.mode==='wing')group.position.y+=Math.sin(seconds*Math.PI/4+Math.abs(motion.pivot_blueprint[2])*.02)*1.5;
      if(motion.mode==='scan')group.position.y-=seconds*8%80;
    }
    document.getElementById('time').value=seconds;document.getElementById('timeLabel').textContent=seconds.toFixed(1)+' 秒';
  }
  function draw(){if(!disposed){renderer.render(scene,camera);frames++;}}
  const initialBounds=new THREE.Box3(new THREE.Vector3(0,0,0),new THREE.Vector3(...data.size));
  const sweptBounds=initialBounds.clone();
  for(const part of config.parts) {
    const motion=motions.get(part.id);if(!motion)continue;
    const pivot=new THREE.Vector3(...motion.pivot_blueprint).add(offset),lo=new THREE.Vector3(...part.origin),hi=lo.clone().add(new THREE.Vector3(...part.size));
    let radius=0;
    for(const x of [lo.x,hi.x])for(const y of [lo.y,hi.y])for(const z of [lo.z,hi.z])radius=Math.max(radius,pivot.distanceTo(new THREE.Vector3(x,y,z)));
    if(['middle','inner','cage','voxels'].includes(motion.mode)) {
      radius*=1.025;sweptBounds.expandByPoint(pivot.clone().addScalar(radius));sweptBounds.expandByPoint(pivot.clone().addScalar(-radius));
    }else {sweptBounds.expandByPoint(lo.clone().add(new THREE.Vector3(0,motion.mode==='scan'?-80:-2,0)));sweptBounds.expandByPoint(hi.clone().add(new THREE.Vector3(0,2,0)));}
  }
  function setView(name) {
    const target=sweptBounds.getCenter(new THREE.Vector3());let direction=new THREE.Vector3(-1,.7,1.25);
    if(name==='orthofront')direction.set(0,0,1);
    if(name==='side')direction.set(1,0,0);
    if(name==='top')direction.set(0,1,.001);
    if(name==='core')target.copy(offset).add(new THREE.Vector3(0,148,0));
    if(name==='controller')target.set(...data.controller);
    controls.target.copy(target);camera.up.set(0,1,0);camera.position.copy(target).add(direction.normalize().multiplyScalar(1800));
    controls.update();camera.zoom=1;camera.updateMatrixWorld();camera.updateProjectionMatrix();
    const bounds=name==='core'?new THREE.Box3(target.clone().addScalar(-74),target.clone().addScalar(74)):
      name==='controller'?new THREE.Box3(target.clone().add(new THREE.Vector3(-52,-20,-35)),target.clone().add(new THREE.Vector3(52,32,8))):sweptBounds;
    let limit=0;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]) {
      const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));
    }
    camera.zoom=.88/Math.max(limit,.01);camera.updateProjectionMatrix();draw();
  }
  function resize(){const {width,height}=stage.getBoundingClientRect();renderer.setSize(width,height);const aspect=width/height;camera.left=-500*aspect;camera.right=500*aspect;camera.top=500;camera.bottom=-500;camera.updateProjectionMatrix();draw();}
  function schedule(){clearTimeout(timer);if(!playing||document.hidden||disposed)return;timer=setTimeout(()=>{
    const now=performance.now();seconds=(seconds+Math.min(.2,(now-last)/1000))%360;last=now;apply();draw();schedule();
  },1000/24);}
  function pause(value){playing=!value;document.getElementById('play').textContent=playing?'暂停原案动画':'播放原案动画';last=performance.now();schedule();}
  function seek(value){seconds=Math.max(0,Math.min(360,value));apply();draw();}
  controls.addEventListener('change',draw);
  document.querySelectorAll('[data-view]').forEach(e=>e.onclick=()=>setView(e.dataset.view));
  document.querySelectorAll('[data-part]').forEach(e=>e.onchange=()=>{groups.find(g=>g.name===e.dataset.part).visible=e.checked;draw();});
  document.getElementById('play').onclick=()=>pause(playing);
  document.getElementById('reset').onclick=()=>{pause(true);seek(0);setView('front');};
  document.getElementById('time').oninput=e=>{pause(true);seek(+e.target.value);};
  document.getElementById('glass').onchange=e=>{allMeshes.forEach(m=>{if(m.userData.glass)m.visible=e.target.checked;});draw();};
  document.getElementById('ports').onchange=e=>{portsGroup.visible=e.target.checked;draw();};
  document.getElementById('layer').oninput=e=>{
    pause(true);sliced=+e.target.value<data.size[1]-1;clippingPlane.constant=+e.target.value+1.01;
    document.getElementById('layerLabel').textContent=e.target.value;apply();draw();
  };
  new ResizeObserver(resize).observe(stage);document.addEventListener('visibilitychange',()=>{last=performance.now();schedule();});
  window.addEventListener('pagehide',()=>{
    disposed=true;clearTimeout(timer);controls.dispose();renderer.dispose();
    allMeshes.forEach(m=>m.geometry.dispose());materialCache.forEach(m=>m.dispose());
    textureCache.forEach(async p=>(await p).dispose());
  },{once:true});
  document.getElementById('loading').remove();document.getElementById('stats').textContent=`${groups.length}个完整独立构件 / ${renderedQuads.toLocaleString()}个合并表面；左键旋转、右键平移、滚轮缩放。`;
  resize();apply();setView('front');
  window.W02V4={config,scene,camera,renderer,controls,groups,pause,seek,setView,
    snapshot:()=>({seconds,playing,sliced,frames,renderedQuads,sweptBounds:{min:sweptBounds.min.toArray(),max:sweptBounds.max.toArray()},
      transforms:groups.map(g=>({id:g.name,position:g.position.toArray(),rotation:g.quaternion.toArray(),scale:g.scale.toArray()}))})};
  window.W02_V4_READY=true;
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent='预览加载失败：'+error.message;});
