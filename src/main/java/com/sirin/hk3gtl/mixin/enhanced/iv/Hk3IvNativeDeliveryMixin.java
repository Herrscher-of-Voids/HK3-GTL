package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3ProductionOutput;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvNativeEngine", remap = false)
public abstract class Hk3IvNativeDeliveryMixin {
    @Shadow @Final private WorkableMultiblockMachine machine;

    @Redirect(method = {"allowed", "prepare", "advance"}, at = @At(value = "INVOKE", target =
            "Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;checkConditions(Lcom/gregtechceu/gtceu/api/machine/trait/RecipeLogic;)Lcom/gregtechceu/gtceu/api/recipe/GTRecipe$ActionResult;"))
    private GTRecipe.ActionResult hk3gtl$isolatedConditions(GTRecipe recipe, RecipeLogic recipeLogic) {
        return !Hk3RecipePower.marked(recipe) ? recipe.checkConditions(recipeLogic)
                : this instanceof Hk3PowerWork.Isolated ? Hk3RecipePower.checkIsolated(recipe, recipeLogic)
                : Hk3RecipePower.unsupportedExecutor();
    }

    @Redirect(method = "acknowledgeDelivery", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/iv/IvJob;validateAccounting()V"), require = 1)
    private void hk3gtl$recordDelivery(@Coerce Object job) {
        var access = (Hk3IvJobAccess) job;
        access.hk3gtl$validateAccounting();
        Hk3ProductionOutput.isolatedSettled(machine, access.hk3gtl$recipe());
    }
}
