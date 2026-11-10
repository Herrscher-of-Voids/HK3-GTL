package com.sirin.hk3gtl.mixin.wmp;

import com.sirin.hk3gtl.common.compat.wmp.Hk3WmpCircuitCompat;
import com.wmp.compat.VoltageHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;

/**
 * 【文件职责】
 * - 扩展 WMP 1.7.0 的电压查询，使 Tier 15~30 不再被 clamp 到 MAX。
 *
 * 【变更记录 #1】2026-07-19 20:14:25（第 1 次备注 · 内测四第 33 次更新）
 * - 删除：无。
 * - 新增：在 getVoltage/getTierName HEAD 对 Tier 15~30 返回 hk3gtl BigInteger 公式电压与阶段名称。
 * - 修改：Tier 0~14 完全保留 WMP 原数组行为，高阶 GUI 不再被钳制显示为 MAX。
 * - 用途：确保高阶电路发电倍率按 8×4^tier 计算，Tier 30 及后续乘法不发生 long 溢出。
 */
@Mixin(value = VoltageHelper.class, remap = false)
public abstract class VoltageHelperMixin {

    @Inject(method = "getVoltage", at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$extendVoltage(int tier, CallbackInfoReturnable<BigInteger> cir) {
        BigInteger voltage = Hk3WmpCircuitCompat.getVoltage(tier);
        if (voltage.signum() > 0) cir.setReturnValue(voltage);
    }

    @Inject(method = "getTierName", at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$extendTierName(int tier, CallbackInfoReturnable<String> cir) {
        String name = Hk3WmpCircuitCompat.getTierName(tier);
        if (!name.isEmpty()) cir.setReturnValue(name);
    }
}
