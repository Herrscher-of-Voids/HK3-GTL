/** I36现实稳定锚：真实外露面、分帧初始化与静止按需绘制。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I36交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i36');
const legacyFolder=path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027');
let builder=await fs.readFile(path.join(legacyFolder,'生成脚本/build_i34_viewer_v1_20261027.mjs'),'utf8');
if(!builder.includes('const output = path.resolve(process.argv[2]);'))throw new Error('共享查看器输出参数已变化，拒绝错写目录');
builder=builder.replace('const output = path.resolve(process.argv[2]);',`const output = ${JSON.stringify(view)};`);
builder=builder.replaceAll('virtual:i34-imaginary-tree-array','virtual:i36-reality-anchor');
builder=builder.replaceAll('I34虚数之树观测预览','I36崩坏能现实稳定锚预览');
builder=builder.replaceAll('I34逐帧实例初始化补丁','I36逐帧实例初始化补丁');
builder=builder.replaceAll('树冠干涉观测院V1-三维预览.png','双叉谐振稳相井V1-三维预览.png');
builder=builder.replaceAll('后侧观测资料交接','后侧隔振与冷却机列');
if(!builder.includes('const oldHotPaths = '))throw new Error('共享查看器自检边界已变化');
builder=builder.replace('const oldHotPaths = ',`new Function('return (async()=>{'+source+'});');\nconst oldHotPaths = `);
if(!builder.includes('initializeMatrixChunk')||!builder.includes('requestRender=()=>'))throw new Error('轻量查看器缺少分帧初始化或按需绘制');
await fs.mkdir(view,{recursive:true});
await import('data:text/javascript;base64,'+Buffer.from(builder).toString('base64'));

const dataJs=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!dataJs.startsWith('window.HK3_PAYLOAD=')||!dataJs.endsWith(';'))throw new Error('I36候选载荷格式错误');
const encoded=JSON.parse(dataJs.slice('window.HK3_PAYLOAD='.length,-1));
const payload=JSON.parse(gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
const {data,audit}=payload;
if(data.key!=='i36'||data.controller[0]!==Math.floor((data.size[0]-1)/2))throw new Error('I36编号或主控居中坐标不符');
if(payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('材质或表面索引数量错误');
const oldPage=await fs.readFile(path.join(legacyFolder,'i34/三维评审.html'),'utf8');
const css=oldPage.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const [w,h,d]=data.size,p=data.controller,title=data.title??'崩坏能现实稳定锚 · 双叉谐振稳相井';
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I36 · ${escape(title)} V1</title><style>${css}
.candidate-note{padding:10px 12px;border-left:3px solid #b8c8ab;background:#26322d;color:#e7eee4}.locator{margin-top:12px}#stage{background:#111b28}</style>
<header><a href="../index.html">← I36交付总览</a><h1>I36 · ${escape(title)} V1</h1><div>QSV · V05 / ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体方块 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I36双叉谐振现实稳定锚真实实体三维预览"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">本轮为建筑外观候选，尚未批准、尚未接入实例。所有实体按同一逐格几何导出；双叉现实基准、贯入稳相芯、开敞沉井与隔振冷却机列共同表达局部现实稳定工程。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平融入主体设备外壳。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧隔振与冷却机列</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>双叉谐振稳相井</summary><p>${escape(data.description)}</p><p>现实稳定锚通过供能、稳定介质与覆盖设定维持局部现实稳定，表达负载抑制、隔振与运行状态读出。覆盖状态与运行记录分别表达，不将覆盖能力当成可制造的万能零件。</p><p>本机不凭空发电，不提供全维度豁免或传送能力；建筑造型、管线与基准装置只表达工艺意图，正式控制器、Pattern、覆盖判定和生存获取仍须另行验收。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="${escape(data.name)}.nbt">NBT</a> · <a href="${escape(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>仅提交${audit.viewer_surface_faces.toLocaleString()}片真实外露面；按高度分帧初始化，静止时按需重绘。隐藏材质或剖切仅调整现有外露面，不补画内部剖切面。候选未批准、未实装；游戏运行及阶段可达性另行验收。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('I36错误地包含其他机器的动态效果');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,projection:false,render_on_demand:true}));
