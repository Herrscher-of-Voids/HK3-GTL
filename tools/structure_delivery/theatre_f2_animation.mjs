export function setupPuppetry({THREE,scene,dominion,puppets,rig}){
  const strings=new THREE.Group();
  strings.name='puppetry_strings';
  scene.add(strings);
  const material=new THREE.LineBasicMaterial({color:0xffd781,transparent:true,opacity:.85,depthTest:true,depthWrite:false});
  const vector=point=>new THREE.Vector3(...point);
  const localPoint=(bone,point)=>vector(point).sub(vector(bone.userData.pivot));
  const actors=Object.keys(rig.hands).map((id,index)=>{
    const hand=dominion.bones.get(rig.hands[id].part),puppet=puppets[id];
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
    return {index,hand,puppet,lines,handPosition:hand.position.clone(),handRotation:hand.rotation.clone(),
      rootPosition:puppet.root.position.clone(),rootRotation:puppet.root.rotation.clone()};
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
      const {index,hand,puppet,handPosition,handRotation,rootPosition,rootRotation}=actor;
      const handMotion=motion(t,index),pose=motion(t-.18,index),side=index===0?-1:1;
      hand.position.set(handPosition.x+handMotion.sway*8,handPosition.y+handMotion.pull*12,handPosition.z+handMotion.forward*10);
      hand.rotation.set(handRotation.x+handMotion.forward*.065,handRotation.y+handMotion.twist*.055,
        handRotation.z+side*handMotion.roll*.07);
      puppet.root.position.set(rootPosition.x+pose.sway*12,rootPosition.y+pose.pull*10,rootPosition.z+pose.forward*14);
      puppet.root.rotation.set(rootRotation.x+pose.forward*.045,rootRotation.y+pose.twist*.06,
        rootRotation.z+pose.sway*.035);
      const bones=puppet.bones;
      bones.get('body').rotation.set(pose.forward*.035,pose.twist*.08,-pose.sway*.025);
      bones.get('head').rotation.set(.22+pose.pull*.035,pose.twist*.04,pose.roll*.025);
      for(const [suffix,direction] of [['l',1],['r',-1]]){
        const knee=Math.sin(pose.phase+(direction===1?0:Math.PI));
        bones.get(`arm_${suffix}`).rotation.set(pose.forward*.05,0,-direction*.7+pose.roll*.055);
        bones.get(`forearm_${suffix}`).rotation.set(pose.pull*.055,0,-direction*.08);
        bones.get(`hand_${suffix}`).rotation.set(pose.roll*.06,pose.twist*.04,0);
        bones.get(`thigh_${suffix}`).rotation.set(knee*.08,0,direction*.025);
        bones.get(`shin_${suffix}`).rotation.set(.18+knee*.13,0,0);
        bones.get(`foot_${suffix}`).rotation.set(-.08-knee*.04,0,0);
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
  return {update,strings,snapshot:()=>({hands:2,puppets:2,strings:10,phase:+(time*.72).toFixed(3),delay:.18})};
}
