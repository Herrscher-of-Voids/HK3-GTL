package com.sirin.hk3gtl.mixin.jei;

import com.gregtechceu.gtceu.integration.jei.recipe.GTRecipeWrapper;
import mezz.jei.common.util.ImmutableRect2i;
import mezz.jei.library.gui.recipes.RecipeLayout;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = RecipeLayout.class, remap = false)
abstract class Hk3JeiRecipeHeightMixin<R> {
    @Shadow @Final private R recipe;
    @Shadow private ImmutableRect2i area;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$includeGtRecipeNotes(CallbackInfo ci) {
        if (recipe instanceof GTRecipeWrapper gtRecipe && gtRecipe.modularUI.getHeight() > area.getHeight()) {
            area = new ImmutableRect2i(area.getX(), area.getY(), area.getWidth(), gtRecipe.modularUI.getHeight());
        }
    }
}
