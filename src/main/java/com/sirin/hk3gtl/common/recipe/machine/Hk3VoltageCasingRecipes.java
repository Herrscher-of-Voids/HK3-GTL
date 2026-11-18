package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.data.recipe.VanillaRecipeHelper;
import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
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
import java.util.Locale;
import java.util.function.Consumer;














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
        // 结构首建不能依赖本机产物；此路线只生产外观机壳，不提供对应电压或主材。
        for (String voltage : java.util.List.of("hrv", "hdv", "civ")) {
            String id = "bootstrap_voltage_machine_casing_" + voltage;
            var recipe = GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "plate", 16))
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "frame", 2))
                    .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV, "fine_wire", 16))
                    .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, voltage.equals("hrv") ? 32 : 64)
                    .inputItems(TagPrefix.gear, GTMaterials.Neutronium, 4)
                    .inputFluids(GTMaterials.Argon.getFluid(16000))
                    .circuitMeta(voltage.equals("hrv") ? 1 : voltage.equals("hdv") ? 2 : 3)
                    .outputItems(new ItemStack(Hk3IndustrialContent.blocks().get("voltage_machine_casing_" + voltage).get()))
                    .duration(3600).EUt(Hk3Values.VA_LONG[GTValues.MAX]);
            Hk3RecipeResearchGate.bindAll("assembler", id, java.util.List.of("RN-LES"));
            Hk3RecipePower.require(recipe, GTValues.MAX).save(provider);
        }
    }
}


