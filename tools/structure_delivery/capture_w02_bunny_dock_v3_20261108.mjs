/** W02原案完整真实材质预览核验，不操作游戏或桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W02_Gemini_十二翼重构船坞_V3_20261108');
const log=path.join(root,'logs/w02-bunny-dock-v3-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1450},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
try{
  const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
  await page.goto(pathToFileURL(path.join(out,'w02/三维评审.html')).href);
  await page.waitForFunction(()=>window.W02_BUNNY_READY,null,{timeout:180000});
  const info=await page.evaluate(()=>{
    let full=true,instances=0;
    window.reviewApi.scene.traverse(o=>{if(o.userData.indices){full&&=o.userData.initialized===o.userData.indices.length;instances+=o.userData.indices.length;}});
    return {blocks:window.REVIEW.audit.blocks,readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
      wings:window.REVIEW.data.wings.length,towers:window.REVIEW.data.towers.length,crowns:window.REVIEW.data.crowns.length,
      cables:window.REVIEW.data.cables.length,materials:window.REVIEW.materials.length,full,instances,
      ports:document.querySelectorAll('[data-port]').length,material_controls:document.querySelectorAll('[data-material]').length};
  });
  if(!info.full||!info.readback||info.blocks!==manifest.blocks||info.wings!==12||info.towers!==64||info.crowns!==3||info.cables!==8||info.ports!==8||info.materials!==16||info.material_controls!==16)
    throw new Error('完整模型核验失败：'+JSON.stringify(info));
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  for(const [view,file] of [['front','完整预览.png'],['orthofront','正面十二翼.png'],['top','俯视布局.png'],['back','后侧双炮.png'],['orthoside','侧面原案.png'],['controller','主控接口.png']]){
    await page.evaluate(view=>window.reviewApi.setView(view),view);
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await style.evaluate(e=>e.remove());
  await page.evaluate(()=>{
    const m=document.querySelector('[data-material]');m.checked=false;m.dispatchEvent(new Event('change'));
    const g=document.getElementById('showGlass');g.checked=false;g.dispatchEvent(new Event('change'));
    const l=document.getElementById('layer');l.value=150;l.dispatchEvent(new Event('input'));
  });
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='150');
  await page.evaluate(()=>{
    document.querySelectorAll('[data-material]').forEach(e=>{e.checked=true;e.dispatchEvent(new Event('change'));});
    window.reviewApi.setView('front');
  });
  if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
  const receipt={passed:true,headless:true,desktop_used:false,game_started:false,info,screenshots:6,
    material_glass_layer_controls_verified:true,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({passed:true,blocks:info.blocks,instances:info.instances,screenshots:6}));
}finally{await browser.close();}
