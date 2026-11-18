import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
if(process.argv.includes('--bundle-only'))process.exit(0);
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],failed=[],captures=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W13_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:240000});
const loadingError=await page.locator('#loading').allTextContents();
if(loadingError.length)throw new Error(loadingError.join('\n'));
await page.evaluate(()=>{window.W13Viewer.setPaused(true);window.W13Viewer.setTime(0);});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
for(const [model,view,file] of [
  ['all','oblique','整体预览.png'],['all','front','正面预览.png'],['all','back','背面预览.png'],['all','top','俯视预览.png'],
  ['base','well','深坑黑盒.png'],['arms','clean','完整侧机械臂.png'],['arms','corrupt','侵蚀侧机械臂.png'],
  ['core','core','白金框与晶花.png'],['core','rings','三道倾斜环.png'],['core','flower','晶花近景.png'],['canopy','canopy','十三倒悬碑与天幕.png'],
  ['base','controller','主控近景.png'],['arms','pixels','像素近景.png']]){
  await page.evaluate(({model,view})=>{window.W13Viewer.setModel(model);window.W13Viewer.setView(view);},{model,view});await settle();
  await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W13Viewer.snapshot())});
}
await page.evaluate(()=>{window.W13Viewer.setModel('all');window.W13Viewer.setCanopy(false);window.W13Viewer.setView('oblique');});await settle();
await page.screenshot({path:path.join(out,'去天幕全景.png')});captures.push({file:'去天幕全景.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await page.evaluate(()=>{window.W13Viewer.setCanopy(true);window.W13Viewer.setMode('work');window.W13Viewer.setTime(0);});await settle();
await page.screenshot({path:path.join(out,'运行零秒.png')});captures.push({file:'运行零秒.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await page.evaluate(()=>window.W13Viewer.setTime(20));await settle();
await page.screenshot({path:path.join(out,'运行二十秒.png')});captures.push({file:'运行二十秒.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await page.evaluate(()=>{window.W13Viewer.setTime(0);window.W13Viewer.setMode('idle');window.W13Viewer.setCutaway(true);window.W13Viewer.setView('front');});await settle();
await page.screenshot({path:path.join(out,'基座前半剖开.png')});captures.push({file:'基座前半剖开.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_0005_w13_author_blueprint_20261117.mjs'),path.join(out,'生成脚本/preview_0005_w13_author_blueprint_20261117.mjs'));
await browser.close();console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
