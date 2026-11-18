import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'deliveries/0005_I37_世界维系试验平台_悬箱稳界试验坞_A1_20261115');
const log = path.join(root, 'logs/0005-i37-suspended-test-dock-a1-20261115');
const skill = path.join(process.env.USERPROFILE, '.codex/skills/minecraft-builder-skill');
const require = createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {rolldown} = await import(pathToFileURL(path.join(skill, 'node_modules/rolldown/dist/index.mjs')));

await fs.mkdir(path.join(out, '生成脚本'), {recursive:true});
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
await page.goto(pathToFileURL(path.join(out, '三维评审.html')).href, {waitUntil:'domcontentloaded'});
await page.waitForFunction(() => window.I37_STATIC_READY && window.I37_REVIEW_READY, null, {timeout:120000});
await page.screenshot({path:path.join(out, '评审界面.png')});
await page.addStyleTag({content:'#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;z-index:9999!important}body{overflow:hidden!important}'});
await page.waitForFunction(() => window.I37Static.renderer.domElement.clientWidth === innerWidth && window.I37Static.renderer.domElement.clientHeight === innerHeight);

const views = [
  ['front', '整体预览.png'], ['right', '前右预览.png'], ['orthofront', '正面预览.png'],
  ['side', '侧面预览.png'], ['back', '背面预览.png'], ['top', '俯视预览.png'],
  ['inside', '逐层剖切.png'], ['core', '中心试验箱.png'], ['controller', '主控近景.png']
];
for (const [view, file] of views) {
  await page.evaluate(view => {
    if (view !== 'inside') {
      const layer = document.getElementById('layer');
      layer.value = String(window.I37Static.config.data.size[1]);
      layer.dispatchEvent(new Event('input'));
    }
    window.I37Review.setView(view);
  }, view);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.evaluate(() => {
    const {renderer, scene, camera} = window.I37Static;
    renderer.render(scene, camera);
  });
  await page.locator('#stage').screenshot({path:path.join(out, file)});
}

await browser.close();
await fs.copyFile(fileURLToPath(import.meta.url), path.join(out, '生成脚本', path.basename(fileURLToPath(import.meta.url))));
await fs.writeFile(path.join(log, 'preview-capture.json'), JSON.stringify({
  created_at:new Date().toISOString(), viewport:{width:1700, height:1100},
  headless:true, desktop_used:false, game_started:false,
  review_screenshot:'评审界面.png', screenshots:views.map(([view, file]) => ({view, file}))
}, null, 2) + '\n');
console.log(JSON.stringify({out, images:views.length + 1}));
