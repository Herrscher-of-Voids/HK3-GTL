import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'deliveries/0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115');
const log = path.join(root, 'logs/0005-w05-wendy-wings-a3-20261115');
const skill = path.join(process.env.USERPROFILE, '.codex/skills/minecraft-builder-skill');
const require = createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {rolldown} = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));

await fs.mkdir(log, {recursive:true});
const bundle = await rolldown({input:path.join(out, '生成脚本/viewer.mjs'), resolve:{alias:{
  'three/addons':path.join(skill, 'node_modules/three/examples/jsm'),
  three:path.join(skill, 'node_modules/three/build/three.module.js')
}}});
await bundle.write({file:path.join(out, 'viewer.bundle.js'), format:'iife', minify:true});
await bundle.close();

const {chromium} = require('playwright');
const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
const page = await browser.newPage({viewport:{width:1700, height:1100}, deviceScaleFactor:1});
const errors = [], failed = [];
page.on('pageerror', error => errors.push(error.message));
page.on('console', message => {if(message.type() === 'error') errors.push(message.text());});
page.on('requestfailed', request => failed.push({url:request.url(), error:request.failure().errorText}));
const views = [
  ['front', '整体预览.png'], ['right', '前右预览.png'], ['orthofront', '正面预览.png'],
  ['side', '侧面预览.png'], ['back', '背面预览.png'], ['top', '俯视预览.png'],
  ['core', '核心近景.png'], ['wing', '风翼近景.png'], ['controller', '主控近景.png']
];

try {
  await page.goto(pathToFileURL(path.join(out, '三维评审.html')).href, {waitUntil:'domcontentloaded'});
  await page.waitForFunction(() => window.W05_STATIC_READY && window.W05_REVIEW_READY, null, {timeout:120000});
  await page.screenshot({path:path.join(out, '评审界面.png')});
  await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
  await page.waitForFunction(() => window.W05Static.renderer.domElement.clientWidth === innerWidth && window.W05Static.renderer.domElement.clientHeight === innerHeight);
  for (const [view, file] of views) {
    await page.evaluate(view => window.W05Review.setView(view), view);
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.locator('#stage').screenshot({path:path.join(out, file)});
  }
} finally {
  await browser.close();
  await fs.writeFile(path.join(log, 'preview-capture.json'), JSON.stringify({
    created_at:new Date().toISOString(), viewport:{width:1700, height:1100},
    headless:true, desktop_used:false, game_started:false, errors, failed,
    review_screenshot:'评审界面.png', screenshots:views.map(([view, file]) => ({view, file}))
  }, null, 2) + '\n');
}
await fs.copyFile(fileURLToPath(import.meta.url), path.join(out, '生成脚本', path.basename(fileURLToPath(import.meta.url))));
if (errors.length || failed.length) throw new Error(JSON.stringify({errors, failed}));
console.log(JSON.stringify({out, images:views.length + 1, errors:errors.length, failed:failed.length}));
