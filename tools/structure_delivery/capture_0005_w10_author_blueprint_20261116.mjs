import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const out=path.join(process.cwd(),'deliveries/0005_W10_引力奇点刑架_作者蓝图_A1_20261116');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
if(process.argv.includes('--bundle-only'))process.exit(0);
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',error=>errors.push(error.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.W10_STATIC_READY,{timeout:240000});
await page.evaluate(()=>window.W10Static.setPaused(true));await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const views=[
  {scene:'all',view:'front',file:'整体_前斜视.png'},{scene:'all',view:'back',file:'整体_后斜视.png'},
  {scene:'all',view:'frontOrtho',file:'整体_前正视.png'},{scene:'all',view:'backOrtho',file:'整体_后正视.png'},
  {scene:'all',view:'side',file:'整体_侧视.png'},{scene:'all',view:'top',file:'整体_俯视.png'},
  {scene:'core',view:'core',file:'奇点核心_待机.png'},{scene:'core',view:'core',mode:'work',time:18,file:'奇点核心_工作18秒.png'},
  {scene:'rings',view:'core',time:30,effects:false,file:'双陨石环_反转30秒.png'},
  {scene:'base',view:'base',file:'基座_井口.png'},{scene:'towers',view:'towers',time:16,file:'四塔_引力牵引束.png'},
  {scene:'dome',view:'dome',time:12,file:'穹顶_下落冲击波.png'},
  {scene:'all',view:'blocks',effects:false,file:'原生像素方块_近景.png'},
  {scene:'all',view:'frontOrtho',time:12,layer:222,file:'整体_Y222剖切.png'}
];
for(const pose of views){
  await page.evaluate(({scene,view,mode='idle',time=0,effects=true,layer})=>{const v=window.W10Static;v.setPaused(true);v.setTime(0);v.setMode(mode);v.setAxis('y');v.setScene(scene);v.setEffects(effects);v.setTime(time);if(layer!==undefined)v.setLayer(layer);v.setView(view);},pose);await settle();await page.locator('#stage').screenshot({path:path.join(out,pose.file)});pose.snapshot=await page.evaluate(()=>window.W10Static.snapshot());
}
const result={size:await page.locator('#actualSize').innerText(),errors,failed,views,snapshot:await page.evaluate(()=>window.W10Static.snapshot())};await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');await browser.close();console.log(JSON.stringify({out,views:views.length,errors,failed,renderedQuads:result.snapshot.renderedQuads}));
