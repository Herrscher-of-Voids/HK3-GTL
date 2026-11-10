/** 使用既有Three依赖离线打包预览效果，运行时不请求外网。 */
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(root,'tools/structure_delivery/w03_gork_review_v7_20261108.mjs'),
  resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(root,'deliveries/W03_穹界虚数锚定环_四锚穹盖_Gork原案_V7_20261108/w03/gork-review.bundle.js'),format:'iife',minify:true});
await bundle.close();
