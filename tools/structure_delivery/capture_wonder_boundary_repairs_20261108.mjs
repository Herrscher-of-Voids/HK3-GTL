/** 四个完整边界候选的离线真实表面核验，不操作桌面或游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const base=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
for(const version of ['V2','V3','V4','V5']){
  const folder='W03_完整几何边界修复_20261108/'+version;
  const m=JSON.parse(await fs.readFile(path.join(root,'deliveries',folder,'manifest.json'),'utf8'));
  const source=base.replace("const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');",`const root=${JSON.stringify(root)};`)
    .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107',folder)
    .replaceAll('mx-c01-converter-v1-20261107','wonder-clipping-audit-20261108/'+version).replaceAll('mx-c01','w03')
    .replace('info.blocks!==10443',`info.blocks!==${m.blocks}`)
    .replaceAll('info.materials!==13',`info.materials!==${m.unique_materials}`)
    .replaceAll('info.materialControls!==13',`info.materialControls!==${m.unique_materials}`)
    .replace('info.ports!==6',`info.ports!==${m.ports.length}`).replace('info.portControls!==6',`info.portControls!==${m.ports.length}`)
    .replace('timeout:60000','timeout:180000').replace("e.value='17'",`e.value='${Math.floor(m.size[1]*.59)}'`)
    .replace('const info=await page.evaluate','await page.waitForFunction(()=>window.BOUNDARY_READY);\n  const info=await page.evaluate')
    .replaceAll('后侧冷却.png','后侧设备.png')
    .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));")
    .replace('await style.evaluate(e=>e.remove());',`await page.evaluate(()=>window.reviewApi.setView('front'));\n  await style.evaluate(e=>e.remove());`);
  await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
}
