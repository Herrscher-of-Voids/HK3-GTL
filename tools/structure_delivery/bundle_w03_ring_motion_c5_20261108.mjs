/** 使用已有Three依赖打包C5，不引入新模组或网络资源。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const skill = path.join(process.env.USERPROFILE, '.codex/skills/minecraft-builder-skill');
const {rolldown} = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));
const source = path.join(root, 'tools/structure_delivery/w03_ring_motion_c5_20261108.mjs');
const out = path.join(root, 'deliveries/W03_C5_四环绕核运动_20261108');
const build = await rolldown({input:source, resolve:{alias:{three:path.join(skill, 'node_modules/three/build/three.module.js')}}});
await build.write({file:path.join(out, 'w03/motion.bundle.js'), format:'iife', minify:true});
await build.close();
for (const name of ['w03_ring_motion_c5_20261108.mjs', 'bundle_w03_ring_motion_c5_20261108.mjs'])
  await fs.copyFile(path.join(root, 'tools/structure_delivery', name), path.join(out, '生成脚本', name));
console.log('C5动态脚本已打包');
