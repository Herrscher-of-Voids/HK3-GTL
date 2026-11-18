/** W02十二翼船坞完整取景；原案冲突不靠镜头隐藏。 */
(()=>{function boot(){
  if(!window.BOUNDARY_READY||!window.reviewApi)return setTimeout(boot,100);
  const a=window.reviewApi,d=window.REVIEW.data,o=d.blueprint_to_export_offset_xyz,old=a.setView;
  a.setView=name=>{
    old(name);
    const c=[324+o[0],156+o[1],246+o[2]];
    if(['front','right','back','orthofront','orthoside'].includes(name)){
      a.controls.target.set(...c);
      const views={front:[-850,550,1200],right:[850,550,1200],back:[-850,450,-1200],orthofront:[0,0,1800],orthoside:[1800,0,0]};
      a.camera.position.set(...c.map((x,i)=>x+views[name][i]));a.camera.zoom=.90;
      a.controls.update();a.camera.updateProjectionMatrix();
      const V=a.camera.position.constructor;let limit=0;
      for(const x of [0,d.size[0]])for(const y of [0,d.size[1]])for(const z of [0,d.size[2]]){
        const p=new V(x,y,z).project(a.camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
      }
      a.camera.zoom=Math.min(1.25,a.camera.zoom*.93/limit);
      a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);
    }
  };
  let complete=0,total=0;
  function ready(){complete=0;total=0;a.scene.traverse(m=>{if(m.userData.indices){complete+=m.userData.initialized;total+=m.userData.indices.length;}});
    if(complete<total)return setTimeout(ready,50);a.setView('front');window.W02_BUNNY_READY=true;
  }ready();
}boot();})();
