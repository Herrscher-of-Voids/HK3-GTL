import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/0005_W06_作者蓝图原案_20261115');
const log=path.join(root,'logs/0005-w06-author-blueprint-20261115');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1680,height:1080},deviceScaleFactor:1});
const errors=[],failed=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
page.on('requestfailed',request=>failed.push({url:request.url(),error:request.failure().errorText}));
await page.goto(pathToFileURL(path.join(out,'三维评审.html')).href,{waitUntil:'load'});
await page.waitForFunction(()=>window.W06_AUTHOR_READY,{timeout:120000});
const samples=await page.evaluate(()=>{
  const c=window.W06Author.renderer.domElement,gl=c.getContext('webgl2')||c.getContext('webgl'),pixels=new Uint8Array(c.width*c.height*4);
  gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
  let colored=0,min=255,max=0;
  for(let i=0;i<pixels.length;i+=400){colored+=pixels[i]>20||pixels[i+1]>20||pixels[i+2]>20?1:0;min=Math.min(min,pixels[i],pixels[i+1],pixels[i+2]);max=Math.max(max,pixels[i],pixels[i+1],pixels[i+2]);}
  return {width:c.width,height:c.height,colored_samples:colored,min,max,parts:window.W06Author.groups.length,bounds:window.W06Author.config.data.bounds};
});
await page.screenshot({path:path.join(out,'评审界面.png')});
await page.locator('#stage').screenshot({path:path.join(out,'front.png')});
for(const [view,name] of [['right','right.png'],['front_ortho','front_ortho.png'],['side','side.png'],['back','back.png'],['top','top.png'],['lotus','lotus.png'],['prism','prism.png'],['rings','rings.png'],['crown','crown.png'],['spears','spears.png'],['controller','controller.png']]){
  await page.evaluate(view=>window.W06Author.fit(view),view);
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.locator('#stage').screenshot({path:path.join(out,name)});
}
await page.selectOption('#mode','work');
await page.evaluate(()=>window.W06Author.freeze(12));
await page.locator('#stage').screenshot({path:path.join(out,'work.png')});
await page.setViewportSize({width:390,height:844});
await page.evaluate(()=>window.W06Author.fit('front'));
await page.waitForTimeout(250);
await page.screenshot({path:path.join(out,'移动端评审界面.png'),fullPage:true});
const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,stage:document.querySelector('#stage').getBoundingClientRect().toJSON(),canvas:{width:window.W06Author.renderer.domElement.clientWidth,height:window.W06Author.renderer.domElement.clientHeight}}));
await browser.close();
const result={created_at:new Date().toISOString(),desktop:{width:1680,height:1080},mobile,canvas:samples,headless:true,game_started:false,desktop_used:false,errors,failed};
await fs.mkdir(log,{recursive:true});
await fs.writeFile(path.join(log,'preview-capture.json'),JSON.stringify(result,null,2)+'\n');
if(errors.length||failed.length||samples.colored_samples<30||mobile.scrollWidth>mobile.width)throw new Error(JSON.stringify(result));
const manifest=JSON.parse(await fs.readFile(path.join(out,'manifest.json'),'utf8'));
const receipt={created_at:result.created_at,machine:'W06',conversation:'0005',conversation_id:'01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',candidate:manifest.candidate,preview:'deliveries/0005_W06_作者蓝图原案_20261115/三维评审.html',source_sha256:manifest.source_sha256,nominal_size_wdh:manifest.nominal_size_wdh,actual_size_wdh:manifest.size_wdh,occupied_bounds_xyz:manifest.occupied_bounds_xyz,parts:manifest.components.length,component_voxels:manifest.source_component_voxels,unique_voxels:manifest.unique_occupied_voxels,overlap_extra_memberships:manifest.overlap_extra_memberships,overlap_pairs:JSON.parse(await fs.readFile(path.join(out,'构件交叠记录.json'),'utf8')).pairs.length,preview_materials:8,game_materials_registered:0,screenshots:14,appearance_approved:false,runtime_blueprint_modified:false,game_code_modified:false,jar_built:false,installed:false,game_started:false,desktop_used:false,game_verified:false,errors,failed,mobile_horizontal_overflow:mobile.scrollWidth>mobile.width,acceptance_score_changed:false};
await fs.writeFile(path.join(log,'completion.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({images:14,canvas:samples,mobile,errors:errors.length,failed:failed.length}));
