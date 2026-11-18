import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = process.cwd();
const out = path.join(root, 'deliveries/0005_W07_原案形制重制_B3_20261116');
const skill = path.join(process.env.USERPROFILE, '.codex/skills/minecraft-builder-skill');
const require = createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {rolldown} = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));

const bundle = await rolldown({input:path.join(out, '生成脚本/viewer.mjs'), resolve:{alias:{
  'three/addons':path.join(skill, 'node_modules/three/examples/jsm'),
  three:path.join(skill, 'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out, 'viewer.bundle.js'), format:'iife', minify:true});
await bundle.close();

const {chromium} = require('playwright');
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
const page = await browser.newPage({viewport:{width:1680,height:1080},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
page.on('response',response=>{if(response.status()>=400)errors.push(`${response.status()} ${response.url()}`);});
page.on('requestfailed',request=>failed.push({url:request.url(),error:request.failure().errorText}));
const views=[['front','整体预览.png'],['right','前右预览.png'],['orthofront','正面预览.png'],
  ['side','侧面预览.png'],['back','背面预览.png'],['top','俯视预览.png'],
  ['core','双生之茧近景.png'],['crown','冠环与蝶翼预览.png'],['controller','主控位置预览.png'],['lily','百合与双生茧.png'],['crownOnly','完整蝶翼与冠环.png'],['arkOnly','船体与四塔.png'],['baseOnly','深渊与肋骨.png']];
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/'+encodeURIComponent('index.html'),{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W07_STATIC_READY,{timeout:180000});
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
for(const [view,file] of views){
  await page.evaluate(view=>{const presets={lily:'lily',crownOnly:'crown',arkOnly:'ark',baseOnly:'base'};window.W07Static.setScene(presets[view]||'all');if(!presets[view])window.W07Static.setView(view);},view);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.locator('#stage').screenshot({path:path.join(out,file)});
}
const result={size:await page.locator('#actualSize').innerText(),snapshot:await page.evaluate(()=>window.W07Static.snapshot()),errors,failed,views};
await fs.writeFile(path.join(out,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();
if(errors.length||failed.length)throw new Error(JSON.stringify({errors,failed}));
console.log(JSON.stringify({out,views:views.length,errors:errors.length,failed:failed.length,snapshot:result.snapshot}));
