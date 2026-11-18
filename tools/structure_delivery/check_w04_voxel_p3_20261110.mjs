/** 核验P3整机真实方块显示、材质、原界面操作及完整取景。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W04_完整真实方块_露首环链修订_P3_20261110');
const log=path.join(root,'logs/w04-voxel-p3-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1,acceptDownloads:true});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
const assert=(v,m)=>{if(!v)throw new Error(m);};
try{
  await page.goto(pathToFileURL(path.join(out,'三维布局.html')).href);
  await page.waitForFunction(()=>window.W04_REVIEW_READY,null,{timeout:120000});
  await page.waitForTimeout(300);
  const snapshot=await page.evaluate(()=>W04Static.snapshot());await page.waitForTimeout(700);
  assert(JSON.stringify(snapshot)===JSON.stringify(await page.evaluate(()=>W04Static.snapshot())),'非静态或持续绘制');
  assert(snapshot.transforms.length===29,'部件数量错误');
  for(const t of snapshot.transforms){
    assert(t.scale.every(v=>v===1)&&t.rotation.every((v,i)=>v===(i===3?1:0)),'模型仍整体缩放或旋转');
    assert(t.position.every(Number.isInteger),'部件原点非整数');
  }
  const geometry=await page.evaluate(()=>{
    const a=W04Static;let integerVertices=true,repeatUV=false,textured=true;
    for(const group of a.groups)for(const mesh of group.children){
      integerVertices&&=[...mesh.geometry.getAttribute('position').array].every(Number.isInteger);
      repeatUV||=[...mesh.geometry.getAttribute('uv').array].some(v=>v>1);
      textured&&=!!mesh.material.map&&mesh.material.map.image?.width>0;
    }
    return {integerVertices,repeatUV,textured,scenery:Object.keys(a.sceneryGroups).length,
      blocks:a.config.parts.reduce((n,p)=>n+p.blocks,0),materials:a.config.materials.map(m=>m.state)};
  });
  assert(geometry.integerVertices&&geometry.repeatUV&&geometry.textured&&geometry.scenery===0,'真实整数格纹理几何不完整');
  const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
  assert(geometry.blocks===manifest.block_count,'整机数量错误');
  assert(await page.evaluate(()=>W04Review.metadata.source_voxels)===geometry.blocks,'材料表未使用整机最终数据');
  const sidebar=await page.locator('aside').boundingBox();assert(Math.abs(sidebar.width-340)<1,'右340像素评审栏被替换');
  await page.locator('#showGrid').check();assert(await page.evaluate(()=>W04Review.grid.visible),'网格失效');
  await page.locator('#showGrid').uncheck();
  await page.locator('#layer').fill('180');await page.locator('#layer').dispatchEvent('input');
  assert(await page.locator('#layerValue').textContent()==='180','逐层剖切失效');
  assert(await page.evaluate(()=>W04Static.groups[0].children[0].material.clippingPlanes[0].constant)<182,'剖切平面失效');
  await page.locator('#reset').click();await page.locator('#glass').uncheck();
  assert(await page.evaluate(()=>W04Static.groups.flatMap(g=>g.children).filter(m=>m.userData.glass).every(m=>!m.visible)),'玻璃开关失效');
  await page.locator('#glass').check();
  await page.locator('details').filter({has:page.locator('#materials')}).locator('summary').click();
  await page.locator('#materialSearch').fill('voltage_machine_casing_hrv');assert(await page.locator('.material:visible').count()===1,'材料搜索失效');
  await page.locator('[data-material="hk3gtl:voltage_machine_casing_hrv"]').uncheck();
  assert(await page.evaluate(()=>W04Static.groups.flatMap(g=>g.children).filter(m=>W04Static.config.materials[m.userData.material].state==='hk3gtl:voltage_machine_casing_hrv').every(m=>!m.visible)),'材质隐藏失效');
  await page.locator('#materialSearch').fill('');await page.locator('#reset').click();
  for(const asset of ['dragon','sword','field','base']){
    await page.locator(`[data-asset="${asset}"]`).uncheck();
    assert(await page.evaluate(asset=>W04Static.groups.filter(g=>g.name.startsWith(asset+'_')).every(g=>!g.visible),asset),'分组开关失效：'+asset);
    await page.locator(`[data-asset="${asset}"]`).check();
  }
  await page.locator('[data-view="controller"]').click();assert((await page.locator('#viewName').textContent()).includes('主控'),'主控定位失效');
  await page.locator('#ports').check();await page.locator('#ports').uncheck();
  const downloadPromise=page.waitForEvent('download');await page.locator('#saveImage').click();const download=await downloadPromise;
  assert((await fs.stat(await download.path())).size>10000,'截图下载失败');
  await page.locator('#fullscreen').click();await page.waitForFunction(()=>!!document.fullscreenElement);await page.evaluate(()=>document.exitFullscreen());
  await page.locator('#reset').click();
  const stage=await page.locator('#stage').boundingBox(),position=await page.evaluate(()=>W04Static.camera.position.toArray());
  await page.mouse.move(stage.x+stage.width/2,stage.y+stage.height/2);await page.mouse.down();
  await page.mouse.move(stage.x+stage.width/2+75,stage.y+stage.height/2+22,{steps:4});await page.mouse.up();
  assert(JSON.stringify(position)!==JSON.stringify(await page.evaluate(()=>W04Static.camera.position.toArray())),'相机旋转失效');
  await page.locator('#reset').click();await page.screenshot({path:path.join(out,'统一评审界面.png')});
  await page.setViewportSize({width:720,height:1000});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'窄屏横向溢出');
  await page.setViewportSize({width:1600,height:1150});
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await page.waitForFunction(()=>W04Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','整体斜视'],['orthofront','正面'],['side','侧面'],['back','背面'],['top','俯视'],
    ['head','龙首近景'],['casing','真实机壳近景'],['torii','三进鸟居'],['magnet','磁轭近景'],['sword','七雷'],['controller','控制器位置']]){
    await page.evaluate(v=>W04Static.setView(v),view);
    if(['front','orthofront','side','back','top'].includes(view)){
      const limit=await page.evaluate(()=>{
        const a=W04Static,s=a.config.data.size,p=a.camera.position.clone();let limit=0;
        for(const x of [0,s[0]])for(const y of [0,s[1]])for(const z of [0,s[2]]){p.set(x,y,z).project(a.camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}
        return limit;
      });assert(limit<=.9,'全景发生裁切：'+view);views.push({view,limit});
    }
    await page.locator('#stage').screenshot({path:path.join(out,file+'.png')});
  }
  await page.evaluate(()=>{const a=W04Static;a.setView('orthofront');a.groups.filter(g=>g.name.startsWith('sword_')).forEach(g=>g.visible=false);a.renderer.render(a.scene,a.camera);});
  await page.locator('#stage').screenshot({path:path.join(out,'正面隐藏七雷.png')});
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const href of await page.locator('a').evaluateAll(a=>a.map(e=>e.getAttribute('href'))))
    if(!/^(https?:|#)/.test(href)&&href!=='verification.json')await fs.access(path.resolve(out,href));
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  const source=JSON.parse(await fs.readFile(path.join(log,'geometry-qa.json'),'utf8'));
  assert(source.export.readback.geometry_nbt_schematic_per_block_equal,'完整导出回读失败');
  const qa={passed:true,static:true,screenshots:13,parts:29,whole_machine_voxel:true,no_scenery_meshes:true,integer_vertices:true,
    runtime_scale_identity:true,runtime_rotation_identity:true,all_meshes_real_textures:true,texture_repeats_per_block:true,
    original_review_ui:true,controls_verified:['逐层剖切','材料搜索显隐','玻璃','网格','四组显隐','主控定位','截图下载','全屏','旋转','窄屏'],
    views,geometry_readback:source.export.readback,export_hashes:source.export.hashes,head_visibility:source.head_visibility,
    collision_free:source.collision_report.unexpected_pairs===0,collision_report:source.collision_report,
    game_verified:false,controller_registered:false,errors,failed};
  await fs.writeFile(path.join(out,'verification.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify({passed:true,blocks:geometry.blocks,screenshots:13,views,collision_free:qa.collision_free}));
}finally{await browser.close();}
