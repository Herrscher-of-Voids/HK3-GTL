/** 四机评审打包：独立交付目录，沿用同一份逐格数据和本地纹理。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createBlueprint as early} from './early-line-buildings-v2.mjs';
import {createBlueprint as i03} from './i03-fractionation-v2.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const base=path.join(root,'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
// 在构建时适配第一版查看器，保留旧页与旧源码以便直接对照。
let viewer=await fs.readFile(path.join(root,'tools/structure_delivery/i03-review-viewer.mjs'),'utf8');
viewer=viewer.replace("const {data,materials,audit}=window.REVIEW;","const {data,materials,audit,controllerTextures}=window.REVIEW;\nconst [W,H,D]=data.size; const cx=W/2,cz=D/2;");
viewer=viewer.replace("controls.target.set(12,10,14)","controls.target.set(cx,H*.4,cz)")
  .replaceAll('set(12,-.035,14)','set(cx,-.035,cz)').replaceAll('set(12,-.015,14)','set(cx,-.015,cz)');
viewer=viewer.replace("const sides=['east','west','up','down','south','north'].map(face=>new THREE.MeshStandardMaterial({",`const controller=material.state==='minecraft:diamond_block';
  const sides=['east','west','up','down','south','north'].map(face=>new THREE.MeshStandardMaterial({`)
  .replace('map:texture(material.faces[face])',"map:texture(controller?(face==='north'?controllerTextures.idle:controllerTextures.shell):material.faces[face])");
viewer=viewer.replace('line([[0,.1,-2],[25,.1,-2]]);line([[-2,.1,0],[-2,.1,29]]);','line([[0,.1,-2],[W,.1,-2]]);line([[-2,.1,0],[-2,.1,D]]);')
  .replace('for(const x of [0,25])','for(const x of [0,W])').replace('for(const z of [0,29])','for(const z of [0,D])')
  .replace("label('25 格',[12.5,.4,-2],'dimension');label('29 格',[-2,.4,14.5],'dimension');","label(W+' 格',[cx,.4,-2],'dimension');label(D+' 格',[-2,.4,cz],'dimension');");
viewer=viewer.replace(/const views=\{[\s\S]*?\};\nfunction setView/,`const views={
front:{pos:[cx-46,H*.85+15,cz-52],target:[cx,H*.4,cz],name:'前左整体'},
right:{pos:[cx+46,H*.85+15,cz-52],target:[cx,H*.4,cz],name:'前右整体'},
back:{pos:[cx-42,H*.8+12,cz+52],target:[cx,H*.4,cz],name:'后侧接口'},
top:{pos:[cx,90,cz],target:[cx,0,cz],name:'正俯视 · 尺寸与通道'},
inside:{pos:[cx+44,40,cz-45],target:[cx,H*.25,cz],name:'分层剖面 · 玻璃隐藏'},
orthofront:{pos:[cx,H*.5,-70],target:[cx,H*.5,cz],name:'正前投影 · 排除透视错觉'},
orthoside:{pos:[-70,H*.5,cz],target:[cx,H*.5,cz],name:'正侧投影 · 模块对齐'},
controller:{pos:[data.controller[0]+2,data.controller[1]+1,data.controller[2]-7],target:data.controller.map(v=>v+.5),name:'专用控制器 · 实际纹理外观'}
};\nfunction setView`);
viewer=viewer.replace('camera.zoom=1;','camera.zoom=name===\'controller\'?7.5:1;')
  .replace("name==='inside'?12:24","name==='inside'?Math.min(12,H-1):H-1")
  .replace('const half=28;','const half=Math.max(W,D,H)*.83;')
  .replace("'I03-三维结构预览.png'","data.key+'-三维结构预览.png'")
  .replace("<span>钻石块标记<small>","<span>新控制器外观（投影中仍为钻石块）<small>")
  .replace("'✓ 结构双格式回读一致 · 10 个接口可达 · 两条通道净空通过'","'✓ 双格式逐格一致 · '+data.ports.length+' 个接口可达 · 通道净空通过'");
viewer+=`\ndocument.getElementById('controllerState').onchange=e=>{const m=stateMeshes.find(m=>m.userData.material.state==='minecraft:diamond_block');m.material[5].map=texture(controllerTextures[e.target.value]);m.material[5].needsUpdate=true;};
document.getElementById('controllerMarker').onchange=e=>{const m=stateMeshes.find(m=>m.userData.material.state==='minecraft:diamond_block');const faces=['east','west','up','down','south','north'];m.material.forEach((mat,i)=>{mat.map=texture(e.target.checked?m.userData.material.faces[faces[i]]:i===5?controllerTextures[document.getElementById('controllerState').value]:controllerTextures.shell);mat.needsUpdate=true;});};\n`;
const compiled=await rolldown({input:'virtual:review-v2',plugins:[{name:'虚拟评审入口',resolveId(id){if(id==='virtual:review-v2')return id},load(id){if(id==='virtual:review-v2')return viewer}}],
resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
const bundle=await compiled.generate({format:'iife',minify:true});await compiled.close();
const code=bundle.output.find(v=>v.type==='chunk').code;
const template=await fs.readFile(path.join(root,'tools/structure_delivery/i03-review-template.html'),'utf8');
const controllerLibrary=JSON.parse(await fs.readFile(path.join(base,'controllers.json'),'utf8'));
const manifests=[];
for(const key of ['i01','i02','s01','i03']){
  // 指定单台修订时复用其余三台清单，不重写无关结构和预览。
  if(process.env.HK3_REVIEW_ONLY && key!==process.env.HK3_REVIEW_ONLY){
    const existing=JSON.parse(await fs.readFile(path.join(base,'manifest.json'),'utf8'));
    manifests.push(existing.find(entry=>entry.key===key));continue;
  }
  const data=key==='i03'?i03():early(key);const out=path.join(base,key);await fs.mkdir(out,{recursive:true});
  await fs.writeFile(path.join(out,'blueprint.json'),JSON.stringify(data),'utf8');
  const env={...process.env,PYTHONUTF8:'1',HK3_REVIEW_MACHINE:key,HK3_REVIEW_OUT:out,HK3_REVIEW_NAME:data.name};
  const recipe=path.join(root,'tools/structure_delivery',key==='i03'?'i03-fractionation-v2.mjs':'early-line-buildings-v2.mjs');
  execFileSync(process.execPath,[path.join(skill,'scripts/run-build.mjs'),recipe,'--out-dir',out,'--name',data.name,'--no-block-state-updates','--json'],{cwd:skill,env,stdio:'inherit'});
  execFileSync('python',[path.join(root,'tools/structure_delivery/package_i03_review.py')],{cwd:root,env,stdio:'inherit'});
  const materials=JSON.parse(await fs.readFile(path.join(out,'materials.json'),'utf8'));
  const audit=JSON.parse(await fs.readFile(path.join(out,'audit.json'),'utf8'));
  const [w,h,d]=data.size;
  let html=template.replaceAll('I03 崩坏能分馏中心',data.title).replaceAll('25 × 29 × 25',`${w} × ${d} × ${h}`)
    .replaceAll('725 格²',`${w*d} 格²`).replace('高位分馏柱 × 卧式净化舱 × 可达接口带　／　建筑评审样例 v1',data.description+' ／ 建筑重设计 v2')
    .replace('id="layer" min="0" max="24" value="24"',`id="layer" min="0" max="${h-1}" value="${h-1}"`)
    .replace('id="layerValue">24','id="layerValue">'+(h-1))
    .replace('<button data-view="inside">内部剖面</button>','<button data-view="inside">内部剖面</button><button data-view="orthofront">正前投影</button><button data-view="orthoside">正侧投影</button><button data-view="controller">控制器近看</button>')
    .replace('<h2>02 ／ 功能接口</h2>',`<h2>控制器外观</h2><p>三维中展示新版纹理；结构文件仍使用钻石主控标记，避免伪造可运行控制器。</p><label>状态 <select id="controllerState"><option value="idle">空闲</option><option value="active">运行</option><option value="paused">暂停</option></select></label><label><input type="checkbox" id="controllerMarker"> 显示结构文件原始钻石标记</label><img style="width:128px;image-rendering:pixelated" src="${controllerLibrary[key].idle}"><h2>02 ／ 功能接口</h2>`)
    .replace(/<details><summary>工艺与搭建说明<\/summary>[\s\S]*?<\/details>/,`<details><summary>工艺与搭建说明</summary><p>${data.description}。保留现有机器功能和接口能力；不添加配方或更改研究扣费。</p><p>主控坐标 (${data.controller.join(',')})，正面 -Z。原点为前左下角；Offset=(0,0,0)。底部 Y=-60 时最高占用 Y=${h-61}。</p><p>研究所付款仍由玩家背包／研究点完成；其 H 接口保留原有可选崩坏能能力，不误标为物品输入仓。</p></details>`)
    .replaceAll('hk3gtl-i03-fractionation-review-v1',data.name)
    .replace('/*__PAYLOAD__*/',()=>`window.REVIEW=${JSON.stringify({data,materials,audit,controllerTextures:controllerLibrary[key]}).replaceAll('<','\\u003c')};`)
    .replace('/*__VIEWER__*/',()=>code.replaceAll('</script','<\\/script'));
  await fs.writeFile(path.join(out,'三维评审.html'),html,'utf8');
  manifests.push({key,title:data.title,name:data.name,size:data.size,blocks:data.blocks.length,ports:data.ports,sha256:audit.sha256});
}
await fs.writeFile(path.join(base,'manifest.json'),JSON.stringify(manifests,null,2),'utf8');
await fs.copyFile(path.join(skill,'node_modules/three/LICENSE'),path.join(base,'Three许可.txt'));
console.log('四台结构与预览同步完成。');
