"""第五阶研究讨论稿生成与静态核验；不修改任何游戏文件。

变更#1：2026-09-28 15:55:09（讨论工具，不增加游戏修订号）。
新增七课题证据/收益候选及三项用户工程资格裁定，追加现有计划和讨论记录。
删除无；保留历史。输入为研究目录、此前四阶稿及来源审计，输出HTML/JSON。
源哈希、覆盖或研究祖先检查失败则在写入前停止；写入后回读并核验生产文件。
重复执行会生成新的讨论记录，接续时应先检查已有输出，不能为验证而重跑。
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

# 课题、前级投入、实验设施、成功事件、研究收益、防自锁、建成后真实运行。
RAW = '''
CKV|可追溯的崩坏/量子/虚数实验证据、具有来源的相互矛盾情报及可复验样本|I32复验样本→I43核对观测条件与情报来源；S05承担正常研究|实际复验区分事实、推论与无法判定项，保留原文和实验来源；不靠选择预设立场获得证据|W09独立控制器及知识交叉验证工况；专项研究完成且二审通过才可正式建造/运行|不要求W09先出证明，不要求看到互斥对话的全部回答；关键矛盾资料需设计可达的稳定来源，不把随机外交作为永久卡点|W09实际消耗验证介质与能源，完成有来源的知识验证批次，结果提交后记录本体工程证明；不重复发研究点，不消耗卷轴，不合并S05
DIO|已运行的多设备生产链、I41基础登记与手动授权操作记录、可追溯实际订单与物料|前级设备按现有方式实际完成跨机工序→I43核对交接及授权边界|不同设备完成同一订单关联工序，投入、产物和权限回执对应；研究前可手动交接，不要求已有W11自动统御|W11控制器、授权机器的订单协调与工况反馈；专项研究和二审双门槛|不要求W02先扩产、不要求W11先自动完成自身研究订单；不接管他人设备、不顺带引入AE2优化依赖|W11实际协调已授权设备完成跨工序订单；输出阻塞不重复结算，撤权/停机停止后续派单；授权角色、在途资源归还规则另审
ASR|ECA已开放侵蚀核心、CPT电路成果、已有课题运行记录与前级隔离演算工装|I32受控演算结果检测→I43核对停止、隔离与基准结果|实际耗能运行有限基准演算，结果可重复核对并验证可停止；不先加速本课题，不重新授予已完成课题奖励|W13控制器、受控优化模型与效率验证工况；正式运行需二审；与ERM研究所模块的叠加规则另审|不以ERM或W13加速作为ASR起步条件，不触及真实文件；不修改研究点计算机产点、不允许无限速度叠加|候选：独立可重复的基准演算工况验证优化前后正确性与成本，不要求剩余未完成课题，不产生研究完成或点数；倍率、模型应用范围和耗能待审
WCE|I29构筑、I30稳定、I31终止回收的同一个合法模拟批次记录及SWR成果|I43核对模拟批次从创建至最终结算的完整链条|同一批次实际耗料、耗能、稳定及终止成功且仅结算一次；封存或暂停不算完成，不拼接不同批次|W14控制器及文明规模模拟工况；专项研究和二审双门槛，保留I29–I31基础路线|不要求W14先运行，不拿真实目标十次采掘账本充当模拟实验，不把捕获真实目标记成模拟制造|W14独立模拟批次完成投入、构筑、稳定、终止与资源结算；每一批只能结算一次，不生成真实世界泡资产，资源池/规模/成本另审
CAV|W09/W11/W13/W14的真实本体运行证明、三领域实验档案及机器来源|I43核对四座证明与工程归属→W09执行跨资料验证|四座本体真实记录与档案对应，校核机器身份、来源与结算事件；复制报告物品不新增证据|文明成果交叉验证报告的正式生成工况，供TAA/W15读取；研究前校验只产CAV实验证据|四座机器各自研究已解锁即可先运行，不把CAV锁在这四座基本验收之前；交叉验证方法预检与正式报告分开|正式报告引用实际证据ID及工程版本；历史报告不替代申请时的现存工程检查，不直接发终审通过或毕业标记
TAA|W01至W14各自真实工程证明、CAV正式验证报告及仿制休伯利安HVI运行记录|I43核对十四类奇观与舰船工程记录，S05正常研究|按类型核验14种不同奇观的真实成果和舰船记录，不以14台同类型机器或14个控制器代替；预检成功只给TAA研究证据|W15控制器、必要建造件及资格汇总功能；研究完成且二审通过方可正式建造和运行|TAA不要求W15自证或满卷轴，避免把本课题与后续交流反锁；W15首机不得依赖自身产物；HVI仍是毕业必需|W15建成后实际运行资格校验，读取前14座、舰船、二审和申请人卷轴等各系统记录，生成一次可追溯结果；申请资格与真正完成终审分开，W15运行不以已有终审准入为前提
DVC|CAV已验证的三领域成果、保留条件差异与来源的实际工况数据|I32复验有差异的样本/工况→W09交叉校验，S05正常研究|实际比较崩坏、量子与虚数工况在各自条件下的差异，能追溯原始实验；不能统一删掉不同结果或用三份复制资料凑数|跨领域工艺诊断与校验资料生成工况，输出差异原因/适用边界；不凭空解锁新物料或终审维度|目录未将DVC列为TAA前置，不擅自追加；若卷轴目录要求此研究，在终审申请阶段核对，不反锁W15制造|诊断按真实工况提供可追溯报告，不授予树海主人权能；报告不替代设备本体验收、二审或终审
'''
GATES = {
    'CKV': ['CLE', 'IAR', 'LTA', 'CEE'],
    'DIO': ['CLE', 'AIM', 'CED', 'CEE'],
    'ASR': ['CLE', 'ECA', 'CPT', 'LTA', 'CEE'],
    'WCE': ['CLE', 'SWR', 'SWC', 'SWS', 'CEE'],
    'CAV': ['CKV', 'DIO', 'ASR', 'WCE', 'CEE'],
    'TAA': ['CAV', 'HVI', 'CEE', 'HCCO', 'AIM', 'IAR', 'SEM', 'IFF', 'CCF', 'MRA', 'SFF', 'GSF', 'ECB'],
    'DVC': ['CKV', 'CAV', 'LTA'],
}
WONDERS = {'CKV': 'W09', 'DIO': 'W11', 'ASR': 'W13', 'WCE': 'W14', 'TAA': 'W15'}
DECISIONS = [
    {'question': '奇观已完成真实运行验收后，如果拆掉或搬迁，终审资格怎样处理？建议保留历史成果和研究，但这座奇观暂不计入当前工程资格；重建后重新验收。',
     'answer': '保留历史，重建后重新验收（推荐）'},
    {'question': '申请终审时，十五座奇观是否必须同时运行？建议逐座完成各自真实工况验收，申请时保持结构完整即可，允许停机，不要求全部同时耗能。',
     'answer': '逐座验收，申请时完整即可，可停机（推荐）'},
    {'question': '成员离队或加入新队时，奇观工程资格是否留在原所属团队？已完成研究和实验证据仍按既定规则继承；建议工程资格不复制，新队需要自己的工程验收。',
     'answer': '工程资格留原队，不随成员复制（推荐）'},
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'src/main').rglob('*')) if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before_source = production()
    catalog = {r['id']: r for r in json.loads(CAT.read_text(encoding='utf-8'))['topics']}
    audit = json.loads(AUDIT.read_text(encoding='utf-8'))
    for name, digest in audit['source_hashes'].items():
        assert sha(ROOT/name) == digest, ('原审计来源已变化', name)
    audited = {r['id']: r for r in audit['rows']}

    def ancestors(key, chain=()):
        assert key not in chain, ('研究循环', key, chain)
        result = set()
        for parent in catalog[key]['prerequisites']:
            result.add(parent)
            result.update(ancestors(parent, chain+(key,)))
        return result

    rows = []
    for line in RAW.strip().splitlines():
        short, inputs, facility, success, unlock, guard, runtime = line.split('|')
        key = 'RN-'+short
        gates = ['RN-'+x for x in GATES[short]]
        assert catalog[key]['lab'] == 5
        assert set(gates) <= ancestors(key), (key, set(gates)-ancestors(key))
        rows.append({**catalog[key], 'inputs': inputs, 'experiment_facility': facility,
                     'success': success, 'formal_unlock': unlock, 'no_self_lock': guard,
                     'post_unlock_runtime': runtime, 'facility_and_input_unlocks': gates,
                     'experiment_recipe_requirements': catalog[key]['prerequisites'],
                     'wonder': WONDERS.get(short),
                     'formal_wonder_build_run_requires_second_judgment': short in WONDERS,
                     'research_adds_explicit_second_judgment_gate': False,
                     'current_evidence_refs': audited[key]['evidence_refs'],
                     'current_gate_refs': audited[key]['gate_refs'],
                     'status': '详细接线候选，非实现；本轮三项裁定单列确认'})
    assert len(rows) == len({r['id'] for r in rows}) == 7
    assert {r['id'] for r in rows} == {k for k, v in catalog.items() if v['lab'] == 5}
    assert not any(r['current_evidence_refs'] for r in rows)

    prior_files = [sorted(OUT.glob(f's0{i}-experiment-contracts-*.json'))[-1] for i in range(1, 5)]
    all_rows = []
    for p in prior_files:
        all_rows.extend(json.loads(p.read_text(encoding='utf-8'))['rows'])
    all_rows.extend(rows)
    assert len(all_rows) == len({r['id'] for r in all_rows}) == 100
    assert {r['id'] for r in all_rows} == set(catalog)
    fourth = json.loads(prior_files[3].read_text(encoding='utf-8'))['rows']
    wonder_ids = {r['wonder'] for r in fourth+rows if r.get('wonder')}
    assert wonder_ids == {f'W{i:02}' for i in range(1, 16)}

    contracts = [
        '已确认：拆除/搬迁保留历史实验与完成研究，但该实体暂不计入当前工程资格；重建后必须重新验收。停机本身不抹去已完成的验收。',
        '已确认：十五座奇观可逐座完成真实工况验收；申请时保持结构完整，允许停机，无须同时耗能。W15执行申请校验这一操作仍需自身正常运行。',
        '已确认：成员离队/入队不复制奇观工程资格；资格留在原所属团队。知识和已完成实验证据按既定规则继承且保留来源，两类账本分开。',
        '沿用二审裁定：研究本身不额外加二审开关；正式奇观建造与运行检查专项研究和二审两项。CAV/TAA/DVC需要真实奇观运行，故自然在二审之后取得必要证据。',
        '数据候选：实验记录绑定证据ID、实验批次、机器身份、原所属团队、时间和来源；工程验收另绑定奇观类型、实体ID、结构版本、维度/位置及实际运行回执。研究继承只引用事实，不复制实体资格。',
        '状态候选：已验收、结构失效、待复验、状态待核实分别记录。失效不删历史；同一回执重试幂等，不重复发证明、产物或研究点。具体存盘事务仍需实现验证。',
        '低内存实施候选：按结构形成/破坏事件维护索引，申请时分批核验；不逐tick扫描十五座巨构、不一次强制加载全部区块。未加载不等于已拆除，也不凭过期缓存判完整，列为待核实并补验；具体加载与快照有效策略待实现评审。',
        'TAA研究核对前十四座及仿制休伯利安，开放W15；W15正式申请再核对十五座、舰船、二审、申请人满级卷轴及其余已确认条件。W15资格校验成功作为其功能运行记录，不要求先进入终审才能验收自己。',
        'W15查询权威服务端记录并列出缺项；控制器物品、可编辑NBT、聊天文字或旧全服毕业布尔值均不能代替二审/工程/个人会面资格。真正毕业仍由终审结果决定。',
        'W13与ERM模块的适用范围、倍率、能耗和叠加未定；重复基准工况仅为验收候选，不自动加速真实课题、不重复研究收费与奖励。W14继续使用独立模拟批次，不污染真实目标采掘次数。',
    ]
    findings = [
        '本次按来源哈希复核的审计中，第五阶7项均未定位生产证据入口；本轮候选不会把目录存在当作接通。',
        'Hk3GraduationData目前保存全服共享的Graduated布尔值。可研究复用SavedData机制，但不能拿一个全服标记代替新方案中的团队工程及申请人资格；未改旧类或存档。',
        'Hk3ResearchStory加载100条叙事文本并检查顺序，不等于100条研究证据、奖励与终审事件已接入。',
        'Hk3MachinesWonderStage仍描述旧v0.3十二台奇观；旧注册或新建材注册存在，不证明内测5十五座本体运行与资格服务已经完成。',
        '全部五阶稿合计100个唯一课题，覆盖25/28/19/21/7；S04和S05专项映射覆盖W01–W15。静态祖先关系不证明具体物料、电压、研究费用和叙事来源全部可达。',
    ]
    pending = [
        'CKV矛盾情报的稳定来源：候选由必达叙事档案提供可复验矛盾，不要求接受某阵营或抽中随机来访；具体档案与事件尚未批准。',
        'W13优化功能与ERM模块的分工、倍率、叠加、能耗；W11授权角色、撤权时在途物料及订单处置仍需确认。',
        '本轮工程资格三项仅处理奇观；仿制休伯利安拆除/搬迁是否同样复验、团队解散后的实体接管、跨队转让与重新验收尚未裁定。',
        '终审是每人分别面见还是团队一起结算、申请中成员变化、断线/重入与申请后工程失效的处理，仍须叙事专项确认；不能从团队研究共享推导全员自动毕业。',
        '卷轴满级目录、最高文明等级与终审条件的关系、提交是否消耗卷轴/其他成本仍未定；不得用满卷轴或W15运行本身作为TAA研究前置。',
        '八项工艺合并具体映射、研究所工程验证的承载方式、舰船档案概率/保底次数、材料支线与各配方数值仍为此前待定项，未被“继续”批准。',
        '100项目前达到逐题设计覆盖，并非100项获批或可玩。下一步应集中收口尚影响研究实施的决定，再按可复用底层、实验来源、正式收益分批实现；外观讨论保持暂停。',
    ]
    sources = [CAT, AUDIT, *prior_files,
               ROOT/'src/main/java/com/sirin/hk3gtl/common/dimension/Hk3GraduationData.java',
               ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchStory.java',
               ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesWonderStage.java',
               ROOT/'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html',
               ROOT/'doc/HK3GTL-内测5/00_总纲/内测5完整主线方案与树状图_v4.html']
    e = lambda value: escape(str(value), quote=True)
    anchor = 'research-s05-'+stamp
    parts = [f'<section id="{anchor}" class="panel"><h2>S05第五阶7课题：文明验证与终审准备</h2>',
             f'<p>变更#第五阶接线1 · {e(now.isoformat())}。研究设计候选；本轮三项用户答复单列已确认。全部100项有逐题稿，不代表全部获批、接通或可玩。</p>',
             '<h3>本轮已确认</h3>']
    for d in DECISIONS:
        parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>用户答复：</b>'+e(d['answer'])+'</p>')
    parts.append('<h3>七项证据与收益候选</h3>')
    for r in rows:
        parts.append(f'<details data-topic="{r["id"]}"><summary>{r["id"]} {e(r["title"])} · 接线候选</summary><div style="padding:12px">')
        for label, value in [('前置研究', '、'.join(r['prerequisites'])), ('前级投入', r['inputs']),
                             ('实验设施', r['experiment_facility']), ('实际成功事件', r['success']),
                             ('研究后开放', r['formal_unlock']), ('防自锁', r['no_self_lock']),
                             ('正式运行与验收候选', r['post_unlock_runtime'])]:
            parts.append('<p><b>'+e(label)+'：</b>'+e(value)+'</p>')
        parts.append('<p>候选工序与运行标准尚未实现；研究证据、完成知识、当前工程资格、终审通过分别判定。</p></div></details>')
    for title, values in [('资格与接线边界', contracts), ('当前代码与静态核对', findings), ('未定事项集中清单', pending)]:
        parts.append('<h3>'+title+'</h3><ul>')
        parts.extend('<li>'+e(x)+'</li>' for x in values)
        parts.append('</ul>')
    parts.append('<p>本轮仅追加讨论与检查结果；没有修改生产源码、资源、配方、结构、游戏实例或存档，没有编译、部署或游戏测试。</p></section>')
    section = '\n'.join(parts)
    class Parser(HTMLParser):
        def __init__(self): super().__init__(); self.ids = []
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == 'details' and 'data-topic' in a: self.ids.append(a['data-topic'])
    parser = Parser(); parser.feed(section)
    assert parser.ids == [r['id'] for r in rows]
    before = PLAN.read_text(encoding='utf-8')
    assert before.count('</body>') == 1
    after = before.replace('</body>', section+'\n</body>', 1)
    assert after.replace(section+'\n', '', 1) == before
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_第五阶7课题与奇观工程资格裁定.html')
    log = OUT/('s05-experiment-contracts-'+stamp+'.json')
    decision_file = OUT/('s05-confirmed-decisions-'+stamp+'.json')
    validation_file = OUT/('s05-contracts-validation-'+stamp+'.json')
    for p in [record, log, decision_file, validation_file]: assert not p.exists(), p
    payload = {'time': now.isoformat(), 'status': '第五阶详细设计，非实现', 'rows': rows,
               'confirmed_this_turn': DECISIONS, 'contracts': contracts, 'findings': findings, 'pending': pending,
               'source_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sources}, 'anchor': anchor, 'game_changed': False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第五阶课题与奇观工程资格</title><style>body{{max-width:1120px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}details{{padding:8px;border-bottom:1px solid #536174}}summary{{cursor:pointer}}</style></head><body><h1>第五阶7课题与奇观工程资格裁定</h1><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；原用户消息精确时间未知。</p><p>用户要求“继续”，承接第四阶21项，继续100课题的证据与解锁讨论；设计收口前不改游戏代码，结构外观暂停。随后用户明确选择本页三项推荐。</p>{section}<h2>覆盖关系、实际执行与后续</h2><p>本轮三项答复明确第四阶记录中奇观拆除/搬迁、同时运行和成员迁移的待定边界，覆盖相应未定状态；不覆盖团队解散接管、舰船现存条件或终审个人结局归属。历史实验继承不等于可用于当前终审的实体资格继承。</p><p>已读取七项目录、此前四阶稿、工业树/主线文档及旧毕业/叙事/奇观代码，核验来源哈希、研究祖先与100项覆盖。追加既有计划，保存结构化方案与明确答复，并回读检查；生产文件哈希前后比对。没有删除历史记录或旧系统。</p><p>下一步先收口集中清单中的关键玩法边界，再修改代码；本页详细工序仍是提案，三个答复不等于批准全部七项工序。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">第五阶详细方案</a> · <a href="2026-09-28_15-51-46_第四阶21课题与二审后奇观建造裁定.html">第四阶与二审裁定</a></p><footer>变更#1 · {e(now.isoformat())}：新增第五阶提案与三项答复；修改现有计划为追加，不覆盖历史；删除无。用途为后续研究实现依据，不代表游戏功能完成。</footer></body></html>'''
    with log.open('x', encoding='utf-8') as f: json.dump(payload, f, ensure_ascii=False, indent=2)
    with decision_file.open('x', encoding='utf-8') as f:
        json.dump({'time': now.isoformat(), 'status': '用户已确认，尚未实现', 'decisions': DECISIONS}, f, ensure_ascii=False, indent=2)
    PLAN.write_text(after, encoding='utf-8')
    with record.open('x', encoding='utf-8') as f: f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['rows'] == rows
    assert json.loads(decision_file.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert before_source == production(), '生产文件变化，须核对并发写入'
    validation = {'time': now.isoformat(), 'topics': 7, 'design_ancestor_checks': 7,
                  'unique_all_stage_topics': 100, 'stages': [25, 28, 19, 21, 7], 'wonder_mappings': 15,
                  'current_evidence_topics': 0, 'prior_plan_preserved': True,
                  'production_files_unchanged': len(before_source), 'confirmed_answers': 3,
                  'compiled': False, 'deployed': False, 'game_tested': False,
                  'record': str(record), 'log': str(log), 'decision_file': str(decision_file), 'anchor': anchor}
    with validation_file.open('x', encoding='utf-8') as f: json.dump(validation, f, ensure_ascii=False, indent=2)
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
