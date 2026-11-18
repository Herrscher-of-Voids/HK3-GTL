/** 无损提取已确认V1树影曲线，游戏只加载紧凑几何，不包含浏览器或Three运行库。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

const root=path.resolve(import.meta.dirname,'../..');
const THREE=await import(pathToFileURL(path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill/node_modules/three/build/three.module.js')));
const source=await fs.readFile(path.join(import.meta.dirname,'i34_tree_projection_scene_20261027.mjs'),'utf8');
const geometry=source.slice(source.indexOf('const V='),source.indexOf('const geometry='));
const data=new Function('THREE',geometry+`;return {positions,colors,curves,tips,dust,dustSizes,dustSeeds,random,range,spine};`)(THREE);
const nodes=[],nodeSizes=[],nodeSeeds=[];
for(let i=0;i<data.tips.length;i++)if(i%3===0){nodes.push(...data.tips[i].toArray());nodeSizes.push(data.range(5,8));nodeSeeds.push(data.random()*6.28);}
const flows=Array.from({length:720},()=>({branch:data.curves[Math.floor(data.random()*data.curves.length)],offset:data.random(),speed:data.range(.035,.1)}));
const flowSizes=flows.map(()=>data.range(1.5,3.4)),flowSeeds=flows.map(()=>data.random()*6.28);
const chunks=[];function int(n){const b=Buffer.alloc(4);b.writeInt32BE(n);chunks.push(b);}
function floats(values){const b=Buffer.alloc(values.length*4);values.forEach((v,i)=>{if(!Number.isFinite(v))throw Error('树影坐标不是有限数');b.writeFloatBE(v,i*4);});chunks.push(b);}
int(0x49333454);int(1);int(data.positions.length/3);floats(data.positions);floats(data.colors);
const points=[];
function append(pos,sizes,seeds,type){for(let i=0;i<sizes.length;i++)points.push(...pos.slice(i*3,i*3+3),sizes[i],seeds[i],type);}
append(data.dust,data.dustSizes,data.dustSeeds,0);append(nodes,nodeSizes,nodeSeeds,1);
for(let i=0;i<9;i++)points.push(...data.spine.getPoint(i/9).toArray(),19-i*.6,i,2);
int(points.length/6);floats(points);int(flows.length);int(65);
for(let i=0;i<flows.length;i++){const f=flows[i];floats([f.offset,f.speed,flowSizes[i],flowSeeds[i]]);for(let k=0;k<=64;k++)floats(f.branch.curve.getPoint(k/64).toArray());}
if(data.positions.length/3!==71948||data.curves.length!==1677||data.tips.length!==816||data.dustSizes.length!==15286)throw Error('已确认V1树影几何发生变化');
const output=path.join(root,'src/main/resources/assets/hk3gtl/effects/i34_tree.bin.gz');await fs.mkdir(path.dirname(output),{recursive:true});
const packed=zlib.gzipSync(Buffer.concat(chunks),{level:9});await fs.writeFile(output,packed);
const log=path.join(root,'logs/i34-native-fx-r234-20261109');await fs.mkdir(log,{recursive:true});
const receipt={source:'I34_虚数之树_动态投影研究_V1_20261027',source_script_sha256:crypto.createHash('sha256').update(source).digest('hex'),vertices:71948,curves:1677,tips:816,dust:15286,points:points.length/6,flows:720,flow_samples:65,projection_source_position:[240,92,167],scale:.9,bytes:packed.length,sha256:crypto.createHash('sha256').update(packed).digest('hex'),world_blocks_added:0,game_verified:false};
await fs.writeFile(path.join(log,'export.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
