package com.sirin.hk3gtl.mixin.jei;

import mezz.jei.gui.recipes.RecipeGuiLogic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(value = RecipeGuiLogic.class, remap = false)
abstract class Hk3JeiSingleRecipePageMixin {
    @ModifyArg(method = "getVisibleRecipeLayoutsWithButtons", at = @At(value = "INVOKE", target =
            "Lmezz/jei/gui/recipes/lookups/ILookupState;setRecipesPerPage(I)V"))
    private int hk3gtl$oneRecipePerPage(int recipesPerPage) {
        return 1;
    }
}
