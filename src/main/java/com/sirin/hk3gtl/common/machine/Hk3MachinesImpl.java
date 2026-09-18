package com.sirin.hk3gtl.common.machine;




import com.gregtechceu.gtceu.api.data.RotationState;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.Hk3Gtl;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchMatrixMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3P1Patterns;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ResearchMatrixPattern;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;

import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 多方块注册总入口。
 *
 * 当前职责：
 * - 定义所有已正式注册的多方块控制器
 * - 绑定对应的 RecipeType
 * - 绑定当前使用的结构 Pattern
 * - 配置展示方块与基础 Tooltip
 *
 * 注意：
 * - 当前大部分多方块仍处于“联调优先”阶段，因此结构可能临时统一为泥土 3x3x3 立方体。
 * - 真正的正式结构保留在 pattern 包中，后续恢复时优先切回对应 pattern provider。
 */
public class Hk3MachinesImpl {

    private static final Logger LOGGER = LogUtils.getLogger();

    private static GTRegistrate registrate() {
        return Hk3Gtl.REGISTRATE;
    }

    // ── P1 核心 4 台（配方类型 → Hk3RecipeTypesImpl 中定义）──

    /** 崩坏能吸收塔 | 配方: HONKAI_ABSORPTION | IO(物入/物出/液入/液出): 1/1/0/0 | 机壳: casing_abyss_energy */
    public static MultiblockMachineDefinition HONKAI_ABSORPTION_TOWER;
    /** 崩坏能结晶器 | 配方: HONKAI_CONDENSATION | IO: 2/2/0/1 | 机壳: casing_abyss_energy */
    public static MultiblockMachineDefinition HONKAI_CRYSTAL_CONDENSER;
    /** 魂钢冶炼炉 | 配方: SOULIUM_SMELTING | IO: 4/4/1/0 | 机壳: casing_soulium */
    public static MultiblockMachineDefinition SOULIUM_SMELTERY;
    /** 海渊研究分析矩阵 | 配方: ABYSS_RESEARCH_ANALYSIS | IO: 4/1/0/0 | 机壳: casing_abyss_research */
    public static MultiblockMachineDefinition ABYSS_RESEARCH_ANALYSIS_MATRIX;

    /**
     * 初始化所有多方块。
     *
     * 这里的顺序按“已启用控制器”组织：
     * - 先 P1 三台核心机
     * - 再 P2 研究矩阵
     *
     * 后续若继续扩机器，建议继续保持“按阶段/主线设备”分组书写，
     * 避免注册类重新变成不可读的大文件。
     */
    private static final ResourceLocation OVERLAY = new ResourceLocation(Hk3Constants.MOD_ID, "block/overlay/default_set");

    /** 机壳贴图路径助手，返回 hk3gtl:block/casings/<name> */
    private static ResourceLocation casingTex(String name) {
        return new ResourceLocation(Hk3Constants.MOD_ID, "block/casings/" + name);
    }

    /**
     * 初始化所有多方块控制器。
     * 调用顺序：P1 核心 4 台 → Max 阶段 → 海渊 → 虚数 → 量子 → 终焉 → 奇观。
     * 新增阶段在此追加子类 init() 调用即可。
     */
    public static void init() {
        long started = System.nanoTime();
        try {
            com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartMachines.init();
        } catch (Exception e) {
            LOGGER.error("[HK3GTL] Hk3PartMachines.init() 失败", e);
        }

        try {
        HONKAI_ABSORPTION_TOWER = registrate()
                .multiblock("honkai_absorption_tower", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.NON_Y_AXIS)
                .recipeType(Hk3RecipeTypes.HONKAI_ABSORPTION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)
                .pattern(Hk3P1Patterns::createAbsorptionTower)
                .workableCasingRenderer(casingTex("casing_abyss_energy"), OVERLAY)
                .tooltips(
                        Component.translatable("hk3gtl.machine.honkai_absorption_tower.tooltip.0"),
                        Component.translatable("hk3gtl.machine.honkai_absorption_tower.tooltip.1"))
                .register();

        HONKAI_CRYSTAL_CONDENSER = registrate()
                .multiblock("honkai_crystal_condenser", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.HONKAI_CONDENSATION_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_ENERGY)
                .pattern(Hk3P1Patterns::createCrystalCondenser)
                .workableCasingRenderer(casingTex("casing_abyss_energy"), OVERLAY)
                .tooltips(
                        Component.translatable("hk3gtl.machine.honkai_crystal_condenser.tooltip.0"),
                        Component.translatable("hk3gtl.machine.honkai_crystal_condenser.tooltip.1"))
                .register();

        SOULIUM_SMELTERY = registrate()
                .multiblock("soulium_smeltery", Hk3WorkableMultiblockMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.SOULIUM_SMELTING_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_SOULIUM)
                .pattern(Hk3P1Patterns::createSouliumSmeltery)
                .workableCasingRenderer(casingTex("casing_soulium"), OVERLAY)
                .tooltips(
                        Component.translatable("hk3gtl.machine.soulium_smeltery.tooltip.0"),
                        Component.translatable("hk3gtl.machine.soulium_smeltery.tooltip.1"))
                .register();

        // 研究矩阵：专用机器类 + 专用 Pattern（无物品/流体仓、无并行、仅能源仓）
        // 仍保留 recipeType() 调用以避免 GT registrate 要求必填，但机器自己不走 RecipeLogic，
        // 而是由 Hk3ResearchMatrixMachine.onServerTick 全局驱动扣电与推进研究进度。
        ABYSS_RESEARCH_ANALYSIS_MATRIX = registrate()
                .multiblock("abyss_research_analysis_matrix", Hk3ResearchMatrixMachine::new)
                .rotationState(RotationState.ALL)
                .recipeType(Hk3RecipeTypes.ABYSS_RESEARCH_ANALYSIS_RECIPES)
                .appearanceBlock(CasingBlocks.CASING_ABYSS_RESEARCH)
                .pattern(Hk3ResearchMatrixPattern::createPattern)
                .workableCasingRenderer(casingTex("casing_abyss_research"), OVERLAY)
                .tooltips(
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.0"),
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.1"),
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.idle",
                                Hk3Constants.RESEARCH_MATRIX_IDLE_EUT_PER_TICK / 1_000_000L),
                        Component.translatable("hk3gtl.machine.abyss_research_analysis_matrix.tooltip.no_parallel"))
                .register();

        // P2 新增多方块
        Hk3MachinesMaxStage.init();
        Hk3MachinesAbyssStage.init();

        // P3 新增阶段
        Hk3MachinesImaginaryStage.init();
        Hk3MachinesQuantumStage.init();
        Hk3MachinesFinalityStage.init();
        Hk3MachinesWonderStage.init();

        // 对齐多方块结构总表 v0.3：海渊12 + 虚数12 + 量子12 + 终焉12 + 奇观12 = 60
        // 代码分布：Hk3MachinesImpl 持有 4 台 P1 核心，其余在各 Stage 类。
        LOGGER.info("[DEBUG] 多方块机器初始化完成（共 {} 台），耗时={}ms",
                4 + 4 + 4 + 12 + 12 + 12 + 12,
                (System.nanoTime() - started) / 1_000_000L);
        } catch (Exception e) {
            LOGGER.error("[HK3GTL] 多方块机器初始化失败！", e);
        }
    }
}
