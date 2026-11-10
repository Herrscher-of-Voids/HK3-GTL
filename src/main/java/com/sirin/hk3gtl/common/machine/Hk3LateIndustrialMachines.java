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



/**
 * 【文件职责】正式注册I19至I33批准建筑的控制器及独立工艺类型。
 * 【变更记录 #1】2026-10-26 19:57:03（修订177）
 * 删除：无。新增：十台批准控制器、真实发电标识及固定电压定义。
 * 修改：禁翻转和扩展朝向，不生成百万方块JEI形状；完整HTML预览继续独立提供。
 * 用途：接入正式成型与工作仓，保留暂定配方、世界泡任务和生存获取未验收边界。
 * 【变更记录 #2】2026-10-26 21:57:03（修订178）
 * 删除：将十台机器排除出游戏内结构信息的预览禁用标记。
 * 新增：从正式模板无损生成的完整形状及世界投影注册。
 * 修改：形状按所选机器懒读取紧凑流，普通状态共享；用途：恢复完整游戏预览而不改成型建筑。
 * 【变更记录 #3】2026-10-26 22:36:20（修订179）
 * 删除：仅依赖构建器收集形状的绑定；新增：注册完成后显式设置完整形状供应器。
 * 修改：采用既有I02的setShapes口径并保留Pattern完整回退；用途：阻止单主控占位进入预览。
 * 【变更记录 #4】2026-10-27（修订180）
 * 删除：正式注册止于I28的限制；新增：I29至I33批准V1及五套独立三态材质。
 * 修改：复用完整巨构Pattern与显式预览供应器；用途：接入第8批，暂定工艺及世界泡任务仍关闭。
 */
/**
 * 【变更记录 #5】2026-10-27 22:31:22（第5次备注 · 内测5修订181）
 * - 删除：无，原15台正式控制器的身份、电压、形状与材质地址保留。
 * - 新增：batch09五台获批控制器、对应电压以及各自修订181三态材质地址。
 * - 修改：新增设备复用严格原位Pattern和完整紧凑预览，I37不注册。
 * - 用途：批准建筑进入正式游戏入口；暂定工艺、未实现任务与生存配方仍不开放。
 */
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
        var definition = Hk3Gtl.REGISTRATE.multiblock(name, holder -> key.equals("i34")
                ? new com.sirin.hk3gtl.common.machine.tree.Hk3TreeObservationMachine(holder)
                : new Hk3LateIndustrialMachine(holder, role))
                .tier(tier).rotationState(RotationState.NON_Y_AXIS)
                .generator(Hk3ResearchProcessEnergy.isGenerator(role))
                .allowFlip(false).allowExtendedFacing(false)
                .recipeType(Hk3ResearchProcessTypes.get(role)).noRecipeModifier()
                .appearanceBlock(() -> Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3LateIndustrialPatterns.create(def, key))
                .multiblockPreviewRenderer(true, true)
                .workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/" + key
                        + (Integer.parseInt(key.substring(1)) >= 40 ? "_unique_r182"
                        : Integer.parseInt(key.substring(1)) >= 34 ? "_unique_r181"
                        : Integer.parseInt(key.substring(1)) >= 29 ? "_unique_r180" : "_unique_r178")))
                .tooltips(Component.translatable("hk3gtl.machine.late_industry.structure_ready"),
                        Component.translatable("hk3gtl.machine.industrial_extension.provisional_locked"),
                        Component.translatable("hk3gtl.machine.industrial_extension.survival_unverified"))
                .register();
        definition.setShapes(() -> java.util.List.of(Hk3LargeArchitectureShapes.create(definition, key)));
        if (MACHINES.putIfAbsent(key, definition) != null)
            throw new IllegalStateException("高阶控制器重复注册：" + key);
    }
}
