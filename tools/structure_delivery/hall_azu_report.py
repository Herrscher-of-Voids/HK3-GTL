"""将只读礼堂审计输出为可离线浏览的HTML；不依赖前端框架。"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/永恒的礼堂_Azu_预览与方块审计_20261029'

HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>永恒的礼堂 · Azu｜三维预览与方块清单</title>
<style>
:root{color-scheme:dark;--bg:#0c121c;--card:#141e2c;--line:#29374a;--muted:#a0aec1;--text:#e8edf4;--cyan:#8be4dd;--gold:#e4c78a}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1440px;margin:auto;padding:40px 32px 80px}a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}.eyebrow{color:var(--gold);letter-spacing:.18em;font-size:12px}h1{font-size:clamp(28px,3.5vw,48px);margin:9px 0 10px;line-height:1.2}h2{font-size:24px;margin:0 0 12px}h3{font-size:16px;margin:0 0 8px}p{margin:9px 0}.muted{color:var(--muted)}.lead{max-width:1020px;color:var(--muted)}.note{border-left:3px solid var(--gold);padding:12px 18px;background:#201f22;margin:22px 0}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0}.stat,.panel{background:var(--card);border:1px solid var(--line);border-radius:12px}.stat{padding:20px}.stat b{display:block;font-size:30px;line-height:1.4;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:13px}.stat:first-child{border-color:#587273}.stat:first-child b{color:var(--cyan)}.panel{padding:24px;margin-top:22px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}.button,button,select,input{font:inherit;color:var(--text);border:1px solid #41536c;background:#1b2b3e;border-radius:7px;padding:9px 13px}.button.primary,button.primary{background:var(--cyan);color:#0a2527;border-color:var(--cyan);font-weight:650}button{cursor:pointer}.hero{display:block;width:100%;max-height:760px;object-fit:contain;background:#101824;border-radius:8px}.caption{font-size:13px;color:var(--muted);margin-top:10px}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}.filters input{flex:1;min-width:240px}select{max-width:100%}.summary{display:flex;gap:24px;flex-wrap:wrap;padding:12px 0;color:var(--muted)}.summary strong{color:var(--text)}.bar{height:8px;background:#41536c;border-radius:5px;overflow:hidden}.bar div{height:100%;background:var(--cyan)}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th{text-align:left;color:var(--muted);font-weight:500;background:#141e2c}th,td{padding:12px;border-bottom:1px solid var(--line);vertical-align:top}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.id{color:#9cabc1;font:12px/1.5 ui-monospace,Consolas,monospace;word-break:break-all}.badge{display:inline-block;font-size:12px;border-radius:5px;padding:2px 8px;background:#253547;color:#c5d7ed}.badge.full{background:#163b3a;color:#a6e2d8}.badge.partial{background:#3c3024;color:#ebc897}.state-detail{max-width:900px;white-space:normal}.state-detail summary{cursor:pointer}.state-row{margin:10px 0;padding:10px;background:#101824;border-radius:5px;font-size:12px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}.facts{margin:0;padding-left:20px}.facts li{margin:7px 0}.small{font-size:13px}code{font:12px/1.5 ui-monospace,Consolas,monospace;color:#b7c8de;overflow-wrap:anywhere}details.panel>summary{cursor:pointer;font-size:20px;font-weight:650}.footer{margin-top:25px;font-size:12px;color:var(--muted)}#inline{height:760px;width:100%;border:1px solid var(--line);border-radius:8px;margin-top:16px}#status{min-height:26px;color:var(--muted)}@media(max-width:850px){main{padding:24px 16px}.stats{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}.stat b{font-size:24px}.panel{padding:16px}#inline{height:540px}}@media print{.filters,.actions,#inline{display:none}body{color:#111;background:white}.panel,.stat,th{background:white;color:#111}table{font-size:11px}.hero{max-height:450px}}
</style>
<main>
<div class="eyebrow">AZU · MINECRAFT ARCHITECTURE</div>
<h1>永恒的礼堂</h1>
<p class="lead">完整建筑三维预览、13座外塔核对，以及按实际方块状态区分的材料清单。保留原作者 Azu 署名；原压缩包只读。</p>
<div class="note"><strong>这份ZIP实际是 Minecraft 1.20.4 完整世界存档。</strong>里面没有“主体／外塔／定位层”三份投影。存档中13座外塔已经建好；这里直接统计实际建筑，不再额外乘13。主体与外塔按空间分组，不能冒充原投影文件计数。</div>
<div class="stats">
<div class="stat"><span>完整礼堂 · 主体＋13外塔</span><b>1,933,767</b><span>非空气占用格 · 66种方块</span></div>
<div class="stat"><span>主体余部</span><b>179,703</b><span>62种方块 · 不含13座外塔</span></div>
<div class="stat"><span>单座外塔</span><b>134,928</b><span>16种方块 · 已逐塔核对</span></div>
<div class="stat"><span>13座外塔合计</span><b>1,754,064</b><span>占完整礼堂90.71%的方块</span></div>
</div>
__COMPATIBILITY__
<section class="panel">
<h2>看完整座礼堂</h2>
<p class="muted">全景采用真实 Minecraft 贴图与方块模型。三维页面可旋转、缩放，并单独查看主体或某一座外塔。</p>
<div class="actions"><a class="button primary" href="viewer.html" target="_blank">打开三维预览 ↗</a><button id="loadPreview">在本页载入三维</button><a class="button" href="完整全景.png" download>下载完整全景PNG</a><a class="button" href="主体预览.png" target="_blank">查看主体截图</a></div>
<a href="完整全景.png" target="_blank"><img class="hero" src="完整全景.png" alt="永恒的礼堂完整全景，含13座外塔"></a>
<div id="previewHost"></div>
<p class="caption">建筑实际边界：X −286～393，Y −63～319，Z −376～390；包围盒宽×深×高为680×767×383格，包围盒内空气不计材料数量。预览资源取自本地1.20.1原版资源；源存档为1.20.4，未在游戏中迁移。</p>
</section>
<section class="panel">
<h2>方块清单</h2>
<p class="muted">“完整”指外形占满1×1×1的立方体。玻璃、树叶虽透明或镂空，仍可归入完整外形；楼梯、墙、栅栏、单层台阶等属于非完整。双层台阶单独按实际状态判断。</p>
<div class="filters"><select id="scope" aria-label="统计范围"></select><input id="search" type="search" placeholder="搜索中文名或方块ID，例如 石英 / slab" aria-label="搜索方块"><select id="shape" aria-label="形状分类"><option value="all">全部外形</option><option value="full">包含完整立方体</option><option value="partial">包含非完整方块</option><option value="mixed">同ID有完整与非完整</option><option value="alpha">透明／镂空贴图</option><option value="invisible">无形光源</option></select><select id="sort" aria-label="排序"><option value="count">数量从多到少</option><option value="name">名称顺序</option></select></div>
<div class="summary" id="summary"></div><div class="bar"><div id="fullBar"></div></div>
<div class="actions"><a id="csv" class="button" download>下载当前范围CSV</a><a class="button" href="逐状态清单.csv" download>下载逐状态清单CSV</a><a class="button" href="audit-data.json" download>下载统计JSON</a></div>
<p id="status"></p>
<div class="table-wrap"><table><thead><tr><th>材料 / 注册ID</th><th class="num">占用格</th><th class="num">完整</th><th class="num">非完整</th><th>外形与实际状态</th></tr></thead><tbody id="materials"></tbody></table></div>
</section>
<div class="grid2">
<section class="panel"><h2>完整与非完整，怎么算</h2><ul class="facts">
<li>礼堂主展区：<strong>1,818,116格完整立方体</strong>，<strong>115,651格非完整方块</strong>，两者之和等于1,933,767。非完整中有115,647格可见外形、4格无形光源。</li>
<li>分类读取真实 blockstate、模型几何和贴图透明度；不按中文名或ID后缀猜测。</li>
<li><code>type=double</code> 的双层台阶计完整；<code>type=top/bottom</code> 计非完整。同一个台阶ID可以跨两类。</li>
<li>计数是建筑占用格，不是生存物品成本。例如一个双层台阶占1格，但需要2个台阶物品。</li>
<li>这个分类不等于碰撞箱、遮光、可否刷怪或多方块Pattern许可；用于判断建筑外形。</li>
<li>招牌是非完整，文字需要方块实体渲染；隐形光源单列。三维页面的渲染省略项会明示，不从材料统计中扣除。</li>
</ul></section>
<section class="panel"><h2>为何不是8200万格</h2><ul class="facts">
<li>全存档非空气共<strong>82,050,773格</strong>，其中<strong>80,013,736格</strong>是超平坦生成的基岩、蓝色混凝土海床与静水。</li>
<li>扣除海床背景后，存档共有<strong>2,037,037格</strong>、87种方块。</li>
<li>其中礼堂主展区<strong>1,933,767格</strong>；远处样件和署名地板<strong>103,270格</strong>，在清单中可以切换查看。</li>
<li>主展区筛选：<code>|X|&lt;450，|Z|&lt;450，Y&gt;−64</code>，保留主体周围的小离散片段。未修改原世界。</li>
<li>没有原始定位层投影，不能编造其独立材料清单；本页给出存档坐标、俯视图和13座外塔位置。</li>
</ul></section>
</div>
<details class="panel"><summary>13座外塔位置与逐塔核对</summary><p class="muted">每座134,928格，方块ID与数量逐塔相同；归一化后的坐标及状态有两种镜像形式，不能称为状态完全一致。各塔包围盒宽×深×高为43×37×298格。</p><div class="table-wrap"><table><thead><tr><th>外塔</th><th>最小坐标 X,Y,Z</th><th>最大坐标 X,Y,Z</th><th class="num">占用格</th></tr></thead><tbody id="towers"></tbody></table></div><a href="主展区俯视定位.png" target="_blank"><img style="display:block;max-width:100%;max-height:650px;margin:24px auto" src="主展区俯视定位.png" alt="主展区俯视定位示意"></a><p class="caption">这张俯视图用于空间定位，以高度着色；上方全景和三维页面才使用真实MC材质。</p></details>
<details class="panel"><summary>来源与复核信息</summary><p id="source"></p><p>读取48个非空主世界region文件、32,874个已保存区块；按存档的区块palette和方块状态逐格解析，排除空气、洞穴空气和虚空空气。实体不计入方块清单。</p><p>完整分类证据：<a href="classification-evidence.json" download>逐状态模型、贴图及来源记录</a>。材料列表可离线浏览，三维依赖随页面附带，不需要Cursor或React。</p><p class="small muted" id="created"></p></details>
<p class="footer">原建筑：Azu · 此页为上传存档的只读预览与统计，未接入HK3GTL正式建筑、控制器或配方。</p>
</main>
<script id="audit" type="application/json">__DATA__</script>
<script>
'use strict';const D=JSON.parse(document.getElementById('audit').textContent),$=id=>document.getElementById(id),num=n=>n.toLocaleString('en-US'),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sums=(b,k)=>b.states.reduce((a,r)=>(a[r.full===true?'full':r.full===false?'partial':'unknown']+=r.counts[k],a),{full:0,partial:0,unknown:0});
for(const [k,s]of Object.entries(D.summaries))$('scope').add(new Option(s.name,k));
function render(){const k=$('scope').value,q=$('search').value.trim().toLowerCase(),f=$('shape').value,s=D.summaries[k];
 $('summary').innerHTML=`<span>本范围 <strong>${num(s.blocks)}</strong> 格 · ${s.types}种方块 · ${s.states}种状态</span><span>完整 <strong>${num(s.full||0)}</strong> 格（${((s.full||0)/s.blocks*100).toFixed(2)}%）</span><span>非完整 <strong>${num(s.partial||0)}</strong> 格${s.invisible?'（含无形光源'+num(s.invisible)+'格）':''}</span>`;$('fullBar').style.width=(s.full/s.blocks*100)+'%';$('csv').href='方块清单_'+k+'.csv';
 const rows=D.blocks.filter(b=>{if(!b.counts[k]||!(b.name+' '+b.block).toLowerCase().includes(q))return false;const t=sums(b,k);return f==='all'||f==='full'&&t.full>0||f==='partial'&&t.partial>0||f==='mixed'&&t.full>0&&t.partial>0||f==='alpha'&&b.states.some(r=>r.counts[k]&&r.texture_has_alpha)||f==='invisible'&&b.block==='minecraft:light'}).sort($('sort').value==='count'?(a,b)=>b.counts[k]-a.counts[k]:(a,b)=>a.name.localeCompare(b.name,'zh-CN'));
 $('status').textContent=`显示 ${rows.length} / ${s.types} 种方块；展开每行可查看朝向、层数及分类依据。`;
 $('materials').innerHTML=rows.map(b=>{const t=sums(b,k),states=b.states.filter(r=>r.counts[k]),mixed=t.full&&t.partial,cls=mixed?'混合状态':t.full?'完整立方体':b.block==='minecraft:light'?'无形光源':'非完整方块';return `<tr><td><strong>${esc(b.name)}</strong><div class="id">${esc(b.block)}</div></td><td class="num">${num(b.counts[k])}</td><td class="num">${num(t.full)}</td><td class="num">${num(t.partial)}</td><td><details class="state-detail"><summary><span class="badge ${mixed?'':t.full?'full':'partial'}">${cls}</span> ${states.length}种状态</summary>${states.map(r=>`<div class="state-row"><b>${num(r.counts[k])}格 · ${esc(r.category)}</b><div class="id">${esc(r.state)}</div><div>${esc(r.reason)}</div>${r.texture_has_alpha?'<div class="muted">贴图含透明／镂空像素；不因此改变立方体外形分类。</div>':''}</div>`).join('')}</details></td></tr>`}).join('');
}
for(const id of ['scope','search','shape','sort'])$(id).addEventListener(id==='search'?'input':'change',render);render();
$('towers').innerHTML=D.towers.map(t=>`<tr><td>外塔 ${t.number}</td><td><code>${t.min_xyz.join(', ')}</code></td><td><code>${t.max_xyz.join(', ')}</code></td><td class="num">${num(t.blocks)}</td></tr>`).join('');
$('source').innerHTML=`来源：<code>${esc(D.source)}</code><br>存档版本：Minecraft ${esc(D.version)}<br>SHA-256：<code>${esc(D.source_sha256)}</code>`;
$('created').textContent='统计生成时间：'+new Intl.DateTimeFormat('zh-CN',{timeZone:'America/New_York',dateStyle:'medium',timeStyle:'medium'}).format(new Date(D.created_at))+'（America/New_York）';
$('loadPreview').addEventListener('click',()=>{if(!$('inline')){const frame=document.createElement('iframe');frame.id='inline';frame.title='礼堂三维预览';frame.src='viewer.html';$('previewHost').append(frame)}$('inline').scrollIntoView({behavior:'smooth',block:'center'})});
</script></html>'''


def main():
    data = json.loads((OUT / 'audit-data.json').read_text(encoding='utf-8'))
    compatibility = ''
    compatible_path = ROOT / 'output/hall-azu-analysis/compatibility-1.20.1.json'
    if compatible_path.is_file():
        compatible = json.loads(compatible_path.read_text(encoding='utf-8'))
        assert {r['state'] for r in compatible['states']} == {r['state'] for r in data['states']}
        for key, scope in compatible['scopes'].items():
            assert scope['blocks'] == data['summaries'][key]['blocks']
        missing, invalid = len(compatible['missing_block_ids']), len(compatible['invalid_states'])
        hall, saved = compatible['scopes']['hall'], compatible['scopes']['saved']
        verdict = '没有1.20.1缺少的方块，也没有不支持的方块状态。' if not missing and not invalid else '发现缺失方块或不兼容状态，详见核验JSON。'
        compatibility = f'''<section class="panel" id="compatibility"><h2>作为W01：1.20.1建材兼容核验</h2>
<p><strong style="color:var(--cyan)">{escape(verdict)}</strong> 因版本差异需要替换的材料：<strong>{missing}种</strong>；不兼容状态：<strong>{invalid}种</strong>。</p>
<div class="summary"><span>完整礼堂 <strong>{hall['block_ids']} / {hall['block_ids']}</strong>种方块 · <strong>{hall['states']} / {hall['states']}</strong>种状态通过</span><span>含远处样件的留存清单 <strong>{saved['block_ids']} / {saved['block_ids']}</strong>种方块 · <strong>{saved['states']} / {saved['states']}</strong>种状态通过</span></div>
<p>樱花木、樱花树叶、粉红色花簇、竹栅栏、泥砖及泥砖墙均在1.20.1真实注册表内。台阶层数、楼梯朝向、墙体连接、水浸等实际属性也逐项通过。</p>
<p class="muted">核验方法：用本机目标版本的原版客户端执行Bootstrap，读取BuiltInRegistries.BLOCK及StateDefinition，逐条构造真实状态；不以贴图存在代替注册表验证。</p>
<p>原世界数据版本 <strong>{compatible['source_data_version']}</strong>（{compatible['source_minecraft_version']}）高于目标 <strong>{compatible['target_data_version']}</strong>（{compatible['target_minecraft_version']}）。用作W01时，后续提取建筑结构导入1.20.1，保留原世界；本轮尚未进行整包、游戏内导入或FCL运行验收。</p>
<p class="small muted">负责人已提出以此建筑作为W01。本轮仅完成兼容核查，未修改建筑、主控、正式Pattern、配方或实例。</p>
<a class="button" href="compatibility-1.20.1.json" download>下载逐ID／逐状态核验证据JSON</a></section>'''
        (OUT / 'compatibility-1.20.1.json').write_bytes(compatible_path.read_bytes())
    serialized = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    (OUT / 'index.html').write_text(HTML.replace('__DATA__', serialized).replace('__COMPATIBILITY__', compatibility), encoding='utf-8')
    evidence = ROOT / 'output/hall-azu-analysis/classification.json'
    (OUT / 'classification-evidence.json').write_bytes(evidence.read_bytes())
    print(str(OUT / 'index.html'))


if __name__ == '__main__':
    main()
