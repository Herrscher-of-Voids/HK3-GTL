/** I44信标候选：复用离线真实MC材质渲染逻辑，独立数据与设备职责。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I44交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i44');
const js=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!js.startsWith('window.HK3_PAYLOAD=')||!js.endsWith(';'))throw new Error('I44载荷格式错误');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i44'||data.candidate_version!=='V2'||data.name!=='hk3gtl-i44-station-v2-20261029'
  ||data.size.join(',')!=='281,209,741'||p.join(',')!=='140,14,16'||data.controller_face!=='north'
  ||p[0]!==Math.floor((w-1)/2)||data.ports.length!==8
  ||payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length
  ||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('I44身份、尺寸、中线、接口或材质合同不符');

const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i39_unmanned_relay_viewer_v1_20261027.mjs'),'utf8');
const boundary=template.indexOf('const dataJs=');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(boundary<0||!template.slice(0,boundary).includes(rootLine))throw new Error('共享真实材质引擎入口已变化');
let engine=template.slice(0,boundary).replaceAll('i39','i44').replaceAll('I39','I44')
  .replaceAll('无人航路中继','仿制的千界一乘信标').replaceAll('偏馈碟阵与双轨整备站','穹顶站台与坐标调度总站')
  .replaceAll('调度楼材质近景','主控材质近景').replaceAll('后侧天线与轴座','后方站台与贯通股道')
  .replaceAll('穹顶站台与坐标调度总站V1-三维预览.png','穹顶站台与坐标调度总站V2-三维预览.png')
  .replace(rootLine,`const root=${JSON.stringify(root)};`);
const zoomBoundary="source=source.replace('camera.zoom=1;', \"camera.zoom=1;\");";
if(!engine.includes(zoomBoundary))throw new Error('车站相机缩放入口已变化');
engine=engine.replace(zoomBoundary,"source=source.replace('camera.zoom=1;', \"camera.zoom=['front','right','back'].includes(name)?1.45:1;\");");
await import('data:text/javascript;base64,'+Buffer.from(engine).toString('base64'));

const prior=await fs.readFile(path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/i34/三维评审.html'),'utf8');
const css=prior.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sourceCounts=Object.fromEntries(['GTCEu','GTL Core','其他模组','原版','项目QCV主机壳','主控标记','工业接口标记'].map(name=>[name,0]));
for(const [state,count] of Object.entries(audit.palette)){
  const category=state==='minecraft:diamond_block'?'主控标记':state==='hk3gtl:industrial_port_casing'?'工业接口标记'
    :state==='hk3gtl:voltage_machine_casing_qcv'?'项目QCV主机壳':state.startsWith('gtceu:')?'GTCEu'
    :state.startsWith('gtlcore:')?'GTL Core':state.startsWith('minecraft:')?'原版':'其他模组';
  sourceCounts[category]+=count;
}
if(Object.values(sourceCounts).reduce((sum,count)=>sum+count,0)!==payload.blockCount
  ||Object.entries(audit.material_source_counts??{}).some(([name,count])=>sourceCounts[name]!==count))throw new Error('I44材料来源分类与实体总量冲突');
const ordinaryBlockCount=payload.blockCount-sourceCounts['主控标记']-sourceCounts['工业接口标记'];
const sourceRows=Object.entries(sourceCounts).map(([name,count])=>`<tr><td>${name}</td><td>${count.toLocaleString()}</td><td>${name.endsWith('标记')?'标记单列':(count/ordinaryBlockCount*100).toFixed(3)+'%'}</td></tr>`).join('');
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I44 · ${esc(data.title)} V2 · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #8e9aca;background:#252e46;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I44交付总览</a><h1>I44 · ${esc(data.title)} V2</h1><div>QCV / V06 / tier20 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I44穹顶站台与坐标调度总站真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">负责人指定的车站式坐标信标：前部站钟与坐标登记厅，后部弧形拱顶雨棚、双侧站台和中央股道。配套I45是独立固定蒸汽列车；本站负责登记、复测、锁定与交接目的地。候选未批准、未安装。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，朝北，齐平嵌入站房坐标柜连续外壁。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后方站台与贯通股道</button><button data-view="top">车站俯视</button><button data-view="inside">站房与站台剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">主控材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">设备分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>穹顶站台与坐标调度总站</summary><p>${esc(data.description)}</p><p>大跨度阶梯弧形雨棚由连续拱肋与落地拱脚承托，QCV深靛蓝承力带与浅银框架配合玻璃透光条。站台有座椅、指示牌、照明、检修道和两端测定工位。高度来自雨棚，不追加无用途高塔。</p></details>
<details open><summary>坐标复测、锁定与目的地交接</summary><p>I25提供已解析坐标，I44复测并锁定合法目标；解锁加强观测后才执行对应观测，向无人任务及I45目的地联锁交接记录。I45是独立固定蒸汽列车，承担既定获许可旅行；I44车站只登记、复测、锁定与调度目的地。车站与列车不合并为同一个Pattern。</p><p>不把信标变成旅行入口，不凭空生成新目标，不解锁终审维度，也不绕过目标来源、权限、研究和任务条件。建筑形体表达设备职责，未实现的逻辑不因本预览而视为接通。</p></details>
<details open><summary>主控与${data.ports.length}处原位内嵌接口</summary><div id="portButtons"></div><div id="ports"></div><p>接口替换有用途的设备外壳方块，周围保留连续壳体与接近空间；没有外挂面板、立柱或管线末端托块。钻石块标记主控，工业接口块只表示候选位置；正式仓室替换与必需能力另行验收。</p></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details open><summary>实际方块来源与普通建材占比</summary><p id="materialSourceBasis">按最终蓝图逐格归类，普通建材占比的分母为${ordinaryBlockCount.toLocaleString()}个实体，不含主控与工业接口的${sourceCounts['主控标记']+sourceCounts['工业接口标记']}个标记；主机壳单列，主控与接口标记单列。</p><table id="materialSources"><thead><tr><th>来源</th><th>数量</th><th>普通建材占比</th></tr></thead><tbody>${sourceRows}</tbody></table></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片。真实MC纹理逐格重复，保留全部原坐标；按高度分帧初始化，静止按需绘制。隐藏玻璃或剖切不补画内部切面。全部资源位于交付目录，可直接以file协议离线打开。</p><p>完整NBT与Schematic回读结果见核验记录；外观候选不替代正式控制器、Pattern、配方、研究与生存获取验收，不证明电脑版或FCL游戏性能。I44未批准、未安装；I43仍待审，batch-10仅I40/I41/I42为3/5，I37留最后。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i44-v2-20261029"></script></html>`;
const requiredIds=['stage','loading','labels','viewName','layerValue','layer','showGlass','showPorts','showPaths','showZones','reset','saveImage','counts','status','portButtons','ports','materials','checks'];
if(requiredIds.some(id=>!page.includes(`id="${id}"`))||/弧幕母线|扇形负载港|开瓣环境穹舱|六轴验收台|偏馈碟阵|四爪抓球/.test(page))throw new Error('I44控件缺失或混入其他建筑造型文案');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(!generated.includes('reviewApi')||/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('共享reviewApi缺失或混入其他机器特效');
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
console.log(JSON.stringify({output,view,candidate_version:'V2',blocks:payload.blockCount,faces:audit.viewer_surface_faces,zones:data.zones.length,ports:data.ports.length,render_on_demand:true,approved:false,installed:false}));
