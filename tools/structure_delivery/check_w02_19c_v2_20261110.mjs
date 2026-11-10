/** 检查19C静态候选与60张参考图库，不操作用户桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries',process.argv[2]||'W02_理之律者19C_多视角重制_V2_20261110');
const log=path.join(root,'logs',process.argv[3]||'w02-19c-reference-study-20261110');
const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
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
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面.png'],['side','侧面.png'],['back','背面.png'],['top','俯视.png'],['low','仰视.png']]){
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
  const details=[];
  if(['V3','V4','V5','V6','A1','A2'].includes(manifest.display_version)){
    const settings=JSON.parse(await fs.readFile(path.join(out,'局部镜头.json'),'utf8'));
    assert(Object.keys(settings).length===5,'局部镜头配置缺失');
    for(const [view,setting] of Object.entries(settings)){
      await page.evaluate(v=>window.W02Static.setView(v),view);
      const framing=await page.evaluate(({setting,offset})=>{
        const api=window.W02Static,p=api.camera.position.clone();let max=0;
        const center=setting.center.map((value,i)=>value+offset[i]);
        for(const x of [-1,1])for(const y of [-1,1])for(const z of [-1,1]){
          p.set(center[0]+x*setting.half[0],center[1]+y*setting.half[1],center[2]+z*setting.half[2]).project(api.camera);
          max=Math.max(max,Math.abs(p.x),Math.abs(p.y));
        }
        return {max,target:api.controls.target.toArray(),center};
      },{setting,offset:manifest.blueprint_to_export_offset_xyz});
      assert(framing.max<.95&&framing.target.every((value,i)=>Math.abs(value-framing.center[i])<.001),'局部镜头偏离目标：'+view);
      await page.locator('#stage').screenshot({path:path.join(out,setting.file)});details.push({view,framing});
    }
  }
  await style.evaluate(e=>e.remove());
  if(['A1','A2'].includes(manifest.display_version)){
    for(const mode of ['robot','dock','all']){
      await page.locator('[data-scene="'+mode+'"]').click();
      assert(await page.evaluate(mode=>window.W02Static.groups.every(group=>{
        const robot=/^0[1-7]_/.test(group.name);return group.visible===(mode==='all'||(mode==='robot'?robot:!robot));
      }),mode),'组合显隐模式失效：'+mode);
    }
  }
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
  const references=JSON.parse(await fs.readFile(path.join(out,'参考图清单.json'),'utf8'));
  const hashes=new Set(),angles=new Set();
  for(const item of references.images){
    const bytes=await fs.readFile(path.resolve(out,references.asset_root||'参考图',item.file));
    const hash=createHash('sha256').update(bytes).digest('hex');
    assert(hash===item.sha256,'参考图校验值失配：'+item.id);
    assert(!hashes.has(hash),'参考图重复：'+item.id);hashes.add(hash);angles.add(item.angle);
    assert(Math.min(...item.resolution)>=1080,'参考图分辨率不足：'+item.id);
    assert(item.url.startsWith('https://www.youtube.com/watch?v=')&&item.url.endsWith('&t='+item.seconds+'s'),'参考来源缺少时间点');
  }
  assert(hashes.size===60,'参考图数量不同');
  await page.goto(pathToFileURL(path.join(out,'参考图总览.html')).href);
  await page.locator('article img').evaluateAll(images=>images.forEach(image=>image.loading='eager'));
  await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>=1080));
  assert(await page.locator('article:visible').count()===60,'初始图库数量错误');
  const filters={};
  for(const kind of ['官方动画','官方教学','二创辅助']){
    await page.selectOption('#kind',{label:kind});
    const expected=references.images.filter(i=>i.source_kind===kind).length;
    filters[kind]=await page.locator('article:visible').count();assert(filters[kind]===expected,'来源筛选错误');
  }
  await page.selectOption('#kind',{label:'全部'});
  for(const angle of angles){
    await page.selectOption('#angle',{label:angle});
    assert(await page.locator('article:visible').count()===references.images.filter(i=>i.angle===angle).length,'角度筛选错误：'+angle);
  }
  await page.selectOption('#angle',{label:'全部'});
  await page.screenshot({path:path.join(log,'reference-gallery-qa.png')});
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const link of await page.locator('a').evaluateAll(links=>links.map(a=>a.getAttribute('href')))){
    if(!/^(https?:|#)/.test(link))await fs.access(path.resolve(out,link));
  }
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  await fs.writeFile(path.join(log,'reference-qa.json'),JSON.stringify({passed:true,unique_images:hashes.size,
    official:filters['官方动画']+filters['官方教学'],fan_assistance:filters['二创辅助'],filters,
    angles:[...angles],original_resolution_loaded:true,source_timestamps_verified:true,
    index_images_and_local_links_verified:true,independent_camera_positions_claimed:false},null,2)+'\n');
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,headless:true,desktop_used:false,
    game_started:false,animation_removed:true,no_idle_redraw:true,idleFrames:[before.frames,after.frames],
    scene_modes_verified:['A1','A2'].includes(manifest.display_version),
    views,details,screenshots:6+details.length,controls:['镜头旋转','玻璃显隐','剖切','独立构件显隐'],errors,failed},null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,screenshots:6+details.length,quads:before.renderedQuads,idleFrames:[before.frames,after.frames]}));
}finally{await browser.close();}
