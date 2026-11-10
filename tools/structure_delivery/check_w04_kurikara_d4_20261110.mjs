/** 俱利伽罗完整静态预览、十四视角和参考图核验；不操作桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W04_俱利伽罗_厚躯与肩背_D4_20261110');
const log=path.join(root,'logs/w04-kurikara-d4-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'dragon/viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1150},deviceScaleFactor:1});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
function assert(v,m){if(!v)throw new Error(m);}
try{
  await page.goto(pathToFileURL(path.join(out,'dragon/三维评审.html')).href);
  await page.waitForFunction(()=>window.W04_STATIC_READY,null,{timeout:120000});
  const before=await page.evaluate(()=>window.W04Static.snapshot());await page.waitForTimeout(800);
  const after=await page.evaluate(()=>window.W04Static.snapshot());
  assert(before.transforms.length===9,'独立部件数不符');assert(before.frames===after.frames,'静态预览持续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'模型发生运动');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  const full=['front','orthofront','side','back','top','underside'],views=[];
  for(const [view,file] of [['front','完整预览'],['orthofront','正面'],['side','侧面'],['back','背面'],['top','俯视'],['underside','腹面'],
    ['head','龙首近景'],['headfront','龙首正面'],['headside','龙首侧面'],['chest','颈腹近景'],['wing','翼爪近景'],
    ['wingback','翼膜背面'],['feet','后足近景'],['feetfront','腿爪正面'],['feetside','腿爪侧面'],['tail','尾部近景']]){
    await page.evaluate(({view,full})=>{
      const box=document.getElementById('isolate');box.checked=!full.includes(view);window.W04Static.setView(view);
    },{view,full});
    if(full.includes(view)){
      const limit=await page.evaluate(()=>{
        const a=window.W04Static,p=a.camera.position.clone();let m=0;
        for(const v of a.config.data.fit_points)for(const x of [0,1])for(const y of [0,1])for(const z of [0,1]){
          p.set(v[0]+x,v[1]+y,v[2]+z).project(a.camera);m=Math.max(m,Math.abs(p.x),Math.abs(p.y));
        }return m;
      });assert(limit<.95,'全景裁切：'+view);views.push({view,projectedLimit:limit});
    }
    await page.locator('#stage').screenshot({path:path.join(out,file+'.png')});
  }
  await style.evaluate(e=>e.remove());await page.locator('#isolate').uncheck();
  await page.click('[data-view="front"]');await page.locator('details summary').click();
  const check=page.locator('[data-part]').first();await check.uncheck();
  assert(await page.evaluate(()=>!window.W04Static.groups[0].visible),'部件隐藏失败');await check.check();
  await page.locator('#layer').fill('120');await page.locator('#layer').dispatchEvent('input');
  assert(await page.locator('#layerLabel').textContent()==='120','剖切失败');
  await page.locator('#layer').fill(await page.locator('#layer').getAttribute('max'));await page.locator('#layer').dispatchEvent('input');
  await page.locator('#isolate').check();await page.click('[data-view="headfront"]');
  assert(await page.evaluate(()=>window.W04Static.groups.filter(g=>g.visible).length)===1,'龙首独立显示失败');
  await page.locator('#isolate').uncheck();
  const position=await page.evaluate(()=>window.W04Static.camera.position.toArray());const box=await page.locator('#stage').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+80,box.y+box.height/2+25,{steps:3});await page.mouse.up();
  assert(JSON.stringify(position)!==JSON.stringify(await page.evaluate(()=>window.W04Static.camera.position.toArray())),'镜头拖动失败');
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  const old=await browser.newPage({viewport:{width:1600,height:1150},deviceScaleFactor:1});
  await old.goto(pathToFileURL(path.join(root,'deliveries/W04_俱利伽罗_展翼与厚尾_D3_20261110/dragon/三维评审.html')).href);
  await old.waitForFunction(()=>window.W04_STATIC_READY);
  await old.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await old.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  for(const [view,file] of [['front','全身'],['chest','胸腹']]){
    const framing=await page.evaluate(view=>{
      const a=window.W04Static;document.getElementById('isolate').checked=view==='chest';a.setView(view);
      return {position:a.camera.position.toArray(),target:a.controls.target.toArray(),zoom:a.camera.zoom,
        offset:a.config.data.blueprint_to_export_offset_xyz,left:a.camera.left,right:a.camera.right,top:a.camera.top,bottom:a.camera.bottom};
    },view);
    await page.locator('#stage').screenshot({path:path.join(out,'对照D4'+file+'.png')});
    await old.evaluate(({view,f})=>{
      const a=window.W04Static;document.getElementById('isolate').checked=view==='chest';a.setView(view);
      const shift=a.config.data.blueprint_to_export_offset_xyz.map((v,i)=>v-f.offset[i]);
      a.camera.position.fromArray(f.position.map((v,i)=>v+shift[i]));a.controls.target.fromArray(f.target.map((v,i)=>v+shift[i]));
      Object.assign(a.camera,{zoom:f.zoom,left:f.left,right:f.right,top:f.top,bottom:f.bottom});
      a.camera.updateProjectionMatrix();a.controls.update();a.renderer.render(a.scene,a.camera);
    },{view,f:framing});
    await old.locator('#stage').screenshot({path:path.join(out,'对照D3'+file+'.png')});
  }
  await old.close();
  execFileSync('python',[path.join(root,'tools/structure_delivery/publish_w04_kurikara_d4_20261110.py'),'--images-only']);
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const href of await page.locator('a').evaluateAll(a=>a.map(e=>e.getAttribute('href'))))
    if(!/^(https?:|#)/.test(href))await fs.access(path.resolve(out,href));
  await page.goto(pathToFileURL(path.join(out,'参考图总览.html')).href);
  await page.locator('img').evaluateAll(a=>a.forEach(i=>i.loading='eager'));
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  assert(await page.locator('article').count()===57,'参考图未齐');
  await page.locator('#kind').selectOption('官方教学原帧');assert(await page.locator('article:visible').count()===34,'官方来源数错误');
  await page.locator('#kind').selectOption('全部');await page.locator('#angle').selectOption('翼爪');
  assert(await page.locator('article:visible').count()>5,'部位筛选错误');
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  const qa={passed:true,static:true,desktop_used:false,game_verified:false,screenshots:16,views,parts:9,reference_images:57,
    official_frames:34,errors,failed,rendered_quads:before.renderedQuads};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify(qa));
}finally{await browser.close();}
