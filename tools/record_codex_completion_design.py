"""记录卷轴补谈裁定并提取候选目录；仅追加设计，绝不修改生产文件。

变更#1：2026-09-28，新增三项用户裁定、旧档案静态映射和未定边界。
记录时间由执行时钟产生；未执行游戏，不将注册数量当成可玩内容数量。
"""
from pathlib import Path
from html import escape
from collections import defaultdict, Counter
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
DOC = ROOT / 'doc/HK3GTL-内测5'
OUT = ROOT / 'logs/research-migration-20260928'
QUESTIONS = [
    ('后来加入队伍的玩家，缺少已经发生过的普通通信经历时，怎样补齐个人卷轴？建议开放个人补谈／补办入口，亲自完成后计入；仅翻阅队伍档案不算完成，补办不改写原队外交决定，也不重复发放团队奖励。', '亲自补谈／补办，完成后计入（推荐）'),
    ('后来加入、未亲历一审或二审的玩家，怎样补齐这两段个人经历？建议开放个人补行会面，沿用已确认的一审问答次数约束，不重置原队审查结果、不重复授予团队技术；具体台词可体现“加入既有文明后的会面”。', '亲自补行会面，保留原队结果（推荐）'),
    ('旧版卷轴还收录随机彩蛋、研究失败等条目；它们是否也属于内测5满级卷轴的必做内容？建议先逐项区分正式对话／交流与纯彩蛋：正式对话和交流全部保留要求，纯彩蛋作为额外收藏，不阻断终审。', '纯彩蛋额外收藏，正式对话交流仍全做（推荐）'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def production():
    return {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / 'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before = production()
    catalog = ROOT / 'src/main/resources/data/hk3gtl/research/research_catalog.json'
    legacy_path = ROOT / 'src/main/java/com/sirin/hk3gtl/common/narrative/Hk3NarrativeNodes.java'
    communication = DOC / '11_系统专项/交流与外交系统/交流与外交系统首轮提案_v1.html'
    topics = json.loads(catalog.read_text(encoding='utf-8'))['topics']
    assert len(topics) == len({t['id'] for t in topics}) == 100
    source = legacy_path.read_text(encoding='utf-8')
    source = re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)
    legacy = []
    for match in re.finditer(r'\breg\("([^"]+)"\s*,(.*?)\);', source, re.S):
        events = re.findall(r'"(E-[A-Z]+-\d+)"', match.group(2))
        assert len(events) == 1
        legacy.append({'node': match.group(1), 'event': events[0], 'origin': '显式reg注册'})
    for match in re.finditer(r'\bregEvents\(Hk3NarrativeFaction\.\w+,(.*?)\);', source, re.S):
        for event in re.findall(r'"(E-[A-Z]+-\d+)"', match.group(1)):
            legacy.append({'node': event, 'event': event, 'origin': 'regEvents注册'})
    assert re.search(r'for\s*\(int i = 1; i <= 100; i\+\+\)', source)
    for i in range(1, 101):
        event = f'E-EG-{i:03d}'
        legacy.append({'node': event, 'event': event, 'origin': '源码固定循环展开'})
    assert len({x['node'] for x in legacy}) == len(legacy)
    by_event = defaultdict(list)
    for row in legacy:
        by_event[row['event']].append(row['node'])
    duplicate_events = {k: v for k, v in by_event.items() if len(v) > 1}
    text = communication.read_text(encoding='utf-8')
    nodes = json.loads(re.search(r'const nodes\s*=\s*(\[.*?\]);', text, re.S).group(1))
    def walk(rows):
        for row in rows:
            yield row
            yield from walk(row.get('children', []))
    communications = [n for n in walk(nodes) if re.fullmatch(r'E\d\d', n['id'])]
    rules = [
        '已确认：新队员的普通通信缺项通过个人补谈／补办真实完成；仅阅读队伍档案不计入个人完成。补办不改写原队外交决定，不重复发放团队奖励。',
        '已确认：未亲历一审、二审的新队员亲自补行会面；原队审查结果与已获技术保留，不重复授予团队技术。沿用一审既定问答次数，不因补行或切队重置次数。',
        '已确认：纯彩蛋作为额外收藏，不阻断终审；正式对话和交流仍全部要求完成。不能仅凭E-EG前缀把实际正式交流降为可选，具体分类须逐项按内容核对。',
        '已确认的既有规则：终审之外全部研究、对话与交流计入满卷轴；互斥回答完成其中一条即可，同一事件只计一次，不要求看完所有回答。',
        '既有共享规则继续：研究与已完成实验证据依规则共享和继承；个人补谈不要求重新支付已完成研究，不将工程资格、团队资产或其他人的个人经历复制给新队员。',
        '文明等级按原始明确意见由队伍共享；终审个人经历与结果分别核验。C0–C7旧命名及具体里程碑仍为待核对设计，没有因本轮获得批准。',
    ]
    findings = [
        f'静态展开Hk3NarrativeNodes得到{len(legacy)}个档案节点，对应{len(by_event)}个事件ID；其中{len(duplicate_events)}个事件映射到多条展示档案。此数量不是内测5必做数量，也未证明全部可触发。',
        'Hk3NarrativeManager会解锁同事件的全部展示节点；Hk3NarrativeLog按布尔键计数。满卷轴必须逐项核验正式要求，不能以展示节点总数或任意旧键数量替代。',
        'E-HQ-005由onFinaleDialogueStarted在终审界面开启时触发；对应HQ-005与E-HQ-005均不能作为入场前要求。终审历史仍可展示。',
        'EG-003对应E-EGG-001研究失败彩蛋；旧机制是否保留需另核，不可为了补齐旧档案而恢复研究失败机制。',
        '现有交流首轮提案只列出8个E组节点，其中同意／拒绝为互斥回应；不能把这8项冒充完整交流目录。其他角色、台词及稳定入口尚未定稿。',
    ]
    proposals = [
        '目录候选分为研究完成、正式对话/交流完成、额外收藏、终审历史四类；满卷轴核验前两类，后两类可展示但不构成准入前置。',
        'CM-MAX-REPLY-ACCEPT与CM-MAX-REPLY-DECLINE归入同一个回应完成要求，满足其一即可；保留实际选择，不伪造另一分支。',
        '补谈入口显示原事件、原队历史、本人尚缺的经历与完成条件；首次补完后仅写本人对应完成事实。补办涉及真实交付时仍需真实交付，不以阅读日志替代履约。具体补办成本仍待逐事件制定。',
        '一审B5与二审D5目前为设计节点标识，尚不在本轮发明或注册新的生产事件ID。补行正文需体现加入既有文明后的语境，不能假称重复完成原文明首次审查。',
    ]
    pending = [
        '全部正式对话及交流的最终目录、旧事件逐项保留/改造/不采用清单；目前仅完成来源索引，不宣布逐项审定。',
        '一审混合新老成员、离线成员及代表断线边界；本轮不覆盖既定问答次数与断线规则。',
        '文明等级的名称与逐级里程碑；继续按已确认队伍共享，不重新提问归属。',
        '个人补行会面的台词、真实任务成本与触发入口；不会擅自把补谈变成重做全部工业。',
    ]
    anchor = 'codex-completion-'+stamp
    e = lambda value: escape(str(value), quote=True)
    parts = [f'<section class="panel" id="{anchor}"><h2>卷轴完成目录与新队员补谈：三项已确认</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong。原始消息精确时间未知；设计记录，生产未实施。</p>']
    for q, a in QUESTIONS:
        parts.append(f'<p><b>问题：</b>{e(q)}<br><b>用户答复：</b>{e(a)}</p>')
    for title, rows in [('已确认边界', rules), ('实际源码与文档差距', findings), ('实施候选，尚未完成', proposals), ('仍待确定', pending)]:
        parts.append('<h3>'+title+'</h3><ul>'+''.join('<li>'+e(r)+'</li>' for r in rows)+'</ul>')
    parts.append('<details><summary>100课题目录引用（按研究所阶级展开；非功能验收）</summary>')
    for stage in range(1, 6):
        rows = [t for t in topics if t['lab'] == stage]
        parts.append(f'<h4>S0{stage} · {len(rows)}项</h4><ul>'+''.join('<li>'+e(t['id']+' · '+t['title'])+'</li>' for t in rows)+'</ul>')
    parts.append('</details><details><summary>当前首轮通信设计索引（仅8项，不是全部交流）</summary><ul>')
    for n in communications:
        parts.append('<li>'+e(n['id']+' · '+n['title']+' · 文档状态：'+n['state'])+'</li>')
    parts.append('</ul></details><details><summary>同事件多档案映射（去重依据）</summary><ul>')
    for key, values in duplicate_events.items():
        parts.append('<li>'+e(key+' → '+', '.join(values))+'</li>')
    parts.append('</ul></details><p>本轮未删除旧文件，未改动生产代码、资源、实例或存档；未编译或游戏测试。</p></section>')
    section = '\n'.join(parts)
    old = PLAN.read_text(encoding='utf-8')
    assert old.count('</body>') == 1
    new = old.replace('</body>', section+'\n</body>', 1)
    assert new.replace(section+'\n', '', 1) == old
    record = DOC/'讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_卷轴目录与新队员补谈三项确认.html')
    log = OUT/('codex-completion-design-'+stamp+'.json')
    validation = OUT/('codex-completion-validation-'+stamp+'.json')
    for p in [record, log, validation]:
        assert not p.exists()
    payload = {'time':now.isoformat(),'status':'三项已确认，目录候选，未实施','decisions':[{'question':q,'answer':a} for q,a in QUESTIONS], 'rules':rules,'findings':findings,'proposals':proposals,'pending':pending,'research_topics':[{'id':t['id'],'title':t['title'],'lab':t['lab']} for t in topics], 'communication_candidates':communications,'legacy_nodes':legacy,'multiple_nodes_per_event':duplicate_events,'sources':{str(p.relative_to(ROOT)):digest(p) for p in [catalog,legacy_path,communication]},'anchor':anchor}
    with log.open('x',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(new,encoding='utf-8')
    body = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>卷轴与个人经历补完确认</title><style>body{max-width:1100px;margin:32px auto;padding:20px;font:16px/1.8 system-ui;background:#14202e;color:#e4ecf5}a{color:#9ddfff}summary{cursor:pointer}</style><body><h1>卷轴目录与新队员补谈三项确认</h1><p>用户要求继续研究系统讨论；本轮完成源码索引与三项明确答复记录。纯彩蛋的分类细化此前“所有交流”的含义，不缩减正式对话和交流要求。旧档案仅作候选来源，未批准全部沿用。</p>'+section+'<p><a href="../09_测试发布/十二天重制计划与交付清单.html#'+anchor+'">返回计划本轮章节</a> · <a href="2026-09-28_16-47-04_个人终审卷轴文明等级与会面恢复确认.html">上一轮终审裁定</a> · <a href="2026-09-20_10-50_第三轮主线修改意见原文.html">卷轴原始范围</a> · <a href="2026-09-20_22-38_主线修改意见原文.html">队伍文明等级原始意见</a></p><footer>变更#1 · '+e(now.isoformat())+'：追加设计裁定和候选目录；历史保留，删除无。下一步细化文明等级里程碑及正式交流目录。</footer></body></html>'
    with record.open('x',encoding='utf-8') as f:
        f.write(body)
    assert PLAN.read_text(encoding='utf-8') == new
    assert record.read_text(encoding='utf-8') == body
    assert len(json.loads(log.read_text(encoding='utf-8'))['decisions']) == 3
    assert production() == before, '生产文件变化，须检查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':3,'topics':len(topics),'stages':dict(Counter(t['lab'] for t in topics)),'legacy_nodes':len(legacy),'legacy_distinct_events':len(by_event),'duplicate_event_groups':len(duplicate_events),'production_files_unchanged':len(before),'record':str(record),'log':str(log),'plan_anchor':anchor,'compiled':False,'deployed':False}
    with validation.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
