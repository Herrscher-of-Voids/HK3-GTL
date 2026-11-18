import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W06-W15_完整静态蓝图_A1_20261113');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'w06/生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),
  three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
const target=path.join(out,'w06/viewer.bundle.js');
await bundle.write({file:target,format:'iife',minify:true});
await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
page.on('pageerror',error=>process.stderr.write(error.message+'\n'));
const rows=[];
const selected=new Set(process.argv.slice(2).map(role=>role.toLowerCase()));
for(let n=6;n<=15;n++){
  const role='w'+String(n).padStart(2,'0'),folder=path.join(out,role);
  const data=JSON.parse(await fs.readFile(path.join(folder,'manifest.json'),'utf8'));
  rows.push({role:role.toUpperCase(),title:data.title,size:data.size,blocks:data.blocks});
  if(selected.size&&!selected.has(role))continue;
  if(n!==6)await fs.copyFile(target,path.join(folder,'viewer.bundle.js'));
  await page.goto(pathToFileURL(path.join(folder,'index.html')).href);
  await page.waitForFunction(()=>window.W05_STATIC_READY);
  for(const [view,name] of [['front','全景'],['orthofront','正面'],['top','俯视']]){
    await page.evaluate(view=>{window.__hk3Preview.setView(view);window.__hk3Preview.draw();},view);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await page.locator('#stage').screenshot({path:path.join(folder,name+'.png')});
  }
  process.stdout.write(role+' rendered\n');
}
await browser.close();
const cards=rows.map(row=>`<article><a href="${row.role.toLowerCase()}/index.html"><img src="${row.role.toLowerCase()}/全景.png" alt="${row.title}"><h2>${row.role} ${row.title}</h2></a><p>宽${row.size[0]} × 深${row.size[2]} × 高${row.size[1]} · ${row.blocks.toLocaleString('en-US')}块</p><p>完整NBT/Schematic · 静态 · 外观待评审</p></article>`).join('');
await fs.writeFile(path.join(out,'index.html'),`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W06–W15完整静态蓝图候选A1</title><style>body{max-width:1500px;margin:32px auto;padding:0 24px;background:#101923;color:#e5edf5;font:16px/1.8 system-ui}a{color:#b9dcfa}main{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{background:#192737;padding:16px}img{width:100%;display:block}h2{font-size:20px}.note{padding:18px;border-left:3px solid #d9bc71;background:#26313c}@media(max-width:850px){main{display:block}article{margin-bottom:20px}}</style><h1>十座奇观 · 完整静态蓝图 A1</h1><p class="note">W06–W14按既定工艺分区生成本轮原创几何；W15将原方案体量逐格展开，撤销旧固定接口标记。先完整生成再计算实际包围盒，使用现存方块与真实纹理；主控位置用红石块明确标记。全部为独立候选，未批准、未接正式Pattern、未安装，未进行游戏搭建、成型或运行验收。</p><p><a href="../../logs/beta5-completion-audit-20261030/index.html">固定完成度审计</a></p><main>${cards}</main></html>`,'utf8');
