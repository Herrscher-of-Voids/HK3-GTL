package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.main.Hk3MainComponentRecipes;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.List;
import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;

public final class Hk3IndustrialSupplyRecipes {
    private Hk3IndustrialSupplyRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        detector("solid", "liquid", Hk3Tiers.HDV, "RN-ALE", "RN-DMT")
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 8)
                .inputItems(TagPrefix.foil, GTMaterials.Platinum, 8).save(provider);
        detector("gaseous", "solid", Hk3Tiers.QSV, "RN-SSC", "RN-MRE")
                .inputItems(TagPrefix.plate, GTMaterials.Polytetrafluoroethylene, 4)
                .inputItems(TagPrefix.foil, GTMaterials.Gold, 8).save(provider);
        detector("energy", "gaseous", Hk3Tiers.IRV, "RN-IAA", "RN-GSC")
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 8)
                .inputItems(TagPrefix.wireGtSingle, GTMaterials.NiobiumTitanium, 8).save(provider);

        carrier(provider, "carbon", TagPrefix.dust, GTMaterials.Carbon, 8, GTValues.MAX, 2, 400).save(provider);
        carrier(provider, "zeolite", TagPrefix.dust, GTMaterials.Zeolite, 8, GTValues.MAX, 4, 600).save(provider);
        carrier(provider, "silica_gel", TagPrefix.dust, GTLMaterials.SilicaGel, 8, GTValues.MAX, 3, 500).save(provider);
        carrier(provider, "silicon_carbide", TagPrefix.dust, GTLMaterials.SiliconCarbide, 8, Hk3Tiers.HBV, 4, 600).save(provider);
        carrier(provider, "boron_carbide", TagPrefix.dust, GTLMaterials.BoronCarbide, 8, Hk3Tiers.HBV, 5, 700).save(provider);
        carrier(provider, "zirconia", TagPrefix.dust, GTLMaterials.ZirconiumOxide, 8, Hk3Tiers.HBV, 6, 800).save(provider);
        carrier(provider, "diamond_copper", TagPrefix.dust, GTMaterials.Diamond, 4, Hk3Tiers.HCV, 8, 800)
                .inputItems(TagPrefix.dust, GTMaterials.Copper, 8).save(provider);
        carrier(provider, "graphene", TagPrefix.dust, GTMaterials.Graphene, 8, Hk3Tiers.HCV, 8, 1000).save(provider);
        carrier(provider, "titanium_carbide", TagPrefix.dust, GTMaterials.TitaniumCarbide, 8, Hk3Tiers.HCV, 6, 800).save(provider);
        carrier(provider, "alumina", TagPrefix.dust, GTLMaterials.Alumina, 8, Hk3Tiers.HRV, 5, 600).save(provider);
        carrier(provider, "tungsten", TagPrefix.dust, GTMaterials.Tungsten, 8, Hk3Tiers.HRV, 6, 800).save(provider);
        carrier(provider, "ptfe_membrane", TagPrefix.foil, GTMaterials.Polytetrafluoroethylene, 8, Hk3Tiers.HRV, 7, 700).save(provider);
        carrier(provider, "pbi_microcapsule", TagPrefix.foil, GTMaterials.Polybenzimidazole, 8, Hk3Tiers.HRV, 8, 1000).save(provider);
    }

    private static GTRecipeBuilder detector(String kind, String previous, int tier, String... research) {
        return base(GTRecipeTypes.ASSEMBLER_RECIPES, kind + "_honkai_detector", tier, 1000, research)
                .inputItems(item(previous + "_honkai_detector", 1))
                .inputItems(item("honkai_detector_calibration_report", 1))
                .inputItems(Hk3MainComponentRecipes.component(tier - 1, "sensor", 2))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(576))
                .outputItems(item(kind + "_honkai_detector", 1));
    }

    private static GTRecipeBuilder carrier(Consumer<FinishedRecipe> provider, String kind, TagPrefix form,
            Material material, int count, int tier, int matrixCount, int ticks) {
        String id = "honkai_" + kind + "_carrier";
        base(GTRecipeTypes.MIXER_RECIPES, id + "_fuel_matrix", tier, ticks, "RN-HFB")
                .inputItems(item(id, 1)).inputItems(TagPrefix.dust, GTMaterials.Carbon, 2)
                .inputFluids(fluid("honkai_stabilization_medium", matrixCount * 50))
                .outputItems(item("fuel_matrix", matrixCount)).save(provider);
        return base(GTRecipeTypes.ASSEMBLER_RECIPES, id, tier, ticks, "RN-HFB")
                .inputItems(form, material, count).inputItems(TagPrefix.plate, GTMaterials.Steel, 2)
                .outputItems(item(id, 4));
    }

    private static GTRecipeBuilder base(GTRecipeType type, String output, int tier, int ticks, String... research) {
        String id = "hk3gtl_supply_" + output;
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id, List.of(research));
        return Hk3RecipePower.require(type.recipeBuilder(id).duration(ticks).EUt(Hk3Values.VA_LONG[tier]), tier);
    }
}
