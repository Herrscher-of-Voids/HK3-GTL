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

public final class Hk3IndustrialContent {
    // 注册线程写入，完成后只读；保持目录顺序，不允许调用方修改。
    private static final Map<String, RegistryObject<Item>> ITEMS = new LinkedHashMap<>();
    private static final Map<String, RegistryObject<Block>> BLOCKS = new LinkedHashMap<>();
    private Hk3IndustrialContent() {}

    public static void registerItems() {
        item("world_mining_legacy_record",64);
        item("ship_engineering_archive",64);
        item("honkai_detector_calibration_report", 64); // 探测器真实校准的纸质报告，升级时消耗。
        item("prototype_honkai_detector", 1); // 试作型崩坏能探测器 / Prototype Honkai Detector; I01/I07
        item("liquid_honkai_detector", 1); // 一阶液态崩坏能探测器 / Liquid Honkai Detector; I01/I07
        item("solid_honkai_detector", 1); // 二阶固态崩坏能探测器 / Solid Honkai Detector; I01/I07
        item("gaseous_honkai_detector", 1); // 三阶气态崩坏能探测器 / Gaseous Honkai Detector; I01/I07
        item("energy_honkai_detector", 1); // 四阶能量态崩坏能探测器 / Energy Honkai Detector; I01/I07
        item("honkai_analysis_sample", 64); // 崩坏能分析样本 / Honkai Analysis Sample; I02–I08
        item("analyzed_honkai_sample", 64); // 已分析崩坏能样本 / Analyzed Honkai Sample; I02–I08
        item("honkai_reference_sample", 64); // 崩坏能标准样本 / Honkai Reference Sample; I02–I08
        item("failed_engineering_specimen", 64);
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
        for (var fuel : com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.ALL) {
            item(fuel.item("_precursor"), 64);
            item(fuel.item("_charge"), 64);
            item(fuel.item("_fuel"), 64);
            item("depleted_" + fuel.item("_fuel"), 64);
            item("broken_" + fuel.item("_fuel"), 64);
        }
        for (var rod : com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.RODS)
            for (int count : com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.BUNDLE_SIZES) {
                item(rod.bundle(count), 64);
                item("depleted_" + rod.bundle(count), 64);
                item("broken_" + rod.bundle(count), 64);
            }
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
        item("located_real_world_bubble", 1);
        item("sealed_real_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("unstable_simulated_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("stable_simulated_world_bubble", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("world_model_carrier", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("world_matter_seed", 1); // 中文备注：该处说明已按当前代码行为整理。
        item("bubble_termination_charge", 1); // 世界泡终止组件 / Bubble Termination Charge; I24–I32/I51/I53
        item("bubble_container_remnant", 1); // 世界泡容器残件 / Bubble Container Remnant; I24–I32/I51/I53
        item("failed_containment_shell", 1); // 不合格收容壳体 / Failed Containment Shell; I24–I32/I51/I53
        item("reverse_engineering_specimen", 1); // 逆向工程复现样本 / Reverse Engineering Specimen; I24–I32/I51/I53
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
        item("imitation_flame_core", 1); // 仿制炎之律者核心 / Imitation Flame Core; I08/I33
        item("imitation_ice_core", 1); // 仿制冰之律者核心 / Imitation Ice Core; I08/I33
        item("imitation_void_core", 1); // 仿制空之律者核心 / Imitation Void Core; I08/I33
        item("imitation_corruption_core", 1); // 仿制侵蚀之律者核心 / Imitation Corruption Core; I08/I33
        item("imitation_rock_core", 1); // 仿制岩之律者核心 / Imitation Rock Core; I08/I33
        item("imitation_binding_core", 1); // 仿制约束之律者核心 / Imitation Binding Core; I08/I33
        item("imitation_thunder_core", 1); // 仿制雷之律者核心 / Imitation Thunder Core; I08/I33
        item("imitation_wind_core", 1); // 仿制风之律者核心 / Imitation Wind Core; I08/I33
        item("imitation_void_archives", 1); // 仿制的虚空万藏 / Imitation Void Archives; I33/RN divine keys
        item("imitation_star_of_eden", 1); // 仿制的伊甸之星 / Imitation Star Of Eden; I33/RN divine keys
        item("imitation_oath_of_judah", 1); // 仿制的犹大的誓约 / Imitation Oath Of Judah; I33/RN divine keys
        item("divine_key_housing", 1); // 神之键封装框架 / Divine Key Housing; I33/RN divine keys
        // V3仅补工装、目标几何坯和芯粒；既有主材与电子部件继续复用。
        item("honkai_lattice_electroforming_mandrel", 64);
        item("honkai_lattice_deposited_interconnect", 64);
        item("optical_reference_grating", 64);
        item("optical_process_feedback_module", 64);
        item("ultradense_pump_housing_mold", 64);
        item("ultradense_pump_housing_blank", 64);
        item("quantum_coherence_logic_chiplet", 64);
        item("quantum_coherence_io_chiplet", 64);
        item("quantum_coherence_interposer", 64);
        item("imaginary_topology_logic_chiplet", 64);
        item("imaginary_topology_io_chiplet", 64);
        item("imaginary_topology_interposer", 64);
        item("civilization_endurance_logic_chiplet", 64);
        item("civilization_endurance_io_chiplet", 64);
        item("civilization_endurance_interposer", 64);
        item("acousto_optic_tuning_array", 64);
        item("active_quiet_bearing_cartridge", 64);
        item("anchor_gap_positioner", 64);
        item("anchored_hermetic_feedthrough", 64);
        item("axial_magnetic_thrust_assembly", 64);
        item("balanced_coherent_readout_tile", 64);
        item("bounded_nano_control_core", 64);
        item("carbon_nanotube_anchoring_mesh", 64);
        item("causal_order_dispatch_core", 64);
        item("ceramic_bellows_seal", 64);
        item("ceramic_drilled_interposer", 64);
        item("ceramic_feedthrough_array", 64);
        item("ceramic_interface_reinforced_fiber_sheet", 64);
        item("ceramic_magnetic_bearing", 64);
        item("civilization_state_checkpoint_core", 64);
        item("clock_phase_recovery_module", 64);
        item("coherence_isolation_interposer", 64);
        item("collapsed_hip_capsule", 64);
        item("compliant_soulium_contact_array", 64);
        item("confinement_boundary_bus", 64);
        item("conjugate_seed_coupling_clamp", 64);
        item("constraint_ceramic_powder_blend", 64);
        item("constraint_compensated_clock_module", 64);
        item("counterflow_isolation_coldplate", 64);
        item("crack_arrest_isolation_interleaf", 64);
        item("cryogenic_pressure_header", 64);
        item("cryogenic_sampling_chamber", 64);
        item("dielectric_edge_sealing_strip", 64);
        item("differential_containment_liner", 64);
        item("differential_measurement_component", 64);
        item("differential_resonance_bridge", 64);
        item("directional_energy_band_interposer", 64);
        item("domain_interlocked_manipulator_core", 64);
        item("drainable_service_loop_jacket", 64);
        item("dual_channel_servo_cartridge", 64);
        item("electrohydraulic_servo_spool", 64);
        item("encapsulation_sidewall_insulation_liner", 64);
        item("energy_isolated_servo_block", 64);
        item("fault_containment_voter", 64);
        item("four_domain_consensus_core", 64);
        item("four_quadrant_servo_drive_module", 64);
        item("four_system_isolation_backplane", 64);
        item("gradient_fiber_sizing_sleeve", 64);
        item("gradient_path_formation_head", 64);
        item("heralded_pair_interface", 64);
        item("hermetic_differential_optical_bus", 64);
        item("hip_pressure_reference_fixture", 64);
        item("hip_sealing_capsule", 64);
        item("honkai_spectral_calibration_film", 64);
        item("imaginary_phase_boundary_die", 64);
        item("imaginary_reference_resonator", 64);
        item("impedance_graded_coupling_ribbon", 64);
        item("independent_failover_manifold", 64);
        item("indexed_remanufacture_joint", 64);
        item("interferometric_path_router", 64);
        item("isolated_service_loop_block", 64);
        item("laminate_registration_fixture", 64);
        item("lamination_busbar_carrier", 64);
        item("lattice_lamination_prepreg", 64);
        item("maintainable_actuator_cartridge", 64);
        item("microchannel_circuit_cold_plate", 64);
        item("multiaxial_worldweave_backplane", 64);
        item("nano_joint_isolation_membrane", 64);
        item("nano_swarm_timing_node", 64);
        item("optical_encoder_drive_pack", 64);
        item("paired_syndrome_decoder", 64);
        item("paired_thermal_balance_bridge", 64);
        item("perennial_handover_checkpoint_core", 64);
        item("phase_boundary_ceramic_nucleant", 64);
        item("phase_difference_decoder", 64);
        item("phase_isolated_actuator_shell", 64);
        item("phase_matched_mesh_spacer", 64);
        item("phase_transition_protocol_core", 64);
        item("phone_duplex_interconnect_module", 64);
        item("phone_isolated_lv_power_module", 64);
        item("phone_optical_touch_panel", 64);
        item("piezoelectric_resonator_blank", 64);
        item("prospecting_payload_cartridge", 64);
        item("pulsation_buffer_valve_group", 64);
        item("quadrature_phase_receiver", 64);
        item("quadrisystem_interoperability_backplane", 64);
        item("quadrisystem_state_reconciler", 64);
        item("quadrisystem_thermal_exchange_hub", 64);
        item("quench_recovery_coldblock", 64);
        item("reactor_instrumentation_header", 64);
        item("reconstruction_composition_charge", 64);
        item("reconstruction_mapping_tile", 64);
        item("rectifier_switching_stack", 64);
        item("redundant_boundary_servo", 64);
        item("reference_frame_anchor_decoder", 64);
        item("replaceable_service_bay", 64);
        item("replaceable_service_interface_tile", 64);
        item("replaceable_service_interposer", 64);
        item("resonance_damping_interlayer", 64);
        item("resonance_texture_seed", 64);
        item("resonant_load_feedback_unit", 64);
        item("reusable_honkai_optical_ampoule", 64);
        item("reversible_topology_scheduler", 64);
        item("seeded_world_lattice_cartridge", 64);
        item("segmented_repair_coolant_jacket", 64);
        item("segmented_thermal_barrier", 64);
        item("segregated_media_exchange_block", 64);
        item("separated_phase_manifold", 64);
        item("soulium_diffusion_bonding_interlayer", 64);
        item("soulium_gradient_foil_pack", 64);
        item("soulium_grain_boundary_inoculant", 64);
        item("soulium_microchannel_manifold", 64);
        item("soulium_nano_actuator_blank", 64);
        item("soulium_nano_actuator_joint", 64);
        item("soulium_nano_deposition_scaffold", 64);
        item("soulium_nucleation_granule", 64);
        item("soulium_porous_carrier", 64);
        item("soulium_structural_preform", 64);
        item("staged_leak_isolation_valve", 64);
        item("stitched_multiaxial_z_binder", 64);
        item("stripped_lamination_busbar", 64);
        item("structural_load_transfer_node", 64);
        item("symmetric_multichip_interconnect_bridge", 64);
        item("tendon_balance_actuator", 64);
        item("torsion_decoupling_flexure_coupling", 64);
        item("triaxial_anchor_interposer", 64);
        item("triaxial_anchor_tendon", 64);
        item("vacuum_return_flow_manifold", 64);
        item("vacuum_screened_quantum_socket", 64);
        item("world_topology_routing_tile", 64);
        item("continuity_fuel_confinement_fixture", 64);
        item("imaginary_fuel_coupling_fixture", 64);
        item("resonant_fuel_activation_fixture", 64);
        item("supercritical_fuel_pressure_fixture", 64);
    }

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
    public static Map<String, RegistryObject<Item>> items() { return Collections.unmodifiableMap(ITEMS); }
    public static Map<String, RegistryObject<Block>> blocks() { return Collections.unmodifiableMap(BLOCKS); }
}

