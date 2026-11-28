package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.llamalad7.mixinextras.sugar.Local;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import org.gtlcore.gtlcore.common.machine.trait.MultipleRecipesLogic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.Iterator;

/**
 * GTL多配方规划器在吃输入前，将显式HK工况转为保留data和long原价的独立单批。
 */
@Mixin(value = MultipleRecipesLogic.class, remap = false)
public abstract class Hk3PowerBatchMixin {
    @Unique private boolean hk3gtl$selectingFixed;
    @Shadow private Iterator<GTRecipe> lookupRecipeIterator() { throw new AssertionError(); }
    @Inject(method = "getRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$singleFixedBatch(CallbackInfoReturnable<GTRecipe> callback) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (!logic.machine.hasProxies() || !Hk3PowerPorts.usesExtendedVoltage(logic.machine.getRecipeType())) return;
        hk3gtl$selectingFixed = true;
        try {
            Iterator<GTRecipe> recipes = lookupRecipeIterator();
            while (recipes.hasNext()) {
                GTRecipe recipe = recipes.next();
                if (recipe == null || !Hk3RecipePower.marked(recipe)) continue;
                GTRecipe fixed = logic.machine.doModifyRecipe(recipe.copy(), new OCParams(), new OCResult());
                if (fixed == null || !fixed.matchTickRecipe(logic.machine).isSuccess()) continue;
                fixed.parallels = 1;
                callback.setReturnValue(fixed);
                return;
            }
        } finally { hk3gtl$selectingFixed = false; }
    }

    @Inject(method = "getRecipe", at = @At(value = "INVOKE", target =
            "Lorg/gtlcore/gtlcore/common/machine/trait/MultipleRecipesLogic;getTotalEuOfRecipe(Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)D"))
    private void hk3gtl$mergeProcessReceipt(CallbackInfoReturnable<GTRecipe> callback,
            @Local(ordinal = 0) GTRecipe batch, @Local(ordinal = 1) GTRecipe recipe) {
        Hk3ResearchRecipeRuntime.mergeReceipt(batch, recipe);
    }

    @Inject(method = "checkRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$excludeUnsafeFixed(GTRecipe recipe, CallbackInfoReturnable<Boolean> callback) {
        // 失败的HK工况不能被原规划器重新尝试并丢掉费用元数据。
        if (Hk3RecipePower.marked(recipe) && (!hk3gtl$selectingFixed
                || !Hk3RecipePower.check(recipe, (RecipeLogic) (Object) this).isSuccess())) callback.setReturnValue(false);
    }
}
