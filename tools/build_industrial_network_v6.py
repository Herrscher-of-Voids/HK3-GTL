"""2026-10-15：生成工业网络讨论稿，保留正式配方与建筑资源。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import hashlib
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'doc/HK3GTL-内测5/02_工业计划'
OUT = ROOT / 'deliveries/工业网络扩展雏形_V6_20261015'
LOG = ROOT / 'logs/industrial-network-v6'


def line(i, name, group, stage, machines, feed, flow, products, buyers, recycle, bootstrap, identity, old):
    return dict(id=f'N{i:02}', title=name, group=group, stage=stage,
                machines=machines.split(), feed=feed.split('；'), flow=flow.split(' → '),
                products=products.split('；'), consumers=buyers.split(), recycle=recycle,
                bootstrap=bootstrap, identity=identity, legacy=old.split(), status='本轮雏形，未注册配方')


LINES = [
line(1,'崩坏能分级与液态原料平台','基础化工','A','I01-1 I02 I03 I04',
     '环境采集物；MAX可得过滤材料；稳定剂与EU',
     '混合液态采集物 → 光谱分级与除杂 → 离心分离 → 各级液态稳定',
     '工艺级稳定液态崩坏能；高纯载能母液；待精制浓缩组分','N03 N07 N19',
     '母液按杂质浓度分流；不可回用部分输出浓缩残液，不能把杂质无限回灌。',
     '首采、分析和基础稳定只用MAX既有材料；高纯路线后解锁，不反卡首批原料。',
     '相分离与原料分级借鉴化工；崩坏能载体和纯度等级为本模组工程设定。','L1'),
line(2,'溶剂、稳定剂与催化介质平台','基础化工','A','I05 I09',
     '格雷已有新鲜溶剂与载体；各线分类废液；补充稳定组分',
     'GT基础溶剂制备 → 崩坏适配调配 → 按用途供液 → 分类解吸再生',
     '稳定工艺介质；纳米分散介质；抗侵蚀包覆浴；再生清洗介质','N01 N07 N08 N11 N17',
     '稳定液、包覆浴、含金属废液各用独立再生配方；新鲜补料和浓缩废物出口常驻。',
     'A阶段由GT配制新鲜基础介质；B阶段再用I09配制特殊分散介质。各类均有新鲜路线，不要求先有自身废液。',
     '平台提供具体化学用途；普通蒸馏和基础反应用GT，I05只承接特殊介质再生。','L1 L3'),
line(3,'分级燃料调配与封装','能源循环','A','I06 I17 I18 I19 I20 I21 I22',
     '稳定液态崩坏能；常规燃料基液；可达棒壳；后期固态浓缩组分',
     '基液调配 → 普通/浓缩两类及浓缩料高纯工况 → 棒壳灌注与检漏 → 对应反应堆运行',
     '普通崩坏能燃料；浓缩燃料棒；高纯长周期规格浓缩燃料组件；EU','N04 N06 N29',
     '高纯规格仍属浓缩燃料，不新增第三类系统。消耗燃料内容物，分离用后棒壳与失活物；不同堆按许可和白名单运行。',
     '普通棒壳由MAX材料制造；高级魂钢壳仅是后续路线。初次启动电量来自已可达电网。',
     '借鉴炼制、调和、封装分工；保留普通线用途，高级堆不等于删除低阶工厂。','L2 L4'),
line(4,'用后燃料与载体后处理','能源循环','B','I03 I05 I17 I18',
     '用后燃料组件；清洗介质；新鲜载体；EU',
     '封装阵列卸料 → 失活物与棒壳分类 → GT清洗分离 → 特殊载体再生与复验',
     '复验棒壳；回收燃料载体；待精制残余组分；浓缩失活废物','N03 N11 N25',
     '残余组分需I17补料再精制；燃料能量不随棒壳恢复。破损壳仅回收基础材料。',
     '新壳和新燃料均有原生路线；后处理提高利用率，不作为首次发电前置。',
     '是多产品回收产业；不新增真实核工业细节，也不把废棒直接变满能燃料棒。','L4'),
line(5,'工艺气氛与异质气体处理','基础化工','A','I01-3 I03 I05 I23',
     'GT惰性气体；纳米与包覆工艺尾气；后期气态崩坏能',
     'GT制气与干燥 → 分流净化 → 崩坏适配气氛配制 → 尾气回收或降级',
     '魂钢保护气氛；低杂质密封气氛；低温工艺气氛；待处理异质尾气','N11 N12 N15 N19',
     '普通气体交GT净化，特殊污染物经专门配方分离；异质尾气不能当免费保护气。',
     '早期保护气来自GT气体加已可达稳定组分；I01-3和I23仅后期分支，不卡魂钢首通。',
     '气体纯度、循环污染和工艺气氛各有用途；I23只处理相变支路，不包办普通制气。','L3 L4'),
line(6,'冷却介质与热量梯级利用','能源循环','A','I05 I19 I20 I21 I22 I23',
     'GT冷却剂与换热材料；反应堆/退火/相变过程热流；补充流体',
     'GT制备冷却剂 → 分温区供给 → 消耗机器配方输出热流体 → GT换热与回流',
     '洁净低温冷却介质；高温传热介质；可利用热流；失效冷却剂','N03 N12 N18 N29',
     '封闭回路仍有损耗与耗电；余热回收与反应堆EU同一能量账，不能双算全部燃料能量。',
     '基础冷却配方用GT普通流体启动；高阶介质不倒挂低阶反应堆。',
     '以热网和多温区供给形成独立公用工程产业；本轮不引入新换热多方块。','L4 L10'),
line(7,'异质前驱体与功能浆料平台','精密材料','B','I09 I03',
     'GT精制金属/陶瓷原料；稳定崩坏能；分类溶剂',
     'GT原料提纯 → 按功能配位/分散 → I09特殊前驱体调配 → 分级与定量供料',
     '魂钢前驱液；薄膜前驱液；陶瓷浸渗浆料；耐侵蚀层前驱液','N08 N11 N12 N15 N17',
     '母液分离回N02；金属回收需识别种类，杂质浆料不能充当任意高纯前驱体。',
     '基础前驱液不需魂钢设备自产魂钢；原料可由MAX现有材料提供。',
     '普通合成在GT；I09承担异质分散稳定与配制，不靠配方名就把所有化工搬进釜。','L3'),
line(8,'纳米基元与功能颗粒','精密材料','B','I10 I03',
     '分用途前驱液；分散介质；GT已有晶种与电子材料',
     '成核与基元合成 → 粒径/缺陷分级 → 功能修饰 → 按用途输出颗粒',
     '结构纳米基元；导热纳米基元；传感纳米基元；微执行基元','N09 N13 N14 N18',
     '不合格基元按成分回收前驱料；失活颗粒须重新合成，不直接变可用机器人。',
     '首批晶种来自普通材料，不依赖已经制成的魂钢或高级核心。',
     '用颗粒功能区别工艺，不是相同配方换颜色；基元不是成熟纳米机器人。','L3'),
line(9,'纳米执行单元与微装置','精密材料','B','I11',
     '各功能纳米基元；微型执行器；控制载体；GT精密零件',
     '微执行器支线 → 基元/载体配准 → 纳米单元装配 → 失效筛除与分档',
     '结构纳米单元；维修纳米单元；传感纳米单元；精密执行单元','N10 N17 N18 N21',
     '失败装配拆出可回收金属和失活基元；合格单元与废件不双返。',
     '初代控制载体用GT电路；后期HK3电路优化，不反卡首批纳米装配。',
     'I11负责纳米尺度装配，不承接完整无人机总装。','L3 L14'),
line(10,'自组织群与可编程材料','精密材料','B','I12',
     '合格纳米单元；规则模板；实物控制载体；EU',
     '结构/传感/维修规则选择 → 实物单元群编程 → 小样稳定性验证 → 合格群体封装',
     '结构自组织纳米群；界面修复纳米群；定向导热纳米群；阵列传感纳米群','N11 N12 N13 N18',
     '失败群失活后回N08；规则模板是非消耗工具，实际单元和控制载体按配方消耗。',
     '基础规则由前序研究解锁；不用未来奇观或魂钢数据载体作为首批规则唯一来源。',
     '产物是具用途的物质纳米群；研究许可是条件，不能当可复制物料。','L3'),
line(11,'抗侵蚀包覆与界面工程','精密材料','B','I13 I05',
     '纳米群/基片/框架；分用途包覆前驱液；保护气氛',
     'GT普通清洗 → I13崩坏适配包覆 → 分层固化 → 隔离/附着力检验',
     '抗性包覆纳米群；耐侵蚀薄膜；气密阻隔层；绝缘复合界面','N12 N17 N21 N30',
     '废包覆浴分类再生；退镀返回原始基材或降级料，不复制基材和完整涂层。',
     '首批包覆介质来自N02/N07，不需要已成形的高级耐侵蚀外壳。',
     '普通涂覆保留GT；I13处理崩坏环境下界面隔离，不泛化成万能表面处理。','L3'),
line(12,'魂钢聚合、退火与精密成形','精密材料','B','I14 I15 I16',
     '抗性包覆结构纳米群；魂钢前驱液；合格金属骨料；保护气氛',
     '纳米群与骨料定量汇合 → I14聚合致密化粗坯 → I15重构退火稳定坯 → I16分用途加工',
     '结构魂钢板；低应力魂钢精密坯；耐热魂钢承压件；魂钢信息载体基底','N13 N20 N21 N27 N32',
     '聚合残渣是副产物；切屑需拆解失活与再配料，回收品不能保持完整已编程组织。',
     '首批压铸/退火机壳走前序可达材料；高级魂钢升级件只优化后续配方。',
     '保留纳米自组织本质。修正当前“残渣→数据基板”断层；I14 V4建筑已认可，工艺重构仍属雏形。','L3'),
line(13,'自修复复合材与智能夹层','精密材料','B','I12 I13 I14 I15',
     '界面修复纳米群；GT复合纤维/树脂；魂钢网；隔离介质',
     '常规层材预制 → 受控群体嵌入 → 压合共固结 → 组织稳定与分层检验',
     '可维修复合板；定向导热夹层；传感复合蒙皮；低应力密封复合垫','N21 N27 N30 N32',
     '维修消耗补充纳米料和基体；损坏构件只回收一部分材料，不能永久无耗自愈。',
     '首代以现有复合材为基底；高阶功能蒙皮不作为制造本线设备的唯一材料。',
     '普通复材由GT制造，专机处理群体嵌入/稳定；是多物料产业，不追加装备战斗系统。','L3'),
line(14,'导能互连与低损耗材料','电子光学','B','I09 I10 I13 I15 I16',
     'GT导体/超导前体；定向导热纳米料；绝缘介质；魂钢基材',
     'GT导体与箔材制备 → 特殊界面浸渗 → 保护层包覆 → 稳定化与线/片加工',
     '崩坏适配互连箔；低温导能复合带；高载流连接片；热界面材料','N17 N28 N29 N31',
     '边角料回金属分选；绝缘层与导体分别回收，热力学损耗由整机配方统一核算。',
     '低阶互连使用GT已有导体；超导与虚数适配带分期解锁，不能提前获得终局导能。',
     '区分微观材料供给与N29整机电力设备；不凭名称宣称所有材料常温零电阻。','L3 L10 L13'),
line(15,'结构陶瓷与场约束介质','精密材料','B','I09 I13 I14 I15',
     'GT氧化物/氮化物等陶瓷料；浸渗浆料；隔离纳米料',
     'GT陶瓷粉体与坯体制备 → 异质浸渗 → 压力复合 → 保护气氛稳定化',
     '耐侵蚀陶瓷衬片；低温绝缘陶瓷件；约束场介质坯；耐热复合衬里','N03 N20 N27 N30',
     '废陶瓷按等级降级利用；浸渗液分离再生，不能把破碎衬片无损回成高精度件。',
     '初代衬里由普通GT陶瓷承担；特殊介质先解锁自身材料，不依赖尚未建成锚阵。',
     '借鉴粉体—成形—烧结—浸渗；专机只承担魂钢/异质复合段。','L9 L11'),
line(16,'功能聚合物与隔离膜材','基础化工','A','I13',
     'GT已有高性能聚合物与前体；纤维/填料；分用途隔离介质',
     'GT双前体与聚合支线 → 膜/纤维/树脂分流 → 功能填料混合 → 崩坏适配界面包覆',
     '耐介质密封膜；精密电路基膜；低放气封装树脂；耐侵蚀滤材','N02 N17 N20 N30',
     '溶剂有分类回用端；固化树脂优先降级回收，不默认逆聚合无损返单体。',
     'GT材料直接供初代膜材；特殊表面处理在B后开放，不要求I13才能获得普通膜材。',
     '参考目标包PEEK跨行业用途；主体合成、蒸馏、聚合留在GT平台。','L13'),
line(17,'崩坏适配电子与控制组件','电子光学','A','I13 I16',
     'GT晶圆/电路；互连箔；功能基膜；纳米执行/传感组件',
     'GT晶圆与逻辑/存储/功率分流 → GT刻蚀/组装 → 特殊隔离封装 → 分档测试',
     '抗侵蚀控制板；阵列传感控制模块；功率驱动模块；魂钢信息载体组件','N09 N18 N21 N29 N32',
     '板卡拆解分别回金属/封装料；运行档案不随拆机复制，测试不把不合格件变合格件。',
     'A阶段普通控制板与首批纳米工艺继续用GT电路；B后才开放I13特殊隔离封装，自有电路是后续耐环境/集成路线。',
     '普通晶圆、蚀刻、整机装配用GT；I16仅加工专用魂钢封装壳与基底。','L2 L13'),
line(18,'光学、探测与测量硬件','电子光学','A','I02 I07 I10 I16',
     'GT光学/传感材料；传感纳米料；功能薄膜；可达控制板',
     'GT光学元件制备 → 传感阵列成形 → 探测器/传感硬件装配 → 普通器件GT检测，既有探测器I07校准',
     '光谱探头；量子异常探测组件；场梯度测量头；精密位置反馈组件','N19 N21 N22 N27',
     '被校准设备返还；校准介质和试片按配方消耗，报告只记录精度不兑换原料。',
     'MAX初始探测器先可制造，基础采集不依赖I07高级校准；后续组件按阶段解锁。',
     '这是实物传感器产业；I07只校准既有探测器，不包办所有光学/传感硬件检测，报告不充当物料产量。','L2 L9'),
line(19,'定向结晶与仿制核心材料','核心器件','B','I08 I02',
     '分级崩坏能载体；GT晶种/定向材料；对应核心研究许可',
     '晶种与载体准备 → 按既有核心种类定向结晶 → 缺陷检测 → 合格晶体分档',
     '合格仿制核心晶体；定向场耦合晶片；研究用缺陷晶体','N20 N27 N28 N31',
     '晶种消耗或返还须逐配方写清；缺陷晶体只降级/回收，不无条件充当各类核心。',
     '每类核心由前序研究/材料解锁；不消耗原作唯一核心，不把所有核心一次开放。',
     '沿用项目已议九类核心边界；配方分支不意味着新增律者种类或官方量产技术。','L5'),
line(20,'核心封装与仿制神之键组件','核心器件','B','I13 I16 I33',
     '对应仿制核心；魂钢精密件；隔离/导能材料；控制载体',
     '魂钢壳与耦合件并联制备 → 核心定向封装 → 既定神之键组件装配 → 功能检验',
     '隔离核心舱；场耦合模块；既有仿制神之键组件；第二神之键工程组件','N23 N24 N27 N32',
     '封装失败拆回可回收外壳料；核心按定义降级，不连同成功成品双返。',
     '普通组件先由I33前序配方制备；信标/列车用途按既定量子阶段可达性审查。',
     '神之键来自官方世界观锚点；这里制造的是已议范围的仿制工程件，不擅加新神器。','L5'),
line(21,'无人作业装置与可维修部件','装备与物流','B','I11 I13 I14 I16 I26',
     '魂钢/常规框架；精密执行器；传感器与控制板；密封耐磨材料',
     '承力件与执行件并联 → GT装配线总装 → 用途模块安装 → 调度前检测',
     '无人采掘作业模块；密封探针组件；维护备件包；跨界物流作业组件','N22 N23 N26 N32',
     '维护消耗密封件/执行件；损坏装置拆件修复，完整新件与回收旧件不能同时产出。',
     '首次量子探测有MAX可造基础探针；高阶无人模块不以首次采掘才出产的稀有件启动。',
     '主体装配用GT；I26只调度，作业装置作为物品/任务能力，不自动新建飞行实体系统。','L6 L14'),
line(22,'真实世界泡无人采掘资源链','装备与物流','C','I24 I25 I26 I44',
     '有效目标与锁定信息；无人作业模块；维护耗材；能源',
     '异常观测与坐标验证 → 锁定真实目标 → 无人采掘任务 → 物品/流体/遗留件分仓',
     '原定随机物品交付包；原定随机流体交付；带来源遗留件','N25 N26 N32',
     '真实目标最多十次采集，重试不重复结算；满仓等待，维护废件回N26。',
     '基础任务不依赖后期I39；首轮使用前序可达装置，保持原ULV–MAX随机资源边界。',
     '资源获取产业，I24/25/26/44为观测和调度服务；并非在调度台里化学合成资源。','L6'),
line(23,'真实世界泡捕获与终止资源链','装备与物流','C','I25 I27 I28 I44',
     '有效真实目标；场约束容器组件；第二神之键组件；稳定介质与能源',
     '目标锁定 → 容器与稳定系统接入 → 完整捕获 → 终止与分类交付',
     '原定终止回收物品；原定终止回收流体；遗留技术实物；用后容器','N25 N26 N30',
     '共享真实目标身份，一次终止结算；用后容器另走清洗/检验，不复活原目标。',
     '首批容器采用前序魂钢与场约束材料；不要求从已终止世界泡才能取得容器首料。',
     '保留原资源/概率规则；不擅加先采掘后终止惩罚，也不额外发一份“高纯资源”。','L7'),
line(24,'模拟世界泡物质投入与回收','装备与物流','C','I29 I30 I31',
     '前序可达模拟种子材料；物质投入；稳定介质；持续能源',
     '构筑初始状态 → 持续投料与稳定 → 模拟运行 → 终止并分类结算',
     '原定随机物品交付包；原定随机流体交付；可回收稳定载体；模拟运行档案','N25 N26 N31',
     '一轮只结算一次；模拟来源单独标记。种子返还/增产倍率待定，不能假定免费复制种子。',
     '不依赖W10/W14或二审后奖励启动；保持原定随机目录、数量与物品等概率规则。',
     '模拟物资采用项目既定玩法；来源档案不能冒充真实遗留文明证据，不私自削改奖励。','L8'),
line(25,'异质回收物分类与稀散材料','基础化工','C','I02 I03 I05',
     '已经结算的世界泡交付物；全线废边料/废液；GT分选介质',
     '来源验收与分类 → GT拆解/洗选/提纯 → 异质成分分离 → 各品级返料',
     '分类金属返料；可回用工艺流体；降级复合填料；特殊组分精制料','N02 N07 N14 N31',
     '只处理实际收到的原料；可直接使用的GT物资无需强制过本线，不另复制世界泡奖励。',
     '常规废料分选早可运行；C阶段仅拓展异质来料，稀缺前驱体有原生备选。',
     '借鉴矿物多产品分离与稀散提取；只有特殊成分段用HK3专机。','L6 L7 L8'),
line(26,'遗留硬件再制造与全厂维修','装备与物流','B','I02 I07 I16 I32',
     '失效泵阀/探头/无人装置；后期遗留硬件；新制备件与清洗料',
     'GT拆检与材料分级 → 更换实物备件 → 特殊零件再加工 → GT普通器件复验，既有探测器I07复校',
     '翻修传感组件；再制造执行组件；合格回用壳体；待逆向遗留实物','N18 N21 N23 N32',
     '消耗新件并剔除不可修复部分；I32只验证遗留技术，重复硬件不复制研究事实。',
     'B阶段维修用本厂常规零件启动；C阶段增加遗留硬件支路，不以随机遗留件卡主线。',
     '这是维修物质流，和I32研究档案分开；不会只靠读一份数据生成完整组件。','L6 L7 L14'),
line(27,'空间锚件与约束容器组件','空间与约束','D','I13 I14 I15 I16 I33 I35',
     '魂钢承力坯；约束陶瓷；隔离核心舱；低温/导能材料',
     '承力坯压力成形 → 退火精加工 → 场耦合组件并联 → GT装配与I35工作态校准',
     '空间锚承力组件；约束容器支承组件；场耦合阵列；稳定锚替换构件','N23 N28 N30 N32',
     '失效承力件只按材料回收；空间状态和坐标是条件，不是可无限复制的物质输入。',
     'C阶段普通捕获容器由前序N12/N15/N20直接装配；本线是D阶段强化件，不卡C首通。',
     'I35执行锚定/工作态校准；锚件实物在制造设备中形成，不在观测阵列凭报告生成。','L9'),
line(28,'能态整流材料与转换器件','空间与约束','D','I01-4 I13 I16 I33 I38',
     '能量态崩坏能；导能复合带；核心耦合件；隔离封装料',
     '转换组件制造 → 授权绑定与安装 → I38受控整流 → HKE生产与工艺介质维护',
     '整流耦合组件；能态隔离组件；工作介质；可用HKE','N27 N29 N30 N31',
     '制造、整流效率与耗材单独记账；已定账户无线无损/无限吞吐不被改成有损传输。',
     '机器建造和启动用前序可达能源与组件；不靠自产HKE作为取得首套整流器唯一条件。',
     '器件制造与I38能源服务分开；不以一条整流配方替代整个材料产业。','L10'),
line(29,'功率模块与文明电力装备','电子光学','D','I16 I33 I41',
     '导能复合材料；绝缘陶瓷；功率板；冷却组件；常规导体',
     '母排/连接件制备 → GT功率模块装配 → 绝缘封装与试验 → 调度端部署',
     '高载流功率组件；低温电力连接器；能态设备供能接口件；电网维护组件','N03 N28 N31 N32',
     '可更换损耗件回N26；I41调度不额外创造能源，不改变既定HKE传输账户规则。',
     '普通MAX电力设备继续承担起步；此线制造后期适配件，非全厂换机硬门槛。',
     'N14供导体材料，本线组成功率装备；I41只调度，整机装配在GT而非调度台。','L10 L12 L13'),
line(30,'隔离、防护与洁净工业组件','空间与约束','B','I13 I16 I36',
     '耐侵蚀膜；密封复合材；场约束衬片；前序可达核心/替代材料',
     'GT过滤密封组件制备 → 特殊隔离包覆 → 防护组件组装 → 稳定锚运行复验',
     '耐侵蚀过滤组件；洁净密封单元；场约束隔离模块；稳定锚维护组件','N17 N21 N23 N32',
     '滤材吸附有饱和/废料出口；维护消耗料与无消耗控制件区分，不以污染凭空变材料。',
     'S01基础稳定锚研究边界保留；基础锚材料不得强制依赖高级仿制核心或D级锚件。',
     '基础防护与高级约束两档分开；I36运行覆盖能力，不作为万能零件制造机。','L9 L10'),
line(31,'四系文明功能材料','文明工程','E','I40 I13 I15',
     '导能带与晶片；约束陶瓷；自组织复材；信息载体与传感阵列',
     '导能支线/约束支线/重构支线/认知支线分别备料 → I40分别合成 → 各系独立稳定化 → 用途分级',
     '导能复合材；约束复合材；重构复合材；认知功能材','N29 N30 N32',
     '四类废料按成分分开返料；不允许一种废料无差别兑换四种终局材料。',
     '每类首批材料由前序工业生产；同一奇观的运行产物只能优化后续配方，不能卡自身首建。',
     '四种功能使用不同物质支路，替换现行一锅产四料的暂定配方；认知材料不等于量产人的意识。','L11'),
line(32,'大型预制件、奇观与仿制舰工程','文明工程','C','I16 I42 I43 H01',
     '魂钢与功能复合材；承力/导能/约束/认知子组件；工程图纸与阶段许可',
     '前序零件并联制造 → 构件族预制 → 分工程GT总装/施工 → C阶段自身成型与功能检查，E阶段I43工程复核',
     '承力框架与舰体分件；导能预制模块；约束预制模块；认知阵列分件','H01 W01 W02 W03 W04 W05 W06 W07 W08 W09 W10 W11 W12 W13 W14 W15',
     '预制边角料回N25；完成记录由运行取得，不在配方里制造“毕业证明”。',
     'C阶段仿制舰基础分件用GT/I16，自身成型/供能/功能检查不等I42或I43；E阶段再走高级预制与工程复核，毕业仍需有效舰工程记录。',
     '构件按用途和工程图组合，拒绝一个万能奇观方块；既定舰体外观、奇观职责与终审顺序保留。','L11 L12 L14'),
]

GROUPS = [
    dict(id='基础化工', subtitle='分级、分离、介质与聚合物'),
    dict(id='能源循环', subtitle='燃料、后处理与热管理'),
    dict(id='精密材料', subtitle='纳米、魂钢、复材与陶瓷'),
    dict(id='电子光学', subtitle='互连、控制、测量与功率'),
    dict(id='核心器件', subtitle='定向核心与受控封装'),
    dict(id='装备与物流', subtitle='无人作业、资源获取与维修'),
    dict(id='空间与约束', subtitle='锚件、隔离与能态器件'),
    dict(id='文明工程', subtitle='四系功能材料与大型预制'),
]

SERVICES = [
    dict(title='分析与研究', machines='I02 I07 I32 S01 S02 S03 S04 S05', duty='分析、校准、逆向与研究许可；样件和实验不计量产产品族。'),
    dict(title='观测与任务状态', machines='I24 I25 I26 I27 I28 I29 I30 I31 I34 I39 I44 I45', duty='目标身份、运行状态、坐标、物流和一次性结算；不是把随机资源写成普通合成。'),
    dict(title='场与能源运行', machines='I19 I20 I21 I22 I23 I35 I36 I37 I38 I41', duty='运行模式、燃料白名单、负载与维持工况；不要求人为凑十种材料配方。'),
    dict(title='工程验收与文明成果', machines='I43 H01 W01 W02 W03 W04 W05 W06 W07 W08 W09 W10 W11 W12 W13 W14 W15', duty='从实际建设和运行读取证据；不能靠配方制作证明、重复提交刷奖励。'),
]

ITEM_DRAFTS = [
    ('化工介质','稳定工艺介质；纳米分散介质；抗侵蚀包覆浴；魂钢保护气氛；陶瓷浸渗浆料；薄膜前驱液'),
    ('纳米与魂钢','导热纳米基元；传感纳米基元；精密执行单元；界面修复纳米群；定向导热纳米群；粗魂钢坯；低应力魂钢坯；耐热魂钢承压件'),
    ('复材与隔离','可维修复合板；定向导热夹层；传感复合蒙皮；耐侵蚀陶瓷衬片；低温绝缘陶瓷件；耐介质密封膜；低放气封装树脂'),
    ('电子与光学','崩坏适配互连箔；低温导能复合带；抗侵蚀控制板；阵列传感控制模块；功率驱动模块；量子异常探测组件'),
    ('装备与工程','无人采掘作业模块；密封探针组件；维护备件包；空间锚承力组件；场耦合阵列；能态隔离组件；耐侵蚀过滤组件；洁净密封单元；高载流功率组件'),
]

RECIPE_POLICY = dict(
    scope='重写HK3GTL目前已有与后续新增的物品制造配方；GTL整合包原有配方保留为比较基准，不在本条范围内批量改写。',
    baseline='以用户指定的GregTech Leisure-增强版2.7实际GTL MAX阶段对应配方与工艺链为基线。比较前实查当前安装版本与配方替换脚本。',
    progression='HK3GTL高于MAX阶段的各电压阶级，配方整体门槛须高于对应MAX工业基线；HK3GTL自身同一产品/产品族随着电压每升一阶，综合难度必须实质提高，不得降低，也不得存在更高阶段的低门槛旁路。',
    dimensions=['前置中间体的工序深度与并行汇流','原料品类、纯度等级和支线来源','所需机器工艺、机器数量/协同与可用电压','研究许可和阶段解锁','固液气流体、催化工具、质量检测与副产物处理','EU/t、总能耗、时间、批量和产出'],
    method='逐品族建立“增强版2.7 GTL MAX基准→HK3GTL最高对应层级→逐级电压配方”对照；记录实际KubeJS/Java最终有效配方来源。每条配方注明直接MAX对照或不可比原因，标记新增支线/设备/阶段门槛，绘制物料依赖并核查可达性。',
    guardrails=['同一产品族每升一电压阶须比前阶有实质难度提升，体现在至少一个工艺/材料/阶段维度；综合门槛不得因其他优惠而变得更轻。','配方层级整体评估，不要求每种原料数量单调增加；难度提升必须有工艺或阶段意义，不能只放大数量/时长/电压数字。','后期配方不得反向成为更便宜、更早产物或跳过低阶前置的捷径；效率升级须保留高阶研究、材料和设备门槛。','GTL MAX配方仅是比较基线，不把其最终配方原样照搬；HK3GTL须增加有主题逻辑的工序和跨线依赖。','面向服务/研究/能量状态的配方或操作单独分类，不用无关材料数量硬造难度。','正式改写前先做完整清单和对照矩阵，再分批实现；配方注册集中遵循Java Hk3RecipeAdder，避免重复KubeJS注册。'],
    status='用户已确认的长期重构要求；当前只记录准则，本轮未改写正式游戏配方。',
)

SOULIUM_STEPS = [
    ('I09','前驱体调配','魂钢前驱液','N02介质、GT精制金属汇入；其余前驱体另供薄膜/陶瓷。'),
    ('I10','纳米基元合成','结构纳米基元','导热/传感基元是同机其他工艺族，分别供N14/N18。'),
    ('I11','执行单元装配','结构纳米单元','GT微执行器、控制载体在这里汇流，不能只给一包金属粉。'),
    ('I12','自组织群编程','结构自组织纳米群','规则模板作为工具；材料和控制载体按具体配方消耗。'),
    ('I13','抗性包覆','抗性包覆纳米群','N11包覆浴与N05气氛在此汇流；薄膜/外壳也有独立包覆路线。'),
    ('I14','聚合压铸','粗魂钢坯 + 聚合残渣/尾液','残渣回收，主产品必须是实物粗坯；多个用途坯料采用不同配料/模具。'),
    ('I15','重构退火','稳定魂钢坯','结构、低应力、耐热/低温用不同工艺；不得从残渣一步跳成信息板。'),
    ('I16','精密加工','板、壳、锚件、载体基底','至少分向N20核心舱、N21无人框架、N27锚件、N32大型工程。'),
]


def main():
    timestamp = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    audit = json.loads((LOG/'existing_network_audit.json').read_text(encoding='utf-8'))
    coverage = json.loads((LOG/'role_coverage.json').read_text(encoding='utf-8'))
    families = json.loads((LOG/'machine_family_proposal.json').read_text(encoding='utf-8'))
    if isinstance(families, dict):
        families = families.get('machines', families.get('roles', families.get('proposal', [])))
    catalog = json.loads((ROOT/'structure_catalog.json').read_text(encoding='utf-8'))
    legacy = audit['lines_L1_L12'] + audit.get('historical_candidate_lines_L13_L14', [])
    for row in legacy:
        if row['id'] in {'L13', 'L14'}:
            row['title'] = row['title'].replace('新增支线 · ', '新增提案 · ')
    data = dict(schema=1, title='工业网络扩展雏形 v6', timestamp=timestamp,
                status='讨论雏形；所有新增工艺与产品均未写入正式注册',
                baseline=dict(historical_structure_catalog=69,structure_minimum=84,
                              structure_conservative_target=88,
                              structure_target_basis='4台MAX + 16个自定义电压各至少5台 = 84台下限；若现有电压映射不能安全调整4台，则按88台补齐。',
                              industrial_roles=48,old_numbered_lines=12,
                              canonical_line_ids=[f'L{i}' for i in range(1,13)],
                              additional_proposed_line_ids=['L13','L14'],
                              line_preservation_rule='原定L1-L12的编号、阶段归属、工业目标与端到端身份必须保留；后续矩阵中的L13/L14须纳入扩展总图并继续标为提案；N01-N32是支撑工艺支线，不得替代或合并工业线。',
                              historical_extra_structures='I46–I53八座仅历史候选，本轮不批准或接入'),
                proposed=dict(process_branches=32,additional_industrial_line_proposals=2,
                              industry_groups=8,new_multiblocks=0,
                              exact_recipe_count=None,texture_approval='全部新增/重绘物品贴图待用户审批'),
                groups=GROUPS, lines=LINES, services=SERVICES, machines=families,
                coverage=coverage, catalog=catalog, legacy=legacy,
                recipe_policy=RECIPE_POLICY,
                item_drafts=[dict(group=g,names=s.split('；'),state='品名草案；先查现有物品复用；未注册、未绘制贴图') for g,s in ITEM_DRAFTS],
                soulium_steps=[dict(machine=m,operation=o,output=p,branch=b) for m,o,p,b in SOULIUM_STEPS],
                references=[
                    dict(title='目标实例：多前体与共产品',path='polymer_materials.js',line=29,detail='14个直接登记，5类操作；催化复用、前体汇流、共产品。'),
                    dict(title='目标实例：同基底多类晶圆',path='circuit_boards.js',line=102,detail='同一基底分流12类晶圆；最终工具受circuit_substitution.js覆盖。'),
                    dict(title='目标实例：跨行业材料出口',path='advanced_circuits.js',line=133,detail='PEEK箔供光学元件与多阶电路。'),
                    dict(title='目标实例：明确试剂回流',path='trace_metals.js',line=49,detail='上游消耗端与下游53行返还端相连；仍需补料耗电。'),
                    dict(title='目标实例：用户举例已找到',path='advanced_chemistry.js',line=160,detail='确认物品存在；只借鉴游戏中的多前体汇流/共享设备/副产物流图式。'),
                    dict(title='官方漫画：《神之键》',url='https://manga.honkaiimpact3.com/book/1018',detail='神之键及前文明研究是世界观锚点；本提案工艺不是官方技术设定。'),
                    dict(title='官方漫画：《第二神之键》',url='https://manga.honkaiimpact3.com/book/1014',detail='其他世界与文明观测的世界观锚点；不据此杜撰官方资源量产配方。'),
                    dict(title='官方漫画：《第二次崩坏》魂钢章节',url='https://manga.honkaiimpact3.com/book/1005/34',detail='魂钢题材锚点；纳米群体工艺细节按本项目衍生工程设定。'),
                ])
    source_root='C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft/kubejs/server_scripts'
    for ref in data['references']:
        if 'path' in ref:
            ref['url']=Path(source_root,ref['path']).as_uri()
    validate(data)
    payload=json.dumps(data,ensure_ascii=False,indent=2)
    DOC.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (DOC/'工业网络扩展雏形_v6.json').write_text(payload+'\n',encoding='utf-8')
    page=(ROOT/'tools/industrial_network_v6_template.html').read_text(encoding='utf-8')
    page=page.replace('__DATA__',payload.replace('</','<\\/'))
    (DOC/'工业网络扩展雏形_v6.html').write_text(page,encoding='utf-8')
    (OUT/'index.html').write_text(page,encoding='utf-8')
    (OUT/'工业网络扩展雏形_v6.json').write_text(payload+'\n',encoding='utf-8')
    for name in ['reference-audit.json','existing_network_audit.json','role_coverage.json','classified_processes.json','machine_family_proposal.json']:
        shutil.copy2(LOG/name,OUT/name)
    shutil.copy2(DOC.parent/'讨论记录/2026-10-15_23-43-21_GTL_MAX基线与HK3GTL配方递增重构.html', OUT/'GTL_MAX基线与HK3GTL配方递增原则.html')
    manifest=dict(timestamp=timestamp,status=data['status'],files=[])
    for f in sorted(OUT.iterdir()):
        if f.is_file() and f.suffix not in {'.zip'} and f.name!='manifest.json':
            manifest['files'].append(dict(name=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    archive=OUT/'工业网络扩展雏形_V6_讨论稿.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.iterdir()):
            if f.is_file() and f!=archive:
                z.write(f,f.name)
    report=validate(data)
    report['zip']=dict(path=str(archive),bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    report['timestamp']=timestamp
    (LOG/'proposal-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(archive) as z:
        archive_matches=all(z.read(row['name'])==(OUT/row['name']).read_bytes() for row in manifest['files'])
        archive_matches=archive_matches and z.read('manifest.json')==(OUT/'manifest.json').read_bytes()
    html_doc=(DOC/'工业网络扩展雏形_v6.html').read_text(encoding='utf-8')
    html_delivery=(OUT/'index.html').read_text(encoding='utf-8')
    json_doc=json.loads((DOC/'工业网络扩展雏形_v6.json').read_text(encoding='utf-8'))
    json_delivery=json.loads((OUT/'工业网络扩展雏形_v6.json').read_text(encoding='utf-8'))
    delivery=dict(timestamp=timestamp,passed=archive_matches and html_doc==html_delivery and json_doc==json_delivery and '\ufffd' not in html_doc,
                  manifest_files=len(manifest['files']),zip_members=len(manifest['files'])+1,
                  zip_sha256=report['zip']['sha256'],archive_matches_disk=archive_matches,
                  document_delivery_identical=html_doc==html_delivery and json_doc==json_delivery,
                  no_replacement_character='\ufffd' not in html_doc,
                  browser_checks_passed=False,
                  browser_check_note='本次仅校验数据、文档副本和归档；浏览器截图检查尚未重跑。')
    assert delivery['passed']
    (LOG/'delivery-verification.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


def validate(d):
    ids={r['id'] for r in d['lines']}
    assert len(ids)==len(d['lines'])==32
    known={m['id'] for m in d['catalog']}
    assert len(known)==69
    for r in d['lines']:
        assert len(r['products'])>=3 and len(r['consumers'])>=2
        assert len(r['flow'])>=4
        assert all(m in known for m in r['machines']), r['id']
        assert all(c in ids|known for c in r['consumers']), r['id']
        assert r['id'] not in r['consumers']
        assert all(r[k] for k in ['bootstrap','recycle','identity'])
    policy=d['recipe_policy']
    assert 'MAX阶段' in policy['baseline'] and '不得降低' in policy['progression']
    assert '目前已有' in policy['scope'] and len(policy['dimensions']) >= 6
    machine_ids={m['id'] for m in d['machines']}
    industrial={r['id'] for r in d['catalog'] if r['id'].startswith('I')}
    assert machine_ids==industrial,(machine_ids^industrial)
    legacy_mapping={old:[r['id'] for r in d['lines'] if old in r['legacy']] for old in [f'L{i}' for i in range(1,13)]}
    assert all(legacy_mapping.values())
    legacy_ids=[row['id'] for row in d['legacy']]
    assert legacy_ids==[f'L{i}' for i in range(1,13)]+['L13','L14']
    assert all(row['state']=='proposal' for row in d['legacy'][-2:])
    assert d['baseline']['historical_structure_catalog']==69
    assert d['baseline']['structure_minimum']==84
    assert d['baseline']['structure_conservative_target']==88
    assert all(len(m['proposed_families'])>=1 for m in d['machines'])
    assert not any(m.startswith(('I46','I47','I48','I49','I50','I51','I52','I53')) for r in d['lines'] for m in r['machines'])
    return dict(passed=True,branches=len(ids),groups=len(d['groups']),industrial_roles=len(machine_ids),
                explicit_supply_edges=sum(len(r['consumers']) for r in d['lines']),
                item_name_drafts=sum(len(g['names']) for g in d['item_drafts']),new_multiblocks=0,
                checks=['32条编号唯一且有产品/下游/首通/回收说明','历史69项目录引用均有效','48工业角色工艺族覆盖','旧L1–L12映射保留且L13/L14仍为提案','84/88结构目标口径有效','历史I46–I53未进入方案必需设备','GTL MAX基线、配方范围、逐阶难度准则已入数据'],
                limitations=['静态结构检查不证明配方物料/能量守恒、数值平衡或首通可达','数值和注册ID未冻结；不是游戏实现验收','世界泡随机目录、数量和物品等概率规则保留，不用物料循环审计擅改既定奖励'])


if __name__=='__main__':
    main()
