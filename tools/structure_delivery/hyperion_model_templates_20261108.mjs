/** 以真实原版模型生成保留旋转、半砖、门及玻璃板的几何模板。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const log=path.join(root,'logs/hyperion-modern-preview-20261108');
const lib=await import(pathToFileURL('C:/Users/OWNER/.codex/skills/minecraft-builder-skill/node_modules/@mattzh72/lodestone/lib/index.js'));
const {BlockDefinition,BlockModel,BlockState,Cull,SpecialRenderers}=lib;
const input=JSON.parse(await fs.readFile(path.join(log,'model-inputs.json'),'utf8'));
const models=new Map(Object.entries(input.models).map(([name,raw])=>[name,BlockModel.fromJson(raw)]));
const textureNames=[],textureIds=new Map();
const atlas={getPixelSize:()=>1/1024,getTextureUV(id){const name=id.toString();if(!textureIds.has(name)){textureIds.set(name,textureNames.length);textureNames.push(name);}const n=textureIds.get(name);return[n*4,0,n*4+1,1];}};
const provider={getBlockModel:id=>{const model=models.get(id.toString());if(!model)throw Error('缺失模型：'+id);return model;}};
const templates=[{name:'minecraft:air',cube:false,quads:[]}];
for(const s of input.palette.slice(1)){
 const state=s.name+(Object.keys(s.properties).length?'['+Object.entries(s.properties).sort().map(([k,v])=>k+'='+v).join(',')+']':'');
 const block=new BlockState(s.name,s.properties),definition=BlockDefinition.fromJson(input.definitions[s.name]);
 const mesh=definition.getMesh(block.getName(),s.properties,atlas,provider,Cull.none());
 mesh.merge(SpecialRenderers.getBlockMesh(block,undefined,atlas,Cull.none()));
 if(!mesh.quads.length)throw Error('模型没有几何：'+state);
 const quads=mesh.quads.map(q=>{
  const vertices=q.vertices(),slot=Math.floor(Math.min(...vertices.map(v=>v.texture[0]))/4+.00001);
  const positions=vertices.flatMap(v=>[v.pos.x,v.pos.y,v.pos.z].map(n=>Math.abs(n)<1e-7?0:Math.abs(n-1)<1e-7?1:n));
  const uv=vertices.flatMap(v=>[v.texture[0]-slot*4,1-v.texture[1]]);
  if(uv.some(n=>!Number.isFinite(n))||!textureNames[slot])throw Error('纹理坐标错误：'+state);
  const axis=[0,1,2].find(a=>vertices.every(v=>Math.abs([v.pos.x,v.pos.y,v.pos.z][a]-[vertices[0].pos.x,vertices[0].pos.y,vertices[0].pos.z][a])<1e-5));
  const constant=axis===undefined?undefined:positions[axis];
  const face=axis===0?(constant===1?0:constant===0?1:-1):axis===2?(constant===1?2:constant===0?3:-1):axis===1?(constant===0?4:constant===1?5:-1):-1;
  return{p:positions,uv,texture:textureNames[slot],face};
 });
 const cube=!Object.keys(s.properties).length&&quads.length===6&&new Set(quads.map(q=>q.face)).size===6&&quads.every(q=>q.face>=0&&q.p.every(n=>n===0||n===1));
 templates.push({name:s.name,properties:s.properties,state,cube,glass:s.name.includes('glass')||s.name.endsWith(':beacon'),quads});
}
await fs.writeFile(path.join(log,'model-templates.json'),JSON.stringify(templates));
console.log(JSON.stringify({states:templates.length-1,cube_states:templates.filter(s=>s.cube).length,textures:textureNames.length,non_empty:templates.slice(1).every(s=>s.quads.length)}));
