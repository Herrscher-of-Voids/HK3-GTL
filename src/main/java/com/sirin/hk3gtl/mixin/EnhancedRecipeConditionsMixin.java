package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = GTRecipe.class, remap = false)
public abstract class EnhancedRecipeConditionsMixin {
    private static final GTRecipe.ActionResult HK3GTL$LOCKED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.compat.research_locked"));

    @Inject(method = "checkConditions", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$checkEnhancedResearch(RecipeLogic logic, CallbackInfoReturnable<GTRecipe.ActionResult> result) {
        try {
            var power = Hk3RecipePower.check((GTRecipe) (Object) this, logic);
            if (!power.isSuccess()) {
                result.setReturnValue(power);
                return;
            }
            var recipe = (GTRecipe) (Object) this;
            var machine = logic.getMachine();
            if (Hk3RecipeAccess.blocks(recipe, machine)) {
                var reason = Hk3RecipeAccess.blockedReason(recipe, machine);
                result.setReturnValue(GTRecipe.ActionResult.fail(() -> reason));
            }
        } catch (RuntimeException exception) {
            result.setReturnValue(HK3GTL$LOCKED);
        }
    }
}
