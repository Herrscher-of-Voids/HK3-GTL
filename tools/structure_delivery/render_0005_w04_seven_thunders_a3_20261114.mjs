import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/0005_W04_七雷取能天枢_构图A3_20261114');
const log=path.join(root,'logs/0005-w04-seven-thunders-a3-20261114');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));

await fs.mkdir(path.join(out,'生成脚本'),{recursive:true});
await fs.mkdir(log,{recursive:true});
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),
  three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();

const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[];
const report={viewport:{width:1700,height:1100},headless:true,
  readiness:['W04_STATIC_READY','W04_REVIEW_READY'],screenshot:'评审界面.png',rendered:[],errors};
page.on('pageerror',error=>errors.push({type:'pageerror',message:error.message}));
page.on('console',message=>{if(message.type()==='error')errors.push({type:'console',message:message.text()});});
page.on('requestfailed',request=>errors.push({type:'requestfailed',url:request.url(),error:request.failure()?.errorText}));

try {
  await page.goto(pathToFileURL(path.join(out,'三维布局.html')).href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.W04_STATIC_READY&&window.W04_REVIEW_READY,null,{timeout:120000});
  await page.screenshot({path:path.join(out,'评审界面.png')});
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth&&window.W04Static.renderer.domElement.clientHeight===innerHeight);
  const views=[
    ['front','整体斜视.png'],['orthofront','正面.png'],['side','侧面.png'],['back','背面.png'],['top','俯视.png'],
    ['swordfront','七雷正面.png'],['swordside','七雷侧面.png'],['blade','刀身近景.png'],
    ['field','磁环与取能装置.png'],['reactor','雷能汇流设施.png'],['controller','主控占位.png']
  ];
  for(const [view,file] of views) {
    await page.evaluate(view=>window.W04Review.setView(view),view);
    await page.evaluate(view=>{
      const a=window.W04Static,isolated=view==='swordfront'||view==='swordside';
      a.groups.forEach(group=>group.visible=!isolated||group.name.startsWith('sword_'));
      a.renderer.render(a.scene,a.camera);
    },view);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const projectedBounds=await page.evaluate(()=>{
      const a=window.W04Static,size=a.config.data.size;
      const xs=[],ys=[],point=a.camera.position.clone();
      for(const x of [0,size[0]])for(const y of [0,size[1]])for(const z of [0,size[2]]) {
        point.set(x,y,z).project(a.camera);
        xs.push(point.x);ys.push(point.y);
      }
      return {ndc:{x:[Math.min(...xs),Math.max(...xs)],y:[Math.min(...ys),Math.max(...ys)]}};
    });
    await page.locator('#stage').screenshot({path:path.join(out,file)});
    report.rendered.push({view,file,isolated_sword:view==='swordfront'||view==='swordside',
      ...(['front','orthofront','side','back','top'].includes(view)?{projectedBounds}:{})});
  }
  report.sceneBounds=await page.evaluate(()=>({size_xyz:window.W04Static.config.data.size,
    offset_xyz:window.W04Static.config.data.blueprint_to_export_offset_xyz}));
} catch(error) {
  errors.push({type:'render',message:error.message});
  throw error;
} finally {
  await fs.writeFile(path.join(log,'viewer-render.json'),JSON.stringify(report,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  await browser.close();
}
