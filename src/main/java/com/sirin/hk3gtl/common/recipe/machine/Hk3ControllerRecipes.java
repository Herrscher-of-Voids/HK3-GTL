package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.machine.Hk3IndustrialExtensionMachines;
import com.sirin.hk3gtl.common.machine.Hk3LateIndustrialMachines;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachines;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderMachines;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessTypes;
import com.sirin.hk3gtl.common.recipe.main.Hk3MainComponentRecipes;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.List;
import java.util.function.Consumer;

public final class Hk3ControllerRecipes {
    private record Controller(String key, String research) {}

    private static final List<Controller> INDUSTRIAL = List.of(
            new Controller("i19", "RN-SRE"), new Controller("i20", "RN-MRE"),
            new Controller("i21", "RN-LRE"), new Controller("i22", "RN-URE"),
            new Controller("i23", "RN-HER"), new Controller("i24", "RN-QOM"),
            new Controller("i25", "RN-WCP"), new Controller("i26", "RN-UED"),
            new Controller("i27", "RN-WBC"), new Controller("i28", "RN-WTR"),
            new Controller("i29", "RN-SWC"), new Controller("i30", "RN-SWS"),
            new Controller("i31", "RN-SWR"), new Controller("i32", "RN-LTA"),
            new Controller("i33", "RN-DKE"), new Controller("i34", "RN-IOP"),
            new Controller("i35", "RN-IAA"), new Controller("i36", "RN-RAT"),
            new Controller("i37", "RN-WME"),
            new Controller("i38", "RN-ESC"), new Controller("i39", "RN-VRC"),
            new Controller("i40", "RN-WMS"), new Controller("i41", "RN-CED"),
            new Controller("i42", "RN-WPF"), new Controller("i43", "RN-CEE"),
            new Controller("i44", "RN-CJK"), new Controller("i45", "RN-CJK"));

    private static final List<Controller> WONDERS = List.of(
            new Controller("W01", "RN-HCCO"), new Controller("W02", "RN-AIM"),
            new Controller("W03", "RN-IAR"), new Controller("W04", "RN-SEM"),
            new Controller("W05", "RN-IFF"), new Controller("W06", "RN-CCF"),
            new Controller("W07", "RN-MRA"), new Controller("W08", "RN-SFF"),
            new Controller("W09", "RN-CKV"), new Controller("W10", "RN-GSF"),
            new Controller("W11", "RN-DIO"), new Controller("W12", "RN-ECB"),
            new Controller("W13", "RN-ASR"), new Controller("W14", "RN-WCE"),
            new Controller("W15", "RN-TAA"));

    private Hk3ControllerRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        controller(provider, "i18", Hk3IndustrialExtensionMachines.HONKAI_FUEL_ROD_ENCAPSULATION_ARRAY,
                GTValues.MAX, List.of("RN-FRP"));
        for (var entry : INDUSTRIAL) {
            var machine = Hk3LateIndustrialMachines.get(entry.key());
            controller(provider, entry.key(), machine, Math.max(GTValues.MAX, machine.getTier() - 1),
                    List.of(entry.research()));
        }
        controller(provider, "hyperion", Hk3HyperionMachines.FLAGSHIP, GTValues.MAX,
                List.of("RN-HBD", "RN-HVI"));
        var first = WONDERS.get(0);
        controller(provider, first.key().toLowerCase(java.util.Locale.ROOT),
                Hk3WonderMachines.get(first.key()), inputTier(first.key()), List.of(first.research()));
        for (int i = 1; i < WONDERS.size(); i++) {
            var predecessor = WONDERS.get(i - 1);
            var target = WONDERS.get(i);
            wonderController(provider, predecessor, target);
        }
        erosionModule(provider);
    }

    private static int inputTier(String key) {
        return switch (key) {
            case "W01", "W02", "W04", "W05", "W06" -> Hk3Tiers.WFV;
            case "W03", "W07", "W08", "W10", "W12" -> Hk3Tiers.WSV;
            default -> Hk3Tiers.CIV;
        };
    }

    private static void wonderController(Consumer<FinishedRecipe> provider, Controller predecessor, Controller target) {
        String id = "hk3gtl_controller_" + target.key().toLowerCase(java.util.Locale.ROOT);
        var machine = Hk3WonderMachines.get(predecessor.key());
        int materialTier = inputTier(target.key());
        var recipe = Hk3ResearchProcessTypes.get(predecessor.key()).recipeBuilder(id)
                .inputItems(Hk3CircuitCatalog.tag(materialTier), 8)
                .inputItems(Hk3MainComponentRecipes.component(materialTier, "robot_arm", 4))
                .inputItems(Hk3MainComponentRecipes.component(materialTier, "field_generator", 4))
                .inputItems(Hk3MainComponentRecipes.component(materialTier, "sensor", 4))
                .inputItems(Hk3MainComponentRecipes.component(materialTier, "emitter", 2))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(4608))
                .outputItems(Hk3WonderMachines.get(target.key()).asStack()).duration(2400)
                .EUt(Hk3Values.VA_LONG[machine.getTier()]);
        if (materialTier == GTValues.MAX) {
            recipe.inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 32)
                    .inputItems(TagPrefix.frameGt, GTMaterials.TungstenSteel, 8)
                    .inputItems(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 32);
        } else {
            recipe.inputItems(Hk3MainMaterialItems.stack(materialTier, "plate", 32))
                    .inputItems(Hk3MainMaterialItems.stack(materialTier, "frame", 8))
                    .inputItems(Hk3MainMaterialItems.stack(materialTier, "fine_wire", 32));
        }
        Hk3RecipePower.require(recipe, machine.getTier()).save(provider);
        var type = Hk3ResearchProcessTypes.get(predecessor.key());
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id,
                List.of(predecessor.research(), target.research()));
    }

    // 首建只消耗前置档材料，目标机器的工艺产物不进入自己的控制器配方。
    private static void controller(Consumer<FinishedRecipe> provider, String key,
                                   MultiblockMachineDefinition machine, int inputTier, List<String> research) {
        String id = "hk3gtl_controller_" + key;
        var recipe = GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                .inputItems(inputTier == GTValues.MAX ? CustomTags.MAX_CIRCUITS : Hk3CircuitCatalog.tag(inputTier), 8)
                .inputItems(Hk3MainComponentRecipes.component(inputTier, "robot_arm", 4))
                .inputItems(Hk3MainComponentRecipes.component(inputTier, "field_generator", 4))
                .inputItems(Hk3MainComponentRecipes.component(inputTier, "sensor", 4))
                .inputItems(Hk3MainComponentRecipes.component(inputTier, "emitter", 2))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(4608))
                .outputItems(machine.asStack()).duration(2400).EUt(Hk3Values.VA_LONG[inputTier]);
        if (inputTier == GTValues.MAX) {
            recipe.inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 32)
                    .inputItems(TagPrefix.frameGt, GTMaterials.TungstenSteel, 8)
                    .inputItems(TagPrefix.wireFine, GTMaterials.NiobiumTitanium, 32);
        } else {
            recipe.inputItems(Hk3MainMaterialItems.stack(inputTier, "plate", 32))
                    .inputItems(Hk3MainMaterialItems.stack(inputTier, "frame", 8))
                    .inputItems(Hk3MainMaterialItems.stack(inputTier, "fine_wire", 32));
        }
        Hk3RecipePower.require(recipe, inputTier).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", id, research);
    }

    private static void erosionModule(Consumer<FinishedRecipe> provider) {
        String id = "hk3gtl_erosion_research_module";
        int tier = Hk3Tiers.HDV;
        var recipe = GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                .inputItems(Hk3CircuitCatalog.tag(tier), 4)
                .inputItems(Hk3MainComponentRecipes.component(tier, "sensor", 4))
                .inputItems(Hk3MainComponentRecipes.component(tier, "emitter", 2))
                .inputItems(Hk3MainMaterialItems.stack(tier, "plate", 8))
                .inputItems(Hk3MainMaterialItems.stack(tier, "fine_wire", 16))
                .inputItems(new ItemStack(Hk3IndustrialContent.items().get("circuit_encapsulation_part").get(), 4))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(1152))
                .outputItems(Hk3Items.EROSION_RESEARCH_MODULE.get()).duration(1200).EUt(Hk3Values.VA_LONG[tier]);
        Hk3RecipePower.require(recipe, tier).save(provider);
        Hk3RecipeResearchGate.bindAll("assembler", id, List.of("RN-ECA", "RN-ALE"));
    }
}
