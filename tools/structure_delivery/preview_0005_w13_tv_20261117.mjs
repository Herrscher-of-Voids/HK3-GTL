import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL';
const out=path.join(root,'deliveries/0005_W13_侵蚀之律者电视本体_T1_20261117');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
if(process.argv.includes('--bundle-only'))process.exit(0);
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],failed=[],captures=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure().errorText}));
await page.goto('http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W13_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:240000});
const loadingError=await page.locator('#loading').allTextContents();if(loadingError.length)throw new Error(loadingError.join('\n'));
await page.evaluate(()=>{window.W13Viewer.setPaused(true);window.W13Viewer.setTime(0);});
await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
for(const [model,view,file] of [
  ['all','oblique','整体预览.png'],['all','front','正面预览.png'],['all','back','背面预览.png'],['all','left','左侧预览.png'],['all','right','右侧预览.png'],['all','top','俯视预览.png'],
  ['all','eye','粉色瞳孔屏幕.png'],['tv','shell','电视机侧壳.png'],['cables','cables','触须线缆.png'],['all','controller','主控近景.png'],['tv','pixels','像素近景.png'],['screen','eye','独立屏幕.png']]){
  await page.evaluate(({model,view})=>{window.W13Viewer.setModel(model);window.W13Viewer.setView(view);},{model,view});await settle();await page.screenshot({path:path.join(out,file)});
  captures.push({file,...await page.evaluate(()=>window.W13Viewer.snapshot())});
}
await page.evaluate(()=>{window.W13Viewer.setModel('all');window.W13Viewer.setView('front');window.W13Viewer.setMode('work');window.W13Viewer.setTime(0);});await settle();
await page.screenshot({path:path.join(out,'运行零秒.png')});captures.push({file:'运行零秒.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await page.evaluate(()=>window.W13Viewer.setTime(5));await settle();await page.screenshot({path:path.join(out,'运行五秒.png')});captures.push({file:'运行五秒.png',...await page.evaluate(()=>window.W13Viewer.snapshot())});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
const figures=captures.map(item=>`<figure><a href="${item.file}" target="_blank"><img src="${item.file}" loading="lazy" alt="${item.file.slice(0,-4)}"></a><figcaption>${item.file.slice(0,-4)}</figcaption></figure>`).join('\n');
await fs.writeFile(path.join(out,'评审图集.html'),`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W13 电视本体 T1 评审图集</title><style>body{margin:0;padding:24px;background:#17141b;color:#e9dfe8;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif}h1{margin:0 0 8px;font-size:24px}a{color:#efa3ce}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:18px}figure{margin:0}img{display:block;width:100%;background:#211a25}figcaption{padding:6px 0 10px}@media(max-width:550px){body{padding:12px}main{display:block}}</style></head><body><h1>W13 侵蚀之律者电视本体 T1</h1><p>真实方块 · 外观待审 · 运行画面为网页屏幕演示</p><p><a href="index.html">交互预览</a> · <a href="manifest.json">生成记录</a> · <a href="W13-侵蚀之律者电视本体-T1.nbt">完整NBT</a></p><main>${figures}</main></body></html>`,'utf8');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_0005_w13_tv_20261117.mjs'),path.join(out,'生成脚本/preview_0005_w13_tv_20261117.mjs'));
await browser.close();console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
