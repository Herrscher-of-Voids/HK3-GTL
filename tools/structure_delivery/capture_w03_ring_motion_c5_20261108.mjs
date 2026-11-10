/** 无桌面操作：核验完整四环动画、静态缓存、暂停与剖切回退。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W03_C5_四环绕核运动_20261108');
const log=path.join(root,'logs/w03-ring-motion-c5-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1400,height:1200},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
function check(condition,message){if(!condition)throw new Error(message);}
try {
  await page.goto(pathToFileURL(path.join(out,'w03/三维评审.html')).href);
  await page.waitForFunction(()=>window.C5_READY,null,{timeout:180000});
  await page.evaluate(()=>window.W03Motion.pause(true));
  const loaded=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,
    full:window.W03Motion.originalMeshes.every(m=>m.userData.initialized===m.userData.indices.length),
    ...window.W03Motion.snapshot()}));
  check(loaded.blocks===6650713&&loaded.full,'完整C4载荷未就绪');
  check(JSON.stringify(loaded.stats.ring_counts)===JSON.stringify([30587,23041,19757,13499]),'四环缺面');
  const snapshots=await page.evaluate(()=>{
    const m=window.W03Motion,versions=()=>m.originalMeshes.map(o=>o.instanceMatrix.version);
    m.seek(0);const a=m.snapshot(),before=versions();
    m.seek(19);const b=m.snapshot();m.seek(360);const c=m.snapshot();
    return {a,b,c,before,after:versions()};
  });
  const near=(a,b)=>a.every((x,i)=>Math.abs(x-b[i])<1e-6);
  check(snapshots.a.pivots.every(p=>near(p,[288,366,264])),'环未围绕实际核心');
  check(snapshots.a.quaternions.every((q,i)=>!near(q,snapshots.b.quaternions[i])),'并非四环全部转动');
  check(snapshots.a.quaternions.every((q,i)=>Math.abs(q.reduce((s,v,j)=>s+v*snapshots.c.quaternions[i][j],0))>1-1e-6),'完整周期不闭合');
  check(JSON.stringify(snapshots.before)===JSON.stringify(snapshots.after),'动画重复上传静态实例矩阵');
  check(snapshots.a.stats.static_passes===snapshots.c.stats.static_passes,'纯动画未复用静态缓存');
  await page.getByRole('button',{name:'继续四环',exact:true}).click();
  await page.waitForFunction(start=>window.W03Motion.snapshot().seconds!==start,snapshots.c.seconds,{timeout:10000});
  await page.getByRole('button',{name:'暂停四环',exact:true}).click();
  const paused=await page.evaluate(()=>window.W03Motion.snapshot().seconds);
  await page.waitForTimeout(180);
  check(await page.evaluate(t=>window.W03Motion.snapshot().seconds===t,paused),'暂停无效');
  await page.locator('#motionTime').fill('37.5');
  check(await page.evaluate(()=>window.W03Motion.snapshot().seconds===37.5),'拖动时间无效');
  await page.getByRole('button',{name:'复位',exact:true}).click();
  check(await page.evaluate(()=>window.W03Motion.snapshot().seconds===0),'复位无效');
  await page.evaluate(()=>{const e=document.getElementById('layer');e.value='200';e.dispatchEvent(new Event('input'));window.reviewApi.rebuild();});
  await page.waitForFunction(()=>window.W03Motion.snapshot().sliced);
  await page.evaluate(()=>{window.reviewApi.setView('front');window.W03Motion.seek(0);});
  await page.waitForFunction(()=>!window.W03Motion.snapshot().sliced);
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
  await page.evaluate(()=>window.reviewApi.setView('front'));
  for(const [seconds,name] of [[0,'初始全景.png'],[19,'转动全景.png'],[47,'另一时相.png']]){
    await page.evaluate(t=>window.W03Motion.seek(t),seconds);
    await page.locator('#stage').screenshot({path:path.join(out,name)});
  }
  await fs.mkdir(path.join(log,'frames'),{recursive:true});
  for(let i=0;i<12;i++){
    await page.evaluate(t=>window.W03Motion.seek(t),i*2);
    await page.locator('#stage').screenshot({path:path.join(log,'frames',String(i).padStart(2,'0')+'.png')});
  }
  await page.evaluate(()=>{window.reviewApi.setView('orthofront');window.W03Motion.seek(19);});
  await page.locator('#stage').screenshot({path:path.join(out,'正面转动.png')});
  check(!errors.length&&!failed.length&&!external.length,JSON.stringify({errors,failed,external}));
  const result={passed:true,headless:true,desktop_used:false,game_started:false,loaded,
    four_rings_move:true,core_pivot_verified:true,full_cycle_closed:true,
    matrix_uploads_unchanged_during_animation:true,static_cache_reused:true,
    pause_seek_reset_and_slice_verified:true,snapshots,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({passed:true,ring_quads:loaded.stats.ring_counts,screenshots:4,animation_frames:12}));
}finally{await browser.close();}
