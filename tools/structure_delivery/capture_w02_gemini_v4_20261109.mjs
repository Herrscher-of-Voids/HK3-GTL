/** 隐藏浏览器验证完整构件、动画变换、视角和控件，不操作桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W02_Gemini_半构造星核船坞_V4_20261109');
const log=path.join(root,'logs/w02-gemini-v4-20261109');
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
  await page.waitForFunction(()=>window.W02_V4_READY,null,{timeout:180000});
  const initial=await page.evaluate(()=>({snapshot:window.W02V4.snapshot(),parts:window.W02V4.config.parts.length,
    wings:window.W02V4.config.data.wings.length,wells:window.W02V4.config.data.wells.length,
    cables:window.W02V4.config.data.cables.length,readback:window.W02V4.config.audit.readback.geometry_nbt_schematic_per_block_equal}));
  assert(initial.parts===39&&initial.wings===12&&initial.wells===4&&initial.cables===8&&initial.readback,'构件或完整回读不符');
  assert(!initial.snapshot.playing&&initial.snapshot.seconds===0,'默认原案状态错误');
  await page.evaluate(()=>window.W02V4.seek(37));
  const moved=await page.evaluate(()=>window.W02V4.snapshot());
  const changed=moved.transforms.filter((v,i)=>JSON.stringify(v)!==JSON.stringify(initial.snapshot.transforms[i]));
  assert(changed.some(t=>t.id==='crown:1')&&changed.some(t=>t.id==='crown:2')&&changed.some(t=>t.id==='core-cage'),'星环或核心未转动');
  assert(changed.filter(t=>t.id.startsWith('wing:')).length===12,'十二翼未完整运动');
  const fixed=initial.snapshot.transforms.find(t=>t.id==='crown:0');
  assert(JSON.stringify(moved.transforms.find(t=>t.id==='crown:0'))===JSON.stringify(fixed),'原案外环未保持固定');
  await page.evaluate(()=>{window.W02V4.seek(0);});
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}#legend{display:none!important}'});
  await page.waitForFunction(()=>window.W02V4.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面十二翼.png'],['top','俯视布局.png'],['side','侧面原案.png'],['core','半构造星核.png'],['controller','主控接口.png']]) {
    await page.evaluate(view=>window.W02V4.setView(view),view);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const framing=await page.evaluate(view=>{
      const a=window.W02V4;const box=a.snapshot().sweptBounds;let limit=0;
      const vector=a.camera.position.clone();
      for(const x of [box.min[0],box.max[0]])for(const y of [box.min[1],box.max[1]])for(const z of [box.min[2],box.max[2]]) {
        vector.set(x,y,z).project(a.camera);limit=Math.max(limit,Math.abs(vector.x),Math.abs(vector.y));
      }
      return {view,projectedLimit:limit,rendererCalls:a.renderer.info.render.calls};
    },view);
    if(['front','orthofront','top','side'].includes(view))assert(framing.projectedLimit<.95,'完整扫掠范围未取全');
    views.push(framing);await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await page.evaluate(()=>window.W02V4.setView('front'));
  const frames=path.join(log,'frames');await fs.mkdir(frames,{recursive:true});
  for(let i=0;i<24;i++) {
    await page.evaluate(t=>window.W02V4.seek(t),i*5);
    await page.locator('#stage').screenshot({path:path.join(frames,String(i).padStart(3,'0')+'.png')});
  }
  await style.evaluate(e=>e.remove());
  await page.locator('#glass').uncheck();
  assert(await page.evaluate(()=>window.W02V4.groups.every(g=>g.children.every(m=>!m.userData.glass||!m.visible))),'玻璃显隐无效');
  await page.locator('#glass').check();await page.locator('#ports').check();
  await page.locator('#layer').fill('150');await page.locator('#layer').dispatchEvent('input');
  assert((await page.evaluate(()=>window.W02V4.snapshot())).sliced,'剖切未进入静态');
  await page.locator('#layer').fill(String(await page.evaluate(()=>window.W02V4.config.data.size[1]-1)));await page.locator('#layer').dispatchEvent('input');
  await page.locator('details').filter({has:page.locator('[data-part="crown:0"]')}).locator('summary').click();
  const checkbox=page.locator('[data-part="crown:0"]');await checkbox.uncheck();
  assert(await page.evaluate(()=>!window.W02V4.groups.find(g=>g.name==='crown:0').visible),'独立显隐无效');await checkbox.check();
  await page.evaluate(()=>{window.W02V4.seek(0);window.W02V4.pause(false);});
  await page.waitForFunction(()=>window.W02V4.snapshot().seconds>.2);
  await page.evaluate(()=>window.W02V4.pause(true));
  assert(!errors.length&&!failed.length&&!external.length,JSON.stringify({errors,failed,external}));
  const receipt={passed:true,headless:true,desktop_used:false,game_started:false,initial,changedParts:changed.map(t=>t.id),
    views,screenshots:6,animation_frames:24,web_preview_only:true,dynamic_clearance_verified:false,
    controls_verified:['播放暂停','时间拖动','外环固定','十二翼浮动','中内环翻转','星笼转动','玻璃显隐','接口框','分层','独立构件显隐'],errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,parts:initial.parts,quads:initial.snapshot.renderedQuads,views:views.length,changed:changed.length}));
}finally{await browser.close();}
