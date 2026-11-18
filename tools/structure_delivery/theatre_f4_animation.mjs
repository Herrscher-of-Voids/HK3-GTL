export function setupPuppetry({THREE,scene,dominion,puppets,rig}){
  const strings=new THREE.Group();
  strings.name='puppetry_strings';
  scene.add(strings);
  const material=new THREE.LineBasicMaterial({color:0xffd781,transparent:true,opacity:.85,depthTest:true,depthWrite:false});
  const vector=point=>new THREE.Vector3(...point);
  const localPoint=(bone,point)=>vector(point).sub(vector(bone.userData.pivot));
  const actors=Object.keys(rig.hands).map((id,index)=>{
    const hand=dominion.bones.get(rig.hands[id].part),puppet=puppets[id];
    const pose=rig.poses.find(pose=>pose.actor===id);
    const rotations=new Map([...puppet.bones].map(([name,bone])=>[name,{bone,base:bone.rotation.clone()}]));
    rotations.set('root',{bone:puppet.root,base:puppet.root.rotation.clone()});
    for(const [name,degrees] of Object.entries(pose.angles_degrees)){
      const {base}=rotations.get(name),radians=degrees.map(THREE.MathUtils.degToRad);
      base.set(base.x+radians[0],base.y+radians[1],base.z+radians[2]);
    }
    const points=[...rig.hands[id].points].sort((a,b)=>a[0]-b[0]);
    const targets=[...rig.puppet_targets].sort((a,b)=>a.point[0]-b.point[0]);
    const lines=targets.map((target,i)=>{
      const bone=puppet.bones.get(target.part);
      const geometry=new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(6),3));
      const line=new THREE.Line(geometry,material);
      line.name=`${id}_string_${target.part}`;
      line.frustumCulled=false;
      strings.add(line);
      return {line,bone,top:localPoint(hand,points[i]),bottom:localPoint(bone,target.point)};
    });
    return {index,hand,puppet,lines,rotations,poseName:pose.name,handPosition:hand.position.clone(),
      handRotation:hand.rotation.clone(),rootPosition:puppet.root.position.clone()};
  });
  const motion=(time,index)=>{
    const phase=time*.72+index*Math.PI;
    return {phase,pull:Math.sin(phase),roll:Math.sin(phase+.5),sway:Math.sin(phase*.73+.2),
      forward:Math.sin(phase*.85-.4),twist:Math.sin(phase*.5+.3)};
  };
  const top=new THREE.Vector3(),bottom=new THREE.Vector3();
  let time=0;
  function update(t){
    time=t;
    for(const actor of actors){
      const {index,hand,puppet,handPosition,handRotation,rootPosition}=actor;
      const handMotion=motion(t,index),pose=motion(t-.18,index),side=index===0?-1:1;
      for(const {bone,base} of actor.rotations.values())bone.rotation.copy(base);
      hand.position.set(handPosition.x+handMotion.sway*8,handPosition.y+handMotion.pull*12,handPosition.z+handMotion.forward*10);
      hand.rotation.set(handRotation.x+handMotion.forward*.065,handRotation.y+handMotion.twist*.055,
        handRotation.z+side*handMotion.roll*.07);
      puppet.root.position.set(rootPosition.x+pose.sway*12,rootPosition.y+pose.pull*10,rootPosition.z+pose.forward*14);
      puppet.root.rotation.x+=pose.forward*.035;
      puppet.root.rotation.y+=pose.twist*.05;
      puppet.root.rotation.z+=pose.sway*.03;
      const bones=puppet.bones,body=bones.get('body').rotation,head=bones.get('head').rotation;
      body.x+=pose.forward*.03;
      body.y+=pose.twist*.08;
      body.z-=pose.sway*.025;
      head.x+=pose.pull*.03;
      head.y+=pose.twist*.035;
      head.z+=pose.roll*(index===0?.05:.025);
      for(const [suffix,direction] of [['l',1],['r',-1]]){
        const knee=Math.sin(pose.phase+(direction===1?0:Math.PI));
        bones.get(`arm_${suffix}`).rotation.x+=pose.forward*.04;
        bones.get(`arm_${suffix}`).rotation.z+=pose.roll*.04;
        bones.get(`forearm_${suffix}`).rotation.x+=pose.pull*.035;
        bones.get(`forearm_${suffix}`).rotation.z+=direction*pose.roll*.03;
        bones.get(`hand_${suffix}`).rotation.x+=pose.roll*.06;
        bones.get(`hand_${suffix}`).rotation.y+=pose.twist*.04;
        bones.get(`thigh_${suffix}`).rotation.x+=knee*.06;
        bones.get(`thigh_${suffix}`).rotation.z+=direction*pose.sway*.018;
        bones.get(`shin_${suffix}`).rotation.x+=knee*.08;
        bones.get(`foot_${suffix}`).rotation.x-=.04+knee*.03;
      }
    }
    scene.updateMatrixWorld(true);
    for(const actor of actors){
      for(const {line,bone,top:upper,bottom:lower} of actor.lines){
        actor.hand.localToWorld(top.copy(upper));
        bone.localToWorld(bottom.copy(lower));
        const position=line.geometry.attributes.position;
        position.setXYZ(0,top.x,top.y,top.z);
        position.setXYZ(1,bottom.x,bottom.y,bottom.z);
        position.needsUpdate=true;
      }
    }
  }
  return {update,strings,snapshot:()=>({hands:2,puppets:2,strings:10,poses:actors.map(actor=>actor.poseName),
    phase:+(time*.72).toFixed(3),delay:.18})};
}
