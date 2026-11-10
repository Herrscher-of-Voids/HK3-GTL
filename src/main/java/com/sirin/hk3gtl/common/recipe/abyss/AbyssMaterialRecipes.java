package com.sirin.hk3gtl.common.recipe.abyss;


/**
 * 【文件职责】
 * - 负责 AbyssMaterialRecipes 对应的配方注册与门槛绑定。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.function.Consumer;

/**
 * 海渊功能性中间件（AbyssFunctionalItems）的生产配方。
 * 这些中间件是高级多方块控制器和配方的关键材料。
 *
 * <h3>涵盖中间件</h3>
 * 能量调制器、数据核心、稳定框架、反应堆芯、测量阵列、
 * 反应堆稳定器、天工开物核心（天命系）、逆熵虚数核心（反熵系）。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>所有配方使用 GT 原版组装机（ASSEMBLER_RECIPES），配方ID前缀 "hk3gtl_" 防冲突</li>
 *   <li>修改电压：调整顶部 AB1/AB2/AB3_EUT 常量</li>
 *   <li>修改物品数量：改 new ItemStack(..., 数量) 的第二参数</li>
 *   <li>修改流体量：改 .getFluid(mB值)</li>
 *   <li>修改工时：改 .duration(tick)，20tick = 1秒</li>
 *   <li>科研门控：Hk3RecipeResearchGate.bind() 绑定研究ID，改解锁条件在此修改</li>
 *   <li>禁止用 GTValues.V[15+]，int 溢出！必须用 Hk3Values.VA_LONG[]</li>
 * </ul>
 */
/**
 * 【变更记录 #2】2026-09-25 03:59:11（第 2 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：电路输入使用本等级标签，允许不同系列替代；输出、材料成本及研究门槛保持明确。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #3】2026-09-30 02:17:47（第3次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public class AbyssMaterialRecipes {

    /** 海渊I 电压 (Tier 15)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1] */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];
    /** 海渊II 电压 (Tier 16)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2] */
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.HCV];
    /** 海渊III 电压 (Tier 17)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3] */
    private static final long AB3_EUT = Hk3Values.VA_LONG[Hk3Tiers.HRV];

    /**
     * 注册所有海渊功能中间件配方。
     * 新增中间件配方在方法体末尾追加，格式参照已有配方。
     */
    public static void register(Consumer<FinishedRecipe> provider) {

        // ── 海渊能量调制器：能源类多方块核心部件 ──
        // 力场发生器AB1×32 + 稳定崩坏晶体×128 + 海渊I电路×32 + 魂钢板×512 + 液态崩坏能9216mB → 能量调制器×2 | AB1电压 | 60秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_energy_modulator")
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_HBV.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 32)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 海渊数据核心：研究/数据类多方块核心 ──
        // 传感器AB1×32 + 发射器AB1×32 + 凝视缓冲×32 + 海渊I电路×64 + 液态崩坏能4608mB → 数据核心×2 | AB1电压 | 50秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_data_core")
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_HBV.get(), 32))
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_HBV.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 32))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 64)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 海渊稳定框架：结构类多方块核心 ──
        // 魂钢框架×256 + 电动活塞AB1×32 + 崩坏能晶体×256 + 海渊I电路×32 → 稳定框架×2 | AB1电压 | 50秒
        // 科研门控：需完成 R-AB-006
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_stable_frame")
                .inputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_HBV.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 32)
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_STABLE_FRAME.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_abyss_stable_frame", List.of("RN-RAT"));

        // ── 海渊反应堆芯：反应堆系列核心 ──
        // 压缩核心×64 + 能量调制器×8 + 海渊II电路×64 + 魂钢板×1024 + 液态崩坏能18432mB → 反应堆芯×1 | AB2电压 | 100秒
        // 科研门控：需完成 R-AB-015
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_reactor_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 8))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(16), 64)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_REACTOR_CORE.get(), 1))
                .duration(2000)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_abyss_reactor_core", List.of("RN-FRP"));

        // ── 海渊测量阵列：检测/分析类核心 ──
        // 传感器AB1×64 + 相位镜×16 + 数据核心×4 + 海渊II电路×32 → 测量阵列×1 | AB2电压 | 70秒
        // 科研门控：需完成 R-AB-013
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_measurement_array")
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_HBV.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 4))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(16), 32)
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY.get(), 1))
                .duration(1400)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_abyss_measurement_array", List.of("RN-DMT"));

        // ── 反应堆稳定器 ──
        // 环磁体×8 + 能量调制器×4 + 超导金属氢×64 + 海渊II电路×32 + 液态崩坏能9216mB → 稳定器×1 | AB2电压 | 80秒
        // 科研门控：需完成 R-AB-014
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_reactor_stabilizer")
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 8))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 64))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(16), 32)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.REACTOR_STABILIZER.get(), 1))
                .duration(1600)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_reactor_stabilizer", List.of("RN-FRP", "RN-SMR"));

        // ── 天工开物核心（虚数核心 - 天命系）──
        // 压缩核心×128 + 远古遗产×4 + 海渊III电路×32 + 数据核心×8 + 液态崩坏能18432mB → 天命虚数核心×1 | AB3电压 | 180秒
        // 科研门控：需完成 R-AB-019
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_schicksal_imaginary_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 4))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(17), 32)
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 1))
                .duration(3600)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_schicksal_imaginary_core", List.of("RN-CCE"));

        // ── 逆熵虚数核心（反熵系）──
        // 压缩核心×128 + 远古意志×2 + 海渊III电路×32 + 能量调制器×8 + 液态崩坏能18432mB → 逆熵核心×1 | AB3电压 | 180秒
        // 科研门控：需完成 R-AB-020
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_anti_entropy_imaginary_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 2))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(17), 32)
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 1))
                .duration(3600)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_anti_entropy_imaginary_core", List.of("RN-CCE", "RN-CPT"));
    }
}

// 【变更记录 · 修订163】2026-10-17 15:05:46：移除本类生产配方对旧 R-* 研究的活动绑定，按现行电路平台或功能前级明确绑定 RN 课题；多前置全部保留。输入输出、数量、耗电与时长不变；本轮接线不代表全部工业工艺或百课题已完成实机验收。
