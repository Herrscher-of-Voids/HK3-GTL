import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL',out=path.join(root,'deliveries/0005_W07_无底座扩大方舟_N2_20261118');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1}),errors=[],captures=[];
page.on('pageerror',error=>errors.push(error.message));
const url='http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html';
await page.goto(url,{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W07_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:240000});
const loading=await page.locator('#loading').allTextContents();if(loading.length)throw new Error(loading.join('\n'));
await page.evaluate(()=>window.W07Viewer.setPaused(true));
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
for(const [view,file] of [['oblique','整体预览.png'],['front','船首预览.png'],['back','船尾预览.png'],['left','黑色左舷.png'],['right','白色右舷.png'],['top','俯视预览.png'],['dark_breach','黑侧破口.png'],['greenhouse','白侧生命舱.png'],['belly','船腹剖切.png'],['pixels','像素近景.png'],['controller','主控候选.png']]){
  await page.evaluate(view=>window.W07Viewer.setView(view),view);await settle();
  await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W07Viewer.snapshot())});
}
await page.evaluate(()=>{window.W07Viewer.setView('oblique');window.W07Viewer.setMode('work');window.W07Viewer.setTime(3);});await settle();
await page.screenshot({path:path.join(out,'运行示意.png')});captures.push({file:'运行示意.png',...await page.evaluate(()=>window.W07Viewer.snapshot())});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,captures},null,2)+'\n');
const figures=captures.map(item=>`<figure><a href="${item.file}" target="_blank"><img src="${item.file}" loading="lazy" alt="${item.file.slice(0,-4)}"></a><figcaption>${item.file.slice(0,-4)}</figcaption></figure>`).join('\n');
await fs.writeFile(path.join(out,'评审图集.html'),`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W07 无底座扩大方舟 N2</title><style>body{margin:0;padding:24px;background:#14202d;color:#e4ebf5;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif}h1{margin:0 0 8px;font-size:24px}a{color:#dfd1ab}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:18px}figure{margin:0}img{display:block;width:100%}figcaption{padding:6px 0 10px}@media(max-width:550px){body{padding:12px}main{display:block}}</style></head><body><h1>W07 无底座扩大方舟 N2</h1><p>无外部底座，船体按整数格扩大25%。左舷凋亡，右舷创生，共用龙骨与对应肋架；主控位于船首甲板。外观候选待审。</p><p><a href="index.html">交互预览</a> · <a href="manifest.json">生成记录</a></p><main>${figures}</main></body></html>`,'utf8');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_0005_w07_noah_n2_20261118.mjs'),path.join(out,'生成脚本/preview_0005_w07_noah_n2_20261118.mjs'));
await browser.close();console.log(JSON.stringify({out,captures:captures.length,errors}));
