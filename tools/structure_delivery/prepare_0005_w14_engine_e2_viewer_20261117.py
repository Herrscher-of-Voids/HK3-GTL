from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W14_行星发动机维度基座_E2_20261117'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scripts = OUT / '生成脚本'
    scripts.mkdir(exist_ok=True)
    css = '''*{box-sizing:border-box}html,body{margin:0;background:#101a25;color:#e4ebf5;font:14px/1.65 system-ui,"Microsoft YaHei",sans-serif}header{padding:14px 24px;border-bottom:1px solid #3b4c60}.eyebrow{color:#c1a9f1;font-size:12px;letter-spacing:.1em}h1{font-size:25px;margin:2px 0}header p{margin:2px 0;color:#b8c9db}main{display:grid;grid-template-columns:minmax(0,1fr) 330px;height:calc(100vh - 111px)}#stage{position:relative;overflow:hidden;min-height:550px}canvas{display:block}#loading{position:absolute;inset:43% 8%;text-align:center}#legend{position:absolute;left:18px;bottom:18px;background:#14202de8;border:1px solid #42526b;padding:10px 14px;font-size:12px;color:#c7d3e2;pointer-events:none}#legend b{color:#e7e0f6}#legend span{color:#b4c6da}aside{overflow:auto;background:#182535;padding:16px}h2{font-size:15px;margin:0 0 8px}p{margin:7px 0}.controls{padding-bottom:16px;margin-bottom:16px;border-bottom:1px solid #3a4b61}.row{display:flex;flex-wrap:wrap;gap:6px}button,select,input[type=search]{background:#213349;color:#dce7f5;border:1px solid #53647a;border-radius:4px;padding:7px 9px;font:inherit}button{cursor:pointer}button:hover,button.active{background:#415373;border-color:#c0a5ee;color:#fff}label{display:block;margin:6px 0}input[type=checkbox]{accent-color:#bda9f3;margin-right:6px}input[type=range],input[type=search]{width:100%}select{max-width:100%}input[type=range]{accent-color:#bda9f3}.slice{display:flex;justify-content:space-between;align-items:center;gap:8px}#modelStats,#stats{font-size:12px;color:#afc0d5}#features{padding-left:19px;margin:0;color:#c6d4e5}#features li{margin:5px 0}#groups{display:grid;grid-template-columns:1fr;gap:0 8px}.animationNote{font-size:12px;color:#b9c9dc;border-left:3px solid #bda9f3;padding-left:9px}.links{font-size:12px;line-height:1.9}a{color:#c3b0f4}code{font-size:11px;overflow-wrap:anywhere}summary{cursor:pointer;color:#d1def0}output{font-size:12px;color:#b8cbe0}[hidden]{display:none!important}@media(max-width:900px){main{display:block;height:auto}#stage{height:70vh;min-height:450px}aside{overflow:visible}header{padding:12px 16px}}'''
    html = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"><title>W14 行星发动机维度基座 E2</title></head><body>
<header><div class="eyebrow">0005 / W14 / E2 · 下层模块外观候选</div><h1>世界泡轮回引擎 · 七维度行星发动机</h1><p>真实整数格方块 · GT／模组像素贴图 · <span id="actualSize">读取完整模型…</span></p></header>
<main><section id="stage"><div id="loading">载入完整方块表面…</div><div id="legend"><b id="modelName">七维度行星发动机</b><br>左键旋转 · 右键平移 · 滚轮缩放<br><span>火箭尾焰与进料粒子为网页演示，不计入实体NBT</span></div></section><aside>
<section class="controls"><h2>观察构件</h2><p class="animationNote">E2为W14下层候选。七个供料球与七个扇区分别表现主世界、末地、地狱、月球、火星、金星和银河系。</p><div id="models" class="row"></div><p id="modelStats"></p><div id="groups"></div></section>
<section class="controls"><h2>观察视角</h2><div id="views" class="row"></div><div class="row actions"><button id="reset">复位</button><button id="screenshot">保存截图</button><button id="fullscreen">全屏</button></div></section>
<section class="controls"><h2>运行演示 <output id="timeValue">0.0 s</output></h2><select id="mode"><option value="idle">待机 · 时间冻结</option><option value="work">运行 · 火箭尾焰与维度进料</option></select><div class="row"><button id="pause" aria-pressed="false">暂停</button><button id="timeZero">回到零秒</button></div><input id="time" type="range" min="0" max="60" step=".1" value="0"><label><input id="effects" type="checkbox" checked>火箭尾焰与维度进料粒子</label><p class="animationNote">喷嘴向上喷出约680格尾焰：白热核心、蓝白内焰、橙黄外焰与逸散火星。七维度球与对应扇区同色连通。动画为网页演示，实体NBT保存静态模型，实际消耗规则另行接入。</p></section>
<section class="controls"><h2>形体细节</h2><ul id="features"></ul></section>
<section class="controls"><h2>方块剖切</h2><div class="slice"><select id="axis"><option value="y">Y 高度</option><option value="x">X 宽度</option><option value="z">Z 深度</option></select><output id="layerLabel"></output></div><input id="layer" type="range" step="1"><div class="row"><button id="fullLayer">显示全部</button></div><label><input id="grid" type="checkbox">16格参考网格</label><label><input id="axes" type="checkbox">XYZ坐标轴</label></section>
<details><summary>原生方块材质</summary><input id="materialSearch" type="search" placeholder="搜索方块ID或名称"><div id="materials"></div></details><p id="stats"></p>
<p class="links"><a id="nbtLink">完整方块NBT</a> · <a href="评审图集.html">评审图集</a> · <a href="../0005_W14_行星发动机基座_E1_20261117/references.html">行星发动机参考图</a></p><p class="links"><a href="manifest.json" target="_blank">生成记录</a> · <a href="materials.json" target="_blank">原生材质</a></p>
</aside></main><script src="data.js"></script><script src="viewer.bundle.js"></script></body></html>'''
    (OUT / 'style.css').write_text(css, 'utf8')
    (OUT / 'index.html').write_text(html, 'utf8')
    shutil.copy2(ROOT / 'tools/structure_delivery/w14_engine_viewer_e2_20261117.mjs', scripts / 'viewer.mjs')
    shutil.copy2(Path(__file__), scripts / Path(__file__).name)
    print(OUT)


if __name__ == '__main__':
    main()
