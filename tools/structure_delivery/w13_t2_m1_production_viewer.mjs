import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

async function main(){
const resource='/src/main/resources/assets/hk3gtl/';
const response=await fetch(resource+'models/scene/w13_t2_m1.json.gz');
const model=JSON.parse(await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).text());
model.layers=null;
const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
renderer.setSize(innerWidth,innerHeight);renderer.setClearColor('#17141b');document.body.append(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera(-750*innerWidth/innerHeight,750*innerWidth/innerHeight,750,-750,.1,16000);
const controls=new OrbitControls(camera,renderer.domElement);
const atlas=await new THREE.TextureLoader().loadAsync(resource+'textures/effect/w13_t2_m1_atlas.png');
atlas.magFilter=atlas.minFilter=THREE.NearestFilter;atlas.generateMipmaps=false;atlas.flipY=false;
const uniforms={atlas:{value:atlas},grid:{value:new THREE.Vector2(...model.data.atlas_grid)}};
function material(transparent){return new THREE.ShaderMaterial({uniforms,transparent,depthWrite:!transparent,side:THREE.DoubleSide,
  vertexShader:`attribute float tile;attribute float shade;attribute float alpha;varying float vTile;varying vec2 vUV;varying float vShade;varying float vAlpha;
  void main(){vTile=tile;vUV=uv;vShade=shade;vAlpha=alpha;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform sampler2D atlas;uniform vec2 grid;varying float vTile;varying vec2 vUV;varying float vShade;varying float vAlpha;
  void main(){vec2 cell=vec2(mod(vTile,grid.x),floor(vTile/grid.x));vec2 uv=clamp(vec2(fract(vUV.x),1.-fract(vUV.y)),.001,.999);vec4 color=texture2D(atlas,(cell+uv)/grid);if(color.a<.12)discard;gl_FragColor=vec4(color.rgb*vShade,color.a*vAlpha);}`});}
const opaque=material(false),transparent=material(true),parts=[];
const corners=[[[1,0,0],[1,1,0],[1,1,1],[1,0,1]],[[0,0,1],[0,1,1],[0,1,0],[0,0,0]],[[1,0,1],[1,1,1],[0,1,1],[0,0,1]],[[0,0,0],[0,1,0],[1,1,0],[1,0,0]],[[0,0,1],[0,0,0],[1,0,0],[1,0,1]],[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]];
let quads=0;
for(const part of model.parts){
  const group=new THREE.Group();group.matrixAutoUpdate=false;scene.add(group);
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
  parts.push({group,info:part.metadata,id:part.id});
}
const rig=model.data.rig,vector=p=>new THREE.Vector3(...p),gaze=[[0,0],[.9,.3],[-.55,-.55],[-1,.45],[.35,.85],[1,-.4],[0,0]];
let time=0,working=true,activeView='front',pose;
function setTime(seconds,active=true){
  time=seconds;working=active;
  const step=time/3,index=Math.floor(step)%gaze.length,phase=step-Math.floor(step),blend=Math.max(0,(phase-.4)/.6),ease=blend*blend*(3-2*blend);
  const from=gaze[index],to=gaze[(index+1)%gaze.length],x=(from[0]+(to[0]-from[0])*ease)*16,y=(from[1]+(to[1]-from[1])*ease)*3;
  const eye=new THREE.Matrix4().makeTranslation(.5+x,525.5+y,254.5).multiply(new THREE.Matrix4().makeRotationFromEuler(new THREE.Euler(-y*.02,x*.005625,Math.sin(time*.7)*.012,'XYZ')));
  const gain=1-Math.exp(-time*2),matrices=[],tips=[];
  rig.forEach((cable,c)=>{
    const points=cable.rest.map(vector),p=time*(.65+c*.047)+c*1.71,transforms=[];
    if(c===2)for(let j=2;j<15;j++){const envelope=Math.sin(Math.PI*(j-1)/14)*gain;points[j].x+=1.8*envelope*Math.sin(p-j*.36);points[j].z+=2.4*envelope*Math.cos(p*.83-j*.31);}
    for(let i=0;i<16;i++){
      const base=new THREE.Quaternion(...cable.quaternions[i]);let rotation;
      if(c===2)rotation=new THREE.Quaternion().setFromUnitVectors(vector(cable.units[i]),points[i+1].clone().sub(points[i]).normalize()).multiply(base);
      else{const amplitude=cable.budget*(i===0?0:(i/15)**1.25)*gain;rotation=new THREE.Quaternion().setFromEuler(new THREE.Euler(.6*amplitude*Math.sin(p-i*.36),0,.4*amplitude*Math.cos(p*.83-i*.29),'XYZ')).multiply(base);points[i+1].copy(new THREE.Vector3(0,1,0).applyQuaternion(rotation).multiplyScalar(cable.lengths[i]).add(points[i]));}
      transforms.push(new THREE.Matrix4().compose(points[i],rotation,new THREE.Vector3(1,1,1)));
    }
    matrices.push(transforms);tips.push(points[16].toArray());
  });
  for(const part of parts){const m=part.info;part.group.visible=(m.mode===0||(active?m.mode>=2:m.mode===1))&&(activeView!=='cables'||m.mode===4||m.mode===1&&part.id.startsWith('cable_'));part.group.matrix.fromArray(m.rest_matrix);if(m.mode===3)part.group.matrix.copy(eye);if(m.mode===4)part.group.matrix.copy(matrices[m.cable][m.segment]);}
  pose={eye:{offset:[x,y,0],angles:[-y*.02,x*.005625,Math.sin(time*.7)*.012]},cableTips:tips};draw();
}
const views={front:{center:[-20,80,-27],direction:[-.8,.4,1.35],half:[650,650,560]},eye:{center:[0,525,250],direction:[.05,.03,1],half:[96,65,25]},cables:{center:[0,215,30],direction:[-.3,.42,1],half:[565,230,500]},controller:{center:[0,47,448],direction:[-.7,.35,1],half:[65,55,65]}};
function draw(){renderer.render(scene,camera);}
function setView(name){activeView=name;const v=views[name],center=vector(v.center);controls.target.copy(center);camera.position.copy(center.clone().add(vector(v.direction).normalize().multiplyScalar(3000)));camera.zoom=1;camera.updateProjectionMatrix();controls.update();camera.updateMatrixWorld();let limit=0;for(const x of [-1,1])for(const y of [-1,1])for(const z of [-1,1]){const p=center.clone().add(vector([x*v.half[0],y*v.half[1],z*v.half[2]])).project(camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}camera.zoom=.9/limit;camera.updateProjectionMatrix();setTime(time,working);}
controls.addEventListener('change',draw);window.ProductionViewer={setTime,setView,snapshot:()=>({time,working,view:activeView,parts:parts.length,quads,materials:model.materials.length,pose,drawCalls:renderer.info.render.calls})};
document.getElementById('loading').remove();setView('front');setTime(0);window.PRODUCTION_READY=true;
}
main().catch(error=>{console.error(error);document.getElementById('loading').textContent=error.message;});
