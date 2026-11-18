/** I41环城候选的离线浏览器核验、真实材质全景与近景。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const folders=await fs.readdir(path.join(root,'deliveries'));
const name=folders.find(x=>x.startsWith('I41_')&&x.includes('_V3_20261028'));
if(!name)throw new Error('I41 V3交付目录不存在');
const output=path.join(root,'deliveries',name),log=path.join(root,'logs/i41-cosmic-customs-v3-20261028');
const expected=JSON.parse(await fs.readFile(path.join(output,'manifest.json'),'utf8'));
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:2560,height:1700},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
  await page.goto(pathToFileURL(path.join(output,'i41/三维评审.html')).href);
  await page.waitForFunction(()=>window.REVIEW_READY&&document.getElementById('status')?.textContent==='三维表面已就绪。',null,{timeout:120000});
  const info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,textures:window.REVIEW.materials.length,
    readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
    rendered_quads:window.REVIEW.audit.viewer_rendered_quads,draw_calls:window.reviewApi.renderer.info.render.calls,
    title:document.title,viewport:innerWidth,content:document.documentElement.scrollWidth}));
  if(info.blocks!==expected.blocks||info.textures!==43||!info.readback)throw new Error('结构身份或真实材质合同不符');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  const views=[['front','完整预览.png'],['back','后部母线.png'],['top','十二港俯视.png'],['controller','主控材质近景.png']];
  for(const [view,file] of views){
    await page.evaluate(name=>{
      window.reviewApi.setView(name);
      for(const id of ['showPorts','showZones']){const el=document.getElementById(id);el.checked=false;el.dispatchEvent(new Event('change'));}
    },view);
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(output,file)});
  }
  await style.evaluate(e=>e.remove());
  await page.evaluate(()=>{
    window.reviewApi.setView('inside');
    const e=document.getElementById('layer');e.value='112';e.dispatchEvent(new Event('input'));
  });
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='112');
  await page.evaluate(()=>{const e=document.getElementById('showGlass');e.checked=false;e.dispatchEvent(new Event('change'));});
  await page.evaluate(()=>window.reviewApi.setView('front'));
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:path.join(log,'评审页面.png')});
  const index=await browser.newPage();
  await index.goto(pathToFileURL(path.join(output,'index.html')).href);
  const links=await index.locator('a[href]').evaluateAll(es=>es.map(e=>e.href));
  const broken=[];
  for(const l of links.filter(x=>x.startsWith('file:'))){try{await fs.access(fileURLToPath(l.split('#')[0]));}catch{broken.push(l);}}
  if(errors.length||broken.length)throw new Error(JSON.stringify({errors,broken}));
  const result={passed:true,...info,errors,broken_local_links:broken,offline_file_html_tested:true,
    views:views.map(x=>x[0]),layer_slider_tested:true,glass_toggle_tested:true,
    screenshots:views.map(x=>x[1]),approved:false,installed:false,game_performance_tested:false,
    verified_at:new Date().toISOString()};
  await fs.writeFile(path.join(log,'browser-verification.json'),JSON.stringify(result,null,2)+'\n','utf8');
  console.log(JSON.stringify(result));
}finally{await browser.close();}
