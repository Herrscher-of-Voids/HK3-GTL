/** I26 码头预览构建：紧凑边界实例、控件分流与按需绘制。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.resolve(process.argv[2]);
const home = process.env.USERPROFILE || process.env.HOME;
const skill = path.join(home, '.codex/skills/minecraft-builder-skill');
const { rolldown } = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));
let source = await fs.readFile(path.join(root, 'logs/research-labs-preview-20260928/candidate02/viewer-source.mjs'), 'utf8');
source = source.replace(/\r\n/g, '\n');
const imports = source.match(/^import .*;$/gm).join('\n');
source = source.replace(/^import .*;$/gm, '');

source = source.replace('const {data,materials,audit,names}=window.REVIEW;', `
const bytes=Uint8Array.from(atob(window.HK3_PAYLOAD),c=>c.charCodeAt(0));
const raw=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
const payload=JSON.parse(raw);window.HK3_PAYLOAD=null;
const {data,materials,audit,names}=payload;
const surfaceGroups=payload.surfaceGroups.map(group=>group.map(face=>new Uint32Array(face)));
const blockCount=payload.blockCount;payload.surfaceGroups=null;
window.REVIEW={data,materials,audit,names};`);
source = source.replace('const [W,H,D]=data.size,cx=W/2,cz=D/2,hiddenMaterials=new Set();',
  'const [W,H,D]=data.size,cx=W/2,cz=D/2,L=Math.max(W,H,D),hiddenMaterials=new Set();');
source = source.replace('32,-32,.1,350', '32,-32,.1,L*12');
source = source.replace('renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));', 'renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));');

const meshCode = `const faceNames=['east','west','south','north','down','up'];
const faceRotations=[[0,Math.PI/2,0],[0,-Math.PI/2,0],[0,0,0],[0,Math.PI,0],[Math.PI/2,0,0],[-Math.PI/2,0,0]];
const planeGeometry=new THREE.PlaneGeometry(1,1),faceGeometries=faceRotations.map(()=>planeGeometry);
const matrix=new THREE.Matrix4(),quaternions=faceRotations.map(rotation=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...rotation)));
const stateMeshes=[];
for(let i=0;i<materials.length;i++){
  const material=materials[i];
  for(let face=0;face<faceNames.length;face++){
    const indices=surfaceGroups[i][face];if(!indices.length)continue;
    const side=new THREE.MeshStandardMaterial({map:texture(material.faces[faceNames[face]]),roughness:.78,metalness:.08,
      alphaTest:material.transparent?.12:0,side:material.transparent?THREE.DoubleSide:THREE.FrontSide});
    const mesh=new THREE.InstancedMesh(faceGeometries[face],side,indices.length);
    mesh.castShadow=false;mesh.receiveShadow=false;mesh.userData={indices,material,face,initialized:0,boundsReady:false};
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);group.add(mesh);stateMeshes.push(mesh);
  }
}`;
source = source.replace('const cube=new THREE.BoxGeometry(1,1,1);const matrix=new THREE.Matrix4();', '');
source = source.replace(/const stateMeshes=\[\];\nfor\(const material of materials\)\{[\s\S]*?\n\}\nconst paths=/, `${meshCode}\nconst paths=`);

const rebuildCode = `let requestRender=()=>{};
let rebuildQueued=false;
function scheduleRebuild(){if(rebuildQueued)return;rebuildQueued=true;requestAnimationFrame(()=>{rebuildQueued=false;rebuild();});}
function rebuild(){
  const layer=+document.getElementById('layer').value,glass=document.getElementById('showGlass').checked;
  let count=0;
  for(const mesh of stateMeshes){
    const {indices,material,face}=mesh.userData;
    let low=0,high=indices.length;
    while(low<high){const mid=(low+high)>>>1;if(Math.floor(indices[mid]/(W*D))<=layer)low=mid+1;else high=mid;}
    const n=low;
    if(n>mesh.userData.initialized){
      for(let i=mesh.userData.initialized;i<n;i++){
        const index=indices[i],y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;
        let px=x+.5,py=y+.5,pz=z+.5;
        if(face===0)px=x+1;else if(face===1)px=x;
        else if(face===2)pz=z+1;else if(face===3)pz=z;
        else if(face===4)py=y;else py=y+1;
        matrix.compose(new THREE.Vector3(px,py,pz),quaternions[face],new THREE.Vector3(1,1,1));
        mesh.setMatrixAt(i,matrix);
      }
      mesh.userData.initialized=n;mesh.instanceMatrix.needsUpdate=true;
    }
    mesh.count=n;
    if(n&&!mesh.userData.boundsReady){mesh.computeBoundingSphere();mesh.userData.boundsReady=true;}
    if(!hiddenMaterials.has(material.state)&&(glass||!material.transparent))count+=n;
  }
  document.getElementById('layerValue').textContent=layer;
  document.getElementById('counts').textContent='绘制外露面 '+count.toLocaleString()+' 片 / '+blockCount.toLocaleString()+' 个实体方块';
  updateVisibility();
  requestRender();
}
function updateVisibility(){
  const glass=document.getElementById('showGlass').checked;
  for(const mesh of stateMeshes){const {material}=mesh.userData;mesh.visible=mesh.count>0&&!hiddenMaterials.has(material.state)&&(glass||!material.transparent);}
  paths.visible=document.getElementById('showPaths').checked;
  markerGroup.visible=document.getElementById('showPorts').checked;
  requestRender();
}
const views=`;
source = source.replace(/function rebuild\(\)\{[\s\S]*?\n\}\nconst views=/, rebuildCode);
source = source.replace("for(const id of ['layer','showGlass','showZones','showPorts','showPaths'])document.getElementById(id).oninput=rebuild;", `
document.getElementById('layer').oninput=scheduleRebuild;
document.getElementById('showGlass').onchange=updateVisibility;
document.getElementById('showZones').onchange=()=>requestRender();
document.getElementById('showPorts').onchange=updateVisibility;
document.getElementById('showPaths').onchange=updateVisibility;`);
source = source.replace("el.checked?hiddenMaterials.delete(state):hiddenMaterials.add(state);rebuild();", "el.checked?hiddenMaterials.delete(state):hiddenMaterials.add(state);updateVisibility();");

const renderCode = `const projected=new THREE.Vector3();
let renderQueued=false;
requestRender=()=>{if(renderQueued)return;renderQueued=true;requestAnimationFrame(renderFrame);};
function renderFrame(){
  renderQueued=false;controls.update();renderer.render(scene,camera);
  for(const label of labels){
    const show=label.kind==='dimension'||(label.kind==='zone'?document.getElementById('showZones').checked&&label.pos.y<=+document.getElementById('layer').value+2:document.getElementById('showPorts').checked);
    projected.copy(label.pos).project(camera);label.el.style.display=show&&projected.z<1&&projected.z>-1?'block':'none';
    label.el.style.left=(projected.x*.5+.5)*stage.clientWidth+'px';label.el.style.top=(-projected.y*.5+.5)*stage.clientHeight+'px';
  }
}
controls.addEventListener('change',requestRender);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)requestRender();});
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);const half=L*.72*Math.max(1,1/(w/h));camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();requestRender();}
new ResizeObserver(resize).observe(stage);resize();
setView(new URLSearchParams(location.search).get('view')??'front');
`;
source = source.replace(/function resize\(\)\{[\s\S]*?setView\(new URLSearchParams\(location\.search\)\.get\('view'\)\?\?'front'\);\n/, '');
source = source.replace(/const projected=new THREE\.Vector3\(\);\nfunction frame\(\)\{[\s\S]*?\n\}\nframe\(\);\n/, renderCode);
source = source.replace('function setView(name){', 'function setView(name){');
source = source.replace("camera.zoom=name==='panel'?Math.max(W,D,H)/12:1;", "camera.zoom=name==='panel'?L/12:1;");
source = source.replace("renderer.render(scene,camera);const a=document.createElement('a');", "renderer.render(scene,camera);const a=document.createElement('a');");

const oldHotPaths = ['data.blocks.filter', 'data.blocks.length', 'function frame(){', 'boundaryGroups'].filter(token => source.includes(token));
if (oldHotPaths.length) throw new Error('预览优化替换不完整，残留：' + oldHotPaths.join('、'));
source = imports + '\nasync function start(){\n' + source + '\n}\nstart().catch(error=>{document.getElementById("loading").textContent="加载失败："+error.message;console.error(error);});';
const compiled = await rolldown({
  input: 'virtual:i26-terminal',
  plugins: [{ name: 'I26码头预览', resolveId(id) { if (id === 'virtual:i26-terminal') return id; }, load(id) { if (id === 'virtual:i26-terminal') return source; } }],
  resolve: { alias: {
    three: path.join(skill, 'node_modules/three/build/three.module.js'),
    'orbit-controls': path.join(skill, 'node_modules/three/examples/jsm/controls/OrbitControls.js'),
  } },
});
const bundle = await compiled.generate({ format: 'iife', minify: true });
await compiled.close();
await fs.writeFile(path.join(output, 'viewer.bundle.js'), bundle.output.find(item => item.type === 'chunk').code, 'utf8');
await fs.copyFile(path.join(skill, 'node_modules/three/LICENSE'), path.join(output, 'Three许可.txt'));
console.log(JSON.stringify({ output, optimized: true }));
