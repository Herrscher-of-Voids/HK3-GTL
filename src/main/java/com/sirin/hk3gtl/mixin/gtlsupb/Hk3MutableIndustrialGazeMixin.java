package com.sirin.hk3gtl.mixin.gtlsupb;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "com.gtlsupb.gtlsupb.api.machine.logic.MutableRecipesLogic", remap = false)
public abstract class Hk3MutableIndustrialGazeMixin {
    @Inject(method = "handleMultipleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$multipleWorking(CallbackInfo callback) {
        if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine()))
            callback.cancel();
    }

    @Inject(method = "tickConcurrentBatch", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$concurrentWorking(CallbackInfoReturnable<Boolean> callback) {
        if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine()))
            callback.setReturnValue(false);
    }
}
