import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_W09_T9与S1融合摆位_F1_20261117');
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
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html');
await page.waitForFunction(()=>window.TAIXUAN_READY,{},{timeout:180000});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
const links=await page.locator('a[href]').evaluateAll(items=>items.map(a=>({text:a.textContent,href:a.getAttribute('href')})));
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
for(const view of ['oblique','front','back','top','weapons','entry','court','controller','creek']){
  await page.evaluate(name=>window.TaixuanViewer.setView(name),view);
  const file='all-'+view+'.png';
  await page.screenshot({path:path.join(out,file)});
  captures.push({file,...await page.evaluate(()=>window.TaixuanViewer.snapshot())});
}
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,failed,links,captures},null,2)+'\n');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_w09_fusion_20261117.mjs'),path.join(out,'生成脚本/preview_w09_fusion_20261117.mjs'));
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors,failed,links}));
