# -*- coding: utf-8 -*-
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    css = (ROOT / 'deliveries/0005_W11_千律机械剧场_作者蓝图_A1_20261117/style.css').read_text('utf8')
    css += '''\n:root{--bg:#101016;--panel:#1b1922;--line:#4c3d4c;--gold:#e196b8;--muted:#aea7b4;--text:#eeeaf1}header{background:#211a25;border-bottom-color:#ad4a7b}h1{font-size:21px;letter-spacing:.03em}#stage{background:#19191f}button.active{background:#593a50;border-color:#d291b4}#legend{border-left-color:#e76ba5}#legend b{color:#e7c5d7}.controls{border-bottom-color:#473a47}.links a{color:#edacd0}#stats{line-height:1.9}@media(max-width:860px){h1{font-size:17px}}\n'''
    html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W13 侵蚀之律者·蚀界·自演算研究母机 A1</title></head>
<body><header><div class="eyebrow">0005 / W13 / 作者蓝图 A1 · 外观待审</div><h1>W13 侵蚀之律者·蚀界·自演算研究母机</h1><p>真实整数格方块 · 原生 GT／模组／原版像素贴图 · <span id="actualSize">读取完整模型…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块表面…</div><div id="legend"><b id="modelName">蚀界研究母机</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>完整实体与原生像素贴图，动画为网页演示</span></div></section><aside>
<section class="controls"><h2>观察构件</h2><p>仅主控位置固定，其余实体格均可换成合法接口。</p><div id="models" class="row"></div><p id="modelStats"></p><label><input id="roof" type="checkbox" checked>显示蜂窝顶网格与数据垂线</label><label><input id="cutaway" type="checkbox">剖开前半基座</label></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row actions"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>运行演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 时间冻结</option><option value="work">运行 · 侵蚀演算</option></select><div class="row"><button id="pause" aria-pressed="false">暂停</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>四束绯红激光、数据雨脉冲与黑色方块粒子</label><p class="animationNote">三环按不同轴向转动，十三碑浮动，晶花轻微搏动。运行推进时间，待机冻结；NBT保存零秒静态整数格。</p></section>
<section class="controls"><h2>形体细节</h2><ul id="features"></ul></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16格参考网格</label><label><input id="axes" type="checkbox">XYZ坐标轴</label></section>
<details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块ID或名称"><div id="materials"></div></details><p id="stats"></p><p class="links">作者名义尺寸：1035×966×332。单角朝下的220格立方框与倾斜环按完整实际边界展示，具体差异见尺寸说明。</p>
<p class="links"><a href="W13-蚀界研究母机-A1.nbt">完整方块NBT</a> · <a href="完整整数格模型.npz">逐格模型</a> · <a href="conflicts.json" target="_blank">尺寸与穿模说明</a></p><p class="links"><a href="评审图集.html">评审图集</a> · <a href="manifest.json" target="_blank">生成记录</a> · <a href="materials.json" target="_blank">原生材质</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>
'''
    (OUT / 'style.css').write_text(css, 'utf8')
    (OUT / 'index.html').write_text(html, 'utf8')
    shutil.copy2(ROOT / 'tools/structure_delivery/w13_viewer_20261117.mjs', OUT / '生成脚本/viewer.mjs')
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    print(OUT)


if __name__ == '__main__':
    main()
