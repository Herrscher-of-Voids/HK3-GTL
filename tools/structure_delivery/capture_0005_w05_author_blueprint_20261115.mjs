import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/0005_W05_作者蓝图原案_20261115');
const log=path.join(root,'logs/0005-w05-author-blueprint-20261115');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/author_w05_viewer_20261115.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[],failed=[],snapshots=[];
let mobile;
page.on('pageerror',e=>errors.push(e.stack));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
const views=[['front','整体预览.png'],['right','前右预览.png'],['orthofront','正面预览.png'],['side','侧面预览.png'],
  ['back','背面预览.png'],['top','俯视预览.png'],['intake','进气口近景.png'],['core','核心近景.png'],
  ['wing','双翼管网近景.png'],['crown','王冠近景.png'],['exhaust','尾喷近景.png'],['controller','主控近景.png']];
try {
  await page.goto(pathToFileURL(path.join(out,'三维评审.html')).href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.W05_AUTHOR_READY,null,{timeout:180000});
  await page.evaluate(()=>window.W05Author.freeze(12));
  await page.screenshot({path:path.join(out,'评审界面.png')});
  const fullscreenStyle=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
  await page.waitForFunction(()=>window.W05Author.renderer.domElement.clientWidth===innerWidth);
  for(const [view,file] of views) {
    await page.evaluate(view=>{window.W05Author.fit(view);window.W05Author.freeze(12);},view);
    await page.locator('#stage').screenshot({path:path.join(out,file)});
    console.log(file);
  }
  snapshots.push(await page.evaluate(()=>window.W05Author.snapshot()));
  await page.evaluate(()=>{window.W05Author.mode('work');window.W05Author.freeze(18);window.W05Author.fit('front');});
  await page.locator('#stage').screenshot({path:path.join(out,'满载工作预览.png')});
  snapshots.push(await page.evaluate(()=>window.W05Author.snapshot()));
  await page.evaluate(()=>window.W05Author.freeze(22));
  snapshots.push(await page.evaluate(()=>window.W05Author.snapshot()));
  await fullscreenStyle.evaluate(e=>e.remove());
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>{window.W05Author.mode('idle');window.W05Author.fit('front');window.W05Author.render();});
  await page.screenshot({path:path.join(out,'移动端评审.png')});
  mobile=await page.evaluate(()=>Object.fromEntries(['stage','viewName','mode','counts'].map(id=>{
    const r=document.getElementById(id).getBoundingClientRect();return [id,{x:r.x,y:r.y,width:r.width,height:r.height}];
  })));
} finally {
  await browser.close();
  await fs.writeFile(path.join(log,'preview-capture.json'),JSON.stringify({created_at:new Date().toISOString(),headless:true,transport:'local-file',
    desktop_used:false,game_started:false,errors,failed,screenshots:[...views.map(([view,file])=>({view,file})),
      {view:'work',file:'满载工作预览.png'},{view:'review',file:'评审界面.png'},{view:'mobile',file:'移动端评审.png'}],snapshots,mobile},null,2)+'\n');
}
await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
console.log(JSON.stringify({out,images:15,errors,failed}));
