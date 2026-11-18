package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 增强版IV多任务执行器的工业降效，只拦截扣电与工时推进前的advance。
 */
@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvRecipeLogic", remap = false)
public abstract class EnhancedIndustrialGazeMixin {
    @Inject(method = "advance(Ljava/util/List;Lcom/gtl/enhancedcore/common/machine/TieredParallelMachine;)V",
            at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$guardIndustrialAdvance(CallbackInfo callback) {
        try {
            if (Hk3RecipeEnvironment.throttlesByGaze(((RecipeLogic) (Object) this).getMachine()))
                callback.cancel();
        } catch (RuntimeException unavailable) {
            callback.cancel();
        }
    }
}
