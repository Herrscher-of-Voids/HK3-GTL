import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=process.argv[2]?path.resolve(process.argv[2]):path.join(root,'deliveries/0005_W09_太虚山方块复刻_T1_20261116');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{
  'three/addons':path.join(skill,'node_modules/three/examples/jsm'),
  three:path.join(skill,'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});
await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1100},deviceScaleFactor:1});
const errors=[],failed=[],captures=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
const url='http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html';
await page.goto(url);
await page.waitForFunction(()=>window.TAIXUAN_READY,{},{timeout:180000});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const targets=[
  ['all',['oblique','front','back','top','court','gate','route','pixels']],
  ['temple',['oblique','doors','roof']],
  ['gallery',['gallery','connection']],
  ['censer',['oblique','front','right']],
  ['courtyard',['bagua']],
  ['mountain_path',['stairs']],
  ['trees',['pine']],
  ['waterfall',['fall']]
];
if(/_T[56789]_/.test(path.basename(out))){
  targets[0][1].push('gate_detail','axis','creek','pines');
  targets.push(['gallery',['gate_detail']],['trees',['bamboo','all_pines','top']],['lanterns',['lantern_detail']]);
}else if(process.argv[2]){
  targets[0][1].push('bridge','gate_detail');
  targets.push(['gallery',['gate_detail']],['mountain_path',['bridge']],['trees',['bamboo']],['lanterns',['lantern_detail']]);
}
if(/_T[6789]_/.test(path.basename(out)))targets[0][1].push('arc','floor','peaks');
if(/_T[3456789]_/.test(path.basename(out)))targets[0][1].push('base_front','base_side','base_under');
if(/_T[89]_/.test(path.basename(out)))targets[0][1].push('outlet','bank');
for(const [model,views] of targets){
  await page.evaluate(id=>window.TaixuanViewer.setModel(id),model);
  for(const view of views){
    await page.evaluate(name=>window.TaixuanViewer.setView(name),view);
    const filename=model+'-'+view+'.png';
    await page.screenshot({path:path.join(out,filename)});
    captures.push({file:filename,...await page.evaluate(()=>window.TaixuanViewer.snapshot())});
  }
}
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({url,captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
await browser.close();
console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
