import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_黑渊白花_轴线与纹样校准_D2_20261116');
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
  {scene:'all',view:'front',axis:false,file:'竖直正视.png'},
  {scene:'all',view:'back',axis:false,file:'竖直背视.png'},
  {scene:'all',view:'front',axis:true,file:'正视真实中轴.png'},
  {scene:'all',view:'pattern',axis:false,file:'纹样正视近景.png'},
  {scene:'all',view:'oblique',axis:false,file:'整体斜视.png'},
  {scene:'all',view:'mouth',axis:false,file:'后方空心筒口.png'},
  {scene:'shell',view:'blocks',axis:false,file:'逐格方块近景.png'}
];
for(const pose of views){
  await page.evaluate(({scene,view,axis})=>{window.W07Static.setScene(scene);window.W07Static.setView(view);window.W07Static.setAxis(axis);},pose);
  await settle();
  await page.locator('#stage').screenshot({path:path.join(out,pose.file)});
}
const compactViews=[
  {view:'front',axis:true,width:320,title:'正视 · 几何中线',file:'正视紧凑图.png'},
  {view:'back',axis:false,width:320,title:'背视',file:'背视紧凑图.png'},
  {view:'pattern',axis:false,width:680,title:'纹样近景',file:'纹样紧凑图.png'}
];
const panels=[];
for(const pose of compactViews){
  await page.setViewportSize({width:pose.width,height:920});
  await settle();
  await page.evaluate(({view,axis})=>{window.W07Static.setScene('all');window.W07Static.setView(view);window.W07Static.setAxis(axis);},pose);
  await settle();
  const buffer=await page.locator('#stage').screenshot({path:path.join(out,pose.file)});
  panels.push({...pose,image:buffer.toString('base64')});
}
const composite=await page.evaluate(async panels=>{
  const canvas=document.createElement('canvas');canvas.width=panels.reduce((sum,p)=>sum+p.width,0);canvas.height=960;
  const context=canvas.getContext('2d');context.fillStyle='#080f1a';context.fillRect(0,0,canvas.width,canvas.height);
  context.fillStyle='#d9e7f7';context.font='22px system-ui';context.textAlign='center';
  let x=0;
  for(const panel of panels){
    const img=new Image();img.src='data:image/png;base64,'+panel.image;await img.decode();
    context.fillText(panel.title,x+panel.width/2,29);context.drawImage(img,x,40);x+=panel.width;
  }
  return canvas.toDataURL('image/png').split(',')[1];
},panels);
await fs.writeFile(path.join(out,'三视角校准对照.png'),Buffer.from(composite,'base64'));
const result={size:await page.locator('#actualSize').innerText(),snapshot:await page.evaluate(()=>window.W07Static.snapshot()),errors,failed,views,compact_views:compactViews,comparison:'三视角校准对照.png'};
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,views:views.length,compact_views:compactViews.length,errors,failed,snapshot:result.snapshot}));
