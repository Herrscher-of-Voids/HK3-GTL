/** DeepSeek改进取景；新增仰视只改相机，不修改实体。 */
(() => {
  function boot(){
    if(!window.reviewApi||!window.REVIEW_READY)return setTimeout(boot,100);
    const api=window.reviewApi,original=api.setView;
    function glass(value){const e=document.getElementById('showGlass');e.checked=value;e.dispatchEvent(new Event('change'));}
    function fit(name){
      if(['front','right','back','inside','low'].includes(name))api.camera.zoom=1.1;
      if(name==='controller')api.camera.zoom=10;
      const paths=document.getElementById('showPaths');paths.checked=false;paths.dispatchEvent(new Event('change'));
      api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
    }
    api.setView=name=>{
      api.controls.maxPolarAngle=Math.PI*(name==='low'?.65:.49);
      if(name==='crown'){original('front');glass(false);document.getElementById('viewName').textContent='悬天瞳孔与十二长锚 · 隐藏真实玻璃';fit('front');return;}
      if(name==='low'){
        original('front');api.camera.up.set(0,1,0);api.controls.target.set(336,146,264);
        api.camera.position.set(960,22,-730);api.controls.update();
        document.getElementById('viewName').textContent='地面仰视 · Y200瞳孔环与不触地长锚';fit(name);return;
      }
      original(name);fit(name);
    };
    for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>e.dataset.view==='low'?api.setView('low'):fit(e.dataset.view));
    document.getElementById('crownView').onclick=()=>api.setView('crown');
    document.getElementById('completeView').onclick=()=>{for(const e of document.querySelectorAll('[data-material]'))if(!e.checked){e.checked=true;e.dispatchEvent(new Event('change'));}api.setView('front');glass(true);};
    fit('front');window.W03_CROWN_READY=true;
  }
  boot();
})();
