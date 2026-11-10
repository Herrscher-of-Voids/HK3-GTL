"""保存文明八级成果及历史等级裁定；只更新设计文档。

变更#1：2026-09-28。新增八级条件、三项原问答和目录静态检查。
保留原页历史；不新增游戏等级锁，不改动源码、资源、实例或存档。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'doc/HK3GTL-内测5'
PLAN = DOC / '09_测试发布/十二天重制计划与交付清单.html'
LEVEL = DOC / '11_系统专项/进度与文明等级/进度与文明等级收口方案_v1.html'
CATALOG = ROOT / 'src/main/resources/data/hk3gtl/research/research_catalog.json'
OUT = ROOT / 'logs/research-migration-20260928'
DECISIONS = [
    {'question':'是否采用刚才列出的C0—C7八级名称与成果条件，作为文明等级方案？条件按级累计，读取真实完成记录；这次确认不批准新结构或新增配方数值。','answer':'采用这八级名称与成果条件（推荐）'},
    {'question':'文明等级是否只用于进度展示与最高等级的终审核验，不再额外锁机器、配方或研究？这些内容继续由具体课题、材料、设备和既定审查条件开放，避免等级与升级所需设备互相卡住。','answer':'不增加等级锁，终审仍要求最高级（推荐）'},
    {'question':'同一队伍已达到的文明等级，是否保留历史最高级、不因拆机或停机降级？终审当前工程资格仍单独复核；成员换队不携带旧队等级，新队按自身事实判定。','answer':'保留本队最高级，现有工程资格另查（推荐）'},
]
LEVELS = [
    {'id':'C0','name':'新生文明','condition':'起始状态。','research':[]},
    {'id':'C1','name':'崩坏识别','condition':'完成奥托首信与任一回信分支，完成崩坏能识别研究，取得真实采样和光谱检测记录。','research':['RN-HED']},
    {'id':'C2','name':'稳定工业','condition':'完成液态稳定化、介质再生研究，并实际完成稳定液生产和一次基础再生。','research':['RN-LES','RN-SMR']},
    {'id':'C3','name':'材料与核心','condition':'完成魂钢精密加工与核心结晶研究，实际制出合格魂钢加工件和基础核心晶体。','research':['RN-SPM','RN-CCE']},
    {'id':'C4','name':'量子航路','condition':'完成一审、世界泡坐标解析及无人采掘研究，并成功结算一次真实世界泡采掘任务。','research':['RN-WCP','RN-UED']},
    {'id':'C5','name':'虚数联系','condition':'完成虚数锚定、世界维系研究；取得真实世界泡终止回收、模拟世界泡构筑—稳定—回收，以及维系原型运行记录，完成二审。','research':['RN-IAA','RN-WME']},
    {'id':'C6','name':'文明奇观','condition':'完成工程验收方法研究，至少一座奇观通过真实运行验收。','research':['RN-CEE']},
    {'id':'C7','name':'认知与审判准备','condition':'100课题全部完成，十五座奇观及仿制休伯利安均取得工程验收记录，完成文明成果交叉验证。个人的对话与交流缺项仍由满卷轴单独核验。','research':'全部100课题'},
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before_source = production()
    topics = json.loads(CATALOG.read_text(encoding='utf-8'))['topics']
    index = {t['id']:t for t in topics}
    assert len(topics) == len(index) == 100
    done, active = set(), set()
    def visit(key):
        assert key in index, f'课题引用不存在：{key}'
        assert key not in active, f'课题循环：{key}'
        if key in done:
            return
        active.add(key)
        for parent in index[key]['prerequisites']:
            visit(parent)
        active.remove(key)
        done.add(key)
    for key in index:
        visit(key)
    for level in LEVELS:
        if isinstance(level['research'],list):
            assert all(k in index for k in level['research'])
    rules = [
        '用户确认八级名称与上述成果条件。条件逐级累计，读取真实完成记录，不用加权刷分，也不以电压等级代替文明等级。',
        '文明等级由队伍共享，仅用于展示和最高等级的终审核验；机器、配方、研究不新增文明等级门槛，仍按具体课题、设备、材料和既定审查规则开放。',
        '同一队伍保存历史最高级，拆机、停机不会使文明等级下降。历史成就不能代替现存工程资格：终审申请前仍按既定规则检查当前结构与验收有效性。',
        '换队不携带旧队文明等级，也不复制工程资格。新队根据自身有效事实判定；已确认可继承的研究与实验证据继续依原规则合并，不能因此推定工程、交流和审查历史也继承。',
        'C7不要求先获得终审入场许可或好结局。W15工程验收不得以完成终审为前置；其结构、供能与资格核验工况的验收和玩家获准入场是不同结果。',
        '二审是C5成果条件，但二审不得反过来以C5为前置；一审与C4、首座奇观与C6同理。等级读取成果，不产生解锁升级所需成果的门槛。',
        'C7的全部研究与工程成果为团队侧条件；每位申请人的正式对话、交流和补行会面仍单独核验。纯彩蛋是额外收藏，不纳入满卷轴准入前置。',
        'C5模拟构筑、稳定、回收记录应能追溯至实际模拟批次，真实世界泡记录另账；具体生产验收参数仍按各系统后续工况制定。',
    ]
    boundaries = [
        '本轮覆盖旧稿C0—C7名称与条件待定的状态，并否定旧页将“权重平衡”列为必须实现内容的推定；新规则使用成果集合，不靠权重刷级。旧页其他奖励、迁移等默认提案不因本轮获批。',
        '奇观拆除/搬迁须重验、终审入场前复核而入场后固定快照继续有效；文明等级不降级不会覆盖上述要求。',
        '仿制休伯利安搬迁复验、团队解散后的资产接管及审查资格跨队边界仍需按专项处理；本轮不把奇观规则自动扩展到所有设施。',
        '静态检查只涵盖100课题目录前置存在且无环，以及本轮课题引用有效；没有验证全部生产配方、实验入口、设备工况或真实玩家流程。',
        '不额外要求重新制造玩家已经真实完成且归属有效的成果。各历史事实须保留来源；具体事件ID与持久化实现尚未完成。',
    ]
    e = lambda x:escape(str(x),quote=True)
    anchor = 'civilization-milestones-'+stamp
    parts = [f'<section class="panel decision" id="{anchor}"><h2>已确认：文明C0—C7成果条件与历史最高级</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong。原始消息精确时间未知。三项答复已确认，尚未实现。</p>']
    for d in DECISIONS:
        parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>用户答复：</b>'+e(d['answer'])+'</p>')
    parts.append('<h3>逐级累计成果</h3><ol start="0">')
    for level in LEVELS:
        refs = '、'.join(level['research']) if isinstance(level['research'],list) else level['research']
        parts.append('<li><b>'+e(level['id']+' '+level['name'])+'</b>：'+e(level['condition'])+('<br>研究引用：'+e(refs) if refs else '')+'</li>')
    parts.append('</ol>')
    for title, rows in [('已确认规则及落实边界',rules),('覆盖关系与检查限度',boundaries)]:
        parts.append('<h3>'+title+'</h3><ul>'+''.join('<li>'+e(r)+'</li>' for r in rows)+'</ul>')
    parts.append('<p>本轮仅修改设计资料；不编译、不部署、不执行游戏测试，不修改源码、资源或存档。</p></section>')
    section = '\n'.join(parts)
    old_plan = PLAN.read_text(encoding='utf-8')
    assert old_plan.count('</body>') == 1
    new_plan = old_plan.replace('</body>',section+'\n</body>',1)
    assert new_plan.replace(section+'\n','',1) == old_plan
    old_level = LEVEL.read_text(encoding='utf-8')
    match = re.search(r'<body\b[^>]*>',old_level)
    assert match
    notice = '\n'+section+'<p><a href="../../09_测试发布/十二天重制计划与交付清单.html#'+anchor+'">现有计划中的本轮裁定</a></p><p>以下保留旧稿及上一轮提示用于追溯；其中“名称与条件待核对”状态已由上方本轮确认覆盖，其他未经明确批准的旧提案仍非定稿。</p>\n'
    new_level = old_level[:match.end()]+notice+old_level[match.end():]
    assert new_level.replace(notice,'',1) == old_level
    record = DOC/'讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_文明八级成果及历史最高级确认.html')
    log = OUT/('civilization-milestones-confirmed-'+stamp+'.json')
    validation = OUT/('civilization-milestones-validation-'+stamp+'.json')
    for p in [record,log,validation]:
        assert not p.exists()
    payload = {'time':now.isoformat(),'status':'用户已确认，游戏未实施','decisions':DECISIONS,'levels':LEVELS,'rules':rules,'boundaries':boundaries,'parameters':{'scope':'team','cumulative':True,'historical_maximum':True,'extra_level_unlock_gates':False,'final_audience_requires_highest':True,'transfer_team_level':False},'catalog_hash':sha(CATALOG),'anchor':anchor}
    with log.open('x',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(new_plan,encoding='utf-8')
    LEVEL.write_text(new_level,encoding='utf-8')
    body = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>文明八级成果确认</title><style>body{max-width:1100px;margin:32px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 system-ui}a{color:#9ddfff}li{margin:12px 0}</style></head><body><h1>文明八级成果与历史等级确认</h1><p>用户要求继续研究系统设计。先核对旧文明等级稿、100课题目录及上一轮卷轴裁定，再提出具体八级条件。用户对八级方案、无额外等级锁、本队历史最高级三项均明确同意。</p>'+section+'<p><a href="../11_系统专项/进度与文明等级/进度与文明等级收口方案_v1.html#'+anchor+'">文明等级正文最新裁定</a> · <a href="../09_测试发布/十二天重制计划与交付清单.html#'+anchor+'">计划本轮章节</a> · <a href="2026-09-28_17-06-38_卷轴目录与新队员补谈三项确认.html">上一轮卷轴与个人经历</a></p><footer>变更#1 · '+e(now.isoformat())+'：新增三项明确答复及八级条件；在原计划追加、原等级页顶部加入新裁定，旧文完整保留，删除无。下一步收口研究与审查仍有歧义的多人边界及各实验参数。</footer></body></html>'
    with record.open('x',encoding='utf-8') as f:
        f.write(body)
    assert PLAN.read_text(encoding='utf-8') == new_plan
    assert LEVEL.read_text(encoding='utf-8') == new_level
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert production() == before_source, '生产文件改变，须检查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':3,'levels':len(LEVELS),'catalog_topics':len(index),'catalog_dependencies_valid_and_acyclic':True,'production_files_unchanged':len(before_source),'history_preserved':True,'record':str(record),'log':str(log),'anchor':anchor,'compiled':False,'deployed':False,'game_tested':False}
    with validation.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
