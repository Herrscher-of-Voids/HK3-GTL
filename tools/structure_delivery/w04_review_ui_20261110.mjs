/* W04统一评审界面适配开始 */
// 沿用W03／休伯利安评审布局，只适配既有静态构件，不改几何数据。
async function installW04ReviewUI(){
  while(!window.W04_STATIC_READY)await new Promise(resolve=>setTimeout(resolve,40));
  const a=window.W04Static,{data,materials}=a.config;
  const meta=JSON.parse(document.getElementById('reviewMetadata').textContent);
  const hidden=new Set(),stage=document.getElementById('stage');
  const byState=new Map();materials.forEach((m,i)=>{if(!byState.has(m.state))byState.set(m.state,[]);byState.get(m.state).push(i);});
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const countFormat=n=>n.toLocaleString('zh-CN');
  const stateCount=new Map(meta.materials.map(m=>[m.state,m.count]));
  document.getElementById('materials').innerHTML=meta.materials.map((m,i)=>{
    const material=materials[byState.get(m.state)[0]],texture=material.faces.south||Object.values(material.faces)[0];
    return `<label class="material" data-row="${i}"><input type="checkbox" data-material="${escape(m.state)}" checked><img class="swatch" src="${texture}" alt=""><span>${escape(m.label)} × ${countFormat(m.count)}</span><small>${escape(m.state)}</small></label>`;
  }).join('');
  const plane=a.groups.flatMap(g=>g.children).find(m=>m.isMesh)?.material.clippingPlanes?.[0];
  for(const group of Object.values(a.sceneryGroups))group.traverse(item=>{
    if(item.isMesh&&plane){item.material.clippingPlanes=[plane];item.material.needsUpdate=true;}
  });
  const grid=new THREE.GridHelper(Math.max(...data.size)*1.1,24,0x496078,0x25354b);
  grid.position.set(data.size[0]/2,-.2,data.size[2]/2);grid.visible=false;a.scene.add(grid);
  function draw(){a.renderer.render(a.scene,a.camera);}
  function apply(){
    const glass=document.getElementById('glass').checked;
    let quads=0,visibleGroups=0;
    for(const group of a.groups){
      const part=document.querySelector(`[data-part="${CSS.escape(group.name)}"]`);
      const asset=document.querySelector(`[data-asset="${group.name.split('_')[0]}"]`);
      group.visible=(part?.checked??true)&&(asset?.checked??true);
      if(group.visible)visibleGroups++;
      for(const mesh of group.children){
        const m=materials[mesh.userData.material];
        mesh.visible=!hidden.has(m.state)&&(glass||!mesh.userData.glass);
        if(group.visible&&mesh.visible)quads+=mesh.geometry.getAttribute('position').count/6;
      }
    }
    for(const [name,group] of Object.entries(a.sceneryGroups))group.visible=document.querySelector(`[data-scenery="${name}"]`)?.checked??true;
    grid.visible=document.getElementById('showGrid').checked;
    document.getElementById('counts').textContent=`显示 ${visibleGroups}/${a.groups.length} 个构件 · ${countFormat(quads)} 个表面（剖切前）`;
    const selected=meta.materials.filter(m=>!hidden.has(m.state)).reduce((n,m)=>n+m.count,0);
    document.getElementById('materialCounts').textContent=`材料筛选对应${meta.whole_integer_voxel?'整机方块':'源体素'} ${countFormat(selected)}/${countFormat(meta.source_voxels)}；${meta.whole_integer_voxel?'与完整导出材料表一致。':'不含草模，非缩放后整机材料表。'}`;
    draw();
  }
  document.querySelectorAll('[data-part],[data-asset],[data-scenery],[data-material]').forEach(e=>e.onchange=()=>{
    if(e.dataset.material)e.checked?hidden.delete(e.dataset.material):hidden.add(e.dataset.material);
    apply();
  });
  document.getElementById('glass').onchange=apply;document.getElementById('showGrid').onchange=apply;
  document.getElementById('layer').oninput=e=>{
    if(plane)plane.constant=+e.target.value+1.01;
    document.getElementById('layerLabel').textContent=e.target.value;
    document.getElementById('layerValue').textContent=e.target.value;apply();
  };
  document.getElementById('materialSearch').oninput=e=>{
    const query=e.target.value.toLowerCase();document.querySelectorAll('[data-row]').forEach(row=>row.hidden=!row.textContent.toLowerCase().includes(query));
  };
  const names={front:'前左全景',right:'前右全景',orthofront:'正面投影',side:'侧面投影',back:'后侧全景',top:'俯视全景',
    reactor:'雷池近景',dragon:'龙体近景',sword:'七雷近景',field:'环塔近景',controller:'主控与接口位置',inside:'逐层剖切',head:'龙首近景',casing:'单格机壳材质',torii:'三进鸟居',magnet:'托卡马克磁轭'};
  function setView(name){
    if(name==='inside'){
      a.setView('front');document.getElementById('layer').value=Math.floor(data.size[1]/2);
      document.getElementById('layer').dispatchEvent(new Event('input'));
    }else if(name==='right'){
      a.setView('front');a.camera.position.x=2*a.controls.target.x-a.camera.position.x;
      a.controls.update();a.camera.updateMatrixWorld();
    }else a.setView(name);
    document.getElementById('viewName').textContent=names[name]||name;
    document.querySelectorAll('[data-view]').forEach(e=>e.classList.toggle('active',e.dataset.view===name));apply();
  }
  document.querySelectorAll('[data-view]').forEach(e=>e.onclick=()=>setView(e.dataset.view));
  document.getElementById('reset').onclick=()=>{
    hidden.clear();document.querySelectorAll('[data-material],[data-part],[data-asset]').forEach(e=>e.checked=true);
    document.getElementById('glass').checked=true;document.getElementById('layer').value=data.size[1];
    document.getElementById('layer').dispatchEvent(new Event('input'));setView('front');
  };
  document.getElementById('saveImage').onclick=()=>{
    draw();const link=document.createElement('a');link.download=meta.candidate+'-三维评审.png';
    link.href=a.renderer.domElement.toDataURL('image/png');link.click();
  };
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():stage.requestFullscreen();
  document.getElementById('status').textContent=meta.whole_integer_voxel?'原评审界面 · 整机真实方块 · 全静态':'统一评审界面已恢复 · 建筑数据与摆位未变 · 全静态';
  document.getElementById('stats').textContent=`${a.groups.length}个完整构件；${meta.whole_integer_voxel?'整机整数格与真实方块贴图。':'体素纹理保持，草模边界单独标注。'}`;
  window.W04Review={apply,setView,grid,hidden,metadata:meta,stateCount};window.W04_REVIEW_READY=true;
  setView('front');
}
installW04ReviewUI().catch(error=>{console.error(error);document.getElementById('status').textContent='评审控件加载失败：'+error.message;});
/* W04统一评审界面适配结束 */
