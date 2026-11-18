"""记录一审多人三项裁定；仅更新设计资料，保留原文。

变更#1：2026-09-28，新增离线补行、代表断线、混队选代表的明确答复。
实际执行时间写入产物，生产文件只读；不将设计确认当成实现完成。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'doc/HK3GTL-内测5'
PLAN = DOC/'09_测试发布/十二天重制计划与交付清单.html'
STORY = DOC/'00_总纲/内测5完整主线方案与树状图_v4.html'
OUT = ROOT/'logs/research-migration-20260928'
DECISIONS = [
    {'question':'一审召入时有队员离线，是否让当时在线的队员先参加，离线成员上线后再补行个人会面？离线者不会被自动记为亲历，团队也不必一直等所有人同时上线。','answer':'在线队员先参加，离线者之后补行（推荐）'},
    {'question':'多人一审中，谁断线会让整场问答从头重开？建议只有答题代表断线才重开整场；其他成员断线不打断代表，缺席者之后从头补行自己的会面，不自动取得个人完成记录。','answer':'代表断线重开整场，其他人之后补行（推荐）'},
    {'question':'新老队员混合参加一审时，是否只从“尚未完成一审会面的在线成员”中随机选答题代表？整场仍只选三问，已完成者可以陪同但不能再次取得问答次数；只有已完成者时只允许回看，不开新问答。','answer':'未完成者中随机代表，整场共三问（推荐）'},
]
RULES = [
    '已确认：一审召入时，在线队员先参加；离线成员上线后另行补行个人会面，不阻塞在线队员，也不自动取得个人亲历完成记录。',
    '已确认：答题代表断线，整场问答从头重开；其他参与成员断线，不打断代表及其余成员，缺席者之后从头补行自己的会面，不自动记为完成。',
    '已确认：只从尚未完成一审会面的在线成员中随机选答题代表；整场共三问，不按人数叠加。已完成者可以陪同，但不能再次取得问答次数；全员已完成时只可回看，不开新问答。',
    '既有规则保持：已完成一审会面后换队，个人问答剩余次数为0；完成前换队的原三次资格规则不因本轮被删除。未完成会面的中途选择如何跨重开保存仍待明确。',
    '既有规则保持：补行会面保留原队审查结果，不重复授予团队技术；研究共享不等于替离线成员填写个人交流经历。',
    '既有规则保持：一审结束返回各自进入前的位置；终审则从已确认检查点恢复，不能将终审恢复规则套到一审。',
]
PENDING = [
    '代表断线后，从头重播是否保留已经确认的问题、已问次数；不得把本轮答复理解成允许断线刷新全部三次选择。',
    '代表重开时是否等待原代表回来，或从剩余合格成员重选；本轮只确认谁的断线影响整场，没有确认替补机制。',
    '会面中主动关闭界面、退队/被移出队伍与服务器重启的具体转移规则；不自动视为通过，也不擅自判坏结局。',
    '原位不可安全返回时的替代位置；尚未确认，不静默改成统一出生点。',
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    anchor = 'first-audience-multiplayer-'+stamp
    before_source = production()
    original = DOC/'讨论记录/2026-09-20_10-50_第三轮主线修改意见原文.html'
    previous = DOC/'讨论记录/2026-09-28_17-06-38_卷轴目录与新队员补谈三项确认.html'
    manager = ROOT/'src/main/java/com/sirin/hk3gtl/common/dialogue/DialogueSessionManager.java'
    assert '问答次数为0' in original.read_text(encoding='utf-8')
    assert '亲自补行会面，保留原队结果' in previous.read_text(encoding='utf-8')
    findings = [
        '主线v4的B5明确列出离线成员、断线作用范围和新老混队为待定；本轮三项答复收口这三处，不批准八问润色稿的全部文字。',
        '本轮阅读的DialogueSessionManager按玩家UUID维护内存会话，onPlayerDisconnect移除该玩家记录；该类没有承载本次设计所需的团队会面、代表和持久化三问状态。此为局部源码检查，不宣称全仓所有对话路径已审完。',
        '实现建议：会面身份、代表、参与情况、个人完成与团队技术授予分别保存；同一完成结算不能重复授予技术。具体断线重选与已问问题恢复策略需等后续裁定。',
    ]
    e = lambda v:escape(str(v),quote=True)
    parts = [f'<section class="panel" id="{anchor}"><h2>一审多人会面：三项已确认</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；原消息精确时间未知。设计已确认，游戏未实施。</p>']
    for d in DECISIONS:
        parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>用户答复：</b>'+e(d['answer'])+'</p>')
    for title,values in [('已确认与保留规则',RULES),('实际核对与实施建议',findings),('仍待明确，不能自动当作批准',PENDING)]:
        parts.append('<h3>'+title+'</h3><ul>'+''.join('<li>'+e(v)+'</li>' for v in values)+'</ul>')
    parts.append('<p>本轮仅追加文档与记录，无删除；未改Java、资源、结构、实例或存档，未编译、部署、游戏测试。</p></section>')
    section = '\n'.join(parts)
    old_plan = PLAN.read_text(encoding='utf-8')
    assert old_plan.count('</body>') == 1
    new_plan = old_plan.replace('</body>',section+'\n</body>',1)
    assert new_plan.replace(section+'\n','',1) == old_plan
    old_story = STORY.read_text(encoding='utf-8')
    match = re.search(r'<body\b[^>]*>',old_story)
    assert match
    notice = '\n<section class="panel"><h2>一审多人规则最新裁定</h2><p>'+e('在线队员先参加，离线者上线后补行；代表断线才重开整场，其他成员断线不打断代表并需另行补行；只从未完成会面的在线成员中随机选代表，整场共三问，已完成者仅陪同或回看。')+'</p><p>下方B5旧待定项的这三处已由本轮明确答复覆盖。已问问题重开处理、替补代表与安全返回仍待定；完整历史保留。</p><a href="../09_测试发布/十二天重制计划与交付清单.html#'+anchor+'">原问题、明确答复及未定边界</a><p>变更追加 · '+e(now.isoformat())+'；生产未实施。</p></section>\n'
    new_story = old_story[:match.end()]+notice+old_story[match.end():]
    assert new_story.replace(notice,'',1) == old_story
    record = DOC/'讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_一审多人离线补行与代表规则确认.html')
    log = OUT/('first-audience-multiplayer-confirmed-'+stamp+'.json')
    validation = OUT/('first-audience-multiplayer-validation-'+stamp+'.json')
    for p in [record,log,validation]:
        assert not p.exists()
    payload = {'time':now.isoformat(),'status':'三项已确认，未实施','decisions':DECISIONS,'rules':RULES,'findings':findings,'pending':PENDING,'anchor':anchor,'sources':{str(p.relative_to(ROOT)):sha(p) for p in [original,previous,manager,STORY]}}
    with log.open('x',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(new_plan,encoding='utf-8')
    STORY.write_text(new_story,encoding='utf-8')
    body = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>一审多人会面确认</title><style>body{max-width:1100px;margin:32px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 system-ui}a{color:#9ddfff}</style></head><body><h1>一审多人离线补行与代表规则确认</h1><p>用户要求继续研究与审查设计。查阅一审原始意见、主线B5及个人补行裁定后，提交三项未决问题，用户均明确采用本页答复。该补充细化旧“全队传入／断线重开”适用范围，未改变终审检查点恢复规则。</p>'+section+'<p><a href="../09_测试发布/十二天重制计划与交付清单.html#'+anchor+'">计划本轮章节</a> · <a href="../00_总纲/内测5完整主线方案与树状图_v4.html#B5">主线一审原章节</a> · <a href="2026-09-28_17-06-38_卷轴目录与新队员补谈三项确认.html">个人补行依据</a></p><footer>变更#1 · '+e(now.isoformat())+'：记录三项答复，原计划追加，原主线页顶部加覆盖提示；历史保留，删除无。下一步仅需明确重开时已问内容与替补代表等实际冲突。</footer></body></html>'
    with record.open('x',encoding='utf-8') as f:
        f.write(body)
    assert PLAN.read_text(encoding='utf-8') == new_plan
    assert STORY.read_text(encoding='utf-8') == new_story
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert production() == before_source, '生产文件发生变化，须检查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':3,'production_files_unchanged':len(before_source),'history_preserved':True,'record':str(record),'log':str(log),'anchor':anchor,'compiled':False,'deployed':False,'game_tested':False}
    with validation.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
