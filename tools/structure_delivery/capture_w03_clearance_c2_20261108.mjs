/** 离线检查C2的正圆正视、整体轮廓与构件净空，不操作游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.join(root,'deliveries/W03_C方案_正圆与净空_C2_20261108');
const log=path.join(root,'logs/w03-clearance-c2-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:2200,height:1700},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
try{
  const manifest=JSON.parse(await fs.readFile(path.join(output,'manifest.json'),'utf8'));
  await page.goto(pathToFileURL(path.join(output,'w03/三维评审.html')).href);
  await page.waitForFunction(()=>window.C2_READY,null,{timeout:180000});
  const info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
    materials:document.querySelectorAll('[data-material]').length,ports:document.querySelectorAll('[data-port]').length,
    intersections:window.REVIEW.audit.component_clearance.intersection_pairs_after,round:window.REVIEW.data.rings[0]}));
  if(info.blocks!==manifest.blocks||info.materials!==manifest.unique_materials||!info.readback||info.ports!==8||info.intersections!==0||info.round.radius_x!==info.round.radius_y)throw new Error('完整载荷、正圆或构件核验不符');
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  for(const [view,file] of [['front','完整预览.png'],['back','后侧设备.png'],['top','俯视布局.png'],['controller','主控材质近景.png'],['orthofront','正圆正视.png']]){
    await page.evaluate(view=>window.reviewApi.setView(view),view);
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    if(view==='orthofront')await page.evaluate(()=>{const a=window.reviewApi,d=window.REVIEW.data,o=d.blueprint_to_export_offset_xyz;
      const x=336+o[0],y=d.rings[0].center_blueprint[1]+o[1],z=264+o[2];a.controls.target.set(x,y,z);a.camera.position.set(x,y,z-1800);a.camera.zoom=1;a.controls.update();a.camera.updateProjectionMatrix();});
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(output,file)});
  }
  await page.evaluate(()=>{const a=window.reviewApi,d=window.REVIEW.data,o=d.blueprint_to_export_offset_xyz;
    a.controls.target.set(336+o[0],350+o[1],264+o[2]);a.camera.position.set(-500+o[0],640+o[1],-500+o[2]);a.camera.zoom=1.6;a.controls.update();a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);});
  await page.locator('#stage').screenshot({path:path.join(output,'局部净空.png')});
  for(const view of ['front','right','back','top','orthofront','orthoside','texture']){
    await page.evaluate(view=>window.reviewApi.setView(view),view);
    if(!await page.evaluate(()=>[...window.reviewApi.camera.position.toArray(),...window.reviewApi.camera.projectionMatrix.elements].every(Number.isFinite)))throw new Error('视角无效');
  }
  if(errors.length||failed.length||external.length)throw new Error(JSON.stringify({errors,failed,external}));
  const receipt={passed:true,headless:true,desktop_used:false,game_started:false,info,views_checked:7,screenshots:6,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await browser.close();}
