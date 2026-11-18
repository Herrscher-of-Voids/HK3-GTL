import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
const resource='/src/main/resources/assets/hk3gtl/';
const response=await fetch(resource+'models/scene/w11_f5.json.gz');
const model=JSON.parse(await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).text());
model.layers=null;
const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
renderer.setSize(innerWidth,innerHeight);renderer.setClearColor('#151922');document.body.append(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,1,16000);
const controls=new OrbitControls(camera,renderer.domElement);
const atlas=await new THREE.TextureLoader().loadAsync(resource+'textures/effect/w11_f5_atlas.png');
atlas.magFilter=atlas.minFilter=THREE.NearestFilter;atlas.generateMipmaps=false;atlas.flipY=false;
const uniforms={atlas:{value:atlas},grid:{value:new THREE.Vector2(...model.data.atlas_grid)}};
function material(transparent){return new THREE.ShaderMaterial({uniforms,transparent,depthWrite:!transparent,side:THREE.DoubleSide,
  vertexShader:`attribute float tile;attribute float shade;attribute float alpha;varying float vTile;varying vec2 vUV;varying float vShade;varying float vAlpha;
  void main(){vTile=tile;vUV=uv;vShade=shade;vAlpha=alpha;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform sampler2D atlas;uniform vec2 grid;varying float vTile;varying vec2 vUV;varying float vShade;varying float vAlpha;
  void main(){vec2 cell=vec2(mod(vTile,grid.x),floor(vTile/grid.x));vec2 uv=clamp(vec2(fract(vUV.x),1.-fract(vUV.y)),.001,.999);vec4 color=texture2D(atlas,(cell+uv)/grid);if(color.a<.12)discard;gl_FragColor=vec4(color.rgb*vShade,color.a*vAlpha);}`});}
const opaque=material(false),transparent=material(true),parts=[],bones=new Map();
const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
let quads=0;
for(const part of model.parts){
  const group=new THREE.Group();group.matrixAutoUpdate=false;scene.add(group);
  const info=part.metadata;
  if(info.dynamic)bones.set(info.actor+'/'+info.bone,info);
  for(const blend of [false,true]){
    let count=0;for(let m=0;m<model.materials.length;m++)if(model.materials[m].transparent===blend)for(let f=0;f<6;f++)count+=part.starts[m][f].length;
    if(!count)continue;
    const positions=new Float32Array(count*12),uv=new Float32Array(count*8),tile=new Float32Array(count*4),shade=new Float32Array(count*4),alpha=new Float32Array(count*4),index=new Uint32Array(count*6);
    const [w,,d]=part.size;let q=0;
    for(let m=0;m<model.materials.length;m++)if(model.materials[m].transparent===blend)for(let f=0;f<6;f++){
      const starts=part.starts[m][f],lengths=part.lengths[m][f],spans=part.spans[m][f],axis=f<2?2:0,cross=f<4?1:2;
      for(let i=0;i<starts.length;i++){
        const at=starts[i],start=[at%w,Math.floor(at/(w*d)),Math.floor(at/w)%d];
        for(let v=0;v<4;v++){
          const c=corners[f][v];for(let k=0;k<3;k++)positions[q*12+v*3+k]=part.origin[k]+start[k]+c[k]*(k===axis?lengths[i]:k===cross?spans[i]:1);
          uv[q*8+v*2]=c[axis]*lengths[i];uv[q*8+v*2+1]=c[cross]*spans[i];tile[q*4+v]=m*6+f;
          shade[q*4+v]=model.materials[m].emissive?1.15:f===5?1:f===4?155/255:f<2?205/255:230/255;alpha[q*4+v]=blend?148/255:1;
        }
        index.set([q*4,q*4+1,q*4+2,q*4,q*4+2,q*4+3],q*6);q++;
      }
    }
    const geometry=new THREE.BufferGeometry();
    for(const [name,data,size] of [['position',positions,3],['uv',uv,2],['tile',tile,1],['shade',shade,1],['alpha',alpha,1]])geometry.setAttribute(name,new THREE.BufferAttribute(data,size));
    geometry.setIndex(new THREE.BufferAttribute(index,1));geometry.computeBoundingSphere();group.add(new THREE.Mesh(geometry,blend?transparent:opaque));quads+=count;
  }
  parts.push({group,info,inverse:info.dynamic?new THREE.Matrix4().fromArray(info.rest_matrix).invert():null});
}
const rig=model.data.rig,scale=rig.voxel_scale??1,vector=p=>new THREE.Vector3(...p),rotate=angles=>new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(...angles,'XYZ'));
function motion(t,i){const phase=t*.72+i*Math.PI;return {phase,pull:Math.sin(phase),roll:Math.sin(phase+.5),sway:Math.sin(phase*.73+.2),forward:Math.sin(phase*.85-.4),twist:Math.sin(phase*.5+.3)};}
function root(actor,t){
  const p=vector(rig.actor_root[actor]),matrix=new THREE.Matrix4().makeTranslation(...p.toArray());if(actor==='dominion')return matrix;
  const a=motion(t-.18,actor==='puppet_l'?0:1),pose=rig.poses.find(pose=>pose.actor===actor),r=pose.angles_degrees.root.map(v=>v*Math.PI/180);
  return matrix.multiply(new THREE.Matrix4().makeTranslation(a.sway*12,a.pull*10,a.forward*14)).multiply(rotate([r[0]+a.forward*.035,r[1]+a.twist*.05,r[2]+a.sway*.03]));
}
function bone(key,t,world){
  if(world.has(key))return world.get(key);
  const m=bones.get(key),p=vector(m.pivot),r=[...m.base_rotation];let parent;
  if(m.parent==='root')parent=root(m.actor,t);else{const k=m.actor+'/'+m.parent;p.sub(vector(bones.get(k).pivot));parent=bone(k,t,world);}
  if(m.actor==='dominion'){
    const side=m.bone==='floating_hand_f03'?0:1,a=motion(t,side);p.add(vector([a.sway*8,a.pull*12,a.forward*10]));r[0]+=a.forward*.065;r[1]+=a.twist*.055;r[2]+=(side===0?-1:1)*a.roll*.07;
  }else{
    const side=m.actor==='puppet_l'?0:1,a=motion(t-.18,side),id=m.bone;
    if(id==='body'){r[0]+=a.forward*.03;r[1]+=a.twist*.08;r[2]-=a.sway*.025;}
    if(id==='head'){r[0]+=a.pull*.03;r[1]+=a.twist*.035;r[2]+=a.roll*(side===0?.05:.025);}
    if(id.endsWith('_l')||id.endsWith('_r')){
      const direction=id.endsWith('_l')?1:-1,knee=Math.sin(a.phase+(direction===1?0:Math.PI));
      if(id.startsWith('arm_')){r[0]+=a.forward*.04;r[2]+=a.roll*.04;}
      if(id.startsWith('forearm_')){r[0]+=a.pull*.035;r[2]+=direction*a.roll*.03;}
      if(id.startsWith('hand_')){r[0]+=a.roll*.06;r[1]+=a.twist*.04;}
      if(id.startsWith('thigh_')){r[0]+=knee*.06;r[2]+=direction*a.sway*.018;}
      if(id.startsWith('shin_'))r[0]+=knee*.08;
      if(id.startsWith('foot_'))r[0]-=.04+knee*.03;
    }
  }
  const matrix=parent.clone().multiply(new THREE.Matrix4().makeTranslation(...p.toArray())).multiply(rotate(r));world.set(key,matrix);return matrix;
}
const lineGeometry=new THREE.BufferGeometry(),linePositions=new Float32Array(60);lineGeometry.setAttribute('position',new THREE.BufferAttribute(linePositions,3));
scene.add(new THREE.LineSegments(lineGeometry,new THREE.LineBasicMaterial({color:0xffd781,transparent:true,opacity:.85,depthWrite:false})));
function setTime(t){
  const world=new Map();for(const {group,info:m,inverse} of parts)if(m.dynamic){
    group.matrix.copy(bone(m.actor+'/'+m.bone,t,world)).multiply(new THREE.Matrix4().makeTranslation(-m.pivot[0],-m.pivot[1],-m.pivot[2])).multiply(inverse);
    for(const i of [12,13,14])group.matrix.elements[i]*=scale;
  }
  let n=0;for(const actor of ['puppet_l','puppet_r']){
    const hand=rig.hands[actor],key='dominion/'+hand.part,top=bone(key,t,world),pivot=vector(bones.get(key).pivot),tips=[...hand.points].sort((a,b)=>a[0]-b[0]),targets=[...rig.puppet_targets].sort((a,b)=>a.point[0]-b.point[0]);
    for(let i=0;i<5;i++){
      linePositions.set(vector(tips[i]).sub(pivot).applyMatrix4(top).toArray(),n);n+=3;
      const target=targets[i],k=actor+'/'+target.part;linePositions.set(vector(target.point).sub(vector(bones.get(k).pivot)).applyMatrix4(bone(k,t,world)).toArray(),n);n+=3;
    }
  }
  for(let i=0;i<n;i++)linePositions[i]*=scale;
  lineGeometry.attributes.position.needsUpdate=true;draw();
}
const views={front:{center:[0,620,-250],direction:[0,.05,1],half:[880,660,820],distance:4700},wallLeft:{center:[-485,680,140],direction:[-.75,.3,1],half:[180,150,190],distance:1800},wallRight:{center:[485,680,140],direction:[.75,.3,1],half:[180,150,190],distance:1800},puppets:{center:[0,165,230],direction:[0,.04,1],half:[315,150,90],distance:1700},palms:{center:[0,800,80],direction:[-.24,.65,1],half:[480,105,300],distance:2200}};
for(const view of Object.values(views)){view.center=view.center.map(n=>n*scale);view.half=view.half.map(n=>n*scale);view.distance*=scale;}
function draw(){renderer.render(scene,camera);}
function setView(name){const v=views[name],center=vector(v.center);controls.target.copy(center);camera.position.copy(center.clone().add(vector(v.direction).normalize().multiplyScalar(v.distance)));camera.zoom=1;camera.updateProjectionMatrix();controls.update();camera.updateMatrixWorld();let limit=0;for(const x of [-1,1])for(const y of [-1,1])for(const z of [-1,1]){const p=center.clone().add(vector([x*v.half[0],y*v.half[1],z*v.half[2]])).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}camera.zoom=.9/limit;camera.updateProjectionMatrix();draw();}
controls.addEventListener('change',draw);window.ProductionViewer={setTime,setView,snapshot:()=>({parts:parts.length,quads,materials:model.materials.length,drawCalls:renderer.info.render.calls})};
document.getElementById('loading').remove();setView('front');setTime(0);window.PRODUCTION_READY=true;
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=error.message;});
