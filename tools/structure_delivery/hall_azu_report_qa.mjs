/** 用户侧普通浏览器离线报告与筛选验证，不关闭浏览器安全限制。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const require=createRequire(path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json'));
const {chromium}=require('playwright');
const out=path.resolve('deliveries/永恒的礼堂_Azu_预览与方块审计_20261029');
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
await page.goto(pathToFileURL(path.join(out,'index.html')).href,{waitUntil:'load'});
assert.equal(await page.locator('#materials>tr').count(),66);
assert.match(await page.locator('#summary').innerText(),/1,933,767/);
if(await page.locator('#compatibility').count()){
 assert.match(await page.locator('#compatibility').innerText(),/需要替换的材料：0种/);
 assert.match(await page.locator('#compatibility').innerText(),/323 \/ 323/);
 await page.locator('#compatibility').screenshot({path:path.join(out,'兼容性页面核验.png')});
}
const imgs=await page.locator('img').evaluateAll(els=>els.map(e=>({src:e.src,ok:e.complete&&e.naturalWidth>0})));
assert.ok(imgs.every(i=>i.ok));
for(const [scope,count]of Object.entries({hall:66,body:62,tower:16,towers:16,saved:87,other:44})){
 await page.selectOption('#scope',scope);assert.equal(await page.locator('#materials>tr').count(),count);
}
await page.selectOption('#scope','hall');await page.selectOption('#shape','mixed');
assert.equal(await page.locator('#materials>tr').count(),1);assert.match(await page.locator('#materials').innerText(),/smooth_quartz_slab/);
await page.selectOption('#shape','all');await page.fill('#search','diorite_wall');
assert.equal(await page.locator('#materials>tr').count(),1);assert.match(await page.locator('#materials').innerText(),/35,162/);
await page.locator('#materials summary').click();assert.match(await page.locator('#materials').innerText(),/非完整方块/);
await page.fill('#search','');await page.selectOption('#shape','invisible');assert.match(await page.locator('#materials').innerText(),/minecraft:light/);
await page.selectOption('#shape','all');
const links=await page.locator('a[href]').evaluateAll(els=>els.map(a=>a.href).filter(h=>h.startsWith('file:')));
for(const href of links)await fs.access(fileURLToPath(href));
await page.screenshot({path:path.join(out,'报告页面核验.png'),fullPage:true});
await page.click('#loadPreview');const frame=page.frameLocator('#inline');await frame.locator('#count').waitFor();
await page.frame({url:/viewer\.html$/}).waitForFunction(()=>window.HALL_VIEWER_READY,{timeout:120000});
assert.match(await frame.locator('#count').innerText(),/1,933,767/);
assert.equal(errors.length,0,errors.join('\n'));
const report={ordinary_browser_security:true,offline:true,images:imgs.length,local_links:links.length,scope_filters:6,checks:['66种主展材料','六种统计范围','双层台阶混合分类','中文/ID搜索','状态展开','无形光源筛选','图片与全部下载链接','内嵌三维加载'],errors};
await fs.writeFile(path.join(out,'report-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
await browser.close();
