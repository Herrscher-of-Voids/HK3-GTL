/** 离线核验完整C1与同源单矛；不操作桌面或游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.join(root,'deliveries/W03_C方案_亚空之矛优化_C1_20261108');
const log=path.join(root,'logs/w03-c-spear-refinement-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const errors=[],failed=[],external=[];
const page=await browser.newPage({viewport:{width:2200,height:1500},deviceScaleFactor:1});
page.on('pageerror',e=>errors.push(e.message));
page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
const records=[];
try{
  for(const single of [false,true]){
    const folder=single?path.join(output,'单矛拆件'):output,key=single?'spear':'w03';
    const manifest=JSON.parse(await fs.readFile(path.join(folder,'manifest.json'),'utf8'));
    await page.goto(pathToFileURL(path.join(folder,key,'三维评审.html')).href);
    await page.waitForFunction(single?()=>window.SPEAR_READY:()=>window.BOUNDARY_READY,null,{timeout:180000});
    const info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
      materials:document.querySelectorAll('[data-material]').length,ports:document.querySelectorAll('[data-port]').length}));
    if(info.blocks!==manifest.blocks||info.materials!==manifest.unique_materials||!info.readback||info.ports!==manifest.ports.length)throw new Error('完整载荷或材质/接口数不符');
    const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
    for(const [name,file] of single?[['single','单矛近景.png']]:[['front','完整预览.png'],['back','后侧设备.png'],['top','俯视布局.png'],['controller','主控材质近景.png']]){
      if(name!=='single')await page.evaluate(name=>window.reviewApi.setView(name),name);
      await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
      await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
      await page.locator('#stage').screenshot({path:path.join(output,file)});
    }
    await style.evaluate(e=>e.remove());
    await page.setViewportSize({width:1440,height:1000});
    for(const name of ['front','right','back','top','orthofront','orthoside','texture']){
      await page.locator(`[data-view="${name}"]`).click();
      if(!await page.evaluate(()=>[...window.reviewApi.camera.position.toArray(),...window.reviewApi.camera.projectionMatrix.elements].every(Number.isFinite)))throw new Error('视角矩阵无效');
    }
    await page.locator('#showGlass').uncheck();await page.locator('#showGlass').check();
    await page.locator('#layer').evaluate(e=>{e.value='12';e.dispatchEvent(new Event('input'));});
    await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='12');
    if(!single){await page.locator('#showPorts').check();await page.locator('[data-port="0"]').click();}
    records.push({single,...info});
    await page.setViewportSize({width:2200,height:1500});
  }
  if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
  const receipt={passed:true,headless:true,desktop_used:false,game_started:false,records,views_checked:14,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify(receipt));
}finally{await browser.close();}
