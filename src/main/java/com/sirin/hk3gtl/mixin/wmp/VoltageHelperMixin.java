package com.sirin.hk3gtl.mixin.wmp;

import com.sirin.hk3gtl.common.compat.wmp.Hk3WmpCircuitCompat;
import com.wmp.compat.VoltageHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;


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
