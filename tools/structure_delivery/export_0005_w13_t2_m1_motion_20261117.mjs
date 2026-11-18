import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createEyeMotion} from './w13_tv_eye_motion_20261117.mjs';
import {createCableMotion} from './w13_tv_cable_motion_20261117.mjs';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const source=path.join(root,'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117');
const target=path.join(root,'logs/0005-w13-t2-production-20261117');
const THREE=await import(pathToFileURL('C:/Users/OWNER/.codex/skills/minecraft-builder-skill/node_modules/three/build/three.module.js'));
const body=await fs.readFile(path.join(source,'data.js'),'utf8');
const payload=JSON.parse(gunzipSync(Buffer.from(body.slice(body.indexOf('"')+1,body.lastIndexOf('"')),'base64')));
const motion=JSON.parse(await fs.readFile(path.join(source,'motion.json'),'utf8'));
const textures=payload.materials.map(()=>Object.fromEntries(['east','west','south','north','down','up'].map(face=>[face,new THREE.Texture()])));
const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),10000);
const eye=createEyeMotion(THREE,payload.materials,textures,plane),cables=createCableMotion(THREE,payload.materials,textures,plane);
eye.update(0,false);cables.update(0,false);eye.group.updateMatrixWorld(true);cables.group.updateMatrixWorld(true);
const normals=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[0,-1,0],[0,1,0]];
const identity=new THREE.Matrix4().toArray(),dynamic=[];
function pack(id,rows,metadata){
  const low=[0,1,2].map(axis=>Math.min(...rows.map(r=>r[axis+2])));
  const high=[...low];
  for(const row of rows){const axis=row[1]<2?2:0,cross=row[1]<4?1:2;for(let k=0;k<3;k++)high[k]=Math.max(high[k],row[k+2]+(k===axis?row[5]:k===cross?row[6]:1));}
  const size=high.map((v,i)=>Math.round(v-low[i]));
  const starts=payload.materials.map(()=>Array.from({length:6},()=>[])),lengths=payload.materials.map(()=>Array.from({length:6},()=>[])),spans=payload.materials.map(()=>Array.from({length:6},()=>[]));
  for(const [material,face,x,y,z,w,h] of rows){starts[material][face].push(Math.round(((y-low[1])*size[2]+z-low[2])*size[0]+x-low[0]));lengths[material][face].push(w);spans[material][face].push(h);}
  return {id,origin:low,size,starts,lengths,spans,metadata};
}
const eyeRows=[],matrix=new THREE.Matrix4();
for(const mesh of eye.group.children)for(let i=0;i<mesh.count;i++){
  mesh.getMatrixAt(i,matrix);const v=new THREE.Vector3().setFromMatrixPosition(matrix);
  for(let face=0;face<6;face++)eyeRows.push([mesh.userData.material,face,v.x-.5,v.y-.5,v.z-.5,1,1]);
}
dynamic.push(pack('moving_eye',eyeRows,{mode:3,cable:-1,segment:-1,rest_matrix:eye.group.matrixWorld.toArray()}));
const rig=[];
for(let cable=0;cable<9;cable++){
  const objects=cables.group.children.slice(cable*16,cable*16+16),rest=objects.map(object=>object.position.toArray());
  rest.push(cables.state().cables[cable].tip);
  const lengths=objects.map((_,i)=>new THREE.Vector3(...rest[i]).distanceTo(new THREE.Vector3(...rest[i+1])));
  rig.push({rest,lengths,units:objects.map((_,i)=>new THREE.Vector3(...rest[i+1]).sub(new THREE.Vector3(...rest[i])).normalize().toArray()),quaternions:objects.map(object=>object.quaternion.toArray()),budget:64/lengths.reduce((sum,length,i)=>sum+length*(i===0?0:(i/15)**1.25),0)});
  for(let segment=0;segment<16;segment++){
    const object=objects[segment],rows=[];
    for(const mesh of object.children){
      const positions=mesh.geometry.getAttribute('position');
      for(const group of mesh.geometry.groups){
        const face=group.materialIndex,normal=normals[face],axis=face<2?2:0,cross=face<4?1:2;
        for(let q=group.start/6;q<(group.start+group.count)/6;q++){
          const points=Array.from({length:4},(_,i)=>[positions.getX(q*4+i),positions.getY(q*4+i),positions.getZ(q*4+i)]);
          const min=[0,1,2].map(k=>Math.min(...points.map(v=>v[k]))),max=[0,1,2].map(k=>Math.max(...points.map(v=>v[k])));
          const base=min.map((v,k)=>v-Math.max(0,normal[k]));rows.push([mesh.userData.material,face,...base,max[axis]-min[axis],max[cross]-min[cross]]);
        }
      }
    }
    dynamic.push(pack(object.name,rows,{mode:4,cable,segment,rest_matrix:object.matrixWorld.toArray()}));
  }
}
for(const part of payload.parts)part.metadata={mode:part.id==='eye_display'||/^cable_\d{2}_[12]$/.test(part.id)?1:0,cable:-1,segment:-1,rest_matrix:identity};
motion.screen.metadata={mode:2,cable:-1,segment:-1,rest_matrix:identity};
payload.parts.push(motion.screen,...dynamic);
payload.data.rig=rig;
await fs.mkdir(target,{recursive:true});
await fs.writeFile(path.join(target,'client-surfaces.json.gz'),gzipSync(JSON.stringify(payload),{level:6}));
await fs.writeFile(path.join(target,'client-motion.json'),JSON.stringify({eye:eye.state(),cables:cables.state(),dynamicParts:dynamic.length,rig}));
eye.dispose();cables.dispose();
console.log(JSON.stringify({parts:payload.parts.length,dynamicParts:dynamic.length,eye:eyeRows.length/6}));
