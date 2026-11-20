package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.data.recipe.VanillaRecipeHelper;
import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.Locale;
import java.util.function.Consumer;

/**
 * 提供16种建筑机壳装配配方；颜色不代表电压处理能力。
 */
public final class Hk3VoltageCasingRecipes {
    private Hk3VoltageCasingRecipes() {}
    public static void register(Consumer<FinishedRecipe> provider) {
        for (var entry : Hk3MainMaterialCatalog.entries()) {
            String id = "voltage_machine_casing_" + entry.voltage().toLowerCase(Locale.ROOT);
            var block = Hk3IndustrialContent.blocks().get(id);
            if (block == null) throw new IllegalStateException("本级机械机壳未注册：" + id);
            VanillaRecipeHelper.addShapedRecipe(provider, new ResourceLocation("hk3gtl", id),
                    new ItemStack(block.get().asItem(), 1), "PPP", "P P", "PPP",
                    'P', Hk3MainMaterialItems.stack(entry.tier(), "plate", 1));
        }
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("bootstrap_voltage_machine_casing_hbv")
                .inputItems(new ItemStack(Hk3StructureBlocks.require("gtceu:max_machine_casing")))
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 32)
                .inputItems(TagPrefix.foil, GTMaterials.Polybenzimidazole, 32)
                .inputItems(TagPrefix.screw, GTMaterials.Neutronium, 32)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(2304))
                .outputItems(new ItemStack(Hk3IndustrialContent.blocks().get("voltage_machine_casing_hbv").get()))
                .duration(600).EUt(Hk3Values.VA_LONG[GTValues.MAX]).save(provider);

        // I09至I16的首建机壳由已完成的HBV材料线供应。
        for (String voltage : java.util.List.of("hrv", "civ")) {
            String id = "bootstrap_voltage_machine_casing_" + voltage;
            var recipe = GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "plate", 16))
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "frame", 2))
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "fine_wire", 16))
                    .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, voltage.equals("hrv") ? 32 : 64)
                    .inputItems(TagPrefix.screw, GTMaterials.Neutronium, 32)
                    .inputFluids(GTMaterials.Argon.getFluid(16000))
                    .circuitMeta(voltage.equals("hrv") ? 1 : 3)
                    .outputItems(new ItemStack(Hk3IndustrialContent.blocks().get("voltage_machine_casing_" + voltage).get()))
                    .duration(1200).EUt(Hk3Values.VA_LONG[GTValues.MAX]);
            Hk3RecipeResearchGate.bindAll("assembler", id, java.util.List.of("RN-LES"));
            Hk3RecipePower.require(recipe, GTValues.MAX).save(provider);
        }

        String hdvId = "bootstrap_voltage_machine_casing_hdv";
        Hk3RecipeResearchGate.bind("assembler", hdvId, "RN-LES");
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(hdvId)
                .inputItems(new ItemStack(Hk3IndustrialContent.blocks().get("voltage_machine_casing_hrv").get(), 2))
                .inputItems(TagPrefix.foil, GTLMaterials.Cosmic, 6144)
                .inputItems(TagPrefix.foil, GTLMaterials.CosmicNeutronium, 2048)
                .inputItems(TagPrefix.screw, GTMaterials.Neutronium, 4096)
                .inputItems(TagPrefix.plate, GTLMaterials.ZirconiumCarbide, 512)
                .inputItems(TagPrefix.plate, GTMaterials.Polybenzimidazole, 512)
                .inputItems(TagPrefix.plate, GTLMaterials.Shirabon, 256)
                .inputFluids(GTLMaterials.Polyimide.getFluid(294912))
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(294912))
                .inputFluids(GTLMaterials.SuperMutatedLivingSolder.getFluid(221184))
                .circuitMeta(2)
                .outputItems(new ItemStack(Hk3IndustrialContent.blocks().get("voltage_machine_casing_hdv").get()))
                .duration(6000).EUt(Hk3Values.VA_LONG[GTValues.MAX]).save(provider);
    }
}

