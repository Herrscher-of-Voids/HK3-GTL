# -*- coding: utf-8 -*-
"""汇总本轮已逐份阅读的通用服务审计；不修改模组或实例。

【变更记录 #1】2026-10-25（只读审计工具；初始备注误填01:05:00，不将其作为写入时间证据）
删除：无。新增：通用系统能力、源码差距、逐文件身份与复核范围。
修改：与工业、推进和客户端审计交叉对账，不以文件数量推算功能完成率。
用途：保存人工语义审查结果，供HTML与交互审计页复用。

【变更记录 #2】2026-10-25（审计口径复核；初始01:07:00备注不能作为写入时间证据，实际生成以输出created_at为准）
删除：从待定发现中撤去旧团队共享G要求。新增：修订109明确批准口径依据。
修改：按9月30日最新明确纠正评价个人原始G、在线团队最高有效值及缓冲；保留尚未接入的设施缺口。
用途：避免旧专项正文覆盖后续已批准决定；仅修正本轮未交付审计草稿。

【变更记录 #3】2026-10-25（证据补充；输出created_at记录实际秒数）
删除：无。新增：GTL/AE融合与创造箱罐自动提取未覆盖的独立审查域。
修改：通用服务补充源码定位，产品文件保持原字节。
用途：覆盖既有34域中的兼容限制，不把手机AE打开成功扩大为全自动化限制已实现。
"""
from pathlib import Path
import datetime as dt
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'src/main/java/com/sirin/hk3gtl'
OUT = ROOT / 'logs/beta5-audit-20261025'


def evidence(rel, needle, claim):
    p = BASE / rel
    lines = p.read_text(encoding='utf-8-sig').splitlines()
    line = next(i for i, text in enumerate(lines, 1) if needle in text)
    return {'path':p.relative_to(ROOT).as_posix(), 'line':line, 'claim':claim}


def main():
    groups = {
        'common/network':'服务端发送者与动作路由、客户端接收边界、协议及载荷限制',
        'common/phone':'服务端电量/应用授权、通知笔记、社交、AE委托与个人数据持久化',
        'common/overview':'GT真实生命周期索引、只读权限、预算与保守状态',
        'common/gaze':'个人原始值、缓冲、来源历史、锚与同步；与团队共享设计对照',
        'common/bootstrap':'欢迎与版本确认、历史详情、有限范围启动健康投影',
        'common/easter':'事实事件入口、条件绑定、作者归属、只读奖励与存储边界',
        'common/util':'数值展示、持久化损坏拒重置、加权同步缓存',
        'common/gui':'研究终端状态同步、服务器动作、GUI缩放和输入映射',
        'common/advancement':'真实文明/研究事实桥接，而非单独伪造阶段',
        'common/compat/wmp':'目录映射电路阶级、BigInteger电压，非法电路返回未识别',
        'common/multiblock/export':'逐份读取扫描、符号及代码草稿生成；导出不是正式机器接入',
        'mixin/overview':'机器真实放置、拆除、卸载、成型生命周期观察',
    }
    rows = []
    for folder, summary in groups.items():
        for p in sorted((BASE/folder).glob('*.java')):
            rows.append((p, summary))
    event_names = ['Hk3ModWelcomeHandler','Hk3CreativeItemGuard','Hk3PlayerDataCloneHandler','Hk3ForgeSetup',
                   'Hk3VoidGiftData','Hk3VoidGiftHandler','Hk3XiguamaoGiftHandler','Hk3EasterEggChecker',
                   'Hk3EasterEggStats','Hk3EasterEggClock']
    for name in event_names:
        rows.append((BASE/'common/event'/f'{name}.java','逐份核对真实事件订阅、数据写入及历史兼容边界；旧彩蛋tryEgg为空，不按旧检测器计算执行覆盖'))
    for p in sorted((BASE/'mixin').rglob('*Egg*.java')):
        rows.append((p,'逐份核对目标方法、实际事务前后观察、服务端归属、清理及可选依赖；未以源码存在代替运行注入成功'))
    for name in ['AvaritiaAbilityHandlerMixin','AvaritiaCCShaderInstanceMixin','AvaritiaCCUniformInvoker',
                 'AvaritiaShaderMixin','CosmicBakeModelMixin','GlDebugMixin','Hk3MixinConfigPlugin',
                 'GTRecipeWidgetMixin','ItemRecipeCapabilityMixin','FluidRecipeCapabilityMixin',
                 'JeiCopyItemHandlerMixin','FluidIngredientMixin','PrimaryLevelDataAccessor','LevelSettingsAccessor',
                 'EnhancedRecipeConditionsMixin','EnhancedRecipeTickMixin','SkyTearsAndGregHeartMixin']:
        rows.append((BASE/'mixin'/f'{name}.java','并发集合/着色器适配或Mixin依赖隔离；旧取消渲染类未列入当前Mixin配置，不能当成活动行为'))
    for name in ['Hk3SocialAiClient','Hk3SocialPersonas']:
        rows.append((BASE/'client/phone'/f'{name}.java','离线与显式自费AI边界、客户端密钥和人格约束；没有调用外部模型'))
    rows.append((BASE/'mixin/gtceu/Hk3GtceuKeyBindMixin.java','断线时取消GT按键回调；未替代游戏运行验收'))
    for name in ['EasterEggItems','Hk3PhoneItem','NarrativeCodexItem']:
        rows.append((BASE/'common/item'/f'{name}.java','逐份读取物品入口：手机电池能力与服务端打开；档案委托个人投影；EasterEggItems本身仍为空槽，不把空槽当奖励物品已实现'))
    unique = {p.relative_to(ROOT).as_posix():(p,s) for p,s in rows}
    reviewed = [{'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                 'lines':len(p.read_text(encoding='utf-8-sig').splitlines()),'semantic_review':s}
                for name,(p,s) in sorted(unique.items())]
    systems = [
        {'id':'N08','name':'无线崩坏能与EU双能源结算','status':'已有真实能源工作票据与持久账户，缺部分机器消费者及实机验收',
         'implemented':['Hk3RecipeLogic在真实推进时提交，失败逆序退还实际能源改量，退款失败保留重试','HW任意精度账户、服务端存档绑定与严格损坏拒绝、临时文件原子替换','EU模拟不扣款、BigInteger精确合计、真实后端支付成功才报告处理，不足返回剩余','绑定真实支付时的账户/团队退款；成功推进后才记录EU/HW运行事实'],
         'gaps':['能源票据不代表物品/流体输入输出的跨资源原子事务','ERM/W13增益及世界泡/工程机器消费者仍未全部接入；能源基础存在不代表能源生产已完成','当前实例真实扣款、欠费、换队、断线/重启及并发机器运行未整体验收'],
         'runtime':'DualEnergyTick、GridEnergyPayment、WirelessAccount隔离生产算法/NBT/临时文件检查通过；本轮未运行世界。'},
        {'id':'gt_ae_integration','name':'GTL/AE融合及无限能力限制','status':'入口与GUI限制已接通，自动化限制未闭合',
         'implemented':['GTMachinesMixin挂GTLMachines.init尾部注册本模组机器','创造箱/罐正常获取保留，仅拦生存/冒险右键GUI','手机调用背包实际AE终端，保留原网络/范围与原生菜单'],
         'gaps':['创造箱/罐的管道、漏斗、AE及能力接口自动提取尚无对应生产拦截','普通获取、机器成型和真实运行事实不可相互替代；全版本兼容没有验收'],
         'runtime':'当前有历史指定实例启动记录；本轮未运行AE或自动化无限供给路径。',
         'decision_source':'doc/HK3GTL-内测5/01_GTL融合/GTL兼容与毕业能力限制.html'},
        {'id':'N01','name':'文明机器总览','status':'查询链已接通，跨模组与多人验收未完成',
         'implemented':['GT实际生命周期索引与队伍权限过滤','保守区分运行/停机/未加载/未知；不强载区块','限额队列与详情查询、客户端筛选分页'],
         'gaps':['需实机覆盖拆除、跨维度、重启、跨队权限和大规模目录；不能将未知状态猜成缺电'],
         'runtime':'历史r171记录过单台GT组装机目录与详情；本轮未启动游戏。'},
        {'id':'N07','name':'注视度与压力','status':'已批准个人/团队研究公式已接通，设施执行器仍有依赖缺口',
         'implemented':['个人原始值、来源日志、阈值一次性触发','按修订109保留个人记录、在线团队最高有效值、缓冲原值减50及增长减半','研究报价/速度、锚接口与HUD投影'],
         'gaps':['I36真实稳定锚及强化提供者尚未正式接入；接口存在不能充当实体供能通过','ERM/W13实际加速尚有机器依赖；全GTL工业独立降效仍待按现行合同实现'],
         'runtime':'规则/布局检查通过；多人上下线、换队、锚真实扣电未在本轮运行。',
         'decision_source':'doc/HK3GTL-内测5/讨论记录/2026-09-30_15-58-36_注视度与研究联动修订109_实现与验收边界.html'},
        {'id':'N14','name':'500彩蛋执行','status':'部分实现，363/500绑定当前条件（72.6%）',
         'implemented':['500条目录与条件文本；363条实际规则绑定','真实事务、作者归属、重放幂等、阅读回执及独立收藏账本'],
         'gaps':['137条尚未绑定；大量依赖尚不存在的机器/工程，不能弱化触发条件来凑数','彩蛋471研究进度读取个人UUID，遗漏队伍研究推进','跨模组Mixin实际注入和完整触发仍需目标实例验收'],
         'runtime':'check已通过规则与当前依赖字节码合同检查；未逐个游戏触发500条。'},
        {'id':'N09','name':'手机/应用/通知/供电','status':'基础服务与交互代码已接通，实例验收待补',
         'implemented':['物理手机128000EU与LV充电能力、服务端操作付费/节流','应用安装/电量门禁、持久通知、个人笔记CAS冲突保护','AE仅委托原终端与网络/权限/距离检查；不绕过原网络'],
         'gaps':['实际GT充电槽、AE无线界面、断线/冲突恢复和多人操作未整体验收'],
         'runtime':'纯逻辑、模拟与源码合同通过；本轮没有AE/GUI操作。'},
        {'id':'N10','name':'20角色微讯息与可选AI','status':'当前缩减范围的代码链已接通',
         'implemented':['20联系人、560离线回复、60动态、阶段0–4、历史回看','显式客户端自费AI配置、HTTPS或本机地址、超时/响应上限/不自动重试','旧连接回包epoch隔离与有界内存历史'],
         'gaps':['AI任意外部模型的人格语义不能由关键词过滤保证；真实服务未调用','扩展5600文本已明确后置；五组织实物贸易已取消，不能算待恢复缺失'],
         'runtime':'离线目录与本地HTTP模拟检查通过；不声称真实模型对话验收。'},
        {'id':'welcome_updates','name':'欢迎/版本详情/健康提示','status':'当前显示与确认代码已接通',
         'implemented':['按用户版本确认阅读、登录排队、不抢当前界面','更新历史/反馈复制/注册健康数据展示'],
         'gaps':['健康项只覆盖已列明注册与契约，不代表全部存档/配方健康','实际多版本阅读/重连/不同GUI缩放仍待游戏验收'],
         'runtime':'版本状态、列表与UI合同检查通过。'},
        {'id':'release_compatibility','name':'联机兼容与正式发布','status':'构建与部分兼容基础具备，正式发布条件未闭合',
         'implemented':['服务端权威动作、SavedData损坏拒重置、客户端投影','可选依赖Mixin隔离、Avaritia并发集合兼容、JEI资源检查','本轮完整Gradle check离线通过'],
         'gaps':['当前源码主线尚有确定缺失；不能仅更名就称正式版','缺当前最终内容下MAX至终局完整新档、专服多人/重启/死亡/重复操作验收','最终整包内存/光影目标按负责人决定后置，尚无通过证据','增强版2.9.2尚未由负责人更新，本轮未验证，不能自动宣布兼容'],
         'runtime':'本轮仅静态/逻辑检查；历史单机局部记录不等于本次全模组发布验收。'},
    ]
    anchors = {
        'N08':[('common/machine/Hk3RecipeLogic.java','energyTick.runWork','真实工作推进才确认能源付款'),('common/machine/Hk3RecipeLogic.java','HonkaiWirelessNetwork.reserve','配方tick预留HW并按工作票据退款'),('common/capability/Hk3EnergyTick.java','public boolean finish','失败逆序退款，失败票据保留'),('common/machine/trait/Hk3PlayerGridEnergyTrait.java','private boolean changeForTick','真实后端EU改量与实际账户退款'),('common/capability/Hk3GridEnergyPayment.java','public static Result input','任意精度求和与后端成功结果'),('common/capability/HonkaiWirelessNetwork.java','public static synchronized boolean reserve','服务端绑定的HW预留'),('common/capability/HonkaiWirelessSavedData.java','StandardCopyOption.ATOMIC_MOVE','临时文件原子替换持久HW账本')],
        'gt_ae_integration':[('mixin/GTMachinesMixin.java','Hk3Machines.init();','实际GTL初始化入口'),('common/event/Hk3CreativeItemGuard.java','event.setUseBlock(Event.Result.DENY);','实际只有右键GUI限制，不是能力提取拦截'),('common/phone/Hk3PhoneAeLink.java','public static int open','原生终端委托')],
        'N01':[('common/overview/Hk3MachineOverviewService.java','public final class','目录服务与只读投影')],
        'N07':[('common/gaze/Hk3GazeManager.java','public final class','个人G、在线团队最高值与缓冲执行')],
        'N14':[('common/easter/Hk3EggExploration.java','private static int progress','471读取个人UUID与队伍研究作用域不一致')],
        'N09':[('common/phone/Hk3PhoneAeLink.java','public static boolean available','实体终端供电/范围及原网络可用性')],
        'N10':[('client/phone/Hk3SocialAiClient.java','public final class','显式客户端AI请求与限制')],
    }
    for system in systems:
        system['evidence']=[]
        for rel,needle,claim in anchors.get(system['id'],[]):
            # 具体类名由现有源码核实；缺失定位拒绝发布而非生成假行号。
            system['evidence'].append(evidence(rel,needle,claim))
    findings = [
        {'id':'G-02','severity':'普通缺陷','title':'彩蛋471没有使用团队研究作用域',
         'evidence':[evidence('common/easter/Hk3EggExploration.java','private static int progress','data.completed(p.getUUID(),id)与当前团队研究作用域不一致')],
         'action':'后续修复使用ResearchTeams.scope并验证准备期间队友推进研究会中断条件；本轮只记录。'},
        {'id':'G-03','severity':'内容覆盖缺口','title':'500目录不等于500个可触发彩蛋',
         'evidence':[{'path':'logs/beta5-audit-20261025-gradle-check.log','claim':'Hk3EggRulesTest输出363个实际绑定'}],
         'action':'保留获批原触发条件，等待对应工业/工程真实事实接入；逐条件补齐137条。'},
    ]
    report = {'created_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
              'scope':'通用服务与事实观察适配器；实际逐份阅读后记录，不含隐藏思考或对话工具日志',
              'reviewed_files':[x['path'] for x in reviewed],'file_reviews':reviewed,
              'systems':systems,'findings':findings,
              'limitations':['未启动游戏、未调用外部AI、未改产品代码/版本/实例。','资源全量哈希及JSON语法检查不等于每张贴图视觉验收。']}
    OUT.joinpath('general-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'reviewed_java':len(reviewed),'systems':len(systems),'findings':len(findings)},ensure_ascii=False))


if __name__ == '__main__':
    main()
