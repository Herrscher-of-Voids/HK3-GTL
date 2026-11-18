/** W02专用取景和材质隐藏预设；只操作真实表面，不补画或替换建筑。 */
(() => {
  function boot() {
    if (!window.reviewApi || !window.REVIEW_READY) return setTimeout(boot,100);
    const api=window.reviewApi, original=api.setView;
    const shellIndex=window.REVIEW.materials.findIndex(m=>m.state==='hk3gtl:voltage_machine_casing_hbv');
    if(shellIndex<0)throw new Error('递归预设缺少HBV主体材料');
    function full() {
      for(const e of document.querySelectorAll('[data-material]'))if(!e.checked){e.checked=true;e.dispatchEvent(new Event('change'));}
      const glass=document.getElementById('showGlass');if(!glass.checked){glass.checked=true;glass.dispatchEvent(new Event('change'));}
    }
    function fit(name) {
      const camera=api.camera;
      if(['front','back','right','inside'].includes(name)) camera.zoom=1.25;
      if(name==='controller')camera.zoom=9;
      camera.updateProjectionMatrix();api.renderer.render(api.scene,camera);
    }
    api.setView=name=>{
      if(name==='recursive') {
        full();original('front');
        const e=document.querySelector(`[data-material="${shellIndex}"]`);e.checked=false;e.dispatchEvent(new Event('change'));
        const glass=document.getElementById('showGlass');glass.checked=false;glass.dispatchEvent(new Event('change'));
        document.getElementById('viewName').textContent='递归内腔 · 隐藏HBV主体与玻璃；只显示真实内部表面';
        fit('front');return;
      }
      original(name);fit(name);
    };
    for(const e of document.querySelectorAll('[data-view]'))e.addEventListener('click',()=>fit(e.dataset.view));
    document.getElementById('recursiveView').addEventListener('click',()=>api.setView('recursive'));
    document.getElementById('completeView').addEventListener('click',()=>{full();api.setView('front');});
    api.restoreComplete=full;fit('front');window.W02_READY=true;
  }
  boot();
})();
