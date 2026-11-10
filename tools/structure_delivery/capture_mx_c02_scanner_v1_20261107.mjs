/** 复用离线查看器核验，检查扫描仪完整材质、视角和控件。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
let source=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(!source.includes(rootLine)||!source.includes('info.blocks!==10443'))throw new Error('原查看器核验合同已变化');
source=source.replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107','MAX复制系统_扫描仪_三环谱系扫描台_V1_20261107')
  .replaceAll('mx-c01-converter','mx-c02-scanner').replaceAll('mx-c01','mx-c02')
  .replace('info.blocks!==10443','info.blocks!==9796')
  .replace('info.materials!==13','info.materials!==14').replace('info.materialControls!==13','info.materialControls!==14')
  .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));")
  .replaceAll('后侧冷却.png','后侧分析.png');
await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
