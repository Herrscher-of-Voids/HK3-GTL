/** Offline full-voxel previews; no game window or desktop control. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W03_C3_眼形莫比乌斯_四方案_20261108');
const log=path.join(root,'logs/w03-eye-c3-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const receipts=[];
try {
  for(const code of ['3H','3U','5H','5U']) {
    const target=path.join(out,code),errors=[],failed=[],external=[];
    const page=await browser.newPage({viewport:{width:1800,height:1800},deviceScaleFactor:1});
    page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
    page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    const manifest=JSON.parse(await fs.readFile(path.join(target,'manifest.json'),'utf8'));
    await page.goto(pathToFileURL(path.join(target,'w03/三维评审.html')).href);
    await page.waitForFunction(()=>window.C3_READY,null,{timeout:180000});
    const info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,
      readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
      materials:document.querySelectorAll('[data-material]').length,ports:document.querySelectorAll('[data-port]').length,
      intersections:window.REVIEW.audit.component_clearance.intersection_pairs_after,
      rings:window.REVIEW.data.rings.length,comparison:window.REVIEW.data.comparison,
      complete:[...function*(){const a=[];window.reviewApi.scene.traverse(o=>{if(o.userData.indices)a.push(o.userData.initialized===o.userData.indices.length);});yield* a;}()].every(Boolean)}));
    if(info.blocks!==manifest.blocks||!info.readback||!info.complete||info.materials!==15||info.ports!==8||info.intersections!==0||info.rings!==Number(code[0]))throw new Error(JSON.stringify(info));
    await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
    for(const [view,file] of [['front','完整预览.png'],['orthofront','正面眼形.png'],['right','侧面层次.png'],['top','俯视布局.png']]) {
      await page.evaluate(view=>window.reviewApi.setView(view),view);
      await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
      await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
      await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
      await page.locator('#stage').screenshot({path:path.join(target,file)});
    }
    await page.evaluate(()=>{const a=window.reviewApi,o=window.REVIEW.data.blueprint_to_export_offset_xyz;
      a.controls.target.set(440+o[0],478+o[1],264+o[2]);a.camera.position.set(150+o[0],700+o[1],-850+o[2]);
      a.camera.zoom=2.2;a.controls.update();a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);});
    await page.locator('#stage').screenshot({path:path.join(target,'环带近景.png')});
    if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
    receipts.push({code,passed:true,headless:true,desktop_used:false,game_started:false,info,screenshots:5,errors,failed,external});
    await page.close();console.log(JSON.stringify({code,passed:true}));
  }
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify({passed:true,variants:receipts},null,2)+'\n');
} finally {await browser.close();}
