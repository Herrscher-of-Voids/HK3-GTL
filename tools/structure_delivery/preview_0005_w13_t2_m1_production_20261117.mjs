import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';

const root=process.cwd(),out=path.join(root,'logs/0005-w13-t2-production-20261117/preview');
await fs.mkdir(out,{recursive:true});
const sources=['src/main/resources/assets/hk3gtl/models/scene/w13_t2_m1.json.gz','src/main/resources/assets/hk3gtl/models/scene/w13_t2_m1_meta.json','src/main/resources/assets/hk3gtl/textures/effect/w13_t2_m1_atlas.png','src/main/java/com/sirin/hk3gtl/client/wonder/Hk3W13Puppetry.java'];
const inputs=await Promise.all(sources.map(async file=>{const bytes=await fs.readFile(path.join(root,file));return {file,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};}));
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(root,'tools/structure_delivery/w13_t2_m1_production_viewer.mjs'),resolve:{alias:{'three/addons':path.join(skill,'node_modules/three/examples/jsm'),three:path.join(skill,'node_modules/three/build/three.module.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
await fs.writeFile(path.join(out,'index.html'),'<!doctype html><html lang="zh"><meta charset="UTF-8"><link rel="icon" href="data:,"><title>W13 T2-M1 正式资源观察</title><style>html,body{margin:0;overflow:hidden;background:#17141b}#loading{position:absolute;color:#fff;padding:24px;font:20px sans-serif}</style><div id="loading">正在读取正式整数格合面资源</div><script src="./viewer.bundle.js"></script></html>');
const types={'.html':'text/html','.js':'text/javascript','.png':'image/png','.gz':'application/octet-stream'};
const server=http.createServer(async(req,res)=>{try{const file=path.join(root,decodeURIComponent(req.url).split('?')[0]);const data=await fs.readFile(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});res.end(data);}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/'),{chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1800,height:1200},deviceScaleFactor:1});
const errors=[],captures=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
await page.goto('http://127.0.0.1:'+server.address().port+'/logs/0005-w13-t2-production-20261117/preview/index.html');
await page.waitForFunction(()=>window.PRODUCTION_READY,{},{timeout:180000});
for(const [view,time,name] of [['front',0,'正式资源-全貌'],['eye',0,'正式资源-眼珠-0秒'],['eye',3,'正式资源-眼珠-3秒'],['cables',0,'正式资源-粗缆-0秒'],['cables',8,'正式资源-粗缆-8秒'],['controller',8,'正式资源-主控固定端-8秒']]){
  await page.evaluate(({view,time})=>{window.ProductionViewer.setView(view);window.ProductionViewer.setTime(time);},{view,time});
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:path.join(out,name+'.png')});captures.push({file:name+'.png',view,time,...await page.evaluate(()=>window.ProductionViewer.snapshot())});
}
await fs.writeFile(path.join(out,'observations.json'),JSON.stringify({created_at:new Date().toISOString(),sources:inputs,rendering:'正式GZIP场景、正式atlas、Java Puppetry同参数变换的离线视觉观察',errors,captures},null,2)+'\n');
await browser.close();server.close();console.log(JSON.stringify({out,errors,captures:captures.length}));
