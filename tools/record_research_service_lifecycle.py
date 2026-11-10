"""记录W13服务规则与独立实验生命周期，仅追加研究设计与讨论。

变更#1：2026-09-28 16:22:04。新增六项用户答复、状态边界与代码核对；
删除无，保留旧方案。读取研究目录、既有裁定及源码作依据，不修改生产文件。
输出带实际记录时间的JSON/HTML和现有计划追加段落；写入后回读并比较生产哈希。
检查为文档/来源检查，不冒充运行中的双能源事务或队列测试。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'logs/research-migration-20260928'
PLAN = ROOT/'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
DECISIONS = [
    {'question':'一台W13同时加速多少个正式研究课题？容量可分配给多座绑定研究所，不增加它们自己的槽位；超过容量的课题仍按本地速度运行，多台W13不能叠加同一课题的倍率。',
     'answer':'16项，相当于一座满槽S05（推荐）'},
    {'question':'W13加速运行采用哪种能源？研究所原有EU供电保持不变；这里确定W13自身的能源类型，具体消耗随后列数值方案，不把EU与HW视为同一账户。',
     'answer':'W13消耗EU与HW，承担双能源成本（推荐）'},
    {'question':'ALE／OPR／ERM这三类独立实验，在停电、研究所失去成型、区块卸载或服务器重启时怎样处理？建议保存进度与已投入样件，条件恢复后续做，不重复扣样件，未成功前不发证据。',
     'answer':'保存实验进度和投入，恢复后续做（推荐）'},
    {'question':'W13加速的运行费用怎样计算？建议按实际获得加速、并成功推进的课题计费；没有有效服务时不扣加速运行费。具体每项EU/HW消耗随后拟定，实验验收等其他工况单独计费。',
     'answer':'按实际服务负载计费，空闲不扣（推荐）'},
    {'question':'主动取消未完成的ALE／OPR／ERM独立实验时，样件怎样处理？建议开始时托管实际投入，成功时才结算消耗；原发起人取消后清除进度，样件原样退入其待领取账本，已耗电不退。',
     'answer':'采用托管，取消退回全部投入（推荐）'},
    {'question':'研究所内的独立实验，在全队离线但区块仍加载、设备成型且有电时，是否继续？正式研究仍按已定规则暂停，这里仅指ALE／OPR／ERM实验。',
     'answer':'继续真实实验，成功记入绑定团队（推荐）'},
]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def production():
    return {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/main').rglob('*') if p.is_file()}


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    before_source = production()
    cat_path = ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
    catalog = {r['id']:r for r in json.loads(cat_path.read_text(encoding='utf-8'))['topics']}
    def ancestors(key, path=()):
        assert key not in path
        out = set()
        for p in catalog[key]['prerequisites']:
            out.add(p);out.update(ancestors(p,path+(key,)))
        return out
    asr_done = ancestors('RN-ASR') | {'RN-ASR'}
    assert len(asr_done) == 65
    assert len(catalog)-len(asr_done) == 35
    prior = OUT/'research-acceleration-confirmed-20260928-161233-722819.json'
    prior_data = json.loads(prior.read_text(encoding='utf-8'))
    assert prior_data['confirmed_parameters']['positive_speed_cap'] == 3
    assert prior_data['confirmed_parameters']['erm_bonus'] == 0.5
    assert prior_data['confirmed_parameters']['w13_bonus'] == 1.5
    contracts = [
        '已确认容量单位为正在加速的正式研究课题，不是研究所数量：每台W13最多16项，可跨多座明确绑定、获授权的研究所分配；不额外增加研究所槽位。',
        '超过W13服务容量的课题保留正常研究和本地ERM效果；不同W13可分担不同课题，但同一课题不叠加多份W13效果。原+50%/+150%、正向最高3倍后算注视减速保持不变。',
        '已确认W13自身EU与HW双能源运行；研究所原本的逐槽EU需求仍在。EU与HW独立记账，不隐含互相兑换，也不以团队研究共享取得队友私人账户权限。',
        '加速运行费按实际得到W13加速且成功推进的课题计算，空闲不扣。暂停、研究所断电、全队离线暂停研究、已完成待提交等不产生有效加速推进的任务，不能计作收费负载。',
        '计费规格：每个有效课题运行tick的EU/HW单价尚未定；按对应单价汇总成功服务的任务。实验验收、工艺优化等其他工况需另列成本，不能借“空闲免费”免除实际工作的耗能。',
        'W13供能不足、停机或卸载只撤掉对应加速；研究所自身条件有效时继续本地研究，进度不清零。既有正式研究的全队离线暂停不变。',
        '已确认ALE/OPR/ERM独立实验开始时托管实际投入；此时物品离开可用库存并随实验保存，不能继续被别处使用。成功时才按实验规格结算消耗并记录证据，非消耗标准件不被改成耗材。',
        '停电、研究所失去成型、区块卸载、服务器重启都暂停独立实验，保留进度和托管投入；恢复运行不能再次扣取样件。未成功不发证据，不补算未运行的墙钟时间。',
        '原发起人主动取消未完成实验：清除该次进度，把全部实际托管投入原样记入其待领取账本，保留物品数据；已耗电不退。背包不足继续保存未领取部分，不丢弃或重复退还。',
        '实验取消与成功结算必须互斥；同一尝试唯一ID对应的托管投入只能消费或转为退款一次。成功回调/领取请求/恢复重试必须去重，不能同时获得证据和取消退款。此为实现约束，未验证现有实现。',
        '已确认全队离线仍可运行这三类独立实验，前提是区块确实加载、设备成型且正常供电；成功记入机器绑定研究团队，保留原始实验来源。不能用在线玩家对象是否存在代替团队归属。',
        '正式研究与独立实验共享研究所槽位，但使用不同离线政策及结算类型。实验只提供证据，不免除后续正式研究的研究点或材料付款，也不修改正式研究的取消退款规则。',
    ]
    transitions = [
        {'event':'启动成功','progress':'从零开始一次新尝试','inputs':'实际物品移入托管','evidence':'不授予','scope':'独立实验'},
        {'event':'停电/失去成型/卸载/重启','progress':'保留并暂停','inputs':'保留托管，不重复扣取','evidence':'不授予','scope':'独立实验'},
        {'event':'运行条件恢复','progress':'从已保存进度继续','inputs':'沿用原托管','evidence':'未成功仍不授予','scope':'独立实验'},
        {'event':'全队离线但设备仍加载正常供电','progress':'独立实验继续；正式研究暂停','inputs':'按各自任务类型处理','evidence':'实验真实成功后记原绑定团队','scope':'明确区分两种任务'},
        {'event':'原发起人取消未完成实验','progress':'清除本次进度','inputs':'原样转入发起人待领取账本','evidence':'不授予','scope':'独立实验，电不退'},
        {'event':'实验成功提交','progress':'本次尝试完成','inputs':'按实验规格结算消费/非耗材返还','evidence':'只记录一次实验证据','scope':'与取消互斥，不直接完成课题'},
    ]
    findings = [
        '当前100项目录中RN-ASR的祖先加自身共65项，理论还可剩35项；这是依赖图计数，不代表35项能同时开题，也不代表都值得等待W13。',
        '当前研究所researchTick在绑定人离线时直接返回，尚不足以实现“团队有人在线研究继续”以及本轮“全队离线实验仍可运行”；必须分别接入研究团队与实验绑定团队规则。',
        '现有材料支付收据保留实际ItemStack数据，可评估复用其精确扣料/凭据能力；尚未实现本轮独立实验托管、待领取退款与取消/成功互斥链路。',
        'HonkaiWirelessNetwork有按UUID的BigInteger全额扣款，IDualEnergyConsumer已有绑定人账户入口；单账户原子扣款不等于跨EU、HW和另一台研究所推进的完整事务已成立。',
        '现有VA_LONG最高档为Long.MAX_VALUE，多任务费用汇总不可直接long求和；汇总需防溢出，且任意精度记账不代表GT能源容器能实际承载相同总吞吐。',
        'Hk3DualEnergyCosts中的奇观默认8192及旧1崩坏能=1000EU注释是旧实现背景，不能直接定为新W13单项成本或新增兑换许可。本轮没有采用这些数值。',
    ]
    implementation_candidates = [
        '服务分配候选：按持久化的绑定优先级和任务顺序确定最多16个有效目标；限制只针对W13服务，不对其他课题停机。界面应显示是否加速和未获服务原因。分配策略尚未批准。',
        '结算候选：使用服务回执关联母机ID、研究尝试ID、服务tick、两项成本及实际加速量，确保成功扣费与加速推进一一对应。需审查跨设备两阶段确认/补偿与重启恢复，不能先免费推进后尝试扣款。',
        '低内存候选：按绑定索引查询任务，不每tick扫描基地或全球研究所；卸载撤销有效服务而保留绑定记录，不主动强制加载所有目标。缓存有界，状态变化及时失效。',
        '实验尝试保存原团队、发起人、设施、实验类型、样件快照、进度和结算状态；精确NBT输入保留，不按材料标签重新生成退款物品。',
    ]
    pending = [
        'W13每有效课题的EU/HW具体成本及ERM附加耗能仍待数值方案；16项服务容量、双能源、实际负载计费已确定，不再作为待定问题。',
        'W13绑定/解绑权限、超额任务服务顺序、能源付款账户授权细则需明确；不能默认可扣课题付款人或全队全部HW余额。',
        '独立实验的具体样件、运行时长与功率尚待逐配方核对；取消和暂停策略已确定，不再重问。实验的主动管理权限及团队解散/设备永久移除后的恢复入口须与团队服务统一。',
        '终审个人/团队结算与卷轴最终条件仍待收口；本轮不讨论结构外观，不修改研究所命名。',
    ]
    source_paths = [cat_path,prior,
        ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchStartService.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchMaterialPayment.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/constants/Hk3ValuesImpl.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/capability/HonkaiWirelessNetwork.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/capability/Hk3DualEnergyCosts.java',
        ROOT/'src/main/java/com/sirin/hk3gtl/common/capability/IDualEnergyConsumer.java']
    e = lambda x:escape(str(x),quote=True)
    anchor = 'research-service-lifecycle-'+stamp
    parts = [f'<section class="panel" id="{anchor}"><h2>已确认：W13服务16项、双能源负载计费与独立实验恢复</h2><p>记录时间：{e(now.isoformat())}，Asia/Hong_Kong；原消息精确时间未知。六项用户答复已确认，尚未实现。</p>']
    for d in DECISIONS:parts.append('<p><b>问题：</b>'+e(d['question'])+'<br><b>答复：</b>'+e(d['answer'])+'</p>')
    for title,values in [('已确认规则与必要约束',contracts),('源码核对',findings),('实现候选，非已批准细节',implementation_candidates),('剩余事项',pending)]:
        parts.append('<h3>'+title+'</h3><ul>');parts.extend('<li>'+e(x)+'</li>' for x in values);parts.append('</ul>')
    parts.append('<h3>独立实验状态对照</h3>')
    for r in transitions:
        parts.append('<p><b>'+e(r['event'])+'：</b>'+e('；'.join([r['progress'],r['inputs'],r['evidence'],r['scope']]))+'。</p>')
    parts.append('<p>本段明确此前服务容量、供能类型、计费方式、实验中断、取消与全队离线行为的待定状态；其他数值、授权及结构审批不变。生产文件哈希比对未变，未编译、部署或游戏测试。</p></section>')
    section = '\n'.join(parts)
    before = PLAN.read_text(encoding='utf-8');assert before.count('</body>') == 1
    after = before.replace('</body>',section+'\n</body>',1)
    assert after.replace(section+'\n','',1) == before
    record = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_W13服务容量双能源及独立实验恢复确认.html')
    log = OUT/('research-service-lifecycle-confirmed-'+stamp+'.json')
    validation = OUT/('research-service-lifecycle-validation-'+stamp+'.json')
    for p in [record,log,validation]:assert not p.exists(),p
    payload = {'time':now.isoformat(),'status':'六项用户决定已确认，尚未实现','decisions':DECISIONS,
        'confirmed_parameters':{'w13_active_topic_capacity':16,'w13_energy_types':['EU','HW'],
            'w13_bill_successful_service_only':True,'w13_acceleration_idle_cost':0,
            'experiment_interrupt':'pause_preserve_progress_and_escrow','experiment_cancel':'return_all_escrow_to_initiator_claim_ledger',
            'experiment_all_team_offline':'continue_if_loaded_formed_powered','formal_research_all_team_offline':'pause'},
        'unapproved_rates':{'w13_eu_per_active_topic_tick':None,'w13_hw_per_active_topic_tick':None,'erm_additional_energy':None},
        'contracts':contracts,'transitions':transitions,'findings':findings,'implementation_candidates':implementation_candidates,
        'pending':pending,'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},'anchor':anchor,'game_changed':False}
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>W13服务与独立实验恢复确认</title><style>body{{max-width:1100px;margin:30px auto;padding:20px;background:#14202e;color:#e4ecf5;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ddfff}}</style></head><body><h1>W13服务容量、双能源及独立实验恢复确认</h1><p>用户要求继续研究系统设计。本轮先核对既有加速裁定、三类实验承载与能源/研究源码，再分两组提出六个问题；用户逐项选择本页记录的方案。没有把“继续”或推荐选项当作批准。</p>{section}<h2>覆盖关系与执行结果</h2><p>覆盖上一轮加速记录和工艺合并记录中相应的六项未定状态。W13系数仍为ERM＋50%、W13＋150%、正向合计最高3倍；新增16项容量不改变研究所1/2/4/8/16槽位。正式研究退款和全队离线暂停继续有效，实验使用本轮独立规则。</p><p>已保存本记录和结构化裁定、追加现有计划并回读。核对目录65项前置及35项理论余量、源文件指纹和生产文件集合；没有执行游戏逻辑、没有宣称跨设备计费原子性已验证。</p><p>下一步提交W13/ERM供能数值和必要授权方案，再继续终审与卷轴边界；外观讨论保持暂停。</p><p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">现有计划本轮段落</a> · <a href="2026-09-28_16-12-33_研究加速相加三倍及授权绑定确认.html">原加速裁定</a> · <a href="2026-09-28_16-07-59_八项工艺合并及研究所实验任务确认.html">实验承载裁定</a></p><footer>变更#1 · {e(now.isoformat())}：新增六项用户决定、适用范围及必要检查；现有计划只追加，删除无。仅设计落盘，非生产实现。</footer></body></html>'''
    with log.open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    PLAN.write_text(after,encoding='utf-8')
    with record.open('x',encoding='utf-8') as f:f.write(body)
    assert PLAN.read_text(encoding='utf-8') == after
    assert record.read_text(encoding='utf-8') == body
    assert json.loads(log.read_text(encoding='utf-8'))['decisions'] == DECISIONS
    assert before_source == production(), '生产文件发生变化，须核查并发写入'
    result = {'time':now.isoformat(),'confirmed_answers':6,'experimental_transition_rows':len(transitions),
        'asr_required_completed_topics':len(asr_done),'possible_remaining_topics':len(catalog)-len(asr_done),
        'previous_plan_preserved':True,'production_files_unchanged':len(before_source),
        'compiled':False,'deployed':False,'game_tested':False,'record':str(record),'log':str(log),'anchor':anchor}
    with validation.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
