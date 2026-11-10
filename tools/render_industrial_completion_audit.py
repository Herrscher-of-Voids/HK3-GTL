"""2026-09-29：生成只读系统审计报告、Canvas与讨论记录，不修改游戏业务。"""
from pathlib import Path
from datetime import datetime
from collections import Counter
import json,html,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/beta5-completion-audit-20260929'
DOC=ROOT/'doc/HK3GTL-内测5'
REPORT=DOC/'09_测试发布/内测5全系统完成度审计_20260929.html'
CANVAS=Path('C:/Users/OWNER/.cursor/projects/c-Users-OWNER-Desktop-progrem-complate-progrem-hk3gtl/canvases/HK3GTL-completion-audit.canvas.tsx')
NOW=datetime.fromisoformat(json.loads((OUT/'report-meta.json').read_text(encoding='utf-8'))['generated_at']) if (OUT/'report-meta.json').exists() else datetime.now().astimezone()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
inventory=load(OUT/'inventory.json');facts=load(OUT/'facts.json');docs=load(OUT/'documents.json')
manifest=load(OUT/'system-findings.json')
java=list((ROOT/'src/main/java').rglob('*.java'))
def resolve(spec):
    name,_,needle=spec.partition('|')
    if name.startswith('@'):
        matches=[d for d in docs if name[1:] in d['path'] and not d['historical']]
        assert matches,spec
        p=ROOT/min(matches,key=lambda x:len(x['path']))['path']
    elif '/' in name:p=ROOT/name
    else:
        matches=[p for p in java if p.name==name]
        assert len(matches)==1,(spec,matches)
        p=matches[0]
    assert p.is_file(),p
    line=1
    if needle:
        line=next((i for i,s in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1) if needle in s),None)
        assert line is not None,spec
    return {'path':p.relative_to(ROOT).as_posix(),'absolute':p.as_posix(),'line':line,'label':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rows=[]
for values in manifest['rows']:
    row=dict(zip(manifest['fields'],values))
    if row['id']=='N06':row['refs']=['Hk3ModWelcomeHandler.java|onPlayerLoggedIn','Hk3ModWelcomeScreen.java']+row['refs']
    if row['id']=='N03':row['refs'].append('Hk3SpectrumBootstrapRecipes.java|personal_phone')
    row['refs']=[resolve(r) for r in row['refs']];rows.append(row)
assert len(facts['production_evidence_topics'])==10
assert len(facts['no_production_evidence_found'])==90
assert len(facts['cost_point_mismatches'])==95
assert len(facts['custom_test_tasks'])==18
counts=dict(Counter(r['status'] for r in rows))
conclusion='有实际接通、并经过局部验证的内容，但内测5研究—工业—团队—奇观—终审主线尚未闭环，不能作为全系统完成或发布验收通过来汇报。'
priorities=[
 '先统一个人点数、团队证据/知识与任务生命周期，接通退款和离队规则，再扩展100课题生产证据与真实解锁映射。',
 '落地已批准R03—R06成本、公式、计算机离线规则与S02—S05。高阶结构标为待正式接入，不冒充已经批准。',
 '逐条接后续工业、世界泡/舰船和15奇观事实；保证研究前起步工艺可用，不用后台给证据掩盖阻断。',
 '完成一/二审、C0—C7与个人档案；终审入场复核和结局归属对齐批准规则，保留用户明确要求的改名与踢出。',
 '同一构建在两底包运行单人/多人/存读档/离线/低内存验收。贸易不恢复，AE专项优化不提前，结构外观讨论不擅自恢复。'
]
result={'generated_at':NOW.isoformat(),'baseline':'r99，2026-09-29，贸易已撤销','conclusion':conclusion,'scope':inventory,'facts':facts,'status_counts':counts,'systems':rows,'priorities':priorities,'limitation':'全量路径索引、文档文本提取和源码标记扫描，关键生产路径人工复核；不是逐行形式证明。未启动游戏，未修改业务代码。'}
(OUT/'system-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
def esc(s):return html.escape(str(s),quote=True)
def link(ref):return '<a href="'+esc(Path(ref['absolute']).as_uri())+'">'+esc(ref['label'])+'</a> <small>第'+str(ref['line'])+'行</small>'
def local(path,label):return '<a href="'+esc((ROOT/path).as_uri())+'">'+esc(label)+'</a>'
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内测5全系统完成度审计</title><style>
body{margin:0;background:#f5f6f7;color:#18212b;font:16px/1.75 system-ui,Microsoft YaHei,sans-serif}main{max-width:1120px;margin:auto;padding:32px 24px 70px}h1{font-size:28px;line-height:1.35}h2{font-size:21px;margin-top:30px}h3{font-size:18px;margin:5px 0}a{color:#145b91}small,.muted{color:#586672}p{margin:8px 0}.lead{font-size:19px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}.metric{padding:14px;border:1px solid #cbd2d8;background:white}.metric strong{display:block;font-size:25px}.callout{padding:14px 18px;background:#e8edf1;border-left:4px solid #526777}nav{display:flex;gap:12px;flex-wrap:wrap}input,select{font:inherit;padding:8px;border:1px solid #acb9c2;border-radius:3px;background:white;max-width:100%}.tools{display:flex;gap:10px;flex-wrap:wrap;position:sticky;top:0;padding:12px 0;background:#f5f6f7;z-index:2}article{padding:20px 0;border-top:1px solid #cbd2d8}article:target{background:#edf2f6}.tag{display:inline-block;border:1px solid #b8c2ca;padding:1px 7px;font-size:13px;margin:0 8px 5px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.refs{font-size:13px;overflow-wrap:anywhere}.refs a{margin-right:5px}details{margin:10px 0}li{margin:7px 0}.hidden{display:none}code{overflow-wrap:anywhere}@media(max-width:700px){.metrics{grid-template-columns:1fr 1fr}main{padding:20px 14px}.grid{grid-template-columns:1fr}}@media print{.tools{display:none}article{break-inside:avoid}body{background:white}main{max-width:none}.hidden{display:block!important}}
</style><main>''']
parts += ['<p class="muted">HK3GTL · 内测5 · 截至 '+esc(NOW.strftime('%Y-%m-%d %H:%M:%S %z'))+' · r99</p><h1>哪些已经接通，哪些仍未完成</h1><p class="lead">'+conclusion+'</p><p>核对当前源码、资源、两实例JAR、内测5文档与最新决定；区分候选预览、批准方案、入包正文和实际玩法。不使用虚假的总完成率。</p>',
 '<div class="metrics"><div class="metric"><strong>100 / 10</strong>课题目录 / 定位到真实产出写入的课题</div><div class="metric"><strong>5 / 1</strong>目标研究所阶数 / 正式注册阶数</div><div class="metric"><strong>69 / 6</strong>规划结构 / 正式结构资源，不是实机通过数</div><div class="metric"><strong>20 / 480</strong>访客形态文本 / 台词句数；访客池未实现</div></div>',
 '<div class="callout"><strong>最容易误判的三件事</strong><p>100课题数据齐 ≠ 100条证据与解锁链能走通。正文已入包 ≠ NPC或审查自然流程已完成。编译和复制成功 ≠ 双底包/FCL实机验收通过。</p></div>',
 '<h2>已有真实成果的具体切片</h2><ul><li>新16档显示名称/电压基础、52电路及标签一致性实现；制造全链另验。</li><li>I01→装罐→I02→RN-HED/RN-HSA付费研究曾有实例通过记录；仅此起步切片。</li><li>奥托首信/回复服务、手机安装/入口、更新阅读资源，以及26条IF逐句/5条额度/免费命令已有接线。</li><li>结构压缩、缓存、研究队列和世界泡账本等有自动检查；未接生产调用的组件不计完整玩法。</li></ul>',
 '<h2>批准与实现的明确差距</h2><p>研究点当前<strong>737,680</strong>，批准<strong>255,750</strong>，<strong>95个课题</strong>不同。旧公式仍是ERM+25% / W13+75%，批准为+50% / +150%；当前机器调用还把两项加速都设为false。</p><p>现行显示是<strong>HBV HCV HRV HDV / QSV QCV QEV QAV / IMV ICV IRV IWV / WFV WSV CIV CEV</strong>。旧注册键不是旧四档正式命名仍有效的证明。</p>',
 '<nav><a href="#systems">逐系统清单</a><a href="#verification">真实验收</a><a href="#documents">文档冲突</a><a href="#coverage">覆盖范围</a><a href="#next">建议顺序</a></nav>',
 '<h2 id="systems">逐系统清单 · '+str(len(rows))+'个审计单元</h2><p>按职责拆分，单元数量不代表功能权重或完成百分比。“已接通”仍待当前版本实机回归；“待实现”指新版批准业务，可能有旧组件可复用。</p><div class="tools"><input id="search" type="search" aria-label="搜索" placeholder="搜索系统、ID或缺口"><select id="status" aria-label="状态"><option value="">全部状态</option>'+''.join('<option>'+esc(s)+'</option>' for s in counts)+'</select><select id="priority" aria-label="优先级"><option value="">全部优先级</option><option>P0</option><option>P1</option><option>P2</option><option>不排期</option></select><span id="count"></span></div>']
for r in rows:
    parts += ['<article id="'+r['id']+'" data-status="'+esc(r['status'])+'" data-priority="'+r['priority']+'"><div><span class="tag">'+esc(r['status'])+'</span><span class="tag">'+r['priority']+'</span><small>'+esc(r['group'])+'</small></div><h3>'+r['id']+' · '+esc(r['title'])+'</h3><div class="grid"><div><strong>已经做到</strong><p>'+esc(r['implemented'])+'</p></div><div><strong>还差什么 / 限制</strong><p>'+esc(r['gaps'])+'</p></div></div><p><strong>验证等级：</strong>'+esc(r['validation'])+'</p><details class="refs"><summary>源码与设计证据（含定位行）</summary>'+''.join('<p>'+link(ref)+'<br><span class="muted">'+esc(ref['path'])+'</span></p>' for ref in r['refs'])+'</details></article>']
parts += ['<h2 id="verification">哪些真的运行过</h2><ul><li>2026-09-24 01:33:14实例：I01→装罐→I02→两课题付费研究，含负面路径和恢复。'+local('logs/research64/instance-results.log','原始日志')+'</li><li>历史I01/I02八方向56项成型/破坏/恢复检查。'+local('logs/structure63/instance-formation-results.log','原始日志')+'</li><li>r66的45配方/8研究静态审计明确以前置MAX外部资源为条件，并非生存实机全程验收。</li><li>r99 build成功，18项自定义检查。世界泡测试明确未测game/inventory delivery，个人攻击账本测试也没有让主流程的世界计数自动消失。'+local('logs/trade-removal-r99/final-build.log','构建日志')+'</li><li>本轮两实例SHA-256相同：<code>'+facts['installed_current_hashes']['base'][0]['sha256']+'</code>。只证部署一致，不证启动/通关。</li><li>本轮1306个运行资源JSON全可解析，不能证明配方逻辑或运行可达性。</li></ul>',
 '<h2 id="documents">现行文档入口仍有版本冲突</h2><ul><li>9月22日总目录仍提77座（69+8）和贸易；后来批准69座及8项工艺合并，9月29日又撤销贸易。</li><li>旧工业总览仍有旧分组/电路口径，当前代码显示已是16新名称和52电路；必须按后续批准判定。</li><li>R03—R06已批准，成本与数学实现却未更新。“确认”是设计状态，不是代码状态。</li><li>r93正文已入包，不能沿用此前“未入包”结论；也不能将正文入包扩大成NPC和团队审查完成。</li><li>早期研究失败记录已被9月24日起步切片通过部分取代，不得将历史失败当成当前全无成果。</li></ul><p>本轮保留原文与讨论历史，仅在此列出冲突；不擅自修改批准方案。</p>',
 '<h2 id="coverage">覆盖范围与方法</h2><p>原始索引时间：'+esc(inventory['time'])+'。内测5目录12,202文件；641份HTML/MD/TXT全文提取，其中历史目录153、非历史488。336份主Java与20份测试Java，共62,773行完成索引及标记扫描，关键生产路径另人工追踪。非历史文档仍含候选和预览，不等于488份独立现行需求。</p><p>其余大量JSON/CLASS/NBT/图片是归档、预览与资产；本轮没有对全部12,202文件逐个语义证明，也没有重新反编译历史第三方CLASS。当前运行JSON全量解析，仓库KubeJS仅1份脚本已读。没有用TODO数量或文件数推算完成率。</p><p>“未找到接线”限定为当前源码审计范围。没有启动游戏、没有FCL测试、没有更改业务代码或恢复贸易。引用保留文件哈希，源码链接旁有定位行；浏览器打开源码时按该行核对。</p><p>'+local('logs/beta5-completion-audit-20260929/system-audit.json','系统证据及哈希JSON')+' · '+local('logs/beta5-completion-audit-20260929/inventory.json','覆盖统计')+' · '+local('logs/beta5-completion-audit-20260929/source-index.json','源码索引')+' · '+local('logs/beta5-completion-audit-20260929/documents.json','文档全文索引')+' · '+local('logs/beta5-completion-audit-20260929/facts.json','本轮核算事实')+'</p>',
 '<h2 id="next">建议顺序（本轮只审计，不自动开工）</h2><ol>'+''.join('<li>'+esc(p)+'</li>' for p in priorities)+'</ol></main><script>const cards=Array.from(document.querySelectorAll("article"));function filter(){const q=document.getElementById("search").value.toLowerCase();const s=document.getElementById("status").value;const p=document.getElementById("priority").value;let n=0;cards.forEach(c=>{const ok=(!q||c.textContent.toLowerCase().includes(q))&&(!s||c.dataset.status===s)&&(!p||c.dataset.priority===p);c.classList.toggle("hidden",!ok);if(ok)n++});document.getElementById("count").textContent=n+" / "+cards.length}for(const id of ["search","status","priority"])document.getElementById(id).addEventListener("input",filter);filter();</script></html>']
REPORT.write_text(''.join(parts),encoding='utf-8')
canvasdata={'time':NOW.strftime('%Y-%m-%d %H:%M:%S %z'),'report':REPORT.as_posix(),'conclusion':conclusion,'rows':rows,'priorities':priorities,'coverage':inventory,'statuses':list(counts)}
canvas='''import {Stack,Row,H1,H2,Text,Select,TextInput,Button,Divider,useCanvasState,useCanvasAction,useHostTheme} from "cursor/canvas";
const data=__DATA__;
export default function CompletionAudit(){
 const theme=useHostTheme(); const dispatch=useCanvasAction();
 const [query,setQuery]=useCanvasState("query",""); const [status,setStatus]=useCanvasState("status","all"); const [priority,setPriority]=useCanvasState("priority","all");
 const filtered=data.rows.filter(r=>(status==="all"||r.status===status)&&(priority==="all"||r.priority===priority)&&JSON.stringify(r).toLowerCase().includes(query.toLowerCase()));
 const groups=Array.from(new Set(filtered.map(r=>r.group)));
 const metrics=[["100 / 10","课题目录 / 已定位真实产出写入"],["5 / 1","目标研究所 / 正式注册"],["69 / 6","结构规划 / 正式结构资源"],["20 / 480","访客形态文本 / 台词句数"]];
 return <Stack gap={18} style={{padding:24,color:theme.text.primary,background:theme.bg.editor}}>
  <Text>HK3GTL 内测5 · r99 · {data.time}</Text><H1>完成度审计：实现不等于验收</H1><Text>{data.conclusion}</Text>
  <Row gap={16} wrap>{metrics.map(([value,label])=><Stack key={label} gap={3} style={{minWidth:210,padding:12,background:theme.fill.secondary}}><H2>{value}</H2><Text>{label}</Text></Stack>)}</Row>
  <Text>最直接差距：研究点737,680 vs 已批准255,750，95课题未同步；ERM/W13旧公式且实际未启用。新16档显示名称已在代码，旧注册键不是旧命名仍有效的证据。</Text>
  <Button onClick={()=>dispatch({type:"openFile",path:data.report})}>打开项目内完整HTML报告</Button>
  <Divider/><H2>逐系统核对</H2><Text>状态按职责划分，不折算完成百分比。展开条目查看缺口和证据；已接通仍需当前版本实机回归。</Text>
  <Row gap={10} wrap><TextInput value={query} onChange={setQuery} placeholder="搜索系统、RN或缺口"/><Select value={status} onChange={setStatus} options={[{value:"all",label:"全部状态"},...data.statuses.map(s=>({value:s,label:s}))]}/><Select value={priority} onChange={setPriority} options={[{value:"all",label:"全部优先级"},...['P0','P1','P2','不排期'].map(s=>({value:s,label:s}))]}/><Text>{filtered.length} / {data.rows.length}</Text></Row>
  {groups.map(group=><Stack key={group} gap={6}><H2>{group}</H2>{filtered.filter(r=>r.group===group).map(r=><details key={r.id} style={{borderBottom:'1px solid '+theme.stroke.primary,padding:'10px 0'}}><summary style={{cursor:'pointer'}}><strong>{r.id} · {r.title}</strong><span style={{color:theme.text.secondary}}>　{r.status} · {r.priority}</span></summary><Stack gap={10} style={{padding:'12px 0'}}><Text><strong>已经做到：</strong>{r.implemented}</Text><Text><strong>仍缺：</strong>{r.gaps}</Text><Text><strong>证据等级：</strong>{r.validation}</Text><Row gap={8} wrap>{r.refs.map((ref,i)=><Button key={ref.path+i} onClick={()=>dispatch({type:'openFile',path:ref.absolute})}>{ref.label} · L{ref.line}</Button>)}</Row></Stack></details>)}</Stack>)}
  <Divider/><H2>如何理解验证结果</H2><Text>9月24日只有起步两课题及I01/I02成型有局部实例通过记录。r99编译和18项自定义检查通过，两实例哈希一致；没有r99整包通关/FCL验收。</Text>
  <Text>覆盖：336主Java、20测试Java，共62,773行索引及标记扫描；641份文本提取含153份历史目录文档。关键生产路径人工复核，并非逐行证明。1306个运行JSON可解析。</Text>
  <H2>后续建议顺序</H2><ol>{data.priorities.map(p=><li key={p}>{p}</li>)}</ol><Text>贸易已撤销，AE专项优化延期，结构外观讨论暂停。本轮只生成审计，没有修改游戏业务或启动实例。</Text>
 </Stack>;
}
'''.replace('__DATA__',json.dumps(canvasdata,ensure_ascii=False))
CANVAS.write_text(canvas,encoding='utf-8')
discussion=DOC/'讨论记录'/f'{NOW:%Y-%m-%d_%H-%M-%S}_内测5全系统代码文档完成度审计.html'
discussion.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>内测5全系统完成度审计记录</title><body><h1>讨论与工作记录</h1><p>'+esc(NOW.isoformat())+'</p><h2>用户要求</h2><p>核对当前全部代码与内测5文档，说明完成与未完成系统；最新贸易撤销决定保持有效。</p><h2>本轮实际执行</h2><p>全量建立文本/源码索引，人工核对关键系统的实际注册与调用，验证当前资源JSON与两实例JAR哈希。形成39项系统审计；没有修改业务源码、没有部署或运行游戏。</p><h2>结论</h2><p>'+conclusion+'</p><p>100课题中定位到10个生产证据写入，研究所仅一阶正式注册；批准成本/公式未同步，团队研究与后期主线未闭环。26IF阅读与局部起步流程已有实际成果。已入包文本与NPC实体/审查业务分开计。</p><h2>证据与下一步</h2><p><a href="'+REPORT.as_uri()+'">完整审计与源码引用</a></p><p>工程顺序仅为建议，不视为本轮用户批准开始新一轮修改。保留旧记录，不恢复贸易，不提前做AE优化。</p></body></html>',encoding='utf-8')
meta={'report':REPORT.as_posix(),'canvas':CANVAS.as_posix(),'discussion':discussion.as_posix(),'systems':len(rows),'status_counts':counts,'generated_at':NOW.isoformat()}
(OUT/'report-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。

# 【变更记录 #1】2026-10-23 23:41:24（内测5名称统一维护）：删除旧项目名引用；新增本条维护记录；修改项目路径、启动标识或纹理目录为 HK3GTL 对应名称；用途为统一工具与构建引用，保留原有业务逻辑。
