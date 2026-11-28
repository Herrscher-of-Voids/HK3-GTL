package com.sirin.hk3gtl.mixin.gtladd;

import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

@Pseudo
@Mixin(targets = "com.gtladd.gtladditions.api.machine.logic.GTLAddMultipleRecipesLogic", remap = false)
public abstract class Hk3AddPowerBatchMixin implements Hk3PowerWork.Batch {
    @Shadow protected abstract boolean checkBeforeWorking();
    @Shadow protected abstract Set<GTRecipe> lookupRecipeIterator();
    @Unique private List<GTRecipe> hk3gtl$receipts;

    @WrapOperation(method = {"findAndHandleRecipe", "onRecipeFinish"}, at = @At(value = "INVOKE", target =
            "Lcom/gtladd/gtladditions/api/machine/logic/GTLAddMultipleRecipesLogic;getGTRecipe()Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;"))
    private GTRecipe hk3gtl$planExact(@Coerce Object logic, Operation<GTRecipe> original) {
        RecipeLogic worker = (RecipeLogic) logic;
        if (Arrays.stream(((WorkableMultiblockMachine) worker.getMachine()).getRecipeTypes())
                .anyMatch(Hk3PowerPorts::usesExtendedVoltage) && checkBeforeWorking()) {
            for (GTRecipe recipe : lookupRecipeIterator()) {
                if (!Hk3RecipePower.marked(recipe)) continue;
                GTRecipe fixed = worker.machine.doModifyRecipe(recipe.copy(), new OCParams(), new OCResult());
                if (fixed != null && RecipeRunnerHelper.matchRecipe(worker.machine, fixed)
                        && fixed.checkConditions(worker).isSuccess() && fixed.matchTickRecipe(worker.machine).isSuccess()) return fixed;
            }
        }
        hk3gtl$receipts = new ArrayList<>();
        try {
            GTRecipe batch = original.call(logic);
            if (batch != null) for (GTRecipe executed : hk3gtl$receipts) Hk3ResearchRecipeRuntime.mergeReceipt(batch, executed);
            return batch;
        } finally { hk3gtl$receipts = null; }
    }

    @Inject(method = "getMaxParallel", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$excludeFixedFromPooling(GTRecipe recipe, long budget, CallbackInfoReturnable<Long> result) {
        if (Hk3RecipePower.marked(recipe)) result.setReturnValue(0L);
    }

    @WrapOperation(method = {"buildFinalNormalRecipe", "buildFinalWirelessRecipe"}, at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/api/recipe/RecipeRunnerHelper;handleRecipeInput(Lcom/gregtechceu/gtceu/api/machine/feature/IRecipeLogicMachine;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Z"))
    private boolean hk3gtl$captureReceipt(IRecipeLogicMachine machine, GTRecipe recipe, Operation<Boolean> original) {
        boolean consumed = original.call(machine, recipe);
        if (consumed && hk3gtl$receipts != null && recipe.data.contains(Hk3ResearchRecipeRuntime.PLAN)) hk3gtl$receipts.add(recipe);
        return consumed;
    }
}
