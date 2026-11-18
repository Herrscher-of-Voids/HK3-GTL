import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_W07_黑渊白花贯通方舟_E1_20261116');
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
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const views=[
  {scene:'all',view:'front',file:'整体方舟预览.png'},
  {scene:'all',view:'orthofront',file:'正面方块预览.png'},
  {scene:'all',view:'side',file:'侧面方块预览.png'},
  {scene:'all',view:'back',file:'背面方块预览.png'},
  {scene:'all',view:'top',file:'俯视方块预览.png'},
  {scene:'core',view:'core',file:'黑白贯通主机.png'},
  {scene:'all',view:'black',file:'黑渊分解工区.png'},
  {scene:'all',view:'white',file:'白花再构工区.png'},
  {scene:'plant',view:'process',file:'独立分流管路.png'},
  {scene:'all',view:'controller',ports:true,file:'主控与通用接口.png'},
  {scene:'all',view:'blocks',file:'逐格方块近景.png'},
  {scene:'weapon',view:'front',file:'完整黑渊白花本体.png'},
  {scene:'plant',view:'front',file:'独立工艺设施.png'},
  {scene:'all',view:'orthofront',axis:true,file:'整机真实中轴.png'},
  {scene:'all',view:'front',viewport:{width:960,height:1120},file:'整体方舟预览紧凑图.png'}
];
for(const pose of views){
  if(pose.viewport){await page.setViewportSize(pose.viewport);await settle();}
  await page.evaluate(({scene,view,axis=false,ports=false})=>{
    window.W07Static.setScene(scene);window.W07Static.setView(view);
    window.W07Static.setAxis(axis);window.W07Static.setPorts(ports);
  },pose);
  await settle();
  await page.locator('#stage').screenshot({path:path.join(out,pose.file)});
  pose.snapshot=await page.evaluate(()=>window.W07Static.snapshot());
}
await page.setViewportSize({width:1680,height:1080});await settle();
await page.evaluate(()=>{window.W07Static.setScene('all');window.W07Static.setAxis(false);window.W07Static.setPorts(false);});
const result={size:await page.locator('#actualSize').innerText(),snapshot:await page.evaluate(()=>window.W07Static.snapshot()),errors,failed,views};
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,views:views.length,errors,failed,snapshot:result.snapshot}));
