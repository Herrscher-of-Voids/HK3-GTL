package com.sirin.hk3gtl.common.machine;

/** 2026-10-30（修订182）：接入I40–I45六台批准控制器、各自额定电压与独立三态面板；完整预览和工艺守卫沿用既有架构，不开放生存获取。 */

/** 【控制器材质变更 · 修订178】2026-10-26 22:02:44：按负责人“采用32套候选，保留4套原材质”接入独立三态面板；保留既有四套像素，不改建筑、控制器ID或工艺。 */

import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LateIndustrialPatterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessEnergy;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;



 
















 






public final class Hk3LateIndustrialMachines {
    private static final ResourceLocation SHELL = new ResourceLocation("hk3gtl", "block/casings/industrial_controller_shell");
    private static final Map<String, MultiblockMachineDefinition> MACHINES = new ConcurrentHashMap<>();

    private Hk3LateIndustrialMachines() {}

    public static void init() {
        register("i19_small_honkai_reactor", "i19", Hk3Tiers.HBV);
        register("i20_medium_honkai_reactor", "i20", Hk3Tiers.QSV);
        register("i21_large_honkai_reactor", "i21", Hk3Tiers.IMV);
        register("i22_ultimate_honkai_reactor", "i22", Hk3Tiers.WSV);
        register("i23_honkai_phase_transition_generator", "i23", Hk3Tiers.QCV);
        register("i24_quantum_anomaly_observation_array", "i24", Hk3Tiers.QEV);
        register("i25_world_bubble_coordinate_analysis_center", "i25", Hk3Tiers.QEV);
        register("i26_world_bubble_unmanned_mining_dispatch", "i26", Hk3Tiers.QAV);
        register("i27_world_bubble_capture_array", "i27", Hk3Tiers.IMV);
        register("i28_world_bubble_termination_reclaimer", "i28", Hk3Tiers.IMV);
        register("i29_simulated_world_bubble_synthesizer", "i29", Hk3Tiers.ICV);
        register("i30_simulated_world_bubble_stabilizer", "i30", Hk3Tiers.ICV);
        register("i31_simulated_world_bubble_termination_reclaimer", "i31", Hk3Tiers.ICV);
        register("i32_relic_technology_reverse_laboratory", "i32", Hk3Tiers.QAV);
        register("i33_imitation_divine_key_assembly_center", "i33", Hk3Tiers.QCV);
        register("i34_imaginary_tree_observation_array", "i34", Hk3Tiers.IRV);
        register("i35_imaginary_space_anchoring_array", "i35", Hk3Tiers.IRV);
        register("i36_honkai_reality_stability_anchor", "i36", Hk3Tiers.QSV);
        register("i37_world_maintenance_trial_platform", "i37", Hk3Tiers.WFV);
        register("i38_imaginary_energy_rectification_hub", "i38", Hk3Tiers.IWV);
        register("i39_unmanned_cross_boundary_route_relay", "i39", Hk3Tiers.ICV);
        register("i40_civilization_wonder_material_synthesis_center", "i40", Hk3Tiers.WFV);
        register("i41_civilization_energy_dispatch_hub", "i41", Hk3Tiers.IWV);
        register("i42_wonder_component_prefabrication_factory", "i42", Hk3Tiers.WFV);
        register("i43_civilization_engineering_acceptance_center", "i43", Hk3Tiers.WSV);
        register("i44_imitation_thousand_realms_beacon", "i44", Hk3Tiers.QCV);
        register("i45_imitation_thousand_realms_train", "i45", Hk3Tiers.QCV);
    }

    public static MultiblockMachineDefinition get(String key) {
        var definition = MACHINES.get(key);
        if (definition == null) throw new IllegalArgumentException("未注册高阶控制器：" + key);
        return definition;
    }

    private static void register(String name, String key, int tier) {
        String role = key.toUpperCase(Locale.ROOT);
        String overlay = key.equals("i37") ? "i35" : key;
        var definition = Hk3Gtl.REGISTRATE.multiblock(name, holder -> key.equals("i34")
                ? new com.sirin.hk3gtl.common.machine.tree.Hk3TreeObservationMachine(holder)
                : key.equals("i36")
                ? new com.sirin.hk3gtl.common.machine.research.Hk3RealityStabilityAnchorMachine(holder)
                : com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.reactor(role)
                ? new com.sirin.hk3gtl.common.machine.energy.Hk3ReactorMachine(holder, role)
                : new Hk3LateIndustrialMachine(holder, role))
                .tier(tier).rotationState(RotationState.NON_Y_AXIS)
                .generator(Hk3ResearchProcessEnergy.isGenerator(role))
                .allowFlip(false).allowExtendedFacing(false)
                .recipeType(Hk3ResearchProcessTypes.get(role)).noRecipeModifier()
                .appearanceBlock(() -> Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3LateIndustrialPatterns.create(def, key))
                .multiblockPreviewRenderer(true, true)
                .workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/" + overlay
                        + (Integer.parseInt(key.substring(1)) >= 40 ? "_unique_r182"
                        : Integer.parseInt(key.substring(1)) >= 34 ? "_unique_r181"
                        : Integer.parseInt(key.substring(1)) >= 29 ? "_unique_r180" : "_unique_r178")))
                .tooltips(Component.translatable("hk3gtl.machine." + name + ".tooltip.0"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.1"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();
        definition.setShapes(() -> java.util.List.of(Hk3LargeArchitectureShapes.create(definition, key)));
        if (MACHINES.putIfAbsent(key, definition) != null)
            throw new IllegalStateException("高阶控制器重复注册：" + key);
    }
}
