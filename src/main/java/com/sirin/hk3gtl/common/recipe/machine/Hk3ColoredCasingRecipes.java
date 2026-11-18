package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

public final class Hk3ColoredCasingRecipes {
    private Hk3ColoredCasingRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        for (DyeColor color : DyeColor.values()) {
            GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(
                    new ResourceLocation("hk3gtl", "casing_colored_" + color.getName()))
                    .inputItems(TagPrefix.plate, GTMaterials.Steel, 6)
                    .inputItems(TagPrefix.frameGt, GTMaterials.Steel, 1)
                    .inputItems(new ItemStack(DyeItem.byColor(color)))
                    .outputItems(new ItemStack(CasingBlocks.ALL_COLORED_CASINGS[color.getId()].get(), 2))
                    .duration(100).EUt(30).save(provider);
        }
    }
}
