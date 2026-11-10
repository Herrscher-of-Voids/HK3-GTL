package com.sirin.hk3gtl.common.recipe.honkai;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.gtlcore.gtlcore.common.data.GTLItems;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.function.Consumer;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/**
 * 【变更记录】2026-09-23：内测5配方迁移。
 * 旧材料配方继续保留兼容性，并统一通过当前液态崩坏能精炼类型运行。
 */
/**
 * 【变更记录 #1】2026-09-24 16:37:18（内测5修订66）
 * 删除：旧精炼类型对压缩核心工艺的归属。新增：探测器升级校准报告与研究门槛。
 * 修改：适配基板实际消耗稳定液，结晶加工交给浓缩精制厂；用途：补齐研究与物料顺序。
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
/**
 * 【变更记录 #4】2026-10-17 14:38:40（第4次备注 · 内测5修订162）
 * 删除：退役虚空档案分析与理构重建结构的远古遗产/意志旧配方。
 * 新增：无。修改：保留当前浓缩精制类型与GT标准机的材料、液态线中间件注册。
 * 用途：清除退役设备配方，不以改挂现行类型代替正式工艺设计；原文件已逐份备份。
 */
public class HonkaiMaterialRecipes {

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static void register(Consumer<FinishedRecipe> provider) {

        registerIndustrialIntermediateRecipes(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
        Hk3IndustrialRecipeTypes.CONCENTRATION.recipeBuilder("stabilized_crystal")
                .circuitMeta(3)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 1024))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 16))
                .duration(900)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 稳定崩坏能晶体、崩坏能晶体和四号编程电路合成为压缩崩坏能核心。
        Hk3IndustrialRecipeTypes.CONCENTRATION.recipeBuilder("compressed_honkai_core")
                .circuitMeta(4)
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 4))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 崩坏能晶体、魂钢板材、魂钢杆件与液态崩坏能合成为燃料棒。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 4))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 燃料棒、压缩核心、魂钢板材与液态崩坏能合成为高密度燃料棒。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_dense_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 原始崩坏粒子、Shirabon 粉末与液态崩坏能合成为抑制剂。
        GTRecipeTypes.CHEMICAL_RECIPES.recipeBuilder("hk3gtl_honkai_suppressant")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // Shirabon、Magmatter、魂钢与液态崩坏能合成为流体合金。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_fluid_alloy")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Shirabon, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 64))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 8))
                .duration(800)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
        GTRecipeTypes.COMPRESSOR_RECIPES.recipeBuilder("hk3gtl_fluid_alloy_block")
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 9))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1))
                .duration(200)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_nano_ceramic")
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(64))
                .outputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 8))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_phase_transfer_mirror")
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16))
                .inputItems(GTLItems.SENSOR_MAX.asStack(16))
                .inputItems(GTLItems.EMITTER_MAX.asStack(16))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 64))
                .outputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 2))
                .duration(900)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 魂钢环、超导金属氢、MAX 力场发生器与海渊电路合成为环形磁体。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_einstein_ringmagnet")
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(8))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 32)
                .outputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 中文备注：该处说明已按当前代码行为整理。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_superconductive_metal_hydrogen")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTLMaterials.Shirabon, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 4))
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);

        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        // 魂钢板、魂钢杆、稳定魂钢原质、崩坏能晶体和海渊电路合成为定向魂钢组件。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_oriented_soulium_component")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 16)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 8))
                .duration(1000)
                .EUt(AB1_EUT)
                .save(provider);

    }

    /** 注册液态崩坏能主线缺失的中间件；所有入口只依赖 MAX/GTL 基础材料或已完成实验产物。 */
    private static void registerIndustrialIntermediateRecipes(Consumer<FinishedRecipe> provider) {
        long eut = Hk3Values.VA_LONG[GTValues.MAX];
        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("assembler", "industrial_liquid_honkai_detector", "RN-DMT");
        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("assembler", "industrial_honkai_adapted_circuit_substrate", "RN-LES");
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_liquid_honkai_detector"))
                .inputItems(betaItem("prototype_honkai_detector", 1))
                .inputItems(betaItem("honkai_detector_calibration_report", 1))
                .inputItems(GTLItems.SENSOR_MAX.asStack(2), GTLItems.EMITTER_MAX.asStack(2))
                .inputItems(CustomTags.MAX_CIRCUITS, 2)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.TungstenSteel, 8))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTMaterials.Platinum, 16))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(576))
                .outputItems(betaItem("liquid_honkai_detector", 1)).duration(800).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_honkai_reference_sample"))
                .inputItems(betaItem("analyzed_honkai_sample", 4))
                .inputItems(Items.GLASS_PANE, 8)
                .inputItems(ChemicalHelper.get(TagPrefix.foil, GTMaterials.Platinum, 8))
                .inputItems(CustomTags.MAX_CIRCUITS, 1)
                .outputItems(betaItem("honkai_reference_sample", 4)).duration(400).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_honkai_crystal_seed"))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.gem, GTMaterials.Diamond, 4))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.StainlessSteel, 4))
                .inputItems(CustomTags.MAX_CIRCUITS, 1)
                .outputItems(betaItem("honkai_crystal_seed", 8)).duration(600).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_directional_crystallization_matrix"))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(2), GTLItems.SENSOR_MAX.asStack(2))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.TungstenSteel, 12))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 24))
                .inputItems(CustomTags.MAX_CIRCUITS, 2)
                .outputItems(betaItem("directional_crystallization_matrix", 2)).duration(900).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_separation_filter"))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.StainlessSteel, 8))
                .inputItems(Items.GLASS_PANE, 8)
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTMaterials.Platinum, 12))
                .inputItems(ChemicalHelper.get(TagPrefix.foil, GTMaterials.Polybenzimidazole, 16))
                .inputItems(CustomTags.MAX_CIRCUITS, 1)
                .outputItems(betaItem("separation_filter", 4)).duration(500).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_fuel_matrix"))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.TungstenSteel, 16))
                .inputItems(ChemicalHelper.get(TagPrefix.foil, GTMaterials.Polybenzimidazole, 24))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(2), GTLItems.EMITTER_MAX.asStack(2))
                .inputItems(CustomTags.MAX_CIRCUITS, 2)
                .outputItems(betaItem("fuel_matrix", 4)).duration(700).EUt(eut).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(new net.minecraft.resources.ResourceLocation("hk3gtl", "industrial_honkai_adapted_circuit_substrate"))
                .inputItems(betaItem("analyzed_honkai_sample", 2))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTMaterials.TungstenSteel, 8))
                .inputItems(ChemicalHelper.get(TagPrefix.foil, GTMaterials.Polybenzimidazole, 16))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 16))
                .inputItems(CustomTags.MAX_CIRCUITS, 2)
                .inputFluids(Hk3LiquidLineRecipes.fluid("stabilized_liquid_honkai_energy", 100))
                .outputItems(betaItem("honkai_adapted_circuit_substrate", 2)).duration(800).EUt(eut).save(provider);
    }

    private static ItemStack betaItem(String id, int amount) {
        var item = Hk3IndustrialContent.items().get(id);
        if (item == null) throw new IllegalStateException("未注册内测5物品：" + id);
        return new ItemStack(item.get(), amount);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
