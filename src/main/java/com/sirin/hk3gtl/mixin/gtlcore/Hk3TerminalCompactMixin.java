package com.sirin.hk3gtl.mixin.gtlcore;

import com.sirin.hk3gtl.common.integration.ae.Hk3AeAmountFormatter;
import org.gtlcore.gtlcore.client.ae2.FastCellDisplayText;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigDecimal;

@Mixin(value = FastCellDisplayText.class, remap = false)
public abstract class Hk3TerminalCompactMixin {
    @Inject(method = "compact(Ljava/math/BigDecimal;I)Ljava/lang/String;", at = @At("HEAD"), cancellable = true)
    private static void hk3gtl$compactAmount(BigDecimal amount, int characters, CallbackInfoReturnable<String> cir) {
        cir.setReturnValue(Hk3AeAmountFormatter.compact(amount));
    }
}
