/** W03取景与真实内腔预设；隐藏外壳不补画内部表面。 */
(() => {
  function boot() {
    if (!window.reviewApi || !window.REVIEW_READY) return setTimeout(boot,100);
    const api=window.reviewApi,original=api.setView;
    const shellIndex=window.REVIEW.materials.findIndex(m=>m.state==='hk3gtl:voltage_machine_casing_hcv');
    if(shellIndex<0)throw new Error('锚座预设缺少HCV主体材料');
    function full() {
      for(const e of document.querySelectorAll('[data-material]'))if(!e.checked){e.checked=true;e.dispatchEvent(new Event('change'));}
      const glass=document.getElementById('showGlass');if(!glass.checked){glass.checked=true;glass.dispatchEvent(new Event('change'));}
    }
    function fit(name) {
      if(['front','back','right','inside'].includes(name))api.camera.zoom=1.1;
      if(name==='controller') {
        api.camera.zoom=9;
        const paths=document.getElementById('showPaths');paths.checked=false;paths.dispatchEvent(new Event('change'));
      }
      api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
    }
    api.setView=name=>{
      if(name==='anchor') {
        full();original('front');
        const e=document.querySelector(`[data-material="${shellIndex}"]`);e.checked=false;e.dispatchEvent(new Event('change'));
        const glass=document.getElementById('showGlass');glass.checked=false;glass.dispatchEvent(new Event('change'));
        document.getElementById('viewName').textContent='锚座内腔 · 隐藏HCV主体与玻璃；只显示真实内部表面';
        fit('front');return;
      }
      original(name);fit(name);
    };
    for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>fit(e.dataset.view));
    document.getElementById('anchorView').addEventListener('click',()=>api.setView('anchor'));
    document.getElementById('completeView').addEventListener('click',()=>{full();api.setView('front');});
    api.restoreComplete=full;fit('front');window.W03_READY=true;
  }
  boot();
})();
