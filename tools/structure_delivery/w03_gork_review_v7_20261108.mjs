/** Gork概念能流与奇点薄环；静态实体默认完整显示，不修改结构载荷。 */
import {Group,Vector3,BufferGeometry,Line,LineBasicMaterial,SphereGeometry,MeshBasicMaterial,InstancedMesh,Object3D,Color,AdditiveBlending} from 'three';

function boot(){
  if(!window.BOUNDARY_READY||!window.reviewApi)return setTimeout(boot,100);
  const api=window.reviewApi,data=window.REVIEW.data,input=document.getElementById('energyPreview');
  const state=document.getElementById('energyState'),group=new Group();group.name='gork-concept-energy';group.visible=false;api.scene.add(group);
  const routes=data.preview_flows.map(f=>({...f,points:f.path.map(p=>new Vector3(...p).addScalar(.5))}));
  const count=routes.length*4,beads=new InstancedMesh(new SphereGeometry(1.25,6,4),new MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.9,blending:AdditiveBlending,depthWrite:false}),count);
  beads.frustumCulled=false;group.add(beads);const dummy=new Object3D(),p=new Vector3();
  const halos=data.preview_halos.map((h,i)=>{
    const ring=new Group();ring.position.set(...h.center.map(n=>n+.5));
    const points=Array.from({length:241},(_,j)=>{const t=j/240*Math.PI*2;return new Vector3(h.radius*Math.cos(t),h.radius*Math.sin(t)*Math.sin(h.tilt),h.radius*Math.sin(t)*Math.cos(h.tilt));});
    ring.add(new Line(new BufferGeometry().setFromPoints(points),new LineBasicMaterial({color:i%2?0xd0fbff:0xbb7dff,transparent:true,opacity:.95,blending:AdditiveBlending,depthWrite:false})));
    group.add(ring);return ring;
  });
  const roofCenter=new Vector3(336,315,264).add(new Vector3(...data.blueprint_to_export_offset_xyz));
  const stars=new InstancedMesh(beads.geometry,beads.material,480),starPositions=[];stars.frustumCulled=false;group.add(stars);
  for(let i=0;i<480;i++){
    const radius=.16+((i*73)%421)/500,angle=Math.floor(i/40)*Math.PI/6+Math.sin(i*2.17)*.043;
    starPositions.push(new Vector3(320*radius*Math.cos(angle),40*(1-radius*radius)+Math.sin(i)*3,260*radius*Math.sin(angle)).add(roofCenter));
    stars.setColorAt(i,new Color(i%3?0xc1a5ff:0xe2fdff));
  }
  const roofHalos=Array.from({length:3},(_,i)=>{
    const angle=i*Math.PI*2/3,r=.53,ring=new Group();ring.position.copy(roofCenter).add(new Vector3(320*r*Math.cos(angle),40*(1-r*r),260*r*Math.sin(angle)));
    const points=Array.from({length:121},(_,j)=>{const t=j*Math.PI/60;return new Vector3(8*Math.cos(t),3*Math.sin(t),8*Math.sin(t));});
    ring.add(new Line(new BufferGeometry().setFromPoints(points),new LineBasicMaterial({color:0xc3f6ff,transparent:true,opacity:.8,blending:AdditiveBlending,depthWrite:false})));group.add(ring);return ring;
  });
  let active=false,manual=false,guard=false,savedHalo=true,raf=0,start=0,last=0,frames=0,time=0;
  const haloIndex=window.REVIEW.materials.findIndex(m=>m.state==='minecraft:light_blue_stained_glass');
  const haloBox=document.querySelector(`[data-material="${haloIndex}"]`);
  if(!haloBox)throw new Error('概念演示缺少独立奇点环材质');
  function draw(seconds){
    time=seconds;let n=0;
    for(let i=0;i<routes.length;i++){
      const f=routes[i],speed=f.kind==='main'?16:f.kind==='cable'?4:8;
      for(let j=0;j<4;j++){
        const t=((seconds/speed+j/4+i*.131)%1+1)%1,k=t*(f.points.length-1),a=Math.floor(k),b=Math.min(a+1,f.points.length-1);
        p.copy(f.points[a]).lerp(f.points[b],k-a);dummy.position.copy(p);dummy.scale.setScalar(f.kind==='main'?1.7:f.kind==='cable'?.75:1.15);dummy.updateMatrix();beads.setMatrixAt(n,dummy.matrix);
        beads.setColorAt(n,new Color(j%2?0xd4fcff:0xb17bff));n++;
      }
    }
    beads.instanceMatrix.needsUpdate=true;if(beads.instanceColor)beads.instanceColor.needsUpdate=true;
    halos.forEach((ring,i)=>{ring.rotation.y=seconds*.18*(i%2?-1:1);ring.rotation.x=Math.sin(seconds*.22+i)*.2;});
    for(let i=0;i<starPositions.length;i++){dummy.position.copy(starPositions[i]);dummy.scale.setScalar(.22+.32*(.5+.5*Math.sin(seconds*1.7+i*.37)));dummy.updateMatrix();stars.setMatrixAt(i,dummy.matrix);}
    stars.instanceMatrix.needsUpdate=true;roofHalos.forEach((ring,i)=>{ring.rotation.y=seconds*.13*(i%2?-1:1);ring.rotation.x=.2*Math.sin(seconds*.19+i);});
    api.renderer.render(api.scene,api.camera);frames++;
  }
  function tick(now){
    raf=0;if(!active||manual||document.hidden)return;
    if(now-last>=33){draw((now-start)/1000);last=now;}
    raf=requestAnimationFrame(tick);
  }
  function setEnabled(value){
    if(active===value)return;guard=true;
    if(value){
      const layer=document.getElementById('layer');layer.value=String(data.size[1]-1);layer.dispatchEvent(new Event('input'));
      savedHalo=haloBox.checked;haloBox.checked=false;haloBox.dispatchEvent(new Event('change'));
      active=true;manual=false;group.visible=true;input.checked=true;start=performance.now();last=0;draw(0);raf=requestAnimationFrame(tick);
      state.textContent='概念演示中：能流移动、奇点薄环旋转，穹盖间隙星光闪烁并有浮游光环；游戏内尚未实装。';
    }else{
      active=false;manual=false;cancelAnimationFrame(raf);raf=0;group.visible=false;input.checked=false;
      haloBox.checked=savedHalo;haloBox.dispatchEvent(new Event('change'));api.renderer.render(api.scene,api.camera);
      state.textContent='静态完整实体；蓝图与导出文件保持原始姿态。';
    }
    guard=false;
  }
  input.addEventListener('change',()=>setEnabled(input.checked));
  for(const e of document.querySelectorAll('[data-material],#showGlass,#layer,#reset')){
    e.addEventListener(e.id==='layer'?'input':e.id==='reset'?'click':'change',()=>{if(!guard)setEnabled(false);});
  }
  document.addEventListener('visibilitychange',()=>{cancelAnimationFrame(raf);raf=0;if(active&&!manual&&!document.hidden)raf=requestAnimationFrame(tick);});
  document.getElementById('coreView').onclick=()=>{
    const center=data.preview_halos[0].center;api.controls.target.set(...center);api.camera.position.set(center[0]+520,center[1]+270,center[2]+460);api.controls.update();api.camera.zoom=2.3;api.camera.updateProjectionMatrix();api.renderer.render(api.scene,api.camera);
    document.getElementById('viewName').textContent='奇点、中轴与汇聚导管近景';
  };
  api.energyPreview={setEnabled,setTime:draw,freezeAt:seconds=>{manual=true;cancelAnimationFrame(raf);raf=0;draw(seconds);},
    diagnostics:()=>({active,manual,frames,time,routes:routes.length,particles:count,roofStars:480,roofHalos:3,staticHaloHidden:!haloBox.checked,overlayVisible:group.visible,rotation:halos[0].rotation.toArray().slice(0,3),firstParticle:[...beads.instanceMatrix.array.slice(12,15)],firstStarScale:stars.instanceMatrix.array[0]})};
  window.GORK_PREVIEW_READY=true;
}
boot();
