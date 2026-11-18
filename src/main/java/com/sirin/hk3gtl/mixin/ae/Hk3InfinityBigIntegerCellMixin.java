package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.KeyCounter;
import it.unimi.dsi.fastutil.objects.Object2ObjectMap;
import org.gtlcore.gtlcore.integration.ae2.storage.PreciseStorageAmount;
import org.gtlcore.gtlcore.integration.ae2.storage.TerminalDisplayRead;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.math.BigInteger;

@Pseudo
@Mixin(targets = "com.extendedae_plus.api.storage.InfinityBigIntegerCellInventory", remap = false)
public abstract class Hk3InfinityBigIntegerCellMixin implements PreciseStorageAmount {
    @Shadow private Object2ObjectMap<AEKey, BigInteger> getCellStoredMap() { return null; }

    @Override
    public BigInteger getExactStoredAmount(AEKey key) {
        return getCellStoredMap().getOrDefault(key, BigInteger.ZERO);
    }

    @Inject(method = "getAvailableStacks", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$collectExactStock(KeyCounter output, CallbackInfo ci) {
        if (!TerminalDisplayRead.tracks(output)) return;
        for (var entry : getCellStoredMap().object2ObjectEntrySet())
            TerminalDisplayRead.addExact(output, entry.getKey(), entry.getValue());
        ci.cancel();
    }
}
