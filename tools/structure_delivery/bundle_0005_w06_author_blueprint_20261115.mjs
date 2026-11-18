import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/0005_W06_作者蓝图原案_20261115');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const three=path.join(skill,'node_modules/three');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const build=await rolldown({
  input:path.join(root,'tools/structure_delivery/author_w06_viewer_20261115.mjs'),
  resolve:{alias:{
    'three/addons':path.join(three,'examples/jsm'),
    'three':path.join(three,'build/three.module.js'),
  }},
});
const bundle=await build.generate({format:'iife',minify:true});
await build.close();
await fs.writeFile(path.join(out,'viewer.bundle.js'),bundle.output.find(item=>item.type==='chunk').code,'utf8');
console.log(`W06 viewer bundle: ${bundle.output[0].code.length.toLocaleString()} chars`);
