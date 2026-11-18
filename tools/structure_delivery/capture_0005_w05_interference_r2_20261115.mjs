import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const folder='0005_W05_部件穿模检查_R2_20261115',out=path.join(root,'deliveries',folder);
const log=path.join(root,'logs/0005-w05-interference-r2-20261115');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1700,height:1100},deviceScaleFactor:1});
const errors=[],failed=[],screenshots=[];
page.on('pageerror',e=>errors.push(e.stack));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(folder)+'/'+encodeURIComponent('部件穿模检查.html'),{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W05_INSPECTION_READY,null,{timeout:180000});
for(let i=0;i<7;i++){
  await page.evaluate(i=>window.W05Inspection.selectCase(i),i);
  const info=await page.evaluate(i=>window.W05Inspection.DATA.cases[i],i);
  const file=info.id+'.png';
  await page.screenshot({path:path.join(out,file)});
  screenshots.push({case:info.id,time:info.time,mode:info.mode,file});
}
await page.evaluate(()=>window.W05Inspection.selectCase(0));
const readback=await page.evaluate(()=>({ready:window.W05_INSPECTION_READY,buttons:document.querySelectorAll('[data-case]').length,
  label:document.getElementById('title').textContent,snapshot:window.W05Inspection.api.snapshot()}));
await browser.close();
await fs.writeFile(path.join(log,'inspection-capture.json'),JSON.stringify({created_at:new Date().toISOString(),headless:true,
  desktop_used:false,game_started:false,errors,failed,screenshots,readback},null,2)+'\n');
console.log(JSON.stringify({screenshots:screenshots.length,errors,failed}));
