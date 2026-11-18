import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_W09_识律武器细节复刻_S2_20261116');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),
  three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1100},deviceScaleFactor:1});
const errors=[],failed=[],captures=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
const url='http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html';
await page.goto(url);
await page.waitForFunction(()=>window.SENTI_READY);
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
for(const [model,views] of [
  ['all',['front','oblique']],
  ['case',['front','back','right','oblique','taiji','rim']],
  ['sword',['front','oblique','guard','grip']],
  ['spear',['front','oblique','head','shaft']],
  ['chain',['front','back','oblique','chain_links','chain_grip']]
]){
  await page.evaluate(id=>window.SentiViewer.setModel(id),model);
  for(const view of views){
    await page.evaluate(name=>window.SentiViewer.setView(name),view);
    const filename=model+'-'+view+'.png';
    await page.screenshot({path:path.join(out,filename)});
    captures.push({file:filename,...await page.evaluate(()=>window.SentiViewer.snapshot())});
  }
}
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({url,captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
