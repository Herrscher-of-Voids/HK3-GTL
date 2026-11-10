/** I26独立样件：外露面实例绘制、按需渲染和单件聚焦。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const out=path.resolve(process.argv[2]);
const skill=path.join(process.env.USERPROFILE||process.env.HOME,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const source=`import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';
async function start(){
const bytes=Uint8Array.from(atob(window.HK3_PAYLOAD),c=>c.charCodeAt(0));
const raw=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
const {data,materials,palette,surfaceGroups,blockCount}=JSON.parse(raw);window.HK3_PAYLOAD=null;
const [W,H,D]=data.size,stage=document.getElementById('stage');
const scene=new THREE.Scene();scene.background=new THREE.Color('#121b2b');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;stage.prepend(renderer.domElement);
const camera=new THREE.OrthographicCamera(-40,40,40,-40,.1,2000);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minZoom=.4;controls.maxZoom=8;
scene.add(new THREE.HemisphereLight(0xc8e5ff,0x384458,2.3));
const sun=new THREE.DirectionalLight(0xfff4e7,3);sun.position.set(-50,100,-60);scene.add(sun);
const fill=new THREE.DirectionalLight(0x81c7ed,1.3);fill.position.set(60,25,40);scene.add(fill);
const faceNames=['east','west','south','north','down','up'];
const rotations=[[0,Math.PI/2,0],[0,-Math.PI/2,0],[0,0,0],[0,Math.PI,0],[Math.PI/2,0,0],[-Math.PI/2,0,0]];
const matrix=new THREE.Matrix4(),geometry=new THREE.PlaneGeometry(1,1),pending=[],cache=new Map(),meshes=[];
const quats=rotations.map(r=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...r)));
function texture(url){if(cache.has(url))return cache.get(url);let ok,fail;pending.push(new Promise((a,b)=>{ok=a;fail=b}));const t=new THREE.TextureLoader().load(url,ok,undefined,fail);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;t.colorSpace=THREE.SRGBColorSpace;cache.set(url,t);return t;}
for(let i=0;i<materials.length;i++)for(let face=0;face<6;face++){
 const indices=surfaceGroups[i][face];if(!indices.length)continue;const material=materials[i];
 const m=new THREE.MeshStandardMaterial({map:texture(material.faces[faceNames[face]]),roughness:.78,metalness:.08,alphaTest:material.transparent?.12:0,side:material.transparent?THREE.DoubleSide:THREE.FrontSide});
 const mesh=new THREE.InstancedMesh(geometry,m,indices.length);
 for(let n=0;n<indices.length;n++){const index=indices[n],y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;let px=x+.5,py=y+.5,pz=z+.5;if(face===0)px=x+1;else if(face===1)px=x;else if(face===2)pz=z+1;else if(face===3)pz=z;else if(face===4)py=y;else py=y+1;matrix.compose(new THREE.Vector3(px,py,pz),quats[face],new THREE.Vector3(1,1,1));mesh.setMatrixAt(n,matrix);}
 mesh.instanceMatrix.needsUpdate=true;mesh.userData={indices,face};mesh.computeBoundingSphere();scene.add(mesh);meshes.push(mesh);
}
const grid=new THREE.GridHelper(Math.max(W,D)+12,Math.max(W,D)+12,0x52677e,0x23334a);grid.position.set(W/2,-.07,D/2);scene.add(grid);
let selected='all',view='iso',queued=false;
function isolate(){
const sample=data.samples.find(x=>x.id===selected);
for(const mesh of meshes){const {indices,face}=mesh.userData;let count=0;
for(const index of indices){const y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;
if(sample&&(x<sample.offset[0]||x>=sample.offset[0]+sample.size[0]||y<sample.offset[1]||y>=sample.offset[1]+sample.size[1]||z<sample.offset[2]||z>=sample.offset[2]+sample.size[2]))continue;
let px=x+.5,py=y+.5,pz=z+.5;if(face===0)px=x+1;else if(face===1)px=x;else if(face===2)pz=z+1;else if(face===3)pz=z;else if(face===4)py=y;else py=y+1;
matrix.compose(new THREE.Vector3(px,py,pz),quats[face],new THREE.Vector3(1,1,1));mesh.setMatrixAt(count++,matrix);}
mesh.count=count;mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();mesh.visible=count>0;}
grid.visible=!sample;
}
function render(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;renderer.render(scene,camera);});}
function fit(){
isolate();
const s=data.samples.find(x=>x.id===selected),size=s?s.size:data.size,origin=s?s.offset:[0,0,0];const center=new THREE.Vector3(origin[0]+size[0]/2,origin[1]+size[1]*.45,origin[2]+size[2]/2),length=Math.max(...size);
controls.target.copy(center);camera.zoom=1;
const v=view==='front'?[0,.12,-2]:view==='side'?[-2,.1,0]:view==='top'?[0,2,.001]:[-1.6,1.25,-1.6];camera.position.copy(center).add(new THREE.Vector3(...v).multiplyScalar(length));camera.lookAt(center);
const width=stage.clientWidth,height=stage.clientHeight,aspect=width/height,half=length*.7*Math.max(1,1/aspect);renderer.setSize(width,height);camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();controls.update();render();
}
controls.addEventListener('change',render);
document.getElementById('sample').onchange=e=>{selected=e.target.value;fit();};
for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>{view=button.dataset.view;fit();};
document.getElementById('reset').onclick=()=>{selected='all';view='iso';document.getElementById('sample').value='all';fit();};
new ResizeObserver(fit).observe(stage);
document.getElementById('counts').textContent=blockCount.toLocaleString()+' 个方块 · '+data.samples.length+' 件独立样件';
document.getElementById('legend').innerHTML=data.samples.map(x=>{const m=materials.find(v=>v.state===x.state);return '<p><img src="'+m.faces.north+'"><b>'+x.label+'</b><small>'+x.state+'</small></p>';}).join('');
await Promise.all(pending);document.getElementById('loading').remove();document.getElementById('status').textContent='实际材质载入完成 · 同形换色 · 未放入码头';fit();
}
start().catch(e=>{document.getElementById('loading').textContent='加载失败：'+e.message;console.error(e);});`;
const compiled=await rolldown({input:'virtual:samples',plugins:[{name:'I26样件',resolveId(id){if(id==='virtual:samples')return id;},load(id){if(id==='virtual:samples')return source;}}],resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
const result=await compiled.generate({format:'iife',minify:true});await compiled.close();
await fs.writeFile(path.join(out,'viewer.bundle.js'),result.output.find(x=>x.type==='chunk').code,'utf8');
await fs.copyFile(path.join(skill,'node_modules/three/LICENSE'),path.join(out,'Three许可.txt'));
console.log(JSON.stringify({output:out,standalone:true}));
