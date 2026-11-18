/** I43环境验收中心：复用离线真实MC材质引擎，替换为独立数据和职责说明。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I43交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i43');
const js=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!js.startsWith('window.HK3_PAYLOAD=')||!js.endsWith(';'))throw new Error('I43载荷格式错误');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i43'||data.candidate_version!=='V1'||data.name!=='hk3gtl-i43-environment-acceptance-v1-20261028'
  ||data.size.join(',')!=='641,297,481'||p.join(',')!=='320,24,0'||p[0]!==Math.floor((w-1)/2)||data.ports.length!==8
  ||payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length
  ||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('I43身份、尺寸、中线、接口或材质合同不符');

const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i41_fan_dispatch_viewer_20261028.mjs'),'utf8');
const boundary=template.indexOf('const js=await fs.readFile');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(boundary<0||!template.slice(0,boundary).includes(rootLine))throw new Error('共享真实材质引擎入口已变化');
let engine=template.slice(0,boundary).replaceAll('i41','i43').replaceAll('I41','I43')
  .replaceAll('文明能源调度','文明工程验收').replaceAll('弧幕母线与扇形负载港','开瓣环境穹舱与六轴验收台')
  .replaceAll('调度厅材质近景','计量前厅材质近景').replace(rootLine,`const root=${JSON.stringify(root)};`);
const launch="await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));";
if(!engine.includes(launch))throw new Error('共享材质引擎启动边界已变化');
engine=engine.replace(launch,"engine=engine.replaceAll('后侧天线与轴座','试验舱后方与热工设备');\n"+launch);
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const prior=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=prior.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sourceCounts=Object.fromEntries(['GTCEu','GTL Core','其他模组','原版','项目WSV主机壳','主控标记','工业接口标记'].map(name=>[name,0]));
for(const [state,count] of Object.entries(audit.palette)){
  const category=state==='minecraft:diamond_block'?'主控标记':state==='hk3gtl:industrial_port_casing'?'工业接口标记'
    :state==='hk3gtl:voltage_machine_casing_wsv'?'项目WSV主机壳':state.startsWith('gtceu:')?'GTCEu'
    :state.startsWith('gtlcore:')?'GTL Core':state.startsWith('minecraft:')?'原版':'其他模组';
  sourceCounts[category]+=count;
}
if(Object.values(sourceCounts).reduce((sum,count)=>sum+count,0)!==payload.blockCount
  ||Object.entries(audit.material_source_counts??{}).some(([name,count])=>sourceCounts[name]!==count))throw new Error('I43材料来源分类与实体总量冲突');
const ordinaryBlockCount=payload.blockCount-sourceCounts['主控标记']-sourceCounts['工业接口标记'];
const sourceRows=Object.entries(sourceCounts).map(([name,count])=>`<tr><td>${name}</td><td>${count.toLocaleString()}</td><td>${name.endsWith('标记')?'标记单列':(count/ordinaryBlockCount*100).toFixed(3)+'%'}</td></tr>`).join('');
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I43 · ${esc(data.title)} V1 · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #9cb5d3;background:#25313d;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I43交付总览</a><h1>I43 · ${esc(data.title)} V1</h1><div>WSV / V14 / tier28 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I43开瓣环境穹舱与六轴验收台真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">单座纵向环境穹舱覆盖六轴受检平台，上部半圆拱壳与沿地轨向外展开的两扇厚型试验门定义轮廓；两侧独立计量走廊连接低阶梯热工与流体设备房。I43检测真实样件和运行证据；候选未批准、未部署。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平嵌入低前厅连续外墙。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">试验舱后方与热工设备</button><button data-view="top">试验舱俯视</button><button data-view="inside">受检平台与仪器剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">计量前厅材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">检验分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>开瓣环境穹舱与六轴验收台</summary><p>${esc(data.description)}</p><p>以受检对象、环境控制和测量路径确定轮廓：中央六轴验收台、开瓣厚门、两侧仪器走廊与热工设备共同组成工程验收中心。分区标签只说明建筑组织，不代表新增正式控制器或空间分区渲染。</p></details>
<details open><summary>输入真实样件，输出可核对的验收档案</summary><p>工程样件、实际运行记录与测试介质进入构件检验、供能热工及流体工况、维系与空间工程核验；针对奇观和既有仿制舰核对其真实运行证据，不合格项经过复测，形成运行合格报告、故障清单和验收档案。</p><p>I40提供专用功能材料，I42预制专用构件，玩家实际建设独立工程，I41调度合法能源负载，I43承担检验。报告不能凭空制造材料、重复授予成果或替代实体工程；W15汇总最终资格，I43不另开终审入口。</p></details>
<details open><summary>方法研究与实体运行证明分别核验</summary><p>RN-CEE对应文明工程验收方法。前级I32使用已知合格与不合格基准样件校准检测方法，关联I42实际预制样件、I37维系记录和前级测量工装；这些形成方法证据，不能代替任何奇观的实际运行证明。I43首机不要求检验自己。</p><p>奇观正式建造和运行仍须分别核对专项研究与二审条件。验收应检测具体功能、输入输出和真实工况，持有控制器、站在附近或通用空转计时均不能冒充运行证据。WSV是已授权方案的本机制作映射，暂定研究实验电压不能替代机器定阶；配方、判据、恢复与运行逻辑尚未随本建筑预览完成。</p></details>
<details open><summary>主控与8处内嵌接口</summary><div id="portButtons"></div><div id="ports"></div><p>钻石块标记主控；工业接口块只表示候选位置，正式仓室替换与必需能力另行验收。</p></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details open><summary>实际方块来源与普通建材占比</summary><p id="materialSourceBasis">按最终蓝图逐格归类，普通建材占比的分母为${ordinaryBlockCount.toLocaleString()}个实体，不含主控与工业接口的${sourceCounts['主控标记']+sourceCounts['工业接口标记']}个标记；主机壳单列，主控与接口标记单列。</p><table id="materialSources"><thead><tr><th>来源</th><th>数量</th><th>普通建材占比</th></tr></thead><tbody>${sourceRows}</tbody></table></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。真实MC纹理逐格重复，保留全部原坐标；按高度分帧初始化，静止按需绘制。隐藏玻璃或剖切不补画内部切面。资源位于交付目录，可直接以file协议打开，不依赖外网。</p><p>建筑预览不替代正式控制器、Pattern、配方、研究与生存获取验收，不证明电脑版或FCL游戏性能。I43未批准，不计入接入批次；I37继续留最后。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i43-v1-20261028"></script></html>`;
const requiredIds=['stage','loading','labels','viewName','layerValue','layer','showGlass','showPorts','showPaths','showZones','reset','saveImage','counts','status','portButtons','ports','materials','checks'];
if(requiredIds.some(id=>!page.includes(`id="${id}"`))||/弧幕|扇形负载|约束笼|宇宙海关|调度法庭|步进龙门|巨构龙骨|预制船坞/.test(page))throw new Error('I43控件缺失或混入其他建筑造型文案');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(!generated.includes('reviewApi')||/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('共享reviewApi缺失或混入其他机器特效');
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
console.log(JSON.stringify({output,view,candidate_version:'V1',blocks:payload.blockCount,faces:audit.viewer_surface_faces,zones:data.zones.length,ports:data.ports.length,render_on_demand:true,approved:false,installed:false}));
