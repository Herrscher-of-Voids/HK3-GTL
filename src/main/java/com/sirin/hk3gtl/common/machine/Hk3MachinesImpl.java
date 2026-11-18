package com.sirin.hk3gtl.common.machine;




import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;



import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchMatrixMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ResearchMatrixPattern;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3IndustrialApprovedPatterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitectureShapes;

import com.gregtechceu.gtceu.api.GTValues;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

import org.slf4j.Logger;
import com.mojang.logging.LogUtils;





























































public class Hk3MachinesImpl {
    public static MultiblockMachineDefinition I01_HONKAI_COLLECTION_TOWER;
    public static MultiblockMachineDefinition I01_2_HONKAI_COLLECTION_TOWER;
    public static MultiblockMachineDefinition I01_3_HONKAI_COLLECTION_TOWER;
    public static MultiblockMachineDefinition I01_4_HONKAI_COLLECTION_TOWER;
    /** 液态崩坏能分馏中心。 */
    public static MultiblockMachineDefinition LIQUID_HONKAI_FRACTIONATION_CENTER;
    /** 液态崩坏能稳定塔。 */
    public static MultiblockMachineDefinition LIQUID_HONKAI_STABILIZATION_TOWER;
    /** 稳定介质再生塔。 */
    public static MultiblockMachineDefinition STABILIZATION_MEDIUM_REGENERATION_TOWER;
    public static MultiblockMachineDefinition HONKAI_FUEL_BLENDING_PLANT;
    public static MultiblockMachineDefinition HONKAI_DETECTOR_CALIBRATION_BENCH;
    public static MultiblockMachineDefinition IMITATION_CORE_CRYSTALLIZATION_CHAMBER;
    public static MultiblockMachineDefinition SOULIUM_PRECURSOR_MIXING_KETTLE;
    public static MultiblockMachineDefinition NANO_BASIC_UNIT_SYNTHESIZER;
    public static MultiblockMachineDefinition NANOBOT_ASSEMBLY_ARRAY;
    public static MultiblockMachineDefinition NANO_SELF_ORGANIZING_PROGRAMMING_CHAMBER;
    /** I13 崩坏抗性包覆阵列，使用既有包覆工艺和无线玩家电网。 */
    public static MultiblockMachineDefinition I13_HONKAI_RESISTANT_COATING_ARRAY;
    public static MultiblockMachineDefinition HONKAI_FUEL_CONCENTRATION_PLANT;

    private static final Logger LOGGER = LogUtils.getLogger();

    private static GTRegistrate registrate() {
        return Hk3Gtl.REGISTRATE;
    }


    /** 一阶研究所，使用既有研究矩阵结构和独立研究任务结算。 */
    public static MultiblockMachineDefinition ABYSS_RESEARCH_ANALYSIS_MATRIX;


    private static ResourceLocation casingTex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    public static void init() {
        long started = System.nanoTime();
        com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.init();
        if (net.minecraftforge.fml.ModList.get().isLoaded("ae2"))
            com.sirin.hk3gtl.common.machine.ae.Hk3NexusMachines.init();
        com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartMachines.init();
        I01_HONKAI_COLLECTION_TOWER = registrate()
                .multiblock("i01_honkai_collection_tower", Hk3HonkaiAbsorptionMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.COLLECTION)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, "i01"))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "i01"))
                // 2026-09-25：采用独立雷达面板与统一新机壳贴图；不改变结构校验及采集工艺。
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i01_appearance_0002_r7"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.1"),
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.2"))
                .register();

        I01_2_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_2_honkai_collection_tower", "i01_2");
        I01_3_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_3_honkai_collection_tower", "i01_3");
        I01_4_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_4_honkai_collection_tower", "i01_4");

        // 内测5液态分馏中心：连接采集液、分析样本和分离滤芯。
        LIQUID_HONKAI_FRACTIONATION_CENTER = registrate()
                .multiblock("liquid_honkai_fractionation_center", com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.LIQUID_REFINING)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, "i03"))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "i03"))
                // 2026-09-25：分馏分支图标区分液态处理设备，空闲、运行和暂停使用对应贴图。
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i03_appearance_0002_r7"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.0"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.1"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();

        // 内测5稳定塔：将母液与稳定介质转化为稳定液体。
        LIQUID_HONKAI_STABILIZATION_TOWER = registrate()
                .multiblock("liquid_honkai_stabilization_tower", com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.STABILIZATION)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, "i04"))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "i04"))
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i04_unique_r178"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.liquid_honkai_stabilization_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_stabilization_tower.tooltip.1"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_stabilization_tower.tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();

        // 内测5介质再生塔：回收废稳定介质并隔离不可逆损失。
        STABILIZATION_MEDIUM_REGENERATION_TOWER = registrate()
                .multiblock("stabilization_medium_regeneration_tower", com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3IndustrialRecipeTypes.REGENERATION)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, "i05"))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "i05"))
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/i05_unique_r178"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.stabilization_medium_regeneration_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.stabilization_medium_regeneration_tower.tooltip.1"),
                        Component.translatable("hk3gtl.machine.stabilization_medium_regeneration_tower.tooltip.2"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();

        HONKAI_FUEL_BLENDING_PLANT = approvedMachine("honkai_fuel_blending_plant", Hk3IndustrialRecipeTypes.FUEL_BLENDING, "i06");
        HONKAI_DETECTOR_CALIBRATION_BENCH = approvedMachine("honkai_detector_calibration_bench", Hk3IndustrialRecipeTypes.CALIBRATION, "i07");
        IMITATION_CORE_CRYSTALLIZATION_CHAMBER = approvedMachine("imitation_core_crystallization_chamber",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I08"), "i08",
                Hk3IndustrialRecipeTypes.CORE_CRYSTALLIZATION);
        SOULIUM_PRECURSOR_MIXING_KETTLE = approvedMachine("soulium_precursor_mixing_kettle",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I09"), "i09");
        NANO_BASIC_UNIT_SYNTHESIZER = approvedMachine("nano_basic_unit_synthesizer",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I10"), "i10");
        NANOBOT_ASSEMBLY_ARRAY = approvedMachine("nanobot_assembly_array",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I11"), "i11");
        NANO_SELF_ORGANIZING_PROGRAMMING_CHAMBER = approvedMachine("nano_self_organizing_programming_chamber",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I12"), "i12");
        I13_HONKAI_RESISTANT_COATING_ARRAY = approvedMachine("i13_honkai_resistant_coating_array",
                com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I13"), "i13");
        HONKAI_FUEL_CONCENTRATION_PLANT = Hk3IndustrialExtensionMachines.registerConcentration();
        Hk3IndustrialExtensionMachines.init();
        Hk3LateIndustrialMachines.init();

        Hk3W01Machines.init();
        com.sirin.hk3gtl.common.machine.w02.Hk3W02Machines.init();
        com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachines.init();
        com.sirin.hk3gtl.common.machine.w03.Hk3W03Machines.init();
        com.sirin.hk3gtl.common.machine.wonder.Hk3WonderMachines.init();





        ABYSS_RESEARCH_ANALYSIS_MATRIX = registrate()
                .multiblock("abyss_research_analysis_matrix", holder -> new com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine(holder, 1))
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypes.ABYSS_RESEARCH_ANALYSIS_RECIPES)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(Hk3ResearchMatrixPattern::createPattern)
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, "s01"))
                // 2026-09-25：研究网络面板仅更新视觉，不改变玩家背包扣费、研究点或接口能力。
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/s01_appearance_0002_r7"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.0"),
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.1"),
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.2"))
                .register();
        com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.initInstitutes(ABYSS_RESEARCH_ANALYSIS_MATRIX);

        Hk3MachinesMaxStage.init();
        Hk3MachinesAbyssStage.init();
        // I02 沿用阶段模块的注册入口，仅在原有初始化之后指定惰性正式模板预览。
        var spectrum = Hk3MachinesAbyssStage.I02_SPECTRUM_ANALYSIS_ARRAY;
        spectrum.setShapes(() -> java.util.List.of(Hk3ApprovedArchitectureShapes.create(spectrum, "i02")));

        // 保持后续阶段的既有注册顺序。

        LOGGER.info("[HK3GTL] 批准工业及研究入口初始化完成，耗时={}ms",
                (System.nanoTime() - started) / 1_000_000L);
    }

    /** 已批准的四阶扩建保留前阶工艺，并加入本阶既有采集类型。 */
    private static MultiblockMachineDefinition collectionUpgrade(String name, String layout) {
        int stage = Integer.parseInt(layout.substring(4));
        var types = new com.gregtechceu.gtceu.api.recipe.GTRecipeType[stage];
        for (int tier = 1; tier <= stage; tier++)
            types[tier - 1] = com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes.get("I01-" + tier);
        return registrate().multiblock(name, Hk3HonkaiAbsorptionMachine::new)
                .tier(GTValues.MAX)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeTypes(types)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, layout))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, layout))
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))
                .tooltips(Component.translatable("hk3gtl.machine." + name + ".tooltip.0"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.1"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();
    }

    private static MultiblockMachineDefinition approvedMachine(String name,
            com.gregtechceu.gtceu.api.recipe.GTRecipeType type, String layout,
            com.gregtechceu.gtceu.api.recipe.GTRecipeType... additionalTypes) {
        var types = new com.gregtechceu.gtceu.api.recipe.GTRecipeType[additionalTypes.length + 1];
        types[0] = type;
        System.arraycopy(additionalTypes, 0, types, 1, additionalTypes.length);
        // I08 以后的计划必须使用既有固定工艺身份执行器，不能由普通液态处理器代替。
        return registrate().multiblock(name, holder ->
                        new com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine(holder,
                                layout.toUpperCase(java.util.Locale.ROOT)))
                .tier(GTValues.MAX).rotationState(RotationState.NON_Y_AXIS).recipeTypes(types)
                .appearanceBlock(() -> com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks.require("hk3gtl:industrial_port_casing"))
                .pattern(def -> Hk3IndustrialApprovedPatterns.create(def, layout))
                .shapeInfo(def -> Hk3ApprovedArchitectureShapes.create(def, layout))
                .workableCasingRenderer(casingTex("industrial_controller_shell"),
                        new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))
                .tooltips(Component.translatable("hk3gtl.machine." + name + ".tooltip.0"),
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.1"),
                        Component.translatable("hk3gtl.machine.controller.research_required"))
                .register();
    }

}


