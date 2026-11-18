package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

import java.util.Set;
import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.*;









final class Hk3MainMaterialFormRecipes {
    private static final Set<Integer> METALLIC = Set.of(Hk3Tiers.HBV, Hk3Tiers.HRV, Hk3Tiers.HDV, Hk3Tiers.IRV);
    private static final Set<Integer> CERAMIC = Set.of(Hk3Tiers.HCV, Hk3Tiers.IMV);

    private Hk3MainMaterialFormRecipes() {}

    static void register(int tier, Consumer<FinishedRecipe> out) {
        Hk3MainMaterialUnits.requireConversion("billet", 8, "plate", 8);
        if (tier == Hk3Tiers.HBV) {
            process(GTRecipeTypes.BENDER_RECIPES, tier, GTValues.MAX, "max_seed_plate", 6400)
                    .inputItems(material(tier, "billet", 8)).circuitMeta(1)
                    .outputItems(material(tier, "plate", 8)).save(out);
        }
        if (METALLIC.contains(tier)) {
            process(GTRecipeTypes.BENDER_RECIPES, tier, "oriented_metal_plate", 1600 + (tier - Hk3Tiers.HBV) * 200)
                    .inputItems(material(tier, "billet", 8)).circuitMeta(1)
                    .outputItems(material(tier, "plate", 8)).save(out);
        } else if (CERAMIC.contains(tier)) {
            process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, tier, "protected_atmosphere_ceramic_plate", 2800 + (tier - Hk3Tiers.HBV) * 200)
                    .inputItems(material(tier, "billet", 8)).inputFluids(fluid("gtceu:argon", 16000))
                    .outputItems(material(tier, "plate", 8)).save(out);
        } else {
            process(GTRecipeTypes.FORMING_PRESS_RECIPES, tier, "composite_laminate_plate", 2400 + (tier - Hk3Tiers.HBV) * 200)
                    .inputItems(material(tier, "billet", 8)).outputItems(material(tier, "plate", 8)).save(out);
        }

        conversion(tier, "billet", 2, "rod", 4, "formed_loadbearing_rods", out);
        conversion(tier, "rod", 1, "ring", 2, "formed_interface_rings", out);
        conversion(tier, "plate", 1, "foil", 4, "functional_thin_layers", out);
        conversion(tier, "rod", 8, "frame", 1, "loadbearing_frame_assembly", out);

        Hk3MainMaterialUnits.requireConversion("rod", 1, "fine_wire", 4);
        var wire = process(GTRecipeTypes.WIREMILL_RECIPES, tier, "functional_fine_wire", 1200 + (tier - Hk3Tiers.HBV) * 100)
                .inputItems(material(tier, "rod", 1));
        if (!METALLIC.contains(tier)) wire.inputItems(external("gtceu:fine_shirabon_wire", 4));
        wire.outputItems(material(tier, "fine_wire", 4)).save(out);
        if (tier == Hk3Tiers.HBV) {
            process(GTRecipeTypes.WIREMILL_RECIPES, tier, GTValues.MAX, "max_seed_fine_wire", 9600)
                    .inputItems(material(tier, "rod", 1)).outputItems(material(tier, "fine_wire", 4)).save(out);
        }
    }

    private static void conversion(int tier, String input, int inputs, String output, int outputs,
                                   String id, Consumer<FinishedRecipe> out) {
        Hk3MainMaterialUnits.requireConversion(input, inputs, output, outputs);
        process(GTRecipeTypes.FORMING_PRESS_RECIPES, tier, id, 1200 + (tier - Hk3Tiers.HBV) * 100)
                .inputItems(material(tier, input, inputs)).outputItems(material(tier, output, outputs)).save(out);
        if (tier == Hk3Tiers.HBV) {
            process(GTRecipeTypes.FORMING_PRESS_RECIPES, tier, GTValues.MAX, "max_seed_" + id, 9600)
                    .inputItems(material(tier, input, inputs)).outputItems(material(tier, output, outputs)).save(out);
        }
    }
}
