import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_W08_恒星核心放大_日珥特效_A2_20261116');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
if(process.argv.includes('--bundle-only'))process.exit(0);
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',error=>errors.push(error.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W08_STATIC_READY,{timeout:180000});
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const views=[
  {scene:'all',view:'front',time:8,file:'整体斜视.png'},
  {scene:'all',view:'orthofront',time:8,file:'正面.png'},
  {scene:'all',view:'side',time:8,file:'侧面.png'},
  {scene:'all',view:'top',time:8,file:'俯视.png'},
  {scene:'star',view:'star',time:8,file:'仅恒星与日珥.png'},
  {scene:'all',view:'front',time:0,corona:false,file:'日珥关闭实体.png'},
  {scene:'all',view:'blocks',time:0,corona:false,file:'逐格方块近景.png'},
  {scene:'star',view:'corona',mode:'work',time:12,file:'粒子日珥近景.png'},
];
for(const pose of views){
  await page.evaluate(({scene,view,mode='idle',time=0,corona=true})=>{
    const v=window.W08Static;v.setPaused(true);v.setScene(scene);v.setMode(mode);v.setCorona(corona);v.setTime(time);v.setView(view);
  },pose);await settle();await page.locator('#stage').screenshot({path:path.join(out,pose.file)});pose.snapshot=await page.evaluate(()=>window.W08Static.snapshot());
}
const result={size:await page.locator('#actualSize').innerText(),errors,failed,views,snapshot:await page.evaluate(()=>window.W08Static.snapshot())};
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');await browser.close();
console.log(JSON.stringify({out,views:views.length,errors,failed,renderedQuads:result.snapshot.renderedQuads}));
