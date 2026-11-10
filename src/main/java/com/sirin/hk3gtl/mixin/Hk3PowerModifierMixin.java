package com.sirin.hk3gtl.mixin;

import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 【文件职责】显式HK工况固定原始long耗电、时长、物料和data，避免第三方double折扣/超频丢价。
 * 【变更记录 #1】2026-10-17 16:45:15（第1次备注 · 修订165）
 * 删除：仅标记工况跳过浮点修饰；新增：原始工况副本入口。
 * 修改：结构本身、配方条件、研究与端口仍验证；用途：原GTL配方和设备注册完全沿原流程。
 */
/**
 * 【变更记录 #2】2026-10-17 16:52:26（第2次备注 · 修订165）
 * 删除：固定工况可能绕过仓室modifyRecipe拒绝判定的缺口。
 * 新增：仍调用已有仓室的准入判断，任一返回null即拒绝；修改：只丢弃数值修饰，保留准入结果。
 * 用途：数据访问仓等原有硬件权限不能因固定long费用而被跳过。
 */
@Mixin(value = WorkableMultiblockMachine.class, remap = false)
public abstract class Hk3PowerModifierMixin {
    @Inject(method = "doModifyRecipe", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$fixedPower(GTRecipe recipe, OCParams params, OCResult result, CallbackInfoReturnable<GTRecipe> callback) {
        if (!Hk3RecipePower.marked(recipe)) return;
        GTRecipe validation = recipe.copy();
        validation.data = recipe.data.copy();
        for (var part : ((WorkableMultiblockMachine) (Object) this).getParts()) {
            validation = part.modifyRecipe(validation);
            if (validation == null) { callback.setReturnValue(null); return; }
        }
        callback.setReturnValue(recipe.copy());
    }
}
