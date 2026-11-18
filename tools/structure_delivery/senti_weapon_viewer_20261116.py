from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律三兵方块复刻_S1_20261116'

HTML = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>识之律者 · 三兵方块复刻 S1</title></head>
<body><header><div class="eyebrow">0005 / W09 / 武器独立复刻 S1</div><h1>识之律者 · 三兵与武器匣</h1><p>完整整数格实体 · 原生像素材质 · <span id="actualSize">读取方块模型…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块表面…</div><div id="legend"><b id="modelName">识之律者武器</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>静态模型 · 每格为一个实际方块</span></div></section><aside>
<section class="controls"><h2>选择武器</h2><div id="models" class="row"></div><p id="modelStats"></p></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row actions"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>形体细节</h2><ul id="features"></ul></section>
<section class="controls"><h2>同源参考 <a class="tiny" href="../0005_W09_识律武器多角度参考_20261116/index.html" target="_blank">完整图册 ↗</a></h2><div id="references"></div></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 厚度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16 格参考网格</label><label><input id="axes" type="checkbox">XYZ 坐标轴</label></section>
<details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块 ID 或名称"><div id="materials"></div></details><p id="stats"></p><p class="links">下载NBT：<a href="NBT/识律-case-方块模型-S1.nbt">武器匣</a> · <a href="NBT/识律-sword-方块模型-S1.nbt">宝剑</a> · <a href="NBT/识律-spear-方块模型-S1.nbt">长枪</a> · <a href="NBT/识律-chain-方块模型-S1.nbt">链刃</a></p><p class="links"><a href="manifest.json" target="_blank">构件与尺寸</a> · <a href="材料清单.json" target="_blank">材质与数量</a></p>
</aside></main><dialog id="referenceModal"><div class="modalActions"><b id="referenceTitle"></b><a id="referenceSource" target="_blank" rel="noreferrer">查看来源 ↗</a><button id="closeReference">关闭 ×</button></div><img id="referenceImage" alt=""></dialog><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'''

JS = r'''import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
  const bytes=Uint8Array.from(atob(window.SENTI_VOXEL_PAYLOAD),c=>c.charCodeAt(0));
  const {data,materials,parts}=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.SENTI_VOXEL_PAYLOAD=null;
  const stage=document.getElementById('stage'),modelById=new Map(data.models.map(m=>[m.id,m]));
  const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.setClearColor('#17171c');renderer.localClippingEnabled=true;stage.append(renderer.domElement);
  const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xfff8ec,1.25));
  const sun=new THREE.DirectionalLight(0xfff5df,1.2);sun.position.set(-450,650,800);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xdde5ff,.65);fill.position.set(500,150,-650);scene.add(fill);
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
  const groups=[],meshes=[],visibleMaterials=new Set(materials.map((_,i)=>i));
  const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),data.bounds.max[1]+1);
  let renderedQuads=0,frames=0;
  for(const part of parts){
    const group=new THREE.Group();group.name=part.id;group.position.set(...part.origin);scene.add(group);groups.push(group);
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
        materialCache.set(key,new THREE.MeshLambertMaterial({map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.5:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane],emissive:info.emissive?0xffffff:0,emissiveIntensity:info.emissive?.2:0}));
      }
      const mesh=new THREE.Mesh(geometry,materialCache.get(key));mesh.userData.material=material;group.add(mesh);meshes.push(mesh);renderedQuads+=starts.length;
    }
    document.getElementById('loading').textContent=`完整方块表面 ${groups.length}/${parts.length}`;
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const [width,,depth]=data.sizeXYZ,gridSize=Math.ceil(Math.max(width,depth)/16)*16;
  const grid=new THREE.GridHelper(gridSize,gridSize/16,0x95856d,0x37343a);
  grid.position.set((data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]-.5,(data.bounds.min[2]+data.bounds.max[2]+1)/2);grid.visible=false;scene.add(grid);
  const axes=new THREE.AxesHelper(32);axes.visible=false;scene.add(axes);
  let activeModel='case',activeView='oblique',axis='y',layer=0,disposed=false,fitBox=new THREE.Box3(),fitZoom=1;
  const layerInput=document.getElementById('layer'),basicViews={front:{label:'正面',direction:[0,0,1]},back:{label:'背面',direction:[0,0,-1]},left:{label:'左侧厚度',direction:[-1,0,0]},right:{label:'右侧厚度',direction:[1,0,0]},oblique:{label:'斜视',direction:[-.65,.25,1.6]},top:{label:'顶部',direction:[0,1,0]}};
  const modelBounds=()=>{
    const bounds=new THREE.Box3();groups.filter(g=>g.visible).forEach(g=>bounds.union(g.userData.bounds));return bounds;
  };
  function draw(){if(!disposed){camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}}
  function views(){return activeModel==='all'?basicViews:{...basicViews,...modelById.get(activeModel).views};}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
    }
    return .86/limit;
  }
  function setView(name){
    activeView=name;const preset=views()[name],bounds=modelBounds();
    const target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3());
    const direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(2000));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));
  }
  function updateViewButtons(){
    const host=document.getElementById('views');host.replaceChildren();
    for(const [name,preset] of Object.entries(views())){
      const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);
    }
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    const title=all?'三兵与武器匣':model.title,blocks=all?data.models.reduce((sum,m)=>sum+m.blocks,0):model.blocks;
    document.getElementById('modelName').textContent=title;
    document.getElementById('actualSize').textContent=`${title} · 宽 ${size[0]} × 深 ${size[2]} × 高 ${size[1]} 格`;
    document.getElementById('modelStats').textContent=`${blocks.toLocaleString()} 个实体方块`;
    const features=document.getElementById('features');features.replaceChildren();
    for(const text of all?['四件以独立静态姿态排列，可分别观察轮廓、厚度与持握细节。']:model.features){
      const item=document.createElement('li');item.textContent=text;features.append(item);
    }
    const references=document.getElementById('references');references.replaceChildren();
    const refs=all?data.models.flatMap(m=>m.references):model.references;
    for(const ref of refs.filter((ref,i,a)=>a.findIndex(r=>r.id===ref.id)===i)){
      const item=document.createElement('div');item.className='reference';
      const button=document.createElement('button'),image=document.createElement('img'),caption=document.createElement('div'),link=document.createElement('a');
      button.className='referencePicture';image.src=ref.thumbnail;image.alt=ref.id;image.loading='lazy';button.append(image);
      button.onclick=()=>{document.getElementById('referenceImage').src=ref.file||ref.thumbnail;document.getElementById('referenceTitle').textContent=ref.id+' · 形体参考';document.getElementById('referenceSource').href=ref.source_url;document.getElementById('referenceModal').showModal();};
      link.href=ref.source_url;link.target='_blank';link.rel='noreferrer';link.textContent=ref.id+' · 来源 ↗';caption.append(link);item.append(button,caption);references.append(item);
    }
    axes.position.copy(bounds.min);
  }
  function setLayer(value){
    layer=value;layerInput.value=value;const i='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(i,-1);plane.constant=value+1;
    document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const i='xyz'.indexOf(axis),bounds=modelBounds();
    layerInput.min=Math.floor(bounds.min.getComponent(i));layerInput.max=Math.ceil(bounds.max.getComponent(i))-1;
    setLayer(+layerInput.max);
  }
  function setModel(id){
    activeModel=id;groups.forEach(g=>g.visible=id==='all'||g.name===id);
    document.querySelectorAll('[data-model]').forEach(b=>b.classList.toggle('active',b.dataset.model===id));
    updateDetails();updateViewButtons();setAxis(axis);setView('oblique');
  }
  for(const model of [...data.models,{id:'all',title:'全组'}]){
    const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.title;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);
  }
  materials.forEach((info,i)=>{
    const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');
    label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;
    input.type='checkbox';input.checked=true;code.textContent=info.state;
    input.onchange=()=>{input.checked?visibleMaterials.add(i):visibleMaterials.delete(i);meshes.forEach(m=>m.visible=visibleMaterials.has(m.userData.material));draw();};
    label.append(input,code);document.getElementById('materials').append(label);
  });
  document.getElementById('materialSearch').oninput=e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(q));};
  document.getElementById('axis').onchange=e=>setAxis(e.target.value);layerInput.oninput=e=>setLayer(+e.target.value);
  document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=e=>{grid.visible=e.target.checked;draw();};document.getElementById('axes').onchange=e=>{axes.visible=e.target.checked;draw();};
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};
  document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download=`识律-${activeModel}-${activeView}-S1.png`;link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  const modal=document.getElementById('referenceModal');document.getElementById('closeReference').onclick=()=>modal.close();
  modal.onclick=e=>{if(e.target===modal)modal.close();};controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;
    renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();
    if(window.SENTI_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);
  const snapshot=()=>({activeModel,activeView,axis,layer,frames,renderedQuads,models:data.models.map(m=>({id:m.id,size:m.sizeXYZ,blocks:m.blocks})),visibleParts:groups.filter(g=>g.visible).map(g=>g.name),camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom},static:true});
  window.SentiViewer={setModel,setView,setAxis,setLayer,snapshot};
  document.getElementById('stats').textContent=`${parts.length} 件完整模型 · ${renderedQuads.toLocaleString()} 个合并表面 · ${materials.length} 项原生材质`;
  document.getElementById('loading').remove();resize();setModel('case');window.SENTI_READY=true;
  window.addEventListener('pagehide',()=>{
    disposed=true;observer.disconnect();controls.dispose();meshes.forEach(m=>m.geometry.dispose());materialCache.forEach(m=>m.dispose());
    textureCache.forEach(async value=>(await value).dispose());grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();renderer.dispose();
  },{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
'''


def main():
    scripts = OUT / '生成脚本'
    scripts.mkdir(parents=True, exist_ok=True)
    style = (ROOT / 'deliveries/0005_W09_作者蓝图原案_A1_20261116/style.css').read_text('utf-8')
    style += '''
    #stage{background:#17171c}#modelStats{margin:9px 0 0;color:#cfc4ac;font-size:12px}.actions{margin-top:9px}#features{padding-left:18px;margin:0;color:#c7bfb1;font-size:12px}#features li{margin:5px 0}.tiny{font-size:10px;float:right;letter-spacing:0}#references{display:grid;grid-template-columns:1fr 1fr;gap:9px}.reference{min-width:0;font-size:10px}.referencePicture{display:block;width:100%;padding:0;background:#0a0a0d;border:1px solid #514738;cursor:zoom-in}.referencePicture img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}dialog{padding:12px;background:#101116;color:#eee5d8;border:1px solid #8c7551;border-radius:4px;width:min(1500px,96vw);max-height:96vh}dialog::backdrop{background:#000d}.modalActions{display:flex;align-items:center;gap:15px;font-size:13px;margin-bottom:10px}.modalActions button{margin-left:auto}#referenceImage{display:block;width:100%;max-height:82vh;object-fit:contain}.reference a{color:#b9aa8b}#materials label{display:flex;gap:5px;align-items:start}#materials code{word-break:break-all}
    '''
    (OUT / 'index.html').write_text(HTML, 'utf-8')
    (OUT / 'style.css').write_text(style, 'utf-8')
    (scripts / 'viewer.mjs').write_text(JS, 'utf-8')


if __name__ == '__main__':
    main()
