"""AE 审计离线网页导出：从已完成快照生成单文件 HTML，不重新扫描或修改实例。
变更记录 #1：2026-09-28，补充无需 Canvas 运行环境的交付入口；保留历史产物。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/ae-mixin-audit-20260928'
data = json.loads((OUT / 'report.json').read_text(encoding='utf-8'))
sources = {}
for pack in data['packs'].values():
    for item in pack['inventory']:
        item.pop('manifest', None)
    for record in pack['records']:
        path = record['source']
        if path not in sources:
            sources[path] = Path(path).read_text(encoding='utf-8')
data['sources'] = sources
payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
page = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GTL · AE Mixin 审计</title>
<style>
:root{color-scheme:light dark;--bg:#f4f6f8;--fg:#17222d;--muted:#52616e;--panel:#fff;--line:#d6dfe5;--accent:#17657e}
@media(prefers-color-scheme:dark){:root{--bg:#11181e;--fg:#e4eaf0;--muted:#a4b3be;--panel:#19232b;--line:#35434e;--accent:#80ccdf}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1180px;margin:auto;padding:32px 24px 70px}h1{font-size:28px;margin:0 0 8px}h2{font-size:21px;margin:32px 0 14px}h3{font-size:16px;margin:0 0 5px}p{margin:8px 0}small,.muted{color:var(--muted)}.notice{border-left:4px solid var(--accent);padding:12px 18px;background:var(--panel);margin:18px 0}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}.stat{padding:18px;background:var(--panel)}.stat b{display:block;font-size:30px;color:var(--accent)}label{display:block;font-size:13px;color:var(--muted)}input,select,button{font:inherit;border:1px solid var(--line);border-radius:5px;background:var(--panel);color:var(--fg);padding:8px 12px}button{cursor:pointer}button:disabled{opacity:.4;cursor:default}input{width:100%}.controls{display:grid;grid-template-columns:2fr 1fr;gap:14px;margin:16px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:var(--panel);font-size:13px}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{white-space:nowrap}td:first-child{overflow-wrap:anywhere}details{border-bottom:1px solid var(--line);padding:12px 0}summary{cursor:pointer;overflow-wrap:anywhere}.detail{padding:12px 8px}.detail p{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 Consolas,monospace;background:var(--panel);padding:14px;border:1px solid var(--line);max-height:650px;overflow:auto}.finding{margin:18px 0}.pagination{display:flex;gap:12px;align-items:center;margin:14px 0}.badge{font-size:12px;color:var(--muted)}a{color:var(--accent)}@media(max-width:650px){main{padding:20px 14px}.stats,.controls{grid-template-columns:1fr}h1{font-size:24px}.stat{padding:10px 15px}.stat b{font-size:25px}}
</style>
<main><h1>GTL 两套底包 · AE Mixin 审计</h1><p id="date" class="muted"></p>
<div class="notice">本页是离线静态快照，包含全部审计数据和反编译证据，不访问网络。数量表示声明，不表示运行时全部成功注入；没有执行新的游戏或性能测试。</div>
<label for="pack">选择底包</label><select id="pack"><option value="original">原实例 GregTech-Leisure-1.4.5.2</option><option value="enhanced">增强版 2.1</option></select>
<div id="stats" class="stats"></div><p id="coverage" class="muted"></p>
<h2>结果与影响</h2><div id="findings"></div>
<h2>各模组修改汇总</h2><p class="muted">行为方法按注入／覆写方法声明计数；访问器另列。一个类或方法可以关联多个目标，不等于独立功能数量。</p><div id="modules"></div>
<h2>逐类清单与代码证据</h2><div class="controls"><div><label for="query">搜索模组、类、目标方法、注解</label><input id="query" type="search" placeholder="例如：CraftingCpuLogic、GTLCore、pushPattern"></div><div><label for="scope">修改范围</label><select id="scope"><option>全部</option><option>AE2直接目标</option><option>附属与ME桥接目标</option><option>间接关联</option></select></div></div>
<p id="count" class="muted"></p><div class="pagination"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></div><div id="records"></div>
<h2>扫描文件与边界</h2><p>未命中 AE 关联 Mixin 的模组仍可能通过事件、普通 API 或通用性能补丁影响 AE。AE2 自身注入游戏的相关类单独列出，不计入外部修改数。</p><details><summary>全部顶层 JAR 与 SHA256</summary><div id="inventory"></div></details><details><summary>另列：AE2 自身关联 Mixin</summary><div id="native"></div></details>
<p class="muted">逐类提取全部注解，重点深读规划、派发、存储、兼容插件与历史失败；未逐行验证每个辅助算法。反编译文本用于证据阅读，不作为可直接编译的原始源码。</p></main>
<script id="audit-data" type="application/json">__DATA__</script>
<script>
'use strict';
const audit=JSON.parse(document.getElementById('audit-data').textContent);
const el=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const PACKS=['original','enhanced'];let currentPage=0;const size=30;
const searchIndex=Object.fromEntries(PACKS.map(k=>[k,audit.packs[k].records.map(r=>JSON.stringify(r).toLowerCase())]));
function selected(){return audit.packs[el('pack').value]}
function renderRecords(){
 const p=selected(),q=el('query').value.trim().toLowerCase(),scope=el('scope').value;
 const filtered=p.records.filter((r,i)=>(scope==='全部'||r.scope===scope)&&searchIndex[el('pack').value][i].includes(q));
 const pages=Math.max(1,Math.ceil(filtered.length/size));currentPage=Math.min(currentPage,pages-1);
 el('count').textContent=`筛选出 ${filtered.length} 类；每页最多显示 ${size} 类，展开时才生成注入详情与代码。`;
 el('page').textContent=`${currentPage+1} / ${pages}`;el('prev').disabled=currentPage===0;el('next').disabled=currentPage>=pages-1;
 el('records').replaceChildren();
 for(const r of filtered.slice(currentPage*size,(currentPage+1)*size)){
  const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent=`${r.module} · ${r.class.split('.').pop()} · ${r.hooks.length} 个行为方法`;details.append(summary);
  let ready=false;details.addEventListener('toggle',()=>{if(!details.open||ready)return;ready=true;
   const body=document.createElement('div');body.className='detail';
   body.innerHTML=`<p><strong>${esc(r.class)}</strong></p><p>来源：${esc(r.jar)}</p><p>目标：${esc(r.targets.join('；'))}</p><p>${esc(r.state)} · ${esc(r.scope)}</p>`;
   if(r.missing_targets.length)body.innerHTML+=`<p>mods 扫描范围内未找到：${esc(r.missing_targets.join('；'))}。游戏自身类不在此范围；可选模组目标应结合加载插件判断。</p>`;
   for(const h of r.hooks){const title=document.createElement('h3');title.textContent=h.type+' · '+h.handler;const pre=document.createElement('pre');pre.textContent=JSON.stringify(h.annotation,null,2);body.append(title,pre)}
   if(r.access.length){const t=document.createElement('p');t.textContent='访问桥：'+r.access.map(x=>x.type+' '+x.method).join('；');body.append(t)}
   const config=document.createElement('p');config.className='muted';config.textContent='配置：'+r.config.map(c=>c.config+' / '+c.side+(c.plugin?' / '+c.plugin:'')).join('；');body.append(config);
   const source=document.createElement('details');source.innerHTML='<summary>在本页阅读反编译证据</summary>';let loaded=false;
   source.addEventListener('toggle',()=>{if(!source.open||loaded)return;loaded=true;const pre=document.createElement('pre');pre.textContent=audit.sources[r.source];source.append(pre)});body.append(source);details.append(body);
  });el('records').append(details);
 }
 if(!filtered.length)el('records').textContent='没有匹配项，请缩短关键词或切换范围。';
}
function renderPack(){
 const p=selected(),s=p.summary;currentPage=0;
 el('stats').innerHTML=[[s.declared_classes,'外部 AE 关联 Mixin 声明类'],[s.direct_ae2,'其中：直接修改 AE2 的类'],[s.behavior_handlers,'行为注入／覆写方法声明']].map(([n,t])=>`<div class="stat"><b>${n}</b>${t}</div>`).join('');
 el('coverage').textContent=`${s.modules} 个来源模组，${s.access_handlers} 个访问方法另计，${s.unique_ae2_targets} 个不同 AE2 目标类。扫描 ${s.top_jars} 个顶层与 ${s.nested_jars} 个嵌套 JAR，解析错误 ${s.parse_errors}。已核对插件条件跳过 ${s.known_plugin_skips} 类；增强版另有仅打包未声明的类。`;
 el('modules').innerHTML='<div class="scroll"><table><thead><tr><th>实际 JAR</th><th>声明类</th><th>直接 AE2</th><th>行为方法</th><th>访问方法</th></tr></thead><tbody>'+p.modules.map(m=>`<tr><td>${esc(m.jar)}</td><td>${m.declared}</td><td>${m.direct}</td><td>${m.hooks}</td><td>${m.access}</td></tr>`).join('')+'</tbody></table></div>'+p.modules.map(m=>`<details><summary><strong>${esc(m.name)}</strong> · ${esc(m.title)}</summary><div class="detail"><p>${esc(m.effect)}</p><p>${esc(m.result)}</p><small>SHA256：${esc(m.sha256)}</small></div></details>`).join('');
 el('inventory').innerHTML=p.inventory.filter(j=>!j.jar.includes('!/')).map(j=>`<p>${esc(j.jar)}<br><small>${esc(j.sha256)}</small></p>`).join('');
 el('native').innerHTML=p.native_ae_mixins.map(c=>`<p>${esc(c)}</p>`).join('');renderRecords();
}
el('date').textContent='审计快照：'+audit.generated_at+' · 离线 HTML 交付版';
el('findings').innerHTML=audit.findings.map(f=>`<section class="finding"><h3>${esc(f[0])}</h3><p>${esc(f[1])}</p></section>`).join('');
el('pack').addEventListener('change',renderPack);el('scope').addEventListener('change',()=>{currentPage=0;renderRecords()});
let timer;el('query').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{currentPage=0;renderRecords()},120)});
el('prev').addEventListener('click',()=>{--currentPage;renderRecords()});el('next').addEventListener('click',()=>{++currentPage;renderRecords()});renderPack();
</script></html>'''.replace('__DATA__', payload)
target=OUT/'AE-Mixin审计报告.html'
target.write_text(page,encoding='utf-8')
(OUT/'offline-page-script.js').write_text(page.rsplit('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
print(json.dumps({'html':str(target),'bytes':target.stat().st_size,'embedded_sources':len(sources)},ensure_ascii=False))
