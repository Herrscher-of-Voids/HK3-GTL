package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKeyType;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeAmountFormatter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigDecimal;

@Mixin(value = AEKeyType.class, remap = false)
public abstract class Hk3KeyTypeCompactMixin {
    @Shadow public abstract int getAmountPerUnit();

    @Inject(method = "formatShortAmount(JI)Ljava/lang/String;", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$compactAmount(long amount, int characters, CallbackInfoReturnable<String> cir) {
        cir.setReturnValue(Hk3AeAmountFormatter.compact(
                BigDecimal.valueOf(amount).divide(BigDecimal.valueOf(getAmountPerUnit()))));
    }
}
