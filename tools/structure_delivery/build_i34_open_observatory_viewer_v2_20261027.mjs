/** I34开穹悬弦观测仪：复用逐面巨构预览，叠加已确认的非实体树影。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';
import crypto from 'node:crypto';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.resolve(process.argv[2]??path.join(root,'deliveries/I34_虚数之树观测阵列_开穹悬弦观测仪_V2_20261027'));
const view=path.join(output,'i34');
const approvedFolder=path.join(root,'deliveries/I34_虚数之树_动态投影研究_V1_20261027');
const approved=JSON.parse(await fs.readFile(path.join(approvedFolder,'manifest.json'),'utf8'));
const approvedHtml=await fs.readFile(path.join(approvedFolder,'index.html'));
if(!approved.approved||crypto.createHash('sha256').update(approvedHtml).digest('hex')!==approved.approved_sha256)throw new Error('已确认树影的来源或批准哈希不一致');
const treeSource=await fs.readFile(path.join(approvedFolder,'生成脚本/i34_tree_projection_scene_20261027.mjs'),'utf8');
const currentTreeSource=await fs.readFile(path.join(root,'tools/structure_delivery/i34_tree_projection_scene_20261027.mjs'),'utf8');
if(treeSource!==currentTreeSource)throw new Error('当前树影源码已偏离已确认交付');
const treeStart=treeSource.indexOf('const tree=new THREE.Group();');
const treeEnd=treeSource.indexOf('// 细薄观测环');
if(treeStart<0||treeEnd<=treeStart)throw new Error('无法找到已确认树影的独立代码边界');
let treeCode=treeSource.slice(treeStart,treeEnd);
treeCode=treeCode.replace('const tree=new THREE.Group();scene.add(tree);','const tree=new THREE.Group();projectionScene.add(tree);');
// 正交预览使用世界单位到像素的比率，不按透视距离缩小世界节点。
treeCode=treeCode.replace('uPixel:{value:renderer.getPixelRatio()}', 'uPixel:{value:renderer.getPixelRatio()},uWorldPixel:{value:1}');
treeCode=treeCode.replace('uniform float uTime;uniform float uPower;uniform float uPixel;', 'uniform float uTime;uniform float uPower;uniform float uPixel;uniform float uWorldPixel;');
treeCode=treeCode.replace('aSize*520.*uPixel/max(1.,-p.z)', 'aSize*uWorldPixel');
if(treeCode.includes('aSize*520.'))throw new Error('正交节点缩放补丁未应用');
const projectionCode=`
const projectionScene=new THREE.Scene();
function createTreeProjection(){
${treeCode}
tree.position.set(240,92,167);tree.scale.setScalar(.90);
lineMaterial.opacity=.72;
const movingPosition=flow.geometry.attributes.position;
let elapsed=0,initialized=false;
return {
  update(dt){
    tree.visible=document.getElementById('showProjection').checked&&+document.getElementById('layer').value===H-1;
    const animated=tree.visible&&document.getElementById('animateProjection').checked;
    if(animated)elapsed+=dt;
    uniforms.uTime.value=elapsed;
    uniforms.uWorldPixel.value=renderer.domElement.height/(camera.top-camera.bottom)*camera.zoom*.90;
    halos.children.forEach((sprite,i)=>sprite.material.opacity=.075+Math.sin(elapsed*.6+i)*.009);
    if(animated||!initialized){
      for(let i=0;i<flows.length;i++){
        const item=flows[i],t=(elapsed*item.speed+item.offset)%1,p=item.branch.curve.getPoint(t);
        movingPosition.setXYZ(i,p.x,p.y,p.z);
      }
      movingPosition.needsUpdate=true;initialized=true;
    }
  },
  active(){return tree.visible&&document.getElementById('animateProjection').checked;}
};
}
const treeProjection=createTreeProjection();
let projectionTimer=0,lastProjectionTime=performance.now(),staticDirty=true;
// 缓存实体画面的颜色与深度，投影动画不重复提交百万片实体表面。
const staticTarget=new THREE.WebGLRenderTarget(1,1,{minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter});
staticTarget.depthTexture=new THREE.DepthTexture(1,1,THREE.UnsignedIntType);
const copyScene=new THREE.Scene(),copyCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
const copyMaterial=new THREE.ShaderMaterial({
  uniforms:{colorBuffer:{value:staticTarget.texture},depthBuffer:{value:staticTarget.depthTexture}},
  vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}',
  fragmentShader:'uniform sampler2D colorBuffer;uniform sampler2D depthBuffer;varying vec2 vUv;void main(){gl_FragColor=texture2D(colorBuffer,vUv);gl_FragDepthEXT=texture2D(depthBuffer,vUv).x;\\n#include <colorspace_fragment>\\n}',
  depthWrite:true,depthTest:true,depthFunc:THREE.AlwaysDepth,toneMapped:false
});
const copyQuad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),copyMaterial);copyQuad.frustumCulled=false;copyScene.add(copyQuad);
const drawingSize=new THREE.Vector2();
function renderCompositedScene(){
  renderer.getDrawingBufferSize(drawingSize);
  if(staticTarget.width!==drawingSize.x||staticTarget.height!==drawingSize.y){staticTarget.setSize(drawingSize.x,drawingSize.y);staticDirty=true;}
  if(staticDirty){
    renderer.setRenderTarget(staticTarget);renderer.autoClear=true;renderer.render(scene,camera);staticDirty=false;
  }
  renderer.setRenderTarget(null);renderer.autoClear=false;renderer.clear();
  renderer.render(copyScene,copyCamera);renderer.render(projectionScene,camera);renderer.autoClear=true;
}
function queueProjectionFrame(){
  if(projectionTimer||document.hidden||!treeProjection.active())return;
  projectionTimer=setTimeout(()=>{projectionTimer=0;requestRender(false);},1000/30);
}
for(const id of ['showProjection','animateProjection'])document.getElementById(id).onchange=()=>requestRender(false);
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){clearTimeout(projectionTimer);projectionTimer=0;}
  else{lastProjectionTime=performance.now();requestRender();}
});
`;

const legacyPath=path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027/生成脚本/build_i34_viewer_v1_20261027.mjs');
let builder=await fs.readFile(legacyPath,'utf8');
builder=builder.replace('const output = path.resolve(process.argv[2]);',`const output = ${JSON.stringify(view)};`);
const injections=`
source=source.replace('const projected=new THREE.Vector3();',${JSON.stringify(projectionCode+'\nconst projected=new THREE.Vector3();')});
source=source.replace('requestRender=()=>{if(renderQueued)return;', 'requestRender=(invalidate=true)=>{if(invalidate)staticDirty=true;if(document.hidden||renderQueued)return;');
source=source.replace('function renderFrame(){\\n  renderQueued=false;controls.update();renderer.render(scene,camera);', 'function renderFrame(now){\\n  renderQueued=false;\\n  if(document.hidden)return;\\n  const dt=Math.min((now-lastProjectionTime)/1000,.08);lastProjectionTime=now;\\n  treeProjection.update(dt);controls.update();renderCompositedScene();');
source=source.replace('\\n}\\ncontrols.addEventListener(\\'change\\',requestRender);', '\\n  queueProjectionFrame();\\n}\\ncontrols.addEventListener(\\'change\\',requestRender);');
source=source.replace('三维表面已就绪。','三维表面已就绪。金白树影为非实体投影。');
source=source.replace('renderer.render(scene,camera);const a=document.createElement(\\'a\\');','renderCompositedScene();const a=document.createElement(\\'a\\');');
source=source.replace('window.REVIEW_READY=true;', 'requestRender();window.REVIEW_READY=true;');
source=source.replace('data.key+\\'-树冠干涉观测院V1-三维预览.png\\'', 'data.key+\\'-开穹悬弦观测仪V2-三维预览.png\\'');
if(!source.includes('treeProjection.update(dt)')||!source.includes('queueProjectionFrame();')||source.includes('aSize*520.'))throw new Error('动态树影集成自检失败');
`;
builder=builder.replace('const oldHotPaths = ',injections+'\nconst oldHotPaths = ');
if(!builder.includes('createTreeProjection()'))throw new Error('未接入动态树影补丁');
await fs.mkdir(view,{recursive:true});
await import('data:text/javascript;base64,'+Buffer.from(builder).toString('base64'));

const dataJs=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!dataJs.startsWith('window.HK3_PAYLOAD=')||!dataJs.endsWith(';'))throw new Error('候选数据载荷格式错误');
const encoded=JSON.parse(dataJs.slice('window.HK3_PAYLOAD='.length,-1));
const payload=JSON.parse(gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
const {data,audit}=payload;
const oldPage=await fs.readFile(path.join(path.dirname(legacyPath),'../i34/三维评审.html'),'utf8');
const css=oldPage.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('缺少既有评审页面样式');
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const [w,h,d]=data.size,p=data.controller;
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I34 · 开穹悬弦观测仪 V2</title><style>${css}
.projection-note{padding:10px 12px;border-left:3px solid #c6a75d;background:#302e25;color:#f2e4be}.projection-controls{display:flex;gap:18px;flex-wrap:wrap}.locator{margin-top:12px}#stage{background:#111b28}</style>
<header><a href="../index.html">← I34交付总览</a><h1>I34 · 虚数之树观测阵列 · 开穹悬弦观测仪 V2</h1><div>${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体方块 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I34实体建筑与独立树影投影三维预览"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="projection-note">已确认的金白树影叠加于实体观测仪中。投影不计入方块、材料、Pattern或高度；本轮建筑仍待审，尚未接入游戏。</div>
<div class="projection-controls"><label><input id="showProjection" type="checkbox" checked>显示树影投影</label><label><input id="animateProjection" type="checkbox" checked>播放投影动画</label></div><p>剖切实体时自动隐藏树影；恢复最高层后重新显示。实体使用颜色与深度缓存，树影以最高30帧播放；暂停或隐藏后按需重绘。</p>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，嵌入主机连续外壳。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">前左整体</button><button data-view="right">前右整体</button><button data-view="back">后侧仪器</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>开穹悬弦观测仪</summary><p>${escape(data.description)}</p><p>不再由四侧厂房围合中央奇观。研究、运算与检修空间融入承台，实体仪器保持开敞轮廓，金白树影作为观测对象的非实体投影。</p><p>只观测树与世界联系及误差，不制造或操纵整棵虚数之树，不代替I35实体锚定。RN-IOP开放本机，首次真实初观证据支持RN-ILE；I35/S04不得成为循环前置。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="${escape(data.name)}.nbt">NBT</a> · <a href="${escape(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>实体建筑来自统一逐格数据；树影是明确分离的视觉层。候选未批准、未接入实例；正式Pattern、工艺与游戏运行尚未验收。隐藏材质仅影响原有外露面，不补画内部剖切面。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
await fs.writeFile(path.join(view,'projection-source.json'),JSON.stringify({approved_html_sha256:approved.approved_sha256,source:'deliveries/I34_虚数之树_动态投影研究_V1_20261027/生成脚本/i34_tree_projection_scene_20261027.mjs',source_sha256:crypto.createHash('sha256').update(treeSource).digest('hex'),position:[240,92,167],scale:.90,counts_as_blocks:false,game_installed:false},null,2)+'\n','utf8');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,projection_source_confirmed:true}));
