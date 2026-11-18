/** 将逐格结构导出为审阅文件；只在专属交付目录写入，不改游戏源码。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createBlueprint} from './i03-fractionation-v1.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'doc/HK3GTL-内测5/03_机器结构/I03分馏中心实物样例_v1');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
await fs.mkdir(out,{recursive:true});
const data=createBlueprint();
await fs.writeFile(path.join(out,'blueprint.json'),JSON.stringify(data),'utf8');
execFileSync(process.execPath,[path.join(skill,'scripts/run-build.mjs'),path.join(root,'tools/structure_delivery/i03-fractionation-v1.mjs'),'--out-dir',out,'--name',data.name,'--no-block-state-updates','--json'],{cwd:skill,stdio:'inherit'});
execFileSync('python',[path.join(root,'tools/structure_delivery/package_i03_review.py')],{cwd:root,stdio:'inherit',env:{...process.env,PYTHONUTF8:'1'}});
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const build=await rolldown({input:path.join(root,'tools/structure_delivery/i03-review-viewer.mjs'),
  resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),
    'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
const bundled=await build.generate({format:'iife',minify:true});
await build.close();
const materials=JSON.parse(await fs.readFile(path.join(out,'materials.json'),'utf8'));
const audit=JSON.parse(await fs.readFile(path.join(out,'audit.json'),'utf8'));
let html=await fs.readFile(path.join(root,'tools/structure_delivery/i03-review-template.html'),'utf8');
html=html.replace('/*__PAYLOAD__*/',()=>`window.REVIEW=${JSON.stringify({data,materials,audit}).replaceAll('<','\\u003c')};`)
  .replace('/*__VIEWER__*/',()=>bundled.output.find(x=>x.type==='chunk').code.replaceAll('</script','<\\/script'));
await fs.writeFile(path.join(out,'I03分馏中心_三维评审.html'),html,'utf8');
const license=await fs.readFile(path.join(skill,'node_modules/three/LICENSE'),'utf8');
await fs.writeFile(path.join(out,'预览依赖许可.txt'),license+'\n本地模组纹理仅用于本项目评审；其权利归原作者。未授权对外分发提取纹理。\n','utf8');
console.log('完成结构与离线三维预览：'+out);
