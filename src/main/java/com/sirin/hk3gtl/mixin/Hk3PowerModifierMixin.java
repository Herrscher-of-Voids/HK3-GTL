package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;













@Mixin(value = WorkableMultiblockMachine.class, remap = false)
public abstract class Hk3PowerModifierMixin {
    @Inject(method = "doModifyRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$fixedPower(GTRecipe recipe, OCParams params, OCResult result, CallbackInfoReturnable<GTRecipe> callback) {
        if (!Hk3RecipePower.marked(recipe)) return;
        GTRecipe validation = recipe.copy();
        validation.data = recipe.data.copy();
        for (var part : ((WorkableMultiblockMachine) (Object) this).getParts()) {
            validation = part.modifyRecipe(validation);
            if (validation == null) { callback.setReturnValue(null); return; }
        }
        callback.setReturnValue(recipe.copy());
    }
}
