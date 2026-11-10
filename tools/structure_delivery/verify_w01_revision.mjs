/** 修订183 · 2026-10-30 00:18:00：独立无界面浏览器核验W01完整真实模型与入口，不操作运行游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json'));
const {chromium}=require('playwright');
const out=path.resolve('deliveries/W01_永恒礼堂_干燥建材与入口主控修订_V2_20261030');
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:2000,height:1500},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
try{
  await page.goto(pathToFileURL(path.join(out,'viewer.html')).href,{waitUntil:'load'});
  await page.waitForFunction(()=>window.HALL_VIEWER_READY,{timeout:120000});
  async function snapshot(name){const data=await page.evaluate(()=>{const v=window.HALL_VIEWER;v.renderer.render(v.scene,v.camera);return v.renderer.domElement.toDataURL('image/png').split(',')[1];});await fs.writeFile(path.join(out,name),Buffer.from(data,'base64'));}
  await snapshot('完整全景.png');
  await page.click('#controller');await snapshot('主控入口.png');
  const report=await page.evaluate(()=>{const {data,renderer}=window.HALL_VIEWER;return {ready:window.HALL_VIEWER_READY,source_blocks:data.source_blocks,exposed_instances:data.render_instances,controller:data.controller,draw_calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,unrendered:data.unrendered,tested:['file://离线加载','全部真实模型','入口主控特写'],game_tested:false};});
  report.errors=errors;await fs.writeFile(path.join(out,'browser-verification.json'),JSON.stringify(report,null,2));
  if(report.source_blocks!==1932713||errors.length)throw Error(JSON.stringify(report));
  console.log(JSON.stringify(report));
}finally{await browser.close();}
