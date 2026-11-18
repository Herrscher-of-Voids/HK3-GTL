import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';

const root='E:/AI/progrem/complate progrem/HK3GTL',source=path.join(root,'tools/structure_delivery');
const out=path.join(root,'deliveries/0005_W15_凌虛晴树海巨书_B1_20261118');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(source,'w15_book_viewer_20261118.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
const style=`*{box-sizing:border-box}html,body{margin:0;height:100%;background:#0c1320;color:#eee9db;font:13px/1.65 system-ui,'Microsoft YaHei',sans-serif}body{display:grid;grid-template-columns:minmax(0,1fr) 292px}#stage{position:relative;min-width:0;height:100vh;overflow:hidden}canvas{display:block;outline:none}header{position:absolute;left:30px;top:24px;z-index:2;pointer-events:none}.eyebrow{font-size:11px;letter-spacing:3px;color:#ba9c63}h1{font-size:27px;letter-spacing:3px;font-weight:500;margin:6px 0 3px}header p{margin:0;color:#91a1b8;font-size:12px}aside{overflow:auto;padding:23px 20px;background:#101a29;border-left:1px solid #2d3542}h2{font-size:12px;font-weight:500;letter-spacing:2px;color:#bda774;margin:24px 0 10px}h2:first-child{margin-top:0}p{color:#a6b0bf;margin:8px 0 14px}.row{display:flex;gap:6px;flex-wrap:wrap}button,select{font:inherit;color:#c4cbd4;background:#182334;border:1px solid #344052;border-radius:3px;padding:6px 9px;cursor:pointer}button:hover,button.active{color:#ffdf9c;border-color:#9f8753;background:#2a2c2e}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #e2c077;outline-offset:2px}label{display:flex;gap:8px;align-items:center;margin:7px 0;color:#b8c1cc}input[type=checkbox]{accent-color:#ddbb70}input[type=range]{width:100%;accent-color:#cfb16d}select{width:100%;margin:3px 0 8px}small{color:#7c8ca2}a{color:#d7bd84;text-decoration:none}a:hover{text-decoration:underline}.divider{height:1px;background:#2b3542;margin:20px 0}.material{display:flex;gap:9px;align-items:center;margin:7px 0;color:#9ba9bb;font-size:12px}.material img{width:23px;height:23px;image-rendering:pixelated}#loading{position:absolute;inset:0;display:grid;place-content:center;z-index:8;background:#0c1320;color:#d5c29b}#caption{position:absolute;bottom:23px;left:30px;font-size:11px;color:#7e8fa5;pointer-events:none}#panelToggle{position:absolute;right:14px;top:16px;z-index:3;background:#101a29c7}.panelHidden{grid-template-columns:minmax(0,1fr)}.panelHidden aside{display:none}output{float:right;color:#d7bf88}details summary{cursor:pointer;color:#bda774}#modelStats{font-size:11px}#stats{color:#77879c;font-size:11px}#cutValue{float:right}@media(max-width:760px){body{grid-template-columns:minmax(0,1fr) 230px}aside{padding:18px 12px}header{left:16px;top:18px}h1{font-size:20px}header p{max-width:260px}#caption{left:16px;max-width:260px}}`;
await fs.writeFile(path.join(out,'style.css'),style);
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W15 凌虛晴 · 树海巨书 B1</title></head><body><section id="stage"><header><div class="eyebrow">0005 / W15 / B1</div><h1>凌虛晴 · 树海巨书</h1><p>展开的实体巨书，生成中的虚数树海</p></header><button id="panelToggle" aria-label="展开或收起控制面板">面板</button><div id="loading">载入整数格模型…</div><div id="caption">左键旋转 · 右键平移 · 滚轮缩放<br>真实方块与原生像素贴图 · 树海为网页特效演示</div></section><aside><h2>外观候选 B1</h2><p>黑金机械书封、层叠白页、中空书脊。金树从书中生成，光根穿过书脊接入下方量子海。</p><p id="actualSize"></p><p id="modelStats"></p><h2>观察视角</h2><div id="views" class="row"></div><div class="row" style="margin-top:10px"><button id="reset">复位</button><button id="screenshot">截图</button><button id="fullscreen">全屏</button></div><h2>树海演出 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="work">运行 · 书写与树海流动</option><option value="idle">待机 · 微光与缓流</option></select><button id="pause">暂停动画</button><input id="time" aria-label="演出时间" type="range" min="0" max="90" step=".1" value="0"><label><input id="effects" type="checkbox" checked>显示特效</label><label><input id="tree" type="checkbox" checked>虚数之树与光根</label><label><input id="sea" type="checkbox" checked>量子海与世界泡</label><h2>实体构件</h2><div id="groups"></div><label><input id="controller" type="checkbox">标记主控候选</label><label><input id="grid" type="checkbox">16格参考网格</label><h2>实体高度剖切 <span id="cutValue">330</span></h2><input id="cut" aria-label="实体高度剖切" type="range" min="77" max="330" value="330"><div class="divider"></div><details><summary>原生方块材质</summary><div id="materials"></div></details><div class="divider"></div><p><a href="W15-凌虛晴树海巨书-B1.nbt">完整实体 NBT</a> · <a href="manifest.json">生成记录</a></p><small>造型待审。网页特效与正式游戏接入分别记录。</small></aside><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>`;
await fs.writeFile(path.join(out,'index.html'),html,'utf8');
for(const file of ['w15_book_viewer_20261118.mjs','w15_book_fx_20261118.mjs','preview_0005_w15_book_20261118.mjs'])await fs.copyFile(path.join(source,file),path.join(out,'生成脚本',file));
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1720,height:1120},deviceScaleFactor:1});
const errors=[],failed=[],captures=[];
page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
const url='http://127.0.0.1:9681/'+encodeURIComponent(path.basename(out))+'/index.html';
await page.goto(url,{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>window.W15_READY||document.getElementById('loading')?.textContent.startsWith('预览载入失败'),{},{timeout:240000});
await page.evaluate(()=>{window.W15Viewer.setPaused(true);window.W15Viewer.setTime(6);});
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.addStyleTag({content:'body{grid-template-columns:minmax(0,1fr)!important}aside,header,#caption,#panelToggle{display:none!important}#stage{width:100vw!important;height:100vh!important}'});
const settle=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
for(const [view,file] of [['oblique','整体预览.png'],['front','正面预览.png'],['top','俯视预览.png'],['book','巨书近看.png'],['pages','叠页细节.png'],['spine','书脊光根.png'],['underside','书封底部.png'],['tree','虚数树冠.png'],['sea','量子海.png'],['pixels','像素近景.png']]){
  await page.evaluate(view=>window.W15Viewer.setView(view),view);await settle();
  await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W15Viewer.snapshot())});
}
await page.evaluate(()=>{window.W15Viewer.setFx(false);window.W15Viewer.setView('book');});await settle();
await page.screenshot({path:path.join(out,'实体巨书.png')});captures.push({file:'实体巨书.png',...await page.evaluate(()=>window.W15Viewer.snapshot())});
await page.evaluate(()=>{window.W15Viewer.setFx(true);window.W15Viewer.setView('front');});
for(const [time,file] of [[0,'运行00秒.png'],[30,'运行30秒.png'],[62,'运行62秒.png']]){
  await page.evaluate(time=>window.W15Viewer.setTime(time),time);await settle();
  await page.screenshot({path:path.join(out,file)});captures.push({file,...await page.evaluate(()=>window.W15Viewer.snapshot())});
}
await page.evaluate(()=>window.W15Viewer.setMode('idle'));await settle();
await page.screenshot({path:path.join(out,'待机预览.png')});captures.push({file:'待机预览.png',...await page.evaluate(()=>window.W15Viewer.snapshot())});
await fs.writeFile(path.join(out,'预览记录.json'),JSON.stringify({captured_at:new Date().toISOString(),url,errors,failed,captures},null,2)+'\n');
await browser.close();console.log(JSON.stringify({out,url,errors,failed,captures:captures.length}));
