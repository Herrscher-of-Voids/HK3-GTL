package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import java.util.function.Consumer;




















public final class HonkaiRecipes {
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];

    private HonkaiRecipes() {}

    private static ItemStack betaItem(String id, int amount) {
        var object = Hk3IndustrialContent.items().get(id);
        if (object == null) throw new IllegalStateException("Missing Beta 5 item registration: " + id);
        return new ItemStack(object.get(), amount);
    }

    private static FluidStack fluid(String id, int amount) {
        var material = Hk3IndustrialFluids.materials().get(id);
        if (material == null) throw new IllegalStateException("Missing Beta 5 fluid registration: " + id);
        return material.getFluid(amount);
    }

    public static void addAbsorptionRecipes(Consumer<FinishedRecipe> provider) {
        Hk3IndustrialRecipeTypes.COLLECTION.recipeBuilder(new ResourceLocation("hk3gtl", "industrial_liquid_sampling"))
                .circuitMeta(3)
                .notConsumable(betaItem("prototype_honkai_detector", 1))
                .inputFluids(GTMaterials.LiquidAir.getFluid(1_000_000))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(100))
                .duration(1200).EUt(MAX_EUT).save(provider);

        com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate.bind("industrial_honkai_collection", "industrial_liquid_collection", "RN-DMT");
        // HBV将液化与选择性提取集成在塔内，省去外置空气液化工序。
        Hk3RecipePower.require(Hk3IndustrialRecipeTypes.COLLECTION.recipeBuilder(new ResourceLocation("hk3gtl", "industrial_liquid_collection"))
                .circuitMeta(4)
                .notConsumable(betaItem("liquid_honkai_detector", 1))
                .notConsumable(betaItem("honkai_reference_sample", 4))
                .inputFluids(GTMaterials.Air.getFluid(1_000_000))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2400))
                .duration(600).EUt(Hk3Values.VA_LONG[Hk3Tiers.HBV]), Hk3Tiers.HBV).save(provider);
    }

    public static void addCondensationRecipes(Consumer<FinishedRecipe> provider) {
        Hk3LiquidLineRecipes.processing(provider);
        Hk3FuelRodBootstrapRecipes.register(provider);
    }

    /** 液态、浓缩与结晶三条路径使用相同的正式网络结算。 */
    public static void addNetworkInjectionRecipes(Consumer<FinishedRecipe> provider) {
        Hk3LiquidLineRecipes.injection(provider);
    }
}


