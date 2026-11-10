package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3RecipeEnvironment;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 【变更记录 #1】2026-09-28 00:04:14（内测5修订91）
 * 删除：无。新增：增强版使用独立执行器时，在handleTickRecipe前保留环境暂停规则。
 * 修改：共用研究、锚与注视度判定，只返回失败，不扣费、不重复产出、不改变并行数。
 * 用途：增强版advance在此返回失败时跳过当批推进，保持原HK3环境限制；原包不加载。
 */
/**
 * 【变更记录 #2】2026-10-17 14:44:46（第2次备注 · 内测5修订162）
 * 删除：退役虚数锚设备的旧环境暂停分支。
 * 新增：无。修改：继续执行研究与注视度只读守卫，不改变能源或产出结算。
 * 用途：增强版执行入口不再调用已移除的旧锚扫描器。
 */
/**
 * 【变更记录 #3】2026-10-17 16:27:36（第3次备注 · 修订165）
 * 删除：无；新增：增强版tick入口的显式高阶工况只读复检。
 * 修改：功率、额定和安全执行器失败保留具体原因；用途：运行中变化不能绕过开始条件，不在守卫扣电。
 */
@Mixin(value = RecipeLogic.class, remap = false)
public abstract class EnhancedRecipeTickMixin {
    private static final GTRecipe.ActionResult HK3GTL$PAUSED = GTRecipe.ActionResult.fail(
            () -> Component.translatable("hk3gtl.compat.environment_paused"));

    @Inject(method = "handleTickRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$checkEnhancedTick(GTRecipe recipe, CallbackInfoReturnable<GTRecipe.ActionResult> result) {
        try {
            var power = Hk3RecipePower.check(recipe, (RecipeLogic) (Object) this);
            if (!power.isSuccess()) {
                result.setReturnValue(power);
                return;
            }
            var machine = ((RecipeLogic) (Object) this).getMachine();
            if (Hk3RecipeAccess.blocks(recipe, machine)
                    || Hk3RecipeEnvironment.throttlesByGaze(machine)) result.setReturnValue(HK3GTL$PAUSED);
        } catch (RuntimeException exception) {
            result.setReturnValue(HK3GTL$PAUSED);
        }
    }
}
