# -*- coding: utf-8 -*-
"""按69座总表编制逐机建筑草案，写入现有机器文档，不产生或替换正式Pattern。
变更#1 2026-09-28：新增功能驱动的轮廓、分区、检修和材质草案；旧记录保留。
"""
from pathlib import Path
import json,re,html,datetime,hashlib
from structure_size_baseline import ROOT,baselines,SOURCE

# 每行：机器编号、构图、设备区、实际连接表达。名称与尺寸只从总表读取。
BRIEFS='''I01-1|竖向采集桅杆与低位冷凝肩舱|采集头、下降干管、冷凝腔、原液出口、仪表座|集流头经竖直干管落入侧置冷凝腔，检修道从另一侧绕柱到达仪表座
I01-2|四瓣收集翼包围低位固化仓|捕集翼、沉降腔、固化仓、颗粒出口、制冷组|捕集翼汇向沉降腔，封闭固化仓与颗粒出口串接，冷却管沿外缘返回
I01-3|双高塔与横向集气桥|集气塔、缓冲罐、气液分离器、回流管、压送组|桥架送气至低位缓冲罐，分离液单独回流，不与成品气出口混用视觉干线
I01-4|四向斜撑场架与悬高采集核|收束臂、约束核、能流转换组、冷却脊、隔离廊|四臂共同约束上部核心，能流沿独立支撑脊落入底部转换组
I02|折线光路实验廊与侧置样品室|样品入口、光谱腔、基准源、记录柜、隔离冷却|样品室与光谱腔相邻；基准源沿封闭光路面对检测端，检修道沿光路外侧
I03|双离心鼓加独立低位回流架|初分离鼓、细分离鼓、滤芯架、母液汇流槽、残渣箱|原液串联两鼓，母液从独立外侧干管返回入口，残渣在相反侧收集
I04|分段稳定柱与三面冷却夹套|进液缓冲、稳定段、约束段、成品冷却、介质返回|液路按高度逐段连接；底部架空穿行，检修入口通向各段外侧维护座
I05|高再生塔与矮除杂塔组成阶梯轮廓|废介质入口、除杂段、再生段、母液出口、废液处理|废液与可回收母液分开出塔，再生干管只返回成品侧，走廊沿两塔间隙
I06|低位配料阵列与高位混合釜|组分储槽、计量架、混合釜、均化罐、检测台|各组分先到计量架再进入主釜，均化罐位于下游，不用整片线圈代替化工设备
I07|双屏蔽测试室与横向标定轨道|标准件座、待校准座、信号源、读出柜、屏蔽层|标准与待测位置共享明确测试轴，读出柜从侧方接入，前台接口不散到背面
I08|内外双层结晶舱及非对称冷却臂|原料准备、结晶舱、核心定位座、冷却组、取样座|核心处于独立定位结构内，供料与取样分开，冷却组连至夹套而非随意伸向空中
I09|并列配液小釜与中央反应大釜|前驱配液、定量混合、反应主釜、过滤座、样品柜|低位配液管汇到中央釜，过滤后再输出；仪表面朝连续服务走道
I10|分层微反应架与封闭合成脊|前驱入口、反应阵列、洗涤柱、筛分组、产物仓|微反应组按模块串联，洗涤与筛分在后场，不做一个空的大箱子
I11|双线装配床跨接上部校验桥|基元供料、装配床、操作构件、检测桥、废件回收|两线在检测桥汇合，返修通道回到装配入口，外沿设置独立维护带
I12|多座隔离编程舱围绕数据脊|样品缓冲、编程舱、隔离屏蔽、计算阵列、记录端|编程舱各接数据脊和供能底座，人员绕外缘进入维护位，不穿过样品区域
I13|贯通式包覆隧道与侧面循环槽|前处理、包覆腔、介质循环、固化段、终检|工作轴连续，循环槽沿侧面返回包覆腔，固化及终检位于尾端
I14|门式压铸梁架与偏置热料炉|热料准备、计量浇注、压铸床、冷却台、余料回收|料从偏置炉进入压床，成品沿纵轴送冷却，余料回路位于独立一侧
I15|三段长向退火廊与交错排热翼|预热段、重构段、保温段、缓冷段、返料座|长度用于连续热工分区，侧面排热构件直接服务对应热段
I16|并列加工床与后置计量塔|坯料入口、粗加工、精加工、尺寸检测、切屑回收|主材沿床身移动，切屑沿低位槽汇集；高计量塔对准检测工位
I17|窄高精馏柱群与低位浓缩仓|粗料缓冲、精馏柱、冷凝头、浓缩仓、尾液罐|上部冷凝回流到柱顶，浓缩产物从低位独立输出，不把尾液当成品线
I18|长向封装洁净廊与侧置检测舱|棒壳进料、灌装段、密封段、隔离检测、成品架|四段前后连续；试验与正式生产语义不靠建筑外观擅自更改
I19|低矮屏蔽堆室与单侧冷却组|燃料缓冲、反应室、换热器、控制屏蔽、废料端|反应室四周保留可解释的隔离距离，换热器外接一组冷却模块
I20|双换热翼夹中央堆室|燃料区、堆芯室、双换热器、冷却环路、废料隔离|两侧换热器各接独立闭合冷却回路，前端控制区与后部废料区分离
I21|多层屏蔽主堆与四座换热塔|堆芯、内屏蔽层、外换热塔、能源汇流、维护环廊|换热塔通过有厚度的屏蔽干线连接主堆，环廊穿行塔间而不截断屏蔽壳
I22|分区反应园区与中央多层堆殿|主堆、分区换热场、冗余供能、隔离废料场、控制前庭|核心集中，换热及废料外围分区；大尺度来自工艺组织，不填实整个包围盒
I23|错层相变舱与双端换热栈|输入缓冲、相变室、约束座、释能换热、残余回收|工质穿过高位相变室进入后端换热，残余物沿侧管回到回收座
I24|长基线观测臂与偏置处理楼|前端观测站、远端观测站、基线桥、数据厅、屏蔽供能|长度用于分离观测端点，数据厅不挡观测轴，维护路沿臂下方
I25|折叠坐标阵列与侧向计算柜墙|输入档案、坐标解析核、校核阵列、缓存厅、输出端|输入与校核两条数据脊在解析核相交，设备中间留真实维护通路
I26|前后双港区与侧置调度塔|出港整备、任务调度、返港隔离、资源卸载、装置维修|出港和返港分开，维修支路接回整备区；真实任务记账不由建筑代替实现
I27|三轴捕获门框与周边锚固阵列|定位站、捕获场、锚固臂、转移廊、隔离回收座|留白是捕获场体积，四周锚臂连接外围动力组；门框不复刻研究所圆环
I28|楔形终止室与两条下游回收槽|真实目标接入、终止隔离室、能量回收、物质回收、残余封存|两类回收从隔离室不同侧引出，检修路不穿越终止核心
I29|分层模拟阵列与中央构筑仓|模型输入、计算阵列、构筑仓、约束层、批次记录端|计算阵列环绕构筑仓但分层错开，模拟批次与真实目标不共用视觉入口
I30|双向稳定梁夹长条控制仓|模拟泡输入、相位校准、稳定梁、读出阵列、维护夹层|左右稳定梁各接校准座，维护夹层位于梁外，不要求穿过泡体区域
I31|并行模拟回收槽与后端分拣楼|批次核验、模拟终止、分流槽、资源分拣、残余出口|核验位在终止前，产物流向后场分拣；模拟与真实终止形体明确区分
I32|前低样品厅与后高档案实验楼|档案接收、拆解试验、成像分析、复现工作台、图纸归档|实物样件和资料分路进入分析厅，在复现工位汇合，服务廊通向各实验间
I33|细长装配厅与分叉检测翼|框架装配、核心安置、约束调试、效能检测、隔离存放|装配轴直达核心安置，检测翼侧向展开；各功能不靠同一种机壳填满
I34|多座高低观测架围绕资料塔|观测端点、信号干线、中央记录塔、校准庭、供能站|高观测架视线朝向中心上部，低位连廊连接资料塔和校准设备
I35|四向锚脚与低位交叉稳定台|四向锚座、中心参考点、反馈阵列、动力侧厅、外环检修|锚脚向四方延伸至外缘，各接反馈阵列；非同心圆环套塔
I36|分叉稳定桅杆与厚底承载座|局部参考源、稳定主柱、校准支臂、散热底座、诊断座|主柱与支臂有连续受力连接，散热底座呈机械肋片，不做装饰细针
I37|两块隔离试验场与中部观测桥|样件场、负载场、观测桥、介质循环、故障隔离间|中桥架空连接两场，场内空区有负载试验用途，检修通道沿场边
I38|高位整流栈与低位分配母线|输入调理、整流栈、平滑阵列、分配母线、热交换|整流段按高度分层，能流落到两侧母线；控制前庭隔开能流核心
I39|双收发桅杆与前后无人装置港|信标校核、发射准备、收发塔、返航区、维修库|收发塔由横桥连接，返航与发射低位分区，维护库与返航相邻
I40|四种复合材料工段围绕共享质检廊|配料、复合烧结、核心嵌入、四类材料暂存、共同质检|每类材料分支有独立工位，质检共享但不把四条支线画成同一根管
I41|两侧仓储岛与中央交换厅|货物暂存、订单检验、交换台、回执柜、缓冲物流|入站与出站仓储在两翼，交换厅连通两侧但保留独立检验步骤
I42|多工位预制床与架空装配横梁|材料准备、构件预制、装配床、尺寸校验、成品转运|长向连续工位，横梁跨越装配床，检修从设备外侧到各驱动座
I43|三个隔离试验舱面对公共证据厅|工程样件入口、负载试验、稳定试验、故障检查、证据归档|试验舱与记录厅连通而保持隔离，不能以建筑命名新增终审功能
I44|分段信标主柱与四角定位塔|坐标库、锁定主柱、定位辅塔、能量调理、检修台|四角定位塔接到底部坐标库，主柱各段有实质支撑，不堆同尺寸环
I45|细长列车舰体与侧向检修站台|前端导航、动力舱、观测舱、维护连接、尾端约束|列车长轴遵循总表，不变成方盒；主控设正面中轴，保留侧向可辨识舱段
S01|错层单仪器实验室与独立记录壁|样品暂存、单工作位、记录柜、供能冷却、维护后廊|一工作位体现单槽规模，研究内容不限定为某学科，人员通道面向设备维护面
S02|双实验翼围合开口中庭|样品准备、左实验翼、右实验翼、共享记录脊、冷却庭|两工作位分别接共享记录脊，中央通道通到后侧维护庭；取消大箱体加两根柱的主构图
S03|四个错位仪器厅与架空数据廊|统一收样、四工作位、资料中庭、计算夹层、散热侧厅|四工作位独立但经数据廊连接，不使用两道大圆环充当整个研究所
S04|八工作位分层研究院与独立设备庭|样品分发、八工作位、交叉资料廊、能源调理、维护庭|八工作位分两层四翼，桥廊连接共享记录区；高部为计算与冷却楼，不是任意加高塔尖
S05|完整分瓣穹顶覆盖十六工作位与资料中枢|分级收样、十六工作位、中央资料厅、环形计算层、外围冷却庭|十六工作位分四组，穹顶有厚度与分瓣表面；环廊服务实际实验间，取消空穹顶骨架包围稀疏箱体
W01|群星观测庭与向心协奏台|迎宾轴、协奏核、群星记录座、能流廊、外围观测区|中心与星状端点经有序曲折走廊相连，星庭留白对应观测与仪式用途
W02|六座自治工厂围合中央调度矩阵|原料中转、六组工厂、共享算力厅、成品调度、维护外环|工厂群之间连接物流与数据干线，重复模块有不同工段职责，不是放大单厂
W03|内外错位锚定环与四座空间门楼|定位门楼、内锚环、外锚环、虚数调理、观测回廊|双环高度与切面不同，四臂承接锚定节点，中心是被约束的空间，不塞普通高塔
W04|对峙双电极山与中央放电峡谷|供能场、电极塔群、放电区、能流整形、屏蔽观察廊|两侧电极构成明显对向关系，峡谷留白服务放电；外侧回流支撑连续
W05|双层流道绕中央整流岛|进流调理、双环流道、中心整流、分流端、回流泵阵|高低流道有明确回路，弯道采用整块机壳阶梯转折，不用细管线冒充主体
W06|阶梯冷凝山与前场密封凝态室|预冷、深冷阵列、凝态室、热端回收、冷媒回路|冷端与热端两侧分离，分层设备呈退台，寒冷材质集中于冷端
W07|舟形再生主体与两翼物质工坊|分解舱、再生舱、物质重组、生命记录、侧翼回收|长轴舟体串接物质过程，两翼回收供主舱；不直接复制休伯利安舰体
W08|厚壁恒星炉与分区熔铸台|中心炉、约束承载、熔铸台、热能回收、材料前庭|炉体有屏蔽层厚度，四向熔铸台接主炉，开口服务热工而非装饰缺口
W09|开放共识中庭与多列知识长厅|文明记录、共识中庭、知识网络、检索翼、维护脊|长厅围合公共中庭，按知识网络横向铺开；与S05研究穹顶保持身份区别
W10|深井式铸造口与同轴重力承台|入料平台、井口约束、竖向铸造、取件层、外围动力|竖向井道决定高差，外层支撑为井壁服务；本地零点起建，不暗中挖出包围盒外
W11|分布式工业节点城与低位调度网|节点厂区、调度网、同步中心、物资中转、分区维护|多个不同大小节点由低位廊网连接，不再以中心高塔统治全部构图
W12|长向双约束壁夹中央试验域|端部门廊、长约束壁、分段供能、中央受约束场、外侧检修|长度用于真正连续且分段供能的壁体，中央空场有明确用途，不堆满方块
W13|交错演算实验翼与封闭样本回廊|样本隔离、演算翼、回收廊、控制中枢、可替换模块座|实验翼有可辨识模块边界，回收廊闭合连通，外围通路不贯穿危险样本舱
W14|前后双循环核心与交叉回收桥|世界泡接入、循环核、回收核、轮回桥、审判门廊|循环与回收核心体量相当、功能不同，交叉桥形成明显方向，不复制捕获阵列
W15|递进式朝觐轴与层层树海圣座|前庭、文明记录廊、审判门、中央圣座、四域外庭|逐级门庭通向圣座，四域外庭有记录与观测用途；尊重既有叙事，不凭建筑新增审判时机
H01|保留既有旗舰轮廓并重审舱段组织|舰桥、动力舱、观测甲板、工程舱、舰载接口|先核对既有舰体坐标和可复用材质，再设计外观与舱段更新；不把原舰抹掉换成通用飞船
'''

PALETTES={
 'process':['gtceu:corrosion_proof_casing','gtceu:tungstensteel_pipe_casing','gtceu:filter_casing','gtlcore:oxidation_resistant_hastelloy_n_mechanical_casing','gtlcore:process_machine_casing','gtlcore:cooler[active=false]'],
 'precision':['gtceu:advanced_computer_casing','gtceu:assembly_line_casing','gtlcore:multi_functional_casing','gtlcore:manipulator','gtlcore:advanced_assembly_line_unit[active=false]','gtlcore:hsss_reinforced_borosilicate_glass'],
 'energy':['gtceu:high_power_casing','gtceu:fusion_coil[active=false]','gtlcore:stellar_containment_casing','gtlcore:power_module[active=false]','gtlcore:rhenium_reinforced_energy_glass','kubejs:titansteel_coil_block[active=false]'],
 'space':['gtlcore:dimension_connection_casing','gtlcore:dimension_injection_casing','gtlcore:dimensionally_transcendent_casing','gtlcore:graviton_field_constraint_casing','gtlcore:infinity_glass','kubejs:eternity_coil_block[active=false]'],
 'research':['gtceu:advanced_computer_casing','gtlcore:law_filter_casing','gtlcore:multi_functional_casing','gtlcore:echo_casing','gtlcore:super_computation_component[active=false]','gtlcore:super_cooler_component[active=false]'],
}

def main():
    now=datetime.datetime.now().astimezone().isoformat();rows=baselines()
    material_data=json.loads((ROOT/'logs/research-labs-preview-20260928/material-expansion/catalog.json').read_text(encoding='utf-8'))
    available={x['state']:x for x in material_data['accepted']}
    catalog=[]
    for line in BRIEFS.strip().splitlines():
        key,form,zones,flow=line.split('|');base=rows[key]
        if key.startswith('S'):family='research'
        elif key.startswith(('W','H')):family='space'
        else:
            n=int(key[1:].split('-')[0]);family='process' if n<=6 or n in (9,13,15,17,18) else 'precision' if n in (7,8,10,11,12,14,16,32,33,40,41,42,43) else 'energy' if n<=23 or n==38 else 'space'
        palette=PALETTES[family]
        assert all(s in available and available[s]['dual_static'] for s in palette),palette
        title=base['name'] if not key.startswith('S') or key=='S05' else '研究所·第'+{'S01':'一','S02':'二','S03':'三','S04':'四'}[key]+'阶（正式名称待定）'
        catalog.append({'id':key,'title':title,'minimum_wdh':base['size'],'form':form,'zones':zones.split('、'),'flow':flow,'family':family,'material_candidates':palette,'status':'建筑概念草案，未生成逐格结构、未审批'})
    assert len(catalog)==69 and {r['id'] for r in catalog}==set(rows)
    # 只提取显式注册及已知包装器调用；无法静态匹配的入口单列，不误删。
    known={'i01_honkai_collection_tower':'I01-1','i02_spectrum_analysis_array':'I02','liquid_honkai_fractionation_center':'I03','liquid_honkai_stabilization_tower':'I04','stabilization_medium_regeneration_tower':'I05','honkai_fuel_blending_plant':'I06','honkai_detector_calibration_bench':'I07','honkai_fuel_concentration_plant':'I17','abyss_research_analysis_matrix':'S01','hyperion_flagship':'H01'}
    legacy={'honkai_absorption_tower','honkai_crystal_condenser'}
    entries=[]
    for file in sorted((ROOT/'src/main/java/com/sirin/hk3gtl').rglob('*.java')):
        text=file.read_text(encoding='utf-8')
        for m in re.finditer(r'(?:\.multiblock|\bliquidMachine)\(\s*"([a-z0-9_]+)"',text):
            key=m[1];entries.append({'id':key,'file':str(file.relative_to(ROOT)),'line':text.count('\n',0,m.start())+1,'mapped':known.get(key),'status':'已明确旧入口，表外去留待定' if key in legacy else '已有直接对应' if key in known else '语义或调用关系待匹配，不据此认定表外或废弃'})
    out=ROOT/'logs/structure-redesign-20260928';out.mkdir(exist_ok=True)
    report={'time':now,'source':str(SOURCE.relative_to(ROOT)),'baseline_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'briefs':catalog,'registration_inventory':entries,'limits':['只有建筑概念草案，不是逐格蓝图或真实材质三维预览','显式调用静态扫描不是完整运行注册表','材质候选为静态模型检查，不代表动态渲染、碰撞或游戏成型']}
    (out/'briefs69.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    # 加入现有设计文档，不新建另一套目录或操作指南。
    doc=ROOT/'doc/HK3GTL-内测5/03_机器结构/机器与文明级奇观.html'
    content=doc.read_text(encoding='utf-8');assert 'id="redesign69-20260928"' not in content,'已存在该轮草案，必须追加变更而非覆盖'
    body=f'<section id="redesign69-20260928"><h2>69座建筑重设计 · 功能与构图草案</h2><p>{html.escape(now)}。范围已确认，以下造型是助手本轮提案，未获得逐台建筑审批。尺寸采用总表下限，尚非已生成结构的实测尺寸。S01–S04名称未定。</p><p>先按用途区分主体、辅助设施、连接与维护空间，再逐台生成真实材质结构。这里没有把69条文字当成69座已完成建筑。</p><label>查找机器 <input id="redesign-search" placeholder="编号、名称、工艺" style="padding:10px"></label><p>材质样片来自实际实例原图，仅表示候选用途；共同白色地板、接口白框与主控标记不重复列入各组。</p>'
    for r in catalog:
        mats=''.join('<span style="display:inline-block;width:165px;vertical-align:top;font-size:11px;overflow-wrap:anywhere;margin:5px"><img style="width:52px;height:52px;image-rendering:pixelated" src="'+available[s]['material']['faces']['north']+'"><br>'+html.escape(s)+'</span>' for s in r['material_candidates'])
        body+=f'<details class="redesign-item" style="padding:12px;border-bottom:1px solid #405169"><summary>{r["id"]} · {html.escape(r["title"])} · 下限 {"×".join(map(str,r["minimum_wdh"]))}（宽×长×高）</summary><p><strong>主体构图：</strong>{r["form"]}</p><p><strong>设备分区：</strong>{" → ".join(r["zones"])}</p><p><strong>连接与维护：</strong>{r["flow"]}。</p><div>{mats}</div><p>下一阶段检查：主体与空区用途、逐格尺寸、材料与纹理协调、真实维护路径、前侧白框接口及主控中轴、导出一致性。不得用以上概念描述冒充实际结构检查。</p></details>'
    body+='<h3>旧多方块注册入口清单：不自动决定去留</h3><p>下列未直接匹配的条目包括语义近似项，不是全部表外机器。仅两个明确旧入口先列为表外待定；其余继续核对对应关系。未删除或归档任何文件。</p>'
    for e in entries:
        body+='<details><summary>'+html.escape(e['id'])+' · '+html.escape(e['mapped'] or e['status'])+'</summary><p>'+html.escape(e['file'])+':'+str(e['line'])+'</p></details>'
    body+='<p><a href="../../../logs/structure-redesign-20260928/briefs69.json">本轮结构化草案与注册清单</a> · <a href="../讨论记录/2026-09-28_03-10-00_按巨构提示词重设计69座结构.html">范围确认记录</a></p><p>变更记录#重设计1：新增本节，不修改原历史正文，不生成或替换正式结构。</p></section><script>document.getElementById("redesign-search").addEventListener("input",e=>{const q=e.target.value.toLowerCase();document.querySelectorAll(".redesign-item").forEach(d=>d.hidden=!d.textContent.toLowerCase().includes(q));});</script>'
    content=content.replace('<h2>设计方向</h2>',body+'<h2>设计方向</h2>',1)
    assert 'id="redesign69-20260928"' in content
    (out/'机器与文明级奇观_追加前.html').write_bytes(doc.read_bytes())
    doc.write_text(content,encoding='utf-8')
    print(json.dumps({'briefs':len(catalog),'explicit_registrations':len(entries),'known_mappings':sum(bool(e['mapped']) for e in entries),'known_legacy':sum(e['id'] in legacy for e in entries),'document':str(doc)},ensure_ascii=False))
if __name__=='__main__':main()
