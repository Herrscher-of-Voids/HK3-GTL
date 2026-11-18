import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL',out=path.join(root,'deliveries/0005_W14_原生维度地貌_E3_20261118');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(out,'生成脚本/viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
if(process.argv.includes('--bundle-only'))process.exit(0);
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright'),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1}),errors=[],failed=[],captures=[];
page.on('pageerror',error=>errors.push(error.message));page.on('response',response=>{if(response.status()>=400)failed.push({url:response.url(),status:response.status()});});page.on('requestfailed',request=>failed.push({url:request.url(),error:request.failure().errorText}));
const url=process.argv.find(value=>/^https?:/.test(value))||'http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html';
await page.goto(url,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.W14_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:240000});
const loadingError=await page.locator('#loading').allTextContents();if(loadingError.length)throw new Error(loadingError.join('\n'));
await page.evaluate(()=>{window.W14Viewer.setPaused(true);window.W14Viewer.setTime(0);});await page.screenshot({path:path.join(out,'评审界面.png'),fullPage:true});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}#legend{display:none!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const staticViews=[['all','oblique','整体预览.png'],['all','front','正面预览.png'],['all','left','侧面预览.png'],['all','top','俯视预览.png'],['engine','oblique','独立行星发动机.png'],['engine','nozzle','发动机喷口.png'],['dimensions','oblique','七维度球.png'],['all','fuel','维度进料近景.png'],['engine','pixels','像素近景.png']];
for(const [index,label] of ['主世界','末地','地狱','月球','火星','金星','银河系'].entries())staticViews.push(['all','sector_'+index,label+'扇区.png']);
for(const [view,label] of [['oak','原版橡树近景'],['end_island','末地主岛全貌'],['dragon_pool','中央龙池近景'],['crystal','方块末影水晶近景'],['crimson','绯红森林近景'],['warped','诡异森林近景'],['wall','隔墙落底近景']])staticViews.push([['oak','dragon_pool','crystal'].includes(view)?'sectors':'all',view,label+'.png']);
for(const [model,view,file] of staticViews){
  await page.evaluate(({model,view})=>{window.W14Viewer.setModel(model);window.W14Viewer.setView(view);},{model,view});await settle();await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W14Viewer.snapshot())});
}
await page.evaluate(()=>{window.W14Viewer.setModel('all');window.W14Viewer.setView('running');window.W14Viewer.setMode('work');window.W14Viewer.setTime(0);});await settle();await page.screenshot({path:path.join(out,'运行零秒.png')});captures.push({file:'运行零秒.png',...await page.evaluate(()=>window.W14Viewer.snapshot())});
await page.evaluate(()=>window.W14Viewer.setTime(3));await settle();await page.screenshot({path:path.join(out,'运行三秒.png')});captures.push({file:'运行三秒.png',...await page.evaluate(()=>window.W14Viewer.snapshot())});
for(const second of [0,3]){
  await page.evaluate(second=>{window.W14Viewer.setView('flame');window.W14Viewer.setTime(second);},second);await settle();const file='火箭尾焰'+second+'秒.png';await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W14Viewer.snapshot())});
}
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),errors,failed,captures},null,2)+'\n');
const figures=captures.map(item=>`<figure><a href="${item.file}" target="_blank"><img src="${item.file}" loading="lazy" alt="${item.file.slice(0,-4)}"></a><figcaption>${item.file.slice(0,-4)}</figcaption></figure>`).join('\n');
await fs.writeFile(path.join(out,'评审图集.html'),`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W14 行星发动机维度基座 E3 图集</title><style>body{margin:0;padding:24px;background:#14202d;color:#e4ebf5;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif}h1{margin:0 0 8px;font-size:24px}a{color:#c3b0f4}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:18px}figure{margin:0}img{display:block;width:100%}figcaption{padding:6px 0 10px}@media(max-width:550px){body{padding:12px}main{display:block}}</style></head><body><h1>W14 行星发动机维度基座 E3</h1><p>七维度球、七扇区地貌与火箭尾焰；运行画面为网页特效演示。</p><p><a href="index.html">交互预览</a> · <a href="manifest.json">生成记录</a> · <a href="../0005_W14_行星发动机基座_E1_20261117/references.html">行星发动机参考图</a></p><main>${figures}</main></body></html>`,'utf8');
await fs.copyFile(path.join(root,'tools/structure_delivery/preview_0005_w14_engine_e3_20261118.mjs'),path.join(out,'生成脚本/preview_0005_w14_engine_e3_20261118.mjs'));await browser.close();console.log(JSON.stringify({out,captures:captures.length,errors,failed}));
