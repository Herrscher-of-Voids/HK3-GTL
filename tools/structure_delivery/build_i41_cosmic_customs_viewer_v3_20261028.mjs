/** I41 V3真实MC材质评审：仅复用既有引擎，概念分区不代表新增游戏能力。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I41 V3交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i41');
const js=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!js.startsWith('window.HK3_PAYLOAD=')||!js.endsWith(';'))throw new Error('I41 V3载荷格式错误');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i41'||data.candidate_version!=='V3'||data.size.join(',')!=='529,289,529'||p.join(',')!=='264,24,0'
  ||p[0]!==Math.floor((w-1)/2)||data.ports.length!==6||data.zones.length!==12
  ||payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length
  ||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('I41 V3身份、尺寸、中线、分区、接口或材质合同不符');

const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i41_fan_dispatch_viewer_20261028.mjs'),'utf8');
const boundary=template.indexOf('const js=await fs.readFile');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
const launch="await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));";
if(boundary<0||!template.slice(0,boundary).includes(rootLine)||!template.slice(0,boundary).includes(launch))throw new Error('既有I41引擎入口已变化');
let engine=template.slice(0,boundary).replace(rootLine,`const root=${JSON.stringify(root)};`)
  .replaceAll('弧幕母线与扇形负载港','宇宙海关与十二港约束环城')
  .replaceAll('调度厅材质近景','调度法庭材质近景');
engine=engine.replace(launch,"engine=engine.replaceAll('宇宙海关与十二港约束环城V1-三维预览.png','宇宙海关与十二港约束环城V3-三维预览.png');\n"+launch);
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const prior=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=prior.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I41 · ${esc(data.title)} V3 · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #74b5bd;background:#25313d;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I41交付总览</a><h1>I41 · ${esc(data.title)} V3</h1><div>IWV / V12 / tier26 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I41宇宙海关与十二港约束环城真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">退台环城围绕黑色约束笼，十二港通过窄青色能流廊连接内环；上部配平环、下部熵流环和前端调度法庭形成一座宇宙能源海关。笼、港与清算区均为建筑隐喻，I41仍只负责授权负载调度。候选未批准、未部署。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平嵌入调度法庭连续外墙。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧环城与服务港</button><button data-view="top">十二港环城俯视</button><button data-view="inside">环城内部剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">调度法庭材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">十二建筑分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>宇宙海关与十二港约束环城</summary><p>${esc(data.description)}</p><p>中央展示核由黑色笼梁、细格栅、锁定环和子午框组织；狭窄青色能流作为径向视觉引导，保持空腔与检修层可辨。上下配平与熵流设施接入城体，调度法庭承担正面入口和操作面。</p><p>十二分区表示建筑组织和定位标签，不新增十二个正式控制器，也不代表已实现空间分区渲染或分区成型。</p></details>
<details open><summary>调度职责与概念边界</summary><p>RN-CED对应基础登记、查看和授权手动开停；RN-ELC在CED与WME前置后才开放优先级和告警，首机不默认自动排程。研究许可、个人UUID账本与机器授权独立。</p><p>I01-4负责采集，I38负责HKE整流和合法记账，I41负责已授权文明负载的登记、查看与调度回执。约束笼不捕获世界泡，能源港不制造或充值能源，熵债清算区不新增熵债规则；不重复结算、不接管未授权设备、不成为无线能源必经中转。</p></details>
<details open><summary>主控与6处内嵌接口</summary><div id="portButtons"></div><div id="ports"></div><p>钻石块标记主控；工业接口块标记候选位置，均不代表已实现正式能力。</p></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。真实MC纹理逐格重复，保留全部原坐标；按高度分帧初始化，静止按需绘制。隐藏玻璃或剖切不补画内部切面。本页资源位于交付目录，可直接以file协议打开，不依赖外网。</p><p>正式控制器、Pattern、研究、个人账本、授权运行及生存获取尚未验收；浏览器表现不代表电脑版或FCL游戏性能。I41未批准，不计入批次；I40仍为batch-10第1/5台，I37留最后。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i41-v3-20261028"></script></html>`;
const requiredIds=['stage','loading','labels','viewName','layerValue','layer','showGlass','showPorts','showPaths','showZones','reset','saveImage','counts','status','portButtons','ports','materials','checks'];
if(requiredIds.some(id=>!page.includes(`id="${id}"`))||/弧幕|六路|扇形/.test(page))throw new Error('I41 V3评审控件缺失或混入旧版造型文案');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('混入其他机器特效');
if(!generated.includes('reviewApi'))throw new Error('既有reviewApi接口缺失');
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
console.log(JSON.stringify({output,view,candidate_version:'V3',blocks:payload.blockCount,faces:audit.viewer_surface_faces,zones:data.zones.length,ports:data.ports.length,render_on_demand:true,approved:false,installed:false}));
