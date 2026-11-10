"""Beta5 physical content specification; stable IDs, bilingual names and source ownership.

Change #1, 2026-09-22: add explicit industrial intermediates and structure materials.
No research completion, HKE balance or judgment permission is represented by an item.
English labels derive deterministically from curated registry names; special lore names override them.
"""
CATALOG = []
def add(kind, source, family, rows):
    for row in rows.strip().splitlines():
        ident, zh = row.strip().split('|')
        CATALOG.append(dict(id=ident, zh=zh, en=ident.replace('_',' ').title(), kind=kind,
                            source=source, family=family))

add('item','I01/I07','detector','''
prototype_honkai_detector|试作型崩坏能探测器
liquid_honkai_detector|一阶液态崩坏能探测器
solid_honkai_detector|二阶固态崩坏能探测器
gaseous_honkai_detector|三阶气态崩坏能探测器
energy_honkai_detector|四阶能量态崩坏能探测器
''')
add('item','I02–I08','sample','''
honkai_analysis_sample|崩坏能分析样本
analyzed_honkai_sample|已分析崩坏能样本
honkai_reference_sample|崩坏能标准样本
honkai_crystal_seed|崩坏结晶晶种
directional_crystallization_matrix|定向结晶基质
separation_filter|崩坏能分离滤芯
concentrated_honkai_impurity|浓缩崩坏杂质
separation_residue|分离残渣
fuel_matrix|崩坏燃料基质
fuel_blending_residue|燃料调配尾料
''')
add('item','I09–I16','nano','''
soulium_microstructure_template|魂钢微结构模板
nano_building_unit|纳米构筑单元
unprogrammed_nanobot|未编程纳米机器人
reconstruction_rule_carrier|重构规则载体
controlled_nano_swarm|受控自组织纳米群
inactive_nano_unit|失活纳米单元
coated_nano_swarm|抗侵蚀涂层纳米群
nano_assembly_scrap|纳米装配废料
soulium_casting_mold|魂钢聚合模具
soulium_polymerization_residue|魂钢聚合残渣
soulium_data_substrate|魂钢数据基板
soulium_swarf|魂钢加工屑
''')
add('item','I18–I23/I47','rod','''
honkai_fuel_rod_casing|崩坏燃料棒壳体
fuel_encapsulation_part|燃料封装组件
rejected_fuel_rod|不合格燃料棒
depleted_honkai_fuel_rod|乏崩坏燃料棒
depleted_dense_honkai_fuel_rod|乏浓缩崩坏燃料棒
broken_honkai_fuel_rod|破损崩坏燃料棒
broken_dense_honkai_fuel_rod|破损浓缩崩坏燃料棒
recovered_fuel_casing_material|回收燃料壳体材料
inactive_fuel_residue|失活燃料残渣
''')
add('item','I24–I32/I51/I53','bubble','''
spatial_probe|空间观测探针
unmanned_resource_probe|无人资源探测器
industrial_work_drone|工业作业无人机
worn_resource_probe|磨损的资源探测器
worn_work_drone|磨损的作业无人机
drone_disassembly_scrap|无人设备拆解废料
empty_bubble_containment_vessel|空世界泡收容容器
sealed_real_world_bubble|封存的真实世界泡
unstable_simulated_world_bubble|不稳定模拟世界泡
stable_simulated_world_bubble|稳定模拟世界泡
world_model_carrier|世界模型载体
world_matter_seed|世界物质种子
bubble_termination_charge|世界泡终止组件
bubble_container_remnant|世界泡容器残件
failed_containment_shell|不合格收容壳体
reverse_engineering_specimen|逆向工程复现样本
failed_engineering_specimen|失败工程样本
''')
add('item','I34–I45','component','''
soulium_anchor_component|魂钢锚定组件
spatial_calibration_module|空间校准模块
world_maintenance_specimen|世界维系工程样本
conducting_composite|高维导能复合材料
confining_composite|高维约束复合材料
reconstructing_composite|高维重构复合材料
cognitive_composite|高维认知复合材料
composite_offcut|高维复合材料边角料
polarized_electromagnetic_material|极化电磁材料
cryogenic_condensed_material|深冷凝聚材料
extreme_casting_material|极限铸造材料
civilization_singularity|文明工程奇点
''')
add('item','I48–I50/I52','circuit','''
honkai_adapted_circuit_substrate|崩坏能适配电路基板
defective_circuit_substrate|不合格电路基板
circuit_lithography_mask|电路光刻掩膜
etched_circuit_layer|已蚀刻电路层
failed_circuit_layer|不合格电路层
circuit_encapsulation_part|电路封装组件
rejected_circuit_package|不合格电路封装
process_gas_filter|工艺气体滤芯
depleted_gas_filter|失效工艺气体滤芯
process_gas_impurity|工艺气体杂质
''')
add('item','H01','ship','''
imitation_hyperion_blueprint|仿制休伯利安蓝图
hyperion_keel_segment|仿制休伯利安龙骨段
hyperion_thruster_assembly|仿制休伯利安推进器组件
hyperion_navigation_module|仿制休伯利安导航模块
hyperion_bridge_module|仿制休伯利安舰桥模块
''')
CORES=[('flame','炎'),('ice','冰'),('reason','理'),('void','空'),('corruption','侵蚀'),('rock','岩'),('binding','约束'),('thunder','雷'),('wind','风')]
for ident,zh in CORES:
    add('item','I08/I33','crystal',f'unencapsulated_{ident}_core|未封装仿制{zh}之律者核心')
    if ident != 'reason': add('item','I33','core',f'imitation_{ident}_core|仿制{zh}之律者核心')
add('item','I33/RN divine keys','key','''
imitation_void_archives|仿制的虚空万藏
imitation_cosmic_juggernaut|仿制的千界一乘
imitation_star_of_eden|仿制的伊甸之星
imitation_oath_of_judah|仿制的犹大的誓约
divine_key_housing|神之键封装框架
''')
add('fluid','I03–I06/I09–I18','liquid','''
crude_honkai_energy|粗制液态崩坏能
honkai_mother_liquor|含能母液
stabilized_liquid_honkai_energy|稳定液态崩坏能
honkai_separation_medium|崩坏能分离介质
honkai_stabilization_medium|崩坏能稳定介质
spent_honkai_stabilization_medium|废稳定介质
spent_analysis_reagent|废分析试剂
honkai_analysis_reagent|崩坏能分析试剂
unrecoverable_process_effluent|不可再生工艺废液
liquid_honkai_fuel|液态崩坏燃料
concentrated_liquid_honkai_fuel|浓缩液态崩坏燃料
fuel_refining_residual|燃料精炼残液
crystallization_residual_liquid|结晶残液
soulium_precursor_fluid|魂钢前驱液
soulium_process_solvent|魂钢工艺溶剂
spent_soulium_solvent|废魂钢溶剂
nano_reaction_tail_liquid|纳米反应尾液
honkai_resistant_coating|抗崩坏侵蚀涂层液
spent_resistant_coating|废抗侵蚀涂层液
''')
add('fluid','I23/I52','gas','''
gaseous_honkai_energy|气态崩坏能
soulium_protective_gas|魂钢保护气体
spent_soulium_process_gas|废魂钢工艺气体
hot_soulium_exhaust|魂钢热尾气
''')
add('fluid','I27–I53','liquid','''
bubble_confinement_medium|世界泡约束介质
world_stabilization_medium|世界稳定介质
spent_world_stabilization_medium|废世界稳定介质
honkai_coolant|崩坏工业冷却液
hot_honkai_coolant|高温崩坏工业冷却液
lost_coolant_residue|劣化冷却液
fuel_waste_processing_fluid|乏燃料处理废液
circuit_growth_medium|电路生长介质
spent_circuit_growth_medium|废电路生长介质
honkai_circuit_etchant|崩坏电路蚀刻液
spent_honkai_etchant|废崩坏电路蚀刻液
stable_transport_medium|稳定输运介质
''')
add('block','I01–I53/S01–S05','casing','''
honkai_collection_casing|崩坏能采集机壳
honkai_separation_casing|崩坏能分离机壳
honkai_stabilization_casing|崩坏能稳定机壳
soulium_chemical_casing|魂钢化工机壳
nano_assembly_casing|纳米装配机壳
honkai_fuel_processing_casing|崩坏燃料处理机壳
small_honkai_reactor_vessel|小型崩坏反应堆压力壳
medium_honkai_reactor_vessel|中型崩坏反应堆压力壳
large_honkai_reactor_vessel|大型崩坏反应堆压力壳
ultimate_honkai_reactor_vessel|终极崩坏反应堆压力壳
quantum_observation_casing|量子观测机壳
world_bubble_containment_casing|世界泡收容机壳
world_simulation_casing|世界模拟机壳
imaginary_anchor_casing|虚数锚定机壳
high_dimensional_assembly_casing|高维装配机壳
precision_circuit_casing|精密电路机壳
research_institute_casing|崩坏研究所机壳
advanced_research_casing|高阶崩坏研究所机壳
quantum_research_casing|量子研究所机壳
imaginary_research_casing|虚数研究所机壳
civilization_cognition_casing|文明认知穹顶机壳
''')
add('block','I01–I53/H01','structure','''
honkai_collection_antenna|崩坏能采集天线组件
spectral_analysis_lens|频谱分析透镜组件
nano_reconstruction_chamber|纳米重构腔体
honkai_heat_exchanger|崩坏工业换热组件
quantum_confinement_coil|量子约束线圈
imaginary_anchor_ring|虚数锚定环组件
high_dimensional_energy_conduit|高维导能构件
civilization_computing_array|文明计算阵列
hyperion_armored_hull|仿制休伯利安装甲舰壳
hyperion_structural_frame|仿制休伯利安结构框架
hyperion_engine_nozzle|仿制休伯利安引擎喷口
hyperion_bridge_panel|仿制休伯利安舰桥面板
''')
WONDERS=[('origin','始源'),('reason','理'),('void','空'),('thunder','雷'),('wind','风'),('ice','冰'),('death','死'),('flame','炎'),('sentience','识'),('rock','岩'),('domination','支配'),('binding','约束'),('corruption','侵蚀'),('finality','终焉'),('tree_sea','树海')]
for n,(ident,zh) in enumerate(WONDERS,1):
    for part,label in [('casing','奇观外壳'),('support','奇观支撑'),('interface','奇观接口'),('core_mount','奇观核心座')]:
        add('block',f'W{n:02}/I42','wonder',f'wonder_{ident}_{part}|{zh}·{label}')

# Already registered physical objects retain IDs and behavior; art is upgraded separately.
REUSE = [('liquid_honkai_energy','fluid','液态崩坏能','I01'),
         ('honkai_energy_crystal','item','固态崩坏能结晶','I01/I23'),
         ('imitation_reason_core','item','仿制理之律者核心','I33'),
         ('honkai_fuel_rod','item','崩坏燃料棒','I18'),
         ('dense_honkai_fuel_rod','item','浓缩崩坏燃料棒','I18'),
         ('soulium_proto_mass','item','粗魂钢坯','I14'),
         ('stabilized_soulium_proto_mass','item','稳定魂钢坯','I15'),
         ('narrative_codex','item','文明档案卷轴','Narrative')]
for ident,kind,zh,source in REUSE:
    add(kind,source,'liquid' if kind=='fluid' else 'core' if 'core' in ident else 'rod' if 'rod' in ident else 'sample',f'{ident}|{zh}')
    CATALOG[-1]['reuse']=True
assert len({r['id'] for r in CATALOG})==len(CATALOG)

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
