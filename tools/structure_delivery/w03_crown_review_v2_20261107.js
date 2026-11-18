/** 原案悬环观察预设；只隐藏玻璃，不改体素或制造剖切面。 */
(() => {
  function boot() {
    if(!window.reviewApi||!window.REVIEW_READY)return setTimeout(boot,100);
    const api=window.reviewApi,original=api.setView;
    function glass(value){const e=document.getElementById('showGlass');e.checked=value;e.dispatchEvent(new Event('change'));}
    function fit(name){
      if(['front','right','back','inside'].includes(name))api.camera.zoom=1.1;
      if(name==='controller')api.camera.zoom=12;
      const paths=document.getElementById('showPaths');paths.checked=false;paths.dispatchEvent(new Event('change'));
      api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
    }
    api.setView=name=>{
      if(name==='crown'){original('front');glass(false);document.getElementById('viewName').textContent='悬环与十二刺桩 · 隐藏真实玻璃面';fit('front');return;}
      original(name);fit(name);
    };
    for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>fit(e.dataset.view));
    document.getElementById('crownView').onclick=()=>api.setView('crown');
    document.getElementById('completeView').onclick=()=>{for(const e of document.querySelectorAll('[data-material]'))if(!e.checked){e.checked=true;e.dispatchEvent(new Event('change'));}api.setView('front');glass(true);};
    fit('front');window.W03_CROWN_READY=true;
  }
  boot();
})();
