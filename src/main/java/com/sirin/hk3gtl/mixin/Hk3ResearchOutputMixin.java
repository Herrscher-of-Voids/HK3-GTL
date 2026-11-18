package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3ProductionOutput;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value=RecipeRunnerHelper.class, remap=false)
public abstract class Hk3ResearchOutputMixin {
    /** 仅服务端真实成功输出触发；各设备负责检查归属、研究及批次幂等性。 */
    @Inject(method="handleRecipeOutput(Lcom/gregtechceu/gtceu/api/machine/feature/IRecipeLogicMachine;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Z",
            at=@At("RETURN"), remap=false, require=1)
    private static void hk3gtl$recordSampling(IRecipeLogicMachine machine, GTRecipe recipe, CallbackInfoReturnable<Boolean> result) {
        if (Boolean.TRUE.equals(result.getReturnValue())) Hk3ProductionOutput.settled(machine, recipe);
    }
}
