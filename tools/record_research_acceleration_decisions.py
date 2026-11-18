"""记录ERM/W13加速裁定和算例；只更新HTML设计与JSON记录。

变更#1：2026-09-28，实时记录时间写入产物。新增三项用户答复及三倍模型算例；
现有计划追加，旧公式文档顶部增加覆盖提示而保留历史公式和算例。
删除无；不改Java、研究资源或实例。输入为已读代码和设计稿，输出可核对记录。
模型检查不是生产测试；执行前检查已有记录，不重复运行制造重复决定。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'logs/research-migration-20260928'
PLAN = ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
FORMULA = ROOT/'doc/HK3GTL-内测5/04_研究系统/研究计算与注视度公式草案_v1.html'
DECISIONS = [
    {'question':'ERM侵蚀模块与W13母机的研究加速，采用哪种关系？两者都不增加研究点产量，多台同类设备也不无限叠加；具体倍率随后给你一组数值方案。',
     'answer':'两者加成相加，再设统一上限'},
    {'question':'W13的研究加速作用到哪里？建议只作用于明确绑定、获得授权的研究所；W13停机或卸载后失去该加速，但研究所自身能正常工作时继续按本地速度研究。',
     'answer':'只作用于明确绑定的授权研究所（推荐）'},
    {'question':'加速系数选哪一档？以下都是“正常速度＋两项加成”，再计算注视度减速；不增加槽位或研究点。沿用原数值稿为：ERM＋25%、W13＋75%，合计最高2倍（基础10分钟课题在无减速、持续供电时为5分钟）。',
     'answer':'提高：＋50%／＋150%，最高3倍'},
]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    hashes = production()
    math_path = ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchMath.java'
    queue_path = ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchWorkQueue.java'
    lab_path = ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java'
    math_source = math_path.read_text(encoding='utf-8')
    queue_source = queue_path.read_text(encoding='utf-8')
    lab_source = lab_path.read_text(encoding='utf-8')
    assert 'erosion ? 0.25' in math_source and 'wonder ? 0.75' in math_source
    assert 'speed > 2' in queue_source
    assert '0, false, false' in lab_source
    examples = []
    for label, erosion, wonder, expected in [('无加速',False,False,1),('仅ERM',True,False,1.5),('仅W13',False,True,2.5),('两者同时有效',True,True,3)]:
        multiplier = min(3, 1+0.5*erosion+1.5*wonder)
        assert multiplier == expected
        seconds = math.ceil(600*20/multiplier)/20
        examples.append({'case':label,'positive_multiplier':multiplier,'base_seconds':600,
                         'duration_seconds_no_pressure':seconds,'effective_conditions':'无注视减速、持续供电及20TPS，仅设计算例'})
    assert [r['duration_seconds_no_pressure'] for r in examples] == [600,400,240,200]
    contracts = [
        '用户确认：ERM与W13加成相加后设统一上限，不采用只取较高效果，也不将两个倍率相乘。',
        '用户确认：ERM有效时增加50%，W13有效时增加150%；加上正常速度，正向倍率最高3倍，再计算注视度减速。不增加研究槽位，不增加研究点计算机产点。',
        '正向倍率表达：A=min(3,1+0.50×e+1.50×w)，e/w表示该来源当前是否有效。沿用旧稿每类来源只记一次的设计，不通过重复摆放W13给同一研究所重复追加150%。',
        '作用范围已确认：W13只给明确绑定且获得授权的研究所提供加速；不能只因同队、距离接近或持有控制器就自动受益。',
        'W13停机/卸载后，该来源加速停止；若研究所仍具备自身工作条件，按剩余本地效果继续，不清除已有进度。全队离线暂停正式研究等既有规则仍适用。',
        '加速判定须来自真实成型、授权、有效运行与供能状态；研究本身仍逐槽正常供电，不能凭加速标志绕过停电暂停。具体W13服务容量及附加能耗未定。',
        '本次只确认两项加速系数、组合方式、作用对象与来源停止时行为；不把整个旧注视度公式、稳定锚参数、材料倍率或S01模块准入一并视为批准。',
        '研究前独立实验与正式研究分开。ERM自身隔离演算不能先要求ERM已解锁；W13自身研究不能先要求W13运行；不能通过加速跳过真实实验成功事件。',
    ]
    findings = [
        'Hk3ResearchMath.speed当前仍为(1+0.25e+0.75w)/(1+3q)，与本次+50%/+150%不同。',
        'Hk3ResearchWorkQueue.advance当前拒绝speed>2；实施时必须同步更新速度合法性校验，保留非有限/非正数检查，不能只改公式。',
        'Hk3ResearchInstituteMachine.researchTick当前传入erosion=false、wonder=false，未接通这两个真实来源；数学方法存在不代表模块或W13已运行。',
        '旧公式HTML中的原公式和交互算例保持历史内容，顶部新增明确覆盖提示。本轮新算例仅核对倍率与时长，没有执行生产Java或平衡测试。',
    ]
    pending = [
        'W13一台能服务的研究所/槽位数量、绑定与解除操作角色、同队变化的授权处理、机器耗能与是否按实际负载计费，需要下一组方案；本轮未授权无限服务。',
        'ERM模块的具体物品/供电成本、实验样件消耗、独立实验任务的中断与离线行为仍需运行规格；原正式研究退款规则不因此改变。',
        'W13还承担受控优化模型/工艺验证的候选职责；本轮仅确定研究加速，不自动给所有生产机器加速或削减配方材料。',
        '终审个人/团队结算、卷轴最终条件和其他跨系统事项尚未收口。旧终局专项文档中存在默认提案及与新奇观门槛不一致的表述，应按明确用户决定校对，不能直接当作当前批准。',
    ]
    e = lambda x:escape(str(x),quote=True)
    anchor = 'research-acceleration-confirmed-'+stamp
    parts = [f'<section class="panel" id="{anchor}"><h2>已确认：ERM＋50%与W13＋150%，合计最高3倍</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；原用户消息精确时间未知。裁定已确认，游戏尚未实现。</p>']
    for d in DECISIONS:parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>实际答复：</b>'+e(d['answer'])+'</p>')
    parts.append('<h3>10分钟基础课题的无减速算例</h3><ul>')
    for r in examples:
        seconds = int(r['duration_seconds_no_pressure'])
        parts.append('<li>'+e(f"{r['case']}：{r['positive_multiplier']}倍，{seconds//60}分{seconds%60}秒。")+'</li>')
    parts.append('</ul><p>以上按20TPS、持续供电及无注视减速计算；有减速时再计算，有停机时不计工作量。不是研究费用或W13耗能数值。</p>')
    for title, values in [('已确认与适用边界',contracts),('实际代码差距',findings),('仍待收口',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<p>覆盖本轮助手推荐的“取较高”方案，并覆盖旧+25%/+75%及最高2倍的加速候选；保留历史，不改其他公式或代码。未编译、部署或游戏测试。</p></section>')
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8'); assert before.count('</body>') == 1
    after = before.replace('</body>',section+'\n</body>',1)
    assert after.replace(section+'\n','',1) == before
    old_formula = FORMULA.read_text(encoding='utf-8')
    notice = f'''\n<aside class="panel" id="acceleration-update-{stamp}"><h2>2026-09-28加速参数已更新：以下旧稿仅供历史对照</h2><p>用户明确确认ERM＋50%、W13＋150%，加成相加后正向上限3倍，再计算注视度减速。W13只作用于明确绑定、获授权的研究所，停机/卸载停止该加速。本页下方原+25%/+75%、2倍公式和交互算例保留历史，不能作为当前加速参数；其他参数未因本次答复重新获批。</p><p>10分钟无减速算例：无加速10分钟，仅ERM为6分40秒，仅W13为4分钟，两者为3分20秒。游戏代码尚未同步。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">查看本次答复、当前算例及待实现清单</a></p><p>变更#2 · {e(now.isoformat())}：新增覆盖提示，保留全部旧内容；删除无，不修改游戏。</p></aside>\n'''
    match = re.search(r'<body\b[^>]*>',old_formula)
    assert match
    new_formula = old_formula[:match.end()]+notice+old_formula[match.end():]
    assert new_formula.replace(notice,'',1) == old_formula
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_研究加速相加三倍及授权绑定确认.html')
    log = OUT/('research-acceleration-confirmed-'+stamp+'.json')
    validation = OUT/('research-acceleration-validation-'+stamp+'.json')
    for p in [record,log,validation]:assert not p.exists()
    sources = [math_path,queue_path,lab_path,FORMULA]
    payload = {'time':now.isoformat(),'status':'用户确认，未实现','decisions':DECISIONS,'examples':examples,
               'confirmed_parameters':{'erm_bonus':0.5,'w13_bonus':1.5,'positive_speed_cap':3,'combination':'additive','scope':'explicit_authorized_bindings'},
               'contracts':contracts,'findings':findings,'pending':pending,'source_hashes_before':{str(p.relative_to(ROOT)):sha(p) for p in sources},
               'anchor':anchor,'game_changed':False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>研究加速与授权绑定确认</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}</style></head><body><h1>研究加速相加三倍及授权绑定确认</h1><p>承接用户“继续”及本轮八项工艺合并确认。用户不采用助手推荐的取高方案，明确选择相加并设上限，进一步选择+50%/+150%及3倍上限。</p>{section}<p>已实际读取旧研究数学、队列和研究所调用、公式草案及原主线讨论。新增结构化裁定、算例与本记录，追加现有计划，在旧公式顶部标明覆盖关系；回读核验并对比生产文件。没有改Java、资源、配方、结构、实例或存档。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">本轮完整确认</a> · <a href="2026-09-28_16-07-59_八项工艺合并及研究所实验任务确认.html">本轮已确认的八项合并与实验任务</a> · <a href="../04_研究系统/研究计算与注视度公式草案_v1.html">带覆盖提示的旧公式稿</a></p><footer>变更#1 · {e(now.isoformat())}：新增三项答复、覆盖关系及模型检查；删除无。当前产物为设计确认，不是生产验收。</footer></body></html>'''
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    FORMULA.write_text(new_formula,encoding='utf-8')
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    assert FORMULA.read_text(encoding='utf-8') == new_formula
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert hashes == production(), '生产文件变化，须检查并发操作'
    result = {'time':now.isoformat(),'confirmed_answers':3,'model_examples':examples,'previous_documents_preserved':True,
              'production_files_unchanged':len(hashes),'compiled':False,'deployed':False,'game_tested':False,
              'record':str(record),'log':str(log),'anchor':anchor}
    with validation.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':main()
