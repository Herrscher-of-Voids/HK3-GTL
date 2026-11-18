/** I26车辆组合：单辆外露面实例绘制，切换时释放旧实例缓冲。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const out=path.resolve(process.argv[2]);
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const source=`import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';
async function start(){
const bytes=Uint8Array.from(atob(window.HK3_COMBINATIONS),c=>c.charCodeAt(0));
const raw=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
const {materials,palette,variants}=JSON.parse(raw);window.HK3_COMBINATIONS=null;
const stage=document.getElementById('stage'),scene=new THREE.Scene();scene.background=new THREE.Color('#121b2b');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;stage.prepend(renderer.domElement);
const camera=new THREE.OrthographicCamera(-30,30,30,-30,.1,1500),controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minZoom=.4;controls.maxZoom=7;
scene.add(new THREE.HemisphereLight(0xc8e5ff,0x384458,2.3));
const sun=new THREE.DirectionalLight(0xfff4e7,3);sun.position.set(-50,100,-60);scene.add(sun);
const fill=new THREE.DirectionalLight(0x81c7ed,1.3);fill.position.set(60,25,40);scene.add(fill);
const faceNames=['east','west','south','north','down','up'],rotations=[[0,Math.PI/2,0],[0,-Math.PI/2,0],[0,0,0],[0,Math.PI,0],[Math.PI/2,0,0],[-Math.PI/2,0,0]];
const quats=rotations.map(r=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...r))),matrix=new THREE.Matrix4(),plane=new THREE.PlaneGeometry(1,1),pending=[],textures=new Map();
function texture(url){if(textures.has(url))return textures.get(url);let ok,fail;pending.push(new Promise((a,b)=>{ok=a;fail=b}));const t=new THREE.TextureLoader().load(url,ok,undefined,fail);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;t.colorSpace=THREE.SRGBColorSpace;textures.set(url,t);return t;}
const faceMaterials=materials.map(material=>faceNames.map(face=>new THREE.MeshStandardMaterial({map:texture(material.faces[face]),roughness:.78,metalness:.08,alphaTest:material.transparent?.12:0,side:material.transparent?THREE.DoubleSide:THREE.FrontSide})));
let selected=variants.findIndex(v=>v.id===new URLSearchParams(location.search).get('variant'));if(selected<0)selected=1;
let meshes=[],view='iso',queued=false;const grid=new THREE.GridHelper(45,45,0x52677e,0x23334a);grid.position.set(4.5,-.07,15.5);scene.add(grid);
function render(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;renderer.render(scene,camera);});}
function fit(){const v=variants[selected],size=v.size,center=new THREE.Vector3(size[0]/2,size[1]*.45,size[2]/2),length=Math.max(...size);controls.target.copy(center);camera.zoom=1;const dir=view==='front'?[0,.12,-2]:view==='side'?[-2,.1,0]:view==='top'?[0,2,.001]:[-1.6,1.25,-1.6];camera.position.copy(center).add(new THREE.Vector3(...dir).multiplyScalar(length));camera.lookAt(center);const w=stage.clientWidth,h=stage.clientHeight,aspect=w/h,half=length*.6*Math.max(1,1/aspect);renderer.setSize(w,h);camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();controls.update();render();}
function choose(index){selected=(index+variants.length)%variants.length;const v=variants[selected],[W,H,D]=v.size;for(const mesh of meshes){scene.remove(mesh);mesh.dispose();}meshes=[];
for(let i=0;i<materials.length;i++)for(let face=0;face<6;face++){const indices=v.surfaceGroups[i][face];if(!indices.length)continue;const mesh=new THREE.InstancedMesh(plane,faceMaterials[i][face],indices.length);for(let n=0;n<indices.length;n++){const index=indices[n],y=Math.floor(index/(W*D)),z=Math.floor(index/W)%D,x=index%W;let px=x+.5,py=y+.5,pz=z+.5;if(face===0)px=x+1;else if(face===1)px=x;else if(face===2)pz=z+1;else if(face===3)pz=z;else if(face===4)py=y;else py=y+1;matrix.compose(new THREE.Vector3(px,py,pz),quats[face],new THREE.Vector3(1,1,1));mesh.setMatrixAt(n,matrix);}mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();scene.add(mesh);meshes.push(mesh);}
document.getElementById('tractor').value=v.tractor;document.getElementById('cargo').value=v.cargo||'EMPTY';document.getElementById('title').textContent=v.id+' · '+v.label;document.getElementById('counts').textContent=v.blockCount.toLocaleString()+' 方块 · '+v.size[0]+'宽×'+v.size[2]+'长×'+v.size[1]+'高';document.getElementById('status').textContent=v.cargo?'挂箱组合 · 共用半挂底盘与后轮连接':'空载拖头 · 不计入32种挂箱组合';document.getElementById('image').href=v.image;
document.getElementById('legend').innerHTML=[v.tractor,v.cargo].filter(Boolean).map(tier=>{const m=materials.find(m=>m.state==='hk3gtl:voltage_machine_casing_'+tier.toLowerCase());return '<p><img src="'+m.faces.north+'">'+tier+'实际机壳纹理</p>';}).join('');fit();}
for(const id of ['tractor','cargo'])document.getElementById(id).onchange=()=>choose(variants.findIndex(v=>v.id===document.getElementById('tractor').value+'-'+document.getElementById('cargo').value));
document.getElementById('random').onclick=()=>{const loaded=variants.map((v,i)=>v.cargo?i:-1).filter(i=>i>=0);choose(loaded[Math.floor(Math.random()*loaded.length)]);};document.getElementById('prev').onclick=()=>choose(selected-1);document.getElementById('next').onclick=()=>choose(selected+1);
for(const b of document.querySelectorAll('[data-view]'))b.onclick=()=>{view=b.dataset.view;fit();};document.getElementById('reset').onclick=()=>{view='iso';fit();};controls.addEventListener('change',render);new ResizeObserver(fit).observe(stage);
await Promise.all(pending);document.getElementById('loading').remove();choose(selected);
}
start().catch(e=>{document.getElementById('loading').textContent='加载失败：'+e.message;console.error(e);});`;
const compiled=await rolldown({input:'virtual:vehicles',plugins:[{name:'I26车辆组合',resolveId(id){if(id==='virtual:vehicles')return id;},load(id){if(id==='virtual:vehicles')return source;}}],resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
const result=await compiled.generate({format:'iife',minify:true});await compiled.close();
await fs.writeFile(path.join(out,'viewer.bundle.js'),result.output.find(x=>x.type==='chunk').code,'utf8');
await fs.copyFile(path.join(skill,'node_modules/three/LICENSE'),path.join(out,'Three许可.txt'));
console.log(JSON.stringify({output:out,standalone:true}));
