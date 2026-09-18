package com.sirin.hk3gtl.common.recipe.honkai;



import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.data.GTLItems;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.function.Consumer;

/**
 * 核心材料生产配方。
 * 为所有已注册但缺少来源的 HonkaiMaterialItems 提供合成路线。
 *
 * <h3>涵盖材料</h3>
 * 稳定崩坏能晶体、压缩崩坏能核心、燃料棒、抑制剂、
 * 流体合金、纳米陶瓷、相位镜、爱因斯坦环磁体、超导金属氢、
 * 定向魂钢构件、远古遗产、远古意志等。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>修改电压：调整顶部 EUT 常量，或在具体配方中直接改 .EUt()</li>
 *   <li>修改物品数量：改 new ItemStack(..., 数量) 或 .asStack(数量) 的第二参数</li>
 *   <li>修改流体量：改 .getFluid(mB值)</li>
 *   <li>修改工时：改 .duration(tick)，20tick = 1秒</li>
 *   <li>配方ID前缀 "hk3gtl_" 用于 GT 原版 RecipeType，避免ID冲突</li>
 *   <li>使用自定义 RecipeType（如 HONKAI_CONDENSATION）的配方无需前缀</li>
 *   <li>禁止用 GTValues.V[15+]，int 溢出！必须用 Hk3Values.VA_LONG[]</li>
 * </ul>
 */
public class HonkaiMaterialRecipes {

    /** MAX 电压 (Tier 14)，用于基础中间材料。改数值 → Hk3Values.VA_LONG[GTValues.MAX] */
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    /** 海渊I 电压 (Tier 15)，用于进阶材料。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1] */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** 海渊II 电压 (Tier 16)，用于高端材料。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2] */
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];

    /**
     * 注册所有崩坏能核心材料配方。
     * 新增材料配方直接在方法体末尾追加即可。
     */
    public static void register(Consumer<FinishedRecipe> provider) {

        // ── 稳定崩坏能晶体：凝结器高压结晶 ──
        // 崩坏能晶体×512 + 原始崩坏粒子×1024 + 编程电路#3 → 稳定崩坏能晶体×16 | AB1电压 | 45秒
        Hk3RecipeTypes.HONKAI_CONDENSATION_RECIPES.recipeBuilder("stabilized_crystal")
                .circuitMeta(3)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 1024))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 16))
                .duration(900)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 压缩崩坏能核心：凝结器二阶压缩 ──
        // 稳定崩坏能晶体×128 + 崩坏能晶体×256 + 编程电路#4 → 压缩崩坏能核心×4 | AB1电压 | 60秒
        Hk3RecipeTypes.HONKAI_CONDENSATION_RECIPES.recipeBuilder("compressed_honkai_core")
                .circuitMeta(4)
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 4))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 崩坏能燃料棒：GT组装机 ──
        // 崩坏能晶体×256 + 魂钢杆×128 + 魂钢板×64 + 液态崩坏能4608mB → 燃料棒×4 | AB1电压 | 40秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 4))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 高密度崩坏能燃料棒：GT组装机 ──
        // 燃料棒×16 + 压缩核心×8 + 魂钢板×128 + 液态崩坏能9216mB → 高密度燃料棒×2 | AB1电压 | 50秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_dense_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 崩坏能抑制剂：GT化学反应器 ──
        // 原始崩坏粒子×512 + Shirabon粉×64 + 液态崩坏能2000mB → 抑制剂×4 | MAX电压 | 30秒
        GTRecipeTypes.CHEMICAL_RECIPES.recipeBuilder("hk3gtl_honkai_suppressant")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        // ── 流体合金：GT组装机 ──
        // Shirabon锭×128 + Magmatter锭×64 + 魂钢锭×128 + 液态崩坏能2304mB → 流体合金×8 | AB1电压 | 40秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_fluid_alloy")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Shirabon, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 64))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 8))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 流体合金块：GT压缩机，9合1 ──
        // 流体合金×9 → 流体合金块×1 | AB1电压 | 10秒
        GTRecipeTypes.COMPRESSOR_RECIPES.recipeBuilder("hk3gtl_fluid_alloy_block")
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 9))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1))
                .duration(200)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 纳米陶瓷：GT组装机 ──
        // Shirabon粉×128 + 原始崩坏粒子×512 + 神经处理器×64 → 纳米陶瓷×8 | MAX电压 | 30秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_nano_ceramic")
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(64))
                .outputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 8))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        // ── 相位转移镜：GT组装机 ──
        // 纳米陶瓷×16 + 传感器MAX×16 + 发射器MAX×16 + Shirabon板×64 → 相位镜×2 | AB1电压 | 45秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_phase_transfer_mirror")
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16))
                .inputItems(GTLItems.SENSOR_MAX.asStack(16))
                .inputItems(GTLItems.EMITTER_MAX.asStack(16))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 64))
                .outputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 2))
                .duration(900)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 爱因斯坦环磁体：GT组装机 ──
        // 魂钢环×256 + 超导金属氢×16 + 力场发生器MAX×8 + 海渊I电路×32 → 环磁体×2 | AB1电压 | 60秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_einstein_ringmagnet")
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 32))
                .outputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 超导金属氢：GT组装机 ──
        // Magmatter锭×128 + Shirabon细线×512 + 崩坏能晶体×256 → 超导金属氢×4 | MAX电压 | 45秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_superconductive_metal_hydrogen")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTLMaterials.Shirabon, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 4))
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);

        // ── 定向魂钢构件：GT组装机 ──
        // 魂钢板×256 + 魂钢杆×128 + 稳定魂钢原质×64 + 崩坏能晶体×128 + 海渊I电路×16 + 液态崩坏能4608mB → 定向魂钢构件×8 | AB1电压 | 50秒
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_oriented_soulium_component")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 8))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 远古遗产：虚空万藏深层解析 ──
        // 虚空万藏(不消耗) + 前文明碎片×128 + 崩坏能晶体×512 → 远古遗产×1 | AB1电压 | 180秒
        Hk3RecipeTypes.VOID_ARCHIVES_ANALYSIS_RECIPES.recipeBuilder("ancient_legacy_extraction")
                .notConsumable(new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get()))
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 1))
                .duration(3600)
                .EUt(AB1_EUT)
                .save(provider);

        // ── 远古意志：理构重建阵列提炼，最高阶材料 ──
        // 远古遗产×8 + 压缩核心×64 + 海渊II电路×64 + 液态崩坏能18432mB → 远古意志×1 | AB2电压 | 240秒
        Hk3RecipeTypes.REASON_RECONSTRUCTION_RECIPES.recipeBuilder("ancient_will_synthesis")
                .inputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 1))
                .duration(4800)
                .EUt(AB2_EUT)
                .save(provider);
    }
}
