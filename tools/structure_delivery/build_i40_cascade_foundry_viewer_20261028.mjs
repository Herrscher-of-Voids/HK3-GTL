/** I40真实MC材质评审；复用表面合并及按需绘制管线，不复用旧建筑几何。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I40候选交付目录');
const output=path.resolve(process.argv[2]),view=path.join(output,'i40');
const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i39_unmanned_relay_viewer_v1_20261027.mjs'),'utf8');
const boundary=template.indexOf('const dataJs=');
if(boundary<0)throw new Error('共享渲染器入口变化');
let engine=template.slice(0,boundary).replaceAll('i39','i40').replaceAll('I39','I40')
  .replaceAll('无人航路中继','文明奇观材料合成')
  .replaceAll('偏馈碟阵与双轨整备站','四系贯流合成工场')
  .replaceAll('调度楼材质近景','质检桥材质近景')
  .replace("const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');",`const root=${JSON.stringify(root)};`);
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const dataJs=await fs.readFile(path.join(view,'data.js'),'utf8');
const encoded=JSON.parse(dataJs.slice('window.HK3_PAYLOAD='.length,-1));
const payload=JSON.parse(gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
const {data,audit}=payload;
if(data.key!=='i40'||data.controller[0]!==Math.floor((data.size[0]-1)/2))throw new Error('I40编号或主控中心错误');
if(payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length)throw new Error('I40材质索引错误');
const oldPage=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=oldPage.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('评审页基础样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const [w,h,d]=data.size,p=data.controller;
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I40 · ${esc(data.title)} · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #b19aba;background:#302739;color:#eee5f0}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I40交付总览</a><h1>I40 · ${esc(data.title)} V1</h1><div>WFV / V13 / tier27 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体方块 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I40四系贯流合成工场真实实体三维预览"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">后部四座独立反应塔连入前侧稳定化与成品长廊：导能、约束、重构、认知四系分料分流，只共享检测采样。主控嵌入居中质检桥，工艺接口齐平融入各自机匣。待审，未批准、未实装。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧加料桥</button><button data-view="top">俯视工艺分线</button><button data-view="inside">内部剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">质检桥材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">工艺分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>四系贯流合成工场</summary><p>${esc(data.description)}</p><p>每系分别备料、合成、稳定化、分级；废料按成分回流。输出导能带材与晶片、约束陶瓷、自组织复材、信息载体与传感阵列，不把认知材料解释为量产意识。</p><p>RN-WMS起步试片由前级GT/I16制备、I32检测；不得用本机或奇观自产材料反锁首次建造。I37外观留至最后，原有工况记录依赖保持规划。</p></details>
<details open><summary>主控与12处内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。合并面逐格重复真实MC纹理，保持全部原坐标；按高度分帧初始化、静止按需绘制。隐藏材质或剖切不补画内部切面。完整NBT与Schematic逐格回读一致。</p><p>结构仅为建筑表达；正式控制器、工艺、研究、生存获取与游戏运行未在本轮验收。全部结构完成后再测FCL/电脑版三种内存场景。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i40-v1-20261028"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('包含其他机器动态效果');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,render_on_demand:true}));
