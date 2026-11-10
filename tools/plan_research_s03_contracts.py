"""变更#1：2026-09-28，细化S03的19课题，记录本轮两项明确答复。
仅追加现有研究计划、讨论记录和JSON；不改生产源码、配方、资源及游戏实例。
区分研究前置、事件技术授权、真实账本、模拟批次与实际库存交付。
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import datetime
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
PLAN=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
CAT=ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
CONTENT=ROOT/'src/main/resources/data/hk3gtl/catalog/industrial_content.json'
AUDIT=OUT/'evidence-links-20260928-035524.json'

# 课题|前级投入|实际实验设施|成功事件|正式解锁|自锁/越级边界
RAW='''
WCP|I24初观资料、获得茧加强技术后的I44原始目标信号及误差记录|I44加强观测取得原始信号→I24完成坐标误差拟合实验|原始目标观测与误差拟合真实完成；输出研究用记录，不提前生成供I26使用的正式坐标|I25控制器及正式坐标解析工况；I44仍负责实际目标锁定|不得要求I25先解析自己的证据；茧技术是独立事件授权，不能因QOM基础校准已开放而跳过
UAA|SPM已可得魂钢件、CPT电路及前级驱动件、合法观测/定位资料|前级GT组装台架试件→I02驱动与控制检测|试件实际完成执行器驱动、指令响应和停止检测；不发射任务、不取世界泡资源|无人资源探测器与工业作业无人机制造；I51合并候选位置I11，I16供精密件；返修留给UPR|首件不要求世界泡残片、磨损无人装置或I26任务成果；不用即将制造的无人装置造自己
UED|I25正式坐标、I44有效锁定记录、UAA制造的无人装置与测试耗材|无人装置装配设备的起步联调工况（合并候选I11）|真实完成导航、载荷、通信及返回协议台架检查；核对服务端目标身份与有效状态，不进行采掘结算|I26控制器和真实无人采掘任务；每个真实目标公共累计最多10次，物品/流体资源池另定|实验不要求I26先成功采掘；台架检查不占十次、不产资源；I39不是首任务的必需设备
LTA|首次成功I26真实采掘保证带回的起步遗留资料，关联目标与任务结算回执|前级GT制封装取样件→I02检测资料载体与工艺痕迹|实际消耗检测耗材并检验任务返回资料，核验原成功任务；不能只持有古代遗产物品授予|I32控制器、遗留实物逆向和技术记录验证工况|首次成功任务保证资料已确认；首次检验不用I32；首次任务失败或未结算不发资料；起步资料不等同舰船工程档案
HBD|LTA完成后I26合格真实任务发现的舰船工程档案|I32首次有效舰船档案解析|I32实际解析有来源的档案，产出仿制休伯利安蓝图并提交HBD证据；重复回调不重复发现或授予物品|仿制舰工程资料解读与后续HCC研究资格；取得后耗材复制蓝图，复制不完成研究|沿用随机提前发现＋有限次数保底；20%/第5次仍为旧数值候选，不视为批准；模拟日志不触发舰船档案保底
HCC|HBD解读的图纸要求、I16魂钢件、UAA可用施工执行组件|I16基础加工工况制舰体连接试件→I02尺寸/承载检测|实际加工并检测龙骨连接、推进接口等试件；测试件不冒充正式舰体组件|仿制舰龙骨段、推进组件及量子阶段可达施工装置的正式制造工况；候选由I16和无人装置装配设备分工|不用虚数阶段复合材料或成舰作为首份投入；具体材料和配方另审，不要求未来I40/I42先运行
HVI|HCC已能制造的舰体部件、控制布线和已解锁导航组件|前级装配/联调工况（候选I16/I33）|供电、控制、导航接口在真实试验回路完成联调并安全停止；不要求整舰先成型|H01控制器/组装入口与仿制舰运行验收方法；实际建设及运行完成后另记毕业工程证据|研究完成、持有蓝图或摆放控制器都不算舰已完成；不自行加入飞行能力、十模块或新外观要求
BCC|SPM魂钢壳体、已解锁空间组件与JOK约束工装|I16制空载试壳→I33密封与约束场检测|空载试壳完成密封和场稳定检验；仅形成检测记录，不生成封存世界泡|正式空世界泡收容容器；I53合并候选为I16制壳、I33装配校准|首个容器不要求捕获样本；试壳不能用于正式捕获；神之键工装不逐配方消耗
WBC|BCC正式空容器、I25坐标、I44锁定及I24既有观测数据|I33捕获边界空载验证工况|真实耗电耗材完成容器容量、边界和锁定数据的校验；验证不改变真实目标状态、不占采掘次数|I27控制器与整体捕获工况；实际捕获后容器绑定原目标身份和采掘计数|不要求I27或已捕获世界泡提供首份证据；复制/换容器不得创造新目标或重置次数
WTR|I27实际捕获的目标与封存记录、终止控制测试件及可用观测数据|I33隔离终止控制试验，使用被捕获对象的观测副本|真实执行控制试验并核对合法捕获回执；只演算安全边界，原目标保持封存，不产生终止资源|I28控制器、真实目标终止和容器残件处理；实际终止仅能结算一次|首份试验不用I28，不暗加非祖先LTA/I32；已采资源对终止收益的核算方案待定，不能当作未采满额再发
LRE|I20真实中型发电工况、I23相变/损耗数据与前级负载耗材|I20/I23实际负载工况→I02核验封装检测件与关联回执|实际高负载运行及热收支记录齐全，回调能追溯原设备和消耗；具体负载阈值待定|I21独立控制器与大型供能工况|不要求I21先发电；不把研究界面tier显示当作S03已能承受本课题功率的证明
SWC|真实目标观测与I28实际终止回收记录、LTA解析资料、前序可制造的世界模型载体与物质种子试件|I16/I33前级制种子与载体试件→I32小尺度构筑模型验证|真实制样和模型验证成功，试验本身不创建可取资世界泡；关联真实终止记录而非只完成WTR研究|I29控制器、前级可制造的正式模型载体/种子工序与模拟构筑；成功构筑建立独立模拟批次|不使用W14、文明奇点或后续虚数材料作首批种子；伊甸之星已由SEK解锁且不消耗，精确种子配方待审
SWS|I29实际构筑的初始模拟批次与模型误差/能流记录|I29构筑成功回调直接提交证据，S03随后正常研究|构筑真实完成且独立批次已持久化，初始状态记录完整；无需先由I30稳定|I30控制器及稳定运行工况，耗稳定介质和能量后得到可终止批次及废介质|已确认初始批次可封存等研究，期间不产资源、不推进也不因离线/等待消失；不重复要求再构筑一份样品
SWR|I30实际稳定的模拟批次、同批构筑和稳定回执、终止控制测试耗材|I32对稳定批次观测副本做隔离终止试验|真实耗材耗电执行终止控制验证，原批次保持稳定，不提前生成资源或标为已终止|I31控制器与模拟终止回收；正式终止只结算该模拟批次一次，输出同真实资源目录范围|不要求I31先终止来证明自己；试验演算不等于真实模拟世界泡的终止；不改变真实目标十次计数
VRC|不同真实目标的I25/I44定位记录和I26成功任务回执，SWS后的模拟稳定资料|I32航路对照验证，基础I26继续独立运行|核验多个不同目标的独立成功任务和路由对照；同坐标多次或复制报告不能冒充多个目标|I39控制器与多目标组织/中继工况；不改变I26起步单任务能力|不要求I39先中继自己的证据；多目标数量、调度并发及维护成本未定，不能把中继当成无限并行
IOP|同一模拟批次的构筑、稳定、I31真实终止记录，以及VRC所用跨目标观测资料|I32稳定/衰变联系差异分析工况|实际分析已有工况及终止日志，确认同批状态变化与跨目标差异，输出初观前研究记录|I34控制器与首次虚数观测方法|不反用I34或I35/I37资料自证；一次模拟状态变化不能靠复制不同载体伪造
ILE|I34首次成功虚数观测的原始设备、工况与观测记录|I34正式初观成功回调；S03正常支付并研究|实际观测完成后提交证据，不另加重复观察或要求提前造S04|S04控制器及必要功能件，世界维系/空间锚定仍由后续课题开放|首台S04不用未开放I35/I37产物；S03的供电能力需独立验证，研究所正式命名仍不在此定案
UPR|I26真实返回的磨损资源探测器/作业无人机及原装置身份和任务回执|已开放无人装置制造设备的诊断工况（合并候选I11）|实际执行故障定位与维修可行性检测，返回同一件待修装置；检测不提前恢复耐久或重复输出旧件|有损耗材的正式返修工况；合并候选仍为I11，保留装置来源与已存在标识|UAA只开制造，不在UAA附送UPR维修收益；维修投入旧件后只交付修复件，具体寿命和费用待定
LTB|独立取得的遗留记录，或获许可的组织资料与同类真实实验证据|I32交叉解析，S03按同一课题研究|实际完成不同来源的资料与工艺证据对照；合作路线验证资料授权，独立路线无需合作授权，两者不必同时满足|I32档案解析改良和受研究控制的复现工况；节料/耗时收益逐配方另列待定|复制同一档案不产生新独立来源；不免费解锁其他课题、舰船保底或白名单外产物；VAK许可不等于本课题已完成
'''

GATES={
 'WCP':['QOM','CJK'], 'UAA':['SPM','CPT','HSA'], 'UED':['UAA','WCP','CJK'],
 'LTA':['UED','HSA'], 'HBD':['LTA','UED'], 'HCC':['HBD','SPM','UAA'],
 'HVI':['HCC','SPM','DKE'], 'BCC':['SPM','DKE','JOK'], 'WBC':['BCC','DKE','WCP'],
 'WTR':['WBC','DKE'], 'LRE':['MRE','PCE','HSA'], 'SWC':['WTR','LTA','SEK','SPM'],
 'SWS':['SWC'], 'SWR':['SWS','LTA'], 'VRC':['UED','SWS','LTA'],
 'IOP':['SWR','VRC','LTA'], 'ILE':['IOP'], 'UPR':['UAA','UED'], 'LTB':['LTA','VAK'],
}
ITEMS={
 'UAA':['unmanned_resource_probe','industrial_work_drone'],
 'UED':['unmanned_resource_probe','industrial_work_drone'],
 'HBD':['imitation_hyperion_blueprint'],
 'HCC':['hyperion_keel_segment','hyperion_thruster_assembly'],
 'HVI':['hyperion_navigation_module','hyperion_bridge_module'],
 'BCC':['empty_bubble_containment_vessel','failed_containment_shell'],
 'WBC':['empty_bubble_containment_vessel','sealed_real_world_bubble'],
 'WTR':['sealed_real_world_bubble','bubble_termination_charge','bubble_container_remnant'],
 'SWC':['world_model_carrier','world_matter_seed','imitation_star_of_eden'],
 'SWS':['unstable_simulated_world_bubble','stable_simulated_world_bubble'],
 'SWR':['stable_simulated_world_bubble'],
 'UPR':['worn_resource_probe','worn_work_drone','drone_disassembly_scrap'],
 'LTB':['reverse_engineering_specimen','failed_engineering_specimen'],
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def production_hashes():
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src/main').rglob('*')) if p.is_file()}


def main():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp=now.strftime('%Y%m%d-%H%M%S-%f')
    before_source=production_hashes()
    topics={r['id']:r for r in json.loads(CAT.read_text(encoding='utf-8'))['topics']}
    content={r['id']:r for r in json.loads(CONTENT.read_text(encoding='utf-8'))['entries']}
    audit=json.loads(AUDIT.read_text(encoding='utf-8'))
    for path,digest in audit['source_hashes'].items():assert sha(ROOT/path)==digest,('源审计已过期',path)
    auditrows={r['id']:r for r in audit['rows']}

    def ancestors(key,chain=()):
        assert key not in chain,('研究环',chain,key)
        out=set()
        for parent in topics[key]['prerequisites']:
            out.add(parent);out.update(ancestors(parent,chain+(key,)))
        return out

    rows=[]
    for line in RAW.strip().splitlines():
        short,inputs,facility,success,unlock,guard=line.split('|')
        key='RN-'+short;n=topics[key];assert n['lab']==3
        gates=['RN-'+x for x in GATES[short]]
        assert set(gates)<=ancestors(key),(key,set(gates)-ancestors(key))
        item_ids=ITEMS.get(short,[])
        assert all(i in content and content[i]['kind']=='item' for i in item_ids),(key,item_ids)
        rows.append({**n,'inputs':inputs,'experiment_facility':facility,'success':success,
                     'formal_unlock':unlock,'no_self_lock':guard,'experiment_recipe_requirements':n['prerequisites'],
                     'facility_and_input_unlocks':gates,
                     'catalog_item_reuse_candidates':[{'id':i,'name':content[i]['zh']} for i in item_ids],
                     'external_authorization':'定位真实世界泡时必须另核对茧加强技术授权；研究继承不自动复制事件权限或资源',
                     'current_evidence_refs':auditrows[key]['evidence_refs'],'current_gate_refs':auditrows[key]['gate_refs'],
                     'status':'具体实验与工况提案，尚未实现','approval':'只有明确答复列入已确认，其余候选不自动定稿'})
    assert len(rows)==19 and len({r['id'] for r in rows})==19
    assert {r['id'] for r in rows}=={k for k,n in topics.items() if n['lab']==3}
    assert not any(r['current_evidence_refs'] for r in rows)
    for r in rows:assert set(r['experiment_recipe_requirements'])<=ancestors(r['id'])

    decisions=[
        {'question':'LTA起步资料采用首次成功保证还是随机有限保底？',
         'answer':'首次成功任务保证带回起步遗留资料（推荐）',
         'effect':'首次成功结算的I26真实采掘任务保证起步遗留资料；普通资源仍随机，舰船档案仍按单独随机＋保底规则。资料跟随真实结算回执交付，复制或恢复不再次发放。'},
        {'question':'I29初始批次能否封存等待SWS，还是必须持续耗能托管？',
         'answer':'允许初始批次封存，研究完成后投入I30（推荐）',
         'effect':'初始批次可封存等待研究，期间不产资源、不推进工况，不因离线或等待消失；投入I30正式运行后按工况耗能。封存不代表免除实际构筑成本，也不等于已经稳定。'},
    ]
    findings=[
        '已读Hk3WorldBubbleLedger和Data：存在规范身份派生、十次上限、捕获/终止状态、事务预留/结算及交付确认、独立模拟批次和持久化。它本身不抽资源、不扣机器费用、不插入库存、不定义团队产权。',
        '本轮搜索src/main/java，账本类/数据类名称的引用仅位于这两个底层文件内；尚未定位生产机器对该账本的调用。已有测试源文件不是本轮运行测试的证据。',
        '旧quantum/world_bubble_reforming可直接制造world_bubble_sample，quantum_trade_contract可制造ancient_legacy；这些通用旧物品不能单靠ID充当新真实目标、任务或模拟批次证据。未停用或删除旧配方。',
        '现有目录RN-UAA的result写了返修，同时RN-UPR也定义返修。提案分开制造和返修权限；尚未修改目录或游戏配方。',
        '现有RN-HBD的evidence仍写发现方式待叙事规格；后续明确答复已确定I26真实任务发现、I32解析、随机＋有限保底，实施时应同步资源描述。',
        '主线v4的C2已写茧技术用于寻找不同世界泡，工业树v5的I25输入也为加强观测；QOM独立基础校准的最新裁定只覆盖起步，不删除后续事件技术授权。',
        'WTR没有LTA作为研究祖先，因此首份终止试验不能悄悄要求I32；本稿用已可达I33隔离试验。SWC以后LTA已在祖先中，才可采用I32模型分析。',
    ]
    pending=[
        '八项补充设备具体合并映射仍待答，尤其无人装置I51→I11、容器I53→I16/I33。本稿以候选标注，不删除旧设备。',
        'S01工程验证承载方式及ERM对应机制仍待答，本稿不把研究所改成通用实验机器。',
        '舰船档案概率20%、第5次保底仅为前次展示候选；发现计数资格、复制成本与全部耗材/功率/时长尚未最终定稿。',
        '真实目标坐标规范化、任务权限、技术授予的团队归属/继承查询须按研究与叙事规则接线；不能用nearest-player或任意物品NBT代替授权。',
        '实际采掘和终止的资源预算关系、流体抽样、空资源成功是否计次、任务失败及装置损耗成本仍需配方专项确认。',
        '模拟稳定后的断电/移动状态、维护与终止收益平衡另行细化；初始封存的明确答复不自动扩大为所有阶段永远免维护。',
        'H01具体运行验收项目与此前未定模块职责另行收口；此处仅确定研究→建造→实际验收的边界，不审批结构。',
    ]
    contracts=[
        '研究证据、研究完成、事件技术授权、机器制造和实际工况分别检查。固定机器研究团队离线时可记录真实实验；课题推进仍遵守全队离线暂停。',
        '真实坐标由可信观测/解析得到规范目标键，同一目标重测、坐标复制、换机器、换容器都不能获得新的十次额度。',
        '实际任务先核验目标/权限并预留；真实耗材耗电完成后固定收据和随机结果。恢复同一事务沿用原结果，不能重抽、重扣或重复计次。',
        '产物阻塞或服务器重启时按持久交付记录恢复。账本settle/acknowledge不等于跨库存事务已原子实现；必须另做机器/库存交付对接验证。',
        'I26成功任务、I27捕获和I28终止共用真实目标状态；捕获后不能继续采掘，终止不可复活。安全演算只读观测副本，不提交真实捕获/终止事务。',
        'I29成功构筑创建独立模拟批次，I30稳定、I31终止沿用同一批次；模拟不占真实十次，也不累计舰船发现保底。',
        '知识和已完成实验证据可以按已定规则继承并保留来源；不因此复制坐标资产、封存目标、装置、物料、在研任务或结算奖励。',
        '真实与模拟资源范围保持既定一致；已有物品等概率规则保留，不在本稿改稀有权重、资源池、数量或流体抽样方式。',
        '所有既有物品仅作为复用候选，目录存在不代表制造来源可达；新试样名称只是设计说明，需逐项查注册、标签、材料和前级机器。',
    ]
    read_sources=[CAT,CONTENT,AUDIT,ROOT/'src/main/java/com/sirin/hk3gtl/common/worldbubble/Hk3WorldBubbleLedger.java',
                  ROOT/'src/main/java/com/sirin/hk3gtl/common/worldbubble/Hk3WorldBubbleData.java',
                  ROOT/'src/main/java/com/sirin/hk3gtl/common/recipe/quantum/QuantumStageRecipes.java',
                  ROOT/'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html',
                  ROOT/'doc/HK3GTL-内测5/00_总纲/内测5完整主线方案与树状图_v4.html']
    external=[]
    for p in (ROOT/'src/main/java').rglob('*.java'):
        if p.name in ['Hk3WorldBubbleLedger.java','Hk3WorldBubbleData.java']:continue
        if re.search(r'\bHk3WorldBubble(?:Ledger|Data)\b',p.read_text(encoding='utf-8')):external.append(str(p.relative_to(ROOT)))
    assert not external,('需更新底层接线判断',external)
    e=lambda v:escape(str(v),quote=True)
    anchor='research-s03-'+stamp
    parts=[f'<section id="{anchor}" class="panel"><h2>S03第三阶19课题：世界泡、无人采掘、舰船与虚数观测</h2>',
           f'<p>变更#第三阶接线1 · {e(now.isoformat())}。仅设计讨论。S01/S02/S03合计72项有详细稿，不代表72项已实现；本阶19项尚未定位生产证据入口。</p>',
           '<h3>本轮用户已确认</h3><ul>']
    parts += ['<li>'+e(d['answer'])+'：'+e(d['effect'])+'</li>' for d in decisions]
    parts += ['</ul><h3>进度顺序</h3><p>I24与加强I44原始观测 → WCP/I25坐标 → UAA无人装置 → UED/I26真实任务 → LTA/I32逆向。其后分为舰船工程、真实捕获终止、模拟构筑稳定终止等分支；IOP/I34首次虚数观测 → ILE/S04。舰船是毕业必要建设，但不擅自追加为ILE的研究前置。</p>',
              '<p><b>事件门槛：</b>茧加强千界一乘技术独立于RN研究目录；QOM基础校准不用该技术，正式寻找不同真实世界泡仍须核对。事件授予与研究继承不能混为同一个完成标记。</p>',
              '<h3>当前源码与目录差距</h3><ul>']
    parts += ['<li>'+e(x)+'</li>' for x in findings]
    parts += ['</ul>']
    for r in rows:
        parts.append(f'<details data-topic="{r["id"]}"><summary>{r["id"]} {e(r["title"])} · 接线候选</summary><div style="padding:12px">')
        fields=[('研究前置','、'.join(r['prerequisites'])),('前级投入',r['inputs']),('执行设施',r['experiment_facility']),
                ('取得证据的实际成功事件',r['success']),('研究后正式开放',r['formal_unlock']),('防自锁与越级',r['no_self_lock'])]
        if r['catalog_item_reuse_candidates']:
            fields.append(('已存在目录中的物品复用候选','；'.join(x['name']+'（'+x['id']+'）' for x in r['catalog_item_reuse_candidates'])))
        for label,value in fields:parts.append('<p><b>'+e(label)+'：</b>'+e(value)+'</p>')
        parts.append('<p>这些工序尚未实现；物品复用候选未证明已有可达配方。实验只要求已完成的前置课题及适用事件授权，不要求本课题先研究。</p></div></details>')
    for title,values in [('结算与证据边界',contracts),('仍待讨论或验证',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<p>检查范围：19项与目录完全匹配、无重复；候选设施的研究解锁均为祖先，实验不自锁；引用物品ID存在于当前目录。这不是完整材料/电压/事件/机器/库存闭合证明。</p></section>')
    section='\n'.join(parts)

    class Parser(HTMLParser):
        def __init__(self):super().__init__();self.ids=[]
        def handle_starttag(self,tag,attrs):
            if tag=='details' and 'data-topic' in dict(attrs):self.ids.append(dict(attrs)['data-topic'])
    parser=Parser();parser.feed(section);assert parser.ids==[r['id'] for r in rows]
    before=PLAN.read_text(encoding='utf-8');assert before.count('</body>')==1
    after=before.replace('</body>',section+'\n</body>',1);assert after.replace(section+'\n','',1)==before
    payload={'time':now.isoformat(),'status':'第三阶19项详细讨论稿，非实现','confirmed_this_turn':decisions,'rows':rows,
             'findings':findings,'contracts':contracts,'pending':pending,'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in read_sources},
             'ledger_external_references':external,'anchor':anchor,'game_changed':False}
    log=OUT/('s03-experiment-contracts-'+stamp+'.json')
    decision_file=OUT/('s03-confirmed-decisions-'+stamp+'.json')
    record=ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_第三阶19课题及起步资料与模拟封存裁定.html')
    for p in [log,decision_file,record]:assert not p.exists(),p
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    with decision_file.open('x',encoding='utf-8') as f:json.dump({'time':now.isoformat(),'status':'用户已确认，尚未实现','decisions':decisions},f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第三阶19课题与起步规则确认</title><style>body{{max-width:1120px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}details{{padding:8px;border-bottom:1px solid #536174}}summary{{cursor:pointer}}</style></head><body><h1>第三阶19课题与起步规则确认</h1>
<p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；用户消息原始精确时间未知。</p><h2>用户要求</h2><blockquote>接下来衔接第三阶的19项：世界泡、无人采掘、舰船与虚数观测。</blockquote><p>承接S01/S02详细稿和I44独立起步校准的明确答复。上轮旧版本查找已结束；本轮回到研究设计。结构外观仍暂停，设计收口前不改生产代码。</p>
<h2>本轮原生提问与实际答复</h2>'''
    body+=''.join('<p><b>问题：</b>'+e(d['question'])+'<br><b>答复：</b>'+e(d['answer'])+'</p>' for d in decisions)
    body+=section
    body+=f'''<h2>覆盖关系与实际执行</h2><p>首次真实任务的起步遗留资料改为明确保证产出；不同于舰船档案随机＋有限保底，后者具体20%和第5次仍未批准。初始模拟批次明确允许封存，覆盖初始等待行为未定状态；不扩大为稳定后所有阶段免费维护。原有I44基础校准、茧加强技术、团队证据和付款退款规则保留。</p>
<p>已读取19项目录、此前路线及决策、工业树v5、主线v4、世界泡账本及存档包装、旧量子配方和相关测试源码。测试源码只读，未运行；核验了引用物品和祖先关系，追加计划与结构化方案并回读。src/main文件集合和内容保持不变，未编译、部署、运行游戏，未删除旧配方或旧机器。</p>
<p>八项合并映射及工程验证承载方式仍待答。本轮没有批准新结构、正式研究所名称、舰船十模块或材料/概率/产量数值。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">计划页第三阶完整方案</a> · <a href="2026-09-28_15-10-16-395758_I44独立起步校准裁定.html">I44已确认边界</a></p>
<p>下一步衔接S04的21项，研究虚数锚定、能量态采集、HW工业应用、世界维系和奇观工程；保留各阶段实验→研究→正式工况的边界。</p><footer>变更#1：新增第三阶方案及两项用户裁定记录；保留历史，删除无。</footer></body></html>'''
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8')==after
    assert record.read_text(encoding='utf-8')==body
    assert json.loads(log.read_text(encoding='utf-8'))['rows']==rows
    assert before_source==production_hashes(),'生产文件变化，检查并发写入后再报告'
    validation={'time':now.isoformat(),'topics':19,'current_evidence_topics':0,'complete_unique_coverage':True,
                'design_ancestor_checks':19,'catalog_item_references':sum(len(r['catalog_item_reuse_candidates']) for r in rows),
                'prior_plan_preserved':True,'production_files_unchanged':len(before_source),'compiled':False,'deployed':False,'game_tested':False,
                'record':str(record),'log':str(log),'decision_file':str(decision_file),'anchor':anchor}
    with (OUT/('s03-contracts-validation-'+stamp+'.json')).open('x',encoding='utf-8') as f:json.dump(validation,f,ensure_ascii=False,indent=2)
    print(json.dumps(validation,ensure_ascii=False))


if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
