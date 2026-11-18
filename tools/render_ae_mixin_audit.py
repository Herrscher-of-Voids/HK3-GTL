"""生成 AE Mixin 审计数据与独立 Canvas；只写审计产物，不修改游戏。
变更记录 #1：2026-09-28，新增统计口径、中文分析、逐类证据与筛选视图。
"""
import json, hashlib, datetime, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/ae-mixin-audit-20260928'
CANVAS=Path.home()/'.cursor/projects/c-Users-OWNER-Desktop-progrem-complate-progrem-hk3gtl/canvases/AE-mixin-audit.canvas.tsx'
HOOKS={'Inject','Redirect','ModifyArg','ModifyArgs','ModifyVariable','ModifyConstant','ModifyExpressionValue','ModifyReturnValue','WrapOperation','WrapWithCondition','WrapMethod','Overwrite'}
NOTES={
 'gtlcore':('规划、执行、容量与显示的主要改写者','MAX_FAST 等规划路径、按需读取库存而非整网复制、模板缓存；普通 CPU 批量执行、超限 CPU 接入；大数量编码、终端显示与分页；GT ME 仓室同步、虚拟不消耗输入。取消原版规划暂停等待，改为检查线程中断。','更适合 GTL 的大数量与批量生产，但没有据此证明任意订单低内存。其覆盖面决定其他合成后端必须专门适配。'),
 'extendedae_plus_gtladd':('EAEP 与 GTL 桥接','1.0.4 包括样板容量／分页协调、倍增样板解包后再查询 GTL 提供者／槽位／分子 IO、超限 CPU 查询适配；两版本都有上传分流、监视器跳转和高亮。','1.0.4 存在针对双方 Mixin 的 MixinSquared 补丁，说明它们并非天然互不干扰。增强版 1.0.3 不具备这些同名适配；其中 MECraftHandlerMixin 仅打包、未声明。'),
 'extendedae_plus':('样板增强、阻挡、倍增与界面','处理样板倍增、虚拟／强制订单等待、普通与扩展提供者、网络卡、分页、快捷上传、样板高亮和监视器界面；新旧版本覆盖面不同。','检测到 MAE2 时跳过自己的 CPU 线程 Mixin；未安装 AdvancedAE 时跳过对应分支。craftingPauseThreshold 在 GTLCore 取消原版等待的组合里不能解释为完整有效的暂停控制。'),
 'gtladditions':('库存遍历与 GTL 机器适配','原实例 3.3：克隆数量映射、快速迭代器、库存树扁平化缓存、精确过滤集合、ME 库存同步与退款。增强定制 3.2.8：长流体 JEI 转换、成型／湮灭面板、超级样板总成模式、分子处理器特殊输出。','同名模组在两套底包里功能分支差别很大，不能将一套的优化数量套给另一套。具体总成与库存能力也有非 Mixin 代码。'),
 'GTL-Enhancedcore':('IV 任务隔离与真实产出结算','普通 CPU 与超限 CPU 的投料上下文；IV 总成独立队列、保存／恢复、取消退款、样板编辑保护；真实产出等待；总成名称显示；终端手动置顶与 JEI 操作。','部分任务禁止从网络已有成品直接恢复完成，必须等待本次加工产出。替换后端必须保留这条约束，否则可能跳过加工或丢失任务归属。'),
 'ExtendedAE':('扩展设备基础衔接','样板终端菜单与数据包、部件入网与 NBT 恢复、扩展库存接口、液位发射器视觉与放置预览。','为扩展设备接入 AE 提供基础能力；不能单凭这些 Mixin 宣称改写了整个合成规划器。'),
 'GTLsupb':('无线编码与终端便利功能','JEI 无线编码后备处理、待编码菜单初始化、加工样板绑定 GT 配方、无线接入点功能按钮与节点状态、手动置顶保留。','提升编码与定位便利性；不是循环规划求解器。只在原实例找到这组声明。'),
 'GTMAdvancedHatch':('ME 仓室朝向','初始化 ME 物品／流体仓所有连接方向，并调整 GTL ME IO 仓的方向行为。','影响机器与 ME 网络接线；不增加合成规划容量。'),
 'mae2':('样板 P2P 与协处理器判定','修改 CPU addBlockEntity 中一次 getAcceleratorThreads 调用；样板 P2P 阻挡状态传递。beta.c 还包含尾部清理、样板更新通知与旧存档迁移。','EAEP 对其已有主动避让。增强版 alpha 的 pushPattern 选择器写法需单独加载核验，不能用 beta.c 的结果代替。'),
 'merequester':('请求器注册与界面接入','向 AE 注册方块、物品、部件、菜单和屏幕；JEI／REI 拖放以及界面访问器。','自动补库存主要属于请求器自己的业务实现；这里的 Mixin 多为接入点。未安装 REI 时插件跳过对应分支。'),
 'alltheleaks':('AE 相关生命周期修复','无线终端玩家表访问、手册上一物品引用访问、无线终端创造页注册重定向与填充。','是否生效由 IssueManager 的问题与版本白名单控制。不能将 5 个打包声明全部视为当前启用。旧启动日志确认过其中 3 个创造页相关声明进入允许列表。'),
 'gtceu':('AE 库存监听访问桥','对 AE2 GenericStackInv 的 listener 提供读取与修改访问器，供 GT 的库存联动设置变更监听。','1 个 Mixin，2 个访问方法；不能计为两项性能优化。'),
 'ae2ct':('合成树显示','将配方树摘要附加到 CraftingPlanSummary 的生成与读写，在合成确认页添加树视图按钮。','增加可解释性，也增加计划摘要数据。fromJob 将 ICraftingPlan 强转 CraftingPlan，第三方计划包装实现需要兼容这个假设。'),
 'ae2wtlib':('无线合成终端入口与补货显示','覆写无线合成终端菜单类型，并在物品图标渲染中提供补货相关显示。','无线终端基础适配，不是大订单规划器。'),
 'AEF':('收藏与排序','终端快捷收藏、收藏高亮、将收藏项移至列表前部。','纯终端便利功能，不解决循环订单。'),
 'wildcard_pattern':('通配样板','扩展已编码样板识别，覆写 PatternProviderLogic.updatePatterns 展开通配样板并重建输入／样板集合。','与 GTLCore、EAEP、MAE2 在样板刷新路径叠加，需要核对刷新后的身份与倍增包装；不能因为类目标相同就判为必然冲突。'),
 'useless_mod':('提供者主从同步保护','对从属提供者限制菜单点击和 Shift 移动；处理样板库存编辑、升级、拆卸与主从关系清理。','只在增强版找到这组声明。影响提供者交互与同步，不能概括成 AE 性能优化。'),
 'ae2cs':('无线连接器与水晶生长','线缆部件变动通知、指定宿主自定义通道数、加速水中种子、渲染边界扩展。','服务无线设备及种子功能，未接管自动合成计划。'),
}
FINDINGS=[
 ('现有 GTL 已经包含完整合成改造','两套实际 GTLCore JAR SHA256 一致；包括分子操纵者相关机器、超限 CPU、MAX_FAST 规划与批量派发。评估万象构序应比较增量能力与注入重叠，不能按原版 AE2 缺少全部这些能力来决策。'),
 ('规划与低内存之间的取舍','GTLCore 跳过 NetworkCraftingSimulationState 的全量库存复制，并在计算结束清理缓存；同时取消原版 handlePausing 的等待与时间切片，仅保留中断检查。减少复制和更快运行有代码依据，但没有手机压力测试、总内存上限或极端配方图保证。'),
 ('刷新频率已被降低','两套 ae2CraftingServiceUpdateInterval 都是 4；库存服务原实例为 8，增强版为 16。当前都是 2 的幂，与位掩码实现对应。减少更新次数的同时也会增加部分状态刷新延迟。'),
 ('批量投料是多层叠加','普通提供者 PatternProviderLogic 是原实例 13 个、增强版 10 个候选 Mixin 的共同目标（含访问器）。GTLCore 自带自动扩量、EAEP 倍增、MAE2 样板 P2P、通配样板及桥接插件同时涉及该路径。当前普通提供者默认扩量配置为 false，但 GTL 特定仓室可独立启用。'),
 ('已有兼容补丁而非全靠偶然','EAEP 遇到 MAE2 跳过 CPU 线程补丁。原实例 EAEP-GTLAdd 1.0.4 使用 MixinSquared 协调 GTLCore 与 EAEP 的容量／分页，并将倍增样板还原后查询提供者和总成槽位。require=0 的适配钩子允许不命中，因此打包存在也不能证明每一项成功应用。'),
 ('真实历史失败证据','原实例 2026-09-28 00:25 启动日志使用 EAEP 1.6.1，记录菜单 clicked、节点 setRemoved、矩阵 use、AEBaseScreen init 的注入失败，另有 JEI 相关失败。当前磁盘为 1.6.2；历史日志不能证明新版已修复或仍失败。增强版没有找到对应 latest.log。'),
 ('非标准计划的额外兼容点','AE2CT 将 ICraftingPlan 强转为 CraftingPlan。新的合成后端、强制计划包装或其他计划实现即使能提交，也需保证摘要生成兼容，避免在确认界面发生 ClassCastException。这里只记录代码风险，未复现。'),
 ('增强版 IV 订单所有权','Enhancedcore 将 IV 隔离总成的投料、持久化与实际产出结算连接到普通／超限 CPU，部分任务禁止直接从网络现成成品结束。新后端不能绕过这些钩子。'),
 ('没有发现重复 Overwrite 不等于没有冲突','本次范围内没有找到两个声明以相同目标类、方法名、完整描述符同时 @Overwrite。仍存在 Overwrite 与 Inject/Redirect/WrapOperation 的叠加、可取消回调、MixinSquared、加载顺序和选择器匹配风险。未执行运行时合成后的类导出。'),
 ('HK3GTL 的边界','本次扫描的已部署 HK3GTL JAR 中未找到直接针对 AE 的 Mixin；HK3 对 GT 配方和研究的门槛仍可能间接影响订单运行。无 AE Mixin 不等于全链自动化已经兼容。'),
]

def module(jar):
    for key in sorted(NOTES,key=len,reverse=True):
        if key.lower() in jar.lower(): return key
    return jar

def make():
    result={'generated_at':datetime.datetime.now().astimezone().isoformat(),'scope':'本地启用扩展名 .jar 与嵌套 JAR 的静态注解；AE2 自身注入游戏的 18 类另列，不计外部修改。未进行游戏启动或新性能测试。','findings':FINDINGS,'packs':{}}
    for pack in ('original','enhanced'):
        d=json.loads((OUT/(pack+'.json')).read_text(encoding='utf-8'))
        extra=[m for m in d['indirect_ae_mixins'] if not m['jar'].startswith('appliedenergistics')]
        records=[]
        inv={x['jar']:x for x in d['inventory']}
        for m in d['ae_mixins']+extra:
            source=OUT/'decompiled'/inv[m['jar']]['sha256'][:12]/'src'/(m['class'].replace('.','/')+'.java')
            if not source.exists() and '$' in m['class']:
                source=OUT/'decompiled'/inv[m['jar']]['sha256'][:12]/'src'/(m['class'].split('$')[0].replace('.','/')+'.java')
            scope='AE2直接目标' if any(t.startswith('appeng.') for t in m['targets']) else ('附属与ME桥接目标' if m in d['ae_mixins'] else '间接关联')
            state='已声明；运行时待核验'
            if not m['declared']:state='仅打包；未在配置声明'
            elif m['class'].startswith('com.extendedae_plus.mixin.advancedae'):state='按插件条件跳过：未安装AdvancedAE'
            elif m['class']=='com.extendedae_plus.mixin.ae2.CraftingCPUClusterMixin':state='按插件条件跳过：已安装MAE2'
            elif 'merequester.mixin.compat.REI' in m['class']:state='按插件条件跳过：未安装REI'
            elif 'alltheleaks' in m['class']:state='由AllTheLeaks问题／版本白名单决定'
            hooks=[];access=[]
            for f in m['methods']:
                for a in f['annotations']:
                    typ=a['type'].rsplit('/',1)[-1].rstrip(';')
                    if typ in HOOKS: hooks.append({'type':typ,'handler':f['name'],'descriptor':f['descriptor'],'annotation':a['values']})
                    elif typ in ('Accessor','Invoker'):access.append({'type':typ,'method':f['name'],'target':a['values'].get('value',[])})
            records.append({'module':module(m['jar']),'jar':m['jar'],'class':m['class'],'targets':m['targets'],'scope':scope,'state':state,'declared':bool(m['declared']),'config':m['declared'],'missing_targets':m['missing_targets'],'hooks':hooks,'access':access,'source':str(source).replace('\\','/'),'source_exists':source.exists(),'sha256':m['sha256']})
        modules=[]
        for jar in sorted(set(r['jar'] for r in records)):
            rows=[r for r in records if r['jar']==jar];declared=[r for r in rows if r['declared']];note=NOTES[module(jar)]
            modules.append({'jar':jar,'name':module(jar),'total':len(rows),'declared':len(declared),'direct':sum(r['scope']=='AE2直接目标' for r in declared),'hooks':sum(len(r['hooks']) for r in declared),'access':sum(len(r['access']) for r in declared),'title':note[0],'effect':note[1],'result':note[2],'sha256':inv[jar]['sha256']})
        declared=[r for r in records if r['declared']]
        targets=set(t for r in declared for t in r['targets'])
        counts=Counter(t for r in declared for t in r['targets'])
        summary={'top_jars':sum('!/' not in x['jar'] for x in d['inventory']),'nested_jars':sum('!/' in x['jar'] for x in d['inventory']),'all_annotated_mixins':len(d['all_mixins']),'modules':len(modules),'declared_classes':len(declared),'packaged_classes':len(records),'direct_ae2':sum(r['scope']=='AE2直接目标' for r in declared),'unique_targets':len(targets),'unique_ae2_targets':len([t for t in targets if t.startswith('appeng.')]),'behavior_handlers':sum(len(r['hooks']) for r in declared),'access_handlers':sum(len(r['access']) for r in declared),'known_plugin_skips':sum(r['state'].startswith('按插件') for r in declared),'parse_errors':len(d['errors']),'missing_sources':sum(not r['source_exists'] for r in records)}
        result['packs'][pack]={'summary':summary,'modules':modules,'records':records,'hotspots':[{'target':t,'classes':n} for t,n in counts.most_common(15)],'inventory':d['inventory'],'native_ae_mixins':[m['class'] for m in d['indirect_ae_mixins'] if m['jar'].startswith('appliedenergistics')]}
    (OUT/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    payload=json.dumps(result,ensure_ascii=False,separators=(',',':'))
    template='''// AE Mixin 审计；2026-09-28 新增只读结果视图，数据来自 report.json 的本地快照。
import {H1,H2,Text,Table,Grid,Stat,Select,TextInput,Button,Callout,useCanvasState,useCanvasAction,useHostTheme} from "cursor/canvas";
const audit: any = __DATA__;
export default function AEAudit(){
 const theme=useHostTheme(); const action=useCanvasAction();
 const [pack,setPack]=useCanvasState("ae-audit-pack","original");
 const [query,setQuery]=useCanvasState("ae-audit-query","");
 const [scope,setScope]=useCanvasState("ae-audit-scope","全部");
 const p=audit.packs[pack];const s=p.summary;
 const rows=p.records.filter((r:any)=>(scope==="全部"||r.scope===scope)&&JSON.stringify(r).toLowerCase().includes(query.toLowerCase()));
 return <main style={{padding:24,color:theme.text.primary,background:theme.bg.editor,fontSize:14,lineHeight:1.65}}>
 <H1>GTL 两套底包 · AE Mixin 审计</H1>
 <Text>{audit.generated_at} · 实际 JAR 哈希快照</Text>
 <Callout title="这些是声明数量，不是运行时全部成功注入的数量" tone="info">{audit.scope} 逐类提取全部注解，重点深读规划、派发、存储、兼容插件与历史失败；没有逐行验证每个辅助算法。</Callout>
 <Select value={pack} onChange={setPack} options={[{value:"original",label:"原实例 GregTech-Leisure-1.4.5.2"},{value:"enhanced",label:"增强版 2.1"}]} />
 <Grid columns={3}><Stat value={s.declared_classes} label="外部 AE 关联 Mixin 声明类"/><Stat value={s.direct_ae2} label="其中：直接修改 AE2 的类"/><Stat value={s.behavior_handlers} label="行为注入／覆写方法声明"/></Grid>
 <Text>{s.modules} 个来源模组；{s.access_handlers} 个 Accessor/Invoker 方法另计；{s.unique_ae2_targets} 个不同 AE2 目标类；扫描 {s.top_jars} 个顶层 JAR 和 {s.nested_jars} 个嵌套 JAR；解析错误 {s.parse_errors}。已核对插件条件跳过 {s.known_plugin_skips} 类，其他条件与运行时是否命中仍需分别判断。</Text>
 <H2>结果与影响</H2>
 {audit.findings.map((f:any,i:number)=><section key={i} style={{marginBottom:16}}><strong>{f[0]}</strong><div style={{color:theme.text.secondary}}>{f[1]}</div></section>)}
 <H2>各模组做了什么</H2>
 <Table headers={["实际 JAR","声明类","直接 AE2","行为方法","访问方法"]} rows={p.modules.map((m:any)=>[m.jar,m.declared,m.direct,m.hooks,m.access])}/>
 <Text>统计方法：一个 @Mixin 类计一次；一个带行为注解的方法计一次，不把它的多个目标选择器或多个字节码命中位置算成多项。仅增加接口／普通方法的类可能没有行为注解。两套实例分开计数，不能相加称为一套包的数量。</Text>
 {p.modules.map((m:any)=><details key={m.jar} style={{padding:"10px 0",borderBottom:`1px solid ${theme.stroke.secondary}`}}><summary><strong>{m.name}</strong> · {m.title} · {m.declared} 类</summary><p>{m.effect}</p><p>{m.result}</p><small>JAR SHA256：{m.sha256}</small></details>)}
 <H2>逐类清单与注入证据</H2>
 <Grid columns={2}><TextInput value={query} onChange={setQuery} placeholder="按模组、类名、目标方法或注解搜索"/><Select value={scope} onChange={setScope} options={["全部","AE2直接目标","附属与ME桥接目标","间接关联"].map(x=>({value:x,label:x}))}/></Grid>
 <Text>当前筛选 {rows.length} 类。展开后可查看全部注入声明，并打开本地反编译证据。</Text>
 {rows.map((r:any)=><details key={r.jar+r.class} style={{padding:"10px 0",borderBottom:`1px solid ${theme.stroke.secondary}`}}><summary>{r.module} · {r.class.split(".").pop()} · {r.hooks.length} 个行为方法</summary><p>{r.class}</p><p>目标：{r.targets.join("；")}</p><p>{r.state} · {r.scope}</p>{r.missing_targets.length>0&&<p>本次模组 JAR 中未找到目标：{r.missing_targets.join("；")}。游戏自身类不在 mods 扫描范围；可选模组目标缺失需结合插件判定。</p>}
 {r.hooks.map((h:any,i:number)=><div key={i} style={{marginBottom:12}}><strong>{h.type} · {h.handler}</strong><pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere",fontSize:12,color:theme.text.secondary}}>{JSON.stringify(h.annotation,null,2)}</pre></div>)}
 {r.access.length>0&&<p>访问桥：{r.access.map((x:any)=>x.type+" "+x.method).join("；")}</p>}
 <small>声明：{r.config.map((c:any)=>c.config+" / "+c.side+(c.plugin?" / "+c.plugin:"")).join("；")}</small><div><Button onClick={()=>action({type:"openFile",path:r.source})}>打开反编译证据</Button></div></details>)}
 <H2>扫描覆盖与未命中模组</H2><Text>以下为全部顶层启用扩展名 JAR。清单中无 AE 关联 Mixin 的模组，仍可能通过事件、普通 API、反射或通用网络／内存补丁影响 AE；它们未被误算为直接 AE Mixin。</Text>
 <details><summary>全部扫描 JAR 与 SHA256</summary>{p.inventory.filter((j:any)=>!j.jar.includes("!/")).map((j:any)=><p key={j.jar}>{j.jar}<br/><small>{j.sha256}</small></p>)}</details>
 <details><summary>另列：AE2 自身注入游戏的 18 个关联类</summary>{p.native_ae_mixins.map((c:string)=><div key={c}>{c}</div>)}</details>
 </main>;
}
'''.replace('__DATA__',payload)
    CANVAS.write_text(template,encoding='utf-8')
    print('Canvas:',CANVAS)
    print(json.dumps({k:v['summary'] for k,v in result['packs'].items()},ensure_ascii=False,indent=2))
if __name__=='__main__':make()

# 【变更记录 #2】2026-10-23 23:41:24（内测5名称统一维护）：删除旧项目名引用；新增本条维护记录；修改项目路径、启动标识或纹理目录为 HK3GTL 对应名称；用途为统一工具与构建引用，保留原有业务逻辑。
