from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117'
OUT = ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117'


def main():
    source = (SOURCE / '生成脚本/viewer.mjs').read_text('utf8')
    source = source[:source.index('  const [width,,depth]=data.sizeXYZ')]
    source = source.replace('TAIXUAN_VOXEL_PAYLOAD', 'W11_VOXEL_PAYLOAD')
    source = source.replace("renderer.setClearColor('#23384a')", "renderer.setClearColor('#202126')")
    source = source.replace('THREE.AmbientLight(0xd2e1ee,1.2)', 'THREE.AmbientLight(0xffffff,1.15)')
    source = source.replace('THREE.DirectionalLight(0xffedcd,1.35)', 'THREE.DirectionalLight(0xfff5e9,1.25)')
    source = source.replace('THREE.DirectionalLight(0xdde5ff,.65)', 'THREE.DirectionalLight(0xffffff,.6)')
    source = source.replace('  let renderedQuads=0,frames=0;', '  const zPlane=new THREE.Plane(new THREE.Vector3(0,0,-1),1000);\n  let renderedQuads=0,frames=0;')
    source = source.replace('const key=`${material}:${face}`;', "const cuttable=part.modelId==='theater'||part.modelId==='canopy',key=`${material}:${face}:${cuttable}`;")
    source = source.replace('clippingPlanes:[plane],emissive:', 'clippingPlanes:cuttable?[plane,zPlane]:[plane],emissive:')
    source += r'''
  const [width,,depth]=data.sizeXYZ,gridSize=Math.ceil(Math.max(width,depth)/16)*16;
  const grid=new THREE.GridHelper(gridSize,gridSize/16,0x9a865c,0x38383d);
  grid.position.set((data.bounds.min[0]+data.bounds.max[0]+1)/2,data.bounds.min[1]-.5,(data.bounds.min[2]+data.bounds.max[2]+1)/2);grid.visible=false;scene.add(grid);
  const axes=new THREE.AxesHelper(32);axes.visible=false;scene.add(axes);
  const modelBlocks=new Map(data.models.map(model=>[model.id,parts.filter(part=>part.modelId===model.id).reduce((sum,part)=>sum+part.blocks,0)]));
  materialCache.forEach((material,key)=>material.userData.emissive=materials[Number(key.split(':')[0])].emissive);
  let activeModel='all',activeView='oblique',axis='y',layer=0,disposed=false,fitBox=new THREE.Box3(),fitZoom=1;
  let mode='idle',paused=false,time=0;
  const layerInput=document.getElementById('layer');
  const basicViews={front:{label:'正面',direction:[0,0,1]},back:{label:'背面',direction:[0,0,-1]},left:{label:'左侧',direction:[-1,0,0]},right:{label:'右侧',direction:[1,0,0]},oblique:{label:'整体斜视',direction:[-.8,.55,1.35]},top:{label:'俯视',direction:[0,1,0]}};
  const routes=data.cabins.map(cabin=>{
    const top=new THREE.Vector3(...cabin.string_top),elbow=new THREE.Vector3(...cabin.string_elbow),roof=new THREE.Vector3(...cabin.roof_anchor);
    const first=top.distanceTo(elbow);return {top,elbow,roof,first,total:first+elbow.distanceTo(roof)};
  });
  const flightGeometry=new THREE.BoxGeometry(1.3,1.3,1.3),flightMaterial=new THREE.MeshBasicMaterial({transparent:true,opacity:.82,clippingPlanes:[plane]});
  const flight=new THREE.InstancedMesh(flightGeometry,flightMaterial,1000);flight.instanceMatrix.setUsage(THREE.DynamicDrawUsage);flight.frustumCulled=false;
  for(let i=0;i<1000;i++)flight.setColorAt(i,new THREE.Color(i%4===0?0xc33b46:0xe8bf66));
  flight.instanceColor.needsUpdate=true;scene.add(flight);
  const canopyBounds=new THREE.Box3();groups.filter(group=>group.userData.modelId==='canopy').forEach(group=>canopyBounds.union(group.userData.bounds));
  const canopyCenter=canopyBounds.getCenter(new THREE.Vector3()),canopySize=canopyBounds.getSize(new THREE.Vector3()),haloRadius=Math.min(canopySize.x,canopySize.z)*.34;
  const haloGeometry=new THREE.BoxGeometry(1.8,.8,1.8),haloMaterial=new THREE.MeshBasicMaterial({color:0xe0ba65,transparent:true,opacity:.6,depthWrite:false,clippingPlanes:[plane]});
  const halo=new THREE.InstancedMesh(haloGeometry,haloMaterial,180);halo.instanceMatrix.setUsage(THREE.DynamicDrawUsage);halo.frustumCulled=false;scene.add(halo);
  const dummy=new THREE.Object3D();
  function updateAnimation(){
    const effects=document.getElementById('effects').checked,canopyShown=activeModel==='canopy'||(activeModel==='all'&&document.getElementById('roof').checked);
    flight.visible=effects&&(activeModel==='all'||activeModel==='strings');halo.visible=effects&&canopyShown;
    for(let i=0;i<1000;i++){
      const route=routes[i%routes.length],distance=((i*.61803398875+time*(mode==='work'?.025:.003))%1)*route.total;
      if(distance<route.first)dummy.position.lerpVectors(route.top,route.elbow,distance/route.first);
      else dummy.position.lerpVectors(route.elbow,route.roof,(distance-route.first)/(route.total-route.first));
      dummy.rotation.set(0,0,0);dummy.scale.setScalar(1);dummy.updateMatrix();flight.setMatrixAt(i,dummy.matrix);
    }
    flight.instanceMatrix.needsUpdate=true;
    for(let i=0;i<180;i++){
      const angle=i*Math.PI*2/180+time*.035;
      dummy.position.set(canopyCenter.x+Math.cos(angle)*haloRadius,canopyBounds.max.y-.6+Math.sin(i*1.7)*.15,canopyCenter.z+Math.sin(angle)*haloRadius);
      dummy.rotation.set(0,-angle,0);dummy.scale.setScalar(1);dummy.updateMatrix();halo.setMatrixAt(i,dummy.matrix);
    }
    halo.instanceMatrix.needsUpdate=true;
    materialCache.forEach(material=>{if(material.userData.emissive)material.emissiveIntensity=mode==='work'?.2+Math.sin(time*1.7)*.035:.2;});
  }
  const modelBounds=()=>{const bounds=new THREE.Box3();groups.filter(group=>group.visible).forEach(group=>bounds.union(group.userData.bounds));return bounds;};
  function draw(){if(disposed)return;updateAnimation();camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function views(){return {...basicViews,...(activeModel==='all'?data.views:modelById.get(activeModel).views)};}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));
    }
    return .86/limit;
  }
  function setView(name){
    activeView=name;const preset=views()[name],bounds=modelBounds(),target=preset.center?new THREE.Vector3(...preset.center):bounds.getCenter(new THREE.Vector3());
    const direction=new THREE.Vector3(...preset.direction).normalize();
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):bounds;
    camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(2000));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(button=>button.classList.toggle('active',button.dataset.view===name));
  }
  function updateViewButtons(){
    const host=document.getElementById('views');host.replaceChildren();
    for(const [name,preset] of Object.entries(views())){const button=document.createElement('button');button.dataset.view=name;button.textContent=preset.label;button.onclick=()=>setView(name);host.append(button);}
  }
  function updateDetails(){
    const all=activeModel==='all',model=modelById.get(activeModel),bounds=modelBounds(),size=bounds.getSize(new THREE.Vector3()).toArray();
    const title=all?data.title:model.title,blocks=all?data.total_blocks:modelBlocks.get(activeModel);
    document.getElementById('modelName').textContent=title;
    document.getElementById('actualSize').textContent=`宽 ${size[0]} × 深 ${size[2]} × 高 ${size[1]} 格`;
    document.getElementById('modelStats').textContent=`${blocks.toLocaleString()} 个实体方块`;
    const features=document.getElementById('features');features.replaceChildren();
    for(const text of all?data.design:model.features){const item=document.createElement('li');item.textContent=text;features.append(item);}
    axes.position.copy(bounds.min);
  }
  function setLayer(value){
    layer=value;layerInput.value=value;const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;
    document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const index='xyz'.indexOf(axis),bounds=modelBounds();
    layerInput.min=Math.floor(bounds.min.getComponent(index));layerInput.max=Math.ceil(bounds.max.getComponent(index))-1;setLayer(+layerInput.max);
  }
  function applyGroups(){groups.forEach(group=>group.visible=(activeModel==='all'||group.userData.modelId===activeModel)&&(activeModel!=='all'||group.userData.modelId!=='canopy'||document.getElementById('roof').checked));}
  function setModel(id){
    activeModel=id;applyGroups();document.querySelectorAll('[data-model]').forEach(button=>button.classList.toggle('active',button.dataset.model===id));
    updateDetails();updateViewButtons();setAxis(axis);setView('oblique');
  }
  function setCanopy(value){document.getElementById('roof').checked=value;applyGroups();updateDetails();setView(activeView);}
  function setCutaway(value){document.getElementById('cutaway').checked=value;zPlane.constant=value?0:1000;draw();}
  function setEffects(value){document.getElementById('effects').checked=value;draw();}
  function setMode(value){mode=value;document.getElementById('mode').value=value;draw();}
  function setPaused(value){paused=value;const button=document.getElementById('pause');button.textContent=paused?'继续':'暂停';button.setAttribute('aria-pressed',String(paused));draw();}
  function setTime(value){time=value;const input=document.getElementById('time');input.max=Math.max(60,Math.ceil(time));input.value=time;document.getElementById('timeValue').textContent=time.toFixed(1)+' s';draw();}
  for(const model of [{id:'all',title:'整体'},...data.models]){const button=document.createElement('button');button.dataset.model=model.id;button.textContent=model.title;button.onclick=()=>setModel(model.id);document.getElementById('models').append(button);}
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input'),code=document.createElement('code');
    label.dataset.materialRow='';label.dataset.search=(info.state+' '+info.label).toLowerCase();label.title=info.label;input.type='checkbox';input.checked=true;code.textContent=info.state;
    input.onchange=()=>{input.checked?visibleMaterials.add(index):visibleMaterials.delete(index);meshes.forEach(mesh=>mesh.visible=visibleMaterials.has(mesh.userData.material));draw();};
    label.append(input,code);document.getElementById('materials').append(label);
  });
  document.getElementById('materialSearch').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.dataset.search.includes(query));};
  document.getElementById('axis').onchange=event=>setAxis(event.target.value);layerInput.oninput=event=>setLayer(+event.target.value);document.getElementById('fullLayer').onclick=()=>setAxis(axis);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};document.getElementById('axes').onchange=event=>{axes.visible=event.target.checked;draw();};
  document.getElementById('roof').onchange=event=>setCanopy(event.target.checked);document.getElementById('effects').onchange=event=>setEffects(event.target.checked);
  document.getElementById('cutaway').onchange=event=>setCutaway(event.target.checked);
  document.getElementById('mode').onchange=event=>setMode(event.target.value);document.getElementById('pause').onclick=()=>setPaused(!paused);document.getElementById('timeZero').onclick=()=>setTime(0);document.getElementById('time').oninput=event=>setTime(+event.target.value);
  document.getElementById('reset').onclick=()=>{setAxis(axis);setView('oblique');};
  document.getElementById('screenshot').onclick=()=>{draw();const link=document.createElement('a');link.download=`W11-${activeModel}-${activeView}-A1.png`;link.href=renderer.domElement.toDataURL('image/png');link.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();
    if(window.W11_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);let last=performance.now();
  function animate(now){if(disposed)return;const elapsed=Math.min((now-last)/1000,.1);last=now;if(!paused)setTime(time+elapsed);requestAnimationFrame(animate);}requestAnimationFrame(animate);
  const snapshot=()=>({activeModel,activeView,axis,layer,frames,renderedQuads,mode,paused,time,showCanopy:document.getElementById('roof').checked,cutaway:document.getElementById('cutaway').checked,effects:document.getElementById('effects').checked,animationWebOnly:true,flightParticles:1000,haloParticles:180,models:data.models.map(model=>({id:model.id,blocks:modelBlocks.get(model.id)})),visibleParts:groups.filter(group=>group.visible).map(group=>group.name),camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom},staticGeometry:true});
  window.W11Viewer={setModel,setView,setAxis,setLayer,setCanopy,setCutaway,setEffects,setMode,setPaused,setTime,snapshot};
  document.getElementById('stats').textContent=`${parts.length} 件完整构件 · ${renderedQuads.toLocaleString()} 个合并表面 · ${materials.length} 项原生材质`;
  document.getElementById('loading').remove();resize();setModel('all');setTime(0);window.W11_READY=true;
  window.addEventListener('pagehide',()=>{
    disposed=true;observer.disconnect();controls.dispose();meshes.forEach(mesh=>mesh.geometry.dispose());materialCache.forEach(material=>material.dispose());textureCache.forEach(async value=>(await value).dispose());
    grid.geometry.dispose();grid.material.dispose();axes.geometry.dispose();axes.material.dispose();flightGeometry.dispose();flightMaterial.dispose();haloGeometry.dispose();haloMaterial.dispose();renderer.dispose();
  },{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
'''
    css = (SOURCE / 'style.css').read_text('utf8')
    css += '''\n:root{--bg:#0e0e11;--panel:#17171c;--line:#54483a;--gold:#dab875;--muted:#aaa6a0;--text:#eeeae3}header{background:#1c171a;border-bottom:2px solid #71363b}h1{font-size:22px;letter-spacing:.07em}#stage{background:#202126}button.active{background:#543439;border-color:#d7ad65}#legend{border-left-color:#b13e48}.controls{border-bottom-color:#393438}#features{color:#ccc6bd}.animationNote{border-left:2px solid #8a4948;padding-left:9px;color:#aaa19a;font-size:11px}#timeValue{float:right;color:var(--gold)}@media(max-width:860px){h1{font-size:18px;letter-spacing:.02em}}\n'''
    html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W11 支配之律者·千律·分布式工业统御阵 A1</title></head>
<body><header><div class="eyebrow">0005 / W11 / AUTHOR BLUEPRINT A1</div><h1>W11 支配之律者·千律·分布式工业统御阵 A1</h1><p>真实整数格方块 · 格雷与本模组原生像素材质 · <span id="actualSize">读取完整模型…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块表面…</div><div id="legend"><b id="modelName">千律机械剧场</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>实体保持原位，运动粒子仅为网页演示</span></div></section><aside>
<section class="controls"><h2>观察构件</h2><p>仅主控位置固定，其余实体方块均可换成合法通用接口。</p><div id="models" class="row"></div><p id="modelStats"></p><label><input id="roof" type="checkbox" checked>显示天幕</label><label><input id="cutaway" type="checkbox">剖开前半回廊</label></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row actions"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>运行演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 低速统御信号</option><option value="work">运行 · 千舱同步</option></select><div class="row"><button id="pause" aria-pressed="false">暂停</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>红金舱丝粒子与金色天幕全息环</label><p class="animationNote">1000个信号粒子沿真实舱丝折线路径，由天幕端流向舱顶。仅发光方块轻微呼吸，所有实体方块保持原位；动画不写入NBT。</p></section>
<section class="controls"><h2>形体细节</h2><ul id="features"></ul></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16格参考网格</label><label><input id="axes" type="checkbox">XYZ坐标轴</label></section>
<details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块ID或名称"><div id="materials"></div></details><p id="stats"></p><p class="links">黑白主甲，金红提线。</p><p class="links"><a href="W11-千律机械剧场-A1.nbt">完整方块NBT</a> · <a href="sources.json" target="_blank">来源依据</a> · <a href="conflicts.json" target="_blank">尺寸说明</a></p><p class="links"><a href="manifest.json" target="_blank">生成记录</a> · <a href="materials.json" target="_blank">原生材质</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>
'''
    (OUT / '生成脚本').mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
    (OUT / 'style.css').write_text(css, 'utf8')
    (OUT / 'index.html').write_text(html, 'utf8')
    print(OUT)


if __name__ == '__main__':
    main()
