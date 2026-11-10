"""变更#1：2026-09-28，追加第二阶28课题的证据、权限与反自锁讨论稿。
仅写现有计划页、讨论记录和审计JSON；不改生产代码，不注册试样或配方。
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/research-migration-20260928'
PLAN = ROOT / 'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
CAT = ROOT / 'src/main/resources/data/hk3gtl/research/research_catalog.json'
AUDIT = OUT / 'evidence-links-20260928-035524.json'

# 各行：课题、输入、实验设施、真实成功条件、研究收益、反向依赖防线。
# 新试样与工况均为设计描述；不代表已有注册物品或已获用户批准。
RAW = '''
SSC|I01-1液态采集回执、SPM后可制造的魂钢场约束试件、前级探测元件|前级GT制作试件→I02相态响应检测|真实完成液态样本与约束试件的响应检测，关联原采集和制样批次|I01-2控制器、固态探测器及固态采集工况|首个试件不得使用固态崩坏能；造塔与造探测器均不能要求二阶塔自产物
CCE|I01-2真实固态样本、前级晶种载体和普通结晶介质|前级GT小批结晶→I02试晶检测|真实结晶试样经成分和晶格检测形成有效回执；试晶不具有核心能力|I08控制器、基础结晶与供各核心课题使用的未定性结晶样件|不得用I08正式晶体制造I08首机；CCE不自动解锁九种完整核心
CFR|HFB后可得液态燃料与既有浓缩耗材|沿用I17液态燃料浓缩成功入口|现有浓缩配方实际输出提交成功；证据可提前记录，研究仍核对SSC和HFB|后续固态精制、浓缩燃料及I18对应燃料棒工况；保持HFB后的液态起步浓缩可用|不得将现有初次浓缩反锁到CFR；不将记录证据等同研究完成
MRE|CFR浓缩燃料安全试件，I19真实运行、HLC换热和SFR失活棒处理回执|前级GT制隔离燃料试件→I02检测并关联前序回执|试件实际完成受控热响应和密封检测；核验已有发电、换热、后处理批次|I20独立控制器与中型反应堆燃料工况|不要求I20先发电；原始I19和新鲜冷却启动路线保留
CPT|MCE电路层、SPM魂钢载体、前级可得封装和绝缘介质|前级GT/GTL封装设备制试件→I02电气与热工况检测|封装试件完成导通、绝缘与热循环检测；检测件不是可用于造首机的新级电路|正式精密封装与终检工况，承接I50职责的候选位置为I16|CPT首枚试件与正式工况首套设备都用前级电路；MCE前级种子封装不回锁
ERA|I36基础运行回执、CCE基础晶体与固态约束试件|I36基础场运行→I02对比试件检测|对同一基准记录强化前后的稳定偏差，真实耗材耗电运行，未启用待解锁强化模式|既有I36的强化介质及后续已研究核心适配工况|初次ERA不要求空核心或约束核心；高级核心槽后续逐项检查对应核心研究
GSC|液态与固态采集回执、前级魂钢封闭场试件、MRE后的可用供电|前级GT制气相约束试件→I02相态对照|真实完成液固记录与试件的封闭场响应对照；试验不产可用气态崩坏能|I01-3控制器、气态探测器及气态采集工况|首机和首个探测器不能消耗三阶塔气态产物，不能要求PCE
PCE|I01-3真实气态样本、HLC已掌握冷却介质与热管理记录|前级GT受控换热试件→I02量热检测|封装气态样本完成受控相变与能量损耗测量，不向电网返还未定量的试验能量|I23控制器、气固转换及明确损耗的正式释能工况|不要求I23先运行；保留已能启动的冷却来源，不凭样品库存授予
GPR|既有工艺真实排气、前级过滤介质和新鲜洗涤介质|前级GT小批洗涤→I02封装气样成分检测|比较真实进出气样和过滤残渣，关联生成排气的批次；新鲜气体用于工况启动|分气种净化与过滤介质回用，I52职责合并候选为I05|必须先核对排气生成配方可达；不得为了GPR强加未列入前置的PCE；回收不是第一份气体来源
FCA|I08未定性结晶样件、普通GT热源与已可得金属对照片|前级GT热响应试验→I02检测|试晶在受控热输入下形成可重复检测回执；消耗或封存试晶，不能直接交付正式炎核心|I08仿制炎核心制造及其专用金属加热配方入口|测试热源不使用炎核心；高温成品的其他材料与工艺研究仍逐项保留
ICA|I08未定性结晶样件、HLC可用冷却介质与普通GT制冷工装|前级GT低温试验→I02检测|实际记录降温及回温响应，冷却介质收支与试晶批次对应|I08仿制冰核心制造及特殊金属冷却工况|初次冷却不要求冰核心；不把热量转移作为免费冷却源
RCA|I08未定性结晶样件、CPT前序已掌握构件与结构对照样本|前级GT制结构对照试件→I02检测|真实完成已知构件结构对照；不在试验中复制新物品或授予未掌握电路|I08仿制理核心、理构重构阵列；具体电路另需正常技术路线、样本解析和白名单|不增加VAK前置；不因持有MAX电路一键掌握全部电压；核心不逐次消耗的既定规则保留
VCA|I08未定性结晶样件、ERA已有稳定场与前级定位工装|I36已开放场工况→I02定位误差检测|同一基准下完成空间定位偏差测量，记录工装、场与试晶来源|I08仿制空核心制造、已定空间组件工艺入口|不使用空核心或千界一乘自证；不开放终审维度或任意传送权限
ECA|I08未定性结晶样件、CPT已有封装回路与隔离载体|前级GT隔离计算试件→I02执行结果检测|真实完成固定测试输入、结果校验及停止指令；记录电耗和输出，异常不算成功|I08仿制侵蚀核心制造及后续受控演算试验资格|研究完成不立即启用ERM加速；不触及真实文件，也不依赖加速模块制造首枚核心
GCA|I08未定性结晶样件、前级GT场发生器与普通压缩对照试件|前级GT受控场试验→I02形变检测|检测有场/基准条件下试件的响应差异，形成可追溯批次|I08仿制岩核心制造与引力压缩工艺入口|不用伊甸之星、黑洞或奇点产品制样；不暗加ERA为必需前置
BCA|I08未定性结晶样件、ERA稳定场与可用能流隔离回路|I36已有场工况→I02隔离前后检测|真实测量同一输入下能流传递与抑制效果，完整记录消耗与残余输出|I08仿制约束核心制造及受控能流隔离工况|不要求约束核心自证；被抑制的能量不转化为免费EU/HW
TCA|I08未定性结晶样件、CPT封装线圈与前级GT电磁工装|前级GT电磁调制试验→I02电气检测|真实完成既定脉冲输入和输出响应测量，输入电力照常消耗|I08仿制雷核心制造与电磁工艺模块入口|不用雷核心或后续超导电磁奇观制样；不将雷属性等同无源发电
WCA|I08未定性结晶样件、I01-3气态样本、前级流动工装|前级GT封闭流路试验→I02气样及流动对照|实际消耗测试介质并记录压差/流量响应；回收部分与损耗分别记账|I08仿制风核心制造及理想流体工艺模块入口|不要求风核心、未来风之奇观或GPR已完成；不能无损返还全部介质
DKE|CPT封装件、SPM魂钢精密件、VCA已可造的空核心和隔离工装|前级GT/GTL装配设备→I02隔离封装检验|真实完成核心封装、接口与安全停止检测；试验装配体不能当作成品神之键|I33控制器、神之键部件装配基础工况；四把神之键分别受专项课题控制|不要求I33造自己的首份证据；使用VCA已可造核心，不额外要求全部九核
VAK|RCA已可造理核心、I33基础装配件、已掌握的结构档案|I33受限构造测试工况|验证既有白名单结构及控制回路，输出测试记录；不产出白名单外成品|仿制虚空万藏制造及前文明档案研究许可|不作为RCA阵列或普通电路重构的新增前置；档案许可不直接完成其他课题
CJK|VCA已可造空核心、I33基础装配件、前序空间测量工装|I33空间组件校准工况|完成同一已知基准坐标的稳定校准与回执提交，试件不能代替正式神之键|仿制千界一乘、I44信标和I45静止列车的控制器及相应工况|首份证据不使用I44/I45；神之键配方不逐次消耗，终审维度排除
SEK|GCA已可造岩核心、I33隔离装配件与前级压缩试件|I33受控压缩测试工况|在安全范围实际完成压缩与释放对照；试验输出仅为检测件|仿制伊甸之星制造、对应引力模块工况；奇点和模拟世界泡仍各受后续课题控制|不授予时间加速；实验不产正式奇点，也不要求先造伊甸之星
JOK|BCA已可造约束核心、I33装配件与既有隔离回路|I33能流隔离测试工况|固定输入下完成约束开启/解除的回路检测，结算实际能耗|仿制犹大的誓约制造与对应约束工艺入口|不要求成品犹大；不从抑制能量创造电力或补充HW余额
QOM|CJK后可制造千界一乘及坐标校准设备、已知合法基准坐标|I44/I45已开放坐标校准工况，具体记录端待定|真实完成校准并提交异常观测回执；异常事件可复现，不能只打开界面或凭物品授予|I24控制器与首次量子观测方法|不反用I24/I25作为首份证据，不要求世界泡采掘或捕获；记录端及确定性触发办法待审
QLE|I24首次成功量子观测的原始记录与设备来源|I24正式初次观测完成回调；S02随后正常研究|观测实际完成并保存回执即满足该项实验来源；不另加重复观测或二次交样|S03控制器及必要功能件，完整坐标解析仍在S03研究|S03首机不用世界泡采掘材料；S02必须能供给本课题用电，不能只按tier数值假定可供电
SSQ|I14/I15/I16不同真实批次的魂钢与工艺回执，必要时附I13包覆来源|既有加工完成记录→I02质量对照检测|不同批次的检验结果可关联其生产环节；同一批回放或复制报告不增加样本数|对应I13至I16的明确质量改良工况，采用逐配方收益而非全局无限倍率|不要求改良后的工艺先产样；具体批次数、材料收率和代价未定，不凭研究名称自动减耗
CQS|CPT已开放封装件、GSC后气态隔离介质、既有电路样品|基础封装工况制样→I02隔离压力与电气检测|真实完成封装工况扩展试验并记录样品性能；不消耗尚未能制造的高一电压种子|基板、蚀刻、封装的高阶工况，合并候选为I12/I16分工|普通机器用同级电路标签；系列升级用具体上一形态；每级首枚仍需前级设备制造
ERM|ECA已可造侵蚀核心、CPT控制回路、同一固定演算任务及已有普通研究结果|S02独立隔离演算验证候选；随工程验证承载方案待定|比较普通与核心辅助演算的真实结果、耗时和停止边界；通过仅记实验，不返还研究点|S02至S05可安装并启用侵蚀研究加速模块，具体倍率与耗能单列待审|不能用已加速研究给自己开锁；不改计算机产点；验证阶段不加速实际课题
'''


def hashes(paths):
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    catalog = json.loads(CAT.read_text(encoding='utf-8'))['topics']
    topics = {r['id']: r for r in catalog}
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    auditrows = {r['id']: r for r in audit['rows']}
    # 已有源码证据只有在原审计来源未变时才能沿用。
    for name, sha in audit['source_hashes'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, ('原审计已过期', name)
    production_paths = sorted(p for p in (ROOT / 'src/main').rglob('*') if p.is_file())
    production_before = hashes(production_paths)

    def ancestors(key, chain=()):
        assert key not in chain, ('前置环', chain, key)
        result = set()
        for parent in topics[key]['prerequisites']:
            result.add(parent)
            result.update(ancestors(parent, chain + (key,)))
        return result

    # 校验选定的实验设施/输入的研究解锁在祖先中，不将其冒称物料闭合检查。
    facility_gates = {
        'SSC':['DMT','SPM'], 'CCE':['SSC'], 'CFR':['HFB'], 'MRE':['SRE','HLC','SFR','CFR'],
        'CPT':['SPM','MCE'], 'ERA':['RAT','CCE'], 'GSC':['SSC','MRE'], 'PCE':['GSC','HLC'],
        'GPR':['GSC','SMR'], 'FCA':['CCE'], 'ICA':['CCE','HLC'], 'RCA':['CCE','CPT'],
        'VCA':['CCE','ERA'], 'ECA':['CCE','CPT'], 'GCA':['CCE'], 'BCA':['CCE','ERA'],
        'TCA':['CCE','CPT'], 'WCA':['CCE','GSC'], 'DKE':['SPM','CPT','VCA'],
        'VAK':['DKE','RCA'], 'CJK':['DKE','VCA'], 'SEK':['DKE','GCA'], 'JOK':['DKE','BCA'],
        'QOM':['CJK'], 'QLE':['QOM'], 'SSQ':['SPC','SRA','SPM'], 'CQS':['CPT','GSC'],
        'ERM':['ECA','CPT','ALE'],
    }
    rows = []
    for line in RAW.strip().splitlines():
        short, inputs, facility, success, unlock, guard = line.split('|')
        key = 'RN-' + short
        n = topics[key]
        assert n['lab'] == 2
        required = ['RN-' + p for p in facility_gates[short]]
        assert set(required) <= ancestors(key), (key, set(required) - ancestors(key))
        refs = auditrows[key]['evidence_refs']
        rows.append({**n, 'inputs': inputs, 'experiment_facility': facility, 'success': success,
                     'formal_unlock': unlock, 'no_self_lock': guard,
                     'experiment_recipe_requirements': ['RN-HFB'] if short == 'CFR' else n['prerequisites'],
                     'facility_and_input_unlocks': required,
                     'current_evidence_refs': refs, 'current_gate_refs': auditrows[key]['gate_refs'],
                     'status': '已有证据入口；正式收益与团队记账待接' if refs else '实验接线候选，未实现',
                     'approval': '细化提案，不将继续视为逐项批准',
                     'new_names_are_descriptions': True})
    assert len(rows) == 28 and len({r['id'] for r in rows}) == 28
    assert {r['id'] for r in rows} == {r['id'] for r in catalog if r['lab'] == 2}
    for r in rows:
        assert set(r['experiment_recipe_requirements']) <= ancestors(r['id'])
        assert all(r[k] for k in ['inputs','experiment_facility','success','formal_unlock','no_self_lock'])

    pending = [
        '已发问待答：I46/I47/I52→I05，I48→I12，I49/I50→I16，I51→I11，I53由I16制壳并由I33装配校准。用户仅要求先看方案。',
        '已发问待答：ALE/OPR是否由S01独立工程验证占用已有槽位、耗电完成；ERM若沿用同机制仍需对应确认，不能直接开启研究所万能实验。',
        '本稿待审：QOM异常记录放I44信标、I45静止列车或两者联动中的哪一端；本文不增加双机必需门槛。',
        '本稿待定：九类核心试验的具体配方、应用配方清单、SSQ批次阈值与收益、ERM倍率和耗能、电路七支线材料；不自动定稿。',
        '工程校核待做：气体排放来源、每个实验的准确设备配方类型/端口、研究供电与首机材料；研究图无环不等于这些已通过。',
    ]
    rules = [
        '研究目录仍为100项；本轮细化S02的28项，加上上一轮S01的25项共53项有详细讨论稿，不代表53项可玩。',
        '已有CFR浓缩证据沿用，其他27项尚未定位真实生产证据入口。RCA已有部分重构门槛并不代表其首份证据已接通。',
        '实际实验成功才记证据，证据与研究支付、完成及正式配方门槛分开；持有成品、复制报告、模拟匹配和输出堵塞不算完成。',
        '按已定规则固定实验机器的研究团队，记录原始机器/配方/批次/时刻，成功回调去重；离线实验可记账，不能回退成最近玩家归属。',
        '九类核心共享基础结晶来源，各自有不同的响应试验和配方权限；基础结晶不直接赠送任何成品核心。',
        '理核心重构遵循2026-09-22已确认边界：正常技术路线已掌握、样本解析、白名单、不逐次消耗核心；VAK不追加为必要前置。',
        '千界一乘校准→QOM→I24真实初观→QLE→S03；不把世界泡采掘或捕获放进第三阶研究所首机材料。',
        'ERA只扩展原I36工况；CPT/CQS分基础封装与扩展工况；ECA/ERM分核心制造与加速启用，课题不得重复授予同一收益。',
        '试样只作为检测件，不匹配正式材料标签或替代核心/电路/燃料；具体ID注册前先检查现有物品能否复用。',
        '本轮沿用旧候选路线细化，没有确定新材料参数、九种核心数值、研究所名称、结构外观，也没有生产代码改动。',
    ]
    esc = lambda x: escape(str(x), quote=True)
    anchor = 'research-s02-' + stamp
    parts = [f'<section id="{anchor}" class="panel"><h2>S02第二阶28课题：核心、神之键与量子初观证据链</h2>',
             f'<p>变更#第二阶接线1 · {esc(now.isoformat())}。设计细化稿；待定内容未获批准，未修改游戏实现。</p><ul>']
    parts += ['<li>' + esc(x) + '</li>' for x in rules]
    parts += ['</ul><p><b>主要路线：</b>固态采集 → 基础结晶 → 专项核心试验 → 神之键装配 → 千界一乘校准 → 量子异常初观 → I24观测 → 第三阶研究所。燃料、气态、质量改良等为并行分支，不强制九核全部完成才能到达S03。</p>']
    for r in rows:
        parts.append(f'<details data-topic="{r["id"]}"><summary>{r["id"]} {esc(r["title"])} · {esc(r["status"])}</summary><div style="padding:12px">')
        for label, value in [('研究前置', '、'.join(r['prerequisites'])),
                             ('实验配方的候选研究门槛', '、'.join(r['experiment_recipe_requirements'])),
                             ('投入来源',r['inputs']),('实验设施',r['experiment_facility']),
                             ('成功事件',r['success']),('研究后真正开放',r['formal_unlock']),
                             ('防自锁与越级',r['no_self_lock'])]:
            parts.append(f'<p><b>{label}：</b>{esc(value)}</p>')
        for label, refs in [('已定位生产证据',r['current_evidence_refs']),('已定位直接RN门槛',r['current_gate_refs'])]:
            parts.append(f'<p><b>{label}：</b>' + ('；'.join(esc(f'{x["file"]}:{x["line"]}') for x in refs) if refs else '本轮源代码审计尚未定位') + '</p>')
        parts.append('</div></details>')
    parts += ['<h3>尚未裁定与检查边界</h3><ul>']
    parts += ['<li>' + esc(x) + '</li>' for x in pending]
    parts += ['</ul><p>静态检查：28项完整且不重复；所有候选实验研究门槛及已列设施解锁均在对应课题祖先中。未校验完整物料、电压、配方类型和游戏运行，不宣称消除了全部进度阻断。</p></section>']
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8')
    assert before.count('</body>') == 1
    after = before.replace('</body>', section + '\n</body>', 1)
    assert after.replace(section + '\n', '', 1) == before

    class TopicParser(HTMLParser):
        def __init__(self):
            super().__init__(); self.ids = []
        def handle_starttag(self, tag, attrs):
            if tag == 'details' and 'data-topic' in dict(attrs):
                self.ids.append(dict(attrs)['data-topic'])
    parser = TopicParser(); parser.feed(section)
    assert parser.ids == [r['id'] for r in rows]
    log = OUT / ('s02-experiment-contracts-' + stamp + '.json')
    record = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M-%S-%f') + '_第二阶28课题证据与解锁细化.html')
    assert not log.exists() and not record.exists()
    payload = {'time':now.isoformat(),'status':'讨论提案，未实现','rows':rows,'rules':rules,
               'pending':pending,'source_hashes':hashes([CAT,AUDIT]),'game_changed':False,'anchor':anchor}
    with log.open('x',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    discussion = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第二阶28课题证据与解锁细化</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;font:16px/1.8 'Microsoft YaHei';background:#14202e;color:#e4ecf5}}a{{color:#a2d8ff}}details{{border-bottom:1px solid #526274;padding:8px}}summary{{cursor:pointer}}</style></head><body>
<h1>第二阶28课题证据与解锁细化</h1><p>记录时间：{esc(now.isoformat())}，Asia/Hong_Kong。用户原消息精确时间未知，本时间为落盘时间。</p>
<h2>用户本轮要求与已确认边界</h2><p>用户“继续”，承接100课题证据来源与解锁对象讨论；不等同逐项批准方案。暂停多方块外观，保留先讨论清楚再改生产代码的要求。SMR扩种类、OPR提效率已确认。八项具体工艺合并映射与S01独立工程验证承载安排仍待答。</p>
<h2>本轮核对</h2><p>终端Get-Location实际成功。读取第二阶28项目录、既有100项候选路线、工艺合并候选、当前重构配方和研究数据；复核2026-09-22理核心迁移裁定。沿用当前源码审计前逐项核对其来源哈希，未把历史助手声明当成实现证据。</p>
{section}
<h2>产物与状态</h2><p>追加现有计划页并保存结构化JSON；28项覆盖与祖先门槛检查通过，生产src/main目录文件集合和内容哈希未变。此为讨论文档，不进行编译、部署或游戏验收；未新建游戏物品/配方/机器，也未定研究所名称。</p>
<p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">现有计划页的第二阶段落</a></p><p>后续继续S03世界泡、舰船与虚数观测；待答问题在收到明确答复后追加记录，不覆盖本条历史。</p>
<footer>变更#1：新增第二阶讨论记录和结构化设计检查；删除无。</footer></body></html>'''
    with record.open('x',encoding='utf-8') as f:
        f.write(discussion)
    assert PLAN.read_text(encoding='utf-8') == after
    assert json.loads(log.read_text(encoding='utf-8'))['rows'] == rows
    assert record.read_text(encoding='utf-8') == discussion
    production_after = hashes(sorted(p for p in (ROOT / 'src/main').rglob('*') if p.is_file()))
    assert production_before == production_after, '生产文件发生变化，应检查并发写入，不能声称未变'
    validation = {'time':now.isoformat(),'topics':28,'existing_evidence_topics':sum(bool(r['current_evidence_refs']) for r in rows),
                  'ids_match_catalog':True,'ancestral_gate_checks':True,'html_topics':len(parser.ids),
                  'prior_plan_preserved':True,'production_files_unchanged':len(production_before),
                  'game_tested':False,'compiled':False,'deployed':False,'record':str(record),'log':str(log),'anchor':anchor}
    with (OUT / ('s02-contracts-validation-' + stamp + '.json')).open('x',encoding='utf-8') as f:
        json.dump(validation,f,ensure_ascii=False,indent=2)
    print(json.dumps(validation,ensure_ascii=False))


if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
