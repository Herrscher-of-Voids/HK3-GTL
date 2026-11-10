"""变更#1：2026-09-28，第四阶21课题讨论稿与二审/奇观门槛明确答复。
只追加现有计划、JSON及讨论记录；保持生产源码、资源和实例不变。
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'
PLAN=ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
CAT=ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
AUDIT=OUT/'evidence-links-20260928-035524.json'

# 课题|可达输入|实际实验设备|成功事件|正式收益|防自锁与越级
RAW='''
IAA|I34真实虚数初观资料、SPM魂钢加工件、VCA空间组件及普通稳定介质|I16制作锚定试件→I33前级空间接口校准|试件在已有空间工装中完成连接稳定性测试，关联I34观测和制样批次|I35控制器、正式虚数锚定组件及连接试验工况|首份试件不用I35自产件，也不要求W03；不开放终审维度，不宣称操纵整棵虚数之树
ESC|前三态采集运行回执、I34联系资料、I35实际锚定检测记录及前级探测工装|前级GT制场响应试件→I33受控能流响应检测|完成前三态与虚数联系的实际对照，记录场响应；试验不产可用能量态或免费HW|I01-4控制器、能量态探测器及第四态采集工况|四阶塔首机和探测器不要求该塔自产能量态，也不要求尚未开放I38整流件
HER|I01-4实际能量态采集记录、前级整流工装和隔离负载|前级GT制整流试件→I33计量与隔离测试|真实消耗测试输入并测量能流/损耗，完成安全隔离；测试不向个人账户任意充值|I38控制器与能量态计量、整流、合法HW入账工况|不要求I38先给自身充值；保留前期HFB等已开放注入路线，HER不是全体HW余额的总开关
CED|I38成功整流及实际HW入账记录、已有可用HW负载和绑定人授权|已可用HW负载实际耗能测试→I32收支/授权记录校核|实际负载扣费与产能回执对应，核验付款UUID、有效运行量和拒绝无授权操作；余额截图不算证据|I41控制器及基础负载登记、状态查看、授权范围内手动开停管理|不要求I41先调度；团队研究不自动取得队友HW账户权限，GTMThings无线EU不视作HW同一账户
WME|I35实际锚定、I36稳定场、I38产能与I41负载记录，已有模拟稳定资料|I32模型分析→I33前级局部维系试件验证|真实完成局部扰动响应、停止与恢复验证并关联输入/能流记录；测试局限于装置和样件|I37控制器与世界维系原型试验工况，实际运行后产生维系报告|不要求I37先运行；不破坏玩家真实世界来制造实验事件；起步试件不用奇观材料
WMS|I37实际维系原型的材料工况记录、I15/I16可达魂钢、前级可得加工介质|前级GT/I16制造复合试片→I32材料工况分析|试片真实制造并完成维系条件下的适配检测，不能将检测件当正式复合材料使用|I40控制器及起步复合材料工况；导能、约束、重构、认知分支各自保留材料和适用核心研究条件|首机不能用I40自产复材或任一奇观自产材料；WMS不一键赠送尚未研究核心的应用，分支精确映射待审
WPF|I40已能制造的起步复合材料、SPM加工件、前级模具|I16连接与承载试件加工→I32分析|实际完成接口、公差与承载试片检测，关联I40产物批次；试片不是奇观控制器|I42控制器、按具体奇观区分的预制工序；正式奇观建造仍受专项课题及二审控制|I42首机不用自产预制件；通用准备不等于所有奇观已可建，具体高阶配方仍核对上游研究
CEE|I42实际预制样件、I37维系记录及前级测量工装|I32基准件与测量方法校准|真实检测已知基准件，并验证判定规则能区分合格/不合格样件；只形成验收方法证据|I43控制器、工程测试与验收记录方法；奇观运行证明必须另核对对应已成型本体和真实工况|不要求I43检验自己；研究完成和校准报告不能代替任何奇观的运行证明，也不另开终审入口
URE|I21真实大型供能回执、I40起步材料与已有热管理成果|I21受控负载试验→I32材料/热收支检测|真实高负载批次和材料安全检验关联，实际耗材耗电；不依赖待开放I22|I22独立控制器与究极供能工况|首机不要求其自产能源/奇观材料；具体供能和风险参数另审，不因研究通过免除运行消耗
HCCO|前序研究档案、已真实完成的交流事件记录与文明工程资料|I43协作档案与工程来源验证|核验研究和交流事件确已发生，关联资料来源并完成工程校核；独立或拒绝合作路线均可提供符合既定条件的交流记录|W01专项建造知识与协作档案验收方法；正式建造/运行还须二审通过|不要求W01先产文明档案；不强制同意某阵营、不要求看全互斥回答；沟通完成不等于合作立场
AIM|I09–I16魂钢连续生产、CPT等已开放电路路线的真实批次与RCA解析资料|I43工业生产链验证|核验实际投入产出、批次来源与连续工况，排除复制报告和未掌握电路|W02专项建造知识与低阶部件/电路扩产工况方法；二审后可正式建设运行|不要求W02先扩产；重构白名单、已解锁制造技术和成本继续生效，不扩大为无限复制
SEM|TCA已解锁雷核心电磁模块、前级极化试件和供电/冷却记录|前级电磁工况实际运行→I43检测|实际电磁响应及供能/冷却回执通过检测，试件不充当W04量产材料|W04专项建造知识与持续电磁场/极化工况验收；二审后建设运行|首座W04不消耗仅由自身制造的极化材料；不以持有雷核心代替电磁运行记录
IFF|WCA已开放流动工艺、GPR气体净化、HLC换热的真实记录|前级流路运行→I43输运与热收支验证|真实输入输出、循环补液和热交换结果可追溯，明确损耗，不靠库存差额推断来源|W05专项建造知识及流体输运/换热验收方法；二审后建设运行|首机不用W05自产介质；理想流体不等于复制流体或零成本能源，不能虚报闭环收率
CCF|ICA冰核心冷却工艺实际记录、前级材料与制冷介质|已有冷却工况→I43低温样件检测|真实完成低温处理并核对介质和能源消耗，样品来源与温控记录对应|W06专项建造知识及低温凝态工况验收；二审后建设运行|不要求W06先产深冷材料；不自定绝对零度或新的现实物理参数
IAR|I35锚定、I37维系实际记录、已可达空间组件|I43空间连接和维系记录验证|核验既有锚定设备的真实工况与局部扰动响应，不提前运行文明级锚定环|W03专项建造知识及大范围锚定验收；二审后建设运行|首座不用W03自产空间材料；新作用范围与耗能待定，不借锚定绕过终审资格
MRA|既有固体后处理、液态介质再生和GPR气体净化回执及实际残渣|I43多支线回收收支验证|核验真实投入、回收与不可回收残渣，排除重复统计同一批次；试验不额外生成回收物|W07专项建造知识及材料再生工况验收；二审后建设运行|不要求W07先回收；损坏燃料棒不恢复为可用棒，不从回收循环产生净免费能源，不新加灵魂科技
SFF|FCA已开放高温工艺、I22真实供能记录与前级铸造试件|前级热工运行→I43热工及材料验证|实际完成高温加工、安全冷却和能耗回执核验，试件不是W08的正式产物|W08专项建造知识及极热熔铸验收；二审后建设运行|首座不用W08自产极限材料，基础魂钢仍走I09–I16；材料温度和产量不在本稿定稿
GSF|GCA/SEK已有引力压缩工况、同批模拟构筑稳定记录与前级高密度试件|I33已有压缩工况→I43检测|实际完成压缩响应并关联模拟种子工艺记录，试验不产文明工程奇点|W10专项建造知识与高阶奇点工况验收；二审后建设运行|I29早期种子不依赖W10；首座W10不要求自产奇点；不授予伊甸之星时间加速能力
ECB|BCA/JOK已开放能流隔离、I36稳定场与前级约束样件记录|已有约束工况→I43能流隔离验证|实际完成开启/解除约束和输入输出计量；验证不把抑制能量返充账户|W12专项建造知识与大范围约束工况验收；二审后建设运行|不要求W12先运行；基础I36保留用途，约束不发免费EU/HW
CLE|崩坏能/量子/虚数三领域可追溯研究与实验、I37运行、CEE验收方法及HCCO研究成果|I43前级研究设施接口与资料联调验证|以现有S04可提供的接口试件和真实资料完成联调，仅输出工程证据，随后在S04正常支付并研究|S05独立研究所及必要功能件，提供16个课题槽位；不与W09共用实体|不要求W09或W01已经运行，不用S05先研究自身首机材料；CLE本身不是奇观专项，不因HCCO建造锁二审而反锁S05研究
ELC|I41已登记负载、I37及其他已可运行设备的实际HW扣费与暂停记录|I41基础手动控制工况→I32多负载收支分析|实际运行与手动开停产生可核对的多设备时间线，验证未授权/余额不足时不继续推进；不先启用待解锁自动优先级|I41负载优先级排序与告警策略；基础登记、手动开停保留|不增加账户容量/距离/吞吐上限，不制造负余额；测试限制仅属试验工况，不强制耗尽玩家全账户
'''

GATES={
 'IAA':['ILE','VCA','SPM','DKE'],'ESC':['IAA','GSC','DKE'],'HER':['ESC','DKE'],
 'CED':['HER','LTA','HFB'],'WME':['IAA','CED','RAT','LTA','DKE','SWS'],
 'WMS':['WME','SPM','LTA'],'WPF':['WMS','SPM','LTA'],'CEE':['WPF','WME','LTA'],
 'URE':['LRE','WMS','LTA'],'HCCO':['CEE'],'AIM':['CEE','SPM','CPT','RCA'],
 'SEM':['CEE','TCA'],'IFF':['CEE','WCA','GPR','HLC'],'CCF':['CEE','ICA'],
 'IAR':['CEE','IAA','WME'],'MRA':['CEE','SFR','GPR','SMR'],'SFF':['CEE','FCA','URE'],
 'GSF':['CEE','GCA','SEK','SWS'],'ECB':['CEE','BCA','JOK','RAT'],
 'CLE':['CEE','WME','HCCO','ILE'],'ELC':['CED','WME','LTA'],
}
WONDERS={'HCCO':'W01','AIM':'W02','IAR':'W03','SEM':'W04','IFF':'W05','CCF':'W06','MRA':'W07','SFF':'W08','GSF':'W10','ECB':'W12'}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def production_hashes():
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'src/main').rglob('*')) if p.is_file()}


def main():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp=now.strftime('%Y%m%d-%H%M%S-%f')
    production_before=production_hashes()
    topics={r['id']:r for r in json.loads(CAT.read_text(encoding='utf-8'))['topics']}
    audit=json.loads(AUDIT.read_text(encoding='utf-8'))
    for path,sha in audit['source_hashes'].items():assert digest(ROOT/path)==sha,('原审计已过期',path)
    ar={r['id']:r for r in audit['rows']}

    def ancestors(key,chain=()):
        assert key not in chain,('研究环',chain,key)
        out=set()
        for p in topics[key]['prerequisites']:out.add(p);out.update(ancestors(p,chain+(key,)))
        return out

    rows=[]
    for line in RAW.strip().splitlines():
        short,inputs,facility,success,unlock,guard=line.split('|');key='RN-'+short;n=topics[key]
        assert n['lab']==4
        gates=['RN-'+x for x in GATES[short]]
        assert set(gates)<=ancestors(key),(key,set(gates)-ancestors(key))
        rows.append({**n,'inputs':inputs,'experiment_facility':facility,'success':success,'formal_unlock':unlock,
                     'no_self_lock':guard,'experiment_recipe_requirements':n['prerequisites'],'facility_and_input_unlocks':gates,
                     'wonder':WONDERS.get(short),'research_requires_second_judgment':False,
                     'formal_wonder_build_run_requires_second_judgment':short in WONDERS,
                     'current_evidence_refs':ar[key]['evidence_refs'],'current_gate_refs':ar[key]['gate_refs'],
                     'status':'详细接线提案，未实现；二审时机单独已确认'})
    assert len(rows)==21 and len({r['id'] for r in rows})==21
    assert {r['id'] for r in rows}=={k for k,n in topics.items() if n['lab']==4}
    assert not any(r['current_evidence_refs'] for r in rows)
    assert sum(r['formal_wonder_build_run_requires_second_judgment'] for r in rows)==10
    for r in rows:assert set(r['experiment_recipe_requirements'])<=ancestors(r['id'])

    decision={'question':'第四阶奇观专项课题与二审怎样衔接？I35至I43等前置工业设施可提前准备。',
              'answer':'二审前可预研专项课题，二审通过后开放奇观正式建造与运行（推荐）',
              'status':'用户已确认，尚未实现',
              'effect':'奇观专项研究完成与二审通过分别检查；前置工业设施、研究证据和方法学试验不反锁到尚未建成的奇观。',
              'scope':'奇观研究与正式建造/运行时机；不改变二审内容，不代替具体结构审批，不限制普通研究所为奇观。'}
    findings=[
        '现有HonkaiWirelessNetwork按个人UUID保存BigInteger余额，提供全额扣款tryExtractExact；Hk3PlayerGridEnergyTrait操作的是GTMThings无线EU。两者不能合并为同一研究支付或供能余额。',
        '现有Hk3HonkaiNetworkInjectorMachine在成功输出回调向绑定人的账户入账，可作为前期HW供应代码复用候选；不能将HER新增整流研究改成该既有能力的总门槛。',
        '第四阶21项在本轮来源哈希复核后的审计中均未定位生产证据入口，也未定位这些RN键的直接生产门槛；旧奇观类存在不能替代新W系列接线证据。',
        '研究开始仍由MAX＋topic.tier计算请求功率；实验设施祖先可达不等于S04能供电，CLE首研究和首台S05必须独立核对电压、端口与材料。',
        '目录HER/CED/ELC仍含玩家可见HKE字样；本稿按用户既定单位HW和HW/t表达，未改目录、账户数值或存档键，实施时应同步显示。',
        'I40四类复合材料在设计中已有分支，但不能由WMS一次赠送所有未掌握的核心能力。首机和起步分支用前级可达料，其余分支逐配方核对材料/核心研究。',
        '本阶10座奇观的研究证据均来自已开放普通工业和I43方法验证；正式奇观运行报告须在二审通过后的真实本体工况另行取得。',
    ]
    contracts=[
        'HW是现有崩坏能容量单位的显示改名，HW/t为速率；个人UUID和数值不变，研究共享不自动合并私人财产。',
        '整流的物料/能源转换成本与无线传输分开：可以有明确工艺消耗，不以整流损耗冒充无线距离损耗、容量或吞吐上限。',
        'CED开放基本登记和授权范围内的手动管理；ELC另开自动排序与告警。I41不是所有机器无线供能的强制中转点。',
        'HW产能证据须关联真实输入、工序和入账收据；用能证据须关联实际扣费和有效工作，不凭余额、模拟查询或只读测量自证。跨机器/账户结算和重试仍需实现验证。',
        '研究前样件、方法测试报告、研究完成、奇观实际运行证明使用不同语义。I43校准成功不得发出W系列本体验收报告。',
        '二审前研究按前级工业实验取得证据；奇观正式建造/运行需同时满足专项研究和二审标记，不能只检查一项或用研究完成代替二审。',
        '实现候选为在正式控制器/关键装配入口和运行许可两端检查门槛；如何落实正式建造的具体配方范围须在配方接线时逐项列出，不自行禁止放置普通装饰方块或清理既有建筑。',
        '奇观运行与验收分别按各自功能核对实际输入输出，不能统一为持有控制器、站在结构旁或通用空转若干tick。运行阈值、批次数和故障恢复规则另审。',
        'I42可承接前置准备工序，但各奇观专用配方、核心应用及最终建造权限仍按对应课题与二审分别核对；不使用万能构件绕过全部材料支线。',
        'S05和W09为独立实体。CLE研究不要求W09成型或W01先运行；HCCO研究知识可提前取得，W01的建造许可才等待二审。',
    ]
    pending=[
        '此前八项工艺合并映射和研究所工程验证承载方案仍待答；本稿不覆盖或默认批准。',
        '个人HW授权的操作角色、撤权/离隊的处理及多账户调度范围另行明确；当前候选试验使用明确授权的绑定人账户，不默认获得团队全部余额。',
        '四类复合材料的精确原料/核心依赖、I38整流产额、各机EU与HW成本和电路七支线数值仍待配方收口。',
        '奇观运行证明的有效期、拆除/搬迁后的再验要求、队伍变化后的工程归属，需要与第五阶毕业资格一起确认；不从知识继承推导实体工程继承。',
        '二审通过的权威事件标记及混队查询应接入叙事系统；不能以当前旧终局毕业标记、物品或聊天文字冒充。',
        '本轮不裁定研究所S01至S04的正式名称，不审批新外观，不把现有69座候选预览视为已批准结构。',
    ]
    source_paths=[CAT,AUDIT,
        ROOT/'src/main/java/com/sirin/hk3gtl/common/capability/HonkaiWirelessNetwork.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/trait/Hk3PlayerGridEnergyTrait.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/energy/Hk3HonkaiNetworkInjectorMachine.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchStartService.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesWonderStage.java',
        ROOT/'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html',
        ROOT/'doc/HK3GTL-内测5/00_总纲/内测5完整主线方案与树状图_v4.html']
    e=lambda x:escape(str(x),quote=True);anchor='research-s04-'+stamp
    parts=[f'<section id="{anchor}" class="panel"><h2>S04第四阶21课题：虚数工程、HW调度与奇观预研</h2>',
           f'<p>变更#第四阶接线1 · {e(now.isoformat())}。仅设计讨论，未改游戏。前四阶合计93项有详细稿，不代表93项已实现。</p>',
           '<h3>本轮已确认：奇观预研与二审分开</h3><p>'+e(decision['answer'])+'。'+e(decision['effect'])+'</p>',
           '<p>前级锚定→能量态采集→HW整流→授权调度→维系原型→奇观材料→预制构件→验收方法。各奇观使用前级工况提供研究证据，二审后才进行正式建造与运行验收；CLE使用前级工程资料开放S05，不要求W09先运行。</p>']
    parts.append('<h3>当前源码与目录核对</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in findings);parts.append('</ul>')
    for r in rows:
        parts.append(f'<details data-topic="{r["id"]}"><summary>{r["id"]} {e(r["title"])} · 接线候选</summary><div style="padding:12px">')
        fields=[('研究前置','、'.join(r['prerequisites'])),('前级投入',r['inputs']),('实际实验设施',r['experiment_facility']),
                ('证据成功事件',r['success']),('正式收益',r['formal_unlock']),('防自锁与越级',r['no_self_lock'])]
        if r['wonder']:fields.append(('二审条件','本专项课题可提前研究；'+r['wonder']+'正式建造和运行须另外通过二审。'))
        for k,v in fields:parts.append('<p><b>'+e(k)+'：</b>'+e(v)+'</p>')
        parts.append('<p>新工序仍为待实现提案；研究依赖检查不代替完整配方、物料、电压、事件和游戏运行验收。</p></div></details>')
    for title,values in [('接线与验收边界',contracts),('未定与未验证',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<p>静态核对：21项完整且唯一，设施解锁均为对应课题祖先，10座奇观的预研和正式建造二审门槛分列；源码未变。未做游戏或结构测试。</p></section>')
    section='\n'.join(parts)
    class Parser(HTMLParser):
        def __init__(self):super().__init__();self.ids=[]
        def handle_starttag(self,tag,attrs):
            if tag=='details' and 'data-topic' in dict(attrs):self.ids.append(dict(attrs)['data-topic'])
    parser=Parser();parser.feed(section);assert parser.ids==[r['id'] for r in rows]
    before=PLAN.read_text(encoding='utf-8');assert before.count('</body>')==1
    after=before.replace('</body>',section+'\n</body>',1);assert after.replace(section+'\n','',1)==before
    log=OUT/('s04-experiment-contracts-'+stamp+'.json')
    decision_path=OUT/('s04-confirmed-decision-'+stamp+'.json')
    record=ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_第四阶21课题与二审后奇观建造裁定.html')
    for p in [log,decision_path,record]:assert not p.exists(),p
    payload={'time':now.isoformat(),'status':'设计细化，非实现','confirmed_this_turn':decision,'rows':rows,'findings':findings,
             'contracts':contracts,'pending':pending,'source_hashes':{str(p.relative_to(ROOT)):digest(p) for p in source_paths},'game_changed':False,'anchor':anchor}
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    with decision_path.open('x',encoding='utf-8') as f:json.dump({'time':now.isoformat(),**decision},f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第四阶21课题与奇观二审门槛</title><style>body{{max-width:1120px;margin:30px auto;padding:20px;font:16px/1.8 'Microsoft YaHei';background:#14202e;color:#e4ecf5}}a{{color:#9ddfff}}details{{padding:8px;border-bottom:1px solid #536174}}summary{{cursor:pointer}}</style></head><body><h1>第四阶21课题与奇观二审门槛</h1><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong。用户原消息精确时间未知，记录时间不代替原消息时间。</p>
<h2>用户要求与实际答复</h2><p>用户要求“继续”，承接第三阶19项，进入第四阶21项；结构外观保持暂停，设计收口前不修改生产代码。</p><p><b>问题：</b>{e(decision['question'])}<br><b>答复：</b>{e(decision['answer'])}</p><p>本条明确此前奇观专项研究与二审先后未定的边界；不重写二审内容，不代替结构审批。上一阶首次任务保证起步资料、初始模拟批次可封存等已确认决定保留。</p>
{section}
<h2>实际执行及下一步</h2><p>读取21项课题、前序设计与工业/主线文档，核对个人HW网络、无线EU适配、前期注入器、研究功率和旧奇观注册。保存21项JSON、明确答复和现有计划页追加段落；检查覆盖、祖先关系、10座奇观门槛分离并回读。src/main文件集合及内容哈希未变，没有编译、部署或游戏测试，没有修改任何生产门槛。</p>
<p>下一步处理第五阶7项：文明档案、统御网络、研究加速、世界泡创生、文明验收和终审朝觐等；届时收口运行证明与毕业资格边界。剩余数值、结构和跨系统授权未因本轮讨论自动定稿。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">第四阶完整方案</a> · <a href="2026-09-28_15-38-17_第三阶19课题及起步资料与模拟封存裁定.html">第三阶已确认记录</a></p><footer>变更#1：新增第四阶讨论与本轮裁定；保留历史，删除无。</footer></body></html>'''
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8')==after
    assert record.read_text(encoding='utf-8')==body
    assert json.loads(log.read_text(encoding='utf-8'))['rows']==rows
    assert production_before==production_hashes(),'生产文件发生变化，需检查并发写入'
    validation={'time':now.isoformat(),'topics':21,'existing_evidence_topics':0,'design_ancestor_checks':21,'wonder_gate_checks':10,
                'coverage_matches_catalog':True,'html_topic_count':len(parser.ids),'prior_plan_preserved':True,
                'production_files_unchanged':len(production_before),'compiled':False,'deployed':False,'game_tested':False,
                'record':str(record),'log':str(log),'decision_file':str(decision_path),'anchor':anchor}
    with (OUT/('s04-contracts-validation-'+stamp+'.json')).open('x',encoding='utf-8') as f:json.dump(validation,f,ensure_ascii=False,indent=2)
    print(json.dumps(validation,ensure_ascii=False))


if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
