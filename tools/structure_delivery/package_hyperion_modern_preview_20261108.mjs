/** 复用最新版评审样式，离线打包休伯利安原稿查看器。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const out=path.join(root,'deliveries/休伯利安_1145格原稿_新版预览_20261108');
const latest=await fs.readFile(path.join(root,'deliveries/W03_穹界虚数锚定环_四锚穹盖_Gork原案_V7_20261108/w03/三维评审.html'),'utf8');
const css=latest.match(/<style>([\s\S]*?)<\/style>/)[1];
const buttons=Object.entries({front:'前左全舰',right:'前右全舰',back:'后侧',top:'俯视',orthofront:'正前',orthoside:'正侧',inside:'逐层剖切',texture:'舰体近景'}).map(([id,name])=>'<button data-view="'+id+'">'+name+'</button>').join('');
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>休伯利安 · 1145格原稿 · 新版三维评审</title><style>${css}
.material[hidden]{display:none}#materialSearch{width:95%;padding:9px;margin:10px 0;background:#172438;color:#fff;border:1px solid #51627b}#stage:fullscreen{width:100vw;height:100vh}#stage canvas{display:block}button{margin-bottom:5px}.candidate-note{padding:10px;border-left:3px solid #c4adff;background:#293042}</style>
<header><a href="index.html">← 舰体总览</a><h1>仿制 · 休伯利安｜1145格原稿</h1><div>1145×549×240（宽×长×高） · 1,469,258个方块 · 113种非空气状态 · 3,402条方块实体</div></header>
<main class="review"><section id="stage" aria-label="休伯利安全舰三维预览"><div id="loading">加载完整舰体与真实模型…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">使用最新版评审界面，保留负责人指定原稿。主控、接口和正式机器结构尚未定案，不把原稿钻石块自动当成接口。</div>
<div>${buttons}</div><p>左键旋转 · 右键平移 · 滚轮缩放</p><label>保留至方块层 Y=<b id="layerValue">239</b><input id="layer" type="range" min="0" max="239" value="239"></label>
<label><input type="checkbox" id="showGlass" checked>显示玻璃</label><label><input type="checkbox" id="showGrid">参考网格</label>
<p><button id="reset">重置全舰</button><button id="saveImage">保存视角</button><button id="fullscreen">全屏查看</button></p><p id="counts"></p><p id="status"></p>
<details open><summary>原稿与预览范围</summary><p>完整保留舰体方块、半砖、门、活板门、活塞和玻璃板的状态模型。没有重画舰体、替换材料或更改连接状态。旧预览保留为历史。</p><p>材质筛选与逐层隐藏不补画新的剖切面；全舰取景不以旧奇观尺寸裁切。</p></details>
<details><summary>材质筛选与用量 · 113种状态</summary><input id="materialSearch" type="search" placeholder="搜索中文名或方块ID" aria-label="搜索方块材质"><div id="materials"></div></details>
<details><summary>核验与显示边界</summary><div id="checks"></div><p>原稿作者元数据：100HIDE。已选定舰体基础；正式Pattern、工艺、生存获取、成型与运行性能尚未验收。本次只更新离线预览。</p></details>
<details><summary>原始文件与核验记录</summary><p><a href="休伯利安.litematic">原始投影</a> · <a href="hyperion-full.nbt">完整NBT</a> · <a href="tiles.nbt">方块实体数据</a> · <a href="材料清单.json">材料清单</a> · <a href="verification.json">核验记录</a></p></details>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>`;
await fs.writeFile(path.join(out,'三维评审.html'),html);
const {rolldown}=await import(pathToFileURL(path.join(skill,'node_modules/rolldown/dist/index.mjs')));
const bundle=await rolldown({input:path.join(root,'tools/structure_delivery/hyperion_modern_viewer_20261108.mjs'),resolve:{alias:{three:path.join(skill,'node_modules/three/build/three.module.js'),'orbit-controls':path.join(skill,'node_modules/three/examples/jsm/controls/OrbitControls.js')}}});
await bundle.write({file:path.join(out,'viewer.bundle.js'),format:'iife',minify:true});await bundle.close();
await fs.copyFile(path.join(skill,'node_modules/three/LICENSE'),path.join(out,'Three许可.txt'));
const index=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>休伯利安 · 最新原稿预览</title><style>body{max-width:1400px;margin:30px auto;padding:20px;background:#121b2b;color:#ecf1fa;font:17px/1.8 system-ui}a{color:#c9b8ff}img{max-width:100%}</style><h1>仿制 · 休伯利安｜1145格原稿新版预览</h1><p>2026-11-08 · 宽1145×长549×高240 · 1,469,258个方块 · 113种非空气状态 · 3,402条方块实体。</p><p><a href="三维评审.html">进入新版三维评审 →</a> · <a href="材料清单.json">原稿材料清单</a> · <a href="verification.json">核验记录</a></p><img src="完整预览.png" alt="休伯利安全舰预览"><p>使用最新预览界面：自由旋转、视角切换、逐层剖切、玻璃开关、材质搜索筛选、全屏与截图。保留全部原稿及方块状态模型，原始文件不变。正式机器仍待独立接入与验收。</p></html>`;
await fs.writeFile(path.join(out,'index.html'),index);
console.log(JSON.stringify({output:out,offline:true,latest_review_style:true}));
