/** 离线浏览器核验：完整礼堂、主体、外塔及层高操作。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json'));
const {chromium}=require('playwright');
const out=path.resolve('deliveries/永恒的礼堂_Azu_预览与方块审计_20261029');
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:2400,height:1800},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
const began=Date.now();await page.goto(pathToFileURL(path.join(out,'viewer.html')).href,{waitUntil:'load'});
await page.waitForFunction(()=>window.HALL_VIEWER_READY,{timeout:120000});
await page.waitForTimeout(1500);
async function snapshot(name){const base64=await page.evaluate(()=>{const {renderer,scene,camera}=window.HALL_VIEWER;renderer.render(scene,camera);return renderer.domElement.toDataURL('image/png').split(',')[1];});await fs.writeFile(path.join(out,name),Buffer.from(base64,'base64'));}
await snapshot('完整全景.png');
await page.selectOption('#part','main');await page.waitForTimeout(300);await snapshot('主体预览.png');
await page.selectOption('#part','tower-1');await page.waitForTimeout(300);await snapshot('单座外塔.png');
await page.selectOption('#part','all');await page.click('[data-view="top"]');await page.waitForTimeout(300);await snapshot('俯视定位.png');
await page.locator('#layer').evaluate(el=>{el.value='50';el.dispatchEvent(new Event('input'));});await page.waitForTimeout(300);
const report=await page.evaluate(()=>{const {renderer,data}=window.HALL_VIEWER,gl=renderer.getContext();return {ready:window.HALL_VIEWER_READY,count:document.getElementById('count').textContent,source_blocks:data.source_blocks,exposed_instances:data.render_instances,draw_calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,layer:document.getElementById('layerValue').textContent,renderer:gl.getParameter(gl.RENDERER),geometry_batches:renderer.info.memory.geometries,textures:renderer.info.memory.textures};});
report.errors=errors;report.elapsed_ms=Date.now()-began;report.tested=['file://离线打开','全景','仅主体','单座外塔','俯视','层高裁切'];
await fs.writeFile(path.join(out,'browser-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
await browser.close();if(errors.length)process.exitCode=1;
