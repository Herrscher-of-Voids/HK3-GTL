import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W03_C4_五环锁芯与立体晶云_20261108');
const log=path.join(root,'logs/w03-core-aim-c4-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1800},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
try {
  const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
  await page.goto(pathToFileURL(path.join(out,'w03/三维评审.html')).href);
  await page.waitForFunction(()=>window.C4_READY,null,{timeout:180000});
  const info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,
    readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
    rings:window.REVIEW.data.rings.length,aiming:window.REVIEW.data.aiming,cloud:window.REVIEW.data.crystal_cloud,
    intersections:window.REVIEW.audit.component_clearance.intersection_pairs_after,
    ports:document.querySelectorAll('[data-port]').length,
    complete:[...function*(){const a=[];window.reviewApi.scene.traverse(o=>{if(o.userData.indices)a.push(o.userData.initialized===o.userData.indices.length);});yield* a;}()].every(Boolean)}));
  if(info.blocks!==manifest.blocks||!info.readback||!info.complete||info.rings!==5||info.intersections!==0||info.ports!==8||!info.aiming.all_six_axes_exactly_collinear_with_core||info.cloud.lower_central_count<8)throw new Error(JSON.stringify(info));
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  for(const [view,file,axes] of [['front','完整预览.png',false],['orthofront','正面眼形.png',false],['orthoside','侧面晶云.png',false],['top','俯视分布.png',false],['front','六矛指向.png',true],['orthoside','侧面指向.png',true]]) {
    await page.evaluate(({view,axes})=>{window.reviewApi.setView(view);window.C4AimOverlay.show(axes);},{view,axes});
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(out,file)});
  }
  await page.getByRole('button',{name:'隐藏六矛指向线',exact:true}).click();
  if(await page.getByRole('button',{name:'显示六矛指向线',exact:true}).count()!==1)throw new Error('Aim toggle failed');
  if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
  const receipt={passed:true,headless:true,desktop_used:false,game_started:false,info,screenshots:6,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({passed:true,blocks:info.blocks,screenshots:6}));
} finally {await browser.close();}
