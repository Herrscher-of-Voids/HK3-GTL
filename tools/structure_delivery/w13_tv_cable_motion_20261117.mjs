const SPECS = [
  {p:[[-260,365,170],[-350,160,330],[-490,-10,410],[-475,120,395]],r:17},
  {p:[[-110,360,195],[-170,140,400],[-250,-50,480],[-280,65,430]],r:14},
  {p:[[30,360,180],[20,140,320],[-30,-5,460],[0,32,450]],r:16},
  {p:[[210,360,160],[330,130,330],[505,0,415],[470,120,360]],r:18},
  {p:[[390,380,-70],[520,170,-20],[520,40,180],[450,160,210]],r:15},
  {p:[[230,360,-150],[390,180,-290],[440,50,-425],[390,125,-400]],r:14},
  {p:[[-20,360,-170],[-25,130,-310],[80,20,-430],[90,155,-385]],r:13},
  {p:[[-250,360,-150],[-430,210,-270],[-510,50,-305],[-450,165,-265]],r:16},
  {p:[[-390,380,5],[-490,220,40],[-505,80,170],[-425,125,205]],r:13},
];
const FACE_NAMES = ['east','west','south','north','down','up'];
const NORMALS = [[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
const CORNERS = [
  [[1,0,0],[1,1,0],[1,1,1],[1,0,1]],
  [[0,0,1],[0,1,1],[0,1,0],[0,0,0]],
  [[1,0,1],[1,1,1],[0,1,1],[0,0,1]],
  [[0,0,0],[0,1,0],[1,1,0],[1,0,0]],
  [[0,0,1],[0,0,0],[1,0,0],[1,0,1]],
  [[0,1,0],[0,1,1],[1,1,1],[1,1,0]],
];

export function createCableMotion(THREE, materials, textures, clippingPlane) {
  const group = new THREE.Group();
  group.name = 'cables_motion';
  group.visible = false;
  const geometries = [], ownMaterials = [], materialCache = new Map();
  const up = new THREE.Vector3(0,1,0), delta = new THREE.Quaternion();
  const direction = new THREE.Vector3(), rotation = new THREE.Euler();
  let enabled = false, seconds = 0, voxelBlocks = 0, renderedQuads = 0;

  function faceMaterials(material) {
    if (!materialCache.has(material)) {
      const info = materials[material];
      const faces = FACE_NAMES.map(face => new THREE.MeshLambertMaterial({
        map:textures[material][face], transparent:info.transparent,
        opacity:info.transparent ? .54 : 1, depthWrite:!info.transparent,
        alphaTest:.01, side:THREE.DoubleSide, clippingPlanes:[clippingPlane],
        emissive:info.emissive ? 0xffffff : 0,
        emissiveMap:textures[material][face], emissiveIntensity:info.emissive ? .22 : 0,
      }));
      ownMaterials.push(...faces);
      materialCache.set(material,faces);
    }
    return materialCache.get(material);
  }

  function makeSegment(length, radius, start, end, collars, first, plug) {
    const object = new THREE.Group(), outer = radius + (plug ? 6 : 4);
    const low = first ? 0 : -2, high = Math.ceil(length) + (plug ? 39 : 2);
    const size = [outer*2,high-low,outer*2], [nx,ny,nz] = size;
    const cells = new Uint8Array(nx*ny*nz);
    const index = (x,y,z) => (y*nz+z)*nx+x;
    let blocks = 0;
    for (let y=0;y<ny;y++) {
      const localY = y+low+.5, s = start+(end-start)*localY/length;
      const collar = collars.find(item => s>=item.start && s<item.end);
      for (let z=0;z<nz;z++) for (let x=0;x<nx;x++) {
        const d = (x-outer+.5)**2+(z-outer+.5)**2;
        let material = d<=radius**2 && d>=(radius-3)**2 ? 1 : 0;
        if (collar && d<=(radius+collar.extra)**2 && d>=(radius-2)**2) material=collar.material+1;
        if (plug && localY>=length) {
          const p = localY-length;
          material = p<29
            ? (d<=(radius+5)**2 && d>=(radius-3)**2 ? 2 : 0)
            : (d<=(radius-4)**2 ? 4 : 0);
          if (p>=11 && p<19 && d<=(radius+6)**2 && d>=(radius-2)**2) material=10;
        }
        cells[index(x,y,z)]=material;
        if (material) blocks++;
      }
    }
    voxelBlocks += blocks;
    const surfaces = new Map();
    function emit(material,face,base,width,height) {
      if (!surfaces.has(material)) surfaces.set(material,Array.from({length:6},()=>[]));
      surfaces.get(material)[face].push([base,width,height]);
      renderedQuads++;
    }
    for (let face=0;face<6;face++) {
      const fixed = face<2 ? 0 : face<4 ? 2 : 1;
      const axis = face<2 ? 2 : 0, cross = face<4 ? 1 : 2;
      const width = size[axis], height = size[cross], mask = new Uint8Array(width*height);
      const sign = face%2===0 && face<4 || face===5 ? 1 : -1;
      for (let slice=0;slice<size[fixed];slice++) {
        mask.fill(0);
        for (let v=0;v<height;v++) for (let u=0;u<width;u++) {
          const cell=[0,0,0];cell[fixed]=slice;cell[axis]=u;cell[cross]=v;
          const material=cells[index(...cell)];
          if (!material) continue;
          cell[fixed]+=sign;
          const neighbor=cell[fixed]>=0 && cell[fixed]<size[fixed] ? cells[index(...cell)] : 0;
          if (!neighbor) mask[v*width+u]=material;
        }
        for (let v=0;v<height;v++) for (let u=0;u<width;u++) {
          const material=mask[v*width+u];
          if (!material) continue;
          let w=1,h=1;
          while (u+w<width && mask[v*width+u+w]===material) w++;
          outer: while (v+h<height) {
            for (let k=0;k<w;k++) if (mask[(v+h)*width+u+k]!==material) break outer;
            h++;
          }
          for (let row=0;row<h;row++) mask.fill(0,(v+row)*width+u,(v+row)*width+u+w);
          const base=[0,0,0];base[fixed]=slice;base[axis]=u;base[cross]=v;
          base[0]-=outer;base[1]+=low;base[2]-=outer;
          emit(material-1,face,base,w,h);
        }
      }
    }
    for (const [material,faces] of surfaces) {
      const count=faces.reduce((sum,quads)=>sum+quads.length,0);
      const positions=new Float32Array(count*12), normals=new Float32Array(count*12);
      const uvs=new Float32Array(count*8), indices=new Uint32Array(count*6);
      const geometry=new THREE.BufferGeometry();
      let q=0;
      faces.forEach((quads,face)=>{
        const firstIndex=q*6,axis=face<2 ? 2 : 0,cross=face<4 ? 1 : 2;
        for (const [base,width,height] of quads) {
          for (let v=0;v<4;v++) {
            const corner=CORNERS[face][v];
            for (let k=0;k<3;k++) {
              positions[q*12+v*3+k]=base[k]+corner[k]*(k===axis ? width : k===cross ? height : 1);
              normals[q*12+v*3+k]=NORMALS[face][k];
            }
            uvs[q*8+v*2]=corner[axis]*width;uvs[q*8+v*2+1]=corner[cross]*height;
          }
          indices.set([q*4,q*4+1,q*4+2,q*4,q*4+2,q*4+3],q*6);q++;
        }
        if (q*6>firstIndex) geometry.addGroup(firstIndex,q*6-firstIndex,face);
      });
      geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
      geometry.setAttribute('normal',new THREE.BufferAttribute(normals,3));
      geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));
      geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingSphere();
      const mesh=new THREE.Mesh(geometry,faceMaterials(material));
      mesh.userData.material=material;object.add(mesh);geometries.push(geometry);
    }
    return object;
  }

  const cables = SPECS.map((spec,cableIndex)=>{
    const controls=spec.p.map(point=>new THREE.Vector3(...point));
    const sample=t=>{
      const u=1-t;
      return controls[0].clone().multiplyScalar(u*u*u)
        .addScaledVector(controls[1],3*u*u*t).addScaledVector(controls[2],3*u*t*t)
        .addScaledVector(controls[3],t*t*t);
    };
    const table=Array.from({length:513},(_,i)=>sample(i/512)), distances=[0];
    for (let i=1;i<table.length;i++) distances.push(distances[i-1]+table[i].distanceTo(table[i-1]));
    const total=distances.at(-1), rootLength=20;
    const stops=Array.from({length:17},(_,i)=>i===0 ? 0 : i===16 ? total : rootLength+(total-rootLength)*(i-1)/15);
    const atDistance=s=>{
      let i=1;while (distances[i]<s) i++;
      return table[i-1].clone().lerp(table[i],(s-distances[i-1])/(distances[i]-distances[i-1]));
    };
    const distanceAt=t=>{
      const i=Math.min(511,Math.floor(t*512)),f=t*512-i;
      return distances[i]+(distances[i+1]-distances[i])*f;
    };
    const collars=[.025,.055].map(t=>({start:distanceAt(t),end:distanceAt(t+.018),extra:3,material:1}));
    if (cableIndex!==2) [.87,.905,.94].forEach((t,i)=>collars.push({start:distanceAt(t),end:distanceAt(t+.023),extra:4,material:i===1 ? 2 : 1}));
    const rest=stops.map(atDistance),joints=rest.map(point=>point.clone());
    const links=rest.slice(0,-1).map((point,i)=>{
      const vector=rest[i+1].clone().sub(point),length=vector.length(),unit=vector.normalize();
      const quaternion=new THREE.Quaternion().setFromUnitVectors(up,unit);
      const object=makeSegment(length,spec.r,stops[i],stops[i+1],collars,i===0,cableIndex!==2 && i===15);
      object.name=`cable_${String(cableIndex+1).padStart(2,'0')}_segment_${String(i+1).padStart(2,'0')}`;
      object.userData.modelId='cables';group.add(object);
      return {object,length,unit,quaternion,weight:i===0 ? 0 : (i/15)**1.25};
    });
    const budget=64/links.reduce((sum,link)=>sum+link.length*link.weight,0);
    return {rest,joints,links,budget,radius:spec.r,index:cableIndex};
  });

  function update(time, active) {
    seconds=time;enabled=active;group.visible=active;
    const gain=active ? 1-Math.exp(-time*2) : 0;
    for (const cable of cables) {
      const {rest,joints,links,index,budget}=cable;
      const phase=time*(.65+index*.047)+index*1.71;
      joints[0].copy(rest[0]);
      if (index===2) {
        for (let j=1;j<17;j++) {
          joints[j].copy(rest[j]);
          if (j>1 && j<15) {
            const envelope=Math.sin(Math.PI*(j-1)/14)*gain;
            joints[j].x+=1.8*envelope*Math.sin(phase-j*.36);
            joints[j].z+=2.4*envelope*Math.cos(phase*.83-j*.31);
          }
        }
      }
      links.forEach((link,i)=>{
        const {object,length,quaternion,weight}=link;
        object.position.copy(joints[i]);
        if (index===2) {
          direction.subVectors(joints[i+1],joints[i]).normalize();
          delta.setFromUnitVectors(link.unit,direction);object.quaternion.copy(delta).multiply(quaternion);
        } else {
          const amplitude=budget*weight*gain;
          rotation.set(.6*amplitude*Math.sin(phase-i*.36),0,.4*amplitude*Math.cos(phase*.83-i*.29));
          delta.setFromEuler(rotation);object.quaternion.copy(delta).multiply(quaternion);
          direction.copy(up).applyQuaternion(object.quaternion);
          joints[i+1].copy(joints[i]).addScaledVector(direction,length);
        }
      });
    }
  }

  function state() {
    return {
      enabled,seconds,cableCount:9,segmentCount:144,voxelBlocks,renderedQuads,
      voxelSize:1,firstSegmentFixed:true,fixedController:[0,16,472],fixedTip:[0,32,450],
      maxFreeJointDisplacement:64,maxControlJointDisplacement:3,
      cables:cables.map(cable=>({
        number:cable.index+1,radius:cable.radius,segmentCount:16,
        root:cable.joints[0].toArray(),tip:cable.joints[16].toArray(),
        fixedTip:cable.index===2,
        tipDisplacement:cable.joints[16].distanceTo(cable.rest[16]),
        maxJointDisplacement:Math.max(...cable.joints.map((point,i)=>point.distanceTo(cable.rest[i]))),
        freePlugOuterDisplacementBound:cable.index===2 ? 0 : 64+2*(45+cable.radius)*Math.sin(cable.budget/2),
      })),
    };
  }

  function dispose() {
    geometries.forEach(geometry=>geometry.dispose());ownMaterials.forEach(material=>material.dispose());
    group.removeFromParent();
  }

  update(0,false);
  return {group,update,state,dispose};
}
