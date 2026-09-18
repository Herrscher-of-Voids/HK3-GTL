package com.sirin.hk3gtl.common.recipe.imaginary;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesFinality;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImaginary;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;


public final class ImaginaryMachineRecipes {

    private static final long IM1_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_1];
    private static final long IM2_EUT = Hk3Values.VA_LONG[Hk3Tiers.IMAGINARY_2];

    private ImaginaryMachineRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesImaginary.IMAGINARY_TREE_OBSERVATION.recipeBuilder("imaginary_tree_scan")
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 64))
                .outputItems(new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 4))
                .duration(1600)
                .EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_tree_observation", "imaginary_tree_scan", "R-IM-001");

        Hk3RecipeTypesImaginary.IMAGINARY_ANCHORING.recipeBuilder("imaginary_anchor_stabilize")
                .inputItems(new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(16000))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 2))
                .duration(2000)
                .EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_anchoring", "imaginary_anchor_stabilize", "R-IM-004");

        Hk3RecipeTypesImaginary.DUAL_ENERGY_STABLE_SUPPLY.recipeBuilder("dual_energy_buffer_charge")
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 8))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(32000))
                .outputItems(new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 4))
                .duration(1800)
                .EUt(IM2_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("dual_energy_stable_supply", "dual_energy_buffer_charge", "R-IM-008");

        Hk3RecipeTypes.SEA_OF_QUANTA_OBSERVATION_RECIPES.recipeBuilder("sea_quanta_imaginary_survey")
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_1.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 128))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1))
                .duration(2400)
                .EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("sea_of_quanta_observation", "sea_quanta_imaginary_survey", "R-IM-005");

        // 虚数维度跃迁门：海渊→虚数的产线入口。把海渊产物 + 液态崩坏能"撕开"成虚数胚体（世界泡样本）。
        // RecipeType IO=(4,4,2,2)。无环：输出 world_bubble_sample，输入均为海渊阶段产物，无反向依赖。
        Hk3RecipeTypesFinality.IMAGINARY_DIMENSION_GATEWAY_PROC.recipeBuilder("imaginary_gateway_embryo")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 8))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(64000))
                .outputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2))
                .duration(2000)
                .EUt(IM1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("imaginary_dimension_gateway", "imaginary_gateway_embryo", "R-IM-001");
    }
}
