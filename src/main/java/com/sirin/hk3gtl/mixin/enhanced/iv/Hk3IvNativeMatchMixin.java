package com.sirin.hk3gtl.mixin.enhanced.iv;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.recipe.power.Hk3IsolatedPower;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.common.recipe.iv.IvNativeMatchContext", remap = false)
public abstract class Hk3IvNativeMatchMixin {
    @Shadow @Final private WorkableMultiblockMachine machine;
    @Shadow @Final private long capacity;
    @Shadow public abstract long limit(GTRecipe recipe, long requested);
    @Shadow public abstract void reserved(long value);

    @WrapOperation(method = "lambda$prepare$0", at = @At(value = "INVOKE", target =
            "Lcom/gtl/enhancedcore/common/recipe/RecipeBatchPreparation;apply(Lcom/gregtechceu/gtceu/api/machine/MetaMachine;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$exactBatch(MetaMachine host, GTRecipe origin, GTRecipe modified, Operation<GTRecipe> original) {
        if (!Hk3RecipePower.marked(origin)) return original.call(host, origin, modified);
        if (modified == null) return null;
        RecipeLogic logic = machine.getRecipeLogic();
        long parallel = limit(origin, Hk3IsolatedPower.parallel(logic, origin, capacity));
        if (parallel == 0) return null;
        reserved(parallel);
        return Hk3IsolatedPower.scale(origin, parallel);
    }
}
