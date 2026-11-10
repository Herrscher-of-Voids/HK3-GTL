/** 打包纯静态查看器，不引入演出调度。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const out=path.join(root,'deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const build=await rolldown({input:path.join(out,'生成脚本/w02_static_viewer_v4s_20261109.mjs'),
  resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await build.write({file:path.join(out,'w02/viewer.bundle.js'),format:'iife',minify:true});await build.close();
await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
console.log('W02 V4S纯静态查看器已打包。');
