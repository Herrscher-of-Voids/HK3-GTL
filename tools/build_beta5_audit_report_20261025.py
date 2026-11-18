# -*- coding: utf-8 -*-
"""汇总已完成的逐份语义审计，生成离线报告及可追溯覆盖清单。

【变更记录 #1】2026-10-25（实际生成秒数写入输出 generated_at）
删除：无。新增：工业、主线、通用服务、客户端及测试审计的统一报告。
修改：按最新明确决定解释旧设计，不沿用历史主观总分；以能力状态和发布门槛呈现差距。
用途：只写审计交付文件，不修改模组版本、源码、资源或游戏实例；SHA不一致即拒绝生成。
"""
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/beta5-audit-20261025'
REPORT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/内测5全库完成度与正式版准备审计_20261025.html'
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')
LABELS = {'complete':'代码能力已闭合','partial':'部分实现','missing':'当前缺失','unknown':'待核实'}
SCORE = {'complete':1.0,'partial':0.5,'missing':0.0,'unknown':0.0}

# 这些细分只用于没有原子能力条款的九个审查域；每项均从该域已有的实现、差距和源码证据拆出。
MANUAL_CAPABILITIES = {
    'N08': [
        ('EU需求模拟、精确合计和真实后端扣款', 'complete', 'BigInteger合计；模拟不扣款，真实后端成功后才报告支付。'),
        ('真实配方推进时预留并提交HW', 'complete', '工作票据与配方进度绑定，只有真实推进才确认付款。'),
        ('失败回滚、逆序退款及退款重试', 'complete', '失败票据保留以便重试；覆盖已核对的EU/HW支付路径。'),
        ('HW账户任意精度、存档绑定与严格恢复', 'complete', '损坏数据拒绝重置，并以临时文件替换账本。'),
        ('世界泡、ERM/W13及工程机器消费者接入', 'partial', '已有公共支付组件，仍有机器消费者没有对应调用。'),
        ('物品/流体与能源之间的跨资源原子事务', 'missing', '工作票据没有覆盖物品、流体与能源的联合提交。'),
        ('目标实例多人、断线/重启及并发机器验收', 'unknown', '本轮是逻辑/存档检查，没有运行目标游戏实例。'),
    ],
    'gt_ae_integration': [
        ('GTL机器初始化期间注册HK3GTL机器', 'complete', 'GTMachinesMixin挂接GTL初始化尾部。'),
        ('生存/冒险模式限制创造箱和创造罐GUI', 'complete', '已实现右键GUI限制；范围不包括自动化能力提取。'),
        ('手机调用AE原生终端并保留网络/范围权限', 'complete', '调用原网络终端，不构造绕过权限的替代通路。'),
        ('拦截创造箱/罐经管道、漏斗、AE或能力接口自动提取', 'missing', '当前未见对应自动化取出限制。'),
        ('当前整合包全部跨模组版本与自动化路径实测', 'unknown', '本轮未运行游戏实例或完整自动化链。'),
    ],
    'N01': [
        ('索引GT机器真实生命周期', 'complete', '记录机器运行/停机及生命周期变化。'),
        ('机器目录按团队权限过滤', 'complete', '查询边界使用当前队伍权限。'),
        ('未加载区块保持未知且查询不强载', 'complete', '将未加载与运行/停机状态分开。'),
        ('目录和详情采用有界查询队列', 'complete', '避免无界同步扫描。'),
        ('客户端筛选与分页', 'complete', '详情查询和展示支持筛选分页。'),
        ('拆除、跨维度、重启及换队权限组合实测', 'unknown', '该组合未在本轮游戏中运行。'),
        ('大规模机器目录的目标实例压力验收', 'unknown', '历史单机记录只覆盖单台机器，不代表规模验收。'),
    ],
    'N07': [
        ('个人注视度原值、来源日志与阈值一次性触发', 'complete', '个人记录与阈值触发已有实现。'),
        ('在线队员最高有效值、缓冲减50及增长减半', 'complete', '依现行修订109规则计算，不用旧团队共享原始G口径。'),
        ('研究报价与研究速度公式接入', 'complete', '计算合同和研究服务已有调用。'),
        ('锚接口与HUD投影', 'complete', '存在接口及玩家侧显示。'),
        ('I36稳定锚和强化的真实供电提供者', 'missing', '接口存在，尚无对应正式机器提供者。'),
        ('ERM/W13研究加速消费者接入', 'missing', '设施真实增益调用尚缺。'),
        ('所有GTL工业路径独立降效合同', 'missing', '当前没有覆盖全GTL工业路径的实际执行。'),
        ('多人换队/上下线及真实锚耗电验收', 'unknown', '本轮没有目标实例多人运行记录。'),
    ],
    'N14': [
        ('500项彩蛋目录及条件文本', 'complete', '目录与条件说明已具备。'),
        ('彩蛋规则实际绑定', 'partial', '363/500条绑定；此项按条数计分，137条仍未绑定。', 363, 500),
        ('真实触发事务、作者归属、重放幂等和阅读回执', 'complete', '服务端事务和回执账本有实现。'),
        ('个人收藏账本与正式叙事分离', 'complete', '收藏作为独立可选目录管理。'),
        ('彩蛋471读取团队研究推进范围', 'missing', '现逻辑按个人UUID读取，未涵盖在线队伍研究推进。'),
        ('跨模组Mixin注入及全部触发的目标实例验收', 'unknown', '本轮没有逐条启动游戏触发500项。'),
    ],
    'N09': [
        ('手机128000 EU容量及LV充电能力', 'complete', '已有物理电池与充电规则。'),
        ('服务端操作收费与节流', 'complete', '操作端检查付款和频率。'),
        ('应用安装与电量门禁', 'complete', '应用服务保留安装及电量条件。'),
        ('通知持久化、去重与离线记录', 'complete', '通知生命周期受服务端记录。'),
        ('个人笔记CAS冲突保护', 'complete', '并发写入使用版本保护。'),
        ('AE终端委托并保留原生网络/权限/范围检查', 'complete', '手机链路委托现有终端。'),
        ('目标实例GT充电槽及AE无线界面验收', 'unknown', '本轮未操作GUI或实际充电槽。'),
        ('断线冲突恢复与多人并发操作验收', 'unknown', '本轮没有目标实例多人操作。'),
    ],
    'N10': [
        ('20联系人、离线回复目录和动态消息', 'complete', '当前范围为20联系人、560离线回复及60动态。'),
        ('阶段0–4状态变化与联系人解锁', 'complete', '当前缩减范围的阶段逻辑已接入。'),
        ('个人历史回看及有界消息保存', 'complete', '历史按用户保留，并设置内存上限。'),
        ('可选AI显式配置、自费请求及超时/响应限制', 'complete', 'HTTPS/本机地址由客户端明确配置，不自动重试。'),
        ('旧连接回包的epoch隔离', 'complete', '旧会话回包不能污染新连接状态。'),
        ('外部模型实际服务及端到端对话验收', 'unknown', '本轮仅做本地HTTP模拟，没有调用真实模型服务。'),
        ('仅靠关键词过滤保证外部模型人格语义', 'partial', '客户端过滤不能对任意外部模型提供完整语义保证。'),
    ],
    'welcome_updates': [
        ('按用户版本确认阅读并在登录队列展示', 'complete', '阅读确认遵循账号版本状态。'),
        ('登录提示不抢占当前界面', 'complete', '提示排队显示。'),
        ('更新历史展示', 'complete', '更新记录可显示。'),
        ('反馈内容复制', 'complete', '反馈文案可复制。'),
        ('显示已列出的注册与契约健康数据', 'complete', '健康视图按当前列明的注册源展示。'),
        ('多版本、重连及不同GUI缩放的实机覆盖', 'unknown', '本轮未运行多版本GUI兼容验收。'),
    ],
    'release_compatibility': [
        ('关键动作由服务端权威判定并投影到客户端', 'complete', '服务端权限与客户端状态投影均有实现。'),
        ('SavedData损坏时拒绝静默重置', 'complete', '损坏状态采用拒绝/保护处理。'),
        ('GTL/AE等可选依赖兼容路径与JEI检查', 'complete', '源码隔离与本轮相关逻辑检查有证据。'),
        ('当前仓库离线Gradle check', 'complete', '本轮check通过77个任务，其中70执行、7最新。'),
        ('当前实例最终配方替换/KubeJS及依赖组合实测', 'unknown', '本轮没有启动当前目标实例验证最终注册。'),
        ('MAX至终局新档专服多人、死亡、重启及重复操作验收', 'unknown', '没有本轮完整流程运行证据。'),
        ('最终整包低于8GB、12视距和光影验收', 'unknown', '负责人决定在最终内容齐备后执行，当前没有达标记录。'),
        ('增强版2.9.2兼容验收', 'unknown', '当前实例版本仍待负责人更新后实测。'),
    ],
}


def read(name):
    return json.loads((LOG / (name + '.json')).read_text(encoding='utf-8-sig'))


def save(name, value):
    (LOG / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def build_percentage_audit(summary, industry):
    """将已审计条款转换成可复算的工程完成度；原始审计结论不在此改写。"""
    systems = []
    for system in summary['systems']:
        capabilities = []
        if system['capabilities']:
            source_rows = system['capabilities']
            for c in source_rows:
                status = c.get('status', 'unknown')
                weight = float(c.get('possible', 1))
                earned = float(c.get('earned', SCORE.get(status, 0.0) * weight))
                capabilities.append({
                    'claim': c.get('claim') or c.get('capability', ''),
                    'status': status,
                    'score_percent': round(earned / weight * 100, 1) if weight else 0,
                    'earned': earned,
                    'possible': weight,
                    'reason': c.get('reason', ''),
                    'evidence': c.get('evidence', []),
                    'scoring_basis': '原分域审计能力条款；每条等权，partial折半。',
                })
        else:
            definitions = MANUAL_CAPABILITIES.get(system['id'])
            if not definitions:
                raise ValueError('没有能力条款或人工评分拆分: ' + system['id'])
            evidence = system.get('evidence', [])
            if not evidence:
                evidence = [{'path': 'logs/beta5-audit-20261025/audit-summary.json',
                             'claim': system['id'] + '：系统级实现/差距摘要；逐条拆分依据见本评分JSON。'}]
            for definition in definitions:
                claim, status, reason, *custom_score = definition
                possible = float(custom_score[1]) if custom_score else 1.0
                earned = float(custom_score[0]) if custom_score else SCORE[status] * possible
                capabilities.append({
                    'claim': claim,
                    'status': status,
                    'score_percent': round(earned / possible * 100, 1) if possible else 0,
                    'earned': earned,
                    'possible': possible,
                    'reason': reason,
                    'evidence': evidence,
                    'scoring_basis': '依据该系统既有implemented/gaps及所列源码证据人工拆为等权工作能力；彩蛋绑定量按500条计。',
                })
        earned = sum(c['earned'] for c in capabilities)
        possible = sum(c['possible'] for c in capabilities)
        counts = Counter(c['status'] for c in capabilities)
        systems.append({
            'id': system['id'], 'name': system['name'], 'group': system['group'],
            'percent': round(earned / possible * 100, 1) if possible else 0,
            'earned': round(earned, 3), 'possible': round(possible, 3),
            'counts': {k: counts.get(k, 0) for k in ('complete', 'partial', 'missing', 'unknown')},
            'capability_count': len(capabilities), 'capabilities': capabilities,
            'implemented': system.get('implemented', []), 'gaps': system.get('gaps', []),
            'evidence': system.get('evidence', []), 'unknowns': system.get('unknowns', []),
            'runtime': system.get('runtime', ''),
        })
    if len(systems) != 36:
        raise ValueError('审查域数量变化，须重新审定等权总分: ' + str(len(systems)))
    mean = sum(s['earned'] / s['possible'] * 100 for s in systems) / len(systems)
    all_earned = sum(s['earned'] for s in systems)
    all_possible = sum(s['possible'] for s in systems)
    metrics = {
        'multiblock_formal': {'label': '正式结构形态', 'earned': 26, 'possible': 88,
                              'percent': round(26 / 88 * 100, 1),
                              'note': '正式接入数量比；不代表结构外观批准或游戏成型验收。'},
        'multiblock_approved': {'label': '明确批准结构形态', 'earned': 29, 'possible': 88,
                                'percent': round(29 / 88 * 100, 1),
                                'note': '外观批准数量比；批准不等于正式接入。'},
        'easter_rules': {'label': '彩蛋规则绑定', 'earned': 363, 'possible': 500,
                         'percent': round(363 / 500 * 100, 1),
                         'note': '实际规则绑定条数比；未弱化尚无依赖的触发条件。'},
    }
    return {
        'schema': 'hk3gtl-beta5-percentage-audit-v1',
        'generated_at': NOW,
        'overall': {
            'percent': round(mean, 1), 'earned': round(mean, 3), 'possible': 100,
            'domain_count': len(systems), 'formula': '36个审查域的百分比算术平均；每域等权。',
            'raw_clause_score_percent': round(all_earned / all_possible * 100, 1),
            'raw_clause_earned': round(all_earned, 3), 'raw_clause_possible': round(all_possible, 3),
            'raw_clause_note': '能力条款数和粒度差异很大，不作为总体完成率；仅供复核计分算术。',
            'interpretation': '源码/工程能力完成度估算，不是生存通关率、实机验收率或正式发布通过概率。',
        },
        'scoring': {
            'complete': 100, 'partial': 50, 'missing': 0, 'unknown': 0,
            'unknown_note': '待核实按0计入本次保守得分，但单列为unknown；这不表示审计已证实该能力不存在。',
            'partial_note': '统一按半项折算，避免仅因代码存在就把部分职责视为完成。',
            'granularity': '每个系统内能力等权；N14的规则绑定子项按363/500的实际条数比例计权。',
            'release_test_boundary': '实机/版本/多人等未验收项仍按unknown单列，不由源代码覆盖率或Gradle check替代。',
        },
        'methodology': [
            '36个审查域分别先计算能力项完成率，再对36个域等权平均；避免16阶材料64条款或窄功能域因条目多而支配总体。',
            '前27域使用原分域审计能力条款；后9域无原子条款，按该域已记录实现、差距及源码证据人工拆成具名工作能力。',
            '一项能力complete计1、partial计0.5、missing计0、unknown计0；unknown明确表示证据待核实，0只表示当前没有可计入的已核实分值。',
            '36域等权估算不等于发布门槛通过。正式结构、外观批准、彩蛋绑定保留独立业务分母，不混入或冒充系统等权总分。',
        ],
        'business_metrics': metrics,
        'systems': systems,
        'source_reports': ['audit-summary.json', 'industry-audit.json', 'progression-audit.json',
                           'general-audit.json', 'client-audit.json', 'test-audit.json'],
        'release_recommendation': '当前分数用于定位工程欠项；正式版1.0仍须逐项满足既定内容、多人实机和发布门槛。',
    }


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_link(path, line=None):
    # 离线HTML链接使用相对文件路径，代码行号保留在文字中，不依赖浏览器跳行。
    from urllib.parse import quote
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return quote(os.path.relpath(p, REPORT.parent).replace('\\','/'), safe='/.:')


def esc(x):
    return html.escape(str(x))


def source(e):
    if isinstance(e, str):
        return '<span>'+esc(e)+'</span>'
    p = e.get('path','')
    detail = e.get('claim') or e.get('reason') or e.get('note') or e.get('excerpt','')
    title = p + (':' + str(e['line']) if e.get('line') else '')
    return ('<a href="'+rel_link(p)+'">'+esc(title)+'</a>' if p else '') + (' — '+esc(detail) if detail else '')


def bullets(rows):
    return '<ul>'+''.join('<li>'+esc(x)+'</li>' for x in rows)+'</ul>' if rows else ''


def main():
    inventory, industry, progression, general, client, tests = [read(n) for n in [
        'repository-inventory','industry-audit','progression-audit','general-audit','client-audit','test-audit']]
    manifests = {
        '通用服务/适配器':general['file_reviews'],
        '工业/配方/能量':industry['reviewed_files'],
        '主线/持久化/场景':read('progression-reviewed-files'),
        '客户端':client['file_reviews'],
    }
    file_map = {}
    for reviewer, rows in manifests.items():
        for row in rows:
            p = row['path']
            current = sha(ROOT/p)
            assert current == row['sha256'], ('审计后文件身份变化',p)
            entry = file_map.setdefault(p, {'path':p,'sha256':current,'reviewers':[]})
            entry['reviewers'].append(reviewer)
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/'src/main/java').rglob('*.java')}
    assert set(file_map) == actual, {'missing':sorted(actual-set(file_map)), 'extra':sorted(set(file_map)-actual)}
    snapshot = {x['path']:x['sha256'] for x in inventory['files']['main_java']}
    unchanged = all(snapshot.get(p)==v['sha256'] for p,v in file_map.items())
    assert unchanged, '初始快照后主源码发生变化'
    for row in tests['file_reviews']:
        assert sha(ROOT/row['path']) == row['sha256'], row['path']
    assert sha(ROOT/'build.gradle') == tests['build_gradle']['sha256']
    for row in inventory['files']['main_resources']:
        assert sha(ROOT/row['path']) == row['sha256'], ('审计后主资源变化',row['path'])
    coverage = {'generated_at':NOW,'main_java_total':len(actual),'semantic_review_unique':len(file_map),
                'missing':[],'extra':[],'snapshot_unchanged':unchanged,
                'main_java':list(sorted(file_map.values(),key=lambda r:r['path'])),
                'test_java_total':tests['counts']['java_test_sources'],
                'test_reviews':'logs/beta5-audit-20261025/test-audit.json',
                'resources':{'files':inventory['counts']['main_resources'],
                             'json_checked':inventory['json_files_checked'],
                             'syntax_failures':inventory['json_syntax_failures'],
                             'duplicate_keys':inventory['json_duplicate_keys'],
                             'snapshot_unchanged':True,
                             'scope':'资源全量身份/JSON语法检查；相关业务资源按分域审计语义核对，不声称所有图片均视觉验收。'}}
    save('coverage-verification.json',coverage)
    systems=[]
    for s in industry['systems']:
        caps=[{'claim':c['capability'],'status':c['status'],'reason':c.get('reason',''),
               'evidence':c.get('evidence',[])} for c in s['clauses']]
        systems.append({'id':'soulium_line' if s['id']=='N08' and '魂钢' in s['name'] else s['id'],'name':s['name'],
                        'group':'工业与建筑','status':'partial','verdict':'部分实现；详见逐项能力',
                        'capabilities':caps,'implemented':s.get('implemented',[]),'gaps':s.get('gaps',[]),
                        'evidence':s.get('design_basis',[]),'unknowns':s.get('unknown',[]),
                        'runtime':'逻辑/合同检查与游戏运行分开；当前没有本轮生存首通或成型验收。'})
    for s in progression['systems']:
        systems.append({'id':s['id'],'name':s['name'],'group':'研究、文明与主线',
                        'status':s.get('status','partial'),'verdict':s.get('summary') or s.get('status','partial'),
                        'capabilities':s.get('capabilities',[]),'implemented':s.get('implemented',[]),
                        'gaps':s.get('gaps',[]),'evidence':s.get('design_evidence',[])+s.get('code_evidence',[]),
                        'unknowns':s.get('unknowns',[]),'runtime':'本轮仅源码/逻辑检查；历史实例证据请见原分域审计。'})
    for s in general['systems']:
        systems.append({'id':s['id'],'name':s['name'],'group':'通用服务与发布','status':'partial',
                        'verdict':s['status'],'capabilities':[], 'implemented':s['implemented'],
                        'gaps':s['gaps'],'evidence':s.get('evidence',[])+([{'path':s['decision_source'],'claim':'现行设计/后续明确决定'}] if s.get('decision_source') else []),
                        'unknowns':[],'runtime':s['runtime']})
    # 客户端作为上述同一系统的交叉验证，另列来源而不再重复计入系统数或完成率。
    count=industry['counts']
    blockers=[
        {'name':'建筑与机器执行器','detail':'26/88种形态已正式接入，29/88种获明确外观批准；I19–I25的外观或批准不等同正式机器运行。'},
        {'name':'工业首通与供料','detail':'16阶主材有231种实体形态及351项配方展开。跨线研究/供料待补验；I14/I15/I16/I18共32项工单受策略锁定，I16的HDV首建链待接通。'},
        {'name':'能源生产与工程事实','detail':'反应堆和双能账本有算法；I19–I22生产控制器未接入，I23等能源机器、每堆15种燃料及逐机15个独立项目待完成。'},
        {'name':'世界泡工业及文明后期','detail':'世界泡目录/账本已有代码；机器生产、任务事实和资源交付调用入口待接通，C6/C7所需奇观与休伯利安工程事实提供者待补。'},
        {'name':'叙事迁移与终局','detail':'正式档案108项有来源，64项仍需决定迁移来源；终审工程准入当前返回WAITING。按最新叙事改造决定完成迁移，不恢复已否决旧内容。'},
        {'name':'指定整包全流程验收','detail':'本轮check通过；最终内容下MAX→终局新档、专服多人、重启/断线、物品与能量守恒、全部UI/渲染尚无实机验收记录。增强版2.9.2须在负责人更新实例后核验。'},
    ]
    priorities=[
        '继续既定结构序列：先评审I25，再做I26。每5台明确批准才接入；当前batch-07为I22/I23/I24，3/5。',
        '完成工业前段：I14–I16魂钢末端、I18及HDV首建；逐条解锁32项工单，并验证主材—机壳—电路—机器的研究与供料。',
        '接通I19–I23能源与I24起世界泡真实执行，把真实事实提供给研究/文明；不以辅助账本或假回调代替机器。',
        '补奇观、休伯利安及C6/C7工程链，再完成正式叙事迁移、终审及结局闭环。',
        '在最终内容齐备后做指定增强版实例的单人/专服多人、持久化与全流程验收；按既定后置顺序检验内存、12视距及光影，再发布1.0。',
    ]
    changes=[
        '数量采用最新“每阶至少5台”：69只是具名形态表。84为理论下限，当前证据下保留映射需要88；额外19个是未命名名额，本轮没有擅自命名或批准新机。',
        '逐台电压按已授权提案制作，不再把映射描述为完全未定。首建档、额定能力与外观机壳分别核验。',
        '注视度按修订109：个人原始记录＋在线队员最高有效值；不能沿用被纠正的“缺团队共享原始G账本”结论。',
        '电路/电子旧结论已过时：52正式电路、64平台生产及5通用辅助已有代码，不再报告旧的51项生产缺失。',
        '五组织实物贸易取消、5600条扩展社交及FTB任务明确后置；不把取消范围强加回本次发布条件。现有草案/安装器仍需如实标记。',
        '正式档案旧64项等待来源是迁移缺口，不要求照搬旧剧本；私人补谈、彩蛋收藏与正式主线互相独立。',
    ]
    summary={'schema':1,'generated_at':NOW,'conclusion':'当前不具备HK3GTL正式版1.0条件；继续作为内测5完成主线，无需另开内测6。',
             'no_product_changes':True,'counts':count,'coverage':{k:v for k,v in coverage.items() if k!='main_java'},
             'systems':systems,'client_crosscheck':client['systems'],'client_gaps':client['gaps'],
             'general_findings':general['findings'],'historical_runtime':progression.get('runtime_evidence',[])+[
                 {'id':'RUNTIME-MATERIAL-R165','path':'logs/main-materials-r165/runtime-verification-v2.json',
                  'claim':'历史r165真实注册快照57965配方、主材/替换合同与部分JEI显示有核验记录；本轮仅重新查阅这些收据。',
                  'limits':['不是当前包或完整加工/供电/生存首通/多人验收。',
                            '合同与身份：logs/main-materials-r165/research-contract-runtime-v2.json；runtime-v2-identity-verification.json。',
                            '部分视觉：logs/main-materials-r165/runtime-v2-visual-verification.json；只证明当时具体可见内容。']}],
             'release_gates':blockers,
             'next_priorities':priorities,'decision_corrections':changes,
             'test_counts':tests['counts'],'test_limits':tests['important_limits'],
             'source_reports':['industry-audit.json','progression-audit.json','general-audit.json','client-audit.json','test-audit.json'],
             'report_path':REPORT.relative_to(ROOT).as_posix(),
             'i25_path':'deliveries/I25_世界泡坐标解析中心_三轴浑仪与双翼解算厅_V1_20261025/index.html',
             'methodology':['全部599份主Java及79份测试Java逐份语义审查，联合路径和SHA去重核验；未按文件数估算产品完成度。',
                            '全部3462项主资源建立文件身份并检查1810份JSON语法；相关规范/数据语义核对见分域清单。不是对每张图片的视觉验收。',
                            '最新设计与讨论按领域检索并实际阅读相关条款；349份历史讨论是索引口径，不声称每一条无关历史均逐字重新验收。',
                            '不审第三方JAR全部源码或历史生成器的全部代码；当前产品/客户端/测试/构建及仓库KubeJS属于本轮审计范围。',
                            '能力complete仅代表其具体代码职责达到计分定义；不代表对应系统、整模组或生存实机完成。系统间条款存在依赖和重叠。']}
    assert len({s['id'] for s in systems})==len(systems),'系统ID冲突'
    percentage = build_percentage_audit({'systems':systems}, industry)
    save('percentage-audit.json', percentage)
    save('audit-summary.json',summary)
    backup = REPORT.with_name(REPORT.stem + '_百分比改版前备份_20261025' + REPORT.suffix)
    if REPORT.exists() and not backup.exists():
        shutil.copy2(REPORT, backup)
    report_html(summary,tests,coverage,percentage)
    save('percentage-audit-change-log.json', {
        'schema': 1, 'generated_at': NOW,
        'report': REPORT.relative_to(ROOT).as_posix(),
        'previous_report_backup': backup.relative_to(ROOT).as_posix() if backup.exists() else None,
        'percentage_data': 'logs/beta5-audit-20261025/percentage-audit.json',
        'changes': [
            '新增36个审查域的等权百分比及逐能力 earned/possible、状态计分和证据。',
            '将9个摘要式通用系统按现存实现/差距拆成可审阅的能力项。',
            '将正式结构、批准结构和彩蛋绑定比例作为独立业务指标显示。',
            '报告主页以百分比及具体待办取代主状态标签；保留原审计事实JSON。',
            '报告新增链接至独立标准HTML交互面板。',
        ],
        'no_product_changes': True,
    })
    print(json.dumps({'report':str(REPORT),'systems':len(systems),'clauses':sum(len(s['capabilities']) for s in systems),
                      'overall_percent':percentage['overall']['percent'],
                      'main_java':len(file_map),'tests':tests['counts']['java_test_sources'],'generated_at':NOW},ensure_ascii=False))


def report_html(data,tests,coverage,percentage):
    css='''*{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#18232c;font:15px/1.75 "Microsoft YaHei",sans-serif}main{max-width:1320px;margin:auto;padding:30px 28px}h1{font-size:29px;margin:0 0 10px}h2{font-size:22px;margin:32px 0 12px}h3{font-size:18px;margin:18px 0 8px}a{color:#125a86;text-underline-offset:3px;overflow-wrap:anywhere}.muted{color:#526675}.lead{font-size:18px}.notice{background:#fff0df;border-left:5px solid #a65c13;padding:18px 22px}.counts{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}.metric{background:white;padding:17px}.metric strong{display:block;font-size:28px}.metric small{display:block;color:#526675}nav{display:flex;gap:20px;flex-wrap:wrap;margin:18px 0}table{border-collapse:collapse;width:100%;background:#fff}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d7dfe5;padding:12px}th{background:#e7edf2}details{background:white;margin:12px 0;padding:14px 18px;border:1px solid #d7dfe5}summary{cursor:pointer;font-weight:600;font-size:17px}.pill{display:inline-block;padding:1px 8px;background:#e7edf2;font-size:13px;font-weight:400;margin-left:8px}small{font-size:13px}li{margin-bottom:5px}code{font-family:Consolas,monospace;overflow-wrap:anywhere}.sources{font-size:13px}.sources li{margin:7px 0}.filters{display:flex;gap:12px;position:sticky;top:0;background:#f4f6f8;padding:12px 0;z-index:2}input,select,button{padding:9px;border:1px solid #aab9c4;background:white;color:#18232c;font:inherit}input{flex:1}button{cursor:pointer}.cap-complete{color:#24614a}.cap-missing{color:#9a3424}.cap-partial{color:#825010}.scroll{overflow:auto}.bar{display:flex;height:13px;background:#d7dfe5;margin:9px 0}.bar span{display:block;background:#315f7b}.bar .approved{background:#8ba6b7}.two{display:grid;grid-template-columns:1fr 1fr;gap:25px}.score{font-variant-numeric:tabular-nums;font-weight:700}.meter{height:9px;background:#d7dfe5;max-width:260px;margin:4px 0}.meter span{display:block;height:100%;background:#315f7b}@media(max-width:800px){.counts,.two{grid-template-columns:1fr 1fr}main{padding:20px 12px}.filters{position:static;flex-wrap:wrap}th,td{padding:8px}h1{font-size:24px}}@media print{.filters,nav,button{display:none}details{break-inside:avoid}body{background:white}main{padding:0}.counts{grid-template-columns:repeat(4,1fr)}}'''
    pcts={s['id']:s for s in percentage['systems']}
    gate_domains=[
        ['multiblocks'],
        ['tier_main_materials','components','casings','circuits_electronics','voltage_progression','industrial_lines','soulium_line'],
        ['energy_production','voltage_foundation'],
        ['N02','N04','N16','N05'],
        ['N03','N05','N06','N11','N12'],
        ['release_compatibility','all_dimension_height','tools_export','multiblocks','energy_production','N02','N05','N16','research','payment_persistence','gt_ae_integration'],
    ]
    gate_progress=[round(sum(pcts[i]['percent'] for i in ids)/len(ids),1) for ids in gate_domains]
    out=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内测5全库完成度与正式版准备审计</title><style>'+css+'</style></head><body><main>',
         '<p class="muted">HK3GTL · '+esc(data['generated_at'])+' · 香港时间 UTC+08:00</p>',
         '<h1>内测5全库完成度：'+str(percentage['overall']['percent'])+'%</h1>',
         '<p class="lead">36个审查域等权工程完成度估算为 <strong>'+str(percentage['overall']['percent'])+'%</strong>。正式版1.0目前仍需补齐下表的具体内容，并完成目标实例新档、多人、重启与兼容验收；无需另开内测阶段，留在内测5完成后可直接进入1.0。</p>',
         '<nav><a href="#machines">结构数量</a><a href="#gates">1.0门槛</a><a href="#systems">逐系统差距</a><a href="#checks">测试边界</a><a href="#sources">证据与覆盖</a></nav>',
         '<p><a href="'+rel_link(data['i25_path'])+'">打开下一台：I25「世界泡坐标解析中心」V1评审</a> · <a href="'+rel_link('logs/beta5-audit-20261025/audit-dashboard.html')+'">打开标准HTML交互面板</a> · <a href="'+rel_link('logs/beta5-audit-20261025/percentage-audit.json')+'">逐系统百分比JSON</a></p>',
         '<div class="notice">总体百分比衡量<strong>源码/工程能力</strong>，不等于生存通关率或正式发布通过概率。每域内能力等权；完整计100%、部分计50%、当前无完成证据计0%、待核实按0%计但明确标注“待核实”（不代表已证明不存在）。本轮未改产品版本、正式源码或游戏实例。</div>',
         '<div class="counts"><div class="metric"><strong>'+str(percentage['overall']['percent'])+'%</strong>36域等权工程完成度<small>每域先计分，再做算术平均</small></div><div class="metric"><strong>26 / 88</strong>正式结构形态<small>29.5%，正式接入数量比</small></div><div class="metric"><strong>29 / 88</strong>明确批准结构形态<small>33.0%，与正式接入分开</small></div><div class="metric"><strong>363 / 500</strong>彩蛋规则绑定<small>72.6%，实际规则绑定条数比</small></div></div>',
         '<h2 id="machines">还有多少台结构要做</h2>',
         '<p>具名表是<strong>69种形态／66个机器编号</strong>，其中I01含四种形态。最新数量要求是MAX四种＋新增16阶每阶至少五种，故<strong>84是理论最低数</strong>。按现行电压映射补足各阶缺口，需要<strong>88种</strong>；压到84还需四项有真实工业拓扑依据的重新定阶，目前未证明。</p>',
         '<div class="bar" aria-label="88种形态中26正式，3已批待接入，59其余"><span style="width:29.545%"></span><span class="approved" style="width:3.409%"></span></div>',
         '<p><strong>现口径仍有59个待设计／评审批准名额：40种具名形态＋19个未命名补充名额。</strong>它们并非59台全部没有画过；I19–I21已有候选，其几何也被I22继承，但没有各自单独明确批准。若按正式资源看，则还差62种＝43种具名未接入＋19个补充名额。</p>',
         '<p>具名待批准：<code>H01、I19–I21、I25–I45、W01–W15</code>。I22、I23、I24已批待接入，batch-07为<strong>3/5</strong>。I25本轮只交候选，未计入批准；没有提前实装。新增19个名额尚未逐一命名或作为新机器获批。</p>',
         '<p class="muted">若以后四项合法改档成立，总数可回落至84；保持29已批／26正式不变时，单纯数量差额为55／58。改档产生的重设计、重新批准与正式资源替换另计，旧批准不能自动继承，因此这不是届时实际待办总数。上述均是形态口径，不把网络注入器等69表外附属设备混入数量。</p>',
         '<h2 id="gates">正式版1.0的待办与核验</h2><p>“关联域参考分”是下方相关系统完成度的算术平均，用来定位工作；不表示发布门槛已通过，也不替代业务硬指标。</p><div class="scroll"><table><thead><tr><th>门槛</th><th>关联域参考分</th><th>需要补齐或核验的工作</th></tr></thead><tbody>']
    out += ['<tr><td>'+esc(b['name'])+'</td><td class="score">'+str(gate_progress[i])+'%</td><td>'+esc(b['detail'])+'</td></tr>' for i,b in enumerate(data['release_gates'])]
    out += ['</tbody></table></div><h3>推进顺序</h3>','<ol>'+''.join('<li>'+esc(p)+'</li>' for p in data['next_priorities'])+'</ol>',
            '<h2 id="systems">逐系统完成度与待办</h2>',
            '<p>36个系统各自提供分子、分母、百分比和证据。百分比是源码/工程能力估算；各系统之间不按条款总数加权。待核实项按0计分并独立标注，不能据此断言能力不存在。</p>',
            '<div class="filters"><input id="search" aria-label="搜索系统与缺口" placeholder="搜索系统、机器编号或缺口"><select id="group" aria-label="筛选领域"><option value="">全部领域</option>'+''.join('<option>'+esc(g)+'</option>' for g in dict.fromkeys(s['group'] for s in data['systems']))+'</select><button id="expand">展开可见系统</button></div><p id="results" class="muted"></p>']
    for s in data['systems']:
        score=pcts[s['id']]
        out += ['<details class="system" data-group="'+esc(s['group'])+'"><summary>'+esc(s['name'])+' <span class="pill">'+esc(s['id'])+'</span> <span class="score">'+str(score['percent'])+'%</span></summary>',
                '<p class="score">'+str(score['earned'])+' / '+str(score['possible'])+' 分 · '+str(score['capability_count'])+'能力项</p><div class="meter"><span style="width:'+str(score['percent'])+'%"></span></div>',
                '<div class="two"><section><h3>计分能力对应内容</h3>'+bullets(s['implemented'])+'</section><section><h3>待完成或实机核验</h3>'+bullets(s['gaps'])+'</section></div>',
                '<p class="muted"><strong>实机边界：</strong>'+esc(s['runtime'])+'</p>']
        if score['capabilities']:
            out += ['<div class="scroll"><table><thead><tr><th>能力要求</th><th>计入完成度</th><th>具体状态、差距与证据</th></tr></thead><tbody>']
            for c in score['capabilities']:
                ev=c.get('evidence',[])
                state='待核实（按0计，不代表已证明不存在）' if c.get('status')=='unknown' else ('该项证据已核实' if c.get('status')=='complete' else ('按折半计入' if c.get('status')=='partial' else '当前0分，具体事项见说明'))
                out.append('<tr><td>'+esc(c['claim'])+'</td><td class="score">'+str(c['score_percent'])+'%<small>（'+str(c['earned'])+' / '+str(c['possible'])+'）</small></td><td>'+esc(state+'：'+c.get('reason',''))+('<ul class="sources">'+''.join('<li>'+source(e)+'</li>' for e in ev)+'</ul>' if ev else '')+'</td></tr>')
            out.append('</tbody></table></div>')
        if s['unknowns']:
            out.append('<h3>待核实</h3>'+bullets(s['unknowns']))
        if s['evidence']:
            out.append('<details><summary>相关设计与源码</summary><ul class="sources">'+''.join('<li>'+source(e)+'</li>' for e in s['evidence'])+'</ul></details>')
        out.append('</details>')
    out += ['<h3>客户端交叉核对</h3><p>48份客户端Java已独立审查，覆盖手机、档案/通信、研究、总览、叙事/终审、可选AI、HUD和实体演出。它们是上述系统的客户端视角，未重复计入系统数量或总分。</p>']
    for c in data['client_crosscheck']:
        out.append('<details><summary>'+esc(c['id'])+'</summary><p>'+esc(c.get('source_status',''))+'</p>'+bullets(c.get('limits',[]))+'<ul class="sources">'+''.join('<li>'+source(e)+'</li>' for e in c.get('evidence',[]))+'</ul></details>')
    out += ['<h3>本轮确认的其他差距</h3>']
    for f in data['general_findings']:
        out.append('<details><summary>'+esc(f['title'])+'</summary><p>'+esc(f['action'])+'</p><ul class="sources">'+''.join('<li>'+source(e)+'</li>' for e in f['evidence'])+'</ul></details>')
    for f in data['client_gaps']:
        out.append('<details><summary>'+esc(f['id'])+' <span class="pill">'+esc(f['kind'])+'</span></summary><p>'+esc(f['conclusion'])+'</p><ul class="sources">'+''.join('<li>'+source(e)+'</li>' for e in f['evidence'])+'</ul></details>')
    out += ['<h3>历史实机证据仍有效的范围</h3><p>以下是本轮重新查阅的历史记录，不是本轮启动游戏取得的新验收。</p>']
    for r in data['historical_runtime']:
        out.append('<details><summary>'+esc(r['id'])+'</summary><p>'+source(r)+'</p>'+bullets(r.get('limits',[]))+'</details>')
    out += ['<h2>本轮纠正的旧口径</h2>',bullets(data['decision_corrections']),
            '<h2 id="checks">check通过的含义与限制</h2>',
            '<p><code>./gradlew.bat check --offline --console=plain</code>：<strong>BUILD SUCCESSFUL，1分43秒，77个任务（70执行、7已是最新）</strong>。69个自定义验证任务与日志逐一吻合（64 JavaExec＋5 Python）；标准test没有JUnit源，不能表述为全部JUnit或100%覆盖率。</p>',
            '<p>79份测试源码中63个主类直接执行、13份间接调用，3份旧测试不在check：<code>ResearchGraphIntegrityTest、ParallelDataTest、MultiRecipeScenarioTest</code>。它们有独立前置或旧断言，不能默认为已通过。</p>',
            bullets(data['test_limits']),
            '<p><a href="'+rel_link('logs/beta5-audit-20261025-gradle-check.log')+'">原始check日志</a> · <a href="'+rel_link('logs/beta5-audit-20261025/test-audit.json')+'">79份测试审查与任务调用图</a></p>',
            '<h2 id="sources">审计范围、覆盖与复核</h2>',bullets(data['methodology']),
            '<p>资源：3462项文件，1810份JSON语法检查无失败、无重复键；资源存在不等于可达。设计目录含大量反编译及生成文件，未把它们冒称为数万份设计文档。</p>',
            '<p>主源码并集599/599，无遗漏、无额外路径，与初始快照SHA逐份一致；本轮未改产品Java、build.gradle或版本。审计读取与写报告的时间分开记载，来源保留原字节。</p><ul>']
    for name in data['source_reports']+['coverage-verification.json','repository-inventory.json','rule-read-receipt.json']:
        out.append('<li><a href="'+rel_link('logs/beta5-audit-20261025/'+name)+'">'+esc(name)+'</a></li>')
    out += ['</ul><p class="muted">人工语义审查发现仍可能遗漏运行时组合问题；未运行的内容明确保留待验收。不以旧报告分数、辅助算法测试或本轮审查覆盖率替代产品完成度。</p></main>',
            '''<script>const cards=[...document.querySelectorAll('.system')],q=document.querySelector('#search'),g=document.querySelector('#group');function filter(){let n=0;const text=q.value.toLowerCase();for(const c of cards){c.hidden=!!((g.value&&c.dataset.group!==g.value)||(text&&!c.textContent.toLowerCase().includes(text)));if(!c.hidden)n++;}document.querySelector('#results').textContent='显示 '+n+' / '+cards.length+' 个审查域';}q.addEventListener('input',filter);g.addEventListener('change',filter);document.querySelector('#expand').addEventListener('click',()=>{const visible=cards.filter(c=>!c.hidden),open=visible.some(c=>!c.open);visible.forEach(c=>c.open=open);});filter();</script></body></html>''']
    REPORT.write_text('\n'.join(out),encoding='utf-8')


if __name__=='__main__':
    main()
