# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-23 · 内测5的69座逐台占地规划和离线比例预览。
读取工业树v5旧尺寸；输出新尺寸提案，保留旧记录，不写NBT/Pattern/存档。
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'doc/HK3GTL-内测5/03_机器结构'
TREE=ROOT/'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html'
OUTPUT=DOC/'内测5_69座多方块逐台占地规划与比例预览_v2.html'
NOW=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 水平尺寸为宽×长，第三项为建议高度；已有成形实体保留现尺寸。
# Width × length in blocks, followed by proposed height; existing physical anchors retain their dimensions.
PROPOSED={
'I01-1':(17,17,33),'I01-2':(25,25,37),'I01-3':(37,37,45),'I01-4':(53,53,61),
'I02':(17,21,17),'I03':(25,29,25),'I04':(21,21,33),'I05':(21,25,29),
'I06':(25,33,21),'I07':(19,21,19),'I08':(33,33,33),'I09':(21,25,25),
'I10':(25,29,25),'I11':(33,37,25),'I12':(25,29,29),'I13':(25,37,29),
'I14':(33,37,29),'I15':(29,49,27),'I16':(33,57,29),'I17':(33,41,29),
'I18':(29,49,27),'I19':(25,25,29),'I20':(41,41,37),'I21':(65,65,49),
'I22':(97,97,73),'I23':(33,37,35),'I24':(65,81,49),'I25':(41,49,33),
'I26':(49,81,37),'I27':(129,129,81),'I28':(81,97,57),'I29':(65,65,57),
'I30':(49,57,43),'I31':(65,81,49),'I32':(41,49,37),'I33':(49,65,41),
'I34':(81,81,97),'I35':(65,65,57),'I36':(33,33,49),'I37':(97,129,65),
'I38':(49,49,57),'I39':(41,65,49),'I40':(65,81,49),'I41':(49,49,57),
'I42':(97,161,65),'I43':(65,81,49),'I44':(49,49,81),'I45':(25,97,29),
'S01':(17,25,17),'S02':(29,33,25),'S03':(41,49,33),'S04':(65,65,49),'S05':(129,129,97),
'W01':(257,257,81),'W02':(257,321,97),'W03':(321,321,129),
'W04':(257,289,113),'W05':(289,321,97),'W06':(289,321,97),
'W07':(321,385,97),'W08':(289,289,129),'W09':(321,321,113),
'W10':(257,257,161),'W11':(385,385,97),'W12':(385,513,113),
'W13':(321,353,129),'W14':(385,385,161),'W15':(513,513,193),
'H01':(536,201,94),
}
# 每座奇观的外包尺寸按其功能轮廓定，不复用同一建筑造型。
# Wonder-specific planning notes describe only footprint purpose, not built geometry.
MOTIFS={
'W01':'圆形星庭＋对向迎宾廊；四角保留群星观测区。',
'W02':'中央工业矩阵＋六座分布式装配场；长向为物料和算力干线。',
'W03':'内外双虚数锚环＋四向悬臂；回路横跨整片广场。',
'W04':'双电极长廊＋中央放电塔；两端留安全隔离场。',
'W05':'双流体环道＋可视化流场核心；纵向保留回流区。',
'W06':'分层冷凝阵列＋低温封闭区；横向容纳维护缓冲。',
'W07':'舟体形再生舱＋左右再生工坊；长向呈明显舰体轮廓。',
'W08':'多层环状熔铸区＋中央竖向恒星炉；四面独立散热。',
'W09':'文明记录大厅＋多列知识网络翼；围出开放中庭。',
'W10':'深井口＋多圈稳定设施；高度服务于竖井而非占地分级。',
'W11':'分布式节点广场＋外围工业调度岛；避免中心塔一统造型。',
'W12':'长边能量约束壁＋端部检修门廊；中央为受约束空场。',
'W13':'并列自演算实验翼＋中间样本回收廊；保留可替换模块区。',
'W14':'世界泡循环环＋二审门廊；入口与回收区分开。',
'W15':'树海朝觐轴线＋中央审判圣座＋层层外庭；四面分区设计。',
'H01':'现行舰体尺寸保留；独立毕业旗舰，不算入15座剧情奇观。',
}
INDUSTRIAL={
'I01-1':'已建一阶主塔保持原外包；后续阶级另建分支。',
'I01-2':'固态塔新增两侧冷凝翼与隔离回廊。',
'I01-3':'气态塔放大集气廊和上下供气回路。',
'I01-4':'能量态主塔与四向收束设施分开检修。',
'I02':'完整建筑稿已做17×21×17；未获最终结构验收，不重标尺寸。',
'I03':'双离心筒与母液、残渣两侧分流设备分开布置。',
'I04':'三段约束立塔，四侧冷却立柱需要独立基础。',
'I08':'核心周围设置玻璃隔离层和对称冷却设施。',
'I15':'长向前后分出退火与重构段，保持实物流转。',
'I16':'扩宽加工巷道，独立废料与成品出口。',
'I19':'保留动力堆芯四周冷却和离线安全空间。',
'I20':'中型反应堆双环供冷与更大检修带。',
'I21':'大型反应堆分开的散热场、能源干线和维护翼。',
'I22':'究极反应堆采用分区外场和隔离廊；并非实心97格盒。',
'I24':'远距观测基线需要长于核心计算舱的两翼。',
'I26':'无人采掘调度台含出港、返港与检修区。',
'I27':'世界泡整体捕获需要环形观测外场和独立回收入口。',
'I28':'真实世界泡终止要求隔离场与回收线物理分区。',
'I29':'模拟泡构筑外周安全环并保留维护入口。',
'I31':'模拟泡终止与资源回收需要独立的出入路径。',
'I33':'神之键装配工段和两侧检测工段串联。',
'I34':'树观测使用多站长基线及中央资料塔。',
'I35':'四向锚脚延伸至外环，中心留信号室。',
'I37':'世界维系试验平台外包包含隔离试验区。',
'I39':'无人中继站前后区分发射与回收。',
'I40':'奇观材料合成按进料、反应、成品独立布置。',
'I42':'预制工厂含长向构件运输廊和两侧生产翼。',
'I43':'文明验收需要样品区与独立仪器走廊。',
'I44':'信标靠竖向观测架，四向锚基不假定新维度已可无限高。',
'I45':'列车须保留细长舰体和前后缓冲段；长97宽25。',
'S01':'现行研究所占地保持，已有研究实机验收。',
'S02':'二阶研究所增加左右独立实验区。',
'S03':'三阶研究所形成共同档案厅和并行仪器翼。',
'S04':'四阶研究所分开实验厅、样本区和供能区。',
'S05':'认知穹顶外包包含资料穹顶、环形研究所及维护走廊。',
}

def flatten(nodes):
    for node in nodes:
        if 'dimensions' in node:
            yield node
        yield from flatten(node.get('children',[]))

def grade(width,length):
    maximum=max(width,length)
    return '普通级' if maximum<=31 else '中型' if maximum<=64 else '大型' if maximum<=95 else '超大型' if maximum<=255 else '文明奇观级'

source=TREE.read_text(encoding='utf-8')
old_nodes=json.loads(source.split('const nodes=',1)[1].split('const labels=',1)[0].strip().rstrip(';'))
original=list(flatten(old_nodes))
assert len(original)==69 and {entry['id'] for entry in original}==set(PROPOSED), 'source tree must still contain exactly these 69 IDs'
rows=[]
for entry in original:
    machine_id=entry['id']
    width,length,height=PROPOSED[machine_id]
    old=entry['dimensions']
    assert min(width,length,height)>=17
    assert max(width,length) >= 256 if machine_id.startswith('W') else True
    assert (width,length,height)==tuple(old) if machine_id in ('I01-1','I02','S01','H01') else True
    rows.append({'id':machine_id,'name':entry['title'],'old':old,'size':[width,length,height],
        'oldGrade':grade(*old[:2]),'grade':grade(width,length),'oldArea':old[0]*old[1],
        'area':width*length,'status':'保持已建/已做建筑外包' if machine_id in ('I01-1','I02','S01','H01') else '新占地候选，待逐台审核',
        'note':MOTIFS.get(machine_id,INDUSTRIAL.get(machine_id,'按实际工艺分区扩展；控制器、物流、检修空间逐台落实。'))})
assert len(rows)==69 and sum(entry['id'].startswith('W') for entry in rows)==15
assert not any(entry['id'].startswith('W') and entry['grade']!='文明奇观级' for entry in rows)
counts=Counter(entry['grade'] for entry in rows)
# Make one portable HTML: no server, CDN, image, generated filler NBT, or mod assets.
# 单份HTML离线预览；比例图只代表外包范围，内区是功能规划说明，不充当逐层实建。
DATA=json.dumps(rows,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
CSS='''
:root{color-scheme:dark;--base:#0b1020;--panel:#141e32;--edge:#405270;--ink:#edf3ff;--cyan:#78e7de;--gold:#ffd392;--muted:#9caecb}*{box-sizing:border-box}body{margin:auto;background:var(--base);color:var(--ink);font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif;max-width:1500px;padding:25px}a{color:var(--cyan)}h1{font-size:clamp(25px,3vw,38px);margin-bottom:6px}h2{font-size:20px}.note{border-left:4px solid var(--gold);padding:12px 17px;background:#26243d}.summary{display:flex;flex-wrap:wrap;gap:9px;margin:17px 0}.summary>div{background:var(--panel);border:1px solid var(--edge);border-radius:12px;padding:10px 16px;min-width:145px}.summary b{display:block;font-size:23px;color:var(--cyan)}.grid{display:grid;grid-template-columns:minmax(330px,0.95fr) minmax(420px,1.05fr);gap:18px}.box{background:var(--panel);border:1px solid var(--edge);border-radius:13px;padding:15px;min-width:0}.controls{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}input,select,button{font:inherit;background:#182943;color:var(--ink);border:1px solid #60718e;border-radius:8px;padding:8px}input{min-width:160px;flex:1}button{cursor:pointer}button:hover,tr:hover{background:#293c59}button:focus-visible,input:focus-visible,select:focus-visible,tr:focus-visible{outline:2px solid var(--cyan)}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:8px;border-bottom:1px solid #34445f;text-align:left;white-space:nowrap}th{color:var(--cyan);position:sticky;top:0;background:#1d2c46}.table-scroll{overflow:auto;max-height:640px}tbody tr{cursor:pointer}tbody tr.selected{background:#365070}small{color:var(--muted)}.drawing{display:flex;gap:12px;flex-wrap:wrap}.draw-panel{min-width:240px;flex:1}.draw-panel svg{width:100%;height:290px;background:#101a2d;border:1px solid #344564;border-radius:8px}.draw-panel p{margin:4px 0;text-align:center}.chips{display:flex;gap:8px;flex-wrap:wrap;margin:13px 0}.chip{background:#253350;padding:4px 9px;border-radius:20px}#detail strong{color:var(--gold)}#buckets{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px}.bucket{border:1px solid var(--edge);border-radius:9px;padding:10px;background:#0f1a2d}.bucket svg{width:100%;height:90px}.bucket a{font-size:13px;display:inline-block;padding:4px}footer{border-top:1px solid var(--edge);color:var(--muted);margin-top:25px;padding-top:15px}canvas{max-width:100%}@media(max-width:850px){.grid{grid-template-columns:1fr}body{padding:12px}}
'''
HTML='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内测5 · 69座多方块最新占地尺寸和等比例预览</title><style>__CSS__</style><h1>内测5 · 69座多方块最新占地规划与比例预览</h1><p>__STAMP__ Asia/Hong_Kong · 逐台尺寸提案 v2；旧工业树v5继续保留历史尺寸</p>
<div class="note"><strong>这才是新占地尺寸方案：</strong>下面69台均给出新的宽×长×高，左侧可搜索和点击，右侧按同一比例尺画出旧/新占地；俯视图是外包面积，<strong>不是</strong>69座实际建筑、Pattern或NBT。W01–W15的旧几十格预览均作废，不计入新结构验收。I02完整建筑保持17×21×17，休伯利安保持536×201×94。</div>
<div class="summary" id="summary"></div><div class="grid"><section class="box"><h2>逐台占地清单</h2><div class="controls"><input id="search" type="search" placeholder="搜索ID或名称" aria-label="搜索机器"><select id="filter" aria-label="筛选占地等级"><option value="all">全部等级</option><option>普通级</option><option>中型</option><option>大型</option><option>超大型</option><option>文明奇观级</option></select><select id="family" aria-label="筛选机器组"><option value="all">全部69台</option><option value="I">I 工业</option><option value="S">S 研究所</option><option value="W">W 奇观</option><option value="H">H 旗舰</option></select></div><small id="resultCount"></small><div class="table-scroll"><table><thead><tr><th>编号／机器</th><th>旧宽×长</th><th>新宽×长×高</th><th>新等级</th><th>面积变化</th></tr></thead><tbody id="list"></tbody></table></div></section>
<section class="box"><h2 id="selected">选择一台机器</h2><div class="chips" id="chips"></div><div class="drawing"><div class="draw-panel"><p>旧尺寸（历史提案）</p><svg id="oldMap" role="img" aria-label="旧占地俯视图"></svg></div><div class="draw-panel"><p>新尺寸（待审候选）</p><svg id="newMap" role="img" aria-label="新占地俯视图"></svg></div></div><p><small>两张图严格共用刻度；方格间距见下方刻度条。长×宽均为方块数，图中框线不是方块。</small></p><p id="detail"></p><div id="scale"></div><p><strong>状态：</strong><span id="state"></span></p><p><a href="I02结构审核_v1/审核入口.html">I02 的实际逐格建筑和NBT</a> · <a href="../02_工业计划/HK3GTL工业计划树状图_v5.html">旧工业树v5</a></p></section></div>
<section class="box"><h2>规模鸟瞰：按组等比例比较</h2><p>组内小图采用同一比例尺，只表达外包面积，不暗示建筑已完工。点击编号可查看旧新对照和设计用途。</p><div id="buckets"></div></section><section class="box"><h2>设计边界与下一步</h2><ul><li>唯一已确认的分级规则：以外包宽与长的最大值划级，普通16–31／中型32–64／大型65–95／超大型96–255／文明奇观≥256；高度不参与等级。</li><li>新尺寸是本轮重新提出的逐台候选；I01-1、I02、S01与H01保持已做外包，其余须逐台审建筑外形、拆分空间、材料可达性、检修与仓室。</li><li>奇观每台有不同功能轮廓；比例图不通过“放大旧占位NBT”造新结构。15座奇观按具体占地重新设计、预览、审图，之后才能迁移GTCEu Pattern。</li><li>巨构结构检查不能靠一次性扫描 513×193×513 体积或强制加载所有区块；设计和实现要先验证分区检查、服务器内存和保存重载。</li><li>休伯利安按最长边536归奇观级体量，但仍独立于15座剧情奇观；全维度解除Y高度限制是独立工程，本页没有宣称已实现。</li></ul></section><footer>变更记录 #1 · __STAMP__ · 读取工业树v5的69台旧尺寸；新增69条明确尺寸、等比例交互预览、规划用途与阶段状态；不改已有NBT、玩家存档、配方、Mixin、控制器与游戏资源。数据与设计仅来自本项目文档，无新增第三方资源。</footer>
<script>/* 中文：仅客户端绘制规划矩形；无网络请求或存档写入。English: read-only, offline footprint comparison. */
const machines=__DATA__;const order=['普通级','中型','大型','超大型','文明奇观级'];const colors={'普通级':'#79d8bd','中型':'#75c4e8','大型':'#a7a0ff','超大型':'#e3a5e6','文明奇观级':'#ffcf83'};const byId=Object.fromEntries(machines.map(x=>[x.id,x]));let current=byId['W01'];
const el=(tag,attrs={},content='')=>{const node=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v));node.textContent=content;return node};const label=(n)=>n.toLocaleString('zh-CN');
function draw(svg,width,length,maxWidth,maxLength,color){svg.replaceChildren();const NS='http://www.w3.org/2000/svg',M=18;svg.setAttribute('viewBox',`0 0 ${maxWidth+M*2} ${maxLength+M*2}`);const element=(type,a)=>{let x=document.createElementNS(NS,type);for(const [k,v] of Object.entries(a))x.setAttribute(k,v);svg.append(x);return x};const step=maxWidth>256?64:maxWidth>95?16:maxWidth>31?8:4;for(let n=0;n<=maxWidth;n+=step)element('line',{x1:M+n,y1:M,x2:M+n,y2:M+maxLength,stroke:'#283752','stroke-width':Math.max(0.5,maxWidth/360)});for(let n=0;n<=maxLength;n+=step)element('line',{x1:M,y1:M+n,x2:M+maxWidth,y2:M+n,stroke:'#283752','stroke-width':Math.max(0.5,maxWidth/360)});const x=M+(maxWidth-width)/2,y=M+(maxLength-length)/2;element('rect',{x,y,width,height:length,fill:color,'fill-opacity':'.18',stroke:color,'stroke-width':Math.max(1.5,maxWidth/190)});element('line',{x1:x,y1:y+length/2,x2:x+width,y2:y+length/2,stroke:color,'stroke-opacity':'.5','stroke-width':Math.max(0.8,maxWidth/320)});element('line',{x1:x+width/2,y1:y,x2:x+width/2,y2:y+length,stroke:color,'stroke-opacity':'.5','stroke-width':Math.max(0.8,maxWidth/320)});svg.setAttribute('aria-label',`${width}×${length} 方块外包占地俯视图`)}
function select(id){current=byId[id];const x=current,maxW=Math.max(x.old[0],x.size[0]),maxL=Math.max(x.old[1],x.size[1]);document.getElementById('selected').textContent=`${x.id} · ${x.name}`;document.getElementById('chips').replaceChildren(...[`${x.old[0]}×${x.old[1]} → ${x.size[0]}×${x.size[1]}`,`高度 ${x.old[2]} → ${x.size[2]}`,`面积 ${label(x.oldArea)} → ${label(x.area)} 格²`,`${(x.area/x.oldArea).toFixed(1)} 倍`,x.grade].map(v=>el('span',{class:'chip'},v)));draw(document.getElementById('oldMap'),x.old[0],x.old[1],maxW,maxL,'#78889f');draw(document.getElementById('newMap'),x.size[0],x.size[1],maxW,maxL,colors[x.grade]);document.getElementById('detail').textContent=`占地理由：${x.note}`;document.getElementById('state').textContent=x.status;document.getElementById('scale').textContent=`同尺度：图宽一格 = ${maxW} 方块；图高一格 = ${maxL} 方块。网格间距随尺寸自动设置。`;for(const tr of document.querySelectorAll('#list tr'))tr.classList.toggle('selected',tr.dataset.id===id)}
function renderList(){const search=document.getElementById('search').value.trim().toLocaleLowerCase(),filter=document.getElementById('filter').value,family=document.getElementById('family').value,rows=machines.filter(x=>(filter==='all'||x.grade===filter)&&(family==='all'||x.id.startsWith(family))&&(x.id.toLocaleLowerCase().includes(search)||x.name.toLocaleLowerCase().includes(search)));const body=document.getElementById('list');body.replaceChildren();for(const x of rows){const tr=el('tr',{tabindex:'0','data-id':x.id});for(const text of [`${x.id} · ${x.name}`,`${x.old[0]}×${x.old[1]}`,`${x.size.join('×')}`,x.grade,`${(x.area/x.oldArea).toFixed(1)}×`])tr.append(el('td',{},text));tr.onclick=()=>select(x.id);tr.onkeydown=(event)=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select(x.id)}};body.append(tr)}document.getElementById('resultCount').textContent=`显示 ${rows.length} / 69 台；点击行看同比例俯视图`;select(current.id)}
function overview(){const host=document.getElementById('buckets');host.replaceChildren();for(const [prefix,title] of [['I','工业机器 I01–I45'],['S','五阶研究所 S01–S05'],['W','十五座文明奇观 W01–W15'],['H','休伯利安 H01']]){const subset=machines.filter(x=>x.id.startsWith(prefix)),max=Math.max(...subset.map(x=>Math.max(x.size[0],x.size[1])));const section=el('div',{class:'bucket'});section.append(el('strong',{},`${title} · 同组最大边 ${max} 格`));const grid=el('div',{style:'display:grid;grid-template-columns:repeat(auto-fill,minmax(84px,1fr));gap:7px'});for(const x of subset){const link=el('a',{href:'#selected',title:`${x.id} ${x.name} / ${x.size[0]}×${x.size[1]}`},`${x.id} · ${x.size[0]}×${x.size[1]}`);link.onclick=()=>select(x.id);const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');draw(svg,x.size[0],x.size[1],max,max,colors[x.grade]);const card=el('div');card.append(svg,link);grid.append(card)}section.append(grid);host.append(section)}}
const stats=document.getElementById('summary');stats.append(el('div',{},'69 座逐台新占地'));for(const grade of order){const node=el('div');node.append(el('b',{},machines.filter(x=>x.grade===grade).length.toString()),document.createTextNode(grade));stats.append(node)}for(const id of ['search','filter','family'])document.getElementById(id).addEventListener(id==='search'?'input':'change',renderList);renderList();overview();</script></html>'''
html=HTML.replace('__CSS__',CSS).replace('__DATA__',DATA).replace('__STAMP__',NOW)
OUTPUT.write_text(html,encoding='utf-8')
print('atlas', OUTPUT)
print('distribution',dict(counts))
print('old mismatches',sum(row['old']!=row['size'] for row in rows))
print('wonders',[(row['id'],row['size']) for row in rows if row['id'].startswith('W')])

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
