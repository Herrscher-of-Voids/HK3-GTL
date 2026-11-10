/** 复用离线截图核验，仅替换V2目录与修复后的实体数量。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
let source=await fs.readFile(path.join(root,'tools/structure_delivery/capture_mx_c01_converter_v1_20261107.mjs'),'utf8');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(!source.includes(rootLine)||!source.includes('info.blocks!==10443'))throw new Error('原查看器核验合同已变化');
source=source.replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('_V1_20261107','_V2_20261107').replaceAll('-v1-20261107','-v2-20261107')
  .replace('info.blocks!==10443','info.blocks!==10453');
await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
