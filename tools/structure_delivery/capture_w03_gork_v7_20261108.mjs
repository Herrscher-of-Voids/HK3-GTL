/** 完整实体及可关闭能流概念预览的离线核验，不操作桌面或游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const folder='W03_穹界虚数锚定环_四锚穹盖_Gork原案_V7_20261108';
const m=JSON.parse(await fs.readFile(path.join(root,'deliveries',folder,'manifest.json'),'utf8'));
let s=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
s=s.replace("const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');",`const root=${JSON.stringify(root)};`)
 .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107',folder)
 .replaceAll('mx-c01-converter-v1-20261107','w03-gork-v7-20261108').replaceAll('mx-c01','w03')
 .replace('info.blocks!==10443',`info.blocks!==${m.blocks}`).replace('info.materials!==13',`info.materials!==${m.unique_materials}`)
 .replace('info.materialControls!==13',`info.materialControls!==${m.unique_materials}`)
 .replace('info.ports!==6',`info.ports!==${m.ports.length}`).replace('info.portControls!==6',`info.portControls!==${m.ports.length}`)
 .replace('timeout:60000','timeout:180000').replace("e.value='17'",`e.value='${Math.floor(m.size[1]*.59)}'`)
 .replace('const info=await page.evaluate','await page.waitForFunction(()=>window.GORK_PREVIEW_READY);\n  const info=await page.evaluate')
 .replaceAll('后侧冷却.png','后侧设备.png')
 .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));");
const effect=String.raw`
  await page.locator('#energyPreview').check();
  const before=await page.evaluate(()=>window.reviewApi.energyPreview.diagnostics());
  await page.waitForFunction(()=>window.reviewApi.energyPreview.diagnostics().frames>=8&&window.reviewApi.energyPreview.diagnostics().time>.25);
  const moving=await page.evaluate(()=>window.reviewApi.energyPreview.diagnostics());
  if(!moving.active||!moving.staticHaloHidden||!moving.overlayVisible||moving.roofStars!==480||moving.roofHalos!==3||before.firstStarScale===moving.firstStarScale||JSON.stringify(before.rotation)===JSON.stringify(moving.rotation)||JSON.stringify(before.firstParticle)===JSON.stringify(moving.firstParticle))throw new Error('能流、薄环或星空未实际运动');
  const energyStyle=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  await page.setViewportSize({width:2200,height:1500});
  await page.evaluate(()=>{document.getElementById('coreView').click();window.reviewApi.energyPreview.freezeAt(5);});
  await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
  await page.evaluate(()=>window.reviewApi.energyPreview.freezeAt(5));
  await page.locator('#stage').screenshot({path:path.join(output,'能量演示.png')});
  await energyStyle.evaluate(e=>e.remove());
  await page.locator('#energyPreview').uncheck();
  let restored=await page.evaluate(()=>window.reviewApi.energyPreview.diagnostics());
  if(restored.active||restored.overlayVisible||restored.staticHaloHidden)throw new Error('关闭演示未恢复静态实体');
  await page.locator('#energyPreview').check();
  await page.locator('#layer').evaluate(e=>{e.value='160';e.dispatchEvent(new Event('input'));});
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='160');
  if(await page.evaluate(()=>window.reviewApi.energyPreview.diagnostics().active))throw new Error('剖切没有自动关闭概念叠加层');
  await page.locator('#energyPreview').check();
  await page.locator('[data-material="0"]').uncheck();
  if(await page.evaluate(()=>window.reviewApi.energyPreview.diagnostics().active))throw new Error('材质筛选没有自动关闭概念叠加层');
  await page.locator('[data-material="0"]').check();
  await page.locator('#layer').evaluate(e=>{e.value=String(window.REVIEW.data.size[1]-1);e.dispatchEvent(new Event('input'));});
  await page.evaluate(()=>window.reviewApi.setView('front'));
  const energyChecks={routes:moving.routes,particles:moving.particles,roof_stars:moving.roofStars,roof_halos:moving.roofHalos,star_twinkle:true,actual_motion:true,rotation:true,disable_restores_static:true,layer_stops_overlay:true,material_filter_stops_overlay:true};
`;
const marker='  if(errors.length||failed.length||external.length)';
if(!s.includes(marker))throw new Error('共享离线核验合同已变化');
s=s.replace(marker,effect+'\n'+marker)
 .replaceAll('screenshots:5','screenshots:6')
 .replace('toggles_and_layer_checked:true','toggles_and_layer_checked:true,energy_preview:energyChecks');
await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
