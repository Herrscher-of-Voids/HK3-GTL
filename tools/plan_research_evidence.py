"""研究讨论阶段：生成100课题证据接线候选并追加现有计划页，不修改游戏实现。

变更记录#1：执行时在输出中写入实际时间；新增逐项路线、旧实现候选与检查，删除无。
目录描述为已存在设计；本脚本提供的路线为待落实方案，源码引用不代表运行验收。
"""
from pathlib import Path
import datetime, hashlib, html, json, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/research-migration-20260928'
PLAN = ROOT / 'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
CAT = ROOT / 'src/main/resources/data/hk3gtl/research/research_catalog.json'
COST = ROOT / 'src/main/resources/data/hk3gtl/research/research_costs.json'

# 每行是具体课题的生产者候选与不能越过的边界，不是统一交样配方。
ROUTES = '''
HED|已有入口|I01首次液态采集成功结算；保留首信知识条件，不要求同意合作。
HSA|已有入口|I02初始光谱实验真实输出；持有分析样本不自动记账。
LSE|已有入口|I03首次分馏成功记录物料分流；起步配方不得要求LSE自身完成。
LES|已有入口|I04稳定化成功输出；回调保留实际消耗与产出事实。
BCE|已有入口|I02使用适配基板与MAX电路完成兼容性试验；保留前序LES门槛。
DMT|已有入口|I07对照校准输出报告；探测器返回与正式制造耗报告分开。
SMR|已有入口|I05实际回收用后稳定介质；不把回收配方反锁到SMR。
HFB|已有入口|调配厂实际制造液态燃料；采样和普通生产结算不得重复登记。
FRP|已有入口|前级GT制作封装样件，I02破坏性隔离检测；不能产出可发电燃料棒。
SRE|前级试验|前级GT封装安全试验件，I02检测绝缘与冷却相容性；不要求先建I19或首次发电。
HLC|前序运行|I19真实产生热冷却剂后，在前级GT换热工序取得检测记录；正式I46随后解锁。
SFR|前级试验|I19输出失活棒后，前级GT拆解一份屏蔽样件；正式I47回收在研究后开放。
RAT|前级试验|MAX场控制元件与液态样本制作屏蔽试件，I02完成干扰对照；基础锚不依赖仿制核心。
SSP|前级试验|前级GT化工设备用稳定介质和可得基材制微量前驱试样，I02检测；试样不能代替I09量产液。
NBS|前级试验|I09前驱液加前级精细金属，GT化工/分离设备制基元试样并分析；不要求I10。
NRA|前级试验|I10基元与前级电路在GT组装设备制驱动试样，I02检测；不要求I11正式纳米单元。
NSP|前级试验|I11未编程单元在隔离条件下完成组装及停止命令对照；证据不授予通用受控纳米群。
CBS|前级试验|I12受控纳米群与MAX基板载体做生长试片并检测；不要求I48或下一阶段魂钢载体。
HRC|前级试验|受控纳米群在前级GT涂覆工序制抗性试片，检测侵蚀前后差异；正式包覆群由I13生产。
SPC|前级试验|I13包覆群与前阶模具在GT压制设备制致密化试件，检测结构；不要求I14量产粗魂钢。
SRA|前级试验|I14粗魂钢经GT热处理形成退火试件并检验缺陷；正式稳定魂钢由I15生产。
SPM|前级试验|I15稳定魂钢经前级GT机床制作公差试件并检测；不要求I16精密成品作为首份证据。
MCE|前级试验|适配基板、已可得导体和掩模做蚀刻试片并检测；不要求I49或I50正式产物。
ALE|升级工程|S01内核对首批魂钢及蚀刻层合格记录，完成设施负载试验；解锁S02控制器及必要功能部件。
OPR|收支记录|汇总I05介质、已开放热管理与废棒处理的实际输入输出；不能凭持有废料生成收支记录。
SSC|前级试验|液态塔运行记录与魂钢约束试件做相态响应检测；不要求首份固态样本。
CCE|前级试验|二阶塔固态样本在前级GT结晶工序制试晶并分析；正式结晶工艺随后开放I08。
CFR|已有入口|液态浓缩成功记录；开始研究仍核对固态采集等已定前置，不修改为提前解锁浓缩棒。
MRE|前序运行|浓缩燃料安全试验与I19、前阶换热及废棒回收记录结合；不要求I20先运行。
CPT|前级试验|前序电路层和魂钢载体在已可用GTL封装工序制工况试件并检测；I50首机使用前级电路。
ERA|前级试验|基础I36运行与固态约束试件检测；开放原机器强化工况，不增加另一座稳定锚。
GSC|前级试验|一、二阶塔取得液固相态记录，测试气态约束试件；不要求三阶塔或首份气态样本。
PCE|前级试验|三阶塔气态样本经前级受控换热试验测量释能；不要求I23先运行。
GPR|前级试验|现有排气与过滤材料完成小批净化对照；早期工艺可用新鲜气体启动，不依赖I52。
FCA|核心试验|I08基础试晶完成热响应试验；不使用未解锁炎核心自证。
ICA|核心试验|I08基础试晶完成低温响应试验；常规GT冷却先可用，不要求冰核心。
RCA|核心试验|基础试晶与已掌握低阶构件做结构对照；研究只开重构功能，具体电路另需白名单和解析。
VCA|核心试验|基础试晶与已有稳定场工装测量定位误差；不要求空核心或千界一乘先造出。
ECA|核心试验|基础试晶在隔离控制回路完成可停止的演算测试；不要求侵蚀加速模块先运行。
GCA|核心试验|基础试晶与已有场控制工装测量引力响应；不要求伊甸之星或奇点产品。
BCA|核心试验|基础试晶与约束试件完成隔离测量；不要求已制造约束核心。
TCA|核心试验|基础试晶完成电磁调制检测；不要求雷核心正式产物。
WCA|核心试验|基础试晶与气态采集样本做流动对照；不要求风核心正式产物。
DKE|前级试验|魂钢精密件及已研究核心在前级组装设备制隔离封装试件；不要求I33先成立。
VAK|前级试验|已可制造理核心在I33受限构造试验；不产出白名单外物品，不直接完成档案课题。
CJK|前级试验|已可制造空核心与前序测量工装在I33校准；不要求信标或列车本体先建成。
SEK|前级试验|已可制造岩核心在I33受控压缩测试；测试不授予时间加速或正式奇点产物。
JOK|前级试验|已可制造约束核心在I33完成能流隔离测试；不从抑制能量生成免费电力。
QOM|前序运行|千界一乘坐标校准成功时保存异常信号；研究后开放I24，不能反用I24作QOM首份证据。
QLE|升级工程|I24首次真实量子观测成功记录，在S02研究S03工程；不要求世界泡采掘成果。
SSQ|收支记录|I14/I15/I16多个真实工艺批次的质量检测对照；重复读取同一批不计新批次。
CQS|前级试验|已开放I50基础封装与相态隔离压力试验；高阶种子电路仍在前一电压制造。
ERM|前级试验|已有侵蚀核心做隔离演算对照，由研究所基础检测功能记录；不要求先启用该加速模块。
WCP|前序运行|I24真实目标信号及误差拟合记录；研究后开放I25可用坐标解析。
UAA|前级试验|已可得魂钢、电路和驱动组件制无人装置台架试件并检测；不依赖采掘残片或I51先生产。
UED|前级试验|I25合法坐标与I51无人装置完成导航、载荷和返回协议检查；不先执行未解锁I26取资。
LTA|前序运行|I26首个成功任务返回遗留资料，在前级已可用分析工序验证载体；研究后开放I32正式逆向。
HBD|发现事件|RN-LTA后I26真实任务随机/保底取得舰船档案，I32实际解析；复制图纸不重复产生证据。
HCC|前级试验|图纸指定接口与I16可得魂钢件做舰体试件检验；不用虚数材料，不要求成舰。
HVI|前级试验|已制舰体件与控制布线在前级装配设备完成子系统联调；整舰运行属于研究后的验收。
BCC|前级试验|已可得空间/约束件与魂钢壳做空容器密封试样并检测；不要求已捕获世界泡。
WBC|前级试验|I53空容器、合法坐标和观测数据做捕获边界演算；不改变真实目标状态，不先执行I27捕获。
WTR|前级试验|已合法捕获对象的观测数据做终止安全演算；此试验不终止、不产资源，正式I28随后解锁。
LRE|前序运行|I20和相变回路真实高负载记录；不要求I21先发电。
SWC|前级试验|真实观测/回收记录与前序种子材料做小尺度稳定性试件；不生成可取资世界泡或消耗W14产物。
SWS|前序运行|I29实际构筑成功记录初始模拟状态及能流；不要求I30先稳定成功。
SWR|前级试验|I30真实稳定模拟批次做终止演算；不结算资源，不要求I31先完成终止。
VRC|前序运行|不同真实目标的独立I26任务记录进行航路对照；不要求I39先提供中继能力。
IOP|前序运行|既有模拟稳定、终止和跨目标资料分析联系差异；完成后才开放I34首次虚数观测。
ILE|升级工程|I34首次真实虚数观测，在S03完成S04工程；不要求I35/I37先建成。
UPR|前级试验|已返回磨损无人装置在已解锁I51完成诊断试验；正式返修随后解锁，不重复返还新旧两件。
LTB|档案验证|I32核对独立遗留资料，或获授权的组织资料与同类实验记录；两条来源可替代，不强制合作。
IAA|前级试验|虚数初观记录与前序魂钢空间试件测量连接稳定性；正式I35组件研究后制造。
ESC|前级试验|前三态塔记录与虚数观测做能流响应对照；不要求四阶塔先提供能量态产物。
HER|前级试验|四阶塔能流记录与前级整流试件检测；试验不向HW账户凭空充值，I38正式产能在研究后。
CED|前序运行|I38合法产能后，对已可用负载执行真实扣费测试；不要求I41先运行，不设人工账户容量上限。
WME|前级试验|已有锚定、能流和世界泡稳定记录完成维系模型验证；不要求I37原型先运行。
WMS|前级试验|I37原型工况与已有魂钢制巨构材料试片并检测；不要求I40正式产物或奇观自产材料。
WPF|前级试验|I40材料在前级加工设备制连接与承载试件；解锁I42正式预制，不提前供给奇观成品件。
CEE|前级试验|I42构件及I37记录完成验收基准件校准；解锁I43方法，不授予任何奇观运行证明。
URE|前序运行|I21真实高负载与巨构材料安全记录；不要求I22先发电。
HCCO|档案验证|既有研究档案和已发生交流事件完成可追溯协作验证；独立路线同样可用，不要求W01先运行。
AIM|前序运行|魂钢与电路连续生产记录在I43核验；不要求W02先扩产。
SEM|前序运行|已解锁雷核心电磁工艺及供能试验记录在I43核验；不要求W04。
IFF|前序运行|现有换热、气体净化和流动试验记录在I43核验；不要求W05。
CCF|前序运行|已解锁冰核心冷却工艺真实记录在I43核验；不要求W06。
IAR|前序运行|I35锚定和I37维系成功记录在I43核验；不要求W03。
MRA|收支记录|固体、液体、气体回收真实账目在I43核验；不要求W07，回收不生成净免费能量。
SFF|前序运行|已有高温材料工艺及I22供能记录在I43核验；不要求W08先产物。
GSF|前序运行|已解锁引力压缩与模拟工艺记录在I43核验；不要求W10先制奇点。
ECB|前序运行|已解锁约束核心和隔离工艺记录在I43核验；不要求W12。
CLE|升级工程|S04核对三领域、I37维系与验收方法记录并完成设施联调；开放S05，不要求W09。
ELC|收支记录|I41多设备负载与实际HW扣费账目核对；不改账户容量、不把余额等于已供能。
CKV|档案验证|S05核对三领域及矛盾资料的来源，必要实物由I32验证；不要求W09先建成。
DIO|前序运行|已运行工业网络与I41权限边界测试在I43核验；不要求W11先统御。
ASR|前序运行|侵蚀核心隔离演算和已有课题完成记录核验；不要求W13加速自身研究。
WCE|前序运行|I29/I30/I31同一合法模拟批次完整生命周期记录核验；不要求W14或真实目标计数充当模拟证明。
CAV|工程验收|I43验证W09/W11/W13/W14实际运行证明及三领域档案；研究完成或持有控制器不能代替运行。
TAA|工程验收|I43验证前14座奇观及仿制舰实际运行证明；解锁W15建造，不要求W15自证，不代替终审。
DVC|档案验证|I43/S05核对三领域可追溯工况差异；只开放诊断资料，不授予角色权能。
'''

def main():
    now = datetime.datetime.now().astimezone().isoformat()
    catalog = json.loads(CAT.read_text(encoding='utf-8'))['topics']
    costs = {n['id']:n for n in json.loads(COST.read_text(encoding='utf-8'))['topics']}
    old = json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))['rows']
    route = {}
    for line in ROUTES.strip().splitlines():
        key, kind, value = line.split('|',2)
        assert 'RN-'+key not in route
        route['RN-'+key] = (kind,value)
    ids = {n['id'] for n in catalog}
    assert len(ids)==100 and ids == set(route) == set(costs)
    byid = {n['id']:n for n in catalog}
    def ancestors(key, chain=()):
        assert key not in chain, ('研究依赖环',chain,key)
        result=set()
        for p in byid[key]['prerequisites']:
            assert p in ids
            result.add(p);result.update(ancestors(p,chain+(key,)))
        return result
    for key in ids: ancestors(key)
    src = ROOT/'src/main/java/com/sirin/hk3gtl'
    source_rows={key:[] for key in ids}
    for p in src.rglob('*.java'):
        for line_number,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
            for key in set(re.findall(r'RN-[A-Z]+',line)) & ids:
                source_rows[key].append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'line':line_number,'text':line.strip()[:350]})
    rows=[]
    for n in catalog:
        key=n['id'];kind,proposal=route[key];c=costs[key]
        reuse=[{'old_id':o['old_id'],'reason':o['reason'],'references':o['references']} for o in old if any(t['id']==key for t in o['targets'])]
        rows.append({**n,'route_kind':kind,'proposed_route':proposal,
          'implementation_status':'已有生产入口，团队归属及运行验收仍待完成' if kind=='已有入口' else '拟接入，未证明生产入口已实现',
          'current_cost':{'points':c['points'],'ticks':c['ticks'],'materials':c['materials']},
          'cost_boundary':'当前费用为旧首轮数据；必须逐物品核对研究前来源，未完成全配方可达性证明。具体试验样件不得以通用电路标签替代。',
          'reuse_candidates':reuse,'java_literal_references':source_rows[key]})
    high_parent=[{'topic':n['id'],'prerequisite':p} for n in catalog for p in n['prerequisites'] if byid[p]['lab']>n['lab']]
    assert not high_parent, high_parent
    upgrades={'RN-ALE':2,'RN-QLE':3,'RN-ILE':4,'RN-CLE':5}
    for key,lab in upgrades.items():assert byid[key]['lab']==lab-1
    counts={kind:sum(r['route_kind']==kind for r in rows) for kind in sorted({r['route_kind'] for r in rows})}
    artifact={'time':now,'status':'研究讨论用实施候选，非100课题已接通','coverage':len(rows),'route_counts':counts,
      'limits':['Java字面量引用不等于真实生产回调','旧实现仅为语义复用候选，未逐条验收其功能','目录无环不证明物料、电压、配方或外部KJS无环','本批未定稿100项具体材料用量、全部数值及S02至S05结构'],
      'rows':rows}
    target=OUT/'evidence-plan-100.json'
    if target.exists():raise RuntimeError('已有产物，避免覆盖历史讨论')
    section_id='research-evidence-plan-100'
    original=PLAN.read_text(encoding='utf-8')
    if 'id="'+section_id+'"' in original:raise RuntimeError('已有章节，避免重复追加')
    esc=lambda x:html.escape(str(x),quote=True)
    pieces=[f'<section id="{section_id}" class="panel"><h2>100课题证据与解锁接线候选</h2><p>变更记录 #1 · {esc(now)}。新增逐项实施路线与源码索引；删除无，保留旧计划。仅讨论稿，不修改生产代码、配方、存档或实例。</p>',
      '<p><strong>覆盖100课题 ≠ 100课题已实现。</strong>10项已有生产证据入口，其余90项为本次接线候选。全部仍需团队归属接线与相应验证。旧实现候选不是旧研究完成状态兑换表。</p>',
      '<p>检索页面可使用浏览器查找课题ID或名称。各阶段展开后可查看逐项路线、现有费用与可定位源码。所有新增试验名称是设计描述，尚非已注册物品。</p>',
      '<p>已确认：真实证据可继承合并；实验按固定团队绑定记账；研究点个人支付；前级试验样件不能充当正式产物。材料付款接口目前只支持标签，需扩展具体物品及必要数据匹配，同时保留精确扣费凭据。</p>']
    for lab in range(1,6):
        subset=[r for r in rows if r['lab']==lab]
        pieces.append(f'<details><summary>S0{lab} · {len(subset)}课题</summary>')
        for r in subset:
            pieces.append(f'<article id="evidence-{esc(r["id"])}"><h3>{esc(r["id"])} · {esc(r["title"])}</h3>')
            for label,value in [('状态',r['implementation_status']),('目录前置','、'.join(r['prerequisites']) or '无研究前置'),('已定证据要求',r['evidence']),('拟接工序',r['proposed_route']),('研究后的解锁',r['result']),('关联设施','、'.join(r['machines']))]:
                pieces.append(f'<p><b>{label}：</b>{esc(value)}</p>')
            c=r['current_cost'];pieces.append(f'<p><b>当前旧费用，非新定稿：</b>{c["points"]}点 / {c["ticks"]/20:g}秒基础耗时；材料 {esc(json.dumps(c["materials"],ensure_ascii=False))}。{esc(r["cost_boundary"])}</p>')
            pieces.append('<details><summary>旧实现复用候选与当前Java引用</summary>')
            for reuse in r['reuse_candidates']:
                pieces.append(f'<p>{esc(reuse["old_id"])}：{esc(reuse["reason"])}</p>')
            for ref in r['java_literal_references']:
                pieces.append(f'<p><code>{esc(ref["path"])}:{ref["line"]}</code> {esc(ref["text"])}</p>')
            pieces.append('</details></article>')
        pieces.append('</details>')
    pieces.append('<p>检查范围：100项唯一覆盖、目录前置无环、前置研究所不高于当前课题、四次研究所升级均在前阶研究。未证明100项物料来源闭合，未执行游戏验收。增强版结构风格调查及新研究所方案另行审批。</p></section>')
    section='\n'.join(pieces)
    marker=original.lower().rfind('</body>')
    assert marker>=0
    output=original[:marker]+section+'\n'+original[marker:]
    backup=OUT/'plan-before-evidence-100.html'
    with backup.open('x',encoding='utf-8') as f:f.write(original)
    target.write_text(json.dumps(artifact,ensure_ascii=False,indent=2),encoding='utf-8')
    PLAN.write_text(output,encoding='utf-8')
    assert PLAN.read_text(encoding='utf-8').replace(section+'\n','',1)==original
    validation={'time':now,'coverage':100,'existing_entry_count':counts['已有入口'],'route_counts':counts,'unique_ids':True,'catalog_acyclic':True,'no_higher_lab_prerequisites':True,'upgrades_in_previous_lab':True,'prior_html_preserved':True,'game_code_changed':False,'game_tested':False,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (CAT,COST)}}
    (OUT/'evidence-plan-validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(validation,ensure_ascii=False))

if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
