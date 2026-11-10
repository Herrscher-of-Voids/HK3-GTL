package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableFluidTank;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.lowdragmc.lowdraglib.misc.FluidStorage;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;
import java.util.List;

/**
 * 【变更记录 #1】2026-11-06 00:21:21 Asia/Hong_Kong（第1次备注 · 修订212）
 * 删除：无；新增：标准GT逐刻流体注入和抽取的单槽撤销接线。
 * 修改：保留原长整型数量和NBT；模拟副本不登记回滚。用途：本地流体失败与同刻能源逆序结算。
 */
@Mixin(value = NotifiableFluidTank.class, remap = false)
public abstract class Hk3FluidTickUndoMixin {
    @Redirect(method = "handleIngredient", at = @At(value = "INVOKE", target =
            "Lcom/lowdragmc/lowdraglib/misc/FluidStorage;drain(Lcom/lowdragmc/lowdraglib/side/fluid/FluidStack;Z)Lcom/lowdragmc/lowdraglib/side/fluid/FluidStack;"), require = 1)
    private static FluidStack hk3gtl$drain(FluidStorage storage, FluidStack stack, boolean simulate,
            IO io, GTRecipe recipe, List<FluidIngredient> left, boolean simulation, IO handlerIO, FluidStorage[] original) {
        return Hk3MaterialTick.fluid(recipe, storage, simulate || simulation || !recipe.ingredientActions.isEmpty(), () -> storage.drain(stack, simulate));
    }

    @Redirect(method = "handleIngredient", at = @At(value = "INVOKE", target =
            "Lcom/lowdragmc/lowdraglib/misc/FluidStorage;fill(Lcom/lowdragmc/lowdraglib/side/fluid/FluidStack;Z)J"), require = 1)
    private static long hk3gtl$fill(FluidStorage storage, FluidStack stack, boolean simulate,
            IO io, GTRecipe recipe, List<FluidIngredient> left, boolean simulation, IO handlerIO, FluidStorage[] original) {
        return Hk3MaterialTick.fluid(recipe, storage, simulate || simulation || !recipe.ingredientActions.isEmpty(), () -> storage.fill(stack, simulate));
    }
}
