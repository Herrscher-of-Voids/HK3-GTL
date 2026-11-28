package com.sirin.hk3gtl.mixin.gtladd;

import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerWork;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.gtlcore.gtlcore.api.machine.trait.ILockRecipe;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.function.BiPredicate;

@Pseudo
@Mixin(targets = "com.gtladd.gtladditions.api.machine.logic.MutableRecipesLogic", remap = false)
public abstract class Hk3SuprachronalPowerMixin extends RecipeLogic implements Hk3PowerWork.Mutable, ILockRecipe {
    @Shadow @Final private BiPredicate<GTRecipe, IRecipeLogicMachine> recipeCheck;

    protected Hk3SuprachronalPowerMixin(IRecipeLogicMachine machine) {
        super(machine);
    }

    @Override
    public boolean hk3gtl$usesFixedMutablePower() {
        return Hk3PowerPorts.usesExtendedVoltage(machine.getRecipeType());
    }

    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$workFixed(CallbackInfo callback) {
        if (hk3gtl$usesFixedMutablePower() && Hk3RecipePower.marked(lastRecipe)) {
            super.handleRecipeWorking();
            callback.cancel();
        }
    }

    @Inject(method = "onRecipeFinish", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$finishFixed(CallbackInfo callback) {
        if (hk3gtl$usesFixedMutablePower() && Hk3RecipePower.marked(lastRecipe)) {
            super.onRecipeFinish();
            callback.cancel();
        }
    }

    @Shadow public abstract boolean isMultipleRecipeMode();

    @Inject(method = "findAndHandleRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$findSingleFixed(CallbackInfo callback) {
        if (isMultipleRecipeMode()) return;
        GTRecipe fixed = hk3gtl$findFixed();
        if (fixed != null) {
            lastRecipe = null;
            setupRecipe(fixed);
            callback.cancel();
        }
    }

    @Inject(method = "getRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$findFixedBeforePooling(CallbackInfoReturnable<GTRecipe> callback) {
        GTRecipe fixed = hk3gtl$findFixed();
        if (fixed != null) callback.setReturnValue(fixed);
    }

    @Unique
    private GTRecipe hk3gtl$findFixed() {
        if (!hk3gtl$usesFixedMutablePower() || !machine.hasProxies()) return null;
        GTRecipe locked = isLock() ? getLockRecipe() : null;
        if (locked != null) return hk3gtl$prepareFixed(locked);
        var recipes = machine.getRecipeType().getLookup().getRecipeIterator(machine, Hk3RecipePower::marked);
        while (recipes.hasNext()) {
            GTRecipe fixed = hk3gtl$prepareFixed(recipes.next());
            if (fixed != null) return fixed;
        }
        return null;
    }

    @Unique
    private GTRecipe hk3gtl$prepareFixed(GTRecipe recipe) {
        if (!Hk3RecipePower.marked(recipe) || recipeCheck != null && !recipeCheck.test(recipe, machine)) return null;
        GTRecipe fixed = machine.doModifyRecipe(recipe.copy(), ocParams, ocResult);
        if (fixed == null || !RecipeRunnerHelper.matchRecipe(machine, fixed)
                || !fixed.checkConditions(this).isSuccess() || !fixed.matchTickRecipe(machine).isSuccess()) return null;
        if (isLock()) setLockRecipe(recipe);
        lastOriginRecipe = recipe;
        return fixed;
    }

    @Inject(method = "checkRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$excludeFixedFromPooling(GTRecipe recipe, CallbackInfoReturnable<Boolean> callback) {
        if (hk3gtl$usesFixedMutablePower() && Hk3RecipePower.marked(recipe)) callback.setReturnValue(false);
    }
}
