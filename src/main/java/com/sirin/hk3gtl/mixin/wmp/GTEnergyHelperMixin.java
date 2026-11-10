package com.sirin.hk3gtl.mixin.wmp;

import com.sirin.hk3gtl.common.compat.wmp.Hk3WmpCircuitCompat;
import com.wmp.compat.GTEnergyHelper;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * 【文件职责】
 * - 在 WMP 1.7.0 电路识别入口追加 hk3gtl 16 个正式高阶电路。
 *
 * 【变更记录 #1】2026-07-19 20:14:25（第 1 次备注 · 内测四第 33 次更新）
 * - 删除：无。
 * - 新增：对 isCircuit 与 getCircuitVoltageTier 的返回值追加 hk3gtl canonical 电路判断。
 * - 修改：保留 WMP 原有 GTCEu/标签识别；只有原逻辑不识别时才使用 hk3gtl 映射；isCircuit 返回注入设为可取消以允许安全改写结果。
 * - 用途：让电路板进入 WMP 电路槽并参与原有 BigInteger 发电计算，不修改燃料消耗或电路数量语义。
 */
@Mixin(value = GTEnergyHelper.class, remap = false)
public abstract class GTEnergyHelperMixin {

    @Inject(method = "isCircuit", at = @At("RETURN"), cancellable = true, remap = false)
    private static void hk3gtl$recognizeCircuit(ItemStack stack, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValue() && Hk3WmpCircuitCompat.isHk3Circuit(stack)) {
            cir.setReturnValue(true);
        }
    }

    @Inject(method = "getCircuitVoltageTier", at = @At("RETURN"), cancellable = true, remap = false)
    private static void hk3gtl$recognizeTier(ItemStack stack, CallbackInfoReturnable<Integer> cir) {
        int tier = Hk3WmpCircuitCompat.getTier(stack);
        if (tier >= 0) cir.setReturnValue(tier);
    }
}
