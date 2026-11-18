import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_支配剧场_提线共演_F1_20261117');
const log=path.join(root,'logs/0005-theatre-f1-20261117');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/theatre_f1_viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();

const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],captures=[];
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
page.on('pageerror',error=>errors.push({type:'pageerror',message:error.message}));
page.on('console',message=>{if(message.type()==='error')errors.push({type:'console.error',message:message.text()});});
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html');
await page.waitForFunction(()=>window.THEATRE_READY,{},{timeout:120000});
await page.evaluate(()=>{
  const viewer=window.TheatreViewer;
  viewer.setPlaying(false);viewer.setShellMode('cutaway');viewer.setModel('all');viewer.setView('ensemble');viewer.setTime(0);
});
await settle();
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
captures.push({file:'评审界面.png',group:'评审界面',viewport:page.viewportSize(),...await page.evaluate(()=>window.TheatreViewer.snapshot())});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});

const plans=[
  ['all','ensemble','全厅共演',1800,1200],
  ['all','front','正面共演',1800,1200],
  ['all','leftHand','左手提线',2400,1600],
  ['all','rightHand','右手提线',2400,1600],
  ['ensemble','front','仅演员共演',1800,1200],
  ['puppets','puppets','双人偶近景',2400,1600],
];
for(const [model,view,label,width,height] of plans){
  await page.setViewportSize({width,height});
  await page.evaluate(({model,view})=>{
    const viewer=window.TheatreViewer;
    viewer.setPlaying(false);viewer.setShellMode('cutaway');viewer.setModel(model);viewer.setView(view);
  },{model,view});
  for(const time of [0,2,5,9,13]){
    await page.evaluate(time=>{window.TheatreViewer.setPlaying(false);window.TheatreViewer.setTime(time);},time);
    await settle();
    const file=time===0?label+'.png':`${label}-${time}s.png`;
    await page.screenshot({path:path.join(out,file)});
    captures.push({file,group:label,viewport:page.viewportSize(),...await page.evaluate(()=>window.TheatreViewer.snapshot())});
  }
}
const record={captured_at:new Date().toISOString(),errors,captures};
await fs.mkdir(log,{recursive:true});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify(record,null,2)+'\n');
await fs.writeFile(path.join(log,'preview.json'),JSON.stringify(record,null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors}));
