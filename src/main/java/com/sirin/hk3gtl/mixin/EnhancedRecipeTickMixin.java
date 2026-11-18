package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

 





 





 




@Mixin(value = RecipeLogic.class, remap = false)
public abstract class EnhancedRecipeTickMixin {
    private static final GTRecipe.ActionResult HK3GTL$PAUSED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.compat.environment_paused"));

    @Inject(method = "handleTickRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$checkEnhancedTick(GTRecipe recipe, CallbackInfoReturnable<GTRecipe.ActionResult> result) {
        try {
            var power = Hk3RecipePower.check(recipe, (RecipeLogic) (Object) this);
            if (!power.isSuccess()) {
                result.setReturnValue(power);
                return;
            }
            var machine = ((RecipeLogic) (Object) this).getMachine();
            if (Hk3RecipeAccess.blocks(recipe, machine)
                    || Hk3RecipeEnvironment.throttlesByGaze(machine)) result.setReturnValue(HK3GTL$PAUSED);
        } catch (RuntimeException exception) {
            result.setReturnValue(HK3GTL$PAUSED);
        }
    }
}
