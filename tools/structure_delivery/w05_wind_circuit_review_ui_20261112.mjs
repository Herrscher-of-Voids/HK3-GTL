import * as THREE from 'three';

export function attachReviewControls(view) {
  const {scene,renderer,config,groups,draw}=view;
  const visible=new Set(config.materials.map((_,i)=>i));
  const meshes=groups.flatMap(group=>group.children);
  const apply=()=>{meshes.forEach(mesh=>mesh.visible=visible.has(mesh.userData.material)&&(!mesh.userData.glass||document.getElementById('glass').checked));draw();};
  document.querySelectorAll('[data-material]').forEach(input=>input.onchange=()=>{
    const id=+input.dataset.material;input.checked?visible.add(id):visible.delete(id);apply();
  });
  document.getElementById('materialSearch').oninput=event=>{
    const query=event.target.value.toLowerCase();
    document.querySelectorAll('[data-material-row]').forEach(row=>row.hidden=!row.textContent.toLowerCase().includes(query));
  };
  document.getElementById('glass').onchange=apply;
  const size=Math.max(config.data.size[0],config.data.size[2]);
  const grid=new THREE.GridHelper(size,Math.ceil(size/16),0x4f9d8a,0x253b38);
  grid.position.set(config.data.size[0]/2,-.05,config.data.size[2]/2);grid.visible=false;scene.add(grid);
  document.getElementById('grid').onchange=event=>{grid.visible=event.target.checked;draw();};
  document.getElementById('fullscreen').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  document.getElementById('screenshot').onclick=()=>{
    draw();const link=document.createElement('a');link.download='W05-长风环流阵.png';link.href=renderer.domElement.toDataURL('image/png');link.click();
  };
  window.addEventListener('pagehide',()=>{grid.geometry.dispose();grid.material.dispose();},{once:true});
}
