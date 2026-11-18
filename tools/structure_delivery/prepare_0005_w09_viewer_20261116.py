from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'deliveries/0005_W12_三环翻转_A3_20261116'
OUT = ROOT / 'deliveries/0005_W09_作者蓝图原案_A1_20261116'
(OUT / '生成脚本').mkdir(parents=True, exist_ok=True)
source = (OLD / '生成脚本/viewer.mjs').read_text('utf8').replace('W12', 'W09')
source = source.replace("['core','base','walls','wings','crown','chains']", "['core','base','weapons','mountains','crown','chains','entry']")
source = source.replace('W09-全域能量约束壁-A3.png', 'W09-文明共识矩阵-A1.png')
source = source.replace("setScene('core');setView('core');", "setScene('all');setView('front');")
source = source.replace('grid.position.set(offset.x,data.bounds.min[1]+offset.y-.5,offset.z)', 'grid.position.set(width/2,data.bounds.min[1]+offset.y-.5,depth/2)')
(OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
shutil.copy2(ROOT / 'tools/structure_delivery/w09_effects_20261116.mjs', OUT / '生成脚本/effects.mjs')
style = (OLD / 'style.css').read_text('utf8').replace('--bg:#0d1015', '--bg:#100d12').replace('--panel:#181a20', '--panel:#1b161b').replace('background:#171a20', 'background:#21151b')
(OUT / 'style.css').write_text(style, 'utf8')
(OUT / 'index.html').write_text('''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W09 · 万象 · 文明共识矩阵 · A1</title></head>
<body><header><div class="eyebrow">0005 / W09 / AUTHOR BLUEPRINT A1</div><h1>识之律者 · 万象 · 文明共识矩阵</h1><p>真实整数方块 · 格雷／本模组原生像素材质 · <span id="actualSize">读取完整几何…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块构件…</div><div id="legend"><b>W09 / 作者原案 A1</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>八峰、三兵、32条实体链与120片羽刃</span></div></section><aside>
<section class="controls"><h2>结构范围</h2><div class="row"><button data-scene="all">整体</button><button data-scene="core">千羽核心</button><button data-scene="weapons">三兵镇岳</button><button data-scene="mountains">机械八峰</button><button data-scene="chains">32条锁链</button><button data-scene="base">立体八卦</button><button data-scene="crown">折扇御座</button><button data-scene="entry">天门神道</button></div></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>动态演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 千羽与水墨</option><option value="work">工作 · 三兵共鸣</option></select><div class="row"><button id="pause">暂停动态</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>羽刃电弧、光带、水墨波纹与脉冲</label><label><input id="glass" type="checkbox" checked>透明材质</label><small>工作态每10秒触发剑枪红束。光带、波纹与流光为网页特效，NBT保存零秒方块姿态。</small></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16 格参考网格</label><label><input id="axes" type="checkbox">XYZ 坐标轴</label></section>
<p id="stats"></p><details><summary>实体构件显隐 <span id="partCount"></span></summary><div id="parts"></div></details><details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块 ID"><div id="materials"></div></details>
<p class="note">唯一主控位于拜仙台(487,160,260)，红石块用于定位。其余全部实体格可换合法通用接口、朝向自选。三羽环同直径的转动交叠按原案保留，详见取样记录。</p><p class="links"><a href="原文与取样.html">原文与取样</a> · <a href="geometry.json">完整几何</a> · <a href="conflicts.json">交叠记录</a> · <a href="manifest.json">交付记录</a> · <a href="W09-文明共识矩阵-A1.nbt">NBT</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>
''', 'utf8')
