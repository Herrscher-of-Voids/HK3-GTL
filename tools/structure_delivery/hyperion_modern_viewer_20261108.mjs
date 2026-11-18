/** 最新评审界面所用的按需绘制、稀疏表面与原版特殊模型适配。 */
import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';

async function start(){
 const bytes=Uint8Array.from(atob(window.HYPERION_PAYLOAD),c=>c.charCodeAt(0));window.HYPERION_PAYLOAD=null;
 const data=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
 const [W,H,D]=data.size,L=Math.max(W,H,D),stage=document.getElementById('stage'),loading=document.getElementById('loading');
 const scene=new THREE.Scene();scene.background=new THREE.Color('#121b2b');
 const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;stage.prepend(renderer.domElement);
 const camera=new THREE.OrthographicCamera(-L,L,L,-L,.1,L*16),controls=new OrbitControls(camera,renderer.domElement);
 controls.enableDamping=false;controls.minZoom=.15;controls.maxZoom=100;controls.maxPolarAngle=Math.PI*.995;
 scene.add(new THREE.HemisphereLight(0xc8e5ff,0x384458,2.3));
 for(const [color,power,pos] of [[0xfff4e7,3,[-L,L,-L]],[0x81c7ed,1.3,[L,L*.3,L]]]){const light=new THREE.DirectionalLight(color,power);light.position.set(...pos);scene.add(light);}
 const grid=new THREE.GridHelper(L*1.2,24,0x496078,0x25354b);grid.position.set(W/2,-.2,D/2);grid.visible=false;scene.add(grid);
 const box=new THREE.Box3(new THREE.Vector3(0,0,0),new THREE.Vector3(W,H,D));
 const center=new THREE.Vector3(W/2,H*.48,D/2),matrix=new THREE.Matrix4(),scale=new THREE.Vector3(),position=new THREE.Vector3();
 const loader=new THREE.TextureLoader(),textureCache=new Map(),materialCache=new Map(),pending=[];
 const meshes=[],hidden=new Set(),stateCounts=data.states.map(s=>{let total=0;return s.layer_counts.map(n=>total+=n);});
 let renderQueued=false,ready=false;
 function requestRender(){if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;renderer.render(scene,camera);});}
 controls.addEventListener('change',requestRender);
 function texture(name){
  if(textureCache.has(name))return textureCache.get(name);
  let ok,fail;pending.push(new Promise((a,b)=>{ok=a;fail=b;}));
  const t=loader.load(data.textures[name].url,ok,undefined,fail);t.colorSpace=THREE.SRGBColorSpace;t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;t.generateMipmaps=false;t.wrapS=t.wrapT=THREE.RepeatWrapping;textureCache.set(name,t);return t;
 }
 function material(name,glass,repeatAxis=-1){
  const transparent=glass&&data.textures[name].alpha,key=name+'|'+transparent+'|'+repeatAxis;
  if(materialCache.has(key))return materialCache.get(key);
  const m=new THREE.MeshStandardMaterial({map:texture(name),roughness:.78,metalness:.08,alphaTest:data.textures[name].alpha?.025:0,transparent,depthWrite:!transparent,side:transparent?THREE.DoubleSide:THREE.FrontSide});
  if(repeatAxis>=0){m.onBeforeCompile=shader=>{shader.vertexShader='attribute float faceRepeat;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <uv_vertex>','#include <uv_vertex>\n#ifdef USE_MAP\nvMapUv.'+(repeatAxis?'y':'x')+'*=faceRepeat;\n#endif');};m.customProgramCacheKey=()=>key;}
  materialCache.set(key,m);return m;
 }
 function geometry(quads){
  const positions=[],uv=[],indices=[];
  for(const q of quads){const base=positions.length/3;positions.push(...q.p);uv.push(...q.uv);indices.push(base,base+1,base+2,base,base+2,base+3);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();g.computeBoundingBox();return g;
 }
 let initialized=0,totalInstances=0,totalQuads=0;
 for(let state=0;state<data.states.length;state++){
  const s=data.states[state];
  if(s.cube){
   for(let face=0;face<6;face++){
    if(!s.groups[face].length)continue;
    const q=s.quads.find(q=>q.face===face),indices=new Uint32Array(s.groups[face]),runs=new Uint16Array(s.runs[face]),axis=face<2?2:0;
    if(!q)throw Error('完整方块缺少表面：'+s.state);
    const du=[],dv=[];
    for(let i=0;i<4;i++)for(let j=i+1;j<4;j++)if(Math.abs(q.p[i*3+axis]-q.p[j*3+axis])>.9&&[0,1,2].filter(a=>a!==axis).every(a=>Math.abs(q.p[i*3+a]-q.p[j*3+a])<1e-5)){du.push(Math.abs(q.uv[i*2]-q.uv[j*2]));dv.push(Math.abs(q.uv[i*2+1]-q.uv[j*2+1]));}
    const repeatAxis=Math.max(...du)>=Math.max(...dv)?0:1,g=geometry([q]);
    g.setAttribute('faceRepeat',new THREE.InstancedBufferAttribute(new Float32Array(runs),1));
    const mesh=new THREE.InstancedMesh(g,material(q.texture,s.glass,repeatAxis),indices.length);
    mesh.userData={state,indices,runs,axis,quads:1};meshes.push(mesh);totalInstances+=indices.length;totalQuads+=indices.length;
   }
  }else{
   const groups=new Map();for(const q of s.quads){if(!groups.has(q.texture))groups.set(q.texture,[]);groups.get(q.texture).push(q);}
   const indices=new Uint32Array(s.indices);
   for(const [name,quads] of groups){const mesh=new THREE.InstancedMesh(geometry(quads),material(name,s.glass),indices.length);mesh.userData={state,indices,quads:quads.length};meshes.push(mesh);totalInstances+=indices.length;totalQuads+=indices.length*quads.length;}
  }
 }
 for(const mesh of meshes){
  mesh.frustumCulled=false;mesh.count=0;scene.add(mesh);
  const {indices,runs,axis}=mesh.userData;
  for(let start=0;start<indices.length;start+=40000){
   const end=Math.min(indices.length,start+40000);
   for(let i=start;i<end;i++){
    const index=indices[i];position.set(index%W,Math.floor(index/(W*D)),Math.floor(index/W)%D);scale.set(1,1,1);if(runs)scale.setComponent(axis,runs[i]);matrix.makeScale(scale.x,scale.y,scale.z);matrix.setPosition(position);mesh.setMatrixAt(i,matrix);
   }
   initialized+=end-start;loading.textContent='建立完整舰体表面… '+Math.round(initialized/totalInstances*100)+'%';await new Promise(resolve=>setTimeout(resolve,0));
  }
  mesh.count=indices.length;mesh.instanceMatrix.needsUpdate=true;
 }
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 document.getElementById('materials').innerHTML=data.states.map((s,i)=>'<label class="material" data-row="'+i+'"><input type="checkbox" data-material="'+i+'" checked><img class="swatch" alt="" src="'+data.textures[s.quads[0].texture].url+'"><span>'+escape(s.label)+' × '+s.count.toLocaleString()+'</span><small>'+escape(s.state)+'</small></label>').join('');
 document.getElementById('checks').innerHTML=data.audit.model_notes.map(s=>'<p>• '+escape(s)+'</p>').join('');
 function upperBound(a,layer){let l=0,r=a.length;while(l<r){const m=(l+r)>>>1;if(Math.floor(a[m]/(W*D))<=layer)l=m+1;else r=m;}return l;}
 function rebuild(){
  const layer=+document.getElementById('layer').value,glass=document.getElementById('showGlass').checked;let count=0,quads=0;
  for(const mesh of meshes){const {state,indices}=mesh.userData;mesh.count=upperBound(indices,layer);mesh.visible=!hidden.has(state)&&(glass||!data.states[state].glass)&&mesh.count>0;if(mesh.visible)quads+=mesh.count*mesh.userData.quads;}
  for(let i=0;i<data.states.length;i++)if(!hidden.has(i)&&(glass||!data.states[i].glass))count+=stateCounts[i][layer];
  grid.visible=document.getElementById('showGrid').checked;document.getElementById('layerValue').textContent=layer;
  document.getElementById('counts').textContent='筛选包含 '+count.toLocaleString()+' / '+data.blocks.toLocaleString()+' 方块 · 绘制 '+quads.toLocaleString()+' 面片';requestRender();return{blocks:count,quads,layer};
 }
 const directions={front:[-1,.65,-1.1],right:[1,.65,-1.1],back:[1,.65,1.1],top:[0,1,.0001],orthofront:[0,0,-1],orthoside:[-1,0,0],inside:[-1,.75,-1.1],texture:[-1,.35,-1]};
 const viewNames={front:'前左全舰',right:'前右全舰',back:'后侧全舰',top:'俯视全舰',orthofront:'正前投影',orthoside:'正侧投影',inside:'逐层剖切',texture:'舰体上层近景'};
 function fit(){
  camera.zoom=1;camera.updateMatrixWorld();const inverse=camera.matrixWorldInverse,bounds=new THREE.Box3();
  for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])bounds.expandByPoint(new THREE.Vector3(x,y,z).applyMatrix4(inverse));
  const aspect=stage.clientWidth/stage.clientHeight,half=Math.max((bounds.max.y-bounds.min.y)/2,(bounds.max.x-bounds.min.x)/2/aspect)*1.13;
  camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();
 }
 function setView(name='front'){
  if(!directions[name])name='front';camera.up.set(0,1,0);if(name==='top')camera.up.set(0,0,1);
  controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(...directions[name]).multiplyScalar(L*2));controls.update();fit();
  if(name==='texture'){
   const upper=data.states.flatMap(s=>s.cell_bounds[1][1]>H*.85?[s.cell_bounds]:[]),point=new THREE.Vector3(W*.5,H*.75,D*.5);
   if(!upper.length)throw Error('舰体上层取景失败');controls.target.copy(point);camera.position.copy(point).add(new THREE.Vector3(-L*.4,L*.13,-L*.3));camera.zoom=4;camera.updateProjectionMatrix();controls.update();
  }
  document.getElementById('layer').value=name==='inside'?Math.floor(H*.5):H-1;document.getElementById('showGlass').checked=name!=='inside';
  document.getElementById('viewName').textContent=viewNames[name];document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));rebuild();
 }
 for(const el of document.querySelectorAll('[data-material]'))el.onchange=()=>{const i=+el.dataset.material;el.checked?hidden.delete(i):hidden.add(i);rebuild();};
 for(const el of document.querySelectorAll('[data-view]'))el.onclick=()=>setView(el.dataset.view);
 for(const id of ['layer','showGlass','showGrid'])document.getElementById(id).oninput=rebuild;
 document.getElementById('materialSearch').oninput=e=>{const q=e.target.value.toLowerCase();for(const el of document.querySelectorAll('[data-row]'))el.hidden=!el.textContent.toLowerCase().includes(q);};
 document.getElementById('reset').onclick=()=>{hidden.clear();document.querySelectorAll('[data-material]').forEach(e=>e.checked=true);setView('front');};
 document.getElementById('saveImage').onclick=()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download='休伯利安-1145格原稿-三维预览.png';a.href=renderer.domElement.toDataURL('image/png');a.click();};
 document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():stage.requestFullscreen();
 let initializedViewport=false;
 function resize(){const width=stage.clientWidth,height=stage.clientHeight;renderer.setSize(width,height);const zoom=camera.zoom;fit();if(initializedViewport)camera.zoom=zoom;camera.updateProjectionMatrix();initializedViewport=true;requestRender();}
 new ResizeObserver(resize).observe(stage);resize();setView('front');
 await Promise.all(pending);loading.remove();ready=true;requestRender();
 window.REVIEW_READY=true;window.REVIEW=data;window.reviewApi={scene,camera,renderer,controls,setView,rebuild,meshes,
  diagnostics:()=>({ready,blocks:data.blocks,states:data.states.length,blockEntities:data.block_entities,meshCount:meshes.length,totalInstances,totalQuads,visible:rebuild(),hiddenStates:[...hidden]})};
 document.getElementById('status').textContent='完整舰体已就绪 · 原稿逐格核对通过 · 原版形体保留';
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)requestRender();});
}
start().catch(error=>{document.getElementById('loading').textContent='加载失败：'+error.message;console.error(error);});
