import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {createTreeSeaEffects} from './w15_book_fx_20261118.mjs';

async function main(){
  const bytes=Uint8Array.from(atob(window.W15_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W15_VOXEL_PAYLOAD=null;
  const stage=document.getElementById('stage'),scene=new THREE.Scene();
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#0c1320');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  scene.add(new THREE.AmbientLight(0xffffff,1.1));
  const sun=new THREE.DirectionalLight(0xfff6e5,1.55);sun.position.set(-700,1400,1000);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xb7d3ff,.75);fill.position.set(1000,700,-800);scene.add(fill);
  const camera=new THREE.OrthographicCamera(-1000,1000,1000,-1000,1,20000);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
  controls.minZoom=.4;controls.maxZoom=80;
  const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map();
  const maps=await Promise.all(materials.map(async info=>{
    const faces={};
    await Promise.all(Object.entries(info.faces).map(async([face,url])=>{
      if(!textureCache.has(url))textureCache.set(url,loader.loadAsync(url));
      const texture=await textureCache.get(url);texture.colorSpace=THREE.SRGBColorSpace;
      texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestMipmapLinearFilter;
      texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());faces[face]=texture;
    }));return faces;
  }));
  const faceNames=['east','west','south','north','down','up'],normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
  const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
  const book=new THREE.Group(),groups=[],meshes=[],plane=new THREE.Plane(new THREE.Vector3(0,-1,0),2000);
  scene.add(book);let quads=0;
  for(const part of parts){
    const group=new THREE.Group();group.position.set(...part.origin);group.userData.modelId=part.modelId;book.add(group);groups.push(group);
    const [w,,d]=part.size;
    for(let m=0;m<materials.length;m++)for(let face=0;face<6;face++){
      const starts=part.starts[m][face],lengths=part.lengths[m][face],spans=part.spans[m][face];
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
      const key=m+':'+face;
      if(!materialCache.has(key)){
        const info=materials[m],texture=maps[m][faceNames[face]];
        materialCache.set(key,new THREE.MeshLambertMaterial({map:texture,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:info.emissive?0xffffff:0,emissiveMap:texture,emissiveIntensity:info.emissive?.35:0}));
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=m;group.add(mesh);meshes.push(mesh);quads+=starts.length;
    }
    delete part.starts;delete part.lengths;delete part.spans;
    document.getElementById('loading').textContent='载入方块表面 '+groups.length+'/'+parts.length;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const fx=createTreeSeaEffects(THREE);scene.add(fx.group);
  const writing=new THREE.Group();scene.add(writing);
  const sweepMaterial=new THREE.MeshBasicMaterial({color:0xffcf66,transparent:true,opacity:.6,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending});
  const sweepPositions=new Float32Array(2*80*18),sweepGeometry=new THREE.BufferGeometry();
  sweepGeometry.setAttribute('position',new THREE.BufferAttribute(sweepPositions,3));const sweep=new THREE.Mesh(sweepGeometry,sweepMaterial);sweep.frustumCulled=false;writing.add(sweep);
  const pageHeight=(x,z)=>Math.round(185+88*Math.pow(Math.abs(x)/520,.76)+7*Math.pow(Math.abs(z)/360,6));
  const marker=new THREE.Mesh(new THREE.BoxGeometry(5,5,5),new THREE.MeshBasicMaterial({color:0x5df5d7,wireframe:true}));
  marker.position.set(...data.controller.map(v=>v+.5));marker.visible=false;scene.add(marker);
  const grid=new THREE.GridHelper(1408,88,0x415169,0x243043);grid.position.y=0;grid.visible=false;scene.add(grid);
  let time=0,working=true,paused=false,currentView='oblique',effectsVisible=true,frames=0,fitZoom=1;
  let fitBox=new THREE.Box3(new THREE.Vector3(-650,8,-490),new THREE.Vector3(650,630,500));
  const views={
    oblique:{label:'整体斜视',center:[0,285,0],half:[655,300,495],direction:[-.96,.82,1.35]},
    front:{label:'正面',center:[0,300,0],half:[650,300,490],direction:[0,.12,1]},
    top:{label:'俯视',center:[0,280,0],half:[650,300,490],direction:[0,1,0]},
    side:{label:'侧面',center:[0,290,0],half:[650,300,495],direction:[1,.28,0]},
    book:{label:'巨书近看',center:[0,193,5],half:[575,140,465],direction:[-.6,1.5,1.4]},
    pages:{label:'叠页近景',center:[-477,250,290],half:[72,49,95],direction:[-1,.45,1.25]},
    spine:{label:'书脊与光根',center:[0,165,100],half:[80,100,240],direction:[-.65,.7,1.2]},
    underside:{label:'书封底部',center:[0,175,0],half:[580,130,475],direction:[-.8,-.65,1.25]},
    tree:{label:'树冠细节',center:[0,409,-35],half:[347,210,270],direction:[-.6,.27,1.3]},
    sea:{label:'量子海',center:[0,46,0],half:[650,75,490],direction:[-.65,.8,1.35]},
    pixels:{label:'像素材质',center:[-518,263,224],half:[18,20,25],direction:[-.8,.65,1.25]}
  };
  function animateWriting(){
    writing.visible=effectsVisible&&working;
    const z=-305+(time*.065%1)*610;let offset=0;
    for(const side of [-1,1])for(let i=0;i<80;i++){
      const x=(68+i*5)*side,x1=(73+i*5)*side;
      const a=[x,pageHeight(x,z)+3,z],b=[x1,pageHeight(x1,z)+3,z],c=[x1,pageHeight(x1,z+2)+3,z+2],d=[x,pageHeight(x,z+2)+3,z+2];
      sweepPositions.set([...a,...b,...c,...a,...c,...d],offset);offset+=18;
    }sweepGeometry.attributes.position.needsUpdate=true;
  }
  function draw(){fx.update(time,working);animateWriting();renderer.render(scene,camera);frames++;}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}
    return .87/limit;
  }
  function setView(name){
    currentView=name;const view=views[name],target=new THREE.Vector3(...view.center),direction=new THREE.Vector3(...view.direction).normalize();
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).addScaledVector(direction,6000);controls.update();
    fitBox=new THREE.Box3(target.clone().sub(new THREE.Vector3(...view.half)),target.clone().add(new THREE.Vector3(...view.half)));
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===name));
  }
  function setTime(value){time=value;document.getElementById('time').value=time%90;document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();}
  function setMode(value){working=value==='work';document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;document.getElementById('pause').textContent=paused?'继续动画':'暂停动画';draw();}
  function setFx(value){effectsVisible=value;fx.group.visible=value;document.getElementById('effects').checked=value;draw();}
  function setGroup(id,visible){groups.filter(g=>g.userData.modelId===id).forEach(g=>g.visible=visible);draw();}
  for(const [id,view] of Object.entries(views)){const b=document.createElement('button');b.dataset.view=id;b.textContent=view.label;b.onclick=()=>setView(id);document.getElementById('views').append(b);}
  for(const model of data.models){
    const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;
    input.onchange=()=>setGroup(model.id,input.checked);label.append(input,model.label);document.getElementById('groups').append(label);
  }
  for(const material of materials){
    const row=document.createElement('div');row.className='material';const image=document.createElement('img');image.src=material.faces.north;
    const span=document.createElement('span');span.textContent=material.label;span.title=material.state;row.append(image,span);document.getElementById('materials').append(row);
  }
  document.getElementById('actualSize').textContent=`实体宽 ${data.sizeXYZ[0]} × 深 ${data.sizeXYZ[2]} × 高 ${data.sizeXYZ[1]} 格`;
  document.getElementById('modelStats').textContent=`${data.blocks.toLocaleString()} 个实体方块 · ${materials.length} 种原生方块材质`;
  document.getElementById('mode').onchange=e=>setMode(e.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);
  document.getElementById('time').oninput=e=>setTime(+e.target.value);document.getElementById('effects').onchange=e=>setFx(e.target.checked);
  document.getElementById('tree').onchange=e=>{fx.tree.visible=e.target.checked;draw();};
  document.getElementById('sea').onchange=e=>{fx.sea.visible=e.target.checked;draw();};
  document.getElementById('grid').onchange=e=>{grid.visible=e.target.checked;draw();};
  document.getElementById('controller').onchange=e=>{marker.visible=e.target.checked;draw();};
  document.getElementById('cut').oninput=e=>{plane.constant=+e.target.value;document.getElementById('cutValue').textContent=e.target.value;draw();};
  document.getElementById('reset').onclick=()=>setView('oblique');document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download='W15-树海巨书.png';link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('panelToggle').onclick=()=>{document.body.classList.toggle('panelHidden');};
  controls.addEventListener('change',draw);
  function resize(){
    const ratio=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);
    camera.left=-1000*w/h;camera.right=1000*w/h;camera.top=1000;camera.bottom=-1000;camera.updateProjectionMatrix();
    if(window.W15_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*ratio;camera.updateProjectionMatrix();draw();}
  }
  new ResizeObserver(resize).observe(stage);resize();setView('oblique');
  document.getElementById('loading').remove();window.W15_READY=true;
  let previous=0;
  function animate(now){const dt=Math.min((now-previous)/1000,.08);previous=now;if(!paused)setTime(time+dt);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({currentView,time,working,paused,effectsVisible,quads,frames,blocks:data.blocks,sizeXYZ:data.sizeXYZ,controller:data.controller,
    fx:fx.stats,rendererCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,visibleGroups:[...new Set(groups.filter(g=>g.visible).map(g=>g.userData.modelId))]});
  window.W15Viewer={setView,setTime,setMode,setPaused,setFx,setGroup,snapshot};
}
main().catch(error=>{document.getElementById('loading').textContent='预览载入失败：'+error.message;console.error(error);});
