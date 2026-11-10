/** Gemini原案取景；隐藏真实玻璃以观察三环与矛阵，不补画内部切面。 */
(() => {
  function boot(){
    if(!window.reviewApi||!window.REVIEW_READY)return setTimeout(boot,100);
    const api=window.reviewApi,original=api.setView;
    function glass(value){const e=document.getElementById('showGlass');e.checked=value;e.dispatchEvent(new Event('change'));}
    function fit(name){
      if(['front','right','back','inside'].includes(name))api.camera.zoom=1.1;
      if(name==='controller')api.camera.zoom=18;
      const paths=document.getElementById('showPaths');paths.checked=false;paths.dispatchEvent(new Event('change'));
      api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
    }
    api.setView=name=>{
      if(name==='celestial'){original('front');glass(false);document.getElementById('viewName').textContent='三环与十二柄矛 · 隐藏真实玻璃材质';fit('front');return;}
      original(name);fit(name);
    };
    for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>fit(e.dataset.view));
    document.getElementById('celestialView').onclick=()=>api.setView('celestial');
    document.getElementById('completeView').onclick=()=>{for(const e of document.querySelectorAll('[data-material]'))if(!e.checked){e.checked=true;e.dispatchEvent(new Event('change'));}api.setView('front');glass(true);};
    fit('front');window.W03_CELESTIAL_READY=true;
  }
  boot();
})();
