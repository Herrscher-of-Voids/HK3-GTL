"""记录八项合并与研究所实验任务裁定，仅追加设计文件。

变更#1：2026-09-28，实际记录时刻写入输出。新增用户两项明确答复、覆盖关系、
机器职责映射及后续实施检查。删除无；不改生产资源、源码或历史讨论。
读取旧合并提案并核对八项接收设备，检查目录祖先；写入后回读并比较生产哈希。
此脚本为本轮记录工具，不应重复执行制造重复讨论记录。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'logs/research-migration-20260928'
PLAN = ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
SOURCE = OUT/'machine-merge-proposal-2026-09-28_04-00-19.json'
EXPECTED = {'I46':['I05'], 'I47':['I05'], 'I48':['I12'], 'I49':['I16'],
            'I50':['I16'], 'I51':['I11'], 'I52':['I05'], 'I53':['I16','I33']}
DECISIONS = [
    {'question':'八台补充设备是否采用这套完整合并分配：I46换热／I47废棒／I52气体净化→I05；I48基板→I12；I49蚀刻／I50封装终检→I16；I51无人装置装配返修→I11；I53容器由I16制壳、I33装配校准？工序、研究门槛分别保留，本次不删除旧文件或批准结构修改。',
     'answer':'采用这套八项分配（推荐）'},
    {'question':'研究前的工程验证是否采用研究所内的独立“实验任务”：ALE升级验证、OPR收支核验在S01起步，ERM隔离演算在S02起步；各占一个现有槽位、实际耗电，成功只记录证据，随后仍需正常付款研究？具体样件消耗另列，不把研究所变成通用生产机器。',
     'answer':'采用独立实验任务，共用现有槽位（推荐）'},
]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    hashes = production()
    proposal = json.loads(SOURCE.read_text(encoding='utf-8'))['proposal']
    assert len(proposal) == 8
    assert {r['old_machine']:r['receiving_machines'] for r in proposal} == EXPECTED
    cat_path = ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
    cat = {r['id']:r for r in json.loads(cat_path.read_text(encoding='utf-8'))['topics']}
    def ancestors(key, chain=()):
        assert key not in chain
        out = set()
        for parent in cat[key]['prerequisites']:
            out.add(parent); out.update(ancestors(parent, chain+(key,)))
        return out
    for row in proposal:
        assert set(row['receiving_unlocks']) <= ancestors(row['topic'])
    tasks = [
        {'topic':'RN-ALE','minimum_lab':'S01','purpose':'前级魂钢与电路样件的升级工程验证','result':'ALE实验证据，不直接开放S02'},
        {'topic':'RN-OPR','minimum_lab':'S01','purpose':'实际回收批次的物料收支核验','result':'OPR实验证据，不直接赠送高效回收'},
        {'topic':'RN-ERM','minimum_lab':'S02','purpose':'普通与侵蚀核心辅助的隔离演算对照','result':'ERM实验证据，不在验证阶段加速正式课题'},
    ]
    boundaries = [
        '已确认八项职责分配，保留每道工序和各自研究门槛；不新增I46至I53八座独立结构，现有69座范围不因此扩为77座。没有授权本轮删除、归档旧文件或修改结构。',
        'I05的换热、失活棒、气体净化与原介质再生分别配方；SMR扩回收种类，OPR改回收效率。无损回收、废棒复原全部能量、混成通用废液均不是本轮批准内容。',
        'I12基板与早期BCE适配基板分开；I16蚀刻、封装、电气终检分开。第一枚种子电路继续由前级可达设备制造，七条材料支线及精确配方未因分配确认而定稿。',
        'I11装配由UAA开放，返修由UPR开放，I26继续负责派遣与结算。当前目录UAA结果同时写返修，实施时需纠正此显示和门槛，不在本轮修改生产目录。',
        'I53职责拆为I16空壳/接口制造、I33装配/密封/场校准；BCC开放正式空容器，WBC负责捕获，不要求捕获产物制造第一个容器。',
        '已确认ALE/OPR在S01、ERM在S02起步的独立实验任务，共用原1/2/4/8/16槽位，不额外赠送实验槽；实际运行耗电，成功仅记证据，之后另行正常支付研究。',
        '实施约束：同一研究所的研究与实验必须统一计算占槽，不能两套队列各占满。预研实验不能走现有“先有本题证据才准入”的普通研究入口，否则自锁。',
        '本轮只批准这三类实验的承载方式，不自动把I02检测、I43验收或全部100课题迁入研究所。实验样件、消耗、功率和时长仍须配方核对。',
        '现有正式研究取消全额退还实际支付点数或材料规则不变。独立实验任务的样件扣取/中断/退料与权限需另列运行规格，不能借本次答复推定实验也产生研究付款账单。',
        '实际代码目前Hk3ResearchWorkQueue的Quote只接受points/materials且要求非空支付收据，start要求已有本题证据；槽位检查仅计研究jobs。可评估复用持久化/排程机制，不能宣称独立实验已经能直接运行。',
    ]
    pending = [
        '工艺分配与实验承载已确认，不再列为待批准；原历史稿保留，由本条覆盖其相应待定状态。',
        '接收机器的配方类型、物品/流体容量、供电、各模式可辨识性与首机制造仍需工程核查；功能确认不等于端口足够或批准重做外观。',
        '研究所实验的具体样件、执行权限、中断恢复与离线推进应形成单独运行规格；不得套用没有核对的队列行为。',
        '下一步讨论ERM与W13效果关系、作用范围及数值候选；既有数学代码中的+25%/+75%和2倍限制不因代码存在视为本轮批准。',
        '终审个人/团队归属、卷轴条件与其余叙事边界仍保留待定；不因研究工艺确认自动决定结局。',
    ]
    e = lambda x:escape(str(x), quote=True)
    anchor = 'research-merge-confirmed-'+stamp
    parts = [f'<section class="panel" id="{anchor}"><h2>已确认：八项工艺合并与研究所独立实验</h2><p>记录时间：{e(now.isoformat())}。用户原消息精确时间未知。仅记录设计裁定，未修改游戏。</p>']
    for d in DECISIONS:
        parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>实际答复：</b>'+e(d['answer'])+'</p>')
    parts.append('<h3>逐台职责分配</h3><ul>')
    for row in proposal:
        parts.append('<li>'+e(row['old_machine']+' '+row['function']+' → '+'＋'.join(row['receiving_machines']))+'。'+e(row['design'])+'</li>')
    parts.append('</ul><h3>研究前实验</h3><ul>')
    for r in tasks:
        parts.append('<li>'+e(r['topic']+'：'+r['minimum_lab']+'起步；'+r['purpose']+'；'+r['result'])+'。</li>')
    parts.append('</ul>')
    for title, values in [('确认范围与实施检查',boundaries),('覆盖关系与剩余事项',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<p>覆盖旧合并提案和S01/S02/S03/S04/S05接线稿中的相应待定项。其他具体工序、数字、资产和审批状态不变。生产文件哈希前后核对，未编译、部署或游戏测试。</p></section>')
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8');assert before.count('</body>') == 1
    after = before.replace('</body>',section+'\n</body>',1)
    assert after.replace(section+'\n','',1) == before
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_八项工艺合并及研究所实验任务确认.html')
    log = OUT/('merge-and-lab-experiments-confirmed-'+stamp+'.json')
    validation = OUT/('merge-and-lab-experiments-validation-'+stamp+'.json')
    for p in [record,log,validation]:assert not p.exists()
    source_files = [SOURCE,cat_path,ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchWorkQueue.java']
    payload = {'time':now.isoformat(),'status':'两项用户决定已确认，尚未实现','decisions':DECISIONS,
               'confirmed_mapping':EXPECTED,'approved_scope':'职责与三类实验承载；不含结构修改、删除文件或精确数值',
               'prior_proposal':proposal,'experimental_tasks':tasks,'boundaries':boundaries,'pending':pending,
               'anchor':anchor,'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in source_files},'game_changed':False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>工艺合并与实验任务确认</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}</style></head><body><h1>八项工艺合并及研究所实验任务确认</h1><p>用户要求继续收口研究系统；本轮核对旧八项提案、100课题目录及研究队列，提交两个独立设计问题。原始消息时间未知，以下为本轮落盘时间。</p>{section}<p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">现有计划中的确认段落</a> · <a href="2026-09-28_04-00-19_八台补充设备工艺合并提案与回收研究裁定.html">被本轮明确的原合并提案</a></p><footer>变更#1 · {e(now.isoformat())}：新增用户答复、映射与覆盖关系；修改既有计划为追加；删除无。用途为后续接线依据，非功能交付。</footer></body></html>'''
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['confirmed_mapping'] == EXPECTED
    assert hashes == production(), '生产文件变化，检查并发操作'
    result = {'time':now.isoformat(),'confirmed_answers':2,'mappings':8,'ancestor_checks':8,'lab_experiments':3,
              'production_files_unchanged':len(hashes),'previous_plan_preserved':True,'compiled':False,'deployed':False,
              'game_tested':False,'record':str(record),'log':str(log),'anchor':anchor}
    with validation.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
