# -*- coding: utf-8 -*-
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '生成脚本').mkdir(exist_ok=True)
    css = (ROOT / 'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117/style.css').read_text('utf8')
    css += '\n#groups{display:grid;grid-template-columns:1fr 1fr;gap:0 8px}#groups label{font-size:12px}.animationNote{border-left-color:#bd4b85}.links{line-height:1.9}\n'
    html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W13 巨眼电视与旧电视山 T2</title></head>
<body><header><div class="eyebrow">0005 / W13 / 巨眼电视与旧电视山 T2-M1 · 外观待审</div><h1>W13 巨眼电视与旧电视山</h1><p>真实整数格方块 · 原生 GT／模组／原版像素贴图 · <span id="actualSize">读取完整模型…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块表面…</div><div id="legend"><b id="modelName">巨眼电视与旧电视山</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>逐格实体、原生像素贴图；眼珠与电缆动画为网页演示</span></div></section><aside>
<section class="controls"><h2>观察构件</h2><p>仅主控位置固定，其余实体格均可换成合法接口。</p><div id="models" class="row"></div><p id="modelStats"></p><div id="groups"></div></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row actions"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>动作演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 恢复静态</option><option value="work">运行 · 眼珠转动与电缆甩动</option></select><div class="row"><button id="pause" aria-pressed="false">暂停</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>眼珠、电缆、屏幕亮度与像素故障</label><p class="animationNote">眼珠在屏幕内改变注视方向，九根粗缆从固定根部向末梢逐渐加大甩幅，主控线两端固定。运行推进时间，暂停定格，待机恢复静态。动作仅接入此网页，NBT仍为T2静态方块。</p></section>
<section class="controls"><h2>形体细节</h2><ul id="features"></ul></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16格参考网格</label><label><input id="axes" type="checkbox">XYZ坐标轴</label></section>
<details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块ID或名称"><div id="materials"></div></details><p id="stats"></p>
<p class="links"><a id="nbtLink" href="W13-侵蚀之律者电视山-T2.nbt">完整方块NBT</a> · <a href="完整整数格模型.npz">逐格模型</a> · <a href="动态图集.html">动态图集</a> · <a href="评审图集.html">静态图集</a></p><p class="links"><a href="manifest.json" target="_blank">生成记录</a> · <a href="materials.json" target="_blank">原生材质</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>
'''
    (OUT / 'style.css').write_text(css, 'utf8')
    (OUT / 'index.html').write_text(html, 'utf8')
    viewer = (ROOT / 'tools/structure_delivery/w13_tv_t2_motion_viewer_20261117.mjs').read_text('utf8')
    (OUT / '生成脚本/viewer.mjs').write_text(viewer.replace('-T1.png', '-${data.candidate}.png'), 'utf8')
    for name in ['w13_tv_eye_motion_20261117.mjs', 'w13_tv_cable_motion_20261117.mjs', 'prepare_0005_w13_motion_data_20261117.py', 'w13_tv_body_20261117.py']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    print(OUT)


if __name__ == '__main__':
    main()
