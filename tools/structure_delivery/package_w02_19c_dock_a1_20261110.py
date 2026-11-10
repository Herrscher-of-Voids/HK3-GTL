# -*- coding: utf-8 -*-
"""复用已验收静态查看器，交付19C与工业船坞组合草案。"""
from html import escape
import json
from pathlib import Path
import re
import shutil
import w02_19c_dock_scene_a1_20261110 as g
import package_w02_19c_v3_20261110 as package


def main(geometry=None):
    g=geometry or globals()['g']
    package.main(g)
    manifest=json.loads((g.OUT/'manifest.json').read_text('utf8'))
    width,height,depth=manifest['size'];size=f'{width}×{depth}×{height}'
    page=g.OUT/'w02/三维评审.html';source=g.OUT/'生成脚本/viewer.mjs'
    script=source.read_text('utf8').replace('new THREE.Vector3(-.8,.35,1.5)','new THREE.Vector3(-.9,.75,1.4)')
    anchor="document.getElementById('loading').remove();"
    controls='''document.querySelectorAll('[data-scene]').forEach(button=>button.onclick=()=>{
    const mode=button.dataset.scene;
    groups.forEach(group=>{
      const robot=/^0[1-7]_/.test(group.name);group.visible=mode==='all'||(mode==='robot'?robot:!robot);
      document.querySelectorAll('[data-part]').forEach(input=>{if(input.dataset.part===group.name)input.checked=group.visible;});
    });draw();
  });
  '''
    assert anchor in script;script=script.replace(anchor,controls+anchor,1);source.write_text(script,'utf8')
    text=page.read_text('utf8')
    text=re.sub(r'<title>.*?</title>','<title>W02 · 19C自律构造船坞A1</title>',text,count=1)
    text=text.replace('<h1>理之律者 · 重装小兔19C</h1>','<h1>万象·自律工业矩阵 · 19C构造船坞</h1>')
    text=text.replace('A1 · 60张多视角参考 · 完整'+size,'A1 · 组合构图 · 完整'+size)
    text=text.replace('普通理之律者19C。沿用60张参考，细化11个完整静态构件；新增5个局部镜头。',
        '19C原形保持V6，仅整体平移；新增U形供料船坞、双手半成品、背部维护架、链井、双炮靶台与前控出货轨。26个静态构件。')
    text=text.replace('<button id="reset">重置视角</button>',
        '<p><button data-scene="all">完整组合</button><button data-scene="robot">只看小兔</button><button data-scene="dock">只看船坞</button></p><button id="reset">重置视角</button>')
    text=text.replace('data-view="core">胸甲','data-view="core">构造核心')
    text=text.replace('未接回649×493×303工业矩阵。没有控制器与接口占位，不代表机器成型或运行。',
        '静态组合草案，新增设施为本项目创作。前控及接口仅为视觉示意；没有注册机器能力，不代表游戏成型、运行或实装测试。')
    page.write_text(text,'utf8')
    cards=[('19C保持原形','V6的11个构件只整体平移，躯干、背部、节链、双臂和双炮均不改形。'),
           ('双手真正有工作对象','中央半成品下半为实体齿轮与装甲，上半为蓝色构造框，连接双掌的静态构造线。'),
           ('U形低矮船坞','两侧各三座加工站，沿供料轨汇入中央装配床；前方留出完整观看入口。'),
           ('背部接入设施','开放检修支架对应背部轴系，原下垂节链悬在约束井口上方。'),
           ('双炮对应处理工序','两座小型处理靶台沿现有炮口方向布置，保留双炮位置与角度。'),
           ('前控与出货轨','中央装配区向前连接出货轨与控制舰桥，控制器和接口仍为视觉示意。')]
    features=''.join('<article><h3>'+escape(title)+'</h3><p>'+escape(body)+'</p></article>' for title,body in cards)
    details=''.join('<figure><img src="'+value['file']+'" alt="'+value['label']+'"><figcaption>'+value['label']+'</figcaption></figure>' for value in g.CAMERA_VIEWS.values())
    (g.OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>万象·自律工业矩阵 · 19C构造船坞A1</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#09131f;color:#dfedff;font:16px/1.8 system-ui}}main{{max-width:1480px;margin:auto;padding:32px}}a{{color:#94c6ff}}nav{{display:flex;gap:22px;flex-wrap:wrap}}h1{{font-size:36px;line-height:1.3}}h2{{margin-top:44px}}.eyebrow{{color:#6da7ff;letter-spacing:2px}}.lead{{max-width:1000px;color:#b9cfe5}}.hero{{width:100%;border:1px solid #23415b;border-radius:10px}}.flow{{padding:18px;background:#13283d;border-left:4px solid #428DFF;margin:22px 0}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}article{{padding:18px;background:#102136;border:1px solid #29435f;border-radius:8px}}article h3{{margin:0;color:#a9ccff}}article p{{font-size:14px;margin-bottom:0}}figure{{margin:0;background:#0b1624}}figure img{{width:100%;display:block}}figcaption{{padding:10px;color:#b6d0e8}}.warning{{border-left:3px solid #acbac9;padding:12px 18px;background:#132332}}small{{color:#9db6ce}}@media(max-width:850px){{main{{padding:20px}}h1{{font-size:27px}}.cards,.grid{{grid-template-columns:1fr}}}}</style>
<main><p class="eyebrow">W02 · 普通理之律者 · 静态组合草案 A1</p><h1>万象·自律工业矩阵<br>重装小兔19C构造船坞</h1><p class="lead">把19C放进一条看得懂的生产工序：六站供料，双炮处理，双手组装，前方出货。V6原形完整保留；船坞围绕它的工作位置生成。</p>
<nav><a href="w02/三维评审.html">打开可旋转三维预览 →</a><a href="../{g.PRIOR.name}/index.html">保留的V6独立小样</a><a href="参考图总览.html">19C参考图库</a><a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></nav>
<p><small>实际宽{width} × 深{depth} × 高{height} · {manifest['blocks']:,}实体方块 · 26个构件 · 无动画 · 未实装</small></p><img class="hero" src="完整预览.png" alt="19C与U形工业船坞组合全景">
<div class="flow">两侧供料加工 → 双炮材料处理 → 双手完成装配 → 前控与出货轨</div><div class="cards">{features}</div>
<h2>从不同方向看组合关系</h2><div class="grid"><figure><img src="正面.png" alt="正面"><figcaption>正面：中央工作对象与低矮两侧船坞</figcaption></figure><figure><img src="俯视.png" alt="俯视"><figcaption>俯视：U形供料布局和前方开口</figcaption></figure><figure><img src="侧面.png" alt="侧面"><figcaption>侧面：半成品、双手与背后支架的距离</figcaption></figure><figure><img src="背面.png" alt="背面"><figcaption>背面：开放维护架及节链约束井</figcaption></figure></div>
<h2>五个局部镜头</h2><div class="grid">{details}</div>
<h2>本轮改动边界</h2><p>19C的11个构件仅整体平移(0,+40,-70)，坐标差和材质逐格核对；新设施与19C无共享体素。完整生成后求实际边界，649×493×303为名义最低参考，不用于裁切。</p><p>普通理律构造蓝#428DFF、白甲、深灰骨架及小面积橙色沿用。60张官方／二创分源参考用于19C；工业船坞、半成品和工序分工为本项目新设计。</p>
<p class="warning">这是完整构图候选，外观尚未批准。前控和接口是视觉示意，未注册机器能力、配方或研究链，未进行游戏成型、运行或性能验收。新增设施之间有供料与支架接合，未宣称全面无穿模。</p>
<nav><a href="verification.json">离线核验</a><a href="manifest.json">坐标与构件记录</a><a href="w02/{manifest['name']}.nbt">NBT</a><a href="w02/{manifest['name']}.schem">Schematic</a></nav></main></html>''','utf8')
    for file in [Path(__file__),Path(g.__file__)]:shutil.copy2(file,g.OUT/'生成脚本'/file.name)


if __name__=='__main__':main()
