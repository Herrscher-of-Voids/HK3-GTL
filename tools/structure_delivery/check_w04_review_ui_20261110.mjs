/** 核验统一评审界面与操作恢复，保持两版几何文件不变。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const log=path.join(root,'logs/w04-review-ui-restore-20261110');
const folders=['W04_龙踞雷池七雷镇枢_组合布局_P1_20261110','W04_中轴七雷三巴纹磁环_组合布局_P2_20261110'];
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const baseline=JSON.parse(await fs.readFile(path.join(log,'geometry-before.json'),'utf8')),results=[];
function assert(v,message){if(!v)throw new Error(message);}
try{
  for(const folder of folders){
    const out=path.join(root,'deliveries',folder);
    const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
      'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
    await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
    const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1,acceptDownloads:true});
    const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
    await page.goto(pathToFileURL(path.join(out,'三维布局.html')).href);
    await page.waitForFunction(()=>window.W04_REVIEW_READY,null,{timeout:120000});
    await page.waitForTimeout(200);
    const before=await page.evaluate(()=>({frames:W04Static.renderer.info.render.frame,transforms:W04Static.snapshot().transforms}));
    await page.waitForTimeout(600);
    const after=await page.evaluate(()=>({frames:W04Static.renderer.info.render.frame,transforms:W04Static.snapshot().transforms}));
    assert(JSON.stringify(before)===JSON.stringify(after),'静态页面持续重绘或构件运动');
    const boxes=await page.evaluate(()=>{
      const stage=document.getElementById('stage').getBoundingClientRect(),aside=document.querySelector('aside').getBoundingClientRect();
      return {stage:{x:stage.x,width:stage.width},aside:{x:aside.x,width:aside.width}};
    });
    assert(boxes.stage.x===0&&boxes.aside.x>=boxes.stage.width&&Math.abs(boxes.aside.width-340)<1,'未恢复左视图右340像素评审栏');
    const metadata=await page.evaluate(()=>W04Review.metadata),sourceBlocks=await page.evaluate(()=>W04Static.config.parts.reduce((n,p)=>n+p.blocks,0));
    assert(metadata.source_voxels===sourceBlocks,'源体素材料统计与构件总量不同');
    await page.locator('#showGrid').check();assert(await page.evaluate(()=>W04Review.grid.visible),'网格控件失败');
    await page.locator('#showGrid').uncheck();await page.locator('#layer').fill('150');await page.locator('#layer').dispatchEvent('input');
    assert(await page.locator('#layerValue').textContent()==='150','剖切高度未同步');
    assert(await page.evaluate(()=>W04Static.groups[0].children[0].material.clippingPlanes[0].constant)<152,'体素剖切失败');
    assert(await page.evaluate(()=>W04Static.sceneryGroups.base.children.filter(m=>m.isMesh).every(m=>m.material.clippingPlanes?.[0]?.constant<152)),'草模未跟随剖切');
    await page.locator('#reset').click();
    await page.locator('#glass').uncheck();
    assert(await page.evaluate(()=>W04Static.groups.flatMap(g=>g.children).filter(m=>m.userData.glass).every(m=>!m.visible)),'玻璃显隐失败');
    await page.locator('#glass').check();
    const materialDetails=page.locator('details').filter({has:page.locator('#materials')});
    await materialDetails.locator('summary').click();await page.locator('#materialSearch').fill('black_concrete');
    assert(await page.locator('.material:visible').count()===1,'材料搜索失败');
    await page.locator('[data-material="minecraft:black_concrete"]').uncheck();
    assert(await page.evaluate(()=>W04Static.groups.flatMap(g=>g.children).filter(m=>W04Static.config.materials[m.userData.material].state==='minecraft:black_concrete').every(m=>!m.visible)),'跨构件材料隐藏失败');
    await page.locator('#materialSearch').fill('');await page.locator('#reset').click();
    await page.locator('[data-asset="dragon"]').uncheck();
    assert(await page.evaluate(()=>W04Static.groups.filter(g=>g.name.startsWith('dragon_')).every(g=>!g.visible)),'分组显隐失败');
    await page.locator('[data-asset="dragon"]').check();
    await page.locator('[data-view="controller"]').click();assert((await page.locator('#viewName').textContent()).includes('主控'),'主控定位失败');
    await page.locator('#reset').click();
    const downloadPromise=page.waitForEvent('download');await page.locator('#saveImage').click();const download=await downloadPromise;
    assert((await fs.stat(await download.path())).size>10000,'截图下载无有效内容');
    await page.locator('#fullscreen').click();await page.waitForFunction(()=>!!document.fullscreenElement);
    await page.evaluate(()=>document.exitFullscreen());
    const stage=await page.locator('#stage').boundingBox();const position=await page.evaluate(()=>W04Static.camera.position.toArray());
    await page.mouse.move(stage.x+stage.width/2,stage.y+stage.height/2);await page.mouse.down();
    await page.mouse.move(stage.x+stage.width/2+70,stage.y+stage.height/2+20,{steps:4});await page.mouse.up();
    assert(JSON.stringify(position)!==JSON.stringify(await page.evaluate(()=>W04Static.camera.position.toArray())),'镜头拖动失败');
    await page.locator('#reset').click();await page.screenshot({path:path.join(out,'统一评审界面.png')});
    await page.setViewportSize({width:720,height:1000});
    const mobile=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,stage:document.getElementById('stage').clientHeight}));
    assert(mobile.scroll<=mobile.width+2&&mobile.stage>=420,'窄屏布局溢出');
    assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
    for(const [name,expected] of Object.entries(baseline[folder])){
      const actual=crypto.createHash('sha256').update(await fs.readFile(path.join(out,name))).digest('hex');assert(actual===expected,'几何或既有核验文件被改写：'+name);
    }
    results.push({candidate:folder,passed:true,static:true,right_sidebar_width:boxes.aside.width,source_voxels:metadata.source_voxels,
      material_search:true,material_visibility:true,clipping_including_scenery:true,glass_visibility:true,grid:true,
      scene_visibility:true,controller_location:true,download_screenshot:true,fullscreen:true,camera_drag:true,mobile:true,
      geometry_and_manifest_unchanged:true,game_verified:false,errors,failed});await page.close();
  }
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,results},null,2)+'\n');
  console.log(JSON.stringify({passed:true,results}));
}finally{await browser.close();}
