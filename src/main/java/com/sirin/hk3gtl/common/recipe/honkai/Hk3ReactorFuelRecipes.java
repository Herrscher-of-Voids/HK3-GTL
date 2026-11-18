package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

public final class Hk3ReactorFuelRecipes {
    private Hk3ReactorFuelRecipes() {}

    private static ItemStack item(String id, int count) {
        return new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(id)), count);
    }

    private static GTRecipeBuilder recipe(GTRecipeType type, Hk3ReactorFuels.Fuel fuel, String step) {
        String id = "industrial_honkai_" + fuel.slug() + "_" + step;
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id, fuel.research());
        return type.recipeBuilder(new ResourceLocation("hk3gtl", id)).duration(600)
                .EUt(Hk3Values.VA_LONG[14]);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        for (var fuel : Hk3ReactorFuels.ALL) {
            var preparation = switch (fuel.slug()) {
                case "carbon", "zeolite", "alumina" -> GTRecipeTypes.VACUUM_RECIPES;
                case "silica_gel", "zirconia", "diamond_copper", "titanium_carbide" -> GTRecipeTypes.MIXER_RECIPES;
                case "silicon_carbide" -> GTRecipeTypes.COMPRESSOR_RECIPES;
                case "boron_carbide" -> GTRecipeTypes.CENTRIFUGE_RECIPES;
                case "tungsten" -> GTRecipeTypes.CUTTER_RECIPES;
                default -> GTRecipeTypes.BENDER_RECIPES;
            };
            var first = recipe(preparation, fuel, "precursor")
                    .inputItems(item(fuel.raw(), fuel.amount()))
                    .outputItems(item("hk3gtl:" + fuel.item("_precursor"), 8));
            if (fuel.additiveAmount() > 0) first.inputItems(item(fuel.additive(), fuel.additiveAmount()));
            if (fuel.slug().equals("silica_gel")) first.inputFluids(GTMaterials.DistilledWater.getFluid(1000));
            if (fuel.slug().equals("tungsten")) first.inputFluids(GTMaterials.Lubricant.getFluid(250));
            first.save(provider);

            var forming = switch (fuel.slug()) {
                case "silicon_carbide", "zirconia", "titanium_carbide", "alumina" -> GTRecipeTypes.BLAST_RECIPES;
                case "zeolite" -> GTRecipeTypes.CENTRIFUGE_RECIPES;
                case "graphene", "tungsten", "ptfe_membrane", "pbi_microcapsule" -> GTRecipeTypes.ASSEMBLER_RECIPES;
                default -> GTRecipeTypes.COMPRESSOR_RECIPES;
            };
            boolean ceramic = forming == GTRecipeTypes.BLAST_RECIPES;
            var second = recipe(forming, fuel, "carrier")
                    .inputItems(item("hk3gtl:" + fuel.item("_precursor"), 8))
                    .outputItems(item("hk3gtl:" + fuel.item("_carrier"), ceramic ? 7 : 8));
            if (forming == GTRecipeTypes.ASSEMBLER_RECIPES) second.onSave(null);
            if (ceramic) second.blastFurnaceTemp(1800).duration(1200)
                    .inputFluids(GTMaterials.Nitrogen.getFluid(1000))
                    .outputItems(item("hk3gtl:inactive_fuel_residue", 1));
            second.save(provider);
        }
        for (var rod : Hk3ReactorFuels.RODS) {
            for (int count : Hk3ReactorFuels.BUNDLE_SIZES) {
                String bundle = rod.bundle(count);
                String pack = "industrial_" + bundle + "_pack";
                String unpack = "industrial_" + bundle + "_unpack";
                Hk3RecipeResearchGate.bindAll(GTRecipeTypes.PACKER_RECIPES.registryName.getPath(), pack, rod.research());
                Hk3RecipeResearchGate.bindAll(GTRecipeTypes.PACKER_RECIPES.registryName.getPath(), unpack, rod.research());
                GTRecipeTypes.PACKER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", pack))
                        .circuitMeta(count)
                        .inputItems(item("hk3gtl:" + rod.path(), count))
                        .outputItems(item("hk3gtl:" + bundle, 1))
                        .duration(count * 20).EUt(Hk3Values.VA_LONG[14]).save(provider);
                GTRecipeTypes.PACKER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", unpack))
                        .circuitMeta(1)
                        .inputItems(item("hk3gtl:" + bundle, 1))
                        .outputItems(item("hk3gtl:" + rod.path(), count))
                        .duration(count * 10).EUt(Hk3Values.VA_LONG[14]).save(provider);
                for (String state : new String[]{"depleted_", "broken_"}) {
                    String recovery = "industrial_" + state + bundle + "_unpack";
                    Hk3RecipeResearchGate.bindAll(GTRecipeTypes.PACKER_RECIPES.registryName.getPath(), recovery, rod.research());
                    GTRecipeTypes.PACKER_RECIPES.recipeBuilder(new ResourceLocation("hk3gtl", recovery))
                            .circuitMeta(1)
                            .inputItems(item("hk3gtl:" + state + bundle, 1))
                            .outputItems(item("hk3gtl:" + state + rod.path(), count))
                            .duration(count * 10).EUt(Hk3Values.VA_LONG[14]).save(provider);
                }
            }
        }
    }
}
