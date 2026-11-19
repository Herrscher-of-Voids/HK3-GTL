package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.capability.IDataAccessHatch;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.common.recipe.condition.ResearchCondition;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Collection;

@Pseudo
@Mixin(targets = {
        "org.gtlcore.gtlcore.common.machine.multiblock.part.WirelessOpticalDataHatchMachine",
        "com.gtladd.gtladditions.common.machine.hatch.CloudOpticalDataHatchMachine"
}, remap = false)
public abstract class Hk3OpticalResearchConditionMixin {
    @Inject(method = "isRecipeAvailable(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;Ljava/util/Collection;)Z",
            at = @At("HEAD"), cancellable = true)
    private void hk3gtl$skipUnusedResearch(GTRecipe recipe, Collection<IDataAccessHatch> seen,
                                         CallbackInfoReturnable<Boolean> result) {
        if (recipe.conditions.stream().noneMatch(ResearchCondition.class::isInstance)) {
            result.setReturnValue(true);
        }
    }
}
