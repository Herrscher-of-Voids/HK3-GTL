package com.sirin.hk3gtl.common.registration;



import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.block.Hk3Blocks;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:37:18（内测5修订66）
 * 删除：无。新增：探测器校准报告物品。修改：报告使用独立模型与中文名称。
 * 用途：校准和探测器升级之间使用可见物品衔接，不改变采集催化剂规则。
 */
/**
 * 【变更记录 #2】2026-09-27 01:54:24（第 2 次备注 · 内测5修订86）
 * 删除：无，保留全部历史注册与工艺。
 * 新增：独立封装试验样件物品，仅用于破坏性隔离检测。
 * 修改：接入负责人确认的棒壳、封装样件与I02检测路线。
 * 用途：补齐RN-FRP实验入口，不注册I18，不跳过研究支付或前置。
 */
/**
 * 【变更记录 #3】2026-09-27 03:05:48（第 3 次备注 · 内测5修订88）
 * 删除：无，保留历史注册。新增：工业接口机械方块及对应物品，沿既有创造页分类收录。
 * 修改：注册普通完整金属方块，六面模型直接引用现有控制器侧面材质。
 * 用途：填充多方块空余接口；自身不提供物品、流体、供能或并行能力。
 */
/**
 * 【变更记录 #4】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：注册检测专用样件及任务资料物品；持有这些物品不能完成课题。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #5】2026-10-01 21:51:39（第5次备注 · 内测5修订152）
 * 删除：无。新增：16档电压配色机械机壳。
 * 修改：沿既有方块注册和创造栏收集入口添加完整立方体机壳。
 * 用途：提供独立建筑材料，不授予电压能力或研究进度，不修改既有结构。
 */
/**
 * 【变更记录 #6】2026-10-20 03:47:24（第6次备注 · 修订174）
 * 删除：无，保留既有物品注册与顺序。
 * 新增：注册13种已批准的能源载体物品，供后续燃料工艺引用；既有创造页会自动收录未分类物品。
 * 修改：未增加配方、方块、机器能力或多方块结构；燃料棒与乏燃料贴图不属于本次资源替换范围。
 * 用途：建立能源工艺所需的载体物品身份，实际制造路线仍由后续配方接入。
 */
public final class Hk3IndustrialContent {
    // 注册线程写入，完成后只读；保持目录顺序，不允许调用方修改。
    // 中文备注：该处说明已按当前代码行为整理。
    private static final Map<String, RegistryObject<Item>> ITEMS = new LinkedHashMap<>();
    private static final Map<String, RegistryObject<Block>> BLOCKS = new LinkedHashMap<>();
    private Hk3IndustrialContent() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static void registerItems() {
        item("world_mining_legacy_record",64);
        item("ship_engineering_archive",64);
        for(var contract:com.sirin.hk3gtl.common.research.Hk3ResearchExecutionContracts.all().values())
            if(!contract.existing())item(contract.specimen(),64);
        item("honkai_detector_calibration_report", 64); // 探测器真实校准的纸质报告，升级时消耗。
        item("prototype_honkai_detector", 1); // 试作型崩坏能探测器 / Prototype Honkai Detector; I01/I07
        item("liquid_honkai_detector", 1); // 一阶液态崩坏能探测器 / Liquid Honkai Detector; I01/I07
        item("solid_honkai_detector", 1); // 二阶固态崩坏能探测器 / Solid Honkai Detector; I01/I07
        item("gaseous_honkai_detector", 1); // 三阶气态崩坏能探测器 / Gaseous Honkai Detector; I01/I07
        item("energy_honkai_detector", 1); // 四阶能量态崩坏能探测器 / Energy Honkai Detector; I01/I07
        item("honkai_analysis_sample", 64); // 崩坏能分析样本 / Honkai Analysis Sample; I02–I08
        item("analyzed_honkai_sample", 64); // 已分析崩坏能样本 / Analyzed Honkai Sample; I02–I08
        item("honkai_reference_sample", 64); // 崩坏能标准样本 / Honkai Reference Sample; I02–I08
        item("honkai_crystal_seed", 64); // 崩坏结晶晶种 / Honkai Crystal Seed; I02–I08
        item("directional_crystallization_matrix", 64); // 定向结晶基质 / Directional Crystallization Matrix; I02–I08
        item("separation_filter", 64); // 崩坏能分离滤芯 / Separation Filter; I02–I08
        item("concentrated_honkai_impurity", 64); // 浓缩崩坏杂质 / Concentrated Honkai Impurity; I02–I08
        item("separation_residue", 64); // 分离残渣 / Separation Residue; I02–I08
        item("fuel_matrix", 64); // 崩坏燃料基质 / Fuel Matrix; I02–I08
        item("fuel_blending_residue", 64); // 燃料调配尾料 / Fuel Blending Residue; I02–I08
        item("honkai_carbon_carrier", 64);
        item("honkai_zeolite_carrier", 64);
        item("honkai_silica_gel_carrier", 64);
        item("honkai_silicon_carbide_carrier", 64);
        item("honkai_boron_carbide_carrier", 64);
        item("honkai_zirconia_carrier", 64);
        item("honkai_diamond_copper_carrier", 64);
        item("honkai_graphene_carrier", 64);
        item("honkai_titanium_carbide_carrier", 64);
        item("honkai_alumina_carrier", 64);
        item("honkai_tungsten_carrier", 64);
        item("honkai_ptfe_membrane_carrier", 64);
        item("honkai_pbi_microcapsule_carrier", 64);
        item("soulium_microstructure_template", 64); // 魂钢微结构模板 / Soulium Microstructure Template; I09–I16
        item("nano_building_unit", 64); // 纳米构筑单元 / Nano Building Unit; I09–I16
        item("unprogrammed_nanobot", 64); // 未编程纳米机器人 / Unprogrammed Nanobot; I09–I16
        item("reconstruction_rule_carrier", 64); // 重构规则载体 / Reconstruction Rule Carrier; I09–I16
        item("controlled_nano_swarm", 64); // 受控自组织纳米群 / Controlled Nano Swarm; I09–I16
        item("inactive_nano_unit", 64); // 失活纳米单元 / Inactive Nano Unit; I09–I16
        item("coated_nano_swarm", 64); // 抗侵蚀涂层纳米群 / Coated Nano Swarm; I09–I16
        item("nano_assembly_scrap", 64); // 纳米装配废料 / Nano Assembly Scrap; I09–I16
        item("soulium_casting_mold", 64); // 魂钢聚合模具 / Soulium Casting Mold; I09–I16
        item("soulium_polymerization_residue", 64); // 魂钢聚合残渣 / Soulium Polymerization Residue; I09–I16
        item("soulium_data_substrate", 64); // 魂钢数据基板 / Soulium Data Substrate; I09–I16
        item("soulium_swarf", 64); // 魂钢加工屑 / Soulium Swarf; I09–I16
        item("honkai_fuel_rod_casing", 64); // 崩坏燃料棒壳体 / Honkai Fuel Rod Casing; I18–I23/I47
        item("fuel_encapsulation_test_specimen", 64); // 仅供实验，不属于发电燃料棒标签。
        item("fuel_encapsulation_part", 64); // 燃料封装组件 / Fuel Encapsulation Part; I18–I23/I47
        item("rejected_fuel_rod", 64); // 不合格燃料棒 / Rejected Fuel Rod; I18–I23/I47
        item("depleted_honkai_fuel_rod", 64); // 乏崩坏燃料棒 / Depleted Honkai Fuel Rod; I18–I23/I47
        item("depleted_dense_honkai_fuel_rod", 64); // 乏浓缩崩坏燃料棒 / Depleted Dense Honkai Fuel Rod; I18–I23/I47
        item("broken_honkai_fuel_rod", 64); // 破损崩坏燃料棒 / Broken Honkai Fuel Rod; I18–I23/I47
        item("broken_dense_honkai_fuel_rod", 64); // 破损浓缩崩坏燃料棒 / Broken Dense Honkai Fuel Rod; I18–I23/I47
        item("recovered_fuel_casing_material", 64); // 回收燃料壳体材料 / Recovered Fuel Casing Material; I18–I23/I47
        item("inactive_fuel_residue", 64); // 失活燃料残渣 / Inactive Fuel Residue; I18–I23/I47
        item("spatial_probe", 1); // 空间观测探针 / Spatial Probe; I24–I32/I51/I53
        item("unmanned_resource_probe", 1); // 无人资源探测器 / Unmanned Resource Probe; I24–I32/I51/I53
        item("industrial_work_drone", 1); // 工业作业无人机 / Industrial Work Drone; I24–I32/I51/I53
        item("worn_resource_probe", 1); // 磨损的资源探测器 / Worn Resource Probe; I24–I32/I51/I53
        item("worn_work_drone", 1); // 磨损的作业无人机 / Worn Work Drone; I24–I32/I51/I53
        item("drone_disassembly_scrap", 1); // 无人设备拆解废料 / Drone Disassembly Scrap; I24–I32/I51/I53
        item("empty_bubble_containment_vessel", 1); // 空世界泡收容容器 / Empty Bubble Containment Vessel; I24–I32/I51/I53
        item("sealed_real_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("unstable_simulated_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("stable_simulated_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("world_model_carrier", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("world_matter_seed", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("bubble_termination_charge", 1); // 世界泡终止组件 / Bubble Termination Charge; I24–I32/I51/I53
        item("bubble_container_remnant", 1); // 世界泡容器残件 / Bubble Container Remnant; I24–I32/I51/I53
        item("failed_containment_shell", 1); // 不合格收容壳体 / Failed Containment Shell; I24–I32/I51/I53
        item("reverse_engineering_specimen", 1); // 逆向工程复现样本 / Reverse Engineering Specimen; I24–I32/I51/I53
        item("failed_engineering_specimen", 1); // 失败工程样本 / Failed Engineering Specimen; I24–I32/I51/I53
        item("soulium_anchor_component", 64); // 魂钢锚定组件 / Soulium Anchor Component; I34–I45
        item("spatial_calibration_module", 64); // 空间校准模块 / Spatial Calibration Module; I34–I45
        item("world_maintenance_specimen", 64); // 中文备注：该处说明已按当前代码行为整理。
        item("conducting_composite", 64); // 高维导能复合材料 / Conducting Composite; I34–I45
        item("confining_composite", 64); // 高维约束复合材料 / Confining Composite; I34–I45
        item("reconstructing_composite", 64); // 高维重构复合材料 / Reconstructing Composite; I34–I45
        item("cognitive_composite", 64); // 高维认知复合材料 / Cognitive Composite; I34–I45
        item("composite_offcut", 64); // 高维复合材料边角料 / Composite Offcut; I34–I45
        item("polarized_electromagnetic_material", 64); // 极化电磁材料 / Polarized Electromagnetic Material; I34–I45
        item("cryogenic_condensed_material", 64); // 深冷凝聚材料 / Cryogenic Condensed Material; I34–I45
        item("extreme_casting_material", 64); // 极限铸造材料 / Extreme Casting Material; I34–I45
        item("civilization_singularity", 64); // 文明工程奇点 / Civilization Singularity; I34–I45
        item("honkai_adapted_circuit_substrate", 64); // 崩坏能适配电路基板 / Honkai Adapted Circuit Substrate; I48–I50/I52
        item("defective_circuit_substrate", 64); // 不合格电路基板 / Defective Circuit Substrate; I48–I50/I52
        item("circuit_lithography_mask", 64); // 电路光刻掩膜 / Circuit Lithography Mask; I48–I50/I52
        item("etched_circuit_layer", 64); // 已蚀刻电路层 / Etched Circuit Layer; I48–I50/I52
        item("failed_circuit_layer", 64); // 不合格电路层 / Failed Circuit Layer; I48–I50/I52
        item("circuit_encapsulation_part", 64); // 电路封装组件 / Circuit Encapsulation Part; I48–I50/I52
        item("rejected_circuit_package", 64); // 不合格电路封装 / Rejected Circuit Package; I48–I50/I52
        item("process_gas_filter", 64); // 工艺气体滤芯 / Process Gas Filter; I48–I50/I52
        item("depleted_gas_filter", 64); // 失效工艺气体滤芯 / Depleted Gas Filter; I48–I50/I52
        item("process_gas_impurity", 64); // 工艺气体杂质 / Process Gas Impurity; I48–I50/I52
        item("imitation_hyperion_blueprint", 64); // 仿制休伯利安蓝图 / Imitation Hyperion Blueprint; H01
        item("hyperion_keel_segment", 64); // 仿制休伯利安龙骨段 / Hyperion Keel Segment; H01
        item("hyperion_thruster_assembly", 64); // 仿制休伯利安推进器组件 / Hyperion Thruster Assembly; H01
        item("hyperion_navigation_module", 64); // 仿制休伯利安导航模块 / Hyperion Navigation Module; H01
        item("hyperion_bridge_module", 64); // 仿制休伯利安舰桥模块 / Hyperion Bridge Module; H01
        item("unencapsulated_flame_core", 64); // 未封装仿制炎之律者核心 / Unencapsulated Flame Core; I08/I33
        item("imitation_flame_core", 1); // 仿制炎之律者核心 / Imitation Flame Core; I33
        item("unencapsulated_ice_core", 64); // 未封装仿制冰之律者核心 / Unencapsulated Ice Core; I08/I33
        item("imitation_ice_core", 1); // 仿制冰之律者核心 / Imitation Ice Core; I33
        item("unencapsulated_reason_core", 64); // 未封装仿制理之律者核心 / Unencapsulated Reason Core; I08/I33
        item("unencapsulated_void_core", 64); // 未封装仿制空之律者核心 / Unencapsulated Void Core; I08/I33
        item("imitation_void_core", 1); // 仿制空之律者核心 / Imitation Void Core; I33
        item("unencapsulated_corruption_core", 64); // 未封装仿制侵蚀之律者核心 / Unencapsulated Corruption Core; I08/I33
        item("imitation_corruption_core", 1); // 仿制侵蚀之律者核心 / Imitation Corruption Core; I33
        item("unencapsulated_rock_core", 64); // 未封装仿制岩之律者核心 / Unencapsulated Rock Core; I08/I33
        item("imitation_rock_core", 1); // 仿制岩之律者核心 / Imitation Rock Core; I33
        item("unencapsulated_binding_core", 64); // 未封装仿制约束之律者核心 / Unencapsulated Binding Core; I08/I33
        item("imitation_binding_core", 1); // 仿制约束之律者核心 / Imitation Binding Core; I33
        item("unencapsulated_thunder_core", 64); // 未封装仿制雷之律者核心 / Unencapsulated Thunder Core; I08/I33
        item("imitation_thunder_core", 1); // 仿制雷之律者核心 / Imitation Thunder Core; I33
        item("unencapsulated_wind_core", 64); // 未封装仿制风之律者核心 / Unencapsulated Wind Core; I08/I33
        item("imitation_wind_core", 1); // 仿制风之律者核心 / Imitation Wind Core; I33
        item("imitation_void_archives", 1); // 仿制的虚空万藏 / Imitation Void Archives; I33/RN divine keys
        item("imitation_cosmic_juggernaut", 1); // 仿制的千界一乘 / Imitation Cosmic Juggernaut; I33/RN divine keys
        item("imitation_star_of_eden", 1); // 仿制的伊甸之星 / Imitation Star Of Eden; I33/RN divine keys
        item("imitation_oath_of_judah", 1); // 仿制的犹大的誓约 / Imitation Oath Of Judah; I33/RN divine keys
        item("divine_key_housing", 1); // 神之键封装框架 / Divine Key Housing; I33/RN divine keys
    }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    public static void registerBlocks() {
        block("voltage_machine_casing_hbv");
        block("voltage_machine_casing_hcv");
        block("voltage_machine_casing_hrv");
        block("voltage_machine_casing_hdv");
        block("voltage_machine_casing_qsv");
        block("voltage_machine_casing_qcv");
        block("voltage_machine_casing_qev");
        block("voltage_machine_casing_qav");
        block("voltage_machine_casing_imv");
        block("voltage_machine_casing_icv");
        block("voltage_machine_casing_irv");
        block("voltage_machine_casing_iwv");
        block("voltage_machine_casing_wfv");
        block("voltage_machine_casing_wsv");
        block("voltage_machine_casing_civ");
        block("voltage_machine_casing_cev");

        block("industrial_port_casing"); // 空余接口填充件，不具备仓室能力。
        block("honkai_collection_casing"); // 崩坏能采集机壳 / Honkai Collection Casing; I01–I53/S01–S05
        block("honkai_separation_casing"); // 崩坏能分离机壳 / Honkai Separation Casing; I01–I53/S01–S05
        block("honkai_stabilization_casing"); // 崩坏能稳定机壳 / Honkai Stabilization Casing; I01–I53/S01–S05
        block("soulium_chemical_casing"); // 魂钢化工机壳 / Soulium Chemical Casing; I01–I53/S01–S05
        block("nano_assembly_casing"); // 纳米装配机壳 / Nano Assembly Casing; I01–I53/S01–S05
        block("honkai_fuel_processing_casing"); // 崩坏燃料处理机壳 / Honkai Fuel Processing Casing; I01–I53/S01–S05
        block("small_honkai_reactor_vessel"); // 小型崩坏反应堆压力壳 / Small Honkai Reactor Vessel; I01–I53/S01–S05
        block("medium_honkai_reactor_vessel"); // 中型崩坏反应堆压力壳 / Medium Honkai Reactor Vessel; I01–I53/S01–S05
        block("large_honkai_reactor_vessel"); // 大型崩坏反应堆压力壳 / Large Honkai Reactor Vessel; I01–I53/S01–S05
        block("ultimate_honkai_reactor_vessel"); // 终极崩坏反应堆压力壳 / Ultimate Honkai Reactor Vessel; I01–I53/S01–S05
        block("quantum_observation_casing"); // 量子观测机壳 / Quantum Observation Casing; I01–I53/S01–S05
        block("world_bubble_containment_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("world_simulation_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("imaginary_anchor_casing"); // 虚数锚定机壳 / Imaginary Anchor Casing; I01–I53/S01–S05
        block("high_dimensional_assembly_casing"); // 高维装配机壳 / High Dimensional Assembly Casing; I01–I53/S01–S05
        block("precision_circuit_casing"); // 精密电路机壳 / Precision Circuit Casing; I01–I53/S01–S05
        block("research_institute_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("advanced_research_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("quantum_research_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("imaginary_research_casing"); // 中文备注：该处说明已按当前代码行为整理。
        block("civilization_cognition_casing"); // 文明认知穹顶机壳 / Civilization Cognition Casing; I01–I53/S01–S05
        block("honkai_collection_antenna"); // 崩坏能采集天线组件 / Honkai Collection Antenna; I01–I53/H01
        block("spectral_analysis_lens"); // 频谱分析透镜组件 / Spectral Analysis Lens; I01–I53/H01
        block("nano_reconstruction_chamber"); // 纳米重构腔体 / Nano Reconstruction Chamber; I01–I53/H01
        block("honkai_heat_exchanger"); // 崩坏工业换热组件 / Honkai Heat Exchanger; I01–I53/H01
        block("quantum_confinement_coil"); // 量子约束线圈 / Quantum Confinement Coil; I01–I53/H01
        block("imaginary_anchor_ring"); // 虚数锚定环组件 / Imaginary Anchor Ring; I01–I53/H01
        block("high_dimensional_energy_conduit"); // 高维导能构件 / High Dimensional Energy Conduit; I01–I53/H01
        block("civilization_computing_array"); // 文明计算阵列 / Civilization Computing Array; I01–I53/H01
        block("hyperion_armored_hull"); // 仿制休伯利安装甲舰壳 / Hyperion Armored Hull; I01–I53/H01
        block("hyperion_structural_frame"); // 仿制休伯利安结构框架 / Hyperion Structural Frame; I01–I53/H01
        block("hyperion_engine_nozzle"); // 仿制休伯利安引擎喷口 / Hyperion Engine Nozzle; I01–I53/H01
        block("hyperion_bridge_panel"); // 仿制休伯利安舰桥面板 / Hyperion Bridge Panel; I01–I53/H01
        block("wonder_origin_casing"); // 始源·奇观外壳 / Wonder Origin Casing; W01/I42
        block("wonder_origin_support"); // 始源·奇观支撑 / Wonder Origin Support; W01/I42
        block("wonder_origin_interface"); // 始源·奇观接口 / Wonder Origin Interface; W01/I42
        block("wonder_origin_core_mount"); // 始源·奇观核心座 / Wonder Origin Core Mount; W01/I42
        block("wonder_reason_casing"); // 理·奇观外壳 / Wonder Reason Casing; W02/I42
        block("wonder_reason_support"); // 理·奇观支撑 / Wonder Reason Support; W02/I42
        block("wonder_reason_interface"); // 理·奇观接口 / Wonder Reason Interface; W02/I42
        block("wonder_reason_core_mount"); // 理·奇观核心座 / Wonder Reason Core Mount; W02/I42
        block("wonder_void_casing"); // 空·奇观外壳 / Wonder Void Casing; W03/I42
        block("wonder_void_support"); // 空·奇观支撑 / Wonder Void Support; W03/I42
        block("wonder_void_interface"); // 空·奇观接口 / Wonder Void Interface; W03/I42
        block("wonder_void_core_mount"); // 空·奇观核心座 / Wonder Void Core Mount; W03/I42
        block("wonder_thunder_casing"); // 雷·奇观外壳 / Wonder Thunder Casing; W04/I42
        block("wonder_thunder_support"); // 雷·奇观支撑 / Wonder Thunder Support; W04/I42
        block("wonder_thunder_interface"); // 雷·奇观接口 / Wonder Thunder Interface; W04/I42
        block("wonder_thunder_core_mount"); // 雷·奇观核心座 / Wonder Thunder Core Mount; W04/I42
        block("wonder_wind_casing"); // 风·奇观外壳 / Wonder Wind Casing; W05/I42
        block("wonder_wind_support"); // 风·奇观支撑 / Wonder Wind Support; W05/I42
        block("wonder_wind_interface"); // 风·奇观接口 / Wonder Wind Interface; W05/I42
        block("wonder_wind_core_mount"); // 风·奇观核心座 / Wonder Wind Core Mount; W05/I42
        block("wonder_ice_casing"); // 冰·奇观外壳 / Wonder Ice Casing; W06/I42
        block("wonder_ice_support"); // 冰·奇观支撑 / Wonder Ice Support; W06/I42
        block("wonder_ice_interface"); // 冰·奇观接口 / Wonder Ice Interface; W06/I42
        block("wonder_ice_core_mount"); // 冰·奇观核心座 / Wonder Ice Core Mount; W06/I42
        block("wonder_death_casing"); // 死·奇观外壳 / Wonder Death Casing; W07/I42
        block("wonder_death_support"); // 死·奇观支撑 / Wonder Death Support; W07/I42
        block("wonder_death_interface"); // 死·奇观接口 / Wonder Death Interface; W07/I42
        block("wonder_death_core_mount"); // 死·奇观核心座 / Wonder Death Core Mount; W07/I42
        block("wonder_flame_casing"); // 炎·奇观外壳 / Wonder Flame Casing; W08/I42
        block("wonder_flame_support"); // 炎·奇观支撑 / Wonder Flame Support; W08/I42
        block("wonder_flame_interface"); // 炎·奇观接口 / Wonder Flame Interface; W08/I42
        block("wonder_flame_core_mount"); // 炎·奇观核心座 / Wonder Flame Core Mount; W08/I42
        block("wonder_sentience_casing"); // 识·奇观外壳 / Wonder Sentience Casing; W09/I42
        block("wonder_sentience_support"); // 识·奇观支撑 / Wonder Sentience Support; W09/I42
        block("wonder_sentience_interface"); // 识·奇观接口 / Wonder Sentience Interface; W09/I42
        block("wonder_sentience_core_mount"); // 识·奇观核心座 / Wonder Sentience Core Mount; W09/I42
        block("wonder_rock_casing"); // 岩·奇观外壳 / Wonder Rock Casing; W10/I42
        block("wonder_rock_support"); // 岩·奇观支撑 / Wonder Rock Support; W10/I42
        block("wonder_rock_interface"); // 岩·奇观接口 / Wonder Rock Interface; W10/I42
        block("wonder_rock_core_mount"); // 岩·奇观核心座 / Wonder Rock Core Mount; W10/I42
        block("wonder_domination_casing"); // 支配·奇观外壳 / Wonder Domination Casing; W11/I42
        block("wonder_domination_support"); // 支配·奇观支撑 / Wonder Domination Support; W11/I42
        block("wonder_domination_interface"); // 支配·奇观接口 / Wonder Domination Interface; W11/I42
        block("wonder_domination_core_mount"); // 支配·奇观核心座 / Wonder Domination Core Mount; W11/I42
        block("wonder_binding_casing"); // 约束·奇观外壳 / Wonder Binding Casing; W12/I42
        block("wonder_binding_support"); // 约束·奇观支撑 / Wonder Binding Support; W12/I42
        block("wonder_binding_interface"); // 约束·奇观接口 / Wonder Binding Interface; W12/I42
        block("wonder_binding_core_mount"); // 约束·奇观核心座 / Wonder Binding Core Mount; W12/I42
        block("wonder_corruption_casing"); // 侵蚀·奇观外壳 / Wonder Corruption Casing; W13/I42
        block("wonder_corruption_support"); // 侵蚀·奇观支撑 / Wonder Corruption Support; W13/I42
        block("wonder_corruption_interface"); // 侵蚀·奇观接口 / Wonder Corruption Interface; W13/I42
        block("wonder_corruption_core_mount"); // 侵蚀·奇观核心座 / Wonder Corruption Core Mount; W13/I42
        block("wonder_finality_casing"); // 终焉·奇观外壳 / Wonder Finality Casing; W14/I42
        block("wonder_finality_support"); // 终焉·奇观支撑 / Wonder Finality Support; W14/I42
        block("wonder_finality_interface"); // 终焉·奇观接口 / Wonder Finality Interface; W14/I42
        block("wonder_finality_core_mount"); // 终焉·奇观核心座 / Wonder Finality Core Mount; W14/I42
        block("wonder_tree_sea_casing"); // 树海·奇观外壳 / Wonder Tree Sea Casing; W15/I42
        block("wonder_tree_sea_support"); // 树海·奇观支撑 / Wonder Tree Sea Support; W15/I42
        block("wonder_tree_sea_interface"); // 树海·奇观接口 / Wonder Tree Sea Interface; W15/I42
        block("wonder_tree_sea_core_mount"); // 树海·奇观核心座 / Wonder Tree Sea Core Mount; W15/I42
    }

    /** @param id 稳定路径 / stable registry path; @param stack 最大件数 / maximum stack count. */
    private static void item(String id, int stack) {
        if (ITEMS.containsKey(id)) throw new IllegalStateException("Duplicate industrial item: " + id);
        ITEMS.put(id, Hk3Items.ITEMS.register(id, () -> new Item(new Item.Properties().stacksTo(stack))));
    }
    /** @param id 方块与物品共用路径 / shared block and BlockItem registry path. */
    private static void block(String id) {
        if (BLOCKS.containsKey(id)) throw new IllegalStateException("Duplicate industrial block: " + id);
        BLOCKS.put(id, Hk3Blocks.registerBlock(id, () -> new Block(BlockBehaviour.Properties.of()
                .strength(5.0F, 10.0F).sound(SoundType.METAL).requiresCorrectToolForDrops())));
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Map<String, RegistryObject<Item>> items() { return Collections.unmodifiableMap(ITEMS); }
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Map<String, RegistryObject<Block>> blocks() { return Collections.unmodifiableMap(BLOCKS); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
