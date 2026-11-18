import * as THREE from 'three';

const V = p => new THREE.Vector3(...p);

export function makeEffects(scene, parts, groups, clippingPlane) {
  const root = new THREE.Group(), working = new THREE.Group(), persistent = new THREE.Group();
  root.add(persistent, working); scene.add(root);
  const moving = [], pulses = [], vortexMeshes = [];
  const light = (color, opacity) => new THREE.MeshBasicMaterial({color, transparent:true, opacity,
    depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, clippingPlanes:[clippingPlane]});
  const green = light('#36f6c0', .23), white = light('#ccfff4', .7), cyan = light('#79fbe9', .28);
  function tube(parent, points, radius, material, closed=false) {
    const curve = new THREE.CatmullRomCurve3(points.map(V), closed, 'centripetal');
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(36, points.length*2), radius, 5, closed), material);
    parent.add(mesh); return {mesh, curve};
  }
  function helix(cx, cz, bottom, top, radius, turns, phase, samples=120) {
    return Array.from({length:samples}, (_,i) => {
      const t=i/(samples-1), angle=turns*2*Math.PI*t+phase;
      const r=radius*(.36+.64*t);
      return [cx+r*Math.cos(angle), bottom+(top-bottom)*t, cz+r*Math.sin(angle)];
    });
  }
  // 逐条沿蓝图管道中线运动；几何未注明的流速仅用于预览演示。
  const paths=parts.flatMap(p => (p.metadata.flow_paths || []).map((path,index) => index===0?path:path.slice(0,path.length/2+1)));
  const streamPaths=[];
  for (const side of [-1,1]) {
    for (let i=0;i<10;i++) {
      const a=i/10*Math.PI*2, r=12+(i%3)*9;
      const wingPaths=paths.filter(p => Math.sign(p[Math.floor(p.length/3)][0])===side);
      const loop=wingPaths[i%wingPaths.length];
      const p=[[-r*Math.sin(a),160+r*Math.cos(a),-350],[r*Math.sin(a),160+r*Math.cos(a),-210],[0,160,0],
        ...loop,[0,160,90],[r*Math.sin(a),160+r*Math.cos(a),250],[r*Math.sin(a)*1.7,160+r*Math.cos(a)*1.7,350]];
      const {curve}=tube(working,p,.35,green);
      streamPaths.push(curve);
      for (let j=0;j<7;j++) {
        const bead=new THREE.Mesh(new THREE.SphereGeometry(j%3===0?1.65:.95,6,4),white);
        working.add(bead); moving.push({mesh:bead,curve,phase:j/7+i*.017,speed:.034});
      }
    }
  }
  const towerEffects=parts.map(p=>p.metadata.effect).filter(e=>e?.kind==='vortex_tower');
  for(const e of towerEffects) {
    const group=new THREE.Group();persistent.add(group);
    group.position.set(e.center[0],0,e.center[2]);
    for(let i=0;i<3;i++)tube(group,helix(0,0,e.bottom,e.top,e.radius,2.7,i*Math.PI*2/3),.75,cyan);
    vortexMeshes.push({mesh:group,speed:.25});
  }
  // 原文的翼尖向内电弧、尾喷激波与王冠光幕均为渲染层，不增加实体方块。
  for(const part of parts.filter(p=>p.metadata.effect?.kind==='lightning')) {
    const [sx,sy,sz]=part.metadata.effect.origin;
    const side=Math.sign(sx);
    for(let i=0;i<4;i++) {
      const points=Array.from({length:15},(_,j)=>{
        const t=j/14;
        return [sx*(1-t)+Math.sin(j*2.7+i)*10*Math.sin(t*Math.PI),
          sy*(1-t)+160*t+(i-1.5)*9*Math.sin(t*Math.PI),
          sz*(1-t)+Math.cos(j*1.9+i)*11*Math.sin(t*Math.PI)];
      });
    const material=light('#38ffb1',.6),{mesh}=tube(persistent,points,.55,material);
      pulses.push({mesh,material,phase:i+side});
    }
  }
  for(let i=0;i<4;i++) {
    const z=295+i*15,r=30-i*5;
    const pts=Array.from({length:65},(_,j)=>[r*Math.cos(j/64*Math.PI*2),160+r*Math.sin(j/64*Math.PI*2),z]);
    const {mesh}=tube(persistent,pts,1,cyan,true);pulses.push({mesh,material:cyan,phase:i});
  }
  for(let i=0;i<3;i++) {
    const start=278+i*23,end=start+23;
    const points=Array.from({length:40},(_,j)=>{
      const t=j/39,a=t*Math.PI*2,r=13+Math.sin(t*Math.PI)*15;
      return [r*Math.cos(a),160+r*Math.sin(a),start+(end-start)*t];
    });
    tube(persistent,points,.8,white);
  }
  const funnel=new THREE.Group();persistent.add(funnel);
  for(let i=0;i<24;i++) {
    const a=i/24*Math.PI*2;
    const points=Array.from({length:40},(_,j)=>{
      const t=j/39,y=160+130*t,r=18+106*t*t;
      return [r*Math.cos(a+t*.7),y,r*Math.sin(a+t*.7)];
    });
    tube(funnel,points,.9,green);
  }
  const veilPositions=[];
  for(let j=0;j<24;j++)for(let i=0;i<36;i++) {
    const coords=[];
    for(const [da,dt] of [[0,0],[1,0],[1,1],[0,0],[1,1],[0,1]]) {
      const t=(i+dt)/36,a=(j+da*.76)/24*2*Math.PI+t*.7,r=18+106*t*t;
      coords.push(r*Math.cos(a),160+130*t,r*Math.sin(a));
    }
    veilPositions.push(...coords);
  }
  const veilGeometry=new THREE.BufferGeometry();
  veilGeometry.setAttribute('position',new THREE.Float32BufferAttribute(veilPositions,3));veilGeometry.computeVertexNormals();
  funnel.add(new THREE.Mesh(veilGeometry,light('#5eebd0',.035)));
  const tornado=new THREE.Group();working.add(tornado);
  for(let i=0;i<6;i++)tube(tornado,helix(0,0,8,320,35,3.1,i*Math.PI/3),1.6,cyan);
  const refractive=new THREE.MeshPhysicalMaterial({color:'#c5fff2',transparent:true,opacity:.22,
    transmission:.78,roughness:.03,metalness:0,ior:1.06,thickness:2,side:THREE.DoubleSide,
    depthWrite:false,clippingPlanes:[clippingPlane]});
  for(let i=0;i<3;i++) {
    const pts=Array.from({length:100},(_,j)=>{
      const t=j/99,a=t*Math.PI*5,r=35+i*8+Math.sin(t*Math.PI)*9;
      return [r*Math.cos(a),160+(t-.5)*77,r*Math.sin(a)];
    });
    const {mesh}=tube(working,pts,2.2,refractive);vortexMeshes.push({mesh,speed:(i%2?-.4:.4)});
    mesh.geometry.translate(0,-160,0);mesh.position.y=160;
  }
  for(const part of parts)for(const a of part.metadata.accents || []) {
    const accent=new THREE.Mesh(new THREE.OctahedronGeometry(a.radius),new THREE.MeshStandardMaterial({
      color:a.color,emissive:a.color,emissiveIntensity:.22,metalness:.25,roughness:.3,clippingPlanes:[clippingPlane]}));
    const group=groups.find(g=>g.name===part.id);
    accent.position.copy(V(a.center).sub(group.position));group.add(accent);
  }
  return {
    root,working,persistent,
    update(time,running) {
      working.visible=running;
      moving.forEach(p=>p.mesh.position.copy(p.curve.getPointAt((time*p.speed+p.phase)%1)));
      vortexMeshes.forEach(p=>p.mesh.rotation.y=time*p.speed*(running?2.5:1));
      tornado.rotation.y=-time*.65;
      pulses.forEach(p=>p.mesh.visible=Math.sin(time*5.5+p.phase*2)>-.55);
    }
  };
}
