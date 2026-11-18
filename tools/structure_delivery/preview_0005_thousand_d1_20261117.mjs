import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_千人人偶_独立像素模型_D1_20261117');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],captures=[];
page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html');
await page.waitForFunction(()=>window.PUPPET_READY,{},{timeout:120000});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
for(const [view,file] of [['front','整体正面.png'],['oblique','整体斜视.png'],['back','背面.png'],['left','左侧.png'],['top','俯视.png'],['face','蒙眼额纹.png'],['hair','后脑发髻.png'],['dress','黑金裙装.png'],['hands','分节金手.png'],['knees','机械腿关节.png'],['pixels','像素近景.png']]){
  await page.evaluate(view=>window.PuppetViewer.setView(view),view);
  await page.screenshot({path:path.join(out,file)});
  captures.push({file,...await page.evaluate(()=>window.PuppetViewer.snapshot())});
}
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,captures},null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors}));
