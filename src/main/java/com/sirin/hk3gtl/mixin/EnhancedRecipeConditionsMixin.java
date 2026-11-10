package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无。新增：增强版存在时，在其开始和推进均调用的GT配方条件入口校验研究。
 * 修改：不依赖增强版私有类，不替换其执行器、并行和耗电逻辑，不在条件检查时扣费。
 * 用途：阻止替换RecipeLogic后绕过HK3研究；异常拒绝执行，原包不加载此兼容Mixin。
 */
/**
 * 【变更记录 #2】2026-10-17 16:27:36（第2次备注 · 修订165）
 * 删除：无；新增：显式HK3高阶工况的额定电压、能源及执行器守卫。
 * 修改：公共条件入口与JEI读取相同配方数据，先检查工况再执行研究判定。
 * 用途：匹配或推进失败时不扣款；不改变未标记第三方配方。
 */
@Mixin(value = GTRecipe.class, remap = false)
public abstract class EnhancedRecipeConditionsMixin {
    private static final GTRecipe.ActionResult HK3GTL$LOCKED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.compat.research_locked"));

    @Inject(method = "checkConditions", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$checkEnhancedResearch(RecipeLogic logic, CallbackInfoReturnable<GTRecipe.ActionResult> result) {
        try {
            var power = Hk3RecipePower.check((GTRecipe) (Object) this, logic);
            if (!power.isSuccess()) {
                result.setReturnValue(power);
                return;
            }
            if (Hk3RecipeAccess.blocks((GTRecipe) (Object) this, logic.getMachine())) result.setReturnValue(HK3GTL$LOCKED);
        } catch (RuntimeException exception) {
            result.setReturnValue(HK3GTL$LOCKED);
        }
    }
}
