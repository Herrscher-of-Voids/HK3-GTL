/** I42预制船坞评审：复用I41 V3的真实MC材质引擎，仅替换建筑数据和说明。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I42交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i42');
const js=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!js.startsWith('window.HK3_PAYLOAD=')||!js.endsWith(';'))throw new Error('I42载荷格式错误');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i42'||data.candidate_version!=='V1'||data.name!=='hk3gtl-i42-prefabrication-dock-v1-20261028'
  ||data.size.join(',')!=='641,295,449'||p.join(',')!=='320,26,0'||p[0]!==Math.floor((w-1)/2)||data.ports.length!==8
  ||payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length
  ||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('I42身份、尺寸、中线、接口或材质合同不符');

const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i41_fan_dispatch_viewer_20261028.mjs'),'utf8');
const boundary=template.indexOf('const js=await fs.readFile');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(boundary<0||!template.slice(0,boundary).includes(rootLine))throw new Error('共享I41真实材质引擎入口已变化');
let engine=template.slice(0,boundary).replaceAll('i41','i42').replaceAll('I41','I42')
  .replaceAll('文明能源调度','奇观构件预制').replaceAll('弧幕母线与扇形负载港','巨构龙骨与步进预制船坞')
  .replaceAll('调度厅材质近景','校验厅材质近景').replace(rootLine,`const root=${JSON.stringify(root)};`);
const launch="await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));";
if(!engine.includes(launch))throw new Error('共享材质引擎启动边界已变化');
engine=engine.replace(launch,"engine=engine.replaceAll('后侧天线与轴座','后端工装与出厂交接');\n"+launch);
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const prior=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=prior.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I42 · ${esc(data.title)} V1 · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #9cb5d3;background:#25313d;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I42交付总览</a><h1>I42 · ${esc(data.title)} V1</h1><div>WFV / V13 / tier27 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I42巨构龙骨与步进预制船坞真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">开放式纵向预制船坞承托在制巨构龙骨与分段弧形构件，连续步进龙门吊沿轨道交接，两侧分层厂房承担不同部件的加工、工装和转运。I42制造专用构件，玩家仍须实际建设每座独立奇观。候选未批准、未部署。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平嵌入前端工厂连续外墙。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后端工装与出厂交接</button><button data-view="top">预制船坞俯视</button><button data-view="inside">厂房与龙骨剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">校验厅材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">生产分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>巨构龙骨与步进预制船坞</summary><p>${esc(data.description)}</p><p>以在制构件和连续搬运工序确定轮廓：中央预制坞、步进龙门吊、两侧部件厂房、模具与出厂交接形成同一工厂。分区标签表示建筑与工艺组织，不代表空间分区渲染或新增正式控制器。</p></details>
<details open><summary>十五奇观分别取用专用构件</summary><p>I40专用功能材料、GT基础机械件、I14/I16先进坯与精密件按用途汇入，预制承力骨架、导能母排、约束隔离壁、重构工作腔、认知载体框、冷热隔热壳段、核心安装座及检修汇接模块。W01–W15各取所需规格和组合，不以一种万能构件绕过材料路线。</p><p>边角料按实际回收配方返料；预制不替玩家实际建造多方块，不制造工程证明或毕业资格。首批构件不得要求尚未建成的同一奇观提供其首建材料。</p></details>
<details open><summary>研究、建造与运行分别验收</summary><p>RN-WPF对应I42各系列构件预制；研究试件由前级I16加工、I32检测，关联已可取得的I40材料。I42首机不用自产预制件。各奇观专用配方、核心应用与正式建造/运行仍须分别核对专项研究及二审，通用预制研究不代表十五奇观全部开放。</p><p>WFV是已授权方案的本机制作映射；暂定实验的电压或数值不替代机器定阶。构件系列、配方投料、回收收支、注册和运行尚未随本建筑预览完成。</p></details>
<details open><summary>主控与8处内嵌接口</summary><div id="portButtons"></div><div id="ports"></div><p>钻石块标记主控；工业接口块只表示候选位置，正式仓室替换与必需能力另行验收。</p></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。真实MC纹理逐格重复，保留全部原坐标；按高度分帧初始化，静止按需绘制。隐藏玻璃或剖切不补画内部切面。资源位于交付目录，可直接以file协议打开，不依赖外网。</p><p>建筑预览不替代正式控制器、Pattern、配方、研究与生存获取验收，不证明电脑版或FCL游戏性能。I42未批准，不计入接入批次；I37继续留最后。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i42-v1-20261028"></script></html>`;
const requiredIds=['stage','loading','labels','viewName','layerValue','layer','showGlass','showPorts','showPaths','showZones','reset','saveImage','counts','status','portButtons','ports','materials','checks'];
if(requiredIds.some(id=>!page.includes(`id="${id}"`))||/I41|弧幕|扇形负载|约束笼|宇宙海关|调度法庭/.test(page))throw new Error('I42控件缺失或混入其他建筑文案');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(!generated.includes('reviewApi')||/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('共享reviewApi缺失或混入其他机器特效');
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
console.log(JSON.stringify({output,view,candidate_version:'V1',blocks:payload.blockCount,faces:audit.viewer_surface_faces,zones:data.zones.length,ports:data.ports.length,render_on_demand:true,approved:false,installed:false}));
