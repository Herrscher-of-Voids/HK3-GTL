/** 鸣雷见独立静态预览、多视角与参考图完整性核验；不操作桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W04_涤罪七雷鸣雷见_独立小样_S1_20261110');
const log=path.join(root,'logs/w04-narukami-study-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'weapon/viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:950},deviceScaleFactor:1});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
function assert(v,m){if(!v)throw new Error(m);}
try{
  await page.goto(pathToFileURL(path.join(out,'weapon/三维评审.html')).href);
  await page.waitForFunction(()=>window.W04_STATIC_READY,null,{timeout:60000});
  const before=await page.evaluate(()=>window.W04Static.snapshot());await page.waitForTimeout(700);
  const after=await page.evaluate(()=>window.W04Static.snapshot());
  assert(before.transforms.length===5,'独立部件数不符');
  assert(before.frames===after.frames,'静态预览持续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'模型发生动画');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['orthofront','正面'],['back','背面'],['front','斜视'],['rearoblique','背斜视'],['top','刃背'],['end','端面'],
    ['root','刃根近景'],['guard','刀镡近景'],['guardend','刀镡端面'],['grip','握柄近景'],['pommel','柄尾近景'],['tip','刀尖近景']]){
    await page.evaluate(v=>window.W04Static.setView(v),view);
    if(['orthofront','back','front','rearoblique','top','end'].includes(view)){
      const limit=await page.evaluate(()=>{
        const a=window.W04Static,b=a.snapshot().fullBounds,p=a.camera.position.clone();let m=0;
        for(const x of [b.min[0],b.max[0]])for(const y of [b.min[1],b.max[1]])for(const z of [b.min[2],b.max[2]]){
          p.set(x,y,z).project(a.camera);m=Math.max(m,Math.abs(p.x),Math.abs(p.y));
        }return m;
      });assert(limit<.95,'全景被裁切：'+view);views.push({view,projectedLimit:limit});
    }
    await page.locator('#stage').screenshot({path:path.join(out,file+'.png')});
  }
  await style.evaluate(e=>e.remove());
  await page.locator('details summary').click();
  const check=page.locator('[data-part]').first();await check.uncheck();
  assert(await page.evaluate(()=>!window.W04Static.groups[0].visible),'部件隐藏失败');await check.check();
  await page.locator('#layer').fill('50');await page.locator('#layer').dispatchEvent('input');
  assert(await page.locator('#layerLabel').textContent()==='50','剖切失败');
  await page.locator('#layer').fill(await page.locator('#layer').getAttribute('max'));await page.locator('#layer').dispatchEvent('input');
  await page.locator('#glass').uncheck();await page.locator('#glass').check();
  await page.click('[data-view="orthofront"]');
  const position=await page.evaluate(()=>window.W04Static.camera.position.toArray());
  const box=await page.locator('#stage').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+80,box.y+box.height/2+25,{steps:3});await page.mouse.up();
  assert(JSON.stringify(position)!==JSON.stringify(await page.evaluate(()=>window.W04Static.camera.position.toArray())),'镜头拖动失败');
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const href of await page.locator('a').evaluateAll(a=>a.map(e=>e.getAttribute('href'))))
    if(!/^(https?:|#)/.test(href))await fs.access(path.resolve(out,href));
  await page.goto(pathToFileURL(path.join(out,'参考图总览.html')).href);
  await page.locator('img').evaluateAll(a=>a.forEach(i=>i.loading='eager'));
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  assert(await page.locator('article').count()===48,'参考图未齐');
  await page.locator('#angle').selectOption('旋转视角');assert(await page.locator('article:visible').count()===30,'转台图数量错误');
  await page.locator('#angle').selectOption('全部');
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  const qa={passed:true,static:true,desktop_used:false,game_verified:false,screenshots:12,views,parts:5,reference_images:48,
    continuous_turntable_samples:30,errors,failed,rendered_quads:before.renderedQuads};
  await fs.writeFile(path.join(log,'s1-viewer-qa.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify(qa));
}finally{await browser.close();}
