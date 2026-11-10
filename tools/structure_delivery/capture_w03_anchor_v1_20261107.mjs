/** W03独立V1真实材质离线核验；不操作游戏或桌面。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const folder='W03_穹界虚数锚定环_四极折界门庭_V1_20261107';
const manifest=JSON.parse(await fs.readFile(path.join(root,'deliveries',folder,'manifest.json'),'utf8'));
let source=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(!source.includes(rootLine)||!source.includes('info.blocks!==10443'))throw new Error('原查看器核验合同已变化');
source=source.replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107',folder)
  .replaceAll('mx-c01-converter-v1','w03-anchor-v1').replaceAll('mx-c01','w03')
  .replace('info.blocks!==10443',`info.blocks!==${manifest.blocks}`)
  .replace('info.materials!==13','info.materials!==46').replace('info.materialControls!==13','info.materialControls!==46')
  .replace('info.ports!==6','info.ports!==8').replace('info.portControls!==6','info.portControls!==8')
  .replace('timeout:60000','timeout:180000').replace("e.value='17'","e.value='167'")
  .replace('const info=await page.evaluate',"await page.waitForFunction(()=>window.W03_READY);\n  const info=await page.evaluate")
  .replace("['inside','逐层剖切.png']","['inside','逐层剖切.png'],['anchor','锚座内腔.png']")
  .replace('await style.evaluate(e=>e.remove());',"await page.locator('#completeView').click({force:true});\n  await style.evaluate(e=>e.remove());")
  .replace('await page.setViewportSize({width:1440,height:1000});',`await page.setViewportSize({width:1440,height:1000});
  await page.locator('#anchorView').click();
  if(!await page.evaluate(()=>{const i=window.REVIEW.materials.findIndex(m=>m.state==='hk3gtl:voltage_machine_casing_hcv');return !document.querySelector('[data-material="'+i+'"]').checked&&!document.getElementById('showGlass').checked;}))throw new Error('锚座内腔按钮未隐藏主体和玻璃');
  await page.locator('#completeView').click();
  if(!await page.evaluate(()=>[...document.querySelectorAll('[data-material]')].every(e=>e.checked)&&document.getElementById('showGlass').checked))throw new Error('完整外观按钮未恢复全部材质');`)
  .replace('toggles_and_layer_checked:true','toggles_and_layer_checked:true,anchor_preset_checked:true,complete_restore_checked:true')
  .replaceAll('screenshots:5','screenshots:6')
  .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));")
  .replaceAll('后侧冷却.png','后侧设备.png');
await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
