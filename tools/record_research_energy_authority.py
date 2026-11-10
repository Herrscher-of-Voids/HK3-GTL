"""保存W13/ERM费用与授权裁定，追加现有研究计划。

变更#1：2026-09-28。实时日期时间写入输出。新增六项用户答复、费用算例、
授权流程及必要工程检查；删除无，保留所有历史。仅写HTML/JSON设计资料。
读取本地电压常量和已确认容量；静态核验不会运行游戏、修改源码或替代能源平衡验收。
写入前检查唯一文件名，写入后回读并比较生产文件哈希；不要重复运行制造重复记录。
"""
from pathlib import Path
from html import escape
from fractions import Fraction
import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'logs/research-migration-20260928'
PLAN = ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
DECISIONS = [
    {'question':'W13采用哪组单项加速成本？研究所自身EU另计；只为成功推进的加速课题收费，最多16项。推荐每项1A（WSV）/t＋64 HW/t，满载为16A（WSV）/t＋1,024 HW/t。',
     'answer':'采用1A WSV＋256 HW/t'},
    {'question':'ERM的＋50%加速，是否采用“每个实际加速课题额外1A（QSV）/t、不额外耗HW”的成本？它与课题自身耗电分列，玩家可以关闭模块加速。',
     'answer':'采用每项额外1A QSV/t（推荐）'},
    {'question':'W13服务多座研究所时，HW从谁的账户扣除？建议统一由W13绑定人支付；不会因队友开始研究，就自动扣课题付款人或研究所绑定人的个人HW。',
     'answer':'由W13绑定人的HW账户统一支付（推荐）'},
    {'question':'W13与研究所建立服务连接，谁来确认？建议由W13绑定人同意供能、研究所绑定人确认接入；双方任一方可撤销连接，只停止加速，不取消已付款研究。',
     'answer':'双方绑定人确认，任一方可撤销（推荐）'},
    {'question':'W13绑定人离开原团队后，原有HW供能授权怎样处理？设备所属研究团队仍不自动迁移。',
     'answer':'暂停加速，原付款人重新授权后才能继续供能（推荐）'},
    {'question':'绑定研究所的待加速课题超过16项时，W13怎样分配服务？未选中的课题仍以本地速度研究。',
     'answer':'可调研究所优先级，同级先开始先服务（推荐）'},
]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before_source = production()
    values_path = ROOT/'src/main/java/com/sirin/hk3gtl/common/constants/Hk3ValuesImpl.java'
    values_text = values_path.read_text(encoding='utf-8')
    match = re.search(r'VA_LONG\s*=\s*\{(.*?)\};', values_text, re.S)
    assert match
    tokens = re.sub(r'//[^\n]*','',match.group(1)).split(',')
    voltages = [(2**63-1 if token.strip() == 'Long.MAX_VALUE' else int(token.strip().removesuffix('L')))
                for token in tokens if token.strip()]
    assert len(voltages) == 31
    qsv, wsv = voltages[19], voltages[28]
    assert qsv == 2061584302080 and wsv == 540431955284459520
    previous = OUT/'research-service-lifecycle-confirmed-20260928-162439-894053.json'
    prev = json.loads(previous.read_text(encoding='utf-8'))
    assert prev['confirmed_parameters']['w13_active_topic_capacity'] == 16
    costs = [{'active_topics':n,'w13_eu_per_tick':n*wsv,'w13_hw_per_tick':n*256,
              'w13_display':f'{n}A（WSV）/t ＋ {n*256:,} HW/t',
              'erm_extra_eu_per_tick_if_enabled_for_same_topics':n*qsv,
              'erm_display':f'额外 {n}A（QSV）/t；0 HW/t'} for n in [0,1,4,16]]
    assert costs[-1]['w13_eu_per_tick'] < 2**63
    assert costs[-1]['w13_hw_per_tick'] == 4096
    # 只比较配方基础产率，不把并行/超频/供料折算成已验证机器数量。
    liquid_rate = Fraction(16000,400)
    nominal_load_ratio = Fraction(4096,1)/liquid_rate
    assert liquid_rate == 40 and nominal_load_ratio == Fraction(512,5)
    contracts = [
        '已确认W13每个实际加速且推进的正式研究课题，每tick消耗1A（WSV）的EU以及256 HW；16项满载为16A（WSV）/t＋4096 HW/t。研究所自身用电和ERM费用另计。',
        '已确认ERM每个实际加速课题额外消耗1A（QSV）/t，不额外耗HW。玩家可关闭模块加速；研究所原课题用电不被这个附加费用替代。',
        '本轮电压表达沿用项目研究界面的VA_LONG档位口径：QSV为索引19，WSV为索引28。显示优先A（电压）/t，悬停再给完整EU/t，不把两种电压的安培数直接相加。',
        'W13的HW统一扣母机绑定人的个人账户，不自动扣课题付款人或受服务研究所绑定人的HW。研究共享不是私人能源共享；EU与HW继续独立记账。',
        '建立连接须W13绑定人同意供能、研究所绑定人确认接入；任一方都可撤销连接。撤销只停止加速，不取消已付款研究、不抹去进度，也不收回已经完成的知识。',
        'W13绑定人离开原团队，暂停加速并保留连接记录，必须由原付款人重新明确授权后才能为原设备团队继续供能。这里原付款人指W13的HW付款人，不是某课题的研究费用付款人。',
        '设备所属研究团队不因付款人离队自动迁移；重新同意供能不代表迁移机器、工程资格或研究成果，也不代表对新队伍所有设备开放服务。',
        '服务分配按可调整的研究所优先级，同优先级按课题开始顺序；每台最多16个有效服务目标。未选中的课题正常按本地速度研究，多个W13不对同一课题叠加倍率。',
        '沿用前次已定规则：按实际服务计费，空闲不扣加速运行费；W13停机、卸载或能源不足失去对应加速，研究所自身条件满足时仍能继续研究。',
        '研究加速仍为ERM＋50%、W13＋150%，相加后的正向上限3倍，再计算注视度减速。不额外增加研究槽位、实验成果或研究点产量。',
    ]
    findings = [
        '当前液态燃料注入配方基础工况400tick消耗16000mB燃料及配套物品、注入16000HW，账面基础产率40HW/t。W13满载4096HW/t相当于102.4份该基础配方产率，不代表必须建设102.4台机器，实际还有并行、超频与上游供料。',
        '后期I38实际产率尚未确定，本轮可以确认W13消耗参数，但不能宣称完整能源生产与消费已经平衡。该参数也不授权增加纯EU兑换HW的路线。',
        '从VA_LONG读取并计算，W13单台16项的EU成本为8646911284551352320EU/t，单独低于Long.MAX_VALUE。此静态结果不证明能源输入、网络适配或全部研究所负载已能运行。',
        '最高课题档位本身为Long.MAX_VALUE；再叠加ERM或多槽研究若用long直接相加会溢出。汇总使用任意精度并核对实际扣款接口；不能用溢出钳制静默少扣能源。',
        '现有Hk3PlayerGridEnergyTrait从GTMThings取BigInteger余额但向GT暴露long接口；现有双能源账户按ownerUUID分离。可复用账户入口，跨设备EU/HW/研究推进仍需实现并验证一致结算。',
        '现有研究所authorized仅检查绑定人，不包含本次服务连接的双边确认、优先级和离队撤权；这些是后续功能，当前未实现。',
    ]
    implementation = [
        '连接记录需包含双方机器身份、绑定人身份、固定研究团队、同意状态及授权版本。收到客户端请求后服务端重核验身份；不能以任意物品NBT或旧缓存代替授权。',
        '已知离队必须使当前授权失效并停止新计费，之后通过明确重新授权恢复；暂时离线不是离队，不应自动删除授权，但正式研究仍受全队离线暂停约束。',
        '同优先级且开始时间完全相同时，以持久化任务ID确定稳定顺序，避免重启后反复争抢。暂停/完成任务不占实际收费服务位，可让其他有效任务补位。',
        '谁能操作哪些优先级控件应遵循母机供能授权；界面显示优先级、被选中目标、有效服务数与当前费用。此为界面实施建议，不授予队长代替私人账户授权的能力。',
        '加速款与当tick实际加速推进需对应。两种能源部分失败、撤权、任务完成竞争、重试和服务器重启不能造成免费加速或重复扣费。尚未证明现有单账户原子方法能覆盖全部步骤。',
        'ERM附加供电不足时如何回落应与可关闭模块和基础研究行为一致；具体降级分支纳入实现评审，不能因加速服务中断直接清空研究。',
    ]
    pending = [
        '本轮六项已确认，覆盖前次记录中W13单项成本、ERM附加成本、HW付款人、连接权限、付款人离队授权及超额服务顺序的未定状态，不再重复提问。',
        '下一步集中处理终审个人/团队归属、卷轴条件与文明等级关系；不重新讨论已确认的奇观拆除复验、可停机验收和工程资格不随成员复制。',
        '实验样件/耗时与各配方材料、HW后期生产参数、具体模块制造成本仍随工业配方核对；本轮费用确认不是批准所有剩余工序或结构。',
    ]
    sources = [values_path,previous,
        ROOT/'src/main/java/com/sirin/hk3gtl/common/constants/Hk3TiersImpl.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/gui/Hk3ResearchTerminalWidget.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/recipe/honkai/Hk3LiquidLineRecipes.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/energy/Hk3HonkaiNetworkInjectorMachine.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/Hk3WorkableMultiblockMachine.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/trait/Hk3PlayerGridEnergyTrait.java']
    e = lambda x:escape(str(x),quote=True)
    anchor = 'research-energy-authority-'+stamp
    parts = [f'<section class="panel" id="{anchor}"><h2>已确认：W13/ERM运行费用与双边授权</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；用户原消息精确时间未知。设计裁定已确认，生产未改。</p>']
    for d in DECISIONS:parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>用户答复：</b>'+e(d['answer'])+'</p>')
    parts.append('<h3>费用对照（不含课题本身耗电）</h3><ul>')
    for r in costs:
        parts.append('<li>'+e(f"有效服务{r['active_topics']}项：W13为{r['w13_display']}；这些课题若同时启用ERM，研究所另承担{r['erm_display']}。")+'</li>')
    parts.append('</ul>')
    for title,values in [('确认范围',contracts),('本地核对及限制',findings),('实施检查，非实现证明',implementation),('覆盖关系与下一步',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<p>本轮不采用助手推荐的64HW/t，明确采用256HW/t。所有源码与生产资源保持不变；没有编译、部署、启动游戏或进行供电实测。</p></section>')
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8');assert before.count('</body>') == 1
    after = before.replace('</body>',section+'\n</body>',1)
    assert after.replace(section+'\n','',1) == before
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_W13及ERM耗能与双边授权确认.html')
    log = OUT/('research-energy-authority-confirmed-'+stamp+'.json')
    validation = OUT/('research-energy-authority-validation-'+stamp+'.json')
    for p in [record,log,validation]:assert not p.exists(),p
    payload = {'time':now.isoformat(),'status':'六项答复已确认，非生产实现','decisions':DECISIONS,
        'confirmed_parameters':{'w13_eu_tier':'WSV','w13_eu_per_active_topic_tick':wsv,
            'w13_hw_per_active_topic_tick':256,'w13_active_topic_cap':16,
            'erm_eu_tier':'QSV','erm_extra_eu_per_active_topic_tick':qsv,'erm_extra_hw_per_tick':0,
            'w13_hw_payer':'mother_machine_bound_player','binding':'both_bound_players_consent_either_can_revoke',
            'payer_leaves_team':'suspend_until_same_payer_reauthorizes_original_team_service',
            'service_order':'lab_priority_then_research_start_time'},
        'cost_examples':costs,'liquid_reference':{'base_credit_hw':16000,'base_ticks':400,'hw_per_tick':40,
            'full_load_to_single_base_recipe_rate':str(nominal_load_ratio),'machine_count_inferred':False},
        'contracts':contracts,'findings':findings,'implementation_checks':implementation,'pending':pending,
        'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sources},'anchor':anchor,'game_changed':False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>W13及ERM耗能与授权确认</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}</style></head><body><h1>W13及ERM耗能与双边授权确认</h1><p>用户要求继续；本轮核对实际EU档位、液态线HW注入、研究功率显示及绑定账户实现，再提出两组六个问题，实际答复如下。没有把推荐值当作默认批准。</p>{section}<h2>实际执行与覆盖关系</h2><p>读取本地源码和前次记录，静态计算0/1/4/16项费用、源产率与long边界，保存结构化答复及本记录，追加现有计划并回读。生产文件哈希前后未变，未实施费用或授权逻辑。旧记录中的相应未知数由本条覆盖，保留原文件。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">当前计划确认段落</a> · <a href="2026-09-28_16-24-39_W13服务容量双能源及独立实验恢复确认.html">容量/双能源/实验恢复裁定</a> · <a href="2026-09-28_16-12-33_研究加速相加三倍及授权绑定确认.html">加速倍率裁定</a></p><footer>变更#1 · {e(now.isoformat())}：新增六项用户决定、数值依据和执行边界；现有计划只追加，删除无。后续终审与卷轴边界继续讨论，尚未开始生产修改。</footer></body></html>'''
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert before_source == production(), '生产文件有变化，核查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':6,'cost_cases':len(costs),
        'w13_full_load_hw_per_tick':4096,'w13_full_load_eu_fits_long':True,
        'all_research_energy_capacity_verified':False,'whole_energy_chain_balanced':False,
        'previous_plan_preserved':True,'production_files_unchanged':len(before_source),
        'compiled':False,'deployed':False,'game_tested':False,'record':str(record),'log':str(log),'anchor':anchor}
    with validation.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':main()
