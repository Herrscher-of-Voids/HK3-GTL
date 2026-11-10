/** 生成可双击打开、无网络依赖的I34投影效果HTML。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import crypto from 'node:crypto';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.join(root,'deliveries/I34_虚数之树_动态投影研究_V1_20261027');
const directory=path.dirname(fileURLToPath(import.meta.url));
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const three=path.join(skill,'node_modules/three');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const alias={three:path.join(three,'build/three.module.js')};
for(const [key,file] of Object.entries({'orbit-controls':'controls/OrbitControls.js','effect-composer':'postprocessing/EffectComposer.js',
 'render-pass':'postprocessing/RenderPass.js','bloom-pass':'postprocessing/UnrealBloomPass.js','output-pass':'postprocessing/OutputPass.js'}))alias[key]=path.join(three,'examples/jsm',file);
const compiled=await rolldown({input:path.join(directory,'i34_tree_projection_scene_20261027.mjs'),resolve:{alias}});
const bundle=await compiled.generate({format:'iife',minify:true});await compiled.close();
const script=bundle.output.find(part=>part.type==='chunk').code;
if(/<\/script/i.test(script))throw new Error('内嵌脚本包含意外结束标签');
const template=await fs.readFile(path.join(directory,'i34_tree_projection_page_20261027.html'),'utf8');
if(!template.includes('/*__PROJECTION_BUNDLE__*/'))throw new Error('HTML缺少脚本占位符');
const html=template.replace('/*__PROJECTION_BUNDLE__*/',()=>script);
await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,'index.html'),html,'utf8');
await fs.copyFile(path.join(three,'LICENSE'),path.join(output,'Three许可.txt'));
const source=path.join(output,'生成脚本');await fs.mkdir(source,{recursive:true});
for(const name of ['i34_tree_projection_scene_20261027.mjs','i34_tree_projection_page_20261027.html','build_i34_tree_projection_20261027.mjs'])await fs.copyFile(path.join(directory,name),path.join(source,name));
const manifest={title:'I34虚数之树观测投影',version:'V1',scope:'独立HTML动态效果研究；未改造建筑或接入游戏。',
 generated_at:new Date().toISOString(),approved:false,installed:false,self_contained:true,network_required:false,
 html_bytes:Buffer.byteLength(html),sha256:crypto.createHash('sha256').update(html).digest('hex')};
await fs.writeFile(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2),'utf8');
console.log(JSON.stringify({output,...manifest}));
