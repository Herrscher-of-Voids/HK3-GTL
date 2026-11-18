from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'deliveries/0005_W10_引力奇点刑架_净空修订_A3_20261116'
OUT = ROOT / 'deliveries/0005_W12_作者蓝图原案_A1_20261116'
(OUT / '生成脚本').mkdir(parents=True, exist_ok=True)
source = (OLD / '生成脚本/viewer.mjs').read_text('utf8').replace('W10', 'W12')
source = source.replace(',voidUniforms=[]', '')
source = source.replace('texture.magFilter=texture.minFilter=THREE.NearestFilter;texture.generateMipmaps=false;', 'texture.magFilter=THREE.NearestFilter;texture.minFilter=THREE.NearestMipmapLinearFilter;texture.generateMipmaps=true;texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());')
start = source.index('      const key=`${material}')
end = source.index('      const mesh=', start)
source = source[:start] + '''      const key=`${material}:${face}`;
      if(!materialCache.has(key)){
        const info=materials[material],options={map:textures[material][faceNames[face]],transparent:info.transparent,opacity:info.transparent?.5:1,depthWrite:!info.transparent,alphaTest:.01,side:THREE.DoubleSide,clippingPlanes:[plane]};
        materialCache.set(key,new THREE.MeshLambertMaterial({...options,emissive:info.emissive?0xffffff:0,emissiveIntensity:info.emissive?.25:0}));
      }
''' + source[end:]
start = source.index('  const predicates=')
end = source.index('\n  function draw', start)
source = source[:start] + "  const predicates={all:()=>true,...Object.fromEntries(['core','base','walls','wings','crown','chains'].map(name=>[name,g=>g.userData.section===name]))};" + source[end:]
source = source.replace(";voidUniforms.forEach(u=>{u.voidTime.value=time;u.voidLines.value=document.getElementById('voidLines').checked?1:0;})", '')
start = source.index('    effects.update(')
end = source.index('\n', start)
source = source[:start] + "    effects.update({time,flow,work,effects:document.getElementById('effects').checked,section:activeScene,pointScale:stage.clientHeight*camera.zoom/1500,layerY:axis==='y'?layer+offset.y+1:1e6,camera,width:size.x,height:size.y});" + source[end:]
source = source.replace("for(const id of ['effects','lens','voidLines'])", "for(const id of ['effects'])")
source = source.replace("W12-引力奇点刑架-A3.png", "W12-全域能量约束壁-A1.png")
source = source.replace(",lens:document.getElementById('lens').checked", '')
source = source.replace('${materials.length} 种方块', '${materials.length} 项原生材质')
(OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
shutil.copy2(OLD / 'style.css', OUT / 'style.css')
(OUT / 'index.html').write_text('''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W12 · 戒律 · 全域能量约束壁 · A1</title></head>
<body><header><div class="eyebrow">0005 / W12 / AUTHOR BLUEPRINT A1</div><h1>约束之律者 · 戒律 · 全域能量约束壁</h1><p>真实整数方块 · 格雷／本模组原生像素材质 · <span id="actualSize">读取完整几何…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块构件…</div><div id="legend"><b>W12 / 作者原案 A1</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>实体锁链逐节穿扣，独立分组可隐藏</span></div></section><aside>
<section class="controls"><h2>结构范围</h2><div class="row"><button data-scene="all">整体</button><button data-scene="core">三重十字</button><button data-scene="chains">32条锁链</button><button data-scene="walls">双约束壁</button><button data-scene="wings">双翼长廊</button><button data-scene="base">基盘深井</button><button data-scene="crown">八塔与天幕</button></div></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>动态演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 金色约束</option><option value="work">工作 · 戒律之蝶与蜂窝场</option></select><div class="row"><button id="pause">暂停动态</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>蜂窝场、光矛、蝴蝶与托举光束</label><label><input id="glass" type="checkbox" checked>透明材质</label><small>每10秒扩散一轮蜂窝场。网页特效独立于方块NBT；旋转陀螺环与奇点使用参考姿态导出。</small></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16 格参考网格</label><label><input id="axes" type="checkbox">XYZ 坐标轴</label></section>
<p id="stats"></p><details><summary>实体构件显隐 <span id="partCount"></span></summary><div id="parts"></div></details><details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块 ID"><div id="materials"></div></details>
<p class="note">仅主控固定在(531,50,10)。其余全部实体格可换合法通用接口、朝向自选。原文两条600格长廊的137格重叠、完整端点及厚度均保留，详见取样记录。</p><p class="links"><a href="原文与取样.html">原文与取样</a> · <a href="geometry.json">完整几何</a> · <a href="conflicts.json">尺寸冲突</a> · <a href="manifest.json">交付记录</a> · <a href="W12-全域能量约束壁-A1.nbt">NBT</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>
''', 'utf8')
