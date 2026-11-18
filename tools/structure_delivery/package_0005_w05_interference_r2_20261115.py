# -*- coding: utf-8 -*-
from datetime import datetime
import json
from pathlib import Path
import shutil

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
OUT = ROOT / 'deliveries/0005_W05_部件穿模检查_R2_20261115'
LOG = ROOT / 'logs/0005-w05-interference-r2-20261115'
OUT.mkdir(exist_ok=True)
archive = np.load(SOURCE / '原始构件数据.npz')
sampled = json.loads((LOG / 'motion-sampled-center-witnesses.json').read_text('utf8'))
cases = []


def static_case(key, title, a, b, note, half, filter_y=0):
    x = archive[a + '_xyz']
    y = archive[b + '_xyz']
    dtype = np.dtype((np.void, x.dtype.itemsize * 3))
    common = np.intersect1d(np.ascontiguousarray(x).view(dtype).ravel(), np.ascontiguousarray(y).view(dtype).ravel())
    points = common.view(x.dtype).reshape(-1, 3)
    points = points[points[:, 1] >= filter_y]
    center = (points.min(0) + points.max(0)) / 2
    cases.append(dict(id=key, title=title, a=a, b=b, mode='idle', time=0,
        metric=f'{len(points):,}个参考姿态共占格', note=note, center=center.tolist(), half=half,
        markers=points.tolist(), marker_kind='原始整数格几何的真实共占格'))


static_case('upper-rim', '后副塔上口 × 青绿管网', 'wing_left_mobius_network', 'wing_left_vortex_tower_3',
    '左右各1,942格共占；其中1,252格涉及深青实体机壳、200格涉及白装甲，不仅是镂空框架包围盒相遇。', [68, 48, 68])
static_case('front-frame', '前副塔侧框 × 青绿管网', 'wing_left_mobius_network', 'wing_left_vortex_tower_1',
    '左右各450格共占，位于Y103～134；框架进入管网占格，需要预留结构通道。', [68, 36, 68])
static_case('vanes', '导流百叶 × 前副塔上部', 'wing_left_guide_vanes', 'wing_left_vortex_tower_1',
    '剔除正常基脚后，左侧仍101格、右侧109格上部交叠；后副塔顶各另有1格擦碰。', [55, 35, 62], filter_y=70)
for key, title, a, b, note, half in [
    ('rotor-network', '前副塔叶轮 × 青绿管网', 'wing_left_lift_rotor_1', 'wing_left_mobius_network',
     '左右前副塔均命中；左侧工作25.50秒有138个源方块中心严格进入管网实体格。', [54, 20, 54]),
    ('rotor-brace', '副塔叶轮 × 塔内斜撑', 'wing_left_lift_rotor_2', 'wing_left_vortex_tower_2',
     '六座副塔均会擦碰；展示左中塔工作47.25秒，8个源方块中心进入塔体。', [49, 18, 49]),
    ('helix-rotor', '实体双螺旋风柱 × 叶轮', 'wing_left_lift_rotor_2', 'wing_left_vortex_column_2',
     '六组均持续命中；风柱由8,600个海晶灯实体格构成，不是单独的光效线。', [46, 80, 46]),
    ('helix-network', '后副塔实体风柱 × 青绿管网', 'wing_left_vortex_column_3', 'wing_left_mobius_network',
     '左右后塔均会扫入管网；展示左侧工作35.25秒，80个源方块中心进入管网实体格。', [58, 48, 60]),
]:
    record = next(r for r in sampled['records'] if r['mode'] == 'work' and r['source'] == a and r['target'] == b)
    point = record['source_center_world']
    center = point if key in ('helix-network',) else [(-175 if 'left' in a else 175), 132, (-170 if '_1' in a else 10)]
    cases.append(dict(id=key, title=title, a=a, b=b, mode='work', time=record['time_s'],
        metric=f"{record['max_center_hits']}个源中心进入目标实体格", note=note, center=center, half=half,
        markers=[point], marker_kind='一个严格位于双方实体格内部的源格中心见证点'))
data = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'), source=str(SOURCE.relative_to(ROOT)),
    material_approval='负责人已认可R2配色；本页标记色只用于检查。', cases=cases,
    scope='73构件完整参考姿态成对交集；21运动构件待机/工作0～60秒、每0.25秒采样；关键核心/王冠另有连续包络净空证明。',
    limitation='中心命中能证实单位方块实体包络交叠；未命中不能单独证明无边角或帧间相交。框架贴图透明孔洞未作逐像素判定；不等于游戏内成型、运行或渲染验收。')
(LOG / 'inspection-cases.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>0005 · W05 R2 部件穿模检查</title><style>
*{box-sizing:border-box}body{margin:0;background:#101e23;color:#deeeea;font:14px/1.65 "Microsoft YaHei",sans-serif}a{color:#96e8cb}header{padding:15px 24px;border-bottom:1px solid #355047}h1{font-size:21px;margin:0}header p{margin:3px 0;color:#b1c9c3}.layout{display:grid;grid-template-columns:minmax(0,1fr) 370px;height:calc(100vh - 128px);min-height:720px}iframe{width:100%;height:100%;border:0}aside{padding:18px;overflow:auto;border-left:1px solid #355047}button{display:block;width:100%;padding:9px;text-align:left;border:1px solid #38544c;background:#19312f;color:#c9e5dc;margin:7px 0;cursor:pointer}button.active{border-color:#a4d9c4;background:#285348}h2{font-size:17px}h3{font-size:14px;margin:18px 0 5px}.note{padding:10px;border-left:3px solid #b8a77b;background:#2c2d26}.metric{font-weight:600;color:#f5d99d}.red{color:#ff6f76}.cyan{color:#6de6ff}.yellow{color:#ffe465}small{color:#abc0b8}.summary{padding:24px;max-width:1100px;margin:auto}li{margin:7px 0}.legend{font-size:12px}.safe{color:#a7ddbc}.status{font-size:12px;color:#a8bfb7}@media(max-width:1000px){.layout{display:flex;flex-direction:column;height:auto}iframe{height:65vh}aside{border:0}}
</style><header><h1>0005 · W05 R2 部件穿模检查</h1><p>已确认存在局部干涉。R2配色保留，本页只增加检查标记；几何与运动参数未改。</p><p><a href="../__SOURCE__/三维评审.html">原配色完整预览</a> · <a href="#details">检查范围与结论</a> · <a href="../../logs/0005-w05-interference-r2-20261115/completion.json">检查回执</a></p></header>
<main class="layout"><iframe id="viewer" src="../__SOURCE__/三维评审.html" title="W05冲突部件定位"></iframe><aside><div id="status" class="status">载入检查视图…</div><div class="legend"><span class="red">红色：部件A</span> · <span class="cyan">蓝色：部件B</span><br><span class="yellow">黄色：共占格或中心见证点</span></div><div id="buttons"></div><h2 id="title"></h2><div id="metric" class="metric"></div><p id="note"></p><small id="time"></small><p><label><input type="checkbox" id="markers" checked>显示黄色冲突标记</label></p><button id="all">恢复完整模型与原配色</button><p class="status">鼠标左键旋转，右键平移，滚轮缩放。截图为固定复现时刻；原配色预览可继续播放动画。</p></aside></main>
<section class="summary" id="details"><h2>检查结论</h2><ul><li>明确静态穿插：左右管网穿过前副塔侧框及后副塔上口；百叶还与塔体局部擦碰。</li><li>明确运动干涉：前副塔叶轮碰管网、六叶轮碰塔内斜撑、六实体双螺旋风柱穿叶轮、两后风柱扫入管网。</li><li class="safe">中央核心、两陀螺环及三王冠环有连续包络净空。核心与内陀螺净空下界6.83格，两陀螺之间8.85格。</li><li>正常底座/承重臂、接口、塔基和轴向过渡嵌接单独保留；管网与百叶的装配接口仍待确认，不直接判作缺陷。</li></ul><h3>方法与限制</h3><p>__SCOPE__</p><p>__LIMIT__</p><p>未改方块、几何或动画，未构建/安装JAR，未运行游戏。</p></section><script>
const DATA=__DATA__,iframe=document.getElementById('viewer');let api,overlay,current;
function markerMesh(points){const sample=api.groups[0].children[0],vertices=[],corners=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]];for(const p of points)for(const face of faces)for(const i of face)for(let a=0;a<3;a++)vertices.push(p[a]+(corners[i][a]-.5)*.92);const geometry=new sample.geometry.constructor();geometry.setAttribute('position',new sample.geometry.attributes.position.constructor(new sample.geometry.attributes.position.array.constructor(vertices),3));geometry.computeVertexNormals();const material=new sample.material.constructor({color:'#ffe465',emissive:'#ffe465',emissiveIntensity:1,transparent:true,opacity:.88,depthTest:false});const mesh=new sample.constructor(geometry,material);mesh.renderOrder=999;return mesh;}
function restore(){for(const g of api.groups){g.visible=true;for(const m of g.children)m.material=m.userData.auditOriginal;}if(overlay){api.scene.remove(overlay);overlay.geometry.dispose();overlay.material.dispose();overlay=null;}}
function selectCase(index){restore();current=index;const c=DATA.cases[index];api.mode(c.mode);api.freeze(c.time);for(const g of api.groups){g.visible=g.name===c.a||g.name===c.b;if(g.visible)for(const m of g.children){const mat=m.userData.auditOriginal.clone();mat.color.set(g.name===c.a?'#ff536a':'#54d5ff');mat.emissive.set(g.name===c.a?'#ff304a':'#319cc9');mat.emissiveIntensity=.35;m.material=mat;}}api.config.data.views.audit={label:c.title,center:c.center,half:c.half,direction:[-1,.6,-1]};api.fit('audit');overlay=markerMesh(c.markers);overlay.visible=document.getElementById('markers').checked;api.scene.add(overlay);api.render();document.getElementById('title').textContent=c.title;document.getElementById('metric').textContent=c.metric;document.getElementById('note').textContent=c.note;document.getElementById('time').textContent=`${c.mode==='work'?'工作':'参考'}姿态 ${c.time.toFixed(2)}秒 · ${c.marker_kind}`;document.querySelectorAll('[data-case]').forEach(b=>b.classList.toggle('active',+b.dataset.case===index));}
document.getElementById('markers').onchange=e=>{if(overlay)overlay.visible=e.target.checked;api.render();};document.getElementById('all').onclick=()=>{restore();api.mode('idle');api.freeze(12);api.fit('front');document.querySelectorAll('[data-case]').forEach(b=>b.classList.remove('active'));document.getElementById('title').textContent='完整模型 · 原配色';document.getElementById('metric').textContent='R2材料已经负责人认可';document.getElementById('note').textContent='本次仅定位干涉，没有修改结构。';document.getElementById('time').textContent='';};
async function ready(){if(!iframe.contentWindow.W05_AUTHOR_READY){setTimeout(ready,100);return;}api=iframe.contentWindow.W05Author;const doc=iframe.contentDocument,style=doc.createElement('style');style.textContent='header,aside{display:none!important}#stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}body{overflow:hidden!important}';doc.head.append(style);doc.getElementById('effects').checked=false;doc.getElementById('bloom').checked=false;doc.getElementById('bloom').dispatchEvent(new iframe.contentWindow.Event('change'));for(const g of api.groups)for(const m of g.children)m.userData.auditOriginal=m.material;DATA.cases.forEach((c,i)=>{const b=document.createElement('button');b.dataset.case=i;b.textContent=`${i+1}. ${c.title}`;b.onclick=()=>selectCase(i);document.getElementById('buttons').append(b);});document.getElementById('status').textContent='7处代表性复现 · 左右对称问题已同时记录';requestAnimationFrame(()=>{selectCase(0);window.W05Inspection={api,selectCase,DATA};window.W05_INSPECTION_READY=true;});}iframe.onload=ready;
</script></html>'''
page = page.replace('__SOURCE__', SOURCE.name).replace('__SCOPE__', data['scope']).replace('__LIMIT__', data['limitation'])
page = page.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c'))
(OUT / '部件穿模检查.html').write_text(page, 'utf8')
shutil.copy2(Path(__file__), LOG / Path(__file__).name)
print(json.dumps(dict(cases=len(cases), output=str(OUT)), ensure_ascii=False))
