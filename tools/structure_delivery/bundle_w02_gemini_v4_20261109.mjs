/** 复用本机Three与Rolldown，不新增依赖。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const out=path.join(root,'deliveries/W02_Gemini_半构造星核船坞_V4_20261109');
const source=path.join(root,'tools/structure_delivery/w02_gemini_viewer_v4_20261109.mjs');
const build=await rolldown({input:source,resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await build.write({file:path.join(out,'w02/viewer.bundle.js'),format:'iife',minify:true});await build.close();
for(const name of ['w02_gemini_viewer_v4_20261109.mjs','bundle_w02_gemini_v4_20261109.mjs'])
  await fs.copyFile(path.join(root,'tools/structure_delivery',name),path.join(out,'生成脚本',name));
console.log('W02 V4预览已打包。');
