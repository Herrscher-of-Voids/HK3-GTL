/** 离线验证新版全舰预览的原版形体、全景边界及交互，不操作桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),out=path.join(root,'deliveries/休伯利安_1145格原稿_新版预览_20261108'),log=path.join(root,'logs/hyperion-modern-preview-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/'),{chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:2200,height:1500},deviceScaleFactor:1}),errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
const check=(x,m)=>{if(!x)throw Error(m);};
try{
 await page.goto(pathToFileURL(path.join(out,'三维评审.html')).href);
 await page.waitForFunction(()=>window.REVIEW_READY,null,{timeout:180000});
 const info=await page.evaluate(()=>window.reviewApi.diagnostics());
 check(info.blocks===1469258&&info.states===113&&info.blockEntities===3402&&info.visible.blocks===1469258,'原稿与控件总数不一致');
 const shape=await page.evaluate(()=>{
  const states=window.REVIEW.states;
  function bounds(id){const s=states.find(s=>s.state===id),p=s.quads.flatMap(q=>q.p);return[0,1,2].map(a=>[Math.min(...p.filter((_,i)=>i%3===a)),Math.max(...p.filter((_,i)=>i%3===a))]);}
  return{top:bounds('minecraft:stone_brick_slab[type=top,waterlogged=false]'),bottom:bounds('minecraft:stone_brick_slab[type=bottom,waterlogged=false]'),door:bounds('minecraft:acacia_door[facing=east,half=lower,hinge=right,open=false,powered=false]'),pistonHead:bounds('minecraft:piston_head[facing=west,short=false,type=normal]'),pane:bounds('minecraft:black_stained_glass_pane[east=true,north=false,south=true,waterlogged=false,west=false]')};
 });
 check(shape.top[1][0]===.5&&shape.bottom[1][1]===.5&&shape.door[0][1]===.1875&&shape.pistonHead[0][1]===1.25&&shape.pane[0][0]===.4375,'特殊模型被压成立方体或方向不符');
 const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
 const allFit=[];
 for(const [name,file] of [['front','完整预览.png'],['back','后侧预览.png'],['top','俯视布局.png'],['texture','舰体近景.png'],['inside','逐层剖切.png']]){
  await page.evaluate(name=>window.reviewApi.setView(name),name);
  await page.waitForFunction(()=>window.reviewApi.renderer.domElement.width===innerWidth);
  const fits=await page.evaluate(()=>{
   const a=window.reviewApi;a.camera.updateMatrixWorld();const projected=[];
   for(const x of [0,1145])for(const y of [0,240])for(const z of [0,549]){const p=a.controls.target.clone().set(x,y,z).project(a.camera);projected.push([p.x,p.y,p.z]);}
   a.renderer.render(a.scene,a.camera);return projected.every(p=>Math.abs(p[0])<1&&Math.abs(p[1])<1&&Math.abs(p[2])<1);
  });
  if(!['texture'].includes(name)){check(fits,'全舰取景发生截断：'+name);allFit.push(name);}
  await page.locator('#stage').screenshot({path:path.join(out,file)});
 }
 await style.evaluate(e=>e.remove());await page.setViewportSize({width:1440,height:1000});
 for(const name of ['front','right','back','top','orthofront','orthoside','inside','texture']){
  await page.locator('[data-view="'+name+'"]').click();check(await page.evaluate(()=>window.reviewApi.camera.projectionMatrix.elements.every(Number.isFinite)),'无效相机：'+name);
 }
 await page.locator('#reset').click();
 await page.locator('details').filter({has:page.locator('#materials')}).locator('summary').click();
 check(await page.locator('[data-material]').count()===113,'状态筛选控件数量不对');
 const firstCount=await page.evaluate(()=>window.REVIEW.states[0].count);await page.locator('[data-material="0"]').uncheck();
 check((await page.evaluate(()=>window.reviewApi.diagnostics())).visible.blocks===1469258-firstCount,'材质开关没有正确过滤');await page.locator('[data-material="0"]').check();
 await page.locator('#materialSearch').fill('活板门');const matching=await page.locator('[data-row]:not([hidden])').count();check(matching>0&&matching<113,'材质搜索无效');await page.locator('#materialSearch').fill('');
 await page.locator('#showGlass').uncheck();check((await page.evaluate(()=>window.reviewApi.diagnostics())).visible.blocks<1469258,'玻璃开关无效');await page.locator('#showGlass').check();
 await page.locator('#layer').evaluate(e=>{e.value='100';e.dispatchEvent(new Event('input'));});
 const sliced=await page.evaluate(()=>window.reviewApi.diagnostics());check(sliced.visible.layer===100&&sliced.visible.blocks>0&&sliced.visible.blocks<1469258,'剖切无效');
 const specialSliced=await page.evaluate(()=>window.reviewApi.meshes.filter(m=>!m.userData.runs).every(m=>m.count===0||Math.floor(m.userData.indices[m.count-1]/(1145*549))<=100));check(specialSliced,'特殊形体未随高度过滤');
 await page.locator('#reset').click();check((await page.evaluate(()=>window.reviewApi.diagnostics())).visible.blocks===1469258,'重置没有恢复全舰');
 const download=page.waitForEvent('download');await page.locator('#saveImage').click();const saved=await download;await saved.saveAs(path.join(log,'截图按钮.png'));check((await fs.stat(path.join(log,'截图按钮.png'))).size>10000,'保存视角失败');
 await page.setViewportSize({width:390,height:844});
 const mobile=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,canvasWidth:document.querySelector('canvas').clientWidth}));check(mobile.width===mobile.documentWidth&&mobile.canvasWidth>0,'手机布局溢出');
 check(!errors.length&&!failed.length&&!external.length,JSON.stringify({errors,failed,external}));
 const result={passed:true,...info,special_model_bounds:shape,full_views_fit:allFit,views_checked:8,screenshots:5,material_filter:true,material_search:true,glass_toggle:true,height_slice:true,special_models_slice:true,reset:true,save_image:true,mobile,headless:true,desktop_used:false,game_started:false,errors,failed,external};
 await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:true,blocks:info.blocks,states:info.states,meshCount:info.meshCount,screenshots:5}));
}catch(e){await fs.writeFile(path.join(log,'viewer-failure.json'),JSON.stringify({message:e.message,errors,failed,external},null,2));throw e;}finally{await browser.close();}
