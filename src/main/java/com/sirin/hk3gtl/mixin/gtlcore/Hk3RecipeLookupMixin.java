package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.lookup.GTRecipeLookup;
import com.gregtechceu.gtceu.api.recipe.lookup.RecipeIterator;
import com.sirin.hk3gtl.common.recipe.Hk3RejectedRecipeIndex;
import org.gtlcore.gtlcore.api.recipe.IAdditionalRecipeIterator;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.function.Predicate;

/** 后于GTL/GTLadd覆盖，在最终迭代器上合并原生树完全漏索引的HK候选。 */
@Mixin(value = GTRecipeLookup.class, remap = false, priority = 500)
public abstract class Hk3RecipeLookupMixin {
    @Unique private final Hk3RejectedRecipeIndex<GTRecipe> hk3gtl$rejected = new Hk3RejectedRecipeIndex<>();

    @Inject(method = "addRecipe", at = @At("RETURN"), require = 1)
    private void hk3gtl$rememberRejected(GTRecipe recipe, CallbackInfoReturnable<Boolean> callback) {
        if (recipe == null || recipe.id == null || !"hk3gtl".equals(recipe.id.getNamespace())) return;
        // 原生终端已有子树时可能返回true却不保存配方；仅注册时检查真实叶，部分入树不重复补充。
        boolean indexed = ((GTRecipeLookup) (Object) this).getLookup().getRecipes(false)
                .anyMatch(leaf -> leaf == recipe);
        hk3gtl$rejected.record(recipe.id.toString(), recipe, indexed);
    }

    @Inject(method = "removeAllRecipes", at = @At("HEAD"), require = 1)
    private void hk3gtl$clearRejected(CallbackInfo callback) {
        hk3gtl$rejected.clear();
        com.sirin.hk3gtl.common.machine.Hk3MultiRecipeLogic.invalidateLookups();
    }

    @Inject(method = "getRecipeIterator", at = @At("RETURN"), require = 1)
    private void hk3gtl$appendRejected(IRecipeCapabilityHolder holder, Predicate<GTRecipe> canHandle,
                                      CallbackInfoReturnable<RecipeIterator> callback) {
        if (!hk3gtl$rejected.isEmpty() && callback.getReturnValue() instanceof IAdditionalRecipeIterator iterator) {
            // 原生hasNext仍调用canHandle；研究、修改器和setupRecipe入口保持原样。
            iterator.setAdditionalRecipes(hk3gtl$rejected.appendTo(iterator.getAdditionalRecipes(), recipe -> recipe.id.toString()));
        }
    }
}
