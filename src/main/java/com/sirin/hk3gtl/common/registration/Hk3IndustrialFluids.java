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

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-27 02:26:24（第 1 次备注 · 内测5修订87）
 * 删除：无，保留历史备注、稳定注册键和不相关工艺。
 * 新增：clarified_honkai_mother_liquor除杂母液，沿现有GT材质流体注册及纹理生成方式注册。
 * 修改：原含能母液保留为晶种提取原料，不以同一ID同时表示净化前后流体。
 * 用途：隔离脏母液与回流液，避免旁路净化复制产物；实际使用受配方新采液和耗材约束。
 */
public final class Hk3IndustrialFluids {
    private static final Map<String, Material> MATERIALS = new LinkedHashMap<>();
    private Hk3IndustrialFluids() {}
    /** 中文说明：该处说明已按当前代码行为整理。*/
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
    }
    /** 中文说明：该处说明已按当前代码行为整理。*/
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
    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static Map<String, Material> materials() { return Collections.unmodifiableMap(MATERIALS); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
