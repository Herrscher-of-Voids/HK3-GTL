/** 生成ME中枢候选的离线多角度图片，不操作桌面或游戏。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'deliveries/0005_ME一体化合成中枢_三舱模块式_A1_20261114');
const log = path.join(root, 'logs/0005-me-crafting-hub-a1-20261114');
const require = createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium} = require('playwright');
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
const page = await browser.newPage({viewport:{width:1800, height:1200}, deviceScaleFactor:1});
const errors = [];
page.on('pageerror', e => errors.push(e.message));
await page.goto(pathToFileURL(path.join(output, '三维评审.html')).href);
await page.waitForFunction(() => window.REVIEW_READY && document.getElementById('status').textContent === '三维表面已就绪。');
const style = await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important;border:0!important}.label{font-size:17px!important}'});
const views = [['front','整体预览.png'], ['right','前右预览.png'], ['back','后侧合成舱.png'],
               ['top','俯视与检修净空.png'], ['controller','主控接口近景.png'], ['inside','逐层剖切.png']];
for (const [view, file] of views) {
  await page.evaluate(view => {
    window.reviewApi.setView(view);
    document.getElementById('showPorts').checked = view === 'controller';
    document.getElementById('showPaths').checked = view === 'top';
    window.reviewApi.rebuild();
  }, view);
  await page.waitForFunction(() => document.getElementById('status').textContent === '三维表面已就绪。');
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.evaluate(() => window.reviewApi.renderer.render(window.reviewApi.scene, window.reviewApi.camera));
  await page.locator('#stage').screenshot({path:path.join(output, file)});
}
await style.evaluate(e => e.remove());
await page.setViewportSize({width:1600, height:1100});
await page.evaluate(() => window.reviewApi.setView('front'));
await page.screenshot({path:path.join(log, '评审页面.png'), fullPage:true});
const record = {created_at:new Date().toISOString(), headless:true, desktop_used:false, game_started:false,
                screenshots:views.map(([view,file]) => ({view,file})), errors};
await fs.writeFile(path.join(log, 'preview-capture.json'), JSON.stringify(record, null, 2) + '\n');
await browser.close();
console.log(JSON.stringify(record));
