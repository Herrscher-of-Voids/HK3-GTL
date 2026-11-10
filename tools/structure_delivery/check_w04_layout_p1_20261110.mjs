/** 核验组合模型摆位、全静态显示与完整取景，不操作游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W04_龙踞雷池七雷镇枢_组合布局_P1_20261110');
const log=path.join(root,'logs/w04-layout-p1-20261110');
const skill=path.join(process.env.USERPROFILE,'.codex/skills/minecraft-builder-skill');
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1600,height:1150},deviceScaleFactor:1});
const errors=[],failed=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
function assert(value,message){if(!value)throw new Error(message);}
try{
  await page.goto(pathToFileURL(path.join(out,'三维布局.html')).href);
  await page.waitForFunction(()=>window.W04_STATIC_READY,null,{timeout:120000});
  await page.waitForFunction(()=>window.W04_REVIEW_READY,null,{timeout:120000});
  const before=await page.evaluate(()=>window.W04Static.snapshot());await page.waitForTimeout(800);
  const after=await page.evaluate(()=>window.W04Static.snapshot());
  assert(before.frames===after.frames,'预览持续重绘');
  assert(JSON.stringify(before.transforms)===JSON.stringify(after.transforms),'模型出现动画');
  assert(before.transforms.length===14,'龙与刀部件不齐');
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}'});
  await page.waitForFunction(()=>window.W04Static.renderer.domElement.clientWidth===innerWidth);
  const views=[];
  for(const [view,file] of [['front','整体斜视'],['orthofront','正面'],['side','侧面'],['back','背面'],['top','俯视'],
    ['reactor','雷池与刀尖'],['dragon','龙体'],['sword','七雷'],['controller','控制器位置']]){
    await page.evaluate(view=>window.W04Static.setView(view),view);
    if(['front','orthofront','side','back','top'].includes(view)){
      const limit=await page.evaluate(()=>{
        const a=window.W04Static,p=a.camera.position.clone();let limit=0;
        for(const v of a.config.data.fit_points){p.fromArray(v).project(a.camera);limit=Math.max(limit,Math.abs(p.x),Math.abs(p.y));}
        return limit;
      });assert(limit<=.9,'完整取景裁切：'+view);views.push({view,projectedLimit:limit});
    }
    await page.locator('#stage').screenshot({path:path.join(out,file+'.png')});
  }
  // 恢复页面排版后验证模型与草模的显隐控件。
  await page.evaluate(()=>document.querySelectorAll('style').forEach(s=>{if(s.textContent.includes('position:fixed!important'))s.remove();}));
  await page.locator('[data-asset="dragon"]').uncheck();
  assert(await page.evaluate(()=>window.W04Static.groups.filter(g=>g.name.startsWith('dragon_')).every(g=>!g.visible)),'龙体显隐失败');
  await page.locator('[data-asset="dragon"]').check();
  await page.locator('[data-asset="sword"]').uncheck();
  assert(await page.evaluate(()=>window.W04Static.groups.filter(g=>g.name.startsWith('sword_')).every(g=>!g.visible)),'刀显隐失败');
  await page.locator('[data-asset="sword"]').check();
  await page.locator('[data-scenery="energy"]').uncheck();
  assert(await page.evaluate(()=>!window.W04Static.sceneryGroups.energy.visible),'能量示意显隐失败');
  await page.locator('[data-scenery="energy"]').check();
  const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
  const [cx,cy,cz]=manifest.controller_world;
  assert(manifest.ports_world.length===8,'接口不是8个');
  for(const [x,y,z] of manifest.ports_world)assert(z===cz&&Math.abs(x-cx)<=1&&Math.abs(y-cy)<=1&&(x!==cx||y!==cy),'接口不在主控周围同面3×3');
  assert(manifest.dragon_sword_z_gap>65,'龙刀净空不足');
  await page.goto(pathToFileURL(path.join(out,'index.html')).href);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  for(const href of await page.locator('a').evaluateAll(a=>a.map(e=>e.getAttribute('href'))))
    if(!/^(https?:|#)/.test(href)&&href!=='verification.json')await fs.access(path.resolve(out,href));
  assert(!errors.length&&!failed.length,JSON.stringify({errors,failed}));
  const qa={passed:true,static:true,desktop_used:false,game_verified:false,screenshots:9,views,parts:14,
    source_models:'D4龙体与S1鸣雷见的完整合并表面，整体摆位；无源网格变形',
    dragon_sword_z_separation:manifest.dragon_sword_z_gap,
    separation_scope:'完整龙与刀的前后包围区间分离；不等于整机所有草模的逐格碰撞验收',
    ports_adjacent_3x3:true,industrial_geometry:'草模',errors,failed};
  await fs.writeFile(path.join(out,'verification.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(qa,null,2)+'\n');
  await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));
  console.log(JSON.stringify(qa));
}finally{await browser.close();}
