/**
 * 【文件职责】将 I18 的同源逐格数据、实例纹理和检查记录打包成离线三维评审页。
 * 输入：命令行指定交付目录中的设计与检查.json、data.js；输出：三维评审.html、viewer.bundle.js。
 * 调用链：I18 结构生成器 → 本文件 → 原有三维渲染源码与本地 rolldown；不修改结构、旧交付或游戏资源。
 * 【变更记录 #1】2026-10-22 22:38:09（I18 独立评审工具）
 * - 删除：无；保留旧查看器源码与历史交付。
 * - 新增：真实坐标控制器定位、常显标签和独立轮廓；动态名称、尺寸与候选状态。
 * - 修改：复用原查看器的分层、视角、接口与材质开关，拆开主控和接口标记显隐。
 * - 用途：避免再次出现标题串台或主控藏在默认关闭的接口图层中；静态预览不代表正式 Pattern 或游戏验收。
 * 【变更记录 #2】2026-10-22 22:43:20：最低可执行档缺失时明确显示尚无独立执行器，不显示空白；不改结构数据。
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
if (!process.argv[2]) throw new Error('缺少 I18 交付目录参数。');
const out = path.resolve(process.argv[2]);
const record = JSON.parse(await fs.readFile(path.join(out, '设计与检查.json'), 'utf8'));
const {data, audit} = record;
const officialName = '崩坏能燃料棒封装阵列';
if (data?.key?.toLowerCase() !== 'i18' || !data.title?.includes(officialName)) {
  throw new Error('输入不是 I18 崩坏能燃料棒封装阵列；拒绝覆盖其他机器的预览。');
}
for (const field of ['size', 'controller']) {
  if (!Array.isArray(data[field]) || data[field].length !== 3 || !data[field].every(Number.isInteger)) {
    throw new Error(`${field} 必须为三个整数。`);
  }
}
if (data.size.some(v => v < 1) || data.controller.some((v, i) => v < 0 || v >= data.size[i])) {
  throw new Error('控制器坐标或结构尺寸越界。');
}
if (!Array.isArray(data.ports) || !Array.isArray(audit?.checks)) {
  throw new Error('缺少接口或实际检查数组。');
}
const packedText = await fs.readFile(path.join(out, 'data.js'), 'utf8');
const packedMatch = packedText.match(/window\.HK3_PAYLOAD\s*=\s*("[A-Za-z0-9+/=]+")\s*;/);
if (!packedMatch) throw new Error('data.js 缺少有效压缩逐格载荷。');
const packed = JSON.parse(gunzipSync(Buffer.from(JSON.parse(packedMatch[1]), 'base64')).toString('utf8'));
for (const field of ['key', 'size', 'controller']) {
  if (JSON.stringify(packed.data?.[field]) !== JSON.stringify(data[field])) {
    throw new Error(`逐格载荷与检查记录的 ${field} 不一致。`);
  }
}
if (!Array.isArray(packed.materials) || !packed.materials.length || packed.materials.some(m => Object.values(m.faces ?? {}).some(url => !String(url).startsWith('data:image/')))) {
  throw new Error('材质不是已嵌入的离线图片。');
}
const [w, h, d] = data.size;
const controllerIndex = (data.controller[1] * d + data.controller[2]) * w + data.controller[0];
const controllerPalette = packed.groups.findIndex(group => group.includes(controllerIndex));
if (controllerPalette < 0) throw new Error('逐格载荷中不存在控制器定位方块。');
const controllerState = packed.palette[controllerPalette];
const title = `I18 · ${officialName} · ${data.candidate_version ?? '建筑候选'}`;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const asScript = value => JSON.stringify(value).replaceAll('<', '\\u003c');
const skill = path.join(process.env.USERPROFILE, '.codex/skills/minecraft-builder-skill');
await fs.access(path.join(skill, 'node_modules/@mattzh72/lodestone'));
const {rolldown} = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));
let viewer = await fs.readFile(path.join(root, 'logs/structure-redesign-20260928/preview01/viewer-source.mjs'), 'utf8');

// 精确匹配上游片段；源文件改动时停止，避免悄悄丢失主控定位能力。
function replaceOnce(before, after) {
  if (!viewer.includes(before) || viewer.indexOf(before) !== viewer.lastIndexOf(before)) {
    throw new Error(`原查看器片段已变动，需要复核适配：${before.slice(0, 60)}`);
  }
  viewer = viewer.replace(before, () => after);
}
viewer = viewer.replaceAll('I03', 'I18');
replaceOnce('const {data,materials,audit,names}=payload;data.blocks=[];',
  'const {data,materials,audit,names}=payload;Object.assign(data,window.HK3_I18_META);Object.assign(audit,window.HK3_I18_AUDIT);data.blocks=[];');
replaceOnce("el.className='label'+(kind==='port'?' port':'');", "el.className='label'+(kind==='port'?' port':kind==='controller'?' controller':'');");
replaceOnce("label('主控',data.controller.map(v=>v+.5),'port');", "label('主控 ['+data.controller.join(', ')+'] · 北 -Z',data.controller.map((v,i)=>v+(i===1?2.2:.5)),'controller');");
replaceOnce('for(const p of [...data.ports.map(p=>p.pos),data.controller]){', 'for(const p of data.ports.map(p=>p.pos)){');
replaceOnce('function rebuild(){', `// 主控轮廓不加入接口开关图层，剖切与隐藏材质时也保持定位。
const controllerMark=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.16,1.16,1.16)),new THREE.LineBasicMaterial({color:0xffdf61,depthTest:false,depthWrite:false}));
controllerMark.position.set(...data.controller.map(v=>v+.5));controllerMark.renderOrder=30;scene.add(controllerMark);
function rebuild(){`);
replaceOnce("const views={panel:{pos:[cx,6,-45],target:[cx,2,3],name:'正面集中接口'},", `const controllerCenter=data.controller.map(v=>v+.5);
const views={controller:{pos:[controllerCenter[0],controllerCenter[1]+.4,controllerCenter[2]-20],target:controllerCenter,name:'控制器定位 · 正面朝北（-Z）'},
panel:{pos:[controllerCenter[0],controllerCenter[1]+2,controllerCenter[2]-28],target:controllerCenter,name:'主控与接口面板'},`);
replaceOnce("camera.zoom=name==='panel'?Math.max(W,D,H)/12:1;", "camera.zoom=['controller','panel'].includes(name)?Math.min(controls.maxZoom,Math.max(1,Math.min(camera.top*2,camera.right-camera.left)/(name==='controller'?10:18))):1;");
replaceOnce("['back','panel'].includes(name)", "['back','panel','controller'].includes(name)");
replaceOnce("const show=l.kind==='dimension'||", "const show=l.kind==='controller'||l.kind==='dimension'||");
replaceOnce("a.download=data.key+'-69座实体草稿01-三维结构预览.png';", "a.download=data.name+'-三维结构预览.png';");
replaceOnce('<span>钻石块标记<small>', '<span>控制器定位方块（外观候选）<small>');
replaceOnce("document.getElementById('status').textContent='逐格导出回读与尺寸检查通过 · '+data.ports.length+' 个接口候选 · 非正式Pattern';", "document.getElementById('status').textContent='建筑外观候选 · '+data.ports.length+' 个接口位置 · 未接入正式 Pattern';");
replaceOnce('window.reviewApi={setView,rebuild,renderer,scene,camera};', 'window.reviewApi={setView,rebuild,renderer,scene,camera,controllerMark,labels};');

const built = await rolldown({
  input: 'virtual:i18-review',
  plugins: [{name: 'I18 离线查看器', resolveId(id) {if (id === 'virtual:i18-review') return id;}, load(id) {if (id === 'virtual:i18-review') return viewer;}}],
  resolve: {alias: {three: path.join(skill, 'node_modules/three/build/three.module.js'), 'orbit-controls': path.join(skill, 'node_modules/three/examples/jsm/controls/OrbitControls.js')}}
});
let bundle;
try {
  const result = await built.generate({format: 'iife', minify: true});
  bundle = result.output.find(item => item.type === 'chunk')?.code;
  if (!bundle) throw new Error('未生成查看器脚本。');
} finally {
  await built.close();
}
const meta = Object.fromEntries(['title', 'description', 'name', 'candidate_version', 'target_voltage', 'minimum_executable_recipe_voltage', 'earliest_build_stage', 'construction_notes'].map(key => [key, data[key]]));
const blockCount = packed.groups.reduce((sum, group) => sum + group.length, 0);
const knownChecks = audit.checks.map(value => `<p class="ok">✓ ${esc(value)}</p>`).join('');
const notVerified = (audit.not_verified ?? []).map(value => `<li>${esc(value)}</li>`).join('');
const controllerNotes = data.construction_notes?.controller_marker ?? '正面中心的主控定位方块；外观标记不等于已注册控制器。';
const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#101d28;color:#e9f1f5;font:15px/1.65 "Microsoft YaHei",sans-serif}a{color:#a7dce9}header{padding:12px 22px;border-bottom:1px solid #3b5664}h1{font-size:23px;margin:3px 0}header p{margin:0;color:#b8cbd5}.review{display:grid;grid-template-columns:minmax(0,1fr) 355px;height:calc(100dvh - 107px);min-height:600px}#stage{position:relative;overflow:hidden;min-width:0}#stage canvas{position:absolute;inset:0}#labels{position:absolute;inset:0;pointer-events:none;z-index:2}.label{position:absolute;padding:2px 5px;white-space:nowrap;font-size:12px;background:#122a3cdd;transform:translate(-50%,-50%)}.label.controller{color:#fff6cc;background:#523e08ed;border:2px solid #ffdf61;border-radius:4px;font-weight:700;z-index:5}.label.port{color:#ffda8b}#loading{position:absolute;z-index:6;top:15px;left:15px;padding:12px;background:#17354a}aside{padding:14px 16px;overflow:auto;border-left:1px solid #3b5664}.locator{background:#263e42;border:1px solid #978243;border-left:4px solid #ffdf61;padding:10px 12px;border-radius:5px;margin:8px 0 12px}.locator p{margin:5px 0}.locator code{color:#ffe499}button{background:#263d50;color:#f3f8fc;border:1px solid #577286;border-radius:4px;padding:7px 9px;cursor:pointer;margin:3px 2px}.active{border-color:#9ee5dc;background:#385766}.locator button{background:#d8c16c;color:#162630;border-color:#f1da88;font-weight:700;padding:8px 14px}label{cursor:pointer}input{accent-color:#b9d9cb}input[type=range]{width:100%}p{margin:9px 0}small,.muted{color:#b2c6cf}small{display:block}code{overflow-wrap:anywhere}details{padding:10px 0;border-bottom:1px solid #334c5e}summary{cursor:pointer;font-weight:600}.swatch{width:32px;height:32px;vertical-align:middle;image-rendering:pixelated;margin:4px}.material{display:block;padding:7px 0}.material small{overflow-wrap:anywhere}.ok{color:#b4dcc4}.portrow{margin:8px 0}.portrow b{color:#e6d59c}#status{color:#f0d596;font-size:13px}#counts{font-size:13px}#viewName{font-weight:700}@media(max-width:950px){header{padding:12px}h1{font-size:20px}.review{display:block;height:auto;min-height:0}#stage{height:65vh;min-height:420px}aside{border-left:0;border-top:1px solid #3b5664}.locator{position:relative}}
</style></head><body>
<header><a href="index.html">← 返回 I18 总览</a><h1>${esc(title)}</h1><p>${w} × ${d} × ${h}（宽×深×高） · ${blockCount.toLocaleString('zh-CN')} 个实体方块 · 主控和接口位置可单独查看</p></header>
<main class="review"><section id="stage"><div id="loading">正在加载本机结构与离线纹理…</div><div id="labels"></div></section><aside>
<div id="viewName">前左整体</div>
<div class="locator"><b>I18 控制器位置</b><p>本地坐标 <code>[${data.controller.join(', ')}]</code><br>正面朝北（−Z），位于建筑正面。</p><p>定位方块：<code>${esc(controllerState)}</code></p><button data-view="controller">定位控制器</button><small>黄色轮廓与主控标签始终显示；接口标记可独立开关。</small></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧</button><button data-view="top">俯视</button><button data-view="panel">接口近景</button><button data-view="inside">内部剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p class="muted">左键旋转 · 右键平移 · 滚轮缩放</p>
<label>剖切高度 <b id="layerValue">${h - 1}</b><input id="layer" type="range" min="0" max="${h - 1}" value="${h - 1}"></label>
<p><label><input id="showGlass" type="checkbox" checked>玻璃</label> <label><input id="showPorts" type="checkbox">接口标记</label> <label><input id="showPaths" type="checkbox">检修净空</label> <label><input id="showZones" type="checkbox">分区标签</label></p>
<button id="reset">重置</button><button id="saveImage">保存当前视角</button><p id="counts"></p><p id="status">建筑外观候选，未接入正式 Pattern。</p>
<details open><summary>建筑概念</summary><p>${esc(data.description)}</p></details>
<details><summary>控制器与电压边界</summary><p>${esc(controllerNotes)}</p><p>目标电压：${esc(data.target_voltage)}<br>最低可执行配方档：${esc(data.minimum_executable_recipe_voltage ?? '尚无独立执行器，未确立')}<br>首次建造阶段：${esc(data.earliest_build_stage)}</p><p>接口使用工业方块表示计划位置，不代表已安装真实仓室。外观、结构导出、正式 Pattern 和游戏运行分别验收。</p></details>
<details><summary>逐种隐藏材质</summary><div id="materials"></div></details><details><summary>接口位置</summary><div id="ports"></div></details>
<details><summary>实际检查</summary><div id="checks">${knownChecks}</div></details><details><summary>尚未验收</summary><ul>${notVerified || '<li>正式 Pattern、仓室能力、游戏成型与配方执行。</li>'}</ul></details>
<details><summary>结构与记录</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="设计与检查.json">设计与检查</a></details>
</aside></main><script src="data.js"></script><script>window.HK3_I18_META=${asScript(meta)};window.HK3_I18_AUDIT=${asScript({checks: audit.checks, palette: audit.palette})};</script><script src="viewer.bundle.js"></script>
<!-- 变更记录 #1：2026-10-22 22:38:09；I18 专用离线评审页，主控坐标、标签和轮廓由同源逐格数据生成；不代表正式 Pattern 或实机验收。 -->
</body></html>`;
await fs.writeFile(path.join(out, 'viewer.bundle.js'), bundle, 'utf8');
await fs.writeFile(path.join(out, '三维评审.html'), html, 'utf8');
console.log(`已生成 I18 专用离线三维页；主控 [${data.controller.join(', ')}]，朝北（-Z）。`);
