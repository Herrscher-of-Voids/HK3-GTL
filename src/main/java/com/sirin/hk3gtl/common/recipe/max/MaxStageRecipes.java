package com.sirin.hk3gtl.common.recipe.max;



import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.data.GTLItems;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.function.Consumer;

/**
 * Max 起始阶段 12 台独立 RecipeType 多方块的配方。
 * 每台 1~3 条核心配方，保证 JEI 有内容、机器可运转。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>修改电压：调整 {@link #MAX_EUT} / {@link #AB1_EUT}，或在具体配方中直接改 .EUt()</li>
 *   <li>修改工时：改各配方的 .duration(tick)，20tick = 1秒</li>
 *   <li>修改输入/输出物品：改 .inputItems() / .outputItems() 的物品类型和数量</li>
 *   <li>修改输入/输出流体：改 .inputFluids() / .outputFluids() 的流体和 mB 值</li>
 *   <li>新增配方：在 register() 中新增方法调用，仿照已有方法编写</li>
 *   <li>配方ID：.recipeBuilder("xxx") 中的字符串，必须全局唯一</li>
 * </ul>
 *
 * <h3>电压策略</h3>
 * <ul>
 *   <li>科研/制造类用 MAX_EUT（Tier 14）</li>
 *   <li>能源产出类 EUt 取负值表示发电（-MAX_EUT / -AB1_EUT）</li>
 *   <li>禁止用 GTValues.V[15+]，int 溢出！必须用 Hk3Values.VA_LONG[]</li>
 * </ul>
 *
 * <h3>变更记录（2026-05-19）</h3>
 * <ul>
 *   <li>删除：MAX 时代已下线机器（如 max_circuit_direct_welder）专属 RecipeType 依赖</li>
 *   <li>新增：将遗留工艺重挂到 v0.3 仍存在的 60 台机器 RecipeType</li>
 *   <li>修改：MAX 阶段残余工艺统一并入 abyss_circuit_foundry / large_honkai_reactor / sea_of_quanta_observatory 等现役机器</li>
 *   <li>用途：清理 130 台时期孤儿配方，避免 JEI 显示无归属工艺</li>
 * </ul>
 */
public class MaxStageRecipes {

    /** MAX 电压 (Tier 14)，用于科研/制造类配方。改数值 → Hk3Values.VA_LONG[GTValues.MAX] */
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    /** 海渊I 电压 (Tier 15)，用于更高阶配方。改数值 → Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1] */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** 瓦尔特馈赠对应的自动研究节点，完成后开放崩坏能电路板构造。 */
    private static final String WALTER_GIFT_RESEARCH = "R-WL-001";
    /** 编程电路 #1~#15 对应 ULV~MAX 崩坏能电路板。 */
    private static final String[] HONKAI_CIRCUIT_TIERS = {
            "ulv", "lv", "mv", "hv", "ev",
            "iv", "luv", "zpm", "uv", "uhv",
            "uev", "uiv", "uxv", "opv", "max"
    };
    /** 每级崩坏能电路板需要的液态崩坏能，按电压等级递增。 */
    private static final int[] HONKAI_CIRCUIT_FLUID_COSTS = {
            144, 288, 576, 1152, 2304,
            4608, 9216, 18432, 36864, 73728,
            147456, 294912, 589824, 1179648, 2359296
    };

    /**
     * 注册所有 Max 阶段配方，由 Hk3RecipeAdderImpl 在数据生成时调用。
     * 新增机器配方时在此添加新方法调用即可。
     */
    public static void register(Consumer<FinishedRecipe> provider) {
        addVoidArchivesAnalysis(provider);
        addMaxCircuitForging(provider);
        addReasonReconstruction(provider);
        addSmallHonkaiReaction(provider);
        addMediumHonkaiReaction(provider);
        addHonkaiEuConversion(provider);
        addAbyssCircuitFoundry(provider);
        addAbyssCasingPress(provider);
        addHonkaiDistillation(provider);
        addSouliumWireDrawing(provider);
        addPrecivilizationDataRecovery(provider);
        addHonkaiEnvironmentSampling(provider);
    }

    // ── 虚空万藏解析室：虚空万藏不消耗，输入EU，输出资料片段 ──

    /**
     * 虚空万藏解析室配方。
     * 修改要点：改产出数量 → outputItems 第二参数；改耗电 → .EUt()；改工时 → .duration()
     */
    private static void addVoidArchivesAnalysis(Consumer<FinishedRecipe> provider) {
        // 基础解析：虚空万藏(不消耗) + 崩坏能晶体×128 → 前文明资料碎片×2 | MAX电压 | 45秒
        Hk3RecipeTypes.VOID_ARCHIVES_ANALYSIS_RECIPES.recipeBuilder("basic_fragment_extraction")
                .notConsumable(new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get()))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 128))
                .outputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 2))
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);

        // 深度解析：虚空万藏(不消耗) + 崩坏能晶体×512 + 海渊I电路×32 → 前文明资料碎片×8 | AB1电压 | 90秒
        Hk3RecipeTypes.VOID_ARCHIVES_ANALYSIS_RECIPES.recipeBuilder("deep_fragment_extraction")
                .notConsumable(new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get()))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 32))
                .outputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 8))
                .duration(1800)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── MAX 电路母锻炉：高效 MAX 级电路批量合成 ──

    /**
     * MAX 电路母锻炉配方。
     * 修改要点：改电路产出量 → outputItems 第二参数；改输入部件 → inputItems 行
     */
    private static void addMaxCircuitForging(Consumer<FinishedRecipe> provider) {
        // 标准批次：神经处理器×512 + 力场发生器MAX×32 + 传感器MAX×32 + Shirabon细线×1024 + 液态崩坏能4608mB → MAX电路×32 | MAX电压 | 60秒
        Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES.recipeBuilder("max_circuit_batch")
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(512))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(32))
                .inputItems(GTLItems.SENSOR_MAX.asStack(32))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTLMaterials.Shirabon, 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(CustomTags.MAX_CIRCUITS, 32)
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);

        // 增强批次：神经处理器×1024 + 力场发生器MAX×64 + 发射器MAX×64 + Magmatter锭×256 + 崩坏能晶体×512 + 液态崩坏能9216mB → MAX电路×64 | AB1电压 | 120秒
        Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES.recipeBuilder("max_circuit_enhanced")
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(1024))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(64))
                .inputItems(GTLItems.EMITTER_MAX.asStack(64))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(CustomTags.MAX_CIRCUITS, 64)
                .duration(2400)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 理构重建阵列：崩坏能电路板 / 理论型中间件合成 ──

    /**
     * 理构重建阵列配方。
     * 修改要点：改凝视缓冲单元产出 → outputItems 第二参数
     */
    private static void addReasonReconstruction(Consumer<FinishedRecipe> provider) {
        addHonkaiCircuitBoardReconstruction(provider);

        // 凝视缓冲单元：传感器MAX×64 + 发射器MAX×64 + Shirabon板×256 + 液态崩坏能4608mB → 凝视缓冲单元×4 | MAX电压 | 60秒
        Hk3RecipeTypes.REASON_RECONSTRUCTION_RECIPES.recipeBuilder("gaze_buffer_unit")
                .inputItems(GTLItems.SENSOR_MAX.asStack(64))
                .inputItems(GTLItems.EMITTER_MAX.asStack(64))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 4))
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);

        // 高级凝视缓冲：凝视缓冲×16 + 稳定崩坏晶体×128 + 海渊I电路×32 + 液态崩坏能9216mB → 高级凝视缓冲×2 | AB1电压 | 80秒
        Hk3RecipeTypes.REASON_RECONSTRUCTION_RECIPES.recipeBuilder("advanced_gaze_buffer")
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 2))
                .duration(1600)
                .EUt(AB1_EUT)
                .save(provider);
    }

    /**
     * 瓦尔特馈赠后开放的崩坏能电路板构造。
     * 修改要点：改 HONKAI_CIRCUIT_FLUID_COSTS 调整各电压等级成本；改 circuitMeta 映射需同步注释。
     */
    private static void addHonkaiCircuitBoardReconstruction(Consumer<FinishedRecipe> provider) {
        for (int i = 0; i < HONKAI_CIRCUIT_TIERS.length; i++) {
            String tier = HONKAI_CIRCUIT_TIERS[i];
            int circuitMeta = i + 1;
            String recipeId = "honkai_circuit_" + tier + "_reconstruction";

            // 编程电路#circuitMeta + 液态崩坏能 → 对应电压等级崩坏能电路板×1 | MAX电压 | 随等级递增耗时
            Hk3RecipeTypes.REASON_RECONSTRUCTION_RECIPES.recipeBuilder(recipeId)
                    .circuitMeta(circuitMeta)
                    .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(HONKAI_CIRCUIT_FLUID_COSTS[i]))
                    .outputItems(new ItemStack(Hk3CircuitItems.getHonkaiCircuit(tier).get(), 1))
                    .duration(200 + i * 80)
                    .EUt(MAX_EUT)
                    .save(provider);

            Hk3RecipeResearchGate.bind("reason_reconstruction", recipeId, WALTER_GIFT_RESEARCH);
        }
    }

    // ── 小型崩坏能反应堆：燃料棒 → EU 产出 ──

    /**
     * 小型崩坏能反应堆配方（发电机）。
     * EUt 为负值表示产出EU。改发电量 → .EUt(-xxx)；改燃料消耗 → inputItems 数量
     */
    private static void addSmallHonkaiReaction(Consumer<FinishedRecipe> provider) {
        // 基础发电：崩坏能燃料棒×4 + 液态崩坏能1000mB → 崩坏能抑制剂×1(副产) | 产出MAX_EUT | 120秒
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("basic_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 4))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 1))
                .duration(2400)
                .EUt(-MAX_EUT)
                .save(provider);
    }

    // ── 中型崩坏能反应堆：高密度燃料棒 → EU 产出 ──

    /**
     * 中型崩坏能反应堆配方（发电机）。
     * 改发电量 → .EUt(-xxx)；改副产物 → outputItems
     */
    private static void addMediumHonkaiReaction(Consumer<FinishedRecipe> provider) {
        // 高密度发电：高密度燃料棒×4 + 液态崩坏能2000mB → 崩坏能抑制剂×4(副产) | 产出AB1_EUT | 240秒
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("dense_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 4))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .duration(4800)
                .EUt(-AB1_EUT)
                .save(provider);
    }

    // ── 崩坏能-EU 转换矩阵：输入 EU 产出崩坏能 ──

    /**
     * 崩坏能-EU 转换矩阵配方（EU→液态崩坏能）。
     * 改产出流体量 → .outputFluids() 的 mB 值；circuitMeta 用于区分配方档位
     */
    private static void addHonkaiEuConversion(Consumer<FinishedRecipe> provider) {
        // 档位1：编程电路#1 → 液态崩坏能2304mB | MAX电压 | 20秒
        Hk3RecipeTypes.HONKAI_EU_CONVERSION_RECIPES.recipeBuilder("eu_to_honkai_energy")
                .circuitMeta(1)
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .duration(400)
                .EUt(MAX_EUT)
                .save(provider);

        // 档位2：编程电路#2 + 崩坏能晶体×64 → 液态崩坏能9216mB | AB1电压 | 20秒
        Hk3RecipeTypes.HONKAI_EU_CONVERSION_RECIPES.recipeBuilder("eu_to_honkai_energy_boosted")
                .circuitMeta(2)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 64))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .duration(400)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 海渊电路铸造厂：高效批量电路合成 ──

    /**
     * 海渊电路铸造厂配方。
     * 改海渊I电路产出 → outputItems 第二参数；改魂钢用量 → plate/wireFine 数量
     */
    private static void addAbyssCircuitFoundry(Consumer<FinishedRecipe> provider) {
        // MAX电路×2048 + 魂钢板×1024 + 魂钢细线×4096 + 崩坏能晶体×1024 + 液态崩坏能18432mB → 海渊I电路×16 | AB1电压 | 90秒
        Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES.recipeBuilder("abyss1_circuit_batch")
                .inputItems(CustomTags.MAX_CIRCUITS, 2048)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16))
                .duration(1800)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 海渊机壳冲压机：高效批量机壳生产 ──

    /**
     * 海渊机壳冲压机配方。
     * 改机壳产出 → outputItems 数量；改魂钢用量 → plate 数量
     */
    private static void addAbyssCasingPress(Consumer<FinishedRecipe> provider) {
        // 魂钢板×4096 + 编程电路#8 → 魂钢机壳×64 | AB1电压 | 40秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("soulium_casing_batch")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 4096))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_SOULIUM.get(), 64))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // 魂钢机壳×256 + 魂钢板×2048 + 崩坏能晶体×1024 → 强化魂钢机壳×64 | AB1电压 | 60秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("reinforced_casing_batch")
                .inputItems(new ItemStack(CasingBlocks.CASING_SOULIUM.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .outputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 64))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 崩坏能蒸馏塔：液态崩坏能分馏产线 ──

    /**
     * 崩坏能蒸馏塔配方。
     * 改粒子产出 → outputItems 数量；改回收流体量 → outputFluids mB
     */
    private static void addHonkaiDistillation(Consumer<FinishedRecipe> provider) {
        // 液态崩坏能18432mB + 编程电路#1 → 原始崩坏粒子×256 + 液态崩坏能2304mB(回收) | AB1电压 | 40秒
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("honkai_distillation_basic")
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .circuitMeta(1)
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 256))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 魂钢拉丝阵列：高效魂钢线材 ──

    /**
     * 魂钢拉丝阵列配方。
     * 改线材/箔产出 → outputItems 数量；改锭/板消耗 → inputItems 数量
     */
    private static void addSouliumWireDrawing(Consumer<FinishedRecipe> provider) {
        // 魂钢锭×512 + 液态崩坏能9216mB → 魂钢细线×1024 | AB1电压 | 40秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("soulium_fine_wire_batch")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 1024))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // 魂钢板×512 → 魂钢箔×512 | AB1电压 | 40秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("soulium_foil_batch")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 512))
                .outputItems(ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 512))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 前文明数据恢复站：碎片 → 研究记录封包 ──

    /**
     * 前文明数据恢复站配方。
     * 改碎片消耗 → inputItems 第一行数量；改封包产出 → outputItems 数量
     */
    private static void addPrecivilizationDataRecovery(Consumer<FinishedRecipe> provider) {
        // 前文明资料碎片×64 + 海渊I电路×16 → 研究记录封包×2 | AB1电压 | 60秒
        Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES.recipeBuilder("fragment_to_package")
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 64))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);
    }

    // ── 崩坏能环境采样器：采样 → 世界泡样本 ──

    /**
     * 崩坏能环境采样器配方。
     * 改采样产出 → outputItems/outputFluids 数量
     */
    private static void addHonkaiEnvironmentSampling(Consumer<FinishedRecipe> provider) {
        // 编程电路#1 + 崩坏能晶体×256 + 前文明资料碎片×16 → 世界泡样本×1 + 液态崩坏能500mB | AB1电压 | 180秒
        Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES.recipeBuilder("world_bubble_sampling")
                .circuitMeta(1)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(500))
                .duration(3600)
                .EUt(AB1_EUT)
                .save(provider);
    }
}
