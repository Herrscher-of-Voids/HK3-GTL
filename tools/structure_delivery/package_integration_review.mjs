/**
 * 文件职责：把控制器融合候选的同源数据打包为离线三维评审；仅写新候选目录。
 * 输入为交付根目录，各子目录已有data.js及设计与检查.json；复用原逐面纹理查看器。
 * 【变更记录 #1】2026-10-23 10:57:25：删除无；新增动态机器标题、常显主控、逐口定位和离线页面；
 * 修改旧集中接口视角为实际坐标定位；用途为评审新结构，不修改正式资源或宣称游戏通过。
 * 【变更记录 #2】2026-10-23 11:05:57：删除无；新增读取逐台principle摘要；修改说明取值，避免通用描述遮蔽具体设备改动。
 * 【变更记录 #3】2026-10-23 11:41:08：删除固定V1标题；新增可选版本名称和宽度中心列提示；
 * 修改摘要优先读取置中修订依据；用途为复用同源离线查看器交付V2，旧V1成品保持原字节。
 * 【变更记录 #4】2026-10-23 19:43:36：删除对所有主控策略均有整宽中心列字段的假设；
 * 新增原位继承策略摘要显示；修改定位说明按实际字段分支，避免出现undefined；用途为支持I20系列原位扩建主控。
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.resolve(process.argv[2]);
const version=process.argv[3]??'融合修订V1';
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
await fs.access(path.join(skill,'node_modules/@mattzh72/lodestone'));
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
let viewer=await fs.readFile(path.join(root,'logs/structure-redesign-20260928/preview01/viewer-source.mjs'),'utf8');
function replace(before,after){if(!viewer.includes(before))throw Error('查看器适配失配：'+before.slice(0,50));viewer=viewer.replace(before,()=>after);}
viewer=viewer.replaceAll('I03','控制器融合候选');
replace("el.className='label'+(kind==='port'?' port':'');","el.className='label'+(kind==='port'?' port':kind==='controller'?' controller':'');");
replace("label('主控',data.controller.map(v=>v+.5),'port');","label('主控 ['+data.controller.join(', ')+']',data.controller.map((v,i)=>v+(i===1?2:.5)),'controller');");
replace('for(const p of [...data.ports.map(p=>p.pos),data.controller]){','for(const p of data.ports.map(p=>p.pos)){');
replace('function rebuild(){',`const controllerMark=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.16,1.16,1.16)),new THREE.LineBasicMaterial({color:0xffdf61,depthTest:false}));
controllerMark.position.set(...data.controller.map(v=>v+.5));controllerMark.renderOrder=30;scene.add(controllerMark);
function rebuild(){`);
replace("const views={panel:{pos:[cx,6,-45],target:[cx,2,3],name:'正面集中接口'},",`const cc=data.controller.map(v=>v+.5);
const views={controller:{pos:[cc[0],cc[1]+1,cc[2]-18],target:cc,name:'主控定位'},panel:{pos:[cx-L,H*.5,cz-L],target:[cx,H*.3,cz],name:'全部接口'},`);
replace('function setView(name){',`for(const p of data.ports){const q=p.pos.map(v=>v+.5),delta={north:[0,0,-1],south:[0,0,1],west:[-1,0,0],east:[1,0,0]}[p.face];views['port:'+p.id]={pos:q.map((v,i)=>v+delta[i]*18+(i===1?1:0)),target:q,name:p.id+' · '+p.purpose};}
function setView(name){`);
replace("camera.zoom=name==='panel'?Math.max(W,D,H)/12:1;","camera.zoom=(name==='controller'||name.startsWith('port:'))?Math.min(controls.maxZoom,Math.max(1,Math.min(camera.top*2,camera.right-camera.left)/13)):1;");
replace("['back','panel'].includes(name)","['back','panel','controller'].includes(name)||name.startsWith('port:')");
replace("const show=l.kind==='dimension'||","const show=l.kind==='controller'||l.kind==='dimension'||");
replace("a.download=data.key+'-69座实体草稿01-三维结构预览.png';","a.download=data.name+'-三维结构预览.png';");
replace("document.getElementById('status').textContent='逐格导出回读与尺寸检查通过 · '+data.ports.length+' 个接口候选 · 非正式Pattern';","document.getElementById('status').textContent='融合修订候选 · '+data.ports.length+' 个接口位置 · 未接入正式Pattern';");
replace("for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>setView(button.dataset.view);","for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>setView(button.dataset.view);");
replace("document.getElementById('materials').innerHTML=", "for(const p of data.ports){const b=document.createElement('button');b.textContent=p.id+' ['+p.pos.join(', ')+']';b.onclick=()=>setView('port:'+p.id);document.getElementById('portButtons').append(b);}\ndocument.getElementById('materials').innerHTML=");
const built=await rolldown({input:'virtual:integration',plugins:[{name:'融合评审',resolveId:id=>id==='virtual:integration'?id:null,load:id=>id==='virtual:integration'?viewer:null}],resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
let bundle;try{bundle=(await built.generate({format:'iife',minify:true})).output.find(x=>x.type==='chunk').code;}finally{await built.close();}
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
for(const entry of await fs.readdir(out,{withFileTypes:true})){
 if(!entry.isDirectory()||!/^i\d/.test(entry.name))continue;
 const folder=path.join(out,entry.name),{data,audit}=JSON.parse(await fs.readFile(path.join(folder,'设计与检查.json'),'utf8'));
 const [w,h,d]=data.size,title=data.key.toUpperCase()+' · '+data.title+' · '+version;
 const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title>
 <style>*{box-sizing:border-box}body{margin:0;background:#121b2b;color:#e2edf5;font:14px/1.7 'Microsoft YaHei',sans-serif}a{color:#a8d9e9}header{padding:10px 20px}h1{font-size:22px;margin:0}.review{display:grid;grid-template-columns:1fr 340px;height:calc(100vh - 105px);min-height:620px}#stage{position:relative;overflow:hidden}#stage canvas,#labels{position:absolute;inset:0}#labels{pointer-events:none}.label{position:absolute;transform:translate(-50%,-50%);white-space:nowrap;background:#122737d9;padding:1px 4px;font-size:12px}.label.port{color:#ffcf8a}.label.controller{color:#ffecae;border:2px solid #ffdf61;background:#483b0ce8;z-index:5}#loading{position:absolute;z-index:6;padding:15px;background:#273e50}aside{overflow:auto;padding:12px 18px;background:#19293a}button{background:#2d455a;border:1px solid #647d8a;color:#ecf2f5;border-radius:4px;padding:6px 8px;margin:3px;cursor:pointer}.active{border-color:#e5d489}.locator{padding:10px;border:1px solid #a3914c;background:#34403c}input[type=range]{width:100%}details{border-top:1px solid #384f63;padding:10px 0}summary{cursor:pointer;font-weight:bold}.swatch{width:28px;height:28px;image-rendering:pixelated;vertical-align:middle;margin:4px}.material{display:block;padding:5px 0}.material small,small{display:block;color:#afc3d1;overflow-wrap:anywhere}.portrow{margin:10px 0}.portrow b{color:#efd49c;margin-right:5px}.ok{color:#afdbc0}@media(max-width:900px){.review{display:block;height:auto}#stage{height:65vh;min-height:420px}}</style>
 <header><a href="../index.html#${esc(data.key)}">← 全部21形态</a><h1>${esc(title)}</h1><div>${w}×${d}×${h}（宽深高） · ${data.block_count.toLocaleString()}方块 · 可旋转、剖切及逐口定位</div></header>
 <main class="review"><section id="stage"><div id="loading">加载本机逐格数据与离线纹理…</div><div id="labels"></div></section><aside>
 <div id="viewName"></div><div class="locator"><b>主控 [${data.controller.join(', ')}]</b>${Number.isInteger(data.controller_centering?.center_column_1based)?`<p>宽${w}格的第${data.controller_centering.center_column_1based}格，X=${data.controller_centering.center_x_0based}。</p>`:data.controller_centering?.summary?`<p>${esc(data.controller_centering.summary)}</p>`:''}<p>黄色轮廓始终显示；钻石块是位置标记。</p><button data-view="controller">定位主控</button></div>
 <div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧</button><button data-view="top">俯视</button><button data-view="panel">接口分布</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
 <p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
 <label><input id="showGlass" type="checkbox" checked>玻璃</label> <label><input id="showPorts" type="checkbox">接口</label> <label><input id="showPaths" type="checkbox">通道</label> <label><input id="showZones" type="checkbox">分区</label>
 <p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
 <details open><summary>本次结构修改</summary><p>${esc(data.controller_centering?.summary??data.controller_centering?.principle??data.integration_revision.summary??data.integration_revision.principle??data.integration_revision.concept??'控制器及接口嵌入实际设备壳面；详见设计与检查。')}</p></details>
 <details open><summary>逐口定位</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>逐种材质</summary><div id="materials"></div></details><details><summary>实际检查</summary><div id="checks"></div></details>
 <details><summary>结构文件与边界</summary><a href="${esc(data.name)}.nbt">NBT</a> · <a href="${esc(data.name)}.schem">Schematic</a> · <a href="设计与检查.json">记录</a><p>${audit.not_verified.map(esc).join('；')}</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script><!-- 变更记录#1：2026-10-23 10:57:25；新融合候选离线评审，不代表正式接入。 --></html>`;
 await fs.writeFile(path.join(folder,'viewer.bundle.js'),bundle,'utf8');await fs.writeFile(path.join(folder,'三维评审.html'),html,'utf8');
 console.log(data.key+' 三维页生成');
}
