from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117'
OUT = ROOT / 'deliveries/0005_W11_支配人偶多角度重塑_P1_20261117'


def main():
    source = (SOURCE / '生成脚本/viewer.mjs').read_text('utf8')
    source = source[:source.index('  const [width,,depth]=data.sizeXYZ')]
    source += r'''
  let activeModel='all',activeView='oblique',axis='y',disposed=false,fitZoom=1,fitBox=new THREE.Box3();
  const basicViews={oblique:{label:'前方斜视',direction:[-.8,.4,1.4]},front:{label:'正面',direction:[0,0,1]},back:{label:'背面',direction:[0,0,-1]},left:{label:'左侧',direction:[-1,0,0]},right:{label:'右侧',direction:[1,0,0]},top:{label:'顶部',direction:[0,1,0]}};
  const layerInput=document.getElementById('layer');
  function bounds(){const box=new THREE.Box3();groups.filter(g=>g.visible).forEach(g=>box.union(g.userData.bounds));return box;}
  function draw(){camera.updateMatrixWorld();renderer.render(scene,camera);frames++;}
  function zoomForBox(box){
    camera.zoom=1;camera.updateProjectionMatrix();camera.updateMatrixWorld();let limit=0;
    for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){
      const p=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
    }
    return .88/limit;
  }
  function setView(name){
    activeView=name;const preset={...basicViews,...data.views}[name],box=bounds();
    const target=preset.center?new THREE.Vector3(...preset.center):box.getCenter(new THREE.Vector3());
    fitBox=preset.half?new THREE.Box3(target.clone().sub(new THREE.Vector3(...preset.half)),target.clone().add(new THREE.Vector3(...preset.half))):box;
    const direction=new THREE.Vector3(...preset.direction).normalize();camera.up.set(0,Math.abs(direction.y)>.999?0:1,Math.abs(direction.y)>.999?-1:0);
    controls.target.copy(target);camera.position.copy(target).add(direction.multiplyScalar(2000));controls.update();
    fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom;camera.updateProjectionMatrix();draw();
    document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));
  }
  function setLayer(value){
    const index='xyz'.indexOf(axis);plane.normal.set(0,0,0).setComponent(index,-1);plane.constant=value+1;
    layerInput.value=value;document.getElementById('layerLabel').textContent=`${axis.toUpperCase()} = ${value}`;draw();
  }
  function setAxis(value){
    axis=value;document.getElementById('axis').value=value;const box=bounds(),index='xyz'.indexOf(value);
    layerInput.min=Math.floor(box.min.getComponent(index));layerInput.max=Math.ceil(box.max.getComponent(index))-1;setLayer(+layerInput.max);
  }
  function setModel(id){
    activeModel=id;groups.forEach(g=>g.visible=id==='all'||g.userData.modelId===id);setAxis(axis);setView('oblique');
    document.querySelectorAll('[data-model]').forEach(b=>b.classList.toggle('active',b.dataset.model===id));
    const size=bounds().getSize(new THREE.Vector3());document.getElementById('actualSize').textContent=`宽 ${size.x} × 深 ${size.z} × 高 ${size.y} 格`;
    document.getElementById('modelName').textContent=id==='all'?data.title:modelById.get(id).title;
  }
  for(const model of [{id:'all',title:'完整人偶'},...data.models]){
    const b=document.createElement('button');b.textContent=model.title;b.dataset.model=model.id;b.onclick=()=>setModel(model.id);document.getElementById('models').append(b);
  }
  for(const [name,view] of Object.entries({...basicViews,...data.views})){
    const b=document.createElement('button');b.textContent=view.label;b.dataset.view=name;b.onclick=()=>setView(name);document.getElementById('views').append(b);
  }
  for(const note of data.design){const p=document.createElement('p');p.textContent=note;document.getElementById('features').append(p);}
  materials.forEach((info,index)=>{
    const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;
    input.onchange=()=>{meshes.filter(m=>m.userData.material===index).forEach(m=>m.visible=input.checked);draw();};
    label.append(input,info.label);document.getElementById('materials').append(label);
  });
  document.getElementById('axis').onchange=e=>setAxis(e.target.value);layerInput.oninput=e=>setLayer(+e.target.value);
  document.getElementById('fullLayer').onclick=()=>setAxis(axis);document.getElementById('reset').onclick=()=>setModel('all');
  document.getElementById('screenshot').onclick=()=>{draw();const a=document.createElement('a');a.download=`乌合之众-P1-${activeView}.png`;a.href=renderer.domElement.toDataURL();a.click();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  controls.addEventListener('change',draw);
  function resize(){
    const relative=camera.zoom/fitZoom,w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);camera.left=-750*w/h;camera.right=750*w/h;camera.top=750;camera.bottom=-750;camera.updateProjectionMatrix();
    if(window.W11_READY){fitZoom=zoomForBox(fitBox);camera.zoom=fitZoom*relative;camera.updateProjectionMatrix();draw();}
  }
  const observer=new ResizeObserver(resize);observer.observe(stage);
  window.W11Viewer={setModel,setView,setAxis,setLayer,snapshot:()=>({activeModel,activeView,axis,frames,renderedQuads,parts:parts.length,blocks:data.total_blocks,camera:{position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom},staticGeometry:true})};
  document.getElementById('stats').textContent=`${data.total_blocks.toLocaleString()} 个方块 · ${parts.length} 个构件`;
  document.getElementById('loading').remove();resize();setModel('all');window.W11_READY=true;
  window.addEventListener('pagehide',()=>{disposed=true;observer.disconnect();controls.dispose();meshes.forEach(m=>m.geometry.dispose());materialCache.forEach(m=>m.dispose());textureCache.forEach(async p=>(await p).dispose());renderer.dispose();},{once:true});
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=`预览载入失败：${error.message}`;});
'''
    (OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
    css = (SOURCE / 'style.css').read_text('utf8')
    css += '\n#features p{font-size:12px;line-height:1.65;color:#c6c0b8}aside .links{line-height:1.8}.referenceLink{display:block;padding:10px;border:1px solid #8d714d;color:#ebd6af;text-decoration:none}#materials label{font-size:12px}\n'
    (OUT / 'style.css').write_text(css, 'utf8')
    html = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W11 乌合之众 · 方块人偶 P1</title></head><body>
<header><div class="eyebrow">0005 / W11 / PUPPET STUDY P1</div><h1>乌合之众 · 方块人偶</h1><p>多角度原作形制 · W11 黑白金红配色 · <span id="actualSize"></span></p></header>
<main><section id="stage"><div id="loading">载入整数格方块模型…</div><div id="legend"><b id="modelName"></b><br>左键旋转 · 右键平移 · 滚轮缩放</div></section><aside>
<section class="controls"><a class="referenceLink" href="参考图册.html" target="_blank">打开多角度参考图册 ↗</a><p>原作形制观察与 W11 配色转译分别记录。</p><div id="models" class="row"></div><p id="stats"></p></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row"><button id="reset">完整复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><button id="fullLayer">显示全部</button></section>
<section class="controls"><h2>形制依据</h2><div id="features"></div></section>
<details><summary>已有方块材质</summary><div id="materials"></div></details>
<p class="links"><a href="W11-乌合之众-方块人偶-P1.nbt">完整人偶 NBT</a> · <a href="manifest.json">模型记录</a> · <a href="参考清单.json">逐图来源</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'''
    (OUT / 'index.html').write_text(html, 'utf8')


if __name__ == '__main__':
    main()
