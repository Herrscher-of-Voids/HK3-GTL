package com.sirin.hk3gtl.common.recipe.quantum;

import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;


public final class QuantumCasingRecipes {

    private static final long Q1_EUT = Hk3Values.VA_LONG[Hk3Tiers.QUANTUM_1];

    private QuantumCasingRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        String research = "R-QT-001";

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_entangle")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_LATTICE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_ENTANGLE.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_quantum_entangle", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_sea")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_TREE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 64))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(18432))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_SEA.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_quantum_sea", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_bubble")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_ANCHOR.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_BUBBLE.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_quantum_bubble", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_flux")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_CORE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_FLUX.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_quantum_flux", research);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_quantum_shipboard")
                .inputItems(new ItemStack(CasingBlocks.CASING_IMAGINARY_WEAVE.get(), 256))
                .inputItems(new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 32))
                .inputItems(new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_QUANTUM_SHIPBOARD.get(), 32))
                .duration(3200).EUt(Q1_EUT).save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_casing_quantum_shipboard", research);
    }
}
