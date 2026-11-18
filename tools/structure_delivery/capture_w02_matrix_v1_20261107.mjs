/** W02离线真实材质预览核验；不操作桌面，不启动游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
let source=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(!source.includes(rootLine)||!source.includes('info.blocks!==10443'))throw new Error('原查看器核验合同已变化');
source=source.replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('MAX复制系统_供料机_双罐脉冲转化厂_V1_20261107','W02_万象自律工业矩阵_六院构造中庭_V1_20261107')
  .replaceAll('mx-c01-converter','w02-matrix').replaceAll('mx-c01','w02')
  .replace('info.blocks!==10443','info.blocks!==27230303')
  .replace('info.materials!==13','info.materials!==45').replace('info.materialControls!==13','info.materialControls!==45')
  .replace('info.ports!==6','info.ports!==8').replace('info.portControls!==6','info.portControls!==8')
  .replace('timeout:60000','timeout:180000')
  .replace("e.value='17'","e.value='133'")
  .replace("document.getElementById('showPorts').checked=false;","document.getElementById('showPorts').checked=false;document.getElementById('showPorts').dispatchEvent(new Event('change'));")
  .replaceAll('后侧冷却.png','后侧设备.png');
await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
