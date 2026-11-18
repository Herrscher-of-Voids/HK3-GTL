package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.recipe.main.Hk3MainComponentRecipes;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;

import java.util.List;
import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;

public final class Hk3FunctionalItemRecipes {
    private Hk3FunctionalItemRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        for (var circuit : Hk3CircuitItems.HONKAI_CIRCUITS.entrySet()) {
            TagKey<Item> input = TagKey.create(Registries.ITEM,
                    new ResourceLocation("gtceu", "circuits/" + circuit.getKey()));
            base(GTRecipeTypes.ASSEMBLER_RECIPES, "honkai_circuit_" + circuit.getKey(), GTValues.MAX, "RN-BCE")
                    .inputItems(input, 1).inputItems(item("honkai_adapted_circuit_substrate", 1))
                    .inputItems(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get())
                    .inputFluids(GTMaterials.SolderingAlloy.getFluid(144))
                    .outputItems(circuit.getValue().get()).save(provider);
        }
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "gaze_buffer_unit", GTValues.MAX, "RN-BCE")
                .inputItems(Hk3MainComponentRecipes.component(GTValues.MAX, "field_generator", 1))
                .inputItems(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 4)
                .inputItems(TagPrefix.plate, GTMaterials.Lead, 8)
                .inputItems(TagPrefix.foil, GTMaterials.Polybenzimidazole, 8)
                .outputItems(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get()).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "advanced_gaze_buffer_unit", Hk3Tiers.HDV, "RN-ERA")
                .inputItems(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 4)
                .inputItems(Hk3MainComponentRecipes.component(Hk3Tiers.HDV, "field_generator", 1))
                .inputItems(item("circuit_encapsulation_part", 4))
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 1000))
                .outputItems(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get()).save(provider);
        base(GTRecipeTypes.LASER_ENGRAVER_RECIPES, "precivilization_fragment_analysis", Hk3Tiers.QEV, "RN-LTA")
                .inputItems(item("world_mining_legacy_record", 1))
                .inputItems(TagPrefix.plate, GTMaterials.Silicon, 4)
                .outputItems(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 4).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "data_research_package", Hk3Tiers.QEV, "RN-LTA")
                .inputItems(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 2)
                .inputItems(item("soulium_data_substrate", 2), item("circuit_encapsulation_part", 2))
                .outputItems(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get()).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "ancient_legacy_reconstruction", Hk3Tiers.QEV, "RN-LTA")
                .inputItems(AbyssFunctionalItems.DATA_PRECIVILIZATION_FRAGMENT.get(), 4)
                .inputItems(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get())
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 4)
                .outputItems(HonkaiMaterialItems.ANCIENT_LEGACY.get()).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "ancient_will_reconstruction", Hk3Tiers.QEV, "RN-LTA")
                .inputItems(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 2)
                .inputItems(item("world_model_carrier", 1), item("circuit_encapsulation_part", 4))
                .outputItems(HonkaiMaterialItems.ANCIENT_WILL.get()).save(provider);
        base(GTRecipeTypes.CHEMICAL_BATH_RECIPES, "world_bubble_observation_sample", Hk3Tiers.QCV, "RN-QOM")
                .inputItems(item("world_model_carrier", 1))
                .inputItems(TagPrefix.dust, GTMaterials.Quartzite, 4)
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 500))
                .outputItems(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 4).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "world_matter_seed", Hk3Tiers.QAV, "RN-SWC")
                .inputItems(item("soulium_data_substrate", 8))
                .inputItems(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 4)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 8)
                .inputItems(TagPrefix.dust, GTMaterials.Quartzite, 16)
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 2000))
                .outputItems(item("world_matter_seed", 1)).save(provider);
        base(GTRecipeTypes.MIXER_RECIPES, "soulium_precursor_mix", GTValues.MAX, "RN-SSP")
                .inputItems(TagPrefix.dust, GTMaterials.Titanium, 8)
                .inputItems(TagPrefix.dust, GTMaterials.Platinum, 2)
                .inputFluids(fluid("soulium_precursor_fluid", 1000))
                .outputItems(SouliumChainItems.SOULIUM_PRECURSOR_MIX.get(), 8).save(provider);
        base(GTRecipeTypes.ASSEMBLER_RECIPES, "activated_nano_matrix", GTValues.MAX, "RN-NSP")
                .inputItems(item("controlled_nano_swarm", 4), item("nano_building_unit", 4))
                .inputFluids(fluid("circuit_growth_medium", 500))
                .outputItems(SouliumChainItems.ACTIVATED_NANO_MATRIX.get()).save(provider);
        Hk3IndustrialSupplyRecipes.register(provider);
    }

    private static GTRecipeBuilder base(GTRecipeType type, String output, int tier, String research) {
        String id = "hk3gtl_functional_" + output;
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id, List.of(research));
        return Hk3RecipePower.require(type.recipeBuilder(id).duration(600).EUt(Hk3Values.VA_LONG[tier]), tier);
    }
}
