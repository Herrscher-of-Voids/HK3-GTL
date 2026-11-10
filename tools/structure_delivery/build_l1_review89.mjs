/**
 * 候选89离线评审页：复用旧查看器、Three和实例真实材质，只写独立候选目录。
 * 【变更记录 #1】2026-09-27 03:28:00
 * 删除：无。新增：五机入口、动态尺寸视角、逐类材质隐藏、同源数据内嵌。
 * 修改：在内存中适配旧I03查看器，不覆盖旧脚本，不操作游戏和正式结构。
 * 用途：交付可离线审核的建筑候选；打包成功不等于浏览器交互或游戏验收。
 * 【变更记录 #2】2026-09-27 03:37:51：增加接口调整版独立输出、说明与接口近景，保留第一版。
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
// 【变更记录 #3】2026-09-27 03:42:11：新增统一地板版独立页面，显示可选接口位而不改变必要仓室规则。
const layout3=process.env.HK3_REVIEW_LAYOUT==='3';
const layout2=layout3||process.env.HK3_REVIEW_LAYOUT==='2';
const base=path.join(root,'doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89'+(layout3?'_统一地板':layout2?'_接口调整':''));
const logDir=path.join(root,'logs/revision89',layout3?'layout3':layout2?'layout2':'');
await fs.mkdir(logDir,{recursive:true});
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
let viewer=await fs.readFile(path.join(root,'tools/structure_delivery/i03-review-viewer.mjs'),'utf8');
// 原片段必须匹配一次，避免旧查看器变化时静默生成残留I03坐标的页面。
function replace(before,after){
  if(!viewer.includes(before))throw new Error('查看器适配片段不存在：'+before.slice(0,100));
  viewer=viewer.replace(before,after);
}
replace('const {data,materials,audit}=window.REVIEW;',`const {data,materials,audit,names}=window.REVIEW;
const [W,H,D]=data.size,cx=W/2,cz=D/2,hiddenMaterials=new Set();`);
replace('controls.target.set(12,10,14)','controls.target.set(cx,H*.4,cz)');
replace('set(12,-.035,14)','set(cx,-.035,cz)');
replace('set(12,-.015,14)','set(cx,-.015,cz)');
replace('sun.position.set(-20,65,-25)','sun.position.set(cx-35,H+40,cz-40);sun.target.position.set(cx,H*.3,cz);scene.add(sun.target)');
replace('left:-40,right:40,top:40,bottom:-40,near:1,far:150','left:-65,right:65,top:65,bottom:-65,near:1,far:240');
replace('line([[0,.1,-2],[25,.1,-2]]);line([[-2,.1,0],[-2,.1,29]]);','line([[0,.1,-2],[W,.1,-2]]);line([[-2,.1,0],[-2,.1,D]]);');
replace('for(const x of [0,25])','for(const x of [0,W])');
replace('for(const z of [0,29])','for(const z of [0,D])');
replace("label('25 格',[12.5,.4,-2],'dimension');label('29 格',[-2,.4,14.5],'dimension');","label(W+' 格',[cx,.4,-2],'dimension');label(D+' 格',[-2,.4,cz],'dimension');");
replace('if(b.pos[1]>layer||(!glass&&mesh.userData.material.transparent))continue;','if(b.pos[1]>layer||hiddenMaterials.has(b.state)||(!glass&&mesh.userData.material.transparent))continue;');
replace('mesh.computeBoundingSphere();count+=n;','mesh.visible=n>0;if(n>0)mesh.computeBoundingSphere();count+=n;');
const viewStart=viewer.indexOf('const views={'),viewEnd=viewer.indexOf('\nfunction setView',viewStart);
if(viewStart<0||viewEnd<0)throw new Error('缺少视角配置');
viewer=viewer.slice(0,viewStart)+`const views={
front:{pos:[cx-60,H*.85+24,cz-65],target:[cx,H*.43,cz],name:'前左整体'},
right:{pos:[cx+60,H*.85+24,cz-65],target:[cx,H*.43,cz],name:'前右整体'},
back:{pos:[cx-60,H*.85+24,cz+65],target:[cx,H*.43,cz],name:'后侧接口与回路'},
top:{pos:[cx,H+100,cz],target:[cx,0,cz],name:'正俯视 · 占地与通道'},
inside:{pos:[cx+55,H*.7+25,cz-65],target:[cx,H*.22,cz],name:'分层剖面 · 玻璃隐藏'},
orthofront:{pos:[cx,H*.5,-90],target:[cx,H*.5,cz],name:'正前投影'},
orthoside:{pos:[-90,H*.5,cz],target:[cx,H*.5,cz],name:'正侧投影'}
};`+viewer.slice(viewEnd);
replace("name==='inside'?12:24","name==='inside'?Math.floor(H*.48):H-1");
replace("document.getElementById('reset').onclick=()=>setView('front');",`document.getElementById('reset').onclick=()=>{hiddenMaterials.clear();document.querySelectorAll('[data-material]').forEach(el=>el.checked=true);setView('front');};`);
replace("'I03-三维结构预览.png'","data.key+'-候选89-三维结构预览.png'");
const materialStart=viewer.indexOf('const display={'),materialEnd=viewer.indexOf("document.getElementById('checks')",materialStart);
if(materialStart<0||materialEnd<0)throw new Error('缺少材料列表入口');
viewer=viewer.slice(0,materialStart)+`document.getElementById('materials').innerHTML=materials.map((m,i)=>\`<label class="material"><input type="checkbox" checked data-material="\${i}"><img class="swatch" src="\${m.faces.north}"><span>\${names[m.state.split('[')[0]]??m.state} × \${audit.palette[m.state]}</span><small>\${m.state}</small></label>\`).join('');
for(const el of document.querySelectorAll('[data-material]'))el.onchange=()=>{const state=materials[+el.dataset.material].state;el.checked?hiddenMaterials.delete(state):hiddenMaterials.add(state);rebuild();};
`+viewer.slice(materialEnd);
replace("'✓ 结构双格式回读一致 · 10 个接口可达 · 两条通道净空通过'","'✓ 结构双格式逐格一致 · '+data.ports.length+' 个接口可达 · 主通道净空通过'");
replace('const half=28;','const half=Math.max(W,D,H)*.72*Math.max(1,1/(w/h));');
replace("l.el.style.display=show&&projected.z<1?'block':'none'","l.el.style.display=show&&projected.z<1&&projected.z>-1?'block':'none'");
if(layout2){
  viewer=viewer.replaceAll('后侧接口与回路','后侧设备与回路');
  replace('const views={',`const views={panel:{pos:[cx,6,-45],target:[cx,2,3],name:'正面集中接口'},`);
  replace('camera.zoom=1;','camera.zoom=name===\'panel\'?3.8:1;');
  replace("name==='back';","['back','panel'].includes(name);");
}
const compiled=await rolldown({input:'virtual:review89',plugins:[{name:'候选89入口',resolveId(id){if(id==='virtual:review89')return id},load(id){if(id==='virtual:review89')return viewer}}],
  resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
const bundle=await compiled.generate({format:'iife',minify:true});await compiled.close();
await fs.writeFile(path.join(base,'viewer.bundle.js'),bundle.output.find(v=>v.type==='chunk').code,'utf8');
await fs.writeFile(path.join(logDir,'viewer-adapted.mjs'),viewer,'utf8');
await fs.copyFile(path.join(skill,'node_modules/three/LICENSE'),path.join(base,'Three许可.txt'));
const names={
  'gtceu:max_machine_casing':'MAX机械方块','gtceu:computer_casing':'计算机机壳','gtceu:high_power_casing':'高功率机壳',
  'gtceu:superconducting_coil':'超导线圈','gtceu:fusion_glass':'聚变玻璃','gtceu:laminated_glass':'夹层玻璃',
  'gtceu:computer_heat_vent':'计算机散热口','gtceu:filter_casing':'过滤机壳','gtceu:sterilizing_filter_casing':'灭菌过滤机壳',
  'gtceu:engine_intake_casing':'进气机壳','gtceu:advanced_computer_casing':'先进计算机机壳','gtceu:heat_vent':'散热口',
  'gtlcore:molecular_casing':'分子机械方块','gtlcore:iridium_casing':'铱机壳','gtlcore:enhance_hyper_mechanical_casing':'增强超维机械机壳',
  'gtlcore:qft_coil':'量子场线圈','gtlcore:rhenium_reinforced_energy_glass':'铼强化能量玻璃','gtlcore:graviton_field_constraint_casing':'引力子场约束机壳',
  'gtlcore:law_filter_casing':'法则过滤机壳','gtlcore:super_computation_component':'超级计算组件','gtlcore:process_machine_casing':'处理机壳',
  'gtlcore:dimension_connection_casing':'维度连接机壳','gtlcore:hyper_core':'超维核心','gtlcore:hsss_reinforced_borosilicate_glass':'HSSS强化硼硅玻璃',
  'gtlcore:super_cooler_component':'超级冷却组件','kubejs:module_base':'模块基座','kubejs:module_connector':'模块连接器',
  'kubejs:dimensional_stability_casing':'维度稳定机壳','kubejs:laser_cooling_casing':'激光冷却机壳','kubejs:accelerated_pipeline':'加速管道机壳',
  'kubejs:hollow_casing':'中空机壳','kubejs:molecular_coil':'分子线圈','kubejs:neutronium_pipe_casing':'中子素管道机壳',
  'kubejs:neutronium_gearbox':'中子素齿轮箱','minecraft:diamond_block':'主控占位标记','minecraft:diamond_ore':'接口占位标记'
};
const template=await fs.readFile(path.join(root,'tools/structure_delivery/i03-review-template.html'),'utf8');
const manifests=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
const allStates=new Set();
for(const entry of manifests){
  const out=path.join(base,entry.key);
  const [data,materials,audit]=await Promise.all(['blueprint.json','materials.json','audit.json'].map(async n=>JSON.parse(await fs.readFile(path.join(out,n),'utf8'))));
  for(const m of materials)if(!m.state.startsWith('minecraft:'))allStates.add(m.state);
  const [w,h,d]=data.size;
  let html=template.replaceAll('I03 崩坏能分馏中心',data.title).replaceAll('实物样例评审','候选89·待审核')
    .replaceAll('25 × 29 × 25',`${w} × ${d} × ${h}`).replaceAll('725 格²',`${w*d} 格²`).replace('普通级占地','候选外包络占地')
    .replace('高位分馏柱 × 卧式净化舱 × 可达接口带　／　建筑评审样例 v1','GT工业＋崩坏科技 / 候选89 · 待审核')
    .replace('id="layer" min="0" max="24" value="24"',`id="layer" min="0" max="${h-1}" value="${h-1}"`)
    .replace('id="layerValue">24','id="layerValue">'+(h-1))
    .replace('<button data-view="inside">内部剖面</button>','<button data-view="inside">内部剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button>')
    .replace('<h2>01 ／ 查看建筑</h2>','<p><a class="link" href="../index.html">← 返回五机总览</a></p><h2>01 ／ 查看建筑</h2>')
    .replace('<h2>03 ／ 方块搭配</h2>','<h2>03 ／ 方块搭配</h2><p class="muted">取消勾选可隐藏一类方块，便于观察内部。名称为评审简写，准确注册ID列在下方。</p>')
    .replace(/<details><summary>工艺与搭建说明<\/summary>[\s\S]*?<\/details>/,`<details open><summary>本机设计</summary><p>${data.description}</p><p>本机 ${data.ports.length} 个接口位，钻石矿占位；主控为钻石块。必要接口的数量约束仍待正式Pattern接入。</p><p>原点为前左下角，正面为-Z；本地控制器坐标 (${data.controller.join(', ')})。主通道宽3格、净高4格。</p><p>底部放在Y=-60时，最高方块位于Y=${h-61}；结构Offset=(0,0,0)。此轮仅提供审核候选。</p></details>`)
    .replace('已扫描实例 KubeJS、配置和数据目录的静态引用。材料模型与纹理可用不等于已证明所有生存前置；完整运行时配方、动态材质染色、成型和生产尚未验收。','选材来自本次980个候选状态的资源扫描，786个通过完整立方体模型与贴图解析。材料不受生存阶段限制，按负责人覆盖要求执行。静态模型解析未验证运行时碰撞、注册与机器成型。三维交互未自动实测，材质使用首帧。')
    .replaceAll('hk3gtl-i03-fractionation-review-v1',data.name).replace('2026-09-25','2026-09-27')
    .replace('/*__PAYLOAD__*/',()=>`window.REVIEW=${JSON.stringify({data,materials,audit,names}).replaceAll('<','\\u003c')};`)
    .replace('<script>/*__VIEWER__*/</script>','<script src="../viewer.bundle.js"></script>')
    .replace('</style>', '.material{display:block;padding:6px;border:1px solid #2a3951;border-radius:4px}.material input{vertical-align:middle;margin-right:7px}.material small{margin-left:0}header .muted{font-size:12px}</style>');
  if(layout2)html=html.replaceAll('候选89','候选89·接口调整版').replace('主通道宽3格、净高4格。','检修路线沿设备自然空隙绕行，宽3格、净高4格；主体方块零切除。主控与前后中轴线居中，全部接口集中在正面面板，最多两层。').replace('后侧接口','后侧').replace('<button data-view="front"','<button data-view="panel">接口近景</button><button data-view="front"');
  if(layout3)html=html.replaceAll('接口调整版','统一地板版').replace('必要接口的数量约束仍待正式Pattern接入。','地板统一灰色模块基座；保留顶部与左右白色外框，框内除居中主控外全部为接口位置。E编号为新增可选槽，可用工业接口机械方块封闭；原有必要仓室数量和并行上限不变，仍待正式Pattern接入。');
  if(html.includes('/*__'))throw new Error('页面占位符未处理');
  await fs.writeFile(path.join(out,'三维评审.html'),html,'utf8');
}
const cards=manifests.map(m=>`<a class="card" href="${m.key}/三维评审.html"><img src="${m.key}/等轴预览.png" alt="${m.title}"><div class="copy"><span class="tag">${m.key.toUpperCase()} / 三维审核</span><h2>${m.title.slice(4)}</h2><p>${m.description}</p><p class="meta">${m.size.join(' × ')}（宽×高×深）<br>${m.blocks.toLocaleString()}实体 · ${m.materials-2}种建材＋2种标记</p><span class="enter">旋转、剖开与查看材料 →</span></div></a>`).join('');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>L1五机 · 候选89审核</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0c1220;color:#e5edf7;font:15px/1.7 "Microsoft YaHei",system-ui,sans-serif}main{max-width:1460px;margin:auto;padding:40px 28px 64px}.eyebrow{color:#8ce3dc;letter-spacing:3px;font-size:12px}h1{font-size:34px;margin:10px 0}header p{max-width:960px;color:#adbcd2}.summary{display:flex;gap:12px;flex-wrap:wrap;margin:24px 0}.summary span{background:#172638;border:1px solid #35495d;padding:10px 18px;border-radius:5px}.summary b{color:#95eadd}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:24px}.card{display:block;text-decoration:none;color:inherit;background:#131d2d;border:1px solid #304156;border-radius:8px;overflow:hidden}.card:hover{border-color:#8ce3dc;transform:translateY(-2px)}.card img{width:100%;height:420px;object-fit:contain;background:#131a28}.copy{padding:20px 24px}.tag{font-size:11px;color:#8ce3dc;letter-spacing:2px}h2{font-size:23px;margin:7px 0 12px}.copy p{color:#afbdd2;font-size:13px}.meta{padding-top:12px;border-top:1px solid #304156}.enter{color:#a6eee3;font-size:14px}.note{margin:28px 0;padding:18px 22px;border-left:3px solid #c8ab75;background:#1b202b;color:#becbe0}details{border:1px solid #304156;padding:18px 22px;margin-top:26px}summary{cursor:pointer;color:#8ce3dc}a{color:#a6eee3}.overview{width:100%;margin-top:18px}footer{font-size:12px;color:#8e9eb6;margin-top:30px}@media(max-width:520px){main{padding:24px 14px}h1{font-size:27px}.grid{grid-template-columns:1fr}.card img{height:360px}}
</style></head><body><main><header><div class="eyebrow">HK3GTL / L1 / DESIGN REVIEW 89</div><h1>五座机器，五种工业轮廓</h1><p>冠式采集塔、贯通分析阵列、阶梯分馏塔群、裂瓣稳定塔与回廊再生中心。扩充GTCEu、GTLCore与KubeJS材质，把滤网、通风、冷却、计算和场约束构件放在各自的工艺位置。</p></header>
<div class="summary"><span><b>${allStates.size}</b> 种建材状态 / 五机合计去重</span><span><b>18–20</b> 种建材 / 每机</span><span><b>5</b> 个离线三维页面</span></div>
<div class="note">待审核候选，正式Pattern与游戏实例尚未替换。点击任意机器进入三维页面；左键旋转、右键平移、滚轮缩放，可分层、隐藏玻璃或指定材料。钻石块和钻石矿分别表示主控与接口位置。</div>
<section class="grid">${cards}</section><details><summary>整包选材与验证边界</summary><p>本次扫描980个候选状态，786个通过完整立方体模型和真实贴图解析。最终五机使用${allStates.size}种普通建材状态；每台另有钻石块、钻石矿两种标记。图像和三维均使用结构同源的逐格坐标。</p><p>GTLAdditions 3.3也已调查：JAR中未发现静态blockstates，主要取得机器及仓室资源；未据此虚构独立建材。未穷尽的动态注册仍记为调查缺口。</p><p>蓝图、原版NBT与Sponge已逐格回读一致；几何连通、主通道净空、所有接口步行可达检查通过。尚未做浏览器交互实测、运行时注册与碰撞核验，也未做游戏成型、生产验收。预览采用材质首帧，不模拟全部游戏渲染效果。</p><p><a href="manifest.json">五机清单</a> · <a href="Three许可.txt">Three.js许可</a></p></details>
<details><summary>五机静态总览</summary><img class="overview" src="五机总览.png" alt="五机真实方块材质等轴图"></details><footer>2026-09-27 · 候选89 · 全部资源离线打包 · 等轴图为本地坐标与纹理渲染，非游戏截图。</footer></main></body></html>`;
const finalHtml=layout2?html.replaceAll('候选89','候选89·接口调整版').replace('五座机器，五种工业轮廓','主控居中 · 接口集中 · 通道绕行').replace('待审核候选，正式Pattern与游戏实例尚未替换。','本版主控位于正面中轴、接口集中为左右两组且最多两层；恢复被旧通道切掉的设备，去除地面散布的2×2装饰墩。正式Pattern与游戏实例尚未替换。'):html;
const materialRange=`${Math.min(...manifests.map(m=>m.materials-2))}–${Math.max(...manifests.map(m=>m.materials-2))}`;
const deliveryHtml=(layout3?finalHtml.replaceAll('接口调整版','统一地板版').replace('主控居中 · 接口集中 · 通道绕行','统一灰色地板 · 白色外框与集中接口').replace('本版主控位于正面中轴、接口集中为左右两组且最多两层；','本版全部地板统一灰色模块基座；正面保留原有白色外框，框内两层除居中主控外全部为接口位置。新增E编号为可选槽，原有必要仓室规则不变；'):finalHtml).replaceAll('18–20',materialRange);
await fs.writeFile(path.join(base,'index.html'),deliveryHtml,'utf8');
console.log(JSON.stringify({pages:6,distinct_material_states:allStates.size,output:base,browser_interaction_tested:false}));

// 【变更记录 #4】2026-09-27 03:45:00：修正页面说明，保留白色外框、框内全接口与统一灰色地板。
