package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusBulkInsert;
import org.gtlcore.gtlcore.integration.ae2.storage.InfinityCellInventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import java.math.BigInteger;

@Mixin(value = InfinityCellInventory.class, remap = false)
public abstract class Hk3GtlNexusBulkInsertMixin {
    @ModifyExpressionValue(method = "insert", at = @At(value = "INVOKE",
            target = "Ljava/math/BigInteger;valueOf(J)Ljava/math/BigInteger;"))
    private BigInteger hk3gtl$insertExactAmount(BigInteger original, AEKey key, long amount,
            Actionable mode, IActionSource source) {
        return Hk3NexusBulkInsert.expand(key, original, source);
    }

    @ModifyArg(method = "insert", at = @At(value = "INVOKE",
            target = "Lorg/gtlcore/gtlcore/integration/ae2/storage/InfinityCellInventory;saveChanges(D)V"))
    private double hk3gtl$saveExactDelta(double nativeDelta, @Local(ordinal = 0) BigInteger delta) {
        return delta.doubleValue();
    }
}
