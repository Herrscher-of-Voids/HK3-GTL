/** MAX供料机离线完整预览核验；不打开桌面浏览器或游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.join(root,'deliveries/MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107');
const log=path.join(root,'logs/mx-c01-converter-v1-20261107');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const errors=[],external=[],failed=[];
const page=await browser.newPage({viewport:{width:2200,height:1500},deviceScaleFactor:1});
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
page.on('requestfailed',r=>failed.push(r.url()));
try{
  await page.goto(pathToFileURL(path.join(output,'mx-c01/三维评审.html')).href);
  await page.waitForFunction(()=>window.REVIEW_READY&&document.getElementById('status').textContent==='三维表面已就绪。',null,{timeout:60000});
  const info=await page.evaluate(()=>({key:window.REVIEW.data.key,blocks:window.REVIEW.audit.blocks,
    materials:window.REVIEW.materials.length,ports:window.REVIEW.data.ports.length,
    readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
    materialControls:document.querySelectorAll('[data-material]').length,
    portControls:document.querySelectorAll('[data-port]').length}));
  if(info.key!=='mx-c01'||info.blocks!==10443||info.materials!==13||info.ports!==6||!info.readback||info.materialControls!==13||info.portControls!==6)throw new Error('候选载荷与完整材质／接口控件不一致');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  for(const [name,file] of [['front','完整预览.png'],['back','后侧冷却.png'],['top','俯视布局.png'],['controller','主控材质近景.png'],['inside','逐层剖切.png']]){
    await page.evaluate(name=>{window.reviewApi.setView(name);document.getElementById('showPorts').checked=false;if(name==='inside'){const e=document.getElementById('layer');e.value='17';e.dispatchEvent(new Event('input'));}},name);
    await page.waitForFunction(()=>document.getElementById('status').textContent==='三维表面已就绪。');
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(output,file)});
  }
  await style.evaluate(e=>e.remove());
  await page.setViewportSize({width:1440,height:1000});
  for(const name of ['front','right','back','top','inside','orthofront','orthoside','texture','controller']){
    await page.locator(`[data-view="${name}"]`).click();
    if(!await page.evaluate(()=>[...window.reviewApi.camera.position.toArray(),...window.reviewApi.camera.projectionMatrix.elements].every(Number.isFinite)))throw new Error('视角矩阵无效：'+name);
  }
  await page.locator('#showGlass').uncheck();
  await page.locator('#showGlass').check();
  await page.locator('#showPorts').check();
  await page.locator('#showPaths').check();
  await page.locator('#showZones').check();
  await page.locator('[data-port="0"]').click();
  await page.locator('details').filter({has:page.locator('#materials')}).locator('summary').click();
  await page.locator('[data-material="0"]').uncheck();
  await page.locator('[data-material="0"]').check();
  await page.locator('#reset').click();
  await page.locator('#layer').evaluate(e=>{e.value='12';e.dispatchEvent(new Event('input'));});
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='12');
  if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,...info,
    headless:true,desktop_used:false,game_started:false,views_checked:9,screenshots:5,
    toggles_and_layer_checked:true,errors,failed,external},null,2)+'\n');
  console.log(JSON.stringify({passed:true,...info,screenshots:5}));
}finally{await browser.close();}
