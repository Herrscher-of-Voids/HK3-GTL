package com.sirin.hk3gtl.common.recipe.abyss;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.sirin.hk3gtl.common.block.CasingBlocks;
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
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.function.Consumer;

/**
 * 海渊阶段 23 台多方块专属 RecipeType 配方。
 * 每台 1~2 条核心配方，确保机器可运转、JEI 有内容。
 *
 * <h3>分类</h3>
 * <ul>
 *   <li>能源类（5台）：反应堆、超导冷却、缓冲站、磁约束、浓缩器</li>
 *   <li>制造类（7台）：材料压缩、精密组装、纳米制造、物流分拣、甲板锻造、化学反应、晶体生长</li>
 *   <li>冶金类（2台）：合金精炼、真空冶炼</li>
 *   <li>研究/数据类（5台）：粒子加速、数据保险库、生物计算、频谱分析、通信放大</li>
 *   <li>探索/环境类（4台）：量子之海观测、世界泡采样、污染抑制、废料回收</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>修改电压：调整顶部 AB1/AB2/AB3_EUT 常量</li>
 *   <li>修改物品数量：改 new ItemStack(..., 数量) 的第二参数</li>
 *   <li>修改流体量：改 .getFluid(mB值)</li>
 *   <li>修改工时：改 .duration(tick)，20tick = 1秒</li>
 *   <li>科研门控：Hk3RecipeResearchGate.bind() 绑定研究ID，无门控则不调用</li>
 *   <li>新增配方：在对应分类方法中追加</li>
 *   <li>禁止用 GTValues.V[15+]，int 溢出！必须用 Hk3Values.VA_LONG[]</li>
 *   <li>发电配方：EUt 传负数表示产出 EU；普通机器 EUt 为正数表示耗电。</li>
 *   <li>配方ID：自定义 RecipeType 下直接用语义 ID（如 large_reactor_operation），不要加重复命名空间。</li>
 * </ul>
 *
 * <h3>变更记录（2026-05-19）</h3>
 * <ul>
 *   <li>删除：130 台时代遗留的孤儿 RecipeType 直连（无对应现役机器）</li>
 *   <li>新增：将遗留工艺统一挂载到 v0.3 仍在运行的 4 台海渊核心机器 RecipeType</li>
 *   <li>修改：研究门槛 bind 的 recipeType 路径同步改为现役类型，避免门槛映射丢失</li>
 *   <li>用途：清理配方残余并保证 JEI/执行链只指向真实存在的机器</li>
 * </ul>
 */
public class AbyssMachineRecipes {

    /** 海渊I 电压 (Tier 15) */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** 海渊II 电压 (Tier 16) */
    private static final long AB2_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_2];
    /** 海渊III 电压 (Tier 17) */
    private static final long AB3_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_3];

    /**
     * 注册入口。按功能分类调用子方法。
     * 新增类别时添加新的 addXxxRecipes 方法并在此调用。
     */
    public static void register(Consumer<FinishedRecipe> provider) {
        addEnergyRecipes(provider);
        addManufacturingRecipes(provider);
        addResearchRecipes(provider);
        addExplorationRecipes(provider);
        addEnvironmentRecipes(provider);
    }

    // ═══════════════════════════════════════
    //  能源类（5台）
    // ═══════════════════════════════════════

    /**
     * 能源类配方：发电、冷却、缓冲、磁约束、浓缩。
     * 发电配方 EUt 取负值表示产出EU。
     * 改能源平衡时优先看本组：燃料消耗、液态崩坏能回收量、产电 EUt。
     */
    private static void addEnergyRecipes(Consumer<FinishedRecipe> provider) {
        // 大型崩坏能反应堆（发电）：高密度燃料棒×16 + 液态崩坏能8000mB → 抑制剂×4 + 液态崩坏能500mB(回收) | 产出AB2_EUT | 400秒
        // 科研门控：R-AB-015
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("large_reactor_operation")
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.REACTOR_STABILIZER.get(), 1))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(8000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(500))
                .duration(8000)
                .EUt(-AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("large_honkai_reaction", "large_reactor_operation", "R-AB-015");

        // 海渊超导冷却环：超导金属氢×64 + 液态崩坏能4608mB → 爱因斯坦环磁体×2 | AB2电压 | 60秒
        // 科研门控：R-AB-014
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("superconductor_cooling")
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 2))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_vacuum_smelting", "superconductor_cooling", "R-AB-014");

        // 海渊能量缓冲站：崩坏能晶体×256 + 编程电路#1 → 液态崩坏能4608mB | AB1电压 | 40秒
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("energy_buffer_cycle")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .circuitMeta(1)
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // 双能源回灌：把大型反应堆回收出的液态崩坏能重新压成结晶，用于供给魂钢和功能件配方。
        // 这是海渊闭环的能量回收支路，效率低于直接凝结，避免无限正反馈。
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("liquid_honkai_recrystallization")
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .circuitMeta(2)
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

        // 海渊磁约束环：原始崩坏粒子×4096 + 液态崩坏能18432mB → 压缩核心×4 | AB2电压 | 90秒
        // 科研门控：R-AB-014
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("magnetic_confinement")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 4096))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 4))
                .duration(1800)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("large_honkai_reaction", "magnetic_confinement", "R-AB-014");

        // 海渊崩坏能浓缩器：崩坏能晶体×1024 + 液态崩坏能18432mB → 稳定崩坏晶体×32 + 液态崩坏能1000mB(回收) | AB2电压 | 60秒
        // 科研门控：R-AB-013
        Hk3RecipeTypes.LARGE_HONKAI_REACTION_RECIPES.recipeBuilder("honkai_concentration")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 32))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(1000))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("large_honkai_reaction", "honkai_concentration", "R-AB-013");
    }

    // ═══════════════════════════════════════
    //  制造类（7台）
    // ═══════════════════════════════════════

    /**
     * 制造类配方：材料压缩、精密组装、纳米制造、物流分拣、甲板锻造、化学反应、晶体生长。
     * 改批量制造效率时优先看本组：输出数量、耗时、是否绑定研究。
     */
    private static void addManufacturingRecipes(Consumer<FinishedRecipe> provider) {
        // 海渊材料压缩阵列：魂钢板×4096 + 崩坏能晶体×512 + 编程电路#1 → 流体合金块×8 | AB2电压 | 60秒
        // 科研门控：R-AB-013
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("soulium_dense_plate")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .circuitMeta(1)
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 8))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "soulium_dense_plate", "R-AB-013");

        // 海渊精密组装中心：力场发生器AB2×16 + 环磁体×8 + 稳定框架×8 + 海渊II电路×64 + 液态崩坏能9216mB → 能量调制器×2 | AB2电压 | 80秒
        // 科研门控：R-AB-011
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("precision_energy_modulator")
                .inputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_2.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 8))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_STABLE_FRAME.get(), 8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 2))
                .duration(1600)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "precision_energy_modulator", "R-AB-011");

        // 海渊精密装配工坊：批量生产高密度燃料棒，把魂钢线、压缩核心、稳定框架接入反应堆闭环。
        // 标准组装机仍可启动；本路线是海渊线的高吞吐版本。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("dense_fuel_rod_industrial")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_STABLE_FRAME.get(), 4))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 2048))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 8))
                .duration(1400)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "dense_fuel_rod_industrial", "R-AB-015");

        // 海渊精密装配工坊：稳定框架量产。相比 GT 标准组装机，额外消耗稳定魂钢原质并提高产出。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("stable_frame_industrial")
                .inputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 96))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_STABLE_FRAME.get(), 8))
                .duration(1400)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "stable_frame_industrial", "R-AB-012");

        // 海渊精密装配工坊：数据核心量产，把前文明碎片和凝视缓冲并入海渊研究闭环。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("data_core_industrial")
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 2))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .inputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_2.get(), 16))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 8))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "data_core_industrial", "R-AB-012");

        // 海渊精密装配工坊：反应堆芯量产，把高密度燃料、调制器和稳定器绑定到大型反应堆建设。
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("reactor_core_industrial")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_ENERGY_MODULATOR.get(), 8))
                .inputItems(new ItemStack(AbyssFunctionalItems.REACTOR_STABILIZER.get(), 2))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(AbyssFunctionalItems.ABYSS_REACTOR_CORE.get(), 2))
                .duration(2200)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "reactor_core_industrial", "R-AB-015");

        // 海渊纳米制造台：Shirabon粉×512 + 原始崩坏粒子×2048 + 海渊I电路×64 + 液态崩坏能9216mB → 纳米陶瓷×16 | AB2电压 | 60秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("nano_ceramic_batch")
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 2048))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊机械匠厅（替代物流分拣）：4种AB1部件各×128 → 4种AB1高级部件各×4 | AB1电压 | 90秒
        // 需求 14：分拣概念改为"匠人手工锻造"，强调叙事感而非无灵魂流水线
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("abyss_component_crafting")
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_1.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_1.get(), 4))
                .outputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_1.get(), 4))
                .outputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_1.get(), 4))
                .outputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_1.get(), 4))
                .duration(1800)
                .EUt(AB1_EUT)
                .save(provider);

        // 海渊甲板锻造机：魂钢板×2048 + 流体合金×128 + 纳米陶瓷×64 → 强化魂钢机壳×16 | AB2电压 | 80秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("reinforced_armor_plate")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 64))
                .outputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 16))
                .duration(1600)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊超级化学反应釜：原始崩坏粒子×4096 + Shirabon粉×512 + 液态崩坏能8000mB → 抑制剂×16 | AB2电压 | 60秒
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("honkai_suppressant_mega")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 4096))
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(8000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 16))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊晶体生长槽：原始崩坏粒子×4096 + 崩坏能晶体×512 + 液态崩坏能18432mB → 稳定崩坏晶体×16 | AB2电压 | 90秒
        // 科研门控：R-AB-013
        Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES.recipeBuilder("stabilized_crystal_growth")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 16))
                .duration(1800)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_precision_assembly", "stabilized_crystal_growth", "R-AB-013");
    }

    // ═══════════════════════════════════════
    //  冶金类（2台）
    // ═══════════════════════════════════════

    /**
     * 冶金类配方：合金精炼炉、真空冶炼室。
     * 改材料纯化/合金产线时优先看本组：流体合金、超导金属氢、稳定魂钢原质。
     */
    private static void addResearchRecipes(Consumer<FinishedRecipe> provider) {
        // 海渊合金精炼炉 - 流体合金：Shirabon锭×512 + Magmatter锭×256 + 魂钢锭×512 + 液态崩坏能9216mB → 流体合金×16 | AB2电压 | 60秒
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("fluid_alloy_refining")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Shirabon, 512))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 256))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 16))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊合金精炼炉 - 超导金属氢：Magmatter锭×512 + Shirabon细线×2048 + 崩坏能晶体×1024 + 液态崩坏能9216mB → 超导金属氢×8 | AB2电压 | 70秒
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("superconductive_hydrogen_refining")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 512))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTLMaterials.Shirabon, 2048))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 8))
                .duration(1400)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊真空冶炼室：魂钢锭×1024 + 原始崩坏粒子×1024 + 液态崩坏能9216mB → 稳定魂钢原始质量×32 + 液态崩坏能500mB(回收) | AB2电压 | 60秒
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("vacuum_soulium_purification")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 32))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(500))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);
    }

    // ═══════════════════════════════════════
    //  研究/数据类（5台）
    // ═══════════════════════════════════════

    /**
     * 研究/数据类配方：粒子加速、数据保险库、生物计算、频谱分析、通信放大。
     * 改研究向材料来源时优先看本组：远古遗产、凝视缓冲、前文明碎片等。
     */
    private static void addExplorationRecipes(Consumer<FinishedRecipe> provider) {
        // 海渊粒子加速环：原始崩坏粒子×8192 + 崩坏能晶体×512 + 液态崩坏能18432mB → 压缩核心×8 + 液态崩坏能2304mB(回收) | AB3电压 | 120秒
        // 科研门控：R-AB-017
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("honkai_particle_acceleration")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 8192))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .duration(2400)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_particle_acceleration", "honkai_particle_acceleration", "R-AB-017");

        // 海渊精炼窑（替代数据保险库）：研究封包×64 + 前文明碎片×128 + 海渊II电路×32 → 远古遗产×1 | AB2电压 | 150秒
        // 需求 11：删数据存储库，用冶金向机器取而代之，保留"提纯远古遗产"的功能意义
        // 科研门控：R-AB-010
        Hk3RecipeTypes.ABYSS_VACUUM_SMELTING_RECIPES.recipeBuilder("abyss_ancient_refining")
                .inputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 64))
                .inputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .outputItems(new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 1))
                .duration(3000)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_vacuum_smelting", "abyss_ancient_refining", "R-AB-010");

        // 海渊生物计算阵列：神经处理器×512 + 数据核心×8 + 海渊II电路×64 + 液态崩坏能9216mB → 高级凝视缓冲×2 | AB2电压 | 80秒
        // 科研门控：R-AB-008
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("biocomputing_analysis")
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(512))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 2))
                .duration(1600)
                .EUt(AB2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_particle_acceleration", "biocomputing_analysis", "R-AB-008");

        // 海渊频谱分析仪：原始崩坏粒子×4096 + 测量阵列×2(消耗) + 海渊II电路×16 → 前文明碎片×4 + 崩坏能晶体×16 | AB2电压 | 60秒
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("spectrum_deep_scan")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 4096))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY.get(), 2))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 16))
                .outputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 4))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16))
                .duration(1200)
                .EUt(AB2_EUT)
                .save(provider);

        // 海渊通信放大器：相位镜×16 + 数据核心×8 + 海渊III电路×16 → 研究封包×4 | AB3电压 | 120秒
        // 科研门控：R-AB-009
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("communication_boost")
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 16))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_DATA_CORE.get(), 8))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 16))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 4))
                .duration(2400)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("abyss_particle_acceleration", "communication_boost", "R-AB-009");
    }

    // ═══════════════════════════════════════
    //  探索/环境类（4台）
    // ═══════════════════════════════════════

    /**
     * 探索/环境类配方：维度观测、世界泡采样、污染抑制、废料回收。
     */
    private static void addEnvironmentRecipes(Consumer<FinishedRecipe> provider) {
        // 量子之海观测站：崩坏能晶体×512 + 测量阵列×2 + 海渊II电路×32 + 液态崩坏能18432mB → 世界泡样本×1 + 前文明碎片×4 | AB3电压 | 180秒
        // 科研门控：R-AB-019
        Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES.recipeBuilder("quanta_observation")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY.get(), 2))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 32))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1))
                .outputItems(new ItemStack(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 4))
                .duration(3600)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("sea_of_quanta_observation", "quanta_observation", "R-AB-019");

        // 世界泡采样场：崩坏能晶体×1024 + 测量阵列×4(消耗) + 液态崩坏能18432mB → 世界泡样本×1 | AB3电压 | 240秒
        // 科研门控：R-AB-020
        Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES.recipeBuilder("world_bubble_batch_sampling")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputItems(new ItemStack(AbyssFunctionalItems.ABYSS_MEASUREMENT_ARRAY.get(), 4))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1))
                .duration(4800)
                .EUt(AB3_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("sea_of_quanta_observation", "world_bubble_batch_sampling", "R-AB-020");

        // 崩坏能污染抑制穹顶：抑制剂×64 + 液态崩坏能9216mB → 原始崩坏粒子×256 | AB1电压 | 60秒
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("pollution_suppression")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 256))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // 海渊废料回收厂：抑制剂×128 + 魂钢粉×128 + 液态崩坏能9216mB → 原始崩坏粒子×512 + 崩坏能晶体×32 + Shirabon粉×4 | AB1电压 | 90秒
        Hk3RecipeTypes.ABYSS_PARTICLE_ACCELERATION_RECIPES.recipeBuilder("suppressant_recycling")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.dust, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 32))
                .outputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 4))
                .duration(1800)
                .EUt(AB1_EUT)
                .save(provider);
    }
}
