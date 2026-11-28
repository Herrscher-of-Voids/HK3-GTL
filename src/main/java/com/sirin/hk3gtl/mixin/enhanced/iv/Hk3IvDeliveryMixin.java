package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.sirin.hk3gtl.common.research.Hk3ProductionOutput;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvRecipeLogic", remap = false)
public abstract class Hk3IvDeliveryMixin {
    @Redirect(method = "acknowledgeDelivery", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvJob;validateAccounting()V"), require = 1)
    private void hk3gtl$recordDelivery(@Coerce Object job) {
        var access = (Hk3IvJobAccess) job;
        access.hk3gtl$validateAccounting();
        Hk3ProductionOutput.isolatedSettled(((RecipeLogic) (Object) this).getMachine(), access.hk3gtl$recipe());
    }
}
