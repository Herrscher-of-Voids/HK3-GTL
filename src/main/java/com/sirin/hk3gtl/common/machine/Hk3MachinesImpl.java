package com.sirin.hk3gtl.common.machine;

/** 【控制器材质变更 · 修订178】2026-10-26 22:02:44：按负责人“采用32套候选，保留4套原材质”接入独立三态面板；保留既有四套像素，不改建筑、控制器ID或工艺。 */

/** 【变更记录 · 修订177】2026-10-26 19:57:03：在既有工业注册链正式接入I19至I28控制器、批准Pattern和独立执行器；不开放暂定工况。 */
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */

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

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:42:00（内测5修订66）
 * 删除：旧采集/冷凝控制器对新版全工艺的关联；保留注册与旧存档实体。
 * 新增：燃料调配、探测器校准和浓缩精制控制器，专用工艺类型与新逐格布局。
 * 修改：离心、稳定、再生改用真实实验结算机器；I01/I02结构定义保持不变。
 * 用途：按设备隔离配方，避免通用处理器绕过整条工业线。
 *
 * 【变更记录 #2】2026-09-24 18:56:36（内测5修订67）
 * 删除：I01 及液态线控制器继续使用洁净不锈钢外观和未分级的默认机器渲染。
 * 新增：第一条工业线控制器统一使用海渊能源机壳外观，并显式标记 MAX 电压等级。
 * 修改：I01/I02 的 Pattern 几何与端口数量保持兼容，I03/I04/I05/I06/I07/I17 使用 MAX 海渊结构材料。
 * 用途：不破坏已经确认的 I01/I02 建筑坐标，同时消除控制器与新结构之间的视觉和等级割裂。
 */
/**
 * 【变更记录 #3】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
/**
 * 【变更记录 #4】2026-09-27 02:38:43（第 4 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：两台主控改用已存在的内测5控制器外壳纹理与GT MAX外观块，保留注册ID及工作覆盖层。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #5】2026-09-27 03:06:43（第 5 次备注 · 内测5修订88）
 * 删除：无，保留历史说明和原有结构几何。
 * 新增：六台采用统一控制器侧面材质的机器，其成型仓室外观同步使用接口机械方块。
 * 修改：接入工业接口机械方块；保留必要能力的全局数量约束。
 * 用途：让多余接口可以封闭，不用填充方块冒充真实仓室能力。
 */
/**
 * 【变更记录 #6】2026-10-01 21:41:57（第6次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：删除旧注册与字段；仅调用仍有内测5机器的初始化模块。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
/**
 * 【变更记录 #7】2026-10-15 01:12:48（内测5修订156）。
 * 删除：批准工业入口对旧几何及待接工艺类型的依赖。
 * 新增：I13 主控及 I01 分阶工艺；修改：工业精确 Pattern、研究所扩建注册。
 * 用途：把本轮批准建筑接入实际能力、既有权限与无线供能，不视为游戏成型验收。
 */
/**
 * 【变更记录 #8】2026-10-15 02:00:40（内测5修订157）
 * 删除：批准入口使用完整空气体积生成预览候选对象的默认路径。
 * 新增：正式 NBT 显式形状供应器，保留 JEI 及世界结构预览。
 * 修改：I01 四阶、I02–I13 和一阶研究所接入共享普通状态与兼容空气表示。
 * 用途：减少预览内存，不改变完整 Pattern、严格空气、批准建筑、配方或注册顺序。
 */
/**
 * 【变更记录 #9】2026-10-23 13:35:32（第9次备注 · 内测5修订175）
 * - 删除：I17对旧液态布局和退役海渊机壳的正式引用。
 * - 新增：I14/I15/I16/I18四个批准控制器初始化入口。
 * - 修改：I17沿用原注册ID与MAX浓缩类型，Pattern和JEI转到批准融合置中V2。
 * - 用途：新建筑具备真实成型入口；暂定计划关闭，控制器生存获取仍单列未验收。
 */
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

    // 中文维护备注：历史说明已整理；当前实现以代码为准。

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    /** 中文说明：该处说明已按当前代码行为整理。*/
    /** 一阶研究所，使用既有研究矩阵结构和独立研究任务结算。 */
    public static MultiblockMachineDefinition ABYSS_RESEARCH_ANALYSIS_MATRIX;

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static ResourceLocation casingTex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static void init() {
        long started = System.nanoTime();
        com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.init();
        try {
            com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartMachines.init();
        } catch (Exception e) {
            throw new IllegalStateException("HK3GTL接口部件注册失败", e);
        }

        try {


        // 中文维护备注：历史说明已整理；当前实现以代码为准。
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
                        new ResourceLocation("hk3gtl", "block/overlay/i01_v2"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.1"),
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.2"))
                .register();

        I01_2_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_2_honkai_collection_tower", "i01_2");
        I01_3_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_3_honkai_collection_tower", "i01_3");
        I01_4_HONKAI_COLLECTION_TOWER = collectionUpgrade("i01_4_honkai_collection_tower", "i01_4");

        // 内测5液态分馏中心：连接采集液、分析样本和分离滤芯。
        // 中文备注：该处说明已按当前代码行为整理。
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
                        new ResourceLocation("hk3gtl", "block/overlay/i03_v2"))
                .tooltips(
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.0"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.1"),
                        Component.translatable("hk3gtl.machine.liquid_honkai_fractionation_center.tooltip.2"))
                .register();

        // 中文备注：该处说明已按当前代码行为整理。
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
                        Component.translatable("hk3gtl.machine.liquid_honkai_stabilization_tower.tooltip.2"))
                .register();

        // 中文备注：该处说明已按当前代码行为整理。
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
                        Component.translatable("hk3gtl.machine.stabilization_medium_regeneration_tower.tooltip.2"))
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
        // 2026-10-29：负责人指定Azu礼堂作为W01，接入完整实体成型，不开放生产或接口。
        Hk3W01Machines.init();
        com.sirin.hk3gtl.common.machine.w02.Hk3W02Machines.init();
        com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachines.init();
        com.sirin.hk3gtl.common.machine.w03.Hk3W03Machines.init();





        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
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
                        new ResourceLocation("hk3gtl", "block/overlay/s01_v2"))
                .tooltips(
                        Component.translatable("hk3gtl.research.lab.tooltip"))
                .register();
        com.sirin.hk3gtl.common.machine.research.Hk3ResearchMachines.initInstitutes(ABYSS_RESEARCH_ANALYSIS_MATRIX);

        // 中文备注：该处说明已按当前代码行为整理。
        Hk3MachinesMaxStage.init();
        Hk3MachinesAbyssStage.init();
        // I02 沿用阶段模块的注册入口，仅在原有初始化之后指定惰性正式模板预览。
        var spectrum = Hk3MachinesAbyssStage.I02_SPECTRUM_ANALYSIS_ARRAY;
        spectrum.setShapes(() -> java.util.List.of(Hk3ApprovedArchitectureShapes.create(spectrum, "i02")));

        // 保持后续阶段的既有注册顺序。

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        LOGGER.info("[HK3GTL] 批准工业及研究入口初始化完成，耗时={}ms",
                (System.nanoTime() - started) / 1_000_000L);
        } catch (Exception e) {
            throw new IllegalStateException("HK3GTL机器注册失败，不能以缺失工业线继续启动",e);
        }
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
                .tooltips(Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.i01_honkai_collection_tower.tooltip.1"))
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
                        Component.translatable("hk3gtl.machine." + name + ".tooltip.1"))
                .register();
    }

}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
