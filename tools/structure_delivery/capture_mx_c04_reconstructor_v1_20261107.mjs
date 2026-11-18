/** 四臂工坊离线预览核验：不操作桌面，不启动游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
let source=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(!source.includes(rootLine)||!source.includes('info.blocks!==10443'))throw new Error('原查看器核验合同已变化');
source=source.replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107','MAX复制系统_重构机_四臂重构工坊_V1_20261107')
  .replaceAll('mx-c01-converter','mx-c04-reconstructor').replaceAll('mx-c01','mx-c04')
  .replace('info.blocks!==10443','info.blocks!==12625')
  .replace('info.materials!==13','info.materials!==16').replace('info.materialControls!==13','info.materialControls!==16')
  .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));")
  .replaceAll('后侧冷却.png','后侧设备.png');
await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
