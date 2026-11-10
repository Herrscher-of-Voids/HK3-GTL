  let disposed=false,frames=0;
  const fullBounds=new THREE.Box3(new THREE.Vector3(0,0,0),new THREE.Vector3(...data.size));
  function draw(){if(!disposed){renderer.render(scene,camera);frames++;}}
  function setView(name) {
    const target=fullBounds.getCenter(new THREE.Vector3());let direction=new THREE.Vector3(-1,.7,1.25);
    if(name==='orthofront')direction.set(0,0,1);
    if(name==='side')direction.set(1,0,0);
    if(name==='top')direction.set(0,1,.001);
    if(name==='core')target.copy(offset).add(new THREE.Vector3(0,148,0));
    if(name==='controller')target.set(...data.controller);
    controls.target.copy(target);camera.up.set(0,1,0);camera.position.copy(target).add(direction.normalize().multiplyScalar(1800));
    controls.update();camera.zoom=1;camera.updateMatrixWorld();camera.updateProjectionMatrix();
    const bounds=name==='core'?new THREE.Box3(target.clone().addScalar(-74),target.clone().addScalar(74)):
      name==='controller'?new THREE.Box3(target.clone().add(new THREE.Vector3(-52,-20,-35)),target.clone().add(new THREE.Vector3(52,32,8))):fullBounds;
    let limit=0;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]) {
      const point=new THREE.Vector3(x,y,z).project(camera);limit=Math.max(limit,Math.abs(point.x),Math.abs(point.y));
    }
    camera.zoom=.88/Math.max(limit,.01);camera.updateProjectionMatrix();draw();
  }
  function resize(){const {width,height}=stage.getBoundingClientRect();renderer.setSize(width,height);const aspect=width/height;camera.left=-500*aspect;camera.right=500*aspect;camera.top=500;camera.bottom=-500;camera.updateProjectionMatrix();draw();}
  controls.addEventListener('change',draw);
  document.querySelectorAll('[data-view]').forEach(e=>e.onclick=()=>setView(e.dataset.view));
  document.querySelectorAll('[data-part]').forEach(e=>e.onchange=()=>{groups.find(g=>g.name===e.dataset.part).visible=e.checked;draw();});
  document.getElementById('reset').onclick=()=>setView('front');
  document.getElementById('glass').onchange=e=>{allMeshes.forEach(m=>{if(m.userData.glass)m.visible=e.target.checked;});draw();};
  document.getElementById('ports').onchange=e=>{portsGroup.visible=e.target.checked;draw();};
  document.getElementById('layer').oninput=e=>{
    clippingPlane.constant=+e.target.value+1.01;document.getElementById('layerLabel').textContent=e.target.value;draw();
  };
  const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);
  window.addEventListener('pagehide',()=>{
    disposed=true;resizeObserver.disconnect();controls.dispose();
    allMeshes.forEach(m=>m.geometry.dispose());materialCache.forEach(m=>m.dispose());
    textureCache.forEach(async p=>(await p).dispose());
    portsGroup.children.forEach(m=>{m.geometry.dispose();m.material.dispose();});renderer.dispose();
  },{once:true});
  document.getElementById('loading').remove();document.getElementById('stats').textContent=`${groups.length}个完整静态构件 / ${renderedQuads.toLocaleString()}个合并表面；左键旋转镜头、右键平移、滚轮缩放。`;
  resize();setView('front');
  window.W02Static={config,scene,camera,renderer,controls,groups,setView,
    snapshot:()=>({frames,renderedQuads,fullBounds:{min:fullBounds.min.toArray(),max:fullBounds.max.toArray()},
      transforms:groups.map(g=>({id:g.name,position:g.position.toArray(),rotation:g.quaternion.toArray(),scale:g.scale.toArray()}))})};
  window.W02_STATIC_READY=true;
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent='预览加载失败：'+error.message;});
