import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_W07_黑渊白花主体轮廓_C1_20261116');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
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
const page=await browser.newPage({viewport:{width:1680,height:1080},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('response',response=>{if(response.status()>=400)errors.push(`${response.status()} ${response.url()}`);});
page.on('requestfailed',request=>failed.push({url:request.url(),error:request.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W07Concept?.ready);
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
const views=[
  {view:'iso',focus:'all',spread:80,file:'整体轮廓.png'},
  {view:'top',focus:'all',spread:80,file:'俯视轮廓.png'},
  {view:'front',focus:'all',spread:80,file:'正面轮廓.png'},
  {view:'side',focus:'all',spread:80,file:'侧面轮廓.png'},
  {view:'top',focus:'weapon',spread:0,file:'原型收拢轮廓.png'},
  {view:'iso',focus:'weapon',spread:125,file:'工业展开轮廓.png'}
];
const poses=[];
for(const pose of views){
  await page.evaluate(({view,focus,spread})=>{const model=window.W07Concept;model.setFocus(focus);model.updateSpread(spread);model.setView(view);},pose);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.locator('#stage').screenshot({path:path.join(out,pose.file)});
  poses.push({...pose,...await page.evaluate(()=>window.W07Concept.snapshot())});
}
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify({poses,errors,failed},null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,views:poses.length,errors,failed,bounds:poses[0].actualBounds}));
