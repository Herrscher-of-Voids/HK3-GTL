import * as THREE from 'three';

const V = p => new THREE.Vector3(...p);

export function makeEffects(scene, clippingPlane, center=[401,0,361]) {
  const root=new THREE.Group(),ambient=new THREE.Group(),laser=new THREE.Group();
  root.add(ambient,laser);scene.add(root);
  const [cx,,cz]=center;
  const rng=(()=>{let s=0x6d2b79f5;return ()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};})();
  const snowCount=620,snowPositions=new Float32Array(snowCount*3),snowVelocity=new Float32Array(snowCount);
  for(let i=0;i<snowCount;i++){
    snowPositions[i*3]=cx+(rng()-.5)*780;
    snowPositions[i*3+1]=rng()*382;
    snowPositions[i*3+2]=cz+(rng()-.5)*700;
    snowVelocity[i]=2+rng()*5;
  }
  const snowGeometry=new THREE.BufferGeometry();
  snowGeometry.setAttribute('position',new THREE.BufferAttribute(snowPositions,3));
  const snow=new THREE.Points(snowGeometry,new THREE.PointsMaterial({color:'#e5faff',size:3.2,transparent:true,opacity:.72,depthWrite:false,clippingPlanes:[clippingPlane]}));
  ambient.add(snow);

  const starPositions=new Float32Array(90*3);
  for(let i=0;i<90;i++){
    starPositions[i*3]=cx+(rng()-.5)*780;
    starPositions[i*3+1]=24+rng()*352;
    starPositions[i*3+2]=cz+(rng()-.5)*700;
  }
  const starGeometry=new THREE.BufferGeometry();
  starGeometry.setAttribute('position',new THREE.BufferAttribute(starPositions,3));
  const stars=new THREE.Points(starGeometry,new THREE.PointsMaterial({color:'#ffd978',size:5,transparent:true,opacity:.85,depthWrite:false,clippingPlanes:[clippingPlane]}));
  ambient.add(stars);

  const auroraMaterial=new THREE.MeshBasicMaterial({color:'#398bbb',transparent:true,opacity:.105,side:THREE.DoubleSide,depthWrite:false,blending:THREE.AdditiveBlending,clippingPlanes:[clippingPlane]});
  for(let band=0;band<4;band++){
    const positions=[],indices=[];
    const width=1000,steps=72;
    for(let i=0;i<=steps;i++){
      const t=i/steps,x=cx+(t-.5)*width;
      const y=420+band*15+Math.sin(t*9+band*1.4)*24;
      const z=cz-430+band*155+Math.sin(t*14+band)*38;
      positions.push(x,y-55,z,x,y+105,z);
      if(i<steps){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2);}
    }
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geometry.setIndex(indices);geometry.computeVertexNormals();
    ambient.add(new THREE.Mesh(geometry,auroraMaterial));
  }

  const iceBeam=new THREE.Mesh(new THREE.CylinderGeometry(7.5,7.5,382,12),new THREE.MeshBasicMaterial({color:'#a7f4ff',transparent:true,opacity:.52,depthWrite:false,blending:THREE.AdditiveBlending}));
  const goldThread=new THREE.Mesh(new THREE.CylinderGeometry(.72,.72,382,8),new THREE.MeshBasicMaterial({color:'#ffd970',transparent:true,opacity:.92,depthWrite:false,blending:THREE.AdditiveBlending}));
  const beamCore=new THREE.Mesh(new THREE.CylinderGeometry(2.5,2.5,382,8),new THREE.MeshBasicMaterial({color:'#e3fdff',transparent:true,opacity:.42,depthWrite:false,blending:THREE.AdditiveBlending}));
  const beamCenter=new THREE.Group();beamCenter.position.set(cx,191,cz);beamCenter.add(iceBeam,goldThread,beamCore);laser.add(beamCenter);
  const endRings=[];
  for(const y of [1,381]){
    const ring=new THREE.Mesh(new THREE.TorusGeometry(11,.7,6,64),new THREE.MeshBasicMaterial({color:'#c4f8ff',transparent:true,opacity:.7,depthWrite:false,blending:THREE.AdditiveBlending}));
    ring.rotation.x=Math.PI/2;ring.position.set(cx,y,cz);laser.add(ring);endRings.push(ring);
  }

  return {root,ambient,laser,update(time,running){
    for(let i=0;i<snowCount;i++){
      const o=i*3;
      snowPositions[o+1]-=snowVelocity[i]*.18;
      snowPositions[o]+=Math.sin(time*.55+i*.37)*.13;
      if(snowPositions[o+1]<0){snowPositions[o+1]=382;snowPositions[o]=cx+(rng()-.5)*780;snowPositions[o+2]=cz+(rng()-.5)*700;}
    }
    snowGeometry.attributes.position.needsUpdate=true;
    stars.material.opacity=.62+Math.sin(time*2.6)*.18;
    auroraMaterial.opacity=.075+Math.sin(time*.28)*.025;
    laser.visible=running;
    iceBeam.material.opacity=.42+Math.sin(time*4)*.1;
    beamCore.material.opacity=.3+Math.sin(time*5.2+1)*.13;
    endRings.forEach((ring,i)=>{ring.scale.setScalar(1+Math.sin(time*2.8+i)*.08);});
  }};
}
