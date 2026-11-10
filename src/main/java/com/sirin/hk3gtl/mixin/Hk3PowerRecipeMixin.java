package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.capability.recipe.IRecipeCapabilityHolder;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 【文件职责】显式HK高阶工况按同源费用模拟能源，其他tick能力继续走GT原匹配器。
 * 【变更记录 #1】2026-10-17 16:45:15（第1次备注 · 修订165）
 * 删除：只对标记工况绕开旧EU清单long求和；新增：功率/余额守卫与不含EU的其余能力模拟。
 * 修改：原GTL配方立即返回原方法；用途：多个long费用不因溢出被误判为无需能源。
 */
@Mixin(value = GTRecipe.class, remap = false)
public abstract class Hk3PowerRecipeMixin {
    @Inject(method = "matchTickRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$matchPower(IRecipeCapabilityHolder holder, CallbackInfoReturnable<GTRecipe.ActionResult> result) {
        GTRecipe recipe = (GTRecipe) (Object) this;
        if (!Hk3RecipePower.marked(recipe)) return;
        if (!(holder instanceof IRecipeLogicMachine machine)) {
            result.setReturnValue(GTRecipe.ActionResult.FAIL_NO_REASON);
            return;
        }
        var check = Hk3RecipePower.check(recipe, machine.getRecipeLogic());
        if (check.isSuccess()) {
            GTRecipe without = Hk3RecipePower.withoutEU(recipe);
            check = without.matchRecipeContents(IO.IN, holder, without.tickInputs, true);
            if (check.isSuccess()) check = without.matchRecipeContents(IO.OUT, holder, without.tickOutputs, true);
        }
        result.setReturnValue(check);
    }
}
