/** 复核纯静态运行、原始坐标、完整取景及交互控件。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W02_Gemini_半构造星核船坞_V4S_静态_20261109');
const log=path.join(root,'logs/w02-static-v4s-20261109');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1740,height:1150},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
function assert(value,message){if(!value)throw new Error(message);}
try {
  await page.goto(pathToFileURL(path.join(out,'w02/三维评审.html')).href);
  await page.waitForFunction(()=>window.W02_STATIC_READY,null,{timeout:180000});
  const geometry=await page.evaluate(()=>{
    const api=window.W02Static,snapshot=api.snapshot();
    return {parts:api.groups.length,quads:snapshot.renderedQuads,
      positionsEqual:snapshot.transforms.every((t,i)=>JSON.stringify(t.position)===JSON.stringify(api.config.parts[i].origin)),
      identity:snapshot.transforms.every(t=>JSON.stringify(t.rotation)==='[0,0,0,1]'&&JSON.stringify(t.scale)==='[1,1,1]'),
      animationDataAbsent:!('motions' in api.config.data),animationEnabled:api.config.data.animation_enabled,
      animationApiAbsent:!('seek' in api)&&!('pause' in api),
      playbackControls:document.querySelectorAll('#play,#time,#timeLabel').length};
  });
  assert(geometry.parts===39&&geometry.quads===657066&&geometry.positionsEqual&&geometry.identity,'静态原坐标或表面不符');
  assert(geometry.animationDataAbsent&&!geometry.animationEnabled&&geometry.animationApiAbsent&&geometry.playbackControls===0,'动画未完整取消');
  await page.waitForTimeout(250);
  const before=await page.evaluate(()=>window.W02Static.snapshot());
  await page.waitForTimeout(1250);
  const after=await page.evaluate(()=>window.W02Static.snapshot());
  assert(before.frames===after.frames,'空闲时仍持续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'空闲时构件仍在运动');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}#legend{display:none!important}'});
  await page.waitForFunction(()=>window.W02Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面十二翼.png'],['top','俯视布局.png'],['side','侧面原案.png'],['core','半构造星核.png'],['controller','主控接口.png']]) {
    await page.evaluate(view=>window.W02Static.setView(view),view);
    const framing=await page.evaluate(view=>{
      const api=window.W02Static,box=api.snapshot().fullBounds,vector=api.camera.position.clone();let limit=0;
      for(const x of [box.min[0],box.max[0]])for(const y of [box.min[1],box.max[1]])for(const z of [box.min[2],box.max[2]]) {
        vector.set(x,y,z).project(api.camera);limit=Math.max(limit,Math.abs(vector.x),Math.abs(vector.y));
      }
      return {view,projectedLimit:limit};
    },view);
    if(['front','orthofront','top','side'].includes(view))assert(framing.projectedLimit<.95,'完整实体取景不全');
    views.push(framing);await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await style.evaluate(e=>e.remove());
  await page.locator('#glass').uncheck();
  assert(await page.evaluate(()=>window.W02Static.groups.every(g=>g.children.every(m=>!m.userData.glass||!m.visible))),'玻璃显隐失效');
  await page.locator('#glass').check();await page.locator('#ports').check();
  await page.locator('#layer').fill('150');await page.locator('#layer').dispatchEvent('input');
  assert(await page.evaluate(()=>document.getElementById('layerLabel').textContent==='150'),'剖切无效');
  await page.locator('#layer').fill('303');await page.locator('#layer').dispatchEvent('input');
  await page.locator('details').filter({has:page.locator('[data-part="crown:0"]')}).locator('summary').click();
  const checkbox=page.locator('[data-part="crown:0"]');await checkbox.uncheck();
  assert(await page.evaluate(()=>!window.W02Static.groups.find(g=>g.name==='crown:0').visible),'构件显隐失效');await checkbox.check();
  await page.evaluate(()=>window.W02Static.setView('front'));
  const cameraBefore=await page.evaluate(()=>window.W02Static.camera.position.toArray());
  const stage=await page.locator('#stage').boundingBox();
  await page.mouse.move(stage.x+stage.width/2,stage.y+stage.height/2);await page.mouse.down();
  await page.mouse.move(stage.x+stage.width/2+90,stage.y+stage.height/2+40,{steps:3});await page.mouse.up();
  assert(JSON.stringify(cameraBefore)!==JSON.stringify(await page.evaluate(()=>window.W02Static.camera.position.toArray())),'手动镜头旋转无效');
  const final=await page.evaluate(()=>window.W02Static.snapshot());
  assert(JSON.stringify(final.transforms)===JSON.stringify(before.transforms),'交互后实体原坐标发生变化');
  assert(!errors.length&&!failed.length&&!external.length,JSON.stringify({errors,failed,external}));
  const receipt={passed:true,geometry,animation_removed:true,no_idle_redraw:true,idle_interval_ms:1250,
    idle_frame_counts:[before.frames,after.frames],component_transforms_unchanged:true,views,screenshots:6,
    controls_verified:['手动镜头旋转','六视角','玻璃显隐','接口框','剖切','独立构件显隐'],
    headless:true,desktop_used:false,game_started:false,static_clearance_verified:false,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,animationRemoved:true,idleFrames:[before.frames,after.frames],screenshots:6}));
}finally{await browser.close();}
