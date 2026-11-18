package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import java.util.function.Consumer;

import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;

/** 首批普通燃料棒的低吞吐封装与无损抽检；实验记录不代替正式研究。 */
public final class Hk3FuelRodBootstrapRecipes {
    private Hk3FuelRodBootstrapRecipes() {}

    /** 全链以已有MAX设备启动；封装研究及其后继不能成为自身实验的门槛。 */
    private static GTRecipeBuilder recipe(GTRecipeType type, String id, int ticks) {
        Hk3RecipeResearchGate.bind(type.registryName.getPath(), id, "RN-HFB");
        return type.recipeBuilder(new ResourceLocation("hk3gtl", id))
                .duration(ticks).EUt(Hk3Values.VA_LONG[GTValues.MAX]);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        recipe(GTRecipeTypes.ASSEMBLER_RECIPES, "industrial_fuel_rod_casing", 400)
                .circuitMeta(21)
                .inputItems(TagPrefix.plate, GTMaterials.TungstenSteel, 4)
                .inputItems(TagPrefix.foil, GTMaterials.Platinum, 2)
                .inputFluids(GTMaterials.SolderingAlloy.getFluid(144))
                .outputItems(item("honkai_fuel_rod_casing", 2)).save(provider);

        recipe(GTRecipeTypes.ASSEMBLER_RECIPES, "industrial_fuel_encapsulation_part", 300)
                .circuitMeta(22)
                .inputItems(TagPrefix.plate, GTMaterials.Polytetrafluoroethylene, 2)
                .inputItems(TagPrefix.foil, GTMaterials.Platinum, 2)
                .outputItems(item("fuel_encapsulation_part", 4)).save(provider);

        // 灌装机使用两个物品输入；不加入编程电路，以免超出原配方类型槽位。
        recipe(GTRecipeTypes.CANNER_RECIPES, "industrial_fuel_rod_bootstrap_encapsulation", 4000)
                .inputItems(item("honkai_fuel_rod_casing", 1), item("fuel_encapsulation_part", 2))
                .inputFluids(fluid("liquid_honkai_fuel", 1000))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get())).save(provider);

        recipe(Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS, "industrial_fuel_rod_isolation_experiment", 800)
                .circuitMeta(3)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get()))
                .notConsumable(item("honkai_reference_sample", 1))
                .inputItems(Items.PAPER, 2)
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get()))
                .addData(Hk3LiquidProcessMachine.EXPERIMENT, "RN-FRP").save(provider);
    }
}

