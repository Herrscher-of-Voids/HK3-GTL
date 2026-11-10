/** I38虚数能量整流中枢：真实外露面、分帧初始化与静止按需绘制。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(!process.argv[2])throw new Error('缺少I38交付根目录参数');
const output=path.resolve(process.argv[2]),view=path.join(output,'i38');
const legacyFolder=path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027');
let builder=await fs.readFile(path.join(legacyFolder,'生成脚本/build_i34_viewer_v1_20261027.mjs'),'utf8');
if(!builder.includes('const output = path.resolve(process.argv[2]);'))throw new Error('共享查看器输出参数已变化，拒绝错写目录');
builder=builder.replace('const output = path.resolve(process.argv[2]);',`const output = ${JSON.stringify(view)};`);
builder=builder.replaceAll('virtual:i34-imaginary-tree-array','virtual:i38-imaginary-rectifier');
builder=builder.replaceAll('I34虚数之树观测预览','I38虚数能量整流预览');
builder=builder.replaceAll('I34逐帧实例初始化补丁','I38逐帧实例初始化补丁');
builder=builder.replaceAll('树冠干涉观测院V1-三维预览.png','双极脉冲换流站V1-三维预览.png');
builder=builder.replaceAll('后侧观测资料交接','后侧冷却与回流');
const runPatch=String.raw`
source=source.replace('controls.enableDamping=true;', 'controls.enableDamping=false;');
source=source.replace('controls.maxZoom=8;', 'controls.maxZoom=36;');
source=source.replace('renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));', 'renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));');
source=source.replace('camera.zoom=1;', "camera.zoom=1;");
source=source.replace('camera.zoom=Math.min(8,L/35);','camera.zoom=Math.min(28,L/20);');
source=source.replace("name==='inside'?Math.floor(H*.48):H-1", "name==='inside'?Math.floor(H*.45):H-1");
source=source.replace('result.magFilter=THREE.NearestFilter;result.minFilter=THREE.NearestFilter;',
  'result.magFilter=THREE.NearestFilter;result.minFilter=THREE.NearestFilter;result.generateMipmaps=false;');
source=source.replace('function setView(name){',
  "function setView(name){if(name==='texture'){camera.up.set(0,1,0);camera.position.set(500,115,95);controls.target.set(476,105,134);camera.zoom=L/40;camera.updateProjectionMatrix();controls.update();document.getElementById('layer').value=H-1;document.getElementById('showGlass').checked=true;document.getElementById('showPorts').checked=false;document.getElementById('showPaths').checked=false;document.getElementById('viewName').textContent='阀组材质近景 · 实例原始MC贴图';rebuild();return;}");
source=source.replace('const blockCount=payload.blockCount;payload.surfaceGroups=null;',
  'const blockCount=payload.blockCount;payload.surfaceGroups=null;const surfaceRunLengths=payload.surfaceRunLengths;payload.surfaceRunLengths=null;');
source=source.replace('const mesh=new THREE.InstancedMesh(faceGeometries[face],side,indices.length);',
  'side.map.wrapS=THREE.RepeatWrapping;side.map.wrapT=THREE.RepeatWrapping;side.map.needsUpdate=true;\n'+
  'side.onBeforeCompile=shader=>{shader.vertexShader=shader.vertexShader.replace("#include <uv_vertex>","#include <uv_vertex>\\n#if defined(USE_MAP) && defined(USE_INSTANCING)\\nvMapUv.x*=length(instanceMatrix[0].xyz);\\n#endif");};\n'+
  'side.customProgramCacheKey=()=>"i38-surface-runs-v1";\nconst mesh=new THREE.InstancedMesh(faceGeometries[face],side,indices.length);');
source=source.replace('mesh.userData={indices,material,face,initialized:0,boundsReady:false};',
  'mesh.userData={indices,material,face,runLengths:surfaceRunLengths[i][face],initialized:0,boundsReady:false};');
source=source.replace('const {indices,face}=mesh.userData,start=', 'const {indices,face,runLengths}=mesh.userData,start=');
source=source.replace('position.set(px,py,pz);matrix.compose(position,quaternions[face],scale);mesh.setMatrixAt(i,matrix);',
  'const runLength=runLengths[i];if(face===0||face===1)pz=z+runLength/2;else px=x+runLength/2;scale.set(runLength,1,1);position.set(px,py,pz);matrix.compose(position,quaternions[face],scale);mesh.setMatrixAt(i,matrix);');
source=source.replace("audit.viewer_surface_faces.toLocaleString()+' 片'", "audit.viewer_rendered_quads.toLocaleString()+' 合并面片'");
source=source.replace("'绘制外露面 '+count.toLocaleString()+' 片 / '", "'合并绘制 '+count.toLocaleString()+' 面片 / '");
if(!source.includes('controls.enableDamping=false;')||!source.includes('runLengths[i]')||!source.includes('vMapUv.x*=length(instanceMatrix[0].xyz)')||source.includes('LinearMipmapLinearFilter;result.anisotropy'))throw new Error('I38逐格纹理或连续表面合并补丁未生效');
`;
if(!builder.includes('const oldHotPaths = '))throw new Error('共享查看器自检边界已变化');
builder=builder.replace('const oldHotPaths = ',runPatch+`\nnew Function('return (async()=>{'+source+'});');\nconst oldHotPaths = `);
if(!builder.includes('initializeMatrixChunk')||!builder.includes('requestRender=()=>'))throw new Error('轻量查看器缺少分帧初始化或按需绘制');
await fs.mkdir(view,{recursive:true});
await import('data:text/javascript;base64,'+Buffer.from(builder).toString('base64'));

const dataJs=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!dataJs.startsWith('window.HK3_PAYLOAD=')||!dataJs.endsWith(';'))throw new Error('I38候选载荷格式错误');
const encoded=JSON.parse(dataJs.slice('window.HK3_PAYLOAD='.length,-1));
const payload=JSON.parse(gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
const {data,audit}=payload;
if(data.key!=='i38'||data.controller[0]!==Math.floor((data.size[0]-1)/2))throw new Error('I38编号或主控居中坐标不符');
if(payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('材质或表面索引数量错误');
const oldPage=await fs.readFile(path.join(legacyFolder,'i34/三维评审.html'),'utf8');
const css=oldPage.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const [w,h,d]=data.size,p=data.controller,title=data.title??'虚数能量整流中枢 · 双极脉冲换流站';
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I38 · ${escape(title)} V1 · MC材质三维评审</title><style>${css}
.candidate-note{padding:10px 12px;border-left:3px solid #b69aa9;background:#342936;color:#eee5ec}.locator{margin-top:12px}#stage{background:#111b28}</style>
<header><a href="../index.html">← I38交付总览</a><h1>I38 · ${escape(title)} V1 · MC材质三维评审</h1><div>IWV · V12 / ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体方块 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I38双极脉冲换流站真实实体三维预览"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">本轮为建筑外观候选，尚未批准、尚未接入实例。十二座分级绝缘阀塔构成双极换流阀列，顶置脉冲母线连接前端变压器与后端散热机列；居中测控室沿连续外墙集成主控与接口。</div>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平融入主体设备外壳。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧冷却与回流</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p><button data-view="texture">阀组材质近景</button> 实例原始MC贴图 · 最近邻采样</p><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>双极脉冲换流站</summary><p>${escape(data.description)}</p><p>接收I01-4能量态采集结果与合同允许的回收能流，承担整流、合法校验和幂等记账的建筑表达。I01-4继续负责能量态采集，I41负责文明负载调度；本机不以外观预览代替HKE结算运行验收。</p><p>不能凭结构存在自动创造HKE或免费EU；不把资料包当作能量，不自动解锁研究或文明。正式供能合同、整流、账户与去重结算均须另行核验。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="${escape(data.name)}.nbt">NBT</a> · <a href="${escape(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>${audit.viewer_surface_faces.toLocaleString()}片逐格外露面合并为${audit.viewer_rendered_quads.toLocaleString()}片连续面，减少${(audit.viewer_surface_merge.reduction*100).toFixed(1)}%绘制面片；逐格纹理重复、同高度合并，重展与真实表面一致。按高度分帧初始化，静止按需重绘。恢复最近邻原始纹理采样，按设备像素比至多1.5倍采样；全景仍受屏幕像素限制，材质细节可用近景按钮查看。隐藏材质或剖切不补画内部剖切面。换流站阀塔、母线和变压器仅作工程造型表达；候选未批准、未实装，游戏运行及阶段可达性另行验收。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js?v=mc-texture-fix-20261027"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection|createThresholdPortal|showPortal|animatePortal/.test(generated))throw new Error('I38错误地包含其他机器的动态效果');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,projection:false,render_on_demand:true,deterministic_camera_presets:true}));
