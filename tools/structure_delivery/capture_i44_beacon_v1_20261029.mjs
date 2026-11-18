/** I44信标候选：file协议离线截图、真实材质和全部评审控件核验。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.resolve(process.argv[2]??path.join(root,'deliveries/I44_仿制的千界一乘信标_双楔准星与轴向观测坞_V1_20261029'));
const log=path.join(root,'logs/i44-beacon-v1-20261029');
await fs.mkdir(log,{recursive:true});
const expected=JSON.parse(await fs.readFile(path.join(output,'manifest.json'),'utf8'));
const verification=JSON.parse(await fs.readFile(path.join(output,'verification.json'),'utf8'));
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const errors=[],consoleErrors=[],failedRequests=[],externalRequests=[];
const observe=page=>{
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',e=>{if(e.type()==='error')consoleErrors.push(e.text());});
  page.on('requestfailed',r=>failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
  page.on('request',r=>{if(/^https?:/.test(r.url()))externalRequests.push(r.url());});
};
const page=await browser.newPage({viewport:{width:2560,height:1700},deviceScaleFactor:1});
observe(page);
let info,broken=[];
try{
  await page.goto(pathToFileURL(path.join(output,'i44/三维评审.html')).href);
  await page.waitForFunction(()=>window.REVIEW_READY&&document.getElementById('status')?.textContent==='三维表面已就绪。',null,{timeout:120000});
  info=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,textures:window.REVIEW.materials.length,
    readback:window.REVIEW.audit.readback.geometry_nbt_schematic_per_block_equal,
    rendered_quads:window.REVIEW.audit.viewer_rendered_quads,draw_calls:window.reviewApi.renderer.info.render.calls,
    title:document.title,viewport:innerWidth,content:document.documentElement.scrollWidth,
    controller:window.REVIEW.data.controller,controller_face:window.REVIEW.data.controller_face,
    camera_presets:[...document.querySelectorAll('[data-view]')].map(e=>e.dataset.view),
    material_controls:document.querySelectorAll('[data-material]').length,port_controls:document.querySelectorAll('[data-port]').length}));
  if(expected.key!=='i44'||info.blocks!==expected.blocks||info.blocks!==verification.blocks
    ||info.textures!==expected.unique_materials||expected.unique_materials!==verification.unique_materials
    ||expected.ordinary_materials!==verification.ordinary_materials||!info.readback
    ||!verification.readback?.geometry_nbt_schematic_per_block_equal||info.rendered_quads!==verification.viewer_rendered_quads
    ||info.material_controls!==expected.unique_materials||info.port_controls!==8||expected.ports.length!==8
    ||info.controller.join(',')!=='120,22,0'||info.controller_face!=='north'||!info.title.startsWith('I44'))throw new Error('I44实体、主控、真实材质、逐格回读或控件合同不符');
  const sources=await page.locator('#materialSources tbody tr').evaluateAll(rows=>rows.map(row=>({
    source:row.cells[0].textContent,blocks:Number(row.cells[1].textContent.replaceAll(',','')),percentage:row.cells[2].textContent})));
  const markerCount=sources.filter(row=>row.source.endsWith('标记')).reduce((sum,row)=>sum+row.blocks,0);
  if(sources.length!==7||sources.reduce((sum,row)=>sum+row.blocks,0)!==expected.blocks
    ||Object.entries(verification.material_source_counts).some(([name,count])=>sources.find(row=>row.source===name)?.blocks!==count)
    ||sources.some(row=>!row.source.endsWith('标记')&&row.percentage!==(row.blocks/(expected.blocks-markerCount)*100).toFixed(3)+'%'))throw new Error('独立预览材料来源或占比统计不符');
  const presets=['controller','front','right','back','top','inside','orthofront','orthoside','texture'];
  if(presets.some(name=>!info.camera_presets.includes(name))||info.camera_presets.length!==9)throw new Error('9个视角预设不完整');
  const style=await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  const views=[['front','完整预览.png'],['back','信标后方.png'],['top','信标俯视.png'],['controller','主控材质近景.png']];
  for(const [view,file] of views){
    await page.evaluate(name=>{
      window.reviewApi.setView(name);
      for(const id of ['showPorts','showZones']){const el=document.getElementById(id);el.checked=false;el.dispatchEvent(new Event('change'));}
    },view);
    await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
    await page.evaluate(()=>window.reviewApi.renderer.render(window.reviewApi.scene,window.reviewApi.camera));
    await page.locator('#stage').screenshot({path:path.join(output,file)});
    console.log(JSON.stringify({screenshot_ready:path.join(output,file),view}));
  }
  await style.evaluate(e=>e.remove());
  await page.setViewportSize({width:1440,height:1000});
  for(const name of presets){
    await page.locator(`[data-view="${name}"]`).click();
    const valid=await page.evaluate(()=>{
      const c=window.reviewApi.camera;
      return [...c.position.toArray(),...c.projectionMatrix.elements].every(Number.isFinite);
    });
    if(!valid)throw new Error('视角包含非法相机矩阵：'+name);
  }
  await page.locator('[data-view="inside"]').click();
  await page.locator('#layer').evaluate(e=>{e.value='80';e.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.waitForFunction(()=>document.getElementById('layerValue').textContent==='80');
  await page.locator('[data-view="front"]').click();
  const visibleGlass=await page.evaluate(()=>{
    let count=0;window.reviewApi.scene.traverse(o=>{if(o.isInstancedMesh&&o.count>0&&o.userData.material?.transparent&&o.visible)count++;});return count;
  });
  if(!visibleGlass)throw new Error('未找到可见透明材质实例，无法核验玻璃切换');
  await page.locator('#showGlass').uncheck();
  await page.waitForFunction(()=>{
    let visible=0;window.reviewApi.scene.traverse(o=>{if(o.isInstancedMesh&&o.count>0&&o.userData.material?.transparent&&o.visible)visible++;});return visible===0;
  });
  await page.locator('#showGlass').check();
  for(const id of ['showZones','showPaths','showPorts']){
    await page.locator('#'+id).check();
    if(!await page.locator('#'+id).isChecked())throw new Error('控件未启用：'+id);
    await page.locator('#'+id).uncheck();
  }
  await page.locator('summary').filter({hasText:'真实材质与用量'}).click();
  const firstMaterial=page.locator('[data-material]').first();
  const materialState=await firstMaterial.getAttribute('data-material');
  await firstMaterial.uncheck();
  await page.waitForFunction(state=>{
    let visible=0;window.reviewApi.scene.traverse(o=>{if(o.isInstancedMesh&&o.userData.material?.state===state&&o.visible)visible++;});return visible===0;
  },materialState);
  await firstMaterial.check();
  for(let i=0;i<expected.ports.length;i++){
    await page.locator(`[data-port="${i}"]`).click();
    const caption=await page.locator('#viewName').textContent();
    if(!caption.includes(expected.ports[i].id)||!caption.includes(expected.ports[i].pos.join(', '))
      ||!await page.locator('#showPorts').isChecked())throw new Error('接口定位回执不符：'+i);
  }
  await page.locator('#reset').click();
  if(await page.locator('[data-material]:not(:checked)').count())throw new Error('重置未恢复全部材质');
  const downloadWait=page.waitForEvent('download');
  await page.locator('#saveImage').click();
  const download=await downloadWait;
  if(!download.suggestedFilename().includes('双楔准星与轴向观测坞'))throw new Error('保存视角仍使用旧机器文件名');
  await page.locator('summary').filter({hasText:'真实材质与用量'}).click();
  await page.locator('[data-view="front"]').click();
  await page.waitForTimeout(400);
  const idleStart=await page.evaluate(()=>window.reviewApi.renderer.info.render.frame);
  await page.waitForTimeout(400);
  const idleEnd=await page.evaluate(()=>window.reviewApi.renderer.info.render.frame);
  if(idleStart!==idleEnd)throw new Error('静止时仍持续绘制，按需渲染未生效');
  await page.screenshot({path:path.join(log,'评审页面.png')});
  const index=await browser.newPage();observe(index);
  await index.goto(pathToFileURL(path.join(output,'index.html')).href);
  const indexLinks=await index.locator('a[href]').evaluateAll(es=>es.map(e=>e.href));
  if(views.some(([,file])=>!indexLinks.some(link=>decodeURIComponent(new URL(link).pathname).endsWith('/'+file))))throw new Error('总览缺少指定截图链接');
  await index.screenshot({path:path.join(log,'交付总览.png'),fullPage:true});
  const links=[...await page.locator('a[href]').evaluateAll(es=>es.map(e=>e.href)),...indexLinks];
  for(const link of [...new Set(links.filter(x=>x.startsWith('file:'))) ]){
    const url=new URL(link);url.hash='';url.search='';
    try{await fs.access(fileURLToPath(url));}catch{broken.push(link);}
  }
  if(errors.length||consoleErrors.length||failedRequests.length||externalRequests.length||broken.length)throw new Error(JSON.stringify({errors,consoleErrors,failedRequests,externalRequests,broken}));
  const result={passed:true,...info,errors,console_errors:consoleErrors,failed_requests:failedRequests,external_requests:externalRequests,
    broken_local_links:broken,offline_file_html_tested:true,index_screenshot_links_tested:true,views:views.map(x=>x[0]),camera_buttons_tested:presets,
    layer_slider_tested:true,glass_toggle_tested:true,material_toggle_tested:true,port_buttons_tested:expected.ports.length,
    zone_path_port_toggles_tested:true,reset_tested:true,save_image_tested:true,saved_image_filename:download.suggestedFilename(),
    render_on_demand_tested:true,idle_render_frames:[idleStart,idleEnd],screenshots:views.map(x=>x[1]),material_sources:sources,
    material_source_breakdown_tested:true,approved:false,installed:false,game_performance_tested:false,verified_at:new Date().toISOString()};
  await fs.writeFile(path.join(log,'browser-verification.json'),JSON.stringify(result,null,2)+'\n','utf8');
  console.log(JSON.stringify(result));
}catch(error){
  await fs.writeFile(path.join(log,'browser-verification.json'),JSON.stringify({passed:false,...info,error:String(error),errors,
    console_errors:consoleErrors,failed_requests:failedRequests,external_requests:externalRequests,broken_local_links:broken,
    approved:false,installed:false,verified_at:new Date().toISOString()},null,2)+'\n','utf8');
  throw error;
}finally{await browser.close();}
