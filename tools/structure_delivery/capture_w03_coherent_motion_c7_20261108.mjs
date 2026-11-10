/** 无桌面操作：核验同步矩阵、连续净空证明对应的运动、指芯和完整取景。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/W03_C7_同步立体净空修订_20261108');
const log=path.join(root,'logs/w03-coherent-motion-c7-20261108');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1400,height:1100},deviceScaleFactor:1});
const errors=[],failed=[],external=[];
const proof=JSON.parse(await fs.readFile(path.join(out,'verification.json'),'utf8'));
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
function check(condition,message){if(!condition)throw new Error(message);}
try {
  await page.goto(pathToFileURL(path.join(out,'w03/三维评审.html')).href);
  await page.waitForFunction(()=>window.C7_READY,null,{timeout:180000});
  await page.evaluate(()=>window.W03Motion.pause(true));
  const loaded=await page.evaluate(()=>({blocks:window.REVIEW.audit.blocks,
    full:window.W03Motion.originalMeshes.every(m=>m.userData.initialized===m.userData.indices.length),
    components:window.W03Motion.config.components.map(c=>c.id), ...window.W03Motion.snapshot()}));
  check(loaded.blocks===6650713&&loaded.full,'完整C4载荷未就绪');
  check(loaded.stats.component_counts.length===33&&loaded.stats.component_counts.every(n=>n>0),'33组运动组件缺失');
  const snapshots=await page.evaluate(()=>{
    const m=window.W03Motion, versions=()=>m.originalMeshes.map(o=>o.instanceMatrix.version);
    m.seek(0);const a=m.snapshot(),before=versions();m.seek(19);const b=m.snapshot();m.seek(360);const c=m.snapshot();
    return {a,b,c,before,after:versions()};
  });
  const near=(a,b)=>a.every((x,i)=>Math.abs(x-b[i])<1e-6);
  check(snapshots.a.quaternions.every((q,i)=>!near(q,snapshots.b.quaternions[i])),'并非全体33组转动');
  check(snapshots.a.quaternions.every((q,i)=>Math.abs(q.reduce((s,v,j)=>s+v*snapshots.c.quaternions[i][j],0))>1-1e-6),'360秒周期不闭合');
  check(JSON.stringify(snapshots.before)===JSON.stringify(snapshots.after),'动画重复上传原始实例矩阵');
  check(snapshots.a.stats.static_passes===snapshots.c.stats.static_passes,'纯动画未复用静态缓存');
  const spatial=await page.evaluate(()=>{
    const m=window.W03Motion, V=m.pivot.constructor;
    m.seek(19);
    const normals=m.config.components.slice(0,5).map((c,i)=>{
      const initial=new V(...c.initial_normal).normalize();
      const current=initial.clone().applyQuaternion(m.groups[i].quaternion);
      return {id:c.id,absolute_dot:Math.abs(initial.dot(current)),initial:initial.toArray(),current:current.toArray()};
    });
    const group=m.groups[m.config.components.findIndex(c=>c.id==='spears')];
    let miss=0,upward=true;
    for(const t of [0,19,47,137,271,360]){
      m.seek(t);
      for(const s of m.config.spears){
        const origin=new V(...m.config.source_pivot_blueprint);
        const tip=new V(...s.tip).sub(origin).applyQuaternion(group.quaternion);
        const tail=new V(...s.tail).sub(origin).applyQuaternion(group.quaternion);
        const direction=tip.clone().sub(tail).normalize(),toCore=tip.clone().negate();
        miss=Math.max(miss,toCore.clone().cross(direction).length());
        upward=upward&&direction.y>0&&toCore.dot(direction)>0;
      }
    }
    const star=m.config.components.findIndex(c=>c.id==='outer_stars');
    m.seek(47);
    return {normals,maximum_spear_miss:miss,all_spears_upward:upward,
      outer_stars_follow_largest_ring:Math.abs(m.groups[0].quaternion.dot(m.groups[star].quaternion))>1-1e-9,
      all_components_same_transform:m.groups.every(g=>Math.abs(g.quaternion.dot(m.groups[0].quaternion))>1-1e-12&&g.position.distanceTo(m.groups[0].position)<1e-12)};
  });
  check(spatial.normals.every(n=>n.absolute_dot<.995),'环面法向没有实际改变，仍是平面旋转');
  check(spatial.maximum_spear_miss<1e-8&&spatial.all_spears_upward,'公转破坏矛尖锁芯');
  check(spatial.outer_stars_follow_largest_ring&&spatial.all_components_same_transform,'同步矩阵失配，连续净空证明不再适用');
  check(proof.passed&&proof.continuous_dynamic_clearance&&proof.guaranteed_static_vertical_gap>=8,'连续净空证据缺失');
  const parity=await page.evaluate(references=>{
    const m=window.W03Motion,V=m.pivot.constructor;let error=0;
    for(const [time,expected] of Object.entries(references)){
      m.seek(+time);
      for(let i=0;i<3;i++){
        const basis=new V(i===0?1:0,i===1?1:0,i===2?1:0).applyQuaternion(m.groups[0].quaternion).toArray();
        basis.forEach((v,j)=>error=Math.max(error,Math.abs(v-expected[j][i])));
      }
    }return error;
  },proof.reference_matrices);
  check(parity<1e-10,'浏览器运动矩阵与连续净空核验不一致');
  await page.getByRole('button',{name:'继续全动',exact:true}).click();
  await page.waitForFunction(()=>window.W03Motion.snapshot().seconds>47,{timeout:10000});
  await page.getByRole('button',{name:'暂停全动',exact:true}).click();
  const paused=await page.evaluate(()=>window.W03Motion.snapshot().seconds);
  await page.waitForTimeout(180);
  check(await page.evaluate(t=>window.W03Motion.snapshot().seconds===t,paused),'暂停无效');
  await page.locator('#motionTime').fill('37.5');
  check(await page.evaluate(()=>window.W03Motion.snapshot().seconds===37.5),'时间轴无效');
  await page.getByRole('button',{name:'复位',exact:true}).click();
  check(await page.evaluate(()=>window.W03Motion.snapshot().seconds===0),'复位无效');
  await page.getByRole('button',{name:'显示六矛指向线',exact:true}).click();
  await page.getByRole('button',{name:'隐藏六矛指向线',exact:true}).click();
  await page.evaluate(()=>{const e=document.getElementById('layer');e.value='200';e.dispatchEvent(new Event('input'));window.reviewApi.rebuild();});
  await page.waitForFunction(()=>window.W03Motion.snapshot().sliced);
  await page.evaluate(()=>window.reviewApi.setView('front'));
  await page.waitForFunction(()=>!window.W03Motion.snapshot().sliced);
  const framing=await page.evaluate(()=>{
    const m=window.W03Motion,a=window.reviewApi,V=m.pivot.constructor,b=m.config.conservative_swept_bounds_export,result=[];
    for(const view of ['front','right','back','top','orthofront','orthoside']){
      a.setView(view);a.camera.updateMatrixWorld();
      const projected=[];
      for(const x of [b.min[0],b.max[0]])for(const y of [b.min[1],b.max[1]])for(const z of [b.min[2],b.max[2]])projected.push(new V(x,y,z).project(a.camera).toArray());
      result.push({view,maximum_xy:Math.max(...projected.flatMap(v=>[Math.abs(v[0]),Math.abs(v[1])])),minimum_z:Math.min(...projected.map(v=>v[2])),maximum_z:Math.max(...projected.map(v=>v[2]))});
    }return result;
  });
  check(framing.every(f=>f.maximum_xy<.9&&f.minimum_z>-1&&f.maximum_z<1),'完整扫掠范围被取景裁切');
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}#labels{display:none!important}'});
  await page.waitForFunction(()=>{const r=window.reviewApi.renderer.domElement.getBoundingClientRect();return r.width===innerWidth&&r.height===innerHeight;});
  for(const [view,t,name] of [['front',0,'初始全景.png'],['front',19,'同步立体摆转.png'],['orthofront',47,'正面全动.png'],['right',90,'侧面全动.png']]){
    await page.evaluate(({view,t})=>{window.reviewApi.setView(view);window.W03Motion.seek(t);},{view,t});
    await page.locator('#stage').screenshot({path:path.join(out,name)});
  }
  await fs.mkdir(path.join(log,'frames'),{recursive:true});
  await page.evaluate(()=>window.reviewApi.setView('front'));
  for(let i=0;i<32;i++){
    await page.evaluate(t=>window.W03Motion.seek(t),i*360/32);
    await page.locator('#stage').screenshot({path:path.join(log,'frames',String(i).padStart(2,'0')+'.png')});
  }
  check(!errors.length&&!failed.length&&!external.length,JSON.stringify({errors,failed,external}));
  const result={passed:true,headless:true,desktop_used:false,game_started:false,loaded,
    all_33_components_move:true,multi_axis_normals_change:true,full_cycle_closed:true,spatial,framing,
    matrix_uploads_unchanged_during_animation:true,static_cache_reused:true,
    pause_seek_reset_aim_and_slice_verified:true,snapshots,errors,failed,external};
  await fs.writeFile(path.join(log,'viewer-qa.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({passed:true,components:33,moving_quads:loaded.stats.component_counts.reduce((a,b)=>a+b,0),spatial,framing,screenshots:4,animation_frames:32}));
}finally{await browser.close();}
