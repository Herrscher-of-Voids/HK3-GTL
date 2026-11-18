import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_支配剧场_细节精修_T2_20261117');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],captures=[];
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html');
await page.waitForFunction(()=>window.THEATRE_READY,{},{timeout:120000});
await settle();
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
await page.evaluate(()=>window.TheatreViewer.setShellMode('full'));
await settle();
await page.screenshot({path:path.join(out,'完整外观.png')});
captures.push({file:'完整外观.png',group:'完整外观',viewport:page.viewportSize(),...await page.evaluate(()=>window.TheatreViewer.snapshot())});
await page.evaluate(()=>window.TheatreViewer.setShellMode('cutaway'));
for(const [view,file] of [['oblique','整体斜视.png'],['front','整体正面.png'],['back','背面.png'],['top','俯视.png']]){
  await page.evaluate(view=>{window.TheatreViewer.setModel('all');window.TheatreViewer.setView(view);},view);
  await settle();
  await page.screenshot({path:path.join(out,file)});
  captures.push({file,group:'模型全貌',viewport:page.viewportSize(),...await page.evaluate(()=>window.TheatreViewer.snapshot())});
}
await page.setViewportSize({width:2400,height:1600});
await settle();
const views=await page.evaluate(()=>Object.fromEntries(Object.entries(window.TheatreViewer.views).map(([key,value])=>[key,value.label])));
for(const [view,label] of Object.entries(views).filter(([key])=>!['oblique','front','back','top'].includes(key))){
  await page.evaluate(view=>{window.TheatreViewer.setModel(view==='ceiling'?'roof':'all');window.TheatreViewer.setView(view);},view);
  await settle();
  const file=label+'.png';
  await page.screenshot({path:path.join(out,file)});
  captures.push({file,group:'局部细节',viewport:page.viewportSize(),...await page.evaluate(()=>window.TheatreViewer.snapshot())});
}
const record={captured_at:new Date().toISOString(),errors,captures};
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify(record,null,2)+'\n');
await fs.writeFile(path.join(root,'logs/0005-theatre-t2-20261117/preview.json'),JSON.stringify(record,null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors}));
