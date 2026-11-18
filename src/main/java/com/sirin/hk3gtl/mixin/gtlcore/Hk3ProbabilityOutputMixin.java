package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = RecipeRunnerHelper.class, remap = false)
public abstract class Hk3ProbabilityOutputMixin {
    @Inject(method = "handleRecipeOutput", at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$escrow(IRecipeLogicMachine machine, GTRecipe recipe, CallbackInfoReturnable<Boolean> result) {
        Boolean handled = Hk3ProbabilityOrderService.output(machine, recipe);
        if (handled != null) result.setReturnValue(handled);
    }
}
