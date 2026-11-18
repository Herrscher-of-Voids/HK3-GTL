package com.sirin.hk3gtl.common.recipe.honkai;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;


import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
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





























public class HonkaiMaterialRecipes {

    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    private static final long AB1_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];

    public static void register(Consumer<FinishedRecipe> provider) {

        registerIndustrialIntermediateRecipes(provider);

        Hk3RecipePower.require(Hk3IndustrialRecipeTypes.CONCENTRATION.recipeBuilder("stabilized_crystal")
                .circuitMeta(3)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 1024))
                .outputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 16))
                .duration(900)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        // 稳定崩坏能晶体、崩坏能晶体和四号编程电路合成为压缩崩坏能核心。
        Hk3RecipePower.require(Hk3IndustrialRecipeTypes.CONCENTRATION.recipeBuilder("compressed_honkai_core")
                .circuitMeta(4)
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 4))
                .duration(1200)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        // 崩坏能晶体、魂钢板材、魂钢杆件与液态崩坏能合成为燃料棒。
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 4))
                .duration(800)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);
        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_honkai_fuel_rod", java.util.List.of("RN-FRP"));

        // 燃料棒、压缩核心、魂钢板材与液态崩坏能合成为高密度燃料棒。
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_dense_fuel_rod")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 8))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(9216))
                .outputItems(new ItemStack(HonkaiMaterialItems.DENSE_HONKAI_FUEL_ROD.get(), 2))
                .duration(1000)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);
        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bindAll("assembler", "hk3gtl_dense_fuel_rod", java.util.List.of("RN-FRP", "RN-CFR"));

        // 原始崩坏粒子、Shirabon 粉末与液态崩坏能合成为抑制剂。
        GTRecipeTypes.CHEMICAL_RECIPES.recipeBuilder("hk3gtl_honkai_suppressant")
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        // Shirabon、Magmatter、魂钢与液态崩坏能合成为流体合金。
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_fluid_alloy")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Shirabon, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 64))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM, 128))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 8))
                .duration(800)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        Hk3RecipePower.require(GTRecipeTypes.COMPRESSOR_RECIPES.recipeBuilder("hk3gtl_fluid_alloy_block")
                .inputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY.get(), 9))
                .outputItems(new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 1))
                .duration(200)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_nano_ceramic")
                .inputItems(ChemicalHelper.get(TagPrefix.dust, GTLMaterials.Shirabon, 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 512))
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(64))
                .outputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 8))
                .duration(600)
                .EUt(MAX_EUT)
                .save(provider);

        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_phase_transfer_mirror")
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16))
                .inputItems(GTLItems.SENSOR_MAX.asStack(16))
                .inputItems(GTLItems.EMITTER_MAX.asStack(16))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 64))
                .outputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 2))
                .duration(900)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        // 魂钢环、超导金属氢、MAX 力场发生器与海渊电路合成为环形磁体。
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_einstein_ringmagnet")
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(8))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 32)
                .outputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 2))
                .duration(1200)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_superconductive_metal_hydrogen")
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 128))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, GTLMaterials.Shirabon, 512))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .outputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 4))
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);

        // 魂钢板、魂钢杆、稳定魂钢原质、崩坏能晶体和海渊电路合成为定向魂钢组件。
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_oriented_soulium_component")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 128))
                .inputItems(new ItemStack(SouliumChainItems.STABILIZED_SOULIUM_PROTO_MASS.get(), 64))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 16)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(4608))
                .outputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 8))
                .duration(1000)
                .EUt(AB1_EUT), Hk3Tiers.HBV).save(provider);

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
                .onSave(null)
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


