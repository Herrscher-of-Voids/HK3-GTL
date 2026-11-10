package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.gtlcore.gtlcore.common.machine.trait.MultipleRecipesLogic;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.Iterator;

/**
 * 【文件职责】GTL多配方规划器在吃输入前，将显式HK工况转为保留data和long原价的独立单批。
 * 【变更记录 #1】2026-10-17 16:45:15（第1次备注 · 修订165）
 * 删除：标记工况不再混入double总EU和无data的输出包；新增：复用锁定/条件/dataCheck筛选后的单批。
 * 修改：输入留给标准setupRecipe恰好消费一次，原GTL工况仍由原规划器处理。
 * 用途：精密压机、拉丝、挤压及提取载体不丢失HK费用和研究条件，不改设备注册或结构。
 */
/**
 * 【变更记录 #2】2026-10-17 16:55:08（第2次备注 · 修订165）
 * 删除：安全筛选失败的HK工况可重入原double规划器的缺口。
 * 新增：仅在独立挑选作用域允许HK匹配，finally清理；修改：未成型时不尝试获取迭代器。
 * 用途：一次标记分流不能漏回原规划器吃料，也不影响原GTL工况的执行价格。
 */
@Mixin(value = MultipleRecipesLogic.class, remap = false)
public abstract class Hk3PowerBatchMixin {
    @Unique private boolean hk3gtl$selectingFixed;
    @Shadow private Iterator<GTRecipe> lookupRecipeIterator() { throw new AssertionError(); }
    @Inject(method = "getRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$singleFixedBatch(CallbackInfoReturnable<GTRecipe> callback) {
        RecipeLogic logic = (RecipeLogic) (Object) this;
        if (!logic.machine.hasProxies()) return;
        hk3gtl$selectingFixed = true;
        try {
            Iterator<GTRecipe> recipes = lookupRecipeIterator();
            while (recipes.hasNext()) {
                GTRecipe recipe = recipes.next();
                if (recipe == null || !Hk3RecipePower.marked(recipe)) continue;
                if (!recipe.matchTickRecipe(logic.machine).isSuccess()) continue;
                GTRecipe fixed = recipe.copy();
                fixed.data = recipe.data.copy();
                fixed.parallels = 1;
                callback.setReturnValue(fixed);
                return;
            }
        } finally { hk3gtl$selectingFixed = false; }
    }

    @Inject(method = "checkRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$excludeUnsafeFixed(GTRecipe recipe, CallbackInfoReturnable<Boolean> callback) {
        // 失败的HK工况不能被原规划器重新尝试并丢掉费用元数据。
        if (Hk3RecipePower.marked(recipe) && (!hk3gtl$selectingFixed
                || !Hk3RecipePower.check(recipe, (RecipeLogic) (Object) this).isSuccess())) callback.setReturnValue(false);
    }
}
