/** I35越界悬索桥：实体表面缓存与独立虚数空间动态层。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {gunzipSync} from 'node:zlib';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const output=path.resolve(process.argv[2]??path.join(root,'deliveries/I35_虚数空间锚定阵列_越界悬索桥_V3_20261027'));
const view=path.join(output,'i35');
const legacyFolder=path.join(root,'deliveries/I34_虚数之树观测阵列_树冠干涉观测院_V1_20261027');
let builder=await fs.readFile(path.join(legacyFolder,'生成脚本/build_i34_viewer_v1_20261027.mjs'),'utf8');
if(!builder.includes('const output = path.resolve(process.argv[2]);'))throw new Error('共享查看器输出参数已变化，拒绝错写目录');
builder=builder.replace('const output = path.resolve(process.argv[2]);',`const output = ${JSON.stringify(view)};`);
builder=builder.replaceAll('virtual:i34-imaginary-tree-array','virtual:i35-threshold-anchor');
builder=builder.replaceAll('I34虚数之树观测预览','I35越界悬索桥预览');
builder=builder.replaceAll('树冠干涉观测院V1-三维预览.png','越界悬索桥V3-三维预览.png');
builder=builder.replaceAll('后侧观测资料交接','虚数空间侧');

const portalCode=String.raw`
const portalScene=new THREE.Scene();
const bridgeFade={value:1};
// 门后实体只在预览中逐渐隐没；关闭界面即可核对完整实体桥尾。
for(const mesh of stateMeshes){
  mesh.material.onBeforeCompile=shader=>{
    shader.uniforms.uBridgeFade=bridgeFade;
    shader.vertexShader='varying float vBridgeZ;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',
      'vec4 bridgePosition=vec4(transformed,1.);\n#ifdef USE_INSTANCING\nbridgePosition=instanceMatrix*bridgePosition;\n#endif\nvBridgeZ=(modelMatrix*bridgePosition).z;\n#include <project_vertex>');
    shader.fragmentShader='varying float vBridgeZ;uniform float uBridgeFade;\n'+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',
      '#include <alphatest_fragment>\nfloat bridgeDissolve=smoothstep('+Number(data.portal.center[2]+3).toFixed(1)+','+Number(data.portal.center[2]+data.portal.depth*.88).toFixed(1)+',vBridgeZ)*uBridgeFade;\nif(fract(sin(dot(gl_FragCoord.xy,vec2(12.9898,78.233)))*43758.5453)<bridgeDissolve)discard;');
  };
  mesh.material.customProgramCacheKey=()=> 'i35-portal-bridge-fade-v3';
  mesh.material.needsUpdate=true;
}
function createThresholdPortal(){
  const p=data.portal;
  if(!p||p.center?.length!==3||![...p.center,p.halfWidth,p.halfHeight,p.depth].every(Number.isFinite)||Math.min(p.halfWidth,p.halfHeight,p.depth)<=0)throw new Error('I35缺少有效虚数界面参数');
  const [px,py,pz]=p.center,hw=p.halfWidth,hh=p.halfHeight,depth=p.depth,deckY=p.bridgeY??p.deckY??102,bridgeHalfWidth=p.bridgeHalfWidth??108;
  const portal=new THREE.Group();portalScene.add(portal);
  const uniforms={uTime:{value:0}};
  const background=new THREE.ShaderMaterial({uniforms,side:THREE.DoubleSide,depthWrite:true,toneMapped:false,
    vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:__PORTAL_SHADER__
      uniform float uTime;varying vec2 vUv;
      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.,1.)),f.x),f.y);}
      void main(){
        vec2 q=vUv*2.-1.;vec2 a=abs(q);
        if(max(max(a.x,a.y),(a.x+a.y)*.70710678)>1.)discard;
        float r=length(q),angle=atan(q.y,q.x),t=uTime*.09;
        float n=noise(q*4.+vec2(t,-t*.4))*.65+noise(q*11.-vec2(t*.3,t))*.35;
        float filament=pow(max(0.,1.-abs(sin(angle*7.+r*14.-t*2.+n*4.))),25.);
        filament*=smoothstep(.2,.8,r)*.33;
        float ring=pow(max(0.,1.-abs(sin(r*28.-t*3.+n*1.5))),50.)*.12;
        vec3 base=mix(vec3(.003,.005,.010),vec3(.014,.020,.028),n);
        vec3 gold=vec3(.68,.52,.24)*(filament+ring);
        gl_FragColor=vec4(base+gold,1.);
        #include <colorspace_fragment>
      }
    __PORTAL_SHADER__});
  const back=new THREE.Mesh(new THREE.PlaneGeometry(hw*2,hh*2),background);
  back.position.set(px,py,pz+depth);portal.add(back);
  const corners=[[-1,-.4142],[-.4142,-1],[.4142,-1],[1,-.4142],[1,.4142],[.4142,1],[-.4142,1],[-1,.4142]];
  const lines=[],rings=8;
  function point(index,level){const s=1-level*.36;return new THREE.Vector3(px+corners[index%8][0]*hw*s,py+corners[index%8][1]*hh*s,pz+depth*level);}
  for(let j=0;j<rings;j++){
    const t=j/(rings-1);
    for(let i=0;i<8;i++){lines.push(point(i,t),point(i+1,t));if(j<rings-1)lines.push(point(i,t),point(i,(j+1)/(rings-1)));}
  }
  const lineMaterial=new THREE.LineBasicMaterial({color:0xcab474,transparent:true,opacity:.23,depthWrite:false,toneMapped:false});
  portal.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(lines),lineMaterial));
  // 深处桥影只传达跨越界面的纵深，不进入实体蓝图。
  const ghost=[];
  for(const dx of [-bridgeHalfWidth,-bridgeHalfWidth+5,bridgeHalfWidth-5,bridgeHalfWidth])ghost.push(new THREE.Vector3(px+dx,deckY,pz+2),new THREE.Vector3(px+dx*.58,deckY+8,pz+depth-3));
  for(let j=1;j<=7;j++){
    const t=j/8,s=1-t*.42,y=deckY+t*8,z=pz+depth*t;
    ghost.push(new THREE.Vector3(px-bridgeHalfWidth*s,y,z),new THREE.Vector3(px+bridgeHalfWidth*s,y,z));
  }
  const ghostMaterial=new THREE.LineBasicMaterial({color:0xdfcc91,transparent:true,opacity:.19,depthWrite:false,toneMapped:false});
  portal.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(ghost),ghostMaterial));
  const starPositions=[],starColors=[],gold=new THREE.Color(0xc8ae6a),white=new THREE.Color(0xe7e5d2);
  let seed=35139;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<260;i++){
    const x=(random()*2-1)*hw*.88,y=(random()*2-1)*hh*.88;
    if(Math.abs(x/hw)+Math.abs(y/hh)>1.28||Math.abs(y+py-deckY)<9&&Math.abs(x)<bridgeHalfWidth+6)continue;
    starPositions.push(px+x,py+y,pz+6+random()*(depth-10));
    const c=random()<.23?white:gold;starColors.push(c.r,c.g,c.b);
  }
  const starsGeometry=new THREE.BufferGeometry();starsGeometry.setAttribute('position',new THREE.Float32BufferAttribute(starPositions,3));starsGeometry.setAttribute('color',new THREE.Float32BufferAttribute(starColors,3));
  const starMaterial=new THREE.PointsMaterial({size:1.2,vertexColors:true,transparent:true,opacity:.62,sizeAttenuation:false,depthWrite:false,toneMapped:false});
  portal.add(new THREE.Points(starsGeometry,starMaterial));
  let elapsed=0;
  return {
    update(dt){
      portal.visible=document.getElementById('showPortal').checked&&+document.getElementById('layer').value===H-1;
      bridgeFade.value=portal.visible?1:0;
      if(portal.visible&&document.getElementById('animatePortal').checked)elapsed+=dt;
      uniforms.uTime.value=elapsed;
      lineMaterial.opacity=.20+Math.sin(elapsed*.6)*.025;
      ghostMaterial.opacity=.18+Math.sin(elapsed*.7+1)*.025;
      starMaterial.opacity=.57+Math.sin(elapsed*.45)*.07;
    },
    active(){return portal.visible&&document.getElementById('animatePortal').checked;}
  };
}
const thresholdPortal=createThresholdPortal();
let portalTimer=0,lastPortalTime=performance.now(),staticDirty=true;
// 实体颜色与深度只在镜头或结构状态改变时重绘，动画复用缓存。
const staticTarget=new THREE.WebGLRenderTarget(1,1,{minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter});
staticTarget.depthTexture=new THREE.DepthTexture(1,1,THREE.UnsignedIntType);
const copyScene=new THREE.Scene(),copyCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
const copyMaterial=new THREE.ShaderMaterial({
  uniforms:{colorBuffer:{value:staticTarget.texture},depthBuffer:{value:staticTarget.depthTexture}},
  vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}',
  fragmentShader:'uniform sampler2D colorBuffer;uniform sampler2D depthBuffer;varying vec2 vUv;void main(){gl_FragColor=texture2D(colorBuffer,vUv);gl_FragDepthEXT=texture2D(depthBuffer,vUv).x;\n#include <colorspace_fragment>\n}',
  depthWrite:true,depthTest:true,depthFunc:THREE.AlwaysDepth,toneMapped:false
});
const copyQuad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),copyMaterial);copyQuad.frustumCulled=false;copyScene.add(copyQuad);
const drawingSize=new THREE.Vector2();
function renderCompositedScene(){
  renderer.getDrawingBufferSize(drawingSize);
  if(staticTarget.width!==drawingSize.x||staticTarget.height!==drawingSize.y){staticTarget.setSize(drawingSize.x,drawingSize.y);staticDirty=true;}
  if(staticDirty){renderer.setRenderTarget(staticTarget);renderer.autoClear=true;renderer.render(scene,camera);staticDirty=false;}
  renderer.setRenderTarget(null);renderer.autoClear=false;renderer.clear();
  renderer.render(copyScene,copyCamera);renderer.render(portalScene,camera);renderer.autoClear=true;
}
function queuePortalFrame(){
  if(portalTimer||document.hidden||!thresholdPortal.active())return;
  portalTimer=setTimeout(()=>{portalTimer=0;requestRender(false);},1000/24);
}
for(const id of ['showPortal','animatePortal'])document.getElementById(id).onchange=()=>{
  clearTimeout(portalTimer);portalTimer=0;lastPortalTime=performance.now();requestRender();
};
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){clearTimeout(portalTimer);portalTimer=0;}
  else{lastPortalTime=performance.now();requestRender();}
});
`.replaceAll('__PORTAL_SHADER__','`');

const injections=`
source=source.replace('const projected=new THREE.Vector3();',${JSON.stringify(portalCode+'\nconst projected=new THREE.Vector3();')});
source=source.replace('requestRender=()=>{if(renderQueued)return;', 'requestRender=(invalidate=true)=>{if(invalidate)staticDirty=true;if(document.hidden||renderQueued)return;');
source=source.replace('function renderFrame(){\\n  renderQueued=false;controls.update();renderer.render(scene,camera);', 'function renderFrame(now){\\n  renderQueued=false;if(document.hidden)return;\\n  const dt=Math.min((now-lastPortalTime)/1000,.08);lastPortalTime=now;\\n  thresholdPortal.update(dt);controls.update();renderCompositedScene();');
source=source.replace('\\n}\\ncontrols.addEventListener(\\'change\\',requestRender);', '\\n  queuePortalFrame();\\n}\\ncontrols.addEventListener(\\'change\\',requestRender);');
source=source.replace('三维表面已就绪。','三维表面已就绪。虚数界面为独立非实体视觉层。');
source=source.replace('renderer.render(scene,camera);const a=document.createElement(\\'a\\');','renderCompositedScene();const a=document.createElement(\\'a\\');');
source=source.replace('window.REVIEW_READY=true;', 'requestRender();window.REVIEW_READY=true;');
if(!source.includes('thresholdPortal.update(dt)')||!source.includes('queuePortalFrame();')||!source.includes('renderCompositedScene();const a='))throw new Error('I35虚数界面集成自检失败');
`;
if(!builder.includes('const oldHotPaths = '))throw new Error('共享查看器补丁边界已变化');
builder=builder.replace('const oldHotPaths = ',injections+'\nconst oldHotPaths = ');
if(!builder.includes('initializeMatrixChunk')||!builder.includes('requestRender=()=>'))throw new Error('轻量查看器缺少分块初始化或按需绘制');
await fs.mkdir(view,{recursive:true});
await import('data:text/javascript;base64,'+Buffer.from(builder).toString('base64'));

const dataJs=await fs.readFile(path.join(view,'data.js'),'utf8');
if(!dataJs.startsWith('window.HK3_PAYLOAD=')||!dataJs.endsWith(';'))throw new Error('I35候选载荷格式错误');
const encoded=JSON.parse(dataJs.slice('window.HK3_PAYLOAD='.length,-1));
const payload=JSON.parse(gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
const {data,audit}=payload;
if(data.key!=='i35'||data.controller[0]!==Math.floor((data.size[0]-1)/2))throw new Error('I35编号或主控居中坐标不符');
if(!data.portal||data.portal.center?.length!==3||![...data.portal.center,data.portal.halfWidth,data.portal.halfHeight,data.portal.depth].every(Number.isFinite))throw new Error('I35虚数界面参数缺失');
if(payload.palette.length!==payload.materials.length||payload.surfaceGroups.length!==payload.palette.length||payload.surfaceGroups.some(group=>group.length!==6))throw new Error('材质或表面索引数量错误');
const oldPage=await fs.readFile(path.join(legacyFolder,'i34/三维评审.html'),'utf8');
const css=oldPage.match(/<style>([\s\S]*?)<\/style>/)?.[1];
if(!css)throw new Error('既有评审样式缺失');
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const [w,h,d]=data.size,p=data.controller;
const title='虚数空间锚定阵列 · 越界悬索桥';
const page=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I35 · ${title} V3</title><style>${css}
.candidate-note{padding:10px 12px;border-left:3px solid #c6ad6b;background:#302d24;color:#f1e6c8}.portal-controls{display:flex;gap:14px;flex-wrap:wrap}.locator{margin-top:12px}#stage{background:#111b28}</style>
<header><a href="../index.html">← I35交付总览</a><h1>I35 · ${title} V3</h1><div>IRV · V11 / ${w}×${d}×${h}（宽×长×高） · ${payload.blockCount.toLocaleString()}个实体方块 · 独立外观候选</div></header>
<main class="review"><section id="stage" aria-label="I35实体悬索桥与虚数空间动态三维预览"><div id="loading">加载真实材质与外露面…</div><div id="labels"></div></section><aside>
<div id="viewName"></div><div class="candidate-note">实体桥头连接本维度，连续桥面和主缆穿过锚定界面，向黑金色虚数空间隐没。界面、星芒与深处桥影属于非实体视觉层，不计入材料、NBT和Pattern；本轮仍为候选，尚未实装。</div>
<div class="portal-controls"><label><input id="showPortal" type="checkbox" checked>显示虚数空间</label><label><input id="animatePortal" type="checkbox" checked>播放界面动画</label></div><p>最高24帧；实体颜色与深度缓存复用。暂停或隐藏后按需重绘；剖层时自动隐藏界面。</p>
<div class="locator"><b>主控蓝图 [${p.join(', ')}]</b><p>从1起算格位 [${p.map(v=>v+1).join(', ')}]；整宽第${p[0]+1}格，齐平融入主体设备外壳。</p><button data-view="controller">定位主控</button></div>
<div><button data-view="front">本维度侧整体</button><button data-view="right">前右整体</button><button data-view="back">虚数空间侧</button><button data-view="top">俯视</button><button data-view="inside">剖面</button><button data-view="orthofront">正前</button><button data-view="orthoside">正侧</button></div>
<p>左键旋转 · 右键平移 · 滚轮缩放</p><label>剖切高度 <b id="layerValue">${h-1}</b><input id="layer" type="range" min="0" max="${h-1}" value="${h-1}"></label>
<label><input id="showGlass" type="checkbox" checked>玻璃</label><label><input id="showPorts" type="checkbox">接口定位框</label><label><input id="showPaths" type="checkbox">维护空间</label><label><input id="showZones" type="checkbox">分区</label>
<p><button id="reset">重置</button><button id="saveImage">保存视角</button></p><div id="counts"></div><p id="status"></p>
<details open><summary>越界悬索桥</summary><p>${escape(data.description)}</p><p>接收实际魂钢锚件、I33空间核心组件、I34校准资料、能源与稳定介质；执行实体锚组件标定、稳定工况验证、负载复验与失效诊断。合格锚定组件与锚定状态、记录分别交付。</p><p>锚件由制造设备形成，资料不能替代材料；门内景象表达锚定界面，不新增实际传送或维度能力，不绕过I44/I45或终审维度禁行。</p></details>
<details open><summary>主控与设备内嵌接口</summary><div id="portButtons"></div><div id="ports"></div></details><details><summary>真实材质与用量</summary><div id="materials"></div></details><details><summary>静态核验</summary><div id="checks"></div></details>
<details><summary>结构文件与验收边界</summary><a href="${escape(data.name)}.nbt">NBT</a> · <a href="${escape(data.name)}.schem">Schematic</a> · <a href="../verification.json">核验记录</a><p>仅提交${audit.viewer_surface_faces.toLocaleString()}片真实外露面；按高度分块初始化。隐藏材质或剖切仅调整现有外露面，不补画内部剖切面。正式控制器、Pattern、配方、生存可达性与游戏运行另行验收。</p></details></aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></html>`;
await fs.writeFile(path.join(view,'三维评审.html'),page,'utf8');
await fs.writeFile(path.join(view,'portal-source.json'),JSON.stringify({portal:data.portal,counts_as_blocks:false,counts_as_pattern:false,actual_dimension_or_teleport:false,max_fps:24,static_color_depth_cache:true,game_installed:false},null,2)+'\n','utf8');
const generated=await fs.readFile(path.join(view,'viewer.bundle.js'),'utf8');
if(/createTreeProjection|showProjection|animateProjection/.test(generated))throw new Error('I35错误地包含I34树影逻辑');
console.log(JSON.stringify({output,view,blocks:payload.blockCount,faces:audit.viewer_surface_faces,portal:data.portal,max_fps:24,static_color_depth_cache:true}));
