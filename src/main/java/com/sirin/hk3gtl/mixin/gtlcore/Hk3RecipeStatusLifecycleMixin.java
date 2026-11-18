package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import org.gtlcore.gtlcore.api.machine.trait.IRecipeStatus;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = RecipeLogic.class, remap = false, priority = 1001)
public abstract class Hk3RecipeStatusLifecycleMixin {
    @Inject(method = "setupRecipe", at = @At(value = "INVOKE",
            target = "Lcom/gregtechceu/gtceu/api/machine/trait/RecipeLogic;setStatus(Lcom/gregtechceu/gtceu/api/machine/trait/RecipeLogic$Status;)V",
            shift = At.Shift.AFTER), require = 1)
    private void hk3gtl$clearStartedRecipeFailure(GTRecipe recipe, CallbackInfo ci) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (logic.isWorking()) {
            IRecipeStatus status = (IRecipeStatus) logic;
            status.setRecipeStatus(null);
            status.setWorkingStatus(null);
        }
    }
}
