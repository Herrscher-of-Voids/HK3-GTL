/** I45蒸汽列车：独立职责页，仅复用真实MC纹理离线渲染逻辑。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I45交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i45');
const js=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!js.startsWith('window.HK3_PAYLOAD=')||!js.endsWith(';'))throw new Error('I45载荷格式错误');
const payload=JSON.parse(gunzipSync(Buffer.from(JSON.parse(js.slice('window.HK3_PAYLOAD='.length,-1)),'base64')).toString('utf8'));
const {data,audit}=payload,[w,h,d]=data.size,p=data.controller;
if(data.key!=='i45'||data.candidate_version!=='V1'||data.name!=='hk3gtl-i45-steam-train-v1-20261029'
  ||data.size.join(',')!=='121,181,821'||p.join(',')!=='60,108,0'||data.controller_face!=='north'
  ||data.ports.length!==8||p[0]!==Math.floor((w-1)/2)||payload.palette.length!==payload.materials.length
  ||payload.surfaceGroups.length!==payload.palette.length||payload.surfaceGroups.some(g=>g.length!==6))throw new Error('I45身份、尺寸、主控、接口或材质合同不符');

const template=await fs.readFile(path.join(root,'tools/structure_delivery/build_i39_unmanned_relay_viewer_v1_20261027.mjs'),'utf8');
const boundary=template.indexOf('const dataJs=');
const rootLine="const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');";
if(boundary<0||!template.slice(0,boundary).includes(rootLine))throw new Error('真实材质引擎入口已变化');
let engine=template.slice(0,boundary).replaceAll('i39','i45').replaceAll('I39','I45')
  .replaceAll('无人航路中继','固定蒸汽列车').replaceAll('偏馈碟阵与双轨整备站','靛蓝蒸汽机车与双节旅客车')
  .replaceAll('调度楼材质近景','烟箱主控材质近景').replaceAll('后侧天线与轴座','客车侧后方')
  .replace(rootLine,`const root=${JSON.stringify(root)};`);
const cameraBoundary="source=source.replace('camera.zoom=1;'";
if(!engine.includes(cameraBoundary))throw new Error('列车低视角补丁入口已变化');
engine=engine.replace(cameraBoundary,"source=source.replaceAll('H*.7+L*.45','H*.5+L*.22');\nsource=source.replace('scene.add(ground);','').replace('scene.add(grid);','');\n"+cameraBoundary);
engine=engine.replace("source=source.replace('camera.zoom=1;', \"camera.zoom=1;\");", "source=source.replace('camera.zoom=1;', \"camera.zoom=['front','right','back'].includes(name)?1.85:1;\");");
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
  ||Object.entries(audit.material_source_counts??{}).some(([name,count])=>sourceCounts[name]!==count))throw new Error('I45来源数量与实体冲突');
const ordinaryBlockCount=payload.blockCount-sourceCounts['主控标记']-sourceCounts['工业接口标记'];
const sourceRows=Object.entries(sourceCounts).map(([name,count])=>`<tr><td>${name}</td><td>${count.toLocaleString()}</td><td>${name.endsWith('标记')?'标记单列':(count/ordinaryBlockCount*100).toFixed(3)+'%'}</td></tr>`).join('');
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I45 · ${esc(data.title)} V1 · MC材质三维评审</title><style>${css}
.candidate-note{padding:12px;border-left:3px solid #8e9aca;background:#252e46;color:#e4edf5}.locator{margin:14px 0}#stage{background:#111b28}</style>
<header><a href="../index.html">← I45交付总览</a><h1>I45 · ${esc(data.title)} V1</h1><div>QCV / V06 / tier20 · ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体 · 独立待审候选</div></header>
<main class="review"><section id="stage" aria-label="I45固定蒸汽列车真实实体三维预览"><div id="loading">加载真实MC材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">深靛蓝卧式锅炉、四对辐条动轮与连杆、短烟囱、驾驶室、煤水车和两节旅客车。按负责人指定制作蒸汽火车；它是固定多方块，不声称实现实体移动。候选未批准、未安装。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，朝北，齐平嵌入烟箱正面。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">客车侧后方</button><button data-view="top">列车俯视</button><button data-view="inside">锅炉与客车剖切</button><button data-view="orthofront">正前</button><button data-view="orthoside">轮轨正侧</button></div>
<p><button data-view="texture">烟箱主控材质近景</button> 实例原始MC纹理 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">车组分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>靛蓝蒸汽机车与双节旅客车</summary><p>${esc(data.description)}</p><p>细金属箍带分开锅炉压力段，烟箱、汽缸、曲柄和外侧踏板均有实际实体。驾驶室接续火箱，煤水车开放煤仓保留真实煤堆，水箱留出内腔；两节客车有座席与中央通道。没有铺满无用途实心底座。</p></details>
<details open><summary>I44交坐标，I45执行允许旅行</summary><p>接收I44有效坐标、传送能量和玩家；出发前检查授权和能量，确认抵达并记录旅行，处理失败恢复。列车固定不移动，不新增神之键或非法目的维度；生命跨平行宇宙运输限制与终审维度禁行边界继续生效。</p><p>煤水与蒸汽造型不自动变成新配方或新能力；正式Pattern、能耗、权限、恢复和生存链仍待实装核验。</p></details>
<details open><summary>主控与8处原位内嵌接口</summary><div id="portButtons"></div><div id="ports"></div><p>接口嵌在驾驶室、煤水车和旅客车实际外壳中，四周连续、有内背板、外侧可达，不外挂面板或托举柱。钻石和工业接口块仅作预览标记，不代表真实仓室能力。</p></details>
<details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details open><summary>固定轮轨与站台净空</summary><p>轨心X25/X95、轨距70格；轨顶Y5、轮底Y5。常规车体宽95格，总宽121格包含前铲与踏板；主动车轮半径34格。与I44站台使用同一空间语言，两座建筑独立审核。</p></details>
<details open><summary>实际方块来源与普通建材占比</summary><p id="materialSourceBasis">普通材料占比分母为${ordinaryBlockCount.toLocaleString()}个实体，不含主控和工业接口9个标记；项目QCV主机壳单列。</p><table id="materialSources"><thead><tr><th>来源</th><th>数量</th><th>普通建材占比</th></tr></thead><tbody>${sourceRows}</tbody></table></details>
<details><summary>文件与性能边界</summary><a href="${esc(data.name)}.nbt">完整NBT</a> · <a href="${esc(data.name)}.schem">完整Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%面片。真实MC纹理逐格重复、保留原坐标，分帧初始化、静止按需绘制。剖切和隐藏玻璃不补画内部切面；可直接以file协议离线打开。</p><p>原始几何、完整NBT和Schematic已逐格回读。候选未批准、未安装；I43仍待审，batch-10为I40/I41/I42三台，3/5；I37最后。PC/FCL游戏运行性能及材料生存可达性未在此轮验收。</p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=i45-v1-20261029"></script></html>`;
const required=['stage','loading','labels','viewName','layerValue','layer','showGlass','showPorts','showPaths','showZones','reset','saveImage','counts','status','portButtons','ports','materials','checks'];
if(required.some(id=>!page.includes(`id="${id}"`))||/双楔准星|轴向观测坞|偏馈碟阵|开瓣环境/.test(page))throw new Error('I45控件缺失或混入其他造型文案');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(!generated.includes('reviewApi')||/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('I45引擎合同不符');
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,ports:data.ports.length,approved:false,installed:false}));
