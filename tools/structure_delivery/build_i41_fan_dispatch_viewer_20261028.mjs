/** I41真实材质三维评审：仅复用渲染器，独立建筑数据和工艺说明。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I41交付目录');
const output=path.resolve(process.argv[2]),view=path.join(output,'i41');
const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i39_unmanned_relay_viewer_v1_20261027.mjs'),'utf8');
const boundary=template.indexOf('const dataJs=');
if(boundary<0)throw new Error('共享渲染器入口已变化');
let engine=template.slice(0,boundary).replaceAll('i39','i41').replaceAll('I39','I41')
  .replaceAll('无人航路中继','文明能源调度').replaceAll('偏馈碟阵与双轨整备站','弧幕母线与扇形负载港')
  .replaceAll('调度楼材质近景','调度厅材质近景')
  .replace("const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');",`const root=${JSON.stringify(root)};`);
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const js=await fs.readFile(path.join(view,'data.js'),'utf8');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i41'||p[0]!==Math.floor((w-1)/2)||payload.palette.length!==payload.materials.length)throw new Error('I41身份、主控或材质合同不符');
const prior=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=prior.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('基础评审样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I41 · ${esc(data.title)} · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #8db8c7;background:#253746;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I41交付总览</a><h1>I41 · ${esc(data.title)} ${esc(data.candidate_version??'V1')}</h1><div>IWV / V12 / tier26 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I41文明能源调度中枢真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">连续弧幕形成后部调度主脊，六路授权负载测控廊向前扇形展开，前置调度大厅沿中轴嵌入主控。只表达负载登记、授权调度与回执记录；不制造能源、不替代I38记账。待审，未批准、未实装。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]，整宽第${p[0]+1}格。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后部母线与检修层</button><button data-view="top">扇形拓扑俯视</button><button data-view="inside">内部剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">调度厅材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">设备分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>弧幕母线与扇形负载港</summary><p>${esc(data.description)}</p><p>实际高度由连续抛物弧顶和内部设备层确定，没有孤立增高塔。六条负载廊内设分层测控机架、隔离保护、授权状态观察窗口及实际维护空间。</p></details>
<details open><summary>基础控制与高级研究分开</summary><p>RN-CED：基础登记、查看、授权手动开停。RN-ELC：在CED与WME前置后才开放优先级与告警，首机不默认自动排程。研究许可与账户/机器授权独立，个人UUID账本不因团队研究合并。</p><p>I01-4负责采集，I38负责HKE整流与合法记账，I41负责文明负载调度。输入真实入账记录、已可用HW负载和绑定人授权，输出调度回执、历史与异常记录；不制造能源、不充值、不重复结算、不接管未授权设备，不成为无线能源必经中转。</p></details>
<details open><summary>主控与6处内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。逐格重复真实MC纹理、保持全部原坐标，按高度分帧初始化、静止按需绘制。隐藏玻璃或剖切不补画内部切面。</p><p>建筑仅为功能表达。正式控制器、Pattern、研究、个人账本和授权运行尚未验收。全部结构完成后再测FCL/电脑版三场景内存。I40获批为batch-10第1/5台；I41尚未批准不计数，I37留最后。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i41-v1-20261028"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('混入其他机器特效');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,render_on_demand:true}));
