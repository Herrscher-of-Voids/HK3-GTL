"""研究重构前的逐项对照：读取旧注册、新目录及生产引用，不改运行时研究身份。

【变更记录 #1】2026-09-28 01:17:00（研究迁移准备，不增加模组修订）
删除：无。新增：77项人工语义对照及可复查源码引用。
修改：计划页追加迁移依据，不覆盖原计划或历史结论。
用途：区分工艺归并、用途拆分和事件/资格事实，禁止将此表用作旧完成状态自动兑换。
"""
from pathlib import Path
import collections
import datetime
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/research-migration-20260928'
PLAN = ROOT / 'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
# 同一行列出的多个RN是不同用途的候选去向，不表示任意一个完成即可解锁全部旧功能。
DECISIONS = '''
R-AB-001|相近迁移|RN-HED|基础识别归入新识别课题；旧持有物品自动完成不能照搬，保留首信和采样条件。
R-AB-002|用途拆分|RN-LES,RN-CCE|普通结晶副产物与仿制核心结晶是不同工艺，不能仅凭“结晶”二字合并。
R-AB-003|用途拆分|RN-SSP,RN-NBS,RN-NRA,RN-NSP,RN-HRC,RN-SPC,RN-SRA,RN-SPM|旧魂钢总许可拆成八段工艺；旧材料、物品和加工实现按用途复用。
R-AB-025|事件事实||转入奥托首信已收到/回复事实，不再注册研究；合作和拒绝均可继续。
R-WL-001|相近迁移|RN-RCA|构造能力归入仿制理核心，仍需白名单及逐电路独立解锁，馈赠剧情本身不授予研究。
R-AB-004|工艺归并|RN-BCE,RN-SPM|取消独立电压许可；电路用途与精密部件用途分别判断，非统一替换。
R-AB-005|用途拆分|RN-BCE,RN-MCE|起步种子与适配部件使用BCE；多层蚀刻使用MCE，不能拿后期封装锁死首枚电路。
R-AB-006|用途拆分|RN-SPM,RN-HFB|精密部件与框架归SPM；实际引用中的能量转换器不属于部件课题，须单独核对能源路线。
R-AB-007|用途拆分|RN-SRE,RN-MRE,RN-LRE,RN-URE|旧反应堆原理不能解锁四档全部工况；按真实反应堆职能拆分，不能只看旧机器名字。
R-AB-008|用途拆分|RN-HER,RN-CED,RN-LTA,RN-ERM|名字是双能源，但实际挂了档案室和生物运算配方；分别核对能源、资料和演算用途。
R-AB-009|用途拆分|RN-HFB,RN-CED,RN-VRC|起步网络注入已迁HFB；能源调度与跨界通讯分别迁移，不给账户增加人为范围限制。
R-AB-010|相近迁移|RN-LTA,RN-LTB|实物逆向与资料交叉验证分别接线；先读实际产物，不能提前获得后续遗留证据。
R-AB-011|工艺归并|RN-SPM,RN-MCE|电压许可取消；部件与调制器归加工，电路归蚀刻；事件里程碑另查。
R-AB-012|用途拆分|RN-MCE,RN-SPC,RN-SRA,RN-SPM|实际同时用于电路、魂钢铸锭、原质稳定、框架和数据核心，必须按配方逐条分开。
R-AB-013|用途拆分|RN-LES,RN-SSC,RN-CFR,RN-NBS,RN-NSP,RN-SPM|液态稳定、固态样件、浓缩燃料、纳米制造与魂钢加工不能共用一个新研究替代。
R-AB-014|用途拆分|RN-CFR,RN-BCA,RN-ICA|高密度燃料、磁约束和低温工况不同；普通冷却不得先要求冰核心，需分基础/高级工序。
R-AB-015|用途拆分|RN-MRE,RN-LRE,RN-CFR,RN-SPM|旧大型反应堆、浓缩棒、反应堆核心和八大件共用门槛，按功能拆开。
R-AB-016|相近迁移|RN-NBS,RN-NSP,RN-SPM|纳米制造与精密加工分开；研究环控制器需检查首份实验是否反向依赖它。
R-AB-017|工艺归并|RN-MCE,RN-SSC|电压许可取消；粒子工艺与电路工艺分别处理，不能只按旧tier迁移。
R-AB-018|工艺归并|RN-MCE,RN-CPT|电路蚀刻与封装按实际形态与平台判断，首台封装设备必须使用前级可得电路。
R-AB-019|用途拆分|RN-QOM,RN-VCA|量子观测归QOM；同ID下天命虚数核心配方属于材料/空间功能，不能按观测名称直接放行。
R-AB-020|用途拆分|RN-WCP,RN-UED|坐标解析与取回实物必须区分；旧固定世界泡样本配方还需真实目标账本接线。
R-AB-023|相近迁移|RN-RAT,RN-ERA|基础稳定与强化稳定分层；历史注视不能被缓冲直接抹除。
R-AB-021|工艺归并|RN-SPM,RN-MCE|取消第四档电压许可，部件与电路分别归工艺，仍受具体材料与设备电压限制。
R-AB-022|工艺归并|RN-MCE,RN-CPT|电路和第二平台电子部件需分开核对；不能以CPT反锁制造S02的首批电路。
R-AB-024|资格拆分|RN-ALE,RN-QLE,RN-ILE|旧海渊→虚数的阶段顺序已改变，不对应单一新课题；现有虚数观测机入口按IOP实验前级条件重接。
R-IM-001|用途拆分|RN-CPT,RN-CQS,RN-IOP,RN-IAA|实际包揽电路、机壳、部件、虚数观测和传送材料，不可整ID替换；旧“虚数”系列名不代表新虚数研究阶段。
R-IM-002|用途拆分|RN-CPT,RN-CQS,RN-LTA|电路/部件与资料/交流设施分别处理；组织交流不等于电路研究。
R-IM-003|工艺归并|RN-CQS|高阶电路工况可复用；是否涉及独立高维组件须按产物再分流。
R-IM-004|用途拆分|RN-CQS,RN-IAA|电路升级归工况，空间锚定归IAA，不能用锚定认证统管全部部件。
R-IM-005|用途拆分|RN-SPM,RN-CPT,RN-QOM|部件工艺与实际引用的量子观测站分开，观测站不能再由部件许可代替研究。
R-IM-006|用途拆分|RN-LTA,RN-LTB|独立解析与合作资料是可替代知识来源，不强制合作；议会控制器另属外交事实。
R-IM-007|工艺归并|RN-LTA,RN-CQS|电压项退出；实际前文明解码器应按资料工艺处理，不按其旧电压名称迁移。
R-IM-008|用途拆分|RN-SPM,RN-GPR,RN-SMR,RN-SWS,RN-CED|部件、相态净化、介质、世界泡稳态与供能缓冲分别核对。
R-IM-009|用途拆分|RN-SSQ,RN-WMS,RN-CED|魂钢质量/巨构材料与实际挂载的供能站分开，不能一项授权全部。
R-IM-010|事件事实||新外交系统的接触、通信、授权及贸易事实；同ID挂载的魂钢锻造控制器应另归魂钢工艺。
R-IM-011|用途拆分|RN-CQS,RN-VCA|电压许可退出；实际虚数熔炼核心用途需按空间/材料工艺核实。
R-IM-012|用途拆分|RN-SPM,RN-IAA,RN-WMS|精密件、相位转移镜、环形磁铁和物质编织按工艺分开；首份锚定样件不能要求IAA完成。
R-IM-013|相近迁移|RN-BCC,RN-WBC,RN-SWS|真实封存与模拟稳定不能混成一个状态；按世界泡身份区分。
R-IM-014|相近迁移|RN-WMS,RN-WPF|可复用材料编织工序，挂到巨构材料/预制件；不沿用旧阶段出口的自动重定向。
R-IM-015|工艺归并|RN-CQS,RN-IAA|取消独立电压项，按高阶工况和空间部件用途约束。
R-IM-016|工艺归并|RN-SPM,RN-IAA,RN-WPF|普通精密件、空间件、巨构件分流；数值电压不自动等于新研究阶段。
R-IM-017|事件事实|RN-RCA|瓦尔特剧情保留事件事实；构造能力统一归RCA，不再保留馈赠研究或免费解锁。
R-IM-018|相近迁移|RN-RCA|并入理核心重构，仍要求每种电路白名单解锁；不由旧研究完成值自动授予。
R-IM-019|用途拆分|RN-IOP,RN-ERA|虚数实验与稳定压力是两个用途；不能沿用“注视稳定为零”即永久清空历史值。
R-IM-020|资格事实||转入文明档案和叙事记录，不用物品提交直接证明全档案完成。
R-IM-021|资格拆分|RN-QLE,RN-ILE|新顺序先量子后虚数，禁止旧阶段出口顺序照搬；实际计算机控制器按电路工况处理。
R-IM-022|相近迁移|RN-VRC|无人跨界中继与外交通信分流；没有相同的通用“跨维通讯”研究。
R-QT-001|用途拆分|RN-QOM,RN-QLE,RN-CQS|量子发现、研究所工程、电路/部件是独立用途，旧根节点不能统一映射。
R-QT-002|工艺归并|RN-CQS|取消逐电压许可，量子电路继续受设备与材料、具体前级电路限制。
R-QT-003|工艺归并|RN-CQS|电路归高阶工况；关联组织事件不能因此自动判定合作。
R-QT-004|用途拆分|RN-CQS,RN-ERM|工业电路计算与研究加速区分，不能把产点等同速度。
R-QT-005|相近迁移|RN-CQS,RN-SEM|基础高阶工况与奇观超导工况不同，首台量子设备不得依赖后期奇观完成。
R-QT-006|相近迁移|RN-CJK|千界一乘工程承接；新设计有信标和静止列车，不能只改门槛就声称两座结构完成。
R-QT-007|工艺归并|RN-CQS,RN-SPM|电压取消；电路、精密部件与关联事件分别接线。
R-QT-008|用途拆分|RN-CQS,RN-CED|电路归工况；同ID的无线能源中枢归能源管理，不能只改一张总表。
R-QT-009|用途拆分|RN-WTR,RN-DKE,RN-CEE|实际涉及世界泡熔毁、神之键陈列、贸易港，分别归回收/装配/外交事实；工程认证不等于终审资格。
R-QT-010|用途拆分|RN-CQS,RN-LRE,RN-SPM|电路、融合供能及精密组装分别处理；不保留逐电压研究。
R-QT-011|用途拆分|RN-CQS,RN-ERA|电路/部件与压力缓冲不同，历史G不降低。
R-QT-012|资格拆分|RN-WMS,RN-WPF,RN-CEE|旧阶段出口退出；奇观施工模拟应读材料/构件/验收方法，不能代表已经建成奇观。
R-FN-001|用途拆分|RN-WMS,RN-CQS|终局总入口拆为材料和电路工况，不能由此授予终局资格。
R-FN-002|相近迁移|RN-HBD,RN-HCC,RN-HVI|图纸、构件、系统整合三步；实际建舰仍需工程记录，不把研究完成当舰已建成。
R-FN-003|用途拆分|RN-HVI,RN-CQS|仿制舰整合与仍在舰载配方类型生产的终局电路分开；旧舰载模块不自动获得新用途。
R-FN-004|用途拆分|RN-CED,RN-ELC,RN-URE,RN-CQS|能源调度、负载、反应堆、电路、神之键舰载项不能全部转成同一新ID。
R-FN-005|相近迁移|RN-WMS,RN-WPF,RN-SFF|材料、预制件与奇观熔铸分层，起步巨构材料不依赖奇观自身。
R-FN-006|用途拆分|RN-HER,RN-WTR,RN-URE,RN-CQS|旧湮灭语义不等于新世界泡终止；核对实际耗料与输出后分配，防止固定配方绕过账本。
R-FN-007|相近迁移|RN-CEE,RN-CAV|工程验收方法与跨成果验证不同；研究完成不是实际证明。
R-FN-008|用途拆分|RN-WPF,RN-CQS,RN-TAA|旧总控门槛挂了多座不同奇观及电路；每座按专属RN重接，不能全部绑定TAA。
R-FN-009|资格事实|RN-TAA|可复用校验流程，最终资格须汇总真实工程、满卷轴和审判状态；TAA只开放圣座工程。
R-FN-010|工艺归并|RN-CQS,RN-WMS|独立电压项取消，保留高阶工况和材料约束。
R-FN-011|工艺归并|RN-CQS|终局电路归工况和实际材料链，不能通过八枚旧电路提交直接解锁全部系列。
R-FN-012|资格事实|RN-CAV,RN-TAA|成果交叉验证与圣座资格收集分开，不把研究直接标记毕业。
R-GR-001|资格事实||由十五奇观各自实际运行记录汇总，不改成任一研究完成即通过。
R-GR-002|资格事实||由新研究与档案真实完成情况汇总，不以提交数据包替代。
R-GR-003|资格事实||由叙事卷轴规定事件事实汇总，彩蛋和终审排除条件按新设计处理。
R-GR-004|资格事实||按三组织新外交/通信事实核验；不能沿用旧五阵营全收集强制合作。
R-GR-005|资格事实||迁入三级审判状态服务；终焉之茧、琪亚娜、凌虚晴顺序与好坏结局分开记录。
'''

def without_comments(text):
    """保留字符串与行号，仅去除Java注释，避免把历史备注计为活动引用。"""
    tokens = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*'
    return re.sub(tokens, lambda m: '\n' * m[0].count('\n') if m[0].startswith(('/',)) else m[0], text)

def main():
    timestamp = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    old_path = ROOT / 'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchNodes.java'
    catalog_path = ROOT / 'src/main/resources/data/hk3gtl/research/research_catalog.json'
    source = old_path.read_text(encoding='utf-8')
    lang = json.loads((ROOT / 'src/main/resources/assets/hk3gtl/lang/zh_cn.json').read_text(encoding='utf-8'))
    topics = {t['id']: t for t in json.loads(catalog_path.read_text(encoding='utf-8'))['topics']}
    decisions = {}
    for line in DECISIONS.strip().splitlines():
        key, kind, targets, reason = line.split('|', 3)
        assert key not in decisions
        ids = targets.split(',') if targets else []
        assert all(i in topics for i in ids), line
        decisions[key] = (kind, ids, reason)
    references = collections.defaultdict(list)
    for path in (ROOT / 'src/main/java').rglob('*.java'):
        if path == old_path:
            continue
        for number, line in enumerate(without_comments(path.read_text(encoding='utf-8')).splitlines(), 1):
            for key in set(re.findall(r'"(R-[A-Z]+-\d+)"', line)):
                references[key].append({'path': path.relative_to(ROOT).as_posix(), 'line': number, 'code': line.strip()})
    pattern = r'reg\("(R-[A-Z]+-\d+)",\s*Hk3ResearchType\.(\w+),\s*([\d.]+),\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"'
    rows = []
    for match in re.finditer(pattern, source):
        key = match[1]
        kind, targets, reason = decisions[key]
        rows.append({'old_id': key, 'old_title': lang[match[4]], 'old_type': match[2],
                     'old_tier': float(match[3]), 'old_effect': lang[match[5]], 'old_unlock': lang[match[6]],
                     'old_source_line': source.count('\n', 0, match.start()) + 1,
                     'kind': kind, 'targets': [topics[i] for i in targets], 'reason': reason,
                     'references': references.get(key, []), 'runtime_migrated': False})
    assert {r['old_id'] for r in rows} == set(decisions)
    counts = dict(collections.Counter(r['kind'] for r in rows))
    extra = {key: refs for key, refs in references.items() if key not in decisions}
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {'time': timestamp, 'status': '逐项语义对照，尚未替换运行时绑定',
               'policy': '新RN体系替代旧身份；按工艺解锁，不新增逐电压课题；本表不兑换旧完成状态。',
               'scope': '77个已注册旧节点、100个新课题和生产Java字符串引用；动态拼接、资源和外部KJS需在迁移验收补查。',
               'counts': counts, 'old_count': len(rows), 'new_count': len(topics), 'rows': rows,
               'unregistered_old_literals': extra,
               'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (old_path, catalog_path)}}
    (OUT / 'comparison.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    escape = html.escape
    entries = []
    for row in rows:
        targets = ''.join('<li><strong>' + escape(t['id'] + ' ' + t['title']) + '</strong>：' + escape(t['result']) + '</li>' for t in row['targets'])
        refs = ''.join('<li><code>' + escape(f"{r['path']}:{r['line']}") + '</code><pre style="white-space:pre-wrap;overflow-wrap:anywhere">' + escape(r['code']) + '</pre></li>' for r in row['references'])
        entries.append('<details><summary>' + escape(row['old_id'] + ' ' + row['old_title'] + ' · ' + row['kind']) + '</summary><p>旧解锁：' + escape(row['old_unlock']) + '</p><p><strong>迁移判断：</strong>' + escape(row['reason']) + '</p>' + ('<ul>' + targets + '</ul>' if targets else '') + ('<details><summary>生产源码引用（' + str(len(row['references'])) + '处，含旧重定向定义）</summary><ul>' + refs + '</ul></details>' if refs else '<p>本次未找到注册表外的直接字符串引用；不据此断定无动态调用。</p>') + '</details>')
    section = '<section id="research-id-comparison"><h2>研究主链优先：77项旧研究逐项对照</h2><p>' + escape(timestamp) + '</p><p><strong>负责人已确认：内测5重构研究体系，不长期保留旧R身份；旧电压/电路/八大件按新工艺课题解锁，电压进度由材料、设备与具体前级电路约束。</strong></p><p>以下是迁移前对照，不是已实施的替换表。多个目标表示不同用途的去向，绝不表示任意完成一个便开放原节点全部内容。旧自动事件不直接完成新研究；没有对应课题的事件与终局资格转为实际事实判定。</p><p>' + escape('；'.join(f'{k}：{v}项' for k,v in counts.items())) + '</p><p>范围：77个当前注册旧节点、100个新课题；逐行附去除注释后的生产Java直接引用。另有' + str(len(extra)) + '个未注册旧ID字面量，仅发现于旧重定向表。尚未完成每条配方的全材料可达性检查，不能把对照当作消除全部自锁。</p><p><a href="../../../logs/research-migration-20260928/comparison.json">完整机器可读对照与源码哈希</a></p>' + ''.join(entries) + '<p>【变更记录 #1 · 研究身份迁移对照】' + escape(timestamp) + '：保留原计划和历史记录；追加负责人决定、77项对照及源码引用。未修改游戏代码、存档、研究完成状态或实例。</p></section>'
    page = PLAN.read_text(encoding='utf-8')
    if 'id="research-id-comparison"' in page:
        raise RuntimeError('已有对照章节，拒绝覆盖历史；请追加新记录')
    (OUT / 'plan-before.html').write_bytes(PLAN.read_bytes())
    assert page.count('</main>') == 1
    PLAN.write_text(page.replace('</main>', section + '\n</main>'), encoding='utf-8')
    print(json.dumps({'old':len(rows),'new':len(topics),'counts':counts,'unregistered_old_literals':list(extra),'production_reference_occurrences':sum(len(r['references']) for r in rows),'plan':str(PLAN)},ensure_ascii=False))

if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
