/** 打包并离线检查19C静态小样，不操作用户桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W02_理之律者19C_静态造型小样_V1_20261110');
const log=path.join(root,'logs/w02-19c-static-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'w02/viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
function assert(value,message){if(!value)throw new Error(message);}
try{
  await page.goto(pathToFileURL(path.join(out,'w02/三维评审.html')).href);
  await page.waitForFunction(()=>window.W02_STATIC_READY,null,{timeout:120000});
  const before=await page.evaluate(()=>window.W02Static.snapshot());
  await page.waitForTimeout(1000);
  const after=await page.evaluate(()=>window.W02Static.snapshot());
  assert(before.frames===after.frames,'空闲仍在连续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'静态构件仍在运动');
  assert(await page.locator('#play,#time').count()===0,'出现播放或时间轴');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}#legend{display:none!important}'});
  await page.waitForFunction(()=>window.W02Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面.png'],['side','侧面.png'],['back','背面待核对.png'],['top','俯视.png']]){
    await page.evaluate(v=>window.W02Static.setView(v),view);
    const limit=await page.evaluate(()=>{
      const api=window.W02Static,box=api.snapshot().fullBounds,p=api.camera.position.clone();let max=0;
      for(const x of [box.min[0],box.max[0]])for(const y of [box.min[1],box.max[1]])for(const z of [box.min[2],box.max[2]]){
        p.set(x,y,z).project(api.camera);max=Math.max(max,Math.abs(p.x),Math.abs(p.y));
      }return max;
    });
    assert(limit<.95,'完整小样取景不全');views.push({view,projectedLimit:limit});
    await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await style.evaluate(e=>e.remove());
  const checkbox=page.locator('[data-part]').first();await checkbox.uncheck();
  assert(await page.evaluate(()=>!window.W02Static.groups[0].visible),'构件显隐无效');await checkbox.check();
  await page.locator('#layer').fill('70');await page.locator('#layer').dispatchEvent('input');
  assert(await page.locator('#layerLabel').textContent()==='70','剖切无效');
  await page.locator('#layer').fill(await page.locator('#layer').getAttribute('max'));await page.locator('#layer').dispatchEvent('input');
  await page.locator('#glass').uncheck();await page.locator('#glass').check();
  const originalCamera=await page.evaluate(()=>window.W02Static.camera.position.toArray());
  const box=await page.locator('#stage').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+70,box.y+box.height/2+30,{steps:3});await page.mouse.up();
  assert(JSON.stringify(originalCamera)!==JSON.stringify(await page.evaluate(()=>window.W02Static.camera.position.toArray())),'镜头旋转无效');
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,headless:true,desktop_used:false,
    game_started:false,animation_removed:true,no_idle_redraw:true,idleFrames:[before.frames,after.frames],
    views,screenshots:5,controls:['镜头旋转','玻璃显隐','剖切','独立构件显隐'],errors,failed},null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,screenshots:5,quads:before.renderedQuads,idleFrames:[before.frames,after.frames]}));
}finally{await browser.close();}
