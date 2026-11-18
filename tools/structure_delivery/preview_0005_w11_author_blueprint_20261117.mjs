import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117');
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
page.on('pageerror',error=>errors.push(error.message));
page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html');
await page.waitForFunction(()=>window.W11_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:180000});
const loadingError=await page.locator('#loading').allTextContents();
if(loadingError.length)throw new Error(loadingError.join('\n'));
await page.evaluate(()=>{window.W11Viewer.setPaused(true);window.W11Viewer.setTime(4);});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
for(const [model,view,file] of [
  ['all','oblique','整体预览.png'],['all','front','正面预览.png'],['all','top','俯视预览.png'],
  ['puppet','puppet','木偶近景.png'],['puppet','stage','舞台近景.png'],
  ['theater','cabins','机舱近景.png'],['foundation','well','冷却井近景.png'],
  ['puppet','controller','主控近景.png'],['theater','pixels','像素近景.png']]){
  await page.evaluate(({model,view})=>{window.W11Viewer.setModel(model);window.W11Viewer.setView(view);},{model,view});
  await page.screenshot({path:path.join(out,file)});
  captures.push({file,...await page.evaluate(()=>window.W11Viewer.snapshot())});
}
await page.evaluate(()=>{window.W11Viewer.setModel('all');window.W11Viewer.setView('oblique');document.getElementById('roof').checked=false;document.getElementById('roof').dispatchEvent(new Event('change'));});
await page.screenshot({path:path.join(out,'去天幕全景.png')});
captures.push({file:'去天幕全景.png',...await page.evaluate(()=>window.W11Viewer.snapshot())});
await page.evaluate(()=>{document.getElementById('roof').checked=true;document.getElementById('roof').dispatchEvent(new Event('change'));window.W11Viewer.setMode('work');window.W11Viewer.setTime(4);});
await page.screenshot({path:path.join(out,'运行预览.png')});
captures.push({file:'运行预览.png',...await page.evaluate(()=>window.W11Viewer.snapshot())});
await page.evaluate(()=>{window.W11Viewer.setCutaway(true);window.W11Viewer.setView('front');});
await page.screenshot({path:path.join(out,'剧场剖面.png')});
captures.push({file:'剧场剖面.png',...await page.evaluate(()=>window.W11Viewer.snapshot())});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_0005_w11_author_blueprint_20261117.mjs'),path.join(out,'生成脚本/preview_0005_w11_author_blueprint_20261117.mjs'));
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
