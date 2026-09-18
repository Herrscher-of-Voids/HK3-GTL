package com.sirin.hk3gtl.common.recipe.abyss;



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
public class AbyssMaterialRecipes {

    /** 海渊I 电压 (Tier 15)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1] */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** 海渊II 电压 (Tier 16)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2] */
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];
    /** 海渊III 电压 (Tier 17)。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3] */
    private static final long AB3_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3];

    /**
     * 注册所有海渊功能中间件配方。
     * 新增中间件配方在方法体末尾追加，格式参照已有配方。
     */
    public static void register(Consumer<FinishedRecipe> provider) {

        // ── 海渊能量调制器：能源类多方块核心部件 ──
        // 力场发生器AB1×32 + 稳定崩坏晶体×128 + 海渊I电路×32 + 魂钢板×512 + 液态崩坏能9216mB → 能量调制器×2 | AB1电压 | 60秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_energy_modulator")
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_1.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 32))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 海渊数据核心：研究/数据类多方块核心 ──
        // 传感器AB1×32 + 发射器AB1×32 + 凝视缓冲×32 + 海渊I电路×64 + 液态崩坏能4608mB → 数据核心×2 | AB1电压 | 50秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_data_core")
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_1.get(), 32))
                .inputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_1.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 32))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 64))
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
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_1.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 32))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_STABLE_FRAME.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_abyss_stable_frame", "R-AB-006");

        // ── 海渊反应堆芯：反应堆系列核心 ──
        // 压缩核心×64 + 能量调制器×8 + 海渊II电路×64 + 魂钢板×1024 + 液态崩坏能18432mB → 反应堆芯×1 | AB2电压 | 100秒
        // 科研门控：需完成 R-AB-015
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_reactor_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 64))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_REACTOR_CORE.get(), 1))
                .duration(2000)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_abyss_reactor_core", "R-AB-015");

        // ── 海渊测量阵列：检测/分析类核心 ──
        // 传感器AB1×64 + 相位镜×16 + 数据核心×4 + 海渊II电路×32 → 测量阵列×1 | AB2电压 | 70秒
        // 科研门控：需完成 R-AB-013
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_measurement_array")
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_1.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 4))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY.get(), 1))
                .duration(1400)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_abyss_measurement_array", "R-AB-013");

        // ── 反应堆稳定器 ──
        // 环磁体×8 + 能量调制器×4 + 超导金属氢×64 + 海渊II电路×32 + 液态崩坏能9216mB → 稳定器×1 | AB2电压 | 80秒
        // 科研门控：需完成 R-AB-014
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_reactor_stabilizer")
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 8))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 64))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.REACTOR_STABILIZER.get(), 1))
                .duration(1600)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_reactor_stabilizer", "R-AB-014");

        // ── 天工开物核心（虚数核心 - 天命系）──
        // 压缩核心×128 + 远古遗产×4 + 海渊III电路×32 + 数据核心×8 + 液态崩坏能18432mB → 天命虚数核心×1 | AB3电压 | 180秒
        // 科研门控：需完成 R-AB-019
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_schicksal_imaginary_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 4))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 32))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 1))
                .duration(3600)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_schicksal_imaginary_core", "R-AB-019");

        // ── 逆熵虚数核心（反熵系）──
        // 压缩核心×128 + 远古意志×2 + 海渊III电路×32 + 能量调制器×8 + 液态崩坏能18432mB → 逆熵核心×1 | AB3电压 | 180秒
        // 科研门控：需完成 R-AB-020
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_anti_entropy_imaginary_core")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 2))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 32))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 1))
                .duration(3600)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_anti_entropy_imaginary_core", "R-AB-020");
    }
}
