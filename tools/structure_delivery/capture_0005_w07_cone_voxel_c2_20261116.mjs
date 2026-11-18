import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_W07_黑渊白花锥壳方块稿_C2_20261116');
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
page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
page.on('response',response=>{if(response.status()>=400)errors.push(`${response.status()} ${response.url()}`);});
page.on('requestfailed',request=>failed.push({url:request.url(),error:request.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W07_STATIC_READY,{timeout:180000});
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
const views=[
  {scene:'all',view:'front',file:'整体方块预览.png'},
  {scene:'all',view:'orthofront',file:'正面方块预览.png'},
  {scene:'all',view:'side',file:'侧面方块预览.png'},
  {scene:'all',view:'top',file:'俯视方块预览.png'},
  {scene:'shell',view:'shell',file:'卷合白锥壳.png'},
  {scene:'shell',view:'mouth',file:'后方空心筒口.png'},
  {scene:'shell',view:'blocks',file:'逐格方块近景.png'}
];
for(const pose of views){
  await page.evaluate(({scene,view})=>{window.W07Static.setScene(scene);window.W07Static.setView(view);},pose);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.locator('#stage').screenshot({path:path.join(out,pose.file)});
}
const result={size:await page.locator('#actualSize').innerText(),snapshot:await page.evaluate(()=>window.W07Static.snapshot()),errors,failed,views};
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,views:views.length,errors,failed,snapshot:result.snapshot}));
