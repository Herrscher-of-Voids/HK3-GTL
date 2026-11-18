package com.sirin.hk3gtl.common.registration;

import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.chemical.material.info.MaterialIconSet;
import com.gregtechceu.gtceu.api.fluids.FluidBuilder;
import com.gregtechceu.gtceu.api.fluids.FluidState;
import com.gregtechceu.gtceu.api.fluids.store.FluidStorageKeys;
import net.minecraft.resources.ResourceLocation;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

public final class Hk3IndustrialFluids {
    private static final Map<String, Material> MATERIALS = new LinkedHashMap<>();
    private Hk3IndustrialFluids() {}
    public static void register() {
        add("crude_honkai_energy", false); // 粗制液态崩坏能 / Crude Honkai Energy
        add("clarified_honkai_mother_liquor", false); // 净化附产，须与新采液共同回流。
        add("honkai_mother_liquor", false); // 含能母液 / Honkai Mother Liquor
        add("stabilized_liquid_honkai_energy", false); // 稳定液态崩坏能 / Stabilized Liquid Honkai Energy
        add("honkai_separation_medium", false); // 崩坏能分离介质 / Honkai Separation Medium
        add("honkai_stabilization_medium", false); // 崩坏能稳定介质 / Honkai Stabilization Medium
        add("spent_honkai_stabilization_medium", false); // 废稳定介质 / Spent Honkai Stabilization Medium
        add("spent_analysis_reagent", false); // 废分析试剂 / Spent Analysis Reagent
        add("honkai_analysis_reagent", false); // 崩坏能分析试剂 / Honkai Analysis Reagent
        add("unrecoverable_process_effluent", false); // 不可再生工艺废液 / Unrecoverable Process Effluent
        add("liquid_honkai_fuel", false); // 液态崩坏燃料 / Liquid Honkai Fuel
        add("concentrated_liquid_honkai_fuel", false); // 浓缩液态崩坏燃料 / Concentrated Liquid Honkai Fuel
        add("fuel_refining_residual", false); // 燃料精炼残液 / Fuel Refining Residual
        add("crystallization_residual_liquid", false); // 结晶残液 / Crystallization Residual Liquid
        add("soulium_precursor_fluid", false); // 中文备注：该处说明已按当前代码行为整理。
        add("soulium_process_solvent", false); // 魂钢工艺溶剂 / Soulium Process Solvent
        add("spent_soulium_solvent", false); // 废魂钢溶剂 / Spent Soulium Solvent
        add("nano_reaction_tail_liquid", false); // 纳米反应尾液 / Nano Reaction Tail Liquid
        add("honkai_resistant_coating", false); // 抗崩坏侵蚀涂层液 / Honkai Resistant Coating
        add("spent_resistant_coating", false); // 废抗侵蚀涂层液 / Spent Resistant Coating
        add("gaseous_honkai_energy", true); // 气态崩坏能 / Gaseous Honkai Energy
        add("soulium_protective_gas", true); // 魂钢保护气体 / Soulium Protective Gas
        add("spent_soulium_process_gas", true); // 废魂钢工艺气体 / Spent Soulium Process Gas
        add("hot_soulium_exhaust", true); // 魂钢热尾气 / Hot Soulium Exhaust
        add("bubble_confinement_medium", false); // 世界泡约束介质 / Bubble Confinement Medium
        add("world_stabilization_medium", false); // 中文备注：该处说明已按当前代码行为整理。
        add("spent_world_stabilization_medium", false); // 中文备注：该处说明已按当前代码行为整理。
        add("honkai_coolant", false); // 崩坏工业冷却液 / Honkai Coolant
        add("hot_honkai_coolant", false); // 高温崩坏工业冷却液 / Hot Honkai Coolant
        add("lost_coolant_residue", false); // 劣化冷却液 / Lost Coolant Residue
        add("fuel_waste_processing_fluid", false); // 中文备注：该处说明已按当前代码行为整理。
        add("circuit_growth_medium", false); // 电路生长介质 / Circuit Growth Medium
        add("spent_circuit_growth_medium", false); // 废电路生长介质 / Spent Circuit Growth Medium
        add("honkai_circuit_etchant", false); // 崩坏电路蚀刻液 / Honkai Circuit Etchant
        add("spent_honkai_etchant", false); // 废崩坏电路蚀刻液 / Spent Honkai Etchant
        add("stable_transport_medium", false); // 稳定输运介质 / Stable Transport Medium
        add("loaded_honkai_separation_medium", 0x9468C8, 300);
        add("spent_honkai_separation_medium", 0x74666D, 300);
        add("copper_electrolyte", 0x238FC3, 300);
        add("contaminated_copper_electrolyte", 0x4E7478, 300);
        add("secondary_heat_transfer_medium", 0x4C91B5, 300);
        add("warm_secondary_heat_transfer_medium", 0xD7A44C, 450);
        add("hot_secondary_heat_transfer_medium", 0xE66B3D, 900);
        add("phase_modulation_medium", 0xA78DE0, 300);
        add("spent_phase_modulation_medium", 0x6D687C, 300);
        add("anchor_stress_transfer_grout", 0xFFFFFF, 300);
        add("constraint_ceramic_suspension", 0xFFFFFF, 300);
        add("cryogenic_grid_infiltrant", 0xFFFFFF, 300);
        add("fatigue_isolation_encapsulant", 0xFFFFFF, 300);
        add("gradient_fiber_sizing_bath", 0xFFFFFF, 300);
        add("honkai_interface_priming_liquid", 0xFFFFFF, 300);
        add("honkai_selective_extractant", 0xFFFFFF, 300);
        add("impedance_matching_coupling_gel", 0xFFFFFF, 300);
        add("low_volatility_lamination_resin", 0xFFFFFF, 300);
        add("multiaxial_cocure_infusion_resin", 0xFFFFFF, 300);
        add("nano_barrier_ceramic_dispersion", 0xFFFFFF, 300);
        add("nano_surface_passivation_liquid", 0xFFFFFF, 300);
        add("nanocarbon_predispersion_slurry", 0xFFFFFF, 300);
        add("paired_seed_growth_bath", 0xFFFFFF, 300);
        add("phase_transfer_ceramic_sol", 0xFFFFFF, 300);
        add("quadrisystem_interface_couplant", 0xFFFFFF, 300);
        add("reconstruction_composition_flux", 0xFFFFFF, 300);
        add("resonance_growth_solution", 0xFFFFFF, 300);
        add("reversible_service_bonding_medium", 0xFFFFFF, 300);
        add("spent_constraint_ceramic_vehicle", 0xFFFFFF, 300);
        add("spent_honkai_interface_carrier", 0xFFFFFF, 300);
        add("spent_honkai_selective_extractant", 0xFFFFFF, 300);
        add("spent_lamination_resin", 0xFFFFFF, 300);
        add("spent_nano_passivation_liquid", 0xFFFFFF, 300);
        add("spent_resonance_growth_solution", 0xFFFFFF, 300);
        add("spent_stress_relief_conditioning_bath", 0xFFFFFF, 300);
        add("stress_relief_conditioning_bath", 0xFFFFFF, 300);
        add("zirconium_carbide_nano_sealing_liquid", 0xFFFFFF, 300);
        add("continuity_confined_honkai_fuel", 0xFFFFFF, 300);
        add("imaginary_coupled_honkai_fuel", 0xFFFFFF, 300);
        add("resonance_activated_honkai_fuel", 0xFFFFFF, 300);
        add("supercritical_honkai_fuel", 0xFFFFFF, 300);
    }
    private static void add(String id, int color, int temperature) {
        add(id, color, temperature, false);
    }
    private static void add(String id, int color, int temperature, boolean gas) {
        FluidBuilder fluid = new FluidBuilder().name(id).translation("material.hk3gtl." + id)
                .textures(true, true).temperature(temperature).state(gas ? FluidState.GAS : FluidState.LIQUID);
        Material material = new Material.Builder(new ResourceLocation("hk3gtl", id))
                .fluid(gas ? FluidStorageKeys.GAS : FluidStorageKeys.LIQUID, fluid)
                .color(color).iconSet(MaterialIconSet.FLUID).buildAndRegister();
        MATERIALS.put(id, material);
    }
    private static void add(String id, boolean gas) {
        if (MATERIALS.containsKey(id)) throw new IllegalStateException("Duplicate industrial fluid: " + id);
        FluidBuilder fluid = new FluidBuilder().name(id).translation("material.hk3gtl." + id)
                .textures(true, true).temperature(id.startsWith("hot_") ? 600 : 300)
                .state(gas ? FluidState.GAS : FluidState.LIQUID);
        Material material = new Material.Builder(new ResourceLocation("hk3gtl", id))
                .fluid(gas ? FluidStorageKeys.GAS : FluidStorageKeys.LIQUID, fluid)
                .color(0xB68CEC).iconSet(MaterialIconSet.FLUID).buildAndRegister();
        MATERIALS.put(id, material);
    }
    public static Map<String, Material> materials() { return Collections.unmodifiableMap(MATERIALS); }
}

