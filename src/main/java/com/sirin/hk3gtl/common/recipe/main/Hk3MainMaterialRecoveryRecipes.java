package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import net.minecraft.data.recipes.FinishedRecipe;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.*;

/**
 * 同级制造边角料及拒收批的有损回收，不按名称混收，也不让小件返还整坯。
 */
final class Hk3MainMaterialRecoveryRecipes {
    private Hk3MainMaterialRecoveryRecipes() {}

    static void register(int tier, Consumer<FinishedRecipe> out) {
        for (String form : new String[]{"billet", "plate", "rod", "fine_wire", "ring", "foil", "frame", "rejected_batch"}) {
            int units = Hk3MainMaterialUnits.perItem(form);
            int inputs = units < 144 ? 144 / units : 1;
            int outputs = units > 144 ? units / 144 : 1;
            Hk3MainMaterialUnits.requireConversion(form, inputs, "classified_scrap", outputs);
            process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "dismantle_" + form, 800)
                    .inputItems(material(tier, form, inputs))
                    .inputFluids(fluid("gtceu:hydrochloric_acid", 1000), fluid("gtceu:distilled_water", 1000))
                    .outputItems(material(tier, "classified_scrap", outputs)).save(out);
        }

        Hk3MainMaterialUnits.requireBalanced(Hk3MainMaterialUnits.amount("classified_scrap", 8),
                Hk3MainMaterialUnits.amount("recovered_fraction", 48) + Hk3MainMaterialUnits.amount("unrecoverable_tailings", 16));
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "lossy_phase_separation", 2400)
                .inputItems(material(tier, "classified_scrap", 8)).inputFluids(fluid("gtceu:argon", 8000))
                .outputItems(material(tier, "recovered_fraction", 48), material(tier, "unrecoverable_tailings", 16)).save(out);

        Hk3MainMaterialUnits.requireConversion("recovered_fraction", 8, "billet", 1);
        process(GTLRecipeTypes.SPS_CRAFTING_RECIPES, tier, "fresh_feed_reconstitution", 3200)
                .inputItems(material(tier, "recovered_fraction", 8), external("gtceu:shirabon_foil", 4))
                .inputFluids(fluid("gtceu:argon", 8000)).outputItems(material(tier, "billet", 1)).save(out);
        process(GTRecipeTypes.LARGE_CHEMICAL_RECIPES, tier, "irreversible_tailings_inerting", 1200)
                .inputItems(material(tier, "unrecoverable_tailings", 16))
                .inputFluids(fluid("gtceu:distilled_water", 1000))
                .outputItems(TagPrefix.dust, GTMaterials.Ash, 2).save(out);
    }
}
