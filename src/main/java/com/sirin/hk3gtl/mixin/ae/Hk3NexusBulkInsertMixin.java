package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusBulkInsert;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

import java.math.BigInteger;

@Pseudo
@Mixin(targets = "com.extendedae_plus.api.storage.InfinityBigIntegerCellInventory", remap = false)
public abstract class Hk3NexusBulkInsertMixin {
    @ModifyExpressionValue(method = "insert", at = @At(value = "INVOKE",
            target = "Ljava/math/BigInteger;valueOf(J)Ljava/math/BigInteger;"))
    private BigInteger hk3gtl$insertExactAmount(BigInteger original, AEKey key, long amount,
            Actionable mode, IActionSource source) {
        return Hk3NexusBulkInsert.expand(key, original, source);
    }
}
