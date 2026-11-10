"""保存终审、卷轴与最高文明等级六项裁定，仅更新设计资料。

变更#1：2026-09-28 16:40:16。新增用户答复、原始意见依据、个人会面状态边界及
旧实现差距；既有计划追加，旧终局/等级文档顶部增补覆盖说明。删除无，历史保留。
输入为已读设计、讨论原文和源码；输出HTML/JSON，回读后检查生产哈希未变。
只作记录与静态核对，不执行终局逻辑，不修改存档或游戏文件。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'logs/research-migration-20260928'
PLAN = ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
ENDING = ROOT/'doc/HK3GTL-内测5/11_系统专项/终局收口/终局审判收口方案_v1.html'
LEVEL = ROOT/'doc/HK3GTL-内测5/11_系统专项/进度与文明等级/进度与文明等级收口方案_v1.html'
DECISIONS = [
    {'question':'终审资格与结局怎样归属？建议团队共享现有工程资格，每位申请人分别核验自己的卷轴和应完成的个人经历，并亲自完成终审；一个人的结局不自动覆盖全队。',
     'answer':'工程共享，个人分别核验与结算（推荐）'},
    {'question':'W15核验满级文明档案卷轴时，是否消耗卷轴物品？建议只读取申请人绑定的真实记录并核验，不消耗卷轴；物品丢失后仍可按原规则重制。',
     'answer':'只核验，不消耗卷轴（推荐）'},
    {'question':'最高文明等级与终审是什么关系？建议保留最高等级要求，但由终审前已验证的研究、工程与交流事实自动判定，不另加刷分，也不以终审许可或结局作为升级前置。具体等级名称与里程碑表另列。',
     'answer':'保留最高等级，由已有事实自动判定（推荐）'},
    {'question':'个人终审对话中断线或主动关闭界面后，怎样恢复？建议保存到最近已确认的对话检查点，回来继续同一次会面；关闭或断线不算通过，也不算坏结局。一审的断线重开规则保持不变。',
     'answer':'从已确认检查点继续同次终审（推荐）'},
    {'question':'终审资格什么时候复核？建议进入会面前重新核对个人条件和团队工程；正式进入后固定本次资格快照，途中队伍或工程变化不打断这次会面，断线恢复仍用同次快照。新申请重新核验。',
     'answer':'入场前复核，入场后固定本次资格（推荐）'},
    {'question':'个人进入坏结局后，是否允许重新申请终审？建议保留坏结局历史，允许重新核验资格后重试；只重开会面，不回滚研究或工业，也不重复领取已有奖励。',
     'answer':'保留历史，允许重新核验后重试（推荐）'},
]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before_source = production()
    original = ROOT/'doc/HK3GTL-内测5/讨论记录/2026-09-20_10-50_第三轮主线修改意见原文.html'
    source_text = original.read_text(encoding='utf-8')
    assert '卷轴上限是除了终审以外的所有对话，所有研究，所有交流事件' in source_text
    assert '只需要完成过对话即可，不需要看过所有回答' in source_text
    contracts = [
        '已确认：团队共享现有工程资格，申请人分别核验自己的卷轴与应完成的个人经历，并亲自完成终审。个人结局不自动覆盖全队或全服，未参加者不因队友完成而自动毕业。',
        '已确认：W15只核验满级卷轴，不消耗卷轴物品；读取申请人绑定的权威真实记录，卷轴丢失可按原规则重制。复制物品/NBT不能复制另一人的资格。',
        '原始用户意见仍有效：卷轴上限涵盖终审以外所有对话、研究、交流事件；互斥回答完成其中一条即可，不要求看过全部回答，可重复交流按已完成事件计入。不得擅自改成只需100研究或少量主线。',
        '已确认：最高文明等级仍是终审要求，但从终审前已验证研究、工业工程及交流事实判定，不另加刷分，不用已经获得终审准入或结局作为升级前置。具体等级名称与分级里程碑未因本轮自动批准。',
        '已确认：个人终审在最近已确认对话检查点保存进度；断线或主动关闭界面暂停，不算通过或坏结局。恢复继续同一次会面，不套用一审断线从头规则。',
        '已确认：正式入场前重新核验个人条件和团队工程；进入会面后固定该次资格快照。途中队伍/工程变化不打断，断线恢复同次快照；重新申请是新尝试，必须重新核验。',
        '本次资格快照只服务该玩家的既有会面，不是可赠送凭证，不复制实体工程资格给新队伍，不给同队其他玩家生成准入。离队不复制工程资格的旧裁定继续有效。',
        '已确认：坏结局历史保留，允许重新核验资格后重试。只重开会面，不回滚研究、工业或既有世界状态，已领取奖励不得重发；不将重試写成撤销原坏结局事实。',
        '先前已确认的奇观规则保持：拆除/搬迁后重验，申请时结构完整但可停机；新申请读取当前所属团队的有效工程。进入后的个人快照例外不改变其他人的申请条件。',
        '保留实验→研究→制造→工程验收→终审资格→终审结果的区别。二审通过仅进入奇观正式建设及终审准备，不能立即送入终审；满卷轴不作为TAA研究或W15首机的前置。',
    ]
    flow = [
        {'stage':'申请/入场前','check':'个人卷轴、应完成的个人经历、二审条件、最高文明等级、当前团队有效奇观及舰船工程等已定条件','result':'显示具体缺项；通过后才能进入本次会面'},
        {'stage':'正式进入','check':'服务端绑定玩家与唯一会面ID，固化本次资格来源','result':'生成个人会面快照，不提前判好结局'},
        {'stage':'正常对话','check':'仅接受当前会面和当前节点允许的选择','result':'保存最近已确认检查点；不因客户端关闭包直接结算'},
        {'stage':'断线/关闭界面','check':'保留会面快照及已确认检查点','result':'暂停会面，既不毕业也不判坏结局'},
        {'stage':'恢复同次会面','check':'核对玩家、会面身份与未完成状态','result':'继续原检查点；无需用已变化的队伍/基地重新推翻这次入场'},
        {'stage':'好/坏结局提交','check':'核对本次有效终止节点及唯一结算状态','result':'记录个人结果与防重奖励；不写成全服统一结果'},
        {'stage':'坏结局后重新申请','check':'重新核对当前全部资格，原历史不删除','result':'建立新的会面尝试；不重置生产、研究或已领取奖励'},
    ]
    findings = [
        'Hk3GraduationData使用主世界SavedData中的单一Graduated布尔值；SirinDialogueEndHandler结束处理同时写玩家标签和该全服标记，不能直接承担本轮个人结算。',
        'Hk3BadEndingData存储跨玩家共享attackCount与stage；新个人结局不能继续由其他玩家累计攻击触发，也不能拿旧世界级状态当所有人的个人结果。具体攻击判定仍另审。',
        'DialogueSessionManager活跃会话为内存ConcurrentHashMap，断线移除会话；现有机制未实现本轮所需的持久化资格快照与检查点恢复。可复用对话定义/网络呈现，状态管理须改造。',
        'NarrativeCodexItem读取使用者的叙事统计，Hk3NarrativeLog.unlockedCount按前缀布尔键计数。这个总数不能直接证明内测5满卷轴目录齐全，需要逐项对照目录和实际事件来源。',
        '旧终局v1中“二审对话完成后进入终审入口”遗漏后来明确的奇观/卷轴等准备条件。本轮在旧页顶部补充权威覆盖提示，保留原文供追溯。',
        '旧文明等级稿的C0–C7命名与里程碑仍需逐项核对；本轮确定的是最高等级与终审的关系，没有批准旧稿全部默认细节。',
    ]
    implementation = [
        '卷轴清单候选以明确RN课题ID、对话完成事件ID和交流完成事件ID组成；互斥分支归入同一完成要求，终审事件从入场前目录排除。未知旧键保留历史但不能凑数量。',
        '等级判定与终审资格查询需要单向依赖：等级读研究/工程/交流事实，准入读等级及其他条件；等级不得反过来要求准入或已毕业。',
        '个人会面快照建议保存玩家、尝试ID、入场时间、当时团队、工程版本/证据引用、卷轴目录版本、对话脚本版本与检查点。客户端仅请求，服务端校验推进及幂等结算。',
        '资格查询、会面状态和奖励领取分开持久化；同次结果只能提交一次，多次会面的历史不能覆盖丢失。断线重入与旧客户端延迟包需拒绝跨尝试写入。',
        '旧毕业标记仍被维度入口、实体交互、坏结局管理和事件代码直接查询。后续须逐入口适配个人/团队作用域，不能只改结束处理器；本轮未删除旧文件或迁移存档。',
        '终审固定快照避免在会面中持续扫描十五座巨构；入场前仍需分批核实有效工程，未加载不能当已拆除，也不能盲信失效缓存。本次未证明区块验证实现完成。',
    ]
    pending = [
        '满卷轴的具体对话/交流事件清单及稳定完成路径、新队员未经历事件的补谈/补做入口仍需列清；已确认全部覆盖的范围不重新缩小。',
        '最高文明等级的具体名称、逐级里程碑与个人/团队事实读取规则仍需细化；不能从旧“默认收口”标题推定每项已批准。',
        '仿制休伯利安拆除/搬迁后的工程复验规则、团队解散后实体接管等此前边界仍待讨论，不擅自把奇观规则扩大到所有资产。',
        '终审具体对话正文、攻击与误伤判定、奖励清单、返回位置/死亡恢复及多人同时会面表现尚需专项设计；本轮确定个人结算不等于这些全部完成。',
        '本轮只确认六项机制，尚未授权修改游戏。研究100项仍为详细设计覆盖，不因终局裁定变成100项可玩。',
    ]
    source_paths = [original,ENDING,LEVEL,
        ROOT/'doc/HK3GTL-内测5/讨论记录/2026-09-28_15-58-27_第五阶7课题与奇观工程资格裁定.html',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/dimension/Hk3GraduationData.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/dialogue/handler/SirinDialogueEndHandler.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/dialogue/DialogueSessionManager.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/badending/Hk3BadEndingData.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/item/NarrativeCodexItem.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/narrative/Hk3NarrativeLog.java']
    e = lambda x:escape(str(x),quote=True)
    anchor = 'final-audience-confirmed-'+stamp
    parts = [f'<section class="panel" id="{anchor}"><h2>已确认：个人终审、卷轴核验与资格快照</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；用户原消息精确时间未知。六项机制已确认，生产未实施。</p>']
    for d in DECISIONS:parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>用户答复：</b>'+e(d['answer'])+'</p>')
    for title,values in [('已确认规则',contracts),('当前实现差距',findings),('实施建议，非完成证据',implementation),('仍需细化',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<h3>一次个人终审的流程</h3>')
    for r in flow:parts.append('<p><b>'+e(r['stage'])+'：</b>'+e(r['check'])+'；'+e(r['result'])+'。</p>')
    parts.append('<p>未修改研究/叙事Java、资源、结构、实例或存档；未编译、部署或游戏测试。静态阅读不代表终审可运行。</p></section>')
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8');assert before.count('</body>') == 1
    after = before.replace('</body>',section+'\n</body>',1)
    assert after.replace(section+'\n','',1) == before
    notice_texts = {
        ENDING:'本页旧默认方案须以2026-09-28明确答复为准：二审后仍需奇观工程、个人满卷轴和最高文明等级等资格，不能直接进入终审。工程由团队共享，终审个人核验与结算；卷轴不消耗；入场前复核、入场后固定本次资格快照；中断从检查点恢复；坏结局保留历史并允许重新核验后重试。以下未涉及的旧条款不因本提示自动获批。',
        LEVEL:'最高文明等级仍是终审要求，由终审前已验证的研究、工程及交流事实自动判定，不另加刷分，不以终审准入或结局作为升级前置。具体分级名称与里程碑未因本轮自动批准；本页旧C0–C7为待核对设计。个人结局与团队工程分开，不用全服毕业标记替代。',
    }
    updates = {}
    for path,text in notice_texts.items():
        old = path.read_text(encoding='utf-8')
        notice = f'\n<aside class="panel decision" id="decision-update-{stamp}"><h2>最新明确裁定覆盖提示</h2><p>{e(text)}</p><p><a href="../../09_测试发布/十二天重制计划与交付清单.html#{anchor}">查看六项原问题、用户答复及实施边界</a></p><p>变更#2 · {e(now.isoformat())}：新增本轮覆盖提示，保留全部历史内容，删除无，游戏未改。</p></aside>\n'
        match = re.search(r'<body\b[^>]*>',old);assert match
        new = old[:match.end()]+notice+old[match.end():]
        assert new.replace(notice,'',1) == old
        updates[path] = new
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_个人终审卷轴文明等级与会面恢复确认.html')
    log = OUT/('final-audience-confirmed-'+stamp+'.json')
    validation = OUT/('final-audience-validation-'+stamp+'.json')
    for p in [record,log,validation]:assert not p.exists(),p
    payload = {'time':now.isoformat(),'status':'六项用户答复已确认，未实现','decisions':DECISIONS,
        'confirmed_parameters':{'engineering_scope':'current_team','eligibility_and_ending_scope':'individual',
            'consume_scroll':False,'requires_highest_civilization_level':True,'civilization_level_basis':'verified_pre_audience_facts_no_extra_grinding',
            'interruption':'resume_confirmed_checkpoint','qualification_snapshot':'freeze_on_entry_reuse_for_same_session',
            'new_attempt':'revalidate','bad_ending_retry':'allowed_preserve_history_no_world_rollback_no_duplicate_rewards'},
        'contracts':contracts,'flow':flow,'findings':findings,'implementation_candidates':implementation,'pending':pending,
        'source_hashes_before':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},'anchor':anchor,'game_changed':False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>个人终审与卷轴资格确认</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}</style></head><body><h1>个人终审、卷轴、文明等级与会面恢复确认</h1><p>用户要求继续研究系统相关边界。先核对原主线意见、第五阶裁定、旧终局/等级稿与实际代码，再提交两组六个问题；用户均明确选择本页记录的方案。原始消息精确时间未知，下列时间为本轮记录时刻。</p>{section}<h2>覆盖关系与实际执行</h2><p>本轮明确终审个人/团队归属、卷轴是否消耗、最高等级关系、断线恢复、资格检查时机和坏结局重试。原全部研究/对话/交流的卷轴范围、一审断线重开、二审自动降临及奇观现存复验规则保持。本次个人已入场快照不扩大为新队伍永久工程资格。</p><p>已追加现有计划、在旧终局及等级页顶部标明覆盖关系，保存结构化答复与本讨论记录并回读。生产文件集合与哈希不变。未删除历史、未修改存档或执行代码中的终局行为。</p><p>下一步列清卷轴目录和稳定完成路径、最高文明等级里程碑，再处理尚未确定的必要会面细节。本轮未批准旧稿全部名称、攻击阈值或奖励。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">本轮完整确认</a> · <a href="2026-09-20_10-50_第三轮主线修改意见原文.html">卷轴范围的原始用户意见</a> · <a href="2026-09-28_15-58-27_第五阶7课题与奇观工程资格裁定.html">第五阶及奇观工程裁定</a></p><footer>变更#1 · {e(now.isoformat())}：新增六项答复、状态边界与当前代码差距；修改设计文档为追加覆盖提示；删除无。设计确认不等于功能实现。</footer></body></html>'''
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    for path,new in updates.items():path.write_text(new,encoding='utf-8')
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    for path,new in updates.items():assert path.read_text(encoding='utf-8') == new
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert before_source == production(), '生产文件发生变化，需检查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':6,'audience_flow_stages':len(flow),
        'original_scroll_scope_verified':True,'prior_document_contents_preserved':True,
        'production_files_unchanged':len(before_source),'compiled':False,'deployed':False,'game_tested':False,
        'record':str(record),'log':str(log),'anchor':anchor}
    with validation.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':main()
