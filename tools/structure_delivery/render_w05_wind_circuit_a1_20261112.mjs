import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W05_长风理想流体环流阵_双层回流_A1_20261112');
const log=path.join(root,'logs/w05-wind-circuit-a1-20261112');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),
  three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();

const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));

try{
  await page.goto(pathToFileURL(path.join(out,'三维评审.html')).href);
  await page.waitForFunction(()=>window.__hk3Preview?.ready===true,null,{timeout:120000});
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const before=await page.evaluate(()=>window.__hk3Preview.snapshot());
  await page.waitForTimeout(600);
  const after=await page.evaluate(()=>window.__hk3Preview.snapshot());
  assert.equal(after.frames,before.frames,'静态场景持续重绘');
  assert.deepEqual(after.transforms,before.transforms,'静态构件意外运动');

  const ui={};
  await page.locator('#materialSearch').fill('voltage_machine_casing_hdv');
  assert.deepEqual(await page.locator('[data-material-row]:visible code').allTextContents(),['hk3gtl:voltage_machine_casing_hdv'],'材料搜索结果错误');
  await page.locator('#materialSearch').fill('');
  ui.material_search=true;
  const material=page.locator('[data-material="0"]');
  await material.uncheck();
  assert(await page.evaluate(()=>{
    const meshes=window.__hk3Preview.groups.flatMap(g=>g.children),target=meshes.filter(m=>m.userData.material===0);
    return target.length>0&&target.every(m=>!m.visible)&&meshes.filter(m=>m.userData.material!==0).every(m=>m.visible);
  }),'单个材料显隐错误');
  await material.check();
  assert(await page.evaluate(()=>window.__hk3Preview.groups.flatMap(g=>g.children).filter(m=>m.userData.material===0).every(m=>m.visible)),'材料恢复失败');
  ui.material_visibility=true;
  const part=page.locator('[data-part]').first(),partName=await part.getAttribute('data-part');
  await part.uncheck();
  assert(await page.evaluate(name=>!window.__hk3Preview.groups.find(g=>g.name===name).visible,partName),'构件隐藏失败');
  await part.check();
  assert(await page.evaluate(name=>window.__hk3Preview.groups.find(g=>g.name===name).visible,partName),'构件恢复失败');
  ui.part_visibility=true;
  await page.locator('#glass').uncheck();
  assert(await page.evaluate(()=>{
    const meshes=window.__hk3Preview.groups.flatMap(g=>g.children),glass=meshes.filter(m=>m.userData.glass);
    return glass.length>0&&glass.every(m=>!m.visible)&&meshes.filter(m=>!m.userData.glass).every(m=>m.visible);
  }),'玻璃隐藏错误');
  await page.locator('#glass').check();
  assert(await page.evaluate(()=>window.__hk3Preview.groups.flatMap(g=>g.children).filter(m=>m.userData.glass).every(m=>m.visible)),'玻璃恢复失败');
  ui.glass=true;
  await page.locator('#grid').check();
  assert(await page.evaluate(()=>window.__hk3Preview.scene.children.find(o=>o.type==='GridHelper').visible),'网格显示失败');
  await page.locator('#grid').uncheck();
  assert(await page.evaluate(()=>!window.__hk3Preview.scene.children.find(o=>o.type==='GridHelper').visible),'网格隐藏失败');
  ui.grid=true;
  const layer=page.locator('#layer'),maxLayer=await layer.getAttribute('max'),cutLayer=Math.floor(Number(maxLayer)/2);
  await layer.fill(String(cutLayer));await layer.dispatchEvent('input');
  const clipping=await page.evaluate(()=>window.__hk3Preview.groups.flatMap(g=>g.children)[0].material.clippingPlanes[0].constant);
  assert(Math.abs(clipping-cutLayer-1.01)<1e-9,'逐层裁切常量错误');
  assert.equal(await page.locator('#layerLabel').textContent(),String(cutLayer),'剖切高度显示错误');
  await layer.fill(maxLayer);await layer.dispatchEvent('input');
  ui.layer={height:cutLayer,clipping_constant:clipping};
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#screenshot').click()]);
  assert.equal(download.suggestedFilename(),'W05-长风环流阵.png','截图下载文件名错误');
  await download.cancel();
  ui.screenshot_download_cancelled=true;
  await page.locator('#fullscreen').click();
  await page.waitForFunction(()=>Boolean(document.fullscreenElement));
  await page.locator('#fullscreen').click();
  await page.waitForFunction(()=>!document.fullscreenElement);
  ui.fullscreen=true;

  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}#legend{display:none!important}'});
  await page.waitForFunction(()=>window.__hk3Preview.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [
    ['front','完整预览.png'],['orthofront','正面.png'],['side','侧面.png'],
    ['back','背面.png'],['top','俯视.png'],['core','核心近景.png'],['controller','主控接口.png']
  ]){
    await page.evaluate(view=>{
      const api=window.__hk3Preview;
      api.setView(view);
      api.camera.updateMatrixWorld();
      api.draw();
    },view);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const record={view,file};
    if(view!=='core'&&view!=='controller'){
      record.projectedLimit=await page.evaluate(()=>{
        const api=window.__hk3Preview,box=api.snapshot().fullBounds,p=api.camera.position.clone();
        let limit=0;
        for(const x of [box.min[0],box.max[0]])for(const y of [box.min[1],box.max[1]])for(const z of [box.min[2],box.max[2]]){
          p.set(x,y,z).project(api.camera);
          limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));
        }
        return limit;
      });
      assert(record.projectedLimit<.95,'全景裁切：'+view);
    }
    await page.locator('#stage').screenshot({path:path.join(out,file)});
    views.push(record);
  }
  assert.deepEqual({errors,failed},{errors:[],failed:[]},'预览脚本或资源加载失败');
  await fs.mkdir(log,{recursive:true});
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({
    passed:true,static:true,desktop_used:false,game_verified:false,screenshots:7,views,
    rendered_quads:before.renderedQuads,ui,errors,failed
  },null,2)+'\n');
  console.log(JSON.stringify({passed:true,screenshots:7,quads:before.renderedQuads,ui_core_checks:Object.keys(ui).length}));
}finally{
  await browser.close();
}
