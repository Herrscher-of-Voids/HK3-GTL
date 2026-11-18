/** I40浏览器可执行核验与完整材质截图，须先启动项目根目录HTTP服务。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.join(root,'deliveries/I40_文明奇观材料合成中心_四系贯流合成工场_V1_20261028');
const log=path.join(root,'logs/i40-cascade-foundry-20261028');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:2560,height:1700},deviceScaleFactor:1});
const errors=[],failures=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('response',r=>{if(r.status()>=400)failures.push({url:r.url(),status:r.status()});});
try{
  const base=process.argv[2]??'http://127.0.0.1:8810';
  const relative=path.relative(root,path.join(output,'i40/三维评审.html')).split(path.sep).map(encodeURIComponent).join('/');
  await page.goto(`${base}/${relative}`);
  await page.waitForFunction(()=>window.REVIEW_READY&&document.getElementById('status')?.textContent==='三维表面已就绪。',null,{timeout:60000});
  const info=await page.evaluate(()=>({title:document.title,blocks:window.REVIEW.audit.blocks,
    count:document.getElementById('counts').textContent,
    textures:window.REVIEW.materials.length,readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal}));
  if(info.blocks!==12697362||info.textures!==44||!info.readback)throw new Error('页面数据与最终结构身份不符');
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  for(const [view,filename] of [['front','完整预览.png'],['back','背面加料桥.png'],['controller','主控材质近景.png']]){
    await page.evaluate(name=>{window.reviewApi.setView(name);for(const id of ['showPorts','showZones']){const el=document.getElementById(id);el.checked=false;el.dispatchEvent(new Event('change'));}},view);
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(output,filename)});
  }
  await page.evaluate(()=>window.reviewApi.setView('top'));
  await page.evaluate(()=>{const el=document.getElementById('layer');el.value='100';el.dispatchEvent(new Event('input'));});
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='100');
  await page.evaluate(()=>{const el=document.getElementById('showGlass');el.checked=false;el.dispatchEvent(new Event('change'));});
  if(errors.length||failures.length)throw new Error(JSON.stringify({errors,failures}));
  await fs.writeFile(path.join(log,'browser-verification.json'),JSON.stringify({passed:true,...info,
    errors,failed_responses:failures,views:['front','back','controller','top'],
    layer_slider_tested:true,glass_toggle_tested:true,screenshots:['完整预览.png','背面加料桥.png','主控材质近景.png'],
    game_performance_tested:false,verified_at:new Date().toISOString()},null,2)+'\n','utf8');
  console.log(JSON.stringify({passed:true,output,errors,failed_responses:failures,blocks:info.blocks}));
}finally{await browser.close();}
