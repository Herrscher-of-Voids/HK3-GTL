export function createEyeMotion(THREE, materials, textures, clippingPlane){
  const group=new THREE.Group();group.name='moving-eye';group.userData.modelId='screen';
  const geometry=new THREE.BoxGeometry(1,1,1),matrix=new THREE.Matrix4(),cells=new Map(),ownedMaterials=[];
  for(let y=-51;y<=51;y++)for(let x=-47;x<=47;x++){
    const r=Math.hypot(x/.75,y/.82);
    if(r>63)continue;
    let state=17;
    if(r<=60)state=21;
    if(r<=36)state=18;
    if(r<=28)state=16;
    if(r<=23)state=13;
    if(r<=20)state=10;
    if(r<=17)state=21;
    if(r<=4)state=17;
    const material=state-1,z=Math.round(3*(1-r*r/(63*63)));
    if(!cells.has(material))cells.set(material,[]);
    cells.get(material).push([x,y,z]);
    if(r>60)cells.get(material).push([x,y,z-1],[x,y,z-2]);
  }
  let voxelCount=0;
  for(const [material,positions] of cells){
    const faces=[0,1,5,4,2,3].map(face=>{
      const map=textures[material][['east','west','south','north','down','up'][face]];
      const surface=new THREE.MeshLambertMaterial({map,clippingPlanes:[clippingPlane],emissive:0xffffff,emissiveMap:map,emissiveIntensity:.24,alphaTest:.01});
      surface.userData.screen=true;ownedMaterials.push(surface);return surface;
    });
    const mesh=new THREE.InstancedMesh(geometry,faces,positions.length);
    mesh.userData.material=material;mesh.userData.eyeDynamic=true;
    positions.forEach(([x,y,z],index)=>{matrix.makeTranslation(x,y,z);mesh.setMatrixAt(index,matrix);});
    mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();group.add(mesh);voxelCount+=positions.length;
  }
  const gaze=[[0,0],[.9,.3],[-.55,-.55],[-1,.45],[.35,.85],[1,-.4],[0,0]];
  let enabled=false,offset=[0,0,0],angles=[0,0,0];
  function update(seconds,active){
    enabled=active;
    let x=0,y=0;
    if(active){
      const step=seconds/3,index=Math.floor(step)%gaze.length,phase=step-Math.floor(step);
      const blend=Math.max(0,(phase-.4)/.6),ease=blend*blend*(3-2*blend);
      const from=gaze[index],to=gaze[(index+1)%gaze.length];
      x=(from[0]+(to[0]-from[0])*ease)*16;y=(from[1]+(to[1]-from[1])*ease)*3;
    }
    offset=[x,y,0];angles=[-y*.02,x*.005625,active?Math.sin(seconds*.7)*.012:0];
    group.position.set(.5+x,525.5+y,254.5);group.rotation.set(...angles);
    ownedMaterials.forEach(material=>material.emissiveIntensity=active?.24:.17);
  }
  update(0,false);
  return {group,update,state:()=>({enabled,voxelCount,offset:[...offset],angles:[...angles],center:group.position.toArray()}),dispose(){geometry.dispose();ownedMaterials.forEach(material=>material.dispose());}};
}
