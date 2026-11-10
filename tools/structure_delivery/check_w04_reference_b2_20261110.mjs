/** W04图片校准B2静态预览、十五视角和参考来源核验；不替代游戏实装。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110');
const log=path.join(root,'logs/w04-reference-b2-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'w04/viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
function assert(value,message){if(!value)throw new Error(message);}
try{
  await page.goto(pathToFileURL(path.join(out,'w04/三维评审.html')).href);
  await page.waitForFunction(()=>window.W04_STATIC_READY,null,{timeout:120000});
  const before=await page.evaluate(()=>window.W04Static.snapshot());
  assert(before.transforms.length===20,'构件数变化');
  await page.waitForTimeout(1000);const after=await page.evaluate(()=>window.W04Static.snapshot());
  assert(before.frames===after.frames,'静态场景持续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'构件意外运动');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}#legend{display:none!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面.png'],['side','侧面.png'],['back','背面.png'],['top','俯视.png'],['low','仰视.png'],['core','核心近景.png'],['dragon','龙首近景.png'],['hand','鬼手近景.png'],['sword','巨刃近景.png'],['wing','翼爪近景.png'],['body','龙体近景.png'],['dragonfront','龙首正面.png'],['dragonside','龙首侧面.png'],['dragonall','龙体独立.png']]){
    // 局部图独立显示目标构件；六个全景与核心图始终保留完整场景。
    await page.evaluate(view=>{
      const api=window.W04Static;
      api.groups.forEach(g=>g.visible=['dragon','dragonfront','dragonside'].includes(view)?g.name.startsWith('10_'):
        view==='wing'?g.name.startsWith('09_+1'):
        ['body','dragonall'].includes(view)?/^(08_|09_|10_|11_)/.test(g.name):
        view==='hand'?g.name.startsWith('06_-1')||g.name.startsWith('07_-1'):
        view==='sword'?g.name.startsWith('03_'):true);
    },view);
    await page.evaluate(v=>window.W04Static.setView(v),view);
    if(!['core','dragon','hand','sword','wing','body','dragonfront','dragonside','dragonall'].includes(view)){
      const limit=await page.evaluate(()=>{
        const api=window.W04Static,box=api.snapshot().fullBounds,p=api.camera.position.clone();let max=0;
        for(const x of [box.min[0],box.max[0]])for(const y of [box.min[1],box.max[1]])for(const z of [box.min[2],box.max[2]]){
          p.set(x,y,z).project(api.camera);max=Math.max(max,Math.abs(p.x),Math.abs(p.y));
        }return max;
      });assert(limit<.95,'全景裁切：'+view);views.push({view,projectedLimit:limit});
    }
    await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await page.evaluate(()=>{window.W04Static.groups.forEach(g=>g.visible=true);window.W04Static.setView('front');});
  await style.evaluate(e=>e.remove());
  const check=page.locator('[data-part]').first();await check.uncheck();
  assert(await page.evaluate(()=>!window.W04Static.groups[0].visible),'构件显隐失败');await check.check();
  await page.locator('#layer').fill('70');await page.locator('#layer').dispatchEvent('input');
  assert(await page.locator('#layerLabel').textContent()==='70','剖切失败');
  await page.locator('#layer').fill(await page.locator('#layer').getAttribute('max'));await page.locator('#layer').dispatchEvent('input');
  await page.locator('#glass').uncheck();await page.locator('#glass').check();
  const camera=await page.evaluate(()=>window.W04Static.camera.position.toArray());
  const box=await page.locator('#stage').boundingBox();await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+70,box.y+box.height/2+30,{steps:3});await page.mouse.up();
  assert(JSON.stringify(camera)!==JSON.stringify(await page.evaluate(()=>window.W04Static.camera.position.toArray())),'镜头拖动失败');
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const link of await page.locator('a').evaluateAll(links=>links.map(a=>a.getAttribute('href'))))if(!/^(https?:|#)/.test(link))await fs.access(path.resolve(out,link));
  await page.goto(pathToFileURL(path.join(out,'参考图总览.html')).href);
  await page.locator('img').evaluateAll(imgs=>imgs.forEach(i=>i.loading='eager'));
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  assert(await page.locator('article').count()===44,'参考图数不同');
  await page.locator('#kind').selectOption('官方教学');assert(await page.locator('article:visible').count()===20,'官方来源筛选错误');
  await page.locator('#kind').selectOption('玩家游戏画面');assert(await page.locator('article:visible').count()===19,'玩家来源筛选错误');
  await page.locator('#kind').selectOption('全部');await page.locator('#angle').selectOption('武器·鸣雷见');
  assert(await page.locator('article:visible').count()===14,'武器形态分组错误');
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,static:true,desktop_used:false,game_verified:false,views,screenshots:15,reference_images:44,isolated_detail_views:['dragon','hand','sword','wing','body','dragonfront','dragonside','dragonall'],errors,failed},null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,screenshots:15,quads:before.renderedQuads}));
}finally{await browser.close();}
